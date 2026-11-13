# Ring footprints and open parts (package W1)

Written 2026-11-13 by W1 (helper ring-parts). Version worked on: the project folder as found, commit b1de827. Nothing here was committed by me.

All paths are under `design/` unless they start with `/`. `RING` means `ecad/ring/` and `PCB` means `ecad/ring/pcb/`. Proof logs are in `PCB/w1-evidence/`, each named `final_*.log` for the last run. The checklist is `PCB/w1-evidence/CHECKLIST.md`.

Scope change (lead, 2026-11-13): the band parts (J_BAND_A, J_BAND_B, SW1 to SW5, M1, RT1, CP1 to CP4, BT1 with PRT1; 14 references) are drawn by band-circuits in `ecad/band/OpenRingBand.pretty` and their interface is in `ecad/band/band-interface.md`. I drew none of them and wrote no interface file for them (my first draft of both was removed). `parts.csv` names their footprints `OpenRingBand:<name>`, `footprint-sources.csv` has a row for each naming that library, and `check_footprints.py` reads them from it. Two lead notes were also applied: C60 changed to 2.2 uF, and distributor copies of a maker sheet are allowed.

Rerun everything: `bash PCB/w1-evidence/run_final.sh final` (generators, ERC, all checks). Rebuild this file: `design/.venv/bin/python -I PCB/w1-evidence/make_notes.py`.

## Answers to points a to g

### a. Footprint library

Folder: `PCB/OpenRing.pretty/`. It holds 19 footprint files, one per distinct package of the 118 parts of `RING/parts.csv`, not counting the 14 band parts (their footprints are in the band library). Written by `PCB/make_footprints.py`. KiCad finds it through `PCB/fp-lib-table` (for the board project in that folder) and `RING/fp-lib-table` (for the schematic project), nickname `OpenRing`.

Each footprint has the pad numbers or ball names of the maker document, the land pattern the document gives where it gives one, a courtyard on F.CrtYd, and the document file and page in its description. No description holds the word PROVISIONAL: `PCB/check_footprints.py` tests that (point f).

