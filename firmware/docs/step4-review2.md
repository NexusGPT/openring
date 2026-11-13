# Step 4, second review: round 2 of the screens

Version judged: the files on disk under firmware/ on 2026-11-12 from 17:15 CET, which the lead names commit 844a6d5. I ran no git, so I did not confirm that id. No file under F/modules, F/tests, F/tools, F/app or F/docs changed while I worked (EV/mtimes.out, checked 17:23). The brief holds no verdict of the builder about this review, so independence holds. I ran no build, no test, no ssh and no browser. Statements about run time come from LOG. Statements marked "by reading" come from the code only.

Short names:
- F/ = firmware/
- LOG = F/build-logs/step4/20261112-163311-os-screens-r2.log (10,178 lines). F/build-logs/20261112-163311-os-screens-r2.log is byte-identical (cmp exit 0, EV/logs-ls.out).
- R2 = F/docs/step4-round2.md, NOTES = F/docs/screens-notes.md, REV1 = F/docs/step4-review.md, FW = design/firmware.md
- RSCR = F/modules/ring_screens/src/rscr.c, LOGIC = F/modules/ring_screens/src/rscr_logic.c, DRAW = F/modules/ring_screens/src/rscr_draw.c, GLUE = F/modules/ring_glue/src/rglue.c, RDEV = F/modules/ring_devices/src/rdev.c, RDEVL = F/modules/ring_devices/src/rdev_logic.c, REAL = F/modules/ring_screens/src/rscr_real.c
- TDRAW = F/tests/screens/src/test_draw.c, TTAB = F/tests/screens/src/test_table.c, REFS = F/tests/screens/src/test_refs.h, CTL = F/tests/bsim/control/ring_app/src/main.c
- EV = my evidence folder, outside the project: <scratch>/r2rev/ (session files, may not last).

## 1. The 15 findings of the first review

Counts: 10 closed, 4 partly, 1 open.

1. **SCR_REC_DIM at brightness 0: closed.**
   - LOGIC:45 `rscr_brightness_level` gives 85 for SCR_REC_DIM. RSCR:313 uses it for the panel.
   - TDRAW:543 asserts the display received 85 while SCR_REC_DIM is shown; TTAB:977 checks all three settings.
   - Copy `dim_brightness_zero` fails at TDRAW:543 (LOG:9951) and its named case (LOG:9972). FW:341 now states level 85.
2. **Picture checks accept other screens: closed.**
   - REFS holds key texts per scene; `save()` compares them (TDRAW:353, assertion at TDRAW:377).
   - Cross check in the suite (TDRAW:1104): own 21 of 21 pass, blank and white fail 21 of 21, other frames fail 420 of 420 (LOG:2208 and LOG:2339).
   - Wrong values fail inside the tests (TDRAW:419 test_01, test_04, test_09, test_10). Copies `wrong_passkey_digit` and `wrong_timer_digit` fail at the scene key values, TDRAW:377 (LOG:10021, LOG:10045).
   - Rest risk in question e below.
3. **Drawing-layer R-SIGN copy does not test blanking: closed.** Copy `blank_after_draw` fails at the "never blanked" assertion TDRAW:575 (LOG:9987), named case at LOG:10007.
4. **Pictures stage accepts a missing or repeated picture: closed.**
   - F/tools/pictures_manifest.py:19 lists the 21 names; each must appear once.
   - Stage `pictures-fakes` (F/tools/build_all.sh:133) ran both fakes. The tool gave the right reasons: "PICTURE pairing is listed 0 times" (LOG:2429) and "PICTURE status is listed 21 times" (LOG:2453). Both exit 1 (LOG:2475), stage exit 0 (LOG:2476).
   - Weak spot: new fault 7.
