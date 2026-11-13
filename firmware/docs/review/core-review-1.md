# Core review 1: ring core against design/firmware.md F6

Reviewer: independent judge (did not write the code). Version: commit 6039562 (HEAD at the time of the run; note: I ran one read-only `git log --oneline -1` to read the commit id, which the brief forbade; no other git command). Files judged: `firmware/modules/ring_core/` and `firmware/tests/core/`, unchanged. All my copies, probes and logs are in `firmware/docs/review/core-review-1/`.

Independence: the brief did not carry the builder's verdict, only the builder's notes, which I treated as claims.

Method in one paragraph: I read the specification lines 91 to 283 and 286 to 309, read every source and test file, compared the 61 rows with my own parser (`cmp_rows.py`, output `cmp_rows.log`), ran the delivered host suite (`base-host-run.log`), ran my own probes through the real entry points (`probe.c`, `probe2.c`), and ran 46 mutation attempts (`run_mut.sh`, `run_mut2.sh`, `run_mut3.sh`) each on a copy under `mut/<id>/ring_core`.

## 1. Rows (bar item 1)

Evidence for from-state, event text, to-state and document line: `cmp_rows.py` parses lines 133 to 193 of the specification itself and compares with `state_table.inc`: `cmp_rows.log` last line `diffs 0`, 61 lines `OK`. Guards were compared by hand to the event text (table below, in brackets). Actions: read from `state_actions.c` and compared with the specification action text line by line; the ordered list is in the table. Each row has exactly one row test (`count_rows.py` shape, test line given).

Result: 61 of 61 rows equal the specification in from-state, event, guard, to-state and ordered actions, with one note: row 13 (finding F5) has an extra MT on the screen-on branch that the row text does not list; section 3.1 line 301 supports it (U12), so it is S3, not S2.

Rows 1 and 2 share one `case` block (state_actions.c:22-25). Row 13's action list in the table shows both branches (screen on: SCREEN_CENTRE MT; screen off: SCREEN_ON SCR_STATUS_5S).

