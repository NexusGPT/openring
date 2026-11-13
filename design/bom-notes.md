# Ring parts list: notes (bom.csv, architecture version A5-draft)

Version: A5-draft (architecture.md header; section 17 wins, then 16, then 1 to 15). Checked 2026-11-10.
`bom.csv` has 78 part lines, 128 designators, 53 lines with a maker order code and 25 lines without one (each of those 25 has an `open_action` naming who must answer what). The A3 file read before this rewrite had 77 lines and 146 designators (its notes said 65 lines; that count was stale).
Check: `design/.venv/bin/python -I design/tools/check_bom.py` exits 0 (run 2026-11-10 on this file: 78 lines, 128 designators, 0 failures; architecture section 2 is at A5).

## Changed against A3
| Line (designators) | Change | Section |
|---|---|---|
| Microphones U5, U6 | 4 x IM73D122V01XTMA1 become 2 x Infineon IM68D128B, code IM68D128BV01XTMA1 (LIST: seen only in a DigiKey URL in search text, datasheet not saved) | 16.4, 17.4 |
| U7, U8 | removed with their microphones | 16.4 |
| C31, C32 / C35, C36 / R31, R32 | quantity 4 to 2 each (C33, C34, C37, C38, R33, R34 removed) | 16.4 |
| Storage U3 | ZDSD64GLGEAG-R 8 GB becomes CS Semiconductor CSNP32GCR01-BOW 4 GB, 8.0 x 6.2 x 0.75 (DS, spec V1.0); R60, R63 to R65, C60, C61 stay (W3 stands) | 16.4, 17.4 |
| Screen connector J1 | Hirose FH35C-15S-0.3SHW(50) was already on the line; open action reworded to S8 | 16.4 |
| Joystick SW1 to SW4 | 1 x SKRHADE010 becomes 4 x Alps SKTAAAE010 | 16.4, 16.5, 17.3 |
| Record button SW5 | Panasonic EVPAVAA1A (SW2) becomes 1 x SKTAAAE010 (SW5) | 16.4, 17.3 |
| Motor M1 | KPD3A-03208-05-05D-0 becomes Vybronics VC0720B088L, USD 3.23 at quantity 1 (DigiKey, read 2026-11-10), no open action | 17.3, 17.4 |
| Motor Q1 | function text only: full duty from VDD_3V0 | 17.4 |
| Cell BT1 | becomes the custom curved cell 1.6 x 6.0 x 38 mm, 20 to 26 mAh, no order code | 17.3, 17.5, S12 |
| Cell protection PRT1 | added, 2 x 5 mm on the cell tab, no code | 17.3 |
| Thermistor RT1 | text only: on the cell, wired in flex tail 2 (conflict 5, closed) | 17.3 |
| Main board PCB1 | 27.0 x 17.4 x 0.6 becomes 27.2 x 12.6 x 0.3, 6 layers; 4 sound holes removed | 17.2, 17.4 |
| Joystick board PCB2, contact board PCB3 | removed, replaced by 2 band flex tails | 17.3 |
| Flex tails FLEX1, FLEX2 | added (thumb side 6 conductors; other side 9) | 17.3 |
| Solder pads J2, J3 | J2 6-pad joystick link kept as flex tail 1 pads; J3 added as the 9 pads of flex tail 2 (was one line "J2, J3") | 17.3 |
| Wires W1 to W4 (contact board) and W5 to W10 (joystick link) | removed, the flex tails replace them | 17.3 |
| Charging pads CP1 to CP4 | 1.6 mm pads on the board become 1.0 mm pads on the band at 180 degrees, X = -2.4, -0.8, +0.8, +2.4 | 17.1, 17.3 |
| USB protection U9 | text only: placed on the main board, contact board gone | W7, 17.4 |
| Top shell HSG1, base HSG2, screws SCR1 to SCR4, gasket GSK1 | replaced by one metal body HSG1 (block and band 29.3 x 14.75 x 3.2); HSG2, SCR1 to SCR4, GSK1 removed | 17.1, 17.3 |
| Band liner LNR1 | added, 0.3 mm resin cast | 17.3 |
| Caps CAP1, CAP2 | added, each with its 0.4 mm flange as one moulded part (joystick cap 4.6 dia; record cap 5.0 x 3.0); no separate plate line (the PLT1, PLT2 placeholders of an earlier draft are removed) | 17.3 |
| Cover glass GL1 | 28.6 x 13.6 x 0.5 becomes 29.3 x 14.75 x 0.4 with rolled edge | 17.1, 17.4 |
| Adhesive ADH1 | size cleared (A3 outline does not fit the new glass) | 17.2 |
| Foam FOAM1 | 0.20 mm becomes 0.10 mm | 17.2 |
| Microphone seal MEM1, MEM2 | 4 become 2 (MEM3, MEM4 removed) | 17.1 |
| Microphone gasket GSK2, GSK3 | 4 become 2 (GSK4, GSK5 removed) | 16.3, 17.1 |
| Test pads TP20 to TP22 | added for the freed pins MIC_B_CLK, MIC_B_DATA, JOY_CENTER | 16.6 |
| C13, R41, C76, L71, TP1, TP16, RT1, PCB1 and others without a code | `open_action` reworded so each names who must answer what | rule 4 of the brief | [History: the recording light parts and the nub were removed in v7, see the v7 note below.]
| Lines named "Schematic addition: ..." | item names shortened (they were cut off mid-word) | none |
| All other lines | unchanged | |

