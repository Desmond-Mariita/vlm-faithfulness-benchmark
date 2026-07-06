# Technical Audit — Benchmark v1.0 Release Plan

**Document reviewed:** `docs/design/Benchmark_v1.0_Release_Plan.md`  
**Audit date:** 2026-07-01  
**Review posture:** technical program management for specification closure and implementation transition. This audit does not re-review benchmark science or redesign the benchmark.

## 1. Scope

The document is partly a release plan and partly an unratified specification/governance layer.

It remains within release-plan scope when it:

- consolidates findings into a backlog;
- groups work into workstreams;
- records gates and exit criteria;
- distinguishes specification freeze from corpus validation;
- identifies implementation and publication follow-up.

It crosses into specification or governance when it:

- declares itself “authoritative” and says it governs disagreements with other documents;
- accepts all review findings without naming the accepting authority;
- prescribes the content and routing of ADR-006 before that ADR exists;
- decides that Q3 closes without an ADR and that DM Q4 closes by a particular altitude split;
- mandates new evidence-region, localization-control, identity-opacity, scorecard, conformance, size-floor, human-protocol, artifact-ownership, and authority-precedence rules;
- directs a D1 schema/name change and a Charter/README precedence ladder;
- declares which documents are normative despite conflicting document metadata, including treating non-normative `04` as normative;
- states that its plan-level classifications determine what changes benchmark semantics.

A release plan may schedule these decisions and amendments. It must not itself make them or outrank the specifications and accepted ADRs.

## 2. Workstream Quality

| Workstream | Assessment | Required correction |
|---|---|---|
| **WS-1 — Benchmark Decisions** | **Incomplete; incorrectly scoped; should be split.** REL-001–003 are decision records. REL-004–007 are a mixture of open design analysis, registry cleanup, and specification amendments. The workstream gives outcomes but no decision owner, decision deadline, alternatives package, approval meeting, or amendment acceptance evidence. | Split into **Decision Resolution** (questions, owner, ADR, ratification) and **Specification Amendment** (approved decision applied and verified). Do not call an outcome decided until its owning authority accepts it. |
| **WS-2 — Repository Synchronization** | **Incorrectly scoped; should be split.** It contains mechanical synchronization, normative specification changes, governance creation, editorial cleanup, publication cleanup, and the freeze act. Several items are not synchronization at all. | Split into **Governance Bootstrap**, **Normative Synchronization**, **Supporting-Document Regeneration**, **Editorial/Link QA**, and **Freeze Execution**. Move public packaging out. |
| **WS-3 — Reference Implementation Preparation** | **Incomplete; should be split; partly duplicated.** It mixes a spec-side RIP contract, an implementation-side RIP instance, responsibility assignment, architecture constraints, acceptance planning, and executable boundary tests. Post-freeze Phase A repeats the same work. | Put the RIP artifact contract in specification closure. Make responsibility assignment a program-start prerequisite. Replace WS-3/Phase A duplication with one implementation-inception workstream containing repositories, interfaces, test harness, acceptance matrix, and pilot-ready pipeline deliverables. |
| **WS-4 — Validation Experiments** | **Wrong dependency; should be split.** VAL-01 is a pilot gate before mass labeling. REL-035/036 need an implemented pilot and approved profile. REL-037 needs a candidate corpus and S18 manifest, which do not exist immediately after WS-3. | Split into **Pilot Viability Validation** before corpus construction and **Release Validation/Rebuild** after candidate-corpus construction. Add the missing corpus-construction node between them. |
| **WS-5 — Public Release Preparation** | **Incomplete; incorrectly scoped.** It combines publication of the specification repository with later publication of the corpus, baselines, and report. REL-040 also contains a pre-freeze document edit. | Split **Specification Repository Packaging** from **Corpus Release Packaging**. Move pre-freeze normative/supporting-document cleanup to WS-2. Give legal/licensing review an owner and gate. |

No workstreams should be merged in their current form. The spec-side portions of REL-027/028 should merge into specification closure; the implementation-side portions should remain in implementation inception.

## 3. Dependency Graph

The graph has no explicit circular edge, but it is incomplete and too coarse to execute.

### Missing or incorrect dependencies

