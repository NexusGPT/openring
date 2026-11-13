#!/bin/bash
# run.sh: the iPhone tests (scenarios N, R, P) on the simulated ring chip, ring against a stand-in iPhone.
# Runs inside the ring-os-toolchain container, firmware at /ws/firmware.
#
# Usage, from the Mac (round 2 added scenarios L and D and more broken copies):
#   sh firmware/tools/remote.sh bsim-iphone "tests/bsim/iphone/run.sh"            scenarios N R P
#   sh firmware/tools/remote.sh bsim-iphone-n "tests/bsim/iphone/run.sh N"        one scenario
#   sh firmware/tools/remote.sh bsim-iphone-b "tests/bsim/iphone/run.sh --broken" every broken copy
#   tests/bsim/iphone/run.sh --broken <variant>                                    one broken copy
#
# What it does: builds the ring application (the real ring_devices, ring_control, ring_glue, ring_inbox,
# ring_time, ring_iphone modules and the core; ring_glue starts the iPhone part, as in the product) and the
# stand-in iPhone (host_app: a central that pairs with the passkey, runs the HID client and serves Apple's
# Notification Center, Media and Current Time services) for the simulated chip, and runs them with the
# BabbleSim phy (real encryption, as tests/bsim/control/run.sh):
#   N  five notifications with exact text and flags (a 200-byte message with multi-byte characters is cut on a
#      character), a change, a removal, the 17th drops the oldest, a dismiss and a positive action arrive at the
#      iPhone, an action without its flag sends nothing, the player state and track follow the iPhone's reports,
#      six media commands arrive and change nothing, the clock follows the iPhone's time, events during RECORDING
#      and STANDBY change no core state
#   R  a dropped link and a reconnect (the store is empty, then rebuilt from what the iPhone sends again); the
#      Notification Center Service removed and added again while linked (Service Changed)
#   P  a host without Apple's services (the step 2 kind): no error, the inbox stays empty, keys still work
#   L  an answer to an attribute request arrives after the ring's 3 s timeout: every later notification still gets its own text
#   D  the link ends while the ring is discovering the services: the three services are found in the next session
#   Z  the zone changes while linked (UTC stays the same, the zone is read again)
#   W  an iPhone with Current Time but no Local Time Information: the clock holds local time, zone not known
#   (N also covers the time zone: the clock shows UTC, and R: no zone given, the clock says the zone is not known)
# Each device prints CHECK <name> PASS|FAIL lines and one RESULT line. A test passes when the phy and both devices
# exit 0, both RESULT lines say PASS, no line says FAIL and the ring finished its script before the stand-in evaluated.
#
# --broken: one copy of a module with ONE named fault per variant (broken_edit.py; the real files are not touched).
# A variant counts only when the run completed normally (phy and devices exit 0, both RESULT lines printed, the ring
# finished its script) and the exact check line named by the variant says FAIL. A timeout, a compile error or any
# other failure does not count.
# Last line: "RESULT PASS" (exit 0) or "RESULT FAIL <what>" (exit 1).

set -u

HERE=$(cd "$(dirname "$0")" && pwd)
BOARD=${IPHONE_BOARD:-nrf54lm20bsim/nrf54lm20a/cpuapp}
JOBS=${RING_JOBS:-8}
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-bsim-iphone}
MODS=$HERE/../../../modules
VARIANTS="inbox_size utf8_cut remove_ignored modify_ignored action_flag action_id reset_on_drop sc_ignored media_local time_ignored core_touch request_len service_error late_fragment action_sent zone_ignored zone_assumed media_local_play late_parser zone_read_failed dm_gone zone_not_reread no_lti_known"

BROKEN=0
WHICH="N R P L D Z W"
case "${1:-}" in
--broken) BROKEN=1; WHICH="" ; [ -n "${2:-}" ] && VARIANTS=$2 ;;
N | R | P | L | D | Z | W) WHICH=$1 ;;
"") ;;
*) echo "usage: run.sh [N|R|P|L|D|Z|W|--broken [variant]]"; exit 2 ;;
esac

mkdir -p "$OUT"
echo "bsim-iphone: firmware $HERE, outputs $OUT, scenarios $WHICH, broken $BROKEN"

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
# run_scenario <N|R|P> <ring build dir> <log tag>
run_scenario() {
	local s=$1 ringdir=$2 tag=$3 sim="iph_${1}_$$"
	local sim_ms=130
	[ "$s" = "P" ] && sim_ms=90
	[ "$s" = "L" ] && sim_ms=130
	[ "$s" = "D" ] && sim_ms=90
	[ "$s" = "Z" ] && sim_ms=70
	[ "$s" = "W" ] && sim_ms=70
	INFRA=""
	CHKFAIL=""
	local pf="$OUT/passkey-$tag-$s.txt"
	local L="$OUT/run-$tag-$s"
	: > "$pf"
	echo "=== test $s ($tag): ring + stand-in iPhone, $sim_ms simulated seconds, $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
	LD_LIBRARY_PATH=/ws/tools/bsim/lib RING_SCENARIO=$s RING_PASSFILE=$pf timeout 900 "$ringdir/zephyr/zephyr.exe" -RealEncryption=1 -s="$sim" -d=0 > "$L-ring.log" 2>&1 &
	local p0=$!
	LD_LIBRARY_PATH=/ws/tools/bsim/lib RING_SCENARIO=$s RING_PASSFILE=$pf timeout 900 "$OUT/host/zephyr/zephyr.exe" -RealEncryption=1 -s="$sim" -d=1 > "$L-phone.log" 2>&1 &
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
	grep -E "RING (CHECK|RESULT|SCRIPT|PASSKEY|EVENT|INFO)" "$L-ring.log"
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
		echo "TEST $s RESULT PASS ($npass checks passed)"
		return 0
	fi
	echo "TEST $s RESULT FAIL ($npass checks passed; infra:${INFRA:- none}; checks:${CHKFAIL:- none})"
	return 1
}

build host "$HERE/host_app"

FAILED=""
if [ "$BROKEN" -eq 0 ]; then
	build ring "$HERE/ring_app"
	for s in $WHICH; do
		if ! run_scenario "$s" "$OUT/ring" ok; then
			FAILED="$FAILED $s"
		fi
	done
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
	module=$(echo "$info" | sed -n 's/^MODULE=//p')
	scen=$(echo "$info" | sed -n 's/^SCEN=//p')
	expect=$(echo "$info" | sed -n 's/^EXPECT=//p')
	case "$module" in
	ring_iphone) var=RING_IPHONE_DIR ;;
	ring_inbox) var=RING_INBOX_DIR ;;
	ring_time) var=RING_TIME_DIR ;;
	esac
	build "ring-$v" "$HERE/ring_app" -D$var="$OUT/broken-$v/$module"
	run_scenario "$scen" "$OUT/ring-$v" "broken-$v"
	if [ -n "$INFRA" ]; then
		echo "broken $v: the run itself failed (infra:$INFRA): it does not count"
		FAILED="$FAILED $v(run)"
	elif grep -q -E "$expect" "$OUT"/run-broken-$v-$scen-*.log; then
		echo "broken $v: test $scen failed on its named check, as required: $(grep -h -E "$expect" "$OUT"/run-broken-$v-$scen-*.log | head -1)"
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
