"""Identity service — the sole mint for instance identities (`06a` §6 R1–R8).

Keys are canonical JSON (sorted, compact) — component values may contain any
character, so naive separator joins would be ambiguous (collision review
finding F-09); JSON escaping makes the key bijective with the identity.

Matrix rows: R1–R8, D-ID1, CC6. Components receive identities as opaque
values and MUST NOT construct them ad hoc (design §4); this module is the
only permitted constructor.

Identity semantics implemented here:

- **Instance identity** is the pair ``(composite generator identity,
  source record identity)`` (R1), carried unchanged across every artifact
  phase (R7).
- **Composite generator identity** identifies every component and
  configuration of the generating subject (R3; ADR-005).
- **Source record identity** is external-anchored: the originating dataset
  plus that dataset's own record identity (R4).
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["SourceRecordId", "GeneratorId", "InstanceId"]


@dataclass(frozen=True, slots=True)
class SourceRecordId:
    """External-anchored source record identity (`06a` R4; matrix row R4).

    Attributes:
        dataset: Originating dataset identifier (e.g. ``"aokvqa"``).
        record_id: The dataset's OWN record identity, verbatim.
    """

    dataset: str
    record_id: str

    def __post_init__(self) -> None:
        """Reject empty components — an anonymous identity is meaningless.

        Raises:
            AssertionError: If either component is empty (R4 requires a
                stable external anchor).
        """
        assert self.dataset, "R4: dataset identifier must be non-empty"
        assert self.record_id, "R4: source record identity must be non-empty"

    def key(self) -> str:
        """Return the canonical, collision-free JSON key for this identity."""
        import json

        return json.dumps({"dataset": self.dataset, "record_id": self.record_id},
                          sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class GeneratorId:
    """Composite generator subject identity (`06a` R3; ADR-005; matrix row R3).

    Every component and configuration that affects generation is part of the
    identity; two subjects differing in any component are different subjects
    and therefore yield different instances.

    Attributes:
        components: Sorted, immutable ``name=value`` pairs — model checkpoint
            id, weight revision hash, decoding config hash, extraction
            contract id, and any further configuration (RIP §4).
    """

    components: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        """Enforce R3 completeness and canonical ordering.

        Raises:
            AssertionError: If empty, unsorted, duplicated, or containing
                empty names/values.
        """
        assert self.components, "R3: a composite identity must name its components"
        names = [n for n, _ in self.components]
        assert names == sorted(names), "R3: components must be canonically sorted"
        assert len(names) == len(set(names)), "R3: duplicate component name"
        assert all(n and v for n, v in self.components), "R3: empty component name/value"

    @classmethod
    def from_mapping(cls, components: dict[str, str]) -> "GeneratorId":
        """Build a canonical identity from a component mapping.

        Args:
            components: Component name → value (checkpoint, revision, …).

        Returns:
            GeneratorId with canonically sorted components.
        """
        return cls(tuple(sorted(components.items())))

    def key(self) -> str:
        """Return the canonical, collision-free JSON key for this identity."""
        import json

        return json.dumps(dict(self.components), sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True, slots=True)
class InstanceId:
    """Instance identity: the R1 pair, minted once, never reassigned (R7).

    Attributes:
        generator: Composite generator identity (never in the Output Tuple —
            R6 is enforced at serialization, matrix row R6).
        source: External-anchored source record identity.
    """

    generator: GeneratorId
    source: SourceRecordId

    def key(self) -> str:
        """Return the canonical, collision-free JSON key for this instance."""
        import json

        return json.dumps({"generator": dict(self.generator.components),
                           "source": {"dataset": self.source.dataset,
                                      "record_id": self.source.record_id}},
                          sort_keys=True, separators=(",", ":"))
