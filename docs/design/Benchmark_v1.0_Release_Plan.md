---
Title: Benchmark Specification v1.0 Execution and Release Plan
Status: Active
Plan-Version: 2.0
Benchmark-Version: v1.0 (pre-freeze)
Plan-Owner: Technical Lead / Release Manager
Last-reviewed: 2026-07-01
Authoritative-inputs:
  - reviews/codex/release_plan_technical_audit.md
Supporting-inputs:
  - reviews/gemini/release_plan_scientific_governance_audit.md
---

# Benchmark Specification v1.0 Execution and Release Plan

## 0. Mandate, authority, and scope

This is the non-normative execution plan for closing Benchmark Specification v1.0, freezing it,
publishing the specification repository, and authorizing implementation. It also records the correct
downstream order from pilot construction through public corpus release so implementation cannot begin
on a contradictory sequence.

This plan controls **work assignment, order, evidence, and release operations only**. It does not define
benchmark meaning and does not govern disagreements between technical authorities. The authority order
applicable at any point is the order ratified through the benchmark's existing governance process. That
order is formally recorded by work package V1-007 as scope-bounded transition precedence with
synchronized specification authority; the current Charter, accepted ADRs, and each owning specification
retain their own authority within that ordering. This plan cannot override any of them.

Review findings are inputs to the backlog, not semantic decisions. Any work item that could change a
label, state, eligibility population, evaluation meaning, artifact ontology, or governance rule must
complete the ADR/change-classification process before a specification is edited. The Release Manager may
schedule such work but may not approve its technical outcome.

### In scope

- governance bootstrap and outstanding decision packages;
- approved specification amendments and synchronization;
- release-candidate verification and Specification v1.0 freeze;
- public packaging of Specification v1.0;
- implementation inception and authorization;
- dependency-correct downstream milestones for pilot, corpus construction, validation, baselines, and
  public corpus release.

### Out of scope

- deciding any open semantic question inside this plan;
- selecting intervention algorithms, thresholds, models, datasets, or evidence representations;
- changing accepted ADR-002 or ADR-003;
- adding benchmark features;
- treating thesis code as normative behavior.

The detailed corpus delivery schedule is re-baselined at Implementation Authorization (M7). Its gates
and ordering in this plan are binding; its estimates are planning targets, not benchmark requirements.

---

## 1. Roles, decision rights, and RACI

Role ownership is sufficient for execution and survives personnel changes. The project owner records the
current human/account holder for each role in issue V1-001. Until delegation is recorded, the default
holder shown below is responsible; therefore no task is unowned.

| ID | Role | Default holder | Decision rights |
|---|---|---|---|
| **BM** | Benchmark Maintainer | Project/repository owner | Accountable for construct integrity, ADR ratification, specification acceptance, and semantic change classification. |
| **TL** | Technical Lead | Appointed technical lead | Responsible for technical coordination, implementation architecture, interface design, and engineering acceptance. |
| **RM** | Release Manager | Appointed release manager | Accountable for this plan, issue tracking, evidence collection, freeze/public tags, and release go/no-go. |
| **SO** | Specification Owner | TL until BM delegates a document | Responsible for drafting approved changes in the owning specification and proving cross-document synchronization. |
| **EL** | Engineering Lead | TL until delegated | Responsible for repository bootstrap, code, CI, fixtures, harness, and implementation work packages. |
| **VQ** | Verification Lead | RM for mechanical verification; BM approves release evidence | Responsible for QA reports, traceability checks, freeze manifest, and release-check execution. |
| **PO** | Publication and Licensing Owner | RM; BM approves license posture | Responsible for LICENSE, README, archive boundary, citation, release notes, and publication checks. |

One person may hold several roles. The following separation is mandatory even when roles are co-held:

- BM alone approves semantic/governance outcomes.
- SO/EL may draft or implement but may not self-ratify a semantic decision.
- RM may stop a release for failed evidence but may not waive a normative requirement.
- BM approves the freeze evidence produced by VQ; unresolved disagreement is a no-go.

### RACI by activity

| Activity | Responsible | Accountable | Consulted | Informed |
|---|---|---|---|---|
| ADR/change classification | SO | BM | TL, RM | EL, VQ |
| Specification amendment | SO | BM | TL, affected SOs | EL, VQ |
| Supporting-document synchronization | SO | TL | RM | BM, EL |
| Freeze evidence and tag | VQ/RM | RM | BM, TL | all roles |
| Freeze approval | RM | BM | TL, VQ | all roles |
| Public specification release | PO | RM | BM, TL | all roles |
| Implementation design and code | EL | TL | SO, VQ | BM, RM |
| RIP instance approval | EL | TL | SO, BM, VQ | RM |
| Corpus release approval | RM/VQ | BM | TL, PO | all roles |

