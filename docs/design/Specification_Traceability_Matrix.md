# Specification Traceability Matrix

> **Synchronization note (2026-07-01).** The specifications `07`, `08`, `10`, and `11` now exist and are
> authoritative; ADR-002 and ADR-003 are **Accepted** and applied; the Charter and Vision are restored.
> Rows below that mark `07/08/10` as "absent (assigned owner)" predate those documents and are retained
> for historical traceability — the assigned owners are now the actual authoring specifications. This
> matrix's stage set (S01–S19) and the branch table §4 remain accurate against the synchronized suite.

**Purpose:** establish normative traceability for the transformations that `docs/07_Label_Generation_Pipeline.md` must later specify  
**Scope:** construction from external source material through corpus freeze; no algorithms, thresholds, metrics, or serialization are defined here  
**Assessment date:** 2026-07-01

## 1. Evidence status

The following accepted inputs were available and read:

- `docs/01_Benchmark_Design.md`
- `docs/03_Problem_Definition.md`
- `docs/05_Formal_Definitions.md`
- `docs/06_Label_Specification.md`
- `docs/06a_Benchmark_Data_Model.md`
- `decisions/ADR-002-Construction-Provenance-Lifecycle.md`
- `decisions/ADR-003-Incomplete-Candidate-Subjects.md`

Two accepted inputs named in the request are not present anywhere in the workspace:

- `docs/00_Benchmark_Charter.md`
- `VISION.md`

Their exact clauses cannot be traced. Requirements attributed to them by available documents—most notably the no-judge boundary and change-control boundary—are mapped only through the available specifications that restate those requirements. This prevents a fully verified Charter/Vision row-level matrix; no content is inferred for the missing files.

The request declares all inputs accepted and frozen. That declaration is used as the governing status. File metadata is inconsistent with it: `01`, `03`, `05`, `06`, and `06a` say `Status: Draft`, while ADR-002 says `Status: Proposed`. ADR-003 alone says `Status: Accepted`.

## 2. Authority and invariant key

### 2.1 Specification authority

| Key | Authority |
|---|---|
| **BD** | `docs/01_Benchmark_Design.md`: architecture, lifecycle, construction/evaluation boundary, one-way flow, artifact ownership. |
| **PD** | `docs/03_Problem_Definition.md`: intervention-only construction target, prohibited judgment shortcuts, generator-specific target, evaluation information restriction. |
| **FD** | `docs/05_Formal_Definitions.md`: normative meanings and dependency order. |
| **LS** | `docs/06_Label_Specification.md`: P1–P6, Conditions A/B, S1–S3, label/reason projection, E1–E6, invariants and immutability. |
| **DM** | `docs/06a_Benchmark_Data_Model.md`: artifact forms, identity, lifecycle, mutability, traceability, and version relationships. |
| **ADR2** | ADR-002: observational/sealed phases of the single provenance artifact; production versus traceability graphs. |
| **ADR3** | ADR-003: incomplete pre-eligibility Output Tuples and Candidate Subjects; P1/E1 lifecycle. |
| **07** | Future Label Generation Pipeline: assigned operational owner for generation, intervention execution, operational determinations, and provenance. Not yet present. |
| **08** | Future Dataset Specification: assigned owner for normalization, tuple/release shape, corpus assembly, splits, and manifest. Not yet present. |
| **10** | Future Evaluation Protocol: assigned scoring owner. Outside construction and not yet present. |

### 2.2 Benchmark invariant abbreviations

| Key | Invariant set |
|---|---|
| **BD1–BD8** | Benchmark Design §13 invariants 1–8. |
| **PD-A1–A5** | Problem Definition §7 intentional assumptions. |
| **PD-R1–R7** | Problem Definition §8 refused assumptions. |
| **LS-I1–I9** | Label Specification §7 label invariants. |
| **DM-R1–R8** | Data Model §6 identity rules. |
| **DM-M1–M5** | Data Model §7 mutability rules. |
| **DM-T1–T6** | Data Model §8 traceability rules. |
| **DM-V1–V6** | Data Model §9 version relationships. |
| **ADR2-N1–N4** | ADR-002 §Decision normative provenance statements. |
| **ADR3-P** | ADR-003 §7 preserved invariants. |
| **ADR3-R** | ADR-003 §8 intentionally relaxed pre-eligibility completeness invariant. |

## 3. Planned-stage traceability matrix