| row | spec line | from | event | to | code: table line / actions line | action list in code (ordered) | test line | verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | 133 | SHIP | VBUS appears (case contact) | BOOT | 4 / 22 | CHARGE_ON | 28 | pass |
| 2 | 134 | OFF | VBUS appears | BOOT | 5 / 23 | CHARGE_ON | 29 | pass |
| 3 | 135 | BOOT | init done, superblock open flag clear, no VBUS, battery [guard OPEN_CLEAR_NO_VBUS_ABOVE_B5] | STANDBY | 6 / 26 | SD_OFF | 30 | pass |
| 4 | 136 | BOOT | init done, superblock open flag set [guard OPEN_SET] | RECOVERY | 7 / 29 | SD_ON | 31 | pass |
| 5 | 137 | BOOT | init done, VBUS present [guard VBUS] | CHARGING | 8 / 32 | SD_OFF CHARGE_ON | 32 | pass |
| 6 | 138 | BOOT | storage init fails 3 times, 200 ms apart | ERR_STORAGE_FAULT | 9 / 36 | LOG_EVENT MF | 33 | pass |
| 7 | 139 | BOOT | battery at B2 and no VBUS [guard NO_VBUS] | OFF | 10 / 40 | SHIP_MODE | 34 | pass |
| 8 | 140 | BOOT | battery at B5 and no VBUS [guard NO_VBUS] | ERR_BATTERY_LOW | 11 / 43 | M3 | 35 | pass |
| 9 | 141 | RECOVERY | scan done, no VBUS [guard NO_VBUS] | STANDBY | 12 / 46 | WRITE_CLOSE_RECOVERED CLEAR_OPEN_FLAG SD_OFF | 36 | pass |
| 10 | 142 | RECOVERY | scan done, VBUS present [guard VBUS] | CHARGING | 13 / 51 | WRITE_CLOSE_RECOVERED CLEAR_OPEN_FLAG SD_OFF CHARGE_ON | 37 | pass |
| 11 | 143 | RECOVERY | read error during scan | ERR_STORAGE_FAULT | 14 / 57 | LOG_EVENT MF | 39 | pass |
| 12 | 144 | STANDBY | long press of the joystick centre | RECORDING | 15 / 61 | OPEN M1 | 40 | pass |
| 13 | 145 | STANDBY | short press of the joystick centre | STANDBY | 16 / 66 | SCREEN_CENTRE MT SCREEN_ON SCR_STATUS_5S | 41 | pass with note F5 (extra MT on the screen-on branch) |
| 14 | 146 | STANDBY | double press of the joystick centre | STANDBY | 17 / 75 | (none) | 42 | pass |
| 15 | 147 | STANDBY | menu "Power off" confirmed | OFF | 18 / 77 | SAVE_SETTINGS_TIME M2 SHIP_MODE | 43 | pass |
| 16 | 148 | STANDBY | VBUS appears | CHARGING | 19 / 82 | CHARGE_ON | 44 | pass |
| 17 | 149 | STANDBY | battery reaches B15 | STANDBY | 20 / 85 | M3 SCR_STATUS_5S | 45 | pass |
| 18 | 150 | STANDBY | battery reaches B5 | ERR_BATTERY_LOW | 21 / 92 | M3 | 46 | pass |
| 19 | 151 | STANDBY | battery reaches B2 | OFF | 22 / 95 | SAVE_SETTINGS_TIME SHIP_MODE | 47 | pass |
| 20 | 152 | STANDBY | free space at SFULL | ERR_STORAGE_FULL | 23 / 99 | M3 | 48 | pass |
| 21 | 153 | RECORDING | long press of the joystick centre | STANDBY | 24 / 102 | CLOSE M2 | 49 | pass |
| 22 | 154 | RECORDING | short press of the joystick centre | RECORDING | 25 / 106 | HIGHLIGHT MH SCR_RECORDING_3S | 50 | pass |
| 23 | 155 | RECORDING | double press of the joystick centre | RECORDING | 26 / 111 | (none) | 51 | pass |
| 24 | 156 | RECORDING | BLE control "highlight" from a bonded phone | RECORDING | 27 / 113 | HIGHLIGHT MH | 52 | pass |
| 25 | 157 | RECORDING | VBUS appears (case insertion during a recording) | CHARGING | 28 / 117 | CLOSE M2 CHARGE_ON | 53 | pass |
| 26 | 158 | RECORDING | battery reaches B15 | RECORDING | 29 / 122 | M3 | 54 | pass |
| 27 | 159 | RECORDING | battery reaches B5 | ERR_BATTERY_LOW | 30 / 128 | CLOSE M3 | 55 | pass |
| 28 | 160 | RECORDING | battery reaches B2 | OFF | 31 / 132 | CLOSE SHIP_MODE | 56 | pass |
| 29 | 161 | RECORDING | free space reaches S30 | RECORDING | 32 / 136 | M3 SCR_MSG_30MIN_3S | 57 | pass |
| 30 | 162 | RECORDING | free space at SFULL | ERR_STORAGE_FULL | 33 / 143 | CLOSE M3 | 58 | pass |
| 31 | 163 | RECORDING | chunk write fails 3 times | ERR_STORAGE_FAULT | 34 / 147 | STOP_PDM CLOCKS_LOW MIC_OFF MF | 59 | pass |
| 32 | 164 | RECORDING | the PDM instance gives no block for 100 ms | ERR_MIC_FAULT | 35 / 153 | CLOSE MF | 61 | pass |
| 33 | 165 | RECORDING | sudden power loss (cell cut, short, brown-out) during a | BOOT | 36 / 157 | (none) | 62 | pass |
| 34 | 166 | CHARGING | USB configured by the case (`USBD_MSG_CONFIGURATION`) | TRANSFER | 37 / 159 | SD_ON MOUNT | 63 | pass |
| 35 | 167 | CHARGING | VBUS removed, free space above SFULL, battery above B5 [guard ABOVE_SFULL_ABOVE_B5] | STANDBY | 38 / 163 | (none) | 64 | pass |
| 36 | 168 | CHARGING | VBUS removed, free space at SFULL [guard SFULL] | ERR_STORAGE_FULL | 39 / 164 | (none) | 65 | pass |
| 37 | 169 | CHARGING | VBUS removed, battery at B5 [guard AT_B5] | ERR_BATTERY_LOW | 40 / 165 | (none) | 66 | pass |
| 38 | 170 | CHARGING | nPM1304 event charge error | ERR_CHARGER | 41 / 167 | LOG_CHARGE_ERROR CHARGE_OFF MF | 67 | pass |
| 39 | 171 | CHARGING | long press | CHARGING | 42 / 172 | M3 SCR_MSG_IN_CASE_3S | 68 | pass |
| 40 | 172 | TRANSFER | USB suspended or unconfigured by the case | CHARGING | 43 / 176 | FINISH_COMMAND SD_OFF CHARGE_ON | 69 | pass |
| 41 | 173 | TRANSFER | VBUS removed | STANDBY | 44 / 181 | ABORT_COMMAND SD_OFF | 70 | pass |
| 42 | 174 | TRANSFER | command FW_END accepted | BOOT | 45 / 185 | REQUEST_UPGRADE_TEST REBOOT | 71 | pass |
| 43 | 175 | TRANSFER | command FACTORY_ENTER with the factory flag set [guard FACTORY_FLAG] | FACTORY_TEST | 46 / 189 | FACTORY_MODE | 72 | pass |
| 44 | 176 | TRANSFER | long press | TRANSFER | 47 / 192 | M3 | 73 | pass |
| 45 | 177 | ERR_STORAGE_FULL | VBUS appears | CHARGING | 48 / 195 | CHARGE_ON | 74 | pass |
| 46 | 178 | ERR_STORAGE_FULL | long press | ERR_STORAGE_FULL | 49 / 198 | M3 SCR_MSG_STORAGE_FULL_3S | 75 | pass |
| 47 | 179 | ERR_STORAGE_FULL | battery reaches B5 | ERR_BATTERY_LOW | 50 / 202 | M3 | 76 | pass |
| 48 | 180 | ERR_STORAGE_FULL | battery reaches B2 | OFF | 51 / 205 | SHIP_MODE | 77 | pass |
| 49 | 181 | ERR_BATTERY_LOW | VBUS appears | CHARGING | 52 / 208 | CHARGE_ON | 78 | pass |
| 50 | 182 | ERR_BATTERY_LOW | long press | ERR_BATTERY_LOW | 53 / 211 | M3 SCR_MSG_BATTERY_LOW_3S | 79 | pass |
| 51 | 183 | ERR_BATTERY_LOW | battery reaches B2 | OFF | 54 / 215 | SAVE_SETTINGS_TIME SHIP_MODE | 80 | pass |
| 52 | 184 | ERR_STORAGE_FAULT | VBUS appears | CHARGING | 55 / 219 | CHARGE_ON | 81 | pass |
| 53 | 185 | ERR_STORAGE_FAULT | 60 s elapsed and storage init succeeds [guard STORAGE_INIT_OK] | STANDBY | 56 / 222 | RUN_RECOVERY | 82 | pass |
| 54 | 186 | ERR_STORAGE_FAULT | battery reaches B2 | OFF | 57 / 227 | SHIP_MODE | 83 | pass |
| 55 | 187 | ERR_MIC_FAULT | 5 s elapsed | STANDBY | 58 / 230 | (none) | 84 | pass |
| 56 | 188 | ERR_MIC_FAULT | VBUS appears | CHARGING | 59 / 232 | CHARGE_ON | 85 | pass |
| 57 | 189 | ERR_CHARGER | VBUS removed | STANDBY | 60 / 235 | (none) | 86 | pass |
| 58 | 190 | FACTORY_TEST | command FACTORY_EXIT | BOOT | 61 / 237 | REBOOT | 87 | pass |
| 59 | 191 | FACTORY_TEST | command SHIP_ENTER | SHIP | 62 / 240 | CLEAR_FACTORY_FLAG SHIP_MODE | 88 | pass |
| 60 | 192 | FACTORY_TEST | command SHIP_SAMPLE (sample rings only) | SHIP | 63 / 244 | SHIP_MODE | 90 | pass |
| 61 | 193 | FACTORY_TEST | VBUS removed, no ship command accepted | BOOT | 64 / 247 | REBOOT | 91 | pass |

