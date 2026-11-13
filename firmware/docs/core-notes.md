# Ring core: notes

Date: 2026-11-11. Specification: `design/firmware.md` version F6 (FW below; line numbers are of that file as it is in the working tree). Part "Core" of `design/software/os/design.md` section 3.

## 1. Interface (one page)

Code: `firmware/modules/ring_core/` (Zephyr module `ring_core`, Kconfig `CONFIG_RING_CORE`). It includes only `stdint.h`, `stdbool.h` and `string.h`: no kernel, driver or Bluetooth call. Time is `rc_ms_t` (int64, ms, from the event timestamps).

| Header | What it gives |
|---|---|
| `ring_core/rc_types.h` | `enum rc_state` (the 14 states of FW 1.1), `enum rc_event`, `enum rc_guard`, `enum rc_action` (open, close, charge on and off, motor M1 M2 M3 MH MT MF MW, rail requests SD_ON SD_OFF MIC_OFF, MOUNT, STOP_PDM, CLOCKS_LOW, SHIP_MODE, log, highlight, screen requests by FW 3.3 name), `struct rc_actions` (the list, the row taken, the highlight time), `struct rc_facts` (vbus, open flag, factory flag, storage full, storage init ok, screen on, vibration, battery level) |
| `ring_core/rc_sm.h` | `rc_table[]` (generated), `rc_sm_find`, `rc_sm_handle`, `rc_row_actions`, `rc_table_checksum` |
| `ring_core/rc_gesture.h` | the key layer of FW 2.2 and the recogniser of FW 2.1: `rc_gesture_input(sw, pressed, t)`, `rc_gesture_tick(now)`, `rc_gesture_next_tick()`; build constant `CENTRE_SOURCE` as `RC_CENTRE_SW2` or `RC_CENTRE_PAIR` at init |
| `ring_core/rc_core.h` | the dispatcher: `rc_core_init(src, start, now)`, `rc_core_input(sw, pressed, t)` for debounced switch edges, `rc_core_event(ev, t)` for system events, `rc_core_tick(now)`, `rc_core_next_tick()`, `rc_core_state()`, `rc_core_facts()`, `rc_core_mic_rail()` |

How the caller uses it: feed each debounced edge of SW1 to SW5 to `rc_core_input`; feed VBUS in and out, USB configured and unconfigured, B15, B5, B2, S30, SFULL, init and scan results, faults, BLE highlight, menu power off and the transfer and factory commands to `rc_core_event`; call `rc_core_tick` at `rc_core_next_tick()` (or later); carry out the returned actions in order. Every call appends to the `struct rc_actions` passed in (`rc_actions_clear` first).

