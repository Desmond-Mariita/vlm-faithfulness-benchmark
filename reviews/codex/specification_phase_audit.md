# Specification Phase Implementation Audit

**Audit date:** 2026-07-01  
**Scope:** the specification, ADR, traceability, DAG, and implementation-inventory documents listed in the audit request, cross-checked against the thesis repository where the suite makes implementation claims.  
**Audit posture:** implementation-facing only. This report does not redesign the benchmark or propose new research directions.

The suite has a coherent high-level construct and ADR-002/ADR-003 are substantially reflected in the current base documents. It is not yet a closed implementation contract. The principal risks are unresolved semantic policy, a contradictory pipeline branch, undefined operational profiles, stale design authorities, and release/evaluation contracts that cannot yet be enforced mechanically.

## Findings

### SPA-001 — Correctness eligibility is unresolved

- **Severity:** Blocker
- **Affected document(s):** `docs/06_Label_Specification.md` §14 Q1; `docs/07_Label_Generation_Pipeline.md` §10; `docs/08_Dataset_Specification.md` §19; `docs/10_Evaluation_Protocol.md` §§8, 16; `docs/design/Specification_Traceability_Matrix.md` §8 A04
- **Exact issue:** The suite does not decide whether unperturbed answer correctness is an eligibility condition. `06` calls Q1 unresolved; `07` says the affected stages cannot claim conformance until it is resolved; `08` and `10` specify corpus and reporting behavior conditionally. The thesis implementation is correctness-centric, so coding against existing behavior would silently choose one policy.
- **Why it matters:** This changes which generator/source pairs receive labels and therefore changes the benchmark population, split distributions, routed-aside accounting, and every reported result. There is no neutral implementation default.
- **Recommended action:** Ratify the correctness policy before implementing eligibility or corpus assembly, then synchronize P-gates, E-code behavior, manifest fields, and correctness reporting.
- **Action requires:** ADR + document edit

### SPA-002 — Composite-generator subject identity is unresolved

- **Severity:** Blocker
- **Affected document(s):** `docs/05_Formal_Definitions.md` §1; `docs/06_Label_Specification.md` §14 Q4; `docs/06a_Benchmark_Data_Model.md` R1–R3; `docs/07_Label_Generation_Pipeline.md` §10; `docs/04_Legacy_Terminology_Mapping.md` §4; `docs/design/Label_Generation_Pipeline_Implementation_Inventory.md` §§3.2, 11, 13
- **Exact issue:** `05` permits a composite generator and current artifact identity rules assume it is a single subject, while `06` still marks the validity of the thesis's two-checkpoint answer/rationale generator as open. The thesis has separate Stage-1 and Stage-2 checkpoints and does not serialize one composite identity per instance.
- **Why it matters:** Every label, intervention, counterfactual, and instance ID is defined on one generator/source pair. If the two components are not one valid subject, S02–S15 target the wrong unit; if they are, the exact identity and configuration of both components must be bound before any output is generated.
- **Recommended action:** Ratify the composite-subject policy and specify the minimum composite identity constituents consumed by S02/S03.
- **Action requires:** ADR + document edit

### SPA-003 — The normative pipeline contains an impossible P6 path for S1/D1

- **Severity:** Blocker
- **Affected document(s):** `docs/06_Label_Specification.md` §§3, 6; `docs/07_Label_Generation_Pipeline.md` §§3, 5 S09–S12, 6; `docs/design/Label_Generation_Pipeline_DAG.md` §§4, 6
- **Exact issue:** `06` requires P6 for every labelled instance. `07` §6 correctly says an A-false candidate must pass P6 before S1, but the overview sends A-false directly to S12, S09 runs only on A-true candidates, and S10's precondition says interventions from both S06 and S09 have been observed. An A-false candidate cannot satisfy that S10 precondition. The DAG also sends determinate A-false directly to S1/D1.
- **Why it matters:** A literal implementation must either bypass a mandatory eligibility gate, run an inapplicable rationale intervention, or invent a second control path. Those implementations produce different D1 populations.
- **Recommended action:** Define the executable A-false control path and make the overview, S10 preconditions, branch table, and DAG agree. If P6 has different applicable evidence by branch, state that explicitly.
- **Action requires:** document edit

