# Step 4, round 3: answers to the second review (`firmware/docs/step4-review2.md`)

Base: the working folder as it was at the start of round 3 (round 2 delivery). This round has targeted runs only; the lead runs the full command. I ran no git and deleted nothing on the server by pattern. Logs (all in `firmware/build-logs/step4/`, names start with `r3-`):
- `r3-scr1.out` first run of the screens suite (48 of 48), `r3-scr2.out` the final screens run on native_sim and on the simulated chip with the pictures stage and `pictures-fakes` on both targets, `r3-bs.out` bsim screens test S, `r3-bsbrk.out` its three broken copies, `r3-ctl.out` control tests B, G and the `pair_takes_over` copy, `r3-brk.out` and `r3-brkfull.out` the screens broken copies (`r3-brk.out` is cut where the poll lost the server; `r3-brkfull.out` is the whole server log), `r3-dk.out` and `r3-stack.out` the kit build and `stack-report`, `r3-pictures-compare.txt` the picture compare. (`r3-tail.out` and the other small `r3-*` files are helper reads.)
- Line numbers below are lines of those files.

## 1. New fault 1: a timed-out `rscr_sign_start` cancels its request
- `rscr_sign_start` (`modules/ring_screens/src/rscr.c:427`) gives every request a number (`sign_req.seq`, `waiting`); on a timeout it cancels under the screens lock (`waiting = 0`, `pending = false`) and returns -ETIMEDOUT; when the thread answered meanwhile its answer counts. `do_sign_start` (`rscr.c:377`) takes the draw lock, then the screens lock, and works on the request only while `waiting` is still its number: a cancelled request changes nothing and draws nothing; an answer goes only to its own request. The wait is `CONFIG_RING_SCREENS_SIGN_WAIT_MS` (`modules/ring_screens/Kconfig:34`, default 5000; `tests/screens/prj.conf:21` sets 300).
- Test `test_17_a_timed_out_sign_start_is_cancelled_and_never_drawn_later` (`tests/screens/src/test_draw.c:1104`): holds the draw lock so the thread cannot draw, checks -ETIMEDOUT, releases the lock, lets the thread run, checks no recording screen and a core not recording, then that the next call draws (writes grew) and returns 0 with SCR_RECORDING. Log: `r3-scr2.out:90` (native_sim) and `:277` (chip).
- Broken copy `sign_timeout_keeps_request` (the request stays after a timeout) fails that test: `r3-brkfull.out:456`.

## 2. New faults 3 and 4: calling context
- On the screens thread `rscr_sign_start` returns -EDEADLK at once (`rscr.c`, the check against `rscr_thread_id()`, line 419). The rules are in `modules/ring_screens/include/ring_screens/rscr.h:82` ("Calling rules": allowed under the glue lock; not on the screens thread; not with the draw lock held; the wait and the cancel).
- Mechanism for the glue lock: the screens thread never waits for it. `rscr_ops.power_off` now returns an int; the real one calls `rglue_event_try` (`modules/ring_glue/src/rglue.c:148`, declared `rglue_ops` header line 67), which returns -EBUSY at once when the glue's lock is taken; the screens thread repeats the call every 10 ms while the power off is pending (`rscr.c:511` and the 10 ms timeout in the thread loop).
- Test `test_18_sign_start_on_the_screens_thread_and_under_the_glue_lock_with_a_power_off_queued` (`test_draw.c:1141`): (a) the screens thread calls it through a test hook (`rscr_test_sign_start_from_thread`): -EDEADLK; (b) a stand-in for the glue lock is held by the caller, a power off is confirmed through the menu, the thread finds the lock busy (counted, no wait), the call returns 0 without the timeout, and the power off runs once the lock is free. Log: `r3-scr2.out:91` and `:278`.

## 3. New fault 2 (lead's ruling): "Power off" only in STANDBY
- `modules/ring_screens/src/rscr_logic.c`: `enter_state` clamps `menu_sel` to the new item count and closes an open power-off confirmation when the state leaves STANDBY (line 527 and the lines after it); Centre and Right on an index beyond the count do nothing (line 290); `FX_POWER_OFF` is pushed only when `core_state == RC_ST_STANDBY` (line 431).
- Pure table test `test_power_off_only_in_standby` (`tests/screens/src/test_table.c:1162`): (a) clamp, then Centre opens Settings; (b) Centre and Right beyond the count do nothing; (c) the confirmation closes on a state change; (d) no effect outside STANDBY, `FX_POWER_OFF` in STANDBY. Log: `r3-scr2.out:118` and `:305`.
- Broken copy `power_off_outside_standby` (the effect is sent in every state): `r3-brkfull.out:478`.

