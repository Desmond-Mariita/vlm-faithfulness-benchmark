---
Title: Baseline Systems
Status: Accepted
Benchmark-Version: v1.0
Last-reviewed: 2026-07-01
Related:
  - docs/01_Benchmark_Design.md
  - docs/03_Problem_Definition.md
  - docs/05_Formal_Definitions.md
  - docs/06_Label_Specification.md
  - docs/06a_Benchmark_Data_Model.md
  - docs/07_Label_Generation_Pipeline.md
  - docs/08_Dataset_Specification.md
  - docs/10_Evaluation_Protocol.md
  - decisions/ADR-002-Construction-Provenance-Lifecycle.md
  - decisions/ADR-003-Incomplete-Candidate-Subjects.md
---

# Baseline Systems

*This specification defines the benchmark's **baseline philosophy** and its required **reference
systems**. Baselines are `predictors` built by the benchmark authors to calibrate the task's difficulty
(Formal Definitions §28). They consume the released dataset exactly as any predictor does and redefine
**no** benchmark semantics.*

> **Boundary of this document.** This document defines *which reference systems exist, what each
> demonstrates, and what information each may and may not use.* It defines **no** evaluation metrics,
> **no** leaderboard or ranking, **no** implementation algorithms, and **no** training procedures —
> those are owned by [Evaluation Protocol](10_Evaluation_Protocol.md) or remain implementation
> decisions (§17). Baselines are described by their **information access** and **purpose**, never by
> their method. Every semantic term is owned by the frozen specifications; this document only
> *instantiates predictors* under the approved information boundary.

> **Requirement keywords.** MUST, MUST NOT, SHOULD, and MAY are used in the RFC-2119 sense.

**Coverage of the required items:** why baselines exist (§3); what each demonstrates and which
assumption each challenges (§4, and per baseline §8–§14); information available (§6), forbidden (§7),
and predictor-visible inputs (§5); reference heuristic (§8); text-only (§9); vision-language (§10);
agentic (§11); oracle upper bound (§12); random (§13); human performance (§14); reporting obligations
(§15); conformance (§16).

---

## 1. Scope and ownership

This specification owns the definition of the benchmark's **reference baseline systems**. It is a
consumer of the released corpus (Dataset Specification §12–§14): a baseline is a `predictor`
(Formal Definitions §7) evaluated in the evaluation world, with **no** privileged access beyond any
external predictor (Benchmark Design invariant 6).

It does **not** own: the `recovery` task target, `floor`, `success`/`failure` criteria, `hard core`
reporting, or the `scorecard` — those are owned by [Evaluation Protocol](10_Evaluation_Protocol.md); nor
corpus construction (owned by `07`/`08`). Where a baseline's purpose refers to a measurable outcome (for
example, "collapses on the hard core"), the outcome is described qualitatively here and **measured** by
`10`.

---

## 2. Normative authorities

| Key | Authority |
|---|---|
| **BD** | Benchmark Design — information boundary §11; baselines are peers (invariant 6); irreversibility. |
| **PD** | Problem Definition — what predictors recover §6; intentional assumptions §7; refused shortcuts R1–R7. |
| **FD** | Formal Definitions — Predictor §7, Recovery §27, Baseline §28, Floor §29, Hard core §30, Transfer §31, Success/Failure §32–§33. |
| **LS** | Label Specification — label meaning; no-judge boundary I2; independence from appearance I6. |
| **DM** | Data Model — the boundary and view separation (T6). |
| **DS** | Dataset Specification — predictor-visible view §12, hidden view §13, audit view §14, split roles §6. |

Where this document appears to differ from any authority, the authority governs.

---

## 3. Why baselines exist

Baselines are **instruments, not competitors.** They exist to make the benchmark's difficulty and its
central claims *measurable* by anchoring the space of achievable performance:

- **They locate the floor.** A genuine solution must beat what trivial or non-visual signal already
  affords; baselines establish that reference level (FD §29).
- **They make the information bound visible.** The benchmark's premise is that faithfulness is a causal
  property withheld from the static output (PD §5–§6). Baselines that use progressively more of the
  predictor-visible tuple — and more aggressive external tooling — show how far output-only reasoning can
  travel, and where it stops.
