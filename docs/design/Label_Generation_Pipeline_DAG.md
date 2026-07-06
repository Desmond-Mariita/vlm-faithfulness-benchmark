# Label Generation Pipeline DAG

> **Synchronization note (2026-07-01).** `docs/07_Label_Generation_Pipeline.md`, `08`, and `10` now
> exist and are authoritative; the "future/absent owner" language below predates them and is retained for
> historical context. Findings **G1 and G2 are RESOLVED** by the now-Accepted **ADR-002** and **ADR-003**
> (see §11); the production graph is acyclic and the incomplete-candidate lifecycle is adopted.

**Purpose:** dependency analysis preceding `docs/07_Label_Generation_Pipeline.md`  
**Scope:** construction artifacts through corpus freeze, plus the evaluation-side information-boundary interfaces  
**Method:** derive only transformations and dependencies required by the approved specifications; do not select algorithms, metrics, perturbations, or thresholds

## 1. Source specifications and authority

This graph is derived from:

- `docs/01_Benchmark_Design.md`
- `docs/03_Problem_Definition.md`
- `docs/05_Formal_Definitions.md`
- `docs/06_Label_Specification.md`
- `docs/06a_Benchmark_Data_Model.md`
- `docs/design/Label_Generation_Pipeline_Implementation_Inventory.md`

The specifications divide authority as follows.

| Specification | Authority used by this graph |
|---|---|
| `01` | Construction/evaluation separation, one-way lifecycle, artifact ownership principle, and information boundary. |
| `03` | Intervention is required during construction and forbidden during evaluation; the label is a generator property rather than a textual judgment. |
| `05` | Definitions and dependency order of generator, source record, output tuple, intervention, counterfactual, image-dependence, evidence, provenance, label, instance, routed-aside set, corpus, and manifest. |
| `06` | P1–P6 eligibility, Conditions A/B, S1–S3, label projection, D1 precedence, E1–E6 routing, and label invariants. |
| `06a` | Canonical first-class artifact forms, identities, lifecycle, traceability, mutability, and producing/consuming specifications. |
| Implementation Inventory | Whether the thesis repository already implements each transformation or only a precursor. It does not define dependencies. |

Specifications `07`, `08`, and `10` are referenced as owners by the approved documents but are not inputs to this derivation. Their named responsibilities are therefore represented as unimplemented contracts, not inferred procedures.

## 2. Dependency-normalization rule

The graph distinguishes three kinds of relationships:

1. **Production dependency:** an artifact must exist before a transformation can produce another artifact. These edges form the DAG.
2. **Containment/reference:** a later aggregate carries or references an earlier artifact. This is a production dependency only when the referenced artifact must already exist to construct the aggregate.
3. **Traceability back-reference:** a derived artifact points back to its evidence, or a final evidence trail points forward to the verdict it justified. A back-reference is not treated as an input to the earlier semantic determination.

This distinction is necessary because `06a` §3.7 says Interventional Provenance both determines eligibility/Conditions A and B/Behavioural State/Label and contains those resulting determinations. Treating both statements as production edges creates a cycle. The dependency-normalized graph treats provenance observations-to-determinations-to-state-to-label as the semantic production direction and the resulting P/E, A/B, state, and label entries in the final provenance trail as traceability back-references.

This normalization preserves the semantic order in `05`, `06`, and `06a` §4. It does not resolve how `07` will seal those back-references. The strict, literal artifact reading is assessed separately in §8.

## 3. Canonical artifact set

### 3.1 Root inputs

These are inputs to construction, not artifacts produced inside the label-generation graph.

| Root input | Authority | Role |
|---|---|---|
| External dataset record | `01` §12; normalization owned by `08` | Raw material from which a Source Record is normalized. |
| Generator and complete generator identity | `05` §1; generator set owned by `08`, execution owned by `07` | Produces the chosen answer/rationale and is later intervened upon. Its identity is withheld from predictors. |
| Governing specification versions | `06a` §§8–9 | Fix artifact meanings and must be recorded in provenance/manifest. |

### 3.2 Produced artifacts

