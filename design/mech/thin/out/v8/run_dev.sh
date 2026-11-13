#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# development run, pair test skipped (result line says DEBUG-NO-PAIRS, never PASS). usage: run_dev.sh <label> [us]
T=$REPO_ROOT/design/mech/thin
PY=$REPO_ROOT/design/.venv/bin/python
EXT=$REPO_ROOT/design/look/s1/out
cd $T || exit 9
LOG=$T/out/v8/$1.log
if [ -n "$2" ]; then
  B=$(awk -F, -v n=$2 '$1==n{print $2}' $EXT/sizes.csv)
  ( date; echo "exterior ring-merged32h-us$2.step bore $B"; THIN_CHECK_SKIP_PAIRS=1 THIN_EXTERIOR=$EXT/ring-merged32h-us$2.step THIN_OVERRIDE="bore_d=$B" nice -n 19 $PY check_thin.py; echo "exit $?"; date ) > $LOG 2>&1
else
  ( date; THIN_CHECK_SKIP_PAIRS=1 nice -n 19 $PY check_thin.py; echo "exit $?"; date ) > $LOG 2>&1
fi
