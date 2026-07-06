---
Title: Evaluation Protocol
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
  - docs/09_Baseline_Systems.md
  - decisions/ADR-002-Construction-Provenance-Lifecycle.md
  - decisions/ADR-003-Incomplete-Candidate-Subjects.md
---

# Evaluation Protocol

*This is the benchmark's final normative specification. It defines how benchmark results are **produced,
validated, reported, and interpreted**, and how benchmark **claims are established**. It consumes the
outputs of every prior specification and redefines **no** benchmark semantics.*

> **Boundary of this document.** This document owns evaluation metrics, scorecards, reporting and
> statistical policy, benchmark success criteria, conformance testing, leaderboard policy, reproducibility
> reporting, and release reports. It defines **no** implementation code, visualization or plotting
> software, or training methods. It names statistical procedures (bootstrap intervals, multiplicity
> correction, AUROC, macro-F1, Cohen's κ) at the level of a standard — *which* measure, on *which*
> subset, and *how* reported — never their code. Every semantic term (`label`, `faithful`/`unfaithful`,
> `D1`/`D2`, `floor`, `hard core`, `transfer`, `recovery`) is owned by the frozen specifications; this
> document only *measures and interprets* their artifacts.

> **Requirement keywords.** MUST, MUST NOT, SHOULD, and MAY are used in the RFC-2119 sense.

**Coverage of the required items:** evaluation philosophy (§1); inputs (§2); outputs (§3); primary
metrics (§4); secondary metrics (§5); split-specific reporting (§6); hard-core reporting (§7);
statistical confidence (§8); baseline comparisons and leaderboard policy (§9); conformance testing
(§10); failure reporting (§11); reproducibility reporting (§12); scorecard format (§13); benchmark
release report (§14); interpretation guidance (§15); limitations (§16); open questions (§17).

---

## 1. Evaluation philosophy

The benchmark's purpose is to measure whether a `predictor` can **recover** the withheld faithfulness
verdict from a model's static output (Formal Definitions §27; Problem Definition §6). Evaluation
therefore does three separable things, and this protocol keeps them separate throughout:

- **Measurement** — a metric value with a confidence interval, computed on a named subset of a named
  corpus version. A measurement asserts nothing beyond itself.
- **Interpretation** — what a measurement implies **under the benchmark's construct** (behavioural,
  necessary-condition faithfulness; Label Specification §5 scope; Charter). Interpretation is bounded by
  what the construct licenses.
- **Scientific claim** — a benchmark-level assertion (for example, "plausibility does not track
  faithfulness") established **only** when a pre-registered measurement, with its CI and multiplicity
  control, supports it under a valid interpretation.

**How a claim is established.** A benchmark claim is established iff (a) it is stated in advance in the
release's analysis plan (§14); (b) it is supported by a measurement with a confidence interval (§8) on a
stated corpus version (§12); (c) the measurement survives multiplicity control if it is not the primary
endpoint (§8); and (d) its interpretation stays within the construct scope (§15). A number without this
chain is a measurement, not a claim.

Evaluation is **adversarial by design** (Benchmark Design §3): predictors may try any signal, so the
protocol anchors every result against the `floor` and the conceptual `oracle` ceiling (§9) and never
reports a bare score.

---

## 2. Evaluation inputs

The protocol consumes, per corpus version:

- **The predictor's predictions.** For each scored instance, a predicted `label` (`faithful`/
  `unfaithful`) and, where the predictor supports it, a continuous score for the `unfaithful` class
  (used for threshold-free measures) and an optional predicted reason code (`D1`/`D2`).
- **The hidden evaluation view** (Dataset Specification §13): the true `Label` and reason code for each
  scored instance, available **only** to this protocol, never to the predictor.
- **The split assignment and hard-core membership** (Dataset Specification §6–§9, §6.8).
- **The baseline reference systems** and their declarations (Baseline Systems §5–§7, §15).
- **The corpus manifest** (Dataset Specification §10): corpus version, specification versions, generator
  identities, pinned selectors and mappings, and coverage/routed-aside counts.

