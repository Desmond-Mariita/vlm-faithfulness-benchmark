"""GLM no-think mode diagnostic (rehearsal) — candidate contract resolution.

The letter scorer's 0.774 agreement gap traces to the think-mode construct
split: generation deliberates, the scorer reads the immediate distribution.
GLM's chat template supports ``enable_thinking=False`` (inserts the same
empty think scaffold the scorer conditions on). This measures, on the same
32 records as the prior diagnostic: no-think extraction quality
(parse/rationale rates), scorer agreement in matched mode, and gold
accuracy vs the thinking mode. Rehearsal artifact; adopting no-think mode
would be a registered contract change (aokvqa-mc-glm-v2).
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
    extract_outcome,
)

OUT = ROOT / "data/runs/rehearsal-glm-nothink.jsonl"


def generate_nothink(gen: GlmGenerator, rec: "object", pil: "object") -> str:
    """Greedy generation with the template's thinking toggle OFF.

    Args:
        gen: The loaded GLM generator (internals reused; rehearsal only).
        rec: The Source Record.
        pil: The record's PIL image.

    Returns:
        The raw decoded text.
    """
    messages = [
        {"role": "user", "content": [
            {"type": "image", "image": pil},
            {"type": "text", "text": build_prompt(rec)},
        ]},
    ]
    inputs = gen._processor.apply_chat_template(
        messages, add_generation_prompt=True, tokenize=True,
        return_dict=True, return_tensors="pt", enable_thinking=False,
    ).to(gen._model.device)
    with gen._torch.inference_mode():
        generated = gen._model.generate(
            **inputs, do_sample=False, num_beams=1, max_new_tokens=256,
        )
    new_tokens = generated[0, inputs["input_ids"].shape[1] :]
    return gen._processor.decode(new_tokens, skip_special_tokens=True)


def main() -> None:
    """Run the no-think diagnostic over the same pool slice."""
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
    print(f"no-think diagnostic: {len(records)} records, {len(done)} done", flush=True)

    for rec in records:
        rid = rec.identity.record_id
        if rid in done:
            continue
        t0 = time.time()
        image_id = rec.image_ref.removeprefix("coco/")
        pil = Image.open(ROOT / "data/coco-pool" / f"{int(image_id):012d}.jpg").convert("RGB")
        raw = generate_nothink(gen, rec, pil)
        outcome = extract_outcome(raw, rec.options)
        scores = gen.score_options(rec)
        argmax = max(range(len(scores)), key=lambda i: scores[i])
        row = {
            "record_id": rid,
            "options": list(rec.options),
            "gold_idx": rec.annotations.get("gold_answer_idx"),
            "raw_text": raw,
            "chosen_answer": outcome.chosen_answer,
            "rationale": outcome.rationale,
            "scorer_argmax_option": rec.options[argmax],
            "scores": list(scores),
            "t_total_s": round(time.time() - t0, 1),
        }
        with open(OUT, "a") as fh:
            fh.write(json.dumps(row) + "\n")
        print(f"{rid[:8]} answer={outcome.chosen_answer!r} "
              f"rationale={'yes' if outcome.rationale else 'NO'} "
              f"t={row['t_total_s']}s", flush=True)

    rows = [json.loads(line) for line in OUT.read_text().splitlines()]
    parsed = [r for r in rows if r["chosen_answer"] is not None]
    agree = sum(
        1 for r in parsed
        if r["scorer_argmax_option"].strip().lower() == r["chosen_answer"].strip().lower()
    )
    summary = {
        "n": len(rows),
        "parsed": len(parsed),
        "with_rationale": sum(1 for r in rows if r["rationale"]),
        "leaked_think_tag": sum(1 for r in rows if "<think>" in r["raw_text"]),
        "scorer_agreement_nothink": round(agree / max(1, len(parsed)), 3),
        "gold_correct_of_parsed": sum(
            1 for r in parsed
            if r["gold_idx"] is not None
            and r["chosen_answer"] == r["options"][r["gold_idx"]]
        ),
        "mean_t_total_s": round(sum(r["t_total_s"] for r in rows) / max(1, len(rows)), 1),
    }
    (ROOT / "data/runs/rehearsal-glm-nothink-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n"
    )
    print("SUMMARY:", json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
