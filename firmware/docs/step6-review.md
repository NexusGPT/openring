# Review of software step 6 (recorder parts), commit af085a68

Reviewer: an independent judge (I wrote none of the code, tests or notes of step 6). Started 2026-11-13 11:45:04 CET, `date`.
Independence: the brief holds no verdict of the authors.
I ran no build, no test, no server command and no git write. I read the code and tests and ran small read-only greps and
Python scripts on the Mac. My raw outputs are in `firmware/build-logs/step6/review-work/` (called W/ below). "F/" is `firmware/`.
"FW l.N" is line N of `design/firmware.md`.

Pin. At the start HEAD was af085a68 and no file under `firmware/` was changed (W/git-status-firmware.txt: only 42 untracked
logs under `build-logs/`). At 12:18 HEAD had moved to 7f9fd031 with four commits outside the firmware; `git diff --name-only
af085a68 HEAD` over `firmware/modules`, `firmware/tests`, `firmware/app`, `firmware/docs` and `design/firmware.md` lists 0 files
(W/pin-diff-code.txt, W/pin-log.txt). So what I read is af085a68.

## Verdict

**FAIL** on bar B1: 6 rule rows owned by the join are not implemented as the specification says or have no case that can fail
(findings R6-01 to R6-06, all major). No blocker: every safety rule of B2 holds in the code. B3 and B4 pass; B5 lists 5 seams.

Counts: 0 blocker, 6 major, 8 minor, 3 notes.

## Findings

