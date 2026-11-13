# rhw notes: unit U0 of software step 6 (shared headers, specification constants, simulated drivers)

Builder: U0 helper. Started 2026-11-13 04:10 CET (`date`). Version read: commit 783ddc4 (master). No git was run.
Contract: `firmware/docs/step6-plan.md` (read in full, rulings included), section 3 "U0 `rhw`", section 5, kit facts
K14 to K16 of section 8. "FW l.N" = line N of `design/firmware.md` at 783ddc4. Raw evidence: `firmware/build-logs/step6/u0-*`.

## 1. What exists (files written)

| Path (under `firmware/`) | What |
|---|---|
| `modules/ring_rhw/zephyr/module.yml`, `CMakeLists.txt`, `Kconfig` | the module; `CONFIG_RING_RHW` (interfaces, active instances, real clock), `CONFIG_RING_RHW_SIM` (simulated drivers; pool, log, hooks, USB host buffer sizes) |
| `modules/ring_rhw/include/ring_rhw/rrec_spec.h` | every shared number of FW 4, 5, 6, 8, 9 once, with its FW line; the event log codes of D13 (marked for the lead); three shared types (`struct rrec_crash`, `struct rrec_logrec`, `rrec_log_fn`) |
| `modules/ring_rhw/include/ring_rhw/rhw.h` | 14 driver interfaces (structs of function pointers) and the active instance of each |
| `modules/ring_rhw/include/ring_rhw/rhw_sim.h` | test builds only: the one ordered event log, every fault and value of plan section 5, `rhw_sim_reset()`, `rhw_sim_reboot()` |
| `modules/ring_rhw/src/rhw.c` | active instances: simulated with SIM, "absent" (-ENODEV) without, `rhw_register_*()` for the real files |
| `modules/ring_rhw/src/rhw_clock_real.c` | the real clock (kernel calls only; also used by the K14 case) |
| `modules/ring_rhw/src/sim_core.c`, `sim_disk.c`, `sim_mic.c`, `sim_pmic.c` (power chip and gauge), `sim_hfxo.c`, `sim_misc.c` (motor pin, storage bus, watchdog, clock, beacon), `sim_usb.c`, `sim_image.c` (image store, settings, retained memory), `sim_int.h` | the simulated drivers, written for this project |
| `modules/ring_rhw/dts/bindings/ring,sim-disk.yaml`, `ring,sim-mic.yaml`, `vendor-prefixes.txt` | the two bindings of the plan and the vendor prefix `ring` they need (run 1 failed without it) |
| `modules/ring_store/include/ring_store/rst.h` | U2's public header |
| `modules/ring_audio/include/ring_audio/rau.h` | U3's |
| `modules/ring_xfer/include/ring_xfer/rxf.h` | U4's |
| `modules/ring_power/include/ring_power/rpw.h` | U5's |
| `modules/ring_motor/include/ring_motor/rmo.h` | U6's |
| `modules/ring_sys/include/ring_sys/rsy.h` | U7's |
| `modules/ring_factory/include/ring_factory/rfa.h` | U8's |
| `modules/ring_recorder/include/ring_recorder/rrec.h` | J's |
| `tests/rhw/` | suite `rhw_sim` (`src/test_rhw.c`), one file per public header (`src/hdr_*.c`, 11 files), `app.overlay` (the two simulated nodes), `broken_edit.py`, `broken_run.sh` |
| `tools/unit_run.sh` | the targeted run for every unit |
| `docs/rhw-notes.md` | this file |

## 2. Design of the headers (what every other builder needs to know)

- **One path to hardware.** Units call `rhw_<kind>()` and never a kit driver; a unit's real file (`*_hw_real.c`, kit
  build only, D15) registers its instance with `rhw_register_<kind>()`. With `CONFIG_RING_RHW_SIM=y` registration is
  refused (-EPERM, proven by `test_registration_refused_in_sim`), so a real driver cannot enter a simulated build.
- **Numbers.** Every number of FW 4, 5, 6, 8, 9 that more than one unit uses is in `rrec_spec.h`, once. Not there on
  purpose: `CHARGE_CURRENT` (FW l.878, l.894; U5 owns it with its five build assertions so its broken copies change one
  place; other units call `rpw_charge_current_ua()`), anything of the motor soft start (ruling D3), chip pins.
- **Pure parts** of each unit are declared in the unit's own `src/` headers (not public, not frozen); the public
  header is the thin part other units call. A unit's tests add its `src/` to their include path.
- **Units do not include each other** except: `rau.h` includes `rst.h` (the chunk hand-off, as the plan says U3 needs
  U2's header); `rrec.h` includes `ring_core/rc_types.h` (the core's actions). Levels and states cross other headers as
  `uint8_t` holding `enum rc_batt` / `enum rc_state` values, so U2 to U8 build without the core.
- **Log hook.** Every unit gets `rrec_log_fn` from the join; only the join adds the state and times and calls
  `rst_log_put()`.
- **Thread rule** (top of `rhw.h`): thread context only, one owner unit per kind; callbacks run in driver context and
  must not block. Exceptions named in the header: `rhw_motor()->set` from the motor's k_timer, the retained memory and
  gpregret1 calls from the fatal error handler, the clock from anywhere.

## 3. Readings and differences (plan against specification; the specification wins)

1. **FACTORY_EXIT has no sub-command number in FW.** FW l.201 has the row "command FACTORY_EXIT"; FW 9.3 (l.1019 to
   l.1037) lists 0x01, 0x10, 0x11, 0x20, 0x30, 0x31, 0x40, 0x41, 0x50, 0x60, 0x70, 0x71, 0x7E, 0x7F and no EXIT.
   `RREC_FAC_EXIT = 0x02` is marked in `rrec_spec.h` as U0's proposal. **For the lead to rule and write into FW.**
