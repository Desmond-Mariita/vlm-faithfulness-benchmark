"""Tests for the identity service and baseline digest (matrix rows R1-R8, D-Q1, D-ATOM half).

Every invariant asserted in the modules gets a dedicated test here per the
repository code standard and matrix row D-ASSERT.
"""

from __future__ import annotations

import pytest

from vlm_faithfulness_benchmark.generation.digest import (
    baseline_digest,
    verify_baseline_digest,
)
from vlm_faithfulness_benchmark.generation.identity import (
    GeneratorId,
    InstanceId,
    SourceRecordId,
)

GEN = GeneratorId.from_mapping(
    {"model": "qwen3-vl-8b-instruct", "revision": "abc123", "decoding": "greedy-v1"}
)
SRC = SourceRecordId(dataset="aokvqa", record_id="r-0001")


class TestIdentity:
    """R1-R8 identity rules."""

    def test_r1_instance_identity_is_the_pair(self) -> None:
        """R1: instance identity is (generator, source), keyed collision-free."""
        import json

        iid = InstanceId(generator=GEN, source=SRC)
        parsed = json.loads(iid.key())
        assert parsed["source"] == {"dataset": "aokvqa", "record_id": "r-0001"}
        assert parsed["generator"]["model"] == "qwen3-vl-8b-instruct"

    def test_keys_are_collision_free_with_separator_chars(self) -> None:
        """F-09: separator characters inside component values cannot collide."""
        a = GeneratorId.from_mapping({"m": "x;n=y", "n": "z"})
        b = GeneratorId.from_mapping({"m": "x", "n": "y;n=z"})
        assert a.key() != b.key()

    def test_r2_same_pair_same_identity(self) -> None:
        """R2/R7: the same pair yields an equal, stable identity."""
        assert InstanceId(GEN, SRC) == InstanceId(GEN, SRC)

    def test_r3_component_change_changes_subject(self) -> None:
        """R3: any differing component is a different subject/instance."""
        other = GeneratorId.from_mapping(
            {"model": "qwen3-vl-8b-instruct", "revision": "def456", "decoding": "greedy-v1"}
        )
        assert InstanceId(GEN, SRC) != InstanceId(other, SRC)

    def test_r3_rejects_empty_and_duplicate_components(self) -> None:
        """R3: identity must name its components, canonically and completely."""
        with pytest.raises(AssertionError):
            GeneratorId(())
        with pytest.raises(AssertionError):
            GeneratorId((("model", ""),))
        with pytest.raises(AssertionError):
            GeneratorId((("b", "1"), ("a", "2")))  # unsorted

    def test_r4_source_identity_is_external_anchored(self) -> None:
        """R4: dataset + the dataset's own record id, both mandatory."""
        assert "aokvqa" in SRC.key() and "r-0001" in SRC.key()
        with pytest.raises(AssertionError):
            SourceRecordId(dataset="", record_id="x")
        with pytest.raises(AssertionError):
            SourceRecordId(dataset="aokvqa", record_id="")

    def test_identities_are_immutable(self) -> None:
        """M2/R7: identities are frozen values, never edited."""
        with pytest.raises(AttributeError):
            SRC.dataset = "other"  # type: ignore[misc]


class TestBaselineDigest:
    """DM Q1 digest designation."""

    TUPLE = {"chosen_answer": "B", "rationale": "the man is holding an umbrella"}

    def test_digest_is_deterministic_and_order_insensitive(self) -> None:
        """Canonicalization: field order in the mapping never matters."""
        reordered = {"rationale": self.TUPLE["rationale"], "chosen_answer": "B"}
        assert baseline_digest(self.TUPLE) == baseline_digest(reordered)

    def test_incomplete_tuple_digests_with_explicit_absence(self) -> None:
        """ADR-003: an absent rationale digests deterministically as null."""
        incomplete = {"chosen_answer": "B"}
        also_incomplete = {"chosen_answer": "B", "rationale": None}
        assert baseline_digest(incomplete) == baseline_digest(also_incomplete)
        assert baseline_digest(incomplete) != baseline_digest(self.TUPLE)

    def test_verification_passes_on_identical_content(self) -> None:
        """DM Q1 point 2: consumers verify against the recorded digest."""
        verify_baseline_digest(self.TUPLE, baseline_digest(self.TUPLE))

    def test_regenerated_rationale_trips_conformance_error(self) -> None:
        """CC4: a regenerated (different) rationale must halt, not route."""
        recorded = baseline_digest(self.TUPLE)
        regenerated = {"chosen_answer": "B", "rationale": "an umbrella is held by the man"}
        with pytest.raises(AssertionError, match="digest mismatch"):
            verify_baseline_digest(regenerated, recorded)

    def test_non_ascii_content_digests_deterministically(self) -> None:
        """Unicode rationale content round-trips stably (canonicalization pin)."""
        t1 = {"chosen_answer": "café", "rationale": "l'homme tient un parapluie ☂"}
        assert baseline_digest(t1) == baseline_digest(dict(reversed(list(t1.items()))))
        verify_baseline_digest(t1, baseline_digest(t1))

    def test_non_string_designated_field_rejected(self) -> None:
        """Designated surface is textual; anything else is a caller defect."""
        with pytest.raises(AssertionError):
            baseline_digest({"chosen_answer": 1, "rationale": "r"})
