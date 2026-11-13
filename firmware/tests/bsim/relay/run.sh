#!/bin/bash
# run.sh: the relay test on the simulated ring chip: the ring (with its screens on a memory frame buffer) against a stand-in helper
# (the GATT client the Android helper app will be), over BabbleSim with real encryption. Runs inside the ring-os-toolchain container,
# firmware at /ws/firmware.
#
# Usage, from the Mac:
#   sh firmware/tools/remote.sh bsim-relay "tests/bsim/relay/run.sh"                scenarios H and I
#   sh firmware/tools/remote.sh bsim-relay-h "tests/bsim/relay/run.sh H"            one scenario
#   sh firmware/tools/remote.sh bsim-relay-b "tests/bsim/relay/run.sh --broken"     every broken copy
#   tests/bsim/relay/run.sh --broken <variant>                                       one broken copy
#
# Scenario H (the helper): the stand-in finds the relay service on an unsecured link and fails to write, subscribe and read; it pairs
#   with the passkey the screen shows (security level 4); Info; HELLO and READY; 4 notifications in pieces of 11 bytes (one record
#   with texts longer than their limits, multi-byte); the screens show them (list, detail); a replace keeps place and read mark; actions
#   the notification does not have send nothing; the positive action and a dismiss arrive as ACTION frames and the entry leaves only on
#   REMOVE; with no subscription to Out the ring refuses the action; frames during RECORDING change nothing in the core; 21 malformed
#   frames are refused with their codes and leave the store unchanged; an unfinished PUT and a dropped link: the store is empty; after
#   the reconnect and a new HELLO the store is rebuilt (frames of 244 bytes, records of 2 and 512 bytes).
# Scenario I (one source per link): the stand-in is an iPhone with the notification service and also writes relay frames: all refused
#   with code 7, the iPhone's notification untouched, a dismiss on the ring reaches the iPhone's service.
# Scenario B (the other order): the stand-in has Apple's notification service too, but its relay HELLO comes first: the ring finds that
#   service and does not use it, the relay's notification stays, and a dismiss goes to the helper.
# Scenario Q (a full Out queue, test hook in the test ring only): 12 refused frames fill the queue; an action is refused on the ring (-EBUSY, not
#   counted as sent); an accepted HELLO drops every frame that waits for Out, so READY is the first frame and nothing from before comes.
# A test passes when the phy and both devices exit 0, both RESULT lines say PASS, no CHECK line says FAIL and the ring finished its
# script before the stand-in evaluated.
#
# --broken: one copy of a module with ONE named fault per variant (broken_edit.py; the real files are not touched). A variant counts
# only when the run completed normally and the exact check line named by the variant says FAIL.
# Last line: "RESULT PASS" (exit 0) or "RESULT FAIL <what>" (exit 1).

set -u

HERE=$(cd "$(dirname "$0")" && pwd)
BOARD=${RELAY_BOARD:-nrf54lm20bsim/nrf54lm20a/cpuapp}
JOBS=${RING_JOBS:-8}
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID-bsim-relay}
MODS=$HERE/../../../modules
VARIANTS="relay_reaches_core code7_not_enforced action_without_flag store_not_emptied_at_link_end remove_ignored put_early refused_changes_store no_security_check action_id hello_keeps_store error_not_notified replace_moves_front relay_wakes_screen source_not_fixed refused_frame_changes_store sc_clears_relay_entries hello_keeps_queue action_counted_when_queue_full session_start_clears_relay"

BROKEN=0
WHICH="H I B Q"
case "${1:-}" in
--broken) BROKEN=1; WHICH=""; [ -n "${2:-}" ] && VARIANTS=$2 ;;
H | I | B | Q) WHICH=$1 ;;
"") ;;
*) echo "usage: run.sh [H|I|B|Q|--broken [variant]]"; exit 2 ;;
esac

