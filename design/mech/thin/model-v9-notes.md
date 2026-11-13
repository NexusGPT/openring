# Inside model v9: board parts at the board plan's places, resin radio corner (notes, written while working)

Work started ven. 13 nov. 2026 03:28 CET (clock from `date`, out/v9/baseline_us9.log first line). Folder: design/mech/thin/. Every log and script named below is in out/v9/ of that folder unless a full path is given. No git command was run. No browser. Heavy runs at `nice -n 19`. Checklist: out/v9/CHECKLIST.md.

Development copies: out/v9/dev/thin.py and out/v9/dev/check_thin.py (the delivered files are written over only after the lead's own v8 runs, which import the delivered thin.py, have ended). The files as found are kept in out/v9/before/ (hashes out/v9/before/shasum_before.log).

## a. Baseline

Command: out/v9/run_check.sh 9 baseline (copy of out/v8/run_check.sh with the log folder out/v9; per-size exterior ring-merged32h-us9.step, bore 18.9452, nice -n 19), on the files as found (hashes out/v9/before/shasum_before.log; no git command was run, so the match with commit cdb1ddc is by the lead's statement, not checked here). Log out/v9/baseline_us9.log: first line `ven. 13 nov. 2026 03:28:41 CET`, last lines `RESULT PASS pairs=1080 parts=47`, `exit 0`, `ven. 13 nov. 2026 03:49:07 CET`. As expected. The lead's own runs (out/v8/v8c_*, out/v8/lead_us13.log) ran at the same time on the same files.

## b. Board parts against the board plan

Sources read (read only): design/wiring/ring-board-plan-work/placement-plan.csv (file time 02:41, round 4 table), design/ecad/ring/pcb/footprint-sources.csv, design/ecad/ring/pcb/OpenRing.pretty/*.kicad_mod. Reader: out/v9/board/fp_read.py, log out/v9/board/fp_read.log, table out/v9/board/board_rows.json. Comparison of the model as found (out/v9/before/placement.csv) with the plan: out/v9/board/compare_before.py, log out/v9/board/compare_before.log (last line `drawn parts compared: 16; differing: 12`).

Rows of the model as found (cdb1ddc) against the plan (lines of out/v9/board/compare_before.log; body size X x Y in the board frame from the footprint's F.Fab outline turned by the plan's turn; heights from the footprint's descr where it gives one):

| Ref | model part | model as found | plan | differs |
|---|---|---|---|---|
| ANT1 | antenna | (-12.700, 4.400), 1.600 x 3.200 x 1.200, in the board notch, no turn | (-10.800, 5.250), turn 180, 3.200 x 1.600, height 1.2 | place, body, turn (plan's list) |
| J1 | screen_connector | (-12.000, 0.000), 3.200 x 5.200 | (-11.650, -0.150), turn 270, 3.350 x 6.100 | place, body, turn (plan's list) |
| U4 | screen_supply_chip | (4.000, -3.500), 2.000 x 2.000 | (3.250, -3.800), turn 180, 2.005 x 2.005 | place, turn (plan's list) |
| L10 | screen_supply_coil | (6.500, -3.500), 2.500 x 2.000 | (6.500, -4.200), turn 90, 2.000 x 2.500 | place, body, turn (plan's list) |
| L71 | power_coil_1 | (8.500, 3.200), 2.000 x 1.600 | (12.020, 3.750), turn 0, 2.500 x 2.000 | place, body (plan's list) |
| L72 | power_coil_2 | (11.000, 3.200), 2.000 x 1.600 | (8.870, 3.750), turn 0, 2.500 x 2.000 | place, body (plan's list) |
| X2 | crystal_32k | (5.500, 3.000), 2.000 x 1.200 x 0.500 | (6.000, 4.250), turn 90, 2.000 x 1.200, height 0.6 | place, height, turn (plan's list; the height is found here) |
| U2 | power_chip | (8.500, 0.000), 3.100 x 2.400 | (8.500, 0.000), turn 270, 2.377 x 3.078 | body, turn (plan's list) |
| C84 | motor_cap_out | (1.200, 5.000), 1.000 x 0.500 | (1.270, 5.000), turn 90, 0.500 x 1.000 | place, body, turn (plan's list) |
| X1 | crystal_32M | (3.000, 3.000), 2.000 x 1.600 x 0.500 | same place, turn 0, 2.000 x 1.600, height 0.4 | **found here**: height 0.500 against the footprint's 0.40 (XTAL_Kyocera_CX2016DB descr "2.00 x 1.60 x 0.40") |
| U5 | mic_1 | (-10.800, -4.800), 4.000 x 3.000, no turn | same place, turn 90, same body | **found here**: turn (the lands and their pattern) |
| U6 | mic_2 | (10.800, -4.800), 4.000 x 3.000, no turn | same place, turn 270, same body | **found here**: turn (the lands and their pattern) |
| U1, U3, U11, C83 | main_chip, storage, motor_regulator, motor_cap_in | place and body as the plan | same | place and body same; **found here**: the lands (gold) of every drawn part were the model's generic pattern (U1 a 9 x 7 grid less 2 corners, U3 8 pads), not the footprint's pads (U1 61 lands with C1 and D3 off the grid, U3 9 lands) |

Board side: the plan's side B (the 19 test pads TP1 to TP22) is the screen face, flat copper with no height; the model draws no test pad (none of the 88 parts the model does not draw is checked here; the plan's own check_placement.log covers them). Every drawn part is side F, the board's under face in the model.

### b.1 What thin.py does now (out/v9/dev/thin.py, delivered as design/mech/thin/thin.py)

- Table `BOARD` (16 rows: footprint, X, Y, turn, F.Fab body size along the footprint's own axes, height where the footprint's descr gives one), copied from placement-plan.csv and the F.Fab outlines (values in out/v9/board/fp_read.log). The board frame follows the plan's convention: local (x, y) to (x cos t + y sin t, -x sin t + y cos t), model = KiCad - 100, no mirror (ring-board-plan.md R2.1: "at rotation 270 local +y points to -X").
- Each drawn part is built at its row (function `bpart`): body box centred on the row's place with the turned body size; the part's turn is kept in the part (`Part.rot`), written into the placement.csv note and into the GLB node extras (`rotation_deg`).
- Lands: every gold land of the board is a pad of the drawn parts' footprints (read at build time from design/ecad/ring/pcb/OpenRing.pretty, read only), placed with the same turn; the solder balls of U1, U2 and U4 stand on those lands (61, 35 and 16).
- Heights from the footprint descr: X1 0.40 (was 0.50), X2 0.6 (was 0.50); U5, U6 1.00, L10, L71, L72 1.0, ANT1 1.20, U11 0.4 unchanged. Parts whose descr gives no height keep the v8 height (U1 0.43, U2 0.5, U3 0.75, U4 0.58, J1 0.9, C83, C84 0.5).
- Coils and 0402 parts: the two metal ends stand along the footprint's own x axis (turned with the part). ANT1: four corner terminations 0.50 along the length x 0.30 across (descr: "terminals b 0.50 x a 0.30 at the four corners"), drawn over the full 1.20 height (ASSUMED wrap-around, the most metal for the free-space figures); v8 drew two 0.4 end caps.
- J1: housing 3.35 x 6.1 x 0.9 turned 270; latch bar on the +X side (the lever side, R2.1), 15 contacts on the -X side.
- Main board: no notch (core and mask are the full 27.2 x 12.6 outline with 0.8 corners).

## c. Radio corner (thin.py)

The body is cut after every pocket, the motor window included: `corner = (body & rc_box) - rc_pocket`, `body = body - rc_box`, with rc_box X -14.80 to -8.60, Y 2.05 to 12.0, Z -30 to 10 (all Z of the block; the band, X -4 to 4, is not reached) and the pocket box X -12.60 to -9.00, Y 4.25 to 6.25 from the floor top Z 0.40 down to Z 0.20 (ring-board-plan.md R2.0 item 5; lead-decisions.md row "W2, rule on places": "resin corner of the body to X -8.60, floor pocket X -12.60 to -9.00"). The corner is the part `radio_corner` (reference RC1, the name assembly.md line 62 already uses), layer body, one class `resin`. It is made last in build(), so the placement.csv rows that assembly.md cites by number (rows 12 to 48) keep their numbers: placement.csv gets one more row at its end.

## d. Named tests (check_thin.py section 14)

- `check_board_plan`: reads placement-plan.csv and the footprints itself (its own reader `_fp_read`, compared with fp_read.py in out/v9/board/parser_test.log: 16 footprints, `differences: 0`), never thin.P or thin.BOARD. For each of the 16 drawn parts (list `BOARD_DRAWN` in the check; any other part on the board layer, or one missing, is a finding): body centre (bounding box of every solid of the part except the marking plate) within 0.01 of the row's X, Y; body size X and Y within 0.01 of the F.Fab outline turned by the row's turn; height (land face Z 1.43 down to the body's lowest point) within 0.01 of the descr height where the footprint gives one; the part's declared turn equal to the row's (mod 360, 0.01); every footprint pad present as a gold land of the board at its turned place and size (0.01); for U1, U2, U4 a solder ball on every land. Prints one `BOARD-PLAN` line per part and the largest difference.
- `check_zone`: no solid of class metal or gold of any part other than ANT1 has more than 0.001 mm3 in the prism X -13.60 to -8.75, Y 3.10 to 6.30, Z -6 to 6 (the whole block), the board's gold lands there being accepted only where they are ANT1's own lands; the radio corner exists with the one class resin; prints every part with volume in the prism, the antenna's free space to the five nearest metal or gold solids, the room under the antenna, and the motor body's distance to the prism with the rule 1.0 mm (item 44; the lead's 1.0 mm in design/mech/mech-notes.md line 54).

## e. Runs so far (each with its expectation written before it, out/v9/expect_*.txt)

| Run | Command | Log | Last line(s) |
|---|---|---|---|
| named tests on the dev copy | out/v9/named_tests.py out/v9/dev out/v9/dev/check_thin.py | out/v9/named_dev1.log | `RESULT PASS`, `exit 0` |
| full check, dev copy, US 9 | out/v9/run_dev.sh 9 dev1 | out/v9/dev1_us9.log | `RESULT PASS pairs=1127 parts=48`, `exit 0` (03:50:32 to 04:06:20) |
| swap into place | out/v9/swap_in.sh | out/v9/swap_in.log | thin.py b0e69e1f..., check_thin.py 7cddd984... (same hashes as the dev copies) |
| build in place, default US 9 | `nice -n 19 .venv/bin/python thin.py` | out/v9/build_v9_us9.log | `exit 0`; 48 parts, 372840 triangles; placement.csv and layers.json equal to the dev build (out/v9/build_v9_shasum.log) |
| broken copy 1 (X2 moved 0.3 mm along X, one line: broken_place/broken_vs_final.diff) | out/v9/run_broken.sh | out/v9/broken_place/named_test.log | `BOARD-PLAN X2 ... model centre off (+0.3000, +0.0000) ... lands 0 of 2  FAIL`, `RESULT FAIL`, `exit 1` |
| broken copy 2 (the radio corner not cut from the metal body, one line: broken_zone/broken_vs_final.diff) | out/v9/run_broken.sh | out/v9/broken_zone/named_test.log | `ZONE holds metal: ['outer_body__metal 6.1823 mm3']`, `RESULT FAIL`, `exit 1` |
| control: the delivered files, named tests | out/v9/run_broken.sh | out/v9/named_final_control.log | `RESULT PASS`, `exit 0` |

The broken copies ran through the named tests alone (out/v9/named_tests.py imports the broken thin.py, then the delivered check_thin.py, and calls check_board_plan and check_zone), not through the whole check with the pair test, as in v8.

Earlier looks, all reported: out/v9/named_dev1.log and out/v9/dev1_us9.log (dev copy, the same code as delivered); broken copies first run against the dev check (same hash as the delivered check): out/v9/broken_place/named_test_dev.log, out/v9/broken_zone/named_test_dev.log (same results). out/v9/corner_probe.py was stopped by me after 11 minutes (pid 61642, out/v9/corner_probe_stopped.log: too slow); its log out/v9/corner_probe_dev.log holds only its start line. Scratch files deleted (out/v9/deleted_scratch.log): the fake STEP of item 104 and a copy of the v8 GLB; also, before any run, two text pieces I had written to paste code (out/v9/dev/board_block.py.txt, out/v9/dev/check_v9_block.py.txt) and a copy of out/v7-export/export_size.py used to derive out/v9/export/export_size.py (its diff: out/v9/export/export_size_v7_to_v9.diff).

## f. Radio corner: the metal left round it, and the antenna to metal (out/v9/corner_probe2.py on the delivered model, log out/v9/corner_probe2.log)

- RC1: volume 26.4216 mm3, X -14.650 to -8.600 (the block ends at -14.65), Y 2.050 to 7.375 (the skin), Z 0.000 to 2.750.
- Metal on the bond planes: plane X -8.60 one piece, Y 2.050 to 7.375, Z 0.000 to 2.750, 3.936 mm2; plane Y 2.05 one piece, X -14.650 to -8.600, Z 0.000 to 2.750, 3.588 mm2.
- Thinnest metal at the bond planes: 0.060 mm (sampled) on plane Y 2.05 at X -13.74 to -14.04, Z 2.65 to 2.71: the roof of the screen tail's fold pocket under the glass seat. Already there in v8: out/v9/sliver_probe.log, the v8 body (out/v9/before/thin.py) has metal only from Z 2.650 to 2.700 over that pocket at X -13.90 and every Y from 0.00 to 2.60; v9 the same up to Y 2.04 and resin from Y 2.06. Not caused by the corner; the corner ends that 0.05 roof at Y 2.05 as a bond face. Next thinnest: 0.380 mm, the floor at the bond planes (Z 0.03 to 0.41 at Y 6.41 on plane X -8.60 and at X -13.69 on plane Y 2.05).
- Antenna to the metal body 0.6000 mm (corner_probe2.log; the same line of the check, dev1_us9.log `ANTENNA free space to metal ... outer_body__metal 0.6000`), antenna to the resin 0.0300 mm (the room under it in the 0.20 pocket: antenna bottom Z 0.230, pocket bottom Z 0.20). Nearest other metal: main_board__gold 1.6000 (a land), screen_connector__metal 2.2000 (J1's latch bar).
- The copper-free zone prism holds, besides ANT1 and RC1, these non-metal parts (dev1_us9.log `ZONE: every part with volume in the zone prism`): main_board 4.6628 mm3 (pcb, mask and ANT1's own lands), foam 0.8220, screen 8.7478, screen_tail 0.5122, clear_adhesive 1.5520, cover_glass 11.2231. The screen_tail's bond on the ledge (X -13.675 to -12.775, Y up to 6.204, maker drawing) and the panel lie over the zone above the board: a flexible circuit with copper over the antenna, the open point S24 of the screen maker (ring-board-plan.md e.6 R3).

## g. Item 104: thin-inside.step read back by a fresh process (out/v9/item104/)

Side A (out/v9/item104/model_figures.py) builds the model in memory and writes per part and class the solid count and volume; side B (step_readback.py, a second process) reads the STEP and compares label by label (volume rule 0.01 mm3).

| File | Model in memory | Log | Last lines |
|---|---|---|---|
| v8 file as found (out/v9/before/thin-inside_v8.step, same hash as the delivered v8 file: out/v9/before/copy_v8_outputs_shasum.log) | v8 thin.py at the default US 9: 47 parts, 84 part classes, 403 solids | out/v9/item104/run_v8.log, out/v9/item104/readback_v8_us9default.log | `labels compared 84, differing 0`, `RESULT PASS labels=84` |
| v9 file (out/thin-inside.step) | v9 thin.py: 48 parts, 85 part classes, 417 solids | out/v9/item104/run_v9.log, out/v9/item104/readback_v9_us9default.log | `417 solids in the file, 417 in the model; labels compared 85, differing 0`, `RESULT PASS labels=85` |
| fake: the v9 file with one solder ball of main_chip__metal left out (make_fake.py) | v9 | out/v9/item104/readback_fake.log | `main_chip__metal: model 61 solids 0.2555 mm3; STEP 60 solids 0.2513 mm3 ... DIFFERS`, `RESULT FAIL labels=85` |

Answer: the v8 file was already complete (no solid lost); v9 writes fresh copies anyway. The maker files' read-back follows the export (section i).

## h. Writing in place, the parts list row for RC1, and how RC1 is made

Switch to the delivered files: at 04:17:24 `ps` showed no `run_check.sh ... v8c` and no `check_thin.py` other than mine (out/v8/lanes.done written 04:14:49); thin.py and check_thin.py were written in place at 04:17:42 (out/v9/swap_in.log), the model outputs at 04:17:54 to 04:18:16 (out/v9/build_v9_us9.log).

design/bom.csv and design/bom-notes.md were NOT edited (lead's correction). check_bom.py on the files as they stood at 04:25:20 (`design/.venv/bin/python design/tools/check_bom.py`, log out/v9/final/check_bom_0430.log), full output:

```
lines 85, designators 131, section-2 rows 19, section-2 part tokens 24, switch lines 2, pad lines 1, designators against model and wiring 131, failures 5
FAIL designator RC1 is in netlist.csv or placement.csv and missing from the parts list
FAIL designator TP13 is in netlist.csv or placement.csv and missing from the parts list
FAIL designator TP16 is in netlist.csv or placement.csv and missing from the parts list
FAIL designator TP2 is in netlist.csv or placement.csv and missing from the parts list
FAIL designator TP22 is in netlist.csv or placement.csv and missing from the parts list
exit 1
```

RC1 is mine. TP2, TP13, TP16, TP22 are not: placement.csv has 0 rows with TP (out/v9/final/check_bom_tp_source.log), and design/ecad/ring/netlist.csv was rewritten at 04:25 by the ring board lane while the check ran; the lead's message saw RC1 alone, so these four came with that rewrite (cause not checked further: outside my lane).

Row for design/bom.csv (columns item, reference, quantity, function, maker, maker_part_number, package, size_mm, value, key_figures, evidence, source_file_or_url, unit_price_and_currency_at_qty1, open_action; format of the SEAL2 and LNR1 rows):

```
Radio corner (resin),RC1,1,"resin part of the body round the antenna: the block's hand-end corner on the +Y side, X -14.80 to -8.60, Y 2.05 to the outer skin, full height, with a floor pocket 3.60 x 2.00 x 0.20 under ANT1 (design/wiring/ring-board-plan.md R2.0 item 5)",Master Bond,EP30Med,cast resin,"6.05 x 5.325 x 2.75 box, 26.42 cubic mm",,"no metal round the antenna: antenna 0.60 mm from the body metal; bonded to the metal body on the planes X -8.60 and Y 2.05; same resin as the liner (lead decision row liner resin)",CALC,design/mech/thin/model-v9-notes.md sections c and f ; design/mfg/specs/body.md section Radio corner RC1 ; design/mfg/parts/radio-corner/radio-corner.step,,"S24: colour match to the gloss black coating, seam sealing (S6), bench T0 T1 T2 of design/mech/antenna/antenna-study.md section 6"
```

Line for design/bom-notes.md: `- RC1 (radio corner, inside model v9): resin part of the body round the antenna, X -14.80 to -8.60, Y 2.05 to the skin, 26.42 cubic mm (design/mech/thin/model-v9-notes.md section f); resin Master Bond EP30Med as the liner (lead-decisions.md row "liner resin"); made before the board goes in and bonded to the body (model-v9-notes.md section h), colour and seams open (S24, S6).`

Cast in the same step as the liner: the model says it cannot be the same pour, with these numbers:
- The two volumes do not touch: the liner fills the band channel X -3.50 to 3.50 (channel 7.0, v8), RC1 lies at X -14.650 to -8.600 (corner_probe2.log): 5.10 mm apart along X, with the metal body between (the floor 0.40 thick and the shoulders). One pour needs two mould cavities and two gates.
- RC1 bounds the board cavity: its floor pocket gives ANT1 0.0300 mm of room (dev1_us9.log `under the antenna 0.0300 mm of room`), and its inner faces carry part of the glass seat and the screen tail's fold pocket. The liner is cast after the board, the screen and the glass are in (assembly.md steps 19 to 21). Cast at that step, RC1 would have to be poured round the fitted antenna with a 0.03 mm gap to hold open, and its glass seat would be under the already fitted glass.
- So the same resin (EP30Med) is possible, the same step is not: RC1 is cast or moulded separately and bonded to the body before the board goes in (assembly.md step 10 already places the corner there). The lead decides; assembly.md lines 158 and 165 then need the planes X -8.60 (not -10.6) and the resin name.

## i. Fit check US 7 to 13 on the final thin.py (out/v9/chain_fit.sh final, pid 3081, nice -n 19 through run_check.sh)

out/v9/final_chain.log: thin.py b0e69e1f0127fdc4de62e4ae37b7471c4a4b7f86, check_thin.py 7cddd98456a79e1ea7d9ae9e0506836b9e117f16, placement.csv 5fd79a75..., thin-inside.glb f340e0c6... at the start (04:24:11) and the same four hashes at the end (06:08:55): every size ran on the final files. Each size log's last lines are `exit 0` and the date. Values per size (out/v9/table_v9.py, log out/v9/table_v9.log):

| Size | Log | Result line | BOARD-PLAN largest difference | ZONE metal hits | Antenna to body metal | Motor free space to the body (rule 0.05) | Motor to the copper-free zone (rule 1.0) | Cell |
|---|---|---|---|---|---|---|---|---|
| US 7 | out/v9/final_us7.log | RESULT PASS pairs=1127 parts=48 | 0.0000 | 0 | 0.6000 | 0.1000 | 11.5430 | 33.936 mm, 17.6 to 23.5 mAh |
| US 8 | out/v9/final_us8.log | RESULT PASS pairs=1127 parts=48 | 0.0000 | 0 | 0.6000 | 0.1000 | 11.5506 | 36.547 mm, 18.9 to 25.3 mAh |
| US 9 | out/v9/final_us9.log | RESULT PASS pairs=1127 parts=48 | 0.0000 | 0 | 0.6000 | 0.0791 | 11.6094 | 39.175 mm, 20.3 to 27.1 mAh |
| US 10 | out/v9/final_us10.log | RESULT PASS pairs=1080 parts=47 | 0.0000 | 0 | 0.6000 | 0.1000 | 11.9385 | 40.914 mm, 21.2 to 28.3 mAh |
| US 11 | out/v9/final_us11.log | RESULT PASS pairs=1080 parts=47 | 0.0000 | 0 | 0.6000 | 0.1000 | 11.9830 | 42.651 mm, 22.1 to 29.5 mAh |
| US 12 | out/v9/final_us12.log | RESULT PASS pairs=1080 parts=47 | 0.0000 | 0 | 0.6000 | 0.0798 | 12.1381 | 44.387 mm, 23.0 to 30.7 mAh |
| US 13 | out/v9/final_us13.log | RESULT PASS pairs=1080 parts=47 | 0.0000 | 0 | 0.6000 | 0.1000 | 12.2889 | 46.121 mm, 23.9 to 31.9 mAh |

Every log reads the board plan with sha1 8af8f57682b4 (104 rows), the file as of 02:41. The cells are the v8 figures (band-fit-notes.md and thin-notes.md v6 table): v9 changes nothing in the band, so the cell's capacity is unchanged (0 percent).

## j. Item 44 (motor free space), answered

- Rule 1, motor to the body: at least 0.05 mm all round at every size (architecture.md line 796, "Rule set by the lead"; check_thin.py v6.1 finding "MOTOR free space to outer_body ... under 0.05"). Values: 0.1000 (US 7, 8, 10, 11, 13), 0.0791 (US 9), 0.0798 (US 12), table above (check line `motor free space to outer_body__metal`). The v8 logs give the same (out/v9/item44_v8_values.log: 0.1000 at US 7, 8, 10, 11, 13, 0.0798 at US 12, 0.0794 at the default US 9 build); the v9 baseline at US 9 gives 0.0791 (out/v9/baseline_us9.log). Passes at every size. The figures 0.042 and 0.000 of item 44 are the v6 values (thin-notes.md v6 table), closed since v6.1.
- Rule 2, motor body to the antenna keep-out (now the board plan's copper-free zone X -13.60 to -8.75, Y 3.10 to 6.30, as a prism over the whole block): at least 1.0 mm (the lead's 1.0 mm, design/mech/mech-notes.md line 54). Values 11.5430 to 12.2889 mm (table above). Passes. The 0.175 mm of item 44 belongs to the old housing of design/mech/mech-notes.md (antenna keep-out X 9.9 to 14.1), not to this model.
- No model change was needed for item 44.

## k. Maker files (design/mfg/parts/export_parts.py 7 8 9 10 11 12 13 through out/v9/export/export_size.py)

Run by out/v9/export/run_export.sh (06:10:14 to 06:14:13): out/v9/export/export_parts_v9.log, each size `export_size.py exit 0`, `index.csv: 104 rows`, `exit 0`; per-size logs out/v9/export/export_usN.log and .txt. export_parts.py now calls the v9 exporter and merges the band circuit rows from out/v8/rows_flex_usN.json (the v7 version is kept as design/mfg/parts/export_parts_v7.py). The two band circuit folders are not written (another lane's files).

Files written and read back (out/v9/export/export_counts.log; read-back out/v9/item104/maker_readback.log, a fresh process, each STEP against the solid count and volume the exporter took from the model in memory, last lines `files compared 52, differing 0`, `RESULT PASS files=52`, `exit 0`). 52 = the STEP files expected:

| Part | STEP files | Read back |
|---|---|---|
| body | 7 (US 7 to 13, plus 7 STL) | 7 |
| band-liner | 7 (plus 7 STL) | 7 |
| cell | 7 | 7 |
| glass-seal | 7 | 7 |
| joystick-dam | 7 | 7 |
| joystick-stiffener | 7 | 7 |
| motor-window-seal | 3 (US 7, 8, 9) | 3 |
| cover-glass, joystick-cap, joystick-frame, main-board, mic-gasket, mic-membrane, radio-corner | 1 each (same at every size; cap, frame and radio-corner also STL) | 7 |
| ring-assembly | 7 | not in the read-back: the exporter compares each with the model's solid count in the same process (no volume) |

Total STEP files newer than the export start: 59 = 52 + 7 assemblies. Files older than the export (not in old_*): only the 28 band circuit files of flex-tail-thumb and flex-tail-away (v8, out/v8/export_ribbons.py); index.csv rows: 76 with source "thin.py v9", 28 "thin.py v8" (the band circuits: 14 tails and 14 foot stiffeners, the rows section e of band-fit-notes.md asked for). RC1 is the same at every size: volume 26.4218 mm3 and the same box at US 7 to 13 (the lines `radio corner US N` of export_usN.txt). Changed against v7/v8: body US 9 volume 982.221 to 934.179 (corner cut away, channel 7.0), band-liner US 9 6.8 x 19.7769 to 7.0 x 19.7916 x 18.2359, 91.7212 to 92.4661 mm3, main-board 94.0318 to 95.8078 mm3 (no notch); joystick-cap 78.7324 and joystick-frame 6.2486 unchanged.

## l. Text lines changed (diff of each page against its copy as found in out/v9/before/docs/; operations from out/v9/final/line_alignment_3.log)

Every change is in place or appended at the end of a page, so the line numbers other files cite (assembly.md, deferred-items.md, w11-item-values.md: out/v9/spec_line_citations.log) still open the same lines. Value now -> value needed:

- design/architecture.md (only the lines section h of band-fit-notes.md names, and line 156): 156 antenna keep-out "no copper and no metal within 4.2 x 4.7 mm" -> that text kept as history plus "ANT1 at X -10.80, Y 5.25 on the board's under face, copper-free zone X -13.60 to -8.75, Y 3.10 to 6.30 on all layers less X -9.20 to -8.75, Y 3.10 to 3.30" (R2.6 row 3); 440 "0.6 mm at each edge, a channel 6.8 mm" -> "0.5 mm ... 7.0 mm (inside model v8)"; 586 "0.7 mm off the band's centre line" -> "+ (0.8 mm at US 7 and US 12)"; 587 "1.4 mm wide; tightest free space 0.1 mm" -> "1.8 mm wide at the neck, 2.5 at the board foot ... foot flat for 1.745 mm (Y 3.4 to 5.145), top 0.03 under the land faces at Z 1.43, fold inner radius 0.70 (least 0.66); 0.075 mm resin to motor, cell and protection circuit, 0.10 to the body"; 795 "6.4 x 6.4 x 0.075 mm stiffener" -> "0.10 mm (0.075 before v8)"; 797 "motor to the joystick ribbon 0.097 to 0.099 mm on US 10 to 13" -> "motor to the ribbon 0.075 mm on US 8 to 11 and US 13, 0.0926 mm on US 7 and US 12"; 809 "ribbon is 1.4 mm wide (X -3.3 to -1.9) ... 0.2 and 0.4 mm to the slot ends" -> "ribbon neck 1.8 mm (X -3.4 to -1.6) in a floor slot 2.1 mm long (X -3.55 to -1.45), 0.15 mm to each end", and "(v8: 2.1 x 0.6, X -3.55 to -1.45)" added after "2.0 x 0.6 mm, from X -3.5 to X -1.5". (Lines 918 to 931 were appended by another writer during my work, not by me.)
- design/mfg/assembly/assembly.md (only lines 71, 72, 234): 71 FLEX1 "1.4 mm wide ... head 6.4 x 6.4 x 0.15 ... 0.075 stiffener" -> "1.8 mm wide at the neck (2.5 at the foot) ... head 6.4 x 6.4 x 0.11 on a 0.10 stiffener"; 72 FLEX2 "1.4 mm wide" -> "1.8 mm wide at the neck (2.5 at the foot)"; 234 "slot 2.0 x 0.6 ... ribbon 1.4 x 0.15 ... 0.99 square mm" -> "slot 2.1 x 0.6 ... neck 1.8 x 0.11 ... 1.062 square mm [CALC: 2.1 x 0.6 - 1.8 x 0.11]". The placement.csv rows these lines cite (47, 48) are unchanged: RC1 is the new last row.
- design/mfg/specs/body.md: 3 (version line: + model v9 and the radio corner), 5 (files: v9, corner cut away), 8 (what it is: + RC1), 48 (joystick stack flex 0.15 -> 0.11 on a 0.10 stiffener), 60 (edge wall 0.6 -> 0.5), 61 (channel 6.8 -> 7.0), 73 (no 0.1 mm strip since v8), 79 (motor 0.7 -> 0.7, 0.8 at US 7 and US 12), 89 (slots 2.0 x 0.6 at X -3.5 to -1.5 -> 2.1 x 0.6 at X -3.55 to -1.45), 104 (files: v9 volume 934.179, radio-corner file), 136 (slots), new last section "Radio corner RC1" (corner X -14.80 to -8.60, Y 2.05 to the skin; pocket 3.60 x 2.00 x 0.20 at X -12.60 to -9.00, Y 4.25 to 6.25; open point 13: resin colour, adhesive, seams).
- design/mfg/specs/band-liner.md: 6 (ribbons 1.4 x 0.15 -> 1.8 at the neck; stiffener 0.075 -> 0.10; no strip), 28 (channel 6.8 -> 7.0), 40 (files v7 -> v9; US 9 box 6.8 x 19.7769, 91.7212 -> 7.0 x 19.7916 x 18.2359, 92.4661), 53 (open point 11: the strips are gone), 59 (ribbon 1.4 x 0.15 -> 1.8 neck), 60 (cable land X -2.25 to 0.25 -> pad strip X -3.4 to 0.25), 61 (stiffener 0.075 -> 0.10), 62 (strips 0.1 -> none), 64 (slots 2.0 at X -3.5 to -1.5 -> 2.1 at X -3.55 to -1.45).
- design/mfg/specs/joystick-nub.md: 62 (stiffener 0.075 -> 0.10), 90 (files written again from v9, same box and volume).
- design/mfg/specs/main-board.md: 3 (version: + v9, KiCad = model + 100), 6 (6 layers -> 4 copper layers, no notch, test pads on the screen face), 12 (material: 4 layers, microvias, 0.30; lead decision "7, 11 (part), W2"), 21 (no notch), 30 (layer count 6 -> 4), 31 (antenna notch 1.8 -> none), 32 (antenna notch 3.6 -> ANT1 X -10.80, Y 5.25 turned 180), 35 (U11 source: board plan), 36 (C84 X 1.2 -> 1.27 turned 90, 4.7 uF), 39 (screen connector -12 -> the copper-free zone row; J1's place is in the last section), 45 (inspect: no notch), 51 (files: no notch, v9), 59 (open point 6 closed by the plan's zone), new last section "Places of the parts drawn in the 3D model" (the 16 places and turns, side B = the 19 test pads on the screen face).
- design/mech/thin/thin-notes.md: new last section "Model v9" (history above unchanged).
- design/mfg/parts/export_parts.py (v7 kept as export_parts_v7.py), design/mfg/parts/index.csv (regenerated, 104 rows).
- Not edited: design/bom.csv, design/bom-notes.md (section h gives the RC1 row), design/mfg/tools/draw.py (not mine).

## m. Changes other files need (not edited: outside my lines or my files; found by the searches out/v9/search_v9_words.log, out/v9/final/assembly_stale_values.log, out/v9/final/citations_edited_lines.log)

| File and line | Value now | Value needed | Why |
|---|---|---|---|
| design/bom.csv, new row; design/bom-notes.md, one line | no RC1 row (check_bom.py `FAIL designator RC1 ...`) | the row and line given in section h | model v9 part RC1 |
| design/bom.csv line 81 (LNR1) | "0.3 thick, 6.8 wide channel" | "0.3 thick, 7.0 wide channel" | model v8 |
| design/architecture.md line 443 | antenna "sits in a notch of the board, 1.8 x 3.6 mm" | "on the board's under face at X -10.80, Y 5.25 (no notch), its 1.20 body 0.20 into the resin corner's floor pocket" | R2.0, model v9 |
| design/architecture.md line 669 | "antenna ... at X -12.7, Y 4.4 ... body metal 0.050 mm under it, 0.225 ... 0.450" | "at X -10.80, Y 5.25; nearest body metal 0.6000 mm (resin corner), 0.0300 mm of resin room under it" | model v9 (section f) |
| design/architecture.md lines 674, 676 | corner "X -14.8 to -10.6 ... 20.3 cubic mm"; "NOT DECIDED ... the body stays one metal piece in every file" | "X -14.80 to -8.60, Y 2.05 to the skin, 26.42 cubic mm; the lead's default of 2026-11-13 (row 'radio corner', owner can overrule): the model v9 and the maker files carry the resin corner RC1" | lead-decisions.md rows "radio corner", "W2, rule on places" |
| design/mfg/assembly/assembly.md lines 62, 84, 158, 165, 270, 345, 376 | "only if the owner adopts it", "if adopted", bond planes "X -10.6 and Y 2.05", adhesive not named | RC1 is in the design (lead's default); planes X -8.60 and Y 2.05; resin EP30Med as the liner, made before the board goes in (section h) | model v9 |
| design/mfg/assembly/assembly.md line 89 | "the antenna notch 1.8 x 3.6 (main-board.md:31)" | "no notch (main-board.md:31)" | model v9 |
| design/mfg/assembly/assembly.md lines 11, 250 | channel "6.8 mm wide" | "7.0 mm wide" | model v8 |
| design/mfg/assembly/assembly.md lines 162, 323 | floor slots "2.0 x 0.6 from X -3.5 to X -1.5" | "2.1 x 0.6 from X -3.55 to X -1.45" | model v8 |
| design/mfg/parts-notes.md line 28 | main-board "with the antenna notch" | "no notch (model v9)"; and a radio-corner line | model v9 |
| design/mfg/tools/draw.py line 26 | DESIGN_VERSION "inside model v7" | "inside model v9" | the title block of every sheet |
| design/mfg/tools/draw.py line 41 (joystick-stiffener) | "Stainless or polyimide, 0.075" | "Polyimide, 0.10 (band-interface.md section 1)" | model v8 |
| design/mfg/tools/draw.py lines 49, 50 (board) | "antenna notch, no other hole", "6 layers, 0.3 mm thick" | "no notch, no hole", "4 copper layers, 0.30 mm (lead decision 7, 11 (part), W2)" | model v9 |
| design/mfg/tools/draw.py line 63 (KEYDIMS "Floor slots, both") | "2.0 x 0.6 at X -3.5 to -1.5" | "2.1 x 0.6 at X -3.55 to -1.45" | model v8 |
| design/mfg/tools/draw.py META | no row for radio-corner (its sheet takes the folder name and "see design/mfg/specs/radio-corner.md", a page that does not exist) | ("radio-corner", "Radio corner of the body, resin", "RC1", "Master Bond EP30Med (as the liner), colour matched; see specs/body.md section Radio corner RC1") | model v9 |
| design/mfg/tools/draw.py main() stem rule | in a folder with several STEP files every file with "us9" in its name becomes the folder's main sheet: flex-tail-thumb-footstiffener-us9.step and flex-tail-thumb-us9.step both write flex-tail-thumb.svg (the later one wins) | a stem rule that keeps the file stem when the stem is not the folder name | the v8 foot stiffener files; I drew those through a second folder (out/v9/drawparts, links) with --parts |
| design/wiring/deferred-items.md rows 44 and 104 | open | closed by this work (sections j and g) | |

## n. Questions for the lead from the model (not owner questions)

- The roof of the screen tail's fold pocket under the glass seat is 0.05 mm of metal (Z 2.650 to 2.700, every Y of the pocket; already in v8, out/v9/sliver_probe.log). With RC1 that roof ends at Y 2.05 on a bond face of that thickness. No rule of check_thin.py measures it.

## o. Final checks (out/v9/final_checks.sh, one after another at nice -n 19; summary out/v9/final_checks.done)

| Check | Command | Log | Last line |
|---|---|---|---|
| fit check US 7 to 13 | out/v9/chain_fit.sh final | out/v9/final_us7.log to final_us13.log | `RESULT PASS pairs=1127 parts=48` (US 7, 8, 9), `RESULT PASS pairs=1080 parts=47` (US 10 to 13), each then `exit 0` (section i) |
| drawings | design/mfg/tools/draw.py | design/mfg/tools/logs/draw_v9.log | `80 drawn, 0 failed` |
| drawings of the foot stiffeners (draw.py --parts out/v9/drawparts, links to the 14 files) | same tool | design/mfg/tools/logs/draw_v9_footstiffener.log | `14 drawn, 0 failed` |
| maker files | design/mfg/parts/check_parts.py | out/v9/final/check_parts.log | `RESULT PASS files=104` |
| maker files read back against the model | out/v9/item104/maker_readback.py | out/v9/item104/maker_readback.log | `RESULT PASS files=52` |
| specifications | design/mfg/tools/check_docs.py | out/v9/final/check_docs.log | `RESULT PASS` (it ended `RESULT FAIL` on the pages as found: out/v9/before/check_docs_before.log, 4 values of band-flex-tails.md missing from architecture.md, now on line 587) |
| band circuits | design/ecad/ring/pcb/run_kipy.sh design/ecad/band/check_band.py | out/v9/final/check_band.log | `RESULT: PASS boards checked 14` (it rewrites its 14 *-drc.rpt files) |
| parts list | design/tools/check_bom.py | out/v9/final/check_bom.log | `FAIL designator RC1 is in netlist.csv or placement.csv and missing from the parts list` then `exit 1`: the one failure, RC1, whose row is in section h for the lead (`failures 1`; the four test pads of 04:25 are gone) |

Every drawing in design/mfg/drawings was written by these runs (out/v9/final/drawings_not_redrawn.log is empty); 80 svg sheets, among them radio-corner.svg and .pdf.

## Not proven and limits

- The 88 parts of the board plan that the model does not draw (0201, 0402, 0603, U9, U10, the J_BAND lands, LT1, the 19 test pads on the screen face) are not in the fit check; the plan's own check_placement.log covers their courtyards. The named test checks the 16 drawn parts only.
- Heights where a footprint gives none stay the v8 values (U1 0.43, U2 0.5 envelope, U3 0.75, U4 0.58, J1 0.9, C83 and C84 0.5): assumed, not from a maker page.
- ANT1's corner terminations over the full 1.20 height, the coils' 0.30 end caps, the crystal base and lid split: assumed shapes.
- The antenna's 0.0300 mm room over the pocket bottom is a model figure; the real gap depends on the solder joint and the resin's tolerance. Start value 0.03; measurement: the antenna's height over the pocket bottom on the first built unit. Its radio performance is not measured here (bench T0, T1, T2; design/sim/antenna).
- The resin corner's bond, seams, colour and its making as a separate part (section h) are not proven by any built part.
- The broken copies ran through the named tests alone (out/v9/named_tests.py), not through the whole check with the pair test.
- ring-assembly files are compared with the model by solid count only (in the exporter), not by volume in a fresh process.
- The second routing round of the board may move X2 (and U10): the named test reads placement-plan.csv, so after a move it fails until thin.py's BOARD table follows; every result here is for the plan with sha1 8af8f57682b4.
- The screen cable: a study found the stock screen's cable does not fit the present block; the owner decides its route, and the cable fold pocket at the hand end and the foam frame may change after that. Model v9 keeps them as they are.
- The 0.05 mm metal roof over that fold pocket (section n) is not covered by any rule of the check.
- No git command was run: the base is commit cdb1ddc by the lead's statement; the files as found are in out/v9/before/ with their hashes.
- Deleted by me (scratch, recorded in out/v9/deleted_scratch.log and out/v9/dev_cleanup.log): the item 104 fake STEP, a copy of the v8 GLB, the dev copy's GLB and STEP (built from the same code as the delivered files), out/v9/dev/__pycache__, two code text pieces and a copy of the v7 exporter.

## questions_for_owner

1. The resin radio corner changes the look of the ring: a resin corner at the hand end on the thumb side with seams on the hand end, the side and the underside (architecture.md line 674 "It adds fine seams"; line 676 "the fix changes the ring's look, which is the owner's decision"). The lead took it as the default (lead-decisions.md row "radio corner"). Best reading, as an option: keep the resin corner in the body's gloss black, colour matched, and judge it on the antenna bench test T0, T1, T2.

RESULT: done, model v9 puts the 16 drawn board parts at the board plan's places (largest difference 0.0000 mm) with a resin radio corner, passes the fit check at US 7 to 13 with both broken copies failing, and the maker files, drawings, check_parts, check_docs and check_band pass, while check_bom fails only on RC1 whose row is given for the lead
