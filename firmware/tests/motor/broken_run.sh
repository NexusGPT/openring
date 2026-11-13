#!/bin/bash
# broken_run.sh: proof that the suites of tests/motor can fail. Runs inside the ring-os-toolchain container, firmware at
# /ws/firmware.
#
# Usage, from the Mac: RING_REMOTE_SRC=/root/ring-os/src-u-motor sh firmware/tools/remote.sh u-motor "bash tests/motor/broken_run.sh"
# (tools/unit_run.sh tests/motor runs it too.) Optional arguments: a list of variants, a list of boards.
#
# For each variant of broken_edit.py (5: mh_cuts_m1 vibration_mutes_mw m2_gap_100 edge_late allowance_5ms) it copies modules/ring_motor to the output folder,
# makes the one fault in the copy, runs the suites against the copy with west twister on native_sim and on the
# simulated ring chip (nrf54lm20bsim/nrf54lm20a/cpuapp), and passes only when, on each board, the suites ran and the
# one named case failed (a build error or a timeout does not count). The real files are not touched.
# Last line: "RESULT PASS" or "RESULT FAIL <what>".

set -u
FW=$(cd "$(dirname "$0")/../.." && pwd)
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-motor-broken}
VARIANTS="mh_cuts_m1 vibration_mutes_mw m2_gap_100 edge_late allowance_5ms"
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
	D=$OUT/broken_ring_motor_$V
	rm -rf "$D"
	cp -r "$FW/modules/ring_motor" "$D"
	CASE=$(python3 -B -I "$FW/tests/motor/broken_edit.py" "$V" "$D") || {
		echo "RESULT FAIL the edit of $V could not be made"
		exit 1
	}
	diff -u -r "$FW/modules/ring_motor" "$D" > "$OUT/broken_$V.diff"
	cat "$OUT/broken_$V.diff"
	if [ ! -s "$OUT/broken_$V.diff" ]; then
		echo "RESULT FAIL the edit of $V changed nothing"
		exit 1
	fi
	for P in $BOARDS; do
		T=$V-$(echo "$P" | tr '/' '_')
		west twister -T "$FW/tests/motor" -p "$P" -O "$OUT/twister-$T" --inline-logs -v \
			--extra-args RING_MOTOR_DIR="$D" > "$OUT/twister-$T.log" 2>&1
		RC=$?
		grep -E "FAIL|PASS|passed|failed|Assertion|assert" "$OUT/twister-$T.log" | head -60
		echo "twister exit code on the broken copy $V, $P: $RC (log $OUT/twister-$T.log)"
		case "$CASE" in
		BUILD:*)
			MSG=${CASE#BUILD:}
			if [ $RC -ne 0 ] && grep -q -F "$MSG" "$OUT/twister-$T.log" && ! grep -q -F "PROJECT EXECUTION" "$OUT/twister-$T.log"; then
				echo "$V on $P: the build failed at the assertion, as required: $(grep -F "$MSG" "$OUT/twister-$T.log" | head -1)"
			else
				echo "$V on $P: the build did not fail at the assertion (twister exit $RC): $MSG"
				FAILED="$FAILED $V/$P"
			fi
			;;
		*)
			NAMED="FAIL - [$CASE]"
			NFAIL=$(grep -c -F -e " - FAIL - [" "$OUT/twister-$T.log")
			if grep -q "PROJECT EXECUTION FAILED" "$OUT/twister-$T.log" && grep -q -F "$NAMED" "$OUT/twister-$T.log"; then
				echo "$V on $P: the named case failed, as required: $(grep -F "$NAMED" "$OUT/twister-$T.log" | head -1) (failed cases listed: $NFAIL)"
			else
				echo "$V on $P: the named case did not fail (twister exit $RC): $NAMED"
				FAILED="$FAILED $V/$P"
			fi
			;;
		esac
	done
done
if [ -z "$FAILED" ]; then
	echo "RESULT PASS"
	exit 0
fi
echo "RESULT FAIL$FAILED"
exit 1
