"""Kimi-VL-A3B 8-bit PLUMBING test (3090) — code-path exercise, NOT readings.

Purpose (M9 disposition): first execution of the Kimi adapter's documented
two-step processor path, the pixel_values invariant, and the
forced-reply-span scorer against the real template. The quantized subject
is a different composite identity; nothing here is a corpus reading or a
calibration act. Requires ``ALLOW_PLUMBING_TEST_MODE=1`` (the code-enforced
gate) — this driver sets it explicitly and prints the poisoned identity as
evidence the gate + recording work.

Usage::

    python scripts_dev_plumb_kimi.py [--n 2] [--offset 1000]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

os.environ["ALLOW_PLUMBING_TEST_MODE"] = "1"

from scripts_run_shard import load_registered_pool  # noqa: E402

from vlm_faithfulness_benchmark.generation.kimi_generator import KimiGenerator  # noqa: E402

OUT = ROOT / "data/runs/rehearsal-kimi-plumbing.json"


def main() -> None:
    """Exercise generate + score once each on a couple of pool records."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--offset", type=int, default=1000)
    args = ap.parse_args()

    pool = load_registered_pool(ROOT / "config/pool_manifest_v1.json")
    records = pool[args.offset : args.offset + args.n]

    t_load = time.time()
    gen = KimiGenerator(image_root=ROOT / "data/coco-pool", load_in_8bit=True)
    identity = gen.identity().key()
    print(f"loaded in {time.time() - t_load:.0f}s | identity: {identity}", flush=True)
    assert "int8-plumbing-test-only" in identity, "identity must record the quantized dtype"

    results = []
    for rec in records:
        t0 = time.time()
        outcome = gen(rec)
        t_gen = time.time() - t0
        t1 = time.time()
        scores = gen.score_options(rec)
        t_score = time.time() - t1
        argmax = max(range(len(scores)), key=lambda i: scores[i])
        results.append(
            {
                "record_id": rec.identity.record_id,
                "question": rec.question,
                "options": list(rec.options),
                "raw_text": gen.last_raw_text,
                "chosen_answer": outcome.chosen_answer,
                "rationale": outcome.rationale,
                "scores": list(scores),
                "scorer_argmax_option": rec.options[argmax],
                "t_generate_s": round(t_gen, 1),
                "t_score_s": round(t_score, 1),
            }
        )
        print(
            f"{rec.identity.record_id}: answer={outcome.chosen_answer!r} "
            f"gen={t_gen:.0f}s score={t_score:.0f}s",
            flush=True,
        )

    OUT.write_text(json.dumps({"identity": identity, "records": results}, indent=2) + "\n")
    print("PLUMBING TEST COMPLETE — two-step path, pixel_values invariant, "
          "span-diff scorer all executed", flush=True)


if __name__ == "__main__":
    main()
