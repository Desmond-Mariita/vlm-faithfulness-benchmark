---
Title: Benchmark Data Model
Status: Accepted
Benchmark-Version: v1.0
Last-reviewed: 2026-07-01
Related:
  - docs/01_Benchmark_Design.md
  - docs/05_Formal_Definitions.md
  - docs/06_Label_Specification.md
  - docs/07_Label_Generation_Pipeline.md
  - docs/08_Dataset_Specification.md
  - docs/10_Evaluation_Protocol.md
  - docs/design/Label_Generation_Pipeline_Implementation_Inventory.md
---

# Benchmark Data Model

*This specification defines the canonical **benchmark artifacts** — the first-class objects that flow
through benchmark construction and evaluation — so that the
[Label Generation Pipeline](07_Label_Generation_Pipeline.md) transforms well-defined artifacts rather
than informal collections of data. It is a **conceptual** data model.*

> **Boundary of this document.** This is a data model, **not** an implementation. It defines **no**
> implementation classes, **no** JSON schemas, **no** serialization formats, and **no** algorithms.
> "Required contents" below name the *conceptual constituents* an artifact must carry — never fields,
> types, or encodings. Every artifact is anchored to a term in
> [Formal Definitions](05_Formal_Definitions.md) or [Label Specification](06_Label_Specification.md);
> this document introduces **no** new benchmark concept — it names the *artifact realizations* of
> concepts fixed elsewhere. Operational rules (interventions, thresholds, localization, metrics) remain
> owned by their specifications.

> **Requirement keywords.** MUST, MUST NOT, SHOULD, and MAY are used in the RFC-2119 sense.

---

## 1. Scope

This document governs the **set** of benchmark artifacts, their **contents**, **relationships**,
**lifecycle**, **identity**, **mutability**, **traceability**, and **versioning**. It is the canonical
reference for *which artifacts exist* and *how they relate*.

It does **not** govern: how any artifact is computed or serialized (owned by the producing
specification); the interventions or localization that populate an `Intervention Record` (owned by
`07`); the label rule or state semantics (owned by `06`); corpus composition or release format (owned
by `08`); or scoring (owned by `10`).

**Instance and its phases.** The `instance` (Formal Definitions §22) is the umbrella unit. It is **not**
a fourth thing beside its phases: an instance is a **Candidate Subject** before labeling, and resolves
to exactly one of a **Corpus Entry** (labelled) or a **Routed-Aside Record** (ineligible). These three
artifacts are the successive phases of one instance and share one identity (§6).

---

## 2. Artifact set and conceptual anchors

| Artifact | Conceptual anchor | Owning specification | Crosses the boundary? |
|---|---|---|---|
| Source Record | Formal Definitions §9 | Dataset Specification (`08`) | Internal; its public fields cross via the Output Tuple |
| Output Tuple | Formal Definitions §19 | Dataset Specification (`08`) | **Yes** — the predictor-visible bundle |
| Candidate Subject | Instance §22 (pre-label phase) | this document (`06a`) / `08` | Internal to construction |
| Intervention Record | Intervention §11 + Counterfactual §12 | Label Generation Pipeline (`07`) | Internal; withheld from predictors |
| Behavioural State | Label Specification §5 | Label Specification (`06`) | Internal; withheld from predictors |
| Label | Formal Definitions §21; Label Spec §6 | Label Specification (`06`) | Crosses **only** as the hidden answer key |
| Interventional Provenance | Formal Definitions §20 | Label Generation Pipeline (`07`) | Released for transparency; **withheld as a predictor input** |
| Routed-Aside Record | Formal Definitions §23; Label Spec §9 | this document (`06a`) / `06` / `08` | Internal; MAY be published separately |
| Corpus Entry | Instance §22 (labelled) + Corpus §25 | Dataset Specification (`08`) | Its Output Tuple crosses; Label/provenance as key/trail |
| Corpus Manifest | Formal Definitions §26 | Dataset Specification (`08`) | **Yes** — public |