5. **Screens draw from two threads: closed.**
   - `rscr_sign_start` (RSCR:393) queues a request. The screens thread draws it in `do_sign_start` (RSCR:362), under `draw_lk` (RSCR:377).
   - `render` takes the same lock (RSCR:340), and so does the test hook (DRAW:635).
   - Copy `sign_on_caller_thread` fails at TDRAW:958 (LOG:10101).
   - New faults 1, 3 and 4 sit in this new code.
6. **Lock fact races and nested core step: closed.**
   - The glue reads the fact right before every core call (GLUE:20, :72, :103, :139). The value comes from `rscr_lock_fact_now` (RSCR:162), computed under the screens lock. Nothing else writes it any more.
   - Power off is a flag (RSCR:116). The screens thread runs it after its pass (RSCR:454).
   - Tests: TDRAW:993 (LOG:2262) and TDRAW:970 (LOG:2261).
   - What is left: new faults 5 and 6.
7. **Deviation 8 drops the new device's link: closed.**
   - RDEV:423 makes the new slot active only when none is active. `active_changed` fires only then (RDEV:444). RDEVL:64 does the same.
   - The screens no longer put the old device back: RSCR:183-191 has no effect list.
   - Test B pairs a second device. The first stays active (LOG:2822), reconnects (LOG:2824) and gets the keys while linked (LOG:2825). Copy `pair_takes_over` fails at that check (LOG:3700). FW:394 and FW:778 state the rule.
8. **Session and status rows: closed.**
   - B15 (LOGIC:612-621) shows "Battery low" for 5 s. It shows nothing while SCR_PAIR is up or a session is open. This matches FW:153.
   - A double press in a session shows SCR_MODES outside RECORDING (LOGIC:669-679), as FW:389 says.
   - Tests: TTAB:1035 (LOG:2268), TTAB:1109 (LOG:2271), TDRAW:1014 (LOG:2263).
9. **Power off does nothing outside STANDBY: partly.**
   - The menu has 5 items outside STANDBY (LOGIC:39, used at LOGIC:286 and DRAW:551). Tests: TTAB:994 (LOG:2277) and TDRAW:1043.
   - A path is left: new fault 2.
10. **MT follows the lock fact: closed.** The lead ruled it (FW:334). Tests: TTAB:1135 (LOG:2280) and TDRAW:993 (LOG:2262).
11. **No screen means no sign, silently: partly.**
    - `rscr_sign_start` returns -ENODEV when the screens did not start (RSCR:397-399). TDRAW:963 tests it.
    - The product still only prints on a failed start (F/app/src/main.c:107). `rscr_glue_after` and `rscr_lock_fact_now` still return true when not started (RSCR:133-135, :166-168).
    - Recording is not blocked. R2 point 5 defers this to step 6.
12. **Stacks not measured: partly.**
    - Sizes were raised: glue 3072 (F/app/prj.conf:66), BT RX 2048 (F/app/prj.conf:67), screens default 8192 (F/modules/ring_screens/Kconfig:36).
    - No runtime peak exists: every thread shows "used at most 24" (LOG:8984-8993). The builder says so.
    - The static sums (LOG:1285-1302) count unknown frames as 0 and the stage cannot fail: new fault 8.
13. **Unprotected small state: closed.** Battery values and names are written under `lk` (RSCR:232-237, :243-250) and copied under `lk` in `fill_frame` (RSCR:273-281). `pair_prev_active` is gone.
14. **Kit source in step 4 logs: open.**
    - F/build-logs/step4/probe2.out and F/build-logs/step4/20261112-102620-probe2.log are still there, dated 10:26 (EV/files-check.out). R2 point 16 leaves them to the lead.
    - Round 2 added kit Kconfig text to a new log: new fault 11.
15. **Memory larger than needed: partly.**
    - The LVGL pool fell from 49,152 to 16,384 bytes (F/app/prj.conf:59), sized from a measured peak of 8848 bytes (LOG:2209). RAM is now 165,792 bytes (LOG:1251).
    - The 57,600-byte frame memory is unchanged (F/modules/ring_screens/src/memdisplay.c:18), and so is the inbox copy in the frame.

