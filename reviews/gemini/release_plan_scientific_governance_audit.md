# Scientific Governance Audit — Benchmark v1.0 Release Plan

**Reviewer Role:** Independent Scientific Governance Reviewer  
**Audit Date:** July 1, 2026  
**Document Under Review:** `docs/design/Benchmark_v1.0_Release_Plan.md`  
**Deliverable Path:** `reviews/gemini/release_plan_scientific_governance_audit.md`

---

## Executive Summary

This audit evaluates the Benchmark v1.0 Release Plan from the perspective of scientific and architectural governance. The Release Plan is a critical transition document designed to bridge the gap between the completed Specification Phase and the active Implementation Phase. 

The overall assessment is that the Release Plan is a **masterclass in scientific discipline and governance hygiene**. It does not merely coordinate tasks; it actively protects the scientific construct of the benchmark from erosion during implementation. By explicitly identifying seven unresolved semantic decisions (WS-1 Blockers) and establishing the **Reference Implementation Profile (RIP)** as an independent operational contract, the plan ensures that implementation-level choices remain strictly separated from core benchmark semantics.

With a few minor corrections—specifically around the naming of the `D1` reason code, parallelizing independent synchronization tasks, and planning for deterministic reproducibility—the Release Plan is ready to serve as the definitive roadmap for Benchmark v1.0.

---

## Evaluation Against Review Criteria

### 1. Scientific Integrity
**Does the Release Plan preserve the benchmark's construct?**  
Yes, absolutely. The Release Plan explicitly protects the necessary behavioral-faithfulness construct. It does so by:
- Directing that the "viability gate" (`VAL-01` / `REL-034`) must run during Phase B, and that its failure must trigger project re-scope or abandonment rather than shipping a compromised corpus.
- Resolving the confirmed causal gap between evidence localization and Condition B (`REL-003`) via `ADR-006`, which introduces a localization causal-control rule to prevent false-positive unfaithfulness labels.

### 2. Governance Integrity
**Are ADRs used appropriately? Do architectural decisions remain architectural? Do implementation choices stay outside the specification?**  
The governance model is highly disciplined:
- **Appropriate ADR Routing:** Major semantic choices (correctness conditioning `REL-001`, composite identity `REL-002`, and P6 completion `REL-003`) are routed through formal ADRs (`ADR-004/005/006`) rather than being made implicitly within implementation code or planning text.
- **The RIP Separation:** Deferring operational thresholds, specific models, and perturbation packages to the **Reference Implementation Profile (RIP)** keeps the specification sheets strictly conceptual and architectural.
- **Clearing the Authority Chain:** Moving stale, contradicting review files and historical matrices out of the normative tree into an archive folder prevents spec-drift and authority contradictions.

### 3. Semantic Stability
**Does the Release Plan redefine terminology, labels, behavior, evaluation, or the ontology?**  
The Release Plan does not inappropriately redefine any part of the benchmark ontology. Instead, it identifies where *existing* documents conflict on terms (such as "crossing the boundary" `REL-011` or the name of `D1` `REL-019`) and schedules WS-2 tasks to synchronize them back to the frozen conceptual standard.
- *Redefining D1 (Appropriate/Ambiguous):* Renaming or clarifying `D1` (currently "Ungrounded answer") is highly appropriate because "grounding" has a distinct, rationale-level definition in the ontology, and using it at the answer-level introduces semantic confusion.
- *Adjusting primary metric evaluations (Appropriate):* Separating decision-threshold selection from confirmatory measurement (`REL-006`) is a scientifically necessary correction that preserves statistical validity without changing the underlying construct.

### 4. Scope Discipline
**Does the Release Plan remain focused on transition planning?**  
The Scope Discipline is exemplary. The document resists "redesigning" the benchmark or pre-empting the policy decisions it schedules. It defines five workstreams, details the dependency rationale, specifies freeze checklists, and charts a post-freeze sequential roadmap (Phases A–G). It specifies *what* must be resolved and *how* the gates operate, without bypassing the required governance (ADRs).

### 5. Future Maintainability
**Would following this Release Plan help preserve the benchmark or create governance debt?**  
It directly **eliminates governance debt** before implementation begins. Freezing the specification suite in its current "un-synchronized" state would leave developers with stale registries and contradictory diagrams. By enforcing a rigorous pre-freeze checklist and establishing the RIP as the versioned home for operational parameters, the plan guarantees that the codebase can evolve and scale to new generators without continuously modifying or breaking the core specification.

### 6. Public Trust
**Would this Release Plan increase confidence or confuse external researchers?**  
If made public, this Release Plan will significantly **increase scientific confidence** in the benchmark.
- *Strengths:* It demonstrates a transparent, peer-reviewed, and highly audited development process. The explicit "abandonment" and "viability" criteria show rare scientific honesty.
- *Weaknesses:* The multi-workstream, phase-gated execution is highly complex. To prevent external researchers from being overwhelmed, the plan wisely schedules root README and LICENSE updates (`REL-039/038`) to provide clean, accessible entry points into the project.