No artifact in this table is a new concept; each realizes an anchored term. Where this document defines
an artifact (`06a`), it defines only the *artifact form*; the anchored term's meaning is owned as shown.

---

## 3. Artifact catalog

Each artifact specifies: **Purpose**, **Ownership** (with conceptual anchor), **Required contents**,
**Relationships**, **Lifecycle**, **Mutability**, **Producing specification**, **Consuming
specification**.

### 3.1 Source Record
- **Purpose.** The model-free raw unit of material; the origin of every instance.
- **Ownership.** Dataset Specification (`08`); anchor: Formal Definitions §9.
- **Required contents.** A stable source identity (the originating dataset and that dataset's own record
  identity); the image; the question; the options; any grounding annotations shipped with the source. It
  carries **no** generator, chosen answer, rationale, or label.
- **Relationships.** Consumed by a generator to produce an Output Tuple; one Source Record MAY father
  many Candidate Subjects (one per generator). Its public fields reappear inside the Output Tuple. It is
  construction-internal; only its public fields cross the boundary, via the tuple.
- **Lifecycle.** Ingested and normalized from an external dataset at the start of construction; fixed
  for the life of a corpus version.
- **Mutability.** Immutable within a corpus version; any change is a new corpus version.
- **Producing specification.** `08` (ingestion/normalization).
- **Consuming specification.** `07` (generation and labeling); `08` (assembly).

### 3.2 Output Tuple
- **Purpose.** The predictor-visible bundle for one instance; fixes the "available to predictors" side
  of the information boundary.
- **Ownership.** Dataset Specification (`08`) for its shape; anchor: Formal Definitions §19.
- **Required contents.** The image; the question; the options; the **exact chosen answer as emitted** by
  the generator; the **exact rationale as emitted** by the generator; any grounding annotations from the
  source. It **excludes** the generator's identity and all interventional information. Per **ADR-003**,
  the chosen answer and/or rationale are present-and-exact for a **complete** tuple; a Candidate Subject's
  tuple prior to eligibility MAY be **incomplete** (either absent), and an incomplete Output Tuple MUST
  NOT appear in a Corpus Entry.
- **Relationships.** Produced by a generator from a Source Record; bound one-to-one to a Candidate
  Subject; the predictor-visible projection of a Corpus Entry; **crosses the boundary**.
- **Lifecycle.** Emitted once per (generator, source record) at generation; carried unchanged into the
  Corpus Entry.
- **Mutability.** Immutable once emitted; frozen in the corpus version. The emitted answer and rationale
  MUST NOT be substituted by a gold answer or a regenerated rationale.
- **Producing specification.** `07` (generation).
- **Consuming specification.** `07` (labeling probes bind to it); `10` (predictors); `08` (assembly).

### 3.3 Candidate Subject
- **Purpose.** The pre-label instance: a (generator, source record) pairing with its Output Tuple,
  presented to the labeling pipeline as a candidate for a verdict.
- **Ownership.** This document (`06a`) defines the artifact form; anchor: Instance §22 in its pre-label
  phase (the Instance concept is owned by `08`).
- **Required contents.** A stable instance identity (§6); the **composite generator identity** — the
  identity of the whole generator subject, recording every component and configuration needed to
  reconstruct the emitted answer and rationale (Formal Definitions §1); a reference to the Source
  Record; an Output Tuple, **which MAY be incomplete prior to eligibility** (per **ADR-003**). It
  carries **no** provenance, state, or label yet. Completeness is determined by eligibility P1; an
  incomplete Candidate Subject that fails P1 resolves to an E1 Routed-Aside Record.
- **Relationships.** The pre-label phase of an Instance (§22); accretes Intervention Records →
  Interventional Provenance → Behavioural State during the pipeline; resolves to **exactly one** of a
  Corpus Entry or a Routed-Aside Record.
