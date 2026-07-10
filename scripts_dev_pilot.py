"""Pilot run driver (V1-045): S02 baselines + observation phase, resumable.

Interrupt at ANY time; rerun resumes from the ledgers. Progress tails to
data/runs/pilot-progress.log.
"""
import json
import time
from pathlib import Path

import numpy as np
from PIL import Image as PILImage

from vlm_faithfulness_benchmark.gating.gates import load_pattern_registry
from vlm_faithfulness_benchmark.gating.pilot import PilotIO, run_pilot_observation
from vlm_faithfulness_benchmark.gating.regimes import wrong_image_partner_index
from vlm_faithfulness_benchmark.generation.harness import run_s02
from vlm_faithfulness_benchmark.generation.qwen_generator import QwenGenerator
from vlm_faithfulness_benchmark.generation.identity import InstanceId
from vlm_faithfulness_benchmark.ingestion.aokvqa import SourceRecord, normalize_aokvqa
from vlm_faithfulness_benchmark.run_ledger import RunLedger

ROOT = Path(__file__).resolve().parent
IMG_DIR = ROOT / "data/coco-pilot"
LOG = ROOT / "data/runs/pilot-progress.log"
PILOT_N = 500


def log(msg: str) -> None:
    line = f"{time.strftime('%H:%M:%S')} {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a") as fh:
        fh.write(line + "\n")


# --- sample: first PILOT_N valid records, identity-sorted ---
raw = json.load(open(ROOT / "data/aokvqa/aokvqa_v1p0_val.json"))
raw.sort(key=lambda r: str(r.get("question_id")))
records: list[SourceRecord] = []
for r in raw:
    rec = normalize_aokvqa(r)
    if isinstance(rec, SourceRecord):
        records.append(rec)
    if len(records) == PILOT_N:
        break
assert len(records) == PILOT_N
position = {rec.identity.record_id: i for i, rec in enumerate(records)}

def image_path(rec: SourceRecord) -> Path:
    return IMG_DIR / f"{int(rec.image_ref.removeprefix('coco/')):012d}.jpg"

missing = [r for r in records if not image_path(r).exists()]
assert not missing, f"{len(missing)} pilot images missing; run the image fetch first"

log(f"pilot sample: {PILOT_N} records; loading generator …")
gen = QwenGenerator(image_root=IMG_DIR)
gen_id = gen.identity()
log(f"generator: {gen_id.key()}")

# --- phase 1: S02 baselines ---
s02_ledger = RunLedger(ROOT / "data/runs/pilot-s02.jsonl")
t0 = time.time()
r1 = run_s02(records, gen, gen_id, s02_ledger,
             on_progress=lambda m: log(f"s02 {m[:60]}"))
log(f"phase1 s02: {r1} in {time.time()-t0:.0f}s")

s02_payloads = {k.removesuffix("::output_tuple"): s02_ledger.payload(k)
                for k in s02_ledger.keys()}

# --- phase 2: observation ---
def load_image(rec: SourceRecord) -> np.ndarray:
    return np.asarray(PILImage.open(image_path(rec)).convert("RGB"), dtype=np.uint8)

def load_partner(rec: SourceRecord) -> np.ndarray:
    partner = records[wrong_image_partner_index(position[rec.identity.record_id], PILOT_N)]
    return load_image(partner)

io = PilotIO(
    load_image=load_image,
    load_partner_image=load_partner,
    score_options=lambda rec, img: gen.score_options(rec, image_override=img),
    generate=lambda rec, img: gen.generate_on(rec, img),
    registry=load_pattern_registry(ROOT / "config/p2_patterns_v1.txt"),
    declared_scope=frozenset({"aokvqa"}),
    spatial_qtypes=lambda rec: any(
        w in rec.question.lower() for w in (" left", " right", "left ", "right ")
    ),
    record_index_of=lambda rec: position[rec.identity.record_id],
)
obs_ledger = RunLedger(ROOT / "data/runs/pilot-obs.jsonl")
t1 = time.time()
done = [0]
def progress(m: str) -> None:
    done[0] += 1
    if done[0] % 10 == 0:
        rate = (time.time() - t1) / done[0]
        log(f"obs {done[0]} committed ({rate:.0f}s/record)")
r2 = run_pilot_observation(
    records, s02_payloads, lambda rec: InstanceId(gen_id, rec.identity), io, obs_ledger,
    on_progress=progress,
)
log(f"phase2 obs: {r2} in {(time.time()-t1)/3600:.2f}h")
s02_ledger.close(); obs_ledger.close()
log("PILOT OBSERVATION COMPLETE")
