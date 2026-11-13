# Band conflicts: measured options (model 17.8 on ring-merged32c.step; controls and exterior fixed)

Measured = a model build and the motor-rim ray test (least metal along the outward ray from 48 rim points; limit 0.40) or the check; calculated = arithmetic on the model's numbers, not a build. Files: out/options/ (thin_opt.py is the live thin.py with parameters; options.py and options.log, v7_polar.py, recess.py, best/). Live model files untouched.
Fixed numbers: channel 6.8 wide (band 8.0, edges 0.6), liner 0.3 (r 9.475 to 9.775), cell 1.6 thick at r 9.775 to 11.375, shell inner face r 11.575, flex ribbon 0.15 thick, shoulders 3.6 (outer r 13.075, easing to 2.6 at 85), motor wall rule 0.40.

## A. Thumb side: the ribbon must pass the motor at +51 to reach the record switch (+88) and the joystick (+150) (S16)
| Option | Result | Fits? | Cost |
|---|---|---|---|
| Baseline: 7.0 x 2.1 motor, 7.2 pocket in a 6.8 channel | wall 0.400 (measured); no room beside the motor: the pocket is wider than the channel | no | already the model |
| A1a ribbon embedded in the liner under the motor (calculated) | liner 0.30 holds ribbon 0.15 + skins 0.075 + 0.075; motor stays on the liner at r 9.775; wall stays 0.400 | yes, with 0.075 mm resin skins (thin for a cast skin) | none visible; the liner becomes a flex-in-resin laminate |
| A1b ribbon on the liner, motor lifted 0.15 (measured) | wall 0.275 (-0.125) and 0.013 mm3 of the motor in the block | no | to restore 0.40 at the rim: outer radius +0.125 there, so the shoulder 3.6 to about 3.75 (calculated), and the motor at 52 degrees to clear the block |
| A2a Jinlong W0525AB001D, 5.0 x 2.5 coin (slim-2.md 1.4, datasheet read, third-party host), X +0.7 beside a 1.4 mm ribbon (measured) | wall 0.425, 0.0000 mm3 in the block; channel use: ribbon X -3.3 to -1.9, pocket 5.2 (X -1.9 to 3.3), 0.1 to the channel wall; zero spare width | yes | none visible; 1.4 mm ribbon (7 lines at 0.2 mm); motor is BLDC with start current under 175 mA (VC0720B088L: 85 mA max rated, 3.0 V), 0.25 G; 0.4 taller (2.5) |
| A2b Vybronics VC0625B001L / Jinlong W0625SS001D, 6.0 x 2.5 | pocket 6.2: 6.8 - 6.2 - 0.2 = 0.4 mm left: ribbon at most 0.4 wide (calculated) | no | |
| A2c PM 304-129.001, 4.4 dia x 6 long cylinder (slim-2.md 1.7, datasheet read) | radial room 12.575 - 9.775 = 2.8 mm at 3.6 shoulder; 4.4 needs 4.4 + 0.1 + 0.5 roof wall = 5.0 radial (calculated) | no, by 2.2 mm | |
| A2d KPD3A-03208 3.2 dia x 8.1 (architecture section 2, lying along the band) | needs 3.2 + 0.1 + 0.5 = 3.8 radial; room 2.8 (calculated) | no, by 1.0 mm (shoulder about 4.1) | |
| A3 widen the band locally (calculated) | with the 7.0 motor: 7.2 + 0.1 + 1.4 + 0.1 + 2 x 0.4 walls = 9.6 mm; today 8.0 leaves (8.0 - 7.2) / 2 = 0.40 per side beside the motor, before the exterior's 1.0 edge rounding | band 9.6 wide at the motor (+1.6), 10.4 for a 2.2 ribbon | visible: the shoulders flare |
| A4 motor on the away side at -51 with the cell shortened (measured for the motor) | wall 0.400, block 0; cell must end by about -72 (back rim at -70.7): 121 degrees = 22.4 mm, 215 mm3, 11.6 to 15.5 mAh (now 28.4 mm, 15 to 20 mAh) | moves the blockage: the away ribbon from the slot (-37) to the cell tab (-72) must then pass the motor | none visible, loses 4 to 5 mAh |

