"""Deterministic offline S12–S15 adjudication over recorded observations."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from vlm_faithfulness_benchmark.gating.condition_a import (
    ConditionAVerdict,
    RegimeReading,
    determine_condition_a,
)
from vlm_faithfulness_benchmark.gating.condition_b import (
    DRIFT_INSTRUMENT_ID,
    compute_drift,
    determine_condition_b,
    instrument_provenance,
)
from vlm_faithfulness_benchmark.gating.controls import (
    ControlResult,
    coherence_screen,
    evaluate_p6,
)
from vlm_faithfulness_benchmark.gating.regimes import REGIMES
from vlm_faithfulness_benchmark.generation.digest import verify_baseline_digest
from vlm_faithfulness_benchmark.generation.identity import (
    GeneratorId,
    InstanceId,
    SourceRecordId,
)
from vlm_faithfulness_benchmark.labeling.calibration_lock import CalibrationLock
from vlm_faithfulness_benchmark.labeling.projection import project_state_and_label
from vlm_faithfulness_benchmark.sealing.provenance import (
    InterventionalProvenance,
    ProvenanceEntry,
    SealedResolution,
)

__all__ = ["InputBindings", "adjudicate_record", "instance_from_key"]

_SCHEMA = "vlm-faithfulness-sealed-adjudication-v1"
_GATE_ROUTE = {"P1": "E1", "P2": "E2", "P3": "E3"}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _mapping(value: object, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RuntimeError(f"{field} must be an object")
    return value


def _list(value: object, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise RuntimeError(f"{field} must be an array")
    return value


def _string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise RuntimeError(f"{field} must be a non-empty string")
    return value


def _boolean(value: object, field: str) -> bool:
    if type(value) is not bool:
        raise RuntimeError(f"{field} must be a boolean")
    return value


def _integer(value: object, field: str) -> int:
    if type(value) is not int:
        raise RuntimeError(f"{field} must be an integer")
    return value


def _number(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RuntimeError(f"{field} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise RuntimeError(f"{field} must be finite")
    return result


def instance_from_key(instance_key: str) -> InstanceId:
    """Parse and canonicalize an R1 instance key."""
    try:
        raw = json.loads(instance_key)
    except json.JSONDecodeError as error:
        raise RuntimeError("instance key is not JSON") from error
    root = _mapping(raw, "instance key")
    generator_raw = _mapping(root.get("generator"), "instance generator")
    source_raw = _mapping(root.get("source"), "instance source")
    generator_components: dict[str, str] = {}
    for key, value in generator_raw.items():
        if not isinstance(key, str) or not key or not isinstance(value, str) or not value:
            raise RuntimeError("instance generator components must be non-empty strings")
        generator_components[key] = value
    dataset = _string(source_raw.get("dataset"), "instance dataset")
    record_id = _string(source_raw.get("record_id"), "instance record_id")
    instance = InstanceId(
        GeneratorId.from_mapping(generator_components), SourceRecordId(dataset, record_id)
    )
    _require(instance.key() == instance_key, "instance key is not in canonical R1 form")
    return instance


@dataclass(frozen=True, slots=True)
class InputBindings:
    """Per-row content bindings copied into the sealed artifact."""

    baseline_mode: str
    s02_sha256: str
    observation_sha256: str
    observation_line: int
    merge_report_sha256: str
    run_binding: Mapping[str, Any]


def _gate_determinations(
    raw_gates: object, provenance: InterventionalProvenance
) -> str | None:
    gates = _list(raw_gates, "gates")
    _require(bool(gates), "observation has no gate determinations")
    expected = ("P1", "P2", "P3")
    route: str | None = None
    for index, raw_value in enumerate(gates):
        raw_gate = _list(raw_value, "gate row")
        _require(len(raw_gate) == 3, "malformed gate row")
        gate = _string(raw_gate[0], "gate id")
        passed = _boolean(raw_gate[1], "gate pass flag")
        evidence = _string(raw_gate[2], "gate evidence")
        _require(index < len(expected) and gate == expected[index], "gate order is non-conformant")
        provenance.append(
            ProvenanceEntry(
                "determination",
                "S04" if gate == "P1" else "S05",
                {"gate": gate, "passed": passed, "evidence": evidence},
            )
        )
        if not passed:
            route = _GATE_ROUTE[gate]
            _require(index == len(gates) - 1, "a gate was evaluated after the first failure")
            break
    if route is None:
        _require(len(gates) == 3, "passing gate prefix is incomplete")
    return route


def _readings(raw: object, baseline_index: int) -> dict[str, RegimeReading]:
    readings_raw = _mapping(raw, "readings")
    _require(set(readings_raw) == set(REGIMES), "observation regime set is not registered")
    readings: dict[str, RegimeReading] = {}
    option_count: int | None = None
    for regime in REGIMES:
        raw_scores = readings_raw[regime]
        if raw_scores is None:
            readings[regime] = RegimeReading(regime, None)
            continue
        score_values = _list(raw_scores, f"{regime} reading")
        _require(bool(score_values), f"empty {regime} reading")
        scores: list[float] = []
        for raw_score in score_values:
            scores.append(_number(raw_score, f"{regime} reading"))
        if option_count is None:
            option_count = len(scores)
        _require(len(scores) == option_count, "regime option-vector lengths differ")
        readings[regime] = RegimeReading(regime, tuple(scores))
    if option_count is None:
        raise RuntimeError("all answer readings are non-evaluable")
    _require(option_count >= 2, "P1-passing row must remain multiple-choice")
    _require(0 <= baseline_index < option_count, "baseline chosen index is out of range")
    return readings


def _resolution_payload(
    provenance: InterventionalProvenance,
    baseline_digest: str,
    bindings: InputBindings,
    calibration: CalibrationLock,
) -> dict[str, Any]:
    return {
        "schema": _SCHEMA,
        "baseline_binding": {
            "mode": bindings.baseline_mode,
            "digest": baseline_digest,
            "canonical_s02_sha256": bindings.s02_sha256,
        },
        "observation_binding": {
            "merged_observation_sha256": bindings.observation_sha256,
            "line": bindings.observation_line,
            "merge_validation_report_sha256": bindings.merge_report_sha256,
            "run": dict(bindings.run_binding),
        },
        "calibration_binding": {
            "id": calibration.lock_id,
            "sha256": calibration.lock_sha256,
        },
        "provenance": provenance.as_dict(),
    }


def _seal_route(
    provenance: InterventionalProvenance,
    e_code: str,
    baseline_digest: str,
    bindings: InputBindings,
    calibration: CalibrationLock,
) -> dict[str, Any]:
    provenance.seal(SealedResolution(None, None, None, e_code, calibration.spec_versions))
    return _resolution_payload(provenance, baseline_digest, bindings, calibration)


def _validate_baseline(
    instance: InstanceId, s02_payload: Mapping[str, Any], observation: Mapping[str, Any]
) -> tuple[Mapping[str, Any], str]:
    output_tuple = _mapping(s02_payload.get("output_tuple"), "S02 output_tuple")
    baseline_digest = _string(s02_payload.get("baseline_digest"), "S02 baseline digest")
    verify_baseline_digest(output_tuple, baseline_digest)
    _require(s02_payload.get("source") == instance.source.key(), "S02 source binding mismatch")
    _require(s02_payload.get("generator") == instance.generator.key(), "S02 generator mismatch")
    _require(observation.get("source") == instance.source.key(), "observation source mismatch")
    return output_tuple, baseline_digest


def adjudicate_record(
    instance_key: str,
    s02_payload: Mapping[str, Any],
    observation: Mapping[str, Any],
    bindings: InputBindings,
    calibration: CalibrationLock,
    coherence_registry: Sequence[Any],
) -> dict[str, Any]:
    """Resolve one candidate exactly once and return its sealed JSON payload."""
    instance = instance_from_key(instance_key)
    output_tuple, baseline_digest = _validate_baseline(instance, s02_payload, observation)
    _require(bindings.baseline_mode in {"in-row", "accepted-legacy-sidecar"}, (
        "unknown baseline binding mode"
    ))
    observed_digest = observation.get("baseline_digest")
    if bindings.baseline_mode == "in-row":
        _require(observed_digest == baseline_digest, "in-row baseline digest mismatch")
    else:
        _require(observed_digest is None, "legacy-sidecar row unexpectedly has an in-row digest")

    provenance = InterventionalProvenance(instance)
    route = _gate_determinations(observation.get("gates"), provenance)
    observed_route = observation.get("route")
    _require(observed_route == route, "recorded early route does not match gate precedence")
    if route is not None:
        return _seal_route(
            provenance, route, baseline_digest, bindings, calibration
        )

    baseline_index = _integer(observation.get("baseline_chosen_index"), (
        "baseline chosen index"
    ))
    chosen_answer = _string(output_tuple.get("chosen_answer"), "P1-passing chosen answer")
    _require(bool(chosen_answer.strip()), "P1-passing chosen answer is blank")
    readings = _readings(observation.get("readings"), baseline_index)
    hflip_raw = _mapping(observation.get("hflip"), "hflip")
    hflip = readings["hflip"]
    hflip_evaluable = hflip.evaluable()
    hflip_persisted = hflip_evaluable and hflip.baseline_held(baseline_index)
    _require(hflip_raw.get("evaluable") is hflip_evaluable, "stored hflip evaluability mismatch")
    _require(hflip_raw.get("persisted") is hflip_persisted, "stored hflip result mismatch")
    spatial_lateral = _boolean(hflip_raw.get("spatial_lateral"), (
        "stored hflip applicability"
    ))
    provenance.append(
        ProvenanceEntry(
            "observation",
            "S06",
            {
                "baseline_chosen_index": baseline_index,
                "readings": observation["readings"],
                "hflip": observation["hflip"],
            },
        )
    )

    condition_a = determine_condition_a(baseline_index, readings, calibration.k)
    stored_flip_count = observation.get("flip_count")
    expected_stored = (
        None
        if condition_a.verdict is ConditionAVerdict.INDETERMINATE
        else condition_a.flip_count
    )
    _require(stored_flip_count == expected_stored, "stored flip count mismatch")
    provenance.append(
        ProvenanceEntry(
            "determination",
            "S07",
            {
                "verdict": condition_a.verdict.value,
                "flip_count": condition_a.flip_count,
                "k": condition_a.k,
                "missing_regimes": list(condition_a.missing_regimes),
            },
        )
    )
    if condition_a.verdict is ConditionAVerdict.INDETERMINATE:
        return _seal_route(
            provenance, "E4", baseline_digest, bindings, calibration
        )

    a_is_true = condition_a.verdict is ConditionAVerdict.TRUE
    baseline_rationale = _string(output_tuple.get("rationale"), "P1-passing baseline rationale")
    _require(bool(baseline_rationale.strip()), "P1-passing baseline rationale is blank")

    targeted_rationale: str | None = None
    control_rationale: str | None = None
    targeted_drift: float | None = None
    control_drift: float | None = None
    control_applicable = False
    coherence: ControlResult | None = None

    if a_is_true:
        saliency_raw = observation.get("saliency")
        saliency = _mapping(saliency_raw, "saliency")
        max_drop = _number(saliency.get("max_drop"), "saliency max_drop")
        locatable = _boolean(saliency.get("locatable"), "saliency locatable flag")
        p5_holds = locatable and max_drop >= calibration.saliency_floor
        provenance.append(ProvenanceEntry("observation", "S08", dict(saliency)))
        provenance.append(
            ProvenanceEntry(
                "determination",
                "S08",
                {
                    "gate": "P5",
                    "holds": p5_holds,
                    "max_drop": max_drop,
                    "floor": calibration.saliency_floor,
                    "comparison": "max_drop >= floor",
                },
            )
        )
        if not p5_holds:
            return _seal_route(
                provenance, "E5", baseline_digest, bindings, calibration
            )
        _require("box" in saliency and "profile" in saliency, (
            "locatable saliency lacks its region/profile"
        ))

        targeted_raw = observation.get("counterfactual_rationale")
        control_raw = observation.get("control_rationale")
        targeted_rationale = targeted_raw if isinstance(targeted_raw, str) else None
        control_rationale = control_raw if isinstance(control_raw, str) else None
        control_applicable = _boolean(
            observation.get("control_edit_applicable"), "control applicability"
        )
        if targeted_rationale is not None and targeted_rationale.strip():
            targeted_drift = compute_drift(
                baseline_rationale, targeted_rationale, calibration.stopwords
            )
        if control_applicable and control_rationale is not None and control_rationale.strip():
            control_drift = compute_drift(
                baseline_rationale, control_rationale, calibration.stopwords
            )
        coherence = coherence_screen(
            baseline_rationale, targeted_rationale, coherence_registry
        )
        _require(observation.get("coherence") == coherence.status, (
            "stored coherence result does not reproduce"
        ))
        provenance.append(
            ProvenanceEntry(
                "observation",
                "S09",
                {
                    "counterfactual_answer": observation.get("counterfactual_answer"),
                    "counterfactual_rationale": targeted_rationale,
                    "control_rationale": control_rationale,
                    "control_edit_applicable": control_applicable,
                    "control_coverage_ratio": observation.get("control_coverage_ratio"),
                    "targeted_drift": targeted_drift,
                    "control_drift": control_drift,
                    "instrument": instrument_provenance(calibration.stopwords_sha256),
                },
            )
        )

    answer_readings_evaluable = all(readings[regime].evaluable() for regime in REGIMES)
    rationale_readings_evaluable = None
    if a_is_true:
        rationale_readings_evaluable = (
            targeted_rationale is not None
            and bool(targeted_rationale.strip())
            and (
                not control_applicable
                or (control_rationale is not None and bool(control_rationale.strip()))
            )
        )
    p6 = evaluate_p6(
        a_is_true_branch=a_is_true,
        baseline_chosen_index=baseline_index,
        hflip_reading=hflip,
        qtype_spatial_lateral=spatial_lateral,
        answer_readings_evaluable=answer_readings_evaluable,
        rationale_readings_evaluable=rationale_readings_evaluable,
        coherence=coherence,
        control_edit_drift=control_drift,
        control_edit_applicable=control_applicable,
        theta_b=calibration.theta_b,
    )
    provenance.append(
        ProvenanceEntry(
            "determination",
            "S10",
            {
                "gate": "P6",
                "holds": p6.holds,
                "results": [
                    {
                        "control": result.control,
                        "status": result.status,
                        "evidence": result.evidence,
                    }
                    for result in p6.results
                ],
            },
        )
    )
    if not p6.holds:
        return _seal_route(
            provenance, "E6", baseline_digest, bindings, calibration
        )

    condition_b = None
    if a_is_true:
        if targeted_drift is None:
            raise RuntimeError("P6-passing A-true row has no targeted drift")
        condition_b = determine_condition_b(targeted_drift, calibration.theta_b)
        provenance.append(
            ProvenanceEntry(
                "determination",
                "S11",
                {
                    "tracks": condition_b.tracks,
                    "targeted_drift": condition_b.targeted_drift,
                    "theta_b": condition_b.theta_b,
                    "comparison": "targeted_drift >= theta_b",
                    "instrument": DRIFT_INSTRUMENT_ID,
                },
            )
        )

    state, label, reason = project_state_and_label(condition_a, condition_b, p6)
    provenance.seal(
        SealedResolution(state, label, reason, None, calibration.spec_versions)
    )
    return _resolution_payload(provenance, baseline_digest, bindings, calibration)
