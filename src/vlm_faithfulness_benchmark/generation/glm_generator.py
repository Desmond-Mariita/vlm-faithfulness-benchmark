r"""GLM-4.6V-Flash generator adapter — second composite generator subject.

Matrix rows: S02-post, CC7 (same subject per call), R3 (identity names every
component), N4.6 (pinned per-generator extraction contract).

**Extraction contract ``aokvqa-mc-glm-v1`` (pinned):** GLM-4.6V is a
*thinking* model — it emits a ``<think>…</think>`` reasoning block before
its visible answer, and may wrap the short answer in box/answer sentinels.
The contract is: (a) strip the think block and sentinels via
:func:`..mc_extraction.strip_think_block` — an *unclosed* think block means
the token budget died mid-thought and the outcome is empty (CC4: never
repaired); (b) apply the shared three answer rules + ``Rationale:`` marker
rule (:func:`..mc_extraction.extract_mc_outcome`) to the visible text.

Decoding: greedy, ``do_sample=False``, ``num_beams=1``,
``max_new_tokens=768`` — larger than Qwen's 160 because the thinking block
consumes budget before the visible answer appears; the value is pinned in
the composite identity.

**Option scorer (contract ``option-letter-logprob-glm-v1``):** same reading
as Qwen's v1.1 — per option, the total log-probability of the forced
assistant reply ``"<LETTER>."`` — but the reply span is *located*, not
assumed: the span is the prefix/suffix diff between the with-reply render
and the generation-prompt render (:func:`..mc_extraction.forced_reply_span`
— no assumption about in-context tokenization, panel F-03), verified by
decoding the span back to the reply text. Any mismatch halts the run
rather than mis-scoring (the pilot-v1 defect class must halt, never
silently misread). The span may include turn-final scaffold the template
appends after the reply; it is identical across options and is part of the
pinned reading.

**Construct note (pinned decision, panel F-05/C3c):** the benchmark's
object of study is the model's *stated* rationale — the visible
explanation presented alongside the answer, the same construct read from
every non-thinking generator. The ``<think>`` block is upstream scratchpad,
not the stated rationale, and using it would break cross-generator
comparability. Consequence: GLM instances whose visible text carries no
``Rationale:`` marker yield ``rationale=None`` (retained incomplete, CC4).
The marker-compliance and unclosed-think rates are measured in the local
rehearsal smoke; a material attrition rate escalates to the maintainer
BEFORE the mass run (it is a selection effect on the retained sample).
"""

from __future__ import annotations

import string
from pathlib import Path
from typing import Any

from vlm_faithfulness_benchmark.generation.harness import GenerationOutcome
from vlm_faithfulness_benchmark.generation.identity import GeneratorId
from vlm_faithfulness_benchmark.generation.mc_extraction import (
    RATIONALE_MARKER,
    extract_mc_outcome,
    forced_reply_span,
    strip_think_block,
)
from vlm_faithfulness_benchmark.ingestion.aokvqa import SourceRecord

__all__ = [
    "EXTRACTION_CONTRACT_ID",
    "OPTION_SCORER_ID",
    "build_prompt",
    "extract_outcome",
    "GlmGenerator",
]

EXTRACTION_CONTRACT_ID = "aokvqa-mc-glm-v1"
OPTION_SCORER_ID = "option-letter-logprob-glm-v1"
_MODEL_ID = "zai-org/GLM-4.6V-Flash"
_MAX_NEW_TOKENS = 768


def build_prompt(record: SourceRecord) -> str:
    """Render the pinned prompt for a Source Record (contract aokvqa-mc-glm-v1).

    Identical wording to the Qwen contract — the prompt is deliberately
    generator-invariant so cross-generator label differences cannot be
    attributed to prompt drift.

    Args:
        record: The normalized Source Record.

    Returns:
        The user-turn text presented alongside the image.
    """
    letters = string.ascii_uppercase
    options = "\n".join(f"{letters[i]}. {opt}" for i, opt in enumerate(record.options))
    return (
        f"Question: {record.question}\n{options}\n\n"
        "Answer with the letter of the correct option on the first line, "
        f'then explain your reasoning after "{RATIONALE_MARKER}".'
    )


