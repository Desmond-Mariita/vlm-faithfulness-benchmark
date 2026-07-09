"""Durable run ledger — the resume-capability substrate for every GPU-touching run.

Matrix rows: D-ATOM, D-ERR3 (retry only when no record exists); maintainer
GPU-run discipline (DEVELOPMENT.md): a run must survive abrupt power-off and
resume without re-producing committed records (`06a` R2/R5).

Mechanism: append-only JSONL, one line per committed record, flushed and
``fsync``-ed per commit so a power cut loses at most the in-flight record.
On load, a truncated final line (the torn-write case) is discarded — that
record was never durably committed, so re-producing it is legitimate
(design §5.3: retry is permitted exactly when no committed record exists).

Engineering note: keys are caller-chosen stable strings (instance keys plus
an artifact discriminator, e.g. ``<instance>::output_tuple``); the ledger is
deliberately ignorant of benchmark semantics.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterator, Mapping

__all__ = ["RunLedger"]


class RunLedger:
    """Append-only, fsync-durable commit ledger for resumable runs.

    One ledger file per run scope. ``commit`` is the atomic-commit boundary
    of design §5.3: a record either has its line durably on disk or it does
    not exist.
    """

    def __init__(self, path: Path) -> None:
        """Open (or create) the ledger and load committed keys.

        Args:
            path: Ledger file location; parent directories are created.
        """
        self._path = path
        self._committed: dict[str, Mapping[str, Any]] = {}
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            self._load()
        # Open for append AFTER load so a torn tail is not re-read as valid.
        self._fh = open(path, "a", encoding="utf-8")

    def _load(self) -> None:
        """Load committed entries, rolling back a torn (truncated) final line.

        A torn tail is not merely skipped: the file is **truncated** to the
        clean prefix, so the subsequent append stream cannot concatenate onto
        the fragment and corrupt an interior line.

        Raises:
            AssertionError: If an interior line is corrupt — that is disk
                corruption, not a torn write, and must halt loudly.
        """
        raw = self._path.read_text(encoding="utf-8")
        raw_lines = raw.split("\n")
        # A well-formed file ends with "\n", so the final split element is "".
        body, tail = raw_lines[:-1], raw_lines[-1]
        if tail:
            # Roll the torn write back on disk (it was never a commit).
            clean_prefix = raw[: len(raw) - len(tail)]
            with open(self._path, "w", encoding="utf-8") as fh:
                fh.write(clean_prefix)
                fh.flush()
                os.fsync(fh.fileno())
        for i, line in enumerate(body):
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as err:
                raise AssertionError(
                    f"ledger corruption at interior line {i + 1}: {line[:80]!r}"
                ) from err
            key = entry["key"]
            assert key not in self._committed, f"duplicate ledger key {key!r} (R2/R5)"
            self._committed[key] = entry["payload"]

    def is_committed(self, key: str) -> bool:
        """Return True iff ``key`` has a durably committed record."""
        return key in self._committed

    def payload(self, key: str) -> Mapping[str, Any]:
        """Return the committed payload for ``key``.

        Raises:
            AssertionError: If ``key`` is not committed.
        """
        assert key in self._committed, f"no committed record for {key!r}"
        return self._committed[key]

    def commit(self, key: str, payload: Mapping[str, Any]) -> None:
        """Durably commit one record: append, flush, fsync.

        Args:
            key: Stable record key (caller-chosen, unique per run scope).
            payload: JSON-serializable record content.

        Raises:
            AssertionError: If ``key`` is already committed — re-producing a
                committed record is a pipeline conformance error
                (`06a` R2/R5; design §5.3).
        """
        assert key not in self._committed, (
            f"conformance error: second commit for {key!r} (06a R2/R5)"
        )
        line = json.dumps({"key": key, "payload": dict(payload)}, sort_keys=True)
        assert "\n" not in line, "ledger entries must be single-line"
        self._fh.write(line + "\n")
        self._fh.flush()
        os.fsync(self._fh.fileno())
        self._committed[key] = dict(payload)

    def keys(self) -> Iterator[str]:
        """Iterate committed keys in insertion order."""
        return iter(self._committed)

    def close(self) -> None:
        """Close the underlying file handle."""
        self._fh.close()