## Conflicts between sections (A5 value kept in the CSV, both stated)
1. Motor: 16.4 says Vybronics VC0625B001L (6 mm coin, wire leads, 2.5 V, 100 mA); 17.3 and 17.4 say VC0720B088L (7 mm, FPC tail, 3.0 V, 85 mA). CSV: VC0720B088L (17 wins). bench-kits.md section 6 also notes a 3 V rating for the VC0625B001L on DigiKey against 2.5 V in the maker spec.
2. Cell: 16.4 flat 2.60 x 11.9 x 19.0 in the block, 37 to 48 mAh; 17.3 curved 1.6 x 6.0 x 38 in the band, 20 to 26 mAh. CSV: 17.
3. Board and glass: 16.4 board 0.4 mm and glass 0.5 mm; 17.4 board 0.3 mm and glass 0.4 mm. CSV: 17.
4. Controls: 16.5 puts joystick and record button on the block wall at X +10.0 and -5.0; 17.1 and 17.3 put them on the band at +38 and +62 degrees. CSV: 17.
5. Thermistor RT1: W13 says on the main board beside the cell; 17.3 says the cell's temperature sensor is wired in flex tail 2. CSV keeps RT1 as one line. CLOSED 2026-11-12 (design review 3, H05, lead's ruling): RT1 sits on the cell, on its protection circuit PRT1, wired in flex tail B FLEX2; section 17 wins over W13, which architecture.md now marks as replaced; the question to the owner is removed from the open action.
6. Microphone slot: 16.3 says 1.4 x 0.4 mm; 17.1 says 1.2 x 0.3 mm. CSV: 17.1.

## Open facts that no file closes (nothing invented)
- IM68D128B order code is LIST only; no saved datasheet (pin order, LR pin, sound port). Price empty.
- SKTAAAE010 outline and land pattern (S9), price (search text only: about USD 0.71 at DigiKey cut tape, not read on the page), production status.
- CSNP32GCR01-BOW price, read and write current.
- Curved cell and its protection circuit: no code, no price (S12). Charge current floor of the nPM1300 is 32 mA, above 1 C for this cell.
- One-piece metal body, band liner, caps, flex tails, glass, adhesive, foam, gaskets, charging pads: no supplier, no drawing (S13, B7, B8, B9).
- Recording light supply (A1 contradiction, still open): architecture section 9 says VDD_MIC 1.8 V through a transistor; the LED needs 2.4 V; R41 and Q2 stay as in W5 (3.0 V, 680 ohm). [History: the recording light parts and the nub were removed in v7, see the v7 note below.]
- No ESD part on the charging pads other than U9; no gate pull-down question remains (R62, R66 exist). Capacitor heights, crystal load capacitors and the nPM1300 VDD_USB_3V3 net are as listed in A1 notes and not resolved.
- Prices: only entries read from files are filled (U2 nPM1300 GBP 1.25, J1 FH35C GBP 1.76, C4 GBP 0.13, C31 and C32 CAD 0.15, R31 and R32 GBP 0.07, M1 USD 3.23); every other price cell is empty.

## Evidence tags
DS, LIST and CALC as in architecture.md. LIST lines still needing a maker document are those whose `open_action` or `key_figures` say so (U1, U2, IM68D128B, LED1, FH35C). [History: the recording light parts and the nub were removed in v7, see the v7 note below.]


