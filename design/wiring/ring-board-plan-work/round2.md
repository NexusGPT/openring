
---

# Round 2: the plan against the real footprints

Written 2026-11-13 from 00:45 to 01:15 (Mac clock). Inputs: the lead's decisions (`design/wiring/lead-decisions.md`, rows "7, 11 (part), W2", "4, W2", "2, 3, 6, 8, W2", "radio corner", "25", "127, 128"); the libraries `design/ecad/ring/pcb/OpenRing.pretty/` (21 footprints) and `design/ecad/band/OpenRingBand.pretty/` (10 footprints), loaded with KiCad's Python (`design/ecad/ring/pcb/run_kipy.sh`); `design/ecad/ring/parts.csv` as on disk at 00:49 (it already holds C89 and LT1, C88 in 0402, C60 2.2 uF 0402); the lead's two messages of round 2 (C35, C36 are 0402 1.0 nF C0G; L71, L72 are 1269AS-H 2.5 x 2.0; C71, C85, C86, C87, C60 0402; C88 0603). Scripts and logs: `design/wiring/ring-board-plan-work/` (`rules.py`, `geom.py`, `make_placement2.py`, `check_placement.py`, `area3.py`, `j1check.py`, `probe_rot.py`, their `.log` files, `placement-final.png`).

The lead's decision replaces step g.8's gate: there is no automatic switch to 6 layers. If routing on 4 layers leaves a connection open, the builder stops and reports the count and the nets; the lead takes it to the owner.

## R2.0 First: the antenna mount and its keep-out change (point 6)

1. **The antenna moves 0.75 mm toward +X: ANT1 at (-10.75, 5.25), rotation 180 (was (-11.50, 5.25)).** Reason, measured on the library footprint: at (-11.50, 5.25) the far-end edge land spans X -13.50 to -12.50, Y 5.60 to 6.20. The board's corner has radius 0.8 (PLACE row PCB1), centre (-12.80, 5.50). The land corner (-13.50, 6.20) is 0.99 mm from that centre; it must be 0.70 or less to keep 0.10 mm of board round the copper. At (-10.75, 5.25) the land corner is (-12.75, 6.20): 0.70 mm. Pins (library footprint, rotation 180, checked by `probe_rot.py`): pin 1 FEED at (-9.25, 5.90), pin 4 GND at (-9.25, 4.60) with its ground stack at (-8.45, 4.20), pins 2 and 3 at X -12.25 to LT1.
2. **Keep-out: X -13.60 to -8.70, Y 2.90 to 6.30** (the lead's Y 2.90 stays; my round-1 value 3.10 in e.3 and f.4 is withdrawn), **less a notch X -9.20 to -8.70, Y 2.90 to 3.30** where the storage chip U3's body corner stands. U3 has no copper there: its nearest pads (pins 1 to 4, column X -8.50, pad 0.8 x 0.7) end at Y 2.255, and pad 9 at (-5.00, 2.60).
3. Antenna pi network and feed, moved with it: C13 (-8.25, 4.98, rot 90), L4 (-7.70, 5.90, rot 0), C89 (-7.10, 4.98, rot 90); the RF line's rise is at X -6.65 (was -7.40): route (0.00, -0.39) to (0.00, 3.30) to (-6.45, 3.30) to (-6.65, 3.50) to (-6.65, 5.70) to (-6.85, 5.90) to L4, then L4 to pin 1 at (-9.25, 5.90). The chip match moved by 0.05 to 0.07 mm to clear U1's real courtyard: L2 (1.70, -0.39), L3 (0.48, -0.39), C3 (1.10, -1.31, rot 90), C12 (-0.12, -1.31, rot 90). Length of the line, sum of the legs between parts: 0.71 + 0.65 + 0.20 + 3.69 + 6.45 + 0.28 + 2.20 + 0.28 + 0.57 + 1.27 = 16.3 mm.
4. LT1 at (-12.40, 3.25), rotation 0, inside the keep-out (allowed). Its ground is J1's +Y mounting pad (X -13.25 to -12.30, Y 2.45 to 2.85), tied to GND with a stacked via in that pad (h.1: J1's mounting pads go on GND).
5. What the body needs, replacing e.6: radio corner (resin) X -14.80 to **-8.55**, Y 2.05 to the skin (was -9.30; the antenna body now ends at X -9.15, plus the same 0.60); floor pocket **X -12.55 to -8.95**, Y 4.25 to 6.25, 0.20 deep (was X -13.30 to -9.70). The corner grows to about 6.25 x 5.3 mm.

