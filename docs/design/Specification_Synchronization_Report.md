# Specification Synchronization Report

**Sprint:** Final Specification Synchronization
**Date:** 2026-07-01
**Authoritative inputs:** `reviews/codex/specification_phase_audit.md`,
`reviews/gemini/specification_phase_conceptual_review.md`
**Revision:** governance refinement (2026-07-01) — reclassifies operational/release decisions out of the
ADR category to prevent ADR inflation; no technical finding removed, no depth reduced.
**Scope:** synchronize, validate, and prepare for implementation. **No redesign.** No new benchmark
concepts. Accepted architectural decisions are **not** reopened.

> **Purpose.** The benchmark's philosophy, ontology, semantics, governance, and architecture are
> **complete and stable**. This report determines what must happen for the repository to be internally
> **self-consistent** and **implementation-ready**. It classifies every review finding, states which the
> maintainer accepts (not all reviewer recommendations survive evaluation against the benchmark
> philosophy), and sequences the work. This revision tightens the governance model: a decision is an ADR
> **only** when it genuinely alters benchmark **semantics or ontology**; corpus-construction, pipeline-
> operational, and release-policy choices are **specification amendments** or **implementation work**.

## 0. Classification legend and method

| Category | Meaning |
|---|---|
| **A — Already Resolved** | No action, or resolved by existing design/governance; reviewer over-flagged. |
| **B — Repository Synchronization** | Document edits/amendments to make the repository self-consistent. **No new semantics.** |
| **C — Requires Explicit Benchmark Decision** | A genuine choice that alters benchmark **semantics or ontology**; needs a ratified **ADR**. |
| **D — Future Implementation Work** | Engineering or research, post-specification; inventory-backed, not speculative. |

Every finding is additionally tagged with the **action type** it requires: *document synchronization /
specification amendment · ADR · implementation guidance · empirical validation · no action.*

**Governance refinement (this revision).** Only decisions that change what a label *means* or what the
benchmark's *subject/ontology* is remain ADRs. Consequently:

- **Answer-correctness policy (Q1)** and **composite-generator policy (Q4)** remain **ADRs** — Q1 changes
  benchmark membership and therefore the scientific construct; Q4 changes benchmark subject identity.
- **Hard-core membership** → **Dataset Specification amendment** (corpus-construction policy, not
  architecture).
- **Condition-B inconclusive routing** → **Pipeline specification amendment** (operational behaviour
  within the accepted architecture; adds no behavioural state — the S1/S2/S3 ontology is frozen and Q3 is
  resolved as binary-B).
- **Audit-view release policy** → **Dataset Specification amendment** (release policy, not an
  architectural concern; the information boundary itself is unchanged).
- **Intervention methodology** → split: **(A) Benchmark Principle** already covered by existing
  philosophy and assurance (no ADR); **(B) Reference Implementation Profile** is implementation +
  empirical validation (no ADR until benchmark semantics themselves change).

**Verified repository facts** (grounding the classifications): `docs/00_Benchmark_Charter.md` and
`VISION.md` are **absent**; ADR-002 is marked **Proposed**; ADR-003 is **Accepted** but `05/06/06a` do
**not** reference it (amendments unapplied); base specs are **Draft**; `09_Baselines.md` is referenced by
`01` and `05` though the file is `09_Baseline_Systems.md`.

## 1. Finding classification

### 1.1 Summary

| ID | Origin | Cat | Requires | Blocks impl. |
|---|---|:--:|---|:--:|
| SPA-001 / REV-01 | Codex+Gemini | **B** | doc synchronization | **Yes** |
| SPA-002 / REV-03 | Codex+Gemini | **C** | ADR ×2 (Q1, Q4); DS amendment (Q2); no action (Q3, frozen) | Yes (Q1/Q4 stages) |
| SPA-003 / REV-02 | Codex+Gemini | **D** | implementation profile + empirical validation (no ADR) | Mass labeling (validation-gated) |
| SPA-004 | Codex | **B** | doc synchronization | **Yes** |
| SPA-005 | Codex | **B** | doc synchronization | **Yes** |
| SPA-006 | Codex | **B** | doc synchronization | **Yes** |
| SPA-007 | Codex | **B** | doc synchronization | Yes (baselines/scoring) |
| SPA-008 | Codex | **B** | doc synchronization | **Yes** (BL8) |
| SPA-009 | Codex | **B** | doc synchronization | **Yes** (BL8) |
| SPA-010 | Codex | **B** | **Dataset Specification amendment** | Yes (corpus assembly/eval) |
| SPA-011 | Codex | **B** | **Pipeline specification amendment** | Yes (pipeline) |
| SPA-012 | Codex | **B** | doc synchronization + impl guidance | Yes (generation) |
| SPA-013 | Codex | **B** | doc synchronization + impl guidance | Release-time |
| SPA-014 | Codex | **B** | **Dataset Specification amendment** | Release-time |
| SPA-015 | Codex | **B** | doc synchronization + impl guidance | Yes (assembly) |
| SPA-016 | Codex | **B** | doc synchronization | Yes (scoring) |
| SPA-017 | Codex | **B** | doc synchronization + impl guidance | Release-time |
| SPA-018 | Codex | **D** | implementation guidance + minor doc sync | No |
| SPA-019 | Codex | **D** | implementation guidance | No |
| SPA-020 | Codex | **B** | doc synchronization + impl guidance | Release-time |
| SPA-027 | Codex | **B** | doc synchronization | Yes (routing determinism) |
| SPA-021 | Codex | **B** | doc synchronization | No (should precede) |
| SPA-022 | Codex | **B** | doc synchronization | No |
| SPA-023 | Codex | **B** | doc synchronization | No |
| SPA-024 | Codex | **D** | implementation guidance | No |
| SPA-028 | Codex | **B** | doc synchronization | No |
| SPA-025 | Codex | **A** | no action | No |
| SPA-026 | Codex | **D** | implementation guidance | No |
| REV-04 | Gemini | **B** | doc synchronization | No |
| REV-05 | Gemini | **A** | no action | No |

