#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# lines.sh tag fabfolder board : the controlled-line read-back of board-notes-r4.md (copy of ring-lines/rb in ring-apply-a2/rb, the ring's
# own netlist) on the Gerber and drill files of fabfolder, then the pcbnew clearance cross-check on board. Logs: logs/p4p5-<tag>.log, logs/xcheck-<tag>.log
W=$REPO_ROOT/design/ecad/ring-apply-a2; T=$1; F=$2; B=$3
PY=$REPO_ROOT/design/.venv/bin/python
date > $W/logs/lines-$T-start.txt
cd $W/rb && RBFAB=$F RBOUT=$W/logs/p4p5-$T.json PYTHONDONTWRITEBYTECODE=1 nice -n 19 "$PY" -B $W/rb/p4p5.py > "$W/logs/p4p5-$T.log" 2>&1
echo "p4p5 exit $?" >> "$W/logs/p4p5-$T.log"
cd $REPO_ROOT/design/ecad/ring/pcb && PYTHONDONTWRITEBYTECODE=1 nice -n 19 ./run_kipy.sh -B $W/rb/xcheck_clear.py "$B" > "$W/logs/xcheck-$T.log" 2>&1
echo "xcheck exit $?" >> "$W/logs/xcheck-$T.log"
date > $W/logs/lines-$T-end.txt
