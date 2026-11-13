# Ring schematic: notes

Contract: `design/architecture.md` version A5-draft (section 17 wins, then section 16 parts 16.4, 16.5, 16.6, then sections 7 and 14) and `design/bom.csv`. A6 (2026-11-10, later): sections 17.11, 17.12 and 17.13 are read too; section 11 lists the A6 changes. Designator list: frozen in `bom_refs_snapshot.csv` (96 electrical designators: bom.csv as on disk at 15:16 on 2026-11-10 plus R51 to R56 from the first read at 15:13). `check_netlist.py` checks against the snapshot and only prints the difference to the live bom.csv (not a failure).

## 1. Files and how to rebuild

All files are in `design/ecad/ring/`.

| File | What it is |
|---|---|
| `make_netlist.py` | writes the source tables below; every pin assignment is in this one file, with its source named next to it; the table `BAND_SPLIT` at its top says which flex tail carries which line |
| `netlist.csv` | source of truth: net, reference, pin_number, pin_name, pin_type (A7: 405 rows, 95 nets, 14 no-connect pins) |
| `parts.csv` | reference, symbol, value, maker part number, footprint name, sheet, dnp (A7: 121 parts) |
| `symbols.csv` | pins of each of the 27 part symbols (A7; ring.kicad_sym adds PWR_FLAG: 28 symbols) |
| `additions.csv` | designators added against bom.csv (A7: 44), bom.csv designators not placed (A7: 22), test pads (22) |
| `bom_refs_snapshot.csv` | the frozen bom.csv designator list the check uses |
| `open-pins.csv` | every provisional pin number and every OPEN part number or order code (A7: 63 rows, was 105) |
| `gen_sch.py` | writes `ring.kicad_sym`, `ring.kicad_sch` (root), 8 sub-sheets `ring_<block>.kicad_sch`, `ring.kicad_pro`, `sym-lib-table` |
| `check_netlist.py` | the rules check; also exports KiCad's own netlist (`ring-kicad.xml`) and compares it with netlist.csv |
| `erc-report.txt`, `erc-report.json` | KiCad ERC output |
| `ring-schematic.pdf` | 9 pages: root plus 8 blocks, title block Rev A7 on each |
| `run_all.sh`, `prove_fail.sh`, `prove_a5.sh`, `render_pdf.py` | the run, the A3 failure proofs, the A5 failure proofs, the page renderer and text-overlap check |

Rebuild: `cd design/ecad/ring && ../../.venv/bin/python make_netlist.py && bash run_all.sh <tag>`.

Drawing style: each pin has a short wire stub to a global label carrying the net name; a pin left open carries a no-connect flag. A flex tail is not drawn as a wire: a band part and the tail pad that carries its line sit in the same net, and `check_netlist.py` (A5-9) proves every band part pin has a tail pad on its net. Footprint names are kept in the symbol field `Footprint_plan` (prefix `ring:`) and the KiCad `Footprint` field stays empty, because no footprint library is drawn yet (board step).

## 2. Block by block (A5)

**Main chip and radio (sheet 2).** Unchanged from A3. U1 nRF54LM20A CAAA, copied pin by pin from Nordic's CAAA reference schematic, configuration 1: VDD balls A4 and E10 on VDD_1V8 with C4, C5, C1, C2; DCC (A5) to L1 to DECD (A6) with C6; FB1 DECD to DECA (A8) and DECRF (B2) with C7, C14; DECUSB (H8) to C10 only; VBUS (H9) through R1 2.2 ohm with C11; TXRTUNE (G6) R2; X1 32 MHz, X2 32.768 kHz; antenna chain L2, C3, L3, C12, L4, C13 (not mounted), ANT1. Every signal ball of section 7 goes to its function; the 11 spare balls go to test pads; MIC_B_CLK (E6), MIC_B_DATA (D7) and JOY_CENTER (H4) go to test pads only (A5).

**Power (sheet 3).** U2 nPM1304 (A6, architecture 17.13) with the passives of the nPM1300 kit design C71 to C80, L71, L72, R71, R72, R57, R58, each marked in bom.csv 'to confirm against the nPM1304 product specification' (S18). A7: U2 is nPM1304-CAAA-R7 with its 35 real balls (Table 33, page 153; section 12); C71 is 1.0 uF 25 V, C85, C86, C87, C88 are added (npm1304-reference.md D1 to D4). The cell BT1 and the thermistor RT1 moved to the band sheet (section 17.3): the nets VBAT and NTC reach them through J_BAND_B. SHPHLD to test pad TP19. CC1, CC2, GPIO1 to GPIO3, LED0 to LED2 are no-connect (A7: GPIO4 does not exist on the package).

**Microphones (sheet 4).** A7: U5 and U6 Knowles SPK0641HT4H-1 (pins 1 DATA, 2 CLOCK, 3 SELECT, 4 Vdd, 5 to 8 GROUND, Knowles sheet 6; all four GROUND pins on ground). Was: IM68D128B with provisional P1 to P5. Both CLOCK on MIC_A_CLK (F1); DATA of each through its own 100 ohm (R31, R32) to MIC_A_DATA (F2); SELECT of U5 on ground, of U6 on VDD_MIC; each has 1 uF (C31, C32) and 100 nF (C35, C36) from VDD_MIC to ground.