## 2. New faults in the round 2 changes

1. **Major, latent until step 6 calls it: a timed-out `rscr_sign_start` leaves its request behind.**
   - On timeout the call returns -ETIMEDOUT (RSCR:408-409) but `sign_req.pending` stays true.
   - The thread later runs `do_sign_start` anyway (RSCR:440-444). It forces SCR_RECORDING with the stale start time (RSCR:368-374), whatever the core state.
   - If the recorder gave up after the error, the ring shows a recording sign and a running timer while not recording (by reading).
   - The next call can also get the old answer. That call sets pending (RSCR:401-405). The late `do_sign_start` then clears it and gives the semaphore (RSCR:387-389), so the new request is never drawn and its result is the old one.
2. **Minor: Power off can still be confirmed outside STANDBY.**
   - Open the menu in STANDBY and move to "Power off" (menu_sel 5). Then B5 or storage full arrives.
   - `enter_state` does not touch the screen for ERR_BATTERY_LOW or ERR_STORAGE_FULL when coming from STANDBY (LOGIC:569-575). So menu_sel stays 5.
   - Centre falls to the default branch and opens SCR_CONFIRM for power off (LOGIC:330-333). Yes sends FX_POWER_OFF with no state check (LOGIC:426-428).
   - The core has a power-off row only in STANDBY (F/modules/ring_core/src/state_table.inc:21). Same effect as finding 9: the wearer confirms and nothing happens. No test covers a state change with the menu open.
3. **Minor: `rscr_sign_start` has no guard for its calling context.**
   - Called on the screens thread, it waits 5 s for itself and returns -ETIMEDOUT (RSCR:400-412). Fault 1 follows.
   - Called while the caller holds the public draw lock (`rscr_draw_lock`, RSCR:346-349), the thread blocks on that lock and the same happens.
   - Called while holding the screens lock: impossible from outside, since `lk` is static (RSCR:19).
   - F/modules/ring_screens/include/ring_screens/rscr.h:74-78 does not state these limits.
4. **Minor: sign start under the glue lock can stall on a queued power off.**
   - The natural step 6 caller is `recording_action`, which runs inside the core step under the glue lock (F/app/src/main.c:67-75, GLUE:33-36).
   - If the screens thread is then in `ops->power_off` (RSCR:455 to REAL:93 to GLUE:137), it waits for the glue lock while the caller waits for the thread. The result is a 5 s stall and -ETIMEDOUT.
   - Rare: it needs a confirmed power off at the same moment.
5. **Minor: a short stale window for the lock fact remains.**
   - The fact is read at GLUE:72, :103, :139. The screens thread changes `s` under the screens lock only (RSCR:445-451), so it can dim or light the screen between that read and `rscr_glue_after`.
   - By reading the effects are benign: a direction from a screen dimmed in that window still shows SCR_RECORDING (LOGIC:651-657), and a press while a message just lit the panel only wakes.
6. **Minor: a queued power off is lost if another core step changes the state first, and the real path is untested.**
   - Between RSCR:116 and RSCR:454 a long press, B5 or VBUS can move the core out of STANDBY. The event then has no row (state_table.inc:21) and is dropped. That is the safe outcome during a recording, but it is silent.
   - TDRAW:989 only checks the stub ran on a thread other than the test's (TDRAW:149-153), not that it ran on the screens thread or through `rglue_event`.
   - Neither bsim ring app drives power off (EV/misc1.out, empty grep).
