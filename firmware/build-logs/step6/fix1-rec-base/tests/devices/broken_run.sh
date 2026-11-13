#!/bin/bash
# broken_run.sh: proof that the logic suite of ring_devices can fail. Runs inside the
# ring-os-toolchain container, firmware at /ws/firmware.
#
# Usage, from the Mac: sh firmware/tools/remote.sh devices-broken "tests/devices/broken_run.sh"
#
# Copies modules/ring_devices to the output folder, breaks the switch decision in the copy (a switch to an empty slot is allowed), runs the suite against the copy
# with west twister on native_sim and on the simulated ring chip
# (nrf54lm20bsim/nrf54lm20a/cpuapp), and passes only when, on each board, the suite ran and
# the one named case failed (a build error or a timeout does not count). The real files are not
# touched. Last line: "RESULT PASS" or "RESULT FAIL <what>".

set -u
FW=$(cd "$(dirname "$0")/../.." && pwd)
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-devices-broken}
mkdir -p "$OUT"
rm -rf "$OUT/broken_ring_devices"
cp -r "$FW/modules/ring_devices" "$OUT/broken_ring_devices"
F=$OUT/broken_ring_devices/src/rdev_logic.c
sed -i 's/return RDEV_SWITCH_REFUSE_EMPTY;/return RDEV_SWITCH_GO;/' "$F"
diff -u "$FW/modules/ring_devices/src/rdev_logic.c" "$F" > "$OUT/broken.diff"
cat "$OUT/broken.diff"
if [ ! -s "$OUT/broken.diff" ]; then
	echo "RESULT FAIL the edit changed nothing"
	exit 1
fi
NAMED="FAIL - [ring_devices.test_switch_decision]"
FAILED=""
for P in native_sim nrf54lm20bsim/nrf54lm20a/cpuapp; do
	T=$(echo "$P" | tr '/' '_')
	west twister -T "$FW/tests/devices" -p "$P" -O "$OUT/twister-$T" --inline-logs -v \
		--extra-args RING_DEVICES_DIR="$OUT/broken_ring_devices" > "$OUT/twister-$T.log" 2>&1
	RC=$?
	grep -E "FAIL|PASS|passed|failed|Assertion" "$OUT/twister-$T.log" | head -30
	echo "twister exit code on the broken copy, $P: $RC (log $OUT/twister-$T.log)"
	NFAIL=$(grep -c -F -e " - FAIL - [" "$OUT/twister-$T.log")
	if grep -q "PROJECT EXECUTION FAILED" "$OUT/twister-$T.log" && grep -q -F "$NAMED" "$OUT/twister-$T.log"; then
		echo "$P: the named case failed, as required: $(grep -F "$NAMED" "$OUT/twister-$T.log" | head -1) (failed cases listed: $NFAIL)"
	else
		echo "$P: the named case did not fail (twister exit $RC): $NAMED"
		FAILED="$FAILED $P"
	fi
done
if [ -z "$FAILED" ]; then
	echo "RESULT PASS"
	exit 0
fi
echo "RESULT FAIL$FAILED"
exit 1
