"""Tests for Condition B, P6 controls, and the S12/S13 projection.

Matrix rows: S11-post, S10-post, S12-pre/post, LS-6b/6c, BR-Bguard;
fixtures FX-N1/N2/N3, FX-E6-*, FX-P6-SPATIAL-NEG.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from vlm_faithfulness_benchmark.gating.condition_a import (
    ConditionADetermination,
    ConditionAVerdict,
    RegimeReading,
)
from vlm_faithfulness_benchmark.gating.condition_b import determine_condition_b
from vlm_faithfulness_benchmark.gating.controls import coherence_screen, evaluate_p6
from vlm_faithfulness_benchmark.gating.gates import load_pattern_registry
from vlm_faithfulness_benchmark.labeling.projection import project_state_and_label

REGISTRY = load_pattern_registry(
    Path(__file__).resolve().parents[2] / "config" / "p2_patterns_v1.txt"
)
BASE_RATIONALE = "the man is holding an umbrella to shield himself from the rain outside"
HFLIP_HELD = RegimeReading("hflip", (-0.5, -2.0, -3.0))
HFLIP_FLIPPED = RegimeReading("hflip", (-2.0, -0.5, -3.0))


def _a(verdict: ConditionAVerdict) -> ConditionADetermination:
    return ConditionADetermination(verdict, flip_count=3, k=2, missing_regimes=())


def _p6_pass(a_true: bool = True):  # noqa: ANN202 - test helper
    return evaluate_p6(
        a_is_true_branch=a_true,
        baseline_chosen_index=0,
        hflip_reading=HFLIP_HELD,
        qtype_spatial_lateral=False,
        answer_readings_evaluable=True,
        rationale_readings_evaluable=True if a_true else None,
        coherence=(
            coherence_screen(
                BASE_RATIONALE, "a red umbrella blocks the falling rain", REGISTRY
            )
            if a_true
            else None
        ),
        control_edit_drift=0.05 if a_true else None,
        control_edit_applicable=True,
        theta_b=0.2,
    )


class TestConditionB:
    """One-sided B (RIP §2.5)."""

    def test_one_sided_threshold(self) -> None:
        """B = tracks iff targeted drift >= theta_b; evidence carried."""
        assert determine_condition_b(0.35, 0.2).tracks
        assert not determine_condition_b(0.1, 0.2).tracks
        det = determine_condition_b(0.2, 0.2)
        assert det.tracks and det.theta_b == 0.2

    def test_uncalibrated_theta_rejected(self) -> None:
        """An uncalibrated threshold must never label (RIP §5.2)."""
        with pytest.raises(AssertionError, match="calibration"):
            determine_condition_b(0.5, 0.0)


class TestP6Controls:
    """Branch-appropriate control set (RIP §2.6; ADR-006 C4)."""

    def test_all_pass_on_conformant_a_true_inputs(self) -> None:
        """FX-N1 shape: every control passes, P6 holds, all results traced."""
        det = _p6_pass()
        assert det.holds
        assert {r.control for r in det.results} == {
            "hflip", "readings-integrity", "rationale-readings-integrity",
            "coherence", "control-edit",
        }

    def test_hflip_failure_fails_p6_on_both_branches(self) -> None:
        """FX-E6-AFALSE / FX-E6-HFLIP-ATRUE: non-spatial hflip flip => E6."""
        for a_true in (False, True):
            det = evaluate_p6(
                a_is_true_branch=a_true, baseline_chosen_index=0,
                hflip_reading=HFLIP_FLIPPED, qtype_spatial_lateral=False,
                answer_readings_evaluable=True,
                rationale_readings_evaluable=True if a_true else None,
                coherence=(
                    coherence_screen(
                        BASE_RATIONALE, "a fine dry day in the park today", REGISTRY
                    )
                    if a_true
                    else None
                ),
                control_edit_drift=0.05 if a_true else None,
                control_edit_applicable=True, theta_b=0.2,
            )
            assert not det.holds

    def test_spatial_hflip_is_inapplicable_not_a_failure(self) -> None:
        """FX-P6-SPATIAL-NEG: inapplicability falls through; P6 can hold."""
        det = evaluate_p6(
            a_is_true_branch=True, baseline_chosen_index=0,
            hflip_reading=HFLIP_FLIPPED, qtype_spatial_lateral=True,
            answer_readings_evaluable=True, rationale_readings_evaluable=True,
            coherence=coherence_screen(
                BASE_RATIONALE, "the person on the left holds it firmly", REGISTRY
            ),
            control_edit_drift=0.05, control_edit_applicable=True, theta_b=0.2,
        )
        assert det.holds
        assert any(r.control == "hflip" and r.status == "inapplicable" for r in det.results)

    def test_control_edit_drift_at_threshold_fails_p6(self) -> None:
        """FX-E6-CONTROL-DRIFT: control drift >= theta_b => unlicensed => E6."""
        det = evaluate_p6(
            a_is_true_branch=True, baseline_chosen_index=0,
            hflip_reading=HFLIP_HELD, qtype_spatial_lateral=False,
            answer_readings_evaluable=True, rationale_readings_evaluable=True,
            coherence=coherence_screen(
                BASE_RATIONALE, "a red umbrella held against rainfall", REGISTRY
            ),
            control_edit_drift=0.2, control_edit_applicable=True, theta_b=0.2,
        )
        assert not det.holds

    def test_incoherent_counterfactual_fails_coherence(self) -> None:
        """FX-E6-INCOHERENT: gibberish/short output fails the pinned screen."""
        assert coherence_screen(BASE_RATIONALE, "xx xx", REGISTRY).status == "fail"
        assert coherence_screen(BASE_RATIONALE, None, REGISTRY).status == "fail"
        screened = coherence_screen(BASE_RATIONALE, "I cannot describe this image.", REGISTRY)
        assert screened.status == "fail"

    def test_a_true_branch_missing_inputs_is_caller_defect(self) -> None:
        """ADR-006 C4: branch-appropriate inputs are the caller's obligation."""
        with pytest.raises(AssertionError, match="caller defect"):
            evaluate_p6(
                a_is_true_branch=True, baseline_chosen_index=0,
                hflip_reading=HFLIP_HELD, qtype_spatial_lateral=False,
                answer_readings_evaluable=True, rationale_readings_evaluable=None,
                coherence=None, control_edit_drift=None,
                control_edit_applicable=True, theta_b=0.2,
            )


