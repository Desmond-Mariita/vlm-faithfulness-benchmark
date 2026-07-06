---
Title: Benchmark Design
Status: Accepted
Benchmark-Version: v1.0
Last-reviewed: 2026-07-01
Related:
  - docs/00_Benchmark_Charter.md
  - VISION.md
  - docs/03_Problem_Definition.md
  - docs/05_Formal_Definitions.md
  - docs/06_Label_Specification.md
  - docs/07_Label_Generation_Pipeline.md
  - docs/08_Dataset_Specification.md
  - docs/09_Baseline_Systems.md
  - docs/10_Evaluation_Protocol.md
---

# Benchmark Design

*This document is the technical blueprint of the benchmark. It answers one question — **how does
the benchmark work?** — at the level of architecture, not implementation. It is meant to be read
before any of the technical specifications, and to remain valid even if every dataset, model,
threshold, and line of code is later replaced. It is the canonical architectural blueprint that
all later specifications refine.*

> **What this document is not.** It is not the [Charter](00_Benchmark_Charter.md) (identity and
> boundaries), the [Vision](../VISION.md) (why we build it), or the
> [Problem Definition](03_Problem_Definition.md). It also does not
> *define* the benchmark's moving parts. It names the components and describes how they fit
> together; the definitions — datasets, interventions, thresholds, metrics, algorithms — are
> authored in the specification documents this blueprint frames.

---

## 1. The one idea the architecture is built around

Faithfulness, as this benchmark uses the word, is a **causal property of the model that produced a
rationale** — a fact about how that model behaves when its visual input is disturbed. It is not a
property of the text, and it cannot be read off the text by inspection. *(The word `faithfulness`
carries a precise technical meaning; that meaning is fixed authoritatively in
[Formal Definitions](05_Formal_Definitions.md), not here.)*

That single commitment forces the entire architecture, because it splits the project into two
worlds with deliberately **unequal access to the model**:

- A **construction world**, where the generating model is present and can be intervened upon. Here,
  and only here, the causal property can actually be measured.
- An **evaluation world**, where the generating model is gone. Here a predictor sees only what the
  model left behind — a static output — and must *recover* the property that was measured while the
  model was still in hand.

Everything below is a consequence of keeping those two worlds separated and of controlling exactly
what crosses the boundary between them.

```
        CONSTRUCTION WORLD                    ║          EVALUATION WORLD
   (the generating model is present)          ║     (the generating model is gone)
                                              ║
  raw records → generator → output tuple      ║      output tuple ──▶ predictor ──▶ guess
                     │                        ║                                       │
                     ▼                        ║                                       ▼
              causal intervention             ║                              compare to frozen
                     │                        ║                                    label
                     ▼                        ║                                       │
                 the LABEL  ──────────────────╫──────────▶  shipped in the corpus ────┘
                (a fact about the model)      ║          (the answer key, hidden at solve time)
                                              ║
        privileged access to the model        ║        no access to the model, ever
```

The vertical line is the benchmark. The label is manufactured on the left, where the model can be
probed, and consumed on the right, where it cannot. The predictor's job is to jump the line.

> **On terminology.** Words in this blueprint that carry a precise technical meaning — among them
> *faithfulness*, *grounding*, *evidence*, *counterfactual*, *instance*, *label*, *generator*,
> *source record*, and *output tuple* — are used here only in their **architectural** sense. Their
> authoritative definitions are fixed in [Formal Definitions](05_Formal_Definitions.md), and this
> document deliberately does not settle them. Where such a term is first introduced below, the
> pointer to `05` is repeated as a reminder.

---

## 2. The benchmark contract

*This is the one-page contract: the whole benchmark reduced to what it consumes, what it produces,
what a predictor is given, what it is denied, and what counts as winning or losing. Every other
section of this document elaborates one of these six lines.*