## B. Other side: the ribbon must reach the cell tabs (-39) and the pads (-150)
| Option | Result | Fits? | Cost |
|---|---|---|---|
| B1 ribbon between the cell and the shell wall (modelled and checked, see best/) | gap (11.575 - 11.375) = 0.20 for a 0.15 ribbon: 0.05 spare; it touches the pads' inner ends (r 11.575) along the way; runs 119 degrees (23.9 mm) from the slot to -150 | yes (check passes) | none visible; no resin between ribbon and shell (0.05); the ribbon is 1.4 wide |
| B2 ribbon inside the liner (calculated) | reaches the cell tabs; to reach the pads it must cross the cell: side gap (6.8 - 6.0) / 2 = 0.4 per side, so a ribbon of at most about 0.3 mm wide | tabs yes, pads no | |
| B3 pads next to the cell end (measure only, calculated) | pads at -45 instead of -150: ribbon 2.8 mm instead of 23.9 mm | yes | visible: the pads move 105 degrees round the band |
Side effect of B1 (not modelled): the cell could end at -31 instead of -39 (+1.5 mm); the protection circuit then needs 4 more degrees of channel past -30, where the floor leaves 0.4 mm: untested.

## C. Openings (S17), for the exterior's builder (measured on the curved surface, v7_polar.log)
The exterior body has no recess at either control: it is solid at the opening centres (recess.py: 0.0 at every depth), the nub, frame and pill are separate solids on its surface. The model cuts a rectangular (sharp-cornered) joystick opening through the shell 6.6 along the band x 5.6 along X (frame 6.4 x 5.4 plus 0.1 each side; the frame has 1.0 corner radius, so the exterior's opening should be rounded 1.1; nub 4.6 x 3.6, radius 0.8), under it a 7.0 x 6.6 pocket; record opening 4.6 x 2.6 (pill 4.4 x 2.4), flange seat 5.4 x 3.4 from 0.3 mm under the surface. Metal left at 0.1 / 0.3 mm under the surface: joystick along X 1.07 / 1.19, along the band 0.59 / 0.99; record along X 1.57 / 1.69, along the band 2.0+ / 0.0 (the flange seat). All at least 0.40 except the seat. Largest openings that keep 0.40 mm: joystick half-width X 3.47 (opening 6.9), half-length along the band 3.49 (opening 7.0) at 0.1 deep; pill half-width X 3.47 (6.9). The earlier V7 text that said 0.0 along the band was an artifact of a flat-frame measurement and is corrected in thin-notes.md.

## D. Motor wall at exactly 0.400 (calculated: the rim ray is radial, so the wall grows 1:1 with the outer radius there; not re-measured on a re-lofted body)
Shoulder 3.6: 0.400. 3.7: about 0.500. 3.8: about 0.600. With option A2a (0.425 at 3.6): 0.525 at 3.7. A1b needs 3.75 for 0.40.

## Best option per conflict (no visible change; modelled in out/options/best/, check passes)
A: A2a (5.0 x 2.5 motor, ribbon 1.4 beside it). B: B1. C: numbers above (the exterior builder cuts the openings). Best model: out/options/best/thin.py, check_thin.py, placement.csv, layers.json, out/thin-inside.glb. out/options/best/check.log: motor rim 0.425, 0 collisions, `RESULT PASS pairs=665 parts=37`, 351,984 triangles. Both flex ribbons now run: thumb from the slot on the liner to the record switch and the joystick (X -3.3 to -1.9, then a 6.6 wide head under the switches), away from the slot between cell and shell to the pads. Not swapped into the live model. Not done: electrical check of the 5.0 BLDC motor against the 3.0 V rail and Q1; the inside-body test is the vertex-sample test (a ribbon crossing a wall without a vertex outside would pass).

RESULT: done, options A1 to A4, B1 to B3, C and D measured or calculated as marked; best = A2a (5.0 x 2.5 coin, wall 0.425) + B1 in out/options/best/, check last line `RESULT PASS pairs=665 parts=37`, live files untouched

Stopped: positions void (the owner moved the joystick off +150; nothing here is to be used for the new position).
Measured before the stop: motor wall at +51 for baseline, A1b (lift 0.15) and A2a (5.0 x 2.5) and the motor at -51 (A4); the opening metal on the curved surface (v7_polar.log); the best model A2a + B1 passed check_thin.py at the +150 positions (out/options/best/check.log).
A3, B2, B3, D and the slim-2.md motor sizes are calculated; they do not depend on the joystick angle except the ribbon runs and the cell end.
