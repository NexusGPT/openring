#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# run4.sh : C5 within 3.0 mm (pad) of U1 A4 from h05, then FB1 and C7 by chain.sh (tag s)
H=$REPO_ROOT/design/ecad/ring-route-h
echo "run 4 (tag s) from h05 at $(date)" >> $H/logs/chain.log
NEARPAD=3.347,-0.978,3.0 $H/scripts/place.sh s-c5 $H/steps/h05-c14.kicad_pcb C5 20
CUR=$H/steps/h05-c14.kicad_pcb; N=6
if [ -f $H/logs/s/s-c5-ok.kicad_pcb ]; then cp $H/logs/s/s-c5-ok.kicad_pcb $H/steps/h06-c5.kicad_pcb; CUR=$H/steps/h06-c5.kicad_pcb; N=7; echo "C5 placed: $CUR" >> $H/logs/chain.log; else echo "C5 not placed near A4 (logs/s-c5-summary.log)" >> $H/logs/chain.log; fi
TAGP=s $H/scripts/chain.sh $CUR $N FB1 C7
echo done > $H/logs/run4.exit
