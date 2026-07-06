# Label Generation Pipeline Implementation Inventory

> **Historical snapshot (dated 2026-07-01, pre-specification).** This inventory compares the thesis
> repository against `docs/06_Label_Specification.md` *before* `07`/`08`/`09`/`10`/`11` were authored. It
> is retained as a **dated pre-specification snapshot** of implementation readiness; it is **not** a
> normative specification and does not define benchmark behavior. For current authority use the
> synchronized specifications and the `Specification_Synchronization_Report.md`.

**Assessment date:** 2026-07-01  
**Benchmark specification assessed:** `docs/06_Label_Specification.md`  
**Implementation assessed:** `~/Documents/thesis`

## 1. Scope and evidence boundary

This document inventories implementation that already exists in the thesis repository against the approved label semantics. It does not define an operational label rule, select thresholds, or redesign the benchmark.

The assessment read the available frozen documents named in the request:

- `docs/01_Benchmark_Design.md`
- `docs/03_Problem_Definition.md`
- `docs/design/Formal_Definition_Dependency_Graph.md`
- `docs/04_Legacy_Terminology_Mapping.md`
- `docs/05_Formal_Definitions.md`
- `docs/06_Label_Specification.md`

Two named inputs are not present in the benchmark workspace: `VISION.md` and `docs/00_Benchmark_Charter.md`. Their requirements therefore could not be independently checked. References to the Charter in `docs/06_Label_Specification.md` were treated as requirements only to the extent that they are restated in the available documents.

The thesis worktree was inspected without modification. It already contained unrelated local changes, including an untracked `scripts/drift_battery.py`; that script is inventoried as a prototype rather than as repository-controlled implementation.

### Status definitions

| Status | Meaning in this inventory |
|---|---|
| **Existing** | Executable implementation exists and directly supplies the named capability, although integration or schema refactoring may still be required. |
| **Partial** | Related executable behavior exists, but it does not establish the approved semantic requirement. |
| **Missing** | No implementation was found. |

## 2. Implementation readiness summary

The thesis repository supplies a usable experimental substrate, but it does not currently implement label generation conforming to `docs/06_Label_Specification.md`.

| Area | Readiness | Finding |
|---|---|---|
| VCR source loading | Existing | Four-choice VCR records, images, captions, gold answers, and gold rationales are loaded for four thesis arms. |
| Answer generation | Existing | A Qwen2.5-VL backbone plus a learned four-way classifier produces answer predictions. |
| Rationale generation | Existing | A separately trained Stage-2 checkpoint generates rationales conditioned on gold or Stage-1-predicted answers. |
| Global answer interventions | Existing | Real, grey, wrong-image, random occlusion, noise, and horizontal-flip regimes are executable. |
| Global rationale interventions | Existing | Real-versus-grey rationale regeneration and BERTScore drift are executable; an untracked six-regime extension also exists. |
| Condition A | Partial | Per-regime answer choices are recorded, but there is no per-instance determinate image-dependence decision, control gate, or indeterminate outcome. |
| Evidence localization | Missing | No answer-relevant localization, saliency/attribution, targeted region selection, or localization-quality check exists. |
| Condition B | Missing | Existing drift measures response change under global perturbations; it does not establish change with the same evidence used by the answer. |
| Eligibility and routed-aside logic | Missing | Load and generation failures are dropped, normalized, or filtered rather than retained with E1–E6 outcomes. |
| Behavioural states and label projection | Missing | No S1/S2/S3, `faithful`/`unfaithful`, D1/D2, or precedence implementation exists. |
| Per-label interventional provenance | Missing | Run manifests and fragmented probe outputs exist, but there is no provenance object sufficient to reconstruct a label. |
| Corpus-version immutability | Missing | No released corpus manifest, frozen label artifact, or new-version-only correction mechanism exists. |

Consequently, none of the three normative labelled cases N1–N3 or routed cases N4–N6 is executable end to end. The existing repository can generate candidate subjects and some raw intervention observations; it cannot yet produce a conformant label artifact.

## 3. Existing thesis execution model

### 3.1 Data and experimental arms

`datasets/vqa_dataset.py` implements VCR loading for `train` and `val` and for four arms:

- `plain`: plain image, no caption
- `point`: polygon/annotation-rendered image, no caption
- `plain_desc`: plain image plus caption
- `point_desc`: polygon/annotation-rendered image plus caption

