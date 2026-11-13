# Case notes (version C4): my choices, assumptions, conflicts, open points

C4 is the pebble case the owner picked ("A: flat on a post"). Everything after the heading "Carried from C2" is the C2 text, valid for the electronics. The C3 mechanics notes (M1 to M11, A1 to A6, R1, F1 to F5) are replaced by the C4 sections below; the C3 files are kept in `out/old_C3/`.

## C4: what I chose myself, and why

| # | Choice (mine) | Why |
|---|---|---|
| M1 | Ring stands with its band axis vertical; the band's bottom face rests on the floor, the block hangs in a pocket beside the post | this is concept A; the block is 29.3 mm long, so the case is as tall as the stack under the floor plus the block |
| M2 | Band clamped between the pins (inside) and two flat flanks at +-20 degrees of a V wall (outside) | the band is 2.6 mm thick at every size, so the pad row stays within a fraction of a millimetre in height for all seven bores with a fixed post; the V wall also guides the bore centre by 2.59 mm |
| M3 | Pins horizontal on a rigid-flex PCB2 of three islands in the post's lug (outer islands recessed), pin row at the pad positions of US 10, design height 2.35 mm at US 10 | the pad row is an arc: on one flat board the outer pins would differ from the inner ones by 0.5 mm, more than the pin window; stepped, the whole spread over sizes and pins is 0.144 mm |
| M4 | Contact window 1.90 to 2.65 mm (0.15 to 0.90 mm below the free height 2.80) | stroke of the Harwin pin is not in the file read; the window is my assumption (A3) |
| M5 | Flat 4.0 mm cap lid on a vertical pin at the -X, -Y corner, four 0.4 mm glides, two magnets | the ring is entirely below the rim, so the lid never has to lift over it; the pivot corner was found by a search so the swung lid uncovers the whole well and pocket (out/work_c4/pivot_search.py) |
| M6 | Rim 0.3 mm above the block's top, lid 0.4 mm above the rim | lid 0.7 mm from the ring (needs 0.5) |
| M7 | Pocket = the block's widest outline over all sizes including its flare into the band (about 20.1 mm wide) with 0.15 mm each side, relief to 20.8 mm beside the band | the block flares into the band over 4 mm (junction blend); a pocket that follows only the 14.75 mm block would have kept the roll tighter but was not built (time): see R1 |
| M8 | Stack under the floor: bottom plate 1.5, cell 8.5, PCB1 1.0 above it, floor 1.8: floor at 17.2 mm | the cell cannot stand under the pocket's deep end; J1 (3.31 mm) sets the height above PCB1 |
| M9 | Plan corners: radius 4 at the -X end, 14 at the +X end | the cell (40 x 23) has square corners at the -X end, the +X end holds only the pocket |
| M10 | Finger notches in the rim beside the pocket | the rim is 0.3 mm above the block's top, so there is nothing to grip without them |
| M11 | No liner part: the 0.6 mm soft skin of the concept is a finish inside the dimensions | fewer parts; clearances are to the finished surface |
| M12 | Other ring sizes computed (US 9 block, glass and joystick kept; band a new tube with the bore of sizes.csv; joystick moved radially; pads computed) | per-size ring files for the new exterior do not exist yet |
| M13 | Pad row 1.0 mm from the band's middle toward the light end, pad diameter 1.0, arc pitch 2.0 at the inner radius (all parameters in case.py) | the pitch and diameter are being fixed by the ring's inside model; the offset keeps a flipped ring 2.0 mm off the pins |
| M14 | The sentences "In the 60 minutes a ring charge takes, the case copies 18.9 recorded hours" and "Chosen 700 mAh: 22.0 charges" now stand in case-architecture.md in the form the explorer extractor reads; the figures are those of C3 | the extractor could not read them in C3 (explorer/collector/extract/case.py FACTS) |

## C4: what is assumed