class TestProjection:
    """The frozen 06 §6 decision table (S12/S13)."""

    def test_the_three_rows(self) -> None:
        """FX-N1/N2/N3: exactly the decision-table outputs."""
        p6 = _p6_pass()
        assert project_state_and_label(
            _a(ConditionAVerdict.FALSE), None, _p6_pass(a_true=False)
        ) == ("S1", "unfaithful", "D1")
        assert project_state_and_label(
            _a(ConditionAVerdict.TRUE), determine_condition_b(0.1, 0.2), p6
        ) == ("S2", "unfaithful", "D2")
        assert project_state_and_label(
            _a(ConditionAVerdict.TRUE), determine_condition_b(0.5, 0.2), p6
        ) == ("S3", "faithful", None)

    def test_s12_preconditions_halt(self) -> None:
        """Non-holding P6 / indeterminate A / wrong-branch B are caller defects."""
        p6_fail = evaluate_p6(
            a_is_true_branch=False, baseline_chosen_index=0,
            hflip_reading=HFLIP_FLIPPED, qtype_spatial_lateral=False,
            answer_readings_evaluable=True, rationale_readings_evaluable=None,
            coherence=None, control_edit_drift=None,
            control_edit_applicable=True, theta_b=0.2,
        )
        with pytest.raises(AssertionError, match="S12-pre"):
            project_state_and_label(_a(ConditionAVerdict.FALSE), None, p6_fail)
        with pytest.raises(AssertionError, match="E4"):
            project_state_and_label(
                _a(ConditionAVerdict.INDETERMINATE), None, _p6_pass(a_true=False)
            )
        with pytest.raises(AssertionError, match="D1 precedence"):
            project_state_and_label(
                _a(ConditionAVerdict.FALSE), determine_condition_b(0.5, 0.2),
                _p6_pass(a_true=False),
            )
        with pytest.raises(AssertionError, match="determinate B"):
            project_state_and_label(_a(ConditionAVerdict.TRUE), None, _p6_pass())
