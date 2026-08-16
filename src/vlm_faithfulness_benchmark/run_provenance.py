"""Content-addressed execution provenance for GPU mass-run shards.

The composite generator identity intentionally describes the model-facing subject;
it does not describe the machine that executed it.  This module supplies the latter
as a separate, immutable run manifest.  Every observation produced by a mass-run
shard references the SHA-256 digest of that manifest.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

__all__ = [
    "ACCEPTANCE_CONTRACT_SCHEMA",
    "MANIFEST_SCHEMA",
    "TAIL_CONTRACT_SCHEMA",
    "capture_runtime",
    "environment_class",
    "gate_environment_fingerprint",
    "file_sha256",
    "load_and_verify_tail_contract",
    "load_and_verify_run_manifest",
    "tree_sha256",
    "verify_reviewed_git_content",
]

MANIFEST_SCHEMA = "vlm-faithfulness-run-provenance-v1"
TAIL_CONTRACT_SCHEMA = "vlm-faithfulness-m9-glm-tail-contract-v1"
ACCEPTANCE_CONTRACT_SCHEMA = "vlm-faithfulness-m9-glm-acceptance-contract-v1"
M9_TAIL_RANGES = [[6154, 7577], [7577, 9000]]
M9_ACCEPTANCE_RANGES = [[2000, 2050]]
M9_ACCEPTANCE_LEGS = {"5090-a", "5090-b", "3090-a", "3090-b"}
M9_S02_SHA256 = "e2f35a869cc874504c4942f30804048ac40de59caaafe8f2c7528262b066408e"
M9_POOL_MANIFEST_SHA256 = "3f34d868d859fa99404c0dcd8a4a1e3b24f84a7cd6420b25893af2133bc8e926"
M9_PREREG_SHA256 = "a4e04011e22990c2d540c8e7b935c7ee0036b66925b0f1856a2683507a4a65dc"
M9_CAL50_SHA256 = "c0c104f237bf1e24539a2fd2a0a491f3da79ba0d17d6fe5a2d70423729bdcc46"
M9_IMAGE_ROOT_TREE_SHA256 = "035b7165c6e4892c2df61f0b4bdb8eafa22d1d2a590d8ce1c2de4ed062362a84"
M9_5090_ENVIRONMENT_FINGERPRINT = "a2836dd9bd44cbb5e211008eb9a97125d7f6d71cbe2e7dd4edb943197317b539"
M9_TAIL_5090_ENVIRONMENT_FINGERPRINTS = {
    M9_5090_ENVIRONMENT_FINGERPRINT,
    # Replacement host after the original provider became repeatedly unavailable:
    # Python 3.12.3, torch 2.12.0+cu130, transformers 5.15.0, CUDA 13.0,
    # cuDNN 92000, driver 580.126.09, RTX 5090 compute capability 12.0.
    "fde8af0f15b4f15ad49592aa3bc574ff7c4b4fde0b07733a6817ce75d6c3d24a",
}
M9_GLM_IDENTITY = (
    '{"decoding":"greedy;beams=1;max_new_tokens=256;enable_thinking=False",'
    '"dtype":"bfloat16","extraction_contract":"aokvqa-mc-glm-v2",'
    '"image_preprocessing":"pil-rgb-native","model":"zai-org/GLM-4.6V-Flash",'
    '"option_scorer":"option-letter-logprob-glm-v1",'
    '"prompt_template":"aokvqa-mc-glm-v2",'
    '"revision":"411bb4d77144a3f03accbf4b780f5acb8b7cde4e"}'
)


def _require(condition: bool, message: str) -> None:
    """Raise unconditionally when a provenance invariant is false."""
    if not condition:
        raise RuntimeError(message)


def file_sha256(path: Path) -> str:
    """Return the lowercase SHA-256 digest of one file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_sha256(root: Path) -> str:
    """Hash a tree by relative path and content, excluding generated caches."""
    digest = hashlib.sha256()
    paths = sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and not any(part.endswith(".egg-info") for part in path.parts)
        and path.suffix != ".pyc"
    )
    for path in paths:
        relative = path.relative_to(root).as_posix().encode("utf-8")
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(bytes.fromhex(file_sha256(path)))
    return digest.hexdigest()