| Contract term | Statement |
|---|---|
| **Benchmark inputs** | Existing multiple-choice visual questions (adapted, not invented) and a set of **generators** — the models whose rationales are under study. Both are consumed only during construction. |
| **Benchmark outputs** | A single **frozen, pre-labelled corpus** of instances, plus a fixed procedure that scores any predictor against it. The corpus is the deliverable; a scorecard is what evaluation produces per predictor. |
| **Available to predictors** | The static **output tuple** of one instance — the visual question, its options, any grounding annotations, the generator's chosen answer, and its rationale — together with whatever external tools the predictor brings to bear on that tuple. |
| **Withheld from predictors** | The generating model, its identity, its **counterfactual** behavior under a disturbed image, the interventional provenance as a *prediction input*, and the held-out generators, question types, and datasets reserved for evaluation. |
| **Success criterion** | A predictor succeeds to the extent that it recovers the frozen **label** from the output tuple alone — on unseen instances and unseen worlds — beyond what trivial non-visual or grounding-only signals already afford. |
| **Failure criterion** | A predictor fails when its performance collapses to the trivial floor, or when it rides generator identity or rationale style instead of the causal property — that is, when it does not transfer across the held-out worlds. |

> The contract is stated at the level of *what*, never *how much*. It carries no thresholds and no
> metrics; the quantities that make "beyond trivial" and "collapses to the floor" measurable are
> fixed in the [Evaluation Protocol](10_Evaluation_Protocol.md), and the terms in **bold** are
> defined in [Formal Definitions](05_Formal_Definitions.md). The contract remains valid even if
> those quantities and definitions are later refined.

---

## 3. Construction versus evaluation

The benchmark is two activities that share a corpus but must never be confused.

| | **Benchmark construction** | **Benchmark evaluation** |
|---|---|---|
| Question | What is the true label of each instance? | How well does a predictor recover the label? |
| Access to the generating model | Full — the model is loaded and intervened upon | None — the model is frozen and out of reach |
| Runs | Once, offline, by the benchmark authors | Many times, by anyone, against the frozen corpus |
| Output | A static, pre-labelled corpus | A scorecard for a predictor |
| Trust model | Interventional and reproducible | Adversarial — predictors may try any signal |

Construction is where the causal work happens; evaluation is where the difficulty lives. A useful
mental rule: **anything a predictor could do at evaluation time to reconstruct the label by
re-running the intervention is out of bounds**, because it would collapse the two worlds back into
one. The whole point is that the intervention is expensive and unavailable, and the benchmark asks
whether its outcome can be predicted without it.

---

## 4. The major components

The six entries below are the benchmark's **processes** — the actors that do work. This blueprint
keeps a firm line between a **process** (named by what it *does*) and an **artifact** (named by what
it *represents* and who *owns* it): the durable objects these processes hand to one another are
catalogued in §6. Each process is described here only by its *responsibility* and its *interfaces*;
each has (or will have) its own specification document.

1. **Source records.** The raw material: multiple-choice visual questions that already carry a
   question, options, and (where available) grounding annotations. The benchmark does not invent
   these; it adapts existing datasets. *(What sources, and how they are normalized, is fixed in the
   [Dataset Specification](08_Dataset_Specification.md).)*

2. **Generators.** The models under study. Each generator, given a source record, produces a chosen
   answer and a rationale. Generators are the *subjects* of the benchmark — the label is a fact
   about them — and they exist in the construction world only. *(Which generators, and how they are
   prompted, is fixed in later specs; this blueprint treats a generator as any model that emits an
   answer-and-rationale for a source record.)*

3. **The intervention / labeling pipeline.** The heart of construction. It takes a generator and its
   output for a record, disturbs the visual input in controlled ways, observes how the generator's
   behavior changes, and turns those observations into a label. This is the only process with
   privileged access to a live model. *(The specific probes and the rule that turns their outcomes
   into a label are defined in the [Label Generation Pipeline](07_Label_Generation_Pipeline.md) and
   the [Label Specification](06_Label_Specification.md).)*

