#!/bin/sh
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# usage: step.sh <log name> <command...>   runs the command from design/ecad/ring at nice 19, both streams to
# evidence/a7/<log name>, appends "exit N", prints the log
E=$REPO_ROOT/design/ecad/ring/evidence/a7
L="$E/$1"; shift
cd $REPO_ROOT/design/ecad/ring || exit 9
date '+started %Y-%m-%d %H:%M:%S' > "$L"
nice -n 19 "$@" >> "$L" 2>&1
echo "exit $?" >> "$L"
date '+ended %Y-%m-%d %H:%M:%S' >> "$L"
cat "$L"
