"""Interventional Provenance store — append-only accretion, then sealed (ADR-002).

Matrix rows: CC11, M1/M5, PL-1..PL-4, S14-post, S14-vers, S15-post, T1, DM-3.7.

One provenance artifact exists per candidate (`06a` §3.7); it accretes
observations and determinations **append-only** during construction
(`07` §7, CC11) and transitions — the *same artifact*, not a copy — into a
**sealed** phase when the candidate resolves (S14 labelled / S15 routed).
Sealing folds the resolution in as **traceability back-references only**
(ADR-002 N1), adds no production edge, and changes no value (N4). After
sealing, any mutation attempt is a pipeline conformance error (design §5.2).

Exactly-once resolution (CC2) is enforced locally: an artifact seals once,
as labelled XOR routed, never both, never twice.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from vlm_faithfulness_benchmark.generation.identity import InstanceId

__all__ = ["ProvenanceEntry", "SealedResolution", "InterventionalProvenance"]

#: E-codes a routed resolution may carry (`06` §9).
_E_CODES: frozenset[str] = frozenset({"E1", "E2", "E3", "E4", "E5", "E6"})
#: Labelled resolutions: (state, label, reason_code) per the `06` §6 table.
_LABELLED_ROWS: frozenset[tuple[str, str, str | None]] = frozenset(
    {("S1", "unfaithful", "D1"), ("S2", "unfaithful", "D2"), ("S3", "faithful", None)}
)


@dataclass(frozen=True, slots=True)
class ProvenanceEntry:
    """One append-only accretion: an observation or a gate determination.

    Attributes:
        kind: Entry kind (e.g. ``"observation"``, ``"determination"``).
        producer: The producing stage (``"S04"`` … ``"S11"``; CC3 single
            producer is auditable from this field).
        payload: Read-only entry content (graded readings, gate results —
            CC5 requires the raw readings, not only hard choices).
    """

    kind: str
    producer: str
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        """Freeze the payload view and reject anonymous entries.

        Raises:
            AssertionError: If kind or producer is empty.
        """
        assert self.kind, "provenance entry needs a kind"
        assert self.producer, "provenance entry needs a producing stage (CC3)"
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))


@dataclass(frozen=True, slots=True)
class SealedResolution:
    """The back-reference block folded in at sealing (ADR-002 N1).

    Exactly one of the two shapes (CC2):

    - labelled: ``state``/``label`` set (reason per the `06` §6 coupling),
      ``e_code`` None;
    - routed: ``e_code`` set, ``state``/``label``/``reason_code`` None.

    Attributes:
        state: Behavioural state for labelled resolutions.
        label: Primary label value for labelled resolutions.
        reason_code: Reason code per the coupling rules (`06` I4/I5).
        e_code: E-route for routed resolutions.
        spec_versions: Governing specification versions (DM-T4; S14-vers).
    """

    state: str | None
    label: str | None
    reason_code: str | None
    e_code: str | None
    spec_versions: Mapping[str, str]

    def __post_init__(self) -> None:
        """Enforce the labelled-XOR-routed shape and the `06` §6 table.

        Raises:
            AssertionError: On any shape violating CC2, the decision table,
                or the reason-code coupling (I4/I5).
        """
        if self.e_code is not None:
            assert self.e_code in _E_CODES, f"unknown E-code {self.e_code!r}"
            assert self.state is None and self.label is None and self.reason_code is None, (
                "routed resolution carries no state/label/reason (06 §9)"
            )
        else:
            assert (self.state, self.label, self.reason_code) in _LABELLED_ROWS, (
                f"labelled resolution {(self.state, self.label, self.reason_code)!r} "
                "is not a row of the 06 §6 decision table"
            )
        assert self.spec_versions, "sealing MUST record governing spec versions (DM-T4)"
        object.__setattr__(self, "spec_versions", MappingProxyType(dict(self.spec_versions)))


class InterventionalProvenance:
    """The per-candidate provenance artifact across both ADR-002 phases.

    Engineering note: a single stateful object (not two classes) because the
    spec is explicit that sealing is a phase of the *same* artifact
    (`07` §5 S14); the phase flag plus asserts give the two-regime
    immutability (`06a` M1) without copying.
    """

    def __init__(self, instance: InstanceId) -> None:
        """Open the artifact in its observational (append-only) phase.

        Args:
            instance: The owning instance identity (R1; carried unchanged).
        """
        self._instance = instance
        self._entries: list[ProvenanceEntry] = []
        self._resolution: SealedResolution | None = None

    @property
    def instance(self) -> InstanceId:
        """The owning instance identity."""
        return self._instance

    @property
    def sealed(self) -> bool:
        """True iff the artifact is in its sealed phase."""
        return self._resolution is not None

    @property
    def entries(self) -> tuple[ProvenanceEntry, ...]:
        """All accreted entries, in append order (order is never rewritten)."""
        return tuple(self._entries)

    @property
    def resolution(self) -> SealedResolution:
        """The sealed back-reference block.

        Raises:
            AssertionError: If the artifact is not sealed yet.
        """
        assert self._resolution is not None, "artifact is not sealed"
        return self._resolution

    def append(self, entry: ProvenanceEntry) -> None:
        """Accrete one entry (observational phase only; CC11).

        Args:
            entry: The observation/determination to append.

        Raises:
            AssertionError: If the artifact is already sealed — post-seal
                mutation is a pipeline conformance error (design §5.2).
        """
        assert not self.sealed, "CC11/M1: sealed provenance is immutable"
        self._entries.append(entry)

    def seal(self, resolution: SealedResolution) -> None:
        """Transition to the sealed phase, folding in the resolution.

        Sealing changes no accreted value (ADR-002 N4) — it only freezes the
        artifact and attaches back-references (N1). E1 resolutions must have
        no intervention-observation entries (ADR-003; S15-E1).

        Args:
            resolution: The labelled-XOR-routed back-reference block.

        Raises:
            AssertionError: On double-seal (CC2 exactly-once) or an E1 seal
                over intervention observations.
        """
        assert not self.sealed, "CC2: an artifact resolves exactly once"
        if resolution.e_code == "E1":
            assert not any(e.kind == "observation" for e in self._entries), (
                "ADR-003: an E1 record carries no Intervention Records"
            )
        self._resolution = resolution
