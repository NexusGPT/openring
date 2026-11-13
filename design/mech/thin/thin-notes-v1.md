# Thin ring, inside model (architecture.md section 17, A5-draft)

Axes: X along the finger (+X fingertip), Y across (+Y thumb), Z up; origin at the centre of the block's underside. Band axis along X at Y 0, Z -9.875 (bore 18.95 mm, top of the bore 0.4 under the underside). Angles from the top, plus toward +Y. Units mm.

Run: `cd design/mech/thin && ../../.venv/bin/python thin.py` writes placement.csv, layers.json, out/thin-inside.glb, out/thin-inside.step. `../../.venv/bin/python check_thin.py` checks. `../../.venv/bin/python render.py` writes out/thin-assembled.png and out/thin-exploded.png.

Files: thin.py (model), check_thin.py (check), render.py (pictures), placement.csv (37 rows), layers.json (5 layers, explode directions), out/ (logs and outputs; out/evidence.py, out/notch_probe.py, out/glb_check.py are the scripts behind the numbers below).

## Result of the check (out/check_r4.log, second pass)
37 parts, 665 pairs (shell x liner excluded), no overlap above 0.001 mm3, every part inside the outer body's envelope, motor out of the block interior (0.0000 mm3), least metal at the motor rim 0.400 mm (limit 0.40), block stack 0.40 + 0.05 + 1.00 + 0.30 + 0.10 + 0.80 + 0.10 + 0.40 = 3.15 mm (limit 3.20). Last line: `RESULT PASS pairs=665 parts=37`.
Note on the first pass: the envelope object was being changed in place by the cavity cuts (found in the second pass; fixed with a deep copy), so the first pass's "inside the outer body" test was weaker than stated; the second pass has it right.

## Broken copy (second pass, once)
out/broken_copy/: copy of thin.py and check_thin.py with the motor moved 3 mm along the arc toward the cell (-49.00 to -64.88 deg; the pocket stays). out/broken_copy/check.log: collisions outer_body x vibration_motor 10.2553 mm3, vibration_motor x cell 5.8094 mm3, vibration_motor x cell_protection 11.2497 mm3, wall 0.000 at the rim, last line `RESULT FAIL pairs=665 parts=37`, exit 1.

## Motor wall test (lead ruling, second pass)
check_thin.py samples 24 points on each rim circle of the motor (back and front face), walks the outward radial ray from each and adds up the metal (body solid) it crosses; under 0.40 mm is a finding. It also fails if the motor enters the block interior (box X +-13.725, Y +-6.45, Z 0.40 to 2.75).
- Old 3.1 mm shoulder (THIN_OVERRIDE="shoulder_t=3.1"): FAIL, 0.000 mm at the front rim, `RESULT FAIL pairs=665 parts=37` (out/check_old_shoulder_3.1.log).
- 3.6 mm shoulders exactly as ruled (19 to 57 deg, easing to 2.6 at 85; THIN_OVERRIDE="taper_start_deg=57") with the motor at 49: FAIL, 0.275 mm (out/check_ruled_taper57.log).
- Angle scan in the asked range with the ruled shoulder (out/angle_scan_a.log; 38 earlier: out/angle_scan_test.log): 40 deg wall 0.00, block overlap 4.02 mm3; 42: 0.00 / 2.50; 44: 0.32 / 1.34; 46: 0.40 / 0.52; 48: 0.32 / 0.039. No angle from 34 to 48 gives both at least 0.40 mm and no block overlap (small angles put the top rim into the block, large angles put the far rim on the easing zone). 49 deg clears the block (out/angle_scan2.log).
- Delivered: motor at 49 deg and the flat 3.6 mm zone kept to 61 deg instead of 57 (easing 61 to 85). Result: least metal 0.400 mm at the front rim, block overlap 0. This is TWO departures from the ruling (angle 49 is 1 deg outside 34 to 48; flat to 61 not 57). What passes at 49 deg: 3.6 mm kept flat to 61 deg (tested, 0.400). A flat zone to about 60 deg is my estimate by calculation only (untested); a thicker flat zone to 57 was not tested. The change is one line: P["motor_angle"], P["motor_pocket_angle"], P["taper_start_deg"] in thin.py.
- The pocket roof is 0.1 above the motor (builder's choice; the architecture's 0.2 gap would cost 0.1 mm of wall). The test does not measure side walls (X) of the pocket.

