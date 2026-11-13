#!/bin/bash
# run.sh: the two-device tests of devices and control (tests A, B, C, D, F) on the simulated
# chip. Runs inside the ring-os-toolchain container, firmware at /ws/firmware.
#
# Usage, from the Mac:
#   sh firmware/tools/remote.sh bsim-control "tests/bsim/control/run.sh"             tests A B C D F
#   sh firmware/tools/remote.sh bsim-control-a "tests/bsim/control/run.sh A"         one test
#   sh firmware/tools/remote.sh bsim-broken "tests/bsim/control/run.sh --broken"     every broken copy
#   tests/bsim/control/run.sh --broken keymap                                        one broken copy
#
# What it does: builds the ring application (the real ring_devices, ring_control and ring_glue
# modules; the glue is the module the product application runs; the core is the joystick source;
# a test hook injects joystick edges in simulated time) and the stand-in host (a HID over GATT
# client) for the simulated chip (see BOARD below), then runs them with the BabbleSim phy:
#   A  ring + host 1: pairing with the passkey; each joystick action in each mode; control not
#      active types nothing; a held direction repeats within bounds; screen off; double press; a drop
#   B  ring + hosts 1, 2: pair in turn, switch both ways; a key in the switch window never reaches
#      the old device
#   C  ring + host 1: remove the pairing, the host cannot reconnect, it pairs again
#   D  ring + host 1: a centre hold of 1,200 ms starts and stops a recording in every mode and sends
#      no key; a failed release is sent later; a host that writes to the ring starts nothing
#   F  ring + hosts 1, 2: a host that was never paired cannot pair while the window is closed
# Each device prints CHECK <name> PASS|FAIL lines and one RESULT line. A test passes when the phy
# and every device exit 0, every device's RESULT is PASS, no line says FAIL and the ring finished
# its script before the host evaluated.
#
# --broken: one copy of a module with ONE named fault per variant (broken_edit.py; the real
# files are not touched). A variant counts only when the run completed normally (phy and devices
# exit 0, every device printed its RESULT line, the ring finished its script) and the exact check
# line named by the variant says FAIL. A timeout, a compile error or any other failure does not count.
# Last line: "RESULT PASS" (exit 0) or "RESULT FAIL <what>" (exit 1).

set -u

HERE=/ws/firmware/tests/bsim/control
# Test board: nrf52_bsim/native, the simulated nRF52 with BabbleSim. The simulated nRF54LM20A
# (nrf54lm20bsim/nrf54lm20a/cpuapp, and the sister nrf54l15bsim/nrf54l15/cpuapp) builds and
# connects, but the first encrypted packet fails its MIC check (disconnect reason 0x3d), so no
# pairing completes there: see docs/devices-control-notes.md section 6. CTRL_BOARD overrides.
BOARD=${CTRL_BOARD:-nrf52_bsim/native}
JOBS=${RING_JOBS:-8}
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/probe54/ctl-realenc}
SIM_MS=${SIM_MS:-75}   # simulated seconds
MODS=$HERE/../../../modules
VARIANTS="keymap hold_key switch_gate window host_write repeat_flood gate release_retry"

BROKEN=0
WHICH="A B C D F"
case "${1:-}" in
--broken) BROKEN=1; WHICH="" ; [ -n "${2:-}" ] && VARIANTS=$2 ;;
A | B | C | D | F | T) WHICH=$1 ;;
"") ;;
*) echo "usage: run.sh [A|B|C|D|F|--broken [variant]]"; exit 2 ;;
esac

mkdir -p "$OUT"
echo "bsim-control: firmware $HERE, outputs $OUT, scenarios $WHICH, broken $BROKEN"

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

COMMON_EXTRA=()
if [ -n "${CTRL_CONF:-}" ]; then
	COMMON_EXTRA+=(-DEXTRA_CONF_FILE="$CTRL_CONF")
fi