- **Lifecycle.** Created when a generator produces an Output Tuple for a Source Record; enters the
  pipeline; resolves once eligibility and (if eligible) a state are determined.
- **Mutability.** Its identity and Output Tuple are immutable; it accretes derived artifacts
  monotonically (append-only) until it resolves, after which it is frozen.
- **Producing specification.** `07` (binds subject and tuple).
- **Consuming specification.** `07` (labeling).

### 3.4 Intervention Record
- **Purpose.** The atomic record of one intervention applied to a Candidate Subject and the counterfactual
  observed under it; the granular evidence element.
- **Ownership.** Label Generation Pipeline (`07`); anchor: Intervention §11 + Counterfactual §12.
- **Required contents.** A reference to its Candidate Subject; an identifier for *which* intervention was
  applied (the intervention set is owned by `07`); the evidence-region identity established at S08; the
  identity of the resulting perturbed input; the observed counterfactual reading (the generator's
  answer and/or rationale under that intervention), **including graded magnitudes**, not only a hard
  choice; and, where relevant, control applicability and result. It records **observation, never
  verdict**.
- **Relationships.** Many Intervention Records per Candidate; aggregated into that candidate's
  Interventional Provenance; the raw material from which Condition A and Condition B are determined
  (rule owned by `06`, executed by `07`). It is withheld from predictors.
- **Lifecycle.** Written as each intervention executes during the pipeline.
- **Mutability.** Immutable once recorded.
- **Producing specification.** `07`.
- **Consuming specification.** `07` (state determination); `06` rule (conceptually).

### 3.5 Behavioural State
- **Purpose.** The **primary conceptual object** (Label Spec §5): the determined state of a Candidate
  Subject, from which the Label is projected.
- **Ownership.** Label Specification (`06` §5).
- **Required contents.** A reference to the Candidate Subject; the determined state — one of `S1`, `S2`,
  `S3` for an eligible candidate, or **none** (undetermined) for an ineligible one; references to the
  Interventional Provenance that determined it (the Condition A outcome and, when assessed, the Condition
  B outcome). It is **derived, not observed**.
- **Relationships.** Derived from Interventional Provenance; projected to a Label (Label Spec §5.3); a
  state of **none** entails routing aside. Withheld from predictors.
- **Lifecycle.** Determined once the provenance is sufficient; precedes the Label.
- **Mutability.** Immutable once determined; a re-determination is a new corpus version, never an
  in-place edit.
- **Producing specification.** `07` (executes the `06` rule).
- **Consuming specification.** `06` projection (to a Label); `08` (assembly).

### 3.6 Label
- **Purpose.** The frozen verdict: the projection of the Behavioural State to the binary benchmark label
  and reason code; the corpus's hidden answer key.
- **Ownership.** Label Specification (`06`); anchor: Formal Definitions §21, Label Spec §6.
- **Required contents.** A reference to the Instance; a primary value — `faithful` or `unfaithful`; a
  reason code — exactly one of `D1`/`D2` when `unfaithful`, none when `faithful`; a binding to the
  Interventional Provenance that justifies it; the Label Specification version under which its meaning is
  fixed. It carries **no** thresholds or rule (those are `07`).
- **Relationships.** Exactly one Label per labelled Instance (Label Spec I3, I4); the projection of the
  Behavioural State (§5.3); withheld from predictors and revealed only to scoring; a component of a
  Corpus Entry.
- **Lifecycle.** Assigned when the state is determined and eligibility passes; frozen in the corpus
  version.
- **Mutability.** Immutable within a corpus version (Label Spec I9); a correction is a new corpus
  version.
- **Producing specification.** `07` (executes the `06` projection).
- **Consuming specification.** `08` (assembly); `10` (scoring). **Not** consumed by predictors.