Note added by the lead, 2026-11-10: the two groups of solder pads for the band flex tails are named J_BAND_A (thumb side, 6 pads) and J_BAND_B (other side, 9 pads), the names the wiring diagram uses (design/ecad/ring/, sheet "Band"). They were J2 and J3 in the first A5 list.

Note added for firmware F3, 2026-11-10: the texts of GL1 (cover glass), CAP1 (joystick cap) and CAP2 (record cap) follow architecture 17.8: GL1 is one formed piece curved across the finger, 29.3 x 14.75 mm, 1.10 mm thick at its centre; CAP1 is a rounded rectangular nub 4.6 x 3.6 mm in a 6.4 x 5.4 mm frame at the bottom of the band; CAP2 is a pill 4.4 x 2.4 mm. Only the size and description cells of those three lines changed. Still at the 17.1 and 17.3 values on other lines and not touched here: the key_figures cell of CAP1 (switches at 1.9 mm, 3.1 mm inside; 17.3 says 2.1 mm and 3.6 mm), the HSG1 line (joystick opening 5.0 mm, record cap 5.0 x 3.0, shoulders 3.1 mm) and the cell, motor and pad lines (cell 1.6 x 6.0 x 38, 20 to 26 mAh; pads at 180 degrees). [History: the recording light parts and the nub were removed in v7, see the v7 note below.]

RESULT: done, bom.csv has 78 lines and 128 designators, 53 lines carry a maker order code, and check_bom.py exits 0.

Note added 2026-11-10 (21:40), architecture 17.10: the cell BT1 is 1.6 x 6.0 x 28.4 mm on its centre line, from -39 degrees through the bottom to +167, about 15 to 20 mAh. This replaces the figures of lines 19 and 44 above (38 mm, 20 to 26 mAh), which are kept as the history of the change. The HSG1 line follows 17.8 and 17.10 (block 3.85 mm at the centre, joystick frame at +150, pill at +88, 7 sizes as files).

Note added 2026-11-10 (A6 wiring task; architecture 17.11, 17.12, 17.13; review F04, F05, F07, F13, F14, K1 to K22), history above not rewritten:
- U2 is the Nordic nPM1304, CSP-35 (17.13). Its order code is EMPTY on purpose (open action S18: Nordic). `parts/research-npm1304.md` section 4 lists nPM1304-CAAA-R and -R7 from Nordic spec Table 11; that disagrees with the brief ("not in the research") and was not used: the lead can close S18 from it. R71, R72 (VSET resistors), C71 to C80, L71, L72 keep the nPM1300 kit design values and carry "to confirm against the nPM1304 product specification (S18)". The U2 and BT1 lines carry no nPM1300 charge limits: the charge settings of the files are 15 mA and 4.35 V.
- One control: CAP2 (record button cap) is removed from the list; SW2 stays on BTN_REC as the switch under the centre of the joystick nub (CAP1). The item text of SW2 still contains the words "record button" because `tools/check_bom.py` matches the function name "Record button" of architecture section 2. [History: the recording light parts and the nub were removed in v7, see the v7 note below.]
- Charging pads CP1 to CP4: on the inside face of the band (17.12). Flex tails: A (joystick side) 8 pads = four direction switches, SW2, motor pair, ground; B (other side) 7 pads = cell, temperature sensor, four pads. The motor's tail is confirmed by the lead after the inside model (table BAND_SPLIT in `design/ecad/ring/make_netlist.py`). Positions that 17.11 says are measured again (motor, cell arc, protection circuit, joystick zone) carry no angle now.
- U10 (TI SN74AXC4T774RSVR) and its 100 nF capacitors C81, C82 are new (review F07: storage at 3.0 V against 1.8 V main chip balls), read from TI's datasheet SCES898C; price and stock not read (NEW-12).
- Microphone: SNR 67.5 dB(A), supply 1.62 to 3.60 V, bottom port, per `design/datasheets/mic-research/im68d128b-brief.txt` (architecture.md section 2 still says 68 dB(A)). R41 key figure now (3.0 V - 2.0 V) / 680 ohm = 1.5 mA (K16). Reference cells now hold one token per designator, separated by commas without spaces. [History: the recording light parts and the nub were removed in v7, see the v7 note below.]

Note added 2026-11-11, architecture 17.15 and 17.16: the cell BT1 is 1.6 x 6.0 x 39.36 mm on its centre line at US 9, from +48.7 degrees through the bottom to -98.0 degrees, about 20 to 27 mAh (this replaces the 28.4 mm and 15 to 20 mAh of the note above). The motor M1 is the Jinlong W0525AB001D (5.0 x 2.5 mm, below 80 mA running, below 175 mA at start); it replaces the Vybronics VC0720B088L of lines 17 and 43 above, which does not fit the inside model. No price was read for it. Update 2026-11-11, architecture 17.26: the cell is 39.175 mm on its centre line and ends at -99.0 degrees at US 9; the figures 39.36 mm and -98.0 degrees above are the values before 17.26.

