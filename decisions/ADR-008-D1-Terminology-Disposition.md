---
Status: Accepted
Date: 2026-07-03
Accepted: 2026-07-03
Supersedes: —
Superseded-by: —
Deprecated-by: —
Charter-clause: — (diagnostic display-name clarification; no label-meaning change)
Related:
  - docs/05_Formal_Definitions.md
  - docs/06_Label_Specification.md
  - docs/conventions/decision-records.md
  - docs/conventions/versioning.md
  - docs/design/Benchmark_v1.0_Release_Plan.md
  - reviews/codex/release_plan_technical_audit.md
  - reviews/gemini/release_plan_scientific_governance_audit.md
---

# ADR-008: D1 Terminology Disposition

> **Decision status.** This is the V1-008 decision package accepted by the Benchmark Maintainer on
> 2026-07-03. It authorizes the bounded terminology and specification changes described below.

## 1. Context

Label Specification §6 assigns diagnostic reason code `D1` the display name **"Ungrounded answer"** and
defines its exact meaning as state S1: Condition A fails because the chosen answer is not
image-dependent. Section 8.1 uses the same name while explaining that D1 is an answer-side failure.

Formal Definitions §15 gives `grounding` a different, rationale-level meaning: correspondence between
visual content stated or implied by a rationale and what is present in the image or evidence. Grounding
is a correlate explicitly excluded from the faithfulness label path. The D1 display name therefore uses
grounding-family vocabulary for an answer-side causal condition even though D1 is not a grounding
judgment.

The machine code `D1`, its S1 mapping, precedence over D2, and exact Condition-A-false semantics are
unambiguous. The decision surface is limited to whether the human-readable name should retain the
collision, be disambiguated in place, or be renamed without changing code or meaning.

## 2. Exact decision surface

V1-008 decides only the human-readable diagnostic name attached to code `D1` and the minimum
disambiguation needed to prevent it from being read as Formal Definitions §15 grounding.

It does **not** decide or alter:

- the code value `D1` or the code set `{D1, D2}`;
- behavioural state S1 or the S1→`unfaithful`/D1 projection;
- Condition A, image-dependence, evidence, grounding, or faithfulness meaning;
- D1 precedence, eligibility, routing, or Condition-B applicability;
- reason-code scoring, serialization, predictor inputs, or implementation fields; or
- any historical review's wording.

## 3. Governing clauses

| Constraint | Governing source |
|---|---|
| Condition A is answer image-dependence | Label Specification §4 |
| S1 is Condition A false | Label Specification §5.2 |
| `D1` maps S1 to `unfaithful` and has precedence over D2 | Label Specification §6 |
| D1 failure-mode semantics | Label Specification §8.1–8.3 |
| Grounding is rationale-to-visual-content correspondence | Formal Definitions §15 |
| Grounding is a correlate, not faithfulness | Formal Definitions §15, §17 |
| Reason-code taxonomy is owned by Label Specification | Formal Definitions §18, §35 |
| Changes to taxonomy/meaning are MAJOR; editorial clarification may be PATCH | Label Specification §11; Versioning §2 |
| Normative changes pass BM classification before editing | Release Plan §2.2 |
| V1-008 permits retain-with-disambiguation or governed rename | Release Plan V1-008 |
| Rename requires governance rather than plan authority | Codex audit RPTA-016; Release Plan RPTA-016/SEM-01 disposition |
| Grounding-family name creates answer/rationale ambiguity | Gemini audit SEM-01 |

## 4. Decision drivers

- **Semantic accuracy.** A diagnostic name should describe the condition its code actually records.
- **Vocabulary separation.** `grounding` must retain the rationale-level meaning fixed by Formal
  Definitions §15.
- **Stable machine contract.** Existing code value `D1` and its mapping must not change.
- **No taxonomy change.** The two-code partition and precedence remain exactly as specified.
- **Pre-freeze clarity.** The ambiguity should be removed before the first accepted v1.0 specification
  and before any corpus release.
- **Historical traceability.** Prior review and design artifacts remain dated evidence and are not
  rewritten.
- **Implementation independence.** The decision fixes terminology only, not schemas or code.

## 5. Alternatives and normative consequences

