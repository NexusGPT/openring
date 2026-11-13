#!/bin/bash
# broken_run.sh: proof that the logic suite of ring_relay can fail. Runs inside the ring-os-toolchain container, firmware at
# /ws/firmware.
#
# Usage, from the Mac: sh firmware/tools/remote.sh relay-broken "tests/relay/broken_run.sh"
#
# For each variant of broken_edit.py (13 of them) it copies the module the variant breaks (ring_relay or ring_inbox) to the output
# folder, makes the one fault in the copy, runs the suite against the copy with west twister on native_sim and on the simulated ring
# chip (nrf54lm20bsim/nrf54lm20a/cpuapp), and passes only when, on each board, the suite ran and the one named case failed (a
# build error or a timeout does not count). The real files are not touched.
# Last line: "RESULT PASS" or "RESULT FAIL <what>".

set -u
FW=$(cd "$(dirname "$0")/../.." && pwd)
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-relay-broken}
VARIANTS="put_early refused_changes_store text_cut_inside_char remove_ignored total_min_1 total_max_513 replace_moves_front store_17 flag_bit5_ok code7_not_enforced repeat_type_ok order_ignored category_above_11_refused"
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
	# which module does the variant break: read it from the edit table without making the edit
	MOD=$(python3 -B -I -c "import re,sys; t=open('$FW/tests/relay/broken_edit.py').read(); m=re.search(r'\"$V\": \(\"(ring_[a-z]+)\"', t); print(m.group(1) if m else '')")
	if [ -z "$MOD" ]; then
		echo "RESULT FAIL variant $V is not in broken_edit.py"
		exit 1
	fi
	D=$OUT/broken_${MOD}_$V
	rm -rf "$D"
	cp -r "$FW/modules/$MOD" "$D"
	INFO=$(python3 -B -I "$FW/tests/relay/broken_edit.py" "$V" "$D") || {
		echo "RESULT FAIL the edit of $V could not be made"
		exit 1
	}
	CASE=${INFO#* }
	diff -u "$FW/modules/$MOD" "$D" > "$OUT/broken_$V.diff"
	cat "$OUT/broken_$V.diff"
	if [ ! -s "$OUT/broken_$V.diff" ]; then
		echo "RESULT FAIL the edit of $V changed nothing"
		exit 1
	fi
	case "$MOD" in
	ring_relay) VAR=RING_RELAY_DIR ;;
	ring_inbox) VAR=RING_INBOX_DIR ;;
	esac
	NAMED="FAIL - [ring_relay.$CASE]"
	for P in $BOARDS; do
		T=$V-$(echo "$P" | tr '/' '_')
		west twister -T "$FW/tests/relay" -p "$P" -O "$OUT/twister-$T" --inline-logs -v \
			--extra-args $VAR="$D" > "$OUT/twister-$T.log" 2>&1
		RC=$?
		grep -E "FAIL|PASS|passed|failed|Assertion" "$OUT/twister-$T.log" | head -30
		echo "twister exit code on the broken copy $V, $P: $RC (log $OUT/twister-$T.log)"
		NFAIL=$(grep -c -F -e " - FAIL - [" "$OUT/twister-$T.log")
		if grep -q "PROJECT EXECUTION FAILED" "$OUT/twister-$T.log" && grep -q -F "$NAMED" "$OUT/twister-$T.log"; then
			echo "$V on $P: the named case failed, as required: $(grep -F "$NAMED" "$OUT/twister-$T.log" | head -1) (failed cases listed: $NFAIL)"
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
