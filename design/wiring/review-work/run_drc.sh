#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
# Runs KiCad's rules check on each of the 17 boards, one at a time, from the board's own folder.
# Output: review-work/drc/<name>.json and <name>.log; done file drc/ALL.exit
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
R=$REPO_ROOT
O=$R/design/wiring/review-work/drc
mkdir -p "$O"
BOARDS="$R/design/ecad/ring/pcb/ring.kicad_pcb $R/design/ecad/case/pcb/case_main.kicad_pcb $R/design/ecad/case/pcb/case_pins.kicad_pcb"
for f in 1 2; do for s in 7 8 9 10 11 12 13; do BOARDS="$BOARDS $R/design/ecad/band/flex$f-us$s.kicad_pcb"; done; done
for b in $BOARDS; do
  n=$(basename "$b" .kicad_pcb)
  d=$(dirname "$b")
  cd "$d" && date '+start %H:%M:%S' > "$O/$n.log" 2>&1 && nice -n 19 "$CLI" pcb drc --severity-all --all-track-errors --format json -o "$O/$n.json" "$(basename "$b")" >> "$O/$n.log" 2>&1
  echo "exit $?" >> "$O/$n.log"
  date '+end %H:%M:%S' >> "$O/$n.log" 2>&1
done
echo done > "$O/ALL.exit"
