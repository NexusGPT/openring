# Specification: curved cell with its protection circuit, references BT1 and PRT1

Design version A5, architecture section 17.8 (2026-11-10), refreshed to the inside model v6.2 (architecture 17.22, 17.25, 17.26, 17.27). All dimensions in mm. Axes: X along the finger, Y across; -Y is the joystick side (17.11). Angles are from the top of the band; minus is the joystick side. Custom part from Grepow (custom order); no order code exists.

## What it is
A thin rechargeable cell bent to follow the band: 1.6 mm thick, 6.0 mm wide, 33.936 mm (US 7) to 46.121 mm (US 13) long on its centre line, 39.175 mm at US 9 (centre-line radius 10.5726 mm at US 9; arc 212.301 degrees at US 9, from +48.713 degrees through the bottom to -98.986 degrees). Start and end angle, length and capacity per ring size are in the table "Ring sizes" below (architecture 17.26, measured in the inside model v6). The cell has a 2.0 mm sealed edge and its two tabs at the +Y end. A protection circuit of 1.5 x 5 mm sits on the cell's tab, before the cell's start (at US 9 from +39.5 to +47.6 degrees, 0.2 mm before the cell). A temperature sensor line goes with the cell (one line on FLEX2). Before v5 this page gave 28.4 mm, an arc from -39 to +167 degrees and 15 to 20 mAh (architecture 17.10, replaced by 17.15 and 17.26).

## Quantity per ring
1 cell and 1 protection circuit per ring, one cell length per ring size (7 sizes, US 7 to 13).

## Material
Open: cell chemistry and format are not stated beyond "4.35 V type" (architecture section 2). Grepow answers (open point 1).

## Process
Custom curved cell: Grepow answers whether it can build the arc at this thickness (S12). Forming, formation cycle and any safety test: open point 1. The cell is soldered at low heat to FLEX2 (assembly.md step 9), is live from step 16 on, and is inside the cast resin liner (step 21): the highest temperature it may see is open point 7.

## Finish and colour
Not applicable to a part inside the band; wrap and tab finish: open point 1.

## General tolerance and tighter tolerances
General: ISO 2768-m for size (default, to confirm with the maker), but a cell maker's own thickness tolerance rules, and the swelling room is a design item (0.2 mm gap, below). The tolerance on thickness is critical: the stack in the band has 2.6 mm in all (liner 0.3, cell 1.6, gap 0.2, shell 0.5). Tolerances: open point 2.

## Critical dimensions

| name | value | tolerance | where it is measured |
|---|---|---|---|
| cell thickness | 1.6 mm | open point 2 | radial, over the whole cell, after charge |
| cell width | 6.0 mm | open point 2 | across the band, along X |
| cell section | 1.6 x 6.0 mm | open point 2 | radial x across |
| cell length on its centre line | 33.936 (US 7) to 46.121 mm (US 13), table below | open point 2 | along the arc, at the middle of the thickness |
| centre-line radius | 9.7598 (US 7) to 12.1982 mm (US 13), table below | open point 2 | bend radius of the centre line |
| start and end angle | +48.713 to -98.986 deg at US 9; per ring size in the table below | ISO 2768-m | from the top; the start is the end near the protection circuit (+Y side), the end is near the joystick (-Y side) |
| end at the joystick | 0.10 mm from the dam DAM1 | design value | the cell ends 0.10 mm beyond the dam's outer face; at US 9 that is 3.50 mm around the band from the joystick centre at the liner (model v5) |
| protection circuit, along the arc | 1.5 mm | open point 2 | on the cell's tab |
| protection circuit, across | 5 mm | open point 2 | same |
| protection circuit start | 43.8 deg (US 7), 41.5 deg (US 8), 39.5 deg (US 9 to 13) | ISO 2768-m | from the top, +Y side; the circuit lies before the cell's start (17.26) |
| resin between the protection circuit and the ribbon | 0.075 mm | design value | the resin skin over the embedded +Y ribbon (FLEX2); the least free space at every size (17.26) |
| gap, cell to shell | 0.2 mm | design value | radial, swelling room |
| liner over the cell | 0.3 mm | design value | radial, finger side |
| charge voltage | 4.35 V | Grepow | full-charge voltage; the charger terminates at 4.35 V (firmware F6 8.1) |
| charge current | 15 mA | not a dimension | 0.85 C of the smallest cell, 17.6 mAh (17.26, 17.13, 17.18); the charger ends at 10 percent of it (firmware F6 8.1) |
| capacity, lowest | 17.6 mAh (US 7) | Grepow | at the volume 325.8 cubic mm [CALC: 0.054 mAh per cubic mm] |
| capacity, highest | 31.9 mAh (US 13) | Grepow | at the volume 442.8 cubic mm [CALC: 0.072 mAh per cubic mm] |
| peak discharge the cell must give | up to 228 mA for the instant of a motor start | open item S12: Grepow confirms | at 3.30 V, with every other load on (17.22); about 13 C of the smallest cell [CALC: 228 / 17.6] |
| running discharge | about 4.1 mA recording | not a dimension | firmware F6 8.5; the motor pulse runs below 80 mA (17.16) |