Counts: **A = 2 · B = 22 · C = 1 · D = 5.** The single remaining **C** row carries the only two genuine
architectural decisions (Q1, Q4). Blockers to **implementation start**: the B-contradictions
(SPA-004/005/006/008/009 + SPA-001) and the two Q1/Q4 decisions gating their stages.

### 1.2 Detailed findings — the specifically-evaluated set

Each entry: **Origin · Category · Current status · Assessment · Recommended action · Owner ·
Implementation impact · Blocks implementation · Requires.** Technical analysis is unchanged from the
reviewed report; only the governance classification is refined where noted.

---

**Missing Charter — SPA-001 / REV-01**
- **Origin:** Codex + Gemini. **Category:** B.
- **Current status:** `docs/00_Benchmark_Charter.md` absent; content exists, ratified, inside
  `Repository_Scaffolding_Proposal.md` §6.4.
- **Assessment:** Accepted. This is synchronization, not a decision — the Charter is approved; it was
  never instantiated as a standalone file. Every `Charter §4–§6` citation is currently unverifiable.
- **Recommended action:** Instantiate `docs/00_Benchmark_Charter.md` verbatim from the ratified §6.4
  draft (Status `Accepted`).
- **Owner:** Specification Owners / Maintainer.
- **Implementation impact:** Restores the governance authority all specs cite.
- **Blocks implementation:** **Yes** — the repo is not self-consistent without it.
- **Requires:** document synchronization.

**Missing Vision — SPA-001 / REV-01**
- **Origin:** Codex + Gemini. **Category:** B.
- **Current status:** `VISION.md` absent; content ratified in `Repository_Scaffolding_Proposal.md` §9.2.
- **Assessment:** Accepted; identical rationale to the Charter.
- **Recommended action:** Instantiate `VISION.md` from the ratified §9.2 draft.
- **Owner:** Specification Owners / Maintainer.
- **Implementation impact:** Restores the purpose/success-stop authority.
- **Blocks implementation:** **Yes**.
- **Requires:** document synchronization.

**ADR synchronization — SPA-008 (ADR-003), SPA-009 (ADR-002)**
- **Origin:** Codex. **Category:** B.
- **Current status:** ADR-002 marked `Proposed` though relied on normatively; ADR-003 `Accepted` but its
  §5 amendments to `05 §19`, `06 P1/E1`, `06a §§3.2–3.3/3.8/4/6/8` are unapplied; DAG still shows
  G1/G2 unresolved.
- **Assessment:** Accepted and required. `11` BL8 explicitly blocks releases while accepted ADR
  amendments are unapplied; the base model currently contradicts ADR-003 (still demands a complete
  Output Tuple before candidacy). This is synchronization of **already-accepted** decisions, not new
  architecture.
- **Recommended action:** Set ADR-002 `Status: Accepted`; apply its N1–N4 cross-references. Apply every
  ADR-003 §5 amendment. Mark DAG G1 and G2 resolved.
- **Owner:** Specification Owners.
- **Implementation impact:** Removes the highest-risk documentation contradiction.
- **Blocks implementation:** **Yes** (BL8).
- **Requires:** document synchronization.

**Canonical rationale representation — SPA-012**
- **Origin:** Codex. **Category:** B.
- **Current status:** "The rationale" is not pinned to a span; the legacy mapping defers it to a
  downstream schema decision, which `08` never makes.
- **Assessment:** Accepted; genuine gap. Output-Tuple identity, P1/P2, Condition B, predictor input, and
  reproducibility all depend on the exact text object. This is a *representation* decision owned by `08`
  (Output Tuple shape) — not a change to the `rationale` concept (FD §6), so it is synchronization, not a
  semantic ADR.
- **Recommended action:** `08` fixes the canonical emitted-rationale representation and its relation to
  raw generator output.
- **Owner:** `08` Owner.
- **Implementation impact:** Fixes the exact object every generation-side stage binds to.
- **Blocks implementation:** Yes (generation, Condition B).
- **Requires:** document synchronization + implementation guidance (per-generator parsing).

**Answer correctness policy — SPA-002 (Q1) / REV-03  — RETAINED AS ADR**
- **Origin:** Codex + Gemini. **Category:** C.
- **Current status:** Open (Label Specification §14 Q1).
- **Assessment:** Accepted as a genuine architectural decision. **Whether correctness is a candidacy
  precondition, an eligibility gate, or a stratification slice changes benchmark membership and therefore
  the scientific construct** — this is precisely the kind of decision that must be an ADR.
