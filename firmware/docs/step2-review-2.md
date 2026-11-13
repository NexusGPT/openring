# Step 2 review 2: devices and control, after the round of fixes

Version judged: the files on disk on 2026-11-11 from 22:00 CET, content id "111abb1140cc6e9b" as written in firmware/build-logs/step2/lead-review2-version.txt line 1. I did not recompute that id (I do not know its recipe and I ran no git), so "the files on disk" is what I judged. I ran no build, no simulation, no git, no ssh. Every finding comes from reading the cited lines. Statements about run time come from the author's last run log, LOG = firmware/build-logs/step2/20261111-214828-r2-all3.log, or are marked "by reading". The author's notes were read last, only to find things.

Short names (every citation still gives the full path):
- PLAN = <home>/.claude/plans/clever-puzzling-grove.md
- FW = design/firmware.md
- R1 = firmware/docs/step2-review.md (the first review)

## 1. Bar items: met, partly met or not met by the code on disk

1. **Pairing with a passkey: met.** Display-only pairing callbacks: firmware/modules/ring_devices/src/rdev.c:398-402. Pairing only inside the window: firmware/modules/ring_devices/src/rdev.c:366. `CONFIG_BT_SMP_SC_ONLY=y`: firmware/app/prj.conf:24. Level 4 is now the gate: firmware/modules/ring_devices/src/rdev.c:346 and :739. The host reads the passkey the ring shows and checks level 4: firmware/tests/bsim/control/host_app/src/main.c:352 and :397.
2. **Three paired devices: partly met.** The code holds three: firmware/app/prj.conf:15-16 and firmware/modules/ring_devices/src/rdev.c:512-521. The Bluetooth proof still pairs two hosts only (firmware/tests/bsim/control/ring_app/src/main.c:295 and :303). A third bond and a refused fourth are proven in logic only (firmware/tests/devices/src/test_devices.c:18-23). Test B checks three local identities, not three bonds (firmware/tests/bsim/control/ring_app/src/main.c:327-330).
3. **Switching the active one: met.** firmware/modules/ring_devices/src/rdev.c:591-636. The send gate is the new pure rule firmware/modules/ring_devices/src/rdev_logic.c:153-156, used at firmware/modules/ring_devices/src/rdev.c:127.
4. **Keyboard, media keys and pointer in the three modes: met, with a fourth mode.** Tables: firmware/modules/ring_control/include/ring_control/rctl_modes.h:99-137. The fourth mode "agent" is still there (firmware/modules/ring_control/include/ring_control/rctl_modes.h:27 and :121-127); PLAN line 18 says three. The author now states it as a deviation (firmware/docs/devices-control-notes.md:138); the lead must decide.
5. **Proof, "a stand-in computer pairs with the ring and receives the right key for each joystick action in each mode": met.** Test A injects each action in each mode through the glue (firmware/tests/bsim/control/ring_app/src/main.c:223-241). The host compares report id, length and every byte against literals, in order, and fails on any extra report (firmware/tests/bsim/control/host_app/src/main.c:89-118 and :160-198). LOG line 1486: "TEST A RESULT PASS (76 checks passed)".
6. **Proof, "after a switch, the second stand-in receives the keys and the first receives none": met, with one weak spot.** Each host's list holds only its own phases (firmware/tests/bsim/control/host_app/src/main.c:121-131), and "no other report received" ends each list (:198). The switch window is now tested (firmware/tests/bsim/control/ring_app/src/main.c:318-320). The weak spot: that window check is on the ring's return code only. With the gate broken, host 1 still passed (LOG line 2280 "HOST H1 RESULT PASS"; it received 8 reports, LOG line 2279, the same as in the good run). So no host check can see a key that leaks to the old device in the window; see part 3, B.
7. **"A long press on the joystick's centre still starts and stops a recording in every mode": met for what is built.** One module carries the joystick to the core, to control and to the recording hook (firmware/modules/ring_glue/src/rglue.c:15-24). The product app runs it (firmware/app/src/main.c:73). Control lets only the five screen actions through (firmware/modules/ring_control/src/rctl_logic.c:142-171). Test D holds the centre for 1,200 ms in all four modes, with control active, and checks start, stop and no report (firmware/tests/bsim/control/ring_app/src/main.c:378-395); LOG line 1718 "TEST D RESULT PASS (31 checks passed)". Not built: the joystick driver (firmware/app/src/main.c:10-11) and the recorder; the hook only prints (firmware/app/src/main.c:40-45).
8. **"No device can start or stop a recording": met.** The HID control point handler only counts (firmware/modules/ring_control/src/rctl.c:60-65). There are no output or feature reports (firmware/app/prj.conf:29-30). Test D has the host write suspend and exit suspend at 45 s and checks that nothing starts (firmware/tests/bsim/control/host_app/src/main.c:576-591, ring firmware/tests/bsim/control/ring_app/src/main.c:406-415). The protocol mode write was not sent: the log shows "protocol mode -95" (LOG line 1710). The check needs only the two control point writes (host_app/src/main.c:587).
9. **"Each step has one broken copy that must fail": met.** There are eight two-device broken copies (firmware/tests/bsim/control/broken_edit.py:18-86). A copy counts only when the run ended normally and its named check line says FAIL (firmware/tests/bsim/control/run.sh:195-203). The two logic copies count only on the named case (firmware/tests/control/broken_run.sh:35-43, firmware/tests/devices/broken_run.sh:35-43). build_all runs all of them (firmware/tools/build_all.sh:138-157). LOG lines 2109-2934: each "as required", and the final "RESULT PASS" (LOG line 2935).
10. **"The tests run on the simulated ring chip, board nrf54lm20bsim/nrf54lm20a/cpuapp": partly met.** The two-device tests now default to that board, with real encryption (firmware/tests/bsim/control/run.sh:43, :97, :101; LOG lines 1325-1331). The core and smoke suites also run there (LOG lines 1300-1322). The two step 2 logic suites run on native_sim only: firmware/tests/control/testcase.yaml:4-5 and firmware/tests/devices/testcase.yaml:4-5. Their broken copies also run there (firmware/tests/control/broken_run.sh:28). LOG lines 1310-1311 list only ring.smoke and ring_core.logic on the bsim board.

