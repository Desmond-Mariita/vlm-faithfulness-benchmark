---
Title: Benchmark Assurance
Status: Accepted
Benchmark-Version: v1.0
Last-reviewed: 2026-07-01
Related:
  - docs/00_Benchmark_Charter.md
  - docs/01_Benchmark_Design.md
  - docs/05_Formal_Definitions.md
  - docs/06_Label_Specification.md
  - docs/06a_Benchmark_Data_Model.md
  - docs/07_Label_Generation_Pipeline.md
  - docs/08_Dataset_Specification.md
  - docs/09_Baseline_Systems.md
  - docs/10_Evaluation_Protocol.md
  - decisions/ADR-002-Construction-Provenance-Lifecycle.md
  - decisions/ADR-003-Incomplete-Candidate-Subjects.md
---

# Benchmark Assurance

*This document is the benchmark's long-term **assurance and governance framework**. It defines how the
benchmark's scientific integrity is monitored, how failures are detected, how assumptions are protected,
when releases are blocked, when decision records become mandatory, and when versioning must change. It
answers one question: **under what conditions should the benchmark no longer be trusted without
intervention?***

> **Boundary of this document.** This is governance, **not** semantics or implementation. It **MUST
> NOT** redefine benchmark semantics, labels, behavioural states, pipeline stages, or evaluation
> metrics, and introduces **no** implementation algorithms. It references every prior specification by
> name and defers to it; where assurance and a specification appear to conflict, the specification's
> semantics govern and assurance's role is to **flag** the conflict, never to resolve it by
> redefinition. It fixes **no** numerical thresholds; where a threshold for action is needed, it is a
> per-release governance decision.

> **Requirement keywords.** MUST, MUST NOT, SHOULD, and MAY are used in the RFC-2119 sense.

---

## 1. Scope

Benchmark assurance preserves the benchmark's **trustworthiness as a scientific instrument over time**.
The frozen specifications (`00`–`10`) define what the benchmark *is*; assurance defines how it *stays
valid* as generators, datasets, code, and understanding evolve. A benchmark can produce well-formed
numbers while silently mis-measuring; assurance exists to catch that condition before it reaches a
release.

This document is distinct from three neighbouring activities:

| Activity | Question it answers | Owner |
|---|---|---|
| **Benchmark assurance** (this document) | *Can the benchmark still be trusted, and if not, what intervention is required?* | governance |
| **Benchmark validation** | *Does this corpus/label satisfy the specifications?* (construction verification, viability gates, pipeline human-checks) | `07`/`08` |
| **Implementation testing** | *Does the code correctly execute the specifications?* (unit/integration tests) | implementation |
| **Paper limitations** | *What does a given publication decline to claim?* (scientific scope of a report) | Evaluation Protocol §16 |

Assurance **consumes** validation and testing results and paper scope statements as evidence; it does
not perform them. It is concerned **only** with preserving benchmark integrity.

**The governing question, stated directly.** The benchmark should no longer be trusted **without
intervention** whenever any **Critical** or **Catastrophic** failure (§4) is present, whenever any
release-blocking condition (§7) holds, or whenever a governance trigger (§9) has fired without its
required decision record. Everything below elaborates and operationalises this answer.

---

## 2. Assurance philosophy

- **A benchmark is a scientific instrument.** Its outputs are measurements; an instrument that drifts
  reports precise, wrong numbers.
- **Instruments require calibration.** The benchmark's ground truth rests on assumptions — that
  plausibility diverges from faithfulness (Problem Definition §3), that targeted interventions yield
  discriminative labels, that faithfulness signatures partially transfer, that the hard core is genuinely
  hard. These are empirical and can decay as models change.
- **Assumptions must remain continuously valid.** Assurance watches the *assumptions*, not only the
  outputs, because an assumption that quietly becomes false makes the instrument mis-measure while still
  passing every code test.
- **Releases must be auditable.** Every release MUST be able to demonstrate its own integrity (§12);
  trust is earned by evidence, not asserted.