- **Recommended action:** Ratify **ADR-004** resolving Q1; synchronize `06/06a/07/08/10`.
- **Owner:** Maintainer (ADR) → Specification Owners (sync).
- **Implementation impact:** Determines which candidates are labelled.
- **Blocks implementation:** Yes (eligibility stages).
- **Requires:** **ADR.**

**Composite generators — SPA-002 (Q4)  — RETAINED AS ADR**
- **Origin:** Codex. **Category:** C.
- **Current status:** Open (Label Specification §14 Q4). The thesis generator is exactly the composite
  Stage-1/Stage-2 case.
- **Assessment:** Accepted as a genuine architectural decision. **Whether the two-checkpoint pipeline is
  one valid subject changes benchmark subject identity** (FD §1) and every observation stage — an
  ontology-level call, correctly an ADR.
- **Recommended action:** Ratify **ADR-005** resolving Q4; synchronize `06a §3.3/§6`, `07 S02–S03`.
- **Owner:** Maintainer (ADR).
- **Implementation impact:** Fixes the subject identity intervened upon.
- **Blocks implementation:** Yes (generation/observation).
- **Requires:** **ADR.**

**Intervention methodology assumptions — SPA-003 / REV-02 (OOD intervention risk)  — RECLASSIFIED (no ADR)**
- **Origin:** Codex + Gemini. **Category:** D (was C).
- **Current status:** `07` defers the intervention set, localization, controls, and Condition A/B criteria
  to implementation; REV-02 warns targeted edits may cause OOD encoder collapse mislabelled as
  unfaithfulness.
- **Assessment (technical, unchanged):** There need **not** be a globally unique candidate→label
  function: the benchmark's reproducibility model is *re-derivable from the manifest on a pinned
  environment* (Benchmark Design §10), and the largest research risk is that a chosen intervention causes
  OOD collapse rather than a semantic shift. **Governance refinement:** this splits into two concerns,
  **neither an ADR**:
  - **A — Benchmark Principle.** The requirement that a new intervention methodology be pinned and
    versioned is **already covered** by existing benchmark philosophy (Benchmark Design §10) and
    assurance (`11 §9` classifies a new intervention methodology as an ADR-gated, versioned trigger). No
    **new** ADR is required now, and no semantic change occurs.
  - **B — Reference Implementation Profile.** Selecting the concrete intervention set/parameters is an
    **implementation responsibility**; **empirical validation** (the viability probe) determines whether
    the chosen methodology satisfies the benchmark's assumptions (semantic shift, not OOD collapse). **No
    architectural decision is required unless benchmark *semantics themselves* change** — at which point
    the existing governance (Charter §4/§5; `11 §9`) already mandates an ADR at that time.
- **Recommended action:** Run the viability probe (**validation experiment VAL-01**); record the chosen
  methodology as a **Reference Implementation Profile** in implementation documentation (**IN-01**). No
  ADR now.
- **Owner:** Implementation Team + Research validation.
- **Implementation impact:** Gates all label production.
- **Blocks implementation:** Mass labeling only (validation-gated); not pipeline scaffolding or coding.
- **Requires:** implementation guidance + empirical validation.

**P6 routing — SPA-004**
- **Origin:** Codex. **Category:** B.
- **Current status:** `06 §3` lists P6 for every eligible instance; `07` routes an A-false candidate
  straight to S1/D1, so P6 is never tested on that branch.
- **Assessment:** Accepted; genuine contradiction. A determinate "answer is not image-dependent" is itself
  a causal reading that P6 exists to license. Making `07` test P6 before assigning S1 conforms to `06 §3`
  **without** changing P6 or D1 meaning — pure synchronization. *(If, instead, the team decides P6 is
  inapplicable to S1, that scope narrowing would require an ADR — flagged as a contingency.)*
- **Recommended action:** Reconcile `07 §§5–6` so P6 gates the A-determination for both branches; an
  A-false candidate failing P6 routes to E6, not S1. Update the DAG §6 sub-dependencies.
- **Owner:** `07` Owner.
- **Implementation impact:** Prevents D1 from an unlicensed causal reading.
- **Blocks implementation:** **Yes** (pipeline).
- **Requires:** document synchronization.

**Information boundary — SPA-014 (audit) · SPA-007 · REV-04**
- **Origin:** Codex + Gemini. **Category:** SPA-014 = B (was C); SPA-007 = B; REV-04 = B.
- **Current status:** (SPA-014) `08 §14` permits publishing a joinable audit view; a public artifact
  joinable by stable ID hands a predictor the answer key. (SPA-007) Train/Val label-access contracts
  conflict across `08/09/10`. (REV-04) OOD-Model split membership could be used as a latent-style feature.
- **Assessment:** All accepted. (SPA-014, technical unchanged) is a real hole — logical "never a predictor
  input" markers do not stop a public join. **Governance refinement:** constraining the audit view's
  *release timing/joinability* is a **release policy**, not an architectural concern — the information
  boundary itself (BD §11) is unchanged — so it is a **Dataset Specification amendment**, not an ADR.
  SPA-007 is synchronization: Train labels are training material (FD §24), Val/OOD labels are hidden, and
  the **evaluation harness** (not the predictor) freezes the operating point on Val — clarify, no boundary
  change. REV-04 is a one-line clarification that split membership is scoring-stratification only.
