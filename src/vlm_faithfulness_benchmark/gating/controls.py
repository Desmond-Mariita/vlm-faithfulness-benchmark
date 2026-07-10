"""P6 control evaluation (S10; RIP-1.0.0 §2.6).

Matrix rows: S10-pre/post/trace, BR-AfalseE6, BR-AtrueE6, BR-Bguard,
ADR-006 C1–C8 (branch-appropriate evidence).

P6 asks whether the controls licensing a causal reading hold for this
instance. Controls are branch-appropriate (ADR-006 C4): the A-false branch
requires only the answer-side controls; the A-true branch adds the
rationale-side controls. Any required-and-applicable control failing → E6
(never D1/D2/E4). An inapplicable control (spatial-lateral hflip;
filled-image control edit) is recorded as inapplicable, and coverage falls
to the remaining controls (RIP §2.6) — inapplicability is never a failure.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence

from vlm_faithfulness_benchmark.gating.condition_a import RegimeReading

__all__ = ["ControlResult", "P6Determination", "coherence_screen", "evaluate_p6"]

#: Coherence screen bounds (RIP §2.6(c), pinned).
_MIN_ABS_TOKENS = 5
_MIN_FRACTION = 0.25
_MAX_FRACTION = 4.0


@dataclass(frozen=True, slots=True)
class ControlResult:
    """One control's outcome (S10-trace records all of these).

    Attributes:
        control: Control id: ``hflip`` | ``readings-integrity`` |
            ``rationale-readings-integrity`` | ``coherence`` |
            ``control-edit``.
        status: ``pass`` | ``fail`` | ``inapplicable``.
        evidence: What the control saw (CC5).
    """

    control: str
    status: str
    evidence: str


@dataclass(frozen=True, slots=True)
class P6Determination:
    """The S10 determination: P6 holds iff no applicable control failed.

    Attributes:
        holds: True iff every required-and-applicable control passed.
        results: Every control's recorded outcome, branch-appropriate set.
    """

    holds: bool
    results: tuple[ControlResult, ...]


def coherence_screen(
    baseline_rationale: str,
    counterfactual_rationale: str | None,
    registry: Sequence[re.Pattern[str]],
) -> ControlResult:
    """Apply the pinned coherence/length screen to the counterfactual (RIP §2.6(c)).

    Structural form checks only (CC1-exempt class, same footing as P2):
    non-empty, whitespace-token length within
    ``[max(5, 25% of baseline), 400% of baseline]``, and no Appendix A
    registry match.

    Args:
        baseline_rationale: The digest-verified baseline rationale.
        counterfactual_rationale: The rationale emitted on the edited input
            (None = absent; that is a (b′) readings matter, reported here as
            fail for the caller's E6 only when the caller marks (b′) — this
            screen treats absence as fail with explicit evidence).
        registry: The pinned Appendix A pattern registry.

    Returns:
        The control result.
    """
    if counterfactual_rationale is None or not counterfactual_rationale.strip():
        return ControlResult("coherence", "fail", "counterfactual rationale absent/empty")
    n_base = len(baseline_rationale.split())
    n_cf = len(counterfactual_rationale.split())
    floor = max(_MIN_ABS_TOKENS, int(_MIN_FRACTION * n_base))
    ceiling = int(_MAX_FRACTION * n_base)
    if not floor <= n_cf <= ceiling:
        return ControlResult(
            "coherence", "fail", f"length {n_cf} outside [{floor}, {ceiling}] (base {n_base})"
        )
    for pattern in registry:
        if pattern.search(counterfactual_rationale):
            return ControlResult("coherence", "fail", f"registry match {pattern.pattern!r}")
    return ControlResult("coherence", "pass", f"coherent; {n_cf} tokens within bounds")


def evaluate_p6(
    a_is_true_branch: bool,
    baseline_chosen_index: int,
    hflip_reading: RegimeReading | None,
    qtype_spatial_lateral: bool,
    answer_readings_evaluable: bool,
    rationale_readings_evaluable: bool | None,
    coherence: ControlResult | None,
    control_edit_drift: float | None,
    control_edit_applicable: bool,
    theta_b: float,
) -> P6Determination:
    """Evaluate the branch-appropriate P6 control set (RIP §2.6).

    Args:
        a_is_true_branch: Which branch's control set applies (ADR-006 C4;
            the A-false branch needs only answer-side controls).
        baseline_chosen_index: The baseline chosen option (for the hflip
            persistence check).
        hflip_reading: The hflip regime reading, or None if non-evaluable.
        qtype_spatial_lateral: True when the pinned question-type mapping
            marks hflip non-semantics-preserving (control inapplicable).
        answer_readings_evaluable: Control (b): all §2.1 readings evaluable.
        rationale_readings_evaluable: Control (b′), A-true branch only
            (None on the A-false branch, where it is not required).
        coherence: Control (c) result, A-true branch only (None otherwise).
        control_edit_drift: Control (d) drift reading, A-true branch only.
        control_edit_applicable: False when no disjoint control placement
            exists (evidence box fills the image).
        theta_b: The calibrated threshold (control drift ≥ θ_B ⇒ E6).

    Returns:
        The determination with every control's recorded outcome (S10-trace).

    Raises:
        AssertionError: If A-true-branch controls are missing on the A-true
            branch — a caller defect, not a control failure.
    """
    results: list[ControlResult] = []

    if qtype_spatial_lateral:
        results.append(ControlResult("hflip", "inapplicable", "spatial-lateral qtype"))
    elif hflip_reading is None or not hflip_reading.evaluable():
        results.append(ControlResult("hflip", "fail", "hflip reading non-evaluable"))
    elif hflip_reading.argmax_option() != baseline_chosen_index:
        results.append(ControlResult("hflip", "fail", "baseline choice did not persist"))
    else:
        results.append(ControlResult("hflip", "pass", "baseline choice persisted"))

    results.append(
        ControlResult(
            "readings-integrity",
            "pass" if answer_readings_evaluable else "fail",
            "all answer-side regime readings evaluable"
            if answer_readings_evaluable
            else "answer-side reading(s) non-evaluable",
        )
    )

    if a_is_true_branch:
        assert rationale_readings_evaluable is not None and coherence is not None, (
            "caller defect: A-true branch requires (b′) and (c) inputs"
        )
        results.append(
            ControlResult(
                "rationale-readings-integrity",
                "pass" if rationale_readings_evaluable else "fail",
                "S09 + control-edit readings evaluable"
                if rationale_readings_evaluable
                else "rationale-side reading(s) non-evaluable",
            )
        )
        results.append(coherence)
        if not control_edit_applicable:
            results.append(
                ControlResult("control-edit", "inapplicable", "no disjoint placement exists")
            )
        else:
            assert control_edit_drift is not None, "caller defect: applicable control needs drift"
            failed = control_edit_drift >= theta_b
            results.append(
                ControlResult(
                    "control-edit",
                    "fail" if failed else "pass",
                    f"control drift {control_edit_drift:.4f} vs theta_b {theta_b:.4f}",
                )
            )

    holds = all(r.status != "fail" for r in results)
    return P6Determination(holds=holds, results=tuple(results))
