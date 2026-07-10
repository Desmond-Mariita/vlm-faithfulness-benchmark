"""Tests for Condition A (matrix rows S07-post, BR-E4, E4!=D1; fixtures FX-N5, FX-A-TOTAL)."""

from __future__ import annotations

import pytest

from vlm_faithfulness_benchmark.gating.condition_a import (
    ConditionAVerdict,
    RegimeReading,
    determine_condition_a,
)

BASELINE_CHOSEN = 0  # option 0 has the highest baseline likelihood


def _readings(flips: int, non_evaluable: tuple[str, ...] = ()) -> dict[str, RegimeReading]:
    """Build destructive-regime readings with the first `flips` regimes flipped."""
    regimes = ("grey", "wrong-image", "occlude", "noise")
    out: dict[str, RegimeReading] = {}
    for i, regime in enumerate(regimes):
        if regime in non_evaluable:
            out[regime] = RegimeReading(regime, None)
        elif i < flips:
            out[regime] = RegimeReading(regime, (-2.0, -0.5, -3.0, -4.0))  # argmax=1: flipped
        else:
            out[regime] = RegimeReading(regime, (-0.5, -2.0, -3.0, -4.0))  # argmax=0: held
    return out


@pytest.mark.parametrize(
    "flips,k,expected",
    [
        (0, 2, ConditionAVerdict.FALSE),
        (1, 2, ConditionAVerdict.FALSE),  # FX-A-TOTAL: below k is determinate FALSE
        (2, 2, ConditionAVerdict.TRUE),
        (4, 2, ConditionAVerdict.TRUE),
        (2, 3, ConditionAVerdict.FALSE),
        (3, 3, ConditionAVerdict.TRUE),
    ],
)
def test_totality_over_complete_readings(
    flips: int, k: int, expected: ConditionAVerdict
) -> None:
    """RIP §2.2: every complete reading set yields a determinate verdict."""
    det = determine_condition_a(BASELINE_CHOSEN, _readings(flips), k)
    assert det.verdict is expected
    assert det.flip_count == flips
    assert det.missing_regimes == ()


def test_non_evaluable_reading_is_indeterminate_never_false(  # FX-N5
) -> None:
    """A missing reading => INDETERMINATE (E4), regardless of visible flips."""
    det = determine_condition_a(BASELINE_CHOSEN, _readings(1, non_evaluable=("noise",)), 2)
    assert det.verdict is ConditionAVerdict.INDETERMINATE
    assert det.missing_regimes == ("noise",)


def test_wholly_absent_regime_is_a_caller_defect() -> None:
    """No entry at all is a conformance error, not indeterminacy."""
    readings = _readings(0)
    del readings["grey"]
    with pytest.raises(AssertionError, match="caller defect"):
        determine_condition_a(BASELINE_CHOSEN, readings, 2)


def test_k_outside_preregistered_grid_rejected() -> None:
    """RIP §5.2 pre-registers k in {2,3}; k=1 is excluded."""
    with pytest.raises(AssertionError, match="pre-registered"):
        determine_condition_a(BASELINE_CHOSEN, _readings(2), 1)


def test_evidence_supports_reconstruction() -> None:
    """CC5: verdict basis (flip count, k) is carried in the determination."""
    det = determine_condition_a(BASELINE_CHOSEN, _readings(3), 2)
    assert (det.flip_count, det.k) == (3, 2)


def test_argmax_requires_evaluable_reading() -> None:
    """Reading surface guards its own preconditions."""
    with pytest.raises(AssertionError):
        RegimeReading("grey", None).argmax_option()