### SPA-004 — The label-producing operational profile is undefined

- **Severity:** Blocker
- **Affected document(s):** `docs/05_Formal_Definitions.md` §§11–14, 17, 20; `docs/07_Label_Generation_Pipeline.md` §§5, 9–11; `docs/08_Dataset_Specification.md` N10.7; `docs/11_Benchmark_Assurance.md` §9; `docs/design/Label_Generation_Pipeline_Implementation_Inventory.md` §§5–7, 13–14
- **Exact issue:** `07` defers the intervention set, localization, controls, all P1–P6 criteria, both A/B criteria, graded readings, and thresholds to implementation while claiming independent teams can implement conformantly. `08` requires a pinned “Reference Implementation Profile identifier,” but no reviewed document defines that profile, its owner, required contents, approval state, or conformance tests.
- **Why it matters:** These choices are the executable candidate-to-label function. Without a governed profile, two implementations can both satisfy the prose while assigning different states and labels. The current thesis code has no conformant P5 or Condition B implementation, so no existing behavior can serve as the implicit reference.
- **Recommended action:** Before label-path coding, define and assign ownership for the versioned reference profile that pins every deferred label-producing choice and its acceptance tests. Empirical viability may gate mass labeling, but the profile contract itself must exist before implementation.
- **Action requires:** document edit + implementation note

### SPA-005 — ADR-002's observational-provenance boundary is not consistently applied

- **Severity:** Major
- **Affected document(s):** `decisions/ADR-002-Construction-Provenance-Lifecycle.md` Decision/N1–N4; `docs/06a_Benchmark_Data_Model.md` §§3.7, 8 T1; `docs/07_Label_Generation_Pipeline.md` §§5 S04–S11, 7; `docs/design/Label_Generation_Pipeline_DAG.md` §§2, 8
- **Exact issue:** ADR-002 defines observational provenance as raw observations with no determinations. `07` repeatedly accretes P1–P6 and Condition A/B “determinations” into observational provenance, and §7 calls the observational phase “observations and determinations-as-inputs.” `06a` also describes the one artifact as both determining and containing those results.
- **Why it matters:** Implementers cannot tell which values are permitted before sealing, which are production outputs, and which are traceability back-references. This can recreate the production cycle ADR-002 was accepted to remove and makes append-only validation ambiguous.
- **Recommended action:** Reconcile the terminology and lifecycle: enumerate which pre-state values are raw observations, which are derived determinations, when each is appended, and which sealed fields are back-references. Preserve one artifact and one producer as required by ADR-002.
- **Action requires:** document edit

### SPA-006 — Historical traceability documents still make false authoritative statements

- **Severity:** Major
- **Affected document(s):** `docs/design/Specification_Traceability_Matrix.md` §§1, 2, 3, 5–9; `docs/design/Label_Generation_Pipeline_DAG.md` §§1, 4–8, 11–13; `docs/design/Label_Generation_Pipeline_Implementation_Inventory.md` §§1, 13–14; `docs/07_Label_Generation_Pipeline.md` §§1, 6
- **Exact issue:** Synchronization banners say later specs now exist, but the retained bodies still say Charter/Vision and `07`/`08`/`10` are absent, ADR amendments are unapplied, and operational authority is missing. The DAG's canonical graph still requires Intervention Records before eligibility, cannot represent E1 without interventions, bypasses P6 on A-false, and ends with a literal-acyclicity failure despite G1 being marked resolved.
- **Why it matters:** These documents are cited normatively by `07` for stage IDs and branch behavior. A developer following the body rather than the banner will implement a different graph and may treat existing specifications as unavailable.
- **Recommended action:** Replace stale normative tables/graphs with current content or clearly move the historical snapshots outside the authority chain. A banner is insufficient when later sections still call themselves canonical conclusions.
- **Action requires:** document edit

