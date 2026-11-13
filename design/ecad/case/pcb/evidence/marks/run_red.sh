#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../../.." && pwd)"  # the repository root, found from this script
# red run: the new check_boards.py on the two boards as they were BEFORE the marks (copies in before/); expected: FAIL lines for the marks
P=$REPO_ROOT/design/ecad/case/pcb
E=$P/evidence/marks
PY=$REPO_ROOT/design/.venv/bin/python
mkdir -p "$E/before_run"
cp "$E/before/case_main.kicad_pcb" "$E/before_run/case_main.kicad_pcb"
cp "$E/before/case_pins.kicad_pcb" "$E/before_run/case_pins.kicad_pcb"
cp "$P/case_main.kicad_pro" "$E/before_run/case_main.kicad_pro"
cp "$P/case_pins.kicad_pro" "$E/before_run/case_pins.kicad_pro"
nice -n 19 "$PY" "$P/check_boards.py" "$E/before_run/case_main.kicad_pcb" "$E/before_run/case_pins.kicad_pcb" > "$E/red_check_boards.log" 2>&1
echo "exit $?" > "$E/red_check_boards.exit"