| ID | Artifact | Canonical owner | Required downstream role |
|---|---|---|---|
| A1 | Source Record | `08` | Model-free normalized source for generation and traceability. |
| A2 | Output Tuple | `08` shape; produced by `07` | Exact predictor-visible image/question/options/chosen-answer/rationale bundle. |
| A3 | Candidate Subject | `06a` artifact form | Stable `(composite generator, source record)` instance before adjudication. |
| A4 | Intervention Record | `07` | Atomic observation of one intervention and its counterfactual result. |
| A5 | Interventional Provenance | `07` | Reconstructive evidence from which eligibility, Conditions A/B, and state are determined. |
| A6 | Behavioural State | `06` | One of S1/S2/S3 for an eligible subject. No state artifact is carried by an ineligible resolution. |
| A7 | Label | `06` | `faithful` or `unfaithful`, with D1/D2 coupling. |
| A8 | Routed-Aside Record | `06a` form; `06` eligibility semantics; `08` handling | Retained no-label resolution carrying E1–E6 justification. |
| A9 | Corpus Entry | `08` | Labelled resolution containing separable visible tuple, hidden key, and evidence trail. |
| A10 | Routed-Aside Set | `05` §23; handling by `08` | Collection of A8 records excluded from the labelled corpus. |
| A11 | Frozen Corpus | `08` | Static, split-organized collection of A9 entries crossing the boundary once. |
| A12 | Corpus Manifest | `08` | Public integrity, specification-version, source, generator, entry, and routed-set linkage. |

`06a` catalogs A1–A9 and A12 directly. A10 and A11 are explicit concepts in `05` and explicit lifecycle outputs in `01`/`06a`; they are included because routed records must be consumed and because the corpus is the artifact that crosses the construction/evaluation boundary.

## 4. Minimal production graph

```text
 External dataset record
          │
          │ T1 Normalize source
          ▼
   A1 Source Record ───────────────────────────────────────────────┐
          │                                                        │
          │ + Generator                                           │
          │ T2 Generate exact output                              │
          ▼                                                        │
   A2 Output Tuple                                                 │
          │                                                        │
          │ + A1 + complete Generator identity                     │
          │ T3 Bind candidate                                     │
          ▼                                                        │
   A3 Candidate Subject                                            │
          │                                                        │
          │ + live Generator                                       │
          │ T4 Observe interventions                               │
          ▼                                                        │
   A4 Intervention Record × N                                      │
          │                                                        │
          │ + A3                                                   │
          │ T5 Aggregate interventional provenance                 │
          ▼                                                        │
   A5 Interventional Provenance                                    │
          │                                                        │
          │ T6 Resolve eligibility and behavioural state           │
          ├──────────────── eligible ───────────────────────┐      │
          │                                                 ▼      │
          │                                      A6 Behavioural State
          │                                          S1 | S2 | S3 │
          │                                                 │      │
          │                                                 │ T7 Project label
          │                                                 ▼      │
          │                                           A7 Label     │
          │                                                        │
          └──────────────── ineligible ── T8 Retain route ──▶ A8 Routed-Aside Record
                                                                   │
 A1 + A2 + A3 + A5 + A6 + A7 ── T9 Assemble entry ──▶ A9 Corpus Entry
                                                                   │
 A8 ─────────────────────────── T10 Collect routes ──▶ A10 Routed-Aside Set
                                                                   │
 A9 × N + A10 + specification versions                            │
          │                                                        │
          │ T11 Organize, freeze, and manifest                     │
          ├────────────────────────▶ A11 Frozen Corpus ◀────────────┘
          └────────────────────────▶ A12 Corpus Manifest

 ═════════════════════ CONSTRUCTION / EVALUATION BOUNDARY ═════════════════════

 A11 Corpus Entry projection ──▶ predictors receive A2 only
 A11 hidden answer-key view ───▶ scoring receives A7
 A5/A4/Generator identity ─────▶ never predictor inputs
 A12 ──────────────────────────▶ public release/reproducibility consumer
```

The two T6 outcomes are mutually exclusive:

- eligible: exactly one A6 state, followed by exactly one A7 label;
- ineligible: one A8 record, with no A6 and no A7.

Condition B is not assessed when Condition A fails. Therefore S1 is produced without a Condition B result; S2/S3 require Condition A to hold and Condition B to be determined.

## 5. Transformation register

Implementation status uses the meanings in the Implementation Inventory: **Existing**, **Partial**, and **Missing**.

### T1 — Normalize source

**Input artifact**  
External dataset record

↓ **Transformation**  
Normalize a model-free multiple-choice visual record while preserving stable source identity and any source grounding annotations.

