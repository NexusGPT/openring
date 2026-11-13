# Microphone sound path (review finding F02)

Design commit fc4ccef, working tree of 2026-11-11. Inside model v4 (`design/mech/thin/`), exterior `design/look/s1/out/ring-merged32e.step`. Axes and units are the inside model's: X along the finger (+X fingertip), Y across (-Y is the joystick side, where the thumb works), Z up, origin at the centre of the block's underside, mm (`design/mech/thin/thin-notes.md` line 5; architecture.md line 536). Brought to the decisions of 2026-11-13 (membrane, gasket, items 73, 74, 77, 78) in section 1 and section 5 rows 2, 6, in sections 7 to 10 and in the changes of section 9 items 2, 19, 20; the rest of the page is the study as written on 2026-11-11.

architecture.md changed on disk at 00:37 during this run (another helper; 644 lines). Its line numbers here are re-checked against that version (`evidence/arch-lines-recheck.log`).

Source tags: `check.log Cnn` is the line of `design/mech/mic-path/check.log` that starts with that tag. `acoustic.log` and `board-conflicts.log` are in this folder. Datasheet copies are in `datasheets/` here (copied from the research run's saved files, hashes in `evidence/datasheet-copies-sha256.log`). [ESTIMATE] marks a figure with no maker source.

## 1. Answer

- Part: **Knowles SPK0641HT4H-1**, a top-port PDM microphone, 4.00 x 3.00 x 1.00 mm. It replaces the Infineon IM68D128B, which is bottom port and has no path to the room in this block.
- Place: both microphones on the board's under face (the face the parts already use), on the joystick side strip, port facing down (-Z). U5 at X -10.8, U6 at X +10.8, both at Y -4.8.
- Path: port, then a foam gasket ring (bore 1.0), then a 1.0 mm hole straight down through the block's floor, then a membrane (a disc of woven acoustic mesh, Saati Acoustex 010a, on a ring of tesa 61305 film; keeps dust and splashes out, no water rating claimed for version 1) in a 2.0 mm seat flush with the block's underside. The sound enters from the gap between the block's underside and the back of the finger. Path length 0.43 mm, one straight bore.
- No opening in any side wall. That removes conflict K8 (slots on the thumb's side). The two present wall slots go.
- Fit: `check_mic_path.py` ends `RESULT PASS` (check.log, last line).
- Cost: SNR 64.5 dB(A) against 67.5 dB(A); 0.63 mA against 0.58 mA per microphone; a 0.10 mm pocket in the floor under each microphone; a gasket chosen per unit from three thicknesses (section 8).

## 2. The defect and the fixed limits

- The IM68D128B is bottom port: "Port location Bottom port" (`design/datasheets/mic-research/im68d128b-brief.txt` line 24), port "ø0.325 thru" (same file, line 37), package "3.5 x 2.65 x 0.98 mm" (line 25).
- The model draws a port "in the can's -Y wall at the body slot" (`design/mech/thin/placement.csv` lines 11 and 12; `design/mech/thin/thin.py` lines 270 to 280). The part has no such port.
- Board top face: covered by the foam frame (0.10 thick, 1.2 wide round the edge, placement.csv line 16; thin-notes.md line 25) and the screen. A hole through the board opens into that closed 0.10 mm layer (option (a), section 7).
- Room under the board: part tops at Z 1.430, floor top at Z 0.400, so 1.03 mm (check.log C02).
- Block shape kept as the owner's: 29.3 x 14.75 mm, 3.85 at the centre line, 2.95 at the long edges (architecture.md, "Key numbers", and 17.15). Nothing in this study makes the block thicker or wider.

## 3. The part

Datasheet copy: `datasheets/knowles-spk0641ht4h-1_chipsmall.pdf` and its text `datasheets/knowles-spk0641ht4h-1_chipsmall.txt` (a third-party host's copy of Knowles "Datasheet SPK0641HT4H-1 Rev A", 2016, text line 57; source URL in `design/parts/research-microphone-port.md` section 2). Page 7 of the PDF (sheet 6) is rendered to `evidence/pages/knowles-spk0641ht4h-1_chipsmall-p7.png`.

| Item | Value | Source |
|---|---|---|
| Maker and part number | Knowles SPK0641HT4H-1 (the number printed on the datasheet; the reel suffix and the distributor code are not confirmed) | text line 30 |
| Port position | top port: "top port silicon digital microphone" | text line 30 |
| Port size | Ø0.25 ±0.05 | text line 348 |
| Port place on the lid | centre 1.500 from the long side (so on the centre line of the 3.00 width) and 1.030 from one short end; Ø0.510 ring round it | drawing on sheet 6, `evidence/pages/knowles-spk0641ht4h-1_chipsmall-p7.png` (read from the image; the text copy has no drawing labels) |
| Package L x W x H | 4.00 ±0.10 x 3.00 ±0.10 x 1.00 ±0.10 | text lines 345 to 347 |
| Gasket and case hole advice | "the recommended Gasket Cavity Diameter is D ≥ 1.0mm and the recommended Case Hole Diameter is 1.0 ≤ D ≤ 1.5mm" | text lines 369 to 370 |
| Supply | 1.6 / 1.8 / 3.6 V | text line 74 |
| Clock, normal mode | 1.000 to 4.800 MHz (the ring's 1.280 MHz, architecture.md line 110, is inside) | text line 95 |
| Current at 1.8 V | 630 typ, 710 max µA | text line 97 |
| Sensitivity | -26 dBFS typ (-27 to -25) at 94 dB SPL | text line 100 |
| SNR | 64.5 dB(A) | text line 102 |
| Acoustic overload | 120 dB SPL | text line 105 |
| Low-power mode | clock 350 to 800 kHz, 230 µA typ at 1.8 V | text lines 121 and 123 |
| Ingress rating | none in the copy: the search for IP ratings, water, dust and ingress hit only the words "industrial" and "industry" (lines 9, 13, 484) | `evidence/ingress-search.log` |

Why this part over the other three top-port candidates of the research (all copies in `datasheets/`):
- Knowles SPK0838HT4H-B: same 4.00 x 3.00 x 1.00 ±0.10 (`knowles-spk0838ht4h-b_eicom.txt` line 271 and `evidence/pages/knowles-spk0838ht4h-b_eicom-p7.png`), lower current 500 µA (line 55), but SNR 64 dB(A) (line 9), clock 1.0 to 3.25 MHz (line 101), no low-power mode table, port 1.220 from the end (page image). It is the drop-in second source: same outline, different pin order (line 276 to 285: 1 VDD, 2 SELECT, 3 CLOCK, 4 DATA).
- Gettop WD-GFA261-H10F: 4.0 x 2.0 x 1.1 ±0.1 (`gettop-wd-gfa261-h10f_szlcsc.txt` lines 465 and 38). It is 0.07 mm too tall for the room under the board (check.log C29 lines "4.0x2.0x1.1"); at its maximum 1.2 the floor under it would be 0.23, under the 0.30 rule (R4, section 6).
- Knowles SPG08P4HM4H-1: height not verified (research-microphone-port.md section 2). Not used.

## 4. Where the two microphones sit

From check.log C10.mic_1 and C10.mic_2 (positions are the design; the check reads them from its own table and tests them):

| Ref | Body X | Body Y | Body Z | Centre | Board face | Port |
|---|---|---|---|---|---|---|
| U5 (mic_1) | -12.800 to -8.800 | -6.300 to -3.300 | 0.430 to 1.430 | (-10.800, -4.800, 0.930) | under face (toward the floor), pads up | faces -Z, at X -11.770, Y -4.800 (toward the hand end of the part) |
| U6 (mic_2) | 8.800 to 12.800 | -6.300 to -3.300 | 0.430 to 1.430 | (10.800, -4.800, 0.930) | under face, pads up | faces -Z, at X 11.770, Y -4.800 (toward the fingertip end of the part) |

Length 4.00 along X, width 3.00 along Y. The ports are 23.54 mm apart along X [CALC: 11.770 x 2], against 22 mm today (architecture.md line 353). Each part is turned so its port end faces its own block end.

Why not the +Y side (away from the thumb): at X -11 the antenna stands at X -13.5 to -11.9, Y 2.8 to 6.0 [CALC: x -12.7 and y 4.4 with size 1.6 x 3.2], and at X +11 the coil L72 sits at Y 2.4 to 4.0 [CALC: y 3.2, size 1.6] (placement.csv lines 13 and 7); a 3.0 wide part needs Y 3.3 to 6.3 there. The ports face down, so the side does not matter for the thumb (section 5).

## 5. The path, piece by piece (inside to outside)

| Piece | What | Size | Held by | Source |
|---|---|---|---|---|
| 1 Port | Ø0.25 hole in the part's lid | lid face at Z 0.430 nominal | the part | section 3; check.log C10 |
| 2 Gasket | ring of Nitto SCF foam (AN010 0.10 mm, SCF400T 0.2 mm, SCF400 0.3 mm), no adhesive | OD 1.80, bore 1.00, fills the gap from the pocket bottom (Z 0.300) to the lid: 0.13 nominal, 0.03 with the tallest part, 0.23 with the shortest | centred on the hole and held against the pocket floor by the microphone's lid when the board goes in | sizes: check.log C16, C19, C20; the three thicknesses are start values (Nitto's sheets with the compression values could not be downloaded), bench B7 measures the leak |
| 3 Floor pocket | flat pocket in the floor's top face under each part | U5: X -13.000 to -8.600, Y -6.450 to -3.100; U6: X 8.600 to 13.000, same Y; 0.10 deep, floor left 0.30 | machined in the body | check.log C17, C18 |
| 4 Hole | straight round hole through the floor, not plated, no thread | Ø1.00, from Z 0.10 to 0.30 (0.20 long) at the port's X and Y | machined | check.log C21, C24 |
| 5 Membrane seat | counterbore from the underside, coaxial | Ø2.00 x 0.10 deep (Z 0 to 0.10) | machined | check.log C24, C26 |
| 6 Membrane | disc of woven acoustic mesh, Saati Acoustex 010a (52 um thick, pores 78 um), bonded with a ring of tesa 61305 film (50 um; 2.0 mm outside, 1.0 mm bore), flush with the underside | Ø2.00; stack 0.102 mm in the 0.10 mm seat; the builder cuts mesh and film with punches of 2.0 and 1.0 mm | bonded in the seat | no catalogue vent of 0.10 mm or less with adhesive exists in any maker document found (the thinnest Gore parts are 0.18 to 0.26 mm; the BOM's Gore GAW112 cut is 0.24 thick); bench B7 measures the sound loss through bore, gasket and mesh on the first ring |
| 7 Opening to the room | the 1.0 mm open centre of the membrane seat, on the block's underside | at X -11.770 and +11.770, Y -4.800 | | check.log C25 |

Channel: one straight vertical bore of 1.00 mm, 0.43 mm long from lid to underside (check.log C24). Its walls: foam (gasket part) and metal (hole part).

Metal round it: 0.40 mm of metal at 0.4 mm beyond the seat edge all round, before any other cut (check.log C26, rule R3). The ring between the seat and the pocket, from Ø1.0 to Ø2.0, is 0.20 thick (check.log C26w). That is under the 0.30 stack floor of R4 in that ring only. No project rule covers a local web; the body maker must accept it (open item O3). It stays (ring from 1.0 to 2.0 mm) as a stated local exception to the 0.30 mm floor rule; on the first body the thickness through the pocket is measured at 4 points with a micrometer, pass 0.17 to 0.23 mm, and a body outside that is scrapped (item 77).

The opening and the finger: the underside faces the back of the finger. With the finger taken as a cylinder of the bore (18.95 mm), the air gap under each hole is 1.706 mm, and 0.400 mm on the centre line (check.log C27) [ESTIMATE: a real finger is not a cylinder]. The gap is open to the room along both long edges.

The thumb (conflict K8): there is no opening in a side wall. The openings are 11.770 mm along X from the joystick nub's centre (nub at X 0, 3.6 along X: placement.csv line 25), so 9.97 mm from the nub's edge [CALC: 11.770 - 1.8]. Whether the thumb or the next finger covers them in use is [ESTIMATE] and goes to bench B7.

Mounting order: gasket and membrane bonded into the body first; the board with the parts then goes in from the top, as today; the lids press the gaskets.

## 6. Fit proof

Command (run from any folder):

`nice -n 19 design/.venv/bin/python design/mech/mic-path/check_mic_path.py`

Output saved as `check.log`; the run's exit code is in `evidence/check-final-exit.log`.

Rules used, quoted:
- R1: `check_thin.py` line 25 `LIMIT = 0.001` with line 63 `if v > LIMIT:` (no two parts share more than 0.001 mm3). Here applied to boxes at the part's maximum size (4.10 x 3.10 x 1.10), against every row of placement.csv (rows turned about X use a box round their turned outline).
- R2: architecture.md line 381: "Parts with a 0.2 mm keep-out".
- R3: `check_thin.py` line 26 `WALL_MIN = 0.40`.
- R4: `check_thin.py` line 8: "the floor is at least 0.30", and the test at its line 161 that no under-board part lies below the floor top.
- R5: `thin.py` line 366: the interior pocket is the screen outline plus 0.1 (27.45 x 12.9; check.log C03).
- D1, D2: the SPK0641HT4H-1 gasket cavity and case hole advice (text lines 369 to 370). D3: PUI guide text lines 112 to 113, hole and gasket at least 0.1 larger than the part's port.

Results (check.log):
- C11, C12: largest overlap 0.0000 mm3 for both parts.
- C13: least plan gap 0.200 mm for U5 (to the recording light LED1 and to the storage part U3, both exactly at the 0.2 rule), 1.050 mm for U6 (to the coil L10).
- C14, C15: inside the interior pocket with 0.100 mm margin at maximum size; nominal outline inside the board outline and its 0.8 corner.
- C16, C17: lid to pocket bottom 0.130 nominal, 0.030 and 0.230 at the height limits; floor under the pocket 0.300. A part at its maximum height would sit 0.070 below the plain floor top, so the pocket is needed.
- C18: pocket to the nearest floor slot 5.100 mm.
- C19 to C23: gasket on the lid with 0.130 margin; D1, D2, D3 met; gasket bore equals the hole.
- C25, C26: under each hole the body's underside is at Z 0.0 with air below; metal round the seat.
- Last line: `RESULT PASS`.

What the check does not cover: parts not in placement.csv (the 0201 parts of the board file, see `board-conflicts.log`); the box test is coarse for turned band parts but they are all within X -3.4 to +3.4 and the microphones start at |X| 8.8.

Larger parts at today's place (centre X ±11.0, Y -5.125), check.log C29:
- 4.0 x 3.0 x 1.0, length along X: X -13.000 to -9.000, Y -6.625 to -3.625. It passes the interior wall (Y -6.450) by 0.175 mm, so it cuts into the -Y wall, and U5 touches LED1 (plan gap 0.000, rule 0.2). To fit: move the centre to Y -4.8 (0.325 toward +Y) and U5's centre to X -10.8 (0.2 toward the fingertip). That is the recommended place.
- 4.0 x 3.0 x 1.0, length along Y: past the wall by 0.675 mm.
- 4.0 x 2.0 x 1.1 (Gettop), length along X: inside the walls, but 0.070 mm below the floor top, and U5 touches LED1 (0.000).
- 4.0 x 2.0 x 1.1, length along Y: past the wall by 0.675 mm and 0.070 below the floor top.

## 7. Options rejected, and the second best

| Option | Works? | Measured reason |
|---|---|---|
| (a) Bottom-port IM68D128B, hole through the board to the top face | No | The board's top face is under the foam frame and the screen; the hole opens into the closed 0.10 mm foam layer (placement.csv line 16, foam 0.10). To reach the room a channel 0.10 high would have to cross the 0.15 mm gap between the board edge (Y 6.300) and the interior wall (Y 6.450) (check.log C03) with nothing under it, then pass the wall. Architecture.md line 347 says the same: "bottom port up through the board is not possible under the screen". |
| (b) Bottom-port part with a lateral channel | No | The port faces the board. Between part and board there is only the 0.02 pad (thin.py line 38, pad_t) and the solder ring, which is the acoustic seal (PUI guide text lines 178 to 179). A channel would have to be cut inside the 0.30 mm board (bom.csv line 52, which then said 6-layer; the board has 4 copper layers since the board plan); no maker source gives such a board. The present model's side port does not exist on the part (`im68d128b-brief.txt` line 24). |
| (c) Top-port part facing the floor | Yes: recommended | Straight Ø1.0 bore of 0.43 mm (check.log C24); fit `RESULT PASS`. Needs the 0.10 pocket (C17). |
| (d) Top-port part facing a side wall or an end wall | No | The port faces a wall only if the part stands on its edge. That needs 3.00 (4.0 x 3.0 part) or 2.0 (4.0 x 2.0 part) of height; the room under the board is 1.03 (check.log C02): short by 1.97 and 0.97 [CALC]. |
| (e) Top-port part facing the floor, with a slit under the lid to the end wall | Fits, second best | Slit 0.6 wide [ESTIMATE width], 0.130 high (0.030 to 0.230 with the part's height), 2.025 long: 1.455 in the pocket plus 0.570 through the end wall at Z 0.35 (check.log C30). Its flow resistance is 1052 times the bore's at nominal height and 85618 times with the tallest part; quarter-wave 42 kHz (acoustic.log) [ESTIMATE]. Kept as the path if bench B7 shows the underside opening is covered by the finger. |
| (f) Today's wall slots with the IM68D128B | No | The part has no side port (`im68d128b-brief.txt` line 24). |
| (g) Gettop WD-GFA261-H10F in (c) | No | 1.1 ±0.1 tall: at maximum it needs the floor at 0.23 (section 3), under R4 0.30. |
| (h) Openings in the +Y wall | No | No room for a 3.0 wide part on the +Y strip at X ±11 (section 4), and a slit to a wall is option (e) with a longer run. |

## 8. Acoustic figures

Against the guidance on file:

| Guidance | Source | This design |
|---|---|---|
| Gasket cavity at least 1.0 | SPK0641HT4H-1 text line 369 | 1.00 (check.log C20) |
| Case hole 1.0 to 1.5 | same, lines 369 to 370 | 1.00 (C21) |
| Hole and gasket channel at least 0.1 larger than the port | PUI guide lines 112 to 113 | 1.00 against 0.40 (C22) |
| Gasket as close as possible to the size of the outer hole, to avoid a resonating chamber | PUI guide lines 101 to 103 | equal, 1.00 (C23) |
| Channel as short as possible | PUI guide line 96 | 0.43 (C24) |
| Gasket fully compressed | PUI guide lines 92 to 93 | gasket chosen per unit (below) |

Estimates (`acoustic.log`, every line [ESTIMATE], textbook lumped formulas):
- Quarter-wave resonance of the bore: 100 kHz, far above the 8 kHz the 16 kHz recording keeps.
- Viscous layer: 0.069 mm at 1 kHz, 0.024 mm at 8 kHz; small against the 0.5 mm bore radius, large against the slit of option (e).
- Leak: the inside air of the block (taken as 250 mm3) has 7.31 times the bore's impedance at 1 kHz and 0.11 times at 8 kHz. So an open leak at the gasket would cut the high frequencies: the gasket must seal.

Gasket thickness per unit [start values, all three numbers; Nitto SCF AN010, SCF400T, SCF400, item 74; not settled by a document]: after reflow, measure the lid height below the board's under face, compute the gap g = lid Z - 0.300, and choose a gasket of free thickness 0.10 (g under 0.07), 0.20 (g 0.07 to 0.14) or 0.30 (g over 0.14), so it is compressed by about 25 to 70 percent. Reason: the part's own height tolerance is ±0.10 (text line 347), so g runs from 0.030 to 0.230 (check.log C16) and no one foam covers that.

Bench test B7 (architecture.md line 399, "Side-ported microphones behind a wall slot") must change to this path and settle: response and level through bore, gasket and membrane against a bare part; the leak with each gasket class; wind noise at the underside; the finger and the thumb covering the openings while worn (closed as a measurement of the build guide, item 78: a ring on a rod of the finger's diameter, a loudspeaker at 1 m, level with the openings free, then with a finger pad and a thumb pad on them; pass: the level falls by at most 3 dB, the noise budget of line 203; above 3 dB the result goes to the owner: the openings have no better place on this ring); the membrane's loss (the BOM's 2 dB figure was for the GAW112, bom.csv line 58, which is no longer the membrane: Saati Acoustex 010a, item 73).

## 9. Changes other files need (not made here)

One line each: file and line, the present text (shortened), the change.

1. design/architecture.md line 41, "| Microphone x2 | IM68D128B (order code IM68D128BV01XTMA1 ...) | Infineon | 3.5 x 2.65 x 0.98 | 68 dB(A), bottom port, PDM, 1.62 to 3.6 V, 0.58 mA |": Knowles SPK0641HT4H-1, 4.00 x 3.00 x 1.00, 64.5 dB(A), top port, PDM, 1.6 to 3.6 V, 0.63 mA.
2. design/architecture.md line 60, "| Microphone seal | GAW112 membrane, custom die-cut, 1.6 mm outer, 0.8 mm inner | Gore | 0.24 thick |": membrane disc Ø2.0 (Saati Acoustex 010a mesh on a tesa 61305 ring, 0.102 in the 0.10 seat; this supersedes the 'at most 0.10 thick' of this line, item 73), in the underside seat; plus a gasket row (foam ring OD 1.8, bore 1.0, three thicknesses).
3. design/architecture.md line 105, "4 microphones, bottom port, on the underside of the board": 2 microphones, top port, port down through the floor (section 5 still describes A3).
4. design/architecture.md line 347, "each microphone ports sideways through a 1.4 x 0.4 mm slot in the -Y wall by a moulded gasket channel": each microphone ports down through a 1.0 mm hole in the floor, gasket and membrane (this file).
5. design/architecture.md line 353, "2 x Infineon IM68D128B (3.5 x 2.65 x 0.98), 22 mm apart on the X axis": 2 x Knowles SPK0641HT4H-1 (4.00 x 3.00 x 1.00), ports 23.54 mm apart.
6. design/architecture.md line 385, "microphones 2 x 0.58 mA at 1.8 V": 2 x 0.63 mA (text line 97).
7. design/architecture.md line 399, "| B7 | Side-ported microphones behind a wall slot | bench |": top-port microphones over a floor hole: response, gasket leak, wind, finger cover.
8. design/architecture.md line 422, "Openings: 2 microphone slots 1.2 x 0.3 mm in the block's wall away from the thumb, at X = -11 and +11.": 2 sound holes Ø1.0 in the block's underside at X -11.77 and +11.77, Y -4.8, each with a Ø2.0 x 0.10 membrane seat; no microphone slot in any wall.
9. design/architecture.md line 426, "parts under the board 1.00 (coil 1.0, microphones 0.98, storage 0.75)": microphones 1.00 ±0.10, with a 0.10 pocket in the floor under each.
10. design/architecture.md line 461, "2 microphones IM68D128B": 2 microphones SPK0641HT4H-1 (section 17.x to be added).
11. design/architecture.md line 509, "2 microphones behind wall slots": 2 microphones over floor holes.
12. design/architecture.md line 518, "and the microphone slots, which today sit on the joystick side where the thumb works": remove the slots; add the floor pockets, holes and seats.
13. design/architecture.md line 570, "Its sound path through the board is decided with the inside model and the board (review finding F02).": decided: top-port SPK0641HT4H-1 through the floor (this file); F02 closed when the files below change.
14. design/bom.csv line 9 (U5, U6), "Infineon,IM68D128BV01XTMA1,PG-LLGA-5 class (3.5 x 2.65 x 0.98)": Knowles, SPK0641HT4H-1, 8-pad LGA 4.00 x 3.00 x 1.00, top port Ø0.25, source this folder's datasheet copy.
15. design/bom.csv line 36 (C31, C32), "same rule kept for the IM68D128B, which has no saved datasheet": source SPK0641HT4H-1 text lines 230 to 231, "Bypass capacitors should be placed next to each" microphone's Vdd pin.
16. design/bom.csv lines 37 and 38 (C35, C36, R31, R32), "same rule kept for IM68D128B" and "datasheet of the removed IM73D122": keep the parts; source to the SPK0641HT4H-1 copy or mark as design choice.
17. design/bom.csv line 52 (PCB1), "sound holes: none (microphones port sideways)": sound holes: none (top-port microphones port down through the floor).
18. design/bom.csv line 54 (HSG1), "openings: 2 microphone slots 1.2 x 0.3": 2 floor pockets (4.4 x 3.35 x 0.10), 2 holes Ø1.0, 2 seats Ø2.0 x 0.10 on the underside; no microphone slots.
19. design/bom.csv line 58 (MEM1, MEM2), "acoustic membrane over each of the 2 slots in the block wall ... 1.6 outer, 0.8 inner, 0.24 thick": disc Ø2.0, over each floor hole; superseded by item 73 of 2026-11-13: Saati Acoustex 010a mesh on a ring of tesa 61305, no Gore part (no Gore catalogue vent is 0.10 mm or less).
20. design/bom.csv line 59 (GSK2, GSK3), "moulded gasket channel from each microphone's side port to its slot in the wall ... 0.6 mm tall": foam ring OD 1.8, bore 1.0, three free thicknesses 0.10, 0.20, 0.30 (the PSA of both faces is superseded by item 74 of 2026-11-13: Nitto SCF AN010, SCF400T, SCF400, no adhesive).
21. design/mech/thin/placement.csv line 11, "mic_1,U5,board,-11.000,-5.125,0.940,3.500,2.650,0.980,...port hole dia 0.35 in the can's -Y wall at the body slot": mic_1,U5,board,-10.800,-4.800,0.930,4.000,3.000,1.000, SPK0641HT4H-1, top port Ø0.25 on the lid facing -Z at X -11.77.
22. design/mech/thin/placement.csv line 12 (mic_2, same text at X 11.000): mic_2,U6,board,10.800,-4.800,0.930,4.000,3.000,1.000, port at X 11.77.
23. design/mech/thin/thin.py lines 270 to 280 (substrate and can with a hole in the -Y wall) and line 369, `cav.append(box(1.2, 1.6, 0.3, mx, -7.375 + 0.5, ZTOP - 0.2 - 0.39))    # mic ports`: new part solids; cavities: pocket, hole, seat (section 5) in place of the wall slots. thin.py line 197 `ZTOP` stays.
24. design/mech/thin/thin-notes.md line 92, "K8 Microphone slots at Y -7.375 are on the -Y wall, the joystick side, where the thumb works": resolved by this file; no wall opening.
25. design/look/s1/exterior.py line 50, `MIC_W, MIC_H, MIC_DEPTH, MIC_Z, MIC_XS = 1.4, 0.4, 0.3, V["mic_z"], (-11.0, 11.0)`, and lines 98 to 103 (slot and 0.06 mesh in the -Y wall): remove the wall slots; add two Ø1.0 holes with Ø2.0 x 0.10 seats on the underside at (±11.77, -4.8). Another helper owns this file.
26. design/ecad/ring/sch-notes.md line 34, "U5 and U6 IM68D128B (pins CLOCK P1, VDD P2, GND P3, DATA P4, SELECT P5; numbers provisional)": SPK0641HT4H-1 pins 1 DATA, 2 CLOCK, 3 SELECT, 4 Vdd, 5 to 8 GROUND (text lines 351 to 359); nets unchanged: CLOCK on MIC_A_CLK, DATA through R31 or R32, SELECT of U5 on ground and of U6 on VDD_MIC, Vdd on VDD_MIC, all four GROUND pins on ground ("All Ground pins must be connected to ground", text line 228).
27. design/ecad/ring/sch-notes.md line 63, "U5, U6 IM68D128B: 5 pins each ... P1 to P5 are placeholders": 8 pins, numbers from the datasheet copy.
28. design/ecad/ring/make_netlist.py lines 73 to 76 (`SYM['IM68D128B'] = [('P1', 'CLOCK', ...), ...]`) and line 244 (`part(u, 'IM68D128B', ...)`): new symbol with the 8 pins above.
29. design/ecad/ring/parts.csv lines 44 and 48, "U5,IM68D128B,IM68D128B,IM68D128BV01XTMA1,ring:Infineon_IM68D128B_3.5x2.65": SPK0641HT4H-1 and a 4.00 x 3.00 footprint.
30. design/ecad/ring/check_netlist.py lines 241 to 246 (checks P1 CLOCK, P5 SELECT, P2 VDD, P3 GND of the IM68D128B): the new pin numbers.
31. design/ecad/ring/pcb/build_board.py lines 224 to 229 (provisional IM68D128B footprint, 5 pads in a row): the land pattern of sheet 6 (`evidence/pages/knowles-spk0641ht4h-1_chipsmall-p7.png`), U5 at (-10.8, -4.8) and U6 at (10.8, -4.8).
32. design/ecad/ring/pcb/check_board.py lines 22 to 24, "U5, U6 body hangs 0.15 mm over the -Y edge": the exception goes; the new outlines are on the board (check.log C15).
33. design/ecad/ring/pcb/placement-report.csv: R31 and R32 lie inside the new outlines; Q2 and R72 in the 0.2 keep-out of U6 (`board-conflicts.log`). They move.
34. design/firmware.md line 15, "two Infineon IM68D128B": SPK0641HT4H-1; sensitivity -26 dBFS (text line 100) against -37 dBFS (`im68d128b-brief.txt` line 12): 11 dB more digital level for the same sound, so the gain stage changes [CALC: -26 - (-37)].
35. design/bench/bench-plan.md line 83, "sound through a slot in a metal wall is bench test B7": sound through the floor hole, gasket and membrane.

## 10. Open items and limits

- O1 Orderable code and stock of the SPK0641HT4H-1: not checked (no web request in this run). Knowles or a distributor must answer. The SPK0838HT4H-B is the same outline as a second source, with another pin order.
- O2 Gasket material: Nitto SCF family (item 74); the three thicknesses are start values, bench B7 settles them.
- O3 The 0.20 mm metal ring under each membrane seat (check.log C26w): the body maker must accept it.
- O4 Membrane: Saati Acoustex 010a on a ring of tesa 61305 (item 73); bench B7 measures its sound loss. Version 1 claims no water rating.
- O5 Whether the finger, the thumb or the next finger covers the openings while worn: a measurement of the build guide (item 78, pass: at most 3 dB lower).
- O6 SNR falls from 67.5 to 64.5 dB(A); bench B1 compares recordings.
- Not done: the inside model, the exterior and the board files are not changed (outside my folder). The check uses boxes from placement.csv, not the solids of thin.py.

## 11. Files

- `mic-path.md` (this file), `check_mic_path.py`, `check.log`, `acoustic_estimates.py`, `acoustic.log`, `board_conflicts.py`, `board-conflicts.log`, `CHECKLIST.md`.
- `datasheets/`: the copies used. `evidence/`: earlier runs, expectations, page images, audit.

RESULT: done, top-port Knowles SPK0641HT4H-1 under the board with a 1.0 mm bore, gasket and membrane straight down through the floor passes the fit check (check.log RESULT PASS), with the wall slots removed and 35 changes to other files listed.
