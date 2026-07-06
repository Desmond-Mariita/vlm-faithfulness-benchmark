# Benchmark Specification v1.0 role assignments

**Work package:** V1-001  
**Recorded:** 2026-07-02  
**Status:** Active for program execution; semantic and release approvals remain explicit acts.

## Assigned roles

| Role | Account holder | Responsibility | Approval boundary |
|---|---|---|---|
| Benchmark Maintainer (BM) | Project Manager / repository owner (user) | Construct integrity, ADR ratification, specification acceptance, freeze and corpus-release approval | Sole approver for semantic/governance outcomes and final project decisions |
| Technical Lead (TL) | Codex | Technical coordination, sequencing, architecture conformance, implementation acceptance | Cannot self-ratify semantic decisions |
| Release Manager (RM) | Codex | Plan maintenance, evidence collection, milestone gates, release stop/go recommendations | Cannot waive normative or assurance requirements |
| Specification Owner (SO) | Codex, until BM delegates a document | Drafting and synchronization instructions; cross-document conformance review | BM approves normative changes |
| Engineering Lead (EL) | Claude | Repository changes, implementation, tests, CI, fixtures, and engineering documentation | TL accepts engineering work; BM approves any semantic impact |
| Verification Lead (VQ) | Codex for mechanical verification; Gemini for independent scientific review; DeepSeek for independent second-opinion audit support | QA evidence, traceability checks, freeze verification, independent milestone review | BM approves freeze/release evidence; Gemini and DeepSeek do not implement reviewed work |
| Publication and Licensing Owner (PO) | Codex, with BM approval | Packaging, licensing inventory, README, citation, release notes, and publication checks | BM approves license posture and public release |

## Role-separation rules

- The BM alone ratifies ADRs and semantic or governance outcomes.
- Claude may implement or edit repository artifacts but does not redesign or ratify benchmark semantics.
- Codex may draft, coordinate, and verify, but BM approval is required for normative acceptance and release.
- Gemini reviews milestone evidence independently and does not act as an implementation partner.
- DeepSeek reviews milestone evidence independently via `scripts/deepseek_review.sh` and does not act as an implementation partner.
- A semantic or freeze artifact may not be accepted solely by its drafter. When Codex is both SO and VQ,
  Gemini and/or DeepSeek supply independent review and the BM supplies approval.
- **Independent-reviewer eligibility (Charter §5 decisions and public release).** For any ADR that
  touches a Charter §5 item, and for public-release evidence review, the separate reviewer the BM
  appoints under `docs/conventions/decision-records.md` §7 must not have drafted or implemented the
  affected artifact and must hold no approval role for it. The reviewer's identity is recorded by
  name in the decision index entry or the release evidence record for that item.
- The user remains the communication bridge between models and the final decision maker.

## Capacity assumptions

- Codex: active technical-program, specification-coordination, and release-management capacity.
- Claude: implementation capacity assigned only through dependency-ready work packages.
- Gemini: milestone review capacity, requested after evidence is assembled.
- DeepSeek: independent second-opinion review capacity, typically requested after evidence is assembled or as a parallel cross-check; outputs are advisory only.
- BM/user: decision and approval capacity; no implementation workload is assumed.

These assumptions support planning estimates only. They do not authorize work whose dependencies are not
accepted.

## Current delegations

- V1-001: Codex (RM), accepted by Codex as TL after producing the required local evidence.
- V1-002: Codex (SO) owns the specification of the task; Claude is the repository-change executor; BM
  approves the resulting process conventions.
- V1-003: Claude (EL) investigates and executes only after the BM chooses recovery/migration versus new
  repository history where that choice is necessary; Codex accepts as RM.
- V1-004 onward: assigned in the issue import manifest and remains gated by its listed dependencies.

## Approval note

The user instruction to proceed authorizes program activation under the team structure stated in the
technical-leadership handover. It does not pre-approve any ADR, normative amendment, Git-history choice,
license posture, freeze, or release.
