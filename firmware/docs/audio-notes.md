# audio notes: unit U3 of software step 6 (the microphones)

Builder: U3 helper. Started 2026-11-13 04:50 CET (`date`). Version read: commit 2d3d5c2 of ROOT (branch master). No git was run.
Contract: `firmware/docs/step6-plan.md` (parts named in the brief, both ruling sections included), `firmware/docs/rhw-notes.md`
sections 2 and 3, the frozen headers `rau.h`, `rst.h`, `rrec_spec.h`, `rhw.h`, `rhw_sim.h`. "FW l.N" = line N of `design/firmware.md`.
Raw evidence: `firmware/build-logs/step6/u3-*`. The cited run is `u3-run2-final.log` (copy of `build-logs/20261113-053138-u-audio.log`, run after ruling R24; the earlier `u3-run1-final.log` is the run before it);
its result line, quoted: `UNIT PASS tests/audio` (the log then ends with the three footer lines `# finished (Mac clock): 2026-11-13 05:42:07 CET`,
`# remote exit code: 0`, `# local log: ...`). Exit code file: `u3-run2.exit` holds `0`.

## 1. What exists

| Path (under `firmware/`) | What |
|---|---|
| `modules/ring_audio/zephyr/module.yml`, `Kconfig`, `CMakeLists.txt` | the module: `CONFIG_RING_AUDIO_LOGIC` (pure), `CONFIG_RING_AUDIO` (thin; selects the pure part; depends on `RING_RHW`); `rau_hw_real.c` compiles only when the simulated drivers are off |
| `modules/ring_audio/src/rau_chunk.h`, `rau_chunk.c` | pure part (stdint, stdbool, string, errno constants; no kernel call, search `u3-rule-searches.log` 1b: 0 hits): 800-frame discard, block into chunk, zero fill, flags, clipped samples, highlights, motor intervals, timestamps, header fields |
| `modules/ring_audio/src/rau.c` | thin part: audio thread, ring of 3 chunks, 100 ms watch, HFXO, clock-pin sleep state, hand-off to the store, cut/halt; hardware only through `rhw_mic()`, `rhw_hfxo()`, `rhw_clock()` (search 2: no kit driver name) |
| `modules/ring_audio/src/rau_hw_real.c` | real PDM (kit's microphone API), pinctrl sleep state, HFXO through the on-off service; compiles only with `pdm20` enabled; NOT PROVEN (section 6) |
| `tests/audio/` | suites `audio_cfg` (4 cases), `audio_chunk` (15), `audio_motor` (6), `audio_svc` (21) = 46 cases; `src/common.[ch]` (stand-in for the store's hand-off: `rst_put_chunk` and `cb.put` both land in it; the store's code is never linked); `broken_edit.py`, `broken_run.sh`; `boards/native_sim.conf` (ticks of 0.1 ms, as in tests/rhw) |
| `docs/audio-notes.md` | this file |

Design in short (the header `rau.h` is unchanged): `rau_start` configures (values from `rrec_spec.h`), puts the pins in the default state, triggers, records
`start_ms` and `start_cycles`. The audio thread reads blocks with a slice of one block time, so the 100 ms watch fires at exactly 100 ms and a cut or halt is
answered within 16 ms. Each block goes through `rac_block()`. Frame indices count from the first kept frame (index 0 = PDM start + 50 ms). A highlight is
`(centre_down_ms - start_ms) x 16 - 800`; a motor edge `(cycles - start_cycles) x 16000 / cycle_hz - 800`. `rau_cut(mark)` sets a frame limit
`(mark_ms - start_ms) x 16 - 800`; the audio thread finishes the partial chunk when the block with the mark arrives, and drops later frames until `rau_halt`.
Highlights and motor edges wait in small queues (spin lock, any context) and are taken by the audio thread; the last 16 motor edges before a start are kept
and read at `rau_start` (M1 before the PDM). `rau_release` refuses (`-EBUSY`) while capturing. The unit never calls `rail_set` (search 5: 0 hits; test `test_unit_never_switches_rail`).

## 2. Kit facts to verify (plan section 8). Method: counts and file lists only, no kit line printed or copied

Server runs `u3-k1-k7-k8-run1.log`, `-run2.log`, `-run3.log` (commands in `u3-k-facts.cmd`, `u3-k-facts2.cmd`, `u3-k-facts3.cmd`), read at 2026-11-13 04:54 to 04:56 CET.

- **K1 (true, one part unverified).** `include/zephyr/audio/dmic.h` exists. Counts of the names: `dmic_configure` 1, `dmic_trigger` 4, `DMIC_TRIGGER_START` 1, `DMIC_TRIGGER_STOP` 1, `dmic_read` 1, `struct dmic_cfg` 3, `dmic_build_channel_map` 1 (run1). `drivers/audio/dmic_nrfx_pdm.c` exists. Unverified: "a driver outside the kit can offer this API on a node of its own": the counts of `struct dmic_driver_api` and `__subsystem` in `dmic.h` are 0 (run2), so I did not find how the header names its driver table; only the simulated input (behind `rhw_mic()`) is a driver of this project and it does not use the kit's header, so nothing built here rests on it.
- **K7 (true for the name, not shown for the nRF54L series).** `include/zephyr/drivers/clock_control/nrf_clock_control.h` exists: `nrf_clock_control_request` 5, `nrf_clock_control_release` 1, `z_nrf_clock_control_get_onoff` 1, `onoff` 10, `CLOCK_CONTROL_NRF_TYPE_HFCLK` 8 (run1). `drivers/clock_control/clock_control_nrf.c` defines the on-off getter (6 hits) and names `nrf54l` once in lower case (run3, `grep -l -i`; the upper-case count is 0, run2); the header names no `NRF54L`. `rau_hw_real.c` uses the on-off route (`z_nrf_clock_control_get_onoff(CLOCK_CONTROL_NRF_SUBSYS_HF)`, `onoff_request`, `onoff_release`); I did NOT count `CLOCK_CONTROL_NRF_SUBSYS_HF` or `sys_notify_init_callback`, so those two names are unverified and the real file is unproven.
- **K8 (true: the application can do it; the driver is not changed).** `include/zephyr/drivers/pinctrl.h`: `pinctrl_apply_state` 3, `PINCTRL_STATE_SLEEP` 1, `PINCTRL_STATE_DEFAULT` 2, `PINCTRL_DT_DEFINE` 3, `PINCTRL_DT_DEV_CONFIG_GET` 4 (run1, run2). `include/zephyr/pm/device.h`: `pm_device_action_run` 1, `PM_DEVICE_ACTION_SUSPEND` 2. `dmic_nrfx_pdm.c`: `PM_DEVICE` 0, `pm_device` 0, `PM_DEVICE_ACTION_SUSPEND` 0, `PINCTRL_STATE_SLEEP` 0, `pinctrl_apply_state` 1, `PINCTRL_STATE_DEFAULT` 1 (run1, run2). So the driver has no suspend action and applies only the default state (as FW l.465 says); the device-PM route does not exist, but the pinctrl route does: the application defines its own pin configuration for the `pdm20` node and applies `PINCTRL_STATE_SLEEP` (`r_pins_sleep` in `rau_hw_real.c`). It needs a `sleep` pin state in the node's devicetree (step 7). `pdm20` is in `dts/vendor/nordic` for the nRF54LM20A (run2: 1 file). Decision D11c holds: no change to the kit's driver. The real call is not compiled or run by any test here (unproven).

## 3. Rows of section 2.2, 2.3 and 2.1 that name U3: case and log line

Green log lines: `u3-green-cases.console` is twister's per-case report of run 1 (44 cases, line numbers below refer to it; the cases not changed by R24 are the same in run 2). Run 2 (the cited run) has 46 cases; its per-case report could not be fetched because the server stopped `remote.sh` (less than 25 GB free, `u3-green-cases2.console`), so for the cases new in run 2 the evidence is the cited run's count lines: `u3-run2-final.log` line 22 `46 of 46 executed test cases passed (100.00%)` (native_sim) and line 44 (simulated chip), and the per-case `PASS` lines of the unaffected suites. "Red" = the named broken copy's failing line in `u3-run2-final.log` (the line numbers are the same as in run 1 for every copy).

| Row | Case (suite.case) | What it shows | Log line |
|---|---|---|---|
| A1 | `audio_cfg.test_dmic_config_values` | the input received 16,000 Hz, 16 bit, 2 channels, 1,200,000 to 1,650,000 Hz, 1,024 bytes, 8 blocks; order configure, pins default, trigger. The channel map is 0 in the record: the real file builds it (`rhw.h` l.58); the map itself is NP | green-cases l.18 |
| A2 | `audio_cfg.test_header_clock_fields` | spec numbers 1,280,000 and 80; the driver's own pick is NP (inside the kit's driver, which the simulation replaces) | l.16 |
| A3 | `audio_cfg.test_gain_zero` | `gain_db` 0 received, code 0x28 in the spec; the register write is NP | l.15 |
| A4 | `audio_chunk.test_interleave_order` | channel 0 first, frame by frame; which microphone lands left is NP (T-MIC) | l.32 |
| A5 | `audio_chunk.test_payload_equals_blocks` | all 8,192 frames of chunk 0 equal the source frames 800 to 8,991 | l.31 |
| A6 | `audio_svc.test_hfxo_before_trigger`, `test_hfxo_released_after_stop`, `test_hfxo_prepare_timeout` | request < running < configure < trigger with a 5 ms crystal; release after stop and after the rail went off; refused while capturing; a crystal that never runs gives `-ETIMEDOUT` and releases | l.58, l.56, l.57. Red: `hfxo_after_trigger`, log l.1088 |
| A7 | `audio_chunk.test_dropout_zero_fill`, `audio_svc.test_dropout_logged`, `test_dropout_on_read_error`, `test_late_thread_is_not_a_dropout` | zeros of 256 frames at the gap, flag bit 7, `dropout_blocks` 1, logged once, length unchanged (15,200 frames), stream continues in place; a late thread (ring full) is not a dropout | l.27, l.55, l.54, l.53. Red: `dropout_skips`, l.266 |
| A8 | `audio_chunk.test_32_blocks_per_chunk`, `audio_svc.test_ring_of_three`, `test_put_waits_on_enobufs` | first chunk full in block 36, second in block 68 (32 apart); with the store holding every chunk exactly 3 puts, buffers of chunks 0 to 2 byte-equal to their copies after 500 ms more, no read while it waits, the 4th chunk starts when chunk 0 is reported written; `-ENOBUFS` makes a chunk wait | l.28, l.52, l.51 |
| A9 | `audio_chunk.test_discard_800_frames`, `test_start_time_is_first_kept_frame` | 3 blocks keep nothing, 4 blocks keep 224; first kept frame = raw frame 800; `uptime_ns` 12,050,000,000 for a start at 12 s | l.30, l.29. Red: `discard_0`, l.127 |
| A10 | `audio_svc.test_stop_keeps_frames_to_mark`, `audio_chunk.test_partial_last_chunk` (pure: mark inside a block keeps exactly 1,000 frames) | mark at 3,000 ms keeps 47,200 frames = 5 chunks + 6,240; last kept frame 47,999; nothing after; later blocks do not change the chunk. "the press start time is logged" is the join's (row also U3, J) | l.50, l.25 |
| A11 | `audio_svc.test_no_read_outside_recording` | 0 `MIC_READ` events after boot, during HFXO and rail wait, and after the halt; the second recording starts at its own frame 800 | l.49 |
| A12 | not mine (J). My part of the order: prepare, 1 ms, start = configure, pins default, trigger | see A1, A6 | |
| A13 | not mine (J). My part: stop, blocks released, pin sleep state, then the caller switches the rail, HFXO last | `audio_svc.test_hfxo_released_after_stop`, `test_clock_low_whenever_rail_off` | l.56, l.46 |
| A14 | `audio_svc.test_clock_low_whenever_rail_off` | sleep state is the first event after boot (index 0) and before the rail on; default while capturing; sleep state again after the stop and before the rail off; real pin levels NP | l.46 |
| A15 | build assertion `BUILD_ASSERT(RAU_RING_CHUNKS >= RREC_CHUNK_RING, ...)` in `rau.c` | broken copy `ring_two` stops the build with the assertion's message on both targets; the real RAM use: NP (stage `dk` memory report) | `u3-run1-final.log` l.1310 and l.1320 |
| A16 | `audio_motor.test_interval_frames` | high at frame 2,400, low at 3,040, interval {2,400; 3,840} | l.38. Red: `motor_no_tail`, l.677 |
| A17 | `audio_motor.test_span_two_chunks`, `test_span_open_interval`, `test_fifth_merged_into_fourth`, `test_unused_pairs_ff` | {8,100; 8,192} then {0; 908}; same with MOTOR still high at the chunk edge; five intervals give 4, the fourth {3,100; 5,000}; unused pairs and highlight slots are 0xFFFFFFFF | l.37, l.36, l.35, l.34. Red: `no_split` l.814, `fifth_dropped` l.951 |
| A18 | `audio_motor.test_m1_rest_marked_in_first_chunk`, `audio_svc.test_motor_edges_marked` | M1 ending at the first kept frame gives {0; 800}; ending 100 ms after the start {0; 1,600}; ending inside the discard {0; 320}; a pulse over before the start leaves none; thin part: M1 {0; 320} and an MW pulse {4,000; 5,440} in the first chunk. The join's part (`recorder_actions.test_mw_in_recording_marked`) is not mine | l.33, l.40 |
| A19, A20 | none | NP: microphone physics, board wiring | |
| S9 | `audio_chunk.test_partial_last_chunk` | buffers pre-filled with 0xA5; bytes after the last frame are zero; `frames` 1,248 (and 1,000 and 0 cases) | l.25 |
| S10 | `audio_chunk.test_flags_each_bit` | 0x03 base; 0x0B motor; 0x13 for -32768 alone and for 32767 alone; 0x23 time not set; 0x43 B15; 0x83 dropout; bit 2 and bits 8 to 15 zero in every case; a clipped sample inside the discard sets nothing | l.26. Red: `clip_high_only`, l.403 |
| S11 (ruling R24: frame numbers) | `audio_chunk.test_highlights_in_header`, `test_late_highlight_in_next_chunk`, `test_highlight_without_partial_chunk_close_only`, `audio_svc.test_highlight_marks_down_time`, `test_late_highlight_in_next_chunk`, `test_highlight_in_partial_last_chunk` | 9 in one chunk: header keeps 8 (frames 160 x k), `highlight_count` 8, CLOSE count 9 and ms values; 40 over 7 chunks: CLOSE count 40, first 32 values 80 x i ms, the header values in order are 1,280 x i; late highlight (CENTRE_DOWN frame 4,000, chunk 0 already out) found in chunk 1's header as 4,000; service: CENTRE_DOWN at 1,200 ms gives 18,400 in chunk 2, one at 700 ms delivered at 1,300 ms gives 10,400 in chunk 2; a stop before the chunk is handed over puts the marker in the partial last chunk (frame 800); with no partial chunk (stop on the chunk edge) it is in the CLOSE record only; calls outside a capture ignored | run 2 count lines (l.22, l.44) |
| S12 | `audio_chunk.test_timestamps`, `test_time_not_set` | uptime of chunk 0 and chunk 1 (+512 ms) on counters of 1 MHz and 16 MHz and after 20 days at 16 MHz (no overflow); `utc_ms` 0 and flag bit 5 when not set | l.21, l.20 |
| S13 | `audio_chunk.test_fill_fields`, `audio_svc.test_chunk_facts_from_power_chip` | battery and temperature taken at each chunk start (3,871 then 3,872 mV; with the simulated power chip 3,790 then 3,788 mV, die 312 then 315), boot count, recording id, type, fw_version | l.19, l.44 |
| C13 | `audio_chunk.test_highlight_frame_from_down_time` | CENTRE_DOWN 600 ms after the start gives the frame number 8,800 in chunk 1's header (FW l.566 as rewritten by R24), although the call comes when 9,440 frames are kept | run 2 count lines. Red: `highlight_release_time`, `u3-run2-final.log` l.540 and l.602 |
| C15 (U3 part) | `audio_svc.test_no_block_100ms_reports`, `test_cut_after_no_block` | reported once, 100 to 101 ms after the last block; after it `rau_cut` returns `-EIO` with the 1,760 frames there are | l.48, l.47. Red: `no_block_150ms`, l.1225 |
| C33 (U3 part) | `audio_motor.*` (A16, A17) | see above | |