- **They demonstrate the benchmark's headline claims.** That plausibility is not faithfulness (PD §3),
  that grounding is not faithfulness (PD §2), and that neither a strong model nor a human can read the
  verdict off the text — these are shown by specific baselines behaving as predicted, especially on the
  hard core.
- **They give external predictors reference points.** A new system is understood relative to the floor,
  the strong reference, and the oracle ceiling — not against a ranking.

Baselines are the benchmark's way of proving, with predictors, what the Problem Definition asserts in
prose.

---

## 4. What each baseline demonstrates and challenges

| Baseline | Demonstrates | Assumption / claim it challenges |
|---|---|---|
| Random (§13) | The chance / label-prior anchor. | — (absolute reference; no claim). |
| Reference heuristic (§8) | What obvious, transparent rules capture. | "The verdict is readable from simple surface/agreement rules." |
| Text-only (§9) | The **floor**: performance without vision. | "Vision is unnecessary; the rationale's style reveals the label" (PD §2–§3). |
| Vision-language (§10) | How much genuine multimodal reasoning recovers above the floor. | "Grounding equals faithfulness" (PD §2); "the verdict is fully recoverable from output." |
| Agentic (§11) | Whether more tools/compute cross the information bound. | "The bound can be circumvented by aggressive analysis" (PD §5; R7). |
| Oracle (§12, conceptual) | The semantic ceiling set by the intervention. | Makes explicit that the true ceiling requires the withheld counterfactual. |
| Human (§14, if applicable) | Whether humans can read faithfulness off the tuple. | "Humans can judge faithfulness from the rationale" (PD §3; LS-I6). |

Each baseline's section (§8–§14) restates its purpose in detail.

---

## 5. Predictor-visible inputs (all baselines)

Every non-conceptual baseline consumes **only** the predictor-visible view (Dataset Specification §12):

- Per scored instance: the **complete** `Output Tuple` — image, question, options, chosen answer,
  rationale, and any source-provided grounding annotations — plus the split membership the evaluation
  protocol requires.
- **Training material.** A baseline that learns is fit **only** on the **Train** split, using that
  split's released training labels (FD §24 training material). The labels of Validation and the held-out
  worlds are **withheld** for scoring (Dataset Specification §13) and MUST NOT be used to fit or select a
  baseline. *(The exact release facet for Train-split labels is owned by `08`/`10`; §18.)*

No baseline receives any input a fair external predictor could not receive (BD invariant 6).

---

## 6. Information available to each baseline

Baselines differ only in **which subset** of the predictor-visible surface (§5), and which **external
tooling**, they use:

| Baseline | Text of the tuple | Image + annotations | External tools (own) | Train labels (fitting) | Interventional access |
|---|:---:|:---:|:---:|:---:|:---:|
| Random | — | — | — | prior only | — |
| Reference heuristic | yes | MAY | fixed, none learned | typically none | — |
| Text-only | yes | **no** | MAY (text-only) | MAY | — |
| Vision-language | yes | yes | MAY (own vision) | MAY | — |
| Agentic | yes | yes | yes (detectors, vision, reasoning) | MAY | — |
| Oracle (conceptual) | n/a | n/a | n/a | n/a | **has the withheld counterfactual (conceptual only)** |
| Human | yes | yes | none beyond own reasoning | — | — |

"External tools (own)" means a baseline may bring its own models/detectors and apply them to the
predictor-visible tuple. It never means access to the generating model (§7).

---

## 7. Information explicitly forbidden (all baselines)

No non-conceptual baseline may use, or derive, any of the following. Using any is a conformance failure
(§16):

- **F1 — The generating model.** A baseline MUST NOT query, run, or re-perturb the original generator, or
  resubmit a perturbed image to it. Doing so would re-run the intervention and read the label off the
  model (PD-R7; FD §27). This is the load-bearing prohibition for the **agentic** baseline.