def extract_outcome(generated_text: str, options: tuple[str, ...]) -> GenerationOutcome:
    """Apply contract aokvqa-mc-glm-v1 to raw decoded text.

    Args:
        generated_text: The generator's decoded output, verbatim (may open
            with a ``<think>`` block).
        options: The instance's options.

    Returns:
        GenerationOutcome; both fields None when the think block never
        closed (no visible answer text exists — ADR-003 retains the
        incomplete tuple).
    """
    visible = strip_think_block(generated_text)
    if visible is None:
        return GenerationOutcome(chosen_answer=None, rationale=None)
    return extract_mc_outcome(visible, options)


class GlmGenerator:
    """The GLM-4.6V-Flash composite subject (CC7: one subject for every call)."""

    def __init__(self, image_root: Path) -> None:
        """Load the model, processor, and pinned decoding configuration.

        Args:
            image_root: Directory containing the COCO pool images
                (``<12-digit-id>.jpg``; Source Records reference
                ``coco/<id>``).
        """
        import torch
        from transformers import AutoModelForImageTextToText, AutoProcessor

        self._torch = torch
        self._image_root = image_root
        # transformers' factories are untyped upstream; the boundary is
        # confined to these calls (mypy: no-untyped-call/misc).
        self._processor = AutoProcessor.from_pretrained(_MODEL_ID)  # type: ignore[no-untyped-call]
        # Auto class resolves the checkpoint's DECLARED architecture
        # (Glm4vForConditionalGeneration — Flash is DENSE 9B; the MoE class
        # silently fabricated newly-initialized expert weights and OOMed:
        # rehearsal finding 2026-07-12).
        # With output_loading_info=True from_pretrained returns a 2-tuple;
        # upstream stubs don't model that — Any confines the boundary.
        loaded: Any = AutoModelForImageTextToText.from_pretrained(
            _MODEL_ID, dtype=torch.bfloat16, device_map="cuda:0",
            output_loading_info=True,
        )
        self._model, loading_info = loaded
        # A checkpoint/architecture mismatch surfaces as "missing keys"
        # that transformers silently NEWLY INITIALIZES — garbage weights
        # masquerading as a loaded subject. Halt, never degrade.
        missing = loading_info.get("missing_keys", [])
        assert not missing, (
            f"checkpoint/architecture mismatch: {len(missing)} keys missing "
            f"from the checkpoint would be newly initialized (e.g. {missing[:3]})"
        )
        self._model.eval()
        revision = getattr(self._model.config, "_commit_hash", None)
        # R3: a subject without a pinned weight revision is not a complete
        # composite identity — halt rather than record "unpinned".
        assert revision, "R3: weight revision hash unavailable; refusing unpinned identity"
        self._revision = str(revision)

    def identity(self) -> GeneratorId:
        """The composite identity naming every component (R3, ADR-005)."""
        return GeneratorId.from_mapping(
            {
                "model": _MODEL_ID,
                "revision": self._revision,
                "decoding": f"greedy;beams=1;max_new_tokens={_MAX_NEW_TOKENS}",
                "extraction_contract": EXTRACTION_CONTRACT_ID,
                "option_scorer": OPTION_SCORER_ID,
                "prompt_template": EXTRACTION_CONTRACT_ID,  # prompt is part of the contract
                "image_preprocessing": "pil-rgb-native",
                "dtype": "bfloat16",
            }
        )

    def scorer_generation_agreement(self, records: "list[SourceRecord]") -> float:
        """Measure scorer-vs-generation agreement on unperturbed images.

        The instrument sanity gate (added after the pilot-v1 defect): run
        on a small batch before any readings-dependent GPU run; the mass
        run is authorized only if this clears the registered 0.90 floor.

        Args:
            records: A small validation batch.

        Returns:
            Agreement fraction in [0, 1] over records whose generation
            parsed to an option.
        """
        agree = total = 0
        for record in records:
            outcome = self(record)
            if outcome.chosen_answer is None:
                continue
            chosen_index = next(
                i
                for i, o in enumerate(record.options)
                if o.strip().lower() == outcome.chosen_answer.strip().lower()
            )
            scores = self.score_options(record)
            total += 1
            if scores[chosen_index] >= max(scores):
                agree += 1
        assert total > 0, "no parseable generations in the validation batch"
        return agree / total

    def __call__(self, record: SourceRecord) -> GenerationOutcome:
        """Run the generator once over a Source Record (S02).

        Args:
            record: The normalized Source Record.

        Returns:
            The emitted outcome under the pinned extraction contract.
        """
        from PIL import Image

        image_id = record.image_ref.removeprefix("coco/")
        image = Image.open(self._image_root / f"{int(image_id):012d}.jpg").convert("RGB")
        return self.generate_on(record, image)

    def generate_on(self, record: SourceRecord, image: "object") -> GenerationOutcome:
        """Run the generator on an explicit image (regime/edited inputs, S06/S09).

        Args:
            record: The normalized Source Record (prompt source).
            image: A PIL image or HxWx3 uint8 array.

        Returns:
            The emitted outcome under the pinned extraction contract.
        """
        import numpy as np
        from PIL import Image

        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": build_prompt(record)},
                ],
            }
        ]
        inputs = self._processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self._model.device)
        with self._torch.inference_mode():
            generated = self._model.generate(
                **inputs,
                do_sample=False,
                num_beams=1,
                max_new_tokens=_MAX_NEW_TOKENS,
            )
        new_tokens = generated[0, inputs["input_ids"].shape[1] :]
        text = self._processor.decode(new_tokens, skip_special_tokens=True)
        # Diagnostics hook (rehearsal): the raw decoded text BEFORE the
        # extraction contract, for think-block/marker-compliance audits.
        # Never consumed by the pipeline (the contract output is the record).
        self.last_raw_text: str = text
        return extract_outcome(text, record.options)

    def score_options(
        self, record: SourceRecord, image_override: "object | None" = None
    ) -> tuple[float, ...]:
        """Score each option's forced-reply log-probability.

        Contract ``option-letter-logprob-glm-v1``: same graded CC5 reading
        as Qwen's v1.1, with the reply span *located* (unique-subsequence
        search after the prompt boundary) instead of assumed, because the
        GLM chat template may inject thinking-scaffold tokens into the
        assistant turn.

        Args:
            record: The Source Record (prompt source).
            image_override: A PIL image or HxWx3 uint8 array to score
                against instead of the record's own image; None uses the
                record's image.

        Returns:
            Per-option total log-probabilities of the reply ``"<LETTER>."``.
        """
        import numpy as np
        from PIL import Image

        if image_override is None:
            image_id = record.image_ref.removeprefix("coco/")
            pil = Image.open(self._image_root / f"{int(image_id):012d}.jpg").convert("RGB")
        elif isinstance(image_override, np.ndarray):
            pil = Image.fromarray(image_override)
        else:
            pil = image_override  # type: ignore[assignment]
        scores: list[float] = []
        prompt = build_prompt(record)
        for i in range(len(record.options)):
            reply = f"{string.ascii_uppercase[i]}."
            messages = [
                {"role": "user", "content": [
                    {"type": "image", "image": pil},
                    {"type": "text", "text": prompt},
                ]},
                {"role": "assistant", "content": [{"type": "text", "text": reply}]},
            ]
            inputs = self._processor.apply_chat_template(
                messages, add_generation_prompt=False, tokenize=True,
                return_dict=True, return_tensors="pt",
            ).to(self._model.device)
            ids_without: list[int] = self._processor.apply_chat_template(
                messages[:1], add_generation_prompt=True, tokenize=True,
                return_dict=True, return_tensors="pt",
            )["input_ids"][0].tolist()
            ids = inputs["input_ids"][0]
            start, end = forced_reply_span(ids_without, ids.tolist())
            decoded = self._processor.tokenizer.decode(
                ids[start:end], skip_special_tokens=True
            ).strip()
            # Verify by decoding, never by assumption (pilot-v1 defect class).
            assert decoded == reply, (
                f"scorer alignment defect: located span decodes to {decoded!r}, "
                f"expected {reply!r}"
            )
            with self._torch.inference_mode():
                logits = self._model(**inputs).logits
            logprobs = self._torch.log_softmax(logits[0, :-1], dim=-1)
            span = logprobs[start - 1 : end - 1].gather(
                1, ids[start:end].unsqueeze(1)
            )
            scores.append(float(span.sum().item()))
        return tuple(scores)
