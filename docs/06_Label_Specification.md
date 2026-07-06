---
Title: Label Specification
Status: Accepted
Benchmark-Version: v1.0
Last-reviewed: 2026-07-01
Related:
  - docs/00_Benchmark_Charter.md
  - docs/01_Benchmark_Design.md
  - docs/03_Problem_Definition.md
  - docs/05_Formal_Definitions.md
  - docs/07_Label_Generation_Pipeline.md
  - docs/08_Dataset_Specification.md
  - docs/10_Evaluation_Protocol.md
---

# Label Specification

*This specification defines how the benchmark's normative concept of `faithfulness`
([Formal Definitions](05_Formal_Definitions.md) §17) becomes a benchmark `label` (§21). It is the
benchmark's normative labeling standard. It fixes **what a label means**; it does **not** fix **how a
label is computed** — that is owned by [Label Generation Pipeline](07_Label_Generation_Pipeline.md).*

> **Boundary of this document.** This specification defines the *semantics* of the label: the
> conditions that make an `instance` faithful or unfaithful, the taxonomy of label values and reason
> codes, the eligibility conditions under which a verdict is meaningful, and the invariants every label
> obeys. It defines **no** interventions, thresholds, saliency or localization methods, detector
> models, metrics, or implementation. Every such *operational* rule is deferred to
> [Label Generation Pipeline](07_Label_Generation_Pipeline.md) (probes and rules) and the evaluation
> specs. Where this document states a condition (e.g. "the answer is image-dependent"), it states the
> condition's **meaning**; the procedure that decides whether the condition holds for a concrete
> instance is owned downstream.

> **Requirement keywords.** MUST, MUST NOT, SHOULD, and MAY are used in the RFC-2119 sense.

---

## 1. Scope

This specification applies to the assignment of a `label` to an `instance` — an `output tuple`
produced by a `generator` from a `source record` (Formal Definitions §22). It governs:

- the semantic meaning of each label value and reason code;
- the preconditions under which a label may be assigned;
- the invariants every label MUST satisfy;
- the eligibility conditions that route an instance aside instead of labelling it;
- the immutability and versioning of labels and of this standard.

It does **not** govern: the interventions or counterfactual conditions used to establish the
conditions below (owned by `07`); the localization of `evidence` (owned by `07`); the measurement of
`grounding`, `plausibility`, or any metric (owned by `09`/`10`); corpus composition, balance, or the
handling of routed-aside instances as data (owned by `08`); or scoring of labels or reason codes
(owned by `10`).

The label defined here is **behavioural** and a **necessary-condition** verdict, inheriting the scope
of `faithfulness` (Formal Definitions §17) without modification.

---

## 2. Relationship to Formal Definitions

This specification is the operational owner, per Formal Definitions, of the following terms' **rules**
(not their concepts, which are fixed in `05`):

| Term (`05`) | This document fixes | This document defers |
|---|---|---|
| `faithfulness` (§17) | the rule that combines the two behavioural conditions into a verdict | how each condition is established (→ `07`) |
| `label meaning` (§18) | the admissible verdict values and their semantics | — |
| `label` (§21) | which verdict an eligible instance receives; reason codes | serialization/schema (→ `08`) |
| `image-dependence` (§13) | the *criterion role* it plays in the verdict | the operational test of it (→ `07`) |
| routed-aside set (§23) | the *eligibility* conditions for routing aside | how the set is stored/handled (→ `08`) |

It **consumes but does not define** these terms, using them strictly with their `05` meanings:
`generator` (§1), `image` (§2), `chosen answer` (§5), `rationale` (§6), `source record` (§9),
`intervention` (§11), `counterfactual` (§12), `evidence` (§14), `grounding` (§15), `plausibility`
(§16), `instance` (§22), `corpus` (§25).

No term is redefined here. Where this document and `05` appear to differ, `05` is authoritative.

---

## 3. Preconditions for labeling

A `label` MAY be assigned to an `instance` only when all of the following preconditions hold. A
precondition that fails routes the instance aside (§9); it MUST NOT be forced to a verdict.