## 2. Gestures (bar item 2)

Each item read in `gesture.c` / `core.c` and exercised by the delivered tests (literal spec numbers in `test_gesture.c`, not module constants: `grep` of `RC_*_MS` in tests found none) and by mutations.

| Item | Spec | Code | Verdict |
|---|---|---|---|
| Graze under 40 ms ignored, 40 included | 214, 221 | gesture.c:78 (`dur < RC_SHORT_MIN_MS`), header rc_gesture.h:18 value 40 | pass (test hold_39 and hold_40; m28 caught) |
| Short press 40 to 450 ms, 450 included, 451 ignored | 128, 212, 221 vs 215 | gesture.c:78, rc_gesture.h:19 value 450 | pass (reading U1; m05 caught) |
| MW at 500 ms, once, STANDBY and RECORDING only | 215, 223, 237 | gesture.c:109-110,147-150; core.c:127-131 | pass (m07, m13 caught) |
| Long press at 1,000 ms while held, once per press, release does nothing | 211, 240 | gesture.c:111-112,151-155,75-77 | pass (m45 caught at 999; m32 caught) |
| Window 400 ms after release, short fires when it closes | 212, 222 | gesture.c:114 (release + 401, first ms after) | pass (reading U3; m24 caught) |
| Double press, second press 60 to 400 ms after first release | 213, 222 | gesture.c:64 (`>= 60`), 114 | pass (59, 60, 400, 401 tested both sources; m06, m20, m55 caught) |
| Release hold-off 30 ms | 224, 255 | gesture.c:113, 233-237 | pass (m08, m19, m36 caught) |
| Direction decision window 40 ms | 225, 254 | gesture.c:107 | pass (m09 caught, by a crash: finding F7) |
| Direction repeat: 500 ms, then every 150 ms | 252 | gesture.c:141, 145 (from the press edge, U17) | pass (m10, m11 caught) |
| After a direction is sent every other switch is ignored until all open | 254 | gesture.c:222-231 | pass (m52 caught) |
| Case SW2: direction 0 to 39 ms before SW2 dropped, 40 ms keeps direction | 232, 255 | gesture.c:195-198, 205-214 | pass (U16) |
| Case PAIR: opposite pair within 40 ms, stamped at second edge; non-opposite ignored; no repeat; BTN_REC ignored | 233, 256 | gesture.c:176, 207-209, 215 | pass (m18b caught) |
| Centre key latch: roll or one side letting go does not end a long press; no direction while down | 255 | gesture.c:232-238 | pass (tests sw2_roll, pair_one_side; probe Q3 in `probe2-run.log`) |
| Highlight carries time of CENTRE_DOWN | 226, 245 | core.c:139-141 | pass (m14 caught) |
| Lock C4 and collisions C1 to C4 | 258, 279-282 | core.c:100-111, 133-146 | pass; C2 "open screens are discarded" is not a core action (U22) |

