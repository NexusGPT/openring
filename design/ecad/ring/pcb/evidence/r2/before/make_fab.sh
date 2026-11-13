#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../../../.." && pwd)"  # the repository root, found from this script
# make_fab.sh: writes the fabrication files of ring.kicad_pcb into fab/ (Gerber per layer, drill per via span, IPC-D-356,
# position file, parts list with order codes, PDF per copper layer, stack drawing with the order notes, board STEP).
# Run only on a fully routed board (the caller checks the rules check first).
P=$REPO_ROOT/design/ecad/ring/pcb
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
B=$P/ring.kicad_pcb
F=$P/fab
mkdir -p "$F/gerber" "$F/drill" "$F/pdf" || exit 9
"$KC" pcb export gerbers --layers "F.Cu,In1.Cu,In2.Cu,B.Cu,F.Mask,B.Mask,F.Paste,B.Paste,F.SilkS,B.SilkS,Edge.Cuts" --no-protel-ext -o "$F/gerber/" "$B" || exit 1
"$KC" pcb export drill --format excellon --excellon-separate-th --generate-map --map-format pdf -o "$F/drill/" "$B" || exit 2
"$KC" pcb export ipcd356 -o "$F/ring.ipc356" "$B" || exit 3
"$KC" pcb export pos --format csv --units mm --side both --exclude-dnp -o "$F/ring-pos.csv" "$B" || exit 4
for L in F.Cu In1.Cu In2.Cu B.Cu; do
  "$KC" pcb export pdf --layers "$L,Edge.Cuts" --mode-single -o "$F/pdf/ring-$L.pdf" "$B" || exit 5
done
"$KC" pcb export step --subst-models --include-tracks --include-zones --force -o "$F/ring.step" "$B" || exit 6
PY=$REPO_ROOT/design/.venv/bin/python
"$PY" "$P/make_fab_docs.py" || exit 7
du -sh "$F"
