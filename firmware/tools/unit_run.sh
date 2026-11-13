#!/bin/bash
# unit_run.sh: the targeted run of one or more test folders (software step 6). Runs inside the ring-os-toolchain
# container, firmware at /ws/firmware.
#
# Usage, from the Mac (project folder):
#   RING_REMOTE_SRC=/root/ring-os/src-u-<name> sh firmware/tools/remote.sh u-<name> "bash tools/unit_run.sh tests/<name> [tests/<other> ...]"
#
# For the folders given (paths relative to the firmware folder, each holding a testcase.yaml):
#   1. twister on native_sim with every folder, then twister on nrf54lm20bsim/nrf54lm20a/cpuapp with every folder
#      (the same command form as stage 3 of tools/build_all.sh; twister keeps only the scenarios whose
#      platform_allow names the board);
#   2. each folder's broken_run.sh, when it has one (each broken copy must fail its own named case).
# Each part's output is kept in $OUT/<part>.log and shown. A part fails on a non-zero exit, and the twister part also
# when it ran no test configuration for a board while a folder allows that board.
# Last line: "UNIT PASS <folders>" (exit 0) or "UNIT FAIL <folders> <parts>" (exit 1).

set -u
FW=$(cd "$(dirname "$0")/.." && pwd)
JOBS=${RING_JOBS:-8}
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-unit}
BOARDS="native_sim nrf54lm20bsim/nrf54lm20a/cpuapp"

if [ $# -lt 1 ]; then
	echo "usage: bash tools/unit_run.sh tests/<name> [tests/<name> ...]"
	echo "UNIT FAIL (none) usage"
	exit 1
fi
FOLDERS="$*"
mkdir -p "$OUT"
FAILED=""

# run_part <name> <command...>: runs the command, shows and keeps its output, returns its exit code.
run_part() {
	local name=$1
	shift
	echo "=== part $name start $(date -u '+%Y-%m-%dT%H:%M:%SZ') log $OUT/$name.log"
	"$@" 2>&1 | tee "$OUT/$name.log"
	local rc=${PIPESTATUS[0]}
	echo "=== part $name end $(date -u '+%Y-%m-%dT%H:%M:%SZ') exit $rc"
	return "$rc"
}

ARGS=()
for d in $FOLDERS; do
	if [ ! -f "$FW/$d/testcase.yaml" ]; then
		echo "unit_run: $FW/$d/testcase.yaml not found"
		FAILED="$FAILED missing-$d"
		continue
	fi
	ARGS+=(-T "$FW/$d")
done

if [ ${#ARGS[@]} -gt 0 ]; then
	for b in $BOARDS; do
		tag=$(echo "$b" | tr '/' '_')
		# does any folder allow this board?
		want=0
		for d in $FOLDERS; do
			if [ -f "$FW/$d/testcase.yaml" ] && grep -q -F -- "$b" "$FW/$d/testcase.yaml"; then
				want=1
			fi
		done
		if ! run_part "tests-$tag" west twister "${ARGS[@]}" -p "$b" -O "$OUT/twister-$tag" -j "$JOBS" --inline-logs -v; then
			FAILED="$FAILED tests-$tag"
		elif [ $want -eq 1 ] && ! grep -q -E "[1-9][0-9]* of [0-9]+ executed test configurations passed" "$OUT/tests-$tag.log"; then
			echo "unit_run: no test configuration passed on $b"
			FAILED="$FAILED tests-$tag(none-ran)"
		fi
	done
fi

for d in $FOLDERS; do
	if [ -f "$FW/$d/broken_run.sh" ]; then
		n=$(basename "$d")
		if ! RING_OUT="$OUT/broken-$n" run_part "broken-$n" bash "$FW/$d/broken_run.sh"; then
			FAILED="$FAILED broken-$n"
		fi
	fi
done

if [ -z "$FAILED" ]; then
	echo "UNIT PASS $FOLDERS"
	exit 0
fi
echo "UNIT FAIL $FOLDERS$FAILED"
exit 1
