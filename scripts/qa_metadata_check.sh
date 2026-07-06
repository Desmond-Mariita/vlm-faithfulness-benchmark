#!/usr/bin/env bash
# qa_metadata_check.sh — V1-029 release QA: metadata check for the exact normative set.
#
# Mechanically verifies (release plan §2.3, §6 "Normative contract" / "Repository QA"):
#   1. Every file in the exact normative set (release plan V1-030 enumeration:
#      Charter, Vision, 01, 03, 05, 06, 06a, 07, 08, 09, 10, 11, and accepted ADRs)
#      exists and carries a YAML front-matter block.
#   2. Every normative specification declares Title: and Status:; the freeze
#      expectation is Status: Accepted and Benchmark-Version: v1.0 (plan §6).
#      Pre-freeze Draft status is reported as a failure finding by design: the
#      check goes green only when V1-032 sets the authorized freeze metadata.
#   3. Every decisions/ADR-*.md declares a valid Status; Accepted ADRs carry an
#      Accepted: date (decision-records convention §5.1, §8).
#   4. When normative_file_manifest.tsv exists (V1-030), each manifest row's
#      status/version columns match the file's front matter. A missing manifest
#      is reported as WARN here; its absence is a failure owned by
#      qa_normative_set_check.sh.
#
# Operational tooling only: this script decides no benchmark meaning
# (v1-029 proposal §1-§2). Evidence: docs/design/release_evidence/spec-v1.0/metadata_check.txt
# Exit: 0 = pass, 1 = findings, 2 = environment error.
set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)" || exit 2
cd "$REPO_ROOT" || exit 2
EVIDENCE_DIR="docs/design/release_evidence/spec-v1.0"
OUT="$EVIDENCE_DIR/metadata_check.txt"
MANIFEST="$EVIDENCE_DIR/normative_file_manifest.tsv"
[ -d "$EVIDENCE_DIR" ] || { echo "ERROR: evidence directory missing: $EVIDENCE_DIR" >&2; exit 2; }

NORMATIVE_DOCS=(
  docs/00_Benchmark_Charter.md
  VISION.md
  docs/01_Benchmark_Design.md
  docs/03_Problem_Definition.md
  docs/05_Formal_Definitions.md
  docs/06_Label_Specification.md
  docs/06a_Benchmark_Data_Model.md
  docs/07_Label_Generation_Pipeline.md
  docs/08_Dataset_Specification.md
  docs/09_Baseline_Systems.md
  docs/10_Evaluation_Protocol.md
  docs/11_Benchmark_Assurance.md
)

findings=()
info=()

# front_matter_field FILE FIELD -> prints value or nothing
front_matter_field() {
  awk -v field="$2" '
    NR==1 && $0!="---" { exit }
    NR>1 && $0=="---" { exit }
    NR>1 && index($0, field ":")==1 {
      v=substr($0, length(field)+2); gsub(/^[ \t]+|[ \t]+$/, "", v); print v; exit
    }' "$1"
}

has_front_matter() {
  [ "$(head -n1 "$1")" = "---" ] && awk 'NR>1 && $0=="---" {found=1; exit} END{exit !found}' "$1"
}

for f in "${NORMATIVE_DOCS[@]}"; do
  if [ ! -f "$f" ]; then
    findings+=("missing normative file: $f")
    continue
  fi
  if ! has_front_matter "$f"; then
    findings+=("$f: no YAML front-matter block")
    continue
  fi
  title="$(front_matter_field "$f" Title)"
  status="$(front_matter_field "$f" Status)"
  version="$(front_matter_field "$f" Benchmark-Version)"
  [ -n "$title" ]  || findings+=("$f: front matter lacks Title:")
  [ -n "$status" ] || findings+=("$f: front matter lacks Status:")
  if [ "$status" != "Accepted" ]; then
    findings+=("$f: Status is '$status' (freeze candidate expects 'Accepted'; set by V1-032 as authorized)")
  fi
  if [ -z "$version" ]; then
    findings+=("$f: front matter lacks Benchmark-Version: (freeze candidate expects v1.0)")
  elif [ "$version" != "v1.0" ]; then
    findings+=("$f: Benchmark-Version is '$version' (freeze candidate expects exact 'v1.0')")
  fi
  info+=("$f: Status='$status' Benchmark-Version='${version:-—}'")
