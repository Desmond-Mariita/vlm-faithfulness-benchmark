---
Title: Label Generation Pipeline
Status: Accepted
Benchmark-Version: v1.0
Last-reviewed: 2026-07-01
Related:
  - docs/01_Benchmark_Design.md
  - docs/03_Problem_Definition.md
  - docs/05_Formal_Definitions.md
  - docs/06_Label_Specification.md
  - docs/06a_Benchmark_Data_Model.md
  - docs/08_Dataset_Specification.md
  - docs/10_Evaluation_Protocol.md
  - decisions/ADR-002-Construction-Provenance-Lifecycle.md
  - decisions/ADR-003-Incomplete-Candidate-Subjects.md
  - docs/design/Specification_Traceability_Matrix.md
  - docs/design/Label_Generation_Pipeline_DAG.md
---

# Label Generation Pipeline

*This specification operationalizes benchmark construction. It defines how benchmark artifacts are
transformed from a `Source Record` and a `Generator` into a `Label` (or a `Routed-Aside Record`) with
sealed `Interventional Provenance`. It implements the approved semantics **exactly** and redefines
**nothing**.*

> **Boundary of this document.** This is an **operational specification**: it states the *required
> behaviour* of each construction stage — its inputs, outputs, invariants, preconditions,
> postconditions, failure routing, and traceability obligations. It is **not** pseudocode, an
> implementation guide, or an algorithm. It defines **no** thresholds, models, saliency methods,
> intervention algorithms, serialization, or JSON schemas; those remain **implementation decisions**
> (§9). Every semantic term is owned by [Formal Definitions](05_Formal_Definitions.md) and
> [Label Specification](06_Label_Specification.md); this document only *executes* them. An independent
> team MUST be able to implement this pipeline without changing any benchmark semantics.

> **Requirement keywords.** MUST, MUST NOT, SHOULD, and MAY are used in the RFC-2119 sense.

---

## 1. Scope and ownership

This pipeline is the operational owner of construction stages **S02–S15**: generator execution,
Candidate Subject binding, eligibility determination (P1–P6), intervention observation, Condition A/B
determination, Behavioural State determination, Label projection, and provenance accretion and sealing
(routed and eligible). Stage identifiers correspond **one-to-one** to the
[Specification Traceability Matrix](design/Specification_Traceability_Matrix.md) §3.

It does **not** own:

- **S01** (Source Record normalization) — owned by [Dataset Specification](08_Dataset_Specification.md);
  consumed here as an input contract (§8.1).
- **S16–S19** (Corpus Entry assembly, split assignment, routed-aside collection, corpus freeze and
  manifest, evaluation views) — owned by `08`/`10`; the pipeline delivers to them via an output handoff
  (§8.2).

The pipeline preserves the single lifecycle (Data Model §1): every `Candidate Subject` resolves exactly
once — to a labelled candidate handed to S16, **or** to a `Routed-Aside Record` handed to S17.

---

## 2. Normative authorities

This pipeline consumes, and MUST NOT contradict, the following (keys as used in the Traceability
Matrix §2):

| Key | Authority |
|---|---|
| **BD** | Benchmark Design — architecture, boundary, one-way flow, invariants BD1–BD8. |
| **PD** | Problem Definition — intervention-only construction, refused shortcuts (PD-R1–R7). |
| **FD** | Formal Definitions — normative meanings and dependency order. |
| **LS** | Label Specification — P1–P6, Conditions A/B, S1–S3, projection, E1–E6, invariants I1–I9. |
| **DM** | Benchmark Data Model — artifact forms, identity (R1–R8), mutability (M1–M5), traceability (T1–T6), versioning (V1–V6). |
| **ADR2** | ADR-002 — observational/sealed provenance phases; production vs traceability graphs (N1–N4). |
| **ADR3** | ADR-003 — incomplete pre-eligibility Output Tuples/Candidate Subjects; P1/E1 lifecycle. |
| **ADR6** | ADR-006 — universal P6 eligibility and branch-appropriate causal-license evidence (C1–C8). |

Where this document appears to differ from any authority above, the authority governs.

---

## 3. Pipeline overview

```
  [S01 Source Record]  ──(input contract, §8.1)──▶
     │
     ▼
  S02 execute generator ──▶ Output Tuple (MAY be incomplete, ADR3)
     ▼
  S03 bind Candidate Subject  ── identity = (composite generator subject, source record)
     ▼
  S04 P1 completeness ──fail─▶ E1 ─┐
     ▼ pass                         │
  S05 P2 non-abstention / P3 scope ─fail─▶ E2/E3 ─┤
     ▼ pass                                        │
  S06 observe answer-side interventions            │
     ▼                                             │
  S07 P4 / Condition A                             │
     ├─ indeterminate ─▶ E4 ───────────────────────┤   (E4 MUST NOT become S1/D1)
     ├─ A false ─────────────────────────────┐     │
     ▼ A true                                │     │
  S08 P5 evidence locatability ──fail─▶ E5 ──┼─────┤   (E5 MUST NOT become D2)
     ▼ pass                                  │     │
  S09 observe evidence-matched rationale interventions
     ▼                                       │     │
  S10 P6 causal license ◀── A-false and A-true branches; branch-appropriate evidence
     ├─ fail ─▶ E6 ───────────────────────────┤   (E6 no state)
     ├─ pass, A false ───────────────┐     │
     ▼ pass, A true                         │     │
  S11 Condition B                            │     │
     ▼                                       ▼     ▼
  S12 Behavioural State  ◀── (A false ⇒ S1; A·¬B ⇒ S2; A·B ⇒ S3)
     ▼                                             │
  S13 project Label (S1→unfaithful/D1, S2→unfaithful/D2, S3→faithful)
     ▼                                             ▼
  S14 seal eligible provenance          S15 resolve + seal routed-aside (E1–E6)
     ▼                                             ▼
  [labelled candidate → S16]           [Routed-Aside Record → S17]
 ══════════════════════ construction / evaluation boundary (S18–S19, §8.2) ══════════════════════
```