## R2.1 J1, the screen connector (point 1)

Facts:
- Catalogue page 3 (`w1_hirose_fh35c_series_catalog.pdf`) and drawing EDC3-338903-01 page 1 (`w1_hirose_fh35c-15s-0.3shw50_drawing.pdf`): A = 6.1 along the contact row (15 contacts), land rows 3.6 apart outer edge to outer edge (B, catalogue page 4), housing depth (3.35) in the top view; the (4.2) is in the side detail, where the flip lever stands open at 90 degrees. Read from the pictures, catalogue page 3 and drawing page 1: the FPC enters on the side of contact No. 1 (the 0.8 mm lands), the lever (back flip) is on the side of contact No. 2; the leads stand 0.05 +-0.15 out on the FPC side and 0.15 +-0.15 on the lever side, so the closed housing sits about centred on the lands.
- The library footprint has its odd row (contact No. 1, 0.8 mm lands) at local y +1.4 and its mounting pads `MP` at local (+-2.8, 1.125). At rotation 270 local +y points to -X: the FPC opening faces the hand end, where the screen tail comes in (PLACE row DISP1 tail: X -13.775, down the hand end, under the board end to J1). Pin 1 is then at the +Y end (-13.05, 1.95 at the final place), pins 13 to 15 (ground) at the -Y end.

At PLACE's (-12.0, 0.0), rotation 270 (`j1check.py`): lands X -13.80 to -10.20, Y -3.00 to 3.00. **It does not fit:** the lands pass the board end (X -13.60) by 0.20 mm, and the +Y mounting pad (Y 2.60 to 3.00) reaches 0.10 mm into the antenna keep-out (from Y 2.90). The library courtyard (X -13.87 to -10.13, Y -3.12 to 3.12, as read at 01:05) passes the board end and enters the keep-out and microphone U5's courtyard.

**Final: J1 at (-11.65, -0.15), rotation 270.** Lands X -13.45 to -9.85, Y -3.15 to 2.85; mounting pads X -13.25 to -12.30 at Y -3.15 to -2.75 and 2.45 to 2.85; closed housing about X -13.33 to -9.98, Y -3.20 to 2.90. It touches U5's courtyard (U5 body edge Y -3.30, courtyard 0.10 round the body) and the keep-out edge, and stays 0.81 mm from U3's courtyard (X -9.17). What moves: J1 by (+0.35, -0.15); J1's courtyard becomes the closed housing 6.10 x 3.35 (the library's courtyard still reaches 0.07 mm into the keep-out at this place); U5's and U6's courtyards become the body plus 0.10 (library: plus 0.145). The keep-out and the antenna do not move for J1.

## R2.2 The microphones and C35, C36 (point 2, with the lead's 0402 ruling)

- U5 at (-10.8, -4.8) rotation 90, U6 at (10.8, -4.8) rotation 270: the Knowles land view (datasheet page 6) puts the port 1.030 from the short end of pad 7 (read from the picture); PLACE puts the ports at X -11.77 and +11.77, toward each block end. With these rotations pin 4 (Vdd) is at (-10.125, -5.225) for U5 and (10.125, -4.375) for U6 (`probe_rot.py`, `j1check.py`).
- **C35 (0402) at (-8.25, -5.35), rotation 90**: its courtyard (X -8.65 to -7.85) is 0.05 from U5's (X -8.70); centre 1.88 mm from U5 pin 4. **C36 (0402) at (8.25, -3.40), rotation 90**: courtyard X 7.85 to 8.65, 0.05 from U6's, 0.18 from L10's; centre 2.12 mm from U6 pin 4. No place is closer: U5 has the board end (-X), the board edge (-Y) and J1 and U3 (+Y) on its other sides; U6 has the board edge, U2 and L10. Pin 4 is an inner land: it leaves by a microvia L1-L2 in the land and runs on L2 to a microvia in the capacitor's pad.
- C31 at (-9.50, -0.70), C32 at (6.20, -5.80): both more than 2.0 mm from the microphone bodies (enforced in `rules.py`, AVOID).

