#!/bin/bash
# broken_run.sh: proof that the power suites can fail and that the build assertions of CHARGE_CURRENT hold. Runs inside
# the ring-os-toolchain container, firmware at /ws/firmware.
#
# Usage, from the Mac: RING_REMOTE_SRC=/root/ring-os/src-u-power sh firmware/tools/remote.sh u-power "bash tests/power/broken_run.sh [variants] [boards]"
# (tools/unit_run.sh tests/power runs it too, with every variant.)
#
# For each variant of broken_edit.py (10 broken copies and the 5 build copies cc_*) it copies modules/ring_power into a
# folder of the output (beside a link to ring_core, whose header the copy needs), makes the one fault in the copy, runs
# the suite against the copy with west twister on native_sim and on the simulated ring chip
# (nrf54lm20bsim/nrf54lm20a/cpuapp), and passes only when, on each board,
#  - a CASE variant: the suite ran, the one named case failed and no other case failed (a build error or a timeout
#    does not count);
#  - a BUILD variant: the build failed and its log holds the variant's own assertion message.
# The real files are not touched. Last line: "RESULT PASS" or "RESULT FAIL <what>".

set -u
FW=$(cd "$(dirname "$0")/../.." && pwd)
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-power-broken}
VARIANTS=$(python3 -B -I "$FW/tests/power/broken_edit.py" --list)
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
	D=$OUT/broken_$V
	rm -rf "$D"
	mkdir -p "$D"
	cp -r "$FW/modules/ring_power" "$D/ring_power"
	ln -s "$FW/modules/ring_core" "$D/ring_core"
	WHAT=$(python3 -B -I "$FW/tests/power/broken_edit.py" "$V" "$D/ring_power") || {
		echo "RESULT FAIL the edit of $V could not be made"
		exit 1
	}
	diff -u -r "$FW/modules/ring_power" "$D/ring_power" > "$OUT/broken_$V.diff"
	cat "$OUT/broken_$V.diff"
	if [ ! -s "$OUT/broken_$V.diff" ]; then
		echo "RESULT FAIL the edit of $V changed nothing"
		exit 1
	fi
	KIND=${WHAT%% *}
	REST=${WHAT#* }
	for P in $BOARDS; do
		T=$V-$(echo "$P" | tr '/' '_')
		west twister -T "$FW/tests/power" -p "$P" -O "$OUT/twister-$T" --inline-logs -v \
			--extra-args RING_POWER_DIR="$D/ring_power" > "$OUT/twister-$T.log" 2>&1
		RC=$?
		grep -E "FAIL|PASS|passed|failed|Assertion|CHARGE_CURRENT" "$OUT/twister-$T.log" | head -60
		echo "twister exit code on the broken copy $V, $P: $RC (log $OUT/twister-$T.log)"
		if [ "$KIND" = "CASE" ]; then
			NAMED="FAIL - [$REST]"
			NFAIL=$(grep -c -F -e " - FAIL - [" "$OUT/twister-$T.log")
			if grep -q "PROJECT EXECUTION FAILED" "$OUT/twister-$T.log" && grep -q -F "$NAMED" "$OUT/twister-$T.log" \
				&& [ "$NFAIL" -eq 1 ]; then
				echo "$V on $P: the named case failed, and only it, as required: $(grep -F "$NAMED" "$OUT/twister-$T.log" | head -1) (failed cases listed: $NFAIL)"
			else
				echo "$V on $P: not as required (named case $NAMED, twister exit $RC, failed cases listed: $NFAIL)"
				FAILED="$FAILED $V/$P"
			fi
		else
			MSGS=$(grep -c -F "$REST" "$OUT/twister-$T.log")
			if [ "$RC" -ne 0 ] && [ "$MSGS" -gt 0 ] && ! grep -q "PROJECT EXECUTION" "$OUT/twister-$T.log"; then
				echo "$V on $P: the build failed with its own message, as required: \"$REST\" (lines in the log: $MSGS)"
			else
				echo "$V on $P: not as required (message \"$REST\" lines: $MSGS, twister exit $RC)"
				FAILED="$FAILED $V/$P"
			fi
			echo "CHARGE_CURRENT messages present in that log, for the record:"
			grep -o -E "CHARGE_CURRENT is [a-z ]+[0-9,]*( uA| set)?" "$OUT/twister-$T.log" | sort | uniq -c
		fi
	done
done
if [ -z "$FAILED" ]; then
	echo "RESULT PASS"
	exit 0
fi
echo "RESULT FAIL$FAILED"
exit 1