### Alternative A — Retain "Ungrounded answer" unchanged

The current display name remains with no new clarification.

Consequences:

- No textual amendment is required.
- The name continues to suggest a Formal Definitions §15 grounding judgment even though D1 is solely
  Condition A false.
- External readers may confuse answer image-independence with rationale grounding.
- Specifications remain internally decipherable from the meaning column, but the avoidable vocabulary
  collision persists.

This alternative is not preferred because the name is less precise than the rule it labels.

### Alternative B — Retain the name and add normative disambiguation

The display name remains "Ungrounded answer," but §6 and §8.1 explicitly state that it does not use the
Formal Definitions §15 meaning of grounding.

Consequences:

- Code, name, state, and meaning remain unchanged.
- The specification must repeatedly explain why the diagnostic name does not mean what its grounding
  vocabulary normally means in the repository.
- Readers scanning tables, schemas, or reports without the note may still misinterpret it.
- The clarification reduces but does not remove the collision.

This alternative is viable but inferior to a precise display name before freeze.

### Alternative C — Rename only the display name to "Image-independent answer" (recommended)

The diagnostic code remains `D1`; its human-readable name becomes **"Image-independent answer."** The
meaning remains state S1 / Condition A false: the chosen answer is not image-dependent.

Consequences:

- The name directly matches the existing meaning and Formal Definitions §13 vocabulary.
- Grounding remains exclusively the rationale-level correlate defined by Formal Definitions §15.
- `D1`, S1, precedence, label projection, decision tables, examples, scoring, and routes are unchanged.
- The old phrase is recorded as a deprecated historical display name, not an alias code or alternate
  semantic value.
- No released corpus or frozen v1.0 specification requires migration.

This alternative removes the ambiguity with the smallest possible amendment.

### Alternative D — Rename the code or redefine D1 as a grounding failure

The code `D1` would be replaced, or its condition would be changed to assess answer/rationale grounding.

Consequences:

- The reason-code taxonomy or failure-mode semantics would change.
- Existing D1 references, projection, scoring, provenance, and prospective schemas would require
  migration.
- A grounding-based condition would introduce a correlate into the label path and conflict with Label
  Specification I2/I6 and Formal Definitions §15/§17.
- Label Specification §11 would classify the change as MAJOR and presumptively v2.

This alternative is rejected as an out-of-scope semantic redesign.

## 6. Proposed decision

**Adopt Alternative C: retain code `D1` and rename only its display name to "Image-independent
answer."**

Normative consequences upon acceptance:

- **T1 — Stable code.** The diagnostic reason code remains exactly `D1`; no alias code or replacement
  code is introduced.
- **T2 — Stable state and projection.** D1 remains state S1, Condition A false, projected to
  `unfaithful` with D1 precedence.
- **T3 — Display-name clarification.** The human-readable name in Label Specification §6, §8.1, and
  the §5.3 projection diagram becomes "Image-independent answer."
- **T4 — Grounding separation.** D1 does not assert or measure `grounding` as defined by Formal
  Definitions §15. No grounding, plausibility, correctness, or judge signal enters D1 determination.
- **T5 — Historical name disposition.** "Ungrounded answer" is a deprecated historical display name for
  D1. It is not a valid code, distinct state, synonym with separate semantics, or implementation field.
- **T6 — No behavioral change.** Eligibility, Condition A, P6, S1, D1 precedence, routing, provenance,
  scoring, and every label value remain unchanged.
- **T7 — No implementation prescription.** This decision does not prescribe schema field names,
  serialization, UI text beyond the normative display name, or migration code.
- **T8 — Meaning preservation.** The amendment is a pre-freeze terminology clarification, not a change
  to label, state, or reason-code meaning.

## 7. Versioning and compatibility

The amendment changes a descriptive name so that it exactly matches the already-fixed meaning column and
failure-mode rule. It does not add, remove, re-partition, or redefine a reason code. Under Label
Specification §11 and Versioning §2 it is a meaning-preserving editorial clarification, not a MAJOR
taxonomy change.

The repository is pre-freeze and no corpus has been released, so no corpus migration or compatibility
line is required. After v1.0 freeze, any further reason-code terminology change must undergo fresh
classification against the frozen specification and corpus interfaces.

