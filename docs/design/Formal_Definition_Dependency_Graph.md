---
Title: Formal Definition Dependency Graph
Status: Design analysis (input to docs/05_Formal_Definitions.md)
Last-reviewed: 2026-07-01
Related:
  - docs/00_Benchmark_Charter.md
  - VISION.md
  - docs/01_Benchmark_Design.md
  - docs/03_Problem_Definition.md
  - docs/05_Formal_Definitions.md
---

# Formal Definition Dependency Graph

*A dependency analysis for the benchmark's formal vocabulary. Its objective is to identify every
concept that will require a formal definition, determine what each depends on, and fix an order of
definition that avoids circular dependencies — so that [Formal Definitions](../05_Formal_Definitions.md)
can be written top-to-bottom with no forward semantic references.*

> **What this document does and does not do.** It is a **design analysis**, not a specification. It
> **does not define any term**, propose any wording, or pre-empt [Formal Definitions](../05_Formal_Definitions.md).
> For each candidate term it records only *why a definition is needed*, *what it depends on*, *what
> uses it*, *which layer it belongs to*, and *the risk of leaving it ambiguous*. The definitions
> themselves remain the sole responsibility of `docs/05`.

> **Sources.** Terms were extracted from the four approved documents named in the margin: the
> Charter, the Vision, the Benchmark Design, and the Problem Definition. No term is introduced here
> that those documents do not already use.

---

## 1. Method

**Extraction.** Every noun phrase carrying a load-bearing technical meaning in the four approved
documents was collected, then merged (synonyms unified) and split (terms used in two senses
separated — see the `grounding` / `grounding annotations` hazard in §6).

**Layer criteria.** Each term is assigned to one of the four layers the project uses. The layers are
a *classification by what a term depends on*, and (with one deliberate exception, §4) they also
suggest definition order:

| Layer | A term belongs here if it… | Depends at most on |
|---|---|---|
| **Foundational** | names a primitive object that exists before any benchmark process | external givens only |
| **Structural** | composes primitives into benchmark artifacts and their organization | Foundational (+ a named slot filled by Behavioral) |
| **Behavioral** | describes model behavior or the causal property under disturbance | Foundational, Behavioral |
| **Evaluation** | describes measuring a predictor against the frozen corpus | all lower layers |

**Dependency reading.** "A depends on B" means A's eventual definition cannot be stated without B
already being defined; equivalently, **B must be defined before A**. The graph in §2 is the transitive
closure of these edges; the order in §3 is a topological sort of it.

---

## 2. Candidate terms

Grouped by proposed layer. `Depends on` lists prerequisite *terms*; `Used by` lists later *terms* and
*owning specifications* (`06` = Label Specification, `07` = Label Generation Pipeline, `08` = Dataset
Specification, `09` = Baselines, `10` = Evaluation Protocol).

### 2.1 Foundational layer

| Term | Why a formal definition is needed | Depends on | Used by | Risk if left ambiguous |
|---|---|---|---|---|
| **Generator** | It is the *subject* every label is a fact about; the whole benchmark hinges on labels attaching to it. | — | output tuple, instance, intervention, counterfactual, faithfulness, `06`,`07`,`08` | Labels lose their referent; "faithful" becomes a property of text, not a model — the core error the benchmark exists to avoid. |
| **Image** (visual input) | It is what the intervention disturbs; the object on which image-dependence and evidence are defined. | — | intervention, image-dependence, evidence, grounding, output tuple | Confusion over what counts as "the image" (raw vs annotated) corrupts every downstream perturbation and agreement claim. |
| **Question** | Part of the source record and the output tuple; the task stem. | — | source record, output tuple, plausibility, `08` | Schema drift; unclear what the model was actually asked. |
| **Options** (answer choices) | The candidate set the answer is drawn from; the multiple-choice frame. | question | chosen answer, output tuple, `08` | The answer's meaning (a selection among these) becomes undefined. |
| **Chosen answer** | The generator's selection; the thing whose image-dependence is probed. | options, generator | image-dependence, evidence, output tuple, faithfulness, `06`,`07` | Cannot state "the answer depends on the image" if "the answer" is unfixed. |
| **Rationale** | The text under test; the object of plausibility and the thing faithfulness is *about*. | question, chosen answer | plausibility, grounding, faithfulness, output tuple, `06` | The benchmark's central object is unbounded; unclear what is being judged for faithfulness. |
| **Source record** | The raw, model-free unit; the origin of an instance. | image, question, options, grounding annotations | instance, output tuple, `08` | The pre-model unit blurs into the post-model tuple, muddying provenance and licensing. |
| **Predictor** | The agent the benchmark scores; defined by what it may and may not access. | — | success/failure criterion, baseline, recovery, `09`,`10` | The information boundary cannot be stated; "solving the benchmark" is undefined. |
| **Construction / evaluation boundary** | The one-way divide that the entire architecture rests on; separates privileged from restricted access. | generator, predictor | intervention, counterfactual, label, recovery, all Evaluation | Without a named boundary, "available vs withheld" is unenforceable and the task collapses. |

