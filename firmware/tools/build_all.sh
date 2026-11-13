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

echo "build_all: logs in $OUT"
if [ -z "$FAILED" ]; then
	echo "RESULT PASS"
	exit 0
fi
echo "RESULT FAIL$FAILED"
exit 1