---

## Audit Findings and Recommendations

### Finding ID: GOV-01
- **Severity:** Informational
- **Section:** Section 2, REL-003 / Section 7, Phase A & B
- **Description:** Causal Control Validation Complexity. Proposing a region-level answer-change check as a localization causal-control rule (`REL-003`) is an outstanding scientific safeguard, but its empirical verification (`REL-035` in `WS-4`) requires a specialized "seeded localization-error study" on a pilot pipeline.
- **Why it matters:** Implementing a custom error-seeding pipeline could introduce unexpected engineering overhead, risking schedule slippage during the Pilot Construction phase.
- **Recommendation:** Keep the initial causal-control rule mathematically simple in the RIP (e.g., comparing argmax distribution shifts) and ensure that the "seeded localization-error study" utilizes synthetic or pre-annotated bounding boxes to avoid overcomplicating the verification phase.
- **Classification:** Future work

---

### Finding ID: SEM-01
- **Severity:** Minor
- **Section:** Section 2, REL-019
- **Description:** Terminology shift for "D1 — Ungrounded answer." The Release Plan flags that `D1` uses grounding-family vocabulary at the answer-level, which conflicts with the normative definition of "grounding" (`05` §15) as a rationale-level property.
- **Why it matters:** Retaining "grounded" in the answer-level failure mode violates the strict terminology separation in the specifications and will confuse external researchers attempting to predict or evaluate the baseline.
- **Recommendation:** We strongly recommend executing the `REL-019` rename by changing the `D1` reason code to **"Image-independent answer"** or **"Answer-level non-dependence"** within `06` and `07` as part of WS-2, completely removing "grounded" from the answer-level taxonomy.
- **Classification:** Release Plan revision

---

### Finding ID: MAINT-01
- **Severity:** Minor
- **Section:** Section 7, Post-Freeze Roadmap (Phases C, D, E)
- **Description:** Stochastic Reproducibility of Perturbations. If any of the visual perturbations in S06 or S09 are stochastic (such as random noise, randomized crop boundaries, or non-deterministic blurring), exact-reproduction requirements (`REL-007`) will fail across different platforms or library versions.
- **Why it matters:** Minor stochastic drift across environments will lead to subtle label flips, violating the corpus's "frozen" immutability and undermining public audit trust.
- **Recommendation:** The Dataset Specification (`08`) and the RIP (`REL-027`) must explicitly mandate that all construction-time perturbations be **fully deterministic** (e.g., using hard-coded grids, integer-level crops, or pinned pseudo-random seeds), or require saving the perturbed image hashes in the internal manifest.
- **Classification:** Specification clarification

---

### Finding ID: SCOPE-01
- **Severity:** Informational
- **Section:** Section 4, Release Dependency Graph
- **Description:** Over-coupling of independent WS-2 tasks in the Dependency Graph. The graph represents the entire WS-2 synchronization phase as sequentially downstream of WS-1.
- **Why it matters:** While core semantic synchronization must wait for WS-1 decisions, several purely mechanical or editorial tasks (e.g., authoring REL-008 conventions, REL-021 RFC-2119 declarations, and REL-024 editorial sweeps) are completely independent of WS-1 and can run in parallel.
- **Recommendation:** Revise the Release Plan's workstream descriptions to explicitly highlight that independent, non-decision-dependent WS-2 tasks should be parallelized with WS-1 to optimize the release timeline.
- **Classification:** Release Plan revision

---

## Executive Assessment

### 1. Does this Release Plan faithfully represent the benchmark?
**Yes.** The Release Plan represents the benchmark with exceptional fidelity. It translates the highly abstract, conceptual specifications into concrete, actionable milestones without compromising the scientific integrity or the rigorous construct boundaries of the original design.

### 2. Does it introduce unintended benchmark semantics?
**No.** The Release Plan is highly disciplined. It does not introduce any back-door semantics or pre-emptively decide open policies. Every semantic change is explicitly routed to an authoritative decision-maker (an ADR or an edit in the owning specification).

### 3. Should it remain an internal planning document or become part of the published repository?
The Release Plan **should be published** as part of the public repository once the freeze act (`REL-026`) is executed and WS-5 is complete. Publishing it demonstrates rare scientific transparency, offers a clear historical record of how reviews were addressed, and provides external contributors with an invaluable roadmap of the benchmark's lifecycle and validation gates.

---

## Final Verdict

### **Approved with Minor Revisions**

**Justification:**  
The Release Plan is an outstanding, highly mature transition plan. It perfectly bridges the specification and implementation worlds. The requirement for "Minor Revisions" is limited to executing the minor improvements identified in this audit (specifically finalizing the `D1` terminology rename pre-freeze, explicitly encouraging deterministic perturbations in `08` to satisfy `REL-007`, and clarifying that non-dependent WS-2 editorial tasks can run in parallel with WS-1 to accelerate the schedule). Once these adjustments are incorporated, the Release Plan is fully approved for execution.
