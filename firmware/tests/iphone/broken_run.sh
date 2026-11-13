#!/bin/bash
# broken_run.sh: proof that the logic suite of ring_iphone can fail. Runs inside the ring-os-toolchain container,
# firmware at /ws/firmware.
#
# Usage, from the Mac: sh firmware/tools/remote.sh iphone-broken "tests/iphone/broken_run.sh"
#
# For each variant of broken_edit.py (media_state: playing and paused swapped; clock_drift: a zone read re-applies the
# time at the uptime of now; clock_failed_read: a failed zone read counts as "no zone") it copies modules/ring_iphone to the
# output folder, makes the one fault in the copy, runs the suite against the copy with west twister on native_sim and on the
# simulated ring chip (nrf54lm20bsim/nrf54lm20a/cpuapp), and passes only when, on each board, the suite ran and the one named
# case failed (a build error or a timeout does not count). The real files are not touched.
# Last line: "RESULT PASS" or "RESULT FAIL <what>".

set -u
FW=$(cd "$(dirname "$0")/../.." && pwd)
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-iphone-broken}
mkdir -p "$OUT"
FAILED=""
for V in media_state clock_drift clock_failed_read; do
	echo "##### broken copy: $V"
	D=$OUT/broken_ring_iphone_$V
	rm -rf "$D"
	cp -r "$FW/modules/ring_iphone" "$D"
	CASE=$(python3 -B -I "$FW/tests/iphone/broken_edit.py" "$V" "$D") || {
		echo "RESULT FAIL the edit of $V could not be made"
		exit 1
	}
	diff -u "$FW/modules/ring_iphone" "$D" > "$OUT/broken_$V.diff"
	cat "$OUT/broken_$V.diff"
	if [ ! -s "$OUT/broken_$V.diff" ]; then
		echo "RESULT FAIL the edit of $V changed nothing"
		exit 1
	fi
	NAMED="FAIL - [ring_iphone.$CASE]"
	for P in native_sim nrf54lm20bsim/nrf54lm20a/cpuapp; do
		T=$V-$(echo "$P" | tr '/' '_')
		west twister -T "$FW/tests/iphone" -p "$P" -O "$OUT/twister-$T" --inline-logs -v \
			--extra-args RING_IPHONE_DIR="$D" > "$OUT/twister-$T.log" 2>&1
		RC=$?
		grep -E "FAIL|PASS|passed|failed|Assertion" "$OUT/twister-$T.log" | head -30
		echo "twister exit code on the broken copy $V, $P: $RC (log $OUT/twister-$T.log)"
		NFAIL=$(grep -c -F -e " - FAIL - [" "$OUT/twister-$T.log")
		if grep -q "PROJECT EXECUTION FAILED" "$OUT/twister-$T.log" && grep -q -F "$NAMED" "$OUT/twister-$T.log"; then
			echo "$V on $P: the named case failed, as required: $(grep -F "$NAMED" "$OUT/twister-$T.log" | head -1) (failed cases listed: $NFAIL)"
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
