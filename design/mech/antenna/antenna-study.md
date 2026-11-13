# Antenna in the metal body: study for review finding F06

Design commit ff89faf. Inside model v4 (design/mech/thin/). Nothing outside design/mech/antenna/ and design/datasheets/antenna_* was changed.

Tags: a number with a file and line, a datasheet file and page, or a log line comes from that place. [CALC] is arithmetic on cited numbers, with its inputs named. [ESTIMATE] is my judgement, with its reason. Logs named here are in design/mech/antenna/.

## 1. The facts, measured

Script: design/mech/antenna/measure_antenna.py. It reads design/mech/thin/placement.csv and layers.json, then casts 25 straight rays out of each face of the antenna body into the inside model's STEP (design/mech/thin/out/thin-inside.step). The STEP was needed because the pocket walls, the floor, the rolls and the formed glass are not boxes. Output: measure.log, last line `RESULT measured` (measure.log line 159). Before the run I wrote the expected values (expected_measure.txt); compare_expected.log shows 0 of 11 cases differing.

Antenna ANT1, Johanson 2450AT18D0100001E: centre X -12.7, Y 4.4, Z 1.05, size 1.6 x 3.2 x 1.2 (placement.csv line 13; measure.log line 2). Box X -13.5 to -11.9, Y 2.8 to 6.0, Z 0.45 to 1.65; the STEP antenna is the same box (measure.log line 6). Axes: X along the finger (-X hand end), Y across (+Y thumb), Z up toward the glass (layers.json line 4).

| Surface | Gap from the antenna body | Metal thickness there | Beyond it | Source |
|---|---|---|---|---|
| Hand-end wall (-X) | 0.225 mm on all 25 rays | 0.602 to 0.925 mm | air | measure.log line 10 |
| Thumb-side wall (+Y) | 0.450 mm on all 25 rays | 0.418 to 0.925 mm | air | measure.log line 12 |
| Side wall away from the thumb (-Y) | 9.250 mm; first met: screen connector J1 housing at 0.200 mm (20 of 25 rays) | 0.418 to 0.925 mm | air | measure.log lines 14 to 16 |
| Floor (-Z) | 0.050 mm on all 25 rays | 0.392 to 0.400 mm | air (the block underside; the finger when worn) | measure.log line 17 |
| Least 3D distance to any body metal | 0.050 mm | | | measure.log line 126 |

Straight up from the antenna top (Z 1.65) to the outside air, on the 5 rays at Y 5.68 (measure.log lines 27 to 33):

| Z from | Z to | What | Thickness | Source |
|---|---|---|---|---|
| 1.650 | 1.750 | open space (the board notch: no board over the antenna) | 0.100 | measure.log line 28 |
| 1.750 | 1.850 | foam frame | 0.100 | measure.log line 29 |
| 1.850 | 2.250 | screen panel, lower glass only (the driver ledge) | 0.400 | measure.log line 30 |
| 2.250 | 2.650 | open space (where the upper glass is absent on the ledge) | 0.400 | measure.log line 31 |
| 2.650 | 2.750 | clear adhesive | 0.100 | measure.log line 32 |
| 2.750 | 3.320 | cover glass | 0.570 | measure.log line 33 |

Other rays differ only as follows. The cover glass is 0.570 to 0.941 mm thick over the antenna (measure.log lines 33 and 41). On 8 rays at X -12.38 and -12.06 with Y 3.12 to 5.04 the foam is absent (measure.log section 2, the stacks after line 33; counted in count_foam.log). On 2 rays at X -12.06 the screen's driver IC lies over the antenna, Z 2.25 to 2.55, 0.300 thick (measure.log lines 98 and 106).

Does the screen panel cover the antenna? Yes, all of it: panel footprint overlap 5.120 of 5.120 mm2 (measure.log line 113). The part over it is the driver ledge, not the lit area: lit-area overlap 0.000 (measure.log line 115). The driver IC overlaps 0.210 mm2 of the antenna footprint (measure.log line 114). Least distance from the antenna to the panel 0.200 mm, to the screen tail 0.347 mm, to the driver IC 0.600 mm (measure.log lines 128 to 130).