The protocol MUST NOT consume the `Interventional Provenance`, margins, or generator identity as a
scoring signal beyond what the manifest exposes for stratification; the audit view (Dataset Specification
§14) is for interpretation and traceability, never a metric input that re-opens the label.

---

## 3. Evaluation outputs

The protocol produces two artifacts:

- **A scorecard** (Formal Definitions §34; §13 here) — the per-predictor record of measurements.
- **A benchmark release report** (§14) — the per-corpus-version document that states and substantiates
  the benchmark's claims.

Both are evaluation-world artifacts; neither touches a generator (Benchmark Design §6).

---

## 4. Primary metrics

- **P-1 — Pre-registered primary endpoint.** The benchmark designates **one** primary endpoint for
  multiplicity control (§8): **macro-averaged F1 over the two label classes on the Validation split**, at
  the operating point of P-3. This is the headline in-distribution recovery measure; Train/Validation
  carry balanced classes (Dataset Specification §6.5), so macro-F1 is well-defined and deployment-relevant.
- **P-2 — Lead discriminative measure.** **AUROC on the balanced hard core** (Formal Definitions §30),
  using the predictor's continuous `unfaithful` score. AUROC is threshold-free and is the benchmark's
  central *separability* measure; it is well-defined only because the hard core is balanced (both classes
  present), and it is the lead evidence for the plausibility-versus-faithfulness claim (§7).
  **Inferential status (multiplicity):** P-2 is the **pre-eminent member of the exploratory secondary
  family** (§8, C-2), not a second confirmatory endpoint — there is exactly **one** confirmatory endpoint
  (P-1). P-2 becomes confirmatory only if a release **pre-registers it as a co-primary** with an explicit
  alpha split in the analysis plan (§14); absent that, it is reported with multiplicity correction like
  every other secondary measure.
- **P-3 — Operating point.** The decision threshold that converts a continuous score to a binary `label`
  MUST be **frozen on the Validation split** and applied **unchanged** to every other split, so that
  held-out-world macro-F1 reflects a deployable fixed operating point rather than a per-split refit.
- **P-4 — Floor gap.** For any subset, the **floor gap** is the primary metric minus the text-only
  floor's value on the same subset (Baseline Systems §9). It quantifies the genuine visual contribution a
  result demonstrates above trivial signal (Problem Definition §2).

A predictor that does not emit a continuous score is measured on the threshold-based metrics only; its
AUROC cells are reported as not-applicable, not as zero.

---

## 5. Secondary metrics

Reported as a multiplicity-corrected family (§8), never as the single headline:

- **S-1 — OOD macro-F1 and transfer gaps.** Macro-F1 on each held-out-world split (OOD-Model,
  OOD-QType, OOD-Dataset) at the P-3 operating point, and the **transfer gap** = Validation macro-F1
  minus held-out macro-F1 (Formal Definitions §31).
- **S-2 — Reason-code F1 (diagnostic).** Macro-F1 over `{D1, D2}` on the **unfaithful** subset,
  reported **separately** so it never muddies the binary headline. *(This resolves Label Specification
  Q5: reason codes are scored as a secondary diagnostic only.)*
- **S-3 — Cross-generator agreement (κ).** Cohen's κ between generators on a shared set of questions,
  as a signal of whether faithfulness signatures are generator-specific. Reported with a CI and its
  paired-n (§8).
- **S-4 — Hard-core macro-F1** at the P-3 operating point (alongside P-2 AUROC).
- **S-5 — Plausibility-matched control.** The strong baselines' values on a randomly-sampled,
  plausibility-matched control subset, reported **beside** the optimized hard core, so the hard-core
  behaviour is shown not to be a selection artifact.
- **S-6 — Baseline reference values.** The floor, vision-language, agentic, random, and (if applicable)
  human values, and the conceptual oracle ceiling (Baseline Systems §8–§14), for every subset a
  predictor is reported on.

Every metric in §4–§5 is reported **sliced by split** (§6) and, where the construct permits, by reason
code and generator; each cell carries its CI and support count (§8).

---

## 6. Split-specific reporting

- **R-1 — Report every split.** Metrics MUST be reported on Train (sanity only), Validation (primary),
  and each held-out world (OOD-Model, OOD-QType, OOD-Dataset), never aggregated into a single number that
  hides the split structure.
