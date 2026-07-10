"""Pilot observation orchestrator (V1-045; RIP §5.1–§5.2).

Matrix rows: S04–S11 stage chain, CC2 (exactly-once per phase), D-ATOM
(record-level atomic commits), GPU discipline (resume via the run ledger).

The pilot collects the observation surface **without labeling**: θ_B and k
do not exist yet (the §5.2 calibration consumes this run's output), so the
pilot records flip counts (Condition A under every pre-registered k),
localization outcomes, and targeted/control drifts. Provisional labels and
the human verification sheet are produced by the calibration step, not
here.

Resume granularity is one record: each candidate's full observation row
commits atomically under ``<instance>::pilot_obs``; interruption loses at
most the in-flight record (the ~70 model calls behind it are recomputed on
retry — a deliberate trade against partial-row complexity).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Mapping, Sequence

import numpy as np
import numpy.typing as npt

from vlm_faithfulness_benchmark.gating.condition_a import RegimeReading
from vlm_faithfulness_benchmark.gating.controls import coherence_screen
from vlm_faithfulness_benchmark.gating.edits import (
    apply_control_edit,
    apply_targeted_edit,
    control_box,
)
from vlm_faithfulness_benchmark.gating.gates import evaluate_p_gates
from vlm_faithfulness_benchmark.gating.regimes import (
    DESTRUCTIVE_REGIMES,
    REGIMES,
    apply_regime,
)
from vlm_faithfulness_benchmark.gating.saliency import (
    GRID_COLS,
    GRID_ROWS,
    SaliencyGrid,
    localize,
)
from vlm_faithfulness_benchmark.generation.harness import GenerationOutcome
from vlm_faithfulness_benchmark.generation.identity import InstanceId
from vlm_faithfulness_benchmark.ingestion.aokvqa import SourceRecord
from vlm_faithfulness_benchmark.run_ledger import RunLedger

__all__ = ["PilotIO", "run_pilot_observation"]

Image = npt.NDArray[np.uint8]

#: Provisional flat-saliency floor for the PILOT sweep only: localization is
#: attempted whenever any positive drop exists; the calibrated floor (§5.2)
#: re-adjudicates E5 at labeling time from the recorded max_drop.
_PILOT_SALIENCY_FLOOR = 1e-9


@dataclass(frozen=True, slots=True)
class PilotIO:
    """The injected model/data surface (testable with stubs; GPU only in real runs).

    Attributes:
        load_image: Source record → HxWx3 uint8 baseline image.
        load_partner_image: Source record → derangement partner's image.
        score_options: (record, image) → per-option log-likelihoods, or
            None when non-evaluable after the design §5.3 retry policy.
        generate: (record, image) → GenerationOutcome (rationale under the
            pinned extraction contract) or None when non-evaluable.
        registry: The pinned Appendix A pattern registry.
        declared_scope: Dataset identifiers declared for this run.
        spatial_qtypes: Instance predicate for hflip inapplicability
            (pinned question-type mapping).
        record_index_of: Record → its identity-sorted position in the FULL
            dataset (review Major: seeds must be partition-independent, so
            the batch position must never key a stream).
    """

    load_image: Callable[[SourceRecord], Image]
    load_partner_image: Callable[[SourceRecord], Image]
    score_options: Callable[[SourceRecord, Image], tuple[float, ...] | None]
    generate: Callable[[SourceRecord, Image], GenerationOutcome | None]
    registry: Sequence[re.Pattern[str]]
    declared_scope: frozenset[str]
    spatial_qtypes: Callable[[SourceRecord], bool]
    record_index_of: Callable[[SourceRecord], int]


def _observe_candidate(
    record: SourceRecord,
    record_index: int,
    s02_tuple: Mapping[str, Any],
    io: PilotIO,
) -> dict[str, Any]:
    """Collect one candidate's full observation row (no labels, no θ/k)."""
    row: dict[str, Any] = {"source": record.identity.key()}

    chosen = s02_tuple.get("chosen_answer")
    rationale = s02_tuple.get("rationale")
    dets, e_code = evaluate_p_gates(
        chosen if isinstance(chosen, str) else None,
        rationale if isinstance(rationale, str) else None,
        record.options,
        has_image=bool(record.image_ref),
        registry=io.registry,
        dataset=record.identity.dataset,
        declared_scope=io.declared_scope,
    )
    row["gates"] = [(d.gate, d.passed, d.evidence) for d in dets]
    if e_code is not None:
        row["route"] = e_code
        return row
    assert isinstance(chosen, str) and isinstance(rationale, str)
    baseline_chosen_index = next(
        i for i, o in enumerate(record.options) if o.strip().lower() == chosen.strip().lower()
    )
    row["baseline_chosen_index"] = baseline_chosen_index

    image = io.load_image(record)
    partner = io.load_partner_image(record)

    readings: dict[str, RegimeReading] = {}
    for regime in REGIMES:  # all six, including `real` (RIP §2.1; review Major)
        variant = apply_regime(
            regime, image, record_index,
            partner_image=partner if regime == "wrong-image" else None,
        )
        scores = io.score_options(record, variant)
        readings[regime] = RegimeReading(regime, scores)
    row["readings"] = {
        r: list(v.option_loglikelihoods) if v.option_loglikelihoods else None
        for r, v in readings.items()
    }
    evaluable = [readings[r] for r in DESTRUCTIVE_REGIMES if readings[r].evaluable()]
    if len(evaluable) < len(DESTRUCTIVE_REGIMES):
        row["flip_count"] = None  # E4 territory at labeling time
        return row
    row["flip_count"] = sum(
        1
        for r in DESTRUCTIVE_REGIMES
        if not readings[r].baseline_held(baseline_chosen_index)
    )
    hflip = readings["hflip"]
    row["hflip"] = {
        "spatial_lateral": io.spatial_qtypes(record),
        "evaluable": hflip.evaluable(),
        "persisted": hflip.evaluable() and hflip.baseline_held(baseline_chosen_index),
    }

    # Localization sweep (always collected when flip_count >= min k could
    # apply; collected unconditionally for calibration completeness).
    grid = SaliencyGrid(image.shape[0], image.shape[1])
    baseline_scores = io.score_options(record, image)
    if baseline_scores is None:
        row["saliency"] = None
        return row
    base = baseline_scores[baseline_chosen_index]
    drops = np.zeros((GRID_ROWS, GRID_COLS), dtype=np.float64)
    sweep_evaluable = True
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            cell_scores = io.score_options(record, grid.occlude_cell(image, r, c))
            if cell_scores is None:  # never coerced to 0.0 (review Major)
                sweep_evaluable = False
                break
            drops[r, c] = base - cell_scores[baseline_chosen_index]
        if not sweep_evaluable:
            break
    if not sweep_evaluable:
        row["saliency"] = None  # readings-integrity territory at labeling time
        return row
    region = localize(drops, grid, _PILOT_SALIENCY_FLOOR)
    if region is None:
        row["saliency"] = {"max_drop": float(drops.max()), "locatable": False}
        return row
    row["saliency"] = {
        "max_drop": region.max_drop,
        "locatable": True,
        "box": list(region.box),
        "profile": region.profile_id,
    }

    targeted_image = apply_targeted_edit(image, partner, region, record_index)
    control_applicable = True
    try:
        control_box(region, image.shape[0], image.shape[1])
    except AssertionError:
        control_applicable = False
    row["control_edit_applicable"] = control_applicable

    targeted_out = io.generate(record, targeted_image)
    control_out = (
        io.generate(record, apply_control_edit(image, partner, region, record_index))
        if control_applicable
        else None
    )
    row["counterfactual_rationale"] = targeted_out.rationale if targeted_out else None
    row["control_rationale"] = control_out.rationale if control_out else None
    row["coherence"] = coherence_screen(
        rationale, targeted_out.rationale if targeted_out else None, io.registry
    ).status
    return row