## R2.3 Zones against the real footprints (point 3)

| Part | Footprint fact | Effect on the plan |
|---|---|---|
| U3 | 9 pads: pins 1 to 4 in a column at X -8.50, pins 5 to 8 at X -1.50 (Y +-0.635, +-1.905, pads 0.8 x 0.7), pad 9 (-5.00, 2.60), courtyard X -9.17 to -0.83, Y -3.27 to 3.27 | RF line along Y 3.30 passes pad 9 (edge Y 3.00) at 0.24 mm: passes the RF check. The J_BAND courtyards of the band library (3.21 x 2.91) overlap U3's by 0.40: replaced by the keep-out rectangles (h.1). U3 and U5 courtyards overlap 0.07 mm; their bodies are 0.20 apart as the mechanical model fixed them (mic-path.md C13): counted as a declared exception |
| U4 | 2.0 x 2.0, pitch 0.5, courtyard 2.35 x 2.35 | moved from Y -3.50 to **-3.90** (with L10) so that the strip between U1 and U4 is 1.345 mm and holds U1's supply parts (C4, C6, FB1, C7); its fly capacitor C23 and input C22 are fixed beside it at (2.37, -3.40) and (2.37, -5.10); L1 moves to (1.00, -4.32) |
| L10, L71, L72 | 1269AS-H, courtyard 3.14 x 2.34 | L10 rotated 90 at (6.50, -3.90): at rotation 0 its courtyard overlapped U4's by 0.20. L72 at (8.87, 3.75), L71 at (12.02, 3.75), rotation 0 (long side along X): their courtyards touch (X 7.30 to 10.44 and 10.45 to 13.59). SW2 runs south along X 8.0 to L72's west pad (7.87, 3.75); SW1 runs east along Y 1.55 to X 10.95 then south to L71's west pad (11.02, 3.75); C74 (PVDD) at (9.05, 2.14) between U2 and L72. These replace the coil places of f.1 |
| U10 | UQFN-16 1.8 x 2.6, courtyard 2.54 x 3.34 | no room in Z15 once U1's supply parts and the RF corridor took theirs: **U10 at (-5.25, -4.60), rotation 90**, north of U3 between U5 and the tail A keep-out, C81 and C82 beside it; the card lines reach U3's two pad columns from there |
| U11 | X2SON 5 pads (thermal pad 5) | unchanged at (0.00, 4.20); C83 stays (0.00, 5.45); **C84 rotated 90 at (1.27, 5.00)** (at rotation 0 it overlapped C83); U9 at (3.12, 5.20) |
| X2 | 9HT11 courtyard 1.74 x 2.54 | rotation 90 at **(6.00, 3.35)** (was 3.00), so a 0402 fits between it and U1 |
| RF corridor X -0.83 to 2.32 | between U3's and U1's courtyards | holds the RF chain and the X 0.00 leg; every pad of another part is 0.20 mm or more from the line (check) |
| USB pair | | its west run moves to Y 5.95 and 6.125 (was 5.89, 6.065): 0.20 from C83's and C84's pads, 0.125 from the board edge |
| Test pads | 19 x TESTPAD_0.8 (courtyard 1.04 x 1.04, 20.6 mm2) | **all 19 go to the screen face (L4)**: flat copper with no height; with them on the parts face the first placement run found no place for C75 |

## R2.4 Area with the real libraries (point 4)