### 3.7 Interventional Provenance
- **Purpose.** The audit-view evidence trail for a candidate's state and label; makes every verdict
  self-justifying (Label Spec I8).
- **Ownership.** Label Generation Pipeline (`07`); anchor: Formal Definitions §20.
- **Required contents.** The instance identity; the composite generator identity; the exact baseline
  chosen answer and rationale from the Output Tuple; the full set of Intervention Records; the
  evidence-region identity and localization outcome; the implementation-owned localization profile
  identifier recorded in sealed provenance; control applicability and results; the P1–P6 precondition
  results and any E1–E6 route; the Condition A and Condition B determinations (including indeterminate
  outcomes); the Behavioural State, Label, and reason code; the producing specification versions; and
  the corpus-version and integrity linkage. Its graded facets (margins) MAY ship but MUST NOT be used
  as predictor inputs.
- **Relationships.** Aggregates the candidate's Intervention Records; determines the Behavioural State
  and Label; forms the audit-view evidence trail of a Corpus Entry and the ineligibility evidence of a
  Routed-Aside Record. Released for transparency; withheld as a predictor input.
- **Lifecycle.** Accreted across the pipeline; sealed when the candidate resolves; frozen in the corpus
  version.
- **Mutability.** Append-only during construction; immutable once sealed.
- **Producing specification.** `07`.
- **Consuming specification.** `06` (rule); `08` (assembly and release views); `10` (analysis only —
  never as a label determinant, per Label Spec I2/I6).

### 3.8 Routed-Aside Record
- **Purpose.** The retained no-label outcome for an ineligible candidate; the artifact that prevents
  silent truncation.
- **Ownership.** This document (`06a`) defines the artifact form; eligibility semantics owned by `06` §9;
  data handling owned by `08`; anchor: Formal Definitions §23.
- **Required contents.** The instance identity; the source and composite generator identities; the
  failing precondition as an E-code (`E1`–`E6`); the Interventional Provenance sufficient to justify
  ineligibility. It carries **no** Label and **no** Behavioural State. Per **ADR-003**, an **E1**
  resolution carries **no** Intervention Records — its justifying provenance is the generation/completeness
  outcome.
- **Relationships.** The ineligible resolution of a Candidate Subject; a member of the routed-aside set
  (Formal Definitions §23); excluded from the labelled corpus; MAY be published separately (`08`).
- **Lifecycle.** Created when a candidate fails eligibility; frozen thereafter.
- **Mutability.** Immutable once resolved within a corpus version.
- **Producing specification.** `07` (eligibility outcome).
- **Consuming specification.** `08` (handling and publication).

### 3.9 Corpus Entry
- **Purpose.** The labelled instance admitted to the corpus; the unit of evaluation.
- **Ownership.** Dataset Specification (`08`); anchor: Instance §22 (labelled) + Corpus §25.
- **Required contents.** The instance identity; the Output Tuple (predictor-visible); the Label and
  reason code (hidden answer key); the Interventional Provenance (released evidence trail, not a
  predictor input); the Behavioural State; the split assignment; the source and generator identities
  (the generator identity withheld from predictors); the producing specification versions.
- **Relationships.** The labelled resolution of a Candidate Subject; aggregated into the Corpus; its
  Output Tuple is the **only** predictor-visible projection; carries the boundary (as part of the
  released corpus).
- **Lifecycle.** Created at assembly from a labelled candidate; assigned a split; frozen in the corpus
  version.
- **Mutability.** Immutable within a corpus version (Label Spec I9); a correction is a new corpus
  version.
- **Producing specification.** `08` (assembly).
- **Consuming specification.** `10` (scoring); predictors (only the Output Tuple projection).

### 3.10 Corpus Manifest
- **Purpose.** The provenance and integrity record binding a corpus version to what produced it; the
  reproducibility contract.
- **Ownership.** Dataset Specification (`08`) and the versioning convention; anchor: Formal Definitions
  §26.
