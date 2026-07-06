---
Title: ADR-003 (Exploration) — E1 Design Alternatives
Status: Exploration (discussion paper preparing ADR-003)
Prepared-for: decisions/ADR-003 (not yet written)
Date: 2026-07-01
Related:
  - docs/05_Formal_Definitions.md
  - docs/06_Label_Specification.md
  - docs/06a_Benchmark_Data_Model.md
  - docs/07_Label_Generation_Pipeline.md
  - docs/08_Dataset_Specification.md
  - docs/design/Label_Generation_Pipeline_DAG.md
  - decisions/ADR-002-Construction-Provenance-Lifecycle.md
---

# ADR-003 (Exploration) — E1 Design Alternatives

> **This is a discussion paper, not a decision.** It presents multiple benchmark-consistent
> alternatives for resolving the E1 ontology ambiguity and analyses each. It makes **no**
> recommendation and selects **no** option. Its sole purpose is to prepare a future
> `decisions/ADR-003`. Nothing here changes any specification.

---

## 1. The ambiguity (DAG finding G2)

The approved artifact lifecycle implies the chain:

```
   Output Tuple  →  Candidate Subject  →  Eligibility (P1–P6)  →  E1
```

But **E1 is defined as the absence of a complete Output Tuple**:

- Label Specification §3 P1 (well-formed subject): *"A generator produced a genuine chosen answer and
  a genuine rationale … a complete output tuple exists."* E1 is the negation, ¬P1 (Label Spec §8, §9):
  *"Malformed or absent output: no complete output tuple."*
- Data Model §3.3 (Candidate Subject) **requires** the artifact to contain an Output Tuple; §3.2
  defines the Output Tuple to contain the exact chosen answer and exact rationale.
- Data Model §3.8 (Routed-Aside Record) defines it as *"the ineligible resolution of a Candidate
  Subject."*

The circularity: a Candidate Subject cannot exist without a complete Output Tuple, yet E1 is exactly
the case where no complete Output Tuple exists — so the artifact that E1 is supposed to resolve
(a Candidate Subject) cannot have been formed. The dependency graph (DAG §11, G2) leaves E1 inside the
eligibility step "because the approved documents require it," while noting that *"the exact input
artifact for the no-output case is not defined,"* and that introducing a generation-attempt artifact,
permitting an incomplete candidate, or routing before candidate creation would *each be a new
specification decision.*

This paper explores those and other benchmark-consistent resolutions.

---

## 2. Constraints any resolution must satisfy

For an alternative to be **benchmark-consistent**, it must preserve the following (these are the
yardsticks used in §4). They are not up for negotiation in ADR-003; only the way E1 is modelled is.

- **CC1 — No silent drop.** Every generation of a (generator, source record) pair must resolve to a
  retained outcome; an E1 case must be preserved with an identity and justifying evidence, never
  discarded (Label Spec I7; Data Model T2; DAG §7.2 resolution totality). This is the whole reason E1
  exists as a named route rather than a filter.
- **CC2 — Identity must be available without a tuple.** An E1 case must carry a stable identity even
  though it has no complete Output Tuple.
- **CC3 — No incomplete tuple crosses the boundary.** Predictors only ever see complete Output Tuples
  (those inside Corpus Entries); an E1 case must never reach the corpus (Benchmark Design §11; Data
  Model §3.9).
- **CC4 — Construction integrity.** One producer per artifact and one-directional production must hold
  (Benchmark Design invariant 8; ADR-002 N2/N3).
- **CC5 — New concepts require justification.** Any new artifact must be justified against the ontology
  (Formal Definitions §36).
- **CC6 — E-route discipline.** E1 must remain distinct from the other eligibility routes; in
  particular the existing discipline that E4 ≠ D1 and that "routed aside" is not a label value must be
  untouched (Label Spec §9).
- **CC7 — Justifying evidence for E1.** A Routed-Aside Record requires provenance sufficient to justify
  ineligibility (Data Model §3.8). For E1 there were **no interventions** (you cannot intervene on a
  subject whose output never formed), so the justifying evidence is the *generation-failure* record,
  not Intervention Records. Every alternative must say where that evidence lives.

---

## 3. A shared observation: identity is tuple-independent

One fact simplifies every alternative and is worth stating once. The instance identity is the pair
`(composite generator identity, source record identity)` (Data Model §6, R1). **Both halves exist
before generation** — the generator identity and the source record identity are known the moment a
generator is pointed at a source record. Therefore an E1 case *always has a well-defined identity*
(CC2 is satisfiable) regardless of whether a tuple was produced. What E1 lacks is not identity but a
**complete Output Tuple**. The alternatives differ chiefly in *which artifact carries that identity*
when the tuple is missing.

