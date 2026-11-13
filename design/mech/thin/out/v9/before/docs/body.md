# Specification: metal body (block and band), reference HSG1

Design version A5, architecture section 17.8 (2026-11-10), refreshed to the inside model v6.2 (architecture 17.11, 17.15, 17.19, 17.24 to 17.27; exterior merged32f, and merged32g on US 7 and US 8), and to design version 7 (architecture 17.29 and 17.30; exterior merged32h: round joystick opening 5.60 with the separate frame FRM1, gloss black finish; the recording light is removed in v7 and the body has no part of it). All dimensions in mm. Axes: X along the finger (+X fingertip), Y across (-Y is the joystick side, the side the thumb works; the older name "+Y thumb side" is retired, 17.11), Z up. Angles are measured around the finger from the top of the band; minus is the joystick side (the joystick is at -78 degrees on US 9 to 13, motor at -44 degrees on US 9; the values per ring size are in the last section).

> **The body files carry every inside pocket since 2026-11-11:** one STEP and one STL per ring size, design/mfg/parts/body/body-us7 to body-us13, cut from the inside model v7 (design/mfg/parts/index.csv; design/mfg/parts-notes.md). Before that date the body files were the outer shape only.

## What it is
The one-piece metal body of the ring: a flat block (holds screen, board, glass) that flows through two shoulders into an 8.0 mm wide band that goes round the finger. The band is a hollow channel, open toward the finger, later closed by the band liner (specs/band-liner.md). It carries the pockets and openings for the screen, glass, 2 microphone floor pockets with their holes and seats on the underside, 2 floor slots, the joystick opening and pocket, and the motor pocket. The ring has one control, the joystick (17.11): no record button, no record cap and no opening for one. The four charging pads sit in the liner on the inside of the band, so the body has no pad holes (17.12). Before v5 this page listed microphone wall slots, a record cap opening, 4 pad holes and the joystick at 150 degrees.

## Quantity per ring
1 body per ring. One body per ring size, 7 sizes (US 7 to 13). Sizes US 5 and 6 are out of version 1 (owner, 2026-11-11: "US 7 to 13 (Recommended)").

## Material
Titanium grade 5 (Ti-6Al-4V), machined from bar (architecture 17.29). Reason: strength at 0.4 to 0.6 mm walls, skin-safe, takes the gloss black coating. The joystick frame FRM1 is the same material and is coated in the same batch as the body (specs/joystick-nub.md).

## Process
Default, to confirm with the maker: CNC machining from bar (multi-axis), one piece. Whether one piece can be machined, or the band must be turned and the block milled and joined, is open point 1 (architecture S13).

## Finish and colour
Owner's decision (2026-11-11, architecture 17.29): one dark glossy finish, no bare metal. The body is polished, then coated gloss black (PVD or DLC; the maker names the process). The glass seat and the microphone seats are masked or finished after coating: open point 4. Coating thickness and Ra: open point 4.

## General tolerance and tighter tolerances
General: ISO 2768-m (default, to confirm with the maker). Tighter, ISO 2768-f (default, to confirm with the maker), on: the screen pocket, the glass seat, the two floor slots. Reason: the screen leaves 0.15 mm or less of clearance and the corner metal is thin. Any tolerance tighter than ISO 2768-f: open point 5.

## Critical dimensions
Values from architecture.md section 17.1, 17.3, 17.8. Angles in degrees.

