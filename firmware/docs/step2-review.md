# Step 2 review: devices and control

Version judged: the files on disk on 2026-11-11, content id in firmware/build-logs/step2/lead-review-version.txt line 1 ("1940d8d05d302076"). I did not run git, any build or any simulation (brief: read only, no build). Every finding below comes from reading the cited lines. Any statement about what a test does at run time is reasoning from the code, not a run, and is marked "by reading". The author's notes were read last, and only to find things.

Paths in this file are absolute. Short names used in the text:
- PLAN = <home>/.claude/plans/clever-puzzling-grove.md
- DS = design/software/os/design.md
- FW = design/firmware.md
Every citation still gives the full path.

## 1. Bar items: met, partly met or not met by the code

1. **Pairing with a passkey: met.** firmware/modules/ring_devices/src/rdev.c:393-397 registers only `pairing_accept`, `passkey_display` and `cancel` (display-only IO). firmware/app/prj.conf:24 sets `CONFIG_BT_SMP_SC_ONLY=y`. firmware/modules/ring_devices/src/rdev.c:361 accepts pairing only inside the window. firmware/modules/ring_devices/src/rdev.c:367-378 passes the passkey on.
2. **Three paired devices: partly met.** The code supports three: firmware/app/prj.conf:15-16 (`CONFIG_BT_MAX_PAIRED=3`, `CONFIG_BT_ID_MAX=3`) and firmware/modules/ring_devices/include/ring_devices/rdev_logic.h:20. The proof over Bluetooth pairs only two hosts (firmware/tests/bsim/control/ring_app/src/main.c:285 and :295). A third pairing, and the refusal of a fourth, are tested only in logic (firmware/tests/devices/src/test_devices.c:18-23). Test B checks three distinct identities (firmware/tests/bsim/control/ring_app/src/main.c:316-319), not three bonds.
3. **Switching the active one: met.** firmware/modules/ring_devices/src/rdev.c:585-630, with the plan from firmware/modules/ring_devices/src/rdev_logic.c:118-136.
4. **Keyboard, media keys and pointer in the three modes: met, with one extra mode.** The tables are at firmware/modules/ring_control/include/ring_control/rctl_modes.h:99-137. The report map is at firmware/modules/ring_control/src/rctl_logic.c:16-83. The sending code is at firmware/modules/ring_control/src/rctl.c:100-143. The code has a fourth mode, "agent" (firmware/modules/ring_control/include/ring_control/rctl_modes.h:27, :121-127); see part 3, item k.
5. **Proof, "a stand-in computer pairs with the ring and receives the right key for each joystick action in each mode": partly met.** Test A does this with exact bytes (part 2). It runs on `nrf52_bsim/native` (firmware/tests/bsim/control/run.sh:31), not on the ring's chip simulation that DS names (design/software/os/design.md:54, `nrf54lm20bsim`).
6. **Proof, "after a switch, the second stand-in receives the keys and the first receives none": partly met.** Test B checks this once the new link is ready (firmware/tests/bsim/control/ring_app/src/main.c:302-311; host side firmware/tests/bsim/control/host_app/src/main.c:120-130 and :168). No key is sent between `rdev_switch()` and the new link, so the gate that stops keys going to the old device in that window (firmware/modules/ring_devices/src/rdev.c:126, `link_slot == list.active`) is never tested (part 2, B).
7. **"A long press on the joystick's centre still starts and stops a recording in every mode": partly met by the code, not proven.** The core does not know the mode, and `rctl_from_core` returns false for `RC_ACT_OPEN` and `RC_ACT_CLOSE` (firmware/modules/ring_control/src/rctl_logic.c:142-163). So in the test ring app, where the core and control run together, a long press reaches the core in every mode. But the product application does not run the core or any joystick source at all (firmware/app/src/main.c:45-60), and no test injects a hold of 1,000 ms or more with control attached. Every `inject` call in firmware/tests/bsim/control/ring_app/src/main.c holds for 100 ms (lines 168 and 245), except the 1,100 ms hold of a direction (line 237). The only check is the logic mapping at firmware/tests/control/src/test_control.c:219-220.
8. **"No device can start or stop a recording": met by the code, not tested.** No Bluetooth callback in firmware/modules/ring_control/src/rctl.c or firmware/modules/ring_devices/src/rdev.c calls the core. HID output and feature reports are off (firmware/app/prj.conf:29-30). No test has a host write anything and then check the core state.
9. **"Each step has one broken copy that must fail": partly met.** The broken copy exists and runs from build_all (firmware/tests/bsim/control/run.sh:68-80 and :152-160; firmware/tools/build_all.sh:140-143). But it counts as passing when test A fails for any reason (firmware/tests/bsim/control/run.sh:153), for example a pairing timeout. It never checks that the failure is the presenter.right check. The two logic broken copies have the same weakness: any nonzero twister exit, a compile error included, counts as the failure they need (firmware/tests/control/broken_run.sh:33 and firmware/tests/devices/broken_run.sh:32). build_all never runs those two scripts (firmware/tools/build_all.sh:135-145 runs only tests/bsim/*/run.sh).

## 2. Each test: the fault that makes it fail, and what it really checks

Logic suite ring_control (firmware/tests/control/src/test_control.c). It checks key codes only, with no device and no silence:
- `test_mode_tables` (:123-133): fails on any wrong kind, usage, dx, dy, report id, length, modifier, extra key or release in firmware/modules/ring_control/include/ring_control/rctl_modes.h. The expected values are literals (:23-52). Gaps: the pointer click report index is not checked (:110-119), and the second report of a move is not checked (:101-109).
- `test_presenter_page_keys_option` (:135-151): fails if the Page option is ignored, or leaks into another mode.
- `test_press_then_release` (:154-175): fails if a press has no all-zero release on the same report.
- `test_out_of_range` (:178-186): fails if an out-of-range mode or action builds a report.
- `test_only_joystick_actions_map` (:191-223): fails if any core action other than the five screen actions maps to a key, OPEN, CLOSE and SCREEN_ON included. This is the only check behind bar items 7 and 8.
- `test_report_map_matches_builder` (:226-274): fails if the bits per report id differ from the builder's lengths, or the collections do not balance. It does not check that Logical Maximum and Usage Maximum cover the codes sent (firmware/modules/ring_control/src/rctl_logic.c:36 and :39, 0x65). A map whose maximum is below 0x52 passes this test, and a host would reject Up Arrow.
- `test_mode_order_and_names` (:276-291): it asserts four modes (:280), so it fixes the deviation in part 3, item k into the tests.

Logic suite ring_devices (firmware/tests/devices/src/test_devices.c). Pure list and plan logic, with no keys, device or silence: `test_three_slots` (:9-26) fails on a count other than 3 or a fourth slot; `test_new_pairing_becomes_active` (:28-37); `test_choose_pair_slot` (:39-52); `test_remove_and_active` (:54-74); `test_next_wraps` (:76-88); `test_switch_decision` (:90-109), which is the target of the broken copy; `test_plan` (:118-159) fails if the plan keeps a link of the wrong slot or advertises while linked. None of these tests covers `link_is_up()` at firmware/modules/ring_devices/src/rdev.c:124-127, which is what really gates sending.

Two-device tests, ring script firmware/tests/bsim/control/ring_app/src/main.c, host checks firmware/tests/bsim/control/host_app/src/main.c:
- **A** (ring :194-276, host expectations :88-117).
  - **Key codes: yes.** Each report is compared by report id (taken from the host's own discovery, :199), length and every byte, in order (:138-166).
  - **Device: yes**, a single host.
  - **Silence: yes, from total count.** `pos == nrec` (:168) fails on any extra report, so it covers screen-off and the double press (:115).
  - It fails on a wrong key, a missing release, a wrong report id, an extra report, or pairing that is not at level 4 (:319).
  - Hole 1: the held step accepts any count of 4 or more (:151-159), so a flood of repeats passes up to the 128-record cap (:60, :194).
  - Hole 2: the record buffer stops at 128 (:194). The test's expected total is far below that (by reading), so this matters only for a flood.
- **B** (ring :278-321, host :120-130).
  - **Key codes: yes.**
  - **Device: yes**: each host's list holds only its own phases.
  - **Silence of the other device: yes, but only after the new link is ready**, and the other device is then disconnected (single link, firmware/app/prj.conf:14). Silence is therefore structural.
  - Fault that passes (by reading): drop `link_slot == list.active` from firmware/modules/ring_devices/src/rdev.c:126. Keys sent between `rdev_switch()` and the disconnect would then reach the old host. B sends nothing in that window (`wait_ready` at :303 and :310 comes first), so B still passes.
  - The hosts also filter by their own bond address (host :436), so the ring's own stranger rejection (rdev.c:288-296) is not what keeps them apart.
- **C** (ring :323-350, host :133-136, :541-543).
  - **Key codes: yes**, one before removal and one after re-pairing.
  - It fails if removal leaves the bond (:335), or if the old keys still work (host :324-329, :541).
  - The check "no key while not paired" (:344) is weak: at that moment the host is holding off (host :328), so `-ENOTCONN` holds whatever the gate does.
  - Pairing outside the window is never tried. A `pairing_accept` that always succeeds (rdev.c:361) passes A, B and C (by reading: every pairing in the scripts happens inside an open window).

## 3. Code against the specification (both sides quoted)

a. Bonds. design/firmware.md:724 says "Bonds: at most 2 (`CONFIG_BT_MAX_PAIRED=2`) ... A third pairing asks on SCR_CONFIRM to remove the oldest bond". The code says `CONFIG_BT_MAX_PAIRED=3` (firmware/app/prj.conf:15), and a fourth pairing is refused with `-ENOSPC` (firmware/modules/ring_devices/src/rdev_logic.c:43), with no offer to remove the oldest. The three is in line with PLAN line 19 and design/software/os/design.md:24 ("three, not two"), but FW was not updated to F7.
b. Filter accept list. design/firmware.md:714 says "when bonds exist, only bonded devices may connect (filter accept list, `CONFIG_BT_FILTER_ACCEPT_LIST`)". The code advertises open to all (firmware/modules/ring_devices/src/rdev.c:165, `BT_LE_ADV_OPT_CONN`) and drops strangers only after they connect (firmware/modules/ring_devices/src/rdev.c:288-296).
c. Privacy. design/firmware.md:725 says "Privacy on (`CONFIG_BT_PRIVACY`), resolvable private address renewed every 15 minutes". The code has no `CONFIG_BT_PRIVACY` in firmware/app/prj.conf (lines 1-39).
d. Security level. design/firmware.md:722 says "authenticated, encrypted link = security mode 1, level 4". The code accepts level 3 (firmware/modules/ring_devices/src/rdev.c:341 and :728, `BT_SECURITY_L3`; header comment firmware/modules/ring_devices/include/ring_devices/rdev.h:77 "security level 3 or more"). HID permission is AUTHEN (firmware/app/prj.conf:33). `SC_ONLY` (prj.conf:24) makes level 4 the result in practice, but the code's own gate is weaker than the specification.
e. Advertising data. design/firmware.md:718 says "Advertising data: flags, complete local name "Ring" plus the last 4 hex digits of the device id, the ring service UUID". The code sends flags, appearance and the HID UUID, with the name "Ring" alone in the scan response (firmware/modules/ring_devices/src/rdev.c:54-63). The HID UUID follows DS :28. The missing digits and the missing ring service UUID contradict FW.
f. Advertising interval. design/firmware.md:714 says "connectable, 1,000 ms interval". The code uses 100 ms for 30 s after every drop or switch (firmware/modules/ring_devices/src/rdev.c:163-164; firmware/modules/ring_devices/Kconfig:14-16, default 30).
g. Advertising per state. design/firmware.md:716 says "`SHIP`, `OFF`, `BOOT`, `RECOVERY`, `CHARGING`, `TRANSFER`, `ERR_CHARGER`, `FACTORY_TEST` | none". The code advertises whatever the core state is: `update_fn` takes no state input (firmware/modules/ring_devices/src/rdev.c:185-222).
h. Link settings. design/firmware.md:690 asks for "TX power 0 dBm. LE data length extension on (`CONFIG_BT_USER_DATA_LEN_UPDATE`), ATT MTU 247", and design/firmware.md:718 asks for "interval 30 to 50 ms, peripheral latency 4, supervision timeout 4 s". None of these is set in firmware/app/prj.conf:1-39.
i. Screen meaning of the joystick. design/firmware.md:282 says "SCR_STATUS | none | none | none | open SCR_MENU | open SCR_MENU", and :289 says "SCR_PAIR | ... | cancel pairing". The code sends a HID report for every `RC_ACT_SCREEN_*` whatever screen is shown (firmware/modules/ring_control/src/rctl.c:145-161; firmware/modules/ring_control/src/rctl_logic.c:142-163). The main.c comment tells later code to send all core actions this way (firmware/app/src/main.c:9-10). So menu navigation would also type on the host.
j. Long press closes the pairing window. design/firmware.md:298 says "an open pairing window (SCR_PAIR) is closed". Nothing links a core long press to `rdev_pair_cancel()` (firmware/modules/ring_devices/src/rdev.c:557-578 is called by no file under review).
k. Number of modes. PLAN line 18 says "Three modes on the ring: media ..., presenter ..., pointer ...". design/software/os/design.md:21 says "Three control modes on the ring." The code has four (firmware/modules/ring_control/include/ring_control/rctl_modes.h:23-29, "RCTL_AGENT"), and the test asserts four (firmware/tests/control/src/test_control.c:280).
l. Two devices at once. PLAN line 54 says "Two devices at the same time ... is tried in step 2 and kept only if the simulation holds." The code says "holding two devices at once is out of this step" (firmware/modules/ring_devices/include/ring_devices/rdev.h:4-5), with `CONFIG_BT_MAX_CONN=1` (firmware/app/prj.conf:14). It was not tried.
m. Which board the tests run on. design/software/os/design.md:54 says "the simulated ring chip `nrf54lm20bsim`". The tests run on `nrf52_bsim/native` (firmware/tests/bsim/control/run.sh:31). Both test apps still say "BabbleSim, nrf54lm20bsim" (firmware/tests/bsim/control/ring_app/src/main.c:2 and firmware/tests/bsim/control/host_app/src/main.c:2).

Found in line with the specification: pairing only inside the window (FW :723, rdev.c:361); a 60 s window (rdev.h:84); 100 ms advertising while pairing (FW :715, rdev.c:30); one connection at a time (FW :690, prj.conf:14); HID UUID in the advertising data (DS :28, rdev.c:59); removal deletes the bond (DS :30, rdev.c:668-675); the screen-off first event sends no key (FW :276, tested in A at ring main.c:242-247).

## 4. Risks the tests do not cover, most serious first

1. The product application never connects the joystick to control or to recording (firmware/app/src/main.c:45-60). The whole chain of bar items 4 and 7 runs only inside the test app.
2. All Bluetooth proof is on the nRF52 simulation. On the ring's chip simulation no encrypted link completes (firmware/tests/bsim/control/run.sh:27-30). See the end of this part.
3. Keys can go to the old device during a switch, and no test covers it (part 2, B; firmware/modules/ring_devices/src/rdev.c:126).
4. A stuck key. If the press report is sent but the release fails, `rctl_action` returns with the key still down on the host (firmware/modules/ring_control/src/rctl.c:126-136). Nothing retries or sends a release later.
5. Menu navigation types on the host (part 3, item i).
6. Pairing outside the window, a stranger connecting outside it, the window closing on its 60 s timeout (rdev.c:235-256), a third bond over Bluetooth, a fourth pairing refused over Bluetooth, and removal of a slot that is not active: none of these is run in the simulation.
7. Bonds and the active slot after a reset are not tested: the test ring app has no `CONFIG_BT_SETTINGS` (firmware/tests/bsim/control/ring_app/prj.conf:1-33).
8. Real phones use resolvable private addresses. The stranger check compares `bt_conn_get_dst` with the bond address (rdev.c:289-290), and the stand-in hosts use fixed addresses, so the resolving path is untested.
9. In `RECORDING` a short centre press is a highlight and sends no key (firmware/modules/ring_core/src/core.c:229-233), so play/pause, click and Return do not work while recording. This matches FW collision C1, but it is not tested and not stated to the owner.
10. Minor: `rdev_active()` reads `list.active` without the lock (rdev.c:697-700); on a `bt_conn_get_info` error, `on_connected` keeps no reference and never drops the link (rdev.c:274-276).

**The nRF54LM20A encryption failure.** The reviewed code gives no reason for it. The ring and host code only set security requirements (`SC_ONLY`, display-only IO, level checks). Nothing in them derives keys or touches link-layer encryption. Neither bsim app has a board-specific configuration (no boards folder under firmware/tests/bsim/control/ring_app or host_app; listing in this review's first command). A MIC failure on the first encrypted packet (reason 0x3d, run.sh:29) points below this code: either at the controller's or simulator's AES-CCM, or at the host's crypto backend for that board giving different keys on the two sides. This is unverified; I could not check it without a build.

## What I could not check

- Whether any test passes or fails, and whether the broken copies fail: no build or run was allowed.
- `helper_inputs.py` and any git comparison against the base: the brief forbids git.
- SDK behaviour I relied on (that `bt_hids_inp_rep_send` sends only to `conn`, and that RPA resolution happens before `on_connected`): the SDK sources are on the build server, which I was not allowed to use.

RESULT: done, of 9 bar items 4 are met by the code (1, 3, 4, 8), 5 are partly met (2, 5, 6, 7, 9) and none is unmet; the main gaps are no test of the long press with control attached, no test of the switch window, all proof on the nRF52 simulation, and broken copies that pass on any failure.