- A1. Pad order along the band: VBUS, D-, D+, GND with increasing Y in the case frame. The ring files do not name the pads (`design/architecture.md` 17.12 gives the order only).
- A2. Pad disc 0.1 mm thick, flush with the inner face, in the resin liner (17.12); the bore of the file is the face of the liner.
- A3. Pin working window 1.90 to 2.65 mm (travel up to 0.90 mm from the free height); the Harwin stroke is not in the file read.
- A4. Ring sizes: bore from sizes.csv (17.32 to 22.20 mm), band 2.6 mm thick at every size, block fixed to the top of the band, joystick at 78 degrees (as the files of 32c do: bbox of the US 7 and US 13 files read only for these facts).
- A5. The junction blend between band and block is the US 9 one at every size (the computed sizes keep the US 9 body above ring Z = -1.5): it overshoots slightly for sizes under US 9; the per-size check used computed bores.
- A6. The case shell and lid are printed or cast in a non-conductive material with a metal-look finish (K2).

## C4: conflicts and findings

- **K1 (conflict, pin pitch).** The ring's pad pitch is 1.6 mm. The C2 pin Mill-Max 0981-0-15-20-87-14-11-0 has a body of 1.94 mm (C2 case.py) and a flange of 2.11 mm (case-architecture.md section 3 row P1-P4): two pins cannot stand 1.6 mm apart. Tilting them does not help: the exposed plunger is 0.87 mm above the body at mid stroke, so the bodies at the tip end stay 1.6 mm apart however the axes are tilted (tried at +-20 degrees in my first model: the pins collided, 0.136 mm3, saved in out/work/run_check_1.log). Pad pitch that would fit the 0981: the flange must clear its neighbour, so at least 2.11 mm and in practice 2.2 mm (flange 2.11 plus 0.09); four pads then span 3 x 2.2 + 1.0 = 7.6 mm on the 8.0 mm band, 0.2 mm from the band edges: not recommended. A pin with a barrel of 1.5 mm fits 1.6 mm (0.1 mm between barrels): Harwin P70-6000045R (barrel 1.50, plunger 0.60, free height 2.80, working height 2.10, 0.39 N, 1 A; `design/parts/ui-pass3.md` line 190). The model uses that pin so that the case can be built and checked. Source of its figures: `design/datasheets/p3_harwin_p70_chipdip.pdf` (distributor-hosted Harwin catalogue page). I re-read today in its text copy `design/datasheets/p3_harwin_p70.txt`: 1 A, 0.39 N +-0.09 N at 2.10 mm working height, 2.80 overall. Barrel 1.50, plunger 0.60 and the length list come from the drawing as read by another helper in `design/parts/ui-pass3.md` line 190; I did not open the drawing; barrel length 1.85 is my reading. Status: [LIST] proposed, not confirmed (no stroke, no maker confirmation). The BOM line P1-P4 (item 15) still lists the 0981: decision needed (lead or owner): swap the pin, or change the ring's pad pitch.
- **K2 (conflict, metal shell and Wi-Fi).** The concept shows satin METAL. U1's Wi-Fi antenna sits inside the shell; a closed metal shell screens it. The model assumes a non-conductive body with a metal-look finish (supplier item S7); a real metal shell would need an antenna window or an external antenna. Needs a decision (owner or lead).
- **K3 (finding, flip).** The pocket blocks a ring turned 180 degrees or across (US 7, 9, 13: intersections in the check). A ring FLIPPED over (band axis reversed, nub on the other side) is not blocked at every size: US 7: 0.00 mm3 (not blocked), nearest pad 2.00 mm; US 9: 2.34 mm3 (blocked), nearest pad 2.00 mm; US 13: 38.88 mm3 (blocked), nearest pad 2.00 mm. The only asymmetric feature of the ring is the joystick nub, and a nub on the +Y side stays inside the well that the larger sizes need, so no size-independent wall can stop it. No pin reaches a pad on a flipped ring (nearest 2.00 mm), so nothing is energised (the pads sit in the liner, the pins touch resin). A ring-side feature (for example a chamfer on one end of the block) would let the pocket block the flip. Needs the ring design.
- **R1 (open, roll).** The band is a cylinder, so the V wall does not fix the ring's turn about its own axis; the pocket's side walls do (a pocket about 20.1 mm wide, wider than the 14.75 mm block, so loose). Measured turn before the ring touches the shell (INFO lines in the check, not failures): US 7: +4.50 / -4.50; US 9: +2.50 / -2.50; US 13: +0.00 / -0.00 degrees; the pad row moves at most 0.680 mm against 0.2 mm a 0.6 mm pin tip can take on a 1.0 mm pad: NOT held. A nub channel (as in C3) or a ring-side feature is needed; not designed. The check proves the nominal pose only.
- **K4 (size).** The concept was 46.0 x 46.0 x 37.7 mm without the cell, the board, the socket and the light. With them the case is 43.2 x 44.0 x 40.6 mm. Drivers: the stack under the floor (floor at 17.2 mm: bottom plate 1.5, cell 8.5, PCB1 1.0 with the 3.31 mm socket, 0.3 mm gaps, floor 1.8) and the block standing 29.3 mm tall on the band.
- **F1 (pins).** The pin spread over the sizes and the four pins is 0.144 mm (heights 2.277 to 2.421); with 0.2 mm of tolerance a pin needs 0.34 mm of stroke. The first design had one flat PCB2: spread 0.502 mm and the outer pins' barrel edges touched the concave pad row (0.0034 mm3 in run_check_1/2); the stepped PCB2 and the working-height window fixed both. The rigid-flex island board is my proposal, not a priced part (BOM PCB2). If the Harwin P70 stroke is below 0.4 mm, the pin must change (K1).
- **F2 (pitch range).** Pitch 1.6 to 2.4 mm is held by the post (1.6: barrels 1.5 mm; above 2.4 the outer pins' barrel edge has no margin over the pad row at US 7, and the outer barrel edge reaches 4.35 mm of PCB2's 4.9 mm half width at 2.4). Pins-only runs at 1.6, 2.4 and 2.6 mm (pitch_1.6.log, pitch_2.4.log, pitch_2.6.log, all PASS) are in the proof files; only the pins part of the check ran at those pitches, the full check ran at 2.0 mm.
- **F3 (lid).** Opened, the lid lies outside the base and is held only by the pivot pin: bench item B7 (friction fit, droop). The magnets' pull across the 0.4 mm gap is not measured (BOM item MECH9).
- **F4 (BOM).** Item 15 (Mill-Max 0981) still lists the pin that does not fit; PA1-PA4 (Harwin P70-6000045R) is the proposed replacement, [LIST] proposed, not confirmed: decision needed (lead or owner). Reference cells were rewritten so that every reference is one token (P1-P4, R3-R4, R1-R2, R6-R7, R8-R10, R12-R13, RT1-RT2; TH1 and C30 became lines of their own, items 79 and 80); no electrical line or designator was removed.
- **F5 (my error).** My first runs wrote into `out/work/` and overwrote three C3 proof logs there (run_case_1.log, run_case_2.log, run_check_1.log); the C3 run_check_3.log and its summary in `out/old_C3/case-notes.md` are intact. All C4 proof files are in `out/work_c4/`.
- **F7 (look).** The drawings (out/case-c4-closed.png, out/case-c4-open-ring.png) show a rounded box: straight walls with large plan corners, flat 4.0 mm cap. It is not yet the organic pebble of the reference picture; softening the walls (barrel the sides) is a look step that needs the cell and board clearances re-run.
- **F6 (pad side).** `design/case/concepts/notes.md` says the C3 architecture put the pads outside; C4 follows 17.12 (inside).