---

## 2. Tracking model and evidence contract

### 2.1 Canonical work item

Each `V1-nnn` row in §5 is a canonical work package and becomes one tracked issue during M0. GitHub
Issues is the system of record once V1-003 restores/configures the repository remote; until then the
rows in this plan and V1-001's import manifest are the system of record. The issue title begins with its
ID. The plan remains the dependency source of truth; issues record execution.

Required issue fields:

- DRI and approver;
- milestone and target date;
- effort estimate in ideal person-days and the role capacity assigned to it;
- dependencies by `V1-nnn`;
- deliverables and exact acceptance checks from §5;
- status: `Queued`, `Ready`, `In Progress`, `In Review`, `Accepted`, or `Blocked`;
- links to ADRs, PRs/patches, test output, and acceptance evidence;
- blocker reason and next decision date when `Blocked`.

An item is `Ready` only when all dependencies are `Accepted`. It is `Accepted` only when its approver
links the required evidence. Closing an issue without evidence does not satisfy a milestone.

### 2.2 Change-classification gate

Before any normative document edit, SO creates a short impact record answering:

1. Does this alter label/state meaning, eligibility membership, an evaluation claim, artifact ontology,
   or governance authority?
2. Does an accepted ADR already authorize the exact change?
3. Is the change editorial synchronization, a specification amendment, or an ADR decision?
4. Which documents and compatibility/version fields are affected?

BM records the classification. ADR-classified work cannot merge until its ADR is accepted. This is how
the plan schedules unresolved questions without deciding them.

### 2.3 Evidence location

Execution evidence is stored under `docs/design/release_evidence/spec-v1.0/` and linked from issues.
Required evidence names are:

- `role_assignments.md`
- `decision_index.md`
- `change_classification_register.md`
- `normative_file_manifest.tsv`
- `adr_application_report.md`
- `open_question_report.md`
- `link_check.txt`
- `metadata_check.txt`
- `terminology_check.txt`
- `stale_authority_check.txt`
- `freeze_manifest.sha256`
- `freeze_approval.md`
- `public_release_checklist.md`
- `implementation_authorization.md`

These are release records, not benchmark specifications.

### 2.4 Active risk register

RM reviews this register at every milestone and records changes in the relevant issue. A trigger invokes
the response shown; no risk response may bypass governance or acceptance evidence.

| Risk | Owner | Trigger | Required response |
|---|---|---|---|
| Semantic decision delay | BM | Any V1-004–008 misses M1 target | Re-plan M2/M3 dates; do not begin dependent edits. |
| Repository history/remote unavailable | EL | V1-003 cannot establish a valid target repository | RM pauses freeze scheduling; BM selects migration/new-history option and records it. |
| RIP cost exceeds available compute/time | TL | V1-039 estimate exceeds M8–M12 capacity | Re-baseline downstream dates at V1-044; do not weaken profile acceptance rules. |
| Pilot viability failure | BM | V1-046 fails its pre-registered gate | Invoke Charter §6 disposition; stop corpus construction. |
| Stochastic reconstruction changes protected artifacts | TL | V1-048 or V1-050 violates accepted reproducibility rule | Stop affected build; correct RIP/implementation or create governed new version. |
| Thesis adapter corrupts identity or drops population | EL | V1-045 reconciliation or boundary fixtures fail | Reject adapter path; retain benchmark-native envelope and ledger as authority. |
| Licensing/redistribution uncertainty | PO | Source/model/output rights cannot be evidenced | Block M5 or M12 as applicable; publish no affected artifact. |
| Single-person role conflict hides failed evidence | RM | Drafter and approver would be the same actor on semantic/freeze work | BM appoints a separate reviewer for that item or records a no-go; no self-approval. |

---

## 3. Milestones and calendar

Targets assume the listed role holders are available. RM updates dates when execution evidence shows a
real dependency change; RM may not reorder semantic dependencies without a dated plan revision.

