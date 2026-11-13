#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# Checks every quote in quotes-list.txt with grep -n -F in its saved text copy.
# Output goes to quotes-verify.log; the last line is the count.
# (case lookup instead of declare -A: macOS /bin/bash 3.2 has no associative arrays)
R="$REPO_ROOT"
OUT="$R/design/ecad/ring/c76-c77-work"
D="$R/design"
filefor() {
  case "$1" in
    GRM0335) echo "$R/design/datasheets/c76_murata_GRM0335C1H102JE01.txt" ;;
    GRM033R71) echo "$R/design/datasheets/c76_murata_GRM033R71H102KA12.txt" ;;
    PARTS) echo "$D/ecad/ring/parts.csv" ;;
    NPM) echo "$D/ecad/ring/npm1304-reference.md" ;;
    BOM) echo "$D/bom.csv" ;;
    BOMNOTES) echo "$D/bom-notes.md" ;;
    SCHNOTES) echo "$D/ecad/ring/sch-notes.md" ;;
    PMIC) echo "$D/ecad/ring/pmic-caps-facts.md" ;;
    DS) echo "$D/datasheets/npm1304_datasheet_v1_0.txt" ;;
    AVXKGM) echo "$D/datasheets/c76_kyocera-avx_C0GNP0-KGM.txt" ;;
  esac
}
n=0
m=0
while IFS='|' read -r key q; do
  f="$(filefor "$key")"
  n=$((n+1))
  hit=$(grep -n -F -- "$q" "$f" 2>&1 | head -1)
  if [ -z "$hit" ]; then
    m=$((m+1))
    echo "NOT FOUND | $key | $q | $f"
  else
    echo "FOUND | $key | $q | $(basename "$f"):$hit"
  fi
done < "$OUT/quotes-list.txt" > "$OUT/quotes-verify.log" 2>&1
echo "quotes checked $n, not found $m" >> "$OUT/quotes-verify.log"
