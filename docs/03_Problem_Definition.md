---
Title: Problem Definition
Status: Accepted
Benchmark-Version: v1.0
Last-reviewed: 2026-07-01
Related:
  - docs/00_Benchmark_Charter.md
  - docs/01_Benchmark_Design.md
  - docs/05_Formal_Definitions.md
  - docs/06_Label_Specification.md
  - docs/07_Label_Generation_Pipeline.md
  - VISION.md
---

# Problem Definition

*This document defines the problem the benchmark measures. It answers one question: **what problem
exists in the current evaluation of vision-language model rationales that this benchmark
addresses?** It is written to remain valid even if every dataset, model, threshold, and line of
code is later replaced.*

> **What this document is not.** It is not a literature review — it states the problem, not the
> history of who found what. It is not the [Benchmark Design](01_Benchmark_Design.md), which
> describes *how* the benchmark works. It is not the [Formal Definitions](05_Formal_Definitions.md),
> which fix the meanings of the technical terms used below. It defines no datasets, interventions,
> labels, thresholds, or the terms *faithfulness*, *grounding*, and *evidence*; those belong to the
> documents named in the margins.

> **On terminology.** Several words below carry a precise technical meaning this document does not
> settle — among them *faithfulness*, *grounding*, *evidence*, *intervention*, and *label*. They are
> used here only intuitively, to state the problem; their **authoritative definitions belong to
> [Formal Definitions](05_Formal_Definitions.md)** (and, for the label, to
> [Label Specification](06_Label_Specification.md); for interventions, to
> [Label Generation Pipeline](07_Label_Generation_Pipeline.md)). Where such a term first appears,
> the pointer is repeated.

> **On observations versus assumptions.** This document is careful to separate two kinds of claim.
> An **observation** is something taken as empirically established — a fact about how current models
> and current evaluations behave, whose evidence lives in the project's references and the source
> thesis, not in this document. An **assumption** is a modeling choice the benchmark *elects* to
> make; it could have been made differently. Observations are marked *(observation)*; the
> benchmark's assumptions are gathered, and marked, in §7 and §8. The distinction matters because
> the benchmark's legitimacy rests on building only on observations and on assumptions it states out
> loud.

---

## 1. The problem

Vision-language models increasingly answer a visual question by first producing a chain-of-thought
rationale — a passage of text that reads as the reason for the answer. Readers, downstream systems,
and auditors treat that passage as an account of *why* the model answered as it did.

