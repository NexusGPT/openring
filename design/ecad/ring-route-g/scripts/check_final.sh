#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# check_final.sh : bar items 1 to 4 as a reader runs them from ROOT (paths below are relative to ROOT).
# Writes logs/final-drc.log (+ final-drc.rpt), logs/final-compare.log, logs/final-broken-R65.log, logs/final-broken-U5.log
ROOT=$REPO_ROOT
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
cd "$ROOT" && date > design/ecad/ring-route-g/logs/final-start.txt
# bar 1: rules check with the base's own rules (pcb/ring-thin-a1.kicad_dru and .kicad_pro are byte copies of the base's)
cd "$ROOT" && nice -n 19 "$KC" pcb drc --severity-all --all-track-errors -o design/ecad/ring-route-g/logs/final-drc.rpt design/ecad/ring-route-g/pcb/ring-thin-a1.kicad_pcb > design/ecad/ring-route-g/logs/final-drc.log 2>&1
echo "drc exit $?" >> "$ROOT/design/ecad/ring-route-g/logs/final-drc.log"
# bars 2 and 3: compare script, final board against the base
cd "$ROOT" && nice -n 19 design/ecad/ring/pcb/run_kipy.sh design/ecad/ring-route-g/scripts/compare.py design/ecad/ring/pcb/ring.kicad_pcb design/ecad/ring-route-g/pcb/ring-thin-a1.kicad_pcb design/ecad/ring/pcb/ring.kicad_dru design/ecad/ring-route-g/pcb/ring-thin-a1.kicad_dru > design/ecad/ring-route-g/logs/final-compare.log 2>&1
echo "compare exit $?" >> "$ROOT/design/ecad/ring-route-g/logs/final-compare.log"
# bar 4: broken copies (R65 moved 0.05 mm in X; U5 moved 0.05 mm in Y toward J1)
for k in R65 U5; do
  cd "$ROOT" && nice -n 19 design/ecad/ring/pcb/run_kipy.sh design/ecad/ring-route-g/scripts/compare.py design/ecad/ring/pcb/ring.kicad_pcb design/ecad/ring-route-g/broken/move-$k.kicad_pcb design/ecad/ring/pcb/ring.kicad_dru design/ecad/ring-route-g/pcb/ring-thin-a1.kicad_dru > design/ecad/ring-route-g/logs/final-broken-$k.log 2>&1
  echo "compare exit $?" >> "$ROOT/design/ecad/ring-route-g/logs/final-broken-$k.log"
done
cd "$ROOT" && date > design/ecad/ring-route-g/logs/final-end.txt
cd "$ROOT/design/ecad/ring-route-g/logs" && grep -h "Found\|drc exit" final-drc.log && grep -h "^CHECK\|^RESULT\|exit" final-compare.log final-broken-R65.log final-broken-U5.log | grep -v "CHECK 2a"