| Milestone | Target | Owner | Exit criterion |
|---|---:|---|---|
| **M0 — Program Activation** | 2026-07-03 | RM | V1-001–003 accepted: operational Git repository, issue backlog, role assignments, and governance convention work ready. |
| **M1 — Decisions Ratified** | 2026-07-10 | BM | V1-004–008 accepted; each open semantic/governance question has an accepted ADR or explicit BM classification outcome. No plan text substitutes for a decision. |
| **M2 — Specification Closure** | 2026-07-21 | BM | V1-009–026 accepted; all authorized amendments synchronized; RIP contract and release-artifact contracts closed; no freeze-blocking registry item remains. |
| **M3 — Release Candidate Verified** | 2026-07-24 | VQ | V1-027–031 accepted; exact normative set verified; all automated/manual evidence green; freeze manifest and approval packet complete. |
| **M4 — Specification v1.0 Frozen** | 2026-07-25 | RM | V1-032 accepted; immutable freeze commit and annotated `benchmark-spec-v1.0-freeze` tag exist; BM approval recorded. |
| **M5 — Public Specification v1.0** | 2026-07-30 | RM | V1-033–037 accepted; packaging complete; normative hashes equal freeze manifest; annotated public tag `benchmark-spec-v1.0` and release notes published. |
| **M6 — Implementation Inception Complete** | 2026-08-05 | TL | V1-038–043 accepted; RIP v1 candidate, implementation design, CI, fixtures, acceptance matrix, and boundary-test skeleton exist. |
| **M7 — Implementation Authorized** | 2026-08-06 | TL | V1-044 accepted; BM/RM/TL authorization record permits normative coding/pilot execution against the frozen contract. |
| **M8 — Pilot and Viability Gate** | 2026-08-28 | TL | V1-045–048 accepted; pilot runs end-to-end; VAL-01 passes or Charter §6 disposition is invoked. |
| **M9 — Candidate Corpus Constructed** | 2026-10-09 | TL | V1-049 accepted; mass construction, reconciliation, S18 transaction, manifest, datasheet, and routed/exclusion ledgers complete. |
| **M10 — Corpus Release Validation** | 2026-10-23 | VQ | V1-050–052 accepted; causal/control checks and manifest rebuild pass; assurance blocking evidence complete. |
| **M11 — Internal Alpha** | 2026-11-06 | TL | V1-053 accepted; baselines, harness, scorecards, and release-report dry run complete. |
| **M12 — Public Corpus v1.0** | 2026-11-13 | RM | V1-054 accepted; legal, assurance, artifact, and publication gates clear; `benchmark-corpus-v1.0` released. |

M8–M12 dates are re-estimated and approved in V1-044 after RIP resource costs are known. Their order and
exit criteria do not change without a plan revision.

---

## 4. Dependency graph

```text
M0 Program Activation
 ├─ V1-002 governance conventions ───────────────┐
 ├─ mechanical/editorial prep (V1-027–029) ──┐  │
 └─ engineering bootstrap prototypes ────────┐│  │
                                              ││  ▼
                                              │└─ M1 Decisions Ratified
                                              │        │
                                              └────────┼─ M2 Specification Closure
                                                       │
                                                       ▼
                                                M3 RC Verification
                                                       │
                                                       ▼
                                                M4 Specification Freeze
                                                   /             \
                                                  ▼               ▼
                                      M5 Public Spec Release   M6 Impl. Inception
                                                                  │
                                                                  ▼
                                                           M7 Authorization
                                                                  │
                                                                  ▼
                                                        M8 Pilot + VAL-01
                                                                  │ pass
                                                                  ▼
                                                        M9 Corpus Construction
                                                                  │
                                                                  ▼
                                                        M10 Release Validation
                                                                  │
                                                                  ▼
                                                        M11 Internal Alpha
                                                                  │
                                      M5 public/legal ─────────────┤
                                                                  ▼
                                                        M12 Public Corpus
```

Justification:

- Governance conventions precede new ADR ratification.
- Decision-dependent edits wait for accepted decisions; independent QA/editorial preparation runs in
  parallel.
- Non-semantic engineering bootstrap may start before freeze, but normative coding and pilot execution
  require M7.
- Specification freeze and public specification release are distinct commits/tags.
- VAL-01 uses a pilot implementation and precedes mass corpus construction.
- Manifest rebuild and release validation require a candidate corpus and therefore follow M9.
- Baselines and release-report dry runs follow validated corpus construction.
- Public corpus release requires both the validated corpus path and public/legal packaging.

There is no permitted feedback edge from implementation results into frozen v1.0 semantics. A discovered
specification defect stops the affected work and enters the ADR/versioning process; code does not patch
meaning.