## 4. New fault 6: queued power off
- `test_12_power_off_is_queued_and_runs_after_the_core_step` (`test_draw.c:979`) now compares the thread that ran the call with the screens thread's id (`rscr_thread_id()`), and also that it is not the thread that ran the core step. Log: `r3-scr2.out:85`.
- Test S (`tests/bsim/screens/ring_app/src/main.c`, checks from "S: Left from the empty list shows the status screen" to "S: the screen is off with the ring", the Yes check at line 280) now drives menu, Power off, Yes through the real glue: the screens queue it, their thread calls `rglue_event_try`, and the core is in OFF (`rglue_state() == RC_ST_OFF`) and the screen is off. `r3-bs.out:48-51`; `TEST S RESULT PASS (38 checks passed)` at `r3-bs.out:86`. The three bsim copies still fail on their named checks: `r3-bsbrk.out:88`, `:164`, `:242`.
- A power off that was queued and dropped because the core left STANDBY first stays dropped (lead's ruling: the safe result); it is said in the notes' section 5b.

## 5. New fault 7: `pictures-fakes` requires the reason lines
- The fakes now live in `tools/pictures_fakes.sh` (called by the stage in `tools/build_all.sh`, for `native_sim` and for the simulated chip: stages `pictures-fakes` and `pictures-fakes-<board>`). The script requires exit 1 from both fakes and, in each output, the line "PICTURE pairing is listed 0 times" (`tools/pictures_fakes.sh:26`) and "PICTURE status is listed 21 times"; an exit 1 without its line, or an empty handler path, fails. Run on both targets: `r3-scr2.out:233-234` (native_sim) and `:420-421` (chip), `pictures listed: 21, bad: 0` at `:51` and `:238`.
- I did not make a fake that crashes the tool to show the stage failing; the check is by reading the script (the two `grep -q` lines).

## 6. New fault 9: test G after the third pairing
- `tests/bsim/control/ring_app/src/main.c:500`: "G: after the third pairing the device that was active (slot 1) is still the active one" (`rdev_active() == 1`), before the switch. `r3-ctl.out:183`; `TEST G RESULT PASS (66 checks passed)` at `:436`; `TEST B RESULT PASS (55 checks passed)` at `:143`; the copy `pair_takes_over` still fails on its named check at `:575`.

## 7. New fault 10 (lead's ruling): LVGL pool 32,768 bytes
- `CONFIG_LV_Z_MEM_POOL_SIZE=32768` in `app/prj.conf:59`, `tests/screens/prj.conf:14`, `tests/bsim/screens/ring_app/prj.conf:52` (3.7 times the measured peak of 8,848 bytes). The notes (5b) say the peak comes from one pass of the picture test and that no long run exists.
- Kit build: 518,984 bytes of flash (53.25%) and 182,184 bytes of RAM (34.82%) (`r3-brkfull.out:483-484`; round 2: 518,580 and 165,792).

## 8. New fault 8: `stack_report.py`
- It prints "unknown" counts per chain and in total (members not in the build output and not declared inlined), counts them as unknown and never as 0 in a sum without saying so, and exits 1 when one is missing (`tools/stack_report.py:91`). Six functions that the compiler inlines (nav, enter_state, render, fill_frame, do_sign_start, draw_notif) have no frame of their own in the build output (checked in `r3-dk.out`: only `render_locked` and `rscr_sign_start` appear); they are declared in `INLINED` (line 48) and printed as "inlined". Result on the kit build: 0 unknown, 7 inlined, exit 0 (`r3-stack.out:27-29`). The notes say it is a static lower bound (5b and section 5).
- The 1,536 figure of round 2 has a source: the line `RING STACK BT RX WQ: size 1536` printed by the round 2 two-device screens test (`r2-bs3.out:50`), the thread's stack size before I set 2048. It is a size, not a use (every thread showed "used at most 24").

## 9. New fault 12: `rglue_set_screen_on`
- Header comment (`modules/ring_glue/include/ring_glue/rglue.h:59`): the setter for builds without `screen_fact`; when `screen_fact` is set its value is replaced before every core call.

## 10. New fault 13: corrections
In `firmware/docs/screens-notes.md`: g.1 the chip's clean manifest is log line 2637 (2474 is the repeat fake); g.2 the compare file is `step4/r2-pictures-compare.txt` (round 3: `r3-pictures-compare.txt`: 42 of 42 identical to the delivered files, and the chip's 42 identical to native_sim); g.3 the R-SIGN copies are 1, 2, 9, 10, 14 and 19; g.4 the stage list now has `stack-report` and the real order; g.5 the pool is 32,768 bytes now (48 KB, 16 KB, 32,768 in the text); g.6 the proposed rule text says the B15 message lasts 5 s and is amber; the copy table has rows 19 and 20; a section 5b describes round 3. Counts that this round changes (stage counts, test counts, log lines of the round 2 log) stay those of the round 2 log until the lead's full run; the notes say which lines are round 3's.
In this file, the review's g.8 to g.10: g.8 (power off "on the screens thread"): the test now compares with the screens thread's id (point 4); g.9 (third pairing in G): the check exists (point 6); g.10 (1,536): source given (point 8).

## Targeted runs, summary
- tests/screens: native_sim `r3-scr2.out:21` (48 of 48), chip `:41` (48 of 48).
- Screens broken copies, 16 (old and new), each failing on its named case: `r3-brkfull.out` (`RESULT PASS` at line 479; copies 456 and 478 are the new ones).
- Control B, G, `pair_takes_over`: `r3-ctl.out:143`, `:436`, `:575`. Screens test S: `r3-bs.out:86`; its copies `r3-bsbrk.out`.
- Pictures stage and fakes on both targets: `r3-scr2.out:51, 233-234` and `:238, 420-421`; pictures byte-identical to the 42 delivered files (`r3-pictures-compare.txt`).
- Kit build with `stack-report`: `r3-dk.out` (build exit 0) and `r3-stack.out` (exit 0).

## Not done
- No full `build_all.sh` run (the lead's). The dk build of `r3-dk` was made from the sources at that time; no later source change touched `app/` or `modules/`.
- The pictures stage output in `r3-scr2.out` is from the targeted command, not from `build_all.sh` itself (the same tool and the same script, called by hand).
- No fake that makes the manifest tool crash (point 5).

RESULT: done, points 1 to 10 are fixed with tests, broken copies and targeted runs passing (screens 48 of 48 on both targets, 16 screens copies caught, test S 38 checks, B and G pass); the full command is left to the lead.
