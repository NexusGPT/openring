#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../.." && pwd)"  # the repository root, found from this script
# after the pin height change: broken copies of test 18 first (short), then the full check on out/ (long); one at a time at nice 19, .done files in r4/
C=$REPO_ROOT/design/case
R4=$C/r4
PY=$REPO_ROOT/design/.venv/bin/python
run() {
  local name=$1; shift
  { echo "start $(date '+%Y-%m-%d %H:%M:%S')"; env "$@"; rc=$?; echo "end $(date '+%Y-%m-%d %H:%M:%S') exit $rc"; echo $rc > "$R4/$name.done"; } > "$R4/$name.log" 2>&1
}
cd "$C" || exit 2
run broken_pin_swap_build CASE_OUT=$R4/broken/pin_swap/out CASE_PIN_SWAP=1 nice -n 19 "$PY" -u case.py
run broken_pin_swap_check CASE_OUT=$R4/broken/pin_swap/out CASE_PIN_SWAP=1 CASE_CONTACT_CSV=$R4/broken/pin_swap/contact.csv CASE_CHECK_ONLY_R4=18 nice -n 19 "$PY" -u case_check.py
run broken_pin_high_build CASE_OUT=$R4/broken/pin_high/out CASE_PIN_H0=2.35 CASE_PIN_H0_OUT=2.35 nice -n 19 "$PY" -u case.py
run broken_pin_high_check CASE_OUT=$R4/broken/pin_high/out CASE_PIN_H0=2.35 CASE_PIN_H0_OUT=2.35 CASE_CONTACT_CSV=$R4/broken/pin_high/contact.csv CASE_CHECK_ONLY_R4=18 nice -n 19 "$PY" -u case_check.py
run pins_full_check nice -n 19 "$PY" -u case_check.py
run pins_docs "$PY" -I check_case_docs.py
echo "run_pins.sh finished $(date '+%Y-%m-%d %H:%M:%S')" > "$R4/run_pins.done"
