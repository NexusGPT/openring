#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# the two broken copies and a control, named tests only, against the delivered check_thin.py; each broken copy differs from the delivered thin.py in one line
T=$REPO_ROOT/design/mech/thin
V=$T/out/v9
PY=$REPO_ROOT/design/.venv/bin/python
cd $V || exit 9
for b in broken_place broken_zone; do
  diff $T/thin.py $V/$b/thin.py > $V/$b/broken_vs_final.diff
  ( date; shasum $T/check_thin.py; nice -n 19 $PY $V/named_tests.py $V/$b $T/check_thin.py; echo "exit $?"; date ) > $V/$b/named_test.log 2>&1
done
( date; shasum $T/thin.py $T/check_thin.py; nice -n 19 $PY $V/named_tests.py $T $T/check_thin.py; echo "exit $?"; date ) > $V/named_final_control.log 2>&1
cat $V/broken_place/broken_vs_final.diff $V/broken_zone/broken_vs_final.diff
grep -h "FAIL\|findings\|RESULT\|^exit\|holds" $V/broken_place/named_test.log $V/broken_zone/named_test.log | cut -c1-250
tail -3 $V/named_final_control.log