## Further changes in the second pass
C8. Cell protection circuit: 2.0 along the arc from the cell's -77 end collides with the motor's back rim at 49 deg (back rim reaches -68.7 deg). Shortened to 1.5 along the arc (-77.05 to -68.5 deg), size 5 x 1.5 x 1.6. Alternative: motor at 46.5 deg, which puts about 0.4 mm3 of its rim into the block.
C9. The thicker shoulder (outer radius 13.075) lifts the joystick cap's rim 0.18 mm into the board layer (0.0738 mm3 overlap at X +-1.12, Y 5.93 to 6.30). Board notch 2.8 x 0.6 at the +Y edge. The motor board notch of the first pass is removed (CH notch_motor False); the antenna notch stays.
Shoulders: 3.6 thick from 19 to 57 deg, 13 wide to 57 (shell 0.6 at the edges), then 8 wide easing in radius to 2.6 at 85 (the rounding 0.4 of the band edge in that zone is NOT modelled). The joystick cap is now 2.22 tall (r 10.855 to 13.075); the record cap follows the easing surface (r 12.9 at 62 deg).
References as sent by the lead: SW1 up, SW3 down, SW4 toward the hand, SW5 toward the fingertip, SW2 record switch, J_BAND_A (thumb tail), J_BAND_B (other tail).
The GLB is Z-up (CAD axes, mm), NOT glTF Y-up: the app must rotate the scene -90 deg about X to stand it up.

## GLB
out/thin-inside.glb: 37 nodes, one per placement.csv row, same names and order (out/glb_check.log). Coordinates are the CAD axes (Z up, mm), NOT glTF Y-up: the app rotates the scene -90 deg about X to stand it up. Each node has `extras` (reference, layer, metal, angle_deg, centre, explode_dir); scene `extras.layers` repeats layers.json. Flat shaded, one material per layer; glass and shell are semi-transparent.

## Conflicts in the architecture (reported, each with the number I used)
C1. Joystick switches: 17.3 says a cross at 1.9 mm from the centre with 2.6 x 1.6 switches. At 1.9 each fingertip/hand switch overlaps each up/down switch by 0.2 x 0.2 mm in plan (out/evidence.log, line C1: 4 collisions of 0.0212 mm3). They touch at 2.1. I used 2.1 (footprint 5.8 x 5.8, not 5.4 x 5.4). Needs the owner's or Alps' ruling.
C2. Antenna: section 2 gives 3.2 x 1.6 x 1.2; 17.2 gives only 1.00 under the board. 1.2 does not fit under it. I made a notch 1.8 x 3.6 in the board's hand-end +Y corner and stand the antenna in it (Z 0.45 to 1.65, below the foam). Without the notch: main_board x antenna 1.024 mm3 (out/evidence.log, C2). The notch costs about 6.5 mm2 of board (board area 57 percent in 16.7, limit 60).
C3 (first-pass text, superseded by the 3.6 mm ruling and the second-pass section below). Motor: 7.0 diameter x 2.1 is a flat disc; the band is curved. Its outer rim reaches polar radius 12.38, past the 12.075 the shoulder's shell inner face has at 3.1 mm thick. In 17.3, "inside 3.1" for the motor (0.3 + 2.1 + 0.2 + 0.5) holds only at the disc centre. Consequences in the model: (a) the pocket is a cylinder 7.2 dia whose roof is 0.075 above the motor; the shell wall left at the rim is 0.095 mm at the bottom rim and nothing at the top rim, which opens into the block (out/evidence.log, "motor pocket rim"); the wall at the pocket centre is 0.63 mm. (b) the top rim goes 0.19 mm into the board layer (Z up to 1.637, board underside 1.45), so the board has a notch 3.6 x 2.0 at the -Y edge. Without it: 0.0559 mm3 overlap (out/notch_probe.log, X -1.43 to 1.43, Y -4.79 to -4.41). A real fix is a thicker shoulder (about 3.6 mm) or a thinner or smaller motor; I did not change a number.
C4. Square screen panel in a plan radius of 2.5 mm: the panel corner (13.675, 6.4) sits 2.157 from the corner arc centre, so the shell wall at the four panel corners is 0.27 mm along the diagonal (not 0.5). Fix: round the panel corners (vendor drawing) or accept it.
C5. Joystick radial stack: liner 0.3 + flex 0.15 + switch 0.53 + plate 0.4 + shell 0.5 = 1.88, not the 3.1 written as "inside". The remaining 1.22 mm is the cap's height above the plate. The 0.4 mm plate is not a listed part; its zone (r 10.455 to 10.855) is left empty and the cap starts at the plate top. Same for the record button.
C6. Cell: 38 mm on the centre line at radius 10.575 (architecture writes 10.58) is 205.9 degrees, shown as 77.05 to 282.95 deg.
C7. Wiring: 17.3 gives 9 lines on the non-thumb flex (motor 2, cell 3, pads 4). Between the motor pocket and the wide shoulder cavity only 2.2 mm of width is free (X -5.8 to -3.6), so each tail is modelled 2.2 wide (two stacked layers needed for 9 lines at 0.3 mm pitch).
Also: the 8 mm band and the 13 mm shoulder width: the motor (7.0) does not fit the 6.8 mm channel, so the channel is 11.8 wide (13 less 2 x 0.6) over 30 to 54 degrees on each side.

