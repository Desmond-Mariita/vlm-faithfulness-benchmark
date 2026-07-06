---
Status: Accepted
Date: 2026-07-02
Accepted: 2026-07-02
Supersedes: —
Superseded-by: —
Deprecated-by: —
Charter-clause: — (v1 eligibility policy; no change to label meaning)
Related:
  - docs/00_Benchmark_Charter.md
  - docs/05_Formal_Definitions.md
  - docs/06_Label_Specification.md
  - docs/06a_Benchmark_Data_Model.md
  - docs/07_Label_Generation_Pipeline.md
  - docs/08_Dataset_Specification.md
  - docs/10_Evaluation_Protocol.md
  - reviews/codex/specification_phase_audit.md
  - reviews/gemini/specification_phase_conceptual_review.md
  - docs/design/Benchmark_v1.0_Release_Plan.md
---

# ADR-004: Answer-Correctness Eligibility

> **Decision status.** This is the V1-004 decision package submitted to the Benchmark Maintainer. It
> authorizes nothing while `Status: Proposed`. The recommendation in §4 becomes binding only if the BM
> accepts this ADR.

## 1. Context

The benchmark label is a behavioural, necessary-condition faithfulness verdict about a generator's
`chosen answer` and `rationale` under intervention. The chosen answer is explicitly distinct from a
source dataset's gold or correct answer (Formal Definitions §5), and correctness MUST NOT determine the
primary label or reason code (Label Specification I6).

The specifications nevertheless leave one population-level question open (Label Specification §14
Q1): must the chosen answer be correct on the unperturbed image before the instance is eligible for a
faithfulness label? The legacy thesis conditioned its answer-side analysis on correctness, while the
benchmark construct can in principle ask whether a generator's rationale faithfully reflects the visual
evidence for an incorrect answer.

This is not an implementation default. The choice changes which `(generator, source record)` pairs enter
the labelled population, affects routed-aside accounting and split distributions, and changes the
interpretation of every reported result. It must be decided before eligibility, corpus assembly, or the
evaluation protocol can claim conformance (review finding SPA-001; release-plan work package V1-004).

The decision changes no meaning of `faithful`, `unfaithful`, S1–S3, D1, or D2. It decides only whether
answer correctness restricts the population on which those existing meanings are applied.

## 2. Decision drivers

- **Construct fidelity.** Faithfulness concerns whether the rationale reflects the evidence the
  generator's chosen answer used, not whether that answer matches a dataset key.
- **No correctness proxy.** Correctness must never enter Conditions A/B, state determination, label
  projection, or reason-code assignment (Label Specification I6; Pipeline CC1/CC4).
- **Population honesty.** Excluding incorrect answers can create selection bias and conceal whether
  faithfulness differs by correctness.
- **Causal decidability.** Some incorrect answers may lack locatable evidence or a licensed causal
  reading; existing P5/P6 and E5/E6 routes already handle those cases.
- **Cross-dataset portability.** The benchmark should not require every source dataset to provide a
  gold answer unless that information is genuinely necessary to define the construct.
- **Traceability.** If correctness is recorded, its role and access class must be explicit so it cannot
  leak into label production or predictor input.
- **Comparability.** The decision must yield one stable v1 population rule rather than an implicit
  per-dataset or per-generator choice.

## 3. Alternatives considered

### Alternative A — Correctness is an eligibility gate

Only candidates whose chosen answer matches the source reference answer may receive a label. Incorrect
answers resolve without a behavioural state or label.

**Advantages**

- Closest to the legacy thesis's conditioned-on-correctness analysis.
- Avoids cases where an incorrect answer's causal evidence is difficult to interpret.
- Produces a population focused on explanations accompanying successful task behavior.

**Costs and risks**

- Faithful-but-incorrect reasoning becomes unmeasurable even though it is coherent under the benchmark's
  behavioural construct.
- Requires a correctness-specific precondition and deterministic route. Reusing E3, E5, or E6 would
  silently change their meanings; adding a new P/E code expands the eligibility taxonomy.
- Requires source datasets to expose a compatible authoritative answer key and makes corpus membership
  depend on it.
- Conditions the population on generator performance, potentially confounding generator and dataset
  comparisons and hiding correctness/faithfulness interactions.
- Risks readers interpreting the benchmark as restricted to correct-answer explanations, narrowing the
  construct for convenience rather than necessity.

### Alternative B — Correctness does not gate eligibility (recommended)