The canonical data and mode paths are in `configs/base.yaml`; arm overrides are in `configs/plain.yaml`, `configs/point.yaml`, `configs/plain_desc.yaml`, and `configs/point_desc.yaml`. The configured modes range from a 212-record debug train set through the full VCR-derived data. Operational benchmark support is VCR-only. AOKVQA material exists under data-preparation notebooks, but no benchmark-ready AOKVQA loader or label probe path was found.

The loader returns a useful source record skeleton: `id` (question ID), image, question, four choices, gold `label`, caption, `image_id`, `orig_image_id`, image paths, source metadata, and `rationale_gold`. It does not return the structured VCR boxes/segmentations available in raw sidecars. Point images contain annotations baked into pixels, which are not equivalent to structured evidence regions.

### 3.2 Generator composition

The thesis generator is a composite system:

1. `scripts/train_answer_qwen.py` and `models/mc_classifier.py` implement Stage 1. A Qwen2.5-VL backbone is pooled and passed to a learned four-class answer head.
2. `scripts/train_rationale_qwen.py` implements Stage 2. A separate checkpoint generates a rationale conditioned on a supplied answer index.

Canonical checkpoint mappings for all four arms are centralized in `utils/checkpoints.py` as `CANONICAL_STAGE1` and `CANONICAL_STAGE2_GOLD`. Stage 2 is warm-started from Stage 1, but answer and rationale behavior still come from distinct checkpointed components. A conformant subject identity therefore has to bind both components and their configuration; no current per-instance output does this.

Stage-2 output contains `image_id`, `orig_image_id`, question, choices, `answer_idx`, `answer_idx_gold`, `answer_idx_pred`, caption, prompt, gold rationale, generated reasoning, generated final rationale, and BLEU/statistics. `rationale_gen` is explicitly an alias for only the parsed `<final>` span, not the complete generated response.

### 3.3 Current intervention and evaluation flow

The implemented answer-side flow is:

```text
VCR record -> Stage-1 prompt -> image regime -> four-way prediction
           -> per-regime prediction/correctness CSV -> aggregate accuracy gaps
```

The implemented rationale-side flow is:

```text
VCR record -> prompt containing a fixed answer -> real/perturbed image
           -> regenerated rationale pair -> BERTScore similarity/drift
```

These flows are separate. They do not share a stable benchmark instance identifier, evidence region, intervention record, eligibility decision, or state-projection step.

## 4. Existing capability inventory