Two lifecycles run underneath every stage:

- **Production** (ADR-002): observational provenance accretes append-only across S04–S11; the
  determinations (state at S12, label at S13) are **produced from** it; sealing (S14/S15) folds them in
  as **traceability back-references**, which MUST NOT be read as production inputs (ADR2-N1).
- **Resolution** (ADR-003 + LS I7): every Candidate Subject — including one with an incomplete Output
  Tuple — resolves exactly once; nothing is silently dropped.

---

## 4. Cross-cutting invariants (bind every stage)

Every stage MUST uphold the following. Stages reference them by number rather than restating them.

- **CC1 — Interventional-only ground truth.** No **faithfulness determination** — Condition A, Condition
  B, a Behavioural State, a Label, or a reason code — MAY be determined, adjusted, or overridden by
  inspection of the rationale's *content/meaning*, by any human or model judge, or by any plausibility,
  grounding, entailment, or answer-correctness estimate. The **structural eligibility checks** (P1
  completeness, P2 non-abstention/degeneracy, P3 scope) MAY examine the rationale's *presence and form*
  to decide **eligibility** — this is not a faithfulness judgment and does not violate the no-judge
  boundary. (LS-I2 governs the *label*, not the structural eligibility gates; LS-I6; PD-R1–R2.)
  Answer correctness never gates eligibility and never selects a route (ADR-004 C1): the P1–P6 gates
  operate identically for correct and incorrect chosen answers, and Condition A concerns the exact
  emitted chosen answer, not its agreement with any reference answer (CC4; ADR-004 C4).
- **CC2 — No silent drop.** Every Candidate Subject MUST resolve exactly once (S16 label path or S15
  route path). No candidate, observation, or failure may be discarded, normalized away, or converted to
  an empty value in place of a resolution. (LS-I7; DM-T2.)
- **CC3 — One-directional production; single producer.** Each artifact has exactly one producing stage;
  no stage consumes a determination from sealed provenance to (re)produce that determination or anything
  upstream of it; sealing is not a second producer of provenance. (ADR2-N1–N4; BD8.)
- **CC4 — Exact baseline outputs.** All interventions and determinations MUST use the candidate's exact
  emitted chosen answer and exact emitted baseline rationale. A gold answer MUST NOT be substituted for
  the chosen answer, and a regenerated rationale MUST NOT be substituted for the baseline rationale.
  (DM-R2; ADR3.)
- **CC5 — Retain graded evidence.** Determinations MUST retain the graded/raw readings (not only hard
  choices) sufficient to reconstruct the verdict. (LS-I8; DM-T1.)
- **CC6 — Identity binding.** Every artifact MUST carry the instance identity `(composite generator
  identity, source record identity)`; the generator identity MUST be recorded and MUST NOT appear in the
  Output Tuple. (DM-R1–R3, R6; LS-I3.)
- **CC7 — Same subject.** Every counterfactual observation MUST use the same composite generator subject
  that produced the baseline output. (FD §1, §12.)
- **CC8 — Incomplete tuples never cross the boundary.** No incomplete Output Tuple may reach a Corpus
  Entry; completeness at the boundary is guaranteed by P1 having passed. (ADR3; BD §11.)
- **CC9 — Provenance and margins are never predictor inputs.** Interventional Provenance and its graded
  facets are released, if at all, through the audit view only. (LS §6 margins; DM-T6; PD-R7.)
- **CC10 — Necessary-condition scope.** A `faithful` outcome licenses nothing about the generator's
  internals; the pipeline asserts behaviour only. (LS §5 scope.)
- **CC11 — Append-only then sealed.** Observational provenance accretes append-only until sealing;
  once sealed it is immutable within a corpus version. (DM-M1, M3; ADR2.)
- **CC12 — Determinism of meaning.** Each determination means exactly the condition defined in LS; it
  means nothing more (in particular nothing mechanistic) and nothing less. (LS-I1.)

---

## 5. Stage specifications (S02–S15)

Each stage lists: **Stage identifier · Purpose · Consumed artifacts · Input artifact(s) · Produced
artifacts · Output artifact(s) · Governing specification(s) · Applicable ADRs · Required invariants ·
Preconditions · Postconditions · Failure routing · Traceability obligations.** Operational methods and
thresholds are deferred to §9.