- **Recommended action:** SPA-014 → **Dataset Specification amendment** fixing audit-view release
  timing/joinability; sync `08 §14/10/11`. SPA-007 → sync `08 §§12–13/09 §5/10 §§2,4`. REV-04 → clarify
  `10 §2` and `08 §12.1`.
- **Owner:** `08` Owner (SPA-014, SPA-007) + `10` Owner (SPA-007, REV-04).
- **Implementation impact:** Protects the benchmark's core boundary integrity.
- **Blocks implementation:** SPA-007 Yes (baselines/scoring); SPA-014 release-time; REV-04 No.
- **Requires:** SPA-014 Dataset Specification amendment; SPA-007 document synchronization; REV-04 document
  synchronization.

**Split policy — SPA-006 · SPA-015**
- **Origin:** Codex. **Category:** B.
- **Current status:** (SPA-006) `08` N6.3 (scene-grouping across *all* splits) contradicts N7.2 (OOD-Model
  accepts shared scenes across generators). (SPA-015) `source scene`, `generator family`, and cross-dataset
  `question type` lack canonical identity relations.
- **Assessment:** Accepted; both synchronization. SPA-006 has an already-established resolution (assessment
  A4): scene-grouping-across-splits governs Train/Val/OOD-QType/OOD-Dataset, while **OOD-Model is
  generator-disjoint with accepted, documented image overlap** (full image-disjointness is impossible, not
  a defect). Qualify N6.3 and align assurance BL3/DF1. SPA-015 refines identity relations for *existing*
  artifacts (not a new ontology) → `06a/08` define the scene/family/qtype identity contracts.
- **Recommended action:** Sync `08 N6.3/N7.2` + `11 BL3/DF1`; define identity/mapping contracts in
  `06a/08`.
- **Owner:** `08` Owner (with `06a`).
- **Implementation impact:** Makes split disjointness and leakage tests satisfiable and auditable.
- **Blocks implementation:** Yes (corpus assembly).
- **Requires:** document synchronization + implementation guidance (the concrete mappings).

**Hard-core definition — SPA-010  — RECLASSIFIED (Dataset Specification amendment, no ADR)**
- **Origin:** Codex. **Category:** B (was C).
- **Current status:** FD §30 defines the hard core as *unfaithful-only* (single-class); `10` requires AUROC
  and thus a *balanced* set with matched hard positives; no operational plausibility/grounding selector is
  fixed.
- **Assessment (technical, unchanged):** Genuine contradiction — AUROC is undefined on a single-class set;
  the balanced-hard-core resolution is the established design (assessment A1). **Governance refinement:**
  this is **corpus-construction policy, not benchmark architecture.** The hard-core *concept* (FD §30)
  already exists and is not being changed; only its **construction/membership contract** must be fixed
  (balanced set, selection inputs, matching/balance rule, pinned membership) — owned by `08`. FD §30
  receives only a clarifying synchronization noting the concept encompasses matched positives so AUROC is
  defined. No ADR.
- **Recommended action:** **Dataset Specification amendment** fixing the balanced hard-core membership
  contract (selectors, matching, balance, pins); clarifying sync to FD §30; align `09/10/11`.
- **Owner:** `08` Owner (with a FD §30 sync by Formal-Definitions owner).
- **Implementation impact:** Makes the headline discriminative claim reproducible.
- **Blocks implementation:** Yes (corpus assembly + evaluation).
- **Requires:** Dataset Specification amendment (document synchronization).

**Manifest completeness — SPA-013**
- **Origin:** Codex. **Category:** B.
- **Current status:** `08` requires a manifest "sufficient for re-derivation" but enumerates no minimum
  contents; `11 AR2/BL2` cannot be tested.
- **Assessment:** Accepted. The *encoding* is legitimately deferred, but the *minimum normative contents*
  must be enumerated for testability (spec versions, generator-component identities, data revisions,
  intervention-methodology profile, deterministic scope, acceptance comparison).
- **Recommended action:** `08 §10` enumerates the minimum manifest/re-derivation contents + a conformance
  check; leave encoding to implementation.
- **Owner:** `08` Owner.
- **Implementation impact:** Makes reproducibility auditable.
- **Blocks implementation:** Release-time (not coding start).
- **Requires:** document synchronization + implementation guidance.

**Baseline reproducibility — SPA-018**
- **Origin:** Codex. **Category:** D.
- **Current status:** Baselines are defined by information access + purpose, not by concrete configuration;
  `10` requires reference values.
- **Assessment:** Partially accepted; strong form rejected. Globally freezing baseline models/features in
  `09` would be redesign and is unnecessary: like the intervention methodology, each **release pins** its
  reference-baseline configurations (identities, configs, seeds) in the release report (`10 RR2`), making
  them reproducible **within** that release. The gap is a one-line statement that baseline configs are
  release-pinned; the pinning itself is implementation.
- **Recommended action:** Add a release-pinning clause to `09`/`10`; pin configs per release at
  implementation.
- **Owner:** `10` Owner (clause) + Implementation (pinning).
- **Implementation impact:** Reference values comparable within a release.
- **Blocks implementation:** No.
- **Requires:** implementation guidance + minor document synchronization.