- **Governance is proactive, not reactive.** Detection signals (§5) and blocking criteria (§7) are
  defined in advance, so integrity problems are caught **before** a release rather than retracted after.
- **Testing is necessary but not sufficient.** Correct code executing a drifted construct is still
  invalid; assurance covers exactly what implementation testing cannot see.

---

## 3. Failure taxonomy

Each failure mode is defined by the integrity property it breaks and the specification it endangers. It
is **not** a redefinition of any concept.

### A. Construct failures (the meaning of what is measured drifts)

| Code | Failure mode | What it breaks · endangered guarantee |
|---|---|---|
| **CF1** | Construct drift | Results are treated as more than behavioural, necessary-condition faithfulness. Endangers Charter scope; Label Specification §5. |
| **CF2** | Semantic drift | A defined term's usage diverges across documents, code, or releases. Endangers Formal Definitions (one-fact-one-home). |
| **CF3** | Behavioural-interpretation drift | Results are read as mechanistic/cognitive rather than behavioural. Endangers Label Specification §5 scope; Evaluation Protocol §15. |
| **CF4** | Premise erosion | The plausibility-versus-faithfulness divergence weakens for newer generators; the hard core stops being hard. Endangers the benchmark's reason to exist; Charter §6. |

### B. Data failures (corpus integrity breaks)

| Code | Failure mode | What it breaks · endangered guarantee |
|---|---|---|
| **DF1** | Split leakage | An instance/scene crosses a train↔evaluation boundary. Endangers Dataset Specification §6.3. |
| **DF2** | Dataset leakage | A held-out dataset appears in Train. Endangers Dataset Specification §8. |
| **DF3** | Generator leakage | A held-out generator appears in Train, or generator identity reaches the predictor view. Endangers Dataset Specification §7, §12; Benchmark Design §11. |
| **DF4** | Distribution collapse | A split degenerates (e.g. near single-class), making a metric ill-defined. Endangers Dataset Specification §6.5; Evaluation Protocol §6. |
| **DF5** | Hard-core degradation | The hard core loses balance, stratification, or plausibility-matching. Endangers Dataset Specification §6.8; Evaluation Protocol §7. |

### C. Label failures (ground truth becomes unreliable)

| Code | Failure mode | What it breaks · endangered guarantee |
|---|---|---|
| **LF1** | Unstable labels | Labels flip across re-derivation beyond the reproducibility tolerance. Endangers Benchmark Design §10; Label Specification I9. |
| **LF2** | Inconsistent behavioural states | S1/S2/S3 determination or D1 precedence applied inconsistently. Endangers Label Specification §5–§6. |
| **LF3** | Provenance corruption | Sealed provenance no longer reconstructs a label. Endangers Label Specification I8; Data Model T1; ADR-002. |
| **LF4** | Pipeline inconsistency | A pipeline stage violates a cross-cutting invariant or resolution totality. Endangers Pipeline §4; Data Model T2. |

### D. Evaluation failures (results produced or read invalidly)

| Code | Failure mode | What it breaks · endangered guarantee |
|---|---|---|
| **EF1** | Metric misuse | A metric used outside its scope (e.g. AUROC on a single-class split, per-split threshold refit). Endangers Evaluation Protocol §4–§7. |
| **EF2** | Statistical misuse | Missing CIs, no multiplicity control, headlining a below-minimum-n cell. Endangers Evaluation Protocol §8. |
| **EF3** | Baseline misuse | A baseline granted forbidden access, or an authors' baseline given privilege. Endangers Baseline Systems §7; Benchmark Design invariant 6. |
| **EF4** | Invalid comparisons | Comparing label values across versions, or across a label-meaning change. Endangers Dataset Specification §17; Evaluation Protocol §12. |

### E. Governance failures (the change process breaks)

