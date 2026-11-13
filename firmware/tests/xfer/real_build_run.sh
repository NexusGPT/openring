#!/bin/bash
# real_build_run.sh: builds tests/xfer/real_build (the real USB file against the kit, simulated drivers off) on native_sim.
# Runs inside the container, firmware at /ws/firmware. Prints only the error lines (no kit source lines).
# Usage: RING_REMOTE_SRC=/root/ring-os/src-u-xfer sh firmware/tools/remote.sh u-xfer "bash tests/xfer/real_build_run.sh"
set -u
FW=$(cd "$(dirname "$0")/../.." && pwd)
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-xfer-realbuild}
mkdir -p "$OUT"
west twister -T "$FW/tests/xfer" -s ring_xfer.real_build -p native_sim -O "$OUT/twister" -j 8 --inline-logs -v > "$OUT/twister.log" 2>&1
R=$?
echo "twister exit code: $R (log $OUT/twister.log)"
grep -E "error:|CMake Error|undefined reference|PASSED|FAILED|built|errored|failed" "$OUT/twister.log" | grep -v '^\[' | cut -c1-260 | head -60
echo "objects named rxf_hw_real.c.obj in the build: $(find "$OUT/twister" -name 'rxf_hw_real.c.obj' | wc -l)"
EXE=$(find "$OUT/twister" -name zephyr.exe | head -1)
if [ -n "$EXE" ]; then
	"$EXE" -stop_at=1 > "$OUT/run.log" 2>&1
	echo "run of the image (not a test): exit $? (log $OUT/run.log)"
	grep -E "rxf_start|rhw_usb" "$OUT/run.log" | cut -c1-200
fi
echo "REAL BUILD exit $R"
exit $R
