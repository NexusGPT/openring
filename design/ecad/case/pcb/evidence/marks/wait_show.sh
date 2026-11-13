#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../../.." && pwd)"  # the repository root, found from this script
# usage: wait_show.sh <tag>: waits (at most 200 s) for <tag>_all.done, then prints exits and the last lines of each log
E=$REPO_ROOT/design/ecad/case/pcb/evidence/marks
T=$1
for i in $(seq 1 40); do
  [ -f "$E/${T}_all.done" ] && break
  sleep 5
done
cd "$E" || exit 9
ls ${T}_*
for f in ${T}_*.exit; do echo "$f: $(cat $f)"; done
cat ${T}_make_netlist.log
tail -5 ${T}_run_all.out
tail -14 ${T}_check_boards.log
tail -2 ${T}_check_case_docs.log
