---
Status: Accepted
Date: 2026-07-02
Accepted: 2026-07-02
Supersedes: —
Superseded-by: —
Deprecated-by: —
Charter-clause: — (eligibility-branch consistency; no change to label meaning)
Related:
  - docs/03_Problem_Definition.md
  - docs/05_Formal_Definitions.md
  - docs/06_Label_Specification.md
  - docs/06a_Benchmark_Data_Model.md
  - docs/07_Label_Generation_Pipeline.md
  - docs/08_Dataset_Specification.md
  - docs/11_Benchmark_Assurance.md
  - docs/design/Specification_Synchronization_Report.md
  - decisions/ADR-004-Answer-Correctness-Eligibility.md
  - decisions/ADR-005-Composite-Generator-Subject-Identity.md
---

# ADR-006: P6 Completeness and Branch Applicability

> **Decision status.** This V1-006 decision package was accepted by the Benchmark Maintainer on
> 2026-07-02. Its amendment list is applied separately by V1-011; acceptance authorizes no
> implementation work.

## 1. Context and exact decision surface

Label Specification §3 makes P6 (licensed causal reading) one of the preconditions that **every**
eligible instance must satisfy. Section 9 maps failure of that precondition to E6, with no Label and no
Behavioural State. This includes both possible labelled paths: S1/D1 when Condition A is determinately
false, and S2 or S3 when Condition A is true and Condition B is assessed.

The Pipeline's branch table and explanatory rule already state the same outcome (`07` §6): P6 must hold
before any Behavioural State is assigned; an A-false candidate that fails P6 routes E6 rather than S1.
However, the stage contracts remain incomplete. S07 says a determinate A-false result goes to the S1
branch, while S10 currently requires both S06 and S09 observations. S09 exists only on the A-true path.
Read literally, the S10 precondition therefore cannot be met on the A-false path that §6 requires S10 to
gate.

V1-006 decides only:

1. whether P6 remains a universal eligibility precondition on both the A-false and A-true branches; and
2. whether the P6 determination consumes the branch-appropriate intervention/control evidence needed to
   license the causal claim made on that branch.

It does **not** decide the concrete controls, intervention methods, thresholds, number of observations,
per-question-type validity tests, serialization, E6 publication policy, Condition-B granularity, or a
new route/state/label. Those remain owned by the existing specifications and implementation-profile
work.

## 2. Governing constraints

- **Eligibility is conjunctive.** A Label may be assigned only when P1–P6 all hold (Label Specification
  §3); failure of P6 is E6 (Label Specification §9).
- **A negative Condition A is causal.** Image-dependence is the chosen answer's causal reliance on visual
  input as revealed by intervention (Formal Definitions §13). A determinate absence of that reliance is
  still an intervention-derived causal reading.
- **No forced verdict.** A failed determinacy or causal-license precondition yields no label and no
  Behavioural State (Label Specification §3, §9, I7).
- **D1 has fixed meaning.** S1/D1 asserts a determinate absence of image-dependence; E4 is
  indeterminacy, and E6 is an unlicensed causal reading (Label Specification §6, §8.1, §9).
- **Existing routes are exhaustive.** The accepted taxonomy is P1–P6 / E1–E6 and S1–S3; ADR-004 C1 and
  C5 preserve those routes and specifically retain E6 for unlicensed causal readings.
- **Traceability is mandatory.** Provenance records control applicability/results and P1–P6/E1–E6
  outcomes; a Label must be reconstructible from them (Data Model §3.7, T1–T2).
- **Synchronization finding.** Specification Synchronization Report SPA-004 and SYNC-06 identify the
  meaning-preserving resolution: P6 gates A-false as well as A-true; narrowing P6 to A-true would require
  a semantic decision.

## 3. Alternatives and normative consequences

### Alternative A — P6 gates every labelled branch using branch-appropriate evidence (recommended)

P6 remains a universal eligibility precondition. After Condition A is determinate, S10 evaluates whether
the available, applicable controls license the causal reading needed on the active branch:

- **A false:** the relevant claim is the determinate absence of answer image-dependence. S10 consumes the
  answer-side intervention and control evidence available from S06/S07; it does not require S09 or a
  Condition-B determination.
- **A true:** S10 consumes the intervention/control evidence required to license the answer-side and
  evidence-matched rationale-side causal reading before S11 determines Condition B.

Consequences:

- A false + P6 holds → S1 → `unfaithful`/D1.
- A false + P6 fails → E6, with no state and no label.
- A true + P5 holds + P6 holds → Condition B is determined, yielding S2 or S3.
- A true + P6 fails → E6, with no state and no label.
- No new gate, E-code, state, label, reason code, or predictor-visible field is introduced.
- The concrete meaning of "applicable controls" remains operational and must be pinned by the Reference
  Implementation Profile; this ADR fixes branch coverage, not a control algorithm.

This alternative follows the existing authority in Label Specification §3/§9 and the Pipeline §6 rule.

### Alternative B — P6 gates only the A-true / Condition-B branch

An A-false candidate would enter S1/D1 as soon as Condition A is determinate, without a P6 causal-license
determination. P6 and E6 would apply only after A is true.

Consequences:

- Some candidates could receive S1/D1 even though the controls do not license the causal claim that the
  answer lacks image-dependence.
- Eligibility would become branch-dependent: P6 would no longer be required for every labelled instance.
- Label Specification §3 P6 and §9 E6 would need semantic narrowing, not merely pipeline synchronization.
- Corpus membership and E6 counts would change because some currently routed candidates would become
  labelled S1 instances.
- Data Model provenance would need to permit S1 labels without a P6 result, weakening uniform verdict
  reconstructability.

This alternative conflicts with the current governing specifications and is not preferred.

### Alternative C — Reclassify an unlicensed A-false reading as E4

An A-false candidate whose controls do not license the causal reading would route as E4
(indeterminate image-dependence) rather than E6.

Consequences:

- E4 would no longer mean only failure of P4 determinacy; it would also absorb failure of P6 license.
- E6 would cease to be the exhaustive negation of P6.
- The P/E taxonomy and deterministic provenance would conflate two distinct failures: inability to obtain
  a determinate reading and inability to license a determinate reading causally.
- Label Specification §3/§9, Pipeline §6, Data Model T1–T2, and routed-aside accounting would require
  semantic changes.

This alternative is rejected because it changes existing E4/E6 meanings and is unnecessary.

## 4. Proposed decision

**Adopt Alternative A: P6 gates every labelled branch using branch-appropriate evidence.**

Normative consequences upon acceptance:

- **C1 — Universal P6 eligibility.** No Behavioural State or Label may be assigned unless P6 holds for
  the causal reading used to establish that state.
- **C2 — A-false is gated.** A determinate Condition A = false does not by itself authorize S1/D1. P6
  MUST hold before S1 is assigned; otherwise the candidate routes E6.
- **C3 — A-true is gated.** On the A-true path, P6 MUST hold before Condition B is converted into S2 or
  S3; otherwise the candidate routes E6.
- **C4 — Branch-appropriate completeness.** The P6 determination MUST consume the intervention and
  control evidence applicable to the active causal claim. The A-false path MUST NOT require S09 or a
  Condition-B observation merely to make S10 reachable.
- **C5 — Distinct failure meanings.** P4 failure remains E4; P6 failure remains E6. Neither may be
  forced into D1, D2, or the other E-code.
- **C6 — Traceability.** Provenance MUST record the active branch, control applicability/results, the P6
  outcome, and any E6 route so that every S1/S2/S3 or routed-aside resolution is reconstructible.
- **C7 — No taxonomy or boundary change.** This decision adds no gate, route, state, label, reason code,
  artifact, or predictor-visible datum and changes no information boundary.
- **C8 — Operational independence.** Concrete control suites, applicability tests, thresholds, and
  serialization remain implementation-profile decisions constrained by P6; this ADR selects none.

## 5. Population and artifact impact

| Area | Effect under the proposed decision |
|---|---|
| Candidate population | Unchanged |
| Labelled population | Only candidates satisfying P1–P6 on their active branch are labelled, as already required by `06` |
| S1/D1 | Requires a determinate A-false result and a licensed causal reading |
| S2/S3 | Continue to require A true, P5, P6, and a determinate Condition B |
| Routed-aside set | P6 failure is E6 on either branch |
| Provenance | Records branch-appropriate control applicability/results and P6 outcome |
| Predictor input | Unchanged; controls and provenance remain withheld |
| Evaluation | Unchanged; consumes existing labels only |

## 6. Compatibility and change classification

Alternative A preserves the eligibility and route meanings already fixed by Label Specification §3/§9,
ADR-004 C5, and Pipeline §6. Its application resolves an internal stage-contract inconsistency without
changing benchmark semantics. No released corpus exists whose membership would change.