## C4: proof files (all in out/work_c4/)

- run_check_final.log: case.py then case_check.py on the delivered files, exit 0; last line "case_check: PASS, 1807 pairs checked, 0 failures, ring sizes US [7, 8, 9, 10, 11, 12, 13]".
- run_check_1.log and run_check_2.log: the first checks, red (cell outside the cavity, pocket too narrow at the band flare, lid still covering the ring, pins against the ring body): the base for the changes made, kept.
- pitch_1.6.log, pitch_2.4.log, pitch_2.6.log: pitch_check.py (the pins part of the check: lateral offset, height window, pin barrel against the ring body, US 7 to 13), exit 0 each; not the full check.
- broken/run_check_broken.log: the same check with all pins moved 1.0 mm in X (CASE_PIN_SHIFT_X=1.0, own out folder): exit 1.
- gen_arch.py, gen_notes.py, bom_c4.py, draw_c4.py, pivot_search.py, dbg1.py, dbg2.py: scripts that wrote the documents and pictures or located the problems.

## questions_for_owner

1. Pin conflict K1: swap to a 1.5 mm barrel pin (Harwin P70-6000045R, stroke unknown) or keep asking Harwin for the stroke?
2. Shell material K2: non-metal body with a metal-look finish, or metal with an antenna window?
3. Flip K3: can the ring get an asymmetric block end so that the pocket blocks a flipped ring?
4. Case size 43.2 x 44.0 x 40.6 mm: accept? (the concept's 46.0 x 46.0 x 37.7 mm left out the electronics)



# Carried from C2 (electronics unchanged)


Tags as in `case-architecture.md` (DS, LIST, CALC). Arithmetic: `evidence/calc_case.log`.

## Rejected choices and the fact that rejected each

| Rejected | Fact | Source |
|---|---|---|
| ESP32-P4 plus a Wi-Fi companion (for example ESP32-C6-MINI-1) | ESP32-P4 has "USB 2.0 High-Speed OTG" but no Wi-Fi: the word appears only in the trademark notice; it needs a second radio chip, a QFN104 10 x 10 mm package and outside flash. The gain is 2.50 min per recorded hour (3.87 against 6.37 min, C2 figures), because the ring's SPI storage read (2 MB/s) limits high speed anyway | DS case_esp32p4_ds.pdf p.1, p.4; evidence/read_p4.log; CALC |
| ESP32-S3-WROOM-1 | Same chip and the same full-speed USB as the MINI-1; larger module | DS case_esp32s3_ds.pdf p.55; size LIST |
| ESP32-C3-MINI-1 (listed in parts/power.md) | No USB OTG host on the C3 (USB Serial/JTAG only) | LIST, not read in a saved document |
| BQ25180 or BQ24074 as the case charger | Their TI pages list no boost output (parts/power.md 6b); the ring needs 5 V from the case cell | parts/power.md section (6) |
| A 500 mAh case cell (for example DNK LP503035, 5 x 30 x 35 mm) | 500 mAh x 3.7 V = 1.85 Wh gives 2.33 ring charges, not 3; 3 charges need 644 mAh | CALC; DNK product page evidence/html/dnk_503035_text.log |
| DNK682624 (26 x 26 x 6.8 mm) | 275 mAh | DS cell_dnk_DNK682624.pdf |
| DNK652545 (6.5 x 25 x 45 mm, 700 mAh) | 45 mm long: the case would be 5 mm taller than with DNK852338 (40.0 mm with PCM) | DS case_cell_dnk652545.pdf, case_cell_dnk852338.pdf |
| Hall switch DRV5032FA plus a lid magnet for lid detection | The only place for the sensor is the pin board, about 15 mm under the lid; a 4 x 2 mm magnet gives about 1.4 mT there (on-axis estimate, LIST), below the 4.8 mT maximum operate point | DS case_drv5032.pdf p.1; estimate LIST |
| Magnets alone holding the lid | The 4 pins push up with 4 x 90 gf = 360 gf; a printed snap latch carries it with no magnet sizing | DS p3_millmax_0981.pdf p.3 |
| Magnetic pogo connectors (EDAC 686 series, listed in parts/power.md) | No dimension or working-height drawing was readable; the Mill-Max 0981 sheet gives height 5.182, stroke 1.397, mid stroke 0.70 | parts/power.md (3); DS p3_millmax_0981.pdf p.1 |
| Mill-Max 0900-8-15-20-76-14-11-0 or Harwin P70-6000045R instead of Mill-Max 0981 (read later by another helper, design/parts/ui-pass3.md lines 167 and 190) | 0900-8: mid stroke 0.495 mm leaves a +-0.25 mm window against +-0.35 mm for the 0981; P70: 0.39 N at 2.10 mm working height, 1 A. Kept as fallbacks if the 0981's 90 gf (4 pins = 360 gf) proves too high for the lid latch (bench B2); the 0981 has a full drawing read [DS] and is already proven in the model | design/parts/ui-pass3.md; DS p3_millmax_0981.pdf |
| Copying straight to Wi-Fi with no case storage | Copy would wait for Wi-Fi each time; with an 8 GB buffer (U4) the ring is free after the copy and the upload runs later | design choice |

## Open points (a bench test or another helper must close)

| # | Open point | Who |
|---|---|---|
| B1 | The ring's nRF54LM20A high-speed USB device must enumerate at full speed under the ESP32-S3 host. USB 2.0 requires it (LIST); Nordic's USBHS page was not readable. Test on the nRF54LM20 DK with an ESP32-S3 board before layout | bench, Nordic (S2) |
| B2 | Lid pad force: the 1.0 mm silicone pad compressed to 0.7 mm must push the block down with more than 360 gf; latch strength in PA12 | bench |
| B3 | Ring presence by touch (IO4, electrode E1 under 1.0 mm of PA12): reading change with the ring block present, and Deep-sleep wake on it | bench |
| B4 | LED1 green and blue from 3.3 V: VF typ 3.3 V at 20 mA [DS], so at 3.3 V drive the current is only a few mA; check brightness, else drive the anodes from SYS through a transistor | bench |
| B5 | Boost efficiency at 0.1 to 0.3 A (taken as 0.85); the 3.26 charges depend on it | bench, TI (S5) |
| B6 | Load on PMID while charging from USB-C: chosen because PMID equals VBUS through the input FET; TI to confirm | TI (S5) |
| O1 | Pad order on the ring's contact board is not written in the ring files (evidence/pad_order_search.log). The case uses VBUS at Y -3.81, D- at -1.27, D+ at +1.27, GND at +3.81 | ring mechanics helper, owner |
| O2 | Pads assumed flush with the block underside (Z = 0). A recess of up to 0.35 mm still leaves the pins inside the working window (0.349 to 1.048 mm); a deeper recess needs a raised pad seat | ring mechanics helper |
| O3 | Band modelled as a circle touching the block underside at Y = 0, centred on X = 0, 8 mm wide. The slot takes any band inside radius 13.6 mm and X from -4.6 to 4.6 | ring mechanics helper |
| O4 | `design/architecture.md` section 8 says the case reads "over high-speed USB" with 4 min per hour; this case reads at full speed, 6.37 min per recorded hour (C2, 464.4 MB per hour). Section 8 and the T3 row of section 10 need the change (file owned by the lead) | lead |
| O5 | Requirement C2 says "500 mAh or more: 3 full charges"; by the arithmetic 500 mAh gives 2.33. The case uses 700 mAh (3.26) | owner |
| O6 | Not modelled in 3D: screws (holes are modelled), wires, passives, the lid's opening swing; the check covers the closed state only | next step |
| O7 | Unit prices: none read; the price column of case-bom.csv is empty for every line | buyer |
| O8 | Case firmware update: USB-C data lines go to the charger's adapter detection only; firmware goes over Wi-Fi or the UART test pads | firmware helper |
| O10 | Two files in design/datasheets/ named .pdf are HTML error pages from blocked downloads: case_cell_dnk503035.pdf, case_cell_eemb_lp503035.pdf (evidence/final_listing.log). out/case_section_pins_US5.png is an earlier drawing (cut at X = -12.6 with US 5, band label misplaced) replaced by case_section_band_US5.png | lead, may delete |
| O9 | Stack tolerance on pin compression: pin length ±0.15 mm [DS Mill-Max standard tolerance], board and print tolerances not measured; the window allows ±0.35 mm around 0.70 | bench |

## Round 2 (C2): schematic conflicts and risks, decided

Source: `design/ecad/case/sch-notes.md` sections 6 and 7. Datasheet reads saved in `evidence/r2_read1.log` to `evidence/r2_read5.log`; figures in `evidence/calc_case_c2.log`.

| Item | Decision | Datasheet fact |
|---|---|---|
| TPS2553 pins | EN 3, FAULT 4, GND 2, ILIM 5, IN 1, OUT 6 (architecture corrected; schematic already right) | Table 5-1, SOT-23 column of TPS2553 |
| LED1 | common anode on 3V3, GPIO through R8-R10 to the cathodes, active low (architecture corrected; schematic already right) | package drawing p.1 as read by the schematic helper |
| DSEL | R28 10 kΩ to 3V3 | Table 6-1: "Connect the DSEL to a logic rail via 10-KΩ resistor" |
| E1 wire | W7, fifth pin-board wire | |
| TPS63802 divider | R3 511 kΩ, R4 91 kΩ: 3.308 V | Table 10-5, 3.3 V row: 511 and 91 |
| BQ25895 L1 | 1 µH | section 9.2.2: "1-µH and minimum of 20-µF output capacitor is recommended"; the 2.2 µH figure label is not used |
| Risk 1, ESD 5.5 V on VRING; and the 9 V / 12 V handshake | U2 D+/D- disconnected from J1, so U2 cannot detect a DCP and never starts the handshake; firmware also clears HVDCP_EN and MAXC_EN. VRING then stays at USB VBUS or the 4.998 V boost | REG02: HVDCP_EN and MAXC_EN default 1; section 8.2.3.3.1: handshake raises "5 V to 9 V / 12 V"; TPS2553 7 V absolute maximum; TPD4E05U06 5.5 V operating maximum |
| Risk 2, PMID load while charging | open, TI item S5 (unchanged) | |
| Risk 3, full speed over pins and wires | open, bench B1 (unchanged) | |
| Risk 4, SD pull-ups | R29, R30 10 kΩ on SD_D2, SD_D3 (all 4 data lines and CMD now pulled up) | Zetta: RCMD, RDAT pull-up 10-100 kΩ |
| Risk 5, strapping pins | IO3, IO45, IO46 stay open: GPIO0 weak pull-up 1, GPIO45 weak pull-down 0, GPIO46 weak pull-down 0 give SPI boot with the default VDD_SPI; GPIO3 floating matters only with EFUSE_STRAP_JTAG_SEL burnt (default 0) | ESP32-S3 series datasheet section 3, Table 3-1 p.32 |
| Risk 6, LED brightness | open, bench B4 (unchanged) | |
| Risk 7, TS window | use E96 5.23 kΩ and 30.1 kΩ (TI Figure 9-1 values, nearest to 5.21 and 29.87) | section 8 example and Figure 9-1 |
| Risk 8, OTG pin floating | R27 100 kΩ CHG_OTG to GND | REG03 bit 5: "1 – OTG Enable (default)"; boost runs when the OTG pin is high and OTG_CONFIG = 1 |
| Risk 9, MODE and PG | keep (power save, PG unused) | |

Ring-side facts taken: the ring records only after a long press (no listening mode), which changes nothing in the case; 464.4 MB per recorded hour gives 381.9 s = 6.37 min.

## Changes the schematic must take

Each changes a connection or a value in `design/ecad/case/` (owner of that folder acts; nothing was sent):
1. Disconnect U2 D+ (pin 2) and D- (pin 3) from J1 A6/B6 and A7/B7; leave J1 A6, B6, A7, B7 and U2 pins 2, 3 not connected (net USB_C_DP and USB_C_DN removed).
2. Add R27 100 kΩ from CHG_OTG (U1 IO6, U2 OTG pin 8) to GND.
3. Add R28 10 kΩ from U2 DSEL (pin 24) to 3V3 (DSEL is now connected, not no-connect).
4. Add R29 10 kΩ from SD_D2 (U1 IO10) to 3V3 and R30 10 kΩ from SD_D3 (U1 IO9) to 3V3.
5. Values only: R3 560 kΩ -> 511 kΩ, R4 100 kΩ -> 91 kΩ; RT1 5.21 kΩ -> 5.23 kΩ, RT2 29.87 kΩ -> 30.1 kΩ.
No change needed for the TPS2553 pins, LED1, W7 or L1: the schematic already has them as above.



RESULT: done, case outside size 43.2 x 44.0 x 40.6 mm; check last line "case_check: PASS, 1807 pairs checked, 0 failures, ring sizes US [7, 8, 9, 10, 11, 12, 13]"; pin travel needed 0.34 mm (heights 2.277 to 2.421 mm) with pad pitch 1.6 to 2.4 mm held; conflicts K1 pin unconfirmed, K2 metal shell vs Wi-Fi, K3 flipped ring not blocked at every size, R1 roll
