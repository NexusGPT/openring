# Product wiring list: notes (written step by step)

Project root: . (ROOT). Started 2026-11-13 07:46 CET (`date`, saved in design/wiring/wiring-work/start-time.txt). Work folder: design/wiring/wiring-work/. No git command is run by me.

## How to rebuild (for the lead; run in this order from the project root)

1. `python design/wiring/build_wiring.py` (re-runs itself under KiCad's Python; reads the ring board and design/wiring/ring-case-contact.csv as they are; writes design/wiring/product-wiring.csv)
2. `python design/wiring/check_wiring.py` (consistency; must end RESULT PASS)
3. `python design/wiring/check_wiring.py --require-complete` (exit 0 only when every conductor is complete; prints `COMPLETE <n> of <total> conductors (<percent>)` and each incomplete line with what it waits for)
4. `design/.venv/bin/python design/wiring/wiring-work/make_broken.py` (7 broken copies; last line BROKEN COPIES PASS)
5. `design/.venv/bin/python design/wiring/draw_wiring.py` (product-wiring.svg and .pdf; prints both counts)

## Step 1. Sources read (07:46 to 07:51)

Read: design/wiring/connections.md (all), design/ecad/band/band-interface.md (all), band-notes.md (all), design/wiring/lead-decisions.md (all), design/ecad/case/pcb/board-notes.md (all), screen-cable-study.md sections 1, 2 and 4.3, cell.md (grep of tabs and protection), case-architecture.md (grep of electrode and pins), case sch-notes.md lines 10 to 20; the pad and net lines of flex1-us9 and flex2-us9; the netlist rows of every off-board part.

My reading of the brief, stated so it can be checked:
- The brief names no separate "quality reference to copy"; I use its "Bar" list 1 to 6 as that reference.
- A part pin is counted once. The land on a band circuit or case board that the pin is soldered to is a board pad, not a counted terminal, so a flex trace line (main board land to the far land) and a lead line (part pin to that far land) can both name the same land.
- Where one net on a band circuit has more far terminals than board lands (GND on FLEX1 and FLEX2, BTN_REC at SW2), each extra terminal's line ends at a node "copper of net X on board Y", proven by the copper path in the board file.
- ANT1 is on the main board today (lead-decisions.md row "W2"); its 4 pins get lines (joints R11, R12) with the main board copper as the carrier, outside the "leaves its board" set.
- Question sent to the lead before 07:51 (clock read at 07:51:16 right after): which state a lead, wire, tab, spring pin or bought cable line gets (no board file can hold a wire).

## Step 2. Build script, hand rows, check (07:51 to 08:02)

- design/wiring/build_wiring.py reads the ring and case netlists and parts lists, the 14 band boards, the ring main board (read in place each run), the two case boards, and the text lines it cites. It runs KiCad's rules check on each of these 17 boards into wiring-work/drc/ (json and log per board). On the band boards it builds the copper graph of each net (tracks chained at every touching point, vias, pads) and pairs each J_BAND land with the far pad reached by the shortest copper path; extra far pads get a line that ends at the net's copper ("node"), with the land it reaches named. The pairing must be the same at all 7 sizes.
- First run (wiring-work/build1.log): SW2 pins 2 and 4 and the motor land 2 were "unreached" on FLEX1. Cause, seen in wiring-work/probe/debug_gnd.log: the B.Cu GND star crosses the SW2 ground strap in the middle of both tracks, and the via at the motor land sits on the body of the GND lane; my first graph joined only track ends. Fixed (crossings and via-on-track points); second run wiring-work/build2.log: every far pad reached; J_BAND_A land 6 (MOT-) pairs with the motor land 2, land 8 (GND) with SW4 pin 4, the other switch grounds reach the main board through land 6.
- design/wiring/system-joints.csv: 9 rows typed by hand, each with its sources: R10 (BT1 pin 1 tab P+, BT1 pin 2 tab P-, RT1 pin 1 tab NTC), R8 (RT1 pin 2 to tab P- on the PRT1 board), R15 (CP1 to CP4 against spring pins P1 to P4), R16 (band metal to E1: no conductor).
- The disk was full once (ENOSPC on an edit, reported to the lead); `date` read 07:58:29 and `df` then showed 1.9 GB free (shown on screen, not saved to a file), and the work went on.
- design/wiring/check_wiring.py: run 3 (wiring-work/check3.log) ends `RESULT PASS lines 68, drawn and routed 44, drawn, not routed 15, stated in text only 9, not drawn 0, problems 0`. 91 terminals required (ring 75: the band parts, DISP1 and J1; case 16: BT1, TH1, W1 to W7, P1 to P4, E1), 91 in exactly one line.
- Broken copies (wiring-work/make_broken.py, log wiring-work/broken-run1.log): 5 copies, each exit 1 and failing only its named check (terminal-twice, terminal-missing, ends-disagree, lead-length, proof-text); last line `BROKEN COPIES PASS: 5 copies, each fails its named check only`.
- Same output twice: build run 3 and run 4 give byte-equal files (wiring-work/cmp-run3-run4.log empty, cmp exit 0; sha256 f80cde51... for both).

## Step 3. connections.md (08:04 to 08:05)

- Before copy: wiring-work/connections.before.md (sha256 da7560ab...). Script: wiring-work/apply_connections.py (log wiring-work/apply_connections.log: `cells changed: 21 of 21`); diff: wiring-work/connections.diff.
- Part 1: only the last cell ("Drawn?") of 21 rows changed (R14 kept: no joint); every Part 1 row still has 8 cells (wiring-work/connections-fieldcount.log: 22 rows before and 22 after, each 8). A dated note is line 3. The line "Count: 21 joints (R1 to R13, R15, R16 and C1 to C6; R14 and the module antenna are not joints)." is kept; only its second sentence changed ("3 are not drawn: R10, R15, R16." now says that on 13 November none is not drawn and R10, R15, R16 are stated in text only). No joint added or removed.
- Parts 2 to 6: one dated line each at the top ("this part describes the files of 12 November ..."), nothing else changed. The note times read 08:04 (clock 08:04:56; the script first wrote 08:05 and the 6 notes were set to 08:04, wiring-work/fix-time.log `replaced 6`).
- Correction found while writing the cells: `grep -c PRT1` gives 1 in design/ecad/ring/parts.csv (BT1's footprint OpenRingBand:PRT1_Tabs), 0 in netlist.csv and ring.kicad_pcb (wiring-work/verify-connections.log). The two R10 rows of system-joints.csv said "PRT1 is in no netlist, parts list or board file"; they now say it is not a part of the netlist or the parts list, named there only in BT1's footprint, and not on the main board.

## Step 4. Final runs (08:06:09 to 08:06:51, wiring-work/final-run.time)

- `python design/wiring/build_wiring.py` twice (wiring-work/build5.log, build6.log, exit 0 each), byte compare `cmp` exit 0 (wiring-work/cmp-run5-run6.log empty).
- `python design/wiring/check_wiring.py` (wiring-work/check-final.log), exit 0, counts printed: terminals required 91, in exactly one line 91; per joint C1 1, C2 1, C3 2, C5 5, R3 10, R4 10, R5 4, R6 2, R7 1, R8 1, R9 4, R10 3, R11 1, R12 3, R13 15, R15 4, R16 1; lines naming a joint at an end: C4 4, R1 10, R10 1, R2 7, R6 2, R7 1, R9 4. Last line, verbatim:
  `RESULT PASS lines 68, drawn and routed 44, drawn, not routed 15, stated in text only 9, not drawn 0, problems 0`
- Broken copies on the final csv (wiring-work/broken-final.log, copies and logs in wiring-work/broken/): terminal_twice fails FAIL[terminal-twice] (2 lines), terminal_missing FAIL[terminal-missing] (1), ends_disagree FAIL[ends-disagree] (1), lead_no_length FAIL[lead-length] (1), proof_wrong_line FAIL[proof-text] (1); each exit 1 with no other check failing; last line `BROKEN COPIES PASS: 5 copies, each fails its named check only`.
- Lines by carrier kind and state (wiring-work/kind-state.log): copper drawn and routed 25 (21 band circuit lines, 4 antenna lines on the main board), copper stated in text only 1 (R8, PRT1 board), inside the part 8, lead 6 (motor 2, case cell 2, TH1 2), wire 5, part cable 15 (screen, drawn, not routed), spring pin 4, tab 3, none 1 (R16).
- The ring main board was read in place (file time 07:52 at the final build, wiring-work/final-facts.log); its rules check at 08:06:35 found 5 violations and 9 unconnected items; two of them are J1 pads 8 (LCD_RST) and 11 (LCD_DCX), column main_board_land of W053 and W042.

## Step 5. Drawing

- `design/.venv/bin/python design/wiring/draw_wiring.py` (wiring-work/draw-final.log): `csv lines: 68`, `conductors drawn: 68`. It writes product-wiring.svg and product-wiring.pdf, A3 landscape 420 x 297 mm, from the csv only.
- Pictures without a browser: `pdftoppm -r 110` of the PDF (wiring-work/pictures/final-pdf-1.png) and `rsvg-convert` of the SVG (wiring-work/pictures/final-svg.png); earlier looks: draw1-pdf-1.png, draw1-svg.png (first layout, used only 190 of 297 mm), draw2-pdf-1.png (block labels with a stray "|"), both fixed before the final.
- What I see in final-svg.png: two columns of panels, one per joint, titled with the joint, its "ends also in" joints and the line count. In each panel the end A blocks are on the left (ring main board J_BAND_A, J_BAND_B, J1 side, motor M1, cell BT1, case pin board) and the end B blocks on the right (FLEX1 with SW1 to SW5 and M1, FLEX2 with PRT1 and CP1 to CP4, case boards). Each conductor is one horizontal line with "REF.pin SIGNAL" at both ends and its id and carrier under it (for example "W001 FLEX1 11.577-13.519 mm", "W023 red lead wire AWG32 of the motor, cut 1.12-1.39 mm", "W064 wire 30 AWG, cut 15.6 mm"). Solid black lines: R3, R4, R5, R6, R7, R9, R11, R12, C1, C2, C3, C5. Blue dashed: the 15 screen lines of R13. Orange dash-dot: R8, R10, R15, R16. No red line. The text is about 2.1 mm high on A3; the smallest (carrier labels) about 1.8 mm.

## Step 6. Evidence against, and what it means

- Copper lengths against band-interface.md section 6 (US 13): VMOT 6.90 mm there, 6.825 here (land 7 to motor land 1); motor GND 10.30 there, 8.855 here (land 6 to motor land 2); VBAT 6.74 there, 6.601 here; cell GND 7.64 there, 7.969 here. My value is the shortest copper path pad centre to pad centre in the board file; band_calc.log's method was not read, so the cause of the differences is not known. The csv states only its own measure (columns copper_mm_us7 to us13). Not a blocker of any line.
- The pairing of a land with a far pad is my rule (shortest copper path). On FLEX2 it gives land 2 (CELL-) to PRT1 land 2 and land 7 (GND) to CP4, which matches the land names of band-interface.md section 2; on FLEX1 land 6 (MOT-) to the motor land 2, which matches section 6; land 8 (GND) gets SW4 pin 4 (band-notes.md section g item 3 describes the switch ground lane reaching land 6 by a stub and land 8 by a strap; it names no switch per land).
- State words for lead, wire, tab, pin and cable lines: my working rule (Step 1) was asked of the lead and not answered by the time of this note. Under the strict reading the 11 lead and wire lines that are `drawn and routed` would read `drawn, not routed` (`WIRING_STRICT=1` switches it in build_wiring.py); the check passes either way, because neither word is `not drawn`.

## Step 7. Lead's ruling and the ring board's round 3 (08:10 to 08:17)

- Ruling of the lead (message received after the first report): a new state `specified and landed` for a carrier that is a lead, wire, tab, spring pin or a part's own cable (every end pad or pin drawn with its net, no open connection at that pad, carrier fully specified: colour or marking, gauge or model, cut length per size or "not size dependent", which end is soldered first where the files say). A line is complete only in `drawn and routed` (copper) or `specified and landed`. The screen cable gets one line per contact that carries a signal.
- build_wiring.py (copy before the change: wiring-work/build_wiring.before-ruling.py; patch wiring-work/patch_ruling.py, log `patched 10`): new columns carrier_marking, carrier_gauge_or_model, solder_first, spec_missing; function spec_state; the WIRING_STRICT switch is gone. The screen lines cite the maker drawing's contact numbers (screen-cable-study.md line 48, sch-notes.md line 309) and the cable's thickness and pitch (lines 46, 49); DISP1 pin 3 and J1 pin 3 (MTP, no net) have no line.
- check_wiring.py (copy: wiring-work/check_wiring.before-ruling.py; patch wiring-work/patch_check.py, `patched 7`): new checks `incomplete` (a line not complete) and `state-kind` (`drawn and routed` on a non-copper carrier, or `specified and landed` on copper or without its specification); the terminal set leaves out pins with no net and prints them; the counts line prints the share complete.
- The build script parsed after the 07:58 disk-full failure of one edit: it ran at 07:58 onward many times, and `py_compile` of the three scripts gave exit 0 at the start of this step (wiring-work/compile-0816.log, empty).
- Two builds on the same ring board file (time 08:08:50) differed (wiring-work/diff-fields-run8-run9.log): KiCad's list of unconnected items named different pads of the large nets in the two runs. The per-pad state is now taken from KiCad's copper connectivity (a pad is open when its copper cluster holds at most half of the pads of its net); after that two builds are byte-equal (wiring-work/cmp-run10-run11.log and cmp-run12-run13.log, empty, cmp exit 0).
- The ring board was rewritten at 08:08:50 for round 3: J1 now stands on B.Cu (the screen face) and the board is unrouted (rules check at 08:11:39: 133 violations, 237 unconnected items, wiring-work/drc json of that build). So the 14 screen lines and ANT1 pad 4 come out `drawn, not routed`, and the J_BAND lands show "open on main board" in the column main_board_land (that column is information; the band lines' carrier is the band circuit, which is routed).
- connections.md second pass (copy before: wiring-work/connections.before-ruling.md; script wiring-work/apply_connections2.py, `cells changed: 8 of 8`; diff wiring-work/connections2.diff; 22 rows with 8 cells, wiring-work/connections-fieldcount2.log): cells R5, R11, R12, R13, C1, C2, C3, C5 and a second dated note (08:12).

- A shell slip of mine at 08:17 (an empty variable before a redirection) left a cat waiting on input; I stopped that process (pid 31098, mine) with kill; the notes tail was then written as intended.

## Step 8. Final runs (08:16:29 to 08:16:53, wiring-work/final3-run.time)

- Disk before: 25 GB free (wiring-work/final3-run.time first line).
- Build twice, exit 0 each, cmp exit 0. Check exit 1 (wiring-work/check-final3.log): 89 terminals with a net required, 89 in exactly one line; no-connect pins not required: 2 (DISP1.3, J1.3). Last line, verbatim:
  `RESULT FAIL lines 67, drawn and routed 24, specified and landed 10, drawn, not routed 24, stated in text only 9, not drawn 0, complete 34 of 67 (51 percent), problems 33 (checks failing: incomplete)`
- The 33 lines that fail `incomplete`, with what is missing:
  - W028 (R8), W033, W034, W035 (R10): stated in text only; PRT1 and its board copper are drawn in no file.
  - W039 (R12, ANT1 pad 4 GND): main board copper not joined (round 3 routing).
  - W040 to W053 (R13, 14 screen contacts): J1 pads not joined on the main board (round 3 routing); cable specification complete.
  - W054 to W057 (R15): pairing ring pad to case pin stated in text only.
  - W058 (R16): no conductor by design; stated in text only.
  - W059, W060 (C1, C2, case cell leads): gauge of the cell lead in no file.
  - W061, W062 (C3, TH1 leads): marking and gauge of the thermistor leads in no file.
  - W063 to W067 (C5, case wires): colour or marking of the wire in no file (30 AWG and cut lengths are given).
- Broken copies (wiring-work/broken-final4.log): the good csv fails only `incomplete` (33 lines); each of 6 copies exits 1 and adds new FAIL lines of its own check only: terminal-twice (2), terminal-missing (1), ends-disagree (1), lead-length (1, on wire W063; a first try on the motor lead also tripped state-kind, which is correct but not "only its check", wiring-work/broken-final3.log), proof-text (1), state-kind (1). Last line `BROKEN COPIES PASS: 6 copies, each fails its named check with new FAIL lines and no other new failure`.
- Drawing (wiring-work/draw-final3.log): `csv lines: 67`, `conductors drawn: 67`. Seen in wiring-work/pictures/final3-svg.png: the legend now has five styles; green solid lines for the 8 switch "inside the part" lines and the 2 motor leads; blue dashed for R13 (14 lines), ANT1 pad 4, C1, C2, C3 and C5; orange dash-dot for R8, R10, R15, R16; black for the band circuit and antenna copper; no red line.

## Step 9. Third pass (lead's four changes, 08:19 to 08:27)

1. States: one rule only. `drawn and routed` for copper; `specified and landed` for leads, wires, tabs, spring pins and a part's own cable (every end in a board file or netlist with its net, the pad joined to its net, the specification cited: marking, gauge or pin model, cut length per size or "not size dependent"). No WIRING_STRICT switch exists in build_wiring.py (removed in Step 7). The open state of a pad is KiCad's copper connectivity (Step 7), which the check now reads too.
2. Completeness: check_wiring.py prints `COMPLETE <n> of <total> conductors (<percent>)` before the RESULT line. Without a flag the check is about consistency (incomplete lines counted, not failed); `--require-complete` adds FAIL[incomplete] per line with the new csv column waits_for (system-joints.csv got the same column for its 8 conductor rows). New check `complete-open`: a line marked complete whose board pad is not joined fails. New broken copy complete_but_open (screen contact W040 marked `specified and landed` while J1 pad 1 is open).
3. R16 (W058, carrier_kind none) stays in the csv and is counted apart: the check prints "sensing gaps, no conductor ...: 1 (W058 R16)" and the percent is of the 66 conductors; the drawing puts it in its own panel "SENSING GAP, NO CONDUCTOR" with a grey dotted line and prints the two counts apart.
4. Copper lengths against band-interface.md section 6, at US 13 (traces: wiring-work/len_cause.log, len_cause2.log to len_cause4.log, script wiring-work/probe/len_cause.py):
   - How band_calc.py measures (design/ecad/band/band_calc.py, read, not changed): it reads no track. VMOT = m1 - U_NEAR (motor land 1 position along the tail minus the near land row, U_NEAR 1.375); motor GND = (m1 + 1.0 - U_FAR) + 1.5 (motor land 2 minus the far row U_FAR 0.475, plus a fixed 1.5 commented "with the strap"); VBAT = PRT1 land 1 position minus U_FAR; cell GND = VBAT + 0.9. These are straight distances along the tail axis between land centres, with two fixed allowances.
   - My first measure (in the csv until Step 8) let the path jump at no cost wherever two copper shapes overlap without their centre lines meeting (a jog between two 0.20 tracks, a via whose copper covers a track end), so it was too short. Fixed in build_wiring.py: such a step now counts its centre-to-centre distance. The csv now holds the centre-line length of the routed copper from land centre to land centre.
   - VMOT: board copper 6.931 (F.Cu 0.475 from land 7, a 0.106 step, then 6.350 along the B.Cu line to the motor land 1 centre). band_calc 6.90 = the straight distance between the two land centres (6.900); the copper is 0.031 longer because the line steps 0.205 across (Y 80.005 to 79.800).
   - Motor GND: board copper 8.980 (F.Cu stub 0.450 from land 6 to its via, 0.125, a 0.615 diagonal, 7.790 along the B.Cu lane to the via in motor land 2). band_calc 10.30 = straight distance 8.80 plus its fixed 1.5 for a path through the strap to land 8; the board's motor ground does not pass land 8 (path printed in len_cause4.log), so 10.30 is 1.32 too long.
   - VBAT: board copper 6.799 (0.450 + 0.275 + a 0.198 jog + 5.876). band_calc 6.74 = straight distance 6.741; the copper is 0.058 longer because of the 0.14 mm jog in Y.
   - Cell GND: board copper 8.037 (0.450 + 0.275 + 0.460 diagonal + 0.235 + 5.956 + 0.662 diagonal to PRT1 land 2). band_calc 7.64 = its VBAT figure plus a fixed 0.9; the straight distance between the land centres is 7.601 and the lane runs 0.33 mm off the land row with two diagonals, so the copper is 0.40 longer than 7.64.
   - So for all four the csv's number describes the copper in the board file; band_calc's numbers are axis distances with allowances. Its voltage drops therefore use 10.30 (too long, safe side) for the motor ground and 7.64 (0.40 short) for the cell ground. Nothing in design/ecad/band was changed.

## Step 10. Final runs of the third pass (08:26:05 to 08:26:40, wiring-work/final5-run.time)

- Disk: 24 GB free (first line of final5-run.time). Ring board file time 08:08:50 (unchanged since round 3 began).
- Build twice, exit 0, cmp exit 0 (wiring-work/cmp-run16-run17.log empty).
- `python check_wiring.py` (wiring-work/check-final5.log), exit 0. Its last two lines, verbatim:
  `COMPLETE 34 of 66 conductors (52 percent)`
  `RESULT PASS lines 67 (66 conductors, 1 sensing gap), drawn and routed 24, specified and landed 10, drawn, not routed 24, stated in text only 9, not drawn 0, complete 34 of 66 conductors (52 percent), problems 0`
- `python check_wiring.py --require-complete` (wiring-work/check-final5-require.log), exit 1, 32 FAIL[incomplete] lines, each with what it waits for; last line verbatim:
  `RESULT FAIL lines 67 (66 conductors, 1 sensing gap), drawn and routed 24, specified and landed 10, drawn, not routed 24, stated in text only 9, not drawn 0, complete 34 of 66 conductors (52 percent), problems 32 (checks failing: incomplete)`
- Broken copies (wiring-work/broken-final6.log): the good csv passes; 7 copies each exit 1 with new FAIL lines of their own check only (terminal-twice, terminal-missing, ends-disagree, lead-length, proof-text, state-kind, complete-open); last line `BROKEN COPIES PASS: 7 copies, each fails its named check with new FAIL lines and no other new failure`.
- Drawing (wiring-work/draw-final5.log): `csv lines: 67 = 66 conductors + 1 sensing gap`, `conductors drawn: 66 ; sensing gaps drawn apart: 1`. Seen in wiring-work/pictures/final5-svg.png: as in Step 8, plus the R16 line moved to its own grey dotted panel at the foot of the right column; the band copper labels show the new lengths (for example W021 7.786-8.980 mm, W022 5.737-6.931 mm).

## Step 11. Fourth pass: case lead and wire specifications (08:27 to 08:30)

- The lead added three rows to design/wiring/lead-decisions.md (case wires W1 to W4 and W7: colour; case cell BT1 leads; case thermistor TH1 leads); maker facts in design/case/lead-specs.md. build_wiring.py (copy before: wiring-work/build_wiring.before-pass4.py; patch wiring-work/patch_pass4.py, `patched 3`) finds those rows by pattern and cites the matched text as carrier proof: wires get their colour (W1 red, W2 white, W3 green, W4 black, W7 yellow) and "30 AWG stranded hook-up wire"; the cell leads get "DNK852338 own lead as delivered (no gauge stated by the maker; polarity measured before cutting)" with red (+) and black (-); TH1's leads get "bare, no polarity" and "Semitec 103AT-2 own lead as delivered (0.5 mm tin plated 42 alloy)", soldered either way round, joint 5 mm or more from the bead (lead-specs.md line 35).
- Ring board file time: 08:08:50 before and after the final runs (wiring-work/final6-run.time); the lead says another helper is rerouting it; the build read the file as it was.
- Final runs 08:28:47 to 08:29:16 (wiring-work/final6-run.time): build twice, exit 0, cmp exit 0. `python check_wiring.py` (wiring-work/check-final6.log) exit 0; last two lines, verbatim:
  `COMPLETE 43 of 66 conductors (65 percent)`
  `RESULT PASS lines 67 (66 conductors, 1 sensing gap), drawn and routed 24, specified and landed 19, drawn, not routed 15, stated in text only 9, not drawn 0, complete 43 of 66 conductors (65 percent), problems 0`
- `python check_wiring.py --require-complete` (wiring-work/check-final6-require.log) exit 1, 23 FAIL[incomplete] lines (W028, W033 to W035, W039 to W057), last line verbatim:
  `RESULT FAIL lines 67 (66 conductors, 1 sensing gap), drawn and routed 24, specified and landed 19, drawn, not routed 15, stated in text only 9, not drawn 0, complete 43 of 66 conductors (65 percent), problems 23 (checks failing: incomplete)`
- Broken copies: the first run (wiring-work/broken-final7.log) failed my own rule for one copy: the lead-length copy blanked a length on wire W063, which is now complete, so state-kind fired too. The copy now also sets that line `drawn, not routed` so only the length is wrong; rerun wiring-work/broken-final8.log: 7 copies, each only its check, last line `BROKEN COPIES PASS: 7 copies, each fails its named check with new FAIL lines and no other new failure`.
- Drawing (wiring-work/draw-final6.log): `csv lines: 67 = 66 conductors + 1 sensing gap`, `conductors drawn: 66 ; sensing gaps drawn apart: 1`. In wiring-work/pictures/final6-svg.png the C1, C2, C3 and C5 lines are now solid green; the rest as in Step 10.
- connections.md (copy before: wiring-work/connections.before-pass4.md; wiring-work/apply_connections3.py, `cells changed: 4`; 22 rows with 8 cells, wiring-work/connections-fieldcount3.log): cells C1, C2, C3, C5 and a third dated note (08:29).

## Step 12. Fifth pass: cell pack and pad-to-pin rules (08:31 to 08:35)

- Lead's ruling 08:31: BT1 + PRT1 + RT1 is one purchased part. build_wiring.py (copy before: wiring-work/build_wiring.before-pass5.py; patch wiring-work/patch_pass5.py) now builds the R10 tab lines (BT1 pin 1, BT1 pin 2, RT1 pin 1 to FLEX2 lands PRT1 1, 2, 3) and the R8 line (RT1 pin 2, `inside the part`) from band-interface.md section 5 (lines 110 to 117 cited by pattern), and the four R15 pad-to-pin lines from the netlists, the board files, case-architecture.md (pin model, soldering) and design/case/pin-travel.md line 16 (maker working-height range). These 8 rows left system-joints.csv (copy before: wiring-work/system-joints.before-pass5.csv; wiring-work/sj-trim.log `kept 1 of 9`): only R16 stays typed by hand.
- R15 rule: complete only when design/wiring/ring-case-contact.csv pairs the pad with the pin at all 7 sizes and every in_range is yes, both ends drawn with their nets, the maker range cited. The file did not exist at the final build (`ls` in wiring-work/final7-run.time), so the 4 lines are `stated in text only` with that reason. The column names of that file are not known to me; my reader accepts pad / ring_pad, pin / case_pin, us / size / ring_size and in_range; any other naming leaves the lines incomplete with "columns not understood", never complete. Tested on two made-up fixtures (wiring-work/contact-test/, values invented for the test only, output to its own folder): all 7 sizes yes gives `specified and landed` for all 4; one `no` for P2 at US 11 leaves W055 `drawn, not routed` with "in_range not yes for P2 at lines 19". product-wiring.csv was unchanged by the tests (wiring-work/cmp-after-contact-test.log empty, cmp 0). build_wiring.py takes WIRING_CONTACT and WIRING_OUT only for such tests.
- Final runs 08:33:08 to 08:33:49 (wiring-work/final7-run.time): ring board file time 08:08:50 before and after; disk 22 GB free; build twice, cmp exit 0; check exit 0, last two lines verbatim:
  `COMPLETE 47 of 66 conductors (71 percent)`
  `RESULT PASS lines 67 (66 conductors, 1 sensing gap), drawn and routed 24, specified and landed 23, drawn, not routed 15, stated in text only 5, not drawn 0, complete 47 of 66 conductors (71 percent), problems 0`
- `--require-complete` (wiring-work/check-final7-require.log) exit 1, 19 incomplete lines: W039 to W053 (ring board round 3: ANT1 pad 4 and J1 pads not joined) and W054 to W057 (contact file missing). Last line verbatim:
  `RESULT FAIL lines 67 (66 conductors, 1 sensing gap), drawn and routed 24, specified and landed 23, drawn, not routed 15, stated in text only 5, not drawn 0, complete 47 of 66 conductors (71 percent), problems 19 (checks failing: incomplete)`
- Broken copies (wiring-work/broken-final9.log): `BROKEN COPIES PASS: 7 copies, each fails its named check with new FAIL lines and no other new failure`. Drawing (wiring-work/draw-final7.log): 66 conductors and 1 sensing gap drawn; pictures wiring-work/pictures/final7-svg.png and final7-pdf-1.png.
- connections.md: cells R8, R10, R15 and a fourth dated note (08:35); 22 rows with 8 cells (wiring-work/connections-fieldcount4.log).

## Files delivered

- design/wiring/product-wiring.csv (67 lines: 66 conductors and 1 sensing gap), system-joints.csv (1 typed row, R16), build_wiring.py, check_wiring.py, draw_wiring.py, product-wiring.svg, product-wiring.pdf, connections.md, this file; work files in design/wiring/wiring-work/. Commands: top of this file.

## questions_for_owner

none

## missing in the design files

| File | What a line needs | Conductors that wait |
|---|---|---|
| design/ecad/ring/pcb/ring.kicad_pcb | J1 pads and ANT1 pad 4 joined to their nets (round 3 routing; J1 already on the screen face) | W039, W040 to W053 |
| design/wiring/ring-case-contact.csv (being written by the case helper) | each pad paired with its pin at all 7 sizes, every in_range yes | W054 to W057 |

R16 (W058) needs nothing: a sensing gap with no conductor, counted apart.

RESULT: done, 67 lines (66 conductors, 1 sensing gap) built from the files; check_wiring.py passes for consistency and with --require-complete fails honestly at COMPLETE 47 of 66 conductors (71 percent), the 19 incomplete lines waiting only for the ring board's round 3 and design/wiring/ring-case-contact.csv.
