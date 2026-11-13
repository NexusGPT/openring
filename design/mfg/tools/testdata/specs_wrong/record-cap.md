# Specification: record cap (no bom.csv reference yet)

Design version A5, architecture section 17.8 (2026-11-10). All dimensions in mm.

## What it is
The pill-shaped push cap of the record button, on the side of the band at +88 degrees (thumb side), over one Alps SKTAAAE010 switch (SW2, 2.6 x 1.6 x 0.53). A long press of 1.0 s starts or stops a recording (architecture section 9).

## Quantity per ring
1 per ring.

## Material
Open: not stated in the architecture (16.5 says a silicone-backed insert bonded in its window, for the older design). The design partner and the maker answer (open point 1).

## Process
Open (open point 1).

## Finish and colour
Open (open point 2). Skin-contact grade: the maker states it.

## General tolerance and tighter tolerances
General: ISO 2768-m (default, to confirm with the maker). Tighter, ISO 2768-f, on the cap outline against its opening in the body (default, to confirm with the maker).

## Critical dimensions

| name | value | tolerance | where it is measured |
|---|---|---|---|
| cap, long side | 4.4 mm | ISO 2768-f | outline at the top face, along X |
| cap, short side | 2.4 mm | ISO 2768-f | outline at the top face, along the band |
| position round the band | 88 deg | ISO 2768-m | from the top, thumb side |
| switch size, long side | 2.6 mm | by the maker of the switch | SKTAAAE010 under the cap |
| switch size, short side | 1.6 mm | by the maker of the switch | SKTAAAE010 |
| switch height | 0.53 mm | by the maker of the switch | SKTAAAE010 |
| shell wall at the opening | 0.5 mm | ISO 2768-f | body wall |
| liner thickness under the switch | 0.3 mm | open point 3 | stack under the switch |
| long press time | 1.0 s | not a dimension | firmware, section 9 |

## What to inspect
Cap outline; cap height against the body surface (open point 3); cap to opening clearance; the cap closes the switch with no sticking at every edge of the cap; press force against the switch's 1.6 N; seal of the opening (like B9).

## Ring sizes
The same cap for all sizes (US 5 to 13).

## Files
Drawing: design/mfg/drawings/record-cap.svg and record-cap.pdf. STEP and STL: design/mfg/parts/record-cap/record-cap.step and .stl (index.csv: exterior shape only, placed at its US 9 position; bbox 4.4 x 0.7231 x 2.4109, so the views show it in its pose on the band).

## Open points
1. Material, process, skin-contact grade: the design partner with a moulding or ring maker.
2. Colour and finish: the design partner.
3. Cap height above the body and the flange: not stated for 17.8; the earlier model had a flange 0.8 mm wider than the pill and the top 0.2 mm proud (design/mech/thin/placement.csv, record_cap). The design partner confirms.
4. The cap stands on a body wall of the band at 88 degrees; the body's wall thickness there is that of the band (2.6 mm total), so the stack of 17.3 for the record switch (inside 2.6) has to be re-checked at 88 degrees: the design partner answers.

## Source lines
design/architecture.md line 227 (section 9 record button), 431, 438 (17.3); 490 (17.8, wins over 17.7 line 480); design/mech/thin/placement.csv (record_cap).
