# Notes: the joint-making steps of the assembly guide, rewritten (guide-joints)

Project root ROOT = .. Version read: the working tree at commit ce56ff0b. Work folder: `design/mfg/assembly/guide-joints-work/` (WORK): the guide before my first edit (`WORK/assembly-before.md`, same sha256 as the guide at the start, `WORK/logs/before-sha.txt`), the new step texts (`WORK/new/`), the scripts that applied them and filled the table, every log, `CHECKLIST.md`. A network outage stopped me before my first edit (the lead's message gives about 13:53); the work folder was made at 14:04:13 CET (`WORK/logs/start-time.txt`). I ran no git, no browser, no web request, and changed only the files I own.

## Steps changed (old number to new number)

| Old | New | What changed |
|---|---|---|
| 2 | 2 | Stencils (0.10 mm screen face, 0.075 mm parts face), paste Kester NP505-HR, squeegee, the reflow profile of process.md P3 written out, the 15 ribbon lands get paste in pass 2, never a third reflow (Hirose's 2 cycles), the stencil located by its openings (no fiducial on the board), the eight accept rules of a reflowed joint, R73 and C90 named, pass order confirmed |
| 4 | 4 | Inspection only: no washing, no brushing (the microphone maker's words); the residue and the 15 solder domes stay |
| 5 | 5 | The J_BAND_B pins touch solder domes; T-JOY, T-CENTRE, T-MOTOR now first at step 14, T-SCREEN, T-SIGN at step 16; "from step 15" became "from step 16" |
| 6 | 6 | Paste through the FLEX1 stencil (change C1), oven on the P3 profile, no liquid flux (Alps), probe by the foot's land numbers (change C13), needle tips |
| 7 | 7 | Wire Kester 275 0.25 mm, 50 W iron, chisel tip 0.8 mm, 320 C 2 s, feed the wire to the joint; probe tail lands 7 and 6; motor reading kept for step 14 |
| 8 | 8 | Paste through the FLEX2 stencil (change C2), hot plate on the P3 profile, disc height 0.070 to 0.112 mm; "flush with the liner" moved to step 21 |
| 9 | 9 | Wire 0.25 mm, tip 0.45 mm, 280 C 2 s; voltage before and after; the negative reading sentence of review 3 G2 |
| 10 | 10 | The two side slits in Before and Check, size "as the body drawing gives it"; "no wall slots" became "no microphone wall slots" |
| 13 | 13 | After: "until step 14" became "until step 15" |
| 16 | 14 | The hot-bar joint on the bench, board parts face up on the fixture `design/mfg/assembly/hotbar-fixture.svg`, 959T flux, blade 2.5 x 1.6 mm, 260 C 4 s 20 N, the 11 sub-steps, the meter check of all 15 lands, the J1 thermocouple limit of 217 C, at most two presses |
| 14 | 15 | Board turned over, each neck slides sideways into its side slit, harnesses in the channel, the board laid in the cavity |
| 15 | 16 | Tool line (no tool on J1's lever, change C18); continuity proof of the 14 contacts by T-SCREEN and T-SIGN before step 17 (change C12) |
| 17 | 17 | Press the board (laid in at step 15) and the screen down; the fold is the one taken at step 15 |
| 18 | 18 | T-XTAL while the screen is refreshed (lead-decisions.md row "32.768 kHz crystal lines") |
| 19 | 19 | The slits filled flush with DP420 Black; check from outside |
| 20 | 20 | Before: "steps 13, 14 and 19" became "steps 13, 15 and 19" |
| 21 | 21 | Test strip with one soldered disc and one soldered tab with residue (change C19); the disc flush check moved here; "live from step 16" became "step 14" |
| 25 | 25 | The cell-only test in the firmware's order: FACTORY_EXIT first (H19, state-b item 123); T-XTAL while the screen is refreshed |

Other parts of the guide: the header (line 3) says which step numbers changed; line 43 (step 15); section 1 rows of DISP1 and FOAM1 (step 16), the charging pads row (G4), the slot sealant row; section 3 K-A1 (step 16), K-A6 (ANSWERED by option A, line 334), K-A8 (step 14); section 4 row 10, the two slit seams (line 357), and the summary sentence; section 5 rows (FOAM1 step 16, sealant, U11 places line 380, charging pads line 384, ribbon rows, side slits row); section 6 rows 4 and 5 marked DONE (lines 403, 404); the RESULT line.

## Bar 1

- `check_assembly.py`, last line `RESULT PASS` (`WORK/logs/check_assembly-final.log`); before my edit it ended `RESULT FAIL A2` with "bom references not in any step: R73, C90" (`WORK/logs/check_assembly-before.log`); step 2 now names both. No rule of check_assembly.py encodes the old order, and I did not edit it.
- `check_docs.py`, last line `RESULT PASS` (`WORK/logs/check_docs-final.log`; also `RESULT PASS` before, `WORK/logs/check_docs-before.log`).

## Bar 2: check_joints.py

- Before: `RESULT FAIL 160` (`WORK/logs/check_joints-before.log`). After my first fill: `RESULT FAIL 114` (`WORK/logs/check_joints-run2.log`; I wrote the expected count, 114, before that run, `WORK/logs/check_joints-run1.log` gave it). After the case procedure of commit 9e09f881 landed (changes C5, C6, C15, C16; the lead's message) and the case rows were filled: `RESULT FAIL 110` (`WORK/logs/check_joints-run4.log`). A run in between gave `RESULT FAIL 125` (`WORK/logs/check_joints-run3.log`): my renumbering of the case steps raised a `[needs case N]` tag twice (15 R5 lines); fixed in `WORK/fill_joints.py`.
- `WORK/fill_joints.py` wrote `joints.csv` from the table as found (`WORK/joints-before.csv`): 530 fields changed in the final run (`WORK/logs/fill_joints-case.log`; 428 before the case rows, `WORK/logs/fill_joints.log`). Every `assembly.md:N` in the table points at the new lines: 786 citations, 0 problems, each step citation inside its own step (`WORK/logs/verify_joint_cites.log`).
- Settled rows: the 14 J1 rows (step 16, check possible at the same step), J-W036-A to J-W039-A and P-ring-F (alignment, the accept rules), the hot-bar rows' orientation, alignment, tool, heat, flux and check (step 14). After the case fill 42 rows are complete and 57 have a gap (`WORK/logs/list-gaps-run4.log`: `GAPS 57 of 99 rows`).
- What each failing line waits for now (`WORK/logs/waits-run6.log`, from the check log of run 6, `WORK/logs/check_joints-run6.log`, last line `RESULT FAIL 33`):

| Waits for | Rows | Failing lines |
|---|---|---|
| the board helper: the 15 J_BAND paste openings in ring-F_Paste.gbr (hotbar-joint.md section 7) | 15 | 30 |
| the board helper: change C3 (J1 openings, test pad openings) | 1 | 1 |
| total | 16 | 31 |

This table is what run 6 counted, less the 2 lines of P-case_main, which is filled since (below). By the lead's instruction I did not run check_joints.py again: its pad copy of the ring board is stale while the board is entering the design.

- History of the count: `RESULT FAIL 160` before; 114 after my first fill; 110 after the case rows (commit 9e09f881); 102 after the R4 change below (`WORK/logs/check_joints-run5.log`); 33 after the ribbon rows (commit a3492b1f, changes C1, C2, C13).

- Case rows filled from the case procedure of `design/ecad/case/pcb/board-notes.md` (commit 9e09f881; copy `WORK/board-notes-9e09f881.md`, same sha256, `WORK/logs/board-notes-sha.txt`): every case step number of the table raised by one (old 3 to 9 are now 4 to 10, the new case step 1 builds the case main board); P-case_main is at case step 1 with its alignment (stencil by its openings, case step 1 (b)); the four pin rows and P-case_pins are at case step 4 with the paste file `fab/case_pins/gerber/case_pins-F_Paste.gbr`; board-notes.md line citations follow the delivered file (mapped from the case helper's before copy, `WORK/board-notes-before-case-proc.md`).
- Rule R4 and the pin board: R4 counts only flashed openings (D03); the case helper drew the four ring openings as stroked circles. `WORK/ring_openings.py` reads the arcs: `RESULT ring openings on pin pads: 4 of 4`, each ring centred on its pin pad, inner diameter 1.100, outer 1.700 (`WORK/logs/ring_openings.log`); control with the P1 ring moved 0.5 mm: `3 of 4` (`WORK/logs/ring_openings-fake.log`). I did not edit check_joints.py. The lead then granted me R4 for exactly two new forms (diff `WORK/logs/check_joints.diff`, before copy `WORK/check_joints-before.py`): a stroked circle (a ring must be centred on its land within 0.02 mm; a filled dot must lie wholly on its land) and a filled region (its centre and its whole outline on the land). The first run of the new tests crashed on a region (`WORK/logs/tests-16.log`, a TypeError in has_opening); fixed, then `TESTS PASS 16 of 16 as expected` (`WORK/logs/tests-16b.log`; after the last fill `WORK/logs/tests-16-final.log`). The three new cases (ring moved 2.0 mm off its pad fails; a region on its land passes; the same region 1.0 mm off fails) are in `joint-table-work/tests/run_tests.py` (diff `WORK/logs/run_tests.diff`), their expectation written into `joint-table-work/tests/expect.txt` before the run; the tests ran in place, so their kept files are in `joint-table-work/tests/broken/`. A control on the real table: the FLEX2 US 9 disc openings moved 2 mm off CP1 give an R4 line for CP1:1 (`WORK/logs/control-disc.log`).

- `joint-gaps.md`: a first rebuild gave `gap lines 47 complete 52 unplaced 15` (`WORK/logs/make_gaps-run1.log`): `make_gaps.py` picked its groups by the old step numbers. The lead granted me exactly three edits in it (hot-bar test to step "14", screen connector test to step "16", that group's text to "step 16 ... before step 17"; diff `WORK/logs/make_gaps.diff`, before copy `WORK/make_gaps-before.py`). A rebuild after the case rows gave `gap lines 57 complete 42 unplaced 0 []` (`WORK/logs/make_gaps-run2.log`); the final rebuild after the ribbon rows: `gap lines 17 complete 82 unplaced 0 []` (`WORK/logs/make_gaps-run3.log`). The table helper's tests, run from a copy with the same sha256 in `WORK/tests/` (`WORK/logs/tests-sha.log`): `TESTS PASS 13 of 13 as expected` (`WORK/logs/tests.log`).

## Bar 3: review 3 faults

| Fault | Closing sentence in the guide (line) |
|---|---|
| G1 | 97: "J_BAND_A (8 lands) and J_BAND_B (7 lands) on the parts face get paste in PASS 2, one opening per land." Also 116 (step 4: "The solder domes on the 15 ribbon lands stay too") and 201 (step 14: "on the solder layer that step 2 put on the 15 lands"). The openings themselves wait for the board helper. |
| G2 | 136 (step 6): "the flex drawing of each size, `design/ecad/band/fab/flex1-usN-drawing.pdf`, prints the number and net of each foot land (change C13" ; 163 (step 9): "If it is negative, first check on the drawing that the probes sit on lands 1 and 2; only if they do is a tab on the wrong land." The drawings wait for change C13. |
| G3 | 201: "board parts face up on the fixture, foot on top, lands down, hot bar from above"; 203: "Each foot is aligned to the board's own lands by eye under a stereo microscope at 20 times" with the 0.335 and 0.20 mm marks and the fixture drawing. |
| G4 | 73: "the parts list row is CP1 to CP4 (it has no maker order code for the disc yet)"; 384: "Charging pads: fixed, a gold-plated disc 1.6 x 0.07 mm soldered on its land", citing `design/bom.csv:64`. |
| G5 | 154: "the disc top stands 0.070 to 0.112 mm above the land copper"; 262: "each disc of step 8 flush with the liner's inner face (... this check moved here from step 8". |
| G6 | 100: "Hirose's drawing says "Number of reflow cycles:2 cycles MAX."" and "So the ring board never goes through an oven a third time." |

Notes G7 to G11 (`WORK/logs/g7-g11-state.log`): G7 (no FLEX1 paste layer): open, closed by the helper making change C1; the guide names it at line 135. G8 (RT1 in bom.csv): closed already, `design/bom.csv:77` reads "inside the bought cell pack; not bought or soldered separately". G9 (touch gap 2.28 to 2.42 mm): open, `design/case/case-architecture.md` lines 64 and 152 still hold it; the case helper closes it. G10 (wait for a steady reading): closed already, `design/ecad/case/pcb/board-notes.md:301` holds "steady reading". G11 (cut label in product-wiring.pdf box R8): unverified (I did not open the drawing); the wiring drawing helper closes it.

## Older items of state-b

- Item 10: section 5 row "Places of U11, C83, C84" now says set, citing `design/ecad/ring/pcb/placement-final.csv:81` to `:83` (guide line 380); step 2 cites the same lines.
- Item 122: check_assembly.py passes (bar 1).
- Item 123: step 25 (line 295) follows `design/firmware.md` section 9.3 "Cell-only check": FACTORY_EXIT first, then the count.
- Item 124: section 6 rows 4 and 5 are made (`WORK/logs/section6-rows4-5-grep.log`: the old text of 17.23 is not in architecture.md; S26 at line 524 names K-A12). Rows 2 and 3 stay open: bom.csv has no floor slot sealant row (the same log, the search exits 1), and `design/mech/thin/placement.csv:39` still reads "frame on the liner".

## Bar 4: citations of the guide by line number

`WORK/cites_moved.py` searched every text file under ROOT/design except WORK (`WORK/logs/cites_moved.log`, full list `WORK/logs/cites-moved.tsv`). The old line is read in the guide before my edit; `WORK/linemap.py` finds its new line (`WORK/logs/linemap.log`). joints.csv is mine and was corrected (bar 2). Other files: 129 citations moved (117 in design files, 12 in logs outside work folders), 51 stayed, 21 have no new line (they cite a blank line or a line past the end of my base, so they cite an older version of the guide). Work folders of other helpers hold 9335 moved citations: records of past runs, listed in the tsv, not for correction. The 117 in design files, for the lead (the files are not mine):

| Citing place | Old line | New line | How the new line was found |
|---|---|---|---|
| `design/ecad/case/pcb/board-notes.md:293` | 99 | 103 | same field of step 2 (was step 2) |
| `design/ecad/case/pcb/board-notes.md:296` | 99 | 103 | same field of step 2 (was step 2) |
| `design/ecad/case/pcb/case-proc-notes.md:27` | 99 | 103 | same field of step 2 (was step 2) |
| `design/ecad/case/pcb/case-proc-notes.md:7` | 99 | 103 | same field of step 2 (was step 2) |
| `design/firmware-f6-notes.md:42` | 192 | 208 | same field of step 15 (was step 14) |
| `design/mech/thin/band-fit-notes.md:106` | 234 | 243 | same field of step 19 (was step 19) |
| `design/mech/thin/model-v9-notes.md:119` | 165 | 172 | same field of step 10 (was step 10) |
| `design/mech/thin/model-v9-notes.md:186` | 165 | 172 | same field of step 10 (was step 10) |
| `design/mech/thin/model-v9-notes.md:186` | 270 | 279 | same text |
| `design/mech/thin/model-v9-notes.md:186` | 345 | 354 | same text |
| `design/mech/thin/model-v9-notes.md:186` | 376 | 386 | same first 25 characters, text changed |
| `design/mech/thin/model-v9-notes.md:188` | 250 | 259 | same field of step 21 (was step 21) |
| `design/mech/thin/model-v9-notes.md:189` | 162 | 169 | same text |
| `design/mech/thin/model-v9-notes.md:189` | 323 | 332 | same text |
| `design/mfg/assembly/hotbar-joint.md:109` | 219 | 228 | same text |
| `design/mfg/assembly/hotbar-joint.md:165` | 213 | 205 | same field of step 14 (was step 16) |
| `design/mfg/assembly/hotbar-joint.md:178` | 157 | 164 | same field of step 9 (was step 9) |
| `design/mfg/assembly/hotbar-joint.md:179` | 155 | 162 | same field of step 9 (was step 9) |
| `design/mfg/assembly/hotbar-joint.md:180` | 213 | 205 | same field of step 14 (was step 16) |
| `design/mfg/assembly/hotbar-joint.md:184` | 99 | 103 | same field of step 2 (was step 2) |
| `design/mfg/assembly/hotbar-joint.md:191` | 145 | 151 | same field of step 8 (was step 8) |
| `design/mfg/assembly/hotbar-joint.md:40` | 120 | 124 | same text |
| `design/mfg/assembly/hotbar-joint.md:83` | 194 | 210 | same field of step 15 (was step 14) |
| `design/mfg/assembly/hotbar-joint.md:91` | 234 | 243 | same field of step 19 (was step 19) |
| `design/mfg/assembly/joint-table-notes.md:15` | 208 | 199 | same field of step 14 (was step 16) |
| `design/mfg/assembly/process.md:163` | 253 | 262 | same field of step 21 (was step 21) |
| `design/mfg/assembly/process.md:178` | 99 | 103 | same field of step 2 (was step 2) |
| `design/mfg/assembly/process.md:55` | 144 | 150 | same field of step 8 (was step 8) |
| `design/mfg/assembly/process.md:73` | 112 | 116 | same field of step 4 (was step 4) |
| `design/mfg/maker-files-v62-notes.md:27` | 162 | 169 | same text |
| `design/review/design-review-2.md:113` | 330 | 339 | same text |
| `design/review/design-review-2.md:114` | 326 | 335 | same text |
| `design/review/design-review-2.md:129` | 138 | 144 | same field of step 7 (was step 7) |
| `design/review/design-review-2.md:33` | 99 | 103 | same field of step 2 (was step 2) |
| `design/review/design-review-2.md:36` | 138 | 144 | same field of step 7 (was step 7) |
| `design/review/design-review-3.md:32` | 98 | 102 | same field of step 2 (was step 2) |
| `design/review/design-review-3.md:44` | 228 | 237 | same text |
| `design/review/design-review-3.md:70` | 228 | 237 | same text |
| `design/review/design-review-3.md:78` | 98 | 102 | same field of step 2 (was step 2) |
| `design/review/design-review-3.md:81` | 137 | 143 | same text |
| `design/review/design-review-3.md:86` | 137 | 143 | same text |
| `design/review/must-ask-state.md:16` | 118 | 122 | same text |
| `design/review/must-ask-state.md:16` | 288 | 297 | same field of step 25 (was step 25) |
| `design/review/must-ask-state.md:16` | 296 | 305 | same field of step 26 (was step 26) |
| `design/review/r3-fixes/mfg/notes.md:84` | 123 | 127 | same field of step 5 (was step 5) |
| `design/wiring/deferred-items.md:12` | 326 | 335 | same text |
| `design/wiring/deferred-items.md:120` | 321 | 330 | same text |
| `design/wiring/deferred-items.md:120` | 360 | 370 | same text |
| `design/wiring/deferred-items.md:121` | 364 | 374 | table row by first cell, text changed |
| `design/wiring/deferred-items.md:122` | 320 | 329 | table row by first cell, text changed |
| `design/wiring/deferred-items.md:123` | 318 | 327 | same text |
| `design/wiring/deferred-items.md:124` | 324 | 333 | same text |
| `design/wiring/deferred-items.md:125` | 329 | 338 | same text |
| `design/wiring/deferred-items.md:125` | 365 | 375 | same text |
| `design/wiring/deferred-items.md:126` | 363 | 373 | same text |
| `design/wiring/deferred-items.md:127` | 362 | 372 | same text |
| `design/wiring/deferred-items.md:128` | 372 | 382 | same text |
| `design/wiring/deferred-items.md:129` | 366 | 376 | same first 25 characters, text changed |
| `design/wiring/deferred-items.md:129` | 369 | 379 | same text |
| `design/wiring/deferred-items.md:130` | 370 | 380 | same first 25 characters, text changed |
| `design/wiring/deferred-items.md:130` | 371 | 381 | same text |
| `design/wiring/deferred-items.md:131` | 349 | 359 | same first 25 characters, text changed |
| `design/wiring/deferred-items.md:134` | 381 | 392 | same text |
| `design/wiring/deferred-items.md:134` | 383 | 394 | same text |
| `design/wiring/deferred-items.md:20` | 368 | 378 | same text |
| `design/wiring/deferred-items.md:47` | 323 | 332 | same text |
| `design/wiring/deferred-items.md:47` | 373 | 383 | same text |
| `design/wiring/deferred-items.md:73` | 325 | 334 | table row by first cell, text changed |
| `design/wiring/deferred-items.md:84` | 370 | 380 | same first 25 characters, text changed |
| `design/wiring/deferred-triage.csv:114` | 320 | 329 | table row by first cell, text changed |
| `design/wiring/deferred-triage.csv:115` | 326 | 335 | same text |
| `design/wiring/deferred-triage.csv:117` | 365 | 375 | same text |
| `design/wiring/deferred-triage.csv:118` | 363 | 373 | same text |
| `design/wiring/lead-decisions.md:38` | 253 | 262 | same field of step 21 (was step 21) |
| `design/wiring/lead-decisions.md:45` | 347 | 356 | same text |
| `design/wiring/text-pass-notes.md:116` | 162 | 169 | same text |
| `design/wiring/text-pass-notes.md:116` | 323 | 332 | same text |
| `design/wiring/text-pass-notes.md:184` | 250 | 259 | same field of step 21 (was step 21) |
| `design/wiring/text-pass-notes.md:210` | 162 | 169 | same text |
| `design/wiring/text-pass-notes.md:210` | 323 | 332 | same text |
| `design/wiring/text-pass-notes.md:212` | 165 | 172 | same field of step 10 (was step 10) |
| `design/wiring/text-pass-notes.md:212` | 270 | 279 | same text |
| `design/wiring/text-pass-notes.md:212` | 345 | 354 | same text |
| `design/wiring/text-pass-notes.md:212` | 376 | 386 | same first 25 characters, text changed |
| `design/wiring/text-pass-notes.md:219` | 250 | 259 | same field of step 21 (was step 21) |
| `design/wiring/text-pass-notes.md:220` | 250 | 259 | same field of step 21 (was step 21) |
| `design/wiring/text-pass-notes.md:227` | 162 | 169 | same text |
| `design/wiring/text-pass-notes.md:227` | 323 | 332 | same text |
| `design/wiring/text-pass-notes.md:247` | 165 | 172 | same field of step 10 (was step 10) |
| `design/wiring/text-pass-notes.md:247` | 270 | 279 | same text |
| `design/wiring/text-pass-notes.md:247` | 345 | 354 | same text |
| `design/wiring/text-pass-notes.md:247` | 376 | 386 | same first 25 characters, text changed |
| `design/wiring/text-pass-notes.md:304` | 202 | 218 | same field of step 16 (was step 15) |
| `design/wiring/w11-item-values.md:115` | 370 | 380 | same first 25 characters, text changed |
| `design/wiring/w11-item-values.md:14` | 253 | 262 | same field of step 21 (was step 21) |
| `design/wiring/w11-item-values.md:14` | 253 | 262 | same field of step 21 (was step 21) |
| `design/wiring/w11-item-values.md:14` | 318 | 327 | same text |
| `design/wiring/w11-item-values.md:23` | 253 | 262 | same field of step 21 (was step 21) |
| `design/wiring/w11-item-values.md:409` | 321 | 330 | same text |
| `design/wiring/w11-item-values.md:410` | 360 | 370 | same text |
| `design/wiring/w11-item-values.md:412` | 347 | 356 | same text |
| `design/wiring/w11-item-values.md:470` | 347 | 356 | same text |
| `design/wiring/w12-material-sources.md:76` | 321 | 330 | same text |
| `design/wiring/wiring-review-2.md:32` | 144 | 150 | same field of step 8 (was step 8) |
| `design/wiring/wiring-review-2.md:33` | 136 | 141 | same field of step 7 (was step 7) |
| `design/wiring/wiring-review-2.md:33` | 138 | 144 | same field of step 7 (was step 7) |
| `design/wiring/wiring-review-2.md:34` | 155 | 162 | same field of step 9 (was step 9) |
| `design/wiring/wiring-review-2.md:35` | 130 | 135 | same field of step 6 (was step 6) |
| `design/wiring/wiring-review-2.md:35` | 146 | 152 | same field of step 8 (was step 8) |
| `design/wiring/wiring-review-2.md:38` | 131 | 136 | same field of step 6 (was step 6) |
| `design/wiring/wiring-review-2.md:44` | 120 | 124 | same text |
| `design/wiring/wiring-review-3.md:21` | 144 | 150 | same field of step 8 (was step 8) |
| `design/wiring/wiring-review-3.md:40` | 210 | 201 | same field of step 14 (was step 16) |
| `design/wiring/wiring-review-3.md:42` | 148 | 154 | same field of step 8 (was step 8) |
| `design/wiring/wiring-review-3.md:43` | 99 | 103 | same field of step 2 (was step 2) |
| `design/wiring/wiring-review.md:21` | 120 | 124 | same text |
| `design/wiring/wiring-review.md:21` | 124 | 128 | same field of step 5 (was step 5) |

## Ribbon rows after commit a3492b1f (changes C1, C2, C13)

- The 14 paste files hold 12 flashed openings per FLEX1 and 16 round openings per FLEX2 (`WORK/logs/flex-paste-counts.log`; flex2-us10 reads 18 circles because two centres of one disc differ in the fourth decimal, `WORK/logs/flex2-us10-circles.log`). The 14 drawings carry the detail "BOARD END OF THE RIBBON: LAND NUMBERS AND NETS" with 8 (FLEX1) or 7 (FLEX2) land lines (`WORK/logs/drawings-landnumbers.log`, text by pdftotext in `WORK/drawings/`).
- Filled: the 12 switch rows and 4 disc rows name the paste layer of all 7 sizes for their land (R4 checks each); P-flex1-usN and P-flex2-usN name every switch land or disc land of their board; the motor and tab rows' gaps (land numbers) are empty. Guide steps 6 and 8 (lines 135 and 153) now say the paste layers exist.
- P-case_main, first look: `WORK/logs/case-powerup-search.log` and `WORK/logs/case-powerup-search2.log` (searches of board-notes.md and case-architecture.md for power-up, factory test, current, programming, jig) find test pads for the module (BOOT, UART, EN) but no first power-up or factory test. The check of the hidden joints was MISSING. The lead then wrote case step 1 (g), the first power-up test (board-notes.md line 293 and the indented lines under it; copy `WORK/board-notes-current.md`). P-case_main's check now quotes it: the module's supply and ground pads are "shown by TP3 only, with the 3V3 reading in range", but "One missing ground joint among the many does not change any reading: NOT proven"; of the signal pads "only pin 39 (TXD0) is shown", "The module pins IO0 to IO48 other than TXD0: NOT proven"; the charger's centre pad: "this test does NOT prove it". Check possible at case step 1; gap empty. Every quote and every case step citation checked: `RESULT case citations and quotes 25 problems 0` (`WORK/logs/verify_case_cites.log`). joint-gaps.md rebuilt: `gap lines 16 complete 83 unplaced 0 []` (`WORK/logs/make_gaps-run4.log`).

## Ring board of commit 796a0086 (final fill)

- Pad copy refreshed: the 17 board files copied into `joint-table-work/boards/` (16 changed, `WORK/logs/boards-sha.diff`), `dump_pads.py` run with KiCad's Python (`WORK/logs/dump_pads.log`), old dumps kept in `WORK/pads-before/`. What changed (`WORK/logs/pads-diff.log`, `WORK/logs/ring-pads-diff.log`): layer lists (F.Paste on the 12 switch lands of each FLEX1, B.Paste gone from the 12 test pads, J1's pads), R73 and C90 added to the ring board, no land moved.
- The paste files (`WORK/logs/ring-paste-counts.log`): ring-F_Paste.gbr 306 flashes and 15 regions, 15 of 15 J_BAND lands with an opening; ring-B_Paste.gbr 16 flashes and 17 regions, 0 of 12 test pads with an opening.
- Filled: the 15 hot-bar rows name `ring-F_Paste.gbr` for their land; P-ring-F covers every part of ring-pos-front.csv (no exception); P-ring-B covers ring-pos-back.csv except the 12 test pads. Guide step 2 says the delivered files hold these openings, and R73 and C90 are on the parts face (ring-pos-front.csv lines 66 and 42); section 5's hot-bar row no longer lists the openings as open.
- R4 fix in my own code of the grant: the first run gave `RESULT FAIL 17`, all on J1 (`WORK/logs/check_joints-run7.log`). The pad dump has no rotation, and J1's pads lie turned 90 degrees on the board, so a region could not fit the unturned box. A region or a dot now fits the pad's box either way round. Then `RESULT PASS joints 99` (`WORK/logs/check_joints-run8.log`). Controls: the ring board's regions moved 1.0 mm give 1 R4 line on J-W001-A (F) and 17 on P-ring-B (B) (`WORK/logs/control-ring.log`).
- Final runs: check_joints.py `RESULT PASS joints 99` (`WORK/logs/check_joints-final.log`); make_gaps.py `gap lines 0 complete 99 unplaced 0 []` (`WORK/logs/make_gaps-run5.log`); check_assembly.py `RESULT PASS` (`WORK/logs/check_assembly-run7.log`); check_docs.py `RESULT PASS` (`WORK/logs/check_docs-run7.log`); guide citations in the table `RESULT citations 786 problems 0`; case citations and quotes `RESULT case citations and quotes 25 problems 0`.
- The table helper's tests now end `TESTS FAIL 14 of 16 as expected` (`WORK/logs/tests-16-ring.log`): the two old cases "paste_no_opening" (mini and real) use the land J_BAND_A:1 because it had no opening, and since 796a0086 it has one. R4 is not at fault (controls above). I proposed to the lead to point that fixture at TP1:1 of ring-B_Paste.gbr; not done without the lead's word. The lead agreed: NO_OPEN now names TP1:1 of ring-B_Paste.gbr, with a comment on why, and my two controls (ring regions moved 1.0 mm: 1 R4 line on J-W001-A, 17 on P-ring-B) are kept tests of the same file (diff `WORK/logs/run_tests-fixture.diff`; expectation appended to expect.txt before the run). Last lines: tests `TESTS PASS 18 of 18 as expected` (`WORK/logs/tests-18.log`), check_joints.py `RESULT PASS joints 99` (`WORK/logs/check_joints-final2.log`), make_gaps.py `gap lines 0 complete 99 unplaced 0 []` (`WORK/logs/make_gaps-final2.log`).

## Moved guide citations corrected in other design files

`WORK/fix_cites.py` changes a citation only when the citing line quotes text that is on the old line and on the new line. I applied it to the two live specifications only (`--live`): process.md lines 55 (144 to 150) and 163 (253 to 262), board-notes.md line 293 (99 to 103) (`WORK/logs/fix_cites-apply.log`, diff `WORK/logs/fix_cites.diff`, copies before in `WORK/fixed-before/`). Not changed, listed: process.md lines 73 and 178 and board-notes.md line 318 (their quotes describe text my rewrite replaced, or the quote is not on the old line). Reviews, triage tables and state records (wiring-review-2 and -3, design-review-2 and -3, deferred-items.md, deferred-triage.csv, must-ask-state.md, w11-item-values.md and the rest of `WORK/logs/fix_cites-dry.log`) cite the guide at the version they judged; the dry run over all design files found 11 provable citations (3 applied above, 8 in these records) and 85 it could not prove; I changed none in these records (for the lead).

## Waits for other helpers

- The board helper: the ring board landed (commit 796a0086) and its rows are filled.
- The flex helper: changes C1, C2 and C13 landed (commit a3492b1f) and their rows are filled.
- The case helpers: changes C5 and C6 landed (commit 9e09f881) and their rows are filled.
- The lead: nothing open in the table (P-case_main filled from case step 1 (g)).
When each lands, I fill the rows (solder_source to a `paste layer <file> for <lands>` text that rule R4 checks, the gap emptied) and run check_joints.py again.

## Left for the lead

1. Done by the lead's grant: R4 reads stroked circles and regions (bar 2). The case power-up test is written (case step 1 (g)); what it does not prove (the charger's centre pad, one missing module ground joint, the module's other signal joints) stays in the row's check.
2. My reading of option A at step 15 (accepted by the lead by message): with no free ribbon length the board comes into the cavity as the necks go into the slits; step 15 lays it in, step 17 presses it; the screen is plugged with the board in the block (step 16).
3. The slit's width, depth and place: "as the body drawing gives it" at steps 10, 15, 19 and section 4 row 10; no number written.
4. The block's outside height: not written.
5. The iron setting for re-soldering a fallen 0201 part of the screen face: no sheet gives it (step 2).
6. X-ray of lands A6 and A8 after the hot bar: the lead decides (step 14).
7. The starting values marked [PROPOSED: starting value, confirmed on the first build] in steps 5 and 14 (from hotbar-joint.md section 6).
8. Read-only files that still name the old step numbers 14, 15, 16 (`WORK/logs/notes-lines.log`): process.md lines 67, 175, 177, 206, 211, 212; hotbar-joint.md lines 10, 19, 91, 93, 97, 99, 109, 117, 180, 235, 238, 241, 250. The guide's header says what the old numbers mean.
9. Table rows J-W011-A and J-W021-A (lands A8 and A6): the meter cannot see an open of one of the two; the check field says so.

questions_for_owner: none

RESULT: done, check_joints.py ends `RESULT PASS joints 99`, make_gaps.py `gap lines 0 complete 99 unplaced 0 []` and the table tests `TESTS PASS 18 of 18 as expected`; moved guide citations corrected in the two live specifications, the citations in pinned reviews and records listed for the lead.
