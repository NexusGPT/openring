#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# Round 2 rebuild of the case boards (netlist, footprints, placement, router, finish, models, fab, checks). Logs in evidence/. Needs about 40 minutes.
# The final delivered run used placement seed 116 (kept in evidence/kept/placement_pcb1_s116e.json) and router seed 1; to reproduce exactly, skip step 3 and
# start from that placement file.
H=$REPO_ROOT/design/ecad/case/pcb
K=$REPO_ROOT/design/ecad/ring/pcb/run_kipy.sh
export CASE_FINE=1 CASE_EXTEND=2.5
cd "$H" || exit 9
mkdir -p work
(cd .. && bash run_all.sh w5_rebuild) > evidence/run_boards_netlist.log 2>&1 || exit 1
$K make_footprints.py > evidence/run_boards_footprints.log 2>&1 || exit 2
PLACE_IC=0.7 PLACE_OUTW=3000 PLACE_EXTRA=0.1 PLACE_OVP=3000 PLACE_TAG=e $K place_pcb1.py 116 800000 > evidence/run_boards_place.log 2>&1 || exit 3
CASE_PLACEMENT=work/placement_pcb1_s116e.json CASE_TAG=_c1 $K build_boards.py unrouted > evidence/run_boards_unrouted.log 2>&1 || exit 4
$K route_io.py export work/case_main_unrouted_c1.kicad_pcb work/c1_in.txt > evidence/run_boards_export.log 2>&1 || exit 5
clang++ -O2 -std=c++17 -o grid_router grid_router.cpp > evidence/run_boards_clang.log 2>&1 || exit 6
VIACOST=600 HISTINC=12 PGROW=1.3 ./grid_router work/c1_in.txt work/c2_out_s1.txt 300 1 > evidence/run_boards_router.log 2>&1
./finish2.sh c1 work/c2_out_s1.txt > evidence/run_boards_finish2.log 2>&1 || exit 7
cp work/c1_final.kicad_pcb case_main.kicad_pcb && cp work/c1_final.kicad_pro case_main.kicad_pro
$K tune_usb.py case_main.kicad_pcb > evidence/run_boards_usb.log 2>&1
$K build_boards.py pcb2 > evidence/run_boards_pcb2.log 2>&1 || exit 9
$K add_models.py case_main.kicad_pcb > evidence/run_boards_models_main.log 2>&1
$K add_models.py case_pins.kicad_pcb > evidence/run_boards_models_pins.log 2>&1
./export_fab.sh main > evidence/run_boards_fab_main.log 2>&1
./export_fab.sh pins > evidence/run_boards_fab_pins.log 2>&1
python3 make_bom.py > evidence/run_boards_bom.log 2>&1
./run_broken_tests.sh > evidence/run_boards_check.log 2>&1
echo "run_boards done"
