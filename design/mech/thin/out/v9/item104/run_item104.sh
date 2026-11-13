#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../../.." && pwd)"  # the repository root, found from this script
# item 104: model figures in memory (one process), then the STEP read back by a fresh process; usage: run_item104.sh <thin folder> <step file> <tag>
I=$REPO_ROOT/design/mech/thin/out/v9/item104
PY=$REPO_ROOT/design/.venv/bin/python
cd $I || exit 9
( date; nice -n 19 $PY model_figures.py $1 $I/model_$3.json; echo "exit $?"; date ) > $I/model_$3.log 2>&1
( date; nice -n 19 $PY step_readback.py $2 $I/model_$3.json; echo "exit $?"; date ) > $I/readback_$3.log 2>&1
tail -4 $I/model_$3.log
echo "DIFFERS lines: $(grep -c DIFFERS $I/readback_$3.log)"
grep DIFFERS $I/readback_$3.log | head -20
tail -5 $I/readback_$3.log