The problem is that current evaluation cannot tell whether that account is true of the model.
Existing measures report whether the **answer** is correct and whether the **rationale** is a good
piece of text — fluent, coherent, consistent with the image, close to a reference. None of them
reports whether the rationale is *faithful*: whether the reason it states is the reason the model's
answer actually depended on. *(The term `faithfulness` is defined authoritatively in
[Formal Definitions](05_Formal_Definitions.md); here it names, intuitively, the property "the stated
reason tracks the visual evidence the answer rested on.")*

Concretely, the gap has two faces:

- A model that is **right for the wrong reason** — correct answer, rationale drawn from language
  priors rather than from the image — scores exactly like a model that is genuinely grounded.
  Current evaluation is blind to the difference *(observation)*.
- The only account of faithfulness anyone trusts is a **causal one** — disturb what the model sees
  and watch whether its answer and its stated reason move accordingly. That account is expensive and
  requires the model in hand, so it is never run at the scale of ordinary evaluation *(observation)*.

The benchmark addresses this gap by turning the expensive causal account into a **static, reusable
measurement target**: a corpus in which the causal verdict has already been established, so that the
open question becomes *whether that verdict can be recovered from a model's output alone*. The
problem the benchmark measures is therefore not "is this rationale good text?" but "can unfaithful
reasoning be detected without re-running the model?"

---

## 2. Why existing evaluation methods fail

Existing methods fall into two families, and each fails for a structural reason, not a fixable one.

**Answer-accuracy evaluation.** It scores the answer and is silent about the reasoning. A correct
answer produced for a spurious reason is indistinguishable from a correct answer that is genuinely
grounded *(observation)*. Accuracy was never meant to measure faithfulness; it simply has nothing to
say about it.

**Rationale-quality / plausibility evaluation.** It scores the rationale as a text — by surface
overlap with a reference, by learned similarity, or by asking a reader (human or model) whether the
rationale is coherent and consistent with the image. Everything in this family measures how
convincing the rationale *looks*. That is a property of the text as read by an observer, and it can
be high for a rationale that the model did not actually use *(observation)*. A judge that reads the
text can be led by a fluent, visually specific passage to call it faithful when it is not — so these
methods do not merely miss faithfulness; they mis-rank exactly the hardest cases, the ones that look
most faithful while being least so.

A special case is worth isolating because it is easy to mistake for a solution: checking whether the
rationale **agrees with the image** (grounding). *(The term `grounding` is defined authoritatively in
[Formal Definitions](05_Formal_Definitions.md).)* Even a perfect image-text agreement checker
measures whether the words match the picture — not whether the model's answer causally depended on
what the words describe. Agreement is about the rationale and the image; faithfulness is about the
model's decision. A method that measures the first cannot, in principle, deliver the second.

The common thread: **every method that reads only the finished output is measuring a correlate of
faithfulness, never faithfulness itself**, because faithfulness is not a property that a finished
output contains (§4).

---

## 3. Why plausibility and faithfulness diverge

That plausibility and faithfulness come apart is an **observation**, not a definition and not an
assumption. It is the empirical fact on which the whole benchmark rests, and it can be stated without
defining either term:

- *Plausibility* is a property of the rationale as read by an observer — how coherent, detailed, and
  image-consistent the text appears.
- *Faithfulness* is a property of the model's behavior — whether the answer's reason is the reason
  the text states.

Nothing forces these to coincide. A rationale can be maximally convincing and still bear no relation
to what the model used; a faithful rationale need not be the most fluent one. In current
vision-language models the two measurably diverge, and they diverge in the direction that most
defeats naive evaluation: the most plausible rationales — the fluent, concrete, visually specific
ones — are frequently among the least faithful *(observation)*. *(The precise senses of
`plausibility` and `faithfulness`, and the evidence for their divergence, belong to
[Formal Definitions](05_Formal_Definitions.md) and the project's references, respectively.)*

The consequence for evaluation is decisive. If plausibility tracked faithfulness, a plausibility
score would be a usable proxy and no new benchmark would be needed. Because plausibility does not
track faithfulness, any evaluation built on reading the text is measuring the wrong quantity, and is
most wrong precisely where it matters most.

---

## 4. Why intervention is required during benchmark construction

Because faithfulness is a property of the model's behavior rather than of the text, it cannot be
read off a single finished output. To establish it, one must change what the model sees and observe
how its answer and its stated reason respond — an **intervention** on the model. *(The term
`intervention` is used here only intuitively; the actual interventions belong to the
[Label Generation Pipeline](07_Label_Generation_Pipeline.md), and the term to
[Formal Definitions](05_Formal_Definitions.md).)*

This is not a preference; it is forced by §2 and §3. Every static, read-only method measures a
correlate. The only way to obtain a verdict that is about the model's decision — and not about how
the rationale reads — is to manipulate the model's input and watch the effect. Construction must
therefore have the live model in hand and must intervene on it; that is the only moment at which a
*trustworthy* label about the model can be manufactured at all.

This is why the benchmark's ground truth is made during construction and never by inspection: the
construction-time intervention is the one process capable of producing a faithfulness verdict rather
than a plausibility estimate.

---

## 5. Why intervention is unavailable during benchmark evaluation

Having required intervention to *build* the benchmark, the benchmark deliberately forbids it to
*solve* the benchmark. There are two reasons, one practical and one structural.

**Practical.** Intervention is exactly the expensive, model-in-hand procedure the benchmark exists
to avoid. The point of the resource is a *cheap surrogate*: a way to flag unfaithful reasoning
without re-running the model on every output. If the surrogate itself required the intervention, it
would solve nothing.

**Structural.** In the setting the benchmark models, whoever receives a model's output usually does
not have the model — it is frozen, remote, or otherwise out of reach. And if a solver *could*
intervene, there would be no problem left to pose: it would simply run the intervention and read off
the verdict, collapsing the two worlds the [Benchmark Design](01_Benchmark_Design.md) keeps apart.
Withholding intervention at evaluation time is therefore not a handicap imposed on predictors — it is
the very thing that makes the task a task.

The asymmetry between §4 and §5 — intervention required to build, forbidden to solve — is the core of
the problem. The benchmark is the gap between a verdict that was obtainable only with the model and a
verdict that must now be recovered without it.

---

## 6. What the benchmark asks predictors to recover

The benchmark asks a predictor to recover, from a model's static output alone, the **outcome the
intervention would have produced** — a statement about the generating model's behavior — without
performing the intervention. *(That outcome, once fixed and frozen, is the `label`; its definition
belongs to [Label Specification](06_Label_Specification.md).)*

Three clarifications make the ask precise:

- It is a **prediction** task, not a judging task. The predictor is not asked whether the rationale
  is good, coherent, or image-consistent; it is asked to predict whether the model was faithful.
- It is a task about the **model**, not the text. The target is a property of the generator, inferred
  through the only trace of the generator the predictor is given.
- It is a task defined by what is **withheld**. The predictor must bridge from non-causal evidence
  (the output) to a causal verdict (the withheld intervention's outcome). The difficulty is exactly
  the size of that bridge.

Whether that bridge can be crossed at all — whether the output carries any recoverable signal of the
hidden property, and whether such a signal generalizes — is the open question the benchmark is built
to pose. The benchmark does not presuppose the answer; it makes the question measurable (§7, A4).

---

## 7. Assumptions the benchmark intentionally makes

These are **assumptions**, not observations: modeling choices the benchmark elects, states openly,
and could in principle have made differently. They remain valid regardless of implementation.

- **A1 — Faithfulness is operationalized by the construction-time intervention.** For the purposes of
  this benchmark, an instance's faithfulness *is* whatever the intervention establishes about the
  model: a behavioral, necessary-condition stand-in for the broader idea, not the full philosophical
  construct. *(The operational definition is owned by
  [Formal Definitions](05_Formal_Definitions.md) and [Label Specification](06_Label_Specification.md);
  the boundary on how much the word may claim is a [Charter](00_Benchmark_Charter.md) commitment.)*
- **A2 — The intervention yields a stable, freezable verdict.** The benchmark assumes that, for an
  eligible instance, the intervention produces a verdict definite enough to be fixed once and frozen,
  so that a static corpus is meaningful.
- **A3 — Faithfulness attaches to a (model, instance) pair.** Because it is a property of the model,
  the benchmark assumes labels belong to the specific generator that produced the output, not to the
  rationale in the abstract.
- **A4 — The recoverability question is worth posing.** The benchmark assumes it is meaningful to ask
  whether the hidden property can be recovered from output alone — and builds itself so that the
  question is *measurable*. It assumes the question is worth asking; it does **not** assume the answer
  is yes (that is settled empirically, not by assumption).
- **A5 — The benchmark may restrict where the question is asked.** It assumes it is legitimate to pose
  the faithfulness question only on a defined population of instances rather than on every possible
  output. *(Which restrictions apply is owned by [Label Specification](06_Label_Specification.md) and
  the scope document.)*

---

## 8. Assumptions the benchmark explicitly refuses to make

Equally important is what the benchmark declines to assume. Each refusal is a deliberate stance, and
several correspond directly to boundaries in the [Charter](00_Benchmark_Charter.md).

- **R1 — It does not assume that a rationale which *looks* faithful *is* faithful.** Plausibility,
  coherence, and image-consistency are refused as evidence of faithfulness (§3).
- **R2 — It does not assume any reader can determine faithfulness by inspecting the text.** No judge —
  human or model — sets the ground truth; the label never comes from reading the rationale.
- **R3 — It does not assume, or claim, anything about the model's internal mechanisms.** The verdict
  is behavioral. The benchmark refuses to assert what the model "really thought," how it computed, or
  what its representations encode.
- **R4 — It does not assume that rationale-image agreement equals faithfulness.** Grounding is treated
  as a different quantity, not a stand-in (§2).
- **R5 — It does not assume that faithfulness signatures generalize across models.** Whether a signal
  learned on some generators transfers to others is measured, never presumed.
- **R6 — It does not assume its operational faithfulness is the whole concept.** The benchmark refuses
  to let the measurable stand-in silently inflate into the full construct the word can suggest.
- **R7 — It does not assume a predictor may re-create the intervention.** Recovering the label by
  re-running or perturbing the model is out of bounds by definition, not a permitted strategy (§5).

Where A-assumptions say what the benchmark builds on, R-refusals say what it will not smuggle in.
Together they fix the problem's honest boundary.

---

## 9. The problem's scope versus broader interpretability questions

The benchmark measures a narrow, behavioral, output-recoverable question, and it is important to say
what neighbouring questions it does **not** touch — so the problem is not mistaken for a larger one it
cannot address.

| The benchmark asks | The benchmark does **not** ask |
|---|---|
| Can we tell, from a model's output, whether its stated reason tracks the visual evidence its answer depended on? | What is the model actually computing internally, and what do its representations encode? |
| Was this model, on this instance, behaviorally faithful under intervention? | Why is the model unfaithful, and how would we make it more faithful? |
| Is the hidden causal verdict recoverable from output alone, and does it generalize? | Is this rationale useful, persuasive, or good for a human reader? |

The distinction is between **behavior** and **mechanism**. Broader interpretability asks what is
happening inside the model; the benchmark stays outside, at the level of what the model *does* under
a controlled disturbance and whether that can be predicted from its output. This is a deliberately
smaller, answerable question. The benchmark's value is that the smaller question is both tractable and
decision-relevant; its discipline is that it never lets its results be read as answers to the larger
one. *(This boundary is also a standing [Charter](00_Benchmark_Charter.md) commitment and is stated at
the point of definition wherever the label is discussed.)*

---

## 10. Summary

The problem is a **measurement gap**: current evaluation of vision-language model rationales scores
answer-correctness and text-quality, both of which are correlates of — and, for the hardest cases,
actively misleading about — the property that matters, *faithfulness*. Faithfulness is a behavioral
property of the model and can only be established by intervening on it, which is expensive and
requires the model in hand; ordinary evaluation therefore never measures it. The benchmark closes the
gap by establishing the causal verdict once, during construction, and then asking whether it can be
recovered from a model's output alone at evaluation time, when the model is gone. It builds only on
stated observations, makes only stated assumptions, refuses a stated set of shortcuts, and confines
itself to a behavioral question distinct from the mechanistic questions of interpretability. The
remaining specifications refine *how* each of these pieces is realized; this document fixes *what
problem* they are realizing, and does so in terms that survive any change of implementation.
