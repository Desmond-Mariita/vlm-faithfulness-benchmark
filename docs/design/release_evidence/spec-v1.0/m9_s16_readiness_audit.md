# M9 S16 readiness audit

**Recorded:** 2026-08-17

**Reviewer:** Desmond Mariita

**Status:** BLOCKED BEFORE S16 — offline adjudication required

The GLM observation lane is complete: the validated merge contains 18,194
unique instances and is fully backed up. No additional GLM/GPU generation is
required. It is not yet a labelled corpus input, however. The merged rows are
the S04–S11 observation surface produced by `run_pilot_observation`, whose
contract explicitly defers calibrated labeling and sealing.

S16 cannot lawfully consume this ledger yet. Dataset Specification N4.1 and
N4.5 require S16 to consume an already assigned Label, Behavioural State, and
sealed Interventional Provenance and carry them through unchanged. None of
those resolution fields is present in any of the 18,194 merged rows.

## Reproducible inventory

The observation and canonical S02 ledgers each contain 18,194 unique instance
keys, and their normalized instance-key sets are identical. The existing
routes are 10 E1 records and 6 E2 records; 18,178 rows pass P1–P3. At the final
registered `k=3`, those passing rows resolve to 13,502 Condition-A-false and
4,676 Condition-A-true candidates, with no indeterminate Condition A reading.

The recorded S04–S11 measurements are sufficient for branch-appropriate
offline adjudication. In particular, the fresh calibration fold reproduces a
flat-saliency floor of `0.625` from 100/100 max-drop readings. Applying the
specified strict comparison to the Condition-A-true rows places 1,079 below
the floor, 324 exactly at the floor, and 3,273 above it. The below-floor rows
must re-adjudicate to E5; equality remains locatable.

Of the observation rows, 14,141 carry their baseline digest in-row and the
remaining 4,053 are bound by the accepted legacy verification sidecar. Run
provenance is in-row for 2,846 rows and externally accepted for 15,348. The
merge validator has already verified these two binding modes without mutating
the source ledgers.

## Calibration authority

Production adjudication must consume these final, pinned values:

- Condition B instrument: `jaccard-content-v1`, with stopwords SHA-256
  `cc8737d5b5eb3580026695487b43b0e38a786193a93fe5600e27c253cdec7860`.
- `theta_B = 0.7558573853989813`, from the VIABLE confirmatory gate result
  SHA-256 `4fc67b57d3c11be00eb7ae73323c793c61f6883bc0918eb6654afbe341668faa`.
- Condition A threshold `k=3`, fixed by `prereg-v3` SHA-256
  `e94d82403309a6948dfe7ff5119fb25f9c17b77ccf018b13db9e410f508b7879`.
- Flat-saliency floor `0.625`, reproduced from fresh confirm observations
  SHA-256 `91a2e4b5d25238604219c5ed1fcb0245f2e375bfdf1fe9cd7e54310200374225`.
  The original 500-row pilot independently produces the same value.

`data/runs/k_calibration_result.json` records the superseded `k=2`
human-agreement result. `prereg-v3` preserves it as descriptive evidence only;
it must never be selected by the production labeling path.

## Implementation boundary

The existing pure projection and sealing primitives are usable, but no
production orchestrator currently turns this mass observation ledger into
S14/S15 sealed resolutions. Two older modules also cannot be used unchanged:
`gating/condition_b.py` still computes BERTScore drift, while the final
registered instrument is Jaccard content drift, and `gating/calibration.py`
still implements the superseded prereg-v1 human-agreement selector.

The next controlled step is therefore a fail-closed offline S12–S15 stage. It
must first materialize an immutable calibration lock, then apply route
precedence, Conditions A/B, P6, state/label projection, and exactly-once
provenance sealing. Its output must cover all 18,194 candidates as labelled XOR
routed and pass deterministic rerun and reconstructability checks.

Only after that report passes may work proceed to S16, S17, S18, and S19.
Machine-readable counts, hashes, implementation gaps, and required outputs are
recorded in `m9_s16_readiness_audit.json`.