7. **Minor: `pictures-fakes` accepts any exit 1.** F/tools/build_all.sh:136-143 reads only the exit codes. A Python crash also exits 1, and so does an empty handler path (`find ... | head -1` at :145). Either way the fakes pass for the wrong reason. In this run the reasons were right (LOG:2429-2431, LOG:2453-2474).
8. **Minor: `stack-report` cannot fail and counts unknown frames as 0.** F/tools/stack_report.py has no exit path (EV/lines-final.out, grep for exit found nothing). Six chain members print "?" and add 0 (LOG:1287, :1289, :1297-1299: nav, enter_state, render, fill_frame, do_sign_start, draw_notif). R2 calls it a lower bound, which is fair. The BT RX claim "the build showed 1,536" (R2 point 11) is not in r2-sym.out or r2-dk.out (EV/misc1.out): unverified.
9. **Minor: test G no longer checks the active device after the third pairing.**
   - After host 3 pairs, CTL:498-499 switches to slot 2 at once.
   - `rdev_switch` returns 0 also when nothing changes (RDEV:647), so a take-over at the third pairing would pass G.
   - Test B covers the second pairing (LOG:2822) and the pure test covers `rdev_list_add`.
   - R2 point 7.5 says G checks after host 2 and after host 3; the check exists only after host 2 (CTL:491).
10. **Minor: the LVGL pool is sized from one pass of the picture test.** 16,384 bytes (F/app/prj.conf:59) against a peak of 8848 bytes (LOG:2209), which includes the test's reference drawings. No long run and no product-side peak were measured. A failed allocation would hit drawing, including the recording sign (by reading).
11. **Minor: new kit text in a project log.** F/build-logs/step4/r2-sym.out:8-17 holds ten lines of Zephyr and nRF Connect SDK Kconfig (paths under zephyr/subsys/bluetooth and nrf/subsys/bluetooth, with defaults and help lines). This contradicts R2 point 16, "I added no kit text to any log". I do not copy those lines here.
12. **Minor: `rglue_set_screen_on` is still public** (GLUE:125-130). With `screen_fact` set, its value is overwritten before every core call (GLUE:20-25), so in the product a call to it does nothing. The bsim control and iPhone ring apps still use it with no `screen_fact`, which is consistent.
13. **Minor (documents): false or stale statements.** See question g.

## 3. The new broken copies, read from LOG

Each line gives the named case's FAIL line, then the assertion that fired.
- `dim_brightness_zero`: named case test_04 at LOG:9972. It fires at TDRAW:543, the brightness not 85 (LOG:9951). Right fault.
- `blank_after_draw`: test_04 at LOG:10007. It fires at TDRAW:575, the blanking count (LOG:9987). Right fault.
- `wrong_passkey_digit`: test_09 at LOG:10031. It fires at TDRAW:377 `scene_ok` in `save` (LOG:10021). Right fault.
- `wrong_timer_digit`: test_04 at LOG:10065. It fires at TDRAW:377 (LOG:10045). Right fault.
- `no_title_app`: test_16 at LOG:10087. It fires at TDRAW:1086, the detail title (LOG:10079). Right fault. The list row has no copy.
- `sign_on_caller_thread`: test_11 at LOG:10109. It fires at TDRAW:958, `on_caller` (LOG:10101). Right fault.
- `pair_takes_over` (control bsim): test B at LOG:3700, on "after the second pairing the first device is still the active one". Right fault.
- All six screens copies ran on native_sim only (F/tests/screens/broken_run.sh, BOARDS line). Cascades: `dim_brightness_zero`, `blank_after_draw` and `wrong_timer_digit` also fail test_05 to test_09 and test_99 (LOG:9952-9957, LOG:9988-9993, LOG:10046-10051). The suite depends on test order. That is not new, but it hides which later checks hold on their own.
- R2 point 17 says `r2-brk` covered "the five new screens copies". There are six. Cannot tell which one was added later.

## 4. Line numbers checked in the builder's answer

- 42 log line citations of R2 and NOTES: all match except one (EV/cites-log.out, EV/cites-files.out).
- 48 file line citations of R2 and NOTES: all match (EV/cites-files.out).
- The one wrong citation: NOTES:14 gives LOG:2474 for the simulated chip's `pictures listed: 21, bad: 0`. LOG:2474 is the repeat fake, "bad: 21". The chip line is LOG:2637.

