# Contributing

Thank you for your interest. This repository holds a **frozen, versioned benchmark
specification**, so contribution works differently than in a typical software project: the
primary object of change is *meaning*, and meaning is governed.

## Ground rules

1. **Released specifications are immutable.** A document released at v1.0 is never edited in
   place for semantic content. Post-release semantic defects go through the decision process and
   produce a *new specification version*; they do not receive in-place fixes (release plan §7).
2. **Every change is classified before it is made.** The classification scale
   (MAJOR / MINOR / PATCH) and what engages an ADR are defined in
   [`docs/conventions/versioning.md`](docs/conventions/versioning.md). Anything that changes what
   an existing artifact, term, or label *means* is MAJOR and requires an Architecture Decision
   Record per [`docs/conventions/decision-records.md`](docs/conventions/decision-records.md).
3. **ADRs are append-only.** An accepted ADR is never edited; it is revised only by a superseding
   ADR that names it.
4. **Authority is fixed.** Which document governs which question — and the precedence between
   ADRs and specifications — is settled by
   [ADR-007](decisions/ADR-007-Authority-Precedence-and-ADR-Specification-Ordering.md). Proposals
   that would silently move authority between documents will be declined.

## How to propose a change

- **Editorial fix** (typo, broken link, formatting — changes no definition, eligibility, verdict,
  or behavior): open an issue or pull request describing the fix. These are PATCH-class and can
  be accepted directly into supporting material; for normative documents they take effect only in
  a subsequent tagged specification release.
- **Substantive proposal** (new definition, changed semantics, new label value, pipeline change):
  open an issue that states (a) the exact clause(s) affected, (b) the proposed change, and (c) why
  it is needed. The maintainer classifies it under the versioning convention; if it is ADR-level,
  a draft ADR following the house format in [`decisions/`](decisions/) is the working artifact.
- **Questions about intent** are welcome as issues. Answers may become clarifying PATCH text, but
  an issue thread is never itself authoritative.

## What not to submit

- Corpus data, model outputs, or labels — no corpus is released yet, and corpus artifacts have
  their own release train and licensing.
- Changes to release evidence under
  [`docs/design/release_evidence/`](docs/design/release_evidence/) — evidence records history and
  is not revised.

## Code standards (applies to all code, current and future)

No implementation code is released yet; when it lands (release plan V1-038 onward), all code in
this repository — contributed or maintainer-authored — must meet this bar:

- **Docstrings & type hints.** Google-style docstrings (`Args:`, `Returns:`, `Raises:`) and
  PEP 484 type hints on every public function, method, and class.
- **Math from scratch.** Formulas specified by the benchmark documents are implemented manually
  and legibly; no high-level black-box solvers standing in for a specified computation. (This is
  the code-level face of the core principle: ground truth is defined by specifications, not by
  implementation — a reviewer must be able to check the code against the spec clause.)
- **LaTeX above implementations.** Every implemented formula carries its LaTeX form in a comment
  directly above the implementation, citing the owning specification clause.
- **Small, testable units.** Prefer small functions with the engineering reasoning stated in
  comments; a unit that cannot be tested in isolation is a design smell.
- **Invariants are encoded, not assumed.** Assumptions become `assert` statements or dedicated
  unit tests — in particular the spec's stated invariants (state-model totality, precedence
  rules, manifest hash equality).

Pull requests with code that does not meet this bar will be asked to revise before review.

## Licensing of contributions

By contributing, you agree your contributions are licensed under the repository licenses: CC BY
4.0 for documentation and specification text, Apache-2.0 for code ([`README.md`](README.md)
"License").