### S02 — Execute generator and retain baseline output
- **Purpose.** Run the generator once over the Source Record and retain its exact baseline output.
- **Consumed artifacts.** Source Record; the live composite generator subject (with a complete
  recorded identity).
- **Input artifact(s).** Source Record.
- **Produced artifacts.** Output Tuple (possibly incomplete); the designated exact baseline output.
- **Output artifact(s).** Output Tuple.
- **Governing specification(s).** FD §§1, 5–6, 19; BD §4(2), §§7, 12; Output Tuple shape owned by `08`.
- **Applicable ADRs.** ADR-003.
- **Required invariants.** CC4, CC6, CC7, CC10; BD1–BD4, BD7–BD8; DM-R1–R3, R6, M2; ADR3-P/R.
- **Preconditions.** A Source Record exists (§8.1); a composite generator subject with a complete
  identity is selected.
- **Postconditions.** Exactly one Output Tuple is emitted for the `(generator, source record)` pair,
  carrying the exact chosen answer and exact rationale **as emitted**. The tuple MAY be incomplete
  (chosen answer and/or rationale absent). The exact baseline output is designated and retained
  unchanged for use by all later stages.
- **Failure routing.** A failed or partial generation MUST be retained as an incomplete Output Tuple;
  completeness is adjudicated at S04. No drop, pad, or empty-string substitution (CC2).
- **Traceability obligations.** Record the composite generator subject identity, the source identity,
  and the exact baseline output. (DM-T1, T3.)

### S03 — Bind Candidate Subject
- **Purpose.** Bind the Output Tuple to its `(generator, source record)` pair and assign the instance
  identity.
- **Consumed artifacts.** Source Record; Output Tuple (possibly incomplete); composite generator
  subject identity.
- **Input artifact(s).** Output Tuple.
- **Produced artifacts.** Candidate Subject.
- **Output artifact(s).** Candidate Subject.
- **Governing specification(s).** DM §§1, 3.3, 6; FD §§1, 22; LS-I3.
- **Applicable ADRs.** ADR-003.
- **Required invariants.** CC2, CC6; LS-I3; DM-R1–R3, R6–R7, M1–M2, T3; ADR3-P/R.
- **Preconditions.** An Output Tuple (possibly incomplete) exists for the pair.
- **Postconditions.** Exactly one Candidate Subject per `(generator, source record)` pair, carrying the
  stable instance identity, the (possibly incomplete) Output Tuple, and the composite generator subject
  identity (withheld from predictors).
- **Failure routing.** None: binding always succeeds when the identity halves exist (both exist before
  generation, DM-R1). Completeness is adjudicated at S04, not here.
- **Traceability obligations.** The instance identity MUST be carried unchanged through every later
  phase. (DM-R1, R7.)

### S04 — Determine P1 completeness
- **Purpose.** Determine whether the Candidate Subject's Output Tuple is sufficiently complete for
  further benchmark processing.
- **Consumed artifacts.** Candidate Subject; the (new) observational Interventional Provenance phase.
- **Input artifact(s).** Candidate Subject.
- **Produced artifacts.** Observational provenance accretion containing the P1 result; on failure, an E1
  route outcome for S15.
- **Output artifact(s).** P1 determination (recorded in observational provenance).
- **Governing specification(s).** LS §3 P1, §9 E1; DM §§3.3, 3.7–3.8, 4, T2.
- **Applicable ADRs.** ADR-002 (provenance phase, N3); ADR-003.
- **Required invariants.** CC1, CC2, CC3, CC5, CC6, CC11; LS-I3, I7–I8; DM-M1–M2, T1–T3; ADR2-N3;
  ADR3-P/R.
- **Preconditions.** A Candidate Subject exists (S03).
- **Postconditions.** A determinate P1 result (sufficiently complete / not) is recorded. If not
  sufficiently complete, an E1 outcome is selected.
- **Failure routing.** P1 fail → **S15 with E1** (no Intervention Records; no state; no label — ADR3).
- **Traceability obligations.** Record the completeness evidence in observational provenance. (DM-T1–T2.)
- *Deferred (§9): the operational completeness criterion, which MUST assess sufficiency of the exact
  baseline output (CC4).*

### S05 — Determine P2 non-abstention and P3 scope
- **Purpose.** Determine whether the rationale is a bona fide justification (P2) and the instance is in
  scope (P3).
- **Consumed artifacts.** P1-qualified Candidate Subject; observational provenance.
- **Input artifact(s).** Candidate Subject.
- **Produced artifacts.** Observational provenance accretion containing the P2/P3 results; on failure, an
  E2 or E3 route outcome for S15.
- **Output artifact(s).** P2/P3 determinations (recorded in provenance).
- **Governing specification(s).** LS §3 P2–P3, §9 E2–E3; PD §7 A5; DM §§3.7–3.8, T2.
- **Applicable ADRs.** ADR-002 (N2–N3).
- **Required invariants.** CC1, CC2, CC5, CC6, CC11; PD-A5, PD-R1–R4; LS-I2, I6–I8; DM-M1, T1–T2.
- **Preconditions.** P1 passed.
- **Postconditions.** Determinate P2 and P3 results recorded.
- **Failure routing.** P2 fail → S15 with E2; P3 fail → S15 with E3 (no state; no label).
- **Traceability obligations.** Record the abstention/scope evidence. (DM-T1–T2.)
- *ADR-004: answer correctness plays no role in P2/P3 — an incorrect chosen answer is neither an
  abstention nor out of scope, and no candidate gates or routes on correctness.*