The design's own rule, "no copper and no metal within 4.2 x 4.7 mm, on every layer" (design/architecture.md line 156), centred on the antenna, reaches X -14.8 to -10.6, Y 2.05 to 6.75 (measure.log line 138; 4.2 along X is my reading, the rule does not say). Body metal lies inside it: yes (measure.log line 152). So does every layer above it: panel, driver IC, screen tail, J1 (measure.log lines 139 to 151).

One side finding, not mine to fix: the cover glass over the antenna is 0.570 to 0.941 mm thick (measure.log lines 33, 41), while architecture 17.1 says "One flat cover glass 0.4 mm thick" (design/architecture.md line 419).

## 2. What the antenna maker requires

No Johanson copy was in design/datasheets (search for "2450AT18" and "johanson": johanson_urls.log; a text copy existed only at design/ecad/ring/evidence/text_johanson.txt, made from a PDF outside the repo). I saved two versions:
- antenna_johanson_2450AT18D0100001E.pdf: fetched from the maker with getpdf.sh (fetch_2.log); 5 pages, "Revision 5.0", 2023. Text: johanson_text.log. The same file is also saved as antenna_johanson_2450AT18D0100.pdf (fetch_1.log; same hash, datasheet_hashes.log).
- antenna_johanson_2450AT18D0100001E_8p.pdf: copied from the PDF behind the ecad text copy; 8 pages, "Revision 5.0", 2024 (johanson_8p_text.log). Pages were also rendered (ds8_p1.png, ds8_p3.png, ds8_p5.png) and read as images.

| Requirement | What the maker says | Where |
|---|---|---|
| Ground clearance, evaluation board | A yellow area marked "No GND on all layers", 4 mm wide and 6 mm deep from the board edge, with the antenna at the edge; lands 1, 2, 1 mm across and 0.6, 0.7, 0.6 mm deep; 4.1 mm of clearance below the lands | 8p PDF page 3 (johanson_8p_text.log line 158; image ds8_p3.png) |
| Ground clearance, round board | "Ground Clearance - no other metallic components like batteries and displays directly underneath antenna." | 8p PDF page 5 (johanson_8p_text.log line 326; image ds8_p5.png) |
| Ground clearance, thin edge | Clearance 8 mm along the edge and 3.4 mm deep (lands 1, 2, 1 and 0.6, 0.7, 0.6; 1.5 below the lands), plus an L/C part "to adjust the initial frequency" | 8p PDF page 5 (image ds8_p5.png; note text johanson_8p_text.log page 5) |
| Matching | The designer should "leave available slots for a" pi network, "(or shunt-series-shunt)". "The matching values on client's PCB will be different, depending on the layout, thickness, material, etc." Evaluation board: one 0 ohm series part; "JTI P/N's for Matching Network" with the answer "N/A" | 8p PDF page 3 (johanson_8p_text.log line 169), page 5 (line 316), page 6 (line 384) |
| Efficiency and gain | Average radiated efficiency 72 %; peak gain 1.5 dBi typ.; average gain -1.0 dBi typ.; return loss 6 dB min.; 2400 to 2500 MHz | 8p PDF page 1 (johanson_8p_text.log lines 34 to 44) |
| Same, 2023 copy | Radiated efficiency 72 %; peak gain 1.5; average gain -1.0; return loss 10 dB min.; 2400 to 2480 MHz | 5p PDF page 1 (johanson_text.log lines 37 to 45) |
| Board they were measured on | "General specifications measured on Johanson's evaluation board P/N 2450AT18D0100001CE1"; that board is 40 x 20 mm | 8p PDF page 1 (johanson_8p_text.log line 33); page 3 drawing (40 and 20, image ds8_p3.png) |
| Return loss on that board | -13.935 dB at 2.400 GHz, -24.894 dB at 2.450 GHz, -14.774 dB at 2.500 GHz | 8p PDF page 4 (johanson_8p_text.log page 4 markers) |

The two copies disagree on the minimum return loss (6 against 10 dB) and the band edge (2500 against 2480 MHz). Both say 72 % efficiency on the 40 x 20 mm board.

