"""Boundary-test skeleton (V1-043): seeded leaks must fail, conformant views pass.

Consumes the FX-VIEWS fixture family from ``tests/fixtures/fixtures_v1.json``
(V1-042). Each seeded-leak fixture mutates the conformant bundle and names the
boundary check that must catch it; the conformant bundle must pass all checks.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

import pytest

from vlm_faithfulness_benchmark.views.boundary import run_boundary_checks

FIXTURES = json.loads(
    (Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "fixtures_v1.json").read_text()
)["fixtures"]

LEAK_IDS = sorted(k for k in FIXTURES if k.startswith("FX-VIEWS-LEAK-"))


def _apply_mutations(base: dict[str, Any], mutate: dict[str, Any]) -> dict[str, Any]:
    """Apply a fixture's declarative mutations to a deep-copied views bundle.

    Args:
        base: The conformant views bundle to mutate.
        mutate: Mutation spec — keys are ``<view>`` or ``<view>[<index>]``,
            values are one of ``add_field`` / ``replace_field`` / ``append``.

    Returns:
        The mutated copy; the input is never modified.
    """
    bundle = copy.deepcopy(base)
    for target, op in mutate.items():
        if target == "base":
            continue
        m = re.fullmatch(r"(\w+)(?:\[(\d+)\])?", target)
        assert m is not None, f"unparseable mutation target '{target}'"
        view, idx = m.group(1), m.group(2)
        if "append" in op:
            bundle[view].append(op["append"])
        else:
            assert idx is not None, f"row index required for field ops on '{target}'"
            row = bundle[view][int(idx)]
            row.update(op.get("add_field", {}))
            row.update(op.get("replace_field", {}))
    return bundle


def test_conformant_views_pass_all_checks() -> None:
    """The conformant separated-views bundle passes every verified check."""
    report = run_boundary_checks(FIXTURES["FX-VIEWS-CONFORMANT"]["input"])
    assert report.all_passed(), report.failing_checks()


def test_report_separates_verified_from_attested() -> None:
    """The report carries attested obligations distinct from verified checks."""
    report = run_boundary_checks(FIXTURES["FX-VIEWS-CONFORMANT"]["input"])
    assert report.attested, "attested obligations must be reported, not dropped"
    assert {c.name for c in report.verified}.isdisjoint(set(report.attested))


@pytest.mark.parametrize("leak_id", LEAK_IDS)
def test_seeded_leaks_fail_their_named_check(leak_id: str) -> None:
    """Every seeded-leak fixture is caught by exactly the check it names."""
    fx = FIXTURES[leak_id]
    base = FIXTURES[fx["mutate"]["base"]]["input"]
    bundle = _apply_mutations(base, fx["mutate"])
    report = run_boundary_checks(bundle)
    assert not report.all_passed(), f"{leak_id}: seeded leak was not detected"
    assert fx["expected"]["failing_check"] in report.failing_checks(), (
        f"{leak_id}: expected {fx['expected']['failing_check']}, got {report.failing_checks()}"
    )
