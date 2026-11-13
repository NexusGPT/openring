# Specification: cover glass, reference GL1

Design version A5, architecture section 17.8 (2026-11-10). All dimensions in mm.

## What it is
The formed cover glass over the whole top face of the block. The face is one arc across the finger, rolled into the side walls and at the two ends. The screen under it stays flat. The glass is bonded to the screen panel by 0.1 mm clear adhesive (ADH1). Black print everywhere outside the lit area.

## Quantity per ring
1 per ring. The same glass for all ring sizes.

## Material
Default, to confirm with the maker: chemically strengthened aluminosilicate glass. Reason: thin formed glass that can be strengthened. Brand, grade and the strengthening depth and surface stress: open point 1.

## Process
Default, to confirm with the maker: formed (hot-bent) to the arc and rolls, then chemically strengthened, then printed. Whether one can form an arc of 30.7 mm with 1.0 mm and 1.2 mm rolls at 1.10 mm thickness, and the forming tolerance: open point 2.

## Finish and colour
Outer surface: clear, polished. Black print outside the lit area on the inner face (so the print is under the glass). Print opacity, ink and any coating (anti-fingerprint): open point 3.

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
| block plan corner radius | 2.5 mm | ISO 2768-m | glass plan outline follows the body corner (open point 4) |

## What to inspect
Thickness at the centre and at 4 positions near the edges; arc radius with a template or scan; roll radii; overall plan size; print window size and position against the edges; print opacity (no light through the black); strengthening depth and surface stress (maker's report); chips and scratches on the outer face; no distortion of the lit area (look at a lit screen through the glass).

## Ring sizes
One glass for all sizes (US 5 to 13): the block does not change with the size (architecture 17.1).

## Files
Drawing: design/mfg/drawings/cover-glass.svg and cover-glass.pdf. STEP and STL: design/mfg/parts/cover-glass/cover-glass.step and .stl (index.csv: exterior shape only, same for all sizes; bbox 29.2958 x 14.429 x 1.1; the drawn outline is 14.38 across, 0.05 less than the box, the dimension number on the drawing is the box).

## Open points
1. Glass brand and grade, strengthening depth and stress: the glass maker proposes.
2. Formability and forming tolerances for the arc, the rolls, the thickness: the glass maker answers. bom.csv line 54 still gives 29.3 x 14.75 x 0.4 (old state); this page follows 17.8.
3. Print ink, opacity, any surface coating: the glass maker with the design partner.
4. Glass plan outline: the architecture gives none for 17.8; the earlier 3D model had 29.1 x 14.56 (design/mech/thin/placement.csv, cover_glass). The design partner answers; until then the glass follows the block outline.
5. Edge finish of the cut edges (the first drawing said edge rounded 0.25 mm in section 16.1, for the older flat glass): the design partner answers.
6. No glass maker is named in any source: the design partner chooses whom to ask.

## Source lines
design/architecture.md lines 417, 419 (17.1), 488 (17.8, wins over 17.7 line 478); design/architecture.md line 315 (16.1, lit area 10.8 x 21.6); design/bom.csv line 54; design/mech/thin/placement.csv (cover_glass).
