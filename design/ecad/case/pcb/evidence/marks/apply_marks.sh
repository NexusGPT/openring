#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../../.." && pwd)"  # the repository root, found from this script
# runs add_marks.py on both case boards and saves the line diff against the copies in before/
P=$REPO_ROOT/design/ecad/case/pcb
E=$P/evidence/marks
cd "$P" || exit 9
bash $REPO_ROOT/design/ecad/ring/pcb/run_kipy.sh "$P/add_marks.py" > "$E/add_marks.log" 2>&1
echo "add_marks exit $?"
grep -v assert "$E/add_marks.log"
for B in case_pins case_main; do
  diff "$E/before/$B.kicad_pcb" "$P/$B.kicad_pcb" > "$E/diff_$B.txt"
  echo "$B diff lines: $(grep -c '^[<>]' "$E/diff_$B.txt") removed lines: $(grep -c '^<' "$E/diff_$B.txt")"
done
date
