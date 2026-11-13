# Band ribbons: paste layers and land numbers (process.md changes C1, C2, C13, C4)

Written 2026-11-13 from 13:46:48 (first `date`) by the builder of this job. Project root ROOT = .. Folder ROOT/design/ecad/band (below: BAND). Work folder and every log: BAND/band-paste-work (below: WORK); checklist WORK/CHECKLIST.md. Every change goes through the generator: make_lib.py (library), build_band.py (14 boards), make_fab.py (new: fab outputs).

## What changed

| Change | How | Source of each value |
|---|---|---|
| C1 FLEX1 paste | make_lib.py: the two switch footprints carry F.Paste on every land, 1:1. 12 openings 0.55 x 0.55 per board (SW1, SW3, SW4, SW5: lands 3 and 4; SW2: lands 1 to 4), on the switch face F. The 8 unsoldered terminals have no land and no opening. | process.md P8 C1 ("paste openings 1:1 on the 12 switch lands (0.55 x 0.55)"); band-interface.md section 4 (which terminals are soldered) |
| C2 FLEX2 paste | build_band.py: four round openings per disc land, 0.58 mm, centred 0.49 mm from the land centre on the diagonals, drawn as filled circles on layer B.Paste (board graphics, not pads; the Gerber draws each as arcs round its centre with a 0.29 mm round pen). 16 per board. Gap to the via at the land centre 0.05 mm (WORK/logs/count_paste5.log). | process.md P8 C2 and P2 row "Band ribbon FLEX2" |
| C13 drawings | build_band.py: on each drawing a detail of the board end, 4 times the ribbon view, each land as a box with its number and net, and a legend `LAND n = NET (name, row)`; FLEX1 marks `1 +: VMOT (red)` and `2 -: GND (blue)` at the motor lands; FLEX2 names `P+ tab: VBAT`, `NTC tab: NTC`, `P- tab: GND` at the cell tab lands. | band-interface.md section 2 (numbers, nets), 5 (tabs), 6 (motor + land 1, red, nearer the slot) |
| Board-side lands (lead's addition, its own item) | make_lib.py: J_BAND_A_BOARD (8 lands) and J_BAND_B_BOARD (7 lands) get one F.Paste opening per land, 0.30 x 0.44, centred, drawn as a filled rectangle in the footprint, not as a pad. The pads keep F.Cu and F.Mask and the counts stay 8 and 7. Read back: 15 openings, each centred on its land (jband_paste_test.log); the Gerber of a test board holding both footprints has 15 regions (jband/jband-F_Paste.gbr, `G36` count 15). | design/mfg/assembly/hotbar-joint.md section 1 (aperture 0.55 x 0.03 / (0.50 x t)) with t = 0.075 mm, process.md P2 row "Ring, parts face" |
| C4 (no copper) | make_fab.py writes fab/flexK-usN/flexK-usN-fab-notes.txt; the drawing has the same note: rails 5 mm; three 1 mm fiducials on the paste face (FLEX1 F, FLEX2 B) on the rails, centred 3.85 mm from the panel edges, not in a line. | process.md P7 (quoting JL :102 "1 mm fiducials centered at 3.85 mm from the panel edges") |

Text height: 0.3 mm on the board for the legend, nets and marks; 0.6 mm for the land numbers in the detail. On the A4 drawing (autoscaled) the 0.3 mm text measures 1.77 to 2.12 mm and the land numbers 3.53 to 4.24 mm (scale 5.89 to 7.06 : 1, read from the PDF by WORK/text_scale.py, WORK/logs/text_scale5.log, same values as text_scale4.log: logs/text_scale-4v5.log is empty).

## Files changed (all in BAND)

- make_lib.py (paste on the switch footprints and on the J_BAND board footprints, descriptions); OpenRingBand.pretty: Alps_SKTAAAE010_4pad, Alps_SKTAAAE010_pads34, J_BAND_A_BOARD, J_BAND_B_BOARD changed; the other 6 footprint files are the same apart from uuid lines (WORK/logs/lib6.log).
- build_band.py (paste circles on the discs, drawing labels, detail, notes on the drawing).
- make_fab.py (new).
- flex1-us7 to flex1-us13 and flex2-us7 to flex2-us13: .kicad_pcb (rebuilt; .kicad_pro and .kicad_dru rewritten with the same content), -drc.rpt (rewritten by check_band.py).
- fab/: the 14 drawings; per board folder the Gerber, drill and job files (rewritten), the new paste Gerber (flex1-usN-F_Paste.gbr or flex2-usN-B_Paste.gbr) and the new flexK-usN-fab-notes.txt.
- evidence/build_rows.json (rewritten, same bytes: WORK/logs/build_rows-cmp.log) and evidence/make_fab.log (new).
- band-notes.md: lines 18, 43 and 65 edited inside the line; new section "Change 2026-11-13: paste layers and land numbers" inserted before the last line.
- band-interface.md: lines 55, 58, 91, 106, 116, 123, 137 and 141 extended inside the line (no line moved; 148 lines before and after; every quote other files take from them is kept).
- band-paste-notes.md (this file) and band-paste-work/ (new).

## Checks

Final run (boards of build5.log). Logs in WORK/logs.

| Bar | Command and log | Last line |
|---|---|---|
| 1a generator is the source | build_band.py run on the committed generator, then dump_boards.py and compare_dumps.py against the boards as found (rebuild0.log, compare-rebuild0.log) | `RESULT: PASS boards compared 14, boards with a not-allowed difference 0, mode identical` |
| 1a same, file text | sorted lines without uuid lines (sortedlines-rebuild0.log) | `RESULT: boards whose sorted non-uuid lines differ: 0 of 14` |
| 1a fab script | make_fab.py on the boards as found, against the old fab folder: Gerber geometry and drill files the same (compare-fab-repro3.log); drawings 1 to 14 pixels of 1170 x 827 differ (compare-fab-repro2.log, anti-aliasing) | `RESULT: boards 14, Gerber/drill/job files differing 0` |
| 1b only paste and text changed | compare_dumps.py before against final, paste and drawing text allowed, copper classes and pads must be equal; no pad added (compare-after5.log) | `RESULT: PASS boards compared 14, boards with a not-allowed difference 0, mode paste-and-text allowed` |
| 1b fab | Gerber geometry and drill files before against final (compare-fab-final5.log): 98 files the same; job files differ only by the paste layer entry | `RESULT: boards 14, Gerber/drill/job files differing 0` |
| 1 control | one track moved 0.1 mm (ctl5-compare-copper.log) | `RESULT: FAIL boards compared 14, boards with a not-allowed difference 1, mode paste-and-text allowed` |
| 2 KiCad rules | kicad-cli pcb drc --severity-all --all-track-errors, run in BAND, each board (drc5.log): 14 of 14 `Found 0 DRC violations`, `Found 0 unconnected pads` | `flex2-us13 exit 0 ** Found 0 DRC violations ** ** Found 0 unconnected pads ** ** Found 0 Footprint errors **` |
| 2 band check | run_kipy.sh check_band.py after the last library change (check_band6.log, exit 0; 14 lines `kicad-cli drc: violations 0, unconnected 0`; mating worst offset 0.0000 mm on 14) | `RESULT: PASS boards checked 14` |
| wiring (lead's added bar) | `design/.venv/bin/python design/wiring/check_wiring.py --require-complete` from ROOT, after the last change (check_wiring6.log, exit 0, 0 FAIL lines, `COMPLETE 66 of 66 conductors (100 percent)`; it writes its rules check reports in the wiring work folder) | `RESULT PASS lines 67 (66 conductors, 1 sensing gap), drawn and routed 25, specified and landed 41, drawn, not routed 0, stated in text only 1, not drawn 0, complete 66 of 66 conductors (100 percent), problems 0` |
| 3 paste | count_paste.py reads each paste Gerber (count_paste5.log): FLEX1 12 flashes, FLEX2 16 closed circles of 0.58 mm (4 per disc land), each on its land | `RESULT: PASS paste Gerbers checked 14, failing 0` |
| 3 control | SW2 land 1 without paste: 11 (ctl5-count-paste1.log); one disc circle removed: 15 (ctl5-count-paste2.log) | `RESULT: FAIL paste Gerbers checked 1, failing 1` (both) |
| 4 drawings | check_drawings.py, pairs parsed from band-interface.md section 2 (check_drawings5.log): FLEX1 8 of 8, FLEX2 7 of 7 at every size, plus the motor and tab marks | `RESULT: PASS drawings checked 14, failing 0` |
| 4 control | copy without the text `LAND 7 = VMOT` (ctl5-check-drawing.log): 7 of 8 | `RESULT: FAIL drawings checked 1, failing 1` |
| J_BAND paste Gerber (lead's ruling, option b) | test board with both new footprints, F.Paste Gerber regions measured (jband_region_sizes.log) | `RESULT: PASS regions 15, all 0.300 x 0.440: True` |
| ring footprints | ring/pcb/check_footprints.py with the final library (ring_check_footprints_after6.log): only C90 and R73 fail, as on the base; with the board helper's pad form the J_BAND lines fail too (ring_check_footprints_helperlib.log) | `RESULT FAIL 2 footprints netlist netlist.csv library OpenRing.pretty` |
| old audit | audit_notes.py of the band folder (audit_notes_after2.log) | `claims checked 36, matched 36, no match 0` |

## Findings

1. My first FLEX2 version made the openings as paste-only pads in each CP footprint. design/wiring/check_wiring.py counts every pad of a band board, so the lead's run printed 28 lines `band-pad ... pad CP1: is named by no line`. I replaced the pads with filled circles on B.Paste (no pad added: compare-after5.log has no PAD line added), and the check now passes (table above). The first version's logs (build2 to build4, count_paste4, drc4, check_band4) stay in WORK/logs.
2. The Gerber job files say "BoardThickness": 1.6 (KiCad default; the board stackup gives 0.11 mm finished). Present in the old job files too (before/fab). Not changed: it is a KiCad setting of the boards that this job did not own as a value. Who acts: the lead (set the board thickness in build_band.py) or the order notes.
3. The ring's own footprint check (ring/pcb/check_footprints.py) ends `RESULT FAIL 2 footprints netlist netlist.csv library OpenRing.pretty` with the band library before and after this change (C90 and R73 have no row in footprint-sources.csv): already there, not caused here (WORK/logs/ring_check_footprints_before.log, ring_check_footprints_after.log). Who acts: the ring board owner.
4. The old fab folder was written from an earlier save of the boards (Gerber date 00:30, boards 01:03): aperture numbers and object order differ from a new export, the geometry is the same (compare-fab-repro2.log).
5. To keep WORK under 50 MB the 60 PPM renders made by the pixel compares were listed (logs/ppm-removed-listing.log) and removed; their pixel counts are in the logs. WORK is 10792 KB after that (logs/du2.log).
6. I ran two read-only git commands at 14:04 (log and status of the band folder) before I saw the brief's "You never run git". No git command changed anything; none after.

## Left for the lead

- J_BAND paste form: the lead ruled option (b), filled F.Paste rectangles, no extra pad; that is what make_lib.py delivers. The board helper must refresh its copy of J_BAND_A_BOARD and J_BAND_B_BOARD from BAND/OpenRingBand.pretty so the ring board matches the library.
- band-notes.md: its last line (the old RESULT line) moved from line 140 to line 151; no file cites it by number (WORK/logs/cited-lines.log lists the cited lines of band-notes.md: 49, 61, 71). band-interface.md: no line moved.
- process.md P8 rows C1, C2, C13 and the C4 part for the ribbons, joints rows waiting for them (joint-gaps.md), and review 3 G2 and G7 can now point at: fab/flexK-usN/*-F_Paste.gbr or *-B_Paste.gbr, the drawings, and the fab notes. I did not edit files outside BAND.
- "Three fiducials" is a [CHOICE] of process.md P7 (other option two); the fiducial coverlay opening is left to the panel maker (P7 says no saved document gives it).
- The version I worked on: the band folder as found at 13:46 (the brief names commit ce56ff0b; the repository head I saw was 5e4d9a60, band folder clean). The lead commits.

questions_for_owner: none

RESULT: done, the 14 ribbons carry paste openings (12 per FLEX1, 16 per FLEX2, no pad added), the J_BAND board footprints one opening per land, and the drawings every land's number and net; copper, outline and nets identical, 0 rules violations, check_band.py and check_wiring.py --require-complete pass.