Note added 2026-11-11 (wiring A7; architecture 17.16 to 17.22; details in `design/ecad/ring/sch-notes.md` section 12), history above not rewritten:
- U2 has its order code nPM1304-CAAA-R7 (Nordic spec Table 50, page 168). R71, R72 are confirmed by Table 36 (page 156). C71 is now 1.0 uF 25 V X5R (Table 37; the 4.7 uF part was 6.3 V); new lines C85 (2.2 uF on VBAT), C86,C87 (1.0 uF on each load switch output, Nordic configuration 2), C88 (third 10 uF on VSYS). Their order codes are empty: no maker sheet of a matching part is on file (NEW-13).
- Motor: Q1 and D1 are deleted; new lines U11 (TLV75530PDQNR, 3.0 V regulator from the cell) and C83,C84 (10 uF); M1's S21 is closed by the motor study; R61 and R62 texts follow.
- Microphones: U5,U6 are the Knowles SPK0641HT4H-1 (S23 open for the reel code). C35,C36 must be Class 1 dielectric (Knowles sheet 4), so their old X5R code is removed (NEW-14). MEM1,MEM2 and GSK2,GSK3 follow the floor-hole path. tools/check_bom.py now fails on 3 tokens of architecture section 2 (IM68D128B, IM68D128BV01XTMA1, NSR0230P2T5G); the rows to change are in sch-notes.md 12.4.
- Recording light: R41 820 ohm; LED1 on the board's under face, pad 1 cathode; new lines LG1 (light guide) and LP1 (light plug). [History: the recording light parts and the nub were removed in v7, see the v7 note below.]
- BT1: 20 to 27 mAh at US 9 (20.3 to 27.1), 17.6 mAh smallest at US 7 (architecture 17.26; before it 18.2 mAh, 17.17).

Note added 2026-11-11 (design v7; architecture 17.29, 17.30; wiring A8, `design/ecad/ring/v7-wiring-notes.md`), history above not rewritten:
- Lines removed in v7: LED1, R41, LG1, LP1 and Q2 (the recording light, its resistor, its guide, its plug and its transistor). A recording shows on the screen (17.30). 82 part lines remain.
- CAP1 is the round joystick cap: one custom moulded part in Covestro Makrolon 2407 colour 901510 black polycarbonate, 4.40 mm, rim 1.400 mm above the frame, dish and three ridges, flange 6.90 x 6.40 x 0.40, SPI A-2 with a VDI 3400 Ref 21 top face.
- New line FRM1: the fixed round frame, titanium grade 5 (Ti-6Al-4V), 5.40 outer, 4.80 bore, 1.30 long, coated with the body, bonded with 3M Scotch-Weld DP420 Black (0.10 mm radial gap).
- HSG1: round joystick opening 5.6 mm and titanium grade 5; GL1: no opening in the print; ADH1: full face; SW1 to SW5: up, down, toward the hand, toward the fingertip, centre.
- `tools/check_bom.py` now fails on 4 items of architecture section 2 (the rows "Light transistor" DMN2450UFB4 and "Recording light" KPG-1005SURC-TT): those rows are the lead's to remove (removed in v7).

