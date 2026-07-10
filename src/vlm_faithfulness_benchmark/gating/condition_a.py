"""Graded regime readings and the Condition A determination (S07).

Matrix rows: S07-post, S07-noE4corr, BR-E4, E4≠D1, CC5; RIP-1.0.0 §2.2.

A reading is the per-option log-likelihood vector for one regime (CC5: the
graded surface is retained, never only the hard choice). Condition A is a
**total** function of the four destructive-regime readings (review-hardened
RIP §2.2): with all four evaluable, the answer is image-dependent iff the
baseline-chosen option ceases to be argmax under ≥ k regimes, determinately
not image-dependent iff under fewer than k (including zero); indeterminate
— routed E4, never S1/D1 — exactly when any of the four is non-evaluable
after the design §5.3 retry policy.

Answer correctness plays no role anywhere (ADR-004; the determination never
sees a gold answer).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from vlm_faithfulness_benchmark.gating.regimes import DESTRUCTIVE_REGIMES

__all__ = ["RegimeReading", "ConditionAVerdict", "ConditionADetermination", "determine_condition_a"]


@dataclass(frozen=True, slots=True)
class RegimeReading:
    """One regime's graded reading (CC5).

    Attributes:
        regime: The regime name (member of ``REGIMES``).
        option_loglikelihoods: Per-option log-likelihoods under the
            generator for this regime's input, or None when the reading is
            non-evaluable after the retry policy (D-ERR3 boundary).
    """

    regime: str
    option_loglikelihoods: tuple[float, ...] | None

    def evaluable(self) -> bool:
        """Return True iff this reading can be consumed by a determination."""
        return self.option_loglikelihoods is not None

    def argmax_option(self) -> int:
        """Return the index of the highest-likelihood option.

        Raises:
            AssertionError: If the reading is non-evaluable.
        """
        assert self.option_loglikelihoods is not None, "non-evaluable reading has no argmax"
        scores = self.option_loglikelihoods
        return max(range(len(scores)), key=scores.__getitem__)


class ConditionAVerdict(Enum):
    """The three-way S07 verdict (`07` §5 S07)."""

    TRUE = "image-dependent"
    FALSE = "not-image-dependent"
    INDETERMINATE = "indeterminate"


@dataclass(frozen=True, slots=True)
class ConditionADetermination:
    """The S07 determination with its reconstructable evidence (CC5).

    Attributes:
        verdict: The three-way outcome.
        flip_count: Destructive regimes where the baseline choice ceased to
            be argmax (meaningful only when all four are evaluable).
        k: The calibrated threshold consumed (recorded for reconstruction).
        missing_regimes: Regimes whose readings were non-evaluable.
    """

    verdict: ConditionAVerdict
    flip_count: int
    k: int
    missing_regimes: tuple[str, ...]


# LaTeX: A = [\, |\{ r : \arg\max s_r \ne c \}| \ge k \,] over the four
# destructive regimes r, with c the baseline chosen index; total for complete
# readings, indeterminate otherwise (RIP §2.2).
def determine_condition_a(
    baseline_chosen_index: int,
    readings: dict[str, RegimeReading],
    k: int,
) -> ConditionADetermination:
    """Determine Condition A over the destructive-regime readings (RIP §2.2).

    Args:
        baseline_chosen_index: The option index the generator chose on the
            unperturbed input (the exact emitted answer — CC4; never a gold
            answer).
        readings: Regime name → reading; must cover all four destructive
            regimes (a wholly absent regime is a caller defect, not
            indeterminacy).
        k: The calibrated flip threshold (RIP §5.2; k ∈ {2, 3}).

    Returns:
        The determination; INDETERMINATE iff any destructive reading is
        non-evaluable (→ E4 at S07, never S1/D1).

    Raises:
        AssertionError: If a destructive regime has no reading entry at all,
            or k is outside the pre-registered grid.
    """
    assert k in (2, 3), f"k={k} outside the pre-registered grid {{2, 3}} (RIP §2.2/§5.2)"
    missing = tuple(r for r in DESTRUCTIVE_REGIMES if r not in readings)
    assert not missing, f"caller defect: no reading entry for {missing}"

    non_evaluable = tuple(
        r for r in DESTRUCTIVE_REGIMES if not readings[r].evaluable()
    )
    if non_evaluable:
        return ConditionADetermination(
            ConditionAVerdict.INDETERMINATE, flip_count=-1, k=k, missing_regimes=non_evaluable
        )
    flip_count = sum(
        1 for r in DESTRUCTIVE_REGIMES if readings[r].argmax_option() != baseline_chosen_index
    )
    verdict = ConditionAVerdict.TRUE if flip_count >= k else ConditionAVerdict.FALSE
    return ConditionADetermination(verdict, flip_count=flip_count, k=k, missing_regimes=())