Count: 8 of 10 met (1, 3, 4, 5, 6, 7, 8, 9), 2 partly met (2, 10), none not met.

## 2. Findings of the first review (R1 parts 1, 2 and 4): closed or open

R1 part 1 (bar items)
- R1 1.2, two hosts only over Bluetooth: **open.** firmware/tests/bsim/control/ring_app/src/main.c:295 and :303.
- R1 1.4, fourth mode: **open, now stated as a deviation** (firmware/modules/ring_control/include/ring_control/rctl_modes.h:27; the test fixes four, firmware/tests/control/src/test_control.c:333).
- R1 1.5 and 4.2, tests on nRF52 instead of the ring chip: **closed for the two-device tests** (firmware/tests/bsim/control/run.sh:38-43; LOG line 1325). For the logic suites, see bar item 10.
- R1 1.6 and 4.3, the switch window was untested: **closed at the ring.** firmware/tests/bsim/control/ring_app/src/main.c:318-320; logic firmware/tests/devices/src/test_devices.c:163-171. The host side cannot see this leak: LOG line 2280.
- R1 1.7, no hold with control attached: **closed** (firmware/tests/bsim/control/ring_app/src/main.c:378-395).
- R1 1.8, no host-write test: **closed** (firmware/tests/bsim/control/ring_app/src/main.c:406-415).
- R1 1.9, broken copies passed on any failure: **closed** (firmware/tests/bsim/control/run.sh:195-203; firmware/tests/control/broken_run.sh:37; firmware/tests/devices/broken_run.sh:37; build_all stage 5 at firmware/tools/build_all.sh:152-157).

