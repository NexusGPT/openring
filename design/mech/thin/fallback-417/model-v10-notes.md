# Inside model v10: the ring's inside on the 4.17 block, flat glass, layout C screen cable, side slits (notes, written while working)

Work started ven. 13 nov. 2026 16:49:52 CET (clock from `date`). Folder: design/mech/thin/. Every log and script named below is in out/v10/ of that folder unless a full path is given. No git command was run, no browser, no script of design/look/s1 was run (its STEP files were read). Heavy runs at `nice -n 19`, one at a time. Checklist: out/v10/CHECKLIST.md.

v9 files as found: out/v10/before/ (thin.py, check_thin.py, placement.csv, thin-notes.md, layers.json, model-v9-notes.md, out/thin-inside.glb and .step), hashes out/v10/before/shasum_before.log (thin.py b0e69e1f..., check_thin.py 7cddd984..., placement.csv 5fd79a75..., the hashes model-v9-notes.md gives for v9). Development copies: out/v10/dev/.

Exterior files read (hashes and times at the start: out/v10/exterior_shasum_start.log). The exterior helper's chain (design/look/s1/out/work-flat/chain-w2.log) had built them by 16:28 and was still measuring when I started; its measures are not mine.

Order of this page: what changed per point 1 to 7; the stack sum; the clearance list; the check's last line per size; the conflicts not solved; what a later job needs; then how the check changed, the broken copies and the working log.

## Point 1: the exterior

- thin.py reads design/look/s1/out/ring-merged417flatw-us<N>.step (default US 9; v9: ring-merged32h). Its solids (out/v10/probe/ext_labels_us9.log): body (Z to 3.72 at the seat), glass Z 3.7200 to 4.1455 (0.4255 at the centre line), joystick, mic_1, mic_2, screen (the lit-area print, X -9.325 to 12.275, not used by the model: see the conflicts) and slit_fill (6 solids, 21.6299 mm3: the two through slits X -3.55 to -1.45 from |Y| 5.6 to the skin, Z slot bottom to 1.53, and the four blind windows X -1.05 to 1.05 and 1.45 to 3.55).
- The stack is hung from the glass underside as before, with the board-to-panel space `scr_gap` 1.07 (v9 `foam_t` 0.10): everything above the board is 0.970 higher (panel 1.85 to 2.82, glass underside 2.75 to 3.72); the board and every part under it stay where v9 has them (board 1.45 to 1.75, floor 0.40).
- The panel pocket (27.45 x 12.9) is cut from the floor up as before; the glass seat lowered 0.05 for SEAL1 follows the flat glass.
- The slits are the exterior's own openings: thin.py cuts no slit; the inside-body envelope includes the exterior's slit_fill, as it includes the joystick opening and the microphone holes.

## Point 2: screen and cable, layout C (screen-cable-study.md section 4.3)

- Panel DISP1 turned 180 degrees: the ledge (lower glass only, 2.951 long) at the fingertip end, X 10.724 to 13.675; the lit area drawn at its true place on the panel, X -12.672 to 8.924 (study line 210), 10.8 across.
- The cable `screen_tail` at its real width (item 48, K16): bond 0.900 x 12.402 on the ledge top (X 12.775 to 13.675, Z 3.22), fold 1 down at the panel end X 13.675 (inner radius 0.30), a straight drop 0.330, fold 2 toward -X, flat run Z 2.15 to 2.29 (0.40 over the board, 0.53 under the panel), the 12.402 wide part to X 3.170 (s 11.997, outer corners r 0.50), the 4.805 neck, the stiffened end 0.20 thick from X -1.629 (s 16.796) into J1's slot, the end at X -4.8326 (study: -4.833; the build stops if its own path ends more than 0.01 away). Thickness 0.14 (study start value). The inner fillets r about 0.5 between the wide part and the neck are not drawn (less cable, no part under them).
- The body gets the fingertip end pocket for the fold: X 13.725 to 14.165, Y +-6.40, Z 2.10 to 3.42 (0.05 under the cable's lowest point, 0.06 over its fold top 3.36); the cable reaches X 14.115 in it, 0.05 from its end wall. The v9 tail pocket at the hand end (0.55 x 5.4 x 2.0 at X -13.775) is gone, and with it the 0.05 metal roof of model-v9-notes.md section n.
- J1 on the screen face at (-4.933, -0.003), turned 270, side B, housing 3.35 x 6.1 x 0.9 on its 17 lands (read from the footprint, mirrored in its y as ring.kicad_pcb stores a side B part), the cable slot from its +X face (4.900 wide, 0.24 high, its floor 0.33 over the land face), lever bar on the -X side. FOAM1 is removed (assembly.md step 16 (4)).

## Point 3: the board parts at their routed places

- Table BOARD of thin.py follows design/ecad/ring/pcb/placement-final.csv: X1 turned 180 (v9 0), J1 moved to side B at (-4.933, -0.003); new in the model: C90 (0402, 10.950, 2.250) and R73 (0201, 10.200, -2.800), both on the parts face, and the eight 0201 parts that the routed board puts on the SCREEN face, C5, C1, C2, FB1, C7, C14, R71, R72 (they stand under the cable). Heights of the chips: 0201 0.33, 0402 0.55 (ASSUMED, point 7).
- check_board_plan reads placement-final.csv (v9: placement-plan.csv), mirrors a side B footprint in its y, measures a side B part's height upward from the screen face and checks the face of every body and land (new). All 26 drawn parts: place and size within 0.0000 of their rows, every land on the right face (out/v10/dev1_named_us9.log `BOARD-PLAN: 26 parts, largest place or size difference 0.0000 mm`).
- Left out (out/v10/left_out_nowindow.log, 73 of 99 rows): the other 0201, 0402 and 0603 chips, L1, U9, U10, LT1 on the parts face, J_BAND_A and J_BAND_B (their footprints are in OpenRingBand; the ribbon feet are drawn over them), and the 12 test pads. Why: on the parts face every one of them is under the 1.00 that the stack gives every under-face part (the drawn 1.00 parts set the floor), none lies in the two ribbon fold volumes, and their spacing to each other is the board's own courtyard check; on the screen face only flat test pads are left, under the cable neck (the cable floats 0.40 over them, study line 205). Found against this reason (out/v10/left_out_us9window.log, the US 9 motor window's box X -1.329 to 2.729, Y -6.750 to -5.599 from out/v10/dev2_us9.log): two left-out parts lie over that box in plan, C82 (0201, X 2.250 to 2.550, Y -5.900 to -5.300) and C25 (0402, X -0.200 to 0.800, Y -6.100 to -5.600). The window opens the floor (Z under 0.40) and the wall (Y under -6.45); these parts hang no lower than about Z 0.88 and stay 0.35 or more inside the wall [CALC from those planes], so the window's 0.30 rule probably holds for them, but it is not measured: they are not drawn (open, the next model run should draw C25 and C82; US 7 and US 8 windows not looked at).

