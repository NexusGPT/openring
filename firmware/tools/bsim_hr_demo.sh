#!/bin/bash
# bsim_hr_demo.sh: one two-device BabbleSim run with stock Zephyr code, to
# prove the simulated radio works in this workspace. Runs in the container.
#
# Usage, from the Mac: sh firmware/tools/remote.sh bsim-hr "tools/bsim_hr_demo.sh [board]"
#   board: default nrf54lm20bsim/nrf54lm20a/cpuapp
#
# Builds zephyr/samples/bluetooth/peripheral_hr and central_hr for the board,
# then runs both against the BabbleSim 2.4 GHz phy for 10 simulated seconds
# (device 0 = peripheral, device 1 = central), as in Zephyr's nrf52_bsim.rst
# lines 158-161. Passes when the central's log shows a heart-rate
# notification ("[NOTIFICATION]" line written by central_hr's notify_func).
# Last line: "RESULT PASS" or "RESULT FAIL <what>".

set -u
BOARD=${1:-nrf54lm20bsim/nrf54lm20a/cpuapp}
JOBS=${RING_JOBS:-8}
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID}
Z=/ws/zephyr
SIM_ID="ring_hr_$$"
mkdir -p "$OUT"

for s in peripheral_hr central_hr; do
	echo "=== build $s for $BOARD, log $OUT/build-$s.log"
	if ! west build -p always -b "$BOARD" --no-sysbuild -d "$OUT/$s" -o=-j"$JOBS" "$Z/samples/bluetooth/$s" > "$OUT/build-$s.log" 2>&1; then
		tail -n 40 "$OUT/build-$s.log"
		echo "RESULT FAIL build $s"
		exit 1
	fi
	echo "build $s ok"
done

echo "=== run, simulation $SIM_ID, 10 simulated seconds, $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
"$OUT/peripheral_hr/zephyr/zephyr.exe" -s="$SIM_ID" -d=0 > "$OUT/run-peripheral_hr.log" 2>&1 &
P0=$!
"$OUT/central_hr/zephyr/zephyr.exe" -s="$SIM_ID" -d=1 > "$OUT/run-central_hr.log" 2>&1 &
P1=$!
(cd "$BSIM_OUT_PATH/bin" && ./bs_2G4_phy_v1 -s="$SIM_ID" -D=2 -sim_length=10e6) > "$OUT/run-phy.log" 2>&1 &
P2=$!
wait $P2
RC_PHY=$?
wait $P0
RC0=$?
wait $P1
RC1=$?
echo "exit codes: phy $RC_PHY, peripheral $RC0, central $RC1"

for f in run-phy run-peripheral_hr run-central_hr; do
	echo "--- $OUT/$f.log (first 40 lines)"
	head -n 40 "$OUT/$f.log"
done
N=$(grep -c "NOTIFICATION" "$OUT/run-central_hr.log")
echo "central_hr notification lines: $N"
grep -m 3 "NOTIFICATION" "$OUT/run-central_hr.log"
if [ "$RC_PHY" -eq 0 ] && [ "$N" -gt 0 ]; then
	echo "RESULT PASS"
	exit 0
fi
echo "RESULT FAIL phy exit $RC_PHY, notifications $N"
exit 1