**Audit view leakage — SPA-014  — RECLASSIFIED (Dataset Specification amendment, no ADR)**
- *(See "Information boundary" above.)* **Category:** B (was C). **Requires:** Dataset Specification
  amendment. **Blocks:** release-time. The single most important boundary-integrity **release policy** —
  reclassified because it constrains audit-view publication, not the architecture.

**Conformance testing — SPA-026 · (SPA-014)**
- **Origin:** Codex. **Category:** D.
- **Current status:** Conformance for external systems relies partly on declarations; the harness cannot
  prove a predictor did not use a public audit artifact or infer generator style.
- **Assessment:** Accepted as an inherent, already-acknowledged limitation (`10 K3`, `11 EF3`). Not a bug;
  the mitigation is (a) the SPA-014 **Dataset Specification amendment** so no joinable answer-key artifact
  is public, and (b) reports that **distinguish mechanically-checked from attested conformance**.
- **Recommended action:** Implementation reports preserve the mechanical-vs-attested distinction; depends
  on the SPA-014 amendment.
- **Owner:** Implementation + `08` Owner (SPA-014 amendment).
- **Implementation impact:** Honest conformance reporting.
- **Blocks implementation:** No (harness); the SPA-014 amendment gates public release.
- **Requires:** implementation guidance (+ the SPA-014 Dataset Specification amendment).

**OOD intervention risk — REV-02**
- *(See "Intervention methodology assumptions" above.)* **Category:** D (was C). **Requires:** empirical
  validation + implementation profile. **Blocks:** mass labeling. The benchmark's largest research risk —
  addressed by the viability probe (VAL-01), **not** by an ADR unless it forces a semantics change.

### 1.3 Remaining findings (compact)

- **SPA-005 (CC1 vs P1/P2)** — Codex · **B** · genuine contradiction: `07 §4 CC1` over-broadens `06 I2`
  (which governs the *label*, not structural eligibility). **Action:** narrow CC1's scope so P1/P2
  structural checks are distinguished from prohibited faithfulness-judgment text inspection. **Owner:**
  `07`. **Blocks:** **Yes**. **Requires:** document synchronization.
- **SPA-011 (Condition B has no inconclusive route)** — Codex · **B** (was C) · genuine gap: an
  inconclusive/error B-determination after P5/P6 pass has no legal resolution (forcing B=false manufactures
  D2; dropping violates no-silent-drop). **Governance refinement:** routing an inconclusive/error outcome
  to an approved route is **operational behaviour within the accepted architecture** — a **Pipeline
  specification amendment**, not an ADR; it adds **no** behavioural state (S1/S2/S3 is frozen; Q3 is
  resolved as binary-B). **Action:** amend `07 S11`/`06 §9` to route an inconclusive/error B outcome to an
  existing approved route, consistent with no-silent-drop. **Owner:** `07`. **Blocks:** Yes (pipeline).
  **Requires:** Pipeline specification amendment.
- **SPA-016 (primary vs co-headline)** — Codex · **B** · `10` calls P2 both "primary/co-headline" and (via
  C2) exploratory. **Action:** clarify P2 is the pre-eminent *secondary* discriminative measure
  (confirmatory only if pre-registered co-primary with alpha-split); define the operating-point selection
  procedure (ties to SPA-007). **Owner:** `10`. **Blocks:** Yes (scoring). **Requires:** doc sync.
- **SPA-017 (reproducibility tolerances)** — Codex · **B** · `10 Y2` ("within CI") and `11` ("tolerance")
  conflate statistical uncertainty with deterministic artifact/label reproducibility. **Action:** separate
  the two notions conceptually in `10/11`; the numeric tolerance is per-release. **Owner:** `10`/`11`.
  **Blocks:** release-time. **Requires:** doc sync + implementation guidance.
- **SPA-027 (P2/P3 E-code precedence)** — Codex · **B** · S05 evaluates P2+P3 together but S15 requires
  exactly one E-code. **Action:** add a deterministic gate/E-code precedence (P1>P2>P3>P4>P5>P6, mirroring
  D1 precedence). **Owner:** `06`/`07`. **Blocks:** Yes (routing determinism). **Requires:** doc sync.
- **SPA-020 (generator/output licensing)** — Codex · **B** · `08` lacks per-generator model/output license
  + downstream-training permission. **Action:** add to pre-generation eligibility + manifest/release checks
  (ties RI8; assessment A12). **Owner:** `08`. **Blocks:** release-time. **Requires:** doc sync +
  implementation guidance.
- **SPA-019 (thesis artifacts violate assumptions)** — Codex · **D** · legacy code breaches exact-baseline
  binding, graded evidence, no-silent-drop, provenance. **Action:** treat inventory refactors as
  implementation prerequisites; prohibit reusing legacy probe outputs as labels. **Owner:** Implementation.
  **Blocks:** No (spec). **Requires:** implementation guidance.
- **SPA-024 (terminology collisions unenforced)** — Codex · **D** · enforce qualified field names for
  `label/split/generator/rationale/...` in implementation schema validation. **Owner:** Implementation.
  **Blocks:** No. **Requires:** implementation guidance.
