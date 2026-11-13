#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# usage: runlog.sh <logfile> <command...>   runs the command in the ring folder, saves both streams and the exit code
LOG=$1; shift
cd $REPO_ROOT/design/ecad/ring || exit 9
"$@" > "$LOG" 2>&1
RC=$?
echo "exit $RC" >> "$LOG"
exit $RC
