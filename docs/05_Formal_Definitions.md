---
Title: Formal Definitions
Status: Accepted
Benchmark-Version: v1.0
Last-reviewed: 2026-07-01
Related:
  - docs/00_Benchmark_Charter.md
  - docs/01_Benchmark_Design.md
  - docs/03_Problem_Definition.md
  - docs/design/Formal_Definition_Dependency_Graph.md
  - docs/06_Label_Specification.md
  - docs/07_Label_Generation_Pipeline.md
  - docs/08_Dataset_Specification.md
  - docs/09_Baseline_Systems.md
  - docs/10_Evaluation_Protocol.md
---

# Formal Definitions

*This document is the benchmark's normative vocabulary. Every later specification, implementation,
ADR, and release inherits the meanings fixed here. It reads as an engineering standard: it states
what each term **is**, and delegates how each term is **computed** to the specification that owns it.
It follows the definition order fixed by the approved
[Formal Definition Dependency Graph](design/Formal_Definition_Dependency_Graph.md), which is
authoritative for ordering and for the elimination of circular dependencies.*

---

## Normative preamble

**Status of this vocabulary.** The definitions below are **normative**. A term used in any project
document carries the meaning fixed here and no other. Changing a definition requires an ADR; changing
the meaning of `faithfulness` or `label` additionally engages [Charter](00_Benchmark_Charter.md) §4–§5.

**Requirement keywords.** MUST, MUST NOT, SHOULD, and MAY are used in the RFC-2119 sense.

**Three levels of meaning, and which this document fixes.** Every entry distinguishes:

- **Conceptual definition** — *what the term is.* Fixed here; normative; implementation-independent.
- **Operational rule** — *the procedure that decides the term for a concrete case* (which
  perturbations, which threshold, which criterion). This document fixes an operational rule only when
  no other specification owns it; otherwise it names the owner and **defers**.
- **Implementation** — *the code that executes an operational rule.* **Never** fixed in any
  specification, including this one; implementations are executors governed by
  [Benchmark Design](01_Benchmark_Design.md) §10. Entries therefore mark only *Conceptual* and
  *Operational*; implementation is out of scope by standing rule.

**Anti-circularity.** Terms are defined strictly in the approved order. No entry references a term
defined later. The three hazards the dependency graph identified are honoured as hard rules:

- `faithfulness` is defined without reference to `label`; the `label` artifact references
  `faithfulness` (never the reverse).
- `plausibility` is defined without reference to `faithfulness`.
- `evidence` and `grounding` are defined without reference to `faithfulness`.

**Ownership.** Each term has at most one owning specification for its operational rule; no later
document redefines a term owned here or elsewhere — it references it (Benchmark Design §6, invariant 8).

**Entry format.** Each entry provides: **Definition (conceptual)** · **Operational** (rule or deferral)
· **Rationale** · **Notes** · **Related** · **Owned by** (only when an operational rule is delegated).

**Terms intentionally omitted.** Derivable and downstream-owned terms are listed in §35, not given
standalone entries, per the dependency graph §6.

---

## Block A — Foundational

*Primitives that exist before any benchmark process. They depend on external givens only.*

### 1. Generator
**Definition (conceptual).** Any model that, given a `source record`, produces a `chosen answer` and a
`rationale`. The generator is the *subject* every `label` is a fact about.
**Operational.** The set of generators studied by the benchmark is deferred.
**Rationale.** Faithfulness is a property *of a model*; fixing the generator as the subject is what
keeps the label from collapsing into a property of text.
**Notes.** A generator exists in the construction world only. Which generator produced a given
`output tuple` (its *identity*) is withheld from predictors; "generator identity" is an attribute of
this term, not a separate term (§35). A generator MAY be implemented as a **composite system** —
several models, stages, or checkpoints that jointly map a `source record` to a `chosen answer` and a
`rationale`. The benchmark treats any such system as a single subject and remains
implementation-independent (Benchmark Design §10); how the subject is constructed is out of scope here.
**Related.** chosen answer, rationale, output tuple, intervention, faithfulness.
**Owned by.** [Dataset Specification](08_Dataset_Specification.md) (generator set) and
[Label Generation Pipeline](07_Label_Generation_Pipeline.md) (how a generator is run).

