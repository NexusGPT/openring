# Specification: the two band flex tails, references FLEX1 (joystick side) and FLEX2 (other side)

> **Both ribbons are drawn as circuit boards in design/ecad/band (band-notes.md, band-interface.md; one board per tail and ring size, flex1-us7 to flex2-us13, with Gerber, drill and a dimensioned drawing in design/ecad/band/fab/) and the inside model v8 carries them exactly as drawn at every ring size US 7 to 13 (architecture 17.15, 17.26, 17.27; design/mech/thin/thin-notes.md section "Model v8"; fit proof design/mech/thin/band-fit-notes.md): neck 1.8 mm wide, centred in the floor slot (the slot is 2.1 wide since v8), a 90 degree fold with 0.70 mm inner radius, a flat foot 2.5 mm wide with a 0.10 mm polyimide stiffener under the main board, 0.11 mm finished thickness outside the liner, and in the liner a 0.15 mm allowance with 0.075 mm of resin on each side. A liner cast with a ribbon inside it is not proven by any maker (bench item B8, open item S19). Before v8 this page said each tail was 1.4 mm wide and that no flat pattern existed; both are replaced by the files named here.**

Design version A5, architecture section 17.8 (2026-11-10). All dimensions in mm.

## What it is
Two flexible printed circuits that leave the main board through slots in the block's floor, one into each shoulder, and run inside the band channel.
- FLEX1, joystick side (-Y): carries the vibration motor and the five joystick switches SW1 to SW5, SW2 being the centre switch under the round joystick cap CAP1 (17.11, 17.14, 17.29). The ring has no record switch and no record button.
- FLEX2, other side: carries the cell (2 lines), the cell's temperature sensor (1 line) and the four charging pads VBUS, D-, D+, GND (17.8; 17.3 had the motor here too). The pads are gold discs in the liner on the inside of the band (17.12), the row at X = -1.0 mm (toward the hand end of the block, ring -X) where the case pins stand: a ring turned over in the case then has its pads 2.0 mm from the pins (architecture 17.28).
Line counts per tail (17.14): 8 pads on FLEX1 (joystick switches, centre switch, motor) and 7 on FLEX2 (cell, temperature sensor, four charging pads); the motor's side is confirmed by the model on the joystick side (-44 degrees at US 9; -47.0 to -42.5 over US 7 to 13). The solder pads on the main board are J_BAND_A (FLEX1) and J_BAND_B (FLEX2).

## Quantity per ring
2 per ring: 1 FLEX1 and 1 FLEX2. The two tails differ.

## Material
Polyimide core 25 um, copper 12 um on both sides, polyimide coverlay on both sides (12.5 um polyimide and 15 um adhesive on 12 um copper), finished 0.11 mm (JLCPCB flexible PCB capabilities page, fetched 2026-11-13; band-notes.md section "Stack and rules").

## Process
Flexible printed circuit, two layers, polyimide 0.10 mm stiffeners on the back (B.Cu) face: under the board foot of each tail (X -3.45 to -0.95, Y from 3.45 to 5.05 in the model frame, mirrored for FLEX1) and, on FLEX1, a flat stiffener of 6.4 x 6.4 x 0.10 mm under the flat switch head with the liner filling under it (band-interface.md section 1; 17.24 K13, 17.26; before v8 the head stiffener was 0.075). The foot is joined to the main board by hot bar (band-interface.md section 7); the motor leads and the cell protection circuit tabs are hand soldered (sections 5 and 6). The hot bar and iron values are starting values that no bench unit has measured yet (band-notes.md "Not closed" 2).