### SPA-007 — Specification freeze and governance status are contradictory

- **Severity:** Major
- **Affected document(s):** `docs/01_Benchmark_Design.md`; `docs/03_Problem_Definition.md`; `docs/05_Formal_Definitions.md`; `docs/06_Label_Specification.md`; `docs/06a_Benchmark_Data_Model.md`; `docs/07_Label_Generation_Pipeline.md`; `docs/08_Dataset_Specification.md`; `docs/09_Baseline_Systems.md`; `docs/10_Evaluation_Protocol.md`; `docs/11_Benchmark_Assurance.md`; `docs/06_Label_Specification.md` §11; `docs/05_Formal_Definitions.md` §36
- **Exact issue:** The phase is described as completed and documents call prior specifications frozen, but every base technical specification is still marked `Draft`; `06` says its policy questions must be resolved before leaving Draft. The referenced `docs/conventions/versioning.md` and `docs/conventions/decision-records.md` do not exist.
- **Why it matters:** Implementers cannot determine whether requirements are stable, what version to stamp into labels/manifests, or which process governs changes. This also makes Assurance BL8 impossible to clear from repository metadata.
- **Recommended action:** Resolve the blockers, instantiate the referenced governance conventions, and perform one explicit Draft-to-Accepted/versioned freeze across the normative suite.
- **Action requires:** document edit

### SPA-008 — Open-question registries are stale and mutually inconsistent

- **Severity:** Major
- **Affected document(s):** `docs/06_Label_Specification.md` §14 Q2–Q5; `docs/06a_Benchmark_Data_Model.md` §10 Q1–Q4; `docs/07_Label_Generation_Pipeline.md` §10; `docs/08_Dataset_Specification.md` §§5, 14, 19; `docs/10_Evaluation_Protocol.md` §§5, 17; `docs/design/Label_Generation_Pipeline_DAG.md` G6
- **Exact issue:** `06` calls E6 publication, binary-vs-partial B, composite validity, and reason-code scoring unresolved. Elsewhere, `08` resolves routed/audit publication as a per-release policy, `07` requires binary B for the v1 path, and `10` resolves reason-code scoring. `06a` still calls baseline-output designation open although `07` S02 and `08` N4.6 prescribe designation and extraction. G6 continues to treat all of these as unresolved.
- **Why it matters:** A developer cannot distinguish live blockers from settled rules or future-version questions. Conformance scope and required fields consequently appear conditional even where downstream specs make them mandatory.
- **Recommended action:** Close or reclassify each question in its owning document and point to the resolving clause/decision. Keep only genuinely live decisions open.
- **Action requires:** document edit

### SPA-009 — “Crossing the boundary” has two incompatible meanings

- **Severity:** Major
- **Affected document(s):** `docs/01_Benchmark_Design.md` §§1, 6, 8, 11; `docs/05_Formal_Definitions.md` §§8, 19–21, 25; `docs/06_Label_Specification.md` §6; `docs/06a_Benchmark_Data_Model.md` §§3.7, 3.9, T6; `docs/08_Dataset_Specification.md` §§12–14
- **Exact issue:** Formal Definitions §8 says the label and interventional provenance do not cross the construction/evaluation boundary, while `01` says the label crosses as a hidden key and provenance is released for transparency, and `06a`/`08` place both in evaluation-world hidden/audit views. Some clauses use “crosses” to mean “exists in evaluation,” while others mean “is a predictor input.”
- **Why it matters:** This is the central security boundary. An implementation may incorrectly omit required audit/key artifacts or, worse, co-package them on the assumption that “released but marked forbidden” is adequate separation.
- **Recommended action:** Adopt one explicit vocabulary for release availability, scoring-only access, audit-only access, and predictor input, then synchronize every boundary table and diagram.
- **Action requires:** document edit

