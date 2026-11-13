#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# red state: the drawn ribbons (v8 thin.py) with the two model changes taken back (slot_w 2.0, shell_edge 0.60); US 9 default, pair test skipped; log out/v8/red_slot2.0_edge0.6_us9.log
T=$REPO_ROOT/design/mech/thin
PY=$REPO_ROOT/design/.venv/bin/python
cd $T || exit 9
LOG=$T/out/v8/red_slot2.0_edge0.6_us9.log
( date; THIN_CHECK_SKIP_PAIRS=1 THIN_OVERRIDE="slot_w=2.0,shell_edge=0.60" nice -n 19 $PY check_thin.py; echo "exit $?"; date ) > $LOG 2>&1
