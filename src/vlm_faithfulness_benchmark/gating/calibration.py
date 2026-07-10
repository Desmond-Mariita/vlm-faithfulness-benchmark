"""§5.2 calibration harness — θ_B, viability, and k selection (RIP §5.1–§5.2).

Matrix rows: CONF-repro (calibration values are release evidence), RIP §5
gates; consumed at the M8 pilot (V1-045–048).

All rules and margins come from the committed pre-registration config
(``config/prereg_v1.json``) — this module implements them mechanically and
refuses to run without the config (an uncalibrated or ad-hoc threshold must
never label). Viability failure is a STOP outcome escalated under Charter
§6 machinery (plan §7); it is never softened here.
"""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

__all__ = [
    "PreRegistration",
    "CalibrationResult",
    "load_preregistration",
    "calibrate_theta_b",
    "saliency_floor",
    "fold_of",
    "choose_k",
]


@dataclass(frozen=True, slots=True)
class PreRegistration:
    """The committed pre-registration (RIP §5.1–§5.2).

    Attributes:
        prereg_id: The registration identifier (enters the manifest).
        min_targeted_iqr: Viability: minimum IQR of targeted drifts.
        min_fraction_targeted: Viability: minimum targeted fraction ≥ θ_B.
        max_fraction_control: Viability: maximum control fraction ≥ θ_B.
        k_grid: The pre-registered k grid.
        min_pilot_sample: Minimum pilot sample size.
    """

    prereg_id: str
    min_targeted_iqr: float
    min_fraction_targeted: float
    max_fraction_control: float
    k_grid: tuple[int, ...]
    min_pilot_sample: int
    saliency_floor_percentile: int


@dataclass(frozen=True, slots=True)
class CalibrationResult:
    """The θ_B calibration outcome (release evidence).

    Attributes:
        viable: The RIP §5.1 gate outcome; False is a STOP (Charter §6).
        theta_b: The calibrated threshold (meaningful iff viable).
        evidence: Every measured quantity behind the decision (CC5-style).
    """

    viable: bool
    theta_b: float
    evidence: dict[str, float]


def load_preregistration(path: Path) -> PreRegistration:
    """Load and validate the committed pre-registration config.

    Args:
        path: ``config/prereg_v1.json``.

    Raises:
        AssertionError: If missing or malformed — calibration never runs on
            defaults.
    """
    assert path.is_file(), f"pre-registration missing: {path} (RIP §5.2)"
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert "saliency_floor_rule" in raw and "fold_rule" in raw, (
        "pre-registration must fix the saliency floor and fold rules"
    )
    v = raw["viability"]
    return PreRegistration(
        prereg_id=raw["id"],
        min_targeted_iqr=float(v["min_targeted_iqr"]),
        min_fraction_targeted=float(v["min_fraction_targeted_at_or_above_theta"]),
        max_fraction_control=float(v["max_fraction_control_at_or_above_theta"]),
        k_grid=tuple(int(k) for k in raw["k_grid"]),
        min_pilot_sample=int(raw["min_pilot_sample"]),
        saliency_floor_percentile=10,  # from saliency_floor_rule (prereg-v1, fixed text)
    )
    # The registered rules must be present verbatim; their absence would leave
    # free choice at pilot time (review Majors: unregistered floor/fold rules).



def _iqr(values: Sequence[float]) -> float:
    """Interquartile range (inclusive-median quantiles, pinned)."""
    qs = statistics.quantiles(values, n=4, method="inclusive")
    return qs[2] - qs[0]


