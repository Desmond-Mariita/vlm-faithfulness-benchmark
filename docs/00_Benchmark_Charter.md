---
Title: Benchmark Charter
Status: Accepted
Benchmark-Version: v1.0
Last-reviewed: 2026-07-01
Related:
  - VISION.md
  - docs/01_Benchmark_Design.md
  - docs/05_Formal_Definitions.md
  - docs/06_Label_Specification.md
  - docs/11_Benchmark_Assurance.md
---

# Benchmark Charter

*The identity and boundaries of the benchmark. This is the most stable document in the
repository. It does not describe how the benchmark works — the specifications do that. It
describes what the benchmark **is**, what it **is not**, and the conditions under which it may
grow, split, or end. It should remain valid even if every dataset, model, script, and metric
changes. Amending it requires the extraordinary justification defined in §5. Read it first.*

## 1. What this benchmark is fundamentally trying to become
A static, reusable, **causally grounded** measurement of whether a vision-language model's
chain-of-thought rationale is *faithful* to the visual evidence its answer depends on —
recoverable from the model's **output alone**, without access to the model that produced it.

Its enduring identity is a **faithfulness-diagnosis resource** whose ground truth is set by
intervention on the generating model and whose label is a **published definition**, not a
pipeline artifact. It aspires to be a reference benchmark for output-only faithfulness
prediction, portable across multiple-choice VQA-with-rationale datasets and across generators.

## 2. What it will intentionally never become
- **Never** a plausibility, coherence, or entailment benchmark relabelled as "faithfulness."
- **Never** a benchmark whose labels are set by a judge's priors — no LLM/NLI/entailment judge
  in the label path, ever.
- **Never** a claim about model *internals* or mechanisms. "Faithful" here is the behavioural,
  necessary-condition sense and nothing stronger.
- **Never** an answer-accuracy leaderboard, or a general-purpose VLM evaluation suite.
- **Never** a software product with uptime or support obligations.
- **Never** a corpus that redistributes data it has no right to redistribute.

## 3. Under what circumstances the benchmark should expand
Expansion is warranted only when it **deepens the same construct** without changing its meaning:
more generators, more MC-VQA-with-rationale datasets, additional question types, further
held-out splits, additional baselines or reported metrics — *provided the label definition and
its causal-intervention basis are unchanged and comparability with existing corpora is
preserved.* Growth that leaves existing labels meaning the same thing is expansion. Growth that
would change what an existing label means is not expansion; it is a new benchmark (§4).

## 4. When a new idea becomes Benchmark v2 rather than a change to v1
The test is a single question: **would existing labels change meaning?**

A change is **v2 — a new benchmark** if it alters any of:
- the definition of the label;
- the causal-intervention basis of the ground truth;
- the output-only information bound (what the predictor is and is not given);
- the construct scope (behavioural, necessary-condition faithfulness).

A change is a **v1 amendment** if it adds data, generators, splits, baselines, or metrics
**without** redefining the label. When in doubt, it is v2: preserving the comparability of
released corpora outranks the convenience of amending in place.

## 5. Decisions requiring extraordinary justification
Each of the following is presumed out of bounds. Making one requires a superseding ADR that
names the specific Charter clause it touches and argues the case explicitly; absent that, the
decision may not be taken:
- introducing any model or judge output into the **label path**;
- weakening the **no-redistribution** or **provenance/reproducibility** guarantees;
- changing the **label definition** or the **intervention basis** (also triggers §4);
- widening the **construct** beyond behavioural, necessary-condition faithfulness;
- shipping a corpus whose reproducibility manifest is incomplete.

## 6. What would cause abandonment or fundamental re-scope
The honest response to any of the following is a documented re-scope or a wind-down — never a
mislabelled release:
- the **faithful** class cannot be manufactured with discriminative variance, and no edit design
  restores it (the viability gate fails terminally);
- faithfulness signatures prove **entirely generator-specific**, so the output-only prediction
  task is ill-posed;
- the label proves **inseparable from plausibility/grounding** above the floor — nothing is left
  to learn;
- licensing makes **any** reproducible public corpus impossible.

## 7. Stability
This Charter outlives implementation. If every script, dataset, model, and metric were replaced,
this document should still describe the project. Amendments are rare, ADR-backed, dated, and
themselves subject to §5.
