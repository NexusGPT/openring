# Ring main board (W2), round 2: notes

Written 2026-11-13 from 04:22 (clock: `date`). Handover: `board-notes.md` (round 1). Evidence of this round: `evidence/r2/` beside this file (named R2 below). Before copies of every file I changed: `R2/before/`. Checklist of the brief: `R2/CHECKLIST.md`.

## Step 0. Base (before any change)

- Round 1's delivered board, `kicad-cli pcb drc --severity-all --all-track-errors` on `ring.kicad_pcb`: `R2/base/base_drc.log`, `Found 13 violations`, `Found 22 unconnected items` (a first run on a copy without the project files beside it gave 1883 violations from KiCad's default rules; it is in the same log and is not a result).

## Step 1. Circuit changes (rulings a and b)

- `../make_netlist.py`: U1 balls B5 (DBG_RX), B9 (SPARE_P2_03), G4 (SPARE_P3_05), H4 (JOY_CENTER) no-connect; TP2, TP13, TP16, TP22 removed (TP2 and TP13 in the not-placed list, they are in the frozen bom snapshot; TP16's addition row removed); C21, C26, C27 Murata GRM155R61A475MEAAD 0402, C25 Murata GRM155R60J106ME15D 0402 (`../../../datasheets/w1d_murata_grm155r61a475meaa.pdf`, `w1d_murata_grm155r60j106me15.pdf`; `u4-capacitors.md` section 3). DBG_TX (TP1) and the SWD pads stay. Run: `R2/a_make_netlist.log`, `netlist rows 407 parts 113 nets 87`, `exit 0`.
- `../run_all.sh w2r2`: `R2/a_run_all.log` ends `run_all exit 0`; ERC `** ERC messages: 0  Errors 0  Warnings 0` (`../erc-report.txt` line 22); `check_netlist exit 0`, `RESULT PASS netlist netlist.csv` (`../evidence/check_w2r2.log`).
- `../check_netlist.py`, expected values changed by ruling b (each named in the file): `W2_OPEN` gets B5 DBG_RX, B9 SPARE_P2_03, G4 SPARE_P3_05, H4 JOY_CENTER; the P3.05 check wants G4 no-connect and TP16 absent (before: G4 on TP16); check A5-4 wants H4 no-connect and JOY_CENTER absent (before: H4 on TP22).
- `footprint-sources.csv`: C21, C25, C26, C27 rows Chip_0402; TP2, TP13, TP16, TP22 rows removed (`R2/edit_footprint_sources.log`). `check_footprints.py`: `R2/b_check_footprints.log`, `RESULT PASS 113 parts, 19 footprints, 407 pins have pads, pad counts equal footprint-sources.csv, no PROVISIONAL`, `exit 0`.
- `design/bom.csv` (rows these changes touch): C21, C26, C27 line 0402 GRM155R61A475MEAAD; C24, C25 line split (C24 stays 0603 GRM188R61C106KAALD; C25 0402 GRM155R60J106ME15D); test pad lines without TP2, TP13, TP16, TP22 (`R2/edit_bom.log`). `tools/check_bom.py`: `R2/a_check_bom.log` ends `FAIL designator RC1 is in netlist.csv or placement.csv and missing from the parts list`, `exit 1`. Already there: RC1 is the radio corner row 49 of `design/mech/thin/placement.csv` (not a part of this board), and the same check on the bom.csv before my change fails on it too (`R2/a_check_bom_before.log`). Who acts: the lead (a bom.csv line or the non-electrical list for RC1).

## Step 2. Placement (rulings a, c, e)

- `placement-final.csv` (plan columns): the plan's current table `design/wiring/ring-board-plan-work/placement-plan.csv` (round 4) less TP2, TP13, TP16, TP22 (ruling b), with round 1's pin-order rotations L2, L3, L4, X1 at 180 written into the rows (`R2/c_placement_step0.log`), and one move: C60 from (-4.35, 4.00, 0) to (-5.60, 5.30, 90), because its GND pad closed the VBAT exit stack of tail B land 1 at (-3.75, 3.875) of plan f.3 (`R2/moves.log`). `build_board.py` reads this file and has no override list any more; `check_board.py` check 5 compares with it.
- Placement checks on it (called as in plan R3.2 and R4.3, with KiCad's Python): `check_placement.py` `R2/s1/check_placement.log` `RESULT PASS` (100 parts, 85 parts face, 15 screen face); `capdist.py` `R2/s1/capdist.log` `RESULT PASS`.
- Ruling c (X2 beside B6, B7) cannot be met in the current table: the strip between U1's courtyard (Y -1.36) and U4 / L10 (Y -2.65) is 1.29 mm and holds the coil L1, which is a must part 1.03 mm from A5; X2's courtyard is 1.74 x 2.54. Trial table `R2/x2trial/placement-x2north.csv` (X2 at (4.16, -2.005) in L1's place, L1 to X2's old place): `check_placement.py` `RESULT FAIL 4` (X2 overlaps U1, U4, C21; L1 overlaps R57), `capdist.py` `RESULT FAIL 2` (L1 6.34 mm and C6 5.32 mm against the 1.5 mm must). X2 stays at (6.00, 4.25).

## Step 3. Scripted copper (route_fixed.py) and the router (finish_route.py)

Changes, each tried on the U1 piece first (router limited to 15 nets round U1 with `ONLY_NETS`, logs `R2/s1` to `R2/s6`, `piece*.log`):
- B5, B9, G4, H4 rows of table a.3 read as no-connect (`route_fixed.py`, `check_escapes.py`; expected value of check_escapes changed by ruling b).
- The antenna line is scripted before the ball escapes (U1 E1's ground stack had landed in its 0.20 gap); ground escapes are scripted after the signal escapes; a ground stack is looked for at the escape's far end first and is always joined by a checked track (round 1 could leave a stack unjoined).
- U1 F1, G1: the L1-L3 stack of a.2 is made only where there is room (C5 and C7 of the round 4 table stand west of the F and G balls): G1 at X 2.30; F1 ends as an L1 stub and the router crosses the antenna line.
- U1 signal escapes on L1 end 0.15 mm past the body (plan: "up to 0.50"); U1 and U2 escapes on L2 and L3 end 0.10 mm past the outermost ball site of their line. With 0.5 mm stubs in the same column on three layers the router found no via place (`R2/s1/piece1.log` to `R2/s3/piece4.log`).
- U1 A7 (ground) is 0.10 mm wide where it passes between the two pads of the coil L1 (0.098 mm to each pad); at 0.15 it stopped 0.650 short.
- `finish_route.py`: short nets first; join limit per net = its group count + 4, at least 12 (ruling f: VDD_1V8 is not stopped after 12 joins; no scripted trunk); free escape ends of open nets are protected like pins (cost x12 near them on every layer; pads x4); A* weighted 1.3 with an expansion limit of 3,000,000.
- Result on the piece: `R2/s6/piece8.log`, `first pass: failed 1 ['XL2']` (15 nets; the first piece run, before the escape and halo changes, `R2/s1/piece1.log`, failed 5 of 12).

## Step 4. Full rebuild 1

- `make_board.sh` started 04:53 with `nice -n 19` in the background; log `R2/full1/make_board.log`, exit code in `R2/full1/make_board.done`, its build logs copied to `R2/full1/build-logs/` when it ends.
- `check_escapes.py` on the scripted board: `R2/s6/check_escapes.log` `RESULT PASS`.
- Ended 05:07:24 (`R2/full1/start.txt`), exit 1 (`R2/full1/make_board.done`). Rules check: `R2/full1/make_board.log` `Found 32 unconnected items`; `check_board.py` last line `RESULT: FAIL, 1 problems` (check 7: 15 violations, 13 track_dangling and 2 via_dangling; checks 1 to 6 pass). Open connections `R2/full1/open_nets.txt`: VDD_1V8 20, DECD 3, GND 2, MIC_A_CLK 2, SD_SCK 1, SD_MOSI 1, XL2 1, LCD_DCX 1, LCD_RST 1. Screen nets at J1: 2 (LCD_DCX, LCD_RST); all other nets: 30.
- Causes read from the router log and the board (`R2/full1/build-logs/3_finish_route.log`, `R2/full1/dbg_e10.log`): VDD_1V8's first failed group (U1 E10's stub, walled by C1's GND pad ahead and by SD_MISO and OLED_PWR_EN routes made before it) ended the whole net, so 18 other joins were never tried; DECD's A6 stub was walled the same way.

## Step 5. Changes after run 1 (tried on 20 nets round U1 first, `R2/s7/piece9.log` to `piece11.log`)

- `finish_route.py`: in the first pass a failed group no longer ends the net; the other groups are still joined. The own track's centre cells count as own copper. A hard keep-clear round other nets' escape ends was tried (`piece9`, `piece10`: 8 nets failed) and is off (`END_HARD`); the cost halo stays (`piece11`: 5 failed).
- `placement-final.csv`: C1, R71, C2 at 270 (round 1's pin-order corrections; their positions are unchanged in the round 4 table), so that U1 E10 runs into C1's VDD_1V8 pad and U2 E2 into R71's VSET1 pad. Checks: `R2/s8/check_placement.log` `RESULT PASS`, `R2/s8/capdist.log` `RESULT PASS`.
- `route_fixed.py`: an escape whose line crosses a pad of its own net within 2.5 mm runs into it (U1 A5 into the coil L1's DCC pad, U1 E10 into C1, U2 E2 into R71). `check_escapes.py`: `R2/s8/check_escapes.log` `RESULT PASS`.

## Step 6. Full rebuild 2

- `make_board.sh` started at the time in `R2/full2/start.txt`, `nice -n 19`, log `R2/full2/make_board.log`, exit code `R2/full2/make_board.done`.
- Ended (`R2/full2/start.txt`), exit 1. `R2/full2/make_board.log`: `Found 10 unconnected items`; `check_board.py` `RESULT: FAIL, 1 problems` (check 7: 9 violations: 1 clearance 0.0744 mm at a PMIC_SCL via beside R71's GND pad, 2 via_dangling, 6 track_dangling). Open (`R2/full2/open_nets.txt`): GND 2, OLED_PWR_EN 2, MIC_A_CLK 2, SD_SCK 1, XL2 1, LCD_DCX 1, LCD_RST 1. Screen nets at J1: 2 (LCD_DCX, LCD_RST); all other nets: 8.
- Every open signal end is a U1 escape stub walled in by routes made before it; the rip-up round made no progress (`R2/full2/build-logs/3_finish_route.log`: `rip-up round 0 failed 6`).

## Step 7. Changes after run 2

- `finish_route.py`: nets with an open escape end at U1 or U2 are routed first; a via's far layer counts as a free end (U1 G1's L1-L3 stack and F2's L2-L3 via were left dangling in run 2 because the route joined elsewhere); raster margin 0.025 (was 0.02: the 0.0744 gap). Tried directly in a full run (a full run now takes about 11 to 14 minutes, against 42 in round 1).
- Full rebuild 3: `R2/run_full.sh full3` (make_board.sh with `nice -n 19`), log `R2/full3/make_board.log`, exit code `R2/full3/make_board.done`.
- Run 3 ended (`R2/full3/start.txt`), exit 1. `R2/full3/make_board.log`: `Found 10 unconnected items`; `check_board.py` `RESULT: FAIL, 1 problems` (check 7: 6 violations, 1 clearance 0.0744 mm, the same via as run 2, and 5 track_dangling). Open (`R2/full3/open_nets.txt`): GND 3, MIC_A_CLK 2, OLED_PWR_EN 2, XL2 1, LCD_DCX 1, LCD_RST 1. Screen nets at J1: 2; all other nets: 8 (3 of them ground).
- Ground pieces cut off (`R2/full3/gnd_islands.log`, my script `R2/gnd_islands.py`): U1 E1 with its L1 stub; U1 D3 with its L2 piece; U4 A3, B2, B3 with a stack whose L4 piece is cut off by L4 tracks (275 L4 segments, `R2/full3/stats.log`).
- Found while checking run 3: plan d.1 wants L2 solid under the antenna line and 0.50 mm each side, with no L2 track under it. Round 1's board does not meet it: `R2/rf_l2.py` gives `RESULT FAIL 90` on it (`R2/base/rf_l2_r1.log`, rerun at 08:06). Run 3's board failed it too (my first look, printed and not saved; that board was overwritten by run 4). Some of the items are the plan's own f.3 stacks, for example VBAT at (-3.75, 3.875), 0.415 mm from the line.
- U1 F1 (MIC_A_CLK) and E1 (ground) are boxed in by C7 at (1.95, 0.522): the plan's F1 crossing stack at X 1.70 has no room. `R2/find_spot.py` finds no other place for C7 within 4 mm of A8 (`R2/find_c7_4.log`: `places found 0`); its should-limit is 3.0 mm and it stands at 2.96.

## Step 8. Changes after run 3

- `finish_route.py`: pads rasterised 0.02 mm larger (the 0.0744 gap); L4 cost 5 (was 2), so the ground plane is cut only where nothing else passes; no L2 copper of another net under the antenna line or the USB pair or within 0.20 mm of their edge (plan d.1, d.2; 0.20 and not 0.50, because the plan's own f.3 stacks stand 0.415 from the line).
- `route_fixed.py`: U1 D3's L2 ground track ends in an L2-L4 stack.
- Full rebuild 4: `R2/run_full.sh full4`, log `R2/full4/make_board.log`, exit code `R2/full4/make_board.done`.
- Run 4 stopped by me at 06:40 (`R2/full4/stop.log`): its first pass left 12 nets open (`R2/full4/3_finish_route_stopped.log`: `first pass: failed 12`), against 7 in run 3.

## Step 9. Run 5 and run 6

- Run 5: L2 keep-clear only under the antenna line (0.075 from its edge, not under the USB pair), L4 cost 3. Stopped by me at 06:52 (`R2/full5/stop.log`): its first pass was worse than run 3 (failures listed in the stop log). So the router does not enforce plan d.1's L2 rule (switch `L2KEEP`, off); the measurement stays in "Not closed".
- Run 6: run 3's router settings (L4 cost 2.0, no L2 rule) with the pad raster fix and D3's L2-L4 stack. `R2/run_full.sh full6`, log `R2/full6/make_board.log`, exit code `R2/full6/make_board.done`.
- Run 6 stopped by me at 07:28 (`R2/full6/stop.log`): `first pass: failed 12` (`R2/full6/3_finish_route_stopped.log`); the Mac's load was 34 to 60 (`uptime` at 07:15), runs took twice as long. The pad raster change was the difference from run 3's settings and is removed again; the 0.0744 gap is handled by a via margin of +0.01 mm instead.
- Run 7: run 3's settings, via margin +0.01, D3's L2-L4 stack. `R2/run_full.sh full7`, log `R2/full7/make_board.log`, exit code `R2/full7/make_board.done`.
- Run 7 ended 07:52:39 (`R2/full7/start.txt`), exit 1 (`R2/full7/make_board.done`). (It was the delivered board until J1 moved; run 9 replaced it.) `R2/full7/make_board.log`: `Found 9 unconnected items`; `check_board.py` (`R2/full7/build-logs/5_check_board.log`): checks 1 to 6 pass, check 7 `rules check: 5 violations, 9 unconnected`, last line `RESULT: FAIL, 1 problems`. The 5 violations are track_dangling: the open ends of the escapes below (`R2/full7/drc-report.txt`). Rip-up: `R2/full7/build-logs/3_finish_route.log`, `rip-up round 1 failed 5`.
- Counts (`R2/full7/stats.log`): 100 footprints, segments F.Cu 398, In1.Cu 2251, In2.Cu 2946, B.Cu 271; vias by span F.Cu-In1.Cu 116, F.Cu-In2.Cu 68, F.Cu-B.Cu 75, In1.Cu-In2.Cu 84, In1.Cu-B.Cu 32, In2.Cu-B.Cu 65; 281 locked items.

## Step 10. Checks on run 7's board (before J1 moved)

- Broken copies of `make_broken.py` on the delivered board, each `check_board.py` exit 1 on its own fault (`R2/broken/check_<kind>.log`): net `FAIL 2 U1 pad A4 net 'GND' but netlist says 'VDD_1V8'`; outside `FAIL 4 C79 pad 1 centre outside the outline`; track (VDD_SD 7.475 mm on In1.Cu deleted) `10 unconnected items`, one more than the board's 9; missing `FAIL 1 C5 has 0 footprints`; antvia `FAIL 4 via (GND) inside the antenna copper-free zone at (-11.000, 4.000)`; swap `FAIL 6 check_escapes.py exit 1: FAIL U1 B4: via ('L1', 'L3'), plan ('L1', 'L2')`. No new check was added to `check_board.py` (its table path changed, check 5), so no new broken copy.
- Placement table: `R2/s8/check_placement.log` `RESULT PASS`, `R2/s8/capdist.log` `RESULT PASS` (the table before J1 moved; after it: `R2/j1/check_placement.log` and `R2/j1/capdist.log`, both `RESULT PASS`). The broken copies were not rerun on run 9's board (time).
- Band boards: `R2/a_check_band.log` `RESULT: PASS boards checked 14`. Note: that check rewrote the band folder's 14 `flex*-drc.rpt` report files (it writes them by design; list `R2/band_files_rewritten.txt`); I found this after the run. I changed no band board or script.
- Firmware check against the new netlist: `R2/firmware_check.log` `0 failures`, `exit 0`.
- Plan d.1 measure on the delivered board: `R2/full7/rf_l2.log` `RESULT FAIL 215` (L2 copper of other nets within 0.50 mm of the antenna line edge; round 1's board: `RESULT FAIL 90`, `R2/base/rf_l2_r1.log`).

## Step 11. J1 on the screen face (owner's decision, lead's message after run 7) and the lead's rulings

- Read `design/wiring/screen-cable-study.md` 4.3 (layout C) and 5. J1 (same part) on the screen face at (-4.933, -0.003), rotation 270 on the flipped footprint: the 0.8 mm land row (contact 1, the FPC entry) is then at X -3.533, toward +X (`R2/j1/j1_rot.log`, all four rotations). The footprint's origin is the land centre, so the centre entered is the study's (-4.933, -0.003). The plan's geometry gives the courtyard X -6.608 to -3.258, Y -3.053 to 3.047 (`R2/j1/apply_j1.log`); the study's housing is X -6.533 to -3.333, Y -3.053 to +3.047.
- Test pads: with TP2, TP13, TP16, TP22 gone (ruling b), all 15 remaining pads lay under J1 (the study counted 16 of 19). They moved to a 3 x 5 grid on the screen face, X -2.65, -1.60, -0.55 and Y -2.10 to 2.10 (1.05 pitch). Each keeps its number and net (`R2/j1/apply_j1.log`). The grid is between J1 and the antenna line's X 0.00 leg, out of the tail keep-outs, and close to U1, where most of their nets come from.
- `placement-final.csv`: checks `R2/j1/check_placement.log` `RESULT PASS` (100 parts, 84 parts face, 16 screen face) and `R2/j1/capdist.log` `RESULT PASS`. The check already reads the face column (side B); nothing had to change in it. The table before this step: `R2/j1/placement-final-before-j1.csv`.
- J1's lands on L4: the L4 ground zone keeps its 0.10 clearance round every pad of another net, so the plane opens there by itself. J1's GND pins 13 to 15 join the plane directly.
- J1's mounting pads to ground: NOT done. They have no net in the netlist (`FPC_15` has 15 pins). Putting them on GND needs a 16th symbol pin, and that changes check A5-8 of `check_netlist.py`, which wants exactly 15. That is a change of an existing check's expected value; I left it for the lead. The time left also limited this.
- Ruling on the antenna line (run 5's rule): `finish_route.py` keeps L2 copper of other nets 0.075 mm clear of the line (switch `L2KEEP`, now on by default). The numbers the lead asked for come from `R2/line_report.py` on the delivered board (step 12).
- Full rebuild 8 (J1 on the screen face, L2 rule on): `R2/run_full.sh full8`, log `R2/full8/make_board.log`, exit code `R2/full8/make_board.done`. Scripted copper: `R2/full8/build-logs/2_route_fixed.log`.
- Run 8 ended 08:34 (`R2/full8/start.txt`), exit 1. `R2/full8/make_board.log`: `Found 15 unconnected items`; `check_board.py` `RESULT: FAIL, 2 problems` (`R2/full8/build-logs/5_check_board.log`): check 6 `FAIL U1 D10: via ('L2', 'L4'), plan None` (a router via at D10's land centre) and check 7 (10 violations: 2 clearance 0.0636 mm between a VDD_1V8 track and a DBG_TX via near U1 A4, 3 via_dangling, 5 track_dangling). Open (`R2/full8/open_nets.txt`): VBAT 5, VMOT 2, MIC_A_CLK 2, OLED_PWR_EN 2, GND 1, BTN_REC 1, XL2 1, LCD_MOSI 1 (screen net at J1: 1; other nets: 14).
- Change after run 8: `finish_route.py` places no via within 0.10 mm of a U1 or U2 ball centre. Full rebuild 9: `R2/run_full.sh full9`, log `R2/full9/make_board.log`, exit code `R2/full9/make_board.done`.

- Run 9 ended 09:09:03 (`R2/full9/start.txt`), exit 1. This is the delivered `ring.kicad_pcb`. The rules check rerun on it at 09:09 (`R2/final_drc9.log`) gives `Found 7 violations` and `Found 18 unconnected items` (2 via_dangling, 5 track_dangling, `R2/final_drc9.txt`). `check_board.py`: checks 1 to 6 pass, check 7 `rules check: 7 violations, 18 unconnected`, last line `RESULT: FAIL, 1 problems` (`R2/full9/build-logs/5_check_board.log`). Run 8 (same placement, before the ball-via rule) ended at 15 unconnected items and 10 violations; it is not kept.

## Step 12. Numbers the lead asked for (delivered board, `R2/full9/line_report.log`, script `R2/line_report.py`)

- Antenna line, L1: closest other-net copper 0.169 mm from the line's edge (a DECA track); 51 items under 0.50 mm (ground copper counted).
- Antenna line, L2: closest other-net copper -0.017 mm, a DECA track that touches the area under the line's edge (overlap 0.017 mm), against the router rule. Cause not found in the time left. 76 items under 0.50 mm. The plan's 0.50 mm each side is not met.
- XL1: routed 8.36 mm (119 track pieces, 3 vias). Within 0.20 mm on In2.Cu: GND, PMIC_SDA, MIC_B_DATA, OLED_PWR_EN, SPARE_P2_00, SPARE_P1_02, PMIC_SCL, VDD_1V8, LCD_TE, SHPHLD (0.100 to 0.155 mm); XL2 on In1.Cu 0.162. Plan d.4: 0.20 from any other copper of the same layer: not met.
- XL2: not routed. Only its 0.43 mm escape exists.

Note: the lead's messages "finish run 8 only", "board closed by 09:20" and "C7 spot taken by C5" reached me at 09:10, after run 9; run 9 went against the first of them.

## Step 13. Placement round near U1 (lead's message after commit ca4d5f3c, 60 minutes)

- Moved to the screen face, each at its own X, Y and rotation (`R2/r3/move_b.log`): C1 (VDD_1V8 100 nF at U1 E10), C2 (VDD_1V8 at U2 E4), C14 (DECA), R71, R72 (VSET resistors), C5 (VDD_1V8 100 nF at A4), C7 (DECA), FB1 (DECD-DECA ferrite). Only C7 has a distance limit (should 3.0 to A8): `R2/r3/capdist.log` `C7 should 3.0 2.96` (X, Y distance; the screen face adds the board's 0.30). Checks: `R2/r3/check_placement.log` `RESULT PASS` (76 parts face, 24 screen face), `R2/r3/capdist.log` `RESULT PASS`. Table before: `R2/r3/placement-final-before-r3.csv`.
- U10 beside U1 (ruling d): not done. The strip between U1 and U2 is 1.5 mm wide and U10's courtyard is 2.54 x 3.34. U10 is an IC, so the screen-face ruling (passives up to 0.6 mm) does not cover it.
- Effect on the scripted copper (`R2/r3/2_route_fixed.log`): U1 F1 gets the plan's L1-L3 stack at X 1.70; U1 E1's ground escape runs its full 1.0 mm; U1 E10 and U2 E4 (both VDD_1V8) run into each other's lands along Y 0.00 on L1. `check_escapes.py`: `R2/r3/check_escapes.log` `RESULT PASS`.
- Piece run round U1 (22 nets, `R2/r3/piece12.log`): `first pass: failed 3 ['OLED_PWR_EN', 'VDD_1V8', 'XL2']` (before the E10-E4 join).
- VBAT and VMOT: no scripted crossing was written; they stay with the router (on L3 and L4 they may cross the antenna line).
- J1's mounting pads stay unconnected in this round (lead's message).
- Full rebuild 10: `R2/run_full.sh full10` (`nice -n 19`), log `R2/full10/make_board.log`, exit code `R2/full10/make_board.done`.
- Run 10 ended 09:43 (`R2/full10/start.txt`), exit 1. `R2/full10/make_board.log`: `Found 11 unconnected items`; violations 8 (3 via_dangling, 5 track_dangling, `R2/full10/drc-report.txt`); `check_board.py` checks 1 to 6 pass, check 7 fails, `RESULT: FAIL, 1 problems`. Open (`R2/full10/open_nets.txt`): DECD 3, U1_VBUS 2, OLED_PWR_EN 2, MIC_A_CLK 2, XL2 1, LCD_MOSI 1 (J1: LCD_MOSI; no ground piece and no VBAT open any more). Its board is kept as `R2/r3/ring_run10.kicad_pcb`.
- Change after run 10: `finish_route.py` routes run 10's open nets first (DECD, U1_VBUS, LCD_MOSI, OLED_PWR_EN, MIC_A_CLK, XL2, XL1). Full rebuild 11: `R2/run_full.sh full11`, log `R2/full11/make_board.log`.

- Run 11 ended 09:58 (`R2/full11/start.txt`), exit 1: `R2/full11/make_board.log` `Found 28 unconnected items` (VDD_1V8 19, MIC_A_DATA 2, GND 1, SD_SCK 1, SD_MOSI 1, BTN_REC 1, MOTOR 1, LCD_DCX 1, LCD_SCK 1; `R2/full11/open_nets.txt`). The open nets moved, as the other helpers saw. The ordering is off again (switch `FIRST_NETS`), and run 10's board is restored as `ring.kicad_pcb` (`R2/r3/restore.log`).
- Delivered board (run 10, restored), rules check rerun 09:58 (`R2/r3/final_drc10.log`): `Found 8 violations`, `Found 11 unconnected items`; `check_board.py` (`R2/r3/check_board10.log`): checks 1 to 6 pass, `rules check: 8 violations, 11 unconnected (7)`, `RESULT: FAIL, 1 problems`, `exit 1`. `build-logs/` beside the board holds run 11's logs; run 10's are in `R2/full10/build-logs/`.
- Numbers on the delivered board (`R2/r3/line_report10.log`): antenna line L1 closest other-net copper 0.169 mm (DECA), 53 items under 0.50 mm; L2 closest 0.034 mm (an NRESET track, beside the line, not under it), 51 items under 0.50 mm. XL1 routed 8.37 mm with DECA, MIC_B_DATA, PMIC_SDA at 0.097 mm and other nets within 0.20 mm on In1.Cu; XL2 not routed beyond its 0.43 mm escape.

## Not closed

Delivered board: run 10 (J1 on the screen face, eight passives on the screen face). On 4 copper layers, 0.30 mm, it has 11 unconnected items and 8 violations (3 via_dangling, 5 track_dangling, all at open ends). Screen nets at J1: 1 (LCD_MOSI). All other nets: 10. Ends (model mm, `R2/full10/open_nets.txt`):
1. LCD_MOSI (J1): U1 G8 L2 escape end (4.65, 0.65 to 1.07) to J1 pad 12 on the screen face.
2. DECD (3): U1 A6 stub (4.00, -0.98) to the coil L1's pad 2 (5.15, -2.00), C6 (6.02, -1.74) and FB1 (1.98, 1.52, screen face). The A6 stub is walled in under L1's pad 1.
3. U1_VBUS (2): U1 H9 (4.97, 0.97) to C11 (5.21, 2.47) and R1 (12.80, -1.90).
4. OLED_PWR_EN (2): U1 E9 L2 escape end (5.40, 0.00) to U4 C2 (3.50, -4.05) and R66 (12.80, 0.98).
5. MIC_A_CLK (2): U1 F1 via its L1-L3 stack at X 1.70 to U5 (-11.47, -4.38) and U6 (11.47, -5.22).
6. XL2 (1): U1 B7 (4.32, -0.65) to X2 pad 2 (6.72, 4.25).
Each open end is a U1 escape walled in by routes made before it; changing the order only moves the failures (run 11). What would close them: hand-planned scripted paths for these six nets in `route_fixed.py` (allowed by the lead), U10 beside U1 (not possible on the parts face: the strip is 1.5 mm, U10 needs 2.54), or a negotiated router instead of the greedy one. Not done: the lead's 60 minutes ended at about 10:13.

Fabrication files: not made. `make_fab.sh` was not run; `fab/` does not exist.

## Changes other files need

- `design/wiring/ring-board-plan-work/placement-plan.csv`: replace it with `placement-final.csv` (the lead's step). Changes against the plan's table: TP2, TP13, TP16, TP22 removed; L2, L3, L4, X1, C1, R71, C2 rotated (round 1's pin-order corrections); C60 at (-5.60, 5.30, 90); J1 on the screen face at (-4.933, -0.003, 270); the 15 test pads in the grid of step 11; C1, C2, C14, R71, R72, C5, C7, FB1 on the screen face (step 13).
- Parts on both faces: J1 and eight 0201 passives on the screen face. Assembly: a second reflow pass; parts list side column: these nine parts on side B; test fixture: the 15 pads at their new places.
- J1's mounting pads on GND (left unconnected in this round, lead's message): a 16th pin MP on symbol FPC_15 in `make_netlist.py`, with check A5-8 of `check_netlist.py` changed with it.
- `design/wiring/ring-board-plan.md` a.3 rows B5, B9, G4, H4: "none" (ruling b).
- `design/firmware.md`: spare pins P2.03 (ball B9) and P3.05 (ball G4) are no longer connected.
- `design/architecture.md` section 7 table: DBG_RX, JOY_CENTER, P2.03, P3.05 are no longer on the board.
- `design/bom.csv` row PCB1: 4 layers any-layer HDI, 0.30 mm, 15 test pads, parts on both faces.
- `design/mech/thin/placement.csv` row RC1 needs a bom.csv line or the non-electrical list of `tools/check_bom.py`.
- `design/ecad/band/flex*-drc.rpt` (14 files) were rewritten by `check_band.py` (step 10); the lead restores them if needed.

questions_for_owner:
1. The last six nets at U1 need either hand-planned paths (hours of layout work) or a router that negotiates congestion; which one does the owner want for round 3?
2. Plan d.1's 0.50 mm beside the antenna line is not met (numbers above); is the bench measurement of the line enough for the first build?

RESULT: blocked, with J1 and eight passives on the screen face the 4-layer 0.30 mm board ends at 11 unconnected items and 8 violations (all at the open ends of six U1 escapes), so no fabrication files were made.
