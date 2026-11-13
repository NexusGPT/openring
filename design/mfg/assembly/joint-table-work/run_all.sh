#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../.." && pwd)"  # the repository root, found from this script
# Final runs, one at a time, at nice 19. Each log gets its exit code as its last line.
R=$REPO_ROOT
W=$R/design/mfg/assembly/joint-table-work
PY=$R/design/.venv/bin/python
L=$W/logs/final
mkdir -p $L
date > $L/time.txt
shasum -a 256 $R/design/mfg/assembly/assembly.md $R/design/wiring/product-wiring.csv $R/design/ecad/band/band-interface.md $R/design/ecad/case/pcb/board-notes.md $R/design/wiring/lead-decisions.md $R/design/case/case-architecture.md $R/design/wiring/screen-cable-study.md $R/design/ecad/ring/pcb/ring.kicad_pcb $W/boards/ring.kicad_pcb > $L/inputs-sha.txt 2>&1
nice -n 19 $PY -B $W/build_joints.py > $L/build.log 2>&1; echo "exit $?" >> $L/build.log
nice -n 19 $PY -B $R/design/mfg/assembly/check_joints.py > $L/check.log 2>&1; echo "exit $?" >> $L/check.log
nice -n 19 $PY -B $R/design/mfg/assembly/check_joints.py --list-gaps > $L/list-gaps.log 2>&1; echo "exit $?" >> $L/list-gaps.log
nice -n 19 $PY -B $W/tests/run_tests.py > $L/tests.log 2>&1; echo "exit $?" >> $L/tests.log
nice -n 19 $PY -B $W/audit_citations.py > $L/audit_citations.log 2>&1; echo "exit $?" >> $L/audit_citations.log
nice -n 19 $PY -B $W/count_ends.py > $L/count_ends.log 2>&1; echo "exit $?" >> $L/count_ends.log
nice -n 19 $PY -B $W/make_gaps.py > $L/make_gaps.log 2>&1; echo "exit $?" >> $L/make_gaps.log
for r in R1 R2 R3 R4 R5; do echo "$r $(grep -c "^$r " $L/check.log)"; done > $L/check-rule-counts.txt 2>&1
grep "^R2 MISSING: J-W0[0-9][0-9]-A field solder_source" $L/check.log > $L/check-hotbar-solder.txt 2>&1
date >> $L/time.txt
du -sh $W >> $L/time.txt 2>&1