↓ **Output artifact**  
A1 Source Record

- **Owning specification:** `08`; named by `01` §§4, 12, `05` §9, and `06a` §3.1.
- **Implementation status:** **Partial.** The thesis repository's `datasets/vqa_dataset.py` loads processed VCR records and exposes most required source content. It silently drops missing records and pads/truncates malformed choice lists, so it is not a conformant source-normalization producer.
- **Hidden assumptions:** the originating dataset supplies stable record IDs; normalization does not alter semantic content; grounding annotations remain distinguishable from pixels; malformed records remain accountable.
- **Downstream dependencies:** T2, T3, T9, T11 traceability.

### T2 — Generate exact output

**Input artifacts**  
A1 Source Record + Generator

↓ **Transformation**  
Run the generator once to emit the exact chosen answer and exact rationale for the source record.

↓ **Output artifact**  
A2 Output Tuple

- **Owning specification:** execution owned by `07`; tuple shape owned by `08`; semantics fixed by `05` §19 and `06a` §3.2.
- **Implementation status:** **Partial.** Thesis Stage 1 generates answers and Stage 2 generates rationales, but they are separate checkpointed components. Gold-answer conditioning, regenerated probe rationales, loss of question IDs, and inconsistent rationale spans prevent a canonical exact tuple from being identified reliably.
- **Hidden assumptions:** a composite generator constitutes one subject; one exact baseline output is designated; the rationale corresponds to the generator's chosen answer rather than a substituted gold answer; generation failure can still be represented for E1.
- **Downstream dependencies:** T3, T9, predictor-visible projection after T11.

### T3 — Bind candidate subject

**Input artifacts**  
A1 Source Record + A2 Output Tuple + complete Generator identity

↓ **Transformation**  
Bind the tuple to the specific composite generator/source-record pair and assign the stable instance identity.

↓ **Output artifact**  
A3 Candidate Subject

- **Owning specification:** artifact form owned by `06a`; producer execution assigned to `07`; identity semantics from `06` I3 and `06a` §6.
- **Implementation status:** **Missing.** Thesis outputs do not serialize a complete composite generator identity or one stable identity carried across answer, rationale, and intervention artifacts.
- **Hidden assumptions:** every component/configuration needed to distinguish the generator is known; there is exactly one Output Tuple for the pair; an E1 case can enter this phase despite A2 being defined as complete.
- **Downstream dependencies:** T4, T5, T6, T8, T9.

### T4 — Observe interventions

**Input artifacts**  
A3 Candidate Subject + live Generator

↓ **Transformation**  
Apply construction-time interventions and controls, observe the generator's answer and/or rationale counterfactual behavior, and retain graded observations without assigning a verdict.

↓ **Output artifact**  
A4 Intervention Record, repeated as required for the candidate

- **Owning specification:** `07`; intervention/counterfactual meanings from `05` §§11–12; required record contents from `06a` §3.4.
- **Implementation status:** **Partial.** The thesis implements global answer regimes and real-versus-grey rationale regeneration. It lacks canonical Intervention Records, evidence localization, matched evidence interventions, Condition B observations, complete control outcomes, raw graded answer scores, and reliable per-instance identity.
- **Hidden assumptions:** interventions are valid for the individual record; the exact candidate tuple remains the baseline; a perturbed input is uniquely identifiable; controls license causal interpretation; evidence can be located when A holds; counterfactual answer/rationale readings use the same generator subject.
- **Downstream dependencies:** T5 and, through A5, all eligibility/state/label decisions.

### T5 — Aggregate interventional provenance

**Input artifacts**  
A3 Candidate Subject + complete applicable set of A4 Intervention Records + governing specification versions

↓ **Transformation**  
Assemble the reconstructive evidence trail for eligibility and behavioural determination.

↓ **Output artifact**  
A5 Interventional Provenance

- **Owning specification:** `07`; conceptual anchor `05` §20; contents and traceability required by `06` I8 and `06a` §§3.7, 8.
- **Implementation status:** **Missing.** Thesis run manifests and probe files provide fragments but no candidate-bound artifact containing exact baseline output, composite generator identity, interventions, localization, controls, P/E outcomes, Conditions A/B, and version linkage.
- **Hidden assumptions:** the applicable intervention set is complete; the observational part of provenance is sufficient to reconstruct the verdict; graded facets remain separable from predictor inputs; the final P/E, A/B, state, and label traceability references do not become circular production dependencies.
- **Downstream dependencies:** T6, T7, T8, T9, T11 integrity and auditability.

