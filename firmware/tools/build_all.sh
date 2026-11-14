#!/bin/bash
# build_all.sh: build the ring firmware and run every test. Runs inside the
# ring-os-toolchain container, with the firmware folder at /ws/firmware.
#
# Usage, from the Mac: sh firmware/tools/remote.sh build-all "tools/build_all.sh"
# Usage, in the container: bash /ws/firmware/tools/build_all.sh
#
# Stages (each one's log is kept in $OUT/<stage>.log):
#   1 dk     firmware/app for nrf54lm20dk/nrf54lm20a/cpuapp, sysbuild with
#            MCUboot; prints flash and RAM use from the linker's memory report
#   2 bsim   firmware/app for nrf54lm20bsim/nrf54lm20a/cpuapp; runs it for 2
#            simulated seconds and checks the start line; step 6: also the recorder's line
#            "ring-os recorder: boot done, state STANDBY" (the product boots through the recorder on the
#            simulated drivers)
#   3 tests  twister on every test under firmware/tests on native_sim, and on
#            each bsim board that a test names in its platform_allow
#   4 bsim-<name>  every firmware/tests/bsim/<name>/run.sh (two-device tests with
#            BabbleSim: control, iphone = the ring against a stand-in iPhone, relay = the ring against a stand-in helper (step 5),
#            screens = the same with the ring's screens), and the same
#            with --broken where the script supports it (every broken copy must fail on its own
#            named check)
#   4b link-settings  the product's built settings files (dk and bsim builds) hold the same MTU, ACL buffer sizes
#            and system workqueue stack as the iPhone test ring (tools/check_link_settings.sh); step 5: the same against the
#            relay test ring, its other Bluetooth settings compared with the product's, and the relay service is in the product
#   4c relay-no-core  step 5: the relay module's sources name nothing of the core, the glue, the devices, the control or the screens
#            (design/firmware.md 7.7: the relay part calls nothing in the core); a copy with one such call must be refused
#   4d recorder-one-mic-path  step 6: only rec_mics_on() in modules/ring_recorder/src/rrec_mics.c switches the microphone rail
#            on (design/firmware.md l.342): one hit of the rail call with "on" in the sources of the step 6 modules and the
#            application; self test: a copy with a second such call in another file is found by the same search
#   4e recorder-no-start-path  step 6: the sources of ring_store, ring_audio, ring_xfer, ring_power, ring_motor, ring_sys and
#            ring_factory never name rglue_input, rc_core_input or RC_EV_LONG_PRESS (design/firmware.md l.209: only a long
#            press starts or stops a recording); self test: a planted copy with rglue_input is found
#   4f recorder-no-raw-pins  step 6: no source, header or overlay of step 6 (the step 6 modules, the application, the step 6
#            test folders) names a chip pin by number (P1.24, NRF_GPIO_PIN_MAP, <&gpio1 24 ...; design/firmware.md l.77);
#            self test: a planted overlay with a pin by number is found
#   4g recorder-product-drivers  step 6 (decision D11b): the development kit build's .config has CONFIG_RING_RHW_SIM off (and
#            the recorder's test read-outs off), the simulated-chip product build has it on; prints which real driver files
#            the kit build compiled (decision D15); self test: a copy of the kit .config with the option on is refused
#   stack-report (after dk) step 6: tools/stack_report.py also sums the chains of the recorder's threads (glue actions,
#            recorder thread, audio, storage, USB, power sampling, motor timer)
#   3b pictures  (step 4) the screens' pictures written by the screens test (tests/screens, env RING_PICS) are checked as PNG files
#            and listed in $OUT/pictures/manifest-<board>.md (tools/pictures_manifest.py)
#   5 broken-<name>  every firmware/tests/<name>/broken_run.sh (a broken copy of a logic
#            suite's module; passes only when the one named case fails): control, devices,
#            inbox, time, iphone, relay (step 5), screens; step 6: rhw, core, store, audio, xfer, power, motor,
#            sys, factory, recorder (they join by their files, no change here)
#   6 ring   step 7: firmware/app for the ring itself, ringrec/nrf54lm20a/cpuapp (board files in firmware/boards/ringrec,
#            BOARD_ROOT=firmware), sysbuild with MCUboot; prints flash and RAM use from the linker's memory report
#   6a ring-drivers  step 7: the ring build's .config has CONFIG_RING_RHW_SIM off and the recorder's test read-outs off;
#            prints each real driver file the ring build compiled with its code size and functions ("real code" or
#            "empty stub"), and the power part's switch CONFIG_RING_POWER_REAL
#   6b ring-ram  step 7: every RAM symbol of the ring image, largest first (nm -S -l --size-sort -r)
#   6c ring-pins  step 7: tools/check_ring_pins.py: the ring build's zephyr.dts against the netlist (rows of U1): pins,
#            GPIO flags, the reverse scan; prints the netlist copy's sha256 and where it was compared with the design's
#   6d ring-pins-broken  step 7 and fix round 1: planted copies of the board (MOTOR on another pin, SD_MISO on another
#            pin in the default state, LCD_TE's property removed, PMIC_INT on another port, JOY_LEFT's node removed,
#            JOY_DOWN's node disabled, an extra pin, JOY_UP without its pull-up), each configured (cmake only), and of the
#            netlist (an unknown net, LCD_RST's row changed): each must fail, naming exactly its signal
#   6e ring-production  fix round 1: the ring with its production settings (app/ringrec_production.conf,
#            boards/ringrec/ringrec_production.overlay and _mcuboot.conf: no UART output, design/firmware.md l.1061),
#            sysbuild, compile only; memory report; ring-production-check: no UART in either image, the pin check in
#            production mode (DBG_TX a hog with pull-down); ring-production-broken (fix round 2): three planted copies
#            (a UART on, DBG_TX without pull-down, a missing input file) must each be refused; fix round 3: also a UART
#            console in MCUboot and uart20 enabled; the pin check's failing list is compared whole
#   6f ring-lines-safe  fix round 3: static check that rst_hw_real.c's b_suspend always ends in lines_safe(), b_resume
#            calls it on every failure, lines_safe reads no state; ring-lines-safe-broken: three planted copies
# Last line: "RESULT PASS" (exit 0) or "RESULT FAIL <stages>" (exit 1).

set -u

FW=$(cd "$(dirname "$0")/.." && pwd)
JOBS=${RING_JOBS:-8}
RUN_ID=${RING_RUN_ID:-$(date -u +%Y%m%d-%H%M%S)-local}
OUT=${RING_OUT:-/ws/out/$RUN_ID}
DK_BOARD=nrf54lm20dk/nrf54lm20a/cpuapp
BSIM_BOARD=nrf54lm20bsim/nrf54lm20a/cpuapp
START_LINE="ring-os start:"
RECORDER_LINE="ring-os recorder: boot done, state STANDBY"

mkdir -p "$OUT"
FAILED=""

# run_stage <name> <command...>: runs the command, shows and keeps its output.
run_stage() {
	local name=$1
	shift
	echo "=== stage $name start $(date -u '+%Y-%m-%dT%H:%M:%SZ') log $OUT/$name.log"
	"$@" 2>&1 | tee "$OUT/$name.log"
	local rc=${PIPESTATUS[0]}
	echo "=== stage $name end $(date -u '+%Y-%m-%dT%H:%M:%SZ') exit $rc"
	return "$rc"
}

