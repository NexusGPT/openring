# Band interface: where each flexible tail meets the main board and its parts (package W4)

Written 2026-11-13 by the W4 builder. Project root: .. Every value has its source (file and line, page of a maker document) or a calculation shown. Status of this file: section 2 (J_BAND land pattern) is final and may be used by the board layout now. Other sections are completed and checked as the boards are built; the last line of band-notes.md says when all is done.

Frames used in this file:
- Model frame (X, Y): the ring model axes. X along the finger (+X toward the fingertip), +Y toward the thumb side. The board underside, seen from below with X to the right, has +Y pointing down the page (design/ecad/ring/pcb/board-notes.md "Coordinates"). A position given as (X, Y) below is the same number in the ring board file (offset OX, OY of that file).
- FLEX1 is the joystick side (-Y). FLEX2 is the other side (+Y). J_BAND_A belongs to FLEX1, J_BAND_B to FLEX2 (design/ecad/ring/netlist.csv, rows `J_BAND_A`, `J_BAND_B`).

## 1. What was fixed, and why (summary)

| Item | Value | Source or calculation |
|---|---|---|
| Flex stack | polyimide core 25 um, copper 12 um both sides, coverlay both sides, finished 0.11 mm | JLCPCB flexible PCB capabilities page, rows "FPC Stack-Up", "FPC Finished Thickness" (2-layer, 25 um dielectric: 0.11 mm) and "Outer Layer Copper Weight" (12 um). Saved: design/ecad/band/evidence/web/jlc_flex_text.txt lines 94-146. 0.11 mm is under the 0.15 mm of the model (design/mech/thin/thin.py line 52 `flex_t=0.15`) |
| Land finish | ENIG (1 to 2 micro-inch gold) | same page, row "Surface Finish" |
| Rules | line 0.08, gap 0.10, exposed land to line 0.25, land to land 0.15, copper to edge 0.30, via 0.30 pad / 0.10 hole | same page: "Minimum Trace Width/Spacing" 12 um: 3/3 mil = 0.076; "Pad-to-Trace Clearance" 0.15 plus the coverlay expansion 0.10 per side ("Coverlay Opening") = 0.25; "FPC Outline" copper to edge 0.3; "Min. Via hole size" extreme 2-layer 0.10/0.30 |
| Minimum bend radius | 0.66 mm (6 x 0.11 mm, static bend); the board fold uses 0.70 mm inner radius | same page, row "Static vs Dynamic Bending" ("Static Bending: Smaller radius allowed (typically 6-10x thickness)") and "Bend Radius" |
| Stiffeners | polyimide 0.10 mm on the back (B.Cu) face under the board foot and under the joystick head | same page, row "PI Stiffener" (0.1 mm available). The model has 0.075 for the head (thin.py line 64): 0.10 is the nearest offered value, see "Changes other files need" in band-notes.md |

## 2. J_BAND_A and J_BAND_B: the lands where each tail meets the main board (FINAL)

Place: the board underside, in the free room beside each floor slot (design/mfg/specs/band-flex-tails.md line 46: free volume 2.6 x 2.2 x 1.03, X -3.5 to -0.9, Y +-3.4 to +-5.6, Z 0.40 to 1.43). The slot is X -3.5 to -1.5, Y +-5.9 (thin.py line 66, 467). The nearest part under the board is U3 (8.0 x 6.2 at X -5, so Y +-3.1; thin-notes placement.csv row `storage`): the lands start at |Y| 3.4, which is 0.3 mm from U3. U11, C83 and C84 stand at X -0.55 and beyond (placement.csv rows `motor_regulator`, `motor_cap_in`, `motor_cap_out`): the lands end at X -1.31, 0.76 mm from them.

Land pattern, both tails: 2 rows of lands, 4 columns. Land size on the board: 0.30 (X) x 0.55 (Y). Column pitch 0.51 mm in X. Row pitch 0.90 mm in |Y|.

