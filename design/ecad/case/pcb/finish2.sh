#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# usage: finish2.sh <tag> <router out>  -> work/<tag>_final.kicad_pcb : import, declash (drop the nets the router could not separate), ground phase
H=$REPO_ROOT/design/ecad/case/pcb
K=$REPO_ROOT/design/ecad/ring/pcb/run_kipy.sh
T=${1:?tag}
OUT=${2:?out}
cd "$H" || exit 9
cp work/case_main_unrouted_$T.kicad_pro work/${T}_p1.kicad_pro
$K route_io.py import work/case_main_unrouted_$T.kicad_pcb $OUT work/${T}_p1.kicad_pcb > evidence/finish2_${T}_import.log 2>&1 || exit 1
$K declash.py work/${T}_p1.kicad_pcb work/${T}_p2.kicad_pcb > evidence/finish2_${T}_declash.log 2>&1 || exit 2
$K gnd_phase.py work/${T}_p2.kicad_pcb work/${T}_final.kicad_pcb > evidence/finish2_${T}_gnd.log 2>&1 || exit 3
echo "finish2 $T done"
tail -3 evidence/finish2_${T}_declash.log
grep '^round\|^saved' evidence/finish2_${T}_gnd.log | tail -3
