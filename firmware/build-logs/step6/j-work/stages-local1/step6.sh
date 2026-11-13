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

# Stage 5: broken copies of the logic suites. Every tests/<name>/broken_run.sh builds a copy of its
