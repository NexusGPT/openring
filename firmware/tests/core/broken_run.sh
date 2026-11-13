#!/bin/bash
# broken_run.sh: proof that the core's Zephyr suite can fail on the new sign hook. Runs inside the ring-os-toolchain container,
# firmware at /ws/firmware.
#
# Usage, from the Mac: sh firmware/tools/remote.sh core-broken "tests/core/broken_run.sh [VARIANTS [BOARDS]]"
#
# For each variant (default: the three of step 6, sign_ignored sign_hook_twice sign_before_b5) it makes a copy of the module
# with the one edit of broken/run_broken.sh (apply only), runs the suite on the copy with west twister on native_sim and on the
# simulated ring chip (nrf54lm20bsim/nrf54lm20a/cpuapp), and passes only when, on each board, the suite ran and the case named in
# broken/named_cases.txt failed (a build error or a timeout does not count). The real files are not touched. The 23 earlier
# variants are proven by the host run (broken/run_all.sh) and can be named here too.
# Last line: "RESULT PASS" or "RESULT FAIL <what>".

set -u
FW=$(cd "$(dirname "$0")/../.." && pwd)
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-core-broken}
VARIANTS="sign_ignored sign_hook_twice sign_before_b5"
BOARDS="native_sim nrf54lm20bsim/nrf54lm20a/cpuapp"
if [ -n "${1:-}" ]; then
	VARIANTS=$1
fi
if [ -n "${2:-}" ]; then
	BOARDS=$2
fi
mkdir -p "$OUT"
FAILED=""
for V in $VARIANTS; do
	echo "##### broken copy: $V"
	NAMED=$(awk -v m="$V" '$1 == m { print $2 }' "$FW/tests/core/broken/named_cases.txt")
	if [ -z "$NAMED" ] || [ "$NAMED" = "-" ]; then
		echo "RESULT FAIL variant $V has no failing named case in named_cases.txt"
		exit 1
	fi
	D=$OUT/copy-$V/ring_core
	rm -rf "$OUT/copy-$V"
	RING_BROKEN_OUT=$OUT RING_BROKEN_APPLY_ONLY=1 sh "$FW/tests/core/broken/run_broken.sh" "$V" > "$OUT/apply-$V.log" 2>&1 || {
		cat "$OUT/apply-$V.log"
		echo "RESULT FAIL the edit of $V could not be made"
		exit 1
	}
	cat "$OUT/apply-$V.log"
	diff -u "$FW/modules/ring_core" "$D" > "$OUT/broken_$V.diff" 2>&1
	if [ ! -s "$OUT/broken_$V.diff" ]; then
		echo "RESULT FAIL the edit of $V changed nothing"
		exit 1
	fi
	SUITE=${NAMED%%.*}
	CASE=${NAMED#*.}
	for P in $BOARDS; do
		T=$V-$(echo "$P" | tr '/' '_')
		west twister -T "$FW/tests/core" -p "$P" -O "$OUT/twister-$T" --inline-logs -v \
			--extra-args RING_CORE_DIR="$D" > "$OUT/twister-$T.log" 2>&1
		RC=$?
		grep -E "FAIL|passed|failed|Assertion" "$OUT/twister-$T.log" | head -30
		echo "twister exit code on the broken copy $V, $P: $RC (log $OUT/twister-$T.log)"
		if grep -q "PROJECT EXECUTION FAILED" "$OUT/twister-$T.log" && grep -E -q -e " - FAIL - \[[^]]*$SUITE\.$CASE\]" "$OUT/twister-$T.log"; then
			echo "$V on $P: the named case failed, as required: $(grep -E -e " - FAIL - \[[^]]*$SUITE\.$CASE\]" "$OUT/twister-$T.log" | head -1)"
		else
			echo "$V on $P: the named case did not fail (twister exit $RC): $NAMED"
			FAILED="$FAILED $V/$P"
		fi
	done
done
if [ -z "$FAILED" ]; then
	echo "RESULT PASS"
	exit 0
fi
echo "RESULT FAIL$FAILED"
exit 1