| Footprint | Parts | Maker document | Page | Pads | Pitch | Where the lands come from |
|---|---|---|---|---|---|---|
| ANT_Johanson_2450AT18D0100001E_3.2x1.6 | ANT1 | antenna_johanson_2450AT18D0100001E.pdf | PDF p2 (terminals), p3 (mounting lands) | 4 | n/a (4 corner lands) | maker evaluation-board lands |
| Chip_0201 | C5 C1 C2 and 35 more | nrf54lm20x_caaa_ref_pcb_0_2.pdf | p1 (C1, C2, C5, C7, FB1, R2, L2 to L4) | 2 | n/a (centres 0.57) | maker reference layout (measured) |
| Chip_0402 | C4 C11 C71 and 16 more | nrf54lm20x_caaa_ref_pcb_0_2.pdf | p1 (C4) | 2 | n/a (centres 0.92) | maker reference layout (measured) |
| Chip_0603 | R1 C88 C21 and 4 more | nrf54lm20x_caaa_ref_pcb_0_2.pdf | p1 (R1) | 2 | n/a (centres 1.4) | maker reference layout (measured) |
| FPC_Hirose_FH35C-15S-0.3SHW | J1 | w1_hirose_fh35c_series_catalog.pdf | p3 dimensions, p4 recommended land; w1_hirose_fh35c-15s-0.3shw50_drawing.pdf p1 (numbering) | 17 | 0.3 (0.6 per row) | maker recommended land pattern |
| FPCtail_Tailor_TOH095XVT-01_15 | DISP1 | display_TOH095XVT-01.pdf | PDF p5 | 15 | 0.3 (derived, not printed) | DERIVED pitch and width (tail 4.8 wide and Hirose F 4.8); contact block 3.2 long as printed |
| LGA-8_Knowles_SPK0641HT4H-1_3.0x4.0 | U5 U6 | design/mech/mic-path/datasheets/knowles-spk0641ht4h-1_chipsmall.pdf; second copy design/datasheets/w1b_knowles_spk0641ht4h-1_chipdip.pdf | PDF p7 (printed p6) | 8 | n/a (8 pads, gaps 0.4) | maker example land pattern |
| LGA-9_CSNP32GCR01-BOW_8.0x6.2 | U3 | slim2_cs-sdnand-20230403.pdf | PDF p5-6 (printed p2-3) | 9 | 1.27 (side pads) | maker package drawing (pads) |
| L_Murata_1269AS-H_2.5x2.0 | L71 L72 L10 | w1b_murata_1269as-h-2r2m.pdf | p1 (body), p5 (recommended PCB pattern), p2 (code) | 2 | n/a (centres 2.0) | maker recommended land pattern |
| L_TDK_MLZ1608_1.6x0.8 | L1 | nrf54lm20x_caaa_ref_pcb_0_2.pdf | p1 (L1) | 2 | n/a (centres 1.35) | maker reference layout (measured) |
| TESTPAD_0.8 | TP1 TP2 TP3 and 19 more | pcb/footprint-notes.md | point a | 1 | n/a | our own size |
| UQFN-16_SN74AXC4T774RSV_1.8x2.6 | U10 | w1_ti_sn74axc4t774.pdf | PDF p40 outline, p41 example board layout | 16 | 0.4 | maker example board layout |
| USON-10_TPD4E05U06DQA | U9 | codes_tpd4e05u06.pdf | PDF p28 outline, p29 example board layout | 10 | 0.5 | maker example board layout |
| WLCSP-16_SGM38046_2.0x2.0_P0.5 | U4 | p3_sgm38046.pdf | p18 (package outline and recommended land pattern); p3 (pins) | 16 | 0.5 | maker recommended land pattern |
| WLCSP-35_nPM1304-CAAA | U2 | npm1304_datasheet_v1_0.pdf | p155 Figure 55 and Table 35; p152 Figure 53; p153 Table 33 | 35 | 0.419 x 0.44 | maker package drawing (no land drawing: land = nominal ball) |
| WLCSP-61_nRF54LM20A-CAAA | U1 | nrf54lm20x_caaa_ref_pcb_0_2.pdf | p1 pads; p11 and p12 body outline (schematic names: nrf54lm20x_caaa_ref_schematic_0_2.pdf p1) | 61 | 0.325 | maker reference layout (measured) |
| X2SON-4_TLV755xxPDQN_1.0x1.0 | U11 | motor_tlv755p.pdf | PDF p41 outline, p42 example board layout | 5 | n/a (rows 0.65, columns 0.86) | maker example board layout |
| XTAL_Kyocera_CX2016DB_2.0x1.6 | X1 | w1_kyocera_cx2016db_catalog_page10.pdf | p1 | 4 | n/a (centres 1.4 x 1.1) | maker recommended land pattern |
| XTAL_TXC_9HT11_2.0x1.2 | X2 | nrf54lm20x_caaa_ref_pcb_0_2.pdf and w1_txc_9ht11_datasheet.pdf | p1 (pads of X2); TXC p1 (2 pads, 2.0 x 1.2 x 0.6) | 2 | n/a (centres 1.45) | maker reference layout (measured) |