def run_pilot_observation(
    records: Sequence[SourceRecord],
    s02_payloads: Mapping[str, Mapping[str, Any]],
    instance_of: Callable[[SourceRecord], InstanceId],
    io: PilotIO,
    ledger: RunLedger,
    on_progress: Callable[[str], None] | None = None,
) -> Mapping[str, int]:
    """Run the pilot observation phase, resumably (record-atomic).

    Args:
        records: The pre-registered pilot sample (S01-normalized).
        s02_payloads: Instance key → committed S02 payload (the baseline
            tuples from the generation ledger; digest-verified upstream).
        instance_of: Record → instance identity (the run's generator).
        io: The injected model/data surface.
        ledger: The pilot run ledger.
        on_progress: Optional per-record callback.

    Returns:
        ``{"committed": n_new, "skipped": n_resumed, "missing_s02": n}``.
    """
    committed = skipped = missing = 0
    for record in records:
        record_index = io.record_index_of(record)  # dataset-identity position
        instance = instance_of(record)
        key = f"{instance.key()}::pilot_obs"
        if ledger.is_committed(key):
            skipped += 1
            continue
        s02 = s02_payloads.get(instance.key())
        if s02 is None:
            missing += 1
            continue
        tuple_payload = s02["output_tuple"]
        assert isinstance(tuple_payload, Mapping)
        row = _observe_candidate(record, record_index, tuple_payload, io)
        ledger.commit(key, row)
        committed += 1
        if on_progress is not None:
            on_progress(f"{record.identity.record_id} observed")
    return {"committed": committed, "skipped": skipped, "missing_s02": missing}