- **R-2 — Fixed operating point across splits.** The P-3 threshold, frozen on Validation, is applied to
  every split (no per-split refit).
- **R-3 — Natural distribution disclosure.** Held-out worlds retain their natural label distribution
  (Dataset Specification §6.5). Reporting MUST disclose each split's class balance; for imbalanced splits,
  macro-F1 is the primary reported measure and AUROC is reported only where both classes are adequately
  present.
- **R-4 — Transfer gaps.** The Validation-to-OOD transfer gap (S-1) MUST be reported per held-out
  dimension, with its CI.
- **R-5 — Provenance of every number.** Each reported value MUST carry its split, its corpus version, its
  support count, and its CI (§8, §12).

---

## 7. Hard-core reporting

The hard core (Formal Definitions §30; Dataset Specification §6.8) is the balanced subset where
plausibility and/or grounding is high yet the label is `unfaithful`, matched with hard positives so
AUROC is defined and stratified so it separates faithfulness rather than generator (Dataset Specification
§6.8).

- **H-1 — Discriminative headline.** Report **AUROC** (P-2) and macro-F1 (S-4) on the hard core.
- **H-2 — The collapse headline.** Report the **text-only floor** and any strong model-as-judge baseline
  (realized as the vision-language or agentic baseline, Baseline Systems §10–§11) **approaching chance**
  on the hard core. This is the benchmark's headline evidence that plausibility does not track
  faithfulness (Charter; Problem Definition §3). The collapse MUST be shown as a measurement with a CI,
  not asserted.
- **H-3 — Contamination check.** Before stating the collapse headline for any model-based baseline, a
  membership/contamination check MUST be reported, so the collapse is not attributable to the model having
  seen the items.
- **H-4 — Selection-artifact control.** Report the plausibility-matched control (S-5) beside the hard
  core, so the hard-core behaviour is demonstrably not an artifact of hard-core selection.
- **H-5 — Composition.** Report the hard core's composition across the matched strata (generator,
  question type, dataset, length), so AUROC cannot be read as separating generator identity.

---

## 8. Statistical confidence

- **C-1 — CI on everything.** Every reported metric MUST carry a confidence interval (paired bootstrap
  where a paired comparison applies; a 95 % level; a stated resample count that is a policy minimum, not
  code). No point estimate may be reported or headlined without its CI.
- **C-2 — One primary endpoint; corrected secondary family.** P-1 is the single pre-registered
  confirmatory endpoint. Every other metric is **exploratory** and reported as a family with multiplicity
  control (Holm–Bonferroni or Benjamini–Hochberg), stated in the analysis plan (§14). The confirmatory
  and exploratory distinction MUST be explicit in the scorecard.
- **C-3 — Support counts and a minimum-n rule.** Every cell MUST report its support count `n`. A cell
  whose `n` is below the pre-registered usable-CI threshold MUST be reported with its `n` and CI but MUST
  NOT be used to **headline** a point estimate; this applies especially to thin OOD and `D1`/`D2`
  diagnostic cells.
- **C-4 — κ discipline.** Cross-generator κ (S-3) MUST be reported with its CI and paired-n. Any
  interpretive threshold on κ (for example, a low-agreement line) is **interpretive, not pass/fail**, and
  MUST be justified or omitted; separating nearby κ values requires large paired-n, which MUST be
  disclosed.
- **C-5 — Correctness slicing.** Where answer-correctness is recorded, metrics SHOULD be reported sliced
  by correctness so that correctness cannot silently proxy the label (Label Specification I6).
  Eligibility does not condition the corpus on correctness (ADR-004; Label Specification §3), so the
  slice is never constant by construction; where correctness is not recorded for a source, the slice
  is omitted for lack of recorded correctness, and that absence changes neither eligibility nor
  conformance (ADR-004 C7).

---

## 9. Baseline comparisons and leaderboard policy