**Storage (sheet 5).** U3 CSNP32GCR01-BOW, pads numbered as the maker table (spec V1.0 p5, section 2.1): 1 DAT2, 2 DAT3 = SDC_CS, 3 CLK = SDC_SCK, 4 VSS, 5 CMD = SDC_MOSI, 6 DAT0 = SDC_MISO, 7 DAT1, 8 VCC = VDD_SD. A6: the four bus lines no longer join the chip balls directly: U10 (SN74AXC4T774RSVR) carries SD_SCK (A9), SD_MOSI (B10), SD_CS (D9) from the 1.8 V side to the card side nets SDC_SCK, SDC_MOSI, SDC_CS and SDC_MISO back to SD_MISO (D10); see section 11, F07. 47 kohm pull-ups to VDD_SD on DAT0 (R60 on SDC_MISO), DAT1 (R63), DAT2 (R64), DAT3/CS (R65 on SDC_CS); C60 4.7 uF and C61 100 nF on VDD_SD (W3).

**Screen and its supply (sheet 6).** U4 SGM38046 and its passives as in A3. J1 Hirose FH35C-15S-0.3SHW(50), 15 positions P1 to P15; DISP1 the screen tail, contact k of the tail on position k of J1, contacts named in the order the table of `parts/slim.md` section 1.3 prints them: 1 ELVSS, 2 ELVDD, 3 MTP (open, printed "4"), 4 VCI = VDD_3V0 (printed "4" again), 5 IOVCC = VDD_1V8, 6 SWIRE, 7 TE = LCD_TE (D6), 8 RESX = LCD_RST (H5), 9 CS = LCD_CS (F7), 10 SCL = LCD_SCK (G9), 11 RS = LCD_DCX (G7), 12 SDA = LCD_MOSI (G8), 13 to 15 ground. Names VCI and RESX follow the Tailor table (A3 wrote VCC and RESET).

**Motor drive (sheet 7).** A7 (17.22): MOTOR (F6) through R61 100 ohm to MOT_EN, the EN pin 3 of U11 TLV75530PDQNR, R62 100 kohm MOT_EN to ground; U11 IN (pin 4) on VBAT with C83 10 uF, OUT (pin 1) on VMOT with C84 10 uF, GND pin 2 and pad on ground. Q1 and D1 are removed. M1 is on the band sheet. The recording light circuit of W5 and 17.21 was removed in v7 (architecture 17.30, section 13): a recording shows on the screen.

**Band (sheet 8).** A6: the split of lines between the two tails is the table `BAND_SPLIT` at the top of `make_netlist.py` (section 11, change e). J_BAND_A (joystick side, 8 pads): 1 UP (JOY_UP), 2 DOWN (JOY_DOWN), 3 LEFT (JOY_LEFT), 4 RIGHT (JOY_RIGHT), 5 CENTRE (BTN_REC), 6 MOT- (GND, A7 W2), 7 MOT+ (VMOT, A7 W1), 8 GND (GND). J_BAND_B (other tail, 7 pads): 1 CELL+ (VBAT), 2 CELL- (GND), 3 NTC (NTC), 4 VBUS (VBUS), 5 D- (USB_DN), 6 D+ (USB_DP), 7 GND (GND). Behind them: SW1 up, SW3 down, SW4 LEFT (toward the hand), SW5 RIGHT (toward the fingertip), each one SKTAAAE010 with terminal P1 on its line and P2 on ground; SW2 on BTN_REC is the switch under the centre of the round joystick cap CAP1 (architecture 17.11, 17.29; a long press of 1.0 s starts and stops a recording; there is no record button); M1 W0525AB001D (A7), + (red lead) on VMOT, - (blue lead) on ground; BT1 the curved cell, + on VBAT, - on ground; RT1 10 kohm NTC from NTC to ground, in the band at the cell; CP1 to CP4 the charging pads, VBUS, D-, D+, GND in order from -Y to +Y, on the inside face of the band (architecture 17.12). The pad order and pad numbers of the two tails are this schematic's own definition (not a maker pin).

**USB protection and test pads (sheet 9 of the PDF).** U9 TPD4E05U06 at the main board end of J_BAND_B: D1+ = USB_DP, D1- = USB_DN, D2+ and D2- both on VBUS, pins 3 and 8 ground, 6, 7, 9, 10 open. TP1 DBG_TX, TP2 DBG_RX, TP3 SWDCLK, TP4 SWDIO, TP5 NRESET, TP6 to TP16 the 11 spare pins, TP17 VDD_1V8, TP18 GND, TP19 SHPHLD, TP20 MIC_B_CLK, TP21 MIC_B_DATA, TP22 JOY_CENTER.

## 3. Values chosen and their basis

