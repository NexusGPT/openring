# Band flexible circuits FLEX1 and FLEX2: notes (package W4)

Project root: .. Folder: design/ecad/band/. Written 2026-11-13 by the W4 builder. All commands run from KiCad's own Python through `design/ecad/ring/pcb/run_kipy.sh` (KiCad 10.0.8). Raw logs are in design/ecad/band/evidence/ (final runs in evidence/final/).

Netlist note: design/ecad/ring/netlist.csv was changed by another helper at 2026-11-13 00:20 (switch pins 1 to 4, M1 and BT1 pins 1 and 2). Everything here is built and checked against that version. The J_BAND_A and J_BAND_B rows did not change.

## Files

| File | What |
|---|---|
| band-interface.md | the interface: J_BAND land pattern, fold, cell tabs, PRT1, RT1, motor leads, switches, pads, current and drop |
| band_geom.py, band_layout.py | lengths from the model formulas, land and lane plan |
| measure_step.py, model_lengths.csv | path length measured on the 14 STEP files of design/mfg/parts |
| make_lib.py, OpenRingBand.pretty/ | footprint library (10 footprints) |
| build_band.py | writes the 14 boards flex1-us7 to us13 and flex2-us7 to us13 (.kicad_pcb, .kicad_pro, .kicad_dru) |
| check_band.py, make_broken.py | check and three broken copies (evidence/broken/) |
| band_calc.py | currents, voltage drops, lead cut lengths |
| fab/ | per board: Gerber (F.Cu, B.Cu, F.Mask = coverlay openings, B.Mask, Edge.Cuts, User.1 = stiffener outline), Excellon drill, job file; per tail a PDF drawing with dimensions and fold lines; since 2026-11-13 also the paste Gerber (F_Paste on FLEX1, B_Paste on FLEX2), a fab notes text with the panel instruction, and land numbers and nets on the drawing (make_fab.py writes them all). 7.9 MB for the whole design/ecad/band folder |
| design/datasheets/w4_alps_skta_catalog.pdf, w4_alps_sktaaae010_spec.pdf | Alps' own catalog and product page documents (public, downloaded from tech.alpsalpine.com) |

## Stack and rules (point of the lead's ruling), source: JLCPCB flexible PCB capabilities page, fetched 2026-11-13, saved text evidence/web/jlc_flex_text.txt

Polyimide core 25 um, copper 12 um both sides, coverlay (PI 12.5 um + adhesive 15 um on 12 um copper) both sides, finished 0.11 mm (page: "FPC Finished Thickness", 2-layer 25 um: 0.11 mm); with 0.10 PI stiffener 0.21 mm at the foot and head against the model's 0.15 allowance (0.225 at the head: 0.15 + 0.075 stiffener). ENIG. Rules: line 0.08, gap 0.10 (page: 12 um copper 3/3 mil), exposed land to line 0.25 (0.15 + coverlay expansion 0.10), copper to edge 0.30, via 0.30 / 0.10 drill, outline tolerance +-0.10. Minimum bend radius 6 x 0.11 = 0.66 mm (static bend); fold radius used 0.70 inner (centre line 0.755): margin 0.04 mm.

## a. Interface document

File: design/ecad/band/band-interface.md. Land pattern of J_BAND_A and J_BAND_B (section 2), tail-end pattern and fold with radius against the minimum (section 3), cell tabs, PRT1 and RT1 with the ground land (section 5), motor leads and cut lengths (section 6), switches (section 4), charging pads (section 8), differences from the model (section 9). Each value carries its source line or a calculation. Command to see the last line of the file: `tail -1 design/ecad/band/band-interface.md` (last line is the end of section 9).

## b. Boards

