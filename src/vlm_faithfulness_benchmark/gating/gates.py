"""Gates P1–P3 (S04–S05) under the RIP §2.7 pins (matrix rows P1, P2, P3, S04/S05-post, E-PREC).

Each gate returns a determination carrying its evidence (CC5) — it never
routes by itself; ``evaluate_p_gates`` applies the frozen first-failing-gate
order P1 > P2 > P3 (`06` §9, `07` §6) and names the single E-code, exactly
once. Correctness plays no role anywhere (ADR-004; CC1).

Operational pins consumed (RIP-1.0.0 §2.7, Appendix A):

- P1: chosen answer parseable to exactly one option AND rationale non-empty
  under the pinned `08` N4.6 extraction.
- P2: rationale matches no Appendix A abstention/refusal pattern and meets
  the ≥5-token content floor.
- P3: instance is a multiple-choice visual question with a rationale, in
  the declared source scope.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

__all__ = ["GateDetermination", "load_pattern_registry", "evaluate_p_gates"]

#: RIP §2.7 minimum-content floor (tokens after N4.6 extraction).
P2_MIN_TOKENS = 5


@dataclass(frozen=True, slots=True)
class GateDetermination:
    """One gate's determination with its evidence (CC5).

    Attributes:
        gate: ``"P1"`` | ``"P2"`` | ``"P3"``.
        passed: The determination.
        evidence: What the criterion saw (reconstructable verdict basis).
    """

    gate: str
    passed: bool
    evidence: str


def load_pattern_registry(path: Path) -> tuple[re.Pattern[str], ...]:
    """Load the pinned abstention/refusal registry (RIP Appendix A).

    Args:
        path: Registry file (``config/p2_patterns_v1.txt``); '#' lines are
            comments; patterns are case-insensitive.

    Returns:
        Compiled patterns, in file order.

    Raises:
        AssertionError: If the registry is missing or empty — running P2
            without its pinned registry would be an unpinned label path.
    """
    assert path.is_file(), f"pinned P2 registry missing: {path}"
    patterns = [
        re.compile(line.strip(), re.IGNORECASE)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    assert patterns, "pinned P2 registry is empty"
    return tuple(patterns)


def _determine_p1(
    chosen_answer: str | None, rationale: str | None, options: Sequence[str]
) -> GateDetermination:
    """P1 completeness: answer parseable to exactly one option; rationale non-empty."""
    if chosen_answer is None or rationale is None or not rationale.strip():
        return GateDetermination("P1", False, "incomplete tuple: absent answer or rationale")
    matches = [o for o in options if o.strip().lower() == chosen_answer.strip().lower()]
    if len(matches) != 1:
        return GateDetermination(
            "P1", False, f"chosen answer {chosen_answer!r} parses to {len(matches)} options"
        )
    return GateDetermination("P1", True, "complete tuple; answer parses to exactly one option")


def _determine_p2(
    rationale: str, registry: Sequence[re.Pattern[str]]
) -> GateDetermination:
    """P2 bona fide justification: no registry match; content floor met."""
    for pattern in registry:
        if pattern.search(rationale):
            return GateDetermination("P2", False, f"abstention pattern {pattern.pattern!r}")
    token_count = len(rationale.split())
    if token_count < P2_MIN_TOKENS:
        return GateDetermination(
            "P2", False, f"content floor: {token_count} < {P2_MIN_TOKENS} tokens"
        )
    return GateDetermination("P2", True, f"bona fide; {token_count} tokens, no pattern match")


def _determine_p3(options: Sequence[str], has_image: bool) -> GateDetermination:
    """P3 scope: a multiple-choice visual question (structural check only)."""
    if not has_image:
        return GateDetermination("P3", False, "out of scope: no image reference")
    if len(options) < 2:
        return GateDetermination("P3", False, "out of scope: not multiple-choice")
    return GateDetermination("P3", True, "in scope: multiple-choice visual question")


def evaluate_p_gates(
    chosen_answer: str | None,
    rationale: str | None,
    options: Sequence[str],
    has_image: bool,
    registry: Sequence[re.Pattern[str]],
) -> tuple[tuple[GateDetermination, ...], str | None]:
    """Run P1–P3 in the frozen gate order and name the single route, if any.

    All three determinations are recorded (CC5 — evidence is retained even
    past the first failure is NOT required by the specs; the first failing
    gate claims the route and later gates are not evaluated, mirroring
    `06` §9's deterministic precedence).

    Args:
        chosen_answer: Emitted answer (None if generation omitted it).
        rationale: Rationale object under the pinned N4.6 extraction
            (None/empty if absent).
        options: The instance's multiple-choice options.
        has_image: Whether the Source Record carries an image reference.
        registry: The pinned P2 pattern registry.

    Returns:
        (determinations-in-order, e_code) where ``e_code`` is ``"E1"`` /
        ``"E2"`` / ``"E3"`` for the FIRST failing gate, or None when all
        pass. Exactly one E-code, by construction (E-PREC).
    """
    p1 = _determine_p1(chosen_answer, rationale, options)
    if not p1.passed:
        return (p1,), "E1"
    assert rationale is not None  # P1 passed ⇒ rationale present
    p2 = _determine_p2(rationale, registry)
    if not p2.passed:
        return (p1, p2), "E2"
    p3 = _determine_p3(options, has_image)
    if not p3.passed:
        return (p1, p2, p3), "E3"
    return (p1, p2, p3), None