R1 part 2 (tests)
- Click report index unchecked: **closed** (firmware/tests/control/src/test_control.c:113-114). The "second report of a move" point does not apply: a move is one report (firmware/modules/ring_control/src/rctl_logic.c:127-131; test :102).
- Report map maximum not checked: **closed** (firmware/tests/control/src/test_control.c:285-306).
- `link_is_up()` not covered: **closed** through the pure `rdev_link_usable` (firmware/modules/ring_devices/src/rdev_logic.c:153-156; firmware/tests/devices/src/test_devices.c:163-171).
- A hole 1, a held flood passed: **closed** (firmware/tests/bsim/control/host_app/src/main.c:115 and :184-187; the repeat_flood copy is caught, LOG line 2673).
- A hole 2, the 128-record cap: **open** (firmware/tests/bsim/control/host_app/src/main.c:60 and :226). Low risk: a flood beyond 128 also loses the later expected steps, so A fails.
- B, the hosts filter by their own bond address: **open** (firmware/tests/bsim/control/host_app/src/main.c:471). The ring's stranger rejection is now run in F instead.
- C, weak check "no key while not paired": **open** (firmware/tests/bsim/control/ring_app/src/main.c:356). `list.active` is RDEV_NONE after the removal (firmware/modules/ring_devices/src/rdev_logic.c:88-89), so `-ENOTCONN` holds whatever the gate does.
- C, pairing outside the window never tried: **partly closed.** Test F tries it, but it proves the stranger drop (firmware/modules/ring_devices/src/rdev.c:293-301), not the pairing gate (:366). See part 3, F.

R1 part 4 (risks)
1. Product app joined nothing: **closed** (firmware/app/src/main.c:63-76). But the product never sets control active (only the test does, firmware/tests/bsim/control/ring_app/src/main.c:220), so the product sends no key until the screens exist (stated at firmware/modules/ring_control/include/ring_control/rctl.h:39-43).
2. nRF54 encryption: **closed** (firmware/tests/bsim/control/run.sh:38-41; LOG lines 1335-1933 pass on that board).
3. Keys to the old device in a switch: **closed in code** (firmware/modules/ring_devices/src/rdev_logic.c:155). Tested at the ring only.
4. Stuck key: **closed** (firmware/modules/ring_control/src/rctl.c:152-194 and :221-227; test firmware/tests/bsim/control/ring_app/src/main.c:397-404).
5. Menu moves type on the host: **closed** by the control-active gate (firmware/modules/ring_control/src/rctl_logic.c:165-171; firmware/modules/ring_control/src/rctl.c:243-246).
6. Untested paths: **partly closed.** A stranger outside the window is now run (F). Still not run: the 60 s window timeout (firmware/modules/ring_devices/src/rdev.c:236-257), a third bond and a refused fourth over Bluetooth, and removal of a slot that is not active.
7. Bonds after a reset: **open.** No settings in the test ring app (firmware/tests/bsim/control/ring_app/prj.conf:1-35); settings are on for the kit only (firmware/app/boards/nrf54lm20dk_nrf54lm20a_cpuapp.conf:2-3).
8. Resolvable private addresses: **open** (firmware/modules/ring_devices/src/rdev.c:294-295 compares fixed addresses).
9. Short centre press in RECORDING is a highlight: **open, stated** (firmware/docs/devices-control-notes.md:140).
10. `rdev_active()` without the lock: **closed** (firmware/modules/ring_devices/src/rdev.c:703-711). `bt_conn_get_info` error: **changed.** The link is now dropped (firmware/modules/ring_devices/src/rdev.c:278-281), but advertising may not restart; see part 4, item 2.

## 3. Each two-device test and each broken copy

The rule for counting a broken copy is sound: it counts only when there is no infra failure and the named line is present (firmware/tests/bsim/control/run.sh:195-203). A copy cannot pass on a timeout or a crash. It also cannot pass on another check's failure: the regex is the exact named line (firmware/tests/bsim/control/broken_edit.py:22, 29, 36, 43, 53, 60, 71, 81).

- **A** (ring firmware/tests/bsim/control/ring_app/src/main.c:195-284).
  - It fails on: a wrong key, report id, length or byte; a missing release; any extra report (host firmware/tests/bsim/control/host_app/src/main.c:160-198); a held count outside 4 to 8; a key while control is off; a key with the screen off; a key on a double press; a drop not seen or no reconnect (ring :276-283).
  - keymap copy: named host check presenter.right. It was the only failed check (LOG line 2108, "1-failed-checks").
  - repeat_flood copy: caught by the host only. The flood bypasses `send_one` and the stats (firmware/tests/bsim/control/broken_edit.py:65-66). So the ring's own bound checks (ring :248-249) are blind to it. The ring said PASS (LOG line 2565).
  - gate copy: makes two edits (firmware/tests/bsim/control/broken_edit.py:72-77), because either gate alone stops the key. So no test shows that each gate works alone. The named line failed (LOG line 2858).
