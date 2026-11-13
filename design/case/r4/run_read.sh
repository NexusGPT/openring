#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
# usage: run_read.sh <main.kicad_pcb> <pins.kicad_pcb> <outdir>   reads both boards with KiCad's Python (board_read.py) and exports their STEP (kicad-cli)
R4=$REPO_ROOT/design/case/r4
KIPY=$REPO_ROOT/design/ecad/ring/pcb/run_kipy.sh
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
O="$3"
mkdir -p "$O"
rc=0
for pair in "main:$1" "pins:$2"; do
  tag="${pair%%:*}"; b="${pair#*:}"
  "$KIPY" "$R4/board_read.py" "$b" "$O/$tag.json" > "$O/read_$tag.log" 2>&1 || rc=1
  "$KC" pcb export step --no-dnp --subst-models --force -o "$O/$tag.step" "$b" > "$O/step_$tag.log" 2>&1 || rc=1
done
exit $rc
