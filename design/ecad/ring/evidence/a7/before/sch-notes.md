# Ring schematic: notes

Contract: `design/architecture.md` version A5-draft (section 17 wins, then section 16 parts 16.4, 16.5, 16.6, then sections 7 and 14) and `design/bom.csv`. A6 (2026-11-10, later): sections 17.11, 17.12 and 17.13 are read too; section 11 lists the A6 changes. Designator list: frozen in `bom_refs_snapshot.csv` (96 electrical designators: bom.csv as on disk at 15:16 on 2026-11-10 plus R51 to R56 from the first read at 15:13). `check_netlist.py` checks against the snapshot and only prints the difference to the live bom.csv (not a failure).

## 1. Files and how to rebuild

All files are in `design/ecad/ring/`.

| File | What it is |
|---|---|
| `make_netlist.py` | writes the source tables below; every pin assignment is in this one file, with its source named next to it; the table `BAND_SPLIT` at its top says which flex tail carries which line |
| `netlist.csv` | source of truth: net, reference, pin_number, pin_name, pin_type (385 rows, 95 nets, 15 no-connect pins) |
| `parts.csv` | reference, symbol, value, maker part number, footprint name, sheet, dnp (116 parts) |
| `symbols.csv` | pins of each of the 27 part symbols (ring.kicad_sym adds PWR_FLAG: 28 symbols) |
| `additions.csv` | designators added against bom.csv (37), bom.csv designators not placed (20), test pads (22) |
| `bom_refs_snapshot.csv` | the frozen bom.csv designator list the check uses |
| `open-pins.csv` | every provisional pin number and every OPEN part number or order code (105 rows) |
| `gen_sch.py` | writes `ring.kicad_sym`, `ring.kicad_sch` (root), 8 sub-sheets `ring_<block>.kicad_sch`, `ring.kicad_pro`, `sym-lib-table` |
| `check_netlist.py` | the rules check; also exports KiCad's own netlist (`ring-kicad.xml`) and compares it with netlist.csv |
| `erc-report.txt`, `erc-report.json` | KiCad ERC output |
| `ring-schematic.pdf` | 9 pages: root plus 8 blocks, title block Rev A6 on each |
| `run_all.sh`, `prove_fail.sh`, `prove_a5.sh`, `render_pdf.py` | the run, the A3 failure proofs, the A5 failure proofs, the page renderer and text-overlap check |

Rebuild: `cd design/ecad/ring && ../../.venv/bin/python make_netlist.py && bash run_all.sh <tag>`.

Drawing style: each pin has a short wire stub to a global label carrying the net name; a pin left open carries a no-connect flag. A flex tail is not drawn as a wire: a band part and the tail pad that carries its line sit in the same net, and `check_netlist.py` (A5-9) proves every band part pin has a tail pad on its net. Footprint names are kept in the symbol field `Footprint_plan` (prefix `ring:`) and the KiCad `Footprint` field stays empty, because no footprint library is drawn yet (board step).

## 2. Block by block (A5)

**Main chip and radio (sheet 2).** Unchanged from A3. U1 nRF54LM20A CAAA, copied pin by pin from Nordic's CAAA reference schematic, configuration 1: VDD balls A4 and E10 on VDD_1V8 with C4, C5, C1, C2; DCC (A5) to L1 to DECD (A6) with C6; FB1 DECD to DECA (A8) and DECRF (B2) with C7, C14; DECUSB (H8) to C10 only; VBUS (H9) through R1 2.2 ohm with C11; TXRTUNE (G6) R2; X1 32 MHz, X2 32.768 kHz; antenna chain L2, C3, L3, C12, L4, C13 (not mounted), ANT1. Every signal ball of section 7 goes to its function; the 11 spare balls go to test pads; MIC_B_CLK (E6), MIC_B_DATA (D7) and JOY_CENTER (H4) go to test pads only (A5).

**Power (sheet 3).** U2 nPM1304 (A6, architecture 17.13) with the passives of the nPM1300 kit design C71 to C80, L71, L72, R71, R72, R57, R58, each marked in bom.csv 'to confirm against the nPM1304 product specification' (S18); no order code for U2. The cell BT1 and the thermistor RT1 moved to the band sheet (section 17.3): the nets VBAT and NTC reach them through J_BAND_B. SHPHLD to test pad TP19. CC1, CC2, GPIO1 to GPIO4, LED0 to LED2 are no-connect.

**Microphones (sheet 4).** U5 and U6 IM68D128B (pins CLOCK P1, VDD P2, GND P3, DATA P4, SELECT P5; numbers provisional). Both CLOCK on MIC_A_CLK (F1); DATA of each through its own 100 ohm (R31, R32) to MIC_A_DATA (F2); SELECT of U5 on ground, of U6 on VDD_MIC; each has 1 uF (C31, C32) and 100 nF (C35, C36) from VDD_MIC to ground.

