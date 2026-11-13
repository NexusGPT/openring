#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# writes the v9 dev copies of thin.py and check_thin.py over the delivered files, with hashes and diffs saved
T=$REPO_ROOT/design/mech/thin
V=$T/out/v9
date
shasum $T/thin.py $T/check_thin.py $T/placement.csv $T/layers.json $T/out/thin-inside.step $T/out/thin-inside.glb > $V/swap_before_shasum.log 2>&1
diff $V/before/thin.py $V/dev/thin.py > $V/thin_v8_to_v9.diff
diff $V/before/check_thin.py $V/dev/check_thin.py > $V/check_thin_v8_to_v9.diff
cmp $V/before/thin.py $T/thin.py && cmp $V/before/check_thin.py $T/check_thin.py && echo "delivered files still as found"
cp $V/dev/thin.py $T/thin.py
cp $V/dev/check_thin.py $T/check_thin.py
shasum $T/thin.py $V/dev/thin.py $T/check_thin.py $V/dev/check_thin.py
wc -l $V/thin_v8_to_v9.diff $V/check_thin_v8_to_v9.diff
date
