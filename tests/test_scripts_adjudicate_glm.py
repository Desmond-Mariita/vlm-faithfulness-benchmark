"""Integration tests for the production GLM adjudication bundle writer."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
import scripts_adjudicate_glm as runner

from vlm_faithfulness_benchmark.generation.digest import baseline_digest
from vlm_faithfulness_benchmark.generation.identity import (
    GeneratorId,
    InstanceId,
    SourceRecordId,
)

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = GeneratorId.from_mapping({"model": "glm-integration", "revision": "abc"})
EXTERNAL_MANIFEST = "1" * 64


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    content = "".join(
        json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in rows
    )
    path.write_text(content, encoding="utf-8")


def _s02_row(instance: InstanceId) -> dict[str, Any]:
    output_tuple = {
        "chosen_answer": "red",
        "rationale": "a red umbrella protects the person from heavy rain",
    }
    return {
        "key": f"{instance.key()}::output_tuple",
        "payload": {
            "source": instance.source.key(),
            "generator": instance.generator.key(),
            "output_tuple": output_tuple,
            "baseline_digest": baseline_digest(output_tuple),
        },
    }


def _observation_rows(instances: tuple[InstanceId, InstanceId]) -> list[dict[str, Any]]:
    early, labelled = instances
    labelled_digest = _s02_row(labelled)["payload"]["baseline_digest"]
    scores = [1.0, 0.0]
    return [
        {
            "key": f"{early.key()}::pilot_obs",
            "payload": {
                "source": early.source.key(),
                "gates": [["P1", False, "chosen answer parses to multiple options"]],
                "route": "E1",
            },
        },
        {
            "key": f"{labelled.key()}::pilot_obs",
            "payload": {
                "source": labelled.source.key(),
                "baseline_digest": labelled_digest,
                "gates": [
                    ["P1", True, "complete tuple"],
                    ["P2", True, "bona fide"],
                    ["P3", True, "in scope"],
                ],
                "baseline_chosen_index": 0,
                "readings": {
                    "real": scores,
                    "grey": scores,
                    "wrong-image": scores,
                    "occlude": scores,
                    "noise": scores,
                    "hflip": scores,
                },
                "flip_count": 0,
                "hflip": {
                    "spatial_lateral": False,
                    "evaluable": True,
                    "persisted": True,
                },
            },
        },
    ]


def _fixture(tmp_path: Path, status: str = "accepted") -> dict[str, Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    instances = (
        InstanceId(GENERATOR, SourceRecordId("aokvqa", "early")),
        InstanceId(GENERATOR, SourceRecordId("aokvqa", "labelled")),
    )
    s02_path = tmp_path / "s02.jsonl"
    observations_path = tmp_path / "observations.jsonl"
    sidecar_path = tmp_path / "legacy-sidecar.jsonl"
    legacy_manifest_path = tmp_path / "legacy-manifest.json"
    report_path = tmp_path / "merge-report.json"
    contract_path = tmp_path / "contract.json"
    _write_jsonl(s02_path, [_s02_row(instance) for instance in instances])
    _write_jsonl(observations_path, _observation_rows(instances))
    early_payload = _s02_row(instances[0])["payload"]
    _write_jsonl(
        sidecar_path,
        [
            {
                "schema": runner.LEGACY_SIDECAR_SCHEMA,
                "obs_line_index": 0,
                "instance_key": instances[0].key(),
                "record_id": instances[0].source.record_id,
                "baseline_digest": early_payload["baseline_digest"],
                "s02_ledger_sha256": _sha256(s02_path),
                "verification": "post-hoc-rederived-from-designated-s02",
                "historical_consumer_verification": "not-recorded",
            }
        ],
    )
    legacy_manifest = {
        "schema": runner.LEGACY_MANIFEST_SCHEMA,
        "inputs": {
            "s02": {"sha256": _sha256(s02_path), "rows": 2},
            "obs": {"sha256": _sha256(observations_path), "rows": 2},
        },
        "result": {
            "sha256": _sha256(sidecar_path),
            "verified_legacy_rows": 1,
            "missing_digest_index_ranges": [[0, 1]],
        },
    }
    legacy_manifest_path.write_text(json.dumps(legacy_manifest), encoding="utf-8")

    segment = {
        "start": 0,
        "end": 2,
        "mode": "external",
        "manifest_sha256": EXTERNAL_MANIFEST,
    }
    report = {
        "status": "PASS",
        "records": 2,
        "unique_positions": 2,
        "canonical_s02_sha256": _sha256(s02_path),
        "merged_output_sha256": _sha256(observations_path),
        "input_references": {
            "canonical_s02": {"path": "s02.jsonl", "sha256": _sha256(s02_path)},
            "legacy_digest_sidecars": [
                {
                    "path": "legacy-sidecar.jsonl",
                    "sha256": _sha256(sidecar_path),
                    "verification_manifest": {
                        "path": "legacy-manifest.json",
                        "sha256": _sha256(legacy_manifest_path),
                    },
                }
            ],
            "observation_artifacts": [
                {
                    "path": "observations.jsonl",
                    "sha256": _sha256(observations_path),
                    "segments": [
                        {
                            "start": 0,
                            "end": 2,
                            "provenance": {
                                "mode": "external",
                                "manifest": {
                                    "path": "accepted-manifest.json",
                                    "sha256": EXTERNAL_MANIFEST,
                                },
                            },
                        }
                    ],
                }
            ],
        },
    }
    report_path.write_text(json.dumps(report), encoding="utf-8")
    lock_path = ROOT / "config/calibration_lock_v1.json"
    contract = {
        "schema": runner.CONTRACT_SCHEMA,
        "id": "integration-contract",
        "status": status,
        "generator_identity": GENERATOR.key(),
        "records": 2,
        "inputs": {
            "canonical_s02_sha256": _sha256(s02_path),
            "merged_observations_sha256": _sha256(observations_path),
            "merge_validation_report_sha256": _sha256(report_path),
            "calibration_lock": {
                "path": "config/calibration_lock_v1.json",
                "sha256": _sha256(lock_path),
            },
        },
        "baseline_binding": {
            "accepted_legacy_prefix": {
                "start": 0,
                "end": 1,
                "mode": "accepted-legacy-sidecar",
                "evidence": {
                    "sidecar_sha256": _sha256(sidecar_path),
                    "verification_manifest_sha256": _sha256(legacy_manifest_path),
                },
            },
            "remaining_mode": "in-row",
        },
        "observation_segments": [segment],
        "output": {
            "directory_schema": runner.BUNDLE_SCHEMA,
            "ledger_key_suffix": "::sealed_provenance",
            "overwrite": "forbidden",
            "commit": "atomic-directory-rename",
        },
    }
    contract_path.write_text(json.dumps(contract), encoding="utf-8")
    return {
        "contract": contract_path,
        "s02": s02_path,
        "observations": observations_path,
        "report": report_path,
        "sidecar": sidecar_path,
        "legacy_manifest": legacy_manifest_path,
    }


def _run(
    paths: dict[str, Path], output: Path, contract_sha256: str | None = None
) -> dict[str, Any]:
    return runner.run_adjudication(
        paths["contract"],
        contract_sha256 or _sha256(paths["contract"]),
        ROOT,
        paths["s02"],
        paths["observations"],
        paths["report"],
        paths["sidecar"],
        paths["legacy_manifest"],
        output,
    )


def test_bundle_success_manifest_and_determinism(tmp_path: Path) -> None:
    """The top-level writer produces a complete deterministic two-record bundle."""
    paths = _fixture(tmp_path)
    first = tmp_path / "bundle-one"
    second = tmp_path / "bundle-two"
    summary = _run(paths, first)
    repeated = _run(paths, second)
    assert summary == repeated
    assert summary["resolution_counts"] == {"E1": 1, "S1": 1}
    assert summary["labelled"] == 1 and summary["routed"] == 1
    assert (first / "sealed-provenance.jsonl").read_bytes() == (
        second / "sealed-provenance.jsonl"
    ).read_bytes()
    assert (first / "summary.json").read_bytes() == (second / "summary.json").read_bytes()
    assert _sha256(first / "sealed-provenance.jsonl") == (
        "83a825d83f5ae48d256678862306a642c1579192cb555eee9344fea849e8bfd5"
    )
    assert _sha256(first / "summary.json") == (
        "07c87d67c8394bf4b23ac350b2f2940a929aa075d4edac511864cbfa4c569c4a"
    )
    assert _sha256(first / "manifest.json") == (
        "29be444d667ae83c459b60d4b5431b903649172375071b9a32c40fb6fc147a39"
    )
    manifest = json.loads((first / "manifest.json").read_text())
    for filename, evidence in manifest["outputs"].items():
        assert evidence["sha256"] == _sha256(first / filename)
        assert evidence["bytes"] == (first / filename).stat().st_size


def test_writer_rejects_overwrite_pending_contract_and_hash_drift(tmp_path: Path) -> None:
    """The production gates fail before mutating an existing or unaccepted target."""
    paths = _fixture(tmp_path)
    with pytest.raises(RuntimeError, match="contract hash mismatch"):
        _run(paths, tmp_path / "wrong-contract-output", "0" * 64)
    output = tmp_path / "bundle"
    _run(paths, output)
    with pytest.raises(RuntimeError, match="overwrite forbidden"):
        _run(paths, output)

    pending_paths = _fixture(tmp_path / "pending", status="review-pending")
    with pytest.raises(RuntimeError, match="not accepted"):
        _run(pending_paths, tmp_path / "pending-output")

    output_drift = _fixture(tmp_path / "output-drift")
    output_contract = json.loads(output_drift["contract"].read_text())
    output_contract["output"]["ledger_key_suffix"] = "::unreviewed"
    output_drift["contract"].write_text(json.dumps(output_contract), encoding="utf-8")
    with pytest.raises(RuntimeError, match="ledger key suffix"):
        _run(output_drift, tmp_path / "output-drift-output")

    drift_paths = _fixture(tmp_path / "drift")
    drift_paths["observations"].write_bytes(
        drift_paths["observations"].read_bytes() + b"\n"
    )
    with pytest.raises(RuntimeError, match="observation hash mismatch"):
        _run(drift_paths, tmp_path / "drift-output")

    sidecar_drift = _fixture(tmp_path / "sidecar-drift")
    sidecar_drift["sidecar"].write_bytes(sidecar_drift["sidecar"].read_bytes() + b"\n")
    with pytest.raises(RuntimeError, match="sidecar hash mismatch"):
        _run(sidecar_drift, tmp_path / "sidecar-drift-output")


def test_legacy_sidecar_is_compared_to_each_bound_row(tmp_path: Path) -> None:
    """A self-consistently rehashed but row-mismatched sidecar still fails closed."""
    paths = _fixture(tmp_path)
    sidecar_row = json.loads(paths["sidecar"].read_text())
    sidecar_row["instance_key"] = InstanceId(
        GENERATOR, SourceRecordId("aokvqa", "substituted")
    ).key()
    _write_jsonl(paths["sidecar"], [sidecar_row])

    legacy_manifest = json.loads(paths["legacy_manifest"].read_text())
    legacy_manifest["result"]["sha256"] = _sha256(paths["sidecar"])
    paths["legacy_manifest"].write_text(json.dumps(legacy_manifest), encoding="utf-8")
    report = json.loads(paths["report"].read_text())
    report_sidecar = report["input_references"]["legacy_digest_sidecars"][0]
    report_sidecar["sha256"] = _sha256(paths["sidecar"])
    report_sidecar["verification_manifest"]["sha256"] = _sha256(
        paths["legacy_manifest"]
    )
    paths["report"].write_text(json.dumps(report), encoding="utf-8")
    contract = json.loads(paths["contract"].read_text())
    contract_legacy = contract["baseline_binding"]["accepted_legacy_prefix"]
    contract_legacy["evidence"]["sidecar_sha256"] = _sha256(paths["sidecar"])
    contract_legacy["evidence"]["verification_manifest_sha256"] = _sha256(
        paths["legacy_manifest"]
    )
    contract["inputs"]["merge_validation_report_sha256"] = _sha256(paths["report"])
    paths["contract"].write_text(json.dumps(contract), encoding="utf-8")

    with pytest.raises(RuntimeError, match="sidecar instance mismatch"):
        _run(paths, tmp_path / "row-mismatch-output")


def test_publication_race_preserves_existing_destination(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An output created at publication time is never replaced."""
    paths = _fixture(tmp_path)
    output = tmp_path / "bundle"
    publish = runner._rename_no_replace

    def occupy_then_publish(source: Path, target: Path) -> None:
        target.mkdir()
        (target / "sentinel").write_text("preserve", encoding="utf-8")
        publish(source, target)

    monkeypatch.setattr(runner, "_rename_no_replace", occupy_then_publish)
    with pytest.raises(RuntimeError, match="overwrite forbidden"):
        _run(paths, output)
    assert (output / "sentinel").read_text() == "preserve"
    assert not list(tmp_path.glob(".bundle.tmp-*"))


def test_failed_publication_cleans_staging_directory(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A rename failure publishes nothing and removes only its scoped staging tree."""
    paths = _fixture(tmp_path)
    output = tmp_path / "bundle"

    def fail_rename(source: Path, target: Path) -> None:
        raise OSError(f"injected rename failure {source} -> {target}")

    monkeypatch.setattr(runner, "_rename_no_replace", fail_rename)
    with pytest.raises(OSError, match="injected rename failure"):
        _run(paths, output)
    assert not output.exists()
    assert not list(tmp_path.glob(".bundle.tmp-*"))
