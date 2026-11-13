# Specification: joystick nub with its frame (no bom.csv reference yet)

Design version A5, architecture section 17.8 (2026-11-10). All dimensions in mm.

## What it is
The thumb control: one rounded rectangular nub in a raised frame, at the bottom of the band, turned toward the thumb (+150 degrees). It tilts; under it four switches (SW1 up, SW3 down, SW4 toward the hand, SW5 toward the fingertip, Alps SKTAAAE010, 2.6 x 1.6 x 0.53 each) sit in a cross at 2.1 mm from the centre. A centre press is read when two opposite switches close within 40 ms. The nub with its flange is one moulded part (architecture 17.3).

## Quantity per ring
1 nub and 1 frame per ring (the frame may be part of the body: open point 2). The four switches are bought parts, not specified here.

## Material
Open: not stated in the architecture (section 16.5 says a silicone-backed insert bonded in its window, for the older design). The design partner and the maker answer (open point 1).

## Process
Open (open point 1). The nub must seal the opening (bench B9).

## Finish and colour
Open (open point 3): the design partner answers. The nub is touched by the thumb, so the maker states the skin-contact grade.

## General tolerance and tighter tolerances
General: ISO 2768-m (default, to confirm with the maker). Tighter, ISO 2768-f, on the nub outline and the frame outline, because the nub must not touch the frame (default, to confirm with the maker).

## Critical dimensions

| name | value | tolerance | where it is measured |
|---|---|---|---|
| nub, along the band | 4.6 mm | ISO 2768-f | outline at the top face |
| nub, across the band | 3.6 mm | ISO 2768-f | outline at the top face |
| frame, along the band | 6.4 mm | ISO 2768-f | outer outline of the frame |
| frame, across the band | 5.4 mm | ISO 2768-f | outer outline of the frame |
| position round the band | 150 deg | ISO 2768-m | from the top; plus is the thumb side |
| band thickness under the frame | 3.6 mm | ISO 2768-m | from 135 to 165 deg |
| switch cross radius | 2.1 mm | ISO 2768-f | centre of the nub to each switch centre |
| switch size, long side | 2.6 mm | by the maker of the switch | SKTAAAE010 |
| switch size, short side | 1.6 mm | by the maker of the switch | SKTAAAE010 |
| switch height | 0.53 mm | by the maker of the switch | SKTAAAE010 |
| cap flange thickness | 0.4 mm | ISO 2768-f | moulded under the nub |
| shell wall under the nub | 0.5 mm | ISO 2768-f | body wall that carries the opening |
| centre press window | 40 ms | not a dimension | firmware reads two opposite switches within this time |

## What to inspect
Nub and frame outline on a projector; nub height above the frame and the body surface (open: value, point 4); switch-to-nub alignment: each of the four switches must close when the nub tilts toward it (feel test on the first article); actuation force at the nub per direction against the switch's 1.6 N and 0.11 mm travel; no binding on the frame; sealing of the opening (B9).

## Ring sizes
The same nub for all sizes (US 5 to 13). The frame and opening are at 150 degrees on every size; whether the curvature under the nub changes with size is open point 5.

## Files
Drawing: design/mfg/drawings/joystick-nub.svg and joystick-nub.pdf. STEP and STL: design/mfg/parts/joystick-nub/joystick-nub.step and .stl (index.csv: exterior shape only, placed at its US 9 position, so the views show it tilted as it sits on the band; the STL is not watertight: open, parts helper).

## Open points
1. Material, process and the skin-contact grade of the nub: the design partner, with a moulding or ring maker.
2. Whether the frame is machined in the body (body.md) or a separate part: the design partner.
3. Colour and finish: the design partner.
4. Height of the nub above the frame and the body surface: the architecture does not give it for 17.8. The earlier model had 0.35 mm proud (design/mech/thin/placement.csv, joystick_cap); the design partner confirms.
5. Radius under the nub for different sizes: the design partner.
6. Bench items B6 (centre press by two switches; if centre presses misread, the nub gets a centre post and a fifth switch on a taller wall) and B9 (feel, sealing, wear) can change this part.
7. The switch cross radius is 2.1 mm in 17.3 text and the footprint is 5.8 x 5.8; at 1.9 mm the switches overlap by 0.2 mm (found by the 3D model).

## Source lines
design/architecture.md lines 430, 443, 444 (17.3); 472 (B9); 489 (17.8, wins over 17.7 line 479); design/mech/thin/thin-notes.md conflict C1.
