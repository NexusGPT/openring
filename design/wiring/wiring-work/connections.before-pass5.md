# Ring and case: every electrical joint, and whether a file draws it

Update 2026-11-13 08:04 CET (product-wiring helper): the column "Drawn?" of Part 1 is brought to the files of 13 November (band circuits in design/ecad/band, routed case boards in design/ecad/case/pcb, the ring board as it was being routed). R10, R15 and R16 are no longer "not drawn": each is now stated in text with its source, and each conductor end to end is one line of design/wiring/product-wiring.csv (built by design/wiring/build_wiring.py, checked by design/wiring/check_wiring.py). Other columns and Parts 2 to 6 are not rewritten; they describe the files of 12 November.

Update 2026-11-13 08:12 CET (product-wiring helper, second pass): the lead's ruling adds the state `specified and landed` for leads, wires, tabs, spring pins and a part's own cable (ends landed, carrier fully specified); the cells of R5, R11, R12, R13, C1, C2, C3 and C5 follow it and the ring board's round 3.

Update 2026-11-13 08:29 CET (product-wiring helper, third pass): the cells of C1, C2, C3 and C5 cite the lead's rows of design/wiring/lead-decisions.md on the case leads and wires; those 9 lines are now `specified and landed`.

Project root: .. Paths below are relative to it. Written 2026-11-12, clock from `date` (23:24 CET at the first write).

Rule used. A joint is "drawn in" a file when that file holds both ends with the net name that joins them. A joint is "not drawn" when no file holds both ends. Where a file holds the net but not the carrier or the pad, the row says so.

Short keys for the files cited:

| Key | File |
|---|---|
| RN | design/ecad/ring/netlist.csv |
| RP | design/ecad/ring/parts.csv |
| RO | design/ecad/ring/open-pins.csv |
| RS | design/ecad/ring/sch-notes.md |
| RB | design/ecad/ring/pcb/board-notes.md |
| RJ | design/ecad/ring/pcb/provisional-footprints.json |
| RPCB | design/ecad/ring/pcb/ring.kicad_pcb |
| WN | design/ecad/ring/v7-wiring-notes.md |
| CN | design/ecad/case/netlist.csv |
| CP | design/ecad/case/parts.csv |
| CO | design/ecad/case/open-pins.csv |
| CS | design/ecad/case/sch-notes.md |
| AR | design/architecture.md (section 17) |
| BOM | design/bom.csv |
| TP | design/mech/thin/placement.csv |
| MP | design/mech/placement.csv (older layout, see Part 6) |
| MD | design/ecad/motor-drive/motor-drive.md |
| CA | design/case/case-architecture.md |
| CB | design/case/case-bom.csv |
| AS | design/mfg/assembly/assembly.md |

Numbers after a key are line numbers in that file.

## Part 1. Physical connections

