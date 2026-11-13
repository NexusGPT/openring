# Second review of software step 6 (recorder parts), fix round 1, commit c26ae988

Reviewer: an independent judge (I wrote none of the code, tests or notes of step 6 or of its fix round). Started
2026-11-13 16:47:57 CET (`date`, W/pin-check.txt line 1). The brief holds no verdict of the authors or of the lead.
I ran no build, no test, no command on the build server, no git write and no browser. I read the code, the tests, the
specification and the logs, and ran small read-only greps and Python scripts on the Mac.
"W/" is `firmware/build-logs/step6/review2-work/` (my raw outputs). "F/" is `firmware/`. "FW l.N" is line N of
`design/firmware.md` at c26ae988. "SRC" is the export of c26ae988 named in the brief.

## Pin

What I read is commit c26ae988. Check (W/pin-check.txt): each of the 37 files of the diff, and `design/firmware.md`,
hashed in SRC and in `git show c26ae988:<path>`: 38 of 38 lines `EQUAL`. `git diff af085a68 c26ae988` over the same 37
files, regenerated, is byte-equal to W/fix-round.diff (`diff identical`), and the same diff over `firmware/modules`,
`firmware/tests`, `firmware/app`, `firmware/tools` and `design/firmware.md` gives `37 files changed, 1283 insertions(+),
80 deletions(-)`: no other file of the code, tests, app, tools or specification changed.

## Verdict

**PASS** against the pass line (0 blocker and 0 major open). The six major findings R6-01 to R6-06 are closed: the code
does what the cited lines say and each has a case with numbers typed from the specification and a broken copy that
fails it. All minors and notes of the first review are closed or ruled. The fix round brings 10 new minor findings and
3 notes, none a blocker or major. The six safety rules of the first review's bar B2 still hold.

Counts (new findings of this review): 0 blocker, 0 major, 10 minor, 3 notes.

## Bar A: the six major findings

"Copy" = the variant of F/tests/recorder/broken_edit.py; W/copycheck.out shows that each copy's text matches exactly
once in the pinned rrec.c (`matches 1`). The copy results are from the run u3 on the final files
(`firmware/build-logs/step6/fix1-rec-u3.log`, last result lines l.802 `RESULT PASS` and l.804 `UNIT PASS tests/recorder`).