**Storage (sheet 5).** U3 CSNP32GCR01-BOW, pads numbered as the maker table (spec V1.0 p5, section 2.1): 1 DAT2, 2 DAT3 = SDC_CS, 3 CLK = SDC_SCK, 4 VSS, 5 CMD = SDC_MOSI, 6 DAT0 = SDC_MISO, 7 DAT1, 8 VCC = VDD_SD. A6: the four bus lines no longer join the chip balls directly: U10 (SN74AXC4T774RSVR) carries SD_SCK (A9), SD_MOSI (B10), SD_CS (D9) from the 1.8 V side to the card side nets SDC_SCK, SDC_MOSI, SDC_CS and SDC_MISO back to SD_MISO (D10); see section 11, F07. 47 kohm pull-ups to VDD_SD on DAT0 (R60 on SDC_MISO), DAT1 (R63), DAT2 (R64), DAT3/CS (R65 on SDC_CS); C60 4.7 uF and C61 100 nF on VDD_SD (W3).

**Screen and its supply (sheet 6).** U4 SGM38046 and its passives as in A3. J1 Hirose FH35C-15S-0.3SHW(50), 15 positions P1 to P15; DISP1 the screen tail, contact k of the tail on position k of J1, contacts named in the order the table of `parts/slim.md` section 1.3 prints them: 1 ELVSS, 2 ELVDD, 3 MTP (open, printed "4"), 4 VCI = VDD_3V0 (printed "4" again), 5 IOVCC = VDD_1V8, 6 SWIRE, 7 TE = LCD_TE (D6), 8 RESX = LCD_RST (H5), 9 CS = LCD_CS (F7), 10 SCL = LCD_SCK (G9), 11 RS = LCD_DCX (G7), 12 SDA = LCD_MOSI (G8), 13 to 15 ground. Names VCI and RESX follow the Tailor table (A3 wrote VCC and RESET).

**Motor drive and recording light (sheet 7).** MOTOR (F6) through R61 100 ohm to the gate of Q1, R62 100 kohm gate to ground, Q1 source to ground, drain MOTOR_DRV; D1 cathode on VDD_3V0, anode on MOTOR_DRV. M1 is on the band sheet. Light (W5): VDD_3V0, R41 680 ohm, LED1, drain of Q2; Q2 source to ground, gate on VDD_MIC. No chip pin touches the light.

**Band (sheet 8).** A6: the split of lines between the two tails is the table `BAND_SPLIT` at the top of `make_netlist.py` (section 11, change e). J_BAND_A (joystick side, 8 pads): 1 UP (JOY_UP), 2 DOWN (JOY_DOWN), 3 LEFT (JOY_LEFT), 4 RIGHT (JOY_RIGHT), 5 CENTRE (BTN_REC), 6 MOT- (MOTOR_DRV), 7 MOT+ (VDD_3V0), 8 GND (GND). J_BAND_B (other tail, 7 pads): 1 CELL+ (VBAT), 2 CELL- (GND), 3 NTC (NTC), 4 VBUS (VBUS), 5 D- (USB_DN), 6 D+ (USB_DP), 7 GND (GND). Behind them: SW1 UP, SW3 DOWN, SW4 LEFT, SW5 RIGHT, each one SKTAAAE010 with terminal P1 on its line and P2 on ground; SW2 on BTN_REC is the switch under the centre of the joystick nub (architecture 17.11; there is no record button); M1 VC0720B088L, + on VDD_3V0, - on MOTOR_DRV; BT1 the curved cell, + on VBAT, - on ground; RT1 10 kohm NTC from NTC to ground, in the band at the cell; CP1 to CP4 the charging pads, VBUS, D-, D+, GND in order from -Y to +Y, on the inside face of the band (architecture 17.12). The pad order and pad numbers of the two tails are this schematic's own definition (not a maker pin).

**USB protection and test pads (sheet 9 of the PDF).** U9 TPD4E05U06 at the main board end of J_BAND_B: D1+ = USB_DP, D1- = USB_DN, D2+ and D2- both on VBUS, pins 3 and 8 ground, 6, 7, 9, 10 open. TP1 DBG_TX, TP2 DBG_RX, TP3 SWDCLK, TP4 SWDIO, TP5 NRESET, TP6 to TP16 the 11 spare pins, TP17 VDD_1V8, TP18 GND, TP19 SHPHLD, TP20 MIC_B_CLK, TP21 MIC_B_DATA, TP22 JOY_CENTER.

## 3. Values chosen and their basis

Unchanged from A3 except: IM68D128B parts keep W4's 100 ohm, 1 uF, 100 nF (Infineon datasheet p10 note of the A3 part; the IM68D128B datasheet is not on disk); charging pad 1.0 mm (17.3); BT1 value 4.35 V 20 to 26 mAh (17.3). All other values: see git history of this file or `evidence/a5/sch-notes_before.md` section 3.

## 4. Additions against bom.csv

Added designators (37), each with its reason in `additions.csv`: U9; CP1 to CP4; R61, R62; R63 to R65; C61; R66; C71 to C80; L71, L72; RT1; TP16 to TP19; J_BAND_A, J_BAND_B; SW3, SW4, SW5; U10, C81, C82 (A6). Test pads TP20 to TP22 are listed as test pads.