- **SPA-021 (stale matrix/DAG/inventory)** — Codex · **B** · sync matrix/DAG to accepted ADRs and existing
  `07/08/10`; mark the inventory a dated pre-spec snapshot. **Owner:** Spec Owners. **Blocks:** No (should
  precede coding). **Requires:** doc sync.
- **SPA-022 (broken 09 filename)** — Codex · **B** · fix `09_Baselines.md` → `09_Baseline_Systems.md` in
  `01`, `05` (and the scaffolding proposal); run a repo-wide link check. **Owner:** Spec Owners. **Blocks:**
  No. **Requires:** doc sync.
- **SPA-023 (duplicate normative lines)** — Codex · **B** · mechanical dedup review across `07/08/09/11`.
  **Owner:** Spec Owners. **Blocks:** No. **Requires:** doc sync.
- **SPA-028 (human-baseline ethics owner)** — Codex · **B** · `08` owns no ethics/consent contract.
  **Action (philosophy-preserving):** mark human performance **out of scope for the initial release**
  (already "optional/if-applicable"), removing the dangling dependency; defer any ethics contract to
  if/when it is added — avoids speculative future work. **Owner:** `09`/`10`/`08`. **Blocks:** No.
  **Requires:** doc sync.
- **SPA-002 Q2 / Q3 (residual open questions)** — Codex · **B / A** · **Q2** (whether E6/control failures
  form a distinct published "void" category) is a **routed-aside handling / release policy** matter →
  **Dataset Specification amendment** (fold with the audit-view amendment), not an ADR. **Q3** (Condition-B
  granularity) is **resolved by the frozen ontology**: B is **binary** in v1 (the S1/S2/S3 state space is
  fixed); any future partial-tracking outcome would be a new benchmark line (v2) requiring an ADR at that
  time — **no action now**. **Owner:** `08` (Q2); none (Q3). **Blocks:** No. **Requires:** Q2 doc sync; Q3
  no action.
- **SPA-025 (dimension-partitioned ownership)** — Codex · **A** · intentional design; use the
  responsibility dimension in tickets. **Requires:** no action.
- **REV-05 (anthropomorphic "faithful")** — Gemini · **A** · already handled by `10 L-1`/§15 and the
  release-report emphasis. **Requires:** no action (standing risk awareness).

## 2. Implementation Readiness Checklist

- ☐ **Charter restored** — instantiate `docs/00_Benchmark_Charter.md` from ratified draft *(SPA-001, B)*.
- ☐ **Vision restored** — instantiate `VISION.md` from ratified draft *(SPA-001, B)*.
- ☐ **ADR-002 synchronized** — status→Accepted, cross-refs applied, DAG G1 resolved *(SPA-009, B)*.
- ☐ **ADR-003 synchronized** — §5 amendments applied to `05/06/06a`, DAG G2 resolved *(SPA-008, B)*.
- ☐ **Traceability Matrix synchronized** — reflect existing `07/08/10`; ADR statuses *(SPA-021, B)*.
- ☐ **Pipeline DAG synchronized** — G1/G2 resolved; P6-routing sub-dependency corrected *(SPA-021, SPA-004, B)*.
- ☐ **Canonical rationale frozen** — `08` fixes the emitted-rationale representation *(SPA-012, B)*.
- ☐ **Answer correctness policy decided** — **ADR-004** ratified + synchronized *(SPA-002 Q1, C)*.
- ☐ **Composite generator policy decided** — **ADR-005** ratified + synchronized *(SPA-002 Q4, C)*.
- ☐ **Manifest contract finalized** — `08` enumerates minimum re-derivation contents *(SPA-013, B)*.
- ☐ **Internal links verified** — fix `09_Baselines` refs; repo-wide link check *(SPA-022, B)*.
- ☐ **Repository-wide terminology validation completed** — collision/qualified-name check *(SPA-024, D)*.
- ☐ **Specification cross-references validated** — every `§`/ID reference resolves *(SPA-022/023, B)*.
- ☐ **Outstanding ADRs resolved** — **only ADR-004 (Q1) and ADR-005 (Q4)** remain as ADRs *(SPA-002, C)*.
- ☐ **Benchmark version frozen** — tag the synchronized specification set as **Benchmark Specification
  v1.0** (§6), after all B-tasks, the two ADRs, and the accepted-ADR synchronization land.

*Note: the previously-proposed ADR-006 (hard core), ADR-007 (Condition-B route), and ADR-008 (audit view)
are **no longer ADRs**; they are specification amendments tracked in §3 (SYNC-21/22/23). The intervention
methodology (former ADR-009) is validation + implementation (VAL-01/IN-01), not an ADR. None of these
boxes is checked yet; all are the output of the tasks in §3.*

## 3. Repository Synchronization Tasks

Effort: **S** ≤1h · **M** a few hours · **L** ≥1 day. "Blocking?" = blocks implementation start. "Type":
DA = document amendment · IN = implementation note · VE = validation experiment · II = implementation issue.

### 3.1 Synchronization and specification-amendment tasks (Category B)

