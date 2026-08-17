#!/usr/bin/env python3
"""Capture an immutable, fail-closed environment manifest for one GPU run."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import time
from pathlib import Path

from vlm_faithfulness_benchmark.run_provenance import (
    MANIFEST_SCHEMA,
    capture_runtime,
    file_sha256,
    load_and_verify_tail_contract,
    tree_sha256,
)

ROOT = Path(__file__).resolve().parent


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _git_state() -> dict[str, object]:
    import subprocess

    commit = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    status = subprocess.run(
        ["git", "-C", str(ROOT), "status", "--porcelain=v1"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    return {"commit": commit, "dirty": bool(status), "status": status}


def main() -> None:
    """Parse arguments and atomically create one immutable run manifest."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generator", required=True)
    parser.add_argument("--shard-start", type=int, required=True)
    parser.add_argument("--shard-end", type=int, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--code-commit", required=True)
    parser.add_argument("--gate", type=Path, required=True)
    parser.add_argument("--s02", type=Path, required=True)
    parser.add_argument("--image-root", type=Path, required=True)
    parser.add_argument("--launch-contract", type=Path, required=True)
    parser.add_argument(
        "--run-dir",
        type=Path,
        help="isolated ledger directory; defaults to the parent of --s02",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run_dir = args.run_dir or args.s02.parent
    _require(0 <= args.shard_start < args.shard_end, "bad shard bounds")
    _require(not args.output.exists(), f"refusing to overwrite run manifest {args.output}")

    gate = json.loads(args.gate.read_text())
    _require(gate.get("passed") is True, "gate did not pass")
    identity = gate.get("identity")
    _require(isinstance(identity, str), "gate has no generator identity")
    git_state = _git_state()
    _require(git_state["commit"] == args.code_commit, "declared commit is not checked-out HEAD")
    _, contract_digest = load_and_verify_tail_contract(
        args.launch_contract,
        project_root=ROOT,
        generator=args.generator,
        shard_start=args.shard_start,
        shard_end=args.shard_end,
        generator_identity=identity,
        code_commit=args.code_commit,
        gate_path=args.gate,
        s02_path=args.s02,
        image_root=args.image_root,
    )
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "run_id": args.run_id,
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "shard": {
            "generator": args.generator,
            "start": args.shard_start,
            "end": args.shard_end,
            "tag": f"{args.generator}-{args.shard_start:05d}-{args.shard_end:05d}",
            "generator_identity": identity,
            "command": [
                "python",
                "scripts_run_shard.py",
                "--generator",
                args.generator,
                "--shard-start",
                str(args.shard_start),
                "--shard-end",
                str(args.shard_end),
                "--run-manifest",
                str(args.output.resolve()),
                "--code-commit",
                args.code_commit,
                "--image-root",
                str(args.image_root.resolve()),
                "--gate-artifact",
                str(args.gate.resolve()),
                "--launch-contract",
                str(args.launch_contract.resolve()),
                "--run-dir",
                str(run_dir.resolve()),
            ],
        },
        "runtime": capture_runtime(),
        "code": {"declared_commit": args.code_commit, "cloud_git_state": git_state},
        "launch_contract": {
            "path": str(args.launch_contract.resolve()),
            "sha256": contract_digest,
        },
        "artifacts": {
            "driver_sha256": file_sha256(ROOT / "scripts_run_shard.py"),
            "source_tree_sha256": tree_sha256(ROOT / "src"),
            "config_tree_sha256": tree_sha256(ROOT / "config"),
            "aokvqa_tree_sha256": tree_sha256(ROOT / "data/aokvqa"),
            "gate_path": str(args.gate.resolve()),
            "gate_sha256": file_sha256(args.gate),
            "s02_ledger_path": str(args.s02.resolve()),
            "s02_ledger_sha256": file_sha256(args.s02),
            "image_root_path": str(args.image_root.resolve()),
            "image_root_tree_sha256": tree_sha256(args.image_root),
        },
        "deterministic_scope": {
            "on_stack": True,
            "cross_stack": False,
            "statement": (
                "Greedy GLM observations are claimed reproducible only on the exact pinned "
                "runtime/GPU class in this manifest. Off-stack numeric and threshold drift is "
                "measured release evidence, not deterministic equivalence."
            ),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    descriptor, temporary = tempfile.mkstemp(prefix=f".{args.output.name}.", dir=args.output.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o444)
        os.link(temporary, args.output)
        directory_fd = os.open(args.output.parent, os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        Path(temporary).unlink(missing_ok=True)
    print(f"run manifest: {args.output}")
    print(f"sha256: {file_sha256(args.output)}")


if __name__ == "__main__":
    main()