### SPA-010 — Public manifest and stable identity rules can leak generator identity

- **Severity:** Major
- **Affected document(s):** `docs/06a_Benchmark_Data_Model.md` R1, R3, R6–R8, §§3.9–3.10; `docs/08_Dataset_Specification.md` N10.2–N10.4, §§12–14; `docs/09_Baseline_Systems.md` F2
- **Exact issue:** Instance identity is defined as the pair `(composite generator identity, source record identity)`. The public manifest lists Corpus Entry identities and generator identities, while predictor-visible entries carry stable instance identities. The suite never requires the released ID encoding to be opaque/non-derivable or prevents a public mapping/dictionary attack.
- **Why it matters:** Generator identity is forbidden because it is a label proxy, especially for OOD-Model. A deterministic pair encoding or predictable hash would violate the information boundary even if no explicit generator field appears in the predictor view.
- **Recommended action:** State that public predictor IDs must be non-derivable and non-joinable to generator identities for live splits; specify separate internal trace IDs or an access-controlled mapping and add a boundary test.
- **Action requires:** document edit + implementation note

### SPA-011 — Split membership is exposed while use of it is declared forbidden

- **Severity:** Major
- **Affected document(s):** `docs/08_Dataset_Specification.md` N12.1, N12.5, N7.4; `docs/09_Baseline_Systems.md` §§5–7; `docs/10_Evaluation_Protocol.md` K2
- **Exact issue:** The predictor-visible view provides split membership but says a predictor MUST NOT consume it as a feature. The protocol explicitly does not inspect predictor internals, so this prohibition cannot be tested. OOD-Model membership is acknowledged as a generator-family proxy.
- **Why it matters:** Supplying a forbidden feature creates an unenforceable conformance rule and a direct shortcut. Declarations do not protect hidden evaluation.
- **Recommended action:** Keep split membership in the harness/score join rather than model input, or define a mechanically enforceable interface in which the model never receives it.
- **Action requires:** document edit + implementation note

### SPA-012 — Train-label delivery is still under-specified

- **Severity:** Major
- **Affected document(s):** `docs/08_Dataset_Specification.md` N12.1a, §§13–14, 18; `docs/09_Baseline_Systems.md` §§5, 17–18; `docs/10_Evaluation_Protocol.md` §§2, 10
- **Exact issue:** `08` allows Train labels as training material while defining the predictor-visible view as the only artifact a predictor may consume and excluding labels from it. `09` explicitly says the Train-label release facet remains under-specified. No reviewed artifact/interface separates fitting-time labels from prediction inputs.
- **Why it matters:** Every learnable baseline depends on this channel. An ad hoc delivery format can accidentally expose validation/held-out labels or make the “only Output Tuple at prediction” rule unverifiable.
- **Recommended action:** Define the train-label facet, keying, access lifecycle, and negative tests ensuring that only Train IDs join to released training labels.
- **Action requires:** document edit + implementation note

### SPA-013 — Validation labels are used both to select the threshold and to report the primary endpoint

- **Severity:** Major
- **Affected document(s):** `docs/08_Dataset_Specification.md` N12.1a; `docs/09_Baseline_Systems.md` F4–F5; `docs/10_Evaluation_Protocol.md` P1–P3, R1–R2
- **Exact issue:** P3 selects/freezes the decision threshold on Validation labels, and P1 then reports Validation macro-F1 at that selected threshold as the sole confirmatory primary endpoint. There is no separate calibration subset or nested selection rule.
- **Why it matters:** The headline score is optimized and evaluated on the same labels, producing optimistic bias and weakening its confirmatory interpretation. Implementations cannot fix this without changing the specified evaluation procedure.
- **Recommended action:** Separate operating-point selection from confirmatory measurement, or explicitly define a pre-registered/nested selection procedure and adjust the primary endpoint claim.
- **Action requires:** document edit

