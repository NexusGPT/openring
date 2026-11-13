#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# usage: export_fab.sh <main|pins>   writes fab/<tag>/ : Gerber, drill, position, copper-layer PDFs, STEP (kicad-cli 10.0.8), logs in fab/<tag>/export.log
H=$REPO_ROOT/design/ecad/case/pcb
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
T=${1:?main or pins}
B=$H/case_$T.kicad_pcb
O=$H/fab/case_$T
rm -rf "$O" && mkdir -p "$O/gerber" "$O/pdf" || exit 9
L="$O/export.log"
if [ "$T" = main ]; then CU="F.Cu,In1.Cu,In2.Cu,B.Cu"; else CU="F.Cu,B.Cu"; fi
LAYERS="$CU,F.Mask,B.Mask,F.Paste,B.Paste,F.SilkS,B.SilkS,Edge.Cuts"
$KC pcb export gerbers --layers "$LAYERS" --subtract-soldermask --no-protel-ext -o "$O/gerber/" "$B" > "$O/gerbers.log" 2>&1; echo "gerbers exit $?" >> "$L"
$KC pcb export drill --format excellon --drill-origin absolute --excellon-units mm --generate-map --map-format gerberx2 --excellon-separate-th -o "$O/gerber/" "$B" > "$O/drill.log" 2>&1; echo "drill exit $?" >> "$L"
$KC pcb export pos --format csv --units mm --side both --use-drill-file-origin -o "$O/case_${T}_position.csv" "$B" > "$O/pos.log" 2>&1; echo "pos exit $?" >> "$L"
for LY in ${CU//,/ }; do
  N=${LY//./_}
  $KC pcb export pdf --layers "$LY,Edge.Cuts" --black-and-white -o "$O/pdf/case_${T}_$N.pdf" "$B" > "$O/pdf/$N.log" 2>&1; echo "pdf $LY exit $?" >> "$L"
done
$KC pcb export step --no-dnp --subst-models -o "$O/case_${T}.step" "$B" > "$O/step.log" 2>&1; echo "step exit $?" >> "$L"
cat "$L"
