#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../../.." && pwd)"  # the repository root, found from this script
# run_broken.sh: each broken copy of make_broken.py, then check_board.py on it; logs in evidence/r2/broken/
P=$REPO_ROOT/design/ecad/ring/pcb; B=$P/evidence/r2/broken
mkdir -p "$B"
for k in net outside track missing antvia swap; do
  cd "$P" && nice -n 19 "$P/run_kipy.sh" "$P/make_broken.py" "$k" "$B" > "$B/make_$k.log" 2>&1
  cd "$P" && nice -n 19 "$P/run_kipy.sh" "$P/check_board.py" "$B/broken_$k.kicad_pcb" > "$B/check_$k.log" 2>&1
  echo "exit $?" >> "$B/check_$k.log"
done