Not placed (bom.csv designators, 20): R51 to R56 (W1); CBL1 (no joystick cable); NPM-REF (placeholder); U7, U8, R33, R34, C33, C34, C37, C38 (2 microphones); W1 to W4 (contact wires: no contact board, the pads reach the board through J_BAND_B).

`make_netlist.py` copies maker part numbers from bom.csv where it names one (U5 and U6 read IM68D128BV01XTMA1 there). U2 has none on purpose (section 11, change a).

## 5. Open pins

`open-pins.csv` holds 105 rows: 101 provisional pin numbers and 4 rows for a part number or order code that is OPEN (L71, L72, RT1, the U2 order code):
- U2 nPM1304: 33 pins, every one (A6). The names are the nPM1300's from the DK schematic; the numbers P1 to P33 are placeholders, not balls (the CSP has 35 balls).
- J_BAND_A (8 pads) and J_BAND_B (7 pads): the pad order is this schematic's own definition (A6 lists them: the split is confirmed by the lead after the inside model).
- U5, U6 IM68D128B: 5 pins each. Names Clock, VDD, Ground, Data, Select as given in the brief; the IM68D128B brief (`datasheets/mic-research/im68d128b-brief.txt`) gives no pin table. P1 to P5 are placeholders.
- SW1 to SW5 SKTAAAE010: 2 terminals each (10 pins); the Alps spec KTA-601 (7 pages) gives no terminal numbers or drawing (open item S9).
- J1: 15 positions; Hirose FH35C-15S-0.3SHW(50) selected, its drawing not read; position k assumed = tail contact k.
- DISP1 pins 3 (MTP) and 4 (VCI): the Tailor table prints "4 MTP, 4 VCI" and no pin 3; order kept as printed.
- Q1, Q2 (G, S, D pad numbers), LED1 (anode, cathode), M1 (plus, minus and tail contact numbers: VC0720B088L has an FPC tail, no polarity printed), BT1 (tabs), X1, X2.
- Not provisional: U10 (pin numbers equal the RSV column of the TI table, check A6-7), U3 (maker table, A5-7).

## 6. ERC result

`kicad-cli sch erc --severity-all --exit-code-violations -o erc-report.txt ring.kicad_sch`: exit 0, "Found 0 violations" (log `evidence/a5/erc_cmd.log`). Power flags unchanged: PWR_FLAG on GND (power sheet) and on U1_VBUS (main sheet). A6 result: section 11, change (check 1).

## 7. Conflicts in the architecture (line numbers of `architecture.md` as read on 2026-11-10)

1. Line 290 (W13): "RT1 = 10 kilo-ohm thermistor on the main board beside the cell". Line 439 (17.3): "cell 2 plus its temperature sensor 1" on the flex tail. Section 17 wins: RT1 is in the band at the cell, on the NTC line through J_BAND_B pad 5. Whether the sensor is a discrete thermistor or part of the cell pack is not stated.
2. Line 284 (W7): protection "at the contact board". Sections 17.1 and 17.3 have no contact board (pads are on the band). U9 stays on the main board at J_BAND_B; the nets are unchanged.
3. Lines 181 to 182 and 199 (section 7): MIC_B_CLK, MIC_B_DATA "mics 3 and 4" and JOY_CENTER as functions. Lines 373 and 374 (16.6) and 450 (17.4): spare test pads. Followed 16.6 and 17.4; `check_netlist.py` still reads the section 7 table and overrides these three rows (A5_SPARE).
4. Line 281 (W4): "LR pin of microphones 1 and 3 to ground, of 2 and 4 to VDD_MIC" (the A3 part IM73D122V01). The A5 part has a Select pin; with 2 microphones U5 on ground, U6 on VDD_MIC (the brief).
5. Line 369 (16.5): "Flex strip: 6 signals and ground" (7 lines). Line 439 (17.3): "5 switch lines and ground" (6 lines). Section 17 wins: J_BAND_A has 6 pads. A6: superseded by 17.11 and 17.12: J_BAND_A has 8 pads and J_BAND_B 7 (section 11).
6. Brief against the files: "with the same pull-ups and protection the old lines had": the old JOY lines had none (line 278, W1: no pull-ups; no protection part in the A3 netlist, `evidence/a5/netlist_before.csv`). The new lines have none; A5-3 enforces that only U1, J_BAND_A and the switch sit on a JOY line. A pull-up or protection part is a decision for the lead.
7. Brief: "slim.md section 5.1" for IM68D128B pin names: that section is the IM68D121J brief (see section 5 above).

## 8. Choices made here (not in the architecture)

- PMIC_INT on nPM1300 GPIO0; U9 channel 2 both on VBUS; SHPHLD on TP19; CC1, CC2 open (as A3).
- Switch designators: SW1 UP, SW2 centre switch under the joystick nub (keeps the bom.csv designator), SW3 DOWN, SW4 LEFT, SW5 RIGHT. "LEFT" is toward the hand, "RIGHT" toward the fingertip (16.6).
- Pad order of J_BAND_A and J_BAND_B (section 2, Band). Ground appears once on J_BAND_A and twice on J_BAND_B (cell minus, charging pad GND).
- The flex tail and the cell protection circuit (on the cell tab at -77 degrees, 17.3) are not drawn as parts: no maker data.