| Capability | Location | Status and maturity | Dependencies | Confidence |
|---|---|---|---|---|
| VCR data loading | `datasets/vqa_dataset.py` | **Existing; mature for thesis experiments.** Supports four arms, captions, train/val, source metadata, and kept-ID manifests. It silently drops some records and pads/truncates non-four-choice records, which is non-conformant for routed-aside accounting. | PIL, PyTorch; processed VCR JSON and image trees | High |
| Answer model training/inference | `scripts/train_answer_qwen.py`, `models/mc_classifier.py`, `cli/run_stage1.py` | **Existing; mature for the four thesis arms.** Produces a four-choice answer from the learned classifier head. It is not a generic interface for other generators. | Qwen2.5-VL-3B, Transformers, PEFT/LoRA, PyTorch, Stage-1 checkpoints | High |
| Rationale model training/inference | `scripts/train_rationale_qwen.py`, `cli/run_stage2.py` | **Existing; mature for the thesis generator.** Supports gold- and predicted-answer conditioning and greedy generation when `cot_samples == 1`. Parsed output distinguishes reasoning and final spans. | Qwen2.5-VL-3B, Transformers, PEFT/LoRA, Stage-2 checkpoints | High |
| Canonical checkpoint selection | `utils/checkpoints.py` | **Existing; mature.** Central mappings reduce accidental checkpoint mixing. Identity is run-level, not bound into each generated subject/probe record. | Local checkpoint artifacts | High |
| Grey-image answer ablation | `scripts/sufficiency_blindfold.py`, `scripts/run_full_val_sufficiency.py` | **Existing; mature for aggregate thesis findings.** Computes real-versus-grey accuracy and per-example predictions. It does not decide per-instance Condition A. | Stage-1 model and VCR loader | High |
| Wrong-image answer ablation | `scripts/mismatched_image_sufficiency.py`, `scripts/sufficiency_battery.py` | **Existing; experimental.** Battery selection uses a prior-batch record with a different `image_id`, falling back to grey. Different rendered `image_id` values do not prove different underlying `orig_image_id` scenes. | Stage-1 model; batch order | High |
| Six-regime answer perturbation | `scripts/sufficiency_battery.py` | **Existing; experimental.** Runs `real`, `grey`, `wrong`, `occlude`, `noise`, and `hflip`, recording per-item choices/correctness and aggregate gaps. Random occlusion covers approximately half the whole image; it is not evidence-targeted. | Stage-1 classifier, NumPy/PIL, VCR loader, CUDA | High |
| Real-versus-grey rationale drift | `scripts/rationale_drift.py` | **Existing; mature as a thesis diagnostic.** Regenerates rationales and computes BERTScore drift. Empty generations are filtered out of scoring. It uses the gold answer in the prompt. | Stage-2 model, BERTScore `roberta-large`, CUDA | High |
| Six-regime rationale drift prototype | untracked `scripts/drift_battery.py` | **Partial; prototype.** Extends rationale regeneration to the answer battery regimes and can join answer rows by `image_id`. It uses a hard-coded drift threshold and gold answer, and no checked-in result establishes validity. | Stage-2 model, BERTScore, answer battery CSVs | High |
| Drift threshold calibration | `scripts/drift_threshold_calibration.py`, `scripts/run_drift_threshold_calibration.sh` | **Existing for same-image stochastic calibration, not Condition B.** Calibrates ordinary output variation, not evidence-targeted tracking. | Stage-2 model and BERTScore | High |
| Rationale text metrics | `scripts/make_rationale_metrics.py`, `scripts/make_rationale_metrics_cot.py`, `scripts/rescore_reparsed.py` | **Existing; mature.** BLEU, BERTScore, BLEURT, length, and CoT statistics support downstream analysis. They are not permitted label determinants under I2/I6. Empty rationales are silently excluded by `_filter_valid_rationales`. | BERTScore, BLEURT, NLTK/metric packages | High |
| Rationale output health diagnostics | `scripts/diagnose_rationale_health.py`, `utils/cot_parser.py`, `scripts/reparse_rationales.py` | **Partial for P1/P2.** Detects empty/short/non-ASCII/missing-tag outputs and supports reparsing. It reports or repairs analysis artifacts; it does not classify refusal/abstention comprehensively or emit routed-aside records. | Generated rationale JSON | High |
| Cross-modal consistency | `scripts/cross_modal_consistency.py` | **Existing as downstream evaluation only.** Uses a text-only model judge. It must remain outside label construction under I2. | Qwen text model, generated rationales | High |
| Label consistency | `scripts/label_consistency.py` | **Existing as a thesis metric only.** This is legacy answer/rationale answer-label agreement, not the benchmark faithfulness label. | Generated rationale outputs | High |
| Caption leakage and robustness diagnostics | `scripts/caption_leakage_drift.py`, `scripts/run_caption_leakage.sh`, robustness sections in Stage 2 | **Existing as ancillary analysis.** No direct approved label semantics are implemented. | Thesis checkpoints and data | Medium |
| Statistical reporting | `scripts/compute_bootstrap_ci.py`, `scripts/compute_significance_tests.py`, `scripts/panel_stats_followups.py` | **Existing for experiment-level analysis.** Not a label-generation component. | Existing result artifacts | High |
| Run configuration and manifests | `cli/_common.py`, `utils/yaml_config.py` | **Existing; mature at run level.** Writes resolved configuration, seed, config hash, Git SHA, device, precision, library versions, backbone, revision, and checkpoint path. It does not attach the reconstructive provenance to each label. | Git and runtime environment | High |
| Timings and resumable JSONL | `utils/perf.py` | **Existing; reusable infrastructure.** `StageTimer`, `load_done_keys`, and `ResumeJSONL` support durable incremental evaluation. No label pipeline currently uses them as a conformant provenance store. | Standard library | High |
| Saliency/attribution | No implementation found | **Missing.** No Grad×Input, integrated gradients, Grad-CAM, answer-likelihood saliency, pointing game, or IoU implementation exists. Thesis documentation explicitly avoids claiming these methods. | — | High |
| Evidence localization | No implementation found | **Missing.** Raw VCR boxes/segmentations and rendered point images exist, but there is no code identifying which region caused a chosen answer. | — | High |
| Targeted counterfactual editing | No implementation found | **Missing.** Existing occlusion/noise/grey/wrong-image transformations operate globally or randomly. | — | High |
| Behavioural states and label projection | No implementation found | **Missing.** Repository search found no implementation of S1/S2/S3, D1/D2, benchmark `faithful`/`unfaithful`, or D1 precedence. | — | High |
| Routed-aside handling | No implementation found | **Missing.** Failures are skipped, normalized, replaced, or filtered rather than represented as E1–E6 outcomes. | — | High |
| Corpus-versioned provenance | No implementation found | **Missing.** No label artifact, corpus manifest, immutable release, or correction-as-new-version facility exists. | — | High |

