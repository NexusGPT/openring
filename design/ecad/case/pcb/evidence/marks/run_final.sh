#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../../.." && pwd)"  # the repository root, found from this script
# usage: run_final.sh <tag>: netlist script, run_all.sh, check_boards.py, check_case_docs.py, each with its own log and exit file in evidence/marks
T=$1
C=$REPO_ROOT/design/ecad/case
E=$C/pcb/evidence/marks
PY=$REPO_ROOT/design/.venv/bin/python
cd "$C" || exit 9
nice -n 19 "$PY" make_netlist.py > "$E/${T}_make_netlist.log" 2>&1; echo "exit $?" > "$E/${T}_make_netlist.exit"
nice -n 19 bash run_all.sh "marks_$T" > "$E/${T}_run_all.out" 2>&1; echo "exit $?" > "$E/${T}_run_all.exit"
nice -n 19 "$PY" "$C/pcb/check_boards.py" > "$E/${T}_check_boards.log" 2>&1; echo "exit $?" > "$E/${T}_check_boards.exit"
nice -n 19 "$PY" "$C/../../case/check_case_docs.py" > "$E/${T}_check_case_docs.log" 2>&1; echo "exit $?" > "$E/${T}_check_case_docs.exit"
echo done > "$E/${T}_all.done"
