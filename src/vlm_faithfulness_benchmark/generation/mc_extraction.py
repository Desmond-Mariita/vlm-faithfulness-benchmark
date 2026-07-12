r"""Shared multiple-choice extraction core for the M9 generator lineup.

Matrix rows: N4.6 (pinned per-generator extraction contract), CC4 (no
substitution — absent fields stay absent).

The three answer rules here are exactly the ``aokvqa-mc-v1.1`` rules pinned
in :mod:`.qwen_generator` (which keeps its own frozen copy — that adapter is
review-accepted and is not re-routed through this module). New adapters
compose these rules with per-generator *pre-normalization* (e.g. GLM's
think-block stripping) under their own contract ids. A cross-check test
asserts this core and the Qwen copy agree on a shared case battery, so the
two implementations cannot drift silently.

Rules, applied to the first line of the (pre-normalized) text, first hit
wins:

1. **Anchored letter with punctuation** — ``^\s*([A-Ha-h])[.):]``.
2. **Bare letter line** — the line is exactly one letter.
3. **Exact option text** — the line, lowercased and stripped of a trailing
   period, equals exactly one option's text.

No rule firing ⇒ chosen answer is None. The rationale is everything after
the first rationale marker, stripped; absent/empty ⇒ None.
"""

from __future__ import annotations

import re

from vlm_faithfulness_benchmark.generation.harness import GenerationOutcome

__all__ = [
    "RATIONALE_MARKER",
    "extract_mc_outcome",
    "locate_unique_subsequence",
    "strip_think_block",
]

RATIONALE_MARKER = "Rationale:"

_THINK_OPEN = "<think>"
_THINK_CLOSE = "</think>"
# GLM-4.5V/4.6V wrap the final short answer in box sentinels; when the
# tokenizer does not treat them as special tokens they survive decoding.
_BOX_SENTINELS = ("<|begin_of_box|>", "<|end_of_box|>", "<answer>", "</answer>")


def strip_think_block(text: str) -> str | None:
    """Remove a leading reasoning block and answer sentinels from decoded text.

    Args:
        text: The generator's decoded output, verbatim.

    Returns:
        The visible post-reasoning text with box/answer sentinels removed,
        or None when the model opened a ``<think>`` block and never closed
        it (the token budget ran out mid-thought — there is no answer text
        to parse, and CC4 forbids inventing one).
    """
    stripped = text.lstrip()
    if stripped.startswith(_THINK_OPEN):
        _, closed, tail = stripped.partition(_THINK_CLOSE)
        if not closed:
            return None
        stripped = tail
    for sentinel in _BOX_SENTINELS:
        stripped = stripped.replace(sentinel, "")
    return stripped.strip()


def locate_unique_subsequence(haystack: list[int], needle: list[int], start: int) -> int:
    """Find the unique occurrence of a token subsequence at/after ``start``.

    Scorer-alignment primitive shared by the multi-generator adapters:
    chat templates may inject scaffold tokens around a forced assistant
    reply, so the reply span is *located*, never assumed — and ambiguity
    halts rather than mis-scores (the pilot-v1 defect class must halt).

    Args:
        haystack: Full input-id sequence.
        needle: Reply token ids to locate.
        start: First index eligible to begin a match (the prompt boundary).

    Returns:
        The start index of the single occurrence.

    Raises:
        AssertionError: If the subsequence occurs zero or multiple times.
    """
    assert needle, "empty reply token sequence"
    hits = [
        i
        for i in range(start, len(haystack) - len(needle) + 1)
        if haystack[i : i + len(needle)] == needle
    ]
    assert len(hits) == 1, (
        f"scorer alignment defect: reply subsequence found {len(hits)} times "
        "after the prompt boundary (expected exactly 1)"
    )
    return hits[0]


def extract_mc_outcome(text: str, options: tuple[str, ...]) -> GenerationOutcome:
    """Apply the three shared answer rules and the rationale-marker rule.

    Args:
        text: Pre-normalized generator text (adapters strip any model-family
            scaffolding *before* calling this).
        options: The instance's options (letter → option text mapping).

    Returns:
        GenerationOutcome; fields are None where extraction finds nothing —
        the tuple stays incomplete rather than repaired (ADR-003/CC4).
    """
    first_line, _, _ = text.strip().partition("\n")
    chosen: str | None = None
    letter_match = re.match(r"\s*([A-Ha-h])[.):]", first_line) or re.fullmatch(
        r"\s*([A-Ha-h])\s*", first_line
    )
    if letter_match is not None:
        idx = ord(letter_match.group(1).upper()) - ord("A")
        if 0 <= idx < len(options):
            chosen = options[idx]
    else:
        normalized = first_line.strip().rstrip(".").lower()
        exact = [o for o in options if o.strip().lower() == normalized]
        if len(exact) == 1:
            chosen = exact[0]
    _, marker, tail = text.partition(RATIONALE_MARKER)
    rationale = tail.strip() if marker and tail.strip() else None
    return GenerationOutcome(chosen_answer=chosen, rationale=rationale)
