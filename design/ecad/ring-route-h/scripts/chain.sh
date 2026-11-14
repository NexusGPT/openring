#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# chain.sh start.kicad_pcb firststep REF... : place each part in turn with place.sh (30 spots), starting from the last board that closed;
# a closed board is saved as steps/h<NN>-<ref>.kicad_pcb. C7: only spots whose DECA pad is within 3.0 mm of U1 A8 (NEARPAD).
H=$REPO_ROOT/design/ecad/ring-route-h; CUR=$1; N=$2; shift 2
for REF in "$@"; do
  T=${TAGP:-p}-$(echo $REF | tr 'A-Z' 'a-z')
  if [ "$REF" = C7 ]; then NEARPAD=4.650,-0.978,3.0 $H/scripts/place.sh $T $CUR $REF 40; else $H/scripts/place.sh $T $CUR $REF 30; fi
  if [ -f $H/logs/s/$T-ok.kicad_pcb ]; then
    NEW=$H/steps/h$(printf %02d $N)-$(echo $REF | tr 'A-Z' 'a-z').kicad_pcb; cp $H/logs/s/$T-ok.kicad_pcb $NEW; CUR=$NEW; N=$((N+1))
    echo "$REF placed: $NEW" >> $H/logs/chain.log
  else
    echo "$REF not placed (see logs/$T-summary.log)" >> $H/logs/chain.log
  fi
done
date >> $H/logs/chain.log; echo done > $H/logs/chain.exit
