#!/usr/bin/env bash
# qa_registry_check.sh — V1-029 release QA: open-registry / stale-open-item check.
#
# Mechanically validates docs/design/release_evidence/spec-v1.0/open_question_report.md
# (release plan §2.3, §6 "Normative contract": no v1-blocking open registry
# entry remains; V1-026 acceptance evidence):
#   1. The report exists.
#   2. It carries the explicit conclusion that no v1 blocker remains.
#   3. Every line mentioning a blocker is a negation ("no ... blocker",
#      "not a blocker", "non-blocking"); a non-negated blocker mention fails.
#   4. Every item the report lists as open names an owner (owned-by / owner /
#      governance / implementation-owned routing).
#   5. Stale-pointer scan: every open-question identifier the report cites
#      (Qn / Q-En) still exists in at least one normative specification's
#      open-questions registry — a report item pointing at a removed registry
#      entry is stale.
#
# This check reads registries only; it never edits the report or a
# specification. Operational tooling: decides no benchmark meaning
# (v1-029 proposal §1-§2). Exit: 0 = pass, 1 = findings, 2 = environment error.
set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)" || exit 2
cd "$REPO_ROOT" || exit 2
REPORT="docs/design/release_evidence/spec-v1.0/open_question_report.md"

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

open_question_registry_qids() {
  awk '
    BEGIN { in_section=0 }
    /^##[[:space:]]+[0-9]+\.[[:space:]]+Open questions/ { in_section=1; next }
    /^##[[:space:]]+[0-9]+\.[[:space:]]+/ && in_section { exit }
    in_section { print }
  ' "$1" | grep -oE 'Q-E[0-9]+|Q[0-9]+' | sort -u
}

if [ ! -f "$REPORT" ]; then
  echo "qa_registry_check: FAIL"
  echo "  - $REPORT not present (produced by V1-026; required release evidence per plan §2.3)"
  exit 1
fi

# 2. Explicit no-v1-blocker conclusion.
grep -qi 'No v1 blocker remains' "$REPORT" || \
  findings+=("$REPORT: missing explicit 'No v1 blocker remains' conclusion")

# 3. Non-negated blocker mentions.
while IFS= read -r line; do
  if ! echo "$line" | grep -qiE 'no[t]? [^.;]*block(er|ing)|non-blocking|blocker status|without [^.;]*blocker'; then
    findings+=("$REPORT: non-negated blocker mention: '$(echo "$line" | sed 's/^[[:space:]]*//' | cut -c1-100)'")
  fi
done < <(grep -inE 'blocker|blocking' "$REPORT" | sed 's/^[0-9]*://')

# 4. Open items must name an owner.
while IFS= read -r line; do
  if ! echo "$line" | grep -qiE 'owned|owner|governance|implementation-owned|deferred to|policy|decision'; then
    findings+=("$REPORT: open item without owner routing: '$(echo "$line" | sed 's/^[[:space:]]*//' | cut -c1-100)'")
  fi
done < <(awk '
  BEGIN { in_section=0 }
  /^##[[:space:]]+3\./ { in_section=1; next }
  /^##[[:space:]]+[0-9]+\./ && $0 !~ /^##[[:space:]]+3\./ { in_section=0 }
  in_section &&
  /^[[:space:]]*-[[:space:]]+\*?\*?Q(-E)?[0-9]+/ &&
  tolower($0) !~ /resolved|not a blocker|non-blocking/ { print }
' "$REPORT")

# 5. Stale-pointer scan: report QIDs must still exist in a normative registry.
while IFS= read -r qid; do
  found=0
  for f in "${NORMATIVE_DOCS[@]}"; do
    [ -f "$f" ] || continue
    if open_question_registry_qids "$f" | grep -qx "$qid"; then found=1; break; fi
  done
  [ "$found" -eq 1 ] || findings+=("$REPORT: cites $qid but no normative specification mentions it (stale pointer)")
done < <(
  awk '
  BEGIN { in_section=0 }
  /^##[[:space:]]+3\./ { in_section=1; next }
  /^##[[:space:]]+[0-9]+\./ && $0 !~ /^##[[:space:]]+3\./ { in_section=0 }
  in_section &&
  /^[[:space:]]*-[[:space:]]+\*?\*?Q(-E)?[0-9]+/ &&
  tolower($0) !~ /resolved|not a blocker|non-blocking/ { print }
  ' "$REPORT" | grep -oE 'Q-E[0-9]+|Q[0-9]+' | sort -u
)

echo "qa_registry_check: validated $REPORT"
if [ "${#findings[@]}" -eq 0 ]; then
  echo "qa_registry_check: PASS"
  exit 0
fi
echo "qa_registry_check: FAIL (${#findings[@]} findings)"
for x in "${findings[@]}"; do echo "  - $x"; done
exit 1