4. **The corpus assembler.** The bridge between the two worlds. It collects labelled instances,
   removes what does not belong, organizes them into splits, and freezes the result into a static,
   reproducible corpus with a manifest. After this step, the model is no longer needed by anyone.
   *(Composition and splits are fixed in the [Dataset Specification](08_Dataset_Specification.md).)*

5. **Baselines / reference solutions.** Predictors built by the benchmark authors to calibrate the
   task — from a deliberately weak floor that uses no visual information, up to a strong reference
   that uses everything a fair predictor is allowed. Their role is to show *how much of the task is
   genuinely hard* and where the easy signals run out. *(Defined as contracts in the
   [Baselines](09_Baseline_Systems.md) spec.)*

6. **The scoring harness.** The evaluation-world engine. It takes a predictor's guesses and the
   frozen labels and produces a scorecard. It never touches a generator. *(Metrics and reporting
   rules are fixed in the [Evaluation Protocol](10_Evaluation_Protocol.md).)*

Above all six sits the **specification layer** (`docs/`), which defines what each process must do.
The processes are executors of the specifications, never the source of the definitions (§10).

---

## 5. How the components interact

The data flow is a single forward pipeline through construction, a freeze, and then a repeatable
evaluation loop:

```
[Source records] ──▶ [Generators] ──▶ output tuples
                                          │
                                          ▼
                              [Intervention / labeling pipeline]
                                          │      (privileged: live model)
                                          ▼
                              labelled instances (+ provenance)
                                          │
                                          ▼
                                 [Corpus assembler] ──▶ ═══ FROZEN CORPUS ═══
                                                                 │
                        ┌────────────────────────────────────────┼───────────────┐
                        ▼                                         ▼               ▼
                 [Baselines] ──▶ guesses              [any predictor] ──▶ guesses
                        └───────────────┐                         ┌───────────────┘
                                        ▼                         ▼
                                        [Scoring harness] ──▶ scorecard
```

Two properties of this flow are load-bearing:

- **It is one-directional through construction.** A label, once produced, does not flow back to
  change a generator or a source record. Each stage refines the artifact and passes it on.
- **The freeze is a hard boundary.** Everything to the left of the frozen corpus happens once and
  requires the model. Everything to the right happens many times and must not require the model. The
  baselines and any external predictor are peers on the right of the boundary — the authors' own
  reference solutions get no privileged access the public does not have.

---

## 6. Artifacts of the benchmark

*A process does work; an **artifact** is the durable object that work produces and passes on. The
benchmark's information lives in its artifacts, and every artifact has exactly one owning
specification — this is the ownership model the later specifications inherit. The table below
catalogues the major artifacts produced during construction: what each represents, which
specification will own its definition, and whether it crosses the construction/evaluation boundary
(i.e. whether it exists in the evaluation world at all). Terms are used in their architectural sense
only; their authoritative definitions belong to [Formal Definitions](05_Formal_Definitions.md).*

| Artifact | What it represents | Owning specification | Crosses the boundary? |
|---|---|---|---|
| **Source record** | A normalized multiple-choice visual question with its options and any grounding annotations; raw material carrying no model. | [Dataset Specification](08_Dataset_Specification.md) | Partly — its public fields reappear inside the output tuple; its construction bookkeeping does not. |
| **Output tuple** | One generator's answer-and-rationale attached to a source record; the instance before it is labelled. | [Dataset Specification](08_Dataset_Specification.md) (shape / schema) | Yes — minus the generator's identity, it is exactly what a predictor sees. |
| **Interventional provenance** | The record of how a generator behaved under a disturbed image; the evidence from which a label is computed. | [Label Generation Pipeline](07_Label_Generation_Pipeline.md) | Released for transparency, but **withheld as a prediction input** — it is the answer key's working, not a feature. |
| **Label (+ diagnostic provenance)** | The verdict about the generator for this instance, with the trail that justifies it. | [Label Specification](06_Label_Specification.md) (rule); provenance from `07` | Yes, as the **hidden answer key** — invisible during prediction, revealed only to the scoring process. |
| **Routed-aside set** | Instances for which a meaningful label cannot hold (ambiguous, or preconditions unmet); set aside, not discarded silently. | [Dataset Specification](08_Dataset_Specification.md) | No — excluded from the corpus by construction; may be published separately for transparency. |
| **Frozen benchmark corpus** | The static, versioned collection of labelled instances organized into splits; the deliverable. | [Dataset Specification](08_Dataset_Specification.md) | It **is** the boundary — the single artifact that carries the benchmark from construction into evaluation. |
| **Corpus manifest** | The provenance and integrity record that makes a release reproducible and citable. | [Dataset Specification](08_Dataset_Specification.md) + the versioning convention | Yes — public, and the basis of the reproducibility guarantee. |