2. **The order of "close" (FW l.125) against the stop of FW 4.5 (l.463).** l.125 writes the partial chunk, the CLOSE
   record and the superblock BEFORE "stop PDM"; l.463 stops the PDM first. `rau.h` splits the stop in two so the join
   can keep l.125's order exactly: `rau_cut(mark)` (frames up to the mark kept, the PDM keeps running and later frames
   are dropped), then `rst_close()`, then `rau_halt()` (stop, blocks released, clock pins asleep), `rec_mics_off()`,
   `rau_release()` (HFXO after VDD_MIC, l.463), `rst_unmount()`.
3. **READ_RANGE and the header CRC (fact for U4).** FW l.686: the header's crc32 covers the payload; FW l.698: the
   payload of READ_RANGE is up to 256 x 33,280 bytes. The CRC precedes the payload, so the ring reads the chunks twice
   or keeps them. Written into `rxf.h`.
4. **U5's "set a rail" is dropped.** The plan lists it among U5's offers; `rpw.h` has no rail call so that exactly one
   path exists per rail (VDD_SD by ring_store, VDD_MIC only by `rec_mics_on()`, both through
   `rhw_pmic()->rail_set(..., caller)`), which keeps the stage `recorder-one-mic-path` a simple search.
5. **The ship task with VBUS present** (simulated power chip). FW l.934 quotes the chip: without VBUS it enters ship
   mode at once; the host must wait for VBUS removal first. The simulated chip enters the "no supply" state (every later
   call refused, plan section 5) only when the task is written without VBUS; with VBUS it logs the task and stays up.
6. **`rhw_sim_reboot()` keeps the three stores and also the test's world**: the faults and set values (card size,
   cell, VBUS present, mic source) and the event log (the test's observer, where it writes `RHW_EV_SIM_REBOOT`).
   Everything that is ring state goes to reset values, the image store's slot 1 and its requests included (MCUboot and
   its swap are not simulated; a test sets "confirmed" for the image it pretends to run).
7. **The simulated card refuses a transfer before init** as well as any call with VDD_SD off (the plan names only the
   rail); a card loses its init when VDD_SD goes off. Both are counted by `rhw_sim_disk_refused()`.
8. **Sampling "in the recording states" (FW l.928)**: `rpw_state()` reads it as `RECORDING` only. Open for the lead
   (a factory test recording runs in `FACTORY_TEST`).
9. **The watchdog rule outside a recording (FW l.1065)**: the audio and storage threads report progress only while a
   recording runs; `rsy.h` reads the rule as "feed when both reported in the last 2 s, or when no recording runs"
   (`rsy_recording()`). Open for the lead.
10. **LIST state of a recovered recording** (FW l.697 lists 1 new, 2 transferred, 3 recovered; FW l.636 says the state
    is the last record): `rst.h` shows RECOVERED for a recovered recording until a CONFIRM, then TRANSFERRED.
11. **Battery thresholds in `rrec_spec.h`** although only U5 judges them: one place for every number of the
    specification; the screens (J) may show them.
12. **Event log codes (D13)**: the list at the end of `rrec_spec.h`, `enum rrec_log_code`, with the argument layout of
    each, **for the lead to copy into FW 9.4**. It holds the plan's list (state change, fault, battery threshold,
    transfer command per opcode, motor pattern start, current limit, reset cause, crash, dropout, recovery, sign
    refused, ship retry, zone unknown at start) and adds recording start, stop press time (FW l.448), storage retry
    result, S30, SFULL, main-chip reset reason (FW l.996), time guess (D18), self-test result, dropped count.
13. **Plan text against FW numbers.** Every value in `rrec_spec.h` was taken from FW, not from the plan; a check script
    compared each define's number with its cited FW line (section 6). I did not compare the plan's own text with FW
    number by number, so no difference of that kind is claimed either way.

## 4. Every function of every header with the specification line it serves