| Code | Failure mode | What it breaks · endangered guarantee |
|---|---|---|
| **GF1** | Undocumented semantic change | A definition changed without a decision record. Endangers Charter §5; the decision-record convention. |
| **GF2** | Missing ADR | A decision requiring a record made implicitly. Endangers the change-control process. |
| **GF3** | Undocumented release change | A corpus/spec change shipped without manifest or changelog record. Endangers Dataset Specification §10; version lineage. |
| **GF4** | Specification drift | Specifications and code/releases diverge; an accepted ADR's amendments remain unapplied. Endangers the internal consistency of the standard. |

---

## 4. Failure severity

| Severity | Definition | Consequence | Trust impact |
|---|---|---|---|
| **Informational** | No integrity impact; recorded for the audit trail. | Note only. | None. |
| **Minor** | Localized, does not affect labels or any headline result. | Correct in place or in a patch release; no meaning change. | Intact. |
| **Major** | Affects a subset of results or a non-primary claim. | Investigate; likely a new corpus/spec version; may block a specific claim. | Reduced for the affected claim. |
| **Critical** | Affects the primary endpoint, the label, or an information-boundary / no-silent-drop guarantee. | **Blocks the affected release** until resolved; likely corpus rebuild and/or an ADR. | **Not trusted without intervention** for the affected release. |
| **Catastrophic** | The construct itself is invalid, or ground truth is systematically wrong (e.g. CF4 premise fails; LF3 corpus-wide). | **Blocks all releases**; engages Charter §5–§6 (new line or retirement). | **Not trusted at all without intervention.** |

The benchmark is "no longer trusted without intervention" precisely at **Critical** and **Catastrophic**,
and at any unresolved **Major** that touches a headline claim.

---

## 5. Detection signals

For each failure mode: observable symptom, monitoring signal, expected diagnostic, and detection
confidence. Signals are **implementation-independent** — they name *what to observe*, never how to
compute it. Detection confidence is **Deterministic** (structural check), **Statistical** (requires data
and CIs), or **Judgmental** (requires expert review).

| Mode | Observable symptom | Monitoring signal | Expected diagnostic | Confidence |
|---|---|---|---|---|
| CF1/CF3 | Citing work reads results as mechanistic/cognitive | Periodic construct-scope review of published uses | Interpretation audit against Label Specification §5 | Judgmental |
| CF2 | A term used inconsistently across docs/releases | Terminology consistency review | Cross-document usage diff vs Formal Definitions | Judgmental/Deterministic |
| CF4 | Floor/judge no longer collapse on the hard core for new generators | Hard-core collapse tracking per generator generation | Comparison of collapse measurements over time | Statistical |
| DF1/DF2/DF3 | Evaluation performance anomalously high; identity recoverable | Split-disjointness and boundary audit | Scene/dataset/generator id intersection across splits; predictor-view field scan | Deterministic |
| DF4 | A split near single-class; a metric undefined | Per-split distribution monitoring | Class/qtype/generator distribution of each split | Deterministic |
| DF5 | Hard-core AUROC no longer isolates faithfulness | Hard-core composition and difficulty tracking | Balance, stratification, plausibility-match, and collapse checks | Statistical |
| LF1 | Labels differ on re-derivation | Reproducibility re-derivation on the pinned environment | Label agreement across re-derivations within tolerance | Statistical |
| LF2 | State/precedence applied inconsistently | Invariant conformance sampling | Check S1/S2/S3 and D1 precedence against Label Specification §6 | Deterministic |
| LF3 | A label cannot be reconstructed from its provenance | Provenance-completeness audit | Reconstruct verdict from sealed provenance (Data Model T1) | Deterministic |
| LF4 | An artifact violates a pipeline invariant or a candidate is unresolved | Pipeline invariant + resolution-totality audit | Cross-cutting invariant checks; Corpus∪Routed-Aside = candidates | Deterministic |
| EF1/EF2 | A reported number lacks a CI, uses a wrong operating point, or is out-of-scope | Scorecard conformance review | Check each metric against Evaluation Protocol §4–§8 | Deterministic |
| EF3 | A baseline used forbidden information | Baseline conformance review | Information-access declaration audit (Baseline Systems §7) | Deterministic/Judgmental |
| EF4 | Cross-version comparison of label values | Version-keying audit | Check comparisons against Dataset Specification §17 | Deterministic |
| GF1/GF2 | A semantic change with no ADR | Change-control review | Diff of definitions vs ADR history | Deterministic |
| GF3 | A release without a complete manifest/changelog | Release-audit checklist | Manifest and lineage completeness (§12) | Deterministic |
| GF4 | Specs and releases/code disagree | Specification-consistency review | Cross-check accepted ADRs applied to base documents | Deterministic |