| name | value | tolerance | where it is measured |
|---|---|---|---|
| block length (X) | 29.3 mm | ISO 2768-m | over the block, at the underside |
| block width (Y) | 14.75 mm | ISO 2768-m | over the block, at the underside |
| block plan corner radius | 2.5 mm | ISO 2768-m | plan view, the four corners (fallback 2.2 mm if the maker cannot machine 0.27 mm of metal: S13) |
| block height at the centre line | 3.85 mm | ISO 2768-m | underside to top of the finished glass surface, centre line |
| block height at the long edges | 2.95 mm | ISO 2768-m | underside to top of the glass at a long edge |
| overall body width (Y), US 9 | 25.149 mm | ISO 2768-m | over the band and the joystick's raised zone, the STEP box of body-us9.step (before model v6.2 this page gave 24.15, the width without the raised zone) |
| overall body height (Z), US 9 | 24.6952 mm | ISO 2768-m | underside of the band to the top of the block, the STEP box of body-us9.step |
| gap, floor top to parts under the board | 0.05 mm | ISO 2768-f | block stack 17.2, inside the block cavity |
| height for parts under the board (tallest: coil 1.0) | 1.00 mm | ISO 2768-f | block stack 17.2, cavity height between floor gap and board underside |
| board thickness seated in the cavity | 0.30 mm | open point 5 | block stack 17.2 (the board is its own part, specs/main-board.md) |
| foam pad thickness above the board | 0.10 mm | open point 5 | block stack 17.2 |
| screen panel seat thickness | 0.80 mm | ISO 2768-f | block stack 17.2, panel seat |
| clear adhesive thickness under the glass | 0.10 mm | open point 5 | block stack 17.2 |
| board cavity, length | 27.2 mm | ISO 2768-f | board outline 17.2 (the cavity is larger by the clearance, open point 2) |
| board cavity, width | 12.6 mm | ISO 2768-f | board outline 17.2 (same) |
| band stack inside the shell: liner | 0.3 mm | open point 5 | radial, band channel (specs/band-liner.md) |
| band stack inside the shell: cell | 1.6 mm | ISO 2768-f | radial, band channel |
| band stack inside the shell: gap cell to shell | 0.2 mm | ISO 2768-f | radial, band channel |
| joystick stack: flex | 0.15 mm | open point 5 | radial, under the switches (17.3) |
| joystick stack: switch | 0.53 mm | by the switch maker | radial (17.3) |
| joystick stack: cap flange | 0.4 mm | ISO 2768-f | radial, the flange of the cap CAP1 (17.3, 17.29) |
| floor thickness of the block | 0.40 mm | ISO 2768-f | under the board, over the whole block floor |
| band width | 8.0 mm | ISO 2768-m | across the band, outside surface |
| band thickness | 2.6 mm | ISO 2768-m | radial, outside to the liner face, away from the shoulders |
| shoulder thickness | 3.6 mm | ISO 2768-m | radial, at 19 to 61 degrees on both sides, flat zone |
| shoulder zone start | 19 deg | ISO 2768-m | from the top, both sides |
| shoulder flat zone end | 61 deg | ISO 2768-m | from the top, both sides; eases back to 2.6 mm by 85 deg |
| hollow curve block to band | radius 4.0 mm | ISO 2768-m | side view of the shoulder |
| band inner diameter, US 9 | 18.95 mm | ISO 2768-m, a plus-only tolerance is open point 6 | across the finger face of the finished liner (the 0.3 mm resin skin); the metal never touches the finger |
| shell wall, outside | 0.5 mm | ISO 2768-f | band outside to channel roof, anywhere |
| shell wall at each band edge | 0.6 mm | ISO 2768-f | band edge |
| band channel width | 6.8 mm | ISO 2768-f | between the two edge walls, open side |
| microphone floor pocket, size | 4.4 x 3.35 x 0.10 mm | ISO 2768-f | in the top face of the floor under each microphone: X -13.0 to -8.6 (left) and 8.6 to 13.0 (right), Y -6.45 to -3.10; floor left under it 0.305 mm (floor rule 0.30) |
| microphone hole | dia 1.0 mm | ISO 2768-f | straight through the floor, not plated, at X -11.77 and +11.77, Y -4.8 (one under each microphone port) |
| microphone membrane seat | dia 2.0 x 0.10 mm | ISO 2768-f | counterbore on the underside, same axis as the hole, Z 0 to 0.10 |
| ring of metal between seat and hole | 0.205 mm | KNOWN EXCEPTION, the body maker must accept it (open item S23) | Z 0.10 to 0.305, between the dia 2.0 seat and the dia 1.0 hole |
| least metal round each microphone seat | 0.72 mm | not a tolerance, a minimum (rule 0.40) | toward -Y at Z 0.05 |
| screen panel, length | 27.35 mm | the pocket takes ISO 2768-f | pocket is larger than the panel; clearance is open point 2 |
| screen panel, width | 12.8 mm | same | same |
| screen panel, thickness | 0.8 mm | same | pocket depth is open point 2 |
| minimum metal at the screen corners | 0.27 mm | not a tolerance, a minimum | plan view, the diagonal at each of the four corners (S13) |
| joystick opening diameter | 5.60 mm | ISO 2768-f | round, axis on the radial line at the joystick angle (-78 deg at US 9, per size below), through the wall from the outer surface to the pocket roof, joystick side; straight cut, no chamfer (merged32h, 17.29) |
| joystick frame FRM1 | 5.40 mm outer diameter, 4.80 bore, 1.30 long | ISO 2768-f on both diameters | separate part (specs/joystick-nub.md), bonded in the opening with 3M Scotch-Weld DP420 Black, 0.10 mm radial gap; 0.80 under the band surface to 0.50 above it |
| joystick pocket | 7.0 mm along X by 6.8 mm around the band | ISO 2768-f | from the inside of the band (the bore) up to a flat roof; roof radius 10.9026 at US 9, per size in the last section (17.26); least metal round it 0.500 mm (model v5, US 9); the liner fills a 0.1 mm strip on each side, where the 7.0 pocket is wider than the 6.8 channel |
| joystick position | -78 deg on US 9 to 13; -81.0 deg on US 8; -84.0 deg on US 7 | ISO 2768-m | centre of the opening, from the top, on the joystick side (-Y); lower on the two small sizes (17.25, the owner confirms on a picture) |
| joystick flange | 6.9 mm along X by 6.4 mm around the band, 0.4 thick | ISO 2768-f | model v6 (17.24 K12, 17.26): the channel is not cut over the joystick; the pocket runs to a flat roof 0.05 mm above the flange top; free space flange top to metal 0.050 at band +-3.1 (US 9); the flange is held by the roof round the round 5.60 opening on all four sides (6.9 and 6.4 both over 5.60, v7); before v6 the flange was 6.4 with 0.297 mm of play |
| least metal round the joystick opening | 1.067 mm on the X sides, 1.097 mm toward the bottom (US 9) | not a tolerance, a minimum (rule 0.50) | 0.1 mm under the outer surface; per ring size in the last section (merged32h-report) |
| motor diameter (pocket is larger) | 5.0 mm, pocket 5.2 mm | ISO 2768-f | Jinlong W0525AB001D, pocket at -44 deg (US 9), joystick-side shoulder; before v5: 7.0 mm at 51 deg |
| motor thickness | 2.5 mm, pocket 2.6 mm | ISO 2768-f | the pocket floor lies 0.05 mm under the motor at every size (17.27); pocket depth is larger by the gap, open point 3 |
| motor position | -47.0, -45.5, -44.0, -45.0, -43.5, -42.5, -42.5 deg on US 7 to 13 | ISO 2768-m | from the top, joystick-side shoulder, 0.7 mm off the band's centre line (17.26, 17.27, model v6.2); before v6: -43.0, -41.5, -40.5, -39.5 on US 10 to 13 |
| least metal round the motor pocket | 0.425 mm (US 7 to 9), 0.450 mm (US 10 to 12), 0.475 mm (US 13) | not a tolerance, a minimum (rule 0.40) | measured outward from every point of the pocket rim; least value at the front rim (model v6.2) |
| charging pad holes | 0 (none) | not a dimension | the four pads (1.6 mm gold discs) sit in the liner on the inside of the band, opposite the block (17.12, 17.15); the body has no pad holes |
| glass seat lowering | 0.05 mm | ISO 2768-f | seat lowered 0.05 mm inside the body under the glass footprint, outside the panel pocket, for the seal ring SEAL1 (17.23 K-A4, 17.24); the outer shape does not change |
| glass face arc radius | 30.7 mm | ISO 2768-f | top of the block across the finger: the seat for the glass |
| glass face rise | 0.90 mm | ISO 2768-f | from the long edges to the centre line |
| side roll radius | 1.0 mm | ISO 2768-f | from the arc into the side walls |
| end roll radius | 1.2 mm | ISO 2768-f | the two ends of the block |

