# factory notes: unit U8 of software step 6 (FACTORY sub-commands and the ship beacon)

Builder: U8 helper. Started 2026-11-13 06:47 CET (`date`). Version read: commit ca9526de of the project plus the working tree (other builders' ring_xfer and ring_screens work in progress). No git was run. Contract: `firmware/docs/step6-plan.md` (read in full, rulings included), `firmware/docs/rhw-notes.md` sections 2 and 3, the frozen headers `rfa.h`, `rrec_spec.h`, `rhw.h`, `rhw_sim.h`, `rrec.h`, and the public headers and notes of units U2, U3, U5, U6, U7. "FW l.N" = line N of `design/firmware.md`. Raw evidence: `firmware/build-logs/step6/u8-*` (checklist `u8-CHECKLIST.md`).

Cited unit run: `bash tools/unit_run.sh tests/factory` through `u8-run-cmd.sh full1`, exit 0 (`u8-full1.exit` holds 0). `u8-full1.console`: line 23 (`native_sim`) and line 46 (simulated chip) `41 of 41 executed test cases passed` (20 cases of scenario `ring_factory.sim` and 21 of `ring_factory.screen`), line 1462 `RESULT PASS` (broken copies), line 1464 `UNIT PASS tests/factory`.
Per-case PASS lines (twister prints them only for failing runs, so one read-only call listed the handler logs of that run): `u8-cases.console` (command `u8-cases.exit` 0); the table below cites its lines, `u8-case-lines.txt` is the generated index. "N / B" = line in the `ring_factory.sim` section of the `native_sim` handler log / of the simulated chip's; `test_frames_reach_display` is in the `ring_factory.screen` section (native_sim line 52, chip line 165).
Two-device test: `u8-bsim-final.console` (line 52 `RESULT PASS`, exit file 0) and `u8-bsim-broken-final.console` (line 119 `RESULT PASS`, exit file 0).

## 1. Files (under `firmware/`)

| Path | What |
|---|---|
| `modules/ring_factory/src/rfa_logic.h`, `rfa_logic.c` | pure part, no kernel call: gate and parse, flag rules, response layouts, RMS in tenths of dBFS (fixed-point log2), longest run of equal samples, ppm, T-CHARGE verdict, T-MOTOR read delay and dip, beacon name |
| `src/rfa.c` | thin part: each test, the joystick event window, the beacon (through `rhw_beacon()`), built-in T-STORE through `rst.h` when the join gives none |
| `src/rfa_hw_real.c` | the real beacon (Bluetooth host, not connectable); registered with ring_rhw; compiled only with the simulated drivers off and `CONFIG_BT` on |
| `CMakeLists.txt`, `Kconfig`, `zephyr/module.yml` | the module (`RING_FACTORY_LOGIC`, `RING_FACTORY`, `RING_FACTORY_REAL`; `RING_FACTORY` implies `RING_STORE`) |
| `tests/factory/` | 11 suites (`src/test_*.c`), `src/common.[ch]` (the join's stand-ins), `app.overlay`, `screen*.overlay`, `screen.conf`, `testcase.yaml` (two scenarios), `broken_edit.py`, `broken_run.sh`, `kfacts.sh` |
| `tests/bsim/factory/` | `run.sh`, `broken_edit.py`, `ring_app/` (real factory part and real beacon on the simulated chip), `host_app/` (the scanner) |

## 2. Readings (mine; each open for the lead)

1. **Request bytes** (FW 9.3 names sub-commands, not bytes): one byte for every sub-command except T-MIC (`0x10`, microphone 1 or 2) and T-JOY, T-CENTRE (`0x30`, `0x31`, window in ms as u16, 1 to 10,000). A wrong length or argument answers BAD_ARG.
2. **Order of answers**: empty request BAD_ARG; flag clear NOT_ALLOWED for every sub-command (also an unknown one); then BAD_ARG (0x11, unknown, bad length); then the state. ENTER only when the core is not in FACTORY_TEST (answered in TRANSFER); every other sub-command only in FACTORY_TEST; else NOT_ALLOWED. ENTER inside FACTORY_TEST is NOT_ALLOWED.
3. **Response layouts** (little endian; `rfa_logic.h`): T-MIC 13 bytes (result, RMS left and right in tenths of dBFS i16, longest run left and right u32); T-SIGN 33 (four i64 uptime ms: on, off, on, off); T-MOTOR 7 (VBAT before, during u16 mV, dip i16); T-STORE 14 (equal, write us, read us, deleted); T-CHARGE 7 (state, latched reason, current uA i32); T-XTAL 17 (ppm x10 i32, GRTC ticks u64, frames u32); T-JOY and T-CENTRE: result, dropped, count, then count x (event, ms since the request began u32), at most 32 events; the others 1 byte.
4. **Verdicts the ring gives**: T-MIC fails on a run of 1,000 equal samples (FW l.1024) or when no recording was made (no sign, no test, R18); the 3 dB rule and the tapping check are the jig's. T-XTAL passes within 50 ppm. T-CHARGE fails when the state is off or an error is latched. T-JOY and T-CENTRE answer timeout (2) when no event came in the window. T-STORE fails on unequal data or any error.
5. **Numbers not in `rrec_spec.h`** (defined in `rfa_logic.h` with their line): 1 s per screen frame, the grid held 1 s (FW l.1025); 50 ppm (FW l.1033); the 32.768 kHz and the 1 ms start-of-frame (assumed full speed). The lead may move them.
6. **Beacon name** upper case: "Ring" + last 4 hex digits (case is not stated in FW l.1057).
7. **SHIP_ENTER order**: the beacon starts first, then the flag is cleared; if either fails nothing changes, the answer is result fail with no effect (the ring stays in FACTORY_TEST with the flag as it was).
8. **T-RADIO** uses the same name and advertises 10 s, then stops.
9. **T-STORE built-in** (when `ops.store_test` is NULL): mounts only if not mounted and unmounts only what it mounted; runs `rst_factory_area_test`, then `rst_delete_factory_recordings`. The LBA 4,096 lives in `rrec_spec.h` and is read by ring_store, so broken copy `store_lba_4097` edits a copy of ring_rhw.

## 3. Rows of the plan mapped to cases and log lines

Lines: `u8-cases.console`, "N / B" as defined above (both pass lines are `PASS`).

| Row | Case | N / B | What it shows |
|---|---|---|---|
| C20 (factory half) and X17 (factory half) | `factory_cmd.test_flag_rules` | 94 / 207 | flag clear: all 11 plain sub-commands, T-MIC, T-JOY, T-CENTRE answer NOT_ALLOWED (11) in TRANSFER and in FACTORY_TEST with no side effect; EXIT gives the reboot effect; SHIP_ENTER clears the flag (settings read back), SHIP_SAMPLE keeps it and ENTER works after a reboot; outside FACTORY_TEST the ship commands start no beacon. The core rows themselves (`recorder_rows.test_factory_rows`) and the xfer case (`xfer_proto.test_factory_not_allowed`) are not this unit's |
| T11 | `factory_cmd.test_flag_rules` | 94 / 207 | as above; `sys_persist.test_factory_flag_survives_reboot` is U7's |
| T12 | `factory_cmd.test_result_layout` | 95 / 208 | codes 0, 1, 2 and the byte layouts typed by hand (T-MIC, T-SIGN, T-STORE, events, and T-CHARGE, T-MOTOR, T-XTAL through the request) |
| T13 | `factory_mic.test_rms_and_runs` | 101 / 214 | sine of peak -20 dBFS reads -230 (+-2), -10 reads -130; runs of 999 and 1,000 and across blocks; stuck right channel gives fail and a run equal to every kept frame |
| T13 | `factory_mic.test_type_2_recording` | 102 / 215 | store holds one recording of type 2, 31,200 kept frames (+-256), chunk header byte 22 = 2, one input start, VDD_MIC on once by caller `rec_mics_on`, after the sign |
| T13 | `factory_mic.test_no_screen_no_mic` | 100 / 213 | sign refused: result fail, VDD_MIC never on, input never started, no block read; T-SIGN the same |
| T14 | `factory_screen.test_frame_sequence` (stand-in call) | 108 / 221 | six frames 0 to 5, 1,000 ms apart; a refused frame ends the test with fail |
| T14 | `factory_screen.test_frames_reach_display` (real screens part, scenario `ring_factory.screen`) | 52 / 165 | the real core in FACTORY_TEST, `rscr_factory_frame` through the ops, the display's frame read back: 28,800 pixels each of red, green, blue, white, black; the grid has lit and dark pixels and a lit first row and column. The camera: not provable |
| T15 | `factory_input.test_directions_reported` | 98 / 211 | four directions and centre down and up reported with times (+-5 ms), single press not part of T-JOY, events outside a run not kept, 40 events keep 32 and count 8 dropped, no recording |
| T15 | `factory_input.test_centre_reported_never_records` | 97 / 210 | real gesture recogniser fed edges: one single, one double, one long, MW at 500 ms of the hold, long at 1,000 ms; the real core in FACTORY_TEST fed the same edges asks for no open, close, M1 or M2; no test recording, no rail, no microphone, no card write, no sign |
| T16 | `factory_motor.test_reads_and_timing` | 104 / 217 | two VBAT samples, the first before MOTOR high, the second 250 ms (+-2) into the pulse, MOTOR on 500 ms (+-2), values 3,900, 3,870, dip 30. The dip and the accelerometer: not provable |
| T17 | `factory_sign.test_two_recordings_times` | 114 / 227 | two type-2 recordings; the four reported times equal the rail events of the simulated chip (+-1 ms); each 1,000 to 1,250 ms, 1,000 to 1,100 ms apart. The camera: not provable |
| T18 | `factory_store.test_area_write_read` | 116 / 229 | one write and one read of 65 sectors at LBA 4,096, VDD_SD on first, write time shows a 20 ms stall, read error gives fail, mount state left as found |
| T18 | `factory_store.test_test_recordings_deleted` | 117 / 230 | one type-1 and two type-2 recordings: two deleted, the type-1 stays. Speeds: not provable |
| T19 | `factory_radio.test_adv_parameters` | 106 / 219 | one start with 100 ms, 0 dBm, not connectable, name RingCDEF; one stop 10 s (+-20 ms) later. Received power: not provable here; scanner: section 5 |
| T20 | `factory_charge.test_fail_when_off_or_error` | 90 / 203 | states 1 to 4 pass with the current reported; off fails; a latched error fails even with a fine state |
| T21 | `factory_xtal.test_ppm_arithmetic` | 119 / 232 | 327,696 ticks over 10,000 frames = 488 tenths (pass), 327,697 = 518 (fail), -488 pass, limit edges 500 and 501, no frame counted fails. The measurement: not provable |
| T22 | `factory_ship.test_beacon_window` (SHIP_ENTER), `test_beacon_window_sample` (SHIP_SAMPLE) | 111, 112 / 224, 225 | the real `rpw_ship` on the simulated chip with `rfa_beacon_stop` as before_task: start before the wait and before VBUS removal, stop after the removal and before the ship task (within 1 s), one stop, no start for the next 60 s |
| T22 | `factory_ship.test_beacon_name` | 110 / 223 | name RingCDEF, Ring0A0F for another id, 100 ms, 0 dBm, not connectable, second stop does nothing |
| T23 | `factory_cmd.test_0x11_bad_arg` | 92 / 205 | 0x11 (with and without bytes), every unknown sub-command and an empty request: BAD_ARG, nothing runs |
| (extra) | `factory_cmd.test_bad_arguments` | 93 / 206 | bad microphone, window and lengths; the 10,000 ms window is accepted |

## 4. Broken copies (plan list of U8): each fails its named case on both targets

Edit check (each matches exactly once): `u8-editcheck2.log` (an earlier check, `u8-editcheck.log`, was made before the beacon file and the `imply` change; the edits are the same). Lines of `u8-full1.console`: "named case failed" line native_sim / chip, then the cases that failed.

| Copy | Named case | Lines (native_sim / chip) | Other cases that failed with it (both targets) |
|---|---|---|---|
| `flag_ignored` | `factory_cmd.test_flag_rules` | 129 / 192 | none |
| `x11_accepted` | `factory_cmd.test_0x11_bad_arg` | 267 / 330 | none |
| `run_999` | `factory_mic.test_rms_and_runs` | 406 / 469 | none |
| `mic_without_sign` | `factory_mic.test_no_screen_no_mic` | 545 / 608 | `factory_mic.test_type_2_recording` (the extra rail-on call has another caller and a second rail event) |
| `centre_records` | `factory_input.test_centre_reported_never_records` | 690 / 753 | none |
| `vbat_read_at_0` | `factory_motor.test_reads_and_timing` | 829 / 892 | `factory_cmd.test_result_layout` (its T-MOTOR bytes: the read at 0 ms changes the "during" value, assertion at `test_cmd.c:230`), `factory_screen.test_frame_sequence` (spacing not 1,000 ms, `test_screen.c:202`; the cause is NOT established: it follows the aborted motor case in the same image, I did not check why) |
| `store_lba_4097` (edit of a copy of ring_rhw) | `factory_store.test_area_write_read` | 968 / 1031 | none |
| `type2_left` | `factory_store.test_test_recordings_deleted` | 1107 / 1170 | none |
| `beacon_connectable` | `factory_ship.test_beacon_name` | 1246 / 1309 | none |
| `beacon_after_ship` | `factory_ship.test_beacon_window` | 1397 / 1460 | `factory_radio.test_adv_parameters` (it stops the beacon through the delayed stop), `factory_ship.test_beacon_name`, `factory_ship.test_beacon_window_sample` |

The twister line "failed cases listed" counts both scenarios (each case runs in `ring_factory.sim` and `ring_factory.screen`), so it is twice the number of distinct cases.

## 5. Two-device test `tests/bsim/factory/run.sh` (decision D6 b)

The ring (real `rfa.c` and real `rfa_hw_real.c`, simulated drivers off) at 2 s takes SHIP_ENTER, at 8 s "VBUS removed" (`rfa_beacon_stop`), at 70 s T-RADIO; a stand-in scanner (passive, continuous) checks 14 things with numbers typed from FW l.1031, l.1034, l.1035, l.1057. `u8-bsim-final.console`: ring checks 7, scanner checks 14, line 34 `HOST REPORTS 150`, line 43 `HOST MEDIAN GAP 106 ms of 56`, line 50 names equal (`Ring0000` both), line 51 `TEST RESULT PASS (21 checks passed)`, line 52 `RESULT PASS`. `--broken` (`u8-bsim-broken-final.console`): `connectable` fails `every report is not connectable` (line 65), `never_stops` fails `stopped within 1 s of VBUS removal` (line 118), line 119 `RESULT PASS`. Earlier looks: `u8-bsim1` (name comparison read the wrong prefix: fixed), `u8-bsim2`, `u8-bsim-broken1` (the named-check pattern had two spaces: `never_stops` was caught but not counted: fixed), `u8-bsim-broken2`.
Not shown by this test: the 0 dBm power (the simulated radio carries no power figure) and any property of a real radio. The device id on the simulated chip is 0, so the name is `Ring0000`; the derivation from an id is proven in `factory_ship.test_beacon_name`.

## 6. Kit fact K13 (counts and file names only; `u8-k13.console`)

- Not-connectable advertising with a set interval: `bt_le_adv_start` and `bt_le_adv_stop` exist (counts 6 and 1 in the host headers); `BT_LE_ADV_OPT_CONN` exists (9), so leaving it out gives a not-connectable advertiser; `BT_GAP_ADV_TYPE_ADV_NONCONN_IND` exists (1). The scanner of section 5 heard only that type. TRUE, and proven on the simulated chip.
- 0 dBm: the controller Kconfig `BT_CTLR_TX_PWR_0` exists (1 file); the vendor command `BT_HCI_OP_VS_WRITE_TX_POWER` exists (1). The real file does not set power: it accepts only 0 and relies on the controller setting. The product must carry `CONFIG_BT_CTLR_TX_PWR_0=y` (join, stage `link-settings`). Unproven (no radio power in the simulation).
- A second advertising set: NOT needed. The devices part uses one legacy advertiser (`rdev.c`: `bt_le_adv_start` 1, `bt_le_ext_adv` 0) and does not advertise in `FACTORY_TEST` (FW l.765: "none (the radio test of section 9.3 advertises on its own)"). If it still advertised, `bt_le_adv_start` would answer -EALREADY and the factory request would fail; the extended advertising API (`bt_le_ext_adv_create` 3, `BT_EXT_ADV` declared) would then be the way, with a new Bluetooth setting.
- Device id for the name: `hwinfo_get_device_id` exists (2); the product needs `CONFIG_HWINFO=y`. On the simulated chip it returns 0.

## 7. What the join must call or supply (and the five gaps)

Calls: `rfa_init(&ops)` once at boot after the other units; the transfer backend's `factory` hook calls `rfa_request(req, len, core_state == FACTORY_TEST, out, &n, &eff)` and maps the effect to the core events (ENTER to `RC_EV_FACTORY_ENTER`, EXIT to `RC_EV_FACTORY_EXIT`, SHIP_ENTER to `RC_EV_SHIP_ENTER`, SHIP_SAMPLE to `RC_EV_SHIP_SAMPLE`); `rpw_ship(rfa_beacon_stop)` for the ship action; `rfa_input()` for each joystick event in FACTORY_TEST; `rpw_state(RC_ST_RECORDING)` while a test recording runs (power notes reading 1, ruling 8). Ops: `flag` and `flag_set` = `rsy_factory_flag`, `rsy_factory_flag_set`; `screen_frame(which)` = `rscr_factory_frame(which + 1)`; `store_test` = NULL (built-in); the rest below. Settings: `CONFIG_BT_CTLR_TX_PWR_0=y`, `CONFIG_HWINFO=y`.

| Gap | How I built round it | What the join does |
|---|---|---|
| 1. `rau.h` has no tap on kept frames for T-MIC | the ops contract (`test_recording` with `on_block`) puts it with the join; the stand-in in `tests/factory/src/common.c` wraps `rau_cb.put`: it passes each chunk's payload to `on_block` in blocks of 256 frames, then calls `rst_put_chunk`, and also passes the partial chunk from `rau_cut` | wrap `rau_cb.put` the same way, tap `cut.last`, run the normal path with type `RREC_REC_TYPE_FACTORY` through `rec_mics_on()`, answer -ENODEV when the sign is refused |
| 2. `rmo.h` has no 500 ms pattern for T-MOTOR (M1 to MF are 80 to 800 ms with gaps) | `ops.motor_on(ms)`; the stand-in sets `rhw_motor()->set(true)`, sleeps, sets false; `rfa.c` calls it from a private work queue so VBAT can be read 250 ms into it | `rmo_stop()` then drive the pin for 500 ms, or ask U6 for a pattern (lead's call) |
| 3. `rpw.h` has no "sample now" and no call for the latched charger error and the battery current | `ops.vbat_mv` and `ops.charge`; the stand-ins read `rhw_pmic()` directly | `rhw.h` says one owner per kind (the power thread), so reading from the transfer thread can race the power thread: add the two calls to ring_power, or hold a lock |
| 4. `rhw.h` has no USB start-of-frame count | `ops.xtal_counts` returns -ENOTSUP in the simulation and the test answers fail; the arithmetic is proven | count start-of-frame from the USB stack over `RREC_FAC_XTAL_MS` and the GRTC beside it |
| 5. The core gives no raw gesture events in FACTORY_TEST (its table has no centre rows; `rc_core_input` returns actions only) | the test feeds the same edges to a real `rc_gesture` and maps `rc_gev` to `rfa_input` (the mapping is in `test_input.c`) | run a second `rc_gesture` on the same edges, or have the glue expose the gesture events (the glue is the join's) |

## 8. Not provable without hardware (this unit)

Every real driver call (`rfa_hw_real.c` ran only on the simulated chip, not compiled for the development kit); the radio power and the RSSI; the microphone levels, the speaker, the channel map and tapping; the screen camera and dead rows; the accelerometer and the real dip; the card's speeds; the charger's real state and current; the crystal's accuracy and the start-of-frame count; the factory flow by assembly step (the jig is not built).

## 9. Runs and looks (every look at results)

`u8-short1.console` (first build: three of 40 cases failed: my test data for the 999-run, my expectation of the chunk's sector (first chunk is sequence 1), and a second ship command after the flag was cleared; test fixes), `u8-short2.console` (one case failed, `test_centre_reported_never_records`: my test passed an uninitialised action list to the core, fixed with `rc_actions_clear`), `u8-short3` to `u8-short6` (green; `short5` showed the 1 s spacing assertion too strict in the real-screens case), `u8-k13.console`, `u8-bsim1/2`, `u8-bsim-broken1/2`, `u8-bsim-final`, `u8-bsim-broken-final`, `u8-editcheck.log`, `u8-editcheck2.log` (the folders `u8-editcopy`, `u8-editcopy2` hold the edited copies), `u8-full1.console` (cited), `u8-cases.console`, `u8-searches.log` (source searches: no chip pin, no kernel call in the pure part, no hardware name in `rfa.c`, no other company's name in a string, no microphone rail name in the unit's sources, no start/stop names; address and key search), `u8-audit.log` (claim audit, below).

## 10. Cleanup

My server copy `/root/ring-os/src-u-factory` and the run folders under `/ws/out` named `*u8-*` were made by my commands and are left for the lead. No process of mine runs. Nothing was written outside my own files and the output folder.

## 11. Audit

`u8-audit.py` took every number and every cited line of this file and checked it against the saved logs; its output is `u8-audit.log` (count and any mismatch are printed there).

questions_for_owner: none

RESULT: done, `UNIT PASS tests/factory` (u8-full1.console line 1464) on both simulated targets with all 10 broken copies failing their named cases and the two-device beacon test passing with both of its broken copies caught; the real beacon file is proven on the simulated chip only and five gaps for the join are listed in section 7.
