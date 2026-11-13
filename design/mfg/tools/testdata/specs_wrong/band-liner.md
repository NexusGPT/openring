# Specification: band liner, resin cast, reference LNR1

Design version A5, architecture section 17.8 (2026-11-10). All dimensions in mm.

## What it is
A 0.3 mm skin of skin-safe resin that closes the open channel of the band (specs/body.md) on the finger side. It is cast in place over the parts in the channel (cell, flex tails, motor tail), so it is also the finger-contact surface and the inside diameter of the ring.

## Quantity per ring
1 per ring, one per ring size (US 5 to 13).

## Material
Default, to confirm with the maker: a skin-safe cast resin. The resin grade is open: the maker proposes one with its skin-contact certificate (open point 1).

## Process
Cast in place over the parts, as smart rings are built (architecture 17.3). Mould, cure temperature and cure time are open points 2 and 3. The cell must not exceed its limit during cure: Grepow answers the limit. Repair after casting is not possible (B8).

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
| gap, cell to shell | 0.2 mm | open point 5 | radial, inside the channel, filled by the resin or left as gap: open point 6 |

## What to inspect
Thickness of the liner at 6 points round the band (the finger face is the inside diameter); inner diameter with a ring gauge; no voids over the cell, no air bubble over the flex tails (visual and a 3D check if the maker has one); resin certificate and lot number; cell temperature during cure (maker's log); charge test warm-up on the first article (B8).

## Ring sizes
The liner follows the inner diameter of each size: US 5 15.69, US 6 16.51, US 7 17.32, US 8 18.13, US 9 18.95, US 10 19.76, US 11 20.57, US 12 21.38, US 13 22.20 mm [CALC from 11.63 + 0.8128 x size, mech-notes.md line 7].

## Files
Drawing: design/mfg/drawings/band-liner.svg and band-liner.pdf. STEP and STL: design/mfg/parts/band-liner/band-liner.step and .stl (index.csv: 0.3 mm resin skin as modelled; this STEP is the older 3D-model state, a 300 degree arc, bbox 6.8 x 19.55 x 18.24, not yet the 17.8 state: open point 7).

## Open points
1. Resin grade, supplier, skin-contact certificate: the maker proposes.
2. Mould and casting method: the maker.
3. Cure temperature and time, and what the cell and flex tails tolerate: the maker with Grepow.
4. Colour: the design partner.
5. Tolerance of the thickness and inner diameter: the maker proposes.
6. Whether the 0.2 mm gap between the cell and the shell (17.3) is filled: the design partner.
7. The angular extent of the liner and its edge shape at the shoulders: the design partner.
8. Bench item B8: resin fill, heat during charge, sealing at the two floor slots.

## Source lines
design/architecture.md lines 418, 433, 438, 471 (17.3, B8); 488-494 (17.8); design/bom.csv line 76; design/mech/mech-notes.md line 7.
