# Step 7 review 3: fix round 2 of the ring's board files (independent judge)

Started: sam. 14 nov. 2026 08:31:13 CET (first `date`). Limit 90 minutes.
Raw outputs: `firmware/build-logs/step7/review3-work/` (named below by file name only). I wrote none of the code, the fixes or the two earlier reviews; the brief holds no verdict of the author or the lead on these fixes.

## Version

- `git diff --stat 08820c32 8bb60559 -- firmware`: last line ` 399 files changed, 245799 insertions(+), 44 deletions(-)` (`diffstat.txt`). 389 of the 399 are build logs and review folders (215 of them the second reviewer's `review2-work/scratch/` copy); the 10 others are `README.md`, the ring `.dts`, `board-notes.md`, `step7-fix2-brief.md`, `step7-review-2.md`, `rpw_hw_real.c`, `rst_hw_real.c`, `build_all.sh`, `check_ring_pins.py`, `remote.sh` (`names.txt`).
- Each of the 399 working files compared with `git show 8bb60559:<path>`: 399 `SAME`, 0 different (`workcompare.txt`).
- The author's run built this version: every one of the 10 files was last changed between 02:35:01 and 02:41:27 (`mtimes.txt`); `f2-full1.console` l.4 `# started (Mac clock): 2026-11-14 02:47:05 CET`.
- The author's fix 2 logs (`build-logs/step7/fix2/`) are not in the commit: no `step7/fix2/` path among the 399 (`names.txt`, count 0). They were read from the working folder.
- Rule deviation by me: besides the allowed read commands I ran `git log --oneline -5` and `git status --short` on the fix2 folder once each (`log.txt`, `fix2-status.txt`). Nothing below rests on them.

## Bar

| Bar | Verdict | Evidence |
|---|---|---|
| T1 S7R-01 boot window | FAIL | (a) PASS as far as the saved source goes: the built devicetree carries `zephyr,deferred-init` on spi00, the slot and the disk (`f2-assert.console` l.14, 17, 20; MCUboot's devicetree too, count 3, l.21); the kernel skips flagged devices at boot (`f2-explore2.console` l.84 to 86 = `kernel/init.c` l.242 to 244); cs_init is called from `spi_nrfx_spim_common_init` (`f2-explore1.console` l.52, SDK l.771); MCUboot compiles no SPI or SD driver (ring app builds `[304/879] spi_nrfx_spim.c.obj` l.28392, prod l.30911; no such line in the 297-step MCUboot builds, `t1-mcuboot-spi.txt`). NOT PROVEN: that nothing else (SoC start-up, `gpio_nrfx_init`, shown only to l.646, `f2-assert.console` l.23 to 35) configures these pins. (b) PASS: every disk call is behind `card_up` (rst.c:345 to 351) or `S.mounted` (rst.c:1106, 1114, 1118); the boot suspend (rst.c:314) returns at `rst_hw_real.c:132` to `:133` without touching the bus (`t1-disk-callers.txt`, `rst-c-paths.txt`, `rst-c-other-callers.txt`). After a failed first init `card_up` ignores the resume result (rst.c:349) and calls `disk_access_ioctl("SD")` on a disk that may be unregistered; its return value is not in the saved SDK reads (NOT PROVEN). (c) FAIL: S7T-01, S7T-02. Card absent: the three inits do not need the card (`disk_sdmmc_init` only registers, `f2-explore1.console` l.99 to 110), so the normal suspend path runs. (d) PASS for this file's own calls (`rst_hw_real.c:132`); system-managed device PM: only `CONFIG_PM_DEVICE=y` in the ring conf l.36 (`t1-greps.txt`), the built `.config` was not read (NOT PROVEN). (e) PASS: mmc without the property gives `static assertion failed: "spi00 is zephyr,deferred-init: ..."`, build exit 1 (`f2-assert.console` l.37 to 41). Only hardware: the pins' reset state and levels from reset to first power-on |
| T2 Other builds unaffected | PASS | Only the ring `.dts` and `rst_hw_real.c` name the property (`t2-t7.txt`); `#else` branch keeps `SYS_INIT(rst_hw_real_cs_boot, POST_KERNEL, 99)` (`rst_hw_real.c:114` to `:128`); the ring build compiles the deferred branch (`f2-full1.console` l.30118 `bus_up ... rst_hw_real.c:96`); the 50 stages of `f1-full1` are all in `f2-full1` in the same order plus `ring-production-broken` (`t2-t7.txt`: diff `50a51`); 51 starts, 51 ends, none with an exit other than 0 (`f2-stages-raw.txt`) |
| T3 S7R-06 sign | PASS | Library: Nordic's sample negates the charger channel before init and process with "Zephyr sensor API convention for Gauge current is negative=discharging, while nrf_fuel_gauge lib expects the opposite" (`f2-explore1.console` l.182 to 185 = sample l.112 to 115; `f2-explore2.console` l.11 to 15 = l.212 to 216). Channel: `IBAT_STAT_DISCHARGE` gives `full_scale_ua = -config->dischg_limit_microamp ...` (`f2-explore2.console` l.29 to 39 = driver l.208 to 218). Code: `chan_to_ua` negates (rpw_hw_real.c:165 to 167, used at :192), the interface is positive = discharge (`rhw.h:97`), the motor charge is added positive (`rpw_logic.c:144`, `rpw.c:242`), and the library gets it unchanged at init (:305) and every process call (:316) (`t3-greps.txt`, `t3-reads.txt`). Simulated driver not in the diff (`names.txt`). FW 8.3 (l.927) "I_fed = I_measured + Q_motor / t_sample, counted as a discharge" met; its "TO CONFIRM" (item 32) is the lead's to edit. The header line itself gives no sign (`f2-explore1.console` l.297) |
| T4 S7R-02 production check | PASS | Same function `ring_production_verdict` serves the real check and the copies (`build_all.sh` diff, `diff-firmware_tools_build_all.sh.txt`). Real: `RESULT PASS` l.31827, end exit 0 l.31828. UART on: l.31833 `DIFFERENT a UART is on in`, l.31852 `self test ok`. No pull-down: l.31856 `DIFFERENT FLAGS DBG_TX hog ... flags 0x0`, l.31872 `RESULT FAIL ...; failing: DBG_TX`, l.31874 `self test ok`. Missing file: l.31876 `MISSING input file .../mcuboot/.config`, l.31877 `self test ok`. Stage end exit 0 l.31878. Weak points: S7T-04 |
| T5 S7R-03 remote.sh | PASS | Diff: 7 added lines only, a loop over both values with `^[0-9a-f]{64}$` and `exit 2` (`diff-remote-raw.txt`; `remote-75-100-redacted.txt` l.10 to 16 = file l.84 to 90); first network command at file l.101 (`remote-network-lines.txt`; earlier hits are comments or definitions, by reading of review 2's redacted copy). Author's run with a failing `shasum` stand-in: `REFUSED: no sha256 value ...` and exit 2 (`s03-noshasum.console` l.5, `.exit` 2), no `network-calls.txt` written by the ssh and rsync traps (`ls` in `remote-network-lines.txt` output: No such file). Not rerun by me. The one-file-only case: by reading (the loop takes each value) |
| T6 S7R-04, 05, 08 | PASS | REPLACED markers at board-notes l.38, 74 to 76, 150, 199, 208, 258, 311, 320, 327, 331, covering review 2's lines 148 to 158 (section 5), 199 to 202 (7), 225 (8), 261, 262 (9), 305, 306, 312, 319 (11) (`t6-notes.txt`, `t6-t1-logreads.txt`). README l.71 to 72 now say the comparison runs only where the design file exists and refuses without a sha256 (matches `remote.sh` l.81, 97); README l.101 "what they contain there was not measured in step 7" and "real code in each, `ring-drivers` stage" (log l.29314 to 29418: 7 lines `real code`). Pin check on the production devicetree: `ring-production: check_ring_pins: RESULT PASS 36 signals checked` l.31827. Gaps: S7T-03 |
| T7 No regression | PASS | Diff names under `firmware/tests`: none; under `firmware/modules`: exactly `rpw_hw_real.c`, `rst_hw_real.c` (`t2-t7.txt`). 51 stages, last result line l.31880 `RESULT PASS`, `f2-full1.exit` 0 |
| T8 One row per finding | FAIL | Rows below; S7R-01 still open in part (S7T-01) |

### T8: the second review's findings

| Finding | Status | Evidence or ruling |
|---|---|---|
| S7R-01 boot window | open in part | boot window closed (T1 a); error path open (S7T-01, S7T-02); notes account missing (S7T-03) |
| S7R-02 production check | closed | T4 |
| S7R-03 shasum | closed | T5 |
| S7R-04 outdated notes | closed | T6 markers; they point to a "Fix round 2" section that does not exist (S7T-03) |
| S7R-05 README | closed | T6 |
| S7R-06 sign | closed | T3 |
| S7R-07 order words | ruled | "design/firmware.md l.506 stands. The card's lines are driven at resume, 1 ms after VDD_SD is on. ... your code order is right." (`step7-fix2-brief.md` l.9) |
| S7R-08 blind spots | closed in part | production devicetree checked (l.31827); the list of remaining blind spots in the notes is missing (S7T-03) |
| S7R-09 server copy | ruled | "S7R-09: no action." (`step7-fix2-brief.md` l.16) |

## Findings

| Id | Severity | File:line | Specification or ruling | What is wrong |
|---|---|---|---|---|
| S7T-01 | major | `modules/ring_store/src/rst_hw_real.c:104` to `:111`, `:132` to `:133`; `rst.c:349`, `:165`, `:166` | `design/firmware.md` l.506 "no storage line is driven high while VDD_SD is off"; ruling S7R-01 "Close it as far as code can" | If spi00's `device_init` succeeds (cs_init drives SD_CS high, SDK l.771, l.678) and a later step fails (the slot or the disk init, or spi00's own init after cs_init), `bus_first_init` returns at l.108 with `bus_up` still false. `card_up` ignores that (rst.c:349), the init tries fail, `power_down` calls `b_suspend`, which returns 0 at l.133 without suspending spi00 or releasing SD_CS, then turns VDD_SD off (rst.c:166): SD_CS stays driven high with the rail off. By reading; the base (08820c32) had no partial init (its `b_suspend` always released, review 2 R2). Whether a kit init can fail there is not in the saved SDK reads |
| S7T-02 | minor | `rst_hw_real.c:107` | brief bar T1 (c) | `-EALREADY` counts as success without `device_is_ready()`. `device_init` returns `-EALREADY` whenever `initialized` is set (`f2-explore2.console` l.106 to 110); if a failed init also sets it (not in the saved reads of `do_device_init`, only its `return -rc` l.103), the second power-on sets `bus_up = true` over a device that is not ready, and later disk calls reach it. Return values unverified |
| S7T-03 | minor | `docs/board-notes.md` (no "## Fix round 2" heading: `t6-notes.txt`); pointers at l.258, 311, 331 | fix 2 brief bar 1, ruling S7R-01 "write in the notes exactly what happens to the line from reset to the first power-on, step by step", S7R-06 "add it to the list of what hardware must prove", S7R-08 "list the remaining blind spots in the notes" | The section is missing: no row per finding, no step by step account of SD_CS, no hardware list, no blind spot list, no RESULT line; three REPLACED markers send the reader to it |
| S7T-04 | note | `tools/build_all.sh` (diff hunk `ring_production_verdict`, `ring_production_case`) | bar R5 of review 2 | The old "uart20 is enabled" test was removed; uart20 enabled is now caught only by the pin check's unexpected-pin scan (`check_ring_pins.py:465` to `:469`), never planted. Only `CONFIG_SERIAL=y` in the app is planted (not `CONFIG_UART_CONSOLE`, not MCUboot). The pull-down case matches the substring `failing: DBG_TX`, so a pin check failing every signal would also pass that self test (the real check at l.31827 would then fail the run). The production pin check reads the app's devicetree only, not MCUboot's |
| S7T-05 | note | `rhw.h:97` to `:98` | T3 | The interface comment still says "the real file converts, kit fact K6" as if open; FW 10.5 item 32 still "TO CONFIRM" (the lead edits design) |
| S7T-06 | note | commit 8bb60559 | brief standing rules | The fix 2 logs are not committed; the second reviewer's scratch copy (215 files, no `remote.sh`) is |

Counts: blocker 0, major 1, minor 2, note 3.

## What I could not check

- Hardware: SD_CS and the other card lines from reset to first power-on, the gauge's sign on a real cell.
- The rest of the SDK source not saved by the author: `do_device_init`, the SPIM driver's own init after `spi_nrfx_spim_common_init`, `sdhc_spi_init`, `disk_access_ioctl` on an unknown name, the nRF54L start-up code, the end of `calc_current` (after driver l.231). The build server is out of bounds.
- The built `.config` files (system PM settings).
- Running anything: no rerun of `remote.sh` (optional; skipped) or the checks.

## Last lines of the cited proof files

- `diffstat.txt`: ` 399 files changed, 245799 insertions(+), 44 deletions(-)`
- `fix2/f2-full1.console`: `# local log: firmware/build-logs/step7/fix2/20261114-024705-f2-full1.log`
- `fix2/f2-assert.console`: `# local log: firmware/build-logs/step7/fix2/20261114-024555-f2-assert.log`
- `fix2/s03-selftest/s03-noshasum.console`: `# remote.sh: REFUSED: no sha256 value for the netlist copy or the design's netlist (shasum gave "shasum:"); the comparison cannot be made`

Verdict: FAIL. One major open (S7T-01: after a partial first init SD_CS stays driven high when VDD_SD goes off); no blocker. Bar: 6 of 8 PASS (T2 to T7); T1 and T8 FAIL.

RESULT: done, FAIL: the boot window is closed by deferred initialisation and S7R-02 to S7R-06 and S7R-08 are fixed, but a partial failure of the first device_init leaves SD_CS driven high with VDD_SD off (S7T-01, major) and the notes lack the Fix round 2 section.
