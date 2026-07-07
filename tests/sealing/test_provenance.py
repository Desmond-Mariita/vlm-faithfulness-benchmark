"""Tests for the provenance artifact (matrix rows CC11, M1/M5, PL-1..4, S14/S15, ADR-003)."""

from __future__ import annotations

import pytest

from vlm_faithfulness_benchmark.generation.identity import (
    GeneratorId,
    InstanceId,
    SourceRecordId,
)
from vlm_faithfulness_benchmark.sealing.provenance import (
    InterventionalProvenance,
    ProvenanceEntry,
    SealedResolution,
)

IID = InstanceId(
    GeneratorId.from_mapping({"model": "qwen3-vl-8b-instruct", "revision": "abc"}),
    SourceRecordId("aokvqa", "r-1"),
)
VERSIONS = {"06": "v1.0", "07": "v1.0"}


def _obs(producer: str = "S06") -> ProvenanceEntry:
    return ProvenanceEntry(kind="observation", producer=producer, payload={"reading": 0.42})


class TestAccretion:
    """Observational-phase behavior (CC11, PL-1)."""

    def test_append_preserves_order(self) -> None:
        """Entries accrete append-only in order; order is never rewritten."""
        p = InterventionalProvenance(IID)
        first, second = _obs("S06"), _obs("S09")
        p.append(first)
        p.append(second)
        assert p.entries == (first, second)

    def test_entry_payload_is_read_only(self) -> None:
        """CC11: a recorded entry's payload cannot be edited in place."""
        entry = _obs()
        with pytest.raises(TypeError):
            entry.payload["reading"] = 0.99  # type: ignore[index]


class TestSealing:
    """Sealed-phase behavior (S14/S15, ADR-002 N1/N4, CC2, DM-T4)."""

    def test_seal_freezes_and_changes_no_value(self) -> None:
        """ADR-002 N4: sealing attaches back-references, values unchanged."""
        p = InterventionalProvenance(IID)
        entry = _obs()
        p.append(entry)
        p.seal(SealedResolution("S3", "faithful", None, None, VERSIONS))
        assert p.sealed and p.entries == (entry,)
        assert p.resolution.spec_versions["06"] == "v1.0"

    def test_post_seal_append_is_conformance_error(self) -> None:
        """CC11/M1: post-seal mutation halts loudly."""
        p = InterventionalProvenance(IID)
        p.seal(SealedResolution(None, None, None, "E2", VERSIONS))
        with pytest.raises(AssertionError, match="immutable"):
            p.append(_obs())

    def test_double_seal_is_conformance_error(self) -> None:
        """CC2: an artifact resolves exactly once."""
        p = InterventionalProvenance(IID)
        p.seal(SealedResolution("S1", "unfaithful", "D1", None, VERSIONS))
        with pytest.raises(AssertionError, match="exactly once"):
            p.seal(SealedResolution(None, None, None, "E2", VERSIONS))

    def test_e1_seal_rejects_intervention_observations(self) -> None:
        """ADR-003/S15-E1: an E1 record carries no Intervention Records."""
        p = InterventionalProvenance(IID)
        p.append(_obs())
        with pytest.raises(AssertionError, match="E1"):
            p.seal(SealedResolution(None, None, None, "E1", VERSIONS))

    def test_e1_seal_allows_determinations_only(self) -> None:
        """The E1 justifying evidence is the P1/generation outcome, not observations."""
        p = InterventionalProvenance(IID)
        p.append(ProvenanceEntry("determination", "S04", {"P1": "fail"}))
        p.seal(SealedResolution(None, None, None, "E1", VERSIONS))
        assert p.sealed


class TestResolutionShape:
    """The 06 §6 decision table and §9 route shape (I4/I5, LS-6a)."""

    @pytest.mark.parametrize(
        "state,label,reason",
        [("S1", "unfaithful", "D1"), ("S2", "unfaithful", "D2"), ("S3", "faithful", None)],
    )
    def test_valid_labelled_rows(self, state: str, label: str, reason: str | None) -> None:
        """Exactly the three decision-table rows are accepted."""
        SealedResolution(state, label, reason, None, VERSIONS)

    @pytest.mark.parametrize(
        "state,label,reason",
        [
            ("S3", "faithful", "D1"),  # faithful must carry no code (I5)
            ("S1", "unfaithful", "D2"),  # S1 couples to D1, not D2
            ("S2", "unfaithful", None),  # unfaithful carries exactly one code (I4/I5)
            ("S4", "faithful", None),  # no fourth state (LS-5a)
        ],
    )
    def test_invalid_labelled_rows_rejected(
        self, state: str, label: str, reason: str | None
    ) -> None:
        """Any off-table combination is a conformance error."""
        with pytest.raises(AssertionError):
            SealedResolution(state, label, reason, None, VERSIONS)

    def test_routed_carries_no_state_or_label(self) -> None:
        """06 §9: a routed record has an E-code and nothing else."""
        with pytest.raises(AssertionError):
            SealedResolution("S1", None, None, "E4", VERSIONS)
        with pytest.raises(AssertionError):
            SealedResolution(None, None, None, "E9", VERSIONS)

    def test_spec_versions_mandatory(self) -> None:
        """DM-T4/S14-vers: sealing without governing versions is rejected."""
        with pytest.raises(AssertionError):
            SealedResolution("S3", "faithful", None, None, {})
