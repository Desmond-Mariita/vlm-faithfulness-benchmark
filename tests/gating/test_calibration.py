"""Tests for the §5.2 calibration harness (RIP §5.1/§5.2; prereg-v1)."""

from __future__ import annotations

from pathlib import Path

import pytest

from vlm_faithfulness_benchmark.gating.calibration import (
    calibrate_theta_b,
    choose_k,
    load_preregistration,
)

PREREG = load_preregistration(
    Path(__file__).resolve().parents[2] / "config" / "prereg_v1.json"
)


def _fold(center: float, spread: float, n: int = 300) -> list[float]:
    """A deterministic synthetic drift fold around `center`."""
    return [center + spread * ((i % 21) - 10) / 10.0 for i in range(n)]


def test_prereg_loads_with_pinned_values() -> None:
    """The committed pre-registration carries the pinned rule parameters."""
    assert PREREG.prereg_id == "prereg-v1"
    assert PREREG.k_grid == (2, 3)
    assert PREREG.min_pilot_sample == 250


def test_separated_distributions_calibrate_viable() -> None:
    """Well-separated targeted/control folds => viable, midpoint theta."""
    result = calibrate_theta_b(_fold(0.5, 0.2), _fold(0.05, 0.04), PREREG)
    assert result.viable
    assert result.theta_b == pytest.approx((0.5 + 0.05) / 2, abs=0.02)
    assert result.evidence["fraction_control_at_or_above_theta"] <= 0.10


def test_degenerate_targeted_distribution_fires_stop() -> None:
    """RIP §5.1(i): near-zero targeted spread => NOT viable (Charter §6 path)."""
    result = calibrate_theta_b(_fold(0.5, 0.001), _fold(0.05, 0.04), PREREG)
    assert not result.viable
    assert result.evidence["targeted_iqr"] < PREREG.min_targeted_iqr


def test_unseparated_control_fires_stop() -> None:
    """RIP §5.1(ii): control drifting like targeted => NOT viable."""
    result = calibrate_theta_b(_fold(0.5, 0.2), _fold(0.48, 0.2), PREREG)
    assert not result.viable


def test_underpowered_fold_is_conformance_error() -> None:
    """Below the pre-registered minimum is an error, never a verdict."""
    with pytest.raises(AssertionError, match="pre-registered minimum"):
        calibrate_theta_b(_fold(0.5, 0.2, n=100), _fold(0.05, 0.04), PREREG)


def test_choose_k_maximizes_agreement_ties_to_stricter() -> None:
    """K rule: max agreement; ties break to the larger k."""
    assert choose_k({2: 0.71, 3: 0.78}, PREREG) == 3
    assert choose_k({2: 0.80, 3: 0.80}, PREREG) == 3
    assert choose_k({2: 0.82, 3: 0.79}, PREREG) == 2
    with pytest.raises(AssertionError, match="grid"):
        choose_k({1: 0.9, 2: 0.8}, PREREG)