Command: `design/ecad/ring/pcb/run_kipy.sh design/ecad/band/build_band.py` (log evidence/final/build.log, last line `boards written: 14`, exit 0). Lengths come from `band_geom.py` (the formulas of design/mech/thin/thin.py: SIZE_TABLE lines 94 to 103, ribbon pieces lines 576 to 613, bend line 592, pads line 604 to 605) and are proven against the STEP files by `measure_step.py` (volume of each solid divided by width times 0.15; evidence/measure_step2.log, model_lengths.csv). Flat length = model path + 2.071 mm (the flat foot 1.745 and the board fold 1.186, less the 0.860 that the model's vertical piece already has above the fold; band_geom.py FOOT_EXTRA).

| US | FLEX1 flat length, mm | FLEX1 model path | FLEX2 flat length, mm | FLEX2 model path |
|---|---|---|---|---|
| 7 | 16.115 | 14.044 | 32.184 | 30.113 |
| 8 | 16.136 | 14.065 | 33.388 | 31.317 |
| 9 | 16.122 | 14.051 | 34.598 | 32.527 |
| 10 | 16.597 | 14.526 | 35.813 | 33.742 |
| 11 | 17.079 | 15.008 | 37.033 | 34.962 |
| 12 | 17.566 | 15.495 | 38.257 | 36.186 |
| 13 | 18.058 | 15.986 | 39.485 | 37.414 |

(evidence/final/band_calc.log). Each board holds: Edge.Cuts outline, fold lines and notes on Dwgs.User, stiffener outlines on User.1, copper on F.Cu and B.Cu, vias, the coverlay openings as the mask layers, and dimensions; since 2026-11-13 also the paste openings (F.Paste on FLEX1, B.Paste on FLEX2) and the land labels on Dwgs.User (section "Change 2026-11-13: paste layers and land numbers"). FLEX1 has 16 vias (head), FLEX2 11. FLEX1 head: 5 switches, motor lands, 8 foot lands. FLEX2: 7 foot lands, PRT1 lands, 4 disc lands.

## c. Connectivity and rules check

check_band.py computes the connectivity from the copper shapes themselves (tracks, vias, pads touching each other on the same layer), not from the net labels, and compares each group of lands with the netlist nets (netlist.csv) on that tail. Copper joined to terminals not in the netlist fails. Terminals not soldered on the tail (switch terminals 1 and 2 of SW1, SW3, SW4, SW5, joined to 3 and 4 inside the Alps part per its circuit diagram) are left out of both sides. It also runs `kicad-cli pcb drc --severity-all --all-track-errors` per board and requires 0 violations and 0 unconnected.

Command: `design/ecad/ring/pcb/run_kipy.sh design/ecad/band/check_band.py`, exit 0, log evidence/final/check_all.log, last line `RESULT: PASS boards checked 14`; in it 14 lines `kicad-cli drc: violations 0, unconnected 0`. Per-board KiCad reports: design/ecad/band/*-drc.rpt (written by the check). Rules file per board: .kicad_dru (exposed land to line 0.25, land to land 0.15) and .kicad_pro (line 0.08, clearance 0.10, edge 0.30, via 0.30/0.10).

## d. Footprint library

design/ecad/band/OpenRingBand.pretty: Alps_SKTAAAE010_4pad, Alps_SKTAAAE010_pads34, W0525AB001D_Lands, PRT1_Tabs, CP_Pad_1.6, RT1_NTC_0402, J_BAND_A_BOARD, J_BAND_B_BOARD, J_BAND_A_TAIL, J_BAND_B_TAIL. Each description names its document and page. Alps terminal numbers as Alps gives them (catalog page 2, Drawing No.1: 1 top left, 2 top right, 3 bottom left, 4 bottom right, seen from above; 1 with 3 and 2 with 4 are joined). The word in question does not occur: `grep -ril provisional design/ecad/band/OpenRingBand.pretty design/ecad/band/band-interface.md design/ecad/band/*.py` prints nothing (exit 1). Library written by `make_lib.py` (evidence/make_lib.log). The motor footprint's pads are named 1 and 2 as the netlist's M1 pins.

## e. Check script and broken copies

Good boards: exit 0 (section c). Broken copies (made by make_broken.py from the final boards, logs evidence/final/):
1. swapped line (CP1 and CP2 discs swap places): evidence/final/check_swapped.log, exit 1, last line `RESULT: FAIL boards checked 1`.
2. missing land (PRT1 removed): evidence/final/check_missing.log, exit 1, `RESULT: FAIL boards checked 1`.
3. wrong length (outline 0.30 mm too long): evidence/final/check_length.log, exit 1, `RESULT: FAIL boards checked 1`, and it prints `outline length 16.4218 formula 16.1218 (diff +0.3000)`.
Length rule: within 0.05 mm of the model path, tested against two measures (formula and STEP).

## f. Fabrication outputs

design/ecad/band/fab/: 14 folders (Gerber, drill, job) and 14 PDF drawings (`flexK-usN-drawing.pdf`) with dimensions (flat length, width, fold length) and fold lines on a drawing layer (since 2026-11-13 also land numbers and nets, paste Gerbers and fab notes, written by make_fab.py; see the section of that date). Command log evidence/final/fab-summary.log: 42 lines, all `... 0` (exit 0 per Gerber, drill and PDF command). Size of design/ecad/band: 7.9 MB (`du -sk`, 7988 KB).

## g. The three connections no file drew

1. Cell protection circuit PRT1: it is the cell's protection board; three output tabs P+ (VBAT, J_BAND_B land 1), NTC (land 3), P- (GND, land 2) on the PRT1_Tabs lands of FLEX2. Drawn in all 7 flex2 boards, explained in band-interface.md section 5. Not in the netlist (the netlist joins BT1 pins 1 and 2 directly; the PRT1 tabs are the physical route of those two pins and the check maps BT1 pin 1 and 2 and RT1 pin 1 and 2 to the PRT1 lands: band_layout.PRT1_MAP).
2. Ground of RT1: RT1 pin 2 is on the PRT1 board and joined there to tab P-; its land on the tail is FLEX2 land 2 of J_BAND_B (CELL-, net GND).
3. Switch ground on FLEX1: terminals 2 and 4 of each switch (GND side) go to B.Cu GND traces in the head (0.10 wide, joined in a star at the middle with vias), then one 0.10 line to the neck GND lane (head frame x 0.085), which continues as the 0.20 GND lane (B.Cu) to a via in the gap row at the foot; from that via a short F.Cu stub goes to land 6 (MOT-) and an F.Cu strap joins land 6 to land 8 (GND) of J_BAND_A. Both are GND on the board. The motor's GND (M1 pin 2, land 2) joins the same B.Cu lane through a via at its land.

## h. What the model does not allow

Tail 1.4 wide cannot hold the lines: drawn at 1.8 (the nearest design that works). See "Changes other files need".

## Deferred items closed here

| Item | Closed by |
|---|---|
| 30 | tails drawn and routed at every size, both tails: boards, section b |
| 31 | pad numbers: the netlist's, fixed in the J_BAND footprints; tail-end mate (band-interface.md sections 2 and 3) |
| 32 | order VBUS, D-, D+, GND with rising angle: pads drawn in that order along the tail (build_rows.json pad_u, flex2 boards); axis: along the tail from the slot toward the pads; same order as the model (thin.py line 611) |
| 35 | stack, finish, coverlay, widths, lengths and path per size: stack section above, table b |
| 37 | ribbon joint at the board end: hot bar, section 7 of band-interface.md; lengths per size and fold radius: table b and section 3 |
| 38 | line count 8 and 7 in 1.4 mm: not possible; 1.8 mm needed, drawn (section 9, item 1) |
| 39 | lead cut length per size: band-interface.md section 6 table |
| 46 | M1 pin 1 = red = VMOT = land 7; pin 2 = blue = GND = land 6 (section 6) |
| 118 | pad: copper land plus gold disc (section 8) |
| 162 | tab order and PRT1: section 5 |
| 163 | switch terminals: Alps drawing numbers (section 4) |

Conflicts of connections.md: motor side = FLEX1 (as ruled); RT1 sits at the cell on FLEX2 through PRT1; pad size 1.6 mm (CP_Pad_1.6).

## Not closed

1. Tab nickel strip size and the tab order of PRT1 are requirements I wrote, not a maker's sheet; the cell part is custom (the lead's ruling says its interface is ours). Nothing is open on the design side; the only unknown is whether the cell supplier builds it: that is S12 and needs the supplier's quote (no contact allowed).
2. Hot bar settings (260 C, 4 s, 20 N), iron limits at the PRT1 tabs (280 C, 2 s) and the motor leads (320 C, 2 s) are starting values from the Alps and polyimide limits, not measured on a built unit. The build guide must hold the measurement (cell voltage before and after; continuity). Tried: no maker sheet gives the cell's heat limit.
3. The motor lead exit pitch at the motor rim (1.0 mm) is read from page 9 of the Jinlong drawing (detail A dimensions 0.5 and 1.0, small scale); lead cut length per size rests on it.
4. (Status after model v8: done, see "After model v8".) A tail 1.8 wide and the foot were not in the 3D model when this was written. The plan view shows the neck edge 0.2 mm over the motor's rim (X -1.6 against -1.8) at the motor: they are at different radii (ribbon 0.075 below the liner face, motor on the liner; thin.py lines 120, 499) but only the model's pair test can confirm it.
5. Vias in the lands (via in pad) and the 0.05 mm mask opening difference are accepted by this design; the capability page lists via-in-pad as not stated. If the maker refuses it the vias move 0.4 mm next to the lands (room exists at the foot, not in the head).
6. Gerber coverlay layers are the mask layers (F.Mask, B.Mask) and the stiffener is User.1; the order of an actual board needs those names told in the order notes (they are in the drawings).

## Changes other files need

| File | Value now | Value needed | Why |
|---|---|---|---|
| design/mech/thin/thin.py line 66 `tail_w` | 1.4 | 1.8 | 5 + 2 lines in the FLEX1 neck, 4 + 3 in FLEX2 (band-interface.md section 9) |
| design/mech/thin/thin.py line 66 `tail_x` | -2.6 | -2.5 | neck centred in the slot X -3.5 to -1.5 (0.1 each side) |
| design/mech/thin/thin.py line 64 `stiff_t` and line 52 `flex_t` | 0.075 / 0.15 | 0.10 stiffener; flex 0.11 (0.15 stays as allowance) | the offered stiffener is 0.10; head stack 0.11 + 0.10 = 0.21 against 0.225 |
| design/mech/thin/thin.py lines 603 to 609 (FLEX2 pad strip) | strip X -2.25 to 0.25 | X -3.4 to 0.25 | straight lines to the pads |
| design/mfg/specs/band-flex-tails.md line 1 ("No flat pattern exists yet") and open points 0 to 5 | open | closed by design/ecad/band | flat pattern, stack, fold, lands exist |
| design/mfg/specs/band-flex-tails.md critical dimensions, tail width | 1.4 | 1.8 at the neck, 2.5 at the foot | as above |
| design/ecad/ring/parts.csv rows CP1 to CP4 | `gold pad 1.0mm`, ring:PAD_1.0 | 1.6 mm, OpenRingBand:CP_Pad_1.6 | architecture 17 and lead's ruling |
| design/ecad/ring/parts.csv rows J_BAND_A, J_BAND_B | provisional pads | OpenRingBand:J_BAND_A_BOARD and J_BAND_B_BOARD | land pattern of band-interface.md section 2 (origin X -2.250, Y -4.325 and +4.325) |
| design/ecad/ring/parts.csv rows SW1 to SW5, M1, BT1, RT1 footprints | ring:Alps_SKTA, ring:WIRE_LEADS_2, ring:CELL_TABS, ring:R_0402 | OpenRingBand footprints of section d; BT1 and RT1 to PRT1_Tabs | same |
| design/ecad/ring placement of J_BAND on the ring board | X -2.2, Y +5.15 and -5.55 | pad group middle at X -2.250, Y +-4.325, keep-out X -3.5 to -1.0, |Y| 3.4 to 5.6 | band-interface.md section 2 |
| design/bom.csv lines 74, 75, 78, 79 | "outline not drawn" | boards in design/ecad/band | drawn |
| design/mfg/assembly/assembly.md steps 6 to 9 | switch land pattern open | the footprints and the soldering values of band-interface.md sections 4 to 8 | |


## Change 2026-11-13: board courtyards
The courtyards of J_BAND_A_BOARD and J_BAND_B_BOARD are now exactly the keep-out of band-interface.md section 2, 2.5 x 2.2 mm (X -3.50 to -1.00, |Y| 3.40 to 5.60), i.e. x -1.25 to +1.25 and y -0.925 to +1.275 (B) or -1.275 to +0.925 (A) from the footprint origin (make_lib.py).
After rebuilding the library and the 14 boards: check_band.py exit 0, last line `RESULT: PASS boards checked 14` (evidence/final/check_all2.log); the ring footprint check exit 0, last line `RESULT PASS 117 parts, 19 footprints, 411 pins have pads, pad counts equal footprint-sources.csv, no PROVISIONAL` (evidence/final/ring_check_footprints.log).
Nothing else changed; the pad positions and the 14 boards are the same.


## Change 2026-11-13: J_BAND_A numbering and mating test
The table of band-interface.md section 2 was stale for lands 1, 4, 6 and 8 of J_BAND_A; the footprint J_BAND_A_BOARD and the 14 boards were right, and the table is corrected. check_band.py now lays each tail foot (outer face F.Cu against the board, no mirror) on the delivered board footprint and requires every land (8 and 7) within 0.05 mm and on the same net: all 14 boards pass, worst offset 0.0000 mm, last line `RESULT: PASS boards checked 14` (evidence/final/check_all3.log).
Broken copy with lands 1 and 4 of the FLEX1 foot swapped: exit 1, `FAIL mating: land 1 JOY_UP ... off by 0.900` (evidence/final/check_mate.log, last line `RESULT: FAIL boards checked 1`). Table: band-interface.md section 2, "Mating of the tail foot".


## After model v8

Model v8 (commit cdb1ddc) holds the 1.8 neck, the fold, the foot and the 0.10 stiffener; its fit check passes at US 7 to 13 (design/mech/thin/band-fit-notes.md). The "not yet in the 3D model" status rows (Not closed 4, Changes rows on tail_w, tail_x, stiff_t, FLEX2 strip) are therefore done.
1. measure_step.py now reads the v8 files (FLEX1 6 solids, FLEX2 5; 0.11 at neck, fold, foot, head; 0.15 at trunk and strip) and rewrote model_lengths.csv (v7 version kept as evidence/model_lengths_v7_files.csv). Its totals already contain the fold and foot.
2. check_band.py compares each board with the new totals WITHOUT adding FOOT_EXTRA, and with the formula. All 14 boards pass: FLEX2 differs by 0.0000 mm, FLEX1 by -0.0172 to -0.0181 mm (v8 bend piece is 0.018 mm longer), limit 0.05. Command `design/ecad/ring/pcb/run_kipy.sh design/ecad/band/check_band.py`, exit 0, last line `RESULT: PASS boards checked 14` (evidence/final/check_all4.log). Broken copy with a 0.30 mm longer outline: exit 1, `outline length 16.4218 formula 16.1218 (diff +0.3000) STEP 16.1397 (diff +0.2821)` (evidence/final/check4_length.log); the swapped-line and missing-land copies also exit 1 (check4_swapped.log, check4_missing.log).
3. band_geom.py comment rewritten (words only). 4. Motor 0.8 mm off the centre line at US 7 and US 12: the motor land position does not change (it follows the arc position); the lead cut length grows from 1.05 to 1.12 mm at US 7 and from 1.39 to 1.44 mm at US 12 (band-interface.md section 6, evidence/final/band_calc2.log). Boards unchanged, no rebuild.

## Change 2026-11-13: paste layers and land numbers (process.md changes C1, C2, C13, C4)

Why: the joint table (design/mfg/assembly/joint-gaps.md) and wiring review 3 (faults G2, G7) found that no stencil could be cut for the ribbons and that no drawing showed which land is which. Work notes and every log: band-paste-notes.md and band-paste-work/.
1. C1, FLEX1: the switch footprints Alps_SKTAAAE010_4pad and Alps_SKTAAAE010_pads34 carry F.Paste on every land (1:1, 0.55 x 0.55; make_lib.py). 12 openings per board, on the switch face F. The 8 unsoldered terminals have no land, so no opening.
2. C2, FLEX2: four round paste openings, 0.58 mm, 0.49 mm from each disc land centre on the diagonals, drawn as filled circles on B.Paste by build_band.py (PASTE_DISC_D, PASTE_DISC_OFF), not as pads: design/wiring/check_wiring.py counts every pad of a band board, and the ring's check_footprints.py counts the pads of CP_Pad_1.6, which is unchanged. 16 openings per board, on the disc face B; gap to the centre via 0.05 mm. A first version with paste-only pads made check_wiring.py fail (28 lines band-pad); replaced the same day.
3. C13: every drawing has a detail of the board end, 4 times the ribbon view, with each land's number and net and a legend "LAND n = NET"; FLEX1 marks the motor lands "1 +: VMOT (red)" and "2 -: GND (blue)"; FLEX2 names the tab lands "P+ tab: VBAT", "NTC tab: NTC", "P- tab: GND". Text 0.3 mm on the board (land numbers 0.6 mm), 1.77 to 2.12 mm on the A4 page.
4. C4 without copper: fab/flexK-usN/flexK-usN-fab-notes.txt and a drawing note give the panel instruction of process.md P7 (rails 5 mm, three 1 mm fiducials on the paste face at 3.85 mm from the panel edges).
5. New script make_fab.py writes all fab outputs (Gerber with the paste layer, drill, PDF, notes). Run on the boards as they were before this change it gives the same Gerber geometry and drill files as the old fab folder and drawings within 14 pixels at 100 dpi.
6. Nothing else changed: pad, track, via, outline and net dump identical before and after except paste layers and drawing text. check_band.py exit 0, last line `RESULT: PASS boards checked 14` (band-paste-work/logs/check_band5.log); check_wiring.py --require-complete exit 0, `problems 0` (band-paste-work/logs/check_wiring5.log); it rewrote the 14 flex*-drc.rpt files.
7. Board-side lands (lead's addition): J_BAND_A_BOARD and J_BAND_B_BOARD carry one F.Paste opening per land, 0.30 x 0.44, centred, as a filled rectangle in the footprint (make_lib.py JB_PASTE; design/mfg/assembly/hotbar-joint.md section 1 with the 0.075 mm parts face stencil of process.md P2). Not a pad: the ring's check_footprints.py compares the pad count (8, 7) with footprint-sources.csv, and paste-only pads made it fail on the board helper's copy (band-paste-work/logs/ring_check_footprints_helperlib.log).

RESULT: done, 14 boards (flex1-us7 to us13, flex2-us7 to us13), each kicad-cli drc 0 violations and 0 unconnected, check_band.py exit 0 on all 14 and exit 1 on 3 broken copies