# run_scenario <A|B|C|D|F> <ring build dir> <log tag>
# Runs one test. Sets INFRA (the run itself went wrong: exit codes, missing RESULT lines, timing)
# and CHKFAIL (a device's RESULT is not PASS, or a check says FAIL); both empty means PASS.
# Prints the device lines and "TEST <s> RESULT PASS|FAIL (...)".
INFRA=""
CHKFAIL=""
run_scenario() {
	local s=$1 ringdir=$2 tag=$3 nh=1 sim="ctl_${1}_$$"
	INFRA=""
	CHKFAIL=""
	[ "$s" = "B" ] || [ "$s" = "F" ] || [ "$s" = "T" ] && nh=2
	local D=$((nh + 1))
	local pf="$OUT/passkey-$tag-$s.txt"
	local L="$OUT/run-$tag-$s"
	: > "$pf"
	echo "=== test $s ($tag): ring + $nh host(s), $SIM_MS simulated seconds, $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
	LD_LIBRARY_PATH=/ws/tools/bsim/lib RING_SCENARIO=$s RING_PASSFILE=$pf timeout 900 "$ringdir/zephyr/zephyr.exe" -RealEncryption=1 -s="$sim" -d=0 > "$L-ring.log" 2>&1 &
	local p0=$!
	local ph=()
	for h in $(seq 1 $nh); do
		LD_LIBRARY_PATH=/ws/tools/bsim/lib HOST_ID=$h RING_SCENARIO=$s RING_PASSFILE=$pf timeout 900 "$OUT/host/zephyr/zephyr.exe" -RealEncryption=1 -s="$sim" -d=$h > "$L-host$h.log" 2>&1 &
		ph+=($!)
	done
	(cd "$BSIM_OUT_PATH/bin" && timeout 900 ./bs_2G4_phy_v1 -s="$sim" -D=$D -sim_length=${SIM_MS}e6) > "$L-phy.log" 2>&1 &
	local pp=$!
	wait $pp
	local rc_phy=$?
	wait $p0
	local rc_ring=$?
	local rc_hosts=""
	for p in "${ph[@]}"; do
		wait $p
		rc_hosts="$rc_hosts $?"
	done
	echo "exit codes: phy $rc_phy, ring $rc_ring, hosts$rc_hosts"
	[ $rc_phy -ne 0 ] && INFRA="$INFRA phy-exit-$rc_phy"
	[ $rc_ring -ne 0 ] && INFRA="$INFRA ring-exit-$rc_ring"
	for c in $rc_hosts; do [ "$c" != "0" ] && INFRA="$INFRA host-exit-$c"; done

	echo "--- ring $L-ring.log"
	grep -E "RING (CHECK|RESULT|SCRIPT|PASSKEY|EVENT|INFO)" "$L-ring.log"
	grep -q "RING RESULT" "$L-ring.log" || INFRA="$INFRA ring-no-result"
	grep -q "RING RESULT PASS" "$L-ring.log" || CHKFAIL="$CHKFAIL ring-result"
	for h in $(seq 1 $nh); do
		echo "--- host $h $L-host$h.log"
		grep -E "HOST H$h (CHECK|RESULT|EVAL|INFO|REPORT|passkey|security|connected|disconnected)" "$L-host$h.log"
		grep -q "HOST H$h RESULT" "$L-host$h.log" || INFRA="$INFRA host$h-no-result"
		grep -q "HOST H$h RESULT PASS" "$L-host$h.log" || CHKFAIL="$CHKFAIL host$h-result"
	done
	local nfail npass
	nfail=$(cat "$L"-*.log | grep -c -E "(RING|HOST H[0-9]) CHECK .* FAIL")
	npass=$(cat "$L"-*.log | grep -c -E "(RING|HOST H[0-9]) CHECK .* PASS")
	[ "$nfail" -ne 0 ] && CHKFAIL="$CHKFAIL $nfail-failed-checks"
	# the ring must be done before the host evaluates
	local done_t eval_t
	done_t=$(grep -o "RING SCRIPT DONE t=[0-9]*" "$L-ring.log" | head -1 | grep -o "[0-9]*$")
	eval_t=$(grep -o "EVAL t=[0-9]*" "$L-host1.log" | head -1 | grep -o "[0-9]*$")
	echo "ring script done at ${done_t:-none} ms, host 1 evaluated at ${eval_t:-none} ms"
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

build host "$HERE/host_app" "${COMMON_EXTRA[@]+"${COMMON_EXTRA[@]}"}"

FAILED=""
if [ "$BROKEN" -eq 0 ]; then
	case " $WHICH " in
	*" T "*) build ring-two "$HERE/trial_app" "${COMMON_EXTRA[@]+"${COMMON_EXTRA[@]}"}" ;;
	esac
	case " $WHICH " in
	*" A "* | *" B "* | *" C "* | *" D "* | *" F "*) build ring "$HERE/ring_app" "${COMMON_EXTRA[@]+"${COMMON_EXTRA[@]}"}" ;;
	esac
	for s in $WHICH; do
		ringdir=$OUT/ring
		[ "$s" = "T" ] && ringdir=$OUT/ring-two
		if ! run_scenario "$s" "$ringdir" ok; then
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
	ring_control) var=RING_CONTROL_DIR ;;
	ring_devices) var=RING_DEVICES_DIR ;;
	esac
	build "ring-$v" "$HERE/ring_app" "${COMMON_EXTRA[@]+"${COMMON_EXTRA[@]}"}" -D$var="$OUT/broken-$v/$module"
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