### SPA-014 — Several scorecard requirements cannot be satisfied for all conformant predictors

- **Severity:** Major
- **Affected document(s):** `docs/09_Baseline_Systems.md` §§12, 16; `docs/10_Evaluation_Protocol.md` §§2, 4–5, 8, 9, 13
- **Exact issue:** Predictions may omit a continuous score and reason code, yet the scorecard requires hard-core AUROC and D1/D2 F1. The oracle MUST NOT be implemented/scored, yet S6/B1 require oracle values for every subset and the scorecard requires baselines and floor/oracle gaps. “Every numeric entry” must carry a CI, support, split, and corpus version, which does not fit a conceptual perfect oracle or a transfer gap spanning two splits.
- **Why it matters:** A conformant hard-label predictor cannot produce the mandatory scorecard, and implementations will invent inconsistent `N/A`, synthetic oracle, and CI rules.
- **Recommended action:** Define mandatory-vs-conditional cells and canonical `not applicable` behavior; distinguish conceptual constants and derived cross-split quantities from sampled metrics.
- **Action requires:** document edit

### SPA-015 — Predictor/baseline information-access conformance is not testable as written

- **Severity:** Major
- **Affected document(s):** `docs/09_Baseline_Systems.md` §§7, 15–16; `docs/10_Evaluation_Protocol.md` §10 K2–K3; `docs/11_Benchmark_Assurance.md` EF3, BL4, AR4
- **Exact issue:** K2 requires proving that a predictor did not use forbidden data or query the generator, while `10` states that internals are not inspected and relies on declarations. Assurance describes the same check as deterministic/judgmental and blocks release on failure without distinguishing mechanically verified facts from attestation.
- **Why it matters:** The system cannot truthfully claim full behavioral conformance for arbitrary external predictors. A declaration is evidence, not a test of non-use.
- **Recommended action:** Partition conformance into harness-verifiable requirements and participant attestations, and report both states distinctly in scorecards and release gates.
- **Action requires:** document edit + implementation note

### SPA-016 — Reproducibility tolerance permits label drift without a stable acceptance rule

- **Severity:** Major
- **Affected document(s):** `docs/03_Problem_Definition.md` A2; `docs/06_Label_Specification.md` I9, §10; `docs/06a_Benchmark_Data_Model.md` M3–M4; `docs/08_Dataset_Specification.md` N10.7, RI7; `docs/10_Evaluation_Protocol.md` Y2a; `docs/11_Benchmark_Assurance.md` LF1, BL5
- **Exact issue:** The construct assumes a stable, freezable verdict, but Y2a permits a per-release bounded label-flip tolerance near operating points. No minimum acceptance principle, adjudication rule for changed labels, or distinction between reproducibility of a frozen release and reproducibility of a stochastic reconstruction is fixed.
- **Why it matters:** A release could be declared reproducible even though its ground-truth labels change. This undermines label immutability, provenance reconstruction, and comparison of rebuilt artifacts.
- **Recommended action:** Define which fields/labels require exact reproduction and how any tolerated stochastic variation is evaluated without treating changed labels as the same frozen corpus.
- **Action requires:** document edit

### SPA-017 — Release artifact ownership and required contents are incomplete

- **Severity:** Major
- **Affected document(s):** `docs/06a_Benchmark_Data_Model.md` §3.10; `docs/08_Dataset_Specification.md` §§10, 18–19; `docs/10_Evaluation_Protocol.md` §§12–14, 17; `docs/11_Benchmark_Assurance.md` GF3, BL8, AR5; `docs/05_Formal_Definitions.md` §26
- **Exact issue:** Releases require a Reference Implementation Profile, corpus datasheet, changelog/lineage record, analysis plan, release report, acceptance comparison, and separated views, but several are not defined as artifacts, have no producing stage/owner, or have only “format deferred” status. The manifest requirements also omit explicit ingestion-exclusion identities/counts even though S01 creates such exclusions.
- **Why it matters:** S18 cannot be implemented as a complete release transaction, and Assurance BL8/AR5 cannot be mechanically cleared. Source exclusions can disappear from end-to-end population accounting before candidacy.
- **Recommended action:** Add an implementation-facing release inventory assigning producer, required minimum contents, identity/version linkage, publication/access class, and manifest reference for every required release artifact and S01 exclusion ledger.
- **Action requires:** document edit + implementation note