A candidate may receive a label whether its chosen answer is correct or incorrect, provided the existing
P1–P6 preconditions hold. Correctness, when an authoritative source answer is available, is retained only
for audit and stratified analysis. It never determines a route, Condition A/B, state, label, or reason
code.

**Advantages**

- Matches the construct directly: the target is fidelity to the generator's actual evidence, not task
  success.
- Preserves the existing P1–P6 and E1–E6 taxonomies without inventing a correctness route.
- Makes faithful-but-incorrect and unfaithful-but-correct behavior observable rather than selecting one
  away.
- Supports datasets without a compatible gold answer, improving portability.
- Existing P5/P6 routes already exclude cases whose evidence or causal interpretation is not
  determinable; correctness need not proxy those gates.
- Enables correctness-stratified reporting to expose rather than conceal correlations.

**Costs and risks**

- Evidence localization and controls may fail more often for incorrect answers, increasing E5/E6 rates.
- Split and hard-core composition must be monitored so correctness does not become an unintended label
  proxy.
- Results must clearly state that a `faithful` label does not mean a correct answer.

### Alternative C — Correctness-stratified dual primary populations

Label all P1–P6-eligible candidates, but define separate correct-answer and incorrect-answer benchmark
populations with separate primary results.

**Advantages**

- Preserves both populations and makes their distinction prominent.
- Avoids hiding correctness-conditioned behavior.

**Costs and risks**

- Creates two headline tasks and weakens the single benchmark contract.
- Makes the primary endpoint and floor/transfer comparisons conditional on population-specific support.
- Adds complexity without improving label validity; stratified secondary reporting under Alternative B
  provides the same diagnostic information.

### Alternative D — Label all candidates, then exclude incorrect answers during corpus assembly

Correctness does not affect semantic eligibility, but the Dataset Specification admits only correct
answers into the released corpus.

**Advantages**

- Keeps label generation conceptually separate from release composition.
- Allows internal analysis of incorrect-answer labels.

**Costs and risks**

- Produces a valid label and then discards it for a correctness-based corpus policy, recreating the same
  selection bias downstream.
- Complicates population reconciliation and the meaning of the released benchmark without a scientific
  benefit over Alternative A.
- Makes the corpus, rather than the label standard, silently narrow the construct's evaluated population.

## 4. Proposed decision

**Adopt Alternative B: answer correctness does not gate eligibility in Benchmark v1.**

Normative consequences upon acceptance:

- **C1 — No correctness gate.** Correctness MUST NOT be added to P1–P6 and MUST NOT create or select an
  E1–E6 route. A candidate is eligible exactly when the existing P1–P6 preconditions hold.
- **C2 — Incorrect answers remain valid subjects.** An incorrect chosen answer MAY receive S1, S2, or
  S3 and the corresponding existing label projection when the existing preconditions are satisfied.
- **C3 — No label-path use.** Correctness MUST NOT determine, adjust, override, calibrate, or break ties
  for Condition A, Condition B, Behavioural State, Label, or reason code.
- **C4 — Exact chosen answer remains the subject.** Every probe continues to use the generator's exact
  chosen answer; a gold answer MUST NOT be substituted (Pipeline CC4).
- **C5 — Existing determinacy routes govern.** If evidence for an incorrect answer cannot be located,
  the candidate routes E5; if the causal reading is unlicensed, it routes E6. Those outcomes arise from
  P5/P6, not from incorrectness itself.
- **C6 — Analysis-only correctness.** Where a source exposes an authoritative answer key and
  correctness is recorded, it is construction/audit and evaluation-stratification information. It is
  not part of the predictor's Output Tuple or a prediction-time feature.
- **C7 — Reporting.** Where correctness is recorded and cell support permits, evaluation SHOULD report
  correctness-stratified measurements under Evaluation Protocol C-5. If correctness is unavailable, its
  absence changes neither eligibility nor conformance.

## 5. Population and artifact impact

| Area | Effect under the proposed decision |
|---|---|
| Candidate population | Every generated candidate remains governed by P1–P6 regardless of correctness |
| Labelled population | Includes correct and incorrect chosen answers that pass P1–P6 |
| Routed-aside population | No correctness-specific route; only existing E1–E6 outcomes |
| Condition A | Measures dependence of the exact chosen answer, not agreement with a gold answer |
| Condition B | Measures tracking of the evidence used by that chosen answer |
| Output Tuple | Unchanged; no gold answer or correctness field is added to predictor input |
| Provenance/audit | MAY record source-reference correctness when available, separately from label determinants |
| Corpus composition | Must not silently filter labelled candidates by correctness; any future restriction requires classification and explicit policy |
| Evaluation | C-5 correctness slices remain conditional on correctness being recorded and adequate support |
| Cross-dataset use | A source can participate without correctness metadata if all other source and pipeline contracts hold |