---

## 6. Required responses

| Severity | Required actions |
|---|---|
| **Informational** | **Monitor**; record in the audit trail. |
| **Minor** | **Investigate**; correct via **patch release** or documentation fix; no label-meaning or version-meaning change. |
| **Major** | **Investigate**; **require an ADR** if semantics or assumptions are touched; issue a **new corpus version** (values) or a **spec MINOR**; block the affected claim only. |
| **Critical** | **Pause the affected release**; **require an ADR**; **rebuild the corpus** and/or **repeat the intervention** as the cause requires; **major version** if label meaning is affected; do not release until resolved. |
| **Catastrophic** | **Pause all releases**; **require an ADR under Charter §5**; **benchmark fork (new line / v2)** or **retirement** per Charter §6; issue a public notice. |

Cross-cutting rules: any response that changes label meaning, the state space, or a probe's meaning
engages Charter §4 (v1/v2 test) and §5 (extraordinary justification) and the Label Specification §11
versioning rule. Any assumption invalidation additionally fires a governance trigger (§9).

---

## 7. Release-blocking criteria

A benchmark release **MUST NOT** proceed while any of the following holds. Each is Critical or
Catastrophic (§4).

- **BL1 — Unresolved provenance inconsistency.** Any label not reconstructible from its sealed provenance
  (LF3; Label Specification I8; ADR-002).
- **BL2 — Missing traceability.** Bidirectional trace or version stamping absent (Data Model T3–T5).
- **BL3 — Split leakage.** Scene/dataset/generator disjointness or grouping violated (DF1–DF3; Dataset
  Specification §6–§9). *Note: accepted, documented image/scene overlap in the **OOD-Model** split is
  **not** a leakage violation (Dataset Specification N6.3/N7.2) — OOD-Model is generator-disjoint by
  design, so BL3/DF1 apply to it only for **generator** disjointness, not scene disjointness.*
- **BL4 — Failed conformance.** A scored baseline/predictor is non-conformant, or the harness cannot
  validate coverage (EF3; Evaluation Protocol §10).
- **BL5 — Uncharacterised label instability.** Labels flip beyond the reproducibility tolerance and the
  cause is not understood (LF1; Benchmark Design §10).
- **BL6 — Violated benchmark assumption.** A protected assumption is invalidated — e.g. the hard core is
  not actually hard (CF4; DF5).
- **BL7 — Boundary breach.** An incomplete Output Tuple, provenance, margin, or generator identity is
  present in or derivable from the predictor-visible view (ADR-003; Benchmark Design §11; Dataset
  Specification §12).
- **BL8 — Governance gap.** A required ADR is missing, an accepted ADR's amendments are unapplied, or the
  manifest/lineage is incomplete (GF1–GF4).
- **BL9 — No analysis plan.** A release that makes claims lacks a pre-registered release report
  (Evaluation Protocol §14).

A release is permitted only when **every** blocking criterion is demonstrably cleared (§12).

---

## 8. Assurance metrics (health indicators)

Health is monitored as **trends and states**, not numbers. This document fixes **no** numerical
thresholds; a threshold for action is a per-release governance decision.