The ring breaks the maker's conditions on three counts. Metal lies 0.050 mm under the chip, where the maker says no metal parts directly underneath (8p PDF page 5). The clearance is 0.225 mm and 0.450 mm to metal walls, against a metal-free area of 4 x 6 mm on the evaluation board (8p PDF page 3). The panel sits 0.200 mm over it (measure.log line 128).

## 3. What can and cannot be claimed

Can be claimed, from the model and the sources:
- The gaps, thicknesses and layers above (section 1, measured on the model at ff89faf).
- The maker's 72 % holds only on its 40 x 20 mm board with its clearance (section 2). It is not a figure for this ring.
- Two maker notes say no metal may cover a chip antenna. Infineon AN91445: "The antenna must not be covered by a metallic enclosure completely. If the product has a metallic casing or a shield, the casing must not cover the antenna. No metal is allowed in the antenna near-field." (antenna_infineon_an91445.pdf page 23; quotes_infineon.log). The same note: "It takes up to 4-mm distance from the antenna to have radiated electric and magnetic fields formed properly" and "Near-field obstructions detune the antenna and may kill the antenna radiation." (page 42).

Cannot be claimed here: any efficiency, gain, range or detuning figure for the ring, as built today or with any option below. No field simulation is available, and no RF part of the ring has been measured. This study gives no such figure. The only way to a number is the bench test of section 6.

## 4. Options

Sources opened for metal-case practice: Infineon AN91445 (antenna_infineon_an91445.pdf, 60 pages, saved; text searched, guideline pages read), TI SWRA161B antenna selection guide (antenna_ti_swra161b.pdf, saved; text searched), the Johanson datasheets and Johanson's tuning page (antenna_johanson_tuning.html, text in johanson_tuning_text.log). Blocked or not the document, recorded and not worked around: Nordic nWP-017 (a "Just a moment..." bot check, html_nordic_head.log), Silicon Labs AN1088 ("Access Denied", html_silabs.log), Taoglas integration guide (bot check, taoglas_head.log), Abracon design guide (the URL gave the home page, abracon_text.log). No opened source describes a slot or loop antenna in a metal wearable body (search_metal_case.log: 3 hits, none on that). Option (b) therefore rests on no source here.

