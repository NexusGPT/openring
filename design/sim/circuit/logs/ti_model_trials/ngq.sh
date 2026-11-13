#!/bin/sh
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# usage: ngq.sh deck.cir [behavior]   prints RESULT and error lines of one ngspice run (scratch helper)
C=$REPO_ROOT/design/sim/circuit
if [ -n "$2" ]; then export NGBEHAVIOR="$2"; fi
"$C/../../.venv/bin/python" -I "$C/ngrun.py" "$1" "$1.out" > "$1.log" 2>&1
grep -E "RESULT|rror|MIF|undefined|nknown" "$1.out" | head -${3:-8}
exit 0