Unchanged from A3 except: IM68D128B parts keep W4's 100 ohm, 1 uF, 100 nF (Infineon datasheet p10 note of the A3 part; the IM68D128B datasheet is not on disk); charging pad 1.0 mm (17.3); BT1 value 4.35 V 20 to 26 mAh (17.3). All other values: see git history of this file or `evidence/a5/sch-notes_before.md` section 3.

## 4. Additions against bom.csv

Added designators (37), each with its reason in `additions.csv`: U9; CP1 to CP4; R61, R62; R63 to R65; C61; R66; C71 to C80; L71, L72; RT1; TP16 to TP19; J_BAND_A, J_BAND_B; SW3, SW4, SW5; U10, C81, C82 (A6). Test pads TP20 to TP22 are listed as test pads.

Not placed (bom.csv designators, 20): R51 to R56 (W1); CBL1 (no joystick cable); NPM-REF (placeholder); U7, U8, R33, R34, C33, C34, C37, C38 (2 microphones); W1 to W4 (contact wires: no contact board, the pads reach the board through J_BAND_B).

`make_netlist.py` copies maker part numbers from bom.csv where it names one (A7: U5 and U6 read SPK0641HT4H-1 there, U2 reads nPM1304-CAAA-R7).

## 5. Open pins

A7: `open-pins.csv` holds 63 rows (was 105): 53 provisional pin numbers and 10 rows for a part number or order code that is OPEN (L71, L72, RT1; C71, C85, C86, C87, C88, C35, C36 with no maker sheet on file). U2 (35 balls, Nordic Table 33), U5 and U6 (Knowles sheet 6) and LED1 (Kingbright p1) left the file. The A6 list below is kept with its closed rows marked. [History: the recording light and its parts were removed in v7, section 13.]
- CLOSED A7: U2 nPM1304 (was 33 placeholder pins P1 to P33).
- J_BAND_A (8 pads) and J_BAND_B (7 pads): the pad order is this schematic's own definition (A6 lists them: the split is confirmed by the lead after the inside model).
- CLOSED A7: U5, U6 (was IM68D128B, 5 placeholder pins each; now SPK0641HT4H-1, 8 pins from Knowles sheet 6).
- SW1 to SW5 SKTAAAE010: 2 terminals each (10 pins); the Alps spec KTA-601 (7 pages) gives no terminal numbers or drawing (open item S9).
- J1: 15 positions; Hirose FH35C-15S-0.3SHW(50) selected, its drawing not read; position k assumed = tail contact k.
- DISP1 pins 3 (MTP) and 4 (VCI): the Tailor table prints "4 MTP, 4 VCI" and no pin 3; order kept as printed.
- M1 (W0525AB001D: red lead +, blue lead -; the maker gives no numbers), BT1 (tabs), X1, X2. CLOSED A7: Q1 (removed). The light parts of the A7 list were removed in v7 (section 13).
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
- Switch designators: SW1 UP, SW2 centre switch under the round joystick cap (keeps the bom.csv designator), SW3 DOWN, SW4 LEFT, SW5 RIGHT. "LEFT" is toward the hand, "RIGHT" toward the fingertip (16.6).
- Pad order of J_BAND_A and J_BAND_B (section 2, Band). Ground appears once on J_BAND_A and twice on J_BAND_B (cell minus, charging pad GND).
- The flex tail and the cell protection circuit (on the cell tab at -77 degrees, 17.3) are not drawn as parts: no maker data.

## 9. Design risks an electronics engineer must review

1 to 9 of A3 stand (screen sequencing, SGM38046 AVIN, USB protection, antenna retune, nPM1300 pin numbers, back-powering, VDD_3V0 load, recording light, crystals; see `evidence/a5/sch-notes_before.md` section 9). New in A5: [History: the recording light and its parts were removed in v7, section 13.]

10. The charger setting: 15 mA and 4.35 V on the nPM1304 (architecture 17.13, 1 C of the smallest cell of the range) until Grepow states the cell's own limit (open item S12). WAS: the nPM1300 could not charge below 32 mA, above 1 C for this cell (architecture 17.5).
11. USB D+ and D- run through a flex tail and J_BAND_B pads 5 and 6; the VBUS ESD part U9 sits at the board end, not at the pads.
12. The storage pads 1 and 7 are "RSV" in SPI mode (maker table); W3 pulls them to VDD_SD as DAT2 and DAT1. Confirm RSV pads tolerate a pull-up.
13. Centre press: SW2 under the centre of the round cap (architecture 17.11, 17.29, first choice). Second choice, if it does not fit between the four direction switches: two opposite switches closing within 40 ms (B6), firmware only.

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