Column X (centre): c0 = -3.015, c1 = -2.505, c2 = -1.995, c3 = -1.485.
Row |Y| (centre): far row 3.875 (nearer to the board middle), near row 4.775 (nearer to the slot). The fold of the tail begins at |Y| 5.145.

J_BAND_B (FLEX2, Y > 0). Pin numbers are the netlist's.

| Land | Name | Net | X | Y | Size X x Y |
|---|---|---|---|---|---|
| 1 | CELL+ | VBAT | -3.015 | +3.875 | 0.30 x 0.55 |
| 3 | NTC | NTC | -2.505 | +3.875 | 0.30 x 0.55 |
| 2 | CELL- | GND | -1.995 | +3.875 | 0.30 x 0.55 |
| 7 | GND | GND | -1.485 | +3.875 | 0.30 x 0.55 |
| 6 | D+ | USB_DP | -3.015 | +4.775 | 0.30 x 0.55 |
| 5 | D- | USB_DN | -2.505 | +4.775 | 0.30 x 0.55 |
| 4 | VBUS | VBUS | -1.995 | +4.775 | 0.30 x 0.55 |
| (none) | | | -1.485 | +4.775 | free |

J_BAND_A (FLEX1, Y < 0). (Corrected 2026-11-13: lands 1, 4, 6, 8 were listed in a stale order; the footprint J_BAND_A_BOARD and the boards were right.)

| Land | Name | Net | X | Y | Size X x Y |
|---|---|---|---|---|---|
| 2 | DOWN | JOY_DOWN | -3.015 | -3.875 | 0.30 x 0.55 |
| 3 | LEFT | JOY_LEFT | -2.505 | -3.875 | 0.30 x 0.55 |
| 6 | MOT- | GND | -1.995 | -3.875 | 0.30 x 0.55 |
| 1 | UP | JOY_UP | -1.485 | -3.875 | 0.30 x 0.55 |
| 5 | CENTRE | BTN_REC | -3.015 | -4.775 | 0.30 x 0.55 |
| 7 | MOT+ | VMOT | -2.505 | -4.775 | 0.30 x 0.55 |
| 8 | GND | GND | -1.995 | -4.775 | 0.30 x 0.55 |
| 4 | RIGHT | JOY_RIGHT | -1.485 | -4.775 | 0.30 x 0.55 |

Rules for the board layout that draws these lands:
- The lands are bare copper with the finish of the board (ENIG or HASL are both accepted by a hot bar), solder mask opening 0.40 x 0.65 (0.05 per side). Pre-tin each land with a thin solder layer (stencil paste 0.05 mm or a tinned land), see section 7. (2026-11-13: done by paste, see the footprint line below.)
- Net names as in the tables. Land 6 and land 8 of J_BAND_A are both GND; land 2 and land 7 of J_BAND_B are both GND. On the board each GND land connects to the GND plane.
- Keep out of the area X -3.50 to -1.00, Y 3.40 to 5.60 (and the mirror, Y -5.60 to -3.40) for every other part and every through hole, so that the tail can lie flat there.
- The footprint "J_BAND_A_BOARD" and "J_BAND_B_BOARD" in design/ecad/band/OpenRingBand.pretty carry exactly these pads, origin at the middle of the pad group (X -2.250, Y -4.325 and +4.325). Since 2026-11-13 each land also has one F.Paste opening 0.30 x 0.44, centred, drawn as a filled rectangle in the footprint (not a pad, so the pad count stays 8 and 7), for the parts face stencil 0.075 mm (design/mfg/assembly/hotbar-joint.md section 1; process.md P2).

Soldering method: HOT BAR (thermode), not an iron. Why: the tail's lands face the board and the tail itself covers them, so an iron tip cannot reach the joint; the heat has to pass through the tail's 0.11 mm film and the 0.10 mm stiffener. The lands are 0.30 wide at pitch 0.51: a hand iron would bridge them. The tail's far-row and near-row lands are on one rigid, flat polyimide-stiffened foot, which is what a hot bar presses. Settings are in section 7.


### Mating of the tail foot on the board lands (checked by check_band.py at every size)