---

## 5. Executable work-package backlog

### A. Program and governance bootstrap

| ID | Deliverable | DRI / approver | Dependencies | Milestone | Acceptance evidence |
|---|---|---|---|---|---|
| **V1-001** | Activate release program: record role holders, create milestone board, and create one issue per work package. | RM / TL | — | M0 | `role_assignments.md`; issue list contains V1-001…054 with required fields. |
| **V1-002** | Author missing decision-record and versioning conventions; explain ADR series origin. This documents process only and must not decide open semantics. | SO / BM | V1-001 | M0 | Both cited convention files exist; BM approval; all normative references resolve. |
| **V1-003** | Restore operational Git repository and release branch: initialize or migrate history, configure remote/branch protection where available, and prove annotated tags work in a disposable test tag. | EL / RM | V1-001 | M0 | `git rev-parse` succeeds; clean baseline commit; test tag created/deleted; evidence linked. |
| **V1-004** | Decision package for correctness eligibility (existing ADR-004 slot): alternatives, population impact, affected stages/artifacts, compatibility, and maintainer decision. Plan expresses no preferred outcome. | SO / BM | V1-002 | M1 | ADR accepted; affected-document amendment list approved. |
| **V1-005** | Decision package for composite-generator subject identity (existing ADR-005 slot), including minimum identity consequences for each alternative. | SO / BM | V1-002 | M1 | ADR accepted; affected-document amendment list approved. |
| **V1-006** | Decision package for P6 completeness and branch applicability (existing ADR-006 slot). It must analyze A-false execution, counterfactual validity, localization-causality risk, route ownership, and control placement without taking the plan's former proposal as decided. | SO / BM | V1-002 | M1 | ADR accepted; executable branch contract and amendment list approved. |
| **V1-007** | Governance decision on authority precedence and ADR-versus-spec ordering. | SO / BM | V1-002 | M1 | Accepted ADR/governance record; scope-bounded transition precedence with synchronized specification authority. |
| **V1-008** | D1 terminology decision: retain with normative disambiguation or rename through the approved compatibility/version process. | SO / BM | V1-002 | M1 | Accepted ADR or BM classification record authorizing the exact non-semantic clarification; no unapproved schema rename. |

### B. Specification closure

Every row begins with the §2.2 change-classification gate. “Amend” below means only the change authorized
by BM/accepted ADR.