### 2. Image
**Definition (conceptual).** The visual input associated with a `source record` and presented to a
`generator`; the object an `intervention` disturbs.
**Operational.** Direct — no operational rule required at this level.
**Rationale.** `evidence`, `image-dependence`, and `grounding` are all defined on the image.
**Notes.** "The image" denotes the visual input *as presented* to the generator. Whether that input
carries `grounding annotations` (annotated vs. unannotated variants) is governed by §10 and the
Dataset Specification.
**Related.** intervention, evidence, image-dependence, grounding, output tuple.

### 3. Question
**Definition (conceptual).** The interrogative stem of a `source record` that a `generator` must
answer.
**Operational.** Direct.
**Rationale.** A component of the `source record` and the `output tuple`.
**Notes.** —
**Related.** options, source record, output tuple.

### 4. Options
**Definition (conceptual).** The fixed set of candidate answers accompanying a `question` in a
multiple-choice `source record`.
**Operational.** Direct.
**Rationale.** The `chosen answer` is a selection among the options; the multiple-choice frame is
assumed by the benchmark (Problem Definition, scope).
**Notes.** —
**Related.** question, chosen answer, source record.

### 5. Chosen answer
**Definition (conceptual).** The single `option` a `generator` selects for a `question`.
**Operational.** Direct (a selection among `options`).
**Rationale.** `image-dependence` and `evidence` are properties of this selection; it is the object
the answer-side intervention probes.
**Notes.** Distinct from any gold or correct answer the source may carry; the benchmark studies the
*model's* choice, not its correctness. (Any restriction of scope to correct answers is an eligibility
rule owned by the Label Specification, not part of this definition.)
**Related.** options, generator, image-dependence, output tuple.

### 6. Rationale
**Definition (conceptual).** The chain-of-thought text a `generator` produces to accompany its
`chosen answer`.
**Operational.** Direct.
**Rationale.** The central object under test: `plausibility` and `grounding` are measured on it, and
`faithfulness` is *about* it.
**Notes.** —
**Related.** chosen answer, plausibility, grounding, faithfulness, output tuple.

### 7. Predictor
**Definition (conceptual).** Any agent evaluated by the benchmark. A predictor receives an
`instance`'s `output tuple` and produces a guess of that instance's `label`, with no access to the
`generator`, its identity, or any interventional information.
**Operational.** The prediction interface and target format are deferred.
**Rationale.** The predictor is defined entirely by the information boundary; "solving the benchmark"
is defined relative to it.
**Notes.** The authors' `baselines` are predictors and receive no access the public lacks
(Benchmark Design invariant 6).
**Related.** output tuple, recovery, baseline, construction/evaluation boundary.
**Owned by.** [Evaluation Protocol](10_Evaluation_Protocol.md).

### 8. Construction / evaluation boundary
**Definition (conceptual).** The one-directional divide separating the **construction world** (the
`generator` present, `intervention` possible) from the **evaluation world** (the generator absent,
only the frozen `corpus` available). It is crossed exactly once, by the corpus.
**Operational.** What crosses is fixed by other terms: the `output tuple` crosses (available to
predictors); the `label`, `interventional provenance`, and generator identity do not (withheld).
**Rationale.** The benchmark's central asymmetry (Benchmark Design §1); the source of the task's
difficulty.
**Notes.** "Construction world" and "evaluation world" denote the two sides of this one term and are
not separately defined (§35). Construction is irreversible: nothing crosses back (Benchmark Design §9).
**Related.** intervention, corpus, output tuple, recovery.

