#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# lines.sh board tag : export Gerber (copper, outline) and drill of the board as make_fab.sh does into fab-<tag>/, run the controlled-line
# read-back (rb/p4p5.py) and the pcbnew cross-check (rb/xcheck_clear.py). Logs: logs/p4p5-<tag>.log, logs/xcheck-<tag>.log, then a summary.
I=$REPO_ROOT/design/ecad/ring-route-i; B=$1; T=$2
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
PY=$REPO_ROOT/design/.venv/bin/python
F=$I/fab-$T; mkdir -p "$F/gerber" "$F/drill"
# the read-back finds the files by the prefix "ring": the board is exported from a copy named ring.kicad_pcb in lw/
cp "$B" $I/lw/ring.kicad_pcb; B0=$B; B=$I/lw/ring.kicad_pcb
nice -n 19 "$KC" pcb export gerbers --layers "F.Cu,In1.Cu,In2.Cu,B.Cu,Edge.Cuts" --no-protel-ext -o "$F/gerber/" "$B" > "$I/logs/fab-$T.log" 2>&1
nice -n 19 "$KC" pcb export drill --format excellon --excellon-separate-th -o "$F/drill/" "$B" >> "$I/logs/fab-$T.log" 2>&1
echo "export exit $?" >> "$I/logs/fab-$T.log"
cd $I/rb && RBFAB=$F RBOUT=$I/logs/p4p5-$T.json PYTHONDONTWRITEBYTECODE=1 nice -n 19 "$PY" -B $I/rb/p4p5.py > "$I/logs/p4p5-$T.log" 2>&1
echo "p4p5 exit $?" >> "$I/logs/p4p5-$T.log"
cd $I/pcb && PYTHONDONTWRITEBYTECODE=1 nice -n 19 $I/scripts/run_kipy.sh -B $I/rb/xcheck_clear.py "$B0" > "$I/logs/xcheck-$T.log" 2>&1
echo "xcheck exit $?" >> "$I/logs/xcheck-$T.log"
grep -h "P4.2 \|^A1 \|XC2 on L3\|XC1 on L3\|XL2 on L\|XL1 on L\|P5 XL1 ('\|P4.4\|exit" "$I/logs/p4p5-$T.log" | cut -c1-200; grep -v "Debug\|assert" "$I/logs/xcheck-$T.log"
