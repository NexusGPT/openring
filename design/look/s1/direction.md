# Slim pilot

Thesis: a thin, flat, glossy black slab on a narrow dark metal band. One piece of black glass runs edge to edge over a metal body; the lit content floats in the black. No shoulders, no dome, no seams you can see, nothing decorative.

Outer size: 28.60 x 14.05 x 6.50 mm (check_exterior: [] against shared/envelope_slim.py).

## Dimensions (mm, from the brief)
- Block 28.6 x 14.05 x 6.5, plan corner radius 1.3, vertical walls, 0.6 fillet on the bottom perimeter edge.
- Glass 0.5 thick over the whole top face, top edge rounded 0.25. Joins the body with no gap and no step.
- Screen plate 21.6 x 10.8 x 0.02 at (1.475, 0). Lit area to edge: 1.625 sides, 2.025 fingertip end, 5.0 unlit strip at the other end.
- Band 4.6 wide, wall 1.5, inner diameter 18.95 (US size 9); block underside 0.3 above the finger.
- Joystick cap diameter 3.0, 0.5 proud, at X +6.0, Z 3.3. Button pill 4.0 x 1.5, 0.3 proud, at X -5.0, Z 3.3.
- Red light disc diameter 1.0 on the glass at X -12.0. Two mic slots 1.4 x 0.4, 0.3 deep, in the -Y wall at X -11 and +11, Z 4.6. Four gold pads diameter 1.2 flush on the underside at X -11.

## Worse at than a plain box
- One end keeps a 5 mm unlit strip: the screen's driver sits there.
- Lit area to edge: 1.6 mm at the sides, 2 mm at the fingertip end.
- Walls are 0.45 mm thick: metal only, machined.

## Chosen by the builder
- Joystick cap top edge rounding 0.2 mm.
- Mic mesh solid (mic_1, mic_2) 0.06 mm thick at the slot bottom; slot ends fully rounded.
- Contact pad thickness 0.1 mm, sunk into the underside so the pad face is flush at Z 0.
- Joystick and button start at the wall surface (no hidden stem).
- Band has plain square edges (no fillet); it is clipped flat at the block underside.
- Viewer: finger 18 mm diameter with its top 0.3 mm under the block; 10 mm scale line placed 10.5 mm in front of the block; screen picture drawn additively so the glass gloss shows through the black.
- Viewer text: the first trade-off is shortened to 12 words ("One end keeps a 5 mm unlit strip for the screen's driver.") and the second to 11 words so both fit the 12-word limit.

## questions_for_owner
none


## merged32 (default look from 2026-11-10)
Outer size: 29.30 x 14.75 x 3.20 mm (nominal block). Printed by `s1/exterior.py --variant merged32` (log s1/out/run_merged32d.log): the block above Z 0 measures X +-14.650, Y +-8.022 because the 4.0 mm junction blend runs out past the plate sides; the earlier 29.11 x 14.56 in the panel was only the bounding box of the top glass slice (above the 0.9 roll), not the block.
- Block: plan radius 2.5, top edge 0.9, bottom edge 1.2; glass = the top 0.5 mm of the same solid.
- Band: 8.0 wide, bore 18.95, wall 2.6, outer edges rounded 1.0, block underside 0.4 above the bore top. One fused body; concave junction blend radius 4.0 (reached on the first try, 12 junction edges), so the band outer surface sweeps into the plate's side walls.
- Vibration motor (7.0 x 2.1 coin, flat in the shoulders, no exported part, no mark): shoulders 3.1 mm thick out to 57 degrees from the top, easing to 2.6 by 70 degrees, both sides.
- Measured shoulder thickness at 38 degrees (X 0, -Y side, radial from the bore): 3.34 mm. Zone 19..57 degrees, X -3..3, both sides: min 3.105 mm. Out to X -4..4 (the band edge, inside the 1.0 edge rounding) the minimum is 2.105 mm. Thickness by angle (X 0, -Y): 0 deg 3.605, 19 deg 4.355, 38 deg 3.34, 57 deg 3.105, 63 deg 2.86, 70 deg 2.605, 80 deg and beyond 2.605.
- Chosen by the builder: the blend replaced the earlier 13 mm flare; the `band` part is a 0.4 mm cube hidden in the band wall and the fused solid is in `body`; pills start 0.15 inside the wall; slots 0.3 deep; pads 0.1 thick curved to the band surface.
- Controls on the band (thumb side, +Y shoulder), run log s1/out/run_merged32e.log: thumb stick at 38 degrees, X 0: cap 4.6 across, 0.7 proud, top edge rounded 0.2 (CHOSEN), 0.25 deep concave dish (sphere, 3.6 across), base ring 5.6 across, 0.15 proud, axis normal to the shoulder surface (normal measured from the surface: 0, 0.877, 0.480); shoulder radius there 12.815, thickness under it 3.340 mm. Record button: pill 5.0 along X x 3.0 along the arc, 0.4 proud, edge rounded 0.3, at 62 degrees, X 0. Plain band between stick base and button: 1.061 mm measured. The block's walls now carry only the two microphone slots. Both parts start 0.3 inside the surface so there is no gap.
- Not done: the dish is not more matte than the cap; it is one part with one material.