### 9. Source record
**Definition (conceptual).** A model-free unit of raw material: a multiple-choice visual question
comprising an `image`, a `question`, `options`, and any `grounding annotations`. It carries no
generator, chosen answer, rationale, or label.
**Operational.** The normalization of external data into source records is deferred.
**Rationale.** The origin of every `instance`; kept distinct from the `output tuple` so that provenance
and licensing remain traceable to raw data.
**Notes.** Source records are adapted from existing datasets, not invented (Problem Definition, scope).
**Related.** image, question, options, grounding annotations, instance.
**Owned by.** [Dataset Specification](08_Dataset_Specification.md).

### 10. Grounding annotations
**Definition (conceptual).** Region- or object-level annotations that ship **with** a `source record`
(for example, marked regions of the `image`) and are available as **inputs**. They are distinct from
behavioural `grounding` (§15).
**Operational.** Their format is deferred to the Dataset Specification; any use of them to localize
`evidence` is deferred to the Label Generation Pipeline.
**Rationale.** Some source datasets provide region data used downstream; the term is required so that
input annotations are never confused with a measured quantity.
**Notes.** **Naming rule (normative).** The structural annotations are ALWAYS called "grounding
annotations" (never bare "grounding"); the behavioural correspondence of §15 is ALWAYS called
"grounding." The two MUST NOT be conflated. This resolves the naming hazard the dependency graph left
open (§7 there).
**Related.** image, source record, evidence, grounding.
**Owned by.** [Dataset Specification](08_Dataset_Specification.md).

---

## Block B — Behavioral

*Terms describing model behavior under disturbance and the causal property. Defined before the
structural artifacts that record them, so that `faithfulness` precedes `label` (dependency graph §4).*

