"""Registered content-word Jaccard drift and Condition B (S11).

The final preregistration selects ``jaccard-content-v1``. Content words are
the unique lowercased ``[a-z']+`` tokens after removal of the pinned stopword
set. Drift is one minus set Jaccard similarity. Condition B is one-sided:
the rationale tracks iff targeted drift is at least the frozen threshold.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

__all__ = [
    "CONTENT_TOKEN_PATTERN",
    "DRIFT_INSTRUMENT_ID",
    "ConditionBDetermination",
    "compute_drift",
    "content_words",
    "determine_condition_b",
    "instrument_provenance",
    "load_stopwords",
]

DRIFT_INSTRUMENT_ID = "jaccard-content-v1"
CONTENT_TOKEN_PATTERN = r"[a-z']+"
_CONTENT_TOKEN_RE = re.compile(CONTENT_TOKEN_PATTERN)


def load_stopwords(path: Path) -> frozenset[str]:
    """Load and validate the pinned whitespace-delimited stopword set.

    Args:
        path: Path to ``config/stopwords_v1.txt``.

    Returns:
        The immutable stopword set.

    Raises:
        RuntimeError: If the file is missing, empty, duplicated, or contains
            a token outside the registered lowercase token language.
    """
    if not path.is_file():
        raise RuntimeError(f"pinned stopword file missing: {path}")
    words = path.read_text(encoding="utf-8").split()
    if not words:
        raise RuntimeError("pinned stopword set is empty")
    if len(words) != len(set(words)):
        raise RuntimeError("pinned stopword set contains duplicates")
    if any(re.fullmatch(CONTENT_TOKEN_PATTERN, word) is None for word in words):
        raise RuntimeError("stopword outside the registered lowercase token language")
    return frozenset(words)


def content_words(text: str, stopwords: frozenset[str]) -> frozenset[str]:
    """Return the registered unique content-word set for one rationale."""
    return frozenset(_CONTENT_TOKEN_RE.findall(text.lower())).difference(stopwords)


def instrument_provenance(stopwords_sha256: str) -> dict[str, str]:
    """Return the complete machine-readable instrument identity."""
    return {
        "instrument": DRIFT_INSTRUMENT_ID,
        "tokenizer_regex": CONTENT_TOKEN_PATTERN,
        "normalization": "lowercase",
        "collection": "set",
        "stopwords_sha256": stopwords_sha256,
        "drift": "1-|A_intersect_B|/|A_union_B|",
    }


@dataclass(frozen=True, slots=True)
class ConditionBDetermination:
    """The S11 binary verdict and its reconstructable graded reading."""

    tracks: bool
    targeted_drift: float
    theta_b: float


def compute_drift(
    baseline_rationale: str,
    counterfactual_rationale: str,
    stopwords: frozenset[str],
) -> float:
    """Compute registered content-word Jaccard drift.

    Empty raw rationales are P6 integrity failures and never reach this
    function. An empty content-word union has no registered numerical value,
    so it is a fail-closed conformance error rather than an invented score.
    The accepted calibration and M9 GLM ledgers contain no such pair.

    Raises:
        RuntimeError: On empty raw text or an empty content-word union.
    """
    if not baseline_rationale.strip():
        raise RuntimeError("empty baseline rationale reaches drift only by defect")
    if not counterfactual_rationale.strip():
        raise RuntimeError("empty counterfactual rationale is a P6 integrity failure")
    baseline = content_words(baseline_rationale, stopwords)
    counterfactual = content_words(counterfactual_rationale, stopwords)
    union = baseline | counterfactual
    if not union:
        raise RuntimeError("jaccard-content-v1 has an empty content-word union")
    return 1.0 - (len(baseline & counterfactual) / len(union))


def determine_condition_b(targeted_drift: float, theta_b: float) -> ConditionBDetermination:
    """Determine Condition B using the registered inclusive threshold."""
    if not (0.0 <= targeted_drift <= 1.0):
        raise RuntimeError("jaccard-content-v1 drift must be finite and in [0, 1]")
    if not (0.0 < theta_b <= 1.0):
        raise RuntimeError("theta_b must be a calibrated value in (0, 1]")
    return ConditionBDetermination(
        tracks=targeted_drift >= theta_b,
        targeted_drift=targeted_drift,
        theta_b=theta_b,
    )
