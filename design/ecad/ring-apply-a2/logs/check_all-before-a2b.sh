#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# check_all.sh : bars 1 to 5 of the apply-A2 brief, run from ROOT. Logs in design/ecad/ring-apply-a2/logs/all-*.log
# 1 pcb/ring.kicad_pcb byte-identical to route-h's A2 board; rules check 0 / 0
# 2 check_board.py, check_footprints.py, check_netlist.py pass
# 3 placement table equals the board (read-back), and a broken row fails
# 4 the six design checks of step 5
# 5 fallback-417 holds the old board; rules check there 0 / 0
ROOT=$REPO_ROOT
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
W=design/ecad/ring-apply-a2; P=design/ecad/ring/pcb; L=$W/logs
cd "$ROOT" && date > $L/all-start.txt
# bar 1
cd "$ROOT" && cmp design/ecad/ring-route-h/pcb/ring-thin-a2.kicad_pcb $P/ring.kicad_pcb > $L/all-1-cmp.log 2>&1; echo "cmp exit $?" >> "$ROOT/$L/all-1-cmp.log"
cd "$ROOT/$P" && nice -n 19 "$KC" pcb drc --severity-all --all-track-errors -o drc-report.txt ring.kicad_pcb > "$ROOT/$L/all-1-drc.log" 2>&1; echo "drc exit $?" >> "$ROOT/$L/all-1-drc.log"
# bar 2
mkdir -p "$ROOT/$W/cbout"
cd "$ROOT/$P" && CHECK_BOARD_OUT="$ROOT/$W/cbout" nice -n 19 ./run_kipy.sh check_board.py > "$ROOT/$L/all-2-check_board.log" 2>&1; echo "check_board exit $?" >> "$ROOT/$L/all-2-check_board.log"
cd "$ROOT/$P" && nice -n 19 ./run_kipy.sh check_footprints.py > "$ROOT/$L/all-2-check_footprints.log" 2>&1; echo "check_footprints exit $?" >> "$ROOT/$L/all-2-check_footprints.log"
cd "$ROOT/design/ecad/ring" && nice -n 19 "$ROOT/design/.venv/bin/python" -B check_netlist.py > "$ROOT/$L/all-2-check_netlist.log" 2>&1; echo "check_netlist exit $?" >> "$ROOT/$L/all-2-check_netlist.log"
# bar 3
cd "$ROOT/$P" && nice -n 19 ./run_kipy.sh "$ROOT/$W/scripts/readback_placement.py" ring.kicad_pcb placement-final.csv > "$ROOT/$L/all-3-readback.log" 2>&1; echo "readback exit $?" >> "$ROOT/$L/all-3-readback.log"
cd "$ROOT/$P" && nice -n 19 ./run_kipy.sh "$ROOT/$W/scripts/readback_placement.py" ring.kicad_pcb "$ROOT/$L/placement-broken-C7.csv" > "$ROOT/$L/all-3-readback-broken.log" 2>&1; echo "readback exit $?" >> "$ROOT/$L/all-3-readback-broken.log"
# bar 4
cd "$ROOT" && /bin/bash $W/scripts/six.sh all4 > $L/all-4-six.log 2>&1
# bar 5
cd "$ROOT/$P/fallback-417" && nice -n 19 "$KC" pcb drc --severity-all --all-track-errors -o "$ROOT/$L/all-5-fallback-drc.rpt" ring.kicad_pcb > "$ROOT/$L/all-5-fallback-drc.log" 2>&1; echo "drc exit $?" >> "$ROOT/$L/all-5-fallback-drc.log"
cd "$ROOT/$P/fallback-417" && H=$(shasum -a 256 ring.kicad_pcb | cut -d" " -f1) && { grep -q "$H  ring.kicad_pcb" "$ROOT/$L/fallback-sha-src.log" && echo "fallback ring.kicad_pcb sha256 $H equals the board folder's ring.kicad_pcb before A2 (logs/fallback-sha-src.log)" || echo "FAIL fallback ring.kicad_pcb sha256 $H not the recorded old board"; } > "$ROOT/$L/all-5-fallback-sha.log" 2>&1
cd "$ROOT" && date > $L/all-end.txt
cd "$ROOT/$L" && echo "bar 1:" && tail -1 all-1-cmp.log && grep "Found\|drc exit" all-1-drc.log && echo "bar 2:" && tail -2 all-2-check_board.log && tail -2 all-2-check_footprints.log && tail -2 all-2-check_netlist.log && echo "bar 3:" && tail -2 all-3-readback.log && tail -2 all-3-readback-broken.log && echo "bar 4:" && cat all-4-six.log && echo "bar 5:" && grep "Found\|drc exit" all-5-fallback-drc.log && cat all-5-fallback-sha.log
