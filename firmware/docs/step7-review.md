# Step 7 review: the ring's board files (independent judge)

Started: ven. 13 nov. 2026 23:46:59 CET (from `date`, `build-logs/step7/review-work/start-date.txt`). Limit 2 hours.
Raw outputs: `firmware/build-logs/step7/review-work/` (named below by file name only). The brief holds no verdict of the author or the lead.

## Version

Each of the 16 artifact files (12 under `firmware/boards`, the two app ringrec files, `check_ring_pins.py`, `build_all.sh`) and `README.md` equals `git show 47204f09:<path>`: 17 lines `EQUAL` (`version-check.txt`). The author's run `s7-full1` started 2026-11-13 21:42:32 CET (`s7-full1.console` l.4), after the last change of every artifact file (latest `build_all.sh` 21:42:17, `mtimes.txt`). `board-notes.md` changed at 23:48:04 and was read last as claims, snapshot sha256 5c5eea35... (`board-notes-read-time.txt`, `board-notes-as-read.md`).

## Pin proof (B1)

My own script `b1_pins.py` reads the board `.dts`, the pin-control `.dtsi` and the app overlay as text and compares every `<&gpioN M` and `NRF_PSEL(fn, port, pin)` with the netlist rows of U1 (`b1-pins.txt`):
- 30 U1 port-pin signals in the netlist; 28 named in the board files, each on its netlist pin; the 2 not named, XL1 and XL2 (P1.20, P1.21), have no pin property (the `lfxo` node, `dts` l.188).
- Reverse: 38 pin uses read, 38 match a netlist net, 0 on a no-connect ball, 0 off the netlist. The overlay names no pin.
- The 6 dedicated-pin signals (XC1, XC2 by `hfxo`; USB_DP, USB_DN, U1_VBUS by `zephyr_udc0: &usbhs`; ANT1_NODE by `radio`) are enabled nodes (`dts` l.183, 257, 218). Total 36 of 36 U1 signals read; the other U1 nets are supply, ground, decoupling, reset and debug.
- Every group the bar names: microphones MIC_A_CLK P1.13, MIC_A_DATA P1.11 (`pinctrl.dtsi` l.79, 80, 86, 90), MIC_B_DATA P1.25 (`dts` l.105); SD bus SD_SCK P2.01, SD_MOSI P2.02, SD_MISO P2.04 (`pinctrl.dtsi` l.27 to 29, 35 to 37), SD_CS P2.05 (`dts` l.264); screen LCD_SCK P1.03, LCD_MOSI P1.04 (`pinctrl.dtsi` l.45, 46), LCD_CS P1.05 (`dts` l.286), LCD_DCX P1.06, LCD_RST P1.07, LCD_TE P1.14 (`dts` l.93 to 95), OLED_PWR_EN P1.30 (`dts` l.104); MOTOR P3.01 (`dts` l.82); joystick BTN_REC P0.04, JOY_UP P0.06, JOY_DOWN P0.07, JOY_LEFT P0.08, JOY_RIGHT P1.31 (`dts` l.52 to 72); PMIC_SDA P1.26, PMIC_SCL P1.27 (`pinctrl.dtsi` l.61, 62), PMIC_INT P1.28 (`dts` l.321); USB and crystals as above.
- Pin changes applied in the netlist: LCD_TE F4 P1.14 (`netlist.csv` l.181), OLED_PWR_EN F9 P1.30 (l.205), D6, E9, F8 no net (l.390, 394, 395); SPARE_P1_02, SPARE_P1_14, SPARE_P1_30 absent (`b1-dropped-spares.txt`: grep exit 1).

## Bar

