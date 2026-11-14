#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# place.sh tag base.kicad_pcb REF [max] : spot list for REF on the base board (freespots.py, TOP=max, env NEAR passes through), then try_spots.sh
H=$REPO_ROOT/design/ecad/ring-route-h; T=$1; MAX=${4:-30}
date > $H/logs/$T-start.txt
cd $H/scripts && TOP=$MAX nice -n 19 ./run_kipy.sh $H/scripts/freespots.py $2 $3 > $H/logs/$T-spots.log 2>&1
$H/scripts/try_spots.sh $T $2 $3 $H/logs/$T-spots.log $MAX > $H/logs/$T-place.out 2>&1
date > $H/logs/$T-end.txt; echo done > $H/logs/$T.exit