From `area3.log` (courtyard bounding boxes including the 0.05 line, as `footprint-notes.md` measures them):
- Board 342.2 mm2.
- Parts face: courtyards 275.6 mm2 (J1 as its housing, J_BAND as the keep-out rectangles, U5 and U6 body + 0.10); with every library courtyard unchanged, 281.2.
- Antenna keep-out on the board 16.46 mm2, of which 9.91 under ANT1 and LT1: 6.55 more that no part may use.
- **Sum 282.2 of 342.2 mm2 = 82.5 percent** (88.5 percent if the 20.6 mm2 of test pads stayed on the parts face). The routing reserves of the RF line, the USB pair and the switching tracks (about 18 mm2 of L1) come on top.

## R2.5 Placement table (point 5)

File: `design/wiring/ring-board-plan-work/placement-plan.csv` (columns reference, footprint, side, x_mm, y_mm, rotation_deg, zone, kicad_x, kicad_y; KiCad = model + (100, 100); side F = parts face L1, B = screen face L4; rotation in KiCad degrees). It is written by `make_placement2.py` run as `SEED=4 OUT=placement-plan.csv run_kipy.sh make_placement2.py`: parts with coordinates in `rules.py` (FIXED) go there; every other part goes to the free place nearest the pin it serves (ANCHOR), on a 0.05 mm grid within 3 mm and 0.1 mm beyond, rotation 0 then 90, avoiding courtyards, keep-outs and the routing reserves; SEED=4 is the one of 8 tried orders that placed all parts with the least total distance (1, 3 to 7 placed all; 2 and 8 left one part out: `seed*.log`).

Check: `check_placement.py placement-plan.csv` → `check_placement.log` ends `RESULT PASS` (104 parts, 85 on the parts face, 19 on the screen face; no courtyard overlap except the declared U5-U3 pair; every courtyard inside the outline, with ANT1, U5, U6 allowed 0.10 / 0.20 / 0.20 past it and their pads 0.10 inside; no part in a keep-out it is not allowed in; every pad of another part 0.20 mm or more from the RF line and the USB pair). Broken copy (C4 pushed onto U1, C79 pushed past the edge): `check_placement_broken.log` ends `RESULT FAIL 4`.

Parts placed more than 3 mm from the pin they serve (all decoupling or bias parts; distances from `place-final.log`): C26 8.2 and C27 8.2 (U4's AVDD and VON outputs), C21 6.1 (U4's VBAT input), C75 6.4 (VSYS), C25 5.3 (ELVDD at J1), C28 5.0 (ELVSS at J1), C11 3.5 (U1 VBUS), C24 3.3 (U4 VOUT), C78 3.1 and C80 3.9 (buck outputs), C73 3.8, C72 3.9 (VBUSOUT, VBUS), C32 3.9 and C31 5.8 (kept away from the microphones on purpose); resistors R57, R58, R60, R63, R64, R66, R61, R62, R1 (bias and series parts, position not critical). The board has no free place nearer: this is the cost of the real footprints. Each gets a measurement on the unit (h.2 below).

@@TABLE@@

## R2.6 Changes other files need (added to h.1)

