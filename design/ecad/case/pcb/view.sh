#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# usage: view.sh <board.kicad_pcb> <out_prefix> <layers comma list> [dpi]   -> <out_prefix>.pdf and <out_prefix>.png (PDF via kicad-cli, PNG via pymupdf)
B=${1:?board}
O=${2:?out}
L=${3:?layers}
D=${4:-500}
/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli pcb export pdf --layers "$L" --include-border-title --black-and-white -o "$O.pdf" "$B" > "$O.pdf.log" 2>&1 || exit 1
$REPO_ROOT/design/ecad/case/pcb/evidence/py.sh -c "
import pymupdf,sys
d=pymupdf.open('$O.pdf')
pix=d[0].get_pixmap(dpi=$D)
pix.save('$O.png')
print(pix.width,pix.height)
"