- **Responsibility assignment precedes all work**, not merely implementation milestones. ADR ratification, specification edits, freeze approval, archival decisions, and legal packaging already require accountable owners.
- **WS-1 and WS-2 are not fully sequential.** Governance bootstrap must precede ratification, and decision-dependent synchronization follows decisions, but link repair, archival preparation, editorial QA, and most packaging can run in parallel. The prose admits this; the graph does not represent it.
- **Non-semantic implementation scaffolding need not wait for the full freeze.** The plan itself says it may begin now, but the graph makes all WS-3 depend on WS-2.
- **REL-034 depends on a working pilot pipeline and RIP instance**, not merely “reference implementation preparation.”
- **REL-035/036 depend on ADR-006, the RIP, and pilot artifacts.** Their inputs and acceptance datasets are not identified.
- **REL-037 depends on a candidate corpus, complete manifest, and S18 release transaction.** The graph places it before corpus construction.
- **Corpus construction is missing from the workstream graph.** It appears only later as Roadmap Phase C.
- **Baseline/evaluation implementation is missing from the graph.** It appears only as Phase E, despite scorecard and harness readiness being major implementation deliverables.
- **Specification-repository publication and corpus publication need separate terminal nodes.** WS-5 currently points toward “Public release of corpus” even though most WS-5 tasks package the specification repository.
- **The release tag depends on packaging if it is the public v1.0 tag.** The current checklist tags at freeze while README, LICENSE, archive cleanup, and release notes occur later.

### Unnecessary dependency

- Requiring all WS-2 work before any WS-3 activity unnecessarily blocks repository scaffolding, CI, schema prototypes, synthetic fixtures, and non-semantic harness plumbing.

## 4. Benchmark Governance

The plan generally respects ADR-002 and ADR-003 and correctly treats their base-document synchronization as required. It does not reopen their accepted decisions.

Governance problems remain:

- The plan assigns itself authority that only specifications, ADRs, and the project governance process can hold.
- Review recommendations are treated as accepted decisions. Reviews are evidence, not ratification.
- ADR-006's proposed contents are pre-decided in the backlog, including ownership movement and new route/control rules.
- REL-019 may alter a published reason-code name; REL-020 introduces a global authority hierarchy; both require governance treatment beyond “repository synchronization.”
- REL-022 makes corpus/split/hard-core floors a freeze requirement even though the existing specifications intentionally defer per-release constants.
- REL-023 uses normative “MUST” language inside a proposed non-normative note.
- The plan says material changes to itself require a dated revision, but it does not identify who approves that revision or whether plan revisions need an ADR.

## 5. Engineering Readiness

An engineering team could use the findings register for orientation, but could not execute the plan as a controlled program yet.

Missing program deliverables:

- accountable owner and approver for every REL item;
- target milestone/date and effort estimate;
- issue/PR linkage and status model;
- per-item acceptance evidence, not only workstream exit prose;
- explicit specification-freeze milestone versus public specification-release milestone;
- implementation repository/bootstrap decision;
- code ownership, CI, test framework, supported environment, dependency management, and artifact locations;
- interfaces/schemas or a named implementation-design deliverable for S01–S19;
- synthetic fixture set and golden conformance cases;
- pilot entry/exit criteria and sample ownership;
- risk register with mitigation, trigger, and owner;
- legal owner for source/model/output licenses;
- decision log showing which review recommendations were accepted, rejected, or deferred by whom.

The workspace is not currently an operational Git repository: `.git` is an empty directory and `git rev-parse` fails. REL-026's tagged atomic commit is therefore not executable until repository initialization or migration is explicitly completed.

## 6. Repository Freeze

The checklist has good coverage of known specification findings, but it is neither minimal nor fully measurable.

### Remove or move

- Move size-floor policy, human-evaluation guidance, general editorial normalization, publication archive cleanup, and other non-contractual improvements out of the freeze gate unless the owning specification authority explicitly marks them release-blocking.
- Remove “no document body asserts a false repository fact” as a checklist item; replace it with named files and automated checks.
- Remove explanatory unchecked boxes under Implementation/Validation/Publication. They are not freeze criteria and make checkbox state ambiguous.
- Do not call `04` normative unless its metadata/authority is deliberately changed.

### Add or make measurable

- Enumerate the exact normative document set and required status/version for each; “01–11” is ambiguous because numbering is non-contiguous and includes `06a`.
- Require an ADR index with statuses and a check that every accepted ADR amendment is present.
- Require zero unresolved freeze-blocking registry entries, with a generated report.
- Require automated internal-link, metadata, terminology, and stale-status checks, with stored output.
- Require a clean repository state and a functioning Git repository before the freeze commit.
- Require named freeze approver(s), recorded sign-off, and rollback criteria.
- Require a freeze manifest containing document hashes and the exact tag/commit.
- Separate an **internal specification freeze tag** from the **public v1.0 release tag**, or complete README/LICENSE/archive/release notes before using `v1.0` publicly.
- State whether post-freeze RIP v1 can expose an omission in the frozen contract and what governance path handles it.

