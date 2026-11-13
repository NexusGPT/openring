#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../../../.." && pwd)"  # the repository root, found from this script
# make_board.sh: rebuilds ring.kicad_pcb from the netlist, the libraries and the placement table, in one command.
#   1 build_board.py   board, stack, outline, footprints, placement, rules, rule areas, ground zones
#   2 route_fixed.py   scripted copper of plan step g.5 (escapes, antenna line, USB pair, crystals, tail exits, ground stacks), locked
#   3 finish_route.py  routes every other connection (grid maze router with rip-up, the board's own rules), refills the zones
#   4 kicad-cli drc    the rules check, report drc-report.txt
#   5 check_board.py   the board checks (parts, pad nets, courtyards, outline, keep-outs, table positions, escapes, rules check)
# The automatic router of plan step g.7 (Freerouting on the build server) was run on this board family as well; its best
# session left more open connections than step 3 alone (board-notes.md, point e), so the rebuild does not need the server.
# Logs: build-logs/ beside this script. Exit code: that of check_board.py.
P=$REPO_ROOT/design/ecad/ring/pcb
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
L=$P/build-logs
mkdir -p "$L" || exit 9
cd "$P" || exit 9
"$P/run_kipy.sh" "$P/build_board.py" > "$L/1_build_board.log" 2>&1 || { echo "build_board failed"; exit 1; }
"$P/run_kipy.sh" "$P/route_fixed.py" > "$L/2_route_fixed.log" 2>&1 || { echo "route_fixed failed"; exit 2; }
"$P/run_kipy.sh" "$P/finish_route.py" "$P/ring.kicad_pcb" "$P/ring.kicad_pcb" 4 > "$L/3_finish_route.log" 2>&1 || { echo "finish_route failed"; exit 3; }
"$KC" pcb drc --severity-all --all-track-errors -o "$P/drc-report.txt" "$P/ring.kicad_pcb" > "$L/4_drc.log" 2>&1
tail -2 "$L/4_drc.log"
"$P/run_kipy.sh" "$P/check_board.py" > "$L/5_check_board.log" 2>&1
rc=$?
tail -1 "$L/5_check_board.log"
exit $rc
