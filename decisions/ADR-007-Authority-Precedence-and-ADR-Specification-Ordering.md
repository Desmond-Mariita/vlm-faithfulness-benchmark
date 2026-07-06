---
Status: Accepted
Date: 2026-07-03
Accepted: 2026-07-03
Supersedes: —
Superseded-by: —
Deprecated-by: —
Charter-clause: — (governance ordering only; the Charter is unchanged)
Related:
  - docs/00_Benchmark_Charter.md
  - docs/01_Benchmark_Design.md
  - docs/conventions/decision-records.md
  - docs/conventions/versioning.md
  - docs/design/Benchmark_v1.0_Release_Plan.md
  - docs/design/Specification_Synchronization_Report.md
  - docs/design/release_evidence/spec-v1.0/role_assignments.md
---

# ADR-007: Authority Precedence and ADR–Specification Ordering

> **Decision status.** This is the V1-007 governance decision package accepted by the Benchmark
> Maintainer on 2026-07-03. It authorizes the bounded authority ordering described below.

## 1. Context

The repository already fixes several authority boundaries:

- the Charter defines benchmark identity, v1/v2 boundaries, and extraordinary-justification constraints;
- specifications define benchmark terms, artifacts, processes, and guarantees within named ownership
  boundaries;
- accepted ADRs are immutable normative records that authorize exact amendments;
- implementation executes specifications and never defines benchmark meaning; and
- plans, reviews, reports, and evidence coordinate or verify work but do not define technical meaning.

One transition remains deliberately unresolved by the accepted decision-record convention: when an ADR
is accepted but its authorized specification amendments have not yet been applied, how should an apparent
conflict between the accepted decision and the still-stale specification text be treated? The same gap
raises the inverse question after application: can a later specification edit silently override an
accepted ADR?

V1-007 fixes this ordering without changing any benchmark semantic. It does not decide an eligibility
rule, state, label, artifact, intervention, metric, or implementation method. It decides how existing
authorities are read together and what work is permitted while their texts are not synchronized.

## 2. Exact decision surface

V1-007 decides:

1. the relationship among the Charter, accepted ADRs, and owning specifications;
2. the authority of an accepted ADR during the interval before its amendments are applied;
3. the authority relationship after faithful application;
4. how conflicts among owning specifications are handled;
5. whether plans, reviews, supporting reports, timestamps, or implementation behavior can break a tie;
   and
6. what an unresolved conflict blocks.

V1-007 does **not**:

- alter the Charter or any existing ADR decision;
- create a technical hierarchy among unrelated specification domains;
- permit an ADR to redefine content outside its stated decision and amendment scope;
- decide whether any concrete future change requires an ADR (the classification gate and mandatory
  triggers continue to govern);
- change specification ownership, versioning semantics, or the normative file set; or
- authorize implementation.

## 3. Governing constraints already fixed

| Constraint | Governing source |
|---|---|
| Charter defines benchmark identity and v1/v2 boundary | Charter §§1–5, 7 |
| Charter §5 decisions require a superseding ADR naming the clause | Charter §5 |
| Specifications are authoritative over implementation | Benchmark Design §10 |
| One artifact has one owning specification | Benchmark Design §6 and invariant 8 |
| Proposed ADR authorizes nothing; only BM accepts ADRs | Decision Records §§6–7 |
| Acceptance authorizes amendments but does not itself edit specifications | Decision Records §7 |
| Accepted ADR bodies are immutable; revision requires supersession | Decision Records §8 |
| Unapplied accepted ADR amendments block release | Decision Records §8 and §10; Assurance BL8 |
| ADR application requires exact clause reconciliation and semantic-fidelity sign-off | Decision Records §10 |
| Every normative change passes classification before editing | Decision Records §§9, 12; Release Plan §2.2 |
| Owning specifications refine version classification for their domains | Versioning §2 |
| Plans do not define meaning or resolve technical-authority conflicts | Release Plan §0 |
| Review findings are inputs, not semantic decisions | Release Plan §0 |
| BM alone approves semantic/governance outcomes | Release Plan §1; role assignments |