## 7. Implementation Transition

The document does not yet complete the handover.

It correctly states that semantic implementation must wait for a closed contract, that thesis code is capability rather than authority, and that validation gates corpus construction. Those are strong transition principles.

The handover fails operationally because:

- there is no owner before the handover starts;
- WS-3 and Roadmap Phase A duplicate each other;
- no implementation design/interface milestone exists between prose specifications and S01–S19 coding;
- pilot validation and release validation are collapsed into one workstream;
- corpus construction is absent from the main dependency graph;
- the acceptance matrix is deferred until implementation start instead of being seeded from freeze criteria;
- the tag/release sequence cannot produce one coherent v1.0 artifact;
- issue tracking, schedule, resource assumptions, and risk ownership are absent.

The plan should end at an explicit implementation-inception gate: frozen specification set, ratified decisions, named implementation owner, approved RIP contract, seeded acceptance matrix, working repository/CI, and authorized first implementation milestone. Corpus construction and public corpus release should be a separate implementation/release plan.

## Findings

### RPTA-001

- **Severity:** Blocker
- **Section:** Preamble; §2; §4
- **Description:** The plan declares itself authoritative, says it governs disagreements, and accepts all review findings. A planning document has no authority to supersede specifications, accepted ADRs, or governance decisions.
- **Recommendation:** Limit authority to backlog status and scheduling. State that specifications and accepted ADRs govern technical meaning, and record the person/body that accepts findings into the backlog.
- **Recommendation classification:** Release Plan revision

### RPTA-002

- **Severity:** Blocker
- **Section:** REL-003; WS-1; §6
- **Description:** The plan pre-decides ADR-006: it assigns P6 semantic ownership, adds localization causal control, chooses E5/E6 behavior, and defines branch applicability before alternatives are considered or an ADR is ratified.
- **Recommendation:** Rewrite REL-003 as a decision question with required affected interfaces and acceptance constraints; move the proposed solution into ADR alternatives, not the release-plan baseline.
- **Recommendation classification:** Release Plan revision

### RPTA-003

- **Severity:** Major
- **Section:** Executive Summary; WS-1/WS-2 classification
- **Description:** “Seven items — and only these — change benchmark semantics” is unsupported. Boundary access, ID opacity, scorecard applicability, conformance categories, D1 naming, authority precedence, size floors, and the RIP artifact contract also alter normative contracts or governance. Conversely, stale Q3 registry cleanup may not be a semantic decision.
- **Recommendation:** Replace the semantic/non-semantic declaration with an owner-approved classification table: decision required, specification amendment, synchronization, implementation, or publication.
- **Recommendation classification:** Release Plan revision

### RPTA-004

- **Severity:** Blocker
- **Section:** All workstreams; REL-031; freeze checklist
- **Description:** No current owner or approver is assigned to any workstream or REL item. Responsibility assignment is deferred until after freeze, although pre-freeze ADRs, edits, archival actions, and tag approval already require accountable execution.
- **Recommendation:** Make a RACI/DRI assignment the first program gate and assign one accountable owner plus approver to every REL item before work begins.
- **Recommendation classification:** Release Plan revision

### RPTA-005

- **Severity:** Major
- **Section:** §2 findings register; §3 workstreams
- **Description:** The REL register is not an executable backlog: it lacks status, owner, target milestone, estimate, issue/PR, acceptance evidence, and decision/approval state. Workstream exit criteria are too coarse to substitute.
- **Recommendation:** Create tracked issues for every actionable REL item, each linked back to the plan and carrying owner, milestone, dependencies, acceptance criteria, and evidence links.
- **Recommendation classification:** GitHub issue only

### RPTA-006

- **Severity:** Major
- **Section:** WS-1
- **Description:** WS-1 mixes decision formation, ADR ratification, registry cleanup, and direct specification amendments. It therefore cannot show when a choice becomes authorized versus when it has merely been edited into text.
- **Recommendation:** Split WS-1 into decision resolution and approved-decision synchronization, with separate exit criteria.
- **Recommendation classification:** Release Plan revision

### RPTA-007