| Bar | Verdict | Evidence |
|---|---|---|
| B1 Pins | PASS | `b1-pins.txt` (last two lines: 30 signals, 28 found, XL1 XL2 by `lfxo`; 38 uses, 38 match, 0 problems); `netlist-u1.txt`; the author's check agrees: `s7-full1.console` l.29577 `RESULT PASS 36 signals checked` |
| B2 Netlist copy | FAIL | byte-equal now (`b2-cmp.txt`: `cmp exit 0`, both sha256 2727a3c7...5442); nothing fails when they differ where the check runs: `s7-full1.console` l.29515 "source netlist ... not present here"; S7-01 |
| B3 Pin check can fail | NOT PROVEN | compares every U1 net (l.29512 to 29577: 61 rows: 36 signals SAME, 15 rows no node by nature, 10 rows with no net); fails on a wrong pin in a GPIO (MOTOR P3.02, l.29600) and in a default pin state (SD_MISO P2.03, l.29622), and on a missing property (LCD_TE, l.29644), each named alone. Wrong port, missing node, extra pin and netlist drift were never run (S7-04); I could not run them (no dtlib on the Mac, `local-dtlib.txt`). Blind spots: S7-03 |
| B4 Power chip | PASS | every pair equal, table below; all property names exist in the kit's bindings (`s7-explore3.console` l.113 to 402) |
| B5 Memory layout | PASS | `b5-layout.txt`: 4 partitions SAME as FW 9.2 l.1010, adjacent, last end 0x1fd000 = 2,036 KB; retained 0x2007f800, 1,024 bytes, outside `cpuapp_sram` (510 KB) and inside the SoC's 511 KB; app 621,112 of 982,896 B, MCUboot 45,596 B of 64 KB (`s7-full1.console` l.29298, 29304); swap using move compiled in the ring build (`b5-swap-move.txt`, l.29128); `wdt31` okay (`dts` l.302), alias `gpregret1` okay (l.40, 306), alias `crashram` a `zephyr,retained-ram` node (l.39, 123) in a 0x400 region (l.115), as `sys-notes.md` l.72 asks |
| B6 Real driver files | PASS | `log-ring-drivers.txt`: real code in `rau` 536, `rfa` 154, `rmo` 108, `rhw_clock` 118, `rscr` 222, `rst` 176, `rsy` 796, `rxf` 848 bytes; `rpw_hw_real.c not compiled`, reason in the ring `.conf` l.42 to 47 and proven by `s7-build1.console` l.1236, 1243, 1249 (`rpw-build1-errors.txt`); `ring-product CONFIG_RING_RHW_SIM is off` (`s7-full1.console` l.29309). Section 6 of `recorder-notes.md` (l.139 to 150): every board item present; the cell model is a stand-in |
| B7 Safety rules | PASS | one mic-rail call, `rrec_mics.c:53` (`log-safety-stages.txt`); no start path in the step 6 parts (hits 0); no new input path: `# CONFIG_INPUT is not set` (`s7-build2.console` l.1371), no gpio-keys object in the ring stage, no input callback in the sources (`b7-input-paths.txt`); no pin by number outside the board files: one hit, a comment in `tests/core/src/test_gesture.c:279` (`b7-raw-pins-code-only.txt`); test switches: none set in `prj.conf`, the ring `.conf` or the defconfig, each defaults off (`b7-test-switches.txt`, `b7-test-switch-defaults.txt`); the run's `.config` check covers RHW_SIM and the recorder hooks only |
| B8 Honesty | FAIL | the proven statements I tested match the log (48 stage ends, none other than exit 0; l.29309, 28967, 28968; `ring-ram` copies equal: `b8-claim-checks.txt`); unproven items are said (no ring, no panel driver, cell model, power file off: README l.77 to 80). But README l.96 contradicts the log (S7-05), the rails left dead are not said (S7-06), board-notes l.189 claims more than the check sees (S7-03), the debug signing key is not said (S7-07) |

### B4 pairs (FW 8.1 l.864 to 890, 8.7 l.988 to 997; devicetree `ringrec_nrf54lm20a_cpuapp.dts`)