## 3. Owner's rule (bar item 3)

Entry into RECORDING. Only row 12 goes into RECORDING (`state_table.inc:15`; test_rules.c:37-49). Row 12 fires only from `RC_EV_LONG_PRESS`, which `rc_core_event` refuses (core.c:93-96) and which `dispatch_gestures` raises only from `RC_GEV_LONG` (core.c:133-135), emitted only by the 1,000 ms deadline (gesture.c:151-155). Directions go only to `screen_input` (core.c:120-126). Proof by run: m12 (long press injectable) is caught by `test_press_events_cannot_be_injected` and `test_no_system_event_starts_a_recording`; my own probe P1 shows a start needs the 1,000 ms mark (`probe-run.log`). Result: no path other than a centre long press in STANDBY enters RECORDING: pass. Caveat F6 (a hold begun in CHARGING that reaches 1,000 ms after VBUS removal starts a recording) and F2 (a start is not refused at B5 or full storage) are not breaks of the rule as worded.

Exit from RECORDING. The rows leaving RECORDING are exactly 21, 25, 27, 28, 30, 31, 32, 33 (test_rules.c:159-174, and my parse: all `from RECORDING` rows in `cmp_rows.log`). Of these only row 21 is user input (long press); 25 is case insertion (allowed by line 198); the others are battery, storage, fault or power loss. A short, double, direction, BLE highlight and menu power off do not stop one (test_rules.c:95-138; rows 22, 23, 24 stay in RECORDING; no row for MENU_POWER_OFF in RECORDING). Every row that leaves RECORDING except row 33 (power loss) closes or cuts VDD_MIC (rows 21, 25, 27, 28, 30, 32 CLOSE; 31 STOP_PDM, CLOCKS_LOW, MIC_OFF as the specification writes; test_rules.c:193-214). Result: pass. No S1.

## 4. Tests (bar item 4)

The delivered run: `base-host-run.log`, last line before exit `RESULT PASS tests=153`, `exit 0`.

- Row tests (test_rows.c:28-91) take the expected actions from the specification text, typed per row, and the timers from `SPEC_*` values typed in th.h:13-17, not from the module. Presses go through the real switch input. Good.
- Gesture tests use literal numbers (40, 450, 500, 1000, 400, 59, 60, 401, 30, 29, 39) and run both sources: good.
- Weak or passing-on-wrong-code, each shown by a surviving mutation or a crash (see section 5): F1 (row 3 guard never tested negatively, m29), F4 (m15, m25, m33), F7 (NULL dereference turns a failure into a crash).
- Row 13's variant test asserts the extra MT (test_rows.c:103) as part of the row; it follows the module's reading, not the row text (F5).
- Rows 4 to 5, 7 to 10 and 35 to 37 are tested only on the matching branch except 35 and 37 (m54 and m17 are caught); no test sends INIT_DONE at B5 or with VBUS and the open flag together (U6, U7 are readings without a test, as the notes say).

## 5. Mutations (bar item 5)

Each mutation: copy of the module in `mut/<id>/ring_core`, one perl edit of one line (`mut/<id>/change.diff`, line numbers are of the edited file, the file is named in `run_mut*.sh`), the delivered `run_host_tests.sh` with the copy as module, build in `mut/<id>/build`. Pattern of `broken/run_broken.sh`, writing only in my folder. Counts come from `mkmut.py` (output `mut-table.md`, last 4 lines).