## 5. Coverage of label preconditions

| Requirement | Status | Existing evidence | Gap and required refactoring before faithful implementation |
|---|---|---|---|
| **P1 — Well-formed subject** | Partial | `train_rationale_qwen.py` can emit answer indices and a generated rationale alongside source fields. | There is no single canonical output tuple bound to the complete composite generator identity. Probe scripts commonly regenerate a new rationale instead of consuming the tuple's rationale. Question ID is dropped from Stage-2 and intervention outputs. Subject records must retain stable source identity, both component checkpoints/configurations, and the exact baseline answer/rationale later assessed. |
| **P2 — Non-abstention** | Partial | `diagnose_rationale_health.py` detects several malformed/empty cases; generation code parses `<reasoning>` and `<final>`. | Current metric paths filter empty strings, and generation failures become `""`. No unified refusal, abstention, or degeneracy outcome is stored. Health checks must become explicit eligibility evidence rather than silent analysis filters. The semantic boundary of “bona fide attempt” remains operationally unspecified outside `06`. |
| **P3 — In scope** | Partial | `VQADataset` is explicitly four-choice visual QA and Stage 2 supplies rationales. | Invalid choice counts are padded or truncated to four rather than routed aside. Only VCR is operational. Scope validation and its outcome are not persisted per source record. |
| **P4 — Determinable image-dependence** | Partial | `sufficiency_battery.py` records answer choices across six image regimes. | The code returns observations and aggregate gaps only. It has no per-instance determination, uncertainty/margin, threshold, or explicit indeterminate result. It cannot distinguish E4 from D1. Raw answer scores/logits are discarded in favor of `argmax`, limiting determinacy analysis. |
| **P5 — Locatable evidence** | Missing | Raw VCR annotations and rendered point images are data assets. | No implementation relates answer behavior to a causal evidence region. Structured boxes are not exposed by `VQADataset`; baked-in polygons are presentation, not attribution. Evidence localization and localization failure accounting are entirely absent. |
| **P6 — Licensed causal reading** | Partial | `hflip` is included as a nominal control, and multiple destructive regimes reduce dependence on one ablation. | The code does not evaluate whether a control is semantically valid for the individual question or record any control pass/fail state. Spatial questions can legitimately change under horizontal flip. Wrong-image selection may reuse the same underlying scene. Control failures are not routed to E6. |

## 6. Coverage of Conditions A and B

### 6.1 Condition A — answer image-dependence

**Status: Partial.**

The strongest reusable implementation is `scripts/sufficiency_battery.py`. For every evaluated record it stores `pred_real`, `pred_grey`, `pred_wrong`, `pred_occlude`, `pred_noise`, and `pred_hflip`, plus correctness under each regime. `scripts/sufficiency_blindfold.py` and `scripts/mismatched_image_sufficiency.py` provide narrower versions of the same answer-side intervention concept.

The implementation does not establish Condition A as approved:

- Results are summarized as corpus-level accuracy gaps; no code emits a per-instance Boolean or determinate/indeterminate reading.
- Only the winning answer index is retained. Scores, margins, and repeated observations needed to support a determinacy claim are absent.
- `correct_*` is defined against the dataset gold answer. Condition A concerns whether the generator's **chosen answer** depends on the image, not whether the perturbed answer is correct.
- No implemented rule distinguishes an invariant chosen answer (potential S1) from an inconclusive probe (E4).
- Global grey/noise/random occlusion can change the input distribution without identifying the relevant visual content.
- The `wrong` regime selects by rendered `image_id`, not reliably by underlying scene identity (`orig_image_id`).
- The `hflip` control is applied without question-type or semantic validity checks.
- The implementation is specific to the thesis `MCClassifier`; it does not expose an answer-scoring interface for generators without that head.

