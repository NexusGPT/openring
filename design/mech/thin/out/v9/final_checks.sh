#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../.." && pwd)"  # the repository root, found from this script
# drawings, then check_parts, check_docs, check_band, check_bom: one after another at nice -n 19; exit codes to final_checks.done
D=$REPO_ROOT/design
V=$D/mech/thin/out/v9
PY=$D/.venv/bin/python
L=$D/mfg/tools/logs
cd $D/.. || exit 9
ls -la $D/mfg/drawings > $V/final/drawings_before.log 2>&1
( date; nice -n 19 $PY $D/mfg/tools/draw.py; echo "exit $?"; date ) > $L/draw_v9.log 2>&1
( date; nice -n 19 $PY $D/mfg/tools/draw.py --parts $V/drawparts; echo "exit $?"; date ) > $L/draw_v9_footstiffener.log 2>&1
ls -la $D/mfg/drawings > $V/final/drawings_after.log 2>&1
( date; cd $D/mfg/parts && nice -n 19 $PY check_parts.py; echo "exit $?"; date ) > $V/final/check_parts.log 2>&1
( date; nice -n 19 $PY $D/mfg/tools/check_docs.py; echo "exit $?"; date ) > $V/final/check_docs.log 2>&1
( date; nice -n 19 $D/ecad/ring/pcb/run_kipy.sh $D/ecad/band/check_band.py; echo "exit $?"; date ) > $V/final/check_band.log 2>&1
( date; nice -n 19 $PY $D/tools/check_bom.py; echo "exit $?"; date ) > $V/final/check_bom.log 2>&1
for f in $L/draw_v9.log $L/draw_v9_footstiffener.log $V/final/check_parts.log $V/final/check_docs.log $V/final/check_band.log $V/final/check_bom.log; do
  echo "$(basename $f): $(tail -3 $f | head -2 | tr '\n' ' ')"
done > $V/final_checks.done
