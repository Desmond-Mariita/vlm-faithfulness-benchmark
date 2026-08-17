# M9 GLM S12–S15 completion

**Status:** PASS — production adjudication and sealing complete

Desmond Mariita approved the reviewed contract, and commit `8db235a` changed only its status from
`review-pending` to `accepted`. GitHub Actions run `32004931110` passed on that commit. The accepted
contract SHA-256 is
`bf089675ed47574e99a1a0bc56b9a71f9ae75934cf0982464dbbf1db16a3c17a`.

The production run resolved all 18,194 GLM candidates exactly once: 13,594 labelled and 4,600 routed
aside. Counts are E1=10, E2=6, E5=1,079, E6=3,505, S1=12,321, S2=719, and S3=554. The sealed ledger
SHA-256 is `c8efd4bbe1e280bd876fcfed85bb01bb80150c7a44a6c536b3ee5dc32dddfe23`.

The complete three-file bundle exists locally under
`runs/release-evidence/m9-glm-adjudicated/<accepted-contract-sha256>` and in B2 under
`manyee/runs/glm-adjudicated/<accepted-contract-sha256>`. The B2 destination was empty before copy;
copying used immutable/no-overwrite mode. All three remote files were streamed back and matched their
local SHA-256 values exactly.

Machine-readable hashes, byte counts, resolution counts, commits, and backup verification are recorded
in `m9_glm_s12_s15_completion.json`. The prior S16 readiness blocker is closed. The next controlled
stage is S16 Corpus Entry assembly and split assignment.
