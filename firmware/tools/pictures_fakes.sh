#!/bin/bash
# pictures_fakes.sh <handler log> <pictures dir> <work folder>: the manifest tool must refuse a run that lost a picture and a run
# that repeated one, and say why. Makes two fakes from the real handler log and runs tools/pictures_manifest.py on them.
# Exit 0 only when both exit 1 AND both reason lines are in the tool's output ("PICTURE pairing is listed 0 times",
# "PICTURE status is listed 21 times"): an exit 1 without its reason (a crash, an empty path) fails.
h=$1
d=$2
OUT=$3
FW=$(cd "$(dirname "$0")/.." && pwd)
if [ -z "$h" ] || [ ! -f "$h" ]; then
	echo "pictures-fakes: no handler log to make the fakes from (path '$h')"
	exit 1
fi
mkdir -p "$OUT"
grep -v "SCREENPIC pairing " "$h" > "$OUT/fake-missing.log"
python3 "$FW/tools/pictures_manifest.py" "$OUT/fake-missing.log" "$d" "$OUT/fake-missing.md" > "$OUT/fake-missing.out" 2>&1
rc1=$?
cat "$OUT/fake-missing.out"
l=$(grep "SCREENPIC status " "$h" | head -1)
for i in $(seq 21); do echo "$l"; done > "$OUT/fake-repeat.log"
python3 "$FW/tools/pictures_manifest.py" "$OUT/fake-repeat.log" "$d" "$OUT/fake-repeat.md" > "$OUT/fake-repeat.out" 2>&1
rc2=$?
cat "$OUT/fake-repeat.out"
echo "pictures-fakes: the fake with the pairing picture missing exits $rc1, the fake with 21 lines of one picture exits $rc2 (both must be 1)"
[ "$rc1" -eq 1 ] && [ "$rc2" -eq 1 ] || exit 1
if ! grep -q "PICTURE pairing is listed 0 times" "$OUT/fake-missing.out"; then
	echo "pictures-fakes: the reason line 'PICTURE pairing is listed 0 times' is missing from the output of the first fake"
	exit 1
fi
if ! grep -q "PICTURE status is listed 21 times" "$OUT/fake-repeat.out"; then
	echo "pictures-fakes: the reason line 'PICTURE status is listed 21 times' is missing from the output of the second fake"
	exit 1
fi
echo "pictures-fakes: both reason lines are in the tool's output"
exit 0
