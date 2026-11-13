# store notes: unit U2 of software step 6 (the storage of recordings on the card)

Builder: U2 helper. Version read: commit 2d3d5c2 of the project plus the lead's later rulings (R24 of the specification, lines 564 and 566, applied). No git was run.
Contract: `firmware/docs/step6-plan.md` (parts named in the brief, both rulings sections), `firmware/docs/rhw-notes.md` sections 2 and 3, the frozen headers `rst.h`, `rrec_spec.h`, `rhw.h`, `rhw_sim.h`. "FW l.N" = line N of `design/firmware.md`.
Cited run: `build-logs/step6/u2-final10.console` (the unit run `bash tools/unit_run.sh tests/store` on the build server). Its last result lines: l.1563: `RESULT PASS` and l.1565: `UNIT PASS tests/store`; l.1567: `# remote exit code: 0`. Suites on both targets: l.22 (native_sim) and l.44 (simulated chip) (63 of 63 cases).
Every earlier run and look is listed in section 8.

## 1. What exists

| Path (under `firmware/`) | What |
|---|---|
| `modules/ring_store/zephyr/module.yml`, `Kconfig`, `CMakeLists.txt` | the module (`CONFIG_RING_STORE`, stack size and priority of the storage thread) |
| `modules/ring_store/src/rst_fmt.c`, `rst_fmt.h` | pure: chunk header, superblock, index record, event log record, digest, CRC-32 |
| `modules/ring_store/src/rst_layout.c`, `rst_layout.h` | pure: sector map, chunk count, LBAs, free space, S30, SFULL, minutes left |
| `modules/ring_store/src/rst_log.c`, `rst_log.h` | pure: superblock choice, recordings from the index (table of 256 and on demand), tail move, recovery scan, event log buffer of 8 |
| `modules/ring_store/src/rst.c` | thin: storage thread, rail sequence, 3 init tries, 3 write tries, one operation at a time, every call of `rst.h` |
| `modules/ring_store/src/rst_hw_real.c` | real disk and `spi00` suspend; only where the simulated drivers are off; NOT PROVEN, never compiled by any run of step 6 (the tests run with the simulation on) |
| `tests/store/` | `CMakeLists.txt`, `prj.conf`, `testcase.yaml`, `app.overlay`, `boards/native_sim.conf`, `src/tst.[ch]` (helpers), `src/test_*.c` (9 suites, 63 cases), `broken_edit.py`, `broken_run.sh` |
| `docs/store-notes.md` | this file |
| `build-logs/step6/u2-*` | logs, the run wrapper, the generator of this table |

The pure files include `<errno.h>` (constants only) and `<zephyr/sys/crc.h>` and call `crc32_ieee()` and also `crc32_ieee_update()` (the digest is built word by word; same library, same header; decision D11a names only `crc32_ieee()`: flagged for the lead). No other kernel header.

## 2. Rows of the plan that name U2: test case and log line

