# Specification: band liner, resin cast, reference LNR1

Design version A5, architecture section 17.8 (2026-11-10), refreshed to the inside model v6.2 (the maker files are exported from the inside model v7) and the assembly order (architecture 17.12, 17.15, 17.22 to 17.27; assembly.md steps 8, 19, 20, 21). All dimensions in mm. -Y is the joystick side.

## What it is
A 0.3 mm skin of skin-safe resin that closes the open channel of the band (specs/body.md) on the finger side. It is cast in place in the channel over the parts (the cell, the protection circuit, the motor and the joystick head), so it is also the finger-contact surface and the inside diameter of the ring. The two flex ribbons (1.4 mm wide, 0.15 thick) are embedded in it with 0.075 mm of resin on each side, and the four charging pads (gold discs of 1.6 mm, 0.07 thick) are set in its inner face, flush (17.12, 17.15). At the joystick the resin fills under the flat ribbon head's stiffener (6.4 x 6.4 x 0.075) and a 0.1 mm strip on each side of the joystick pocket (17.26). Before the cast the floor slots, the motor window on US 7 to 9 and the joystick pocket are sealed (steps 19 and 20; see the section below Open points). Before v5 this page named the cell, the flex tails and the motor tail only.

## Quantity per ring
1 per ring, one per ring size (US 7 to 13). Sizes US 5 and 6 are out of version 1 (owner, 2026-11-11: "US 7 to 13 (Recommended)").

## Material
Default, to confirm with the maker: a skin-safe cast resin. The resin grade is open: the maker proposes one with its skin-contact certificate (open point 1).

## Process
Cast in place over the parts, as smart rings are built (architecture 17.3), after the floor slots and the motor window are sealed and the dam DAM1 is made (assembly.md steps 19, 20, 21). Mould, cure temperature and cure time are open points 2 and 3. The cell is live during the cure and must not exceed its limit: Grepow answers the limit (K-A8). Whether the ribbons can float 0.075 mm inside a single cast, or the liner must be made as a laminate first, is open (K-A5, S19, B8). Repair after casting is not possible (B8).

## Finish and colour
Surface toward the finger: smooth, no sharp edge. Colour: open point 4, the design partner answers (not stated in the architecture).

## General tolerance and tighter tolerances
General: ISO 2768-m (default, to confirm with the maker). No tighter tolerance is stated; liner thickness and inner diameter limits are open point 5.

## Critical dimensions

| name | value | tolerance | where it is measured |
|---|---|---|---|
| liner thickness | 0.3 mm | open point 5 | radial, over the whole channel |
| channel width closed by the liner | 6.8 mm | ISO 2768-f | between the two body edge walls |
| band width | 8.0 mm | ISO 2768-m | outside of the body at the same position |
| band inner diameter, US 9 | 18.95 mm | open point 5 | the finger face of the liner |
| gap, cell to shell | 0.2 mm | open point 5 | radial, inside the channel, filled by the resin or left as gap: open point 6 (more liner rows: section "What the cast fills" below) |