Checks kept: section 7 pin plan (now with the three A5 spare rows), contact pad order, R41 and the light, P3.05 spare, designators, every pin once, single-pin nets, rails of section 3, H8, KiCad export compare. Checks removed or changed: (a) the check that each JOY line passes the wire link J2, wire, J3 (J2, J3, W5 to W10 no longer exist; A5-3 and A5-9 replace it); (b) the LR check on U5 to U8 became a SELECT check on U5, U6 (same logic); (c) the second-level R33, R34 data check and the FUNC rows for U7, U8, SW1 five-way pins and EVPAVAA1A (parts removed; A5-1, A5-3, A5-5 replace them). `prove_fail.sh` (A3 proofs) still holds the PWR_FLAG ERC probe; its first case names a pin LR that no longer exists and its output is the A3 state. [History: the recording light and its parts were removed in v7, section 13.]

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
| b | ONE control: no record button. SW2 stays on BTN_REC as the switch under the nub's centre (17.11); SW1, SW3, SW4, SW5 stay; CAP2 is deleted from the parts list (it was line 78 of `evidence/a6/bom_before.csv`), CAP1 stays and names the nub with SW2 under its centre; the lines that named the record button (SW2, SW1 and the other direction switches, CAP1, HSG1, the flex tails, J_BAND_A) follow. The item text of SW2 still contains the words "record button" ("the former record button"), because `tools/check_bom.py` requires the function name "Record button" of architecture section 2 (line 48) to appear in the CSV | `bom.csv` lines 39 (SW1, SW3, SW4, SW5), 40 (SW2), 78 (CAP1), 54 (HSG1), 75, 76, 73; `make_netlist.py` line 306 (comment); `check_netlist.py` line 398 (check A6-2) | [History: the nub was replaced by the round cap; the nub was removed in v7, section 13.]
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

Fixed in the owned files: K1 (motor angle: `bom.csv` line 44 no longer says -38; its place waits for the rebuild, 17.11), K2 (the record pill is gone, line 40), K3 (joystick: line 78 and line 75 carry no +38), K4 (BT1: line 50 and `parts.csv` line 41 say 15 to 20 mAh and 28.4 mm), K5 (pads: line 61 says inside, 17.12), K6 (protection circuit: line 51), K7 (cross radius 2.1 mm: lines 39 and 78), K8 (this file, change e), K10 (charge voltage, change f, in the owned files), K12 (section 11.4), K16 (R41 key figure: line 48 now (3.0 V - 2.0 V) / 680 ohm = 1.5 mA as W5). [History: the recording light and its parts were removed in v7, section 13.]
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

## 12. A7 changes (2026-11-11)

Contract: design commit 471150d; `design/architecture.md` 17.16 to 17.22; `npm1304-balls.csv` and `npm1304-reference.md` (read only); `design/ecad/motor-drive/motor-drive.md` section 2; `design/mech/mic-path/mic-path.md` section 9; `design/mech/light-path/light-path.md` sections 6 and 10. Evidence: `evidence/a7/` (before copies in `evidence/a7/before/`, logs, the broken copy in `evidence/a7/broken/`). The run logs of `run_all.sh a7_<n>` sit in `evidence/` beside the A6 ones, as the folder already does.

### 12.1 Changes applied

