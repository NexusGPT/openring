# recorder notes: unit J of software step 6 (the join)

Builder: J helper. Started 2026-11-13 07:05 CET (`date`). Version read: commit 6a52396e of ROOT (branch master), with the
factory builder's unfinished work in the tree. No git was run. Contract: `firmware/docs/step6-plan.md` (read in full,
every ruling section included), the notes of every finished unit, every public header. "FW l.N" = line N of
`design/firmware.md`. Raw evidence: `firmware/build-logs/step6/j-*` and `firmware/build-logs/step6/j-work/`.

(Written step by step while working; the run results are filled in below as they come.)

## 1. What exists (files written or changed)

| Path (under `firmware/`) | What |
|---|---|
| `modules/ring_recorder/zephyr/module.yml`, `Kconfig`, `CMakeLists.txt` | the module: `CONFIG_RING_RECORDER` (depends on the step 6 units, the glue, the screens, the clock), stack and priority of the recorder's thread, `CONFIG_RING_RECORDER_TEST_HOOKS` (tests only, needs the simulated drivers) |
| `modules/ring_recorder/src/rrec.c` | the action executor (`rrec_action`: every `rc_action`), the close in the order of FW l.125, the open of FW l.126 and 4.5, `rrec_glue_after` (state change record, sampling class, rails that follow the state, reboot, then the screens), `rrec_glue_screen_fact` (the facts the caller owns, then the screens' lock fact), the factory's test recording, the event log hook |
| `modules/ring_recorder/src/rrec_mics.c` | `rec_mics_on()` (the ONE VDD_MIC-on call), `rec_mics_off()`, `rrec_sign_hook()` |
| `modules/ring_recorder/src/rrec_boot.c` | `rrec_init()` / `rrec_boot()`: the boot sequence |
| `modules/ring_recorder/src/rrec_bridge.c` | the recorder's thread and job queue; the callbacks of power, store, audio, USB and motor; the battery values to the screens every second |
| `modules/ring_recorder/src/rrec_backend.c` | the backend of `rxf.h` and the ops of `rfa.h` |
| `modules/ring_recorder/src/rrec_int.h` | the join's own header (not frozen): the two glue entries `rrec.h` has no name for, the shared state, the test read-outs |
| `modules/ring_glue/include/ring_glue/rglue.h`, `src/rglue.c` | the plan's two additions: `rglue_ops.sign_start` (given to `rc_core_set_sign_hook` in `rglue_init`) and `rglue_battery(level)`; a third under the lead's ruling 5 on the factory unit's gaps: `rglue_ops.factory_gesture` (section 4); the comment of `rglue_ops.action` now says the recorder may block |
| `app/CMakeLists.txt`, `app/prj.conf`, `app/src/main.c`, `app/boards/nrf54lm20bsim_nrf54lm20a_cpuapp.conf` (new), `app/boards/nrf54lm20bsim_nrf54lm20a_cpuapp.overlay` | the step 6 modules in the product; the core starts in BOOT; `rrec_init()`; the line `ring-os recorder: boot done, state <state>`; `CONFIG_RING_RHW_SIM=y` for the simulated chip only (D11b); the simulated card and microphone nodes in the simulated chip's overlay; glue stack 4096 |
| `tools/build_all.sh` | section 6 items 2 to 8 (section 6 of this file) |
| `tools/stack_report.py` | the recorder's thread chains |
| `README.md` | step 6 |
| `tests/recorder/` | 10 suites (`src/test_*.c`), the harness `src/rt.[ch]`, `broken_edit.py`, `broken_run.sh`, `short_run.sh`, `stages_run.sh`, board overlays |
| `docs/recorder-notes.md` | this file |

## 2. Design and readings (each one is open for the lead; none is settled silently)

1. **Threads.** The core's actions run inside the glue's step, under its lock, on the thread that made the step: the glue's
   tick thread (presses), the caller of `rglue_event` / `rglue_battery`, or `main()` at boot. They may block (card, sign).
   A unit's callback (power thread, storage thread, audio thread, transfer thread, motor timer) never takes the glue's lock:
   it posts a job to the recorder's own thread (`rrec_bridge.c`, `rrec_thread_fn`), which calls `rglue_event` or
   `rglue_battery`. Reason: a CLOSE inside the step waits for the storage thread (`rst_close`), so the storage thread must
   never wait for the step. The recovery scan and the 60 s storage retry also run on that thread.
2. **Two glue entries beyond `rrec.h`.** `rrec.h` (frozen) names the action hook and the sign hook only. The join also needs
   the step's end (state change records, rails per state, the reboot of FW_END and FACTORY_EXIT) and a place to write the
   facts the caller owns under the glue's lock (open flag at start-up, factory flag, storage full cleared). Both are in
   `src/rrec_int.h` (not frozen): `rrec_glue_after` (the product's `rglue_ops.after`; it calls `rscr_glue_after` last) and
   `rrec_glue_screen_fact` (the product's `rglue_ops.screen_fact`; it returns `rscr_lock_fact_now()` last). The glue got the plan's two additions
   (and the factory gesture op of ruling 5, section 4). **For the lead:** if these two belong in `rrec.h`, U0's helper adds them there.
3. **The sign is drawn twice per start.** The core's hook (`rrec_sign_hook`) draws the sign through `rscr_sign_start`; the
   OPEN that follows calls `rec_mics_on()`, which draws it again and switches VDD_MIC on only on that second answer of 0
   (the choice `rrec.h` leaves to the join). Every VDD_MIC-on thus follows its own answer 0. If the second draw fails, the
   recording is closed empty at once and the core is sent `RC_EV_MIC_NO_BLOCK` (row FW l.169: close; MF) with a
   `RREC_LOG_SIGN_REFUSED` record: FW has no row for "sign refused after the hook said drawn".
4. **Open fails.** A mount or `rst_open` error inside OPEN sends `RC_EV_CHUNK_WRITE_FAILED` (row FW l.168) with a
   `RREC_LOG_FAULT_CHUNK_WRITE` record (chunk_seq 0): FW has no row for "open failed"; this reaches ERR_STORAGE_FAULT.
5. **Rails follow the state** (`rails_follow_state`, after each step, not in BOOT, not in FACTORY_TEST): VDD_SD is mounted in
   RECOVERY, RECORDING, TRANSFER and unmounted elsewhere (FW l.912 to l.920); VDD_MIC is switched off outside RECORDING
   unless a factory test recording runs (a last guard; the actions already do it); HFXO is held for USB in CHARGING,
   TRANSFER and FACTORY_TEST (FW l.917, l.918: the transfer part does not request it itself).
6. **Row FW l.168 (3 failed chunk writes):** STOP_PDM = `rau_halt` (it also applies the clock pins' sleep state, so
   CLOCKS_LOW has nothing more to do), MIC_OFF = `rec_mics_off` then `rau_release`. The superblock is left open (no
   `rst_close`); VDD_SD goes off when ERR_STORAGE_FAULT is entered (rails per state).
7. **LOG_EVENT, WRITE_CLOSE_RECOVERED, CLEAR_OPEN_FLAG, REQUEST_UPGRADE_TEST carry nothing more:** the part that reported
   the event wrote the record (storage init, scan read error, sign refused); `rst_recover` wrote CLOSE RECOVERED and cleared
   the flag; `rsy_fw_end` requested the test upgrade before its OK (rsy.h).
8. **The reboot** of rows FW l.180, l.201, l.204 is done after the step (`rrec_glue_after`) with the reason of the step's
   event: FW_END = `RHW_REBOOT_UPDATE`, FACTORY_EXIT = `RHW_REBOOT_FACTORY_EXIT`, VBUS removed = `RHW_REBOOT_FACTORY_VBUS`.
   REBOOT (opcode 0x0C) reboots in `after_response` with `RHW_REBOOT_COMMAND` (FW l.707), after the OK was handed over.
9. **Commands and the core.** The backend posts only FW_END (after its OK response) and the factory part's effects (ENTER,
   EXIT, SHIP_ENTER, SHIP_SAMPLE, after the response). No command reaches the gestures (FW l.209).
10. **Sampling class (ruling 8).** `rpw_state` gets the core state after each step, and RECORDING while a factory test
    recording runs (then FACTORY_TEST again).
11. **Watchdog (ruling 9).** `rsy_recording(true)` at OPEN and around a test recording, false at the close; progress is
    reported on the audio thread at each full chunk (`au_put`) and on the storage thread at each written chunk
    (`chunk_written`), every 512 ms, under the 2 s of FW l.1065.
12. **Main chip reset reason.** `RREC_LOG_MAIN_RESET` carries 0 as the reason and `gpregret1`: `rhw.h` has no call for the
    chip's own reset reason (hwinfo). For the lead: a field of `rhw_retained_api` or a call in `rsy.h` (frozen headers).
13. **The battery values to the screens** (FW l.374): every second on the system work queue, `rpw_values()` to
    `rscr_set_battery()`.
14. **T-MOTOR** (factory op `motor_on`): `rmo.h` plays the seven patterns only, so the join drives `rhw_motor()` directly
    for the 500 ms and gives the gauge the pulse's charge with FW l.332's formula. **For the lead:** a call in `rmo.h` would
    keep the motor kind owned by ring_motor alone; the lead ruled the pin drive by the join (ruling 2). `vbat_mv` and
    `charge` use the two reads added to the power unit (ruling 3, section 4). `xtal_counts` answers -ENOTSUP (no
    start-of-frame count in `rhw.h`).
15. **Joystick events in FACTORY_TEST** (T-JOY, T-CENTRE): the glue hands the events of the core's own recogniser to the
    join, which maps them to `rfa_input` (ruling 5; section 4, gap 5).
16. **Boot.** `rrec_boot()` order: `rsy_init`, crash block (RREC_LOG_CRASH) or gpregret1, RREC_LOG_MAIN_RESET, time guess
    (RREC_LOG_TIME_GUESS), `rpw_boot_causes`, `rmo_init`, `rst_init`, `rau_init`, `rxf_start`, `rfa_init`,
    `rsy_wdt_start`, then **`rpw_start` (charge on with VBUS) immediately before `rst_mount(true)`** (FW l.893), the level
    (`rglue_battery`), VBUS (`rglue_event(RC_EV_VBUS_IN)`), the mount result (`RC_EV_STORAGE_INIT_FAILED` with
    RREC_LOG_FAULT_STORAGE_INIT) or the facts (open flag, factory flag, SFULL) and `RC_EV_INIT_DONE`. The self-test items
    storage and Bluetooth (`bt_is_ready`) pass here; USB passes at the configured callback.

## 3. Findings for other units (reported to the lead; files not mine, not changed)

- **F1, ring_audio (U3), simulation only.** `modules/ring_audio/src/rau.c` `clear_state()` (lines 313 to 320, the
  `rhw_sim_reboot` hook) sets `halting` to stop a running capture; `rau_init()` (line 336) clears it again. When the boot
  after a simulated reboot calls `rau_init` before the audio thread has seen the flag, the old `capture()` loop keeps
  running with its local `sent` already true (lines 287 to 292), so the next recordings report no "no block for 100 ms".
  Seen: `build-logs/step6/j-work/j-rows3.console` (rows 64 and 65 after a reboot: "FAULT_MIC records 0"). The harness waits
  100 ms after `rhw_sim_reboot()` (`tests/recorder/src/rt.c`, `rt_fresh` and `rt_reboot`); with it the rows pass
  (`j-rows4.console`). On the ring a reboot stops the thread: the product is not affected. Sent to the lead by message while working.
- **F2, warnings in the kit build** (not errors; the kit build exits 0): `modules/ring_audio/src/rau.c:313` `clear_state`
  and `:48` `hook_added` unused, `modules/ring_motor/src/rmo.c:95` `reboot_hook` unused, when `CONFIG_RING_RHW_SIM` is off
  (`build-logs/step6/j-prod1.log`).

## 4. What the factory unit needs from the join (factory-notes.md section 7; the lead's rulings 1 to 5)

| Gap | How the join supplies it |
|---|---|
| 1. T-MIC sees the kept frames | `au_put` (`rrec_bridge.c`, the wrapper of `rau_cb.put`) hands each full chunk's payload to the factory's `on_block` in blocks of 256 frames (`rrec_feed_test_blocks`, `rrec.c`) before `rst_put_chunk`; the partial chunk of `rau_cut` (`cut.last`) is handed too. The test recording (`rrec_test_recording`, `rrec.c`) is the normal path with type `RREC_REC_TYPE_FACTORY` through `rec_mics_on()`; a refused sign answers -ENODEV. Sampling class RECORDING while it runs (ruling 8). |
| 2. T-MOTOR pulse | `fo_motor_on` (`rrec_backend.c`): only in FACTORY_TEST (else -EPERM), `rmo_stop()`, `rhw_motor()->set(true)`, the given ms, `set(false)`, the pulse's charge to the gauge (FW l.332). No new pattern in ring_motor. |
| 3. T-MOTOR and T-CHARGE reads | the granted ADDITION to the power unit, read by the power thread: `rpw_sample_now(mv, ua)` and `rpw_charger_now(state, err_reason, ua)`. Exact lines added: `modules/ring_power/include/ring_power/rpw.h` lines 98 to 109; `modules/ring_power/src/rpw.c` line 28 (event `EV_READ`), lines 349 to 357 (the read's lock, semaphore and buffer), 359 to 412 (`do_read`, `read_now`, the two calls), 436 to 438 (the case in the power thread); `tests/power/CMakeLists.txt` lines 24 and 25 (the new file); `tests/power/src/test_read.c` (new: suite `power_read`, cases `test_sample_now_from_power_thread`, `test_charger_now_latched_error`, `test_read_before_start_times_out`); `tests/power/broken_edit.py` lines 42 to 45 (copy `read_on_caller_thread`, named case `power_read.test_sample_now_from_power_thread`). The diffs against the files before: `build-logs/step6/j-work/j-diff-rpw-h.txt`, `j-diff-rpw-c.txt`, `j-diff-power-cmake.txt`, `j-diff-power-broken.txt`. No existing declaration, code path or case changed. |
| 4. T-XTAL start-of-frame count | `fo_xtal_counts` answers -ENOTSUP in every build (`rhw.h` has no start-of-frame count). **Step 7:** count USB start-of-frame from the USB stack over `RREC_FAC_XTAL_MS` beside the GRTC. Not provable without hardware. |
| 5. T-JOY, T-CENTRE events | one recogniser: a third glue addition under ruling 5, `rglue_ops.factory_gesture`: while the core is in FACTORY_TEST, `rglue_input` feeds the edge to the core's own recogniser (`rc_gesture_input(&core.g, ...)`) instead of `rc_core_input` (the core has no press row in FACTORY_TEST), the tick thread runs `rc_gesture_tick(&core.g, ...)` before `rc_core_tick`, and each event goes to `rrec_factory_gesture` (`rrec.c`), which maps it to `rfa_input` (direction, centre down and up, MW, long, single, double). Case `recorder_rules.test_factory_gestures_reach_the_jig`. |

Product settings for the factory unit: `CONFIG_BT_CTLR_TX_PWR_0=y`, `CONFIG_HWINFO=y` (`app/prj.conf`).

## 5. tools/build_all.sh: the changes of plan section 6 (items 2 to 8)

The comment block at the top of the script lists each one. Each new stage was run alone from the text of the delivered
script by `tests/recorder/stages_run.sh`, which cuts the blocks out of `tools/build_all.sh` and runs them with the
script's own `run_stage`: `RING_REMOTE_SRC=/root/ring-os/src-u-join sh firmware/tools/remote.sh j-stages "bash tests/recorder/stages_run.sh all"`
(`search` runs the three search stages only). The run cited for each is in section 8.

| Item | Stage | What it checks | Self test (the planted copy it must refuse) |
|---|---|---|---|
| 1 | (none) | the new suites and broken copies join stages 3 and 5 by their files | (none) |
| 2 | `bsim-run` (stage 2, changed) | also the line `ring-os recorder: boot done, state STANDBY` in the 2 simulated seconds; else `bsim-recorderline` fails | (none: a check of the run's own output) |
| 3 | `recorder-one-mic-path` (new) | the VDD_MIC-on call (`rail_set(RHW_RAIL_MIC, true` or `1`) appears exactly once in the `src` folders of the step 6 modules and `app/src`, and that one is in `modules/ring_recorder/src/rrec_mics.c` | a copy of ring_store's `src` with a second such call: the same search must count one more |
| 4 | `recorder-no-start-path` (new) | the sources of ring_store, ring_audio, ring_xfer, ring_power, ring_motor, ring_sys, ring_factory never name `rglue_input`, `rc_core_input`, `RC_EV_LONG_PRESS` | a copy of ring_xfer's `src` with an `rglue_input` call is found |
| 5 | `recorder-no-raw-pins` (new) | no `.c`, `.h`, `.overlay`, `.dts`, `.dtsi`, `.conf` of the step 6 modules, their test folders, `app/src` and `app/boards` names a pin by number (`P1.24`, `NRF_GPIO_PIN_MAP`, `<&gpio1 24`) | a planted overlay with `<&gpio1 24 0>` is found |
| 6 | `recorder-product-drivers` (new) | the kit build's `.config` has `CONFIG_RING_RHW_SIM` off and `CONFIG_RING_RECORDER_TEST_HOOKS` off; the simulated-chip product build has `CONFIG_RING_RHW_SIM=y`; prints the real driver files the kit build compiled (D15) and the count of simulated driver objects in it | a copy of the kit `.config` with `CONFIG_RING_RHW_SIM=y` is refused |
| 7 | `stack-report` (changed through `tools/stack_report.py`) | the chains of the glue's thread with the recorder's actions, the recorder's thread, audio, storage, USB, power sampling, motor timer | the script's own rule: a named function missing from the build fails it (one was found and declared inlined: `thread_write_one`, run `j-stack1`) |
| 8 | `link-settings` | unchanged: the factory unit needs `CONFIG_BT_CTLR_TX_PWR_0=y` and `CONFIG_HWINFO=y` in the product; neither is one of the keys the stage compares, so the stage needs no change | (the stage's existing self tests) |

The last line of the script stays `RESULT PASS` or `RESULT FAIL <stages>`.

## 6. The development kit build and what step 7 (the ring's board files) must add

The kit build (`nrf54lm20dk/nrf54lm20a/cpuapp`, sysbuild with MCUboot) compiles with the recorder parts and the real files
(section 8 cites the run). `app/boards/nrf54lm20dk_nrf54lm20a_cpuapp.conf` now sets `CONFIG_RING_RHW_SIM=n`,
`CONFIG_USB_DEVICE_STACK_NEXT`, `CONFIG_WATCHDOG`, `CONFIG_RETAINED_MEM`, `CONFIG_STREAM_FLASH`, `CONFIG_IMG_MANAGER`,
`CONFIG_MCUBOOT_IMG_MANAGER`. Each real file compiles only where its node exists (D15), so most of them are empty stubs on
the kit. Step 7 must add, for the real drivers to exist at all:
- `pdm20` enabled with a `default` and a `sleep` pin state (the microphone clock and data; `rau_hw_real.c`, FW l.465);
- `spi00` with the SD card slot (`zephyr,sdhc-spi-slot`, `zephyr,sdmmc-disk` "SD", 16 MHz, FW l.504, l.505) and
  `CONFIG_DISK_ACCESS` (`rst_hw_real.c` compiles only with both);
- the nPM1304 nodes (mfd, regulators with the two load switches, charger, FW l.862 to l.890; `CONFIG_RING_POWER_REAL`
  depends on them) and a lithium cell model for the fuel gauge (power notes, K6);
- the alias `ring-motor` (the MOTOR pin, `rmo_hw_real.c`);
- `wdt31` enabled, the partition `slot1_partition`, the alias `crashram` (a `zephyr,retained-ram` node of 1,024 bytes),
  the alias `gpregret1` (`rsy_hw_real.c`, sys notes section 6), and the settings back end on the RRAM (K10, not settled);
- the USB controller node the transfer part names (`zephyr_udc0`) and the product's vendor and product id (section 9);
- a start-of-frame count for T-XTAL (section 4, gap 4);
- the main chip's reset reason for `RREC_LOG_MAIN_RESET` (section 2, item 12).

## 7. Open points inherited (from the units' notes; decided nothing silently)

- **The real USB file only builds** (xfer notes section 6: `usbd_init` returned -ENOENT on the virtual controller in a
  standalone run). The product on the simulated chip does not use it: `CONFIG_RING_RHW_SIM=y` there, so `rxf_hw_real.c` is
  not compiled and the transfer part runs on the simulated USB transport. The recorder's boot line is reached with the
  simulated drivers (section 8, stage 2). The real file compiles in the kit build and is unproven.
- **The settings back end on the chip's memory (K10)** is not settled: step 7.
- **The USB vendor and product id** in `modules/ring_xfer/src/rxf_hw_real.c` lines 31 and 32 (0x2fe3, 0x0100) are the
  kit's test pair: kept, and marked "NOT FOR SHIPPING" where the join can write it (`app/prj.conf`, the comment at its
  end); the file itself is the transfer unit's. The question is in `questions_for_owner`.
- **Ruling 9 (watchdog outside a recording)** and **ruling 8 (sampling class)** are applied as ruled (section 2, items 10
  and 11).
- **Finding F1** (section 3) is for the review after step 6.

## 8. Runs and looks, in order (every one; logs in `build-logs/step6/`)

All from ROOT with `RING_REMOTE_SRC=/root/ring-os/src-u-join sh firmware/tools/remote.sh <name> "<command>"`.

| Log | Command | Remote exit | What it showed |
|---|---|---|---|
| `j-build1.log`, `j-build2.log` | `tests/recorder/short_run.sh native_sim CONFIG_RING_FACTORY=n build` | 1, 1 | compile errors in my tests (an unused function, a maybe-uninitialized), then missing Bluetooth settings (`CONFIG_BT_SMP_APP_PAIRING_ACCEPT`) for the control part |
| `j-build3.log` | the same | 0 | builds |
| `j-run1-native.log` | `short_run.sh native_sim CONFIG_RING_FACTORY=n` | 1 | 36 of 39 cases; ran at real time (3,573 s): `CONFIG_NATIVE_SIM_SLOWDOWN_TO_REAL_TIME=n` added; row 11's read error at the wrong LBA (a new log starts at chunk 1), `was_cut` read after the reboot that clears it: test faults, fixed; rows 64, 65 not taken (finding F1) |
| `j-boot2.log` | `short_run.sh native_sim CONFIG_RING_FACTORY=n,RT_SUITE=test_boot` | 0 | the boot suite after the fixes |
| `j-run2.log` | `short_run.sh` both boards, factory off | 1 | 38 of 39 on each board; rows 64 and 65 |
| `j-peek1.log` | a grep of run 2's twister log on the server | 0 | the microphone fault never reached the core after row 63 |
| `j-rows3.log` | rows suite with diagnostics | 0 (short_run's own exit not kept) | "FAULT_MIC records 0": the audio thread, finding F1 |
| `j-rows4.log` | rows suite with the 100 ms wait | 0 | 8 of 8 |
| `j-broken1.log` | `RING_BROKEN_EXTRA=CONFIG_RING_FACTORY=n tests/recorder/broken_run.sh` (11 copies) | 0 | `RESULT PASS`: each fails its named case on both boards |
| `j-bsim1.log` | `tests/bsim/{control,iphone,relay,screens}/run.sh` | 0 | the two-device tests of steps 2 to 5 pass with the glue's changes |
| `j-prod1.log` | product app, simulated chip build and 2 s run, kit build, factory off | 0 | the boot line; the kit build exits 0 (warnings F2) |
| `j-stack1.log` | `tools/stack_report.py` on that kit build | 0 (the script's own exit 1 is printed inside) | one chain member missing (`thread_write_one`, inlined): declared |
| `j-run3.log` | `short_run.sh` both boards, factory off | 0 | 41 of 41 on each board |
| `j-run4.log` | `short_run.sh` both boards, factory on (U8 landed) | 1 | 41 of 43: `test_factory_rows` checked rows 70 and 71 before ship mode let the step end; `test_fw_end_row` failed after it (the ship still held the glue): test order fixed |
| `j-power1.log` | `tools/unit_run.sh tests/power` | 1 | 35 of 35 cases on each board; my copy `read_on_caller_thread` also failed `test_read_before_start_times_out`: edit narrowed |
| `j-power2.log` | `tools/unit_run.sh tests/power` | 0 | `UNIT PASS tests/power` |
| `j-stages1.log` | `tests/recorder/stages_run.sh all` | 0 | stages dk, stack-report, bsim-build, bsim-run (both lines), the four new stages with their self tests: `STAGES PASS` |
| `j-run5.log` | `short_run.sh` both boards, factory on | 0 | 43 of 43 on each board |
| `j-unit1.log` | `tools/unit_run.sh tests/recorder` (the cited run, section 9) | 0 | `UNIT PASS tests/recorder` |
| `j-cases1.log` | a read of that run's `twister.json` on the server | 0 | 86 lines, every case passed on each board |
| `j-screens1.log` | `tests/screens/short_run.sh` (the screens unit's) | 0 | 56 of 56 cases on each board; the pictures compared: `j-work/j-compare-screens.txt`, `RESULT EQUAL` |

## Lead's rulings received during the work

- `rrec_glue_after` and `rrec_glue_screen_fact` stay in the join's own header `src/rrec_int.h`; no change to `rrec.h`.
- F1: keep the 100 ms wait in the harness; for the review after step 6. F2: noted for the review.
- The factory unit's five gaps: rulings 1 to 5, applied as in section 4.

## 9. The cited run and the rows of the plan that name J

**The cited run:** `RING_REMOTE_SRC=/root/ring-os/src-u-join sh firmware/tools/remote.sh j-unit1 "rm -rf /ws/out/20261113-092918-j-run5-recorder-short && bash tools/unit_run.sh tests/recorder"`
(the `rm` removes my previous run folder by its name), log `build-logs/step6/j-unit1.log` (copy of
`build-logs/20261113-093051-j-unit1.log`), exit file `build-logs/step6/j-work/j-unit1.exit` holding 0. Its last result line,
quoted: `UNIT PASS tests/recorder`; the broken part ends `RESULT PASS`. The log's own last line is
`# local log: firmware/build-logs/20261113-093051-j-unit1.log`.
Suites: "43 of 43 executed test cases passed" on native_sim (log line 22) and on the simulated chip (line 44). Twister's
summary shows no per-case lines for a passing run, so each case's result was read from that run's `twister.json` on the
server (`build-logs/step6/j-cases1.log`, 86 lines "board case passed"); the table below is printed by
`build-logs/step6/j-work/j-map.py` from that file (output `j-work/j-map.out`), line numbers are of `j-cases1.log`.

| Row | Case | native_sim | nrf54lm20bsim_nrf54lm20a_cpuapp |
|---|---|---|---|
| C1 | `recorder_rows.test_mic_rail_only_in_recording` | l.19 passed | l.51 passed |
| C4 | `recorder_actions.test_close_order` | l.29 passed | l.65 passed |
| C5 | `recorder_actions.test_open_order` | l.28 passed | l.66 passed |
| C6 | `recorder_rows.test_charge_on_every_vbus_row` | l.13 passed | l.57 passed |
| C6 | `recorder_boot.test_vbus_boot_charges_before_mount` | l.35 passed | l.75 passed |
| C7 | `recorder_boot.test_vbus_boot_charges_before_mount` | l.35 passed | l.75 passed |
| C8 | `recorder_boot.test_init_done_each_row` | l.34 passed | l.76 passed |
| C9 | `recorder_boot.test_recovery_rows` | l.33 passed | l.77 passed |
| C10 | `recorder_sign.test_start_draws_sign_before_mic` | l.39 passed | l.81 passed |
| C11 | `recorder_sign.test_sign_refused_no_mic_m3_log` | l.38 passed | l.82 passed |
| C12 | `recorder_actions.test_stop_m2_after_mic_off` | l.27 passed | l.67 passed |
| C13 | `recorder_actions.test_ble_highlight_marks` | l.25 passed | l.69 passed |
| C14 | `recorder_rows.test_vbus_in_recording` | l.18 passed | l.52 passed |
| C15 | `recorder_rows.test_recording_exits` | l.17 passed | l.53 passed |
| C16 | `recorder_boot.test_restart_after_cut_recovers` | l.32 passed | l.78 passed |
| C17 | `recorder_rows.test_usb_configured` | l.16 passed | l.54 passed |
| C18 | `recorder_rows.test_transfer_rows` | l.15 passed | l.55 passed |
| C18 | `recorder_rows.test_fw_end_row` | l.14 passed | l.56 passed |
| C19 | `recorder_actions.test_retry_storage_reports_result` | l.23 passed | l.71 passed |
| C20 | `recorder_rows.test_factory_rows` | l.12 passed | l.58 passed |
| C21 | `recorder_rules.test_no_command_starts_or_stops` | l.47 passed | l.60 passed |
| C22 | `recorder_rows.test_charge_on_every_vbus_row` | l.13 passed | l.57 passed |
| C23 | `recorder_actions.test_watchdog_fed_while_recording` | l.20 passed | l.74 passed |
| C24 | (none of J's) | - | - |
| C25 | `recorder_actions.test_refusal_plays_m3` | l.24 passed | l.70 passed |
| C26 | `recorder_actions.test_mw_in_recording_marked` | l.22 passed | l.72 passed |
| C27 | `recorder_sign.test_start_draws_sign_before_mic` | l.39 passed | l.81 passed |
| C27 | `recorder_actions.test_m1_at_start` | l.26 passed | l.68 passed |
| C33 | `recorder_log.test_pattern_start_logged` | l.9 passed | l.63 passed |
| C33 | `recorder_actions.test_mw_in_recording_marked` | l.22 passed | l.72 passed |
| C36 | `recorder_sign1.test_sign1_every_row` | l.41 passed | l.85 passed |
| C37 | `recorder_sign.test_only_rec_mics_on_enables_mic` | l.37 passed | l.83 passed |
| C37 | `recorder_sign.test_close_mic_off_before_screen_leaves` | l.36 passed | l.84 passed |
| C38 | `recorder_sign1.test_sign1_every_row` | l.41 passed | l.85 passed |
| C38 | `recorder_sign1.test_forced_draw_failure` | l.40 passed | l.86 passed |
| C39 | `recorder_screens.test_battery_reaches_screens` | l.50 passed | l.91 passed |
| A6 | `recorder_sequence.test_start_order_and_times` | l.43 passed | l.87 passed |
| A6 | `recorder_sequence.test_stop_order` | l.42 passed | l.88 passed |
| A10 | `recorder_log.test_stop_press_time_logged` | l.8 passed | l.64 passed |
| A12 | `recorder_sequence.test_start_order_and_times` | l.43 passed | l.87 passed |
| A13 | `recorder_sequence.test_stop_order` | l.42 passed | l.88 passed |
| P4 | `recorder_boot.test_vbus_boot_charges_before_mount` | l.35 passed | l.75 passed |
| P6 | `recorder_rails.test_rails_per_state` | l.45 passed | l.89 passed |
| P6 | `recorder_rails.test_sd_rail_per_state` | l.44 passed | l.90 passed |
| P11 | `recorder_rows.test_vbus_out_at_b2_goes_off` | l.11 passed | l.59 passed |
| P12 | `recorder_actions.test_ship_closes_everything_first` | l.21 passed | l.73 passed |
| P18 (J part) | `recorder_screens.test_ilim_dims_in_recording` | l.49 passed | l.92 passed |
| P18 (J part) | `recorder_screens.test_start_during_ilim_hold_is_dim` | l.48 passed | l.93 passed |
| T8 | `recorder_rows.test_fw_end_row` | l.14 passed | l.56 passed |
| T9 | `recorder_boot.test_selftest_items` | l.30 passed | l.80 passed |
| T24 | `recorder_boot.test_boot_count_only_at_boot` | l.31 passed | l.79 passed |
| T27 | `recorder_log.test_each_kind_logged` | l.10 passed | l.62 passed |

cases not found in a part: 0; parts: native_sim, nrf54lm20bsim_nrf54lm20a_cpuapp

Rows and parts not provable here (or not J's):
- **C24** (one recording at a time; no storage operation while the case reads): the store's and the transfer part's rows
  (`store_svc.test_one_open_recording`, `xfer_proto.test_busy_while_running`, their notes); the join adds nothing to it.
- **C26** (MW at 500 ms; the Vibration setting): the motor unit's `motor_player.test_vibration_off_keeps_the_others`; the
  join's part is that MW in a recording reaches the audio part (`test_mw_in_recording_marked`).
- **C23** the watchdog reset itself: not provable (no reset in the simulation). **C38** OLED_PWR_EN: not provable (the
  memory display has none). **C6** the charger's own behaviour: the power unit's cases.
- **T9** Bluetooth enabling: these suites do not enable Bluetooth; the test gives that item itself (section 2, item 16
  says the join passes it on `bt_is_ready()`), so the join's Bluetooth step is not proven here.
- **SIGN-1 in a factory test recording:** the 72-row SIGN-1 loop does not run a T-MIC in FACTORY_TEST; whether the
  screens keep the red dot during a test recording is not checked (T-SIGN's camera, plan section 7).

## 10. Broken copies (`tests/recorder/broken_edit.py`, `broken_run.sh`; each builds the harness and the suite of its named case)

Each edit matches exactly once (`build-logs/step6/j-work/j-editcheck1.log`). In the cited run each fails its named case on
both boards (`j-unit1.log`, broken part, line numbers of the "cases that failed" lines):

| Copy | Edit | Named case | Other cases that failed with it |
|---|---|---|---|
| `mic_before_sign` | `rec_mics_on` switches VDD_MIC on before it draws the sign | `recorder_sign.test_start_draws_sign_before_mic` (l.84, l.96) | none |
| `mic_on_refused_sign` | the screens' refusal ignored (the sign counts as drawn) | `recorder_sign.test_sign_refused_no_mic_m3_log` (l.122, l.134) | none |
| `screen_leaves_before_mic_off` | the close tells the screens "STANDBY" before VDD_MIC off | `recorder_sign.test_close_mic_off_before_screen_leaves` (l.163, l.175) | none |
| `dim_dark` | the join blanks the panel each second while recording | `recorder_sign1.test_sign1_every_row` (l.201, l.213) | none |
| `m2_before_mic_off` | M2 played before the close | `recorder_actions.test_stop_m2_after_mic_off` (l.243, l.261) | none |
| `sd_off_before_mic_off` | VDD_SD off before VDD_MIC off in the close | `recorder_actions.test_close_order` (l.295, l.314) | `recorder_actions.test_ship_closes_everything_first` (it checks the same order before ship mode) |
| `charge_after_mount` | the mount before `rpw_start` | `recorder_boot.test_vbus_boot_charges_before_mount` (l.342, l.356) | none |
| `retry_not_reported` | the 60 s retry's result not given to the core | `recorder_actions.test_retry_storage_reports_result` (l.388, l.407) | none |
| `mic_in_factory_idle` | the test recording leaves VDD_MIC on | `recorder_rows.test_mic_rail_only_in_recording` (l.436, l.453) | none |
| `usb_long_press` | every USB request also makes a long press | `recorder_rules.test_no_command_starts_or_stops` (l.478, l.489) | `recorder_rules.test_factory_gestures_reach_the_jig` (its command makes a press too) |
| `no_log_on_state_change` | no STATE_CHANGE record | `recorder_log.test_each_kind_logged` (l.513, l.524) | none |
| `sd_on_in_standby` | VDD_SD wanted in STANDBY | `recorder_rails.test_rails_per_state` (l.548, l.559) | `recorder_rails.test_sd_rail_per_state` |

The power unit's new copy `read_on_caller_thread` fails only `power_read.test_sample_now_from_power_thread` on both boards
(`j-power2.log`, last result line `UNIT PASS tests/power`).

## 10b. The exact lines added to the glue (`modules/ring_glue`; diffs against the files before:
`build-logs/step6/j-work/j-diff-rglue-h.txt`, `j-diff-rglue-c.txt`)

- `include/ring_glue/rglue.h`: lines 38 and 39 (the comment of `rglue_ops.action`: the recorder may block); lines 48 to 57
  (`rglue_ops.sign_start` and, under ruling 5, `rglue_ops.factory_gesture`); lines 78 to 80 (`rglue_battery`).
- `src/rglue.c`: lines 52 to 64 (`factory_gestures`, `hand_gestures`); lines 88 to 94 (the tick thread gives the
  recogniser's deadlines to the factory part in FACTORY_TEST); lines 113 and 114 (`rc_core_set_sign_hook` in
  `rglue_init`); lines 128 to 136 (`rglue_input` in FACTORY_TEST feeds the core's own recogniser); lines 195 to 208
  (`rglue_battery`).

## 11. Tests asked by the brief

- Suites `recorder_rows`, `recorder_actions`, `recorder_boot`, `recorder_sign`, `recorder_sign1`, `recorder_sequence`,
  `recorder_rails`, `recorder_rules`, `recorder_log`, `recorder_screens`: all on `native_sim` and on
  `nrf54lm20bsim/nrf54lm20a/cpuapp`, with the real core, glue, screens and every unit on the simulated drivers: 43 of 43 cases
  on each board in the cited run.
- Red first: the 12 broken copies, each failing its named case on both targets (section 10); the self test of each new stage
  of build_all.sh (section 5, run `j-stages1.log`). The suites were written before their first run, so the order was not
  red before green for the suites themselves; the copies are the red proof.
- Runner: `tools/unit_run.sh`; the full run `tools/build_all.sh` not run by me.
- The existing suites of steps 1 to 5: the glue and the application changed; the two-device tests that use the glue pass
  (`j-bsim1.log`); the screens suites on both boards with the pictures (`tests/screens/short_run.sh`, `j-screens1.log`)
  and the screens unit's compare script (`build-logs/step6/u9-compare.py` against `design/software/os/screens/manifest.md`
  and step 5's run): `build-logs/step6/j-work/j-compare-screens.txt`, last line `RESULT EQUAL` (21 of 21 on each board).
  The suites of the other units of steps 1 to 6 were not re-run by me (their files are not changed by me, except the
  power unit, run in full: `j-power2.log`).

## questions_for_owner

1. The USB vendor id and product id of the ring: the firmware uses the kit's test pair (0x2fe3, 0x0100), not for shipping.
   Buy a vendor id, or use a product id lent under another vendor? (Also the last question of `design/firmware.md`.)


## Fix round 1 (review of step 6, docs/step6-review.md: findings R6-01 to R6-10, R6-13, R6-14, R6-17, F1, F2)

Builder: fix1 helper. Started 2026-11-13 12:25:37 CET (`date`). Version read: commit 51c76fd4 of ROOT, firmware folder equal
to af085a68 (brief). No git was run. Raw evidence: `build-logs/step6/fix1-rec-*` (the files `fix1-broken*.console`,
`fix1-plain.console`, `fix1-compare.txt` are another helper's, not this round's). Base copies of every file changed here:
`build-logs/step6/fix1-rec-base/` (taken before the first edit). Checklist: `build-logs/step6/fix1-rec-CHECKLIST.md`.

(Written step by step; the run results are filled in below as they come.)

### FR1.1 What changed, per finding (file:line of the delivered files; case; broken copy)

"F/" is `firmware/`. Every number of the join comes from `rrec_spec.h` except the two the join states itself (marked).

| Finding | Change (file:line) | Case(s) | Broken copy (named case) |
|---|---|---|---|
| R6-01 (FW l.151) | Ship mode moved out of the step: `RC_ACT_SHIP_MODE` only sets `ship_pending` (F/modules/ring_recorder/src/rrec.c:462); after the step `rrec_glue_after` posts `RREC_JOB_SHIP` (rrec.c:668) and the recorder's thread runs `rrec_ship_now` (rrec.c:350): it waits while `rmo_playing()` is true, at most `RREC_PAT_M2_MS` (280 ms, FW l.323; added to rrec_spec.h:329 under the lead's ruling on my question, rrec_spec.h had the segments only as the comment of `RREC_PAT_M2`) plus `SHIP_M2_MARGIN_MS` 100 ms (the join's margin for the timer and the threads, rrec.c:44), rrec.c:352, then `rmo_stop()` | `recorder_ship.test_ship_feels_whole_m2` (F/tests/recorder/src/test_ship.c): 4 MOTOR edges before SHPHLDCONFIG, levels 1 0 1 0, segments 80, 120, 80 ms typed from FW l.323, with the motor unit's tolerance (-1 us to +1 ms), and 280 ms from the first high to the last low (FW l.323; +3 ms: the three segments' tolerance) | `ship_cuts_m2`: the wait loop disabled (`while (false && ...)`) |
| R6-02 (FW l.937, l.939) | `rrec_ship_now` step 1 (rrec.c:350 to 392): recording (`rrec_close` if one is open, a guard: the rows close it), storage (`unmount_now`, the waiting unmount of R6-03), USB (`rxf_stop(FINISH_WAIT_MS)`, new in ring_xfer), the join's HFXO, radio (`rdev_stop()`, new in ring_devices), screen (the screens were told SHIP or OFF in the step, rrec.c:664, before the job was posted; `rscr_sync()` waits until the screens thread drew SCR_OFF, panel off; under the lead's ruling 4 a sync asked before `rscr_start` returns at once, F/modules/ring_screens/src/rscr.c:544 to 551, so ship mode ends with no screens thread, case `recorder_a_noscreens.test_ship_without_screens_ends`, F/tests/recorder/src/test_noscreens.c: the suite sorts first and checks the screens were never started), then `rpw_ship(rfa_beacon_stop)` as before (the ship beacon of R20 unchanged: it stops right before the ship task). Test read-outs: `rrec_test_set_ship_hook` (called right before `rpw_ship`), `rrec_test_radio_stops` (F/modules/ring_recorder/src/rrec_int.h:147 to 150) | `recorder_ship.test_ship_closes_each_part_first`: factory SHIP_ENTER with VBUS (the ship waits for VBUS removal): at the end of step 1 VDD_MIC off, VDD_SD off (its rail event before SHPHLDCONFIG), USB disabled (its event before SHPHLDCONFIG), one `rdev_stop`, panel blanked, beacon not stopped, thread `rrec`; then the menu's power off with the screen on (status screen): panel blanked before SHPHLDCONFIG, thread `rrec`. The existing `recorder_actions.test_ship_closes_everything_first` (row 33: VDD_MIC, VDD_SD before SHPHLDCONFIG) stays | `ship_screen_on`: ship mode runs inside the step before the screens are told (the reviewed order: `rrec_ship_now()` called right before `rscr_glue_after`). A first edit (the screens told the state before the step) did NOT fail the case in run u1, because the SHIP row's own screen actions still turned the panel off; replaced |
| R6-03 (FW l.178, l.179) | `unmount_now` (rrec.c:273 to 324): `rst_unmount_wait(FINISH_WAIT_MS)` (new in ring_store); on `-EBUSY` a job `RREC_JOB_UNMOUNT` (`rrec_unmount_retry`, rrec.c:395, tries again while the state wants VDD_SD off). The record `RREC_LOG_UNMOUNT_FAILED` (0x0290, the 27th code of FW l.1234, added to rrec_spec.h:448; args errno i32, state u8, try u8) is written, under the lead's last ruling, at the FIRST failed try (its errno, try 1) and once more when the tries end (errno 0 when the unmount then succeeded, else the last errno; try = the number of tries made), never once per try. Used by `RC_ACT_SD_OFF` (rrec.c:454), by the rails after each step and by ship step 1. `RC_ACT_ABORT_COMMAND` now waits for the command to end after `rxf_abort()`, `rxf_finish(FINISH_WAIT_MS)` (rrec.c:509 at commit c26ae988; corrected in fix round 2, review 2 finding R2-10), the same bound as `RC_ACT_FINISH_COMMAND` (rrec.c:503) | `recorder_unmount.test_vbus_out_during_read_command` (VBUS removed while GET_LOG holds the store on a card stalling each write 400 ms with 6 queued records); `recorder_unmount.test_unconfigured_finish_times_out` (row l.178 while GET_LOG holds the store about 7.8 s, longer than the 5,000 ms finish); `recorder_unmount.test_failed_unmount_retried_and_reported` (a store call longer than both waits: exactly 2 records 0x0290: errno -EBUSY with try 1 in state TRANSFER, then errno 0 with the number of tries, 2 or more; VDD_SD off in the end). A stalled chunk READ is not simulated (the simulated card stalls writes only); the read command is GET_LOG, whose store call first writes the queued log records (the lead accepted this reading). Each checks VDD_SD off when the step of its row ended, the rail event inside that step (F/tests/recorder/src/test_unmount.c) | `unmount_result_dropped`: `unmount_now` calls `rst_unmount()` and drops its result (the reviewed code), named case `test_unconfigured_finish_times_out` (the abort's wait alone makes the VBUS case pass, so the finish case is the one that needs the waiting unmount) |
| R6-04 (FW l.915) | `hfxo_wanted` (rrec.c:533): BOOT, RECOVERY, CHARGING, TRANSFER, FACTORY_TEST; `rrec_hfxo_follow_state` (rrec.c:538) after every step and at the start of the boot sequence (F/modules/ring_recorder/src/rrec_boot.c:52) | `recorder_rails.test_hfxo_in_boot_and_recovery` (HFXO held from the boot card init through BOOT and, row 9, RECOVERY until the step into STANDBY, then 0 requests); `test_rails.c` header comment corrected to the table (F/tests/recorder/src/test_rails.c:6 to 10) | `no_hfxo_in_boot`: BOOT and RECOVERY removed from `hfxo_wanted` |
| R6-05 (FW l.125) | `recorder_actions.test_close_order` (F/tests/recorder/src/test_actions.c) also checks the frames: the stop press is timed so its mark falls in the middle of a chunk; every kept frame of the closed recording equals the simulated input's frame counter from frame 800 (FW l.460) and its inverse, none missing; the chunks' frames add up to the CLOSE duration; the last chunk is partial (1 to 8,191 frames); the duration is (mark - start) x 16 - 800 frames within one block of 256 frames plus 32 (FW l.443, l.460; the start and the mark are ms times) | the same | `close_drops_partial`: `rst_close(NULL, ...)` in `rrec_close` |
| R6-06 (FW l.1024, l.1029) | none in the product (the real path was already there) | `recorder_factory.test_tmic_records_type_2_for_2s`: T-MIC1 over the simulated USB to the real factory part and the real `rrec_test_recording`: result pass, VDD_MIC on once, the newest recording is type 2 with 32,000 frames (2 s, FW l.1024) within 256 frames; `recorder_factory.test_tsign_reports_mic_times`: T-SIGN: result pass, VDD_MIC on twice, the four reported times equal the rail's own on and off times (same ms or the next), each recording at least 1,000 ms and the second at least 1,000 ms after the first (FW l.1029) (F/tests/recorder/src/test_factory.c) | `test_recording_wrong_type`: the test recording opened as type 1 |
| R6-07 (FW l.161) | notes only: row C13 below | - | - |
| R6-08 | `rrec_post` keeps a job of the kinds VBUS_OUT, CHUNK_WRITE_FAILED, MIC_NO_BLOCK (and the jobs SHIP and UNMOUNT) that finds the queue full as one latched bit per kind (F/modules/ring_recorder/src/rrec_bridge.c:40 to 87); `latch_flush` queues it again when there is room, after every job and at least every 100 ms (rrec_bridge.c:89 to 103, 180 to 183); `rrec_idle` waits for the latch too (rrec_bridge.c:108). No new event log code | `recorder_actions.test_latched_events_not_lost`: the queue filled under `k_sched_lock()`, then each of the three events posted (refused by the full queue): rows 40, 37 and 36 are taken | - (not asked) |
| R6-09 | `run_retry` reads `mi` only after its own `rst_mount`; already mounted: result 0 and the open flag fact untouched (rrec_bridge.c:158 to 166) | `recorder_actions.test_retry_storage_reports_result` (existing) | - |
| R6-10 (accepted by the lead) | the ship (rpw_ship) runs on the recorder's thread for every path (RREC_JOB_SHIP, rrec.c:668), so the menu's power off, whose step runs on the screens thread (rscr.c:534 calls `ops->power_off()`), returns at once and the screens thread draws SCR_OFF while ship mode waits. `rscr_real.c` is NOT changed: the hand-over is in the join, so the file was not needed | `recorder_ship.test_ship_closes_each_part_first` asserts the thread name `rrec` at the end of step 1, for the factory path and the menu path | - |
| R6-13 | proof first: `fix1-rec-r613a.log` (the copy `vbat_read_at_0` with the stamps printed, the assertion unchanged): frame 0 at 424,299 ticks (42,429.9 ms), frame 1 at 434,300 ticks; spacing 10,001 ticks = 1,000.1 ms each, but 1,001 ms between the ms stamps 42,429 and 43,430, so the result depends on the sub-ms moment the case starts, which the shorter motor case moved. Then: the stand-in records `k_uptime_ticks()` too (F/tests/factory/src/common.c:134, common.h:56) and the case asserts each spacing in us: at least 1,000,000 and under 1,001,000 (F/tests/factory/src/test_screen.c:205 to 216). The frames are spaced by `k_sleep(1,000 ms)` in rfa.c `run_screen`, not by a periodic timer: tolerance 1 ms (a sleep ends on the next tick and the kernel adds one tick to a relative timeout: 100 us at 10,000 ticks per second). Old check: `fx_frame_ms[i] - fx_frame_ms[i - 1] == 1000`; new: `1,000,000 <= us < 1,001,000` | `factory_screen.test_frame_sequence` | the factory copy `vbat_read_at_0` must now fail only its own case |
| R6-14 (FW l.374) | `recorder_screens.test_battery_reaches_screens` (F/tests/recorder/src/test_screens.c): a boot with VBUS on a set world (1,000 uAh cell at 50.0 %, charging at 1 mA); the picture the join's values drew equals the picture of the typed values 50 %, "Charging", 30 min [CALC: 1,000 uAh x (1,000 - 500) / 1,000 at 1 mA = 0.5 h], and differs from 31 min, 51 % and "Full"; then with the charger completed: equal to 50 %, "Full", not "Charging". Harness: `rt_boot.ua` and `rt_boot.chg_forced` (F/tests/recorder/src/rt.h, rt.c `apply`) | the same | - |
| R6-17 | `rrec_st.test_recording` is an `atomic_t` (rrec_int.h:80), set and read with `atomic_set`/`atomic_get` (rrec.c:560, 655, 733, 778; rrec_bridge.c `au_no_block`; F/tests/recorder/src/rt.c, test_rows.c) | the existing cases that read it | - |
| F2 | `#ifdef CONFIG_RING_RHW_SIM` around `hook_added` and `clear_state` (F/modules/ring_audio/src/rau.c:48 to 50, 315 to 329) and `reboot_hook` (F/modules/ring_motor/src/rmo.c:95 to 112) | kit build (run k1 below): 0 of the three warnings | - |
| F1 | `clear_state` sets `halting` and waits for the capture loop to end (`k_sem_take(&halt_sem, ...)`, the same bound as `rau_halt`), rau.c:324; the drivers are reset before the reboot hooks run (rhw_sim_reboot), so the loop's read fails and it ends. In F/tests/recorder/src/rt.c the two 100 ms sleeps after `rhw_sim_reboot()` are removed (`rt_fresh`, `rt_reboot`); KEPT: the 100 ms sleep BEFORE the reboot in `rt_reboot` (not F1's: it lets the units finish what the last step started before the simulated reset) and the 50 ms sleep in `rt_fresh` before the reset (the same reason) | every recorder case after a simulated reboot (rows 64 and 65 of `test_mic_rail_only_in_recording` are the ones F1 broke) | - |

R6-07, row C13: **no product code sends `RC_EV_BLE_HIGHLIGHT` before the Bluetooth source of FW 7 exists** (FW l.161; the control part of FW 7 is outside step 6, plan row T2); `recorder_actions.test_ble_highlight_marks` and row 29 of `rt_run_row` inject the event with `rglue_event`, so the case proves the join's half (highlight marker, MH) only.

R6-06, the T rows: **T13** (T-MIC, FW l.1024, the join's half) = `recorder_factory.test_tmic_records_type_2_for_2s`; **T17** (T-SIGN, FW l.1029, the join's half: VDD_MIC on and off times) = `recorder_factory.test_tsign_reports_mic_times`.

R6-04, the corrected wording of plan row P6 (for the lead to write into step6-plan.md l.189): "P6 | FW 8.2 l.912 to l.920 | rails
per state: VDD_MIC only in `RECORDING`; VDD_SD in `BOOT`, `RECOVERY`, `RECORDING`, `TRANSFER`; HFXO on in `BOOT`, `RECOVERY`
(l.915), `RECORDING` (l.917) and `TRANSFER` (l.919), with USB in `CHARGING` (l.918), with the radio in `STANDBY` and the error
states (l.916, l.920), off in `SHIP` and `OFF` (l.914) | J | `recorder_rails.test_rails_per_state` (rail and HFXO facts after
every row), `recorder_rails.test_hfxo_in_boot_and_recovery` (HFXO through `BOOT` and `RECOVERY`, from the event log). Radio and
wake sources: existing parts; System ON idle: NP".

### FR1.2 Changes outside the unit (each one an addition; no existing declaration changed)

| File:line | What | Why | Its case |
|---|---|---|---|
| F/modules/ring_store/include/ring_store/rst.h:143 to 147 | `int rst_unmount_wait(int32_t timeout_ms);` | R6-03: `rst_unmount` returns -EBUSY at once while another store call runs (rst.c `op_take`, K_NO_WAIT); no public call waited | `store_svc.test_unmount_wait_waits_for_running_call` (F/tests/store/src/test_svc.c, after `test_busy_while_operation_runs`): with a close running on another thread, a 50 ms bound answers -EBUSY and changes nothing; a 5,000 ms bound waits for the close and unmounts (VDD_SD off) |
| F/modules/ring_store/src/rst.c:467 to 512 | the body of `rst_unmount` moved into `unmount_locked()` unchanged; `rst_unmount` = `op_take` + body; `rst_unmount_wait` = `k_mutex_lock(&op_lock, K_MSEC(timeout))` + body | the same | the same; the 11 store copies still match (edit check below) |
| F/modules/ring_xfer/include/ring_xfer/rxf.h:91 to 95 | `int rxf_stop(int32_t timeout_ms);` | R6-02: the class disables the stack only on VBUS removed; no public call closed USB with VBUS present (factory SHIP_ENTER, FW l.937) | `xfer_svc.test_stop_closes_usb_for_ship` (F/tests/xfer/src/test_svc.c, after `test_finish_and_abort`): a running command aborted with no response and not reported, the stack off when `rxf_stop` returns and still off with VBUS present, on again at the next VBUS ready and answering |
| F/modules/ring_xfer/src/rxf_class.c:49, 229 to 234, 259, 310, 353 to 371 | the flag `stopped`; VBUS ready clears it; the thread enables the stack only when it is clear; `rxf_start` clears it; `rxf_stop` | the same | the same |
| F/modules/ring_devices/include/ring_devices/rdev.h:85 to 89 | `int rdev_stop(void);` | R6-02: no public call stopped the devices part's advertising and link | none in tests/devices: that suite builds only `rdev_logic.c` (CONFIG_RING_DEVICES_LOGIC, no Bluetooth), so `rdev.c` cannot run there; the call is compiled in tests/recorder and the kit build and counted by `recorder_ship.test_ship_closes_each_part_first` (one call); its effect on advertising is not proven in these suites (they do not enable Bluetooth). It is proven in the step 2 two-device suite tests/bsim/control (built under the lead's word, below) |
| F/modules/ring_devices/src/rdev.c:46, 194 to 198, 498 to 514 | the flag `stopped`; `update_fn` returns at once when set; `rdev_stop` (stops this part's own advertising through `adv_stop()`, which acts only when this part advertises, and ends the link) | the same | the same |
| F/tests/bsim/control/ring_app/src/main.c (end of `run_c`), host_app/src/main.c (`C_WATCH_MS`, `watch_only`, the two checks in case 'C'), broken_edit.py (`radio_not_stopped`), run.sh (`VARIANTS`) | test C: at 55 s the ring calls `rdev_stop()` (ring check "C: ship close stops the radio (rdev_stop answers 0)"); host 1 watches only from 54 s and counts advertising reports with the HID service from 56 s on; at its evaluation (70 s): "C: the link ended after the ship close" and "C: no advertising after ship close" (0 reports). Broken copy `radio_not_stopped`: `rdev_stop` ends the link but does not set `stopped`, so the devices part advertises again after the disconnect; it must fail "HOST H1 CHECK C: no advertising after ship close" | R6-02, the lead granted tests/bsim/control/** for this one addition: the radio's close is proven over the simulated radio | its 15 copy edits match (`fix1-rec-editcheck-control.log`); runs c1 and c2 (FR1.6) |
| F/modules/ring_audio/src/rau.c:48 to 50, 315 to 329 | F2 guards; F1 wait in `clear_state` | F1, F2 of the units | tests/audio (unit run) and every recorder case after a reboot |
| F/modules/ring_motor/src/rmo.c:95 to 112 | F2 guard | F2 | tests/motor (unit run) |
| F/tests/factory/src/common.c:11, 134; common.h:56; test_screen.c:198 to 201, 205 to 216 | the ticks of each frame; the stamps printed; the spacing in us | R6-13 | `factory_screen.test_frame_sequence` |
| F/modules/ring_screens/src/rscr_real.c | NOT changed | R6-10 is met in the join (above; the lead accepted it) | - |
| F/modules/ring_screens/src/rscr.c:544 to 551 | `rscr_sync()` returns at once before `rscr_start` | lead's ruling 4: ship mode must not wait for a screens thread that does not exist | `recorder_a_noscreens.test_ship_without_screens_ends`; the 19 screens copies still match (`fix1-rec-editcheck-screens.log`), tests/screens in run u2 |
| F/modules/ring_rhw/include/ring_rhw/rrec_spec.h:329, 448 to 451 | `RREC_PAT_M2_MS 280u` (FW l.323) and `RREC_LOG_UNMOUNT_FAILED = 0x0290` | the lead's rulings on my two questions (lane s6-fix1 grants both) | `recorder_ship.test_ship_feels_whole_m2` (280 ms), `recorder_unmount.test_failed_unmount_retried_and_reported` (0x0290). No case in firmware/tests or tools counts or lists the codes (search: `fix1-rec-codes-search.txt`, its hits read: none counts 26), so none was brought to 27 |

### FR1.3 Runs and looks, in order (every one; logs in `build-logs/step6/`, each with its `.start`, `.end`, `.exit`, `.expect`)

All from ROOT with `RING_REMOTE_SRC=/root/ring-os/src-u-fix6 sh firmware/tools/remote.sh <name> "<command>"`; one at a time.

| Log | Command (short) | Remote exit | What it showed |
|---|---|---|---|
| `fix1-rec-editcheck1.log` (Mac) | `python3 -B -I fix1-rec-editcheck.py` (each unit's own broken_edit.py on a fresh copy) | 0 | `EDITCHECK 55 variants, 0 not matching` (recorder 18, store 11, xfer 10, audio 10, motor 5, the devices sed pattern 1) |
| `fix1-rec-r613a.log` | `broken_run.sh vbat_read_at_0` of tests/factory with the stamps printed, the assertion unchanged | 0 (`RESULT PASS`, `broken_run exit 0`: the copy fails its named case) | the cause of R6-13 (FR1.1): spacing 10,001 ticks each, the first ms spacing 1,001; `factory_screen.test_frame_sequence` failed with the copy |
| `fix1-rec-s1.log` | `tests/recorder/short_run.sh` | 1 | native_sim: build error (`maybe-uninitialized` in my test_factory.c); bsim: 49 of 52, the 3 of recorder_unmount failed: the transfer class runs "unconfigured" on its thread after the running command, so the event did not come while GET_LOG ran; the next two cases then started with the old command still running. Fixed in the tests (the l.178 cases give the core the event themselves; each case waits for the command to end) |
| `fix1-rec-s2.log` | the same | 0 | 52 of 52 cases on each board |
| `fix1-rec-s3.log` | twister on tests/store, xfer, audio, motor, devices, factory, both boards (no broken copies) | 0 | 221 of 221 cases on each board; native_sim "7 of 8 executed test configurations passed, 1 built (not run)" |
| `fix1-rec-k1.log` | `tests/screens/short_run.sh`; then the kit build (`nrf54lm20dk/nrf54lm20a/cpuapp`, sysbuild) | 0 | pictures listed: 21, bad: 0 on each target; `fix1-rec-compare-screens.txt` (u9-compare.py against design/software/os/screens/manifest.md and step 5's log) ends `RESULT EQUAL`; `dk build exit 0`, `F2 warnings: 0` (the base kit build `j-prod1.log` had the three) |
| `fix1-rec-u1.console` (local, cut by a network outage at about 13:54; the server's own log is to be copied by the lead as `fix1-rec-u1-server.log`) | `RING_OUT=/ws/out/fix1rec-u1 bash tools/unit_run.sh tests/recorder tests/store tests/xfer tests/audio tests/motor tests/devices tests/factory`, then the cases' prints and statuses | 255 locally (link cut); the lead read the server's last result line: `UNIT FAIL tests/recorder tests/store tests/xfer tests/audio tests/motor tests/devices tests/factory broken-recorder broken-xfer` | files from BEFORE the lead's rulings. Both test parts exit 0. broken-recorder: 17 of 18 copies failed their named case on both boards; `ship_screen_on` did not (cause and new edit in FR1.1). broken-xfer: `usb_on_without_vbus` also failed my new `xfer_svc.test_stop_closes_usb_for_ship` (it counted enable events; the copy enables at start), so the count was removed. broken-store, -audio, -motor, -devices RESULT PASS in the local console |
| (Mac) | rulings applied: `RREC_PAT_M2_MS`, `RREC_LOG_UNMOUNT_FAILED`, `rscr_sync` before start, case `recorder_a_noscreens`; `fix1-rec-editcheck3.log` `EDITCHECK 55 variants, 0 not matching`; `fix1-rec-editcheck-screens.log` 19 of 19 screens copy edits exit 0 | - | a misplaced duplicate of the base copy of rrec_spec.h, written into fix1-rec-base/ under a wrong name, was deleted by me in the same command that wrote it; the base copy is `fix1-rec-base/modules/ring_rhw/include/ring_rhw/rrec_spec.h` |
| `fix1-rec-s4.log` | recorder short_run; twister tests/xfer and tests/screens on both boards; recorder `broken_run.sh ship_screen_on`; xfer `broken_run.sh usb_on_without_vbus` | 0 | 53 of 53 recorder cases on each board; 104 of 104 xfer and screens cases on each board; both copies `RESULT PASS` (ship_screen_on fails its named case on both boards; usb_on_without_vbus fails only its named case) |
| `fix1-rec-u2.log` | `RING_OUT=/ws/out/fix1rec-u2 bash tools/unit_run.sh tests/recorder tests/store tests/xfer tests/audio tests/motor tests/devices tests/factory tests/screens`, then the cases' prints (l.7537 to 7630), every case's status from twister.json (l.7632 to 8292), `tests/screens/short_run.sh`, the kit build; exit = unit_run's | 0 | l.7535 `UNIT PASS tests/recorder tests/store tests/xfer tests/audio tests/motor tests/devices tests/factory tests/screens`; 330 of 330 cases per board (l.31, l.62); every broken stage `RESULT PASS` (recorder l.822, store l.2335, xfer l.3716, audio l.4987, motor l.5457, devices l.5523, factory l.6933, screens l.7533); twister.json: 330 cases passed per board and one build-only configuration `ring_xfer.real_build` "not run" on native_sim; pictures listed: 21, bad: 0 per target (l.8313, l.8332), `fix1-rec-compare-screens2.txt` ends `RESULT EQUAL`; `dk build exit 0`, `F2 warnings: 0` (l.8423, l.8425; the 3 remaining "warning:" lines are Kconfig messages, as in the base kit build `j-prod1.log`) |
| `fix1-rec-c1.log` | `RING_OUT=/ws/out/fix1rec-c1 bash tests/bsim/control/run.sh` (tests A B C D F G T on the simulated chip) | 0 | l.936 `RESULT PASS`; test C l.372 `TEST C RESULT PASS (31 checks passed)` |
| `fix1-rec-c2.log` | `RING_OUT=/ws/out/fix1rec-c2 bash tests/bsim/control/run.sh --broken radio_not_stopped` | 0 | l.100 the copy failed its named check, l.101 `RESULT PASS` |
| `fix1-rec-s5.log` | `RING_OUT=/ws/out/fix1rec-s5 bash tests/recorder/short_run.sh` (after the lead's ruling on 0x0290) | 0 | 53 of 53 cases on each board; 2 records 0x0290 (try 1, then errno 0 try 6) |
| `fix1-rec-u3.log` | `RING_OUT=/ws/out/fix1rec-u3 bash tools/unit_run.sh tests/recorder` on the final files | 0 | l.804 `UNIT PASS tests/recorder`; l.802 `RESULT PASS` (18 copies) |
| (Mac) | final audit `fix1-rec-audit.py` on my final reply | - | a first look found 2 without a match, both faults of the audit script (it read "FW l.178" as a log line, and took the failed-unmount count from the broken copy's print instead of the cited run's); fixed in the script; the saved `fix1-rec-audit.txt` ends `AUDIT 68 claims checked, 0 without a match`. Left on the server: my run folder /ws/out/fix1rec-c2 |

### FR1.4 The cited run: each finding's case and copy, by line of `build-logs/step6/fix1-rec-u2.log`

Case status lines (twister.json, native_sim / simulated chip); copy lines ("the named case failed, as required", native_sim /
simulated chip). The run's last result line, quoted: `UNIT PASS tests/recorder tests/store tests/xfer tests/audio tests/motor
tests/devices tests/factory tests/screens` (l.7535); the log's own last line is the local log path.

| Finding | Case: native_sim / chip | Copy: native_sim / chip | The case's own print (l.7537 to 7630) |
|---|---|---|---|
| R6-01 | `recorder_ship.test_ship_feels_whole_m2` l.7678 / 7999 | `ship_cuts_m2` l.607 / 617 | "M2 segment 0 lasted 80000 us", "segment 1 lasted 120000 us", "segment 2 lasted 80000 us", "M2 lasted 280000 us on the MOTOR pin" |
| R6-02 | `recorder_ship.test_ship_closes_each_part_first` l.7677 / 8000; `recorder_a_noscreens.test_ship_without_screens_ends` l.7684 / 8005 | `ship_screen_on` l.642 / 653 | "ship (factory): ... SHPHLDCONFIG 12, USB disable 11, VDD_SD off 9; ... VDD_MIC 0, VDD_SD 0, USB 0, screen blanked 1, radio stops 1, beacon stopped 0"; "ship (menu): ... screen blanked 1"; "ship without screens: idle 1, SHPHLDCONFIG at 5, ship task at 7" |
| R6-03 | `recorder_unmount.test_vbus_out_during_read_command` l.7681 / 7977; `test_unconfigured_finish_times_out` l.7680 / 7978; `test_failed_unmount_retried_and_reported` l.7679 / 7979; `store_svc.test_unmount_wait_waits_for_running_call` l.7736 / 8039 | `unmount_result_dropped` l.684 / 701 | "the unconfigured step took about 7760 ms"; "unmount: 11 failed unmounts reported, VDD_SD now 0, state CHARGING", "record 1: errno -16, state TRANSFER, try 1" to "record 11: ... try 11"; "rst_unmount_wait waited 450 ms for the running close" |
| R6-04 | `recorder_rails.test_hfxo_in_boot_and_recovery` l.7669 / 8012 | `no_hfxo_in_boot` l.725 / 736 | "HFXO BOOT: requests 1 at the boot card init", "HFXO RECOVERY: requests 1 at the boot card init" |
| R6-05 | `recorder_actions.test_close_order` l.7654 / 7980 | `close_drops_partial` l.768 / 787 | "close frames: 6 chunks, 44000 frames in the chunks, CLOSE duration 44000, last chunk 3040 frames, captured to the mark 44000 ... 0 frames not as captured" (and 43984 on the other board) |
| R6-06 (T13, T17) | `recorder_factory.test_tmic_records_type_2_for_2s` l.7683 / 7997; `test_tsign_reports_mic_times` l.7682 / 7998 | `test_recording_wrong_type` l.810 / 820 | "T-MIC1: recording 1 type 2, 32000 frames, 4 chunks"; "T-SIGN: reported on 235838 off 236911 on 237912 off 238985 ms; rail on 235838 off 236911 on 237912 off 238985 ms" |
| R6-08 | `recorder_actions.test_latched_events_not_lost` l.7645 / 7989 | - | "latch: 33 jobs filled the queue, the post of event 1 answered -42" (and events 16, 17) |
| R6-09 | `recorder_actions.test_retry_storage_reports_result` l.7648 / 7986 | - | - |
| R6-02 USB | `xfer_svc.test_stop_closes_usb_for_ship` l.7778 / 8114 | - | - |
| R6-13 | `factory_screen.test_frame_sequence` (scenario ring_factory.sim) l.7885 / 8215 | factory copy `vbat_read_at_0`: its failed cases are now `factory_cmd.test_result_layout factory_motor.test_reads_and_timing` (l.6301, 6364); before the fix `fix1-rec-r613a.log` l.83, 146 listed `factory_screen.test_frame_sequence` too | "T-SCREEN stamps: frame 1 at 43930 ms, 439301 ticks ..., spacing 1000 ms" |
| R6-14 | `recorder_screens.test_battery_reaches_screens` l.7676 / 8013 | - | "SCR_CHARGING frames: from the join 7655bffd0ef9a850; typed 50 % Charging 30 min 7655bffd0ef9a850, 31 min 591387ab3360d06d, 51 % 48e46b48e88ce877, Full e228d8ba8a36c877" |

The 0x0290 record (lead's ruling after run u2): in u2, one record per failed try on a card stalling every write made the
store's work longer (11 tries, l.7579 of fix1-rec-u2.log). Now one record at the first failed try and one at the end:
`fix1-rec-u3.log` l.806 `unmount: record 1: errno -16, state TRANSFER, try 1`, l.807 `unmount: record 2: errno 0, state
CHARGING, try 6`, l.808 `unmount: 2 records 0x0290` (and l.812 to 814 on the simulated chip). The rows of R6-03 in FR1.4 above
cite run u2 (files before this change, the failed-unmount case then asserted one record per try); run u3 is the recorder's run
on the final files: l.22, l.44 `53 of 53 executed test cases passed`, copy `unmount_result_dropped` fails its named case on both
boards (l.665, l.681), l.802 `RESULT PASS` (all 18 copies), l.804 `UNIT PASS tests/recorder`.

### FR1.5 State of every finding

| Finding | State | Proof |
|---|---|---|
| R6-01 | fixed | FR1.4 |
| R6-02 | fixed (recording, storage, USB, screen in the recorder suites; radio over the simulated radio in tests/bsim/control, run c1) | FR1.4, FR1.6 |
| R6-03 | fixed | FR1.4 |
| R6-04 | fixed; plan row P6's corrected wording in FR1.1 for the lead | FR1.4 |
| R6-05 | fixed (the case) | FR1.4 |
| R6-06 | fixed (cases; T13, T17 mapped) | FR1.4 |
| R6-07 | done (notes) | FR1.1 |
| R6-08 | fixed | FR1.4 |
| R6-09 | fixed | rrec_bridge.c:158 to 166; FR1.4 |
| R6-10 | fixed in the join, accepted by the lead | FR1.4 (thread `rrec`) |
| R6-11, R6-12 | the lead's (brief) | - |
| R6-13 | fixed, cause shown first | FR1.1, FR1.4 |
| R6-14 | fixed | FR1.4 |
| R6-15, R6-16 (F1, F2) | fixed | kit build F2 warnings: 0; recorder suites without the F1 sleeps |
| R6-17 | fixed | rrec_int.h:80 |

### FR1.6 The two-device radio check (tests/bsim/control)

- `fix1-rec-c1.log` (the suite on the delivered files): l.330 `RING CHECK C: ship close stops the radio (rdev_stop answers 0) PASS
  (t=55001)`; l.363 `HOST H1 CHECK C: the link ended after the ship close PASS`; l.364 `advertising reports after the ship close:
  0`; l.365 `HOST H1 CHECK C: no advertising after ship close PASS`; the other tests unchanged and passing (l.936 `RESULT PASS`).
- `fix1-rec-c2.log` (copy `radio_not_stopped`): l.91 `advertising reports after the ship close: 131`; l.92 `HOST H1 CHECK C: no
  advertising after ship close FAIL`; l.100 "test C failed on its named check, as required"; l.101 `RESULT PASS`.
- The suite runs on the simulated chip only (run.sh's BOARD), so the radio proof is on one target; the recorder suites' ship case
  checks that the join calls `rdev_stop` once (on both targets).

### FR1.7 What I could not do

- `rdev_stop`'s effect on advertising is not proven in the recorder suites (no Bluetooth there); it is proven over the simulated radio by tests/bsim/control test C on the simulated chip only (FR1.6).
- A stalled chunk READ is not simulated (the simulated card stalls writes only); the read command of the R6-03 cases is GET_LOG.
- With the transfer class as built, "unconfigured" reaches the core only after the running command ended (rxf_class.c runs its
  bus events on the transfer thread), so the l.178 cases give the core the event themselves; in the product a timed-out finish
  through the class's own event order was not seen.
- The ztest order of suites (name order) is relied on by `recorder_a_noscreens`; the case checks it (`rt_screens_started`).
- My full run u1 was cut locally by a network outage; its server log was copied by the lead (`fix1-rec-u1-server.log`).
- tools/build_all.sh: not run by me (brief).

### questions_for_owner

none


## Fix round 2 (review 2 of step 6, docs/step6-review-2.md: findings R2-01 to R2-08, R2-10, note R2-11)

Started 2026-11-13 17:04:51 CET (`date`), budget 3 hours (lead). Version read: commit c26ae988 (fix round 1). No git. Raw
evidence: `build-logs/step6/fix2-rec-*`; base copies of the files changed: `build-logs/step6/fix2-rec-base/`. Line numbers
below are of the delivered files after this round ("F/" = firmware/); the round 1 sections above cite c26ae988.

### FR2.1 What changed, per finding

| Finding | Change (file:line) | Case | Copy |
|---|---|---|---|
| R2-01 | The retry job no longer decides by itself: `rrec_unmount_retry` (F/modules/ring_recorder/src/rrec.c:469 to 477) runs an empty core step, `rglue_event(RC_EV_COUNT)` (an event the core ignores, core.c:179), so the decision and the unmount happen in `rails_follow_state` (rrec.c:627 to 639) under the glue's lock, from the state at that moment. The counters (`unmount_tries`, `unmount_ep_err`, `step_unmount_tried`, `step_finish_waited`, rrec.c:281 to 284) are written only inside core steps; ship mode's unmount uses none of them (`ship_unmount`, rrec.c:335 to 352). Test hook `rrec_test_set_retry_hook` (rrec_int.h) at the start of the job | `recorder_unmount.test_retry_never_takes_the_card`: VBUS removed while GET_LOG holds the store; the retry job is held at its start; the wearer starts a recording; then the retry goes on: still RECORDING with VDD_SD on (F/tests/recorder/src/test_unmount.c) | `retry_outside_lock`: the job checks the state, then (hook) unmounts outside the lock (the code of round 1) |
| R2-02 | `unmount_ep_err` (rrec.c:282) is this episode's last errno: set at each failed try (rrec.c:320), cleared when the episode ends (`unmount_tries_end`); when the state wants the card again the end record carries it (rrec.c:632) | `recorder_unmount.test_episode_end_keeps_its_errno`: an episode starts in CHARGING (row 46 while GET_LOG holds the store); still held, TRANSFER wants the card (row 39): 2 records, both errno -EBUSY | `end_errno_stale`: the episode's errno is not kept (the end record then says 0) |
| R2-03 | One wait per step for the command (`step_finish_waited`, rrec.c:574, 583) and one for the unmount (`step_unmount_tried`, set in `unmount_now`; the rails skip a second try, rrec.c:636; reset at the end of the step, rrec.c:745). **Worst-case time one step holds the glue's lock:** 5,000 ms (`rxf_finish`, FINISH_WAIT_MS) + 5,000 ms (`rst_unmount_wait`) + the unmount's own time when it succeeds (wait for the queued chunks, write the queued log records, deinit, rail off: the card's time, not bounded by a number of the join) = **about 10 s plus that card time** (before: up to about 15 s plus it, review 2). A retry step: at most 5,000 ms plus the same card time | `recorder_unmount.test_one_wait_each_per_step`: row 46 while GET_LOG holds the store about 21 s: the step held the lock under 11,500 ms (measured 10,000 ms in run s2) | `rails_tries_again`: the rails' pass waits again |
| R2-04 (FW l.937) | `ship_unmount` (rrec.c:335 to 352): if the unmount fails within its wait, 0x0290 (try 1), USB closed first (`rxf_stop`), the unmount tried once more, 0x0290 with that answer (try 2); ship mode goes on in any case (rrec.c:424 to 428) | `recorder_ship.test_ship_closes_usb_before_second_unmount`: factory SHIP_ENTER while another thread's store call (GET_LOG's read of the log) holds the store about 24 s: ship mode reaches SHPHLDCONFIG; the USB disable comes before the second try's 0x0290 record (F/tests/recorder/src/test_ship.c) | `ship_storage_before_usb`: no second try (the order of round 1) |
| R2-05 (FW l.937) | `RREC_SHIP_SCREEN_WAIT_MS 1000u` (F/modules/ring_rhw/include/ring_rhw/rrec_spec.h:308, beside the other ship constants); `screen_wait` (rrec.c:369 to 379): `rscr_sync()` runs on a work queue of the join's own and ship mode waits for it at most that long (rrec.c:444) | `recorder_ship.test_ship_with_stuck_screens_goes_on`: the draw lock held (the screens thread cannot draw): SHPHLDCONFIG within 280 + 100 + 1,000 + 300 ms of the power off (measured 1,281 ms in run s2) | `screen_wait_forever`: `K_FOREVER` |
| R2-06 | When a latched VBUS job is finally queued, its event is the one of the VBUS level read then (F/modules/ring_recorder/src/rrec_bridge.c:98 to 101) | `recorder_actions.test_latched_vbus_follows_the_level`: full queue, VBUS out latched, VBUS in dropped: the core ends in CHARGING with VBUS present, no row 40. The VBUS part of `test_latched_events_not_lost` moved here (it posted VBUS out with VBUS present, which this rule now answers with VBUS in) | `latched_vbus_stale` |
| R2-07 (FW l.1029) | the T-SIGN case bounds each recording from above: under 1,000 + 50 (FW l.460) + 100 ms (the join's allowance for the close; FW gives no number) | `recorder_factory.test_tsign_reports_mic_times` (F/tests/recorder/src/test_factory.c) | `tsign_2s`: 2 s recordings |
| R2-08 (FW l.179) | the case's store is held about 6 s (1,000 ms per write, 6 records), longer than one 5,000 ms wait, so each wait alone is not enough | `recorder_unmount.test_vbus_out_during_read_command` | `abort_no_wait`: no wait for the command after the abort; the case fails by itself (it does not depend on an earlier case) |
| R2-10 | the citation in FR1.1, row R6-03: `rrec.c:509 at commit c26ae988` | - | - |
| R2-11 (note) | comment at the guard (rrec.c:416 to 417): not reached in the product, every row into SHIP or OFF from RECORDING closes first (FW l.165) | - | - |
| R2-12, R2-13 (notes) | no change (R2-12 is FR1.6's limit; R2-13: after a failed ship the radio stays stopped until a reboot) | - | - |

### FR2.2 Changes outside the unit

- F/modules/ring_rhw/include/ring_rhw/rrec_spec.h:308: `RREC_SHIP_SCREEN_WAIT_MS 1000u` (addition; the lead's ruling R2-05).
- Nothing else outside ring_recorder and tests/recorder. tests/bsim/control is not run again: rdev and the ship path's radio
  part are not changed in this round.

### FR2.3 Runs, in order

| Log | Command | Remote exit | What it showed |
|---|---|---|---|
| `fix2-rec-editcheck1.log` (Mac) | `fix1-rec-editcheck.py` | 0 | 63 variants, 1 not matching: `unmount_result_dropped`'s text now also matched the two unmount lines of `ship_unmount`; those lines got comments; `fix2-rec-editcheck3.log` `EDITCHECK 63 variants, 0 not matching` |
| `fix2-rec-s1.log` | `tests/recorder/short_run.sh` | 1 | 2 case faults of mine: `test_retry_never_takes_the_card` asserted an end errno -EBUSY, but in its scenario a regular step's rails unmounted successfully (errno 0, try 3) before the recording started, which is correct; the errno check moved to the new case of R2-02. `test_one_wait_each_per_step` measured the lock from another thread and a retry step took the lock first (15,000 ms); it now measures the end of the step itself |
| `fix2-rec-s2.log` | the same | 0 | 59 of 59 cases on each board |
| `fix2-rec-u1.log` | `RING_OUT=/ws/out/fix2rec-u1 bash tools/unit_run.sh tests/recorder` | 0 | l.22, l.44 `59 of 59 executed test cases passed` (native_sim, simulated chip); l.1199 `RESULT PASS` (26 copies); last result line l.1201 `UNIT PASS tests/recorder` |

### FR2.5 The eight new copies in run u1 (lines of `fix2-rec-u1.log`: "the named case failed, as required", native_sim / simulated chip; the other cases that failed with it)

| Finding | Copy | Lines | Failed with it |
|---|---|---|---|
| R2-01 | `retry_outside_lock` | l.871 / 887 | none |
| R2-02 | `end_errno_stale` | l.920 / 941 | `test_failed_unmount_retried_and_reported` and others of the unmount suite (they read the same end record) |
| R2-03 | `rails_tries_again` | l.970 / 986 | none |
| R2-04 | `ship_storage_before_usb` | l.1014 / 1027 | `recorder_ship.test_ship_feels_whole_m2` (runs after it in the suite: the copy's ship mode left the card mounted and its retries running when the next case began) |
| R2-05 | `screen_wait_forever` | l.1052 / 1064 | none |
| R2-06 | `latched_vbus_stale` | l.1097 / 1117 | none |
| R2-07 | `tsign_2s` | l.1141 / 1152 | `recorder_factory.test_tmic_records_type_2_for_2s` (its 2 s recording is 4 s in the copy) |
| R2-08 | `abort_no_wait` | l.1181 / 1197 | none: the FW l.179 case fails by itself |

### FR2.6 State of every finding

| Finding | State |
|---|---|
| R2-01, R2-02, R2-03, R2-04, R2-05, R2-06 | fixed: case and copy (FR2.1, FR2.5) |
| R2-07, R2-08 | fixed: the cases bound/detect alone (FR2.5) |
| R2-09 | the lead's (done) |
| R2-10 | fixed (FR1.1, row R6-03) |
| R2-11 | comment added (rrec.c:416 to 417) |
| R2-12, R2-13 | notes, no change |

### FR2.4 What I could not do

- The worst-case lock time has a part that no number bounds: the unmount's own time on the card (FR2.1, R2-03).
- R2-04's store holder in the case is a store call from a test thread (GET_LOG's read), not a USB command: with the factory
  SHIP_ENTER as the running command, no second command can hold the store (the class answers BUSY).
- If the screens thread stays stuck, the work item of `screen_wait` stays pending; a later ship mode waits its 1,000 ms again.

### questions_for_owner (round 2)

none

RESULT: done, R2-01 to R2-08, R2-10 and the R2-11 comment are in, each of the eight new broken copies fails its named case on both simulated targets, and the unit run ends `UNIT PASS tests/recorder` (fix2-rec-u1.log l.1201).
