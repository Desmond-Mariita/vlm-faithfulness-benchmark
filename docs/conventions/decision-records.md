---
Title: Decision Records Convention
Status: Accepted
Last-reviewed: 2026-07-02
Related:
  - docs/00_Benchmark_Charter.md
  - docs/05_Formal_Definitions.md
  - docs/06_Label_Specification.md
  - docs/11_Benchmark_Assurance.md
  - docs/conventions/versioning.md
  - docs/design/Benchmark_v1.0_Release_Plan.md
  - decisions/ADR-002-Construction-Provenance-Lifecycle.md
  - decisions/ADR-003-Incomplete-Candidate-Subjects.md
---

# Decision Records Convention

*This convention defines the **process** for proposing, recording, approving, superseding, and tracing
Architecture/Benchmark Decision Records (ADRs). It is the file referenced by
[Formal Definitions §36](../05_Formal_Definitions.md) as the change-control route for normative
entries. It was authored under work package V1-002 of the active release plan; BM approval under that
work package activates it for repository process, recorded by updating `Status:` (that bookkeeping
update, like `Last-reviewed`, is not a substantive convention change under §9). It defines no benchmark
semantics: no label meaning, no eligibility rule, no state space, no threshold, and no artifact
ontology. Where this convention and a Charter clause, an accepted ADR, or an owning specification
appear to disagree, this convention yields; it claims no authority over benchmark meaning. The
project-wide ordering of technical authorities is an open governance question owned by work package
V1-007 of the active release plan and is **not** decided here.*

## 1. Scope

- **Governs:** the lifecycle, format, numbering, approval, immutability, and traceability of decision
  records in `decisions/`.
- **Does not govern:** the content or outcome of any decision. In particular, this convention takes no
  position on correctness eligibility (V1-004), composite-generator subject identity (V1-005), P6
  completeness (V1-006), authority precedence (V1-007), D1 terminology (V1-008), intervention
  methodology, numerical thresholds, or corpus size.

## 2. What a decision record is

An ADR is the immutable record of one governed decision: the problem, the options considered, the
choice, its consequences, and the amendments it authorizes. ADRs live in `decisions/` at the
repository root, a register separate from the specifications (`docs/`) and from exploratory material
(`design/`, notes).

Accepted ADRs are part of the exact normative file set (release plan V1-030 lists "accepted ADRs" in
the normative manifest). How accepted ADR text and specification text relate while an ADR's authorized
amendments are pending — and the ordering of technical authorities generally — is answered by
**ADR-007 / V1-007**: within the ADR's exact decision and amendment scope, the accepted decision
governs until faithful application lands; outside that scope, each owning specification retains its
authority; after faithful application, the owning specification is the integrated implementation-facing
authority. This convention records that process rule but does not itself decide benchmark meaning.

## 3. Numbering and the origin of the existing series

### 3.1 Rule

- Numbers are **sequential integers, zero-padded to three digits** (`ADR-002`, `ADR-003`, …),
  matching the recorded series in `decisions/`.
- A number is assigned when the ADR file is created and is **never reused and never renumbered**,
  regardless of the ADR's eventual status (Rejected and Superseded ADRs keep their numbers).
- Numbers **004–006** are reserved by the active release plan for the decision packages V1-004
  (existing ADR-004 slot), V1-005 (existing ADR-005 slot), and V1-006 (existing ADR-006 slot). The
  next free number after the reserved block is **007**.
- **Only numbers 004–006 are reserved.** A decision package with no reserved number (e.g.
  V1-007/V1-008, which the plan permits to conclude with an explicit BM classification record
  instead of an ADR) simply consumes no number. A reserved slot lapses — is retired unassigned like
  001 (§3.2), never reallocated — only through a release-plan revision that removes its package's
  ADR outcome. The decision index (§10) records every such disposition, so every numbering gap is
  explicable from the record.

### 3.2 Why the recorded series starts at ADR-002 (explanatory, not a renumbering)

The Repository Scaffolding Proposal (§2, §11.6, §14) proposed a **four-digit** series
(`ADR-0001`, …) and pre-assigned its first three numbers: `ADR-0001` (repository name), `ADR-0002`
(adoption of the scaffolding proposal), `ADR-0003` (adoption of the Benchmark Charter). None of those
three foundational records was ever authored as a file, and the proposal's four-digit format was never
used in a recorded ADR.

The recorded series in `decisions/` instead begins with two accepted, three-digit records whose
subjects differ from the proposal's planned assignments:

- [ADR-002 — Construction Provenance Lifecycle](../../decisions/ADR-002-Construction-Provenance-Lifecycle.md)
  (front matter: `Status: Accepted`, `Accepted: 2026-07-01`);
- [ADR-003 — Incomplete Candidate Subjects](../../decisions/ADR-003-Incomplete-Candidate-Subjects.md)
  (front matter: `Status: Accepted`, `Date: 2026-07-01`; it carries no separate `Accepted:` field —
  see the grandfathering rule in §5.3).

This convention records the actual practice as canonical:

- `ADR-002` and `ADR-003` **as filed** are the authoritative holders of those numbers. No file is
  renamed or renumbered.
- Number **001 is permanently retired unassigned**. It was informally associated with the
  repository-name decision that was proposed but never recorded; under never-reuse it is not
  back-filled. If the repository-name decision is ever formally recorded, it receives the next free
  number.
- The proposal's planned subjects for 0002 (scaffolding adoption) and 0003 (Charter adoption) were
  likewise never authored; those numbers were subsequently consumed by ADR-002 and ADR-003 as filed,
  which stand. If either adoption decision is ever formally recorded, it too receives the next free
  number.
- The gap at 001 and any future gaps are deliberate and documented; a reader encountering a missing
  number should consult this section and the decision index (§10) rather than infer a lost record.

## 4. File naming and directory contents

`decisions/ADR-NNN-Hyphenated-Title.md`, matching the two recorded files (e.g.
`ADR-003-Incomplete-Candidate-Subjects.md`). The status of an ADR lives in its front matter, never in
the filename. `decisions/` contains only ADR files. The scaffolding proposal's draft template
(`decisions/0000-template.md`) was never instantiated and is **not** adopted; §5 of this convention is
the authoritative statement of ADR form. Adding a template file later is a substantive convention
change and enters the change-classification gate (§9, §12).

## 5. Required form

The form requirements in §§5.1–5.2 apply to every ADR **created after this convention takes effect**.
They are consolidated from the two recorded ADRs and the scaffolding proposal's draft template, made
uniform where the recorded ADRs differ from each other; §5.3 states how the recorded ADRs stand.

### 5.1 Front matter

```yaml
---
Status: Proposed            # Proposed | Accepted | Rejected | Superseded | Deprecated
Date: YYYY-MM-DD            # date the record was created
Accepted: YYYY-MM-DD        # date of BM ratification (added on acceptance)
Supersedes: —               # ADR-NNN it replaces, or —
Superseded-by: —            # ADR-NNN that replaced it, or — (added on supersession)
Deprecated-by: —            # ADR-NNN that deprecated it, or — (added on deprecation)
Charter-clause: —           # the specific Charter clause touched or gated by this decision, or —
Related:                    # affected specifications, design analyses, reviews, issues
  - docs/…
---
```

`Charter-clause` is mandatory content, not decoration: a decision that touches a Charter §5 item MUST
name the specific clause there (see §9 and §11).

### 5.2 Required sections

Every new ADR contains, in order (heading numbering and exact titles may vary, as they do between the
recorded ADRs):

1. **Context** — the problem, the forces, and links to whatever raised it (review finding, DAG
   finding, registry entry, issue).
2. **Decision drivers / Alternatives considered** — the options genuinely weighed, each with its
   trade-offs. A single-option ADR must say why no alternative existed.
3. **Decision** — the choice, stated plainly, and why it won.
4. **Consequences** — positive, negative/accepted costs, and follow-ups.
5. **Required amendments** — the exact list of documents and clauses the decision authorizes to
   change (may be empty for decisions with no document impact). This list is the input to the
   amendment work items and to the ADR-application check (see §10).
6. **Links** — traceability to related ADRs, issues, evidence, and reviews.

An ADR SHOULD record its own versioning classification explicitly, as ADR-003 §8 does against Label
Specification §11; the classification is verified against the owning specifications and
[versioning.md](versioning.md), which govern.

### 5.3 Recorded ADRs (grandfathering)

ADR-002 and ADR-003 are **conformant as filed**. Their form is not retrofitted — §8 forbids editing
them — and their acceptance is evidenced by their front matter and the decision index (§10). Their
amendment obligations are those stated **in their own text** and scheduled by the release plan: for
ADR-003, its §5 "Required amendments"; for ADR-002, its normative statements and follow-ups as
reconciled by work package V1-022. The ADR-application check (§10) verifies each recorded ADR against
its own stated obligations, and each future ADR against its §5.2 Required-amendments section.

## 6. Lifecycle

```text
Proposed ──► Accepted ──► Superseded
    │                └──► Deprecated
    └──────► Rejected
```