| Id | Severity | File and line | Spec line | What is wrong | Evidence |
|---|---|---|---|---|---|
| R6-01 | major | F/modules/ring_recorder/src/rrec.c:268 | FW l.151 | Menu "Power off": the row's M2 is never felt. The core gives SAVE_SETTINGS_TIME, M2, SHIP_MODE in that order (F/modules/ring_core/src/state_actions.c:93 to 96); `play(M2)` starts the pattern and the next action, `ship_mode()`, calls `rmo_stop()` first, which sets the pin low at once (F/modules/ring_motor/src/rmo.c:184 to 196). No test checks M2 in row 19: `test_ship_closes_everything_first` checks only the save before SHPHLDCONFIG (F/tests/recorder/src/test_actions.c:280 to 289). | `rmo_stop();                              /* no motor while the chip is cut */` (rrec.c:268); `case 19: /* line 151: save settings and time; M2; ship mode */` (F/modules/ring_core/src/state_actions.c:93) |
| R6-02 | major | F/modules/ring_recorder/src/rrec.c:266 to 281 | FW l.937, l.939 | Ship entry step 1 closes "recording, storage, USB, radio, screen"; `ship_mode()` closes storage and the join's USB crystal only. No call for the screen, the radio or the USB stack is in the ship path (W/ship-close-search.txt: "grep exit 1 (1 = no hit)"). The screens learn of the new state only at the end of `rrec_glue_after`, `return rscr_glue_after(a, last_event, state, t);` (rrec.c:525), after `rpw_ship` returns, so during the VBUS wait of SHIP_ENTER and SHIP_SAMPLE ("the ring does nothing else: no screen, no radio", l.939) the screen keeps its picture. The ship beacon of R20 is the allowed radio. The test checks VDD_MIC and VDD_SD only (test_actions.c:277). | `zassert_true(i_mic >= 0 && i_sd > i_mic && i_cfg > i_sd, "VDD_MIC off, VDD_SD off, then SHPHLDCONFIG");` (test_actions.c:277) |
| R6-03 | major | F/modules/ring_recorder/src/rrec.c:330 and :412 | FW l.179, l.178, l.912 to l.920 | VBUS removed in TRANSFER while a command reads the card: `rxf_abort()` does not wait (F/modules/ring_xfer/include/ring_xfer/rxf.h:80 to 82, rxf_class.c:318 to 324); `rst_unmount()` returns -EBUSY at once while another store call runs (rst.h:8 to 11; `op_take` is `k_mutex_lock(&op_lock, K_NO_WAIT)`, rst.c:169 to 172, used at the start of `rst_unmount`, rst.c:467); the join drops the result (`(void)rst_unmount();`) and retries only at the next core step. VDD_SD can stay on in STANDBY. Same for row l.178 when `rxf_finish(5000)` times out (rrec.c:37, :380). The test removes VBUS with no command running, so neither "abort" nor "finish" is exercised (F/tests/recorder/src/test_rows.c:179 to 187). From reading; not run. | `return k_mutex_lock(&op_lock, K_NO_WAIT) == 0;` (rst.c:171); `void rxf_abort(void);` "does not wait" (rxf.h:80 to 82) |
| R6-04 | major | F/modules/ring_recorder/src/rrec.c:406 to 431 | FW l.915 | HFXO is "on" in BOOT and RECOVERY (FW 8.2 table). The join requests it only in CHARGING, TRANSFER and FACTORY_TEST and skips BOOT; RECOVERY gets none. With VBUS at boot the USB stack is enabled on VBUS ready (rrec_boot.c:70) and the self-test waits for USB to enumerate (FW l.1014) with no crystal held by anyone (recorder-notes section 2 item 5: "the transfer part does not request it itself"). The plan's row P6 (step6-plan.md l.189) leaves BOOT and RECOVERY out and the test says so (F/tests/recorder/src/test_rails.c:6, 7, 16). Against the plan as well: the lead rules whether l.915 holds, then J. | `bool usb = s == RC_ST_CHARGING \|\| s == RC_ST_TRANSFER \|\| s == RC_ST_FACTORY_TEST;` (rrec.c:406); W/b2-mic-and-misc.txt (FW l.915 row) |
| R6-05 | major | F/tests/recorder/src/test_actions.c:48 to 62 | FW l.125 (C4) | `test_close_order` cannot fail for "write the partial chunk". It takes the first chunk-area write after the log clear (l.53), but the stop press is held 1,100 ms (F/tests/recorder/src/rt.c:303 to 310) and a full chunk is written every 512 ms (FW l.443), so that write is a full chunk. A close that drops the partial chunk (`rst_close(NULL, ...)` at rrec.c:232) passes. No other recorder case looks at the frames of a closed recording (W/grep-partial-chunk-tests.txt). From reading; not run. | `i_part = find_write(RREC_LBA_CHUNK_FIRST, UINT32_MAX, 0);` (l.53); `rt_sleep(1100);` (F/tests/recorder/src/rt.c:306) |
| R6-06 | major | F/modules/ring_recorder/src/rrec.c:569 to 637 | FW l.1024, l.1029 (T13, T17) | The join's half of T-MIC and T-SIGN is not tested on the real join. The factory suites run a stand-in test recording that switches VDD_MIC itself (F/tests/factory/src/common.c:50 to 92, `rail_set(RHW_RAIL_MIC, true, "rec_mics_on")` at l.92). The real `rrec_test_recording` (type 2, the 2 s length, the VDD_MIC on and off times of T-SIGN) is reached only by `recorder_rows` row 49 (VDD_MIC rule only, F/tests/recorder/src/test_rows.c:40 to 53) and by `recorder_rules` (no recording, no times, F/tests/recorder/src/test_rules.c:109 to 141). recorder-notes section 9 maps no case to T13 or T17. | `rc = rhw_pmic()->rail_set(RHW_RAIL_MIC, true, "rec_mics_on");` (tests/factory/src/common.c:92) |
| R6-07 | minor | F/tests/recorder/src/test_actions.c:173 | FW l.161 (C13) | No product code sends `RC_EV_BLE_HIGHLIGHT`; the case injects it with `rglue_event`. recorder-notes row C13 does not say so. FW 7 is outside step 6 (plan row T2), so the Bluetooth source is not built. | W/grep-ble-highlight.txt (hits only in rc_types.h, core tests, recorder tests) |
| R6-08 | minor | F/modules/ring_recorder/src/rrec_bridge.c:46 to 49 | FW l.164 to l.169, l.179 | A job that does not fit the 32-entry queue (rrec_bridge.c:33) is dropped and only counted as done: a lost VBUS_OUT, CHUNK_WRITE_FAILED or MIC_NO_BLOCK reaches no row and leaves no event log record. | `(void)atomic_inc(&done);   /* not queued: counted as done so a waiting test does not hang */` (l.48) |
| R6-09 | minor | F/modules/ring_recorder/src/rrec_bridge.c:102 to 110 | FW l.192 | `run_retry` reads `mi.open_flag` of an uninitialised `mi` when the card was already mounted (`r = rst_mounted() ? 0 : rst_mount(...)`). | `struct rst_mount_info mi;` (l.102), `rrec_st.fact_open = mi.open_flag;` (l.108) |
| R6-10 | minor | F/modules/ring_screens/src/rscr.c:534 | rpw.h:74, 75 | Seam: menu "Power off" runs the glue's step on the screens thread (`ops->power_off()` -> `rglue_event_try`, rscr_real.c:94), so `rpw_ship` blocks the screens thread, while rpw.h names "Join's thread" for it. On the simulated chip the ship returns after its 1 s retry (power_ship.test_retry_once_after_1s: "two tries of 1 s each"). | `if (atomic_get(&power_off_pending) != 0 && ops->power_off() == 0) {` (rscr.c:534) |
| R6-11 | minor | design/firmware.md l.218, l.1065 | FW l.218, l.1065 | Against the specification: the watchdog is "fed every 1 s by the main loop" and "resets the chip when the main loop stops", but the product has no main loop (F/app/src/main.c:125 to 127 sleeps); ring_sys feeds from a work item (F/modules/ring_sys/src/rsy.c:461). The specification does not say which thread's stall must cause the reset. The code holds ruling 9 and the 2 s progress rule. | `static void wdt_tick(struct k_work *w)` (rsy.c:461) |
| R6-12 | minor | F/docs/xfer-notes.md (K3 lines) | - | The K3 evidence the transfer notes cite (`20261113-063327-u4-k3c.log`, `-055850-u4-k34.log`, `-062437-u4-k3b.log`) is not in commit af085a68 (untracked on disk). The line I checked exists on disk. | W/cited-files-tracked.txt: `NOT IN COMMIT firmware/build-logs/step6/20261113-063327-u4-k3c.log` |
| R6-13 | minor | F/tests/factory/src/test_screen.c:202 | FW l.1025 | `factory_screen.test_frame_sequence` demands exactly 1,000 ms between `rhw_clock()->now_ms()` stamps (F/tests/factory/src/common.c:132; the simulated clock is `k_uptime_get()`, F/modules/ring_rhw/src/sim_misc.c:131 to 134), at 10,000 ticks per second on native_sim. See "The three findings reported by the units" below. | `zassert_equal(fx_frame_ms[i] - fx_frame_ms[i - 1], 1000, "1 s each (FW l.1025)");` |
| R6-14 | minor | F/tests/recorder/src/test_screens.c:38 to 46 | FW l.374 (C39) | The case checks only that two gauge values give two different pictures, not the percent, "Charging" or "Full", or the time to full. | `zassert_not_equal(a1, b1, "another gauge value, another picture: the value reaches the screen");` |
| R6-15 | note | F/modules/ring_audio/src/rau.c:313 to 320, 336 | - | Finding F1 of the units: simulation only (judged below). | j-prod1.log l.17, 18 |
| R6-16 | note | rau.c:313, :48; F/modules/ring_motor/src/rmo.c:95 | - | Finding F2 of the units: warnings only (judged below). | j-prod1.log l.17 to 19 |
| R6-17 | note | F/modules/ring_recorder/src/rrec_int.h:72 | - | `test_recording` is a plain `bool` written on the transfer thread and read on others; the comment says "atomic flag". | `bool test_recording;     /* a factory test recording runs (transfer thread; atomic flag) */` |

