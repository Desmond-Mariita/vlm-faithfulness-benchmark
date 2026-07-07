"""Boundary checks over separated release views (V1-043 skeleton).

Mechanically verifies four information-boundary obligations the Dataset
Specification places on the separated release views (acceptance-matrix rows
N12.2, N12.1a, N6.4, N14.2a):

- predictor-view field exclusions (`08` N12.2),
- Train-label join restriction (`08` N12.1a),
- split isolation of the training channel (`08` N6.4),
- audit-view non-joinability to scored instances (`08` N14.2a).

The report separates **verified** results (mechanically checked here) from
**attested** obligations (boundary properties no field scan can prove), per
the V1-043 verified-vs-attested reporting requirement. Obligations this
module neither verifies nor attests (e.g. `08` N12.1/N12.3 completeness,
N12.4 annotation safety, N13.2 physical separability, design D-VIEW
structural separation) are owned by other acceptance-matrix rows and are
NOT claimed here.

Engineering note: checks are pure functions over plain mappings so they can
run against any serialized view without importing pipeline code — none
exists before implementation authorization (V1-044).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

# Fields that must never appear in (nor be trivially present in) the
# predictor-visible view (`08` N12.2; `07` CC9; `06a` R6).
FORBIDDEN_PREDICTOR_FIELDS: frozenset[str] = frozenset(
    {"label", "reason_code", "state", "behavioural_state", "generator_id", "margins",
     "provenance", "sealed_provenance", "interventional_provenance",
     "correct", "correctness", "answer_correct", "correct_real"}
)

#: Split names of the two non-held-out worlds (`08` N6.1).
NON_HELD_OUT_SPLITS: frozenset[str] = frozenset({"train", "validation"})


@dataclass(frozen=True)
class CheckResult:
    """Outcome of one mechanical boundary check.

    Attributes:
        name: Stable check identifier (used by tests and evidence records).
        passed: True iff no violation was found.
        violations: Human-readable descriptions, one per violation.
    """

    name: str
    passed: bool
    violations: tuple[str, ...] = ()


@dataclass(frozen=True)
class BoundaryReport:
    """Verified-vs-attested boundary report (V1-043 reporting contract).

    Attributes:
        verified: Mechanically executed checks with their outcomes.
        attested: Obligations this module cannot verify mechanically; they
            require recorded attestation at review time (never silently
            treated as verified).
    """

    verified: tuple[CheckResult, ...]
    attested: tuple[str, ...] = field(
        default=(
            "08 N12.2 non-derivability of withheld artifacts beyond field presence",
            "08 N12.5 strict-projection property of the predictor view",
            "08 N13.2 physical/logical separability of the hidden view",
        )
    )

    def failing_checks(self) -> tuple[str, ...]:
        """Return the names of all verified checks that failed."""
        return tuple(c.name for c in self.verified if not c.passed)

    def all_passed(self) -> bool:
        """Return True iff every verified check passed."""
        return not self.failing_checks()


def check_predictor_view_exclusions(predictor_view: Sequence[Mapping[str, Any]]) -> CheckResult:
    """Verify no forbidden field is present on any predictor-view row.

    Args:
        predictor_view: Rows of the predictor-visible view (`08` §12).

    Returns:
        CheckResult named ``predictor_view_exclusions``.
    """
    violations = [
        f"row {i} ({row.get('instance_id', '?')}): forbidden field '{f}'"
        for i, row in enumerate(predictor_view)
        for f in sorted(FORBIDDEN_PREDICTOR_FIELDS & set(row))
    ]
    return CheckResult("predictor_view_exclusions", not violations, tuple(violations))


def check_train_label_join_restriction(
    train_labels: Sequence[Mapping[str, Any]],
    predictor_view: Sequence[Mapping[str, Any]],
) -> CheckResult:
    """Verify delivered labels join only to Train-split instances (`08` N12.1a).

    Validation and held-out labels are withheld from every predictor-facing
    channel; only the evaluation harness may consume them.

    Args:
        train_labels: The train-label delivery channel rows.
        predictor_view: Predictor-view rows carrying split membership.

    Returns:
        CheckResult named ``train_label_join_restriction``.
    """
    split_of = {row["instance_id"]: row.get("split") for row in predictor_view}
    violations = [
        f"label delivered for {lbl['instance_id']} in split '{split_of.get(lbl['instance_id'])}'"
        for lbl in train_labels
        if split_of.get(lbl["instance_id"]) != "train"
    ]
    return CheckResult("train_label_join_restriction", not violations, tuple(violations))


def check_split_isolation(
    train_labels: Sequence[Mapping[str, Any]],
    predictor_view: Sequence[Mapping[str, Any]],
) -> CheckResult:
    """Verify held-out worlds never leak into the training channel (`08` N6.4).

    Args:
        train_labels: The train-label delivery channel rows.
        predictor_view: Predictor-view rows carrying split membership.

    Returns:
        CheckResult named ``split_isolation``.
    """
    split_of = {row["instance_id"]: row.get("split") for row in predictor_view}
    violations = [
        f"training channel touches held-out instance {lbl['instance_id']}"
        f" (split '{split_of.get(lbl['instance_id'])}')"
        for lbl in train_labels
        if split_of.get(lbl["instance_id"]) not in NON_HELD_OUT_SPLITS
    ]
    return CheckResult("split_isolation", not violations, tuple(violations))


def check_audit_non_joinability(
    audit_view: Sequence[Mapping[str, Any]],
    predictor_view: Sequence[Mapping[str, Any]],
) -> CheckResult:
    """Verify audit identifiers are severed from scored instance ids (`08` N14.2a).

    Args:
        audit_view: Audit-view rows keyed by their own identifiers.
        predictor_view: Predictor-view rows keyed by instance ids.

    Returns:
        CheckResult named ``audit_non_joinability``.
    """
    instance_ids = {row["instance_id"] for row in predictor_view}
    violations = [
        f"audit row {i} joinable via identifier '{row.get('audit_id')}'"
        for i, row in enumerate(audit_view)
        if row.get("audit_id") in instance_ids
    ]
    return CheckResult("audit_non_joinability", not violations, tuple(violations))


def run_boundary_checks(views: Mapping[str, Any]) -> BoundaryReport:
    """Run every mechanical boundary check over a separated-views bundle.

    Args:
        views: Mapping with keys ``predictor_view``, ``train_labels``,
            ``hidden_view``, ``audit_view`` (the FX-VIEWS fixture shape).

    Returns:
        BoundaryReport with all verified results and the standing attested
        obligations.

    Raises:
        AssertionError: If a required view is missing — a malformed bundle is
            a caller defect, not a boundary finding (design §5 error model).
    """
    for key in ("predictor_view", "train_labels", "hidden_view", "audit_view"):
        assert key in views, f"views bundle missing required key '{key}'"
    predictor = views["predictor_view"]
    return BoundaryReport(
        verified=(
            check_predictor_view_exclusions(predictor),
            check_train_label_join_restriction(views["train_labels"], predictor),
            check_split_isolation(views["train_labels"], predictor),
            check_audit_non_joinability(views["audit_view"], predictor),
        )
    )