| Finding | (1) Code against the specification | (2) Case and its copy | Verdict |
|---|---|---|---|
| R6-01 (FW l.151, l.323) | `RC_ACT_SHIP_MODE` only sets `ship_pending` (F/modules/ring_recorder/src/rrec.c:461 to 462); after the step the job is posted (rrec.c:665 to 668) and `rrec_ship_now` waits while `rmo_playing()`, bounded by 280 + 100 ms, before `rmo_stop()` (rrec.c:352 to 359). M2 is played in the step before (row order SAVE_SETTINGS_TIME, M2, SHIP_MODE). | `recorder_ship.test_ship_feels_whole_m2` (F/tests/recorder/src/test_ship.c:35): exactly 4 MOTOR edges before SHPHLDCONFIG (l.61), levels 1 0 1 0, segments 80, 120, 80 ms typed from FW l.323, total 280 ms. Copy `ship_cuts_m2` disables the wait (rrec.c:356): the motor stops at once, so fewer than 4 edges come before SHPHLDCONFIG and l.61 fails. u3 l.589 and l.599: the named case failed on both boards. | CLOSED |
| R6-02 (FW l.937, l.939) | `rrec_ship_now` step 1: recording guard (rrec.c:361 to 363), storage (`unmount_now`, rrec.c:364), USB (`rxf_stop`, rrec.c:365; F/modules/ring_xfer/src/rxf_class.c:356 to 371), the join's HFXO (rrec.c:366 to 369), radio (`rdev_stop`, rrec.c:371; F/modules/ring_devices/src/rdev.c:501 to 514, its only advertising start is in `update_fn`, which returns at once when stopped, rdev.c:194, W/rdev-rpw-check.txt), screen (`rscr_sync` after the screens were told SHIP or OFF in the step, rrec.c:381 and :664), then `rpw_ship` (rrec.c:388). CONFIG_RING_DEVICES=y in app/prj.conf:37 and tests/recorder/prj.conf:32 (W/seam-greps2.txt). | `recorder_ship.test_ship_closes_each_part_first` (F/tests/recorder/src/test_ship.c:81): at the end of step 1 VDD_MIC off, VDD_SD off before SHPHLDCONFIG, USB disabled before SHPHLDCONFIG, one radio stop, panel blanked (l.123, l.143), beacon not stopped, thread `rrec`, for the factory path and the menu path. Copy `ship_screen_on` runs ship mode before the screens are told (rrec.c:664): the panel is not blanked at the hook, l.123 fails; u3 l.624 and l.635. Radio effect: tests/bsim/control test C, `fix1-rec-c1.log` l.364 `advertising reports after the ship close: 0`, l.372 `TEST C RESULT PASS (31 checks passed)`; copy `radio_not_stopped`, `fix1-rec-c2.log` l.91 `... 131`, l.99 `TEST C RESULT FAIL` (W/bsim-lines.txt). Residual weaknesses: R2-04, R2-05, R2-13. | CLOSED |
| R6-03 (FW l.178, l.179, l.1234) | `unmount_now` uses `rst_unmount_wait(FINISH_WAIT_MS)` (rrec.c:308; F/modules/ring_store/src/rst.c:506 to 508, op_lock with a timeout), keeps the result, posts a retry on -EBUSY (rrec.c:300 to 322, 395 to 406); used by `RC_ACT_SD_OFF` (rrec.c:454), the rails after each step (rrec.c:556) and ship step 1. `RC_ACT_ABORT_COMMAND` now waits with `rxf_finish(FINISH_WAIT_MS)` (rrec.c:508 to 509). 0x0290 is written at the first failed try (rrec.c:313 to 316) and once at the end (rrec.c:292 to 297), as FW l.1234 says, except R2-02. | `recorder_unmount.test_unconfigured_finish_times_out` (F/tests/recorder/src/test_unmount.c:90): VDD_SD off inside the step of row 46 (l.100), the finish timed out first. Copy `unmount_result_dropped` (rrec.c:308): the unmount answers -EBUSY at once and is dropped, so VDD_SD is still on at the step's end; u3 l.665 and l.681 (`sd_off_in_the_step: (rt_sd() is true)`, u3 l.655). `test_failed_unmount_retried_and_reported` (l.107): exactly 2 records 0x0290 (l.140), first -EBUSY try 1 in TRANSFER, then errno 0 with 2 or more tries (u3 l.806 to l.808). The case of FW l.179 (`test_vbus_out_during_read_command`, l.79) has no copy of its own: R2-08. | CLOSED |
| R6-04 (FW l.915) | `hfxo_wanted` holds BOOT, RECOVERY, CHARGING, TRANSFER, FACTORY_TEST (rrec.c:533 to 536); `rrec_hfxo_follow_state` after every step (rrec.c:569) and at the start of the boot (F/modules/ring_recorder/src/rrec_boot.c:52). The table of FW l.915 says HFXO "on" in BOOT and RECOVERY; the design decision keeps that table. | `recorder_rails.test_hfxo_in_boot_and_recovery` (F/tests/recorder/src/test_rails.c:119): HFXO held from the boot card init to the step into STANDBY (l.132, l.146), released in STANDBY (l.133, l.147, FW l.916). Copy `no_hfxo_in_boot` removes BOOT and RECOVERY (rrec.c:535): no request at the card init, l.132 fails; u3 l.696 (`held_through(i_init, t_stb_us) is false`), l.705, l.716. | CLOSED |
| R6-05 (FW l.125, l.443, l.460) | The close itself is unchanged and in the order of FW l.125 (rrec.c:238 to 243). The finding was about the case. | `recorder_actions.test_close_order` (F/tests/recorder/src/test_actions.c:98) now times the mark in the middle of a chunk and reads every frame of the closed recording: each equals the input counter from frame 800 (FW l.460) (l.87), the chunks add up to the CLOSE duration, the last chunk is partial (l.90), the duration matches 16 frames per ms within 256 + 32 frames. Copy `close_drops_partial` (`rst_close(NULL, ...)`, rrec.c:239): the partial chunk is missing, so the last chunk is full and about 3,000 to 5,000 frames are missing; l.90 fails. u3 l.748 and l.767. | CLOSED |
| R6-06 (FW l.1024, l.1029) | The real path: rfa calls `ops.test_recording` (F/modules/ring_factory/src/rfa.c:218, :246) = `rrec_test_recording` (F/modules/ring_recorder/src/rrec_backend.c:369), type 2 (rrec.c:727). | `recorder_factory.test_tmic_records_type_2_for_2s` (F/tests/recorder/src/test_factory.c:55) over the simulated USB: type 2 (l.76), 32,000 frames within 256 (l.78, FW l.1024 and l.443), VDD_MIC on once. Copy `test_recording_wrong_type` opens type 1 (rrec.c:727): l.76 fails; u3 l.790 and l.800. `test_tsign_reports_mic_times` (l.87): the four reported times equal the rail's own within 1 ms (l.117); the lengths have a lower bound only and the case has no copy: R2-07. | CLOSED |

