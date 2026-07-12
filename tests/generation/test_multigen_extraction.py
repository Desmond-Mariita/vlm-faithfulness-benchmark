"""Tests for the M9 multi-generator extraction contracts (N4.6, CC4).

Covers the shared core (mc_extraction), the GLM think-block contract, the
DeepSeek/Kimi pass-through contracts, the scorer span locator, and the
no-drift cross-check against the frozen Qwen v1.1 copy.
"""

from __future__ import annotations

import pytest

from vlm_faithfulness_benchmark.generation import (
    deepseek_generator,
    glm_generator,
    kimi_generator,
    qwen_generator,
)
from vlm_faithfulness_benchmark.generation.mc_extraction import (
    extract_mc_outcome,
    forced_reply_span,
    strip_think_block,
)

OPTIONS = ("cigarette", "cigar", "pipe", "pen")

# Case battery shared with the frozen Qwen copy: (text, chosen, rationale).
SHARED_CASES = [
    ("A. cigarette\nRationale: he is smoking.", "cigarette", "he is smoking."),
    ("b)\nRationale: looks like a cigar.", "cigar", "looks like a cigar."),
    ("C\nRationale: a pipe shape.", "pipe", "a pipe shape."),
    ("cigarette.\nRationale: visible smoke.", "cigarette", "visible smoke."),
    ("Pen\nRationale: held like a pen.", "pen", "held like a pen."),
    ("A cigarette is visible.\nRationale: smoke.", None, "smoke."),  # article ≠ letter
    ("The answer is B.\nRationale: cigar.", None, "cigar."),  # unanchored letter
    ("E. something\nRationale: out of range.", None, "out of range."),  # letter > options
    ("A. cigarette\nNo marker here.", "cigarette", None),  # missing rationale
    ("", None, None),  # empty output
    # Panel F-10: edge shapes the battery previously left unpinned.
    ("B: cigar\nRationale: colon anchor.", "cigar", "colon anchor."),  # rule-1 ":"
    ("a.\nRationale: lowercase anchored.", "cigarette", "lowercase anchored."),
    ("b\nRationale: lowercase bare.", "cigar", "lowercase bare."),
    ("A. cigarette Rationale: same-line marker.", "cigarette", "same-line marker."),
    ("Ａ. fullwidth\nRationale: unicode letter.", None, "unicode letter."),
    ("AB. option\nRationale: two letters.", None, "two letters."),
    ("A. cigarette or B. cigar\nRationale: first anchor wins.", "cigarette",
     "first anchor wins."),
]


@pytest.mark.parametrize("text,chosen,rationale", SHARED_CASES)
def test_shared_core_rules(text: str, chosen: str | None, rationale: str | None) -> None:
    """The shared three-rule core maps each case shape correctly."""
    outcome = extract_mc_outcome(text, OPTIONS)
    assert outcome.chosen_answer == chosen
    assert outcome.rationale == rationale


@pytest.mark.parametrize("text,chosen,rationale", SHARED_CASES)
def test_no_drift_from_frozen_qwen_copy(
    text: str, chosen: str | None, rationale: str | None
) -> None:
    """The shared core and the frozen Qwen v1.1 copy agree on every case.

    The Qwen adapter keeps its own review-accepted copy of the rules; this
    cross-check makes silent divergence between the two impossible.
    """
    ours = extract_mc_outcome(text, OPTIONS)
    frozen = qwen_generator.extract_outcome(text, OPTIONS)
    assert (ours.chosen_answer, ours.rationale) == (
        frozen.chosen_answer,
        frozen.rationale,
    )


def test_contract_ids_are_distinct_pins() -> None:
    """Each generator pins its own contract id (N4.6 — per-generator pin)."""
    ids = {
        qwen_generator.EXTRACTION_CONTRACT_ID,
        glm_generator.EXTRACTION_CONTRACT_ID,
        deepseek_generator.EXTRACTION_CONTRACT_ID,
        kimi_generator.EXTRACTION_CONTRACT_ID,
    }
    assert ids == {
        "aokvqa-mc-v1.1",
        "aokvqa-mc-glm-v1",
        "aokvqa-mc-dsvl2-v1",
        "aokvqa-mc-kimi-v1",
    }


def test_prompts_are_generator_invariant() -> None:
    """All four adapters render the identical prompt for the same record.

    Cross-generator label differences must not be attributable to prompt
    drift; the wording is deliberately shared.
    """
    from vlm_faithfulness_benchmark.generation.identity import SourceRecordId
    from vlm_faithfulness_benchmark.ingestion.aokvqa import SourceRecord

    record = SourceRecord(
        identity=SourceRecordId("aokvqa", "q-1"),
        image_ref="coco/1",
        question="What is it?",
        options=OPTIONS,
        annotations={"gold_answer_idx": 0},
    )
    prompts = {
        qwen_generator.build_prompt(record),
        glm_generator.build_prompt(record),
        deepseek_generator.build_prompt(record),
        kimi_generator.build_prompt(record),
    }
    assert len(prompts) == 1