## 9. Design risks an electronics engineer must review

1 to 9 of A3 stand (screen sequencing, SGM38046 AVIN, USB protection, antenna retune, nPM1300 pin numbers, back-powering, VDD_3V0 load, recording light, crystals; see `evidence/a5/sch-notes_before.md` section 9). New in A5:

10. The charger setting: 15 mA and 4.35 V on the nPM1304 (architecture 17.13, 1 C of the smallest cell of the range) until Grepow states the cell's own limit (open item S12). WAS: the nPM1300 could not charge below 32 mA, above 1 C for this cell (architecture 17.5).
11. USB D+ and D- run through a flex tail and J_BAND_B pads 5 and 6; the VBUS ESD part U9 sits at the board end, not at the pads.
12. The storage pads 1 and 7 are "RSV" in SPI mode (maker table); W3 pulls them to VDD_SD as DAT2 and DAT1. Confirm RSV pads tolerate a pull-up.
13. Centre press: SW2 under the nub's centre (architecture 17.11, first choice). Second choice, if it does not fit between the four direction switches: two opposite switches closing within 40 ms (B6), firmware only.

## 10. A5 changes

A6: rows 5, 9 and 10 of the table are superseded by checks A6-2, A6-9 and A6-10 (section 11). `prove_a5.sh` and `prove_fail.sh` describe the A5 and A3 states; they are not files of this task and were not rerun.

Each change has its own check in `check_netlist.py` (tag A5-n) and one broken copy that exits 1 (`prove_a5.sh`; logs and copies in `evidence/a5/broken/`; `exits.txt` lists exit code and the number of FAIL lines carrying the tag).

| # | Change (source) | Check | Broken copy (what is broken) |
|---|---|---|---|
| 1 | 2 microphones IM68D128B, U5 SELECT ground, U6 SELECT VDD_MIC, on F1 and F2 (16.4, 16.6) | A5-1 | `a5_1_u6_select_gnd.csv`: U6 P5 on GND |
| 2 | second pair and its decoupling removed; E6, D7 to test pads (16.6) | A5-2 | `a5_2_u7_back.csv`: a U7 pin on MIC_B_CLK |
| 3 | joystick: no 5-way part; 4 x SKTAAAE010 line to ground (16.4, 16.5) | A5-3 | `a5_3_sw4_not_ground.csv`: SW4 P2 on VDD_1V8 |
| 4 | JOY_CENTER H4 on a test pad only (16.6, 17.4) | A5-4 | `a5_4_testpad22_moved.csv`: TP22 moved to GND |
| 5 | record button one SKTAAAE010 on BTN_REC (16.4) | A5-5 | `a5_5_sw2_wrong_line.csv`: SW2 P1 on JOY_UP |
| 6 | motor M1 = VC0720B088L, W6 circuit unchanged (17.4) | A5-6 | `a5_6_motor_minus_gnd.csv`: M1 P2 on GND |
| 7 | storage CSNP32GCR01-BOW, 8 pads, W3 wiring (16.4) | A5-7 | `a5_7_u3_vcc_gnd.csv`: U3 pad 8 on GND |
| 8 | screen connector 15 positions FH35C-15S-0.3SHW(50), mapped in the printed table order (16.4, slim.md 1.3) | A5-8 | `a5_8_j1_p5_wrong.csv`: J1 P5 on VDD_3V0 |
| 9 | flex tails J_BAND_A (6 pads) and J_BAND_B (9 pads), counts read from 17.3 (17.3) | A5-9 | `a5_9_tail_ntc_gnd.csv`: J_BAND_B pad 5 on GND |
| 10 | title block A5 on every sheet file and every PDF page | A5-10 | `title_a3/`: one sheet file with rev A3 and the pre-A5 PDF |

Checks kept: section 7 pin plan (now with the three A5 spare rows), contact pad order, R41 and the light, P3.05 spare, designators, every pin once, single-pin nets, rails of section 3, H8, KiCad export compare. Checks removed or changed: (a) the check that each JOY line passes the wire link J2, wire, J3 (J2, J3, W5 to W10 no longer exist; A5-3 and A5-9 replace it); (b) the LR check on U5 to U8 became a SELECT check on U5, U6 (same logic); (c) the second-level R33, R34 data check and the FUNC rows for U7, U8, SW1 five-way pins and EVPAVAA1A (parts removed; A5-1, A5-3, A5-5 replace them). `prove_fail.sh` (A3 proofs) still holds the PWR_FLAG ERC probe; its first case names a pin LR that no longer exists and its output is the A3 state.

Before and after (evidence): base check `evidence/a5/base_check.log` (PASS on the A3 state), copies of the A3 sources `evidence/a5/*_before.*`, final runs `evidence/a5/check_final_run.log`, `evidence/a5/erc_cmd.log`, PDF render and text-overlap check `evidence/a5/render_a5.log` (0 overlapping word pairs on 9 pages), pages `evidence/pdf_a5_p1.png` to `p9.png` (every page whose circuit changed was opened: 1, 3, 4, 5, 6, 7, 8, 9).