| # | Source and item | Change | Files touched | Check |
|---|---|---|---|---|
| 1 | 17.18; npm1304-balls.csv (Table 33, page 153) | U2 symbol has the 35 real balls with Nordic's names; connections by ball number; VBUS B1 B2, VSYS C1 C2, VBAT D1 D2; ball C2 is typed passive so VSYS has one power output for ERC; no P1 to P33 left; U2 left open-pins.csv | make_netlist.py, netlist.csv, symbols.csv, parts.csv, open-pins.csv | A7-1 |
| 2 | npm1304-reference.md D5 | GPIO4 removed (not on the package) | make_netlist.py, netlist.csv | A7-1 |
| 3 | 17.18 (Table 50, page 168) | U2 order code nPM1304-CAAA-R7 | make_netlist.py, parts.csv, bom.csv (U2) | A7-1 |
| 4 | D1 | C71 becomes 1.0 uF X5R 25 V (Table 37, page 157); order code empty (no maker sheet of such a part on file), open action NEW-13 | make_netlist.py, parts.csv, bom.csv (C71), open-pins.csv | A7-4 |
| 5 | D2 | C85 2.2 uF X5R 10 V on VBAT at balls D1, D2 (Table 37); C21 stays for U4 | make_netlist.py, additions.csv, bom.csv (new line C85) | A7-4 |
| 6 | D3 | C88, third 10 uF X5R 16 V on VSYS/PVDD (Table 37) | make_netlist.py, additions.csv, bom.csv (new line C88) | A7-4 |
| 7 | D4 | The LOADSW chapter (6.4, pages 67 to 71) gives no output capacitor rule; its only figure is tSS measured with 10 uF (Table 20, page 69). Nordic's configuration 2, which runs one LOADSW in load switch mode, puts C14 1.0 uF X5R 10 V on LSOUT1 (Figure 59 page 158, rendered to `evidence/a7/npm1304_p158_config2.png`; Table 38 page 159). Applied to both outputs: C86 on VDD_MIC at ball A4, C87 on VDD_SD at ball A5 | make_netlist.py, additions.csv, bom.csv (new line C86,C87) | A7-4 |
| 8 | 17.22; motor-drive.md W1, W2 | BAND_SPLIT: MOT+ on VMOT, MOT- on GND (J_BAND_A keeps 8 pads, two of them ground) | make_netlist.py | A6-9 |
| 9 | W3 | M1 W0525AB001D, + VMOT, - GND | make_netlist.py, parts.csv, open-pins.csv (M1 reason) | A7-2 |
| 10 | W4, W5; B1, B2 | D1 and Q1 removed (listed as not placed); bom lines Q1 and D1 deleted | make_netlist.py, additions.csv, bom.csv | A7-2 |
| 11 | W6, W7 | R61 MOTOR to MOT_EN, R62 MOT_EN to GND | make_netlist.py, netlist.csv | A7-2 |
| 12 | W8; B3, B4 | U11 TLV75530PDQNR (1 OUT VMOT, 2 GND, 3 EN MOT_EN, 4 IN VBAT, thermal pad drawn as pin EP on GND: TI gives the pad no number); C83 VBAT, C84 VMOT, 10 uF GRM155R60J106ME15 | make_netlist.py, symbols.csv, parts.csv, bom.csv (new lines U11 and C83,C84) | A7-2 |
| 13 | W9 to W12; B5, B6 | additions texts of R61, R62 and rows U11, C83, C84; M1 open action S21 closed by the study; R61 and R62 line texts (R62 shares its line with R66, so that line names both) | make_netlist.py, additions.csv, bom.csv | A7-2 |
| 14 | 17.19; mic-path 26 to 29 | U5, U6 SPK0641HT4H-1, 8 pins 1 DATA, 2 CLOCK, 3 SELECT, 4 Vdd, 5 to 8 GROUND (Knowles sheet 6, text lines 351 to 359), nets unchanged, all GROUND pins on GND; footprint name ring:Knowles_SPK0641HT4H_LGA8_4.0x3.0; U5, U6 left open-pins.csv; sections 2 and 5 of this file | make_netlist.py, netlist.csv, symbols.csv, parts.csv, open-pins.csv, sch-notes.md | A7-3 |
| 15 | mic-path 30 | the microphone check reads the new pin numbers and compares the symbol with the Knowles text copy | check_netlist.py | A7-3 |
| 16 | mic-path 14 | bom U5,U6: Knowles SPK0641HT4H-1, 8-pad LGA 4.00 x 3.00 x 1.00, SNR 64.5 dB(A), source the datasheet copy, open action S23 | bom.csv | A7-6 |
| 17 | mic-path 15 and the datasheet read here | Knowles sheet 4 (Figure 4 and its notes): 0.1 uF next to each Vdd pin, and "Capacitors near the microphone should not contain Class 2 dielectrics". C35, C36 (100 nF, next to Vdd) become "100 nF Class 1": the old code CL03A104KP3NNNC is X5R, so the code is emptied with open action NEW-14. C31, C32 (1 uF X5R, W4) stay on VDD_MIC but must sit away from the microphones (board list) | make_netlist.py, parts.csv, bom.csv (C31,C32 and C35,C36), open-pins.csv | A7-3 |
| 18 | mic-path 16, 17, 18 | R31, R32 marked a design choice (the Knowles sheet names no series resistor); PCB1 sound holes text; HSG1 openings text (pockets, holes, seats, no microphone slots) | bom.csv | none (text) |
| 19 | mic-path 19, 20 | MEM1, MEM2: disc 2.0 mm, at most 0.10 thick, Gore to quote a thinner cut; GSK2, GSK3: foam ring 1.8 outer, 1.0 bore, PSA both faces, thickness 0.10, 0.20 or 0.30 per unit | bom.csv | none (text) |
| 20 | 17.21; light-path 6, 10 | R41 820 ohm (make_netlist, parts, bom value and key figure: (3.0 V - 1.767 V - 1.5 mA x 0.7 ohm) / 1.5 mA = 821 ohm) | make_netlist.py, parts.csv, bom.csv, sch-notes.md section 2 | A7-5 and the R41 check, which now reads 17.21 | [History: the recording light and its parts were removed in v7, section 13.]
| 21 | light-path 6 | LED1 pad 1 cathode on LED_K, pad 2 anode on LED_A (Kingbright p1 symbol); LED1 left open-pins.csv | make_netlist.py, netlist.csv, symbols.csv, open-pins.csv | A7-5 | [History: the recording light and its parts were removed in v7, section 13.]
| 22 | light-path 10 | bom LED1: under face at X -9.70, Y -2.10 into LG1, Vf 1.767 V at 1.5 mA, pad 1 cathode, open action S25; new lines LG1 and LP1 | bom.csv | A7-5 | [History: the recording light and its parts were removed in v7, section 13.]
| 23 | input 5, 17.15, 17.17 and 17.26 | BT1 value 20 to 27 mAh at US 9, 17.6 mAh at US 7 (netlist value and bom value, key figure; 18.2 mAh before 17.26) | make_netlist.py, parts.csv, bom.csv | A7-8 |
| 24 | input 5 re-checked | one control: only SW1 to SW5, SW2 on BTN_REC, no CAP2 (A5-5, A6-2, A7-8); band split 8 and 7 pads (A6-9 now also counts 8 and 7 and two GND pads on A); U10, C81, C82 wiring (A6-7); cell (A7-8) | check_netlist.py | A5-5, A6-2, A6-7, A6-9, A7-8 |
| 25 | revision | title block Rev A7 on every sheet and PDF page (check A6-10 became A7-10) | gen_sch.py, ring*.kicad_sch, ring-schematic.pdf | A7-10 |

