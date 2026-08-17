"""End-to-end per-record S12–S15 adjudication tests."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest

from vlm_faithfulness_benchmark.generation.digest import baseline_digest
from vlm_faithfulness_benchmark.generation.identity import (
    GeneratorId,
    InstanceId,
    SourceRecordId,
)
from vlm_faithfulness_benchmark.labeling.adjudication import (
    InputBindings,
    adjudicate_record,
)
from vlm_faithfulness_benchmark.labeling.calibration_lock import CalibrationLock

INSTANCE = InstanceId(
    GeneratorId.from_mapping({"model": "glm-test", "revision": "abc"}),
    SourceRecordId("aokvqa", "r-1"),
)
BASELINE = "a red umbrella protects the person from heavy rain"
REGISTRY = (re.compile(r"cannot", re.IGNORECASE),)


def _calibration() -> CalibrationLock:
    return CalibrationLock(
        lock_id="test-lock",
        lock_sha256="a" * 64,
        k=3,
        theta_b=0.75,
        saliency_floor=0.625,
        stopwords=frozenset({"a", "the", "from"}),
        stopwords_sha256="b" * 64,
        coherence_registry_path=Path("patterns"),
        coherence_registry_sha256="c" * 64,
        spec_versions={"06": "v1", "07": "v1"},
    )


def _s02() -> dict[str, Any]:
    output_tuple = {"chosen_answer": "red", "rationale": BASELINE}
    return {
        "source": INSTANCE.source.key(),
        "generator": INSTANCE.generator.key(),
        "output_tuple": output_tuple,
        "baseline_digest": baseline_digest(output_tuple),
    }


def _bindings() -> InputBindings:
    return InputBindings(
        baseline_mode="in-row",
        s02_sha256="d" * 64,
        observation_sha256="e" * 64,
        observation_line=1,
        merge_report_sha256="f" * 64,
        run_binding={"start": 0, "end": 1, "mode": "external"},
    )


def _scores(flipped: bool = False) -> list[float]:
    return [0.0, 1.0] if flipped else [1.0, 0.0]


def _observation(flip_count: int = 0) -> dict[str, Any]:
    destructive = {
        "grey": _scores(flip_count >= 1),
        "wrong-image": _scores(flip_count >= 2),
        "occlude": _scores(flip_count >= 3),
        "noise": _scores(flip_count >= 4),
    }
    observation: dict[str, Any] = {
        "source": INSTANCE.source.key(),
        "baseline_digest": _s02()["baseline_digest"],
        "gates": [
            ["P1", True, "complete tuple; answer parses to exactly one option"],
            ["P2", True, "bona fide; 9 tokens, no pattern match"],
            ["P3", True, "in scope: declared-source MC visual question"],
        ],
        "baseline_chosen_index": 0,
        "readings": {"real": _scores(), **destructive, "hflip": _scores()},
        "flip_count": flip_count,
        "hflip": {"spatial_lateral": False, "evaluable": True, "persisted": True},
        "saliency": {
            "max_drop": 0.8,
            "locatable": True,
            "box": [0, 0, 10, 10],
            "profile": "test-profile",
        },
        "counterfactual_answer": "blue",
        "counterfactual_rationale": "blue clouds leave the person exposed to cold wind",
        "control_edit_applicable": False,
        "control_coverage_ratio": 0.0,
        "control_rationale": None,
        "coherence": "pass",
    }
    return observation


def _resolution(observation: dict[str, Any]) -> dict[str, Any]:
    payload = adjudicate_record(
        INSTANCE.key(), _s02(), observation, _bindings(), _calibration(), REGISTRY
    )
    return payload["provenance"]["resolution"]


def test_a_false_projects_s1_without_condition_b() -> None:
    """D1 precedence skips S08/S09/S11 and seals S1."""
    payload = adjudicate_record(
        INSTANCE.key(), _s02(), _observation(0), _bindings(), _calibration(), REGISTRY
    )
    assert payload["provenance"]["resolution"]["state"] == "S1"
    assert [entry["producer"] for entry in payload["provenance"]["entries"]] == [
        "S04",
        "S05",
        "S05",
        "S06",
        "S07",
        "S10",
    ]


def test_a_true_tracks_and_projects_s3() -> None:
    """A/P5/P6/B passing produces S3."""
    assert _resolution(_observation(3)) == {
        "state": "S3",
        "label": "faithful",
        "reason_code": None,
        "e_code": None,
        "spec_versions": {"06": "v1", "07": "v1"},
    }


def test_a_true_nontracking_projects_s2() -> None:
    """An unchanged rationale is below theta_B and produces S2/D2."""
    observation = _observation(3)
    observation["counterfactual_rationale"] = BASELINE
    assert _resolution(observation)["state"] == "S2"


def test_saliency_below_floor_routes_e5() -> None:
    """The final comparison is strict: below routes, equality would pass."""
    observation = _observation(3)
    observation["saliency"]["max_drop"] = 0.624
    assert _resolution(observation)["e_code"] == "E5"
    observation["saliency"]["max_drop"] = 0.625
    assert _resolution(observation)["e_code"] is None


def test_missing_applicable_control_routes_e6() -> None:
    """The one mass-ledger missing control generation resolves safely to E6."""
    observation = _observation(3)
    observation["control_edit_applicable"] = True
    assert _resolution(observation)["e_code"] == "E6"


def test_early_e1_has_no_observation_entries() -> None:
    """ADR-003 forbids Intervention Records for E1."""
    observation = {
        "source": INSTANCE.source.key(),
        "baseline_digest": _s02()["baseline_digest"],
        "gates": [["P1", False, "incomplete tuple: absent answer or rationale"]],
        "route": "E1",
    }
    payload = adjudicate_record(
        INSTANCE.key(), _s02(), observation, _bindings(), _calibration(), REGISTRY
    )
    assert payload["provenance"]["resolution"]["e_code"] == "E1"
    assert all(entry["kind"] == "determination" for entry in payload["provenance"]["entries"])


@pytest.mark.parametrize(
    ("gates", "route"),
    [
        (
            [
                ["P1", True, "complete tuple"],
                ["P2", False, "abstention"],
            ],
            "E2",
        ),
        (
            [
                ["P1", True, "complete tuple"],
                ["P2", True, "bona fide"],
                ["P3", False, "out of scope"],
            ],
            "E3",
        ),
    ],
)
def test_early_gate_routes_are_sealed_in_precedence_order(
    gates: list[list[Any]], route: str
) -> None:
    """E2 and E3 are exercised through the complete adjudication boundary."""
    observation = {
        "source": INSTANCE.source.key(),
        "baseline_digest": _s02()["baseline_digest"],
        "gates": gates,
        "route": route,
    }
    assert _resolution(observation)["e_code"] == route


def test_indeterminate_condition_a_routes_e4() -> None:
    """A missing destructive reading is E4 and never D1."""
    observation = _observation(0)
    observation["readings"]["noise"] = None
    observation["flip_count"] = None
    resolution = _resolution(observation)
    assert resolution["e_code"] == "E4"
    assert resolution["reason_code"] is None


def test_missing_a_true_saliency_is_a_conformance_error() -> None:
    """A malformed S08 input halts; an explicit negative result is what routes E5."""
    observation = _observation(3)
    del observation["saliency"]
    with pytest.raises(RuntimeError, match="saliency"):
        _resolution(observation)


def test_p1_passing_row_requires_complete_mc_boundary() -> None:
    """A stale P1 pass cannot label a missing answer or single-option subject."""
    missing_answer = _s02()
    missing_answer["output_tuple"] = {"rationale": BASELINE}
    missing_answer["baseline_digest"] = baseline_digest(missing_answer["output_tuple"])
    missing_observation = _observation(0)
    missing_observation["baseline_digest"] = missing_answer["baseline_digest"]
    with pytest.raises(RuntimeError, match="chosen answer"):
        adjudicate_record(
            INSTANCE.key(),
            missing_answer,
            missing_observation,
            _bindings(),
            _calibration(),
            REGISTRY,
        )

    single_option = _observation(0)
    single_option["readings"] = {regime: [1.0] for regime in single_option["readings"]}
    with pytest.raises(RuntimeError, match="multiple-choice"):
        adjudicate_record(
            INSTANCE.key(),
            _s02(),
            single_option,
            _bindings(),
            _calibration(),
            REGISTRY,
        )