| # | mutation | file:line changed | failing tests (first 3 of N) | caught | log |
|---|---|---|---|---|---|
| m01 | row 22 drops MH | diff `108d107` | 3: test_c1_short_in_recording_marks_highlight_not_status,test_c4_short_in_recording_screen_off_marks_and_shows_3s,test_row_22 | yes | mut/m01/host-run.log |
| m02 | row 21 swaps close and M2 | diff `103d102` | 1: test_row_21 | yes | mut/m02/host-run.log |
| m03 | row 25 drops charge on | diff `120d119` | 1: test_row_25 | yes | mut/m03/host-run.log |
| m04 | row 31 drops VDD_MIC off | diff `150d149` | 3: test_open_only_into_recording_and_every_exit_turns_mic_off,test_rail_follows_state_on_every_event_from_every_state,test_row_31 | yes | mut/m04/host-run.log |
| m05 | short ceiling 449 (off by one) | diff `78c78` | 2: test_pair_hold_450ms_short,test_sw2_hold_450ms_short | yes | mut/m05/host-run.log |
| m06 | double gap minimum 61 | diff `64c64` | 2: test_pair_gap_60ms_double,test_sw2_gap_60ms_double | yes | mut/m06/host-run.log |
| m07 | warning pulse at 501 ms | diff `109,110c109,110` | 6: test_mw_in_standby_and_recording_only,test_next_tick_follows_deadlines,test_pair_hold_500ms_ignored_warn | yes | mut/m07/host-run.log |
| m08 | release hold-off 29 ms | diff `113c113` | 2: test_next_tick_follows_deadlines,test_release_holdoff_29ms_bounce_same_press | yes | mut/m08/host-run.log |
| m09 | direction window 41 ms | diff `107c107` | 0:  | yes | mut/m09/host-run.log |
| m10 | repeat period 151 ms | diff `145c145` | 8: test_pair_dir_down_hold_repeat,test_pair_dir_left_hold_repeat,test_pair_dir_right_hold_repeat | yes | mut/m10/host-run.log |
| m11 | first repeat at 501 ms | diff `141c141` | 8: test_pair_dir_down_hold_repeat,test_pair_dir_left_hold_repeat,test_pair_dir_right_hold_repeat | yes | mut/m11/host-run.log |
| m12 | long press injectable through rc_core_event | diff `93c93` | 2: test_no_system_event_starts_a_recording,test_press_events_cannot_be_injected | yes | mut/m12/host-run.log |
| m13 | MW only in STANDBY | diff `129c129` | 1: test_mw_in_standby_and_recording_only | yes | mut/m13/host-run.log |
| m14 | highlight time = window close, not CENTRE_DOWN | diff `140c140` | 1: test_highlight_carries_centre_down_time | yes | mut/m14/host-run.log |
| m15 | B15 flag never cleared by VBUS | diff `60d59` | 0:  | NO | mut/m15/host-run.log |
| m16 | screen lock removed | diff `103c103` | 1: test_c4_lock_direction_and_short_only_wake | yes | mut/m16/host-run.log |
| m17 | guard AT_B5 excludes B5 | diff `99c99` | 1: test_row_37 | yes | mut/m17/host-run.log |
| m18 | PAIR: any other switch makes a centre press | diff `208c208` | 0:  | COMPILE-ERROR | mut/m18/host-run.log |
| m19 | roll or bounce does not hold the key down | diff `234d233` | 1: test_release_holdoff_29ms_bounce_same_press | yes | mut/m19/host-run.log |
| m20 | double press never recognised | diff `64c64` | 7: test_c3_centre_action_comes_after_window_and_double_is_dead,test_pair_gap_400ms_double,test_pair_gap_60ms_double | yes | mut/m20/host-run.log |
| m21 | hold released at exactly the mark is not long | diff `94c94` | 0:  | NO | mut/m21/host-run.log |
| m22 | state timers fire one ms late | diff `191c191` | 3: test_row53_open_flag_set_recovery_first,test_row_53,test_row_55 | yes | mut/m22/host-run.log |
| m23 | Vibration off also drops MW | diff `13c13` | 0:  | NO | mut/m23/host-run.log |
| m24 | short press fires at 400 not 401 | diff `114c114` | 13: test_c1_short_in_recording_marks_highlight_not_status,test_c4_lock_direction_and_short_only_wake,test_c4_short_in_recording_screen_off_marks_and_shows_3s | yes | mut/m24/host-run.log |
| m25 | S30 once never re-armed by a new recording | diff `64d63` | 0:  | NO | mut/m25/host-run.log |
| m26 | row 53 always runs recovery | diff `223,225c223` | 1: test_row_53 | yes | mut/m26/host-run.log |
| m27 | row 17 drops status screen | diff `90d89` | 1: test_row_17 | yes | mut/m27/host-run.log |
| m28 | graze limit 40 inclusive | diff `78c78` | 2: test_pair_hold_40ms_short,test_sw2_hold_40ms_short | yes | mut/m28/host-run.log |
| m29 | row 3 guard drops the battery test | diff `87c87` | 0:  | NO | mut/m29/host-run.log |
| m30 | row 12 drops M1 | diff `63d62` | 4: test_c2_long_press_with_screen_on_starts,test_c4_long_press_with_screen_off_starts,test_vibration_off_drops_mh_mt_only | yes | mut/m30/host-run.log |
| m31 | row 15 drops M2 | diff `79d78` | 1: test_row_15 | yes | mut/m31/host-run.log |
| m32 | long press may fire again (no once-per-press) | diff `152d151` | 23: test_c2_long_press_with_screen_on_starts,test_c4_long_press_with_screen_off_starts,test_vibration_off_drops_mh_mt_only | yes | mut/m32/host-run.log |
| m33 | timers injectable through rc_core_event | diff `94c94` | 0:  | NO | mut/m33/host-run.log |
| m34 | row 38 drops charge off | diff `169d168` | 1: test_row_38 | yes | mut/m34/host-run.log |
| m35 | row 29 drops the 30 min message | diff `141d140` | 1: test_row_29 | yes | mut/m35/host-run.log |
| m18b | PAIR: any other switch also makes a centre press | diff `208c208` | 1: test_pair_non_opposite_switch_ignored | yes | mut/m18b/host-run.log |
| m23b | Vibration off also drops M3 | diff `13c13` | 1: test_vibration_off_drops_mh_mt_only | yes | mut/m23b/host-run.log |
| m36 | marks after the release instant still fire during hold-off | diff `94c94` | 6: test_pair_hold_499ms_ignored_no_warn,test_pair_hold_999ms_ignored_warn,test_release_before_mark_in_holdoff_no_long | yes | mut/m36/host-run.log |
| m38 | mic rail not cleared on power loss into BOOT | diff `` | 0: - | NOT-APPLIED | mut/m38/host-run.log |
| m39 | row 5 swaps SD off and charge on | diff `33d32` | 1: test_row_05 | yes | mut/m39/host-run.log |
| m45 | long press at 999 ms | diff `111,112c111,112` | 20: test_c2_long_press_with_screen_on_starts,test_c4_long_press_with_screen_off_starts,test_next_tick_follows_deadlines | yes | mut/m45/host-run.log |
| m52 | after a sent direction other held switches are no longer ignored | diff `224c224` | 1: test_dir_sent_then_others_ignored_until_all_open | yes | mut/m52/host-run.log |
| m53 | up and down swapped on the screen | diff `122c122` | 2: test_screen_on_direction_goes_to_screen_with_mt,test_vibration_off_drops_mh_mt_only | yes | mut/m53/host-run.log |
| m54 | row 35 guard drops the battery test | diff `95c95` | 1: test_row_37 | yes | mut/m54/host-run.log |
| m38b | mic rail not cleared on power loss into BOOT | diff `46d45` | 1: test_rail_follows_state_on_every_event_from_every_state | yes | mut/m38b/host-run.log |
| m55 | second press no longer cancels the pending short press | diff `62c62` | 9: test_c3_centre_action_comes_after_window_and_double_is_dead,test_pair_gap_400ms_double,test_pair_gap_60ms_double | yes | mut/m55/host-run.log |

