---
Status: Accepted
Date: 2026-07-01
Accepted: 2026-07-01
Supersedes: —
Superseded-by: —
Charter-clause: — (clarification only; changes no label meaning)
Related:
  - docs/01_Benchmark_Design.md
  - docs/05_Formal_Definitions.md
  - docs/06_Label_Specification.md
  - docs/06a_Benchmark_Data_Model.md
  - docs/07_Label_Generation_Pipeline.md
  - docs/design/Label_Generation_Pipeline_DAG.md
---

# ADR-002: Construction Provenance Lifecycle

> **This ADR clarifies benchmark semantics only.** It introduces **no** new benchmark concept, defines
> **no** new artifact, and modifies **no** benchmark behavior. It formalizes an interpretation already
> implied by the approved specifications, so that the construction dependency graph is unambiguously
> acyclic. It resolves finding **G1** of
> [Label Generation Pipeline DAG](../docs/design/Label_Generation_Pipeline_DAG.md).

## Context

The dependency analysis in [Label Generation Pipeline DAG](../docs/design/Label_Generation_Pipeline_DAG.md)
(§2, §8.2, §12, and finding G1) exposed an ambiguity in the approved specifications concerning
**Interventional Provenance** (Formal Definitions §20; Benchmark Data Model §3.7).

Interventional Provenance is specified to play two roles at once:

1. **As observational evidence** — the reconstructive evidence *from which* eligibility, Conditions A
   and B, the Behavioural State, and the Label are derived (Data Model §3.5: "Behavioural State is
   derived from Interventional Provenance"; §3.6: the Label is projected and binds to provenance).
2. **As the sealed evidence trail** — the record that ultimately *contains* those resulting
   determinations, so that a verdict is self-justifying and reconstructible (Data Model §3.7 required
   contents include the Behavioural State, Label, and reason code; Data Model T1 verdict
   reconstructability; Label Specification I8 self-justification).

If **both** roles are read as *production* dependencies over the one artifact, the graph is cyclic
(DAG §8.2):

```
   Interventional Provenance ──▶ determinations ──▶ Behavioural State ──▶ Label
             ▲                                                              │
             └───────────── "provenance must contain the Label" ───────────┘
```

The DAG is acyclic **only** if the determinations recorded in the sealed trail are interpreted as
**traceability back-references** rather than **production inputs** (DAG §2, §13). That interpretation is
fully consistent with the benchmark philosophy — construction is one-directional and irreversible
(Benchmark Design §9), provenance accretes append-only and is then frozen (Data Model §7, M1), and
ground truth is defined by specification and merely executed by code (Benchmark Design §10). But it has
never been stated explicitly, and the DAG warns that the Label Generation Pipeline (`07`) "must not
introduce a second semantic producer" for provenance while resolving this lifecycle detail.

This ADR fixes the interpretation. It is scoped to G1; other DAG findings (e.g. G2, the E1 no-output
case) are out of scope and remain open.

## Decision drivers

- **Preserve self-justification.** Label Specification I8 and Data Model T1 require the sealed
  provenance to *contain* the determinations, so a label is reconstructible from its provenance alone.
- **Preserve acyclicity of derivation.** The determinations must be *produced from* provenance, never
  the reverse; the production order in Formal Definitions, Label Spec, and Data Model §4 must hold.
- **Introduce nothing new.** No new benchmark concept or artifact (Formal Definitions §36); no behaviour
  change.
- **Give `07` an unambiguous contract.** The pipeline must never re-consume a determination as an input,
  and sealing must not count as a second producer of provenance.

## Considered options

1. **Remove the determinations from sealed provenance.** Rejected — it breaks I8/T1: a label would no
   longer be reconstructible from its provenance alone, defeating self-justification.
2. **Split Interventional Provenance into two separate first-class artifacts** ("observational" and
   "sealed"). Rejected — this introduces new benchmark artifacts, contradicting the no-new-concepts
   constraint and Formal Definitions §36. The lifecycle-phase framing (as Candidate Subject / Corpus
   Entry / Routed-Aside Record are phases of one Instance in Data Model §1) already suffices.
3. **Add an ordering / timestamp / layer field to disambiguate.** Rejected — a serialization/
   implementation detail; the Data Model is conceptual and fixes no schema (Data Model boundary).
4. **(Chosen) Formalize the provenance *lifecycle* and the two *graphs*.** Treat Interventional
   Provenance as one artifact passing through phases (observational → sealed); distinguish the
   production graph from the traceability graph as two *relations* over the same artifacts; and rule
   that the determinations recorded in sealed provenance are traceability back-references that MUST NOT
   be read as production dependencies. Purely a semantic clarification — no new artifact, no behaviour
   change.

## Decision

### Definitions (interpretations of existing artifacts, not new artifacts)

- **Observational provenance.** The phase of Interventional Provenance (§20) consisting *solely* of the
  raw, model-derived observations produced by applying interventions — the Intervention Records, the
  per-condition raw readings, control applicability and results, and precondition/eligibility
  observations. It is the **input** to semantic determination. It contains **no** determinations. It is
  accreted append-only during construction (Data Model M1).
- **Semantic determination.** The act of deriving the Behavioural State from observational provenance
  and projecting it to the Label (meaning owned by `06`; execution owned by `07`). The Behavioural
  State, Label, and reason code are its **outputs**.
- **Sealed provenance.** The finalized, immutable Interventional Provenance record after a Candidate
  Subject resolves — the observational provenance *together with* the resulting determinations folded in
  as traceability back-references, so the record is self-justifying (I8) and reconstructible (T1). It is
  frozen within a corpus version (Data Model M1).
- **Traceability back-reference.** A reference within sealed provenance that points to a determination
  (Behavioural State, Label, or reason code) it records, existing **solely** for audit and
  reconstruction. It is **not** a production input to that determination or to anything upstream of it.
- **Production graph.** The directed acyclic graph of *derivation* edges — observational provenance →
  semantic determination (Conditions A/B) → Behavioural State → Label. It is the authoritative graph for
  **how artifacts are produced** and MUST remain acyclic (DAG §8.1).
- **Traceability graph.** The *reference* graph over the sealed artifacts, used for audit, which
  additionally includes the back-references from sealed provenance to the determinations it records. It
  is **not** a production graph and is never consulted for derivation.

### The two graphs, side by side

```
 PRODUCTION GRAPH (authoritative for derivation; acyclic)

   observational provenance ──▶ [Condition A / B] ──▶ Behavioural State ──▶ Label
     (Intervention Records)          determination

 TRACEABILITY GRAPH (sealed artifact, for audit; back-references only)

   sealed provenance ⊇ observational provenance
   sealed provenance ┄┄back-ref┄┄▶ Behavioural State      (records the outcome)
   sealed provenance ┄┄back-ref┄┄▶ Label / reason code    (records the outcome)
                     └── these ┄┄▶ edges are NOT production edges ──┘
```

The apparent cycle exists only if one collapses two distinct relations — "is produced from" and
"is-traceable-to" — into a single edge set. Keeping them as separate graphs makes each acyclic and
removes the ambiguity.

### Normative statements

- **N1.** Traceability back-references MUST NOT be interpreted as production dependencies. The presence
  of a Behavioural State, Label, or reason code inside a sealed Interventional Provenance record is a
  **record-of-outcome for audit**, not an input consumed by any producing process.
- **N2.** The production graph is the sole authority for derivation and MUST remain acyclic. No process
  MAY consume a determination from sealed provenance in order to (re)produce that determination, or any
  artifact upstream of it in the production graph.
- **N3.** Interventional Provenance is a **single** artifact (Formal Definitions §20) with two lifecycle
  phases — observational (input) and sealed (self-justifying output). "Observational provenance" and
  "sealed provenance" are **phases**, not new artifacts. There is exactly **one** producer of
  Interventional Provenance (`07`); sealing does **not** create a second producer (DAG §8.2).
- **N4.** Sealing folds the determinations into provenance as back-references **only after** they are
  produced. Sealing changes no value and adds no production edge (Data Model M1; Benchmark Design §10).

### Scope of this decision

This ADR is an interpretation. It introduces no new benchmark concept and modifies no benchmark
behaviour; it makes explicit what is already implied by Formal Definitions §20, Label Specification I8,
Data Model §§3.5–3.7, T1, and M1, and Benchmark Design §9–§10. It resolves DAG finding **G1** and leaves
all other DAG findings untouched.

## Consequences

**Positive.**
- The construction production graph is unambiguously acyclic under a stated interpretation, while I8
  self-justification and T1 reconstructability are fully preserved.
- The interpretation matches append-only-then-freeze accretion (Data Model M1) and construction
  irreversibility (Benchmark Design §9).
- `07` inherits an unambiguous contract: sealing is not a second producer, and determinations are never
  re-consumed as inputs.
- Future readers cannot misread the determinations contained in sealed provenance as production inputs.

**Negative / accepted costs.**
- Readers and any provenance tooling must understand the two-graph distinction; the sealed artifact's
  reference structure is intentionally richer than its production structure.
- `07` and any provenance store MUST keep production edges one-directional. Enforcing this is an
  implementation responsibility and is not fixed here.

**Follow-ups.**
- `07` (Label Generation Pipeline) MUST reference this ADR when specifying provenance sealing and MUST
  NOT introduce a second producer for Interventional Provenance.
- The DAG design document's finding **G1** is resolved by this ADR and MAY be annotated accordingly
  (non-normative).
- A clarifying cross-reference to this ADR MAY be added to Data Model §3.7 and §8 (a clarification, not
  a semantic change). Recommended; not performed by this ADR.

## Links

- [Label Generation Pipeline DAG](../docs/design/Label_Generation_Pipeline_DAG.md) §2, §8.2, §12, §13, G1
- [Formal Definitions](../docs/05_Formal_Definitions.md) §20 (Interventional Provenance)
- [Label Specification](../docs/06_Label_Specification.md) §5 (Behavioural State), I8 (self-justification)
- [Benchmark Data Model](../docs/06a_Benchmark_Data_Model.md) §§3.4–3.7, §7 (M1–M5), §8 (T1)
- [Benchmark Design](../docs/01_Benchmark_Design.md) §9 (irreversibility), §10 (spec vs implementation)