Required refactoring is therefore not limited to wrapping `run_arm`: its per-item outputs must retain stable subject identity, raw answer evidence, intervention identity, and control/determinacy outcomes. The numeric decision rule itself is not present in the approved documents assessed here and is outside this inventory.

### 6.2 Condition B — rationale tracks the same evidence

**Status: Missing.**

`scripts/rationale_drift.py` is reusable for rationale regeneration and text-distance computation, but it tests global real-versus-grey sensitivity. The untracked `scripts/drift_battery.py` extends the same pattern to six whole-image regimes. Neither implementation identifies the answer's evidence, changes that evidence specifically, or verifies that the rationale's stated visual content changes accordingly.

Additional incompatibilities are material:

- Both drift scripts condition rationale generation on `sample["label"]`, the dataset gold answer. They do not bind the probe to the actual Stage-1 chosen answer.
- They regenerate a baseline rationale during the probe. The regenerated text is not guaranteed to be the exact rationale in the candidate output tuple.
- `rationale_drift.py` compares full decoded generations, while standard Stage-2 artifacts define `rationale_gen` as only the parsed `<final>` span. The assessed rationale object is inconsistent.
- BERTScore magnitude measures text change, not directionally correct change in stated visual content. No current code establishes the approved “changes accordingly” relation.
- Failed or empty generations are filtered from metric computation rather than routed aside.
- There is no link from an answer intervention to the corresponding rationale intervention. A join by `image_id` in the prototype is not a unique (`generator`, `source record`) binding.

Rationale generation and BERTScore are existing lower-level capabilities. Evidence targeting, subject binding, response-scope consistency, and the Condition B determination are missing implementations rather than completed label logic.

## 7. Behavioural state generation and label projection

| Semantic requirement | Status | Inventory finding |
|---|---|---|
| Generate **S1** when A determinately fails | Missing | No per-instance A verdict or E4 distinction exists. |
| Generate **S2** when A holds and B fails | Missing | No Condition B implementation or joined A/B record exists. |
| Generate **S3** when A and B hold | Missing | No Condition B implementation or state artifact exists. |
| Do not assess B when A fails | Missing | Current answer and rationale probes are independent batch experiments; neither gates the other. |
| Project S1 to `unfaithful`/D1 | Missing | No D1 implementation. |
| Project S2 to `unfaithful`/D2 | Missing | No D2 implementation. The prototype's informal “dissociation” output is not this normative state projection. |
| Project S3 to `faithful`/no reason | Missing | No benchmark label implementation. |
| Enforce exactly one primary label | Missing | No label schema or invariant validation. |
| Enforce exactly one reason only for `unfaithful` | Missing | No reason-code schema or validation. |
| Enforce D1 precedence | Missing | No ordered evaluation/projection code. |

Legacy thesis uses of `label` refer to the VCR gold answer index, and “label consistency” refers to answer agreement. They cannot be reused as the benchmark label field without namespace separation. This collision is already identified in `docs/04_Legacy_Terminology_Mapping.md`; it remains present throughout the thesis code.

## 8. Label-invariant coverage

| Invariant | Status | Evidence and incompatibility |
|---|---|---|
| **I1 — Determinism of meaning** | Missing | No label implementation exists. Current experimental terms such as sufficiency, drift, and consistency are measurements, not the S1–S3 verdict. |
| **I2 — Interventional provenance only** | Partial | Answer and rationale probe signals are intervention-derived. Existing CMC, BLEU, BERTScore-to-gold, BLEURT, label-consistency, and rationale-health analyses are separate evaluation paths and currently do not override a label. However, no boundary is enforced because there is no label path. BERTScore used between counterfactual outputs is an interventional response statistic, but current code does not demonstrate that it assesses stated visual-content tracking rather than generic text change. |
| **I3 — Subject binding** | Missing | Outputs lack a stable composite generator identifier and often lack `question_id`. The answer and rationale probes write separate files and can join only on weak keys such as `image_id` and question text. |
| **I4 — Exactly one primary value** | Missing | No benchmark label field or validation. |
| **I5 — Reason-code coupling** | Missing | No D1/D2 fields or validation. |
| **I6 — Independence from correctness and appearance** | Partial | Thesis probe outputs preserve predictions and correctness separately, and plausibility metrics are separate scripts. However, current sufficiency analyses are accuracy-centric, and the drift prompt is conditioned on the gold answer. No code prevents correctness, grounding, or text-quality signals from entering a future verdict. The specification's Q1 still leaves correctness-as-eligibility open. |
| **I7 — Eligibility exclusivity** | Missing | There is no eligibility object. Silent drops, padding/truncation, empty-output filtering, and exception-to-empty-string handling can remove or alter failed cases without a routed outcome. |
| **I8 — Self-justification** | Missing | `cli/_common.py` provides strong run-level manifests, and probe CSV/JSON files record some observations, but no label carries sufficient per-instance intervention provenance to reconstruct A, B, controls, eligibility, state, and projection. |
| **I9 — Immutability** | Missing | Research outputs can be regenerated/reparsed/rescored in place. There is no corpus version, frozen label/provenance artifact, or manifest-enforced correction policy. |

