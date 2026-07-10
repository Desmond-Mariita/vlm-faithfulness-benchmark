"""Tests for the pilot observation orchestrator (V1-045 infrastructure)."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from vlm_faithfulness_benchmark.gating.gates import load_pattern_registry
from vlm_faithfulness_benchmark.gating.pilot import PilotIO, run_pilot_observation
from vlm_faithfulness_benchmark.generation.harness import GenerationOutcome
from vlm_faithfulness_benchmark.generation.identity import (
    GeneratorId,
    InstanceId,
    SourceRecordId,
)
from vlm_faithfulness_benchmark.ingestion.aokvqa import SourceRecord
from vlm_faithfulness_benchmark.run_ledger import RunLedger

REGISTRY = load_pattern_registry(
    Path(__file__).resolve().parents[2] / "config" / "p2_patterns_v1.txt"
)
GEN_ID = GeneratorId.from_mapping({"model": "stub", "revision": "t"})
IMG = np.random.default_rng(3).integers(0, 256, (64, 96, 3), dtype=np.uint8)


def _record(i: int) -> SourceRecord:
    return SourceRecord(
        identity=SourceRecordId("aokvqa", f"q-{i}"),
        image_ref=f"coco/{i}",
        question="what is held?",
        options=("umbrella", "bat"),
        annotations={"gold_answer_idx": 0},
    )


def _io(image_dependent: bool = True) -> PilotIO:
    """A stub IO: option 0 wins on the real image; flips under perturbation iff image_dependent."""

    def score(record: SourceRecord, image: np.ndarray) -> tuple[float, ...]:
        pristine = np.array_equal(image, IMG) or np.array_equal(image, IMG[:, ::-1, :])
        if pristine or not image_dependent:
            return (-0.5, -3.0)
        return (-3.0, -0.5)

    return PilotIO(
        load_image=lambda r: IMG,
        load_partner_image=lambda r: np.roll(IMG, 7, axis=1),
        score_options=score,
        generate=lambda r, img: GenerationOutcome(
            "umbrella", "the edited region now shows a very different object entirely"
        ),
        registry=REGISTRY,
        declared_scope=frozenset({"aokvqa"}),
        spatial_qtypes=lambda r: False,
        record_index_of=lambda r: int(r.identity.record_id.split("-")[1]),
    )


def _s02(records: list[SourceRecord]) -> dict[str, dict[str, object]]:
    return {
        InstanceId(GEN_ID, r.identity).key(): {
            "output_tuple": {
                "chosen_answer": "umbrella",
                "rationale": "the man is holding an umbrella against the rain",
            }
        }
        for r in records
    }


def test_full_observation_row_for_image_dependent_candidate(tmp_path: Path) -> None:
    """Gates pass, 4/4 flips recorded, saliency + drifts + coherence collected."""
    records = [_record(1)]
    ledger = RunLedger(tmp_path / "pilot.jsonl")
    result = run_pilot_observation(
        records, _s02(records), lambda r: InstanceId(GEN_ID, r.identity), _io(), ledger
    )
    assert result == {"committed": 1, "skipped": 0, "missing_s02": 0}
    row = ledger.payload(f"{InstanceId(GEN_ID, records[0].identity).key()}::pilot_obs")
    assert row["flip_count"] == 4
    assert row["hflip"]["persisted"] is True
    assert row["saliency"]["locatable"] is True
    assert row["coherence"] == "pass"
    assert row["counterfactual_rationale"]
    ledger.close()


def test_gate_routed_candidate_stops_at_gates(tmp_path: Path) -> None:
    """An abstention tuple records its route and collects no readings."""
    records = [_record(1)]
    s02 = _s02(records)
    key = next(iter(s02))
    s02[key]["output_tuple"] = {"chosen_answer": "umbrella", "rationale": "I cannot tell."}
    ledger = RunLedger(tmp_path / "pilot.jsonl")
    run_pilot_observation(
        records, s02, lambda r: InstanceId(GEN_ID, r.identity), _io(), ledger
    )
    row = ledger.payload(f"{key}::pilot_obs")
    assert row["route"] == "E2"
    assert "readings" not in row
    ledger.close()


def test_image_independent_candidate_records_zero_flips(tmp_path: Path) -> None:
    """A stubborn answer records flip_count=0 (S1 territory at labeling time)."""
    records = [_record(1)]
    ledger = RunLedger(tmp_path / "pilot.jsonl")
    run_pilot_observation(
        records, _s02(records), lambda r: InstanceId(GEN_ID, r.identity),
        _io(image_dependent=False), ledger,
    )
    row = ledger.payload(f"{InstanceId(GEN_ID, records[0].identity).key()}::pilot_obs")
    assert row["flip_count"] == 0
    ledger.close()


def test_resume_skips_and_missing_s02_counted(tmp_path: Path) -> None:
    """Record-atomic resume; candidates without S02 payloads are surfaced."""
    records = [_record(1), _record(2)]
    s02 = _s02(records[:1])  # record 2 has no baseline tuple
    path = tmp_path / "pilot.jsonl"
    ledger = RunLedger(path)
    first = run_pilot_observation(
        records, s02, lambda r: InstanceId(GEN_ID, r.identity), _io(), ledger
    )
    assert first == {"committed": 1, "skipped": 0, "missing_s02": 1}
    ledger.close()
    resumed = RunLedger(path)
    second = run_pilot_observation(
        records, s02, lambda r: InstanceId(GEN_ID, r.identity), _io(), resumed
    )
    assert second == {"committed": 0, "skipped": 1, "missing_s02": 1}
    resumed.close()
