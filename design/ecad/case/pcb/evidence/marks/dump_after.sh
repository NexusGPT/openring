#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../../.." && pwd)"  # the repository root, found from this script
# pads, tracks, vias, zones, outline of both boards after the change, compared with the dumps made before (same dump_pins.py)
P=$REPO_ROOT/design/ecad/case/pcb
E=$P/evidence/marks
RK=$REPO_ROOT/design/ecad/ring/pcb/run_kipy.sh
bash $RK $E/dump_pins.py $P/case_pins.kicad_pcb > $E/pins_dump_after.log 2>&1
bash $RK $E/dump_pins.py $P/case_main.kicad_pcb > $E/main_dump_after.log 2>&1
for T in pins main; do
  grep -E '^(PAD|TRK|ZONE)' $E/${T}_dump_before.log | sort > $E/${T}_cu_before.txt
  grep -E '^(PAD|TRK|ZONE)' $E/${T}_dump_after.log | sort > $E/${T}_cu_after.txt
  if cmp -s $E/${T}_cu_before.txt $E/${T}_cu_after.txt; then r=IDENTICAL; else r=DIFFERENT; fi
  echo "$T: pads $(grep -c '^PAD' $E/${T}_cu_before.txt) -> $(grep -c '^PAD' $E/${T}_cu_after.txt), tracks+vias $(grep -c '^TRK' $E/${T}_cu_before.txt) -> $(grep -c '^TRK' $E/${T}_cu_after.txt), zones $(grep -c '^ZONE' $E/${T}_cu_before.txt) -> $(grep -c '^ZONE' $E/${T}_cu_after.txt), pad/track/zone lines $r; Edge.Cuts shapes $(grep -c 'Edge.Cuts' $E/${T}_dump_before.log) -> $(grep -c 'Edge.Cuts' $E/${T}_dump_after.log); drawings after: $(grep '^DRAW' $E/${T}_dump_after.log | sort | uniq -c | tr -s ' ' | tr '\n' ',')"
done
