"""Mechanical check: the pinned P2 pattern registry ships and is non-empty.

Traces to RIP v1 Appendix A and acceptance-matrix rows P2 / §2.6(c): the
registry is a versioned config artifact whose hash enters the manifest
integrity block.
"""

from pathlib import Path

REGISTRY = Path(__file__).resolve().parents[1] / "config" / "p2_patterns_v1.txt"


def test_registry_exists_and_has_patterns() -> None:
    """Registry file exists with at least one non-comment pattern line."""
    assert REGISTRY.is_file()
    patterns = [
        line
        for line in REGISTRY.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]
    assert len(patterns) >= 5
