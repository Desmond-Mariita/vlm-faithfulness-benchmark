"""Smoke run: S02 over 10 A-OKVQA val records (resumable; minimal).

Run: .../python scripts_dev_smoke_s02.py
Interrupt at ANY time; rerun resumes, skipping committed records.
"""
import json
import time
from pathlib import Path

from vlm_faithfulness_benchmark.generation.harness import run_s02
from vlm_faithfulness_benchmark.generation.qwen_generator import QwenGenerator
from vlm_faithfulness_benchmark.ingestion.aokvqa import SourceRecord, normalize_aokvqa
from vlm_faithfulness_benchmark.run_ledger import RunLedger

ROOT = Path(__file__).resolve().parent
records: list[SourceRecord] = []
for raw in json.load(open(ROOT / "data/aokvqa/aokvqa_v1p0_val.json"))[:10]:
    rec = normalize_aokvqa(raw)
    assert isinstance(rec, SourceRecord), f"smoke sample excluded: {rec}"
    records.append(rec)

print(f"[smoke] {len(records)} records; loading generator …", flush=True)
t0 = time.time()
gen = QwenGenerator(image_root=ROOT / "data/coco-smoke")
print(f"[smoke] model loaded in {time.time()-t0:.0f}s; identity: {gen.identity().key()}", flush=True)

ledger = RunLedger(ROOT / "data/runs/smoke-s02.jsonl")
t1 = time.time()
result = run_s02(records, gen, gen.identity(), ledger, on_progress=lambda m: print("[smoke]", m, flush=True))
dt = time.time() - t1
n = max(result["committed"], 1)
print(f"[smoke] done: {result} in {dt:.0f}s ({dt/n:.1f}s/record)", flush=True)
for key in ledger.keys():
    p = ledger.payload(key)
    print(f"  {p['source']}: answer={p['output_tuple']['chosen_answer']!r} "
          f"rationale={'yes' if p['output_tuple']['rationale'] else 'ABSENT'}", flush=True)
ledger.close()
