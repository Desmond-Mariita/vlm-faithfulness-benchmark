#!/usr/bin/env python3
"""Produce the reviewed, atomic S12–S15 GLM adjudication bundle."""

from __future__ import annotations

import argparse
import ctypes
import errno
import hashlib
import json
import os
import shutil
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterator, Mapping

from vlm_faithfulness_benchmark.gating.gates import load_pattern_registry
from vlm_faithfulness_benchmark.labeling.adjudication import (
    InputBindings,
    adjudicate_record,
    instance_from_key,
)
from vlm_faithfulness_benchmark.labeling.calibration_lock import load_calibration_lock

CONTRACT_SCHEMA = "vlm-faithfulness-m9-glm-adjudication-contract-v1"
BUNDLE_SCHEMA = "vlm-faithfulness-m9-adjudication-bundle-v1"
LEGACY_SIDECAR_SCHEMA = "vlm-faithfulness-legacy-baseline-verification-v1"
LEGACY_MANIFEST_SCHEMA = "vlm-faithfulness-legacy-baseline-verification-manifest-v1"


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"cannot read JSON object {path}") from error
    _require(isinstance(value, dict), f"{path} is not a JSON object")
    return value


def _jsonl(path: Path) -> Iterator[tuple[int, dict[str, Any]]]:
    with path.open("rb") as handle:
        for line_number, line in enumerate(handle, 1):
            _require(line.endswith(b"\n"), f"{path}:{line_number} has an incomplete final line")
            try:
                value = json.loads(line)
            except json.JSONDecodeError as error:
                raise RuntimeError(f"bad JSON at {path}:{line_number}") from error
            _require(isinstance(value, dict), f"non-object row at {path}:{line_number}")
            yield line_number, value


def _canonical_line(value: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n"
    ).encode("utf-8")