### 2.2 Structural layer

| Term | Why a formal definition is needed | Depends on | Used by | Risk if left ambiguous |
|---|---|---|---|---|
| **Grounding annotations** (regions) | The spatial data shipped *with* a source; distinct from behavioral `grounding` (name hazard, §6). | image, source record | output tuple, evidence(optional), `07`,`08` | Conflation with behavioral grounding; unclear whether a region is an input or a measurement. |
| **Output tuple** | The exact bundle a predictor may see; the benchmark's public unit. | question, options, chosen answer, rationale, grounding annotations | instance, recovery, plausibility, grounding, `09`,`10` | The information boundary cannot be drawn precisely; leakage risk. |
| **Instance** | The row of the corpus; the carrier that accretes provenance and a label. | output tuple, generator, **label slot**, interventional provenance, split | corpus, recovery, `06`,`08`,`10` | The unit of evaluation is undefined; construction-only fields may leak to evaluation. |
| **Interventional provenance** (incl. margins) | The recorded evidence a label is computed from; released for transparency, withheld as input. | intervention, counterfactual | label, hard core(possibly), `06`,`07` | Risk of being (mis)used as a predictor input — a direct label leak. |
| **Label** *(artifact)* | The frozen record of the verdict; the corpus's answer key. **Its rule is owned by `06`; only its term-anchor is in `05`.** | faithfulness *(meaning)*, instance | corpus, recovery, success/failure, `06`,`10` | The faithfulness↔label cycle (§5, C1) if the artifact and the property are not kept distinct. |
| **Routed-aside / ineligible set** | Instances where no meaningful label can hold; must be a named category, not silent deletion. | instance, faithfulness *(eligibility)* | corpus, `06`,`08` | Silent truncation; hidden bias in what the corpus contains. |
| **Split / held-out worlds** | The partition that turns the task into a generalization test. | instance, generator | transfer, recovery, `08`,`10` | "Generalization" is unmeasurable; train/eval contamination goes undetected. |
| **Corpus** (frozen benchmark corpus) | The deliverable and the boundary artifact. | instance, split | recovery, baseline, scorecard, `08`,`10` | The single thing that crosses the boundary is undefined; reproducibility claims lose their referent. |
| **Corpus manifest** | The provenance/integrity record underwriting reproducibility. | corpus | reproducibility guarantee, `08` | "Reproducible" becomes unverifiable. |

### 2.3 Behavioral layer

| Term | Why a formal definition is needed | Depends on | Used by | Risk if left ambiguous |
|---|---|---|---|---|
| **Intervention** *(concept)* | The only operation that yields a faithfulness verdict rather than a plausibility estimate; the engine of ground truth. **Concrete interventions owned by `07`.** | generator, image, boundary | counterfactual, image-dependence, evidence, faithfulness, `06`,`07` | Ground truth becomes a matter of inspection; the benchmark's legitimacy collapses. |
| **Counterfactual** | The behavior-under-disturbance that the label reads; the quantity withheld from predictors. | intervention, generator, chosen answer, rationale | image-dependence, evidence, faithfulness, recovery, `06`,`07` | The withheld quantity is undefined, so "recover it" is undefined. |
| **Image-dependence** | Whether the *answer* moves with the image; the precondition faithfulness is conditioned on. | counterfactual, chosen answer, image | evidence, faithfulness, `06` | Cannot separate an ungrounded answer from an inert rationale — the two failure modes blur. |
| **Evidence** (the visual content the answer depends on) | The referent of "faithful to the evidence"; the target region/content the rationale must track. | image-dependence, image, chosen answer | grounding, faithfulness, `06`,`07` | "Faithful to the evidence" has no object; grounding and faithfulness cannot be told apart. |
| **Grounding** *(behavioral)* | The rationale-vs-image agreement that the benchmark insists is **not** faithfulness; must be defined to be excluded. | rationale, image, evidence | faithfulness (by contrast/exclusion), baseline, `09` | The most common confusion (grounding = faithfulness) re-enters through the back door. |
| **Plausibility** | The observer-facing property the benchmark refuses as ground truth; defined independently, never as "not faithfulness." | rationale, question | faithfulness (divergence, as an *observation* not a dependency), hard core, `09`,`10` | Define-by-negation cycle with faithfulness (§5, C3); plausibility silently used as a proxy. |
| **Faithfulness** | The central construct; the property labels encode. Must carry its behavioral, necessary-condition scope explicitly. | counterfactual, image-dependence, evidence | label *(meaning)*, faithful/unfaithful, signature, recovery, `06`,`10` | Over-claiming (mechanistic reading) or under-specifying; the Charter's construct boundary is violated. |
| **Label meaning** (verdict content) | The bridge from the property to the artifact; what the frozen label *asserts*. | faithfulness | label *(artifact)*, `06` | The faithfulness↔label cycle (§5, C1). |

