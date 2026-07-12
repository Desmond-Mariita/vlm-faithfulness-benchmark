"""GLM scorer-agreement diagnostic (rehearsal) — letter vs option-text reading.

The 12-record smoke measured scorer-vs-generation agreement 0.667 (< 0.90
floor): GLM's forced-immediate letter distribution disagrees with its
deliberated (post-think) choice. This diagnostic extends the sample and
compares TWO candidate graded readings on the same records:

- ``letter``: the pinned contract (forced reply ``"<LETTER>."``);
- ``text``: forced reply = the option's exact text (rehearsal-only
  candidate; adopting it would be a registered contract change).

Outputs a decision package for BM. Rehearsal artifacts only — no corpus
readings.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts_run_shard import load_registered_pool  # noqa: E402

from vlm_faithfulness_benchmark.generation.glm_generator import (  # noqa: E402
    GlmGenerator,
    build_prompt,
)
from vlm_faithfulness_benchmark.generation.mc_extraction import (  # noqa: E402
    forced_reply_span,
    refine_reply_span,
)

OUT = ROOT / "data/runs/rehearsal-glm-diagnostic.jsonl"


def score_with_reply(gen: GlmGenerator, rec: "object", pil: "object", reply: str) -> float:
    """Total log-probability of an arbitrary forced reply (diagnostic only).

    Same render/diff/refine machinery as the pinned scorer, with the reply
    text as a parameter.

    Args:
        gen: The loaded GLM generator (its internals are reused).
        rec: The Source Record.
        pil: The record's PIL image.
        reply: The forced assistant reply text.

    Returns:
        The summed reply log-probability.
    """
    messages_user = [
        {"role": "user", "content": [
            {"type": "image", "image": pil},
            {"type": "text", "text": build_prompt(rec)},
        ]},
    ]
    messages = messages_user + [
        {"role": "assistant", "content": [{"type": "text", "text": reply}]}
    ]
    proc = gen._processor
    inputs = proc.apply_chat_template(
        messages, add_generation_prompt=False, tokenize=True,
        return_dict=True, return_tensors="pt",
    ).to(gen._model.device)
    ids_without = proc.apply_chat_template(
        messages_user, add_generation_prompt=True, tokenize=True,
        return_dict=True, return_tensors="pt",
    )["input_ids"][0].tolist()
    ids = inputs["input_ids"][0]
    ids_list = ids.tolist()
    start, end = forced_reply_span(ids_without, ids_list)
    start, end = refine_reply_span(
        ids_list, start, end, reply,
        lambda span: proc.tokenizer.decode(span, skip_special_tokens=True),
    )
    torch = gen._torch
    with torch.inference_mode():
        logits = gen._model(**inputs).logits
    logprobs = torch.log_softmax(logits[0, :-1], dim=-1)
    span = logprobs[start - 1 : end - 1].gather(1, ids[start:end].unsqueeze(1))
    return float(span.sum().item())


def main() -> None:
    """Run the letter-vs-text scorer diagnostic over a pool slice."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=32)
    ap.add_argument("--offset", type=int, default=1000)
    args = ap.parse_args()

    from PIL import Image

    pool = load_registered_pool(ROOT / "config/pool_manifest_v1.json")
    records = pool[args.offset : args.offset + args.n]
    done: set[str] = set()
    if OUT.exists():
        for line in OUT.read_text().splitlines():
            done.add(json.loads(line)["record_id"])

    gen = GlmGenerator(image_root=ROOT / "data/coco-pool")
    print(f"diagnostic: {len(records)} records, {len(done)} done", flush=True)

    for rec in records:
        rid = rec.identity.record_id
        if rid in done:
            continue
        t0 = time.time()
        outcome = gen(rec)
        image_id = rec.image_ref.removeprefix("coco/")
        pil = Image.open(ROOT / "data/coco-pool" / f"{int(image_id):012d}.jpg").convert("RGB")
        letter_scores = gen.score_options(rec)
        text_scores = tuple(
            score_with_reply(gen, rec, pil, opt) for opt in rec.options
        )
        row = {
            "record_id": rid,
            "options": list(rec.options),
            "gold_idx": rec.annotations.get("gold_answer_idx"),
            "chosen_answer": outcome.chosen_answer,
            "letter_scores": list(letter_scores),
            "text_scores": list(text_scores),
            "t_total_s": round(time.time() - t0, 1),
        }
        with open(OUT, "a") as fh:
            fh.write(json.dumps(row) + "\n")
        print(f"{rid[:8]} done in {row['t_total_s']}s", flush=True)

    rows = [json.loads(line) for line in OUT.read_text().splitlines()]
    parsed = [r for r in rows if r["chosen_answer"] is not None]

    def agreement(key: str) -> float:
        agree = 0
        for r in parsed:
            am = max(range(len(r[key])), key=lambda i: r[key][i])
            if r["options"][am].strip().lower() == r["chosen_answer"].strip().lower():
                agree += 1
        return round(agree / max(1, len(parsed)), 3)

    summary = {
        "n": len(rows),
        "parsed": len(parsed),
        "letter_agreement": agreement("letter_scores"),
        "text_agreement": agreement("text_scores"),
        "gold_correct_generation": sum(
            1 for r in parsed
            if r["gold_idx"] is not None
            and r["chosen_answer"] == r["options"][r["gold_idx"]]
        ),
    }
    (ROOT / "data/runs/rehearsal-glm-diagnostic-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print("SUMMARY:", json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