### SPA-018 — Artifact ownership violates the architecture's literal one-owner rule

- **Severity:** Major
- **Affected document(s):** `docs/01_Benchmark_Design.md` §§6, 13 BD8; `docs/06a_Benchmark_Data_Model.md` §§3, 5; `docs/design/Label_Generation_Pipeline_DAG.md` §10.2
- **Exact issue:** `01` requires exactly one owning specification per artifact. `06a` assigns Candidate Subject to `06a`/`08` and Routed-Aside Record to `06a`/`06`/`08`, then reinterprets the invariant as one owner per “dimension.” The DAG admits these are literal exceptions.
- **Why it matters:** Schema changes, validation failures, and amendment responsibility can be bounced among form, semantic, and handling owners. “Dimension” is not defined or represented in change control.
- **Recommended action:** Name one canonical artifact owner for each artifact and list other specs as semantic authorities or consumers, without changing the existing responsibility split.
- **Action requires:** document edit

### SPA-019 — Thesis artifacts violate the canonical identity/output assumptions

- **Severity:** Major
- **Affected document(s):** `docs/04_Legacy_Terminology_Mapping.md` §§3–5; `docs/06a_Benchmark_Data_Model.md` R1–R6; `docs/07_Label_Generation_Pipeline.md` CC4, CC6–CC8; `docs/08_Dataset_Specification.md` N4.6; `docs/design/Label_Generation_Pipeline_Implementation_Inventory.md` §§3–12
- **Exact issue:** The thesis has no single artifact containing the exact chosen answer, canonical rationale, source identity, and complete composite-generator identity. Existing rationale probes use gold-answer conditioning, regenerate the baseline rationale, assess inconsistent rationale spans, and join on weak IDs such as `image_id`. Existing run manifests are not bound per candidate.
- **Why it matters:** Reusing these artifacts directly violates subject binding and exact-baseline invariants and can assign a label to behavior from a different output or generator configuration.
- **Recommended action:** Treat the thesis as a source of lower-level capabilities only. Introduce a benchmark-native immutable subject/output envelope and require every probe to consume its identity and exact baseline fields; reject legacy rows that cannot be bound unambiguously.
- **Action requires:** implementation note

### SPA-020 — Thesis ingestion and failure behavior conflicts with accountability rules

- **Severity:** Major
- **Affected document(s):** `docs/07_Label_Generation_Pipeline.md` CC2, S02–S05, S15; `docs/08_Dataset_Specification.md` N3.4, N5.3; `docs/design/Label_Generation_Pipeline_Implementation_Inventory.md` §§4–5, 8–12
- **Exact issue:** The thesis loader silently drops missing records, pads/truncates invalid choices, and treats manifest writing as fail-open; generation and metric paths convert failures to empty strings or filter them. The benchmark requires explicit ingestion exclusions before candidacy and exactly one E-code resolution after candidacy.
- **Why it matters:** Wrapping current loaders/probes would change denominators and erase precisely the cases the no-silent-drop rule is designed to retain.
- **Recommended action:** Make source normalization strict and ledgered; once S03 creates a candidate, prohibit filtering/repair paths and require an immutable routed-aside resolution. Add reconciliation tests across raw records, exclusions, candidates, corpus entries, and routes.
- **Action requires:** implementation note

### SPA-021 — Thesis terminology collisions need schema-level enforcement