def _write_durable(path: Path, content: bytes) -> None:
    """Write and fsync one complete bundle file."""
    with path.open("wb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())


def _fsync_directory(path: Path) -> None:
    """Persist directory entries surrounding the atomic publication rename."""
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _rename_no_replace(source: Path, target: Path) -> None:
    """Atomically publish a directory while refusing an existing destination."""
    libc = ctypes.CDLL(None, use_errno=True)
    renameat2 = getattr(libc, "renameat2", None)
    _require(renameat2 is not None, "atomic no-replace rename is unavailable")
    result = renameat2(
        -100,
        os.fsencode(source),
        -100,
        os.fsencode(target),
        1,
    )
    if result == 0:
        return
    error_number = ctypes.get_errno()
    if error_number == errno.EEXIST:
        raise RuntimeError(f"output already exists; overwrite forbidden: {target}")
    raise OSError(error_number, os.strerror(error_number), target)


def _load_contract(path: Path) -> dict[str, Any]:
    contract = _json_object(path)
    _require(contract.get("schema") == CONTRACT_SCHEMA, "wrong adjudication contract schema")
    _require(contract.get("status") == "accepted", "adjudication contract is not accepted")
    output = contract.get("output")
    _require(isinstance(output, dict), "adjudication contract lacks output binding")
    _require(output.get("directory_schema") == BUNDLE_SCHEMA, "wrong output bundle schema")
    _require(output.get("ledger_key_suffix") == "::sealed_provenance", (
        "wrong sealed ledger key suffix"
    ))
    _require(output.get("overwrite") == "forbidden", "output overwrite must be forbidden")
    _require(output.get("commit") == "atomic-directory-rename", (
        "wrong output publication contract"
    ))
    return contract


def _normalized_report_segments(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    references = report.get("input_references")
    _require(isinstance(references, dict), "merge report lacks input references")
    artifacts = references.get("observation_artifacts")
    _require(isinstance(artifacts, list), "merge report lacks observation artifacts")
    normalized: list[dict[str, Any]] = []
    for artifact in artifacts:
        _require(isinstance(artifact, dict), "malformed observation artifact reference")
        segments = artifact.get("segments")
        _require(isinstance(segments, list), "observation artifact lacks segments")
        for segment in segments:
            _require(isinstance(segment, dict), "malformed observation segment")
            provenance = segment.get("provenance")
            _require(isinstance(provenance, dict), "observation segment lacks provenance")
            manifest = provenance.get("manifest")
            _require(isinstance(manifest, dict), "observation segment lacks manifest")
            item: dict[str, Any] = {
                "start": segment.get("start"),
                "end": segment.get("end"),
                "mode": provenance.get("mode"),
                "manifest_sha256": manifest.get("sha256"),
            }
            if provenance.get("mode") == "in-row":
                launch = provenance.get("launch_contract")
                _require(isinstance(launch, dict), "in-row segment lacks launch contract")
                item.update(
                    {
                        "run_id": provenance.get("run_id"),
                        "run_provenance_digest": provenance.get("run_provenance_digest"),
                        "launch_contract_sha256": launch.get("sha256"),
                    }
                )
            normalized.append(item)
    return normalized


def _report_legacy_evidence(report: Mapping[str, Any]) -> dict[str, Any]:
    references = report.get("input_references")
    _require(isinstance(references, dict), "merge report lacks references")
    sidecars = references.get("legacy_digest_sidecars")
    _require(
        isinstance(sidecars, list) and len(sidecars) == 1,
        "merge report must identify exactly one legacy sidecar",
    )
    sidecar = sidecars[0]
    _require(isinstance(sidecar, dict), "malformed legacy sidecar reference")
    manifest = sidecar.get("verification_manifest")
    _require(isinstance(manifest, dict), "legacy sidecar lacks verification manifest")
    return {
        "sidecar_sha256": sidecar.get("sha256"),
        "verification_manifest_sha256": manifest.get("sha256"),
    }


def _verify_merge_report(
    report: Mapping[str, Any], contract: Mapping[str, Any], expected_records: int
) -> None:
    inputs = contract.get("inputs")
    _require(isinstance(inputs, dict), "contract lacks inputs")
    _require(report.get("status") == "PASS", "merge validation report is not PASS")
    _require(report.get("records") == expected_records, "merge report record count mismatch")
    _require(report.get("unique_positions") == expected_records, "merge report is not one-to-one")
    _require(
        report.get("canonical_s02_sha256") == inputs.get("canonical_s02_sha256"),
        "merge report canonical S02 mismatch",
    )
    _require(
        report.get("merged_output_sha256") == inputs.get("merged_observations_sha256"),
        "merge report observation hash mismatch",
    )
    contract_segments = contract.get("observation_segments")
    _require(isinstance(contract_segments, list), "contract lacks observation segments")
    _require(
        _normalized_report_segments(report) == contract_segments,
        "contract segments do not reproduce the accepted merge report",
    )
    baseline_binding = contract.get("baseline_binding")
    _require(isinstance(baseline_binding, dict), "contract lacks baseline binding")
    legacy = baseline_binding.get("accepted_legacy_prefix")
    _require(isinstance(legacy, dict), "contract lacks legacy baseline prefix")
    evidence = legacy.get("evidence")
    _require(
        isinstance(evidence, dict) and evidence == _report_legacy_evidence(report),
        "contract legacy evidence does not reproduce the accepted merge report",
    )


def _report_artifact_covers_prefix(
    report: Mapping[str, Any], artifact_sha256: str, end: int
) -> bool:
    references = report.get("input_references")
    if not isinstance(references, dict):
        return False
    artifacts = references.get("observation_artifacts")
    if not isinstance(artifacts, list):
        return False
    for artifact in artifacts:
        if not isinstance(artifact, dict) or artifact.get("sha256") != artifact_sha256:
            continue
        segments = artifact.get("segments")
        if not isinstance(segments, list):
            continue
        ranges = sorted(
            (segment.get("start"), segment.get("end"))
            for segment in segments
            if isinstance(segment, dict)
        )
        cursor = 0
        for start, stop in ranges:
            if start != cursor or type(stop) is not int:
                break
            cursor = stop
            if cursor >= end:
                return True
    return False


def _load_legacy_sidecar(
    sidecar_path: Path,
    manifest_path: Path,
    evidence: Mapping[str, Any],
    report: Mapping[str, Any],
    expected_s02_sha256: str,
    legacy_end: int,
) -> list[dict[str, Any]]:
    """Verify the accepted legacy evidence and return its position-ordered rows."""
    sidecar_hash = evidence.get("sidecar_sha256")
    manifest_hash = evidence.get("verification_manifest_sha256")
    _require(isinstance(sidecar_hash, str), "contract lacks legacy sidecar hash")
    _require(isinstance(manifest_hash, str), "contract lacks legacy manifest hash")
    _require(_sha256(sidecar_path) == sidecar_hash, "legacy sidecar hash mismatch")
    _require(_sha256(manifest_path) == manifest_hash, "legacy manifest hash mismatch")
    manifest = _json_object(manifest_path)
    _require(manifest.get("schema") == LEGACY_MANIFEST_SCHEMA, "wrong legacy manifest schema")
    inputs = manifest.get("inputs")
    _require(isinstance(inputs, dict), "legacy manifest lacks inputs")
    s02_reference = inputs.get("s02")
    observation_reference = inputs.get("obs")
    _require(isinstance(s02_reference, dict), "legacy manifest lacks S02 reference")
    _require(isinstance(observation_reference, dict), (
        "legacy manifest lacks observation reference"
    ))
    _require(s02_reference.get("sha256") == expected_s02_sha256, (
        "legacy manifest S02 hash mismatch"
    ))
    source_observation_hash = observation_reference.get("sha256")
    _require(isinstance(source_observation_hash, str), (
        "legacy manifest observation hash is invalid"
    ))
    _require(
        _report_artifact_covers_prefix(report, source_observation_hash, legacy_end),
        "legacy manifest observation is not the report-bound prefix artifact",
    )
    result = manifest.get("result")
    _require(isinstance(result, dict), "legacy manifest lacks result")
    _require(result.get("sha256") == sidecar_hash, "legacy manifest sidecar hash mismatch")
    _require(result.get("verified_legacy_rows") == legacy_end, (
        "legacy manifest row count mismatch"
    ))
    _require(result.get("missing_digest_index_ranges") == [[0, legacy_end]], (
        "legacy manifest range mismatch"
    ))

    rows: list[dict[str, Any]] = []
    for line_number, row in _jsonl(sidecar_path):
        position = line_number - 1
        _require(position < legacy_end, "legacy sidecar has excess rows")
        _require(row.get("schema") == LEGACY_SIDECAR_SCHEMA, (
            f"wrong legacy sidecar schema at line {line_number}"
        ))
        _require(row.get("obs_line_index") == position, (
            f"legacy sidecar position mismatch at line {line_number}"
        ))
        _require(row.get("s02_ledger_sha256") == expected_s02_sha256, (
            f"legacy sidecar S02 hash mismatch at line {line_number}"
        ))
        _require(row.get("verification") == "post-hoc-rederived-from-designated-s02", (
            f"legacy sidecar verification mode mismatch at line {line_number}"
        ))
        instance_key = row.get("instance_key")
        digest = row.get("baseline_digest")
        _require(isinstance(instance_key, str), (
            f"legacy sidecar lacks instance key at line {line_number}"
        ))
        instance_from_key(instance_key)
        _require(isinstance(digest, str) and len(digest) == 64, (
            f"legacy sidecar digest is invalid at line {line_number}"
        ))
        rows.append(row)
    _require(len(rows) == legacy_end, "legacy sidecar row count mismatch")
    return rows


def _load_s02(path: Path, records: int) -> dict[str, dict[str, Any]]:
    payloads: dict[str, dict[str, Any]] = {}
    for _, row in _jsonl(path):
        key = row.get("key")
        payload = row.get("payload")
        _require(isinstance(key, str) and key.endswith("::output_tuple"), "bad S02 ledger key")
        _require(isinstance(payload, dict), "bad S02 payload")
        instance_key = key.removesuffix("::output_tuple")
        instance_from_key(instance_key)
        _require(instance_key not in payloads, f"duplicate S02 instance {instance_key}")
        payloads[instance_key] = payload
    _require(len(payloads) == records, "canonical S02 record count mismatch")
    return payloads


def _segment_for(position: int, segments: list[dict[str, Any]]) -> dict[str, Any]:
    matches = [segment for segment in segments if segment["start"] <= position < segment["end"]]
    _require(len(matches) == 1, f"position {position} is not in exactly one run segment")
    return matches[0]


def _verify_segment_row(observation: Mapping[str, Any], segment: Mapping[str, Any]) -> None:
    mode = segment.get("mode")
    if mode == "in-row":
        _require(observation.get("run_id") == segment.get("run_id"), "run_id segment mismatch")
        _require(
            observation.get("run_provenance_digest")
            == segment.get("run_provenance_digest"),
            "run provenance segment mismatch",
        )
    else:
        _require(mode == "external", "unknown run-provenance mode")
        _require(
            "run_id" not in observation and "run_provenance_digest" not in observation,
            "external-provenance row unexpectedly carries in-row provenance",
        )


def _resolution_counter(payload: Mapping[str, Any]) -> str:
    provenance = payload.get("provenance")
    _require(isinstance(provenance, dict), "sealed payload lacks provenance")
    resolution = provenance.get("resolution")
    _require(isinstance(resolution, dict), "sealed payload lacks resolution")
    e_code = resolution.get("e_code")
    if isinstance(e_code, str):
        return e_code
    state = resolution.get("state")
    _require(isinstance(state, str), "labelled resolution lacks state")
    return state


def run_adjudication(
    contract_path: Path,
    expected_contract_sha256: str,
    repo_root: Path,
    s02_path: Path,
    observations_path: Path,
    merge_report_path: Path,
    legacy_sidecar_path: Path,
    legacy_manifest_path: Path,
    output_dir: Path,
) -> dict[str, Any]:
    """Verify all inputs, adjudicate all records, and atomically publish a bundle."""
    _require(not output_dir.exists(), f"output already exists; overwrite forbidden: {output_dir}")
    _require(_sha256(contract_path) == expected_contract_sha256, (
        "adjudication contract hash mismatch"
    ))
    contract = _load_contract(contract_path)
    contract_hash = expected_contract_sha256
    records = contract.get("records")
    _require(type(records) is int and records > 0, "contract record count is invalid")
    inputs = contract.get("inputs")
    _require(isinstance(inputs, dict), "contract lacks inputs")
    expected_s02_hash = inputs.get("canonical_s02_sha256")
    expected_observation_hash = inputs.get("merged_observations_sha256")
    expected_report_hash = inputs.get("merge_validation_report_sha256")
    _require(_sha256(s02_path) == expected_s02_hash, "canonical S02 hash mismatch")
    _require(_sha256(observations_path) == expected_observation_hash, (
        "merged observation hash mismatch"
    ))
    _require(_sha256(merge_report_path) == expected_report_hash, (
        "merge validation report hash mismatch"
    ))
    report = _json_object(merge_report_path)
    _verify_merge_report(report, contract, records)

    calibration_ref = inputs.get("calibration_lock")
    _require(isinstance(calibration_ref, dict), "contract lacks calibration lock reference")
    calibration_path_value = calibration_ref.get("path")
    calibration_hash = calibration_ref.get("sha256")
    _require(isinstance(calibration_path_value, str), "bad calibration lock path")
    calibration_path = repo_root / calibration_path_value
    _require(_sha256(calibration_path) == calibration_hash, "calibration lock hash mismatch")
    calibration = load_calibration_lock(calibration_path, repo_root)
    registry = load_pattern_registry(calibration.coherence_registry_path)
    s02 = _load_s02(s02_path, records)

    baseline_binding = contract.get("baseline_binding")
    _require(isinstance(baseline_binding, dict), "contract lacks baseline binding")
    legacy = baseline_binding.get("accepted_legacy_prefix")
    _require(isinstance(legacy, dict), "contract lacks legacy baseline prefix")
    _require(legacy.get("start") == 0 and legacy.get("mode") == "accepted-legacy-sidecar", (
        "legacy baseline prefix is malformed"
    ))
    legacy_end = legacy.get("end")
    _require(type(legacy_end) is int and 0 <= legacy_end <= records, "legacy prefix end invalid")
    _require(baseline_binding.get("remaining_mode") == "in-row", (
        "remaining baseline mode must be in-row"
    ))
    evidence = legacy.get("evidence")
    _require(isinstance(evidence, dict), "legacy prefix lacks evidence binding")
    legacy_rows = _load_legacy_sidecar(
        legacy_sidecar_path,
        legacy_manifest_path,
        evidence,
        report,
        str(expected_s02_hash),
        legacy_end,
    )
    segments_raw = contract.get("observation_segments")
    _require(isinstance(segments_raw, list), "contract lacks observation segments")
    segments = [dict(segment) for segment in segments_raw if isinstance(segment, dict)]
    _require(len(segments) == len(segments_raw), "malformed observation segment")
    _require(segments[0].get("start") == 0 and segments[-1].get("end") == records, (
        "observation segments do not cover the full ledger"
    ))
    for left, right in zip(segments, segments[1:]):
        _require(left.get("end") == right.get("start"), "observation segments have a gap")

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{output_dir.name}.tmp-", dir=output_dir.parent)
    )
    ledger_path = temporary / "sealed-provenance.jsonl"
    seen: set[str] = set()
    counts: Counter[str] = Counter()
    try:
        with ledger_path.open("wb") as output:
            for line_number, row in _jsonl(observations_path):
                position = line_number - 1
                key = row.get("key")
                observation = row.get("payload")
                _require(
                    isinstance(key, str) and key.endswith("::pilot_obs"),
                    f"bad observation key at line {line_number}",
                )
                _require(isinstance(observation, dict), "bad observation payload")
                instance_key = key.removesuffix("::pilot_obs")
                _require(instance_key not in seen, f"duplicate observation {instance_key}")
                _require(instance_key in s02, f"observation lacks canonical S02 {instance_key}")
                instance = instance_from_key(instance_key)
                _require(instance.generator.key() == contract.get("generator_identity"), (
                    "observation generator identity violates the run contract"
                ))
                if position < legacy_end:
                    legacy_row = legacy_rows[position]
                    _require(legacy_row.get("instance_key") == instance_key, (
                        f"legacy sidecar instance mismatch at position {position}"
                    ))
                    _require(legacy_row.get("record_id") == instance.source.record_id, (
                        f"legacy sidecar source mismatch at position {position}"
                    ))
                    _require(
                        legacy_row.get("baseline_digest")
                        == s02[instance_key].get("baseline_digest"),
                        f"legacy sidecar digest mismatch at position {position}",
                    )
                segment = _segment_for(position, segments)
                _verify_segment_row(observation, segment)
                baseline_mode = "accepted-legacy-sidecar" if position < legacy_end else "in-row"
                bindings = InputBindings(
                    baseline_mode=baseline_mode,
                    s02_sha256=str(expected_s02_hash),
                    observation_sha256=str(expected_observation_hash),
                    observation_line=line_number,
                    merge_report_sha256=str(expected_report_hash),
                    run_binding=segment,
                )
                payload = adjudicate_record(
                    instance_key,
                    s02[instance_key],
                    observation,
                    bindings,
                    calibration,
                    registry,
                )
                output.write(
                    _canonical_line(
                        {"key": f"{instance_key}::sealed_provenance", "payload": payload}
                    )
                )
                seen.add(instance_key)
                counts[_resolution_counter(payload)] += 1
            output.flush()
            os.fsync(output.fileno())
        _require(len(seen) == records, "sealed output record count mismatch")
        _require(seen == set(s02), "S02 and observation instance sets differ")
        _require(sum(counts.values()) == records, "resolution totality failed")

        ledger_hash = _sha256(ledger_path)
        summary: dict[str, Any] = {
            "schema": "vlm-faithfulness-m9-adjudication-summary-v1",
            "contract_id": contract.get("id"),
            "contract_sha256": contract_hash,
            "records": records,
            "labelled": sum(counts[state] for state in ("S1", "S2", "S3")),
            "routed": sum(counts[code] for code in ("E1", "E2", "E3", "E4", "E5", "E6")),
            "resolution_counts": dict(sorted(counts.items())),
            "sealed_provenance_sha256": ledger_hash,
        }
        summary_path = temporary / "summary.json"
        _write_durable(summary_path, _canonical_line(summary))
        manifest: dict[str, Any] = {
            "schema": BUNDLE_SCHEMA,
            "contract": {"id": contract.get("id"), "sha256": contract_hash},
            "inputs": {
                "canonical_s02_sha256": expected_s02_hash,
                "merged_observations_sha256": expected_observation_hash,
                "merge_validation_report_sha256": expected_report_hash,
                "calibration_lock_sha256": calibration.lock_sha256,
                "legacy_sidecar_sha256": evidence["sidecar_sha256"],
                "legacy_manifest_sha256": evidence["verification_manifest_sha256"],
            },
            "outputs": {
                "sealed-provenance.jsonl": {
                    "bytes": ledger_path.stat().st_size,
                    "records": records,
                    "sha256": ledger_hash,
                },
                "summary.json": {
                    "bytes": summary_path.stat().st_size,
                    "sha256": _sha256(summary_path),
                },
            },
        }
        manifest_path = temporary / "manifest.json"
        _write_durable(manifest_path, _canonical_line(manifest))
        _fsync_directory(temporary)
        _rename_no_replace(temporary, output_dir)
        _fsync_directory(output_dir.parent)
        return summary
    except BaseException:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--contract-sha256", required=True)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--s02", type=Path, required=True)
    parser.add_argument("--observations", type=Path, required=True)
    parser.add_argument("--merge-report", type=Path, required=True)
    parser.add_argument("--legacy-sidecar", type=Path, required=True)
    parser.add_argument("--legacy-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser


def main() -> None:
    """CLI entry point."""
    args = _parser().parse_args()
    summary = run_adjudication(
        args.contract,
        args.contract_sha256,
        args.repo_root,
        args.s02,
        args.observations,
        args.merge_report,
        args.legacy_sidecar,
        args.legacy_manifest,
        args.output_dir,
    )
    print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
