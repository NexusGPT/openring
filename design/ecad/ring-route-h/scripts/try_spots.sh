#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# try_spots.sh tag base.kicad_pcb REF spots.log [max] : for each spot line of a freespots log (in order): flip REF there on the base board,
# delete the copper the rules check then calls dangling (clean.sh), route each non-GND pad of REF with hand.py, then every other open pair
# the rules check lists (2 passes), add ground vias to islands (fixislands.sh), run the rules check;
# stop at the first board with 0 violations and 0 unconnected (copied to logs/s/<tag>-ok.kicad_pcb)
H=$REPO_ROOT/design/ecad/ring-route-h; S=$H/logs/s; T=$1; BASE=$2; REF=$3; MAX=${5:-40}
python3 - "$4" > $H/logs/$T-cands.txt <<'PY'
import re, sys
for ln in open(sys.argv[1]):
    m = re.search(r"at \((-?[\d.]+),(-?[\d.]+)\) rot-code \d+ pads \{'1': \((-?[\d.]+), (-?[\d.]+)\), '2': \((-?[\d.]+), (-?[\d.]+)\)\}", ln)
    if m: print(" ".join(m.groups()))
PY
n=0
while read x y p1x p1y p2x p2y; do
  n=$((n+1)); [ $n -gt $MAX ] && break
  $H/scripts/kp.sh $BASE $S/$T-try.kicad_pcb $H/scripts/flip.py $REF@$x,$y,$p1x,$p1y > $H/logs/$T-try$n-flip.log 2>&1
  $H/scripts/clean.sh $S/$T-try.kicad_pcb $T-try$n-pre
  J=$(cd $H/scripts && nice -n 19 ./run_kipy.sh $H/scripts/parts.py $S/$T-try.kicad_pcb $REF 2>&1 | awk '/pad/ && $3!="GND" {gsub(/[(),]/," ",$4); split($4,a," "); printf "%s %s %s F a a ", $3, a[1], a[2]}')
  $H/scripts/kp.sh $S/$T-try.kicad_pcb $S/$T-try.kicad_pcb $H/scripts/hand.py $J > $H/logs/$T-try$n-hand.log 2>&1
  R=$($H/scripts/fixislands.sh $S/$T-try.kicad_pcb $T-try$n | head -2 | tr '\n' ' ')
  $H/scripts/clean.sh $S/$T-try.kicad_pcb $T-try$n-post
  for k in 1 2; do
    $H/scripts/drc.sh $S/$T-try.kicad_pcb $T-try$n-open$k > $H/logs/$T-try$n-open$k.out 2>&1
    J2=$(python3 $H/scripts/jobs_from_drc.py $H/logs/drc-$T-try$n-open$k.json none)
    echo "open pass $k jobs: $J2" >> $H/logs/$T-try$n-open.log
    [ -z "$J2" ] && break
    $H/scripts/kp.sh $S/$T-try.kicad_pcb $S/$T-try.kicad_pcb $H/scripts/hand.py $J2 >> $H/logs/$T-try$n-open.log 2>&1
    $H/scripts/clean.sh $S/$T-try.kicad_pcb $T-try$n-post$k
  done
  R=$($H/scripts/fixislands.sh $S/$T-try.kicad_pcb $T-try$n | head -2 | tr '\n' ' ')
  echo "$n $REF@$x,$y pad1 ($p1x,$p1y) jobs [$J] -> $R" | tee -a $H/logs/$T-summary.log
  if echo "$R" | grep -q "Found 0 violations Found 0 unconnected"; then cp $S/$T-try.kicad_pcb $S/$T-ok.kicad_pcb; echo "OK at try $n" | tee -a $H/logs/$T-summary.log; break; fi
done < $H/logs/$T-cands.txt
