"""Calibration-lock verification and frozen-value reproduction tests."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest

from vlm_faithfulness_benchmark.gating.condition_b import compute_drift
from vlm_faithfulness_benchmark.labeling.calibration_lock import load_calibration_lock

ROOT = Path(__file__).resolve().parents[2]


def test_accepted_lock_verifies_all_sources() -> None:
    """The machine-consumed values are bound to every accepted source hash."""
    lock = load_calibration_lock(ROOT / "config/calibration_lock_v1.json", ROOT)
    assert lock.k == 3
    assert lock.theta_b == 0.7558573853989813
    assert lock.saliency_floor == 0.625
    assert len(lock.lock_sha256) == 64


def test_confirmatory_values_reproduce_exactly() -> None:
    """Raw accepted calibration rows reproduce theta_B and the saliency floor."""
    lock = load_calibration_lock(ROOT / "config/calibration_lock_v1.json", ROOT)
    baselines: dict[str, str] = {}
    with (ROOT / "data/runs/confirm-s02.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            instance = row["key"].removesuffix("::output_tuple")
            baselines[instance] = row["payload"]["output_tuple"]["rationale"]

    control_drifts: list[float] = []
    saliency_drops: list[float] = []
    with (ROOT / "data/runs/confirm-obs.jsonl").open(encoding="utf-8") as handle:
        for position, line in enumerate(handle):
            if position % 2:
                continue
            row = json.loads(line)
            instance = row["key"].removesuffix("::pilot_obs")
            payload = row["payload"]
            control = payload.get("control_rationale")
            if isinstance(control, str):
                control_drifts.append(
                    compute_drift(baselines[instance], control, lock.stopwords)
                )
            saliency_drops.append(float(payload["saliency"]["max_drop"]))

    assert len(control_drifts) == 47
    assert float(np.quantile(control_drifts, 0.9, method="linear")) == lock.theta_b
    assert float(np.quantile(saliency_drops, 0.1, method="linear")) == lock.saliency_floor


@pytest.mark.parametrize(
    "path,value",
    [
        (("condition_a", "rule"), "flip_count > k"),
        (("condition_a", "source_role"), "prereg-v2"),
        (("condition_b", "normalization"), "casefold"),
        (("condition_b", "rule"), "targeted_drift > theta_b"),
        (("condition_b", "threshold_source_role"), "prereg-v3"),
        (("saliency", "source_role"), "prereg-v1"),
    ],
)
def test_semantic_lock_mutations_are_rejected(
    tmp_path: Path, path: tuple[str, str], value: str
) -> None:
    """Every declarative semantic field is checked, not silently ignored."""
    document = json.loads((ROOT / "config/calibration_lock_v1.json").read_text())
    mutated = deepcopy(document)
    mutated[path[0]][path[1]] = value
    candidate = tmp_path / "calibration-lock.json"
    candidate.write_text(json.dumps(mutated), encoding="utf-8")
    with pytest.raises(RuntimeError):
        load_calibration_lock(candidate, ROOT)
