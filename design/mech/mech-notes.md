# Ring recorder, 3D model notes (mechanics step; architecture.md A2; round 2) - OLD BLOCK MODEL, replaced by the inside model in design/mech/thin/ (thin.py, model v9; notes design/mech/thin/model-v9-notes.md) with the exterior in design/look/s1/; the numbers below describe the one-block model of version A1 and are not edited

## What was built

- `ring.py`: one parametric build123d script. Every dimension sits in `DIM_TABLE` at its top; `dimensions.csv` is written from it (name, value_mm, source; ASSUMED and CHANGED rows say so). Running it writes `dimensions.csv`, `placement.csv` and every file in `out/`. A test override without editing: `RING_OVERRIDE="cell_t=5.6" python ring.py`.
- Housing: top shell (walls 1.0, plan corner radius 2.4, glass seat for a 28.6 x 13.3 x 0.5 glass, screen pocket, four 0.8 mm microphone openings at X -12.0, -5.5, +1.0, +7.5 and Y 4.9, a 2.0 mm clear-window recess 0.4 deep and a 1.0 mm light hole at X +4.0, a 5.0 mm joystick opening in the thumb wall at X -6.0, a 2.0 x 1.4 record-key opening at X +4.0, a pocket over the joystick board, two screw bosses). Base: floor 0.8, contact-board window at X -12.6 with ledges and a raised pad, two M1.2 clearance holes with counterbores, gasket groove 0.5 wide, one motor cradle rail, and the band for US sizes 5 to 13 (width 8.0, wall 2.0, fillet r0.5 into the floor).
- Band inner diameter = 11.63 + 0.8128 x size, checked on en.wikipedia.org/wiki/Ring_size (saved raw text `src_text/wikipedia_ring_size_raw.txt` line 81). Size 5: 15.69 mm, size 9: 18.95 mm, size 13: 22.20 mm.
- Internal parts (positions in `placement.csv`): cover glass, clear adhesive, screen, foam pad, main board with the joystick notch, joystick board, joystick body and stem, 4 microphones, record button, push plate and printed key, recording light, clear window, antenna, motor and its 0.3 mm sleeve, cell and its 0.5 mm swelling volume, contact board, contact protection chip TPD4E05U06, screen cable fold, screen connector FH35C-15S-0.3SHW, storage, main chip, power chip (3.1 x 2.4 x 0.5), screen supply chip and coil, gasket, 2 screws, 6 wire pads on the main board and 6 on the joystick board.
- `check_fit.py`: pairwise intersection volume of all internal solids, each solid against the top shell and the base of all 9 sizes, every solid inside the cavity, no metal part in the antenna keep-out (X 9.9 to 14.1, Y 4.3 to 9.0, Z 0.8 to 9.5, under and over the board), and the new wall-thickness rule. Any volume above 0.001 mm3, any wall under 0.5 mm, or any boolean error gives exit 1.
- Wall-thickness rule (round 2): every face of every housing solid is sampled (triangle centres of a 0.15 mm tessellation, projected onto the true surface); from each sample a ray goes into the material along the inward normal and the distance to the next face is the local thickness. Under `min_wall` = 0.5 mm (ASSUMED in `dimensions.csv`, to be confirmed by the printing service) is a finding; samples within 1.0 mm count as one place. A 0.001 mm allowance absorbs ray noise, so exactly 0.5 passes. Limit of the method: it measures along surface normals only, so a thin spot that is thin only on a diagonal is not seen.
- Proof the wall rule fails before the fixes: on the round-1 model it reported 45 places on the top shell and 58 to 60 per base, exit 1 (`logs/r2_wallrule_before_fix_v2.log`). An earlier version of the rule gave false 0.000 readings on curved faces (`logs/r2_wallrule_before_fix.log`); I fixed the normal projection and kept both logs.
- Final model: 0 places under 0.5 mm on the top shell and on all 9 bases, thinnest 0.500 mm (`logs/r2_final2.log`); collisions 0; exit 0. Proof the collision check still fails: cell 1 mm thicker gives 15 findings, exit 1 (`logs/r2_failproof_cell_plus1_final.log`).

## Differences from architecture.md (for version A3)

