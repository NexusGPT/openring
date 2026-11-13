# power notes: unit U5 of software step 6 (battery levels, charger, ship mode, current limit, reset causes)

Builder: U5 helper, 2026-11-13 05:00 to 05:55 CET (`date`). Version read: commit 2d3d5c2. No git was run.
"FW l.N" = line N of `design/firmware.md`. Evidence: `firmware/build-logs/step6/u5-*` (L = `u5-run2.console`).
Cited run: `RING_REMOTE_SRC=/root/ring-os/src-u-power sh firmware/tools/remote.sh u-power-run2 "bash tools/unit_run.sh tests/power"`,
exit 0 (`u5-run2.exit`). Its last result line, L line 1637: `UNIT PASS tests/power`; L line 1635: `RESULT PASS`.
A first run (`u5-run1.console`) stopped at the copy `ilim_plays_m3` (its edit text no longer matched after a refactor); fixed, all 15 edits
checked to match once (`u5-editcheck2.log`), then run 2. Earlier development runs `u5-dev1` to `u5-dev4` (red then green: races and
a missing status read at start found and fixed) are kept.

## 1. Files

| File | What |
|---|---|
| `modules/ring_power/src/rpw_logic.c`, `rpw_logic.h` | pure part: levels, window of 10, report on change, charge order, `CHARGE_CURRENT` with 5 build assertions, motor charge, current-limit decision, ship step machine, reset-cause args, GET_BATTERY codes and bytes |
| `src/rpw.c`, `src/rpw_priv.h` | thin part: power thread, sampling timer, gauge, chip calls (only through `rhw.h`), callbacks; `rpw_priv.h` = test reset |
| `src/rpw_hw_real.c` | real nPM1304 and gauge; kit build only; NOT PROVEN |
| `CMakeLists.txt`, `Kconfig`, `zephyr/module.yml` | module |
| `tests/power/` | 9 suites, 32 cases, `broken_edit.py`, `broken_run.sh`, `k_probe*.sh` (kit facts) |

## 2. Rows of the plan that name U5: test case and log line

L = `build-logs/step6/u5-run2.console`. Both targets: L line 22 (`native_sim`) and line 44 (`nrf54lm20bsim/nrf54lm20a/cpuapp`):
`32 of 32 executed test cases passed`. Per-case PASS lines: L lines 67 to 100 (native_sim, of the first broken copy's run, where the cases
that copy does not break pass), full per-case list `u5-dev4.console` (64 of 64 passed on both targets). Broken-copy lines are in section 3.