# Prints the linker's "Memory region" tables from a build log, in build order.
size_report() {
	# Each table is followed by "Generating files from <build>/<image>/zephyr/zephyr.elf",
	# which names the image the table belongs to.
	awk '/Memory region[ \t]+Used Size/ {p=1; buf=$0 "\n"; next}
	     p && /^[ \t]*[A-Za-z0-9_]+:[ \t]+[0-9]+/ {buf=buf $0 "\n"; next}
	     p && /Generating files from .*zephyr\.elf/ {n=split($4, a, "/"); img=(n>=3 ? a[n-2] : $4);
	        printf "image %s (%s)\n%s", img, $4, buf; p=0; next}
	     p {printf "image unknown\n%s", buf; p=0}' "$1"
}

echo "build_all: firmware $FW, outputs $OUT, jobs $JOBS"
echo "build_all: ring_core module $( [ -f "$FW/modules/ring_core/zephyr/module.yml" ] && echo present || echo absent )"

# Stage 1: development kit build.
if run_stage dk west build -p always -b "$DK_BOARD" --sysbuild -d "$OUT/dk" -o=-j"$JOBS" "$FW/app"; then
	echo "--- flash and RAM use, $DK_BOARD (linker memory report; images in build order, see $OUT/dk/domains.yaml)"
	cat "$OUT/dk/domains.yaml" 2>&1
	echo
	size_report "$OUT/dk.log" | tee "$OUT/dk-size.txt"
	# step 4 round 2: static stack frame sums of the chains the screens added (the simulated builds cannot measure a stack peak)
	if ! run_stage stack-report python3 "$FW/tools/stack_report.py" "$OUT/dk"; then
		FAILED="$FAILED stack-report"
	fi
	if [ ! -s "$OUT/dk-size.txt" ]; then
		echo "build_all: no memory report found in $OUT/dk.log"
		FAILED="$FAILED dk-size"
	fi
else
	FAILED="$FAILED dk-build"
fi

# Stage 2: simulated chip build and a 2 s simulated run.
if run_stage bsim-build west build -p always -b "$BSIM_BOARD" --no-sysbuild -d "$OUT/bsim" -o=-j"$JOBS" "$FW/app"; then
	EXE="$OUT/bsim/zephyr/zephyr.exe"
	# One device on the BabbleSim phy; the phy ends the simulation after
	# 2e6 simulated microseconds (2 s).
	SIM_ID="ring_app_$$"
	bsim_run() {
		"$EXE" -s="$SIM_ID" -d=0 &
		local dev=$!
		(cd "$BSIM_OUT_PATH/bin" && ./bs_2G4_phy_v1 -s="$SIM_ID" -D=1 -sim_length=2e6)
		local phy=$?
		wait $dev
		local d=$?
		echo "bsim-run: phy exit $phy, device exit $d"
		[ $phy -eq 0 ] && [ $d -eq 0 ]
	}
	run_stage bsim-run timeout 300 bash -c "$(declare -f bsim_run); EXE='$EXE' SIM_ID='$SIM_ID' bsim_run"
	RC=$?
	if [ $RC -ne 0 ]; then
		FAILED="$FAILED bsim-run(exit $RC)"
	elif ! grep -q -F "$START_LINE" "$OUT/bsim-run.log"; then
		echo "build_all: start line \"$START_LINE\" not found in $OUT/bsim-run.log"
		FAILED="$FAILED bsim-startline"
	else
		echo "build_all: start line found: $(grep -F "$START_LINE" "$OUT/bsim-run.log")"
		# step 6: the product boots through the recorder on the simulated drivers
		if ! grep -q -F "$RECORDER_LINE" "$OUT/bsim-run.log"; then
			echo "build_all: recorder line \"$RECORDER_LINE\" not found in $OUT/bsim-run.log"
			FAILED="$FAILED bsim-recorderline"
		else
			echo "build_all: recorder line found: $(grep -F "$RECORDER_LINE" "$OUT/bsim-run.log")"
		fi
	fi
else
	FAILED="$FAILED bsim-build"
fi

# Stage 3: tests.
TEST_ROOTS=$(find "$FW/tests" -name testcase.yaml 2>&1 | sort)
echo "build_all: test folders found:"
echo "$TEST_ROOTS"
if [ -z "$TEST_ROOTS" ] || ! echo "$TEST_ROOTS" | grep -q testcase.yaml; then
	echo "build_all: no testcase.yaml under $FW/tests"
	FAILED="$FAILED tests-none"
else
	mkdir -p "$OUT/pictures/native_sim"
	if ! run_stage tests-native_sim env RING_PICS="$OUT/pictures/native_sim" west twister -T "$FW/tests" -p native_sim \
		-O "$OUT/twister-native_sim" -j "$JOBS" --inline-logs -v; then
		FAILED="$FAILED tests-native_sim"
	fi
	if ! run_stage pictures-native_sim python3 "$FW/tools/pictures_manifest.py" \
		"$(find "$OUT/twister-native_sim" -path '*tests/screens/ring_screens.all/handler.log' | head -1)" \
		"$OUT/pictures/native_sim" "$OUT/pictures/manifest-native_sim.md"; then
		FAILED="$FAILED pictures-native_sim"
	fi
	# the manifest check must refuse a run that lost a picture and a run that repeated one (two fakes made from the real log)
	pictures_fakes() {
		bash "$FW/tools/pictures_fakes.sh" "$1" "$2" "$OUT/pictures-fakes-work"
	}
	if ! run_stage pictures-fakes pictures_fakes "$(find "$OUT/twister-native_sim" -path '*tests/screens/ring_screens.all/handler.log' | head -1)" \
		"$OUT/pictures/native_sim"; then
		FAILED="$FAILED pictures-fakes"
	fi
	# Each bsim board a test names in platform_allow, with the test folders.
	BSIM_PLAN=$(python3 "$FW/tools/bsim_tests.py" "$FW/tests")
	PLAN_RC=$?
	echo "build_all: bsim test plan: ${BSIM_PLAN:-none}"
	if [ $PLAN_RC -ne 0 ]; then
		FAILED="$FAILED tests-bsim-plan"
	elif [ -n "$BSIM_PLAN" ]; then
		while read -r board dirs; do
			args=()
			for d in $dirs; do args+=(-T "$d"); done
			tag=$(echo "$board" | tr '/' '_')
			mkdir -p "$OUT/pictures/$tag"
			if ! run_stage "tests-$tag" env RING_PICS="$OUT/pictures/$tag" west twister "${args[@]}" -p "$board" \
				-O "$OUT/twister-$tag" -j "$JOBS" --inline-logs -v; then
				FAILED="$FAILED tests-$tag"
			fi
			H=$(find "$OUT/twister-$tag" -path '*tests/screens/ring_screens.all/handler.log' | head -1)
			if [ -n "$H" ]; then
				if ! run_stage "pictures-$tag" python3 "$FW/tools/pictures_manifest.py" "$H" \
					"$OUT/pictures/$tag" "$OUT/pictures/manifest-$tag.md"; then
					FAILED="$FAILED pictures-$tag"
				fi
				if ! run_stage "pictures-fakes-$tag" pictures_fakes "$H" "$OUT/pictures/$tag"; then
					FAILED="$FAILED pictures-fakes-$tag"
				fi
			fi
		done <<< "$BSIM_PLAN"
	fi