| ID | Deliverable | DRI / approver | Dependencies | Milestone | Acceptance evidence |
|---|---|---|---|---|---|
| **V1-009** | Apply ADR-004 to all affected P-gates, routes, manifests, and evaluation clauses. | SO / BM | V1-004 | M2 | ADR amendment checklist complete; cross-document test cases agree. |
| **V1-010** | Apply ADR-005 to generator/instance identity, S02/S03, and all intervention subject references. | SO / BM | V1-005 | M2 | One consistent subject identity contract; amendment checklist complete. |
| **V1-011** | Apply ADR-006 to P6 semantics and the executable pipeline/DAG branches. | SO / BM | V1-006 | M2 | Every branch has satisfiable preconditions and exactly one terminal outcome; DAG regenerated later by V1-027. |
| **V1-012** | Resolve DM Q4 through its owning process: define only the evidence-region identity contract required between S08/S09; concrete representation stays in the RIP. | SO / BM | V1-002 | M2 | Q4 status closed or explicitly deferred with no missing S08/S09 interface; classification record linked. |
| **V1-013** | Reconcile Q3 registry with the accepted v1 state-space authority; any semantic change routes to ADR rather than this edit. | SO / BM | V1-002 | M2 | Registry points to governing clause/ADR; no contradictory “open” statement remains. |
| **V1-014** | Resolve confirmatory-endpoint independence through the Evaluation Protocol's owning process. The plan does not select calibration/nesting policy. | SO / BM | V1-002 | M2 | Approved rule has independent selection/measurement semantics, implementable inputs, and normative example. |
| **V1-015** | Resolve artifact/label reproducibility and immutability interaction through the owning process. | SO / BM | V1-002 | M2 | Exact versus tolerated fields and changed-label adjudication are testable; affected clauses agree. |
| **V1-016** | Unify boundary vocabulary for release availability, scoring-only access, audit-only access, and predictor input. | SO / BM | V1-002 | M2 | Boundary tables/diagrams use one vocabulary; predictor-input prohibition unchanged. |
| **V1-017** | Close identity/public-manifest leakage: specify live-split public-ID non-derivability/non-joinability and family-level transparency without instance-level generator disclosure. | SO / BM | V1-002 | M2 | Threat-model examples and required negative test interface approved. |
| **V1-018** | Move split membership to harness/scoring metadata rather than model input. | SO / BM | V1-002 | M2 | Predictor interface excludes split field; harness can stratify; conformance language agrees. |
| **V1-019** | Define Train-label delivery facet, keying, access lifecycle, and held-out negative join contract. | SO / BM | V1-002 | M2 | Learnable baseline can train; validation/held-out labels cannot join through released training interface. |
| **V1-020** | Define scorecard mandatory/conditional/N-A cells, including hard-label predictors, optional reason codes, conceptual oracle, and cross-split derived values. | SO / BM | V1-002 | M2 | Three conformance fixtures yield unambiguous scorecards. |
| **V1-021** | Partition conformance into mechanically verified facts and participant attestations. | SO / BM | V1-002 | M2 | Scorecard/release gate records both states separately; no claim of proving internal non-use. |
| **V1-022** | Reconcile observational and sealed provenance with ADR-002. | SO / BM | V1-002 | M2 | Raw observations, derived determinations, append timing, and back-references enumerated; one artifact/producer preserved. |
| **V1-023** | Restore one canonical owner per artifact while preserving semantic authorities and consumers. | SO / BM | V1-002 | M2 | Artifact table has one owner column value per row; change responsibility unambiguous. |
| **V1-024** | Define the RIP as an implementation artifact contract: owner, required decision categories, versioning, approval, compatibility, and conformance evidence. Do not pin implementation choices here. | SO / BM | V1-002 | M2 | Independent team can author a profile without adding semantics; N10.7 reference resolves. |
| **V1-025** | Complete release-artifact contract: define/repoint datasheet requirement, S01 exclusion ledger, and producer/reference for analysis plan, report, lineage, and acceptance comparison. | SO / BM | V1-002 | M2 | S18 transaction has a named producer and required contents for every output; manifest includes exclusions. |
| **V1-026** | Close all remaining freeze-blocking registries and version/governance metadata; classify RFC-2119 use project-wide. Do not impose fixed size floors or a v1 human protocol without separate approval. | SO / BM | V1-009–025 | M2 | `open_question_report.md` contains no v1 blocker; size-floor and human-protocol topics are future issues unless approved separately. |

### C. Repository synchronization and release-candidate QA

| ID | Deliverable | DRI / approver | Dependencies | Milestone | Acceptance evidence |
|---|---|---|---|---|---|
| **V1-027** | Regenerate current normative portions of the DAG/Traceability Matrix; archive historical bodies and synchronization reports outside the authority chain. | SO / TL | V1-011, V1-022–023 | M3 | Current stages/branches match specs; archived files visibly non-authoritative; no stale absence/status claims. |
| **V1-028** | Normalize editorial mirrors, terminology, links, metadata, and paths. Treat `04` according to its actual non-normative status; remove private-path/review-evidence dependencies without changing its mapping purpose. | SO / TL | V1-009–026 | M3 | Diff is non-semantic; links and terminology checks pass; BM confirms no hidden amendment. |
| **V1-029** | Build release QA commands/scripts for metadata, links, ADR application, open registries, stale authority text, and normative-set enumeration. | VQ / RM | V1-003 | M3 | Commands run from a fresh checkout and produce named §2.3 evidence files with nonzero failure exits. |
| **V1-030** | Produce the exact normative manifest: Charter, Vision, `01`, `03`, `05`, `06`, `06a`, `07`, `08`, `09`, `10`, `11`, and accepted ADRs. `04`, reviews, plans, inventories, and historical design reports are explicitly supporting/non-normative. | VQ / BM | V1-026–029 | M3 | `normative_file_manifest.tsv` lists path, authority, status, version, and hash; BM signs classification. |
| **V1-031** | Assemble release-candidate evidence and conduct go/no-go review. | RM/VQ / BM | V1-027–030 | M3 | All §2.3 pre-freeze evidence present and green; no waived Blocker/Major; signed go decision. |

### D. Freeze and public specification release

