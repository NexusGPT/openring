#!/bin/bash
# run.sh: the screens test on the simulated ring chip: the ring (with its screens on a memory frame buffer) against the stand-in
# iPhone of step 3, over BabbleSim with real encryption. Runs inside the ring-os-toolchain container, firmware at /ws/firmware.
#
# Usage, from the Mac:
#   sh firmware/tools/remote.sh bsim-screens "tests/bsim/screens/run.sh"           scenario S
#   sh firmware/tools/remote.sh bsim-screens-b "tests/bsim/screens/run.sh --broken" every broken copy
#   tests/bsim/screens/run.sh --broken <variant>                                    one broken copy
#
# Scenario S (joystick edges into the real glue and core; the screens draw with LVGL; the display is the memory display):
#   the first joystick event wakes the screen; the menu opens; "Pair device" opens SCR_PAIR and the pairing window; the stand-in
#   pairs with the passkey the screen shows; the first paired device is the active one; a notification arrives from the stand-in
#   and the list shows it (the screen table's state and a frame hash that differs from the empty list); the detail opens; a
#   dismiss chosen with the joystick arrives at the stand-in as the negative action; the stand-in removes the notification
#   and the screens go back to the empty list (the same frame as before).
# A test passes when the phy and both devices exit 0, both RESULT lines say PASS, no CHECK line says FAIL and the ring finished
# its script before the stand-in evaluated.
#
# --broken: one copy of ring_screens with ONE named fault per variant (broken_edit.py; the real files are not touched). A variant
# counts only when the run completed normally and the exact check line named by the variant says FAIL.
# Last line: "RESULT PASS" (exit 0) or "RESULT FAIL <what>" (exit 1).

set -u

HERE=$(cd "$(dirname "$0")" && pwd)
BOARD=${SCREENS_BOARD:-nrf54lm20bsim/nrf54lm20a/cpuapp}
JOBS=${RING_JOBS:-8}
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-bsim-screens}
MODS=$HERE/../../../modules
VARIANTS="dismiss_positive no_detail passkey_not_drawn"

BROKEN=0
if [ "${1:-}" = "--broken" ]; then
	BROKEN=1
	[ -n "${2:-}" ] && VARIANTS=$2
elif [ -n "${1:-}" ]; then
	echo "usage: run.sh [--broken [variant]]"
	exit 2
fi

mkdir -p "$OUT"
echo "bsim-screens: firmware $HERE, outputs $OUT, broken $BROKEN"

build() { # build <dir name> <source> [cmake args]
	local name=$1 src=$2
	shift 2
	echo "=== build $name for $BOARD, log $OUT/build-$name.log"
	if ! west build -p always -b "$BOARD" --no-sysbuild -d "$OUT/$name" -o=-j"$JOBS" "$src" "$@" > "$OUT/build-$name.log" 2>&1; then
		tail -n 60 "$OUT/build-$name.log"
		echo "RESULT FAIL build $name"
		exit 1
	fi
	grep -E "warning:" "$OUT/build-$name.log" | sort | uniq -c | head -20
	echo "build $name ok"
}