## 5. Answers to the questions

**a. ring_devices change.**
- Callers by reading: `rdev_list_add` is called only by tests (EV/callers.out). `on_pairing_complete` sets the active slot itself (RDEV:423-427).
- `active_changed` users (F/app/src/main.c:38, REAL:150, both bsim ring apps) only refresh or count. They do not depend on a pairing firing it.
- `rdev_switch` (RDEV:603) and `rdev_remove` fire it as before.
- The new link: the plan disconnects a link whose slot is not the target (RDEVL:131-132), and `submit_update` runs after pairing (RDEV:449). FW:394 states this.
- Bonded device with no active device and no way to reach it: no new path by reading.
  - Remove moves the active slot to the next paired one (RDEVL:91-93).
  - Boot picks the saved or the first paired slot (RDEV:537-545).
  - A pairing with none active takes over (RDEV:423).
  - A bonded, inactive device is reached with "Use" (FX_DEV_USE, LOGIC:414, RSCR:98-99).
  - One edge is not new: a pairing that completes after the window closed is not counted (RDEV:416), the same as in round 1.
- Step 2 assertions:
  - `test_remove_and_active` and `test_switch_decision` now reach the old state with `rdev_list_switch` and then assert what they asserted before (diff lines 1656-1658, 1665-1667). Not weakened.
  - `test_new_pairing_becomes_active_only_when_none_is_active` asserts more than before.
  - B keeps "host 2 reconnects, link ready" after a switch (CTL:338 onward, LOG:2832). It no longer checks a link that is ready right after bonding, which the rule now forbids.
  - Host 2's "no other report received" check still rejects early keys (F/tests/bsim/control/host_app/src/main.c:215).
  - G lost one check: new fault 9.

**b. Lock order found in the code (by reading).**
- glue `lk` before screens `lk` (GLUE:72 then RSCR:169, and GLUE:46 then RSCR:136).
- screens `lk` before the devices and iPhone locks (`load_view`, RSCR:52-73).
- `draw_lk` before screens `lk` (RSCR:340 then RSCR:273), and `draw_lk` before the iPhone lock (RSCR:295-301).
- `sign_lk` before screens `lk` (RSCR:400 then :402).
- The screens thread takes the glue lock only in `ops->power_off`, with no screens lock or `draw_lk` held (RSCR:451-455). The devices callbacks run after the devices lock is released (RDEV:434-449).
- I found no lock cycle. The one wait cycle runs through the sign semaphore, not a mutex (new fault 4).
- Stale read: the window is now one core step (new fault 5). Before, it was until the next writer.

**c. `rscr_sign_start` waiting 5 s.**
- On timeout it returns -ETIMEDOUT but the request stays queued and is drawn later. It can poison the next call (new fault 1).
- From the screens thread it waits for itself for 5 s (new fault 3).
- The screens lock cannot be held by an outside caller. With `draw_lk` held it times out. With the glue lock held it works unless the thread is in a power off (new fault 4).

**d. Power off queued.** Yes, other core steps can run between RSCR:116 and RSCR:454: input, tick, battery and VBUS events. If one leaves STANDBY, the power off is dropped (state_table.inc:21). During a recording that is the safe result. Otherwise the wearer's confirmed power off is lost silently (new fault 6).

**e. Picture checks.**
- No two of the 21 scenes share every key text (REFS:69-172, by reading). The cross check proves the 21 sets tell the 21 captured frames apart (LOG:2208).
- Weakest scene: `recording-idle` has one reference, the dim timer (REFS:87-89). A frame with that timer and no red dot passes the scene. The separate red-dot count catches it (TDRAW:537).
- `message` and `message-battery-low` also have one reference each (REFS:167-172).
- `scene_ok` reads only the listed regions (REFS:205-213). A wrong screen outside the 21 can pass. Example: the five-item menu passes the `menu` scene, whose three rows (REFS:73-77) are the same in both.
- The reference text is drawn by the screens' own helpers (DRAW:635-650), so a fault in those helpers is in both. NOTES:24 says so.
- TDRAW:569-572: the second highlight may also move the timer. Cannot tell whether the count alone would fail the scene there.