- **B-1 — Anchored reporting.** Every predictor MUST be reported against the reference levels from
  Baseline Systems: `random`, the text-only `floor`, the vision-language reference, the agentic probe,
  the conceptual `oracle` ceiling, and (if applicable) human performance. The **floor gap** (P-4) and the
  **oracle gap** frame each result: the floor gap is the genuine contribution; the oracle gap is the
  information bound (§15).
- **B-2 — Peers, not privileged.** The authors' baselines received no access beyond an external predictor
  (Benchmark Design invariant 6); the scorecard MUST state this.
- **B-3 — References, not a ranking.** Baselines and predictors are reported as reference points, not as
  a competitive ordering.

**Leaderboard policy.** A leaderboard is **optional**. If one exists, it MUST: (a) be gated on
conformance (§10); (b) report the pre-registered primary endpoint (P-1) with its CI; (c) key every entry
to a specific corpus version; (d) display the floor and the oracle ceiling alongside entries; and (e)
**never** reduce the benchmark to a single rank that hides the hard-core and OOD structure. A rank is not
a benchmark claim; claims are established only through the release report (§14). If a leaderboard cannot
satisfy (a)–(e), it MUST NOT be published.

---

## 10. Conformance testing

A predictor's run is **conformant** iff:

- **K-1** its predictions cover **exactly** the scored instances of the stated corpus version — no
  missing, extra, or reordered instances;
- **K-2** it consumed only the predictor-visible view for prediction and only Train-split labels for any
  fitting (Baseline Systems §5, §16), used **no** forbidden information (Baseline Systems §7), and never
  queried or re-perturbed the generator (Problem Definition R7);
- **K-3** it declares its information access and conformance (Baseline Systems BR1–BR2);
- **K-4** it is keyed to a specific corpus version (§12);
- **K-5** it re-derives or overrides **no** benchmark semantic — it consumes the corpus as-is (ADR-002
  N1–N4).

A **scorecard is produced only for a conformant run.** A non-conformant run MUST be reported as
non-conformant with the reason (§11), never silently scored or excluded. Conformance is a property of
**behaviour and declared access**, not of method; the protocol does not inspect a predictor's internal
algorithm.

---

## 11. Failure reporting

Failure reporting is a first-class output, not an omission.

- **N-1 — Failure-criterion outcomes.** Report the Formal Definitions §33 failure signatures explicitly:
  collapse to the floor; dependence on generator style (low κ, or OOD-Model collapse); reliance on
  plausibility or grounding (hard-core collapse for a system claiming faithfulness).
- **N-2 — Non-conformant runs.** Report non-conformant runs and their reasons (§10); do not hide them.
- **N-3 — Null and negative results.** Report null findings — including the case where **no** predictor
  exceeds the floor on the hard core, which is itself a benchmark finding and engages the Charter §6
  stop/re-scope conditions. A null result MUST be reported with the same statistical rigor as a positive
  one (§8).
- **N-4 — Coverage caveats.** Report routed-aside counts by E-code (Dataset Specification §5.5), any
  minimum-n cells (C-3), any contamination flags (H-3), and any split whose class balance limits a
  measure.

---

## 12. Reproducibility reporting

- **Y-1 — Two reproducibility layers.** *Corpus* reproducibility is owned by Dataset Specification (the
  corpus is re-derivable from its manifest on a pinned environment, not byte-identical — Benchmark Design
  §10). *Scorecard* reproducibility is owned here.
- **Y-2 — Scorecard reproducibility record.** A scorecard MUST record: the corpus version and its
  manifest reference; the specification versions that govern label meaning and production; the predictor's
  declared configuration and information access; and the evaluation-harness version.