| Indicator | What it tracks | How it is read |
|---|---|---|
| **Label stability** | Agreement of labels across re-derivation on the pinned environment | Trend; drift near operating points is a warning (LF1). |
| **Provenance completeness** | Coverage of labels whose sealed provenance fully reconstructs the verdict | Should be total; any gap is a red flag (LF3). |
| **Split integrity** | Disjointness and scene-grouping conformance across splits | Structural state; any violation blocks (DF1–DF3). |
| **Generator diversity** | Breadth of generator families/architectures and held-out coverage | Trend; declining diversity risks generator-specific overfit. |
| **Hard-core integrity** | Balance, stratified composition, plausibility-matching, continued difficulty | Trend; loss of difficulty signals CF4/DF5. |
| **Release reproducibility** | Whether a release re-derives within tolerance on the pinned environment | State + tolerance band (no numbers). |
| **Baseline validity** | Baselines remain conformant and their reference behaviour (floor collapse) holds | State; a non-collapsing floor is a warning. |
| **Audit completeness** | Whether a release demonstrates traceability/provenance/conformance/lineage/ADR history | State; incompleteness blocks (§12). |

---

## 9. Governance triggers

Certain events **automatically** require governance action. The table states the minimum action.

| Trigger | Required governance action |
|---|---|
| **New behavioural state discovered** | ADR; changes the state space ⇒ **major / new benchmark line (v2)** (Charter §4). |
| **Label semantics change** | ADR under Charter §5; **major**, presumptively a **benchmark fork (v2)** (Label Specification §11). |
| **Benchmark assumption invalidated** | ADR; re-scope or **retire** per Charter §6; at minimum **major**. |
| **New intervention methodology** (Pipeline) | ADR; **new corpus version** — MINOR if label meaning is preserved, MAJOR if not. |
| **Ontology modification** (artifacts/identity/mutability) | ADR; Data Model version bump; **major** if artifact meaning changes. |
| **Release incompatibility** | Document in the manifest; **new version** with a compatibility statement (Dataset Specification §17). |

**When each level applies (referencing, not redefining, the versioning rules):**

- **ADR required** — for any semantic, ontology, assumption, intervention-methodology, or state-space
  change; any Charter-flagged decision; and any resolution of a release-blocking condition (§7).
- **MINOR** — additive, meaning-preserving changes (new generators, datasets, question types, splits,
  baselines, or reporting) under the **same** label meaning.
- **MAJOR** — any change to label meaning, the state space, the label taxonomy, or a probe's meaning.
- **Benchmark fork (new line / v2)** — a MAJOR that changes the construct or label meaning (Charter §4).

---

## 10. Benchmark lifecycle

| Stage | Description | Assurance obligation | Exit |
|---|---|---|---|
| **Proposal** | The design is argued; no corpus. | None beyond decision records. | Design ratified. |
| **Development** | Specifications and pipeline built; internal corpora. | Validation and testing; no external claims. | Pipeline conformant end-to-end. |
| **Internal release** | Non-public corpus for integrity validation. | Full blocking-criteria audit (audit-lite for lineage). | Assurance metrics healthy. |
| **Research preview** | Limited external, clearly marked non-final. | Blocking criteria cleared; results **not citable as final**. | Feedback incorporated. |
| **Public release** | Citable, immutable, versioned corpus. | Full audit (§12); pre-registered release report; manifest. | Superseded or deprecated. |
| **Maintenance** | Monitoring and versioned updates. | Continuous assurance-metric monitoring; respond to triggers. | A trigger forces a new version/line. |
| **Deprecation** | Superseded by a newer version/line. | Remains reproducible; **no new claims**; migration guidance. | Retirement. |
| **Retirement** | No longer trusted or supported. | Results MUST NOT ground new claims; Charter §6 or supersession. | — |

A lifecycle transition MUST NOT skip an unmet assurance obligation; a stage advance is itself gated by
the blocking criteria (§7).

---

## 11. Assurance responsibilities

Responsibilities are assigned to **roles** (functions), not people; one person may hold several roles,
but the duties remain distinct.