### T6 — Resolve eligibility and behavioural state

**Input artifacts**  
A3 Candidate Subject + A5 Interventional Provenance

↓ **Transformation**  
Apply P1–P6. For an eligible candidate, determine Condition A and, only when A holds, Condition B; map the outcomes to S1/S2/S3. For an ineligible candidate, produce no behavioural state and select the applicable E1–E6 route.

↓ **Output artifact**  
Eligible branch: A6 Behavioural State  
Ineligible branch: route outcome consumed immediately by T8; no A6

- **Owning specification:** state and eligibility semantics owned by `06`; operational execution owned by `07`; artifact form from `06a` §3.5.
- **Implementation status:** **Missing.** The thesis provides partial raw observations for Condition A but no determinate A/E4 distinction, no P5 evidence localization, no Condition B, no P6 decision, and no S1/S2/S3 generation.
- **Hidden assumptions:** P1–P6 are operationally decidable; A is distinguishable from indeterminate A; evidence identity is sufficient for B; controls are instance-valid; B is binary; the composite generator is a single label subject; correctness policy is settled.
- **Downstream dependencies:** A6 feeds T7 and T9; the ineligible outcome feeds T8. D1 precedence depends on B not being assessed on the S1 branch.

### T7 — Project behavioural state to label

**Input artifacts**  
A3 Candidate Subject + A5 Interventional Provenance + A6 Behavioural State

↓ **Transformation**  
Apply the total projection over eligible states: S1 → `unfaithful`/D1, S2 → `unfaithful`/D2, S3 → `faithful`/no reason.

↓ **Output artifact**  
A7 Label

- **Owning specification:** projection and label semantics owned by `06` §§5–7; execution assigned to `07`; artifact form in `06a` §3.6.
- **Implementation status:** **Missing.** No benchmark faithfulness label, reason-code projection, D1 precedence, or invariant validation exists in the thesis repository.
- **Hidden assumptions:** A6 is valid and immutable; exactly one state exists; label-specification version is bound; no correctness, plausibility, grounding, human judgment, or model judgment enters the projection.
- **Downstream dependencies:** T9, scoring after T11, and A5 traceability back-reference.

### T8 — Retain routed-aside resolution

**Input artifacts**  
A3 Candidate Subject + A5 Interventional Provenance + ineligible outcome from T6

↓ **Transformation**  
Retain the no-label resolution with its E1–E6 justification.

↓ **Output artifact**  
A8 Routed-Aside Record

- **Owning specification:** artifact form owned by `06a`; eligibility semantics by `06` §9; handling by `08`; production assigned to `07`.
- **Implementation status:** **Missing.** The thesis drops, normalizes, substitutes, or filters failures instead of producing routed records.
- **Hidden assumptions:** every failed candidate has a stable identity and sufficient provenance; exactly one retained resolution is produced; E4 never collapses into D1; routed aside is not a third label.
- **Downstream dependencies:** T10 and T11 manifest traceability.

### T9 — Assemble corpus entry

**Input artifacts**  
A1 Source Record + A2 Output Tuple + A3 Candidate Subject + A5 Interventional Provenance + A6 Behavioural State + A7 Label

↓ **Transformation**  
Create the labelled instance representation, assign its corpus role/split, and preserve separable predictor-visible, answer-key, provenance, source, and generator views.

↓ **Output artifact**  
A9 Corpus Entry

- **Owning specification:** `08`; named by `01` §§4–7 and defined conceptually by `06a` §3.9.
- **Implementation status:** **Missing.** No benchmark Corpus Entry or benchmark split assignment exists.
- **Hidden assumptions:** split assignment does not feed back into label construction; A2 remains byte/semantically unchanged; generator identity is retained for traceability but withheld from predictors; label and provenance remain separable from the predictor view.
- **Downstream dependencies:** T11, predictors and scoring after freeze.

### T10 — Collect routed-aside set

**Input artifact**  
A8 Routed-Aside Record × N

↓ **Transformation**  
Collect retained ineligible resolutions without admitting them to the labelled population.

↓ **Output artifact**  
A10 Routed-Aside Set

