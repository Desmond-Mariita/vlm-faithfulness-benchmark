# M9 GLM merge completion

**Recorded:** 2026-08-17

**Reviewer:** Desmond Mariita

**Status:** PASS

The manifest-driven GLM merge completed with exactly 18,194 unique canonical
positions across the reviewed seven-segment layout. The production validator
confirmed generator identity, baseline binding, legacy-sidecar disposition,
external and in-row provenance, exact segment coverage, canonical order,
routed-aside evidence, and the absence of gaps or duplicates.

The merged observation ledger has SHA-256
`861f33b4e4b5cec34ef82c414232c45caf3b717e1fefc73e6003c4f6c4884ede`.
The merge plan has SHA-256
`2c07e8703eb0e0d551986a0ecd5dc67b2c31d3cdf0fea7bdf8e84bdc7262877a`.
Exact artifact locations, sizes, hashes, segment counts, and the B2 backup
binding are recorded in `m9_glm_merge_completion.json`.

## Storage boundary

Raw ledgers are intentionally not committed to Git. The complete input and
output bundle is stored in the `manyee` Backblaze B2 bucket under:

`runs/glm-merge-inputs/2c07e8703eb0e0d551986a0ecd5dc67b2c31d3cdf0fea7bdf8e84bdc7262877a/workspace/`

The bundle contains 19 objects totaling 99,900,315 bytes. Every listed input
and output passed download-based SHA-256 verification. The earlier Vast
snapshot's two 50-row tail checkpoints are retained only as historical backup
state and are not merge inputs; the merge used the completed 1,423-row tail
ledgers bound to their immutable run manifests.

## Claim boundary and handoff

This evidence closes the raw GLM observation-lane merge. It does not claim that
a labelled candidate ledger or released Corpus Entry view exists. The S16
readiness audit found that deterministic offline S12–S15 adjudication and
provenance sealing must run first. After that stage passes, the controlled work
continues with S16 Corpus Entry assembly and split assignment, S17 Routed-Aside
Set construction, S18 corpus freeze and manifest, and S19 separated
predictor-visible, hidden, and audit views. See
`m9_s16_readiness_audit.{md,json}` for the corrected handoff.
