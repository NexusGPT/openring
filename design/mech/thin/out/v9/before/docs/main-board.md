# Specification: main board as a bare board, reference PCB1

Design version A5, architecture section 17.8 (2026-11-10), refreshed to the inside model v5 (architecture 17.19, 17.22, 17.24) and to design version 7 (architecture 17.30, 2026-11-11: the recording light and its parts are removed in v7, and the board has no hole). All dimensions in mm. Y: -Y is the joystick side.

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
| antenna notch, X | 1.8 mm | ISO 2768-m | notch at the hand-end corner, +Y side (away from the joystick) |
| antenna notch, Y | 3.6 mm | ISO 2768-m | same notch |
| joystick notch | 0 (none) | not a dimension | the board has no joystick notch (before v5 this page gave 2.8 x 0.6 mm; open point 4) |
| holes through the board | 0 (none) | not a dimension | no drilled or routed hole in the outline; the non-plated light guide hole at X -12.425, Y -2.95 is removed in v7 (17.30), with LED1, R41 and Q2 removed in v7 |
| motor regulator U11 | X 0.0, Y 4.2 | ISO 2768-m | TLV75530PDQNR 1.0 x 1.0 x 0.4 mm, under face, model v5 proposal; the layout confirms (S22) |
| motor capacitors C83, C84 | C83 X 0.0, Y 5.45; C84 X 1.2, Y 5.0 | ISO 2768-m | 10 uF, 0402 (1.0 x 0.5 mm, height 0.5 assumed), under face, model v5 proposal; the layout confirms (S22) |
| ribbon fold keep-free zone | X -3.5 to -0.9, Y +-3.4 to +-5.6 | not a dimension | no part on the under face there: one ribbon fold beside each floor slot (K-A6) |
| board fill, populated area | 72 percent | not a dimension | 17.22 (before 17.22 this page gave 57 percent); the design limit stated earlier was 60 percent for a routable one-sided board: the layout answers |
| screen connector position | -12 mm | ISO 2768-m | on the board, X from the board centre |
| microphone 1 (U5) position | X -10.8, Y -4.8 mm | ISO 2768-m | Knowles SPK0641HT4H-1, 4.00 x 3.00 x 1.00 mm, top port facing the floor; the port is at X -11.77 (17.19) |
| microphone 2 (U6) position | X +10.8, Y -4.8 mm | ISO 2768-m | same part; the port is at X +11.77 |
| parts height limit under the board | 1.00 mm | not a dimension | tallest part (coil 1.0) |

## What to inspect
Outline and notch sizes; thickness (finished); layer count and stack-up by a section coupon; impedance if the antenna line needs it (open point 2); electrical test of every net (100 percent flying probe or fixture); solderability; no copper or metal in the antenna zone; warp (the board is 0.3 mm thick and must stay flat for the 0201 parts); the board maker's own report.

## Ring sizes
The same for all sizes (US 7 to 13). The block does not change with ring size.

## Files
Drawing: design/mfg/drawings/main-board.svg and main-board.pdf. STEP only: design/mfg/parts/main-board/main-board.step (no STL exists for the board; index.csv: bare board core 27.2 x 12.6 x 0.28 with the antenna notch, no other hole, no mask, pads, copper or parts; the thickness in the STEP is 0.28, the architecture says 0.3: open point 8). That STEP file is exported from the inside model v7 and has no light guide hole and no other hole than the antenna notch; it agrees with this page: no hole. KiCad files: design/ecad (open: Gerber, drill and pick-and-place not made).

## Open points
1. Gerber, drill, stack-up drawing and pad drawing: the ring electronics designer (bom.csv line 51, NEW-2).
2. Laminate, copper weight, via type, track and gap, finished thickness tolerance, impedance: the board maker proposes after the stack-up exists.
3. Surface finish and solder-mask colour: the board maker proposes, the design partner accepts.
4. Closed: the 2.8 x 0.6 joystick notch of 17.3 is not needed. The board has had no joystick notch since model v3 (C13), and the joystick is at -78 degrees on the joystick side of the band (-81.0 on US 8, -84.0 on US 7; 17.11, 17.25), where the board does not reach.
5. Corner radius 0.8 mm is the modeller's assumption (placement.csv), not in the architecture: the design partner answers.
6. Antenna keep-out, section 6 (older state): no copper and no metal within 4.2 x 4.7 mm on every layer; the antenna now sits in a 1.8 x 3.6 notch (17.3). The electronics designer states the current keep-out.
8. Thickness: the STEP file has 0.28 mm (solder mask is a separate solid), the architecture and bom.csv say 0.3 mm: the parts helper and the electronics designer answer which is the finished thickness.
7. Test pads: bom.csv lists 15 plus 4 plus 3 test pads on the board; their positions come from the layout.
9. Room for U11, C83 and C84 on a board 72 percent full, and the ribbon keep-free zone: the board layout confirms or moves them (S22, 17.24 K20). The pads of U11 and the 0402 height 0.5 are assumed.
10. Closed in v7: the board has no hole (17.30); the copper rule round the light guide hole, LED1, R41 and Q2 are removed in v7.

## Source lines
design/architecture.md lines 424 (17.2, board 0.3 mm), 440, 441 (17.3 notches; the joystick notch is no longer needed), 456 (board 0.3 mm, 6 layers), 379 (16.7, fill 57 percent; 17.22 says 72 percent), 358 (16.4 board row); 17.19 (microphones U5, U6, ports at X +-11.77), 17.22 (U11, C83, C84), 17.24; design/bom.csv line 51; design/mech/thin/thin-notes.md.