| Option | What it changes in the ring | For | Against | Look | Water seal |
|---|---|---|---|---|---|
| (a1) Radio window through the glass end: keep the chip, rely on the top glass | Nothing in the body. The screen maker keeps the ledge metal-free over the antenna | The path up is non-metal except the panel's lower glass and the driver IC (measure.log lines 27 to 33, 98) | Metal still 0.050 mm under the chip and 0.225 / 0.450 mm beside it (measure.log lines 10 to 17); the maker forbids metal directly underneath (8p PDF page 5); Infineon page 23 | none | unchanged |
| (a2) Non-metal insert in the hand-end wall only | End wall X -14.65 to -13.725 over Y 2.05 to 6.75 becomes resin [CALC: inner face -13.5 - 0.225 from measure.log line 10, outer face from step_tree.log line 345, Y span from measure.log line 138] | Removes the nearest wall (0.225 mm) | Floor (0.050 mm) and thumb wall (0.450 mm) stay metal (measure.log lines 12, 17) | a resin patch on the hand-end face | one bonded seam ring |
| (a3) Resin-filled slot in the metal | A narrow cut through the floor or a wall, filled with resin | Smallest visible change | A slot much shorter than half a wavelength (61.4 mm at 2.44 GHz [CALC: 299.79 / 2.44 / 2, with 299.79 mm x GHz the speed of light, a physical constant]) [ESTIMATE: lets little through]; no opened source sizes one | a line on the body | a filled slot to seal |
| (a4) Radio corner: the body's corner inside the keep-out box made in resin | Body inside X -14.8 to -10.6, Y 2.05 to the outer skin, Z 0 to 2.75 becomes a bonded resin part (insert_check.log line 2) | Nearest body metal goes from 0.050 to 0.752 mm (insert_check.log lines 8, 9); the design's own keep-out then holds for the body; no metal under, beside or at the end of the chip | Panel 0.200 mm above, J1 housing 0.200 mm and screen tail 0.347 mm beside stay (measure.log lines 127 to 129); bond areas small: 3.970 and 2.834 mm2 (insert_check.log lines 5, 7) | a corner of different material, seams on the hand end, the thumb side and the underside | two bonded seams |
| (b) Metal body as the antenna (slot or loop) | An insulating break in the body, a feed clip from the board's radio line to the body, ground clips, a new match | The band is about half a wavelength round [CALC: pi x (18.95 + 2.6) = 67.7 mm mid circumference, inputs architecture.md line 420; 122.9 mm wavelength at 2.44 GHz: 299.79 / 2.44] | No opened source; cannot be sized without a field simulation; a break changes the one-piece body | a visible insulating line | the break must be sealed |
| (c) Antenna on the band liner side or a flex tail | Antenna in the band channel under the 0.3 mm liner | The liner is non-metal (design/mfg/specs/band-liner.md line 6) | Only open face points into the finger; channel has no room under the cell (design/mech/thin/thin-notes.md, Model v4 row C: "free height under the cell 0"); Infineon page 42 on near-field obstructions | none | none |
| (d) Flex or wire antenna under the glass's end roll | A custom flex antenna in the measured 0.400 mm space on the panel ledge, Z 2.25 to 2.65 (measure.log line 31), between the hand end and the driver IC (X -13.675 to -12.075, measure.log lines 113, 114); fed by a flex that folds down the hand end like the screen tail | Above all metal of the ring; Infineon: "The wire antenna gives the best performance" (page 4); TI: a wire "can be formed around the mechanical housing" (antenna_ti_swra161b.pdf page 11) | No part exists on file; needs an antenna maker to design and tune; the walls still rise to Z 2.75 round it (step_tree.log line 345); TI page 11: position "will have to be controlled" | none | none |
| (e) Leave it, accept the risk until a bench test | Nothing | No cost; the bench test of section 6 measures this case as T1 anyway | Breaks the maker's conditions and the design's own rule (sections 1 and 2) | none | unchanged |

## 5. Recommendation: option (a4), the radio corner

Make the corner of the body that lies inside the design's own keep-out a bonded resin part, and keep the chip antenna where it is.

Geometry, inside-model coordinates (mm):
- Radio corner = the body solid inside the box X -14.8 to -10.6, Y 2.05 to 7.6, all Z. Measured on the STEP: it spans X -14.650 to -10.600, Y 2.050 to 7.375, Z 0 to 2.750; volume 20.265 mm3 (insert_check.log line 2). The metal body left: 938.203 mm3 (insert_check.log line 3).
- Bond faces: plane X = -10.6, Y 2.05 to 7.375, Z 0 to 2.75, area 3.970 mm2 (insert_check.log lines 4, 5); plane Y = 2.05, X -14.65 to -10.6, Z 0 to 2.75, area 2.834 mm2 (insert_check.log lines 6, 7).
- The corner keeps the body's outer shape, the panel pocket wall and floor, and carries the glass seat on its top at Z 2.75 (step_tree.log line 345, body top). It touches no part: overlap 0 with the screen tail, J1, microphone 1, the light and the light pipe (insert_check.log lines 23 to 27).
- Antenna ANT1 unchanged: X -12.7, Y 4.4, Z 1.05 (placement.csv line 13). Its nearest body metal becomes 0.752 mm (insert_check.log line 9).
- Material: a non-metal resin, coloured in the mass. No metal flake, no metal plating, no metallic paint on it. No metal print on the cover glass over X -14.65 to -10.6, Y 2.05 to 7.375. [ESTIMATE: any metal coat would close the window; this is reasoning from Infineon page 23, not a measured rule.]
- Screen maker: no metal on the panel's ledge over X -13.675 to -10.6, Y 2.05 to 6.4, or a statement of what metal is there. The driver IC already lies at X -12.075 to -10.475, Y -4.0 to 4.0 (measure.log line 114). This is open and is in the bench test.
- S15 (antenna pads off the board, design/architecture.md line 513) stays open. The resin floor makes one fix possible: a pocket 1.8 x 3.4 x 0.22 mm in the corner's floor lets the chip hang under the board with its pads on it, Z 0.23 to 1.43, leaving 0.180 mm of resin under it (insert_check.log lines 10 to 13). But the maker's land pattern (4.0 x 1.9 mm, 8p PDF page 3) at this spot would reach Y 2.4 to 6.4 [CALC: 4.4 +- 2.0], past the board edge at 6.3 (placement.csv line 15: board 12.6 wide) and into J1's housing, which ends at Y 2.6 (step_tree.log line 159). The layout engineer decides.

