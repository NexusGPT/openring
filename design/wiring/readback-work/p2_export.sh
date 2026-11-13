#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
# p2_export.sh <name>: exports Gerber, drill and IPC-D-356 of $W/p2/<name>/ring.kicad_pcb with the options of ring/pcb/make_fab.sh
W=$REPO_ROOT/design/wiring/readback-work
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
N=$1
B=$W/p2/$N/ring.kicad_pcb
F=$W/p2/$N/fab
mkdir -p "$F/gerber" "$F/drill" || exit 9
"$KC" pcb export gerbers --layers "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.Paste,B.Paste,F.SilkS,B.SilkS,Edge.Cuts" --no-protel-ext -o "$F/gerber/" "$B" || exit 1
"$KC" pcb export drill --format excellon --excellon-separate-th --generate-map --map-format pdf --generate-report --report-path "$F/drill/ring-drill-report.txt" -o "$F/drill/" "$B" || exit 2
"$KC" pcb export ipcd356 -o "$F/ring.ipc356" "$B" || exit 3
echo "EXPORT_DONE $N"