## 9. Routed-aside coverage

| Route | Status | Current behavior | Required refactoring |
|---|---|---|---|
| **E1 — Malformed or absent output** | Partial detection; missing routing | Dataset records may be dropped; generation exceptions become empty strings; malformed generated spans can be diagnosed or reparsed. | Preserve the failed source/subject record and the failure outcome instead of dropping or repairing it invisibly in the label input. |
| **E2 — Abstention/refusal/degenerate rationale** | Partial detection; missing routing | Empty and very short rationales can be detected. Empty text is filtered from metrics. Refusal semantics are not comprehensively classified. | Convert the approved eligibility test result into a retained no-label outcome with evidence; do not silently filter it. |
| **E3 — Out of scope** | Partial validation; missing routing | The loader assumes VCR and normalizes the choices list to length four. | Retain invalid-scope records as route outcomes where they enter the labeling input; do not make malformed choice structure look valid. |
| **E4 — Indeterminate image-dependence** | Missing | The battery always emits argmax predictions if inference succeeds. No determination confidence or indeterminate state exists. | Preserve information needed by the future approved P4 test and represent its indeterminate outcome separately from S1/D1. |
| **E5 — Unlocatable evidence** | Missing | There is no localization attempt or localization quality result. | Add the missing localization outcome to the inventory of label-construction data; inability to localize must survive as no label rather than becoming D2. |
| **E6 — Unlicensed causal reading** | Missing | Controls are perturbation columns, not per-instance causal-license decisions. | Persist control applicability/results and retain failed controls as no-label outcomes, not D1. |

There is no routed-aside set artifact in the thesis repository. The kept-ID manifest from `VQADataset` records aggregate drop counts and the retained IDs, but it is fail-open and does not preserve one record per rejected subject with an E-code or full reason evidence.

## 10. Interventional provenance inventory

### 10.1 Provenance already available

At run level, `cli/_common.py` records:

- resolved configuration and config hash;
- run ID, arm, mode, suffix, and seed;
- Git SHA;
- device and precision;
- Python/platform and key package versions;
- backbone model and revision;
- Stage-1 checkpoint;
- timestamp and resume status.

`utils/checkpoints.py` supplies canonical checkpoint lineage, and `utils/perf.py` supplies append-and-fsync JSONL plus record-level resume primitives. `VQADataset` can emit a kept-ID manifest. These are directly reusable infrastructure capabilities.

Probe-specific artifacts currently contain only fragments:

- answer battery CSV: `image_id`, question, gold answer, per-regime argmax prediction and correctness;
- answer battery summary: arm, sample count, Stage-1 checkpoint, accuracies, and aggregate gaps;
- rationale drift JSON: local index, `image_id`, question, choices, gold answer, caption, two generated rationales, and drift score;
- Stage-2 generation JSON: source text fields, answer indices, generated rationale spans, prompt, and rationale metrics.

### 10.2 Provenance required by I8 but absent

No current artifact binds all of the following for one verdict:

- stable benchmark instance ID and original `question_id`;
- exact source record identity and dataset/split version;
- composite generator identity: both answer and rationale checkpoints, configurations, code revision, and model revision;
- exact baseline chosen answer and exact baseline rationale from the output tuple;
- each intervention's identity, parameters, random seed, and resulting input identity/hash;
- answer scores/margins as well as argmax choices under each intervention;
- evidence-region identity and evidence-localization outcome;
- rationale response under the matched evidence intervention and the exact response span assessed;
- control applicability and results;
- P1–P6 results and any E1–E6 route;
- Condition A and B determinations, including indeterminate outcomes;
- S1/S2/S3 state, primary label, reason code, and projection/version identifiers;
- artifact/corpus version and integrity information supporting immutability.