## Model values to confirm (not in the architecture, taken from the 3D model design/mech/thin/thin-notes.md, section "Model v5", US 9)
Floor slots 2.0 x 0.6 at Y = +-5.9, from X = -3.5 to X = -1.5 (two; model v6.2, architecture 17.27: shortened from 2.6 x 0.6 to keep at least 0.30 mm of metal beside the motor pocket). On ring sizes US 7, 8 and 9 the motor pocket opens into the block's cavity through a window of about 4.0 x 1.1 mm (the pocket grown by 0.30 mm intersected with the cavity grown by 0.30 mm), closed at assembly by the sealant plug SEAL2; on US 10 to 13 a wall of at least 0.30 mm stands there. Motor pocket angle per size: -47.0, -45.5, -44.0, -45.0, -43.5, -42.5, -42.5 degrees on US 7 to 13; the pocket floor lies 0.05 mm under the motor. Earlier text of this line: floor slots 2.6 x 0.6 at X = -2.2 (corrected 2026-11-11 from X = -4.7: inside model, thin-notes.md K7; assembly.md conflict K-A10). The bottom of each slot lies at Z -0.20 on US 7 and 8, then -0.23, -0.63, -1.04, -1.45, -1.85 on US 9 to 13 (17.26, model v6), so each ribbon reaches the band channel at every size. Beside each slot, under the board, 2.6 x 2.2 x 1.03 mm stay free for one ribbon fold (K-A6). Panel pocket = panel + 0.05 per side (27.45 x 12.9), corner radius 0.1. The microphone pockets, holes and seats are in the table above; no microphone slot exists in any wall. These are the modeller's choices; the maker takes the STEP file for the final geometry once the parts helper has delivered it.