### 11. Intervention
**Definition (conceptual).** A deliberate, controlled modification of the visual input given to a
`generator`, applied during construction, whose purpose is to reveal how the generator's `chosen
answer` and `rationale` depend on that input.
**Operational.** The concrete interventions — which modifications, their parameters, and how many —
are deferred.
**Rationale.** The only operation that yields a faithfulness verdict rather than a plausibility
estimate (Problem Definition §4); the engine of ground truth.
**Notes.** An intervention exists in the construction world only and MUST NOT be available to a
`predictor` (Benchmark Design invariant 4). Defined as the *operation*; the observed behaviour under
it is the `counterfactual` (§12) — this ordering removes the intervention⇄counterfactual hazard.
**Related.** generator, image, counterfactual, construction/evaluation boundary.
**Owned by.** [Label Generation Pipeline](07_Label_Generation_Pipeline.md).

### 12. Counterfactual
**Definition (conceptual).** The behavior a `generator` exhibits — the `chosen answer` it selects and
the `rationale` it produces — under an `intervention`, as opposed to under the original input.
**Operational.** Which counterfactual conditions are observed, and how their outcomes are read, are
deferred.
**Rationale.** The quantity a `label` is computed from, and precisely the quantity withheld from
predictors; the gap the benchmark asks a predictor to bridge (Problem Definition §6).
**Notes.** A counterfactual is always relative to an `intervention`. It MUST NOT cross the
construction/evaluation boundary as a predictor input.
**Related.** intervention, image-dependence, faithfulness, recovery.
**Owned by.** [Label Generation Pipeline](07_Label_Generation_Pipeline.md).

### 13. Image-dependence
**Definition (conceptual).** The extent to which a `generator`'s `chosen answer` changes under
`intervention` on the `image` rather than remaining the same; the answer's causal reliance on visual
input.
**Operational.** The exact criterion for "the answer depends on the image" is deferred (which
interventions count, and what magnitude of change qualifies).
**Rationale.** The precondition on which `faithfulness` is conditioned; it separates an answer that
does not use the image from one that does.
**Notes.** A property of the `chosen answer`, not of the `rationale`. Defined via `counterfactual`,
not via `faithfulness`.
**Related.** counterfactual, chosen answer, evidence, faithfulness.
**Owned by.** [Label Specification](06_Label_Specification.md) (criterion),
[Label Generation Pipeline](07_Label_Generation_Pipeline.md) (probes).

### 14. Evidence
**Definition (conceptual).** The visual content of the `image` on which a `generator`'s `chosen answer`
causally depends — the content whose disturbance changes the answer.
**Operational.** How the evidence is localized or identified for a given instance is deferred.
**Rationale.** The referent of "faithful to the evidence"; without it, `grounding` and `faithfulness`
cannot be told apart.
**Notes.** Defined via `image-dependence` (a property of the answer), NOT via `faithfulness` — this is
the anchor that keeps the evidence⇄faithfulness⇄grounding triangle acyclic. Distinct from `grounding
annotations` (§10), which are *inputs*, not this *measured* content.
**Related.** image-dependence, image, grounding, faithfulness.
**Owned by.** [Label Generation Pipeline](07_Label_Generation_Pipeline.md).

### 15. Grounding
**Definition (conceptual).** The correspondence between the visual content a `rationale` states or
implies and what is actually present in the `image` (or in the `evidence`) — how well the rationale's
claims about the image match the image.
**Operational.** How correspondence is measured is deferred (it appears as a `baseline` feature and in
reporting).
**Rationale.** Grounding is the quantity most often mistaken for `faithfulness`; it MUST be defined
precisely so that it can be explicitly *excluded* from the label.
**Notes.** Grounding is a **correlate** of faithfulness, not faithfulness itself (Problem Definition
§2). It is defined without reference to the `counterfactual`, so a rationale MAY be well-grounded yet
unfaithful. See the naming rule in §10.
**Related.** evidence, rationale, image, faithfulness, plausibility.
**Owned by.** [Baselines](09_Baseline_Systems.md), [Evaluation Protocol](10_Evaluation_Protocol.md)
(measurement).

### 16. Plausibility
**Definition (conceptual).** The extent to which a `rationale` appears coherent, well-formed, and
convincing to an observer reading it (optionally alongside the `image`) — a property of the rationale
*as read*, independent of the generator's behavior under disturbance.
**Operational.** How plausibility is estimated is deferred.
**Rationale.** The observer-facing property the benchmark refuses as ground truth; defined
independently so it can never silently serve as a proxy for the label.
**Notes.** Defined **without reference to `faithfulness`** (breaks the define-by-negation hazard). The
empirical divergence between plausibility and faithfulness is an *observation* recorded in Problem
Definition §3, not a definitional link.
**Related.** rationale, faithfulness, grounding, hard core.
**Owned by.** [Baselines](09_Baseline_Systems.md), [Evaluation Protocol](10_Evaluation_Protocol.md).

### 17. Faithfulness
**Definition (conceptual).** A property of a `generator` on a `source record`, concerning whether the
generator's `rationale` reflects the `evidence` its `chosen answer` causally depends on, as revealed by
`intervention`. It concerns two behaviours: whether the answer is `image-dependent`, and whether the
rationale tracks the evidence the answer relies on.

**Scope qualifiers (normative; inherited wherever the term is used).** In this benchmark,
faithfulness is:
- **behavioural** — a statement about what the generator *does* under disturbance, NOT about its
  internal mechanism, representations, or "what it really thought"; and
- **necessary-condition** — failing the behavioural tests licenses the reading "not behaviourally
  faithful"; passing them licenses *nothing* about internal computation.

This scope is a standing [Charter](00_Benchmark_Charter.md) commitment and MUST be restated wherever
the label is defined or reported.

**Operational.** The exact rule that maps intervention outcomes (image-dependence together with the
rationale's tracking of the evidence) to a faithfulness verdict — including the distinction between
failure modes — is deferred.
**Rationale.** The central construct; every `label` encodes it.
**Notes.** Defined via `counterfactual`, `image-dependence`, and `evidence` — and NOT via `label`
(this is the one-directional edge that makes the vocabulary acyclic). It is defined on its own terms,
not as "not `plausible`" or "not `grounded`"; the contrast with those correlates is stated here in
Notes only. The verdict values "faithful"/"unfaithful" are derivable and not separately defined (§35).
**Related.** counterfactual, image-dependence, evidence, grounding, plausibility, label meaning.
**Owned by.** [Label Specification](06_Label_Specification.md) (the verdict rule and failure modes).

### 18. Label meaning
**Definition (conceptual).** The `faithfulness` verdict for a (`generator`, `source record`) pair — the
semantic content that an `intervention` establishes, independent of whether or how it is recorded.
**Operational.** The set of admissible verdict values and the rule that assigns them are deferred.
**Rationale.** Fixing the verdict content on its own terms — with no reference to any recording
artifact — is what keeps the vocabulary acyclic: the semantic verdict is defined here; the artifact
that records it references this entry, never the reverse.
**Notes.** This entry fixes only that the verdict content *is* the `faithfulness` verdict. Its taxonomy
of values and any diagnostic reason codes are owned downstream and are not enumerated here.
**Related.** faithfulness.
**Owned by.** [Label Specification](06_Label_Specification.md).

---

## Block C — Structural

*Artifacts and organization. Each records a property already defined in Block B, so no structural
container forward-references an undefined meaning.*

### 19. Output tuple
**Definition (conceptual).** The bundle of information a `predictor` is permitted to see for one
`instance`: the `image`, `question`, `options`, `chosen answer`, `rationale`, and any `grounding
annotations` from the source. It excludes the generator's identity and all interventional information.
**Operational.** The field-level schema is deferred.
**Rationale.** Fixes the "available to predictors" side of the information boundary precisely
(Benchmark Design §11; the Benchmark Contract).
**Notes.** The `image` is a required member of the tuple: the predictor receives the visual question,
consistent with Benchmark Design §11 and the Problem Definition. An output tuple MUST NOT contain
`interventional provenance`, generator identity, or the `label`. It is exactly what crosses the
construction/evaluation boundary as a predictor input. Per **ADR-003**, an output tuple is guaranteed
**complete** only on the predictor-visible side (inside a `Corpus Entry`); prior to eligibility a
`Candidate Subject`'s output tuple MAY be **incomplete** (the `chosen answer` and/or `rationale` absent).
"Incomplete" is a pre-eligibility *state* of this artifact, not a new term; an incomplete output tuple
MUST NOT cross the boundary.
**Related.** image, question, options, chosen answer, rationale, grounding annotations, instance,
recovery.
**Owned by.** [Dataset Specification](08_Dataset_Specification.md) (schema).

### 20. Interventional provenance
**Definition (conceptual).** The recorded observations of a `generator`'s `counterfactual` behavior
from which that instance's `label` is computed — the evidence trail that justifies the label. Its
continuous facets (commonly called *margins*) are part of this term, not a separate one.
**Operational.** Exactly what is recorded is deferred.
**Rationale.** Makes labels self-justifying and auditable (Benchmark Design §6, §8).
**Notes.** MAY be released with the `corpus` for transparency, but MUST NOT be used as a `predictor`
input (Benchmark Design invariant 4) — it is the answer key's working, not a feature.
**Related.** counterfactual, label, hard core.
**Owned by.** [Label Generation Pipeline](07_Label_Generation_Pipeline.md).

### 21. Label
**Definition (conceptual).** The frozen record, attached to an `instance`, of that instance's `label
meaning` (its `faithfulness` verdict). It is the `corpus`'s answer key for the instance.
**Operational.** The admissible values and the rule assigning them are deferred.
**Rationale.** Separating the *artifact* (this entry) from the *property* (`faithfulness`, §17) and the
*content* (`label meaning`, §18) is what breaks the central circular dependency.
**Notes.** A label is withheld during prediction and revealed only to the scoring process
(Benchmark Design §8). It is immutable within a `corpus` version; a correction is a new version, never
an edit (invariant 5). Reason codes and thresholds are NOT defined here.
**Related.** label meaning, faithfulness, instance, interventional provenance.
**Owned by.** [Label Specification](06_Label_Specification.md).

### 22. Instance
**Definition (conceptual).** One unit of the benchmark: an `output tuple` produced by a specific
`generator` from a specific `source record`, together with the construction-time information it accrues
— `interventional provenance` always, and, **when a `faithfulness` label is established for it**, a
`label` and a `split` assignment. An instance for which no label can be established carries neither and
does not enter the `corpus`. In the evaluation world a labelled instance is reduced to its `output
tuple` plus its withheld `label`.
**Operational.** The instance schema is deferred.
**Rationale.** The unit of both construction and evaluation.
**Notes.** One `source record` MAY yield many instances — one per generator. A `label` (and its
`split` assignment) is an **optional** attribute of an instance, present only when a `faithfulness`
verdict is established; instances lacking it are set aside rather than entering the `corpus`. This is
the minimal ontology adjustment that reconciles an instance with the unlabelled cases. Every field an
instance carries is defined before this entry, so there is no forward semantic reference (dependency
graph §4, the "seam").
**Related.** output tuple, generator, source record, label, interventional provenance, split, corpus.
**Owned by.** [Dataset Specification](08_Dataset_Specification.md).

### 23. Routed-aside set
**Definition (conceptual).** The set of `instance`s for which a meaningful `faithfulness` `label`
cannot be established — because the preconditions are unmet or the case is ambiguous — set aside rather
than silently discarded.
**Operational.** What makes an instance ineligible is deferred to the Label Specification; how the set
is handled and reported is deferred to the Dataset Specification.
**Rationale.** Prevents silent truncation and the hidden bias it introduces (Benchmark Design §5).
**Notes.** Its members are `instance`s (§22) that carry no `label`; they are excluded from the corpus's
labelled population and MAY be published separately for transparency.
**Related.** instance, faithfulness, corpus.
**Owned by.** [Label Specification](06_Label_Specification.md) (eligibility),
[Dataset Specification](08_Dataset_Specification.md) (handling).

### 24. Split
**Definition (conceptual).** A partition of `instance`s into **benchmark roles** — for example,
training material and one or more held-out evaluation partitions — such that generalization can be
measured. The reserved partitions (held-out generators, question types, or datasets) are together the
**held-out worlds**, an application of this term rather than a separate one (§35). A benchmark split is
distinct from any partition a `source record`'s originating dataset may already carry (for instance, a
source dataset's own train/validation division): the latter is a property of the source, not a
benchmark split.
**Operational.** The concrete partitions and their disjointness rules are deferred.
**Rationale.** Turns the task into a generalization test rather than a memorization test (Problem
Definition §6; `transfer`, §31).
**Notes.** Enforced disjointness is what prevents train/evaluation contamination. A source's
pre-existing partitions do not determine benchmark splits; the two remain distinct objects even where
external data uses the word "split" for both.
**Related.** instance, generator, transfer, corpus.
**Owned by.** [Dataset Specification](08_Dataset_Specification.md).

### 25. Corpus
**Definition (conceptual).** The static, versioned collection of labelled `instance`s organized into
`split`s; the benchmark's deliverable, and the single artifact that crosses the construction/evaluation
boundary.
**Operational.** Composition, size, and balance are deferred.
**Rationale.** The frozen product on which all evaluation runs (Benchmark Design §6).
**Notes.** Immutable per version; a correction is a new version (Benchmark Design §8, invariant 5).
**Related.** instance, split, corpus manifest, recovery.
**Owned by.** [Dataset Specification](08_Dataset_Specification.md).

### 26. Corpus manifest
**Definition (conceptual).** The provenance and integrity record accompanying a `corpus` release that
makes it reproducible and citable — identifying, by pinned inputs and content hashes, exactly what was
released.
**Operational.** The manifest's fields are deferred.
**Rationale.** Reproducibility is a property of the corpus, not of the code (Benchmark Design §10).
**Notes.** Public. It underwrites the reproducibility guarantee: a release is *re-derivable* on a
pinned environment, not necessarily byte-identical.
**Related.** corpus.
**Owned by.** [Dataset Specification](08_Dataset_Specification.md) and the versioning convention.

---

## Block D — Evaluation

*Terms for measuring a `predictor` against the frozen `corpus`. They depend on all lower blocks; their
metrics and thresholds are owned by the Evaluation Protocol.*

### 27. Recovery
**Definition (conceptual).** The `predictor`'s task: to reproduce, from an `instance`'s `output tuple`
alone, the withheld `faithfulness` verdict recorded in that instance's `label`, without performing or
re-creating the `intervention`.
**Operational.** The exact prediction target and output format are deferred.
**Rationale.** Names precisely what "solving the benchmark" means (Problem Definition §6).
**Notes.** Recovery bridges non-causal evidence (the tuple) to a causal verdict (the label).
Recovering a label by querying, re-running, or perturbing the `generator` is out of bounds by
definition (Problem Definition R7).
**Related.** output tuple, label, counterfactual, construction/evaluation boundary, success criterion.
**Owned by.** [Evaluation Protocol](10_Evaluation_Protocol.md).

### 28. Baseline
**Definition (conceptual).** A `predictor` constructed by the benchmark authors to calibrate the
task's difficulty — from a deliberately weak reference to a strong one. A baseline is a predictor and
holds no privileged access beyond any other predictor.
**Operational.** Which baselines exist and the contract each must satisfy are deferred.
**Rationale.** Baselines provide the anchors against which "beyond trivial" is judged.
**Notes.** Authors' baselines are peers of external predictors (Benchmark Design invariant 6).
**Related.** predictor, recovery, floor, corpus.
**Owned by.** [Baselines](09_Baseline_Systems.md).

### 29. Floor
**Definition (conceptual).** The performance attainable using only trivial or non-visual signal
available in the `output tuple`; the reference level a genuine solution MUST exceed to show it uses
more than surface cues.
**Operational.** Which `baseline` realizes the floor, and the semantics of "exceed," are deferred.
**Rationale.** Distinguishes genuine `recovery` from riding a correlate such as `plausibility`
(Problem Definition §2).
**Notes.** The floor is a *reference level*, not a numeric threshold fixed here.
**Related.** baseline, plausibility, success criterion, failure criterion.
**Owned by.** [Baselines](09_Baseline_Systems.md), [Evaluation Protocol](10_Evaluation_Protocol.md).

### 30. Hard core
**Definition (conceptual).** The **balanced** evaluation subset centred on the region where the
plausibility/faithfulness divergence is sharpest: high-`plausibility` (and/or high-`grounding`)
`instance`s whose `label` is **unfaithful** (the hard *negatives*, where a plausibility judge is expected
to fail), paired with **matched** high-plausibility `instance`s whose `label` is **faithful** (the hard
*positives*). Both label classes are present **so that a threshold-free discriminative measure (AUROC) is
defined** on the subset (Evaluation Protocol §7).
**Operational.** The selection criteria, the matching/balance rule, and the pinned membership are
deferred (owned by the Dataset Specification).
**Rationale.** The benchmark's sharpest discriminative test (Vision; Problem Definition §3); balancing is
what makes that test well-defined.
**Notes.** Defined entirely via already-defined terms (`plausibility`, `grounding`, `label`); its
membership criteria and pinned selectors are owned downstream. The balanced two-class construction is a
corpus-construction contract (Dataset Specification §6.8), not a change to this concept.
**Related.** plausibility, grounding, faithfulness, label.
**Owned by.** [Dataset Specification](08_Dataset_Specification.md) (membership),
[Evaluation Protocol](10_Evaluation_Protocol.md) (reporting).

### 31. Transfer
**Definition (conceptual).** The extent to which `recovery` achieved on training material holds on the
held-out worlds of a `split` (unseen generators, question types, or datasets) — whether a faithfulness
signal generalizes rather than fitting one world.
**Operational.** Which comparisons express transfer, and how they are measured, are deferred.
**Rationale.** The [Charter](00_Benchmark_Charter.md) refuses to *assume* that faithfulness signatures
generalize; transfer is how that refusal is turned into a measurement.
**Notes.** Low transfer indicates world-specific signal (e.g., generator style), not `faithfulness`.
**Related.** split, recovery, success criterion, failure criterion.
**Owned by.** [Evaluation Protocol](10_Evaluation_Protocol.md).

### 32. Success criterion
**Definition (conceptual).** The condition under which a `predictor` is judged to have recovered
`faithfulness`: recovering `label`s on held-out `instance`s beyond the `floor` and with adequate
`transfer`.
**Operational.** The exact metrics and thresholds are deferred.
**Rationale.** Makes "success" measurable rather than rhetorical (the Benchmark Contract).
**Notes.** Stated at the level of *what*, never *how much*.
**Related.** recovery, floor, transfer, scorecard.
**Owned by.** [Evaluation Protocol](10_Evaluation_Protocol.md).

### 33. Failure criterion
**Definition (conceptual).** The condition under which a `predictor` is judged NOT to have recovered
`faithfulness`: performance collapsing to the `floor`, or depending on generator identity, rationale
style, `plausibility`, or `grounding` instead of `transfer`ring across held-out worlds.
**Operational.** The exact metrics and thresholds are deferred.
**Rationale.** Names correlate-riding so that it can be detected and reported (Problem Definition §8).
**Notes.** The complement of the `success criterion`; both are stated as *what*, not *how much*.
**Related.** floor, transfer, plausibility, grounding, recovery.
**Owned by.** [Evaluation Protocol](10_Evaluation_Protocol.md).

### 34. Scorecard
**Definition (conceptual).** The artifact produced by evaluating a `predictor` against the frozen
`corpus`: the record of how well the predictor satisfied the `success criterion`.
**Operational.** Its fields, metrics, and reporting rules are deferred.
**Rationale.** The evaluation-world deliverable (Benchmark Design §6) — the benchmark's only artifact
besides the `corpus`.
**Notes.** Produced in the evaluation world; it never touches a `generator`.
**Related.** corpus, recovery, success criterion, failure criterion.
**Owned by.** [Evaluation Protocol](10_Evaluation_Protocol.md).

---

## 35. Terms intentionally not defined here

Per the dependency graph §6, the following are **not** given standalone definitions: they are either
derivable from the terms above by a short, obvious composition, or their operational meaning is owned
by a downstream specification. Any document needing them MUST reference the source below rather than
redefine them.

| Term | Not defined because | Source / owner |
|---|---|---|
| **faithful / unfaithful** | The two values of the `faithfulness` verdict. | §17 + §18; values owned by [06](06_Label_Specification.md) |
| **behavioural, necessary-condition** | Scope qualifiers *of* `faithfulness`, stated inside §17. | §17 |
| **margins** | A continuous facet of `interventional provenance`. | §20 |
| **diagnostic provenance / reason codes** | The taxonomy of *why* an instance is unfaithful. | [Label Specification](06_Label_Specification.md) |
| **generator identity** | An attribute of a `generator` (which one); relevant only as a *withheld* field. | §1 + §8 |
| **faithfulness signature** | A recoverable correlate of `faithfulness` in the `output tuple`. | §17 + §19 + §27 |
| **held-out worlds** | An application of `split` (held-out generators / question types / datasets). | §24 |
| **recoverability** | The property that `recovery` succeeds; named by the `success criterion`. | §27 + §32 |
| **construction world / evaluation world** | The two sides of the one boundary term. | §8 |
| **the label rule / thresholds** | *How* provenance becomes a label value, and any numeric cutoffs. | [06](06_Label_Specification.md), [10](10_Evaluation_Protocol.md) |

---

## 36. Change control

This document is normative and inherited project-wide. A change to any entry requires an ADR
(`docs/conventions/decision-records.md`). A change to the meaning of `faithfulness` (§17) or `label`
(§21) additionally engages [Charter](00_Benchmark_Charter.md) §4 (v1-vs-v2 test) and §5 (extraordinary
justification). The definition **order** established here is fixed by the approved dependency graph; a
new term MUST be justified against the ontology (why it cannot be derived from existing terms) and
inserted at a position that preserves acyclicity before it is used.