fi

# Stage 4: two-device tests. Every tests/bsim/<name>/run.sh runs several simulated
# devices against the BabbleSim phy (twister cannot). A run.sh that understands
# --broken is run a second time with a broken copy, which must fail its test.
for r in $(find "$FW/tests/bsim" -name run.sh 2>&1 | sort); do
	n=$(basename "$(dirname "$r")")
	if ! RING_OUT="$OUT/bsim-$n" run_stage "bsim-$n" bash "$r"; then
		FAILED="$FAILED bsim-$n"
	fi
	if grep -q -e "--broken" "$r"; then
		if ! RING_OUT="$OUT/bsim-$n-broken" run_stage "bsim-$n-broken" bash "$r" --broken; then
			FAILED="$FAILED bsim-$n-broken"
		fi
	fi
done

# Stage 4b: the iPhone part's link and stack settings. The product application's own built settings files (the
# development kit build and the simulated chip build) must hold the same MTU, ACL buffer sizes and system
# workqueue stack as the test ring that ran the iPhone tests (all three include
# modules/ring_iphone/ring_iphone_link.conf). A self test first shows the check can fail: a copy of the test
# ring's settings with the MTU changed must be refused.
# hook_guard <product .config> <name>: 0 when CONFIG_RING_RELAY_TEST_HOOKS is not on in the file, 1 (with a DIFFERENT line) when it is
hook_guard() {
	if grep -q '^CONFIG_RING_RELAY_TEST_HOOKS=y' "$1"; then
		echo "link-settings: DIFFERENT CONFIG_RING_RELAY_TEST_HOOKS is on in $2 (it must be off in the product)"
		return 1
	fi
	echo "link-settings: $2 CONFIG_RING_RELAY_TEST_HOOKS is off"
	return 0
}
link_settings() {
	local ring="$OUT/bsim-iphone/ring/zephyr/.config"
	local rc=0
	if [ ! -f "$ring" ]; then
		echo "link-settings: no test ring settings file $ring"
		return 1
	fi
	sed 's/^CONFIG_BT_L2CAP_TX_MTU=.*/CONFIG_BT_L2CAP_TX_MTU=23/' "$ring" > "$OUT/ring-config-tampered"
	if "$FW/tools/check_link_settings.sh" "$OUT/ring-config-tampered" "$ring" self-test-tampered > "$OUT/link-self-test.log" 2>&1; then
		echo "link-settings: SELF TEST FAILED: a changed MTU was not refused"
		cat "$OUT/link-self-test.log"
		return 1
	fi
	grep "DIFFERENT" "$OUT/link-self-test.log"
	echo "link-settings: self test ok: the changed MTU was refused"
	# two equal wrong values: both sides at MTU 23 must be refused too (the value is pinned to 247)
	sed 's/^CONFIG_BT_L2CAP_TX_MTU=.*/CONFIG_BT_L2CAP_TX_MTU=23/' "$ring" > "$OUT/ring-config-both-23"
	if "$FW/tools/check_link_settings.sh" "$OUT/ring-config-both-23" "$OUT/ring-config-both-23" self-test-both-23 > "$OUT/link-self-test2.log" 2>&1; then
		echo "link-settings: SELF TEST FAILED: two equal MTU values of 23 were not refused"
		return 1
	fi
	grep "DIFFERENT" "$OUT/link-self-test2.log"
	echo "link-settings: self test ok: two equal MTU values of 23 were refused"
	# an application that has CONFIG_RING_IPHONE on and an MTU below 247 cannot be built (BUILD_ASSERT in the module)
	sed 's/^CONFIG_BT_L2CAP_TX_MTU=.*/CONFIG_BT_L2CAP_TX_MTU=100/' "$FW/modules/ring_iphone/ring_iphone_link.conf" > "$OUT/ring_iphone_link_mtu100.conf"
	if west build -p always -b "$BSIM_BOARD" --no-sysbuild -d "$OUT/mtu100" -o=-j"$JOBS" "$FW/tests/bsim/iphone/ring_app" -DRING_IPHONE_LINK_CONF="$OUT/ring_iphone_link_mtu100.conf" > "$OUT/mtu100-build.log" 2>&1; then
		echo "link-settings: a build with CONFIG_RING_IPHONE and MTU 100 SUCCEEDED (it must not)"
		return 1
	fi
	if ! grep -q "ring_iphone needs CONFIG_BT_L2CAP_TX_MTU >= 247" "$OUT/mtu100-build.log"; then
		echo "link-settings: the MTU 100 build failed for another reason (see $OUT/mtu100-build.log)"
		return 1
	fi
	grep -m1 "ring_iphone needs CONFIG_BT_L2CAP_TX_MTU >= 247" "$OUT/mtu100-build.log"
	echo "link-settings: build refused: CONFIG_RING_IPHONE with MTU 100 does not build"
	for p in "dk-product:$OUT/dk/app/zephyr/.config" "bsim-product:$OUT/bsim/zephyr/.config"; do
		if [ ! -f "${p#*:}" ]; then
			echo "link-settings: no settings file ${p#*:}"
			rc=1
			continue
		fi
		"$FW/tools/check_link_settings.sh" "${p#*:}" "$ring" "${p%%:*}" || rc=1
	done
	# step 5: the relay test ring (tests/bsim/relay/ring_app) must hold the product's settings too
	local relay="$OUT/bsim-relay/ring/zephyr/.config"
	if [ ! -f "$relay" ]; then
		echo "link-settings: no relay test ring settings file $relay"
		return 1
	fi
	sed 's/^CONFIG_BT_L2CAP_TX_MTU=.*/CONFIG_BT_L2CAP_TX_MTU=23/' "$relay" > "$OUT/relay-config-tampered"
	if "$FW/tools/check_link_settings.sh" "$OUT/relay-config-tampered" "$relay" self-test-relay-tampered > "$OUT/link-self-test3.log" 2>&1; then
		echo "link-settings: SELF TEST FAILED: a changed MTU of the relay test ring was not refused"
		return 1
	fi
	grep "DIFFERENT" "$OUT/link-self-test3.log"
	echo "link-settings: self test ok: a relay test ring with a changed MTU was refused"
	"$FW/tools/check_link_settings.sh" "$relay" "$ring" relay-test-ring || rc=1
	for p in "dk-product:$OUT/dk/app/zephyr/.config" "bsim-product:$OUT/bsim/zephyr/.config"; do
		"$FW/tools/check_link_settings.sh" "${p#*:}" "$relay" "${p%%:*}-vs-relay-test-ring" || rc=1
	done
	# the Bluetooth settings the relay service depends on beyond the shared file: the same value in the product and in the relay test ring
	for p in "dk-product:$OUT/dk/app/zephyr/.config" "bsim-product:$OUT/bsim/zephyr/.config"; do
		for k in CONFIG_BT_PERIPHERAL CONFIG_BT_SMP CONFIG_BT_SMP_SC_ONLY CONFIG_BT_SMP_APP_PAIRING_ACCEPT CONFIG_BT_MAX_CONN CONFIG_BT_MAX_PAIRED \
			CONFIG_BT_ID_MAX CONFIG_BT_ATT_TX_COUNT CONFIG_BT_GATT_AUTO_SEC_REQ CONFIG_RING_RELAY CONFIG_RING_IPHONE CONFIG_RING_INBOX; do
			local pv rv
			pv=$(grep -E "^$k=" "${p#*:}" | head -1 | cut -d= -f2)
			rv=$(grep -E "^$k=" "$relay" | head -1 | cut -d= -f2)
			echo "link-settings: ${p%%:*} $k=${pv:-unset} relay-test-ring $k=${rv:-unset}"
			if [ "$k" = "CONFIG_RING_RELAY" ] && [ "$pv" != "y" ]; then
				echo "link-settings: DIFFERENT the relay service is not in ${p%%:*} (CONFIG_RING_RELAY=${pv:-unset})"
				rc=1
			fi
			if [ "$pv" != "$rv" ]; then
				echo "link-settings: DIFFERENT $k (${p%%:*} ${pv:-unset}, relay test ring ${rv:-unset})"
				rc=1
			fi
		done
		# the test hooks of the relay (block the Out queue, hold the iPhone part's session start) are for the test ring only: the product must not have them
		if ! hook_guard "${p#*:}" "${p%%:*}"; then
			rc=1
		fi
	done
	# self test of the hook guard: a copy of a product settings file with the option on must be refused
	cp "$OUT/dk/app/zephyr/.config" "$OUT/dk-config-hooks-on"
	echo "CONFIG_RING_RELAY_TEST_HOOKS=y" >> "$OUT/dk-config-hooks-on"
	if hook_guard "$OUT/dk-config-hooks-on" self-test-hooks-on > "$OUT/link-self-test4.log" 2>&1; then
		echo "link-settings: SELF TEST FAILED: a product settings file with the test hooks on was not refused"
		return 1
	fi
	grep "DIFFERENT" "$OUT/link-self-test4.log"
	echo "link-settings: self test ok: a product settings file with the relay test hooks on was refused"
	return $rc
}
if ! run_stage link-settings link_settings; then
	FAILED="$FAILED link-settings"