*(The **scorecard** is the benchmark's other artifact, but it is produced in the evaluation world,
not during construction, and is owned by the [Evaluation Protocol](10_Evaluation_Protocol.md).)*

The rule of thumb the ownership model enforces: **one artifact, one owning specification.** No later
document should define an artifact another already owns; it should reference it. This is what keeps
the specifications from quietly forking a definition.

---

## 7. The lifecycle of an instance

An *instance* is one row of the eventual benchmark. *(The term is defined authoritatively in
[Formal Definitions](05_Formal_Definitions.md).)* It accretes information as it moves through
construction and then sheds most of it at the boundary.

1. **Born as a source record.** A multiple-choice visual question with its options and any grounding
   annotations. It carries no model, no answer choice, no rationale, no label.
2. **Paired with a generator.** A generator answers the question and writes a rationale. The record
   is now an *output tuple*: the visual question plus one model's answer-and-rationale. The same
   source record can father many instances, one per generator.
3. **Interrogated by the labeling pipeline.** The instance's generator is intervened upon; the
   instance gains provenance describing how the generator behaved under disturbance.
4. **Adjudicated.** From that provenance, the instance receives a **label** and, where applicable,
   diagnostic provenance explaining *why* it earned that label. Some instances are found not to
   belong (they are ambiguous, or the preconditions for a meaningful label do not hold) and are
   routed aside rather than labelled.
5. **Placed.** The corpus assembler assigns the instance to a role — training material, or one of
   the held-out evaluation splits — and records it in the manifest.
6. **Frozen and stripped.** At the boundary, the instance is reduced to what a predictor is allowed
   to see plus its now-hidden answer key. It never changes again; a correction is a new corpus
   version, not an edit.

> The instance is richest in the construction world and deliberately impoverished in the evaluation
> world. Its journey is the story of information being *earned* through intervention and then
> *withheld* at the boundary — an asymmetry §9 states as a first-class property.

---

## 8. The lifecycle of a label

The label is the benchmark's product, and its lifecycle is what gives the benchmark its integrity.

1. **Undefined at birth.** A source record has no label; a label is meaningless without a generator,
   because it is a statement *about a generator*.
2. **Measured, not judged.** The label is derived from how the generator behaves under intervention
   — an observation about the model, not an opinion about the rationale's wording. No reader, human
   or machine, assigns it by inspecting the text. *(This "no judge in the label path" boundary is a
   [Charter](00_Benchmark_Charter.md) invariant; the exact derivation rule lives in the
   [Label Specification](06_Label_Specification.md).)*
3. **Provenanced.** Every label ships with the trail of observations that produced it, so that any
   later reader can see *why* the instance is labelled as it is. The label is self-justifying by
   construction.
4. **Frozen.** Once the corpus is assembled, the label is fixed. It becomes the hidden answer key
   for evaluation.
5. **Withheld, then revealed only for scoring.** During prediction the label is invisible; the
   scoring harness is the only party that compares a guess against it.
6. **Immutable across the corpus version.** A label is never quietly corrected. If construction is
   found to be wrong, the fix is a re-labelled, re-versioned corpus with its own manifest — so that
   comparisons across published corpora always mean the same thing.