INFRA=""
CHKFAIL=""
# run_scenario <ring build dir> <log tag>
run_scenario() {
	local ringdir=$1 tag=$2 sim="scr_S_$$"
	local sim_ms=100
	INFRA=""
	CHKFAIL=""
	local pf="$OUT/passkey-$tag.txt"
	local L="$OUT/run-$tag"
	: > "$pf"
	echo "=== test S ($tag): ring + stand-in iPhone, $sim_ms simulated seconds, $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
	LD_LIBRARY_PATH=/ws/tools/bsim/lib RING_SCENARIO=S RING_PASSFILE=$pf timeout 900 "$ringdir/zephyr/zephyr.exe" -RealEncryption=1 -s="$sim" -d=0 > "$L-ring.log" 2>&1 &
	local p0=$!
	LD_LIBRARY_PATH=/ws/tools/bsim/lib RING_SCENARIO=S RING_PASSFILE=$pf timeout 900 "$OUT/host/zephyr/zephyr.exe" -RealEncryption=1 -s="$sim" -d=1 > "$L-phone.log" 2>&1 &
	local p1=$!
	(cd "$BSIM_OUT_PATH/bin" && timeout 900 ./bs_2G4_phy_v1 -s="$sim" -D=2 -sim_length=${sim_ms}e6) > "$L-phy.log" 2>&1 &
	local pp=$!
	wait $pp
	local rc_phy=$?
	wait $p0
	local rc_ring=$?
	wait $p1
	local rc_phone=$?
	echo "exit codes: phy $rc_phy, ring $rc_ring, stand-in $rc_phone"
	[ $rc_phy -ne 0 ] && INFRA="$INFRA phy-exit-$rc_phy"
	[ $rc_ring -ne 0 ] && INFRA="$INFRA ring-exit-$rc_ring"
	[ $rc_phone -ne 0 ] && INFRA="$INFRA phone-exit-$rc_phone"

	echo "--- ring $L-ring.log"
	grep -E "RING (CHECK|RESULT|SCRIPT|PASSKEY|EVENT|INFO|MEMORY|STACK)" "$L-ring.log"
	grep -q "RING RESULT" "$L-ring.log" || INFRA="$INFRA ring-no-result"
	grep -q "RING RESULT PASS" "$L-ring.log" || CHKFAIL="$CHKFAIL ring-result"
	echo "--- stand-in iPhone $L-phone.log"
	grep -E "PHONE (CHECK|RESULT|EVAL|INFO|REPORT|START)" "$L-phone.log"
	grep -q "PHONE RESULT" "$L-phone.log" || INFRA="$INFRA phone-no-result"
	grep -q "PHONE RESULT PASS" "$L-phone.log" || CHKFAIL="$CHKFAIL phone-result"
	local nfail npass
	nfail=$(cat "$L"-ring.log "$L"-phone.log | grep -c -E "(RING|PHONE) CHECK .* FAIL")
	npass=$(cat "$L"-ring.log "$L"-phone.log | grep -c -E "(RING|PHONE) CHECK .* PASS")
	[ "$nfail" -ne 0 ] && CHKFAIL="$CHKFAIL $nfail-failed-checks"
	local done_t eval_t
	done_t=$(grep -o "RING SCRIPT DONE t=[0-9]*" "$L-ring.log" | head -1 | grep -o "[0-9]*$")
	eval_t=$(grep -o "PHONE EVAL t=[0-9]*" "$L-phone.log" | head -1 | grep -o "[0-9]*$")
	echo "ring script done at ${done_t:-none} ms, stand-in evaluated at ${eval_t:-none} ms"
	if [ -z "$done_t" ] || [ -z "$eval_t" ] || [ "$done_t" -ge "$eval_t" ]; then
		INFRA="$INFRA ring-not-done-before-eval"
	fi
	if [ -z "$INFRA" ] && [ -z "$CHKFAIL" ]; then
		echo "TEST S RESULT PASS ($npass checks passed)"
		return 0
	fi
	echo "TEST S RESULT FAIL ($npass checks passed; infra:${INFRA:- none}; checks:${CHKFAIL:- none})"
	return 1
}

build host "$HERE/host_app"

FAILED=""
if [ "$BROKEN" -eq 0 ]; then
	build ring "$HERE/ring_app"
	if ! run_scenario "$OUT/ring" ok; then
		FAILED="$FAILED S"
	fi
	if [ -z "$FAILED" ]; then
		echo "RESULT PASS"
		exit 0
	fi
	echo "RESULT FAIL$FAILED"
	exit 1
fi

# Broken copies: each one named fault must be caught by its own named check.
for v in $VARIANTS; do
	echo "##### broken copy: $v"
	mkdir -p "$OUT/broken-$v"
	if ! info=$(python3 -I "$HERE/broken_edit.py" "$v" "$MODS" "$OUT/broken-$v" 2> "$OUT/broken-$v/edit.log"); then
		cat "$OUT/broken-$v/edit.log"
		echo "broken $v: the edit could not be made"
		FAILED="$FAILED $v(edit)"
		continue
	fi
	cat "$OUT/broken-$v/edit.log"
	expect=$(echo "$info" | sed -n 's/^EXPECT=//p')
	build "ring-$v" "$HERE/ring_app" -DRING_SCREENS_DIR="$OUT/broken-$v/ring_screens" -DRING_RHW_INCLUDE_DIR="$MODS/ring_rhw/include"
	run_scenario "$OUT/ring-$v" "broken-$v"
	if [ -n "$INFRA" ]; then
		echo "broken $v: the run itself failed (infra:$INFRA): it does not count"
		FAILED="$FAILED $v(run)"
	elif grep -q -E "$expect" "$OUT"/run-broken-$v-*.log; then
		echo "broken $v: test S failed on its named check, as required: $(grep -h -E "$expect" "$OUT"/run-broken-$v-*.log | head -1)"
	else
		echo "broken $v: the named check line did not say FAIL: $expect"
		FAILED="$FAILED $v(not-caught)"
	fi
done
if [ -z "$FAILED" ]; then
	echo "RESULT PASS"
	exit 0
fi
echo "RESULT FAIL$FAILED"
exit 1