## What to inspect
Dimensions after bending: thickness at 5 points, width, length, radius with a gauge at ring size; capacity at the stated rate; open-circuit voltage; protection circuit limits (overvoltage, overcurrent, undervoltage) against the maker's datasheet and its trip current against the 228 mA start (S12); swelling after the first full charges (thickness growth against the 0.2 mm gap); insulation resistance; tab strength; temperature sensor value; lot number. Safety test report: open point 1.

## Ring sizes
One cell per ring size. The lengths below are measured in the inside model v6 (architecture 17.26; thin-notes.md section "Model v6, continued", table for the cell spec); they replace the earlier calculation of a constant 154 degrees. Each row passed the model's fit check (`RESULT PASS`, v6.2). Volume = 1.6 x 6.0 x length; capacity at 0.054 to 0.072 mAh per cubic mm [CALC].

| US size | Joystick | Cell from, deg | Cell to, deg | Length on the centre line, mm | Centre-line radius, mm | Volume, mm3 | Capacity, mAh | Recording hours at 4.1 mA [CALC] |
|---|---|---|---|---|---|---|---|---|
| 7 | -84.0 | +53.78 | -106.994 | 33.936 | 9.7598 | 325.8 | 17.6 to 23.5 | 4.3 to 5.7 |
| 8 | -81.0 | +51.081 | -102.943 | 36.547 | 10.1662 | 350.9 | 18.9 to 25.3 | 4.6 to 6.2 |
| 9 | -78.0 | +48.713 | -98.986 | 39.175 | 10.5726 | 376.1 | 20.3 to 27.1 | 5.0 to 6.6 |
| 10 | -78.0 | +48.372 | -98.111 | 40.914 | 10.9790 | 392.8 | 21.2 to 28.3 | 5.2 to 6.9 |
| 11 | -78.0 | +48.055 | -97.308 | 42.651 | 11.3854 | 409.4 | 22.1 to 29.5 | 5.4 to 7.2 |
| 12 | -78.0 | +47.76 | -96.567 | 44.387 | 11.7918 | 426.1 | 23.0 to 30.7 | 5.6 to 7.5 |
| 13 | -78.0 | +47.485 | -95.883 | 46.121 | 12.1982 | 442.8 | 23.9 to 31.9 | 5.8 to 7.8 |

The smallest cell is US 7, 17.6 mAh. Every rule that protects a recording time, and the charge current of 15 mA, use this cell (17.26). The joystick sits lower on US 7 (-84.0) and US 8 (-81.0) than on the other sizes (17.25); the cell ends 0.10 mm past the dam, so it ends earlier there. The motor angles per size (-47.0, -45.5, -44.0, -45.0, -43.5, -42.5, -42.5 degrees for US 7 to 13) do not change the cell. US 5 and US 6 are not built (17.17). Charge time at 15 mA from empty, constant-current part only [CALC, firmware F6 8.1]: 1.17 to 1.57 hours at US 7 and 1.59 to 2.13 hours at US 13.

## Files
Drawing: design/mfg/drawings/cell.svg and cell.pdf. STEP only, one per ring size, exported from the inside model v7: design/mfg/parts/cell/cell-us7.step to cell-us13.step (no STL exists for the cell; index.csv: pouch body only, sealed edge and tabs not in it; the length on the centre line of each file is the length of the table below). At US 9 the box is 6.0 x 22.5584 x 17.0231 and the volume 353.4595 cubic mm, which is under the 1.6 x 6.0 x 39.175 figure of the table because the 0.3 rounding and the 2.0 sealed edge are left out of the solid. The drawing cell.svg is the US 9 cell; the other sizes are cell-us7 to cell-us13 in the same folder.

## Requirements on the cell (fixed by the design, 2026-11-13 00:41)

The cell is a custom part. These lines are requirements the cell must meet; they replace the questions of the open points below, which stay as history. A cell that does not meet one of them is not this part. Each value has its reason; only a built cell can prove it, and the build guide carries the test.