Rules the code holds:
- The press events (long, short, double) and the 5 s and 60 s timers cannot be given to `rc_core_event`; they come only from the switch input and from `rc_core_tick`. So nothing but a centre long press can start a recording (owner's rule, FW line 3 and line 198).
- One table entry per FW 1.2 row, first match in document order. An event with no matching row changes nothing and returns no action.
- The Vibration setting off removes MH and MT only (FW line 276); MW and the others stay.
- MW is sent at 500 ms of a centre hold only in STANDBY and RECORDING (FW line 223).
- Deadlines: a deadline at time D runs when now is D or later. An input at time t first runs every deadline at or before t, then applies the edge.

Code and document kept the same: `firmware/modules/ring_core/tools/gen_table.py` reads FW 1.2 and writes `src/state_table.inc` and `src/state_table.json` (row number, document line, from-state, event, guard, to-state, event text, and an FNV-1a checksum). The event text is mapped to an event and a guard by an exact-text map in the generator: a changed text stops it. The actions are prose in the document, so they are hand-written in `src/state_actions.c`, one `case` per row with the row number and the document line beside it. The host run regenerates the table and compares it byte for byte (row count and checksum printed); the test `rc_table.test_table_checksum_matches_generator` recomputes the checksum from the compiled table.

## 2. Counts

Output of `python3 count_rows.py --table` (exit 0):

```
rows in section 1.2 of design/firmware.md: 61 (the document states 61)
row tests in tests/core/src/test_rows.c: 61
COUNT MATCH
```

| Row | Line | From | Event | To | Test |
|---|---|---|---|---|---|
| 1 | 133 | SHIP | VBUS appears (case contact) | BOOT | rc_rows.test_row_01 |
| 2 | 134 | OFF | VBUS appears | BOOT | rc_rows.test_row_02 |
| 3 | 135 | BOOT | init done, superblock open flag clear, no VBUS, battery above B5 | STANDBY | rc_rows.test_row_03 |
| 4 | 136 | BOOT | init done, superblock open flag set | RECOVERY | rc_rows.test_row_04 |
| 5 | 137 | BOOT | init done, VBUS present | CHARGING | rc_rows.test_row_05 |
| 6 | 138 | BOOT | storage init fails 3 times, 200 ms apart | ERR_STORAGE_FAULT | rc_rows.test_row_06 |
| 7 | 139 | BOOT | battery at B2 and no VBUS | OFF | rc_rows.test_row_07 |
| 8 | 140 | BOOT | battery at B5 and no VBUS | ERR_BATTERY_LOW | rc_rows.test_row_08 |
| 9 | 141 | RECOVERY | scan done, no VBUS | STANDBY | rc_rows.test_row_09 |
| 10 | 142 | RECOVERY | scan done, VBUS present | CHARGING | rc_rows.test_row_10 |
| 11 | 143 | RECOVERY | read error during scan | ERR_STORAGE_FAULT | rc_rows.test_row_11 |
| 12 | 144 | STANDBY | long press of the joystick centre | RECORDING | rc_rows.test_row_12 |
| 13 | 145 | STANDBY | short press of the joystick centre | STANDBY | rc_rows.test_row_13 |
| 14 | 146 | STANDBY | double press of the joystick centre | STANDBY | rc_rows.test_row_14 |
| 15 | 147 | STANDBY | menu "Power off" confirmed | OFF | rc_rows.test_row_15 |
| 16 | 148 | STANDBY | VBUS appears | CHARGING | rc_rows.test_row_16 |
| 17 | 149 | STANDBY | battery reaches B15 | STANDBY | rc_rows.test_row_17 |
| 18 | 150 | STANDBY | battery reaches B5 | ERR_BATTERY_LOW | rc_rows.test_row_18 |
| 19 | 151 | STANDBY | battery reaches B2 | OFF | rc_rows.test_row_19 |
| 20 | 152 | STANDBY | free space at SFULL | ERR_STORAGE_FULL | rc_rows.test_row_20 |
| 21 | 153 | RECORDING | long press of the joystick centre | STANDBY | rc_rows.test_row_21 |
| 22 | 154 | RECORDING | short press of the joystick centre | RECORDING | rc_rows.test_row_22 |
| 23 | 155 | RECORDING | double press of the joystick centre | RECORDING | rc_rows.test_row_23 |
| 24 | 156 | RECORDING | BLE control "highlight" from a bonded phone | RECORDING | rc_rows.test_row_24 |
| 25 | 157 | RECORDING | VBUS appears (case insertion during a recording) | CHARGING | rc_rows.test_row_25 |
| 26 | 158 | RECORDING | battery reaches B15 | RECORDING | rc_rows.test_row_26 |
| 27 | 159 | RECORDING | battery reaches B5 | ERR_BATTERY_LOW | rc_rows.test_row_27 |
| 28 | 160 | RECORDING | battery reaches B2 | OFF | rc_rows.test_row_28 |
| 29 | 161 | RECORDING | free space reaches S30 | RECORDING | rc_rows.test_row_29 |
| 30 | 162 | RECORDING | free space at SFULL | ERR_STORAGE_FULL | rc_rows.test_row_30 |
| 31 | 163 | RECORDING | chunk write fails 3 times | ERR_STORAGE_FAULT | rc_rows.test_row_31 |
| 32 | 164 | RECORDING | the PDM instance gives no block for 100 ms | ERR_MIC_FAULT | rc_rows.test_row_32 |
| 33 | 165 | RECORDING | sudden power loss (cell cut, short, brown-out) during a write | BOOT | rc_rows.test_row_33 |
| 34 | 166 | CHARGING | USB configured by the case (`USBD_MSG_CONFIGURATION`) | TRANSFER | rc_rows.test_row_34 |
| 35 | 167 | CHARGING | VBUS removed, free space above SFULL, battery above B5 | STANDBY | rc_rows.test_row_35 |
| 36 | 168 | CHARGING | VBUS removed, free space at SFULL | ERR_STORAGE_FULL | rc_rows.test_row_36 |
| 37 | 169 | CHARGING | VBUS removed, battery at B5 | ERR_BATTERY_LOW | rc_rows.test_row_37 |
| 38 | 170 | CHARGING | nPM1304 event charge error | ERR_CHARGER | rc_rows.test_row_38 |
| 39 | 171 | CHARGING | long press | CHARGING | rc_rows.test_row_39 |
| 40 | 172 | TRANSFER | USB suspended or unconfigured by the case | CHARGING | rc_rows.test_row_40 |
| 41 | 173 | TRANSFER | VBUS removed | STANDBY | rc_rows.test_row_41 |
| 42 | 174 | TRANSFER | command FW_END accepted | BOOT | rc_rows.test_row_42 |
| 43 | 175 | TRANSFER | command FACTORY_ENTER with the factory flag set | FACTORY_TEST | rc_rows.test_row_43 |
| 44 | 176 | TRANSFER | long press | TRANSFER | rc_rows.test_row_44 |
| 45 | 177 | ERR_STORAGE_FULL | VBUS appears | CHARGING | rc_rows.test_row_45 |
| 46 | 178 | ERR_STORAGE_FULL | long press | ERR_STORAGE_FULL | rc_rows.test_row_46 |
| 47 | 179 | ERR_STORAGE_FULL | battery reaches B5 | ERR_BATTERY_LOW | rc_rows.test_row_47 |
| 48 | 180 | ERR_STORAGE_FULL | battery reaches B2 | OFF | rc_rows.test_row_48 |
| 49 | 181 | ERR_BATTERY_LOW | VBUS appears | CHARGING | rc_rows.test_row_49 |
| 50 | 182 | ERR_BATTERY_LOW | long press | ERR_BATTERY_LOW | rc_rows.test_row_50 |
| 51 | 183 | ERR_BATTERY_LOW | battery reaches B2 | OFF | rc_rows.test_row_51 |
| 52 | 184 | ERR_STORAGE_FAULT | VBUS appears | CHARGING | rc_rows.test_row_52 |
| 53 | 185 | ERR_STORAGE_FAULT | 60 s elapsed and storage init succeeds | STANDBY | rc_rows.test_row_53 |
| 54 | 186 | ERR_STORAGE_FAULT | battery reaches B2 | OFF | rc_rows.test_row_54 |
| 55 | 187 | ERR_MIC_FAULT | 5 s elapsed | STANDBY | rc_rows.test_row_55 |
| 56 | 188 | ERR_MIC_FAULT | VBUS appears | CHARGING | rc_rows.test_row_56 |
| 57 | 189 | ERR_CHARGER | VBUS removed | STANDBY | rc_rows.test_row_57 |
| 58 | 190 | FACTORY_TEST | command FACTORY_EXIT | BOOT | rc_rows.test_row_58 |
| 59 | 191 | FACTORY_TEST | command SHIP_ENTER | SHIP | rc_rows.test_row_59 |
| 60 | 192 | FACTORY_TEST | command SHIP_SAMPLE (sample rings only) | SHIP | rc_rows.test_row_60 |
| 61 | 193 | FACTORY_TEST | VBUS removed, no ship command accepted | BOOT | rc_rows.test_row_61 |

Tests per suite in `firmware/tests/core/host/host-tests.log` (every one PASS):

| Suite | Tests |
|---|---|
| generator (shell check in run_host_tests.sh, not a ztest) | 1 |
| rc_collisions | 7 |
| rc_core_timing | 1 |
| rc_feedback | 4 |
| rc_gesture | 62 |
| rc_mic_rail | 2 |
| rc_owner_rule | 7 |
| rc_row_variants | 7 |
| rc_rows | 61 |
| rc_table | 2 |
| total: 153 ztest tests (the `RESULT PASS tests=153` line) plus the generator check | 154 |

Gesture and rule cases (suite.test; the FW lines are in the comment above each test in `firmware/tests/core/src/`):

- generator: fresh_run_matches_committed_table
- rc_collisions: test_c1_short_in_recording_marks_highlight_not_status, test_c2_long_press_with_screen_on_starts, test_c3_centre_action_comes_after_window_and_double_is_dead, test_c4_lock_direction_and_short_only_wake, test_c4_long_press_with_screen_off_starts, test_c4_short_in_recording_screen_off_marks_and_shows_3s, test_screen_on_direction_goes_to_screen_with_mt
- rc_core_timing: test_core_next_tick_includes_state_timers
- rc_feedback: test_highlight_carries_centre_down_time, test_long_press_ignored_in_other_states, test_mw_in_standby_and_recording_only, test_vibration_off_drops_mh_mt_only
- rc_gesture: test_dir_sent_then_others_ignored_until_all_open, test_next_tick_follows_deadlines, test_pair_centre_has_no_repeat, test_pair_dir_down_hold_repeat, test_pair_dir_down_tap, test_pair_dir_left_hold_repeat, test_pair_dir_left_tap, test_pair_dir_right_hold_repeat, test_pair_dir_right_tap, test_pair_dir_up_hold_repeat, test_pair_dir_up_tap, test_pair_gap_400ms_double, test_pair_gap_401ms_two_shorts, test_pair_gap_59ms_not_double, test_pair_gap_60ms_double, test_pair_hold_1000ms_long, test_pair_hold_39ms_graze_ignored, test_pair_hold_40ms_short, test_pair_hold_450ms_short, test_pair_hold_451ms_ignored, test_pair_hold_499ms_ignored_no_warn, test_pair_hold_500ms_ignored_warn, test_pair_hold_999ms_ignored_warn, test_pair_ignores_btn_rec, test_pair_long_fires_once_while_held, test_pair_non_opposite_switch_ignored, test_pair_one_side_lets_go_does_not_end_long_press, test_pair_opposite_at_39ms_is_centre_stamped_second_edge, test_pair_opposite_at_40ms_is_direction, test_pair_second_press_long_counts_from_own_down, test_pair_short_fires_when_window_closes, test_pair_warn_at_500ms, test_release_before_mark_in_holdoff_no_long, test_release_holdoff_29ms_bounce_same_press, test_release_holdoff_30ms_ends_press_stamped_at_release, test_sw2_dir_down_hold_repeat, test_sw2_dir_down_tap, test_sw2_dir_left_hold_repeat, test_sw2_dir_left_tap, test_sw2_dir_right_hold_repeat, test_sw2_dir_right_tap, test_sw2_dir_then_centre_at_39ms_centre_wins, test_sw2_dir_then_centre_at_40ms_direction_kept, test_sw2_dir_up_hold_repeat, test_sw2_dir_up_tap, test_sw2_gap_400ms_double, test_sw2_gap_401ms_two_shorts, test_sw2_gap_59ms_not_double, test_sw2_gap_60ms_double, test_sw2_hold_1000ms_long, test_sw2_hold_39ms_graze_ignored, test_sw2_hold_40ms_short, test_sw2_hold_450ms_short, test_sw2_hold_451ms_ignored, test_sw2_hold_499ms_ignored_no_warn, test_sw2_hold_500ms_ignored_warn, test_sw2_hold_999ms_ignored_warn, test_sw2_long_fires_once_while_held, test_sw2_roll_does_not_end_long_press, test_sw2_second_press_long_counts_from_own_down, test_sw2_short_fires_when_window_closes, test_sw2_warn_at_500ms
- rc_mic_rail: test_open_only_into_recording_and_every_exit_turns_mic_off, test_rail_follows_state_on_every_event_from_every_state
- rc_owner_rule: test_directions_never_start, test_long_press_starts_and_same_long_press_stops, test_no_system_event_starts_a_recording, test_only_row_12_enters_recording, test_press_events_cannot_be_injected, test_rows_leaving_recording_are_the_stated_ones, test_user_inputs_other_than_long_never_stop
- rc_row_variants: test_row13_screen_on, test_row17_m3_once_per_discharge, test_row26_m3_once_per_discharge, test_row29_m3_once, test_row43_needs_factory_flag, test_row53_needs_storage_init_success, test_row53_open_flag_set_recovery_first
- rc_table: test_table_checksum_matches_generator, test_table_has_61_rows_in_order

## 3. Where the specification is silent or unclear, and the reading taken

| Id | Lines | What | Reading taken |
|---|---|---|---|
| U1 | 128, 212, 215, 221 | 450 ms is in "short press 40 to 450 ms" (lines 128, 212, 221) and in "held 450 ms to 999 ms, ignored" (line 215). | 450 ms is a short press: three lines and the parameter table's [CHOICE] (line 221) say so; 451 ms is ignored. Tested at 450 and 451. |
| U2 | 213, 222, 246 | A second press under 60 ms after the release: not a double (60 to 400 ms), but line 246 says any press inside the 400 ms window cancels the earlier short press and is judged on its own. Possible because the release hold-off is 30 ms (line 224). | Not a double; the first short press is cancelled; the second is judged on its own, so one short press fires, after its own window. Tested at 59 ms. |
| U3 | 212, 213, 222, 245 | The window "400 ms after a release" with a second press "60 ms to 400 ms" after it: 400 is inside. Line 245 says the highlight fires 400 ms after the release. | 400 ms is inside the window (a double); the short press fires at release + 401 ms, the first ms after the window: 1 ms later than line 245. Tested at 400 and 401. |
| U4 | 149, 158 | "M3 once per discharge": when a discharge ends is not stated. | A VBUS appearance starts a new discharge (flag cleared on VBUS in). Only "no second M3 in the same discharge" is tested. |
| U5 | 149, 161 | "M3 once" (S30) has no scope; for B15 the status screen is not said to be once. | S30: once per recording (cleared by open, row 12). "Once" binds M3 only: a second B15 in STANDBY still shows the status screen, a second S30 still shows the message. Only the absence of a second M3 is tested. |
| U6 | 136, 137, 200 | Rows 4 and 5 both match "init done" with the open flag set and VBUS present. | Document order, row 4: RECOVERY, then row 10 to CHARGING with charge on. Line 200 supports it ("BOOT goes to RECOVERY"). Not tested (a reading). |
| U7 | 135, 139, 140 | "Init done" with the open flag clear, no VBUS and the battery at B5 or B2 matches no "init done" row (row 3 needs above B5). | The core stays in BOOT; the caller sends the battery event, rows 7 and 8. Which comes first is not stated. Not tested. |
| U8 | 168, 169 | Rows 36 and 37 both match VBUS removed with storage at SFULL and the battery at B5. | Document order: row 36, ERR_STORAGE_FULL. Owner or lead should choose; not tested. |
| U9 | 185 | Row 53 goes to STANDBY but "RECOVERY runs first if the open flag is set"; nothing says what happens when the storage init fails at 60 s. | To-state STANDBY with the action RUN_RECOVERY when the open flag is set. A failed init at 60 s: no row, the core stays in ERR_STORAGE_FAULT and does not start a new 60 s timer. The first is tested; the failing case is tested only as "no row matches". |
| U10 | 193 | Row 61 guard "no ship command accepted": after a ship command the state is already SHIP. | No guard is coded: in FACTORY_TEST it always holds. |
| U11 | 107, 163 | Row 31 does not turn VDD_SD off, while the state table says storage is off in ERR_STORAGE_FAULT. | The row is coded as written (stop PDM, clocks low, VDD_MIC off, MF); no SD_OFF added. |
| U12 | 145, 212, 301 | Row 13 and the 2.1 table give "the centre action of the screen" with the screen on; FW 3.1 line 301 plays MT on a "joystick move or select (only when screen is on)". | With the screen on a short press gives SCREEN_CENTRE then MT, and a direction gives SCREEN_UP, DOWN, LEFT or RIGHT then MT. Tested. |
| U13 | 133, 134 | Rows 1 and 2: "leaves ship mode, powers the bucks, the chip starts" are done by the hardware. | Only CHARGE_ON is a core action. |
| U14 | 136 | Row 4 "keep VDD_SD on". | Coded as the request SD_ON. |
| U15 | 3, 198, 157 to 165 | The owner's rule says only a long press starts or stops a recording; the table also stops one on case insertion (allowed by line 198), B5, B2, SFULL, write failure, microphone fault and power loss. | Start: only row 12 (tested over every state, every event and 128 fact combinations). Stop: no user input except the centre long press, and not Bluetooth, stops one (tested); the rows leaving RECORDING are exactly 21, 25, 27, 28, 30, 31, 32, 33 (tested). |
| U16 | 232, 254, 256 | At exactly 40 ms: "0 to 40 ms before SW2 is dropped" against "40 ms or more keeps its direction"; "within 40 ms" for the pair. | 40 ms is a direction in both cases (the window ends at 40 ms). Tested at 39 and 40 for each direction. |
| U17 | 252 | "Holding a direction for 500 ms repeats it every 150 ms": from which instant. | First repeat 500 ms after the press edge, then every 150 ms, until the release. Tested. |
| U18 | 232, 256 | Case SW2: another direction switch inside the window. Line 232 says "nothing else". | Ignored, as rule (4) of case PAIR. |
| U19 | 214, 246 | Does a graze inside the window cancel an earlier short press? Line 246 says any press does. | Literal: yes. Not tested. |
| U20 | 207, 255 | Same-ms order of an edge and a deadline. | The deadline runs first (a hold reaching 1,000 ms at the release ms is a long press). |
| U21 | 101 to 109 | The screen times per state (error screen 10 s, charging screen 5 s) are not in the rows. | Not coded in the core: the Screens part owns the screen; the core reads `screen_on` from the caller. |
| U22 | 280 | C2: "open screens are discarded; an open pairing window is closed". | Not a core action; left to the Screens and Devices parts. Only "the long press starts from any screen" is tested. |
| U23 | 156 | Time of a BLE highlight. | The event time; `highlight_ms` is set only for the centre short press (CENTRE_DOWN time, line 226). |

## 4. How to run

Host (Mac, `cc`), the early check:

    cd firmware/tests/core/host && sh run_host_tests.sh

It regenerates the table into `host/build/fresh/`, compares it with the committed one, compiles `firmware/modules/ring_core/src/*.c` and `firmware/tests/core/src/*.c` with the shim `host/shim/zephyr/ztest.h` and `host/shim/runner.c`, and prints `RESULT PASS tests=<n>` or `RESULT FAIL`. Log of the delivered run: `firmware/tests/core/host/host-tests.log`.

Broken copy (must fail):

    cd firmware/tests/core/broken && sh run_broken.sh long900

Mutations: `long900` (long press 900 ms, the one asked for), `row12to` (row 12 to STANDBY in the generated table), `gap60` (double-press gap 50 ms), `row27act` (row 27 without close). Logs: `firmware/tests/core/broken/broken-<mutation>.log` and `copy-<mutation>/host-run.log`.

Row count against test count:

    cd firmware/tests/core && python3 count_rows.py --table

Zephyr (`native_sim`), the real proof, through the other helper's script from the project root:

    cd . && sh firmware/tools/remote.sh core-tests "west twister -T tests/core -p native_sim --inline-logs"

Zephyr result (run through `firmware/tools/remote.sh`, container `ring-os-toolchain:v3.4.2`, saved in `firmware/build-logs/20261111-105051-core-tests.log` and `firmware/tests/core/evidence/zephyr-run-2.log`):

```
# remote.sh run 20261111-105051-core-tests
INFO    - Zephyr version: 9133dab6b066
INFO    - 1 of 1 executed test configurations passed (100.00%), 0 built (not run), 0 failed, 0 errored, with no warnings in 13.89 seconds.
INFO    - 153 of 153 executed test cases passed (100.00%) on 1 out of total 1514 platforms (0.07%).
# remote exit code: 0
```

The first Zephyr run (`firmware/build-logs/20261111-103851-core-tests.log`, `evidence/zephyr-run-1.log`) stopped with exit 2: `platform_allow in ring_core.logic - unrecognized platform - nrf54lm20bsim/nrf54lm20/cpuapp`. The simulated chip board was then removed from `testcase.yaml`; the suite is allowed on `native_sim` only.

## 5. Not done

- The per-screen mapping of FW 2.2 (menu, settings, confirm, pair) and the screen time-outs: the Screens part. The core only sends SCREEN_ON, the named screens and the direction or centre request.
- The motor player rule "M1, M2, M3 and MF are never cut short by MH or MT" (FW line 293): the player, not the core.
- The 20 ms debounce: `gpio-keys` before the core (FW line 219).
- The simulated chip board `nrf54lm20bsim/nrf54lm20/cpuapp`: twister in the server image does not know it (first Zephyr run, exit 2), so it is not in `testcase.yaml` and the core tests did not run on it. Who acts: the other helper (server tools), if a bsim run of the core is wanted.
- The parts of readings U4 to U10 and U19 that the specification does not state are coded but not asserted by tests.

## 6. Runs in order, and problems met

1. Host run 1 (`firmware/tests/core/evidence/host-run-1-debug.log`): compile error, an unused function in `gesture.c`; removed.
2. Host run 2 (`evidence/host-run-2-debug.log`): `RESULT PASS tests=153`.
3. Broken copy `long900`, first run: `RESULT FAIL` with 10 failing tests, but the row tests 12, 21, 39, 44, 46, 50 passed, because the test helpers took the long press time from the module's own constant. Fixed: the tests now use the specification's values (`SPEC_*` in `tests/core/src/th.h`), and the helpers assert that no row fires before the 1,000 ms mark or while the window is open. The log of that first run was overwritten by the rerun; its output is only in the builder's transcript.
4. Host run 3 (`evidence/host-run-3-debug.log`) and the four broken copies (`broken/broken-*.log`): PASS on the module, `RESULT FAIL` on each mutation (long900: 21 failing tests, row12to: 10 plus the generator check, gap60: 2, row27act: 4).
5. Zephyr run 1: exit 2, unknown bsim platform (section 4). Zephyr run 2: 153 of 153 passed on `native_sim`.
6. Delivered host run: `firmware/tests/core/host/host-tests.log`, `RESULT PASS tests=153`.
7. Against the brief: one read-only `git status` was run to see which build outputs git ignores; no other git command. `firmware/tests/core/.gitignore` keeps `host/build/` and the copied modules of the broken runs out of git; their logs stay tracked.

Round 1 result (F6, 61 rows, 153 tests): done. Round 2 below supersedes the counts, the row numbers and the readings U4 to U9.

## Round 2 (2026-11-11): rulings R1 to R8 and C1 to C6 of `firmware/docs/core-delta-1.md`

Specification: `design/firmware.md` line 3 now starts "Version F6, with F7 part 1 (2026-11-11): rulings R1 to R8 of firmware/docs/core-delta-1.md in sections 1 and 2;" (the lead's ruling on the version line; the full move to F7 is a later step of the lead's). Only line 3 and sections 1 and 2 changed: the diff against the saved F6 copy is `firmware/tests/core/evidence/r2-firmware-md.diff` (copy: `evidence/r2-firmware-md-before.md`). The table has 65 rows (61 before): row N is still line 132 + N, and every row from old row 13 on moved down by 2, and from old row 54 on by 4. Line numbers in the round 1 test comments are those of the F6 copy.

`firmware-check.py`: "0 failures" (`evidence/r2-fwcheck-final2.log`). A first version line "Version F7 part 1 ..." gave 1 failure, `FAIL header does not say Version F6`, from `design/firmware-check.py` lines 531 and 532 (`evidence/r2-fwcheck-final.log`); the lead then ruled to keep "Version F6, " and add the F7 part 1 sentence after it. No failure came from a ruling. The check script was not edited.

| Ruling | What changed in firmware.md | What changed in the code | Tests named after it |
|---|---|---|---|
| R1 | Row 12 actions start "only with the battery above B5 and free space above SFULL"; new rows 13 ("long press of the joystick centre, battery at B5") and 14 ("..., free space at SFULL"): no recording starts, the message 3 s; rule R-STB under the table; gesture table long press cell | guard `ABOVE_B5_ABOVE_SFULL` (the generator reads it from the actions cell, see below); after every row from another state into STANDBY, `sm_event` runs the STANDBY row for B2, else B5, else SFULL | `test_r1_long_press_at_b5_refused_with_message`, `test_r1_long_press_at_sfull_refused_with_message`, `test_r1_long_press_at_b5_and_sfull_battery_message`, `test_r1_entry_into_standby_checks_battery_then_storage`, `test_r1_entry_actions_are_those_of_the_standby_row`, `test_row_13`, `test_row_14` |
| R2 | Row 38: "VBUS removed, free space at SFULL, battery above B5" | guard `SFULL_ABOVE_B5` | `test_r2_vbus_out_with_sfull_and_b5_gives_battery_low`, `test_row_38` |
| R3 | Old row 53 split into rows 55 ("60 s elapsed": retry storage, every 60 s), 56 ("storage retry succeeds": STANDBY, RECOVERY first if the open flag is set), 57 ("storage retry fails": none) | action `RC_ACT_RETRY_STORAGE`, events `RC_EV_STORAGE_RETRY_OK` and `_FAILED`; the 60 s timer repeats while in ERR_STORAGE_FAULT; the fact `storage_init_ok` is gone | `test_r3_storage_retried_every_60s_until_success`, `test_row_55`, `test_row_56`, `test_row_57`, `test_row56_open_flag_set_recovery_first` |
| R4 | Rule "Order at init done" | none needed (rows in document order) | `test_r4_unfinished_recording_with_case_recovery_then_charging` |
| R5 | Same rule: battery first | on INIT_DONE in BOOT with no VBUS, B2 runs row 7 and B5 runs row 8 | `test_r5_init_done_reads_battery_first` |
| R6 | Row 15 (old 13): "..., then MT" | none (the code already did it) | `test_r6_row15_screen_on_centre_action_then_mt` |
| R7 | Rule in 2.1, the ruling's words | `rc_gesture_cancel_hold()` called on every change of state: no MW, long, short or double from that hold | `test_r7_hold_begun_in_charging_never_starts`, `test_r7_hold_cancelled_by_change_of_state_in_standby`, `test_r7_no_change_of_state_keeps_the_hold` |
| R8 | Sentence added to rule R-CHG | CHARGE_ON pushed on VBUS in when the row did not send it (or no row matched) | `test_r8_charge_on_at_every_vbus_appearance` |
| C1 | | `rc_core_battery(level)`: the only way to set the battery fact, both directions; a downward crossing runs its row; `rc_core_event` refuses the battery events; `rc_core.h` says the power part calls it after each fuel gauge sample whose level changed | `test_code_c1_battery_fact_both_directions`, `test_code_c1_battery_events_refused_from_event_entry` |
| C2 | | | `test_code_c2_row3_guard_refuses_b5` (kills m29) |
| C3 | | | `test_code_c3_b15_rearmed_by_vbus` (m15), `test_code_c3_s30_rearmed_by_new_recording` (m25), `test_code_c3_timers_refused_from_event_entry` (m33) |
| C4 | | `tg_get()` asserts the event exists and names the test | m09 now gives 12 named FAIL lines and no crash (`broken/broken-m09.log`) |
| C5 | | `testcase.yaml` allows `nrf54lm20bsim/nrf54lm20a/cpuapp` | Zephyr run below |
| C6 | | | m21 and m23: reasoning below; `test_code_c6_no_row_action_is_mw` |

C6, why m21 and m23 cannot change behaviour (both copies pass all 176 tests: `broken/broken-m21.log`, `broken/broken-m23.log`):
- m21 (`g->rel_t >= mark` to `>`): `rc_gesture_input` runs every deadline at or before t before it applies an edge at t. So when a release at t sets `rel_t = t`, every mark at or before t has already fired. `mark_live` is asked only about marks not yet fired, which are after `rel_t`, so both forms are false for them. A re-close clears `rel_pending`, and both forms then are true. No input gives a different result.
- m23 (MW added to the Vibration filter in `state_actions.c`): that filter sees only row actions. MW is pushed by `core.c` directly, never through it. `test_code_c6_no_row_action_is_mw` checks that no row, with any of the screen and open flag values, lists MW.

Generator: row 12's event text must stay exactly "long press of the joystick centre", because `firmware-check.py` check 17 requires the one row into RECORDING to have exactly that text. So the R1 guard is written at the start of row 12's actions cell, and `gen_table.py` reads it through an exact-phrase map (`ACTION_GUARDS`). The checksum now includes the guard. `count_rows.py` also checks that each `case N:` of `state_actions.c` carries the document line of row N.

Where I wrote more than the ruling says, or read it, for the lead to confirm:
- R1: the ruling says where the ring goes on entry, not what it does. I wrote "through the row of `STANDBY` for that event, with that row's actions" (B2: save settings and time, ship mode; B5 and SFULL: M3). For the refusal rows 13 and 14 the ruling names only the message, so there is no M3, unlike the other refusals.
- R4 and R5 together: the battery is read before the open flag when there is no VBUS. A start-up with an unfinished recording at B5 and no case goes to ERR_BATTERY_LOW; the recovery waits for the next boot. R4 speaks of the case attached, so I read R5 as first in that case.
- R3: the next try is 60 s after the previous try, not 60 s after the failure report.
- R7: a short press already released and waiting for its 400 ms window is not a hold, so a change of state does not cancel it.
- U4 and U5 (B15 re-armed by VBUS, S30 once per recording) are now asserted by the C3 tests, as the delta asks.

Results:
- Host: `firmware/tests/core/host/host-tests.log`: `suites=10 tests=176 pass=176 fail=0`, `RESULT PASS tests=176`, exit 0.
- Rows: `evidence/r2-count-rows.log` (and `evidence/r2-count-rows-2.log` after the version line): 65 rows in section 1.2 (the document states 65), 65 row tests, 65 action cases each with its row's line, `COUNT MATCH`.
- Broken copies (`firmware/tests/core/broken/broken-<name>.log`): long900 fail=28, row12to fail=13 plus the generator check, gap60 fail=2, row27act fail=3 (now the B5 row of RECORDING, row 29), each `RESULT FAIL`. The review's survivors: m15, m25, m29, m33 each fail=1 (`RESULT FAIL`); m09 fail=12. m21 and m23 pass (equivalent, above).
- Zephyr (`evidence/r2-zephyr-run-1.log`, `firmware/build-logs/20261111-113611-core-tests-r2.log`): "2 of 2 executed test configurations passed (100.00%), 0 built (not run), 0 failed, 0 errored, with no warnings", "352 of 352 executed test cases passed (100.00%) on 2 out of total 1514 platforms", exit 0, platforms `native_sim` and `nrf54lm20bsim/nrf54lm20a/cpuapp`. The log gives no split per platform.

Not done in round 2: nothing in the rulings was left out.

Round 2 result (65 rows, 176 tests): done. Round 2b below supersedes its counts, row numbers and the R4 and R5 reading.

## Round 2b (2026-11-11): the lead's correction R4b

The lead confirmed the round 2 readings except R4 with R5. Correction: an unfinished recording is recovered before the battery-low rule; only B2 skips recovery. Also, a recording never starts while the superblock open flag is set.

firmware.md (sections 1 and 2; diff against F6 in `firmware/tests/core/evidence/r2-firmware-md.diff`, copy before 2b in `evidence/r2b-firmware-md-before.md`):
- Row 12 actions now start "only with the superblock open flag clear, the battery above B5 and free space above SFULL".
- New row 13: `STANDBY` | "long press, superblock open flag set" | `RECOVERY` | no recording starts; VDD_SD on; mount; `RECOVERY` scans and closes the unfinished recording; the wearer presses again. The event text has no "joystick", because check 17 of `firmware-check.py` refuses a state change on an event naming the joystick other than the exact centre texts. The table has 66 rows; rows from old 13 on move down by 1.
- The order note (line 206): B2 (no VBUS) to `OFF` without recovery, the flag stays set; else open flag set: `RECOVERY` first, and at the end of the scan "scan done, no VBUS" enters `STANDBY` through R-STB (B5: `ERR_BATTERY_LOW`); else B5 (no VBUS); else rows 3 or 5. New rule R4b (line 207).
- The version line is unchanged: "Version F6, with F7 part 1 (2026-11-11): rulings R1 to R8 ... in sections 1 and 2;".

Code: guard `OPEN_CLEAR_ABOVE_B5_ABOVE_SFULL` on row 12; at init done the B5 redirect applies only with the open flag clear. The open flag now follows the core's own actions: OPEN sets it, and CLOSE, CLEAR_OPEN_FLAG and RUN_RECOVERY clear it. The caller sets it at start-up. A failed write (row 34) leaves it set, as the row says.

Tests (suite `rc_round2`): `test_r4b_b5_with_open_flag_at_init_done_recovers_first`, `test_r4b_b2_with_open_flag_goes_off_without_recovery`, `test_r4b_long_press_with_open_flag_runs_recovery_first`, `test_r4b_failed_write_then_case_then_long_press_never_records_over_it` (the lead's path), and `test_row_13`. New broken copy `r4b` (row 12 guard without the open flag): 3 failing tests.

My readings in 2b, for the lead:
- Row 13 actions "VDD_SD on; mount" are mine: `RECOVERY` needs the storage on and mounted, as after `BOOT`, and row 36 uses the same words. There is no message and no M3, because the correction names none.
- RUN_RECOVERY (row 57) is taken to clear the open flag, like CLEAR_OPEN_FLAG in rows 9 and 10.

Results:
- Host: `firmware/tests/core/host/host-tests.log`: `suites=10 tests=181 pass=181 fail=0`, `RESULT PASS tests=181`, exit 0.
- Rows: `evidence/r2b-count-rows.log`: 66 rows (the document states 66), 66 row tests, 66 action cases each with its row's line, `COUNT MATCH`.
- `firmware-check.py`: "0 failures" (`evidence/r2b-fwcheck-final.log`).
- Broken copies (`firmware/tests/core/broken/broken-<name>.log`): long900 fail=31, row12to fail=15 plus the generator check, gap60 fail=2, row27act fail=3 (the RECORDING B5 row, now row 30), m09 fail=12, m15, m25, m29, m33 fail=1 each, r4b fail=3, all `RESULT FAIL`; m21 and m23 pass (equivalent, round 2).
- Zephyr (`evidence/r2b-zephyr-run.log`, `firmware/build-logs/20261111-114428-core-tests-r2b.log`): "2 of 2 executed test configurations passed", "362 of 362 executed test cases passed", "with no warnings", exit 0, on `native_sim` and `nrf54lm20bsim/nrf54lm20a/cpuapp`.

Round 2b result (66 rows, 181 tests): done. Round 3 below supersedes its counts and row numbers.

## Round 3 (2026-11-11): rulings R9 to R14 and C7 to C9 of `firmware/docs/core-delta-2.md`

firmware.md: line 3 now names "rulings R1 to R8 of firmware/docs/core-delta-1.md and R9 to R14 of firmware/docs/core-delta-2.md in sections 1 and 2;". Everything else changed is in sections 1 and 2 (`firmware/tests/core/evidence/r3-firmware-md.diff`, copy before: `evidence/r3-firmware-md-before.md`). The table has 69 rows. The old to new row map is `evidence/r3-rowmap.json`.

| Ruling | firmware.md | Code | Tests |
|---|---|---|---|
| R9 | Old row 57 split: row 59 "storage retry succeeds, superblock open flag set" to `RECOVERY` (keep VDD_SD on); row 60 "..., superblock open flag clear" to `STANDBY` (R-STB applies); new rule "Open flag (ruling R9)" | `RC_ACT_RUN_RECOVERY` removed; only CLOSE and CLEAR_OPEN_FLAG clear the flag; guard `OPEN_CLEAR` | `test_r9_recovery_request_keeps_open_flag`, `test_r9_long_press_recovery_keeps_flag_until_scan_done`, `test_r9_retry_with_flag_clear_goes_to_standby`, `test_row_59`, `test_row_60` |
| R10 | New row 41: `CHARGING`, "VBUS removed, battery at B2", to `OFF`: save settings and time; ship mode; R-STB says B2 before B5 for every row leaving `CHARGING` or `TRANSFER` | guard `AT_B2` | `test_r10_leaving_case_at_b2_switches_off`, `test_row_41` |
| R11 | New rule "Storage fault"; R-STB order B2, storage fault, B5, SFULL; new row 24: `STANDBY`, "storage fault set at entry (rule R-STB)", to `ERR_STORAGE_FAULT`, none, the 60 s retry starts | fact `storage_fault`: set on entering ERR_STORAGE_FAULT (and at init in that state), cleared by INIT_DONE and STORAGE_RETRY_OK; internal event `RC_EV_STORAGE_FAULT_SET`, refused by `rc_core_event` | `test_r11_storage_fault_survives_the_case`, `test_r11_fault_cleared_only_by_successful_init`, `test_r15a_b2_checked_before_the_storage_fault`, `test_row_24` |
| R12 | Order note: battery events in `BOOT` are kept until "init done" | `rc_core_battery` in BOOT only keeps the level | `test_r12_b5_in_boot_kept_then_recovery_first`, `test_r12_b2_in_boot_kept_then_off`; rows 7 and 8 are now tested through "init done" |
| R13 | Row 8: "VDD_SD off; M3" | case 8 | `test_r13_row8_turns_sd_off`, `test_row_08` |
| R14 | Row 58 ("60 s elapsed"): at most one try per call of the tick, the next 60 s after it | the tick fires once and sets the next try to now + 60 s | `test_r14_one_retry_per_tick_whatever_the_delay` |
| C7 | | | m21: the R9 tests; m31: `test_code_c7_repeated_battery_level_does_nothing`; m35: `test_code_c7_invalid_battery_level_refused`; m40: `test_code_c7_sfull_event_sets_the_fact` |
| C8 | | | `test_r6_row15_...` renamed `test_r6_row16_screen_on_centre_action_then_mt` (row 16 is the short press row since round 2b) |
| C9 | | | m33 and m41: reasoning below |

Mutations (`firmware/tests/core/broken/broken-<name>.log`; m21 to m41 are review 2's names, m09 to m33r1 review 1's):
- m21 in its R9 form (entering RECOVERY clears the open flag; the review's own diff removed `RUN_RECOVERY`, which no longer exists): fail=3. m31: fail=1. m35: fail=1. m40: fail=1. Each is `RESULT FAIL`.
- C9, m33 (the battery fact set after the row runs instead of before) passes all 197 tests (`broken-m33.log`). The only code that reads `facts.batt` while a battery row runs is the R-STB entry check and the init-done order. No battery row goes from another state into `STANDBY`, the init-done order runs only on INIT_DONE, and the BOOT branch keeps the level in both forms. So no guard sees the difference.
- C9, m41 (the cancel skipped when the long press already fired) passes all 197 tests (`broken-m41.log`). After a long press, the warning and long-press deadlines are off because `long_fired` is set, and `centre_up` returns at `long_fired` before it looks at `cancelled` or `second`. Both forms give no event.
- Review 1 equivalents m21r1 and m23 still pass, as argued in round 2.

Problem found and fixed in this round: after the renumbering, rows 39 and 40 fell through into the new case 41 (a `break` was missing) and gave save settings and ship mode on leaving the case. `test_row_39` and `test_row_40` failed in the first host run (`evidence/r3-host-run-1-debug.log`). With the `break` added, the next run passed (`evidence/r3-host-run-2-debug.log`).

R15 (the lead's ruling, after my question at the start of round 3): "With no VBUS, a battery at B2 always ends in OFF." It is written into firmware.md as rule R15 under the table. R-STB now reads "battery at B2 with no VBUS goes to `OFF` (ruling R15)", and the order note names R15 for a failed storage init in BOOT. Two new rows give the states that had none their B2 row: row 65 (`ERR_MIC_FAULT`, "battery reaches B2", to `OFF`) and row 67 (`ERR_CHARGER`, the same), both "save settings and time; ship mode". The table has 71 rows (old rows 65 to 69 are now 66, 68 to 71: `evidence/r3b-rowmap.json`).
- Code: on every change of state into `STANDBY`, `ERR_STORAGE_FAULT`, `ERR_STORAGE_FULL`, `ERR_BATTERY_LOW`, `ERR_MIC_FAULT` or `ERR_CHARGER`, with the battery fact at B2 and no VBUS, the core takes that state's B2 row first. Then R-STB checks the storage fault, B5 and SFULL. "Init done" keeps its R5 redirect. `RECOVERY` is not in the list (R4b).
- Tests: `test_r15a_b2_checked_before_the_storage_fault` (path a), `test_r15b_failed_storage_init_with_b2_kept_goes_off` and `test_r12_b2_in_boot_kept_then_off` (path b), `test_r15_walk_every_entry_with_b2_kept_ends_off`, `test_r15_with_vbus_b2_does_not_switch_off`, `test_row_65`, `test_row_67`.
- The walk takes every row from another state into one of the six states, through the real entry points, with the battery fact at B2 and no VBUS, and asserts OFF and ship mode. It skips rows whose event is a battery event (the event sets the level itself), the internal R-STB row, and rows whose guard cannot hold at B2. `ERR_BATTERY_LOW` is entered by none: every row into it is a B5 row, and a B2 row comes before "VBUS removed, battery at B5". The test asserts that count is 0 and that each of the other five states is entered at least once.
- New broken copy `r15` (the entry check removed): 7 failing tests, `RESULT FAIL`.
- Rows 22 and 56 were my reading for R10's actions. R15's "same actions as the other B2 rows" is read the same way for rows 65 and 67.

Results (after R15):
- Host: `firmware/tests/core/host/host-tests.log`: `suites=11 tests=202 pass=202 fail=0`, `RESULT PASS tests=202`, exit 0.
- Rows: `evidence/r3b-count-rows.log`: 71 rows (the document states 71), 71 row tests, 71 action cases each with its row's line, `COUNT MATCH`.
- `firmware-check.py`: "0 failures" (`evidence/r3b-fwcheck-final.log`).
- Broken copies, each `RESULT FAIL`: long900 fail=34, row12to fail=16, gap60 fail=2, row27act fail=3, m09 fail=12, review 1's m15, m25, m29, m33r1 fail=1 each, r4b fail=3, review 2's m21 fail=3, m31, m35, m40 fail=1 each, r15 fail=7. m21r1, m23, m33 and m41 pass all 202 (equivalent: round 2 and above; m33 stays equivalent with R15, because a battery row never enters a state at B2).
- Zephyr (`evidence/r3b-zephyr-run.log`, `firmware/build-logs/20261111-122607-core-tests-r3b.log`): "2 of 2 executed test configurations passed", "404 of 404 executed test cases passed", "with no warnings", exit 0, on `native_sim` and `nrf54lm20bsim/nrf54lm20a/cpuapp`. The round 3 run before R15 (`evidence/r3-zephyr-run.log`) had 394 of 394.

Not implemented as written: nothing.

Round 3 result (71 rows, 202 tests): done. Round 4 below supersedes its counts.

## Round 4 (2026-11-11): ruling R16 and C10 (`firmware/docs/core-delta-2.md`, "Round 4")

firmware.md: line 3 now ends "... and R15, R16 in sections 1 and 2;". Rule R16 is added under R15 (diff: `firmware/tests/core/evidence/r4-firmware-md.diff`, lines 3 and 212). No row changes: the table keeps 71 rows. The lead confirmed "save settings and time; ship mode" for the B2 rows.

R16 in my words for the states the ruling does not name, for the lead to confirm. In `CHARGING`, the row "VBUS removed, battery at B2" (row 41) is the B2 check. `TRANSFER`, `RECOVERY` and `FACTORY_TEST` have no "battery reaches B2" row and get none. They take their own "VBUS removed" row (or none, in `RECOVERY`) and reach `OFF` through the B2 check of the state they enter: `TRANSFER` through `STANDBY` (R15, R-STB), so the transfer command is still aborted; `FACTORY_TEST` through `BOOT` and "init done"; `RECOVERY` at the end of its scan. `BOOT` has row 7, so at B2 with VBUS removed it goes to `OFF` before "init done"; R12's "kept until init done" is read as applying to battery events, not to VBUS removal.

Code: in `sm_event`, a VBUS removal at B2 runs the state's BATT_B2 row when the table has one; otherwise the state's own row runs and R15 checks the entry.

C10: `rc_core_event` already refused the six events the core makes for itself. Each now has its own test: `test_c10_refuses_storage_fault_set`, `_timer_5s`, `_timer_60s`, `_long_press`, `_short_press`, `_double_press`. The reviewer's r21 (STORAGE_FAULT_SET accepted) fails 1 test (`broken/broken-r21.log`).

Tests (suite `rc_round4`):
- `test_r16_storage_fault_entered_in_case_then_vbus_out_goes_off`: the reviewer's D1 path from BOOT.
- `test_r16_recovery_read_error_in_case_then_vbus_out_goes_off`: the D1 path from RECOVERY.
- `test_r16_b2_row_comes_before_the_vbus_removed_row`
- `test_r16_above_b2_vbus_out_keeps_the_state_row`
- `test_r16_walk_every_state_vbus_present_b2_then_vbus_out_ends_off`: the walk of the bar. Every state starts in the case at B2, VBUS is removed, and the test asserts OFF (RECOVERY after its scan, BOOT after "init done"). SHIP stays SHIP: the factory ship mode entered in the case completes on VBUS removal (FW 8.4). The walk starts each state with `rc_core_init`, not through a row.
- `test_r16_sequences_never_awake_at_b2_without_vbus`: my own sequence walk, not the reviewer's (I did not run anything in the review folders). It covers 14 states × 8 fact sets × 24³ sequences of three steps (23 outside events and a 70 s tick), 1,548,288 runs. After every step with no VBUS, the ring is OFF, SHIP, BOOT or RECOVERY. The reviewer's own 92,928-sequence walk is theirs to rerun.
- One expected value I set in round 2 changed with R16: in `test_r1_entry_into_standby_checks_battery_then_storage`, ERR_CHARGER at B2 with VBUS removed now ends OFF through its own B2 row 67 instead of row 22 through STANDBY. The end state is OFF in both cases, and the line carries a comment.

Results:
- Host: `firmware/tests/core/host/host-tests.log`: `suites=12 tests=214 pass=214 fail=0`, `RESULT PASS tests=214`, exit 0.
- Rows: `evidence/r4-count-rows.log`: 71 rows (the document states 71), 71 row tests, 71 action cases with their lines, `COUNT MATCH`.
- `firmware-check.py`: "0 failures" (`evidence/r4-fwcheck-final.log`).
- Broken copies, each `RESULT FAIL`: long900 fail=34, row12to fail=16, gap60 fail=2, row27act fail=3, m09 fail=12, m15, m25, m29 fail=1 each, m33r1 fail=3, r4b fail=3, m21 fail=3, m31, m35, m40 fail=1 each, r15 fail=8, r16 fail=6 (the new walks among them), r21 fail=1. m21r1, m23, m33 and m41 pass (equivalent, earlier rounds).
- Zephyr (`evidence/r4-zephyr-run.log`, `firmware/build-logs/20261111-123647-core-tests-r4.log`): "2 of 2 executed test configurations passed", "428 of 428 executed test cases passed", "with no warnings", exit 0, on `native_sim` and `nrf54lm20bsim/nrf54lm20a/cpuapp`.

Not implemented as written: nothing.

Round 4 result (214 tests): done; the lead confirmed the R16 readings. Final review: S1 0, S2 0; the test gaps T1 and T2 are closed below.

## Final review test gaps (T1, T2)

- T1: `test_t1_r16_does_not_fire_at_b5` (ERR_STORAGE_FAULT in the case at B5, VBUS removed, stays there); mutation v02 fails 1 test (`firmware/tests/core/broken/broken-v02.log`).
- T2: `test_t2_r16_boot_vbus_out_at_b2_takes_row_7_before_init_done` (BOOT at B2, VBUS removed, row 7, OFF); mutation v09 fails 1 test (`broken/broken-v09.log`).
- Tests only: the module and firmware.md are unchanged. Host: `suites=12 tests=216 pass=216 fail=0`, `RESULT PASS tests=216`, exit 0. `count_rows.py`: 71 and 71, `COUNT MATCH` (`evidence/r5-count-rows.log`).
- Zephyr (`RING_REMOTE_SRC=/root/ring-os/src-core`; `evidence/r5-zephyr-run.log`, `firmware/build-logs/20261111-125303-core-tests-t1t2.log`): "432 of 432 executed test cases passed", 2 of 2 configurations (native_sim and nrf54lm20bsim/nrf54lm20a/cpuapp), exit 0.

RESULT: done, T1 and T2 tested, v02 and v09 fail; host 216 of 216 pass, Zephyr 432 of 432 on both targets.

## Step 6 (2026-11-13): unit U1 `core6`, the row "recording sign not drawn" and the sign hook

Contract: `firmware/docs/step6-plan.md`, section 3 "U1 `core6`", decisions D1 (A, the sign hook), D2 (row 12 reads "M1; open", ruling R21 in `design/firmware.md` line 144) and D9 (generator and row count run with Python on the Mac).

### What changed

- `modules/ring_core/tools/gen_table.py`: `EVENT_MAP` knows the new event text "long press of the joystick centre, recording sign not drawn" (guard `SIGN_NOT_DRAWN`); `ACTION_GUARDS` now matches the longer guard phrase of row 12 ("... and the recording sign drawn"), guard `OPEN_CLEAR_ABOVE_B5_ABOVE_SFULL_SIGN`. No other text of the specification needed a change in the generator. Run: `python3 -B firmware/modules/ring_core/tools/gen_table.py` prints `rows=72 stated=72 fnv1a32=0xe61dece0` (`build-logs/step6/u1-gen-run.log`). Table: 72 rows, `RC_TABLE_ROWS 72`.
- `include/ring_core/rc_types.h`: guard `RC_G_OPEN_CLEAR_ABOVE_B5_ABOVE_SFULL` is renamed `..._SIGN` (the name says what it tests); new guard `RC_G_SIGN_NOT_DRAWN`; new fact `rc_facts.sign_not_drawn` (set by the core for one long press only, never by a caller).
- `src/state_table.c`: the guard names and the two guard tests (row 12 also needs `!sign_not_drawn`; row 16 needs `sign_not_drawn`).
- `include/ring_core/rc_core.h`, `src/core.c`: `typedef int (*rc_sign_hook_fn)(void *ctx, rc_ms_t t)` and `rc_core_set_sign_hook(core, fn, ctx)` (fn NULL clears it; `rc_core_init` clears it). `sm_event` calls the hook once for a `LONG_PRESS` that starts in `STANDBY` when the open flag is clear, the battery is above B5 and free space is above SFULL, before the row is chosen (time = the 1,000 ms mark). 0 = drawn (row 12); anything else sets `sign_not_drawn` (row 16). The fact is cleared right after the row ran. With no hook the sign counts as drawn.
- `src/state_actions.c`: row 12 is "M1; open" (R21); new row 16 is "M3; event log record" (`RC_ACT_M3`, `RC_ACT_LOG_EVENT`; VDD_MIC stays off because no OPEN is pushed); old rows 16 to 71 are cases 17 to 72, each with its new document line (row N is line 132 + N).
- Tests: see "Tests and renumbering". Broken copies: `tests/core/broken/run_broken.sh` (new copies, copy folder and apply-only switch), `named_cases.txt` (the case each copy must fail), `run_all.sh` (all 26 on the host); `tests/core/broken_run.sh` (the three new copies through twister on both targets); `tests/core/CMakeLists.txt` takes `RING_CORE_DIR`; `tests/core/unit_run_core.sh` (this unit's runner until `tools/unit_run.sh` exists).

### Tests and renumbering

New cases: `rc_rows.test_row_16`; `rc_rules.test_sign_hook_once_per_press`; `rc_rules.test_sign_hook_not_called_when_refused_otherwise` (open flag, B5 and B2, SFULL, B5 with SFULL, every other state, and the B15 positive side); `rc_rules.test_no_hook_takes_the_sign_as_drawn`; `rc_rules.test_refused_sign_leaves_no_recording_m3_and_event_log`. Count: 216 before, 221 now (216 + 1 row test + 4 rules).

Every renumbered row: the old rows 16 to 71 are now 17 to 72 (new row 16 is the first at line 148; the old table already named line 148 for the short press, which is now line 149). The old rows 1 to 15 keep their numbers. Every changed number in the tests is listed one by one in `build-logs/step6/u1-renumber.log` (88 lines: the `ROW(NN, num)` lines of `test_rows.c` for rows 16 to 71, each `zassert_equal(out.last_row, N)` with N of 16 or more, the `entry_case` calls of `test_round2.c`, and the list `expect_rows` of `test_rules.c`: 25, 29, 31, 32, 34, 35, 36, 37 became 26, 30, 32, 33, 35, 36, 37, 38). The test names `test_row_16` to `test_row_71` are now `test_row_17` to `test_row_72`; `test_r6_row16_screen_on_centre_action_then_mt` is `test_r6_row17_...`. A copy of the test sources before the renumbering: `build-logs/step6/u1-src-before-renumber/`.

Expected values changed beyond row numbers (all caused by ruling R21, row 12 "M1; open"): the order of the action list of row 12 in `rc_rows.test_row_12` and in the three cases of `test_rules.c` that list `OPEN, M1` (`test_c2_long_press_with_screen_on_starts`, `test_c4_long_press_with_screen_off_starts` and `test_vibration_off_drops_mh_mt_only`; the third also has MW first): they now list `M1, OPEN`. Also `test_table_has_71_rows_in_order` is now `test_table_has_72_rows_in_order` (72 rows, same line rule 133 + i). Nothing else was edited: no limit, threshold or timing.

### Rows of section 2.1 of the plan

| Rule | Case | Evidence |
|---|---|---|
| C10 (long press in STANDBY starts a recording only with open flag clear, battery above B5, free space above SFULL and the sign drawn) | `rc_rows.test_row_12` (row 12, actions M1 then OPEN, to RECORDING), `rc_rules.test_sign_hook_not_called_when_refused_otherwise` (rows 13, 14, 15 with the hook never asked), `rc_rows.test_row_13`, `rc_rows.test_row_14`, `rc_rows.test_row_15` | host `u1-host-2.log`; Zephyr: `u1-unit-run2` log, 221 of 221 on each target |
| C11 (sign not drawn: no recording, VDD_MIC stays off, M3, event log record) | `rc_rows.test_row_16`, `rc_rules.test_refused_sign_leaves_no_recording_m3_and_event_log` (state STANDBY, no OPEN, open flag clear, `rc_core_mic_rail` false) | same |
| C27, the core's part (M1 at the press, before the open) | `rc_rows.test_row_12` and the three `test_rules.c` cases above (order M1, OPEN) | same |

The recorder's side of C10, C11 and C27 (`recorder_sign.*`, `recorder_actions.test_m1_at_start`) belongs to the join unit.

### Broken copies

File `tests/core/broken/named_cases.txt` names, for each of the 26 copies, the case it must fail. Host run of all 26 after the table was refreshed (`build-logs/step6/u1-broken-host-1.log`, last line `BROKEN ALL PASS 26 copies`):

| Copy | Case it still fails |
|---|---|
| long900 | `rc_collisions.test_c2_long_press_with_screen_on_starts` |
| row12to | `rc_rows.test_row_12` (the generator check fails too) |
| gap60 | `rc_gesture.test_sw2_gap_59ms_not_double` |
| row27act | `rc_rows.test_row_32` (was `test_row_31`) |
| m09 | `rc_gesture.test_next_tick_follows_deadlines` |
| m15 | `rc_round2.test_code_c3_b15_rearmed_by_vbus` |
| m21 | `rc_round3.test_r9_recovery_request_keeps_open_flag` |
| m25 | `rc_round2.test_code_c3_s30_rearmed_by_new_recording` |
| m29 | `rc_round2.test_code_c2_row3_guard_refuses_b5` |
| m31 | `rc_round3.test_code_c7_repeated_battery_level_does_nothing` |
| m33r1 | `rc_round4.test_c10_refuses_timer_5s` |
| m35 | `rc_round3.test_code_c7_invalid_battery_level_refused` |
| m40 | `rc_round3.test_code_c7_sfull_event_sets_the_fact` |
| r15 | `rc_round3.test_r15a_b2_checked_before_the_storage_fault` |
| r16 | `rc_round4.test_r16_b2_row_comes_before_the_vbus_removed_row` |
| r21 | `rc_round4.test_c10_refuses_storage_fault_set` |
| r4b | `rc_rows.test_row_13` |
| v02 | `rc_round4.test_t1_r16_does_not_fire_at_b5` |
| v09 | `rc_round4.test_t2_r16_boot_vbus_out_at_b2_takes_row_7_before_init_done` |
| m21r1, m23, m33, m41 | none: equivalent mutations (rounds 2 and 3 argue why); the suite passes on them, as it did before step 6; each is declared equivalent in this file: m21r1 at line 235 and line 304 ("Review 1 equivalents m21r1 and m23 still pass, as argued in round 2"), m23 at line 236 and line 304, m33 at line 302 ("C9, m33 ... passes all 197 tests") and m41 at line 303 ("C9, m41 ... passes all 197 tests"); line 319 names all four ("m21r1, m23, m33 and m41 pass all 202 (equivalent ...)") |
| sign_ignored (new) | `rc_rows.test_row_16` |
| sign_hook_twice (new) | `rc_rules.test_sign_hook_once_per_press` |
| sign_before_b5 (new) | `rc_rules.test_sign_hook_not_called_when_refused_otherwise` |

So 19 of the 23 old copies fail their named case; the other 4 were already equivalent before this step and cannot fail. The edits that had to follow the new table: `row12to` (guard name in the row text), `row27act` (case 31 is now case 32), `r4b` (the guard line now also has `!f->sign_not_drawn`). Before the table was refreshed the old copy folders held the 71-row table; each `copy-<name>/` was rebuilt by the run above. The three new copies on both targets: see the run below.

### Runs cited

| Run | Runner | Result (file, line) |
|---|---|---|
| Host row count | `python3 -B firmware/tests/core/count_rows.py` on the Mac | `build-logs/step6/u1-count-rows-1.log`: 72 rows in the document, 72 row tests, 72 action cases, last line `COUNT MATCH` |
| Host suite | `sh tests/core/host/run_host_tests.sh` | `u1-host-2.log`: `suites=13 tests=221 pass=221 fail=0`, `RESULT PASS tests=221`, exit 0. Before (`u1-red-count-rows.log`, `u1-red-host.log`): `COUNT MISMATCH`, 71 row tests, generator check FAIL (committed 71 rows, fresh 72) |
| Host broken copies | `sh tests/core/broken/run_all.sh` | `u1-broken-host-1.log`, last line before the exit code: `BROKEN ALL PASS 26 copies` |
| Core alone on the server | my `tests/core/unit_run_core.sh tests/core` | `u1-core-run1.stdout`: 221 of 221 on both targets, the three new copies fail their named case on both targets, last line `UNIT PASS tests/core` |
| Four folders on the server | my `tests/core/unit_run_core.sh tests/core tests/screens tests/control tests/relay` (written before `tools/unit_run.sh` existed; I did not rerun with it) | `u1-unit-run2.stdout` line 60: `UNIT PASS tests/core tests/screens tests/control tests/relay`; line 62 `# remote exit code: 0`. Cases per target: core 221, screens 48, control 9, relay 23 (lines 10 to 54); the broken copies of screens, control and relay passed inside it |
| Two-device tests | `remote.sh` with a loop over `tests/bsim/screens`, `control` and `relay` `run.sh` (no `--broken`); `tools/unit_run.sh` only runs twister folders, so it does not serve | `u1-bsim-run3.stdout` lines 87 to 88, 1010 to 1011, 1537 to 1538 (`RESULT PASS`, `BSIM <name> exit 0`), line 1539 `BSIM ALL PASS screens control relay`, line 1541 `# remote exit code: 0` |

Where the new sign copies fail on the Zephyr targets: `u1-core-run1.stdout` (and the broken part of `u1-unit-run2.stdout`) quote the failed named case per board. Not done: the full `tools/build_all.sh` (not mine to run); no test of the recorder side (join unit).

Open note for the join unit: the glue and screens find rows by event through the table, so row 16 (event `LONG_PRESS`) shows up as a second long-press row of `STANDBY`; the screens and control suites above pass with it. The product must call `rc_core_set_sign_hook()` after `rc_core_init()`.

questions_for_owner: none

RESULT: done, row 16 and the sign hook are in the 72-row core (count 72 and 72), the core passes 221 of 221 on both targets, 19 of 23 old copies and the 3 new ones fail their named case (4 old ones are documented equivalents), and the screens, control and relay suites and two-device tests pass.