Existing ADR practice reinforces these constraints. ADR-004, ADR-005, and ADR-006 state normative
consequences that become effective upon acceptance and list separately applied amendments. V1-009,
V1-010, and V1-011 then record faithful application rather than treating the pre-amendment specification
as permission to ignore the accepted decision.

## 4. Decision drivers

- **Construct integrity.** No process artifact or implementation may override the Charter or benchmark
  meaning.
- **Scope discipline.** An ADR must not acquire authority outside the exact decision it records.
- **Usable transition.** Acceptance must have a defined effect even before editorial application lands.
- **Specification usability.** Implementers should normally read the synchronized owning specification,
  not synthesize behavior from an unbounded pile of ADRs.
- **No silent override.** Neither stale specification text nor a later unclassified edit may erase an
  accepted decision.
- **No false conformance.** A contradiction is a blocking defect, not an invitation to choose whichever
  text is convenient.
- **Traceability.** Every transition from decision to specification must remain reconstructible.

## 5. Alternatives and normative consequences

### Alternative A — Owning specification always controls until amended

An accepted ADR would only permit future editing. Until its amendments land, the existing specification
would remain the operative technical authority even where it contradicts the accepted decision.

Consequences:

- BM acceptance would not bind technical behavior during the application interval.
- Implementers could conform to a rule the BM has formally rejected or replaced.
- Amendment delays could indefinitely postpone the effect of a decision.
- The release blocker for unapplied ADRs would prevent release but would not prevent contradictory
  implementation work before release.
- Accepted ADR language stating consequences "upon acceptance" would become misleading.

This alternative is rejected because it makes ratification operationally inert and permits work against
an accepted decision.

### Alternative B — Every accepted ADR globally outranks every specification

Accepted ADR text would be treated as the top technical authority below the Charter, without limiting
precedence to its decision scope or transition period.

Consequences:

- Implementers would need to reconstruct the current standard by reading every historical ADR.
- Broad or contextual ADR prose could displace precise owning-specification contracts outside the
  amendment list.
- Artifact ownership and specification refinement would be weakened.
- Superseded, applied, and historical decisions would remain easy to misread as free-standing alternate
  specifications.

This alternative is rejected because ADRs are decision records, not replacement specifications.

### Alternative C — Scope-bounded transition precedence with synchronized specification authority
(recommended)

The authority relation is a partial order:

1. the Charter constrains every lower authority;
2. within an accepted ADR's exact decision and amendment scope, the accepted decision governs during the
   interval before faithful application;
3. outside that exact scope, each owning specification continues to govern its domain;
4. once the amendments are faithfully applied and accepted, the owning specification is the integrated
   operational authority, read consistently with the immutable ADR that justifies the change;
5. a later specification edit cannot silently reverse an accepted ADR; changing the decision requires a
   new superseding ADR or other route explicitly authorized by the governing classification rules; and
6. any unresolved contradiction blocks the affected amendment, conformance claim, implementation work,
   and release rather than creating a selectable alternate rule.

Consequences:

- ADR acceptance has immediate, bounded governance effect.
- Stale text cannot authorize behavior contrary to the accepted decision.
- The synchronized owning specification remains the normal implementation-facing authority.
- ADRs retain immutable decision rationale and constrain later drift without becoming general-purpose
  technical specifications.
- Cross-specification conflicts are resolved through ownership and synchronization, not a global file
  ranking.

This alternative follows the existing Charter, ownership model, ADR lifecycle, application evidence,
and release-blocking rules.

### Alternative D — Most recent text or latest approval wins

Conflicts would be resolved by file modification time, commit order, document date, or latest approval.

Consequences:

- Editorial changes could silently change authority.
- Historical reports or plans could outrank normative sources merely by being newer.
- Git history and local working-tree state would become part of benchmark meaning.
- Reproducibility would depend on chronology rather than the normative manifest and explicit
  supersession.

