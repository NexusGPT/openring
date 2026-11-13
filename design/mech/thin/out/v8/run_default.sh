#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# default US 9 fit check (same command as out/v7/run_one.sh default); usage: run_default.sh <label>
T=$REPO_ROOT/design/mech/thin
PY=$REPO_ROOT/design/.venv/bin/python
cd $T || exit 9
LOG=$T/out/v8/$1_us9_default.log
( date; nice -n 19 $PY check_thin.py; echo "exit $?"; date ) > $LOG 2>&1
