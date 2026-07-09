"""Tests for extraction contract aokvqa-mc-v1.1 (review F-01/F-05; N4.6)."""

from __future__ import annotations

import pytest

from vlm_faithfulness_benchmark.generation.identity import SourceRecordId
from vlm_faithfulness_benchmark.generation.qwen_generator import (
    EXTRACTION_CONTRACT_ID,
    build_prompt,
    extract_outcome,
)
from vlm_faithfulness_benchmark.ingestion.aokvqa import SourceRecord

OPTIONS = ("cigarette", "cigar", "pipe", "pen")


def test_contract_version_is_v11() -> None:
    """The recorded contract id matches the implemented rules."""
    assert EXTRACTION_CONTRACT_ID == "aokvqa-mc-v1.1"


@pytest.mark.parametrize(
    "text,expected",
    [
        ("A. cigarette\nRationale: he is smoking.", "cigarette"),  # rule 1
        ("b)\nRationale: looks like a cigar.", "cigar"),  # rule 1, lowercase
        ("C\nRationale: a pipe shape.", "pipe"),  # rule 2 bare letter
        ("cigarette.\nRationale: visible smoke.", "cigarette"),  # rule 3 exact text
        ("Pen\nRationale: held like a pen.", "pen"),  # rule 3 case-insensitive
    ],
)
def test_correct_extractions(text: str, expected: str) -> None:
    """Each contract rule maps its shape to the right option."""
    assert extract_outcome(text, OPTIONS).chosen_answer == expected


@pytest.mark.parametrize(
    "text",
    [
        "A cigarette is being smoked.\nRationale: smoke.",  # article, not a choice (F-01)
        "The answer is B.\nRationale: cigar.",  # letter not anchored
        "Definitely one of A or B.\nRationale: unsure.",  # multi-letter prose
        "banana\nRationale: nonsense.",  # matches no option
    ],
)
def test_ambiguous_first_lines_yield_incomplete_not_wrong(text: str) -> None:
    """F-01: prose first lines must yield None, never a silent wrong capture."""
    assert extract_outcome(text, OPTIONS).chosen_answer is None


def test_rationale_extraction_and_absence() -> None:
    """Rationale is everything after the marker; absent marker => None."""
    assert extract_outcome("A.\nRationale:  smoke rises.  ", OPTIONS).rationale == "smoke rises."
    assert extract_outcome("A. cigarette, clearly.", OPTIONS).rationale is None


def test_prompt_contains_options_and_marker() -> None:
    """The pinned prompt lists every option letter and the marker."""
    rec = SourceRecord(
        identity=SourceRecordId("aokvqa", "q-1"),
        image_ref="coco/1",
        question="What is it?",
        options=OPTIONS,
        annotations={"gold_answer_idx": 0},
    )
    prompt = build_prompt(rec)
    assert "A. cigarette" in prompt and "D. pen" in prompt and "Rationale:" in prompt
