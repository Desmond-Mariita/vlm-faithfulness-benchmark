---
Title: Dataset Specification
Status: Accepted
Benchmark-Version: v1.0
Last-reviewed: 2026-07-01
Related:
  - docs/01_Benchmark_Design.md
  - docs/03_Problem_Definition.md
  - docs/05_Formal_Definitions.md
  - docs/06_Label_Specification.md
  - docs/06a_Benchmark_Data_Model.md
  - docs/07_Label_Generation_Pipeline.md
  - docs/10_Evaluation_Protocol.md
  - decisions/ADR-002-Construction-Provenance-Lifecycle.md
  - decisions/ADR-003-Incomplete-Candidate-Subjects.md
  - docs/design/Specification_Traceability_Matrix.md
---

# Dataset Specification

*This specification defines the benchmark corpus as a **released research artifact**. It owns source
normalization (S01), Corpus Entry construction and split assignment (S16), Routed-Aside Set
construction (S17), corpus freeze and manifest (S18), and the released evaluation views (S19). It
**consumes** the outputs of [Label Generation Pipeline](07_Label_Generation_Pipeline.md) and redefines
**no** benchmark semantics.*

> **Boundary of this document.** This document specifies the corpus as an artifact: how source
> material is normalized, how labelled and routed candidates become released entries, how the corpus is
> split, versioned, frozen, and exposed through separated views. It defines **no** evaluation metrics,
> baseline systems, intervention methods, algorithms, or serialization formats — those are owned by
> `09`/`10` or remain implementation decisions (§18). Every semantic term is owned by
> [Formal Definitions](05_Formal_Definitions.md), [Label Specification](06_Label_Specification.md), and
> [Benchmark Data Model](06a_Benchmark_Data_Model.md); this document only *assembles and releases* their
> artifacts.

> **Requirement keywords.** MUST, MUST NOT, SHOULD, and MAY are used in the RFC-2119 sense.

**Coverage of the required specification items:** source normalization (§3), Corpus Entry structure
(§4), Routed-Aside Record handling (§5), split policy (§6), generator split (§7), dataset split (§8),
question-type split (§9), release manifest (§10), corpus versioning (§11), predictor-visible view
(§12), hidden evaluation view (§13), audit view (§14), release invariants (§15), traceability
obligations (§16), version compatibility (§17).

---

## 1. Scope and ownership

This specification is the operational owner of construction/release stages **S01** and **S16–S19**
(Specification Traceability Matrix §3). It does **not** own S02–S15 (generation, labeling, provenance),
which belong to [Label Generation Pipeline](07_Label_Generation_Pipeline.md), nor scoring, which belongs
to [Evaluation Protocol](10_Evaluation_Protocol.md).

**Artifacts owned** (their *form and assembly*, anchored to the Data Model): `Source Record` (§3.1),
`Output Tuple` shape (§3.2), `Corpus Entry` (§3.9), `Corpus Manifest` (§3.10), split assignment (§24),
and the *handling* of the `Routed-Aside Record` / `Routed-Aside Set` (§3.8, FD §23).

**Artifacts consumed from `07`** (unchanged, per the §8.2 handoff): labelled candidates — a
`Candidate Subject` with sealed `Interventional Provenance`, a `Behavioural State`, and a `Label` — and
`Routed-Aside Records`. This document MUST NOT alter the meaning of any consumed artifact (BD8; ADR-002
N1–N4; ADR-003).

---

## 2. Normative authorities

| Key | Authority |
|---|---|
| **BD** | Benchmark Design — boundary, irreversibility, reproducibility, invariants BD1–BD8. |
| **PD** | Problem Definition — refused shortcuts (PD-R1–R7); evaluation information restriction. |
| **FD** | Formal Definitions — Source Record §9, Output Tuple §19, Instance §22, routed-aside set §23, Split §24, Corpus §25, Manifest §26, Transfer §31. |
| **LS** | Label Specification — label meaning, immutability §10, versioning §11, invariants I1–I9. |
| **DM** | Data Model — artifact forms, identity R1–R8, mutability M1–M5, traceability T1–T6, versioning V1–V6. |
| **ADR2** | ADR-002 — sealed provenance; provenance/margins never predictor inputs. |
| **ADR3** | ADR-003 — completeness guaranteed at the boundary; incomplete tuples never enter a Corpus Entry. |

