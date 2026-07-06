# Release notes — Benchmark Specification v1.0

**Release:** Public Specification v1.0 (`benchmark-spec-v1.0`)
**Date:** 2026-07-06
**Milestone:** M5 (release plan §3)

## What this release is

The first public release of the VLM Faithfulness Benchmark **specification**: the complete
frozen normative set that defines the benchmark — what it measures, how labels are defined and
produced, what the corpus must contain, and how systems are evaluated.

The benchmark targets a gap in VQA evaluation: a vision-language model's chain-of-thought
rationale can be fluent and visually specific without being *faithful* — without the answer or
the rationale actually depending on the visual evidence. The specification defines the
requirements for a future static, pre-labelled corpus and the protocol for predicting the outcome
of the underlying causal test from model output alone; no corpus is released here.

## Contents

- **Normative set (19 files):** enumerated with SHA-256 hashes in
  [`normative_file_manifest.tsv`](normative_file_manifest.tsv) — Charter, Vision, and the
  specification series `01`–`11`, plus accepted ADRs 002–008.
- **Governing conventions:** decision records and versioning
  ([`docs/conventions/`](../../../conventions/)).
- **Supporting material (non-normative):** the release plan, design and synchronization reports,
  cited external review records, and this release evidence.
- **Packaging:** root `README.md` (navigation and read order), `LICENSE` (CC BY 4.0, text),
  `LICENSE-CODE` (Apache-2.0, future code), `CONTRIBUTING.md`, `CITATION.cff`, `CHANGELOG.md`.

## What this release is not

- **No corpus.** Public specification release never implies corpus readiness (release plan §7).
  The corpus is a separate immutable release train (`benchmark-corpus-v…`) with its own manifest,
  compatibility statement, and licensing.
- **No implementation.** Pipeline code, baselines, and validation studies are downstream work
  packages (V1-038 onward). Ground truth is defined by specifications, not by implementation.
- **No claim over third-party data.** Source-dataset rights remain with their owners; nothing
  here grants or claims corpus rights.

## Integrity

- Internal freeze: tag `benchmark-spec-v1.0-freeze`, approved in
  [`freeze_approval.md`](freeze_approval.md).
- Every normative file in this public tree is byte-identical to the freeze manifest; the
  verification record is [`public_release_checklist.md`](public_release_checklist.md).

## Known open items (tracked, not blocking this release)

Work-package (`V1-…`) and milestone (`M…`) identifiers below are defined in the
[release plan](../../Benchmark_v1.0_Release_Plan.md) §§3, 5.

- Corpus construction, validation study VAL-01, baselines, and human evaluation are scheduled in
  the release plan (M6–M12).
- The Reproducibility/Implementation Profile (RIP) v1 will pin all operational choices before any
  label is produced (V1-024 contract, V1-039).