## questions_for_owner

1. Pin tables: the IM68D128B datasheet (pin numbers), the Alps SKTAAAE010 assembly drawing (terminal numbers), the Hirose FH35C-15S drawing and the nPM1300 CAAA ball table are not on disk; they close 86 provisional pin numbers in part.
2. Does the thermistor sit on the cell pack or as a discrete part in the band (conflict 1)? Should the JOY lines get pull-ups or ESD protection now that they run through a flex tail (conflict 6)?

## 11. A6 changes (2026-11-10)

Contract: `design/architecture.md` 17.13, 17.12, 17.11, 17.10, 17.3 (the later section wins), the review `_review/design-review-1.md` findings F04, F05, F07, F13, F14 and the contradictions K1 to K22 that name the wiring diagram or the parts list. Line numbers below are those of the files as delivered. Evidence (raw logs, saved copies of the sources, the "before" copies) is in `design/ecad/ring/evidence/a6/`.

### 11.1 Changes, each with the file and line it changed

| Id | Change | Files and lines |
|---|---|---|
| a | U2 becomes the Nordic nPM1304, 35-ball CSP 3.1 x 2.4 mm (17.13): symbol `nPM1304_CSP35`, value `nPM1304`, footprint name `ring:WLCSP-35_nPM1304`, order code EMPTY (open action "S18: Nordic"), every ball provisional. The pin names are the nPM1300 names (DK schematic) and are an assumption. The two resistor-set supplies (R71 47 kohm, R72 150 kohm) and the other passives (C71 to C80, L71, L72) are kept as they were and marked "to confirm against the nPM1304 product specification (S18)": the research file gives no passive or VSET value for the nPM1304 | `make_netlist.py` lines 46 (symbol), 220 (part), 422 (provisional reason), 371 (empty order code row); `netlist.csv` lines 110 to 382 (U2 rows); `parts.csv` line 25; `symbols.csv` lines 63 to 95; `open-pins.csv` lines 6 to 103 (33 ball rows) and line 103 (order code); `additions.csv` the U2 passives' reasons; `gen_sch.py` line 17 (sheet title); `bom.csv` line 3 (U2), 4, 5, 66, 70, 65 (passives marked); `check_netlist.py` line 384 (check A6-1) |
| b | ONE control: no record button. SW2 stays on BTN_REC as the switch under the nub's centre (17.11); SW1, SW3, SW4, SW5 stay; CAP2 is deleted from the parts list (it was line 78 of `evidence/a6/bom_before.csv`), CAP1 stays and names the nub with SW2 under its centre; the lines that named the record button (SW2, SW1 and the other direction switches, CAP1, HSG1, the flex tails, J_BAND_A) follow. The item text of SW2 still contains the words "record button" ("the former record button"), because `tools/check_bom.py` requires the function name "Record button" of architecture section 2 (line 48) to appear in the CSV | `bom.csv` lines 39 (SW1, SW3, SW4, SW5), 40 (SW2), 78 (CAP1), 54 (HSG1), 75, 76, 73; `make_netlist.py` line 306 (comment); `check_netlist.py` line 398 (check A6-2) |
| c | Charging pads on the inside of the band (17.12): electrically unchanged (CP1 VBUS, CP2 D-, CP3 D+, CP4 GND). Skin protection stated in section 11.2 | `make_netlist.py` line 323 (comment); `additions.csv` lines 31 to 32 and the CP1 line; `bom.csv` line 61 (CP1 to CP4), 60 (U9); `check_netlist.py` line 405 (check A6-3: VBUS has one source, the pad CP1; D- and D+ hold only U1, U9, their pad and the tail) |
| d | Review F07 (storage at 3.0 V against 1.8 V balls): settled with sources, section 11.3. A level shifter U10 (TI SN74AXC4T774RSVR) and its two 100 nF capacitors C81, C82 are added on the four bus lines; the card side nets are SDC_SCK, SDC_MOSI, SDC_CS, SDC_MISO | `make_netlist.py` lines 57 (symbol), 257 (U3, U10, C81, C82, pull-ups); `netlist.csv` lines 107 to 349 (U10 rows); `parts.csv` line 53; `symbols.csv` lines 104 to 119; `additions.csv` lines 33 to 35; `bom.csv` line 7 (U10), 65 (C81, C82); `check_netlist.py` lines 83 (section 7 function rows) and 414 (check A6-7, which also reads the TI pin table from the saved text) |
| e | Review F04: the split of lines between J_BAND_A and J_BAND_B is the table `BAND_SPLIT` at the top of `make_netlist.py`; one edit of a row's side (A or B) moves a line, then run `make_netlist.py` and `run_all.sh`. Set per 17.8 as replaced by 17.11 and 17.12: A (joystick side, 8 pads) carries the four direction switches, SW2 (BTN_REC), the motor pair and ground; B (other side, 7 pads) carries cell plus and minus, NTC, VBUS, D-, D+ and the pad ground. The motor is on the joystick side "unless a later note says otherwise": THE LEAD CONFIRMS IT after the inside model (open point O2) | `make_netlist.py` lines 128 (table), 302 (J_BAND_A and J_BAND_B parts); `netlist.csv` lines 10 to 327 (J_BAND_A) and 87 to 294 (J_BAND_B); `parts.csv` lines 76, 77; `open-pins.csv` lines 66 to 73, 74 to 80; `bom.csv` lines 73, 74, 75, 76, 44 (M1 tail); `check_netlist.py` line 338 (check A6-9: the rules do not depend on which tail is which, the table is the only place) |
| f | Review F13: the charge settings named in the files of this task are 15 mA and 4.35 V (17.13): U2 and BT1 lines of the parts list, BT1 value in the netlist (also the capacity 15 to 20 mAh of 17.10 in place of 20 to 26 mAh: K4), section 9 item 10 of this file | `bom.csv` lines 3 (U2), 50 (BT1); `make_netlist.py` line 236; `parts.csv` line 41; `check_netlist.py` check A6-5 (no 32 mA, 68 mA, 4.4 V, 4.40 V, 4.45 V or 800 mA in the owned files, lines marked WAS: excepted) |
| g | Review F14 (main chip ball grid stated two ways): section 11.4 | this file only; no file of `pcb/` touched |
| h | Microphone signal-to-noise figure 67.5 dB(A) per the IM68D128B brief (line 13 of `design/datasheets/mic-research/im68d128b-brief.txt`), not 68; the line says "bottom port" and nothing about the sound hole | `bom.csv` line 9 (U5, U6); `check_netlist.py` line 443 (check A6-4) |
| i | Rev A6 on every sheet and PDF page; check A5-10 became A6-10; checks A5-3, A5-5 and A5-7 follow the tail table and the card side nets; A5-9 (tail counts from 17.3, which F26 says enforces the superseded split) is replaced by A6-9 | `gen_sch.py` line 223; `check_netlist.py` line 371 |
| j | K1 to K22 that name the parts list or the wiring diagram: section 11.5 | `bom.csv`, `parts.csv`, this file |

