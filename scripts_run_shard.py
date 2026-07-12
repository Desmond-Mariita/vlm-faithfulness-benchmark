"""Sharded mass-run driver for the M9 corpus construction runs.

One invocation = one (generator, shard) slice of the registered pool
(``config/pool_manifest_v1.json``). Everything is resume-capable at record
granularity: re-running the same invocation after a kill/power-cut skips
committed records (RunLedger record-atomic resume), so cloud instances can
be preempted safely.

Usage::

    python scripts_run_shard.py --generator glm --shard-start 0 --shard-end 2000
    python scripts_run_shard.py --generator qwen --shard-start 2000 --shard-end 4000 \
        --image-root data/coco-pool

Guards (halt, never degrade):
- The loaded pool must hash-match the registered manifest (pre-registration
  binding: the run consumes exactly the registered pool, in the registered
  order).
- Quantized composite identities are refused — corpus runs are bf16 only.
- The instrument sanity gate (scorer-vs-generation agreement on the shard's
  first records) must clear the floor before any observation is committed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image as PILImage

from vlm_faithfulness_benchmark.gating.gates import load_pattern_registry
from vlm_faithfulness_benchmark.gating.pilot import PilotIO, run_pilot_observation
from vlm_faithfulness_benchmark.gating.regimes import wrong_image_partner_index
from vlm_faithfulness_benchmark.generation.harness import run_s02
from vlm_faithfulness_benchmark.generation.identity import InstanceId
from vlm_faithfulness_benchmark.ingestion.aokvqa import SourceRecord, normalize_aokvqa
from vlm_faithfulness_benchmark.run_ledger import RunLedger

ROOT = Path(__file__).resolve().parent
AGREEMENT_FLOOR = 0.90
VALIDATE_N = 20

GENERATOR_CHOICES = ("qwen", "glm", "deepseek", "kimi")


def build_generator(name: str, image_root: Path) -> "object":
    """Instantiate the named composite generator subject (lazy imports).

    Args:
        name: One of ``qwen``, ``glm``, ``deepseek``, ``kimi``.
        image_root: The pool image directory.

    Returns:
        The generator adapter instance.

    Raises:
        ValueError: If the name is unknown.
    """
    if name == "qwen":
        from vlm_faithfulness_benchmark.generation.qwen_generator import QwenGenerator

        return QwenGenerator(image_root=image_root)
    if name == "glm":
        from vlm_faithfulness_benchmark.generation.glm_generator import GlmGenerator

        return GlmGenerator(image_root=image_root)
    if name == "deepseek":
        from vlm_faithfulness_benchmark.generation.deepseek_generator import (
            DeepseekVL2Generator,
        )

        return DeepseekVL2Generator(image_root=image_root)
    if name == "kimi":
        from vlm_faithfulness_benchmark.generation.kimi_generator import KimiGenerator

        return KimiGenerator(image_root=image_root)
    raise ValueError(f"unknown generator {name!r}")


def load_registered_pool(manifest_path: Path) -> list[SourceRecord]:
    """Load the pool and verify it against the registered manifest.

    Args:
        manifest_path: Path to ``pool_manifest_v1.json``.

    Returns:
        The identity-sorted Source Records.

    Raises:
        AssertionError: If counts or the id-sequence hash diverge from the
            manifest — the run must consume exactly the registered pool.
    """
    manifest = json.loads(manifest_path.read_text())
    records: list[SourceRecord] = []
    n_excluded = 0
    for split_file in ("aokvqa_v1p0_train.json", "aokvqa_v1p0_val.json"):
        for raw in json.load(open(ROOT / "data/aokvqa" / split_file)):
            rec = normalize_aokvqa(raw)
            if isinstance(rec, SourceRecord):
                records.append(rec)
            else:
                n_excluded += 1
    records.sort(key=lambda r: r.identity.record_id)
    assert len(records) == manifest["n_records"], (
        f"pool size {len(records)} != registered {manifest['n_records']}"
    )
    assert n_excluded == manifest["n_ingestion_exclusions"], (
        f"exclusions {n_excluded} != registered {manifest['n_ingestion_exclusions']}"
    )
    digest = hashlib.sha256(
        "\n".join(r.identity.record_id for r in records).encode()
    ).hexdigest()
    assert digest == manifest["sha256_of_record_id_sequence"], (
        "pool id-sequence hash diverges from the registered manifest"
    )
    return records


def main() -> None:
    """Run one (generator, shard) slice of the registered pool."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--generator", choices=GENERATOR_CHOICES, required=True)
    ap.add_argument("--shard-start", type=int, required=True)
    ap.add_argument("--shard-end", type=int, required=True)
    ap.add_argument("--image-root", type=Path, default=ROOT / "data/coco-pool")
    ap.add_argument(
        "--validate-n",
        type=int,
        default=VALIDATE_N,
        help="records for the instrument sanity gate (0 skips ONLY if a prior "
        "shard of this generator already passed on this machine)",
    )
    args = ap.parse_args()

    pool = load_registered_pool(ROOT / "config/pool_manifest_v1.json")
    n_pool = len(pool)
    assert 0 <= args.shard_start < args.shard_end <= n_pool, "bad shard bounds"
    shard = pool[args.shard_start : args.shard_end]
    position = {rec.identity.record_id: i for i, rec in enumerate(pool)}

    tag = f"{args.generator}-{args.shard_start:05d}-{args.shard_end:05d}"
    run_dir = ROOT / "data/runs"
    run_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_dir / f"shard-{tag}.log"

    def log(msg: str) -> None:
        line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} [{tag}] {msg}"
        print(line, flush=True)
        with open(log_path, "a") as fh:
            fh.write(line + "\n")

    log(f"pool verified against manifest ({n_pool} records); shard n={len(shard)}")
    log("loading generator …")
    gen = build_generator(args.generator, args.image_root)
    gen_id = gen.identity()  # type: ignore[attr-defined]
    identity_key = gen_id.key()
    # Corpus runs are bf16-only: a quantized subject is a different composite
    # identity and must never contribute corpus records.
    assert "int8" not in identity_key, (
        f"quantized identity refused for corpus runs: {identity_key}"
    )
    log(f"generator identity: {identity_key}")

    if args.validate_n > 0:
        agreement = gen.scorer_generation_agreement(  # type: ignore[attr-defined]
            shard[: args.validate_n]
        )
        log(f"instrument sanity gate: agreement={agreement:.3f} on {args.validate_n}")
        assert agreement >= AGREEMENT_FLOOR, (
            f"instrument sanity gate FAILED ({agreement:.3f} < {AGREEMENT_FLOOR}); "
            "shard aborted before any observation was committed"
        )
        log("instrument sanity gate PASSED")
    else:
        log("instrument sanity gate SKIPPED by flag (prior shard must have passed)")

    def image_path(rec: SourceRecord) -> Path:
        return args.image_root / f"{int(rec.image_ref.removeprefix('coco/')):012d}.jpg"

    def load_image(rec: SourceRecord) -> np.ndarray:
        return np.asarray(PILImage.open(image_path(rec)).convert("RGB"), dtype=np.uint8)

    def load_partner_image(rec: SourceRecord) -> np.ndarray:
        # Registered derangement: cyclic successor in the FULL pool order —
        # partners may live outside this shard, which is why the whole pool
        # stays loaded.
        partner = pool[wrong_image_partner_index(position[rec.identity.record_id], n_pool)]
        return load_image(partner)

    s02_ledger = RunLedger(run_dir / f"s02-{tag}.jsonl")
    t0 = time.time()
    r1 = run_s02(shard, gen, gen_id, s02_ledger)  # type: ignore[arg-type]
    log(f"s02: {dict(r1)} in {time.time() - t0:.0f}s")
    s02_payloads = {
        k.removesuffix("::output_tuple"): s02_ledger.payload(k) for k in s02_ledger.keys()
    }

    io = PilotIO(
        load_image=load_image,
        load_partner_image=load_partner_image,
        score_options=lambda rec, img: gen.score_options(rec, image_override=img),  # type: ignore[attr-defined]
        generate=lambda rec, img: gen.generate_on(rec, img),  # type: ignore[attr-defined]
        registry=load_pattern_registry(ROOT / "config/p2_patterns_v1.txt"),
        declared_scope=frozenset({"aokvqa"}),
        spatial_qtypes=lambda rec: any(
            w in rec.question.lower() for w in (" left", " right", "left ", "right ")
        ),
        record_index_of=lambda rec: position[rec.identity.record_id],
    )
    obs_ledger = RunLedger(run_dir / f"obs-{tag}.jsonl")
    t1 = time.time()
    done = [0]

    def progress(_: str) -> None:
        done[0] += 1
        if done[0] % 50 == 0:
            pace = (time.time() - t1) / done[0]
            log(f"obs {done[0]}/{len(shard)} committed ({pace:.0f}s/record)")

    make_instance: Callable[[SourceRecord], InstanceId] = lambda rec: InstanceId(  # noqa: E731
        gen_id, rec.identity
    )
    r2 = run_pilot_observation(
        shard, s02_payloads, make_instance, io, obs_ledger, on_progress=progress
    )
    log(f"obs: {dict(r2)} in {(time.time() - t1) / 3600:.2f}h")
    s02_ledger.close()
    obs_ledger.close()
    log("SHARD COMPLETE")


if __name__ == "__main__":
    main()