Each proof gives the case name with the line of its `PASS` result in `build-logs/step6/u2-cases10.console` (the handler logs of the cited run's two green twister runs, read off the server by one extra call; twister prints per-case lines only for failing runs), first on native_sim, then on the simulated chip. Rows whose test is another unit's say so.

| Row | Proof | What it shows |
|---|---|---|
| S2 | `test_rail_sequence` (build-logs/step6/u2-cases10.console l.214, l.524); `test_no_disk_call_with_rail_off` (build-logs/step6/u2-cases10.console l.199, l.509) | Order deinit, suspend, rail off / rail on, 1 ms, resume, init; sleep state at boot first; the card refuses nothing. Pin levels: NP. |
| S3 | `test_mount_reads_sector_count` (build-logs/step6/u2-cases10.console l.193, l.503) | Sector count read at mount: 1,000,000 gives 14,124 chunks; 7,812,500 gives 118,932. |
| S4 | `test_sector_map` (build-logs/step6/u2-cases10.console l.121, l.431); `test_chunk_lba_wraps` (build-logs/step6/u2-cases10.console l.112, l.422); `test_examples` (build-logs/step6/u2-cases10.console l.115, l.425); `test_chunks_wrap_on_small_card` (build-logs/step6/u2-cases10.console l.178, l.488) | Sector map, wrap at s = total - 1, total, total + 1, both examples of FW l.654, and a real wrap on a card of 24 chunks. |
| S5 | `test_no_rewrite_during_recording` (build-logs/step6/u2-cases10.console l.202, l.512); `test_one_write_per_chunk` (build-logs/step6/u2-cases10.console l.208, l.518) | No chunk sector written twice; superblock and index outside the chunk area. |
| S6 | `test_one_write_per_chunk` (build-logs/step6/u2-cases10.console l.208, l.518) | One 65-sector write per chunk, sequential. Whether the card gets one CMD25: NP (FW 10.5 item 12). |
| S7 | `test_chunk_header_bytes` (build-logs/step6/u2-cases10.console l.56, l.366); `test_chunk_header_roundtrip_and_rejects` (build-logs/step6/u2-cases10.console l.59, l.369); `test_unused_slots_are_ff` (build-logs/step6/u2-cases10.console l.91, l.401); `test_chunk_encode_rejects_bad_counts` (build-logs/step6/u2-cases10.console l.53, l.363) | Every header field at its offset, bytes written out by hand with the test's own bit-wise CRC. |
| S8 | `test_crc_check_value` (build-logs/step6/u2-cases10.console l.63, l.373); `test_little_endian` (build-logs/step6/u2-cases10.console l.82, l.392) | 0xCBF43926 for "123456789"; little-endian fields. |
| S9 | `test_last_chunk_zero_tail` (build-logs/step6/u2-cases10.console l.79, l.389); `test_full_cycle_with_partial_last_chunk` (build-logs/step6/u2-cases10.console l.184, l.494) | Store zeroes the tail and sets payload_bytes = frames x 4. The audio side (frames counted by audio) is U3's. |
| S10 | not a U2 case | Flag bits are filled by U3 (`audio_chunk.test_flags_each_bit`). Store side: the flags field is written as given (`test_chunk_header_bytes`, flags 0x00A9). |
| S11 | `test_close_highlights_32` (build-logs/step6/u2-cases10.console l.97, l.407) | CLOSE record keeps the first 32 and the full count (40); a ninth highlight in one chunk header is refused with -EINVAL (decision D4). Highlights per chunk header are U3's. |
| S12 | not a U2 case | Filled by U3. Store side: utc_ms, uptime_ns and cycle_hz are written as given (`test_chunk_header_bytes`). |
| S13 | not a U2 case | Filled by U3. Store side: battery_mv, temp_c_x10, boot_count, fw_version written as given (`test_chunk_header_bytes`); boot_count of the superblock: `test_boot_count`. |
| S14 | `test_superblock_bytes` (build-logs/step6/u2-cases10.console l.88, l.398); `test_mount_picks_newer_valid_copy` (build-logs/step6/u2-cases10.console l.127, l.437); `test_mount_uses_the_valid_copy` (build-logs/step6/u2-cases10.console l.196, l.506) | Superblock bytes; both valid, one bad CRC, one bad magic, both bad; the same on the simulated card. |
| S15 | `test_index_record_bytes` (build-logs/step6/u2-cases10.console l.72, l.382); `test_index_lba_wraps` (build-logs/step6/u2-cases10.console l.118, l.428) | Index record bytes and the wrap at 65,536. |
| S16 | `test_digest` (build-logs/step6/u2-cases10.console l.66, l.376); `test_digest_stream_equals_oneshot` (build-logs/step6/u2-cases10.console l.69, l.379) | Digest of 3 chunks typed (0x6ddb5d74, from Python zlib, build-logs/step6/u2-typed-values.log). |
| S17 | `test_state_is_last_record` (build-logs/step6/u2-cases10.console l.103, l.413); `test_table_pushes_out_oldest_and_finds_on_demand` (build-logs/step6/u2-cases10.console l.106, l.416); `test_list_beyond_cache_reads_index` (build-logs/step6/u2-cases10.console l.100, l.410) | CLOSE = new, CONFIRM = transferred, DELETE = deleted, recovered = recovered until confirmed; the 256-entry table and the index on demand (decision D16). |
| S18 | `test_superblock_twice_per_recording` (build-logs/step6/u2-cases10.console l.220, l.530) | Superblock twice per recording (open, close), no rail event between. `recorder_rails.test_sd_rail_per_state` is J's. |
| S19 | not a U2 case | NP: bench S1. The rail-on-during-recording default is what `test_superblock_twice_per_recording` shows. |
| S20 | `test_three_tries_then_fault_open_flag_kept` (build-logs/step6/u2-cases10.console l.223, l.533) | Two failures then success (3 write calls, no fault); three failures: one fault callback, nothing more written, the superblock on the card still open, no CLOSE record. |
| S21 | `test_loss_bound_with_stalled_card` (build-logs/step6/u2-cases10.console l.136, l.446) | A card taking 2 s per write, a chunk offered every 512 ms: at the cut 6 accepted, 3 on the card, 3 lost = the ring. |
| S22 | `test_cut_inside_chunk_write` (build-logs/step6/u2-cases10.console l.133, l.443) | Cut after sector 1, 33 and 64: the chunk in flight is dropped. "The superblock is never in flight with a chunk" holds by construction (one storage thread, one disk lock) and is not asserted by a case of its own. |
| S23 | `test_stop_on_each_mismatch` (build-logs/step6/u2-cases10.console l.151, l.461); `test_recovered_close_record` (build-logs/step6/u2-cases10.console l.142, l.452); `test_scan_summary` (build-logs/step6/u2-cases10.console l.148, l.458) | Five cases (magic, header CRC, payload CRC, recording_id, chunk_seq); CLOSE RECOVERED, head past the last good chunk, open flag cleared. |
| S24 | `test_counts` (build-logs/step6/u2-cases10.console l.160, l.470); `test_s30_sfull_edges` (build-logs/step6/u2-cases10.console l.163, l.473); `test_storage_left_minutes` (build-logs/step6/u2-cases10.console l.166, l.476); `test_callbacks_once_per_crossing` (build-logs/step6/u2-cases10.console l.157, l.467) | Counts, edges 3,517/3,516/17/16, minutes, callbacks once per crossing. |
| S25 | not a U2 case | NP (FW 10.5 item 25). |
| S26 | `test_confirm_match_and_mismatch` (build-logs/step6/u2-cases10.console l.14, l.324) | Match appends CONFIRM, mismatch -EBADMSG and nothing appended. |
| S27 | `test_delete_needs_confirm` (build-logs/step6/u2-cases10.console l.17, l.327) | -EACCES without CONFIRM, no record appended. |
| S28 | `test_tail_moves_over_leading_only` (build-logs/step6/u2-cases10.console l.32, l.342) | Delete the second of three: free unchanged; then the first: both freed; also after a restart. |
| S29 | `test_no_erase` (build-logs/step6/u2-cases10.console l.26, l.336); `test_read_chunk_deleted_not_found` (build-logs/step6/u2-cases10.console l.29, l.339) | Delete writes an index record and a superblock only; the chunk is unchanged; read of a deleted recording -ENOENT. `xfer_store...` is U4's. |
| C3 | `test_s30_sfull_edges` (build-logs/step6/u2-cases10.console l.163, l.473) | 3,517 / 3,516 / 17 / 16 free chunks. |
| C8 | `test_init_three_tries_200ms` (build-logs/step6/u2-cases10.console l.187, l.497) | 3 tries 200 ms apart, rail off again after the third failure. The J half (`recorder_boot.*`) is J's. |
| C9 | `test_read_error_reports` (build-logs/step6/u2-cases10.console l.139, l.449); `test_scan_read_error_reports` (build-logs/step6/u2-cases10.console l.145, l.455) | -EIO, open flag still set, the next start recovers. |
| C16 | `test_cut_inside_chunk_write` (build-logs/step6/u2-cases10.console l.133, l.443) | A new mount of the same simulated card sees the open flag. `recorder_boot.test_restart_after_cut_recovers` is J's. |
| C24 | `test_one_open_recording` (build-logs/step6/u2-cases10.console l.205, l.515); `test_busy_while_operation_runs` (build-logs/step6/u2-cases10.console l.175, l.485) | A second open -EBUSY; any call while another runs returns -EBUSY at once. `xfer_proto.test_busy_while_running` is U4's. |
| T26 | `test_log_record_bytes` (build-logs/step6/u2-cases10.console l.85, l.395); `test_buffer_of_8_drops_oldest` (build-logs/step6/u2-cases10.console l.38, l.348); `test_written_when_rail_on` (build-logs/step6/u2-cases10.console l.47, l.357); `test_ring_of_2046` (build-logs/step6/u2-cases10.console l.44, l.354) | Record bytes (with and without a crash block), buffer of 8 drops the oldest and counts, written at the next mount and at once when mounted, ring of 2,046. |

Rows not provable without hardware (from the plan, section 7 item 3): S6's one CMD25 per chunk, S19 (bench S1), S25 (real card size), S30 (wear). Pin levels of S2: NP. The real card, SPI and `rst_hw_real.c`: NP.

## 3. Broken copies (11 of the plan's list)

Run: `tests/store/broken_run.sh` inside the cited run (part `broken-store`). Each copy is `modules/ring_store` with one edit (`broken_edit.py`, the diff of each is in the run's output folder on the server and printed in the console). A copy counts only when its NAMED case fails on both targets; the cases listed as "also failed" run the same broken code, are listed in `broken_edit.py` (a case failing that is not listed fails the run) and no case failed for another reason. All 63 cases ran in each copy.

| Copy | Named case | Result line (named case failed, both targets) | Also failed (same broken code) |
|---|---|---|---|
| `hdr_crc_512` | `store_fmt.test_chunk_header_bytes` | l.129 (native_sim), l.191 (simulated chip) | none |
| `digest_big_endian` | `store_fmt.test_digest` | l.266 (native_sim), l.328 (simulated chip) | `store_delete.test_confirm_match_and_mismatch`, `store_delete.test_delete_needs_confirm`, `store_delete.test_delete_refused_while_open`, `store_delete.test_no_erase`, `store_delete.test_read_chunk_deleted_not_found`, `store_delete.test_tail_moves_over_leading_only`, `store_fmt.test_digest_stream_equals_oneshot`, `store_recovery.test_cut_inside_chunk_write`, `store_recovery.test_recovered_close_record`, `store_recovery.test_scan_summary`, `store_svc.test_chunks_wrap_on_small_card`, `store_svc.test_full_cycle_with_partial_last_chunk` |
| `sb_older_wins` | `store_log.test_mount_picks_newer_valid_copy` | l.403 (native_sim), l.465 (simulated chip) | `store_delete.test_confirm_match_and_mismatch`, `store_delete.test_tail_moves_over_leading_only`, `store_index.test_list_beyond_cache_reads_index`, `store_recovery.test_cut_inside_chunk_write`, `store_recovery.test_loss_bound_with_stalled_card`, `store_recovery.test_read_error_reports`, `store_recovery.test_recovered_close_record`, `store_svc.test_boot_count`, `store_svc.test_mount_uses_the_valid_copy`, `store_svc.test_one_open_recording`, `store_svc.test_three_tries_then_fault_open_flag_kept` |
| `lba_no_wrap` | `store_layout.test_chunk_lba_wraps` | l.540 (native_sim), l.602 (simulated chip) | `store_svc.test_chunks_wrap_on_small_card` |
| `scan_accepts_gap` | `store_recovery.test_stop_on_each_mismatch` | l.677 (native_sim), l.739 (simulated chip) | none |
| `sfull_17` | `store_space.test_s30_sfull_edges` | l.814 (native_sim), l.876 (simulated chip) | `store_space.test_callbacks_once_per_crossing` |
| `delete_frees_middle` | `store_delete.test_tail_moves_over_leading_only` | l.951 (native_sim), l.1013 (simulated chip) | `store_delete.test_factory_recordings_deleted`, `store_index.test_list_beyond_cache_reads_index` |
| `delete_without_confirm` | `store_delete.test_delete_needs_confirm` | l.1088 (native_sim), l.1150 (simulated chip) | `store_index.test_list_beyond_cache_reads_index` |
| `two_tries` | `store_svc.test_three_tries_then_fault_open_flag_kept` | l.1225 (native_sim), l.1287 (simulated chip) | none |
| `init_before_rail` | `store_svc.test_rail_sequence` | l.1361 (native_sim), l.1423 (simulated chip) | none |
| `log_drops_newest` | `store_evlog.test_buffer_of_8_drops_oldest` | l.1500 (native_sim), l.1562 (simulated chip) | `store_evlog.test_written_when_rail_on` |

Why the extra cases: `digest_big_endian` breaks every case that compares a digest; `sb_older_wins` every case that restarts the store (the older superblock copy would be read); `lba_no_wrap` the wrap on the 24-chunk card; `sfull_17` the SFULL callback at 17; `delete_frees_middle` the factory delete and the 300-recording case (they use the same walk); `delete_without_confirm` the 300-recording case (it also checks -EACCES); `log_drops_newest` the case that checks which records reach the card. `hdr_crc_512`, `scan_accepts_gap`, `two_tries`, `init_before_rail` fail only their named case.
The plan's name `init_before_rail` is built as: the card init is issued once before VDD_SD is on (the simulated card refuses it and counts it).

## 4. Kit facts

- **K12** (`crc32_ieee()` is CRC-32/ISO-HDLC): TRUE. `store_fmt.test_crc_check_value` gives 0xCBF43926 for "123456789" through `crc32_ieee` and through the test's own bit-wise CRC; its line is in section 2 (row S8). `crc32_ieee_update` chains (`test_digest_stream_equals_oneshot`).
- **K2** (disk access API names): the names `disk_access_read`, `disk_access_write`, `disk_access_ioctl`, `DISK_IOCTL_CTRL_INIT`, `DISK_IOCTL_CTRL_DEINIT`, `DISK_IOCTL_GET_SECTOR_COUNT` exist: TRUE for existence, by the compile test `store_fmt.test_kit_disk_and_crc_names_exist` (`test_kit_disk_and_crc_names_exist` (build-logs/step6/u2-cases10.console l.76, l.386)) and by the counts in `build-logs/step6/u2-k2-grep.log` (see section 8). Not checked: the argument types (the real file is not compiled by any step 6 run).

## 5. For the header (comments the lead adds to `rst.h`; no signature changes)

1. `rst_put_chunk` returns `-ENOSPC` when the chunk would overwrite a chunk that is not freed (the chunks queued plus those on the card already equal the chunk count). It also returns `-EINVAL` when the header's frames are 0 or over 8,192, highlight_count over 8 or motor_count over 4 (decision D4: a ninth highlight stays out of the chunk), and the store overwrites `recording_id` and `recording_type` of the header with those of the open recording.
2. `rst_delete` returns `-EBUSY` when a recording is open or the superblock open flag is set (a recording waits for its recovery): a delete moves the tail and must not free chunks of a recording not closed. Also `rst_delete_factory_recordings`.
3. `rst_close` with `last` having an invalid header returns `-EINVAL` before anything is written.
4. `rst_log_read`, `rst_list`, `rst_read_chunk`, `rst_confirm`, `rst_delete`, `rst_open`, `rst_recover` return `-ENODEV` when not mounted; `rst_mount` before `rst_init` returns `-ENODEV`.
5. `rst_log_put` sets `seq` when the record is written to the card (gap-free numbers from 1), not when it is queued; the dropped count is the only trace of a drop.
6. `rst_recover` returns `-EINVAL` when the open flag is clear.

## 6. Readings and decisions taken (the specification or header is silent)

1. **A card with no valid superblock gets a new log** (both copies unreadable as superblocks). A card that could not be READ is never formatted (`-EIO`, `test_mount_never_formats_an_unreadable_card`). Formatting a card that holds other data is a choice: see `questions_for_owner`.
2. **The superblock is also written at CONFIRM, DELETE and the end of the recovery** (it commits the index head). FW says twice per recording; recordings still have exactly two (`test_superblock_twice_per_recording`).
3. **Index record numbers and event log seq start at 1.** The event log record of seq s is in LBA 2 + ((s - 1) mod 2,046). The superblock's `log_head` lags; at mount the scan goes on from it, and the store writes the superblock after 1,023 log records so the lag stays under a lap (`test_ring_of_2046`).
4. **Tail move** (FW l.660) is derived from the index only: the first CLOSE record whose recording has no DELETE record; `index_tail` moves with it, so the index walk at mount covers live recordings only.
5. **Decision D16** (256 newest in RAM, older read from the index) is built; **decision D17** (index wrap at 65,536) is not.
6. **S30 and SFULL callbacks** are once per crossing counted from the state at the open: a recording that opens already under S30 is not told.
7. **boot_count** (D14): grows at a mount with `boot = true`, one superblock write for the boot (also on a new card).
8. **Ruling R24** (lines 564, 566): `highlight_frame` is a frame number from the first kept frame; the store writes it as given; the recovery scan turns it into ms as frame x 1000 / 16,000 for the CLOSE RECOVERED record (`test_scan_summary`).
9. **Reboot hook** (sim only): `rst_init` registers a reset hook with `rhw_sim_add_reboot_hook`; a reboot while the storage thread is inside a write is not supported (tests wait for the thread first).
10. The two threads' locks: calls take `op_lock` without waiting (-EBUSY), disk access is serialised by a second lock.

## 7. Findings

- No change of a frozen header is needed (section 5 lists comments only).
- `rst.h` says `rst_recover` ends with a CLOSE record with RECOVERED; a recovered recording that is not confirmed shows state 3 in the list (ruling 10 of rhw-notes).
- `RREC_LOG_DROPPED` (rrec_spec.h) is written by the join, not the store; the store only counts.
- Not done: nothing of the brief is left out; `rst_hw_real.c` is unproven and was never compiled by a run.

## 8. Runs and looks

`u2-cases10.console` (the per-case lines of the cited run) and `u2-k2.console`/`u2-k2-grep.log` (the counts of K2: each kit name is found in its header, e.g. `disk_access_read` 1 in `storage/disk_access.h`, `DISK_IOCTL_CTRL_DEINIT` 2 and `DISK_IOCTL_GET_SECTOR_COUNT` 1 in `drivers/disk.h`, `crc32_ieee_update` 2 in `sys/crc.h`; the one count of 0 per header is a name that belongs to the other header) are from the same server. `build-logs/step6/u2-*.console`: dev1 (first build, 59 of 62 passed), dev2 (broken copies working, counting error found), run3 (kit-name check did not compile), short4 to short8 (suites alone: compile errors, then twister read suite names from a macro; short8 green, 126 of 126), full9 (UNIT PASS before ruling R24), the cited run (after R24). `u2-editcheck.log`: each of the 11 edits matches once. `u2-typed-values.log`: the numbers typed from Python. Searches of the sources: `u2-search-*.log`.

## questions_for_owner

1. A card that holds no valid superblock (a new card, or a card from another use) is formatted at the first mount, which destroys what it held. Should the ring instead refuse a card whose first sectors are not blank?

RESULT: done, unit U2 passes on both simulated targets (63 of 63 cases, 11 of 11 broken copies fail their named case) in the cited run