The tail foot lies under the board with its OUTER face (F.Cu, the face with the lands) touching the board's lands. The tail board files are drawn looking at that face (x = u along the tail from the end under the board, y = +-v). Laid on the board the tail position (u, v) maps to the ring model position X = v - 2.5, Y = side x (3.4 + u), side = +1 for FLEX2 and -1 for FLEX1 (u grows toward the slot). Checked by working out the view from +Z: the transform has no mirror, so the pattern is NOT mirrored; the board footprint and the tail footprint use the same land numbers in the same places. check_band.py reads the pads of the delivered footprint J_BAND_x_BOARD (placed at X -2.250, Y side x 4.325) and the pads of the tail board, and requires each of the 8 and 7 lands to be within 0.05 mm and on the same net.

| Tail | Land | Net | Board X | Board Y | Tail u | Tail v | Face touching the board |
|---|---|---|---|---|---|---|---|
| FLEX1 / J_BAND_A | 1 UP | JOY_UP | -1.485 | -3.875 | 0.475 | 1.015 | F.Cu (outer) |
| FLEX1 / J_BAND_A | 2 DOWN | JOY_DOWN | -3.015 | -3.875 | 0.475 | -0.515 | F.Cu (outer) |
| FLEX1 / J_BAND_A | 3 LEFT | JOY_LEFT | -2.505 | -3.875 | 0.475 | -0.005 | F.Cu (outer) |
| FLEX1 / J_BAND_A | 4 RIGHT | JOY_RIGHT | -1.485 | -4.775 | 1.375 | 1.015 | F.Cu (outer) |
| FLEX1 / J_BAND_A | 5 CENTRE | BTN_REC | -3.015 | -4.775 | 1.375 | -0.515 | F.Cu (outer) |
| FLEX1 / J_BAND_A | 6 MOT- | GND | -1.995 | -3.875 | 0.475 | 0.505 | F.Cu (outer) |
| FLEX1 / J_BAND_A | 7 MOT+ | VMOT | -2.505 | -4.775 | 1.375 | -0.005 | F.Cu (outer) |
| FLEX1 / J_BAND_A | 8 GND | GND | -1.995 | -4.775 | 1.375 | 0.505 | F.Cu (outer) |
| FLEX2 / J_BAND_B | 1 CELL+ | VBAT | -3.015 | +3.875 | 0.475 | -0.515 | F.Cu (outer) |
| FLEX2 / J_BAND_B | 2 CELL- | GND | -1.995 | +3.875 | 0.475 | 0.505 | F.Cu (outer) |
| FLEX2 / J_BAND_B | 3 NTC | NTC | -2.505 | +3.875 | 0.475 | -0.005 | F.Cu (outer) |
| FLEX2 / J_BAND_B | 4 VBUS | VBUS | -1.995 | +4.775 | 1.375 | 0.505 | F.Cu (outer) |
| FLEX2 / J_BAND_B | 5 D- | USB_DN | -2.505 | +4.775 | 1.375 | -0.005 | F.Cu (outer) |
| FLEX2 / J_BAND_B | 6 D+ | USB_DP | -3.015 | +4.775 | 1.375 | -0.515 | F.Cu (outer) |
| FLEX2 / J_BAND_B | 7 GND | GND | -1.485 | +3.875 | 0.475 | 1.015 | F.Cu (outer) |

Result: all 14 boards, worst offset 0.0000 mm (evidence/final/check_all3.log, 14 lines `mating: ... worst offset 0.0000 mm [limit 0.05]`). Broken copy with lands 1 and 4 of the FLEX1 foot swapped: exit 1, lines `FAIL mating: land 1 JOY_UP ... off by 0.900` and land 4 (evidence/final/check_mate.log).

## 3. The tail end that mates with the lands, and the fold between the board and the slot

(See band-notes.md for the per size lengths; they are computed by build_band.py and printed in a table.)

