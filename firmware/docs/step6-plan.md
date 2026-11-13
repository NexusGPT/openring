# Software step 6 (recorder parts): build plan

Author: planning helper, 2026-11-13 (clock read 03:57 CET at the start). Version read: commit 6185c42 of the project (branch master).
Specification: `design/firmware.md` (called FW below; "FW l.N" = line N of that file at 6185c42).
Step approved by the owner: "6 | Recorder parts | Microphones, storage, USB transfer, power and factory tests of the specification, written against simulated drivers. | The storage format, the transfer commands and the power rules run as tests on the simulated board. The drivers themselves stay unproven."

This plan writes no code and runs no test. Every "[to verify]" fact is in section 8. Every choice the specification does not settle is in section 9, with the reading this plan uses until the lead rules.

## 1. What step 6 builds

### 1.1 In one paragraph per part

- **Microphones (FW 4).** The audio part fills 512 ms chunks from the one stereo PDM input (`pdm20`, 2 channels, 16 kHz, 16 bits), replaces a missing block by zeros, drops the first 50 ms, and marks every motor pulse in the chunk headers. The one function that switches the microphone supply on, `rec_mics_on()`, first has the recording sign drawn on the screen.
- **Storage (FW 5).** The raw append-only log on the card: superblock (two copies), index records, event log records, chunks with CRC-32, the recovery scan, free-space accounting (S30, SFULL) and deletion after a confirmed transfer. No file system.
- **USB transfer (FW 6).** The vendor class (one interface, bulk OUT 0x01 and IN 0x81, 64-byte packets at full speed, 512 at high speed) and the 13 commands of FW 6.3 with their 12 status codes.
- **Power (FW 8).** Battery levels B15, B5, B2 from the gauge with the motor's charge added, the charger rules (R-CHG, the one constant `CHARGE_CURRENT`), ship mode entry after VBUS removal, the battery current limit status, the reset causes, the rails per state.
- **Motor (FW 3.1).** The pattern player (M1, M2, M3, MH, MT, MW, MF), the motor charge per pulse for the gauge, the MOTOR edge times for the audio marking, and the motor soft start of the lead's decision "sim finding 4" (`design/wiring/lead-decisions.md` line 29) as a build option with a test.
- **Time, update, factory, log (FW 9).** The saved time, firmware update over USB with the 30 s self-test and the slot limits, the factory sub-commands with the ship beacon (ruling R20), the event log, crash capture, the watchdog feed rule.
- **Join.** The recorder part that carries out the core's actions (open, close, rails, charge, ship, motor, log), starts the core in `BOOT` and feeds it the boot events, and wires everything into the application.

### 1.2 Facts found while reading that shape the plan

1. **The core's table is one row short.** FW l.206 says "The table has 72 transitions"; FW l.148 is the row "`STANDBY` | long press of the joystick centre, recording sign not drawn | `STANDBY` | ... M3; event log record". The generated table has 71 rows (`firmware/modules/ring_core/src/state_table.inc` line 2, `#define RC_TABLE_ROWS 71`) and no such row; its row 16 points at line 148 with the text of the short press (state_table.inc line 19), which is now FW l.149. The guard list of the core has no "sign" fact (`modules/ring_core/include/ring_core/rc_types.h`, enum `rc_guard`). Step 6 must add the row (unit U1, decision D1).
2. **Nothing plays the motor.** `RC_ACT_M1` and `RC_ACT_MW` appear only in `ring_core` (search of `firmware/modules` and `firmware/tests` outside `tests/core`). The application prints recording starts and stops and does nothing else (`firmware/app/src/main.c` lines 67 to 73, `recording_action()`).
3. **The application starts the core in `STANDBY`** "until the recorder part sends the boot events" (`app/src/main.c` lines 110 and 111). Step 6 starts it in `BOOT`.
4. **The glue has no battery call.** `rglue.h` offers `rglue_event()` (system events) but the battery level enters the core only through `rc_core_battery()` (`rc_core.h` line 42), and `rc_core_event()` refuses battery events. Step 6 adds `rglue_battery()` (unit J).
5. **The sign call exists and waits.** `rscr_sign_start()` (`modules/ring_screens/include/ring_screens/rscr.h` lines 78 to 89): allowed under the glue's lock, refused on the screens thread, cancelled on timeout, 0 only when the display accepted every write and is not blanked. Step 4 report: "Nothing calls the function that starts the recording sign yet. The recorder (step 6) must call it before it powers the microphones, and must refuse to record when the sign is not drawn" (`firmware/docs/step4-report.md`, "Not built, not proven").
6. **Rows are looked up by number through the table**, never by a fixed number, in the glue and the screens (`modules/ring_glue/src/rglue.c` lines 41 to 43, `rscr_row_event()` in `rscr_logic.h` line 180). Renumbering rows after the new row 16 therefore does not break them; the core's own row tests and broken copies must follow.
7. **New test folders join the full run without a script change.** Stage 3 runs twister on every `testcase.yaml` under `firmware/tests` (`tools/build_all.sh` lines 119 to 172); stage 5 runs every `tests/<name>/broken_run.sh` (lines 326 to 331); stage 4 runs every `tests/bsim/<name>/run.sh` and its `--broken` copy (lines 177 to 187).
8. **Only `firmware/` reaches the server** (`firmware/README.md`, "Build and test": "It copies `firmware/` to the server"). The core's generator reads `../design/firmware.md` (`modules/ring_core/tools/gen_table.py` line 24), so the generator cannot run on the server (decision D9).
9. **The lane file names one lane for step 6**, `os-recorder`, owning `firmware/modules/ring_recorder/**` and `firmware/tests/recorder/**`, "to be split by part (storage, transfer, power, factory) when step 6 starts" (`firmware/docs/lane-dag.json`). This plan splits it into eleven units (section 3: ten, plus U9 under decision D7); the lead updates `lane-dag.json` (decision D10).
10. **The motor soft start conflicts with FW 3.1.** The lead's decision "sim finding 4" names "a soft start of the motor in the ring software (the enable line switched in steps)" as the fallback when a cell does not meet 1.9 ohm. FW l.314 says: "There is no PWM: the motor's maker rates it only for 2.7 to 3.3 V DC, and a pulse train would restart its own drive chip at each on time (an estimate of motor-drive.md section 3.2)". The plan builds the soft start as a build option, off by default, and lists the conflict (decision D3).
11. **The simulation already proved the dip goes away with C84 at 4.7 uF** ("3.023 V left in place of 2.995 V", `lead-decisions.md` line 29; `design/sim/circuit/sim-notes.md` line 18). The soft start is therefore a fallback, which is why it is off by default.

### 1.3 Limits every unit keeps

- Every unit has a pure part (no kernel call: stdint, stdbool, string, and `crc32_ieee()` from the Zephyr C library, decision D11) that the logic suites cover on `native_sim` and on `nrf54lm20bsim/nrf54lm20a/cpuapp`, and a thin part that calls drivers only through the interfaces of unit U0 (section 5). This is the pattern of step 5 (`firmware/docs/relay-notes.md` section 2, ruling 1: "a pure part (`rrl.c`, no kernel, no Bluetooth) and a Bluetooth part (`rrl_bt.c`)").
- No source of this step names a chip pin by number. Pins come from the devicetree of step 7. P1.24, P1.25 and P0.03 are never configured (FW l.77). A full-run stage checks it (section 6).
- No code or text is copied from Nordic's kit or from Zephyr. Units call the kit's headers and settings only.
- The real driver calls (the thin "real" files) compile in the development kit build only and stay unproven (section 7).
- A long press of the joystick centre stays the only start and stop. No USB command, no Bluetooth write and no factory command starts or stops a recording (FW l.209; the case closes one only by its VBUS).

## 2. Rule table