| ID | Deliverable | DRI / approver | Dependencies | Milestone | Acceptance evidence |
|---|---|---|---|---|---|
| **V1-032** | Execute specification freeze: set exact normative set to Accepted/v1.0 as authorized, commit atomically, rerun QA on commit, write hashes, and create annotated `benchmark-spec-v1.0-freeze`. | RM/VQ / BM | V1-031 | M4 | Clean Git state; tag resolves to verified commit; `freeze_manifest.sha256` and `freeze_approval.md` signed. |
| **V1-033** | Approve license posture for specification text separately from source/model/output/corpus licenses. | PO / BM | V1-003 | M5 | Root LICENSE and licensing statement approved; corpus rights not overclaimed. |
| **V1-034** | Publish root README with purpose, exact authority/read order, governance pointer, status, implementation entry point, license, citation, and deliberate numbering gaps. | PO / RM | V1-030, V1-032 | M5 | Fresh-reader checklist passes without private context; README does not create technical authority. |
| **V1-035** | Execute archive/public-tree cleanup; keep this plan and accepted audits explicitly non-normative and preserve history without ambiguous `00_` peers. | PO / RM | V1-027, V1-032 | M5 | Published tree has clear normative/supporting/archive boundaries; no broken links. |
| **V1-036** | Add CONTRIBUTING, CITATION.cff, changelog/lineage, and specification release notes. | PO / RM | V1-002, V1-032–035 | M5 | Contribution path uses accepted governance; citation and lineage identify freeze commit. |
| **V1-037** | Public Specification v1.0 release: verify normative hashes unchanged since freeze, tag packaging commit `benchmark-spec-v1.0`, and publish release notes. | RM/VQ / BM | V1-033–036 | M5 | `public_release_checklist.md`; public tag; normative hash equality; fresh-clone smoke check. |

### E. Implementation inception and authorization

| ID | Deliverable | DRI / approver | Dependencies | Milestone | Acceptance evidence |
|---|---|---|---|---|---|
| **V1-038** | Implementation architecture/interface design for S01–S19: component boundaries, schemas, identity/error model, storage/access views, and trace links. | EL / TL | V1-032 | M6 | Design review approved; every stage has concrete input/output interface without changing semantics. |
| **V1-039** | Author RIP v1 candidate under V1-024 contract. Operational selections only; include deterministic scope, seeds/realized input hashes where stochastic behavior exists, environment pins, and validation obligations. | EL / TL | V1-024, V1-032 | M6 | RIP validates against contract; all deferred label-producing choices pinned; BM confirms no semantic content. |
| **V1-040** | Build versioned implementation acceptance matrix mapping every MUST/stage invariant to mechanical test, inspection, attestation, or release evidence. | VQ/EL / TL | V1-030, V1-038 | M6 | No requirement unmapped; each row names test/evidence owner and fixture. |
| **V1-041** | Bootstrap implementation repository/layout, dependency environment, CI, code ownership, lint/type/test commands, and artifact directories. | EL / TL | V1-003, V1-032 | M6 | Fresh clone installs; CI passes empty/skeleton suite; commands documented. |
| **V1-042** | Create synthetic/golden fixtures for all routes E1–E6, states S1–S3, D1 precedence, incomplete tuples, resolution totality, and separated views. | EL/VQ / TL | V1-038, V1-040–041 | M6 | Fixture manifest complete; expected outcomes reviewed against frozen specs. |
| **V1-043** | Implement boundary-test skeleton: ID non-joinability, split isolation, Train-label join restriction, hidden/audit separation, and verified-vs-attested reporting. | EL / TL | V1-017–021, V1-041–042 | M6 | Tests fail on seeded leaks and pass on conformant synthetic views. |
| **V1-044** | Implementation Authorization review and downstream re-baseline. | TL/RM / BM | V1-038–043 | M7 | `implementation_authorization.md` names frozen spec/tag, RIP version, acceptance matrix, owners, approved first sprint, risks, and M8–M12 dates. |

### F. Pilot, corpus, validation, and corpus release

These packages are downstream implementation work, included here to make the transition and ordering
unambiguous. They cannot modify frozen semantics.

