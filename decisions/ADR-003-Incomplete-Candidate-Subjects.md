---
Status: Accepted
Date: 2026-07-01
Supersedes: —
Superseded-by: —
Charter-clause: — (v1 amendment; no change to label meaning — see §8)
Related:
  - docs/05_Formal_Definitions.md
  - docs/06_Label_Specification.md
  - docs/06a_Benchmark_Data_Model.md
  - docs/07_Label_Generation_Pipeline.md
  - docs/design/Label_Generation_Pipeline_DAG.md
  - design/ADR-003_E1_Design_Alternatives.md
  - decisions/ADR-002-Construction-Provenance-Lifecycle.md
  - reviews/gemini/pipeline_dag_review.md
---

# ADR-003: Incomplete Candidate Subjects

> **This ADR resolves the E1 ontology inconsistency** (DAG finding G2) by adopting **Alternative B** from
> the exploration paper: a Candidate Subject MAY carry an **incomplete Output Tuple** before eligibility
> evaluation. It authorizes and requires the amendments in §5. It changes no label meaning (§8).

## 1. Context

The approved lifecycle implies `Output Tuple → Candidate Subject → Eligibility → E1`, but **E1 is the
absence of a complete Output Tuple**:

- Label Specification §3 P1 requires *"a complete output tuple exists"*; E1 (§8/§9) is *"malformed or
  absent output: no complete output tuple."*
- Benchmark Data Model §3.3 requires every Candidate Subject to **contain** an Output Tuple, and §3.2
  defines the Output Tuple to contain the exact chosen answer and exact rationale.
- Data Model §3.8 defines the Routed-Aside Record as *"the ineligible resolution of a Candidate
  Subject."*

