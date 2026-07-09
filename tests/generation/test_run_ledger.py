"""Tests for the resumable run ledger (matrix rows D-ATOM, D-ERR3; GPU discipline)."""

from __future__ import annotations

from pathlib import Path

import pytest

from vlm_faithfulness_benchmark.run_ledger import RunLedger


def test_commit_then_resume_skips_committed(tmp_path: Path) -> None:
    """Resume semantics: committed records survive reload and are skipped."""
    path = tmp_path / "run.jsonl"
    ledger = RunLedger(path)
    ledger.commit("i-1::output_tuple", {"digest": "abc"})
    ledger.commit("i-2::output_tuple", {"digest": "def"})
    ledger.close()

    resumed = RunLedger(path)
    assert resumed.is_committed("i-1::output_tuple")
    assert resumed.payload("i-2::output_tuple") == {"digest": "def"}
    assert not resumed.is_committed("i-3::output_tuple")
    assert list(resumed.keys()) == ["i-1::output_tuple", "i-2::output_tuple"]
    resumed.close()


def test_double_commit_is_conformance_error(tmp_path: Path) -> None:
    """R2/R5: re-producing a committed record halts loudly."""
    ledger = RunLedger(tmp_path / "run.jsonl")
    ledger.commit("k", {"v": 1})
    with pytest.raises(AssertionError, match="second commit"):
        ledger.commit("k", {"v": 2})
    ledger.close()


def test_double_commit_rejected_across_resume(tmp_path: Path) -> None:
    """The exactly-once rule survives a restart, not just a process."""
    path = tmp_path / "run.jsonl"
    first = RunLedger(path)
    first.commit("k", {"v": 1})
    first.close()
    resumed = RunLedger(path)
    with pytest.raises(AssertionError, match="second commit"):
        resumed.commit("k", {"v": 2})
    resumed.close()


def test_torn_final_line_is_discarded_and_retryable(tmp_path: Path) -> None:
    """Power-cut simulation: a truncated tail is not a committed record."""
    path = tmp_path / "run.jsonl"
    ledger = RunLedger(path)
    ledger.commit("k1", {"v": 1})
    ledger.close()
    with open(path, "a", encoding="utf-8") as fh:
        fh.write('{"key": "k2", "payl')  # torn mid-write, no newline

    resumed = RunLedger(path)
    assert resumed.is_committed("k1")
    assert not resumed.is_committed("k2"), "a torn write is not a commit"
    resumed.commit("k2", {"v": 2})  # retry is legitimate: no record existed
    resumed.close()
    assert RunLedger(path).is_committed("k2")


def test_interior_corruption_halts_loudly(tmp_path: Path) -> None:
    """Interior (non-tail) corruption is disk damage, never silently skipped."""
    path = tmp_path / "run.jsonl"
    path.write_text('{"key": "k1", "payload": {}}\nGARBAGE-NOT-JSON\n', encoding="utf-8")
    with pytest.raises(AssertionError, match="corruption"):
        RunLedger(path)


def test_interruption_loses_at_most_inflight_record(tmp_path: Path) -> None:
    """GPU discipline rule 2: after N commits and a cut, exactly N survive."""
    path = tmp_path / "run.jsonl"
    ledger = RunLedger(path)
    for i in range(5):
        ledger.commit(f"k{i}", {"i": i})
    ledger.close()  # abrupt stop AFTER commit 5, before any 6th work
    resumed = RunLedger(path)
    assert sum(1 for _ in resumed.keys()) == 5
    resumed.close()