### 11.2 What protects the charging pads on the skin (change c)

The pads CP1 to CP4 touch the finger (17.12). Five statements, each checked:
1. VBUS is an input only. The only source on the net VBUS is the pad CP1 (the case); U2's VBUS ball (power in), U1 ball H9 (through R1) and U9 are loads (check A6-3). The ring's own supply output VBUSOUT is a separate net that touches no pad. With no case, no voltage is on the pad.
2. D- and D+: the nets USB_DN and USB_DP hold only U1 balls H6 and H7 (the chip's dedicated USB pads), U9, the pads CP2 and CP3 and the tail pad: no pull-up, no pull-down, no series part (check A6-3). So when no case is present they are held by the chip alone, as 17.12 says. WHAT THE CHIP DOES WITH THESE TWO PADS while VBUS is absent and USB is off is NOT stated in any source in the project: architecture 17.12 says "held by the chip" with no source, and Nordic's product specification chapter for the USB pins is not saved here (it is HTML only, `parts/mcu.md` line 8). Open point O4. A line with no source and a high impedance puts no current into skin; the exposure is static discharge and sweat leakage, which is U9's job.
3. U9 TPD4E05U06 is still the right part for that job: IEC 61000-4-2 level 4, 12 kV contact and 15 kV air discharge (`parts/codes_tpd4e05u06_text.log` line 10 and the ESD table), reverse stand-off 5.5 V (line 550, above the 5 V of USB), leakage 10 nA at 2.5 V (line 572), input capacitance 0.42 to 0.5 pF (line 24, low enough for the USB data lines). A finger discharge is within that rating.
4. Its limits: it clamps at the board end of J_BAND_B; the flex between the pads and the board has no clamp, so U9 must sit next to the J_BAND_B pads (the board's business, `pcb/board-notes.md`). Both D2 channels are on VBUS, so a strike on the VBUS pad is clamped to ground by two channels. A VBUS above 5.5 V on the pad is outside U9's stand-off: the case must deliver 5 V only (case designer).
5. Not changed: no part is added at the pads, because the pads are in the resin liner and no source says a part fits there (open point O6).

### 11.3 Review F07 (change d): how it was settled and the source of each fact

- The main chip: one supply for every I/O. The CAAA package has two VDD balls (A4, E10), no other supply ball for I/O (`parts/nrf54lm20a-csp61-pins.csv`: the supply-type names are VDD, VSS, VBUS and the decoupling balls DECD, DECA, DECRF, DECUSB). Nordic's reference layout says "VDD:nRF supplied by 1.8 V to 3.6 V" (`parts/nordic-ref-text/caaa_schematic.txt` line 55). So the chip's I/O for D9, A9, B10, D10 follows A4 and E10, which are on VDD_1V8 (1.8 V). The chip's I/O CAN run at 3.0 V only if A4 and E10 are moved to VDD_3V0, which moves every chip pin to 3.0 V: the microphone clock into 1.8 V microphones (VDD_MIC), the power chip's I2C (VDDIO), and the screen's IOVCC. That is a design change to the whole rail plan, not a wiring detail: not done here.
- The chip's input limit: any I/O pin from -0.3 V to VDD + 0.3 V (the nRF54L15 document of another maker, IndieSemiC ISC-nRF54L15-A, `datasheets/mcu_nrf54l15_ds_v2.2.pdf` page 15, saved text line 614 of `evidence/a6/mcu_nrf54l15_ds_v2.2.txt`). Nordic's own nRF54LM20A product specification is not in the project; this limit is that document's, for a sibling chip, and is an assumption for the nRF54LM20A.
- The storage part: supply 2.7 to 3.6 V (maker spec `datasheets/slim2_cs-sdnand-20230403.pdf` page 4, saved text line 72) and input high VIH min 0.625 x VCC, max VCC + 0.3 V (page 8, line 279): 1.875 V at 3.0 V. A 1.8 V chip high is below that, so the chip's outputs do not meet the storage part's input high. In the other direction the storage part's output high (VOH min 0.75 x VCC = 2.25 V, same page) and the 47 kohm pull-ups to 3.0 V exceed VDD + 0.3 V = 2.1 V on D10 and D9. F07 is confirmed, both ways.
- Option "storage at 1.8 V": the CSNP32GCR01-BOW has one supply pad (VCC) and its maker spec gives 2.7 to 3.6 V only; the file `datasheets/slim2_cs-csnp32gcr01-20260408.pdf` holds the XTX XTSDx0xG datasheet (1.8 V and 3.3 V series, another maker's family), not the CSNP32GCR01-BOW. Not an option.
- So a level shifter: TI SN74AXC4T774, orderable code SN74AXC4T774RSVR (UQFN-16 RSV, 2.6 x 1.8 mm, 3000 per reel, Active, Production), read from TI's datasheet SCES898C fetched from `https://www.ti.com/lit/ds/symlink/sn74axc4t774.pdf` (HTTP 200, `evidence/a6/curl_axc4t774.log`; copy `evidence/a6/dl_ti/ti_sn74axc4t774.pdf`, text `evidence/a6/ti_sn74axc4t774.txt`, orderable table line 4136, pin table line 279). Each port 0.65 to 3.6 V; independent direction pins (function table line 3733: DIR high = A to B); VCC isolation: below 100 mV on either supply every port is Hi-Z (line 3684), so the part is safe while VDD_SD is switched off; 0.1 uF bypass on each supply (line 3813). Wiring: VCCA on VDD_1V8, VCCB on VDD_SD, DIR1 to DIR3 on VDD_1V8 (A to B: SCK, MOSI, CS), DIR4 on ground (B to A: MISO), OE on ground; A side = the chip nets, B side = the card nets with the W3 pull-ups. No supplier was contacted; the part was read, not priced.
- Open point O3: the lead confirms this choice (the alternative, VDD of the main chip on 3.0 V, is a rail-plan change and is not taken). The board needs U10, C81, C82 (the board file is read-only here).

### 11.4 Review F14 (change g): the main chip's ball grid

Statement 1: `design/ecad/ring/pcb/board-notes.md` line 42: the ball names "A to H x 1 to 10 are an 8 x 10 grid of 80 sites". Statement 2: `design/mech/thin/placement.csv` line 2: "61 balls: 9 x 7 grid less 2 corners ... dia 0.2, pitch 0.325". Maker source in the project: Nordic's CAAA reference schematic (`design/datasheets/nrf54lm20x_caaa_ref_schematic_0_2.pdf`, copied into `design/parts/nrf54lm20a-csp61-pins.csv`), which names every ball; the reference layout `nrf54lm20x_caaa_ref_pcb_0_2.pdf` page 1 is a picture without dimensions (rendered, `evidence/a6/caaa_pcb_png/p1_u1_zoom2.png`), and the package drawing is not saved (`parts/mcu.md` line 68).
Verdict. The grid of ball NAMES is right: the 61 names use rows A to H and columns 1 to 10 (counted from the csv: A 9, B 8, C 1, D 7, E 9, F 9, G 9, H 9 balls; 19 of the 80 sites empty), so they cannot sit on a 9 x 7 lattice (63 sites, no row H, no column 10). Statement 2 is wrong for the names. The PITCH is not settled and statement 2's pitch is wrong for an 8 x 10 lattice: 9 x 0.325 + 0.2 = 3.125 mm is wider than the 3.02 mm body, and 7 x 0.325 + 0.2 = 2.475 mm is taller than 2.43 mm. For 10 columns in 3.017 mm the pitch is at most (3.017 - 0.2) / 9 = 0.313 mm. (My reading, not confirmed: `parts/mcu.md` line 68 gives a nominal BALL DIAMETER of about 0.325 mm, and that may be where the 0.325 came from.) Open point O5: Nordic's CSP61 (CAAA) package drawing (ball pitch, ball diameter, A1 corner and orientation); then the board owner corrects the footprint. This file does not change the pcb folder.

### 11.5 K1 to K22 against the wiring diagram and the parts list

Fixed in the owned files: K1 (motor angle: `bom.csv` line 44 no longer says -38; its place waits for the rebuild, 17.11), K2 (the record pill is gone, line 40), K3 (joystick: line 78 and line 75 carry no +38), K4 (BT1: line 50 and `parts.csv` line 41 say 15 to 20 mAh and 28.4 mm), K5 (pads: line 61 says inside, 17.12), K6 (protection circuit: line 51), K7 (cross radius 2.1 mm: lines 39 and 78), K8 (this file, change e), K10 (charge voltage, change f, in the owned files), K12 (section 11.4), K16 (R41 key figure: line 48 now (3.0 V - 2.0 V) / 680 ohm = 1.5 mA as W5).
Not in the owned files (read-only conflicts, both lines): K1, K3 and K4 again in `design/architecture.md` lines 49 (motor "-38 degrees"), 47 (joystick "+38 degrees"), 46 (cell "20 to 26 mAh"); K10 in `design/architecture.md` line 77 (WAS: "Charge voltage 4.40 V, charge current 68 mA") against 17.13 (4.35 V, 15 mA). K11, K13, K14, K15, K18 to K22 name mechanics, the board, the case or the firmware, not the wiring diagram or the parts list.
Open, not decidable here: K9 (7 sizes in `bom.csv` line 54 against 9 in the requirement: the owner), K17 (RT1 on the cell or on the main board: the owner; `bom.csv` line 71 keeps the question).

### 11.6 Conflicts found in read-only files (both lines named)

1. `design/architecture.md` line 41 (section 2, microphone) says "68 dB(A)"; the IM68D128B brief (`datasheets/mic-research/im68d128b-brief.txt` line 13) says 67.5 dB(A). The parts list follows the brief.
2. `design/architecture.md` line 45 (section 2, power chip) still says (WAS: "nPM1300 ... charger 32 to 800 mA, termination 3.5 to 4.45 V"); 17.13 replaces it. `design/architecture.md` line 48 (record button row) and line 441 ("Thumb side: 5 switch lines and ground") are older than 17.11.
3. `design/parts/research-npm1304.md` line 66 lists the orderable parts nPM1304-CAAA-R and nPM1304-CAAA-R7 (Nordic spec Table 11); the brief of this task says the order code "is NOT in the research". Followed the brief: U2 has no order code; the lead can close S18 from that line.
4. `design/ecad/ring/pcb/` was built from the A5 files (`pcb/build_board.py` hardcodes 6 pads for J_BAND_A and reads the symbol and footprint names of U2): it must be rebuilt for U2 (nPM1304), U10, C81, C82 and the pad counts 8 and 7.

### 11.7 Open points

| Id | Point | Who answers |
|---|---|---|
| O1 (S18) | nPM1304 ball map against the nPM1300 (`parts/research-npm1304.md` line 37: no compatibility stated), orderable part number (left empty), whether 4.35 V is a selectable termination voltage (line 24), termination current options, the passives and VSET resistors for the nPM1304; until then every U2 ball in `open-pins.csv` is provisional | Nordic (product specification of the nPM1304) |
| O2 | which tail carries the motor (and any later move of a line): edit one row of `BAND_SPLIT`, run `make_netlist.py` and `run_all.sh` | the lead, after the inside model is rebuilt |
| O3 | the level shifter U10 against the alternative of moving the main chip's VDD to 3.0 V; price and stock of SN74AXC4T774RSVR (not read) | the lead; a distributor for price |
| O4 | state of the main chip's USB D- and D+ pads when VBUS is absent (no source in the project) | Nordic (nRF54LM20A product specification, USB chapter), then the firmware owner |
| O5 | ball pitch, ball diameter, A1 corner and orientation of the CAAA package | Nordic (CSP61 (CAAA) package drawing), then the board owner |
| O6 | whether a protection part can sit at the pads inside the liner; that the case delivers no more than 5 V on VBUS | the design partner (ring maker); the case designer |
| O7 | RT1 on the cell or on the main board (K17); 9 sizes against 7 (K9); the pins and part numbers listed in section 5 (S8, S9, 12.x as before) | the owner; the makers named in `open-pins.csv` |
| O8 | the pcb files and the architecture lines of section 11.6 | the board owner; the lead |

### 11.8 Checks run

The commands and their last lines are in the delivering reply; raw logs are in `evidence/a6/` (`check_netlist_final.log`, `erc_final.log`, `check_bom_final.log`, `broken/`).

RESULT: done, check_netlist.py ends "RESULT PASS netlist netlist.csv" (exit 0), KiCad ERC "Found 0 violations" (0 errors), check_bom.py 0 failures; F07 settled with the level shifter U10 SN74AXC4T774RSVR on sources (chip I/O follows VDD at 1.8 V, storage VIH 1.875 V at 3.0 V, storage has no 1.8 V option) and F14 settled as the 8 x 10 name grid right with the ball pitch left open to Nordic; open points O1 to O8
