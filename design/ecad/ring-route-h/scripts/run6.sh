#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# run6.sh : from h08, move R72 out of the box X 6.7..7.6, Y -2.8..-1.5 (spots nearest U2 E1), then C7 with its DECA pad within 3.0 mm of U1 A8
H=$REPO_ROOT/design/ecad/ring-route-h; S=$H/logs/s
echo "run 6 (tag v) from h08 at $(date)" >> $H/logs/chain.log
cd $H/scripts && EXCL=6.7,-2.8,7.6,-1.5 BALL=7.620,-1.257 SPREAD=0.25 TOP=15 nice -n 19 ./run_kipy.sh $H/scripts/freespots.py $H/steps/h08-c7.kicad_pcb R72 > $H/logs/v-r72-spots.log 2>&1
$H/scripts/try_spots.sh v-r72 $H/steps/h08-c7.kicad_pcb R72 $H/logs/v-r72-spots.log 15 > $H/logs/v-r72-place.out 2>&1
if [ -f $S/v-r72-ok.kicad_pcb ]; then
  echo "R72 moved: logs/s/v-r72-ok.kicad_pcb" >> $H/logs/chain.log
  cd $H/scripts && NEARPAD=4.650,-0.978,3.0 TOP=20 nice -n 19 ./run_kipy.sh $H/scripts/freespots.py $S/v-r72-ok.kicad_pcb C7 > $H/logs/v-c7-spots.log 2>&1
  $H/scripts/try_spots.sh v-c7 $S/v-r72-ok.kicad_pcb C7 $H/logs/v-c7-spots.log 20 > $H/logs/v-c7-place.out 2>&1
  if [ -f $S/v-c7-ok.kicad_pcb ]; then cp $S/v-c7-ok.kicad_pcb $H/steps/h09-c7near.kicad_pcb; echo "C7 within 3.0: steps/h09-c7near.kicad_pcb" >> $H/logs/chain.log; else echo "C7 within 3.0 not closed (logs/v-c7-summary.log)" >> $H/logs/chain.log; fi
else echo "R72 not moved (logs/v-r72-summary.log)" >> $H/logs/chain.log; fi
echo done > $H/logs/run6.exit