Where this document appears to differ from any authority, the authority governs.

---

## 3. Source normalization contract (S01)

**Purpose.** Transform an external dataset record into a canonical `Source Record` (FD §9; DM §3.1)
that the pipeline can consume source-agnostically.

- **N3.1 — Canonical form.** A `Source Record` MUST carry: a stable **source identity** (the originating
  dataset and that dataset's own record identity); the image (by reference); the question; the options;
  and any source-provided grounding annotations. It MUST carry **no** generator, chosen answer,
  rationale, or label.
- **N3.2 — Semantic preservation.** Normalization MUST NOT alter the semantic content of a source
  record (it may reshape, not rewrite).
- **N3.3 — Structured annotations.** Grounding annotations MUST be preserved as **structured**
  information distinguishable from image pixels; annotations baked into pixels do not satisfy this and
  MUST NOT be treated as structured evidence (matrix S01; DM §10 Q4 context).
- **N3.4 — Explicit malformed/absent accounting.** Source material that cannot be normalized to the
  canonical form MUST be recorded as an **explicit ingestion exclusion** with a reason; it MUST NOT be
  silently dropped, padded, or truncated (BD5; matrix S01 non-conformance note). Ingestion exclusions are
  a *pre-candidacy* accounting and are distinct from the `Routed-Aside Set` (§5), which is
  candidate-level.
- **N3.5 — Multi-source uniformity.** Multiple source datasets MAY be normalized to the same canonical
  `Source Record` form so that later stages are source-agnostic; the source identity records provenance
  regardless.
- **N3.6 — Provenance and licensing.** Each `Source Record`'s originating dataset, licensing terms, and
  redistribution constraints MUST be recorded for the manifest (§10, RI8). Where a source license forbids
  redistribution of images or annotations, the release MUST reference them by identity rather than
  redistribute them (§15 RI8).

*Which datasets are used, and the concrete normalization procedure, are implementation decisions
(§18). This section fixes the contract, not the method.*

---

## 4. Corpus Entry structure (S16)

**Purpose.** Assemble a labelled candidate into a `Corpus Entry` (DM §3.9) and assign its split.

- **N4.1 — Inputs.** S16 consumes, per labelled candidate: the `Source Record`, the **complete**
  `Output Tuple`, the `Candidate Subject`, the sealed `Interventional Provenance`, the `Behavioural
  State`, and the `Label`.
- **N4.2 — Required constituents.** A `Corpus Entry` MUST carry: the instance identity; the complete
  `Output Tuple` (predictor-visible); the `Label` and reason code (hidden evaluation view / hidden
  answer key); the sealed `Interventional Provenance` (audit view / audit trail); the `Behavioural
  State`; the split assignment; the source and generator identities (the generator identity withheld
  from predictors); and the governing specification versions (DM-T4).
- **N4.3 — Completeness gate (ADR-003 / CC8).** Only labelled candidates — for which P1 passed — reach
  S16. Every `Corpus Entry`'s `Output Tuple` MUST be complete. S16 MUST verify completeness and MUST
  reject an incomplete tuple as a **pipeline conformance error**, never admit it or silently repair it.
- **N4.4 — View separability.** A `Corpus Entry` MUST be structured so that its predictor-visible view
  (§12), hidden evaluation view (§13), and audit view (§14) are **separable** at release. Nothing
  withheld may be derivable from the predictor-visible view.
- **N4.5 — No redefinition.** S16 MUST carry the consumed `Label`, `Behavioural State`, and provenance
  through unchanged; it MUST NOT re-derive, adjust, or reinterpret them (ADR-002 N1–N4).
- **N4.6 — Canonical rationale representation.** The `rationale` field of the `Output Tuple` MUST be a
  **single canonical representation** of the generator's emitted rationale — the exact baseline text the
  pipeline bound to (Pipeline CC4) — under a **fixed, per-generator extraction contract** (which span of
  the raw decoded output constitutes the rationale). That extraction contract MUST be **pinned in the
  manifest** so the same generation always yields the same rationale object. This fixes the one text
  object on which Output-Tuple identity, P1/P2, Condition B, and predictor input depend; it does not
  change the `rationale` concept (Formal Definitions §6), only its released representation.

---

## 5. Routed-Aside Record handling (S17)

**Purpose.** Collect `Routed-Aside Records` from `07` (S15) into the `Routed-Aside Set` (FD §23; DM §3.8).

- **N5.1 — Inputs.** S17 consumes `Routed-Aside Records`, each carrying the instance identity, an E-code
  (E1–E6), and justifying sealed provenance, with **no** label and **no** behavioural state. (For E1, the
  provenance carries no Intervention Records — ADR-003.)
- **N5.2 — Exclusion from the labelled corpus.** The `Routed-Aside Set` is **not** part of the labelled
  corpus, is **not** assigned a split, and is **never** evaluated or exposed to predictors.
- **N5.3 — Resolution totality.** The union of `Corpus Entries` and the `Routed-Aside Set` MUST cover
  **every** `Candidate Subject` exactly once (DM-T2; DAG §7.2). No candidate may be absent from both.
- **N5.4 — Optional transparency release.** The `Routed-Aside Set` MAY be published for transparency.
  If published, it is part of the **audit view** (§14): it MUST receive manifest coverage (§10) and MUST
  NOT share a channel with, or leak into, the predictor-visible view. If not published, its counts are
  still recorded in the manifest (N10 / RI3). *(Resolves the routed-aside boundary ambiguity.)*
- **N5.5 — E-code accounting.** The manifest MUST record routed-aside counts by E-code (§10).

---

## 6. Split policy

A benchmark **Split** (FD §24) partitions the labelled corpus into benchmark roles; it is **distinct**
from any partition a source dataset already carries (FD §24; a source's own train/val division is not a
benchmark split).

- **N6.1 — Roles.** The corpus defines a **Train** split, a **Validation** split, and one or more
  **held-out-world** splits along three dimensions: generator (§7), dataset (§8), and question type
  (§9).
- **N6.2 — Exhaustive and exclusive.** Every `Corpus Entry` MUST be assigned to exactly one split;
  splits are mutually exclusive and jointly exhaustive over the labelled corpus. Routed-aside records
  are **not** assigned a split (N5.2).
- **N6.3 — Scene-level grouping.** All instances derived from one **source scene** MUST be assigned to
  the same split, so no source scene spans a Train/held-out boundary; this prevents a scene's presence in
  Train from leaking its label to a held-out instance of the same scene. **This rule governs the
  Train/Validation, OOD-QType, and OOD-Dataset splits.** It is **qualified for the OOD-Model split**
  (§7): because every generator runs over the *same* source scenes, generator-disjointness and
  scene-disjointness cannot both hold, so OOD-Model is **generator-disjoint with accepted, documented
  image/scene overlap** (N7.2). This is the governing rule, not a defect; the OOD-Model split tests
  generator-style generalization, not image novelty.
- **N6.4 — Held-out worlds withheld in training.** A predictor's training view (§12) contains only the
  Train split. The held-out-world splits are withheld during training, so that evaluation measures
  **transfer** (FD §31), not familiarity.
- **N6.5 — Label-distribution policy.** Train and Validation (and any explicitly balanced evaluation
  subset) MAY be constructed to a balanced label distribution. Held-out-world splits MUST retain their
  **natural** label distribution, so generalization is measured on realistic distributions. Any
  balancing choice MUST be recorded in the manifest (§10).
- **N6.6 — Quarantine.** Any instance used to calibrate an operational threshold or probe (a `07`/
  implementation activity) MUST be **excluded** from every evaluation split, so an operating point is
  never tuned on evaluation data. The split policy MUST honor this quarantine; the calibration procedure
  itself is out of scope here.
- **N6.7 — Assignment and freeze.** Splits are assigned at S16 and frozen at S18; the assignment is
  recorded in the manifest (§10) and is immutable within a corpus version (§11).
- **N6.7a — Grouping-key identities.** The keys the split rules depend on — **source scene**, **generator
  family**, and cross-dataset **question type** — MUST each be defined by a stable identity relation
  recorded (pinned) in the manifest: a scene-identity that groups all instances of one underlying scene
  (N6.3), a generator-family relation that groups generators for OOD-Model (N7.1), and the single
  cross-dataset question-type mapping (N9.3). These identity relations make disjointness and grouping
  auditable; their concrete construction is an implementation decision (§18), but their presence and
  pinning are required here.
- **N6.8 — Evaluation subsets (including the hard core).** The corpus designates evaluation subsets whose
  **membership** this document owns. For the **hard core** (FD §30), membership is a **balanced** two-class
  contract: high-plausibility/high-grounding **unfaithful** instances (hard negatives) paired with
  **matched** high-plausibility **faithful** instances (hard positives), so that AUROC is defined
  (Evaluation Protocol §7). Membership selectors MUST be **pinned and recorded in the manifest** so
  membership is reproducible; the plausibility/grounding selectors and the matching criteria MUST be
  **disjoint from any baseline backbone** whose behaviour they are used to test (to avoid selection
  artifacts). The concrete selector *implementations* and *reporting* are deferred to implementation and
  to `10`; the balanced-membership contract itself is fixed here.

*The concrete assignment procedure (e.g. how scenes are grouped or sampled) is an implementation
decision (§18). This section fixes the split policy and its invariants, not the algorithm.*

---

## 7. Generator split (OOD-Model)

**Purpose.** Test whether faithfulness signatures transfer to **unseen generators** (FD §31; PD refusal
to assume signatures generalize).

- **N7.1 — Held-out unit.** One or more entire **generator families** unseen in Train are assigned
  wholly to this split; a held-out family appears in **no** other split (generator-disjoint).
- **N7.2 — Image overlap accepted (governing rule for OOD-Model).** Because generators run over the
  **same** source scenes, image/scene-disjointness with Train is **not** required for this split; image
  overlap with Train is **accepted and MUST be documented** in the manifest. This clause **governs**
  OOD-Model and qualifies the general scene-grouping rule (N6.3): for OOD-Model, generator-disjointness
  is the operative constraint and cross-split scene overlap is expected. (Assurance BL3/DF1 treat
  OOD-Model image overlap as **not** a leakage violation.)
- **N7.3 — Natural distribution.** This split retains its natural label distribution (N6.5).
- **N7.4 — Membership-as-proxy disclosure.** Because the held-out family is grouped, membership in the
  OOD-Model split is itself a weak proxy for a generator grouping. The predictor-visible view still MUST
  NOT expose **which** generator produced an instance (§12); the inherent grouping signal of the
  generalization test MUST be documented in the manifest so evaluators can interpret results honestly.

---

## 8. Dataset split (OOD-Dataset)

**Purpose.** Test transfer to an **unseen source dataset / domain** (FD §31).

- **N8.1 — Held-out unit.** An entire **source dataset** unseen in Train is assigned wholly to this
  split; that dataset appears in **no** other split (dataset-disjoint). Scene-level grouping (N6.3) is
  trivially satisfied.
- **N8.2 — Natural distribution.** This split retains its natural label distribution (N6.5).
- **N8.3 — Provenance.** The held-out dataset's identity and licensing are recorded in the manifest
  (§10; RI8).

---

## 9. Question-type split (OOD-QType)

**Purpose.** Test transfer to **unseen question types / reasoning types** (FD §31).

- **N9.1 — Held-out unit.** One or more **question types** unseen in Train are assigned to this split;
  those question types appear in **no** Train instance (qtype-disjoint).
- **N9.2 — Scene grouping is mandatory here.** Because one source scene may carry several question
  types, scene-level grouping (N6.3) MUST hold so a scene's held-out-qtype question never shares a scene
  with a Train question. This reconciles qtype-disjointness with scene-grouping and prevents scene→label
  memorization.
- **N9.3 — Cross-dataset question-type mapping.** A single question-type mapping MUST make question
  types comparable across source datasets; the mapping MUST be pinned and recorded in the manifest (§10).
  The mapping's construction is an implementation decision (§18).
- **N9.4 — Natural distribution.** This split retains its natural label distribution (N6.5).
- **N9.5 — Control coordination.** The choice of held-out question type SHOULD coordinate with control
  validity in `07` (e.g. question types whose controls are known to be fragile); this document does not
  define controls, which remain owned by `07`.

---

## 10. Release manifest (S18)

**Purpose.** Produce the `Corpus Manifest` (FD §26; DM §3.10) that makes a corpus release reproducible,
traceable, and citable.

A `Corpus Manifest` MUST record (conceptually — the format is deferred, §18):

- **N10.1** the corpus-version identity;
- **N10.2** the set of `Corpus Entry` identities, and a reference to the `Routed-Aside Set` with
  **counts by E-code** (§5.5);
- **N10.3** the governing specification versions that produced and give meaning to the corpus —
  including the `Label Specification` version that fixes label **meaning** (DM-T4, V6);
- **N10.4** the generator identities and the source-dataset references, with **per-source** licensing and
  provenance **and per-generator model-license, output-license, redistribution, and downstream-training
  permissions** (§3.6; RI8) — a corpus of model outputs intended for predictor training MUST record that
  its generators' output licenses permit that use;
- **N10.5** the **split assignment summary** and any label-balancing choices (N6.5), including the
  OOD-Model image-overlap disclosure (N7.2, N7.4);
- **N10.6** the **pinned question-type mapping** (N9.3) and any **pinned evaluation-subset membership
  selectors** (N6.8), so those memberships are reproducible;
- **N10.7** integrity information sufficient for **re-derivation** on a pinned reference environment
  (BD §10). At minimum this MUST enumerate: the specification versions (N10.3); the composite-generator
  component identities and revisions; the source-data revisions; the **pinned intervention-methodology
  profile** (the Reference Implementation Profile identifier), the pinned rationale-extraction contract
  (N4.6), and the pinned evaluation-subset selectors (N10.6); the runtime/stack pins and the declared
  deterministic scope; and the **acceptance comparison** by which a re-derivation is judged reproducible
  (the artifact/label reproducibility tolerance, Evaluation Protocol §12 / Assurance §8) — the encoding of
  these fields is deferred to implementation, their presence is not;
- **N10.8** a statement of which artifacts are exposed in which release view (§12–§14).

The manifest is **public** and is the basis of traceability (§16) and reproducibility. It MUST NOT
contain anything that would place a withheld artifact into the predictor-visible view.

---

## 11. Corpus versioning

- **N11.1 — Two version trains** (DM V1). Specifications/code version under Semantic Versioning; the
  corpus is released as **frozen numbered versions**. Each corpus version records the specification
  versions that produced it (N10.3).
- **N11.2 — Immutability.** A released corpus version — its entries, labels, provenance, splits, and
  manifest — is **immutable** (LS §10; DM-M1–M5). A correction is a **new corpus version** with a new
  manifest, never an in-place edit (DM-M4).
- **N11.3 — Meaning vs value** (DM V2). A label's **meaning** is fixed by the `Label Specification`
  version stamped in the manifest; a label's **value** is fixed by the corpus version that carries it.
- **N11.4 — Label-meaning change ⇒ new benchmark line.** A change that alters label meaning is a MAJOR
  matter and, by the Charter §4 test, presumptively a **new benchmark (v2)** — a new corpus line, not an
  amended version (LS §11; DM V3). A pipeline (`07`) change that alters label *values* under the same
  meaning yields a **new corpus version** (DM V4).
- **N11.5 — Manifest binds the version set** (DM V6).

---

## 12. Predictor-visible view (S19)

The **only** artifact a predictor may consume.

- **N12.1 — Contents.** Per instance: the **complete** `Output Tuple` — image, question, options, chosen
  answer, rationale, and any source grounding annotations — plus only the split membership required by the
  applicable evaluation protocol. Split membership is provided **for scoring stratification only** and
  MUST NOT be consumed as a prediction input feature (a predictor conditioning on split ID is
  non-conformant; Evaluation Protocol §2).
- **N12.1a — Training material (label access).** The **Train** split's `Label`s are released as **training
  material** (Formal Definitions §24), so learnable predictors and baselines may fit on them. The
  `Label`s of Validation and every held-out world are **withheld** (hidden evaluation view, §13). The
  **evaluation harness** — never the predictor — selects and freezes the decision operating point on
  Validation labels (Evaluation Protocol §4). This is the only label access a predictor's *training* has;
  its *prediction* input remains the Output Tuple alone (N12.2).
- **N12.2 — Exclusions.** It MUST exclude, and MUST NOT allow derivation of: the generator identity, the
  `Label` and reason code, the `Behavioural State`, the `Interventional Provenance`, and any margins
  (BD §11; PD-R7; LS-I2 and §6 margins; DM-T6).
- **N12.3 — Completeness.** Every `Output Tuple` in this view is complete (N4.3; ADR-003; CC8). No
  incomplete tuple ever appears here.
- **N12.4 — Annotation safety.** Only **source-provided** grounding annotations may be exposed; any
  annotation that would reveal generator identity (e.g. generator-specific rendering) MUST NOT be exposed.
- **N12.5 — Strict projection.** This view is a strict projection of `Corpus Entries`; it adds nothing
  and reveals nothing withheld. The OOD-Model grouping signal (N7.4) is the only generator-related
  information inherent to the design, and it is documented rather than exposed as identity.

---

## 13. Hidden evaluation view (S19)

The answer-key view, available **only** to scoring (`10`), never to predictors.

- **N13.1 — Contents.** Per instance: the `Label` and reason code, and the split needed for scoring.
- **N13.2 — Separability.** It MUST be physically/logically separable from the predictor-visible view so
  that a predictor cannot access it (BD §11; DM-T6).
- **N13.3 — Scored target.** The scored target is the binary `Label`; the `Behavioural State` and reason
  code MAY accompany the hidden/audit views for analysis but their scoring is owned by `10` (LS Q5).
- **N13.4 — No re-derivation.** `10` consumes these labels as-is; nothing in this view re-opens the
  label semantics (ADR-002 N1–N4).

---

## 14. Audit view (S19)

The transparency view for auditors and researchers.

- **N14.1 — Contents.** The sealed `Interventional Provenance` (the evidence trail), the `Behavioural
  State`, the generator identities, any margins, and — if published — the `Routed-Aside Set` (§5.4).
- **N14.2 — Never a predictor input.** Every element of the audit view MUST be marked never-a-predictor-
  input (CC9; LS §6 margins; DM-T6). The audit view MUST NOT be co-mingled with the predictor-visible
  channel.
- **N14.2a — Non-joinability of a public audit view (release policy).** A **logical** "never a predictor
  input" marker does not, by itself, prevent misuse: a public audit artifact that is **joinable by stable
  instance identity** to the scored corpus hands any consumer the withheld answer key. Therefore, for any
  split whose labels are **live** (Validation and the held-out worlds of a released corpus version), the
  audit view MUST NOT be published in a form joinable to those scored instances. A release MAY satisfy
  this by (a) **withholding** the audit view for live splits, (b) publishing it **only after** a split is
  retired from scoring, or (c) publishing it under **severed identifiers** that cannot be joined to the
  predictor-visible instances. The chosen mechanism MUST be recorded in the manifest.
- **N14.3 — Optional.** The audit view MAY be withheld or published per release policy (subject to
  N14.2a); the decision and its scope MUST be recorded in the manifest (N10.8). Withholding it does not
  relax the traceability obligations (§16), which are satisfied by the retained (possibly internal)
  provenance.

---

## 15. Release invariants

- **RI1 — Boundary.** The predictor-visible view contains only complete `Output Tuples` plus necessary
  split membership; nothing withheld is present or derivable (§12; BD §11).
- **RI2 — Immutability.** A released corpus version and its manifest are immutable; corrections are new
  versions (§11; LS §10; DM-M4).
- **RI3 — Resolution totality.** `Corpus Entries` ∪ `Routed-Aside Set` = all `Candidate Subjects`, each
  exactly once; no silent drop; counts recorded (§5; DM-T2).
- **RI4 — Boundary completeness.** Every corpus-entry `Output Tuple` is complete (§4.3; ADR-003).
- **RI5 — No judge, end to end.** The release re-introduces **no** judge, plausibility, grounding, or
  correctness signal as the label; the label remains purely interventional (LS-I2, I6; PD-R1–R2).
- **RI6 — Provenance separability.** Provenance, margins, and generator identity are never in the
  predictor-visible view; they appear only in the audit view (§14; CC9; DM-T6).
- **RI7 — Reproducibility.** The corpus is **re-derivable** from its manifest on a pinned reference
  environment (not necessarily byte-identical; BD §10); the manifest records the full version set.
- **RI8 — Licensing and provenance.** Per-source licensing and provenance are recorded; source material
  is referenced by identity where its license forbids redistribution; the release MUST NOT redistribute
  material it has no right to redistribute.
- **RI9 — Split integrity.** Scene-level grouping (N6.3) and per-split disjointness (§7–§9) hold; splits
  are mutually exclusive and exhaustive over the labelled corpus; calibration/probe items are quarantined
  from evaluation splits (N6.6).
- **RI10 — One artifact, one owner.** This document owns the assembly and release of the Source Record,
  Output Tuple shape, Corpus Entry, Corpus Manifest, split assignment, and routed-aside handling; it
  consumes `07`'s Label, Behavioural State, and provenance without redefining them (BD8).
- **RI11 — No correctness filtering or exposure (ADR-004).** Corpus assembly MUST NOT filter labelled
  candidates by answer correctness; the released corpus contains correct and incorrect chosen answers
  exactly as labelled (ADR-004 C1–C2). Where source-reference correctness is recorded, it is
  construction/audit and evaluation-stratification metadata only: it MUST NOT appear in, or be
  derivable from, the predictor-visible view (§12; ADR-004 C6). Any future correctness-based
  restriction of corpus composition requires change classification and explicit policy; it cannot be
  applied silently (ADR-004 §5).

---

## 16. Traceability obligations

- **T-1 — Verdict reconstructability.** Every `Corpus Entry`'s `Label` MUST be reconstructible from its
  sealed `Interventional Provenance` carried in the audit trail (DM-T1; LS-I8).
- **T-2 — Bidirectional trace.** From a `Corpus Entry` one MUST be able to trace back to its `Source
  Record` and generator identity; from a `Source Record` one MUST be able to enumerate every instance it
  produced — labelled and routed-aside (DM-T3).
- **T-3 — Routed-aside accountability.** The `Routed-Aside Set` MUST record each record's E-code and
  justifying evidence; the manifest records counts by E-code (§5.5; DM-T2).
- **T-4 — Version stamping.** Every `Corpus Entry` MUST carry the specification versions that fixed its
  meaning (`06`) and produced its provenance (`07`) (DM-T4).
- **T-5 — Manifest completeness.** The manifest MUST reference every `Corpus Entry` and the `Routed-Aside
  Set`, and record the specification versions, generator identities, source references, split summary,
  and pinned selectors/mappings needed to re-derive the corpus (§10; DM-T5).
- **T-6 — Boundary auditability.** The release MUST keep the predictor-visible, hidden, and audit views
  separable so that the information boundary is auditable (DM-T6).

---

## 17. Version compatibility

- **N17.1 — Compare within a version.** A label **value** MUST be compared only **within** a corpus
  version. Cross-version comparison requires reading each version against its stamped specification
  versions (DM-V5).
- **N17.2 — Published compatibility statement.** Each corpus release MUST publish which specification
  versions it was built against and a **compatibility statement** identifying which prior corpus versions
  it is, and is not, comparable to.
- **N17.3 — Same-line vs new-line.** Additive changes under the **same** label meaning (new generators,
  datasets, question types, or splits) yield a new corpus version on the **same** benchmark line —
  backward-readable, but label values are not comparable across versions without re-derivation. A change
  to label **meaning** yields a **different benchmark line** (v2), not a comparable version (N11.4;
  Charter §4; LS §11).
- **N17.4 — Consumers key to a version.** Predictors and scorecards MUST key their results to a specific
  corpus version; a result is meaningful only against the version it was produced on.
- **N17.5 — Stable identities.** Instance identities are stable across corpus versions (DM-R7); a later
  version may re-issue the same instance identity with a corrected label value, and the two are related
  by identity but compared only within their own versions (N17.1).

---

## 18. Deferred to implementation

The following remain implementation decisions; each MUST satisfy the invariants and contracts above and
MUST change no benchmark semantic:

- which **source datasets** are used and the concrete **normalization procedure** (§3);
- the **split-assignment procedure** — how scenes are grouped and sampled — and any label-balancing
  method (§6–§9);
- the concrete **question-type mapping** and evaluation-subset **membership selectors** (§6.8, §9.3);
- the **manifest format**, integrity/pinning mechanism, and all **serialization** of every artifact and
  view (§10, §12–§14);
- the physical mechanism that separates the predictor, hidden, and audit **views** (§12–§14).

This document specifies *what the corpus and its release must be and guarantee*; it does not specify
*how* they are built or encoded.

---

## 19. Open dependencies

- **LS Q1 (correctness eligibility)** is **resolved by ADR-004** (accepted 2026-07-02): correctness
  does not gate eligibility, and corpus assembly does not filter labelled candidates by correctness
  (RI11). It is no longer an open dependency of this document.
- **LS Q3 (Condition B granularity)** is resolved for Benchmark v1 by the fixed binary
  Condition-B / S1-S3 contract; corpus composition consumes that fixed contract, while any future
  partial-tracking outcome would require a new MAJOR/v2 decision.
- **DM Q4 (evidence-region identity)** is resolved by V1-012 (accepted 2026-07-03): the audit view's
  provenance contents (§14) now consume the candidate-scoped interface contract defined in `07`; it is
  no longer an open dependency of this document. **LS Q4 (composite-generator validity)** is resolved
  by ADR-005 (accepted 2026-07-02) and no longer an open dependency of this document.
- The routed-aside **publication policy** (§5.4) and the **audit-view** publication scope (§14.3) are
  release-policy choices to be recorded per release; they interact with **RI8** licensing.

These MUST be reconciled before a public release, but they do not change the corpus contracts fixed here.

---

*This document defines the benchmark corpus as a released artifact: normalized sources, labelled Corpus
Entries and a retained Routed-Aside Set, split for generalization, frozen and versioned with a public
manifest, and exposed through separated predictor, hidden, and audit views. It consumes the Label
Generation Pipeline's outputs unchanged and defers every metric, baseline, method, and format to their
owners.*