- *Deferred (§9): the operational "bona fide attempt" and scope tests.*

### S06 — Observe answer-side interventions
- **Purpose.** Observe how the generator's chosen answer behaves under interventions on the image.
- **Consumed artifacts.** Eligible-so-far Candidate Subject; the live composite Generator.
- **Input artifact(s).** Candidate Subject.
- **Produced artifacts.** Answer-side Intervention Records; observational provenance accretion.
- **Output artifact(s).** Answer-side Intervention Records.
- **Governing specification(s).** FD §§11–13, 20; BD §§4–5, 7–8, 12; PD §§4–5; DM §§3.4, 3.7.
- **Applicable ADRs.** ADR-002 (definitions, N1–N3).
- **Required invariants.** CC1, CC3, CC4, CC5, CC6, CC7, CC11; PD-A1–A3, PD-R2–R4, R7; LS-I2–I3, I6, I8;
  DM-R5–R6, M1, T1, T6; ADR2-N1–N3.
- **Preconditions.** P1–P3 passed.
- **Postconditions.** For each applied intervention, one Intervention Record recording the perturbed-
  input identity, the graded chosen-answer counterfactual reading, and control applicability where
  relevant; observational provenance accreted append-only. Records observation only — no verdict.
- **Failure routing.** None (observation stage). A non-response under an intervention is itself recorded
  as an observation, not a route.
- **Traceability obligations.** Bind every Intervention Record to the candidate identity. (DM-T1, T6.)
- *Deferred (§9): the intervention set, parameters, and perturbation method — which MUST use the exact
  baseline chosen answer (CC4), the same subject (CC7), and retain graded readings (CC5).*

### S07 — Determine P4 and Condition A
- **Purpose.** Determine whether the chosen answer is image-dependent.
- **Consumed artifacts.** Candidate Subject; observational provenance with answer-side Intervention
  Records.
- **Input artifact(s).** Observational provenance (answer-side).
- **Produced artifacts.** Observational provenance accretion containing the Condition A determination; on
  indeterminacy, an E4 route outcome for S15.
- **Output artifact(s).** Condition A verdict ∈ {image-dependent, not-image-dependent, indeterminate}.
- **Governing specification(s).** FD §13; LS §3 P4, §4 Condition A, §§5–6, §9 E4.
- **Applicable ADRs.** ADR-002 (N1–N4); ADR-006 (C1–C5).
- **Required invariants.** CC1, CC5, CC12; LS-I1–I3, I6–I8; DM-M1, M3, T1–T2; ADR2-N1–N4.
- **Preconditions.** S06 completed; answer-side Intervention Records present.
- **Postconditions.** A determinate Condition A verdict is recorded. **Indeterminate** → E4.
  **Determinately false** → the prospective S1 branch, which proceeds to S10 and may reach S12 only
  if P6 holds (Condition B is not assessed). **True** → continue through S08/S09 to S10.
- **Failure routing.** Indeterminate → **S15 with E4** (MUST NOT become S1/D1). A determinately false
  verdict is **not** a P4 failure — it selects the prospective S1 branch, still subject to P6 at S10.
- **Traceability obligations.** Record the A determination and its graded basis. (DM-T1.)
- *ADR-004: Condition A measures image-dependence of the exact emitted chosen answer regardless of
  its correctness (C4); incorrectness itself never produces E4 or any other route (C5).*
- *Deferred (§9): the Condition A criterion, which MUST concern the chosen answer (not correctness), and
  MUST distinguish a determinate negative (→S1) from indeterminacy (→E4).*

### S08 — Determine P5 evidence locatability
- **Purpose.** When Condition A holds, determine whether the evidence the answer depends on can be
  located and establish the candidate-scoped evidence-region reference used downstream.
- **Consumed artifacts.** Candidate Subject with Condition A = true; observational provenance.
- **Input artifact(s).** Observational provenance.
- **Produced artifacts.** Observational provenance accretion containing the evidence-region identity and
  localization result; on failure, an E5 route outcome for S15.
- **Output artifact(s).** Evidence-region identity (candidate-scoped, stable, audit-resolvable reference)
  (or E5).
- **Governing specification(s).** FD §14; LS §3 P5, §4 (Condition B dependency), §9 E5; DM §§3.7, T1.
- **Applicable ADRs.** ADR-002 (N1–N3).
- **Required invariants.** CC1, CC5, CC6; PD-A1–A3, PD-R4; LS-I2–I3, I6–I8; DM-M1, T1–T2; ADR2-N1–N3.
- **Preconditions.** Condition A = true.
- **Postconditions.** The evidence-region identity is established (locatable) or an E5 outcome is
  selected.