## 4. Findings and readings (the specification wins; none is settled silently)

- **F1 (ruled: R24, accepted and built).** A highlight fires 440 to 850 ms after CENTRE_DOWN, longer than a chunk, so the chunk of the press has often gone to the store. Ruling R24 (FW l.564, l.566; `step6-plan.md` last section): the marker in a chunk header is the frame number of CENTRE_DOWN counted from the first kept frame of the recording, written in the header of the chunk being filled when the highlight fires. Built in `rac_highlight()` and `chunk_marks()` (`rau_chunk.c`): every highlight that fired during a chunk is written, in order, into that chunk's header (at most 8; a ninth stays out, D4); the CLOSE record keeps ms from the start; a highlight before the first kept frame is frame 0. A stop before the chunk is handed over puts the marker in the last (partial) chunk; with no partial chunk (F2) it is in the CLOSE record only (both tested). Chunks still go to the store when full.
- **F2. A stop exactly on a chunk edge.** The chunk is already with the store, so no partial chunk exists: `rau_cut` returns `last = NULL` and no chunk carries flag bit 1 (`test_partial_last_chunk`, third case). The join passes NULL to `rst_close` (allowed by `rst.h`).
- **F3. The simulated input after a stop with "stop delivering after block n" set never returns -EIO** (its read keeps answering -EAGAIN because the stop came after the blocks' due times). The audio thread therefore also ends the stop on one -EAGAIN after the stop (no block for a whole block time). Found by a leftover thread in run `u3-dev2` (see section 7); fixed in `rau.c`.
- **F4. The simulated input has no slab overflow.** While the audio thread waits for a free chunk (ring full, `test_ring_of_three`) the real driver's 8 blocks (128 ms) would overflow and lose blocks; the simulation queues them without limit, so the test proves "nothing in the ring is overwritten and no frame is skipped by this unit", not "no audio is lost when the store stalls for more than 128 ms" (FW l.644's worst case is that loss).
- **F5. A silently lost block is detected by time.** A block that arrives a whole block time or more after its due time while the thread was already waiting is taken to follow a lost one, and zeros are inserted (the simulated drop gives no error). A read error (`-EIO`) while capturing is one lost block, zeros at its due time. Whether the real driver reports a loss as an error or silently is NP; a thread that is merely late is not mistaken (`test_late_thread_is_not_a_dropout`).
- **F6. Readings.** (a) `rau_cut` waits up to `RREC_MIC_NO_BLOCK_MS - RREC_BLOCK_MS` for the mark's block, then ends with the frames there are and returns `-EIO`, `out` filled (header says "up to RREC_MIC_NO_BLOCK_MS"; total at most 100 ms plus one block). (b) `dropout` callback's `block` = frame position in the chunk divided by 256 at the moment the block starts (FW names no number). (c) A dropout block that touches two chunks is counted in each (`dropout_blocks` "in this chunk", FW l.570) and flags both. (d) Battery, temperature and fw_version and the B15 flag are taken at the start of each chunk (FW l.567 "at the chunk start"). (e) `rau_init` may be called again (the tests do, after `rhw_sim_reset`): it clears the RAM state, re-applies the sleep state and returns `-EBUSY` only while capturing; a simulated reboot hook stops a running capture. (f) `rau_release` without a prior successful `rau_prepare` returns 0. (g) Highlights before the first kept frame count as frame 0. (h) `chan_map_lo` is 0 in the configuration; the real file builds the map (as `rhw.h` says). (i) The real file leaves the gain to the kit's driver and devicetree (FW l.417's `gain_db`); not set there, unproven.

