#!/bin/bash
# broken_run.sh: proof that the logic suite of ring_control can fail. Runs inside the
# ring-os-toolchain container, firmware at /ws/firmware.
#
# Usage, from the Mac: sh firmware/tools/remote.sh control-broken "tests/control/broken_run.sh"
#
# Copies modules/ring_control to the output folder, changes one key in the copy's mode table (presenter, right: Right Arrow becomes Left Arrow), runs the suite against the copy
# with west twister on native_sim and on the simulated ring chip
# (nrf54lm20bsim/nrf54lm20a/cpuapp), and passes only when, on each board, the suite ran and
# the one named case failed (a build error or a timeout does not count). The real files are not
# touched. Last line: "RESULT PASS" or "RESULT FAIL <what>".

set -u
FW=$(cd "$(dirname "$0")/../.." && pwd)
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-control-broken}
mkdir -p "$OUT"
rm -rf "$OUT/broken_ring_control"
cp -r "$FW/modules/ring_control" "$OUT/broken_ring_control"
F=$OUT/broken_ring_control/include/ring_control/rctl_modes.h
sed -i 's/\[RCTL_RIGHT\]  = RCTL_E_KEY(RCTL_K_RIGHT_ARROW),/[RCTL_RIGHT]  = RCTL_E_KEY(RCTL_K_LEFT_ARROW),/' "$F"
diff -u "$FW/modules/ring_control/include/ring_control/rctl_modes.h" "$F" > "$OUT/broken.diff"
cat "$OUT/broken.diff"
if [ ! -s "$OUT/broken.diff" ]; then
	echo "RESULT FAIL the edit changed nothing"
	exit 1
fi
NAMED="FAIL - [ring_control.test_mode_tables]"
FAILED=""
for P in native_sim nrf54lm20bsim/nrf54lm20a/cpuapp; do
	T=$(echo "$P" | tr '/' '_')
	west twister -T "$FW/tests/control" -p "$P" -O "$OUT/twister-$T" --inline-logs -v \
		--extra-args RING_CONTROL_DIR="$OUT/broken_ring_control" > "$OUT/twister-$T.log" 2>&1
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