“Implementation” describes the thesis repository and its historical implementation state, not benchmark
conformance. **Partial** means a related primitive exists but the governed transformation does not yet
produce the required benchmark artifact or decision. Any Charter/Vision citations that appear below are
historical traceability markers only; they do not alter Charter/Vision authority.

| ID | Planned stage | Input artifact(s) | Output artifact(s) | Governing specification and section | Applicable ADRs | Applicable benchmark invariants | Thesis implementation |
|---|---|---|---|---|---|---|---|
| **S01** | Normalize source material | External dataset record | Source Record | **Primary:** `08` (assigned, absent). **Constraints:** BD §§4–5, §7 step 1, §12; FD §9; DM §3.1. | None | BD5, BD7, BD8; DM-R4, R7; DM-M1; DM-T3, T5 | **Partial.** `datasets/vqa_dataset.py` loads processed VCR and stable IDs, but silently drops missing records and pads/truncates malformed choices. |
| **S02** | Execute generator and retain baseline output | Source Record + Generator | Output Tuple, possibly incomplete before P1 | **Primary:** `07` (assigned, absent). **Shape:** `08` (assigned, absent). **Constraints:** BD §4 item 2, §§7, 12; FD §§1, 5–6, 19; DM §3.2. | ADR3 §§3–5, 7–8 | BD1–BD4, BD7–BD8; DM-R1–R3, R6; DM-M2; ADR3-P, ADR3-R | **Partial.** Stage 1 answer and Stage 2 rationale generation exist, but do not reliably bind one exact chosen-answer/rationale tuple. Gold-answer conditioning and regenerated rationales remain. |
| **S03** | Bind Candidate Subject | Source Record + Output Tuple + complete composite Generator identity | Candidate Subject | **Primary:** `07` producer. **Artifact form:** DM §§1, 3.3, 6; FD §§1, 22; LS I3. | ADR3 §3, §5.2, §§6–8 | BD1, BD7, BD8; LS-I3; DM-R1–R3, R6–R7; DM-M1–M2; DM-T3; ADR3-P/R | **Missing.** No stable benchmark instance identity or serialized composite Stage-1/Stage-2 generator identity exists. |
| **S04** | Determine P1 completeness | Candidate Subject with possibly incomplete Output Tuple | Observational Interventional Provenance phase containing P1 result; on failure, E1 route outcome for S15 | **Meaning:** LS §3 P1 and §9 E1. **Artifact/lifecycle:** DM §§3.3, 3.7–3.8, 4, 8 T2. **Operational owner:** `07` absent. | ADR2 definitions/N3; ADR3 §§3–7 | BD7–BD8; LS-I3, I7–I8; DM-R1–R2; DM-M1–M2; DM-T1–T3; ADR2-N3; ADR3-P/R | **Partial.** Rationale-health and parsing checks detect some failures, but failures become empty strings, filters, or drops rather than P1 evidence and E1 outcomes. |
| **S05** | Determine P2 non-abstention and P3 scope | P1-qualified Candidate Subject + observational provenance | Accreted observational provenance containing P2/P3 results; E2/E3 route outcome for S15 on failure | **Meaning:** LS §3 P2–P3, §9 E2–E3. **Scope:** PD §7 A5. **Artifact:** DM §§3.7–3.8, 8 T2. **Operational owner:** `07` absent. | ADR2 N2–N3 | BD2, BD7–BD8; PD-A5; PD-R1–R4; LS-I2, I6–I8; DM-M1; DM-T1–T2 | **Partial.** `diagnose_rationale_health.py` detects empty/short/malformed outputs and the loader is VCR-specific, but no canonical abstention/scope gate or routed outcome exists. |
| **S06** | Observe answer-side interventions | Eligible-so-far Candidate Subject + live Generator | Answer-side Intervention Records; observational provenance accretion | **Primary:** `07` absent. **Meaning:** FD §§11–13, 20; BD §§4–5, 7–8, 12; PD §§4–5; DM §§3.4, 3.7. | ADR2 definitions, N1–N3 | BD1–BD4, BD7–BD8; PD-A1–A3; PD-R2–R4, R7; LS-I2–I3, I6, I8; DM-R5–R6; DM-M1; DM-T1, T6; ADR2-N1–N3 | **Partial.** `scripts/sufficiency_battery.py` and related scripts run global regimes and retain argmax choices, but not canonical Intervention Records, complete graded readings, or reliable control/input identity. |
| **S07** | Determine P4 and Condition A | Candidate Subject + observational provenance containing answer intervention records | Accreted observational provenance containing determinate A result; E4 route outcome for S15 if indeterminate | **Meaning:** FD §13; LS §3 P4, §4 Condition A, §§5–6, §9 E4. **Operational owner:** `07` absent. | ADR2 N1–N4 | BD1–BD2, BD7–BD8; PD-A1–A3; LS-I1–I3, I6–I8; DM-M1, M3; DM-T1–T2; ADR2-N1–N4 | **Partial.** Per-regime predictions exist, but no per-instance Condition A determination, raw margin retention, or E4/D1 distinction exists. |
| **S08** | Determine P5 evidence locatability | Candidate with A=true + observational provenance | Accreted observational provenance containing evidence-region identity/localization result; E5 route outcome for S15 on failure | **Meaning:** FD §14; LS §3 P5, §4 Condition B dependency, §9 E5; DM §§3.7, 8 T1. **Operational owner:** `07` absent. | ADR2 N1–N3 | BD1–BD2, BD7–BD8; PD-A1–A3; PD-R4; LS-I2–I3, I6–I8; DM-M1; DM-T1–T2; ADR2-N1–N3 | **Missing.** No saliency, attribution, answer-relevant localization, localization-quality result, or evidence identity exists. Raw VCR annotations do not establish causal evidence. |
| **S09** | Observe evidence-matched rationale interventions | Candidate with A=true and locatable evidence + live Generator | Rationale-side Intervention Records tied to the same evidence; observational provenance accretion | **Primary:** `07` absent. **Meaning:** FD §§11–12, 14, 17, 20; LS §4 Condition B; DM §§3.4, 3.7. | ADR2 definitions, N1–N3 | BD1–BD4, BD7–BD8; PD-A1–A3; PD-R1–R4, R7; LS-I2–I3, I6, I8; DM-R5–R6; DM-M1; DM-T1, T6 | **Missing.** Global real/grey rationale regeneration and BERTScore primitives exist, but no matched evidence intervention is implemented or bound to the exact baseline rationale/chosen answer. |
| **S10** | Determine P6 causal license | Candidate + applicable intervention/control observations | Accreted observational provenance containing control applicability/result; E6 route outcome for S15 on failure | **Meaning:** LS §3 P6 and §9 E6; FD §§11–12; DM §§3.4, 3.7. **Operational owner:** `07` absent. | ADR2 N1–N3 | BD2–BD4, BD7–BD8; PD-A1–A3; PD-R2, R7; LS-I2, I6–I8; DM-M1; DM-T1–T2, T6 | **Partial.** Horizontal flip and multiple destructive regimes exist, but no per-instance control applicability or causal-license decision exists. |
| **S11** | Determine Condition B | Candidate with A=true + locatable evidence + licensed observational provenance | Accreted provenance containing B result | **Meaning:** FD §§14, 17–18; LS §4 Condition B, §§5–6, §8.2. **Operational owner:** `07` absent. | ADR2 N1–N4 | BD1–BD2, BD7–BD8; PD-A1–A3; PD-R1–R4; LS-I1–I3, I6, I8; DM-M1, M3; DM-T1; ADR2-N1–N4 | **Missing.** Existing text drift measures generic response change, not whether stated visual content changes with the same evidence used by the answer. |
| **S12** | Determine Behavioural State | Candidate + observational provenance containing eligibility and A/B determinations | Behavioural State S1, S2, or S3 | **Meaning:** LS §5, §6 truth table, §8; FD §§17–18; **artifact:** DM §3.5. **Execution:** `07` absent. | ADR2 definitions, N1–N4 | BD1–BD2, BD7–BD8; LS-I1–I4, I6–I8; DM-M1, M3; DM-T1; ADR2-N1–N4 | **Missing.** No S1/S2/S3 implementation. Condition B is correctly required to be unassessed on S1, but no executable precedence exists. |
| **S13** | Project state to Label and reason code | Candidate + observational provenance + Behavioural State | Label: S1→`unfaithful`/D1, S2→`unfaithful`/D2, S3→`faithful`/no reason | **Meaning:** LS §§4–8, especially §5.3 and §6; FD §§18, 21; **artifact:** DM §3.6. **Execution:** `07` absent. | ADR2 N1–N4 | BD1–BD2, BD7–BD8; PD-R1–R4; LS-I1–I9; DM-M1, M3; DM-T1, T4; ADR2-N1–N4 | **Missing.** No benchmark label, D1/D2 projection, D1 precedence validation, or label invariant enforcement exists. |
| **S14** | Seal eligible provenance | Observational provenance + Behavioural State + Label/reason | Same Interventional Provenance artifact in sealed phase, with determination back-references | **Primary:** ADR2 definitions and N1–N4. **Supporting:** FD §20; LS I8; DM §§3.7, 7 M1/M3, 8 T1. **Producer:** `07` remains the sole producer. | ADR2 entire Decision | BD2, BD5, BD7–BD8; LS-I8–I9; DM-M1, M3–M4; DM-T1, T4, T6; ADR2-N1–N4 | **Missing.** Run manifests and fragmented probe files do not form or seal candidate-level provenance. |
| **S15** | Resolve and seal routed-aside candidate | Candidate + observational provenance + one E1–E6 outcome | Routed-Aside Record + same provenance artifact sealed with route back-reference | **Meaning:** LS §3, §9, I7–I8; **artifact/lifecycle:** DM §§1, 3.7–3.8, 4, 7 M5, 8 T2. **Execution:** `07` absent. | ADR2 N1–N4; ADR3 for E1, especially §§3–7 | BD5, BD7–BD8; LS-I2–I3, I6–I9; DM-R1–R2; DM-M1, M4–M5; DM-T1–T4; ADR2-N1–N4; ADR3-P/R | **Missing.** The thesis has no E-code record, route artifact, or sealed no-label provenance. E1 cases are currently lost or converted to empty output. |
| **S16** | Assemble labelled Corpus Entry and assign split | Source Record + complete Output Tuple + Candidate + sealed provenance + Behavioural State + Label | Corpus Entry | **Primary:** `08` absent. **Constraints:** BD §§4–7, 11–12; FD §§22, 24–25; DM §§3.9, 6–9. | ADR3 §3 boundary guarantee | BD3–BD8; LS-I3–I9; DM-R1–R8; DM-M2–M4; DM-T1, T3–T6; DM-V1–V6; ADR3-P/R | **Missing.** No benchmark Corpus Entry, benchmark split, or separated predictor/key/provenance view exists. |
| **S17** | Collect routed-aside set | Routed-Aside Records | Routed-Aside Set | **Primary:** `08` absent. **Meaning:** FD §23; LS §9; BD §§6–7; DM §§3.8, 8 T2/T5. | ADR3 for inclusion of E1 | BD5, BD7–BD8; LS-I7–I9; DM-M4–M5; DM-T2, T3, T5; ADR3-P | **Missing.** No routed-aside collection exists. |
| **S18** | Freeze corpus version and manifest | Corpus Entries + Routed-Aside Set + source/generator/specification references | Frozen Corpus + Corpus Manifest | **Primary:** `08` absent. **Constraints:** BD §§5–6, 8–13; FD §§25–26; LS §§10–11; DM §§3.10, 7–9. | ADR2 N3–N4; ADR3 boundary guarantee | BD2–BD8; LS-I8–I9; DM-R7–R8; DM-M1–M5; DM-T3–T6; DM-V1–V6; ADR2-N3–N4; ADR3-P | **Missing.** Thesis experiment manifests are run-level; no immutable corpus release, complete entry/routed-set manifest, or new-version-only correction mechanism exists. |
| **S19** | Expose evaluation views without crossing the information boundary | Frozen Corpus + Corpus Manifest | Predictor view containing only complete Output Tuples; hidden answer-key view for scoring; optional audit provenance not usable as predictor input | **Primary:** `08` release and `10` evaluation, both absent. **Constraints:** BD §§2–3, 9, 11–13; PD §§5–6, §8 R7; FD §§7–8, 19–21, 27; LS continuous-margins note and I2/I6; DM §§3.9–3.10, 8 T6. | ADR3 §§3–4, 7–8 | BD3–BD7; PD-R1–R7; LS-I2, I6, I8–I9; DM-R6; DM-T6; ADR3-P/R | **Missing.** No benchmark release/evaluation view exists. Existing files do not enforce that provenance, generator identity, and margins are unavailable to predictors. |

