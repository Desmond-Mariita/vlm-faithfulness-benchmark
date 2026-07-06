---
Title: Vision
Status: Accepted
Benchmark-Version: v1.0
Last-reviewed: 2026-07-01
Related:
  - docs/00_Benchmark_Charter.md
  - docs/01_Benchmark_Design.md
  - docs/03_Problem_Definition.md
  - docs/05_Formal_Definitions.md
---

# Vision

## The problem
Vision-language models emit a chain-of-thought rationale before answering, and readers treat that
text as the reason for the decision. But a fluent, visually specific rationale need not be
*faithful*: it can be a story from language priors rather than from the visual evidence the answer
depends on. A model right for the wrong reason scores like one that is genuinely grounded.

## The claim we operationalize
Faithfulness is a **causal property of the generating model** — established by intervening on that
model and seeing whether its answer and its rationale depend on the image. That test is too costly
to run everywhere. This benchmark predicts its outcome **from the static output alone**, with the
generator out of reach. It is a cheap surrogate for the intervention.

## Vision vs Charter
This document explains **why** we are building the benchmark and what success and stopping look
like. It is distinct from [`docs/00_Benchmark_Charter.md`](docs/00_Benchmark_Charter.md), which
fixes **what the benchmark permanently is and will never be**. When the two are in tension, the
Charter's boundaries win; the Vision may evolve, the Charter changes only with extraordinary
justification.

## Core principle
**Ground truth is defined by specifications, not by implementation.**

## What success looks like
- A static, pre-labelled corpus whose label is reproducible from a manifest on a pinned environment.
- A hard core where a strong plausibility judge lands near chance.
- Held-out splits (unseen generators, question types, dataset) that report how far faithfulness
  signatures travel.

## Explicit non-goals
- **Not** a plausibility or entailment benchmark.
- **Not** a claim about model *internals* — behavioural, necessary-condition faithfulness only.
- **Not** an answer-accuracy leaderboard.
- **Not** a software product.

## Construct honesty
The word *faithfulness* carries exactly the epistemic weight the source thesis was permitted to
give it, and no more. Every document that touches the label restates this scope at its point of
definition. See [`docs/05_Formal_Definitions.md`](docs/05_Formal_Definitions.md).

## What would make us stop
If the "faithful" class cannot be manufactured with discriminative variance, or if faithfulness
signatures prove entirely generator-specific, the project re-scopes rather than ships a
mislabelled corpus. These are named as abandonment conditions in the
[Charter](docs/00_Benchmark_Charter.md) §6.
