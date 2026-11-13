#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# build the model outputs (default US 9, exterior merged32h): placement.csv, layers.json, out/thin-inside.glb, .step, triangles.txt
T=$REPO_ROOT/design/mech/thin
PY=$REPO_ROOT/design/.venv/bin/python
cd $T || exit 9
( date; nice -n 19 $PY thin.py; echo "exit $?"; date ) > $T/out/v8/$1.log 2>&1