This is a genuine ontological contradiction, independently confirmed by the pipeline DAG (§11, G2) and
the Gemini review (*"a profound, genuine ontological inconsistency … a logical contradiction in the core
data schema … it must relax the schema of Candidate Subject to allow optional/nullable outputs"*): to
record an E1 outcome, an item must be a Candidate Subject; to be a Candidate Subject it must have a
complete Output Tuple; but E1 is exactly the case where it does not. A concrete motivating case is a
**composite generator** that produces a chosen answer but fails to produce a rationale — a *partial*
tuple the current ontology cannot represent (exploration §3; Inventory §3.2).

The design alternatives were catalogued in `design/ADR-003_E1_Design_Alternatives.md`. This ADR records
the decision.

## 2. Alternatives considered (briefly)

From the exploration paper:

- **A — Generation Attempt artifact.** A new pre-tuple artifact carries failed generations; the
  Candidate Subject stays strictly complete. *Cleanest separation, but introduces a new concept
  (Formal Definitions §36) and adds a pre-phase to the Instance lifecycle.*
- **B — Incomplete Candidate Subjects (adopted).** Relax the Candidate Subject so it MAY hold an
  incomplete Output Tuple; eligibility P1 adjudicates completeness. *No new artifact; uniform lifecycle;
  relaxes one artifact-level invariant.*
- **C — Route before Candidate Subject creation.** Keep the completeness invariant but emit E1 without
  forming a candidate. *Preserves the invariant but breaks "routed-aside = a phase of an Instance" for
  E1 and/or bifurcates the eligibility gate.*
- **D — Redraw the E1/E2 boundary.** Treat a structural tuple as always present, folding absence into
  E2. *Smallest footprint but the largest semantic change to approved E-route meanings.*

Alternative B is adopted. The Gemini review names exactly two viable resolutions — a new primitive (A)
or relaxing the schema (B); B is chosen because it resolves G2 **without** fragmenting the ontology
(§8 justification).

## 3. Decision

The benchmark adopts **Alternative B: allow incomplete Candidate Subjects.**

- Every `(generator, source record)` pair still becomes **exactly one** Candidate Subject.
- Every Candidate Subject still resolves **exactly once**, to a Corpus Entry **or** a Routed-Aside
  Record. The single lifecycle is unchanged:

  ```
                 Candidate Subject
                        │
            ┌───────────┴───────────┐
            ▼                       ▼
       Corpus Entry          Routed-Aside Record
  ```

- **The only semantic change:** a Candidate Subject MAY carry an **incomplete Output Tuple** before
  eligibility evaluation — the chosen answer and/or rationale MAY be absent.
- **Eligibility P1** becomes responsible for determining whether the Output Tuple is **sufficiently
  complete for further benchmark processing.** A Candidate Subject whose Output Tuple fails P1's
  completeness determination resolves to an **E1** Routed-Aside Record.
- **Completeness is still guaranteed where it matters:** an incomplete Output Tuple MUST NOT cross the
  construction/evaluation boundary. Any Output Tuple inside a Corpus Entry — the only tuple a predictor
  ever sees — is complete by construction (guaranteed by P1 having passed).

This introduces **no new artifact** and **no new benchmark concept** (Formal Definitions §36 is not
engaged): "incomplete Output Tuple" is a pre-eligibility *state* of the existing Output Tuple, not a new
artifact.

## 4. Consequences

**Positive.**
- G2 is resolved without adding an artifact or an ontological primitive.
- The uniform lifecycle is preserved exactly: one Candidate Subject per pair, one resolution each, and
  every Routed-Aside Record — including E1 — remains a phase of a real Instance (Data Model §1).
- No-silent-drop (Label Spec I7; Data Model T2) becomes *structurally* satisfiable for E1: a failed
  generation is a Candidate Subject that routes to E1, not a dropped record.
- The composite partial-tuple case is directly representable as an incomplete Candidate Subject.
- No change to the released corpus, the information boundary, or predictors: incomplete tuples never
  ship, so downstream consumers are unaffected.

**Negative / accepted costs.**
- The Candidate Subject / Output Tuple **completeness invariant is relaxed** (§8): code and readers MUST
  NOT assume a Candidate Subject's Output Tuple is complete *before* the P1 gate.
- Eligibility P1 carries an explicit new responsibility (the completeness determination), which the
  Label Generation Pipeline (`07`) must specify operationally.
- Provenance for an E1 case contains **no** Intervention Records (you cannot intervene on an output that
  never formed); its justifying evidence is the generation/completeness outcome. This must be stated so
  I8/T2 still hold (consistent with ADR-002: observational provenance may be empty of interventions).

**Relationship to ADR-002.** Orthogonal and compatible. ADR-002 fixed the provenance production vs.
traceability distinction (G1); this ADR fixes the E1 lifecycle (G2). The production graph's shape and
acyclicity are unchanged.

## 5. Required amendments

The following amendments are **authorized and required** by this ADR. They are compatible extensions
(MINOR; §8), to be executed as spec revisions that cite this ADR.

### 5.1 Formal Definitions (`docs/05_Formal_Definitions.md`)
- **§19 Output Tuple.** Add that an Output Tuple is **guaranteed complete only on the predictor-visible
  side** (inside a Corpus Entry). Prior to eligibility, a Candidate Subject's Output Tuple MAY be
  **incomplete** (the chosen answer and/or rationale absent). An incomplete Output Tuple MUST NOT cross
  the construction/evaluation boundary. Note that "incomplete" is a state of the existing artifact, not a
  new term (§36 not engaged).

### 5.2 Benchmark Data Model (`docs/06a_Benchmark_Data_Model.md`)
- **§3.2 Output Tuple — Required contents.** Change "the exact chosen answer as emitted" and "the exact
  rationale as emitted" from unconditional to: present-and-exact for a **complete** tuple; for a
  Candidate Subject's tuple prior to eligibility, the chosen answer and/or rationale MAY be absent. Add:
  an incomplete Output Tuple MUST NOT appear in a Corpus Entry.
- **§3.3 Candidate Subject — Required contents.** Relax "the Output Tuple" to "an Output Tuple, which
  MAY be incomplete prior to eligibility." Add a note: completeness is determined by eligibility P1; an
  incomplete Candidate Subject failing P1 resolves to an E1 Routed-Aside Record.
- **§3.8 Routed-Aside Record.** No change to producer or phase model. Clarify that for an **E1**
  resolution the justifying Interventional Provenance contains the generation/completeness outcome and
  **no** Intervention Records.
- **§6 R2.** Clarify "exactly one Output Tuple per instance (possibly incomplete)."
- **§4 lifecycle diagram / §8 T2.** Note that P1's completeness determination is the first eligibility
  gate; an incomplete tuple routes to E1 with retained identity and evidence.

### 5.3 Label Specification (`docs/06_Label_Specification.md`)
- **§3 P1 (Well-formed subject).** Reframe P1 as the gate that **determines whether the Candidate
  Subject's Output Tuple is sufficiently complete for further benchmark processing** (a complete chosen
  answer and a genuine rationale are present). P1 now adjudicates a possibly-incomplete tuple rather than
  presupposing a complete one.