fi

# Stage 4c (step 5): the relay part calls nothing in the core. The module's sources must not name the core, the glue, the devices, the control
# or the screens (headers or functions). A copy with one such include must be refused (a self test, so the check can fail).
relay_no_core() {
	local pat='ring_(core|glue|devices|control|screens)|rglue_|rdev_|rctl_|rscr_|rc_core|rc_ev'
	local d="$FW/modules/ring_relay"
	local n
	n=$(grep -r -n -E "$pat" "$d/src" "$d/include" 2>&1 | wc -l | tr -d ' ')
	echo "relay-no-core: hits in $d/src and $d/include for /$pat/: $n"
	grep -r -n -E "$pat" "$d/src" "$d/include" 2>&1
	rm -rf "$OUT/relay-no-core-fake"
	mkdir -p "$OUT/relay-no-core-fake"
	cp -r "$d/src" "$d/include" "$OUT/relay-no-core-fake/"
	echo '#include <ring_glue/rglue.h>' >> "$OUT/relay-no-core-fake/src/rrl_bt.c"
	if ! grep -r -q -E "$pat" "$OUT/relay-no-core-fake/src"; then
		echo "relay-no-core: SELF TEST FAILED: a copy with a glue include was not found"
		return 1
	fi
	echo "relay-no-core: self test ok: a copy with a glue include is found by the same search"
	[ "$n" = "0" ]
}
if ! run_stage relay-no-core relay_no_core; then
	FAILED="$FAILED relay-no-core"
fi

# Stages 4d to 4g (step 6): the recorder's rules that a search of the sources and the built settings can show. Each has a
# self test: a planted copy that the same check must refuse.
STEP6_MODS="ring_rhw ring_store ring_audio ring_xfer ring_power ring_motor ring_sys ring_factory ring_recorder"
# recorder-one-mic-path: the microphone rail switched on (design/firmware.md l.342, rhw.h rail_set with RHW_RAIL_MIC and
# true or 1) appears once, in modules/ring_recorder/src/rrec_mics.c
MIC_ON_PAT='rail_set\([[:space:]]*RHW_RAIL_MIC[[:space:]]*,[[:space:]]*(true|1)[[:space:]]*,'
mic_on_hits() {
	grep -r -n -E "$MIC_ON_PAT" "$@" 2>&1
}
recorder_one_mic_path() {
	local dirs=() m hits n where fake
	for m in $STEP6_MODS; do
		[ -d "$FW/modules/$m/src" ] && dirs+=("$FW/modules/$m/src")
	done
	dirs+=("$FW/app/src")
	hits=$(mic_on_hits "${dirs[@]}")
	n=$(printf '%s\n' "$hits" | grep -c -E "$MIC_ON_PAT")
	echo "recorder-one-mic-path: hits for /$MIC_ON_PAT/ in ${dirs[*]}: $n"
	printf '%s\n' "$hits"
	where=$(printf '%s\n' "$hits" | grep -c -F "modules/ring_recorder/src/rrec_mics.c:")
	fake="$OUT/recorder-one-mic-path-fake"
	rm -rf "$fake"
	mkdir -p "$fake"
	cp -r "$FW/modules/ring_store/src" "$fake/"
	echo 'static void fake_mic_on(void) { (void)rhw_pmic()->rail_set(RHW_RAIL_MIC, true, "fake"); }' >> "$fake/src/rst.c"
	if [ "$(mic_on_hits "${dirs[@]}" "$fake/src" | grep -c -E "$MIC_ON_PAT")" != "$((n + 1))" ]; then
		echo "recorder-one-mic-path: SELF TEST FAILED: a second call in a copy of ring_store was not found"
		return 1
	fi
	echo "recorder-one-mic-path: self test ok: a second call in a copy of ring_store is found by the same search"
	[ "$n" = "1" ] && [ "$where" = "1" ]
}
if ! run_stage recorder-one-mic-path recorder_one_mic_path; then
	FAILED="$FAILED recorder-one-mic-path"
fi

# recorder-no-start-path: no unit of step 6 but the recorder names the gesture entry or the long press (design/firmware.md
# l.209); the recorder itself only carries out the core's actions
START_PAT='rglue_input|rc_core_input|RC_EV_LONG_PRESS'
recorder_no_start_path() {
	local dirs=() m n fake
	for m in ring_store ring_audio ring_xfer ring_power ring_motor ring_sys ring_factory; do
		[ -d "$FW/modules/$m" ] && dirs+=("$FW/modules/$m")
	done
	n=$(grep -r -n -E "$START_PAT" "${dirs[@]}" 2>&1 | grep -c -E "$START_PAT")
	echo "recorder-no-start-path: hits for /$START_PAT/ in ${dirs[*]}: $n"
	grep -r -n -E "$START_PAT" "${dirs[@]}" 2>&1
	fake="$OUT/recorder-no-start-path-fake"
	rm -rf "$fake"
	mkdir -p "$fake"
	cp -r "$FW/modules/ring_xfer/src" "$fake/"
	echo 'static void fake_press(void) { rglue_input(RC_SW_CENTRE, true); }' >> "$fake/src/rxf_class.c"
	if ! grep -r -q -E "$START_PAT" "$fake/src"; then
		echo "recorder-no-start-path: SELF TEST FAILED: a copy with rglue_input was not found"
		return 1
	fi
	echo "recorder-no-start-path: self test ok: a copy of ring_xfer with rglue_input is found by the same search"
	[ "$n" = "0" ]
}
if ! run_stage recorder-no-start-path recorder_no_start_path; then
	FAILED="$FAILED recorder-no-start-path"
