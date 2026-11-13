# Step 4 review: the screens

Version judged: the files on disk under firmware/ on 2026-11-12 from 15:05 CET, which the lead names commit f82e7a5. I ran no git, so I could not confirm that id. The builder's notes name the design version f12c0d6 (F/docs/screens-notes.md:3). No file under F/modules, F/app, F/tests or F/tools is newer than the start of the builder's final run (11:55:40); the newest is F/tests/screens/src/test_table.c at 11:55:34 (EV/mtimes.out). I ran no build, no simulation, no ssh and no browser. Statements about run time come from LOG or LEAD, from my own scripts on the delivered pictures (EV/matrix.out), or are marked "by reading".

Short names:
- F/ = firmware/
- LOG = F/build-logs/20261112-115540-os-screens.log (the builder's final run; F/build-logs/step4/20261112-115540-os-screens.log is a byte-identical copy, cmp printed nothing).
- LEAD = F/build-logs/20261112-150252-lead-step4-rerun.log (the lead's rerun).
- PICS = design/software/os/screens/
- FW = design/firmware.md
- LOGIC = F/modules/ring_screens/src/rscr_logic.c, RSCR = F/modules/ring_screens/src/rscr.c, DRAW = F/modules/ring_screens/src/rscr_draw.c, MEMD = F/modules/ring_screens/src/memdisplay.c, REAL = F/modules/ring_screens/src/rscr_real.c, GLUE = F/modules/ring_glue/src/rglue.c
- TDRAW = F/tests/screens/src/test_draw.c, TTAB = F/tests/screens/src/test_table.c, RING = F/tests/bsim/screens/ring_app/src/main.c
- EV = my evidence folder, outside the project: <scratch>/ev/ (probe scripts in its sibling folder probe/). These are session files and may not last.

## 1. The bar, point by point

**a. Every screen drawn by the screen code on the simulated display, read back from the frame the driver received, saved with a manifest: met.**
- LVGL draws each screen (DRAW:527-630). The flush turns each area and calls `display_write` (DRAW:43-67, :63). The memory display stores what it receives (MEMD:55-82, fb at MEMD:18).
- The test reads that memory back (F/modules/ring_screens/src/rscr_capture.c:25-44) and saves it (TDRAW:337-354). No script draws a picture.
- 21 pictures, 42 SCREENPIC lines in LOG (21 per board, EV/pics.out). PICS holds 43 PNG files: 21 at 240 x 120, 21 at 960 x 480, and all-screens.png. Every one of the 42 matches the server sha256 list (EV/pics-sha-compare.out). PICS/manifest.md has 23 lines: a header, a rule line and 21 picture lines.
- Weak spot: the read-back ignores blanking and brightness. MEMD:106-114 only stores the brightness value. A picture shows what was written, not what a panel would show (see question 1).
- Weak spot: the stage check counts picture lines, not the 21 expected names (F/tools/pictures_manifest.py:18 `MIN = 20`, :59, :92). I ran the real tool on two fake inputs: a log and folder with the pairing picture missing (20 pictures), and a log of 21 lines that all name the status picture. Both ended `bad: 0` with exit 0 (EV/manifest-fakes.out). So a run that loses one scene, or repeats one, passes the pictures stage.

**b. Each picture checked by a test that can fail (a blank frame or another screen's frame fails it): partly met.**
- I copied the region checks of TDRAW by hand into EV/../probe/matrix.py (a stand-in for the test, not the test). I ran each picture's checks on all 21 delivered pictures, a blank frame, a full white frame and a flat grey frame (EV/matrix.out).
- Honest control: every picture passes its own checks (21 of 21, EV/matrix.out). This matches LOG:2207 (`screens_draw` 10 of 10).
- Blank frame: it fails all 21 check sets.
- Another screen's frame passes every check in 13 of the 21 sets: status (notifications-empty, charging), settings (4 others), recording (recording-highlight), recording-highlight (8 others), notifications-empty (11 others), notification (6 others), modes (4 others), control-media (control-presenter), control-presenter (control-media), control-pointer (8 others), device (3 others), pairing (3 others), message (17 others). A full white frame passes 6 sets (recording-highlight, notifications-empty, notification, control-pointer, pairing, message).
- Many scenes also assert the logic state `s.screen` (for example TDRAW:431, :510, :596). That catches a wrong table, not a frame that shows the wrong picture.
- The notes' sentence "a frame of another screen fails the region it lacks" (F/docs/screens-notes.md:17) is false for those 13 sets.

**c. The pure screen table is tested for every screen and every joystick action, and agrees with FW 1.2, 2.2, 3.2, 3.3, 3.4: partly met.**
- Coverage met. `rows[]` (TTAB:135-265) has 112 rows (EV/table-count.out; LOG:2202 `rows checked: 112`). By reading, each of the 17 screens listed in the notes has all five actions. SCR_RECORDING and SCR_REC_DIM are covered by TTAB:900, SCR_RECOVERY and SCR_FACTORY by TTAB:927. The rows feed `RC_ACT_SCREEN_*` straight in (TTAB:285). The lock, the session and the gestures come from the real core in the rig tests (TTAB:366-479).
- Rows where code and rules disagree (by reading):
  1. SCR_STATUS Up opens SCR_NOTIFS (LOGIC:256-258, TTAB:137). FW:283 says "none". This is deviation 4, a proposal for the lead.
  2. SCR_NOTIFS and SCR_NOTIF rows (TTAB:246-264) have no rule in FW.
  3. SCR_REC_DIM is driven at panel brightness 0 (RSCR:307). FW:338 says "at the lowest of the three levels of the setting" and FW:352 says "lowest brightness level". This code's lowest level is 85 (RSCR:307: 85 + 85 x level).
  4. SCR_PAIR stays on for 60 s (LOGIC:154-156). FW:277 says every screen turns off 5 s after the last input. Deviation 7, declared.
  5. A double press in a session closes it, but SCR_MODES is shown only when the screen was SCR_CONTROL (LOGIC:171-179). With the panel off in a session, the session closes and the panel stays dark. FW:380 says the double press "shows SCR_MODES".
  6. Battery B15 in STANDBY: `RC_ACT_SCR_STATUS_5S` jumps to SCR_STATUS from any screen (LOGIC:593-596). From SCR_PAIR it does not close the pairing window (no `leave_pair`). From SCR_CONTROL the session stays open, so the next direction goes to the device (lock fact true) and also acts on SCR_STATUS: Right or Centre opens the menu, Up opens the list (LOGIC:255-264). FW:379 says that in a session the keys "do nothing else on the ring".
  7. "Power off" Yes (LOGIC:408-410) sends `RC_EV_MENU_POWER_OFF`, whose only row is in STANDBY (F/modules/ring_core/src/state_table.inc:21). In ERR_BATTERY_LOW and ERR_STORAGE_FULL the wake shows SCR_STATUS (LOGIC:146-147), the menu opens, and Yes does nothing but show SCR_STATUS. FW:293 says Centre on SCR_CONFIRM is "Yes".
  8. MT tick (FW:324 "only when screen is on"): with the new lock fact the core gives no MT for the first direction on the lit SCR_REC_DIM, and gives MT for a direction with the panel off in a session (F/modules/ring_core/src/core.c:192-203). See question 3.
  9. FW:148 (long press, sign not drawn) and FW:339 (one code path before VDD_MIC): not built. `rscr_sign_start` has no caller outside the test (EV/greps3.out). Declared in notes section 5.
  10. Declared and not built: the 3.3 fields not drawn (deviation 6), two fonts ruled but four used (F/docs/screens-notes.md:65), device names (deviation 10), SCR_FACTORY "reported to the jig" (LOGIC:485-487), and the SCR_ERROR times of 10 s and 5 s (F/modules/ring_screens/include/ring_screens/rscr_logic.h:71-72), which no rule states.

**d. One two-device test over Bluetooth on the simulated chip drives pairing, a notification, its detail and a dismiss through the screens: met, with gaps.**
- RING:188-249 drives every step with `rglue_input` edges (RING:125-131). Menu to SCR_PAIR and the real pairing window (RING:207). Passkey, then paired and active (RING:214). The empty list, the notification, the list frame change (RING:233), the detail (RING:236) and the dismiss through ring_iphone (RING:241). The stand-in received the negative action for 201 (LOG:8508). `TEST S RESULT PASS (33 checks passed)` (LOG:8512).
- Gaps: the digits on the screen are never compared with the passkey; only the frame hash changes (RING:212). Only one device pairs, so the switch-back of deviation 8 never runs over Bluetooth (RING:166-169 expects slot 0).

**e. Each broken copy fails on its own named check, for the fault it plants; R-SIGN has one copy at the logic layer and one at the drawing layer: partly met.**
- All 12 copies end with their named case failing (LOG:9174, :9189, :9213, :9237, :9267, :9288, :9310, :9342, :9372, :9394, :8580, :8640, :8702). Every copy built and ran (EV/broken-lines.out).
- The assertions that fire match the fault for 11 copies: rsign_dark at TTAB:730 `sign_check` (LOG:9164); lock_open at TTAB:487 (LOG:9229); double_ignored at TTAB:539 (LOG:9256); long_closes_session at TTAB:616 (LOG:9281); first_device_moved at TTAB:686 (LOG:9303); down_stuck at TTAB:292, the selection (LOG:9330); dismiss_key at TTAB:295, the effect kind (LOG:9361); passkey_not_drawn at TDRAW:834 (LOG:9386). The three bsim copies fail their own check lines (LOG:8580, :8640, :8702).
- rsign_blank_panel (the drawing-layer copy) does not fail on its fault. Its edit (F/tests/screens/broken_edit.py:22) makes `want_on` false for SCR_REC_DIM, so the frame is also not drawn. The case fails at TDRAW:512, the red-dot count on a stale frame (LOG:9203). It never reaches the "never blanked" assertion at TDRAW:543. So no copy shows that TDRAW:543 can fail, and no copy and no test covers the brightness path (no test reads `.brightness`, EV/greps3.out).
- Copies 7 and 8 share one case (said in the notes). Several copies fail more than one case: rsign_dark 4 (LOG:9171), down_stuck 6 (LOG:9339), double_ignored 5 (LOG:9264), dismiss_key 5 (LOG:9369). Each extra failure follows from the same planted fault.

**f. The whole build and test command ends with RESULT PASS and every earlier stage still passes: met (LOG, and LEAD up to its last build_all line).**
- LOG: 20 lines `=== stage ... end ... exit 0` and none with another exit (EV/stages.out), `RESULT PASS` at LOG:9460, `# remote exit code: 0` after it.
- Step 1 to 3 stages are among them: tests-native_sim (LOG:2144), bsim-control (LOG:3251), bsim-iphone (LOG:5404), the broken stages (LOG:8794 to :9458). `308 of 308` on both boards (LOG:2137, :2268).
- LEAD at 15:12: 3,518 lines. Stages up to bsim-control ended with exit 0 (LEAD:1259 to :3251). Then it was inside bsim-control-broken, where the failing lines are the planted faults that stage expects (LEAD:3424, :3506).
- LEAD at 15:48: 9,460 lines, 20 stage end lines, all `exit 0`, none other (EV/lead-now.out). Last build_all line `RESULT PASS` at LEAD:9460. Pictures `listed: 21, bad: 0` on both boards (LEAD:2244, :2375). `TEST S RESULT PASS (33 checks passed)` at LEAD:8512; the three `TEST S RESULT FAIL` lines (LEAD:8579, :8639, :8701) are the planted bsim copies. At 15:48 the remote.sh trailer line `# remote exit code` was not yet in the file, so I did not see the remote exit code.

## 2. Answers to the questions

**1. R-SIGN.**
- Table layer, by reading: no path sets SCR_OFF while the state is RECORDING.
  - Entry to RECORDING shows SCR_RECORDING and closes pairing (LOGIC:511-517).
  - In RECORDING `arm_idle` arms only the dim timer (LOGIC:112-114). The off timer is skipped (LOGIC:715-720).
  - Directions show SCR_RECORDING (LOGIC:626-632). The wake goes to SCR_RECORDING (LOGIC:132-133).
  - Messages keep the dot and the timer: `rscr_has_sign` (LOGIC:85-88) and the drawing (DRAW:433-439). After a message the screen goes back to SCR_RECORDING (LOGIC:690-692).
  - A double press shows SCR_RECORDING (LOGIC:644-649). A session timeout or a device removal calls `close_session`, which changes the screen only from SCR_CONTROL (LOGIC:171). That screen cannot be shown in RECORDING (LOGIC:132-133, :626).
  - Pairing callbacks act only on SCR_PAIR (LOGIC:741, :759). The refresh acts only on SCR_NOTIF, SCR_DEVICE and SCR_CONFIRM (LOGIC:656-667), which RECORDING never shows. The 1 s pass draws every screen other than SCR_OFF (RSCR:306-309, :364, :391).
- Panel layer: not met.
  - SCR_REC_DIM sets the panel brightness to 0 (RSCR:307, DRAW:93). On an OLED, brightness 0 is the darkest setting, and FW:338 asks for the lowest of the three levels. By reading, the dimmed sign may be unlit on a real panel for most of every recording.
  - The memory display ignores brightness (MEMD:106-114). No test reads it. So the picture recording-idle and TDRAW:512-515 cannot see this.
- Other dark paths:
  - If `rscr_start` fails, `rscr_glue_after` returns true and draws nothing (RSCR:122-124). The product only prints and goes on (F/app/src/main.c:104-109). The ring would then record with no screen.
  - A failed draw is counted (RSCR:310-313) and nothing else happens.
  - `rscr_sign_start` draws on its caller's thread while the screens thread may be in LVGL (RSCR:347-349). LVGL has no lock here (question 5). Today only the test calls it.
- The dimmed picture is really drawn: dot and timer at DRAW:230-233, red dot at DRAW:160-167, checked at TDRAW:512-515 (240 lit px in PICS/manifest.md).

**2. Recording safety.**
- By reading, nothing in the screens part, and nothing that reaches it, can start or stop a recording.
  - `rglue_event` has one caller: REAL:93 sends `RC_EV_MENU_POWER_OFF` (EV/greps3.out). Its only row is STANDBY to OFF (state_table.inc:21). The effect comes only from SCR_CONFIRM Centre (LOGIC:404-414), and in RECORDING no direction reaches `nav` (LOGIC:626-632).
  - `rglue_set_vibration` writes only `vibration_on` (GLUE:134-139). The core uses it only to drop MH and MT (F/modules/ring_core/src/state_actions.c:14).
  - `after` and `lock_fact` write only `screen_on` (GLUE:37, :114-119). The core reads `screen_on` only in `screen_input` and row 16 (core.c:195, state_actions.c:79). A long press goes to `sm_event` directly (core.c:225-226).
  - Notifications, media, device events and timeouts reach only `rscr_poke`, `rscr_refresh`, the rdev callbacks and `rscr_tick`. Their effects are control active, device use, pair cancel and dismiss (RSCR:65-110). None calls the core.
- Two side issues:
  - `rglue_event` is a public entry that takes any event (F/modules/ring_glue/include/ring_glue/rglue.h:57-59), so the rule rests on its callers.
  - FX_POWER_OFF runs inside `dispatch` (RSCR:131 runs under the glue lock held at GLUE:91-95). The nested step's `screen_on` is then overwritten by the outer return value at GLUE:37.

**3. Deviation 9 (the meaning of `screen_on`).** The core reads the fact in two places (core.c:192-203 and state_actions.c:78-85, row 16 = FW:149). Changes that step 1's tests do not see (they set the fact directly):
- (a) RECORDING with SCR_REC_DIM lit: the fact is false, so a direction gives only `RC_ACT_SCREEN_ON`, with no MT. Under the old meaning (panel lit) it gave the screen action and MT. FW:324 gives MT whenever the screen is on.
- (b) A session with the panel off: the fact is true, so a direction gives the screen action and MT with the panel dark. MT plays with the screen off, against FW:324.
- (c) Row 16 (STANDBY short press, FW:149) in a session with the panel off: `SCREEN_CENTRE` and MT, instead of "screen on, status screen, 5 s". This is the R17 exception, so it is intended.
- (d) The fact now has writers outside a core step (RSCR:388-390, :149-151, :180-182, :207-209). A stale value can overwrite a newer one (question 5).
- Rows touched: the direction path of FW 2.2 (lock), row 16 (FW:149), and the MT rule of FW 3.1.

**4. Deviation 8 (switch back after pairing).** By reading F/modules/ring_devices/src/rdev.c:
- What it costs:
  - `on_pairing_complete` makes the new device active and saves it (rdev.c:420, :424). It then calls `paired` (rdev.c:435-437), which runs `rscr_on_paired`, then `rdev_switch(old)` (RSCR:172-179, REAL:71-74). That sets the old device active and saves again (rdev.c:605-623). This is a second settings write.
  - Back in `on_pairing_complete`, `active_changed(new)` still fires (rdev.c:438-440). It now names a device that is not active.
  - `update_fn` then sees the link on the new slot while the active slot is the old one, and disconnects the device that has just bonded (rdev.c:199-206). It then advertises for the old device, which must reconnect.
  - So each later pairing costs the new phone's link right after bonding, two settings writes and a reconnect of the old device.
- Wrong-device window: keys go out only while control is active, that is in a control session (GLUE:22-23). By reading, a session cannot be open while SCR_PAIR is shown (SCR_CONTROL ignores navigation, LOGIC:367-370). The one way is case 6 of bar c: B15 leaves SCR_PAIR with the window still open. Even then, the time from rdev.c:420 to the switch is one synchronous call chain, and after it the link is to a slot that is not active.
- I did not check what ring_control sends in that window. Not tested over the air (bar d).

**5. Threads.**
- State touched from two contexts without protection, by reading:
  - `pair_prev_active` (RSCR:29): written at RSCR:79 outside `lk`, in the glue's or thread's context. Read and written at RSCR:172-173 under `lk`, in the Bluetooth callback context.
  - LVGL and everything `render` uses: `frame` (RSCR:35), `panel_on_state`, `panel_level` (RSCR:30-31), `stats` (RSCR:23), `flush_err`, `vdb`, `rot` (DRAW:39-41). The screens thread uses them (RSCR:391), and so does `rscr_sign_start` on its caller's thread (RSCR:347-349).
  - `batt_*` (RSCR:24-26): written by `rscr_set_battery` (RSCR:230-233), read at RSCR:284-287.
  - `dev_names` (RSCR:27): `memset` plus `strncpy` at RSCR:240-242 against the `memcpy` at RSCR:288. A torn name can be drawn.
  - `gen_asked` (RSCR:399): `++` from any caller of `rscr_sync` (tests only).
  - `stats` is read without a lock (RSCR:257).
  - The fb of the memory display is read without the spinlock by `rmd_hash` and the capture (MEMD:23-26, :44-53), while the thread writes it under the spinlock (tests only).
  - The core fact `screen_on`: each write holds the glue lock, but the thread computes the value under its own lock and writes it later (RSCR:385-390). A newer value from `dispatch` (GLUE:37) can be overwritten by an older one. Same for RSCR:146-151, :177-182, :204-209.
  - The screens thread waits on the glue lock in `lock_fact` before it draws (RSCR:388-391). While the glue holds that lock in a blocking HID send (F/modules/ring_glue/include/ring_glue/rglue.h:16-19), the timer and the dim step are not drawn.
- Stacks that look tight (not measured; the logs hold no stack or LVGL memory figures, EV/mem.out):
  - The glue thread, 2048 by default (F/modules/ring_glue/Kconfig; F/app/prj.conf does not set it). It now also runs `rscr_glue_after`, `load_view` with a 283-byte `rinbox_item` on the stack (RSCR:53; F/modules/ring_inbox/include/ring_inbox/rinbox.h:40-50), `apply_fx` into ring_devices and ring_iphone, and a nested `rglue_event` core step.
  - The Bluetooth RX context now runs `rscr_on_paired`: `load_view`, then `rdev_switch`, its callbacks, `rscr_poke`, `after_async` and a second `load_view`. F/app/prj.conf sets no BT RX stack size.
  - The screens thread is 8192 in F/app/prj.conf, but the Kconfig default is 4096 (F/modules/ring_screens/Kconfig) for any build that does not set it.

**6. The 21 picture checks: (i) blank, (ii) another screen, (iii) wrong key text.** (i) and (ii) are measured in EV/matrix.out with the stand-in copy of the checks. (iii) is by reading TDRAW.
| Picture | (i) blank fails | (ii) another screen fails | (iii) wrong key text fails |
|---|---|---|---|
| status | yes | no: notifications-empty, charging pass | no: any time passes (TDRAW:405); the hash only shows a change (:416) |
| menu | yes | yes | highlighted row: yes, rows 0 and 1 (:433-435, :442-445); item text: no |
| settings | yes | no (4 pass) | row 0 highlight: yes (:480); value text: no |
| recording-idle | yes | yes | timer: no, lit count only (:513) |
| recording | yes | no (recording-highlight passes) | timer: no (:525) |
| recording-highlight | yes | no (8 pass, white frame too) | count: no, lit count only (:539) |
| notifications-empty | yes | no (11 pass, white frame too) | "None": no (:598) |
| notifications | yes | yes | highlighted first row: yes (:608); titles: no |
| notification | yes | no (6 pass, white frame too) | title and message: no; button present or absent: yes (:623, :631) |
| modes | yes | no (4 pass) | Media row highlight: yes (:669) |
| control-media | yes | no (control-presenter passes) | title or state: changes only (:704, :709); wrong title: no |
| control-presenter | yes | no (control-media passes) | no |
| control-pointer | yes | no (8 pass, white frame too) | no |
| control-agent | yes | yes | colour and side of Decline and Accept: yes (:728-729) |
| devices | yes | yes | active pill and cursor position: yes (:768-771); names: no |
| device | yes | no (3 pass) | Use highlight: yes (:784); name: no |
| confirm | yes | yes | question text: no (:792) |
| pairing | yes | no (3 pass, white frame too) | wrong digit: no; any passkey passes (:833-844) |
| charging | yes | yes | percent: no (:864) |
| message | yes | no (17 pass, white frame too) | text: no (:873) |
| message-battery-low | yes | yes | another amber message passes (:883) |

**7. Public release rule.**
- New and changed code: no copyright or licence lines from another party in F/modules/ring_screens, F/modules/ring_glue, F/app, F/tests/screens, F/tests/bsim/screens, F/tools/pictures_manifest.py or F/tools/build_all.sh (EV/q7-scan.out). No font, image or binary file was added under ring_screens, tests/screens or tests/bsim/screens. By reading, MEMD follows the shape of the display API, not the text of display_dummy.c (compare MEMD:55-149 with F/build-logs/step4/probe2.out:42-125).
- Names on screen: the static strings of DRAW and LOGIC hold no company or product name (EV/q7-scan.out; the two hits are comments). But a notification with no title shows its app identifier (DRAW:476, :503). For an iPhone message that is "com.apple.MobileSMS" (the test data at TDRAW:601 and F/tests/bsim/screens/host_app/src/main.c:1221). That is data, not artwork, but the notes' "no ... product name is drawn" (F/docs/screens-notes.md:58) holds only while a title exists.
- Logs that hold kit source text at length:
  - F/build-logs/step4/probe2.out and F/build-logs/step4/20261112-102620-probe2.log (802 lines each). They hold Zephyr's display_dummy.c (Copyright Nordic Semiconductor, probe2.out:10-11), zephyr,dummy-dc.yaml (:144), modules/lvgl/lvgl.c (:152-554) and lvgl_display.c (:555-705).
  - F/build-logs/step4/probe2.sh is the script that printed them.
  - F/build-logs/step4/audit-output.txt has one `#include <zephyr/...>` line (line 455). That is not kit source.

**8. The notes' citations.**
- I checked 61 cited numbers: 35 log lines (EV/cites-log.out) and 26 file lines (EV/cites-files.out, EV/lines2.out). All 61 are right.
- False or overstated claims:
  1. F/docs/screens-notes.md:17 "a frame of another screen fails the region it lacks": false for 13 of 21 pictures (bar b).
  2. F/docs/screens-notes.md:36, copy 2 "the panel is blanked ... (drawing layer)": the copy also stops the drawing and fails on the red-dot pixels (LOG:9203), not on the blanking check (bar e).
  3. F/docs/screens-notes.md:75 and :105: the dimmed picture is said to follow 3.2 and brightness to have 3 levels. Not said: SCR_REC_DIM is driven at brightness 0 (RSCR:307), against FW:338.
  4. F/docs/screens-notes.md:102 "That costs a link change": it disconnects the device that has just bonded, makes two settings writes and fires a stale `active_changed` (question 4).
  5. F/docs/screens-notes.md:57 "rscr.c ... draws on its thread": `rscr_sign_start` draws on the caller's thread (RSCR:349).
  6. F/docs/screens-notes.md:58 "No other company's logo or product name is drawn": not while a notification has no title (question 7).
  7. F/docs/screens-notes.md:17 "test_04 ... waveform pixels": true. But TDRAW:527-535 computes a hash "a second later the lines differ" and never compares it (`(void)h`, :534).

**9. Memory.**
- From the configuration and the code (by reading; nothing was measured):
  - Frame memory of the memory display: 57,600 bytes (120 x 240 x 2, MEMD:18). The product will not need it once the SH8501A driver exists, since the panel keeps its own picture. It is the largest item.
  - LVGL pool: 49,152 bytes (`CONFIG_LV_Z_MEM_POOL_SIZE`, F/app/prj.conf). By reading, the busiest screen makes a few dozen objects, a few kB. The logs hold no LVGL memory figure, so whether 48 KB is needed is unmeasured. It looks larger than needed.
  - Draw buffers: `vdb` 11,520 bytes and `rot` 11,520 bytes (240 x 24 x 2 each, DRAW:40-41).
  - Screens stack: 8,192 bytes (F/app/prj.conf).
  - `frame.inbox`: 16 copies of `rinbox_item`, about 4,528 bytes (RSCR:35, F/modules/ring_screens/include/ring_screens/rscr_draw.h:32). This duplicates the inbox.
  - Waveform points: about 2,280 bytes (DRAW:178).
- These sum to 144,792 bytes. The difference between the two reports is 146,320 bytes (197,584 at LOG:945 minus step 3's 51,264), so 1,528 bytes are left (EV/ram-sum.out).
- Unverified: whether Zephyr's lvgl.c keeps its own static draw buffer when `CONFIG_LV_Z_AUTO_INIT=n` (probe2.out:200-265 shows the buffer behind `CONFIG_LV_Z_BUFFER_ALLOC_STATIC`). The map file would show it.

## 3. Findings, heaviest first

1. **The dimmed recording sign is sent at brightness 0.** Where: RSCR:307, DRAW:93; the rule is FW:338 and FW:352. What it causes: on a real panel the sign may be unlit from 3 s after each input to the end of the recording. That breaks R-SIGN for most of every recording. The memory display and every test are blind to it (MEMD:106-114, EV/greps3.out). Fixed when: SCR_REC_DIM uses the lowest setting level (85 here, or a measured visible level), and a test reads `rmd_stats.brightness` in SCR_REC_DIM and fails on 0. Also a broken copy that sets the level to 0 must fail that test.
2. **Picture checks accept other screens' frames.** Where: TDRAW region checks; EV/matrix.out. What it causes: 13 of 21 pictures would pass if the screen code drew another screen, and 6 would pass a full white frame. No check reads a digit, a timer or a passkey value. Fixed when: each scene also fails on every other scene's frame (a cross check like EV/../probe/matrix.py run in the suite), and the key values (time, timer, passkey, percent) are compared, for example against a frame drawn from the expected text.
3. **The drawing-layer R-SIGN copy does not test blanking.** Where: F/tests/screens/broken_edit.py:22; LOG:9203. What it causes: the "never blanked" assertion (TDRAW:543) has never been seen to fail, and the brightness path has no copy. Fixed when: one copy blanks the panel but still draws (for example `rscr_panel(false, ...)` after the draw in SCR_REC_DIM) and fails at TDRAW:543, and a second copy sets brightness 0 and fails the new test of finding 1.
4. **The pictures stage accepts a missing or repeated picture.** Where: F/tools/pictures_manifest.py:18, :92. What it causes: a run with 20 of the 21 scenes, or 21 copies of one, passes (EV/manifest-fakes.out, both fakes exit 0). Fixed when: the tool requires each of the 21 expected names exactly once, and the two fakes above exit 1.
5. **The screens draw from two threads.** Where: RSCR:347-349 against RSCR:391. What it causes: once the recorder calls `rscr_sign_start` (the one R-SIGN path of FW:339), it runs LVGL and `render` alongside the screens thread with no lock. That can corrupt LVGL state or the panel state at the start of a recording. Fixed when: `rscr_sign_start` hands the draw to the screens thread and waits for its result, or a draw lock covers `render`. A test then calls it while the thread draws.
6. **Lock fact races and a re-entrant core step.** Where: RSCR:385-390, :146-151, :177-182, :204-209 against GLUE:37; REAL:93 inside GLUE:29-38. What it causes: a stale `screen_on` can overwrite a newer one, so the next press is swallowed as a wake or acts without a wake. Power off runs a nested core step whose fact is then overwritten. Fixed when: the fact is computed and stored under one lock (or read by the core from the screens part when needed), and power off is queued to run after `dispatch` returns.
7. **Deviation 8 drops the new device's link.** Where: rdev.c:420-440 with RSCR:172-179 and rdev.c:199-206. What it causes: each later pairing ends with the new phone disconnected right after bonding, two settings writes and a stale `active_changed(new)`. Not tested over the air. Fixed when: ring_devices keeps the old active slot on a later pairing (owner: ring_devices) and a bsim scenario pairs a second device and checks that the first stays active and linked.
8. **Session and status rows against 3.4.** Where: LOGIC:593-596 (B15 status from SCR_PAIR or SCR_CONTROL) and LOGIC:171-179 (double press with the panel off). What it causes: a pairing window stays open off-screen; keys in an open session both go to the device and act on SCR_STATUS; a double press with the panel off closes the session but shows nothing. Fixed when: B15 status does not leave SCR_PAIR or SCR_CONTROL (or closes both properly), the double press always shows SCR_MODES in STANDBY, and rows for these cases are in TTAB.
9. **Power off from the menu does nothing in ERR_BATTERY_LOW and ERR_STORAGE_FULL.** Where: LOGIC:408-410, state_table.inc:21. What it causes: the wearer confirms "Power off" and the ring stays on. Fixed when: the menu hides Power off outside STANDBY, or the lead rules a row for those states, and a test covers it.
10. **MT tick follows the lock fact, not the panel.** Where: core.c:192-203 with LOGIC:78-83. What it causes: no tick on the first direction from the lit SCR_REC_DIM; a tick with the panel off in a session (FW:324). Fixed when: the lead rules which fact MT follows, and a test checks MT in both cases.
11. **No screen means no sign, silently.** Where: RSCR:122-124, F/app/src/main.c:104-109. What it causes: if LVGL or the display fails to start, every core step reports the screen as lit and recordings start with nothing on the panel. Fixed when: a failed `rscr_start` blocks recording (the FW:148 row) and a test starts the product with the display not ready.
12. **Stacks not measured.** Where: glue 2048 (F/modules/ring_glue/Kconfig) with the new work in its thread; the BT RX context running `rscr_on_paired`. What it causes: possible overflow in the product, not seen in simulation. Fixed when: a thread analyzer run of the two-device test reports the peak use of glue, BT RX and screens.
13. **Unprotected small state.** Where: RSCR:24-27, :29, :240-242, :288. What it causes: torn names or battery values on the screen, and a stale `pair_prev_active`. Fixed when: they are written and read under `lk`.
14. **Kit source in step 4 logs.** Where: F/build-logs/step4/probe2.out, F/build-logs/step4/20261112-102620-probe2.log. What it causes: about 700 lines of Zephyr and Nordic source in files that may be published. Fixed when: they are left out of the public copy or cut to the listing.
15. **Memory larger than needed.** Where: MEMD:18 (57,600 bytes), F/app/prj.conf LVGL pool 49,152 bytes, RSCR:35 inbox copy. What it causes: the first two alone are 106,752 bytes, over half of the 197,584 bytes of RAM the kit build uses (LOG:945). Fixed when: the panel driver replaces the memory display in the product, and the LVGL pool is sized from a measured peak.

## 4. Notes that agree with the code

- By reading, deviations 1 to 13 are each visible where the notes say (for example 1: REAL calls no `rip_media_command`; 11: About shows a fixed "0.1", DRAW:572; 13: GLUE:29-38, :121-139). Deviations 4, 7, 8 and 9 change behaviour and need the lead's ruling.
- Section 6 of the notes reports the earlier runs. I read the two cited stage lines (F/build-logs/step4/os-screens-run.out:2150, os-screens-run2.out:2148, both `exit 1`, EV/cites-files.out).

## 5. What I could not check

- The commit id f82e7a5: I ran no git.
- Anything at run time beyond LOG, LEAD and my scripts on the delivered PNG files: I ran no build or simulation (the brief forbids it). So the brightness, race, stack and memory points are by reading.
- The region checks in EV/matrix.out are my hand copy of TDRAW, run on the delivered PNG files, not the test itself. Its own-picture control passes 21 of 21.
- What a real SH8501A shows at brightness 0. The panel driver does not exist.
- What ring_control sends during the switch-back window of question 4.
- Lock order beyond this: no other module calls an `rscr_` function (EV/callbacks.out), so ring_iphone's lock is only taken inside the screens' lock, not the other way round. The rdev callbacks I read run after rdev.c releases its lock (rdev.c:428-437, :625-638). I did not trace every Bluetooth callback path.
- Whether ring_core files changed in this step: the notes say no (F/docs/screens-notes.md:57). Without git I could not compare.
- The remote exit code of LEAD: not yet written at my last look (15:48, EV/lead-now.out).

RESULT: done, of 6 bar points 3 are met (a, d, f) and 3 partly met (b: 13 of 21 picture checks accept another screen's frame; c: 10 rule disagreements listed; e: the drawing-layer R-SIGN copy fails on stale pixels, not on blanking); the heaviest new issue is that the dimmed recording sign is driven at panel brightness 0, which no test can see.
