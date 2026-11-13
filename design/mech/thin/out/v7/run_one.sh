#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# one v7 run: arg 1 = label (default, us7..us13, broken_led, broken_height)
T=$REPO_ROOT/design/mech/thin
PY=$REPO_ROOT/design/.venv/bin/python
EXT=$REPO_ROOT/design/look/s1/out
L=$1
cd $T
case $L in
  default) LOG=out/v7/check_us9_default_v7.log; ( date; nice -n 19 $PY check_thin.py; echo "exit $?"; date ) > $LOG 2>&1 ;;
  us*) N=${L#us}; B=$(awk -F, -v n=$N '$1==n{print $2}' $EXT/sizes.csv)
       LOG=out/v7/size_us${N}_v7.log
       ( date; echo "exterior ring-merged32h-us$N.step bore $B"; THIN_EXTERIOR=$EXT/ring-merged32h-us$N.step THIN_OVERRIDE="bore_d=$B" nice -n 19 $PY check_thin.py; echo "exit $?"; date ) > $LOG 2>&1 ;;
  broken_*) D=$T/out/v7/$L; cd $D
       ( date; nice -n 19 $PY thin.py; echo "build exit $?"; THIN_CHECK_SKIP_PAIRS=1 nice -n 19 $PY check_thin.py; echo "exit $?"; date ) > $D/check.log 2>&1 ;;
esac
