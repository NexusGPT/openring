#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
# usage: run_all.sh <tag>  - generate, ERC, PDF, netlist export, check; logs in evidence/
R=$REPO_ROOT/design/ecad/case
PY=$REPO_ROOT/design/.venv/bin/python
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
T=${1:-run}
E=$R/evidence
cd "$R" || exit 9
"$PY" "$R/gen_sch.py" > "$E/gen_$T.log" 2>&1; echo "gen_sch exit $?" | tee -a "$E/gen_$T.log"
"$KC" sch erc --severity-all --format report -o "$R/erc-report.txt" "$R/case.kicad_sch" > "$E/erc_$T.log" 2>&1; echo "erc exit $?" | tee -a "$E/erc_$T.log"
cp "$R/erc-report.txt" "$E/erc-report_$T.txt"
"$KC" sch erc --severity-all --format json -o "$R/erc-report.json" "$R/case.kicad_sch" >> "$E/erc_$T.log" 2>&1
"$KC" sch export pdf -o "$R/case-schematic.pdf" "$R/case.kicad_sch" > "$E/pdf_$T.log" 2>&1; echo "pdf exit $?" | tee -a "$E/pdf_$T.log"
if [ -f "$R/check_netlist.py" ]; then
  "$PY" "$R/check_netlist.py" > "$E/check_$T.log" 2>&1; echo "check_netlist exit $?" | tee -a "$E/check_$T.log"
fi
