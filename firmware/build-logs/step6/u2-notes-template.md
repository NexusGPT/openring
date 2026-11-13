# store notes: unit U2 of software step 6 (the storage of recordings on the card)

Builder: U2 helper. Version read: commit 2d3d5c2 of the project plus the lead's later rulings (R24 of the specification, lines 564 and 566, applied). No git was run.
Contract: `firmware/docs/step6-plan.md` (parts named in the brief, both rulings sections), `firmware/docs/rhw-notes.md` sections 2 and 3, the frozen headers `rst.h`, `rrec_spec.h`, `rhw.h`, `rhw_sim.h`. "FW l.N" = line N of `design/firmware.md`.
Cited run: `@@CONSOLE@@` (the unit run `bash tools/unit_run.sh tests/store` on the build server). Its last result lines: @@RESLINE@@ and @@UNITLINE@@; @@RCLINE@@. Suites on both targets: @@TWLINES@@ (63 of 63 cases).
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
@@ROWS@@

Rows not provable without hardware (from the plan, section 7 item 3): S6's one CMD25 per chunk, S19 (bench S1), S25 (real card size), S30 (wear). Pin levels of S2: NP. The real card, SPI and `rst_hw_real.c`: NP.

## 3. Broken copies (11 of the plan's list)

Run: `tests/store/broken_run.sh` inside the cited run (part `broken-store`). Each copy is `modules/ring_store` with one edit (`broken_edit.py`, the diff of each is in the run's output folder on the server and printed in the console). A copy counts only when its NAMED case fails on both targets; the cases listed as "also failed" run the same broken code, are listed in `broken_edit.py` (a case failing that is not listed fails the run) and no case failed for another reason. All 63 cases ran in each copy.

| Copy | Named case | Result line (named case failed, both targets) | Also failed (same broken code) |
|---|---|---|---|
@@BROKEN@@

Why the extra cases: `digest_big_endian` breaks every case that compares a digest; `sb_older_wins` every case that restarts the store (the older superblock copy would be read); `lba_no_wrap` the wrap on the 24-chunk card; `sfull_17` the SFULL callback at 17; `delete_frees_middle` the factory delete and the 300-recording case (they use the same walk); `delete_without_confirm` the 300-recording case (it also checks -EACCES); `log_drops_newest` the case that checks which records reach the card. `hdr_crc_512`, `scan_accepts_gap`, `two_tries`, `init_before_rail` fail only their named case.
The plan's name `init_before_rail` is built as: the card init is issued once before VDD_SD is on (the simulated card refuses it and counts it).

## 4. Kit facts

- **K12** (`crc32_ieee()` is CRC-32/ISO-HDLC): TRUE. `store_fmt.test_crc_check_value` gives 0xCBF43926 for "123456789" through `crc32_ieee` and through the test's own bit-wise CRC; its line is in section 2 (row S8). `crc32_ieee_update` chains (`test_digest_stream_equals_oneshot`).
- **K2** (disk access API names): the names `disk_access_read`, `disk_access_write`, `disk_access_ioctl`, `DISK_IOCTL_CTRL_INIT`, `DISK_IOCTL_CTRL_DEINIT`, `DISK_IOCTL_GET_SECTOR_COUNT` exist: TRUE for existence, by the compile test `store_fmt.test_kit_disk_and_crc_names_exist` (@@K2LINE@@) and by the counts in `build-logs/step6/u2-k2-grep.log` (see section 8). Not checked: the argument types (the real file is not compiled by any step 6 run).

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

RESULT: @@RESULT@@
