#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# attempt.sh tag base.kicad_pcb R x y NET sx sy layer : rip unlocked copper (not GND, RF, USB) within R of (x, y), route NET from (sx, sy) first,
# then route every open pair the rules check lists (3 passes), rules check after. Board: logs/s/<tag>.kicad_pcb. All KiCad Python runs via kp.sh.
H=$REPO_ROOT/design/ecad/ring-route-h; S=$H/logs/s; T=$1
$H/scripts/kp.sh "$2" $S/$T.kicad_pcb $H/scripts/ripall.py $3 $4 $5 > $H/logs/$T-rip.log 2>&1
$H/scripts/kp.sh $S/$T.kicad_pcb $S/$T.kicad_pcb $H/scripts/hand.py $6 $7 $8 $9 a a > $H/logs/$T-first.log 2>&1
for k in 1 2 3; do
  $H/scripts/drc.sh $S/$T.kicad_pcb $T-pass$k > $H/logs/$T-pass$k.out 2>&1
  J=$(python3 $H/scripts/jobs_from_drc.py $H/logs/drc-$T-pass$k.json ${SKIP:-none})
  echo "pass $k jobs: $J" >> $H/logs/$T-jobs.log
  [ -z "$J" ] && break
  $H/scripts/kp.sh $S/$T.kicad_pcb $S/$T.kicad_pcb $H/scripts/hand.py $J > $H/logs/$T-re$k.log 2>&1
done
$H/scripts/drc.sh $S/$T.kicad_pcb $T-final > $H/logs/$T-final.out 2>&1
grep -h "found\|FAILED\|removed" $H/logs/$T-rip.log $H/logs/$T-first.log $H/logs/$T-re*.log; head -2 $H/logs/$T-final.out