- **Y-2a — Two distinct reproducibility notions.** *Statistical* uncertainty (a metric's CI) and
  *artifact/label* reproducibility (deterministic re-derivation of the same labels/scores) are **separate
  concepts and MUST NOT be conflated.** A CI measures sampling uncertainty, not acceptable software drift.
  Artifact/label reproducibility is judged against a declared **acceptance tolerance or exactness scope**
  (the manifest's acceptance comparison, Dataset Specification N10.7) — for example, an exact-match scope
  for deterministic fields and a bounded label-flip tolerance near operating points. A result is
  reproducible when (a) its labels/scores re-derive within that declared tolerance on the pinned reference
  environment **and** (b) the reported metric re-computes within its CI; off-stack re-runs may differ near
  operating-point thresholds, and this MUST be stated. The numeric tolerance is a per-release constant,
  fixed in the manifest, not here.
- **Y-3 — Version keying.** Every reported number is meaningful only against its corpus version; the
  scorecard MUST make cross-version comparison impossible to do implicitly (Dataset Specification §17).

---

## 13. Scorecard format

The scorecard (Formal Definitions §34) MUST contain the following (the *serialization* is deferred, §17;
this fixes required *contents*, not a format):

- **Identity and conformance:** predictor identity; information-access declaration; conformance statement
  (§10); peer-status statement (B-2).
- **Versioning:** corpus version; governing specification versions; evaluation-harness version (§12).
- **Primary result:** the pre-registered primary endpoint (P-1) with its CI, flagged as confirmatory.
- **Discriminative result:** hard-core AUROC (P-2) with its CI.
- **Secondary family:** each secondary metric (§5) with its CI, support count, and multiplicity-corrected
  significance, flagged as exploratory.
- **Split table:** every metric per split, with transfer gaps, class balances, CIs, and support counts
  (§6).
- **Hard-core panel:** AUROC, macro-F1, floor/judge collapse, contamination check, plausibility-matched
  control, and composition (§7).
- **Diagnostic:** reason-code (`D1`/`D2`) F1 with support counts (S-2, C-3).
- **Cross-generator:** κ with CI and paired-n (S-3, C-4).
- **Baselines:** the reference values and the floor/oracle gaps (§9).
- **Failure and coverage:** failure-criterion outcomes, non-conformance, null results, routed-aside and
  minimum-n caveats (§11).

**Every numeric entry MUST carry: value, CI, support count `n`, split, and corpus version.** No entry may
appear without them.

---

## 14. Benchmark release report

Each corpus version is accompanied by a **release report** — the document through which the benchmark's
claims are established and published. It MUST contain:

- **RR-1 — Pre-registered analysis plan.** The primary endpoint (P-1), the secondary family and its
  multiplicity-correction procedure, the operating-point rule (P-3), the minimum-n rule (C-3), and the
  claims to be tested — all stated **before** the results, so confirmatory and exploratory analyses are
  distinguishable (§8).
- **RR-2 — Reference scorecards.** The scorecards of the reference baselines (§13).
- **RR-3 — The headline analyses.** The hard-core collapse (§7), the OOD/transfer results (§6), and the
  cross-generator κ analysis (§5), each as measurements with CIs.
- **RR-4 — Established claims.** The benchmark-level claims the release asserts, each tied explicitly to
  its supporting measurement, CI, and place in the pre-registered plan (§1, §15).
- **RR-5 — Limitations and datasheet reference.** The limitations (§16) and a reference to the corpus
  datasheet (Dataset Specification).
- **RR-6 — Three-layer separation.** The report MUST keep measurement, interpretation, and scientific
  claim visibly separate (§15).

A benchmark claim not present in a release report, with its supporting chain, is **not** an established
claim of the benchmark.

---

## 15. Interpretation guidance

The three layers of §1, applied:

- **Measurement → interpretation.** A metric value with a CI on a subset licenses an interpretation only
  within the **construct scope**. "Above the floor on Validation with adequate transfer" is interpreted as
  *a predictor recovers behavioural faithfulness signatures from the output* — **not** as "the model
  understands, or reasons about, faithfulness" (Label Specification §5 scope; Charter). A `faithful`
  recovery result licenses nothing mechanistic.
- **Correlates are not the target.** Grounding and plausibility are correlates, not the label (Problem
  Definition §2–§3; Label Specification I6); a result driven by them (e.g. strong grounding-only
  performance that collapses on the hard core) MUST be interpreted as *correlate-riding*, not recovery.
- **Correctness is not the label.** Answer-correctness MUST NOT be read as faithfulness (Label
  Specification I6; C-5).
- **The oracle gap is the information bound, not a defect.** A predictor's distance from the conceptual
  oracle ceiling reflects the part of faithfulness the static output cannot carry (Problem Definition
  §5–§6); it MUST NOT be interpreted as a fixable shortcoming of the predictor.
- **Generalization is bounded by the splits and κ.** Claims of transfer are bounded by the held-out
  worlds evaluated and by the cross-generator κ; a claim MUST NOT generalize beyond the generators,
  datasets, and question types in the corpus version.
- **Claim = measurement + interpretation + pre-registration.** A scientific claim is established only when
  a pre-registered, CI-bearing, multiplicity-controlled measurement supports it under a construct-valid
  interpretation (§1, §14). Any stronger statement is out of scope.

---

## 16. Limitations

- **L-1 — Construct.** Faithfulness here is **behavioural and necessary-condition**; the benchmark cannot
  distinguish a severed-verbalisation mechanism from an absent-grounding one, and a `faithful` result
  proves nothing about internal computation (Label Specification §5; Charter).
- **L-2 — Generator-specificity.** Faithfulness signatures may be generator-specific; results are bounded
  by the corpus's generators and are only as general as κ and the OOD-Model result permit (§5, §7).
- **L-3 — Thin cells.** OOD and `D1`/`D2` cells may be small; CIs may be wide; the minimum-n rule (C-3)
  constrains what may be headlined.
- **L-4 — Method dependence.** Results depend on the (deferred) operational determinations in `07` —
  evidence localization, Condition B, controls — whose methods are implementation decisions; a corpus's
  labels, hence all downstream measurements, are only as sound as those determinations.
- **L-5 — Hard-core dependence.** Hard-core AUROC depends on pinned membership selectors and stratified
  matching (Dataset Specification §6.8); its interpretation is contingent on those pins.
- **L-6 — The information bound may be tight.** Output-only recovery has a ceiling below the oracle by
  construction; a persistently low ceiling above the floor is a genuine possible finding — that
  faithfulness is largely unrecoverable from output alone — and engages the Charter §6 re-scope
  conditions.
- **L-7 — Open label policy.** Label Specification Q3 (Condition B granularity) is resolved for
  Benchmark v1 by the fixed binary Condition-B / S1-S3 contract and no longer makes affected
  measurements conditional. Q4 (composite-generator validity) is **resolved by ADR-005** — a
  composite generator is one subject — so affected measurements are not conditional on that policy.
  Q1 (correctness eligibility) is **resolved by ADR-004** — correctness does not gate eligibility —
  so correctness-related measurements are conditional only on correctness being recorded and
  supported (C-5), not on an open policy.
- **L-8 — Human performance.** If reported, human performance is typically small-sample and bounded by
  the release's consent/ethics policy (Dataset Specification).

---

## 17. Open questions

- **Q-E1 — Minimum-n threshold.** The pre-registered usable-CI support threshold (C-3) is a policy
  constant to be fixed per release; it is not set here.
- **Q-E2 — κ interpretation.** Whether, and at what value, a cross-generator κ line is reported as
  interpretively meaningful (C-4) remains open and MUST be justified per release.
- **Q-E3 — Leaderboard existence.** Whether a given release publishes a leaderboard (§9) is a per-release
  policy decision, subject to the stated constraints.
- **Q-E4 — Human-performance scope.** Whether human performance is in scope for a release depends on the
  ethics/consent policy (Dataset Specification).
- **Q-E5 — Cross-version meta-analysis.** Rules for comparing results across corpus versions beyond
  "within a version only" (Dataset Specification §17) are not defined here and require a future decision.
- **Q-E6 — Serialization.** The scorecard and release-report **formats** are deferred to implementation;
  this document fixes their required contents only (§13, §14).

Resolved here: **Label Specification Q5** (reason-code scoring) is resolved as the secondary diagnostic
S-2 — a separately reported `D1`/`D2` macro-F1 over the unfaithful subset that never enters the binary
headline.

---

*This protocol closes the specification set. It defines how the benchmark measures recovery, how it
anchors every result against the floor and the oracle, how it controls statistical and multiplicity
error, how it tests conformance, and how — through a pre-registered release report that separates
measurement, interpretation, and claim — the benchmark's scientific assertions are established. It
consumes every prior specification and changes none of their semantics.*