Selecting Alternative B or C would change eligibility or routed-aside meaning and would require a
separate version-impact assessment. This ADR does not authorize either change.

## 7. Required amendments upon acceptance

No amendment below was authorized while this ADR remained Proposed.

1. **Label Generation Pipeline (`docs/07_Label_Generation_Pipeline.md`)**
   - §3 pipeline overview: show the P6/S10 gate on both determinate Condition-A branches before state
     assignment.
   - S07: state that A-false selects the prospective S1 branch but proceeds through S10 before S12 may
     assign S1.
   - S10: replace the impossible all-branch precondition "S06, S09 observed" with branch-appropriate
     intervention/control evidence; make pass/fail destinations explicit for both A-false and A-true.
   - S12: require P6 to hold before any S1/S2/S3 assignment.
   - §6: retain the existing branch table and universal-P6 rule; correct the D1-precedence sentence so
     "A-false is always S1/D1" applies only to eligible (P6-passing) candidates.
   - Applicable-ADR and traceability references: cite ADR-006 without changing control methods.
2. **Label Specification (`docs/06_Label_Specification.md`)**
   - No semantic amendment. Add only an ADR-006 cross-reference at P6/E6 if needed for application
     traceability; retain P6, E6, S1, D1, and eligibility wording unchanged.
3. **Benchmark Data Model (`docs/06a_Benchmark_Data_Model.md`)**
   - No artifact or semantic amendment. Existing §3.7 and T1–T2 already require control applicability,
     P6/E6, and reconstructability; add only an ADR-006 traceability reference if required.
4. **Dataset Specification and Evaluation Protocol (`docs/08_Dataset_Specification.md`,
   `docs/10_Evaluation_Protocol.md`)**
   - No normative amendment. Existing routed-aside handling and evaluation contracts remain unchanged.
5. **Supporting traceability**
   - V1-011 records the accepted-decision application. V1-027/V1-030 later regenerate the DAG,
     Traceability Matrix, registries, and freeze evidence; dated historical reviews remain unchanged.

## 8. Acceptance and review criteria

The BM may accept this ADR only after review confirms all of the following:

1. The decision is limited to P6 branch coverage and does not select operational controls.
2. Alternative A follows Label Specification §3/§9 and does not alter label, state, or E-code meaning.
3. The A-false path can reach S10 without requiring A-true-only S09 evidence.
4. P4/E4 and P6/E6 remain distinct and deterministic.
5. Every labelled state remains reconstructible from provenance including a passing P6 result.
6. The amendment list is exact and confined to V1-011 application and later traceability regeneration.
7. No implementation, pilot, corpus construction, or normative edit occurs before acceptance.

## 9. Consequences

**Positive**

- Removes the S10 reachability contradiction while preserving the authoritative eligibility rule.
- Prevents D1 from being assigned from an unlicensed negative causal reading.
- Keeps one P6/E6 meaning and one reconstructability contract across all labelled states.

**Costs and residual risks**

- The implementation profile must define and validate which controls are applicable to each branch.
- A-false candidates may route E6 when their negative causal reading cannot be licensed; this is the
  existing P6 consequence, not a new exclusion.
- Poorly chosen controls can still cause excessive E6 rates; V1-024/V1-039 and V1-047 own the operational
  contract and validation rather than this ADR.

## 10. Links

- [Problem Definition](../docs/03_Problem_Definition.md)
- [Formal Definitions](../docs/05_Formal_Definitions.md) §§11–14, 17–18
- [Label Specification](../docs/06_Label_Specification.md) §§3, 6, 8–9
- [Benchmark Data Model](../docs/06a_Benchmark_Data_Model.md) §§3.7–3.8, T1–T2
- [Label Generation Pipeline](../docs/07_Label_Generation_Pipeline.md) S06–S12, S15, §6
- [Dataset Specification](../docs/08_Dataset_Specification.md) §5
- [Benchmark Assurance](../docs/11_Benchmark_Assurance.md) LF2–LF4, GF1–GF4
- [Specification Synchronization Report](../docs/design/Specification_Synchronization_Report.md) SPA-004, SYNC-06
- [ADR-004](ADR-004-Answer-Correctness-Eligibility.md) C1, C5
- [ADR-005](ADR-005-Composite-Generator-Subject-Identity.md) C3, C7
