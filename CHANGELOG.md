# Changelog

All notable releases of this repository are recorded here. Specification versions follow the
[versioning convention](docs/conventions/versioning.md); released specifications are immutable —
corrections produce new versions, never in-place edits.

## Specification v1.0 — 2026-07-06

**Tag:** `benchmark-spec-v1.0` (annotated, on the packaging commit of this repository).

First public release of the benchmark specification: the complete normative set enumerated in
[`normative_file_manifest.tsv`](docs/design/release_evidence/spec-v1.0/normative_file_manifest.tsv)
— Charter, Vision, Benchmark Design, Problem Definition, Formal Definitions, Label Specification,
Benchmark Data Model, Label Generation Pipeline, Dataset Specification, Baseline Systems,
Evaluation Protocol, Benchmark Assurance, and accepted ADRs 002–008 — together with the governing
conventions, supporting design documents, and release evidence.

### Lineage

- Authored and frozen in a private working repository under the Benchmark v1.0 release program
  ([release plan](docs/design/Benchmark_v1.0_Release_Plan.md), work packages V1-001–V1-032; the
  plan's §5 backlog defines these `V1-…` identifiers).
- **Internal freeze (M4):** commit `75e0320`, annotated tag `benchmark-spec-v1.0-freeze`,
  approved 2026-07-06
  ([freeze approval](docs/design/release_evidence/spec-v1.0/freeze_approval.md)). The freeze
  commit identifier refers to the private archive repository; its content is carried here by
  hash: every normative file in this public repository is byte-identical to the freeze manifest
  ([`freeze_manifest.sha256`](docs/design/release_evidence/spec-v1.0/freeze_manifest.sha256) →
  `normative_file_manifest.tsv`).
- **Public packaging (M5):** this repository is the curated public tree (work packages
  V1-033–V1-037): licensing, README, CONTRIBUTING, CITATION, release notes, and public release
  checklist added; private working material (drafts, internal reviews not cited by the normative
  set, agent configuration) is retained only in the private archive.
- Verification that public normative hashes equal the freeze manifest is recorded in the
  [public release checklist](docs/design/release_evidence/spec-v1.0/public_release_checklist.md).

No corpus is released. The corpus train (`benchmark-corpus-v1.0`) will be recorded here when it
ships.
