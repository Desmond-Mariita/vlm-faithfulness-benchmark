"""Tests for the A-OKVQA S01 adapter (matrix rows N3.1-N3.5, IN-8.1, DM-3.1)."""

from __future__ import annotations

from typing import Any

import pytest

from vlm_faithfulness_benchmark.ingestion.aokvqa import (
    SOURCE_LICENSING,
    IngestionExclusion,
    SourceRecord,
    normalize_aokvqa,
)

RAW: dict[str, Any] = {
    "question_id": "q-123",
    "image_id": 51234,
    "question": "What is the man holding?",
    "choices": ["umbrella", "bat", "phone", "cup"],
    "correct_choice_idx": 0,
    "rationales": ["He is shielding himself from rain."],
}


class TestNormalization:
    """Reshape-not-rewrite (N3.2) and content contract (N3.1)."""

    def test_valid_record_normalizes_verbatim(self) -> None:
        """Question, options, and identity are carried unchanged."""
        rec = normalize_aokvqa(RAW)
        assert isinstance(rec, SourceRecord)
        assert rec.identity.key() == "aokvqa/q-123"
        assert rec.question == RAW["question"]
        assert rec.options == tuple(RAW["choices"])
        assert rec.image_ref == "coco/51234"

    def test_gold_index_is_annotation_human_rationales_dropped(self) -> None:
        """Field policy: gold idx carried as annotation; human rationales not carried."""
        rec = normalize_aokvqa(RAW)
        assert isinstance(rec, SourceRecord)
        assert rec.annotations["gold_answer_idx"] == 0
        assert "rationales" not in rec.annotations

    def test_forbidden_fields_unconstructible(self) -> None:
        """N3.1/DM-3.1: a Source Record carrying a label or rationale is rejected."""
        rec = normalize_aokvqa(RAW)
        assert isinstance(rec, SourceRecord)
        with pytest.raises(AssertionError, match="forbidden"):
            SourceRecord(
                identity=rec.identity,
                image_ref=rec.image_ref,
                question=rec.question,
                options=rec.options,
                annotations={"label": "faithful"},
            )

    def test_annotations_read_only(self) -> None:
        """M2: source content is immutable from creation."""
        rec = normalize_aokvqa(RAW)
        assert isinstance(rec, SourceRecord)
        with pytest.raises(TypeError):
            rec.annotations["gold_answer_idx"] = 1  # type: ignore[index]


class TestExclusions:
    """Explicit exclusions with reasons (N3.4) — never silent drops."""

    @pytest.mark.parametrize(
        "mutation,reason_fragment",
        [
            ({"question_id": ""}, "question_id"),
            ({"image_id": None}, "image_id"),
            ({"question": "  "}, "empty question"),
            ({"choices": ["only-one"]}, "choices"),
            ({"choices": ["a", " "]}, "empty option"),
            ({"correct_choice_idx": 9}, "gold index"),
            ({"correct_choice_idx": None}, "gold index"),
        ],
    )
    def test_malformed_records_excluded_with_reason(
        self, mutation: dict[str, Any], reason_fragment: str
    ) -> None:
        """Each defect class yields an exclusion naming its reason."""
        raw = {**RAW, **mutation}
        result = normalize_aokvqa(raw)
        assert isinstance(result, IngestionExclusion)
        assert reason_fragment in result.reason
        assert result.dataset == "aokvqa"

    def test_exclusion_requires_reason(self) -> None:
        """N3.4: a reason-less exclusion is unconstructible."""
        with pytest.raises(AssertionError):
            IngestionExclusion("aokvqa", "q-1", "")


def test_licensing_posture_recorded() -> None:
    """N3.6: per-source licensing posture exists and flags release verification."""
    assert SOURCE_LICENSING["dataset"] == "aokvqa"
    assert "pending" in SOURCE_LICENSING["verified_at_release"]