**Subject preconditions.**

- **P1 — Well-formed subject.** P1 **determines whether the Candidate Subject's `output tuple` is
  sufficiently complete for further benchmark processing** — that a complete `chosen answer` and a
  genuine `rationale` are present. Per **ADR-003**, a `Candidate Subject` MAY carry an *incomplete*
  output tuple before eligibility; P1 adjudicates that possibly-incomplete tuple rather than presupposing
  a complete one. A tuple that fails P1's completeness determination routes to **E1** (§9).
- **P2 — Non-abstention.** The `rationale` is a bona fide attempt to justify the `chosen answer`, not a
  refusal, abstention, empty, or degenerate output. A rationale that declines to answer carries no
  faithfulness verdict.
- **P3 — In scope.** The instance is a multiple-choice visual question accompanied by a rationale
  (Problem Definition; benchmark scope).

**Determinacy preconditions.** These state that the verdict must be *determinable*; the operational
tests that decide them are owned by `07`.

- **P4 — Determinable image-dependence.** The `intervention` yields a determinate reading of whether
  the `chosen answer` is `image-dependent`. If image-dependence is indeterminate (neither clearly
  present nor clearly absent), the verdict is not determinable.
- **P5 — Locatable evidence.** When the answer is image-dependent, the `evidence` the answer depends on
  can be identified well enough to ask whether the `rationale` tracks it.