Units (section 3): U0 `rhw` (root: interfaces, constants, simulated drivers), U1 `core6` (the core's new row), U2 `store`, U3 `audio`, U4 `xfer` (USB transfer), U5 `power`, U6 `motor`, U7 `sys` (time, update, crash, watchdog), U8 `factory`, U9 `screens6` (decision D7), J `recorder` (join). A test name is `<suite>.<case>`; every suite runs on `native_sim` and on `nrf54lm20bsim/nrf54lm20a/cpuapp`. "NP" = not provable without hardware, with the reason. "Step 7" = the board description (pins, devicetree, partitions), outside step 6. "Existing" = built and tested by steps 1 to 5; step 6 adds the proof named when it adds one.

### 2.1 Rules of sections 1 to 3 that step 6 makes true

| Id | Place | Rule | Unit | Proof |
|---|---|---|---|---|
| C1 | FW 1.1 l.112, l.110 | VDD_MIC is on only in `RECORDING`, and in `FACTORY_TEST` only inside a test recording | J | `recorder_rows.test_mic_rail_only_in_recording`: every row of FW 1.2 run from its From state through the real core and the recorder on the simulated drivers; after each row and each 100 ms tick of 10 s, the simulated rail log shows VDD_MIC on only in those two cases |
| C2 | FW 1.1 l.114 to l.118 | B15 at or under 15 %; B5 at or under 5 % or mean voltage at or under 3.45 V; B2 at or under 2 % or at or under 3.30 V; voltage averaged over 10 s | U5 | `power_levels.test_soc_edges` (16, 15, 6, 5, 3, 2 %), `power_levels.test_voltage_edges` (3.451, 3.450, 3.301, 3.300 V), `power_levels.test_mean_of_ten_in_recording` |
| C3 | FW 1.1 l.120, 5.6 | S30 and SFULL thresholds | U2 | `store_space.test_s30_sfull_edges` (3,517 / 3,516 / 17 / 16 free chunks) |
| C4 | FW 1.2 l.125 | "close" = partial chunk, CLOSE record, superblock with open flag clear, stop PDM, clocks low, VDD_MIC off, VDD_SD off, in this order | J | `recorder_actions.test_close_order` (one ordered log across the simulated disk, microphone input and power chip) |
| C5 | FW 1.2 l.126, 4.5 | "open" = VDD_SD on, mount, superblock with open flag and new recording id, then the microphone start of FW 4.5 | J | `recorder_actions.test_open_order` |
| C6 | FW 1.2 l.129 | "charge on" enables the charger at `CHARGE_CURRENT`; already on, nothing changes; "charge off" disables it | U5 | `power_charger.test_charge_on_twice_writes_once`, `power_charger.test_charge_off` |
| C7 | FW 1.2 l.133, l.134; 8.1 l.893 | from `SHIP` or `OFF`, VBUS wakes the ring; `BOOT` turns the charger on before it mounts storage | J | `recorder_boot.test_vbus_boot_charges_before_mount` (order in the log) |
| C8 | FW 1.2 l.135 to l.140, l.216 | `BOOT`: init done with the open flag, VBUS and battery facts; storage init 3 tries 200 ms apart; the order at "init done" (B2, open flag, B5, the rest) | J, U2 | `recorder_boot.test_init_done_each_row` (rows 3 to 8 of the table, each reached from the simulated facts), `store_svc.test_init_three_tries_200ms` |
| C9 | FW 1.2 l.141 to l.143 | `RECOVERY` ends with scan done (VBUS or not) or a read error | J, U2 | `recorder_boot.test_recovery_rows`, `store_recovery.test_read_error_reports` |
| C10 | FW 1.2 l.144; 2.1 l.256 (G3); 3.2 l.342 | a long press in `STANDBY` starts a recording only with the open flag clear, the battery above B5, free space above SFULL and the recording sign drawn | U1, J | `rc_rows.test_row_12` (new guard), `recorder_sign.test_start_draws_sign_before_mic` |
| C11 | FW 1.2 l.148 | the row "recording sign not drawn": no recording, VDD_MIC stays off, M3, event log record | U1, J | `rc_rows.test_row_16` (new row), `recorder_sign.test_sign_refused_no_mic_m3_log` (simulated screens that refuse the frame) |
| C12 | FW 1.2 l.158; 4.4 l.448 | a long press in `RECORDING` closes; M2 runs after VDD_MIC is off | J | `recorder_actions.test_stop_m2_after_mic_off` (MOTOR high time later than the VDD_MIC off time) |
| C13 | FW 1.2 l.159, l.161; 2.1 l.244, l.263 | highlight by short press or by the Bluetooth "highlight", with the time of CENTRE_DOWN; MH | U3, J | `audio_chunk.test_highlight_frame_from_down_time`, `recorder_actions.test_ble_highlight_marks` |
| C14 | FW 1.2 l.162 | VBUS during a recording: close; M2; charge on | J | `recorder_rows.test_vbus_in_recording` |
| C15 | FW 1.2 l.164 to l.169 | B5 and B2 during a recording close it (B2 then ship mode); S30 once; SFULL closes; 3 failed chunk writes: stop PDM, clocks low, VDD_MIC off, superblock left open, MF; no PDM block for 100 ms: close, MF | J, U2, U3 | `recorder_rows.test_recording_exits` (each row from the simulated faults), `audio_svc.test_no_block_100ms_reports`, `store_svc.test_three_tries_then_fault_open_flag_kept` |
| C16 | FW 1.2 l.170; 5.5 | a power loss during a write: nothing runs; the open flag leads to `RECOVERY` at the next start | U2, J | `store_recovery.test_cut_inside_chunk_write` (simulated disk stops mid write; a new mount of the same simulated card sees the open flag), `recorder_boot.test_restart_after_cut_recovers` |
| C17 | FW 1.2 l.171 | USB configured in `CHARGING`: `TRANSFER`, VDD_SD on, mount, charge stays on | J | `recorder_rows.test_usb_configured` |
| C18 | FW 1.2 l.178 to l.182 | in `TRANSFER`: unconfigured finishes the command, VDD_SD off; VBUS removed aborts it; FW_END reboots into the test image; FACTORY_ENTER with the flag | U4, J | `xfer_svc.test_finish_and_abort`, `recorder_rows.test_transfer_rows` |
| C19 | FW 1.2 l.191, l.192 to l.194 | `ERR_STORAGE_FAULT`: every 60 s the caller runs the storage init and reports success or failure | J | `recorder_actions.test_retry_storage_reports_result` (both answers) |
| C20 | FW 1.2 l.201 to l.204 | `FACTORY_TEST`: FACTORY_EXIT reboots; SHIP_ENTER clears the flag; SHIP_SAMPLE keeps it; VBUS removed without a ship command reboots | U8, J | `factory_cmd.test_flag_rules`, `recorder_rows.test_factory_rows` |
| C21 | FW 1.2 l.209; PRD step table | only a long press starts or stops; no USB command, no Bluetooth write, no factory command does | J | `recorder_rules.test_no_command_starts_or_stops` (every USB opcode and every factory sub-command, in every state where USB answers, with a recording state check after each) |
| C22 | FW 1.2 l.210 (R-CHG, ruling R8) | charge on at every VBUS appearance, in every state, also in `BOOT` and `RECOVERY`; off only in `CHARGING` to `ERR_CHARGER` | U5, J | `power_charger.test_on_at_every_vbus`, `recorder_rows.test_charge_on_every_vbus_row` |
| C23 | FW 1.2 l.218; 9.4 l.1065 | watchdog 8 s, fed every 1 s only when the audio and storage threads progressed in the last 2 s | U7 | `sys_wdt.test_feed_only_with_progress`. The reset itself: NP (no watchdog reset in the simulation; section 7) |
| C24 | FW 1.2 l.219 | one recording open at a time; no storage operation while the case reads (USB `BUSY`) | U2, U4 | `store_svc.test_one_open_recording`, `xfer_proto.test_busy_while_running` |
| C25 | FW 2.1 l.229, l.265 | a long press in `CHARGING`, `TRANSFER`, `ERR_STORAGE_FULL`, `ERR_BATTERY_LOW` is refused with M3 | Existing (core), J | the core rows exist; `recorder_actions.test_refusal_plays_m3` checks the motor plays it |
| C26 | FW 2.1 l.241; 2.2 l.301 | MW at 500 ms of a centre hold; the setting "Vibration" off disables MH and MT only, never M1, M2, M3, MF, MW | U6 | `motor_player.test_vibration_off_keeps_the_others` |
| C27 | FW 2.1 l.256 (G3); 4.4 l.447 | at the start: M1 and the sign; the sign is on the screen before VDD_MIC comes on; M1 runs at once | J, U6 | `recorder_sign.test_start_draws_sign_before_mic`, `recorder_actions.test_m1_at_start` (decision D2 sets when M1 starts) |
| C28 | FW 3.1 l.314 | MOTOR high = motor on; no PWM | U6 | `motor_player.test_one_high_per_on_segment` (soft start off) |
| C29 | FW 3.1 l.315 | pattern times are MOTOR-pin times; the player does not lengthen them | U6 | `motor_player.test_every_pattern_pin_times` (each on and off edge at its ms) |
| C30 | FW 3.1 l.318 | a new pattern replaces the one playing, except that M1, M2, M3 and MF are never cut by MH or MT | U6 | `motor_player.test_replace_rules` (all 49 pairs of 7 patterns) |
| C31 | FW 3.1 l.320 to l.328 | the seven patterns and their on/off times | U6 | `motor_player.test_every_pattern_pin_times` |
| C32 | FW 3.1 l.332; 8.3 l.927 | motor charge per ON pulse: t_on x 80 mA + 10 ms x 175 mA; per pattern M1 8.15, M2 16.30, M3 24.45, MH 4.95, MT 3.75, MW 6.55, MF 51.50 mA.s | U6 | `motor_charge.test_charge_per_pattern` (values typed from FW l.332, not computed by the code under test) |
| C33 | FW 3.1 l.333; 4.7 | every pulse during capture is marked from MOTOR high to 50 ms after MOTOR low; the pattern start time is logged | U6, U3, J | `motor_player.test_edge_times_reported`, `audio_motor.*` (A16, A17), `recorder_log.test_pattern_start_logged` |
| C34 | FW 3.1 l.334, l.335 | MT follows the lock fact; whether 25 ms is felt | Existing (core, screens); U6 plays MT | the felt part: NP (bench test F1, a person's thumb) |
| C35 | `lead-decisions.md` l.29 (sim finding 4); FW 3.1 l.314 | motor soft start, the fallback when a cell does not meet 1.9 ohm: the enable line switched in steps | U6 | `motor_soft.test_soft_start_steps`, `motor_soft.test_off_by_default` (decision D3 sets the steps). Whether it lowers the cell dip: NP (motor driver chip behaviour, bench B-M5) |
| C36 | FW 3.2 l.340, l.341 | R-SIGN: the screen is never dark while recording; dimmed at panel level 85, never 0 | Existing (screens); J | `recorder_sign1.test_sign1_every_row` (C38) |
| C37 | FW 3.2 l.342; 4.5 l.457 | `rec_mics_on()` is the only code that enables VDD_MIC; it has the sign drawn first; it enables VDD_MIC only when the frame was accepted; the close turns VDD_MIC off before the screen may leave the recording pictures | J | `recorder_sign.test_only_rec_mics_on_enables_mic` (the simulated power chip records the caller of each rail write), stage `recorder-one-mic-path` (section 6), `recorder_sign.test_close_mic_off_before_screen_leaves` |
| C38 | FW 3.2 l.344 | test SIGN-1: every row of FW 1.2 from its From state with a screen stub that records blanking and every frame; after the row and at every 100 ms of 10 s idle, VDD_MIC on means not blanked and the last frame holds the red dot; a forced draw failure at the start leaves VDD_MIC off | J | `recorder_sign1.test_sign1_every_row`, `recorder_sign1.test_forced_draw_failure`. The OLED_PWR_EN part: NP (no panel driver: the memory display has no OLED_PWR_EN; step 4 report, "Not built") |
| C39 | FW 3.3 l.374 | SCR_CHARGING shows battery %, "Charging" or "Full", time to full from the gauge | J, U5 | `recorder_screens.test_battery_reaches_screens` (`rscr_set_battery()` called with the gauge values) |
| C40 | FW 3.3 l.364, l.365, l.375, l.377 | SCR_RECORDINGS list, SCR_RECORDING_INFO, SCR_TRANSFER fields, SCR_RECOVERY chunks scanned | not in step 6 by default (decision D7) | the screens part has no read for these fields (`struct rscr_ops`, `rscr.h` lines 19 to 44) |
| C41 | FW 3.3 l.380 to l.383 | screen power sequence (LCD_RST, OLED_PWR_EN, SWIRE) | Step 7 and the panel driver (W2) | NP: no panel driver exists (PRD, "Not in this plan") |

### 2.2 Section 4, audio

| Id | Place | Rule | Unit | Proof |
|---|---|---|---|---|
| A1 | FW 4.1 l.402, l.406, l.408 to l.420 | one instance `pdm20`, 2 channels; `pcm_rate` 16,000, `pcm_width` 16, `req_num_chan` 2, the channel map, clock window 1,200,000 to 1,650,000 Hz, `block_size` 1,024, 8 blocks | U3 | `audio_cfg.test_dmic_config_values` (the simulated microphone input records the configuration it received) |
| A2 | FW 4.1 l.404, l.416 | the driver picks 1.280 MHz, prescaler 25, ratio 80 | U3 | NP: the pick is made inside the kit's PDM driver, which the simulated input replaces. `audio_cfg.test_header_clock_fields` checks only that the header carries 1,280,000 and 80 |
| A3 | FW 4.1 l.417; 5.3 l.562 | gain 0 dB, register value 0x28; header `gain_code` 0x28 | U3 | `audio_cfg.test_gain_zero`, `store_fmt.test_chunk_header_bytes`; the register write itself: NP |
| A4 | FW 4.1 l.418, l.422 | left = mic 1, right = mic 2 | U3 | `audio_chunk.test_interleave_order` (the order of the blocks is kept, channel 0 first). Which microphone lands left: NP (edge of the real part, T-MIC on each ring) |
| A5 | FW 4.1 l.423 | samples stored as they come; no level rule | U3 | `audio_chunk.test_payload_equals_blocks` (bytes equal, after the 50 ms) |
| A6 | FW 4.2 l.428, l.429 | HFXO requested and running before the microphones start, released after they stop; start order: configure, HFXO, trigger | U3, J | `audio_svc.test_hfxo_before_trigger`, `audio_svc.test_hfxo_released_after_stop` |
| A7 | FW 4.2 l.430 | a missing block is replaced by zeros of the same length, sets flag bit 7, counts in `dropout_blocks`, is logged; the recording never changes length | U3 | `audio_chunk.test_dropout_zero_fill`, `audio_svc.test_dropout_logged` |
| A8 | FW 4.3 l.434 to l.443 | block 1,024 bytes = 16 ms; 32 blocks per chunk; chunk ring of 3 | U3 | `audio_chunk.test_32_blocks_per_chunk`, `audio_svc.test_ring_of_three` (a fourth full chunk waits; nothing is overwritten) |
| A9 | FW 4.4 l.447; 4.5 l.460 | the first kept frame is 50 ms (800 frames) after the PDM start; the recording time is that of the first kept frame | U3 | `audio_chunk.test_discard_800_frames`, `audio_chunk.test_start_time_is_first_kept_frame` |
| A10 | FW 4.4 l.448 | at a stop the frames up to the 1,000 ms mark are kept; the press start time is logged | U3, J | `audio_svc.test_stop_keeps_frames_to_mark`, `recorder_log.test_stop_press_time_logged` |
| A11 | FW 4.4 l.449 | nothing captured before the start press; no earlier audio kept in RAM | U3 | `audio_svc.test_no_read_outside_recording` (no microphone read call outside an open recording) |
| A12 | FW 4.5 l.455 to l.460 | start: HFXO, `rec_mics_on()` (sign, then VDD_MIC), wait 1 ms, configure and start PDM, discard 50 ms | J | `recorder_sequence.test_start_order_and_times` |
| A13 | FW 4.5 l.463 | stop: trigger STOP, wait for the blocks to be released, clock pin sleep state, VDD_MIC off, HFXO released; only then the screen may leave the recording pictures | J | `recorder_sequence.test_stop_order` |
| A14 | FW 4.5 l.465 | MIC_A_CLK low whenever VDD_MIC is off; sleep state applied at boot before VDD_MIC is ever on; DATA input with no pull | U3 | `audio_svc.test_clock_low_whenever_rail_off` (a fact of the simulated input: the thin part's sleep-state call precedes every rail-off and follows boot). Real pin levels: NP |
| A15 | FW 4.6 | RAM budget; the chunk ring is never below 3 chunks | U3 | a build assertion on the ring size (broken copy `ring_two` fails the build); the real RAM use: the development kit build's memory report (stage `dk`), the lines themselves NP |
| A16 | FW 4.7 l.495 | a motor interval runs from the frame of MOTOR high to 50 ms (800 frames) after MOTOR low | U3 | `audio_motor.test_interval_frames` |
| A17 | FW 4.7 l.496; 5.3 l.576, l.577 | edge times converted to frames of the current chunk; each overlapping interval written in that chunk's header, flag bit 3; an interval over two chunks is written in both, cut at the edge; at most 4, a fifth merged into the fourth | U3 | `audio_motor.test_span_two_chunks`, `audio_motor.test_fifth_merged_into_fourth`, `audio_motor.test_unused_pairs_ff` |
| A18 | FW 4.7 l.497, l.498 | M1 runs during the discarded 50 ms, the rest plus 50 ms is marked in the first chunk; MW in a recording is marked | U3, J | `audio_motor.test_m1_rest_marked_in_first_chunk`, `recorder_actions.test_mw_in_recording_marked` |
| A19 | FW 4.5 l.453 | power-up 50 ms, current, sleep current of the part | none | NP: microphone physics |
| A20 | FW 4.1 l.422 | microphone wiring (DATA through R31 and R32, SELECT on GND and on VDD_MIC) | none | NP: board wiring; T-MIC on each ring |

### 2.3 Section 5, storage

| Id | Place | Rule | Unit | Proof |
|---|---|---|---|---|
| S1 | FW 5.1 l.504, l.505 | `zephyr,sdhc-spi-slot` on `spi00` at 16 MHz, `zephyr,sdmmc-disk` "SD" | Step 7 | NP: no card and no SPI in the simulation |
| S2 | FW 5.1 l.506 | before VDD_SD off: disk deinit, then `spi00` suspended (sleep state); after VDD_SD on: wait 1 ms, resume, disk init; sleep state at boot before any SPI use | U2 | `store_svc.test_rail_sequence` (ordered log: deinit, suspend, rail off / rail on, 1 ms, resume, init) and `store_svc.test_no_disk_call_with_rail_off` (the simulated disk refuses and counts any call while the simulated VDD_SD is off). The pin levels: NP |
| S3 | FW 5.1 l.507 | disk access API, no file system; sector count read at mount | U2 | `store_svc.test_mount_reads_sector_count` |
| S4 | FW 5.2 l.519 to l.531 | sector map: superblock A at 0, B at 1, log 2 to 2,047, reserved, index 8,192 to 73,727, chunk area from 81,920; `chunk_count_total` = floor((sectors - 81,920) / 65); chunk s at 81,920 + (s mod total) x 65 | U2 | `store_layout.test_sector_map`, `store_layout.test_chunk_lba_wraps` (s = total - 1, total, total + 1), `store_layout.test_examples` (7,812,500 sectors gives 118,932 chunks; 7,226,562 gives 109,917, FW l.654) |
| S5 | FW 5.2 l.514; 5.5 l.644 | no written sector is rewritten during a recording | U2 | `store_svc.test_no_rewrite_during_recording` (write log of the simulated disk: every chunk sector once; superblock and index sectors outside the chunk area) |
| S6 | FW 5.2 l.515 | one 65-sector write per chunk, sequential addresses | U2 | `store_svc.test_one_write_per_chunk`. Whether the card gets one CMD25: NP (FW 10.5 item 12) |
| S7 | FW 5.3 l.537 to l.580 | the chunk header, every field at its offset | U2 | `store_fmt.test_chunk_header_bytes` (expected bytes written out by hand in the test from the FW table, not produced by the code under test) |
| S8 | FW l.70; 5.3 l.579, l.580 | CRC-32/ISO-HDLC over the payload and over header bytes 0 to 507; little-endian fields | U2 | `store_fmt.test_crc_check_value` ("123456789" gives 0xCBF43926), `store_fmt.test_little_endian` |
| S9 | FW 5.3 l.535, l.555, l.556 | `frames`, `payload_bytes` = frames x 2 x 2; unused payload bytes of the last chunk are zero | U2, U3 | `store_fmt.test_last_chunk_zero_tail`, `audio_chunk.test_partial_last_chunk` |
| S10 | FW 5.3 l.547 | flag bits 0 to 7 and 8 to 15 zero | U3 | `audio_chunk.test_flags_each_bit` (first, last, motor, clipped at -32768 and at 32767, time not set, B15, dropout) |
| S11 | FW 5.3 l.576, l.582; 5.4 l.626, l.632 | up to 8 highlights per chunk header (frame offset of the press), the first 32 in the CLOSE record (ms from the start), `highlight_count` | U3, U2 | `audio_chunk.test_highlights_in_header`, `store_index.test_close_highlights_32` (decision D4 for a ninth in one chunk) |
| S12 | FW 5.3 l.557, l.558, l.573, l.583 | `utc_ms` (0 when not set), `uptime_ns`, `cycle_hz` | U3 | `audio_chunk.test_timestamps`, `audio_chunk.test_time_not_set` |
| S13 | FW 5.3 l.568 to l.571 | `battery_mv`, `temp_c_x10`, `boot_count`, `fw_version` filled | U3 | `audio_chunk.test_fill_fields` (values from the simulated power chip and the superblock) |
| S14 | FW 5.4 l.587 to l.610 | superblock fields; written to LBA `sb_seq` mod 2; at mount the valid copy with the higher `sb_seq` wins | U2 | `store_fmt.test_superblock_bytes`, `store_log.test_mount_picks_newer_valid_copy` (both valid, one bad CRC, one bad magic, both bad) |
| S15 | FW 5.4 l.612 to l.634 | index record fields; at 8,192 + (n mod 65,536); types CLOSE, CONFIRM, DELETE; close states | U2 | `store_fmt.test_index_record_bytes`, `store_layout.test_index_lba_wraps` |
| S16 | FW 5.4 l.630 | digest = CRC-32 over the `payload_crc32` values of all chunks in order, as 4-byte little-endian words | U2 | `store_fmt.test_digest` (3 chunks, value typed in the test) |
| S17 | FW 5.4 l.636 | a recording's state is its last record | U2 | `store_index.test_state_is_last_record` |
| S18 | FW 5.5 l.640, l.641 | VDD_SD on for the whole recording, off between; a chunk written as soon as full; the partial chunk at close; the superblock twice per recording | U2, J | `store_svc.test_superblock_twice_per_recording`, `recorder_rails.test_sd_rail_per_state` |
| S19 | FW 5.5 l.642 | rail on during a recording until bench S1 | U2 | the rule is the default and is tested by S18; bench S1: NP |
| S20 | FW 5.5 l.643 | a failed chunk write is retried 2 times at once (3 tries), then the fault | U2 | `store_svc.test_three_tries_then_fault_open_flag_kept` |
| S21 | FW 5.5 l.644 | audio lost on a cut: normal at most 1,024 ms, worst 1.536 s (3 chunks) | U2, U3 | `store_recovery.test_loss_bound_with_stalled_card` (a stalled simulated card: at most 3 chunks are missing after recovery) |
| S22 | FW 5.5 l.645 | a chunk cut in flight fails its CRC and is dropped; the superblock is never in flight with a chunk; every chunk of the open recording is checked | U2 | `store_recovery.test_cut_inside_chunk_write` (cut after each of sectors 1, 33 and 64 of the 65) |
| S23 | FW 5.5 l.646 | the scan keeps a chunk while magic, header CRC, payload CRC, `recording_id` and `chunk_seq` = previous + 1 all match; stops at the first mismatch; CLOSE record RECOVERED; `head_chunk_seq` past the last good chunk; open flag cleared | U2 | `store_recovery.test_stop_on_each_mismatch` (five cases, one per field), `store_recovery.test_recovered_close_record` |
| S24 | FW 5.6 l.650 to l.653 | used and free chunks; SFULL at or under 16; S30 at or under 3,516; "storage left" = free x 0.512 s | U2 | `store_space.test_counts`, `store_space.test_s30_sfull_edges`, `store_space.test_storage_left_minutes` |
| S25 | FW 5.6 l.654 | which size the real card shows at mount | none | NP (FW 10.5 item 25) |
| S26 | FW 5.7 l.658 | CONFIRM compares the case's digest with the CLOSE digest: match appends CONFIRM; no match DIGEST_MISMATCH, nothing changes | U2, U4 | `store_delete.test_confirm_match_and_mismatch` |
| S27 | FW 5.7 l.659 | DELETE refused without CONFIRM (`NOT_CONFIRMED`) | U2, U4 | `store_delete.test_delete_needs_confirm` |
| S28 | FW 5.7 l.660 | DELETE appends a record, moves `tail_chunk_seq` over every leading deleted recording in chunk order, writes the superblock; a deleted recording in the middle stays counted as used | U2 | `store_delete.test_tail_moves_over_leading_only` (delete the second of three: free unchanged; then the first: both freed) |
| S29 | FW 5.7 l.661 | audio sectors are not erased; READ_RANGE refuses a deleted recording (`NOT_FOUND`) | U2, U4 | `store_delete.test_no_erase`, `xfer_store.test_read_range_deleted_not_found` |
| S30 | FW 5.2 l.516 | wear of the card's own controller | none | NP (FW 10.5 item 11) |

### 2.4 Section 6, USB transfer

| Id | Place | Rule | Unit | Proof |
|---|---|---|---|---|
| X1 | FW 6.1 l.667, l.668 | `usbhs` (DWC2) with the device stack "device_next" | U4 | NP for the controller (no USB controller in the simulation). The stack calls: see X2 |
| X2 | FW 6.1 l.669 | one vendor interface 0xFF/0x00/0x00, bulk OUT 0x01, bulk IN 0x81; full speed 64 bytes, high speed 512 bytes; both configurations registered; descriptors picked with `usbd_bus_speed()` | U4 | `xfer_desc.test_descriptor_bytes_fs_hs` (the class's descriptor tables against bytes typed from FW 6.1). Served by the stack to a host: only if the virtual USB controller of `native_sim` exists and works at SDK 3.4.2 ([to verify] K3); then `xfer_usb.test_virtual_host_enumerates_fs` (decision D6), else NP |
| X3 | FW 6.1 l.670 | the ring enumerates at full speed with the case's full-speed host | none | NP (PHY behaviour, case bench B1) |
| X4 | FW 6.1 l.673; 8.6 l.978 | USB answers only in `CHARGING`, `TRANSFER`, `FACTORY_TEST`; the stack runs only while VBUS is present: `usbd_enable()` after VBUS ready, `usbd_disable()` on VBUS removed; `TRANSFER` on `USBD_MSG_CONFIGURATION` | U4, J | `xfer_svc.test_stack_follows_vbus` (simulated VBUS events: enable count and disable count), `recorder_rows.test_usb_events_reach_core` |
| X5 | FW 6.2 l.677 to l.686 | 16-byte header: magic 0x5252, opcode, status (0 in requests), tag echoed, length, CRC-32 of the payload (0 when the length is 0) | U4 | `xfer_proto.test_header_bytes`, `xfer_proto.test_tag_echoed`, `xfer_proto.test_crc_zero_for_empty` |
| X6 | FW 6.2 l.688 | the response is exactly 16 + `length` bytes; no zero-length packet | U4 | `xfer_proto.test_response_length_exact`, `xfer_svc.test_no_zero_length_packet` (simulated transport log) |
| X7 | FW 6.2 l.689, l.690 | status codes 0 to 11; a wrong magic or CRC gets that status and no payload | U4 | `xfer_proto.test_bad_magic`, `xfer_proto.test_bad_crc`, `xfer_proto.test_unknown_opcodes` (all 243 values outside 0x01 to 0x0D give UNKNOWN_OPCODE) |
| X8 | FW 6.3 l.696 | GET_INFO: 35 bytes in the stated order | U4 | `xfer_proto.test_get_info_layout` |
| X9 | FW 6.3 l.697 | LIST_RECORDINGS: first, max 1 to 64; count then 64-byte entries | U4, U2 | `xfer_proto.test_list_args` (max 0 and 65 give BAD_ARG), `xfer_store.test_list_entries` (decision D5 for the meaning of "first") |
| X10 | FW 6.3 l.698; 6.4 l.715 | READ_RANGE: chunk_count 1 to 256; each chunk exactly as stored | U4, U2 | `xfer_proto.test_read_range_args`, `xfer_store.test_read_range_bytes_equal_disk` |
| X11 | FW 6.3 l.699, l.700 | CONFIRM, DELETE (free chunks after) | U4, U2 | `xfer_store.test_confirm_then_delete` |
| X12 | FW 6.3 l.701; 9.1 l.1004 | SET_TIME sets the clock (UTC, zone known) | U4 | `xfer_proto.test_set_time_calls_clock` (`rtime_set()` with the values and zone known true) |
| X13 | FW 6.3 l.702 | GET_BATTERY: mV, SoC x10, charging state 0 to 5, die temperature, time to full | U4, U5 | `xfer_proto.test_get_battery_layout`, `power_report.test_charge_state_codes` |
| X14 | FW 6.3 l.703 to l.705; 9.2 | FW_BEGIN, FW_DATA (1 to 4,096 bytes), FW_END | U4, U7 | `xfer_proto.test_fw_args`, `sys_update.*` (T6 to T10) |
| X15 | FW 6.3 l.706 | GET_LOG: first, max 1 to 32; 512-byte records | U4, U2 | `xfer_proto.test_get_log_args`, `xfer_store.test_get_log_records` |
| X16 | FW 6.3 l.707 | REBOOT | U4 | `xfer_proto.test_reboot_after_ok` (the reboot request comes after the OK response was handed to the transport) |
| X17 | FW 6.3 l.708 | FACTORY: NOT_ALLOWED when the factory flag is clear | U4, U8 | `xfer_proto.test_factory_not_allowed` |
| X18 | FW 6.3 l.710 | the case's order (SET_TIME, GET_BATTERY, LIST) | none | a rule of the case, not of the ring; the ring accepts any order (`xfer_proto.test_any_order`) |
| X19 | FW 6.3 l.711 | BUSY while the previous command still runs | U4 | `xfer_proto.test_busy_while_running` |
| X20 | FW 6.4 l.715 to l.717 | no transfer state kept on the ring; the case's digest equals the ring's | U4, U2 | `xfer_store.test_resume_from_any_chunk`, `xfer_store.test_case_digest_matches_close` |
| X21 | FW 6.4 l.718 | transfer time 3.21 minutes per recorded hour | none | NP (bench S2, case bench B1) |
| X22 | FW 6.1 l.672; 5.2 l.517 | no mass storage class and no serial class: the case reads only through the vendor protocol | U4 | `xfer_desc.test_one_vendor_interface_only` |

### 2.5 Section 8, power

| Id | Place | Rule | Unit | Proof |
|---|---|---|---|---|
| P1 | FW 8.1 l.862 to l.890 | the power chip's devicetree properties (address 0x6B, interrupt pin, regulators, load switches, charger, thermistor, die temperature) | Step 7 | NP: devicetree of the real board, names TO CONFIRM (FW 10.5 item 3) |
| P2 | FW 8.1 l.878, l.894 (rule 2) | `CHARGE_CURRENT` is one named constant, 15,000 µA, in one place; the build fails when it is unset, above 17,600, under 4,000, over 100,000 or not a multiple of 500 | U5 | build assertions; broken copies `cc_unset`, `cc_17601`, `cc_3999`, `cc_100500`, `cc_15250` each fail the build with the named assertion message (section 3, U5) |
| P3 | FW 8.1 l.894 | the charger is disabled before the current register is written and enabled after | U5 | `power_charger.test_disable_write_enable_order` |
| P4 | FW 8.1 l.893 (rule 1) | first power: `BOOT` turns the charger on before it mounts storage | J | C7 |
| P5 | FW 8.1 l.879 to l.889, l.895 to l.908 (rules 3 to 5) | termination, trickle, VBUS limit, thermistor and die-temperature limits; charge times; the chip stops and resumes by itself | Step 7 (settings); none | NP: the charger's own behaviour |
| P6 | FW 8.2 l.912 to l.920 | rails per state: VDD_MIC only in `RECORDING`; VDD_SD in `BOOT`, `RECOVERY`, `RECORDING`, `TRANSFER`; HFXO on in `BOOT`, `RECOVERY`, `RECORDING` and `TRANSFER`, with USB in `CHARGING` (ruling of 2026-11-13 after review finding R6-04: the table of FW 8.2 holds) | J | `recorder_rails.test_rails_per_state` (simulated rail and HFXO facts after every row). Radio and wake sources: existing parts; System ON idle: NP |
| P7 | FW 8.2 l.922 | VMOT (U11) on only while MOTOR is high | U6 | `motor_player.test_pin_low_between_patterns` (the regulator itself: NP) |
| P8 | FW 8.3 l.926, l.927 | each sample feeds the gauge; the motor's charge since the last sample is added as a discharge: I_fed = I_measured + Q_motor / t_sample | U5 | `power_gauge.test_motor_charge_added` (one MF, 51.50 mA.s, in a 1 s sample adds 51.5 mA, FW l.927). The sign the library expects: [to verify] K6 |
| P9 | FW 8.3 l.928 | a sample every 1 s in the recording states (thresholds on the mean of the last 10), every 60 s in the other awake states (single sample); every sample also reads the current limit status | U5 | `power_sample.test_period_per_state`, `power_sample.test_ilim_read_with_every_sample` |
| P10 | FW 8.3 l.929, l.930 | the battery model of the real cells; full scale | none | NP (cell maker, bench) |
| P11 | FW 1.2 l.210 (R-CHG), l.211 to l.213 (R-STB, R15, R16) | the level is reported to the core on every change, both directions; B2 before B5 when VBUS goes | U5, J | `power_levels.test_report_on_change_both_ways`, `recorder_rows.test_vbus_out_at_b2_goes_off` (the order rule itself is the core's, existing) |
| P12 | FW 8.4 l.936 to l.941 | ship entry: (1) close everything, save settings and time (SHIP_ENTER clears the flag, SHIP_SAMPLE keeps it); (2) SHPHLDCONFIG at 96 ms and TASKSHPHLDCFGSTROBE; (3) with VBUS, wait for VBUS removed, doing nothing else, USB disabled; (4) TASKENTERSHIPMODE; (5) still running 1 s later: log, back to step 3 once | U5, J | `power_ship.test_entry_order_without_vbus`, `power_ship.test_waits_for_vbus_removed`, `power_ship.test_retry_once_after_1s`, `recorder_actions.test_ship_closes_everything_first` |
| P13 | FW 8.4 l.939 | only the factory commands reach step 3 with VBUS present: every row into `OFF` starts without VBUS | U5 | `power_ship.test_off_never_waits` |
| P14 | FW 8.4 l.943; 8.7 l.996 | after a wake, `BOOT` reads RSTCAUSE and the charger error log, writes them into the event log, clears them (TASKCLRERRLOG) | U5 | `power_reset.test_causes_logged_then_cleared` (each of the 7 bits) |
| P15 | FW 8.4 l.943, l.945 | the chip leaves ship mode on VBUS; ship current | none | NP (the power chip) |
| P16 | FW 8.5 | currents and hours per state; R19 | none | NP (bench T2) |
| P17 | FW 8.6 l.977 to l.980 | VBUS is an input only; D+ and D- are not driven while worn; a case is recognised only by VBUS from the power chip; GND nothing | U4, U5 | X4 for the stack; `power_cfg.test_no_vbus_output_call` (the power interface has no call that drives VBUS, and the simulated chip counts none). Pad and pin levels: NP |
| P18 | FW 8.7 l.990 to l.995 | the current limit bit ACTIVE: one log record (mV, state, screen on); the screen off for 10 s, in `RECORDING` SCR_REC_DIM for 10 s, never dark; nothing closed or refused; no motor; again with the screen off: logged with a count, nothing else | U5, J | `power_ilim.test_first_active`, `power_ilim.test_again_with_screen_off`, `recorder_screens.test_ilim_dims_in_recording` (decision D7: the screens part needs a call for this) |
| P19 | FW 8.7 l.997 | power-fail warning not used: POFCONFIG and VSYSPOF left at reset | U5 | `power_cfg.test_pof_untouched` (no write to those registers in the simulated chip's log) |
| P20 | FW 8.7 l.988, l.989 | the limit is fixed; the chip path stays under 55.7 mA | none | NP |

### 2.6 Section 9, time keeping, update, factory, logging

| Id | Place | Rule | Unit | Proof |
|---|---|---|---|---|
| T1 | FW 9.1 l.1003 | the GRTC from the 32.768 kHz crystal, 20 ppm | none | NP |
| T2 | FW 9.1 l.1004 | wall time = uptime + offset, set by SET_TIME at every insertion, by the Bluetooth Time characteristic and by the iPhone | Existing (`ring_time`, iPhone part); U4 | X12. The Bluetooth Time characteristic of FW 7.2 l.751 is not built by step 6 (FW 7 is outside this step) |
| T3 | FW 9.1 l.1004 | a recording started while the zone is unknown "carries the flag" | U3 | decision D8 (no header field holds it); `audio_chunk.test_zone_unknown_flag` once ruled |
| T4 | FW 9.1 l.1005 | the last time is saved on entry into `SHIP` and `OFF`; after the next boot it is a guess, the time is "not set" (chunk flag bit 5, `utc_ms` 0) and the screen shows "--:--" until SET_TIME | U7, U3 | `sys_time.test_saved_on_ship_and_off`, `sys_time.test_guess_is_not_set`, `audio_chunk.test_time_not_set` |
| T5 | FW 9.2 l.1009 to l.1011 | MCUboot, swap using move, the flash layout (64 KB, 976 KB, 976 KB, 20 KB) | Step 7; U7 | the layout constants: `sys_update.test_layout_sums_to_2036_kb`; swap and rollback: NP (MCUboot does not run in the simulated builds, which build without sysbuild, `build_all.sh` line 89) |
| T6 | FW 9.2 l.1012 (rules 1 to 3) | the USB path writes only slot 1: FW_BEGIN refuses `image_size` above 999,424 and FW_DATA an end past it, with BAD_ARG; no command writes MCUboot or slot 0; settings only through the settings subsystem | U7, U4 | `sys_update.test_size_limit` (999,424 accepted, 999,425 refused), `sys_update.test_data_end_limit`, `sys_update.test_writes_only_slot1` (the simulated image store's write log) |
| T7 | FW 9.2 l.1012 (rule 4) | the chip's own write protection of the MCUboot area | Step 7 and assembly | NP (FW 10.5 item 33) |
| T8 | FW 9.2 l.1013 | FW_BEGIN erases slot 1; FW_DATA blocks; FW_END checks the CRC-32, requests the test upgrade, reboots after the OK | U7, U4, J | `sys_update.test_sequence`, `sys_update.test_end_bad_crc_fw_error`, `recorder_rows.test_fw_end_row` |
| T9 | FW 9.2 l.1014 | self-test within 30 s: storage mounts, Bluetooth enables, USB enumerates again with VBUS; microphones not powered; all pass: confirm; any fail or 30 s: reboot without confirming | U7, J | `sys_update.test_self_test_pass_confirms`, `sys_update.test_self_test_timeout_reboots`, `sys_update.test_self_test_no_mic` |
| T10 | FW 9.2 l.1015 | an update only with the battery above 30 % or VBUS present | U7 | `sys_update.test_allowed_rule` (30 % refused, 30.1 % accepted, VBUS any) (decision D12 for the status code) |
| T11 | FW 9.3 l.1019 | FACTORY ENTER (0x01) only with the factory flag 1; the flag cleared only by SHIP_ENTER (0x7F); SHIP_SAMPLE (0x7E) keeps it; flag clear: NOT_ALLOWED | U8, U7 | `factory_cmd.test_flag_rules`, `sys_persist.test_factory_flag_survives_reboot` |
| T12 | FW 9.3 l.1020 | each test answers result u8 (0 pass, 1 fail, 2 timeout) and its values; the jig judges | U8 | `factory_cmd.test_result_layout` |
| T13 | FW 9.3 l.1024; R18 l.1053 | T-MIC1/T-MIC2: a 2 s test recording (type 2) through the normal path; RMS of each channel in dBFS; count of identical consecutive samples; the microphones only through `rec_mics_on()` after the sign; no screen, no test | U8, J | `factory_mic.test_rms_and_runs` (simulated input with a known sine and a stuck channel), `factory_mic.test_type_2_recording`, `factory_mic.test_no_screen_no_mic`. Real levels and the 1 kHz speaker: NP |
| T14 | FW 9.3 l.1025 | T-SCREEN: red, green, blue, white, black 1 s each, then a grid | U8 | `factory_screen.test_frames_reach_display` once the screens part has the call (decision D7); the camera: NP |
| T15 | FW 9.3 l.1026, l.1027 | T-JOY and T-CENTRE: events reported to the jig; single, double, long and MW; factory test mode never starts a recording | U8 | `factory_input.test_directions_reported`, `factory_input.test_centre_reported_never_records` (real core gestures fed by edges) |
| T16 | FW 9.3 l.1028 | T-MOTOR: VBAT before, MOTOR on 500 ms, VBAT 250 ms into the pulse, report both and the dip | U8 | `factory_motor.test_reads_and_timing` (simulated power chip voltage with a set dip). The dip and the accelerometer: NP |
| T17 | FW 9.3 l.1029 | T-SIGN: two 1 s test recordings 1 s apart; report the VDD_MIC on and off times | U8, J | `factory_sign.test_two_recordings_times`. The camera: NP |
| T18 | FW 9.3 l.1030 | T-STORE: VDD_SD on, init, write 65 sectors at LBA 4,096, read back, compare CRC, time both; delete every type-2 recording | U8, U2 | `factory_store.test_area_write_read`, `factory_store.test_test_recordings_deleted`. Speeds: NP |
| T19 | FW 9.3 l.1031 | T-RADIO: advertise 10 s at 0 dBm, 100 ms | U8 | `factory_radio.test_adv_parameters` (the advertising call's arguments); received power: NP. A scanner over BabbleSim: decision D6 |
| T20 | FW 9.3 l.1032 | T-CHARGE: state, latched errors, current; fail when off or an error is latched | U8, U5 | `factory_charge.test_fail_when_off_or_error` |
| T21 | FW 9.3 l.1033 | T-XTAL: GRTC against USB start-of-frame over 10 s, within 50 ppm | U8 | `factory_xtal.test_ppm_arithmetic` (counts in, ppm out); the measurement: NP (no start-of-frame in the simulation) |
| T22 | FW 9.3 l.1034, l.1035, l.1057 (R20) | ship beacon from the acceptance of SHIP_ENTER or SHIP_SAMPLE until TASKENTERSHIPMODE: not connectable, every 100 ms, 0 dBm, name "Ring" plus the last 4 hex digits of the device id; only in `FACTORY_TEST` | U8, U5 | `factory_ship.test_beacon_window` (advertising start before the wait, stop before the ship task), `factory_ship.test_beacon_name` ; over BabbleSim with a scanner: decision D6 |
| T23 | FW 9.3 l.1037 | sub-command 0x11 answers BAD_ARG | U8 | `factory_cmd.test_0x11_bad_arg` |
| T24 | FW 9.3 l.1043 to l.1056 | the factory flow by assembly step; the cell-only check: `boot_count` does not change when VBUS goes and comes back in `CHARGING` and `STANDBY` | J | `recorder_boot.test_boot_count_only_at_boot`; the flow itself is the jig's (W13 jig side not built) |
| T25 | FW 9.4 l.1061 | development builds log on `uart20` at 115,200; production builds none, pins pulled down | Step 7 | NP |
| T26 | FW 9.4 l.1062 | event log record: 512 bytes, magic "RRLG", seq, uptime_ns, utc_ms, code, state, 16 argument bytes, crash block, CRC-32 last; 8 records wait in 4 KB of RAM; written at the next time VDD_SD is on; when full the oldest unwritten is dropped and counted | U2 | `store_fmt.test_log_record_bytes`, `store_evlog.test_buffer_of_8_drops_oldest`, `store_evlog.test_written_when_rail_on`, `store_evlog.test_ring_of_2046` |
| T27 | FW 9.4 l.1062 | each state change, fault, battery threshold and transfer command becomes a record | J | `recorder_log.test_each_kind_logged` (decision D13 fixes the code list) |
| T28 | FW 9.4 l.1063 | crash capture: the fatal error handler writes a crash block (reason, PC, LR, PSR, thread name, 64 stack words) into retained RAM and the reason into `gpregret1`, then reboots; `BOOT` copies a valid block into the log and clears it | U7 | `sys_crash.test_block_format`, `sys_crash.test_boot_copies_valid_block_once` (simulated retained RAM). The handler on the real chip, and retained RAM across a real reset: NP |
| T29 | FW 9.4 l.1065 | watchdog rule | U7 | C23 |

## 3. Units

Rules for every unit:
- A unit edits only the files it owns. A public header is written by U0 and frozen; a unit that needs a change asks the lead, who has U0's helper change it (one writer per file).
- Paths are under `firmware/` (called F/ below).
- Every unit runs its own targeted run, from the project folder, with its own server copy:
  `RING_REMOTE_SRC=/root/ring-os/src-u-<name> sh firmware/tools/remote.sh u-<name> "bash tools/unit_run.sh tests/<name>"`
  `tools/unit_run.sh` (written by U0) runs twister on the one folder on `native_sim` and on `nrf54lm20bsim/nrf54lm20a/cpuapp`, then the folder's `broken_run.sh`, and ends with `UNIT PASS tests/<name>` or `UNIT FAIL tests/<name> <parts>`.
- A broken copy follows the step 5 pattern (`tests/relay/broken_edit.py` and `broken_run.sh`): one exact edit that must match once, the suite builds and runs to its end, and the named case fails on both targets. A copy that fails for another reason, or does not build when it should, counts as not failing.
- A unit's notes file names, for each of its rows of section 2, the test and the log line that proves it, and quotes the last line of the run it cites.
- "Done when" is checked by the lead from the cited log.

### U0 `rhw`: root (interfaces, spec constants, simulated drivers)

- **Owns:** F/modules/ring_rhw/** (`zephyr/module.yml`, `CMakeLists.txt`, `Kconfig`, `include/ring_rhw/rhw.h`, `include/ring_rhw/rrec_spec.h`, `include/ring_rhw/rhw_sim.h`, `src/sim_*.c`, `src/rhw_clock_real.c`, `dts/bindings/ring,sim-disk.yaml`, `dts/bindings/ring,sim-mic.yaml`); every public header of U2 to U8 and J: F/modules/ring_store/include/**, ring_audio/include/**, ring_xfer/include/**, ring_power/include/**, ring_motor/include/**, ring_sys/include/**, ring_factory/include/**, ring_recorder/include/**; F/tests/rhw/**; F/tools/unit_run.sh; F/docs/rhw-notes.md.
- **Offers:**
  - `rrec_spec.h`: every number of FW 4, 5, 6, 9 that more than one unit uses, each with its FW line: sector map and chunk sizes (FW 5.2, 5.3), magics, record sizes, opcodes 0x01 to 0x0D, status codes 0 to 11, factory sub-commands, the pattern ids M1 to MF, S30 3,516 and SFULL 16, the slot limits of FW 9.2. Nothing else defines these numbers (a number in two files is a defect).
  - `rhw.h`: one interface per kind of driver, each a struct of function pointers with an active instance chosen at start (simulated when `CONFIG_RING_RHW_SIM=y`, real otherwise):
    - disk: init, deinit, read sectors, write sectors (one call for many sectors), sector count;
    - microphone input: configure (rate, width, channels, map, clock window, block size, block count), start, stop, read one block with a time limit, free a block, apply the clock pins' sleep state, apply their default state;
    - power chip: set and read a rail (microphone, storage) with the caller's name, charger enable, charger current write, charge status and latched errors, one sample (mV, µA, temperature x10, die temperature x10), current limit status, reset causes read and clear, SHPHLD configuration and strobe, ship task, VBUS present, and a callback for VBUS in, VBUS out and charge error;
    - HFXO: request with a "running" callback, release, running;
    - motor pin: set high or low;
    - storage bus: suspend, resume;
    - USB transport: enable, disable, send bytes, a receive callback, an event callback (VBUS ready, VBUS removed, configured, unconfigured, suspended), bus speed;
    - image store: erase slot 1, write at an offset, request the test upgrade, image confirmed, confirm, reboot with a reason;
    - persistent settings: load and save the factory flag and the saved time;
    - retained memory: crash block read, write, clear; `gpregret1` read and write;
    - watchdog: start with a timeout, feed;
    - gauge: start, process one sample (mV, mA, °C, seconds) giving SoC x10, time to empty and time to full;
    - clock: ms now, cycles now, cycles per second, device id (64 bits);
    - beacon: start not-connectable advertising with a name, an interval and a power, stop.
  - `rhw_sim.h` (test builds only): one ordered event log of every simulated driver call (kind, arguments, time, caller), and the fault and value controls listed in section 5; `rhw_sim_reboot()`, which clears every unit's RAM state through their reset hooks and keeps the simulated card, the persistent settings and the retained memory.
- **Needs:** nothing. It may start at once.
- **Tests:** `tests/rhw`: suite `rhw_sim` proves each fault fires at the named call and only there (one case per fault of section 5), the event log keeps order and time, `rhw_sim_reboot()` keeps exactly the three kept stores.
- **Broken copies:** `disk_fault_late` (the write fault fires one call late) fails `rhw_sim.test_disk_write_fault_at_n`; `cut_keeps_tail` (a cut write keeps the sectors after the cut) fails `rhw_sim.test_disk_cut_after_sector`; `reboot_wipes_card` fails `rhw_sim.test_reboot_keeps_card_settings_retained`; `mic_no_block_ignored` fails `rhw_sim.test_mic_stop_delivering`.
- **Done when:** `UNIT PASS tests/rhw`; every header of this list exists and compiles alone in a test (one `#include` per test file of `tests/rhw/src/headers.c`); `docs/rhw-notes.md` lists each header function with the FW line it serves.

### U1 `core6`: the core's new row

- **Owns:** F/modules/ring_core/**, F/tests/core/**, a new section "Step 6" at the end of F/docs/core-notes.md.
- **Work:** apply decision D2 (row 12's actions "M1; open" under the reading used); regenerate the table from FW 1.2 with `tools/gen_table.py` (72 rows, FW l.206); add the row of FW l.148 as row 16 with its guard; renumber the actions of `state_actions.c` and the row tests of `test_rows.c` so that `count_rows.py` passes; refresh the table inside each of the 23 broken copies under `tests/core/broken/` so that each still fails its own case. The reading of D1 option A: a sign hook.
- **Offers** (in `rc_core.h`): `rc_core_set_sign_hook(core, fn, ctx)`. The core calls `fn(ctx, t)` once per long press, only in `STANDBY`, only when the open flag is clear, the battery is above B5 and free space is above SFULL, before it chooses the row. A return of 0 means "the sign is drawn": row 12 (open; M1). Any other value means "not drawn": row 16 (no recording, M3, event log record, VDD_MIC stays off). With no hook set the core takes the sign as drawn (the test applications of steps 2 to 5 have no recorder; decision D1).
- **Needs:** nothing from U0.
- **Tests:** `rc_rows.test_row_12`, `rc_rows.test_row_16`, `rc_rules.test_sign_hook_once_per_press`, `rc_rules.test_sign_hook_not_called_when_refused_otherwise` (open flag, B5, SFULL), plus every existing core test renumbered.
- **Broken copies:** `sign_ignored` (row 12 taken when the hook refuses) fails `rc_rows.test_row_16`; `sign_hook_twice` fails `rc_rules.test_sign_hook_once_per_press`; `sign_before_b5` (hook called at B5) fails `rc_rules.test_sign_hook_not_called_when_refused_otherwise`.
- **Done when:** `UNIT PASS tests/core`, `count_rows.py` prints 72 rows and 72 tests (decision D9 says where it runs), and the earlier suites that use the core (control, screens, relay and their Bluetooth tests) pass in the same targeted run: `bash tools/unit_run.sh tests/core tests/screens tests/control tests/relay`.

### U2 `store`: storage

- **Owns:** F/modules/ring_store/** except `include/`; F/tests/store/**; F/docs/store-notes.md.
- **Files:** `src/rst_fmt.c` (pure: encode and decode the chunk header, superblock, index record, event log record; CRC-32; digest), `src/rst_layout.c` (pure: LBAs, chunk count, free space, S30, SFULL, storage left), `src/rst_log.c` (pure: superblock choice at mount, recovery scan over a read callback, recording states from the index, tail move on delete, the event log buffer of 8 with its drop count), `src/rst.c` (thin: the storage thread, the rail sequence of FW 5.1, 3 init tries 200 ms apart, 3 write tries, the BUSY guard), `src/rst_hw_real.c` (real disk access and `spi00` suspend, development kit build only).
- **Offers** (`rst.h`, written by U0): mount (rail on, init, sector count, superblock, list of recordings rebuilt from the index; reports the open flag, the boot count and the space), unmount (deinit, suspend, rail off); open a recording (type, start time, time-set flag) giving its id and writing the superblock with the open flag; put a full chunk (queued; the 3 tries; a fault callback); close (partial chunk, CLOSE record with highlights and duration, superblock with the flag clear); recover (scan, CLOSE RECOVERED, head moved, flag cleared, progress callback); space (free chunks, S30, SFULL, minutes left); list recordings; read a chunk as stored; confirm with a digest; delete; put an event log record; read log records; the factory area test (FW 9.3 T-STORE); delete every type-2 recording; callbacks for S30 reached, SFULL reached, write fault, read error.
- **Needs:** U0 (`rrec_spec.h`, disk, power chip rail, storage bus, clock).
- **Tests:** suites `store_fmt`, `store_layout`, `store_log`, `store_index`, `store_space`, `store_recovery`, `store_delete`, `store_evlog` (pure), `store_svc` (thin part on the simulated card and power chip). Rows S2 to S29, C3, C8, C9, C16, C24, T26 of section 2.
- **Broken copies:** `hdr_crc_512` (header CRC over bytes 0 to 511) fails `store_fmt.test_chunk_header_bytes`; `digest_big_endian` fails `store_fmt.test_digest`; `sb_older_wins` fails `store_log.test_mount_picks_newer_valid_copy`; `lba_no_wrap` fails `store_layout.test_chunk_lba_wraps`; `scan_accepts_gap` (a skipped `chunk_seq` kept) fails `store_recovery.test_stop_on_each_mismatch`; `sfull_17` fails `store_space.test_s30_sfull_edges`; `delete_frees_middle` fails `store_delete.test_tail_moves_over_leading_only`; `delete_without_confirm` fails `store_delete.test_delete_needs_confirm`; `two_tries` fails `store_svc.test_three_tries_then_fault_open_flag_kept`; `init_before_rail` fails `store_svc.test_rail_sequence`; `log_drops_newest` fails `store_evlog.test_buffer_of_8_drops_oldest`.
- **Done when:** `UNIT PASS tests/store`; `docs/store-notes.md` maps rows S2 to S29 and T26 to their cases and log lines.

### U3 `audio`: microphones

- **Owns:** F/modules/ring_audio/** except `include/`; F/tests/audio/**; F/docs/audio-notes.md.
- **Files:** `src/rau_chunk.c` (pure: a block into the chunk, the 800-frame discard, zero fill and dropout count, flags, clipped samples, highlight frames, motor intervals with the 800-frame tail, split at chunk edges, merge of a fifth, timestamps and header fields), `src/rau.c` (thin: the audio thread, the ring of 3 chunks, the 100 ms no-block watch, HFXO request and release, the clock pins' sleep state at boot and after stop, hand-off of full chunks to the store), `src/rau_hw_real.c` (real PDM through the kit's microphone API, the clock pins' sleep state, HFXO request; development kit build only).
- **Offers** (`rau.h`): pins to sleep state at boot; start capture (recording id, boot count, time-set flag, `utc_ms`; the caller has already enabled VDD_MIC through `rec_mics_on()`); stop capture at a mark time (frames to the mark kept, the partial chunk handed over, PDM stopped, blocks released, clock pins to sleep state; returns when the caller may switch VDD_MIC off); highlight at a CENTRE_DOWN time; a MOTOR edge (high or low, cycle count); the B15 flag; callbacks: no block for 100 ms, chunk ready, dropout.
- **Needs:** U0 (microphone input, HFXO, clock, `rrec_spec.h`); U2's `rst.h` (header only, for the chunk hand-off).
- **Tests:** `audio_cfg`, `audio_chunk`, `audio_motor` (pure), `audio_svc` (thin part on the simulated input). Rows A1 to A18, S9 to S13, C13.
- **Broken copies:** `discard_0` fails `audio_chunk.test_discard_800_frames`; `dropout_skips` (a missing block shortens the recording) fails `audio_chunk.test_dropout_zero_fill`; `clip_high_only` fails `audio_chunk.test_flags_each_bit`; `highlight_release_time` fails `audio_chunk.test_highlight_frame_from_down_time`; `motor_no_tail` fails `audio_motor.test_interval_frames`; `no_split` fails `audio_motor.test_span_two_chunks`; `fifth_dropped` fails `audio_motor.test_fifth_merged_into_fourth`; `hfxo_after_trigger` fails `audio_svc.test_hfxo_before_trigger`; `no_block_150ms` fails `audio_svc.test_no_block_100ms_reports`; `ring_two` (a ring of 2 chunks) fails the build at the ring-size assertion (the named check is the assertion's message in the build log).
- **Done when:** `UNIT PASS tests/audio`; notes map A1 to A18.

### U4 `xfer`: USB transfer

- **Owns:** F/modules/ring_xfer/** except `include/`; F/tests/xfer/**; F/docs/xfer-notes.md.
- **Files:** `src/rxf_proto.c` (pure: header, CRC, status codes, opcode table, argument limits, response layouts, BUSY), `src/rxf_desc.c` (pure: the full-speed and high-speed descriptor tables), `src/rxf_class.c` (thin: the vendor class with `USBD_DEFINE_CLASS`, both configurations, endpoint choice by bus speed, the stack enabled on VBUS ready and disabled on VBUS removed, the transport to the protocol).
- **Offers** (`rxf.h`): the backend struct the join fills (get info, list, read chunks, confirm, delete, set time, get battery, firmware begin, data, end, get log, reboot, factory); handle one request and write the response; start with a backend and a "may answer" query (the state); VBUS present or not; callbacks configured and unconfigured or suspended.
- **Needs:** U0 (USB transport, `rrec_spec.h`); for suite `xfer_store` also U2's implementation (it runs the protocol against the real store on the simulated card).
- **Tests:** `xfer_proto` and `xfer_desc` (pure, fake backend), `xfer_svc` (thin part on the simulated transport), `xfer_store` (protocol plus store). Rows X2, X4 to X20, C18, C24, S26 to S29. `xfer_usb` only if decision D6 says so.
- **Broken copies:** `tag_not_echoed` fails `xfer_proto.test_tag_echoed`; `crc_on_empty` fails `xfer_proto.test_crc_zero_for_empty`; `bad_crc_payload` (an error response with a payload) fails `xfer_proto.test_bad_crc`; `list_max_65` fails `xfer_proto.test_list_args`; `range_257` fails `xfer_proto.test_read_range_args`; `no_busy` fails `xfer_proto.test_busy_while_running`; `factory_flag_ignored` fails `xfer_proto.test_factory_not_allowed`; `hs_packet_64` fails `xfer_desc.test_descriptor_bytes_fs_hs`; `usb_on_without_vbus` fails `xfer_svc.test_stack_follows_vbus`; `read_deleted` fails `xfer_store.test_read_range_deleted_not_found`.
- **Done when:** `UNIT PASS tests/xfer`; notes map X1 to X21.

### U5 `power`: power chip, battery, charger, ship mode

- **Owns:** F/modules/ring_power/** except `include/`; F/tests/power/**; F/docs/power-notes.md.
- **Files:** `src/rpw_logic.c` (pure: the levels from SoC and voltage, the mean of 10 in the recording states, the report on every change in both directions, "charge on" when off only, the `CHARGE_CURRENT` constant and its build assertions, the motor charge added to the measured current, the current-limit decision, the ship entry steps 2 to 5 as a step machine, the reset-cause decoding, the GET_BATTERY charge-state codes), `src/rpw.c` (thin: the sampling timer per state, the gauge, the power chip calls, the VBUS and charge-error callbacks), `src/rpw_hw_real.c` (load switches through the regulator API, the charger's sensor channels, the task registers, the kit's fuel gauge library; development kit build only).
- **Offers** (`rpw.h`): start with callbacks (level changed, VBUS in, VBUS out, charge error, current limit active); the core state now (sets the sample period); charge on, charge off; set a rail (microphone, storage) with the caller's name; add motor charge (mA.s, from the motor); ship mode (steps 2 to 5 of FW 8.4; step 1 is the join's); the GET_BATTERY values; read, log and clear the reset causes at boot; the battery percent (for U7's update rule).
- **Needs:** U0 (power chip, gauge, clock, `rrec_spec.h`).
- **Tests:** `power_levels`, `power_charger`, `power_gauge`, `power_sample`, `power_ship`, `power_reset`, `power_ilim`, `power_cfg`, `power_report`. Rows C2, C6, C22, P2, P3, P8, P9, P11 to P14, P17 to P19, X13.
- **Broken copies:** `voltage_ignored` fails `power_levels.test_voltage_edges`; `mean_of_5` fails `power_levels.test_mean_of_ten_in_recording`; `report_down_only` fails `power_levels.test_report_on_change_both_ways`; `charge_on_rewrites` fails `power_charger.test_charge_on_twice_writes_once`; `write_while_enabled` fails `power_charger.test_disable_write_enable_order`; `motor_charge_subtracted` fails `power_gauge.test_motor_charge_added`; `ship_no_strobe` fails `power_ship.test_entry_order_without_vbus`; `ship_no_wait` fails `power_ship.test_waits_for_vbus_removed`; `ilim_plays_m3` fails `power_ilim.test_first_active`; `causes_not_cleared` fails `power_reset.test_causes_logged_then_cleared`. Five build copies for P2 (`cc_unset`, `cc_17601`, `cc_3999`, `cc_100500`, `cc_15250`): each must fail the build with its own assertion message; `broken_run.sh` counts a copy only when the build log holds that message.
- **Done when:** `UNIT PASS tests/power`; notes map the rows above.

### U6 `motor`: motor patterns and soft start

- **Owns:** F/modules/ring_motor/** except `include/`; F/tests/motor/**; F/docs/motor-notes.md.
- **Files:** `src/rmo_logic.c` (pure: the pattern table, the replace rule, the Vibration filter, the edge schedule, the charge per pulse, the soft-start schedule), `src/rmo.c` (thin: the `k_timer` player, the pin through U0, the edge, charge and pattern-start callbacks), `src/rmo_hw_real.c` (the MOTOR GPIO; development kit build only). `Kconfig`: `RING_MOTOR_SOFT_START` (default n) and the step values of decision D3.
- **Offers** (`rmo.h`): play a pattern; the Vibration setting; playing or not; callbacks: MOTOR edge (high or low, cycle count, for U3), pulse charge (mA.s, for U5), pattern started (id, time, for the event log).
- **Needs:** U0 (motor pin, clock, `rrec_spec.h`).
- **Tests:** `motor_player`, `motor_charge`, `motor_soft` (the last in a second twister scenario with `CONFIG_RING_MOTOR_SOFT_START=y`). Rows C26, C28 to C33, C35, P7.
- **Broken copies:** `mh_cuts_m1` fails `motor_player.test_replace_rules`; `vibration_mutes_mw` fails `motor_player.test_vibration_off_keeps_the_others`; `m2_gap_100` fails `motor_player.test_every_pattern_pin_times`; `edge_late` fails `motor_player.test_edge_times_reported`; `allowance_5ms` fails `motor_charge.test_charge_per_pattern`; `soft_on_by_default` fails `motor_soft.test_off_by_default`; `soft_one_step_short` fails `motor_soft.test_soft_start_steps`.
- **Done when:** `UNIT PASS tests/motor`; notes map the rows.

### U7 `sys`: time saving, update, persistent settings, crash, watchdog

- **Owns:** F/modules/ring_sys/** except `include/`; F/tests/sys/**; F/docs/sys-notes.md.
- **Files:** `src/rsy_logic.c` (pure: image size and range checks, running CRC-32, the 30 s self-test step machine, the "update allowed" rule, the crash block format, the watchdog feed decision, the saved-time guess), `src/rsy.c` (thin: settings load and save, image writes, the feed thread, the fatal-error handler, the crash copy at boot), `src/rsy_hw_real.c` (image writing, MCUboot calls, settings, retained memory, `gpregret1`, `wdt31`; development kit build only).
- **Offers** (`rsy.h`): firmware begin (size, CRC), data (offset, bytes), end (status); self-test start and one call per item passed (storage, Bluetooth, USB); factory flag get, set, clear; save the time; restore the saved time as a guess; report progress of a thread (audio, storage); watchdog start; take the crash block at boot; the layout constants of FW 9.2.
- **Needs:** U0 (image store, persistent settings, retained memory, watchdog, clock); `ring_time` (existing, `rtime.h`) for the time.
- **Tests:** `sys_update`, `sys_time`, `sys_persist`, `sys_crash`, `sys_wdt`. Rows C23, T4 to T6, T8 to T11, T28, T29.
- **Broken copies:** `size_999425_ok` fails `sys_update.test_size_limit`; `end_off_by_one` fails `sys_update.test_data_end_limit`; `writes_slot0` fails `sys_update.test_writes_only_slot1`; `selftest_31s` fails `sys_update.test_self_test_timeout_reboots`; `allowed_at_30` fails `sys_update.test_allowed_rule`; `feed_without_progress` fails `sys_wdt.test_feed_only_with_progress`; `crash_copied_twice` fails `sys_crash.test_boot_copies_valid_block_once`; `guess_marked_set` fails `sys_time.test_guess_is_not_set`.
- **Done when:** `UNIT PASS tests/sys`; notes map the rows.

### U8 `factory`: factory sub-commands and the ship beacon

- **Owns:** F/modules/ring_factory/** except `include/`; F/tests/factory/**; F/tests/bsim/factory/** (only with decision D6); F/docs/factory-notes.md.
- **Files:** `src/rfa_logic.c` (pure: sub-command parsing, the flag rules, the result layout, RMS in dBFS and the longest run of equal samples, ppm, the T-CHARGE judgement, the T-MOTOR timing, the beacon name), `src/rfa.c` (thin: each test through the other units' headers, the joystick events reported in `FACTORY_TEST`, the beacon), `src/rfa_hw_real.c` (the advertising calls; development kit build only).
- **Offers** (`rfa.h`): run one FACTORY request (sub-command, arguments) giving a status and the response bytes; a joystick event in `FACTORY_TEST`; ship begin (start the beacon; keep or clear the flag) and beacon stop (called by U5's ship steps right before the ship task).
- **Needs:** U0; U2, U3, U5, U6, U7 implementations for `factory_store`, `factory_mic`, `factory_charge`, `factory_motor`, `factory_ship` (the pure suites need headers only); J's `rec_mics_on()` for T-MIC and T-SIGN (through `rrec.h`; until J lands, a test stand-in inside `tests/factory`).
- **Tests:** `factory_cmd`, `factory_mic`, `factory_input`, `factory_motor`, `factory_sign`, `factory_store`, `factory_radio`, `factory_charge`, `factory_xtal`, `factory_ship`, and `factory_screen` only with decision D7. Rows C20, T11 to T23.
- **Broken copies:** `flag_ignored` fails `factory_cmd.test_flag_rules`; `x11_accepted` fails `factory_cmd.test_0x11_bad_arg`; `run_999` (stuck at 999 equal samples) fails `factory_mic.test_rms_and_runs`; `mic_without_sign` fails `factory_mic.test_no_screen_no_mic`; `centre_records` fails `factory_input.test_centre_reported_never_records`; `vbat_read_at_0` fails `factory_motor.test_reads_and_timing`; `store_lba_4097` fails `factory_store.test_area_write_read`; `type2_left` fails `factory_store.test_test_recordings_deleted`; `beacon_connectable` fails `factory_ship.test_beacon_name`; `beacon_after_ship` fails `factory_ship.test_beacon_window`.
- **Done when:** `UNIT PASS tests/factory` (and `tests/bsim/factory/run.sh` with `--broken`, if D6); notes map T11 to T23.

### U9 `screens6`: two calls of the screens part (decision D7, reading used)

- **Owns:** F/modules/ring_screens/**; F/tests/screens/**; a new section "Step 6" at the end of F/docs/screens-notes.md.
- **Offers** (in `rscr.h`): "current limit active": the screen goes off for 10 s, except in `RECORDING`, where it shows SCR_REC_DIM for those 10 s and never goes dark (FW 8.7 l.992); "factory frame": full red, green, blue, white, black or the grid, drawn on SCR_FACTORY's display path (FW 9.3 l.1025), only in `FACTORY_TEST`.
- **Needs:** nothing new (the screens part and the core of step 4); U0 only for the shared constants.
- **Tests:** `screens_table.test_ilim_dim_never_dark_in_recording`, `screens_table.test_ilim_off_10s_outside_recording`, `screens_draw.test_factory_colours` (pixels read back from the memory display), `screens_draw.test_factory_frame_refused_outside_factory`. Rows P18 (screen part) and T14. Every existing screens case and picture stays as it is (the 21 pictures byte for byte, `step4-report.md`).
- **Broken copies:** `ilim_dark_in_recording` fails `screens_table.test_ilim_dim_never_dark_in_recording`; `factory_wrong_colour` (green drawn for red) fails `screens_draw.test_factory_colours`.
- **Done when:** `UNIT PASS tests/screens` with the existing `broken_run.sh` copies still failing their cases, and the picture manifest of the run equal to step 5's.

### J `recorder`: the join

- **Owns:** F/modules/ring_recorder/** except `include/`; F/modules/ring_glue/** (two additions); F/app/** (`src/main.c`, `CMakeLists.txt`, `prj.conf`, `boards/*.overlay`, `boards/*.conf`); F/tools/build_all.sh; F/tools/stack_report.py (the new threads); F/README.md; F/tests/recorder/**; F/docs/recorder-notes.md.
- **Files:** `src/rrec.c` (the action executor: every `rc_action` of the core carried out in order through U2 to U8), `src/rrec_mics.c` (`rec_mics_on()` and its off twin: the one path to VDD_MIC), `src/rrec_boot.c` (the boot sequence: reset causes, crash block, charge on with VBUS before mount, mount, the facts, "init done" or "storage init fails"), `src/rrec_bridge.c` (power, USB, store and audio callbacks into the glue as core events; the level into `rglue_battery()`; battery values into `rscr_set_battery()`), `src/rrec_backend.c` (fills U4's backend).
- **Glue additions:** `rglue_battery(level)` (takes the lock, calls `rc_core_battery()`, carries out the actions like `rglue_event()`); `rglue_ops.sign_start`, passed to the core's sign hook (U1).
- **Application:** the module list of `app/CMakeLists.txt` gains `ring_rhw ring_store ring_audio ring_xfer ring_power ring_motor ring_sys ring_factory ring_recorder`; `main.c` starts the core in `BOOT` (it starts in `STANDBY` now, line 111) and calls `rrec_init()`; the simulated-chip overlay gains the simulated card and microphone nodes; `prj.conf` sets `CONFIG_RING_RHW_SIM` per board (decision D11b). The start line of stage 2 stays; `main.c` adds the line `ring-os recorder: boot done, state STANDBY`.
- **Offers** (`rrec.h`): start; the glue's action hook; `rec_mics_on(t)` (screen sign through `rscr_sign_start()`, then VDD_MIC only on an answer of 0; returns the answer); `rec_mics_off()`; the sign hook for the core.
- **Needs:** every unit landed (U0 to U9).
- **Tests:** `recorder_rows` (every row of FW 1.2 from its From state, with the real core, glue, screens and every unit on the simulated drivers), `recorder_actions`, `recorder_boot`, `recorder_sign`, `recorder_sign1` (SIGN-1), `recorder_sequence`, `recorder_rails`, `recorder_rules`, `recorder_log`, `recorder_screens`. Rows C1, C4 to C27, C33, C36 to C39, A6, A10, A12, A13, P4, P6, P11, P12, T8, T9, T24, T27.
- **Broken copies:** `mic_before_sign` fails `recorder_sign.test_start_draws_sign_before_mic`; `mic_on_refused_sign` fails `recorder_sign.test_sign_refused_no_mic_m3_log`; `screen_leaves_before_mic_off` fails `recorder_sign.test_close_mic_off_before_screen_leaves`; `dim_dark` (SCR_REC_DIM blanked at the 10 s idle) fails `recorder_sign1.test_sign1_every_row`; `m2_before_mic_off` fails `recorder_actions.test_stop_m2_after_mic_off`; `sd_off_before_mic_off` fails `recorder_actions.test_close_order`; `charge_after_mount` fails `recorder_boot.test_vbus_boot_charges_before_mount`; `retry_not_reported` fails `recorder_actions.test_retry_storage_reports_result`; `mic_in_factory_idle` fails `recorder_rows.test_mic_rail_only_in_recording`; `usb_long_press` (a USB request reaches the glue as a long press) fails `recorder_rules.test_no_command_starts_or_stops`; `no_log_on_state_change` fails `recorder_log.test_each_kind_logged`; `sd_on_in_standby` fails `recorder_rails.test_rails_per_state`.
- **Done when:** `UNIT PASS tests/recorder`; then the full run of section 6 by the lead ends with `RESULT PASS`.

## 4. Order and what runs at the same time

The PRD allows at most three helpers at a time on the server ("At most three helpers at a time on the server", `firmware/docs/PRD.md` line 53).

| Wave | Units at the same time | Starts when | Why this order |
|---|---|---|---|
| 0 | U0 `rhw` (root) and U1 `core6` | at once | U0 holds every shared header, the constants and the simulated drivers; every other unit compiles against them. U1 touches only the core and needs nothing from U0 |
| 1 | U2 `store`, U3 `audio`, U5 `power` | U0's done line read by the lead | the three largest parts; U3 needs U2's header only, which U0 wrote |
| 2 | U4 `xfer`, U6 `motor`, U7 `sys` | a wave 1 slot frees (a unit starts as soon as one of three slots is free, not when the whole wave ends) | U4's suite `xfer_store` needs U2's code, so U4 starts after U2 lands; U6 and U7 need U0 only and may take an earlier free slot |
| 3 | U8 `factory`, U9 `screens6` | U8: U2, U3, U5, U6, U7 landed; U9: U0 landed (it may take any earlier free slot) | U8's thin tests run the other units' code; U9 touches only the screens part |
| 4 | J `recorder` | U1 to U9 landed | the only unit that edits `app/`, `ring_glue`, `tools/build_all.sh` and `README.md` |
| 5 | the lead's full run | J's done line | section 6 |
| 6 | a separate review helper | the full run passed | owner: "a separate helper reads each step's code and tests against the specification before I call the step done". The reviewer gets this plan's rule table (section 2) and the code, reads each row against its test and its code, and reruns no full run. A fix round follows; the lead reruns the full run after it |
| 7 | report to the owner | the lead's last full run passed | owner: "After each step I show you the result and the usage it cost before I start the next one." The report follows the shape of `step5-report.md` (what exists, what is proven, decisions, deviations, not proven, usage) |

- Each unit proves itself with its targeted run (`tools/unit_run.sh`, one test folder, two targets, its broken copies). The full run (60 to 90 minutes on the loaded server, lead's brief) is run once by J's builder at the end of wave 4 and then by the lead.
- A unit lands when the lead has read its done line and committed its files. A later unit builds against the committed tree.
- A unit never edits another unit's files to make its own run pass; it reports the fault to the lead.

## 5. Simulated drivers

All are written for this project by U0, in `modules/ring_rhw/src/sim_*.c`. They contain no code of the kit. They run on `native_sim` and on `nrf54lm20bsim/nrf54lm20a/cpuapp`. Each writes every call into the one ordered event log of `rhw_sim.h` (kind, arguments, time, caller), so a test reads order and time from one place.

| Driver | What it does | Faults and values a test can set | What it cannot show |
|---|---|---|---|
| card (`ring,sim-disk`) | sectors of 512 bytes in a sparse store (unwritten sectors read as zero), so a test can use the real sector count of a 4 GB card or a small card that wraps fast; init and deinit; one write call for many sectors | sector count; init fails n times; write fails at call n (k times); read error at an LBA; cut after sector k of a multi-sector write (the rest of that write and every later write are lost); a stall of t ms per write; refuses and counts any call while the simulated VDD_SD is off | SPI timing, CMD25 on the wire, CRC-16, start-up charge and time (bench S1), speeds (S2), wear, what the card's controller does to other sectors on a cut, the real usable size |
| microphone input (`ring,sim-mic`) | the kit's microphone interface shape: configure, start, stop, read with a time limit, free; a block of 1,024 bytes every 16 ms of simulated time; records the configuration it received | source: frame counter (left) and its inverse (right), a sine of a set level in dBFS, one channel stuck at a value, clipped samples at -32768 and 32767; stop delivering after block n; drop block n; a read error | the PDM clock pick of the kit's driver, which microphone lands in which channel, the microphone's power-up, its levels, the clock pin level after a stop (FW 10.5 item 9) |
| power chip | two rails (microphone, storage) with the caller's name; charger enable and current register writes in order; charge status and latched errors; samples from a script (mV, µA, temperature) or from a simple cell (capacity, current per rail); current-limit bit; reset causes; SHPHLD configuration and strobe; ship task (after it, every later call of the units is refused and counted, standing for "no supply"); VBUS events | VBUS in and out at a time; a charge error; the current-limit bit at a sample; any reset cause bits; a voltage dip during MOTOR high (for T-MOTOR); the gauge's SoC | the register map and the devicetree names (TO CONFIRM, FW 10.5 item 3), real charging, the thermistor, ship-mode current, the real dip |
| gauge | SoC from a counted charge and the start value; time to empty and to full from the current | start SoC; a set error | the kit's fuel gauge library and its battery model (FW 10.5 items 4, 26) |
| HFXO | request with a "running" callback after a set delay; release; counts | the delay; never running | the crystal |
| motor pin | records each high and low with its time | none | the motor's spin, the felt pulse (F1), the start current, the cell dip, whether a soft start lowers it |
| storage bus | suspend and resume, recorded | none | pin levels in the sleep state (FW 10.5 item 22) |
| USB transport | a byte pipe between a test (the "case") and the class: requests in, responses out in packets of the bus speed's size; VBUS ready, removed, configured, unconfigured, suspended events | bus speed full or high; a host that stops reading | the USB controller, the PHY, full-speed fallback (FW 10.5 item 19), the real rate (1.216 MB/s is a USB figure not read, FW 10.5 item 20) |
| image store | slot 1 of 976 KB in RAM; erase and write with their ranges recorded; "request test upgrade", "confirmed", "confirm", "reboot" recorded | a write error; the image already confirmed or not | MCUboot, the swap, the signature check, the rollback, the RRAM, the chip's write protection |
| persistent settings | the factory flag and the saved time in a store that survives `rhw_sim_reboot()` | start values | RRAM and the settings back end of the kit |
| retained memory | a crash block and `gpregret1` that survive `rhw_sim_reboot()` | a valid or a corrupt block | survival across a real reset; the real fatal-error path |
| watchdog | start and feed recorded; a "would reset" flag when 8 s pass without a feed | none | the reset |
| clock | ms and cycles from the simulated time; a fixed device id | the cycle rate | the GRTC and the crystal accuracy |
| beacon | start and stop recorded with name, interval, power, connectable flag | none | the radio; over BabbleSim only if decision D6 says so |

The real screens part (step 4, its memory display) is used as it is: `rscr_sign_start()` draws on the memory display. SIGN-1 reads the display's blanking and frames from step 4's test hooks (`rscr_snapshot()`, `rscr_capture_rgb()`, `rscr_test_force_down()` in `rscr.h`). The memory display has no OLED_PWR_EN, so that part of SIGN-1 stays unproven.

## 6. Full run

What step 6 adds to `tools/build_all.sh` (J writes it; the comment block at the top lists each new stage):

1. **Nothing for the new suites and broken copies.** Stage 3 finds every `testcase.yaml` under `firmware/tests`, stage 5 every `tests/<name>/broken_run.sh` (`build_all.sh` lines 119 and 326): `tests/rhw`, `core`, `store`, `audio`, `xfer`, `power`, `motor`, `sys`, `factory`, `recorder` join by their files. With decision D6, `tests/bsim/factory/run.sh` joins stage 4 the same way.
2. **Stage 2 (bsim-run)** also checks the line `ring-os recorder: boot done, state STANDBY` within the 2 simulated seconds: the product application boots through the recorder on the simulated drivers.
3. **New stage `recorder-one-mic-path`:** only `rec_mics_on()` in `modules/ring_recorder/src/rrec_mics.c` switches the microphone rail on (a search of every new module's sources for the rail call with "on"); a copy with a second such call in another file must be found by the same search (self test, as `relay-no-core`, lines 302 to 322).
4. **New stage `recorder-no-start-path`:** the sources of `ring_store`, `ring_audio`, `ring_xfer`, `ring_power`, `ring_motor`, `ring_sys` and `ring_factory` never name `rglue_input`, `rc_core_input` or `RC_EV_LONG_PRESS`; a planted copy is found (self test).
5. **New stage `recorder-no-raw-pins`:** no source or overlay of step 6 names a chip pin by number (patterns such as `P1.24`, `NRF_GPIO_PIN_MAP`, `<&gpio1 24`); a planted copy is found (self test).
6. **New stage `recorder-product-drivers`:** the development kit build's `.config` has `CONFIG_RING_RHW_SIM` off and the simulated-chip product build has it on; the test hooks of `rhw_sim.h` are off in the kit build; a planted kit `.config` with the option on is refused (self test, as `hook_guard`, lines 195 to 202).
7. **Stage `stack-report`:** the new threads (audio, storage, USB, power sampling, motor timer) are added to `tools/stack_report.py`.
8. **Stage `link-settings`:** unchanged, unless U8's beacon needs a Bluetooth setting the product does not have; then J adds that setting to the product and the stage shows the test rings still equal the product (decision D6).

The last line stays `RESULT PASS` or `RESULT FAIL <stages>`. The lead's proof is that log's last line, quoted, and the stage count with every exit 0.

## 7. Not provable without hardware

What stays unproven after step 6 (the "NP" rows of section 2, grouped):

1. **Every real driver call.** The real files (`*_hw_real.c`) compile in the development kit build at most (decision D15) and never run: PDM, SD card over SPI, USB controller, the nPM1304 registers and devicetree names, the fuel gauge library, HFXO, the MOTOR GPIO, image writing, MCUboot, settings in RRAM, retained memory, `gpregret1`, `wdt31`, advertising power.
2. **Microphones:** the 1.280 MHz pick of the kit's driver, which microphone lands in which channel, levels, power-up, the clock pin level after a stop, the current at 1.280 MHz (FW 10.5 items 5, 6, 9).
3. **Storage:** card timing, one CMD25 per chunk, speeds, start-up charge (bench S1), wear, power-loss damage by the card's controller, the usable size (FW 10.5 items 10 to 12, 25).
4. **USB:** enumeration at full speed with the case's host, the rate, D+ and D- levels without VBUS (FW 10.5 items 19, 20, 29). The descriptors are served to a host only if decision D6 (a) holds.
5. **Power:** charging, termination, thermistor and die-temperature limits, ship-mode current, the wake by VBUS, the battery model, the SoC accuracy with the motor charge, the current limit's real trip, every current of FW 8.5 and R19 (bench T2), the pads on the skin (FW 8.6).
6. **Motor:** the felt pulse (F1), the start current and start time (B-M3), the cell dip (B-M5, T-MOTOR's 20 mV line), whether the soft start lowers the dip at all (decision D3).
7. **Screen:** the panel, OLED_PWR_EN, the power sequence (FW 3.3), the cost of the always-lit sign (FW 3.2, l.345). SIGN-1 runs on the memory display.
8. **Update:** the swap, the signature check, the rollback of an image that is not confirmed, the write protection of the MCUboot area (FW 10.5 items 2, 33).
9. **Crash and watchdog:** a real fault reaching the handler, retained RAM across a real reset, the watchdog reset.
10. **Factory:** every judgement of the jig (camera, speaker, accelerometer, RSSI), T-XTAL's measurement, the factory flow by assembly step (the jig of W13 is not built).
11. **Time:** the crystal's accuracy (FW 9.1).
12. **Stack and RAM:** stack peaks on the real chip; the RAM budget lines of FW 4.6 beyond the kit build's memory report.

## 8. Kit facts to verify first

Facts this plan assumes about nRF Connect SDK 3.4.2 (Zephyr 4.4.2 inside it, `firmware/docs/infra-notes.md`, "Versions and tags") that no file of this project and no page read here confirms. The first builder of the unit named verifies each in its first hour and writes the answer, with the file and line, into its notes. Route: read the file in the server's workspace through the project's remote command, for example `sh firmware/tools/remote.sh k-<id> "grep -n '<name>' /ws/zephyr/<path>"`, or the public documentation pages of Zephyr and Nordic. A fact found false goes to the lead before any work that rests on it.

| Id | Fact assumed [to verify] | Unit | How to verify |
|---|---|---|---|
| K1 | The microphone API has `dmic_configure()`, `dmic_trigger()` with `DMIC_TRIGGER_START` and `DMIC_TRIGGER_STOP`, `dmic_read()` with a timeout, `struct dmic_cfg` and `dmic_build_channel_map()`; a driver outside the kit can offer this API on a devicetree node of its own (for the real wrapper only; the simulated input sits behind U0's interface) | U3 | `/ws/zephyr/include/zephyr/audio/dmic.h` |
| K2 | The disk access API has `disk_access_read()`, `disk_access_write()`, `disk_access_ioctl()` with `DISK_IOCTL_CTRL_INIT`, `DISK_IOCTL_CTRL_DEINIT` and `DISK_IOCTL_GET_SECTOR_COUNT` (FW 10.5 item 18 lists them as not opened) | U2 | `/ws/zephyr/include/zephyr/storage/disk_access.h`, `/ws/zephyr/include/zephyr/drivers/disk.h` |
| K3 | `native_sim` has a virtual USB device controller and a virtual host that can run in one test image (decision D6 a) | U4 | `/ws/zephyr/boards/native/native_sim/native_sim.dts`, `/ws/zephyr/dts/bindings/usb/` (a `udc-virtual` and a `uhc-virtual` binding), `/ws/zephyr/tests/subsys/usb/device_next/` |
| K4 | The device stack names of FW 6.1: `USBD_DEFINE_CLASS`, `usbd_add_configuration()` with a speed argument, `usbd_bus_speed()`, the messages for VBUS ready, VBUS removed, configuration and suspend, and `subsys/usb/device_next/class/loopback.c` as the model | U4 | `/ws/zephyr/include/zephyr/usb/usbd.h`, `usbd_msg.h`, `/ws/zephyr/subsys/usb/device_next/class/` |
| K5 | The nPM13xx drivers serve the nPM1304: its compatibles, the load-switch soft-start and active-discharge property names, the charger's sensor channels, the call that writes a task register (FW 10.5 item 3); whether the kit has an emulator of the chip | U5 | `/ws/zephyr/dts/bindings/` (files with `npm1304` or `npm13xx` in the name), `/ws/zephyr/drivers/mfd/`, `/ws/zephyr/drivers/regulator/regulator_npm13xx.c`, `/ws/zephyr/drivers/sensor/nordic/npm13xx_charger/` |
| K6 | The fuel gauge library: its 3.4.2 function names and arguments; the sign of a discharge current (FW 10.5 item 32); whether a build for the host architecture exists (if not, `native_sim` and the simulated chip use the simulated gauge only, which this plan already assumes) | U5 | `/ws/nrfxlib/nrf_fuel_gauge/include/nrf_fuel_gauge.h`, `/ws/nrfxlib/nrf_fuel_gauge/lib/` (the folders per architecture) |
| K7 | The call that requests HFXO on the nRF54L series and tells when it runs (FW 4.2 says "the nRF clock control on-off service") | U3 | `/ws/zephyr/include/zephyr/drivers/clock_control/nrf_clock_control.h` |
| K8 | The clock pins of `pdm20` and the pins of `spi00` can be put in their sleep state from the application without changing the kit's driver (pin control "apply state", or the device power-management suspend); FW 10.2 W3 calls it a driver change (decision D11c) | U3, U2 | `/ws/zephyr/include/zephyr/drivers/pinctrl.h`, `/ws/zephyr/include/zephyr/pm/device.h`, `/ws/zephyr/drivers/audio/dmic_nrfx_pdm.c` (whether it handles a suspend action) |
| K9 | The image API names: `boot_request_upgrade()`, `boot_is_img_confirmed()`, `boot_write_img_confirmed()`, the flash image writer's calls | U7 | `/ws/zephyr/include/zephyr/dfu/mcuboot.h`, `/ws/zephyr/include/zephyr/dfu/flash_img.h` |
| K10 | The settings back end on the nRF54L RRAM in the kit (which one, which partition name) | U7 | the kit's documentation pages on settings for the nRF54L series; `/ws/zephyr/subsys/settings/Kconfig` |
| K11 | `k_sys_fatal_error_handler()` can be replaced by the application, with its 4.4.2 signature; the retained memory driver's compatible `zephyr,retained-ram` (FW 10.5 item 18) | U7 | `/ws/zephyr/include/zephyr/fatal.h`, `/ws/zephyr/dts/bindings/retained_mem/` |
| K12 | `crc32_ieee()` is CRC-32/ISO-HDLC (FW l.70) | U2 | `/ws/zephyr/include/zephyr/sys/crc.h`; the test `store_fmt.test_crc_check_value` settles it |
| K13 | Not-connectable advertising with a set interval and 0 dBm, started while the devices part may advertise; whether a second advertising set (extended advertising) is needed | U8 | `/ws/zephyr/include/zephyr/bluetooth/bluetooth.h`, the controller's Kconfig for the TX power, `firmware/modules/ring_devices/src/rdev.c` (how it advertises now) |
| K14 | `sys_clock_hw_cycles_per_sec()` and `k_cycle_get_32()` work on `nrf54lm20bsim/nrf54lm20a/cpuapp` (FW 10.5 item 16) | U0 | a case in `tests/rhw` that prints both on the simulated chip |
| K15 | The simulated chip target gives a test enough RAM for the sparse card store and 3 chunks of 33,280 bytes (`research-sdk.md` line 114 states "unlimited RAM" for the nRF54L15 simulated target only) | U0 | `/ws/zephyr/boards/native/nrf_bsim/doc/nrf54lm20bsim.rst`; the first run of `tests/rhw` on that target |
| K16 | Twister accepts two scenarios of one test folder with different `extra_configs` (for U6's soft start on and off), and one suite on two targets runs in minutes on the loaded server | U0 | `/ws/zephyr/doc/develop/test/twister.rst`; the time of the first `unit_run.sh` |

## 9. Decisions for the lead

Each item: the options, the reading this plan uses (marked "used"), and why. None is settled silently; the builders use the marked reading until the lead rules.

- **D1. How the core learns that the sign was not drawn (FW l.148).** (A, used) a sign hook in the core (U1): called before the core chooses the row of a long press in `STANDBY`, only when the other guards of row 12 hold; 0 takes row 12, anything else row 16. Nothing is opened before the sign is up, so a refusal leaves no empty recording. With no hook set the core takes the sign as drawn, because the test applications of steps 2 to 5 have no recorder; the product always sets it (`recorder_sign` checks it). (B) open first, then a new event "sign failed" from `RECORDING` back to `STANDBY` with a close: the table gains a row the specification does not have, and an empty recording gets a CLOSE record. (C) refuse inside the recorder only, without a row: the core would sit in `RECORDING` with no microphones, against FW l.148.
- **D2. When M1 starts.** FW l.144 lists the actions "open; M1"; FW 4.4 l.447 says "M1 runs at once; the microphones start" and "The press and M1 fall before or inside the discarded 50 ms". The open (storage on, mount, superblock) takes card time that no file states, so M1 after it may fall into kept audio. (a, used) row 12's actions in the order "M1; open" (U1), citing l.447, and the lead writes it into FW; (b) keep "open; M1": M1 lands later and is marked like any pulse (FW 4.7), which costs audio but no rule.
- **D3. The motor soft start.** (a, used) build it, off by default (`RING_MOTOR_SOFT_START=n`), with a schedule of 3 enable steps of 2 ms high and 2 ms low before the steady high, counted inside the pattern's own on time so pattern totals do not change, each step counted as a start for the gauge (the values are this plan's [CHOICE]; bench B-M5 sets real ones); (b) do not build it until a cell is measured above 1.9 ohm; (c) build it on. Conflict to rule: FW 3.1 l.314 says a pulse train "would restart its own drive chip at each on time", so stepping the enable line may not lower the start current at all; and C84 at 4.7 uF already removes the dip in the simulation (`lead-decisions.md` l.29). Whether the soft start stays in the design is the lead's call.
- **D4. A ninth highlight inside one chunk.** The header holds 0 to 8 (FW l.576). (used) the ninth and later are not in that chunk's header, `highlight_count` of the chunk stays 8, and the CLOSE record keeps the first 32 of the recording with the full count; (other) move the extra ones to the next chunk's header, which gives them a wrong frame offset.
- **D5. LIST_RECORDINGS "first u32 (0 = oldest not deleted)".** (used) a `recording_id`: the list starts at that id, 0 at the oldest not deleted; (other) an index into the list.
- **D6. Two extra simulation proofs.** (a) the vendor class against `native_sim`'s virtual USB host, if K3 holds: proves the stack serves the full-speed descriptors and the bulk transfers; (b, used) a BabbleSim test `tests/bsim/factory`: a stand-in scanner sees the ship beacon while the simulated VBUS is on, sees it stop within 1 s of VBUS removal and none for 60 s, and sees T-RADIO's advertising. (a) is used only if K3 holds in U4's first hour; both add minutes to the full run.
- **D7. Calls the screens part does not have.** Step 6 needs: the 10 s dim or off on the current limit (P18), T-SCREEN's colour frames (T14), and, for FW 3.3, the fields of SCR_TRANSFER, SCR_RECOVERY, SCR_RECORDINGS and SCR_RECORDING_INFO (C40). (a) none now: P18's screen part, T14 and C40 stay not built and listed; (b, used) a small unit U9 `screens6` in wave 3: owns F/modules/ring_screens/** and F/tests/screens/**, adds a call "current limit: dim or off for 10 s" (SCR_REC_DIM in `RECORDING`, never dark) and a call "factory frame: colour or grid", with tests `screens_table.test_ilim_dim_never_dark_in_recording`, `screens_draw.test_factory_colours`, and broken copies `ilim_dark_in_recording` and `factory_wrong_colour`; C40's fields stay for a later step (they need new pictures the owner judges); (c) all of it in step 6, with new pictures for the owner.
- **D8. "A recording started then carries the flag" (zone unknown, FW l.1004).** No header field holds it (FW 5.3). (used) an event log record at the start of a recording when the zone is unknown, no header change; (other) use the reserved flag bit 2 (FW l.547 says "reserved (0)"), a format change the lead writes into FW.
- **D9. Where the core's generator runs.** It reads `design/firmware.md`, which the server does not receive (section 1.2 item 8). (used) U1's builder runs `tools/gen_table.py` and `tests/core/count_rows.py` with Python on the Mac (a code generator and a count, no build or test of the firmware) and quotes their output; (other) `tools/remote.sh` also copies `design/firmware.md`, a change to an infrastructure file.
- **D10. The lane file.** The lead replaces the step 6 lane `os-recorder` of `firmware/docs/lane-dag.json` by the units of section 3, with their owns and `depends_on` as in section 4.
- **D11. Small readings.** (a, used) a pure part may call `crc32_ieee()`: a library function, not a kernel call. (b, used) `CONFIG_RING_RHW_SIM` is on for `native_sim` and the simulated chip, off for the development kit. (c, used) the clock pins' sleep state (FW 4.5, W3) is applied from the recorder's thin part without changing the kit's driver (K8); if K8 shows that is impossible, the rule stays unproven and a patch to the kit's driver is the lead's call, because the public copy carries no code copied from the kit.
- **D12. The status of FW_BEGIN when the update is not allowed** (battery at or under 30 % without VBUS, FW l.1015; FW 6 names no code for it). (used) NOT_ALLOWED (11); (other) FW_ERROR (10).
- **D13. Event log codes.** FW 9.4 names the record but no code list. (used) U0 writes the list into `rrec_spec.h` (state change, fault, battery threshold, transfer command per opcode, motor pattern start, current limit, reset cause, crash, dropout, recovery, sign refused, ship retry, zone unknown at start), and the lead copies it into FW.
- **D14. When `boot_count` grows.** FW l.641 writes the superblock twice per recording; the chunk header and GET_INFO carry `boot_count`. (used) the store increments it at each mount in `BOOT` and writes the superblock once per boot; (other) increment in RAM and write at the next open, which loses boots without a recording.
- **D15. The development kit build and the real files.** (a, used) the real files compile in the kit build, each only when its devicetree node exists in the kit build, otherwise a stub that returns -ENODEV, and stage `recorder-product-drivers` prints which compiled; the full compile comes with the ring's board in step 7; (b) no real file until step 7.
- **D16. More than 256 recordings.** The list cache holds 256 entries (FW 4.6 l.485). (used) the cache keeps the 256 newest; LIST and READ_RANGE of older ones read the index on demand; (other) refuse a new recording beyond 256, which no rule states.
- **D17. The index ring wraps after 65,536 records** (FW l.612); FW states no rule for records still needed when it wraps. (used) not built in step 6 (at least 21,845 recordings away at three records each [CALC: 65,536 / 3]); listed for the lead to rule into FW.
- **D18. The saved time "as a guess" (FW l.1005).** The same line marks the time "not set", writes `utc_ms` 0 and shows "--:--". (used) the guess is written once into the event log at boot and used nowhere else; the clock stays not set until SET_TIME.

## questions_for_owner

none

## Lead's rulings on section 9 (2026-11-13 04:09)

The lead read sections 1, 2.1, 2.2 and 3 to 9 in full and counted the rows of 2.3 to 2.6 (30, 22, 20 and 29 rows). The builders follow these rulings; where a ruling differs from the reading "used" above, the ruling wins.

| Decision | Ruling |
|---|---|
| D1 | A: the sign hook in the core. |
| D2 | (a): row 12 reads "M1; open". Written into design/firmware.md line 144 as ruling R21. |
| D3 | (b): the motor soft start is NOT built in step 6. Reason: the MOTOR pin drives the enable pin of the motor's regulator (design/firmware.md line 314), and the dip the simulation found comes from charging that regulator's output capacitor; switching the enable line in steps would charge it several times. The circuit simulation first tests a stepped enable; the rule C35 and the suite motor_soft are dropped from unit U6. The rule C28 (one high per on segment, no PWM) stays. |
| D4 | as used (a ninth highlight in one chunk stays out of that chunk's header). |
| D5 | as used (a recording id). |
| D6 | (b) yes: the two-device test of the ship beacon. (a) only if kit fact K3 holds in U4's first hour. |
| D7 | (b): the small unit U9. The fields of SCR_TRANSFER, SCR_RECOVERY, SCR_RECORDINGS and SCR_RECORDING_INFO stay not built in step 6 and are listed in the step report. |
| D8 | as used (an event log record, no format change). |
| D9 | as used (the generator and the row count run with Python on the Mac). |
| D10 | done: firmware/docs/lane-dag.json holds the 11 units. |
| D11 | a, b and c as used. |
| D12 | as used: NOT_ALLOWED (11). |
| D13 | as used: U0 writes the event code list; the lead copies it into the specification after U0 lands. |
| D14 | as used: the count grows at each mount in BOOT. |
| D15 | (a): the real files compile in the development kit build where their devicetree node exists. |
| D16 | as used. |
| D17 | not built; listed in the step report. |
| D18 | as used. |

Models and order: U0 on Opus (every other unit compiles against its headers), the other units on Sonnet; at most three builders at a time on the server; the review after the build on Opus.

## Lead's rulings on the root unit's readings (2026-11-13 04:49)

Unit U0 is landed (firmware/docs/rhw-notes.md; its run ends UNIT PASS tests/rhw). Its public headers are frozen: a unit that needs a change asks the lead. Rulings on section 3 of its notes:

| Reading | Ruling |
|---|---|
| 1. FACTORY_EXIT has no number in the specification | 0x02, as in rrec_spec.h; the lead writes it into the specification. |
| 2. Order of "close" | the order of the specification's line 125 holds; the join uses rau_cut, rst_close, rau_halt, rec_mics_off, rau_release, rst_unmount. |
| 3. READ_RANGE and its CRC | as written in rxf.h (the unit reads the chunks twice or keeps them). |
| 4. No rail call in the power unit | accepted: VDD_SD only by the store, VDD_MIC only by rec_mics_on. |
| 8. Sampling "in the recording states" | RECORDING, and FACTORY_TEST while a test recording runs. |
| 9. Watchdog outside a recording | fed when both threads reported in the last 2 s, or when no recording runs. |
| 10. LIST state of a recovered recording | as in rst.h: RECOVERED until a CONFIRM, then TRANSFERRED. |
| 12. Event log codes | the list in rrec_spec.h is the list; the lead copies it into the specification. |

Every unit builder reads firmware/docs/rhw-notes.md sections 2 and 3 and its own public header before it writes a line.

## Lead's ruling R24 on the microphone unit's finding F1 (2026-11-13 05:30)

A highlight fires 440 to 850 ms after its CENTRE_DOWN, and a chunk is 512 ms, so the chunk that holds the press has usually gone to the store. Ruling R24 (written into design/firmware.md lines 564 and 566): a highlight marker in a chunk header is the FRAME NUMBER of CENTRE_DOWN counted from the first kept frame of the recording, and it is written in the header of the chunk being filled when the highlight fires. No marker is lost to timing; the ninth marker in one chunk stays out of that header (D4); the CLOSE record keeps its list in ms as before. Chunks are still handed to the store when full (line 443) and the loss bound of line 644 is unchanged. Units touched: U3 (the header values and their tests). The store encodes the field as it is given; the transfer sends chunks as stored.

## Lead's rulings on the storage unit's notes

- A card with no valid superblock copy gets a new log at the first mount: accepted as built. It is not a question for the owner: the storage is a chip soldered on the ring's board, so a "card from another use" cannot occur; a new chip from the factory has no superblock. A card that cannot be read is never formatted. The case "both superblock copies damaged in use" starts a new log and loses the list of recordings; it goes into the step report as a known limit.
- The pure files may call `crc32_ieee_update` as well as `crc32_ieee` (decision D11a covers both: library functions, not kernel calls).
- The superblock is also written at CONFIRM, DELETE and the end of a recovery: accepted.
- The return codes of section 5 of firmware/docs/store-notes.md are now comments at the end of rst.h (no signature changed).

RESULT: done, the plan cuts step 6 into eleven units (one root, nine parallel parts, one join) with a rule table for FW sections 1 to 6, 8 and 9, the simulated drivers, the full-run stages, the unproven list, 16 kit facts to verify and 18 decisions for the lead.
