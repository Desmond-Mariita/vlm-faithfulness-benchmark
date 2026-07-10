r"""Qwen3-VL generator adapter — the first composite generator subject.

Matrix rows: S02-post, CC7 (same subject per call), R3 (identity names every
component), N4.6 (pinned per-generator extraction contract).

Loaded lazily so the package (and the whole test suite) never needs model
weights; only real runs import torch/transformers through here.

**Extraction contract ``aokvqa-mc-v1.1`` (pinned, `08` N4.6):** the prompt
asks for the option letter on the first line and a rationale after the
literal marker ``Rationale:``. Answer extraction applies three rules to the
first line, in order, taking the first that fires (review F-01 retired the
v1 free-floating letter match, which wrong-captured English articles like
"A cigarette"):

1. **Anchored letter with punctuation** — ``^\s*([A-Ha-h])[.):]`` (e.g.
   ``"B. umbrella"``, ``"c)"``).
2. **Bare letter line** — the first line is exactly one letter (e.g. ``"B"``).
3. **Exact option text** — the first line, lowercased and stripped of a
   trailing period, equals exactly one option's text.

No rule firing ⇒ chosen answer is None. The rationale is everything after
the first ``Rationale:`` marker, stripped; absent/empty ⇒ None. Absent
fields make an incomplete Output Tuple, retained per ADR-003 — never
repaired here.

Decoding (RIP-1.0.0 §3): greedy, ``do_sample=False``, ``num_beams=1``,
``max_new_tokens=160`` (pinned in the identity components).

**Option scorer (contract ``option-letter-logprob-v1``):** the graded CC5
reading for S06/S08 is, per option, the total log-probability of the
assistant reply ``"<LETTER>."`` under the same prompt — one forward pass
per option, no sampling. The scorer never sees a gold answer (ADR-004).
"""

from __future__ import annotations

import re
import string
from pathlib import Path

from vlm_faithfulness_benchmark.generation.harness import GenerationOutcome
from vlm_faithfulness_benchmark.generation.identity import GeneratorId
from vlm_faithfulness_benchmark.ingestion.aokvqa import SourceRecord

__all__ = [
    "EXTRACTION_CONTRACT_ID",
    "OPTION_SCORER_ID",
    "build_prompt",
    "extract_outcome",
    "QwenGenerator",
]

EXTRACTION_CONTRACT_ID = "aokvqa-mc-v1.1"
OPTION_SCORER_ID = "option-letter-logprob-v1"
_MODEL_ID = "Qwen/Qwen3-VL-8B-Instruct"
_MAX_NEW_TOKENS = 160
_RATIONALE_MARKER = "Rationale:"


def build_prompt(record: SourceRecord) -> str:
    """Render the pinned prompt for a Source Record (contract aokvqa-mc-v1).

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

    Args:
        generated_text: The generator's decoded output, verbatim.
        options: The instance's options (letter → option text mapping).

    Returns:
        GenerationOutcome; fields are None where extraction finds nothing —
        the tuple stays incomplete rather than repaired (ADR-003/CC4).
    """
    first_line, _, _ = generated_text.strip().partition("\n")
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
    _, marker, tail = generated_text.partition(_RATIONALE_MARKER)
    rationale = tail.strip() if marker and tail.strip() else None
    return GenerationOutcome(chosen_answer=chosen, rationale=rationale)


class QwenGenerator:
    """The composite generator subject (CC7: one subject for every call)."""

    def __init__(self, image_root: Path) -> None:
        """Load the model, processor, and pinned decoding configuration.

        Args:
            image_root: Directory containing the COCO smoke images
                (``<12-digit-id>.jpg``; Source Records reference
                ``coco/<id>``).
        """
        import torch
        from transformers import AutoModelForImageTextToText, AutoProcessor

        self._torch = torch
        self._image_root = image_root
        # transformers' Auto* factories are untyped upstream; the boundary is
        # confined to these three calls (mypy: no-untyped-call/misc).
        self._processor = AutoProcessor.from_pretrained(_MODEL_ID)  # type: ignore[no-untyped-call]
        self._model = AutoModelForImageTextToText.from_pretrained(
            _MODEL_ID, dtype=torch.bfloat16, device_map="cuda:0"
        )
        self._model.eval()  # type: ignore[no-untyped-call]
        revision = getattr(self._model.config, "_commit_hash", None)
        # Review F-02: a subject without a pinned weight revision is not a
        # complete composite identity (R3) — halt rather than record "unpinned".
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

        Same composite subject, same decoding pins (CC7); only the visual
        input varies — which is exactly what an intervention is.

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
        """Score each option's reply log-probability (contract option-letter-logprob-v1).

        Args:
            record: The Source Record (prompt source).
            image_override: A PIL image or HxWx3 uint8 array to score
                against instead of the record's own image (regime/sweep
                inputs); None uses the record's image.

        Returns:
            Per-option total log-probabilities of the reply ``"<LETTER>."``
            — the CC5 graded reading consumed by Condition A and the S08
            sweep.
        """
        import string

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
            reply_token_count = len(
                self._processor.tokenizer(reply, add_special_tokens=False)["input_ids"]
            )
            with self._torch.inference_mode():
                logits = self._model(**inputs).logits
            ids = inputs["input_ids"][0]
            logprobs = self._torch.log_softmax(logits[0, :-1], dim=-1)
            tail = logprobs[-reply_token_count:].gather(
                1, ids[-reply_token_count:].unsqueeze(1)
            )
            scores.append(float(tail.sum().item()))
        return tuple(scores)