done

# ADR register metadata
shopt -s nullglob
adr_files=(decisions/ADR-*.md)
shopt -u nullglob
[ "${#adr_files[@]}" -gt 0 ] || findings+=("no decisions/ADR-*.md files found")
for f in "${adr_files[@]}"; do
  if ! has_front_matter "$f"; then
    findings+=("$f: no YAML front-matter block")
    continue
  fi
  status="$(front_matter_field "$f" Status)"
  accepted="$(front_matter_field "$f" Accepted)"
  case "$status" in
    Accepted|Proposed|Rejected|Superseded|Deprecated) : ;;
    *) findings+=("$f: invalid ADR Status '$status'") ;;
  esac
  # Ratification evidence: accepted ADRs require an Accepted: date, except for
  # the grandfathered ADR-002/ADR-003 records (decision-records §3.2, §5.3),
  # which may carry a Date: field with acceptance evidenced by the decision
  # index.
  if [ "$status" = "Accepted" ] && ! [[ "$accepted" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    case "$f" in
      decisions/ADR-002-*|decisions/ADR-003-*)
        adr_date="$(front_matter_field "$f" Date)"
        if ! [[ "$adr_date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
          findings+=("$f: grandfathered Accepted ADR lacks ratification date in Accepted: or Date:")
        fi
        ;;
      *)
        findings+=("$f: Status Accepted but missing required Accepted: ratification date")
        ;;
    esac
  fi
  info+=("$f: Status='$status' Accepted='${accepted:-—}'")
done

# Cross-check against the normative manifest when present (V1-030 output).
if [ -f "$MANIFEST" ]; then
  while IFS=$'\t' read -r m_path m_authority m_status m_version m_hash; do
    [ "$m_path" = "path" ] && continue
    [ -z "$m_path" ] && continue
    if [ ! -f "$m_path" ]; then
      findings+=("manifest row names missing file: $m_path")
      continue
    fi
    f_status="$(front_matter_field "$m_path" Status)"
    f_version="$(front_matter_field "$m_path" Benchmark-Version)"
    [ "$f_status" = "$m_status" ] || \
      findings+=("$m_path: front-matter Status '$f_status' != manifest status '$m_status'")
    if [ -n "$m_version" ] && [ "$m_version" != "—" ] && [ "$f_version" != "$m_version" ]; then
      findings+=("$m_path: front-matter Benchmark-Version '$f_version' != manifest version '$m_version'")
    fi
  done < "$MANIFEST"
else
  info+=("WARN: $MANIFEST not present (V1-030 pending); status/version cross-check skipped")
fi

commit="$(git rev-parse --short HEAD 2>/dev/null || echo 'no-git')"
dirty=""
[ -n "$(git status --porcelain 2>/dev/null)" ] && dirty=" (working tree dirty)"
{
  echo "# metadata_check.txt — generated by scripts/qa_metadata_check.sh (V1-029)"
  echo "# Run: $(date -u +%Y-%m-%dT%H:%M:%SZ)  commit: ${commit}${dirty}"
  echo "# Scope: exact normative set per release plan V1-030 enumeration + decisions/ADR-*.md"
  if [ "${#findings[@]}" -eq 0 ]; then
    echo "RESULT: PASS (0 findings)"
  else
    echo "RESULT: FAIL (${#findings[@]} findings)"
    for x in "${findings[@]}"; do echo "FINDING: $x"; done
  fi
  for x in "${info[@]}"; do echo "INFO: $x"; done
} > "$OUT"

echo "qa_metadata_check: wrote $OUT"
if [ "${#findings[@]}" -eq 0 ]; then
  echo "qa_metadata_check: PASS"
  exit 0
fi
echo "qa_metadata_check: FAIL (${#findings[@]} findings)"
sed -n 's/^FINDING: /  - /p' "$OUT"
exit 1
