#!/usr/bin/env python3
"""Validate and optionally assemble the GLM observation lane from a pinned plan."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from vlm_faithfulness_benchmark.generation.digest import baseline_digest
from vlm_faithfulness_benchmark.run_provenance import (
    M9_5090_ENVIRONMENT_FINGERPRINT,
    M9_IMAGE_ROOT_TREE_SHA256,
    M9_POOL_MANIFEST_SHA256,
    M9_PREREG_SHA256,
    MANIFEST_SCHEMA,
    TAIL_CONTRACT_SCHEMA,
    file_sha256,
    gate_environment_fingerprint,
)

PLAN_SCHEMA = "vlm-faithfulness-glm-merge-plan-v1"
SIDECAR_SCHEMA = "vlm-faithfulness-legacy-baseline-verification-v1"
M9_EXPECTED_RECORDS = 18_194
M9_CANONICAL_S02_SHA256 = "e2f35a869cc874504c4942f30804048ac40de59caaafe8f2c7528262b066408e"
M9_GLM_IDENTITY = (
    '{"decoding":"greedy;beams=1;max_new_tokens=256;enable_thinking=False",'
    '"dtype":"bfloat16","extraction_contract":"aokvqa-mc-glm-v2",'
    '"image_preprocessing":"pil-rgb-native","model":"zai-org/GLM-4.6V-Flash",'
    '"option_scorer":"option-letter-logprob-glm-v1",'
    '"prompt_template":"aokvqa-mc-glm-v2",'
    '"revision":"411bb4d77144a3f03accbf4b780f5acb8b7cde4e"}'
)
M9_LEGACY_END = 4053
M9_SEGMENTS = [
    (0, 3969),
    (3969, 4053),
    (4053, 6154),
    (6154, 7577),
    (7577, 9000),
    (9000, 13600),
    (13600, 18194),
]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _resolve(plan_path: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else plan_path.parent / path


def _read_jsonl(path: Path) -> list[tuple[bytes, dict[str, Any]]]:
    raw = path.read_bytes()
    _require(not raw or raw.endswith(b"\n"), f"{path} has an incomplete final line")
    out = []
    for index, line in enumerate(raw.splitlines(keepends=True), 1):
        _require(line.endswith(b"\n"), f"{path}:{index} has no complete line ending")
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise RuntimeError(f"bad JSON at {path}:{index}") from error
        _require(isinstance(row, dict), f"non-object JSON at {path}:{index}")
        out.append((line, row))
    return out


def _instance(key: object, suffix: str) -> tuple[str, dict[str, Any]]:
    _require(isinstance(key, str) and key.endswith(suffix), f"bad ledger key {key!r}")
    instance_key = key.removesuffix(suffix)
    parsed = json.loads(instance_key)
    _require(
        isinstance(parsed, dict) and isinstance(parsed.get("source"), dict),
        f"ledger key has no source object: {key!r}",
    )
    return instance_key, parsed


def _verify_file_ref(plan_path: Path, reference: dict[str, Any]) -> Path:
    path = _resolve(plan_path, reference["path"])
    _require(path.is_file(), f"missing pinned artifact {path}")
    _require(file_sha256(path) == reference["sha256"], f"hash mismatch for {path}")
    return path


def _verify_provenance_manifest(
    plan_path: Path,
    provenance: dict[str, Any],
    start: int,
    end: int,
    expected_identity: str,
) -> None:
    manifest_path = _verify_file_ref(plan_path, provenance["manifest"])
    manifest = json.loads(manifest_path.read_text())
    _require(isinstance(manifest, dict), f"non-object provenance manifest {manifest_path}")
    scope = manifest.get("deterministic_scope")
    _require(isinstance(scope, dict), f"missing deterministic scope in {manifest_path}")
    _require(
        scope.get("on_stack") is True and scope.get("cross_stack") is False,
        f"invalid deterministic scope in {manifest_path}",
    )
    if provenance["mode"] == "in-row":
        _require(manifest.get("schema") == MANIFEST_SCHEMA, "bad run-manifest schema")
        _require(manifest.get("run_id") == provenance["run_id"], "run_id mismatch")
        shard = manifest.get("shard")
        _require(isinstance(shard, dict), "run manifest has no shard object")
        _require(
            shard.get("start") == start and shard.get("end") == end,
            "run manifest bounds mismatch",
        )
        _require(shard.get("generator_identity") == expected_identity, "identity mismatch")
        _require(
            provenance["run_provenance_digest"] == provenance["manifest"]["sha256"],
            "in-row provenance digest does not bind manifest",
        )
        artifacts = manifest.get("artifacts")
        _require(isinstance(artifacts, dict), "run manifest has no artifacts object")
        for required_pin in (
            "driver_sha256",
            "source_tree_sha256",
            "config_tree_sha256",
            "aokvqa_tree_sha256",
            "gate_sha256",
            "s02_ledger_sha256",
            "image_root_tree_sha256",
        ):
            _require(
                isinstance(artifacts.get(required_pin), str),
                f"run manifest lacks {required_pin}",
            )
        _require(
            artifacts.get("s02_ledger_sha256") == M9_CANONICAL_S02_SHA256,
            "run manifest binds the wrong S02",
        )
        _require(
            artifacts.get("image_root_tree_sha256") == M9_IMAGE_ROOT_TREE_SHA256,
            "run manifest binds the wrong image root",
        )
        runtime = manifest.get("runtime")
        _require(isinstance(runtime, dict), "run manifest has no runtime object")
        _require(
            gate_environment_fingerprint(runtime) == M9_5090_ENVIRONMENT_FINGERPRINT,
            "run manifest is not the registered 5090 environment",
        )
        contract_path = _verify_file_ref(plan_path, provenance["launch_contract"])
        contract = json.loads(contract_path.read_text())
        _require(isinstance(contract, dict), "tail launch contract is not an object")
        _require(contract.get("schema") == TAIL_CONTRACT_SCHEMA, "bad tail contract schema")
        _require(
            provenance["launch_contract"]["sha256"]
            == manifest.get("launch_contract", {}).get("sha256"),
            "run manifest does not bind the supplied tail contract",
        )
        _require(
            contract.get("authorized_shards") == [[6154, 7577], [7577, 9000]],
            "tail contract has wrong authorized ranges",
        )
        _require(
            contract.get("generator_identity") == expected_identity, "contract identity mismatch"
        )
        _require(
            contract.get("canonical_s02_sha256") == M9_CANONICAL_S02_SHA256,
            "tail contract binds wrong S02",
        )
        _require(
            contract.get("pool_manifest_sha256") == M9_POOL_MANIFEST_SHA256,
            "tail contract binds wrong pool manifest",
        )
        _require(
            contract.get("prereg_sha256") == M9_PREREG_SHA256,
            "tail contract binds wrong preregistration",
        )
        _require(
            contract.get("environment_fingerprint") == M9_5090_ENVIRONMENT_FINGERPRINT,
            "tail contract binds wrong environment",
        )
        code = manifest.get("code")
        _require(isinstance(code, dict), "run manifest has no code object")
        _require(
            contract.get("code_commit") == code.get("declared_commit"),
            "tail contract/run manifest code mismatch",
        )
        for field in (
            "driver_sha256",
            "source_tree_sha256",
            "config_tree_sha256",
            "aokvqa_tree_sha256",
            "gate_sha256",
            "s02_ledger_sha256",
            "image_root_tree_sha256",
        ):
            _require(
                contract.get(field) == artifacts.get(field),
                f"tail contract/run manifest {field} mismatch",
            )
    else:
        _require(provenance["mode"] == "external", "unknown provenance mode")
        _require(
            manifest.get("schema") == "vlm-faithfulness-reconstructed-run-provenance-v1",
            "bad reconstructed provenance schema",
        )
        segments = manifest.get("segments")
        _require(isinstance(segments, list), f"external manifest has no segments: {manifest_path}")
        matches = [s for s in segments if s.get("start") == start and s.get("end") == end]
        _require(
            len(matches) == 1,
            (f"external provenance {manifest_path} does not uniquely bind [{start},{end})"),
        )
        generator = manifest.get("generator")
        _require(
            isinstance(generator, dict) and generator.get("identity") == expected_identity,
            "external provenance identity mismatch",
        )
        top_level_pins = manifest.get("installed_content_hashes")
        segment_pins = matches[0]
        _require(
            isinstance(top_level_pins, dict)
            or (
                isinstance(segment_pins.get("benchmark_commit"), str)
                and isinstance(segment_pins.get("driver_sha256"), str)
                and isinstance(segment_pins.get("git_src_tree"), str)
            ),
            f"external provenance has no code-content pins for [{start},{end})",
        )
        host = manifest.get("host")
        _require(isinstance(host, dict), "external provenance has no host object")
        for field in (
            "platform",
            "python",
            "numpy",
            "pillow",
            "torch",
            "torch_cuda",
            "cudnn",
            "transformers",
            "driver",
        ):
            _require(host.get(field) not in (None, ""), f"external host lacks {field}")
        if start >= 9000:
            environment = dict(host)
            environment["gpu"] = {
                "name": matches[0].get("gpu_name"),
                "compute_capability": matches[0].get("compute_capability"),
                "driver": host.get("driver"),
            }
            _require(
                gate_environment_fingerprint(environment) == M9_5090_ENVIRONMENT_FINGERPRINT,
                "existing cloud segment is not the registered 5090 environment",
            )
        else:
            _require(host.get("gpu_name") == "NVIDIA GeForce RTX 3090", "wrong local GPU")
            _require(host.get("compute_capability") == "8.6", "wrong local GPU capability")
        canonical_hash = None
        if isinstance(top_level_pins, dict):
            canonical_hash = top_level_pins.get("canonical_s02_sha256")
        if canonical_hash is None and isinstance(manifest.get("evidence"), dict):
            canonical_hash = manifest["evidence"].get("canonical_s02_sha256")
        _require(canonical_hash == M9_CANONICAL_S02_SHA256, "external provenance binds wrong S02")


def _write_new(path: Path, payload: bytes) -> None:
    _require(not path.exists(), f"refusing to overwrite {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.link(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def main() -> None:
    """Validate coverage, identity, baseline binding, and environment provenance."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--merged-output", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    plan = json.loads(args.plan.read_text())
    _require(plan.get("schema") == PLAN_SCHEMA, "unexpected merge-plan schema")
    expected = plan["expected_records"]
    _require(expected == M9_EXPECTED_RECORDS, "plan does not bind the M9 record count")
    expected_identity = plan["generator_identity"]
    _require(expected_identity == M9_GLM_IDENTITY, "plan does not bind the registered GLM identity")

    s02_path = _verify_file_ref(args.plan, plan["canonical_s02"])
    _require(
        plan["canonical_s02"]["sha256"] == M9_CANONICAL_S02_SHA256,
        "plan does not bind the canonical registered GLM S02",
    )
    s02_rows = _read_jsonl(s02_path)
    _require(len(s02_rows) == expected, f"S02 count {len(s02_rows)} != {expected}")
    position: dict[str, int] = {}
    s02_by_instance: dict[str, dict[str, Any]] = {}
    for index, (_, row) in enumerate(s02_rows):
        instance_key, instance = _instance(row.get("key"), "::output_tuple")
        _require(
            json.dumps(instance["generator"], sort_keys=True, separators=(",", ":"))
            == expected_identity,
            f"S02 identity mismatch at position {index}",
        )
        record_id = instance["source"]["record_id"]
        _require(record_id not in position, f"duplicate S02 record_id {record_id}")
        position[record_id] = index
        payload = row["payload"]
        _require(
            payload["source"]
            == json.dumps(instance["source"], sort_keys=True, separators=(",", ":")),
            f"S02 source mismatch at position {index}",
        )
        _require(isinstance(payload.get("baseline_digest"), str), "S02 digest missing")
        output_tuple = payload.get("output_tuple")
        _require(isinstance(output_tuple, dict), "S02 output_tuple missing")
        _require(
            payload["baseline_digest"] == baseline_digest(output_tuple),
            (f"S02 digest does not re-derive at position {index}"),
        )
        s02_by_instance[instance_key] = payload

    legacy_artifacts = [
        artifact
        for artifact in plan["observation_artifacts"]
        if any(segment.get("start") == 0 for segment in artifact.get("segments", []))
        and any(segment.get("end", 0) >= M9_LEGACY_END for segment in artifact.get("segments", []))
    ]
    _require(
        len(legacy_artifacts) == 1, "legacy population does not resolve to one observation artifact"
    )
    legacy_obs_sha256 = legacy_artifacts[0]["sha256"]
    legacy_digest: dict[str, str] = {}
    legacy_positions: set[int] = set()
    for reference in plan.get("legacy_digest_sidecars", []):
        path = _verify_file_ref(args.plan, reference)
        manifest_reference = reference.get("verification_manifest")
        _require(
            isinstance(manifest_reference, dict),
            "legacy sidecar has no deterministic verification manifest",
        )
        verification_manifest_path = _verify_file_ref(args.plan, manifest_reference)
        verification_manifest = json.loads(verification_manifest_path.read_text())
        _require(
            verification_manifest.get("schema")
            == "vlm-faithfulness-legacy-baseline-verification-manifest-v1",
            "bad legacy verification manifest schema",
        )
        _require(
            verification_manifest.get("inputs", {}).get("s02", {}).get("sha256")
            == M9_CANONICAL_S02_SHA256,
            "legacy verification manifest binds wrong S02",
        )
        _require(
            verification_manifest.get("inputs", {}).get("obs", {}).get("sha256")
            == legacy_obs_sha256,
            "legacy verification manifest binds wrong observation ledger",
        )
        _require(
            verification_manifest.get("result", {}).get("sha256") == reference["sha256"],
            "legacy verification manifest does not bind the supplied sidecar",
        )
        _require(
            verification_manifest.get("result", {}).get("verified_legacy_rows") == M9_LEGACY_END,
            "legacy verification manifest has wrong population",
        )
        claim = verification_manifest.get("claim_boundary")
        _require(isinstance(claim, dict), "legacy verification manifest has no claim boundary")
        _require(
            claim.get("observation_ledger_modified") is False
            and "historical observation consumer" in claim.get("does_not_prove", ""),
            "legacy verification manifest overclaims historical DM-Q1",
        )
        for _, row in _read_jsonl(path):
            instance_key = row["instance_key"]
            _require(row.get("schema") == SIDECAR_SCHEMA, "bad legacy sidecar schema")
            _require(
                row.get("historical_consumer_verification") == "not-recorded",
                "legacy sidecar misstates historical verification",
            )
            _require(
                row.get("verification") == "post-hoc-rederived-from-designated-s02",
                "bad legacy sidecar verification claim",
            )
            _require(instance_key not in legacy_digest, f"duplicate legacy sidecar {instance_key}")
            _require(
                row["s02_ledger_sha256"] == plan["canonical_s02"]["sha256"],
                "legacy sidecar binds a different S02",
            )
            record_id = row.get("record_id")
            _require(record_id in position, "legacy sidecar has unknown record_id")
            legacy_position = position[record_id]
            _require(
                row.get("obs_line_index") == legacy_position,
                "legacy sidecar line index does not match canonical position",
            )
            legacy_positions.add(legacy_position)
            legacy_digest[instance_key] = row["baseline_digest"]
    _require(
        len(legacy_digest) == M9_LEGACY_END,
        f"GLM legacy sidecar must contain exactly {M9_LEGACY_END:,} rows",
    )
    _require(
        legacy_positions == set(range(M9_LEGACY_END)),
        f"GLM legacy sidecar must bind exactly canonical positions [0,{M9_LEGACY_END})",
    )

    merged: dict[int, bytes] = {}
    segment_counts: dict[str, int] = {}
    declared_ranges: list[tuple[int, int]] = []
    for artifact in plan["observation_artifacts"]:
        obs_path = _verify_file_ref(args.plan, artifact)
        segments = artifact["segments"]
        _require(bool(segments), f"{obs_path} has no declared provenance segments")
        for segment in segments:
            start, end = segment["start"], segment["end"]
            _require(0 <= start < end <= expected, f"bad segment [{start},{end})")
            declared_ranges.append((start, end))
            label = f"{obs_path.name}[{start},{end})"
            segment_counts[label] = 0
            provenance = segment["provenance"]
            if (start, end) in {(6154, 7577), (7577, 9000)}:
                _require(
                    provenance["mode"] == "in-row",
                    ("new GLM tail segments require in-row run provenance"),
                )
            _verify_provenance_manifest(args.plan, provenance, start, end, expected_identity)
            if provenance["mode"] == "in-row":
                _require(isinstance(provenance["run_id"], str), "missing run_id")
                _require(
                    isinstance(provenance["run_provenance_digest"], str),
                    "missing run provenance digest",
                )

    _require(
        declared_ranges == M9_SEGMENTS,
        "merge plan does not declare the reviewed seven-segment GLM provenance layout",
    )

    for artifact in plan["observation_artifacts"]:
        obs_path = _verify_file_ref(args.plan, artifact)
        segments = artifact["segments"]
        for raw, row in _read_jsonl(obs_path):
            instance_key, instance = _instance(row.get("key"), "::pilot_obs")
            _require(
                json.dumps(instance["generator"], sort_keys=True, separators=(",", ":"))
                == expected_identity,
                "observation generator identity mismatch",
            )
            record_id = instance["source"]["record_id"]
            _require(record_id in position, f"unknown observation record_id {record_id}")
            index = position[record_id]
            matching = [s for s in segments if s["start"] <= index < s["end"]]
            _require(
                len(matching) == 1,
                (f"record {record_id} at position {index} resolves to {len(matching)} segments"),
            )
            segment = matching[0]
            label = f"{obs_path.name}[{segment['start']},{segment['end']})"
            segment_counts[label] += 1
            payload = row["payload"]
            s02 = s02_by_instance.get(instance_key)
            _require(s02 is not None, f"observation has no matching S02 for {record_id}")
            _require(payload["source"] == s02["source"], f"source mismatch for {record_id}")
            observed_digest = payload.get("baseline_digest", legacy_digest.get(instance_key))
            _require(
                observed_digest == s02["baseline_digest"],
                (f"baseline digest missing/mismatched for {record_id}"),
            )
            gates = payload.get("gates")
            _require(isinstance(gates, list) and bool(gates), f"missing gate route for {record_id}")
            _require(len(gates) <= 3, f"too many gate entries for {record_id}")
            expected_gate_names = ["P1", "P2", "P3"]
            for gate_index, gate in enumerate(gates):
                _require(
                    isinstance(gate, list)
                    and len(gate) == 3
                    and gate[0] == expected_gate_names[gate_index]
                    and isinstance(gate[1], bool)
                    and isinstance(gate[2], str),
                    f"malformed gate route for {record_id}",
                )
                if gate[1] is False:
                    _require(
                        gate_index == len(gates) - 1,
                        f"gate route continues after failure for {record_id}",
                    )
            provenance = segment["provenance"]
            if provenance["mode"] == "in-row":
                _require(payload.get("run_id") == provenance["run_id"], "run_id mismatch")
                _require(
                    payload.get("run_provenance_digest") == provenance["run_provenance_digest"],
                    "run provenance digest mismatch",
                )
            _require(index not in merged, f"duplicate observation position {index} ({record_id})")
            merged[index] = raw

    for artifact in plan["observation_artifacts"]:
        for segment in artifact["segments"]:
            label = (
                f"{_resolve(args.plan, artifact['path']).name}[{segment['start']},{segment['end']})"
            )
            expected_segment = segment["end"] - segment["start"]
            _require(
                segment_counts[label] == expected_segment,
                (f"segment {label} has {segment_counts[label]} rows, expected {expected_segment}"),
            )
    _require(
        set(merged) == set(range(expected)),
        (
            f"observation coverage is not exactly [0,{expected}); "
            f"missing={len(set(range(expected)) - set(merged))}"
        ),
    )

    output_hash = None
    if args.merged_output is not None:
        _write_new(args.merged_output, b"".join(merged[index] for index in range(expected)))
        output_hash = file_sha256(args.merged_output)
    report = {
        "status": "PASS",
        "plan": str(args.plan),
        "plan_sha256": file_sha256(args.plan),
        "canonical_s02_sha256": file_sha256(s02_path),
        "records": expected,
        "unique_positions": len(merged),
        "segment_counts": segment_counts,
        "input_references": {
            "canonical_s02": plan["canonical_s02"],
            "legacy_digest_sidecars": plan.get("legacy_digest_sidecars", []),
            "observation_artifacts": plan["observation_artifacts"],
        },
        "merged_output": str(args.merged_output) if args.merged_output else None,
        "merged_output_sha256": output_hash,
    }
    encoded_report = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode()
    if args.report is not None:
        _write_new(args.report, encoded_report)
    print(encoded_report.decode(), end="")


if __name__ == "__main__":
    main()
