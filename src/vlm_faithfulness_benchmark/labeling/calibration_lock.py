"""Hash-verifying loader for the accepted production calibration lock."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from vlm_faithfulness_benchmark.gating.condition_b import (
    CONTENT_TOKEN_PATTERN,
    DRIFT_INSTRUMENT_ID,
    load_stopwords,
)

__all__ = ["CalibrationLock", "load_calibration_lock"]

_SCHEMA = "vlm-faithfulness-calibration-lock-v1"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _mapping(value: object, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RuntimeError(f"calibration lock field {field!r} must be an object")
    return value


def _string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise RuntimeError(f"calibration lock field {field!r} must be a non-empty string")
    return value


@dataclass(frozen=True, slots=True)
class CalibrationLock:
    """Verified values and artifacts consumed by production adjudication."""

    lock_id: str
    lock_sha256: str
    k: int
    theta_b: float
    saliency_floor: float
    stopwords: frozenset[str]
    stopwords_sha256: str
    coherence_registry_path: Path
    coherence_registry_sha256: str
    spec_versions: dict[str, str]


def load_calibration_lock(path: Path, repo_root: Path) -> CalibrationLock:
    """Load the lock, verify every pinned source, and reject stale semantics."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"cannot load calibration lock {path}") from error
    root = _mapping(document, "root")
    if root.get("schema") != _SCHEMA or root.get("status") != "accepted":
        raise RuntimeError("production requires an accepted calibration-lock-v1")

    artifacts = root.get("source_artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise RuntimeError("calibration lock has no source artifacts")
    role_hashes: dict[str, str] = {}
    for raw_reference in artifacts:
        reference = _mapping(raw_reference, "source_artifacts[]")
        role = _string(reference.get("role"), "source role")
        relative = _string(reference.get("path"), "source path")
        expected = _string(reference.get("sha256"), "source sha256")
        source_path = repo_root / relative
        if not source_path.is_file() or _sha256(source_path) != expected:
            raise RuntimeError(f"calibration source hash mismatch for {relative}")
        if role in role_hashes:
            raise RuntimeError(f"duplicate calibration source role {role!r}")
        role_hashes[role] = expected

    condition_a = _mapping(root.get("condition_a"), "condition_a")
    condition_b = _mapping(root.get("condition_b"), "condition_b")
    saliency = _mapping(root.get("saliency"), "saliency")
    coherence = _mapping(root.get("coherence"), "coherence")
    stopword_ref = _mapping(condition_b.get("stopwords"), "condition_b.stopwords")
    registry_ref = _mapping(coherence.get("registry"), "coherence.registry")

    k = condition_a.get("k")
    theta_b = condition_b.get("theta_b")
    saliency_floor = saliency.get("floor")
    if type(k) is not int or k != 3:
        raise RuntimeError("production calibration lock must pin accepted k=3")
    if not isinstance(theta_b, float) or theta_b != 0.7558573853989813:
        raise RuntimeError("production calibration lock has an unaccepted theta_b")
    if not isinstance(saliency_floor, float) or saliency_floor != 0.625:
        raise RuntimeError("production calibration lock has an unaccepted saliency floor")
    if condition_b.get("instrument") != DRIFT_INSTRUMENT_ID:
        raise RuntimeError("production calibration lock selects the wrong drift instrument")
    if condition_a.get("rule") != "flip_count >= k":
        raise RuntimeError("production calibration lock selects the wrong Condition A rule")
    if condition_a.get("source_role") != "prereg-v3":
        raise RuntimeError("Condition A is not bound to prereg-v3")
    if condition_b.get("tokenizer_regex") != CONTENT_TOKEN_PATTERN:
        raise RuntimeError("production calibration lock selects the wrong tokenizer")
    if condition_b.get("normalization") != "lowercase":
        raise RuntimeError("production calibration lock selects the wrong normalization")
    if condition_b.get("collection") != "set":
        raise RuntimeError("production calibration lock must use set Jaccard")
    if condition_b.get("rule") != "targeted_drift >= theta_b":
        raise RuntimeError("production calibration lock selects the wrong Condition B rule")
    if condition_b.get("threshold_source_role") != "confirm-gate-result":
        raise RuntimeError("theta_b is not bound to the confirmatory gate result")
    if condition_b.get("empty_union_policy") != "conformance-error":
        raise RuntimeError("unknown Jaccard empty-union policy")
    if saliency.get("route_e5_rule") != "max_drop < floor":
        raise RuntimeError("production saliency comparison must be strict")
    if saliency.get("equality_is_locatable") is not True:
        raise RuntimeError("production saliency equality must remain locatable")
    if saliency.get("source_role") != "confirm-observations":
        raise RuntimeError("saliency floor is not bound to confirm observations")

    stopword_path_value = _string(stopword_ref.get("path"), "stopword path")
    stopword_hash = _string(stopword_ref.get("sha256"), "stopword sha256")
    registry_path_value = _string(registry_ref.get("path"), "registry path")
    registry_hash = _string(registry_ref.get("sha256"), "registry sha256")
    if role_hashes.get("stopwords") != stopword_hash:
        raise RuntimeError("stopword reference is not source-bound")
    if role_hashes.get("coherence-registry") != registry_hash:
        raise RuntimeError("coherence registry reference is not source-bound")

    required_roles = {
        "prereg-v1",
        "prereg-v2",
        "prereg-v3",
        "stopwords",
        "coherence-registry",
        "confirm-gate-result",
        "confirm-s02",
        "confirm-observations",
        "label-specification",
        "generation-pipeline",
        "superseded-k-calibration",
    }
    if set(role_hashes) != required_roles:
        raise RuntimeError("calibration lock source-role set is incomplete or unexpected")
    superseded = next(
        reference
        for reference in artifacts
        if isinstance(reference, dict) and reference.get("role") == "superseded-k-calibration"
    )
    if superseded.get("disposition") != "descriptive-only; production use forbidden":
        raise RuntimeError("superseded k calibration is not explicitly forbidden in production")

    stopword_path = repo_root / stopword_path_value
    registry_path = repo_root / registry_path_value
    return CalibrationLock(
        lock_id=_string(root.get("id"), "id"),
        lock_sha256=_sha256(path),
        k=k,
        theta_b=theta_b,
        saliency_floor=saliency_floor,
        stopwords=load_stopwords(stopword_path),
        stopwords_sha256=stopword_hash,
        coherence_registry_path=registry_path,
        coherence_registry_sha256=registry_hash,
        spec_versions={
            "06_Label_Specification": f"v1.0@sha256:{role_hashes['label-specification']}",
            "07_Label_Generation_Pipeline": f"v1.0@sha256:{role_hashes['generation-pipeline']}",
            "calibration_lock": f"{_string(root.get('id'), 'id')}@sha256:{_sha256(path)}",
        },
    )