This alternative is rejected because recency is provenance, not authority.

## 6. Proposed decision

**Adopt Alternative C: scope-bounded transition precedence with synchronized specification authority.**

Normative governance consequences upon acceptance:

- **AP1 — Charter constraint.** No ADR, specification, convention, plan, review, implementation, or
  release artifact may authorize a result forbidden by the Charter. Charter amendment follows the
  Charter's own §5/§7 route.
- **AP2 — Proposed records have no precedence.** A Proposed or Rejected ADR authorizes nothing and cannot
  override any specification.
- **AP3 — Accepted-ADR transition rule.** Within the exact decision and required-amendment scope of an
  Accepted ADR, the ADR governs over contradictory pre-application specification text. That stale text
  MUST NOT be used to implement, claim conformance, or approve release contrary to the accepted decision.
- **AP4 — Scope limit.** An ADR has no precedence outside the decision and amendment boundaries it
  actually records. Unaffected clauses remain governed by their owning specifications.
- **AP5 — Application rule.** Acceptance does not edit specifications. The authorized amendments MUST be
  applied through separate classified work, reconciled clause by clause, and approved before the
  affected specification is treated as synchronized.
- **AP6 — Post-application rule.** After faithful application, the owning specification is the integrated
  implementation-facing authority. The accepted ADR remains immutable decision provenance and a guard
  against silent reversal; the two MUST be read consistently, not as competing standards.
- **AP7 — No silent supersession.** A specification edit, convention, plan, report, or implementation
  cannot supersede an Accepted ADR. A change to the accepted decision requires a new ADR naming the prior
  record in `Supersedes:` when it replaces that decision, plus all applicable Charter/versioning review.
- **AP8 — Ownership over arbitrary rank.** Where specifications appear to conflict, the specification
  that owns the disputed term, artifact, rule, or process governs that dimension. If ownership does not
  resolve the conflict, the repository is inconsistent and the affected work stops for classification
  and synchronization; there is no generic "later document wins" rule.
- **AP9 — Supporting sources do not break ties.** Plans, reviews, audits, synchronization reports,
  completion evidence, README text, issue trackers, and implementation behavior cannot override the
  Charter, an Accepted ADR within scope, or an owning specification.
- **AP10 — Blocking effect.** An unresolved authority conflict or unapplied Accepted ADR blocks affected
  normative edits, conformance claims, implementation authorization, freeze, and release. No role may
  waive the conflict by choosing a preferred source.
- **AP11 — Traceability.** The decision index, application work item, amended clauses, and
  `adr_application_report.md` together record the transition from ADR to synchronized specification.
- **AP12 — Meaning preservation.** This ordering changes no benchmark definition, eligibility rule,
  state, label, artifact ontology, information boundary, metric, or implementation method.

## 7. Practical precedence procedure

When two sources appear to disagree, a reader or reviewer applies this procedure:

1. identify whether the Charter directly constrains the issue;
2. identify any Accepted, non-superseded ADR whose exact decision scope covers the issue;
3. identify the specification that owns the disputed dimension;
4. check whether the ADR's required amendments have been faithfully applied and accepted;
5. if applied, read the owning specification as the integrated rule and use the ADR for decision
   provenance and scope validation;
6. if not applied, follow the Accepted ADR only within its exact scope and stop affected implementation,
   conformance, freeze, or release work until synchronization lands; and
7. if no source owns or resolves the conflict, enter change classification rather than inferring a rule
   from recency, a plan, a review, or code.

## 8. Required amendments upon acceptance

The amendment list below is authorized by this accepted ADR.

1. **Decision Records Convention (`docs/conventions/decision-records.md`)**
   - §2: replace the open V1-007 deferral with AP1–AP6's scope-bounded ADR/spec relationship.
   - §7/§8: clarify that acceptance binds the decision scope but does not itself edit a specification;
     unapplied conflicts block affected work.
   - §10: retain bidirectional application evidence and add the post-application integrated-authority
     rule.
   - §13: remove authority precedence from the list of matters deliberately undecided.
