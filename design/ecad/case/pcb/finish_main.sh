#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# usage: finish_main.sh <tag> <router out file>   tag = the eval tag of the unrouted board (work/case_main_unrouted_<tag>.kicad_pcb)
# Imports the grid_router result, runs the ground phase and the USB length tuning, writes pcb/case_main.kicad_pcb (+ .kicad_pro) and pcb/case_pins.kicad_pcb.
H=$REPO_ROOT/design/ecad/case/pcb
K=$REPO_ROOT/design/ecad/ring/pcb/run_kipy.sh
T=${1:?tag}
OUT=${2:?router out}
cd "$H" || exit 9
$K route_io.py import work/case_main_unrouted_$T.kicad_pcb $OUT work/${T}_p1.kicad_pcb > evidence/finish_${T}_import.log 2>&1 || exit 1
$K gnd_phase.py work/${T}_p1.kicad_pcb work/${T}_full.kicad_pcb > evidence/finish_${T}_gnd.log 2>&1 || exit 2
cp work/${T}_full.kicad_pcb case_main.kicad_pcb
cp work/${T}_full.kicad_pro case_main.kicad_pro
$K tune_usb.py case_main.kicad_pcb > evidence/finish_${T}_usb.log 2>&1 || exit 3
$K build_boards.py pcb2 > evidence/finish_${T}_pcb2.log 2>&1 || exit 4
echo finished