class TestGlmThinkContract:
    """Contract aokvqa-mc-glm-v1: think-block stripping before the rules."""

    def test_closed_think_block_is_stripped(self) -> None:
        """Text after </think> parses under the shared rules."""
        text = "<think>the object glows red at the tip</think>A. cigarette\nRationale: lit tip."
        outcome = glm_generator.extract_outcome(text, OPTIONS)
        assert outcome.chosen_answer == "cigarette"
        assert outcome.rationale == "lit tip."

    def test_unclosed_think_block_yields_empty_outcome(self) -> None:
        """Budget death mid-thought: no visible answer exists (CC4: no repair)."""
        text = "<think>it could be A because the tip glows, but then again"
        outcome = glm_generator.extract_outcome(text, OPTIONS)
        assert outcome.chosen_answer is None
        assert outcome.rationale is None

    def test_unclosed_think_never_leaks_letters(self) -> None:
        """Letters inside an unclosed think block must not be parsed as answers."""
        text = "<think>B. cigar\nRationale: fake.\n"
        outcome = glm_generator.extract_outcome(text, OPTIONS)
        assert outcome.chosen_answer is None

    def test_box_sentinels_are_removed(self) -> None:
        """GLM's answer/box sentinels are stripped before rule application."""
        text = "<think>hmm</think><|begin_of_box|>B.<|end_of_box|>\nRationale: cigar shape."
        outcome = glm_generator.extract_outcome(text, OPTIONS)
        assert outcome.chosen_answer == "cigar"

    def test_no_think_block_passes_through(self) -> None:
        """Non-thinking output parses exactly like the shared core."""
        text = "C\nRationale: pipe."
        assert glm_generator.extract_outcome(text, OPTIONS).chosen_answer == "pipe"

    def test_strip_think_block_plain_text_identity(self) -> None:
        """strip_think_block on sentinel-free text is (stripped) identity."""
        assert strip_think_block("  plain answer  ") == "plain answer"

    def test_rationale_quoting_a_sentinel_is_never_mutated(self) -> None:
        """Sentinel cleanup is confined to the answer region (panel F-04)."""
        text = '<think>x</think>B.\nRationale: the sign literally reads "<answer>".'
        outcome = glm_generator.extract_outcome(text, OPTIONS)
        assert outcome.chosen_answer == "cigar"
        assert outcome.rationale == 'the sign literally reads "<answer>".'


@pytest.mark.parametrize(
    "module", [deepseek_generator, kimi_generator], ids=["deepseek", "kimi"]
)
def test_passthrough_contracts_match_shared_core(module: object) -> None:
    """DeepSeek/Kimi contracts are the shared core with no pre-normalization."""
    for text, chosen, rationale in SHARED_CASES:
        outcome = module.extract_outcome(text, OPTIONS)  # type: ignore[attr-defined]
        assert (outcome.chosen_answer, outcome.rationale) == (chosen, rationale)


class TestForcedReplySpan:
    """The scorer-alignment primitive: diff the renders, never assume."""

    def test_strict_prefix_insertion(self) -> None:
        """Reply appended after the shared prefix (DeepSeek inference shape)."""
        assert forced_reply_span([1, 2, 3], [1, 2, 3, 7, 8]) == (3, 5)

    def test_insertion_with_shared_suffix(self) -> None:
        """Template end-of-turn scaffold after the reply is excluded."""
        assert forced_reply_span([1, 2, 9], [1, 2, 7, 8, 9]) == (2, 4)

    def test_leading_space_merge_is_captured(self) -> None:
        """A boundary token that changes with the reply joins the span.

        The F-03 failure shape: ``": "`` merging with the reply's first
        character produces a token absent from the empty render; the diff
        includes it, where a standalone-needle search would find nothing.
        """
        assert forced_reply_span([1, 2, 30], [1, 2, 31, 8, 30]) == (2, 4)

    def test_identical_renders_halt(self) -> None:
        """No inserted region ⇒ AssertionError (halt, never mis-score)."""
        with pytest.raises(AssertionError, match="empty"):
            forced_reply_span([1, 2, 3], [1, 2, 3])

    def test_span_at_sequence_start_halts(self) -> None:
        """A span with no predecessor position cannot be scored (F-07)."""
        with pytest.raises(AssertionError, match="predecessor|empty"):
            forced_reply_span([9, 1], [7, 9, 1])
