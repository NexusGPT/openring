#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# check_final.sh : bar items 1 to 4 of board A2, run from ROOT (paths below are relative to ROOT).
# Writes logs/final-drc.log (+ .rpt), logs/final-compare.log, logs/final-broken-C7.log
ROOT=$REPO_ROOT
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
L=design/ecad/ring-route-h/logs
cd "$ROOT" && date > $L/final-start.txt
# bar 1: rules check; pcb/ring-thin-a2.kicad_pro and .kicad_dru beside the board are byte copies of A1's
cd "$ROOT" && nice -n 19 "$KC" pcb drc --severity-all --all-track-errors -o $L/final-drc.rpt design/ecad/ring-route-h/pcb/ring-thin-a2.kicad_pcb > $L/final-drc.log 2>&1
echo "drc exit $?" >> "$ROOT/$L/final-drc.log"
# bars 2 and 3: compare2.py, A2 against A1
cd "$ROOT" && nice -n 19 design/ecad/ring/pcb/run_kipy.sh design/ecad/ring-route-h/scripts/compare2.py design/ecad/ring-route-g/pcb/ring-thin-a1.kicad_pcb design/ecad/ring-route-h/pcb/ring-thin-a2.kicad_pcb design/ecad/ring-route-g/pcb/ring-thin-a1.kicad_dru design/ecad/ring-route-h/pcb/ring-thin-a2.kicad_dru > $L/final-compare.log 2>&1
echo "compare exit $?" >> "$ROOT/$L/final-compare.log"
# bar 4: broken copy, C7 left on the screen face as on A1 (broken/c7-on-screen-face.kicad_pcb)
cd "$ROOT" && nice -n 19 design/ecad/ring/pcb/run_kipy.sh design/ecad/ring-route-h/scripts/compare2.py design/ecad/ring-route-g/pcb/ring-thin-a1.kicad_pcb design/ecad/ring-route-h/broken/c7-on-screen-face.kicad_pcb design/ecad/ring-route-g/pcb/ring-thin-a1.kicad_dru design/ecad/ring-route-h/pcb/ring-thin-a2.kicad_dru > $L/final-broken-C7.log 2>&1
echo "compare exit $?" >> "$ROOT/$L/final-broken-C7.log"
cd "$ROOT" && date > $L/final-end.txt
cd "$ROOT/$L" && grep -h "Found\|drc exit" final-drc.log && grep -h "^CHECK\|^RESULT\|exit" final-compare.log final-broken-C7.log