| Position | Architecture value | Model value | Reason |
|---|---|---|---|
| Block plan corner radius | not in s6 (brief: 3.0) | 2.4 | at 3.0 the screen-pocket corners kept 0.325 mm of wall; 2.4 gives 0.6 |
| Cover glass | 28.6 x 13.6 x 0.5 (s6) | 28.6 x 13.3 x 0.5, Y -9.4 to 3.9, corners r1.75 (-Y) and r0.5 (+Y) | the seat lip on the -Y side was 0.25; it is 0.55 now. The glass still covers the screen corners (0.03 margin) |
| Screen | position not given | X -13.675 to 13.675, Y -8.95 to 3.85, Z 8.1 to 8.9 | stays under the r1.75 glass corners |
| Cell along X | -11.6 to +13.4 (s6) | -11.9 to +13.1 | +X corner clears the 1.4 inner wall radius by 0.1; -X end leaves room for the contact-board ledge pad (to -12.0) |
| Cell across Y | screen zone -9.0 to +3.9 (12.9 wide) | -8.8 to +4.2 | the cell is 13.0 wide; it enters the 0.4 zone gap, not the strip (from 4.3) |
| Motor X centre | -7.2 | +3.925 (body -1.875 to 9.725) | the upright joystick board fills the strip at -7.2. Round 2: no move toward -X is possible, the sleeve already starts 0.1 from the joystick body end (-2.275), which the joystick board ends flush with |
| Motor Z | 0.8 to 4.0 | 1.1 to 4.3 | the 0.3 mm sleeve sits on the floor at 0.8 |
| Motor Y | strip, not given | axis 6.5 (sleeve 4.6 to 8.4) | one 0.55 cradle rail fits on the +Y side; two rails of 0.4 broke the wall rule |
| Motor gap to antenna keep-out | not given | 0.175 mm (body), sleeve enters by 0.125 | open radio risk, see below |
| Mic 1 X | -12.0 | -11.9 (opening stays at -12.0) | at -12.0 the body touches the wall |
| Microphones Y | not given | centre 4.9; mic 3 turned 90 deg (3.0 along X) | the openings keep 0.55 to the glass seat edge (3.95); mic 3 turned clears the record button |
| Antenna | on top of the board, X +12.0 | under the board, X 10.4 to 13.6, Y 5.85 to 7.45, Z 6.1 to 7.3 | lead round 2: on top it needed a pocket with a 0.35 skin; the full 1.0 top plate is back |
| Record button recess | 0.8 mm (s6) | no recess pocket; key face 0.3 below the wall face, opening 2.0 x 1.4 | the 0.8 recess left a 0.2 skin |
| Contact board thickness | 0.6 (s6) | 0.4, pads flush with the underside | lead round 2 |
| Contact board ledge | not given | 0.4 wide on +Y and -Y, 0.6 on -X, open under the cell end; floor raised to Z 0.95 over X -13.95 to -12.0 so the ledge is 0.55 thick | a 0.4 ledge in a 0.8 floor over a 0.4 board is 0.4 thick; the -X ledge at 0.4 made a 0.35 lip |
| Screws | 4 x M1.2 x 3 at the corners (s6) | 2 x M1.2 x 3 at (-12.35, 7.0) steel and (+12.35, 7.0) non-metal (PEEK or nylon, ASSUMED available), boss r1.0, head 2.0 x 0.3 in a 0.3 counterbore | see "Screws" below |
| Gasket groove | 0.5 mm, in a groove (s6) | 0.5 wide, 0.55 to 1.05 in from the outer edge, 0.25 deep | outer lip 0.55, floor under it 0.55 |
| Joystick board | 9.0 x 8.0 x 0.6 upright (s6) | X -11.275 to -2.275, Y 6.45 to 7.05, Z 0.8 to 8.8; pocket in the top plate to 8.85 (skin 0.65) | the strip top is at 8.5 |
| Joystick link | flat cable 6 wires (s6) | 6 wire pads 0.5 x 0.5 on the main board top (Y 5.7 to 6.2) and 6 on the joystick board face; wires not modelled | architecture A2 s14 per the lead |
| Main board | 27.0 x 17.4 x 0.6, position not given | X -13.6 to 13.4, Y -8.7 to 8.7, corners r1.5 | the cable fold (13.4 to 14.0) stays free |
| Screen cable fold | X 13.4 to 14.0 | X 13.4 to 14.0, Y -6.55 to 1.45 (8.0 wide, ASSUMED), Z 6.3 to 7.9 | |
| Screen connector | not placed | X 7.5 to 12.7, Y -8.3 to -5.1, Z 6.4 to 7.3 (5.2 x 3.2 x 0.9 ASSUMED) | under the board near the fold, clear of the coil |
| Protection chip | not placed | on the contact board, X -12.9 to -11.9, Y -1.25 to 1.25, Z 0.4 to 0.9 (height ASSUMED) | in the opening above the board |
| Chips under the board | not placed | row at Y -2.5: main chip X 1.0, power chip X 5.0, screen supply chip X 8.5, coil X 12.0; storage X -5.0, Y -5.0 | screen zone, no collision |

## Screws

At the X ends, the pilot rib (0.5 each side of a 0.95 pilot), the 1.3 clearance hole and the gasket groove with 0.5 lips need 3.275 mm from the cell end to the outer face (0.1 gap + 0.5 rib + 0.475 pilot radius + 0.65 clearance radius + 0.5 lip + 0.5 groove + 0.55 outer lip); there are 1.9 (cell end 13.1, outer face 15.0). The -Y side has 0.2 mm between the cell and the wall. So with the 25.0 x 13.0 cell, M1.2 fits only at the two +Y corners; M1.0 does not fit at the X ends either (the groove conflict stays). The +X corner screw sits inside the antenna keep-out, so it is non-metal in the model. The -Y side has no fastener: it needs adhesive on the gasket line or snap hooks; question below.

