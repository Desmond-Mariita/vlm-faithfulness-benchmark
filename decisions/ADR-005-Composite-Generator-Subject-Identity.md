---
Status: Accepted
Date: 2026-07-02
Accepted: 2026-07-02
Supersedes: —
Superseded-by: —
Deprecated-by: —
Charter-clause: — (Q4 subject-identity policy; no change to label meaning)
Related:
  - docs/00_Benchmark_Charter.md
  - docs/05_Formal_Definitions.md
  - docs/06_Label_Specification.md
  - docs/06a_Benchmark_Data_Model.md
  - docs/07_Label_Generation_Pipeline.md
  - docs/08_Dataset_Specification.md
  - docs/10_Evaluation_Protocol.md
  - reviews/codex/specification_phase_audit.md
  - docs/design/Benchmark_v1.0_Release_Plan.md
---

# ADR-005: Composite-Generator Subject Identity

> **Decision status.** This is the V1-005 decision package submitted to the Benchmark Maintainer. It
> authorizes nothing while `Status: Proposed`. The recommendation in §4 became binding when the BM
> accepted this ADR.

## 1. Context

The benchmark's formal vocabulary already defines a `generator` as the subject every `label` is a fact
about, and it explicitly allows a generator to be implemented as a composite system composed of several
models, stages, or checkpoints (Formal Definitions §1). The current data model and pipeline likewise
assume a stable instance identity formed from the composite generator identity and the source record
identity (Data Model R1–R3; Pipeline CC6).

What remains open is not whether a composite implementation exists, but whether the benchmark treats the
answer-producing and rationale-producing components of the thesis-style two-checkpoint generator as one
valid subject for Q4. That choice determines whether S02–S15 bind one subject identity across the full
labeling chain or whether the benchmark must split the generator into multiple subjects or phases.

This is a semantic and ontological decision. It must be decided before implementation of the generation
and observation stages can claim conformance for composite generators (review finding SPA-002; release
plan work package V1-005).

The decision changes no meaning of `faithful`, `unfaithful`, S1–S3, D1, D2, or the output-only
information boundary. It decides only how the benchmark identifies the single generator subject whose
behaviour is being measured when that subject is implemented as a composite system.

## 2. Decision drivers

- **Subject integrity.** The benchmark must identify one subject per generator/source pair, not an
  implementation-dependent sequence of partial subjects.
- **Traceability.** Every intervention, counterfactual, provenance record, and label must bind to the
  same subject identity throughout the construction chain.
- **Composite portability.** The benchmark should not assume a single monolithic model if a composite
  system can still behave as one generator subject.
- **No proxy split.** Separating the answer-producing and rationale-producing components into distinct
  subjects would change the object under test and risk turning an implementation detail into ontology.
- **Implementation fidelity.** The thesis-style two-checkpoint generator is the motivating case: the
  benchmark needs one rule that can be implemented consistently across systems with multiple internal
  components.
- **Compatibility.** The choice must stay consistent with the existing instance-identity and provenance
  assumptions already present in `06a` and `07`.

## 3. Alternatives considered

### Alternative A — Each component is a separate subject

The answer-producing component and rationale-producing component are treated as distinct benchmark
subjects, each with its own identity and label path.

**Advantages**

- Mirrors the internal separation of a two-checkpoint implementation.
- Makes component-level attribution explicit.

**Costs and risks**

- Changes the benchmark subject from one generator to multiple subjects.
- Breaks the current one-instance-per-generator/source pair model.
- Splits S02–S15 across multiple subjects, creating an ontology the current specs do not own.
- Makes a single label no longer clearly attributable to one generator subject.

### Alternative B — A composite generator is one subject for the benchmark (recommended)

A generator implemented as multiple components, models, stages, or checkpoints is still one benchmark
subject if those components jointly produce the chosen answer and rationale for a single instance. The
benchmark binds one composite generator identity to the instance and treats the internal components as
part of that identity.

**Advantages**

- Preserves the existing formal definition that a generator may be composite.
- Keeps one instance identity per generator/source pair.
- Allows a single label path, provenance trail, and intervention chain across the whole generator.
- Matches the current data model and pipeline assumptions.
- Avoids silently redefining the subject when implementation architecture changes.

**Costs and risks**

- Composite identity must be recorded carefully enough that different component/configuration sets are
  distinguishable.
- Internal component changes that alter the composite identity may increase the number of distinct
  instances.

### Alternative C — Composite identity is implementation-defined and not fixed by the benchmark

The benchmark treats the generator as a subject, but leaves the exact composite identity constituents to
implementation.

**Advantages**

- Reduces the amount of identity detail the benchmark must name.
- Leaves internal modeling latitude to implementers.

**Costs and risks**

- Recreates the subject-identity ambiguity flagged in SPA-002.
- Makes S02/S03 binding and provenance reconstruction inconsistent across implementations.
- Permits incompatible implementations to disagree about the unit being measured.

## 4. Proposed decision

**Adopt Alternative B: a composite generator is one benchmark subject in Benchmark v1.**

Normative consequences upon acceptance:

- **C1 — One subject, one instance identity.** The benchmark treats a composite generator as one valid
  generator subject. The instance identity remains the pair `(composite generator identity, source record
  identity)`.
