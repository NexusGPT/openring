#!/bin/bash
# run.sh: the ship beacon test (software step 6, unit U8, decision D6 b): the ring with its real factory part and real beacon
# (rfa_hw_real.c) on the simulated ring chip, against a stand-in scanner (the jig's ear), over BabbleSim. Runs inside the
# ring-os-toolchain container, firmware at /ws/firmware.
#
# Usage, from the Mac (project folder):
#   RING_REMOTE_SRC=/root/ring-os/src-u-factory sh firmware/tools/remote.sh u-factory-bsim "tests/bsim/factory/run.sh"
#   ... "tests/bsim/factory/run.sh --broken"            both broken copies
#   ... "tests/bsim/factory/run.sh --broken <variant>"  one broken copy (connectable, never_stops)
#
# The ring: at 2 s FACTORY SHIP_ENTER (0x7F) in FACTORY_TEST; at 8 s "VBUS removed": rfa_beacon_stop() (what rpw_ship calls right
# before the ship task); at 70 s T-RADIO (0x60), which advertises 10 s. The scanner (a passive scan, nothing shared with the code
# under test; its numbers are typed from design/firmware.md l.1031, l.1034, l.1035, l.1057) checks: nothing before the command; the
# beacon within 300 ms of it; at least 40 reports in the 6 s with VBUS on; the name "Ring" and 4 upper case hex digits, the same
# in every report and the same as the name the ring prints; every report is ADV_NONCONN_IND (not connectable); the median gap
# between reports 95 to 125 ms (100 ms interval); none later than 1 s after the removal, none for 60 s; the radio test heard for
# 10 s (at least 80 reports) and silent after it. Not checked here: the 0 dBm power (the simulated radio carries no power figure).
# A run passes when the phy and both devices exit 0, both RESULT lines say PASS, no CHECK line says FAIL and the two names agree.
#
# --broken: one copy of ring_factory with ONE named fault per variant (broken_edit.py; the real files are not touched). A variant
# counts only when the run completed normally (the three exits 0, both RESULT lines present) and the exact check line named by
# the variant says FAIL.
# Last line: "RESULT PASS" (exit 0) or "RESULT FAIL <what>" (exit 1).

set -u

HERE=$(cd "$(dirname "$0")" && pwd)
BOARD=${FACTORY_BOARD:-nrf54lm20bsim/nrf54lm20a/cpuapp}
JOBS=${RING_JOBS:-8}
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-bsim-factory}
MODS=$HERE/../../../modules
VARIANTS="connectable never_stops"
SIM_S=88

BROKEN=0
case "${1:-}" in
--broken) BROKEN=1; [ -n "${2:-}" ] && VARIANTS=$2 ;;
"") ;;
*) echo "usage: run.sh [--broken [variant]]"; exit 2 ;;
esac