Tail-end pattern (footprints "J_BAND_A_TAIL", "J_BAND_B_TAIL"): same land centres as section 2 seen on the tail; tail land 0.30 (along the tail) x 0.30 (across), bare ENIG, coverlay opening 0.40 x 0.40 (0.05 more per side than the land, so the land is NSMD). Tail frame: u = distance along the tail from the tail end that goes under the board (u = |Y| - 3.4 on the foot), v = X + 2.5. Foot outline: u 0 to 1.745, v -1.0 to +1.5 (X -3.5 to -1.0). Far row lands at u 0.475 (centre), near row at u 1.375, via row at u 0.925 (between the rows). The drawings fab/flexK-usN-drawing.pdf show this pattern 4 times larger with the number and net of every land (added 2026-11-13, process.md change C13).

The fold (the tail rises through the slot and turns toward the board middle):
- The tail stands vertical at |Y| 5.9 in the slot (thin.py line 66 `tail_y=5.9`). Above the floor it turns 90 degrees toward the board middle and lies flat under the board, outer face (F.Cu, the lands) up.
- Inner radius of the fold 0.70 mm, centre line radius Rc = 0.70 + 0.055 = 0.755 mm. Minimum allowed 0.66 mm (section 1): margin 0.04 mm.
- Where it stands: the board's land face is at Z 1.43 (placement: board underside 1.45, land 0.02; thin.py lines 52 and 273). Joint 0.03 after the hot bar, tail top face at Z 1.40, centre line Z 1.345. The fold starts on the vertical piece at Z = 1.345 - 0.755 = 0.590, which is above the floor top (Z 0.40, band-flex-tails.md line 46): 0.19 mm clear. The flat run ends at |Y| = 5.9 - 0.755 = 5.145 and starts at |Y| 3.4: flat length 1.745 mm.
- Along the tail the fold uses 0.755 x pi/2 = 1.186 mm; the width goes from 2.5 (foot) down to 1.8 (neck) across the fold (taper), so the neck that passes the slot is 1.8 wide (slot 2.0 wide: 0.1 mm clear each side).
- Length added to the model's path by the foot and the fold: 2.071 mm (calculation in band_geom.py: LF + LARC - (Z_BD0 - Z_ARC0)); the model's path itself is unchanged.

## 4. Switches SW1 to SW5 (FLEX1 head)