A concrete motivating case (from the pipeline inventory §3.2): a **composite** generator may produce a
chosen answer at its answer stage but fail to produce a rationale at its rationale stage — a *partial*
Output Tuple (answer present, rationale absent). This is neither a clean abstention (E2) nor a total
absence; it is precisely the "incomplete tuple" that the current ontology cannot represent.

---

## 4. Alternatives

Each is analysed across: **ontology impact · benchmark semantics · compatibility with existing
specifications · implementation impact · strengths · weaknesses.**

### 4.A — Introduce a Generation Attempt artifact

A new pre-tuple artifact — a **Generation Attempt** — represents the (generator, source record) pairing
and the act of generation, whether or not it yields a complete Output Tuple. A Candidate Subject is
formed **only** from a Generation Attempt that produced a complete tuple. A Generation Attempt that
failed to produce a complete tuple resolves **directly** to an E1 Routed-Aside Record.

- **Ontology impact.** Adds one first-class artifact upstream of Output Tuple/Candidate Subject. The
  Routed-Aside Record's producing input generalizes from "a Candidate Subject" to "a Candidate Subject
  *or* a failed Generation Attempt." Instance identity anchors on the Generation Attempt, so E1 records
  inherit identity. The Candidate Subject retains its strong invariant (always complete).
- **Benchmark semantics.** E1 becomes "a generation attempt that did not yield a complete tuple,"
  cleanly retained (CC1). Downstream artifacts keep the guarantee that every Candidate Subject, Corpus
  Entry, and non-E1 route rests on a complete tuple. E1's justifying evidence (CC7) lives in the
  Generation Attempt record.
- **Compatibility.** Requires amending Data Model (add the artifact; generalize §3.8 producing input;
  re-anchor identity from Candidate Subject to a shared attempt identity) and likely Formal Definitions
  (a new §-term, justified per CC5/§36). Label Spec E1 meaning is unchanged. DAG T2/T3/T8 shift so T8
  can consume a failed attempt. ADR-002's one-producer rule is respected (the Generation Attempt has
  one producer).
- **Implementation impact.** The generation stage always emits a Generation Attempt; on success it
  derives the Output Tuple and Candidate Subject; on failure it emits an E1 Routed-Aside Record. The
  thesis currently turns generation exceptions into empty strings or drops (Inventory §9, assumptions
  10/14) — capturing the attempt is net-new but localized to the generation stage.
- **Strengths.** Cleanest separation; the Candidate Subject/Output Tuple completeness invariant is
  preserved intact; E1 identity and evidence are well-defined; the partial-tuple composite case (§3) is
  naturally an "attempt that failed to complete."