mkdir -p "$OUT"
echo "bsim-factory: firmware $HERE, outputs $OUT, broken $BROKEN"

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
# run_test <ring build dir> <log tag>
run_test() {
	local ringdir=$1 tag=$2 sim="fac_$$_$2"
	local L="$OUT/run-$tag"
	INFRA=""
	CHKFAIL=""
	echo "=== test ($tag): ring + scanner, $SIM_S simulated seconds, $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
	LD_LIBRARY_PATH=/ws/tools/bsim/lib timeout 1200 "$ringdir/zephyr/zephyr.exe" -RealEncryption=1 -s="$sim" -d=0 > "$L-ring.log" 2>&1 &
	local p0=$!
	LD_LIBRARY_PATH=/ws/tools/bsim/lib timeout 1200 "$OUT/host/zephyr/zephyr.exe" -RealEncryption=1 -s="$sim" -d=1 > "$L-scanner.log" 2>&1 &
	local p1=$!
	(cd "$BSIM_OUT_PATH/bin" && timeout 1200 ./bs_2G4_phy_v1 -s="$sim" -D=2 -sim_length=${SIM_S}e6) > "$L-phy.log" 2>&1 &
	local pp=$!
	wait $pp
	local rc_phy=$?
	wait $p0
	local rc_ring=$?
	wait $p1
	local rc_host=$?
	echo "exit codes: phy $rc_phy, ring $rc_ring, scanner $rc_host"
	[ $rc_phy -ne 0 ] && INFRA="$INFRA phy-exit-$rc_phy"
	[ $rc_ring -ne 0 ] && INFRA="$INFRA ring-exit-$rc_ring"
	[ $rc_host -ne 0 ] && INFRA="$INFRA scanner-exit-$rc_host"

	echo "--- ring $L-ring.log"
	grep -E "RING (CHECK|RESULT|SCRIPT|BEACON|VBUS|SHIP)" "$L-ring.log"
	grep -q "RING RESULT" "$L-ring.log" || INFRA="$INFRA ring-no-result"
	grep -q "RING RESULT PASS" "$L-ring.log" || CHKFAIL="$CHKFAIL ring-result"
	echo "--- scanner $L-scanner.log"
	grep -E "HOST (CHECK|RESULT|REPORTS|BEACON|MEDIAN)" "$L-scanner.log"
	grep -q "HOST RESULT" "$L-scanner.log" || INFRA="$INFRA scanner-no-result"
	grep -q "HOST RESULT PASS" "$L-scanner.log" || CHKFAIL="$CHKFAIL scanner-result"
	local nfail npass
	nfail=$(cat "$L-ring.log" "$L-scanner.log" | grep -c -E "(RING|HOST) CHECK .* FAIL")
	npass=$(cat "$L-ring.log" "$L-scanner.log" | grep -c -E "(RING|HOST) CHECK .* PASS")
	[ "$nfail" -ne 0 ] && CHKFAIL="$CHKFAIL $nfail-failed-checks"
	# the name the ring prints is the name the scanner heard
	local rn hn
	rn=$(grep -o 'RING BEACON NAME .*' "$L-ring.log" | head -1 | sed 's/^RING BEACON NAME //')
	hn=$(grep -o 'HOST BEACON NAME .*' "$L-scanner.log" | head -1 | sed 's/^HOST BEACON NAME //')
	echo "names: ring '$rn', scanner '$hn'"
	if [ -z "$rn" ] || [ "$rn" != "$hn" ]; then
		CHKFAIL="$CHKFAIL names-differ"
	fi
	if [ -z "$INFRA" ] && [ -z "$CHKFAIL" ]; then
		echo "TEST RESULT PASS ($npass checks passed)"
		return 0
	fi
	echo "TEST RESULT FAIL ($npass checks passed; infra:${INFRA:- none}; checks:${CHKFAIL:- none})"
	return 1
}

build host "$HERE/host_app"

FAILED=""
if [ "$BROKEN" -eq 0 ]; then
	build ring "$HERE/ring_app"
	if ! run_test "$OUT/ring" ok; then
		FAILED=" beacon"
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
	if ! info=$(python3 -B -I "$HERE/broken_edit.py" "$v" "$MODS" "$OUT/broken-$v" 2> "$OUT/broken-$v/edit.log"); then
		cat "$OUT/broken-$v/edit.log"
		echo "broken $v: the edit could not be made"
		FAILED="$FAILED $v(edit)"
		continue
	fi
	cat "$OUT/broken-$v/edit.log"
	diff -u -r "$MODS/ring_factory" "$OUT/broken-$v/ring_factory" > "$OUT/broken-$v/diff.txt"
	cat "$OUT/broken-$v/diff.txt"
	expect=$(echo "$info" | sed -n 's/^EXPECT=//p')
	build "ring-$v" "$HERE/ring_app" "-DRING_FACTORY_DIR=$OUT/broken-$v/ring_factory"
	run_test "$OUT/ring-$v" "broken-$v"
	if [ -n "$INFRA" ]; then
		echo "broken $v: the run itself failed (infra:$INFRA): it does not count"
		FAILED="$FAILED $v(run)"
	elif grep -q -E "$expect" "$OUT/run-broken-$v-scanner.log"; then
		echo "broken $v: the test failed on its named check, as required: $(grep -h -E "$expect" "$OUT/run-broken-$v-scanner.log" | head -1)"
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