- **Severity:** Major
- **Section:** WS-2
- **Description:** WS-2 is an oversized catch-all containing governance creation, semantic specification amendments, supporting-document regeneration, editorial cleanup, publication cleanup, and freeze execution.
- **Recommendation:** Decompose WS-2 into governance bootstrap, normative synchronization, supporting-document regeneration, editorial/link QA, and freeze execution.
- **Recommendation classification:** Release Plan revision

### RPTA-008

- **Severity:** Major
- **Section:** WS-3; §7 Phase A
- **Description:** WS-3 mixes specification and implementation and is duplicated by Phase A. Its exit says the pipeline is pilot-ready, while its listed items include preparation and tests but not an explicit S01–S19 implementation deliverable.
- **Recommendation:** Merge the implementation-side WS-3 work with Phase A into one implementation-inception workstream; keep RIP contract changes in specification closure.
- **Recommendation classification:** Release Plan revision

### RPTA-009

- **Severity:** Blocker
- **Section:** WS-4; §4 graph; §7 Phases B–D
- **Description:** WS-4 combines pre-corpus viability with post-corpus reproducibility. REL-037 cannot run after WS-3 as graphed; it requires Phase C's candidate corpus, manifest, and S18 transaction. The roadmap and graph disagree.
- **Recommendation:** Split pilot validation from release validation and add corpus construction as an explicit dependency node before REL-037.
- **Recommendation classification:** Release Plan revision

### RPTA-010

- **Severity:** Major
- **Section:** WS-5; §4 graph; §7 Phase F
- **Description:** The plan conflates release of Benchmark Specification v1.0 with public release of a corpus, baselines, and scientific report. The artifacts, gates, licenses, and dates are materially different.
- **Recommendation:** Create separate milestones and plans for public specification release and public corpus release; this plan should own the former and only hand off to the latter.
- **Recommendation classification:** Release Plan revision

### RPTA-011

- **Severity:** Major
- **Section:** REL-026; freeze checklist; WS-5
- **Description:** REL-026 creates the v1.0 tag before README, LICENSE, archive cleanup, release notes, and other public packaging are complete. The later public release would therefore not match the tagged release commit.
- **Recommendation:** Either use a clearly internal freeze tag and create `v1.0` after packaging, or make public packaging prerequisites of the `v1.0` tag.
- **Recommendation classification:** Release Plan revision

### RPTA-012

- **Severity:** Blocker
- **Section:** REL-026; Repository freeze
- **Description:** The requested atomic commit/tag is currently impossible: the workspace `.git` directory is empty and Git reports that the workspace is not a repository.
- **Recommendation:** Initialize or migrate the project into the intended Git repository and verify commit/tag operations before scheduling the freeze.
- **Recommendation classification:** Implementation issue

### RPTA-013

- **Severity:** Major
- **Section:** §4 dependency graph
- **Description:** The diagram serializes entire workstreams despite the prose allowing parallel work, blocks all implementation preparation on freeze, omits corpus construction and baseline implementation, and points a mixed validation workstream directly to corpus release.
- **Recommendation:** Replace the workstream-only graph with milestone-level dependencies and explicit parallel lanes for decisions, synchronization, engineering bootstrap, packaging, pilot, corpus construction, and release validation.
- **Recommendation classification:** Release Plan revision

### RPTA-014

- **Severity:** Major
- **Section:** §5 freeze checklist
- **Description:** The freeze gate is over-loaded with requirements not yet accepted as release-blocking, including size-floor policy and plan-originated normative changes. It also includes non-gating Implementation/Validation/Publication checkboxes.
- **Recommendation:** Restrict the checklist to accepted specification closure, consistency, governance, and release-integrity conditions; move future and non-gating items to a handoff checklist.
- **Recommendation classification:** Release Plan revision

### RPTA-015

- **Severity:** Major
- **Section:** §5 freeze checklist
- **Description:** Several checks are not measurable: “no false claim anywhere,” “every normative document,” and “every open question” lack an enumerated input set, command, report, or evidence owner.
- **Recommendation:** Define a freeze manifest and automated QA report listing exact files, expected metadata, ADR status/application, registry state, links, and hashes; require recorded sign-off.
- **Recommendation classification:** Release Plan revision

### RPTA-016

