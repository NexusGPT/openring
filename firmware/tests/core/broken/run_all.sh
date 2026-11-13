#!/bin/sh
# Runs every mutation of named_cases.txt on the host (run_broken.sh) and prints one line per mutation and a last line
# "BROKEN ALL PASS <n> copies" or "BROKEN ALL FAIL <names>". Each run's log: $RING_BROKEN_OUT (default: this folder)/broken-<m>.log
BROKEN_DIR=$(cd "$(dirname "$0")" && pwd)
OUT_BASE=${RING_BROKEN_OUT:-$BROKEN_DIR}
mkdir -p "$OUT_BASE"
N=0
BAD=""
for M in $(awk '!/^#/ && NF { print $1 }' "$BROKEN_DIR/named_cases.txt"); do
	N=$((N + 1))
	RING_BROKEN_OUT=$OUT_BASE sh "$BROKEN_DIR/run_broken.sh" "$M" > "$OUT_BASE/broken-$M.log" 2>&1
	RC=$?
	echo "$M exit $RC: $(tail -1 "$OUT_BASE/broken-$M.log")"
	if [ "$RC" -ne 0 ]; then
		BAD="$BAD $M"
	fi
done
if [ -z "$BAD" ]; then
	echo "BROKEN ALL PASS $N copies"
	exit 0
fi
echo "BROKEN ALL FAIL$BAD"
exit 1
