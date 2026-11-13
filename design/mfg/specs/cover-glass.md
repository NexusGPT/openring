# Specification: cover glass, reference GL1

Design version A5, architecture section 17.8 (2026-11-10), refreshed to the inside model v5 (architecture 17.23, 17.24) and to design version 7 (architecture 17.30, 2026-11-11: the recording light is removed in v7). All dimensions in mm.

## What it is
The formed cover glass over the whole top face of the block. The face is one arc across the finger, rolled into the side walls and at the two ends. The screen under it stays flat. The glass is bonded to the screen panel by 0.1 mm clear adhesive (ADH1, tesa 69404, optically clear, 100 um, haze under 0.5 percent) over the whole face, so no air gap shows the edge of the lit area (17.30). It is also sealed to the body's glass seat all round by a perimeter seal ring SEAL1, 0.05 thick (Z 2.70 to 2.75), in a seat lowered 0.05 inside the body (model v5; assembly.md step 23, conflict K-A4; architecture 17.23, 17.24). SEAL1 is a ring of tesa 61305 double-sided film, 50 um (bond to glass 12.4 N/cm); its sheet states no value for coated titanium and none for water: on the first body a bond check after 24 hours, then a water spray test; version 1 claims no water rating (item 110). Black print everywhere outside the lit area, with no opening of any kind in the print. History: the 0.4 mm print window for the recording light (17.21) is removed in v7 (17.30); the ring's recording sign is drawn on the screen by the firmware.

## Quantity per ring
1 per ring. The same glass for all ring sizes.

## Material
AGC Dragontrail Pro, chemically strengthened (surface stress 1000 MPa, depth 40 um), density 2.46: the glass weighs 0.82 g (332.87 cubic mm). Reason: thin formed glass that can be strengthened. Its sheet gives no thickness range and no forming limit (open point 2). The ring's weight is measured on the first unit, part by part, on a 0.01 g balance (items 107 to 109).

## Process
Default, to confirm with the maker: formed (hot-bent) to the arc and rolls, then chemically strengthened, then printed. Whether a maker can form an arc of 30.7 mm with 1.0 mm and 1.2 mm rolls at 1.10 mm thickness, and the forming tolerance: open point 2; it is shown only by the first formed sample (thickness at 5 points with a micrometer, radius with a gauge; items 107 to 109).

## Finish and colour
Outer surface: clear, polished. Black print outside the lit area on the inner face (so the print is under the glass), continuous, with no opening. The print is the same black as the screen panel when it is off (17.30). Print opacity, ink and any coating (anti-fingerprint): open point 3.

## General tolerance and tighter tolerances
General: ISO 2768-m (default, to confirm with the maker). Tighter: ISO 2768-f on the glass seat in the body (specs/body.md); the glass outline's own limits: open point 2.

## Critical dimensions
Values from architecture.md section 17.1 and 17.8.

| name | value | tolerance | where it is measured |
|---|---|---|---|
| glass thickness at the centre | 1.10 mm | open point 2 | centre line, at the middle of the lit area |
| glass thickness over the screen edge | 0.42 mm | open point 2 | over the edge of the screen panel |
| face arc radius | 30.7 mm | open point 2 | across the finger, outer surface |
| rise from the long edges to the centre line | 0.90 mm | open point 2 | outer surface, across the finger |
| side roll radius | 1.0 mm | open point 2 | from the arc into the side walls |
| end roll radius | 1.2 mm | open point 2 | the two ends |
| block height at the centre line (glass on body) | 3.85 mm | ISO 2768-m | assembled, from the underside |
| block height at the long edges | 2.95 mm | ISO 2768-m | assembled |
| lit area, along the finger | 21.6 mm | ISO 2768-f | the unprinted window |
| lit area, across | 10.8 mm | ISO 2768-f | the unprinted window |
| print border to block edge, long side | 1.98 mm | ISO 2768-f | window edge to block edge, each long side |
| print border, fingertip end | 2.38 mm | ISO 2768-f | window edge to block edge |
| print border, hand end | 5.33 mm | ISO 2768-f | window edge to block edge |
| openings in the black print | 0 (none) | not a dimension | the print is continuous outside the lit area; the light window of 17.21 is removed in v7 (17.30) |
| clear adhesive ADH1 | 0.10 mm | open point 2 | glass to screen panel over the whole face (17.2, 17.30); tesa 69404, 100 um (item 96, rest) |
| glass seal ring SEAL1 | 0.05 mm thick | open | tesa 61305 film, 50 um (item 110); perimeter ring between the glass underside and the body seat, Z 2.70 to 2.75; the seat is lowered 0.05 mm in the body; the glass and the outer shape do not change |
| glass plan outline | 29.2958 x 14.429 mm | open point 2 | the box of design/mfg/parts/cover-glass/cover-glass.step, cut from the accepted exterior (open point 5) |
| block plan corner radius | 2.5 mm | ISO 2768-m | plan view of the block corner; the glass outline above follows it |

