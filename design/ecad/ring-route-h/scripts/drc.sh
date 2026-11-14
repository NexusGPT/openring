#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# drc.sh board tag : copy the board to pcb/work.kicad_pcb (beside work.kicad_pro and work.kicad_dru, byte copies of the base's
# ring.kicad_pro and ring.kicad_dru, and OpenRing.pretty), run the project's rules check with the flags of
# design/ecad/ring/pcb/board-notes-r3.md step 2, JSON + short listing in logs/
G=$REPO_ROOT/design/ecad/ring-route-h
KC=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
cp "$1" $G/pcb/work.kicad_pcb
nice -n 19 "$KC" pcb drc --severity-all --all-track-errors --format json -o "$G/logs/drc-$2.json" $G/pcb/work.kicad_pcb > "$G/logs/drc-$2.log" 2>&1
echo "exit $?" >> "$G/logs/drc-$2.log"
python3 -c "
import json;d=json.load(open('$G/logs/drc-$2.json'))
for k in ('violations','unconnected_items'):
  for v in d[k]: print(k[:5],v['type'],'|',' || '.join('%s @(%.3f,%.3f)'%(i['description'][:70],i['pos']['x']-100,i['pos']['y']-100) for i in v['items']))
" > "$G/logs/drc-$2.list" 2>&1
grep "Found" "$G/logs/drc-$2.log"; cat "$G/logs/drc-$2.list"
