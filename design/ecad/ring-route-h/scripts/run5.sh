#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# run5.sh : from h06, C5 at the free spots nearest U1 A4, then C7 at the free spots nearest U1 A8 (spots spread 0.25 mm, 15 each)
H=$REPO_ROOT/design/ecad/ring-route-h
echo "run 5 (tag ${TAGP:-t}) from h06 at $(date)" >> $H/logs/chain.log
CUR=$H/steps/h06-fb1.kicad_pcb; N=7
for spec in "C5 3.347,-0.978" "C7 4.650,-0.978"; do
  set -- $spec; REF=$1; T=${TAGP:-t}-$(echo $1 | tr 'A-Z' 'a-z')
  date > $H/logs/$T-start.txt
  cd $H/scripts && BALL=$2 SPREAD=0.25 TOP=15 nice -n 19 ./run_kipy.sh $H/scripts/freespots.py $CUR $REF > $H/logs/$T-spots.log 2>&1
  $H/scripts/try_spots.sh $T $CUR $REF $H/logs/$T-spots.log 15 > $H/logs/$T-place.out 2>&1
  if [ -f $H/logs/s/$T-ok.kicad_pcb ]; then NEW=$H/steps/h$(printf %02d $N)-$(echo $REF | tr 'A-Z' 'a-z').kicad_pcb; cp $H/logs/s/$T-ok.kicad_pcb $NEW; CUR=$NEW; N=$((N+1)); echo "$REF placed: $NEW" >> $H/logs/chain.log
  else echo "$REF not placed (logs/$T-summary.log)" >> $H/logs/chain.log; fi
done
echo done > $H/logs/run5.exit
