"""Tests for fail-closed mass-run provenance manifests."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest

from vlm_faithfulness_benchmark import run_provenance


def test_gate_fingerprint_is_environment_class_not_physical_gpu() -> None:
    """Two identical 5090s share a gate; a package change invalidates it."""
    runtime: dict[str, object] = {
        "platform": "linux",
        "python": "3.12",
        "numpy": "2",
        "pillow": "12",
        "torch": "2.12",
        "torch_cuda": "13",
        "cudnn": 92000,
        "transformers": "5.15",
        "gpu": {
            "name": "RTX 5090",
            "compute_capability": "12.0",
            "driver": "580",
            "uuid": "gpu-a",
            "physical_index": "0",
        },
    }
    other_gpu = deepcopy(runtime)
    assert isinstance(other_gpu["gpu"], dict)
    other_gpu["gpu"].update({"uuid": "gpu-b", "physical_index": "1"})
    assert run_provenance.gate_environment_fingerprint(runtime) == (
        run_provenance.gate_environment_fingerprint(other_gpu)
    )
    changed_package = deepcopy(runtime)
    changed_package["pillow"] = "13"
    assert run_provenance.gate_environment_fingerprint(runtime) != (
        run_provenance.gate_environment_fingerprint(changed_package)
    )


def _tail_contract(*, environment: str | None = None) -> dict[str, object]:
    return {
        "schema": run_provenance.TAIL_CONTRACT_SCHEMA,
        "profile": "m9-glm-tail-v1",
        "authorized_shards": run_provenance.M9_TAIL_RANGES,
        "generator": "glm",
        "generator_identity": run_provenance.M9_GLM_IDENTITY,
        "code_commit": "reviewed-commit",
        "canonical_s02_sha256": run_provenance.M9_S02_SHA256,
        "pool_manifest_sha256": run_provenance.M9_POOL_MANIFEST_SHA256,
        "prereg_sha256": run_provenance.M9_PREREG_SHA256,
        "environment_fingerprint": (environment or run_provenance.M9_5090_ENVIRONMENT_FINGERPRINT),
    }


def test_tail_contract_rejects_unregistered_range_before_artifact_access(
    tmp_path: Path,
) -> None:
    """A self-consistent manifest cannot authorize an arbitrary shard."""
    contract = tmp_path / "contract.json"
    contract.write_text(json.dumps(_tail_contract()))
    with pytest.raises(RuntimeError, match="not an authorized tail range"):
        run_provenance.load_and_verify_tail_contract(
            contract,
            project_root=tmp_path,
            generator="glm",
            shard_start=0,
            shard_end=1,
            generator_identity=run_provenance.M9_GLM_IDENTITY,
            code_commit="reviewed-commit",
            gate_path=tmp_path / "absent-gate.json",
            s02_path=tmp_path / "absent-s02.jsonl",
            image_root=tmp_path / "absent-images",
        )


def test_tail_contract_rejects_unregistered_environment_before_artifact_access(
    tmp_path: Path,
) -> None:
    """The local or a changed cloud stack cannot authorize the 5090 tail."""
    contract = tmp_path / "contract.json"
    contract.write_text(json.dumps(_tail_contract(environment="wrong-stack")))
    with pytest.raises(RuntimeError, match="approved 5090 environment"):
        run_provenance.load_and_verify_tail_contract(
            contract,
            project_root=tmp_path,
            generator="glm",
            shard_start=6154,
            shard_end=7577,
            generator_identity=run_provenance.M9_GLM_IDENTITY,
            code_commit="reviewed-commit",
            gate_path=tmp_path / "absent-gate.json",
            s02_path=tmp_path / "absent-s02.jsonl",
            image_root=tmp_path / "absent-images",
        )


def _project(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    root = tmp_path / "project"
    for directory in (root / "src", root / "config", root / "data/aokvqa"):
        directory.mkdir(parents=True)
        (directory / "content.txt").write_text(directory.name)
    (root / "scripts_run_shard.py").write_text("driver\n")
    gate = root / "data/runs/gate-glm.json"
    gate.parent.mkdir(parents=True)
    gate.write_text("{}\n")
    s02 = root / "data/runs/s02-glm-00000-00001.jsonl"
    s02.write_text("{}\n")
    images = root / "data/coco-pool"
    images.mkdir()
    (images / "000000000001.jpg").write_bytes(b"image")
    return root, gate, s02, images


def _manifest(
    root: Path,
    gate: Path,
    s02: Path,
    images: Path,
    runtime: dict[str, object],
    contract: Path,
) -> dict[str, object]:
    return {
        "schema": run_provenance.MANIFEST_SCHEMA,
        "run_id": "run-1",
        "code": {"declared_commit": "reviewed-commit"},
        "shard": {
            "generator": "glm",
            "start": 0,
            "end": 1,
            "generator_identity": "identity",
        },
        "runtime": runtime,
        "launch_contract": {
            "path": str(contract.resolve()),
            "sha256": run_provenance.file_sha256(contract),
        },
        "artifacts": {
            "driver_sha256": run_provenance.file_sha256(root / "scripts_run_shard.py"),
            "source_tree_sha256": run_provenance.tree_sha256(root / "src"),
            "config_tree_sha256": run_provenance.tree_sha256(root / "config"),
            "aokvqa_tree_sha256": run_provenance.tree_sha256(root / "data/aokvqa"),
            "gate_sha256": run_provenance.file_sha256(gate),
            "s02_ledger_sha256": run_provenance.file_sha256(s02),
            "image_root_tree_sha256": run_provenance.tree_sha256(images),
        },
        "deterministic_scope": {"on_stack": True, "cross_stack": False},
    }


def test_manifest_digest_is_stamped_only_after_live_verification(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """All pinned content and runtime values must match before a digest is returned."""
    root, gate, s02, images = _project(tmp_path)
    runtime = {"gpu": "stub"}
    monkeypatch.setattr(run_provenance, "capture_runtime", lambda: runtime)
    contract = tmp_path / "contract.json"
    contract.write_text("{}\n")
    monkeypatch.setattr(
        run_provenance,
        "load_and_verify_tail_contract",
        lambda *args, **kwargs: ({}, run_provenance.file_sha256(contract)),
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(_manifest(root, gate, s02, images, runtime, contract), sort_keys=True) + "\n"
    )
    result = run_provenance.load_and_verify_run_manifest(
        manifest,
        project_root=root,
        generator="glm",
        shard_start=0,
        shard_end=1,
        generator_identity="identity",
        code_commit="reviewed-commit",
        gate_path=gate,
        s02_path=s02,
        image_root=images,
        launch_contract_path=contract,
    )
    assert result == {
        "run_id": "run-1",
        "run_provenance_digest": hashlib.sha256(manifest.read_bytes()).hexdigest(),
    }


def test_manifest_rejects_code_changed_after_capture(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A post-capture driver edit invalidates the run before GPU observation work."""
    root, gate, s02, images = _project(tmp_path)
    runtime = {"gpu": "stub"}
    monkeypatch.setattr(run_provenance, "capture_runtime", lambda: runtime)
    contract = tmp_path / "contract.json"
    contract.write_text("{}\n")
    monkeypatch.setattr(
        run_provenance,
        "load_and_verify_tail_contract",
        lambda *args, **kwargs: ({}, run_provenance.file_sha256(contract)),
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(_manifest(root, gate, s02, images, runtime, contract)) + "\n")
    (root / "scripts_run_shard.py").write_text("changed\n")
    with pytest.raises(RuntimeError, match="driver_sha256"):
        run_provenance.load_and_verify_run_manifest(
            manifest,
            project_root=root,
            generator="glm",
            shard_start=0,
            shard_end=1,
            generator_identity="identity",
            code_commit="reviewed-commit",
            gate_path=gate,
            s02_path=s02,
            image_root=images,
            launch_contract_path=contract,
        )


def test_manifest_rejects_substituted_image_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A changed image pool invalidates the manifest before model loading."""
    root, gate, s02, images = _project(tmp_path)
    runtime = {"gpu": "stub"}
    monkeypatch.setattr(run_provenance, "capture_runtime", lambda: runtime)
    contract = tmp_path / "contract.json"
    contract.write_text("{}\n")
    monkeypatch.setattr(
        run_provenance,
        "load_and_verify_tail_contract",
        lambda *args, **kwargs: ({}, run_provenance.file_sha256(contract)),
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(_manifest(root, gate, s02, images, runtime, contract)) + "\n")
    (images / "000000000001.jpg").write_bytes(b"substituted")
    with pytest.raises(RuntimeError, match="image_root_tree_sha256"):
        run_provenance.load_and_verify_run_manifest(
            manifest,
            project_root=root,
            generator="glm",
            shard_start=0,
            shard_end=1,
            generator_identity="identity",
            code_commit="reviewed-commit",
            gate_path=gate,
            s02_path=s02,
            image_root=images,
            launch_contract_path=contract,
        )