| Row | Test case | Evidence |
|---|---|---|
| C2 | `power_levels.test_soc_edges` (16, 15, 6, 5, 3, 2 %; also 1.9 and 2.1), `test_voltage_edges` (3.451, 3.450, 3.301, 3.300 V; also 4.35 V, 3.299 V, exact compare), `test_mean_of_ten_in_recording` | L 83, 81; `test_voltage_edges` PASS in the unbroken run (L 22, 44) and FAIL on its copy (L 127, 189) |
| C6 | `power_charger.test_charge_on_twice_writes_once`, `test_charge_off` | L 72, 71; copy `charge_on_rewrites` L 538, 600 |
| C22 | `power_charger.test_on_at_every_vbus` (14 states, BOOT and RECOVERY included; charge on done before the VBUS callback), `test_on_at_start_with_vbus` | L 74, 75. The join half `recorder_rows.test_charge_on_every_vbus_row` is the join's |
| C39 | `power_report.test_values_and_time_to_full` (values for SCR_CHARGING: vbus, charging, full, to_full_min); the call `rscr_set_battery()` is the join's | L 90 |
| P2 | build assertions in `rpw_logic.c` lines 15 to 23; runtime `power_cfg.test_charge_current_constant` (15000, one place) | copies `cc_*`: L 1450, 1470, 1500, 1514, 1541, 1555, 1582, 1596, 1621, 1632; search of every `CHARGE_CURRENT` site: `u5-searches.log` section 9 |
| P3 | `power_charger.test_disable_write_enable_order` (disable, current written while disabled, enable) | L 73; copy `write_while_enabled` L 675, 737 |
| P8 | `power_gauge.test_motor_charge_added` (3,000 uA + 51.50 mA.s over the sample, used once; pure rule; charge kept when the gauge fails). The dt is whole ms, so 54,500 is checked within 100 and exactly against 3000 + 51500000 / dt | L 76; copy `motor_charge_subtracted` L 812, 874. Sign for the library: K6 |
| P9 | `power_sample.test_period_per_state` (all 14 states), `test_period_in_time` (1,000 ms apart in RECORDING; 60 s in STANDBY), `test_no_sampling_in_ship_and_off`, `test_ilim_read_with_every_sample` | L 96, 95, 94, 93 |
| P11 | `power_levels.test_report_on_change_both_ways` (B5, B2, B15, OK), `test_first_level_reported_at_start` | L 82, 80; copy `report_down_only` L 401, 463. Join half `recorder_rows.test_vbus_out_at_b2_goes_off` is the join's |
| P12 | `power_ship.test_entry_order_without_vbus`, `test_waits_for_vbus_removed` (part A wait for removal; part B retry waits again), `test_retry_once_after_1s` | L 97, 100, 99; copies `ship_no_strobe` L 949, 1011; `ship_no_wait` L 1086, 1148. Step 1 and `recorder_actions.test_ship_closes_everything_first` are the join's |
| P13 | `power_ship.test_off_never_waits` | L 98 |
| P14 | `power_reset.test_causes_logged_then_cleared` (each of the 7 bits, read then clear, chip empty after), `test_all_bits_and_none` | L 92, 91; copy `causes_not_cleared` L 1362, 1424 |
| P17 | `power_cfg.test_no_vbus_output_call` (the power interface has 14 calls, size checked; no log kind outside the interface; VBUS entries are only the test's own; no rail call) | L 68. Pads and levels: not provable without hardware |
| P18 | `power_ilim.test_first_active` (one record, callback first, no motor, no rail, no level or VBUS report), `test_again_with_screen_off` (counts 2, 3, then a new run after 11 s), `test_screen_off_edge_10s` | L 78, 77, 79; copy `ilim_plays_m3` L 1225, 1287. The screen itself (`recorder_screens.test_ilim_dims_in_recording`) is the join's |
| P19 | `power_cfg.test_pof_untouched` (interface has no POFCONFIG or VSYSPOF call; a full session logs no other kind) | L 69; source search `u5-searches.log` section 8 (no hit) |
| X13 | `power_report.test_charge_state_codes` (0 to 5, latched error reads 5), `test_battery_bytes_layout` (9 bytes, little endian) | L 88, 87 |

Not provable without hardware (unit's share): the register map and devicetree names (FW 10.5 item 3), real charging, thermistor and
die limits (P5), ship current and the real supply cut (P15), the battery model (P10), the pads (P17 pad levels), the real driver file.

## 3. Broken copies (L = `u5-run2.console`)

All 10 copies failed their named case and only it, on both targets (`failed cases listed: 1`), lines: `voltage_ignored` 127, 189;
`mean_of_5` 264, 326; `report_down_only` 401, 463; `charge_on_rewrites` 538, 600; `write_while_enabled` 675, 737;
`motor_charge_subtracted` 812, 874; `ship_no_strobe` 949, 1011; `ship_no_wait` 1086, 1148; `ilim_plays_m3` 1225, 1287; `causes_not_cleared` 1362, 1424.
The 5 build copies failed the build with their own message on both targets: `cc_unset` 1450, 1470; `cc_17601` 1500, 1514; `cc_3999` 1541, 1555;
`cc_100500` 1582, 1596; `cc_15250` 1621, 1632. Overlap of messages: 17601, 3999 and 100500 also break a second assertion (17601 and 3999 are
not multiples of 500; 100500 is also above 17,600); the build log holds the named message in each case, and `broken_run.sh` counts a copy only for that.
How the strict "only its own case" rule shaped the copies: `voltage_ignored` removes only the B5 voltage term (the mean test judges by the B2 term, so it does not
depend on it); the pure-rule checks of a fault live inside its one named case (`test_motor_charge_added`, `test_entry_order_without_vbus`,
`test_waits_for_vbus_removed`), not in separate cases; the charger test counts only the current writes and enable-on calls so that dropping the disable
fails only `test_disable_write_enable_order`.

## 4. Readings (differences from or additions to the plan; the lead rules)

1. **Sampling class.** `rpw_state` reads only RECORDING as the 1 s class (ruling 8). A factory test recording runs in `FACTORY_TEST`: the join must pass the
   RECORDING value to `rpw_state()` while one runs, and the FACTORY_TEST value otherwise. SHIP and OFF do not sample; every other state 60 s.
2. **Window.** The window is the last 10 samples taken, also when the earlier ones come from the 60 s class; after `rpw_start` it holds the first sample. Outside
   RECORDING the single sample judges. Mean compared exactly (sum against limit x count), not rounded.
3. **First step of the gauge** at `rpw_start` uses dt 0 (the sim returns the start value; the real library's behaviour for dt 0 is unproven).
4. **Charge on after VBUS removed.** VBUS removal marks the charger "not on" in RAM, so each appearance writes the full sequence (R8: every appearance);
   a second call with VBUS present and the charger on writes nothing.
5. **Callbacks at start** (`vbus(true)`, first level, first current-limit reading) run from the power thread right after `rpw_start` returns; the first sample, gauge
   start, charge on and the first status read run in the caller. The current-limit status is read at that first sample too.
6. **Current-limit count** = ACTIVE readings of the run (1 at the first, +1 for each "again"); the 10 s screen window is not extended by "again"; a reading at 10,000 ms or later starts a new run.
   Log args as in `rrec_spec.h`: mV u16, state u8, screen on u8 (1 first, 0 again), count u32.
7. **Ship.** `before_task` is called once (first try). While `rpw_ship` runs, sampling is stopped. Callbacks for VBUS still go out and VBUS-in still does "charge on" (R-CHG, every state).
   In the simulation the chip cuts supply at the first task without VBUS, so the rest runs on a refused chip; the test reads the order and times only.
8. **GET_BATTERY.** A latched error reads 5 whatever the state; an out-of-range state reads 5; time to full is rounded up to whole minutes, 0xFFFF unknown.
9. **No rail call** in this unit (ruling 4); no motor soft start (not built).

## 5. Kit facts (answered by file listings and counts only; no kit line printed)

K5 (`u5-k56.console`, `u5-k56b.console`, `u5-k56c.console`, `u5-k56d.console`): the nPM13xx family serves the nPM1304: binding files with `npm1304` in the name exist for
the mfd, regulator, charger, gpio, led and watchdog (`zephyr/dts/bindings/...`), drivers `drivers/mfd/mfd_npm13xx.c`, `drivers/regulator/regulator_npm13xx.c`,
`drivers/sensor/nordic/npm13xx_charger/npm13xx_charger.c`. The charger sensor channels for voltage, average current, thermistor temperature and die temperature exist
(count 1 each in the driver and in `sensor.h`). The register read, write and callback calls exist in `include/zephyr/drivers/mfd/npm13xx.h` (counts 2, 2, 1); the
events for VBUS detected, VBUS removed and charge error exist there too. Property names: `soft-start-microamp`, `active-discharge`, `regulator-boot-off`,
`regulator-initial-mode` are in the common regulator binding (count 1, 2, 1, 1); `thermistor-ohms`, `thermistor-beta`, `vbus-limit-microamp`, `trickle-microvolt`, `charging-enable`,
`dietemp-stop-millidegrees`, `dietemp-resume-millidegrees`, the cold, cool, warm, hot thermistor properties are in the common charger binding; `term-microvolt`,
`current-microamp`, `term-current-percent`, `term-warm-microvolt` are in the nPM1304 charger binding. `charging-enable` is in the common one (count 1) and not in the 1304 file (count 0). There is
**no emulator** of the chip in the kit (empty listing), so the simulated chip stays. Not checked: that the chip's TASKENTERSHIPMODE needs the register write (it does, by the
datasheet: SHIP base 0x0B offset 0x02; the real file writes it).
K6: the fuel gauge library header has `nrf_fuel_gauge_init`, `_process`, `_tte_get`, `_ttf_get` and `struct nrf_fuel_gauge_init_parameters` with `v0`, `i0`, `t0`, `model` (counts
in `u5-k56d.console`). Libraries exist for ARM cores and one Xtensa only, **no host build**: `native_sim` and the simulated board use the simulated gauge, as the plan assumes. The kit has
battery models for primary cells only; a lithium cell model (nPM PowerUP) is missing: the real file stops the build with a message until `rpw_battery_model.h` exists (FW l.930, open). **The sign of a
discharge current is not settled**: the header holds no line with the words negative or positive together with charge words (counts 0), and the kit's sample for the same chip family applies a unary minus to the
current before the library call (count 1) while the charger driver does not negate it (count 0). Which sign the library wants stays open; the real file converts in two places
(`chan_to_ua` and the two `-(...)` in the gauge calls) and the simulated interface is positive = discharge. Settled only on the bench.

## 6. Searches (`u5-searches.log`)

Pure part includes only `string.h`, `ring_core/rc_types.h` (pure), `rpw_logic.h`, `stdbool.h`, `stdint.h`, `rrec_spec.h` (section 1); no kernel name in code (section 2: the hits are the words
`LOG_RETRY` and a comment). Thin part includes only kernel, spinlock, atomic, core types, `rpw.h`, `rhw.h` (section 3); no direct hardware name (section 4: the one hit is the field `err_sensor`).
No chip pin by number (section 5), no server address or key (section 6; `power-notes.md` included, run after this file was written), no rail call (section 7).
Not run: no browser, no git, no full run.

## 7. Not done / open

- `rpw_hw_real.c` is not compiled (no board devicetree here); only its kit names were checked by count (`u5-k56d.console`).
- The real library's sign and its dt 0 behaviour (readings 3 and K6).
- Expected values typed from FW: 15000 (l.878), thresholds (l.115 to l.117), 96 ms (l.938), 1 s retry (l.941), 51.5 mA (l.927), codes 0 to 5 (l.702); GET_BATTERY little endian (l.70).

questions_for_owner: none

RESULT: done, `UNIT PASS tests/power` on both simulated targets with all 10 broken copies failing only their named case and all 5 `cc_*` copies failing the build with their own message; real driver file unproven.
