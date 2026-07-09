"""Tests for the S02 harness (matrix rows S02-post/fail, CC4, D-ATOM, D-ERR3)."""

from __future__ import annotations

from pathlib import Path

import pytest

from vlm_faithfulness_benchmark.generation.harness import (
    GenerationOutcome,
    run_s02,
)
from vlm_faithfulness_benchmark.generation.identity import (
    GeneratorId,
    InstanceId,
    SourceRecordId,
)
from vlm_faithfulness_benchmark.ingestion.aokvqa import SourceRecord
from vlm_faithfulness_benchmark.run_ledger import RunLedger

GEN_ID = GeneratorId.from_mapping({"model": "stub", "revision": "test"})


def _record(i: int) -> SourceRecord:
    return SourceRecord(
        identity=SourceRecordId("aokvqa", f"q-{i}"),
        image_ref=f"coco/{i}",
        question="what?",
        options=("a", "b"),
        annotations={"gold_answer_idx": 0},
    )


def test_commits_output_tuple_as_emitted_with_digest(tmp_path: Path) -> None:
    """S02-post: exact emitted content committed once, digest attached."""
    ledger = RunLedger(tmp_path / "run.jsonl")
    result = run_s02(
        [_record(1)],
        lambda r: GenerationOutcome("a", "because it is a"),
        GEN_ID,
        ledger,
    )
    assert result == {"committed": 1, "skipped": 0}
    key = f"{InstanceId(GEN_ID, _record(1).identity).key()}::output_tuple"
    payload = ledger.payload(key)
    assert payload["output_tuple"] == {"chosen_answer": "a", "rationale": "because it is a"}
    assert len(payload["baseline_digest"]) == 64
    assert payload["rip"] == "RIP-1.0.0"
    ledger.close()


def test_incomplete_generation_is_retained_not_dropped(tmp_path: Path) -> None:
    """S02-fail/ADR-003: absent rationale commits as an incomplete tuple."""
    ledger = RunLedger(tmp_path / "run.jsonl")
    run_s02([_record(1)], lambda r: GenerationOutcome("a", None), GEN_ID, ledger)
    key = f"{InstanceId(GEN_ID, _record(1).identity).key()}::output_tuple"
    payload = ledger.payload(key)
    assert payload["output_tuple"]["rationale"] is None
    ledger.close()


def test_resume_skips_committed_and_never_reinvokes(tmp_path: Path) -> None:
    """GPU discipline / R2: resumed runs skip committed instances entirely."""
    path = tmp_path / "run.jsonl"
    calls: list[str] = []

    def gen(record: SourceRecord) -> GenerationOutcome:
        calls.append(record.identity.record_id)
        return GenerationOutcome("a", "a fine rationale here")

    ledger = RunLedger(path)
    run_s02([_record(1), _record(2)], gen, GEN_ID, ledger)
    ledger.close()

    resumed = RunLedger(path)
    result = run_s02([_record(1), _record(2), _record(3)], gen, GEN_ID, resumed)
    assert result == {"committed": 1, "skipped": 2}
    assert calls == ["q-1", "q-2", "q-3"], "committed instances were re-invoked"
    resumed.close()


def test_infrastructure_failure_leaves_no_record_and_is_retryable(tmp_path: Path) -> None:
    """D-ERR3: an infra exception propagates; the instance stays uncommitted."""
    path = tmp_path / "run.jsonl"
    boom = RuntimeError("CUDA OOM")

    def failing(record: SourceRecord) -> GenerationOutcome:
        raise boom

    ledger = RunLedger(path)
    with pytest.raises(RuntimeError, match="OOM"):
        run_s02([_record(1)], failing, GEN_ID, ledger)
    ledger.close()

    resumed = RunLedger(path)
    result = run_s02(
        [_record(1)], lambda r: GenerationOutcome("b", "recovered rationale text"), GEN_ID, resumed
    )
    assert result == {"committed": 1, "skipped": 0}
    resumed.close()