## Finish and colour
Pad finish ENIG (1 to 2 micro-inch gold) on the lands; the charging pads of FLEX2 are 1.6 mm gold-plated discs 0.07 thick soldered on the lands (band-interface.md section 8). Coverlay colour: not stated by design/ecad/band (the maker's standard polyimide coverlay).

## General tolerance and tighter tolerances
Outline tolerance +-0.10 and copper to edge 0.30 (JLCPCB flexible PCB capabilities page, band-notes.md); lines 0.08 at gaps 0.10, exposed land to line 0.25, via 0.30 / 0.10 (band-interface.md section 1).

## Critical dimensions

| name | value | tolerance | where it is measured |
|---|---|---|---|
| flex thickness, finished | 0.11 mm (0.21 mm under a 0.10 stiffener) | outline +-0.10; thickness per the maker's page | flat parts outside the liner (vertical neck, fold, foot, head) |
| flex thickness, radial allowance in the liner | 0.15 mm | not a dimension | embedded trunk and pad strip: 0.075 mm of resin on each side |
| neck width | 1.8 mm, centred in the floor slot (X -3.4 to -1.6) | outline +-0.10 | vertical piece in the slot and the trunk in the liner (band-interface.md section 9 item 1; v7 model: 1.4) |
| foot | 2.5 mm wide (X -3.5 to -1.0), flat run 1.745 mm (Y from 3.4 to 5.145 on the tail's side), top face Z 1.400 under the board's land faces Z 1.430 (joint 0.03) | outline +-0.10 | under the main board at J_BAND_A and J_BAND_B (band-interface.md sections 2 and 3) |
| fold | 90 degrees, inner radius 0.70 mm (minimum 0.66 = 6 x 0.11), outer face (F.Cu, the lands) toward the board; width tapers from 2.5 to 1.8 across the fold | not a dimension | between the foot and the vertical neck |
| pad strip, FLEX2 | X -3.4 to 0.25 (3.65 wide), 0.45 mm beyond the pad edge on the +X side and along the arc | outline +-0.10 | under the four charging pads |
| liner thickness over the tail | 0.3 mm | open point 2 | radial stack above the flex |
| block floor slot count | 2 | not a dimension | one slot per tail, in the block floor |
| switch pad group count, FLEX1 | 5 | not a dimension | the five joystick switches SW1 to SW5 (SW2 centre) on the same tail; before v5: four switches plus a record switch |
| charging pad count, FLEX2 | 4 | not a dimension | VBUS, D-, D+, GND |
| charging pad diameter | 1.6 mm | ISO 2768-f | gold disc on the inside face of the band, set in the liner, flush (17.12, 17.15); before v5: 1.0 mm on the outside |
| charging pad pitch | 2.4 mm along the arc | ISO 2768-f | pads centred opposite the block at 158.2, 172.7, 187.3 and 201.8 degrees, the row at X = -1.0 mm (case pins at X = -1.0; a turned-over ring has its pads 2.0 mm from the pins; architecture 17.28; the pad strip of the cable under them is X -3.4 to 0.25 since v8 (v7: X -2.25 to 0.25 with a jog piece) and 0.45 mm beyond the pad edge on the +X side and along the arc); order VBUS, D-, D+, GND |
| joystick position | -78 deg (US 9 to 13); -81.0 (US 8); -84.0 (US 7) | ISO 2768-m | switches under the cap CAP1, joystick side (17.25) |
| centre switch | SW2 under the cap centre | not a dimension | one of the five switches (17.11, 17.15); there is no record switch and no record button |
| switch cross radius | 2.4 mm | ISO 2768-f | four direction switches round SW2 |
| motor position | -47.0, -45.5, -44.0, -45.0, -43.5, -42.5, -42.5 deg on US 7 to 13 | ISO 2768-m | joystick-side shoulder, 0.7 mm off the band's centre line (0.8 mm at US 7 and US 12 since v8: at US 7 the 1.8 neck came to 0.0246 mm of the motor at 0.7, at US 12 the metal between the motor pocket and the slot 2.1 wide was 0.2977 mm at 0.7, rule 0.30); motor 5.0 diameter x 2.5, pocket 5.2 x 2.6 (17.26, 17.27) |
| protection circuit start | 43.8 deg (US 7), 41.5 deg (US 8), 39.5 deg (US 9 to 13) | ISO 2768-m | the +Y ribbon meets the liner at 42.0 deg at US 7, so the circuit starts later there (17.26); 0.075 mm of resin between the circuit and the ribbon |
| cell at US 9 | from +48.713 through the bottom to -98.986 deg | ISO 2768-m | 39.175 mm on its centre line, 20.3 to 27.1 mAh (17.26); per size: 33.936 mm at US 7 to 46.121 mm at US 13, start and end angles in specs/cell.md; the cell ends 3.50 mm around the band from the joystick centre because of the dam |

Flat length of each tail per ring size (design/ecad/band/band-notes.md section b, the boards' outline lengths, each equal to the model's path within 0.05 mm; the model's path is the v7 path plus the fold and foot, 2.071 mm): FLEX1 16.115, 16.136, 16.122, 16.597, 17.079, 17.566, 18.058 mm and FLEX2 32.184, 33.388, 34.598, 35.813, 37.033, 38.257, 39.485 mm at US 7 to 13. Widths and the fold are in the table above. The 3D model (design/mech/thin/thin-notes.md, model v8) uses the floor slot 2.1 x 0.6 from X -3.55 to -1.45 (v6.2 to v7: 2.0 x 0.6 at X -3.5 to -1.5; before v6.2 2.6 x 0.6) at Y = +-5.9, with the bottom at Z -0.20 (US 7 and 8), -0.23, -0.63, -1.04, -1.45 and -1.85 (US 9 to 13) (17.26); the free volume 2.6 x 2.2 x 1.03 beside each slot under the board (X -3.5 to -0.9, Y +-3.4 to +-5.6, Z 0.40 to 1.43) holds the foot, its stiffener and the fold, and the model's fit check finds no other part in it (check_thin.py item 10). The channel of the band is 7.0 wide since v8 (6.8 before): the 1.8 neck at X -3.4 would touch a 6.8 channel wall.

## What to inspect
Outline; layer count and thickness; continuity of every line on the tail (electrical test of all lines, 100 percent); no short between lines; fold radius 0.70 mm inner at the board fold (the minimum allowed is 0.66) and the tail must lie in the channel (7.0 wide); the pad solder test; cleanliness at the soldered ends.

## Ring sizes
The path length of each tail changes with the ring size (the band diameter changes, US 7 to 13); the block-side end does not. Length per size: the paragraph above. The slot bottom per size is in the line above and in specs/body.md (17.26); the flat pattern per size is design/ecad/band/flexK-usN.kicad_pcb with its drawing design/ecad/band/fab/flexK-usN-drawing.pdf.

## Files
Drawing: design/mfg/drawings/flex-tail-thumb.svg and .pdf (FLEX1), design/mfg/drawings/flex-tail-away.svg and .pdf (FLEX2); both are redrawn from the model v9 files on 2026-11-13 (the foot stiffeners are drawn as flex-tail-thumb-footstiffener-us7 to -us13 and flex-tail-away-footstiffener-us7 to -us13, .svg and .pdf, in the same folder). The flat patterns are design/ecad/band/flex1-us7.kicad_pcb to flex2-us13.kicad_pcb with their Gerber, drill and PDF drawings in design/ecad/band/fab/. STEP only for the 3D shape, one per ring size, exported from the inside model v8 (out/v8/export_ribbons.py, the v7 exporter's emit()): design/mfg/parts/flex-tail-thumb/flex-tail-thumb-us7.step to flex-tail-thumb-us13.step and design/mfg/parts/flex-tail-away/flex-tail-away-us7.step to flex-tail-away-us13.step (no STL exists for the tails). Each file is the bent ribbon as drawn, 0.11 thick outside the liner and 0.15 in it, no copper and no layer stack: 6 solids for FLEX1 (vertical neck, fold, foot, trunk, flat head, bend) and 5 for FLEX2 (vertical neck, fold, foot, trunk, pad strip). The polyimide foot stiffener of each tail is its own file in the same folder: flex-tail-thumb-footstiffener-us7.step to -us13.step and flex-tail-away-footstiffener-us7.step to -us13.step (1 solid, 0.10 thick). At US 9 the box of the thumb file is 6.7 x 6.8244 x 12.3937 and that of the away file 3.75 x 14.4487 x 20.9702; the stiffener boxes are 2.5 x 1.6 x 0.1 and 2.5 x 1.6 x 0.1. They give the shape and the length of the path; the flat pattern is the board file of design/ecad/band.

## Open points
0. S16 (architecture 17.9 and 17.10), route of both tails in the band: closed for the route and the shape at every ring size by design/ecad/band/band-notes.md (14 boards, check_band.py) and the inside model v8 fit check (design/mech/thin/band-fit-notes.md). A liner cast with the ribbon inside is not proven by any maker (B8, S19; band-liner.md open point 10).
1. Line count per tail: closed by design/ecad/band/band-interface.md section 2 (8 lands on FLEX1, 7 on FLEX2) and band-notes.md section c (connectivity computed from the netlist for every board; the motor's supply comes from the regulator U11 on the board, the tail carries the motor's two lines).
2. Stack-up, copper weight, coverlay, stiffener, pad finish, tolerances: closed by design/ecad/band/band-notes.md section "Stack and rules" (polyimide 25 um, copper 12 um, coverlay, finished 0.11, stiffener 0.10, ENIG, outline +-0.10).
3. Soldering method: closed by design/ecad/band/band-interface.md sections 5 to 7 (hot bar for the foot, hand soldering for the motor leads and the protection circuit tabs; assembly order steps 7, 9, 16 and the cast at step 21 in design/mfg/assembly/assembly.md). The hot bar and iron values are starting values that no unit has measured (band-notes.md "Not closed" 2).
4. Outline drawing, widths, lengths per size, bend radii, slot size: closed by design/ecad/band (outlines and flat lengths band-notes.md section b; fold radius band-interface.md section 3) and the model's floor slot 2.1 x 0.6 (thin-notes.md "Model v8").
5. Pad pitch and position at the floor slot on the main board: closed by design/ecad/band/band-interface.md section 2 (lands at X -3.015 to -1.485, |Y| 3.875 and 4.775 on each side, keep-out X -3.5 to -1.0, |Y| 3.4 to 5.6).
6. Still unmeasured (design/ecad/band/band-notes.md "Not closed" 1, 2, 3, 5, 6): the cell supplier's build of the protection circuit tabs (S12), the hot bar and iron settings, the motor lead exit pitch read from a small drawing, via-in-pad acceptance by the flex maker, the Gerber layer names for the coverlay and the stiffener.

## Source lines
design/architecture.md lines 435, 439 (17.3), 489-494 (17.8), 17.9 row S16 and 17.10 (line 514 on; win over 17.8); 17.11, 17.12, 17.14, 17.15, 17.22 and 17.24 (the newest; they win);  design/bom.csv lines 74, 75; design/mech/thin/thin-notes.md conflict C7.
