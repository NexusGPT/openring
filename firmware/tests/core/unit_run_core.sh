#!/bin/bash
# unit_run_core.sh: the targeted run of unit U1 (core6), until tools/unit_run.sh exists. Runs inside the ring-os-toolchain
# container, firmware at /ws/firmware.
#
# Usage, from the Mac:
#   RING_REMOTE_SRC=/root/ring-os/src-u-core6 sh firmware/tools/remote.sh u-core6 "bash tests/core/unit_run_core.sh tests/core tests/screens tests/control tests/relay"
#
# For each test folder: west twister on native_sim and on the simulated ring chip (nrf54lm20bsim/nrf54lm20a/cpuapp), then the
# folder's broken_run.sh when it has one. Last line: "UNIT PASS <folders>" or "UNIT FAIL <folders> <parts>".

set -u
FW=$(cd "$(dirname "$0")/../.." && pwd)
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-unit}
JOBS=${RING_JOBS:-8}
BOARDS="native_sim nrf54lm20bsim/nrf54lm20a/cpuapp"
if [ $# -eq 0 ]; then
	echo "UNIT FAIL (no folder named)"
	exit 2
fi
FOLDERS="$*"
mkdir -p "$OUT"
FAILED=""
for F in "$@"; do
	N=$(echo "$F" | tr '/' '_')
	if [ ! -f "$FW/$F/testcase.yaml" ]; then
		echo "no testcase.yaml in $FW/$F"
		FAILED="$FAILED $F(no-testcase)"
		continue
	fi
	mkdir -p "$OUT/pictures-$N"
	for P in $BOARDS; do
		T=$N-$(echo "$P" | tr '/' '_')
		echo "=== twister $F on $P start $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
		RING_PICS="$OUT/pictures-$N" west twister -T "$FW/$F" -p "$P" -O "$OUT/twister-$T" -j "$JOBS" --inline-logs -v > "$OUT/twister-$T.log" 2>&1
		RC=$?
		grep -E "executed test (configurations|cases)|FAIL|ERROR" "$OUT/twister-$T.log" | head -20
		echo "=== twister $F on $P exit $RC (log $OUT/twister-$T.log)"
		if [ $RC -ne 0 ]; then
			FAILED="$FAILED $F/$P"
		fi
	done
	if [ -f "$FW/$F/broken_run.sh" ]; then
		echo "=== broken copies of $F start $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
		RING_OUT="$OUT/broken-$N" bash "$FW/$F/broken_run.sh" > "$OUT/broken-$N.log" 2>&1
		RC=$?
		tail -3 "$OUT/broken-$N.log"
		echo "=== broken copies of $F exit $RC (log $OUT/broken-$N.log)"
		if [ $RC -ne 0 ]; then
			FAILED="$FAILED $F/broken"
		fi
	fi
done
if [ -z "$FAILED" ]; then
	echo "UNIT PASS $FOLDERS"
	exit 0
fi
echo "UNIT FAIL $FOLDERS$FAILED"
exit 1