| Role | Assurance duties |
|---|---|
| **Benchmark Maintainers** | Own this framework; ratify ADRs; declare severity; approve or **block/pause** releases; steward the construct. |
| **Specification Owners** | Keep their specification tree internally consistent; ensure accepted ADRs are applied; guard against semantic drift (CF2, GF4). |
| **Implementation Team** | Execute specifications faithfully; run validation and conformance checks; surface pipeline inconsistencies; perform implementation testing (distinct from assurance). |
| **Release Manager** | Assemble releases; verify every blocking criterion is cleared; produce manifest, lineage, and the audit record; publish the release report; enforce version keying. |
| **Contributors** | Follow the spec-first workflow; open issues and ADRs; declare the conformance of contributed baselines. |
| **External Evaluators / Auditors** | Independently verify traceability, reproducibility, and conformance; report failures; their findings feed assurance. |

---

## 12. Audit requirements

Every release MUST be able to demonstrate the following on demand. A release that cannot demonstrate all
of them MUST be blocked (§7).

- **AR1 — Traceability.** Bidirectional trace between every Corpus Entry and its Source Record and
  generator identity (Data Model T3).
- **AR2 — Reproducibility.** The corpus is re-derivable from its manifest on the pinned reference
  environment (Benchmark Design §10), and each scorecard is reproducible within its CI (Evaluation
  Protocol §12).
- **AR3 — Provenance.** Every label reconstructs from its sealed provenance (Label Specification I8;
  ADR-002).
- **AR4 — Conformance.** Every scored predictor/baseline and the release itself pass conformance
  (Evaluation Protocol §10; Baseline Systems §16).
- **AR5 — Version lineage.** The corpus version, its governing specification versions, and its relation
  to prior versions are recorded (Dataset Specification §17).
- **AR6 — ADR history.** The decision records governing the release, with their status, are enumerable.

---

## 13. Relationship to existing specifications

This document **observes and governs**; the specifications **define**. It never redefines them.

- **Evaluation Protocol** — Assurance consumes its statistical, conformance, and reporting outputs as
  detection signals (§5) and audit evidence (§12). It defines no metric.
- **Dataset Specification** — Assurance consumes split integrity, manifest, versioning, and views as
  health indicators (§8) and blocking criteria (§7). It defines no corpus structure.
- **Label Generation Pipeline** — Assurance monitors pipeline invariants and provenance as label-failure
  signals (LF3, LF4). It defines no stage.
- **Label Specification** — Assurance protects the label and behavioural-state semantics from drift
  (CF1–CF3, LF1–LF2) and enforces that any change travels through an ADR and Charter §4–§5. It defines no
  label or state.
- **ADRs** — Assurance is the mechanism that makes ADRs **mandatory** at the right triggers (§9); ADRs
  remain the authoritative record of decisions. This document references the decision-record process; it
  does not supersede it.

If assurance and any specification appear to conflict, the specification's semantics govern; assurance
raises the conflict as a governance failure (GF-series), it does not resolve it by redefinition.

---

## 14. Open questions

Only long-term governance questions remain:

- **Cadence.** How frequently assurance-metric health is audited during Maintenance (§10) is a
  per-release governance decision.
- **Severity independence.** Who arbitrates severity and blocking when the Maintainer, Implementation,
  and Release roles are held by one person — the assurance framework assumes role separation that a solo
  project must simulate.
- **External-audit requirement.** Whether an independent external audit (§11) is **mandatory** for a
  public release, or recommended.
- **Sunset policy.** How long reproducibility is guaranteed for a deprecated version before retirement
  (§10).
- **Meta-governance across lines.** How competing or forked benchmark lines (v1/v2) are jointly governed
  and compared over time (Dataset Specification §17; Evaluation Protocol Q-E5).
- **Standing drift item.** The reconciliation of any accepted ADR whose amendments are not yet applied to
  the base documents (GF4) is a live governance item that MUST be closed before a public release.

---

*This framework closes the standard. It adds no semantics and changes none; it defines how the benchmark
is watched, how its failures are named and graded, when a release must be stopped, and when a change must
pass through a decision record or a version boundary — so that the benchmark remains a trustworthy
instrument, and the conditions under which it is not are explicit, detectable, and actionable.*