## 4. Branch and precedence traceability

| Decision branch | Governing authority | Required downstream stage |
|---|---|---|
| P1 fails | LS §3 P1, §9 E1; ADR3 §§3–7 | S15 with E1; no Intervention Records required; no state or label. |
| P2 fails | LS §3 P2, §9 E2 | S15 with E2; no state or label. |
| P3 fails | LS §3 P3, §9 E3 | S15 with E3; no state or label. |
| P4 indeterminate | LS §3 P4, §9 E4 | S15 with E4; MUST NOT become S1/D1. |
| A determinately false | LS §§4–6, §8.1 | S12 produces S1; S13 produces `unfaithful`/D1; B is not assessed. |
| A true, P5 fails | LS §3 P5, §9 E5 | S15 with E5; MUST NOT become D2. |
| A true, P6 fails | LS §3 P6, §9 E6 | S15 with E6; no state or label. |
| A true, B false | LS §§4–6, §8.2 | S12 produces S2; S13 produces `unfaithful`/D2. |
| A true, B true | LS §§4–6 | S12 produces S3; S13 produces `faithful` with no reason code. |

## 5. Transformation authority gaps

Every planned stage has a named conceptual authority or assigned future owner. However, the following transformations lack a currently available **operational governing specification**:

| Stage(s) | Assigned owner | Missing authority |
|---|---|---|
| S01 | `08` | Source normalization rules, malformed-source handling, and canonical source production. |
| S02–S15 | `07` | Generator execution contract; P1–P6 operational tests; intervention set; evidence localization; controls; Condition A/B operational determinations; provenance accretion/sealing execution; routing execution. |
| S16–S19 | `08` / `10` | Corpus entry construction, split assignment, routed-set handling, release/manifest format, predictor/key/audit view enforcement, and scoring access. |

