# Specification: main board as a bare board, reference PCB1

Design version A5, architecture section 17.8 (2026-11-10). All dimensions in mm.

## What it is
The bare printed circuit board of the ring electronics: 6 layers, 0.3 mm thick, 27.2 x 12.6 mm. Parts on the under side only (the top faces the screen). This page is the bare board; the parts on it are bought parts listed in bom.csv. Gerber and drill files do not exist yet (open point 1).

## Quantity per ring
1 per ring. The same board for all ring sizes.

## Material
Default, to confirm with the maker: 6 layers, 0.3 mm thick. Laminate type, copper weight and the stack-up: open point 2 (bom.csv line 51: the ring electronics designer answers with the stack-up).

## Process
Standard multilayer board process; fine-pitch 0201 assembly afterwards. Via type and minimum track and gap: open point 2.

## Finish and colour
Open (point 3): surface finish and solder-mask colour are not stated. The 3D model shows gold pad rectangles on a solder-mask face (design/mech/thin/thin-notes.md); that is the modeller's assumption.

## General tolerance and tighter tolerances
General: ISO 2768-m for the outline, notches and corner radius (default, to confirm with the maker). Thickness, copper and hole tolerances: the board maker's own, open point 2.

## Critical dimensions

| name | value | tolerance | where it is measured |
|---|---|---|---|
| board length (X) | 27.2 mm | ISO 2768-m | outline |
| board width (Y) | 12.6 mm | ISO 2768-m | outline |
| board thickness | 0.3 mm | open point 2 | finished board |
| layer count | 6 | not a dimension | stack-up |
| antenna notch, X | 1.8 mm | ISO 2768-m | notch at the hand-end corner, thumb side |
| antenna notch, Y | 3.6 mm | ISO 2768-m | same notch |
| joystick notch, long | 2.8 mm | ISO 2768-m | on the thumb-side edge (open point 4) |
| joystick notch, short | 0.6 mm | ISO 2768-m | same |
| board fill, populated area | 57 percent | not a dimension | design limit 60 percent for a routable one-sided board |
| screen connector position | -12 mm | ISO 2768-m | on the board, X from the board centre |
| microphone 1 position | -11.0 mm | ISO 2768-m | X from the board centre |
| microphone 2 position | 11 mm | ISO 2768-m | X from the board centre |
| parts height limit under the board | 1.00 mm | not a dimension | tallest part (coil 1.0) |

## What to inspect
Outline and notch sizes; thickness (finished); layer count and stack-up by a section coupon; impedance if the antenna line needs it (open point 2); electrical test of every net (100 percent flying probe or fixture); solderability; no copper or metal in the antenna zone; warp (the board is 0.3 mm thick and must stay flat for the 0201 parts); the board maker's own report.

## Ring sizes
The same for all sizes (US 5 to 13). The block does not change with ring size.

## Files
Drawing: design/mfg/drawings/main-board.svg and main-board.pdf. STEP and STL: design/mfg/parts/main-board/main-board.step and .stl (index.csv: bare PCB outline only, 27.2 x 12.6 x 0.28; the thickness in the STEP is 0.28, the architecture says 0.3: open point 8). KiCad files: design/ecad (open: Gerber, drill and pick-and-place not made).

## Open points
1. Gerber, drill, stack-up drawing and pad drawing: the ring electronics designer (bom.csv line 51, NEW-2).
2. Laminate, copper weight, via type, track and gap, finished thickness tolerance, impedance: the board maker proposes after the stack-up exists.
3. Surface finish and solder-mask colour: the board maker proposes, the design partner accepts.
4. The 2.8 x 0.6 joystick notch (17.3) was needed because the joystick cap's rim reached into the board layer on the 3.6 mm shoulder at +38 degrees. In 17.8 the joystick moved to +150 degrees at the bottom of the band; whether the notch is still needed: the 3D model owner answers.
5. Corner radius 0.8 mm is the modeller's assumption (placement.csv), not in the architecture: the design partner answers.
6. Antenna keep-out, section 6 (older state): no copper and no metal within 4.2 x 4.7 mm on every layer; the antenna now sits in a 1.8 x 3.6 notch (17.3). The electronics designer states the current keep-out.
8. Thickness: the STEP file has 0.28 mm (solder mask is a separate solid), the architecture and bom.csv say 0.3 mm: the parts helper and the electronics designer answer which is the finished thickness.
7. Test pads: bom.csv lists 15 plus 4 plus 3 test pads on the board; their positions come from the layout.

## Source lines
design/architecture.md lines 424 (17.2, board 0.3 mm), 440, 441 (17.3 notches), 456 (board 0.3 mm, 6 layers), 420 (mic slots at X = -11 and +11), 379 (16.7, fill 57 percent), 358 (16.4 board row); design/bom.csv line 51; design/mech/thin/thin-notes.md.
