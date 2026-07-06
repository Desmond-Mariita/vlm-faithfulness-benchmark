# ADR application report

**Evidence class:** release record required by the active release plan §2.3 and §6 ("ADR application
report passes") and by the Decision Records Convention §10.

**Prepared by:** Verification Lead (VQ)

**Date:** 2026-07-05

**Repository state examined:** working tree at baseline commit `1a42e3f` plus the accepted, not yet
committed amendment set (see §4). Mechanical validation: `scripts/qa_adr_application_check.sh` (V1-029).

## 1. Scope and method

This report reconciles every accepted ADR in `decisions/` against its amendment obligations, per
Decision Records Convention §10: for each required amendment it records **(a)** the exact affected
file and clause, **(b)** the corresponding diff evidence, **(c)** a semantic-fidelity verification
that the applied text matches what the ADR authorized — no more and no less — and **(d)** explicit
BM or VQ sign-off.

Obligation sources follow convention §5.3: ADR-004 through ADR-008 are reconciled against their own
"Required amendments upon acceptance" sections; grandfathered ADR-002 is reconciled against its
normative statements as reconciled by work package V1-022; grandfathered ADR-003 against its §5
"Required amendments".

Verification method: clause-level inspection of the current specification text at every cited
location, cross-checked against the BM-accepted reconciliation matrices in the applying work
packages' completion reports (`v1-007` through `v1-011`, `v1-022`, `v1-028`). This report records
verification outcomes only; it edits no specification and no ADR.

## 2. Reconciliation by accepted ADR

### ADR-002 — Construction Provenance Lifecycle (Accepted 2026-07-01)

Obligations: normative provenance-lifecycle statements, as reconciled by V1-022 (BM accepted
2026-07-03).

| Amendment | Affected file and clause | Applied text verified | Fidelity |
|---|---|---|---|
| Observational vs sealed provenance lifecycle | `docs/07_Label_Generation_Pipeline.md` §7 Provenance lifecycle obligations, S14/S15, CC3/CC11; §2 authority table row ADR2 | Yes — observational/sealed phases and production-vs-traceability graphs (N1–N4) stated at the cited clauses; V1-022’s amendment list names the exact edited `07` surface (`lifecycle`, `S14/S15`, `CC3/CC11`) | Matches ADR-002; one artifact/producer preserved; no production-graph change |
| Provenance append timing and back-references | `docs/06a_Benchmark_Data_Model.md` §3.7, §8 T1/T3/T4/T6 | Yes — raw observations, derived determinations, and append timing enumerated at the cited clauses | Matches ADR-002 as reconciled by V1-022; wording/lifecycle only |
| Registry / traceability | `docs/design/release_evidence/spec-v1.0/decision_index.md` ADR-002 row; `docs/design/release_evidence/spec-v1.0/change_classification_register.md` `V1-022 / provenance lifecycle` row | Yes — acceptance and package classification are recorded at the cited rows; no semantic change | Matches ADR-002 record trail; supported by V1-022 package bookkeeping |

Diff evidence: `docs/design/release_evidence/spec-v1.0/v1-022_completion.md` §6 item 1 and §8; the attached `adr_application_report_diff.patch` is broader working-tree context and does not isolate ADR-002 hunks cleanly once later normalization edits are included; the current `07` and `06a` clauses are verified directly against the attached specs; current working tree over baseline `1a42e3f`.

Semantic-fidelity sign-off for ADR-002: **Verification Lead (VQ), 2026-07-05** — V1-022 package BM-accepted 2026-07-03.

### ADR-003 — Incomplete Candidate Subjects (Accepted 2026-07-01)

Obligations: ADR-003 §5.1–§5.4.

| Amendment | Affected file and clause | Applied text verified | Fidelity |
|---|---|---|---|
| §5.1 Output Tuple completeness bound | `docs/05_Formal_Definitions.md` §19 | Yes — pre-eligibility incompleteness stated; incomplete tuple barred from crossing the construction/evaluation boundary; "incomplete" marked a state, not a new term | Matches §5.1 exactly |
| §5.2 Data Model contents/lifecycle | `docs/06a_Benchmark_Data_Model.md` §3.2, §3.3, §3.8, §6 R2, §9 T2 | Yes — "an Output Tuple, which MAY be incomplete prior to eligibility (per ADR-003)"; R2 "possibly incomplete before eligibility"; E1 routing retained | Matches §5.2; no new artifact |
| §5.3 P1 reframed as completeness gate | `docs/06_Label_Specification.md` §3 P1, §9 E1 | Yes — P1 "determines whether the Candidate Subject's Output Tuple is sufficiently complete"; E1 meaning unchanged | Matches §5.3; E1 semantics preserved |
| §5.4 DAG updates | `docs/design/Label_Generation_Pipeline_DAG.md` §5 T2/T3/T6, §11 G2 | Yes — G2 marked resolved by ADR-003; incomplete-tuple generation/binding noted and verified against the current DAG text | Matches §5.4; resolution totality unaffected |

Diff evidence: `docs/design/release_evidence/spec-v1.0/adr_application_report_diff.patch` for the `docs/06a_Benchmark_Data_Model.md` §3.3 amendment; `docs/design/release_evidence/spec-v1.0/v1-027_completion.md` §6 item 1 and §8 for the DAG regeneration surface; the cited `§5 T2/T3/T6` and `§11 G2` clauses are verification targets against the current DAG text rather than V1-027 amendment-list items; no edit was required for `docs/05_Formal_Definitions.md` §19 or `docs/06_Label_Specification.md` §3 P1, §9 E1 beyond clause-level verification; current working tree over baseline `1a42e3f`.

Semantic-fidelity sign-off for ADR-003: **Verification Lead (VQ), 2026-07-05** — acceptance recorded in the
decision index (convention §5.3).

### ADR-004 — Answer Correctness Eligibility (Status: Accepted; Date: 2026-07-02; applied by V1-009, BM accepted 2026-07-02)

Obligations: ADR-004 §7 items 1–6.

| Amendment | Affected file and clause | Applied text verified | Fidelity |
|---|---|---|---|
| 1. Correctness not an eligibility precondition | `docs/06_Label_Specification.md` §3, I6, §14 Q1 | Yes — "Correctness is not a precondition (ADR-004)"; I6 analysis-only; Q1 marked resolved by ADR-004 | Matches §7.1; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-009_completion.md` §1 rows 1a–1c |
| 2. Pipeline gates never route on correctness | `docs/07_Label_Generation_Pipeline.md` CC1/CC4, S05/S07/S15, §10 | Yes — "Answer correctness never gates eligibility and never selects a route (ADR-004 C1)"; Condition A concerns the exact chosen answer | Matches §7.2; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-009_completion.md` §1 rows 2a–2e |
| 3. Corpus assembly unfiltered by correctness | `docs/08_Dataset_Specification.md` §15 RI11, §19 | Yes — LS Q1 removed from open dependencies; optional correctness metadata not predictor-visible | Matches §7.3; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-009_completion.md` §1 rows 3a–3b |
| 4. Evaluation slicing retained, corpus branch removed | `docs/10_Evaluation_Protocol.md` §8 C-5, §16 L-7 | Yes — conditional correctness slicing retained (ADR-004 C7); Q1 recorded as resolved by ADR-004 | Matches §7.4; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-009_completion.md` §1 rows 4a–4b |
| 5. Data Model consistency-only clarification | `docs/06a_Benchmark_Data_Model.md` §3.2, §3.3, §3.8, §6 R2, §4/§8 T2 — no edit required (ADR-004 §7.5) | Yes — correctness outside identity/eligibility/state/label; no predictor-visible field added | Matches §7.5 (bounded); diff evidence: `docs/design/release_evidence/spec-v1.0/v1-009_completion.md` §1 row 5 |
| 6. Registries/traceability | `docs/design/release_evidence/spec-v1.0/decision_index.md` ADR-004 row; `docs/design/release_evidence/spec-v1.0/change_classification_register.md` `V1-004 / ADR-004` row, `## V1-004 impact record`, and `## V1-009 impact record`; `docs/06_Label_Specification.md` §14 Q1; `docs/10_Evaluation_Protocol.md` §16 L-7 | Yes — the decision index and change-classification register carry the resolution; the normative specs record the resolved Q1 in the affected authorities | Matches §7.6; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-029_completion.md` §2 and §6 item 9; current working tree over baseline `1a42e3f` |

Diff evidence: stable diff artifact `docs/design/release_evidence/spec-v1.0/adr_application_report_diff.patch`; `docs/design/release_evidence/spec-v1.0/v1-009_completion.md` §1 rows 1c, 2e, 3a–3b, 4a–4b, 5, 6 and §4; current working tree over baseline `1a42e3f`.

Semantic-fidelity sign-off for ADR-004: **Verification Lead (VQ), 2026-07-05** — V1-009 package BM-accepted 2026-07-02.

### ADR-005 — Composite-Generator Subject Identity (Status: Accepted; Date: 2026-07-02; applied by V1-010, BM accepted 2026-07-02)

Obligations: ADR-005 §7 items 1–6.

| Amendment | Affected file and clause | Applied text verified | Fidelity |
|---|---|---|---|
| 1. Q4 resolved; composite generator one subject | `docs/06_Label_Specification.md` §14 Q4 | Yes — "Status: resolved by ADR-005 (accepted 2026-07-02) — a composite generator is one valid subject" | Matches §7.1; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-010_completion.md` §1 row 1 |
| 2. Whole-generator identity | `docs/06a_Benchmark_Data_Model.md` §3.3, §6 R3 | Yes — composite identity is the whole generator subject; pair identity retained with no component-level split | Matches §7.2; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-010_completion.md` §1 rows 2a–2b |
| 3. Same subject bound across pipeline | `docs/07_Label_Generation_Pipeline.md` S02/S03, CC6/CC7, §10 | Yes — live composite generator bound across the pipeline; LS Q4 closed in §10 | Matches §7.3; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-010_completion.md` §1 rows 3a–3b |
| 4. Corpus-entry provenance same subject | `docs/08_Dataset_Specification.md` §19 | Yes — Q4 removed from open dependencies; provenance references the composite subject identity | Matches §7.4; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-010_completion.md` §1 row 4 |
| 5. Evaluation open-policy references | `docs/10_Evaluation_Protocol.md` §16 L-7 | Yes — "Q4 (composite-generator validity) is resolved by ADR-005" | Matches §7.5; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-010_completion.md` §1 row 5 |
| 6. Registries/traceability | `docs/design/release_evidence/spec-v1.0/decision_index.md` ADR-005 row; `docs/design/release_evidence/spec-v1.0/change_classification_register.md` `V1-005 / ADR-005` row, `## V1-005 impact record`, and `## V1-010 impact record`; `docs/06_Label_Specification.md` §14 Q4; `docs/10_Evaluation_Protocol.md` §16 L-7 | Yes — the decision index and change-classification register carry the resolution; the normative specs record the same applied decision | Matches §7.6; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-029_completion.md` §2 and §6 item 9; current working tree over baseline `1a42e3f` |

Diff evidence: stable diff artifact `docs/design/release_evidence/spec-v1.0/adr_application_report_diff.patch`; `docs/design/release_evidence/spec-v1.0/v1-010_completion.md` §1 rows 1, 2, 3a–3b, 4, 5, 6 and §4; current working tree over baseline `1a42e3f`.

Semantic-fidelity sign-off for ADR-005: **Verification Lead (VQ), 2026-07-05** — V1-010 package BM-accepted 2026-07-02.

### ADR-006 — P6 Completeness and Branch Applicability (Status: Accepted; Date: 2026-07-02; applied by V1-011, BM accepted 2026-07-02)

Obligations: ADR-006 §7 amendments 1–10, reconciled row by row in the V1-011 completion report §1.

| Amendment | Affected file and clause | Applied text verified | Fidelity |
|---|---|---|---|
| 1. Route both determinate A branches through S10 | `docs/07_Label_Generation_Pipeline.md` §3 | Yes — both branches converge on S10 with satisfiable preconditions and exactly one terminal outcome | Matches ADR-006 C1–C4; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-011_completion.md` §1 row 1 |
| 2. Make A-false prospective S1 subject to P6 | `docs/07_Label_Generation_Pipeline.md` S07 | Yes — A-false selects a prospective S1 branch and proceeds to S10 rather than assigning S1 directly | Matches ADR-006 C1–C2, C5; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-011_completion.md` §1 row 2 |
| 3. Use branch-appropriate evidence at P6 | `docs/07_Label_Generation_Pipeline.md` S10 | Yes — the impossible `S06, S09` all-branch precondition is replaced with branch-appropriate evidence | Matches ADR-006 C3–C4, C8; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-011_completion.md` §1 row 3 |
| 4. Make P6 pass/fail destinations explicit | `docs/07_Label_Generation_Pipeline.md` S10 | Yes — P6 pass sends A-false to S12 and A-true to S11; P6 failure on either branch sends E6 to S15 | Matches ADR-006 C1–C5; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-011_completion.md` §1 row 4 |
| 5. Require P6 before every state | `docs/07_Label_Generation_Pipeline.md` S12 | Yes — S12 preconditions now require a recorded passing P6 result before S1/S2/S3 assignment | Matches ADR-006 C1–C3, C6; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-011_completion.md` §1 row 5 |
| 6. Preserve universal-P6 rule and qualify D1 precedence | `docs/07_Label_Generation_Pipeline.md` §6 | Yes — the branch table remains intact and the `A-false is always S1/D1` sentence is qualified so it does not contradict E6 | Matches ADR-006 C1–C5, C7; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-011_completion.md` §1 row 6 |
| 7. Add application traceability | `docs/07_Label_Generation_Pipeline.md` §2, S07, S10, S12, §6 | Yes — ADR6 authority and consequence references are added without defining control methods | Matches ADR-006 C6–C8; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-011_completion.md` §1 row 7 |
| 8. Optional P6/E6 citations (consolidates ADR-006 §7 items 2 and 3) | `docs/06_Label_Specification.md` §3/§9; `docs/06a_Benchmark_Data_Model.md` §3.7/T1–T2 | Yes — existing clauses already state universal P6/E6 exactly | No edit needed; meaning preserved; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-011_completion.md` §1 row 8 |
| 9. Dataset Specification and Evaluation Protocol: no normative amendment | `docs/08_Dataset_Specification.md` §19; `docs/10_Evaluation_Protocol.md` §16 L-7 | Yes — existing routed-aside handling and evaluation contracts remain unchanged | No edit required; meaning preserved; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-011_completion.md` §3 |
| 10. Supporting traceability | `docs/design/release_evidence/spec-v1.0/decision_index.md` ADR-006 row; `docs/design/release_evidence/spec-v1.0/change_classification_register.md` `V1-006 / ADR-006` row, `## V1-006 impact record`, and `## V1-011 impact record` | Yes — V1-011 records the accepted-decision application; later registry and traceability regeneration remain deferred to V1-027/V1-030 | Matches ADR-006 §7.5; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-011_completion.md` §3 and §6 |

Diff evidence: stable diff artifact `docs/design/release_evidence/spec-v1.0/adr_application_report_diff.patch`; `docs/design/release_evidence/spec-v1.0/v1-011_completion.md` §1 rows 1–8 and §4, including `git diff --check`; current working tree over baseline `1a42e3f`.

Semantic-fidelity sign-off for ADR-006: **Verification Lead (VQ), 2026-07-05** — V1-011 package BM-accepted 2026-07-02.

### ADR-007 — Authority Precedence and ADR/Specification Ordering (Status: Accepted; Date: 2026-07-03; applied under V1-007, BM approved 2026-07-03)

Obligations: ADR-007 §8 items 1–4.

| Amendment | Affected file and clause | Applied text verified | Fidelity |
|---|---|---|---|
| 1. Decision-records convention ordering | `docs/conventions/decision-records.md` §2, §7/§8, §10, §13 | Yes — scope-bounded ADR/spec relationship is recorded in the operative clauses; the file's introductory historical framing remains descriptive only | Matches §8.1; process only; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-007_completion.md` §6.1 item 1 |
| 2. Versioning convention cross-reference | `docs/conventions/versioning.md` introductory preamble, §8, §9 | Yes — ADR-007 cross-referenced; open-question entry removed; no version-train change | Matches §8.2; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-007_completion.md` §6.1 item 2 |
| 3. Release plan records outcome without authority | `docs/design/Benchmark_v1.0_Release_Plan.md` §0, V1-007 row | Yes — plan disclaims authority and records scope-bounded transition precedence | Matches §8.3; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-007_completion.md` §6.1 item 3 |
| 4. Release evidence and freeze-time checks | `docs/design/release_evidence/spec-v1.0/decision_index.md` ADR-007 row; `docs/design/release_evidence/spec-v1.0/change_classification_register.md` `V1-007 / ADR-007` row and `## V1-007 impact record`; `docs/design/release_evidence/spec-v1.0/v1-007_completion.md` §6.1 items 4–5 and §8 | Yes — release evidence and freeze-time checks are recorded without rewriting historical reviews | Matches §8.4; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-007_completion.md` §6.1 items 4–5 and §8 |

Diff evidence: stable diff artifact `docs/design/release_evidence/spec-v1.0/adr_application_report_diff.patch`; `docs/design/release_evidence/spec-v1.0/v1-007_completion.md` §6.1 items 1–5 and §8; current working tree over baseline `1a42e3f`.

Semantic-fidelity sign-off for ADR-007: **Verification Lead (VQ), 2026-07-05** — applied text
matches the authorized amendments exactly; V1-007 package BM-approved 2026-07-03.

### ADR-008 — D1 Terminology Disposition (Accepted 2026-07-03; applied under V1-008, BM approved 2026-07-03; terminology carried into V1-028/V1-029)

Obligations: ADR-008 §8 items 1–3.

| Amendment | Affected file and clause | Applied text verified | Fidelity |
|---|---|---|---|
| 1. Display-name change and deprecation note | `docs/06_Label_Specification.md` §6 table and following note, §8.1 heading and body | Yes — D1 name is "Image-independent answer"; §6 note marks "Ungrounded answer" a deprecated historical display name | Matches §8.1; code `D1`, meaning, and precedence unchanged; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-008_completion.md` §6 item 1 |
| 2. Cross-document verification | `docs/06_Label_Specification.md` §5.3, §6 and §8.1; `docs/07_Label_Generation_Pipeline.md` §6; `docs/06a_Benchmark_Data_Model.md` §3.7; `docs/10_Evaluation_Protocol.md` §16 L-7 | Yes — documents use the stable code `D1`; the projection line and display-name occurrences use the accepted terminology outside the authorized deprecation note | Matches §8.2; no edits beyond authorization; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-008_completion.md` §6 items 1–3 and §8 |
| 3. Release evidence and QA carry-over | `docs/design/release_evidence/spec-v1.0/decision_index.md` ADR-008 row; `docs/design/release_evidence/spec-v1.0/change_classification_register.md` `V1-008 / ADR-008` row and `## V1-008 impact record` | Yes — old/new display-name check is carried forward in release evidence bookkeeping and later QA tooling | Matches §8.3; diff evidence: `docs/design/release_evidence/spec-v1.0/v1-008_completion.md` §6 item 4 and `terminology_check.txt` |

Diff evidence: stable diff artifact `docs/design/release_evidence/spec-v1.0/adr_application_report_diff.patch`; V1-008 completion report (exact §6/§8.1 diff recorded); `terminology_check.txt` generated by the V1-029 suite; current working tree over baseline `1a42e3f`.

Semantic-fidelity sign-off for ADR-008: **Verification Lead (VQ), 2026-07-05** — V1-008 package BM-approved 2026-07-03.

## 3. Semantic-fidelity sign-off

- BM acceptance of each applying package is recorded in the completion reports and the change
  classification register: V1-009 and V1-010 and V1-011 (2026-07-02); V1-007, V1-008, and V1-022
  (2026-07-03).
- **VQ semantic-fidelity sign-off:** I verified, at the clause level listed in §2, that each applied
  text matches the amendment its ADR authorized — its intent and its exact boundaries, no more and
  no less — and that no accepted ADR body was edited. Signed off: **Verification Lead (VQ),
  2026-07-05**, recorded before the freeze as required by Decision Records Convention §10(d).
- No accepted ADR has unapplied required amendments. No release-blocking BL8 governance gap is open
  against the amendment trail.

## 4. Evidentiary limitations

- The accepted amendment set is present in the working tree but not yet committed beyond baseline
  `1a42e3f`; the plan's freeze transaction (V1-032) requires the amendments to land in one clean,
  verified commit, at which point the per-amendment diff evidence becomes addressable by commit
  hash. Until then diff evidence is the working tree over the named baseline plus the per-package
  completion matrices. This is a freeze-transaction precondition, not an unapplied amendment.
- This report is regenerated or re-signed whenever a new ADR is accepted or an amendment surface
  changes; `scripts/qa_adr_application_check.sh` fails if an accepted ADR is missing from it.
