# Assembly guide fix: two-face board and the screen turned 180 degrees

Written 2026-11-13 (Mac clock, `date`: 11:30 at the first command). File changed: `design/mfg/assembly/assembly.md` only. Copy before my first edit: `design/wiring/guide-fix-work/assembly.before.md`; full diff: `design/wiring/guide-fix-work/assembly.diff`; edit scripts and their logs: `design/wiring/guide-fix-work/edit1.py` to `edit8.py` and `edit*.log` (all empty = no error). I made no git write. `check_assembly.py` and `check_docs.py` were not changed.

## Face names used in the guide

PARTS FACE = KiCad F.Cu = "top" in `ring-pos-front.csv` (72 parts, ribbon lands J_BAND_A and J_BAND_B; the old guide's "under face"). SCREEN FACE = KiCad B.Cu = "bottom" in `ring-pos-back.csv` (J1, C1, C2, C5, C7, C14, FB1, R71, R72, 12 test pads). Sources: `board-notes-r3.md:35`, `placement-final.csv:78`, `fab/stackup.txt:10`. Count check: `guide-fix-work/refs_diff.log` (front 74 entries = 72 parts + 2 land rows; back 21).

## Edits (found by their text; before, after, source)

| # | Place (found by text) | Before | After | Source |
|---|---|---|---|---|
| 1 | Section 0, "Face names on the main board" | UNDER face carries all parts, TOP face bare | both faces named and filled as above | files above |
| 2 | Header paragraph "Basis" | none | one sentence naming this update | this file |
| 3 | Section 1 rows Screen, Foam, Main board, Board parts, U11 row | "tail into J1", "foam frame closed all round", "parts on the under face only", "under the board" | screen turned 180, cable plugged into J1 on screen face (J1 opening to the fingertip, contacts up, contact 1 on +Y); foam NOT a frame; parts on both faces; "on the parts face" | `screen-cable-study.md:166,207`, `board-notes-r3.md:35,47` |
| 4 | Step 2 (title, Join, Locate, Before, Check, After) | one reflow, every part on the under face, 15 test pads and 7 dropped pads named | two passes: pass 1 screen face (J1, 8 chips, stencil `ring-B_Paste.gbr`), pass 2 parts face (stencil `ring-F_Paste.gbr`); order and reason; how pass 1 parts stay on; inspection per face; the 12 pads | `ring-pos-*.csv`, `refs_diff.log` |
| 5 | Step 3 | "board's under face" (2 places) | "parts face" | microphones U5, U6 are in `ring-pos-front.csv` |
| 6 | Step 4 | cleans the under face round 15 test pads and ribbon lands | cleans both faces: pads on the screen face, ribbon lands on the parts face | `placement-final.csv:79,80,87` |
| 7 | Step 5 | jig touches the under face; pads TP2 etc. | jig touches both faces; the 12 pads, grid, signal of each; DBG_RX pad no longer named; After rewritten | `placement-final.csv:80,87-98`, `netlist.csv:18,116,189,196,253,255,257,259,261,267,269,319`, `screen-cable-study.md:205` |
| 8 | Step 15 (whole step) | foam frame on the top face, tail round the hand end into J1 on the under face | screen turned 180, cable route, J1 entry (opening +X, contacts up, contact 1 on +Y), lever, no foam frame, clearances, 14 contacts, checks | `screen-cable-study.md:166-186,205-211`, `wiring-review.md:23`, `product-wiring.csv:41-54` |
| 9 | Step 16 | "board's under face", "under face up" | "parts face", "parts face up" | ribbon lands are on F (`placement-final.csv:79,80`) |
| 10 | Step 17 Locate and After | stack of the 3.20 mm block; "under face, test pads and ribbon joints closed" | stack kept with a note that the board-to-panel space is 1.07 mm; After names both faces | `screen-cable-study.md:243` |
| 11 | Step 27 After | SHPHLD on TP19 "under the board" | on the screen face under the panel | `netlist.csv:253` |
| 12 | Conflict K-A1 | test pads on the populated under face, facing the floor | 12 pads on the screen face, cable over them from step 15 | `placement-final.csv:87-98`, `screen-cable-study.md:205` |
| 13 | Conflict K-A6 | "on the under face" | "on the parts face" | same |
| 14 | Section 5 row Foam FOAM1 | outline closed all round, fixed | material fixed; shape open | `screen-cable-study.md:207` |

## Search of the whole file (bar 4), after the edits

Terms "under face", "TOP face", "one side", "bare", "J1", "test pad", "foam": command `grep -n -i "under face\|top face\|TP2\b\|TP8\|15 test"` leaves 3 hits, each kept: line 21 (the definition of the old name, on purpose), line 257 (step 22, "the screen's top face": the lit face of the screen, not a board face), line 326 (K-A9, "ANT1 ... off the board", unrelated). "bare" stays in step 1 and its title: it means the unpopulated board. "one side" no longer occurs. J1 in steps 16 and 17 and in K-A rows is consistent with step 15. "foam" in steps 3, 12 (microphone gasket foam) is a different part and stays.

## Evidence

- `check_assembly.py` before: `guide-fix-work/base-check_assembly.log`; after: `guide-fix-work/check_assembly.final.log`, last lines `RESULT PASS` then `exit 0` (232 citations open; 28 steps).
- `check_docs.py` before: `guide-fix-work/base-check_docs.log`; after: `guide-fix-work/check_docs.final.log`, last lines `RESULT PASS` then `exit 0`.
- No check was changed or weakened. No check expected a single reflow.
- Stencil openings: `guide-fix-work/paste_count.log`: `ring-B_Paste.gbr` has 12 flashes of the 0.80 mm round aperture D10, at the test pad positions.

## For the lead (open, not decided in the guide)

1. Order of the two solder passes (screen face first, parts face second) and how pass 1 parts stay on: my choice by the standard small-part rule, written as [PROPOSED]. Confirm or change. Also open: the number of reflows J1 and the 0201 parts accept (no file cited).
2. Stencil: the delivered `ring-B_Paste.gbr` has apertures at the 12 test pads; the guide says the stencil maker closes them. The board owner may change the file instead.
3. Figures that wait for the taller block's inside model (written in the guide as "confirmed by the inside model of the taller block"): clearances 0.370, 0.400, 0.500, 0.050 mm (step 15 Locate); the fingertip end pocket X 13.725 to 14.165, Y +-6.40 (step 15 Before; step 10, outside my files, does not list it); the board-to-panel space 1.07 mm (step 17 Locate).
4. The block's outside height is not written in the guide. The stack line of step 17 (floor to glass, 3.20 mm block) is left as it was; it is the 3.20 mm stack.
5. Fold inner radius 0.30 mm is the study's start value; the maker gives none (study line 100). Measure on a real module.
6. Foam FOAM1: the study says only that no frame can stay and any spacer must leave X -4.8 to +14.2 open across Y +-6.4. Whether a spacer stays is open; the guide places none.
7. Continuity check of the 14 contacts: a test pad exists for 4 only (contact 5 on TP17, contacts 13 to 15 on TP18). The guide measures TP17 to TP18 (no short) and leaves the other 10 to T-SCREEN at step 18. A better measurement needs a pad or a point on the board that no file gives.
8. The jig touches both faces (pads on the screen face, J_BAND_B lands on the parts face, as the old step 5 already required the lands): written as [PROPOSED]; the jig maker must be told.
9. Stale text outside my files: `design/mfg/specs/main-board.md:6` ("top faces the screen", "15 flat test pads"; 12 now), `design/ecad/ring/pcb/board-notes.md:53` area (old round 2 notes), step 1 Before of the guide (it says no track is drawn; I left it, it is not part of the faults), `design/architecture.md:426` ("one side populated"). Steps 10 to 14 and 19 to 28 are unchanged except the single word change in step 27 (item 11).
10. Contact 1 on the +Y side: taken from `wiring-review.md:23` (the reviewer's check of J1 pad coordinates); the maker drawing was not re-read by me.

questions_for_owner: none

RESULT: done, assembly.md now describes the two-face board (two solder passes, 12 test pads on the screen face) and the screen turned 180 degrees into J1 on the screen face with no foam frame, check_assembly.py and check_docs.py both end RESULT PASS.
