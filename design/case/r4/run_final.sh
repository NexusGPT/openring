#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
# r4 proof runs, one at a time at nice 19, each with its own log and exit code:
#  1. build the delivered model into design/case/out (case.py)            -> r4/final_build.log, r4/final_build.done
#  2. full fit check on it (case_check.py, tests 1 to 17)                 -> r4/final_check.log, r4/final_check.done
#  3. the doc check (check_case_docs.py)                                  -> r4/final_docs.log, r4/final_docs.done
#  4. broken copies (each its own CASE_OUT under r4/broken/, only the tests they target):
#     board_long  (main board 1 mm longer, file copy)    tests 15,16  -> r4/broken_board_long_{build,check}.log
#     part_tall   (J1 1 mm taller, file copy)            tests 15,16  -> r4/broken_part_tall_{build,check}.log
#     lead_low    (wire run 0.6 mm lower, CASE_LEAD_FAULT) tests 15,16 -> r4/broken_lead_low_{build,check}.log
#     lift_wall   (tooth in the lift path, CASE_LIFT_FAULT) test 17   -> r4/broken_lift_wall_{build,check}.log
# usage: run_final.sh [all|final|broken]
C=$REPO_ROOT/design/case
R4=$C/r4
PY=$REPO_ROOT/design/.venv/bin/python
WHAT=${1:-all}
run() {  # name, then env assignments and the command
  local name=$1; shift
  { echo "start $(date '+%Y-%m-%d %H:%M:%S')"; env "$@"; rc=$?; echo "end $(date '+%Y-%m-%d %H:%M:%S') exit $rc"; echo $rc > "$R4/$name.done"; } > "$R4/$name.log" 2>&1
}
cd "$C" || exit 2
if [ "$WHAT" = all ] || [ "$WHAT" = final ]; then
  run final_build nice -n 19 "$PY" -u case.py
  run final_check nice -n 19 "$PY" -u case_check.py
  run final_docs "$PY" -I check_case_docs.py
fi
if [ "$WHAT" = all ] || [ "$WHAT" = broken ]; then
  for b in board_long part_tall; do
    run broken_${b}_build CASE_OUT=$R4/broken/$b/out CASE_BOARD_MAIN=$R4/broken/$b/case_main.kicad_pcb nice -n 19 "$PY" -u case.py
    run broken_${b}_check CASE_OUT=$R4/broken/$b/out CASE_BOARD_MAIN=$R4/broken/$b/case_main.kicad_pcb CASE_CHECK_ONLY_R4=15,16 nice -n 19 "$PY" -u case_check.py
  done
  run broken_lead_low_build CASE_OUT=$R4/broken/lead_low/out CASE_LEAD_FAULT=1 nice -n 19 "$PY" -u case.py
  run broken_lead_low_check CASE_OUT=$R4/broken/lead_low/out CASE_CHECK_ONLY_R4=15,16 nice -n 19 "$PY" -u case_check.py
  run broken_lift_wall_build CASE_OUT=$R4/broken/lift_wall/out CASE_LIFT_FAULT=1 nice -n 19 "$PY" -u case.py
  run broken_lift_wall_check CASE_OUT=$R4/broken/lift_wall/out CASE_CHECK_ONLY_R4=17 nice -n 19 "$PY" -u case_check.py
fi
echo "run_final.sh $WHAT finished $(date '+%Y-%m-%d %H:%M:%S')" > "$R4/run_final_$WHAT.done"
