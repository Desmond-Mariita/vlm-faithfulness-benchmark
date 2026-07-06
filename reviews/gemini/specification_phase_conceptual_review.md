# Specification Phase Conceptual Review

**Reviewer Role:** Independent Conceptual Reviewer  
**Review Date:** July 1, 2026  
**Status of Specification Phase:** Complete (Synchronized)  
**Deliverable Path:** `reviews/gemini/specification_phase_conceptual_review.md`

---

## Executive Summary

This independent review presents a whole-system sanity check of the completed benchmark specification phase. The evaluated documents comprise the full standard—including the Benchmark Charter, Vision, Benchmark Design, Formal Definitions, Label Specification, Benchmark Data Model, Label Generation Pipeline, Dataset Specification, Baseline Systems, Evaluation Protocol, Benchmark Assurance, and governing ADRs (ADR-002 and ADR-003).

The overall architecture of the benchmark is **exceptionally rigorous, conceptually honest, and scientifically sound**. The paradigm of using an *interventional construction world* to establish a causal necessary-condition ground truth, which must then be *recovered in an output-only evaluation world* without model access, is highly elegant. It provides a robust, airtight boundary that prevents the "cheating" common in existing evaluations and prevents subjective human/LLM priors from contaminating the label path.

However, several unresolved policy questions, semantic edge cases, and causal gaps remain. Addressing these—particularly the correctness eligibility policy (`LS Q1`), the evidence-region representation (`DM Q4`), and a causal gap between evidence localization and rationale tracking—is necessary to ensure the benchmark remains resilient during implementation.

---

## Detailed Assessment of the 12 Core Questions

