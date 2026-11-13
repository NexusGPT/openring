# sys notes: unit U7 of software step 6 (saved time, firmware update, persistent settings, crash block, watchdog)

Builder: U7 helper. Started 2026-11-13 05:52 CET (`date`). Contract: `firmware/docs/step6-plan.md` (read in full, rulings included), `firmware/docs/rhw-notes.md` sections 2 and 3, `firmware/modules/ring_sys/include/ring_sys/rsy.h` (frozen, not touched). No git was run. "FW l.N" = line N of `design/firmware.md`. Raw evidence: `firmware/build-logs/step6/u7-*`.
Cited proof run: `build-logs/step6/u7-full1.log` (command `bash tools/unit_run.sh tests/sys`, exit 0, `u7-full1.exit` holds 0). Its last result line: `UNIT PASS tests/sys` (line 1169); the broken-copy part ends `RESULT PASS` (line 1167).

## 1. Files written (all under `firmware/`)

| Path | What |
|---|---|
| `modules/ring_sys/CMakeLists.txt`, `Kconfig`, `zephyr/module.yml` | the module; `RING_SYS_LOGIC` (pure), `RING_SYS` (thin, selects `REBOOT` outside the simulation), `RING_SYS_FATAL_HANDLER` (off under ZTEST, which has its own handler) |
| `modules/ring_sys/src/rsy_logic.h`, `rsy_logic.c` | pure part, no kernel call: update-allowed rule, FW_BEGIN and FW_DATA checks, running CRC-32, self-test step machine and its 30 s window, crash block encode and decode, watchdog feed decision, saved-time guess |
| `modules/ring_sys/src/rsy.c`, `rsy_int.h`, `rsy_fatal.c` | thin part: hardware only through `rhw_image()`, `rhw_persist()`, `rhw_retained()`, `rhw_wdt()`, `rhw_clock()`; the fatal path (`rsy_fatal`) and the override wrapper |
| `modules/ring_sys/src/rsy_hw_real.c` | real drivers (image slot 1 and MCUboot calls, settings, retained memory, `wdt31`); kit build only, each registers only when its node or option exists |
| `tests/sys/` | five suites (`src/test_update.c`, `test_time.c`, `test_persist.c`, `test_crash.c`, `test_wdt.c`), `src/common.[ch]`, `src/crash_expect.h` (typed bytes), `broken_edit.py`, `broken_run.sh`, `kfacts.sh`, `kitcompile/` (manual kit compile check) |

## 2. Readings and choices (mine; each is open for the lead)

1. FW_BEGIN checks "not allowed" first (`NOT_ALLOWED` 11, ruling D12), then `BAD_ARG`. A refused FW_BEGIN leaves a running earlier update as it was.
2. "Above 30 percent" is `soc_x10 > 300` (RREC_UPDATE_MIN_SOC_X10); VBUS present allows any level.
3. FW_END ends the update whatever it answers: one FW_END per FW_BEGIN (a second one answers FW_ERROR). FW_END does not reboot (the join does, after the OK).
4. A zero-length FW_DATA inside the range answers OK without a write. Length limits 1 to 4,096 are the transfer unit's.
5. Self-test: storage and Bluetooth always needed, USB only with VBUS. Window ends 30,000 ms after the start: log RREC_LOG_SELFTEST result 2 (mask of items passed) then reboot `RHW_REBOOT_SELFTEST_FAIL`. Result 1 is used only if the confirm write fails. `is_confirmed` negative is treated as "nothing to do" (not reboot-looped); not testable on the simulation.
6. Saved time: `rsy_time_save` with `utc_ms <= 0` (clock not set) saves nothing and clears an older saved time; the guess is what was loaded at `rsy_init`, so a save in this boot is not a guess until the next boot. The saved flag is never cleared after a boot (a later reset without a save would log the old time again as a guess).
7. Crash block in retained memory: this unit's magic "CRSH" (4 bytes) in front and a CRC-32 behind the 288-byte block of FW l.1063 (296 bytes). An invalid area is left untouched. `rsy_crash_take` returns gpregret1 with the block, then clears both.
8. Watchdog: "in the last 2 s" is `age <= 2000 ms`. `rsy_recording(true)` forgets earlier progress reports, so reports of an earlier recording never feed a new one. The first feed of a recording may be refused until both threads have reported (the 8 s timeout covers it).
9. The ARM exception frame fields (`basic.pc`, `basic.lr`, `basic.xpsr`) and the stack words from the frame are read only under `CONFIG_ARM`; compile-checked for the dev kit, never run.