- **Severity:** Major
- **Section:** REL-019; WS-2
- **Description:** Renaming D1 is treated as synchronization even though the label specification fixes the diagnostic name and the plan itself says a post-freeze change would be breaking. The release plan cannot authorize that schema-facing change.
- **Recommendation:** Resolve whether the D1 name is part of stable label semantics through a decision record before any rename; a non-semantic clarification may then be applied without changing the code value.
- **Recommendation classification:** ADR

### RPTA-017

- **Severity:** Major
- **Section:** REL-020; WS-2; REL-039
- **Description:** A global precedence ladder changes project governance and may alter the Charter's relationship to formal definitions and ADRs. Scheduling it as a README/Charter edit lets the plan invent authority ordering.
- **Recommendation:** Ratify the authority-precedence model through the governance decision process before publishing it in the Charter or normative conventions.
- **Recommendation classification:** ADR

### RPTA-018

- **Severity:** Major
- **Section:** REL-022; freeze checklist
- **Description:** The plan turns absence of corpus/split/hard-core size floors into a mandatory pre-freeze decision. Existing specifications intentionally allow per-release statistical thresholds; the reviews did not establish that fixed floors are necessary benchmark semantics.
- **Recommendation:** Remove REL-022 from the unconditional freeze gate. If owners want a minimum-support policy, process it through the owning evaluation/dataset specifications with rationale and compatibility analysis.
- **Recommendation classification:** Release Plan revision

### RPTA-019

- **Severity:** Minor
- **Section:** REL-023
- **Description:** The plan proposes adding a non-normative note that says human evaluation “MUST” follow a new instruction protocol. That is a new normative requirement disguised as guidance and is irrelevant to v1.0 because human performance is explicitly out of scope for the initial release.
- **Recommendation:** Defer it to the future human-evaluation issue already identified for v1.1/later; do not add it to v1.0 specification closure.
- **Recommendation classification:** GitHub issue only

### RPTA-020

- **Severity:** Minor
- **Section:** REL-040; freeze checklist
- **Description:** The plan repeatedly calls `docs/04_Legacy_Terminology_Mapping.md` normative, but its frontmatter and body explicitly mark it non-normative. Rewriting private-path evidence may be useful publication cleanup, but it is not a normative freeze amendment on current authority.
- **Recommendation:** Correct the authority classification and place `04` cleanup in supporting-document/publication QA unless its status is separately changed.
- **Recommendation classification:** Release Plan revision

### RPTA-021

- **Severity:** Major
- **Section:** §5–§7 implementation handoff
- **Description:** There is no implementation-design milestone between frozen prose and coding S01–S19. The plan names an acceptance matrix and RIP but not component interfaces, schema ownership, error model, storage boundaries, CI, fixtures, or test strategy.
- **Recommendation:** Add an implementation-inception milestone producing the architecture/interface design, repository bootstrap, CI, synthetic fixtures, and traceability from every conformance requirement to an executable or attested check.
- **Recommendation classification:** Release Plan revision

### RPTA-022

- **Severity:** Major
- **Section:** Executive Summary; §6; §7
- **Description:** The plan claims implementation begins after freeze, yet responsibility assignment, the RIP instance, acceptance criteria, and repository setup all occur afterward. The first engineering milestone therefore opens without the prerequisites needed to control it.
- **Recommendation:** Define a formal implementation authorization gate after freeze and before normative coding, with named owner, approved RIP instance, seeded acceptance matrix, working repository/CI, and authorized first milestone.
- **Recommendation classification:** Release Plan revision

## Executive Verdict

### 1. Is this document an appropriate Release Plan?

Not yet. It is a strong synthesis and backlog source, but it lacks the ownership, milestone mechanics, evidence model, and correctly separated release targets required of an executable plan.

### 2. Has it accidentally become normative?

Yes. It claims governing authority, accepts review recommendations, pre-decides ADR content, and mandates multiple specification and governance rules.

### 3. Would you approve it for implementation planning?

No. I would approve a revised version after authority is narrowed, decisions are separated from amendments, owners and issue milestones are assigned, the dependency graph is corrected, and specification freeze is separated from corpus/public release.

## Executive Verdict: Requires Revision

The findings register is valuable and most underlying blockers are correctly identified. The execution model is not approvable because it is simultaneously a plan, an unratified decision record, a specification amendment list, an implementation roadmap, and a corpus-release roadmap. The most serious defects are plan-level authority over technical meaning, pre-decided ADR-006 content, absent ownership, an incorrect validation/corpus dependency, and a freeze/tag sequence that cannot produce the intended public v1.0 artifact. These are repairable through release-plan revision; rejection of the overall program is not warranted.