The absence is expected before `07`/`08`/`10` are authored, but it means none of these transformations is fully governed at the operational level today. This matrix does not fill those gaps.

S12 and S13 are semantically complete in `06`; their missing authority is limited to execution and artifact production. S06–S11 lack both operational procedures and thresholds/methods by explicit deferral to `07`.

## 6. Specification consumption audit

| Accepted specification | Consumed by matrix stages | Result |
|---|---|---|
| `docs/00_Benchmark_Charter.md` | Exact consumption cannot be established; indirectly cited by LS I2 and change-control text in FD/LS/ADR3. | **Unverified: file absent.** |
| `VISION.md` | Exact consumption cannot be established; referenced by `01`/`03` metadata but no content is available. | **Unverified: file absent.** |
| `docs/01_Benchmark_Design.md` | S01–S03, S06, S09, S16–S19; cross-cutting BD invariants throughout. | Consumed. |
| `docs/03_Problem_Definition.md` | S05–S13, S19; A/R constraints prohibit judgment and evaluation-time intervention. | Consumed. |
| `docs/05_Formal_Definitions.md` | S01–S19 through artifact/concept meanings and dependency order. | Consumed. |
| `docs/06_Label_Specification.md` | S04–S15 and S18–S19. | Consumed. |
| `docs/06a_Benchmark_Data_Model.md` | S01–S19 through artifact form, identity, lifecycle, mutability, traceability, versioning. | Consumed. |
| ADR-002 | S04–S15 and S18; production/back-reference distinction. | Consumed under user-declared accepted status. |
| ADR-003 | S02–S04, S15–S19; incomplete-candidate/E1 branch and boundary guarantee. | Consumed. |