- **Proposed** — drafted, numbered, under review. A Proposed ADR authorizes nothing.
- **Accepted** — ratified by the BM (§7). Only an Accepted ADR authorizes amendments, and
  ADR-classified work cannot merge until its ADR is Accepted (release plan §2.2).
- **Rejected** — considered and declined. The record is kept; the number is not reused.
- **Superseded** — replaced by a later Accepted ADR that names it in `Supersedes`. The old ADR
  remains in place as history.
- **Deprecated** — the decision no longer applies (e.g. its subject was removed) but no specific ADR
  replaces it. Deprecation itself requires an Accepted ADR stating why, named in `Deprecated-by:`.
  (This obligation is established by this convention — see the marked rows in §9.)

## 7. Approval

- The **Benchmark Maintainer (BM) alone** accepts or rejects an ADR (release plan §1 and §7;
  `role_assignments.md`). For ADRs created under this convention, acceptance is recorded in the ADR
  (`Accepted:` date) and in the decision index (§10); for the recorded ADRs, §5.3 applies.
- The **drafter may not self-ratify**. SO/EL may draft; BM approves. When one actor would be both
  drafter and approver, the BM appoints a separate reviewer or records a no-go (release plan §2.4,
  single-person-role risk). For any ADR touching a **Charter §5 item** and for **public-release
  evidence review**, the appointed reviewer must additionally satisfy the independence eligibility
  rule in `role_assignments.md`: the reviewer must not have drafted or implemented the affected
  artifact and must hold no approval role for it, and the reviewer's identity is recorded by name.
- Acceptance of an ADR does not itself edit any specification: the authorized amendments are applied
  as separate, classified work items approved by the BM (release plan §2.2).

## 8. Immutability and supersession

- ADRs are **append-only**. After acceptance, the body of an ADR MUST NOT be edited, softened, or
  re-argued in place. Grandfathered ADRs (§5.3) are likewise not retrofitted to newer form rules.
- The **ratification transition is part of the acceptance act, not a post-acceptance mutation**.
  Acceptance sets `Status: Accepted` and fills `Accepted:` with the ratification date; rejection
  sets `Status: Rejected` and leaves `Accepted:` as `—`. Both transitions are front-matter edits the
  BM's ratification itself performs and records (§7). Immutability begins after an Accepted
  transition is recorded.
- The only permitted post-acceptance modifications are front-matter bookkeeping that records the
  ADR's fate without altering its content: setting `Status:` to Superseded/Deprecated and filling
  `Superseded-by:` or `Deprecated-by:` when a later ADR replaces or deprecates it.
- A reversed or revised decision is a **new ADR** that names the old one in `Supersedes:` and carries
  the full justification burden of a new decision — including Charter §5 extraordinary justification
  when the subject is Charter-flagged.
- Terminology note: `Supersedes:`/`Superseded-by:` link an ADR that replaces a **prior ADR**. The
  Charter §5 phrase "superseding ADR" is the Charter's own term for the record that overrides a §5
  presumption by naming the clause and arguing the case; that requirement applies as the Charter
  states it, whether or not any prior ADR exists on the subject.
- A missing required ADR, or an accepted ADR whose required amendments are unapplied, is a
  release-blocking governance gap (Benchmark Assurance §7, BL8).

## 9. Mandatory triggers

An ADR is **required** — not optional — for the events below. The table consolidates two kinds of
rows. Rows citing a specification, the Charter, or the plan **index obligations that already exist**;
the cited source governs its own wording, and this table adds no trigger semantics to them. Rows
marked *established here* are **process obligations created by this convention** under V1-002's
authoring mandate; they bind repository process only and touch no benchmark semantics.

| Trigger | Source of the obligation |
|---|---|
| Change to any Formal Definitions entry; a **new** term additionally requires justification against the ontology and acyclicity-preserving insertion | Formal Definitions §36 |
| Any Charter amendment | Charter §7; Charter §5 |
| Any Charter §5 extraordinary-justification decision (label path, redistribution/provenance guarantees, label definition or intervention basis, construct widening, incomplete manifest) | Charter §5 |
| Label semantics change | Benchmark Assurance §9; Label Specification §11 |
| New behavioural state discovered | Benchmark Assurance §9 |
| Benchmark assumption invalidated | Benchmark Assurance §9 |
| New intervention methodology | Benchmark Assurance §9 |
| Ontology modification (artifacts / identity / mutability) | Benchmark Assurance §9 |
| **Major** failure response, if semantics or assumptions are touched | Benchmark Assurance §6 |
| **Critical** failure response (unconditional) | Benchmark Assurance §6 |
| **Catastrophic** failure response (unconditional, under Charter §5) | Benchmark Assurance §6 |
| Resolution of any release-blocking condition | Benchmark Assurance §9 (with §7) |
| Any work the BM classifies as ADR-level under the change-classification gate | Release plan §2.2 |
| Any change Charter §4 classifies as v2, on any of its four axes | *Established here*, consolidating Charter §5 and Benchmark Assurance §9 (which already cover the recorded cases) so that no v2 axis lacks an ADR route |
| Any MAJOR (backward-incompatible definition) change to a versioned specification | [versioning.md](versioning.md) §2 (*established there*; for the Label Specification the obligation already exists in its §11) |
| Deprecation of an Accepted ADR | *Established here* (§6) |

