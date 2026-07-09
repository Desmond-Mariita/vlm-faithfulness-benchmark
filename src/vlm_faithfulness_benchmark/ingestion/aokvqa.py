"""A-OKVQA source adapter — S01 normalization (`08` §3; matrix rows N3.1–N3.6, IN-8.1).

Normalizes raw A-OKVQA records into canonical Source Records, or explicit
ingestion exclusions (never a silent drop — N3.4). Normalization reshapes,
never rewrites (N3.2): question, options, and image reference are carried
verbatim; source-provided extras are carried as annotations.

Field policy (recorded per N3.2/N3.3):

- ``gold_answer_idx`` is carried as a **source annotation** — it is the
  dataset's own ground-truth key, not a generator's chosen answer, so N3.1's
  exclusion list does not cover it; downstream, recorded correctness is
  audit-only (ADR-004; `08` RI11) and the boundary suite forbids it in the
  predictor view.
- A-OKVQA's human-written ``rationales`` are **not** carried: they are
  neither the question, the options, the image, nor grounding annotations
  (N3.1's enumerated contents), and carrying free-text human rationales
  adjacent to generator rationales invites exactly the substitution/leak
  hazards CC4 and the information boundary exist to prevent.

Licensing posture (N3.6, recorded at ingestion, verified at corpus-release
gates): A-OKVQA annotations are distributed by AI2 under a permissive
license over COCO imagery (CC-BY-style photo terms); images are carried by
reference (`08` N3.1), never redistributed by this pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping

from vlm_faithfulness_benchmark.generation.identity import SourceRecordId

__all__ = ["SourceRecord", "IngestionExclusion", "SOURCE_LICENSING", "normalize_aokvqa"]

DATASET = "aokvqa"

#: N3.6 licensing posture, recorded per source for the Corpus Manifest
#: (`08` N10.4); release gates re-verify before any corpus publication.
SOURCE_LICENSING: Mapping[str, str] = MappingProxyType(
    {
        "dataset": DATASET,
        "annotations": "AI2 A-OKVQA release terms (permissive; verify at release gate)",
        "images": "COCO / Flickr photo terms; carried by reference only, never redistributed",
        "verified_at_release": "pending (corpus-release gate, plan §7 no-go rule applies)",
    }
)


@dataclass(frozen=True, slots=True)
class SourceRecord:
    """Canonical Source Record (`08` N3.1; `06a` §3.1).

    Attributes:
        identity: External-anchored source identity (R4).
        image_ref: Image reference (by identity, not pixels — N3.1).
        question: Question text, verbatim.
        options: Multiple-choice options, verbatim order.
        annotations: Source-provided structured annotations (N3.3),
            including ``gold_answer_idx`` (see module field policy).
    """

    identity: SourceRecordId
    image_ref: str
    question: str
    options: tuple[str, ...]
    annotations: Mapping[str, Any]

    def __post_init__(self) -> None:
        """Enforce the N3.1 content contract.

        Raises:
            AssertionError: If required content is missing or a forbidden
                field (generator, chosen answer, rationale, label — N3.1)
                appears among the annotations.
        """
        assert self.image_ref, "N3.1: Source Record carries an image reference"
        assert self.question, "N3.1: Source Record carries the question"
        assert len(self.options) >= 2, "N3.1: multiple-choice needs >=2 options"
        forbidden = {"generator", "generator_id", "chosen_answer", "rationale", "label"}
        leaked = forbidden & set(self.annotations)
        assert not leaked, f"N3.1: forbidden field(s) in Source Record: {sorted(leaked)}"
        object.__setattr__(self, "annotations", MappingProxyType(dict(self.annotations)))


@dataclass(frozen=True, slots=True)
class IngestionExclusion:
    """Explicit ingestion exclusion (`08` N3.4) — distinct from routed-aside.

    Attributes:
        dataset: Source dataset identifier.
        raw_record_id: Best-effort identity of the excluded raw record.
        reason: Human-readable exclusion reason (mandatory).
    """

    dataset: str
    raw_record_id: str
    reason: str

    def __post_init__(self) -> None:
        """Reject reason-less exclusions (N3.4 requires the reason)."""
        assert self.reason, "N3.4: an ingestion exclusion records its reason"


def normalize_aokvqa(raw: Mapping[str, Any]) -> SourceRecord | IngestionExclusion:
    """Normalize one raw A-OKVQA record (S01).

    Args:
        raw: The raw A-OKVQA JSON record (``question_id``, ``image_id``,
            ``question``, ``choices``, ``correct_choice_idx``, …).

    Returns:
        A SourceRecord on success, or an IngestionExclusion naming the
        defect — never a silent drop, pad, or truncation (N3.4).
    """
    record_id = str(raw.get("question_id") or "")
    if not record_id:
        return IngestionExclusion(DATASET, "<missing question_id>", "missing question_id")
    image_id = raw.get("image_id")
    if image_id is None or str(image_id) == "":
        return IngestionExclusion(DATASET, record_id, "missing image_id")
    question = str(raw.get("question") or "").strip()
    if not question:
        return IngestionExclusion(DATASET, record_id, "empty question")
    choices = raw.get("choices")
    if not isinstance(choices, (list, tuple)) or len(choices) < 2:
        return IngestionExclusion(DATASET, record_id, "malformed choices (need >=2 options)")
    if any(not str(c).strip() for c in choices):
        return IngestionExclusion(DATASET, record_id, "empty option text")
    gold_idx = raw.get("correct_choice_idx")
    if not isinstance(gold_idx, int) or not 0 <= gold_idx < len(choices):
        return IngestionExclusion(DATASET, record_id, "gold index missing or out of range")

    return SourceRecord(
        identity=SourceRecordId(dataset=DATASET, record_id=record_id),
        image_ref=f"coco/{image_id}",
        question=question,
        options=tuple(str(c) for c in choices),
        annotations={"gold_answer_idx": gold_idx},
    )