## Point 4: the ribbons through the side slits

- The necks stand where v8 put them (1.8 wide, X -3.4 to -1.6, in the floor slot at Y +-5.9); the slit opens each slot through the side wall from |Y| 5.6 to the skin, Z slot bottom to 1.53 (the exterior's). Rule of body.md line 89, measured on the solids: 0.1500 from each neck end to the slit's ends (X -3.55 and -1.45); the threading path (the slit's section X -3.55 to -1.45 from |Y| 5.6 out to 9.6, Z slot bottom to 1.53) holds 0.0000 mm3 of metal on both sides (check_thin.py 15c).
- The slit seal SEAL3 (`side_slit_seal`, new part, layer body): the exterior's slit_fill less the block cavity and less the two necks and folds, so it fills each slit and floor slot round the neck, flush with the side wall, and the four blind windows (US 9: 17.3487 mm3 in out/v10/dev/placement.csv, row side_slit_seal; per size in the table below). The slit space outside the cavity not filled by SEAL3 or a ribbon: 0.0000 mm3 each side. Sealant: the floor-slot sealant DP420 Black of assembly.md step 19.

## Point 5: the radio corner RC1 and the antenna on the taller block

RC1 is made as in v9 (thin.py `rc_box` X -14.80 to -8.60, Y 2.05 to the skin, Z -30 to 10, cut from the body after every pocket, floor pocket X -12.60 to -9.00, Y 4.25 to 6.25, 0.20 deep): on the taller block it reaches the glass seat. US 9 (out/v10/dev2_us9.log, `radio corner RC1`): X -14.650 to -8.600, Y 2.050 to 7.375, Z -0.000 to 3.670, 35.0862 mm3 (v9 Z to 2.750, 26.4216 mm3: out/v10/red_v9_named_us9.log). The antenna is unchanged under the board: free space to the body metal 0.6000, 0.0300 of room over the pocket bottom; nearest other metal now main_board__gold 2.2154 (v9: 1.6000, and J1's latch bar 2.2000, gone from the corner). The copper-free zone prism holds no metal or gold but ANT1's (0 hits); the cable and J1 are 2.1427 from the zone (study: 2.218 for the cable's courtyard boxes).

## Point 6 worked out: the dam DAM1 before the cast (items 112 and 115; K-A3, K-A12, K15)

What the model gives (out/v10/dam_numbers.log, per size; US 9 here): bore (the mould core's face) r 9.4726, liner face r 9.7726, ribbon head 9.6626 to 9.7726 (flex 0.11), stiffener under it to r 9.5626 (0.10), switch base tops r 10.1226. The pocket is 7.0 along X by 6.8 round the band, the head stack 6.4 x 6.4: the gap from the stack's edge to the pocket walls is 0.300 along X and 0.200 round the band. v9 drew the dam from the liner's face up, 0.05 off the stack's edge all the way down: before the cast there is nothing under it (K-A12), and the 0.05 ring between the dam and the stack runs from the liner up to the switch space, a path for the cast resin to rise between the switches (K15). Measured on the v9 model with the v10 rule: 2652 of 10440 points across the pocket's edge band at the stack's level are open, first at (-3.152, 3.205, r 9.5826) (out/v10/red_v9_named_us9.log, line `DAM barrier at the head stack's level`).

| | Option A (modelled): bead bonded to the head stack and the walls | Option B: two-shot cast (the K-A12 proposal, assembly.md line 340) |
|---|---|---|
| What it stands on before the cast | the four pocket walls (coated titanium) and the edge faces of the head stack (polyimide flex 0.11 + stiffener 0.10); nothing under it: 0.0900 of open space to the core at the middle, 0.7212 at the band edges (US 9; 0.6236 to 0.7854 over US 13 to US 7) | the cured first-shot skin: the liner resin cast under the joystick only (core in, a removable plug filling the pocket above the stiffener) |
| Height | from the stiffener's underside to the switch base tops: 0.5600 at every size | from the liner face to the switch base tops: 0.3500 |
| Gaps it closes | 0.300 (along X) and 0.200 (round the band) from the stack's edge to the walls, over the stack's 0.21 height with no gap at the stack; above the head top it stays 0.05 off the switch bases; it wraps the ribbon's bend where the bend leaves the head toward the +Y slot | the same 0.300 / 0.200 above the skin; the 0.05 ring at the stack's edge is closed by the first shot rising to the plug's underside (it must seal on the head top) |
| Builder | step 20 (after 13, 15 and 19 as now): ring held bore up, dispense the bead round the head through the bore into the gaps, cure it in place, inspect at 20 times that it meets the stack's edge and the walls all round; then step 21 as written (one cast, which also fills under the bead and under the stiffener) | step 20a: plug in, core segment in, cast shot 1, wait for its cure (EP30Med cure time: not on disk, band-liner.md line 43); 20b: plug out, dispense the dam on the cured skin, cure; step 21: cast the rest (a second core fill) |
| Worse at | the bead hangs over open space (up to 0.72 deep at the band edges) until the cast: a material that slumps runs down to the core and shows on the liner's inner face or skins over the stiffener's underside; its bond to the stack edge is only 0.21 high; the bead hides the stack's edge, so a closed seal is seen only from the bore side | two casts, two cure waits, a plug that must seal on the head top and come out without lifting the head, a first shot whose own resin can wick up the 0.05 ring if the plug does not seal |

Choice: A, modelled (thin.py, the joystick_dam block; check_thin.py 15d). It is one dispensed part and one cast, the steps a builder already has; B adds a plug, a part-cast and a second cure to every ring. What A is worse at is listed above; the slump risk is the one to prove on the bench (B9).

What the dam material must do (no dam material document on disk, deferred-facts.md item 112 (d); I do not choose it):
- Viscosity class: a non-slump thixotropic paste (gel), not a liquid: it must bridge 0.30 and stand 0.56 high over up to 0.79 of open depth without running, from a fine needle (about 0.25 bore).
- Cure: in place, at room temperature, within minutes and before the cast; by light from the bore side (UV or visible) with a second cure for the shadowed side under the head (the bead's inner face is shaded by the head); never above 45 C (the cell, assembly.md step 21).
- Height held: 0.56 (option A) without slump through the cure; low shrinkage, so it stays bonded to the stack edge and the walls.
- Bond: to polyimide (flex and stiffener) and to the coated body; the liner resin must bond to it and not dissolve it; it must not wet the switch bases (0.05 away).

Where the cast resin can still reach (model, option A): the stiffener's underside and the space under the bead (the liner fill, as intended: the liner fill now covers the whole 7.0 x 6.8 pocket footprint from the bore to the stiffener's underside, thin.py `liner_fill`); not the switches: at the stack's level no point of the pocket's edge band is open (out/v10/dev1_named_us9.log `0 of 10440`; rule 15d of check_thin.py), and above the head top the switch space is closed below by the head itself. The model cannot show a void in a real bead.

## Point 7: the values marked ASSUMED, and item 103

thin.py (grep `ASSUMED` of the delivered thin.py: out/v10/final/assumed_final_grep.log; as found: out/v10/assumed_thin_grep.log):

| Value | Fate | Source or reason, and what settles it |
|---|---|---|
| X1 height 0.40, X2 height 0.6 (the v8 0.5 was ASSUMED) | closed in v9 | footprint descr (XTAL_Kyocera_CX2016DB "2.00 x 1.60 x 0.40", XTAL_TXC_9HT11 "2.0 x 1.2 x 0.6"); v10 removes the old word from the comment |
| board corner radius 0.8 | closed | the routed board's Edge.Cuts: arcs from (86.4, 94.5) to (87.2, 93.7) etc., radius 0.8 (out/v10/probe/edge_cuts.log) |
| J1 height 0.9 (v8 value) | closed | 0.9 +-0.1, Hirose catalogue p3 (screen-cable-study.md line 59) |
| coil end caps 0.30 (L10, L71, L72) | kept | the Murata 1269AS sheet on disk gives its dimensions only as a drawing image (out/v10/probe/murata1269_text.log); settles: the terminal length on that drawing (p1) or a caliper on a part |
| crystal base / lid split 0.6 / 0.4 of the height | kept | no maker drawing of the split; settles: a sectioned part or the maker's outline drawing |
| microphone substrate 0.2 / lid 0.8 | kept | the Knowles copy gives 1.00 overall only; settles: the maker's package drawing with layer heights |
| ANT1 terminations over the full 1.20 | kept | Johanson p2 gives the terminal footprint 0.50 x 0.30, not its height; settles: a side view of the part |
| J1 inner shape (latch bar, contacts, slot) | kept | the catalogue gives the outline only; the slot is drawn to take the cable 0.02 clear each face |
| C83, C84 height 0.5; new: 0201 0.33 and 0402 0.55 (C90, R73 and the eight screen-face parts) | kept | the saved Murata files are 404 pages (out/v10/probe/murata_text.log); settles: the GRM155 / GRM033 sheets (T 0.50 +-0.05, 0.30 +-0.03 are the usual sizes, not read here) |
| screen lower glass 0.40 of 0.80 | kept | thin-notes.md line 39; settles: the panel maker's side view |
| cable thickness 0.14, fold inner radius 0.30 | kept (start values of the study) | screen-cable-study.md lines 47 and 100; settles: micrometer on a real cable and the mandrel test of study section 6 |
| foam open middle | gone | FOAM1 is removed in v10 |

design/mech/dimensions.csv (30 lines with ASSUMED, out/v10/assumed_dimensions_grep.log): none is read by thin.py or check_thin.py (out/v10/dimensions_users.log: read only by design/mech/ring.py, audit.py, check_fit.py, thin_spots.py, the older box model). The file is outside my lane, so no tag is removed there; their fate for the inside model:
- fold_w 8.0 (line 37, "cable width"): superseded: the cable is 12.401 wide for 11.496, neck 4.805 (display drawing p5, study section 2; drawn so in v10).
- fpc_conn_x/y/z 3.2 / 5.2 / 0.9 (lines 106 to 108): superseded: FH35C housing 6.1 x 3.35 (footprint F.Fab, catalogue p3), 0.9 +-0.1 high (catalogue p3).
- joy_stem_d 2.5 (line 49) = item 103's stem: not in the design since v7: the round cap CAP1 4.40 with its flange (architecture 17.29); no stem value is used.
- mic_yc 4.9 "port at the package centre ASSUMED" (line 62) = item 103's microphone port: closed for the inside model: the port is 1.030 from one short end, centred on the 3.00 width (Knowles SPK0641HT4H-1 drawing sheet 6, mic-path.md line 35); thin.py's port at X +-11.77 (10.80 + 0.97) is that value.
- seat_clear 0.05 (line 31) and pocket_clear 0.05 (line 89): the inside model uses 0.05 per side for the panel pocket (body.md line 89 calls it the modeller's choice): still a choice; settles: the body maker's tolerance.
- min_wall, top_plate, glass_r_plus_y, notch_clear, btn_open_x/z, key_x/z, win_d, win_t, led_hole_d, tvs_z, wpad, wpad_t, wpad_pitch, cb_clear, screw_core_d, screw_clear_d, screw_head_d, screw_head_t, gasket_d, blend_r (lines 7, 8, 30, 43, 72 to 75, 80 to 82, 105, 109 to 111, 113, 131 to 134, 140, 146): parts of the older box model (printed nylon, button, light window, screws, wire pads) that the thin model does not have; no measurement asked; the owner of design/mech/dimensions.csv may mark them superseded.

## The stack above the board (check_thin.py 15a, measured on the solids; out/v10/dev2_us9.log lines `STACK-ABOVE`, the same at every size: the block does not change with the size)

| Layer | From Z | To Z | Thickness | Source |
|---|---|---|---|---|
| board | 1.4500 | 1.7500 | 0.30 | the board does not move in layout C (screen-cable-study.md section 3 table, line 241) |
| J1 lands (screen face) | 1.7500 | 1.7700 | 0.02 | the model's land thickness pad_t (ASSUMED since v2, no maker value) |
| J1 housing | 1.7700 | 2.6700 | 0.90 (+0.10 at most) | Hirose catalogue p3, 0.9 +-0.1 (study line 59) |
| J1 at its highest to the panel | 2.7700 | 2.8200 | 0.05 | study line 199 (0.9 +0.1 plus 0.05) |
| cable path instead of J1: board top to cable | 1.7500 | 2.1500 | 0.40 | study line 172 |
| cable (flat run) | 2.1500 | 2.2900 | 0.14 | study line 47 (start value, not printed) |
| cable to the panel | 2.2900 | 2.8200 | 0.53 | study line 172 |
| stiffened contact end (in J1) | 2.1200 | 2.3200 | 0.20 | printed 0.2 +-0.03 (study line 46), 0.37 over the board (line 184) |
| panel | 2.8200 | 3.6200 | 0.80 | display_TOH095XVT-01.pdf p5, printed 0.8 (study line 33) |
| clear adhesive ADH1 | 3.6200 | 3.7200 | 0.10 | cover-glass.md line 6 (tesa 69404, 100 um) |
| glass underside (seat) | 3.7200 | | | merged417flat-notes.md line 60 |
| glass | 3.7200 | 4.1455 | 0.4255 | merged417flat-notes.md line 60 |

Sum along J1: 1.75 + 0.02 + 0.90 (+0.10) + 0.05 = 2.8200; + 0.80 + 0.10 = 3.7200 = the glass underside 3.7200. Along the cable: 1.75 + 0.40 + 0.14 + 0.53 + 0.80 + 0.10 = 3.7200 (out/v10/dev2_us9.log line 267, `STACK-ABOVE sum`). The whole block: floor 0.40 + gap 0.05 + parts 1.00 + board 0.30 + board to panel 1.07 + panel 0.80 + adhesive 0.10 + glass 0.4255 = 4.1455 (same log, `block stack`). J1 at its nominal 0.9 leaves 0.15 to the panel.

## Clearances under 0.15 mm (check_thin.py CLEARANCE report, per size)

PENDING: from the final chain (out/v10/final_usN.log, lines starting `CLEARANCE under`), filled per size when it ends.

US 9, from the final chain's US 9 log: `CLEARANCE: 110 pairs of parts closer than 0.15 mm (0.0000 = touching, as designed or bonded)`. The full list is in out/v10/final/clearance_us9.log: 64 pairs touch (0.0000) and 46 pairs have a gap.

The gaps, smallest first:

| Parts | Gap (mm) |
|---|---|
| the four charging pads to band_flex_away | 0.0050 |
| screen_connector to screen_tail (the J1 slot) | 0.0200 |
| vibration_motor to side_slit_seal (new, the slit conflict) | 0.0237 |
| screen to outer_body, radio_corner; clear_adhesive to outer_body, glass_seal, radio_corner | 0.0293 |
| the coils L10, L71, L72 to outer_body (floor) | 0.0300 |
| antenna to radio_corner | 0.0300 |
| top_C5, top_C1, top_C2, top_FB1, top_C7, top_C14, top_R71, top_R72 to screen_tail (new) | 0.0500 |
| main_board to the two ribbon feet | 0.0500 |
| screen_tail to outer_body (end pocket, new) | 0.0500 |
| cover_glass to outer_body, radio_corner | 0.0500 |
| outer_body to joystick_cap | 0.0500 |
| screen to glass_seal | 0.0579 |
| joystick_dam to vibration_motor | 0.0700 |
| vibration_motor to band_flex_thumb; cell and cell_protection to band_flex_away | 0.0750 |
| outer_body to vibration_motor | 0.0791 |
| screen to cover_glass | 0.1000 |
| outer_body to joystick_frame and to both ribbons | 0.1000 |
| motor_window_seal to vibration_motor | 0.1000 |
| motor_window_seal to side_slit_seal (new) | 0.1210 |
| main_board to outer_body, radio_corner | 0.1250 |
| mic_1, mic_2 to outer_body | 0.1300 |
| screen_connector to screen (J1 at nominal height) | 0.1500 (printed rounded; under 0.15) |

US 7 and US 8: `CLEARANCE: 108 pairs` and `CLEARANCE: 114 pairs` (lines in out/v10/final_us7.log and final_us8.log, not tabled here); US 10 to 13 not run to the end.

## The check's last line per size

Final chain: out/v10/chain_final.sh (second start 18:22:54, pid 45500, order US 9, 7, 8, 10, 11, 12, 13). Summary out/v10/final_chain.log; logs out/v10/final_us7.log to final_us13.log. The delivered files ran it: thin.py 8eff4bf8, check_thin.py 2cf73958.

| Size | Last lines (verbatim) | Findings | Log |
|---|---|---|---|
| US 9 | `RESULT FAIL pairs=1652 parts=58`, `exit 1` | 3, all the -Y slit against the motor: `WALL under 0.4 mm at the motor rim: 0.000 mm at ('front', 150, -1.47, -7.63, -0.18)`, `WINDOW within 0.30 of side_slit_seal: 0.1210 mm`, `SLIT -Y to the motor window 0.1210 under 0.30` | out/v10/final_us9.log, lines 392 to 397 |
| US 7 | `RESULT FAIL pairs=1652 parts=58`, `exit 1` | 2: `WINDOW within 0.30 of side_slit_seal: 0.2454 mm`, `SLIT -Y to the motor window 0.2454 under 0.30` (motor rim 0.425, passes) | out/v10/final_us7.log, lines 390 to 394 (run two at a time, 19:22 to 20:09) |
| US 8 | `RESULT FAIL pairs=1652 parts=58`, `exit 1` | 3: `WALL under 0.4 mm at the motor rim: 0.000 mm at ('front', 150, -1.47, -7.59, -0.26)`, `WINDOW within 0.30 of side_slit_seal: 0.1416 mm`, `SLIT -Y to the motor window 0.1416 under 0.30` | out/v10/final_us8.log, lines 396 to 401 |
| US 10, 11 | not finished: stopped by me at 20:28 on the lead's word, after 18:35 of their checks (out/v10/final/par_stopped.log) | | out/v10/final_us10.log, final_us11.log (partial) |
| US 12, 13 | not started | | |

US 9 has no COLLISION, OUTSIDE or ERROR line (count in out/v10/final/us9_collisions_count.log). Every other rule passes, the v9 rules and the new ones alike.

## Conflicts found and NOT solved (each: the file that must change, who owns it)

1. The -Y side slit against the motor pocket (new, found by the existing rules): at US 9 the outward ray from the motor's hand-end rim crosses the slit, `WALL under 0.4 mm at the motor rim: 0.000 mm at ('front', 150, -1.47, -7.63, -0.18)`, and the motor window (US 7, 8, 9) is 0.1210 from the slit's seal, rule 0.30 (out/v10/dev2_us9.log; per size in the table of the last lines). Cause: the motor (dia 5.0 at motor_x 0.7, X -1.8 to 3.2) reaches into the slit's X range (to -1.45) at its -X rim; the neck needs X -3.4 to -1.6 with 0.15 each end, and the motor cannot move to X min about -1.05 inside the 8.0 band. To change: the slit's depth or shape on the -Y side (design/look/s1/exterior.py variant merged417flatw: the exterior helper) or the motor's place (design/architecture.md 17.26 and 17.27: the lead); the rule is not loosened here. The lead was told at 17:51 (message).
2. Cover glass print window: the turned panel's lit area is X -12.672 to 8.924; the cover glass window (cover-glass.md lines 36 to 40: borders 5.33 at the hand end and 2.38 at the fingertip) and the exterior's lit-area solid (X -9.325 to 12.275, out/v10/probe/ext_labels_us9.log) are still the unturned place. Borders needed: 1.978 at the hand end, 5.726 at the fingertip (14.65 - 12.672, 14.65 - 8.924). Files: design/mfg/specs/cover-glass.md (spec owner), design/look/s1 (exterior helper); an owner question in the study (line 210).
3. Body: design/mfg/specs/body.md needs the fingertip end pocket X 13.725 to 14.165, Y +-6.40, Z 2.10 to 3.42 (metal over it to the lowered seat 3.67: 0.25, to the end face 14.65: 0.485 [CALC from these planes, not probed on the solid]), no hand-end tail pocket, the side slits and SEAL3, RC1 now Z 0 to 3.67 (35.0862 mm3 at US 9). Owner: the body spec (mfg specs lane).
4. Assembly guide design/mfg/assembly/assembly.md: step 17 "Locate" still gives the 3.20 block stack with foam 0.10 (architecture.md line 426); step 20 text ("on the liner", "0.05 mm off the switch bases" all the way down, K-A12 open) against the option A dam (bonded to the stack's edge from its underside, 0.56 high); step 19 can now give the slit seal volume (SEAL3, per size below). Owner: the assembly guide.
5. Parts list design/bom.csv: line 58 DAM1 "dam frame on the liner"; line 60 FOAM1 (no foam in layout C); no row for SEAL3 (the slit seal, DP420 Black). Owner: the parts list.
6. design/architecture.md line 426 (the 3.20 stack with foam) and the band-liner spec item 9 (design/mfg/specs/band-liner.md line 51, K-A12: two-shot proposal) against option A. Owners: the lead (architecture), the liner spec.
7. design/mech/dimensions.csv: 30 ASSUMED rows of the older box model that the thin model does not use (point 7). Owner: design/mech (ring.py's lane).

## The -Y slit against the motor pocket: options

**None of S, X and Z passes every existing rule with no change outside design/mech/thin.** S needs a new rule from the lead and a body change. X fails the 0.40 rule at every size. Z cannot leave metal where the conflict is, because the strip must pass there.

### Sources of the numbers
- **US 9, the delivered model** (out/v10/final_us9.log, final/clearance_us9.log):
  - motor rim `0.000 mm` (rule 0.40);
  - window to the slit `0.1210` (rule 0.30);
  - the window `window: metal removed 0.8122 mm3, extent X -1.329 to 2.729 (4.058 long), Y -6.750 to -5.599, Z 0.100 to 1.258`;
  - motor to the slit seal 0.0237;
  - SEAL2 to the motor 0.1000 and to SEAL3 0.1210;
  - SEAL3 17.3487 mm3 (out/v10/sizes/us9/placement.csv).
- **Other sizes, from primitives** (out/v10/probe/slit_options.log, out/v10/probe/web.log):
  - built from the delivered thin.py's formulas without building the model;
  - the slit is taken as a box from |Y| 5.6 outward, so beyond the skin it counts air as slit;
  - "within 0.40 of the pocket" is the pocket-to-slit distance, standing in for the check's ray rule;
  - the check's own per-size lines come with the size runs.

Per size (primitives):

| Size | Pocket inside the slit box | Motor to the slit box | Slit within 0.40 of the pocket: X, Z | Its area on the slit wall X -1.45 |
|---|---|---|---|---|
| US 7 | 0.0000 mm3 | 0.1479 | -2.042 to -1.450, -0.200 to 0.548 | 0.5609 mm2 |
| US 8 | 0.0013 | 0.0253 | -2.180 to -1.450, -0.200 to 0.694 | 0.7988 |
| US 9 | 0.0060 | 0.0000 | -2.228 to -1.450, -0.230 to 0.769 | 0.9979 |
| US 10 | 0.0207 | 0.0000 | -2.263 to -1.450, -0.630 to 0.519 | 1.3211 |
| US 11 | 0.1884 | 0.0000 | -2.300 to -1.450, -1.040 to 0.609 | 2.7240 |
| US 12 | 0.3470 | 0.0000 | -2.200 to -1.450, -1.450 to 0.565 | 4.0742 |
| US 13 | 0.8244 | 0.0000 | -2.300 to -1.450, -1.850 to 0.531 | 5.6897 |

### What holds the motor, and whether its case is closed
- **Hold:** today the motor is held by a glue line 0.05 thick all round it, the pocket floor included (thin.py `motor_glue`), under the cast liner. assembly.md step 19 says "the motor is glued rigid in its pocket anyway".
- **Motor sheet** (design/datasheets/slim2_jinlong-w0525ab001d.pdf, text in out/v10/probe/jinlong_text.log): the parts list names "CASE", "SPCC", "BRACKET", "SUS304" and "DOUBLE-SIDE TAPE", "DT7605-45 (0.045t)".
  - It warns: "If some materials(metal, powder) and dust become mixing condition in the motor it might cause feature declines by occurring rotation faulty".
  - And: "Please be careful of not soaking in liquid like water or alcohol".
- **Whether the case is closed against a liquid sealant: not in a document on disk.** My reading of those two warnings is that it should be treated as not sealed.

### S. The slit's sealant closes the rim
- **(a) The web.**
  - At US 9 the check leaves 0.1210 of metal between the motor window and the slit seal.
  - On the primitive window, metal under 0.30 lies at Y -6.750 to -6.600 (about 0.15 long) and Z 0.120 to 0.170 (about 0.05 high, at the probe's 0.05 grid), 0.140 to 0.295 thick.
  - At US 8 it is 2 grid points (0.220 to 0.260, Y -6.650 to -6.600, Z 0.100). At US 7 there is none (out/v10/probe/web.log).
  - A cutter cannot leave such a web standing, so S must remove it on purpose. The body is then the slit, the motor window (US 7 to 9) and the web between them cut as ONE opening, closed by ONE seal (SEAL2 and SEAL3 as one plug, applied in step 19).
  - On US 10 to 13 (no window) the slit opens into the pocket itself (0.0207 to 0.8244 mm3 of overlap), and the same one-opening shape applies.
- **(c) Hold and contact.** At that rim the motor is held by its glue line and by the seal itself, with no metal on that side.
  - The seal reaches the motor's glue line on US 8 to 13: motor to the slit 0.0253 at US 8, 0.0000 from US 9.
  - At US 9 the model has 0.0237 between the motor and SEAL3.
  - Only US 7 keeps 0.1479.
  - With the case not documented as closed, the seal must not enter the case.
- **Rule to replace "0.40 metal" there** (yours to set): the seal at least a named thickness (for example 0.20) between its outer face and the motor's glue line, and no seal in the 0.05 glue gap. No size passes 0.20 as modelled.
- **Changes:** exterior.py (the slit and window merged on the -Y side), body.md (the one opening per size), assembly.md step 19 (one plug: window and slit together, not into the motor's glue gap), check_thin.py (the rim and window rules at that spot replaced by your rule).
- **Worse at:** the motor case meets sealant at 6 of 7 sizes; the vibration loads the seal; a larger seal to inspect.

### X. Shift the motor in X and trim the slit's +X clearance
- **Shift:** the band allows motor x up to 1.0 at every size, keeping 0.40 of metal from the pocket (radius 2.6) to the band's side face X 4.0 (the check's WALL_MIN). Today x is 0.7 or 0.8.
- **Slit clearance:** the smallest +X clearance that still passes the neck is 0.15 by body.md line 89 (slit end -1.45). The least defensible value is 0.10, the flex outline tolerance that check_thin.py uses for every ribbon (`WALL_MIN_RIBBON = 0.10`, from band-notes.md), giving a slit end of -1.50.
- **Pocket to slit at x 1.0** (slit end -1.45 / -1.50):

| Size | Slit end -1.45 | Slit end -1.50 |
|---|---|---|
| US 7 | 0.1740 | 0.2150 |
| US 8 | 0.1307 | 0.1723 |
| US 9 | 0.0676 | 0.1104 |
| US 10 | 0.0000 | 0.0437 |
| US 11 to 13 | 0.0000 | 0.0000 |

- **No combination reaches 0.40.** It would also move FLEX1's routed motor lands, which you have ruled fixed.
- **(c) Hold:** the same glue line, with a thinner metal wall on the slit side. The seal touches the motor wherever the distance above is 0.0000.
- **Changes:** thin.py SIZE_TABLE motor_x, design/ecad/band FLEX1 lands, exterior.py's slit end, body.md line 89.
- **Worse at:** it fails at every size and moves routed lands.

### Z. Leave metal in the lower outer part of the -Y slit
**(b) What the neck sweeps** (assembly.md steps 14 and 15, hotbar-joint.md section 2.3: free ribbon length 0.000 at every size, lift allowed 0.000, tilt 0.00 deg).
- With no free length, the foot, the fold and the neck move as one with the board. The board fits its pocket with 0.15 a side (12.6 in 12.9), so once the board is in the cavity the neck can go straight down at Y 5.9 into the floor slot, which is open from above, but it cannot slide sideways.
- What must pass the wall sideways is the strip where it crosses the floor: the floor ring round the slot, from the slot bottom to the floor top (Z -0.20 to 0.40 at US 7 up to Z -1.85 to 0.40 at US 13). Above that it is in the cavity; below it, in the channel, laid from the bore.
- A ring of metal closed at ANY level between the slot bottom and the floor top holds the strip. So the opening has to reach from the slot to the outside at every level from the slot bottom up to the floor top, plus the room the strip needs to turn into the cavity above 0.40 and into the channel below. The flex bend inner radius is 0.70 (band-interface.md), not checked here.
- The conflict region (Z from the slot bottom up to 0.519 to 0.769, table above) lies inside that band at every size. So Z can leave metal only above about 0.40 plus the turn, which is not where the motor is.
- This corrects my first Z reading (the floor steps of the first options run, out/v10/probe/slit_options.log rows Z and Z2). Those assumed the strip could cross the wall above a raised floor; the floor ring makes that impossible.
- **(c) Hold:** if a step were possible, the 0.40 metal would stay at the rim. It is not possible, so nothing changes.
- **Changes if pursued anyway:** exterior.py (a stepped -Y slit), assembly.md step 15 (a threading motion that the free length of 0.000 does not allow).
- **Worse at:** it is not buildable with today's ribbon lengths.

### Reading for the lead (not a decision)
The only option that gives a buildable body is S with one merged opening and one seal on the -Y side. It needs your replacement rule and a closed-case answer from the motor maker, or a barrier film over the motor's side before step 19.

## What a later job needs from this model

- Cover glass print window: the panel's lit area X -12.672 to 8.924, Y -5.4 to 5.4 (ctx `lit_x` in the build log; the `mark` solid of part screen), so the window moves 3.6 toward the hand end (conflict 2).
- Case seat: the model adds nothing outside the exterior's outline except the joystick cap and frame, proud by design (the inside-body test of the check); SEAL3 and the blind window fills are flush with the exterior's skin (they are the exterior's slit_fill less the cavity and the necks), so the case can seat on the exterior file itself.
- Antenna simulation: ANT1 at (-10.80, 5.25) on the under face, body X -12.400 to -9.200, Y 4.450 to 6.050, Z 0.230 to 1.430; RC1 resin X -14.650 to -8.600, Y 2.050 to 7.375, Z 0 to 3.670 at US 9; nearest metal the body 0.6000 away, board lands 2.2154; J1 and the screen cable 2.1427 from the copper-free zone (the bond fingers no longer lie over the antenna); the panel lies over the zone 0.97 higher than in v9 (its underside Z 2.82, v9 1.85); the block metal is 0.97 taller round the corner. Files: out/thin-inside.step (labels `<part>__<class>`), placement.csv.
- The app's Inside screen: layers.json and out/thin-inside.glb, same node contract as v9 (top nodes = placement.csv rows, children `<part>__<class>`); new nodes screen_tail (the full cable), side_slit_seal, chip_C90, chip_R73, top_C5, top_C1, top_C2, top_FB1, top_C7, top_C14, top_R71, top_R72; node foam is gone; screen_connector now stands on the board's top face (layer board); the screen layer holds screen and screen_tail only.

## check_thin.py: what changed (diff against v9: out/v10/final/check_thin_v9_to_v10.diff)

No limit, threshold or expected value of a v9 rule was changed or loosened. Changes:
- 14a board check: the source is the routed board's design/ecad/ring/pcb/placement-final.csv (v9: the board plan placement-plan.csv); side B parts mirrored in their y; a side B part's height measured upward; new: the face of each body and of each land (F under the board, B over it); 26 parts in the list (v9 16).
- The light-removed test: its foam line (v9: "the foam is solid at the old hole") becomes "FOAM1 is absent" (the foam is gone in layout C); the rule itself moved to 15b so the named tests and the full check run one code.
- The stack line: "foam 0.10" becomes "board to panel 1.07"; the rule (sum = glass top) is unchanged.
- The lowest-part line also takes C90 and R73.
- Pair test: a class pair whose bounding boxes do not meet is skipped before the boolean, and the count line says how many (`class pairs with boxes apart skipped`); the pair count is unchanged. Found afterwards: v9's own `def common(a, b)` already returns 0 for boxes that do not meet, so this skip changes the count line only, not the time and not the result.
- New report: every pair of parts closer than 0.15 (CLEARANCE lines).
- New rules, section 15 `check_v10`, each with its expected values written in the check with their source (STACK_SRC, CABLE_SRC, SLIT_SRC): 15a STACK-ABOVE; 15b CABLE and FOAM1 absent; 15c SLIT threading path and SLIT seal; 15e slit to the motor pocket or window (0.30, the v6.2 rule for the -Y floor slot applied to the slit); 15d DAM barrier and DAM before the cast.

## Broken copies (one line of thin.py changed in each: out/v10/broken/<rule>/broken.diff; run through the named tests at US 9 by out/v10/run_broken.sh; findings each adds over the unbroken base: out/v10/broken/diff_summary.log, base out/v10/dev3_named_us9.log `RESULT FAIL 1`, its one finding the slit-to-window rule)

| Rule | Change | Log | Last line | Findings over the base |
|---|---|---|---|---|
| 15b FOAM1 absent | a foam piece added | out/v10/broken_foam_absent_named_us9.log | `RESULT FAIL 2` | `FOAM1 present: layout C has no foam frame ...` |
| 14a face (new part of the board check) | J1's housing under the board | out/v10/broken_board_face_named_us9.log | `RESULT FAIL 5` | `BOARD-PLAN J1: face: body Z 0.5300 to 2.6700, side B, board 1.4500 to 1.7500`, the J1 stack rows, `CABLE J1 not on the screen face` |
| 15a STACK-ABOVE | first copy scr_gap 1.00: the build stopped (my guard: the cable then ends at -4.9026, not -4.833), a crash, not a result (out/v10/broken_stack_above_named_us9.log); second copy adh_t 0.12 | out/v10/broken_stack_above2_named_us9.log | `RESULT FAIL 11` | 10 STACK-ABOVE rows (board top 1.7300 against 1.7500, ...) and `STACK-ABOVE J1 at its highest 2.7700 + 0.05 over the panel underside 2.8000` |
| 15b CABLE | neck 5.0 | out/v10/broken_cable_named_us9.log | `RESULT FAIL 2` | `CABLE neck 5.0000, source 4.805` |
| 15c SLIT path | a 2.0 x 0.3 x 0.3 metal bar left in the +Y slit | out/v10/broken_slit_path_named_us9.log | `RESULT FAIL 2` | `SLIT +1 blocked: 0.1800 mm3 of metal in the threading path` |
| 15c SLIT seal | a void cut in SEAL3 | out/v10/broken_slit_seal_named_us9.log | `RESULT FAIL 2` | `SLIT +1 seal leaves 0.3150 mm3 open` |
| 15e slit to motor | US 9 motor_x 0.3 | out/v10/broken_slit_motor_named_us9.log | `RESULT FAIL 1` | `SLIT -Y to the motor window 0.0000 under 0.30`; the base already fails this rule at US 9 (0.1210), so this copy shows the value moving, not the rule turning red |
| 15d DAM barrier | the v9 0.05 gap down to the dam's bottom | out/v10/broken_dam_barrier_named_us9.log | `RESULT FAIL 2` | `DAM barrier open: 1052 of 10440 points, first (-3.152, 3.205, 9.5826)` |
| 15d DAM before the cast | dam 0.2 deeper than the stack | out/v10/broken_dam_precast_named_us9.log | `RESULT FAIL 2` | `DAM stands on the liner: bottom r 9.3626, stiffener underside r 9.5626, liner face r 9.7726` |

The broken copies ran through the named tests alone (out/v10/named_v10.py imports the copy's thin.py and calls check_board_plan, check_zone and check_v10 of the delivered check, same hash 2cf73958), not through the pair test, as in v8 and v9.
## Working log (in order; each look at a result is listed)

- 16:50 v9 files kept (out/v10/before/shasum_before.log). 16:55 exterior labels read (out/v10/probe/ext_labels_us9.log: body, glass 3.72 to 4.1455, screen, joystick, mic_1, mic_2, slit_fill of 6 solids, 21.6299 mm3).
- Board sources: the routed board's own pad positions for a side B part (J1) read from ring.kicad_pcb (out/v10/probe/pcb_read_J1.log: a side B footprint is stored mirrored in its y); plan against final rows (out/v10/probe/plan_vs_final.log: new C90, R73; X1 turned 180; J1 and eight 0201 parts on side B; 7 test pads gone).
- 17:01 first dev build at US 9 (out/v10/dev1_build_us9.log, `exit 0`, 58 parts). 17:04 named tests on the dev copy (out/v10/dev1_named_us9.log, `RESULT PASS`) and the red state: the same tests on the v9 model with its own exterior (out/v10/red_v9_named_us9.log, `RESULT FAIL 40`, exit 1). The red run showed one rule that did not separate v9 from v10: the dam's "stands on the liner" test passed on v9 by the projected radius; rule changed to "the dam reaches exactly down to the stack's underside" (edit6), and the liner fill widened to the pocket footprint under the dam (edit6).
- 17:07 full dev check at US 9 started without the box skip (out/v10/dev2_us9.log; its check process read check_thin.py after edit7, hash in out/v10/dev2_note_check_hash.log, not the hash printed at the log's start).
- During it (dev only, not in that run): clearance report (edit8), the box skip of the pair test (edit10), the slit-to-motor rule 15e (edit12).

- 17:46 dev2 ended: `RESULT FAIL pairs=1652 parts=58`, two findings, both the -Y slit against the motor (`WALL under 0.4 mm at the motor rim: 0.000 mm at ('front', 150, -1.47, -7.63, -0.18)`, `WINDOW within 0.30 of side_slit_seal: 0.1210 mm`); no collision; told the lead 17:51.
- 17:48 a per-size probe of the motor rim and the slit (out/v10/probe/motor_slit.py) was stopped by me at 17:51 (pids 27793, 27843, out/v10/probe/motor_slit_kill.log): the rim measure took over 2 minutes per size; its log holds only its start line. The final chain gives the same lines per size.
- 17:52 to 17:56 named tests on the dev copy with rule 15e (out/v10/dev3_named_us9.log, `RESULT FAIL 1`, the 0.1210 slit-to-window finding) and the broken copies (table above). 17:57 the second stack copy (out/v10/broken_stack_above2_named_us9.log).
- 17:57:40 dev files copied into place (out/v10/swap_in.log: thin.py 8eff4bf8..., check_thin.py 2cf73958...; no process ran thin.py there); 17:57:49 the final chain started (out/v10/chain_final.sh, pid 16882; expectations out/v10/expect_final_chain.txt).
- 18:21 the first final chain stopped by me (out/v10/chain1_stopped.log; its logs kept in out/v10/chain1/): its US 7 check ran 22:51 without ending its pair test; my four wait loops on logs that would no longer get their line stopped too (out/v10/waitloops_stopped.log). A try to speed the pair test by cutting the body in chunks (edit15, dev only) was rejected: the chunks' volumes sum to 973.9915 against the body's 975.3034, and a whole-body boolean takes 0.7 s (out/v10/probe/chunk_test.log, out/v10/edit15_rejected.log); the delivered check never had it (hash 2cf73958 throughout).
- 18:22:54 the final chain started again, US 9 first (out/v10/final_chain2_launch.log, pid 45500).

- 19:07 the chain's US 9 check had run 44 minutes without reaching the end of its pair test (out/v10/final/waitloops2_stopped.log shows chain pid 45500 at 44:59); my five wait loops on its log stopped (same file); the chain keeps running. At this pace one size takes about an hour under the present load, so the seven sizes end hours after my time limit: the last-line and clearance sections above stay PENDING until the lead's message that the chain has ended.
- 19:13 lead's message: keep building and bring three options (S, X, Z) with numbers. Primitives per size in out/v10/probe/slit_options.py (log out/v10/probe/slit_options.log, two runs, the second adds the Z2 rows); the motor sheet's text in out/v10/probe/jinlong_text.log; the options section is above. The chain's US 9 log reached its clearance line (110 pairs, out/v10/final/clearance_us9.log).

- 19:21 the chain's US 9 check ended: `RESULT FAIL pairs=1652 parts=58`, three findings, all from the slit. The chain goes on with US 7 (pid 45500).

- 19:22 the lead's second message: chain pid 45500 and only its children stopped by me after US 9 had ended (out/v10/final/chain2_stopped.log); two sizes at a time chosen from the memory read (out/v10/final/parallel_choice.log); out/v10/par_sizes.sh started 19:22:45 (out/v10/final_par.log). Web probe out/v10/probe/web.log; the options section rewritten (first version kept in out/v10/final/options_section.md); the Z reading corrected.

- 20:28 the lead's third message (the owner chose the custom full-face panel and the 3.20 mm block; v10 becomes the fallback): my size runs stopped by pid (out/v10/final/par_stopped.log, before that out/v10/final/par_before_stop.log); v10 kept in design/mech/thin/fallback-417/ with a README and sha256 hashes; the live files restored to v9 (out/v10/final/restore_v9.log, out/v10/final/restore_verify.log).

## Final state (20:29)

- Built: inside model v10 for the 4.17 mm block and the stock screen, points 1 to 7 above. It is now the fallback in design/mech/thin/fallback-417/ (README.md, thin.py, check_thin.py, placement.csv, layers.json, us9/ outputs, thin-notes-v10-section.md, a copy of these notes).
- Checked: US 9, US 7, US 8 to their last line (table above), each failing only on the -Y slit against the motor pocket. US 10 and 11 were stopped unfinished, US 12 and 13 never started. The bar (pass at US 7 to 13) does not hold.
- The live files of design/mech/thin are back to v9. thin.py, check_thin.py, placement.csv, layers.json, thin-notes.md, out/thin-inside.glb and out/thin-inside.step each equal their copy in out/v10/before/, by the sha1 of shasum_before.log and by sha256 (out/v10/final/restore_verify.log: 7 lines `EQUAL`).
- out/triangles.txt was not kept before I overwrote it. It is rewritten as 372840 (the v9 build's count, out/v9/build_v9_us9.log), not proven by a hash.
- __pycache__/thin.cpython-312.pyc is a cache my runs rewrote; it is not restored.
- Added and kept: model-v10-notes.md, fallback-417/, out/v10/.
- The owner chose "Sealed opening" (option S); the v10 model does not carry it.

## For the thin model (3.20 mm block, custom panel; not started)

What carries over from v10 unchanged, and what each needs from the thin block:
- **Side slits and SEAL3:** they need the thin exterior (merged32h line) with the same -Y and +Y slits X -3.55 to -1.45, Z slot bottom to 1.53, and the slit_fill solid. The slit lies wholly under the board (Z under 1.53), so the block's height does not touch it.
- **Sealed opening at the motor (owner's S):**
  - It needs one opening per size: slit, motor window (US 7 to 9) and the web between them as one cut, with one seal (SEAL2 and SEAL3 merged) on the -Y side.
  - It needs the lead's rule for the sealant there (a minimum thickness to the motor's glue line, no sealant in the 0.05 glue gap) and an answer on whether the motor's case is closed (not in a document on disk).
  - The check's rim and window rules at that spot are then replaced by that rule.
- **Dam DAM1, option A:** it lies in the band and does not depend on the block. It carries over as modelled (thin.py joystick_dam block, liner_fill over the 7.0 x 6.8 footprint, check 15d).
- **Board parts:** the 26 parts of placement-final.csv carry over (side B mirrored in y, C90, R73, the eight screen-face 0201 parts), unless the custom panel's connection moves J1 or the screen-face parts.
  - J1, the screen-face parts and the J1 rules (15a, 15b) depend on the panel's connection, which another helper sets first.
  - On a 3.20 block, the board top to panel space is the v9 value 0.10, so nothing taller than 0.10 - 0.02 can stand on the screen face. The eight 0201 parts (0.33) and J1 (0.9) do not fit there [CALC from the v9 stack].
- **Resin corner RC1:** as v9 (X -14.80 to -8.60, Y 2.05 to the skin, all Z): on the thin block it ends at the 2.75 seat again (v9 Z 0 to 2.750, 26.4216 mm3).
- **The motor clash on the thin block:** the band, the slots, the motor and its pocket, and the size table are the same in v9 and v10 (out/v10/final/size_table_diff.log: no difference). The slit lies under the board, at the same Z in both.
  - So the primitive numbers of the options section apply unchanged to the thin block: the pocket within 0.40 of the slit at every size, the slit box in the pocket from US 8 up (0.0013 to 0.8244 mm3), and touching the motor from US 9 up.
  - My reading, not built: the thin exterior's skin under Z 1.53 is merged32h's, the same skin that merged417flat keeps under its fold.

RESULT: blocked, inside model v10 (4.17 mm block, stock screen) is built and kept as the fallback in design/mech/thin/fallback-417, checked at US 7, 8 and 9 where it fails only on the -Y slit against the motor pocket (US 10 to 13 not finished), and the live folder is restored to v9 with every saved file's hash equal.