- **Owning specification:** handling owned by `08`; membership semantics from `05` §23 and `06` §9.
- **Implementation status:** **Missing.** No routed-aside collection exists.
- **Hidden assumptions:** all candidates are enumerable; no silent drop occurs; publication policy does not change membership.
- **Downstream dependencies:** T11 and A12.

### T11 — Organize, freeze, and manifest

**Input artifacts**  
A9 Corpus Entry × N + A10 Routed-Aside Set + source/generator/specification-version references

↓ **Transformation**  
Freeze the versioned labelled collection and seal its integrity/re-derivation record. No label or provenance value is changed by this transformation.

↓ **Output artifacts**  
A11 Frozen Corpus + A12 Corpus Manifest

- **Owning specification:** `08`; lifecycle and boundary constraints from `01` §§5–12, `05` §§25–26, `06` §§10–11, and `06a` §§3.10, 7–9.
- **Implementation status:** **Missing.** Thesis run directories have manifests, but there is no immutable benchmark corpus, entry manifest, routed-set reference, or correction-as-new-version mechanism.
- **Hidden assumptions:** all admitted entries are conformant; the manifest is complete; freeze is irreversible within the version; corrections create a new version; physical release views enforce the information boundary.
- **Downstream dependencies:** predictors consume only A2 projections; scoring consumes A7; transparency/audit consumers may inspect A5 subject to the no-predictor-input rule; reproducibility consumes A12.

## 6. Semantic sub-dependencies inside T4–T6

The approved specifications imply the following order but do not define the operational transformations. These are constraints within T4–T6, not additional first-class artifacts or algorithms.

```text
P1 well-formed subject ─┐
P2 non-abstention ──────┼─ failure ─▶ E1/E2/E3 ─▶ T8
P3 in-scope ────────────┘
             │ all hold
             ▼
answer intervention observations
             │
             ▼
P4 / Condition A determination
      │ indeterminate ───────────────▶ E4 ─▶ T8
      │ determinately false
      └──────────────────────────────▶ S1 ─▶ D1
      │ true
      ▼
P5 evidence localization
      │ failure ─────────────────────▶ E5 ─▶ T8
      ▼
matched evidence intervention observations
      │
      ▼
P6 causal-license controls
      │ failure ─────────────────────▶ E6 ─▶ T8
      ▼
Condition B determination
      │ false ───────────────────────▶ S2 ─▶ D2
      └ true ────────────────────────▶ S3 ─▶ faithful
```

This ordering establishes D1 precedence without defining a test, metric, threshold, localization method, intervention, or control.

## 7. Producer and consumer verification

### 7.1 Dependency-normalized producer table

| Artifact | Sole producer transformation | Consumers |
|---|---|---|
| A1 Source Record | T1 | T2, T3, T9, T11 traceability |
| A2 Output Tuple | T2 | T3, T9, predictors after T11 |
| A3 Candidate Subject | T3 | T4, T5, T6, T8, T9 |
| A4 Intervention Record | T4 | T5 |
| A5 Interventional Provenance | T5 | T6, T7, T8, T9, audit/release views |
| A6 Behavioural State | T6 eligible branch | T7, T9 |
| A7 Label | T7 | T9, scoring after T11 |
| A8 Routed-Aside Record | T8 | T10, T11 traceability |
| A9 Corpus Entry | T9 | T11, evaluation views |
| A10 Routed-Aside Set | T10 | T11, A12 reference |
| A11 Frozen Corpus | T11 | predictors, scoring, release |
| A12 Corpus Manifest | T11 | release, reproducibility, scoring-version lookup |

Under dependency normalization:

- **Exactly one producer:** pass for A1–A12.
- **At least one consumer:** pass for A1–A12. A11 and A12 are terminal construction artifacts with explicit external consumers.
- **Root-input exception:** external dataset records, generators, and governing specification versions are intentionally not produced inside this graph.

### 7.2 Resolution totality

For each A3 Candidate Subject, the graph requires exactly one terminal construction resolution:

```text
A3 -> A9 Corpus Entry
XOR
A3 -> A8 Routed-Aside Record -> A10 Routed-Aside Set
```

There is no path to both, and there is no permitted path to neither. This is the no-silent-drop requirement in `06a` T2 and `06` I7.

## 8. Acyclicity verification

### 8.1 Semantic production graph

The production edges in §4 admit the following topological ordering:

