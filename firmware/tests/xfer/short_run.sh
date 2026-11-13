#!/bin/bash
# short_run.sh: the suites of tests/xfer alone (no broken copies), on both simulated targets. Runs inside the
# ring-os-toolchain container, firmware at /ws/firmware.
# Usage, from the Mac: RING_REMOTE_SRC=/root/ring-os/src-u-xfer sh firmware/tools/remote.sh u-xfer "bash tests/xfer/short_run.sh"
set -u
FW=$(cd "$(dirname "$0")/../.." && pwd)
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-xfer-short}
mkdir -p "$OUT"
RC=0
for P in native_sim nrf54lm20bsim/nrf54lm20a/cpuapp; do
	T=$(echo "$P" | tr '/' '_')
	west twister -T "$FW/tests/xfer" -p "$P" -O "$OUT/twister-$T" -j 8 --inline-logs -v > "$OUT/twister-$T.log" 2>&1
	R=$?
	echo "twister exit code on $P: $R (log $OUT/twister-$T.log)"
	grep -E "FAIL|PASS|passed|failed|Assertion|error:|CMake Error|warning:" "$OUT/twister-$T.log" | cut -c1-300 | head -150
	[ "$R" -ne 0 ] && RC=1
done
echo "SHORT RUN exit $RC"
exit $RC
