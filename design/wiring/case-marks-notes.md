# Case pin board marks, wire order, wire pads in the netlist (review 2026-11-13, minors m2, m3, m4)

Written 2026-11-13 (clock from `date`; start 11:30 CET, last check run finished 11:47 CET). ROOT = .. E = ROOT/design/ecad/case/pcb/evidence/marks/ (all logs; copies before the change in E before/). Full text of the changes: ROOT/design/ecad/case/pcb/board-notes.md, "Wiring table (replaces part f)" steps 1 to 7 and "Round 3".

## What was changed (files)
- ROOT/design/ecad/case/pcb/case_pins.kicad_pcb and case_main.kicad_pcb: silkscreen text only (script ROOT/design/ecad/case/pcb/add_marks.py; diffs against the old files have 0 removed lines: E diff_case_pins.txt, E diff_case_main.txt).
- ROOT/design/ecad/case/make_netlist.py (and the files it writes: netlist.csv, parts.csv, additions.csv, case-kicad.xml, case_ringlink.kicad_sch, erc-report.*, case-schematic.pdf through run_all.sh).
- ROOT/design/ecad/case/pcb/check_boards.py (WP pads are ordinary placed parts now; sixth check "marks"), make_bom.py, board-notes.md, ROOT/design/ecad/case/sch-notes.md, fab/ (made again).

## m2 marks
- The pin board file holds three separate closed outlines (12 Edge.Cuts lines, gaps 0.10 mm; E pins_dump_before.log), so route (b), pieces joined in one outline, cannot be proven; route (a) is done.
- Front (F.SilkS, the face with pins and wire pads): "P1 +" on the P1 wing, "P4 -" on the P4 wing. Back (B.SilkS, mirrored): P1 and +, P4 and GND, P2 and D-, P3 and D+ (name above the pad, content below). Main board bottom face: W1 +, W2 D-, W7 TCH, W3 D+, W4 GND, one per hole row.
- Height 1.0 mm, stroke 0.15 mm = the maker's smallest legible text ("Minimum text height | 40 mil (1.0mm)", "Minimum Line Width | >=0.15mm" in design/ecad/case/pcb/evidence/capab_jlc.html.txt). Character widths 0.55 mm (wing fronts) and 0.60 mm (others).
- Not done, with the measured limit: "P4 GND" in one line on the wing front needs 3.35 mm, the wing is 2.55 mm wide (E measure_ink.log); the inner piece front has no free place for a 1.0 mm text (the nearest spots are on the wings, E search_pins_F_inner.log), so P2 and P3 are marked on the back only; on the main board top face the nearest free place for "W1 +" is 2.38 mm away but on the row between the holes W1 and W2, and for the other four labels it is 5.06 to 5.60 mm away (E search_main_F_final.log), so its labels are on the bottom face. White silkscreen colour is my assumption (no file states it).
- Rules check (kicad-cli pcb drc --severity-all --all-track-errors, run by check_boards.py with each board in its own folder; E s4_check_boards.log): "ok   PCB1: rules check 0 violations, 0 unconnected items (kicad-cli pcb drc --severity-all --all-track-errors)" and "ok   PCB2: rules check 0 violations, 0 unconnected items (kicad-cli pcb drc --severity-all --all-track-errors)".
- Copper, pads, nets, outline unchanged: PCB2 10 pads, 7 tracks and vias, 1 zone, 12 outline lines before and after; PCB1 306 pads, 737 tracks and vias, 5 zones, 8 outline lines before and after, all identical (E dump_after.log). Every copper, mask, paste, outline, drill and job file of fab/ equals its earlier copy except the creation-date lines; only case_pins-F_Silkscreen.gbr, case_pins-B_Silkscreen.gbr and case_main-B_Silkscreen.gbr differ (E compare_fab.log). The Gerber files are not byte-equal because KiCad writes the creation time in each header; with those lines removed they are equal.