| Setting | Specification | Devicetree |
|---|---|---|
| bus, speed, address | i2c22, 400 kHz, 0x6B (l.864) | `&i2c22`, `I2C_BITRATE_FAST`, `pmic@6b` (l.311, 313, 318 to 320); the macro's value was not read here |
| compatible | MFD TO CONFIRM; charger `nordic,npm1304-charger` (l.864, 876) | `nordic,npm1304` (l.319), `nordic,npm1304-charger` (l.366); both bindings exist (`s7-explore3.console` l.102, 276) |
| host-int-gpios | P1.28 active high (l.865) | `<&gpio1 28 GPIO_ACTIVE_HIGH>` (l.321) |
| pmic-int-pin | 0 (l.866) | 0 (l.322) |
| ship-to-active-time-ms | 96 (l.867) | 96 (l.323) |
| BUCK1 | 1,800,000, boot on, always on, AUTO (l.868, 869) | l.330 to 335 |
| BUCK2 | 3,000,000, boot on, always on, AUTO (l.870, 871) | l.340 to 345 |
| LDSW1 VDD_MIC | LDSW mode, 25,000, active discharge, off at boot (l.872, 873) | l.350 to 353 |
| LDSW2 VDD_SD | LDSW mode, 50,000, active discharge, off at boot (l.874, 875) | l.358 to 361 |
| term-microvolt | 4,350,000 (l.877) | 4350000 (l.367) |
| current-microamp | 15,000 (l.878) | 15000 (l.369) |
| term-current-percent | 10 (l.879) | 10 (l.370) |
| trickle-microvolt | 2,900,000 (l.880) | 2900000 (l.371) |
| vbus-limit-microamp | 500,000 (l.881) | 500000 (l.372) |
| thermistor-ohms, beta | 10,000, 3,380 (l.882) | 10000, 3380 (l.373, 374) |
| cold, cool, warm, hot | 0, 10,000, 40,000, 45,000 (l.883 to 886) | 0, 10000, 40000, 45000 (l.375 to 378) |
| term-warm-microvolt | 4,100,000 (l.887) | 4100000 (l.368) |
| charging-enable | on (l.888) | `charging-enable` (l.381) |
| dietemp stop, resume | 90,000, 80,000 (l.889) | 90000, 80000 (l.379, 380) |
| battery discharge limit | none, fixed in the chip (l.890, l.988) | no property set (binding: const 125000, S7-08) |
| power-fail warning | off, reset value (l.997) | no property set |

Not expressible in the devicetree, so NOT PROVEN here: charger off before writing the current (l.894), the reset causes read at boot (l.996), ship-mode entry steps (8.4).

## Findings