rows in tsv 46 applied and compiled 44 caught yes 38 survived NO 6
not applied/compile error: ['m18:COMPILE-ERROR', 'm38:NOT-APPLIED']
survivors: ['m15', 'm21', 'm23', 'm25', 'm29', 'm33']

Notes on the table:
- m18 did not compile (unused function under `-Werror`; invalid mutation, replaced by m18b). m38 did not apply (my pattern had one tab too many; replaced by m38b). Both kept, not counted.
- m09 is caught by a crash: the run ended with `Segmentation fault: 11` and no named test (`mut/m09/host-run.log`); cause: test code dereferences `tg_find(...)` which is NULL when the expected event is missing (finding F7; cause stated from reading test_gesture.c:50,77,92,128,148 and the 40 ms test, not separately run under a debugger).
- Survivors: m15, m25, m29, m33 are real test gaps (F1, F4). m21 and m23 I judge equivalent by reading only (unverified): m21, because `run_deadlines` runs every deadline at or before `t` before an edge is applied (gesture.c:247-249), so a mark equal to the release stamp has already fired; m23, because MW is pushed straight through `rc_actions_push` (core.c:130), not through the Vibration filter in state_actions.c:11-17.

## 6. Readings U1 to U23 (bar item 6)

Verdict words: A = agrees with the specification; S = the specification is silent or unclear, the reading is reasonable; C = contradicts.

