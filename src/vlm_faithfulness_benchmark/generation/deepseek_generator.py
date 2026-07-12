r"""DeepSeek-VL2 generator adapter — third composite generator subject.

Matrix rows: S02-post, CC7, R3, N4.6.

**Environment (isolated — see ``config/env_deepseek_vl2_requirements.txt``):**
DeepSeek-VL2 is *not* natively supported by the ``transformers`` library; it
loads through DeepSeek's own ``deepseek_vl2`` package, which pins an older
``transformers`` than the one the Qwen/GLM adapters require. The sharded
mass-run driver therefore runs this adapter in its **own virtual
environment**; nothing here may be imported into the same process as the
other adapters' model stacks (the pure-text functions are safe everywhere).
The 27B MoE weights (~4.5B active) need a cloud-class GPU; this adapter is
**cloud-validated-pending** — its model-touching paths cannot be exercised
on the local 24 GB card, and every alignment ambiguity is an assert that
halts rather than mis-scores.

**License (verified 2026-07-12):** code MIT; weights under the DeepSeek
Model License — commercial use permitted, outputs owned by the user,
use-based restrictions (Attachment A) that benchmark generation does not
touch; redistribution of the *model* requires passing the license through.
We redistribute only outputs, which the license does not claim.

**Extraction contract ``aokvqa-mc-dsvl2-v1`` (pinned):** DeepSeek-VL2 is a
plain instruct model (no thinking scaffold): the shared three answer rules
+ ``Rationale:`` marker rule apply directly to the decoded text.

Decoding: greedy, ``do_sample=False``, ``max_new_tokens=160`` (matches the
Qwen pin; no thinking budget needed).

**Option scorer (contract ``option-letter-logprob-dsvl2-v1``):** per
option, the total log-probability of the forced assistant reply
``"<LETTER>."``, computed through DeepSeek's processor/embedding path. The
reply span is the prefix/suffix diff between the with-reply render and the
empty-reply render (panel F-03: the conversation template renders
``<|Assistant|>: <reply>``, so the reply's first token carries a
leading-space BPE prefix that standalone tokenization would never match —
the diff makes no such assumption), verified by decoding; mismatch halts.
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
    "DeepseekVL2Generator",
]

EXTRACTION_CONTRACT_ID = "aokvqa-mc-dsvl2-v1"
OPTION_SCORER_ID = "option-letter-logprob-dsvl2-v1"
_MODEL_ID = "deepseek-ai/deepseek-vl2"
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
    """Apply contract aokvqa-mc-dsvl2-v1 to raw decoded text.

    Args:
        generated_text: The generator's decoded output, verbatim.
        options: The instance's options.

    Returns:
        GenerationOutcome; fields are None where extraction finds nothing
        (ADR-003/CC4 — never repaired).
    """
    return extract_mc_outcome(generated_text, options)


class DeepseekVL2Generator:
    """The DeepSeek-VL2 composite subject (CC7: one subject for every call)."""

    def __init__(self, image_root: Path) -> None:
        """Load the model through DeepSeek's own package (isolated venv).

        Args:
            image_root: Directory containing the COCO pool images
                (``<12-digit-id>.jpg``; Source Records reference
                ``coco/<id>``).

        Raises:
            ImportError: If the ``deepseek_vl2`` package is absent — this
                adapter must run in its dedicated environment.
        """
        import torch
        from deepseek_vl2.models import (  # type: ignore[import-not-found]
            DeepseekVLV2ForCausalLM,
            DeepseekVLV2Processor,
        )

        self._torch = torch
        self._image_root = image_root
        self._processor = DeepseekVLV2Processor.from_pretrained(_MODEL_ID)
        self._tokenizer = self._processor.tokenizer
        model = DeepseekVLV2ForCausalLM.from_pretrained(
            _MODEL_ID, trust_remote_code=True, torch_dtype=torch.bfloat16
        )
        self._model = model.cuda().eval()
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
                "image_preprocessing": "deepseek-vl2-processor-native",
                "dtype": "bfloat16",
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

    def _load_record_image(self, record: SourceRecord) -> "object":
        """Open a record's pool image as PIL RGB.

        Args:
            record: The Source Record.

        Returns:
            The PIL image.
        """
        from PIL import Image

        image_id = record.image_ref.removeprefix("coco/")
        return Image.open(self._image_root / f"{int(image_id):012d}.jpg").convert("RGB")

    def _prepare(self, record: SourceRecord, image: "object", reply: str) -> Any:
        """Build batched model inputs for a conversation with a fixed reply.

        Args:
            record: The Source Record (prompt source).
            image: PIL image for the user turn.
            reply: Assistant-turn content ("" for generation prompts).

        Returns:
            The processor's batched prepare-inputs object, on device
            (deepseek_vl2's untyped batch container — the Any boundary is
            confined to this method's return).
        """
        conversation = [
            {
                "role": "<|User|>",
                "content": "<image>\n" + build_prompt(record),
                "images": [image],
            },
            {"role": "<|Assistant|>", "content": reply},
        ]
        prepared = self._processor(
            conversations=conversation,
            images=[image],
            force_batchify=True,
            system_prompt="",
        )
        return prepared.to(self._model.device)

    def __call__(self, record: SourceRecord) -> GenerationOutcome:
        """Run the generator once over a Source Record (S02).

        Args:
            record: The normalized Source Record.

        Returns:
            The emitted outcome under the pinned extraction contract.
        """
        return self.generate_on(record, self._load_record_image(record))

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
        prepared = self._prepare(record, image, reply="")
        with self._torch.inference_mode():
            inputs_embeds = self._model.prepare_inputs_embeds(**prepared)
            generated = self._model.language.generate(
                inputs_embeds=inputs_embeds,
                attention_mask=prepared.attention_mask,
                pad_token_id=self._tokenizer.eos_token_id,
                eos_token_id=self._tokenizer.eos_token_id,
                do_sample=False,
                num_beams=1,
                max_new_tokens=_MAX_NEW_TOKENS,
                use_cache=True,
            )
        text = self._tokenizer.decode(generated[0], skip_special_tokens=True)
        return extract_outcome(text, record.options)

    def score_options(
        self, record: SourceRecord, image_override: "object | None" = None
    ) -> tuple[float, ...]:
        """Score each option's forced-reply log-probability.

        Contract ``option-letter-logprob-dsvl2-v1``: the conversation is
        rendered with the assistant turn forced to ``"<LETTER>."``; the
        reply span is the prefix/suffix diff against the empty-reply render
        (never assumed), verified by decoding, and its total
        log-probability is read from one forward pass. Mismatch halts.

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
            pil = self._load_record_image(record)
        elif isinstance(image_override, np.ndarray):
            pil = Image.fromarray(image_override)
        else:
            pil = image_override
        ids_without: list[int] = (
            self._prepare(record, pil, reply="").input_ids[0].tolist()
        )
        scores: list[float] = []
        for i in range(len(record.options)):
            reply = f"{string.ascii_uppercase[i]}."
            prepared = self._prepare(record, pil, reply=reply)
            ids = prepared.input_ids[0]
            start, end = forced_reply_span(ids_without, ids.tolist())
            decoded = self._tokenizer.decode(
                ids[start:end], skip_special_tokens=True
            ).strip()
            # Verify by decoding, never by assumption (pilot-v1 defect class).
            assert decoded == reply, (
                f"scorer alignment defect: located span decodes to {decoded!r}, "
                f"expected {reply!r}"
            )
            with self._torch.inference_mode():
                inputs_embeds = self._model.prepare_inputs_embeds(**prepared)
                logits = self._model.language(
                    inputs_embeds=inputs_embeds,
                    attention_mask=prepared.attention_mask,
                ).logits
            logprobs = self._torch.log_softmax(logits[0, :-1], dim=-1)
            span = logprobs[start - 1 : end - 1].gather(1, ids[start:end].unsqueeze(1))
            scores.append(float(span.sum().item()))
        return tuple(scores)
