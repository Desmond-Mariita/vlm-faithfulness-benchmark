"""GLM-4.6V-Flash local rehearsal smoke (3090) — rehearsal artifacts, not corpus.

Produces the BM-review deliverables pinned in the M9 adapter disposition:
per-record raw outputs + contract extractions, scorer-vs-generation
agreement (registered floor 0.90), think-block diagnostics
(marker-compliance and unclosed-think rates — the GLM attrition question),
and per-record timing. Record-idempotent: rerunning skips completed
records (JSONL keyed by record id).

Usage::

    python scripts_dev_smoke_glm.py [--n 12] [--offset 1000]
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

from vlm_faithfulness_benchmark.generation.glm_generator import GlmGenerator  # noqa: E402


def main() -> None:
    """Run the GLM rehearsal smoke over a fixed pool slice."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--offset", type=int, default=1000)
    ap.add_argument(
        "--out", type=Path, default=ROOT / "data/runs/rehearsal-glm-smoke.jsonl"
    )
    args = ap.parse_args()
    OUT = args.out

    pool = load_registered_pool(ROOT / "config/pool_manifest_v1.json")
    records = pool[args.offset : args.offset + args.n]
    done: set[str] = set()
    if OUT.exists():
        for line in OUT.read_text().splitlines():
            done.add(json.loads(line)["record_id"])
    print(f"smoke: {len(records)} records, {len(done)} already done", flush=True)

    t_load = time.time()
    gen = GlmGenerator(image_root=ROOT / "data/coco-pool")
    print(f"loaded in {time.time() - t_load:.0f}s | identity: {gen.identity().key()}", flush=True)

    for rec in records:
        rid = rec.identity.record_id
        if rid in done:
            continue
        t0 = time.time()
        outcome = gen(rec)
        t_gen = time.time() - t0
        raw = gen.last_raw_text
        t1 = time.time()
        scores = gen.score_options(rec)
        t_score = time.time() - t1
        argmax = max(range(len(scores)), key=lambda i: scores[i])
        row = {
            "record_id": rid,
            "question": rec.question,
            "options": list(rec.options),
            "gold_idx": rec.annotations.get("gold_answer_idx"),
            "raw_text": raw,
            "chosen_answer": outcome.chosen_answer,
            "rationale": outcome.rationale,
            "opened_think": raw.lstrip().startswith("<think>"),
            "unclosed_think": raw.lstrip().startswith("<think>") and "</think>" not in raw,
            "has_marker": "Rationale:" in raw,
            "scores": list(scores),
            "scorer_argmax_option": rec.options[argmax],
            "t_generate_s": round(t_gen, 1),
            "t_score_s": round(t_score, 1),
        }
        with open(OUT, "a") as fh:
            fh.write(json.dumps(row) + "\n")
        has_rat = "yes" if outcome.rationale else "NO"
        print(
            f"{rid}: answer={outcome.chosen_answer!r} rationale={has_rat} "
            f"unclosed={row['unclosed_think']} gen={t_gen:.0f}s score={t_score:.0f}s",
            flush=True,
        )

    rows = [json.loads(line) for line in OUT.read_text().splitlines()]
    parsed = [r for r in rows if r["chosen_answer"] is not None]
    agree = sum(
        1 for r in parsed
        if r["scorer_argmax_option"].strip().lower() == r["chosen_answer"].strip().lower()
    )
    summary = {
        "n": len(rows),
        "parsed_answers": len(parsed),
        "with_rationale": sum(1 for r in rows if r["rationale"]),
        "unclosed_think": sum(1 for r in rows if r["unclosed_think"]),
        "marker_compliance": sum(1 for r in rows if r["has_marker"]),
        "scorer_generation_agreement": round(agree / max(1, len(parsed)), 3),
        "gold_correct_of_parsed": sum(
            1 for r in parsed
            if r["gold_idx"] is not None and r["chosen_answer"] == r["options"][r["gold_idx"]]
        ),
        "mean_t_generate_s": round(sum(r["t_generate_s"] for r in rows) / max(1, len(rows)), 1),
        "mean_t_score_s": round(sum(r["t_score_s"] for r in rows) / max(1, len(rows)), 1),
    }
    OUT.with_suffix(".summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print("SUMMARY:", json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