## Bar B2: the safety rules, in the code

| Rule | Verdict | Evidence |
|---|---|---|
| Only a long press starts or stops (FW l.209) | pass | No unit names `rglue_input`, `rc_core_input` or `RC_EV_LONG_PRESS` outside the glue and the core (W/grep-start-paths.txt; the only other `rglue_event_try` is the menu's power off, rscr_real.c:94). Every event the join posts is in W/grep-posts.txt: none is a press. `rc_core_event` refuses press events (F/modules/ring_core/src/core.c:177 to 181). A factory test recording is type 2 and only in FACTORY_TEST (rrec.c:577 to 582). |
| VDD_MIC on in one place, only after the sign answered 0 | pass | The only `rail_set(RHW_RAIL_MIC, true` in modules and app is rrec_mics.c:53, after `sign_draw(t)` returned 0 (rrec_mics.c:48 to 52) (W/b2-mic-and-misc.txt). |
| Close order: microphones off before the screen leaves the sign; storage rail off last | pass | `rrec_close`: rau_cut, rst_close, rau_halt, rec_mics_off, rau_release, rst_unmount (rrec.c:231 to 236), ruling 2; the screens learn of the state only after the actions (rglue.c:35 to 48, rrec.c:525). Row l.168: rrec.c:245 to 263. |
| Watchdog (FW l.1065, ruling 9) | pass (spec note R6-11) | `rsl_wdt_should_feed`: feed when no recording, else both threads within 2,000 ms (rsy_logic.c:139 to 150); 8,000, 1,000, 2,000 ms in rrec_spec.h:400 to 402; progress from the audio and storage threads (rrec_bridge.c:262, :271). |
| Update size and slot limits (FW l.1012) | pass | `image_size > RREC_IMAGE_MAX_BYTES` (999,424) refused BAD_ARG; data end past min(size, limit) refused (rsy_logic.c:22, 28 to 39); the image interface has only `erase_slot1` and `write(offset)` (rsy.c:132, :160), the real writer bounds every write to slot 1 (rsy_hw_real.c:34 to 51). |
| Factory flag (FW l.1019) | pass | Flag clear: NOT_ALLOWED before anything else (rfa_logic.c:17 to 19); only SHIP_ENTER clears it (rfa_logic.c:71 to 73, rfa.c:435 to 436, rrec.c:345 to 349); every writer of the flag is listed in my search (rfa.c:436, rrec_backend.c:361, rrec.c:346). |

## Bar B1: coverage, N of M rows per unit

M = rows of plan section 2 that name the unit (W/plan-rows-per-unit.txt). For each row read I opened the code and the named
case and checked that the case asserts numbers typed from FW (W/b1-test-excerpts.txt holds the assertions).

| Unit | Rows read | N of M | Result |
|---|---|---|---|
| J | every row: C1, C4, C5, C7, C8, C9, C10, C11, C12, C13, C14, C15, C16, C17, C18, C19, C20, C21, C22, C25, C27, C33, C36, C37, C38, C39, A6, A10, A12, A13, A18, S18, X4, P4, P6, P11, P12, P18, T8, T9, T13, T17, T24, T27 | 44 of 44 | 38 pass; fail: C4 (R6-05), C18 (R6-03), P6 (R6-03, R6-04), P12 (R6-02), T13 and T17 (R6-06); minor on C13 (R6-07) and C39 (R6-14). R6-01 is FW l.151, a core row the join carries out |
| U1 core6 | C10, C11; cases test_row_16 (core test_rows.c:62), test_sign_hook_once_per_press, test_sign_hook_not_called_when_refused_otherwise, test_no_hook_takes_the_sign_as_drawn | 2 of 2 | pass |
| U2 store | C3, C8, S4, S14, S16, S20, S23, S28, T26 | 9 of 37 | pass |
| U3 audio | A1, A6, A7, A8, A9, A16, A17, C13, C15, S10 | 10 of 27 | pass |
| U4 xfer | X2, X4, X5, X6, X7, X8, X9, X10, X17, X19 | 10 of 28 | pass |
| U5 power | C2, C6, P3, P8, P9, P12, P14, P18 | 8 of 18 | pass |
| U6 motor | C26, C28, C29, C30, C31, C32, C33, P7 | 8 of 11 | pass (C34 not provable, C35 dropped by D3) |
| U7 sys | C23, T4, T6, T9, T10, T11, T28, T29 | 8 of 11 | pass |
| U8 factory | T11, T12, T13, T16, T18, T20, T21, T22, T23 | 9 of 15 | pass (T13's join half: R6-06) |
| U9 screens6 | P18 (screen part), T14 | 2 of 2 | pass |
| U0 rhw | no rule row; its 4 fault cases (write fault at n, cut after sector, reboot keeps card, mic stops delivering) | 4 of 4 cases | pass |

Rulings checked as done: D3 (no soft start in ring_motor; rmo.h:6), R22 (FACTORY_EXIT 0x02, rrec_spec.h:349, asserted by
xfer test_proto.c:673), R23 (26 of 26 codes of FW l.1202 equal rrec_spec.h by number and name, W/r23-names.txt), R24 (frame
8,800 asserted, audio test_chunk.c:279), USB test pair marked "NOT FOR SHIPPING" (app/prj.conf:89, 90) (W/rulings-check.txt).

## Bar B3: broken copies

37 copies read, across all 11 units: rhw 3 (disk_fault_late, cut_keeps_tail, mic_no_block_ignored), core 3 (sign_ignored,
sign_before_b5, sign_hook_twice; W/core-broken-diffs.txt), store 2 (hdr_crc_512, sfull_17), audio 2 (discard_0, motor_no_tail),
xfer 2 (tag_not_echoed, range_257), power 2 (mean_of_5, write_while_enabled), motor 3 (m2_gap_100, allowance_5ms,
vibration_mutes_mw), sys 4 (size_999425_ok, end_off_by_one, allowed_at_30, feed_without_progress), factory 2 (flag_ignored,
vbat_read_at_0), screens 2 (ilim_dark_in_recording, factory_wrong_colour), recorder 12 (all of its list). Each edit removes or
inverts the rule (W/broken-edits-sample.txt and the edit files), and the named case asserts the rule's own number or order
typed from FW (for example 999,425 refused, F/tests/sys/src/test_update.c:55; 3,517 / 3,516 / 17 / 16 free chunks, F/tests/store/src/test_space.c:48 to 57;
257 refused, F/tests/xfer/src/test_proto.c:327; 8,150 uA.s per M1 pulse, F/tests/motor/src/test_charge.c:30). Result: pass. Weakness found beside the copies:
R6-05 (no copy drops the partial chunk, and the case would not catch it).

## Bar B4: citations of the notes

64 of 64 sampled citations match (W/cite_check.out, last line `TOTAL 64 of 64 citations match`): rhw 6, core 5, store 8,
audio 6, xfer 5, power 5, motor 5, sys 5, factory 6, recorder 8, screens 5. An earlier look (W/cite_check.run1.out) gave 61 of
64; the 3 misses were my own probe texts (twister drops `test_` from case names; my guess of the motor edit-check text) and the
first K14 hit was the native_sim line; I corrected the probes (W/cite_check.edit.log) and reran. Result: pass, with R6-12.

## Bar B5: seams

Holding: boot order follows the headers (rpw_boot_causes before rpw_start, rpw.h:50; rst_init before rst_mount; one init each,
rrec_boot.c:53 to 80); the storage thread never takes the glue's lock (its callbacks log and post with K_NO_WAIT,
rrec_bridge.c:215 to 241, 257 to 267); who may call the power chip: VDD_SD only by the store, VDD_MIC only by rec_mics_on
(ruling 4), the join reads rail state and VBUS and drives the MOTOR pin for T-MOTOR (ruling 2); the motor's `started` callback
runs in the caller of rmo_play, not the timer (rmo.c:159, rmo.h:29, 30; W/seam-motor-isr.txt).

Seams where two units assume different things: (1) rxf_abort does not wait, rst_unmount does not wait, the join assumes the
unmount worked (R6-03); (2) rpw.h says rpw_ship runs on the join's thread, menu "Power off" runs it on the screens thread
(R6-10); (3) rxf.h lets the class request HFXO, the join says the class does not, and nobody holds it in BOOT and RECOVERY
(R6-04); (4) units post events assuming delivery, the queue drops when full (R6-08); (5) `test_recording` called atomic, is a
plain bool (R6-17).

## The three findings reported by the units

- **F1** (rau.c:313 to 320 and 336): agreed, simulation only. `clear_state` is registered only under `CONFIG_RING_RHW_SIM`
  (rau.c:346 to 348) and is unused in the kit build (j-prod1.log l.17); on the ring a reboot ends the thread. It does make the
  recorder suites depend on a 100 ms sleep after each simulated reboot (F/tests/recorder/src/rt.c:289 and 298). Who acts: U3, if the lead wants it:
  `clear_state` waits for the capture loop to end.
- **F2** (rau.c:313, :48; rmo.c:95): agreed, warnings only, the kit build exits 0 (j-prod1.log l.17 to 19: `'clear_state'
  defined but not used`, `'hook_added' defined but not used`, `'reboot_hook' defined but not used`). Guarding them with the
  same `#ifdef CONFIG_RING_RHW_SIM` removes them.
- **factory_screen.test_frame_sequence with vbat_read_at_0** (factory-notes section 4): a fragile test, not a product fault. The
  copy changes only `rfa_motor_read_delay_ms` (F/tests/factory/broken_edit.py:36 to 38), which T-SCREEN does not call (rfa.c:260 to
  274). The aborted motor case ends after 0.521 s instead of 1.021 s (u8-full1.console l.782 against l.81), so later cases start
  at another moment, and the case demands exactly 1,000 ms between two clock stamps (F/tests/factory/src/test_screen.c:202). Probable
  cause, not proven by a run (R6-13). Who acts: U8, give the spacing a tolerance.

## What I covered and what I did not

Covered: B2 fully (6 of 6); J 44 of 44 rows; the other units as in the B1 table; 37 broken copies; 64 citations; the seams above.

## What I could not check

- No build or run (forbidden by the brief): R6-03 and R6-05 rest on reading the code and the timing, not on a run.
- Rows of U2 to U8 not in the B1 table (28 of 37 store, 17 of 27 audio, 18 of 28 xfer, 10 of 18 power, 3 of 11 motor, 3 of
  11 sys, 6 of 15 factory) were not read; the full run of `tools/build_all.sh` was not judged (brief).
- The real driver files and the two-device factory test were not read beyond their notes.

## questions_for_owner

none

RESULT: done, FAIL on bar B1 with 0 blocker and 6 major findings (R6-01 to R6-06, all in the join), 8 minor and 3 notes; B2, B3 (37 copies) and B4 (64 of 64 citations) pass.
