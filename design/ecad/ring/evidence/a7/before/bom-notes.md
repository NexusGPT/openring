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
| Thermistor RT1 | text only: now on the cell, wired in flex tail 2 (see conflict 5) | 17.3 |
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
| C13, R41, C76, L71, TP1, TP16, RT1, PCB1 and others without a code | `open_action` reworded so each names who must answer what | rule 4 of the brief |
| Lines named "Schematic addition: ..." | item names shortened (they were cut off mid-word) | none |
| All other lines | unchanged | |

## Conflicts between sections (A5 value kept in the CSV, both stated)
1. Motor: 16.4 says Vybronics VC0625B001L (6 mm coin, wire leads, 2.5 V, 100 mA); 17.3 and 17.4 say VC0720B088L (7 mm, FPC tail, 3.0 V, 85 mA). CSV: VC0720B088L (17 wins). bench-kits.md section 6 also notes a 3 V rating for the VC0625B001L on DigiKey against 2.5 V in the maker spec.
2. Cell: 16.4 flat 2.60 x 11.9 x 19.0 in the block, 37 to 48 mAh; 17.3 curved 1.6 x 6.0 x 38 in the band, 20 to 26 mAh. CSV: 17.
3. Board and glass: 16.4 board 0.4 mm and glass 0.5 mm; 17.4 board 0.3 mm and glass 0.4 mm. CSV: 17.
4. Controls: 16.5 puts joystick and record button on the block wall at X +10.0 and -5.0; 17.1 and 17.3 put them on the band at +38 and +62 degrees. CSV: 17.
5. Thermistor RT1: W13 says on the main board beside the cell; 17.3 says the cell's temperature sensor is wired in flex tail 2. CSV keeps RT1 as one line, with the question in its open action.
6. Microphone slot: 16.3 says 1.4 x 0.4 mm; 17.1 says 1.2 x 0.3 mm. CSV: 17.1.

## Open facts that no file closes (nothing invented)
- IM68D128B order code is LIST only; no saved datasheet (pin order, LR pin, sound port). Price empty.
- SKTAAAE010 outline and land pattern (S9), price (search text only: about USD 0.71 at DigiKey cut tape, not read on the page), production status.
- CSNP32GCR01-BOW price, read and write current.
- Curved cell and its protection circuit: no code, no price (S12). Charge current floor of the nPM1300 is 32 mA, above 1 C for this cell.
- One-piece metal body, band liner, caps, flex tails, glass, adhesive, foam, gaskets, charging pads: no supplier, no drawing (S13, B7, B8, B9).
- Recording light supply (A1 contradiction, still open): architecture section 9 says VDD_MIC 1.8 V through a transistor; the LED needs 2.4 V; R41 and Q2 stay as in W5 (3.0 V, 680 ohm).
- No ESD part on the charging pads other than U9; no gate pull-down question remains (R62, R66 exist). Capacitor heights, crystal load capacitors and the nPM1300 VDD_USB_3V3 net are as listed in A1 notes and not resolved.
- Prices: only entries read from files are filled (U2 nPM1300 GBP 1.25, J1 FH35C GBP 1.76, C4 GBP 0.13, C31 and C32 CAD 0.15, R31 and R32 GBP 0.07, M1 USD 3.23); every other price cell is empty.

## Evidence tags
DS, LIST and CALC as in architecture.md. LIST lines still needing a maker document are those whose `open_action` or `key_figures` say so (U1, U2, IM68D128B, LED1, FH35C).


Note added by the lead, 2026-11-10: the two groups of solder pads for the band flex tails are named J_BAND_A (thumb side, 6 pads) and J_BAND_B (other side, 9 pads), the names the wiring diagram uses (design/ecad/ring/, sheet "Band"). They were J2 and J3 in the first A5 list.

