#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# broken copy: the joystick-side trunk goes back to 1.4 wide in this one place; the check with the pair test skipped (as the v7 broken copies); log out/v8/broken_trunk/check.log
T=$REPO_ROOT/design/mech/thin
PY=$REPO_ROOT/design/.venv/bin/python
D=$T/out/v8/$1
cd $D || exit 9
( date; THIN_CHECK_SKIP_PAIRS=1 nice -n 19 $PY check_thin.py; echo "exit $?"; date ) > $D/check.log 2>&1
