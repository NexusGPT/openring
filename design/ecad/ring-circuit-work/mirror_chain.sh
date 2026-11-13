#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
# usage: mirror_chain.sh <ring folder of a mirror> <tag> : gen_sch, ERC (report and json), PDF, check_netlist, as run_all.sh,
# on a copy; logs in <work>/logs/chain_<tag>_*.log; check_bom on the mirror's bom.csv with the mirror's netlist.
R="$1"; T="$2"
W=$REPO_ROOT/design/ecad/ring-circuit-work
PY=$REPO_ROOT/design/.venv/bin/python
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
L=$W/logs
cd "$R" || exit 9
PYTHONDONTWRITEBYTECODE=1 nice -n 19 "$PY" -B "$R/gen_sch.py" > "$L/chain_${T}_gen.log" 2>&1; echo "gen_sch exit $?" >> "$L/chain_${T}_gen.log"
nice -n 19 "$KC" sch erc --severity-all --format report -o "$R/erc-report.txt" "$R/ring.kicad_sch" > "$L/chain_${T}_erc.log" 2>&1; echo "erc exit $?" >> "$L/chain_${T}_erc.log"
nice -n 19 "$KC" sch erc --severity-all --format json -o "$R/erc-report.json" "$R/ring.kicad_sch" >> "$L/chain_${T}_erc.log" 2>&1; echo "erc json exit $?" >> "$L/chain_${T}_erc.log"
nice -n 19 "$KC" sch export pdf -o "$R/ring-schematic.pdf" "$R/ring.kicad_sch" > "$L/chain_${T}_pdf.log" 2>&1; echo "pdf exit $?" >> "$L/chain_${T}_pdf.log"
PYTHONDONTWRITEBYTECODE=1 nice -n 19 "$PY" -B "$R/check_netlist.py" > "$L/chain_${T}_check.log" 2>&1; echo "check_netlist exit $?" >> "$L/chain_${T}_check.log"
DS="$(cd "$R/../.." && pwd)"
PYTHONDONTWRITEBYTECODE=1 nice -n 19 "$PY" -B -I $REPO_ROOT/design/tools/check_bom.py "$DS/bom.csv" $REPO_ROOT/design/architecture.md $REPO_ROOT/design/mech/thin/placement.csv "$R/netlist.csv" > "$L/chain_${T}_check_bom.log" 2>&1; echo "check_bom exit $?" >> "$L/chain_${T}_check_bom.log"
echo done > "$L/chain_${T}.exit"