## Bar B: the minors and notes of the first review

| Finding | Verdict | Evidence |
|---|---|---|
| R6-07 | CLOSED | The notes now say it: `firmware/docs/recorder-notes.md` l.368 (row C13: no product code sends `RC_EV_BLE_HIGHLIGHT` before FW 7). |
| R6-08 | CLOSED | Full-queue jobs of VBUS_OUT, CHUNK_WRITE_FAILED, MIC_NO_BLOCK, SHIP, UNMOUNT are latched (F/modules/ring_recorder/src/rrec_bridge.c:82) and queued again after each job and at least every 100 ms (rrec_bridge.c:90, :181 to 182, :208); case `recorder_actions.test_latched_events_not_lost` (test_actions.c:383). New weakness: R2-06. |
| R6-09 | CLOSED | `run_retry` reads `mi` only after its own `rst_mount` (rrec_bridge.c:158 to 166, W/citecheck.out c19). |
| R6-10 | CLOSED | `rpw_ship` runs on the recorder's thread for every path (job RREC_JOB_SHIP, rrec.c:668); the menu's step on the screens thread only posts it. Case asserts thread `rrec` for both paths (test_ship.c). |
| R6-11 | RULED | FW l.218 and l.1065 changed: the watchdog is fed by a work item on the system work queue, every turn with no recording. Code: `k_work_reschedule(&wdt_work, K_MSEC(RREC_WDT_FEED_MS))` (F/modules/ring_sys/src/rsy.c:473, :494, system work queue) and `rsl_wdt_should_feed` (W/b2-check.txt). |
| R6-12 | CLOSED | The three K3 logs are in commit c26ae988 (W/r617-r612-check.txt: `IN COMMIT` for each). |
| R6-13 | CLOSED | Cause shown first (`fix1-rec-r613a.log`); the case now measures in ticks and accepts 1,000,000 to under 1,001,000 us (F/tests/factory/src/test_screen.c:205 to 216, W/citecheck.out c35). |
| R6-14 | CLOSED | `recorder_screens.test_battery_reaches_screens` (test_screens.c:49) compares the join's picture with pictures of typed values (50 %, Charging, 30 min; Full) and requires a difference for 31 min, 51 % and Full (l.62, l.72). `frame_hash` calls `rscr_sync()` first (test_screens.c), so each reference picture is the one just set (W/code-excerpts2.txt). |
| R6-15 (F1) | CLOSED | `clear_state` waits for the capture loop (F/modules/ring_audio/src/rau.c:324, bounded 32 x 16 ms; the loop gives `halt_sem` at its end, rau.c:310, W/rau-halt.txt); the two sleeps after the simulated reboot are gone (F/tests/recorder/src/rt.c, diff). |
| R6-16 (F2) | CLOSED | Guards in rau.c and F/modules/ring_motor/src/rmo.c:95 to 112; kit build `F2 warnings: 0` (`fix1-rec-u2.log` l.8425). |
| R6-17 | CLOSED | `atomic_t test_recording` (F/modules/ring_recorder/src/rrec_int.h:80); every use is `atomic_get` or `atomic_set` (W/r617-r612-check.txt lists all 8 uses in modules and tests). |

## Bar C: new findings from the fix round

I read every hunk of W/fix-round.diff (2,174 lines, 37 files). The six safety rules of B2 still hold (W/b2-check.txt):
(1) no press event is posted by the join, the latch re-posts only VBUS_OUT, CHUNK_WRITE_FAILED, MIC_NO_BLOCK, SHIP and
UNMOUNT, and `rc_core_event` still refuses press events (F/modules/ring_core/src/core.c:177 to 181); (2) the only
`rail_set(RHW_RAIL_MIC, true` is F/modules/ring_recorder/src/rrec_mics.c:53, after `sign_draw`; (3) `rrec_close` keeps its
order (rrec.c:238 to 243) and the screens learn the state after the actions (rrec.c:664); (4) the watchdog rule and
(5) the update limits are in ring_sys, which the fix round did not change (F/modules/ring_sys/src/rsy_logic.c:22 to 39,
:144 to 150); (6) the factory flag is written only by rrec.c:469, rrec_backend.c:361 and ring_sys (rsy.c:305).
Seams checked: who runs core steps (W/seam-rglue-callers.txt: the recorder's thread, the glue's tick thread, the
screens thread through `rglue_event_try`, the boot); no caller on the system work queue, so the new waits do not stall
the watchdog's feed.