fi

# recorder-no-raw-pins: no chip pin by number in step 6 (design/firmware.md l.77: pins come from the board files of step 7)
PIN_PAT='(^|[^A-Za-z0-9_])P[0-9]\.[0-9]{1,2}([^0-9]|$)|NRF_GPIO_PIN_MAP|<&gpio[0-9]+[[:space:]]+[0-9]+'
pin_hits() {
	grep -r -n -E --include='*.c' --include='*.h' --include='*.overlay' --include='*.dts' --include='*.dtsi' \
		--include='*.conf' "$PIN_PAT" "$@" 2>&1
}
recorder_no_raw_pins() {
	local dirs=() m t n fake
	for m in $STEP6_MODS; do
		[ -d "$FW/modules/$m" ] && dirs+=("$FW/modules/$m")
	done
	for t in rhw store audio xfer power motor sys factory recorder; do
		[ -d "$FW/tests/$t" ] && dirs+=("$FW/tests/$t")
	done
	dirs+=("$FW/app/src" "$FW/app/boards")
	n=$(pin_hits "${dirs[@]}" | grep -c -E "$PIN_PAT")
	echo "recorder-no-raw-pins: hits for /$PIN_PAT/ in ${dirs[*]}: $n"
	pin_hits "${dirs[@]}"
	fake="$OUT/recorder-no-raw-pins-fake"
	rm -rf "$fake"
	mkdir -p "$fake"
	cp "$FW/app/boards/nrf54lm20bsim_nrf54lm20a_cpuapp.overlay" "$fake/planted.overlay"
	echo '/ { fake_pin: fake-pin { gpios = <&gpio1 24 0>; }; };' >> "$fake/planted.overlay"
	if [ "$(pin_hits "$fake" | grep -c -E "$PIN_PAT")" = "0" ]; then
		echo "recorder-no-raw-pins: SELF TEST FAILED: a planted overlay with a pin by number was not found"
		return 1
	fi
	echo "recorder-no-raw-pins: self test ok: a planted overlay with <&gpio1 24 is found by the same search"
	[ "$n" = "0" ]
}
if ! run_stage recorder-no-raw-pins recorder_no_raw_pins; then
	FAILED="$FAILED recorder-no-raw-pins"
fi

# recorder-product-drivers: the simulated drivers only in the simulated-chip build (decision D11b)
sim_guard() {
	# <.config> <name> <want: on|off>: 0 when CONFIG_RING_RHW_SIM is as wanted (and the test read-outs are off)
	local on=0
	grep -q '^CONFIG_RING_RHW_SIM=y' "$1" && on=1
	if grep -q '^CONFIG_RING_RECORDER_TEST_HOOKS=y' "$1"; then
		echo "recorder-product-drivers: DIFFERENT the recorder's test read-outs are on in $2"
		return 1
	fi
	if [ "$3" = "off" ] && [ $on -eq 1 ]; then
		echo "recorder-product-drivers: DIFFERENT CONFIG_RING_RHW_SIM is on in $2 (the simulated drivers and the hooks of rhw_sim.h)"
		return 1
	fi
	if [ "$3" = "on" ] && [ $on -eq 0 ]; then
		echo "recorder-product-drivers: DIFFERENT CONFIG_RING_RHW_SIM is off in $2"
		return 1
	fi
	echo "recorder-product-drivers: $2 CONFIG_RING_RHW_SIM is $3"
	return 0
}
recorder_product_drivers() {
	local dk="$OUT/dk/app/zephyr/.config" bs="$OUT/bsim/zephyr/.config" rc=0 f
	for f in "$dk" "$bs"; do
		if [ ! -f "$f" ]; then
			echo "recorder-product-drivers: no settings file $f"
			return 1
		fi
	done
	sim_guard "$dk" dk-product off || rc=1
	sim_guard "$bs" bsim-product on || rc=1
	echo "recorder-product-drivers: real driver files compiled in the kit build (decision D15):"
	find "$OUT/dk/app" -name '*_hw_real.c.obj' 2>&1 | sed 's|.*/||' | sort
	echo "recorder-product-drivers: simulated driver files in the kit build: $(find "$OUT/dk/app" -name 'sim_*.c.obj' 2>&1 | grep -c 'sim_')"
	cp "$dk" "$OUT/dk-config-sim-on"
	echo "CONFIG_RING_RHW_SIM=y" >> "$OUT/dk-config-sim-on"
	if sim_guard "$OUT/dk-config-sim-on" self-test-sim-on off > "$OUT/recorder-drivers-self-test.log" 2>&1; then
		echo "recorder-product-drivers: SELF TEST FAILED: a kit settings file with the simulated drivers on was not refused"
		return 1
	fi
	grep "DIFFERENT" "$OUT/recorder-drivers-self-test.log"
	echo "recorder-product-drivers: self test ok: a kit settings file with CONFIG_RING_RHW_SIM=y was refused"
	return $rc
}
if ! run_stage recorder-product-drivers recorder_product_drivers; then
	FAILED="$FAILED recorder-product-drivers"
fi

# Stage 5: broken copies of the logic suites. Every tests/<name>/broken_run.sh builds a copy of its
# module with one named fault and passes only when the suite runs and the named case fails.
for r in $(find "$FW/tests" -name broken_run.sh 2>&1 | sort); do
	n=$(basename "$(dirname "$r")")
	if ! RING_OUT="$OUT/broken-$n" run_stage "broken-$n" bash "$r"; then
		FAILED="$FAILED broken-$n"
	fi
done

