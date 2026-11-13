# Case procedure: build step, pin reflow, two checks, panel notes (process.md C4, C5, C6, C15, C16)

Written 2026-11-13, work from 13:47 CET to 14:09 CET (clock: `date`, W/clock.txt). ROOT = .. P = ROOT/design/ecad/case/pcb. W = P/case-proc-work/ (every log and script; copies of the files before the change in W/before/ and W/wbefore/). PM = ROOT/design/mfg/assembly/process.md. I ran no git command, no check_band.py, no browser, no web request. A first try of the paste ring (W/try/, a copy of the board) was made before the real run; it is kept.

## Changes (file, before, after, source, proof)

1. C5, P/board-notes.md, case procedure: new step 1 "Build the case main board" (stencil 0.10 mm; paste; placing from case_main_position.csv; one reflow with the P3 profile, saying that the module U1 accepts 1 reflow; inspection of every joint at 10 times; then the USB socket shell slots by hand; nothing powered). Before: 9 numbered steps starting with "Parts". After: 10 steps. Sources are named in each sentence (PM P1.2, P2, P3, P4, P6, P7, E1 p.47, assembly.md line 99). Proof: W/edit_notes.py, W/edit_notes.log ("OK").
2. Step numbers, old to new: 1 to 2 (Parts), 2 to 3 (Twist), 3 to 4 (Which end first, now also the pin reflow), 4 to 5 (Depth gauge), 5 to 6 (Order inside each end), 6 to 7 (Pin board end), 7 to 8 (Main board end), 8 to 9 (Check after soldering), 9 to 10 (Cell leads and thermistor). References inside the file updated: "order of step 5" now "step 6"; "after step 8, because step 8 needs" now "after step 9, because step 9 needs"; "step 7 of the soldering order" now "step 8"; "numbered steps 1 to 9" now "1 to 10". The generator's two cited lines moved from 295 and 297 to 296 and 298.
3. C6, P/case_pins.kicad_pcb: 4 paste openings added on F.Paste, one ring over each pin pad P1 to P4 (outer 1.70 mm = pad, inner 1.10 mm = hole; p3_harwin_p70.txt lines 68 and 69), drawn as a stroked circle of dia 1.40 mm and width 0.30 mm; added by W/add_pin_paste.py (add only). The ring shape is my choice: PM P4 pins row says only "pin in paste" and gives no size. Proof: W/add_pin_paste.log ("DONE added 4"); W/paste_count.log: before "arcs 0 ring openings 0", after "arcs 8 ring openings 4" (8 half arcs = 4 rings; flashes 0, regions 0).
4. C6, P/fab/case_pins/ regenerated with `bash P/export_fab.sh pins` (every export exit 0, W/fab_export_pins.log). Against the copy before (W/compare_fab_pins.log): only case_pins-F_Paste.gbr differs, plus the creation-date lines of the two drill files (the gerber compare ignores date lines; the drill diff shows only the date lines, read by hand in this run).
5. C6, board-notes.md step 4 (old 3), pin part rewritten: pins reflowed in paste, stencil from the new paste file, carrier with holes under the pin tails, place from case_pins_position.csv, one reflow with the P3 profile (pin limit 260 C for 10 s, margin 15 C), inspect at 10 times, then the wires by hand, then press, stakes; the depth gauge step (now 5) is unchanged. The phrase the wiring generator searches for ("Which end first: the pin board end (pads WP1 to WP4 and WP7) of all five wires first, then the main board end") is unchanged.
6. C15, board-notes.md step 9 (old 8): after the 147 kohm sentence: "Wait for a steady reading ... capacitor C15 (10 uF, parts.csv line 52, net VRING, netlist.csv line 252) ... charges through the meter". Source: PM P8 C15 and review 3 G10.
7. C16, board-notes.md step 10 (old 9): after "Never swap the two": red probe on pad W5, black on pad W6, +3.0 to 4.35 V; source PM P8 C16 and lead-decisions.md line 70.
8. C4, board-notes.md, new section "Round 4", "Fabrication notes for both case boards" (the fabrication notes of both boards are this section; export_fab.sh deletes and rewrites the fab folders, so no note file can live there): panel rails 5 mm, three 1 mm fiducials on F per panel, centred 3.85 mm from the panel edges, not in a line; fiducial mask opening open; stencils; copper weight (the lead's ruling 4 of 11:53 said it is written here at the next change); one reflow per board. No new copper: see bar 1.
9. Wiring list: ROOT/design/wiring/product-wiring.csv rebuilt with `python3 design/wiring/build_wiring.py` (W/build_after.log). My lines: the 5 case wire rows W063 to W067 now cite board-notes.md lines 296 and 298 (were 295 and 297). The rebuild also changed 49 other rows (W001 to W057, ring and band rows): their line numbers cite ring/netlist.csv and other files that other helpers have changed since the last build; before my rebuild check_wiring gave 78 `proof-text` failures on those rows (W/product-wiring.csv.bak is the file with only my two numbers changed; W/wbefore/product-wiring.csv is the file as found). W/product-wiring.rebuilt.csv is the delivered one. build_wiring.py also rewrote the cache files in ROOT/design/wiring/wiring-work/drc/ (its normal output). system-joints.csv: not changed (no cited board-notes line). draw_wiring.py not run: no label changed; the svg holds no board-notes line (grep count 0).

## Bars

1. Rules check, each run inside its own folder (cd P first), `kicad-cli pcb drc --severity-all --all-track-errors`: case_pins before `Found 0 violations`, `Found 0 unconnected items` (W/drc_before_pins.log); after, same two lines (W/drc_after_pins.log). case_main before and after the same two lines (W/drc_before_main.log, W/drc_after_main.log). Copper compare by W/cu_compare.py (pad, track, zone and Edge.Cuts dump before and after): last line of W/cu_compare.log: `CU IDENTICAL both boards`; its lines: `pins pads 10 trk 7 zones 1 edge 12 IDENTICAL` and `main pads 306 trk 737 zones 5 edge 8 IDENTICAL`. The only line added in the dump of the pin board is four `DRAW PCB_SHAPE F.Paste` (diff in the run output, W/dump_before_pins.log, W/dump_after_pins.log).
2. Paste file of the pin board: W/paste_count.log, `case_pins F_Paste before arcs 0 ring openings 0 flashes 0 regions 0` and `case_pins F_Paste after arcs 8 ring openings 4 flashes 0 regions 0`.
3. check_boards.py (CHECK_BOARDS_TMP = W/cb_tmp): last line `RESULT PASS check_boards case_main.kicad_pcb case_pins.kicad_pcb`, exit 0 (W/check_boards_after.log, W/check_boards_after.exit). check_case_docs.py: last line `RESULT PASS (0 findings)` (W/check_case_docs_after.log, exit 0). check_wiring.py --require-complete: exit 0, `COMPLETE 66 of 66 conductors (100 percent)` and a last line that ends `problems 0` (W/check_wiring_after.log).
4. Sources: each new sentence of steps 1, 4, 9 and 10 and of Round 4 names its section of PM, its maker file with line, or "my reading" or [CHOICE].

## Findings and what is left for the lead

- Step numbers in other files now off by one (not mine): PM P4 and P8 (C5 says "step 0", C6 "step 3", C15 "step 8", C16 "step 9", the P4 rows "case steps 3, 6, 7, 9"); design/mfg/assembly/joints.csv and joint-gaps.md (column "case 3", "case 6", "case 7", "case 9" and "case step 3"); ROOT/design/case/case-architecture.md line 219 ("step 4 of the numbered case procedure" now step 5). New numbers: pins reflow 4 (was 3), wire pin end 7 (was 6), wire main end 8 (was 7), check 9 (was 8), cell leads 10 (was 9), new build step 1.
- The accept rule for a reflowed joint is not in PM (PM C14 says the lead names it; lead-decisions.md row 82 says the guide writes the visible criteria out, but none are written yet). Step 1 (e) uses only assembly.md line 99 (no bridge, in place, not tilted). Open.
- Joints under U1 and under the thermal pad of U2 cannot be seen at 10 times; no file gives a check. Open.
- The carrier "with holes for the pin tails" (lead's instruction): the peg is 0.65 mm and the board 0.8 mm, so no tail leaves the back face (w15 file lines 280, 345). Step 4 (c) says the hole serves the paste pushed through the hole (my reading). The lead may confirm or drop the carrier holes.
- The paste rings are stroked circles in the Gerber (4 rings, 8 arcs). A stencil maker that wants flashed or region openings needs a note; PM gives no size, so ring 1.70/1.10 is a [CHOICE].
- check_boards.py does not check paste openings. Owner of that file: add a check for the 4 rings if wanted.
- Fiducials: not drawn on the boards (they are on the panel rails, PM P7); their mask opening is open.
- Rework settings of step 1 (e) (340 C, 50 W, 7 s) are my reading, not a source.
- Not done: the automatic claim audit of rule 4 beyond the checks listed above; nothing was built on a real board.

questions_for_owner: none

## Second item: first power-up test of the case main board (16:00 to 16:06 CET, clock from `date`)

Change. File: P/board-notes.md, step 1, new last sub-step "(g) First power-up test of the case main board, before any wire is soldered": the end of the step 1 line names it, and 22 indented lines follow it (g1 the connection, g2 the order, then one line per rail and per test pad, then the four hidden joint groups H1 to H4, then one line of what the test does NOT prove). Step 1 (e) now points to (g) instead of "open, for the lead". Later step numbers are unchanged (2 to 10). Script: W/edit_pu.py, W/edit_pu2.py, W/edit_pu3.py (logs edit_pu*.log). Text files read for it: W/txt/ (pdftotext copies of case_bq25895.pdf, case_esp32s3_mini1.pdf and case_esp32s3_ds.pdf; every page cited was computed from them).

What the test gives (all values from the cited files):
- Connected: bench supply 5.0 V, limit 1.5 A, on J1 VBUS and GND only; no cell, no pin board, no wire (sources in line g1).
- Lines with an expected value: VBUS_IN above 3.6 V (BQ p.7); SYS 3.50 to 3.65 V no load, up to 4.42 V loaded (BQ p.7); REGN 4.7 V or more (BQ p.10); 3V3 3.274 to 3.341 V (SN line 74, SL lines 126 and 127); VRING off, under 0.1 V (SL R2.5 as a stand-in limit); LED hand test across R8 1.53 to 2.35 V, across R9 and R10 0.59 to 1.27 V (CS lines 114 to 119, [CALC] mA times ohm); CHG_STAT and CHG_CE_N high; TP1 and TP2 high (the 3V3 reading); TP3 activity after power-up.
- Serial pad: ES p.15 says the ROM prints to UART0 by default; the message text, baud rate and timing are in no saved document (W/search_boot.log), so only "activity" is written.

Left for the lead (no expected value in the files, written as such in the lines):
- TP4 RXD0; TP6 to TP15 (SPARE_IO33 to IO42): no expected value; unpowered short check only (below about 50 ohm, the step 9 limit).
- TP5 QON: only a typical 4.3 V (BQ p.10), no range.
- Resistance in ohm of VBUS_IN, SYS, 3V3 to GND (unpowered), and the idle supply current in mA.
- The three LED line voltages with the module pins undriven (CS section 9 gives only a bound near 3.7 V).
- The VRING "off" limit of 0.1 V is borrowed from a ring row; no file gives one for VRING.
- BAT pad (W5) with no cell; the charger's STAT or fault display with TH1 not fitted.
- No test for the charger's centre pad (H4): an X-ray or a section.
- The simulation rows C4.1 to C4.4 (SL lines 122 to 125) still name 470 and 150 ohm and a 3V3 supply; they predate sim finding 3 and were not used.

Not proven by the test (also written in step 1 (g)): solder under the charger's centre pad; every module signal joint except TXD0; a single missing module ground joint; the charger's BAT pins; charging; VRING current limit and boost; the module's LED drive; TH1; the SD NAND; USB data.

Checks after the change (same commands as before; logs in W):
- check_boards.py (CHECK_BOARDS_TMP = W/cb_tmp): last line `RESULT PASS check_boards case_main.kicad_pcb case_pins.kicad_pcb`, exit 0 (W/check_boards_after2.log).
- check_case_docs.py: last line `RESULT PASS (0 findings)`, exit 0 (W/check_case_docs_after2.log).
- check_wiring.py --require-complete: exit 0, last line `RESULT PASS lines 68 (67 conductors, 1 sensing gap), drawn and routed 26, specified and landed 41, drawn, not routed 0, stated in text only 1, not drawn 0, complete 67 of 67 conductors (100 percent), problems 0` (W/check_wiring_after2.log). It is 67 of 67 and not 66 of 66 because another helper added one conductor to the ring files before this run; the case rows are unchanged.
- Lines moved: the two lines the wiring generator cites ("Which end first", "Order inside each end") moved from 296 and 298 to 318 and 320. build_wiring.py was run again (W/build_after2.log): against the list before this run (W/wbefore2/product-wiring.csv) 5 rows differ, the 5 case wire rows (W064 to W068 in the new numbering), and only in their cited board-notes line numbers. Both cited lines now read 318 and 320 in the five rows. system-joints.csv: not changed; draw_wiring.py not run (no label changed).
- Copper: not touched in this item (no board file was opened for writing).
- Not done: the automatic claim audit of rule 4 beyond these checks; nothing was built on a real board.

questions_for_owner: none


RESULT: done, step 1 (g) first power-up test written with 22 lines (connection, order, rails, 16 pads, 4 hidden joint groups, what is not proven), later step numbers unchanged, check_boards and check_case_docs pass, check_wiring --require-complete exit 0 (67 of 67).
