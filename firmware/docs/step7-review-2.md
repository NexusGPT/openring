# Step 7 review 2: fix round 1 of the ring's board files (independent judge)

Started: sam. 14 nov. 2026 02:24:03 CET (from `date`, `build-logs/step7/review2-work/start-date.txt`). Limit 2 hours.
Raw outputs: `firmware/build-logs/step7/review2-work/` (named below by file name only). The brief holds no verdict of the author or the lead on the fixes. I wrote none of the code, the fixes or the first review.

## Version

- `git diff --stat 47204f09 08820c32 -- firmware`: 90 files changed (`diffstat.txt`, last line ` 90 files changed, 34558 insertions(+), 60 deletions(-)`).
- Each changed artifact file compared with `git show 08820c32:<path>` (`version-compare.txt`): 17 `SAME`, 1 `DIFFERS`: `firmware/docs/board-notes.md` (still in writing, as the brief says). It was read last as claims: snapshot `board-notes-as-read.md`, sha256 0173028...aa3f8 at 02:30:07 (`board-notes-read-time.txt`).
- The author's run `f1-full1` started 2026-11-14 00:11:11 CET (`f1-full1.console` l.4); every changed code and settings file was last modified between 00:02:19 and 00:06:39 (`mtimes.txt`), so the run built the committed version.
- While I worked, a lead run `lead-full6` was being written (`ls-step7.txt`); not mine, not touched, not used.

## Bar

