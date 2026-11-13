#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
# second run of the two board-file broken copies (after fix_broken_text.py), one at a time at nice 19; waits for run_final.sh to end first
C=$REPO_ROOT/design/case
R4=$C/r4
PY=$REPO_ROOT/design/.venv/bin/python
until [ -f "$R4/run_final_all.done" ]; do sleep 20; done
run() {
  local name=$1; shift
  { echo "start $(date '+%Y-%m-%d %H:%M:%S')"; env "$@"; rc=$?; echo "end $(date '+%Y-%m-%d %H:%M:%S') exit $rc"; echo $rc > "$R4/$name.done"; } > "$R4/$name.log" 2>&1
}
cd "$C" || exit 2
for b in board_long part_tall; do
  run broken_${b}_build CASE_OUT=$R4/broken/$b/out CASE_BOARD_MAIN=$R4/broken/$b/case_main.kicad_pcb nice -n 19 "$PY" -u case.py
  run broken_${b}_check CASE_OUT=$R4/broken/$b/out CASE_BOARD_MAIN=$R4/broken/$b/case_main.kicad_pcb CASE_CHECK_ONLY_R4=15,16 nice -n 19 "$PY" -u case_check.py
done
echo "run_broken2.sh finished $(date '+%Y-%m-%d %H:%M:%S')" > "$R4/run_broken2.done"