## 8. Required amendments upon acceptance

The amendment list below is authorized by this accepted ADR.

1. **Label Specification (`docs/06_Label_Specification.md`)**
   - §6 diagnostic-reason-code table: change only the D1 **Name** from "Ungrounded answer" to
     "Image-independent answer"; leave the code and Meaning column unchanged.
   - §6 immediately after the table: state that the former phrase "Ungrounded answer" is a deprecated
     historical display name and that D1 is not a Formal Definitions §15 grounding judgment.
   - §5.3 projection diagram: change only the D1 verdict text from "ungrounded-answer verdict" to
     "image-independent-answer verdict"; leave the state mapping and binary label unchanged.
   - §8.1 heading: rename only the heading to "D1 — Image-independent answer (state S1)."
   - §8.1 body: retain the existing Condition-A-false explanation and add one sentence distinguishing D1
     from rationale grounding; make no behavioral edit.
2. **Cross-document verification**
   - Verify that Pipeline, Evaluation Protocol, Data Model, Dataset Specification, and Assurance use the
     stable code `D1` rather than depending on the old display name; edit none unless an exact normative
     occurrence is found.
   - Preserve dated reviews, assessments, dependency graphs, and synchronization reports as historical
     evidence; do not rewrite their terminology.
3. **Release evidence**
   - Record ADR-008 acceptance, V1-008 completion, change classification, decision-index traceability,
     independent review, and the exact §6/§8.1 diff.
   - Include the old/new display-name check in V1-028 terminology normalization and V1-029/V1-030 release
     QA without creating a second code value.

No amendment to Formal Definitions, the `D1` code, state S1, label meaning, Pipeline behavior, scoring,
information boundaries, accepted ADRs, or implementation is authorized.

## 9. Acceptance and review criteria

The BM accepted ADR-008 on 2026-07-03 after independent review confirmed:

1. `D1` remains the sole machine code for state S1;
2. S1, Condition A false, D1 precedence, and the `unfaithful` projection remain unchanged;
3. "Image-independent answer" accurately describes the existing D1 Meaning column;
4. the amendment does not redefine Formal Definitions §13 image-dependence or §15 grounding;
5. grounding, plausibility, correctness, and judge signals remain outside D1 determination;
6. no reason code, state, label value, route, field, or ontology entry is added or removed;
7. the former name is historical terminology only, not an alias code or separate semantic value;
8. the versioning classification is meaning-preserving and valid before first freeze;
9. the amendment list is limited to Label Specification §5.3/§6/§8.1 and release evidence;
10. historical evidence remains unchanged; and
11. no implementation work is authorized.

## 10. Consequences

**Positive**

- Aligns the D1 name with its exact causal condition.
- Preserves `grounding` for the rationale-level correlate defined in Formal Definitions.
- Removes ambiguity before schemas, corpora, and public reports freeze.
- Keeps the stable code and every behavioral contract unchanged.

**Negative / accepted costs**

- Historical materials continue to contain the former name and require readers to recognize it as dated
  terminology.
- Any downstream UI or documentation created before freeze must use the new display name, though no
  implementation migration exists yet.
- The Label Specification needs a brief historical-name note until terminology QA confirms the public
  normative surface is consistent.

## 11. Links

- [Label Specification](../docs/06_Label_Specification.md) §§4–6, 8.1–8.3, 11–12
- [Formal Definitions](../docs/05_Formal_Definitions.md) §§13, 15, 17–18, 35
- [Decision Records Convention](../docs/conventions/decision-records.md) §§3, 6–10, 12
- [Versioning Convention](../docs/conventions/versioning.md) §2
- [Execution and Release Plan](../docs/design/Benchmark_v1.0_Release_Plan.md) §§2.2, V1-008, RPTA-016, SEM-01
- [Specification Synchronization Report](../docs/design/Specification_Synchronization_Report.md)
- [Codex Release-Plan Technical Audit](../reviews/codex/release_plan_technical_audit.md) RPTA-016
- [Gemini Scientific/Governance Audit](../reviews/gemini/release_plan_scientific_governance_audit.md) SEM-01