# Step 7 (the ring's board files) begin. Stage 6: the application for the ring itself and its devicetree against the
# circuit's netlist (firmware/docs/board-notes.md). The netlist is a copy in the board folder (the build server receives
# firmware/ only); tools/check_ring_pins.py compares it with design/ecad/ring/netlist.csv wherever that file exists.
RING_BOARD=ringrec/nrf54lm20a/cpuapp
RING_NETLIST="$FW/boards/ringrec/netlist.csv"
RING_NETLIST_SRC="$FW/../design/ecad/ring/netlist.csv"
ring_drivers() {
	local cfg="$OUT/ring/app/zephyr/.config" nm sz o t f
	if [ ! -f "$cfg" ]; then
		echo "ring-drivers: no settings file $cfg"
		return 1
	fi
	sim_guard "$cfg" ring-product off || return 1
	grep -E '^(# )?CONFIG_RING_POWER_REAL[ =]' "$cfg" 2>&1
	nm=$(sed -n 's/^CMAKE_NM:FILEPATH=//p' "$OUT/ring/app/CMakeCache.txt")
	sz="${nm%nm}size"
	echo "ring-drivers: real driver files compiled in the ring build (code size from $sz, functions from $nm):"
	for o in $(find "$OUT/ring/app/modules" \( -name '*_hw_real.c.obj' -o -name 'rhw_clock_real.c.obj' -o -name 'rscr_real.c.obj' \) 2>&1 | sort); do
		t=$("$sz" "$o" | awk 'NR==2 {print $1}')
		if [ "${t:-0}" -gt 0 ]; then
			echo "ring-drivers: $(basename "$o") text $t bytes: real code"
		else
			echo "ring-drivers: $(basename "$o") text ${t:-0} bytes: empty stub (no code)"
		fi
		"$nm" --defined-only "$o" | awk '$2 ~ /^[Tt]$/ {print "ring-drivers:   function " $3}'
	done
	for f in rau_hw_real rst_hw_real rmo_hw_real rpw_hw_real rsy_hw_real rxf_hw_real rfa_hw_real; do
		if [ -z "$(find "$OUT/ring/app/modules" -name "$f.c.obj" 2>&1)" ]; then
			echo "ring-drivers: $f.c not compiled in the ring build"
		fi
	done
	echo "ring-drivers: the kit's drivers compiled for the ring's nodes:"
	find "$OUT/ring/app/zephyr" -name '*.c.obj' 2>&1 | sed 's|.*/||' | sort | grep -E \
		'^(dmic_nrfx_pdm|sdhc_spi|sdmmc_subsys|spi_nrfx_spim|mfd_npm13xx|regulator_npm13xx|npm13xx_charger|uart_nrfx_uarte|udc_dwc2|i2c_nrfx_twim|retained_mem_zephyr_ram|retained_mem_nrf_gpregret|wdt_nrfx|zms|settings_zms|gpio_nrfx)\.c\.obj$' |
		sed 's/^/ring-drivers:   /'
}
ring_ram() {
	local nm elf="$OUT/ring/app/zephyr/zephyr.elf"
	nm=$(sed -n 's/^CMAKE_NM:FILEPATH=//p' "$OUT/ring/app/CMakeCache.txt")
	echo "# ring build: every RAM symbol, largest first: address size type name file:line (nm -S -l --size-sort -r)"
	"$nm" -S -l --size-sort -r "$elf" | awk '$1 ~ /^2/ && $3 ~ /^[bBdD]$/' | sed 's|/ws/||'
}
ring_pins() {
	echo "ring-pins: netlist copy $RING_NETLIST sha256 $(sha256sum "$RING_NETLIST" 2>&1 | cut -d' ' -f1)"
	if [ -f "$RING_NETLIST_SRC" ]; then
		echo "ring-pins: the copy is compared with $RING_NETLIST_SRC here (the check below, --source-netlist)"
	else
		echo "ring-pins: the copy was compared with design/ecad/ring/netlist.csv on the Mac by tools/remote.sh before this copy was sent (its refusal rule, ruling S7-01); design/ is not here"
	fi
	python3 "$FW/tools/check_ring_pins.py" "$OUT/ring/app/zephyr/zephyr.dts" "$RING_NETLIST" --source-netlist "$RING_NETLIST_SRC"
}
# ring_pins_plant <file> <old text> <new text>: replaces the first <old text> of <file> (which must hold it)
ring_pins_plant() {
	python3 -c 'import sys
p, old, new = sys.argv[1:4]
s = open(p, newline="").read()
if old not in s:
    sys.exit("planted copy: text not found in " + p)
open(p, "w", newline="").write(s.replace(old, new, 1))' "$1" "$2" "$3"
}
# ring_pins_verdict <name> <signal> <check log> <check exit>: 0 when the check exited 1 and its failing list is exactly <signal>
ring_pins_verdict() {
	local name=$1 sig=$2 log=$3 rc=$4 got
	grep -E '^(DIFFERENT|NO NODE |UNEXPECTED|UNLISTED|UNSEEN)|RESULT' "$log"
	if [ "$rc" -ne 1 ]; then
		echo "ring-pins-broken: $name: SELF TEST FAILED: the check exited $rc on the planted copy (1 wanted)"
		return 1
	fi
	got=$(sed -n 's/^check_ring_pins: RESULT FAIL [0-9]* signals checked; failing: //p' "$log")
	if [ "$got" != "$sig" ]; then
		echo "ring-pins-broken: $name: SELF TEST FAILED: the check failed on \"$got\", not on exactly \"$sig\""
		return 1
	fi
	echo "ring-pins-broken: $name: self test ok: the planted copy fails on $sig alone"
	return 0
}
# ring_pins_case <name> <signal> <file in boards/ringrec> <old text> <new text>: a copy of the board with the first
# <old text> of <file> replaced, configured (cmake only, no sysbuild), checked; 0 when the check fails naming exactly <signal>
ring_pins_case() {
	local name=$1 sig=$2 file=$3 old=$4 new=$5 root="$OUT/ring-broken-$1-root" d="$OUT/ring-broken-$1" rc
	rm -rf "$root" "$d"
	mkdir -p "$root"
	cp -r "$FW/boards" "$root/boards"
	ring_pins_plant "$root/boards/ringrec/$file" "$old" "$new" || return 1
	diff "$FW/boards/ringrec/$file" "$root/boards/ringrec/$file"
	if ! west build -p always --cmake-only -b "$RING_BOARD" --no-sysbuild -d "$d" "$FW/app" -- -DBOARD_ROOT="$root" > "$d.log" 2>&1; then
		echo "ring-pins-broken: $name: the planted copy did not configure (see $d.log)"
		return 1
	fi
	python3 "$FW/tools/check_ring_pins.py" "$d/zephyr/zephyr.dts" "$RING_NETLIST" > "$d-check.log" 2>&1
	rc=$?
	ring_pins_verdict "$name" "$sig" "$d-check.log" $rc || return 1
	rm -rf "$root" "$d"
	return 0
}
# ring_pins_net_case <name> <signal> <old text> <new text>: a copy of the netlist with one row changed, checked against
# the ring build's own devicetree
ring_pins_net_case() {
	local name=$1 sig=$2 net="$OUT/ring-broken-$1-netlist.csv" rc
	cp "$RING_NETLIST" "$net"
	ring_pins_plant "$net" "$3" "$4" || return 1
	diff "$RING_NETLIST" "$net"
	python3 "$FW/tools/check_ring_pins.py" "$OUT/ring/app/zephyr/zephyr.dts" "$net" > "$OUT/ring-broken-$name-check.log" 2>&1
	rc=$?
	ring_pins_verdict "$name" "$sig" "$OUT/ring-broken-$name-check.log" $rc
}
ring_pins_broken() {
	local rc=0
	local D=ringrec_nrf54lm20a_cpuapp.dts P=ringrec_nrf54lm20a_cpuapp-pinctrl.dtsi
	# a wrong pin in a GPIO property, in a default pin state; a removed property (step 7)
	ring_pins_case motor MOTOR $D 'gpios = <&gpio3 1 GPIO_ACTIVE_HIGH>;' 'gpios = <&gpio3 2 GPIO_ACTIVE_HIGH>;' || rc=1
	ring_pins_case sd-miso SD_MISO $P '<NRF_PSEL(SPIM_MISO, 2, 4)>;' '<NRF_PSEL(SPIM_MISO, 2, 3)>;' || rc=1
	ring_pins_case lcd-te LCD_TE $D 'te-gpios = <&gpio1 14 GPIO_ACTIVE_HIGH>;' '' || rc=1
	# fix round 1 (S7-04): a wrong port, a removed node, a disabled node, an extra pin, a wrong flag
	ring_pins_case port PMIC_INT $D 'host-int-gpios = <&gpio1 28 GPIO_ACTIVE_HIGH>;' \
		'host-int-gpios = <&gpio2 28 GPIO_ACTIVE_HIGH>;' || rc=1
	ring_pins_case node-removed JOY_LEFT $D '&wdt31 {' $'/delete-node/ &ring_joy_left;\n\n&wdt31 {' || rc=1
	ring_pins_case node-disabled JOY_DOWN $D 'ring_joy_down: joy_down {' \
		$'ring_joy_down: joy_down {\n\t\t\tstatus = "disabled";' || rc=1
	ring_pins_case extra-pin 'unexpected-pins(1)' $D 'oled-pwr-en-gpios = ' \
		$'extra-test-gpios = <&gpio1 24 0>;\n\t\toled-pwr-en-gpios = ' || rc=1
	ring_pins_case flag JOY_UP $D '<&gpio0 6 (GPIO_PULL_UP | GPIO_ACTIVE_LOW)>' '<&gpio0 6 GPIO_ACTIVE_LOW>' || rc=1
	# fix round 1 (S7-04): an unknown net and a changed row in a copy of the netlist
	ring_pins_net_case unknown-net NEWNET ',U1,E6,P1.24,no_connect' 'NEWNET,U1,E6,P1.24,bidirectional' || rc=1
	ring_pins_net_case netlist-row LCD_RST 'LCD_RST,U1,H5,P1.07,' 'LCD_RST,U1,H5,P1.08,' || rc=1
	return $rc
}
# ring-production (fix round 1, design/firmware.md l.1061): the ring's production settings, no UART output: compile only.
# ring_production_verdict <app zephyr dir> <mcuboot zephyr dir> <pin check log> (fix round 2, S7R-02 and S7R-08): 0 when
# both .config files and the app's zephyr.dts exist, no UART is on in either image, and the pin check in production
# mode passes on the app's devicetree (DBG_TX a hog, input with pull-down; uart20 naming no pin)
ring_production_verdict() {
	local a=$1 m=$2 log=$3 rc=0 f
	for f in "$a/.config" "$m/.config" "$a/zephyr.dts"; do
		if [ ! -s "$f" ]; then
			echo "ring-production: MISSING input file $f"
			return 1
		fi
	done
	for f in "$a/.config" "$m/.config"; do
		grep -E '^(# )?CONFIG_(SERIAL|UART_CONSOLE)[ =]' "$f" 2>&1 | sed "s|^|ring-production: $f |"
		if grep -q -E '^CONFIG_(SERIAL|UART_CONSOLE)=y' "$f"; then
			echo "ring-production: DIFFERENT a UART is on in $f"
			rc=1
		fi
	done
	python3 "$FW/tools/check_ring_pins.py" --production "$a/zephyr.dts" "$RING_NETLIST" > "$log" 2>&1
	f=$?
	grep -E '^(SAME DBG_TX|DIFFERENT|NO NODE |UNEXPECTED|UNLISTED|UNSEEN)|RESULT' "$log" | sed 's|^|ring-production: |'
	if [ $f -ne 0 ]; then
		echo "ring-production: DIFFERENT the pin check in production mode exited $f"
		rc=1
	fi
	return $rc
}
ring_production_check() {
	ring_production_verdict "$OUT/ring-prod/app/zephyr" "$OUT/ring-prod/mcuboot/zephyr" "$OUT/ring-prod-pins.log"
}
# ring_production_case <name> <expected line> <how>: a copy of the production build's three input files, changed by
# <how> (uart: CONFIG_SERIAL=y in the app's .config; pulldown: DBG_TX's hog without its pull-down; missing: no MCUboot
# .config); 0 when the verdict fails and prints <expected line>
ring_production_case() {
	local name=$1 want=$2 how=$3 d="$OUT/ring-prod-broken-$1" rc got
	rm -rf "$d"
	mkdir -p "$d/app" "$d/mcuboot"
	cp "$OUT/ring-prod/app/zephyr/.config" "$OUT/ring-prod/app/zephyr/zephyr.dts" "$d/app/"
	cp "$OUT/ring-prod/mcuboot/zephyr/.config" "$d/mcuboot/"
	case "$how" in
	uart) echo "CONFIG_SERIAL=y" >> "$d/app/.config"; grep -n '^CONFIG_SERIAL=y' "$d/app/.config" || return 1 ;;
	pulldown)
		ring_pins_plant "$d/app/zephyr.dts" 'gpios = < 0xf 0x20 >;' 'gpios = < 0xf 0x0 >;' || return 1
		grep -n 'gpios = < 0xf 0x0 >;' "$d/app/zephyr.dts" || return 1 ;;
	missing) rm "$d/mcuboot/.config"; [ ! -e "$d/mcuboot/.config" ] && echo "planted: $d/mcuboot/.config removed" ;;
	uart-mcuboot) echo "CONFIG_UART_CONSOLE=y" >> "$d/mcuboot/.config"; grep -n '^CONFIG_UART_CONSOLE=y' "$d/mcuboot/.config" || return 1 ;;
	uart20-on)
		# fix round 3 (S7T-04): uart20 enabled in the devicetree, the path that replaced the old "uart20 is enabled" test
		python3 -c 'import sys
