# Specification: main board as a bare board, reference PCB1

Design version A5, architecture section 17.8 (2026-11-10), refreshed to the inside model v5 (architecture 17.19, 17.22, 17.24) and to design version 7 (architecture 17.30, 2026-11-11: the recording light and its parts are removed in v7, and the board has no hole), and to the inside model v9 (2026-11-13: the parts the model draws stand at the places of the board plan design/wiring/ring-board-plan-work/placement-plan.csv, the board has no notch, 4 copper layers: design/wiring/lead-decisions.md rows "7, 11 (part), W2", "2, 3, 6, 8, W2" and "W2, rule on places"). All dimensions in mm, in the model frame (KiCad = model + 100 on X and Y). Y: -Y is the joystick side.

## What it is
The bare printed circuit board of the ring electronics: 4 copper layers, every via a laser microvia, 0.30 mm finished, 27.2 x 12.6 mm, no notch. Parts on both faces since ring board round 3 (2026-11-13): the parts face (F.Cu, L1, the under side) holds all parts but nine; the screen face (B.Cu, L4, side B of the board plan) holds the screen connector J1, eight 0201 parts (C1, C2, C5, C7, C14, R71, R72, FB1) and the 12 flat test pads TP1, TP3, TP4, TP5, TP6, TP12, TP14, TP15, TP17, TP18, TP19, TP21 (`design/ecad/ring/pcb/placement-final.csv`, `design/ecad/ring/pcb/board-notes-r3.md`; 19 pads before round 2, 15 before round 3). This page is the bare board; the parts on it are bought parts listed in bom.csv. Gerber, drill, position and stack-up files exist: `design/ecad/ring/pcb/fab/` (open point 1 closed).

## Quantity per ring
1 per ring. The same board for all ring sizes.