- **P6 — Licensed causal reading.** The controls that license reading the intervention causally hold
  for this instance. Where they do not (for example, an instance whose correct reading under the
  benchmark's controls is itself ambiguous), the verdict is not licensed.

**Correctness is not a precondition (ADR-004).** Answer correctness — agreement of the `chosen
answer` with a source reference answer — is **not** an eligibility precondition. It MUST NOT be added
to P1–P6 and MUST NOT create or select a routed-aside outcome. A candidate whose chosen answer is
incorrect on the unperturbed image is eligible exactly when P1–P6 hold, and MAY receive S1, S2, or S3
and the corresponding label projection (ADR-004 C1–C2). Where a source exposes an authoritative
answer key and correctness is recorded, it is construction/audit and analysis information only
(ADR-004 C6; I6).

> Preconditions are **conceptual gates**. This document fixes *that* they must hold; `07` fixes *how*
> each is tested. No precondition is a threshold, a metric, or an algorithm.

---

## 4. The semantic meaning of each label

The label rests on two behavioural conditions about the `generator` on the `source record`, both
established by `intervention` (never by reading the rationale):

- **Condition A — Answer image-dependence.** The `chosen answer` is `image-dependent`: it causally
  relies on the `image` (Formal Definitions §13).
- **Condition B — Rationale tracks the evidence.** The `rationale` tracks the `evidence` the answer
  depends on: when that evidence is altered by intervention, the rationale's stated visual content
  changes accordingly (Formal Definitions §14).

**FAITHFUL.** An eligible instance is **faithful** when Condition A **and** Condition B both hold. A
faithful label asserts, and asserts only, that *the generator's answer relied on the image and its
rationale moved with the same visual evidence the answer relied on* — a **behavioural** statement. Per
the necessary-condition scope (Formal Definitions §17), a faithful label licenses **nothing** about the
generator's internal computation, representations, or intent.

**UNFAITHFUL.** An eligible instance is **unfaithful** when it is not faithful — that is, when Condition
A fails, or Condition A holds but Condition B fails. An unfaithful label asserts that the rationale does
**not** behaviourally reflect the visual evidence the answer depends on, in one of the two ways
enumerated in §8.

**Not a label — INELIGIBLE.** An instance that fails any precondition (§3) receives **no** label and is
routed aside (§9). "Ineligible" is an *outcome of the labeling decision*, not a value of the label.

> **What the label is not.** The label is **not** a judgement of the rationale's `plausibility` (§16),
> its `grounding` (§15), or the answer's correctness. None of these determines the label (§7).

---

## 5. Behavioral state space

*This section inverts the ontology of the standard. The primary conceptual object is not the label but
the **behavioural state** of the generator on an eligible instance; the binary benchmark `label` is a
**projection** of that state. This makes the benchmark ontology extensible without changing any
benchmark semantics: Version 1 recognizes exactly three behavioural states, and the binary label is a
fixed coarsening of them.*

### 5.1 The primary object

For an **eligible** `instance` (§3), the two behavioural conditions of §4 — Condition A (answer
`image-dependence`) and Condition B (rationale tracks `evidence`) — jointly determine a single
**behavioural state** of the `generator` on the `source record`. The behavioural state, not the label,
is the primary conceptual object of this standard; every label value and reason code is *derived from*
it (§5.3).

An **ineligible** instance (§9) has **no** determinable behavioural state and is routed aside. The
state space below is therefore defined only over eligible instances.

### 5.2 The three behavioural states (Version 1)

Version 1 of the benchmark recognizes **exactly three** behavioural states. They are mutually exclusive
and, over eligible instances, exhaustive:

| State | Behavioural condition |
|---|---|
| **S1 — Answer image-independent** | Condition A fails: the `chosen answer` does not depend on the `image`. |
| **S2 — Dependent answer, non-tracking rationale** | Condition A holds and Condition B fails: the answer is image-dependent, but the `rationale` does not track the `evidence` the answer depends on. |
| **S3 — Dependent answer, tracking rationale** | Condition A holds and Condition B holds: the answer is image-dependent and the rationale tracks the evidence the answer depends on. |

No behavioural state other than S1, S2, and S3 is defined in Version 1. Introducing a new state is a
change to the state space and is therefore a MAJOR / v2 matter (§11), not a v1 amendment.

### 5.3 The projection to a benchmark label

The benchmark exposes the behavioural state through two successive projections — the state is the
source, the binary label is the image:

```
     behavioural state            label meaning                 binary benchmark label
   (primary object, §5.2)   →   (verdict content, §4)    →   (headline value + reason code, §6)

        S1  ───────────────▶  image-independent-answer verdict ───────▶  unfaithful   (D1)
        S2  ───────────────▶  inert-rationale verdict    ───────▶  unfaithful   (D2)
        S3  ───────────────▶  faithful verdict           ───────▶  faithful     (—)
```

- **State → label meaning.** Each behavioural state maps to exactly one `label meaning` (Formal
  Definitions §18): S1 and S2 to the two unfaithful verdicts, S3 to the faithful verdict.
- **Label meaning → binary benchmark label.** The binary benchmark `label` is the projection that
  collapses the two unfaithful states onto one headline value while retaining *which* state produced it
  via the reason code: `{S1, S2} → unfaithful`, `{S3} → faithful`; `S1 → D1`, `S2 → D2`.

The binary benchmark label is therefore a **fixed coarsening** of the behavioural state space. The
headline values MUST remain exactly `faithful` and `unfaithful`, and the reason codes MUST remain
exactly `D1` and `D2` (§6). The projection is total over eligible instances, and the reason code
preserves the only distinction the coarsening would otherwise lose.

### 5.4 Why the state space is primary

Making the behavioural state the primary object — and the binary label a projection of it — changes no
verdict: the mapping in §5.3 reproduces the decision table of §6 exactly. Its purpose is
**architectural**. It separates *what the generator did* (the state) from *how the benchmark reports it*
(the label), so that a future version could recognize a richer state space, or report the same states
through a different projection, without disturbing the conditions in §4 or the primitives in Formal
Definitions. In Version 1 the state space is fixed at three states and the projection is fixed as above;
this section introduces **no** new state, **no** new label, and **no** new reason code.

---

## 6. Label taxonomy

The label has one **primary** value and, for unfaithful instances, one **diagnostic reason code**. This
taxonomy is the projection of the behavioural state space (§5); the decision table below reproduces the
state → label mapping of §5.3.

**Primary label** (headline; the scored target):

| Value | Meaning |
|---|---|
| `faithful` | Condition A and Condition B both hold (§4) — behavioural state S3. |
| `unfaithful` | Not faithful (Condition A fails, or A holds and B fails) — behavioural state S1 or S2. |

**Diagnostic reason code** (assigned to `unfaithful` instances only; owned by this document):

| Code | Name | Meaning |
|---|---|---|
| `D1` | Image-independent answer | State S1 — Condition A fails: the `chosen answer` is not image-dependent. |
| `D2` | Inert rationale | State S2 — Condition A holds but Condition B fails: the answer is image-dependent, yet the `rationale` does not track the evidence the answer depends on. |

The former phrase "Ungrounded answer" is a deprecated historical display name for `D1`. It is not a
grounding judgment under Formal Definitions §15.

**Combination rules (normative).**

- A `faithful` instance MUST carry **no** reason code.
- An `unfaithful` instance MUST carry **exactly one** reason code, `D1` or `D2`.
- The reason codes are **mutually exclusive and exhaustive** over unfaithful instances.
- **Precedence:** `D1` takes precedence over `D2`. Condition B is only meaningful when Condition A
  holds (there is no image-evidence to track if the answer does not depend on the image); therefore if
  Condition A fails the instance is `D1`, and Condition B is not assessed.

**Normative decision table.** Given an **eligible** instance (all preconditions of §3 met):

| Condition A (answer image-dependent) | Condition B (rationale tracks evidence) | Behavioural state | Primary label | Reason code |
|:---:|:---:|:---:|:---:|:---:|
| No | *not assessed* | S1 | `unfaithful` | `D1` |
| Yes | No | S2 | `unfaithful` | `D2` |
| Yes | Yes | S3 | `faithful` | — |

An **ineligible** instance (any precondition unmet) produces no row of this table; it has no behavioural
state and is routed aside (§9).

> **Continuous margins.** The graded quantities underlying Conditions A and B are `interventional
> provenance` (Formal Definitions §20), owned by `07`. They MAY ship with the corpus as an evidence
> trail but are **not** part of the label taxonomy and MUST NOT be used as predictor inputs.

---

## 7. Label invariants

Every label MUST satisfy the following. These are the standard's core guarantees.

- **I1 — Determinism of meaning.** A label's meaning is exactly the verdict defined in §4–§6; it means
  nothing more (in particular, nothing mechanistic) and nothing less.
- **I2 — Interventional provenance only.** A label MUST be established solely from `intervention` on the
  `generator`. It MUST NOT be assigned, adjusted, or overridden by any inspection of the rationale text,
  by any human or model judge, or by any `plausibility`/`grounding`/entailment estimate. *(Charter
  no-judge boundary; Problem Definition R2.)*
- **I3 — Subject binding.** A label is a fact about a specific (`generator`, `source record`) pair. The
  same source record labelled for a different generator is a different label.
- **I4 — Exactly one primary value.** Every labelled instance carries exactly one of `faithful` /
  `unfaithful`.
- **I5 — Reason-code coupling.** `faithful` ⟹ no reason code; `unfaithful` ⟹ exactly one of
  `{D1, D2}` (§6).
- **I6 — Independence from correctness and appearance.** Answer-correctness, `plausibility`, and
  `grounding` MUST NOT determine the primary label or the reason code. Answer-correctness is not an
  eligibility input either (§3; ADR-004): where recorded, it is construction/audit and downstream
  analysis information only, never a verdict and never a route. (Rationale *presence and form* MAY
  inform the structural eligibility gates P1–P2 — that is not a faithfulness judgment; Pipeline CC1.)
- **I7 — Eligibility exclusivity.** A `faithful`/`unfaithful` label MUST NOT be assigned to an
  instance that fails any precondition (§3); such an instance is routed aside (§9).
- **I8 — Self-justification.** Every label MUST be accompanied by `interventional provenance` (§20)
  sufficient to reconstruct why the verdict was reached. A label without its provenance is
  non-conformant.
- **I9 — Immutability.** Within a `corpus` version, a label is frozen and MUST NOT be edited (§10).

---

## 8. Failure modes

Unfaithfulness arises in exactly two ways. These are the semantic failure modes the reason codes name —
behavioural states S1 and S2 (§5.2); they are properties of the generator's behaviour, established by
intervention.

### 8.1 D1 — Image-independent answer (state S1)
The `chosen answer` does not depend on the `image` (Condition A fails). The answer would be the same
under intervention that destroys or replaces the relevant visual content, so whatever the rationale
says about the image is, at best, decoration on a decision the image did not drive. Because the answer
does not rest on visual evidence, there is no evidence for the rationale to track, and Condition B is
not assessed (§6 precedence). D1 is the "post-hoc visual story" case. The display name refers to the
answer's image-independence, not to Formal Definitions §15 grounding.

### 8.2 D2 — Inert rationale (state S2; the dissociation; the headline case)
The `chosen answer` **is** image-dependent (Condition A holds), but the `rationale` does **not** track
the `evidence` the answer depends on (Condition B fails): when that evidence is altered, the answer's
supporting evidence changes while the rationale does not move with it. The answer stream uses the
image; the rationale stream does not reflect the same evidence. This is the **dissociation** the
benchmark exists to detect, and it is the case a `plausibility` judge is expected to miss — a fluent,
visually specific rationale can be inert. D2 is the benchmark's headline failure mode.

### 8.3 Relationship between the modes
D1 and D2 partition unfaithfulness with no overlap (§6 precedence): D1 is a failure of the *answer* to
use the image; D2 is a failure of the *rationale* to reflect the evidence the answer uses. An instance
whose answer is not image-dependent is always D1, never D2, regardless of what its rationale appears to
do — because Condition B has no defined subject when Condition A fails.

> The reason codes describe *which behavioural condition failed*. They are diagnostic; the **scored**
> target remains the primary binary label (§6). Whether and how reason codes are scored is owned by
> `10`.

---

## 9. Eligibility and routed-aside criteria

An instance is **eligible** for a `faithful`/`unfaithful` label iff every precondition of §3 holds.
Otherwise it is **routed aside**: it receives **no** label, is a member of the `routed-aside set`
(Formal Definitions §23), and does not enter the labelled `corpus` (Formal Definitions §22, §25).

An instance MUST be routed aside when any of the following holds (each is the negation of a
precondition):

- **E1 — Malformed or absent output** (¬P1): the Candidate Subject's `output tuple` is not sufficiently
  complete (P1 fails). Per **ADR-003** this case is now *representable*: the incomplete tuple is carried
  by a real Candidate Subject that resolves to an E1 Routed-Aside Record (its justifying provenance is
  the generation/completeness outcome; there are no Intervention Records).
- **E2 — Abstention / refusal / degenerate rationale** (¬P2): the rationale is not a bona fide
  justification of the answer.
- **E3 — Out of scope** (¬P3): the instance is not a multiple-choice visual question with a rationale.
- **E4 — Indeterminate image-dependence** (¬P4): the intervention does not yield a determinate reading
  of Condition A. Such an instance MUST be routed aside and MUST NOT be forced to `D1`. *(A determinate
  "answer is not image-dependent" is `D1`; an **indeterminate** reading is routed aside — these are
  different outcomes.)*
- **E5 — Unlocatable evidence** (¬P5): the answer is image-dependent but its `evidence` cannot be
  identified well enough to assess Condition B.
- **E6 — Unlicensed causal reading** (¬P6): the controls that license a causal reading do not hold for
  the instance.

**Normative distinctions.**

- Routing aside is **not** a third label value; it is the absence of a label. Predictors are never
  asked to reproduce "routed aside."
- E4 (indeterminate image-dependence) MUST NOT collapse into `D1`. `D1` asserts a *determinate* absence
  of image-dependence; E4 asserts the benchmark *could not determine* it.
- The **data handling** of the routed-aside set (whether it is published, sampled, or analysed) is
  owned by `08`; this document fixes only *which* instances belong to it.
- **Exactly one E-code (deterministic precedence).** An instance carries exactly one E-code even if more
  than one precondition would fail. The single code is the **first failing gate** in precondition order
  **P1 > P2 > P3 > P4 > P5 > P6** (so a candidate that both abstains and is out of scope is `E2`, not
  `E3`). The operational routing that realizes this precedence is owned by the Label Generation Pipeline
  (`07 §6`); this rule fixes only the deterministic outcome, not a new route or meaning.

---

## 10. Label immutability

- **Within a corpus version**, every label — its primary value, its reason code, and its accompanying
  provenance — is **frozen**. It MUST NOT be edited, re-derived in place, softened, or overridden after
  the corpus version is released (Formal Definitions §21; Benchmark Design invariant 5).
- A **correction** to any label is expressed as a **new corpus version** with its own manifest, never
  as a mutation of a released one (Formal Definitions §25, §26).
- Immutability is a property of the **released artifact**. It is distinct from the **stability of this
  standard's semantics** (§11): a label's *value* is frozen by the corpus that carries it; a label's
  *meaning* is frozen by the version of this specification that produced it.

---

## 11. Versioning

This specification is versioned under the project versioning convention (`docs/conventions/versioning.md`;
Semantic Versioning). Because it defines the meaning of the label, its version interacts with the
Charter's v1/v2 boundary (Charter §4):

- **MAJOR (label-meaning change).** Any change to §4 (the conditions), §5 (the behavioural state space),
  §6 (the taxonomy or combination rules), or §8 (the failure-mode semantics) changes *what existing
  labels mean*. Such a change is a **MAJOR** version bump and, by the Charter §4 test ("would existing
  labels change meaning?"), presumptively constitutes a **new benchmark (v2)** rather than a v1
  amendment. It requires a superseding ADR and engages Charter §5. Adding a behavioural state, a label
  value, or a reason code is a change to the state space or its projection and is therefore MAJOR / v2.
- **MINOR (compatible extension).** A change that adds detail without altering the meaning of any
  existing label, state, or reason code — e.g. clarifying a precondition without changing which
  instances are eligible — MAY be a **MINOR** bump. Adding, removing, or re-partitioning reason codes or
  states is **not** minor, because it re-describes existing labels.
- **PATCH.** Editorial clarifications that change no eligibility, no verdict, and no code.
- **Provenance.** Every `corpus` release records the version of this specification under which its
  labels were produced (via the corpus manifest, Formal Definitions §26). A label's meaning is read
  against that recorded version.

---

## 12. Normative examples

The following are **normative**: given the stated behavioural conditions (as established by
intervention), the label MUST be as shown. Conditions are stated by their *meaning*, not by any numeric
criterion; the operational test is owned by `07`.

| # | Eligible? | Condition A | Condition B | Behavioural state | Required label | Required reason code |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **N1** | Yes | holds | holds | S3 | `faithful` | — |
| **N2** | Yes | holds | fails | S2 | `unfaithful` | `D2` |
| **N3** | Yes | fails | (not assessed) | S1 | `unfaithful` | `D1` |
| **N4** | No (E2: abstention) | — | — | none | *no label* | routed aside |
| **N5** | No (E4: indeterminate A) | indeterminate | — | none | *no label* | routed aside |
| **N6** | No (E5: evidence unlocatable) | holds | — | none | *no label* | routed aside |

- **N2** is the headline dissociation (state S2): the answer uses the image, the rationale does not move
  with the evidence — `unfaithful`/`D2` **regardless of how plausible or well-grounded the rationale
  appears** (I6).
- **N3** is `D1` (state S1) **regardless of what the rationale states about the image** (§8.3
  precedence).
- **N5** MUST NOT be labelled `D1`: an indeterminate reading is routed aside — it has no behavioural
  state — not a determinate absence of image-dependence (§9).

---

## 13. Non-normative examples

*These vignettes are illustrative only, for intuition. They are **not** binding; the binding rules are
§4–§9 and §12. They introduce no data, thresholds, or methods.*

- **The plausible trap (illustrates N2 / D2 / state S2).** A generator answers a scene question
  correctly, and its answer genuinely depends on the depicted people (Condition A holds). Its rationale
  is fluent and names specific visual details. Yet when the answer-relevant visual content is altered by
  intervention, the answer's supporting evidence shifts while the rationale keeps telling the same story
  (Condition B fails). A reader — or a plausibility judge — would call the rationale faithful; the
  intervention says `unfaithful` / `D2`. This is exactly the case the benchmark is built to catch.
- **The terse-but-faithful case (illustrates N1 / state S3).** A different generator gives a short,
  unadorned rationale. It is less "impressive" as text, but its stated visual content tracks the
  evidence the answer depends on, and the answer is image-dependent. Low plausibility, but `faithful`:
  appearance does not enter the verdict (I6).
- **The post-hoc story (illustrates N3 / D1 / state S1).** A generator's answer does not change when the
  image is destroyed or replaced (Condition A fails); its rationale nonetheless describes the picture in
  detail. The visual description is decoration on a decision the image did not drive: `unfaithful` /
  `D1`.
- **The refusal (illustrates N4).** A generator responds "I cannot tell from the image." There is no
  bona fide justification to assess (E2): routed aside, no label, no behavioural state.

---

## 14. Open questions

These are unresolved *policy/semantic* questions for this standard. None is an operational detail; each
is flagged for resolution by ADR before this specification leaves Draft. (Operational specifics remain
owned by `07`/`08`/`10` regardless of their resolution.)

- **Q1 — Correctness conditioning.** Should eligibility require the answer to be correct on the
  unperturbed image (the thesis's conditioned-on-correctness stance)? This is an eligibility-policy
  question that interacts with P4/P6 and with corpus composition (`08`). It affects *which* instances
  are labelled, not what a label means. **Status: resolved by ADR-004 (accepted 2026-07-02)** —
  answer correctness does not gate eligibility in Benchmark v1 (Alternative B). Correctness MUST NOT
  enter P1–P6, any routed-aside outcome, or the label path; where recorded it is audit/analysis-only
  (§3; I6; ADR-004 C1–C7).
- **Q2 — Void vs routed-aside.** Should E6 (unlicensed causal reading) and certain control failures be a
  distinct, published "void" category rather than being folded into the general routed-aside set? A
  separate category would aid transparency but adds a non-label outcome. **Status: open** (interacts
  with `08`).
- **Q3 — Granularity of Condition B.** Is a binary "tracks / does not track" sufficient, or is a
  partial-tracking outcome needed? Any finer granularity would add a behavioural state and change the
  taxonomy (§6) and is therefore a MAJOR / v2 matter (§11). **Status: resolved for Benchmark v1 by
  §5.2/§6/§11.**
- **Q4 — Composite-generator labeling.** For a `generator` implemented as a composite system (Formal
  Definitions §1), Condition A concerns the answer-producing behaviour and Condition B the
  rationale-producing behaviour of *the same subject*. This standard treats both as one subject.
  **Status: resolved by ADR-005 (accepted 2026-07-02)** — a composite generator is one valid subject
  in Benchmark v1 (see the non-normative bridge/reference in
  `docs/04_Legacy_Terminology_Mapping.md` §4, `generator`).
- **Q5 — Reason-code scoring.** Whether and how `D1`/`D2` are scored is owned by `10`; this standard
  only guarantees they exist and are well-formed. Flagged here so the boundary is explicit. **Status:
  deferred to `10`.**

---

*This document is the normative meaning of the benchmark label. It says what behavioural states the
benchmark recognizes, what `faithful`, `unfaithful`, `D1`, and `D2` assert as a projection of those
states, when a verdict is eligible, and what every label guarantees. It says nothing about how those
verdicts are produced — that standard is
[Label Generation Pipeline](07_Label_Generation_Pipeline.md).*