Note added for firmware F3, 2026-11-10: the texts of GL1 (cover glass), CAP1 (joystick cap) and CAP2 (record cap) follow architecture 17.8: GL1 is one formed piece curved across the finger, 29.3 x 14.75 mm, 1.10 mm thick at its centre; CAP1 is a rounded rectangular nub 4.6 x 3.6 mm in a 6.4 x 5.4 mm frame at the bottom of the band; CAP2 is a pill 4.4 x 2.4 mm. Only the size and description cells of those three lines changed. Still at the 17.1 and 17.3 values on other lines and not touched here: the key_figures cell of CAP1 (switches at 1.9 mm, 3.1 mm inside; 17.3 says 2.1 mm and 3.6 mm), the HSG1 line (joystick opening 5.0 mm, record cap 5.0 x 3.0, shoulders 3.1 mm) and the cell, motor and pad lines (cell 1.6 x 6.0 x 38, 20 to 26 mAh; pads at 180 degrees).

RESULT: done, bom.csv has 78 lines and 128 designators, 53 lines carry a maker order code, and check_bom.py exits 0.

Note added 2026-11-10 (21:40), architecture 17.10: the cell BT1 is 1.6 x 6.0 x 28.4 mm on its centre line, from -39 degrees through the bottom to +167, about 15 to 20 mAh. This replaces the figures of lines 19 and 44 above (38 mm, 20 to 26 mAh), which are kept as the history of the change. The HSG1 line follows 17.8 and 17.10 (block 3.85 mm at the centre, joystick frame at +150, pill at +88, 7 sizes as files).

Note added 2026-11-10 (A6 wiring task; architecture 17.11, 17.12, 17.13; review F04, F05, F07, F13, F14, K1 to K22), history above not rewritten:
- U2 is the Nordic nPM1304, CSP-35 (17.13). Its order code is EMPTY on purpose (open action S18: Nordic). `parts/research-npm1304.md` section 4 lists nPM1304-CAAA-R and -R7 from Nordic spec Table 11; that disagrees with the brief ("not in the research") and was not used: the lead can close S18 from it. R71, R72 (VSET resistors), C71 to C80, L71, L72 keep the nPM1300 kit design values and carry "to confirm against the nPM1304 product specification (S18)". The U2 and BT1 lines carry no nPM1300 charge limits: the charge settings of the files are 15 mA and 4.35 V.
- One control: CAP2 (record button cap) is removed from the list; SW2 stays on BTN_REC as the switch under the centre of the joystick nub (CAP1). The item text of SW2 still contains the words "record button" because `tools/check_bom.py` matches the function name "Record button" of architecture section 2.
- Charging pads CP1 to CP4: on the inside face of the band (17.12). Flex tails: A (joystick side) 8 pads = four direction switches, SW2, motor pair, ground; B (other side) 7 pads = cell, temperature sensor, four pads. The motor's tail is confirmed by the lead after the inside model (table BAND_SPLIT in `design/ecad/ring/make_netlist.py`). Positions that 17.11 says are measured again (motor, cell arc, protection circuit, joystick zone) carry no angle now.
- U10 (TI SN74AXC4T774RSVR) and its 100 nF capacitors C81, C82 are new (review F07: storage at 3.0 V against 1.8 V main chip balls), read from TI's datasheet SCES898C; price and stock not read (NEW-12).
- Microphone: SNR 67.5 dB(A), supply 1.62 to 3.60 V, bottom port, per `design/datasheets/mic-research/im68d128b-brief.txt` (architecture.md section 2 still says 68 dB(A)). R41 key figure now (3.0 V - 2.0 V) / 680 ohm = 1.5 mA (K16). Reference cells now hold one token per designator, separated by commas without spaces.

Note added 2026-11-11, architecture 17.15 and 17.16: the cell BT1 is 1.6 x 6.0 x 39.36 mm on its centre line at US 9, from +48.7 degrees through the bottom to -98.0 degrees, about 20 to 27 mAh (this replaces the 28.4 mm and 15 to 20 mAh of the note above). The motor M1 is the Jinlong W0525AB001D (5.0 x 2.5 mm, below 80 mA running, below 175 mA at start); it replaces the Vybronics VC0720B088L of lines 17 and 43 above, which does not fit the inside model. No price was read for it.