## What to inspect
Thickness at the centre and at 4 positions near the edges; arc radius with a template or scan; roll radii; overall plan size; lit area size and position against the edges; print opacity (no light through the black, checked over the whole printed border with a lit backlight: no pinhole and no opening); print colour against the screen panel when off (17.30); strengthening depth and surface stress (maker's report); chips and scratches on the outer face; no distortion of the lit area (look at a lit screen through the glass).

## Ring sizes
One glass for all sizes (US 7 to 13): the block does not change with the size (architecture 17.1).

## Files
Drawing: design/mfg/drawings/cover-glass.svg and cover-glass.pdf. STEP only: design/mfg/parts/cover-glass/cover-glass.step (no STL exists for the glass; index.csv: the exterior's formed glass, same for all sizes, cut from the accepted exterior merged32h; bbox 29.2958 x 14.429 x 1.1; the drawn outline is 14.38 across, 0.05 less than the box, the dimension number on the drawing is the box). The one plan outline of the glass is this file's box, 29.2958 x 14.429 mm (open point 5).

## Open points
1. Glass: AGC Dragontrail Pro, chemically strengthened, surface stress 1000 MPa, depth 40 um (items 107 to 109); the glass former (a maker that can form it) is still to be found.
2. Formability and forming tolerances for the arc, the rolls, the thickness: the glass maker answers. bom.csv line 52 gives the thickness 1.10 mm at the centre, as this page does (the older line 54 and its 0.4 are not the glass any more).
3. Print ink, opacity, any surface coating: the glass maker with the design partner.
4. Seal: tesa 61305, 50 um (item 110); whether it holds on coated titanium and against water is measured on the first body. (Before v7 this point also held the recording light window; removed in v7, 17.30.)
5. Glass plan outline: fixed to the box of the maker file, 29.2958 x 14.429 mm, from design/mfg/parts/cover-glass/cover-glass.step (cut from the accepted exterior merged32h; index.csv row cover-glass). The parts list (design/bom.csv line 52) and the inside model's placement file (row cover_glass, 29.296 x 14.429) give the same outline since 2026-11-12; the older values 29.3 x 14.75 (the block's size) and 29.1 x 14.56 (a stale size note of the model) are gone.
6. Edge finish of the cut edges (the first drawing said edge rounded 0.25 mm in section 16.1, for the older flat glass): the design partner answers.
7. No glass maker is named in any source: the design partner chooses whom to ask.

## Source lines
design/architecture.md lines 417, 419 (17.1), 488 (17.8, wins over 17.7 line 478); 17.23 and 17.24 (seal); 17.30 (the recording light is removed in v7, print with no opening, ADH1 over the whole face); design/architecture.md line 315 (16.1, lit area 10.8 x 21.6); design/bom.csv line 52; design/mfg/parts/index.csv (row cover-glass); design/mech/thin/placement.csv (cover_glass).
