# Specification: joystick cap CAP1 and frame FRM1 (design/bom.csv lines 81 and 82, design/mfg/part-map.csv)

Design version 7 (2026-11-11): architecture 17.29 (round joystick, gloss black finish) and 17.30, on the exterior merged32h (`design/look/s1/merged32h-report.md`, all seven sizes `RESULT PASS`). Pocket, dam DAM1, stiffener and switch cross are unchanged from the inside model v6.3 (`design/mech/thin/thin-notes.md` sections "Model v6" to "Model v6.3"). The file keeps its old name joystick-nub.md; the rectangular nub of version 6 and earlier is removed in v7 and replaced by the round cap CAP1. All dimensions in mm. "Along the finger" is X; "around the band" is the direction of the band's curve.

## What it is
The one control of the ring: a round cap CAP1 that tilts and presses, guided by a fixed round frame FRM1 bonded in a round opening of the body. Both sit on the joystick side of the band (minus side, toward the thumb on a ring worn on the right index finger) at -84.0 deg on US 7, -81.0 deg on US 8 and -78.0 deg on US 9 to 13 (17.25). Axis of cap and frame: on the radial line at the joystick angle, through the wall.
- Under the cap five Alps SKTAAAE010 switches (2.6 x 1.6 x 0.53 each) sit in a cross at 2.4 mm from the cap axis: SW1 up, SW3 down, SW4 toward the hand, SW5 toward the fingertip, SW2 in the centre (17.15).
- A press on the centre closes SW2. A long press of 1.0 s on the centre starts a recording, a second long press of 1.0 s stops it (17.11). The ring has no record button.
- The recording is shown on the screen by the firmware (17.30); no part of this page carries a light.
- CAP1 is one moulded part: round shank and its flange, with no joint between them. (Its maker file writes it as two touching solids, shank and flange; that is the file's way of drawing one part: see Files.) FRM1 is a separate machined part, coated with the body and bonded in the opening.

## Quantity per ring
1 cap CAP1 and 1 frame FRM1 per ring. The same CAP1 and the same FRM1 at every ring size. The five switches are bought parts (bom.csv lines 39 and 40), not specified here.

## Material
- CAP1: Covestro Makrolon 2407, colour 901510 (black polycarbonate).
- FRM1: titanium grade 5, Ti-6Al-4V (the body's material, 17.29).
- Bond of FRM1 in the body: 3M Scotch-Weld Epoxy Adhesive DP420 Black (two-part epoxy, mix ratio 2:1 by volume, 3M technical data sheet, revision June 2024, page 1).

## Process
- CAP1: injection moulding in one shot, flange and shank together. Gate on the flange underside (the face toward the bore), so no gate mark is on the shank or the top face.
- FRM1: CNC turning from Ti-6Al-4V bar, in one setup for the outer diameter and the bore (concentric). Then polished, then coated with the body's gloss black coating in the same coating batch as the body HSG1 (17.29; specs/body.md).
- FRM1 into the body: bonded with DP420 Black, 0.10 mm radial gap, cured 24 h at 22 C before the cap goes in (assembly.md step 13; 3M data sheet page 3, 4,500 psi overlap shear on aluminium after 24 h at 22 C).

## Finish and colour
- CAP1: gloss black. Mould finish SPI A-2 on every face except the top face. Top face (dish and ridges): VDI 3400 Ref 21 (matt texture for grip).
- FRM1: polished, then the body's gloss black coating, all faces (17.29).
- No bare metal and no light part shows at the joystick.

## General tolerance and tighter tolerances
- ISO 2768-f on: the cap diameter 4.40, the frame outer diameter 5.40, the frame bore 4.80.
- ISO 2768-m on every other dimension of CAP1 and FRM1 of 0.5 mm and more.
- ISO 2768-1 gives no general tolerance below 0.5 mm. For those features this page sets: ridge height 0.08 +-0.02; ridge width 0.25 +-0.05; dish depth 0.25 +-0.05; top edge radius 0.30 +-0.05; flange thickness 0.40 +-0.05; frame top above the band surface 0.50 +-0.05 (fixed by the lead for v7, because ISO 2768-1 is silent under 0.5 mm).
- Fit stack [CALC, worst case]: cap 4.40 +-0.05 in bore 4.80 +-0.05 leaves 0.15 to 0.25 radial clearance. Frame 5.40 +-0.05 in the body opening 5.60 +-0.05 (body.md, ISO 2768-f) leaves a glue gap of 0.05 to 0.15 radial.

## Critical dimensions

| name | value | tolerance | where it is measured |
|---|---|---|---|
| body opening diameter | 5.60 mm | ISO 2768-f | round, through the band wall, axis on the radial line at the joystick angle (body.md) |
| position round the band | -78 deg (US 9 to 13); -81.0 (US 8); -84.0 (US 7) | ISO 2768-m | angle of the cap and frame axis from the top; minus is the joystick side (17.25) |
| frame FRM1 outer diameter | 5.40 mm | ISO 2768-f | turned outer face |
| frame FRM1 bore | 4.80 mm | ISO 2768-f | turned bore, concentric with the outer face |
| frame FRM1 length | 1.30 mm | ISO 2768-m | along its axis: 0.80 under the band surface to 0.50 above it |
| frame top above the band surface | 0.50 mm | see the list above | on the X lines (merged32h-report: 0.500 to 0.501) |
| frame glue gap | 0.10 mm | from the two ISO 2768-f diameters | radial, frame to opening, filled with DP420 Black |
| cap CAP1 shank diameter | 4.40 mm | ISO 2768-f | round shank, from the flange top up to the top face |
| cap radial clearance to the frame bore | 0.20 mm | from the two ISO 2768-f diameters | radial, cap shank to frame bore (4.80 - 4.40) / 2 |
| cap rim above the frame top | 1.400 mm | ISO 2768-m | along the axis, at the cap rim (merged32h-report, all sizes) |
| top edge radius | 0.30 mm | see the list above | round the top of the shank |
| dish depth | 0.25 mm | see the list above | spherical dish in the top face, sphere radius 7.345, dish rim at radius 1.90 from the axis |
| ridge radii | 0.70, 1.30, 1.90 mm | ISO 2768-m | three concentric ridges, centre line of each ridge from the axis (merged32h-report: 0.700, 1.300, 1.900 on every size) |
| ridge width | 0.25 mm | see the list above | each ridge, radial width |
| ridge height | 0.08 mm | see the list above | each ridge raised over the dish surface, following the dish; the outer ridge is the highest point of the cap, 1.480 above the frame top (merged32h-report) |
| flange along the finger | 6.90 mm | +0.00 / -0.10 | moulded flange at the bore end of the cap; one-sided so it always enters the 7.0 pocket (7.0 ISO 2768-f is 6.90 at least): flange 6.80 to 6.90 |
| flange around the band | 6.40 mm | ISO 2768-m (+-0.1) | same flange; 6.8 pocket |
| flange thickness | 0.40 mm | see the list above | same flange |
| flange corner radius | 1.0 mm | ISO 2768-m | four corners of the flange in plan |
| body pocket under the flange | 7.0 mm along X by 6.8 mm around the band | ISO 2768-f | from the bore up to a flat roof; the roof is 0.05 above the flange top; roof radius per size in body.md (10.0898 on US 7 to 12.5282 on US 13); unchanged from model v6.3 |
| switch cross radius | 2.4 mm | ISO 2768-f | cap axis to each of the four direction switch centres; SW2 on the axis, 0.30 mm to its neighbours |
| cap to the dome of SW2 | 0.15 mm | by the model | travel before the centre press closes SW2 (model v6.3) |
| stiffener under the switch head | 6.4 x 6.4 x 0.075 mm | by the flex maker | flat stiffener under the FLEX1 head, the liner filling under it; unchanged from model v6.3 (band-flex-tails.md) |
| switch size | 2.6 x 1.6 x 0.53 mm | by the maker of the switch | SKTAAAE010 |
| metal round the opening, X sides | 1.067 mm | not a tolerance, a minimum (rule 0.50) | 0.1 mm under the surface, every size (merged32h-report) |
| metal round the opening, toward the bottom | 1.094 (US 7) to 1.592 (US 13) mm | not a tolerance, a minimum (rule 0.50) | 0.1 mm under the surface; per size in body.md (merged32h-report) |

## What to inspect
CAP1, first article and each lot sample:
- shank diameter 4.40 (ISO 2768-f) at two heights, with a micrometer or an optical comparator;
- flange 6.90 x 6.40 x 0.40 and its 1.0 corner radius; the flange passes the pocket go gauge of 6.95 mm (assembly.md step 10);
- dish depth 0.25, ridge radii 0.70, 1.30, 1.90, ridge width 0.25 and height 0.08, measured by a profile scan across the top face;
- the outer ridge (highest point) stands 0.080 above the cap rim, so 1.480 above the frame top once fitted;
- colour 901510 against the Covestro colour chip; gloss A-2 on the shank and flange; Ref 21 texture on the top face; no flash, no sink, no gate mark outside the flange underside;
- material certificate of the lot (Makrolon 2407, colour 901510).
FRM1, first article and each lot sample:
- outer diameter 5.40 and bore 4.80 (ISO 2768-f), concentric; length 1.30;
- coating colour, gloss and adhesion, the same acceptance as the body (body.md);
- material certificate (Ti-6Al-4V).
After fitting (assembly.md step 13):
- frame top 0.50 above the band surface; DP420 bead closed all round with no glue in the bore;
- cap rim 1.400 above the frame top; the cap moves freely in the bore with no contact in any tilt;
- each of SW1, SW3, SW4, SW5 closes when the cap tilts toward it, SW2 closes on a centre press, and no other switch closes (feel test and ohmmeter, step 18);
- actuation force per direction against the switch's 1.6 N and 0.11 mm travel.

## Ring sizes
The same CAP1 and the same FRM1 at all sizes, US 7 to 13. Only the angle of the opening and of the pocket changes with the size: -84.0 deg on US 7, -81.0 on US 8, -78.0 on US 9 to 13 (17.25). The metal toward the bottom of the opening is 1.094 on US 7 and US 8, 1.097 on US 9, 1.219, 1.344, 1.467 and 1.592 on US 10 to 13 (merged32h-report).

## Files
- Exterior shape of cap and frame: the exterior merged32h, design/look/s1/out/ (merged32h-report.md).
- Maker files (inside model v7): design/mfg/parts/joystick-cap/joystick-cap.step and .stl (CAP1 with its flange; the file holds two solids, the shank and the flange, 78.7324 cubic mm together, and they are ONE moulded part with no joint, no parting line and no weld: the shank's lower end face, a disc of diameter 4.40, lies on the flange's top face, at the plane where the model starts the shank (thin.py: the shank from the flange top up, the flange 0.40 down from it). Make CAP1 as one piece. Work still to do on the file: write the cap as one solid, `parts-notes.md`, section Maker-file work still to do) and design/mfg/parts/joystick-frame/joystick-frame.step and .stl (FRM1), both placed at the US 9 position (-78 deg); index.csv rows. The version 6 files (rectangular nub, removed in v7) are kept in design/mfg/parts/old_v63/ for history only: do not make anything from them.
- Drawings: design/mfg/drawings/joystick-cap.svg and .pdf, joystick-frame.svg and .pdf (v7).

## Open points
Points 1 to 5 of the version 6 page are answered in v7:
1. Material and process: fixed. CAP1 in Makrolon 2407 colour 901510 by injection moulding; FRM1 in Ti-6Al-4V by CNC turning.
2. Frame part or machined in the body: fixed. FRM1 is a separate part, bonded with DP420 Black, 0.10 radial gap.
3. Colour and finish: fixed. CAP1 SPI A-2 gloss black, top face VDI 3400 Ref 21; FRM1 polished and coated gloss black with the body.
4. Height above the frame: fixed. Cap rim 1.400 above the frame top, highest point 1.480; frame top 0.50 above the band surface.
5. Shape under the cap per size: fixed. One cap for all sizes; the cap is round, so its shape does not follow the band's curve.
Still open, outside the parts on this page:
6. Bench items B6 (centre press) and B9 (feel, sealing, wear of the coating) can change this part.
7. The joystick opening relies on the switches' own rating (IP6X and IPX7) and the dam DAM1 for water; dam material and the stiffener material are open item S26 (assembly.md section 5).
8. Answered by the inside model v7 (design/mech/thin/thin-notes.md section "Model v7"): CAP1 is 4.517 mm from the flange underside to the rim plane (flange 0.40 plus shank 4.117 at US 9; 4.110 to 4.118 over the seven size builds, the spread is the model's 0.01 surface probe step), 4.597 to the top of the outer ridge. The frame's bottom stands 1.365 mm above the pocket roof at US 9 (frame bottom r 12.270, roof r 10.905); the opening's wall between them is body metal round the 5.6 hole.

## Source lines
design/architecture.md 17.11 (one control, long press 1.0 s), 17.15 (cross 2.4), 17.24 and 17.26 (flange, roof, stiffener), 17.25 (angle per size), 17.29 (round joystick, finish), 17.30 (the recording light is removed in v7); design/look/s1/merged32h-report.md (opening, frame, cap and metal figures); design/bom.csv lines 39, 40, 81, 82; design/mech/thin/thin-notes.md sections "Model v6" to "Model v6.3"; 3M Scotch-Weld Epoxy Adhesive DP420 Black technical data sheet, revision June 2024, pages 1 and 3.