| ID | Deliverable | DRI / approver | Dependencies | Milestone | Acceptance evidence |
|---|---|---|---|---|---|
| **V1-045** | Implement pilot-capable S01–S19 vertical slice using benchmark-native subject/output envelope, strict exclusion/route ledgers, and thesis capabilities only behind adapters. | EL / TL | V1-044 | M8 | Synthetic acceptance matrix green; one real pilot slice resolves every candidate exactly once. |
| **V1-046** | Execute VAL-01 viability gate on pilot. | EL/VQ / BM | V1-045 | M8 | Pre-registered result; pass authorizes continued pilot, terminal failure invokes Charter §6 decision path. |
| **V1-047** | Validate localization/causal-control behavior required by the accepted ADR/RIP, using the simplest approved study design; the plan does not prescribe boxes or a statistic. | EL/VQ / TL | V1-006, V1-039, V1-045 | M8 | Approved study report; false-route/false-label risks within pre-registered acceptance rule. |
| **V1-048** | Validate intervention/control behavior and pilot reproducibility. | EL/VQ / TL | V1-039, V1-045 | M8 | Controls and routes meet RIP acceptance rules; rerun evidence recorded. |
| **V1-049** | Construct candidate corpus: mass labeling, splits, hard-core construction under assigned TL ownership, S18 freeze transaction, manifest, datasheet, exclusion/routed ledgers, and full population reconciliation. | EL / TL | V1-046–048 | M9 | Candidate corpus immutable; raw→exclusion→candidate→entry/route counts reconcile; manifest complete. |
| **V1-050** | Manifest-driven candidate-corpus rebuild and immutability/reproducibility acceptance. | VQ/EL / TL | V1-049 | M10 | Rebuild satisfies frozen V1-015 rule; exact fields and hashes verified as required. |
| **V1-051** | Release-scale control/localization validation on candidate corpus. | VQ/EL / TL | V1-049 | M10 | Pre-registered release-scale results satisfy RIP/assurance rules. |
| **V1-052** | Assurance blocking-criteria audit and corpus release-candidate approval. | VQ/RM / BM | V1-050–051 | M10 | Every applicable BL criterion has evidence and passes; signed candidate approval. |
| **V1-053** | Internal alpha: implement/run required baselines and harness; dry-run analysis plan, scorecards, conformance, and release report. | EL/VQ / TL | V1-052 | M11 | Complete reproducible baseline scorecards; report dry run; no unresolved harness defect. |
| **V1-054** | Public corpus release with access-class enforcement, licenses, artifacts, baselines, report, citation, and annotated `benchmark-corpus-v1.0` tag. | RM/PO/VQ / BM | V1-037, V1-053 | M12 | Public corpus checklist signed; artifact hashes published; fresh-consumer smoke test passes. |

---

## 6. Freeze evidence checklist

M3/M4 are executable only through this checklist. “Pass” means evidence is linked; verbal confirmation
does not count.

### Governance and decisions

- [ ] Role assignments and decision rights recorded (V1-001).
- [ ] Decision-record and versioning conventions exist (V1-002).
- [ ] ADR-004, ADR-005, ADR-006, authority-precedence decision, and D1 terminology disposition accepted
      and indexed (V1-004–008).
- [ ] Every normative change has BM classification and required ADR/spec approval.
- [ ] ADR-002/003 and all newly accepted ADR amendments are applied with no stale base text.

### Normative contract

- [ ] Exact normative file set is enumerated in `normative_file_manifest.tsv` (V1-030).
- [ ] Each normative document has expected `Status: Accepted` and Benchmark-Version `v1.0` in the freeze
      candidate; `04` and planning/review/design history remain explicitly non-normative.
- [ ] No v1-blocking open registry entry remains.
- [ ] RIP artifact contract and release-artifact contract exist; no frozen text depends on an unwritten
      implementation choice.
- [ ] Boundary, conformance, scorecard, provenance, ownership, and release interfaces are mutually
      consistent.

### Repository QA

- [ ] Git repository operational; release candidate clean; expected remote/branch recorded.
- [ ] Link check passes with zero broken internal normative links.
- [ ] Metadata check passes for exact normative set.
- [ ] ADR application report passes.
- [ ] Terminology and stale-authority checks pass or have BM-approved non-blocking exceptions.
- [ ] DAG/Matrix current portions match the frozen stage and branch model.
- [ ] No normative document depends on private filesystem paths or review files for authority.

### Freeze transaction

- [ ] Release-candidate evidence reviewed by VQ, TL, RM, and BM.
- [ ] BM signed go/no-go record says Go.
- [ ] Freeze commit contains all accepted normative changes in one commit.
- [ ] QA rerun against freeze commit is green.
- [ ] SHA-256 manifest records exact normative files.
- [ ] Annotated `benchmark-spec-v1.0-freeze` tag resolves to freeze commit.
- [ ] No public `benchmark-spec-v1.0` tag is created until M5 packaging passes.