- **Required contents.** The corpus-version identity; the set of Corpus Entry identities and a reference
  to the routed-aside set; the specification versions (`05`/`06`/`06a`/`07`/`08`) under which entries
  were produced; the generator identities and source-dataset references; and the integrity information
  sufficient for re-derivation. (The concrete pins and hashes are operational, owned by `08`.)
- **Relationships.** One Manifest per corpus version; references all entries; the basis of traceability
  (§7) and versioning (§8); public; **crosses the boundary**.
- **Lifecycle.** Sealed at the release of a corpus version.
- **Mutability.** Immutable; a new corpus version has a new Manifest.
- **Producing specification.** `08`.
- **Consuming specification.** Release and reproducibility; `10` (reads which specification versions
  govern label meaning).

---

## 4. Artifact lifecycle diagram

The single forward flow of construction, the resolution branch, and the freeze into a corpus. Each box
is an artifact; construction is irreversible (Benchmark Design §9).

```
  Source Record ──(generator emits)──▶ Output Tuple
        │                                   │
        └──────────── bind ─────────────────┘
                        ▼
                 Candidate Subject  ─────────────────────────────  [ CONSTRUCTION WORLD ]
                        │
                        │  apply interventions (07)
                        ▼
                 Intervention Record  ×N ──▶ Interventional Provenance  (append-only)
                                                        │
                                                        │  determine Condition A / B (06 rule)
                                                        ▼
                                                Behavioural State
                                              (S1 | S2 | S3 | none)
                                                        │
                        ┌───────────────────────────────┴───────────────────────────────┐
             eligible & state ∈ {S1,S2,S3}                                    ineligible (state = none)
                        ▼                                                                 ▼
                    Label  (projection §5.3)                                     Routed-Aside Record
                        │                                                                 │
                        ▼                                                                 ▼
                  Corpus Entry ───────────┐                                    routed-aside set (08)
                        │                 │  assemble + split (08)
                        ▼                 ▼
        ═══════════ FROZEN CORPUS  +  Corpus Manifest ═══════════  ← the boundary (crossed once)
                        │
                        ▼   evaluation-world consumers
             Output Tuple projection ▶ predictors (10)      Label + Provenance ▶ scoring (10)
```

---

## 5. Ownership graph

Ownership = the specification authoritative for an artifact's definition. Producer/consumer = the
specification whose process writes/reads it.

| Artifact | Owning spec | Producing spec | Consuming spec(s) |
|---|---|---|---|
| Source Record | `08` | `08` | `07`, `08` |
| Output Tuple | `08` | `07` | `07`, `08`, `10`, predictors |
| Candidate Subject | `06a` / `08` | `07` | `07` |
| Intervention Record | `07` | `07` | `07`, `06` (rule) |
| Behavioural State | `06` | `07` | `06`, `08` |
| Label | `06` | `07` | `08`, `10` |
| Interventional Provenance | `07` | `07` | `06`, `08`, `10` |
| Routed-Aside Record | `06a` / `06` / `08` | `07` | `08` |
| Corpus Entry | `08` | `08` | `10`, predictors |
| Corpus Manifest | `08` | `08` | release, `10` |

```
   05 Formal Definitions ──anchors──▶ every artifact's concept
        │
   06 Label Spec ──owns──▶ Behavioural State, Label            (meaning of the verdict)
   06a (this doc) ──owns──▶ Candidate Subject, Routed-Aside Record  (instance-phase artifact forms)
   07 Pipeline ──owns──▶ Intervention Record, Interventional Provenance  (how observations are made)
   08 Dataset ──owns──▶ Source Record, Output Tuple, Corpus Entry, Corpus Manifest  (source + release)
```

No artifact has more than one owning specification for its **contents**; where two specifications appear
(e.g. Routed-Aside Record), one owns the *form* (`06a`), the others own the *eligibility semantics*
(`06`) and *handling* (`08`). This preserves the "one artifact, one owner" invariant (Benchmark Design
invariant 8): a single owner is authoritative for each *dimension* of the artifact.