| File | Value now | Value needed | Reason |
|---|---|---|---|
| `design/mech/thin/placement.csv` | ANT1 X -12.700, Y 4.400, 1.6 x 3.2; J1 (-12.000, 0.000) 3.2 x 5.2; U4 Y -3.500; L10 (6.500, -3.500) 2.5 x 2.0; L71 (8.500, 3.200), L72 (11.000, 3.200) 2.0 x 1.6; X2 (5.500, 3.000); U2 3.1 x 2.4; C84 (1.200, 5.000) | ANT1 (-10.750, 5.250) 3.2 x 1.6, Z 0.85; J1 (-11.650, -0.150) 3.35 x 6.1; U4 Y -3.900; L10 (6.500, -3.900) 2.0 x 2.5; L71 (12.020, 3.750), L72 (8.870, 3.750) 2.5 x 2.0; X2 (6.000, 3.350); U2 2.4 x 3.1; C84 (1.270, 5.000) | R2.0 to R2.3; the model's fit check reruns (W11) |
| same, outer_body and the radio corner (`thin.py`, `mfg/specs/body.md`) | corner X -14.80 to -9.30 (lead's row "radio corner"); pocket X -13.30 to -9.70 | corner X -14.80 to -8.55; pocket X -12.55 to -8.95, Y 4.25 to 6.25, 0.20 deep | R2.0 |
| `design/wiring/lead-decisions.md` row "2, 3, 6, 8, W2" and `design/architecture.md` line 156 | keep-out X -13.60 to -9.45, Y 2.90 to 6.30 | X -13.60 to -8.70, Y 2.90 to 6.30, less X -9.20 to -8.70, Y 2.90 to 3.30 | R2.0 |
| `design/ecad/ring/pcb/OpenRing.pretty/FPC_Hirose_FH35C-15S-0.3SHW.kicad_mod` | courtyard 3.74 x 6.24 (as read at 01:05) | the closed housing, 6.10 along the row x 3.35, centred on the lands | R2.1 |
| `OpenRing.pretty/LGA-8_Knowles_SPK0641HT4H-1_3.0x4.0.kicad_mod` | courtyard body + 0.145 | body + 0.10 | R2.1 (J1 and U5 bodies are 0.10 apart) |
| `design/ecad/band/OpenRingBand.pretty/J_BAND_A_BOARD.kicad_mod`, `J_BAND_B_BOARD.kicad_mod` | courtyard 3.21 x 2.91, overlapping U3's by 0.40 | the keep-out rectangle of band-interface.md section 2 (2.50 x 2.20) | R2.3 |
| `J_BAND_A_BOARD.kicad_mod` against `design/ecad/band/band-interface.md` section 2 | footprint pad 1 at (-1.485, -3.875), pad 4 at (-1.485, -4.775), pad 6 at (-1.995, -3.875), pad 8 at (-1.995, -4.775) (placed at (-2.25, -4.325), rotation 0, `probe_rot.py`) | the table: land 1 UP (-1.995, -3.875), land 4 RIGHT (-1.485, -3.875), land 6 MOT- (-1.995, -4.775), land 8 GND (-1.485, -4.775). One of the two files is wrong: the band helper settles which (lands 2, 3, 5, 7 agree; J_BAND_B agrees in all 7) | conflict found while placing; my exits of f.3 follow the table |
| `design/ecad/ring/make_netlist.py`, `netlist.csv` | J1 mounting pads MP without a net | MP on GND | R2.0 item 4 (LT1's ground) |
| `design/ecad/ring/pcb/build_board.py` | own placement | load `placement-plan.csv` (side B = flipped to the screen face for the 19 test pads) | R2.5 |

## R2.7 Added to h.2 (cannot be settled on paper)

| Item | Start value | Measurement on the unit |
|---|---|---|
| Screen supply with its capacitors 3 to 8 mm away (C21, C24, C26, C27, C25, C28) | positions of R2.5 | ripple on SGM_AVDD, SGM_VON, ELVDD, ELVSS at full white screen, and the screen's start-up, on 3 units |
| Buck outputs and VSYS with C78, C80, C75 3 to 6 mm away | positions of R2.5 | ripple on VDD_1V8, VDD_3V0, VSYS at 200 mA load |
| VDD_MIC at the microphones (C35, C36 1.0 nF C0G, 1.9 and 2.1 mm from pin 4) | lead's decision row 25 | noise floor of a silent recording (the lead's decision already names it) |
| Test pads on the screen face | 19 pads on L4 | probe contact with the pogo fixture before the board goes into the body |

RESULT: done, every one of the 104 board parts fits on the 4-layer board's parts face with the real footprints (check PASS, 82.5 percent of the area) once the 19 test pads move to the screen face, J1 moves to (-11.65, -0.15), the antenna and its keep-out move 0.75 mm toward the fingertip (keep-out now X -13.60 to -8.70), U4, L10, X2, L71, L72, C84 move, and 14 capacitors sit 3 to 8 mm from their pins.