- **§8/§9 E1.** Clarify that E1 is the outcome when P1's completeness determination fails; E1 remains a
  Routed-Aside outcome with no behavioural state. E1's *meaning* ("no complete output tuple") is
  unchanged — it is now merely *representable* as a resolved Candidate Subject.
- **§5/§6/§7 (states, taxonomy, failure modes).** No change: E1 candidates never receive a behavioural
  state or a label value.

### 5.4 Label Generation Pipeline DAG (`docs/design/Label_Generation_Pipeline_DAG.md`)
- **§5 T2 (Generate exact output).** Note that generation MAY yield an incomplete Output Tuple; update
  the hidden assumption that a canonical *complete* tuple always results.
- **§5 T3 (Bind candidate).** Remove the requirement that A2 be complete to bind A3; a Candidate Subject
  MAY hold an incomplete tuple.
- **§6 / §5 T6.** P1's completeness determination is the first eligibility check; an incomplete tuple
  routes to E1 → T8.
- **§11 G2.** Mark **resolved by ADR-003.** §7.2 resolution totality and §8.1 acyclicity are unaffected
  (every Candidate Subject still resolves exactly once; the production graph shape is unchanged).

## 6. Migration impact

- **Generation stage (`07`, implementation).** Failed or partial generations MUST be **retained as
  incomplete Candidate Subjects**, not dropped, normalized, padded, or converted to empty strings
  (Inventory §9; assumptions 10 and 14). The existing kept-ID/drop-count behaviour becomes explicit E1
  Routed-Aside Records.
- **Composite generators.** "Answer present, rationale absent" is now an incomplete Candidate Subject
  routed to E1 (subject to Label Spec Q4 on composite-generator validity); it is no longer an
  unrepresentable case.
- **Downstream code.** Any consumer of a Candidate Subject MUST NOT assume tuple completeness before P1.
  After P1 passes, and for every Corpus Entry, completeness is guaranteed.
- **Consumers / predictors.** No migration: the released corpus and the predictor-visible guarantee are
  unchanged (incomplete tuples never ship).
- **Legacy mapping.** Unaffected; the `label` collision and other mappings in
  `docs/04_Legacy_Terminology_Mapping.md` are untouched.

## 7. Benchmark invariants preserved

- **Single, uniform lifecycle:** Candidate Subject → Corpus Entry XOR Routed-Aside Record (Data Model
  §1) — unchanged.
- **One Candidate Subject per `(generator, source record)` pair; exactly one resolution each** (Data
  Model R1/R2; DAG §7.2).
- **Routed-Aside Record remains a phase of a real Instance** — including E1 (the key advantage over
  Alternatives A and C).
- **No silent drop** (Label Spec I7; Data Model T2) — now structural for E1.
- **No incomplete tuple crosses the boundary**; predictor-visible completeness preserved (Benchmark
  Design §11).
