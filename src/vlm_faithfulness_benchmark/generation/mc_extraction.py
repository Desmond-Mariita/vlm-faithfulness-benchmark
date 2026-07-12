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
from typing import Callable

from vlm_faithfulness_benchmark.generation.harness import GenerationOutcome

__all__ = [
    "RATIONALE_MARKER",
    "extract_mc_outcome",
    "forced_reply_span",
    "refine_reply_span",
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
    # Sentinel cleanup is confined to the answer region (everything before
    # the rationale marker): a rationale that legitimately QUOTES a sentinel
    # string must never be mutated (panel F-04, CC4-adjacent).
    head, marker, rationale_tail = stripped.partition(RATIONALE_MARKER)
    for sentinel in _BOX_SENTINELS:
        head = head.replace(sentinel, "")
    return (head + marker + rationale_tail).strip()


def forced_reply_span(ids_without: list[int], ids_with: list[int]) -> tuple[int, int]:
    r"""Locate a forced assistant reply by prefix/suffix diff of two renders.

    Scorer-alignment primitive shared by the multi-generator adapters
    (panel F-03 replaced the earlier standalone-needle search): the reply
    span is the region of the with-reply render not shared with the
    without-reply render. This makes NO assumption about how the tokenizer
    splits the reply in context (leading-space BPE merges, template
    scaffolds) — callers must still verify by decoding the span and halt
    on mismatch (the pilot-v1 defect class must halt, never mis-score).

    LaTeX: p = \\max\\{k : a_{<k} = b_{<k}\\},\\;
    s = \\max\\{k \\le \\min(|a|,|b|) - p : a_{>|a|-k} = b_{>|b|-k}\\};
    span = [p, |b| - s).

    Args:
        ids_without: Input-id sequence rendered WITHOUT the forced reply
            (e.g. generation prompt, or an empty assistant turn).
        ids_with: Input-id sequence rendered WITH the forced reply.

    Returns:
        ``(start, end)`` — the half-open inserted region in ``ids_with``.

    Raises:
        AssertionError: If the diff region is empty or starts at position 0
            (a predecessor position is required to read next-token
            log-probabilities).
    """
    limit = min(len(ids_without), len(ids_with))
    p = 0
    while p < limit and ids_without[p] == ids_with[p]:
        p += 1
    s = 0
    while (
        s < limit - p
        and ids_without[len(ids_without) - 1 - s] == ids_with[len(ids_with) - 1 - s]
    ):
        s += 1
    start, end = p, len(ids_with) - s
    assert 0 < start < end, (
        f"scorer alignment defect: forced-reply span [{start}, {end}) is empty "
        "or lacks a predecessor position"
    )
    return start, end


def refine_reply_span(
    ids: list[int],
    start: int,
    end: int,
    reply: str,
    decode: "Callable[[list[int]], str]",
) -> tuple[int, int]:
    r"""Shrink a diff span to the minimal token run decoding to the reply.

    Chat templates may inject scaffold INSIDE the forced-reply insertion
    (GLM rehearsal finding 2026-07-12: an empty ``<think></think>\\n`` is
    rendered before the reply, so the raw diff span decodes to
    ``"<think></think>\\nA."``). The scored span must be the reply itself:
    this scans the insertion for the unique shortest sub-span whose decoded,
    whitespace-stripped text equals the reply, and halts otherwise (the
    pilot-v1 defect class must halt, never mis-score). The scaffold tokens
    still condition the reply's probability (they precede its positions),
    identically across options.

    Args:
        ids: Full input-id sequence.
        start: Diff-span start (from :func:`forced_reply_span`).
        end: Diff-span end (exclusive).
        reply: The forced reply text.
        decode: Detokenizer for an id slice (special tokens skipped).

    Returns:
        ``(start, end)`` of the minimal matching sub-span.

    Raises:
        AssertionError: If no sub-span decodes to the reply, the shortest
            match is ambiguous, or the match starts at position 0.
    """
    matches: list[tuple[int, int]] = []
    for s in range(start, end):
        for e in range(s + 1, end + 1):
            if decode(ids[s:e]).strip() == reply:
                matches.append((s, e))
    assert matches, (
        f"scorer alignment defect: no sub-span of the insertion decodes to "
        f"{reply!r} (insertion decodes to {decode(ids[start:end])!r})"
    )
    shortest = min(e - s for s, e in matches)
    minimal = [(s, e) for s, e in matches if e - s == shortest]
    assert len(minimal) == 1, (
        f"scorer alignment defect: {len(minimal)} equally short sub-spans "
        f"decode to {reply!r} — ambiguous"
    )
    s, e = minimal[0]
    assert s > 0, "scorer alignment defect: reply span lacks a predecessor position"
    return s, e


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