def _nvidia_row(physical_selector: str) -> dict[str, str]:
    query = "index,uuid,name,driver_version"
    result = subprocess.run(
        [
            "nvidia-smi",
            f"--id={physical_selector}",
            f"--query-gpu={query}",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    rows = [row.strip() for row in result.stdout.splitlines() if row.strip()]
    _require(len(rows) == 1, f"expected one visible GPU provenance row, got {rows!r}")
    values = [value.strip() for value in rows[0].split(",", 3)]
    _require(len(values) == 4, f"unexpected nvidia-smi provenance row: {rows[0]!r}")
    return dict(zip(("physical_index", "uuid", "name", "driver"), values, strict=True))


def capture_runtime() -> dict[str, Any]:
    """Capture the runtime and selected physical GPU used by this process."""
    import numpy as np
    import PIL
    import torch
    import transformers

    visible = os.environ.get("CUDA_VISIBLE_DEVICES", "")
    selectors = [item.strip() for item in visible.split(",") if item.strip()]
    _require(
        len(selectors) == 1,
        (
            "mass-run provenance requires exactly one CUDA_VISIBLE_DEVICES selector, "
            f"got {visible!r}"
        ),
    )
    _require(torch.cuda.is_available(), "CUDA is unavailable while capturing GPU provenance")
    _require(
        torch.cuda.device_count() == 1,
        ("the shard process must see exactly one GPU after CUDA_VISIBLE_DEVICES filtering"),
    )
    gpu = _nvidia_row(selectors[0])
    gpu["compute_capability"] = ".".join(str(v) for v in torch.cuda.get_device_capability(0))
    gpu["torch_visible_name"] = torch.cuda.get_device_name(0)
    return {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "python_executable": str(Path(sys.executable).resolve()),
        "numpy": np.__version__,
        "pillow": PIL.__version__,
        "torch": torch.__version__,
        "torch_cuda": torch.version.cuda,
        "cudnn": torch.backends.cudnn.version(),
        "transformers": transformers.__version__,
        "cuda_visible_devices": visible,
        "gpu": gpu,
    }


def gate_environment_fingerprint(runtime: Mapping[str, Any] | None = None) -> str:
    """Hash the runtime *class* for a per-environment CAL-50 authorization.

    Hostname, GPU UUID/index, executable path, and ``CUDA_VISIBLE_DEVICES`` are
    deliberately excluded so identical GPUs on one rented host share one gate.
    Exact per-process/physical-GPU provenance remains in each run manifest.
    """
    environment = environment_class(runtime if runtime is not None else capture_runtime())
    encoded = json.dumps(environment, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def environment_class(runtime: Mapping[str, Any]) -> dict[str, Any]:
    """Flatten the runtime fields that define a CAL-50 environment class."""
    observed = dict(runtime)
    gpu = observed["gpu"]
    _require(isinstance(gpu, Mapping), "runtime has no GPU provenance object")
    return {
        "platform": observed["platform"],
        "python": observed["python"],
        "numpy": observed["numpy"],
        "pillow": observed["pillow"],
        "torch": observed["torch"],
        "torch_cuda": observed["torch_cuda"],
        "cudnn": observed["cudnn"],
        "transformers": observed["transformers"],
        "gpu_name": gpu["name"],
        "compute_capability": gpu["compute_capability"],
        "driver": gpu["driver"],
    }


def _verify_m9_cal50_gate(
    gate: Mapping[str, Any], *, generator_identity: str, environment_fingerprint: str
) -> None:
    """Verify that a gate artifact records the fixed preregistered CAL-50 test."""
    _require_equal(gate.get("prereg"), "prereg-m9-v1", "gate preregistration")
    _require_equal(gate.get("cal50_sha256"), M9_CAL50_SHA256, "gate CAL-50 slice")
    _require_equal(gate.get("identity"), generator_identity, "gate identity")
    _require_equal(gate.get("environment_fingerprint"), environment_fingerprint, "gate environment")
    _require_equal(gate.get("n"), 50, "gate sample size")
    parsed = gate.get("parsed")
    agree = gate.get("agree")
    _require(isinstance(parsed, int) and 0 <= parsed <= 50, "invalid gate parsed count")
    _require(isinstance(agree, int) and 0 <= agree <= parsed, "invalid gate agreement count")
    parseability = round(parsed / 50, 4)
    agreement = round(agree / parsed, 4) if parsed else 0.0
    if parsed:
        z = 1.96
        p = agree / parsed
        denominator = 1 + z * z / parsed
        center = (p + z * z / (2 * parsed)) / denominator
        half = (z * (p * (1 - p) / parsed + z * z / (4 * parsed * parsed)) ** 0.5) / denominator
        wilson95 = [round(max(0.0, center - half), 4), round(min(1.0, center + half), 4)]
    else:
        wilson95 = [0.0, 0.0]
    _require_equal(gate.get("parseability"), parseability, "gate parseability")
    _require_equal(gate.get("agreement"), agreement, "gate agreement")
    _require_equal(gate.get("agreement_wilson95"), wilson95, "gate Wilson interval")
    expected_passed = parseability >= 0.90 and agreement >= 0.60
    _require_equal(gate.get("passed"), expected_passed, "gate pass decision")
    _require(expected_passed, "contract gate did not pass")


def _require_equal(actual: object, expected: object, label: str) -> None:
    _require(
        actual == expected,
        f"run provenance mismatch for {label}: {actual!r} != {expected!r}",
    )


def verify_reviewed_git_content(project_root: Path, code_commit: str) -> None:
    """Bind the runtime paths to an exact, clean checked-out Git commit.

    Runtime ledgers/logs may make the overall worktree dirty. Only the executable
    mass-run surface is checked, and both tracked modifications and untracked files
    within that surface are rejected.
    """
    head = subprocess.run(
        ["git", "-C", str(project_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    _require_equal(head, code_commit, "checked-out Git commit")
    scope = [
        "scripts_run_shard.py",
        "scripts_capture_run_manifest.py",
        "scripts_create_acceptance_contract.py",
        "scripts_create_tail_launch_contract.py",
        "scripts_validate_glm_merge.py",
        "scripts_verify_legacy_digests.py",
        "src",
        "config",
        "data/aokvqa",
    ]
    tracked = subprocess.run(
        ["git", "-C", str(project_root), "diff", "--quiet", code_commit, "--", *scope]
    )
    _require(tracked.returncode == 0, "reviewed runtime has tracked modifications")
    untracked = subprocess.run(
        [
            "git",
            "-C",
            str(project_root),
            "ls-files",
            "--others",
            "--exclude-standard",
            "--",
            *scope,
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    _require(not untracked, f"reviewed runtime has untracked files: {untracked!r}")


def load_and_verify_tail_contract(
    path: Path,
    *,
    project_root: Path,
    generator: str,
    shard_start: int,
    shard_end: int,
    generator_identity: str,
    code_commit: str,
    gate_path: Path,
    s02_path: Path,
    image_root: Path,
) -> tuple[Mapping[str, Any], str]:
    """Validate a tail or acceptance contract against immutable M9 policy and live bytes.

    The public name is retained for compatibility with the reviewed tail launcher. The
    contract profile determines whether this is a publication tail shard or one of the
    four pre-registered reproducibility-probe legs.
    """
    raw = path.read_bytes()
    contract = json.loads(raw)
    _require(isinstance(contract, Mapping), "tail launch contract must be an object")
    profile = contract.get("profile")
    if profile == "m9-glm-tail-v1":
        _require_equal(contract.get("schema"), TAIL_CONTRACT_SCHEMA, "contract.schema")
        _require_equal(contract.get("authorized_shards"), M9_TAIL_RANGES, "authorized shards")
        _require(
            [shard_start, shard_end] in M9_TAIL_RANGES,
            "shard is not an authorized tail range",
        )
        expected_environment = contract.get("environment_fingerprint")
        _require(
            expected_environment in M9_TAIL_5090_ENVIRONMENT_FINGERPRINTS,
            "tail contract is not bound to an approved 5090 environment",
        )
        environment_label = "approved 5090 environment"
    elif profile == "m9-glm-repro-acceptance-v1":
        _require_equal(contract.get("schema"), ACCEPTANCE_CONTRACT_SCHEMA, "contract.schema")
        _require_equal(contract.get("authorized_shards"), M9_ACCEPTANCE_RANGES, "authorized shards")
        _require(
            [shard_start, shard_end] in M9_ACCEPTANCE_RANGES,
            "shard is not the registered CAL-50 acceptance range",
        )
        leg = contract.get("acceptance_leg")
        _require(leg in M9_ACCEPTANCE_LEGS, "contract has an invalid acceptance leg")
        _require_equal(contract.get("cal50_sha256"), M9_CAL50_SHA256, "registered CAL-50")
        expected_environment = contract.get("environment_fingerprint")
        _require(
            isinstance(expected_environment, str) and bool(expected_environment),
            "acceptance contract has no environment fingerprint",
        )
        environment_label = "acceptance environment"
        runtime_class = contract.get("runtime_class")
        _require(isinstance(runtime_class, Mapping), "acceptance contract has no runtime class")
        expected_gpu = (
            "NVIDIA GeForce RTX 5090" if str(leg).startswith("5090-") else "NVIDIA GeForce RTX 3090"
        )
        _require_equal(runtime_class.get("gpu_name"), expected_gpu, "acceptance GPU class")
    else:
        raise RuntimeError(f"unknown launch contract profile: {profile!r}")
    _require_equal(contract.get("generator"), generator, "contract.generator")
    _require_equal(generator, "glm", "authorized generator")
    _require_equal(generator_identity, M9_GLM_IDENTITY, "registered GLM identity")
    _require_equal(contract.get("generator_identity"), generator_identity, "contract identity")
    _require_equal(contract.get("code_commit"), code_commit, "contract code commit")
    _require_equal(contract.get("canonical_s02_sha256"), M9_S02_SHA256, "canonical S02")
    _require_equal(
        contract.get("pool_manifest_sha256"),
        M9_POOL_MANIFEST_SHA256,
        "registered pool manifest",
    )
    _require_equal(contract.get("prereg_sha256"), M9_PREREG_SHA256, "registered prereg")
    _require_equal(contract.get("environment_fingerprint"), expected_environment, environment_label)
    verify_reviewed_git_content(project_root, code_commit)
    gate = json.loads(gate_path.read_text())
    _require(isinstance(gate, Mapping), "gate artifact must be an object")
    live_runtime = capture_runtime()
    live_environment = gate_environment_fingerprint(live_runtime)
    _verify_m9_cal50_gate(
        gate,
        generator_identity=generator_identity,
        environment_fingerprint=str(expected_environment),
    )
    _require_equal(live_environment, expected_environment, "live environment")
    if profile == "m9-glm-tail-v1":
        _require_equal(
            contract.get("runtime_class"),
            environment_class(live_runtime),
            "runtime class",
        )
    live = {
        "driver_sha256": file_sha256(project_root / "scripts_run_shard.py"),
        "source_tree_sha256": tree_sha256(project_root / "src"),
        "config_tree_sha256": tree_sha256(project_root / "config"),
        "aokvqa_tree_sha256": tree_sha256(project_root / "data/aokvqa"),
        "gate_sha256": file_sha256(gate_path),
        "s02_ledger_sha256": file_sha256(s02_path),
        "image_root_tree_sha256": tree_sha256(image_root),
    }
    for field, actual in live.items():
        _require_equal(contract.get(field), actual, f"contract.{field}")
    _require_equal(
        live["image_root_tree_sha256"],
        M9_IMAGE_ROOT_TREE_SHA256,
        "registered image root",
    )
    _require_equal(live["s02_ledger_sha256"], M9_S02_SHA256, "live canonical S02")
    _require_equal(
        file_sha256(project_root / "config/pool_manifest_v1.json"),
        M9_POOL_MANIFEST_SHA256,
        "live pool manifest",
    )
    _require_equal(
        file_sha256(project_root / "config/prereg_m9_v1.json"),
        M9_PREREG_SHA256,
        "live prereg",
    )
    return contract, hashlib.sha256(raw).hexdigest()


def load_and_verify_run_manifest(
    path: Path,
    *,
    project_root: Path,
    generator: str,
    shard_start: int,
    shard_end: int,
    generator_identity: str,
    code_commit: str,
    gate_path: Path,
    s02_path: Path,
    image_root: Path,
    launch_contract_path: Path,
) -> dict[str, str]:
    """Verify an immutable run manifest against the executing shard.

    Returns the two values that are stamped into every newly committed row:
    ``run_id`` and the exact-file ``run_provenance_digest``.
    """
    raw = path.read_bytes()
    manifest = json.loads(raw)
    _require(isinstance(manifest, Mapping), "run manifest must be a JSON object")
    _require_equal(manifest.get("schema"), MANIFEST_SCHEMA, "schema")
    run_id = manifest.get("run_id")
    _require(isinstance(run_id, str) and bool(run_id), "run manifest has no non-empty run_id")
    code = manifest.get("code")
    _require(isinstance(code, Mapping), "run manifest has no code object")
    _require_equal(code.get("declared_commit"), code_commit, "code.declared_commit")

    shard = manifest.get("shard")
    _require(isinstance(shard, Mapping), "run manifest has no shard object")
    _require_equal(shard.get("generator"), generator, "shard.generator")
    _require_equal(shard.get("start"), shard_start, "shard.start")
    _require_equal(shard.get("end"), shard_end, "shard.end")
    _require_equal(shard.get("generator_identity"), generator_identity, "generator identity")

    _, contract_digest = load_and_verify_tail_contract(
        launch_contract_path,
        project_root=project_root,
        generator=generator,
        shard_start=shard_start,
        shard_end=shard_end,
        generator_identity=generator_identity,
        code_commit=code_commit,
        gate_path=gate_path,
        s02_path=s02_path,
        image_root=image_root,
    )
    contract_ref = manifest.get("launch_contract")
    _require(isinstance(contract_ref, Mapping), "run manifest has no launch contract")
    _require_equal(contract_ref.get("sha256"), contract_digest, "launch contract digest")
    _require_equal(
        Path(str(contract_ref.get("path"))).resolve(),
        launch_contract_path.resolve(),
        "launch contract path",
    )

    artifacts = manifest.get("artifacts")
    _require(isinstance(artifacts, Mapping), "run manifest has no artifacts object")
    checks = {
        "driver_sha256": file_sha256(project_root / "scripts_run_shard.py"),
        "source_tree_sha256": tree_sha256(project_root / "src"),
        "config_tree_sha256": tree_sha256(project_root / "config"),
        "aokvqa_tree_sha256": tree_sha256(project_root / "data/aokvqa"),
        "gate_sha256": file_sha256(gate_path),
        "s02_ledger_sha256": file_sha256(s02_path),
        "image_root_tree_sha256": tree_sha256(image_root),
    }
    for field, actual in checks.items():
        _require_equal(artifacts.get(field), actual, f"artifacts.{field}")

    runtime = manifest.get("runtime")
    _require(isinstance(runtime, Mapping), "run manifest has no runtime object")
    live_runtime = capture_runtime()
    _require_equal(dict(runtime), live_runtime, "runtime")

    scope = manifest.get("deterministic_scope")
    _require(isinstance(scope, Mapping), "run manifest has no deterministic_scope object")
    _require(scope.get("on_stack") is True, "manifest must declare on-stack deterministic scope")
    _require(scope.get("cross_stack") is False, "manifest must not claim cross-stack determinism")
    return {
        "run_id": run_id,
        "run_provenance_digest": hashlib.sha256(raw).hexdigest(),
    }
