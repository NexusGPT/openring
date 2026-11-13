#!/bin/zsh
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# Runs kicad-cli DRC on the 17 boards, one at a time, reports into W/drc.
W=$REPO_ROOT/design/wiring/review4-work
R=$REPO_ROOT/design/ecad
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
boards=("$R/ring/pcb/ring.kicad_pcb")
for f in 1 2; do for s in 7 8 9 10 11 12 13; do boards+=("$R/band/flex$f-us$s.kicad_pcb"); done; done
boards+=("$R/case/pcb/case_main.kicad_pcb" "$R/case/pcb/case_pins.kicad_pcb")
for b in $boards; do
  n=$(basename "$b" .kicad_pcb)
  echo "START $n $(date +%H:%M:%S)"
  nice -n 19 "$CLI" pcb drc --severity-all --all-track-errors -o "$W/drc/$n.rpt" "$b" > "$W/drc/$n.cli.log" 2>&1
  echo "EXIT $n $?"
done
echo "ALLDONE $(date +%H:%M:%S)"
