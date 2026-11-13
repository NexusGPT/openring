# Bench prototype plan

Version B2, 2026-11-12. It replaces version B1 of 2026-11-10 (kept beside it as `design/bench/bench-plan-B1.md`). Basis: the ring files at commit bf21943 (`design/architecture.md` 17.13 to 17.31, `design/firmware.md`, `design/bom.csv`, `design/ecad/motor-drive/motor-drive.md`). It closes finding H09 of `design/review/design-review-3.md`.

Written to be built by the owner or by a partner without change (owner, 2026-11-10: "I will decide later if I build it or a partner does. At the end of the day, it shoul dbe the same"). Bar (owner): "There should be no ambiguity to build it 100%". What cannot be written without ambiguity is listed in section 9 with its measured cause; nothing else is left open.

How to read the status words. **confirmed** = the order code is printed in the cited source and the cited source is saved under `design/` (the saved page copies carry their read time in `design/bench/logs/fetch_all.log`, UTC). **not confirmed** = no saved source prints a seller's order code; the ring's maker part number is then the only name given and the builder asks the maker or a distributor. Prices and stock are in `design/bench/bench-kits.md`; they are not repeated here.

## 1. What the bench build is, and what it proves

A table-top recorder made from development kits, three small carrier boards (section 4.1) and jumper wires. It has no ring shape. It runs the ring's own power chip family (nPM1304), microphones, motor, motor regulator and a screen on Nordic's development kit. It answers these questions before any custom board is paid for:

| Question | Test (section 5) |
|---|---|
| Do the rails and the joystick wiring come up as designed? | T0 |
| Is the speech quality as good as a Plaud recorder's? | T1 |
| How much current does recording take, with the always-lit recording sign? | T2 |
| Do the controls behave as designed? | T3 |
| Does the screen show the recording sign before the microphones get power, and does no state record with the screen dark? | T4 |
| Does the motor stay out of the power chip's battery limit? | T5 |
| Does the storage path meet its speed lines? | T6 |
| Are both microphones alive and in the right channels? | T7 |

The recording light is removed from the ring (v7, `design/architecture.md` 17.30; `design/firmware.md` 3.2). This plan wires no recording light and tests none. The sign that a recording runs is the screen (test T4).

## 2. Parts map: what to buy, and what each item stands in for

One row per ring part. "Ring part (bom.csv)" is the maker part number in `design/bom.csv`, column maker_part_number, on the line of the ring reference given. "Code source" is the saved file that prints the order code.