- **Failure routing.** Locatability failure → **S15 with E5** (MUST NOT become D2).
- **Traceability obligations.** Record the evidence-region identity, localization outcome, and the
  implementation-owned localization profile identifier recorded in sealed provenance. (DM-T1.)
- *Deferred (§9): the localization method. The evidence-region identity form is fixed by V1-012 as a
  candidate-scoped, stable, audit-resolvable reference; concrete representation remains an
  implementation decision. No saliency, attribution, or detector method is fixed here.*

### S09 — Observe evidence-matched rationale interventions
- **Purpose.** Observe how the generator's rationale behaves when the located evidence is altered using
  the exact evidence-region identity established by S08.
- **Consumed artifacts.** Candidate with Condition A = true and locatable evidence; the live composite
  Generator.
- **Input artifact(s).** Candidate Subject; exact evidence-region identity from S08.
- **Produced artifacts.** Rationale-side Intervention Records tied to the same evidence; observational
  provenance accretion.
- **Output artifact(s).** Rationale-side Intervention Records.
- **Governing specification(s).** FD §§11–12, 14, 17, 20; LS §4 Condition B; DM §§3.4, 3.7.
- **Applicable ADRs.** ADR-002 (definitions, N1–N3).
- **Required invariants.** CC1, CC3, CC4, CC5, CC6, CC7, CC11; PD-A1–A3, PD-R1–R4, R7; LS-I2–I3, I6, I8;
  DM-R5–R6, M1, T1, T6; ADR2-N1–N3.
- **Preconditions.** Condition A = true; evidence located (S08) with the exact evidence-region identity
  established by S08.
- **Postconditions.** For interventions on the **same** evidence the answer depends on, Intervention
  Records recording graded readings of the generator's stated visual content, using the exact baseline
  rationale and chosen answer. S09 consumes the exact S08 identity and MUST NOT silently relocalize or
  substitute it.
- **Failure routing.** None (observation stage); a non-response is recorded as an observation.
- **Traceability obligations.** Bind each Intervention Record to the candidate identity and to the
  evidence-region identity used at S08; record the implementation-owned localization profile
  identifier recorded in sealed provenance. (DM-T1, T6.)
- *Deferred (§9): the counterfactual edit method — which MUST target the located evidence, use the exact
  baseline rationale (CC4), and not substitute a gold answer or regenerated rationale.*

### S10 — Determine P6 causal license
- **Purpose.** Determine whether the controls that license a causal reading hold for this instance.
- **Consumed artifacts.** Candidate Subject; intervention and control observations.
- **Input artifact(s).** Observational provenance (interventions and controls).
- **Produced artifacts.** Observational provenance accretion containing control applicability and result;
  on failure, an E6 route outcome for S15.
- **Output artifact(s).** Control applicability/result (or E6).
- **Governing specification(s).** LS §3 P6, §9 E6; FD §§11–12; DM §§3.4, 3.7.
- **Applicable ADRs.** ADR-002 (N1–N3); ADR-006 (C1–C8).
- **Required invariants.** CC1, CC5, CC6, CC11; PD-A1–A3, PD-R2, R7; LS-I2, I6–I8; DM-M1, T1–T2, T6.
- **Preconditions.** Condition A is determinate and branch-appropriate intervention/control evidence is
  available: answer-side evidence from S06/S07 on the A-false branch; answer-side plus evidence-matched
  rationale-side evidence from S06–S09 on the A-true branch. S09 is not a precondition on the A-false
  branch. (ADR6-C4.)
- **Postconditions.** Control applicability and result are recorded per instance. If P6 holds,
  **A false** → S12 for S1 assignment; **A true** → S11 for Condition B. If P6 fails, either branch
  selects E6 for S15. (ADR6-C1–C5.)
- **Failure routing.** Control failure or another unlicensed causal reading → **S15 with E6** on either
  branch (no state; MUST NOT become D1, D2, or E4).
- **Traceability obligations.** Record the active branch, branch-appropriate evidence set, per-instance
  control applicability/result, and P6 outcome. (DM-T1–T2; ADR6-C6.)
- *Deferred (§9): the control tests and their per-instance validity (e.g. the validity of a control for a
  given question type — matrix A09).*

### S11 — Determine Condition B
- **Purpose.** Determine whether the rationale tracks the evidence the answer depends on.
- **Consumed artifacts.** Candidate with Condition A = true, locatable evidence, and licensed controls;
  observational provenance.
- **Input artifact(s).** Observational provenance (rationale-side, matched to evidence).
- **Produced artifacts.** Observational provenance accretion containing the Condition B determination.
- **Output artifact(s).** Condition B verdict ∈ {tracks, does-not-track}.
- **Governing specification(s).** FD §§14, 17–18; LS §4 Condition B, §§5–6, §8.2.
- **Applicable ADRs.** ADR-002 (N1–N4).
- **Required invariants.** CC1, CC5, CC12; PD-A1–A3, PD-R1–R4; LS-I1–I3, I6, I8; DM-M1, M3, T1;
  ADR2-N1–N4.
- **Preconditions.** Condition A = true; evidence located; controls licensed.
- **Postconditions.** A determinate Condition B verdict is recorded. **Does-not-track** → the S2 branch;
  **tracks** → the S3 branch.
