#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# clean.sh board tag : up to 25 rounds of (rules check; delete what it calls dangling, not GND/RF/USB, rmdangle2.py) until nothing dangles
H=$REPO_ROOT/design/ecad/ring-route-i; B=$1; T=$2
for r in $(seq 1 25); do
  $H/scripts/drc.sh $B $T-cl > $H/logs/$T-cl.out 2>&1
  grep -q "dangling" $H/logs/drc-$T-cl.list || break
  $H/scripts/kp.sh $B $B $H/scripts/rmdangle2.py $H/logs/drc-$T-cl.json >> $H/logs/$T-clean.log 2>&1
done
echo "clean rounds $r" >> $H/logs/$T-clean.log