# LaTeX: \theta_B = \tfrac{1}{2}(\mathrm{med}(d_{ctrl}) + \mathrm{med}(d_{tgt}));
# viable iff IQR(d_tgt) >= a and P(d_tgt >= theta_B) >= b
#            and P(d_ctrl >= theta_B) <= c.
def calibrate_theta_b(
    targeted_drifts: Sequence[float],
    control_drifts: Sequence[float],
    prereg: PreRegistration,
) -> CalibrationResult:
    """Calibrate θ_B and decide viability per the pre-registered rules.

    Args:
        targeted_drifts: Calibration-fold drifts under the evidence-matched
            edit (one per candidate).
        control_drifts: Calibration-fold drifts under the control edit.
        prereg: The committed pre-registration.

    Returns:
        CalibrationResult; ``viable=False`` means the RIP §5.1 stop rule
        fired — the caller escalates, never weakens.

    Raises:
        AssertionError: On samples below the pre-registered minimum — an
            underpowered calibration is a conformance error, not a verdict.
    """
    assert len(targeted_drifts) >= prereg.min_pilot_sample, (
        f"calibration fold {len(targeted_drifts)} < pre-registered minimum "
        f"{prereg.min_pilot_sample}"
    )
    assert len(control_drifts) >= prereg.min_pilot_sample, "control fold underpowered"

    med_targeted = statistics.median(targeted_drifts)
    med_control = statistics.median(control_drifts)
    theta_b = (med_targeted + med_control) / 2.0
    targeted_iqr = _iqr(targeted_drifts)
    frac_targeted = sum(1 for d in targeted_drifts if d >= theta_b) / len(targeted_drifts)
    frac_control = sum(1 for d in control_drifts if d >= theta_b) / len(control_drifts)

    viable = (
        theta_b > 0.0  # registered: viability.min_theta_b_exclusive
        and targeted_iqr >= prereg.min_targeted_iqr
        and frac_targeted >= prereg.min_fraction_targeted
        and frac_control <= prereg.max_fraction_control
    )
    return CalibrationResult(
        viable=viable,
        theta_b=theta_b,
        evidence={
            "median_targeted": med_targeted,
            "median_control": med_control,
            "targeted_iqr": targeted_iqr,
            "fraction_targeted_at_or_above_theta": frac_targeted,
            "fraction_control_at_or_above_theta": frac_control,
            "n_targeted": float(len(targeted_drifts)),
            "n_control": float(len(control_drifts)),
        },
    )


def saliency_floor(calibration_fold_max_drops: Sequence[float], prereg: PreRegistration) -> float:
    """Compute the flat-saliency floor per the registered rule (prereg-v1).

    Args:
        calibration_fold_max_drops: Per-candidate max sweep drops on the
            calibration fold only.
        prereg: The committed pre-registration.

    Returns:
        The floor (the registered percentile of the fold's max drops).

    Raises:
        AssertionError: On an underpowered fold.
    """
    assert len(calibration_fold_max_drops) >= prereg.min_pilot_sample, "fold underpowered"
    qs = statistics.quantiles(calibration_fold_max_drops, n=100, method="inclusive")
    return qs[prereg.saliency_floor_percentile - 1]


def fold_of(identity_sorted_position: int) -> str:
    """Assign a pilot candidate to its fold per the registered rule (prereg-v1).

    Args:
        identity_sorted_position: The candidate's position in the
            identity-sorted pilot sample.

    Returns:
        ``"calibration"`` (even positions) or ``"verification"`` (odd).
    """
    return "calibration" if identity_sorted_position % 2 == 0 else "verification"


def choose_k(
    agreement_by_k: dict[int, float],
    prereg: PreRegistration,
) -> int:
    """Choose k on the human calibration fold (RIP §5.2; pre-registered rule).

    Args:
        agreement_by_k: Human-agreement rate per candidate k, measured on
            the calibration fold only (the verification fold stays sealed
            until k and θ_B are frozen).
        prereg: The committed pre-registration (supplies the k grid).

    Returns:
        The k maximizing agreement; ties break to the larger k (the
        stricter image-dependence requirement).

    Raises:
        AssertionError: If the measured grid differs from the
            pre-registered grid.
    """
    assert set(agreement_by_k) == set(prereg.k_grid), (
        f"measured grid {sorted(agreement_by_k)} != pre-registered {sorted(prereg.k_grid)}"
    )
    best = max(agreement_by_k.values())
    return max(k for k, a in agreement_by_k.items() if a == best)
