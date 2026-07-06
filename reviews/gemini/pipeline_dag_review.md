# Conceptual Review: Label Generation Pipeline DAG (docs/design/Label_Generation_Pipeline_DAG.md)

This review provides a critical, independent conceptual evaluation of the specification and data model dependencies as documented in `docs/design/Label_Generation_Pipeline_DAG.md`. The review focuses exclusively on **Sections 8, 11, and 12**, evaluating whether the identified ambiguities are genuine specification-level concerns or merely implementation details.

---

## 1. Is the provenance cycle (Section 8.2, G1) a true semantic ambiguity?

**Yes. The provenance cycle is a true semantic ambiguity in the specification, not an implementation detail.**

* **The Problem:** 
  `06a` (§3.5/§3.6) specifies that the `Behavioural State` and `Label` are derived *from* the `Interventional Provenance` (A5). Yet, `06a` (§3.7) requires the same `Interventional Provenance` (A5) to *contain* the resulting `Behavioural State` and `Label`. This creates a literal cycle: $A5 \rightarrow A6 \rightarrow A7 \rightarrow A5$.
* **Why it is Semantic, Not Implementation-Only:**
  In a data model, if an artifact is defined to contain another artifact, its valid existence is conceptually dependent on that contained object. If we treat this as a mere "implementation detail," developers might bypass it with schema mutability or nullable fields, but the underlying conceptual integrity is broken. 
  Is `Interventional Provenance` a raw record of the input measurements (the physical interventions), or is it a composite report of the final labeling decisions? If it is the latter, it cannot be used as a clean, independent source to reconstruct the label without circularity. This distinction between *raw interventional history* and *derived decision metadata* must be semantically codified in the specifications (`06a` and `07`), rather than being left as an ad-hoc implementation patch.

---

## 2. Is the E1 issue (Section 11, G2) a genuine ontology inconsistency?

**Yes. The E1 issue is a profound, genuine ontological inconsistency.**

* **The Problem:** 
  The label specification (`06`) defines `E1` (Eligibility Fail 1) as "no complete output tuple" (e.g., when the generator refuses or fails to output a readable answer/rationale). However, the data model (`06a`) requires that every `Candidate Subject` (A3)—which is the input to the entire labeling pipeline—MUST contain a valid, well-formed `Output Tuple` (A2) with an exact chosen answer and rationale.
* **The Catch-22:**
  1. To record that an item failed with `E1`, it must be processed as a `Candidate Subject` in the pipeline.
  2. To represent an item as a `Candidate Subject`, we must construct a valid `Output Tuple`.
  3. We cannot construct a valid `Output Tuple` because the generator failed to produce a complete output.
* **Why it is Ontological:**
  This is a logical contradiction in the core data schema. It cannot be fixed in code without violating the written rules. To resolve this, the benchmark needs a new ontological primitive—such as a `Generation Attempt` (which can represent failures)—or it must relax the schema of `Candidate Subject` to allow optional/nullable outputs. This is a fundamental conceptual design decision that belongs in the specifications.

---

## 3. Would you resolve these through ADRs rather than specification revisions?

The correct approach requires **both**, partitioned by the nature of the decision:

1. **For G2 (The E1 Ontology Inconsistency):** 
   This must be resolved through an **ADR (Architecture Decision Record) first, followed by a specification revision.**
   * *Why:* The E1 issue presents distinct architectural and philosophical choices. Do we introduce a `Generation Attempt` primitive? Do we relax the `Candidate Subject` schema to allow nullable fields? Do we route refusals out of the pipeline before candidates are created? Choosing among these divergent design paths requires an ADR. Once chosen, the decision must be formally written into the specs (`06`, `06a`, `07`) to eliminate document drift.
2. **For G1 (The Provenance Cycle):**
   This can be resolved directly through a **specification revision** to `06a` and `07`.
   * *Why:* There is no complex design trade-off here; it is simply a modeling error. The spec should be revised to separate the *Raw Interventional Provenance* (the input to state/label derivation) from the *Sealed Corpus Entry* (which contains the raw provenance alongside the derived state and label as sibling attributes, rather than nesting them inside the provenance).

---

## 4. Are there any additional semantic ambiguities the DAG exposes?

Yes, the DAG exposes three additional conceptual ambiguities:

1. **The Representation of Baseline Outputs (G6):**
   The benchmark uses baselines to calibrate performance. Do baseline outputs (which do not go through causal interventions) exist as `Candidate Subjects`? If so, are they labeled as ineligible, or is there an unlabelled "Output-Tuple-Only" path in the data model? The relationship between baseline models and the artifact schema is left undefined.
2. **Generator Identity vs. Information Boundary (Section 9.2):**
   While generator identity is forbidden from the predictor, the predictor is given access to the `Split` assignment. In an `OOD-Model` split, knowing that a group of instances belongs to the held-out split acts as a proxy for generator style. The boundary has a semantic leak where partition membership partially exposes generator groupings.
3. **The Routed-Aside Set (G5):**
   Section 11 notes that the `Routed-Aside Set` and `Frozen Corpus` are omitted from the `06a` artifact table. If the routed-aside set is released for transparency, does it have its own `Corpus Manifest`? How is its integrity verified? This leaves the boundary properties of the routed-aside set ambiguous.

---

## Verification Summary Evaluation (Section 12)

The summary in Section 12 is highly accurate. It correctly marks the literal graph as **Failing** acyclicity due to the $A5 \leftrightarrow A6/A7$ cycle, and correctly identifies that responsibility allocation passes only when partitioned by **dimension** rather than by bare artifact ownership labels. This candid assessment confirms that the pipeline is not yet structurally coherent at the specification level.

---

## Recommendation

**Revision required**