Checks replaced, old against new, and why: A5-1 (IM68D128B P1 to P5) became A7-3; A5-6 (Q1, D1, VDD_3V0) became A7-2; A6-1 (U2 order code empty, every ball provisional) became A7-1; A6-4 (67.5 dB(A) of the IM68D128B brief) became A7-6 (64.5 dB(A) of the Knowles sheet 2); A6-10 (Rev A6) became A7-10; the R41 check read W5 (680 ohm) and now reads 17.21 (820 ohm), because 17.21 replaces W5's value and W5 still says 680 (architecture line 284). A6-9 checks the motor line VMOT on the joystick tail in place of the pair MOTOR_DRV and VDD_3V0. Each old check described a state the five inputs remove; none was loosened. New: A7-4, A7-5, A7-8. [History: the recording light and its parts were removed in v7, section 13.]

### 12.2 Changes refused, or not made here

| Source and item | Reason |
|---|---|
| D3, "the 1.0 nF pair ... is not in this reference" | C76, C77 kept: the note says they are not in Nordic's circuit, it does not ask to remove them. The electronics designer decides. |
| D3 return of the VSYS capacitors to PVSS1 and PVSS2, D6 net tie, D7 capacitor size | layout rules, not netlist changes: in the board list below |
| motor-drive F1 to F5 (firmware.md) | not my file |
| mic-path items 1 to 13, 21 to 25, 31 to 35 | architecture.md, mech, look, pcb, firmware, bench: not my files (31 to 33 are in the board list) |
| light-path rows for architecture.md, placement.csv, thin.py, pcb, mfg specs | not my files (the pcb row is in the board list) |
| order codes for C71, C85, C86, C87, C88, C35, C36, R41 | no maker sheet of a matching part is on file; no fetch was made. Each line has an empty code and an open action naming who answers | [History: the recording light and its parts were removed in v7, section 13.]

### 12.3 For the board (`design/ecad/ring/pcb/`, not touched here)

1. U2: land pattern of the nPM1304-CAAA, 2.3775 x 3.0775 mm, ball pitch 0.419 and 0.44 mm (spec Table 35, page 155; architecture 17.18), ball map of `npm1304-balls.csv`; the board was built from placeholder balls.
2. PVSS1 (A7) and PVSS2 (E7) each with its own via to the ground layer ("net tie", Nordic Figure 57/59; D6); return two of the three VSYS capacitors to PVSS1 and PVSS2 as drawn (D3).
3. New capacitors next to their balls: C85 at D1, D2; C86 at A4; C87 at A5; C88 with C74, C75 at C1, C2, C7. C71 at B1, B2 is now 1.0 uF 25 V. Nordic uses 0603 for every capacitor; the ring uses 0402 and 0201: check the value under bias (D7).
4. Q1 and D1 leave; U11 (X2SON-4 DQN, 1.0 x 1.0 mm, thermal pad to a ground area with vias, TI) and C83, C84 (0402) come in; nets VMOT and MOT_EN are new, MOTOR_DRV and MOTOR_G are gone.
5. J_BAND_A pad 6 is now GND and pad 7 VMOT.
6. U5, U6: 8-pad land pattern of Knowles sheet 6 at (-10.8, -4.8) and (10.8, -4.8), port facing the floor (mic-path items 31 to 33: build_board.py, check_board.py, R31, R32, Q2, R72 move). C35, C36 next to each Vdd pin; C31, C32 (Class 2) away from the microphones. [History: the recording light and its parts were removed in v7, section 13.]
7. LED1 on the under face at X -9.70, Y -2.10, long side along Y, pad 1 = cathode (build_board.py line 70 maps it the other way); 0.50 mm non-plated hole at X -12.425, Y -2.95, no copper within 0.20 mm of its edge; keep the LG1 area free (light-path.md section 10, pcb row). [History: the recording light and its parts were removed in v7, section 13.]
8. U10, C81, C82 are still owed from A6 (architecture 17.14).

### 12.4 Rows of `design/architecture.md` section 2 the lead must change (check_bom.py fails on them)

`design/tools/check_bom.py` ends with 3 failures, all "part ... is absent from the CSV" (log `evidence/a7/check_bom.log`); on the A6 parts list it ended with 0 (`evidence/a7/check_bom_before.log`).