**f. Recording safety.**
- By reading, no round 2 change starts or stops a recording.
  - B15 acts only outside RECORDING (LOGIC:616).
  - The double press shows SCR_RECORDING in RECORDING (LOGIC:671-673).
  - Power off has no RECORDING row.
  - The fact refresh feeds only `screen_on`.
  - ring_devices does not touch the core.
- Dark screen while recording: SCR_REC_DIM now runs at 85 (closed 1).
- Two latent paths remain:
  - An LVGL allocation failure in the smaller pool (new fault 10).
  - A failed `rscr_start`, which still lets a recording run with no sign (finding 11).
- Block: a future `rscr_sign_start` call can stall the glue for up to 5 s (new faults 3 and 4).

**g. False or overstated claims.**
1. NOTES:14: LOG:2474 cited for the chip's clean manifest. It is the repeat fake ("bad: 21"); the right line is LOG:2637.
2. NOTES:14 cites F/build-logs/step4/pictures-compare.txt for "all 42 files byte-identical". That file is from 14:59, round 1 (EV/files-check.out). The round 2 file is r2-pictures-compare.txt. Its content agrees, and all 21 LOG hashes are in the delivered manifest (EV/files-check2.out).
3. NOTES:38: "the R-SIGN ones are 1, 2, 10, 11, 12 and 14". Copy 11 is the passkey digit, and copy 9 (brightness 0) is missing from the list.
4. NOTES:64 lists 21 stage names for "22 stage lines". `stack-report` (LOG:1303) is missing. `pictures-fakes` ran before the chip tests (LOG:2476 before LOG:2506), not where the list puts it.
5. NOTES:65: "the 48 KB LVGL pool" is stale. It is 16 KB now (F/app/prj.conf:59).
6. NOTES:166, the proposed rule text, says "a message 3 s". It leaves out the 5 s B15 message that FW:353 now has.
7. R2 point 16: "I added no kit text to any log" is false for r2-sym.out:8-17 (new fault 11).
8. R2 point 6: power off "on the screens thread". The test checks only "not the caller's thread" (TDRAW:989).
9. R2 point 7.5: the third-pairing check in G does not exist (new fault 9).
10. R2 point 11: "the build showed 1,536" for BT RX is not found in the round 2 outputs (unverified).

## 6. What I could not check

- The commit id 844a6d5: I ran no git.
- Any run-time behaviour beyond LOG: no build or simulation was allowed. New faults 1 to 6 and 10 are by reading.
- Whether a real panel shows level 85 visibly. No panel driver exists.
- The lead's ruling that finding 11 and the recorder call wait for step 6: I saw R2's statement, not the ruling.
- The ring_devices printk lines of test B are not in LOG (only CHECK lines are copied). So "the new device's link ends right after the bonding" is by reading (RDEVL:131-132), not seen in a log.
- LVGL's behaviour on a failed allocation: I did not read LVGL source (kit code).

## 7. Evidence files (EV)

start.txt, logs-ls.out, cites-log.out, cites-files.out, stages.out, broken-screens.out, broken-all.out, rdev-grep.out, callers.out, fw-greps.out, fw-lines.out, logic-enter.out, confirm.out, fakes-stage.out, files-check.out, files-check2.out, misc1.out, misc2.out, devscene.out, g-lines.out, lines-final.out, bsim-B.out, mtimes.out.

RESULT: done, of 15 findings 10 are closed, 4 partly closed (9, 11, 12, 15) and 1 open (14), and round 2 brings 13 new faults, the heaviest being that a timed-out rscr_sign_start leaves its request queued so the recording sign can appear later with a stale start time.