| Id | Verdict | Why (spec line, code line) |
|---|---|---|
| U1 | S | The specification overlaps at 450 ms: 128, 212, 221 say short, 215 says "450 to 999 ignored". Code gesture.c:78 takes 450 as short; three lines against one and the [CHOICE] note support it. |
| U2 | A | Line 246: any press in the window cancels the earlier short and is judged alone; line 213 gives double only from 60 ms. gesture.c:64 does exactly that. Tested at 59. |
| U3 | S | 213 puts 400 inside; 212 says fires when the window closes; 245 says 400 ms after release. Code fires at release + 401 (gesture.c:114): 1 ms later than 245. Reasonable; keeps 400 inside the double. |
| U4 | S | "Once per discharge" is undefined; VBUS in starts a new discharge (core.c:60). Reasonable; untested (m15 survived). |
| U5 | S | "M3 once" for S30: once per recording (state_actions.c:64). Reasonable; untested (m25 survived). |
| U6 | A | Line 200 ("BOOT goes to RECOVERY"), row order 136 before 137; table first match. |
| U7 | S | No "init done" row for B5 or B2 without VBUS; the core stays in BOOT (probe P6, `probe-run.log`). Reasonable only if the caller always sends the battery event; see F2. |
| U8 | S | Rows 168 and 169 overlap; first match in order. Reasonable (P4 shows B2 gives row 37). |
| U9 | S, reading weak | Specification silent on a failed init at 60 s. Code: no retry ever (core.c:168-170,191-194; probe P2: still ERR_STORAGE_FAULT, next tick RC_NO_TICK at 130 s). Finding F3. |
| U10 | A | State is already SHIP after a ship command, so the guard cannot be false in FACTORY_TEST. |
| U11 | S | Row 163 omits SD off, while the state table (107) says storage off in ERR_STORAGE_FAULT. Code follows the row as written; the specification disagrees with itself. |
| U12 | S | Row 145 says "centre action of the screen", 301 says MT on "select". gesture MT is added in state_actions.c:69 and core.c:109. Reasonable; finding F5. |
| U13 | A | Hardware does it; only CHARGE_ON is a core action (state_actions.c:24). |
| U14 | S | "keep VDD_SD on" coded as SD_ON (state_actions.c:30); reasonable. |
| U15 | A | Confirmed by my parse and by test_rules.c:37-49, 159-174; m12 caught. |
| U16 | S | 232 says "0 to 40" and "40 or more"; 254 says "40 ms or more"; 256 says "within 40". Code treats 40 as a direction (gesture.c:107, deadline first). Reasonable. |
| U17 | S | "Holding 500 ms repeats every 150 ms" does not say from which instant; code counts from the press edge (gesture.c:141). Reasonable. |
| U18 | S | Line 232 "nothing else"; another direction in the window is ignored (gesture.c:215). Reasonable. |
| U19 | A | Line 246 literally says any press cancels; gesture.c:62-66. Untested, as the notes say. |
| U20 | S | Same-ms order unspecified; deadline first (gesture.c:247). Reasonable; a hold reaching 1,000 ms at the release ms is a long press. |
| U21 | S | Screen times are not row actions; left to the Screens part. Reasonable. |
| U22 | S | Line 280 discards open screens; not a core action. Reasonable, but nobody owns it in the core tests. |
| U23 | S | BLE highlight has no CENTRE_DOWN; the event time is used by the caller; `highlight_ms` stays -1 (core.c:139-141). Reasonable. |

Counts: A 6 (U2, U6, U10, U13, U15, U19), S 17, C 0. U9 is S with a weak reading (F3).

## 7. Findings

No S1 and no S2. All findings are S3. "Who acts" is given for the open ones.