## Chosen by the builder
- Band axis at X centre 0, all band parts at X 0 (joystick, record button, motor, cell, pads). The architecture gives no X for them.
- Joystick cross at 2.1 (C1). Switch orientation: the two fingertip/hand switches have the 2.6 side across the arc; the two others have it along X.
- Chip positions on the board (under side, X, Y): main chip U1 (4.0, 0), power chip U2 (8.5, 0), screen supply U4 (4.0, -3.5) with its coil L10 (6.5, -3.5), storage U3 (-5.0, 0) long side along X, power coils L71 (8.5, 3.2) and L72 (11.0, 3.2), crystals X1 (3.0, 3.0) and X2 (5.5, 3.0), connector J1 (-12.0, 0) with the 5.2 side across Y and the tail entering from the hand end, antenna (-12.7, 4.4) with its 3.2 side along Y. Reason: rules of 16.3 (connector at X -12, antenna at the hand end under the unlit strip, mics at X -11 and +11 on the -Y wall), nothing in the strips Y +-5.9, X -5.8 to -3.6 kept for the flex tails, supply parts grouped near their chip.
- Microphones: 3.5 along X, 2.65 along Y, flush against the -Y cavity wall (Y centre -5.125).
- Reference numbers taken from bom.csv: U1, U2, U3, U4, U5 and U6 (mics, listed there as 4 x), L10, L71 and L72 (the 2.2 uH buck inductors, 2.0 x 1.6 as in 16.7), X1, X2, J1, ANT1, DISP1, PCB1, GL1, ADH1, FOAM1, M1, BT1, CP1 to CP4 (VBUS, D-, D+, GND in the order of 17.3 along X). Per the lead's naming (section 17.3): joystick up SW1, down SW3, toward the hand SW4, toward the fingertip SW5, record switch SW2; the two flex tails carry the board pad groups J_BAND_A (thumb side) and J_BAND_B. The caps, protection circuit, liner and the body have no bom.csv row for this design (bom.csv still lists the older SW1/SW2 parts), so the reference is empty. The TDK chip power coil L1 (0603) is not in the list given for this model and is not drawn.
- Block cavity = panel + 0.05 per side (27.45 x 12.9), corner radius 0.1; glass recess with a 0.5 rim, concentric with the 2.5 radius; shell floor 0.40.
- Cover glass 28.3 x 13.75 x 0.4 (block minus the 0.5 rim); its top is at Z 3.15, 0.05 under the block top.
- Screen tail: 0.2 thick, 5.0 wide; down the hand end beside the panel (pocket X -14.05 to -13.5, wall left 0.6), then 0.275 mm under the board end, touching J1's face (the insertion is not drawn). Foam is a full pad at board size.
- (first pass; see second pass for the shoulder) wide cavity from 30 to 54; channel from +30 round the bottom to -30 degrees. The channel is closed toward the top by the block floor; flex slots 2.6 x 0.6 at Y +-5.9, X -4.7 through the floor.
- Floor slot, tail Z from -0.9 to 1.45 (touching the board underside). The run of the tail inside the band to the switches, the motor and the cell is not drawn.
- Cell protection circuit: curved plate 2 (arc) x 5 (X) x 1.6 (cell envelope), starting at the cell's -77 end and running 2 mm toward the top (-77.05 to -68.5 degrees, 1.5 along the arc since the second pass; the csv angle column says 288.36).
- Pads: 1.0 dia x 0.5 through the shell, outer face clipped to the band's outer surface; shell holes 1.0 dia.
- Caps are clipped flush to the outer surface (joystick cap 4.6 dia, record cap 5.0 x 3.0); shell openings 5.0 dia and 5.2 x 3.2.
- Mic slots 1.2 (X) x 0.3 (Z) at Z 0.96, through the -Y wall.
- Layer split in layers.json: glass (cover_glass, clear_adhesive), screen (screen, foam, screen_tail), board (main_board and the 15 board parts), band (liner, flexes, joystick, record button, motor, cell, protection, pads), body (outer_body). Explode: glass +Z 14, screen +Z 9, board +Z 4, body -Z 6, band parts outward along their radius 9. Because the band parts sit inside the shell, show the shell transparent when exploding.

## Assumed (what each rests on)
- Power chip nPM1300 height 0.5 mm: not in the architecture; typical WLCSP.
- Crystals 0.5 mm high: not in the architecture; both sit under the 1.0 mm limit.
- Screen supply coil 2.5 x 2.0 x 1.0 (section 2), power coils 2.0 x 1.6 x 1.0 (lead's brief; matches 16.7 area 9.6).
- Screen tail width 5.0 (15 contacts at 0.3 pitch = 4.2 plus margin; the architecture gives no width) and thickness 0.2 (16.4).
- Flex tail thickness 0.15 (17.3 radial stack), width 2.2 (C7).

## Not modelled
Rolled edges (top 0.9, bottom 1.2), the 0.4 plate and 0.15 flex under the switches, the resin fill, the recording light, test pads, small parts (0201 and similar; about 60 on the board, 16.7), the antenna match parts, the mic membranes and gaskets, the cell's swelling room.

RESULT: done, 37 parts, check last line `RESULT PASS pairs=665 parts=37`, motor at 49 deg (no angle in 34 to 48 passes both wall and block), least metal 0.400 mm with the flat 3.6 zone kept to 61 deg (ruled 57 gives 0.275 mm), also C8 protection arc 1.5 and C9 joystick board notch