Details that matter:
- U1: the 61 land centres are measured from Nordic's own reference layout (`datasheets/nrf54lm20x_caaa_ref_pcb_0_2.pdf` page 1, drawn at 12:1) by `PCB/measure_u1.py`. The ball names come from Nordic's reference schematic. The match is 61 names to 61 pads. Only one of four ways to lay the name grid on the pads fits (A1 top left, the other three fit 55 of 59 grid sites: `PCB/w1-evidence/final_measure_u1.log`). The grid is 8 rows (A B D E F G H, no C row except ball C1) by up to 10 columns at 0.325 pitch, 59 balls on the grid and C1 and D3 off it. This ends the 8 x 10 against 9 x 7 disagreement of deferred item 9: `placement.csv` is wrong. The 62nd circle the script finds inside the body outline is a duplicate drawn 0.07 mm from another.
- U2: 7 columns at 0.419 pitch and 5 rows at 0.44, ball 0.225 (nPM1304 specification page 155, Table 35). The ball map was already the real one (page 153, Table 33).
- U4: pitch 0.5, land 0.26 (SG Micro sheet PDF page 18). A1 is top left in the top view: this closes deferred item 16.
- U3: nine pads, not eight. The package drawing (PDF page 5) shows a ninth pad at the bottom centre. The pin table has no pin 9, so pad 9 has no net.
- J1: the Hirose recommended land (catalogue page 4) with 15 contacts in two staggered rows plus two mounting pads `MP`. Pin 1 is the right end of the 8-pad row; the numbering runs left in 0.3 steps (drawing `w1_hirose_fh35c-15s-0.3shw50_drawing.pdf` page 1). The mounting-pad offsets are measured from the drawing by `PCB/measure_hirose_mp.py`.
- U5 and U6: Knowles example land pattern (printed page 6). U11: TI example board layout with a 0.48 thermal pad turned 45 degrees, numbered 5 as the TI drawing numbers it.
- Chip parts 0201, 0402, 0603: pad sizes measured on Nordic's reference layout for parts of the same size (C1, C4, R1, L1: `PCB/measure_passives.py`, saved `PCB/w1-evidence/passive-pads-measured.csv`). KiCad's own sizes differ (its 0201 pads are 0.46 along the part and 0.40 across, Nordic's are 0.27 along and 0.30 across), so I did not copy KiCad's. This follows bar a: a maker document backs each size.

### b. footprint-sources.csv

File: `PCB/footprint-sources.csv`, 118 rows, one per part reference, columns: reference, package, footprint, maker_document_file, page, pad_count, pitch, pin_to_net_map_source, land_source, document_obtained. Written by `make_footprints.py`, which stops if a part has no row or a footprint has no part.

### c. Netlist scripts use the makers' real pin numbers

Changes in `RING/make_netlist.py` (old file saved as `PCB/w1-evidence/make_netlist_before.py`, diff `make_netlist.diff`):

| Part | Before | Now | Source |
|---|---|---|---|
| J1 | positions P1 to P15 | 1 to 15 | Hirose drawing page 1 (Contact No.1, No.2), catalogue page 4 |
| X1 | P1, P2 | 1 = X1 net, 3 = X2 net, 2 = GND (lid), 4 no connection | Kyocera catalogue page (`w1_kyocera_cx2016db_catalog_page10.pdf`), connection diagram |
| X2 | P1, P2 | 1, 2 (a crystal has no polarity) | TXC sheet `w1_txc_9ht11_datasheet.pdf` page 1: 2 pads, no drawing |
| U11 | thermal pad EP | pad 5 | TI DQN0004A land drawing (`motor_tlv755p.pdf` PDF page 42) |
| DISP1 pins 3 and 4 | listed open ("4 MTP, 4 VCI") | 3 MTP, 4 VCC | Tailor sheet PDF page 5 table (page 6 misprints it) |
| U1 balls, U2 balls, U3, U4, U5, U6, U9, U10, ANT1 | already real | unchanged | as before; each footprint now carries the same names (check f) |
| SW1 to SW5 | P1, P2 (round 2 first rolled back to these, then corrected by the lead) | terminals 1 to 4: 1 and 3 one contact, 2 and 4 the other | Alps SKTA catalogue (`w1_alps_skta_catalog.pdf`) page 2, Drawing No.1 |
| M1, BT1 | P1, P2 | pins 1 and 2 (M1 1 = red lead +, 2 = black or blue lead -; BT1 1 = +, 2 = -) | Jinlong sheet PDF page 9; band interface |
| J_BAND_A, J_BAND_B | land numbers 1 to 8 and 1 to 7 | unchanged | `ecad/band/band-interface.md` |

Also changed in `make_netlist.py`: footprint names (map `FPMAP`), the charging pad value "gold pad 1.6mm" (was 1.0 mm; architecture 17.12 wins, so `parts.csv` is corrected), C60 (2.2 uF) and the order codes of point d. `RING/check_netlist.py` was edited in 11 changed lines (diff `PCB/w1-evidence/check_netlist.diff`) for J1 pin names, SW1 to SW5, M1, U11 pad 5 and DISP1 pins 3 and 4, and in test A7-3 so that C35 and C36 may be marked C0G or NP0 as well as Class 1 (C0G is a Class 1 dielectric); no limit or expected value was loosened.

Commands and last lines (all re-run by `run_final.sh`):

| Check | Command | Last line | Exit |
|---|---|---|---|
| generate | `design/.venv/bin/python -I RING/make_netlist.py` | `netlist rows 410 parts 118 nets 93` | exit 0 |
| netlist check | `design/.venv/bin/python -I RING/check_netlist.py` (inside `run_all.sh`) | `RESULT PASS netlist netlist.csv` | exit 0 |
| ERC | `kicad-cli sch erc` (inside `run_all.sh`) | `** ERC messages: 0  Errors 0  Warnings 0` | 0 |
| all | `bash RING/run_all.sh final` | `check_netlist exit 0` | exit 0 |

`RING/open-pins.csv` now holds the header only (0 data rows; it was 60 rows). No pin number waits on a document. Before: `PCB/w1-evidence/check_netlist_before.log` ended `RESULT PASS netlist netlist.csv`, ERC `PCB/w1-evidence/erc_report_before.txt` also 0 errors and 0 warnings.

### d. Part numbers for the open lines (and C60)

Rule from the lead: a part line carries only a code that a saved maker document shows. Documents: Murata sheets saved by reader w1b (`design/datasheets/w1b_*.pdf`, see `PCB/part-docs.md`), Kyocera AVX tables (`w1_kyocera_avx_x7r_dielectric.pdf`, `w1_kyocera_avx_c0g_dielectric.pdf`, PDF page 3 each; cells read in `PCB/w1-evidence/avx_x7r_cells.log` and `avx_c0g_options.log`).

| Ref | Order code | Package, height | Document | Reason (one line) |
|---|---|---|---|---|
| C71, C86, C87 | Murata GRM155R61E105KA12D | 0402, 0.5 | `w1b_murata_grm155r61e105ka12.pdf` p1 (code), p2 (1.0 uF 25 V X5R) | one part for three lines: 25 V covers the 10 V of Table 38, and 0402 stays the board size |
| C85, C60 | Kyocera AVX 0402ZC225KAT2A | 0402, 0.71 max | AVX X7R table PDF p3, row 2.2 uF, 0402, 6.3 V and 10 V (code E) | 2.2 uF 10 V as Table 37 (C6); C60 on VDD_SD by lead decision 24 and the storage sheet PDF p11 |
| L71, L72 | Murata 1269AS-H-2R2M=P2 | 2.5 x 2.0 x 1.0 max | `w1b_murata_1269as-h-2r2m.pdf` p2 (2.2 uH, DCR 156 mohm max, 1.9 A), p1, p5 | same part as L10; meets Table 17 of the nPM1304 (2.2 uH, DCR below 400 mohm, Isat above 350 mA, page 44) |
| RT1 | Murata NCP15XH103F03RC | 0402 | `w1b_murata_ncp15xh103f03rc.pdf` p1, p2 | 10 kohm 1 percent, B 3380 K as the nPM1304 thermistor table (page 24) |
| C35, C36 | Kyocera AVX 04025A102JAT2A (1.0 nF C0G) | 0402, 0.56 max | AVX C0G table PDF p3 (printed p5): 0402 row 1000 pF at 16, 25, 50 V, code C | Class 1 as Knowles asks; the table has 0.1 uF C0G only in 1206, 2.29 mm high, and 1.00 mm is free |
| C88 | Murata GRT188R61A106KE13D | 0603, 0.8 | `w1c_murata_grt188r61a106ke13.pdf` p1 (code D = 180 mm paper tape), p2 (10 uF 10 V X5R) | lead decision. STATED DEVIATION from Nordic Table 37 (16 V): C88 sits on VSYS, which never exceeds VBUSOVP 5.5 V (nPM1304 PDF p17); 10 V is 1.8 times that; the AVX X7R table has 10 uF 16 V only at 1.52 mm and 2.29 mm |

**C35 and C36.** Knowles asks for a bypass capacitor next to each Vdd pin and no Class 2 part near the microphone, and its Figure 4 shows 0.1 uF (PDF page 4 of `w1b_knowles_spk0641ht4h-1_chipdip.pdf`): "Capacitors near the microphone should not contain Class 2 dielectrics due to their piezoelectric effect." The 0.1 uF value is **not met** with a Class 1 part of this height. C35 and C36 are 1.0 nF C0G in 0402, each next to its microphone's Vdd pin. C31 and C32 (1 uF, Class 2) stay at least 2.0 mm from each microphone edge and carry the bulk. The build guide measures the noise floor. My round 1 sentence that put a 0.1 uF C0G cell in 0805 was wrong: the table shows 0.1 uF C0G only in 1206.

Room (courtyards, `PCB/w1-evidence/final_courtyard.log`: 0201 0.667, 0402 1.292, 0603 2.839, 1269AS inductor 7.076 mm2): C86, C87, C35 and C36 grow from 0201 to 0402, +0.625 mm2 each (+2.500 together); C71, C85, C60 and C88 stay 0402; L71 and L72 become 2.5 x 2.0 parts of 7.076 mm2 each (placement.csv has them at 2.0 x 1.6).

Files changed for point d: `bom.csv` (8 lines: C71, C85, C86 and C87, C88, C60, L71 and L72, RT1, C35 and C36), `bom-notes.md` (one note), `sch-notes.md` (open point O10 and the W1 section). `tools/check_bom.py`: before `lines 82, designators 136, section-2 rows 19, section-2 part tokens 24, switch lines 2, pad lines 1, designators against model and wiring 136, failures 0` (`PCB/w1-evidence/check_bom_before.log`), after `lines 82, designators 136, section-2 rows 19, section-2 part tokens 24, switch lines 2, pad lines 1, designators against model and wiring 136, failures 0` (exit 0, `PCB/w1-evidence/final_check_bom_after.log`).

### e. Custom parts

Moved to band-circuits by the lead: tab order, land order, land size and pitch of J_BAND_A, J_BAND_B, BT1 with PRT1, CP1 to CP4, M1, RT1 and the switches are theirs, in `ecad/band/band-interface.md`. I wrote no `custom-part-interfaces.md` (the draft was removed). What stays mine here: the charging pad is 1.6 mm in `parts.csv` and `bom.csv` (architecture 17.12 wins over 1.0 mm), and the 22 test pads TP1 to TP22 (footprint `TESTPAD_0.8`, 0.8 mm round, the size of the first draft, from the list `TPS` in `make_netlist.py`).

### f. Check script

`PCB/check_footprints.py` loads every part's footprint with KiCad's Python (`PCB/run_kipy.sh`). It exits 1 when a netlist pin has no pad of that name, when a pad count differs from `footprint-sources.csv`, when a description holds PROVISIONAL or names no document file, or when the library holds a footprint no part uses. Band parts are read from `ecad/band/OpenRingBand.pretty` like the others: every netlist pin must be a pad name, the pad count must equal `footprint-sources.csv`, and a missing footprint file fails ("not yet delivered" is no longer accepted).

| Run | Command | Last line | Exit |
|---|---|---|---|
| good | `PCB/run_kipy.sh PCB/check_footprints.py` | `RESULT PASS 118 parts, 19 footprints, 410 pins have pads, pad counts equal footprint-sources.csv, no PROVISIONAL` | exit 0 |
| renamed ball | `PCB/run_kipy.sh PCB/check_footprints.py PCB/w1-evidence/broken_ball.pretty` | `RESULT FAIL 1 footprints netlist netlist.csv library broken_ball.pretty` | exit 1 |
| missing pad | `PCB/run_kipy.sh PCB/check_footprints.py PCB/w1-evidence/broken_missing.pretty` | `RESULT FAIL 2 footprints netlist netlist.csv library broken_missing.pretty` | exit 1 |
| band library absent | same with an empty folder as 4th argument | `RESULT FAIL 14 footprints netlist netlist.csv library OpenRing.pretty` | exit 1 |
| band circuits | `PCB/run_kipy.sh ecad/band/check_band.py` (read only for me) | `RESULT: PASS boards checked 14` | exit 0 |

The broken copies are made by `PCB/make_broken_fp.py` (U1 ball A1 renamed A1X; U2 pad E7 deleted). The first fails on the name, the second on the missing pad and on the count. I did not run the new script on the old state: the library did not exist then, so a failure there would be a missing name, which is not red.

### g. Not closed

Each item names what I tried and the exact document that is missing.

1. C35 and C36: the 0.1 uF at the Vdd pin that Knowles shows is not met with a Class 1 part of this height (1.0 nF C0G 0402 instead). Missing: a Class 1 100 nF part of 1.0 mm or less in a readable maker document; the build guide measures the noise floor.
2. U1 mechanical drawing: Nordic's package page (docs.nordicsemi.com, CSP61 CAAA) answered 403 in the logged pass. Lands and names are closed from the reference layout and schematic. Missing: ball height and ball diameter tolerance, which the land does not need.
3. Knowles SPK0641HT4H-1: the Knowles product page returned 212 bytes of HTML, no sheet (logged pass). I use the two distributor copies of Knowles Datasheet Rev A (Chipsmall, on disk; ChipDip, `w1b_knowles_spk0641ht4h-1_chipdip.pdf`). The corner chamfers of the land (8 x 0.1 x 45 degrees) are not drawn.
4. TXC 9HT11: the one-page sheet (`w1_txc_9ht11_datasheet.pdf`) has no drawing, so pad size comes from Nordic's reference layout for the same part. Pad numbers are not printed; the two terminals are interchangeable.
5. TLV75530P U11: the four small pads have a cut inner corner on the TI drawing; the cut is not dimensioned on the page, so the pads are drawn as plain rectangles 0.36 x 0.21.
6. `FPCtail_Tailor_TOH095XVT-01_15`: pitch 0.3 and pad width 0.15 are not printed on the Tailor page (4.8 mm tail, 3.2 mm contact block are). This is the module's own tail, not a ring board part.
7. J1 courtyard: the housing depth 4.2 is on the Hirose page, but which side the 0.6 overhang lies on is not read; the courtyard is centred on the lands.
8. Hirose mounting-pad offset: confirmed from the drawing by script only through the nearest drawn pad (the drawing breaks the pad row in the middle), see `PCB/w1-evidence/measure_hirose_mp.log`.

## Deferred items answered

Item: result. 9: closed (8 x 10 grid, measured). 13: closed for U1 U2 U3 U4 U5 U6 ANT1 J1 L10 L71 L72; J_BAND_A and J_BAND_B moved to band-circuits. 14: closed (X1 X2; Q1, Q2, LED1 were removed from the circuit earlier). 15: closed for U9 and the chip sizes. 16: closed. 19: closed: Nordic's reference leaves LED1 and LED2 unconnected and Table 36 (page 156) lists LEDs as not used in configuration 3; the balls stay open. 20: lands closed, drawing not obtained (Not closed 3). 21: closed (ball map Table 33, order code nPM1304-CAAA-R7 Table 50, land Table 35). 31, 46, 162, 163 and the SKTAAAE010 land of 125: band-circuits' work now. 49: closed (pitch 0.3, 15 contacts, Hirose catalogue). 50: closed. 51: closed. 127: C71, C86, C87 (Murata sheet), C85 (AVX table), C35, C36 (AVX C0G, 1.0 nF, Not closed 2) closed; C88 closed by the lead's decision (point d); R41 is gone. 128: L71, L72 (Murata 1269AS sheet) and RT1 (Murata sheet) closed.

## Facts about files in datasheets

Checked with `file` (`PCB/w1-evidence/datasheet_types.log`): `slim_cs-csnp32gcr01-bow.pdf`, `slim_knowles-everest-miconflex-brief.pdf` and `slim_knowles-sph0690lm4h-1.pdf` are HTML pages, not PDFs. `nrf54lm20a_szlcsc.pdf` is a PDF of a Seeed board, not Nordic's package drawing. I cite none of them; the storage part is cited from `slim2_cs-sdnand-20230403.pdf`.

## Changes other files need

I did not touch these (they are on the must-not-touch list or outside my files).

1. `PCB/build_board.py`, `PCB/check_board.py`, `PCB/board-notes.md`, `PCB/ring.kicad_pcb`: the board is stale and these still use the old `ring:` footprint names, the old pin maps (`PADMAP` for X1, X2 in `check_board.py`) and the PROVISIONAL drawn footprints. They must load `OpenRing.pretty` and `ecad/band/OpenRingBand.pretty` and the new pin numbers (J1 1 to 15, U11 pad 5). `PCB/provisional-footprints.json` (written by `build_board.py`) is obsolete.
2. `design/mech/thin/placement.csv` (not mine): row U1 says "9 x 7 grid less 2 corners" but the real grid is 8 rows by 10 columns, 61 balls; row U2 says pitch 0.4 and ball 0.25 but the sheet says 0.419 x 0.44 and 0.225; row U4 says pitch 0.4 but the sheet says 0.5; row U3 says 8 pads 0.7 x 0.5 4 x 2 but the drawing shows 9 pads 0.8 x 0.7 in two columns 7.0 apart; row J1 says housing 3.2 x 5.2 but the Hirose housing is 6.1 along the contact row and 4.2 deep. The last one matters: along Y the real housing is 0.9 mm longer than the model, and along X 1.0 mm deeper (J1 sits at X -12.0 and the board edge is X -13.6).
3. `design/architecture.md` and `design/mech/thin/thin-notes.md` repeat the U1 "9 x 7" grid (sch-notes O5 and thin-notes line 39).
4. `design/ecad/band`: nothing needed; with the makers' pin numbers back in the netlist `check_band.py` ends `RESULT: PASS boards checked 14`.
5. `design/tools/build_supplier_package.py` copies `open-pins.csv`, `netlist.csv` and `parts.csv`; its package index may list `open-pins.csv` as holding provisional rows.
6. `design/wiring/connections.md` Part 4 and Part 5 and `deferred-items.md` rows above: the lead can mark them closed from this file.

## Files made or changed

Made: `PCB/OpenRing.pretty/` (19 files), `PCB/footprint-sources.csv`, `PCB/make_footprints.py`, `PCB/check_footprints.py`, `PCB/make_broken_fp.py`, `PCB/measure_u1.py`, `PCB/measure_passives.py`, `PCB/measure_hirose_mp.py`, `PCB/footprint-notes.md`, `PCB/w1-evidence/` (logs, scripts, broken copies, `CHECKLIST.md`), `RING/fp-lib-table`, `PCB/fp-lib-table`, and in `datasheets/`: `w1_hirose_fh35c_series_catalog.pdf`, `w1_hirose_fh35c-15s-0.3shw50_drawing.pdf`, `w1_hirose_fh35c-15s-0.3shw50_spec.pdf` (saved, no number taken from it), `w1_ti_sn74axc4t774.pdf`, `w1_alps_skta_catalog.pdf` (used for the switch terminals by the netlist history only), `w1_kyocera_cx2016db_catalog_page10.pdf`, `w1_kyocera_avx_c0g_dielectric.pdf`, `w1_kyocera_avx_x7r_dielectric.pdf`, `w1_txc_9ht11_datasheet.pdf`, `w1_knowles_spk0641ht4h-1_chipsmall.pdf`.

Changed: `RING/make_netlist.py`, `RING/check_netlist.py`, and by the run `RING/parts.csv`, `netlist.csv`, `symbols.csv`, `additions.csv`, `open-pins.csv`, `ring.kicad_sch` and its sheets, `ring.kicad_sym`, `ring-kicad.xml`, `ring-schematic.pdf`, `erc-report.txt` and `.json`, `RING/sch-notes.md` (W1 section appended), `bom.csv` (8 lines), `bom-notes.md` (note appended).

Process notes: I read the web only with curl and python (no browser). I used the session scratchpad folder under /private/tmp for downloads and page images; those scratch files are not deleted (they are logs of what I read) and are not part of the delivery. No secret was read. No git command was run. No purchase, sign-up or contact was made.

## Round 2 (lead messages, 2026-11-13)

1. Band parts: `parts.csv` (through `make_netlist.py`), `footprint-sources.csv` and `check_footprints.py` use the band library `OpenRingBand` for J_BAND_A, J_BAND_B, SW1 to SW5, M1, BT1 and RT1 (both to PRT1_Tabs and RT1_NTC_0402) and CP1 to CP4; my own band footprints are not in `OpenRing.pretty`; `PCB/custom-part-interfaces.md` holds one line naming `band-interface.md` and the test pads. Correction by the lead: the band parts carry the makers' pin numbers again (SW1 to SW5 terminals 1 to 4, M1 and BT1 pins 1 and 2), the netlist of the first delivery. Both checks, last lines:
   - `PCB/run_kipy.sh PCB/check_footprints.py`: `RESULT PASS 118 parts, 19 footprints, 410 pins have pads, pad counts equal footprint-sources.csv, no PROVISIONAL` (exit 0). Every pin of the 14 band parts is a pad of the band library.
   - `PCB/run_kipy.sh ecad/band/check_band.py`: `RESULT: PASS boards checked 14` (exit 0). I did not edit `design/ecad/band`.
   - With the band library missing the first check now fails: `RESULT FAIL 14 footprints netlist netlist.csv library OpenRing.pretty` (exit 1).
2. C60 on VDD_SD is 2.2 uF, Kyocera AVX 0402ZC225KAT2A (10 V, 0402, the code of C85): `make_netlist.py`, `parts.csv`, `bom.csv`; `sch-notes.md` open point O9 is marked CLOSED by decision 24.
3. Documents and rulings (reader w1b, `PCB/part-docs.md`, then the lead's rulings): C71, C86, C87 are Murata GRM155R61E105KA12D in 0402 (code on p1 of its sheet); RT1 NCP15XH103F03RC confirmed; L10, L71 and L72 are one footprint drawn from p5 of the Murata 1269AS-H-2R2M=P2 sheet (two pads 0.8 x 2.0, centres 2.0 apart; the DFE201610E code and footprint are gone); C35 and C36 are 1.0 nF C0G 0402 (point d); C85 and C60 keep AVX 0402ZC225KAT2A (row 2.2 uF, 0402, 10 V on PDF p3); C88 is Murata GRT188R61A106KE13D (lead decision); the Knowles land (printed page 6) was drawn earlier and the second copy is cited. No part line of `bom.csv` says NOT CLOSED. Lines still without a document: 0.
4. C88 (lead, last line of round 2): Murata GRT188R61A106KE13D, 10 uF 10 V X5R, 0603, 0.8 mm, orderable code with packaging letter D (180 mm paper tape) as page 1 of `w1c_murata_grt188r61a106ke13.pdf` lists it; `make_netlist.py`, `parts.csv` (footprint Chip_0603), `bom.csv` and `footprint-sources.csv` changed; the NOT CLOSED text is gone.
5. Stated deviation from Nordic Table 37: 10 V instead of 16 V, because C88 is on VSYS and VSYS never exceeds the charger input limit VBUSOVP 5.5 V (nPM1304 PDF p17); 10 V is 1.8 times that. No 16 V part with a readable document exists at 1.0 mm or less.
6. Checks after the change: see the table in point f and the two lines under item 1 above; all re-run by `run_final.sh`.

RESULT: done, 19 footprints, 11 of 11 open part lines closed against a maker document, 0 lines without a code, 8 items under Not closed
