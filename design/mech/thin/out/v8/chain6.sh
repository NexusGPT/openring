#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# after the US 13 run: US 12 again (motor_x 0.8), the broken copy's named test, the exports; one heavy run at a time, nice -n 19
T=$REPO_ROOT/design/mech/thin/out/v8
PY=$REPO_ROOT/design/.venv/bin/python
EXT=$REPO_ROOT/design/look/s1/out
until grep -q "^exit" $T/v8_us13.log; do perl -e 'select(undef,undef,undef,10)'; done
$T/run_check.sh 12 v8b
( date; cd $T/broken_trunk && nice -n 19 $PY broken_named_test.py; echo "exit $?"; date ) > $T/broken_trunk/named_test.log 2>&1
for N in 9 7 8 10 11 12 13; do
  B=$(awk -F, -v n=$N '$1==n{print $2}' $EXT/sizes.csv)
  ( date; THIN_EXTERIOR=$EXT/ring-merged32h-us$N.step THIN_OVERRIDE="bore_d=$B" nice -n 19 $PY $T/export_ribbons.py $N; echo "exit $?"; date ) > $T/export_flex_us$N.log 2>&1
done
date > $T/chain6.done