| Bar | Verdict | Evidence |
|---|---|---|
| R1 S7-01 refusal | PASS | `tools/remote.sh:79` to `:91` (compare, `REFUSED`, `exit 2` at l.86) come before the first network command, `ssh` at l.94 (`remote-sh-redacted.txt`, server and key lines withheld). Run in a scratch copy with `ssh` and `rsync` replaced on PATH by a trap that only records a call: 4 cases (A board copy row 181 P1.14 to P1.15, B the design copy's row changed, C board copy missing, D one byte added), each `exit=2`, a `REFUSED` line, `network_calls_before=0 network_calls_after=0` (`r1-refusal.console`). Unchanged case, by reading only: l.88 prints "equals", then l.94 onward run as before; the author's real run shows it: `f1-full1.console` l.5 `# netlist copy equals design/ecad/ring/netlist.csv (sha256 2727a3c7...5442)`. Not weakened: the diff of `remote.sh` is additions only, 20 lines (`diff-firmware_tools_remote.sh.txt`); the path rule l.53 to 57, the 25 GB rule l.98 to 107 and the key handling l.31, 50 are unchanged. Weak point: S7R-03 |
| R2 S7-02 SD_CS | FAIL | Paths that switch VDD_SD (`r2-paths.txt`, `r2-more-paths.txt`): unmount `rst.c:481` deinit, `:484` suspend, `:485` rail off; mount failures `rst.c:360`, `:459` through `power_down` `:160` to `:166` (suspend, then rail off); rail on `rst.c:345`, then 1 ms, then resume `:349`; boot `rst.c:314` suspend and `rst_hw_real.c:79` `SYS_INIT(..., POST_KERNEL, 99)`. `b_suspend` releases SD_CS (`GPIO_DISCONNECTED`, `rst_hw_real.c:66`, `:95`) even when the suspend fails; `b_resume` drives it (`:71`, `:102`) before the SPI resume. No other caller switches VDD_SD (only `rst.c:166`, `:485`); ship mode (`rpw.c:627`) and the cold reboot (`rsy_hw_real.c:80`) do not switch it. MCUboot compiles no SPI driver (`r2-mcuboot-spi-count.txt`: 297 MCUboot build lines, the only `spi` or `gpio_nrfx` hit is `gpio_nrfx.c.obj`). Open: at every boot SD_CS is driven high with VDD_SD off from spi00's init until the POST_KERNEL 99 release (S7R-01, major). The `pinctrl.dtsi` comment (l.22 to 26, `r2-pinctrl-spi00.txt`) is true by reading. Only hardware can prove: the pin levels, the length of the boot window, that `GPIO_DISCONNECTED` leaves the line without pull on this chip |
| R3 Power real file | NOT PROVEN | Calls against the header quoted in `f1-explore1.console` (header l.380 is console l.9): `nrf_fuel_gauge_process(float v, float i, float T, float t_delta, float *soc, struct nrf_fuel_gauge_state_info *state)` (console l.104, 105 = header l.475) against `rpw_hw_real.c:311`, `:312`: V, A, °C, s, `&soc`, `NULL`, int return checked; `nrf_fuel_gauge_tte_get(float *tte)` (l.127 = 498) and `ttf_get(float *ttf)` (l.139 = 510) against `:317`, `:320`. Units: soc in % times 10 (`:324`, `rhw.h:272` 0.1 %), tte and ttf in s (`:325`, `:326`, `rhw.h:273`, `:274`), NAN or 0 turns into "unknown" UINT32_MAX. `CONFIG_RING_POWER_REAL=y` (`app/boards/ringrec_nrf54lm20a_cpuapp.conf`, `r3-ring-drivers-stage.txt` l.26 of the stage, `f1-full1.console` l.29312); driver list `rpw_hw_real.c.obj text 6840 bytes: real code` (`f1-full1.console` l.29335) with `g_process`, `r_rail_set`. Rail switch: `rpw_hw_real.c:344` `rhw_register_pmic(&real_pmic)`, `:285` `.rail_set = r_rail_set`, `:101` `regulator_enable/disable` of `ldsw_sd` (`r3-rail-path.txt`). NOT PROVEN: the sign of the current given to the library (S7R-06): the code passes the kit channel's raw value and itself calls the sign open (`rpw_hw_real.c:162`, `:293`, `:294`) |
| R4 Pin check | PASS | Flags compared where a source states them: 11 `SAME FLAGS`, 7 `no source` (`r4-ringpins-flags.txt`, table `check_ring_pins.py:103` to `:122`, sources FW l.82, 83, 84, 381, 865, 506, `r4-flag-sources.txt`). Fixed-function pins: "pin ... from the chip's fixed function" per pin (8 lines); the devicetree states none. Unparsable property: `UNEXPECTED ... cannot be read as GPIOs` (`:414` to `:419`), gpio hog (`:403` to `:411`), by reading only (no planted copy). Broken copies, each `RESULT FAIL 36 signals checked; failing: <one>` and `self test ok` (`f1-full1.console`): MOTOR l.30241, SD_MISO l.30263, LCD_TE l.30285, wrong port PMIC_INT l.30307, removed node JOY_LEFT l.30328, disabled node JOY_DOWN l.30348, extra pin `unexpected-pins(1)` l.30368, wrong flag JOY_UP l.30390, unknown net NEWNET l.30412, changed netlist row LCD_RST l.30434; the verdict compares the whole failing list as a string (`build_all.sh:585` to `:591`). Blind spots: S7R-08 |
| R5 Production settings | PASS | `app/ringrec_production.conf:7` to `:9` (SERIAL, CONSOLE, UART_CONSOLE off), overlay: console chosen deleted, `uart20` disabled, DBG_TX P1.15 hog input with pull-down (`ringrec_production.overlay:9`, `:10`, `:15`, `:19` to `:23`; netlist DBG_TX U1 P1.15, `r5-code.txt`), MCUboot conf the same. Stage `ring-production` exit 0 (`f1-full1.console` l.31794); `ring-production-check` reads both `.config` files (l.31809, 31810 `# CONFIG_SERIAL is not set`) and the hog (l.31812 to 31815), exit 0 (l.31816). It fails on `CONFIG_SERIAL=y` or `CONFIG_UART_CONSOLE=y` in either image and on `uart20` okay (`build_all.sh:649` to `:656`; the node `uart20: uart@c6000` exists, `s7-explore4.console`, `r5-uart-addr.txt`), by reading; never shown failing (S7R-02). Development build keeps its console: `zephyr,console = &uart20` (`dts:26`), `CONFIG_CONSOLE=y` (`prj.conf:2`), `uart_nrfx_uarte.c.obj` compiled in the ring build (`r3-ring-drivers-stage.txt`) |
| R6 Honesty | FAIL | Stated: debug key NOT FOR SHIPPING (README l.82 to 84, board-notes l.337; the warning is in the run, `f1-full1.console` l.74, 27985, 30502), stand-in cell (README l.69, 70, 81; `rpw_battery_model.h` head), real files for the ring (README l.100; log l.29314 to 29419: 7 `*_hw_real.c` with real code), unproven items (README l.80 to 84; board-notes l.331, 332). 20 line citations of the Fix round 1 section checked, each matches (`r6-notes-line-check.txt`). Claims more than the log: README l.100 "most of them empty there: no node" for the kit (S7R-05); board-notes sections 5, 7, 8, 9, 11 and l.312, 319 still say the power file is off, three planted copies, 80 symbols, no production configuration (S7R-04) |
| R7 No regression | PASS | `git diff ... -- firmware/tests`: empty (`r7-diff-tests.txt`); `-- firmware/modules`: exactly `rpw_hw_real.c` and `rst_hw_real.c` (`r7-touch.txt`). Stages: first version 48 started, 48 ended; fix run 50 and 50; none missing, new `ring-production`, `ring-production-check`; every end `exit 0` (`r7-stage-compare.txt`); last result line `f1-full1.console` l.31818 `RESULT PASS`; remote exit 0 (`f1-full1.exit`: `0`) |
| R8 One row per finding | FAIL | Rows below. S7-02 is not closed (S7R-01); the other eight are closed or ruled |

### R8: the first review's findings

| Finding | Status | Evidence or ruling |
|---|---|---|
| S7-01 netlist drift | closed | R1 |
| S7-02 SD_CS while VDD_SD off | open in part | released after every suspend and before every rail-off path; not during the boot window (S7R-01) |
| S7-03 check blind spots | closed | R4; what remains: S7R-08; board-notes l.188 to 195 now says what the check sees |
| S7-04 too few broken copies | closed | R4, 10 copies, 7 new |
| S7-05 README l.96 | closed, with S7R-05 | README l.100 |
| S7-06 dead rails | closed | R3 rail path; README l.80, 81 rewritten |
| S7-07 debug key | closed | README l.82 to 84, board-notes l.337 |
| S7-08 IBATLIM | ruled | "S7-08 and S7-09: no code change; S7-09 see "production setting" below." (`step7-fix1-brief.md` l.15) |
| S7-09 console on | closed | R5 |

## Findings

| Id | Severity | File:line | Specification, netlist or ruling | What is wrong |
|---|---|---|---|---|
| S7R-01 | major | `modules/ring_store/src/rst_hw_real.c:74` to `:79` | ruling S7-02 (`step7-fix1-brief.md` l.10: "an input with no pull whenever VDD_SD is off"); `design/firmware.md` l.506 ("no storage line is driven high while VDD_SD is off") | From spi00's init (the kit's `cs_init` configures the CS GPIO `GPIO_OUTPUT_INACTIVE`, i.e. high for `GPIO_ACTIVE_LOW`: `f1-explore4.console` l.58 to 66, `dts:264`) until `SYS_INIT(rst_hw_real_cs_boot, POST_KERNEL, 99)`, SD_CS is driven high at every boot while VDD_SD is off (`regulator-boot-off`, `dts:361`). The file's own comment l.74 and board-notes l.331 say so; the length is not measured. Who acts: the author, ruled by the lead |
| S7R-02 | minor | `tools/build_all.sh:645` to `:659` | `design/firmware.md` l.1061; bar R5 | `ring-production-check` was never shown failing (no planted copy); DBG_TX's pull-down is printed (l.658), not checked; a missing `.config` or `zephyr.dts` makes `grep -q` return 2, which sets no failure, so the check passes |
| S7R-03 | minor | `tools/remote.sh:82` to `:84` | ruling S7-01 | Fails open where `shasum` cannot run: both values become the same shell error word, so two different netlists pass. Shown with a stand-in of those lines (copied rule, not `remote.sh` itself): `r1-shasum-missing.console` "would PASS (no refusal) although the files differ". `shasum` ships with macOS, so low risk |
| S7R-04 | minor | `docs/board-notes.md:148` to `:158`, `:199` to `:202`, `:225`, `:261`, `:262`, `:305`, `:306`, `:312`, `:319` (snapshot 0173028...) | bar R6 | The step 7 sections still say the power file does not compile and is off, three planted copies, the 80 largest symbols, no production configuration; the Fix round 1 section says otherwise; nothing marks the old text as superseded |
| S7R-05 | minor | `firmware/README.md:100` | bar R6 | "(most of them empty there: no node)" for the development kit: no log in `build-logs/step7` shows the kit's real-file sizes (`r6-readme-claims.txt`: every `hw_real.c.obj text` line of `f1-full1.console` is the ring's); the S7-05 row cites ring lines only. Also README l.70, 71 "compares ... before every run": `remote.sh:89` to `:90` skip the comparison when `design/` is absent |
| S7R-06 | note | `modules/ring_power/src/rpw_hw_real.c:162` to `:167`, `:300`, `:311` | `design/firmware.md` 8.3 (l.926) | The library gets the kit channel's raw current; the header quote gives "[A]" with no sign (`f1-explore1.console` l.97); the code calls the sign open (K6). Unchanged by this round |
| S7R-07 | note | `modules/ring_store/src/rst.c:345` to `:349` | ruling S7-02 ("driven again before VDD_SD comes on") against `design/firmware.md` l.506 ("After VDD_SD comes on: wait 1 ms, resume spi00 (default pin state: SD_CS output high)") | The code follows FW (drive at resume, 1 ms after the rail is on); the ruling's words say the opposite order. For the lead to settle |
| S7R-08 | note | `tools/check_ring_pins.py:335`, `:347`, `:422` to `:423`, `:125`, `:320` to `:327` | bar R4 | Blind spots that remain: flags of the first entry only and only ACTIVE_LOW, PULL_UP, PULL_DOWN; GPIOs of a controller with no port (for example the nPM1304's GPIOs) are skipped silently; pin configuration of the states (sleep `low-power-enable`, bias) is not checked; fixed-function pins: node enabled only, P1.20 and P1.21 from the table; pins selected in code; the UNSEEN compatible list is fixed and its NFC name for this chip is unverified; hog and unreadable-property paths never planted; the production devicetree is never checked (its DBG_TX hog would be `UNEXPECTED`); on the server the netlist copy is compared only through `remote.sh` (l.30134) |
| S7R-09 | note | `docs/board-notes.md:354` to `:358` | brief: R1 test must not reach the server (this review) | The author's first S7-01 self test did not plant its change and ran: it copied a scratch folder into their own server copy `/root/ring-os/src-s7`. Disclosed; their own copy; listed for the lead |

Counts: blocker 0, major 1, minor 4, note 4.

## What I could not check

- Anything on hardware: SD_CS levels, the length of the boot window, the gauge's sign and values, the rails.
- Running `check_ring_pins.py` or a planted production copy myself: no dtlib on the Mac (first review, `local-dtlib.txt`) and the build server is out of bounds.
- The caller of the kit's `cs_init` and `CONFIG_SPI_INIT_PRIORITY`'s value in this build: not in the saved SDK reads; the boot window rests on the quoted `cs_init` and the file's own comment.
- The value of `GPIO_PULL_DOWN` (the hog's `0x20`) and the NFC compatible of this chip: no saved read of those headers.
- The unchanged `remote.sh` path past l.91: read only, not run (brief).

## Last lines of the cited proof files

- `review2-work/version-compare.txt`: `SAME firmware/build-logs/step7/lead-full5.exit`
- `review2-work/diffstat.txt`: ` 90 files changed, 34558 insertions(+), 60 deletions(-)`
- `review2-work/r1-refusal.console`: `script exit 1`
- `review2-work/r1-shasum-missing.console`: `exit 0`
- `review2-work/remote-sh-redacted.txt`: ` 174 exit "$EXIT_CODE"`
- `review2-work/r2-paths.txt`: `	}`
- `review2-work/r2-more-paths.txt`: `--- mcuboot SPI config in ring build log`
- `review2-work/r2-mcuboot-spi-count.txt`: `[234/297] Building C object zephyr/drivers/gpio/CMakeFiles/drivers__gpio.dir/gpio_nrfx.c.obj`
- `review2-work/r2-pinctrl-spi00.txt`: `	spi21_default: spi21_default {`
- `review2-work/fw-506.txt`: `- **Write speed:** one 65-sector multi-block write (CMD25) per chunk, sequential addresses, no table updates in between.`
- `review2-work/r3-units.txt`: `326:	out->ttf_s = ttf > 0.0f ? (uint32_t)ttf : UINT32_MAX;`
- `review2-work/r3-code.txt`: `	    !device_is_ready(ldsw_sd)) {`
- `review2-work/r3-rail-path.txt`: `firmware/modules/ring_power/Kconfig-25-endif`
- `review2-work/r3-ring-drivers-stage.txt`: `=== stage ring-drivers end 2026-11-14T01:18:52Z exit 0`
- `review2-work/r4-log-lines.txt`: `30436:=== stage ring-pins-broken end 2026-11-14T01:19:58Z exit 0`
- `review2-work/r4-ringpins-flags.txt`: `SAME XL2 netlist P1.21 devicetree lfxo enabled; pin P1.21 from the chip's fixed function (the devicetree names no pin for this node)`
- `review2-work/r4-flag-sources.txt`: `--- nfct/saadc compat in saved SDK reads`
- `review2-work/r5-log.txt`: `47:warning: BOOT_MAX_IMG_SECTORS (defined at /ws/bootloader/mcuboot/boot/zephyr/Kconfig:974) was`
- `review2-work/r5-code.txt`: `19:DBG_TX,U1,B4,P1.15,bidirectional
`
- `review2-work/r5-uart-addr.txt`: `654:	if grep -q -E 'uart@c6000 \{' "$a/zephyr.dts" && awk '/uart20: uart@c6000`
- `review2-work/r6-notes-line-check.txt`: `30502:  WARNING: Using default MCUboot signing key file, this file is for debug use`
- `review2-work/r6-readme-claims.txt`: `firmware/build-logs/step7/fix1/20261114-001111-f1-full1.log`
- `review2-work/r7-stage-compare.txt`: `FIX ring-production-check                              exit 0 line 31816`
- `review2-work/r7-touch.txt`: `diff --git a/firmware/modules/ring_store/src/rst_hw_real.c b/firmware/modules/ring_store/src/rst_hw_real.c`
- `review2-work/mtimes.txt`: `2026-11-14 02:23:48 firmware/docs/board-notes.md`
- `review2-work/board-notes-read-time.txt`: `017302877ec81862b1585cc79cf95f111d9286d7a4c986bcf172bc47203aa3f8  firmware/docs/board-notes.md`
- `review2-work/secret-scan.txt`: `grep exit 1`
- `review2-work/scratch-remote-removed.txt`: `sam. 14 nov. 2026 02:31:42 CET`
- `fix1/f1-full1.console`: `# local log: firmware/build-logs/step7/fix1/20261114-001111-f1-full1.log`
- `fix1/f1-explore1.console`: `# local log: firmware/build-logs/step7/fix1/20261114-000014-f1-explore1.log`
- `fix1/f1-explore3.console`: `# local log: firmware/build-logs/step7/fix1/20261114-000128-f1-explore3.log`
- `fix1/f1-explore4.console`: `# local log: firmware/build-logs/step7/fix1/20261114-000152-f1-explore4.log`

Verdict: FAIL. One major open (S7R-01: SD_CS driven high at boot while VDD_SD is off); no blocker. Bar: 4 of 8 PASS (R1, R4, R5, R7); R2, R6, R8 FAIL; R3 NOT PROVEN.

RESULT: done, FAIL: fix round 1 closes seven of the nine findings and S7-08 is ruled and the power part's real file now compiles on the ring, but SD_CS is still driven high at every boot while VDD_SD is off (S7R-01, major).
