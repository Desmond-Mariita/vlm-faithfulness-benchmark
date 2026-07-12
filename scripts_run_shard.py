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
- The registered instrument sanity gate (prereg-m9-v1: fixed CAL-50 slice,
  parseability >= 0.90, agreement >= 0.60, one-shot per generator-contract
  per environment) must have PASSED before any shard runs: run it with
  ``--run-gate`` once; shards then require the matching gate artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Callable  # noqa: F401  (used in gate signature annotation)

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

GENERATOR_CHOICES = ("qwen", "glm", "glm-thinking", "deepseek", "kimi")


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
    if name == "glm-thinking":
        # Ablation-only lane (prereg-m9-v1): outputs never enter corpus labels.
        from vlm_faithfulness_benchmark.generation.glm_generator import GlmGenerator

        return GlmGenerator(image_root=image_root, thinking=True)
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


def wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    r"""Wilson score 95% confidence interval for a binomial proportion.

    LaTeX: \hat{p}_\pm = \frac{\hat{p} + \frac{z^2}{2n} \pm
    z\sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + z^2/n}

    Args:
        successes: Number of successes.
        n: Number of trials (must be positive).
        z: Normal quantile (1.96 for 95%).

    Returns:
        ``(lower, upper)`` bounds in [0, 1].
    """
    assert n > 0 and 0 <= successes <= n, "invalid binomial counts"
    p = successes / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def run_calibration_gate(
    gen: "object", pool: "list[SourceRecord]", log: "Callable[[str], None]"
) -> dict:
    """Run the registered CAL-50 instrument sanity gate (prereg-m9-v1).

    One-shot per generator-contract per environment: generation + option
    scoring on the fixed calibration slice; pass iff parseability >= 0.90
    and scorer-generation agreement over parseable records >= 0.60. The
    Wilson 95% CI of the agreement is recorded alongside the binary result.

    Args:
        gen: The composite generator subject.
        pool: The full registered pool (identity order).
        log: Line logger.

    Returns:
        The gate-result payload (also written by the caller).
    """
    prereg = json.loads((ROOT / "config/prereg_m9_v1.json").read_text())
    gate = prereg["instrument_sanity_gate"]
    slice_records = [pool[i] for i in gate["cal50_positions"]]
    ids = [r.identity.record_id for r in slice_records]
    assert (
        hashlib.sha256("\n".join(ids).encode()).hexdigest() == gate["cal50_sha256"]
    ), "CAL-50 slice diverges from the registered pre-registration"
    parsed = agree = 0
    for rec in slice_records:
        outcome = gen(rec)  # type: ignore[operator]
        if outcome.chosen_answer is None:
            continue
        parsed += 1
        scores = gen.score_options(rec)  # type: ignore[attr-defined]
        argmax = max(range(len(scores)), key=lambda i: scores[i])
        if rec.options[argmax].strip().lower() == outcome.chosen_answer.strip().lower():
            agree += 1
    n = len(slice_records)
    parseability = parsed / n
    agreement = agree / parsed if parsed else 0.0
    lo, hi = wilson_interval(agree, parsed) if parsed else (0.0, 0.0)
    result = {
        "prereg": "prereg-m9-v1",
        "identity": gen.identity().key(),  # type: ignore[attr-defined]
        "n": n,
        "parsed": parsed,
        "parseability": round(parseability, 4),
        "agree": agree,
        "agreement": round(agreement, 4),
        "agreement_wilson95": [round(lo, 4), round(hi, 4)],
        "passed": parseability >= gate["parseability_floor"]
        and agreement >= gate["agreement_floor"],
    }
    log(f"CAL-50 gate: parseability={parseability:.3f} agreement={agreement:.3f} "
        f"CI=[{lo:.3f},{hi:.3f}] passed={result['passed']}")
    return result


def main() -> None:
    """Run the registered gate, or one (generator, shard) slice of the pool."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--generator", choices=GENERATOR_CHOICES, required=True)
    ap.add_argument("--shard-start", type=int)
    ap.add_argument("--shard-end", type=int)
    ap.add_argument("--image-root", type=Path, default=ROOT / "data/coco-pool")
    ap.add_argument(
        "--run-gate",
        action="store_true",
        help="run the one-shot CAL-50 instrument sanity gate for this "
        "generator-contract and write the gate artifact; shards refuse to "
        "run without a passing artifact",
    )
    args = ap.parse_args()

    pool = load_registered_pool(ROOT / "config/pool_manifest_v1.json")
    n_pool = len(pool)
    position = {rec.identity.record_id: i for i, rec in enumerate(pool)}
    run_dir = ROOT / "data/runs"
    run_dir.mkdir(parents=True, exist_ok=True)
    gate_path = run_dir / f"gate-{args.generator}.json"

    if args.run_gate:
        log_path = run_dir / f"gate-{args.generator}.log"

        def glog(msg: str) -> None:
            line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} [gate-{args.generator}] {msg}"
            print(line, flush=True)
            with open(log_path, "a") as fh:
                fh.write(line + "\n")

        glog("loading generator for CAL-50 gate …")
        gen = build_generator(args.generator, args.image_root)
        result = run_calibration_gate(gen, pool, glog)
        gate_path.write_text(json.dumps(result, indent=2) + "\n")
        glog(f"gate artifact written: {gate_path.name}")
        assert result["passed"], (
            "CAL-50 gate FAILED — halt the lane and file an amendment "
            "(prereg-m9-v1: the slice is never redrawn, the floors never retuned)"
        )
        return

    assert args.shard_start is not None and args.shard_end is not None, (
        "provide --shard-start/--shard-end, or --run-gate"
    )
    assert 0 <= args.shard_start < args.shard_end <= n_pool, "bad shard bounds"
    shard = pool[args.shard_start : args.shard_end]

    tag = f"{args.generator}-{args.shard_start:05d}-{args.shard_end:05d}"
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

    # Registered gate (prereg-m9-v1): a shard runs only after this
    # generator-contract passed CAL-50 in THIS environment, and only under
    # the exact identity the gate certified.
    assert gate_path.exists(), (
        f"no gate artifact for {args.generator!r}: run --run-gate first"
    )
    gate_result = json.loads(gate_path.read_text())
    assert gate_result["passed"], "gate artifact records a FAILED gate"
    assert gate_result["identity"] == identity_key, (
        "gate artifact certifies a DIFFERENT composite identity; re-run --run-gate"
    )
    log("CAL-50 gate artifact verified for this identity")

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
