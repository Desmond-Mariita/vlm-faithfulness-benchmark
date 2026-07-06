#!/usr/bin/env bash
# qa_adr_application_check.sh — V1-029 release QA: ADR-application report check.
#
# Mechanically validates docs/design/release_evidence/spec-v1.0/adr_application_report.md
# against the accepted amendment trail (decision-records convention §10; release
# plan §2.3, §6 "Repository QA": ADR application report passes):
#   1. The report exists (it is produced by the ADR-application reporting work,
#      not by this check; a missing report is a failure, not a waiver).
#   2. Every ADR in decisions/ with front-matter Status: Accepted is reconciled
#      in the report (its ADR-NNN identifier appears).
#   3. The report carries the §10 reconciliation elements for each accepted ADR
#      in a dedicated ADR section or table row keyed by ADR id: affected
#      file/clause records, git diff evidence, semantic-fidelity verification,
#      and explicit BM or Verification Lead (VQ) sign-off.
#
# This check READS the report only. It never writes to or overwrites the report
# or its human sign-off fields (v1-029 proposal §7 item 3). It emits no separate
# evidence file: the report itself is the §2.3 evidence surface.
#
# Operational tooling only: decides no benchmark meaning (v1-029 proposal §1-§2).
# Exit: 0 = pass, 1 = findings, 2 = environment error.
set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)" || exit 2
cd "$REPO_ROOT" || exit 2
REPORT="docs/design/release_evidence/spec-v1.0/adr_application_report.md"

findings=()

if [ ! -f "$REPORT" ]; then
  echo "qa_adr_application_check: FAIL"
  echo "  - $REPORT not present (pending upstream reporting work; decision-records §10 requires it before freeze)"
  exit 1
fi

# Accepted ADR identifiers from the decision register front matter.
accepted_ids=()
shopt -s nullglob
for f in decisions/ADR-*.md; do
  status="$(awk 'NR==1 && $0!="---" {exit} NR>1 && $0=="---" {exit} NR>1 && index($0,"Status:")==1 {v=substr($0,8); gsub(/^[ \t]+|[ \t]+$/,"",v); print v; exit}' "$f")"
  if [ "$status" = "Accepted" ]; then
    id="$(basename "$f" | grep -oE '^ADR-[0-9]{3}')"
    [ -n "$id" ] && accepted_ids+=("$id")
  fi
done
shopt -u nullglob
[ "${#accepted_ids[@]}" -gt 0 ] || findings+=("no accepted ADRs found in decisions/ (cannot reconcile an empty trail)")

for id in "${accepted_ids[@]}"; do
  block=""
  block="$(
    awk -v id="$id" '
      function heading_level(line,   tmp) {
        match(line, /^#+/)
        return RLENGTH
      }
      BEGIN { capture=0; level=0; seen=0 }
      {
        if (!capture && $0 ~ "^#+[[:space:]]+" id "([[:space:]]|$)") {
          capture=1
          level=heading_level($0)
          seen=1
          print
          next
        }
        if (capture) {
          if ($0 ~ /^#+[[:space:]]+/ && heading_level($0) <= level) exit
          print
        }
      }
      END {
        if (!seen) exit 3
      }
    ' "$REPORT"
  )" || true

  if [ -z "$block" ]; then
    block="$(
      awk -v id="$id" '
        BEGIN { seen=0 }
        $0 ~ "^[[:space:]]*\\|[[:space:]]*" id "[[:space:]]*\\|" {
          print
          seen=1
          exit
        }
        END { if (!seen) exit 3 }
      ' "$REPORT"
    )" || true
  fi

  if [ -z "$block" ]; then
    findings+=("$REPORT: accepted $id is not reconciled in the report")
    continue
  fi
  echo "$block" | grep -qiE 'affected[[:space:]]+file.*clause|clause.*affected[[:space:]]+file|file.*clause|clause.*file' || \
    findings+=("$REPORT: accepted $id lacks explicit affected file/clause reconciliation in its local block (§10 element a)")
  echo "$block" | grep -qiE 'git[[:space:]]+diff|diff|commit [0-9a-f]{7}|[0-9a-f]{7,40}' || \
    findings+=("$REPORT: accepted $id lacks git diff / commit evidence in its local block (§10 element b)")
  echo "$block" | grep -qiE 'fidelity' || \
    findings+=("$REPORT: accepted $id lacks semantic-fidelity verification in its local block (§10 element c)")
  if ! echo "$block" | grep -qiE 'sign(ed)?[- ]?off' || ! echo "$block" | grep -qE 'BM|Verification Lead|VQ'; then
    findings+=("$REPORT: accepted $id lacks explicit BM/VQ sign-off in its local block (§10 element d)")
  fi
done

echo "qa_adr_application_check: reconciled ${#accepted_ids[@]} accepted ADR(s) against $REPORT"
if [ "${#findings[@]}" -eq 0 ]; then
  echo "qa_adr_application_check: PASS"
  exit 0
fi
echo "qa_adr_application_check: FAIL (${#findings[@]} findings)"
for x in "${findings[@]}"; do echo "  - $x"; done
exit 1
