#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# six.sh tag : the six design checks of the brief's step 5, run from ROOT in order; logs logs/six-<tag>-<n>.log with the exit code appended
W=$REPO_ROOT/design/ecad/ring-apply-a2; T=$1
ROOT=$REPO_ROOT
cd "$ROOT" && cp design/wiring/product-wiring.csv $W/logs/product-wiring-before-$T.csv
n=0
for c in "design/wiring/build_wiring.py" "design/wiring/check_wiring.py --require-complete" "design/tools/check_bom.py" "design/mfg/assembly/check_joints.py" "design/mfg/assembly/check_assembly.py" "design/mfg/tools/check_docs.py"; do
  n=$((n+1))
  cd "$ROOT" && nice -n 19 design/.venv/bin/python $c > $W/logs/six-$T-$n.log 2>&1
  echo "exit $?" >> $W/logs/six-$T-$n.log
  echo "$n $c: $(tail -2 $W/logs/six-$T-$n.log | tr '\n' ' ')"
done
