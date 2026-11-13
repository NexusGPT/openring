# Notes on the 39 open items of open-b.csv (state of today's design files)

Date of the review: 2026-11-13, 12:44 to 12:52 CET. Version: ROOT commit 0fa35499 (branch master). Output: `design/wiring/deferred-work/state-b.csv` (39 rows, header as asked). Paths in state-b.csv are relative to ROOT.

## Method

1. Read each item text in `design/wiring/deferred-items.md` (rows 1 to 163, with the items of open-b.csv) and the decisions in `design/wiring/lead-decisions.md` (74 lines, read in full; the newest row is first).
2. For each item, searched the design files named in its row and the files that the design today names (`ecad/ring/pcb/board-notes-r3.md`, `fab/stackup.txt`, `mfg/assembly/assembly.md`, `architecture.md`, `firmware.md`, `case/*`, `bom.csv`, `parts/order-codes.md`).
3. Old copies were not cited (no line under `*/evidence/`, `*/out/`, `*-work/`, `r3-fixes/`, `ring-route-*`, `sandbox_*`, `ring-lines`, `look/`). Lines marked REPLACED, history or before were not taken as today's answer.
4. Where a lead decision (lead-decisions.md) and an older file disagree, the decision was used as the answer and the older line is named in what_the_files_say.
5. Each quote was checked with a script that reads every cited file and confirms the quote is on the cited line (53 quotes, 0 problems). Every CLOSED TODAY and CONTRADICTED line carries its quote.
6. No script that writes files was run (the check scripts write logs into the design folders). Item 122 therefore rests on the last recorded run (`design/cell-sweep-notes.md` line 30).
7. Changed only my two files. No existing file was written. No browser, no web request, no supplier contact, no git write.

## Counts per state

| State | Count | Items |
|---|---|---|
| CLOSED TODAY | 10 | 1, 5, 12, 17, 18, 28, 113, 114, 116, 117 |
| CONTRADICTED | 5 | 10, 11, 95, 156, 161 |
| STILL OPEN, NEEDS HARDWARE | 1 | 120 |
| STILL OPEN, NEEDS A MAKER OR SUPPLIER | 9 | 20, 55, 72, 83, 84, 90, 111, 119, 126 |
| STILL OPEN, OWNER | 0 | none |
| STILL OPEN, DESIGN WORK | 14 | 27, 48, 61, 102, 103, 112, 115, 122, 123, 124, 129, 157, 158, 160 |
| Total | 39 | |

## Things that did not fit, and the way each was handled

- The open-item texts and their line cites in `deferred-items.md` are old in many rows. Example: the item 1 cite `board-notes.md` line 31 ("Route everything") is not in that file today (grep for "Route everything" found nothing in `board-notes.md`, `assembly.md` or `architecture.md`). Line cites in that file were not used; the current line of each quote was found by grep.
- Item 1 (225 connections unrouted) is CLOSED TODAY by the r3 rules check (`board-notes-r3.md` line 20).
- Items 10, 11, 95, 156 and 161 are CONTRADICTED: two present files give different answers, and both are quoted. For 11 the lead did not decide the finish, so the stack-up file was not taken over the spec; the conflict is left for the owner or the maker to settle.
- Item 103: the M1.2 screw is removed by the lead's row for items 45, 100 and 103 (`lead-decisions.md` line 57), but `architecture.md` line 162 still says 4 screws M1.2 x 3. Recorded as DESIGN WORK.
- Item 48: the owner's choice of the stock screen (`lead-decisions.md` line 63) and layout C (line 65) make the 5.0 mm fold in the model the thing to change; the narrower-cable route S27 is still listed open. Recorded as DESIGN WORK, not as needing a maker.
- Item 120 is split: the membrane is fixed (lead row 49), the gasket thicknesses are start values to be measured by bench B7. Recorded as NEEDS HARDWARE because the open part needs a measurement.
- Item 114: `assembly.md` line 300 still names SHIP_ENTER in the ship step; the K-A7 row says closed by SHIP_SAMPLE. Recorded as CLOSED TODAY on the K-A7 row; the step text is not changed by the lead's rows.
- Item 18: `design/ecad/ring/pcb/provisional-footprints.json` lines 13 and 14 still say PROVISIONAL for J_BAND_A and J_BAND_B; the band library file (`J_BAND_A_BOARD.kicad_mod` line 6) is the current answer. The json file is stale.
- Item 27: the risk list is spread over two files; case items 6 and 8 are already CLOSED by design, the others are open.
- Item 102 and 103: counts are from grep today. `grep -c ASSUMED` gives 30 for `design/mech/dimensions.csv` and 32 for `design/mech/ring.py` (the item text gives the same counts).
- Item 120 and 111: the 3M order number of DP420 Black is not in any saved file (`assembly.md` line 76 says so, and `w12-material-sources.md` rows 5, 9, 10 say it is ordered by name).
- Item 129: the nPM1304 datasheet on disk is `design/datasheets/npm1304_datasheet_v1_0.txt` (exists). It was not read for the C73 to C79 values, which is the design work named.

## Not checked

- Items 61 and 27 are judged from the text of the cited files; no audit or check script was run for either.
- Item 122: the script was not run; the open state is the last recorded run.

RESULT: done, 39 of 39 items: 10 CLOSED TODAY, 5 CONTRADICTED, 1 STILL OPEN NEEDS HARDWARE, 9 STILL OPEN NEEDS A MAKER OR SUPPLIER, 0 STILL OPEN OWNER, 14 STILL OPEN DESIGN WORK.