## Walls and smallest gaps

- Wall rule result: 0 places under 0.5 mm on all 10 housing files. Two places sit exactly at 0.500: the plate under the glass seat edge (top plate 1.0 minus the 0.5 glass seat) and the floor over the screw counterbore (0.8 minus 0.3).
- Smallest open gaps from `check_fit.py` (`logs/r2_final2.log`): foam pad to shell 0.010, wire pads on the joystick board to the shell pocket 0.015, then 0.05 (joystick board to the shell, cell to the gasket, joystick board to mics 1 and 2, adhesive to the shell).

## Open radio risk

The motor body ends 0.175 mm from the antenna keep-out, under the 1.0 mm the lead set. The motor cannot move further toward -X (it is 0.1 from the joystick body). Options: a shorter motor, or the antenna and keep-out moved toward +X if the board allows; both need the lead or the owner.

## Mass estimate (size 9)

`mass.py` gives 8.46 g (`out/mass-estimate.csv`). Densities: PA12 1.01, glass 2.42, FR-4 1.85, steel 7.9, silicone 1.1 g/cm3 are handbook values not fetched in this run (unverified); cell 2.0, screen 2.5, chips 2.3, switches 2.0 are ASSUMED; motor 0.7 g from architecture.md s2. The cell figure is the weakest; the Grepow sample weight replaces it.

## What a printing service needs (nylon PA12, multi-jet fusion, dyed black)

- Files: `out/top-shell.stl` (all sizes) and `out/base-size5.stl` to `out/base-size13.stl`, each with a STEP copy, units mm.
- Wall check: the model holds 0.5 mm everywhere by the rule above (normal-direction sampling). Ask the service to confirm 0.5 as its minimum and to run its own wall check.
- Holes: pilot 0.95 for M1.2 self-tapping, clearance 1.3, microphone openings 0.8, light hole 1.0. Ask whether small holes print undersize.
- Glass seat and screen pocket clearance 0.05 per side: tighter than MJF tolerance (unverified); plan to sand or reprint.
- Cover glass is a bought part: 28.6 x 13.3 x 0.5, corners r1.75 on the -Y side and r0.5 on the +Y side.

## Not done or open

- ASSUMED values to confirm: mic port position, joystick stem diameter 2.5, key and push plate, cable width, screw head 2.0 x 0.3, gasket depth 0.25, clear window 0.4, protection chip height, connector footprint, wire pad size, non-metal M1.2 screw availability.
- The record button datasheet notes a PCB height of 0.975 mm (mid-mount); the model hangs the 1.95 mm body under the board.
- Wires (contact board, joystick link) are not modelled.
- architecture.md is the lead's file; the table above is for A3.

## State at stop

The lead stopped round 2 on 2026-11-10: the owner rejected the exterior, and the shell will be redesigned. All files are saved as they are. The last full run, after the last code change, is `logs/r2_final2.log`: ring.py and check_fit.py both ran, exit 0, and the cell +1 mm proof gave exit 1. The internal part positions and the collision check stay valid for reuse. The wall rule in check_fit.py also stays; it will apply to the new shell.

| Round 2 fix | State | Evidence |
|---|---|---|
| 1. Antenna under the board, keep-out over and under the board, full 1.0 top plate | done | placement.csv antenna Z 6.1 to 7.3; wall rule 0 places |
| 2. Motor toward -X, report the gap | done as a report; no move possible (0.1 from the joystick body), gap 0.175 mm, open radio risk | logs/r2_derived_final.log |
| 3. Record button recess without skins under 0.5 | done | key 0.3 below the wall face, no recess pocket |
| 4. Contact board 0.4 on a 0.4 ledge, pads flush | done, with a raised pad and a 0.6 -X ledge so the rule holds | dimensions.csv cb_* rows |
| 5. Glass seat lip and screen-pocket corners at 0.5 | done (glass 28.6 x 13.3, corner radius 2.4); belongs to the rejected exterior | logs/r2_final2.log |
| 6. Screw ribs at 0.5 | done by moving to 2 screws at the +Y corners; the -Y side has no fastener; belongs to the rejected exterior | logs/calc_screw_budget.log |

Section 14 parts (protection chip, wire pads, screen connector) are added. Fixes 5 and 6 and the corner radius are shell changes, so they will probably be replaced by the new exterior.

## questions_for_owner

1. Join: two M1.2 screws at the +Y corners (one non-metal) plus adhesive or snap hooks on the -Y side, instead of four screws?
2. Radio: accept the motor 0.175 mm from the antenna keep-out for the first prototype, or change the motor or the antenna position?

RESULT: done, check_fit.py exit 0 on the final run and out/ holds 32 files.