| # | Role | Ring ref | Ring part (bom.csv) | Bench item | Maker | Order code | Status | Choice source | Code source |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Main chip | U1 | NRF54LM20A-CAAA-R7 | nRF54LM20 DK, built for board target nrf54lm20dk/nrf54lm20a/cpuapp (the A chip rules on the DK) | Nordic | NRF54LM20-DK | confirmed | design/bom.csv line 2; design/bench/bench-kits.md section 1; design/bench/sources/zephyr_nrf54lm20dk_board.txt ("Nordic does not offer a development kit for the nRF54LM20A") | design/bench/bench-kits.md |
| 2 | Current meter | none | none | Power Profiler Kit II | Nordic | nRF-PPK2 | confirmed | design/bench/bench-kits.md section 1 | design/bench/bench-kits.md |
| 3 | Power chip | U2 | nPM1304-CAAA-R7 | nPM1304 EK evaluation kit | Nordic | nPM1304-EK | confirmed | design/architecture.md line 644 and 17.18; design/ecad/motor-drive/motor-drive.md section 2.9; design/bom.csv line 3 | design/datasheets/npm1304_datasheet_v1_0.txt |
| 4 | Microphones (2) | U5, U6 | SPK0641HT4H-1 | the ring's part itself, two pieces, soldered on carrier CB-MIC (no maker evaluation board found) | Knowles | SPK0641HT4H-1 | not confirmed | design/bom.csv line 9; design/mech/mic-path/mic-path.md line 32 ("the reel suffix and the distributor code are not confirmed") | none |
| 5 | Vibration motor | M1 | W0525AB001D | the ring's part itself, two lead wires | Jinlong Machinery | W0525AB001D | not confirmed | design/bom.csv line 44; design/architecture.md 17.16 | none |
| 6 | Motor regulator | U11 | TLV75530PDQNR | the ring's part itself, soldered on carrier CB-MOT | Texas Instruments | TLV75530PDQNR | confirmed | design/bom.csv line 45; design/ecad/motor-drive/motor-drive.md section 2.2 | design/ecad/motor-drive/src_tlv755p.txt |
| 7 | Joystick switches (5: up, down, toward the hand, toward the fingertip, centre) | SW1, SW3, SW4, SW5, SW2 | SKTAAAE010 | 5-way navigation switch, one body with five switches (the ring's five switches are separate parts under a round cap) | Adafruit (switch family Alps SKQU) | 504 | confirmed | design/bom.csv lines 39 and 40; design/architecture.md 17.11 and 17.29 | design/bench/sources/adafruit_504.txt |
| 8 | Screen | DISP1 | TOH095XVT-01 | 0.95 inch RGB OLED module, 96 x 64, SSD1331, SPI (the ring's panel cannot run on the bench today: its start-up code is open, architecture 12.1) | Waveshare | 10507 | confirmed | design/bom.csv line 10; design/architecture.md 17.30; design/bench/bench-kits.md section 4 | design/bench/sources/waveshare_oled095_a.txt |
| 9 | Storage | U3 | CSNP32GCR01-BOW | microSD card breakout with its own level shifter (the ring's SD NAND has no breakout) | Adafruit | 254 | confirmed | design/bom.csv line 6; design/bench/bench-kits.md section 5 | design/bench/sources/adafruit_254.txt |
| 10 | Storage and screen level shifters (2 pieces) | U10 | SN74AXC4T774RSVR | TXB0108 8-channel level converter breakout, one for the storage lines (called LS-SD) and one for the screen lines (called LS-LCD) | Adafruit | 395 | confirmed | design/bom.csv line 7; design/architecture.md 17.14 | design/bench/sources/adafruit_395.txt |
| 11 | Reference device | none | none | Plaud NotePin (the device to beat) | Plaud | not confirmed | not confirmed | requirements.md section 4; design/bench/bench-kits.md section 8 | none |

Items with no order code (instruments and small parts, fixed by their values):

- microSD card for row 9: SDHC, 8 GB to 32 GB, any maker.
- Resistors: 2 pieces 4.7 kohm 1 % (R57, R58 of the ring); 1 piece 100 ohm and 1 piece 100 kohm for carrier CB-MOT (R61, R62); 2 pieces 100 ohm for carrier CB-MIC (R31, R32); for T5 only: 1 ohm and 3 ohm, 2 W each, and one 0.5 ohm 1 % 1 W shunt (motor-drive.md section 2.9).
- Capacitors: 4 pieces 10 uF X5R 6.3 V (C83, C84 on CB-MOT, spares); 2 pieces 1 uF X5R 6.3 V (C31, C32 on CB-MIC); 2 pieces 100 nF C0G or NP0 (C35, C36 on CB-MIC; `design/bom.csv` line 37: the ring's part is not chosen).
- Logic analyser: 8 channels, 100 MS/s or faster, input range covering 1.8 V and 3.3 V (T4).
- Oscilloscope: 4 channels, 10 microseconds per point or finer (motor-drive.md section 2.9) (T5).
- Video camera: 60 frames per second or faster, fixed on the screen (T4).
- 3-axis accelerometer, 100 g block, foam (T5; as Jinlong's own test, motor-drive.md section 2.9).
- Adjustable DC supply 3.0 V to 4.4 V, 1 A or more (T5).
- A loudspeaker with a flat response for speech, a second loudspeaker for noise, and a sound level meter (T1).
- Jumper wires, breadboards, 0.1 inch headers.

Not bought: a battery cell. The ring's cell is a custom 4.35 V curved cell (`design/bom.csv` line 47); the saved listing of a 40 mAh cell is 3.70 V nominal (`design/bench/bench-kits.md` section 7) and the 4.35 V charge setting of the ring would overcharge a cell rated for 4.2 V. The Power Profiler Kit II stands in for the cell (T2, T5). Charging is not tested (section 8).

## 3. Where the bench differs from the ring (each a fixed choice)

| # | Ring | Bench | Why, and source |
|---|---|---|---|
| D1 | VDD_3V0 is 3.0 V (design/bom.csv line 5: 150 kohm gives 3.0 V) | EK buck 2 is set to 3.3 V after T0 has read 3.0 V | Both breakouts (rows 8, 9) are specified for 3.3 V to 5 V supply (design/bench/sources/waveshare_oled095_a.txt "3.3V / 5V"). The motor regulator and the microphones do not see this rail |
| D2 | Screen and storage lines run at 1.8 V into a 1.8 V screen and, through U10, into a 3.0 V storage part | The DK's I/O rail is 1.8 V at start-up (DK schematic sheet 6 note: "Startup VOUT1: 47k -> 1.8V"); the breakouts need 3.3 V logic, so each line passes a TXB0108 breakout (row 10) | design/bench/sources/dk_sch_p6-06.png; the ring's U10 is a one-way part with Hi-Z ports below 100 mV on VDD_SD (design/bom.csv line 7), the TXB0108 is not (section 8) |
| D3 | The cell feeds VBAT | The Power Profiler Kit II in source mode at 3.8 V (the voltage the design uses, design/firmware.md section 8.5) feeds VBAT | A 4.35 V cell is not on sale in the saved listings (section 2) |
| D4 | The main chip is the nRF54LM20A in package CAAA | The DK carries the nRF54LM20B; the board target nrf54lm20dk/nrf54lm20a/cpuapp applies the A chip's limits on that kit | design/bench/sources/zephyr_nrf54lm20dk_board.txt |
| D5 | The DK's chip is powered by the ring's buck 1 | The DK keeps its own power chip (nPM1300 on the DK, USB powered); its I/O rail is VDD_1V8 for the bench | design/bench/sources/dk_sch_p6-06.png and dk_sch_p4-04.png ("DK requires power from USB connector" in default configuration) |
| D6 | Switches are five separate Alps SKTAAAE010 under one round cap | One 5-way switch body | Logic and timing only; the feel (force, travel) is not represented (section 8) |
| D7 | Screen is the AMOLED TOH095XVT-01 with the SH8501A driver, 120 x 240 | OLED 96 x 64 with the SSD1331 driver | The ring's start-up code is open (architecture 12.1) |
| D8 | Microphones sit under the board and hear through the floor | Microphones sit on carrier CB-MIC with the port open to the room | The sound path is bench B7 on the first housing (architecture 17.19) |

## 4. Wiring

Signal names are the ring's own net names (`design/ecad/ring/netlist.csv`); chip pins are the ring's (`design/architecture.md` 16.6 and the netlist). A pin written `DK P2-14 [P1.13]` means header P2 of the DK, pin 14, which carries chip pin P1.13 (DK schematic sheet 8, saved as `design/bench/sources/dk_sch_p8_P1P2-08.png`; pin n of header P1 is P0.(n-3); of P2, P1.(n-3); of P3, P1.(n+13); of P4, P2.(n-3) with the _A nets; of P5, P3.(n-3); pins 1, 2, 19, 20 of P1 to P5 are VDD:IO). The DK has no ground pin on those headers: use the pin named GND on header P17 (sheet 8, saved as `design/bench/sources/dk_sch_p8_P17top-08.png`) or the test points TP15 to TP20.

An nPM1304 pin is written with its ball from `design/ecad/ring/npm1304-balls.csv` (for example VOUT1 ball B6). The EK brings every PMIC pin to a male header (design/bench/bench-kits.md section 2); the label printed beside each header on the EK is not confirmed in any saved file (section 9, point 1).

### 4.1 Carrier boards (three small boards; any builder makes them from these netlists)

Carrier CB-MIC (microphones; netlist from `design/ecad/ring/netlist.csv`, pins from `design/bom.csv` line 9: pin 1 DATA, 2 CLOCK, 3 SELECT, 4 Vdd, 5 to 8 GROUND; package outline and pads from the Knowles sheet in `design/mech/mic-path/datasheets/knowles-spk0641ht4h-1_chipsmall.pdf`, sheets 2 and 4):

| Part | Pin | Net |
|---|---|---|
| U5 | 1 DATA | through R31 (100 ohm) to MIC_A_DATA |
| U5 | 2 CLOCK | MIC_A_CLK |
| U5 | 3 SELECT | GND (left channel) |
| U5 | 4 Vdd | VDD_MIC, with C31 (1 uF to GND) and C35 (100 nF C0G to GND) at the pin |
| U5 | 5, 6, 7, 8 | GND |
| U6 | 1 DATA | through R32 (100 ohm) to MIC_A_DATA |
| U6 | 2 CLOCK | MIC_A_CLK |
| U6 | 3 SELECT | VDD_MIC (right channel) |
| U6 | 4 Vdd | VDD_MIC, with C32 (1 uF to GND) and C36 (100 nF C0G to GND) at the pin |
| U6 | 5, 6, 7, 8 | GND |
| J-MIC | 1, 2, 3, 4 | VDD_MIC, GND, MIC_A_CLK, MIC_A_DATA |

Carrier CB-MOT (motor regulator; netlist from `design/ecad/motor-drive/motor-drive.md` section 2.1; U11 pins from TI's pin table: OUT 1, GND 2, EN 3, IN 4):

| Part | Pin | Net |
|---|---|---|
| U11 | 1 OUT | VMOT, with C84 (10 uF to GND) |
| U11 | 2 GND and thermal pad | GND |
| U11 | 3 EN | MOT_EN; R61 (100 ohm) from MOTOR to MOT_EN; R62 (100 kohm) from MOT_EN to GND |
| U11 | 4 IN | VBAT, with C83 (10 uF to GND) |
| J-MOT | 1, 2, 3, 4, 5 | VBAT, GND, MOTOR, VMOT, GND |

The motor's red lead goes to J-MOT 4 (VMOT) and its blue lead to J-MOT 5 (GND) (motor-drive.md section 2.1).

The switch body, the screen module and the storage breakout are used as delivered; no carrier.

### 4.2 Wiring table (every connection between kits)

Names used in the table: DK = nRF54LM20 DK (row 1); EK = nPM1304 EK (row 3); PPK2 = Power Profiler Kit II (row 2); CB-MIC and CB-MOT = the carriers of section 4.1; OLED = the Waveshare module (row 8), pins by its own numbers 1 to 8; SDB = the Adafruit 254 microSD breakout (row 9); LS-SD and LS-LCD = the two Adafruit 395 converters (row 10), side A on the 1.8 V rail and side B on the 3.3 V rail; NAV = the Adafruit 504 switch (row 7).

| # | Ring net | From (kit, pin) | To (kit, pin) | Note |
|---|---|---|---|---|
| 1 | VBAT | PPK2 source output VOUT | EK battery input, PMIC pin VBAT (balls D1, D2) | polarity from the EK board (section 9, point 1) before any voltage is applied |
| 2 | VBAT | PPK2 source output VOUT | CB-MOT J-MOT 1 | the same node as row 1, upstream of the EK, as in the ring (motor-drive.md section 2.1) |
| 3 | GND | PPK2 GND | EK GND | |
| 4 | GND | EK GND | DK P17 GND | one common ground for every kit and carrier |
| 5 | VDD_1V8 | DK P1-1 (VDD:IO) | LS-SD VA; LS-LCD VA; R57 pin 2; R58 pin 2 | 1.8 V from the DK's own power chip (D2, D5) |
| 6 | VDD_1V8 | EK PMIC pin VOUT1 (ball B6) | EK PMIC pin LSIN1 (ball B4) | as in the ring: LSIN1 on VDD_1V8; VOUT1 set to 1.8 V |
| 7 | VDD_3V0 | EK PMIC pin VOUT2 (ball C6) | EK PMIC pin LSIN2 (ball B5) | VOUT2 3.0 V in T0, 3.3 V afterwards (D1) |
| 8 | VDD_3V0 | EK PMIC pin VOUT2 (ball C6) | OLED VCC (pin 1); LS-LCD VB | |
| 9 | VDD_MIC | EK PMIC pin LSOUT1 (ball A4) | CB-MIC J-MIC 1 | load switch 1, enabled by firmware only (T4) |
| 10 | VDD_SD | EK PMIC pin LSOUT2 (ball A5) | SDB pin 5V (supply input); LS-SD VB | load switch 2 |
| 11 | PMIC_SDA | DK P3-13 [P1.26] | EK PMIC pin SDA (ball E5); R57 pin 1 | 4.7 kohm pull-up to VDD_1V8 |
| 12 | PMIC_SCL | DK P3-14 [P1.27] | EK PMIC pin SCL (ball E3); R58 pin 1 | 4.7 kohm pull-up to VDD_1V8 |
| 13 | PMIC_INT | DK P3-15 [P1.28] | EK PMIC pin GPIO0 (ball D6) | |
| 14 | VDD_1V8 | DK P1-1 (VDD:IO) | EK PMIC pin VDDIO (ball E4) | as in the ring (VDDIO on VDD_1V8); how the EK ties VDDIO is not read (section 9, point 2) |
| 15 | MIC_A_CLK | DK P2-16 [P1.13] | CB-MIC J-MIC 3 | 1.280 MHz PDM clock |
| 16 | MIC_A_DATA | DK P2-14 [P1.11] | CB-MIC J-MIC 4 | |
| 17 | GND | EK GND | CB-MIC J-MIC 2 | |
| 18 | SD_SCK | DK P4-4 [P2.01] | LS-SD A1 | |
| 19 | SD_MOSI | DK P4-5 [P2.02] | LS-SD A2 | |
| 20 | SD_CS | DK P4-8 [P2.05] | LS-SD A3 | same channel order as the ring's U10 (A3 = SD_CS) |
| 21 | SD_MISO | DK P4-7 [P2.04] | LS-SD A4 | A4 = SD_MISO |
| 22 | SD_SCK | LS-SD B1 | SDB CLK | |
| 23 | SD_MOSI | LS-SD B2 | SDB DI | |
| 24 | SD_CS | LS-SD B3 | SDB CS | |
| 25 | SD_MISO | LS-SD B4 | SDB DO | |
| 26 | LCD_SCK | DK P2-6 [P1.03] | LS-LCD A1; LS-LCD B1 to OLED CLK (pin 5) | |
| 27 | LCD_MOSI | DK P2-7 [P1.04] | LS-LCD A2; LS-LCD B2 to OLED DIN (pin 4) | |
| 28 | LCD_CS | DK P2-8 [P1.05] | LS-LCD A3; LS-LCD B3 to OLED CS (pin 6) | |
| 29 | LCD_DCX | DK P2-9 [P1.06] | LS-LCD A4; LS-LCD B4 to OLED D/C (pin 7) | |
| 30 | LCD_RST | DK P2-10 [P1.07] | LS-LCD A5; LS-LCD B5 to OLED RES (pin 8) | |
| 31 | OLED_PWR_EN | DK P3-16 [P1.29] | logic analyser channel 3 only | the ring's pin AVDDEN of U4 has no counterpart on the module (section 8) |
| 32 | LCD_TE | DK P3-9 [P1.22] | not wired | the SSD1331 module has no TE pin |
| 33 | GND | EK GND | OLED GND (pin 2); SDB GND; LS-SD GND; LS-LCD GND; NAV common | |
| 34 | BTN_REC | DK P1-7 [P0.04] | NAV centre pin | switch to GND, internal pull-up on (design/firmware.md section 2.1) |
| 35 | JOY_UP | DK P1-9 [P0.06] | NAV up pin | switch SW1 |
| 36 | JOY_DOWN | DK P1-10 [P0.07] | NAV down pin | switch SW3 |
| 37 | JOY_LEFT | DK P1-11 [P0.08] | NAV left pin (toward the hand) | switch SW4 |
| 38 | JOY_RIGHT | DK P3-18 [P1.31] | NAV right pin (toward the fingertip) | switch SW5 |
| 39 | MOTOR | DK P5-4 [P3.01] | CB-MOT J-MOT 3 | |
| 40 | VBAT, VMOT, GND | CB-MOT J-MOT 1, 4, 5 | PPK2 VOUT; motor red lead; motor blue lead | rows 2 and section 4.1 |
| 41 | JOY_CENTER (P0.03) | DK P1-6 | not wired | the ring leaves this pin unused (design/firmware.md section 2.2) |
| 42 | PMIC loads | EK PMIC pin LSOUT1 | logic analyser channel 4 | T4 |
| 43 | MIC_A_CLK, MOTOR | CB-MIC J-MIC 3; CB-MOT J-MOT 3 | logic analyser channels 5 and 6 | T4 |

Logic analyser channels for T4: 1 = LCD_CS, 2 = LCD_DCX, 3 = OLED_PWR_EN, 4 = VDD_MIC, 5 = MIC_A_CLK, 6 = MOTOR.

Navigation switch pin order (row 34 to 38). The saved Alps sheet for the similar part SKQUCAA010 (`design/bench/sources/SKQUCAA010-ALPS.txt`, circuit diagram) gives: pin 1 = A (up), 2 = B (left), 3 = C (down), 5 = D (right), 6 = centre, 4 = common. Adafruit calls part 504 "a similar part" (`design/bench/sources/adafruit_504.txt`), so the pin order of the delivered body is read by continuity in T0 step 3 before the five switch wires are soldered.

Pins the DK shares with its own parts (from DK schematic sheet 2, sheet 4 and the DK's devicetree, `design/bench/sources/zephyr_nrf54lm20dk_common.dtsi` and `zephyr_nrf54lm20dk_a_b_pinctrl.dtsi`):

| Ring net | DK chip pin | DK part on the same pin | Bench rule |
|---|---|---|---|
| PMIC_SDA | P1.26 | push button 0 | devicetree: node button0 disabled |
| PMIC_SCL | P1.27 | LED 2 | node led2 disabled |
| PMIC_INT | P1.28 | LED 3 | node led3 disabled |
| JOY_UP, JOY_DOWN, JOY_LEFT | P0.06, P0.07, P0.08 | UART 30 of the DK's debugger port (analog switches, sheet 4) | node uart30 disabled; idle level checked in T0 step 4 |
| SD_SCK, SD_MOSI, SD_MISO, SD_CS | P2.01, P2.02, P2.04, P2.05 | the DK's on-board QSPI flash lines (names _A on sheet 8) | the on-board flash node is not enabled |

## 5. Tests (each pass line comes from a current design file)

The column "Quote from source" is a verbatim piece of the cited file, checked by `design/bench/check_bench.py`. Several quotes in one cell are separated by " ~ ".

| ID | Test | Method | Pass line | Source (file and section) | Quote from source |
|---|---|---|---|---|---|
| T0 | Rails and joystick | 1. Power the DK from its debugger USB connector. 2. Set the EK to VOUT1 1.8 V and VOUT2 3.0 V (nPM PowerUP app), read both on a meter, then set VOUT2 to 3.3 V (D1). 3. With the 5-way switch alone on the bench, find by continuity which of its pins closes to the common pin for each of up, down, left, right and centre; solder the five wires to the rows 34 to 38 pins. 4. With the joystick wired and nothing pressed, read the five GPIO levels in the bench firmware | VOUT1 reads 1.8 V and VOUT2 reads 3.0 V at the ring's settings (a reading more than 5 percent off is a fail [CHOICE: no tolerance is written in the design files]); five distinct switch pins found, each closing to common only while its direction or the centre is pressed; all five GPIO levels read high when nothing is pressed | design/bom.csv line 4 and line 5 (power chip VSET1 and VSET2); design/firmware.md section 2.2 | 47 kohm gives 1.8 V, 150 kohm gives 3.0 V ~ Debounce 20 ms (`gpio-keys`), one event per press |
| T1 | Speech quality against the Plaud | section 7 | The word error rate of the bench recorder is equal to or below the Plaud's at 1 m and at 3 m, in each of the three noise levels of section 7 (the requirement names no noise level; applying it at every level is stricter [CHOICE]) | requirements.md section 4 | error rate equal to or below the Plaud at 1 m and 3 m with the hand on the table |
| T2 | Recording current, with the always-lit recording sign | Run R-A: PPK2 in source mode at 3.8 V on the EK battery input (rows 1 to 3), bench firmware recording 2 channels, 16 kHz, 16 bit for 60 s, average of the last 50 s, three states in turn: S0 screen blanked (measurement build only, never in the ring build), S1 SCR_REC_DIM (red dot and timer, lowest brightness), S2 SCR_RECORDING. Run R-B: the same three states with the PPK2 in ampere meter mode at DK header P14 (the jumper removed from P14), which gives the main chip's current at 1.8 V. Cell current = R-A + R-B x 1.8 / (3.8 x 0.9) (the conversion the design uses in firmware.md section 8.5) | Today's design figure is 4.1 mA from the cell (firmware.md 8.5), which counts the removed light's 1.5 mA; without it the computed figure is 2.6 mA (4.1 - 1.5, firmware.md 8.5). The always-lit sign has no measured figure yet: this test measures it as I(S1) - I(S0) and I(S2) - I(S0) and records both with no pass line. The 4.1 mA excludes the screen (firmware.md 8.5), so the sign is the new part of the sum. Pass: the cell current in S1 is 4.1 mA or less, so that the hours of firmware.md 8.5 stay valid (this reading of the pass line is a [CHOICE]: the design files give the figure and the rule that it is kept until a bench result exists, not a pass line). Above it, the hours of firmware.md 8.5 and architecture 17.26 are recomputed from the measured value. The result on the stand-in OLED (D7) is not the result for the ring's panel: S1 and S2 are run again on the TOH095XVT-01 before 4.1 mA is changed | design/firmware.md sections 8.5 and 3.2 | about 4.1 mA [CALC: 4.0 + 2 x (0.63 - 0.58)] ~ so without the light the computed recording figure is 4.1 - 1.5 = 2.6 mA [CALC] ~ Cost: a bench item, no number. ~ It excludes the motor (section 3.1) and the screen. |
| T3 | Controls | Bench firmware with the state machine of firmware.md section 1.2. 10 repetitions each: hold the centre 1.0 s in STANDBY; hold the centre 1.0 s in RECORDING; press the centre 40 to 450 ms in RECORDING; press the centre 200 ms twice 200 ms apart; press up, down, left, right once each; hold the centre 0.5 s and release; close a direction switch 20 ms before the centre and then hold the centre. Log the state, the MOTOR pin pulses and the GPIO events | A long press of 1.0 s starts a recording (motor pattern M1, one 80 ms pulse) and a second long press of 1.0 s stops it (M2, two 80 ms pulses 120 ms apart); a short press in RECORDING marks one highlight and starts no stop; a double press, a direction, and a release before 1.0 s change no state; the warning pulse MW (60 ms) sounds at 500 ms of a continuous centre hold; a direction closed 0 to 40 ms before the centre is dropped and the centre wins | design/firmware.md sections 2.1, 2.2 and 3.1 | Only a long press of the joystick centre starts or stops a recording. ~ 80 on, 120 off, 80 on ~ a direction switch that closed 0 to 40 ms before SW2 is dropped and the centre wins |
| T4 | The screen as the recording sign (replaces B1's test of the removed light) | Bench firmware with the real function order of rule R-SIGN: rec_mics_on() powers the screen, draws the red dot and the timer at 00:00:00 and enables load switch 1 (VDD_MIC) only after display_write() returned 0. Logic analyser channels 1 to 6 (section 4.2). Part a: 20 starts from STANDBY with the screen off, 20 with the screen on; for each start read the time from the last LCD_CS frame that holds the dot to the VDD_MIC rising edge. Part b: 10 starts with the bench flag that forces a draw failure at the start (measurement build only). Part c: two 1 s test recordings 1 s apart filmed at 60 frames per second or faster (procedure of T-SIGN). Part d: one recording left idle for 10 s after the last input, filmed. Part e: 10 stops; read the order of VDD_MIC falling and the screen leaving the recording pictures | Part a: in every start OLED_PWR_EN is high and a frame with the red dot was sent before VDD_MIC rises; at no logged time is VDD_MIC high while OLED_PWR_EN is low. Part b: VDD_MIC never rises, MOTOR plays M3 (three pulses), no recording opens. Part c: in every camera frame between VDD_MIC on and VDD_MIC off the red dot is lit; no such frame shows a dark screen. Part d: the screen dims to SCR_REC_DIM and the red dot and the timer stay lit. Part e: VDD_MIC falls before the screen may leave the recording pictures. Prerequisite, not part of the bench: the host test SIGN-1 of firmware.md 3.2 passes (one failing case fails the build) | design/firmware.md sections 3.2 and 9.3 | VDD_MIC on must mean OLED_PWR_EN high, the screen not blanked and the last frame holding the red dot pixels ~ A forced draw failure at the start must leave VDD_MIC off ~ in every camera frame between VDD_MIC on and VDD_MIC off the red dot is lit; no such frame shows a dark screen ~ The close turns VDD_MIC off before the screen may leave the recording pictures |
| T5 | Motor outside the power chip's battery limit | Wiring change for this test only: the battery node is an adjustable supply (3.30 V, 3.45 V, 4.35 V) through a series resistor of 1 ohm, then 3 ohm; the 0.5 ohm shunt between the battery node and the EK battery input; CB-MOT IN on the battery node upstream of the shunt; the motor taped to the 100 g block on foam with the accelerometer; the loads of motor-drive.md section 2.9 on the EK outputs. 1,350 patterns per supply voltage (each of M1, M2, M3, MH, MT, MW, MF 50 times, then M2 1,000 times); oscilloscope across the shunt | Chip path current at or under 80 mA at every point of every pattern, at all three supply voltages and both resistors. BCHGILIMSTATUS never reads 1 when polled during a pulse, no power-fail warning edge, and RSTCAUSE shows no new reset after the 1350 patterns. VMOT at or above 2.7 V while the motor runs, and the motor starts on every pattern. Vibration within 10 percent of the present drive at 3.30 V is dropped: the present drive no longer exists on the bench (the ring removed Q1) | design/ecad/motor-drive/motor-drive.md section 2.9 | Chip path current at or under 80 mA at every point of every pattern, at all three supply voltages and both resistors. ~ VMOT at or above 2.7 V while the motor runs, and the motor starts on every pattern (accelerometer). |
| T6 | Storage speed | VDD_SD on, init, write 65 sectors at LBA 4,096, read back, compare the CRC, time both, then delete the test data |  | design/firmware.md section 9.3 | data equal; write at least 0.5 MB/s; read at least 1.0 MB/s |
| T7 | Microphones | A 2 s test recording through the normal path while the loudspeaker plays 1 kHz; report the RMS level of each channel in dBFS and the count of identical consecutive samples; then tap only microphone 1, then only microphone 2 | the tested channel within 3 dB of the mean of the 2; no channel stuck (no run of 1,000 equal samples); tapping only mic n raises channel n first (this checks the channel map) | design/firmware.md section 9.3 | the tested channel within 3 dB of the mean of the 2; no channel stuck (no run of 1,000 equal samples) |

## 6. Firmware starting point

- Tool: Nordic's nRF Connect SDK (Zephyr). Board target `nrf54lm20dk/nrf54lm20a/cpuapp` (design/bench/sources/zephyr_nrf54lm20dk_board.txt). Power chip: the Zephyr shield `npm1304_ek` exists (design/bench/sources/zephyr_npm1304_ek_overlay.txt); its overlay attaches to the board's Arduino I2C bus, so the bench devicetree attaches the same node to the bus on P1.26 and P1.27 (rows 11, 12) instead.
- Start from four of the SDK's own samples, then join them: the digital microphone sample (PDM capture), the file system sample on an SD card over SPI, the nPM13xx sample, and the button sample. Sample names change between SDK versions: pick them in the SDK's sample browser. They were not opened for B2.
- Settings fixed by the design: microphone clock 1.280 MHz, ratio 80, 16 kHz, 16 bit, 2 channels, gain 0 dB (design/firmware.md section 4.1); raw file of 64,000 bytes per second (design/firmware.md section 4.3); behaviour and states from design/firmware.md; recording sign by rule R-SIGN (design/firmware.md section 3.2).
- Order of work: (1) record 10 seconds from 2 microphones to memory and send it over USB; (2) write the stream to the card; (3) add the joystick rules and the screen with the red dot and the timer, and the R-SIGN order of rec_mics_on(); (4) add the power chip and the motor; (5) run T4, then T2.

## 7. Test against the Plaud (T1)

Method taken from published sources (design/bench/bench-kits.md section 9): the LibriSpeech test-clean corpus (licence CC BY 4.0), the Whisper speech-to-text model (MIT licence), the jiwer scoring tool (Apache-2.0), and the two distances and three noise levels that Plaud itself publishes for its chamber test.

1. Take 50 sentences from LibriSpeech test-clean, the same 50 for every run.
2. Play them from the loudspeaker. Set the speech level once, at 1 m, with the sound level meter, and write the value down.
3. Put the bench microphones and the Plaud side by side. Record both at the same time.
4. Six conditions: 1 m and 3 m, each at three noise levels: quiet (about 35 dB), moderate (about 55 dB), loud (about 70 dB). Noise comes from a second loudspeaker playing recorded office noise.
5. Export both recordings. Transcribe both with the same Whisper model. Score each against the corpus text with jiwer.
6. Result table: 6 rows, word error rate of the bench and of the Plaud, and the difference. Pass line: T1 in section 5.

- The bench recording is 2 raw channels. Score channel 1 alone first, then the two channels combined toward the loudspeaker.
- The bench has no hand and no ring shape: the three hand positions of the requirement are not run (section 8).
- Plaud's export format (MP3 or WAV, sample rate) is not confirmed: its support page refused automated reading. Note what the device exports on the day (section 9, point 5).

## 8. What the bench build does not cover

- The ring's panel: the always-lit sign's current on the TOH095XVT-01 and its SH8501A start-up; the stand-in is an SSD1331 OLED (D7). T2 and T4 run again on the ring's panel when Tailor Pixels sends it with its start-up code (architecture 12.1).
- Whether the panel's supply is really off with OLED_PWR_EN low: the module has no enable pin; T4 only reads the pin.
- A panel that fails during use (design/firmware.md 3.2, "What is lost").
- The ring's one-way level shifter U10 (Hi-Z below 100 mV on VDD_SD) and the SD NAND CSNP32GCR01-BOW: the bench uses a microSD breakout behind two bidirectional converters.
- The feel and sealing of the ring's switches and cap (D6; bench B9).
- The microphones' sound path through the floor of the housing (bench B7), the ring's size, its antenna and the curved cell.
- Charging at 15 mA to 4.35 V and the cell's discharge limit (open item S12): no battery cell is on the bench.
- The nRF54LM20A die itself (D4) and the ring's rail arrangement (D5).
- The three hand positions of the requirement (requirements.md section 4).

## 9. Open points (each with its measured cause)

1. EK battery connector polarity and the label of each EK header: the user guide of the nPM1304 EK is behind a browser check (HTTP 403, Cloudflare page, `design/bench/logs/fetch_all.log` lines for nordic_ug_npm1304_ek_a.html and nordic_npm1304_ek.html). The EK side of the wiring is therefore given by PMIC pin and ball. Rule: read the polarity from the EK's printed marks and test with a meter against the battery connector before any voltage is applied.
2. How the EK supplies the PMIC's VDDIO and whether it has its own I2C pull-ups: same cause. The plan fits 4.7 kohm pull-ups and ties VDDIO to VDD_1V8 (rows 11, 12, 14); if the EK already ties it, row 14 is not fitted.
3. Seller order codes for the Knowles SPK0641HT4H-1 and the Jinlong W0525AB001D: no saved file prints one, and the distributor sites were not reachable from the build machine (`design/bench/logs/fetch_all.log`: HTTP 403 or no reply). The ring's own maker part number is the item.
4. The Power Profiler Kit II header names and the P14 pin that carries the chip supply are not read; the DK user guide is blocked (design/bench/bench-kits.md section 1). T2 run R-B uses the P14 set-up step quoted there ("Remove the jumper from the P14 header").
5. The Plaud export format: see section 7.
6. The sample names of the SDK: section 6.