Footprint "Alps_SKTAAAE010_pads34" (SW1, SW3, SW4, SW5) and "Alps_SKTAAAE010_4pad" (SW2). Source: Alps Alpine SKTA catalog, design/datasheets/w4_alps_skta_catalog.pdf page 2, Drawing No.1 (saved from the maker's own product page). Numbers used: land dimensions outer span 3.2, inner span 2.1, overall 1.3, gap 0.2 (four lands 0.55 x 0.55 at +-1.325 / +-0.375 from the centre). Terminal numbers as Alps gives them, seen from above in the "Dimensions" view: 1 top left, 2 top right, 3 bottom left, 4 bottom right. Circuit diagram on the same page: 1 and 3 are one side of the contact, 2 and 4 the other. The ring netlist matches it: P1 side = pins 1 and 3 (signal), P2 side = pins 2 and 4 (GND) (netlist.csv rows SW1 to SW5, changed to pins 1 to 4 at 2026-11-13 00:20).
- SW1, SW3, SW4, SW5 use only the two lands of one side (terminals 3 = signal, 4 = GND on the footprint). Terminals 1 and 2 are not soldered: Alps' circuit diagram joins 1 to 3 and 2 to 4 inside the part, so nothing is lost. Why: the head is 6.4 wide (thin.py line 67, stiffener 6.4 x 6.4) and the outer switch lands would lie 0.15 mm from the cut edge; the copper to edge rule is 0.30. The check script counts only the soldered terminals (check_band.py `present`).
- SW2 (centre) has all four lands: terminals 1 and 3 on the BTN_REC line, 2 and 4 on GND.
- Positions in the head frame (x along the finger, t around the band; head centre is the cap axis): SW2 (0, 0), SW1 (0, +2.4), SW3 (0, -2.4), SW4 (-2.4, 0), SW5 (+2.4, 0) (thin.py lines 686 to 688, `joy_sw_off` 2.4). Placed so that P1 and P2 land on the routing plan; the rotation of each footprint is printed by build_band.py in evidence/build_rows.json (saved listing evidence/sw_rot.log, US 9: SW1 90, SW2 90, SW3 -90, SW4 180, SW5 0 degrees; same at every size because the head is the same).
- Solder: reflow, paste 0.08 thick (Alps spec slim_alps-skta-aaae010-orwin.pdf page 4, item 10.2 (4)), peak 260 C 3 s max, at most 2 reflows. No through hole under a switch (same page 10.2 (5)): the head vias sit in the lands, under the switch. Alps' item 10.2 (5) and D2 (page 7) warn about flux rising through holes when the back of a board is dip-soldered; here nothing is dip-soldered and the back of the head is closed by the polyimide stiffener (0.10, bonded on the back face), so no flux path exists. Held by: reflow only, stiffener on the back. Paste openings (added 2026-11-13, design/mfg/assembly/process.md change C1): 1:1, 0.55 x 0.55, on each of the 12 soldered lands (SW1, SW3, SW4, SW5: lands 3 and 4; SW2: lands 1 to 4), layer F.Paste of the two switch footprints; Gerber fab/flex1-usN/flex1-usN-F_Paste.gbr; the 8 unsoldered terminals have no land and no opening.

## 5. Cell, protection circuit PRT1 and RT1 (FLEX2)

What PRT1 joins (closes connections.md R10, N4, N5; deferred item 162). PRT1 is the cell's own protection circuit board (1.5 along the band x 5 across, thin.py `prot`; it sits on the cell tab, 0.2 mm before the cell; cell.md). It has three output tabs and the cell's two tabs are inside it (cell maker's side). Seen from the ring, BT1 plus PRT1 is one part with three outputs. Interface fixed here:
- Tab P+ (PRT1 pad 1) = cell positive after protection = ring netlist BT1 pin 1, net VBAT, FLEX2 land 1 of J_BAND_B (CELL+).
- Tab P- (PRT1 pad 2) = cell negative after protection = ring netlist BT1 pin 2, net GND, FLEX2 land 2 (CELL-).
- Tab NTC (PRT1 pad 3) = RT1 pin 1, net NTC, FLEX2 land 3.
- RT1 pin 2 (ground) is on the PRT1 board and is joined there to tab P- (pad 2 of the same board). So RT1's ground land is FLEX2 land 2 (J_BAND_B pin 2, CELL-, net GND) through tab P-. This closes N3 / R8 / part of g. In the netlist RT1 pin 2 is net GND, which is what this is.
- Tab order along the band, from the slot toward the cell: P+, NTC, P- (lands in that order 1, 3, 2). Tab material: nickel strip 0.30 wide x 0.10 thick (my requirement to the cell/PRT1 supplier; the model's tabs are 1.0 wide, thin.py line 735, they may be wider than the land, and the 0.30 strip is fully inside the land footprint 0.26 x 0.45).
- FLEX2 lands (footprint PRT1_Tabs): 0.26 along the tail x 0.45 across, pitch 0.43, bare ENIG, coverlay opening 0.36 x 0.55. Position along the tail per size: first land centre at s = 0.586 (US 7), 0.604, 0.620, 0.836, 1.154, 1.466, 1.774 mm (US 13) after the slot junction, which is inside the PRT1 span (PRT1 spans s 0.270 to 1.624 at US 7 and 1.544 to 2.927 at US 13; evidence/build_rows.json `prt1_l1_s`, `pcm_s0`, `pcm_end_s`; PRT1 start angle per size from thin.py SIZE_TABLE). The lands sit on the tail's outer face (F.Cu, facing the cell). They are via-connected to B.Cu lines. The FLEX2 drawings name the three tab lands "P+ tab: VBAT", "NTC tab: NTC", "P- tab: GND" (added 2026-11-13).
- Soldering: the tabs are laid on the lands and soldered by hand, low heat: iron tip 280 C maximum, contact 2 s per joint, solder SAC305 0.3 wire or a pre-tinned land [my proposal; the cell's maker limit S12 is a bench value the build guide measures: touch each joint with the iron for at most 2 s and measure the cell voltage before and after; open item S12 in architecture 17.9].
- Cell side tabs (cell to PRT1): inside the cell part (custom, Grepow). The cell's two tabs are at the +Y end (cell.md). Not on the flex.

## 6. Motor leads (FLEX1)

Footprint "W0525AB001D_Lands": two lands 0.30 along the tail x 0.80 across, pitch 1.0. Source for the leads: design/datasheets/slim2_jinlong-w0525ab001d.pdf page 9 (drawing: lead wire AWG32, Red (+) and Black or Blue (-), length 30 +-1.5, detail A: 0.5 and 1.0 mm dimensions at the lead ends) and page 14 item 9-2 (red to +, blue to -).
- Land 1 (pad 1) = red lead = M1 pin 1 = net VMOT = J_BAND_A land 7 (MOT+). Land 2 (pad 2) = blue lead = M1 pin 2 = net GND = J_BAND_A land 6 (MOT-) (netlist.csv rows M1, J_BAND_A 6 and 7; closes N7/R5 order; deferred item 46). Order along the tail from the slot: red first, then blue. The FLEX1 drawings mark the lands "1 +: VMOT (red)" and "2 -: GND (blue)" (added 2026-11-13).
- Position: the first land centre at u = 7.15 (US 9; the model's pigtail position is 7.53, moved 0.38 toward the slot because the lanes need room before the head; per size slide in band_calc.log, 0.00 to 0.42 mm); v = 0.07 (X -2.43). The motor stands on the +X side of the tail, so leads arrive from +v.
- Lead cut length (closes deferred item 39 / S10): the maker delivers 30 mm. Cut each lead to the length in the table (measured from the motor body edge to the lead end), strip 0.6 mm, tin it, lay the stripped end along the 0.80 side of the land and solder by hand (iron 320 C, 2 s). Model v8 puts the motor 0.8 mm off the centre line at US 7 and US 12 (0.7 elsewhere): the motor land position along the tail does not change (it follows the motor's arc position, not its offset), only the across distance from the rim to the stripped end grows from 0.7 to 0.8, so the cut length grows at those two sizes (US 7 from 1.05 to 1.12, US 12 from 1.39 to 1.44; evidence/final/band_calc2.log). Table is band_calc.log (my calculation: exit points on the rim assumed at 1.0 pitch around the motor's tail-side point, distance to the land plus 0.7 mm across).

| US | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|
| lead cut length, mm | 1.12 | 1.07 | 1.08 | 1.14 | 1.39 | 1.44 | 1.39 |

A lead this short has no slack; it is the lead's length in the finished ring and the lead may be cut to 1.5 mm more to leave a loop of 0.4 mm, since the motor pocket has room beside the ribbon [the pocket is 5.2 wide, the model has the pigtail 1.0 long, thin.py line 714].
- Current: motor start 175 mA (motor-drive.md; Jinlong W0525 pages 5 and 6), the cell gives 227.5 mA at 3.30 V at a start with every other load on (motor-drive.md section 2.5). Lines VMOT and GND to the motor are 0.20 wide (12 um copper): 0.00717 ohm per mm (rho 1.72e-5 ohm mm / (0.20 x 0.012)). Longest size, US 13: VMOT 6.90 mm, drop 8.7 mV at 175 mA; GND 10.30 mm, drop 12.9 mV. Total at a start 21.6 mV, against the motor's 2.7 to 3.3 V window and U11's 3.0 V +-1.2 percent (motor-drive.md): the motor still gets 2.96 V minus 0.022 V = 2.94 V at worst. Current capacity: IPC-2221 external layer, 0.20 x 0.012 mm, 10 K rise: 0.343 A, which is 1.96 times the start current (band_calc.log). The land to land strap and vias carry the same current: one via 0.30/0.10 in the GND path (resistance below 1 milliohm: copper 12 um plating assumed in a hole 0.10 x 0.12 long).
- Cell lines VBAT and GND on FLEX2, 0.20 wide, 227.5 mA: longest (US 13) 6.74 mm VBAT, drop 11.0 mV, GND 7.64 mm, 12.5 mV (band_calc.log).

## 7. How the lands are soldered, in order (hot bar)

Board lands pre-tinned (SAC305 stencil 0.05 mm). Tail foot placed on the lands (alignment by the 0.10 mm outline shown on the fixture, outline +-0.10 tolerance of the laser cut, JLCPCB flexible PCB capabilities page "FPC Outline"), coverlay openings 0.05 larger than the lands. Hot bar blade 3 mm wide (the foot is 2.5 wide, X -3.5 to -1.0, and 1.745 long) covering the whole foot, 260 C for 4 s at 20 N [my starting values: the Alps and the polyimide's limits are 260 C 3 s; the polyimide film is rated far above it]; the PI stiffener 0.10 on the back of the foot carries the pressure. Check after: continuity of each land to the next stage lands by the test pads (build guide), no bridge between the 0.21 mm gaps (land pitch 0.51 minus land 0.30). (2026-11-13: the board lands now get paste through the 0.075 mm parts face stencil, openings 0.30 x 0.44 in J_BAND_A_BOARD and J_BAND_B_BOARD, section 2.)

## 8. Charging pads (FLEX2)

Closes N6, R9, deferred item 118. The copper land is a 1.6 mm disc on the inner face (B.Cu), ENIG (1 to 2 micro-inch gold, the only finish on the capability page). ENIG gold is a few hundredths of a micrometre thick and the case's spring pins touch it at every charge, so it would wear through. Decision: the pad that the case touches is a gold-plated disc, 1.6 dia x 0.07 thick (the model's pad, thin.py line 56 `cpad_t`), soldered flat on the land with SAC305 paste at assembly step 8 and set in the liner at step 21. The land is the joint, the disc is the wear surface. Position: disc centres on the flat tail at u = 26.01, 28.45, 30.89, 33.33 (US 9; per size in build_rows.json `pad_u`), pitch 2.438 on the flat (neutral axis, ribbon mid radius 9.62 against the pad face radius 9.475: 2.4 x 9.625/9.475 on the inner face), v = +1.5 (X -1.0), order VBUS, D-, D+, GND with rising angle (band-flex-tails.md critical dimensions; thin.py lines 603, 604). Each disc land has one via 0.30/0.10 at its centre to the F.Cu line. Pad lands are via-in-pad, filled by the disc. Paste (added 2026-11-13, process.md change C2): four round openings 0.58 mm per disc land, centred 0.49 mm from the land centre on the diagonals, 0.05 mm clear of the via at the centre (filled circles drawn on layer B.Paste by build_band.py, not pads, so the land keeps one pad); Gerber fab/flex2-usN/flex2-usN-B_Paste.gbr.

## 9. Differences from the model, and what they need (also in band-notes.md)

1. The tail is 1.8 wide at the neck, not 1.4 (thin.py line 66 `tail_w=1.4`, `tail_x=-2.6`, slot 2.0 wide). Reason: the FLEX1 neck carries 5 lines on B.Cu (0.08 lines at 0.10 gaps, one 0.20 ground) and 2 on F.Cu; the usable width is the width minus 2 x 0.30 edge rule; 1.4 gives 0.8 which holds 4 lines of 0.08 with 0.10 gaps, not 5 plus a 0.2 ground. 1.8 gives 1.2.
2. The pad strip of FLEX2 spans X -3.4 to +0.25 (3.65 wide); the model's strip is X -2.25 to 0.25 (2.5 wide, thin.py line 606) with the jog piece X -3.3 to 0.25 before it (STEP file solid 2, evidence/step_solids.csv). Mine is the envelope of both, so the neck lines run straight to the pads.
3. The stiffener under the head is 0.10 (offered value), the model 0.075 (thin.py line 64 `stiff_t`).
4. Finished thickness 0.11 in the flat parts, 0.21 under the foot and head (0.11 + 0.10 stiffener); the model has 0.15 everywhere.