## 3. Rows of the plan mapped to cases and log lines

Log lines cited are of `u7-full1.log`: lines 8 to 29 (twister on `native_sim`, 24 of 24 cases passed, exit 0), 30 to 51 (same on `nrf54lm20bsim/nrf54lm20a/cpuapp`, 24 of 24, exit 0), and the broken-copy part (lines 52 to 1167) where each named case shows `FAIL` and the other cases of the suites show `PASS` (for example lines 233 to 260). The cases also print `EVIDENCE` lines with the measured values; twister shows them only for a failing run (`u7-short2.console` holds the output of an earlier run, with the evidence lines of the passing cases).

| Row | Rule | Case (suite.case) | Log line |
|---|---|---|---|
| C23 and T29 | watchdog 8 s, fed every 1 s only with progress of both threads in the last 2 s (or no recording) | `sys_wdt.test_feed_only_with_progress` (10 s of progress feeds about 1 per second; one thread stalling stops the feeding and the simulated watchdog reports it would reset), `test_progress_window_edges` (2,000 ms counts, 2,001 ms does not, never reported does not), `test_feed_when_no_recording` (30 feeds in 30.5 s, spacing 1 s), `test_start_8s_once`, `test_new_recording_clears_old_progress`. The reset itself: not provable without hardware (no watchdog reset in the simulation) | `u7-full1.log` lines 117 to 121 and 180 to 184; broken copy `feed_without_progress` fails the named case, listed in section 4 |
| T4 | time saved on SHIP and OFF; after the boot it is a guess; clock stays not set | `sys_time.test_saved_on_ship_and_off`, `sys_time.test_guess_is_not_set` (checks `rtime_is_set()` false, `rtime_utc_ms()` 0, no clock update). The chunk flag bit 5 and "--:--" are U3's and the screens' (`audio_chunk.test_time_not_set`) | lines 103, 104 |
| T5 | flash layout 64 + 976 + 976 + 20 = 2,036 KB | `sys_update.test_layout_sums_to_2036_kb` (literals typed from FW l.1010). Swap and rollback: not provable without hardware (MCUboot does not run in the simulated builds) | line 109 |
| T6 | USB path writes only slot 1, size limit 999,424, data end limit | `sys_update.test_size_limit` (999,424 accepted, 999,425, 0 and 4,294,967,295 refused with BAD_ARG, nothing erased), `test_data_end_limit`, `test_writes_only_slot1` (every image write inside 0..999,424 at the offset sent, after the erase; slot content equals the data). Settings only through the settings API: no other call in `rsy.c` (the unit has no flash call besides `rhw_image()`). MCUboot write protection (T7) is not this unit's | lines 107, 113 to 115 |
| T8 | FW_BEGIN erases slot 1; FW_DATA blocks; FW_END checks CRC-32, requests the test upgrade; reboot after the OK | `sys_update.test_sequence` (order erase, write, read-back, request; no reboot by FW_END), `test_end_bad_crc_fw_error` (wrong CRC, one byte differing, incomplete image, write error: FW_ERROR, no request). `recorder_rows.test_fw_end_row` is the join's | lines 108, 113 |
| T9 | self-test within 30 s; no microphones; all pass confirms; otherwise reboot without confirming | `sys_update.test_self_test_pass_confirms` (with VBUS three items, without two; one confirm; no reboot at 30 s), `test_self_test_timeout_reboots` (no reboot at 29.9 s, reboot 30.0 s after the start, reason 5, never confirmed, log result 2), `test_self_test_no_mic` (no rail write and no microphone input call in either run). That storage, Bluetooth and USB are reported by the join is `recorder`'s | lines 110 to 112 |
| T10 | update only with battery above 30 % or VBUS | `sys_update.test_allowed_rule` (300 without VBUS gives 11, 299 gives 11, 301 accepted, VBUS at 0 % and 30.0 % accepted; refused begin erases nothing) | line 106 |
| T11 | factory flag only cleared by SHIP_ENTER, kept by SHIP_SAMPLE, survives reboot | `sys_persist.test_factory_flag_survives_reboot` (1 over three reboots, kept by a time save, cleared by the write and clear after a reboot, the saved time kept by the flag write, a failing write reported and the flag unchanged), `test_blank_settings_read_as_clear`. The command rules (NOT_ALLOWED, 0x7E, 0x7F) are `factory_cmd.test_flag_rules` (U8) | lines 100, 101 |
| T28 | crash block format and boot copy once | `sys_crash.test_block_format` (296 stored bytes equal the bytes in `crash_expect.h`, generated by `u7-gen-crash-expect.py` from the FW layout with zlib CRC; name cut to 15 characters, short and long stack lengths), `test_boot_copies_valid_block_once` (first take 1, second 0, retained and gpregret1 cleared), `test_invalid_block_ignored` (blank, 0xFF, four damaged blocks), `test_fatal_path_order` (block, then gpregret1, then reboot reason 6; no hang when every call is refused). The handler on the real chip and retained RAM across a real reset: not provable without hardware | lines 94 to 98 |