**Changes with no listed trigger route through the classification gate, not to a blanket ADR.** The
following MUST enter the release plan §2.2 change-classification gate before any edit:

- a new or altered normative definition in `docs/` not already covered by a row above (Formal
  Definitions entries are covered by FD §36; label/state/ontology changes by the Assurance rows);
- any substantive change to a `docs/conventions/` convention, including this one (`Status:` and
  `Last-reviewed` bookkeeping excluded);
- a structural repository change;
- a licensing or release-format decision.

For these, an ADR is required only when **(a)** an existing governing authority — the Charter, Formal
Definitions, the Label Specification, Benchmark Assurance, or accepted release governance — requires
one, or **(b)** the BM classifies the change as ADR-level under the gate. The Repository Scaffolding
Proposal's §11.6 draft made these blanket ADR triggers; that draft was never adopted, and this
convention routes them through the accepted classification gate instead.

## 10. Traceability

- Every ADR — whatever its status, including Rejected — **must be indexed** in the decision index:
  `decision_index.md` under `docs/design/release_evidence/spec-v1.0/` while that evidence set is
  active (release plan §2.3). The index is created as V1 release evidence and also records the
  disposition of retired numbers (§3.1–3.2), so numbering gaps are explicable.
- Forward traceability from an accepted ADR to the work that applied it lives in the **decision
  index and the applying work items/issues** — never in post-acceptance edits to the ADR itself
  (§8). Backward traceability lives in the amended documents: every specification clause changed
  under an ADR links back to it. Together these satisfy the bidirectional-trace release requirement
  (Benchmark Assurance BL2).
- Every Accepted ADR's amendment obligations (§5.2 item 5 for new ADRs; §5.3 for the recorded ones)
  must be fully applied before a specification freeze; the ADR-application report
  (`adr_application_report.md`) is the check (release plan §2.3 and §6; Benchmark Assurance BL8).
  The report MUST **reconcile** each required amendment, not merely link it, recording per
  amendment: **(a)** the exact affected file and clause; **(b)** the corresponding git diff
  evidence; **(c)** a semantic-fidelity verification that the applied text matches the amendment the
  ADR authorized — its intent and its exact boundaries, no more and no less; and **(d)** explicit BM
  or Verification Lead sign-off, recorded before the freeze.

## 11. Charter interaction (preserved, not restated)

Two Charter rules bind every decision recorded under this convention and are preserved exactly as the
Charter states them:

- **The v1/v2 test (Charter §4).** The test is a single question: *would existing labels change
  meaning?* A change that alters the label definition, the causal-intervention basis, the output-only
  information bound, or the construct scope is **v2 — a new benchmark**, not a v1 amendment. When in
  doubt, it is v2.
- **Extraordinary justification (Charter §5).** Each Charter §5 item is presumed out of bounds. Making
  such a decision requires a **superseding ADR that names the specific Charter clause it touches and
  argues the case explicitly**; absent that, the decision may not be taken.

This convention adds process (where the record lives, its form, who approves it); it neither weakens
nor reinterprets either rule.

## 12. Relationship to the change-classification gate

While the active release plan is in force, every proposed normative edit first passes the plan §2.2
classification (editorial synchronization / specification amendment / ADR decision), recorded by the
BM. This convention supplies the form of the record when the classification is *ADR decision*. The
classification gate, not this convention, decides which of the three routes applies.

## 13. What this convention deliberately does not do

- It does not rank technical authorities or resolve ADR-versus-spec ordering (owned by V1-007; see
  §2 and ADR-007).
- It does not decide, prejudge, or constrain the outcome of any reserved or future ADR.
- It does not modify ADR-002 or ADR-003, whose accepted content stands as filed (§5.3).
- It does not create issue templates, labels, or CI checks; those are tooling owned by their own work
  packages.