- **B** (ring :286-332; host :121-131).
  - It fails on: a key of one phase at the wrong host, a missing key, a switch that does not reconnect, a refused empty-slot switch not refused, or identities not distinct.
  - switch_gate copy: the named ring check failed (LOG line 2310). But both hosts passed (LOG lines 2280, 2307). The leaked key never reached host 1's records, so the host-side "first receives none" cannot catch this fault. Only the ring's return code catches it: `r == -ENOTCONN` at ring :320.
  - A fault that sends the key and still returns `-ENOTCONN` would pass B. That would be contrived (by reading).
- **C** (ring :334-362; host :606-608).
  - It fails if the bond is not deleted (ring :347), if the old keys still work (host :357-363, :606), or if there is no second pairing (host :607).
  - The check at ring :356 is weak (part 2). C has no broken copy.
- **D** (ring :366-416; host :134-136, :576-591).
  - It fails on: no start or stop of a recording in any mode; a report on a hold; a release not retried; a host write that starts something.
  - hold_key copy: the named media check (LOG line 2191).
  - host_write copy: it calls a hook of the test app (firmware/tests/bsim/control/ring_app/src/main.c:187-191), so it stands for any path from a host write to the joystick. Named line at LOG line 2486.
  - release_retry copy: named line at LOG line 2934.
  - In presenter mode the "sends no report" check is blind: the centre sends nothing there (firmware/modules/ring_control/include/ring_control/rctl_modes.h:108). The recording checks still cover presenter.
  - The release failure is injected only as `-EIO` from the test hook (firmware/modules/ring_control/src/rctl.c:141-145).
- **F** (ring :420-434; host :620-627).
  - It fails when an unbonded host gets a bond or keys while the window is closed.
  - Hole: F exercises the stranger drop, not the pairing gate. In the good run each host 2 link ends with reason 0x13 from the ring about 100 ms after it opens, with security "err 9", not "pair not allowed" (LOG lines 1766-1768). So the ring drops it in `on_connected` (firmware/modules/ring_devices/src/rdev.c:293-301) before any pairing request.
  - The window copy needs both edits, the gate and the stranger check (firmware/tests/bsim/control/broken_edit.py:44-49). By reading, a copy with only `ok = true` at rdev.c:366 would pass F. That is not run, so it is unverified.
  - The ring's own checks are blind. Under the window copy the ring printed "RESULT PASS" (LOG line 2367) while host 2 held a bond and had received host 1's key (LOG lines 2391 and 2395). `wait_ready` cannot tell which host is linked (ring :158-170). "one bond" reads the slot mask, which cannot see a second bond on the same identity (ring :430 and :433).
- **T** (firmware/tests/bsim/control/trial_app/src/main.c:116-150; host :145-152).
  - It fails if a key reaches the wrong link or both links are not up.
  - It bypasses ring_devices and the glue and sends with a test hook to a given connection (trial main.c:134-142). So it proves only that the SDK's per-connection send keeps the two hosts apart.
  - T has no broken copy.
- **Logic broken copies**: they count only "PROJECT EXECUTION FAILED" plus the one named case (firmware/tests/control/broken_run.sh:35-43; firmware/tests/devices/broken_run.sh:35-43). They have no other way to pass.

## 4. New faults found after the fixes, most serious first

1. **A stranger held the ring's only link for 12.3 s in test F.** Host 2 connected at 18.571 s, and the ring ended the link at 30.892 s (LOG line 1790 and lines 1860-1861); the other attempts lasted about 100 ms. With `CONFIG_BT_MAX_CONN=1` (firmware/app/prj.conf:14), the bonded device cannot connect during that time.
   - A possible cause, by reading: `disconnecting = true` is set even when `bt_conn_disconnect` fails (firmware/modules/ring_devices/src/rdev.c:298-300). After that `update_fn` never retries (:201), and the plan says STAY because the stranger is on the target slot (firmware/modules/ring_devices/src/rdev_logic.c:128-129).
   - Unverified: the ring's `rdev:` lines are not in LOG (run.sh:121 keeps only RING lines).
   - No test bounds how long a stranger may hold the link. F passed only because host 1 stayed away until 32 s (host :570).
