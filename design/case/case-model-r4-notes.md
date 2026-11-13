# Case model r4: the routed boards in the case model (notes, written step by step)

Started 2026-11-13 04:07 CET (clock from `date`, r4/base_check.log first line). Project root: . (ROOT). Version read: commit 8bddd8a (stated by the lead; I ran no git).
Scripts and logs of this round: ROOT/design/case/r4/ (checklist r4/CHECKLIST.md).

## 1. Baseline

Command: `nice -n 19 ../.venv/bin/python case_check.py` in ROOT/design/case, as delivered (out/ of 2026-11-11 21:45); log r4/base_check.log, exit code in r4/base_check.done.
Result: `case_check: PASS, 3447 pairs checked, 0 failures, ring sizes US [7, 8, 9, 10, 11, 12, 13]`, exit 0; start 2026-11-13 04:07:56, end 04:30:38 (22 min 42 s). Same line as c5d-open-points-handover.md line 38.
Ring files read (unchanged by me, the ones case.py already reads): design/look/s1/out/ring-merged32h-us7.step to -us13.step and measures-merged32h-us<n>.json; pads from design/mech/thin/placement.csv (dates: section 8).

## 1b. Debug runs (all kept, none is a proof)

- r4/try1_build.log: first build with the boards (into r4/try1/), exit 0, 40 s.
- r4/try1_quick.log: test-1 pairs of the new parts, test 5, tests 15 and 16 on try1: 0 intersections; one finding (15b counted the insulating sheet as rigid: J1's shell legs are 0.065 mm above it inside the board) fixed by counting the sheet and the foam pad as soft parts.
- r4/try1_lift7_killed_slow.log, try1_lift7b_killed_slow.log, try1_lift7c_killed_slow.log, try1_lift7d_killed_slow.log, try1_lift7e_killed_slow.log: test 17 at US 7, stopped by me (pids of my own runs) because the point sampling and the exact phase were too slow (4.6 million ring points; whole-solid distances); the sampling and the exact phase were rewritten each time.
- r4/try1_lift7f_stopped_contact_rule.log: the exact phase failed on the outer pins touching the band at US 7 (common volume 0.0002 mm3); my code had made any touch a failure, which is stricter than the pass line written before the first run (common volume above 0.001 mm3); the code was put back to the pass line.
- r4/try1_lift7g.log: US 7 only, 288 s: smallest free space 0.172 mm to shell at lift 0.25 mm; pins touch with 0.000151 mm3 at most; OK.
- First proof chain (run_final.sh all, 05:04): build r4/run1_final_build.log exit 0; the full check (r4/run1_final_check_stopped_15c_fail.log) printed `FAIL 15c main board to light_window 0.100 mm` (and 0.195 mm to usb_bezel): the light window rod ended 0.1 mm from the board edge (C5d's rule) and the bezel's hidden inner end was 0.195 mm from the real board tab, which reaches 0.505 mm further out than C5d's tab. I stopped the chain (my pids 43814 and 48741) during test 17, kept both logs under the names above and removed the two .done files of that run (their content was the exit codes, 0 for the build). Fix, inside only: the light window rod now ends at the cavity wall (x = cav_x0, 0.4 mm from the board edge), the bezel recess ends 0.35 mm before the tab (`rec_x1`); faces seen from outside unchanged.
- r4/try2.log: build + debug check after the fix: 0 intersections among new pairs, 15c smallest 0.350 mm (shell, usb_bezel), failures 0.
- Second proof chain started 05:54:32 (run_final.sh all, pid 72093; master log r4/run_final_all_run2.log).

## 2. The boards as read

Reader: r4/board_read.py (KiCad 10.0.8's own Python, `design/ecad/ring/pcb/run_kipy.sh`) and `kicad-cli pcb export step --no-dnp --subst-models` (r4/run_read.sh), on every run of case.py (into out/boards/) and again in the check (out/boards_check/). r4/case_boards.py turns them into the case frame. The sheet origin of each board is read from design/ecad/case/pcb/build_boards.py line 22 (`OX, OY = 100.0, 100.0`) and line 23 (`OX2, OY2 = 100.0, 100.0`).

First read (r4/inspect_now.log, from r4/boards_now/):
- Main board: thickness 1.0 mm; one outline of 8 corners, KiCad x 98.150 to 123.000, y 79.800 to 117.700: the board is u 0 to 23.0 by d -20.2 to +17.7 (23.0 x 37.9 mm, not symmetric: case y -17.7 to +20.2), plus the socket tab u -1.85 to 0, d -17.57 to -7.37 (10.2 mm wide).
- 84 footprints; 16 on the back face, all test pads TP1 to TP16, none with a body (r4/inspect_now.log lines "TP.. B").
- 59 footprints with a 3D model, all on the front face; 25 without (BT1, TH1, TP1 to TP16, W1 to W7).
- U1 module courtyard KiCad y 99.08 to 119.83: the module overhangs the board's -y end (antenna end) by 2.13 mm (courtyard), body to y -19.7 (r4/inspect_step_main.log line 86).
- Wire pads W1 W2 W7 W3 W4 at u 17.95, d -3.2 -1.6 0 1.6 3.2; W5 at u 15.55 d -17.4; W6 at u 8.8 d -18.65; TH1 pads around u 20.25 d -18.3.
- Pin board: thickness 0.8 mm; three islands: inner y -2.25 to 2.25 (case frame), wings 2.35 to 4.90 and -4.90 to -2.35, all 5.0 mm high; pins P1 to P4 at y +3.521, +1.197, -1.197, -3.521; wire pads WP1 to WP4, WP7 on the FRONT face (the pin face) at z_pin - 1.75.

## 3. Finding: the socket sits 0.505 mm deeper than designed

KiCad's own USB4105 footprint (same pad coordinates as the board's footprint) draws the body from -3.675 to +3.675 mm about the origin (F.Fab rect) with its "PCB Edge" line at +3.675; the courtyard ends at +4.18 (r4/j1_front_evidence.log). The board's footprint (design/ecad/case/pcb/make_footprints.py line 309) and board-notes.md take +4.18 as the mating face. The 3D model in the board's STEP ends at +3.675 (KiCad x 97.055, r4/inspect_step_main.log line 48). With the board where C5d put it (pcb1_x0 -9.637) the socket front would be 0.805 mm behind the skin instead of 0.3 (check test 10).
Fix used (case side, outside unchanged): the model now places the board so that the socket body's front is J1_LIP = 0.3 mm behind the skin: pcb1_x0 = jx0 - (front of the J1 body in the board frame). Reported to the lead at about 04:15 (SendMessage); the other fix would be J1 0.505 mm further out on the board.

Lead's ruling (received after 05:04): fix A. What follows the move (r4/follow_board.py on the delivered out/, log r4/follow_board.log); none of it changes what is seen from outside (the light window and the mouth are where C5d had them):
1. Status light: LED1 body (board STEP) x -9.342 to -7.742, y 5.300 to 6.900, z 13.195 to 13.895. Light window (shell part, dia 1.00; its outside face unchanged) axis y 6.000, z 13.550, now ends at the cavity wall x -10.542 (r4/follow_board_final.log; it ended at -10.242 in the first r4 build, which failed check 15c at 0.100 mm from the board). The window axis is 0.100 mm off the LED's centre in y and +0.005 mm in z, inside the LED's span; air gap from window end to the LED 1.200 mm (C5d's reserved box: 0.700 mm). The light still sits behind its opening; the longer air gap makes the dot dimmer by an amount not computed (bench B4 checks brightness).
2. Touch electrode E1: PCB2 did not move (x_b 5.8201 before and after); E1 still reads through the holder's front wall 1.9745 mm thick (unchanged). E1's front strip is at z 25.41; the new wire recess ends at z 22.66, below it.
3. Leads and cell: path lengths in section 6; cut = path + 5 mm, all inside the parts list lengths (W1 to W4 30, W7 20, W5 W6 40 mm). Cell top z 11.900 to board back z 12.200: 0.300 mm (the 0.25 mm insulating sheet, modelled 0.260 mm, lies in it). The board now runs x -10.142 to 12.858 over the cell's x -7.737 to 15.263 (C5d board from -9.637).
Socket and plug (r4/plug_seat.py, log r4/plug_seat_final.log): the socket body's front (board STEP) is x -13.0870, 0.3000 mm behind the skin at the socket's outermost corner. The USB4105 drawing (design/datasheets/case_usb4105.pdf p.1, "Plug and Receptacle Mating View") shows the mated plug's overmold face at "1.85 Min" in front of the receptacle and the overmold "6.5 Max" high. The overmold cannot enter the 4.51 mm high mouth slot, so it stops on the outermost skin in front of the socket: 0.887 mm in front of the socket front for an 8.34 mm wide overmold, 0.893 mm for 12.35 mm wide (my width value; the drawing gives none). Both are under 1.85: a standard plug seats fully, with 0.96 mm to spare.

## 4. Holding the main board

C5d had no feature (case.py lines 642 to 645 of 8bddd8a: the board floated between the cell and the floor with 0.3 mm gaps). The stack under the floor, from the bottom: bottom plate top z 3.0 (4 screws M1.6 x 5, BOM MECH6), 0.4 mm gap, cell 8.5 mm, 0.3 mm gap, main board 1.0 mm, parts, ceiling (underside of the floor) z 16.9.

Options (at most two):
- A, chosen: a printed board retainer (own part `board_retainer`, BOM MECH18) clamps a stack. A foam pad (MECH19, 0.8 mm free, closed-cell PE or PU, self-adhesive on one face) under the cell, an insulating sheet (MECH20, 0.25 mm polyimide or PET) on the cell under the board's 16 bare test pads; the retainer lies under the ceiling and its four posts press the board's top face; the bottom plate's four screws compress the foam to the 0.4 mm gap. A fence of the retainer fills the space between the board's +X edge and the cavity's +X wall. A first-time builder needs: the printed part (same printer or service as the shell; PLA or PETG on a hobby printer also works for this part), scissors, the four existing screws.
- B, rejected: screws or heat-set inserts through the board (needs holes in the board: a board change) or adhesive between board and ceiling (no rework, glue near parts, unknown bond on PA12).

Forces: a USB-C plug pushes the socket toward +X with 5 to 20 N (case_usb4105.pdf p.1, "Mating Force: 5 to 20 N"); path: socket, board, fence, cavity wall (+X). Pulling a plug out (case_usb4105.pdf p.1, "Unmated force 6 to 20 N after test") pulls toward -X: the clamp's friction holds it; if it slips, the board's -X edge meets the cavity wall after 0.4 mm (BOARD_WALL_GAP). The clamp force depends on the foam and is not known: it is a named measurement (below), not proven.
Numbers: see section 7 (from out/case_params.json key `retainer`).

## 5. Straight lift out (check test 17)

Pass line, printed by the test and fixed in the code before its first run: no common volume above 0.001 mm3 with any case part at any step, and free space >= 0.10 mm to every case part except the seat contacts (the 4 spring pins at their working compression for the size, and the two flank faces of the V wall). Reason for 0.10: the smallest designed gap on the way out other than the seat is the block's guide in its pocket, POCKET_G 0.15 mm per side. Method: lid swung to its open angle (100 degrees) about the pivot; ring parts (body, glass, joystick) lifted along +Z in 0.25 mm steps until the ring's lowest point passes the case's highest point (the open lid's top, z 41.40); a screen of surface points (ring 0.2 mm, case parts 0.1 mm) at every step, then OCC face-to-face distances at every step whose screen value is below 0.5 mm and at each part's closest step; where boundaries meet, the common volume.
Results per size: section 9 (from r4/final_check.log).

## 6. Leads (check test 16)

Modelled as swept wires (case.py `swept_wire`), axis points in out/case_params.json key `leads`; each end sits 0.02 mm from its solder joint or glue face. Paths:
- W1 to W4, W7 (30 AWG, 0.50 mm, start value): from the wire pad on PCB2's front face straight down the holder's new recess (0.7 mm deep, up to z 22.66) and the floor slot (now x 4.82 to 9.82, y -4.0 to 4.0) into the cavity, across at z 16.30 (0.6 mm under the ceiling, over U1's top at 15.595), down into the plated hole. Path / cut (path + 5 mm): W1 10.2 / 15.2, W2 10.8 / 15.8, W3 10.8 / 15.8, W4 10.2 / 15.2, W7 10.7 / 15.7 mm; parts list 30, 30, 30, 30, 20 mm.
- Thermistor TH1 (bead 1.6 mm, leads 0.30 mm, start values): bead glued on the cell's top face at x 14.06, y 18.30 (between the board's +X edge 12.86 and the cell's edge 15.26); leads up to z 14.20, over the board edge, down into TH1.1 (x 9.108) and TH1.2 (x 11.108): 6.7 and 4.7 mm.
- Cell leads W5 (+, red) and W6 (-, black) (1.0 mm, start value): out of the cell's PCM end 10 mm apart about its centre line (case_cell_dnk852338.pdf p.1, M = 10), 1.0 mm below its top face (my reading), into a pocket in the cavity's +Y wall (x -2.34 to 9.76, y 20.10 to 21.80, z 9.90 to 15.20), up past the board's end at y 21.0, over to W5 (x 5.408, y 17.4) and W6 (x -1.342, y 18.65): 11.2 and 6.7 mm, cut 16.2 and 11.7 mm (parts list 40; the cell is ordered with 100 mm leads, board-notes.md part f).
Free room per lead: section 9.

## 7. Numbers of the holding feature (out/case_params.json key `retainer`)

- Web: 0.8 mm thick, z 16.08 to 16.88 (0.02 mm under the ceiling at 16.90), plan = the main board x -10.142 to 15.843, y -17.70 to 20.20, with the socket J1 (+0.3 mm) and the wire runs (+0.3 mm) cut out; one solid, 984.4 mm3.
- Posts: 4, dia 1.6 mm, 2.86 mm long (web to 0.02 mm above the board's top face), at (6.71, 10.15), (-9.04, 18.90), (9.21, -0.60), (-5.29, 18.15); placed by the script on free board spots at least 0.3 mm (plus the post radius) from every part body and lead (67 free spots found). None lands on the module half (y below -0.60): that half lies on the insulating sheet and is not pressed from above.
- Fence: x 12.878 to 15.843 (board edge + 0.02 to the cavity wall - 0.02), y -10.0 to 10.0, z 12.20 to 16.08.
- Stack: foam pad 0.8 mm free (modelled 0.36 mm compressed), insulating sheet 0.25 mm (modelled 0.26 mm), cell 8.5 mm, board 1.0 mm.
- Cavity (inside change only): at the board's level (z 11.85 to 16.90) the -X wall moved to x -10.542 (board edge -10.142 + 0.4) and the socket-side end to y 20.6 (board end 20.2 + 0.4); below it the C5d cavity (x -10.037, y +-20.35). Thinnest plan wall to the skin, box corners not rounded: 0.655 mm at (-10.54, 20.60, 11.85) (r4/wall_check_final.log), C5d 1.023 mm at (-10.04, -20.35, 3.0) (r4/wall_check_base.log); the cavity's 0.5 mm corner round makes the real corner thicker (not measured).
- Outside unchanged: size box, outline extremes, seam, pivot, magnet, dimple, socket front and skin at the socket are the same numbers as C5d (r4/outside_compare.log). The board-tab channel behind the mouth follows the real tab (x from -12.392, y 7.02 to 17.92, z 11.85 to 13.60; C5d x from -11.887, y 7.65 to 17.29); it lies inside the wall behind the mouth.

## 8. Ring files read (read only), with dates

From `ls -lT` (r4/ring_files_dates.log): design/look/s1/out/ring-merged32h-us7.step to -us13.step and measures-merged32h-us7.json to -us13.json, all 2026-11-12 00:52 to 00:53; design/mech/thin/placement.csv 2026-11-13 04:18:08, changed by another helper DURING this work (after my baseline had read it at 04:07). Its four pad rows give the same values as the C5d build (row X -1.0, arc pitch 2.3999954, face radius 9.4761251, arc positions +-3.59999 and +-1.19978: r4/placement_compare.log), so the pins did not move. The check reads the file again; if the pad rows change later, test 3 fails until the case is rebuilt.

## Not proven and limits

- Only a built unit can show these; each has a fixed start value and a named measurement, none is proven:
  - Clamp of the stack (foam 0.8 mm free, pressed into 0.4 mm): measurement: with the bottom plate screwed on, push a USB-C plug in and pull it out 10 times; the socket front must stay behind the skin (straight edge across the mouth) and the board must not rattle when the closed case is shaken. If it moves: a thicker foam pad (1.0 mm).
  - USB-C pull: held by the clamp's friction; past that, the board's -X edge meets the cavity wall after 0.4 mm and the socket front would then sit 0.1 mm proud of the skin at its outermost corner. The friction force is not known.
  - Print tolerance of the retainer: posts and fence are modelled 0.02 mm from what they press; real printed parts differ (named measurement: the fence must touch the cavity wall and the board edge with the board in place; sand or shim 0.1 mm).
  - Wire, cell lead and thermistor diameters (0.50, 1.0, 0.30 and bead 1.6 mm) are start values, not from a maker sheet read here; wires are flexible and the modelled path is one possible path.
  - Where the cell's leads leave its PCM end (10 mm apart, 1.0 mm under the top face) is my reading of case_cell_dnk852338.pdf p.1; the red lead is put on the +X side.
- The part bodies are those the board author attached: KiCad library models (resistors, capacitors, U2, U5, J1) and plain boxes of the maker's size (U1, U3, U4, U6, L1, L2, LED1); no body for the 16 test pads, TH1, the wire pads and the cell (board-notes.md Round 2). The pin board's 4 pin cylinders in its STEP (2.8 mm, free height) are not used: the model keeps its own pins at their working compression; the check matches their axes to the pin board file (test 15a).
- The board's 3D bodies sit 0.005 mm into the board's top face in the STEP (z 0.995 on a 1.0 mm board); they are kept as one node `main_board` with the board, so the check does not count that overlap.
- The lift test screens with sampled points (ring 0.2 mm, case 0.1 mm) and measures exactly only the steps whose screen value is below 0.5 mm; a contact at a step whose screen is above 0.5 mm would need a sampling hole of more than 0.5 mm, which the sampling (edges every 0.2 / 0.1 mm, area / step^2 points inside each triangle) does not leave by construction, but this is not proven for every triangle.
- The outer spring pins graze the band at US 7 (common volume up to 0.000151 mm3 at US 7 in the debug run, under the 0.001 mm3 limit of tests 1, 2 and 17): the pins are modelled at their working compression; a real pin follows the band.
- The posts all sit on the half of the board away from the module (y above -0.60): the module half lies on the insulating sheet and is not pressed from above.
- Thinnest cavity wall 0.655 mm (box corners) at the board's corner on the socket side (section 7).
- design/ecad/case/pcb/geom.py parses case.py lines (PCB1, JY, LED_Y, the U1 box) and case_params.json (pcb1_x0 among them); the U1 box line is gone and pcb1_x0 moved by -0.505 mm, so rerunning build_boards.py would stop at geom.py's own assert. Finding for the board owner; I did not touch design/ecad.
- Pictures: none re-rendered (the outside is unchanged, section 7). Older than the model in an inside detail: look/case-open.png, case-open-empty.png, case-post-closeup.png and case-post-closeup-ring.png may show the floor under the pin holder, where the wire slot now starts at x 4.82 instead of 6.82; not checked whether it is visible in them.

## 10. Changed values and text lines

Values (source in brackets): main board 23.0 x 37.9 x 1.0 mm with a 1.85 x 10.2 mm tab (board file); pcb1_x0 -9.637 -> -10.142 (socket body front, board STEP); cavity at board level -X wall -10.037 -> -10.542, socket-side end 20.35 -> 20.6 (case.py BOARD_WALL_GAP, CAV_Y1); pin board inner island 3.9 -> 4.5 mm, wings 2.05..4.9 -> 2.35..4.9 (board file); holder island pockets and new wire recess 0.7 mm (case.py); floor slot x0 6.82 -> 4.82; light window inner end -10.242 (first r4 build) / -9.737 (C5d) -> -10.542; bezel recess inner end xs_j + 1.2 -> tab x - 0.35; new parts board_retainer, foam_pad, insulation_sheet, TH1_bead, 9 leads; part boxes U1, U2, U3, U4, U5, L1, L2, J1, LED1 replaced by the board's 59 bodies.
Text lines: case-bom.csv lines 17, 18, 22, 24, 25, 70 changed and items 98 to 100 added (r4/edit_bom.log, each old and new line); case-architecture.md lines 83, 92, 110, 125, 173, 176, 178, 179 and case-notes.md line 136 (r4/edit_docs1.log); case-architecture.md new section "Changes from C5d to C5d-r4", compartments, pin-holder "Back" and files lines, case-notes.md new section "C5d-r4" (r4/edit_docs2.py, log r4/edit_docs2.log, applied after the final check). Code: case.py, case_check.py (tests 5 adapted to the board node; new 15, 16, 17; CASE_CHECK_ONLY_R4 for the broken copies), new r4/case_boards.py, r4/board_read.py, r4/run_read.sh.


## 9. Proof runs

- Build of the delivered model into out/: r4/final_build.log, exit 0 (r4/final_build.done).
- Full check: r4/final_check.log ends `case_check: PASS, 8012 pairs checked, 0 failures, ring sizes US [7, 8, 9, 10, 11, 12, 13]`, exit 0, 05:55 to 07:37 (r4/final_check.done). Per-size lift results (r4/final_check_summary.log, from summarize_check.py):

| Size | Smallest free space (seat contacts left out) | Where, lift | Next | Seat contacts smallest | Steps where boundaries meet | Largest common volume |
|---|---|---|---|---|---|---|
| US 7 | 0.172 mm | shell (block pocket), 0.25 mm | liner 0.260 | 0.000 (pin P1 at 0.50) | 42 (pins P1, P4) | 0.000151 mm3 |
| US 8 | 0.175 mm | shell, 0.25 mm | liner 0.260 | 0.000 (pin P1 at 2.00) | 42 (pins P1, P4) | 0.000035 mm3 |
| US 9 | 0.182 mm | shell, 0.25 mm | liner 0.260 | 0.000 (pin P1 at 0.25) | 42 (pins P1, P4) | 0.000000 mm3 |
| US 10 | 0.188 mm | shell, 0.25 mm | liner 0.260 | 0.004 (pin P4 at 1.00) | 0 | 0.000000 mm3 |
| US 11 | 0.163 mm | shell, 0.25 mm | liner 0.260 | 0.008 (pin P4 at 4.75) | 0 | 0.000000 mm3 |
| US 12 | 0.141 mm | shell, 0.25 mm | liner 0.260 | 0.010 (flank faces at 2.00) | 0 | 0.000000 mm3 |
| US 13 | 0.121 mm | shell, 0.25 mm | liner 0.260 | 0.010 (flank faces at 1.50) | 0 | 0.000000 mm3 |

All 7 sizes meet the pass line (free space >= 0.10 mm, common volume <= 0.001 mm3). The smallest, 0.121 mm at US 13, is the block's guide in its pocket (designed 0.15 mm per side).
- Doc check: r4/final_docs.log `RESULT PASS (0 findings)`; after the r4 text of edit_docs2.py again r4/final_docs2.log `RESULT PASS (0 findings)`, exit 0.
- Broken copies (each its own build folder under r4/broken/, only the tests it targets; the last check line of each log, then the run wrapper's `end ... exit 1`):
  - Board 1 mm longer (outline end moved 1 mm toward +Y in a copy of the board file, r4/make_broken_boards.py; 3D model paths of the copy fixed by r4/fix_broken_text.py after the first try, whose build stopped with "footprints with a 3D model but no body in the STEP", r4/run1_broken_board_long_build.log): r4/broken_board_long_check.log `FAIL 15c main board to shell 0.000 mm`, `case_check: FAIL, 2746 pairs checked, 1 failures, ring sizes US [7, 8, 9, 10, 11, 12, 13] (only tests [15, 16])`.
  - J1 1 mm taller (model scale z 1.302115 in a copy, same fix): r4/broken_part_tall_check.log `FAIL 15b J1 to shell 0.000 mm (needs >= 0.3)` (and to usb_bezel, cell), `case_check: FAIL, 2746 pairs checked, 3 failures, ...`.
  - Wire run 0.6 mm lower (CASE_LEAD_FAULT=1): r4/broken_lead_low_check.log `FAIL 16 lead_W3 free room 0.000 to main_board bodies` (W4 0.038, W7 0.000), `case_check: FAIL, 2746 pairs checked, 3 failures, ...`. Test 15b did not flag these touches (its lead rule fails only on a common volume above 0.001 mm3); test 16 did.
  - Tooth on the dish wall in the lift path (CASE_LIFT_FAULT=1): r4/broken_lift_wall_check.log `FAIL 17 US 7: ring lifted 3.25 mm meets liner: common volume 0.3154 mm3`, 252 FAIL lines over the 7 sizes, `case_check: FAIL, 1714 pairs checked, 252 failures, ...`.

## 11. Pair count in the documents

check_case_docs.py takes the pair count from look/c5d_check_lead_rerun.log (3447, the lead's rerun of C5d); the documents keep quoting 3447 and give this version's 8012 as "pair checks" with that remark. When the lead reruns this version and replaces that log, the "3447 pairs checked" lines of case-architecture.md and case-notes.md must take the new count.

## 12. Added work after 07:19 (pin working height, contact file, transfer figures)

- Pin height (lead 07:19, maker range of P70-6000045R 1.90 to 2.20 mm, design/case/pin-travel.md): case.py now has PIN_H_MIN, PIN_H_MAX = 1.90, 2.20 and PIN_H0 = 2.05 (C5d 2.35); new check test 18 prints "pin working height inside 1.90 to 2.20" and "each pin over its pad, nets paired" per size and pin and writes the contact file. Trial build r4/pins_try (r4/pins_try_check.log, `case_check: PASS, 28 pairs checked, 0 failures, ... (only tests [18])`): heights P2, P3 1.980 (US 13) to 2.118 (US 7), P1, P4 2.039 to 2.042; pairing CP1 VBUS / P1 VRING, CP2 USB_DN / P2 USB_D-, CP3 USB_DP / P3 USB_D+, CP4 GND / P4 GND at every size, tip to pad 0.000 to 0.024 mm.
- Design error found: at those heights the OUTER pins' barrels (1.50 x 1.85) cut the band at every size, 0.0056 (US 13) to 0.0288 mm3 (US 7) (r4/quick_pins.log); scan r4/outer_pin_scan.log: at US 7 the outer pin clears the 0.001 mm3 limit only from 2.18 mm (0.00085), touch-free from 2.25. The outer pads sit about 22 degrees round the bore, so the band face is tilted under the barrel edge. First choice (a) therefore holds for P2, P3 only. Reported to the lead (two messages about 09:05 and 09:07) with options b1 (P70-7000045 on the outer pins, barrel length not in the saved documents) and b2 (outer wing islands turned square to the band); waiting for the ruling. out/ and design/wiring/ring-case-contact.csv are NOT written with the new heights.
- Transfer figures (lead 07:19): case-architecture.md section 1 now follows design/firmware.md line 718 (234.0 MB, 192.4 s = 3.21 min per recorded hour) and requirements.md row P2 (4.3 to 7.8 hours: 13.8 to 25.0 min); 6 lines changed, old and new in r4/edit_transfer.log; check_case_docs after it: r4/docs_after_transfer.log `RESULT PASS (0 findings)`.

## 13. Pin heights, as delivered (09:14 build of out/)

- Lead's ruling b2 (outer pins radial) was not built: radial outer pins put the P1 land centre 1.654 mm from the P2 land centre (r4/radial_pins.log), less than the 1.70 mm land, so the islands cannot both exist without changing the pin board. Reported 09:16.
- Cause of the barrel contact was the model, not the pin: the maker's drawing (P70-6000045R sheet 2) has a flange 1.50 x 0.40 at the board and a 1.06 mm body to 1.85; C5d modelled 1.50 x 1.85. case.py `PIN` and `make_pin` now follow the drawing. With it, the outer pin clears the band from 2.10 mm at US 7 (r4/outer_pin_scan_fine.log: 2.09 gives 0.00009 mm3, 2.10 gives 0.00002 mm3, only the tip; r4/outer_pin_scan_maker_body.log).
- Heights (case.py PIN_H0 2.05 for P2, P3 and PIN_H0_OUT 2.15 for P1, P4, at US 10): working heights per size (r4/pins_out_check18.log, design/wiring/ring-case-contact.csv):

| Size | P1 (CP1 VBUS / VRING) | P2 (CP2 USB_DN / USB_D-) | P3 (CP3 USB_DP / USB_D+) | P4 (CP4 GND / GND) |
|---|---|---|---|---|
| US 7 | 2.139 | 2.118 | 2.118 | 2.139 |
| US 8 | 2.146 | 2.096 | 2.096 | 2.146 |
| US 9 | 2.149 | 2.073 | 2.073 | 2.149 |
| US 10 | 2.150 | 2.050 | 2.050 | 2.150 |
| US 11 | 2.149 | 2.027 | 2.027 | 2.149 |
| US 12 | 2.146 | 2.003 | 2.003 | 2.146 |
| US 13 | 2.142 | 1.980 | 1.980 | 2.142 |

  All inside the maker's 1.90 to 2.20; left over: P2, P3 +-0.08 mm, P1, P4 +-0.05 mm (2.10 body clearance to 2.20), below the lead's +-0.07 target for the outer pins. Tip to pad centre 0.000 to 0.024 mm. Pin against ring at every size: largest common volume 0.000151 mm3 (r4/pins_out_quick.log), no part pair of pins, holder, post, islands, liner, shell intersecting.
- Contact file design/wiring/ring-case-contact.csv: written by case_check test 18 from out/ (header + 28 lines, 28 `yes`); pairing from coordinates: CP1 VBUS / P1 VRING, CP2 USB_DN / P2 USB_D-, CP3 USB_DP / P3 USB_D+, CP4 GND / P4 GND at every size. Ring names: band-interface.md lines 37, 38, 80, 81; case names: the pin board file.
- Broken copies of test 18: two middle pins swapped (CASE_PIN_SWAP=1): r4/broken_pin_swap_check.log `FAIL 18 US 7: CP2 USB_DN under P3 USB_D+ offset 0.001`, `case_check: FAIL, 28 pairs checked, 14 failures, ...`; old heights 2.35 (CASE_PIN_H0 and CASE_PIN_H0_OUT 2.35): r4/broken_pin_high_check.log `FAIL 18 US 7: P1 height 2.339`, `case_check: FAIL, 28 pairs checked, 28 failures, ...`.
- Builder's depth-gauge and shim step: case-architecture.md section 7 (nominal free tip stand-out 1.170 mm for P2, P3 and 1.021 mm for P1, P4, r4/pin_gauge.log; shim 0.025 / 0.05 / 0.10 mm behind an island, or lap the lug face).
- Documents: case-architecture.md lines 60, 104, 123, 219 (two sentences), 256; case-notes.md lines 42 (M4), 58 (A3), 88; case-bom.csv line 16; old and new in r4/edit_pins_docs.log (source file names in r4/edit_srcname.log). check_case_docs: r4/docs_after_pins.log `RESULT PASS (0 findings)`.
- Full check of this model: r4/pins_full_check.log ends `case_check: PASS, 8035 pairs checked, 0 failures, ring sizes US [7, 8, 9, 10, 11, 12, 13]`, exit 0 (09:18:40 to 10:28:38); lift results unchanged from section 9 (r4/pins_full_check_summary.log); doc check r4/pins_docs.log `RESULT PASS (0 findings)`.

## questions_for_owner

none

RESULT: done, both routed boards are in the model, the pins work inside the maker's 1.90 to 2.20 mm (P2 P3 1.980 to 2.118, P1 P4 2.139 to 2.150) with every pin over its own pad, case_check passes with 8035 pairs and 0 failures at US 7 to 13 including the lift out, and every broken copy fails its test.
