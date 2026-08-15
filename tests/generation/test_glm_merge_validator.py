"""End-to-end fixture for the manifest-driven GLM merge validator."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from vlm_faithfulness_benchmark import run_provenance
from vlm_faithfulness_benchmark.generation.digest import baseline_digest
from vlm_faithfulness_benchmark.run_provenance import file_sha256


def _jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))


def test_merge_validator_accepts_legacy_sidecar_and_in_row_provenance(tmp_path: Path) -> None:
    """A two-segment lane must validate every required binding exactly once."""
    root = Path(__file__).resolve().parents[2]
    identity = {"model": "glm", "revision": "pinned"}
    identity_key = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    s02_rows = []
    obs_legacy = []
    obs_new = []
    sidecar_rows = []
    for index in range(2):
        source = {"dataset": "aokvqa", "record_id": f"r{index}"}
        instance = {"generator": identity, "source": source}
        instance_key = json.dumps(instance, sort_keys=True, separators=(",", ":"))
        source_key = json.dumps(source, sort_keys=True, separators=(",", ":"))
        output_tuple = {"chosen_answer": "a", "rationale": f"r{index}"}
        digest = baseline_digest(output_tuple)
        s02_rows.append(
            {
                "key": f"{instance_key}::output_tuple",
                "payload": {
                    "source": source_key,
                    "output_tuple": output_tuple,
                    "baseline_digest": digest,
                },
            }
        )
        payload: dict[str, object] = {
            "source": source_key,
            "gates": [["P1", False, "fixture route"]],
            "route": "E1",
        }
        row = {"key": f"{instance_key}::pilot_obs", "payload": payload}
        if index == 0:
            obs_legacy.append(row)
            sidecar_rows.append(
                {
                    "schema": "vlm-faithfulness-legacy-baseline-verification-v1",
                    "obs_line_index": index,
                    "record_id": source["record_id"],
                    "instance_key": instance_key,
                    "baseline_digest": digest,
                    "s02_ledger_sha256": "pending",
                    "verification": "post-hoc-rederived-from-designated-s02",
                    "historical_consumer_verification": "not-recorded",
                }
            )
        else:
            payload.update(
                {
                    "baseline_digest": digest,
                    "run_id": "new-run",
                    "run_provenance_digest": "a" * 64,
                }
            )
            obs_new.append(row)
    s02 = tmp_path / "s02.jsonl"
    legacy = tmp_path / "legacy.jsonl"
    new = tmp_path / "new.jsonl"
    sidecar = tmp_path / "sidecar.jsonl"
    sidecar_manifest = tmp_path / "sidecar-manifest.json"
    environment = tmp_path / "legacy-env.json"
    _jsonl(s02, s02_rows)
    s02_hash = file_sha256(s02)
    sidecar_rows[0]["s02_ledger_sha256"] = s02_hash
    _jsonl(legacy, obs_legacy)
    _jsonl(new, obs_new)
    _jsonl(sidecar, sidecar_rows)
    sidecar_manifest.write_text(
        json.dumps(
            {
                "schema": "vlm-faithfulness-legacy-baseline-verification-manifest-v1",
                "inputs": {
                    "s02": {"sha256": s02_hash},
                    "obs": {"sha256": file_sha256(legacy)},
                },
                "result": {
                    "sha256": file_sha256(sidecar),
                    "verified_legacy_rows": 1,
                },
                "claim_boundary": {
                    "observation_ledger_modified": False,
                    "does_not_prove": (
                        "The historical observation consumer performed verification."
                    ),
                },
            }
        )
        + "\n"
    )
    environment.write_text(
        json.dumps(
            {
                "schema": "vlm-faithfulness-reconstructed-run-provenance-v1",
                "segments": [
                    {
                        "start": 0,
                        "end": 1,
                        "benchmark_commit": "old",
                        "driver_sha256": "d" * 64,
                        "git_src_tree": "tree",
                    }
                ],
                "generator": {"identity": identity_key},
                "host": {
                    "platform": "test",
                    "python": "test",
                    "numpy": "test",
                    "pillow": "test",
                    "torch": "test",
                    "torch_cuda": "test",
                    "cudnn": "test",
                    "transformers": "test",
                    "driver": "test",
                    "gpu_name": "NVIDIA GeForce RTX 3090",
                    "compute_capability": "8.6",
                },
                "evidence": {"canonical_s02_sha256": s02_hash},
                "deterministic_scope": {"on_stack": True, "cross_stack": False},
            }
        )
        + "\n"
    )
    runtime = {
        "platform": "test-cloud",
        "python": "test",
        "numpy": "test",
        "pillow": "test",
        "torch": "test",
        "torch_cuda": "test",
        "cudnn": "test",
        "transformers": "test",
        "gpu": {
            "name": "test-5090",
            "compute_capability": "test",
            "driver": "test",
        },
    }
    environment_fingerprint = run_provenance.gate_environment_fingerprint(runtime)
    contract = tmp_path / "tail-contract.json"
    contract.write_text(
        json.dumps(
            {
                "schema": run_provenance.TAIL_CONTRACT_SCHEMA,
                "authorized_shards": [[6154, 7577], [7577, 9000]],
                "generator_identity": identity_key,
                "canonical_s02_sha256": s02_hash,
                "pool_manifest_sha256": run_provenance.M9_POOL_MANIFEST_SHA256,
                "prereg_sha256": run_provenance.M9_PREREG_SHA256,
                "environment_fingerprint": environment_fingerprint,
                "code_commit": "reviewed",
                "driver_sha256": "a",
                "source_tree_sha256": "a",
                "config_tree_sha256": "a",
                "aokvqa_tree_sha256": "a",
                "gate_sha256": "a",
                "s02_ledger_sha256": s02_hash,
                "image_root_tree_sha256": "a",
            }
        )
        + "\n"
    )
    contract_hash = file_sha256(contract)
    new_manifest = tmp_path / "new-run-manifest.json"
    new_manifest.write_text(
        json.dumps(
            {
                "schema": "vlm-faithfulness-run-provenance-v1",
                "run_id": "new-run",
                "shard": {"start": 1, "end": 2, "generator_identity": identity_key},
                "runtime": runtime,
                "code": {"declared_commit": "reviewed"},
                "launch_contract": {"sha256": contract_hash},
                "artifacts": {
                    "driver_sha256": "a",
                    "source_tree_sha256": "a",
                    "config_tree_sha256": "a",
                    "aokvqa_tree_sha256": "a",
                    "gate_sha256": "a",
                    "s02_ledger_sha256": s02_hash,
                    "image_root_tree_sha256": "a",
                },
                "deterministic_scope": {"on_stack": True, "cross_stack": False},
            }
        )
        + "\n"
    )
    new_manifest_hash = file_sha256(new_manifest)
    obs_new[0]["payload"]["run_provenance_digest"] = new_manifest_hash  # type: ignore[index]
    _jsonl(new, obs_new)
    plan = {
        "schema": "vlm-faithfulness-glm-merge-plan-v1",
        "expected_records": 2,
        "generator_identity": identity_key,
        "canonical_s02": {"path": str(s02), "sha256": s02_hash},
        "legacy_digest_sidecars": [
            {
                "path": str(sidecar),
                "sha256": file_sha256(sidecar),
                "verification_manifest": {
                    "path": str(sidecar_manifest),
                    "sha256": file_sha256(sidecar_manifest),
                },
            }
        ],
        "observation_artifacts": [
            {
                "path": str(legacy),
                "sha256": file_sha256(legacy),
                "segments": [
                    {
                        "start": 0,
                        "end": 1,
                        "provenance": {
                            "mode": "external",
                            "manifest": {
                                "path": str(environment),
                                "sha256": file_sha256(environment),
                            },
                        },
                    }
                ],
            },
            {
                "path": str(new),
                "sha256": file_sha256(new),
                "segments": [
                    {
                        "start": 1,
                        "end": 2,
                        "provenance": {
                            "mode": "in-row",
                            "run_id": "new-run",
                            "run_provenance_digest": new_manifest_hash,
                            "manifest": {
                                "path": str(new_manifest),
                                "sha256": new_manifest_hash,
                            },
                            "launch_contract": {
                                "path": str(contract),
                                "sha256": contract_hash,
                            },
                        },
                    }
                ],
            },
        ],
    }
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan, indent=2) + "\n")
    merged = tmp_path / "merged.jsonl"
    report = tmp_path / "report.json"
    bootstrap = (
        "import sys; import scripts_validate_glm_merge as m; "
        "m.M9_EXPECTED_RECORDS=2; m.M9_CANONICAL_S02_SHA256=sys.argv.pop(1); "
        "m.M9_GLM_IDENTITY=sys.argv.pop(1); m.M9_LEGACY_END=1; "
        "m.M9_SEGMENTS=[(0,1),(1,2)]; "
        f"m.M9_5090_ENVIRONMENT_FINGERPRINT='{environment_fingerprint}'; "
        "m.M9_IMAGE_ROOT_TREE_SHA256='a'; m.main()"
    )
    subprocess.run(
        [
            sys.executable,
            "-c",
            bootstrap,
            s02_hash,
            identity_key,
            "--plan",
            str(plan_path),
            "--merged-output",
            str(merged),
            "--report",
            str(report),
        ],
        cwd=root,
        check=True,
    )
    assert len(merged.read_text().splitlines()) == 2
    assert json.loads(report.read_text())["status"] == "PASS"