Files that would change (not changed by me), one line per change. Items 6 to 8 and 10 are written by thin.py (thin.py line 13), so they follow from item 9 when the model is rebuilt:
1. design/architecture.md line 156. Present: `| Antenna | +12.0 | on top of the board | no copper and no metal within 4.2 x 4.7 mm, on every layer |`. New: `| Antenna | X -12.7, Y 4.4 (inside model) | under the board, hand-end thumb-side corner | no copper and no metal within X -14.8 to -10.6, Y 2.05 to 6.75 on every board layer; in the body this box is the resin radio corner (17.18) |`.
2. design/architecture.md line 420. Present: `Block and band are one metal body.` New: `Block and band are one metal body, except the resin radio corner at the hand-end thumb-side corner of the block (17.18).`
3. design/architecture.md after section 17.17 (which starts at architecture.md line 601; that section was added while this study ran). Present: none. New: section `### 17.18 Radio corner` with the geometry of this section 5.
4. design/architecture.md line 271. Present: `| B4 | antenna match values from Nordic's reference | measure the antenna on the assembled ring with a network analyser | new coil and capacitor values |`. New: `| B4 | antenna match values from Nordic's reference; radio corner | return loss on a finger, and radiated signal against the bare board and the all-metal body (design/mech/antenna/antenna-study.md section 6) | new coil and capacitor values; radio corner kept or dropped |`.
5. design/architecture.md open items, after line 513. Present: none. New: `| S-new | Screen ledge over the antenna: metal on the panel's ledge in X -13.675 to -10.6, Y 2.05 to 6.4 | the screen maker |`.
6. design/mech/thin/placement.csv line 23 (outer_body note). Present: `joystick and record openings, motor pocket, 4 pad holes"`. New: `joystick and record openings, motor pocket, 4 pad holes; the part inside X -14.8 to -10.6, Y 2.05 to the edge is the radio_corner row"`.
7. design/mech/thin/placement.csv, new row after line 23. Present: none. New [CALC from insert_check.log line 2: centre X (-14.65 - 10.6) / 2 = -12.625, Y (2.05 + 7.375) / 2 = 4.713, Z 2.75 / 2 = 1.375; size 4.05, 7.375 - 2.05 = 5.325, 2.75]: `radio_corner,,body,-12.625,4.713,1.375,4.050,5.325,2.750,,False,"resin radio corner: the body inside X -14.8 to -10.6, Y 2.05 to the outer skin, Z 0 to 2.75; bonded on the planes X -10.6 and Y 2.05; glass seat on its top"`.
8. design/mech/thin/layers.json line 185. Present: `"outer_body"`. New: `"outer_body", "radio_corner"`.
9. design/mech/thin/thin.py lines 384 to 385. Present: `for c in cav:` / `body = body - c`. New [CALC: box size Y 7.6 - 2.05 = 5.55, centre Y (2.05 + 7.6) / 2 = 4.825; X size 4.2 centre -12.7 as the keep-out]: the same two lines, then `corner = body & box(4.2, 5.55, 4.0, -12.7, 4.825, 1.0)` and `body = body - box(4.2, 5.55, 4.0, -12.7, 4.825, 1.0)`, and after line 389 a new part `newp("radio_corner", "", "body", (-12.625, 4.713, 1.375), (4.05, 5.325, 2.75), None, False, "resin radio corner")` with `.add("resin", corner)`.
10. design/mech/thin/out/thin-inside.step and thin-inside.glb: rebuilt by thin.py with the radio_corner node (no hand edit).
11. design/mfg/specs/body.md line 8. Present: `The one-piece metal body of the ring:`. New: `The metal body of the ring, with a bonded resin radio corner (specs/radio-corner.md):`.
12. design/mfg/specs/radio-corner.md. Present: none (new file). New: the geometry, material rule and bond faces of this section 5.
13. design/bom.csv line 12 (ANT1). Present: `keep-out 4.2 x 4.7 mm no copper on any layer`. New: `keep-out X -14.8 to -10.6, Y 2.05 to 6.75 (4.2 x 4.7) no copper on any layer; the body is resin there (radio corner)`.
14. design/bom.csv, new row. Present: none. New: `Radio corner,RC1,1,resin body corner,,,,4.05 x 5.325 x 2.75,,"bonded into the body; no metal coat",,`.
15. design/bench/bench-plan.md line 83. Present: `- The ring's size, its antenna and its microphone openings: sound through a slot in a metal wall is bench test B7 on the first housing.` New: the same line, then `- The antenna: bench test T0, T1, T2 of design/mech/antenna/antenna-study.md section 6 (network analyser and RSSI).`