| Line | Present text (Part cell) | New text |
|---|---|---|
| 41 | "IM68D128B (order code IM68D128BV01XTMA1, from a distributor listing)", Infineon, 3.5 x 2.65 x 0.98, "68 dB(A), bottom port, PDM, 1.62 to 3.6 V, 0.58 mA" | "SPK0641HT4H-1 (top port; orderable code open, S23)", Knowles, 4.00 x 3.00 x 1.00, "64.5 dB(A), top port, PDM, 1.6 to 3.6 V, 0.63 mA" (mic-path.md item 1) |
| 51 | "Motor diode", "NSR0230P2T5G", onsemi, SOD-923 | remove the row (the diode leaves, 17.22), or make it "Motor regulator", "TLV75530PDQNR", Texas Instruments, X2SON-4 1.0 x 1.0 x 0.4, "3.0 V, 500 mA" |
| 50 (not failing) | "Motor switch", "DMN2450UFB4" | the part stays only as the light transistor Q2; the row's function is out of date (17.22) | [History: the recording light and its parts were removed in v7, section 13.]
| 60 (not failing) | "GAW112 membrane, custom die-cut, 1.6 mm outer, 0.8 mm inner", 0.24 thick | membrane disc 2.0 mm, at most 0.10 thick (mic-path.md item 2) |

The function names "Motor switch" and "Motor diode" are kept in the CSV inside the U11 item text ("in place of the motor switch and the motor diode"), which is true and keeps the function-name test from failing.

### 12.5 Open points added by A7

