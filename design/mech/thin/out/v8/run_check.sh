#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# usage: run_check.sh <us> <label>   one size, fit check; log out/v8/<label>_us<N>.log
T=$REPO_ROOT/design/mech/thin
PY=$REPO_ROOT/design/.venv/bin/python
EXT=$REPO_ROOT/design/look/s1/out
N=$1
L=$2
cd $T || exit 9
B=$(awk -F, -v n=$N '$1==n{print $2}' $EXT/sizes.csv)
LOG=$T/out/v8/${L}_us${N}.log
( date; echo "exterior ring-merged32h-us$N.step bore $B"; THIN_EXTERIOR=$EXT/ring-merged32h-us$N.step THIN_OVERRIDE="bore_d=$B" nice -n 19 $PY check_thin.py; echo "exit $?"; date ) > $LOG 2>&1
