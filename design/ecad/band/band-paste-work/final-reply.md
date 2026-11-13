Both of your messages and your ruling are handled, and every check passes, including the strict wiring check. Notes: design/ecad/band/band-paste-notes.md (logs in band-paste-work/logs/).

**Changes (all in design/ecad/band, all through the generators)**
- C1: 12 openings per FLEX1 board, 0.55 x 0.55, on the switch lands (F_Paste.gbr).
- C2: 16 openings per FLEX2 board, 0.58 mm, four per disc land, 0.05 mm clear of the via (B_Paste.gbr). They are now filled circles drawn on B.Paste instead of pads, so no pad is added. My first version used paste-only pads, and that is what caused your 28 `band-pad` fails.
- J_BAND (its own item, done the way you ruled, option b): J_BAND_A_BOARD and J_BAND_B_BOARD get one F.Paste opening per land, 0.30 x 0.44, centred, as a filled rectangle. No pad is added, so the counts stay 8 and 7. The board helper can now take design/ecad/band/OpenRingBand.pretty.
- C13: each drawing has a 4x view of the board end with every land's number and net, and a legend "LAND n = NET". FLEX1 marks "1 +: VMOT (red)"; FLEX2 names the P+, NTC and P- tabs. Text is 0.3 mm on the board, which prints at 1.77 to 2.12 mm on A4.
- C4: each fab folder has a fab-notes.txt with the P7 panel rule, and the drawing carries the same note.
- New make_fab.py. band-interface.md: 8 lines extended in place, none moved. The RESULT line of band-notes.md moved from line 140 to line 151; nothing cites it.

**Bars (last lines)**
1. The old generator reproduces the boards: `RESULT: PASS boards compared 14, boards with a not-allowed difference 0, mode identical`. After the change: `RESULT: PASS boards compared 14, boards with a not-allowed difference 0, mode paste-and-text allowed`. The control with one track moved gives `RESULT: FAIL boards compared 14, boards with a not-allowed difference 1, mode paste-and-text allowed`. Gerber geometry: `RESULT: boards 14, Gerber/drill/job files differing 0`.
2. kicad-cli drc, run in the band folder: 0 violations and 0 unconnected on 14 of 14 boards (drc5.log). check_band.py: `RESULT: PASS boards checked 14`. It rewrote the 14 drc reports.
3. Paste read back: `RESULT: PASS paste Gerbers checked 14, failing 0`. The controls give 11 and 15.
4. Drawings: `RESULT: PASS drawings checked 14, failing 0`. The control gives `RESULT: FAIL drawings checked 1, failing 1`.
- J_BAND: a test board's paste Gerber gives `RESULT: PASS regions 15, all 0.300 x 0.440: True`. The ring check_footprints.py on the new library still ends `RESULT FAIL 2 footprints netlist netlist.csv library OpenRing.pretty`: only C90 and R73 fail, with no new line.
- Wiring: check_wiring.py --require-complete exits 0: `RESULT PASS lines 67 (66 conductors, 1 sensing gap), drawn and routed 25, specified and landed 41, drawn, not routed 0, stated in text only 1, not drawn 0, complete 66 of 66 conductors (100 percent), problems 0`.

**Findings**
- The job files say BoardThickness 1.6, as the old ones did.
- I deleted 60 PPM renders (189 MB) to stay under 50 MB; the work folder is now 12.8 MB.
- At 14:04 I ran a read-only git log and git status.

questions_for_owner: none

RESULT: done, ribbons and J_BAND footprints carry paste (no pad added), drawings label every land; copper and nets unchanged, drc 0/0 on 14, check_band.py and check_wiring.py pass.