## Material
4 copper layers, any-layer laser microvias (0.10 mm hole, 0.20 mm land, filled), 0.30 mm finished (lead's decision, design/wiring/lead-decisions.md row "7, 11 (part), W2"; stack-up in design/wiring/ring-board-plan.md section c.2). Laminate type and copper weight: open point 2.

## Process
Standard multilayer board process; fine-pitch 0201 assembly afterwards. Via type and minimum track and gap: open point 2.

## Finish and colour
Surface finish ENEPIG; solder mask green on both sides, U1 and U2 land openings equal to the land (source: design/ecad/ring/pcb/fab/stackup.txt line 20; open point 3 closed). Before: "not stated"; the 3D model shows gold pad rectangles on a solder-mask face (design/mech/thin/thin-notes.md), the modeller's assumption.

## General tolerance and tighter tolerances
General: ISO 2768-m for the outline and corner radius (default, to confirm with the maker); the board has no notch. Thickness, copper and hole tolerances: the board maker's own, open point 2.

## Critical dimensions

| name | value | tolerance | where it is measured |
|---|---|---|---|
| board length (X) | 27.2 mm | ISO 2768-m | outline |
| board width (Y) | 12.6 mm | ISO 2768-m | outline |
| board thickness | 0.3 mm | open point 2 | finished board |
| layer count | 4 | not a dimension | copper layers, stack-up (lead's decision row "7, 11 (part), W2"; before: 6) |
| antenna notch | 0 (none) | not a dimension | the board is the full rectangle with 0.8 corners; the antenna sits on the under face (design/wiring/ring-board-plan.md e.7, R2.0; inside model v9). Before v9 a 1.8 x 3.6 notch at the hand-end corner |
| antenna ANT1 | X -10.80, Y 5.25, turned 180 | ISO 2768-m | on the under face at the hand-end corner, +Y edge, long side along X, on the maker's four lands; its 1.20 body reaches 0.20 below the floor top into the resin radio corner's floor pocket (specs/body.md) |
| joystick notch | 0 (none) | not a dimension | the board has no joystick notch (before v5 this page gave 2.8 x 0.6 mm; open point 4) |
| holes through the board | 0 (none) | not a dimension | no drilled or routed hole in the outline; the non-plated light guide hole at X -12.425, Y -2.95 is removed in v7 (17.30), with LED1, R41 and Q2 removed in v7 |
| motor regulator U11 | X 0.0, Y 4.2 | ISO 2768-m | TLV75530PDQNR 1.0 x 1.0 x 0.4 mm, under face, board plan (placement-plan.csv) |
| motor capacitors C83, C84 | C83 X 0.0, Y 5.45; C84 X 1.27, Y 5.0 turned 90 | ISO 2768-m | C83 10 uF, C84 4.7 uF, 0402 (1.0 x 0.5 mm, height 0.5 assumed), under face, board plan (placement-plan.csv); before v9 C84 at X 1.2, not turned |
| ribbon fold keep-free zone | X -3.5 to -0.9, Y +-3.4 to +-5.6 | not a dimension | no part on the under face there: one ribbon fold beside each floor slot (K-A6) |
| board fill, populated area | 72 percent | not a dimension | 17.22 (before 17.22 this page gave 57 percent); the design limit stated earlier was 60 percent for a routable one-sided board: the layout answers |
| copper-free zone, all layers | X -13.60 to -8.75, Y 3.10 to 6.30, less X -9.20 to -8.75, Y 3.10 to 3.30 | not a dimension | no copper and no pad except the antenna's own lands and LT1 (ring-board-plan.md R2.0); the inside model v9 checks that no metal part stands in it |
| microphone 1 (U5) position | X -10.8, Y -4.8 mm | ISO 2768-m | Knowles SPK0641HT4H-1, 4.00 x 3.00 x 1.00 mm, top port facing the floor; the port is at X -11.77 (17.19) |
| microphone 2 (U6) position | X +10.8, Y -4.8 mm | ISO 2768-m | same part; the port is at X +11.77 |
| parts height limit under the board | 1.00 mm | not a dimension | tallest part (coil 1.0) |

## What to inspect
Outline size (no notch); thickness (finished); layer count and stack-up by a section coupon; impedance if the antenna line needs it (open point 2); electrical test of every net (100 percent flying probe or fixture); solderability; no copper or metal in the antenna zone; warp (the board is 0.3 mm thick and must stay flat for the 0201 parts); the board maker's own report.

## Ring sizes
The same for all sizes (US 7 to 13). The block does not change with ring size.

## Files
Drawing: design/mfg/drawings/main-board.svg and main-board.pdf. STEP only: design/mfg/parts/main-board/main-board.step (no STL exists for the board; index.csv: bare board core 27.2 x 12.6 x 0.28, no notch and no hole, no mask, pads, copper or parts; the thickness in the STEP is 0.28, the architecture says 0.3: open point 8). That STEP file is exported from the inside model v9 (no notch since v9; no light guide hole since v7); it agrees with this page. The places of all 104 parts: design/wiring/ring-board-plan-work/placement-plan.csv. KiCad files: the routed board `design/ecad/ring/pcb/ring.kicad_pcb` with its Gerber, drill, position and stack-up files in `design/ecad/ring/pcb/fab/`; the board maker builds from those files, and this STEP (the model's core, 0.28 mm without solder mask) is for the mechanical fit only.

## Open points
1. CLOSED 2026-11-13: Gerber, drill, position files, IPC-356 netlist and stack-up are in `design/ecad/ring/pcb/fab/` (routed board `design/ecad/ring/pcb/ring.kicad_pcb`, rules check 0 violations and 0 unconnected, `board-notes-r3.md`). Before: the ring electronics designer (bom.csv line 51, NEW-2).
2. CLOSED 2026-11-13 as the design's order values: `design/ecad/ring/pcb/fab/stackup.txt` gives the laminate (106 prepreg, core), finished copper 0.018 mm, laser microvias 0.10 / 0.20 mm stacked and filled, track and gap 0.065 / 0.065 mm minimum, thickness 0.30 mm +-0.025 and the two impedance coupons. The board maker confirms them with its quote. Before: laminate, copper weight, via type, track and gap, finished thickness tolerance, impedance: the board maker proposes after the stack-up exists.
3. CLOSED 2026-11-13: surface finish ENEPIG, solder mask green on both sides (`design/ecad/ring/pcb/fab/stackup.txt` line 20). Before: the board maker proposes, the design partner accepts.
4. Closed: the 2.8 x 0.6 joystick notch of 17.3 is not needed. The board has had no joystick notch since model v3 (C13), and the joystick is at -78 degrees on the joystick side of the band (-81.0 on US 8, -84.0 on US 7; 17.11, 17.25), where the board does not reach.
5. Corner radius 0.8 mm is the modeller's assumption (placement.csv), not in the architecture: the design partner answers.
6. Closed in v9: the antenna keep-out is the copper-free zone of the board plan (X -13.60 to -8.75, Y 3.10 to 6.30, all layers, less the notch at the storage chip's corner; ring-board-plan.md R2.0), and the antenna sits on the under face with no notch. History: 4.2 x 4.7 mm (section 6), then a 1.8 x 3.6 notch (17.3, model v2 to v8).
8. Thickness: the STEP file has 0.28 mm (solder mask is a separate solid), the architecture and bom.csv say 0.3 mm: the parts helper and the electronics designer answer which is the finished thickness. Decided 2026-11-13 (lead): the finished board is 0.30 mm, as routed (`design/ecad/ring/pcb/board-notes.md` line 3); the STEP file's 0.28 mm is the board without its solder mask and is made again from the routed board.
7. Test pads: 15 (TP1, TP3, TP4, TP5, TP6, TP8, TP9, TP11, TP12, TP14, TP15, TP17, TP18, TP19, TP21; design/ecad/ring/parts.csv) after the four of 'ring board round 2' are dropped (TP13, TP16, TP22, TP2: the debug log is send-only, DBG_TX, and the programming pads stay); their positions come from the layout.
9. Room for U11, C83 and C84 on a board 72 percent full, and the ribbon keep-free zone: the board layout confirms or moves them (S22, 17.24 K20). The pads of U11 and the 0402 height 0.5 are assumed.
10. Closed in v7: the board has no hole (17.30); the copper rule round the light guide hole, LED1, R41 and Q2 are removed in v7.

## Source lines
design/architecture.md lines 424 (17.2, board 0.3 mm), 440, 441 (17.3 notches; the joystick notch is no longer needed), 456 (board 0.3 mm; the line said 6 layers, 4 copper layers since the board plan), 379 (16.7, fill 57 percent; 17.22 says 72 percent), 358 (16.4 board row); 17.19 (microphones U5, U6, ports at X +-11.77), 17.22 (U11, C83, C84), 17.24; design/bom.csv line 51; design/mech/thin/thin-notes.md.

## Places of the parts drawn in the 3D model (board plan; not dimensions of the bare board; at the end of the page so that the line numbers other files cite stay)
The places of all 104 parts are the board plan's table design/wiring/ring-board-plan-work/placement-plan.csv (round 4, ring-board-plan.md R4.4); its own check (check_placement.log) covers every courtyard. The inside model v9 draws these 16 at the plan's place, turn (KiCad degrees) and body size (footprint F.Fab outline, design/ecad/ring/pcb/OpenRing.pretty), checked by design/mech/thin/check_thin.py section 14 within 0.01 mm: U1 (4.000, 0.000) 0; U2 (8.500, 0.000) 270; U3 (-5.000, 0.000) 0; U4 (3.250, -3.800) 180; U5 (-10.800, -4.800) 90; U6 (10.800, -4.800) 270; U11 (0.000, 4.200) 0; X1 (3.000, 3.000) 0; X2 (6.000, 4.250) 90; L10 (6.500, -4.200) 90; L71 (12.020, 3.750) 0; L72 (8.870, 3.750) 0; ANT1 (-10.800, 5.250) 180; J1 (-11.650, -0.150) 270, its FPC opening toward the hand end (R2.1); C83 (0.000, 5.450) 0; C84 (1.270, 5.000) 90. The other 88 parts (0201, 0402, 0603 and the test pads) are not drawn in the 3D model. Side B of the plan (the 15 test pads TP1, TP3, TP4, TP5, TP6, TP8, TP9, TP11, TP12, TP14, TP15, TP17, TP18, TP19, TP21; 19 in the plan file until round 2) is the screen face: flat copper with no height, not drawn.