- **Failure routing.** None here; an inability to determine B when its preconditions held is handled by
  the upstream P5/P6 gates (E5/E6), not by inventing a route at S11.
- **Traceability obligations.** Record the B determination and its graded basis. (DM-T1.)
- *Deferred (§9): the Condition B criterion, which MUST establish directional same-evidence tracking —
  not generic text change (matrix A08) — and MUST guard against incoherent output being counted as
  tracking. Benchmark v1 uses the fixed binary Condition-B / S1-S3 contract; any future partial
  outcome would be a MAJOR/v2 change.*

### S12 — Determine Behavioural State
- **Purpose.** Map the eligibility and Condition determinations to a single Behavioural State.
- **Consumed artifacts.** Candidate Subject; observational provenance with eligibility and A/B
  determinations.
- **Input artifact(s).** Observational provenance.
- **Produced artifacts.** Behavioural State (S1, S2, or S3).
- **Output artifact(s).** Behavioural State.
- **Governing specification(s).** LS §5, §6 decision table, §8; FD §§17–18; DM §3.5.
- **Applicable ADRs.** ADR-002 (definitions, N1–N4); ADR-006 (C1–C6).
- **Required invariants.** CC1, CC3, CC12; LS-I1–I4, I6–I8; DM-M1, M3, T1; ADR2-N1–N4.
- **Preconditions.** An eligible candidate with P6 recorded as holding, a determinate Condition A, and,
  when A holds, a determinate Condition B. No S1/S2/S3 assignment is permitted without P6.
- **Postconditions.** Exactly one state: Condition A false ⇒ **S1** (Condition B unassessed); A true and
  B does-not-track ⇒ **S2**; A true and B tracks ⇒ **S3**. D1 precedence is enforced by not assessing B
  on the S1 branch (LS §6).
- **Failure routing.** None (the routed cases have already left via S15). A state MUST NOT be produced
  for an ineligible candidate.
- **Traceability obligations.** The state is a production output *derived from* observational provenance;
  it MUST NOT be treated as an input to any upstream determination (ADR2-N2). (DM-T1.)

### S13 — Project state to Label and reason code
- **Purpose.** Project the Behavioural State to the binary benchmark Label and reason code.
- **Consumed artifacts.** Candidate Subject; observational provenance; Behavioural State.
- **Input artifact(s).** Behavioural State.
- **Produced artifacts.** Label (primary value + reason code).
- **Output artifact(s).** Label.
- **Governing specification(s).** LS §§4–8 (esp. §5.3 and §6); FD §§18, 21; DM §3.6.
- **Applicable ADRs.** ADR-002 (N1–N4).
- **Required invariants.** CC1, CC3, CC10, CC12; PD-R1–R4; LS-I1–I9; DM-M1, M3, T1, T4; ADR2-N1–N4.
- **Preconditions.** A determinate Behavioural State (S12).
- **Postconditions.** S1 → `unfaithful`/D1; S2 → `unfaithful`/D2; S3 → `faithful`/no reason. Exactly one
  primary value; reason-code coupling holds (LS-I4, I5); the Label Specification version is stamped
  (DM-T4). No correctness, plausibility, grounding, or judge signal enters the projection (LS-I2, I6).
- **Failure routing.** None.
- **Traceability obligations.** The Label binds to the provenance that justifies it (LS-I8); the label is
  a production output, never an upstream input (ADR2-N2). (DM-T1, T4.)

### S14 — Seal eligible provenance
- **Purpose.** Freeze the Interventional Provenance of a labelled candidate, folding in the
  determinations as traceability back-references.
- **Consumed artifacts.** Observational provenance; Behavioural State; Label.
- **Input artifact(s).** Observational Interventional Provenance (accreted).
- **Produced artifacts.** The **same** Interventional Provenance artifact in its **sealed** phase, with
  determination back-references.
- **Output artifact(s).** Sealed Interventional Provenance.
- **Governing specification(s).** ADR-002 (entire Decision); FD §20; LS-I8; DM §§3.7, M1, M3, T1.
- **Applicable ADRs.** ADR-002.
- **Required invariants.** CC3, CC5, CC9, CC11; LS-I8–I9; DM-M1, M3–M4, T1, T4, T6; ADR2-N1–N4.
- **Preconditions.** A Label (S13) and its Behavioural State (S12) exist for the candidate.
- **Postconditions.** Provenance is frozen; the Behavioural State, Label, and reason code appear as
  **traceability back-references** (NOT production inputs — ADR2-N1); sealing changes no value (ADR2-N4);
  the pipeline remains the **sole** producer of the artifact (ADR2-N3); the Label is reconstructible from
  the sealed provenance alone (DM-T1).
- **Failure routing.** None.
- **Traceability obligations.** The sealed provenance MUST make the verdict fully reconstructible and
  MUST record the governing specification versions (DM-T1, T4).

### S15 — Resolve and seal routed-aside candidate
- **Purpose.** Resolve an ineligible candidate to a Routed-Aside Record and seal its provenance.
- **Consumed artifacts.** Candidate Subject; observational provenance; exactly one E1–E6 outcome.
- **Input artifact(s).** Candidate Subject + the E-code outcome from S04–S10.
- **Produced artifacts.** Routed-Aside Record; the same Interventional Provenance artifact sealed with a
  route back-reference.