The current run manifest cannot substitute for this record because answer and rationale probes are separate runs and their per-item outputs do not reference the manifest or each other reliably.

The label specification permits continuous margins to ship as provenance but prohibits their use as predictor inputs. The thesis computes aggregate sufficiency gaps and per-pair drift values, but it has no release-layer separation enforcing that information boundary.

## 11. Assumptions baked into thesis code

1. **Gold answer is the default rationale subject.** `rationale_drift.py` and the drift-battery prototype hold the dataset gold answer fixed. Stage 2 also defaults to `answer_source: gold`. This assumes the gold answer and generator's chosen answer are interchangeable; P1, Condition A, and Condition B do not permit that substitution.
2. **The baseline rationale may be regenerated.** Most faithfulness diagnostics call the generator again rather than consume the exact emitted tuple. This assumes deterministic regeneration reproduces the subject. It is not encoded or verified, and runtime/library variation or span parsing can change the text.
3. **A composite generator can be treated as one subject without explicit identity.** Stage 1 and Stage 2 are distinct checkpointed components. The repository tracks them at different places but does not serialize a composite identity per instance. This is the unresolved Q4 case in `06`.
4. **Answer correctness is the primary answer-side lens.** Sufficiency outputs and summaries emphasize `correct_*` and accuracy gaps. The approved Condition A concerns chosen-answer dependence. Correctness may affect eligibility only if Q1 is resolved that way; it cannot determine the verdict under I6.
5. **Global destruction is an adequate intervention proxy.** Grey, noise, random whole-image occlusion, and wrong-image replacement are treated as answer/rationale sensitivity probes. None identifies or specifically alters the answer's evidence as required for Condition B.
6. **Argmax changes are sufficient evidence.** Answer logits and margins are discarded. This assumes a hard-choice change alone provides all information required for P4 determinacy.
7. **Horizontal flip is a universal preserving control.** It is applied to all records without checking spatial language or question type. This assumption is false for some left/right or directional questions and can create an E6 case.
8. **Different `image_id` means a genuinely wrong scene.** The wrong-image selection compares rendered IDs. VCR records can share an underlying `orig_image_id`, so the code does not guarantee an independent scene.
9. **`image_id` is an adequate join key.** The rationale battery prototype maps answer rows by `image_id`; question-specific rendered IDs and repeated scene records make this weaker than a stable generator/source-pair ID.
10. **Invalid data may be normalized or discarded.** Missing files/IDs may be silently dropped; invalid choice lengths are padded/truncated; empty rationale pairs are filtered. The benchmark requires explicit no-label outcomes.
11. **Generated final span is the rationale.** Stage-2 artifacts alias `rationale_gen` to `<final>`, while `rationale_drift.py` can assess a fuller decoded response. The repository has no single canonical rationale scope for label construction.
12. **Point overlays provide usable grounding information.** Polygon/person markers are rendered into pixels during preprocessing, but the loader exposes no structured relation between those annotations and the chosen answer. They cannot establish P5.
13. **Run-level reproducibility is enough.** Manifests are strong for experiments but do not reconstruct an individual verdict or enforce released-artifact immutability.
14. **Probe failure may be omitted from denominators.** Empty outputs are filtered before BERTScore and some data errors are skipped. This changes the evaluated population without a routed-aside ledger.

## 12. Required refactoring inventory

The following are implementation prerequisites exposed by the comparison. They do not select methods or change the approved semantics.

