r"""Kimi-VL-A3B-Instruct generator adapter — registered BACKUP subject.

Matrix rows: S02-post, CC7, R3, N4.6.

**Status:** registered backup to DeepSeek-VL2 (BM decision, M9 plan): it
substitutes — as a *recorded substitution*, never silently — only if the
DeepSeek-VL2 lane hits a material hurdle (environment breakage on the
rental machine, license blocker, or a failed instrument sanity gate).

Loads via ``transformers`` with ``trust_remote_code=True`` (Moonshot ships
the modeling code in the checkpoint repo). 16B MoE, ~2.8B active; ~32 GB
bf16 — cloud-class for full precision; the local 24 GB card can exercise
the plumbing only under 8-bit quantization, which changes the composite
identity and is therefore **never** used for corpus runs. Quantization
enforcement (panel F-11): the identity honestly records the quantized
dtype (detection), and the mass-run driver ``scripts_run_shard.py``
refuses any identity whose dtype is not bf16 before a single record is
committed (prevention at the only ledger-writing entry point).

Inference follows the model card's documented TWO-STEP path (panel F-01/
F-04: the one-step tokenizing chat-template call is not the published
interface): first ``apply_chat_template(..., tokenize=False)`` renders the
prompt text, then ``processor(images=..., text=...)`` builds the batch.
Every call asserts the processed inputs actually carry image features —
the silent failure mode (text-only inputs scoring without the image) would
invalidate the lane while looking healthy, so it must halt instead.

**Extraction contract ``aokvqa-mc-kimi-v1`` (pinned):** plain instruct
model — the shared three answer rules + ``Rationale:`` marker rule apply
directly to the decoded text.

Decoding: greedy, ``do_sample=False``, ``max_new_tokens=160``.

**Option scorer (contract ``option-letter-logprob-kimi-v1``):** forced
assistant reply ``"<LETTER>."``; the span is the prefix/suffix diff between
the with-reply and generation-prompt renders (never assumed), verified by
decoding; any mismatch halts.
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
)
from vlm_faithfulness_benchmark.ingestion.aokvqa import SourceRecord

__all__ = [
    "EXTRACTION_CONTRACT_ID",
    "OPTION_SCORER_ID",
    "build_prompt",
    "extract_outcome",
    "KimiGenerator",
]

EXTRACTION_CONTRACT_ID = "aokvqa-mc-kimi-v1"
OPTION_SCORER_ID = "option-letter-logprob-kimi-v1"
_MODEL_ID = "moonshotai/Kimi-VL-A3B-Instruct"
_MAX_NEW_TOKENS = 160


def build_prompt(record: SourceRecord) -> str:
    """Render the pinned prompt (generator-invariant wording).

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
    """Apply contract aokvqa-mc-kimi-v1 to raw decoded text.

    Args:
        generated_text: The generator's decoded output, verbatim.
        options: The instance's options.

    Returns:
        GenerationOutcome; fields are None where extraction finds nothing
        (ADR-003/CC4 — never repaired).
    """
    return extract_mc_outcome(generated_text, options)


