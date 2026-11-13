#!/bin/bash
# broken_run.sh: proof that the suites of tests/factory can fail. Runs inside the ring-os-toolchain container, firmware at
# /ws/firmware.
#
# Usage, from the Mac: RING_REMOTE_SRC=/root/ring-os/src-u-factory sh firmware/tools/remote.sh u-factory "bash tests/factory/broken_run.sh"
# (tools/unit_run.sh tests/factory runs it too.) Optional arguments: a list of variants, a list of boards.
#
# For each variant of broken_edit.py (10: flag_ignored x11_accepted run_999 mic_without_sign centre_records vbat_read_at_0
# store_lba_4097 type2_left beacon_connectable beacon_after_ship) it copies the module the variant edits (ring_factory;
# ring_rhw for store_lba_4097) to the output folder, makes the one fault in the copy, runs the suites against the copy
# with west twister on native_sim and on the simulated ring chip (nrf54lm20bsim/nrf54lm20a/cpuapp), and passes only when,
# on each board, the suites ran and the one named case failed (a build error or a timeout does not count). The cases that
# fail with it are listed. The real files are not touched.
# Last line: "RESULT PASS" or "RESULT FAIL <what>".

set -u
FW=$(cd "$(dirname "$0")/../.." && pwd)
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-factory-broken}
VARIANTS="flag_ignored x11_accepted run_999 mic_without_sign centre_records vbat_read_at_0 store_lba_4097 type2_left beacon_connectable beacon_after_ship"
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
	MOD=$(python3 -B -I "$FW/tests/factory/broken_edit.py" --module "$V") || {
		echo "RESULT FAIL unknown variant $V"
		exit 1
	}
	D=$OUT/broken_${MOD}_$V
	rm -rf "$D"
	cp -r "$FW/modules/$MOD" "$D"
	CASE=$(python3 -B -I "$FW/tests/factory/broken_edit.py" "$V" "$D") || {
		echo "RESULT FAIL the edit of $V could not be made"
		exit 1
	}
	diff -u -r "$FW/modules/$MOD" "$D" > "$OUT/broken_$V.diff"
	cat "$OUT/broken_$V.diff"
	if [ ! -s "$OUT/broken_$V.diff" ]; then
		echo "RESULT FAIL the edit of $V changed nothing"
		exit 1
	fi
	if [ "$MOD" = "ring_rhw" ]; then
		VAR=RING_RHW_DIR
	else
		VAR=RING_FACTORY_DIR
	fi
	for P in $BOARDS; do
		T=$V-$(echo "$P" | tr '/' '_')
		west twister -T "$FW/tests/factory" -p "$P" -O "$OUT/twister-$T" --inline-logs -v \
			--extra-args $VAR="$D" > "$OUT/twister-$T.log" 2>&1
		RC=$?
		grep -E "FAIL|PASS|passed|failed|Assertion|assert" "$OUT/twister-$T.log" | head -60
		echo "twister exit code on the broken copy $V, $P: $RC (log $OUT/twister-$T.log)"
		NAMED="FAIL - [$CASE]"
		NFAIL=$(grep -c -F -e " - FAIL - [" "$OUT/twister-$T.log")
		if grep -q "PROJECT EXECUTION FAILED" "$OUT/twister-$T.log" && grep -q -F "$NAMED" "$OUT/twister-$T.log"; then
			echo "$V on $P: the named case failed, as required: $(grep -F "$NAMED" "$OUT/twister-$T.log" | head -1) (failed cases listed: $NFAIL)"
			echo "$V on $P: cases that failed: $(grep -F -e " - FAIL - [" "$OUT/twister-$T.log" | sed -e 's/.*FAIL - \[//' -e 's/\].*//' | sort -u | tr '\n' ' ')"
		else
			echo "$V on $P: the named case did not fail (twister exit $RC): $NAMED"
			FAILED="$FAILED $V/$P"
		fi
	done
done
if [ -z "$FAILED" ]; then
	echo "RESULT PASS"
	exit 0
fi
echo "RESULT FAIL$FAILED"
exit 1
