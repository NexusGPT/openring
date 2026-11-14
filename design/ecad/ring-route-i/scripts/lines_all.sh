#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# lines_all.sh board tag : the 8 controlled-line limits on one board: lines.sh (Gerber read-back p4p5.py + xcheck_clear.py), round 4's
# linestretch.py with FAR=1.0, then lines_check.py. Last line of logs/lines_check-<tag>.log: RESULT PASS / FAIL.
I=$REPO_ROOT/design/ecad/ring-route-i; B=$1; T=$2
$I/scripts/lines.sh "$B" "$T" > $I/logs/lines-$T.out 2>&1
FAR=1.0 PYTHONDONTWRITEBYTECODE=1 nice -n 19 $I/scripts/run_kipy.sh -B $I/rb/linestretch.py "$B" > $I/logs/linestretch-far-$T.log 2>&1
echo "exit $?" >> $I/logs/linestretch-far-$T.log
python3 -B $I/scripts/lines_check.py $I/logs/p4p5-$T.log $I/logs/xcheck-$T.log $I/logs/linestretch-far-$T.log > $I/logs/lines_check-$T.log 2>&1
echo "exit $?" >> $I/logs/lines_check-$T.log
cat $I/logs/lines_check-$T.log