class KimiGenerator:
    """The Kimi-VL-A3B composite subject (CC7: one subject for every call)."""

    def __init__(self, image_root: Path, load_in_8bit: bool = False) -> None:
        """Load the model, processor, and pinned decoding configuration.

        Args:
            image_root: Directory containing the COCO pool images
                (``<12-digit-id>.jpg``; Source Records reference
                ``coco/<id>``).
            load_in_8bit: Local plumbing-test mode ONLY (24 GB card). The
                quantized subject is a different composite identity; the
                identity string records it, and corpus-run drivers must
                refuse it.

        Raises:
            AssertionError: If ``load_in_8bit`` is requested without
                ``ALLOW_PLUMBING_TEST_MODE=1`` in the environment — the
                quantized mode is a code-enforced invariant, not a
                convention (panel Gemini F-02).
        """
        import os

        import torch
        from transformers import AutoModelForCausalLM, AutoProcessor

        assert not load_in_8bit or os.environ.get("ALLOW_PLUMBING_TEST_MODE") == "1", (
            "quantized (8-bit) mode is plumbing-test only; set "
            "ALLOW_PLUMBING_TEST_MODE=1 to acknowledge (never for corpus runs)"
        )

        self._torch = torch
        self._image_root = image_root
        self._quantized = load_in_8bit
        self._processor = AutoProcessor.from_pretrained(  # type: ignore[no-untyped-call]
            _MODEL_ID, trust_remote_code=True
        )
        if load_in_8bit:
            from transformers import BitsAndBytesConfig

            self._model = AutoModelForCausalLM.from_pretrained(
                _MODEL_ID,
                trust_remote_code=True,
                quantization_config=BitsAndBytesConfig(load_in_8bit=True),  # type: ignore[no-untyped-call]
                device_map="cuda:0",
            )
        else:
            self._model = AutoModelForCausalLM.from_pretrained(
                _MODEL_ID,
                trust_remote_code=True,
                dtype=torch.bfloat16,
                device_map="cuda:0",
            )
        self._model.eval()  # type: ignore[no-untyped-call]
        revision = getattr(self._model.config, "_commit_hash", None)
        # R3: halt rather than record an unpinned composite identity.
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
                "prompt_template": EXTRACTION_CONTRACT_ID,
                "image_preprocessing": "pil-rgb-native",
                "dtype": "int8-plumbing-test-only" if self._quantized else "bfloat16",
            }
        )

    def scorer_generation_agreement(self, records: "list[SourceRecord]") -> float:
        """Measure scorer-vs-generation agreement on unperturbed images.

        The instrument sanity gate: must clear the registered 0.90 floor on
        a small batch before any readings-dependent mass run.

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
        """Run the generator on an explicit image (regime/edited inputs).

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
        inputs = self._process(image, build_prompt(record), reply=None)
        with self._torch.inference_mode():
            generated = self._model.generate(  # type: ignore[misc]
                **inputs,
                do_sample=False,
                num_beams=1,
                max_new_tokens=_MAX_NEW_TOKENS,
            )
        new_tokens = generated[0, inputs["input_ids"].shape[1] :]
        text = self._processor.decode(new_tokens, skip_special_tokens=True)
        return extract_outcome(text, record.options)

    def _process(self, image: "object", prompt: str, reply: str | None) -> Any:
        """Build model inputs via the documented two-step processor path.

        Args:
            image: PIL image for the user turn.
            prompt: The user-turn text.
            reply: Forced assistant reply, or None for a generation prompt.

        Returns:
            The processor's batch on device, guaranteed to carry image
            features (transformers' untyped BatchFeature — the Any boundary
            is confined to this method's return).

        Raises:
            AssertionError: If the processed batch has no image features —
                text-only inputs would silently invalidate the lane.
        """
        messages: list[dict[str, object]] = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        if reply is not None:
            messages.append(
                {"role": "assistant", "content": [{"type": "text", "text": reply}]}
            )
        text = self._processor.apply_chat_template(
            messages, add_generation_prompt=reply is None, tokenize=False
        )
        inputs = self._processor(
            images=image, text=text, return_tensors="pt", padding=True
        ).to(self._model.device)
        # Panel F-04: halt if the batch silently dropped the image — a
        # text-only lane would look healthy while measuring nothing.
        assert "pixel_values" in inputs and inputs["pixel_values"].numel() > 0, (
            "kimi processor produced no image features (text-only inputs refused)"
        )
        return inputs

    def score_options(
        self, record: SourceRecord, image_override: "object | None" = None
    ) -> tuple[float, ...]:
        """Score each option's forced-reply log-probability.

        Contract ``option-letter-logprob-kimi-v1``: per option, one forward
        pass over the conversation with the assistant turn forced to
        ``"<LETTER>."``; the reply span is the prefix/suffix diff against
        the generation-prompt render, verified by decoding. Mismatch halts.

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
        ids_without: list[int] = self._process(pil, prompt, reply=None)[
            "input_ids"
        ][0].tolist()
        for i in range(len(record.options)):
            reply = f"{string.ascii_uppercase[i]}."
            inputs = self._process(pil, prompt, reply=reply)
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
            span = logprobs[start - 1 : end - 1].gather(1, ids[start:end].unsqueeze(1))
            scores.append(float(span.sum().item()))
        return tuple(scores)