The single most important fact about the label: **it is defined by a specification, computed by an
intervention, and frozen in a corpus** — three different documents/artifacts, three different
moments, one meaning.

---

## 9. The irreversibility of construction

Benchmark construction is **intentionally irreversible**, and this is a design commitment, not an
accident of engineering. Each stage on the construction side does not merely add information — it
also *discards* privileged information on purpose, and none of it can be recovered from what the
stage passes on:

- Generation keeps the emitted answer and rationale and lets go of everything else the model
  computed to produce them.
- Intervention observes the generator's counterfactual behavior and records only its distilled
  provenance; the live behavior itself is not retained.
- The freeze releases the generating model entirely, drops the generator's identity from the
  predictor's view, and reduces each instance to its output tuple plus a hidden label.

The frozen corpus is therefore a **one-way, lossy transformation of the construction world**: given
only the corpus, one cannot reconstruct the generator, re-run its counterfactual, or otherwise walk
back across the boundary. This is not a limitation to be engineered away — it is the mechanism that
makes the task both hard and honest. If construction were reversible, a predictor could invert it
and read the label off the model; because it is not, the predictor must genuinely recover the causal
property from what little the boundary lets through.

Irreversibility is thus part of the benchmark's philosophy, not merely its plumbing: **information is
earned through intervention and then deliberately destroyed at the boundary, and the boundary only
ever runs one way.**

---

## 10. The separation of specifications and implementation

The architecture treats *definitions* and *code* as different kinds of thing, in different places,
with different authority.

- A **specification** states what a process must produce — for example, what makes an instance
  labelled one way rather than another — as a published function of published inputs. Specifications
  live in `docs/` and are the authoritative source of truth.
- An **implementation** is a faithful executor of a specification. It may be rewritten, optimized,
  ported, or replaced at any time. It is never the source of a definition.

Two rules make this real:

1. **The specification wins.** If an implementation and its governing specification disagree, the
   implementation is defective — not the specification.
2. **Reproducibility is a property of the corpus, not the code.** Because the corpus is static and
   ships with a manifest of its inputs, a released number is reproducible by re-checking the frozen
   artifact, and *re-derivable* — not necessarily bit-identical — on a pinned environment. The
   benchmark's guarantee is the frozen artifact plus its provenance, not a promise that any two runs
   of the code produce identical bytes.

The practical consequence for a reader: you can understand and trust this benchmark entirely from
its specifications and its manifest, without reading a line of implementation. That is the intended
state.

---

## 11. What predictors may see, and what is hidden from them

The benchmark's difficulty is set almost entirely by the **information boundary** — the line between
what crosses into the evaluation world and what does not. *(The terms `grounding`, `evidence`, and
`counterfactual` used below are defined authoritatively in
[Formal Definitions](05_Formal_Definitions.md).)*

**Available to a predictor** (the static output tuple):

- the visual question, its options, and any grounding annotations that shipped with the source;
- the generator's chosen answer;
- the generator's rationale.

A predictor is free to bring its own external tools to bear on this tuple — its own vision models,
detectors, or reasoning — because none of that recovers the one thing that is missing.

**Hidden from a predictor** (everything that would trivialize the task):

- **The generating model itself.** It is frozen and out of reach. A predictor cannot query it,
  cannot re-run it, and cannot disturb its input and observe the result — doing so would simply
  re-run the intervention and read the label off the model.
- **The generator's identity.** A predictor is not told *which* model produced the tuple, so it
  cannot succeed by memorizing a particular model's style.
- **The generator's counterfactual behavior.** How the model would have answered or reasoned under a
  disturbed image — the very thing the label is computed from — is exactly what the static output
  does not contain.
- **The interventional provenance as an input.** The observations and margins that define the label
  may ship *with the corpus* for transparency and analysis, but they are the answer key. Using them
  as prediction inputs is out of bounds; they are released to be audited, not to be consumed by a
  solver.
- **Held-out worlds during training.** Certain generators, question types, or whole datasets are
  reserved so that generalization — not familiarity — is what evaluation measures.