## 4. Broken copies (plan list of U7): each fails its named case on both targets

Local check that each edit matches exactly once: `u7-editcheck.log` (8 variants, RESULT PASS). Run: `u7-full1.log`, lines 52 to 1167.

| Copy | Named case | Other cases that failed with it (from `u7-full1.log`) |
|---|---|---|
| `size_999425_ok` | `sys_update.test_size_limit` | none (both targets) |
| `end_off_by_one` | `sys_update.test_data_end_limit` | none |
| `writes_slot0` | `sys_update.test_writes_only_slot1` | `sys_update.test_data_end_limit`, `sys_update.test_sequence` (both targets) |
| `selftest_31s` | `sys_update.test_self_test_timeout_reboots` | none |
| `allowed_at_30` | `sys_update.test_allowed_rule` | none |
| `feed_without_progress` | `sys_wdt.test_feed_only_with_progress` | `sys_wdt.test_new_recording_clears_old_progress`, `sys_wdt.test_progress_window_edges` (both targets) |
| `crash_copied_twice` | `sys_crash.test_boot_copies_valid_block_once` | none |
| `guess_marked_set` | `sys_time.test_guess_is_not_set` | none |

The red state before the unit's code: the broken copies are the red runs (each fails its named case on the unit's own suites). A separate red-first run of the suites against an empty module was not made: the suites cannot build without the unit's code.

## 5. Kit facts

Evidence: `u7-kfacts.console`, `u7-kfacts2.console`, `u7-short1.console`, `u7-short2.console` (counts and file names only, no kit lines printed).

- **K9 (image API names): true.** `boot_request_upgrade`, `boot_is_img_confirmed`, `boot_write_img_confirmed`, `BOOT_UPGRADE_TEST` each appear in `include/zephyr/dfu/mcuboot.h` (counts 2, 1, 3, 3); `flash_img_init_id`, `flash_img_buffered_write`, `flash_img_check` appear in `flash_img.h`. The real file calls the three `boot_` functions and writes slot 1 through the flash device of its partition; it compiles and links for the nRF54LM20 development kit (`u7-kit5.console`: exit 0, no warning in a ring_sys file), with `CONFIG_FLASH_MAP`, `CONFIG_STREAM_FLASH`, `CONFIG_IMG_MANAGER` and `CONFIG_MCUBOOT_IMG_MANAGER` set. Two kit findings: `flash_area_open` and the `FIXED_PARTITION_*` size and offset macros are deprecated in this kit (replaced in the real file); `sys_reboot` needs `CONFIG_REBOOT` (the module selects it outside the simulation). Never run.
- **K10 (settings back end on the RRAM): not settled.** The settings subsystem offers the NVS, ZMS, file and FCB back ends (Kconfig counts 5, 10, 3, 3); `settings_save_one`, `settings_load_subtree_direct`, `settings_name_steq` exist. 81 files of the SDK's samples, boards and applications name `SETTINGS_ZMS` and 109 name `SETTINGS_NVS`; no board file of `zephyr/boards/nordic` names either. Which back end and which partition the ring uses for the nRF54L RRAM is not read from the kit files here: unverified, step 7 (board files). The real file uses only the back-end-independent calls.
- **K11 (fatal handler and retained memory): true.** `k_sys_fatal_error_handler` is declared in `fatal.h`, defined weak in `kernel/fatal.c` (so an application may override it), and the test framework defines its own (hence the split: override in `rsy_fatal.c` only outside tests). Its 4.4.2 signature is proven by the compile-time check `sys_crash.test_handler_signature_matches_kit` (a static assertion on both targets; PASS lines 97 and 160). Binding `zephyr,retained-ram` exists and `drivers/retained_mem/retained_mem_zephyr_ram.c` is present; the API has read, write and clear; a binding `nordic,nrf-gpregret` exists, which the real file uses for `gpregret1` through the alias `gpregret1`. The real handler (override linked, `k_sys_fatal_error_handler` in the kit image) compiled for the kit; the retained-memory part of `rsy_hw_real.c` was NOT compiled (needs the alias `crashram` of step 7).

