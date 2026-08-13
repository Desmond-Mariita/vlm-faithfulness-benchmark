r"""Gemma 4 12B generator adapter — candidate fourth composite subject.

Matrix rows: S02-post, CC7 (same subject per call), R3 (identity names every
component), N4.6 (pinned per-generator extraction contract).

**Status: cloud-validated-pending.** Every model-touching path below is
unexercised: Gemma 4 12B needs ~27 GB at bf16 (vendor estimate, unmeasured)
and cannot be loaded on the 24 GB local card. Nothing here may be treated as
working until a CAL-50 gate and a throughput probe have run on an 80 GB box
(`m9_throughput_probe_protocol.md`). This banner exists because the Kimi
adapter looked healthy for a month while its bf16 path could not execute at
all (run log 2026-08-12): "the adapter imports" is not evidence.

**Environment.** Unlike Kimi (pinned ``transformers==4.48.2``) and DeepSeek
(``deepseek_vl2`` on CPython 3.10), Gemma 4 targets current transformers and
runs in the **main** venv alongside Qwen and GLM — no isolated environment,
so no separate requirements pin is registered for it.

**Why this candidate (M9 fourth-family question).** Google lineage shares no
LLM backbone with Qwen, GLM, DeepSeek or Moonlight/Kimi, so it is
generator-disjoint for the OOD-Model split under a backbone-lineage family
relation (`08` N6.7a/N7.1). Apache 2.0 (2026-04-02) with no acceptable-use
or jurisdictional carve-out, so it carries none of the non-commercial
output-rights doubt that blocks Molmo 2 (`08` N10.4).

**Architecture note.** Gemma 4 12B is *encoder-free*: raw image patches are
projected straight into the LLM embedding space rather than passing through
a CLIP/SigLIP tower. Consequences here: (i) the model card documents
``AutoModelForMultimodalLM``, NOT the ``AutoModelForImageTextToText`` that
the Qwen and GLM adapters use — the class is pinned to what the card
documents; (ii) there is no vision-tower submodule to interrogate, so the
"did the image actually reach the model?" invariant is enforced on the
processed batch, and accepts the alternative feature keys an encoder-free
processor may emit (see :func:`_assert_carries_image`).

**Extraction contract ``aokvqa-mc-gemma-v1`` (pinned, `08` N4.6):** the
prompt is construct-identical to the other lanes (D1/D2 unified position:
the visible rationale is the entire stated reasoning) — option letter on the
first line, rationale after the literal marker ``Rationale:``. Gemma is a
plain instruct model with no thinking scaffold, so the shared multi-generator
core applies directly: the three answer rules (anchored letter, bare letter
line, exact option text) plus the ``Rationale:`` marker rule, via
:func:`~vlm_faithfulness_benchmark.generation.mc_extraction.extract_mc_outcome`.
Absent fields make an incomplete Output Tuple, retained per ADR-003 — never
repaired here.

Decoding (RIP-1.0.0 §3): greedy, ``do_sample=False``, ``num_beams=1``,
``max_new_tokens=160`` — matching Qwen and Kimi. (GLM's 256 is a
GLM-contract artifact, not the house default.)

**Option scorer (contract ``option-letter-logprob-gemma-v1``):** per option,
the total log-probability of the assistant reply ``"<LETTER>."`` under the
same prompt — one forward pass per option, no sampling. The scorer never
sees a gold answer (ADR-004). The reply span is located by prefix/suffix
diff against the generation-prompt render and refined to the minimal
sub-span that decodes to the reply, then **verified by decoding** rather
than assumed; any mismatch or ambiguity halts, because silently scoring
option-independent scaffold is the v1 defect class the pilot caught only by
accident.
"""

from __future__ import annotations

import string
from pathlib import Path
from typing import Any

