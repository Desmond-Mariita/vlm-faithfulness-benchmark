"""Baseline-output-of-record designation digest (DM Q1 disposition; RIP §2.8).

Matrix rows: D-Q1, S02-post, CC4 (verification half). The Output Tuple
committed at S02 is the baseline-of-record; this module computes the content
digest that binds it, and verifies it at every downstream consumption point.
A mismatch is a **pipeline conformance error** (design §5.2), never a route.

Algorithm (RIP-1.0.0 §2.8): SHA-256 over the canonical JSON form of the
tuple's designated fields, with absent fields encoded as explicit ``null``
so an incomplete tuple (ADR-003) digests deterministically.

Canonicalization: JSON with sorted keys, no insignificant whitespace, UTF-8,
and lowest-escape encoding — the RFC 8785 (JCS) subset sufficient for the
designated field types (strings and null only; no floats, whose JCS number
form would otherwise need care).
"""

from __future__ import annotations

import hashlib
import json
from typing import Mapping

__all__ = ["DESIGNATED_FIELDS", "baseline_digest", "verify_baseline_digest"]

#: The designated Output Tuple fields bound by the digest (DM Q1 decision).
DESIGNATED_FIELDS: tuple[str, ...] = ("chosen_answer", "rationale")


def _canonical_form(output_tuple: Mapping[str, object]) -> bytes:
    """Serialize the designated fields to canonical JSON bytes.

    Args:
        output_tuple: The Output Tuple mapping; absent designated fields are
            encoded as ``null`` (ADR-003 explicit-absence rule).

    Returns:
        Canonical UTF-8 JSON bytes over exactly the designated fields.

    Raises:
        AssertionError: If a designated field holds a non-string, non-null
            value — the designated surface is textual by construction
            (`08` N4.6 fixes the rationale object; the chosen answer is the
            emitted option text/index as a string).
    """
    designated: dict[str, object] = {}
    for field_name in DESIGNATED_FIELDS:
        value = output_tuple.get(field_name)
        assert value is None or isinstance(value, str), (
            f"designated field '{field_name}' must be str or absent, got {type(value).__name__}"
        )
        designated[field_name] = value
    # sort_keys + separators yields the JCS form for this value domain.
    canonical = json.dumps(designated, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return canonical.encode("utf-8")


# LaTeX: d(t) = \mathrm{SHA256}(\mathrm{JCS}(\{f \mapsto t[f] \lor \varnothing : f \in F\}))
# where F = DESIGNATED_FIELDS and \varnothing is the explicit null absence marker.
def baseline_digest(output_tuple: Mapping[str, object]) -> str:
    """Compute the baseline-of-record digest at the S02 atomic commit.

    Args:
        output_tuple: The Output Tuple exactly as emitted (CC4 — no
            substitution, no repair).

    Returns:
        Lowercase hex SHA-256 digest string.
    """
    return hashlib.sha256(_canonical_form(output_tuple)).hexdigest()


def verify_baseline_digest(output_tuple: Mapping[str, object], recorded_digest: str) -> None:
    """Verify a consumed tuple against the recorded baseline digest.

    Every downstream consumer (S04–S11 gates, S09 edit targeting) calls this
    before use and records the verified digest in its own provenance entry
    (DM Q1 decision, point 2).

    Args:
        output_tuple: The tuple content the consumer is about to use.
        recorded_digest: The digest recorded at the S02 commit.

    Raises:
        AssertionError: On mismatch — a regenerated or substituted baseline
            is a pipeline conformance error (halt loudly; never a route,
            never silently repaired).
    """
    actual = baseline_digest(output_tuple)
    assert actual == recorded_digest, (
        "baseline-of-record digest mismatch (CC4/DM-Q1 conformance error): "
        f"recorded {recorded_digest}, computed {actual}"
    )