Note added 2026-11-12 (design review 3, H06, H15, H11):
- Cover glass GL1 plan outline: 29.2958 x 14.429 mm, taken from the maker file (design/mfg/parts/index.csv line 14, the glass of the accepted exterior ring-merged32h.step). The inside model uses the same glass solid; its placement row cover_glass now gives 29.296 x 14.429 (the 29.100 x 14.560 there was a stale size note, corrected by the lead on 2026-11-12). Earlier values in the lines above (29.3 x 14.75, 28.6 x 13.6) are history.
- Motor M1: the angle is given per ring size (-47.0, -45.5, -44.0, -45.0, -43.5, -42.5, -42.5 degrees on US 7 to 13), from design/mfg/specs/body.md.
- tools/check_bom.py has rules 8 to 13 (designators against the netlist and the model's placement file, removed-in-v7 names, pad order, motor angles, glass outline, RT1 place).

Note added 2026-11-13 (W1 rounds 1 and 2, with the lead's rulings; reasons in `design/ecad/ring/pcb/footprint-notes.md` section d and "Round 2"):
- Every line below carries only a code that a saved maker document shows. C71, C86 and C87: Murata GRM155R61E105KA12D (1.0 uF 25 V X5R 0402; `w1b_murata_grm155r61e105ka12.pdf` p1, p2). RT1: Murata NCP15XH103F03RC (`w1b_murata_ncp15xh103f03rc.pdf` p2). L71, L72 (and L10): Murata 1269AS-H-2R2M=P2 (`w1b_murata_1269as-h-2r2m.pdf` p2, land p5). C85 and C60: Kyocera AVX 0402ZC225KAT2A (AVX X7R table PDF p3, row 2.2 uF 0402 10 V). C35 and C36: Kyocera AVX 04025A102JAT2A, 1.0 nF C0G 0402 (AVX C0G table PDF p3).
- C60 changed from 4.7 uF to 2.2 uF (lead decision 24; storage maker sheet PDF p11).
- C35 and C36 are 1.0 nF, not the 0.1 uF of the Knowles figure: the AVX C0G table has 0.1 uF only in 1206 (2.29 mm high) and 1.00 mm is free. The 0.1 uF value is not met with a Class 1 part of this height. The build guide measures the noise floor.
- C88: Murata GRT188R61A106KE13D (10 uF 10 V X5R 0603, 0.8 mm; `w1c_murata_grt188r61a106ke13.pdf` p1, p2). Stated deviation from Nordic Table 37 (16 V): VSYS never exceeds VBUSOVP 5.5 V (nPM1304 PDF p17), 10 V is 1.8 times that, and no 16 V part with a readable document exists at 1.0 mm or less.
- `tools/check_bom.py` before and after: "failures 0" both times (`ecad/ring/pcb/w1-evidence/check_bom_before.log`, `final_check_bom_after.log`).

## W2 ring main board (2026-11-13)

- LT1 added: antenna frequency trim part, 0201, 0 ohm fitted, from ANT1 pins 2 and 3 (new net ANT_TRIM) to ground (design/wiring/ring-board-plan.md e.2). No order code: no saved maker document shows a 0201 0 ohm code (lead decision 127, 128).
- C89 added: antenna-side shunt of the pi match C89, L4, C13 on ANT3_NODE, 0201, not fitted (ring-board-plan.md e.4).
- TP7, TP10 and TP20 removed with the main chip balls E8 (P1.01), E5 (P1.19) and E6 (P1.24, MIC_B_CLK), which are left unconnected so that the chip escapes on 3 signal layers (ring-board-plan.md a.2; lead-decisions.md row "2, 3, 6, 8, W2"). The test pad lines of bom.csv now list 13 and 2 pads.
- `tools/check_bom.py` after the change: "failures 0" (`<work>/ring-board-evidence/a_check_bom.log`).
- RC1 (radio corner, inside model v9): resin part of the body round the antenna, X -14.80 to -8.60, Y 2.05 to the skin, 26.42 cubic mm (design/mech/thin/model-v9-notes.md section f); resin Master Bond EP30Med as the liner (lead-decisions.md row "liner resin"); made before the board goes in and bonded to the body (model-v9-notes.md section h), colour and seams open (S24, S6).
- CP1 to CP4 (charging pads): the pad is a gold-plated disc 1.6 dia x 0.07 thick soldered on its land (design/ecad/band/band-interface.md line 141); the parts list row no longer leaves "pad part or plating" open; the disc has no maker order code yet.
- R73 added (2026-11-13, circuit change C1, lead-decisions.md row "sim finding 1"): 330 kohm 0201 from VBUS to GND, Yageo RC0201FR-07330KL; the code follows the coding of the series RC0201FR-07 (parts/order-codes.md section 1) and is not confirmed at a distributor.
- C83 and C84 are two lines (2026-11-13, circuit change C2, lead-decisions.md rows "sim finding 4 (item 41)" and "sim finding 4, correction"): C83 stays 10 uF GRM155R60J106ME15; C84 is 4.7 uF Murata GRM155R61A475MEAAD, same 0402 footprint and nets.
- C90 added (2026-11-13, circuit change C3, pmic-caps-facts.md G5 and D7): a second 10 uF 0402 Murata GRM155R60J106ME15D on VDD_3V0 beside C79, in the 10 uF row of C74, C75, C78, C79 (quantity 5): nPM1304 Table 18 page 45 asks 4 uF or more effective.