Generated by `build-logs/step6/u0-map-functions.py` from the headers themselves (the FW lines are those cited in each
function's own comment; full table and count in `build-logs/step6/u0-map-functions.log`). Functions with no FW line:
the 14 `rhw_<kind>()` getters and the 13 `rhw_register_<kind>()` calls serve the plan's selection rule
(`step6-plan.md` line 256 and decision D15), and the 75 functions of `rhw_sim.h` are test controls that serve the plan's
section 5 (`step6-plan.md` lines 397 to 416), not a line of FW.

| Header | Function | Line | FW lines cited |
|---|---|---|---|
| rhw.h | `rhw_disk_api.init` | rhw.h:40 | 506, 507 |
| rhw.h | `rhw_disk_api.deinit` | rhw.h:42 | 506 |
| rhw.h | `rhw_disk_api.read` | rhw.h:45 | 143 |
| rhw.h | `rhw_disk_api.write` | rhw.h:48 | 515, 643 |
| rhw.h | `rhw_disk_api.sector_count` | rhw.h:50 | 507, 654 |
| rhw.h | `rhw_mic_api.configure` | rhw.h:68 | 429 |
| rhw.h | `rhw_mic_api.start` | rhw.h:70 | 429 |
| rhw.h | `rhw_mic_api.stop` | rhw.h:73 | 463 |
| rhw.h | `rhw_mic_api.read` | rhw.h:78 | 443 |
| rhw.h | `rhw_mic_api.free_block` | rhw.h:80 | 443 |
| rhw.h | `rhw_mic_api.pins_sleep` | rhw.h:83 | 463, 465 |
| rhw.h | `rhw_mic_api.pins_default` | rhw.h:85 | 465 |
| rhw.h | `rhw_pmic_cb.vbus` | rhw.h:108 | 979 |
| rhw.h | `rhw_pmic_cb.charge_error` | rhw.h:109 | 176, 979 |
| rhw.h | `rhw_pmic_api.rail_set` | rhw.h:115 | 342 |
| rhw.h | `rhw_pmic_api.rail_get` | rhw.h:117 | 912 |
| rhw.h | `rhw_pmic_api.charger_enable` | rhw.h:119 | 888 |
| rhw.h | `rhw_pmic_api.charger_current` | rhw.h:121 | 878, 894 |
| rhw.h | `rhw_pmic_api.charge_status` | rhw.h:123 | 1032 |
| rhw.h | `rhw_pmic_api.sample` | rhw.h:125 | 926, 928 |
| rhw.h | `rhw_pmic_api.ilim_active` | rhw.h:127 | 990 |
| rhw.h | `rhw_pmic_api.reset_causes` | rhw.h:129 | 996 |
| rhw.h | `rhw_pmic_api.reset_causes_clear` | rhw.h:131 | 996 |
| rhw.h | `rhw_pmic_api.shphld_config` | rhw.h:133 | 938 |
| rhw.h | `rhw_pmic_api.shphld_strobe` | rhw.h:135 | 938 |
| rhw.h | `rhw_pmic_api.ship_task` | rhw.h:138 | 940, 941 |
| rhw.h | `rhw_pmic_api.vbus_present` | rhw.h:141 | 979 |
| rhw.h | `rhw_pmic_api.set_callbacks` | rhw.h:144 | 977, 997 |
| rhw.h | `rhw_hfxo_api.request` | rhw.h:151 | 428 |
| rhw.h | `rhw_hfxo_api.release` | rhw.h:153 | 463 |
| rhw.h | `rhw_hfxo_api.running` | rhw.h:155 | 428 |
| rhw.h | `rhw_motor_api.set` | rhw.h:162 | 314 |
| rhw.h | `rhw_sdbus_api.suspend` | rhw.h:169 | 506 |
| rhw.h | `rhw_sdbus_api.resume` | rhw.h:171 | 506 |
| rhw.h | `rhw_usb_cb.rx` | rhw.h:188 | 677 |
| rhw.h | `rhw_usb_cb.event` | rhw.h:190 | 978 |
| rhw.h | `rhw_usb_api.enable` | rhw.h:194 | 978 |
| rhw.h | `rhw_usb_api.disable` | rhw.h:196 | 978 |
| rhw.h | `rhw_usb_api.send` | rhw.h:200 | 688 |
| rhw.h | `rhw_usb_api.speed` | rhw.h:202 | 669 |
| rhw.h | `rhw_usb_api.set_callbacks` | rhw.h:204 | 669 |
| rhw.h | `rhw_image_api.erase_slot1` | rhw.h:218 | 1013 |
| rhw.h | `rhw_image_api.write` | rhw.h:221 | 1012 |
| rhw.h | `rhw_image_api.read` | rhw.h:223 | 1013 |
| rhw.h | `rhw_image_api.request_test_upgrade` | rhw.h:225 | 180, 1013 |
| rhw.h | `rhw_image_api.is_confirmed` | rhw.h:227 | 1014 |
| rhw.h | `rhw_image_api.confirm` | rhw.h:229 | 1014 |
| rhw.h | `rhw_image_api.reboot` | rhw.h:231 | 180, 201, 707 |
| rhw.h | `rhw_persist_api.load` | rhw.h:244 | 1010 |
| rhw.h | `rhw_persist_api.save` | rhw.h:246 | 1012 |
| rhw.h | `rhw_retained_api.read` | rhw.h:253 | 1063 |
| rhw.h | `rhw_retained_api.write` | rhw.h:254 | 1063 |
| rhw.h | `rhw_retained_api.clear` | rhw.h:256 | 1063 |
| rhw.h | `rhw_retained_api.gpregret1_get` | rhw.h:258 | 1063 |
| rhw.h | `rhw_retained_api.gpregret1_set` | rhw.h:259 | 1063 |
| rhw.h | `rhw_wdt_api.start` | rhw.h:265 | 1065 |
| rhw.h | `rhw_wdt_api.feed` | rhw.h:267 | 1065 |
| rhw.h | `rhw_gauge_api.start` | rhw.h:278 | 926 |
| rhw.h | `rhw_gauge_api.process` | rhw.h:281 | 927 |
| rhw.h | `rhw_clock_api.now_ms` | rhw.h:287 | 1003 |
| rhw.h | `rhw_clock_api.cycles` | rhw.h:290 | 558, 573 |
| rhw.h | `rhw_clock_api.cycles_per_sec` | rhw.h:292 | 573 |
| rhw.h | `rhw_clock_api.device_id` | rhw.h:294 | 696, 1057 |
| rhw.h | `rhw_beacon_api.start` | rhw.h:303 | 1057 |
| rhw.h | `rhw_beacon_api.stop` | rhw.h:305 | 1057 |
| rhw.h | `rhw_disk` | rhw.h:312 | NONE |
| rhw.h | `rhw_mic` | rhw.h:313 | NONE |
| rhw.h | `rhw_pmic` | rhw.h:314 | NONE |
| rhw.h | `rhw_hfxo` | rhw.h:315 | NONE |
| rhw.h | `rhw_motor` | rhw.h:316 | NONE |
| rhw.h | `rhw_sdbus` | rhw.h:317 | NONE |
| rhw.h | `rhw_usb` | rhw.h:318 | NONE |
| rhw.h | `rhw_image` | rhw.h:319 | NONE |
| rhw.h | `rhw_persist` | rhw.h:320 | NONE |
| rhw.h | `rhw_retained` | rhw.h:321 | NONE |
| rhw.h | `rhw_wdt` | rhw.h:322 | NONE |
| rhw.h | `rhw_gauge` | rhw.h:323 | NONE |
| rhw.h | `rhw_clock` | rhw.h:324 | NONE |
| rhw.h | `rhw_beacon` | rhw.h:325 | NONE |
| rhw.h | `rhw_register_disk` | rhw.h:329 | NONE |
| rhw.h | `rhw_register_mic` | rhw.h:330 | NONE |
| rhw.h | `rhw_register_pmic` | rhw.h:331 | NONE |
| rhw.h | `rhw_register_hfxo` | rhw.h:332 | NONE |
| rhw.h | `rhw_register_motor` | rhw.h:333 | NONE |
| rhw.h | `rhw_register_sdbus` | rhw.h:334 | NONE |
| rhw.h | `rhw_register_usb` | rhw.h:335 | NONE |
| rhw.h | `rhw_register_image` | rhw.h:336 | NONE |
| rhw.h | `rhw_register_persist` | rhw.h:337 | NONE |
| rhw.h | `rhw_register_retained` | rhw.h:338 | NONE |
| rhw.h | `rhw_register_wdt` | rhw.h:339 | NONE |
| rhw.h | `rhw_register_gauge` | rhw.h:340 | NONE |
| rhw.h | `rhw_register_beacon` | rhw.h:341 | NONE |
| rhw_sim.h | `rhw_sim_log_count` | rhw_sim.h:120 | NONE |
| rhw_sim.h | `rhw_sim_log_get` | rhw_sim.h:121 | NONE |
| rhw_sim.h | `rhw_sim_log_overflow` | rhw_sim.h:122 | NONE |
| rhw_sim.h | `rhw_sim_log_clear` | rhw_sim.h:123 | NONE |
| rhw_sim.h | `rhw_sim_log_find` | rhw_sim.h:125 | NONE |
| rhw_sim.h | `rhw_sim_log_count_kind` | rhw_sim.h:127 | NONE |
| rhw_sim.h | `rhw_sim_log_dump` | rhw_sim.h:129 | NONE |
| rhw_sim.h | `rhw_sim_reset` | rhw_sim.h:132 | NONE |
| rhw_sim.h | `rhw_sim_reboot` | rhw_sim.h:133 | NONE |
| rhw_sim.h | `rhw_sim_add_reboot_hook` | rhw_sim.h:136 | NONE |
| rhw_sim.h | `rhw_sim_reboots` | rhw_sim.h:138 | NONE |
| rhw_sim.h | `rhw_sim_disk_set_sectors` | rhw_sim.h:144 | 654 |
| rhw_sim.h | `rhw_sim_disk_fail_init` | rhw_sim.h:146 | NONE |
| rhw_sim.h | `rhw_sim_disk_fail_write` | rhw_sim.h:148 | NONE |
| rhw_sim.h | `rhw_sim_disk_read_error_at` | rhw_sim.h:150 | NONE |
| rhw_sim.h | `rhw_sim_disk_cut` | rhw_sim.h:154 | NONE |
| rhw_sim.h | `rhw_sim_disk_was_cut` | rhw_sim.h:156 | NONE |
| rhw_sim.h | `rhw_sim_disk_stall_ms` | rhw_sim.h:158 | NONE |
| rhw_sim.h | `rhw_sim_disk_refused` | rhw_sim.h:160 | 506 |
| rhw_sim.h | `rhw_sim_disk_write_calls` | rhw_sim.h:161 | NONE |
| rhw_sim.h | `rhw_sim_disk_peek` | rhw_sim.h:163 | NONE |
| rhw_sim.h | `rhw_sim_disk_poke` | rhw_sim.h:164 | NONE |
| rhw_sim.h | `rhw_sim_disk_stored` | rhw_sim.h:166 | NONE |
| rhw_sim.h | `rhw_sim_mic_source` | rhw_sim.h:173 | NONE |
| rhw_sim.h | `rhw_sim_mic_stuck` | rhw_sim.h:175 | NONE |
| rhw_sim.h | `rhw_sim_mic_clip_block` | rhw_sim.h:177 | NONE |
| rhw_sim.h | `rhw_sim_mic_stop_after` | rhw_sim.h:180 | 169 |
| rhw_sim.h | `rhw_sim_mic_drop_block` | rhw_sim.h:182 | NONE |
| rhw_sim.h | `rhw_sim_mic_read_error` | rhw_sim.h:184 | NONE |
| rhw_sim.h | `rhw_sim_mic_last_cfg` | rhw_sim.h:186 | NONE |
| rhw_sim.h | `rhw_sim_mic_delivered` | rhw_sim.h:187 | NONE |
| rhw_sim.h | `rhw_sim_mic_held` | rhw_sim.h:188 | NONE |
| rhw_sim.h | `rhw_sim_mic_pins_asleep` | rhw_sim.h:189 | NONE |
| rhw_sim.h | `rhw_sim_vbus` | rhw_sim.h:194 | NONE |
| rhw_sim.h | `rhw_sim_pmic_vbus` | rhw_sim.h:196 | NONE |
| rhw_sim.h | `rhw_sim_vbus_at` | rhw_sim.h:198 | NONE |
| rhw_sim.h | `rhw_sim_pmic_charge_error` | rhw_sim.h:200 | NONE |
| rhw_sim.h | `rhw_sim_pmic_ilim_at_sample` | rhw_sim.h:203 | NONE |
| rhw_sim.h | `rhw_sim_pmic_set_reset_causes` | rhw_sim.h:205 | NONE |
| rhw_sim.h | `rhw_sim_pmic_motor_dip` | rhw_sim.h:207 | 1028 |
| rhw_sim.h | `rhw_sim_pmic_script` | rhw_sim.h:210 | NONE |
| rhw_sim.h | `rhw_sim_pmic_cell` | rhw_sim.h:215 | NONE |
| rhw_sim.h | `rhw_sim_pmic_charge_state` | rhw_sim.h:217 | NONE |
| rhw_sim.h | `rhw_sim_pmic_charger_on` | rhw_sim.h:218 | NONE |
| rhw_sim.h | `rhw_sim_pmic_charger_ua` | rhw_sim.h:219 | NONE |
| rhw_sim.h | `rhw_sim_pmic_rail_caller` | rhw_sim.h:221 | NONE |
| rhw_sim.h | `rhw_sim_shipped` | rhw_sim.h:223 | NONE |
| rhw_sim.h | `rhw_sim_ship_refused` | rhw_sim.h:224 | NONE |
| rhw_sim.h | `rhw_sim_gauge_start_soc` | rhw_sim.h:227 | NONE |
| rhw_sim.h | `rhw_sim_gauge_capacity` | rhw_sim.h:228 | 114 |
| rhw_sim.h | `rhw_sim_gauge_error` | rhw_sim.h:229 | 114 |
| rhw_sim.h | `rhw_sim_hfxo_delay_ms` | rhw_sim.h:232 | NONE |
| rhw_sim.h | `rhw_sim_hfxo_never` | rhw_sim.h:233 | NONE |
| rhw_sim.h | `rhw_sim_hfxo_requests` | rhw_sim.h:234 | NONE |
| rhw_sim.h | `rhw_sim_motor_pin` | rhw_sim.h:237 | NONE |
| rhw_sim.h | `rhw_sim_sdbus_suspended` | rhw_sim.h:238 | NONE |
| rhw_sim.h | `rhw_sim_usb_speed` | rhw_sim.h:241 | NONE |
| rhw_sim.h | `rhw_sim_usb_host_stop` | rhw_sim.h:243 | NONE |
| rhw_sim.h | `rhw_sim_usb_host_write` | rhw_sim.h:245 | NONE |
| rhw_sim.h | `rhw_sim_usb_host_read` | rhw_sim.h:247 | NONE |
| rhw_sim.h | `rhw_sim_usb_host_sink` | rhw_sim.h:250 | NONE |
| rhw_sim.h | `rhw_sim_usb_event` | rhw_sim.h:252 | NONE |
| rhw_sim.h | `rhw_sim_usb_enabled` | rhw_sim.h:253 | NONE |
| rhw_sim.h | `rhw_sim_image_write_error` | rhw_sim.h:257 | NONE |
| rhw_sim.h | `rhw_sim_image_set_confirmed` | rhw_sim.h:258 | NONE |
| rhw_sim.h | `rhw_sim_image_upgrade_requested` | rhw_sim.h:259 | NONE |
| rhw_sim.h | `rhw_sim_image_reboots` | rhw_sim.h:260 | NONE |
| rhw_sim.h | `rhw_sim_image_last_reboot` | rhw_sim.h:261 | NONE |
| rhw_sim.h | `rhw_sim_image_peek` | rhw_sim.h:262 | NONE |
| rhw_sim.h | `rhw_sim_persist_set` | rhw_sim.h:265 | NONE |
| rhw_sim.h | `rhw_sim_persist_get` | rhw_sim.h:266 | NONE |
| rhw_sim.h | `rhw_sim_retained_set` | rhw_sim.h:267 | NONE |
| rhw_sim.h | `rhw_sim_retained_get` | rhw_sim.h:268 | NONE |
| rhw_sim.h | `rhw_sim_gpregret1_set` | rhw_sim.h:269 | NONE |
| rhw_sim.h | `rhw_sim_gpregret1_get` | rhw_sim.h:270 | NONE |
| rhw_sim.h | `rhw_sim_wdt_would_reset` | rhw_sim.h:275 | NONE |
| rhw_sim.h | `rhw_sim_wdt_started` | rhw_sim.h:276 | NONE |
| rhw_sim.h | `rhw_sim_wdt_feeds` | rhw_sim.h:277 | NONE |
| rhw_sim.h | `rhw_sim_clock_rate` | rhw_sim.h:280 | NONE |
| rhw_sim.h | `rhw_sim_clock_device_id` | rhw_sim.h:281 | NONE |
| rhw_sim.h | `rhw_sim_beacon_get` | rhw_sim.h:293 | NONE |
| rrec_spec.h | `typedef rrec_log_fn` | rrec_spec.h:471 | 1062 |
| rst.h | `typedef rst_chunk_done_fn` | rst.h:64 | 643 |
| rst.h | `rst_cb.s30` | rst.h:121 | 166, 167 |
| rst.h | `rst_cb.sfull` | rst.h:122 | 166, 167 |
| rst.h | `rst_cb.write_fault` | rst.h:124 | 168 |
| rst.h | `rst_init` | rst.h:129 | 506 |
| rst.h | `rst_mount` | rst.h:137 | 135, 138, 506, 507, 587 |
| rst.h | `rst_unmount` | rst.h:141 | 506 |
| rst.h | `rst_mounted` | rst.h:144 | 640 |
| rst.h | `rst_open` | rst.h:149 | 126, 219, 641 |
| rst.h | `rst_put_chunk` | rst.h:155 | 641, 643 |
| rst.h | `rst_close` | rst.h:161 | 125, 630 |
| rst.h | `rst_recover` | rst.h:167 | 143, 646 |
| rst.h | `rst_space` | rst.h:170 | 650 |
| rst.h | `rst_list` | rst.h:175 | 697 |
| rst.h | `rst_read_chunk` | rst.h:179 | 661, 698 |
| rst.h | `rst_confirm` | rst.h:183 | 658 |
| rst.h | `rst_delete` | rst.h:187 | 659, 660 |
| rst.h | `rst_log_put` | rst.h:192 | 1062 |
| rst.h | `rst_log_dropped` | rst.h:195 | 1062 |
| rst.h | `rst_log_read` | rst.h:199 | 706 |
| rst.h | `rst_factory_area_test` | rst.h:203 | 1030 |
| rst.h | `rst_delete_factory_recordings` | rst.h:207 | 1030 |
| rau.h | `rau_cb.put` | rau.h:36 | 443 |
| rau.h | `rau_cb.no_block` | rau.h:38 | 169 |
| rau.h | `rau_cb.dropout` | rau.h:40 | 430 |
| rau.h | `rau_cb.chunk_facts` | rau.h:43 | 567, 571 |
| rau.h | `rau_init` | rau.h:48 | 465 |
| rau.h | `rau_prepare` | rau.h:52 | 428, 456 |
| rau.h | `rau_start` | rau.h:66 | 429, 460 |
| rau.h | `rau_cut` | rau.h:76 | 448 |
| rau.h | `rau_halt` | rau.h:81 | 168, 169, 463 |
| rau.h | `rau_release` | rau.h:84 | 463 |
| rau.h | `rau_highlight` | rau.h:88 | 159, 582 |
| rau.h | `rau_motor_edge` | rau.h:93 | 496, 497 |
| rau.h | `rau_set_b15` | rau.h:96 | 547 |
| rau.h | `rau_capturing` | rau.h:99 | 112 |
| rxf.h | `rxf_backend.may_answer` | rxf.h:36 | 673 |
| rxf.h | `rxf_backend.get_info` | rxf.h:38 | 696 |
| rxf.h | `rxf_backend.list` | rxf.h:40 | 697 |
| rxf.h | `rxf_backend.range_check` | rxf.h:43 | 661, 698 |
| rxf.h | `rxf_backend.read_chunk` | rxf.h:45 | 698 |
| rxf.h | `rxf_backend.confirm` | rxf.h:47 | 699 |
| rxf.h | `rxf_backend.del` | rxf.h:49 | 700 |
| rxf.h | `rxf_backend.set_time` | rxf.h:51 | 701 |
| rxf.h | `rxf_backend.get_battery` | rxf.h:53 | 702 |
| rxf.h | `rxf_backend.fw_begin` | rxf.h:56 | 703, 705, 1012, 1015 |
| rxf.h | `rxf_backend.fw_data` | rxf.h:57 | 704 |
| rxf.h | `rxf_backend.fw_end` | rxf.h:58 | 704, 705 |
| rxf.h | `rxf_backend.get_log` | rxf.h:60 | 706 |
| rxf.h | `rxf_backend.factory` | rxf.h:63 | 708 |
| rxf.h | `rxf_backend.after_response` | rxf.h:66 | 705, 707, 1062 |
| rxf.h | `rxf_cb.configured` | rxf.h:71 | 171, 673 |
| rxf.h | `rxf_cb.unconfigured` | rxf.h:73 | 178 |
| rxf.h | `rxf_start` | rxf.h:78 | 978 |
| rxf.h | `rxf_abort` | rxf.h:82 | 179 |
| rxf.h | `rxf_finish` | rxf.h:86 | 178 |
| rxf.h | `rxf_busy` | rxf.h:89 | 219 |
| rpw.h | `rpw_cb.level` | rpw.h:36 | 211, 213 |
| rpw.h | `rpw_cb.vbus` | rpw.h:38 | 210, 979 |
| rpw.h | `rpw_cb.charge_error` | rpw.h:40 | 176 |
| rpw.h | `rpw_cb.ilim` | rpw.h:43 | 990, 995 |
| rpw.h | `rpw_start` | rpw.h:51 | 893 |
| rpw.h | `rpw_boot_causes` | rpw.h:55 | 996 |
| rpw.h | `rpw_state` | rpw.h:60 | 928 |
| rpw.h | `rpw_charge_on` | rpw.h:64 | 129, 894 |
| rpw.h | `rpw_charge_off` | rpw.h:65 | 129 |
| rpw.h | `rpw_motor_charge` | rpw.h:69 | 927 |
| rpw.h | `rpw_ship` | rpw.h:76 | 939, 941 |
| rpw.h | `rpw_battery_report` | rpw.h:80 | 702 |
| rpw.h | `rpw_values` | rpw.h:93 | 374 |
| rpw.h | `rpw_charge_current_ua` | rpw.h:96 | 878 |
| rmo.h | `rmo_cb.edge` | rmo.h:25 | 496 |
| rmo.h | `rmo_cb.charge` | rmo.h:28 | 332 |
| rmo.h | `rmo_cb.started` | rmo.h:31 | 333 |
| rmo.h | `rmo_init` | rmo.h:35 | 314 |
| rmo.h | `rmo_play` | rmo.h:41 | 301, 318 |
| rmo.h | `rmo_set_vibration` | rmo.h:44 | 301 |
| rmo.h | `rmo_playing` | rmo.h:47 | 318 |
| rmo.h | `rmo_stop` | rmo.h:50 | 937 |
| rsy.h | `rsy_init` | rsy.h:29 | 1010 |
| rsy.h | `rsy_fw_begin` | rsy.h:35 | 703, 1012, 1013, 1015 |
| rsy.h | `rsy_fw_data` | rsy.h:38 | 704, 1012 |
| rsy.h | `rsy_fw_end` | rsy.h:42 | 705, 1013 |
| rsy.h | `rsy_selftest_start` | rsy.h:53 | 1014 |
| rsy.h | `rsy_selftest_pass` | rsy.h:56 | 1014 |
| rsy.h | `rsy_selftest_running` | rsy.h:59 | 1014 |
| rsy.h | `rsy_factory_flag` | rsy.h:62 | 1005, 1019 |
| rsy.h | `rsy_factory_flag_set` | rsy.h:65 | 1019 |
| rsy.h | `rsy_time_save` | rsy.h:67 | 1005 |
| rsy.h | `rsy_time_guess` | rsy.h:70 | 1005 |
| rsy.h | `rsy_crash_take` | rsy.h:75 | 1063 |
| rsy.h | `rsy_progress` | rsy.h:84 | 1065 |
| rsy.h | `rsy_wdt_start` | rsy.h:87 | 1065 |
| rsy.h | `rsy_recording` | rsy.h:89 | 1065 |
| rfa.h | `rfa_ops.test_recording` | rfa.h:56 | 1029, 1053 |
| rfa.h | `rfa_ops.screen_frame` | rfa.h:59 | 1025 |
| rfa.h | `rfa_ops.motor_on` | rfa.h:61 | 1028 |
| rfa.h | `rfa_ops.vbat_mv` | rfa.h:63 | 1028 |
| rfa.h | `rfa_ops.store_test` | rfa.h:65 | 1030 |
| rfa.h | `rfa_ops.charge` | rfa.h:67 | 1032 |
| rfa.h | `rfa_ops.xtal_counts` | rfa.h:70 | 1033 |
| rfa.h | `rfa_ops.flag` | rfa.h:72 | 1019 |
| rfa.h | `rfa_ops.flag_set` | rfa.h:73 | 1019 |
| rfa.h | `rfa_init` | rfa.h:77 | 1019 |
| rfa.h | `rfa_request` | rfa.h:84 | 708, 1019, 1020, 1037 |
| rfa.h | `rfa_input` | rfa.h:89 | 1026, 1027 |
| rfa.h | `rfa_ship_begin` | rfa.h:94 | 1057 |
| rfa.h | `rfa_beacon_stop` | rfa.h:96 | 1057 |
| rrec.h | `rrec_init` | rrec.h:22 | 133, 140 |
| rrec.h | `rrec_action` | rrec.h:26 | 124 |
| rrec.h | `rec_mics_on` | rrec.h:32 | 342, 457 |
| rrec.h | `rec_mics_off` | rrec.h:35 | 342, 463 |
| rrec.h | `rrec_sign_hook` | rrec.h:42 | 148 |

functions: 287; without a FW line in their own comment: 102

## 5. Kit facts K14, K15, K16

| Id | Answer | Evidence |
|---|---|---|
| K14 | TRUE on `nrf54lm20bsim/nrf54lm20a/cpuapp`: `sys_clock_hw_cycles_per_sec()` = 1,000,000 and `k_cycle_get_32()` advanced 100,100 cycles over a 100 ms sleep (the real clock of rhw the same) | printed by `test_k14_real_clock` in run 2 (`build-logs/step6/u0-20261113-043605-u-rhw.log`, line "K14: sys_clock_hw_cycles_per_sec 1000000; k_cycle_get_32 advanced 100100 in 100 ms"); the case passes on both boards in the final run 3 (`PASS - test_k14_real_clock`). On native_sim with its default ticks the same case failed in run 2 (110 ms for a 100 ms sleep); with 0.1 ms ticks it passes |
| K15 | TRUE for this suite: the simulated chip target holds the sparse card's full pool (4,096 sectors, 2,097,152 bytes), three chunk buffers of 33,280 bytes and the 999,424-byte image slot (static memory) | `test_k15_ram` PASS on both boards in run 3; printed line "K15: pool 4096 sectors (2097152 bytes) and 3 x 33280 chunk bytes held on this target" in run 2. The board document exists (`ls` of `/ws/zephyr/boards/native/nrf_bsim/doc/` lists `nrf54lm20bsim.rst`, `build-logs/step6/u0-k16.console`); I did not read its text |
| K16 | PARTLY. Twister's documentation names `extra_configs` (count 3 in `/ws/zephyr/doc/develop/test/twister.rst`, `u0-k16.console`); two scenarios of one folder were NOT run (the soft start that needed them is not built, ruling D3), so "twister accepts two scenarios with different extra_configs" stays unverified by a run. Time: the targeted run of `tests/rhw` took 04:41:07 to 04:45:46 CET (4 min 39 s) on the loaded server: twister 22.85 s on native_sim and 33.64 s on the simulated chip, the rest the 8 broken-copy builds | run 3 log lines "with no warnings in 22.85 seconds" and "in 33.64 seconds", and its part end times |

## 6. Runs (each from the project folder, `RING_REMOTE_SRC=/root/ring-os/src-u-rhw sh firmware/tools/remote.sh u-rhw "bash tools/unit_run.sh tests/rhw"`)

| Run | Log (copied) | Exit | Last result line | What it showed |
|---|---|---|---|---|
| 1 | `build-logs/step6/u0-20261113-043354-u-rhw.log` | 1 | `UNIT FAIL tests/rhw tests-native_sim tests-nrf54lm20bsim_nrf54lm20a_cpuapp broken-rhw` | devicetree: unknown vendor prefix `ring`; the broken copies were NOT counted as failing (a build error does not count), as required. Fix: `dts/bindings/vendor-prefixes.txt` |
| 2 | `build-logs/step6/u0-20261113-043605-u-rhw.log` | 1 | `UNIT FAIL tests/rhw tests-native_sim tests-nrf54lm20bsim_nrf54lm20a_cpuapp` | native_sim 29 of 42 cases (timing cases: a 1 ms sleep took 20 ms; fixed with 0.1 ms ticks in `tests/rhw/boards/native_sim.conf`); simulated chip 40 of 42; on both, two expected values I had typed wrong (3,824 mV instead of 3,820: I counted 1,000 µA where the cell counts the rails' 7,000 µA; a 1,100-byte read buffer for 1,228 bytes). Broken copies: `RESULT PASS` (each named case failed on both boards) |
| 3 (final) | `build-logs/step6/u0-20261113-044107-u-rhw.log` | 0 | `UNIT PASS tests/rhw` | 42 of 42 cases on native_sim and 42 of 42 on the simulated chip; each of the 4 broken copies fails its own named case and only that case on each board ("failed cases listed: 1"), `RESULT PASS` |

The final log's last line is `# local log: .../build-logs/20261113-044107-u-rhw.log` (written by remote.sh); its last result line (line 606) is `UNIT PASS tests/rhw`.
Every delivered file is the one run 3 copied: nothing I deliver changed after 04:41:07 (only this notes file and my logs).
Run 3 copied the whole `firmware/` folder, including U1's work in progress in `ring_core/`; `tests/rhw` uses only `ring_core/include/ring_core/rc_types.h` (through `rrec.h`), so `hdr_rrec.c` compiled against U1's working copy of that header.

Other checks:
- each header alone with the Mac's C compiler (`-std=c11 -Wall -Wextra -fsyntax-only`): no message (`build-logs/step6/u0-mac-header-syntax.log`); the proof that counts is the target build of `tests/rhw/src/hdr_*.c` in run 3 (`test_headers_compiled`).
- the numbers of `rrec_spec.h` against their cited FW lines (`u0-check-spec-lines.py`, log `u0-check-spec-lines.log`): 223 defines with a number, 196 found on the cited line, 27 not found literally; I read all 27: each is a unit change of the cited value (s to ms, % to 0.1 %, V to mV, KB to bytes) or a byte count summed from the cited field sizes (for example SET_TIME i64 + i16 = 10). 12 skipped (bit flags of FW l.547 read by hand; offsets and sizes derived, with no line).
- no chip pin by number and no `/dev/null` in any file I wrote (`u0-search-pins-devnull.log`: grep exit 1, no hit).
- the edits of the 4 broken copies match once each (`u0-editcheck.log`).
- files changed: only those of my `Owns` (`u0-owned-files.log`; the `ring_core` and `tests/core` entries there are U1's).

## 7. Tests (answers to the brief)

- Suite `rhw_sim` on native_sim and on `nrf54lm20bsim/nrf54lm20a/cpuapp`: 42 cases, all PASS in run 3. One case per fault or value of plan section 5: card 7 (`test_disk_sector_count`, `_init_fails_n`, `_write_fault_at_n`, `_read_error_at_lba`, `_cut_after_sector`, `_stall_per_write`, `_refused_rail_off`), microphone 7 (`test_mic_counter_and_timing`, `_sine_level`, `_stuck_channel`, `_clipped`, `_stop_delivering`, `_drop_block`, `_read_error`) plus `test_mic_stop_and_slab`, power chip 6 (`test_pmic_vbus_now_and_at`, `_charge_error`, `_ilim_at_sample`, `_reset_causes`, `_motor_dip`; the gauge's SoC in `test_gauge_start_soc_and_error`) plus `_script_and_cell`, `_rails_and_charger`, `_ship_refuses_later_calls`, gauge 2 (start SoC and error, one case), HFXO 2 (`test_hfxo_delay`, `_never`), USB 2 (`test_usb_speed_packets`, `_host_stops_reading`), image store 2 (`test_image_write_error`, `_confirmed_flag`), settings 1 (`test_persist_start_values`), retained 1 (`test_retained_valid_or_corrupt`), clock 1 (`test_clock_cycle_rate`), and the drivers without faults (`test_wdt_would_reset`, `test_beacon_recorded`, `test_motor_and_sdbus_recorded`). Event log order and time: `test_event_log_order_and_time`. Reboot: `test_reboot_keeps_card_settings_retained` (card, settings, retained memory and gpregret1 kept; rails, charger, HFXO, motor, USB, watchdog, beacon, image slot, microphone input reset).
- Red first: run 2 and run 3 show each broken copy failing its named case on both boards (`disk_fault_late` -> `test_disk_write_fault_at_n`, `cut_keeps_tail` -> `test_disk_cut_after_sector`, `reboot_wipes_card` -> `test_reboot_keeps_card_settings_retained`, `mic_no_block_ignored` -> `test_mic_stop_delivering`). The order was not red-before-green: the suite and its broken copies were written together and first ran in run 1.
- Runner `tools/unit_run.sh`: any number of folders, both boards, each folder's `broken_run.sh`, last line `UNIT PASS <folders>` / `UNIT FAIL <folders> <parts>`, exit 1 on failure (runs 1 and 2 exit 1, run 3 exit 0). It also fails a board where a folder allows it but no configuration passed.
- Not run by me: the full run (`tools/build_all.sh`).

## 8. Not done, not settled, not provable

- Not provable without hardware: every real driver behind these interfaces (no real file of U0 except the clock, whose real counter runs only in the simulation here); what each simulated driver "cannot show" (plan section 5 column 4).
- Not settled (for the lead): FACTORY_EXIT's sub-command (section 3 item 1); the sampling states of FW l.928 (item 8); the watchdog rule outside a recording (item 9); the event log code list (item 12) to copy into FW 9.4.
- Not built here: the plan's `tests/rhw/src/headers.c` single file; one file per header instead (the brief allows it).
- K16's two-scenario part (section 5).

## questions_for_owner

none

RESULT: done, the shared headers, the specification constants and the simulated drivers of step 6 exist and the targeted run ends `UNIT PASS tests/rhw` on both simulated targets with each broken copy failing its own named case.