p = sys.argv[1]
s = open(p).read()
i = s.index("uart20: uart@c6000 {")
j = s.index("status = \"disabled\";", i)
open(p, "w").write(s[:j] + "status = \"okay\";" + s[j + len("status = \"disabled\";"):])' "$d/app/zephyr.dts" || return 1
		awk '/uart20: uart@c6000 \{/{p=1} p&&/status =/{print "planted: uart20 " $0; exit}' "$d/app/zephyr.dts" | grep -q okay || return 1
		echo "planted: uart20 status okay" ;;
	esac
	ring_production_verdict "$d/app" "$d/mcuboot" "$d/pins.log" > "$d/verdict.log" 2>&1
	rc=$?
	cat "$d/verdict.log"
	if [ $rc -ne 1 ]; then
		echo "ring-production-broken: $name: SELF TEST FAILED: the verdict exited $rc (1 wanted)"
		return 1
	fi
	case "$want" in
	failing=*)
		# fix round 3 (S7T-04): the pin check's whole failing list, not a substring
		got=$(sed -n 's/^ring-production: check_ring_pins: RESULT FAIL [0-9]* signals checked; failing: //p' "$d/verdict.log")
		if [ "$got" != "${want#failing=}" ]; then
			echo "ring-production-broken: $name: SELF TEST FAILED: the pin check failed on \"$got\", not on exactly \"${want#failing=}\""
			return 1
		fi ;;
	*)
		if ! grep -q -F "$want" "$d/verdict.log"; then
			echo "ring-production-broken: $name: SELF TEST FAILED: no line \"$want\""
			return 1
		fi ;;
	esac
	echo "ring-production-broken: $name: self test ok: refused with \"$want\""
	return 0
}
ring_production_broken() {
	local rc=0
	ring_production_case uart "ring-production: DIFFERENT a UART is on in" uart || rc=1
	ring_production_case pulldown "failing=DBG_TX" pulldown || rc=1
	ring_production_case missing "ring-production: MISSING input file" missing || rc=1
	ring_production_case uart-mcuboot "ring-production: DIFFERENT a UART is on in $OUT/ring-prod-broken-uart-mcuboot/mcuboot/.config" uart-mcuboot || rc=1
	ring_production_case uart20-on "failing=unexpected-pins(2)" uart20-on || rc=1
	return $rc
}
# ring-lines-safe (fix round 3, S7T-01): a static check of modules/ring_store/src/rst_hw_real.c: lines_safe() reads no
# state and makes SD_CS disconnected and applies spi00's sleep pin state; b_suspend() and b_resume() have exactly the
# wrapper shapes that end in lines_safe() (b_suspend on every return, b_resume on every failure); suspend_inner,
# resume_inner and bus_first_init are called only through those wrappers; the sdbus table names the two wrappers. It sees
# the text of the file only: not what the called kit functions do, not the hardware.
# ring_lines_check <file>: prints SAME or DIFFERENT per rule and "failing: <rules>"; 0 when every rule holds
ring_lines_check() {
	python3 - "$1" <<'PYCHECK'
import re, sys
src = open(sys.argv[1]).read()
code = re.sub(r"/\*.*?\*/", " ", src, flags=re.S)
def body(name):
    m = re.search(r"static int " + name + r"\(void\)\s*\{(.*?)\n\}", code, flags=re.S)
    return " ".join(m.group(1).split()) if m else None
fail = []
def rule(name, ok, what):
    print("ring-lines-safe: %s %s: %s" % ("SAME" if ok else "DIFFERENT", name, what))
    if not ok and name not in fail:
        fail.append(name)
ls = body("lines_safe")
rule("lines_safe", ls is not None and "GPIO_DISCONNECTED" in ls and "pinctrl_apply_state(spi00_pins, PINCTRL_STATE_SLEEP)" in ls
     and not re.search(r"\b(if|bus_up|device_is_ready|pm_device_action_run|return 0)\b", ls),
     "no condition, no device state; SD_CS GPIO_DISCONNECTED and spi00's sleep pin state: %s" % ls)
bs = body("b_suspend")
rule("b_suspend", bs == "int r = suspend_inner(); int s = lines_safe(); return r != 0 ? r : s;",
     "one wrapper that always ends in lines_safe(): %s" % bs)
br = body("b_resume")
rule("b_resume", br == "int r = resume_inner(); if (r != 0) { (void)lines_safe(); } return r;",
     "lines_safe() on every failure: %s" % br)
for f, n in (("suspend_inner", 2), ("resume_inner", 2)):
    c = len(re.findall(r"\b" + f + r"\(", code))
    rule(f, c == n, "%d occurrences (its definition and the one call in its wrapper: %d wanted)" % (c, n))
ri = body("resume_inner") or ""
calls = len(re.findall(r"\bbus_first_init\(\)\s*;", code))
rule("bus_first_init", "return bus_first_init();" in ri and calls == 1,
     "called once, from resume_inner: %d call(s)" % calls)
rule("sdbus", ".suspend = b_suspend, .resume = b_resume" in code, "the sdbus table names the two wrappers")
if fail:
    print("ring-lines-safe: RESULT FAIL failing: " + " ".join(fail))
    sys.exit(1)
print("ring-lines-safe: RESULT PASS")
PYCHECK
}
ring_lines_case() {
	local name=$1 sig=$2 old=$3 new=$4 f="$OUT/ring-lines-broken-$1.c" got rc
	cp "$FW/modules/ring_store/src/rst_hw_real.c" "$f"
	ring_pins_plant "$f" "$old" "$new" || return 1
	diff "$FW/modules/ring_store/src/rst_hw_real.c" "$f"
	ring_lines_check "$f" > "$f.log" 2>&1
	rc=$?
	cat "$f.log"
	got=$(sed -n 's/^ring-lines-safe: RESULT FAIL failing: //p' "$f.log")
	if [ $rc -ne 1 ] || [ "$got" != "$sig" ]; then
		echo "ring-lines-safe-broken: $name: SELF TEST FAILED: exit $rc, failing \"$got\" (wanted exit 1, \"$sig\")"
		return 1
	fi
	echo "ring-lines-safe-broken: $name: self test ok: the planted copy fails on $sig alone"
}
ring_lines_safe() {
	ring_lines_check "$FW/modules/ring_store/src/rst_hw_real.c"
}
ring_lines_safe_broken() {
	local rc=0
	ring_lines_case early-return b_suspend 'int r = suspend_inner();' $'int r = suspend_inner();\n\n\tif (r != 0) {\n\t\treturn r;\n\t}' || rc=1
	ring_lines_case gated lines_safe $'static int lines_safe(void)\n{\n' $'static int lines_safe(void)\n{\n\tif (!bus_up) {\n\t\treturn 0;\n\t}\n' || rc=1
	ring_lines_case resume-no-safe b_resume '(void)lines_safe();' '(void)0;' || rc=1
	return $rc
}
if ! run_stage ring-lines-safe ring_lines_safe; then
	FAILED="$FAILED ring-lines-safe"
