"""Tests for gates P1-P3.

Matrix rows P1/P2/P3, S04/S05-post, E-PREC; fixtures FX-E1/FX-N4/FX-E3/FX-E-PREC.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from vlm_faithfulness_benchmark.gating.gates import (
    evaluate_p_gates,
    load_pattern_registry,
)

REGISTRY = load_pattern_registry(
    Path(__file__).resolve().parents[2] / "config" / "p2_patterns_v1.txt"
)
OPTIONS = ("umbrella", "bat", "phone", "cup")
GOOD_RATIONALE = "the man is holding an umbrella to shield himself from rain"


def test_all_gates_pass_on_bona_fide_tuple() -> None:
    """A complete, justified, in-scope tuple passes with no route."""
    dets, e_code = evaluate_p_gates("umbrella", GOOD_RATIONALE, OPTIONS, True, REGISTRY)
    assert e_code is None
    assert [d.gate for d in dets] == ["P1", "P2", "P3"]
    assert all(d.passed for d in dets)


class TestP1:
    """FX-E1: incomplete tuples route E1."""

    def test_absent_rationale_routes_e1(self) -> None:
        """ADR-003: retained incomplete tuple fails P1, never dropped."""
        dets, e_code = evaluate_p_gates("umbrella", None, OPTIONS, True, REGISTRY)
        assert e_code == "E1" and not dets[0].passed

    def test_unparseable_answer_routes_e1(self) -> None:
        """An answer matching zero options is not a complete chosen answer."""
        _, e_code = evaluate_p_gates("banana", GOOD_RATIONALE, OPTIONS, True, REGISTRY)
        assert e_code == "E1"

    def test_answer_matching_two_options_routes_e1(self) -> None:
        """Exactly-one-option parse is required."""
        _, e_code = evaluate_p_gates(
            "umbrella", GOOD_RATIONALE, ("umbrella", "Umbrella "), True, REGISTRY
        )
        assert e_code == "E1"


class TestP2:
    """FX-N4: abstentions route E2; the pinned floor applies."""

    @pytest.mark.parametrize(
        "text",
        [
            "I cannot determine this.",
            "As an AI, I don't have access to the image.",
            "no rationale",
        ],
    )
    def test_registry_match_routes_e2(self, text: str) -> None:
        """Appendix A patterns fail P2 regardless of length."""
        _, e_code = evaluate_p_gates("umbrella", text, OPTIONS, True, REGISTRY)
        assert e_code == "E2"

    def test_below_floor_routes_e2(self) -> None:
        """RIP §2.7: fewer than five tokens is not a bona fide justification."""
        _, e_code = evaluate_p_gates("umbrella", "holding an umbrella", OPTIONS, True, REGISTRY)
        assert e_code == "E2"

    def test_correctness_plays_no_role(self) -> None:
        """ADR-004/CC1: a wrong-but-justified answer passes the gates."""
        dets, e_code = evaluate_p_gates("bat", GOOD_RATIONALE, OPTIONS, True, REGISTRY)
        assert e_code is None and all(d.passed for d in dets)


class TestP3AndPrecedence:
    """FX-E3 and FX-E-PREC."""

    def test_no_image_routes_e3(self) -> None:
        """Out of scope: not a visual question."""
        _, e_code = evaluate_p_gates("umbrella", GOOD_RATIONALE, OPTIONS, False, REGISTRY)
        assert e_code == "E3"

    def test_first_failing_gate_claims_the_route(self) -> None:
        """FX-E-PREC: abstention AND out-of-scope => E2, not E3; one code only."""
        dets, e_code = evaluate_p_gates(
            "umbrella", "I cannot determine this.", OPTIONS, False, REGISTRY
        )
        assert e_code == "E2"
        assert [d.gate for d in dets] == ["P1", "P2"], "later gates not evaluated"


def test_registry_loader_rejects_missing_or_empty(tmp_path: Path) -> None:
    """Running P2 without its pinned registry would be an unpinned label path."""
    with pytest.raises(AssertionError, match="missing"):
        load_pattern_registry(tmp_path / "nope.txt")
    empty = tmp_path / "empty.txt"
    empty.write_text("# only comments\n", encoding="utf-8")
    with pytest.raises(AssertionError, match="empty"):
        load_pattern_registry(empty)
