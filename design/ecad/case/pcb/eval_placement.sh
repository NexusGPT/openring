#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# usage: eval_placement.sh <placement.json> <tag> [seconds]  builds the unrouted board for that placement, runs grid_router, prints the summary line (work/<tag>_*)
H=$REPO_ROOT/design/ecad/case/pcb
K=$REPO_ROOT/design/ecad/ring/pcb/run_kipy.sh
P=$1
T=$2
S=${3:-120}
cd "$H" || exit 9
CASE_PLACEMENT=$P CASE_TAG=_$T $K build_boards.py unrouted > evidence/eval_${T}_build.log 2>&1
GND_MODE=${GND_MODE:-skip} $K route_io.py export work/case_main_unrouted_$T.kicad_pcb work/${T}_in.txt > evidence/eval_${T}_export.log 2>&1
nice -n 5 ./grid_router work/${T}_in.txt work/${T}_out.txt $S 1 > evidence/eval_${T}_router.log 2>&1
echo "$T: $(tail -1 evidence/eval_${T}_router.log)"
grep DIAG evidence/eval_${T}_router.log | sort | uniq | head -12
