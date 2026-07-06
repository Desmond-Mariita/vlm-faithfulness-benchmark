# Public release checklist — Benchmark Specification v1.0 (V1-037)

**Release:** Public Specification v1.0, tag `benchmark-spec-v1.0` (M5)
**Date:** 2026-07-06
**Approver:** Benchmark Maintainer (Desmond Mariita) — approval recorded for V1-033 through
V1-037 before packaging began.

"Pass" means the evidence exists in this repository or is stated inline; verbal confirmation does
not count (release plan §2, §6).

## V1-033 — License posture

- [x] Root `LICENSE` is the canonical CC BY 4.0 text (specification text and documentation).
- [x] `LICENSE-CODE` is the canonical Apache License 2.0 text (future source code).
- [x] Licensing statement in `README.md` §License separates specification text, code, and
      corpus/third-party data.
- [x] Corpus rights are not overclaimed: README, CONTRIBUTING, release notes, and CITATION all
      state that no corpus is released and no third-party data rights are granted or claimed.

## V1-034 — Root README

- [x] Contains purpose, exact authority/read order (normative set defined by
      `normative_file_manifest.tsv`), governance pointer, status, implementation entry point,
      license, citation, and the deliberate-numbering-gaps explanation.
- [x] Declares itself non-normative and creates no technical authority.
- [x] Fresh-reader review: three independent external reviewers (DeepSeek, Gemini, Codex)
      reviewed the packaging files against the V1-033/034/036 acceptance criteria with no
      private context beyond the attached files. Consensus: approve-after-fixes; all findings
      (one Major: CITATION `type`; five Minor/Nit) were fixed before tagging. Review records are
      retained in the private archive repository.

## V1-035 — Archive / public-tree cleanup

- [x] Public tree is a curated set: the 19 frozen normative files, governing conventions,
      the (non-normative) release plan, supporting design documents, cited external review
      records, QA tooling, and release evidence — plus the packaging files.
- [x] Private working material (project-origin brief, proposal drafts, internal review
      transcripts not cited by the normative set, agent configuration) is retained only in the
      private archive repository and is absent from this repository and its history (fresh
      packaging history; no ambiguous `00_` peers).
- [x] Link check over the public tree: zero broken internal links
      (`link_check.txt`, regenerated in this tree).

## V1-036 — Community and citation files

- [x] `CONTRIBUTING.md` routes changes through the accepted governance (change classification,
      ADR process, immutability of released specifications).
- [x] `CITATION.cff` (CFF 1.2.0, `type: software`, `version: v1.0`) identifies the release;
      `CHANGELOG.md` lineage names the internal freeze commit `75e0320` and tag
      `benchmark-spec-v1.0-freeze`.
- [x] Specification release notes published
      ([`release_notes_spec_v1.0.md`](release_notes_spec_v1.0.md)).

## V1-037 — Release transaction

- [x] **Normative hash equality:** SHA-256 of all 19 normative files in this tree verified
      byte-identical to the freeze manifest (`normative_file_manifest.tsv`), 19/19 OK, verified
      2026-07-06 in the packaging tree.
- [x] Release QA suite (`scripts/release_qa.sh`) green on the packaging tree: metadata, link,
      ADR-application, open-question registry, stale-authority, terminology, and normative-set
      checks all PASS.
- [x] Annotated tag `benchmark-spec-v1.0` created on the packaging commit that introduces this
      checklist (the freeze tag `benchmark-spec-v1.0-freeze` remains distinct, on the private
      archive's freeze commit, per versioning convention §6).
- [x] Fresh-clone smoke check: clean clone of the packaging repository; hash verification and
      QA suite re-run green in the clone.
- [x] Public specification release does **not** imply corpus readiness (release plan §7); the
      corpus train is untouched.