## 6. Needs for the join and the board files (for J and step 7)

- Product `prj.conf` for the kit: `CONFIG_RING_SYS`, `CONFIG_SETTINGS`, `CONFIG_WATCHDOG`, `CONFIG_RETAINED_MEM`, `CONFIG_FLASH`, `CONFIG_FLASH_MAP`, `CONFIG_STREAM_FLASH`, `CONFIG_BOOTLOADER_MCUBOOT`, `CONFIG_IMG_MANAGER`, `CONFIG_MCUBOOT_IMG_MANAGER` (see `tests/sys/kitcompile/prj.conf`).
- Devicetree: `wdt31` enabled, partition `slot1_partition`, alias `crashram` (a `zephyr,retained-ram` node of 1,024 bytes), alias `gpregret1`. The `kitcompile/app.overlay` enables `wdt31` only.
- Join: call `rsy_init` first; `rsy_recording(true/false)` around recordings; `rsy_progress` from the audio and storage threads; `rsy_time_save(rtime_utc_ms(), tz, zone_known)` on SHIP and OFF; write the guess once into the log with `RREC_LOG_TIME_GUESS`; after `rsy_crash_take` returns 1 write `RREC_LOG_CRASH`; reboot after the OK of FW_END; call `rsy_selftest_pass` for storage, Bluetooth and USB.

## 7. Not provable without hardware (this unit)

The swap, the signature check, the rollback of an unconfirmed image, the MCUboot write protection, the real settings in the RRAM, retained RAM and `gpregret1` across a real reset, a real fault reaching the handler (stack words, registers), the watchdog reset. A failing image erase, a failing `is_confirmed`, a failing confirm write, a failing settings load and a failing `wdt` feed cannot be produced by the simulated drivers; their paths in `rsy.c` are written and untested.

## 8. Run list (every look at results)

`u7-kfacts*.console` (facts), `u7-short1.console` (first build failed: missing include in my test, fixed), `u7-short2.console` (one case failed: my test expectation on a refused FW_BEGIN, test corrected), `u7-short3.log` (suites alone: 2 of 2 configurations, 48 of 48 cases passed), `u7-kit1` to `u7-kit5` (kit compile; kit1 to kit4 had errors or warnings that were fixed in the real file, kit5 clean), `u7-cfg`, `u7-nm`, `u7-boards`, `u7-dts`, `u7-kit3b`, `u7-kit3c`, `u7-kit4b`, `u7-kit4c` (looks at the kit build), `u7-full1.log` (the cited full unit run).

## 9. Cleanup

The server folder `/root/ring-os/src-u-sys` (my copy) and the run folders under `/ws/out` named `u7-*` and `20261113-0*-u7-*` in the container's output were made by my commands; left in place for the lead. No process of mine runs. Nothing was written outside my own files and the output folder.

questions_for_owner: none

RESULT: done, `UNIT PASS tests/sys` on both simulated targets with all 8 broken copies failing their named cases; the real-driver file compiles for the kit but is unproven, and K10 (settings back end on the RRAM) is unverified.