- **Weaknesses.** Introduces a new benchmark concept, engaging §36 and (if it changes what artifacts
  the label rests on) possibly Charter review; adds an artifact that overlaps conceptually with the
  Candidate Subject (risk of two similar pre-instance artifacts); the phase model ("Instance = Candidate
  Subject → Corpus Entry XOR Routed-Aside") gains a pre-phase.

### 4.B — Allow incomplete Candidate Subjects

Relax the Candidate Subject so it MAY carry an incomplete or absent Output Tuple. A Candidate Subject
is formed from every (generator, source record) generation regardless of completeness; eligibility (P1)
then detects incompleteness and routes E1.

- **Ontology impact.** No new artifact, but the Candidate Subject invariant changes: it no longer
  guarantees a complete Output Tuple (Data Model §3.3), and the Output Tuple becomes possibly-partial
  *within a pre-eligibility candidate*. The "Instance has three phases" model is untouched (E1 is still
  the ineligible resolution of a Candidate Subject).
- **Benchmark semantics.** E1 is handled uniformly with the other eligibility routes, all inside the
  eligibility step. A Candidate Subject means "a (generator, source record) pairing with whatever output
  resulted." Because E1 candidates never reach the corpus, no incomplete tuple ever ships (CC3 holds).
  E1 evidence (CC7) is the partial/empty tuple recorded on the candidate.
- **Compatibility.** Amends Data Model §3.3 (candidate may hold an incomplete tuple) and clarifies §3.2
  / Formal Definitions §19 (the Output Tuple is guaranteed complete only for Corpus Entries, i.e. on the
  predictor-visible side). Label Spec P1/E1 meanings are unchanged. DAG T3 no longer requires a complete
  A2 to bind A3.
- **Implementation impact.** Generation always yields a candidate (possibly with a partial/empty
  tuple); eligibility checks P1 first. Single pre-instance artifact; the pipeline is simple. The thesis
  still needs to *retain* the failed case rather than drop it. Directly represents the composite
  partial-tuple case (§3) as an incomplete candidate.
- **Strengths.** No new concept (lightest ontology change); one uniform pre-instance artifact; E1 sits
  in the same eligibility gate as E2–E6, so the routing model is homogeneous.
- **Weaknesses.** Weakens a core cleanliness property — the guarantee that a Candidate Subject/Output
  Tuple is always complete; "incomplete output tuple" is a slightly awkward object that every downstream
  reader must remember is possible pre-eligibility; care is needed so no code assumes completeness before
  the P1 gate.

### 4.C — Route before Candidate Subject creation

Keep the Candidate Subject strictly requiring a complete tuple, but detect E1 **before** candidacy: if
generation fails to produce a complete tuple, produce an E1 Routed-Aside Record directly, without ever
forming a Candidate Subject. Two framings differ in where E1 "belongs":

- **C1 — Pre-candidacy eligibility route.** P1 is split: the "complete tuple exists" check runs at
  generation (pre-candidacy) and yields E1; P2–P6 run after candidacy as today.
- **C2 — E1 as a generation-stage outcome.** E1 is removed from the eligibility list entirely and
  defined as one of two outcomes of the generation transformation (T2): *complete tuple* or *E1*. The
  eligibility gate then assumes a complete tuple always exists.

- **Ontology impact.** No new persistent artifact, but the Routed-Aside Record's producing input
  generalizes from "a Candidate Subject" to "a Candidate Subject *or* a failed generation" (Data Model
  §3.8). Crucially, an E1 Routed-Aside Record then corresponds to **no formed Instance**, so the "three
  phases of one Instance" model (Data Model §1) acquires an exception: some routed-aside records are not
  a phase of any Instance. Identity is still (generator, source record) (CC2).
- **Benchmark semantics.** E1 becomes a *pre-instance* route (C1) or a *generation outcome* (C2). Under
  C2, the eligibility gate is cleaner (all candidates complete) but P1/E1 leave the P1–P6 list, a
  visible change to Label Spec §3/§8's uniform gate. E1 evidence (CC7) lives in the generation-failure
  record attached to the routed-aside record.
- **Compatibility.** Amends Data Model §3.8 (generalized producer) and §1 (phase-model exception), and —
  under C2 — Label Spec §3/§8 (relocate P1/E1 out of the instance-eligibility list). Formal Definitions
  §23 (routed-aside set) is unaffected in meaning. DAG §7.2 totality restates from "every Candidate
  Subject resolves…" to "every generation resolves…". ADR-002 is respected.
- **Implementation impact.** The generation stage detects completeness; on failure it emits an E1
  Routed-Aside Record and skips candidacy. Avoids constructing candidates for failed generations.
  Reasonably simple; localizes E1 to the generation stage.
- **Strengths.** Preserves the Candidate Subject completeness invariant; introduces no new artifact;
  avoids the "incomplete candidate." C2 makes the eligibility gate uniform over complete subjects.
- **Weaknesses.** Breaks the clean "Routed-Aside = phase of an Instance" model for E1 (an E1 record has
  no Instance); heterogeneous producer for the Routed-Aside Record; C1 bifurcates eligibility (P1
  pre-candidacy, P2–P6 post-candidacy); C2 changes the shape of the P1–P6 list, which readers currently
  treat as one uniform gate.

### 4.D — Redraw the E1/E2 boundary

Interpret a "complete Output Tuple" as *structurally present fields*: generation is defined to always
emit **some** answer and **some** (possibly empty) rationale string, so a Candidate Subject is always
formable. "Absent/malformed output" then largely collapses into the degeneracy already covered by **E2**
(abstention/refusal/degenerate rationale). E1 is narrowed to only catastrophic cases (e.g. the generator
process never returns at all), which are handled as a generation exception outside the instance
lifecycle.

- **Ontology impact.** Minimal: the Candidate Subject invariant is preserved (a structural tuple always
  exists), and no new artifact appears. The change is to the **E1/E2 semantic boundary** (Label Spec §8,
  §9): most "no complete output" cases become E2 degeneracy, and E1 becomes near-vacuous at the instance
  level.
- **Benchmark semantics.** The routing model stays homogeneous (all candidates complete; degeneracy is
  E2). The risk is semantic drift: E1 ("malformed/absent output") and E2 ("degenerate rationale") were
  deliberately separate; merging blurs "the generator produced nothing usable" with "the generator
  declined/produced junk." E1 evidence (CC7) is subsumed into E2 evidence for the common cases; the rare
  catastrophic case still needs a generation-exception record.
- **Compatibility.** Amends Label Spec §3 (P1 becomes "a structurally complete tuple exists," nearly
  always true) and §8/§9 (E1 narrowed, E2 broadened). Data Model §3.2/§3.3 gain a note that "complete"
  means structurally present. No new artifact; DAG unchanged in shape (E1 rarely fires). Interacts with
  the composite partial-tuple case (§3): a missing rationale would become E2, not E1 — which may or may
  not be the desired reading.
- **Implementation impact.** Generation must guarantee a structural tuple (fill an empty rationale
  rather than throw), and health checks classify degeneracy as E2. The thesis already turns failures
  into empty strings (Inventory §9) — this alternative would *formalize* that behaviour as E2 rather than
  E1, which is closer to current code but changes the approved E-route meanings.
- **Strengths.** Smallest artifact/lifecycle change; keeps one uniform eligibility gate; aligns with how
  generators typically behave (they emit *something*).
- **Weaknesses.** Redefines two approved E-codes and their boundary — the most direct change to *label
  semantics* of any alternative here, so the most likely to engage Charter §4/§5 and the "would existing
  routed outcomes change meaning?" test; risks conflating "produced nothing" with "produced junk," which
  the original E1/E2 split kept apart; the composite partial-tuple case is reclassified, which needs
  explicit endorsement.

---

## 5. Comparison matrix

| Dimension | A · Generation Attempt | B · Incomplete Candidate | C · Route before candidacy | D · Redraw E1/E2 |
|---|---|---|---|---|
| New artifact? | Yes (one) | No | No | No |
| Candidate completeness invariant | Preserved | **Weakened** | Preserved | Preserved |
| "Routed-aside = phase of Instance" | Pre-phase added | Preserved | **Exception (E1 has no Instance)** | Preserved |
| Changes E-route meanings? | No | No | C2: relocates P1/E1 | **Yes (E1↔E2)** |
| Specs touched | 05, 06a (, DAG) | 06a (, 05 §19 note) | 06a (, 06 for C2) | 06 (, 06a note) |
| Engages Charter §4/§5? | Possibly (new concept) | Unlikely | C2: possibly | **Likely** |
| Composite partial-tuple case | "failed attempt" | "incomplete candidate" | pre-candidacy route | reclassified as E2 |
| Implementation locus | generation stage | generation + eligibility | generation stage | generation + health |
| Ontology footprint | Largest | Small | Medium | Smallest |

*(The matrix is a summary aid, not a scoring; a low footprint is not automatically preferable — e.g. D's
small footprint carries the largest semantic change.)*

---

## 6. Cross-cutting questions ADR-003 will need to resolve

Independent of which alternative is chosen, ADR-003 should address:

- **Where E1's justifying evidence lives (CC7).** For all alternatives, an E1 outcome has no Intervention
  Records; the decision must state what constitutes sufficient provenance for an E1 Routed-Aside Record
  (a generation-failure record), so I8/T2 still hold.
- **Whether the Instance phase model admits pre-tuple members.** A (Generation Attempt) or a
  pre-candidacy E1 record forces a stance on whether every Routed-Aside Record is a phase of a formed
  Instance (Data Model §1).
- **The composite partial-tuple case (§3).** The chosen model must classify "answer present, rationale
  absent" unambiguously (E1 vs E2 vs incomplete candidate). This interacts with Label Spec **Q4**
  (composite-generator validity).
- **Interaction with baseline-output identity.** Data Model **Q1** (whether an explicit
  "baseline-output-of-record" is needed) bears on when an Output Tuple is deemed "complete," which is the
  crux of E1.
- **Whether the change touches label meaning.** Alternatives that redraw E-route meanings (notably D, and
  C2's relocation of P1) must be tested against the Charter §4 v1/v2 boundary; alternatives that only add
  or relax an *artifact* (A, B) more likely stay within a v1 amendment.

---

## 7. Status and next step

This paper deliberately makes **no recommendation**. It enumerates four benchmark-consistent ways to
resolve G2 — a Generation Attempt artifact, incomplete Candidate Subjects, pre-candidacy routing (two
framings), and redrawing the E1/E2 boundary — and analyses each against the same constraints and
dimensions.

The next step is a decision record, `decisions/ADR-003`, which will select one alternative (or a
synthesis), record the rationale, and specify the resulting amendments to the affected documents. Until
then, the E1 lifecycle remains an **open ontology question** and the DAG's G2 stands.

---

## Links

- [Label Generation Pipeline DAG](../docs/design/Label_Generation_Pipeline_DAG.md) §11 (G2), §7.2, §5 (T2, T3, T8)
- [Label Specification](../docs/06_Label_Specification.md) §3 (P1), §8–§9 (E1/E2 routing), I7
- [Benchmark Data Model](../docs/06a_Benchmark_Data_Model.md) §1 (Instance phases), §3.2, §3.3, §3.8, §6 (R1), T2
- [Formal Definitions](../docs/05_Formal_Definitions.md) §19 (Output Tuple), §23 (routed-aside set), §36 (new terms)
- [ADR-002](../decisions/ADR-002-Construction-Provenance-Lifecycle.md) (one producer per artifact; production vs traceability)
