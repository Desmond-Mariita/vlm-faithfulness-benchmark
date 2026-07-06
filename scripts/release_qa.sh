#!/usr/bin/env bash
# release_qa.sh — V1-029 top-level release QA runner.
#
# Runs the release QA suite from a fresh checkout and prints/records the
# required evidence surfaces (release plan §2.3, §5 V1-029, §6). It runs every
# check even after a failure so one run reports the complete QA state, and it
# exits nonzero if any check failed. No check may silently waive a normative
# requirement (plan §7); failures return to their owning work packages.
#
# Checks and evidence surfaces:
#   qa_metadata_check.sh        -> generates  metadata_check.txt
#   qa_link_check.sh            -> generates  link_check.txt
#   qa_adr_application_check.sh -> validates  adr_application_report.md
#   qa_registry_check.sh        -> validates  open_question_report.md
#   qa_stale_authority_check.sh -> generates  stale_authority_check.txt
#   qa_terminology_check.sh     -> generates  terminology_check.txt
#   qa_normative_set_check.sh   -> validates  normative_file_manifest.tsv
# (all evidence under docs/design/release_evidence/spec-v1.0/)
#
# Operational tooling only: decides no benchmark meaning (v1-029 proposal,
# meaning-preserving operational tooling; no ADR). Exit: 0 = all pass,
# 1 = at least one check failed, 2 = environment error.
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || exit 2
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)" || exit 2
cd "$REPO_ROOT" || exit 2
EVIDENCE_DIR="docs/design/release_evidence/spec-v1.0"

checks=(
  qa_metadata_check.sh
  qa_link_check.sh
  qa_adr_application_check.sh
  qa_registry_check.sh
  qa_stale_authority_check.sh
  qa_terminology_check.sh
  qa_normative_set_check.sh
)
declare -A surface=(
  [qa_metadata_check.sh]="generates  $EVIDENCE_DIR/metadata_check.txt"
  [qa_link_check.sh]="generates  $EVIDENCE_DIR/link_check.txt"
  [qa_adr_application_check.sh]="validates $EVIDENCE_DIR/adr_application_report.md"
  [qa_registry_check.sh]="validates $EVIDENCE_DIR/open_question_report.md"
  [qa_stale_authority_check.sh]="generates  $EVIDENCE_DIR/stale_authority_check.txt"
  [qa_terminology_check.sh]="generates  $EVIDENCE_DIR/terminology_check.txt"
  [qa_normative_set_check.sh]="validates $EVIDENCE_DIR/normative_file_manifest.tsv"
)

commit="$(git rev-parse --short HEAD 2>/dev/null || echo 'no-git')"
dirty=""
[ -n "$(git status --porcelain 2>/dev/null)" ] && dirty=" (working tree dirty)"
echo "release_qa: Benchmark Specification v1.0 release QA suite (V1-029)"
echo "release_qa: repo=$REPO_ROOT commit=${commit}${dirty}"
echo "release_qa: run=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo

failed=0
env_error=0
declare -A result
for c in "${checks[@]}"; do
  if [ ! -x "$SCRIPT_DIR/$c" ]; then
    echo "release_qa: ERROR — missing or non-executable check: scripts/$c" >&2
    exit 2
  fi
  echo "release_qa: ── running scripts/$c"
  if "$SCRIPT_DIR/$c"; then
    result[$c]="PASS"
  else
    status=$?
    if [ "$status" -eq 2 ]; then
      result[$c]="ERROR"
      env_error=1
    else
      result[$c]="FAIL"
      failed=$((failed + 1))
    fi
  fi
  echo
done

echo "release_qa: ── summary"
for c in "${checks[@]}"; do
  printf 'release_qa: %-4s %-28s %s\n' "${result[$c]}" "$c" "${surface[$c]}"
done
echo

if [ "$failed" -eq 0 ]; then
  if [ "$env_error" -eq 0 ]; then
    echo "release_qa: RESULT PASS — all ${#checks[@]} checks green"
    exit 0
  fi
fi
if [ "$env_error" -ne 0 ]; then
  echo "release_qa: RESULT ERROR — at least one subcheck returned environment error (exit 2)"
  exit 2
fi
echo "release_qa: RESULT FAIL — $failed of ${#checks[@]} checks failed; each failure returns to its owning work package (plan §7)"
exit 1
