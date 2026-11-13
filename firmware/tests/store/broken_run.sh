#!/bin/bash
# broken_run.sh: proof that the suites of tests/store can fail. Runs inside the ring-os-toolchain container, firmware
# at /ws/firmware.
#
# Usage, from the Mac: RING_REMOTE_SRC=/root/ring-os/src-u-store sh firmware/tools/remote.sh u-store "bash tests/store/broken_run.sh"
# (tools/unit_run.sh tests/store runs it too.)
#
# For each of the 11 variants of broken_edit.py it copies modules/ring_store to the output folder, makes the one fault
# in the copy, runs the whole suite against the copy with west twister on native_sim and on the simulated ring chip
# (nrf54lm20bsim/nrf54lm20a/cpuapp), and passes only when, on each board, the build worked, every test case ran, the one
# named case failed, and no case failed that is not on the variant's list of cases that run the same broken code
# (a build error, a timeout or another failing case does not count). The real files are not touched.
# Last line: "RESULT PASS" or "RESULT FAIL <what>".

set -u
FW=$(cd "$(dirname "$0")/../.." && pwd)
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-store-broken}
VARIANTS="hdr_crc_512 digest_big_endian sb_older_wins lba_no_wrap scan_accepts_gap sfull_17 delete_frees_middle delete_without_confirm two_tries init_before_rail log_drops_newest"
BOARDS="native_sim nrf54lm20bsim/nrf54lm20a/cpuapp"
if [ -n "${1:-}" ]; then
	VARIANTS=$1
fi
if [ -n "${2:-}" ]; then
	BOARDS=$2
fi
mkdir -p "$OUT"
NCASES=$(cat "$FW"/tests/store/src/test_*.c | grep -c '^ZTEST(')
FAILED=""

run_board() {	# run_board <variant> <board> <copy>
	local V=$1 P=$2 D=$3 T
	T=$V-$(echo "$P" | tr '/' '_')
	west twister -T "$FW/tests/store" -p "$P" -O "$OUT/twister-$T" --inline-logs -v \
		--extra-args RING_STORE_DIR="$D" > "$OUT/twister-$T.log" 2>&1
	echo $? > "$OUT/twister-$T.exit"
}

for V in $VARIANTS; do
	echo "##### broken copy: $V"
	D=$OUT/broken_ring_store_$V
	rm -rf "$D"
	cp -r "$FW/modules/ring_store" "$D"
	EDIT=$(python3 -B -I "$FW/tests/store/broken_edit.py" "$V" "$D") || {
		echo "RESULT FAIL the edit of $V could not be made"
		exit 1
	}
	CASE=$(echo "$EDIT" | sed -n 1p)
	ALSO=$(echo "$EDIT" | sed -n 2p)
	[ "$ALSO" = "-" ] && ALSO=""
	diff -u -r "$FW/modules/ring_store" "$D" > "$OUT/broken_$V.diff"
	cat "$OUT/broken_$V.diff"
	if [ ! -s "$OUT/broken_$V.diff" ]; then
		echo "RESULT FAIL the edit of $V changed nothing"
		exit 1
	fi
	for P in $BOARDS; do
		run_board "$V" "$P" "$D" &
	done
	wait
	for P in $BOARDS; do
		T=$V-$(echo "$P" | tr '/' '_')
		L=$OUT/twister-$T.log
		RC=$(cat "$OUT/twister-$T.exit")
		grep -E "FAIL|PASS|passed|failed|Assertion" "$L" | head -60
		echo "twister exit code on the broken copy $V, $P: $RC (log $L)"
		GOT=$(grep -o -E ' - FAIL - \[[A-Za-z0-9_.]+\]' "$L" | sed -E 's/.*\[(.*)\]/\1/' | sort -u | tr '\n' ' ')
		RAN=$(grep -o -E '(PASS|FAIL) - test_[A-Za-z0-9_]+' "$L" | sed -E 's/.* - //' | sort -u | wc -l | tr -d ' ')
		EXTRA=""
		for c in $GOT; do
			if [ "$c" != "$CASE" ] && ! echo " $ALSO " | grep -q -F " $c "; then
				EXTRA="$EXTRA $c"
			fi
		done
		if ! grep -q "PROJECT EXECUTION FAILED" "$L" || ! echo " $GOT" | grep -q -F " $CASE "; then
			echo "$V on $P: the named case did not fail (twister exit $RC): $CASE"
			FAILED="$FAILED $V/$P"
		elif [ -n "$EXTRA" ]; then
			echo "$V on $P: the named case failed but so did other cases that are not on the list:$EXTRA"
			FAILED="$FAILED $V/$P(extra:$EXTRA)"
		elif [ "$RAN" -lt "$NCASES" ]; then
			echo "$V on $P: only $RAN of $NCASES cases ran"
			FAILED="$FAILED $V/$P(ran-$RAN)"
		else
			echo "$V on $P: the named case failed, as required: $CASE (cases that failed: ${GOT:-none}; $RAN of $NCASES cases ran)"
		fi
	done
done
if [ -z "$FAILED" ]; then
	echo "RESULT PASS"
	exit 0
fi
echo "RESULT FAIL$FAILED"
exit 1