## What to inspect
Thickness of the liner at 6 points round the band (the finger face is the inside diameter); inner diameter with a ring gauge; no voids over the cell, no air bubble over the flex tails (visual and a 3D check if the maker has one); resin certificate and lot number; cell temperature during cure (maker's log); charge test warm-up on the first article (B8); pads flush with the inner face and free of resin (four pads, 2.4 mm apart); no resin in the joystick pocket above the dam, the cap CAP1 and its flange free; no resin through the floor slots into the block.

## Ring sizes
The liner follows the inner diameter of each size; the mould core is a ring of that diameter (US 5 and 6 are listed for reference only, they are out of version 1): US 5 15.69, US 6 16.51, US 7 17.32, US 8 18.13, US 9 18.95, US 10 19.76, US 11 20.57, US 12 21.38, US 13 22.20 mm [CALC from 11.63 + 0.8128 x size, mech-notes.md line 7].

## Files
Drawing: design/mfg/drawings/band-liner.svg and band-liner.pdf. STEP and STL, one pair per ring size, exported from the inside model v7 on the accepted exterior merged32h: design/mfg/parts/band-liner/band-liner-us7 to band-liner-us13 (.step and .stl; index.csv: 0.3 resin skin with the stiffener fill, ribbons and pads cut out). At US 9 the box is 6.8 x 19.7769 x 18.2359 and the volume 91.7212 cubic mm. The drawing band-liner.svg is the US 9 liner; the other sizes are band-liner-us7 to band-liner-us13 in the same folder (the angular extent at the shoulders: open point 7).

## Open points
1. Resin grade, supplier, skin-contact certificate: the maker proposes.
2. Mould and casting method: the maker.
3. Cure temperature and time, and what the cell and flex tails tolerate: the maker with Grepow.
4. Colour: the design partner.
5. Tolerance of the thickness and inner diameter: the maker proposes.
6. Whether the 0.2 mm gap between the cell and the shell (17.3) is filled: the design partner.
7. The angular extent of the liner and its edge shape at the shoulders: the design partner.
8. Bench item B8: resin fill, heat during charge, sealing at the two floor slots. The slot seal (with the motor window seal SEAL2 on US 7 to 9) and the dam DAM1 of the joystick pocket come BEFORE the cast (design/mfg/assembly/assembly.md steps 19 and 20; the sealant and the dam material are not chosen, open item S26).
9. Conflict K-A12 (assembly.md): the dam DAM1 is drawn standing on the liner but must exist before the liner is cast. Proposal: cast the liner in two shots, first the skin under the joystick with a removable plug filling the pocket above the stiffener, then DAM1 on that cured skin, then the rest. The mechanical designer decides (S26).
10. Conflict K-A5 (S19): the ribbons embedded with 0.075 mm of resin each side, and the windows in that skin where the cell tabs, the motor leads, the switches and the protection circuit touch the ribbon, are not proven by a single cast; no maker has built such a liner. The first bench housing measures it.
11. Whether the resin skin over the stiffener and the 0.1 mm strips beside the joystick pocket can be filled without a void (the pocket is 7.0 wide, the channel 6.8): the maker answers on the bench housing.
12. Pad flush and clean of resin: how the core presses on the four pads (assembly.md step 21, proposed): the maker.

## What the cast fills and what it must keep out (model v6.2, US 9 unless stated)
| item | value | note |
|---|---|---|
| ribbon in the liner | 1.4 x 0.15 mm, 0.075 mm of resin on each side | both ribbons; the protection circuit sits 0.075 mm from the +Y ribbon at every size (17.26) |
| charging pads | 4 discs, dia 1.6, 0.07 thick, pitch 2.4 mm along the arc | at 158.23, 172.74, 187.26 and 201.77 degrees at US 9, flush with the inner face; order VBUS, D-, D+, GND (17.12, 17.15; assembly.md step 8); the pad row stands at X = -1.0 mm (toward the hand end of the block, ring -X) so that the case pins at X = -1.0 meet the pad centres; a ring turned over in the case then has its pads 2.0 mm from the pins and VBUS never meets GND (architecture 17.28; before model v6.3 the row was at X = 0); the liner opening and the cable land (X -2.25 to 0.25, 0.45 mm beyond the pad edge all round) follow the pads |
| fill under the stiffener | stiffener 6.4 x 6.4 x 0.075 mm under the flat ribbon head | the liner fills under it; the flat switch bases stand 0.13 to 0.54 mm off the curved liner (17.24 K13, 17.26) |
| strips beside the joystick pocket | 0.1 mm wide, each side, over the pocket's length | the pocket is 7.0 mm wide from the bore to the roof, the channel 6.8 mm (17.26) |
| dam DAM1 | 0.15 mm wide round the band, 0.05 mm off the switch bases, up to the switch base tops | keeps the resin out of the pocket above it; seals its edge only (K15); wholly in the pocket in model v6; K-A12 open |
| floor slots | 2.0 x 0.6 mm at X -3.5 to -1.5, Y +-5.9 | sealed from the channel side before the cast (step 19); before v6.2 2.6 x 0.6 (17.27) |
| motor window seal SEAL2 | 0.79 to 0.81 cubic mm, about 4.0 x 1.1 mm | US 7, 8 and 9 only; same sealant and same step as the floor slots, before the cast (17.27); none on US 10 to 13 |
| cell end at the joystick | 0.10 mm from the dam | 3.50 mm around the band from the joystick centre at US 9 |

## Source lines
design/architecture.md lines 418, 433, 438, 471 (17.3, B8); 488-494 (17.8); 17.12, 17.15, 17.22 to 17.27 (the newest; they win); design/mfg/assembly/assembly.md steps 8, 19, 20, 21 and conflicts K-A2, K-A3, K-A5, K-A8, K-A12; design/mech/thin/thin-notes.md sections "Model v6, continued" and "Model v6.2"; design/bom.csv line 76; design/mech/mech-notes.md line 7.