| Task | Type | Prio | Files to modify | Effort | Blocking | Expected outcome |
|---|:--:|:--:|---|:--:|:--:|---|
| **SYNC-01** Restore Charter | DA | P0 | `docs/00_Benchmark_Charter.md` (new) | S | Yes | Governance authority instantiated. |
| **SYNC-02** Restore Vision | DA | P0 | `VISION.md` (new) | S | Yes | Purpose/stop authority instantiated. |
| **SYNC-03** Accept + sync ADR-002 | DA | P0 | `ADR-002`, `06a §§3.5–3.7`, DAG | S | Yes | Provenance acyclicity authoritative; G1 resolved. |
| **SYNC-04** Apply ADR-003 amendments | DA | P0 | `05 §19`, `06 P1/E1`, `06a §§3.2–3.3/3.8/4/6/8`, DAG | M | Yes | Incomplete-candidate lifecycle consistent; G2 resolved. |
| **SYNC-05** Fix CC1 scope | DA | P0 | `07 §4 CC1`, S04–S05 | S | Yes | P1/P2 decidable without violating the no-judge label boundary. |
| **SYNC-06** Route P6 for A-false | DA | P0 | `07 §§5–6`, DAG §6 | M | Yes | Every labelled state satisfies P6; E6 reachable from the S1 branch. |
| **SYNC-07** Reconcile OOD-Model vs scene-grouping | DA | P0 | `08 N6.3/N7.2`, `11 BL3/DF1` | S | Yes | Split policy satisfiable; OOD-Model rule authoritative. |
| **SYNC-08** Label-access model | DA | P0 | `08 §§12–13`, `09 §5`, `10 §§2,4` | M | Yes | Train-as-training-material; harness owns Val operating point. |
| **SYNC-09** E-code precedence | DA | P1 | `06 §9`, `07 §6` | S | Yes | Deterministic routed-aside accounting. |
| **SYNC-10** Canonical rationale representation | DA | P1 | `08 §4/§12`, `04 §4` | M | Yes | One text object for identity/P1/P2/Condition B. |
| **SYNC-11** Identity contracts (scene/family/qtype) | DA | P1 | `06a §6`, `08 §§7–9/N10.6` | M | Yes | Split disjointness/leakage auditable. |
| **SYNC-12** P2 status + operating point | DA | P1 | `10 §4 (P1–P3), C2, §13–§14` | S | Yes | Confirmatory/exploratory status unambiguous. |
| **SYNC-21** Hard-core membership | DA | P1 | `08 N6.8` (contract), `05 §30` (clarify), `09/10/11` | M | Yes | Balanced hard-core membership contract; AUROC well-defined. |
| **SYNC-22** Condition-B inconclusive route | DA | P0 | `07 S11`, `06 §9` | S | Yes | Inconclusive/error B routes to an approved outcome; no silent drop. |
| **SYNC-23** Audit-view release policy | DA | P2 | `08 §14`, `10 K2`, `11` | M | Release | Public audit artifact cannot serve as an answer key. |
| **SYNC-24** E6/Q2 routed-aside handling | DA | P2 | `08 §5/§14` | S | No | E6/control-failure publication policy fixed (fold with SYNC-23). |
| **SYNC-13** Manifest minimum contents | DA | P2 | `08 §10`, `11 AR2/BL2` | M | Release | AR2 testable. |
| **SYNC-14** Reproducibility notions | DA | P2 | `10 Y2`, `11 LF1/BL5/§8` | S | Release | Artifact/label vs statistical separated. |
| **SYNC-15** Generator/output licensing | DA | P2 | `08 N3.6/N10.4/RI8` | M | Release | Release legality checkable. |
| **SYNC-16** Split-ID scoring-only | DA | P2 | `10 §2`, `08 §12.1` | S | No | Split membership is scoring-stratification, not a feature. |
| **SYNC-17** Human baseline out-of-scope (v1) | DA | P2 | `09 §14/§18`, `10 Q-E4/L8` | S | No | Removes dangling ethics dependency. |
| **SYNC-18** Sync matrix/DAG/inventory | DA | P2 | matrix, DAG, inventory | M | No | Design artifacts reflect the completed suite. |
| **SYNC-19** Fix links + dedup | DA | P2 | `01`, `05`, `07/08/09/11` | M | No | `09_Baseline_Systems` links; duplicate lines removed. |
| **SYNC-20** Advance base-doc status | DA | P3 | `01/03/05/06/06a/07/08/09/10/11` | S | No | Draft→Accepted after tasks land; version frozen. |

### 3.2 Non-synchronization work (decisions, validation, implementation)

| Item | Type | Prio | Owner | Blocking | Expected outcome |
|---|:--:|:--:|---|:--:|---|
| **ADR-004** Answer-correctness policy (Q1) | ADR | P0 | Maintainer | Yes (eligibility) | Benchmark membership fixed; construct settled. |
| **ADR-005** Composite-generator policy (Q4) | ADR | P0 | Maintainer | Yes (subject) | Subject identity fixed. |
| **VAL-01** Intervention-methodology viability probe | VE | P0 | Research validation | Mass labeling | Confirms semantic-shift (not OOD-collapse) before labeling. |
| **IN-01** Reference Implementation Profile (interventions, localization, controls, thresholds, baseline/manifest configs) | IN | P1 | Implementation | Mass labeling | Concrete, release-pinned methods recorded in implementation docs. |
| **II-01** Legacy-code refactor prerequisites (SPA-019/024) | II | P1 | Implementation | Coding | Exact-baseline binding, graded evidence, no-silent-drop, provenance, qualified field names. |
| **II-02** Conformance mechanical-vs-attested reporting (SPA-026) | II | P2 | Implementation | No | Honest conformance reports. |

