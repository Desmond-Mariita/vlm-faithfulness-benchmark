# VLM Faithfulness Benchmark — Specification v1.0

*A benchmark specification for classifying the causal faithfulness of vision-language-model
rationales in visual question answering.*

**Status: Specification v1.0 (frozen and released). No corpus has been released yet.**

> This README is a navigational aid only. It is **not normative** and creates no technical
> authority. If anything here appears to conflict with a specification document, the
> specification governs.

## Purpose

Vision-language models emit chain-of-thought rationales before answering, and readers treat that
text as the reason for the decision. But a fluent, visually specific rationale need not be
*faithful*: it can be a story from language priors rather than from the visual evidence the answer
depends on. A model that is right for the wrong reason scores like one that is genuinely grounded.

This benchmark specifies the requirements for a static, pre-labelled corpus — none is released
yet — and an evaluation protocol for predicting the outcome of a causal faithfulness test —
whether a model's answer and rationale actually depend on the image — from the static output
alone, with the generating model out of reach. See
[`VISION.md`](VISION.md) for why, and the [Benchmark Charter](docs/00_Benchmark_Charter.md) for
what the benchmark permanently is and is not.

## What is released here

**Specification v1.0** — the frozen normative document set that defines the benchmark: its
formal definitions, label semantics, data model, label-generation pipeline, dataset requirements,
baseline-system contract, evaluation protocol, and assurance obligations.

**Not released yet:** the corpus itself, pipeline code, and baseline results. Public
specification release deliberately precedes and never implies corpus readiness (release plan §7).
The corpus will be a separate, versioned, immutable release (`benchmark-corpus-v1.0`) once
construction and validation complete.

## Authority and read order

The exact normative set is enumerated, with per-file SHA-256 hashes, in
[`normative_file_manifest.tsv`](docs/design/release_evidence/spec-v1.0/normative_file_manifest.tsv).
A document is normative if and only if it appears there. Everything else in this repository —
including this README, the release plan, design/synchronization reports, and review records — is
supporting material.

Read in this order:

| Order | Document | Role |
|---|---|---|
| 1 | [`docs/00_Benchmark_Charter.md`](docs/00_Benchmark_Charter.md) | Identity and boundaries. Read first. |
| 2 | [`VISION.md`](VISION.md) | Why the benchmark exists; success and stopping conditions. |
| 3 | [`docs/01_Benchmark_Design.md`](docs/01_Benchmark_Design.md) | Technical umbrella; ties the specification series together. |
| 4 | [`docs/03_Problem_Definition.md`](docs/03_Problem_Definition.md) | The prediction problem being posed. |
| 5 | [`docs/05_Formal_Definitions.md`](docs/05_Formal_Definitions.md) | Formal objects and terms. Definitions live here. |
| 6 | [`docs/06_Label_Specification.md`](docs/06_Label_Specification.md) | Label semantics, versioning of label meaning. |
| 7 | [`docs/06a_Benchmark_Data_Model.md`](docs/06a_Benchmark_Data_Model.md) | Entities, identity, and state model. |
| 8 | [`docs/07_Label_Generation_Pipeline.md`](docs/07_Label_Generation_Pipeline.md) | How labels are produced (stages S01–S19). |
| 9 | [`docs/08_Dataset_Specification.md`](docs/08_Dataset_Specification.md) | Corpus content, splits, access classes, manifests. |
| 10 | [`docs/09_Baseline_Systems.md`](docs/09_Baseline_Systems.md) | Baseline-system contract. |
| 11 | [`docs/10_Evaluation_Protocol.md`](docs/10_Evaluation_Protocol.md) | Scoring and reporting rules. |
| 12 | [`docs/11_Benchmark_Assurance.md`](docs/11_Benchmark_Assurance.md) | Verification and release obligations. |

Accepted Architecture Decision Records live in [`decisions/`](decisions/) and are immutable;
authority precedence between ADRs and specifications is fixed by
[ADR-007](decisions/ADR-007-Authority-Precedence-and-ADR-Specification-Ordering.md).

**Deliberate numbering gaps.** Identifiers are never reused or renumbered. Gaps in the
specification series (e.g. no `02`, no `04`) and in the ADR series (the series as released begins
at ADR-002) are deliberate: the missing numbers belonged to documents or decisions that were
superseded or retained internally, and renumbering would break recorded cross-references.

## Governance

Changes are governed by the conventions in [`docs/conventions/`](docs/conventions/):
[decision records](docs/conventions/decision-records.md) (how decisions are made and superseded)
and [versioning](docs/conventions/versioning.md) (the specification/code and corpus version
trains). Anything that changes what an existing artifact, term, or label *means* is a MAJOR
change and requires an ADR. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

The program that produced this release is recorded in the (non-normative)
[Benchmark v1.0 Release Plan](docs/design/Benchmark_v1.0_Release_Plan.md); release evidence,
including the freeze approval and hash manifests, is under
[`docs/design/release_evidence/spec-v1.0/`](docs/design/release_evidence/spec-v1.0/).

## Implementation entry point

Implementation has not started in this repository. The contract every implementation must
satisfy is the specification set above; the implementation program (architecture, reproducibility
profile, acceptance matrix, fixtures) is laid out in the
[release plan](docs/design/Benchmark_v1.0_Release_Plan.md) §5, whose backlog defines the
work-package identifiers (`V1-…`) used throughout this repository — the implementation items are
V1-038–V1-043. Ground truth is defined by specifications, not by implementation.

## Release identity

- Frozen at internal tag `benchmark-spec-v1.0-freeze` (see
  [`freeze_approval.md`](docs/design/release_evidence/spec-v1.0/freeze_approval.md)).
- Published as annotated tag `benchmark-spec-v1.0` on this repository's packaging commit.
- Normative file hashes at the public tag are byte-identical to the freeze manifest.
- Lineage: see [`CHANGELOG.md`](CHANGELOG.md).

## License

- **Specification text and documentation** (everything in this repository unless stated
  otherwise): [Creative Commons Attribution 4.0 International](LICENSE) (CC BY 4.0).
- **Source code** (none released yet; applies to future code in this repository):
  [Apache License 2.0](LICENSE-CODE).
- **Corpus and third-party data:** *no rights are granted or claimed here.* The benchmark
  builds on third-party datasets (e.g. VQA datasets with their own terms); corpus licensing will
  be stated by the corpus release itself, per the versioning convention and Dataset
  Specification.

## Citation

If you use or build on this specification, please cite it (see [`CITATION.cff`](CITATION.cff)):

> Mariita, D. (2026). *VLM Faithfulness Benchmark — Specification v1.0.*
> https://github.com/Desmond-Mariita/vlm-faithfulness-benchmark