The following do **not** gate specification freeze: RIP v1 implementation selections, pipeline code,
VAL-01, corpus construction, baseline results, human evaluation, fixed corpus-size floors, or public
corpus artifacts.

---

## 7. Release and stop rules

- RM stops a milestone when a dependency is not accepted, required evidence is missing, or a Blocker is
  discovered. RM records owner and next decision date; no silent waiver exists.
- BM alone may accept or reject an ADR/specification outcome.
- A failed M3 check returns to its owning V1 work package. It does not receive an exception at M4.
- Post-freeze semantic defects do not receive in-place edits. They enter the accepted ADR/versioning
  process and may require a new specification/corpus version.
- Terminal VAL-01 failure invokes Charter §6. No corpus construction begins until the disposition is
  accepted.
- Public specification release never implies corpus readiness. Public corpus release requires M10 and
  M11 evidence independently.
- A license or redistribution uncertainty is a publication no-go even when technical checks pass.

---

## 8. Accepted-audit disposition

Every accepted technical finding and supporting governance finding is mapped below. “Resolved” means the
execution defect is removed from this plan; it does not falsely claim that the scheduled specification or
implementation work is already complete.

| Finding | Disposition in this plan | Status |
|---|---|---|
| RPTA-001 | §0 removes plan authority over specifications/ADRs. | Resolved |
| RPTA-002 | V1-006 is a neutral decision package; former ADR-006 solution is not pre-decided. | Resolved |
| RPTA-003 | §2.2 makes BM classify every normative change; WS labels no longer assert seven-only semantics. | Resolved |
| RPTA-004 | §1 and V1-001 assign DRI/approver before any work. | Resolved |
| RPTA-005 | §2.1 defines issue-level fields; V1-001 creates all issues. | Resolved |
| RPTA-006 | M1 decision work is separated from M2 amendment work. | Resolved |
| RPTA-007 | Backlog separates governance, spec closure, synchronization, freeze, and publication. | Resolved |
| RPTA-008 | RIP contract is V1-024; implementation inception is V1-038–043 with no duplicate Phase A. | Resolved |
| RPTA-009 | M8 pilot validation and M10 post-corpus validation are separate; M9 is explicit. | Resolved |
| RPTA-010 | M5 public specification and M12 public corpus are distinct releases. | Resolved |
| RPTA-011 | Internal freeze tag and public specification tag are separate. | Resolved |
| RPTA-012 | V1-003 owns Git restoration before freeze. | Resolved |
| RPTA-013 | §4 uses milestone-level dependencies and parallel lanes. | Resolved |
| RPTA-014 | §6 removes non-contractual/future work from freeze gate. | Resolved |
| RPTA-015 | §2.3 and §6 specify exact evidence files and measurable checks. | Resolved |
| RPTA-016 | V1-008 routes D1 terminology through ADR/classification; plan chooses no name. | Resolved |
| RPTA-017 | V1-007 routes authority precedence through governance decision. | Resolved |
| RPTA-018 | Fixed size floors removed from freeze; future issue unless separately approved. | Resolved |
| RPTA-019 | Human protocol removed from v1 closure and retained only as future work. | Resolved |
| RPTA-020 | V1-028 and V1-030 preserve `04` as non-normative. | Resolved |
| RPTA-021 | V1-038–043 create implementation design, CI, fixtures, and acceptance traceability. | Resolved |
| RPTA-022 | M7/V1-044 is the formal implementation authorization gate. | Resolved |
| GOV-01 | V1-047 owns empirical causal-control validation but does not prescribe its scientific method. | Resolved |
| SEM-01 | V1-008 sends D1 terminology to governance rather than accepting the review's preferred rename. | Resolved |
| MAINT-01 | V1-039 and V1-050 require pinned deterministic scope/realized hashes and rebuild evidence. | Resolved |
| SCOPE-01 | §4 explicitly parallelizes independent synchronization and engineering preparation. | Resolved |

---

## 9. Immediate execution order

The team can begin without clarification:

1. RM opens V1-001 and records role holders.
2. EL executes V1-003 while SO executes V1-002.
3. RM creates issues V1-004…054 with §2.1 fields and assigns the listed DRIs/approvers.
4. When V1-002 is accepted, SO starts V1-004…008 in parallel; BM schedules ratification reviews.
5. Independent QA/editorial preparation for V1-027–030 may start, but decision-dependent outputs cannot
   be accepted before their dependencies.
6. No normative pipeline coding or pilot execution starts before V1-044.

## Technical Release Readiness

Ready for Execution
