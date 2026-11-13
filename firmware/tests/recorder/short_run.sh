#!/bin/bash
# short_run.sh: the suites of tests/recorder alone (no broken copies). Runs inside the ring-os-toolchain container, firmware
# at /ws/firmware.
# Usage, from the Mac:
#   RING_REMOTE_SRC=/root/ring-os/src-u-join sh firmware/tools/remote.sh u-join "bash tests/recorder/short_run.sh [boards] [extra] [build]"
#   boards: "native_sim nrf54lm20bsim/nrf54lm20a/cpuapp" (default both); extra: cmake cache entries for twister's
#   --extra-args, separated by commas, for example CONFIG_RING_FACTORY=n,RT_SUITE=test_boot ("-" = none);
#   build: "build" = build only (twister -b).
set -u
FW=$(cd "$(dirname "$0")/../.." && pwd)
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-recorder-short}
BOARDS=${1:-native_sim nrf54lm20bsim/nrf54lm20a/cpuapp}
EXTRA=${2:--}
MODE=${3:-run}
mkdir -p "$OUT"
ARGS=()
if [ "$EXTRA" != "-" ]; then
	for X in $(echo "$EXTRA" | tr ',' ' '); do
		ARGS+=(--extra-args "$X")
	done
fi
if [ "$MODE" = "build" ]; then
	ARGS+=(-b)
fi
RC=0
for P in $BOARDS; do
	T=$(echo "$P" | tr '/' '_')
	west twister -T "$FW/tests/recorder" -p "$P" -O "$OUT/twister-$T" -j 8 --inline-logs -v "${ARGS[@]}" > "$OUT/twister-$T.log" 2>&1
	R=$?
	echo "twister exit code on $P: $R (log $OUT/twister-$T.log)"
	grep -E "FAIL|PASS|passed|failed|Assertion|error:|CMake Error|warning:|ROW|RULES|RAILS|SIGN-1|stop|start|close|open order|boot|frame hash|M1 action|ship|unmount|SCR_CHARGING|T-MIC|T-SIGN|latch|HFXO|close frames" "$OUT/twister-$T.log" | cut -c1-300 | head -400
	[ "$R" -ne 0 ] && RC=1
done
echo "SHORT RUN exit $RC"
exit $RC