- **C2 — Composite identity is complete.** The composite generator identity MUST identify every
  component and configuration that jointly produce the chosen answer and rationale for the instance.
- **C3 — Same subject across stages.** S02 through S15 MUST bind to the same composite generator subject
  across generation, intervention, provenance accretion, state determination, label projection, and
  routing.
- **C4 — No component splitting.** The benchmark MUST NOT split the answer-producing and rationale-
  producing components into separate benchmark subjects for the same instance.
- **C5 — Traceability binding.** The composite generator identity MUST be recorded in provenance and MUST
  remain withheld from predictors, while remaining reconstructible for audit and release.
- **C6 — Implementation independence preserved.** The benchmark does not prescribe how a composite
  generator is internally assembled; it prescribes only that the assembled whole is the subject.
- **C7 — No meaning change.** This decision changes no label meaning, behavioural state meaning,
  intervention meaning, or boundary meaning.

## 5. Population and artifact impact

| Area | Effect under the proposed decision |
|---|---|
| Candidate population | Every `(composite generator, source record)` pair remains one candidate subject |
| Subject identity | The generator identity includes all components and configuration needed to reproduce the emitted answer and rationale |
| Intervention chain | All interventions apply to the same composite subject across answer and rationale observations |
| Behavioural State | S1–S3 are determined for the whole composite generator subject, not per component |
| Label | One label per composite-subject instance; no component-level labels are introduced |
| Provenance | The composite identity is recorded once and carried through the provenance trail |
| Corpus composition | Unchanged except that composite generators are now explicitly confirmed as valid subjects |
| Evaluation | Scoring continues to consume the released instance output tuple, not internal component identities |

## 6. Compatibility and versioning

This decision closes an explicitly open pre-v1 subject-identity policy. It changes no label meaning,
behavioural state meaning, output-boundary meaning, or corpus-release meaning. No released corpus exists
whose membership would change.

It is therefore a pre-freeze subject-identity decision within Benchmark v1, not a Charter §4 v2 change.
It requires this ADR because subject identity is semantically material and V1-005 mandates the decision
record. Subsequent reversal after release would require a new ADR, a specification-version assessment,
and a new corpus version at minimum; it could not mutate an existing corpus.

## 7. Required amendments upon acceptance

No amendment below is authorized while this ADR remains Proposed.

1. **Label Specification (`docs/06_Label_Specification.md`)**
   - §14 Q4: mark resolved by ADR-005 and state that a composite generator is one valid subject for
     Benchmark v1.
2. **Benchmark Data Model (`docs/06a_Benchmark_Data_Model.md`)**
   - §3.3 / R1–R3 / T1: clarify that the composite generator identity is the identity of the whole
     generator subject and must record every component/configuration needed for reconstruction.
   - §6: retain the pair identity `(composite generator identity, source record identity)` with no
     component-level split.
3. **Label Generation Pipeline (`docs/07_Label_Generation_Pipeline.md`)**
   - S02/S03 and CC6/CC7: clarify that the live composite generator subject is the one bound across the
     entire pipeline and that the same subject performs both answer and rationale observation.
   - §10: close LS Q4 and remove conditional conformance wording.
4. **Dataset Specification (`docs/08_Dataset_Specification.md`)**
   - Remove LS Q4 from open dependencies and ensure corpus-entry provenance references the same composite
     subject identity.
5. **Evaluation Protocol (`docs/10_Evaluation_Protocol.md`)**
   - L-7/open-policy references: remove Q4 as open and reference ADR-005.
6. **Supporting traceability and registries**
   - Update current open-question/traceability references during V1-027/V1-030; preserve historical
     reviews and inventories as dated evidence rather than rewriting them.

## 8. Consequences

**Positive**

- The benchmark has one stable subject per generator/source pair, even when the generator is internally
  composite.
- Answer-side and rationale-side evidence stay bound to the same measured subject.
- Existing provenance and identity assumptions remain intact and implementation-independent.
- Independent implementers can support multi-component generators without inventing a new benchmark
  ontology.

**Negative / accepted costs**

- Composite identity must be recorded precisely enough to distinguish materially different component
  configurations.
- Internal architecture changes that alter the composite identity will create new instance identities.

**Risks controlled by existing specifications**

- R1–R3 and T1 in the Data Model require full identity reconstruction.
- CC6 and CC7 require identity binding across the pipeline.
- CC4 and ADR-003 protect exact baseline output handling.
- Evaluation and corpus assembly remain subject to the output-only boundary.

## 9. Links

- [Benchmark Charter](../docs/00_Benchmark_Charter.md) §§1–4
- [Formal Definitions](../docs/05_Formal_Definitions.md) §1
- [Label Specification](../docs/06_Label_Specification.md) §14 Q4
- [Benchmark Data Model](../docs/06a_Benchmark_Data_Model.md) R1–R3, R6, T1
- [Label Generation Pipeline](../docs/07_Label_Generation_Pipeline.md) CC6–CC7, §10
- [Dataset Specification](../docs/08_Dataset_Specification.md) §19
- [Evaluation Protocol](../docs/10_Evaluation_Protocol.md) L-7
- [Specification Synchronization Report](../docs/design/Specification_Synchronization_Report.md) SPA-002
- [Execution and Release Plan](../docs/design/Benchmark_v1.0_Release_Plan.md) V1-005/V1-010