from vlm_faithfulness_benchmark.generation.harness import GenerationOutcome
from vlm_faithfulness_benchmark.generation.identity import GeneratorId
from vlm_faithfulness_benchmark.generation.mc_extraction import (
    extract_mc_outcome,
    forced_reply_span,
    refine_reply_span,
)
from vlm_faithfulness_benchmark.ingestion.aokvqa import SourceRecord

__all__ = [
    "EXTRACTION_CONTRACT_ID",
    "OPTION_SCORER_ID",
    "build_prompt",
    "extract_outcome",
    "GemmaGenerator",
]

EXTRACTION_CONTRACT_ID = "aokvqa-mc-gemma-v1"
OPTION_SCORER_ID = "option-letter-logprob-gemma-v1"
_MODEL_ID = "google/gemma-4-12B-it"
_REVISION = "707f0a3b8a3c7ad586ed01e27eafbad8a27dd0f7"
_MAX_NEW_TOKENS = 160
_RATIONALE_MARKER = "Rationale:"
# Feature keys an image-carrying batch may use. Encoder-free processors need
# not emit `pixel_values`; the invariant is that SOME image feature arrives.
_IMAGE_FEATURE_KEYS = ("pixel_values", "image_patches", "input_image_patches")


def build_prompt(record: SourceRecord) -> str:
    """Render the pinned prompt for a Source Record (contract aokvqa-mc-gemma-v1).

    Deliberately byte-identical to the Qwen/Kimi prompt: the construct under
    test must not vary with the generator (D1/D2 unified position).

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
        f'then explain your reasoning after "{_RATIONALE_MARKER}".'
    )


def extract_outcome(generated_text: str, options: tuple[str, ...]) -> GenerationOutcome:
    """Apply the pinned extraction contract to raw generated text.

    Gemma emits no thinking scaffold, so the shared core applies unmodified.

    Args:
        generated_text: The generator's decoded output, verbatim.
        options: The instance's options (letter → option text mapping).

    Returns:
        GenerationOutcome; fields are None where extraction finds nothing —
        the tuple stays incomplete rather than repaired (ADR-003/CC4).
    """
    return extract_mc_outcome(generated_text, options)


def _assert_carries_image(inputs: Any) -> None:
    """Halt unless the processed batch actually carries image features.

    The silent failure mode for an encoder-free model is a batch that
    tokenized the text but dropped the image: generation and scoring then
    proceed happily on text alone, producing a plausible-looking lane that
    measures the wrong construct entirely. Gemma 4 has no vision tower to
    interrogate, so the batch itself is the only place to check.

    Args:
        inputs: The processor's returned batch mapping.

    Raises:
        AssertionError: If no recognized image-feature key is present and
            non-empty.
    """
    present = [k for k in _IMAGE_FEATURE_KEYS if inputs.get(k) is not None]
    assert present, (
        f"gemma processor produced no image features (looked for "
        f"{_IMAGE_FEATURE_KEYS}); refusing a text-only forward pass"
    )
    for key in present:
        assert inputs[key].numel() > 0, f"image feature {key!r} is empty"


class GemmaGenerator:
    """The Gemma 4 12B composite subject (CC7: one subject for every call)."""

    def __init__(self, image_root: Path) -> None:
        """Load the model, processor, and pinned decoding configuration.

        Args:
            image_root: Directory containing the COCO pool images
                (``<12-digit-id>.jpg``; Source Records reference
                ``coco/<id>``).

        Raises:
            AssertionError: On checkpoint/architecture mismatch, a
                non-bfloat16 loaded dtype, or an unavailable weight revision
                — each of which would otherwise produce a subject that runs
                while being the wrong subject.
        """
        import torch
        from transformers import AutoModelForMultimodalLM, AutoProcessor

        self._torch = torch
        self._image_root = image_root
        # transformers' Auto* factories are untyped upstream; the boundary is
        # confined to these calls (mypy: no-untyped-call/misc).
        self._processor = AutoProcessor.from_pretrained(  # type: ignore[no-untyped-call]
            _MODEL_ID, revision=_REVISION
        )
        # Class pinned to the model card's documented entry point for the
        # encoder-free architecture. With output_loading_info=True
        # from_pretrained returns a 2-tuple; upstream stubs don't model that.
        loaded: Any = AutoModelForMultimodalLM.from_pretrained(
            _MODEL_ID,
            revision=_REVISION,
            dtype=torch.bfloat16,
            device_map="cuda:0",
            output_loading_info=True,
        )
        self._model, loading_info = loaded
        # A checkpoint/architecture mismatch surfaces as "missing keys" that
        # transformers silently NEWLY INITIALIZES — garbage weights
        # masquerading as a loaded subject. Halt, never degrade.
        missing = loading_info.get("missing_keys", [])
        assert not missing, (
            f"checkpoint/architecture mismatch: {len(missing)} keys missing "
            f"from the checkpoint would be newly initialized (e.g. {missing[:3]})"
        )
        # The identity claims bfloat16 and the mass-run driver refuses any
        # other dtype. Assert the LOADED dtype rather than trusting that the
        # keyword was honoured: the Kimi adapter passed a dtype keyword its
        # pinned transformers did not accept, and nothing caught it until the
        # first real load (run log 2026-08-12).
        loaded_dtype = getattr(self._model, "dtype", None)
        assert loaded_dtype == torch.bfloat16, (
            f"loaded dtype is {loaded_dtype!r}, not bfloat16; the composite "
            "identity would misdescribe the subject"
        )
        self._model.eval()
        loaded_revision = getattr(self._model.config, "_commit_hash", None)
        assert loaded_revision == _REVISION, (
            f"R3: requested revision {_REVISION} but loaded {loaded_revision!r}"
        )
        self._revision = _REVISION

    def identity(self) -> GeneratorId:
        """The composite identity naming every component (R3, ADR-005).

        Returns:
            The GeneratorId whose key is recorded on every emitted record.
        """
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

        The quantity the CAL-50 instrument sanity gate thresholds
        (prereg-m9-v1): the fraction of parseable records where the scorer's
        argmax matches the generator's own emitted choice.

        Args:
            records: A small validation batch.

        Returns:
            Agreement fraction in [0, 1] over records whose generation
            parsed to an option.

        Raises:
            AssertionError: If no generation in the batch parsed.
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

    def _open_pool_image(self, record: SourceRecord) -> Any:
        """Open a record's pool image as PIL RGB.

        Args:
            record: The Source Record whose ``image_ref`` names the file.

        Returns:
            The PIL image in RGB.
        """
        from PIL import Image

        image_id = record.image_ref.removeprefix("coco/")
        return Image.open(self._image_root / f"{int(image_id):012d}.jpg").convert("RGB")

    def _resolve_image(self, record: SourceRecord, image_override: "object | None") -> Any:
        """Return the PIL image to condition on.

        Args:
            record: The Source Record (supplies the default image).
            image_override: A PIL image, an HxWx3 uint8 array, or None.

        Returns:
            A PIL image.
        """
        import numpy as np
        from PIL import Image

        if image_override is None:
            return self._open_pool_image(record)
        if isinstance(image_override, np.ndarray):
            return Image.fromarray(image_override)
        return image_override

    def _process(self, pil: Any, prompt: str, reply: str | None) -> Any:
        """Build one processed batch, with or without a forced assistant reply.

        Args:
            pil: The PIL image to condition on.
            prompt: The rendered user-turn text.
            reply: The forced assistant reply (scoring), or None to render
                the generation prompt.

        Returns:
            The processed batch, on the model's device.

        Raises:
            AssertionError: If the batch carries no image features.
        """
        messages: list[dict[str, Any]] = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": pil},
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        if reply is not None:
            messages.append(
                {"role": "assistant", "content": [{"type": "text", "text": reply}]}
            )
        inputs = self._processor.apply_chat_template(
            messages,
            add_generation_prompt=reply is None,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        ).to(self._model.device)
        _assert_carries_image(inputs)
        return inputs

    def __call__(self, record: SourceRecord) -> GenerationOutcome:
        """Run the generator once over a Source Record (S02).

        Args:
            record: The normalized Source Record.

        Returns:
            The emitted outcome under the pinned extraction contract.
        """
        return self.generate_on(record, self._open_pool_image(record))

    def generate_on(self, record: SourceRecord, image: "object") -> GenerationOutcome:
        """Run the generator on an explicit image (regime/edited inputs, S06/S09).

        Same composite subject, same decoding pins (CC7); only the visual
        input varies — which is exactly what an intervention is.

        Args:
            record: The normalized Source Record (prompt source).
            image: A PIL image or HxWx3 uint8 array.

        Returns:
            The emitted outcome under the pinned extraction contract.
        """
        pil = self._resolve_image(record, image)
        inputs = self._process(pil, build_prompt(record), reply=None)
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

    def score_options(
        self, record: SourceRecord, image_override: "object | None" = None
    ) -> tuple[float, ...]:
        """Score each option's forced-reply log-probability.

        Contract ``option-letter-logprob-gemma-v1``: per option, one forward
        pass over the conversation with the assistant turn forced to
        ``"<LETTER>."``; the reply span is the prefix/suffix diff against the
        generation-prompt render, refined to the minimal sub-span decoding to
        the reply and verified by decoding. Mismatch or ambiguity halts.

        Args:
            record: The Source Record (prompt source).
            image_override: A PIL image or HxWx3 uint8 array to score
                against instead of the record's own image (regime/sweep
                inputs); None uses the record's image.

        Returns:
            Per-option total log-probabilities of the reply ``"<LETTER>."``
            — the CC5 graded reading consumed by Condition A and the S08
            sweep.

        Raises:
            AssertionError: If a reply span cannot be located unambiguously,
                or a batch carries no image features.
        """
        pil = self._resolve_image(record, image_override)
        prompt = build_prompt(record)
        ids_without: list[int] = self._process(pil, prompt, reply=None)["input_ids"][
            0
        ].tolist()
        scores: list[float] = []
        for i in range(len(record.options)):
            scores.append(self._score_one_option(pil, prompt, ids_without, i))
        return tuple(scores)

    def _score_one_option(
        self, pil: Any, prompt: str, ids_without: list[int], option_index: int
    ) -> float:
        """Total log-probability of the forced reply for one option.

        Args:
            pil: The PIL image to condition on.
            prompt: The rendered user-turn text.
            ids_without: Input ids of the generation-prompt render, reused
                across options (the diff baseline).
            option_index: Zero-based option index (0 → ``"A."``).

        Returns:
            The summed log-probability of the reply tokens.

        Raises:
            AssertionError: If the reply span cannot be located unambiguously.
        """
        reply = f"{string.ascii_uppercase[option_index]}."
        inputs = self._process(pil, prompt, reply=reply)
        ids = inputs["input_ids"][0]
        ids_list: list[int] = ids.tolist()
        start, end = forced_reply_span(ids_without, ids_list)
        # Refine to the minimal sub-span decoding to the reply: a template
        # may inject scaffold inside the insertion. Halt on ambiguity.
        start, end = refine_reply_span(
            ids_list,
            start,
            end,
            reply,
            lambda span: self._processor.tokenizer.decode(span, skip_special_tokens=True),
        )
        with self._torch.inference_mode():
            logits = self._model(**inputs).logits
        # LaTeX: s_i = \sum_{t=1}^{n_i} \log p\!\left(y^{(i)}_t \mid x, y^{(i)}_{<t}\right)
        # Position t of `logits` predicts token t+1, hence the -1 shift on
        # both the log-softmax slice and the span bounds.
        logprobs = self._torch.log_softmax(logits[0, :-1], dim=-1)
        span = logprobs[start - 1 : end - 1].gather(1, ids[start:end].unsqueeze(1))
        return float(span.sum().item())
