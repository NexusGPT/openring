#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# full fit check of the dev copy (out/v9/dev) at a size; usage: run_dev.sh <us> <label>; log out/v9/<label>_us<N>.log; done file out/v9/<label>_us<N>.done
T=$REPO_ROOT/design/mech/thin
PY=$REPO_ROOT/design/.venv/bin/python
EXT=$REPO_ROOT/design/look/s1/out
N=$1
L=$2
cd $T/out/v9/dev || exit 9
B=$(awk -F, -v n=$N '$1==n{print $2}' $EXT/sizes.csv)
LOG=$T/out/v9/${L}_us${N}.log
( date; echo "dev copy; exterior ring-merged32h-us$N.step bore $B"; THIN_EXTERIOR=$EXT/ring-merged32h-us$N.step THIN_OVERRIDE="bore_d=$B" nice -n 19 $PY check_thin.py; echo "exit $?"; date ) > $LOG 2>&1
tail -2 $LOG | head -1 > $T/out/v9/${L}_us${N}.done
