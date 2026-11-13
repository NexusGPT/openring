#!/bin/bash
# broken_run.sh: proof that the screens suite can fail. Runs inside the ring-os-toolchain container, firmware at /ws/firmware.
#
# Usage, from the Mac: sh firmware/tools/remote.sh screens-broken "tests/screens/broken_run.sh"
#                      tests/screens/broken_run.sh <variant>      one variant
#
# For each variant (broken_edit.py): copies modules/ring_screens to the output folder, makes ONE named fault in the copy, runs
# the suite against the copy with west twister and passes only when the suite ran (it was built and started) and the one named
# ztest case failed: the line " FAIL - <case> in " is in the log (a build error, a crash or a timeout does not count).
# rsign_dark (R-SIGN at the table layer) and, since software step 6, ilim_dark_in_recording, factory_wrong_colour and start_in_hold_full_bright run on native_sim and on
# the simulated ring chip; the others on native_sim.
# The real files are not touched. Last line: "RESULT PASS" or "RESULT FAIL <what>".

set -u
FW=$(cd "$(dirname "$0")/../.." && pwd)
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-screens-broken}
VARIANTS="rsign_dark rsign_blank_panel lock_open double_ignored long_closes_session down_stuck dismiss_key passkey_not_drawn dim_brightness_zero blank_after_draw wrong_passkey_digit wrong_timer_digit no_title_app sign_on_caller_thread sign_timeout_keeps_request power_off_outside_standby ilim_dark_in_recording factory_wrong_colour start_in_hold_full_bright"
[ -n "${1:-}" ] && VARIANTS=$1
mkdir -p "$OUT"
FAILED=""
for v in $VARIANTS; do
	echo "##### broken copy: $v"
	mkdir -p "$OUT/$v"
	if ! info=$(python3 -I "$FW/tests/screens/broken_edit.py" "$v" "$FW/modules" "$OUT/$v" 2> "$OUT/$v/edit.log"); then
		cat "$OUT/$v/edit.log"
		echo "RESULT FAIL the edit for $v could not be made"
		FAILED="$FAILED $v(edit)"
		continue
	fi
	cat "$OUT/$v/edit.log"
	diff -u "$FW/modules/ring_screens/$(sed -n 's/^edited //p' "$OUT/$v/edit.log")" "$OUT/$v/ring_screens/$(sed -n 's/^edited //p' "$OUT/$v/edit.log")" > "$OUT/$v/broken.diff"
	cat "$OUT/$v/broken.diff"
	if [ ! -s "$OUT/$v/broken.diff" ]; then
		echo "the edit for $v changed nothing"
		FAILED="$FAILED $v(nodiff)"
		continue
	fi
	NAME=$(echo "$info" | sed -n 's/^EXPECT=//p')
	BOARDS="native_sim"
	case "$v" in rsign_dark|ilim_dark_in_recording|factory_wrong_colour|start_in_hold_full_bright) BOARDS="native_sim nrf54lm20bsim/nrf54lm20a/cpuapp" ;; esac
	for P in $BOARDS; do
		T=$(echo "$P" | tr '/' '_')
		west twister -T "$FW/tests/screens" -p "$P" -O "$OUT/$v/twister-$T" --inline-logs -v \
			--extra-args RING_SCREENS_DIR="$OUT/$v/ring_screens" > "$OUT/$v/twister-$T.log" 2>&1
		RC=$?
		grep -E " - FAIL - |TESTSUITE .* (failed|succeeded)|passed|failed" "$OUT/$v/twister-$T.log" | head -20
		echo "twister exit code on the broken copy $v, $P: $RC (log $OUT/$v/twister-$T.log)"
		if grep -q "Running TESTSUITE" "$OUT/$v/twister-$T.log" && grep -q -F " FAIL - $NAME in " "$OUT/$v/twister-$T.log"; then
			echo "$v on $P: the named case failed, as required: $(grep -F " FAIL - $NAME in " "$OUT/$v/twister-$T.log" | head -1)"
		else
			echo "$v on $P: the named case did not fail (twister exit $RC): $NAME"
			FAILED="$FAILED $v@$P"
		fi
	done
done
if [ -z "$FAILED" ]; then
	echo "RESULT PASS"
	exit 0
fi
echo "RESULT FAIL$FAILED"
exit 1