## What to inspect
First article, then each lot sample: overall block length, width, height at centre line and at the long edges; floor thickness at 3 points; band inner diameter with a ring gauge (plug) at the ring's size; band width; shoulder thickness at 40 and 60 deg; shell wall at the motor pocket rim and at the four screen corners (0.27 mm minimum; the corner is the hardest); joystick opening dia 5.60 (pin gauge) and its position at -78 deg (US 9; per size below), FRM1 bonded with a closed DP420 bead and its top 0.50 above the surface; microphone hole and seat positions at X +-11.77, Y -4.8 and the 0.305 mm floor under each pocket; motor pocket 5.2 x 2.6 at -44 deg; fit of a dummy glass (formed to 30.7 mm) in the seat; fit of a dummy panel 27.35 x 12.8 x 0.8 in the pocket; coating colour and adhesion; no burr at the microphone holes and seats and at the floor slots. Method and sampling plan: open point 5.

## Ring sizes
Inner diameter = 11.63 + 0.8128 x size (mech-notes.md line 7). One body per size; the block, glass seat, microphone pockets and screen pocket are identical across sizes, the band changes. The joystick angle (US 7 and 8), the motor angle, the pocket roof, the floor slot depth and the motor window (US 7 to 9) are values per ring size: the table in the last section (model v6.2, architecture 17.25 to 17.27).

| US size | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|---|---|
| inner diameter, mm [CALC] | 15.69 | 16.51 | 17.32 | 18.13 | 18.95 | 19.76 | 20.57 | 21.38 | 22.20 |

US 5 and 6 are out of version 1 (17.17) and shown for reference only. Whether the shoulder angles stay the same at every size: open point 7. The inside model v6.2 passes its fit check at each of the 7 sizes, US 7 to 13 (17.26, 17.27; each `RESULT PASS`); the owner confirms the lower joystick on US 7 and 8 on a picture (17.25). Before v6 only US 9 passed.

## Files
Drawing: design/mfg/drawings/body.svg and body.pdf (US 9), and body-us7 to body-us13 (.svg and .pdf) for the other sizes (design/mfg/tools/draw.py). STEP and STL: design/mfg/parts/body/body-us9.step and .stl (also us7, us8, us10, us11, us12, us13), listed in design/mfg/parts/index.csv. Status in that index: machined body WITH the inside pockets cut (model v7), so the pockets, slots and openings of the table above are in the STEP file.

