#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# Makes the four broken copies of case_main.kicad_pcb and runs check_boards.py on each (with the good case_pins.kicad_pcb); logs in evidence/broken_*.log, exit codes in evidence/broken_exits.txt
H=$REPO_ROOT/design/ecad/case/pcb
K=$REPO_ROOT/design/ecad/ring/pcb/run_kipy.sh
cd "$H" || exit 9
$K make_broken.py > evidence/make_broken.log 2>&1
: > evidence/broken_exits.txt
"$H/check_boards.py" > evidence/check_boards_good.log 2>&1
echo "good: exit $?" >> evidence/broken_exits.txt
for n in broken_wrongnet broken_outside broken_notrack broken_nopart; do
  "$H/check_boards.py" "$H/broken/$n.kicad_pcb" "$H/case_pins.kicad_pcb" > evidence/$n.log 2>&1
  echo "$n: exit $?" >> evidence/broken_exits.txt
done
cat evidence/broken_exits.txt
