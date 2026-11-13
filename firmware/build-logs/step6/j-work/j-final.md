The join (unit J) is done: `bash tools/unit_run.sh tests/recorder` ends `UNIT PASS tests/recorder` on both simulated targets, with all 12 broken copies failing their named case.

**Cited run:** `RING_REMOTE_SRC=/root/ring-os/src-u-join sh firmware/tools/remote.sh j-unit1 "... bash tools/unit_run.sh tests/recorder"`, remote exit 0, log `firmware/build-logs/step6/j-unit1.log`. Its last line, quoted: `# local log: firmware/build-logs/20261113-093051-j-unit1.log`; its last result line: `UNIT PASS tests/recorder`.

**Tests (each line of the brief):**
- **Suites:** the 10 suites (`recorder_rows`, `_actions`, `_boot`, `_sign`, `_sign1`, `_sequence`, `_rails`, `_rules`, `_log`, `_screens`) pass 43 of 43 cases on `native_sim` and 43 of 43 on `nrf54lm20bsim/nrf54lm20a/cpuapp` (log lines 22 and 44). They run the real core, glue, screens and every unit, the factory part included, on the simulated drivers. Each case's result is in `j-cases1.log`, read from that run's `twister.json`.
- **Red first:** each of the 12 broken copies fails its named case on both targets (broken part `RESULT PASS`). Three copies fail one more case each: `sd_off_before_mic_off` (`test_ship_closes_everything_first`), `usb_long_press` (`test_factory_gestures_reach_the_jig`), `sd_on_in_standby` (`test_sd_rail_per_state`). The suites were written before their first run, so the copies are the red proof.
- **New build_all.sh stages:** run alone from the script's own text with `tests/recorder/stages_run.sh all`, log `j-stages1.log`, last result line `STAGES PASS`. The four new stages pass with their self tests. Stage 2 finds both the start line and `ring-os recorder: boot done, state STANDBY`. The kit build compiles (exit 0). The stack report passes.
- **Runner:** `tools/unit_run.sh`. I did not run the full `tools/build_all.sh`.

**Also proven:**
- The 21 screen pictures are equal (`j-work/j-compare-screens.txt`, `RESULT EQUAL`).
- The two-device tests control, iphone, relay and screens pass with the glue changes (`j-bsim1.log`).
- Power addition (your ruling 3): `UNIT PASS tests/power` (`j-power2.log`). Its new copy `read_on_caller_thread` fails only its own case. The exact lines added are in notes section 4.

**Changes outside the plan, each ruled by you:**
- A third glue op, `rglue_ops.factory_gesture` (ruling 5).
- Two power calls, `rpw_sample_now` and `rpw_charger_now` (ruling 3).
- `rrec_glue_after` and `rrec_glue_screen_fact` stay in `firmware/modules/ring_recorder/src/rrec_int.h`, as you accepted.

**Findings for other units (not changed by me):**
- F1: `firmware/modules/ring_audio/src/rau.c` lines 313 to 320 and 336, simulation only. The harness waits 100 ms after the simulated reboot.
- F2: warnings in the kit build at `rau.c:313`, `rau.c:48` and `rmo.c:95`.

**Not proven:**
- Every real driver file (they only compile).
- The Bluetooth item of the update self-test (the suites do not enable Bluetooth).
- OLED_PWR_EN; the watchdog reset itself; the start-of-frame count for T-XTAL.
- SIGN-1 during a factory test recording.

What the kit build needs from step 7 is in notes section 6.

**Disk:** the server had 27 GB free at 09:30. I delete only my own run folders, by exact name.

**Question for the owner:** the USB vendor and product id are the kit's test pair (0x2fe3, 0x0100), not for shipping.

Notes: `firmware/docs/recorder-notes.md`. Checklist and audit: `firmware/build-logs/step6/j-work/`.

RESULT: done, commit (none: the lead commits), tools/unit_run.sh tests/recorder exit 0
