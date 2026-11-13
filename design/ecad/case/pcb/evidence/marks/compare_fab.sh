#!/bin/bash
export REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")/../../../../../.." && pwd)"  # the repository root, found from this script
# compares every Gerber and drill file of fab/ with the copy made before the change (evidence/marks/before/fab): bytes, and bytes without the creation-date line
P=$REPO_ROOT/design/ecad/case/pcb
B=$P/evidence/marks/before/fab
for T in case_pins case_main; do
  for f in "$P/fab/$T/gerber/"*; do
    n=$(basename "$f")
    if [ ! -f "$B/$T/gerber/$n" ]; then echo "NEW $T/$n $(stat -f %z "$f") bytes"; continue; fi
    a=$(shasum -a 256 < "$B/$T/gerber/$n" | cut -c1-12)
    b=$(shasum -a 256 < "$f" | cut -c1-12)
    a2=$(grep -v -E 'CreationDate|GenerationSoftware|Created by KiCad|DRILL file KiCad' "$B/$T/gerber/$n" | shasum -a 256 | cut -c1-12)
    b2=$(grep -v -E 'CreationDate|GenerationSoftware|Created by KiCad|DRILL file KiCad' "$f" | shasum -a 256 | cut -c1-12)
    if [ "$a" = "$b" ]; then r=BYTE-EQUAL; elif [ "$a2" = "$b2" ]; then r=EQUAL-EXCEPT-DATE-LINES; else r=DIFFERENT; fi
    echo "$r $T/$n before $(stat -f %z "$B/$T/gerber/$n") after $(stat -f %z "$f")"
  done
done
echo "--- files before not after:"
(cd "$B" && find . -type f | sort) > "$P/evidence/marks/fab_list_before.txt"
(cd "$P/fab" && find . -type f | sort) > "$P/evidence/marks/fab_list_after.txt"
diff "$P/evidence/marks/fab_list_before.txt" "$P/evidence/marks/fab_list_after.txt" && echo "same file list"