## Open points
1. Who machines the one-piece body, and can it be one piece: a ring maker or the design partner answers (S13).
2. Pocket clearance and depth for the screen panel (architecture 16.1 says 0.15 mm per side; the model uses 0.05): the design partner answers, then the maker confirms.
3. Clearance between the motor and its pocket: the design partner answers. The joystick clearances are fixed in v7: frame to opening 0.10 radial, cap to frame bore 0.20 radial (specs/joystick-nub.md).
4. Coating thickness, roughness, masking at the glass seat and the microphone seats: the maker answers.
5. Tighter than ISO 2768-f anywhere, inspection method, sampling plan: the maker proposes, the design partner accepts.
6. Tolerance of the band inner diameter: the maker proposes.
7. Body variants for sizes other than US 9: the values per size are in the last section; the maker takes them from the STEP file per size once the parts helper exports it. The sealant of the floor slots and the motor window (US 7 to 9) is open item S26.
8. Block heights 3.85 and 2.95 (17.8) include the glass. The body's own seat heights are in the STEP file only: the parts helper answers. bom.csv line 53 still says block height 3.2 and an older stack.
9. Closed in v7: the joystick opening is round, 5.60 diameter, through the wall, with the separate frame FRM1 (5.40 outer diameter, 1.30 long, 0.80 under the band surface to 0.50 above) bonded in it (17.29; specs/joystick-nub.md). History: the opening 6.6 along the finger by 5.6 around the band with a rectangular frame (17.24) is removed in v7.
10. Bench items B8 (resin closure, heat, floor-slot sealing) and B9 (joystick feel and sealing) can change the openings.
11. The 0.205 mm ring of metal between each microphone seat and hole is below the 0.30 mm floor rule: the body maker must accept it (17.24, open item S23).
12. Sealing of the glass seat (seal SEAL1 in a seat lowered 0.05 mm), of the floor slots and of the joystick pocket (dam DAM1) is open item S26 (17.23); no rating can be claimed yet.

## Source lines
design/architecture.md lines 417, 418, 420, 424, 428-444 (17.1 to 17.3), 469-470 (S12, S13), 488-494 (17.8), 17.10 line 514 on (before v5 it set the motor at 51 deg); 17.11, 17.12, 17.15, 17.19, 17.23 and 17.24 (the newest; they win: joystick at -78 deg, motor 5.0 x 2.5 at -44 deg, microphone floor pockets, no pad holes); 17.7 at lines 478-482 is replaced; design/bom.csv line 53; design/mech/mech-notes.md line 7; design/mech/thin/thin-notes.md.

## Per ring size values (model v6.2; architecture 17.25 to 17.27; thin-notes.md "Model v6, continued" and "Model v6.2")
The block is the same at every size. Roof span: the channel is left uncut over the joystick for this angle on each side of the joystick centre. Window: the cut between the motor pocket and the block's cavity, sealed by SEAL2.

| US size | Joystick opening and pocket centre | Channel left uncut (roof span) | Pocket roof radius [CALC: bore / 2 + 1.43] | Motor pocket dia 5.2 x 2.6 at | Floor slot bottom Z | Motor window | Metal round the round opening (v7, merged32h-report): X sides / toward the bottom |
|---|---|---|---|---|---|---|---|
| 7 | -84.0 deg | +-19.693 deg | 10.0898 | -47.0 deg | -0.2 | yes, 4.009 x 1.049 | 1.067 / 1.094 |
| 8 | -81.0 deg | +-18.901 deg | 10.4962 | -45.5 deg | -0.2 | yes, 4.017 x 1.100 | 1.067 / 1.094 |
| 9 | -78.0 deg | +-18.171 deg | 10.9026 | -44.0 deg | -0.23 | yes, 4.055 x 1.157 | 1.067 / 1.097 |
| 10 | -78.0 deg | +-17.496 deg | 11.3090 | -45.0 deg | -0.63 | no, wall at least 0.30 | 1.067 / 1.219 |
| 11 | -78.0 deg | +-16.871 deg | 11.7154 | -43.5 deg | -1.04 | no, wall at least 0.30 | 1.067 / 1.344 |
| 12 | -78.0 deg | +-16.289 deg | 12.1218 | -42.5 deg | -1.45 | no, wall at least 0.30 | 1.067 / 1.467 |
| 13 | -78.0 deg | +-15.747 deg | 12.5282 | -42.5 deg | -1.85 | no, wall at least 0.30 | 1.067 / 1.592 |

At every size the body also has: the joystick pocket 7.0 along X by 6.8 around the band from the bore up to the roof, the round opening 5.60 at the joystick angle (v7), the glass seat lowered 0.05, the microphone pockets, holes and seats, and the two floor slots 2.0 x 0.6 at X -3.5 to -1.5, Y +-5.9. Window size is length x height in mm (opening area 1.8969, 1.9087 and 1.9891 square mm on US 7, 8, 9; sealant 0.7967, 0.7937, 0.8107 cubic mm). The edges of each window are at least 0.30 mm thick and the nearest part inside the block is the circuit board, 0.44 to 0.49 mm away.