- **Label meaning, behavioural states, taxonomy, D1 precedence, E4 ≠ D1, immutability** — all unchanged.
- **One producer per artifact; production graph acyclic** (ADR-002; Benchmark Design invariant 8).
- **Identity is tuple-independent** (Data Model R1): E1 candidates carry a stable identity.

## 8. Benchmark invariants intentionally relaxed

**Exactly one** invariant is relaxed:

- **The Candidate Subject / Output Tuple completeness invariant.** Previously, forming a Candidate
  Subject guaranteed a complete Output Tuple. Now it does not — *before eligibility*. Completeness is
  guaranteed only (a) after P1 passes, and (b) for any Output Tuple that crosses the boundary (Corpus
  Entries).

### Why a uniform ontology is worth more than the completeness invariant

The uniform lifecycle — one pre-instance artifact, one resolution model, every case travelling the same
path — is a **global, architectural** property of the benchmark. The completeness invariant is a
**local, artifact-level convenience** on a single artifact. When the two conflict, the global property
is the more valuable to keep, for four reasons:

1. **No-silent-drop becomes structural, not procedural.** With a uniform lifecycle, an E1 case is a
   Candidate Subject that resolves to a routed record — the benchmark *cannot* silently lose it, because
   there is only one path and it must terminate in a resolution. Alternatives that preserve the
   completeness invariant (A, C) must re-introduce a *separate* path for failures, and no-silent-drop
   then depends on that path being implemented correctly rather than on the ontology's shape.
2. **The phase model stays exact.** "An Instance is a Candidate Subject, then a Corpus Entry or a
   Routed-Aside Record" remains literally true for every case. Alternative A adds a pre-phase; Alternative
   C creates routed records that are not phases of any Instance. Both fragment the very model that makes
   the benchmark auditable.
3. **Completeness is eligibility's job anyway.** P1 already exists to adjudicate well-formedness. Encoding
   completeness as a *schema precondition of candidacy* forces the schema to be unable to represent its
   own failure — the contradiction G2 names. Relaxing the tuple and letting P1 decide simply relocates the
   check to where the specification already put the responsibility.
4. **The relaxation is safe exactly where it matters.** Completeness is still guaranteed at the boundary,
   so no predictor and no released artifact ever sees an incomplete tuple. The invariant is not abandoned;
   it is **moved** from "a precondition of candidacy" to "a guarantee of the boundary" — a strictly better
   placement, because the boundary is where completeness is actually consumed.

Trading a local artifact-level guarantee for a global lifecycle guarantee is therefore the better deal:
the uniform ontology is what makes the benchmark's integrity structural, and the completeness invariant
is preserved in the one place it is load-bearing.

### Versioning classification

This amendment changes **no** label meaning, behavioural state, taxonomy, or E-route *meaning*; it only
relaxes an artifact's pre-eligibility contents and clarifies P1's role. It is therefore a **compatible
extension (MINOR)** under Label Specification §11 and does **not** engage the Charter §4 v1/v2 boundary.

## Links

- [ADR-003 Exploration](../design/ADR-003_E1_Design_Alternatives.md) (alternatives A–D)
- [Label Generation Pipeline DAG](../docs/design/Label_Generation_Pipeline_DAG.md) §11 (G2), §5, §7.2, §8.1
- [Gemini pipeline DAG review](../reviews/gemini/pipeline_dag_review.md) §2
- [Label Specification](../docs/06_Label_Specification.md) §3 (P1), §8–§9 (E1), I7
- [Benchmark Data Model](../docs/06a_Benchmark_Data_Model.md) §1, §3.2, §3.3, §3.8, §6, T2
- [Formal Definitions](../docs/05_Formal_Definitions.md) §19, §36
- [ADR-002](./ADR-002-Construction-Provenance-Lifecycle.md) (provenance lifecycle; orthogonal)