## 6. Bench test that proves it

Kit on file: the nRF54LM20 DK and the Power Profiler Kit II (design/bench/bench-plan.md lines 21 to 22). Not in the kit and needed: a vector network analyser covering 2.4 to 2.5 GHz, a thin coaxial pigtail, and Johanson's evaluation board 2450AT18D0100001CE1 (8p PDF page 8 lists it as orderable). Architecture B4 already calls for a network analyser (design/architecture.md line 271). Johanson also offers to measure radiated efficiency in a chamber, with probes through the housing (johanson_tuning_text.log lines 161 to 163); that is the owner's choice, not contacted.

What to build:
- One ring board (or a board of the same outline with ANT1, its pi match and the parts within the keep-out), the real screen panel, foam, adhesive and cover glass.
- One machined metal body to the drawing. Test it as T1 (all metal). Then cut the corner off on the two planes of section 5 and bond the resin corner in: that is T2. Same board, same body, same glass.
- T0: the same board out of the body.
- A coaxial pigtail soldered at the match input, ground close by, as Infineon describes (antenna_infineon_an91445.pdf page 36). Firmware: the ring advertises at one fixed transmit power in every run.

What to measure:
1. Return loss of ANT1 through the match, 2.3 to 2.6 GHz, for T0, T1, T2: on the bench and worn on a finger, hand open and in a fist. Infineon says to check "with a hand on the device" (page 42). Retune the pi network on T2 worn, then measure again.
2. Received signal: the DK at 1.0 m as the scanner logs the RSSI of 100 packets at each of 8 headings, 45 degrees apart, for T0, T1 and T2 worn by the same person at the same spot; repeat 3 times; report the mean and the spread. [ESTIMATE: 1.0 m, 100 packets, 8 headings and 3 repeats are my choices, to average out reflections in a room.]

Pass line:
- Return loss at least 10 dB from 2400 to 2480 MHz on T2 worn, after retune (the 2023 datasheet's minimum, 5p PDF page 1).
- Mean RSSI of T2 worn no more than 10 dB below T0 [ESTIMATE: my pass line; 10 dB of loss cuts free-space range by a factor of 3.2 (CALC: 10 to the power 10/20), which the owner may tighten], and at least 3 dB above T1 [ESTIMATE: the smallest gain I would pay a seam for, given a spread of a few dB between repeats].
- If T1 already meets the first two lines, option (e) holds: keep the one-piece metal body and drop the corner.

## 7. What the owner would see

Yes, it changes the look. The hand-end corner on the thumb side, about 4 by 5.3 mm (insert_check.log line 2), becomes a different material with fine seams on the hand end, the thumb side and the underside, while the top stays all glass. If the bench shows the all-metal body already passes, the corner is not needed and the look stays as it is.

RESULT: done, F06 measured (metal 0.050 mm under and 0.225 / 0.450 mm beside the antenna, measure.log ends RESULT measured), options (a) to (e) compared, one recommendation: a bonded resin radio corner X -14.8 to -10.6, Y 2.05 to the edge, proven or dropped by bench test T0, T1, T2.