| Id | Point | Who answers |
|---|---|---|
| O9 | CLOSED 2026-11-13 by lead decision 24 (`design/wiring/lead-decisions.md`): C60 is 2.2 uF (Kyocera AVX 0402ZC225KAT2A, the same code as C85), as the CS Semiconductor sheet recommends on VCC (`slim2_cs-sdnand-20230403.pdf` PDF page 11). VDD_SD now carries 2.2 + 0.1 + 0.1 + 1.0 uF. Was: VDD_SD now carries C60 4.7 uF, C61, C82 100 nF and C87 1.0 uF = 5.9 uF. The C60 line of bom.csv cites a Zetta datasheet limit of 5 uF on the storage supply (another maker's part); the CSNP32GCR01-BOW  | closed | W1 |
| O10 | C31, C32 1 uF X5R on VDD_MIC against Knowles's "no Class 2 dielectric near the microphone": they stay at least 2.0 mm from each microphone edge and carry the bulk. C35, C36 next to each Vdd pin are 1.0 nF C0G in 0402 (Kyocera AVX 04025A102JAT2A), not the 0.1 uF of the Knowles figure: the AVX C0G table has 0.1 uF only in 1206 (2.29 mm high) and 1.00 mm is free. The 0.1 uF value is NOT met with a Class 1 part of this height; the build guide measures the noise floor (lead ruling 2026-11-13) | the electronics designer, bench B7 |
| O11 | Order codes with maker sheets for C71 (1.0 uF 25 V), C85, C86, C87, C88, C35, C36 (Class 1 100 nF), R41 (820 ohm) | a distributor or the electronics designer | [History: the recording light and its parts were removed in v7, section 13.]
| O12 | VSYS ball C2 is typed passive in the symbol so ERC sees one VSYS output; electrically both VSYS balls are the same output | none (drawing choice) |

### 12.6 Checks run (A7)

- Rebuild: `make_netlist.py` (`evidence/a7/make_netlist_3.log`, exit 0: 405 netlist rows, 121 parts, 95 nets), then `bash run_all.sh a7_<n>` (logs `evidence/gen_a7_<n>.log`, `evidence/erc_a7_<n>.log`, `evidence/erc-report_a7_<n>.txt`, `evidence/pdf_a7_<n>.log`, `evidence/check_a7_<n>.log`); the final tag is named in the end line.
- KiCad ERC: "Found 0 violations", report "ERC messages: 0 Errors 0 Warnings 0".
- The extended check can fail: one broken copy `evidence/a7/broken/netlist_broken.csv` (six pins moved, `make_broken.log`); expected FAIL tags A7-1 to A7-5 written before the run (`expected.txt`); the run (`check_broken.log`) ends "RESULT FAIL 7", exit 1, with A7-1, A7-2, A7-3, A7-4, A7-5, the KiCad compare and A6-3 (not expected: A6-3 lists C71 among the VBUS members, and the copy moved C71 to VSYS).
- open-pins.csv: 105 rows before, 63 after (`evidence/a7/counts.log`).
- Text overlap of the 9 PDF pages: 0 pairs (`evidence/a7/render_a7_1.log`); page 7 (motor drive and light) was opened: `evidence/pdf_a7_1_p7.png`.

2026-11-11 (cell sweep): the BT1 value now follows architecture 17.26: 20-27mAh at US 9 and 17.6mAh minimum at US 7 (18.2 mAh before 17.26); check A7-8 requires 17.6 mAh.
RESULT: done, wiring A7 carries the five inputs: check_netlist.py ends RESULT PASS (evidence/check_a7_final.log), KiCad ERC 0 violations (evidence/erc-report_a7_final.txt), check_bom.py 3 failures, all architecture section 2 part tokens of the microphone and motor diode changes (rows in 12.4), open-pins.csv 105 rows to 63


## 13. v7 changes (2026-11-11): the recording light removed in v7, round joystick

Contract: `design/architecture.md` 17.29 and 17.30 (17.30 wins over 17.21 and 17.22: "Recording light: removed. Out of the design: LED1, the light guide LG1, the light pipe LP1, the window in the glass print, the plug, R41 and Q2. The hole for the guide in the main board goes."), and the lead's fixed choices for v7 (round joystick, see `v7-wiring-notes.md`). Wiring revision A8 carries design v7. Evidence: `evidence/v7/`. Every part of that quote is removed in v7.

- Removed in v7 from the circuit: R41, LED1, Q2, their symbols LED_KPG1005 and DMN2450UFB4, the nets LED_A and LED_K. VDD_MIC keeps its real loads: U5, U6 and their capacitors C31, C32, C35, C36, plus C86 at the power chip's output (check A8-1). LED1, R41 and Q2 are listed as not placed in `additions.csv` and marked in `bom_refs_snapshot.csv` ("removed in v7").
- How a recording shows: on the screen (red dot and timer); firmware, no part (17.30).
- Joystick: unchanged in wiring. Five SKTAAAE010: SW1 up, SW3 down, SW4 toward the hand, SW5 toward the fingertip, SW2 centre on BTN_REC (long press 1.0 s starts and stops a recording). The cap CAP1 is the round moulded cap; the frame FRM1 is a new mechanical line in `bom.csv` (check A8-2).
- New checks: A8-1 (a list of references, symbols, nets and words that must not appear; proved to fail on a copy with R41 and LED1, removed in v7, put back), A8-2 (round joystick in the parts list). Removed: the R41 value check of 17.21, the check "no chip pin touches the light", A7-5. A7-10 became A8-10 (Rev A8).
- Counts after v7: `netlist.csv` 398 rows, 93 nets, 14 no-connect pins; `parts.csv` 118 parts; 25 symbols; `additions.csv` 44 added, 25 not placed, 22 test pads; `open-pins.csv` 60 rows (was 63: the three pins of Q2, removed in v7).
- For the board (`pcb/`, not touched here): R41, LED1, Q2 are removed in v7; the 0.50 mm non-plated hole at X -12.425, Y -2.95 goes (no such hole is drawn in `pcb/ring.kicad_pcb` today). File and line list in `v7-wiring-notes.md`.
## W1 (2026-11-13): exact footprints, maker pin numbers, order codes (package W1 of design/wiring/package-plan.md)

What changed in the sources (`make_netlist.py`, then `run_all.sh`); the history above is not rewritten, and where a line above says otherwise, this section wins:
- Every part on the main board has a footprint of the new library `pcb/OpenRing.pretty` (21 files, written by `pcb/make_footprints.py`); `parts.csv` names them `OpenRing:<name>`. The 14 band parts (J_BAND_A, J_BAND_B, SW1 to SW5, M1, RT1, CP1 to CP4, BT1) are drawn by band-circuits in `ecad/band/OpenRingBand.pretty` and `parts.csv` names them `OpenRingBand:<name>`. `pcb/footprint-sources.csv` has one row per reference. `pcb/check_footprints.py` checks pin names against pad names.
- Pin numbers: J1 positions are 1 to 15 (were P1 to P15; Hirose drawing, Contact No.1 and No.2); X1 has pins 1 (X1), 3 (X2), 2 (GND) and 4 (no connection) (Kyocera); X2 has pins 1 and 2; U11 pad 5 is the thermal pad (was EP). SW1 to SW5 have terminals 1 to 4 (1 and 3 one contact, 2 and 4 the other, Alps drawing), M1 and BT1 pins 1 and 2, as in the first W1 delivery; J_BAND_A and J_BAND_B keep their land numbers (lead, 2026-11-13).
- DISP1 pins 3 (MTP) and 4 (VCC, named VCI in the table of the maker's page 6) are closed by the table on page 5 of the Tailor sheet (3 MTP, 4 VCC). The "4 MTP, 4 VCI" line above was a misprint of page 6.
- Charging pads CP1 to CP4: 1.6 mm (architecture 17.12), was 1.0 mm in `parts.csv` and in line 48 above.
- C60 on VDD_SD is 2.2 uF (lead decision 24; storage maker sheet PDF page 11), Kyocera AVX 0402ZC225KAT2A.
- `check_netlist.py`: the A7-3 test now accepts C0G or NP0 as well as the words Class 1 in the value of C35 and C36 (both are Class 1 dielectrics).
- Order codes (round 2, lead rulings): C71, C86, C87 Murata GRM155R61E105KA12D; RT1 Murata NCP15XH103F03RC; L71, L72 and L10 Murata 1269AS-H-2R2M=P2; C85 and C60 Kyocera AVX 0402ZC225KAT2A; C35 and C36 Kyocera AVX 04025A102JAT2A (1.0 nF C0G, see O10). C88 has no code (no 10 uF 16 V row at 1.0 mm or less), its bom.csv line says NOT CLOSED.
- `open-pins.csv` holds the header only: no pin number waits on a document. What is not closed is listed in `pcb/footprint-notes.md` under "Not closed".
- `check_netlist.py` was edited for the J1 pin names, U11 pad 5 and DISP1 pins 3 and 4 (`pcb/w1-evidence/check_netlist.diff`). Result: RESULT PASS, ERC 0 errors 0 warnings.
