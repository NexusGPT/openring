#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../../.." && pwd)"  # the repository root, found from this script
# makes the broken copies (4 from the new good main board, 4 for the marks) and runs check_boards.py on each; log + exit per copy in evidence/marks/broken/
P=$REPO_ROOT/design/ecad/case/pcb
E=$P/evidence/marks
RK=$REPO_ROOT/design/ecad/ring/pcb/run_kipy.sh
PY=$REPO_ROOT/design/.venv/bin/python
mkdir -p "$E/broken"
cd "$E" || exit 9
bash $RK "$E/make_broken_copy.py" "$P/case_main.kicad_pcb" > "$E/broken/make_broken_copy.log" 2>&1
for n in broken_nomarks_pins broken_swapped_pins broken_nomarks_main broken_small_pins; do bash $RK "$E/make_broken_marks.py" $n > "$E/broken/make_$n.log" 2>&1; done
GP=$P/case_pins.kicad_pcb
GM=$P/case_main.kicad_pcb
: > "$E/broken/exits.txt"
nice -n 19 "$PY" "$P/check_boards.py" "$GM" "$GP" > "$E/broken/good.log" 2>&1; echo "good: exit $?" >> "$E/broken/exits.txt"
for n in broken_wrongnet broken_outside broken_notrack broken_nopart broken_nomarks_main; do
  nice -n 19 "$PY" "$P/check_boards.py" "$E/broken/$n.kicad_pcb" "$GP" > "$E/broken/$n.log" 2>&1; echo "$n: exit $?" >> "$E/broken/exits.txt"
done
for n in broken_nomarks_pins broken_swapped_pins broken_small_pins; do
  nice -n 19 "$PY" "$P/check_boards.py" "$GM" "$E/broken/$n.kicad_pcb" > "$E/broken/$n.log" 2>&1; echo "$n: exit $?" >> "$E/broken/exits.txt"
done
echo done > "$E/broken/all.done"