| # | From (part, pad or pin) | To (part, pad or pin) | Carrier | Conductors | Net names | Stated at | Drawn? |
|---|---|---|---|---|---|---|---|
| R1 | Ring board pad group J_BAND_A, pads 1 to 8 | Flex tail A (FLEX1), board end | Flexible circuit, hot-bar soldered to board lands | 8 | JOY_UP (1), JOY_DOWN (2), JOY_LEFT (3), JOY_RIGHT (4), BTN_REC (5), GND (6), VMOT (7), GND (8) | RN 10, 92, 93, 138, 141, 144, 147, 363; BOM 78 (8 conductors); AS 209 | Drawn (13 Nov): RPCB lands J_BAND_A 1 to 8 (footprint J_BAND_A_BOARD) carry the RN nets; the 7 FLEX1 boards design/ecad/band/flex1-us7 to us13 carry the tail lands J_BAND_A_TAIL 1 to 8; hot bar (band-interface.md line 60). design/wiring/product-wiring.csv: the 10 lines that start at these lands are `drawn and routed`. |
| R2 | Ring board pad group J_BAND_B, pads 1 to 7 | Flex tail B (FLEX2), board end | Flexible circuit, hot-bar soldered | 7 | VBAT (1), GND (2), NTC (3), VBUS (4), USB_DN (5), USB_DP (6), GND (7) | RN 94, 95, 189, 285, 289, 296, 304; BOM 79 (7 conductors); AS 209 | Drawn (13 Nov): RPCB lands J_BAND_B 1 to 7 (footprint J_BAND_B_BOARD) carry the RN nets; the 7 FLEX2 boards flex2-us7 to us13 carry J_BAND_B_TAIL 1 to 7; hot bar. design/wiring/product-wiring.csv: the 7 lines that start at these lands are `drawn and routed`. |
| R3 | Tail A pads 1 to 5 | Switch terminal P1 of SW1 (up), SW3 (down), SW4 (toward hand), SW5 (toward fingertip), SW2 (centre) | Flex head, solder with reflow | 5 | JOY_UP (RN 148), JOY_DOWN (139), JOY_LEFT (142), JOY_RIGHT (145), BTN_REC (11) | AS 128; AR 441 ("5 switch lines") | Drawn and routed (13 Nov) in the 7 FLEX1 boards: J_BAND_A lands 1 to 4 to terminal 3 of SW1, SW3, SW4, SW5, land 5 to SW2 terminals 1 and 3 (Alps numbers, band-interface.md section 4). Terminal 1 of SW1, SW3, SW4, SW5 is not soldered (joined to 3 inside the part). design/wiring/product-wiring.csv: 10 lines, all `drawn and routed`. |
| R4 | Switch terminal P2 of SW1 to SW5 | GND net on tail A (pads 6 and 8) | Flex head | 5 | GND | RN 103 to 107, 92, 93 | Drawn and routed (13 Nov) in the 7 FLEX1 boards: switch terminal 4 (and 2 of SW2) on a B.Cu GND star to J_BAND_A lands 6 and 8 (band-notes.md section g item 3). design/wiring/product-wiring.csv: 10 lines, all `drawn and routed`. |
| R5 | Motor M1 red lead + (P1) and blue lead - (P2) | Tail A pad 7 (MOT+, VMOT) and pad 6 (MOT-, GND) | Lead wires, hand soldered to pads | 2 | VMOT, GND | RN 364, 96, 363, 92; AS 136; AR 605; MD 26 and 27 | Drawn and routed (13 Nov): FLEX1 lands W0525AB001D_Lands 1 (VMOT) and 2 (GND) to J_BAND_A lands 7 and 6 in the 7 FLEX1 boards. The motor leads are specified and landed: red lead to land 1, blue to land 2, AWG32, cut length per size (band-interface.md section 6). design/wiring/product-wiring.csv: 2 copper lines `drawn and routed`, 2 lead lines `specified and landed`. |
| R6 | Cell BT1 tab + (P1) and tab - (P2) | Tail B pad 1 (CELL+) and pad 2 (CELL-) | Cell tabs, hand soldered to flex lands | 2 | VBAT, GND | RN 292, 40, 296, 94; AS 152 | Drawn and routed (13 Nov): FLEX2 lands PRT1_Tabs 1 (VBAT) and 2 (GND) to J_BAND_B lands 1 and 2 in the 7 FLEX2 boards. The tabs on these lands are the PRT1 output tabs (row R10). design/wiring/product-wiring.csv: 2 copper lines `drawn and routed`. |
| R7 | Thermistor RT1 pin 1 (NTC) | Tail B pad 3 (NTC) | One flex line, hand soldered | 1 | NTC | RN 190, 189; BOM 74 ("its one line runs in FLEX2"); AS 152 | Drawn and routed (13 Nov): FLEX2 land PRT1_Tabs 3 (NTC) to J_BAND_B land 3 in the 7 FLEX2 boards. RT1 sits on the PRT1 board and reaches that land through tab NTC (row R10, text only). RT1 order code NCP15XH103F03RC (RP). design/wiring/product-wiring.csv: 1 line `drawn and routed`. |
| R8 | Thermistor RT1 pin 2 | GND net (tail B has GND on pads 2 and 7, no pad named for RT1) | Not stated | 1 | GND | RN 102 | Stated in text only (13 Nov): RT1 pin 2 is joined on the PRT1 board to tab P-, which lands on FLEX2 land PRT1_Tabs 2 and so on J_BAND_B land 2 (band-interface.md line 114; cell.md line 84). The PRT1 board is drawn in no file. design/wiring/product-wiring.csv: 1 line `stated in text only`. |
| R9 | Charging pads CP1, CP2, CP3, CP4 (inside the band) | Tail B pads 4, 5, 6, 7 | Gold disc on a flex land; how the pad is made is open | 4 | VBUS (CP1 RN 303, pad RN 304), USB_DN (CP2 RN 284, pad RN 285), USB_DP (CP3 RN 288, pad RN 289), GND (CP4 RN 85, pad RN 95) | AS 144; BOM 61; AR 590 and 814 (1.6 mm discs) | Drawn and routed (13 Nov): CP1 to CP4 (CP_Pad_1.6, 1.6 mm disc lands on B.Cu) to J_BAND_B lands 4 to 7 in the 7 FLEX2 boards; RP rows CP1 to CP4 now say 1.6 mm. Gold disc soldered on each land (band-interface.md section 8). design/wiring/product-wiring.csv: 4 lines `drawn and routed`. |
| R10 | Cell protection circuit PRT1 (output tabs) | Cell tabs, FLEX2 cell lands | Solder tabs, hand soldered at low heat | not stated | not stated | BOM 48; AS 152 and 193; AR 436 | Stated in text only (13 Nov; was NOT DRAWN): band-interface.md section 5 and cell.md lines 83 and 84 give the three output tabs P+ (BT1 pin 1, VBAT), P- (BT1 pin 2, GND), NTC (RT1 pin 1) and their order; their FLEX2 lands PRT1_Tabs 1, 2, 3 are drawn in the 7 FLEX2 boards. PRT1 is not a part of RN or RP (RP names it only in BT1's footprint) and not in RPCB. Rows typed in design/wiring/system-joints.csv. design/wiring/product-wiring.csv: 3 lines (and R8). |
| R11 | Antenna ANT1 pad 1 (FEED) | Match chain: U1 pin C1 (ANT) through L2, C3, L3, C12, L4, C13 | 50 ohm board track, not routed | 1 | RF_FEED, ANT1_NODE, ANT2_NODE, ANT3_NODE | RN 3, 5 to 9, 203 to 205; RB 32 | Drawn (13 Nov) in RN and RPCB; the antenna is on its maker's land pattern on the board's under face, no notch (lead-decisions.md row W2). Whether the feed is routed follows the ring board, which is being routed again (round 3): design/wiring/product-wiring.csv gives the state at each build (rules check by build_wiring.py, design/wiring/wiring-work/drc/). |
| R12 | Antenna ANT1 pads 2, 3, 4 | GND net on board | Terminations on board pads that stand in the board notch | 3 | GND | RN 37 to 39; RJ 3; RB 33; AS 98; AR 729 (K-A9: "cannot be soldered as drawn") | Drawn (13 Nov): ANT1 pads 2 and 3 on ANT_TRIM (to LT1, 0 ohm) and pad 4 on GND in RN and RPCB. Routed or not: as R11, the state of each build is in design/wiring/product-wiring.csv. |
| R13 | Screen tail DISP1 pins 1, 2, 4 to 15 (pin 3 MTP not connected) | Board connector J1 positions 1, 2, 4 to 15 (position 3 not connected) | Flexible screen tail inserted into a 15-way 0.3 mm FPC connector | 14 | ELVSS (1), ELVDD (2), VDD_3V0 (4), VDD_1V8 (5), SWIRE (6), LCD_TE (7), LCD_RST (8), LCD_CS (9), LCD_SCK (10), LCD_DCX (11), LCD_MOSI (12), GND (13 to 15) | RN 34, 29, 335, 319, 276, 165, 159, 150, 162, 153, 156, 86 to 88 (DISP1); RN 35, 30, 336, 320, 277, 166, 160, 151, 163, 154, 157, 89 to 91 (J1); BOM 10, 11; TP 18, 25 | Drawn (13 Nov) in RN and RPCB: J1 pads 1 to 15 carry the RN nets; contact k on position k (RS line 38); DISP1 pins 3 and 4 closed by the Tailor table page 5 (RS line 309); pin 3 (MTP) carries no signal and has no line. At the build of 08:11 J1 stood on the screen face (B.Cu) and its pads were open in the main board's rules check (round 3 routing). design/wiring/product-wiring.csv: 14 lines, `drawn, not routed` until J1 is routed. |
| R14 | Microphones U5 and U6 | Ring board | None off board | 0 | none | RB 25; TP 11 and 14 | No joint. Both parts are on the ring board, pads on its under face (TP 11 and 14). Not counted. |
| R15 | Charging pads CP1 to CP4 (ring) | Case spring pins P1 to P4 (case) | Gold pad pressed by a spring pin tip | 4 | Ring VBUS to case VRING; ring USB_DN to case USB_D-; ring USB_DP to case USB_D+; ring GND to case GND | CS 17 ("P1/W1 VRING (ring VBUS), P2/W2 USB_D-, P3/W3 USB_D+, P4/W4 GND"); CA 108; CB 16; RN 85, 284, 288, 303; CN 249, 238, 234, 87 | Stated in text only (13 Nov; was NOT DRAWN): the ring pad to case pin table of design/ecad/case/pcb/board-notes.md Part g (from CS 17). Each end is drawn in its own files (CP1 to CP4 in the FLEX2 boards; P1 to P4 in design/ecad/case/pcb/case_pins.kicad_pcb); no file holds both ends. Rows typed in design/wiring/system-joints.csv. design/wiring/product-wiring.csv: 4 lines. |
| R16 | Ring band metal (no wire) | Case electrode E1 (copper 6 x 3 mm on PCB2 front face) | None. Capacitive touch through the band liner, 2.28 to 2.42 mm gap | 0 | RING_TOUCH on the case side only | CA 49, 110, 137; CN 166 to 168 | Stated in text only (13 Nov; was NOT DRAWN): no conductor by design. E1 is drawn in case_pins.kicad_pcb (net RING_TOUCH); the band is 2.28 to 2.42 mm from PCB2's front face behind the 1.97 mm pin holder wall (CA lines 64 and 235). Row typed in design/wiring/system-joints.csv. design/wiring/product-wiring.csv: 1 line. |
| C1 | Case cell BT1 lead + (P1) | Case board BAT net (U2 pins 13, 14) through wire W5 | 40 mm flying lead, soldered to the case board | 1 | BAT | CN 25, 29, 27, 28; CB 28 ("cell leads to main board"); CA 238 (S1: "40 mm flying leads") | Drawn (13 Nov): case BT1 red lead + to PCB1 pad W5, cut 13.0 mm (case board-notes.md Round 2 wiring table); the cell's own lead as delivered, polarity measured before cutting (design/wiring/lead-decisions.md row 'case cell BT1 leads'). design/wiring/product-wiring.csv: 1 line `specified and landed`. |
| C2 | Case cell BT1 lead - (P2) | Case board GND through wire W6 | 40 mm flying lead, soldered to the case board | 1 | GND | CN 65, 135; CB 28 | Drawn (13 Nov): case BT1 black lead - to PCB1 pad W6, cut 15.2 mm; own lead as delivered (design/wiring/lead-decisions.md row 'case cell BT1 leads'). design/wiring/product-wiring.csv: 1 line `specified and landed`. |
| C3 | Case NTC TH1 (pins 1 and 2) | TS net (U2 pin 11) and GND | Not stated. Footprint "NTC_wired" | 2 | TS, GND | CN 224, 98; CP 31; CB 70 ("0402, NTC on the cell face") | Drawn (13 Nov): TH1 pins 1 (TS) and 2 (GND) to PCB1 plated holes TH1.1 and TH1.2 (footprint NTC_wired), either way round; bare 0.5 mm tin plated 42 alloy leads cut to 10 mm, joint 5 mm or more from the bead (design/wiring/lead-decisions.md row 'case thermistor TH1 leads'; design/case/lead-specs.md). design/wiring/product-wiring.csv: 2 lines `specified and landed`. |
| C4 | Case spring pins P1 to P4 | Case PCB2 (solder) | SMT spring pin, soldered to PCB2 | 4 | VRING, USB_D-, USB_D+, GND | CN 249, 238, 234, 87; CA 223 ("solder P1 to P4 to PCB2"); CB 16 | Drawn (13 Nov) in case_pins.kicad_pcb: P1 to P4 (footprint HARWIN_P70_6000045R) with nets VRING, USB_D-, USB_D+, GND; soldered to PCB2 (CA line 238). In design/wiring/product-wiring.csv the spring pins are the carriers of the 4 R15 lines. |
| C5 | PCB2 wires W1 to W4 and W7 | Case PCB1: W1 VRING, W2 USB_D-, W3 USB_D+, W4 GND, W7 RING_TOUCH | 30 AWG wire (W1 to W4: D+ and D- twisted) | 5 | VRING, USB_D-, USB_D+, GND, RING_TOUCH | CN 254, 241, 237, 134, 168; CB 26 ("5 wires to PCB1"), CB 27 ("length 30"); CA 221 ("five wires drop to the floor slot") | Drawn (13 Nov): WP1 to WP4 and WP7 on case_pins.kicad_pcb, W1 to W4 and W7 on case_main.kicad_pcb; 30 AWG stranded, red, white, green, black, yellow, cut 15.6 to 16.3 mm (design/wiring/lead-decisions.md row 'case wires W1 to W4 and W7: colour'). design/wiring/product-wiring.csv: 5 lines `specified and landed`. |
| C6 | USB-C socket J1 (USB4105): A4, A9, B4, B9 (VBUS); A5 (CC1); B5 (CC2); A1, A12, B1, B12 and shell (GND); A6 to A8, B6 to B8 (no connect) | Case PCB1 (surface mount on its top face) | Surface mount, no off-board joint | 11 with a net, 6 no connect | VBUS_IN, CC1, CC2, GND | CN 243 to 246, 35, 40, 82 to 86, 264 to 269; CA 228 | Drawn (13 Nov) in CN and case_main.kicad_pcb (J1 USB4105 on PCB1). Not a conductor between boards or to an off-board part of the product: no line in design/wiring/product-wiring.csv. |

Checked, no joint found: the case module U1 has its Wi-Fi antenna inside the module and the shell (CA 93, 232). No external joint. The ring parts on the sheets "main", "power", "storage", "mics", "controls" and "contacts" in RP are on the ring board (RB 24 and 25 list them as board placements). The case's storage U4, LED1 and test pads TP1 to TP16 are on case PCB1 (CB 25, 60 to 75; CA 228).

Count: 21 joints (R1 to R13, R15, R16 and C1 to C6; R14 and the module antenna are not joints). On 13 November none is not drawn: R10, R15 and R16 are stated in text only (see design/wiring/product-wiring.csv); on 12 November 3 were not drawn.

## Part 2. Counts from the files

Note 2026-11-13 08:04 CET: this part describes the files of 12 November. The present state of each conductor is in design/wiring/product-wiring.csv and in the column "Drawn?" of Part 1.

Command: `python3 -I` on the counting script saved at `<scratch>/counts.py`. Output saved at `<scratch>/counts.log` (same folder). The last line of the output is the case parts count.

| Count | Value | Source |
|---|---|---|
| Ring netlist, pin rows | 398 | counts.log: "ring netlist pin rows: 398"; RN lines 2 to 399 |
| Ring netlist, pin rows with a net | 384 (398 minus 14 blank) | counts.log: 14 rows with blank net (no-connect), RN lines 386 to 399 |
| Ring netlist, distinct nets | 93 | counts.log: "nets: 93" |
| Ring netlist, distinct references | 118 | counts.log: "distinct refs: 118" |
| Case netlist, pin rows | 279 | counts.log: "case netlist pin rows: 279" |
| Case netlist, blank-net rows (no connect) | 17 | counts.log: "rows with blank net (no-connect): 17" |
| Case netlist, distinct nets | 61 | counts.log: "nets: 61" |
| Case netlist, distinct references | 89 | counts.log: "distinct refs: 89" |
| Ring parts.csv, rows | 118 | counts.log: "ring parts.csv rows: 118" |
| Ring parts.csv, rows by sheet | main 23, power 21, band 14, mics 8, storage 10, screen 14, controls 5, contacts 23 | counts.log, same line |
| Ring parts in sheet "band" | 14: RT1, BT1, J_BAND_A, J_BAND_B, SW1 to SW5, M1, CP1 to CP4 | counts.log: "ring parts in sheet band: 14" |
| Of those, not on the ring board | 12: RT1, BT1, SW1 to SW5, M1, CP1 to CP4 | compare_ring.log LIST 1 (BT1, CP1 to CP4, M1, RT1, SW1 to SW5 are listed as references not in the board). J_BAND_A and J_BAND_B are on the board as pad groups. |
| Case parts.csv, rows | 89 | counts.log: "case parts.csv rows: 89" |
| Case parts.csv, rows by sheet | main 16, power 26, usbc 5, ringlink 17, storage 9, test 16 | counts.log, same line |

The sheets "screen" (14 parts) include DISP1 (the screen module). It is off the board and is not counted in the 12 above.

Note: RB 24 says "the 113 lines of parts.csv". RP has 118 rows. RB 24 is out of date.

## Part 3. Board files

Note 2026-11-13 08:04 CET: this part describes the files of 12 November. The present state of each conductor is in design/wiring/product-wiring.csv and in the column "Drawn?" of Part 1.

Command: `find` on design, with the folders review, .venv, datasheets, out, evidence, logs and sandbox excluded (`-not -path`). Output saved at `<scratch>/board-list.txt`. It holds one line:

- design/ecad/ring/pcb/ring.kicad_pcb

Counts, command `grep -c -F "<text>" design/ecad/ring/pcb/ring.kicad_pcb`:

| Text | Count |
|---|---|
| "(footprint " | 100 |
| "(segment " | 0 |
| "(via " | 0 |
| "(zone " | 0 |

So the one board file has no track, no via and no zone. RB 5 and RB 26 say the same ("No track, via or zone is drawn"; "225 unconnected items"). The file has 410 pads. 94 pads carry no net name (compare_ring.log, output line "BOARD pads: 410 pads with no net: 94").

Circuits with no board file at all:

- Case (design/ecad/case): a netlist and a schematic, no .kicad_pcb. Case PCB1 and PCB2 have no board file (CB 25, 26 give their outlines only).
- Band: the cell BT1, the five joystick switches SW1 to SW5, the motor M1, the thermistor RT1, the charging pads CP1 to CP4 and the protection circuit PRT1 are not on the ring board (RB 24). The band has only the two pad groups J_BAND_A and J_BAND_B on the ring board. The flex tails themselves have no board file (BOM 78, 79: "outline not drawn").
- Screen module DISP1 and its tail: not on the ring board (RB 24). The connector J1 is on the ring board.
- Antenna mount: no file draws the mount (AS 98; AR 729).
- Motor drive (design/ecad/motor-drive): notes only, no board.
- Ring board: one file, and it is stale against the current netlist. See Part 5.

## Part 4. Footprints and pin maps marked PROVISIONAL, OPEN, assumed or unverified

Note 2026-11-13 08:04 CET: this part describes the files of 12 November. The present state of each conductor is in design/wiring/product-wiring.csv and in the column "Drawn?" of Part 1.

Maker document column: the names in design/datasheets (from `ls`, saved at `<scratch>/datasheet-names.txt`). Only the names were read; no document was opened. "None by name" means no file name in that folder matches the part.

| Part | What is missing or assumed | Stated at | Maker document on disk (file name) |
|---|---|---|---|
| U1 nRF54LM20A (61 balls) | Pitch 0.325 and ball 0.20 from the placement note; grid 8 x 10 against "9 x 7 less 2 corners"; ball names to sites and orientation assumed | RJ 2; RB 42 | Nordic reference and distributor files: nrf54lm20a_szlcsc.pdf, nrf54lm20x_caaa_ref_pcb_0_2.pdf, nrf54lm20x_caaa_ref_schematic_0_2.pdf. No package drawing read. |
| U2 nPM1304 | RJ says the 33 pins are laid on sites in number order (placeholder). RS 210 says the real 35 balls are in the netlist (A7). The board is stale. | RJ 4; RB 43; RS 210 | npm1304_datasheet_v1_0.pdf |
| U4 SGM38046 | 4 x 4 balls, pitch 0.4; orientation of A1 not read | RJ 10; RB 44 | p3_sgm38046.pdf |
| U3 CSNP32GCR01-BOW | 8 pads 0.7 x 0.5 with positions assumed; no pitch in any file | RJ 9; RB 45 | slim_cs-csnp32gcr01-bow.pdf; slim2_cs-csnp32gcr01-20260408.pdf |
| U5, U6 Knowles SPK0641HT4H-1 | Five pads in a row; pin table not on disk (RB 46). RS 60 (A7) says the Knowles sheet closed it: conflict. | RJ 7, 8; RB 46 | None by name. The names slim_knowles-everest-miconflex-brief.pdf and slim_knowles-sph0690lm4h-1.pdf are other parts. |
| ANT1 Johanson 2450AT18D0100001E | Four terminations on a regular line, not read from the drawing; stands in the board notch | RJ 3; RB 32, 33 | antenna_johanson_2450AT18D0100001E.pdf |
| J1 Hirose FH35C-15S-0.3SHW(50) | 15 positions at 0.3 pitch, pad 0.5 x 0.16 from the model; contact k on position k assumed | RJ 12; RO 8 to 22 | None by name. |
| L10 Murata 1269AS-H-2R2M | Body 2.5 x 2.0 from the placement note; end pads drawn | RJ 11 | None by name. |
| L71, L72 | Part number OPEN; end pads drawn | RJ 5, 6; RO 57, 58 | None (no part chosen). |
| J_BAND_A | Board has 6 pads; netlist has 8. Pitch in no file. | RJ 13; RB 47; RS 62 | None (flex maker not on disk). |
| J_BAND_B | Board has 9 pads; netlist has 7. Pitch in no file. | RJ 14; RB 47 | None. |
| X1 Kyocera CX2016DB | Crystal maker sheet not on disk; pads 1 and 3 assumed for X1 P1 and P2 | RO 2 to 3; RB 48 | None by name. |
| X2 TXC 9HT11 | Same as X1; X2 P1 and P2 on pads assumed | RO 4 to 5; RB 48 | None by name. |
| BT1 Grepow custom curved cell | Tab order and protection circuit not drawn | RO 6, 7 | None by name. The cell_dnk_* sheets are other cells. |
| DISP1 Tailor Pixels TOH095XVT-01 | Pin 3 MTP and pin 4 VCI: printed table has "4 MTP, 4 VCI" | RO 50, 51 | display_TOH095XVT-01.pdf; slim_tailor-toh095xvt-01.pdf |
| SW1 to SW5 Alps SKTAAAE010 | Two terminals, no terminal numbers or drawing (S9) | RO 38 to 47 | slim_alps-skta-aaae010-orwin.pdf; slim_alps-skta-aaae010-ibs.pdf |
| M1 Jinlong W0525AB001D | Lead colours only; P1 (+) and P2 (-) are schematic names; lead length open (S10) | RO 48, 49 | slim2_jinlong-w0525ab001d.pdf |
| U9 TPD4E05U06 (library USON-10) | TI DQA size not read; "not verified against a maker drawing" | RB 49 | codes_tpd4e05u06.pdf |
| Q1, Q2, LED1, D1, R41 (in RPCB only) | Removed from the netlist in later versions (WN 9 to 13); still in the board file. LED1 polarity unverified. | RB 48; WN 47 to 57 | Q1: p3_dmn2450ufb4.pdf (removed part). LED1: light_kb_KPG-1005SURC-TT.pdf (removed part). |
| 0201, 0402, 0603, SOD-923, DFN1006-3 library parts | "Not verified against a maker drawing" | RB 49 | Not applicable (no single part) |
| C71 (1.0 uF 25 V X5R) | Order code empty; no maker sheet of such a part | RO 52 | None. Values from npm1304_datasheet_v1_0.pdf. |
| C85 (2.2 uF 10 V), C88 (10 uF 16 V), C86 and C87 (1.0 uF 10 V) | Order codes empty; no maker sheet on file | RO 53 to 56 | None. Values from npm1304_datasheet_v1_0.pdf. |
| C35, C36 (100 nF Class 1) | Order code empty; no Class 1 part chosen | RO 60, 61 | None |
| RT1 (10k NTC) | Part number OPEN | RO 59 | None |
| Case U2 BQ25895 | PowerPAD has no number | CO 2 | case_bq25895.pdf |
| Case BT1 DNK852338 | Cell leads: datasheet gives terminals WC and FL only | CO 3, 4 | case_cell_dnk852338.pdf |
| Case J1 USB4105 | Shell tabs have no number | CO 5 | case_usb4105.pdf |
| Case U4 ZDSD64GLQEAG-R | SD-mode names from family datasheet; LGA pad numbers not in a readable drawing | CO 6 to 13 | sdnand_zetta_zdsd64glgeag_r_lcsc.pdf; slim_zetta-p4-5.txt |

Count: the Part 4 table has 27 data rows. Some rows group several parts (for example U5 and U6, or the five switches). The case rows are CO 2 to 13, grouped.

## Part 5. Netlist (11 November) against the ring board file (10 November)

Note 2026-11-13 08:04 CET: this part describes the files of 12 November. The present state of each conductor is in design/wiring/product-wiring.csv and in the column "Drawn?" of Part 1.

Dates: RPCB is dated 10 November and RN 11 November (file times, `ls -la`). The comparison is by script. Its text is below, unchanged from the file saved at `<scratch>/compare_ring.py`. Command: `python3 -I compare_ring.py > compare_ring.log 2>&1` (exit 0). Its output, unchanged:

```text
NETLIST rows (pin rows): 398
NETLIST pin rows with a net: 384
NETLIST distinct references: 118
NETLIST distinct nets: 93
PARTS.CSV rows: 118
BOARD footprints: 100
BOARD pads: 410 pads with no net: 94
BOARD distinct nets on pads: 91

LIST 1: references in netlist not in board: 23
  BT1 C81 C82 C83 C84 C85 C86 C87 C88 CP1 CP2 CP3 CP4 DISP1 M1 RT1 SW1 SW2 SW3 SW4 SW5 U10 U11
LIST 2: references in board not in netlist: 5
  D1 LED1 Q1 Q2 R41
LIST 3a: nets named on board pads that netlist does not hold: 4
  LED_A LED_K MOTOR_DRV MOTOR_G
LIST 3b: nets in netlist with no board pad on them: 6
  MOT_EN SDC_CS SDC_MISO SDC_MOSI SDC_SCK VMOT

LIST 4 (extra): references in both with pin-to-net differences: 12
  J_BAND_A netlist-only=[('7', 'VMOT'), ('8', 'GND')] board-only=[]
  J_BAND_B netlist-only=[('1', 'VBAT'), ('2', 'GND'), ('3', 'NTC'), ('4', 'VBUS'), ('5', 'USB_DN'), ('6', 'USB_DP'), ('7', 'GND')] board-only=[('1', 'MOTOR_DRV'), ('2', 'VDD_3V0'), ('3', 'VBAT'), ('4', 'GND'), ('5', 'NTC'), ('6', 'VBUS'), ('7', 'USB_DN'), ('8', 'USB_DP'), ('9', 'GND')]
  R60 netlist-only=[('1', 'SDC_MISO')] board-only=[('1', 'SD_MISO')]
  R61 netlist-only=[('2', 'MOT_EN')] board-only=[('2', 'MOTOR_G')]
  R62 netlist-only=[('1', 'MOT_EN')] board-only=[('1', 'MOTOR_G')]
  R65 netlist-only=[('1', 'SDC_CS')] board-only=[('1', 'SD_CS')]
  U2 netlist-only=[('A4', 'VDD_MIC'), ('A5', 'VDD_SD'), ('A6', 'GND'), ('A7', 'GND'), ('B1', 'VBUS'), ('B2', 'VBUS'), ('B4', 'VDD_1V8'), ('B5', 'VDD_3V0'), ('B6', 'VDD_1V8'), ('B7', 'SW1'), ('C1', 'VSYS'), ('C2', 'VSYS'), ('C3', 'VBUSOUT'), ('C6', 'VDD_3V0'), ('C7', 'VSYS'), ('D1', 'VBAT'), ('D2', 'VBAT'), ('D3', 'NTC'), ('D4', 'SHPHLD'), ('D6', 'PMIC_INT'), ('D7', 'SW2'), ('E1', 'VSET2'), ('E2', 'VSET1'), ('E3', 'PMIC_SCL'), ('E4', 'VDD_1V8'), ('E5', 'PMIC_SDA'), ('E7', 'GND')] board-only=[('P1', 'VBUS'), ('P14', 'VSET1'), ('P15', 'VSET2'), ('P16', 'SHPHLD'), ('P17', 'PMIC_SCL'), ('P18', 'PMIC_SDA'), ('P19', 'VDD_1V8'), ('P20', 'VBUSOUT'), ('P21', 'VSYS'), ('P22', 'VSYS'), ('P23', 'VDD_1V8'), ('P24', 'SW1'), ('P25', 'GND'), ('P26', 'VDD_3V0'), ('P27', 'SW2'), ('P28', 'GND'), ('P29', 'VDD_1V8'), ('P30', 'VDD_3V0'), ('P31', 'VDD_MIC'), ('P32', 'VDD_SD'), ('P33', 'GND'), ('P4', 'VBAT'), ('P5', 'NTC'), ('P6', 'PMIC_INT')]
  U3 netlist-only=[('2', 'SDC_CS'), ('3', 'SDC_SCK'), ('5', 'SDC_MOSI'), ('6', 'SDC_MISO')] board-only=[('2', 'SD_CS'), ('3', 'SD_SCK'), ('5', 'SD_MOSI'), ('6', 'SD_MISO')]
  U5 netlist-only=[('1', 'MIC1_DATA'), ('2', 'MIC_A_CLK'), ('3', 'GND'), ('4', 'VDD_MIC'), ('5', 'GND'), ('6', 'GND'), ('7', 'GND'), ('8', 'GND')] board-only=[('P1', 'MIC_A_CLK'), ('P2', 'VDD_MIC'), ('P3', 'GND'), ('P4', 'MIC1_DATA'), ('P5', 'GND')]
  U6 netlist-only=[('1', 'MIC2_DATA'), ('2', 'MIC_A_CLK'), ('3', 'VDD_MIC'), ('4', 'VDD_MIC'), ('5', 'GND'), ('6', 'GND'), ('7', 'GND'), ('8', 'GND')] board-only=[('P1', 'MIC_A_CLK'), ('P2', 'VDD_MIC'), ('P3', 'GND'), ('P4', 'MIC2_DATA'), ('P5', 'VDD_MIC')]
  X1 netlist-only=[('P1', 'XC1'), ('P2', 'XC2')] board-only=[('1', 'XC1'), ('3', 'XC2')]
  X2 netlist-only=[('P1', 'XL1'), ('P2', 'XL2')] board-only=[('1', 'XL1'), ('2', 'XL2')]
```

The script text:

```python
import csv
import re
import sys
from collections import defaultdict

ROOT = "design/ecad/ring"
NETLIST = ROOT + "/netlist.csv"
PARTS = ROOT + "/parts.csv"
BOARD = ROOT + "/pcb/ring.kicad_pcb"


def tokenize(text):
    # KiCad s-expression tokenizer: parens, quoted strings, bare words
    tokens = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c in " \t\r\n":
            i += 1
        elif c in "()":
            tokens.append(c)
            i += 1
        elif c == '"':
            j = i + 1
            buf = []
            while j < n and text[j] != '"':
                if text[j] == "\\" and j + 1 < n:
                    buf.append(text[j + 1])
                    j += 2
                else:
                    buf.append(text[j])
                    j += 1
            tokens.append(("STR", "".join(buf)))
            i = j + 1
        else:
            j = i
            while j < n and text[j] not in " \t\r\n()":
                j += 1
            tokens.append(text[i:j])
            i = j
    return tokens


def parse(tokens):
    stack = [[]]
    for t in tokens:
        if t == "(":
            stack.append([])
        elif t == ")":
            node = stack.pop()
            stack[-1].append(node)
        else:
            stack[-1].append(t)
    return stack[0][0] if stack[0] else None


def val(x):
    return x[1] if isinstance(x, tuple) else x


def find_children(node, name):
    return [c for c in node if isinstance(c, list) and c and c[0] == name]


# ---- netlist
net_pins = defaultdict(list)  # net -> [(ref, pin)]
net_rows = 0
netlist_refs = set()
netlist_pins = 0
with open(NETLIST, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        net_rows += 1
        net = row["net"].strip()
        ref = row["reference"].strip()
        pin = row["pin_number"].strip()
        if ref:
            netlist_refs.add(ref)
        if net:
            net_pins[net].append((ref, pin))
            netlist_pins += 1

netlist_nets = set(net_pins.keys())

# ---- parts.csv
with open(PARTS, newline="") as f:
    parts_refs = [r["reference"].strip() for r in csv.DictReader(f)]

# ---- board
text = open(BOARD, encoding="utf-8").read()
tree = parse(tokenize(text))
board_refs = {}
board_pad_nets = defaultdict(set)  # net -> set of refs with a pad on it
board_pad_count = 0
board_pad_no_net = 0
for fp in find_children(tree, "footprint"):
    ref = None
    for prop in find_children(fp, "property"):
        if len(prop) >= 3 and val(prop[1]) == "Reference":
            ref = val(prop[2])
    if ref is None:
        for ft in find_children(fp, "fp_text"):
            if len(ft) >= 3 and val(ft[1]) == "reference":
                ref = val(ft[2])
    if ref is None:
        ref = "?"
    pads = []
    for pad in find_children(fp, "pad"):
        pnum = val(pad[1]) if len(pad) > 1 else ""
        nets = find_children(pad, "net")
        netname = (val(nets[0][-1]) if nets and len(nets[0]) > 1 else "")
        pads.append((val(pnum), netname))
        board_pad_count += 1
        if not netname:
            board_pad_no_net += 1
        else:
            board_pad_nets[netname].add(ref)
    board_refs[ref] = pads

# ---- comparisons
print("NETLIST rows (pin rows):", net_rows)
print("NETLIST pin rows with a net:", netlist_pins)
print("NETLIST distinct references:", len(netlist_refs))
print("NETLIST distinct nets:", len(netlist_nets))
print("PARTS.CSV rows:", len(parts_refs))
print("BOARD footprints:", len(board_refs))
print("BOARD pads:", board_pad_count, "pads with no net:", board_pad_no_net)
print("BOARD distinct nets on pads:", len(board_pad_nets))
print()

refs_in_netlist_not_board = sorted(netlist_refs - set(board_refs), key=lambda s: (re.sub(r"\d+", "", s), len(s), s))
refs_in_board_not_netlist = sorted(set(board_refs) - netlist_refs)
nets_on_board_not_netlist = sorted(set(board_pad_nets) - netlist_nets)
nets_netlist_not_on_board = sorted(netlist_nets - set(board_pad_nets))

print("LIST 1: references in netlist not in board:", len(refs_in_netlist_not_board))
print("  " + " ".join(refs_in_netlist_not_board))
print("LIST 2: references in board not in netlist:", len(refs_in_board_not_netlist))
print("  " + " ".join(refs_in_board_not_netlist))
print("LIST 3a: nets named on board pads that netlist does not hold:", len(nets_on_board_not_netlist))
print("  " + " ".join(nets_on_board_not_netlist))
print("LIST 3b: nets in netlist with no board pad on them:", len(nets_netlist_not_on_board))
print("  " + " ".join(nets_netlist_not_on_board))
print()

# pin-level check for references present in both
pin_mismatch = []
for ref in sorted(netlist_refs & set(board_refs)):
    nl_pins = set()
    for net, lst in net_pins.items():
        for r, p in lst:
            if r == ref:
                nl_pins.add((p, net))
    bd_pins = set((p, n) for p, n in board_refs[ref] if n)
    only_nl = nl_pins - bd_pins
    only_bd = bd_pins - nl_pins
    if only_nl or only_bd:
        pin_mismatch.append((ref, sorted(only_nl), sorted(only_bd)))
print("LIST 4 (extra): references in both with pin-to-net differences:", len(pin_mismatch))
for ref, a, b in pin_mismatch:
    print("  " + ref + " netlist-only=" + str(a) + " board-only=" + str(b))
```

Summary of the three lists, from the output above:

| List | Count | Items |
|---|---|---|
| 1. References in the netlist, not in the board file | 23 | BT1, C81 to C88, CP1 to CP4, DISP1, M1, RT1, SW1 to SW5, U10, U11 |
| 2. References in the board file, not in the netlist | 5 | D1, LED1, Q1, Q2, R41 (removed from the design: WN 9 to 13; RS 67 says Q1 was removed in A7) |
| 3a. Nets named on board pads, not in the netlist | 4 | LED_A, LED_K, MOTOR_DRV, MOTOR_G |
| 3b. Nets in the netlist with no board pad | 6 | MOT_EN, SDC_CS, SDC_MISO, SDC_MOSI, SDC_SCK, VMOT |
| 4 (extra). References in both with pin-to-net differences | 12 | J_BAND_A, J_BAND_B, R60, R61, R62, R65, U2, U3, U5, U6, X1, X2 |

Reading: RPCB was built from an older netlist. It has the removed light parts (list 2), lacks the parts added after it (list 1: U10, U11, C81 to C88, the band parts), has 6 pads on J_BAND_A where the netlist has 8, and 9 pads on J_BAND_B where the netlist has 7. Its J_BAND_B nets are not the current ones (MOTOR_DRV, VDD_3V0). RB 24 and AR 575 say the same in words.

How the script was fixed: the first run read no net names, because KiCad writes `(net "NAME")` with one argument. The parser was corrected, and the run above is the corrected one. Pad counts in the output come from the corrected run.

## Part 6. Not found, and conflicts

Note 2026-11-13 08:04 CET: this part describes the files of 12 November. The present state of each conductor is in design/wiring/product-wiring.csv and in the column "Drawn?" of Part 1.

Each "not found" line names what was searched. Searches were on the brief's sources only, by the terms given.

| # | Connection | What is not found | Searched |
|---|---|---|---|
| N1 | Switch terminal pads (SW1 to SW5, P1 and P2) on tail A | Pad numbers and terminal order. Carrier is found: solder with reflow on the flex head (AS 128). | RO 38 to 47 (states the gap); RN 10 to 11, 138 to 148, 103 to 107 |
| N2 | Path of the switch ground (P2) on the flex | Which conductor carries it, and where it meets tail A | RN 92, 93, 103 to 107; RS 26 (flex not drawn as a wire) |
| N3 | Thermistor RT1 pin 2 (GND) | Which tail B pad carries it. RN puts it on the GND net only (line 102). | RN 102, 189, 190; BOM 74; AR 441; RS 76 |
| N4 | Protection circuit PRT1 | Pins, conductor count, carrier, and any netlist entry. Only a note says its tabs go to FLEX2 (AS 152). | BOM 48; AS 150 to 156, 193; TP 42; RN, RP, RO and RPCB (0 hits each); RS 89 |
| N5 | Cell tab order (BT1 P1 and P2) | Which tab is which on the cell | RO 6, 7; AR 585 (cell placement only) |
| N6 | Charging pad metal (plated land or soldered disc) | How the pad is made | BOM 61; AS 144 and 372 (open, S19) |
| N7 | Motor lead wire gauge and length | Gauge not found. Length is open (S10). | RN 96, 364; AR 597 to 605; MD 40; AS 134 to 140; RO 48, 49 |
| N8 | Flex tail outline and conductor pitch | Outline and pitch. Width (1.4 mm), line count (8 and 7) and layers are found (TP 47, 48; AS 71, 72). | BOM 78, 79 ("outline not drawn"); RB 47 ("pitch in no file"); TP 47, 48 |
| N9 | Antenna mount (how ANT1 pads are fixed to the board) | Not drawn and not solderable as drawn (AS 98; AR 729 K-A9; AR 513 S15). | RN 3, 37 to 39, 203; RJ 3; RPCB (ANT1 pads only); RB 33 |
| N10 | RF feed track to ANT1 | Not routed: RPCB has 0 segments (Part 3); RB 32 | RPCB; RB 32 |
| N11 | Screen tail contact order on J1 | The tail-to-position map is assumed (S8). | RO 8 to 22; RS 38; RJ 12 |
| N12 | Screen tail pins 3 (MTP) and 4 (VCI) | Order unconfirmed: the printed table has "4" twice | RO 50, 51; RS 38 |
| N13 | Ring pad to case pin pairing | No netlist or board file holds both ends. The pairing is text only (CS 17). | RN 85, 284, 288, 303; CN 87, 234, 238, 249; CS 17; CA 108; CB 16; CP 56 to 62 |
| N14 | Spring pin model | Harwin P70-6000045R is the fitted part in CB 16 and CA 108. CP 56 to 62 still lists Mill-Max 0981, which CA 108 says does not fit. Stroke not confirmed (CA 108; CB 16). | CP 56 to 62; CB 16; CA 108; CS 17 |
| N15 | Case thermistor TH1: where it sits and how it is joined | Location and carrier. Three files say three things (Part 6, conflicts). | CP 31; CB 70; CA 238 (S1, "NTC optional"); CS 13 |
| N16 | Case USB socket shell pins (J1 SH) | Pin number, and the joint from the shell to PCB1 | CO 5; CN 86 (GND net only) |
| N17 | Case wire far ends on PCB1 and PCB2 pads | No netlist lists the pads; W5 and W6 are 40 mm (CB 28; CA 238), W1 to W4 are 30 mm (CB 27); W7 length not found | CN 25 to 29, 134 to 168, 237 to 254; CB 26 to 28; CA 221, 223 |
| N18 | Case PCB2 build (rigid-flex or FR4) | Conflict: CA 47 says rigid-flex; CB 26 says "FR4 2 layers" (see conflicts) | CA 47, 223; CB 26 |
| N19 | Ring band metal to case electrode E1 | No contact design. Touch is through the liner at 2.28 to 2.42 mm (CA 137). | CA 49, 110, 137; RN (no band metal net) |
| N20 | Ring thermistor RT1 part number | OPEN | RO 59 |
| N21 | U11 (motor regulator) on the board file | U11 is in RN (list 1 of Part 5) but not in RPCB; its pad map is not drawn anywhere | RB 24, 42 to 49; RJ (no U11 entry); RPCB (no U11 footprint) |

Conflicts noticed (not counted as joints, but they change a row):

- Charging pad size: RP 93 to 96 say "gold pad 1.0mm" and PAD_1.0. BOM 61, TP 43 to 46, AR 590 and AR 814 say 1.6 mm. Row R9 uses 1.6 mm as the stated design, and RP is the outlier.
- Motor side: AR 441 puts the motor on the other tail (tail B). AR 576, RS 62, TP 47 and RN put it on tail A. Rows R1 and R5 use tail A.
- Ring thermistor place: RS 76 says the thermistor is on the main board; BOM 74 says it sits on the cell and is joined to tail B. RN and RP put RT1 on the band. Row R7 uses tail B.
- Case TH1: CP 31 says "NTC_wired"; CB 70 says "0402, NTC on the cell face"; CA 238 says "NTC 10 k optional". Row C3 is drawn only at net level.
- Case PCB2: CA 47 says rigid-flex; CB 26 says FR4 2 layers.
- Knowles sheet: RS 60 says the U5 and U6 pin numbers are closed ("Knowles sheet 6"); RB 46 and RJ 7, 8 say they are not on disk. Not verified by me; the Knowles file is not in design/datasheets by name.
- MP (design/mech/placement.csv) is an older layout. It has rows for record_button (line 14), recording_light (17) and contact_board (24), and puts the antenna at x 12.0 (line 19). Those parts are removed or moved in v7. Not used here; TP is used instead.
- RB 24 says "113 lines of parts.csv". RP has 118 rows (Part 2).
- RS 60 says open-pins.csv holds "63 rows". RO has 60 data rows (RO 2 to 61; wc -l gives 61 lines with the header).
- RB 24, RB 47 and RJ 13, 14 give 6 and 9 pads for the J_BAND groups; RN gives 8 and 7. RN is used here.

Files I wrote: `design/wiring/connections.md` (this file). Also `design/wiring/board-files.lst` (one line, from an early `find` I ran before I had the scratch folder). I cannot delete files, so it stays; it can be removed by hand. Scratch files, all in the scratchpad folder `<scratch>`: `compare_ring.py`, `compare_ring.log`, `counts.py`, `counts.log`, `board-list.txt`, `datasheet-names.txt`.

No git command was run. No other file was changed. No process was started or stopped. No browser was used.

## Audit of this file

Script: `<scratch>/audit_cites.py`. It opens 150 cited lines (file and line number) and checks that each line holds the quoted words. Output: `<scratch>/audit_cites.log`, last line `checked 150 bad 0`. The script covers the citations for the rows, counts and conflicts above. It does not cover every line number in the file. The counts in Part 2 and Part 5 come from `counts.py` and `compare_ring.py` (logs in the same folder). Both were run after their last change.

Dates checked with `ls -l`: RPCB 10 November 19:29; RN 11 November 21:16.

RESULT: done, 21 connections found; 3 of them are not drawn in any file (R10 cell protection PRT1, R15 ring charging pads to case spring pins, R16 band metal to case touch electrode).