### Final shoulder numbers (run log s1/out/run_merged32f.log)
- Shoulders 3.6 mm thick from 19 to 61 degrees, easing to 2.6 by 85 degrees, both sides (motor at -49 degrees inside, no mark). Band outer edge rounding 0.4 mm in that zone, easing to 1.0 by 85 degrees (variable-radius fillet, built, valid). Junction blend radius 4.0 reached again (13 junction edges).
- Measured shoulder thickness at 38 degrees (X 0, -Y side): 3.72 mm; under the stick (+Y side): 3.715 mm. By angle (X 0): 0 deg 3.605, 19 deg 4.355, 38 deg 3.72, 61 deg 3.605, 70 deg 3.2, 85 deg 2.605.
- Minimum over X -3.6..3.6, 19 to 61 degrees, both sides: 3.240 mm, NOT 3.6 (the thinnest points are at the X edges, inside the 0.4 rounding); to X -4..4 the minimum is 2.420 mm. So the 3.6 holds along the centre line but not out to X +-3.6.
- Stick at 38 degrees: surface radius 13.190, normal (0, 0.807, 0.591); button at 62 degrees: surface radius 13.070; plain band between stick base and button: 1.133 mm. Block bbox above Z 0: Y -8.606..9.100 (the shoulders are thicker, so the blend runs further out).
- The earlier 'dimple' and 'knuckle' are not visible in the from-below and side shots after this build; the soft lit blend face stays.

## merged32b (default from 2026-11-10): curved glass, controls on the side of the band
Built by `s1/exterior.py --variant merged32b` (run log s1/out/run_merged32b_g.log, triangles s1/out/tris_merged32b.log: 299,771; file 7.1 MB, finer tessellation than the other variants).
- Block: plan 29.3 x 14.75, plan radius 2.5; top flat at Z 3.45 between Y +-5.375, quarter-round radius 2.0 down both long sides to Z 1.45, end rolls 1.2, bottom roll 1.2; glass = everything above Z 2.75 (0.70 thick at the centre). Printed block bounding box above Z 0: X +-14.650, Y +-8.570 (the 4.0 blend runs past the plate), Z 0..3.450; whole model Y -12.075..13.075, Z -21.950..3.450.
- Band: 8.0 wide, wall 2.6, 3.6 thick over the shoulders (19 to 61 degrees, easing to 2.6 by 85) and over the thumb zone (80 to 110 degrees on the +Y side only, easing over 12 degrees each way). Measured at 95 degrees (X 0, +Y): 3.605 mm. Shoulders at 38 degrees: 3.605 mm on both sides. Junction blend 4.0 reached.
- joystick at 95 degrees on the +Y side: frame 6.4 along the arc x 5.4 along X, corner radius 1.2, 0.5 proud; nub 4.6 x 3.6, corner radius 1.0, 0.9 proud of the frame, 0.15 dome (nub 4.6 taken along the arc, 3.6 along X: my reading). Record button at 62 degrees: pill 4.4 x 2.4, 0.35 proud, 0.3 edge; 3.103 mm of plain band between it and the joystick frame. Nothing on the shoulder.
- Deviations (CHOSEN by the builder): (1) band edge rounding is 0.4 everywhere, not 0.4 in the zone and 1.0 elsewhere: a 0.4 to 1.0 variable rounding gives an invalid solid on this outline. (2) Mic slots at Z 1.4 (wall is only Z 1.2..1.45 tall now). (3) The sampled band outline spline has no end tangents (explicit tangents made a cusp that broke the fillet). (4) Nub dimensions: 4.6 along the arc.
- Shoulder thickness over X +-3.6 was not re-measured for this variant (the measurement was dropped to keep the run short); the merged32 value (min 3.240) does not carry over.
- Not done: the long soft highlight on the rolled long edges is weak. In the three-quarter shot it shows as a thin light line along the front roll and a gloss on the band; the side view shows the rolled bar profile clearly.

## merged32c (default from 2026-11-10): the whole glass face is one arc, joystick at the bottom of the band
Built by `s1/exterior.py --variant merged32c` (run log s1/out/run_merged32c_a.log; triangles s1/out/tris_merged32c.log: 201,479, 4.9 MB).
- Glass face: one arc across Y of radius 30.7 (top Z 3.85 on the centre line, Z 2.95 at Y +-7.375), roll 1.0 into the side wall, ends rolled 1.2, bottom roll 1.2, plan 29.3 x 14.75 radius 2.5; straight along X. glass = everything above Z 2.75, body = the rest. Lit screen plate = a 0.02 thick shell on the same arc (21.6 x 10.8); the viewer bends the textured picture with the same radius. Light disc at X -12 on the centre line.
- Band: 8.0 wide, wall 2.6; 3.6 thick at the shoulders (19 to 61 degrees, easing to 2.6 by 85, both sides) and at 135 to 165 degrees on the +Y side (easing over 12 degrees each way). Junction blend 4.0 reached. Band edge rounding 0.4 everywhere (as merged32b).
- joystick at 150 degrees on +Y (bottom of the band, toward the thumb): frame 6.4 x 5.4 radius 1.2, 0.5 proud; nub 4.6 x 3.6 radius 1.0, 0.9 proud of the frame, 0.15 dome. Measured band thickness at 150 degrees: 3.605 mm. Record button at 88 degrees on +Y: pill 4.4 x 2.4, 0.35 proud; 9.076 mm of plain band to the joystick frame. Contacts: four pads (X -2.4, -0.8, 0.8, 2.4) on the -Y side at 150 degrees, flush; plain wall there 2.605 mm.
- Printed: shoulder thickness at 38 degrees +Y 3.775, -Y 3.810 mm. Block bounding box above Z 0 as printed: Y -9.479..9.414, Z -0.869..3.850 (the Z minimum below 0 comes from the blend and is not a real block dimension; the printed value is reported as is). Whole model Z -22.537..3.850 (the joystick stands below the band's lowest point).
- Chosen by the builder: mic slots at Z 1.4; nub 4.6 along the arc; the screen shell is the part `screen` (curved), not a flat plate.
- Not done: the face shows no clear single long highlight bending across the arc; the side shot shows the arc, the three-quarter shot shows a soft gradient only.

