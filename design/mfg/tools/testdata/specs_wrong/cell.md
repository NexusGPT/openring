# Specification: curved cell with its protection circuit, references BT1 and PRT1

Design version A5, architecture section 17.8 (2026-11-10). All dimensions in mm. Custom part from Grepow (custom order); no order code exists.

## What it is
A thin rechargeable cell bent to follow the band: 1.6 mm thick, 6.0 mm wide, 36.4 mm long on its centre line at ring size US 9 (centre-line radius 10.58 mm, 197 degrees of arc, from -30 degrees through the bottom to +133 degrees from the top, plus is the thumb side). A protection circuit of 1.5 x 5 mm sits on the cell's tab at its end near -28 degrees. A temperature sensor line goes with the cell (one line on FLEX2).

## Quantity per ring
1 cell and 1 protection circuit per ring.

## Material
Open: cell chemistry and format are not stated beyond "4.35 V type" (architecture section 2). Grepow answers (open point 1).

## Process
Custom curved cell: Grepow answers whether it can build the arc at this thickness (S12). Forming, formation cycle and any safety test: open point 1.

## Finish and colour
Not applicable to a part inside the band; wrap and tab finish: open point 1.

## General tolerance and tighter tolerances
General: ISO 2768-m for size (default, to confirm with the maker), but a cell maker's own thickness tolerance rules, and the swelling room is a design item (0.2 mm gap, below). The tolerance on thickness is critical: the stack in the band has 2.6 mm in all (liner 0.3, cell 1.6, gap 0.2, shell 0.5). Tolerances: open point 2.

## Critical dimensions

| name | value | tolerance | where it is measured |
|---|---|---|---|
| cell thickness | 1.67 mm | open point 2 | radial, over the whole cell, after charge |
| cell width | 6.0 mm | open point 2 | across the band, along X |
| cell length on its centre line, US 9 | 36.4 mm | open point 2 | along the arc, at the middle of the thickness |
| centre-line radius, US 9 | 10.58 mm | open point 2 | bend radius of the centre line |
| arc angle | 197 deg | open point 2 | from the start to the end of the cell |
| start angle | -30 deg | ISO 2768-m | end near the protection circuit, from the top |
| end angle | 133 deg | ISO 2768-m | end near the joystick, from the top |
| protection circuit, along the arc | 1.5 mm | open point 2 | on the cell's tab |
| protection circuit, across | 5 mm | open point 2 | same |
| gap, cell to shell | 0.2 mm | design value | radial, swelling room |
| liner over the cell | 0.3 mm | design value | radial, finger side |
| charge voltage | 4.35 V | Grepow | full-charge voltage |
| capacity, lowest | 19 mAh | Grepow | at the volume 349 cubic mm [CALC] |
| capacity, highest | 25 mAh | Grepow | same |
| least charge current of the charger | 32 mA | not a dimension | power chip's lowest setting; above 1 C for this cell |

## What to inspect
Dimensions after bending: thickness at 5 points, width, length, radius with a gauge at ring size; capacity at the stated rate; open-circuit voltage; protection circuit limits (overvoltage, overcurrent, undervoltage) against the maker's datasheet; swelling after the first full charges (thickness growth against the 0.2 mm gap); insulation resistance; tab strength; temperature sensor value; lot number. Safety test report: open point 1.

## Ring sizes
The arc length scales with the diameter (17.3): the centre line radius is half the inner diameter plus 0.3 liner plus 0.8 (half the cell), so the values for US 5 to 13 are in the table below [CALC]. The same angle (197 degrees) is kept: this is an assumption of this page, the design partner confirms (open point 3).

| US size | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 |
|---|---|---|---|---|---|---|---|---|---|
| centre-line radius, mm [CALC] | 8.95 | 9.36 | 9.76 | 10.16 | 10.58 | 10.98 | 11.38 | 11.79 | 12.20 |
| length on the centre line, mm [CALC] | 30.8 | 32.2 | 33.6 | 35.0 | 36.4 | 37.8 | 39.1 | 40.5 | 41.9 |

## Files
Drawing: design/mfg/drawings/cell.svg and cell.pdf. STEP and STL: design/mfg/parts/cell/cell.step and .stl (index.csv: pouch body only, tabs and tape not exported; bbox 6.0 x 21.73 x 11.05, an older arc of the 3D model, not the 197 degrees of 17.8: open point 3 and the parts helper).

## Open points
1. Cell chemistry, format, order code, price, whether a 1.6 x 6.0 x 36.4 mm arc can be built at 4.35 V, protection circuit part code and its limits, safety test reports: Grepow (S12, bom.csv lines 49 and 50).
2. Tolerances of thickness, width, length, radius: Grepow.
3. Cell length at other sizes: the design partner confirms the constant 197 degrees.
4. The highest charge current the cell accepts: Grepow; the power chip cannot charge below 32 mA (S12), a second charger part may be needed (Nordic).
5. Where the temperature sensor sits and its type: Grepow and the electronics designer.
6. Capacity 19 to 25 mAh is a calculation from volume (0.054 to 0.072 mAh per cubic mm), not a maker figure. bom.csv lines 49 and 50 still state 1.6 x 6.0 x 38 and 206 degrees (older, 17.3).

## Source lines
design/architecture.md lines 433, 434, 437 (17.3), 469 (S12), 492 (17.8, wins over 17.7 line 482 and 17.3); design/bom.csv lines 49, 50.