mkdir -p "$OUT"
echo "bsim-relay: firmware $HERE, outputs $OUT, scenarios $WHICH, broken $BROKEN"

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
# run_scenario <H|I> <ring build dir> <log tag>
run_scenario() {
	local s=$1 ringdir=$2 tag=$3 sim="rly_${1}_$$"
	local sim_ms=300
	[ "$s" = "I" ] && sim_ms=150
	[ "$s" = "B" ] && sim_ms=140
	[ "$s" = "Q" ] && sim_ms=100
	INFRA=""
	CHKFAIL=""
	local pf="$OUT/passkey-$tag-$s.txt"
	local rs="$OUT/ring-sync-$tag-$s.txt"
	local hs="$OUT/helper-sync-$tag-$s.txt"
	local L="$OUT/run-$tag-$s"
	: > "$pf"
	: > "$rs"
	: > "$hs"
	echo "=== test $s ($tag): ring + stand-in, $sim_ms simulated seconds, $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
	LD_LIBRARY_PATH=/ws/tools/bsim/lib RING_SCENARIO=$s RING_PASSFILE=$pf RING_SYNC=$rs HELPER_SYNC=$hs timeout 1200 "$ringdir/zephyr/zephyr.exe" -RealEncryption=1 -s="$sim" -d=0 > "$L-ring.log" 2>&1 &
	local p0=$!
	LD_LIBRARY_PATH=/ws/tools/bsim/lib RING_SCENARIO=$s RING_PASSFILE=$pf RING_SYNC=$rs HELPER_SYNC=$hs timeout 1200 "$OUT/host/zephyr/zephyr.exe" -RealEncryption=1 -s="$sim" -d=1 > "$L-helper.log" 2>&1 &
	local p1=$!
	(cd "$BSIM_OUT_PATH/bin" && timeout 1200 ./bs_2G4_phy_v1 -s="$sim" -D=2 -sim_length=${sim_ms}e6) > "$L-phy.log" 2>&1 &
	local pp=$!
	wait $pp
	local rc_phy=$?
	wait $p0
	local rc_ring=$?
	wait $p1
	local rc_helper=$?
	echo "exit codes: phy $rc_phy, ring $rc_ring, stand-in $rc_helper"
	[ $rc_phy -ne 0 ] && INFRA="$INFRA phy-exit-$rc_phy"
	[ $rc_ring -ne 0 ] && INFRA="$INFRA ring-exit-$rc_ring"
	[ $rc_helper -ne 0 ] && INFRA="$INFRA helper-exit-$rc_helper"

	echo "--- ring $L-ring.log"
	grep -E "RING (CHECK|WAIT|RESULT|SCRIPT|PASSKEY|EVENT|INFO)" "$L-ring.log"
	grep -q "RING RESULT" "$L-ring.log" || INFRA="$INFRA ring-no-result"
	grep -q "RING RESULT PASS" "$L-ring.log" || CHKFAIL="$CHKFAIL ring-result"
	echo "--- stand-in $L-helper.log"
	grep -E "HELPER (CHECK|WAIT|RESULT|EVAL|INFO|OUT|START)" "$L-helper.log"
	grep -q "HELPER RESULT" "$L-helper.log" || INFRA="$INFRA helper-no-result"
	grep -q "HELPER RESULT PASS" "$L-helper.log" || CHKFAIL="$CHKFAIL helper-result"
	local nfail npass
	nfail=$(cat "$L"-ring.log "$L"-helper.log | grep -c -E "(RING|HELPER) (CHECK|WAIT) .* FAIL")
	npass=$(cat "$L"-ring.log "$L"-helper.log | grep -c -E "(RING|HELPER) CHECK .* PASS")
	[ "$nfail" -ne 0 ] && CHKFAIL="$CHKFAIL $nfail-failed-checks"
	local done_t eval_t
	done_t=$(grep -o "RING SCRIPT DONE t=[0-9]*" "$L-ring.log" | head -1 | grep -o "[0-9]*$")
	eval_t=$(grep -o "HELPER EVAL t=[0-9]*" "$L-helper.log" | head -1 | grep -o "[0-9]*$")
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
	# one -D per copied module
	dargs=()
	for m in $module; do
		case "$m" in
		ring_relay) dargs+=("-DRING_RELAY_DIR=$OUT/broken-$v/ring_relay") ;;
		ring_iphone) dargs+=("-DRING_IPHONE_DIR=$OUT/broken-$v/ring_iphone") ;;
		ring_inbox) dargs+=("-DRING_INBOX_DIR=$OUT/broken-$v/ring_inbox") ;;
		esac
	done
	build "ring-$v" "$HERE/ring_app" "${dargs[@]}"
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
