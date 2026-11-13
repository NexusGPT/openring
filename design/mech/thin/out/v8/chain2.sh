#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# after chain.sh: the red state run, then the per-size exports of the two ribbons (one heavy build at a time)
T=$REPO_ROOT/design/mech/thin/out/v8
PY=$REPO_ROOT/design/.venv/bin/python
EXT=$REPO_ROOT/design/look/s1/out
until [ -f $T/chain.done ]; do perl -e 'select(undef,undef,undef,10)'; done
for N in 9 7 8 10 11 12 13; do
  B=$(awk -F, -v n=$N '$1==n{print $2}' $EXT/sizes.csv)
  ( date; THIN_EXTERIOR=$EXT/ring-merged32h-us$N.step THIN_OVERRIDE="bore_d=$B" nice -n 19 $PY $T/export_ribbons.py $N; echo "exit $?"; date ) > $T/export_flex_us$N.log 2>&1
done
$T/run_red.sh
date > $T/chain2.done
