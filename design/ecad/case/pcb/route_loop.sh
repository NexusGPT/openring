#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# usage: route_loop.sh <dsn name> <first ses name> <prefix> <max rounds>
# Continues Freerouting rounds (route_cont.sh) from <first ses> until the router reports 0 unrouted, or 2 rounds in a row do not improve, or the round limit.
H=$REPO_ROOT/design/ecad/case/pcb
D=$1
PREV=$2
PFX=$3
MAX=${4:-8}
BEST=999
STALL=0
for r in $(seq 1 $MAX); do
  NAME=${PFX}$r
  $H/route_cont.sh $D $PREV $NAME 100 > $H/evidence/route_loop_$NAME.log 2>&1
  N=$(grep -o 'final score: [0-9.]* ([0-9]* unrouted' $H/work/$NAME.route.log | tail -1 | grep -o '[0-9]* unrouted' | grep -o '^[0-9]*')
  echo "round $r $NAME unrouted ${N:-unknown}" >> $H/evidence/route_loop_summary.log
  if [ -z "$N" ]; then break; fi
  if [ "$N" -eq 0 ]; then break; fi
  if [ "$N" -lt "$BEST" ]; then BEST=$N; STALL=0; else STALL=$((STALL+1)); fi
  if [ $STALL -ge 2 ]; then break; fi
  PREV=$NAME
done
echo "loop done best $BEST" >> $H/evidence/route_loop_summary.log