- F1 (S3, test) Row 3's guard is never tested on its negative side: mutation m29 (`state_table.c:87`, drop `f->batt < RC_BATT_B5`) passes all 153 tests (`mut/m29/host-run.log`). Who: test builder.
- F2 (S3, specification gap, open) STANDBY can be reached with the battery at B5 or B2 or storage full, because rows 41, 53, 55 and 57 have no battery or storage guard and ERR_MIC_FAULT, ERR_CHARGER and TRANSFER have no B5 or SFULL row; row 12 has no guard, so a long press then starts a recording at B5 (section 1.1 line 116 says new recordings are refused) or on full storage (`probe2-run.log` Q1c and Q2b). The core follows the rows as written; it is not a break of the owner's rule. Who: specification owner, either to add guards to rows 41, 53, 55, 57 or a guard on row 12. If the lead counts a recording on full storage as at risk of loss, this becomes S1; I found no corruption path (a failed write goes to row 31 with the open flag left set).
- F3 (S3, open) A failed storage init at the 60 s mark leaves the ring in ERR_STORAGE_FAULT for good: `state_timer` stops after one try (`core.c:168-170`, `191-194`, probe P2). The caller also has to set `storage_init_ok` before the tick, so it cannot run the init after the timer fires. The specification does not say whether the 60 s repeats. Who: lead to decide, then builder.
- F4 (S3, tests) Surviving mutations m15 (B15 flag never cleared by VBUS), m25 (S30 flag never re-armed), m33 (timers injectable through `rc_core_event`, core.c:93-94): no test asserts them (`mut-table.md`). U4 and U5 readings are untested, as the notes admit; the timer refusal that the notes promise (note section 1, "cannot be given") is untested.
- F5 (S3, row text) Row 13, screen on: code gives SCREEN_CENTRE then MT (state_actions.c:68-69), row 145 lists no MT; test_rows.c:103 asserts the MT. Specification 301 supports it. Who: specification owner to write MT in the row or the builder to drop it.
- F6 (S3, behaviour) A centre hold that begins in CHARGING (where a long press is refused) fires a start if VBUS is removed before the 1,000 ms mark: `probe-run.log` P1a and P1b (STANDBY at 600 ms, RECORDING at 1000 ms). The gesture layer is state-blind (core.c:133-135). The rule is not broken (the user held a full second in STANDBY) but it is outside what G1 describes. Who: lead.
- F7 (S3, tests) `tg_find(...)->field` is dereferenced without a NULL check in test_gesture.c (lines 50, 51, 77, 92, 128, 148, 149 and others), so a missing event kills the whole run with `Segmentation fault: 11` and names no test (m09, `mut/m09/host-run.log`). Who: test builder.
- F8 (S3, interface) `facts.batt` is only raised by events (core.c:65-77) and nothing lowers it; after a charge the caller must write the fact itself, which `rc_core.h` and the notes do not say (`probe-run.log` P7c: `batt=1` after VBUS cycle). Who: builder, document it or reset on VBUS removal after a full charge.
- F9 (S3, specification reading) VBUS appearing in BOOT, RECOVERY, ERR_STORAGE_FAULT (ok, row 184) and others without a row gives no CHARGE_ON until a later row (probe P3: BOOT, VBUS_IN, no action). R-CHG (line 199) says the first VBUS event in BOOT turns the charger on; rows 1, 2 and 5 cover first power and init done. Who: specification owner.

## 8. Counts

- Rows: 61 of 61 equal the specification (one with note F5); `cmp_rows.log` `diffs 0`.
- Gesture items: 15 of 15 pass (section 2).
- Owner's rule: both halves pass.
- Readings: 6 agree, 17 silent with reasonable reading (one weak: U9), 0 contradict.
- Mutations: see the last lines of `mut-table.md` (reproduced in section 5): 44 applied, 38 caught, 6 survived (4 real test gaps, 2 judged equivalent by reading, unverified); 2 attempts invalid (compile error, not applied).
- Findings: S1 0, S2 0, S3 9.

## 9. What I could not check

- The Zephyr `native_sim` run (needs the server image): not run; I trust only the host run I made (`base-host-run.log`).
- Equivalence of m21 and m23: by reading only.
- The cause of the m09 crash: by reading the tests, not under a debugger.
- The lines of the specification outside sections 1, 2.1, 2.2, 3.1 (screens, storage, BLE): not in scope.
- `gen_table.py` itself: I checked its output against my own parser (`cmp_rows.log`), not its source.
- Whether the first 1.0 s guard works with a real debounce: hardware.

## 10. Files

`cmp_rows.py`, `cmp_rows.log`, `base-host-run.log`, `probe.c`, `probe-run.log`, `probe2.c`, `probe2-run.log`, `run_mut.sh`, `run_mut2.sh`, `run_mut3.sh`, `mut-results*.tsv`, `mkmut.py`, `mut-table.md`, `mkrows.py`, `rows-table.md`, `mut/<id>/` (copy, change.diff, host-run.log). Nothing outside this folder and `core-review-1.md` was written.

next: none, the review is complete; only a lead decision on F2, F3 and F6 is open.

RESULT: done, 0 S1, 0 S2 and 9 S3 open; 38 of 44 mutations caught (4 real test gaps survived, 2 judged equivalent), 61 of 61 rows equal the specification.