- **Output artifact(s).** Routed-Aside Record.
- **Governing specification(s).** LS §3, §9, I7–I8; DM §§1, 3.7–3.8, 4, M5, T2.
- **Applicable ADRs.** ADR-002 (N1–N4); ADR-003 (E1).
- **Required invariants.** CC1, CC2, CC3, CC5, CC6, CC11; LS-I2–I3, I6–I9; DM-R1–R2, M1, M4–M5, T1–T4;
  ADR2-N1–N4; ADR3-P/R.
- **Preconditions.** Exactly one E1–E6 outcome selected by an upstream gate (S04–S10).
- **Postconditions.** Exactly one Routed-Aside Record carrying the instance identity, the E-code, and
  justifying provenance; **no** Label and **no** Behavioural State. Provenance is sealed. For **E1**,
  there are **no** Intervention Records — the justifying evidence is the P1/generation outcome (ADR3).
  The record is excluded from the labelled corpus (handed to S17).
- **Failure routing.** None (this stage is the terminal routed resolution).
- **Traceability obligations.** Record which precondition failed and the evidence for it; guarantee
  no-silent-drop (CC2; DM-T2).
- *ADR-004: no E-code arises from answer incorrectness. Every Routed-Aside Record carries exactly one
  of E1–E6 produced by a P1–P6 gate; there is no correctness-specific route.*

---

## 6. Branch and precedence rules

The pipeline MUST implement exactly the branch and precedence behaviour of the Traceability Matrix §4
and LS §6:

