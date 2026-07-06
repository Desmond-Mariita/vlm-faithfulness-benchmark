# Benchmark Specification v1.0 open-question report

**Created:** 2026-07-03  
**Purpose:** Consolidated registry of open questions, deferred policy items, and blocker status for the
Specification v1.0 release program.

## 1. Report scope

This report classifies the currently recorded open questions across the normative specification set and
the governance conventions. It does not decide new benchmark semantics.

The release plan uses this report as the evidence that no v1 blocker remains before later M3/M4 work.

## 2. Summary disposition

- No open item in this report requires a new benchmark semantic to proceed with M2 closure.
- Size-floor and v1 human-protocol topics are future issues unless separately approved.
- RFC-2119 requirement-keyword usage is already the project-wide convention across the normative
  specifications.
- Version-metadata closure remains coordinated with V1-026/V1-030.
- Q5 is resolved by Evaluation Protocol §17 and is not a blocker.

## 3. Current open items by authority

### Label Specification

- Q2 — Void vs routed-aside: open, policy-owned by `08`.
- Q5 — Reason-code scoring: resolved by Evaluation Protocol §17 as the secondary diagnostic S-2;
  not a blocker.

### Benchmark Data Model

- Q1 — Candidate identity for regenerated outputs: open, owned by `07`/`08`.
- Q2 — Publication of construction-internal artifacts: open, release-policy owned by `08`.

### Evaluation Protocol

- Q-E1 — Minimum-n threshold: per-release governance decision.
- Q-E2 — κ interpretation: per-release governance decision.
- Q-E3 — Leaderboard existence: per-release governance decision.
- Q-E4 — Human-performance scope: owned by Dataset Specification ethics/consent policy.
- Q-E5 — Cross-version meta-analysis: future governance decision.
- Q-E6 — Serialization: implementation-owned.

### Benchmark Assurance

- Cadence, severity independence, external-audit requirement, sunset policy, and meta-governance
  remain governance items.
- Standing drift items must still be closed before public release.

### Versioning Convention

- Complete per-document version-metadata scheme: deferred to V1-026/V1-030.
- Post-v1.0 corpus increment grammar: deferred to V1-026 or another BM-classified version-metadata
  decision.

## 4. Non-blocking classification

The items above remain open or deferred, but they do not constitute a v1 blocker for M2 closure.
The only explicitly future-gated topics called out by the release plan for V1-026 are:

- fixed size floors; and
- a v1 human protocol.

Those topics remain future issues unless separately approved.

## 5. RFC-2119 classification note

The normative documents already state their requirement-keyword convention consistently. The project
therefore treats MUST, MUST NOT, SHOULD, and MAY in the RFC-2119 sense across the normative
specification set.

## 6. Conclusion

No v1 blocker remains in the recorded open-question inventory. The residual items are either:

- already resolved by existing authority;
- explicitly deferred to later work packages; or
- governance/implementation items that do not alter v1 benchmark semantics.
