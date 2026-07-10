"""S12/S13 — Behavioural State assignment and Label projection (C4).

Matrix rows: S12-pre/post, S13-post, LS-5a/5b, LS-6a/6b/6c, I1–I5, D1-PREC,
BR-S1/S2/S3; `06` §§5–6 (the frozen decision table).

Pure functions over determinate upstream determinations. No candidate
reaches here without P6 recorded as holding, a determinate Condition A,
and — on the A-true path — a determinate Condition B (S12-pre); violations
are caller defects and halt. D1 precedence is structural: B is never
consulted on the A-false path (`06` §6/§8.3).

The projection output feeds ``SealedResolution`` directly, whose
constructor independently re-enforces the same decision table — two layers,
one frozen source of truth.
"""

from __future__ import annotations

from vlm_faithfulness_benchmark.gating.condition_a import (
    ConditionADetermination,
    ConditionAVerdict,
)
from vlm_faithfulness_benchmark.gating.condition_b import ConditionBDetermination
from vlm_faithfulness_benchmark.gating.controls import P6Determination

__all__ = ["project_state_and_label"]


# LaTeX: (S, \ell, \delta) = \begin{cases}
#   (S1, \text{unfaithful}, D1) & \neg A \\
#   (S2, \text{unfaithful}, D2) & A \wedge \neg B \\
#   (S3, \text{faithful}, \varnothing) & A \wedge B
# \end{cases}  — the frozen `06` §6 decision table, total over eligible inputs.
def project_state_and_label(
    condition_a: ConditionADetermination,
    condition_b: ConditionBDetermination | None,
    p6: P6Determination,
) -> tuple[str, str, str | None]:
    """Project the Behavioural State and Label (S12 → S13).

    Args:
        condition_a: The determinate S07 outcome (INDETERMINATE candidates
            were routed E4 upstream and never reach S12).
        condition_b: The S11 outcome on the A-true path; MUST be None on the
            A-false path (D1 precedence: B is never assessed there).
        p6: The S10 determination; MUST hold (P6 failures routed E6
            upstream).

    Returns:
        ``(state, label, reason_code)`` — exactly one row of the `06` §6
        decision table.

    Raises:
        AssertionError: On any S12-pre violation: non-holding P6,
            indeterminate A, B present on the A-false path, or B absent on
            the A-true path. All are caller defects (conformance errors),
            never routes.
    """
    assert p6.holds, "S12-pre: no state without P6 (route E6 upstream, not here)"
    assert condition_a.verdict is not ConditionAVerdict.INDETERMINATE, (
        "S12-pre: indeterminate A is E4, never a state"
    )
    if condition_a.verdict is ConditionAVerdict.FALSE:
        assert condition_b is None, (
            "D1 precedence (06 §6/§8.3): Condition B is never assessed on the A-false path"
        )
        return ("S1", "unfaithful", "D1")
    assert condition_b is not None, "S12-pre: A-true path requires a determinate B"
    if condition_b.tracks:
        return ("S3", "faithful", None)
    return ("S2", "unfaithful", "D2")