> The boundary is the benchmark's entire source of difficulty. What the predictor is given is
> *grounding* — how well the rationale and image agree. What it must produce is a statement about
> the model's *counterfactual*, which the tuple withholds by design. The gap between the two is the
> problem the benchmark poses.

---

## 12. The end-to-end benchmark lifecycle

Assembling the pieces, the benchmark's life runs in one direction, from raw data to a scorecard,
crossing the boundary exactly once:

```
  raw dataset
      │   normalize into source records
      ▼
  source records
      │   each generator answers + rationalizes
      ▼
  output tuples  ─────────────  [ CONSTRUCTION WORLD — model present ]
      │   intervene on the generator; observe counterfactual behavior
      ▼
  interventional provenance
      │   apply the label rule (specification)
      ▼
  labelled instances (+ provenance, some routed aside)
      │   dedup · organize · split · freeze · manifest
      ▼
  ═══════════════ FROZEN BENCHMARK CORPUS ═══════════════   ← the boundary (irreversible, §9)
      │
      ├─▶ baselines (author reference solutions) ─┐
      │                                           │   [ EVALUATION WORLD — model gone ]
      └─▶ any predictor ──────────────────────────┤
                                                  ▼
                                        scoring harness
                                                  │   compare guesses to hidden labels
                                                  ▼
                                             scorecard
```

Reading it as a sentence: **a raw dataset becomes source records; generators turn those into output
tuples; an intervention pipeline turns each tuple, plus its generator's counterfactual behavior,
into a labelled instance; the corpus assembler freezes the labelled instances into a static corpus;
baselines and predictors then guess the labels from the output alone; and a scoring harness reports
how close they came.** The model is required for exactly the first half and forbidden for exactly
the second.

---

## 13. Invariants this blueprint commits to

These hold regardless of how any process is implemented. Later specifications may refine *how* they
are achieved, but not *whether*:

1. **The label is a property of the generating model,** fixed at construction time.
2. **The label is defined by specification, computed by intervention, and frozen in the corpus** —
   never assigned by inspecting the rationale.
3. **Construction has privileged access to the model; evaluation has none.** The boundary between
   them is crossed once, in one direction.
4. **Predictors never touch the generator, its identity, its counterfactual, or the interventional
   provenance as an input.**
5. **The corpus is static and reproducible from its manifest;** corrections are new versions, not
   edits.
6. **The authors' baselines are peers of any external predictor** on the evaluation side — they earn
   no access the public lacks.
7. **Construction is irreversible.** The frozen corpus is a one-way, lossy transformation of the
   construction world; the generator and its counterfactual cannot be reconstructed from it (§9).
8. **One artifact, one owning specification.** No later document redefines an artifact another owns;
   it references it (§6).

---

## 14. What this blueprint deliberately leaves open

By design, this document names processes, artifacts, and flows but defines none of their internals.
The following belong to the specifications it frames, and are intentionally absent here:

- which **datasets** become source records, and how they are normalized → [Dataset Specification](08_Dataset_Specification.md);
- which **generators** are studied → later specs;
- the **interventions** and the **rule** that turns their outcomes into a label →
  [Label Generation Pipeline](07_Label_Generation_Pipeline.md), [Label Specification](06_Label_Specification.md);
- the exact **terms** used throughout (faithfulness, grounding, evidence, counterfactual, and the
  rest), defined once → [Formal Definitions](05_Formal_Definitions.md);
- the **thresholds**, **metrics**, and **reporting rules** → [Evaluation Protocol](10_Evaluation_Protocol.md);
- the **baseline contracts** → [Baselines](09_Baseline_Systems.md).

A reader who has finished this document should understand *how the benchmark works as a system* — the
two worlds, the boundary, the contract, the artifacts and who owns them, the lifecycle of an instance
and of a label, the irreversibility of construction, and the flow from raw data to scorecard — and
should be ready to read the specifications, each of which fills in one part of the blueprint without
changing its shape.