- **Severity:** Minor
- **Affected document(s):** `docs/04_Legacy_Terminology_Mapping.md` §§2, 4, 7; `docs/05_Formal_Definitions.md`; `docs/design/Label_Generation_Pipeline_Implementation_Inventory.md` §§7, 11–12
- **Exact issue:** The legacy repository actively uses `label`, `split`, `generator`, `rationale`, `grounding`, `baseline`, `floor`, and `recovery` with meanings different from the benchmark. The mapping is non-normative guidance and no implementation contract requires qualified benchmark field names.
- **Why it matters:** The highest-risk collision is thesis `label` (gold answer index) versus benchmark `Label` (faithfulness verdict); accidental reuse can contaminate both construction and scoring without a type error.
- **Recommended action:** Establish explicit benchmark namespaces/types and reject unqualified legacy names at ingestion and serialization boundaries.
- **Action requires:** implementation note

### SPA-022 — Hard-core production has no single operational owner

- **Severity:** Minor
- **Affected document(s):** `docs/05_Formal_Definitions.md` §30; `docs/08_Dataset_Specification.md` N6.8, N10.6; `docs/09_Baseline_Systems.md` §§9–11, 18; `docs/10_Evaluation_Protocol.md` §§5, 7; `docs/11_Benchmark_Assurance.md` DF5
- **Exact issue:** `08` owns membership but defers plausibility/grounding selectors and matching; `09`/`10` own measurement but do not produce membership; selector implementations must be disjoint from baseline backbones. No role is assigned to choose, validate, and sign off the pinned selector/matcher set.
- **Why it matters:** Hard-core AUROC is the lead discriminative claim. Unowned selector choices can create selection artifacts or violate backbone disjointness.
- **Recommended action:** Assign one operational owner for hard-core construction and require a selector/matcher provenance record plus disjointness check in the release profile.
- **Action requires:** implementation note

### SPA-023 — Human-check and assurance duties lack assigned execution owners

- **Severity:** Minor
- **Affected document(s):** `docs/09_Baseline_Systems.md` §14; `docs/11_Benchmark_Assurance.md` §§1, 11–14; `docs/07_Label_Generation_Pipeline.md`; `docs/08_Dataset_Specification.md`
- **Exact issue:** Assurance assigns abstract roles, and `09` distinguishes an unspecified construction “human check,” but the suite does not designate who owns pipeline validation sampling, who approves operational profiles, or who supplies independent release sign-off in a solo-maintainer repository. `11` itself leaves severity independence and external audit open.
- **Why it matters:** Required validation and release-blocking decisions may exist only on paper, with no accountable executor or evidence artifact.
- **Recommended action:** Before implementation milestones are opened, publish a responsibility assignment for specification ownership, reference-profile approval, construction validation, release management, and assurance sign-off; document how conflicts are handled when one person holds multiple roles.
- **Action requires:** implementation note

### SPA-024 — The current implementation inventory is useful but not a current acceptance baseline

- **Severity:** Informational
- **Affected document(s):** `docs/design/Label_Generation_Pipeline_Implementation_Inventory.md`; `docs/design/Specification_Traceability_Matrix.md`
- **Exact issue:** The inventory is explicitly a pre-specification historical snapshot and correctly concludes that no conformant label path exists. It is nevertheless referenced from current normative documents and contains now-stale claims about absent specifications and unresolved ownership.
- **Why it matters:** Its code-level gap analysis remains valuable, but treating its status tables as current conformance evidence would conflate historical readiness with the implementation acceptance plan.
- **Recommended action:** Retain it as historical evidence and create a separate, versioned implementation acceptance matrix after SPA-001–SPA-023 are resolved.
- **Action requires:** implementation note

# Implementation Readiness Verdict

**Not ready — specification issues remain**

Implementation scaffolding and non-semantic infrastructure can begin, but the label path, corpus assembly, evaluation harness, and release interfaces should not be coded as normative behavior until the Blocker findings are resolved and the Major synchronization/boundary issues have an explicit disposition.