## 6. Compatibility and versioning

This decision closes an explicitly open pre-v1 eligibility policy. It changes no label meaning,
behavioural state, label value, reason code, intervention basis, output-only information boundary, or
construct scope. No released corpus exists whose membership would change.

It is therefore a pre-freeze eligibility-policy decision within Benchmark v1, not a Charter §4 v2
change. It requires this ADR because population membership is semantically material and V1-004 mandates
the decision record. Subsequent reversal after release would require a new ADR, a specification-version
assessment, and a new corpus version at minimum; it could not mutate an existing corpus.

## 7. Required amendments upon acceptance

No amendment below is authorized while this ADR remains Proposed.

1. **Label Specification (`docs/06_Label_Specification.md`)**
   - §3: state that correctness is not an eligibility precondition.
   - I6: remove the unresolved allowance for correctness to act as eligibility; retain analysis-only use.
   - §14 Q1: mark resolved by ADR-004 and point to the decision.
2. **Label Generation Pipeline (`docs/07_Label_Generation_Pipeline.md`)**
   - CC1 and affected S05/S07/S15 text: state explicitly that correctness never gates or routes a
     candidate and that Condition A concerns the exact chosen answer.
   - §10: close LS Q1 and remove conditional conformance wording.
3. **Dataset Specification (`docs/08_Dataset_Specification.md`)**
   - Remove LS Q1 from open dependencies.
   - State that corpus assembly does not filter labelled candidates by correctness and that optional
     correctness metadata is not predictor-visible.
4. **Evaluation Protocol (`docs/10_Evaluation_Protocol.md`)**
   - C-5: retain conditional correctness slicing but remove the branch for a correctness-conditioned
     corpus.
   - L-7/open-policy references: remove Q1 as open and reference ADR-004.
5. **Benchmark Data Model (`docs/06a_Benchmark_Data_Model.md`)**
   - Clarify, only if needed for cross-document consistency, that correctness is not part of instance
     identity, eligibility, Behavioural State, or Label and is optional audit/analysis information.
     This MUST NOT introduce a predictor-visible field or new benchmark artifact.
6. **Supporting traceability and registries**
   - Update current open-question/traceability references during V1-026/V1-027; preserve historical
     reviews and inventories as dated evidence rather than rewriting them.

## 8. Consequences

**Positive**

- The labelled population aligns with the benchmark's stated construct rather than legacy accuracy
  conditioning.
- The existing eligibility and routing ontology remains intact.
- Correctness/faithfulness interaction becomes measurable and reportable.
- Dataset portability improves because correctness metadata is optional.

**Negative / accepted costs**

- More candidates may route E5/E6 when an incorrect answer's evidence is not recoverably localizable or
  causally licensed.
- Corpus validation must inspect label/correctness association and support counts when correctness exists.
- Documentation must repeatedly prevent readers from interpreting `faithful` as `correct`.

**Risks controlled by existing specifications**

- P5/E5 controls evidence locatability.
- P6/E6 controls causal-license validity.
- I6 and CC1 prohibit correctness from entering the verdict.
- Evaluation C-5 exposes correctness correlations when data permits.
- Dataset and Assurance distribution checks detect degenerate or proxy-heavy cells.

## 9. Links

- [Benchmark Charter](../docs/00_Benchmark_Charter.md) §§1–4
- [Formal Definitions](../docs/05_Formal_Definitions.md) §5
- [Label Specification](../docs/06_Label_Specification.md) §3, I6, §14 Q1
- [Label Generation Pipeline](../docs/07_Label_Generation_Pipeline.md) CC1, CC4, §10
- [Dataset Specification](../docs/08_Dataset_Specification.md) §19
- [Evaluation Protocol](../docs/10_Evaluation_Protocol.md) C-5, L-7
- [Specification Phase Audit](../reviews/codex/specification_phase_audit.md) SPA-001
- [Conceptual Review](../reviews/gemini/specification_phase_conceptual_review.md) OPEN-Q1
- [Execution and Release Plan](../docs/design/Benchmark_v1.0_Release_Plan.md) V1-004/V1-009
