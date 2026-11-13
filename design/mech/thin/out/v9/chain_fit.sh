#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# Fit check US 7 to 13 on the delivered thin.py and check_thin.py, one size after another at nice -n 19 (through run_check.sh).
# usage: chain_fit.sh <label>   logs: out/v9/<label>_usN.log; summary: out/v9/<label>_chain.log; real exit codes: out/v9/<label>_chain.done
T=$REPO_ROOT/design/mech/thin
L=$1
S=$T/out/v9/${L}_chain.log
cd $T || exit 9
echo "chain $L start $(date)" > $S
shasum $T/thin.py $T/check_thin.py $T/placement.csv $T/out/thin-inside.glb >> $S 2>&1
worst=0
for N in 7 8 9 10 11 12 13; do
  $T/out/v9/run_check.sh $N $L
  e=$(tail -2 $T/out/v9/${L}_us${N}.log | awk '/^exit /{print $2}')
  [ -z "$e" ] && e=99
  echo "US $N exit $e last: $(grep '^RESULT' $T/out/v9/${L}_us${N}.log | tail -1) $(date)" >> $S
  [ "$e" != "0" ] && worst=1
done
shasum $T/thin.py $T/check_thin.py $T/placement.csv $T/out/thin-inside.glb >> $S 2>&1
echo "chain $L end $(date) exit $worst" >> $S
grep -E "^US |exit [0-9]+$" $S > $T/out/v9/${L}_chain.done
exit $worst