- **F2 — Generator identity.** A baseline MUST NOT use which generator produced an instance (Dataset
  Specification §12; BD §11). (In the OOD-Model split, membership is an inherent, documented grouping
  signal, but the specific generator identity is still withheld — DS §7.4.)
- **F3 — The counterfactual and interventional provenance.** A baseline MUST NOT use the generator's
  counterfactual behaviour, the `Interventional Provenance`, or its margins (LS §6 margins; DM-T6;
  PD-R7). The **audit view** (Dataset Specification §14) is never a baseline input.
- **F4 — The withheld labels.** A baseline MUST NOT use the `Label`, reason code, or `Behavioural State`
  of any scored instance, nor the labels of Validation or the held-out worlds (Dataset Specification
  §13).
- **F5 — Held-out worlds during fitting.** A baseline MUST be fit and selected on the **Train** split
  only; the held-out-world splits are withheld until scoring (FD §31; Dataset Specification §6).

The single conceptual exception is the **oracle** (§12), which is defined *by* having F3 access and is
therefore **not a benchmark participant**.

---

## 8. Reference heuristic baseline

- **Role / purpose.** A simple, transparent, fixed heuristic over the predictor-visible tuple — the
  most method-simple sensible predictor.
- **What it demonstrates.** What obvious rules (for example, coarse text–image agreement or surface
  cues) capture of the label, with no learning.
- **Assumption challenged.** That the verdict is readable from simple surface or agreement rules; a low
  result argues the task is not trivially rule-solvable.
- **Information access.** The tuple; it MAY inspect the image and annotations; it uses no learned
  parameters. (§5, §6.)
- **Specifically forbidden.** The universal list (§7); in particular it MUST NOT smuggle in a
  plausibility or correctness judgment as the verdict (LS-I2, I6).
- **Expected behaviour.** Modest; it is a transparency reference. Its behaviour relative to the floor is
  reported by `10`.

---

## 9. Text-only baseline

- **Role / purpose.** The **floor** (FD §29): a predictor that consumes only the **text** of the tuple
  (question, options, chosen answer, rationale) and **not** the image.
- **What it demonstrates.** How much of the label is recoverable from text alone — i.e. the level any
  vision-using solution must exceed to show it is using vision (PD §2).
- **Assumption challenged.** That vision is unnecessary, and that the rationale's style/coherence reveals
  faithfulness (PD §3). It embodies the plausibility-is-not-faithfulness claim.
- **Information access.** Text fields of the tuple only; **no** image or image-derived signal. It MAY
  learn on Train labels. (§5, §6.)
- **Specifically forbidden.** The image and anything derived from it; plus the universal list (§7).
- **Expected / required behaviour.** On the **hard core** — where rationales are highly plausible yet
  labelled unfaithful — the text-only floor is **expected to approach chance**. Demonstrating this
  collapse is a purpose of this baseline; the metric by which collapse is measured is owned by `10`. A
  strong text-only floor that did **not** collapse on the hard core would signal a text-shortcut and MUST
  be reported (§15).

---

## 10. Vision-language baseline

- **Role / purpose.** The strong reference that uses everything a fair predictor may use — the full
  predictor-visible tuple, image and text together.
- **What it demonstrates.** How much genuine multimodal reasoning recovers **above** the floor; the
  benchmark's estimate of the achievable output-only signal.
- **Assumption challenged.** That grounding equals faithfulness (PD §2): a system that reasons about
  image–rationale agreement should do well where grounding correlates with the label yet **struggle on
  the hard core**, where grounding and faithfulness diverge by construction. It also tests the claim that
  the verdict is fully recoverable from output.
- **Information access.** The full tuple, including the image and source annotations; it MAY apply its
  own vision analysis and MAY incorporate a **grounding signal** (its own estimate of image–rationale
  agreement) as a feature. It MAY learn on Train labels. (§5, §6.)
- **Specifically forbidden.** It MUST NOT treat its grounding signal as the label (grounding is a
  correlate, not the verdict — FD §15; LS-I6), and MUST NOT use the generator's counterfactual (§7 F3).
