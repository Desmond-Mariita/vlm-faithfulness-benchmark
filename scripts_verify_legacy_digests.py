#!/usr/bin/env python3
"""Re-derive missing observation baseline digests into an immutable sidecar.

This is deliberately a post-hoc verification artifact.  It never edits an
append-only observation ledger and never claims that the historical consumer
performed DM-Q1 verification before use.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable

from vlm_faithfulness_benchmark.generation.digest import baseline_digest
from vlm_faithfulness_benchmark.run_provenance import file_sha256

SIDECAR_SCHEMA = "vlm-faithfulness-legacy-baseline-verification-v1"
MANIFEST_SCHEMA = "vlm-faithfulness-legacy-baseline-verification-manifest-v1"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _complete_lines(path: Path) -> Iterable[tuple[int, dict[str, Any]]]:
    raw = path.read_bytes()
    _require(not raw or raw.endswith(b"\n"), f"{path} has an incomplete final line")
    for index, line in enumerate(raw.splitlines()):
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"bad JSON at {path}:{index + 1}") from error
        _require(isinstance(row, dict), f"non-object row at {path}:{index + 1}")
        yield index, row


def _instance_from_key(key: str, suffix: str) -> tuple[str, dict[str, Any]]:
    _require(key.endswith(suffix), f"key {key!r} does not end with {suffix!r}")
    instance_key = key.removesuffix(suffix)
    instance = json.loads(instance_key)
    _require(
        isinstance(instance, dict) and isinstance(instance.get("source"), dict),
        f"ledger key has no source identity: {key!r}",
    )
    return instance_key, instance


def _write_new(path: Path, payload: bytes) -> None:
    _require(not path.exists(), f"refusing to overwrite evidence artifact {path}")
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


def _ranges(indices: list[int]) -> list[list[int]]:
    if not indices:
        return []
    out: list[list[int]] = []
    start = previous = indices[0]
    for value in indices[1:]:
        if value != previous + 1:
            out.append([start, previous + 1])
            start = value
        previous = value
    out.append([start, previous + 1])
    return out


def main() -> None:
    """Verify every digest-missing observation and write immutable evidence."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--s02", type=Path, required=True)
    parser.add_argument("--obs", type=Path, required=True)
    parser.add_argument("--expected-missing", type=int, required=True)
    parser.add_argument("--expected-s02-sha256", required=True)
    parser.add_argument("--expected-s02-rows", type=int, required=True)
    parser.add_argument("--expected-obs-sha256", required=True)
    parser.add_argument("--expected-obs-rows", type=int, required=True)
    parser.add_argument("--expected-generator-identity", required=True)
    parser.add_argument(
        "--expected-missing-range",
        required=True,
        help="exact half-open missing-digest range formatted START:END",
    )
    parser.add_argument("--sidecar", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    _require(args.sidecar != args.manifest, "sidecar and manifest paths must differ")
    try:
        missing_start, missing_end = (
            int(value) for value in args.expected_missing_range.split(":", 1)
        )
    except (ValueError, TypeError) as error:
        raise RuntimeError("--expected-missing-range must be START:END") from error
    _require(
        0 <= missing_start <= missing_end <= args.expected_obs_rows,
        "bad expected missing range",
    )

    s02_hash = file_sha256(args.s02)
    obs_hash = file_sha256(args.obs)
    _require(s02_hash == args.expected_s02_sha256, "unexpected S02 input hash")
    _require(obs_hash == args.expected_obs_sha256, "unexpected observation input hash")

    s02_by_instance: dict[str, dict[str, Any]] = {}
    for line_index, row in _complete_lines(args.s02):
        key = row.get("key")
        _require(isinstance(key, str), f"S02 row {line_index + 1} has no key")
        instance_key, instance = _instance_from_key(key, "::output_tuple")
        _require(
            json.dumps(instance.get("generator"), sort_keys=True, separators=(",", ":"))
            == args.expected_generator_identity,
            f"unexpected S02 generator identity at line {line_index + 1}",
        )
        _require(instance_key not in s02_by_instance, f"duplicate S02 instance {instance_key}")
        payload = row.get("payload")
        _require(isinstance(payload, dict), f"S02 row {line_index + 1} has no payload")
        output_tuple = payload.get("output_tuple")
        _require(
            isinstance(output_tuple, dict),
            f"S02 row {line_index + 1} has no output tuple",
        )
        computed = baseline_digest(output_tuple)
        _require(
            payload.get("baseline_digest") == computed,
            (f"S02 recorded digest mismatch at line {line_index + 1}"),
        )
        s02_by_instance[instance_key] = payload

    _require(len(s02_by_instance) == args.expected_s02_rows, "unexpected S02 row count")
    obs_seen: set[str] = set()
    missing_indices: list[int] = []
    sidecar_rows: list[dict[str, Any]] = []
    obs_count = 0
    for line_index, row in _complete_lines(args.obs):
        obs_count += 1
        key = row.get("key")
        _require(isinstance(key, str), f"observation row {line_index + 1} has no key")
        instance_key, instance = _instance_from_key(key, "::pilot_obs")
        _require(
            json.dumps(instance.get("generator"), sort_keys=True, separators=(",", ":"))
            == args.expected_generator_identity,
            f"unexpected observation generator identity at line {line_index + 1}",
        )
        _require(instance_key not in obs_seen, f"duplicate observation instance {instance_key}")
        obs_seen.add(instance_key)
        s02 = s02_by_instance.get(instance_key)
        _require(
            s02 is not None,
            f"observation has no matching S02 instance at line {line_index + 1}",
        )
        payload = row.get("payload")
        _require(isinstance(payload, dict), f"observation row {line_index + 1} has no payload")
        _require(
            payload.get("source") == s02.get("source"),
            (f"observation/S02 source mismatch at line {line_index + 1}"),
        )
        recorded = s02["baseline_digest"]
        if "baseline_digest" in payload:
            _require(
                payload["baseline_digest"] == recorded,
                (f"observation/S02 digest mismatch at line {line_index + 1}"),
            )
            continue
        missing_indices.append(line_index)
        sidecar_rows.append(
            {
                "schema": SIDECAR_SCHEMA,
                "obs_line_index": line_index,
                "record_id": instance["source"]["record_id"],
                "instance_key": instance_key,
                "baseline_digest": recorded,
                "s02_ledger_sha256": s02_hash,
                "verification": "post-hoc-rederived-from-designated-s02",
                "historical_consumer_verification": "not-recorded",
            }
        )

    _require(obs_count == args.expected_obs_rows, "unexpected observation row count")
    _require(
        len(sidecar_rows) == args.expected_missing,
        (f"expected {args.expected_missing} missing digests, found {len(sidecar_rows)}"),
    )
    _require(
        _ranges(missing_indices) == [[missing_start, missing_end]],
        f"missing digest positions {_ranges(missing_indices)} do not match the declared range",
    )
    sidecar_bytes = b"".join(
        (json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        for row in sidecar_rows
    )
    _write_new(args.sidecar, sidecar_bytes)
    sidecar_hash = file_sha256(args.sidecar)
    manifest = {
        "schema": MANIFEST_SCHEMA,
        "inputs": {
            "s02": {
                "artifact_name": args.s02.name,
                "sha256": s02_hash,
                "rows": len(s02_by_instance),
            },
            "obs": {
                "artifact_name": args.obs.name,
                "sha256": obs_hash,
                "rows": obs_count,
            },
        },
        "result": {
            "sidecar_artifact_name": args.sidecar.name,
            "sha256": sidecar_hash,
            "verified_legacy_rows": len(sidecar_rows),
            "missing_digest_index_ranges": _ranges(missing_indices),
        },
        "claim_boundary": {
            "proves": (
                "Each listed observation instance resolves to the designated S02 tuple whose "
                "recorded digest was independently re-derived from its tuple content."
            ),
            "does_not_prove": (
                "The historical observation consumer performed or recorded DM-Q1 verification "
                "before consuming the tuple. Acceptance requires an explicit legacy disposition."
            ),
            "observation_ledger_modified": False,
        },
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    _write_new(args.manifest, manifest_bytes)
    print(f"verified legacy rows: {len(sidecar_rows)}")
    print(f"missing index ranges: {_ranges(missing_indices)}")
    print(f"sidecar sha256: {sidecar_hash}")
    print(f"manifest sha256: {file_sha256(args.manifest)}")


if __name__ == "__main__":
    main()
