#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
R=$REPO_ROOT
W=$R/design/wiring/review2-work
for b in $R/design/ecad/ring/pcb/ring.kicad_pcb $R/design/ecad/case/pcb/case_main.kicad_pcb $R/design/ecad/case/pcb/case_pins.kicad_pcb $(ls $R/design/ecad/band/flex[12]-us*.kicad_pcb); do
  n=$(basename $b .kicad_pcb)
  ( cd "$(dirname $b)" && nice -n 19 $R/design/ecad/ring/pcb/run_kipy.sh $W/scripts/dump_pads.py "$b" "$W/pads/$n.csv" ); echo "$n exit=$?"
done