2. **Versioning Convention (`docs/conventions/versioning.md`)**
   - Introduction/§8: cross-reference ADR-007 for authority ordering without changing any version train,
     compatibility rule, or change classification.
   - §9: remove authority precedence from the open-question list.
3. **Execution and Release Plan (`docs/design/Benchmark_v1.0_Release_Plan.md`)**
   - §0 and V1-007: record the accepted governance outcome and continue to disclaim technical authority;
     do not turn the plan into a normative technical source.
4. **Release evidence**
   - Record ADR-007 status, V1-007 acceptance, change classification, independent review, and decision
     index traceability.
   - Carry AP1–AP12 into freeze-time authority/ADR-application checks without rewriting historical
     reviews or the dated Specification Synchronization Report.

No amendment to the Charter, Benchmark Design, technical specifications, accepted ADR-002 through
ADR-006, benchmark semantics, or implementation is authorized.

## 9. Compatibility and versioning

This is a governance-ordering decision. It formalizes how existing authorities interact and changes no
technical meaning. It is compatible with Benchmark v1 and requires no corpus version or benchmark-line
change. Any later use of this ordering to approve a substantive technical change must independently pass
the classification, Charter, and versioning rules applicable to that change.

## 10. Acceptance and review criteria

The BM accepted ADR-007 on 2026-07-03 after independent review confirmed:

1. the Charter remains the controlling constraint and is not amended or reinterpreted;
2. accepted-ADR precedence is limited to the ADR's exact decision/amendment scope;
3. a Proposed or Rejected ADR has no authority;
4. acceptance is not falsely described as editing specification text;
5. post-application owning-specification authority does not permit silent reversal of the ADR;
6. ownership resolves only the dimension actually owned, not unrelated specification content;
7. unresolved conflicts block work instead of creating a discretionary tie-break;
8. plans, reviews, evidence, recency, and implementation behavior cannot override normative authority;
9. the amendment list is exact and changes no technical specification or existing ADR;
10. AP1–AP12 change no benchmark semantic, version meaning, or implementation method; and
11. the decision and application path remain bidirectionally traceable.

## 11. Consequences

**Positive**

- Removes ambiguity during the accepted-ADR application interval.
- Preserves specifications as the normal implementation-facing standard.
- Prevents plans, reviews, recency, or code from inventing authority.
- Makes conflicts fail closed and traceable.

**Negative / accepted costs**

- Implementers may need to consult both an accepted ADR and stale specification text during a short
  transition, but affected implementation is blocked until synchronization.
- Determining exact ADR scope requires disciplined amendment lists and application evidence.
- Cross-owner conflicts may require classification rather than an immediate textual tie-break.

## 12. Links

- [Benchmark Charter](../docs/00_Benchmark_Charter.md) §§4–5, 7
- [Benchmark Design](../docs/01_Benchmark_Design.md) §§6, 10, invariant 8
- [Decision Records Convention](../docs/conventions/decision-records.md) §§2, 6–10, 12–13
- [Versioning Convention](../docs/conventions/versioning.md) §§2, 8–9
- [Execution and Release Plan](../docs/design/Benchmark_v1.0_Release_Plan.md) §§0–2, V1-007
- [Specification Synchronization Report](../docs/design/Specification_Synchronization_Report.md)
- [ADR-002](ADR-002-Construction-Provenance-Lifecycle.md)
- [ADR-003](ADR-003-Incomplete-Candidate-Subjects.md)
- [ADR-004](ADR-004-Answer-Correctness-Eligibility.md)
- [ADR-005](ADR-005-Composite-Generator-Subject-Identity.md)
- [ADR-006](ADR-006-P6-Completeness-and-Branch-Applicability.md)
