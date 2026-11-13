#!/bin/bash
# broken_run.sh: proof that the suites of tests/sys can fail. Runs inside the ring-os-toolchain container, firmware at
# /ws/firmware.
#
# Usage, from the Mac: RING_REMOTE_SRC=/root/ring-os/src-u-sys sh firmware/tools/remote.sh u-sys "bash tests/sys/broken_run.sh"
# (tools/unit_run.sh tests/sys runs it too.) Optional arguments: a list of variants, a list of boards.
#
# For each variant of broken_edit.py (8: size_999425_ok end_off_by_one writes_slot0 selftest_31s allowed_at_30
# feed_without_progress crash_copied_twice guess_marked_set) it copies modules/ring_sys to the output folder, makes the one
# fault in the copy, runs the suites against the copy with west twister on native_sim and on the simulated ring chip
# (nrf54lm20bsim/nrf54lm20a/cpuapp), and passes only when, on each board, the suites ran and the one named case failed
# (a build error or a timeout does not count). It lists every case that failed with it. The real files are not touched.
# Last line: "RESULT PASS" or "RESULT FAIL <what>".

set -u
FW=$(cd "$(dirname "$0")/../.." && pwd)
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-sys-broken}
VARIANTS="size_999425_ok end_off_by_one writes_slot0 selftest_31s allowed_at_30 feed_without_progress crash_copied_twice guess_marked_set"
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
	D=$OUT/broken_ring_sys_$V
	rm -rf "$D"
	cp -r "$FW/modules/ring_sys" "$D"
	CASE=$(python3 -B -I "$FW/tests/sys/broken_edit.py" "$V" "$D") || {
		echo "RESULT FAIL the edit of $V could not be made"
		exit 1
	}
	diff -u -r "$FW/modules/ring_sys" "$D" > "$OUT/broken_$V.diff"
	cat "$OUT/broken_$V.diff"
	if [ ! -s "$OUT/broken_$V.diff" ]; then
		echo "RESULT FAIL the edit of $V changed nothing"
		exit 1
	fi
	NAMED="FAIL - [$CASE]"
	for P in $BOARDS; do
		T=$V-$(echo "$P" | tr '/' '_')
		west twister -T "$FW/tests/sys" -p "$P" -O "$OUT/twister-$T" --inline-logs -v \
			--extra-args RING_SYS_DIR="$D" > "$OUT/twister-$T.log" 2>&1
		RC=$?
		grep -E "FAIL|PASS|passed|failed|Assertion" "$OUT/twister-$T.log" | head -60
		echo "twister exit code on the broken copy $V, $P: $RC (log $OUT/twister-$T.log)"
		NFAIL=$(grep -c -F -e " - FAIL - [" "$OUT/twister-$T.log")
		FAILED_CASES=$(grep -o -E "FAIL - \[[A-Za-z0-9_.]+\]" "$OUT/twister-$T.log" | sort -u | tr '\n' ' ')
		if grep -q "PROJECT EXECUTION FAILED" "$OUT/twister-$T.log" && grep -q -F "$NAMED" "$OUT/twister-$T.log"; then
			echo "$V on $P: the named case failed, as required: $(grep -F "$NAMED" "$OUT/twister-$T.log" | head -1)"
			echo "$V on $P: cases that failed (distinct): $FAILED_CASES (lines with FAIL: $NFAIL)"
		else
			echo "$V on $P: the named case did not fail (twister exit $RC): $NAMED"
			echo "$V on $P: cases that failed (distinct): $FAILED_CASES"
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