2. **No advertising restart after a `bt_conn_get_info` error.** firmware/modules/ring_devices/src/rdev.c:278-281 disconnects without setting `cur_conn`, `adv_on` stays true, and `on_disconnected` returns early for a link that is not `cur_conn` (:312-314). Nothing calls `submit_update`, so the ring may stop advertising. By reading; this path is rare.
3. **The glue sends Bluetooth reports while it holds the core's lock.** In firmware/modules/ring_glue/src/rglue.c:46-50 and :71-75, `dispatch` runs while `lk` is held, and that leads to `bt_hids_inp_rep_send`. `rglue_input` takes a mutex, so the coming joystick driver must not call it from an interrupt. firmware/modules/ring_glue/include/ring_glue/rglue.h:39-40 does not say so. By reading.
4. **The wearer's action is dropped with `-EBUSY` for up to 1 s while a release waits** (firmware/modules/ring_control/src/rctl.c:247-252; 20 x 50 ms at firmware/modules/ring_control/include/ring_control/rctl.h:55-56). This is a design choice; it is not tested from the wearer's side.
5. **Stale text.**
   - Both test apps say "simulated nRF52 by default" (firmware/tests/bsim/control/ring_app/src/main.c:2, firmware/tests/bsim/control/host_app/src/main.c:2), but run.sh defaults to nrf54lm20bsim (run.sh:43).
   - The run.sh usage line omits T (run.sh:57).
   - Two notes say nRF52 against their own later lines: firmware/docs/step2-round2.md:57 against :63, and firmware/docs/devices-control-notes.md:160 against :110.

I checked the release retry for a release sent to the new device after a switch and found no fault. After `rdev_switch` the old link is no longer usable (firmware/modules/ring_devices/src/rdev_logic.c:155). The next retry finds no connection and drops the release as lost (firmware/modules/ring_control/src/rctl.c:160-165). That retry comes within 50 ms, well before a new link can be ready (by reading).

## 5. Still not built against the specification

- The joystick driver (firmware/app/src/main.c:10-11). The screens: passkey display, device picker, mode choice, and `rctl_set_active` on control screens (main.c:12-15).
- The recorder acting on RC_ACT_OPEN and RC_ACT_CLOSE (main.c:40-45).
- Filter accept list: FW:720, not set. Privacy with RPA: FW:731, not set. The stranger check stands in (firmware/modules/ring_devices/src/rdev.c:292-301).
- Advertising data "Ring" plus 4 hex digits and the ring service UUID: FW:724 against firmware/modules/ring_devices/src/rdev.c:55-64.
- No advertising in SHIP, OFF, CHARGING and the other states of FW:722: the devices part has no state input (rdev.c:186-223).
- 1,000 ms advertising (FW:720) comes only after 100 ms for 30 s (rdev.c:162-165; firmware/modules/ring_devices/Kconfig).
- TX power, data length, ATT MTU (FW:696) and connection parameters (FW:724): not set in firmware/app/prj.conf:1-40.
- Bonds: FW:730 still says 2 and "asks to remove the oldest". The code has 3 and refuses a fourth (firmware/modules/ring_devices/src/rdev_logic.c:43). F7 is drafted in the notes, not written into FW.
- A long press closing the pairing window: `rdev_pair_cancel` exists (rdev.c:563-584), but nothing calls it.
- Two devices at once in the product: tried in T, not wired (firmware/modules/ring_devices/include/ring_devices/rdev.h:4-5).
- Bonds after a reset, the window timeout, a third bond and a refused fourth over Bluetooth: not tested.

Which of these break a bar item: only the missing third stand-in host, which keeps bar item 2 partly met. The logic suites on native_sim keep bar item 10 partly met. The others are outside the step 2 bar.

## What I could not check

- Any run of my own: the brief forbids builds, simulation and ssh. Every run-time statement is from LOG or marked "by reading".
- The content id 111abb1140cc6e9b: its recipe is unknown to me and I ran no git, so I judged the files on disk.
- `helper_inputs.py` and any comparison with the base commit: both need git.
- The cause of the 12.3 s stranger link (part 4, item 1): the ring's raw `rdev:` log lines are on the build server, which I may not use.
- Whether a single-gate window copy (`ok = true` only) passes F: by reading only, not run.

RESULT: done, 8 of 10 bar items met and 2 partly met (three devices proven over Bluetooth with two hosts only; logic suites not on nrf54lm20bsim); most first-review findings are closed, and the main new issues are a stranger holding the only link for 12.3 s in test F, F not testing the pairing gate alone, and the switch-window leak being visible only at the ring.
