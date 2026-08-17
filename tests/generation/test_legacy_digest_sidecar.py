"""Tests for post-hoc legacy baseline verification evidence."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from vlm_faithfulness_benchmark.generation.digest import baseline_digest
from vlm_faithfulness_benchmark.run_provenance import file_sha256


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))


def test_legacy_sidecar_is_truthful_and_does_not_mutate_inputs(tmp_path: Path) -> None:
    """The verifier covers only missing rows and explicitly limits its claim."""
    root = Path(__file__).resolve().parents[2]
    instance = {
        "generator": {"model": "stub", "revision": "1"},
        "source": {"dataset": "aokvqa", "record_id": "r1"},
    }
    instance_key = json.dumps(instance, sort_keys=True, separators=(",", ":"))
    output_tuple = {"chosen_answer": "a", "rationale": "because"}
    digest = baseline_digest(output_tuple)
    s02 = tmp_path / "s02.jsonl"
    obs = tmp_path / "obs.jsonl"
    _write_jsonl(
        s02,
        [
            {
                "key": f"{instance_key}::output_tuple",
                "payload": {
                    "source": json.dumps(instance["source"], sort_keys=True, separators=(",", ":")),
                    "output_tuple": output_tuple,
                    "baseline_digest": digest,
                },
            }
        ],
    )
    _write_jsonl(
        obs,
        [
            {
                "key": f"{instance_key}::pilot_obs",
                "payload": {
                    "source": json.dumps(instance["source"], sort_keys=True, separators=(",", ":")),
                },
            }
        ],
    )
    before = obs.read_bytes()
    sidecar = tmp_path / "sidecar.jsonl"
    manifest = tmp_path / "manifest.json"
    subprocess.run(
        [
            sys.executable,
            str(root / "scripts_verify_legacy_digests.py"),
            "--s02",
            str(s02),
            "--obs",
            str(obs),
            "--expected-missing",
            "1",
            "--expected-s02-sha256",
            file_sha256(s02),
            "--expected-s02-rows",
            "1",
            "--expected-obs-sha256",
            file_sha256(obs),
            "--expected-obs-rows",
            "1",
            "--expected-generator-identity",
            json.dumps(instance["generator"], sort_keys=True, separators=(",", ":")),
            "--expected-missing-range",
            "0:1",
            "--sidecar",
            str(sidecar),
            "--manifest",
            str(manifest),
        ],
        cwd=root,
        check=True,
    )
    assert obs.read_bytes() == before
    row = json.loads(sidecar.read_text())
    assert row["baseline_digest"] == digest
    assert row["historical_consumer_verification"] == "not-recorded"
    evidence = json.loads(manifest.read_text())
    assert evidence["claim_boundary"]["observation_ledger_modified"] is False
    assert "does_not_prove" in evidence["claim_boundary"]


def test_optimized_python_cannot_disable_legacy_input_guards(tmp_path: Path) -> None:
    """Every release guard remains active under ``python -O``."""
    root = Path(__file__).resolve().parents[2]
    s02 = tmp_path / "s02.jsonl"
    obs = tmp_path / "obs.jsonl"
    s02.write_text("{}\n")
    obs.write_text("{}\n")
    sidecar = tmp_path / "sidecar.jsonl"
    manifest = tmp_path / "manifest.json"
    result = subprocess.run(
        [
            sys.executable,
            "-O",
            str(root / "scripts_verify_legacy_digests.py"),
            "--s02",
            str(s02),
            "--obs",
            str(obs),
            "--expected-missing",
            "1",
            "--expected-s02-sha256",
            "0" * 64,
            "--expected-s02-rows",
            "1",
            "--expected-obs-sha256",
            "0" * 64,
            "--expected-obs-rows",
            "1",
            "--expected-generator-identity",
            "{}",
            "--expected-missing-range",
            "0:1",
            "--sidecar",
            str(sidecar),
            "--manifest",
            str(manifest),
        ],
        cwd=root,
        env={"PYTHONPATH": str(root / "src")},
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert (
        "unexpected S02 input hash" in result.stderr
        or "refuses to run under python -O" in result.stderr
    )
    assert not sidecar.exists()
    assert not manifest.exists()
