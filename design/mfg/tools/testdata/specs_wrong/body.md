# Specification: metal body (block and band), reference HSG1

Design version A5, architecture section 17.8 (2026-11-10). All dimensions in mm. Axes: X along the finger (+X fingertip), Y across (+Y thumb side), Z up. Angles are measured around the finger from the top of the band; plus is the thumb side.

## What it is
The one-piece metal body of the ring: a flat block (holds screen, board, glass) that flows through two shoulders into an 8.0 mm wide band that goes round the finger. The band is a hollow channel, open toward the finger, later closed by the band liner (specs/band-liner.md). It carries the pockets and openings for the screen, glass, 2 microphone slots, 2 floor slots, the joystick frame, the record cap, the motor, and 4 charging-pad holes.

## Quantity per ring
1 body per ring. One body per ring size, 9 sizes (US 5 to 13).

## Material
Default, to confirm with the maker: titanium grade 5 (Ti-6Al-4V), machined from bar. Reason: strength at 0.4 to 0.6 mm walls, skin-safe, takes PVD. Named alternative: stainless steel 316L. Section 16.10 states the housing is machined metal (titanium or stainless steel), not printed plastic.

## Process
Default, to confirm with the maker: CNC machining from bar (multi-axis), one piece. Whether one piece can be machined, or the band must be turned and the block milled and joined, is open point 1 (architecture S13).

## Finish and colour
Default, to confirm with the maker: black PVD coating. Pad holes and the glass seat are masked or finished after coating: open point 4. Coating thickness and Ra: open point 4.

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
| overall body width (Y), US 9 | 24.15 mm | ISO 2768-m | over the band, the STEP box of body-us9.step (outer shape) |
| overall body height (Z), US 9 | 25.28 mm | ISO 2768-m | underside of the band to the top of the block, the STEP box of body-us9.step |
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
| microphone slot, length | 1.2 mm | ISO 2768-f | in the block wall away from the thumb |
| microphone slot, height | 0.3 mm | ISO 2768-f | same slot |
| microphone slot X position | 11 mm | ISO 2768-m | from the block centre, one slot at X = -11 and one at X = +11 |
| screen panel, length | 27.35 mm | the pocket takes ISO 2768-f | pocket is larger than the panel; clearance is open point 2 |
| screen panel, width | 12.8 mm | same | same |
| screen panel, thickness | 0.8 mm | same | pocket depth is open point 2 |
| minimum metal at the screen corners | 0.27 mm | not a tolerance, a minimum | plan view, the diagonal at each of the four corners (S13) |
| joystick frame, along the band | 6.4 mm | ISO 2768-f | opening in the band at 150 deg |
| joystick frame, across | 5.4 mm | ISO 2768-f | same opening |
| joystick position | 150 deg | ISO 2768-m | centre of the frame, from the top; band 3.6 mm thick from 135 to 165 deg |
| record cap opening, long | 4.4 mm | ISO 2768-f | pill opening at 88 deg (clearance to the cap is open point 3) |
| record cap opening, short | 2.4 mm | ISO 2768-f | same |
| record cap position | 88 deg | ISO 2768-m | from the top, thumb side |
| motor diameter (pocket is larger) | 7.0 mm | ISO 2768-f | pocket at 49 deg, thumb-side shoulder |
| motor thickness | 2.1 mm | ISO 2768-f | pocket depth is larger by the gap, open point 3 |
| motor position | 49 deg | ISO 2768-m | from the top, thumb-side shoulder |
| least metal round the motor pocket | 0.40 mm | not a tolerance, a minimum | measured outward from every point of the pocket rim |
| charging pad hole diameter | 1.0 mm | ISO 2768-f | four through holes at -150 deg (finish: open point 4) |
| charging pad hole X positions | 0.8 mm | ISO 2768-f | the four holes at X = -2.4, -0.8, +0.8, +2.4 |
| glass face arc radius | 30.7 mm | ISO 2768-f | top of the block across the finger: the seat for the glass |
| glass face rise | 0.90 mm | ISO 2768-f | from the long edges to the centre line |
| side roll radius | 1.0 mm | ISO 2768-f | from the arc into the side walls |
| end roll radius | 1.2 mm | ISO 2768-f | the two ends of the block |