No available accepted specification is unused. Charter and Vision cannot be audited and therefore remain unconsumed as direct authorities.

## 7. Conflicting or stale authorities

### C1 — Acceptance metadata conflicts with the declared frozen set

- User-declared authority: all listed documents are accepted and frozen.
- File metadata: `01`, `03`, `05`, `06`, and `06a` are Draft; ADR-002 is Proposed; ADR-003 is Accepted.

This matrix follows the user-declared status, but an implementation cannot derive governance state solely from repository metadata.

### C2 — ADR-003 is accepted but its required amendments are absent

ADR-003 §5 requires amendments to FD §19, DM §§3.2–3.3/3.8/4/6/8, LS P1/E1, and the DAG. Those files do not mention ADR-003 or incomplete Output Tuples. Their current text still requires a complete Output Tuple before Candidate creation.

For this matrix, ADR-003 is the later accepted authority and overrides that pre-eligibility completeness requirement. The unamended base documents remain textually conflicting until synchronized.

### C3 — ADR-002 resolves the provenance cycle but is marked Proposed

The user declares ADR-002 accepted, so this matrix applies its N1–N4. Without it, DM §3.7/T1 and DM §§3.5–3.6 create an ambiguous apparent production cycle: provenance determines state/label while sealed provenance contains them. Repository metadata alone would not authorize the adopted interpretation.

### C4 — Frozen label document retains open policy questions