- **Expected behaviour.** Best among the output-only baselines overall, with a **reduced margin on the
  hard core**. A strong general model used as a judge over the tuple is realized as this baseline (or the
  agentic one, §11); its drop toward chance on the hard core is a headline demonstration of the
  benchmark and MUST be reported (§15).

---

## 11. Agentic baseline

- **Role / purpose.** The most aggressive output-only predictor: it may call external detectors, vision
  models, and multi-step reasoning on the tuple.
- **What it demonstrates.** Whether more tooling and compute can **cross** the information bound — i.e.
  whether the withheld counterfactual can be reconstructed from the static output by any amount of
  external analysis.
- **Assumption challenged.** That the information bound is a mere compute limitation rather than a
  structural one (PD §5). If even an agentic system cannot exceed the strong reference on the hard core,
  the bound is shown to be structural.
- **Information access.** The full tuple plus **its own** external tools applied to that tuple. (§5, §6.)
- **Specifically forbidden — load-bearing.** It MUST NOT query, run, re-perturb, or resubmit inputs to
  the **original generator** (PD-R7; §7 F1); doing so would simply re-run the intervention. It MUST NOT
  use generator identity, the counterfactual, or provenance (§7). Its external tools are its own; they are
  never the generating model.
- **Expected behaviour.** May exceed the vision-language baseline in the aggregate, but is **not expected
  to escape the hard core**; a failure to cross the bound there is itself the demonstration.

---

## 12. Oracle upper bound (conceptual only)

- **Role / purpose.** A **conceptual** reference: a predictor defined by having the withheld
  interventional information — effectively, the intervention itself.
- **What it demonstrates.** The **semantic ceiling**. Because the label *is* the intervention's outcome
  (LS §4; FD §27), an oracle with that information recovers the label by construction. The point is to
  make explicit that the true ceiling requires the counterfactual, which no real predictor may have.
- **Assumption illuminated.** That any real predictor's gap to the oracle is exactly the **information
  bound** — the part of faithfulness that the static output cannot carry (PD §5–§6).
- **Information access.** The withheld counterfactual (§7 F3) — which is why it is **not a benchmark
  participant**.
- **Explicitly conceptual.** The oracle MUST NOT be implemented as a scored system, entered into any
  comparison of predictors, or released as a baseline; it has the answer key and crosses the information
  boundary. It is reported only as a conceptual ceiling (perfect by construction) to frame the achievable
  range.

---

## 13. Random baseline

- **Role / purpose.** The absolute chance anchor.
- **What it demonstrates.** The lower reference of the achievable range: performance with **no**
  instance information.
- **Assumption challenged.** None; it is a reference floor for interpreting every other result.
- **Information access.** No per-instance input. It MAY use only the **Train** split's label prior (from
  training material) to set a constant/majority prediction, or predict uniformly at random. It MUST NOT
  use the labels of the split being scored (§7 F4).
- **Specifically forbidden.** Any per-instance signal, and any held-out/scored label (§7).
- **Notes.** Both a uniform variant and a prior/majority variant MAY be reported; both are references,
  not competitors.

---

## 14. Human performance (if applicable)

- **Role / purpose.** An **optional** reference: human annotators acting as predictors, reading the
  predictor-visible tuple and predicting the label.
- **What it demonstrates.** Whether faithfulness is a **human-readable** property of the output. Because
  the verdict is interventional and not a property of the text (LS-I2, I6; PD §3), humans — like a strong
  model — are expected to be subject to the plausibility trap and **not to exceed the floor on the hard
  core**.
- **Assumption challenged.** That a human can judge faithfulness by reading the rationale.
- **Information access.** The predictor-visible tuple (§5); human reasoning only, no external model
  access.
- **Distinct from pipeline verification.** This is **not** the human check of the construction pipeline
  (which verifies the pipeline, not faithfulness, and is a construction activity owned by `07`/`08`).
  Human performance here is a *predictor* bound by the information boundary.
- **Out of scope for the initial (v1.0) release.** Human performance is **not** in scope for the first
  release: it is an optional, additive reference whose ethics/consent contract is not part of the v1.0
  standard, and omitting it removes a dangling dependency. It MAY be introduced in a later release as an
  additive, meaning-preserving change (a v1 amendment) *only* once a release ethics/consent contract
  exists; if reported, it MUST obey the universal forbidden list (§7). Adding it changes no benchmark
  semantic.