fi
if ! run_stage ring-lines-safe-broken ring_lines_safe_broken; then
	FAILED="$FAILED ring-lines-safe-broken"
fi
if run_stage ring west build -p always -b "$RING_BOARD" --sysbuild -d "$OUT/ring" -o=-j"$JOBS" "$FW/app" -- -DBOARD_ROOT="$FW"; then
	echo "--- flash and RAM use, $RING_BOARD (linker memory report; images in build order, see $OUT/ring/domains.yaml)"
	cat "$OUT/ring/domains.yaml" 2>&1
	echo
	size_report "$OUT/ring.log" | tee "$OUT/ring-size.txt"
	if [ ! -s "$OUT/ring-size.txt" ]; then
		echo "build_all: no memory report found in $OUT/ring.log"
		FAILED="$FAILED ring-size"
	fi
	if ! run_stage ring-drivers ring_drivers; then
		FAILED="$FAILED ring-drivers"
	fi
	if ! run_stage ring-ram ring_ram; then
		FAILED="$FAILED ring-ram"
	fi
	if ! run_stage ring-pins ring_pins; then
		FAILED="$FAILED ring-pins"
	fi
	if ! run_stage ring-pins-broken ring_pins_broken; then
		FAILED="$FAILED ring-pins-broken"
	fi
else
	FAILED="$FAILED ring-build"
fi
if run_stage ring-production west build -p always -b "$RING_BOARD" --sysbuild -d "$OUT/ring-prod" -o=-j"$JOBS" "$FW/app" -- \
	-DBOARD_ROOT="$FW" -Dapp_EXTRA_CONF_FILE="$FW/app/ringrec_production.conf" \
	-Dapp_EXTRA_DTC_OVERLAY_FILE="$FW/boards/ringrec/ringrec_production.overlay" \
	-Dmcuboot_EXTRA_CONF_FILE="$FW/boards/ringrec/ringrec_production_mcuboot.conf" \
	-Dmcuboot_EXTRA_DTC_OVERLAY_FILE="$FW/boards/ringrec/ringrec_production.overlay"; then
	echo "--- flash and RAM use, $RING_BOARD production settings (linker memory report)"
	size_report "$OUT/ring-production.log" | tee "$OUT/ring-prod-size.txt"
	if [ ! -s "$OUT/ring-prod-size.txt" ]; then
		FAILED="$FAILED ring-production-size"
	fi
	if ! run_stage ring-production-check ring_production_check; then
		FAILED="$FAILED ring-production-check"
	fi
	if ! run_stage ring-production-broken ring_production_broken; then
		FAILED="$FAILED ring-production-broken"
	fi
else
	FAILED="$FAILED ring-production"
fi
# Step 7 end

echo "build_all: logs in $OUT"
if [ -z "$FAILED" ]; then
	echo "RESULT PASS"
	exit 0
fi
echo "RESULT FAIL$FAILED"
exit 1
