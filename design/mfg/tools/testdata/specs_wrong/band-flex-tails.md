# Specification: the two band flex tails, references FLEX1 (thumb side) and FLEX2 (other side)

Design version A5, architecture section 17.8 (2026-11-10). All dimensions in mm.

## What it is
Two flexible printed circuits that leave the main board through slots in the block's floor, one into each shoulder, and run inside the band channel.
- FLEX1, thumb side: carries the vibration motor, the record switch SW2 and the four joystick switches SW1, SW3, SW4, SW5 (17.8). Section 17.3 gave 5 switch lines and ground for the switches.
- FLEX2, other side: carries the cell (2 lines), the cell's temperature sensor (1 line) and the four charging pads VBUS, D-, D+, GND (17.8; 17.3 had the motor here too).
Line counts per tail after the 17.8 move of the motor are open point 1. The solder pads on the main board are J_BAND_A (FLEX1) and J_BAND_B (FLEX2).

## Quantity per ring
2 per ring: 1 FLEX1 and 1 FLEX2. The two tails differ.

## Material
Default, to confirm with the maker: polyimide base with two copper layers. Stack-up details (copper weight, coverlay, adhesive): open point 2.

## Process
Flexible printed circuit, two layers, with a stiffener at the solder ends (the stiffener is not stated: open point 2). Soldering of the motor tail, the cell tab and the pads, and who does it: open point 3 (bom.csv line 75).

## Finish and colour
Pad finish and coverlay colour: open point 2 (the architecture does not state them).

## General tolerance and tighter tolerances
General: ISO 2768-m for the outline (default, to confirm with the maker). Copper tolerances: the flex maker's own, open point 2.

## Critical dimensions

| name | value | tolerance | where it is measured |
|---|---|---|---|
| flex thickness (radial stack allowance) | 0.15 mm | open point 2 | whole tail, as built |
| liner thickness over the tail | 0.3 mm | open point 2 | radial stack above the flex |
| block floor slot count | 2 | not a dimension | one slot per tail, in the block floor |
| switch pad group count, FLEX1 | 4 | not a dimension | four joystick switches plus the record switch on the same tail |
| charging pad count, FLEX2 | 4 | not a dimension | VBUS, D-, D+, GND |
| charging pad diameter | 1.0 mm | ISO 2768-f | pad on the outside of the band |
| charging pad X positions | 0.8 mm | ISO 2768-f | pads at X = -2.4, -0.8, +0.8, +2.4 |
| charging pad angle | 150 deg | ISO 2768-m | at -150 deg from the top |
| joystick position | 150 deg | ISO 2768-m | switches under the nub at +150 deg |
| record switch position | 88 deg | ISO 2768-m | SW2 at +88 deg |
| motor position | 49 deg | ISO 2768-m | on the thumb side shoulder; motor 7.0 diameter x 2.1 |
| cell end near the protection circuit | 30 deg | ISO 2768-m | cell starts at -30 deg |
| cell end at the joystick side | 133 deg | ISO 2768-m | cell ends at +133 deg |

Length, width and path of each tail are open point 4: the architecture gives none. The 3D model (design/mech/thin/thin-notes.md, an older state) uses width 2.2 and the floor slot 2.6 x 0.6 at Y = +-5.9, X = -4.7, because only 2.2 mm of width is free between the motor pocket and the shoulder cavity.

## What to inspect
Outline; layer count and thickness; continuity of every line on the tail (electrical test of all lines, 100 percent); no short between lines; bend test at the shoulder radius of the band (the tail must lie in the channel: the mechanics helper supplies the bend radius); the pad solder test; cleanliness at the soldered ends.

## Ring sizes
The path length of each tail changes with the ring size (the band diameter changes, US 5 to 13); the block-side end does not. Length per size: open point 4.

## Files
Drawing: design/mfg/drawings/flex-tail-thumb.svg and .pdf (FLEX1), design/mfg/drawings/flex-tail-away.svg and .pdf (FLEX2). STEP and STL: design/mfg/parts/flex-tail-thumb/flex-tail-thumb.step and design/mfg/parts/flex-tail-away/flex-tail-away.step (and .stl). These are 3D-model shapes of an older state (index.csv: thumb 6.6 x 4.1 x 15.04, away 2.2 x 0.15 x 1.4), not a flat pattern: a maker needs the flat outline, open point 4.

## Open points
1. Line count per tail after the motor moved to the thumb side: the electronics designer (thin-sch helper) answers.
2. Stack-up, copper weight, coverlay, stiffener, pad finish, tolerances: the flex maker proposes.
3. Who solders the motor tail, the cell tab and the pads, and in which order against the resin cast: the design partner and the flex maker.
4. Outline drawing, widths, lengths per size, bend radii, slot size: the mechanics step supplies the path through the band; the design partner answers (bom.csv lines 74 and 75: "no drawing exists").
5. Pad pitch and position at the floor slot on the main board: the PCB layout step.

## Source lines
design/architecture.md lines 435, 439 (17.3), 489-494 (17.8, wins over 17.7); design/bom.csv lines 74, 75; design/mech/thin/thin-notes.md conflict C7.