---

## 15. Baseline reporting obligations

For each baseline it reports, the benchmark MUST disclose (the *metrics* themselves are owned by `10`;
this section fixes *what must be declared*):

- **BR1 — Information-access declaration.** The exact subset of the predictor-visible view the baseline
  used, any external tools, and whether and how it was fit on the Train split (§5, §6).
- **BR2 — Conformance statement.** An explicit confirmation that the baseline used **no** forbidden
  information (§7), in particular that it never queried or re-perturbed the generator (F1).
- **BR3 — Corpus version.** The corpus version the baseline was run on; results are meaningful only
  against that version (Dataset Specification §17).
- **BR4 — Floor and hard-core behaviour.** The text-only floor's behaviour on the hard core MUST be
  reported; any failure of the floor to collapse there (a text-shortcut signal) MUST be flagged (§9).
- **BR5 — Peer status.** A statement that the authors' baselines received no privileged access beyond an
  external predictor (BD invariant 6).
- **BR6 — Reference, not ranking.** Baselines MUST be reported as **reference points** against the floor,
  the strong reference, and the oracle ceiling — **not** as a ranking or leaderboard (which are out of
  scope; §17).

The oracle (§12) is reported only as a conceptual ceiling and carries no information-access or
conformance obligations, since it is not a participant.

---

## 16. Conformance requirements

A baseline system is **conformant** iff:

1. it consumes only the predictor-visible view for prediction (§5) and only Train-split labels for any
   fitting (§5, §6);
2. it uses **no** forbidden information (§7) — above all, it never queries, runs, re-perturbs, or
   resubmits to the original generator (F1; PD-R7);
3. it is fit and selected on the **Train** split only, with Validation and held-out worlds withheld until
   scoring (F5; FD §31);
4. it declares its information access and conformance (BR1–BR2);
5. its results are keyed to a specific corpus version (BR3);
6. it never re-derives or overrides any benchmark semantic — it consumes the released corpus as-is
   (BD8; ADR-002 N1–N4).

The **oracle** is conformant to its own definition **only** as a conceptual reference and MUST NOT be
scored or ranked as a predictor (§12). The authors' baselines are peers of any external predictor and
MUST NOT be given access the public lacks (BD invariant 6).

---

## 17. Deferred to implementation and other owners

- **Metrics, floor computation, success/failure criteria, hard-core reporting, and the scorecard** →
  [Evaluation Protocol](10_Evaluation_Protocol.md).
- **Any leaderboard or ranking of systems** → out of scope for the benchmark's reference systems; not
  defined here.
- **The concrete algorithms, feature designs, model choices, and training procedures** of every baseline
  → implementation decisions, constrained only by §5–§7 and §16.
- **The Train-label release facet** (how training labels are delivered) → owned by `08`/`10` (§18).

This document specifies *which reference systems must exist and what they may use*; it does not specify
*how* any is built.

---

## 18. Open dependencies

- The precise **release facet for Train-split labels** (training material) is under-specified across
  Dataset Specification §12–§13 and MUST be fixed by `08`/`10`; every learnable baseline depends on it.
- The **hard core** membership (Dataset Specification §6.8) and its **reporting** (`10`) determine where
  the floor/vision-language/agentic collapse claims are measured; the baselines here reference that
  subset but do not define it.
- **Human performance** depends on the release's ethics/consent policy (owned by `08`); it remains
  optional until that policy is fixed.

These MUST be reconciled before the affected baselines are reported, but they do not change the baseline
definitions or the information boundary fixed here.

---

*This document defines the benchmark's reference systems as instruments: a random anchor, a transparent
heuristic, a text-only floor, a vision-language strong reference, an agentic upper probe, a conceptual
oracle ceiling, and optional human performance. Each is a predictor bound by the same information
boundary, each demonstrates a specific benchmark claim, and none redefines a benchmark semantic or is
ranked — the metrics that measure them belong to the Evaluation Protocol.*