| Id | Severity | File:line | Specification or netlist line | What is wrong |
|---|---|---|---|---|
| S7-01 | major | `tools/build_all.sh:517`, `:555`, `:577`; `tools/check_ring_pins.py:216` to `:227` | bar B2 | The copy `boards/ringrec/netlist.csv` can drift silently. The source comparison runs only when `design/ecad/ring/netlist.csv` exists; on the build server it does not (`s7-full1.console` l.29515, "the copy's sha256 above is the one checked", against no expected value); the broken-copy stage passes no `--source-netlist`; no other script compares them (`b2-drift-checkers.txt`). A missing or mistyped source path also passes. |
| S7-02 | major | `boards/ringrec/ringrec_nrf54lm20a_cpuapp-pinctrl.dtsi:33` to `:40`, `:22` to `:24`; `ringrec_nrf54lm20a_cpuapp.dts:264` | `design/firmware.md` l.506 | FW 5.1 puts SD_CS among the lines that are inputs with no pull in the sleep state while VDD_SD is off. The board's `spi00_sleep` holds SD_SCK, SD_MOSI, SD_MISO only; SD_CS is a `cs-gpios` GPIO, outside every pin state. The comment in `pinctrl.dtsi` at l.23 says "every line". Whether the kit's SPI driver releases that GPIO on suspend or drives it high at boot is unverified (SDK source not read); nothing in `rst_hw_real.c` or `store-notes.md` handles SD_CS (`sd-cs-store.txt`). |
| S7-03 | minor | `tools/check_ring_pins.py:285` to `:294`, `:68` to `:75`, `:331` to `:335`, `:345`, `:306` to `:310`; `docs/board-notes.md:189` | bar B3 | Blind spots, from reading (not run): GPIO flags are printed, never compared (a joystick without pull-up or an active-low MOTOR passes); the 8 fixed-function pins come from the table's constants, not from the devicetree; the reverse scan sees only properties ending in `gpios` and pin-control states, and skips silently any property it cannot parse (a gpio hog), so analog inputs, NFC pads or hogs never give UNEXPECTED; a sleep state may lack a pin. Board-notes l.189 says it fails "on any pin an enabled node names". |
| S7-04 | minor | `tools/build_all.sh:594` to `:599` | bar B3 | The three planted copies are all a wrong pin on the same port or a removed property. No copy plants a wrong port, a removed or disabled node, an extra pin (UNEXPECTED), an unknown net (UNLISTED) or a changed netlist. |
| S7-05 | minor | `firmware/README.md:96` | `s7-full1.console` l.29311 to 29408 | Says the real driver files "build only for the development kit"; the ring build compiles 8 real files. |
| S7-06 | minor | `firmware/README.md:77` to `:80`; `docs/board-notes.md:148` to `:158` | `modules/ring_rhw/src/rhw.c:36`; `dts` l.353, 361 | With `CONFIG_RING_POWER_REAL=n` the only power ops are rhw.c's `none_rail_set`, which returns -ENODEV; VDD_SD and VDD_MIC are off at boot, so this image never powers the card or the microphones. Neither file says so. |
| S7-07 | minor | ring build, `s7-full1.console` l.27986 | `design/firmware.md` l.1013 | MCUboot is signed with the default debug key ("this file is for debug use only and is not secure"); the signature check of 9.2 then protects nothing. Already there in the kit build (`s7-full1.console` l.73). Not said in README or board-notes (`signing-key-mentions.txt`: 0 and 0). |
| S7-08 | note | `s7-explore3.console` l.302 to 307 | `design/firmware.md` l.988 | The kit's binding says the nPM1304 discharge limit is fixed to 125 mA; FW 8.7 says IBATLIM 100 mA minimum. Not settable; for the specification's owner. |
| S7-09 | note | `boards/ringrec/ringrec_nrf54lm20a_cpuapp.dts:247` to `:254` | `design/firmware.md` l.1061 (per board-notes l.36) | `uart20` console on: a development build. The author states it as open (board-notes l.36 to 38). |

Counts: blocker 0, major 2, minor 5, note 2.

## What I could not check

- Running `check_ring_pins.py` on planted copies (wrong port, missing node, extra pin, changed netlist): no dtlib and no `nrf-pinctrl.h` on the Mac (`local-dtlib.txt`); the build server is out of bounds.
- The built `zephyr.dts`, so SoC nodes the board leaves at their defaults (for example NFC pads, analog inputs) are unverified.
- The kit's SPI driver behaviour for the CS GPIO on suspend and at boot (S7-02); the value of `I2C_BITRATE_FAST`; the chip's own LFXO pins (taken from FW l.87, as the author also says).
- Anything on a ring.

Verdict: FAIL. No blocker; 2 majors open (S7-01, S7-02). Bar lines: 5 of 8 PASS (B1, B4, B5, B6, B7), B2 and B8 FAIL, B3 NOT PROVEN.

RESULT: done, FAIL: pins and power chip settings match the netlist and specification, but the netlist copy can drift silently (S7-01) and the SD_CS sleep state differs from FW 5.1 (S7-02).
