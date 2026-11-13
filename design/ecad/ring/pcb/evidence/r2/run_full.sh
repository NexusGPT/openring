#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../../.." && pwd)"  # the repository root, found from this script
# run_full.sh <tag>: make_board.sh with nice 19, its logs, the rules check report and the open list copied to evidence/r2/<tag>
P=$REPO_ROOT/design/ecad/ring/pcb; E=$P/evidence/r2/$1
mkdir -p "$E" && date > "$E/start.txt"
cd "$P" && nice -n 19 /bin/bash "$P/make_board.sh" > "$E/make_board.log" 2>&1
rc=$?
date >> "$E/start.txt"
cp -r "$P/build-logs" "$E/" && cp "$P/ring-drc.json" "$P/drc-report.txt" "$E/"
$REPO_ROOT/design/.venv/bin/python "$P/open_nets.py" "$E/ring-drc.json" > "$E/open_nets.txt" 2>&1
echo $rc > "$E/make_board.done"
