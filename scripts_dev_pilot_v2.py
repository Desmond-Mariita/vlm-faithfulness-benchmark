"""Pilot v2: scorer-v1.1 validation gate, then observation rerun (fresh ledger)."""
import json
import time
from pathlib import Path

import numpy as np
from PIL import Image as PILImage

from vlm_faithfulness_benchmark.gating.gates import load_pattern_registry
from vlm_faithfulness_benchmark.gating.pilot import PilotIO, run_pilot_observation
from vlm_faithfulness_benchmark.gating.regimes import wrong_image_partner_index
from vlm_faithfulness_benchmark.generation.qwen_generator import QwenGenerator
from vlm_faithfulness_benchmark.generation.identity import InstanceId
from vlm_faithfulness_benchmark.ingestion.aokvqa import SourceRecord, normalize_aokvqa
from vlm_faithfulness_benchmark.run_ledger import RunLedger

ROOT = Path(__file__).resolve().parent
IMG_DIR = ROOT / "data/coco-pilot"
LOG = ROOT / "data/runs/pilot-progress.log"
PILOT_N = 500
AGREEMENT_GATE = 0.8

def log(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    with open(LOG, "a") as fh:
        fh.write(line + "\n")

raw = json.load(open(ROOT / "data/aokvqa/aokvqa_v1p0_val.json"))
raw.sort(key=lambda r: str(r.get("question_id")))
records: list[SourceRecord] = []
for r in raw:
    rec = normalize_aokvqa(r)
    if isinstance(rec, SourceRecord):
        records.append(rec)
    if len(records) == PILOT_N:
        break
position = {rec.identity.record_id: i for i, rec in enumerate(records)}

log("v2: loading generator (scorer v1.1) …")
gen = QwenGenerator(image_root=IMG_DIR)
gen_id = gen.identity()
log(f"v2 generator: {gen_id.key()}")

# --- validation gate ---
agreement = gen.scorer_generation_agreement(records[:20])
log(f"VALIDATION: scorer-vs-generation agreement on 20 records = {agreement:.2f}")
assert agreement >= AGREEMENT_GATE, (
    f"instrument gate FAILED ({agreement:.2f} < {AGREEMENT_GATE}); rerun aborted"
)
log("validation gate PASSED — starting observation rerun")

# --- observation rerun (fresh ledger; S02 baselines reused) ---
s02_ledger = RunLedger(ROOT / "data/runs/pilot-s02.jsonl")
s02_payloads = {k.removesuffix("::output_tuple"): s02_ledger.payload(k)
                for k in s02_ledger.keys()}

def image_path(rec: SourceRecord) -> Path:
    return IMG_DIR / f"{int(rec.image_ref.removeprefix('coco/')):012d}.jpg"

def load_image(rec: SourceRecord) -> np.ndarray:
    return np.asarray(PILImage.open(image_path(rec)).convert("RGB"), dtype=np.uint8)

io = PilotIO(
    load_image=load_image,
    load_partner_image=lambda rec: load_image(
        records[wrong_image_partner_index(position[rec.identity.record_id], PILOT_N)]
    ),
    score_options=lambda rec, img: gen.score_options(rec, image_override=img),
    generate=lambda rec, img: gen.generate_on(rec, img),
    registry=load_pattern_registry(ROOT / "config/p2_patterns_v1.txt"),
    declared_scope=frozenset({"aokvqa"}),
    spatial_qtypes=lambda rec: any(
        w in rec.question.lower() for w in (" left", " right", "left ", "right ")
    ),
    record_index_of=lambda rec: position[rec.identity.record_id],
)
obs_ledger = RunLedger(ROOT / "data/runs/pilot-obs-v2.jsonl")
t1 = time.time()
done = [0]
def progress(m: str) -> None:
    done[0] += 1
    if done[0] % 25 == 0:
        log(f"obs-v2 {done[0]} committed ({(time.time()-t1)/done[0]:.0f}s/record)")
r2 = run_pilot_observation(
    records, s02_payloads, lambda rec: InstanceId(gen_id, rec.identity), io, obs_ledger,
    on_progress=progress,
)
log(f"obs-v2: {r2} in {(time.time()-t1)/3600:.2f}h")
s02_ledger.close(); obs_ledger.close()
log("PILOT V2 OBSERVATION COMPLETE")
