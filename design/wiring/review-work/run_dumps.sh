#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
# Pad dump with copper clusters for each of the 17 boards, one at a time. Done file: pads/ALL.exit
R=$REPO_ROOT
W=$R/design/wiring/review-work
K=$R/design/ecad/ring/pcb/run_kipy.sh
BOARDS="$R/design/ecad/case/pcb/case_main.kicad_pcb $R/design/ecad/case/pcb/case_pins.kicad_pcb"
for f in 1 2; do for s in 7 8 9 10 11 12 13; do BOARDS="$BOARDS $R/design/ecad/band/flex$f-us$s.kicad_pcb"; done; done
BOARDS="$BOARDS $R/design/ecad/ring/pcb/ring.kicad_pcb"
for b in $BOARDS; do
  n=$(basename "$b" .kicad_pcb)
  date '+start %H:%M:%S' > "$W/pads/$n.log" 2>&1
  cd "$W" && nice -n 19 bash "$K" "$W/dump_pads.py" "$b" "$W/pads/$n.csv" >> "$W/pads/$n.log" 2>&1
  echo "exit $?" >> "$W/pads/$n.log"
  date '+end %H:%M:%S' >> "$W/pads/$n.log" 2>&1
done
echo done > "$W/pads/ALL.exit"