### 1. Is the benchmark measuring one coherent construct?
**Yes.** The benchmark measures **output-only necessary behavioural faithfulness** (recovering whether a vision-language model's chain-of-thought rationale reflects the visual evidence its answer causally depended on). The construct is kept strictly coherent by:
- Operationalizing faithfulness causally via input perturbation rather than surface similarity.
- Strictly enforcing that "faithfulness" is a necessary behavioural condition, never an internal mechanistic or cognitive claim.
- Porting this causal verdict into a static, output-only prediction target.

### 2. Are the claims proportional to the evidence the benchmark can produce?
**Yes.** The standard is remarkably self-aware and honest. It refuses to claim that a "faithful" label implies anything about the generator's internal computational mechanism (R3). It repeatedly qualifies its labels as *behavioural, necessary-condition* verdicts only. If a predictor scores highly, the benchmark claims only that the predictor has recovered behavioural signatures of visual dependence, nothing more.

### 3. Are faithfulness, grounding, plausibility, evidence, intervention, label, and recovery kept separate?
**Yes.** The Formal Definitions (`05`) and the dependency graph enforce strict anti-circularity:
- `plausibility` (observer-facing) and `grounding` (image-text correspondence) are defined independently of `faithfulness`.
- `evidence` (the visual content the answer depends on) is defined via `image-dependence` (a property of the answer), which keeps the `evidence` ⇄ `faithfulness` ⇄ `grounding` triangle acyclic.
- `faithfulness` is defined via behavioral conditions, and the `label` merely references or projects it.
- `recovery` is the prediction task.
The boundaries between these concepts are kept pristine throughout the documents.

### 4. Does the benchmark accidentally smuggle implementation choices into semantics?
**No.** The specifications (`07`, `08`, `10`, `11`) are extremely disciplined at separating "operational rules" (what must be determined/guaranteed) from "implementation decisions" (pseudocode, models, thresholds, serialization formats, or specific dataset paths). The contracts are written at the architectural level, allowing independent teams to implement the software without altering the underlying benchmark semantics.

### 5. Does the benchmark over-rely on assumptions that remain unproven?
**Minimally, but intentionally.** The benchmark openly states its core modeling assumptions (PD §7, A1–A5) and gathers them in the Traceability Matrix (A01–A16) to ensure they are transparent. It assumes that:
- Faithfulness is stable enough to be captured in a static, frozen corpus.
- Faithfulness can be operationalized by construction-time interventions.
Importantly, it does **not** assume that output-only recovery is possible or that faithfulness signatures generalize across models; these are treated as empirical questions measured by the benchmark's splits and baseline gaps.

### 6. Are the failure modes and assurance rules sufficient?
**Yes, they are exemplary.** The Benchmark Assurance framework (`11`) is exceptionally comprehensive, establishing a clear failure taxonomy (construct, data, label, evaluation, and governance failures), grading their severities, and defining rigorous release-blocking criteria (`BL1`–`BL9`). It is a model-grade governance framework that protects the scientific integrity of the instrument over time.

### 7. Are the information boundary and oracle distinction clear?
**Yes, perfectly so.** The construction/evaluation boundary is a one-way, irreversible divide. The predictor-visible `Output Tuple` carries only the complete raw outputs. The generator identity, interventional provenance, and continuous margins are strictly withheld from predictors to prevent leakage. The conceptual "Oracle" baseline (which has access to the counterfactuals) provides an explicit ceiling that represents the maximum theoretically recoverable signal under the information bound, ensuring realistic difficulty calibration.

### 8. Are there unresolved open questions that should block implementation?
**Yes.** Several open policy/semantic questions explicitly flagged in the standard block implementation:
- `LS Q1` (correctness eligibility) is open. We cannot implement source normalization (`S01`), generator execution (`S02`), or precondition evaluation (`S05`) without a final policy on whether incorrect answers are filtered out or kept.
- `DM Q4` (evidence-region identity form) is open. S08 (localize evidence) cannot produce an interface and S09 (rationale interventions) cannot consume it without defining how an "evidence region" is conceptually structured.
- `LS Q3` (Condition B granularity) is open, which affects S11/S12 state mapping.

### 9. Are there places where future researchers may misunderstand or misuse the benchmark?
**Yes, particularly in two areas:**
- **Construct Drift (CF1/CF3):** Despite the clear qualifiers, downstream researchers will likely market high-scoring models as "mechanistically faithful" or claim their models "truly reason" because they pass the benchmark.
- **Visual Intervention Generality:** Researchers might mistake the benchmark's faithfulness as absolute, forgetting that it is relative to the specific visual perturbations implemented during construction.

### 10. What are the strongest parts of the specification?
- **Causal Grounding / Static Evaluation Split:** The core paradigm of using privileged causal interventions during offline construction to label a static corpus for an output-only predictor.
- **Anti-Judge Commitment:** Complete exclusion of human/LLM text-only judges from the label path, ensuring ground truth is purely behavioral and causal.
- **The "Hard Core" Subset:** The mathematically balanced subset matching high-plausibility unfaithful negatives with high-plausibility faithful positives, completely exposing style-riding predictors.
- **Ontological Hygiene (ADR-002 & ADR-003):** Excellent formalization of the provenance lifecycle and incomplete Candidate Subjects, resolving cyclic dependency hazards and representation issues.

### 11. What are the weakest parts?
- **Causal Gap in Rationale Tracking:** There is a subtle but critical gap between evidence localization and Condition B. If the localization pipeline identifies a non-causal visual region, a faithful model's rationale won't change when that region is perturbed, resulting in a false `unfaithful/D2` (inert rationale) label (see `CONC-01`).
- **Open Policy Questions:** Having key eligibility and granularity questions left "open" in the draft standard blocks clean pipeline scaffolding.

### 12. What has been underestimated?
- **Computational Cost of Construction:** Adding new generators (which is required for long-term relevance) requires running the entire multi-perturbation interventional pipeline. For large, state-of-the-art vision-language models, this construction cost could restrict the benchmark's scalability and maintenance frequency.

---

## Conceptual Issue Log

### Issue ID: CONC-01
- **Severity:** Major
- **Affected document(s):** `docs/06_Label_Specification.md`, `docs/07_Label_Generation_Pipeline.md`
- **Conceptual concern:** Causal gap between evidence localization (S08) and Condition B (S11) determination. If the localization pipeline selects an incorrect region $R_{wrong}$ instead of the true causal region $R_{true}$, a perfectly faithful generator's rationale will not change when $R_{wrong}$ is perturbed (since its true visual evidence was untouched). Because the rationale does not change, S11 will conclude that the rationale does not track the evidence, resulting in a false-positive `unfaithful/D2` (inert rationale) label.
- **Why it matters:** This gap risks a high false-positive rate for unfaithfulness due to upstream errors in the localization model rather than actual generator unfaithfulness, undermining the benchmark's claim of being an honest causal instrument.
- **Recommended action:** Mandate a **localization causal-control rule** (as part of S10/P6). The control must verify that perturbing the localized evidence region $R$ actually changes the generator's answer (mirroring the global Condition A test at the region level). If perturbing $R$ does not change the answer, then $R$ is not confirmed as the causal evidence, and the instance must be routed aside as `E5` (unlocatable evidence) or `E6` (unlicensed causal reading) rather than being falsely labeled `unfaithful/D2`.
- **Whether action requires:** Document edit.

---

### Issue ID: OPEN-Q1
- **Severity:** Blocker
- **Affected document(s):** `docs/06_Label_Specification.md`, `docs/07_Label_Generation_Pipeline.md`, `docs/08_Dataset_Specification.md`
- **Conceptual concern:** `LS Q1` (correctness eligibility conditioning) remains open. Whether answer correctness on the unperturbed image gates eligibility is a fundamental design policy.
- **Why it matters:** The pipeline (`07`) cannot specify preconditions (S05) or routing (S15), and the dataset specification (`08`) cannot normalize sources (S01) or assemble entries (S16), until this policy is resolved. Starting code implementation without resolving this will lead to major throwaway work.
- **Recommended action:** Draft and approve an ADR to resolve `LS Q1`. We recommend **not** gating on correctness generally (as a model's rationale can be perfectly faithful to its incorrect reasoning), but perhaps establishing correctness-stratified splits or gating only if evidence localization is shown to be impossible on incorrect choices.
- **Whether action requires:** ADR.

---

### Issue ID: OPEN-Q3
- **Severity:** Major
- **Affected document(s):** `docs/06_Label_Specification.md`, `docs/07_Label_Generation_Pipeline.md`
- **Conceptual concern:** `LS Q3` (granularity of Condition B) remains open.
- **Why it matters:** If the pipeline is built with binary "tracks / does not track" labels but later requires a "partial tracking" state, it will trigger a MAJOR version bump (v2), invalidating all existing corpora, state mappings, and predictor scorecard comparisons.
- **Recommended action:** Resolve `LS Q3` via an ADR before implementation. We recommend sticking to a strictly binary Condition B for Version 1 to preserve simplicity and discriminative power, and documenting "partial tracking" as a deferred goal for v2.
- **Whether action requires:** ADR.

---

### Issue ID: OPEN-Q4
- **Severity:** Major
- **Affected document(s):** `docs/06a_Benchmark_Data_Model.md`, `docs/07_Label_Generation_Pipeline.md`
- **Conceptual concern:** `DM Q4` (evidence-region identity form) remains open.
- **Why it matters:** S08 (localize evidence) must produce this artifact, and S09 (rationale interventions) must consume it. Without defining its form (e.g., bounding boxes, semantic pixel-masks, or textual spans), the data contracts between pipeline stages are incomplete, blocking implementation of these two core stages.
- **Recommended action:** Issue a clarifying ADR or document edit that defines the canonical representation of an evidence region. We recommend using **bounding boxes** (or sets of bounding boxes) as they are the most common, well-defined, and portable format across visual MC-VQA datasets (such as VCR or GQA) and easy to perturb.
- **Whether action requires:** ADR or document edit.

---

### Issue ID: SCALE-01
- **Severity:** Minor
- **Affected document(s):** `docs/08_Dataset_Specification.md`, `docs/07_Label_Generation_Pipeline.md`, `docs/11_Benchmark_Assurance.md`
- **Conceptual concern:** Computational cost of benchmark construction and scaling. Every new generator added to the corpus requires running the full multi-perturbation pipeline (S02–S15), which involves dozens of forward passes per instance.
- **Why it matters:** If the construction cost is too high, the benchmark will struggle to keep pace with state-of-the-art vision-language models, accelerating its obsolescence.
- **Recommended action:** Add a "generator eligibility/selection guide" in the Dataset Specification to prioritize which models to include, and encourage lightweight perturbation methods to keep construction feasible.
- **Whether action requires:** Clarification note or document edit.

---

### Issue ID: CONC-02
- **Severity:** Minor
- **Affected document(s):** `docs/08_Dataset_Specification.md`, `docs/10_Evaluation_Protocol.md`, `docs/11_Benchmark_Assurance.md`
- **Conceptual concern:** Potential split leakage of held-out generator families. While generator *identity* is withheld from predictors, the families of generators used in the train split versus the OOD splits must be transparent.
- **Why it matters:** If external developers do not know which generator families are held out (OOD-Model), they might accidentally train their predictors on those families, violating split disjointness (DF3) and inflating transfer scores.
- **Recommended action:** Explicitly specify that the *generator families* (e.g., "Qwen-VL", "LLaVA") used in Train, Validation, and OOD-Model splits MUST be publicly named and listed in the public Corpus Manifest (§10) and Dataset Specification (§7).
- **Whether action requires:** Document edit.

---

### Issue ID: CONC-03
- **Severity:** Informational
- **Affected document(s):** `docs/08_Dataset_Specification.md`, `docs/10_Evaluation_Protocol.md`
- **Conceptual concern:** Human-Performance Evaluation framing. Humans are highly prone to "plausibility bias" (treating a fluent, coherent CoT as faithful based on text appearance).
- **Why it matters:** If humans are compared as a baseline without highly specific instructions, their scores will reflect a plausibility prior rather than the causal construct, leading to invalid human-vs-model comparisons.
- **Recommended action:** Recommend that if a release includes human evaluation, the evaluators MUST be given an instruction protocol that explicitly trains them to look for causal evidence tracking rather than text plausibility, with calibrated unfaithful examples.
- **Whether action requires:** Clarification note.

---

# Conceptual Readiness Verdict

### **Ready after minor clarification**

**Justification:**  
The benchmark specification phase is in an incredibly advanced and rigorous state. The core construct, information boundaries, evaluation protocols, and assurance metrics are mathematically and conceptually airtight. The cyclic hazards of the pipeline were resolved beautifully by ADR-002, and the incomplete-candidate lifecycle was addressed cleanly by ADR-003. 

The standard is not "Conceptually ready for implementation" only because a small number of critical policy and interface questions (`LS Q1` correctness, `LS Q3` granularity, and `DM Q4` evidence-region identity form) are explicitly flagged as "open." Once these few open questions are clarified and decided via ADRs, the project will be fully ready for software implementation.