| Requirement | Value | Reason and source |
|---|---|---|
| chemistry and format | lithium polymer pouch, 4.35 V full-charge type, curved to the band radius of its ring size | the charger ends at 4.35 V (firmware 8.1; nPM1304 termination option 4V35, specification page 36) |
| size | the sizes of the table "Ring sizes" are maximum sizes after bending, protection circuit not included; the cell may be smaller by at most 0.2 mm in thickness and width | the model's free space (gap cell to shell 0.2 mm, liner 0.3 mm, this page) |
| swelling over life | at most 0.2 mm in thickness | the radial gap of 0.2 mm (this page, critical dimensions) |
| capacity | at least the value of the table "Ring sizes" for its size (17.6 mAh at US 7 to 31.9 mAh at US 13), at a 0.2 C discharge to 3.0 V | the design's calculation from volume (open point 6); the battery life figures use these values |
| charge | accepts a constant current of 15 mA to 4.35 V at 0 to 45 C, every size | design/wiring/lead-decisions.md item 65; the charger's setting (nPM1304: 4 to 100 mA in 0.5 mA steps) |
| pulse discharge | series resistance of the cell with its protection circuit at most 1.9 ohm at 20 percent state of charge and 20 C, with an open-circuit voltage of 3.45 V or more there; measured with a pulse of 235 mA for 100 ms, which must leave at least 3.0 V at the output tabs | motor start below 175 mA plus the recording load; the circuit simulation gives a peak of 232.5 mA and the limit 1.93 ohm at 3.45 V (design/sim/circuit/sim-notes.md finding 4; design/wiring/lead-decisions.md, row "sim finding 4"). Not known: whether a cell of 17.6 mAh meets it; the fallback is a soft start of the motor in the ring software |
| protection circuit: overcurrent | trips between 0.5 A and 1.0 A, never under 0.5 A | above the 230 mA pulse with margin; under the regulator U11's current limit of 560 mA or more only as a second barrier (TLV755P datasheet page 5) |
| protection circuit: overcharge | cuts off at 4.425 V, tolerance 0.025 V | above the charger's 4.35 V end voltage, under the cell's limit for a 4.35 V type |
| protection circuit: undervoltage | cuts off at 2.5 V, tolerance 0.1 V | under the power chip's 2.7 V power-fail reset, so the ring's own ordered shutdown at 3.30 V and the chip's reset come first (design/wiring/lead-decisions.md item 69) |
| protection circuit: place and tabs | on the cell tab, start angle per size as in the critical dimensions; three output tabs P+, P- and NTC with the order, sizes and positions of design/ecad/band/band-interface.md section 5 | the lands of the band circuit FLEX2 are drawn for them (design/ecad/band, boards flex2-us7 to us13) |
| temperature sensor | RT1, 10 kohm NTC, on the protection circuit, one pin to tab NTC and one to tab P- | design/wiring/lead-decisions.md item 34; design/ecad/band/band-interface.md section 5 |
| heat in assembly | the cell is never above 45 C while it is live in the assembly; the liner resin is cast and cured at room temperature | design-side rule that replaces the question to the cell maker (open point 8); the resin choice of the assembly file must meet it |
| safety documents | a test report to IEC 62133-2 and a UN 38.3 transport report come with the first lot | needed to ship a product with a lithium cell |

## Open points
History: the points below are answered by the section "Requirements on the cell" above, except the tolerance of the bend radius (point 2), which the ring body drawing of each size fixes.
1. Cell chemistry, format, order code, price, whether a 1.6 x 6.0 mm arc of the lengths in the table can be built at 4.35 V, protection circuit part code and its limits, safety test reports: Grepow (S12, bom.csv lines 49 and 50).
2. Tolerances of thickness, width, length, radius: Grepow.
3. The cell angles of the table are model values; the design partner confirms them after the owner confirms the joystick angles of 17.25 on a picture.
4. The highest charge current the cell accepts: Grepow must confirm 15 mA (0.85 C of 17.6 mAh) and the termination at 4.35 V; the nPM1304 charges below 32 mA, so the earlier "second charger part" question is closed (17.13, 17.18).
5. Where the temperature sensor sits and its type: Grepow and the electronics designer.
6. Capacity 17.6 to 31.9 mAh is a calculation from volume (0.054 to 0.072 mAh per cubic mm), not a maker figure. bom.csv line 49 may still show an older length: this page follows 17.26.
7. The peak discharge: the cell and its protection circuit must allow a start of up to 228 mA at 3.30 V (17.22, open item S12). Grepow states the continuous and the peak discharge current and the protection circuit's trip current. If the cell cannot give it, a series resistor or a soft start is the remedy named in 17.16 and neither is designed.
8. Highest temperature the cell may see in the resin cure and its heat limit while live in the cast (assembly.md K-A8): Grepow.
9. Position of the protection circuit per size (43.8, 41.5, 39.5 degrees) and the 0.075 mm of resin between it and the ribbon: Grepow confirms the circuit's outline and tab position fit this place.

## Source lines
design/architecture.md lines 433, 434, 437 (17.3), 469 (S12); 17.13 and 17.18 (charge 15 mA, 4.35 V); 17.22 (228 mA); 17.25, 17.26 and 17.27 (per size values; they win over 17.10, 17.8, 17.7 and 17.3); design/bom.csv lines 49, 50; design/mech/thin/thin-notes.md sections "Model v6, continued" and "Model v6.2"; design/firmware.md F6 sections 8.1 and 8.5.