## Model values to confirm (not in the architecture, taken from the 3D model design/mech/thin/thin-notes.md, an older state than section 17.8)
Floor slots 2.6 x 0.6 at Y = +-5.9, X = -4.7 (two). Panel pocket = panel + 0.05 per side (27.45 x 12.9), corner radius 0.1. Mic slot Z = 0.96. These are the modeller's choices; the maker takes the STEP file for the final geometry once the parts helper has delivered it.

## What to inspect
First article, then each lot sample: overall block length, width, height at centre line and at the long edges; floor thickness at 3 points; band inner diameter with a ring gauge (plug) at the ring's size; band width; shoulder thickness at 40 and 60 deg; shell wall at the motor pocket rim and at the four screen corners (0.27 mm minimum; the corner is the hardest); mic slot size and position; pad hole positions; fit of a dummy glass (formed to 30.7 mm) in the seat; fit of a dummy panel 27.35 x 12.8 x 0.8 in the pocket; coating colour and adhesion; no burr at the mic slots and floor slots. Method and sampling plan: open point 5.

## Ring sizes
Inner diameter = 11.63 + 0.8128 x size (mech-notes.md line 7). One body per size; the block, glass seat and all pockets are identical across sizes, the band changes.

| US size | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|---|---|
| inner diameter, mm [CALC] | 15.69 | 16.51 | 17.32 | 18.13 | 18.95 | 19.76 | 20.57 | 21.38 | 22.20 |

Whether the shoulder angles stay the same at every size: open point 7 (the 3D model checks US 9 only).

## Files
Drawing: design/mfg/drawings/body.svg and body.pdf (US 9), and body-us7 to body-us13 (.svg and .pdf) for the other sizes (design/mfg/tools/draw.py). STEP and STL: design/mfg/parts/body/body-us9.step and .stl (also us7, us8, us10, us11, us12, us13), listed in design/mfg/parts/index.csv. Status in that index: outer shape only, cavities not cut; so the pockets, slots and openings of the table above are NOT in the STEP file yet. A reference with cavities: design/mfg/parts/body-cavity-reference/ (reference only, not a made part). Open: the parts helper must deliver the body with the cavities cut.

## Open points
1. Who machines the one-piece body, and can it be one piece: a ring maker or the design partner answers (S13).
2. Pocket clearance and depth for the screen panel (architecture 16.1 says 0.15 mm per side; the model uses 0.05): the design partner answers, then the maker confirms.
3. Clearance between the record cap, the motor and their openings: the design partner answers.
4. Coating thickness, roughness, masking at the glass seat and pad holes: the maker answers.
5. Tighter than ISO 2768-f anywhere, inspection method, sampling plan: the maker proposes, the design partner accepts.
6. Tolerance of the band inner diameter: the maker proposes.
7. Body variants for sizes other than US 9: the design partner (3D model) answers.
8. Block heights 3.85 and 2.95 (17.8) include the glass. The body's own seat heights are in the STEP file only: the parts helper answers. bom.csv line 53 still says block height 3.2 and an older stack.
9. The joystick opening of 5.0 mm diameter (17.3) was for the older cap and is replaced by the frame 6.4 x 5.4 (17.8); the frame's seat depth is open: the design partner answers.
10. Bench items B8 (resin closure, heat, floor-slot sealing) and B9 (joystick feel and sealing) can change the openings.

## Source lines
design/architecture.md lines 417, 418, 420, 424, 428-444 (17.1 to 17.3), 469-470 (S12, S13), 488-494 (17.8, wins over 17.7 at lines 478-482); design/bom.csv line 53; design/mech/mech-notes.md line 7; design/mech/thin/thin-notes.md.