| Refactoring prerequisite | Why it is required | Existing code affected |
|---|---|---|
| Separate legacy answer-label names from benchmark label names | `label` currently means VCR gold answer; reuse would create incompatible records and logic. | `datasets/vqa_dataset.py`, all training/evaluation scripts consuming `labels` |
| Preserve canonical source and subject identity through every artifact | I3 cannot be met with missing question IDs and joins on image/question text. | Stage-1 outputs, `train_rationale_qwen.py`, all sufficiency/drift scripts |
| Bind probes to the exact emitted answer–rationale tuple | P1 and Condition B concern the genuine output tuple, not an independently regenerated or gold-conditioned substitute. | `rationale_drift.py`, untracked `drift_battery.py`, Stage-2 artifact handling |
| Represent failures and exclusions as retained outcomes | P1–P6/I7/E1–E6 prohibit silent drop, normalization, and filtering. | `VQADataset`, rationale generation, rationale metric filters, probe exception handling |
| Retain per-intervention answer evidence rather than only aggregate accuracy/argmax | P4, Condition A, E4, and I8 require a reconstructible per-instance determination. | `sufficiency_battery.py`, blindfold/mismatch scripts |
| Correct wrong-image source identity handling | A control/intervention cannot be reconstructed or trusted when the supposedly different image may share the source scene. | `sufficiency_battery.py`, untracked `drift_battery.py` |
| Make control applicability and result explicit | P6/E6 cannot be inferred from the existence of an `hflip` prediction column. | Answer and rationale perturbation scripts |
| Expose structured source annotations separately from rendered pixels | Existing VCR annotations are otherwise unavailable to any P5 implementation or provenance record. This does not by itself implement evidence localization. | `datasets/vqa_dataset.py`, data-preparation outputs |
| Standardize the assessed rationale span | Condition B cannot be reproducible while one path assesses full decoded text and another defines only `<final>` as `rationale_gen`. | `train_rationale_qwen.py`, `rationale_drift.py`, rationale metrics |
| Bind run manifests to per-instance intervention artifacts | I8 requires each verdict to reference its generator/configuration/interventions, not merely rely on directory convention. | `cli/_common.py`, `utils/perf.py`, all probe writers |
| Add invariant checks for states, projection, reasons, and no-label outcomes | I4, I5, I7 and D1 precedence currently have no executable enforcement. | Missing label/state layer; no current implementation to refactor |
| Add corpus-version and integrity handling | I9 cannot be satisfied by mutable research result directories. | Missing release artifact layer; no current implementation to refactor |

Several requirements are wholly missing and therefore cannot be satisfied by refactoring alone: evidence localization (P5), matched evidence intervention and tracking determination (Condition B), behavioural-state generation, label/reason projection, routed-aside storage, and immutable corpus-versioned provenance.

## 13. Unresolved specification dependencies affecting implementation

Although the request describes the listed specifications as approved and frozen, `docs/06_Label_Specification.md` identifies itself as Draft and leaves the following semantic questions open:

- Q1: whether answer correctness is an eligibility condition;
- Q2: whether some E6/control failures form a distinct published outcome;
- Q3: whether Condition B is binary or admits partial tracking;
- Q4: whether the thesis's composite Stage-1/Stage-2 subject is valid as one generator;
- Q5: reason-code scoring, deferred to the scoring specification.

Q1–Q4 directly affect label-pipeline behavior or schema. The thesis code currently makes implicit choices for Q1 and Q4—gold/correct-answer conditioning and a two-checkpoint composite—without implementing them as explicit approved policy. These cannot be treated as settled implementation behavior solely because code exists.

The operational owner repeatedly referenced by `06` as `07` is also absent from the assessed workspace. Therefore no approved thresholds, determinacy test, evidence-localization test, control rule, Condition B statistic, or provenance schema was available to compare with the thesis code. Existing thresholds and experimental constants—especially the prototype drift threshold and global perturbation parameters—are thesis/prototype settings, not approved benchmark semantics.

## 14. Final readiness assessment

The thesis repository is **ready as a source of candidate outputs, checkpoints, VCR loading, global perturbation execution, metric computation, and run metadata**. Those components are concrete and mostly mature within the four thesis arms.

It is **not ready to generate approved benchmark labels**. The blocking implementation gaps are semantic, not merely integration gaps:

- Condition A has observations but no conformant per-instance determination or E4/E6 handling.
- Condition B's same-evidence requirement has no implementation.
- P5 evidence localization has no implementation.
- Eligibility and routed-aside outcomes are not represented.
- S1/S2/S3 and the D1-precedence projection are absent.
- Per-label reconstructive provenance and corpus-version immutability are absent.
- Existing rationale probes are not consistently bound to the generator's chosen answer or exact emitted rationale.

No current thesis artifact can be interpreted as a conformant `faithful` or `unfaithful` label under `docs/06_Label_Specification.md`. The reusable implementation boundary ends at raw subject generation, global intervention observations, metrics, and run-level experiment metadata.
