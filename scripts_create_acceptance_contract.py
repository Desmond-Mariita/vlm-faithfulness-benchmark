#!/usr/bin/env python3
"""Create one immutable, environment-bound M9 GLM reproducibility-probe contract."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from vlm_faithfulness_benchmark.run_provenance import (
    ACCEPTANCE_CONTRACT_SCHEMA,
    M9_ACCEPTANCE_LEGS,
    M9_ACCEPTANCE_RANGES,
    M9_CAL50_SHA256,
    M9_GLM_IDENTITY,
    M9_IMAGE_ROOT_TREE_SHA256,
    M9_POOL_MANIFEST_SHA256,
    M9_PREREG_SHA256,
    M9_S02_SHA256,
    capture_runtime,
    file_sha256,
    gate_environment_fingerprint,
    tree_sha256,
    verify_reviewed_git_content,
)

ROOT = Path(__file__).resolve().parent


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _write_new(path: Path, payload: bytes) -> None:
    _require(not path.exists(), f"refusing to overwrite acceptance contract {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o444)
        os.link(temporary, path)
        directory_fd = os.open(path.parent, os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        Path(temporary).unlink(missing_ok=True)


def main() -> None:
    """Validate one native stack and create a contract for exactly one probe leg."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acceptance-leg", choices=sorted(M9_ACCEPTANCE_LEGS), required=True)
    parser.add_argument("--code-commit", required=True)
    parser.add_argument("--gate", type=Path, required=True)
    parser.add_argument("--s02", type=Path, required=True)
    parser.add_argument("--image-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    verify_reviewed_git_content(ROOT, args.code_commit)
    runtime = capture_runtime()
    expected_gpu = (
        "NVIDIA GeForce RTX 5090"
        if args.acceptance_leg.startswith("5090-")
        else "NVIDIA GeForce RTX 3090"
    )
    _require(runtime["gpu"]["name"] == expected_gpu, "acceptance leg uses the wrong GPU class")
    environment_fingerprint = gate_environment_fingerprint(runtime)
    gate = json.loads(args.gate.read_text())
    _require(gate.get("passed") is True, "CAL-50 gate did not pass")
    _require(
        gate.get("environment_fingerprint") == environment_fingerprint,
        "CAL-50 gate is not bound to this native stack",
    )
    identity = gate.get("identity")
    _require(identity == M9_GLM_IDENTITY, "CAL-50 gate has the wrong GLM identity")
    _require(file_sha256(args.s02) == M9_S02_SHA256, "wrong canonical S02 bytes")
    _require(
        file_sha256(ROOT / "config/pool_manifest_v1.json") == M9_POOL_MANIFEST_SHA256,
        "registered pool manifest changed",
    )
    _require(
        file_sha256(ROOT / "config/prereg_m9_v1.json") == M9_PREREG_SHA256,
        "registered preregistration changed",
    )
    image_root_tree_sha256 = tree_sha256(args.image_root)
    _require(
        image_root_tree_sha256 == M9_IMAGE_ROOT_TREE_SHA256,
        "image root is not the registered 17,662-image pool",
    )
    contract = {
        "schema": ACCEPTANCE_CONTRACT_SCHEMA,
        "profile": "m9-glm-repro-acceptance-v1",
        "acceptance_leg": args.acceptance_leg,
        "authorized_shards": M9_ACCEPTANCE_RANGES,
        "cal50_sha256": M9_CAL50_SHA256,
        "generator": "glm",
        "generator_identity": identity,
        "code_commit": args.code_commit,
        "canonical_s02_sha256": M9_S02_SHA256,
        "pool_manifest_sha256": M9_POOL_MANIFEST_SHA256,
        "prereg_sha256": M9_PREREG_SHA256,
        "environment_fingerprint": environment_fingerprint,
        "driver_sha256": file_sha256(ROOT / "scripts_run_shard.py"),
        "source_tree_sha256": tree_sha256(ROOT / "src"),
        "config_tree_sha256": tree_sha256(ROOT / "config"),
        "aokvqa_tree_sha256": tree_sha256(ROOT / "data/aokvqa"),
        "gate_sha256": file_sha256(args.gate),
        "s02_ledger_sha256": file_sha256(args.s02),
        "image_root_tree_sha256": image_root_tree_sha256,
        "runtime_class": {
            "platform": runtime["platform"],
            "python": runtime["python"],
            "numpy": runtime["numpy"],
            "pillow": runtime["pillow"],
            "torch": runtime["torch"],
            "torch_cuda": runtime["torch_cuda"],
            "cudnn": runtime["cudnn"],
            "transformers": runtime["transformers"],
            "gpu_name": runtime["gpu"]["name"],
            "compute_capability": runtime["gpu"]["compute_capability"],
            "driver": runtime["gpu"]["driver"],
        },
    }
    _write_new(args.output, (json.dumps(contract, indent=2, sort_keys=True) + "\n").encode())
    print(f"acceptance contract: {args.output}")
    print(f"sha256: {file_sha256(args.output)}")


if __name__ == "__main__":
    main()
