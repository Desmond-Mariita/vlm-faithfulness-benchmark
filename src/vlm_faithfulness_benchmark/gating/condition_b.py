"""Drift instrument and the one-sided Condition B determination (S11; RIP §2.4/§2.5).

Matrix rows: S11-post, S11-track, BR-S2/S3, LS-4a; RIP-1.0.0 §2.5.

Condition B is **one-sided** (review-hardened RIP §2.5): B = tracks iff the
targeted-edit drift ≥ θ_B. Attribution of the signal to the located
evidence is P6's job (§2.6(d)), evaluated before B ever runs — by the time
S11 executes, its input is determinate by construction (`06` §8.2: no
inconclusive B outcome exists).

The drift instrument is BERTScore-F1 (``roberta-large``, pinned revision)
between the exact baseline rationale and the counterfactual rationale;
drift = 1 − F1 (RIP §2.4). It is a similarity instrument producing the CC5
graded reading — it never scores plausibility, grounding, or agreement with
the image or any label (CC1 / `06` I2 defense recorded in the RIP). The
heavy model loads lazily; the determination logic is pure.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "DRIFT_INSTRUMENT_ID",
    "ConditionBDetermination",
    "compute_drift",
    "determine_condition_b",
]

#: The pinned drift instrument identity (recorded in provenance).
DRIFT_INSTRUMENT_ID = "bertscore-f1;roberta-large;drift=1-F1"


@dataclass(frozen=True, slots=True)
class ConditionBDetermination:
    """The S11 determination with its reconstructable evidence (CC5).

    Attributes:
        tracks: The binary verdict (`06` §4: tracks / does-not-track).
        targeted_drift: The graded reading consumed.
        theta_b: The calibrated threshold consumed.
    """

    tracks: bool
    targeted_drift: float
    theta_b: float


def compute_drift(baseline_rationale: str, counterfactual_rationale: str) -> float:
    """Measure rationale drift under the pinned instrument (RIP §2.4).

    LaTeX is above the return expression; the instrument compares the two
    texts and nothing else.

    Args:
        baseline_rationale: The exact digest-verified baseline rationale
            (CC4 — never regenerated).
        counterfactual_rationale: The rationale emitted on the edited input.

    Returns:
        drift in [0, 1]-ish (1 − BERTScore-F1; F1 can dip slightly negative
        on pathological pairs, so drift may slightly exceed 1).

    Raises:
        AssertionError: On empty inputs — an absent counterfactual rationale
            is a P6 readings-integrity matter (§2.6(b′)), never scored here.
    """
    assert baseline_rationale.strip(), "empty baseline rationale reaches S11 only by defect"
    assert counterfactual_rationale.strip(), (
        "absent counterfactual rationale is a P6 (b′) matter, not a drift input"
    )
    from bert_score import score as bertscore  # type: ignore[import-untyped]  # heavy

    _, _, f1 = bertscore(
        [counterfactual_rationale], [baseline_rationale], model_type="roberta-large", lang="en"
    )
    # LaTeX: d = 1 - F1_{BERTScore}(r_{cf}, r_{base})
    return float(1.0 - f1[0].item())


def determine_condition_b(targeted_drift: float, theta_b: float) -> ConditionBDetermination:
    """Determine Condition B, one-sided (RIP §2.5).

    Args:
        targeted_drift: Drift under the evidence-matched edit (S09 reading).
        theta_b: The calibrated threshold (RIP §5.2; the legacy 0.3 is
            pre-registered as NOT inherited — any value must come from the
            calibration record).

    Returns:
        The determination; deterministic and total for finite inputs.

    Raises:
        AssertionError: On non-finite drift or a non-positive θ_B (an
            uncalibrated threshold must never label).
    """
    assert targeted_drift == targeted_drift and abs(targeted_drift) != float("inf"), (
        "non-finite drift is a conformance error"
    )
    assert theta_b > 0.0, "theta_b must come from the §5.2 calibration record"
    # LaTeX: B = [\, d_{targeted} \ge \theta_B \,]
    return ConditionBDetermination(
        tracks=targeted_drift >= theta_b, targeted_drift=targeted_drift, theta_b=theta_b
    )