## m4 netlist
- make_netlist.py now writes WP1, WP2, WP3, WP4, WP7 (PCB2 wire pads) with the net of W1, W2, W3, W4, W7: netlist 284 rows, 94 parts, 61 nets (before 279, 89, 61; E s4_make_netlist.log). The netlist describes both boards (PCB2 holds P1 to P4, E1 and the wire ends), so the rows sit with the other ringlink parts.
- Pads with a net but no netlist row: 5 before (E parity_before.log), 0 on both boards after (E parity_after.log).
- check_netlist.py (through run_all.sh): last lines of design/ecad/case/evidence/check_marks_s4.log: "RESULT PASS netlist netlist.csv", "check_netlist exit 0"; ERC " ** ERC messages: 0  Errors 0  Warnings 0".
- check_boards.py: `RESULT PASS check_boards case_main.kicad_pcb case_pins.kicad_pcb`, exit 0 (E s4_check_boards.log, E s4_check_boards.exit). Same command on the base: `RESULT PASS check_boards case_main.kicad_pcb case_pins.kicad_pcb` (E base_check_boards.log). Red run of the new check on the boards before the marks: `RESULT FAIL 11 check_boards case_main.kicad_pcb case_pins.kicad_pcb` (E red_check_boards.log). Broken copies (E broken/exits.txt, a log each): wrongnet, outside, notrack, nopart (rebuilt from the new main board) and nomarks_main, nomarks_pins, swapped_pins, small_pins all exit 1; the good boards exit 0.

## m3 order
Written in board-notes.md "Wiring table (replaces part f)": pin board end first (the pads are in the 0.7 mm recess behind the pin holder wall, unreachable after the board is pressed in: case-architecture.md lines 17, 236, 238), order W4, W2, W3, W7, W1 with the reason, W2 and W3 twisted about one turn per 5 mm (lead's instruction: no source states turns), colours from lead-decisions.md line 68, cut 15.6 / 16.3 / 16.3 / 15.6 / 15.9 mm from the table, strip 2.5 mm per end (the table's allowance), continuity from each spring pin and from E1 to the main board pad, no continuity between any two of the five (10 pairs; about 147 kohm W1 to W4 is normal through R12 and R13). Values marked "(lead)" in that section are my practice written as the lead's instruction to confirm.

## Fabrication files made again
`export_fab.sh pins`, `export_fab.sh main`, `make_bom.py`: all exit 0 (E fab_exits.txt). 58 files with sizes in E fab_sizes_final.txt (for example case_pins-F_Silkscreen.gbr 14770 bytes, case_pins-B_Silkscreen.gbr 10421, case_main-B_Silkscreen.gbr 35688; the same list of files as before, E compare_fab.log "same file list"). fab/ size 3256 kB (du -sk).
design/case/check_case_docs.py: last line `RESULT PASS (0 findings)` (E s4_check_case_docs.log, exit 0; base: E base_check_case_docs.log, same line).

## Looks that are not the final result
- First broken-copy run: three of the new broken copies were not written because my script reused one KiCad board object (E broken_first_run_note.txt); fixed by one process per copy, run again.
- The first searches used a 0.05 mm larger distance to pads (0.20 mm) and a vias-as-obstacles test; E search_main_B.log, search_main_F.log, search_main_R_F.log are from those earlier parameters and are not cited as results; the final placement is E search_pins_F_wings_w0.55.log, search_pins_B.log, search_main_R_B.log, and the top-face limit is E search_main_F_final.log. The pins front text first fitted the P1 wing only because the first edge test let the text cross the 0.10 mm gap to the next piece; the test was corrected and rerun.
- Runs s1, s2 and s3 of run_final.sh (E s1_*, s2_*, s3_*) came before the last change of board-notes.md (the top-face search wording); s4 is the run after it and the one cited. All four runs ended with the same last lines.
- check_boards.py writes its temporary rules reports into ROOT/design/ecad/case/pcb/evidence/ (check_drc_*.json and .log); they are left there.
- Not verified: soldering order and marks were not built or tested on a real board; the face on which the PCB1 joint is made is not fixed by any file.

questions_for_owner: none

RESULT: done, 5 wire pads in the netlist, marks on both case boards (front wings and back; main board bottom face), soldering order in board-notes.md; both boards 0 violations and 0 unconnected, check_boards, check_netlist and check_case_docs pass.