### 2.4 Evaluation layer

| Term | Why a formal definition is needed | Depends on | Used by | Risk if left ambiguous |
|---|---|---|---|---|
| **Recovery** (the predictor's task) | The precise ask: reproduce the withheld verdict from the output tuple alone. | output tuple, label, counterfactual, boundary | success/failure, baseline, `10` | The task itself is fuzzy; "solving" the benchmark is undefined. |
| **Baseline / reference solution** | A predictor built to calibrate difficulty; a peer of any external predictor. | predictor, recovery, corpus | floor, success/failure, `09`,`10` | The calibration points are undefined; "beyond trivial" has no anchor. |
| **Floor** (trivial baseline) | The threshold a genuine solution must clear to show it uses more than trivial signal. | baseline, output tuple | success/failure criterion, `09`,`10` | "Above trivial" is unmeasurable; grounding-only solutions look like successes. |
| **Hard core** | The subset where plausibility is high yet the label is unfaithful; the sharpest test. | plausibility, faithfulness, label | evaluation reporting, `08`,`10` | The benchmark's headline discriminative claim has no defined locus. |
| **Transfer / generalization** | Whether a signal learned on some worlds holds on held-out ones; the thing the splits measure. | split, recovery | success/failure, `10` | The Charter's "signatures may not generalize" refusal cannot be tested. |
| **Success criterion** | What counts as recovering the property. | recovery, floor, transfer | `10` | "Success" is rhetorical, not measurable. |
| **Failure criterion** | What counts as riding a correlate instead of the property. | recovery, floor, transfer, plausibility, grounding | `10` | Correlate-riding solutions are mistaken for genuine ones. |
| **Scorecard** | The evaluation-world artifact; the output of scoring. | corpus, recovery, success/failure | `10` | The reported result has no defined shape. |

---

## 3. Dependency graph

Arrows point **from prerequisite to dependent** (`A → B` = "A must be defined before B"). Grouped by
layer; only the load-bearing edges are drawn (transitive edges omitted for readability).

```
 FOUNDATIONAL
   generator ─┬─────────────► intervention ──► counterfactual ──► image-dependence ──► evidence
   image ─────┤                     ▲                                   │                 │
   question ──┤ boundary ───────────┘                                   ▼                 ▼
   options ──► chosen answer ───────────────────────────────────► (image-dependence)   grounding
   rationale ─────────────────────────────────────────────────────────────────────────► (grounding)
   predictor                                                                              │
                                                                                          ▼
 BEHAVIORAL (core)                          plausibility (independent) ┐                faithfulness
   intervention ─► counterfactual ─► image-dependence ─► evidence ─► grounding ─────────► faithfulness
                                                                     plausibility ┄┄(observation)┄┄► faithfulness
   faithfulness ─► label meaning
                                                                                          │
 STRUCTURAL                                                                                ▼
   {question,options,chosen answer,rationale,grounding annotations} ─► output tuple ─► instance
   grounding annotations ◄─ image, source record                              │           ▲
   source record ◄─ {image,question,options,grounding annotations}            │           │
   intervention,counterfactual ─► interventional provenance ──────────────────┼───────────┤
   label meaning ─► LABEL (artifact) ─────────────────────────────────────────┴───────────┤ (fills label slot)
   instance ─► split ─► corpus ─► corpus manifest                                          │
   faithfulness(eligibility) ─► routed-aside set                                           │
                                                                                           ▼
 EVALUATION
   output tuple, label, counterfactual, boundary ─► recovery
   recovery, corpus ─► baseline ─► floor
   plausibility, faithfulness, label ─► hard core
   split, recovery ─► transfer
   recovery, floor, transfer ─► success criterion / failure criterion ─► scorecard
```

The single most important structural feature of this graph: **`faithfulness` (Behavioral) points into
`label` (Structural), never the reverse.** Keeping that edge one-directional is what makes the whole
graph acyclic (§5, C1).

---

## 4. Recommended definition order

A topological sort of §3. The four layers remain the *classification*, but the safe *order*
deliberately places the Behavioral core property **before** the Structural label artifact — the one
place where dependency-correctness overrides the plain layer sequence (justified in §5, C1).

**Block A — Foundational primitives** (no internal dependencies; any internal order):
1. Generator
2. Image
3. Question
4. Options
5. Chosen answer
6. Rationale
7. Predictor
8. Construction / evaluation boundary
9. Source record  ·  10. Grounding annotations *(structural primitives that depend only on Foundational)*

**Block B — Behavioral chain** (define the property before any artifact that records it):
11. Intervention
12. Counterfactual
13. Image-dependence
14. Evidence
15. Grounding *(behavioral)*
16. Plausibility *(define independently; do not reference faithfulness)*
17. Faithfulness
18. Label meaning *(the verdict content — the bridge term)*

**Block C — Structural artifacts** (now safe: every property they record is already defined):
19. Output tuple
20. Interventional provenance
21. Label *(artifact — fills the slot with the Block-B meaning)*
22. Instance
23. Routed-aside / ineligible set
24. Split / held-out worlds
25. Corpus
26. Corpus manifest

**Block D — Evaluation terms** (depend on all lower blocks):
27. Recovery
28. Baseline / reference solution
29. Floor
30. Hard core
31. Transfer / generalization
32. Success criterion
33. Failure criterion
34. Scorecard

> **The one seam to watch.** `Instance` (22) references a `label` field, and `label` (21) is defined
> just before it — both *after* `faithfulness` (17). Defining the Behavioral property before both
> Structural terms removes every forward semantic reference. If `docs/05` instead followed a strict
> Foundational → Structural → Behavioral order, it would hit the C1 cycle; this interleaving is the
> deliberate fix, not an inconsistency.

---

## 5. Circular dependencies discovered, and how to eliminate them

Five potential cycles / hazards surfaced. Each is resolvable *before* writing `docs/05`, by the stated
move.

**C1 — `faithfulness` ⇄ `label` (the central cycle).**
*Cause:* the word "label" is used for two things — the *artifact* (a frozen field in the corpus) and
the *property* it asserts. If `label` is defined via `faithfulness` and `faithfulness` via "the label
the intervention assigns," the two are circular.
*Elimination:* split the senses. Define `faithfulness` as a Behavioral property with **no reference to
`label`**; introduce `label meaning` (the verdict content) atop faithfulness; define the `label`
*artifact* as the frozen record of that verdict. The dependency then runs one way
(`faithfulness → label meaning → label artifact`). Additionally, the **label rule** (how the
intervention's outcome becomes a value) is owned by `docs/06`, not `docs/05`; `docs/05` fixes only the
term. Order faithfulness (17) before label (21).

**C2 — `evidence` ⇄ `faithfulness` ⇄ `grounding` (the reference triangle).**
*Cause:* "faithful to the evidence" tempts a definition of `evidence` in terms of `faithfulness`, while
`grounding` and `faithfulness` are both about rationale-and-image.
*Elimination:* make the chain strictly linear —
`counterfactual → image-dependence → evidence → grounding → faithfulness`. `Evidence` is anchored on
`image-dependence` (a property of the *answer*), **not** on `faithfulness`; `grounding` is anchored on
`evidence` and the rationale, **not** on `faithfulness`. `Faithfulness` may then reference all three
without any back-edge.

**C3 — `plausibility` ⇄ `faithfulness` (define-by-negation).**
*Cause:* the documents contrast the two, inviting "plausibility = looks faithful but isn't," which makes
each depend on the other.
*Elimination:* define `plausibility` **independently** (a property of the rationale as read by an
observer; depends only on `rationale`/`question`). Their divergence is recorded in
[Problem Definition](../03_Problem_Definition.md) as an **observation**, not encoded as a definitional
dependency. Neither term's definition names the other.

**C4 — `instance` ⇄ `label` (container references content).**
*Cause:* `instance` contains a `label`; if Structural is defined before Behavioral, `instance` forward-
references an undefined property.
*Elimination:* the Block B-before-C ordering (§4) removes it — `label` and `faithfulness` are both
defined before `instance`. No structural container is defined before the property it carries.

**C5 — `intervention` ⇄ `counterfactual` (mutual-sounding pair).**
*Cause:* they are easy to define in terms of each other.
*Elimination:* `intervention` is the *operation* (a controlled change to the model's visual input) and
is defined first, depending only on Foundational terms; `counterfactual` is the *observed behavior under*
that operation and depends on it. One-directional.

**Naming hazard (not a cycle) — `grounding` vs `grounding annotations`.**
Two distinct concepts share a root word: the Structural *annotations* shipped with a source, and the
Behavioral *agreement* between rationale and image. This is not circular but will cause silent
conflation. *Resolution:* treat them as two separate catalog entries with visibly distinct names (they
are kept distinct throughout this document), and have `docs/05` disambiguate them at first use. Consider
a distinct surface term for one of them if confusion persists — a naming decision for `docs/05`, flagged
here, not made here.

After these five moves, the graph in §3 is a **directed acyclic graph**; the order in §4 is a valid
topological sort.

---

## 6. Terms that should NOT receive standalone definitions

These are derivable from other definitions or owned by a later specification; giving them independent
entries in `docs/05` would duplicate meaning (violating *one fact, one home*) or usurp another
document's ownership.

| Term | Why no standalone definition | Derive from / owner |
|---|---|---|
| **Faithful / unfaithful** | The two values of the faithfulness verdict. | `faithfulness` + `label meaning` |
| **Behavioral, necessary-condition** | Scope qualifiers of faithfulness, not separate concepts. | stated *inside* the `faithfulness` entry |
| **Margins** | A continuous facet of the interventional provenance. | `interventional provenance` |
| **Diagnostic provenance** | The subset of provenance that justifies a reason code. | `interventional provenance`; reason codes owned by `06` |
| **Reason codes (e.g. failure modes)** | The taxonomy of *why* an instance is unfaithful. | owned by [Label Specification](../06_Label_Specification.md), not `05` |
| **Generator identity** | An attribute of a `generator` (which one it is); relevant only as a *withheld* field. | `generator` + `construction/evaluation boundary` |
| **Faithfulness signature** | A recoverable correlate of `faithfulness` in the `output tuple`. | `faithfulness` + `output tuple` + `recovery` |
| **Held-out worlds** | An application of `split` (held-out generators / question types / datasets). | `split` |
| **Recoverability** | The property that `recovery` succeeds; named by the success criterion. | `recovery` + `success criterion` |
| **Construction world / evaluation world** | The two sides of the one boundary term. | `construction/evaluation boundary` |
| **The label rule / thresholds** | *How* provenance becomes a label value. | owned by `06` and `10`, never `05` |

> The guiding test applied above: a term earns a standalone definition only if it is (a) load-bearing,
> (b) not reconstructible from already-defined terms by a short, obvious composition, and (c) not owned
> by a downstream specification. Terms failing any of the three are listed here for the author of
> `docs/05` to reference rather than redefine.

---

## 7. Handoff to `docs/05_Formal_Definitions.md`

The author of Formal Definitions inherits, from this analysis, three fixed decisions and one open one:

**Fixed (resolve the cycles):**
1. Define along the order in §4 — Foundational, then the Behavioral core (through `faithfulness` and
   `label meaning`), then Structural artifacts (including the `label` artifact), then Evaluation.
2. Keep every edge into `label`, `evidence`, `grounding`, and `faithfulness` one-directional per §5;
   define `plausibility` without naming `faithfulness`.
3. Do not give standalone entries to the §6 terms; reference or defer them (to `06`/`10`) instead.

**Open (a naming decision, deliberately left to `05`):**
- Whether `grounding` (behavioral) and `grounding annotations` (structural) keep the shared root or one
  is renamed. This analysis only flags the hazard; the surface-term choice belongs to `docs/05`.

Everything above is a map of *what must be defined and in what order*. No meaning has been assigned; the
definitions remain to be written.
