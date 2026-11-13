#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# usage: eval_r2.sh <placement.json> <tag> [seconds] [seed]   round 2: unrouted board (fine rules, planes), router input, grid_router (VIACOST 600)
H=$REPO_ROOT/design/ecad/case/pcb
K=$REPO_ROOT/design/ecad/ring/pcb/run_kipy.sh
export CASE_FINE=1
export CASE_EXTEND=${CASE_EXTEND:-2.5}
cd "$H" || exit 9
CASE_PLACEMENT=$1 CASE_TAG=_$2 $K build_boards.py unrouted > evidence/r2e_$2_build.log 2>&1
$K route_io.py export work/case_main_unrouted_$2.kicad_pcb work/$2_in.txt > evidence/r2e_$2_export.log 2>&1
VIACOST=600 HISTINC=12 PGROW=1.3 nice -n 5 ./grid_router work/$2_in.txt work/$2_out.txt ${3:-300} ${4:-1} > evidence/r2e_$2_router.log 2>&1
echo "$2: $(tail -1 evidence/r2e_$2_router.log)"
