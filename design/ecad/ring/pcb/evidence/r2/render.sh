#!/bin/bash
# render.sh board.kicad_pcb out_prefix layer [layer...]: one PNG per copper layer (tracks, pads, vias, courtyards), no zones
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
B=$1; O=$2; shift 2
for L in "$@"; do
  "$KC" pcb export svg --layers "$L,F.Courtyard,Edge.Cuts" --mode-single --exclude-drawing-sheet --fit-page-to-board -o "$O-$L.svg" "$B" > "$O-render.log" 2>&1 && rsvg-convert -w 2600 -b white "$O-$L.svg" -o "$O-$L.png" >> "$O-render.log" 2>&1
  rm -f "$O-$L.svg"
done