| Branch | Required routing |
|---|---|
| P1 fail | S15 with **E1**; no Intervention Records; no state; no label. |
| P2 fail | S15 with **E2**; no state; no label. |
| P3 fail | S15 with **E3**; no state; no label. |
| P4 indeterminate | S15 with **E4**; MUST NOT become S1/D1. |
| Condition A determinately false, **P6 holds** | S12 ⇒ **S1**; S13 ⇒ `unfaithful`/**D1**; Condition B not assessed. |
| Condition A determinately false, **P6 fail** | S15 with **E6**; no state. |
| A true, P5 fail | S15 with **E5**; MUST NOT become D2. |
| A true, P6 fail | S15 with **E6**; no state. |
| A true, B does-not-track | S12 ⇒ **S2**; S13 ⇒ `unfaithful`/**D2**. |
| A true, B tracks | S12 ⇒ **S3**; S13 ⇒ `faithful`, no reason code. |

**P6 applies to every labelled state (LS §3; ADR6-C1–C5).** The causal-license control (P6) MUST hold before a
Behavioural State is assigned on **either** branch: a determinate "answer is not image-dependent" is
itself a causal reading that P6 licenses. An A-false candidate for which P6 fails routes to **E6**, not
S1/D1. (The S10 P6 gate therefore governs the A-determination generally; the pipeline MUST evaluate it on
the A-false path before S12 assigns S1.)

**Condition-B determinacy guard (LS §8.2).** The coherence/validity of the counterfactual rationale is
part of the P6 causal-license control: an incoherent, malformed, or non-bona-fide counterfactual rationale
is a P6 failure (**E6**) evaluated *before* Condition B. Consequently, once S11 is reached, Condition B is
**determinate** (tracks / does-not-track); there is no inconclusive B outcome that lacks a route, and
no-silent-drop (CC2) holds. This introduces no new route, state, or reason code.

**E-code precedence (deterministic routing).** When more than one precondition would fail, the single
E-code is assigned by **gate order P1 > P2 > P3 > P4 > P5 > P6** — the *first* failing gate determines the
routed outcome. (In particular, a candidate that both abstains and is out of scope is **E2**, not E3.)
This mirrors D1 precedence and guarantees deterministic routed-aside accounting; exactly one E-code per
routed candidate.

**D1 precedence** (LS §6) is structural: Condition B is evaluated only on the A-true path, so an
**eligible (P6-passing)** A-false candidate is always S1/D1 and is never assessed for B. An A-false
candidate that fails P6 routes E6. Each E-route is mutually exclusive with every other and with the
labelled outcomes; exactly one resolution occurs per candidate (CC2; ADR6-C2, C5).

---

## 7. Provenance lifecycle obligations

Per ADR-002, applied across S04–S15:

- **Observational phase (S04–S11).** Provenance accretes **append-only**; it contains observations and
  determinations-as-inputs only. It is the input to semantic determination (CC11).
- **Semantic determination (S12–S13).** The Behavioural State and Label are **produced from**
  observational provenance. They are production outputs; nothing consumes them as an input to their own
  or any upstream determination (CC3; ADR2-N2).
- **Sealed phase (S14/S15).** The determinations (or the E-route) are folded into the same artifact as
  **traceability back-references** (ADR2-N1). Sealing adds no production edge and changes no value
  (ADR2-N4). The pipeline is the **sole** producer of Interventional Provenance throughout (ADR2-N3).
- **Reconstructability.** Every sealed provenance MUST make its Label or route reconstructible on its own
  (LS-I8; DM-T1) and MUST carry the governing specification versions (DM-T4).

---

## 8. Pipeline boundary interfaces

### 8.1 Input contract (from S01, owned by `08`)
The pipeline requires, per Source Record: a stable source identity; the image; the question; the
options; and any source grounding annotations, with malformed or missing source material represented
**explicitly** (not silently dropped). The pipeline treats the Source Record as immutable input and
does not normalize it. (BD §12; FD §9; DM §3.1.)

### 8.2 Output handoff (to S16–S19, owned by `08`/`10`)
The pipeline delivers:

- **Labelled candidates** (Candidate Subject + sealed provenance + Behavioural State + Label) to **S16**
  for Corpus Entry assembly and split assignment. The receiver relies on: the Output Tuple being
  **complete** (guaranteed because P1 passed — CC8); the Label being separable from the predictor-visible
  Output Tuple; and provenance/margins being marked never-a-predictor-input (CC9).
- **Routed-Aside Records** to **S17** for collection into the Routed-Aside Set.

The pipeline makes **no** decision about corpus composition, splits, release format, freeze, manifest,
or evaluation views (S16–S19); it only guarantees the handed-off artifacts satisfy their invariants.
The information boundary is enforced at S18–S19 by the receiving specifications; the pipeline's
obligation is only that no incomplete tuple, provenance, generator identity, or margin is ever part of a
predictor-visible artifact it produces (CC8, CC9).

---

## 9. Deferred to implementation

The following remain **implementation decisions**. Each MUST satisfy the cross-cutting invariants (§4)
and the postconditions of its stage; none may change any benchmark semantic.

- The **intervention set, parameters, and perturbation/edit methods** (S06, S09).
- The **evidence-localization method** and the concrete representation/serialization of the evidence-
  region identity (coordinates, masks, segments, cardinality, and similar forms).
- The **control tests** and their per-instance validity (S10).
- The **operational criteria and thresholds** for P1–P6 and for Conditions A and B, including the P1
  completeness test, the P2 "bona fide attempt" and P3 scope tests, the determinate-vs-indeterminate
  boundary for Condition A (S07), and the same-evidence tracking criterion for Condition B (S11).
- The **graded-reading (margin) definitions** retained in provenance (all observation stages).
- All **serialization and schemas** of every artifact.

This document specifies *what each stage must determine and guarantee*; it does not specify *how*.

---

## 10. Open dependencies

The pipeline's behaviour is specified conditionally where an upstream policy is open. These MUST be
resolved by ADR before conformance can be claimed for the affected stages:

- **LS Q1 — correctness eligibility. Resolved by ADR-004 (accepted 2026-07-02).** Answer correctness
  does not gate eligibility and never routes a candidate (CC1; LS §3). The P-gates (S05, S07, S15)
  operate identically for correct and incorrect chosen answers; no conditional conformance remains
  for this item.
- **LS Q3 — Condition B granularity.** Resolved for Benchmark v1 by the fixed binary
  Condition-B / S1-S3 contract; any future partial outcome would change the state space and be a
  MAJOR/v2 matter.
- **LS Q4 — composite-generator validity.** Resolved by ADR-005 (accepted 2026-07-02): a composite
  generator is one subject, so S02–S03 and every observation stage bind the same composite subject
  (matrix A01).
- **DM Q1 — baseline-output identity.** How the exact baseline Output Tuple is designated affects S02 and
  CC4 (matrix A02).
- **DM Q4 — evidence-region identity.** Resolved by V1-012 (accepted 2026-07-03): the located evidence
  uses the candidate-scoped, stable, audit-resolvable reference defined by the accepted interface
  contract; concrete representation remains in the RIP.

The Traceability Matrix §8 assumptions A01–A16 enumerate the corresponding implementation assumptions
that MUST NOT be treated as settled operational rules until resolved.

---

## 11. Conformance

A pipeline implementation is **conformant** iff, for every Candidate Subject:

1. it satisfies every stage's preconditions, postconditions, and failure routing (§5, §6);
2. it upholds all cross-cutting invariants (§4) and the provenance lifecycle obligations (§7);
3. it resolves the candidate exactly once, with no silent drop (CC2);
4. it produces sealed provenance from which the Label or route is reconstructible (DM-T1), carrying the
   governing specification versions (DM-T4);
5. it never allows an incomplete Output Tuple, provenance, generator identity, or margin to become part
   of a predictor-visible artifact (CC8, CC9).

Conformance is a property of the **behaviour** specified here, not of any method chosen in §9.
Reproducibility follows the corpus guarantee (Benchmark Design §10): a released corpus is re-derivable
on a pinned reference environment from its sealed provenance and manifest, not necessarily byte-identical
across environments.

---

*This document specifies the required behaviour of benchmark construction. It transforms well-defined
artifacts (Data Model), implements the label semantics (Label Specification) exactly, respects the
provenance lifecycle (ADR-002) and the incomplete-candidate lifecycle (ADR-003), and defers every method
and threshold to implementation — so that independent teams can build a conformant pipeline without
changing benchmark semantics.*