LS §14 still marks correctness eligibility, E6 publication, Condition B granularity, and composite-generator labeling as open. DM §10 also leaves baseline-output designation and evidence-region identity open. These are not conflicting rules yet, but “frozen” and “open” are inconsistent governance signals for stages S02, S07–S12, S15, and S19.

### C5 — Multi-spec artifact authority is dimension-partitioned

DM lists Candidate Subject under `06a`/`08` and Routed-Aside Record under `06a`/`06`/`08`. This does not conflict when interpreted as form (`06a`), semantics (`06`), and handling (`08`), but it is not literally one specification name per artifact. BD8 is satisfied only at the responsibility-dimension level.

## 8. Remaining implementation assumptions

These assumptions are not settled by existing thesis code and must not be silently treated as approved operational rules.

| ID | Assumption | Affected stages | Current evidence |
|---|---|---|---|
| **A01** | The thesis's separate Stage-1 answer checkpoint and Stage-2 rationale checkpoint form one valid composite generator subject. | S02–S03, S06–S13 | FD §1 permits composite generators, but LS Q4 remains open; code does not serialize a complete composite identity. |
| **A02** | One exact baseline Output Tuple can be designated and retained unchanged. | S02–S04, S09, S16 | Current probes regenerate rationales; Stage-2 artifacts and drift scripts assess different rationale spans. DM Q1 remains open. |
| **A03** | Gold answer conditioning is interchangeable with the generator's chosen answer. | S02, S09–S11 | Current rationale probes use the dataset gold answer. LS/DM require the exact chosen answer; the assumption is unsupported. |
| **A04** | Answer correctness is or is not an eligibility gate. | S05, S07, S12, S15 | LS Q1 is open. Current answer evaluation is correctness-centric. |
| **A05** | Per-instance Condition A can be determined from existing hard answer choices. | S06–S07 | Current battery discards raw scores/margins and has no E4 determination. |
| **A06** | Existing global perturbations reveal the answer's causal evidence. | S06–S09 | No evidence localization exists; global grey/noise/occlusion cannot establish P5 by themselves. |
| **A07** | A source annotation or rendered polygon is equivalent to answer-relevant evidence. | S08–S09 | VCR annotations exist, but no code relates them causally to the chosen answer. |
| **A08** | Generic rationale text drift establishes that stated visual content tracks the same evidence. | S09–S11 | BERTScore drift measures response difference, not directional evidence tracking. Condition B remains unimplemented. |
| **A09** | Horizontal flip and wrong-image regimes are valid controls for every instance. | S06, S10 | Spatial questions may legitimately change under flip; wrong-image selection may retain the same underlying VCR scene. |
| **A10** | Condition B is binary. | S11–S12 | LS Q3 remains open. |
| **A11** | P2 “bona fide attempt” and P3 scope can be operationalized from current health/loader checks. | S05 | Existing diagnostics are incomplete and filters are not routed outcomes. |
| **A12** | Failed generation can be retained uniformly as an incomplete Candidate Subject. | S02–S04, S15 | ADR3 requires it; current loaders/generators drop failures or convert them to empty strings. |
| **A13** | Observational and sealed provenance can remain one artifact with one producer while retaining an append-only lifecycle. | S04–S15 | ADR2 requires this; no candidate-level provenance store exists. |
| **A14** | Run-level manifests are sufficient label provenance. | S14–S18 | They are not: answer/rationale/intervention artifacts are fragmented and not bound per candidate. |
| **A15** | Released provenance can coexist with the corpus without becoming a predictor input. | S16–S19 | Required by BD/LS/DM, but no release-view enforcement exists. |
| **A16** | Source normalization, split assignment, corpus composition, and release manifest behavior are fixed. | S01, S16–S19 | They are assigned to absent `08`; thesis train/val splits are not benchmark splits. |

## 9. Traceability conclusion

The accepted documents imply a fully traceable conceptual sequence:

```text
source normalization
  -> generator output, possibly incomplete
  -> Candidate binding
  -> P1/P2/P3
  -> answer intervention and P4/Condition A
  -> P5 evidence localization when A holds
  -> matched rationale intervention and P6/Condition B
  -> S1/S2/S3
  -> Label projection OR E1–E6 routing
  -> provenance sealing
  -> Corpus Entry or Routed-Aside Set
  -> corpus freeze, manifest, and separated evaluation views
```

All planned transformations have conceptual ownership. Operational authority remains intentionally absent until `07` and `08` are authored. Direct Charter/Vision traceability is impossible from the current workspace, and repository status/amendment metadata must be reconciled before the specifications alone can serve as an unambiguous machine-readable authority set.