```text
Root inputs
  < A1
  < A2
  < A3
  < A4
  < A5
  < (A6 or A8)
  < A7
  < (A9 or A10)
  < (A11, A12)
  < evaluation consumers
```

No production edge points to an earlier element. **The dependency-normalized semantic graph is acyclic.**

### 8.2 Strict artifact-content reading

The strict reading of `06a` does **not** pass acyclicity without clarification:

```text
A5 Interventional Provenance -> P/E and A/B determinations -> A6 State -> A7 Label
              ^                                                        │
              └── A5 required to contain all resulting determinations ─┘
```

Relevant requirements are:

- `06a` §3.5: Behavioural State is derived from Interventional Provenance.
- `06a` §3.6: Label is projected from Behavioural State and binds to Interventional Provenance.
- `06a` §3.7: Interventional Provenance's required contents include P1–P6/E1–E6 results, Condition A/B determinations, Behavioural State, Label, and reason code.
- `06a` T1: a Label must be reconstructible from provenance alone, including the resulting state and label.

The cycle disappears only when those derived entries in sealed provenance are interpreted as traceability back-references rather than inputs to their own determination. That interpretation is consistent with the semantic order but is not stated explicitly by the approved artifact model. `07` must not introduce a second semantic producer for A5 while resolving this lifecycle detail.

## 9. Information-boundary verification

### 9.1 Permitted evaluation inputs

The sole predictor input is the A2 Output Tuple projection carried unchanged inside A9/A11:

- image;
- question;
- options;
- any source grounding annotations;
- exact chosen answer;
- exact rationale.

### 9.2 Forbidden predictor inputs

The following have no edge to a predictor:

- live Generator or generator identity;
- A3 Candidate Subject identity details that reveal the generator;
- A4 Intervention Records and counterfactual behavior;
- A5 Interventional Provenance or continuous margins;
- A6 Behavioural State;
- A7 Label/reason code;
- A8/A10 routed-aside information;
- held-out-world assignments unavailable to the applicable training view.

A7 is consumed only by scoring. A5 may be released for transparency or analysis but remains forbidden as a predictor input. Publication and predictor availability are distinct edges.

### 9.3 Verification result

**Pass at the specification-dependency level.** No required transformation bypasses the boundary, and the corpus is the only artifact that crosses it. Enforcement is not implemented: T9/T11 must preserve separable release views for the conceptual pass to hold in an actual corpus.

## 10. Specification-responsibility verification

### 10.1 Non-overlapping responsibility dimensions

| Responsibility | Sole authority in the approved allocation |
|---|---|
| Problem and construction/evaluation asymmetry | `03` |
| Architecture, lifecycle, and boundary | `01` |
| Concept meanings and dependency order | `05` |
| Eligibility, A/B meaning, S1–S3, label/reason projection, E1–E6 | `06` |
| Artifact forms, identity, mutability, traceability, version relationships | `06a` |
| Intervention execution, operational determinations, and provenance production | `07` |
| Source normalization, tuple/release shape, splits, assembly, corpus and manifest | `08` |
| Predictor evaluation and scoring | `10` |

Production and ownership are deliberately different: for example, `06` owns Label meaning while `07` executes the projection, and `08` owns Output Tuple shape while `07` runs the generator that fills it. This is not a responsibility overlap when the producing specification does not redefine the artifact.

### 10.2 Literal ownership exceptions in `06a`

The artifact-level “exactly one owner” statement is not literal for two rows in `06a` §2/§5:

- Candidate Subject is listed as owned by `06a` / `08`.
- Routed-Aside Record is listed as owned by `06a` / `06` / `08`.

`06a` resolves these by assigning different dimensions: form to `06a`, instance concept or handling to `08`, and eligibility semantics to `06`. Therefore **responsibility dimensions do not overlap**, but **artifact ownership labels are multi-spec**. The approved documents support a one-owner-per-dimension claim, not a strict one-spec-name-per-artifact claim.

## 11. Unresolved dependency points exposed by the graph

These are specification-level ambiguities in the derived graph, not proposed algorithms or architecture.

### G1 — Provenance has a semantic self-reference — **RESOLVED (ADR-002, Accepted)**