## 5. Broken copies (plan U3 list: 10), each on both targets

Edits: `tests/audio/broken_edit.py` (each matches once, diffs in the run log). Each fails its named case and the build or run reaches its end. Other failed cases per copy (from the server's twister logs of run 1, `u3-failed-lists.console`; run 2's counts are in `u3-run2-final.log`, equal for every copy except the highlight copy and `discard_0`) are consequences of the same fault:

| Copy | Named case (red on both targets) | Also failed (same on both targets) and why |
|---|---|---|
| `discard_0` | `audio_chunk.test_discard_800_frames` (l.127, l.189) | in run 1 18 more (run 2 lists 18 in all, names not fetched): every case that reads a frame value, a frame count, a mark or a motor/highlight frame measured from the first kept frame (the stream is 800 frames early) |
| `dropout_skips` | `audio_chunk.test_dropout_zero_fill` (l.266, l.328) | `test_flags_each_bit` (dropout case), `audio_svc.test_dropout_logged`, `test_dropout_on_read_error`: all use a missing block |
| `clip_high_only` | `audio_chunk.test_flags_each_bit` (l.403, l.465) | none |
| `highlight_release_time` | `audio_chunk.test_highlight_frame_from_down_time` (l.540, l.602 of run 2) | 6 more in run 2 (the log says `failed cases listed: 7`); their names could not be fetched (server space rule); from the cases that check a frame number of a highlight: `test_highlights_in_header`, `test_late_highlight_in_next_chunk`, `test_highlight_without_partial_chunk_close_only`, `audio_svc.test_highlight_marks_down_time`, `test_late_highlight_in_next_chunk`, `test_highlight_in_partial_last_chunk` (inferred, not read) |
| `motor_no_tail` | `audio_motor.test_interval_frames` (l.677, l.739) | the other motor cases and `audio_svc.test_motor_edges_marked`: all check interval ends that include the tail |
| `no_split` | `audio_motor.test_span_two_chunks` (l.814, l.876) | none |
| `fifth_dropped` | `audio_motor.test_fifth_merged_into_fourth` (l.951, l.1013) | none |
| `hfxo_after_trigger` | `audio_svc.test_hfxo_before_trigger` (l.1088, l.1150) | `test_hfxo_prepare_timeout` (prepare no longer waits, so no `-ETIMEDOUT`) |
| `no_block_150ms` | `audio_svc.test_no_block_100ms_reports` (l.1225, l.1287) | none |
| `ring_two` | the BUILD: `static assertion failed: "audio: the chunk ring must never be below the specified count (FW l.490)"` (l.1310, l.1320); no test ran (44 blocked) | |