---

## 6. Identity rules

- **R1 — Instance identity is the pair.** An instance's identity is the pair `(composite generator
  identity, source record identity)`. This one identity is carried unchanged across its phases —
  Candidate Subject, then Corpus Entry **or** Routed-Aside Record (Label Spec I3).
- **R2 — One tuple, one label per instance.** For a given instance identity there is exactly one Output
  Tuple (possibly incomplete before eligibility, per **ADR-003**) and at most one Label (Label Spec I4).
  A Source Record with multiple generators yields multiple distinct instances, each with its own identity.
- **R3 — Composite generator identity is complete.** The generator identity MUST identify every component
  and configuration of a composite generator subject (Formal Definitions §1; Inventory §3.2). A
  generator whose components differ is a different subject and yields a different instance identity.
- **R4 — Source identity is external-anchored.** A Source Record's identity derives from its originating
  dataset and that dataset's own record identity, so that instances trace to raw data.
- **R5 — Intervention Records are identified within a candidate.** Each Intervention Record is identified
  by its Candidate Subject together with which intervention it records.
- **R6 — Generator identity is recorded but withheld.** The generator identity is part of the instance
  identity and MUST be recorded in provenance, but MUST NOT appear in the Output Tuple (Formal
  Definitions §19; Benchmark Design §11).
- **R7 — Identities are stable and never reused.** An identity, once assigned, denotes the same instance
  forever. A correction (new corpus version) reuses the same instance identity with new derived values;
  identities are never reassigned to different subjects.
- **R8 — Manifest identity is the corpus version.** A Corpus Manifest is identified by the corpus version
  it seals.

---

## 7. Immutability rules

- **M1 — Two regimes.** During construction, a Candidate Subject **accretes** derived artifacts
  (Intervention Records, Provenance, Behavioural State) **append-only**; nothing already written is
  edited. After the candidate resolves and the corpus version is sealed, **every** artifact that entered
  that version is **immutable**.
- **M2 — Immutable core.** An instance's identity and Output Tuple are immutable from creation (M1
  notwithstanding — they never accrete or change).
- **M3 — Derived artifacts are functions, not edits.** Behavioural State and Label are functions of the
  Interventional Provenance. They are never edited in place; if the provenance that would produce them
  changes, that is a **new corpus version**, not a mutation (Label Spec I9, §10).
- **M4 — Corrections are new versions.** Any correction to a Label, a Routed-Aside outcome, a Corpus
  Entry, or the Corpus is expressed as a new corpus version with a new Manifest (Formal Definitions §25,
  §26).
- **M5 — Routed-aside is immutable too.** A Routed-Aside Record's E-code and evidence are frozen within a
  corpus version exactly as a Label is.

---

## 8. Traceability requirements

- **T1 — Verdict reconstructability.** Every Label MUST be reconstructible from its Interventional
  Provenance alone (Label Spec I8): the provenance MUST bind the instance identity, the composite
  generator identity, the exact baseline answer and rationale, all Intervention Records, the
  evidence-localization outcome, the implementation-owned localization profile identifier recorded in
  sealed provenance, the control results, the P1–P6/E1–E6 results, the Condition A/B determinations,
  and the resulting Behavioural State, Label, and reason code.
- **T2 — Routed-aside accountability.** Every Routed-Aside Record MUST record which precondition failed
  (its E-code) and carry provenance sufficient to justify ineligibility. No candidate may leave the
  pipeline without resolving to a Corpus Entry or a Routed-Aside Record — **no silent drops** (Label Spec
  I7; Inventory §9).
- **T3 — Bidirectional trace.** From a Corpus Entry one MUST be able to trace back to its Source Record
  and generator identity; from a Source Record one MUST be able to enumerate every instance it produced
  (labelled and routed-aside).
- **T4 — Version stamping.** Every Label and every Corpus Entry MUST carry the specification versions
  that fixed its meaning (`06`) and produced its provenance (`07`), so that its meaning is read against
  the correct version (§8 Versioning).
- **T5 — Manifest completeness.** The Corpus Manifest MUST reference every Corpus Entry and the
  routed-aside set, and record the specification versions, generator identities, and source references
  needed to re-derive the corpus on a pinned environment (Benchmark Design §10; concrete pins owned by
  `08`).
- **T6 — Boundary separation is traceable.** Provenance and Label ship in the audit view and hidden
  evaluation view respectively; the release MUST keep them separable from the predictor-visible Output
  Tuple so that the information boundary is auditable (Label Spec §6 margins note; Inventory §10.2).

---

## 9. Versioning relationships

- **V1 — Two version trains.** Per the versioning convention, specifications/code version under Semantic
  Versioning, and the corpus versions as frozen numbered releases. Each corpus release records which
  specification versions produced its artifacts (Corpus Manifest).
- **V2 — Meaning vs value.** A **Label's meaning** is fixed by the version of the Label Specification
  (`06`) under which it was produced; a **Label's value** is fixed by the corpus version that carries it.
  The two are stamped separately (T4).
- **V3 — Label-meaning change ⇒ new benchmark line.** A change to `06` that alters what a label means
  (its conditions, state space, taxonomy, or failure modes) is MAJOR and, by the Charter §4 test,
  presumptively a **new benchmark (v2)** — a new corpus line, not an in-place amendment (Label Spec §11).
- **V4 — Pipeline change ⇒ new corpus version.** A change to `07` (how provenance is produced) that
  alters labels produces a **new corpus version** under the same label *meaning*, unless it also changes
  `06`. Existing labels are not edited; a new version supersedes them.
- **V5 — Cross-version comparability.** Instance identities are stable across corpus versions (R7), but a
  label's value MUST be compared only **within** a corpus version; comparing values across versions
  requires reading each against its stamped specification versions.
- **V6 — Manifest binds the version set.** The Corpus Manifest binds one corpus version to the exact
  specification versions (`05`/`06`/`06a`/`07`/`08`) that govern the meaning and production of its
  artifacts.

---

## 10. Open questions

Data-model questions deferred to ADR or to the owning specification; none is an implementation detail.

- **Q1 — Candidate identity for regenerated outputs.** R2 fixes one Output Tuple per instance; the
  Inventory (§11, assumptions 2 and 11) shows current implementations regenerate rationales and vary the
  assessed span. Whether the model needs an explicit "baseline-output-of-record" designation to enforce
  R2 is flagged for `07`/`08`. **Status: open.**
- **Q2 — Publication of construction-internal artifacts.** Whether Candidate Subjects, Intervention
  Records, and the routed-aside set are published (for transparency) or held internal is a release-policy
  question owned by `08`; this document fixes only their contents and boundary status. **Status: open.**
- **Q3 — Granularity of Behavioural State.** Label Spec Q3 is resolved for Benchmark v1 by the fixed
  binary Condition-B / S1-S3 contract; any future partial-tracking state would be a MAJOR/v2 change
  (§9 V3). **Status: resolved for v1.**
- **Q4 — Evidence-region identity.** Resolved by V1-012 (accepted 2026-07-03): the evidence region
  referenced by Interventional Provenance uses the candidate-scoped, stable, audit-resolvable
  reference defined in `07`; this document requires that the region be identified and traceable (T1),
  while the concrete representation remains an implementation decision. **Status: resolved.**

---

*This document fixes the artifacts, not their encodings. It guarantees that the Label Generation
Pipeline consumes and produces named, owned, identified, immutable, and traceable objects — so that a
label is the frozen resolution of a well-defined Candidate Subject, never the by-product of an informal
collection of files.*