| Id | Severity | File and line | Spec line | What is wrong |
|---|---|---|---|---|
| R2-01 | minor | F/modules/ring_recorder/src/rrec.c:395 to 405, :279, :324 | FW l.912 to l.920 | Seam: `rrec_unmount_retry` checks the state, then waits up to 5,000 ms in `rst_unmount_wait`, on the recorder's thread without the glue's lock. A step on another thread (the glue's tick thread runs the long press deadline, F/modules/ring_glue/src/rglue.c:85 to 97) can move the state to RECORDING meanwhile; the retry then unmounts the card that RECORDING wants, and the recording fails. `unmount_tries` and `unmount_last_err` are plain statics written by that thread without a lock and by steps under the lock. Needs a failed unmount and a long press inside the retry's wait. From reading. |
| R2-02 | minor | rrec.c:324, :402, :405 | FW l.1234 | When the retry ends because the state wants the card again, the end record uses `unmount_last_err`, which only a retry writes. After an earlier episode that ended with a successful retry it still holds 0, so the record says errno 0 ("the unmount then succeeded") for an unmount that never succeeded. FW l.1234: "0 when the unmount then succeeded, else the last errno". No case covers it. |
| R2-03 | minor | rrec.c:503, :508 to 509, :454, :556 | FW l.178, l.179 | Seam, blocking under the glue's lock: one step can now wait 5,000 ms in `rxf_finish`, then 5,000 ms in the SD_OFF unmount, then 5,000 ms again in the rails' unmount of the same step (the second try also counts as a try and posts a second retry job). The step holds the glue's lock for up to about 15 s (before the fix: at most the 5 s finish). The tick thread and `rglue_set_vibration` on the screens thread (F/modules/ring_screens/src/rscr_real.c:99, K_FOREVER) wait that long. Bounded, so not a hang. |
| R2-04 | minor | rrec.c:364, :388 | FW l.937 | Ship step 1 goes on after a failed unmount: the -EBUSY of `unmount_now()` is dropped and `rpw_ship` runs with the card mounted and VDD_SD on. The retry job it posted runs only after `rpw_ship` returns. Storage is closed before USB, so a USB command that holds the store is aborted only after the 5 s unmount wait failed. Needs a store call longer than 5 s at ship time. |
| R2-05 | minor | rrec.c:381; F/modules/ring_screens/src/rscr.c:554 to 556 | FW l.937, l.165, l.174 | `rscr_sync()` waits without a bound once the screens started (a loop of 200 ms waits until the screens thread has drawn). Ship mode now depends on the screens thread: a stuck screens thread stops every ship, including OFF at B2. Before the fix, ship mode did not wait for the screens. The lead's ruling 4 covers only the case before `rscr_start` (rscr.c:548). |
| R2-06 | minor | F/modules/ring_recorder/src/rrec_bridge.c:82, :90, :208 | FW l.172, l.152 | A latched job goes to the back of the queue, behind jobs posted after it. A latched VBUS_OUT can then reach the core after a later VBUS_IN, and the core ends up without VBUS while VBUS is present. Only when the 32-entry queue was full. |
| R2-07 | minor | F/tests/recorder/src/test_factory.c:121 to 123 | FW l.1029 | Test weakness: T-SIGN asks for "two 1 s test recordings". The case checks each length and the gap only from below (`>= 1000`) and has no copy. A join that records 2 s per T-SIGN recording would pass it, and T-MIC (a 2 s request) would pass too. |
| R2-08 | minor | F/tests/recorder/src/test_unmount.c:79 to 86 | FW l.179 | Test weakness: the FW l.179 case has no copy of its own. Each of the two new waits alone (abort then `rxf_finish`, rrec.c:509; `rst_unmount_wait`, rrec.c:308) makes it pass. Under `unmount_result_dropped` it failed only in its setup, `transfer_with_busy_store: (rt_state() not equal to RC_ST_TRANSFER)` (u3 l.656), after the case before it had failed. That is a cascade, not a detection (W/u3-unmount-copy.txt). |
| R2-09 | minor | design/firmware.md l.1204 | FW l.1204, l.1234 | Section D below. |
| R2-10 | minor | firmware/docs/recorder-notes.md l.354 | - | Section E below: one wrong citation. |
| R2-11 | note | rrec.c:361 to 363 | FW l.125 | The guard `rrec_close` in ship step 1 would close a recording after the screens were told SHIP or OFF, against the close order of B2 rule 3. It is not reached when the rows close first (FW l.165: "close; ship mode"). |
| R2-12 | note | rrec.c:375 to 377 | FW l.937 | `rrec_test_radio_stops` counts the call, not its effect. The effect is shown only by tests/bsim/control test C, on the simulated chip (fix1-rec-c1.log l.364). |
| R2-13 | note | F/modules/ring_devices/src/rdev.c:46, :506 | FW l.941 | `stopped` is never cleared (`rdev_init` does not clear it, W/rdev-rpw-check.txt). If ship mode fails (`rpw_ship` returns after its retry, FW l.941), the ring runs on with no radio until a reboot. |

## Bar D: the specification change

The hunks of `design/firmware.md` (W/fix-round.diff l.1 to l.44): l.218 and l.1065 (watchdog), H11 and H15 (status
lines), the new row l.1234 (0x0290).

- l.218 and l.1065 agree with each other and with the code (rsy.c:473, system work queue). No other line still names a
  "main loop" (W/spec-greps.txt: the only hit is l.1065's "(the product has no main loop)").
- H11 and H15: the cited lines exist at c26ae988 (`design/architecture.md` l.303 carries REPLACED;
  `design/case/case-architecture.md` l.88 gives 3.21 min; the ten H15 lines all carry REPLACED or 17.11,
  W/spec-d-check.txt).
- **R2-09 (minor):** FW l.1204 still says "that file and this table hold the same 26 codes". Row l.1234 adds a 27th
  code and itself says "27 codes", and rrec_spec.h now has 0x0290 (rrec_spec.h:448). l.1204 contradicts the change.
  Who acts: the specification's owner.
- The row l.1234 matches the code's two records (first try, end), except R2-02.

## Bar E: citations of "Fix round 1"

66 citations sampled from recorder-notes.md sections FR1.1 to FR1.6: 36 file:line citations against SRC and 30
log:line citations against `firmware/build-logs/step6/fix1-rec-*.log`. Result: **65 of 66 match** (W/citecheck.out,
last line `TOTAL 65 of 66 citations match`). The miss: FR1.1 R6-03 (notes l.354) puts `RC_ACT_ABORT_COMMAND`'s
`rxf_finish(FINISH_WAIT_MS)` at "rrec.c:533"; it is at rrec.c:509 (rrec.c:533 is `hfxo_wanted`) (R2-10, minor).
An earlier look (W/citecheck.run1.out, `TOTAL 59 of 66`) had 6 more misses. They were my own probe texts: twister drops
`test_` from case names in its status lines. I corrected them (W/citecheck.edit.log, `edits 6`) and ran the check again.
Also: run u2 ran the 0x0290 code from before the lead's last ruling. The notes say so (FR1.4), and the diff between
that code and the pinned rrec.c covers only the 0x0290 record logic (W/runs-vs-final.txt). The final rrec.c was run in
u3, whose copy diffs show the pinned line numbers (u3 l.641 `@@ -305,7 +305,8 @@`, matching rrec.c:305 and :308).

## What I covered and what I did not

Covered: every hunk of the 37 files of the diff; A for 6 of 6 findings, each with its case and copy; B for 11 of 11
earlier minors and notes (R6-07 to R6-17); the six B2 rules at the pin; the threads that run core steps and every new
wait in them; D for the five hunks of the specification; E for 66 citations.
Not covered: code that the fix round did not change, except where a new call reaches it (rglue.c, rscr.c sync and
thread loop, rxf_class.c finish, rst.c lock, rdev.c advertising start, rpw.c ship wait, rau.c halt). The plan rows of
the other units were not read again.

## What I could not check

- No build or run (forbidden by the brief). Every pass of a case and every failing copy rests on the logs
  `fix1-rec-u2.log`, `fix1-rec-u3.log`, `fix1-rec-c1.log`, `fix1-rec-c2.log`, not on a run of mine. That the server
  built exactly c26ae988 is shown only for rrec.c, by the copy diffs' line numbers in u3. For the other changed modules
  (store, xfer, devices, screens, audio, motor) the last full run is u2, and I could not compare the server's files with
  the pin.
- R2-01, R2-03, R2-04, R2-05 and R2-06 rest on reading the code and the thread model, not on a run.
- The radio close is proven only on the simulated chip (bsim test C calls `rdev_stop` directly, not through ship mode);
  the real Bluetooth stack and the real panel, USB and power drivers were not read.

## questions_for_owner

none

RESULT: done, PASS: R6-01 to R6-06 closed and every earlier minor and note closed or ruled, with 0 blocker, 0 major, 10 minor and 3 notes new from the fix round.