Run 2: `RESULT PASS` (line 1321), then `UNIT PASS tests/audio` (line 1323).

## 6. Not provable here (marked, with the reason)

A2 (the driver's clock pick), A3 (register write), A4 (which microphone lands left), A12 and A13 as whole sequences (the join), A14 real pin levels, A15 real RAM use, A19, A20, the channel map and gain of the real configuration, `rau_hw_real.c` as a whole (no build here compiles it; `CLOCK_CONTROL_NRF_SUBSYS_HF`, `sys_notify_init_callback`, `PDM_CHAN_LEFT`, `struct pcm_stream_cfg` names not counted), and the behaviour of the real driver on a lost block (F5).

## 7. Looks at results before the final run (all reported)

- `u3-k-facts.cmd` runs: kit facts only (section 2).
- `u3-dev1.console`: native_sim only, first full compile: 34 of 44 cases passed, 10 failed. Causes: one test expectation (feed of 8 blocks too short for a 1,600-frame interval end) and one real defect: `k_sem_reset()` wakes the idle audio thread with an error and my thread started a capture; found from the event log dump in dev2.
- `u3-dev2.console`: same plus a log dump and values in messages (the dump was removed afterwards): leftover capture visible as reads before the start.
- `u3-dev3.console`: after making the stop end on -EAGAIN (F3): still 9 failures, same wake-up defect.
- `u3-dev4.console`: after removing `k_sem_reset(&run_sem)` and checking the return of `k_sem_take`: 43 of 44 passed; the one failure was a test bug (expected 47,999 as a 16-bit value; now cast to `int16_t`).
- `u3-run1.console` / `u3-run1-final.log`: the cited run, no edit between dev4 and it except that test fix.
- Ruling R24 (2026-11-13 05:30): `rau_chunk.c`, `test_chunk.c`, `test_svc.c` changed; run 2 (`u3-run2.console`, `u3-run2-final.log`) is the cited run: 46 of 46 on both targets, 10 broken copies as named, `UNIT PASS tests/audio`.
- After run 2 the server refused `remote.sh` (`# remote.sh: less than 25 GB free on the server; stop`, `u3-green-cases2.console`), so the per-case lists of run 2 were not fetched; I did not try another way to reach the server. My own run folders under `/ws/out` and `/root/ring-os/src-u-audio` use space there; the lead may have them removed.
- No other file was edited outside Owns. Listing of newer files outside my folders at the end (`u3-rule-searches.log` 6) shows other builders' work (`tests/store/`, `docs/core-notes.md`), not mine. The server's `/root/ring-os/src-u-audio` and `/ws/out` run folders of my runs are left in place (no deletion by pattern).

## 8. Rules checked (saved in `u3-rule-searches.log`)

Pure part: no `zephyr/` include, no `k_` call (1b: 0 hits). Thin part: includes only the kernel, `rau.h`, `rhw.h`, the simulation header under `CONFIG_RING_RHW_SIM` and the pure header (2). No chip pin by number in any owned file (3: 0 hits). Numbers of two digits or more in `rau_chunk.c` and `rau.c` outside comments: unit conversions (ns per s, ms per s), two queue sizes of 16 and the tuning poll of 4 ms; none is a specification number (4). The unit makes no rail call (5). No code or text of the kit or Zephyr was copied or printed.

questions_for_owner: none

RESULT: done, unit U3 passes its targeted run (`UNIT PASS tests/audio`: 46 cases green on both simulated targets, 10 broken copies red as named, ring_two stops the build), with ruling R24 built and findings F2 to F6 for the lead.