As detailed in §8.2, A5 is both the input to eligibility/A/B/state/label derivation and specified to contain all of those resulting determinations. The normalized DAG treats the latter as backlinks; the literal graph is cyclic. **Resolution:** ADR-002 (Accepted) formalizes the provenance lifecycle — observational provenance is the production input; the determinations recorded in *sealed* provenance are **traceability back-references, not production inputs** (ADR-002 N1). The production graph is therefore acyclic; there is one producer of provenance and sealing is not a second producer (N3). The dependency-normalized graph in §2/§8.1 is the authoritative reading.

### G2 — E1 precedes a well-formed Candidate Subject — **RESOLVED (ADR-003, Accepted)**

`06` previously defined E1 as “no complete output tuple” while `06a` required every A3 Candidate Subject to contain a complete A2 Output Tuple. **Resolution:** ADR-003 (Accepted) adopts **incomplete Candidate Subjects** — a Candidate Subject MAY carry an incomplete Output Tuple before eligibility, and P1 adjudicates completeness (E1 on failure). The base documents have been amended accordingly (05 §19, 06 P1/E1, 06a §3.2–3.3/3.8/R2). The single lifecycle is preserved: every Candidate Subject — including one with an incomplete tuple — resolves exactly once to a Corpus Entry or a Routed-Aside Record. No new artifact is introduced.

### G3 — “Behavioural State = none” is an outcome, not a carried artifact

`06a` §3.5 and its lifecycle diagram mention state `none` for an ineligible candidate, while §3.8 says a Routed-Aside Record carries no Behavioural State. The graph interprets `none` as T6's absence-of-state outcome and produces no A6 artifact. This is consistent with `06` §9, where ineligible is not a label or behavioural state.

### G4 — No labelled pre-assembly artifact is named

`01` describes “labelled instances (+ provenance)” before corpus assembly. `06a` moves directly from Candidate Subject plus derived artifacts to Corpus Entry, with no separate labelled-candidate artifact. The graph therefore feeds A2/A3/A5/A6/A7 directly into T9 and introduces no intermediate artifact.

### G5 — Corpus and routed-aside set sit outside the `06a` artifact table

`06a` §2 lists Corpus Entry and Routed-Aside Record but not Frozen Corpus or Routed-Aside Set as separate rows, although `05`, `01`, and the `06a` lifecycle require both. A10/A11 are included from those authoritative concepts so that A8/A9 have consumers and the boundary has a crossing artifact.

### G6 — Open semantic policies affect T6

`06` still records open questions concerning correctness eligibility, control-failure publication, Condition B granularity, and composite-generator validity. `06a` also records open questions about baseline-output identity and evidence-region identity. These alter T6 inputs/outcomes or T4/T5 traceability. The graph can place the dependencies, but it cannot resolve them.

## 12. Verification summary

| Required verification | Result | Basis |
|---|---|---|
| Graph is acyclic | **Pass for semantic production dependencies; fail under literal final-provenance containment.** | Topological order in §8.1; A5↔A6/A7 self-reference in §8.2. |
| Every artifact has exactly one producer | **Pass in the dependency-normalized graph.** | Producer table §7.1. Root inputs are external. The pass depends on treating provenance backlinks as references, not a second production step. |
| Every artifact has at least one consumer | **Pass.** | Consumer table §7.1; terminal construction artifacts have release/evaluation consumers. |
| No transformation bypasses the information boundary | **Pass conceptually.** | Only the A2 projection reaches predictors; A4–A7 and generator identity do not. Implementation enforcement is absent. |
| No specification responsibilities overlap | **Pass by responsibility dimension; not literal by artifact-owner label.** | Allocation in §10.1; Candidate Subject and Routed-Aside Record have multi-spec ownership labels partitioned by dimension. |

## 13. Canonical conclusion

The approved specifications imply one minimal forward semantic order:

```text
Source Record
  -> exact Output Tuple
  -> Candidate Subject
  -> Intervention Records
  -> Interventional Provenance
  -> eligibility resolution
       -> Behavioural State -> Label -> Corpus Entry
       OR
       -> Routed-Aside Record -> Routed-Aside Set
  -> Frozen Corpus + Corpus Manifest
  -> evaluation through separated visible and hidden views
```

No threshold, intervention method, localization method, metric, or serialization follows from this graph. Those remain outside this dependency analysis.

The graph is a valid DAG only under the semantic/reference distinction in §2. Before `07` can claim a literal artifact DAG, it must preserve that directionality without making the final provenance backlink a second producer, and it must account for the E1 no-output case using an artifact contract authorized by the specifications.
