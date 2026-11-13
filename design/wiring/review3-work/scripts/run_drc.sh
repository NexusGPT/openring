#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# review 3: KiCad DRC on all 17 boards, each inside its own folder, one at a time, reports into review3-work/drc
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
R=$REPO_ROOT
W=$R/design/wiring/review3-work/drc
git -C "$R" status --short --untracked-files=all -- design/ecad > "$W/gitstatus-before.log" 2>&1
date "+start %H:%M:%S"
for b in $R/design/ecad/ring/pcb/ring.kicad_pcb $R/design/ecad/case/pcb/case_main.kicad_pcb $R/design/ecad/case/pcb/case_pins.kicad_pcb $(ls $R/design/ecad/band/flex[12]-us*.kicad_pcb); do
  n=$(basename $b .kicad_pcb)
  ( cd "$(dirname $b)" && nice -n 19 "$K" pcb drc --severity-all --all-track-errors -o "$W/$n.rpt" "$(basename $b)" > "$W/$n.log" 2>&1 ); echo "$n exit=$?"
done
git -C "$R" status --short --untracked-files=all -- design/ecad > "$W/gitstatus-after.log" 2>&1
date "+end %H:%M:%S"
touch "$W/DONE"