**Only two ADRs remain** (ADR-004, ADR-005). Everything previously proposed as ADR-006/007/008/009 has
been reclassified to SYNC-21/22/23, VAL-01, or IN-01.

## 4. Implementation Prerequisites

```
 Specification Complete  →  Repository Synchronization  →  Two Benchmark Decisions  →  Reference Implementation
        (architecture)           (§3.1 SYNC-01..24)          (ADR-004 Q1, ADR-005 Q4)      (engineering, IN-01/II-01)
                                                                      │
                                                                      ▼
                          Validation Experiments  →  Corpus Generation  →  Internal Release
                            (VAL-01 viability probe)     (labeling at scale)     (audit-lite)
```

**Specification tasks** *(must precede coding of the affected component)*: SYNC-01..12, SYNC-16..22, and
the two ADRs (ADR-004 Q1, ADR-005 Q4). The former ADR items now living here as amendments are SYNC-21
(hard core), SYNC-22 (Condition-B route), SYNC-23 (audit-view policy), and SYNC-24 (E6/Q2). These make the
standard self-consistent and decidable.

**Engineering tasks** *(post-synchronization; inventory-backed, SPA-019/024)*: the reference pipeline
against `07`; source normalization + view separation against `08`; baseline systems against `09`; the
scoring harness against `10`; schema-level terminology-collision enforcement; manifest encoding; and the
**Reference Implementation Profile (IN-01)** recording the concrete, release-pinned intervention/baseline
methods.

**Research validation tasks** *(gate label production)*: the intervention-methodology **viability probe
(VAL-01)** — does a targeted edit produce a semantic shift, not OOD collapse? — and the OOD-QType
cross-dataset mapping curation flagged by Gemini as underestimated. **No mass corpus generation may begin
until VAL-01 passes.** VAL-01 is **not** an architectural decision; it is validation that the chosen
Reference Implementation Profile satisfies the (already-frozen) benchmark assumptions.

**Release-gated (not coding-gated) items:** SYNC-13/14/15/23, and generator licensing — required before an
internal/public release, not before reference-implementation coding.

## 5. Final Recommendation

**Chosen: (2) Specification Phase Complete after Repository Synchronization.**

**Justification.** The benchmark's **philosophy is complete**, its **ontology is complete**, its
**semantics are complete**, and its **governance framework is complete**. Both reviews affirm the
construct, the information boundary, the artifact lifecycle, and the measurement/interpretation/claim
separation; Gemini's verdict is "conceptually ready." **No redesign is warranted and none is proposed** —
every accepted finding is either repository synchronization, a specification amendment within the accepted
architecture, one of exactly **two** genuine benchmark decisions, implementation planning, or empirical
validation.

The earlier recommendation ("Requires Additional ADRs") is **superseded** because it over-classified
operational and release decisions as architectural. On governance review, only **two** decisions genuinely
alter benchmark semantics or ontology — **answer-correctness eligibility (Q1)** and **composite-generator
validity (Q4)** — and both were pre-registered as open. The remaining previously-labelled "ADRs" are
corpus-construction policy (hard core), pipeline-operational behaviour (Condition-B routing), and release
policy (audit view), which are **specification amendments**; the intervention methodology is an
**implementation profile validated empirically**, already governed by existing philosophy and assurance.
Option (1) is rejected because unapplied accepted ADRs, missing governing documents, and five internal
contradictions mean the repository is not yet self-consistent.

Therefore the remaining work consists of: **repository synchronization** (§3.1), **two remaining benchmark
decisions** (ADR-004 Q1, ADR-005 Q4), **synchronization of the accepted ADRs** (ADR-002/003), plus
**implementation planning and empirical validation** (§3.2, §4). After these, **the benchmark
specification itself is frozen.**

## 6. Repository Freeze Recommendation

After completion of:

1. **repository synchronization** (§3.1, SYNC-01..24),
2. **resolution of the two remaining benchmark decisions** (ADR-004 answer-correctness, ADR-005
   composite-generator), and
3. **synchronization of the accepted ADRs** (ADR-002, ADR-003),

the repository **should be tagged**:

> ### Benchmark Specification v1.0

From that point onward, the governance model is strict and final:

- **Semantic or ontological changes require a new ADR.** Any change to a label's meaning, the behavioural
  state space, the taxonomy, a probe's meaning, or subject identity is an ADR and, by Charter §4, is
  presumptively a new benchmark line (v2) — never an in-place edit to v1.0.
- **Operational improvements become implementation work.** Better interventions, localization, controls,
  metrics *implementations*, and tooling are engineering changes recorded as Reference Implementation
  Profiles and release notes — not specification edits — provided they preserve v1.0 semantics.
- **Implementation decisions belong in implementation documentation**, not in the benchmark
  specifications. The `docs/` standard fixes *what* and *what guarantees*; the *how* lives in
  implementation docs, pinned per release in the manifest and release report.

This freeze is the mechanism that keeps the benchmark a stable scientific instrument: the specification
stops changing, the implementation begins, and the two are kept apart by the version boundary and the
assurance framework (`docs/11`). The benchmark's philosophy, ontology, semantics, and governance remain
untouched by this report.
