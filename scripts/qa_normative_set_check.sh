#!/usr/bin/env bash
# qa_normative_set_check.sh — V1-029 release QA: normative-set enumeration check.
#
# Mechanically validates docs/design/release_evidence/spec-v1.0/normative_file_manifest.tsv
# (produced and BM-signed by V1-030) against the release plan's exact normative
# enumeration (plan §5 V1-030, §6 "Normative contract"):
#   1. The manifest exists (missing = failure: V1-030 pending).
#   2. Header is the five-column contract, tab-separated:
#      path <TAB> authority <TAB> status <TAB> version <TAB> hash
#   3. Every listed path exists and its SHA-256 equals the hash column.
#   4. Set equality with the plan enumeration: Charter, Vision, 01, 03, 05, 06,
#      06a, 07, 08, 09, 10, 11, and every decisions/ADR-*.md whose front matter
#      is Status: Accepted. Missing rows and unexpected extra rows both fail.
#   5. Explicitly non-normative surfaces (04, the release plan, reviews,
#      inventories, design history) must not appear in the manifest.
#
# The manifest's classification content is BM's (V1-030); this tool only checks
# the enumeration mechanically and decides no authority itself.
#
# Operational tooling only: decides no benchmark meaning (v1-029 proposal §1-§2).
# Exit: 0 = pass, 1 = findings, 2 = environment error.
set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)" || exit 2
cd "$REPO_ROOT" || exit 2
MANIFEST="docs/design/release_evidence/spec-v1.0/normative_file_manifest.tsv"

findings=()
declare -A seen_paths=()

front_matter_field() {
  awk -v field="$2" '
    NR==1 && $0!="---" { exit }
    NR>1 && $0=="---" { exit }
    NR>1 && index($0, field ":")==1 {
      v=substr($0, length(field)+2); gsub(/^[ \t]+|[ \t]+$/, "", v); print v; exit
    }' "$1"
}

expected_authority_for() {
  case "$1" in
    docs/00_Benchmark_Charter.md) echo "Benchmark Charter" ;;
    VISION.md) echo "Vision" ;;
    docs/01_Benchmark_Design.md) echo "Benchmark Design" ;;
    docs/03_Problem_Definition.md) echo "Problem Definition" ;;
    docs/05_Formal_Definitions.md) echo "Formal Definitions" ;;
    docs/06_Label_Specification.md) echo "Label Specification" ;;
    docs/06a_Benchmark_Data_Model.md) echo "Benchmark Data Model" ;;
    docs/07_Label_Generation_Pipeline.md) echo "Label Generation Pipeline" ;;
    docs/08_Dataset_Specification.md) echo "Dataset Specification" ;;
    docs/09_Baseline_Systems.md) echo "Baseline Systems" ;;
    docs/10_Evaluation_Protocol.md) echo "Evaluation Protocol" ;;
    docs/11_Benchmark_Assurance.md) echo "Benchmark Assurance" ;;
    decisions/ADR-*.md) front_matter_field "$1" Title ;;
    *) return 1 ;;
  esac
}

if [ ! -f "$MANIFEST" ]; then
  echo "qa_normative_set_check: FAIL"
  echo "  - $MANIFEST not present (produced by V1-030; required before freeze per plan §6)"
  exit 1
fi

# Expected exact set (release plan V1-030 row).
expected=(
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
shopt -s nullglob
for f in decisions/ADR-*.md; do
  status="$(awk 'NR==1 && $0!="---" {exit} NR>1 && $0=="---" {exit} NR>1 && index($0,"Status:")==1 {v=substr($0,8); gsub(/^[ \t]+|[ \t]+$/,"",v); print v; exit}' "$f")"
  [ "$status" = "Accepted" ] && expected+=("$f")
done
shopt -u nullglob

# 2. Header contract.
header="$(head -n1 "$MANIFEST")"
if [ "$header" != "$(printf 'path\tauthority\tstatus\tversion\thash')" ]; then
  findings+=("$MANIFEST: header is not 'path<TAB>authority<TAB>status<TAB>version<TAB>hash'")
fi

# 3. Rows: existence and hash equality.
listed=()
while IFS=$'\t' read -r m_path m_authority m_status m_version m_hash; do
  [ "$m_path" = "path" ] && continue
  [ -z "$m_path" ] && continue
  if [ -n "${seen_paths[$m_path]+x}" ]; then
    findings+=("$MANIFEST: duplicate path entry: $m_path")
    continue
  fi
  seen_paths[$m_path]=1
  listed+=("$m_path")
  if [ ! -f "$m_path" ]; then
    findings+=("$MANIFEST: listed file missing: $m_path")
    continue
  fi
  for col in "$m_authority" "$m_status" "$m_version" "$m_hash"; do
    [ -n "$col" ] || { findings+=("$MANIFEST: incomplete row for $m_path"); break; }
  done
  expected_authority="$(expected_authority_for "$m_path" 2>/dev/null || true)"
  if [ -n "$expected_authority" ] && [ "$m_authority" != "$expected_authority" ]; then
    findings+=("$MANIFEST: authority mismatch for $m_path (manifest '$m_authority' != expected '$expected_authority')")
  fi
  if [ -n "$m_hash" ]; then
    actual="$(sha256sum "$m_path" | cut -d' ' -f1)"
    [ "$actual" = "$m_hash" ] || \
      findings+=("$MANIFEST: hash mismatch for $m_path (manifest ${m_hash:0:12}…, actual ${actual:0:12}…)")
  fi
done < "$MANIFEST"

# 4. Set equality.
for e in "${expected[@]}"; do
  found=0
  for l in "${listed[@]:-}"; do [ "$l" = "$e" ] && { found=1; break; }; done
  [ "$found" -eq 1 ] || findings+=("$MANIFEST: expected normative file not enumerated: $e")
done
for l in "${listed[@]:-}"; do
  found=0
  for e in "${expected[@]}"; do [ "$e" = "$l" ] && { found=1; break; }; done
  [ "$found" -eq 1 ] || findings+=("$MANIFEST: unexpected entry outside the plan enumeration: $l")
done

# 5. Explicitly non-normative surfaces.
for banned in docs/04_Legacy_Terminology_Mapping.md docs/design/Benchmark_v1.0_Release_Plan.md; do
  for l in "${listed[@]:-}"; do
    [ "$l" = "$banned" ] && findings+=("$MANIFEST: explicitly non-normative file enumerated as normative: $banned")
  done
done
for l in "${listed[@]:-}"; do
  case "$l" in
    reviews/*) findings+=("$MANIFEST: review evidence enumerated as normative: $l") ;;
  esac
done

echo "qa_normative_set_check: validated $MANIFEST (${#listed[@]} rows vs ${#expected[@]} expected files)"
if [ "${#findings[@]}" -eq 0 ]; then
  echo "qa_normative_set_check: PASS"
  exit 0
fi
echo "qa_normative_set_check: FAIL (${#findings[@]} findings)"
for x in "${findings[@]}"; do echo "  - $x"; done
exit 1
