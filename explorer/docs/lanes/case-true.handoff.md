# Handoff: case-true (the Case screen shows the true case with every part)

Owner, 2026-11-13: "You need to make sure we have the true case with everything". No browser of any kind was opened (owner's rule). The screen is built and seen by nobody until the owner opens http://localhost:8790/case. The dev server (pid 36469) was not touched. Agent file's `REF/*` folder does not exist in this checkout: built from the documents named in the brief.

## What I built
- `collector/extract/case_links.py` (new helper of case.py): reads the parts list, the solids' names, the two case board files' footprints, `case_params.json` (file time) and the row "block height 4.17 mm: what follows" of `design/wiring/lead-decisions.md`. Rules link a solid to its line(s): R0 reference token in the name (range-aware), R1 own part name in back quotes in the line's cells, R2 file name in the source cell, R3 maker part number, R4 child of another solid, R5 words of the function (head words first). A line of quantity 0 is never linked. Every line gets exactly one class: solid, board, not-fitted, no-solid (reason from its own cells). No case value in app source.
- `collector/extract/case.py`: nodes take their ids from the rules; adds `lines`, `counts`, `unlinked_nodes`, `boards`, `model`, `refit` to `case/index.json`. `contract/schema/case.schema.json` + `src/contract/records.ts` (regenerated) carry them as optional fields.
- App (`src/routes/case/`): `model.ts` (counts line, class words, solid/board lookups; solid hover names now come from the solid's own first line), `BoardParts.tsx` (parts of a board, each opening the existing part card, "Open this board" to `/board?board=<picker>`), `Honest.tsx` (model file and time, the design's refit sentence with file and line), `PartsList.tsx` (class tag per row), `index.tsx`, `case.css` (a few rules in the existing tokens). Same layout and style.
- `collector/lib/casecheck.py` (checks the tests use). Docs: CONTRACT.md section 16 and the check range case-true, DATA-MAP.md, SOURCE-CONTRACT.md, surfaces/case.md, TEST-PLAN.md.

## The data (from `npm run collect`, built 11:42)
Counts line quoted from the data: **90 parts-list lines: 25 in the 3D model, 61 on the boards, 1 not fitted, 3 without a solid** (25 + 61 + 1 + 3 = 90). Solids linked: **40 of 40** (0 without a parts-list line). The 3 lines without a solid: MECH6 (screws), MECH14 (marking field, "feature of the bottom plate"), MECH15 (thumb dimple, "feature of the lid"). Boards: main 84 footprints, pins 10, each with its solid (`main_board`, `pin_board_pcb2`) and picker id (`case-main`, `case-pins`). Model source shown: `design/case/out/case_params.json`, file time 2026-11-13 09:15. Refit sentence shown: the decision cell of lead-decisions.md line 65 (names the 4.17 mm block and "case fit" among the work that follows; "Until each is done its files describe the 3.20 mm block"); the app shows it as read.

## Open this to see it: http://localhost:8790/case
- Under "Parts of the case": the counts line, one tag per row (3D, case main board, case pin board, not fitted, no solid).
- Click a solid on the stage (any of 40): its part card opens. Click the main board solid: the card of "main board" opens and "Parts on this board: case main board · 84" appears with "Open this board"; each part opens its card. Click a glide, shell, lid, liner: their own line and the class "3D".
- At the bottom: "Model: design/case/out/case_params.json, file time ..." and "From the design files: ..." with the refit sentence.
- Not shown: nothing is shown about the case's real refit state beyond the design's own sentence; the 3D model is still the one fitted to the older ring (the design says its refit is not done). Whether the layout reads well is unseen.

## Checks (command, last line)
| command | last line |
|---|---|
| `npm run collect` | `collector: d56edbd -> .../explorer/public/data  ok 13` (0 unparsed; one earlier run read `ok 12 unparsed 1` because another job deleted a temp file under design/ecad/case/pcb/evidence during the run; rerun clean) |
| `npm run typecheck` | no output, exit 0 |
| `npm run check:types` | `types fresh: 32 declarations` |
| `npm run check:docs` | `check-contract-doc: ok (34 lane check ranges, 9 constants)` |
| `npm run guard` | `guard-no-ring-facts: clean` |
| `npm run test:unit` | `Test Files  35 passed (35)` / `Tests  253 passed (253)` |
| `.venv-pytest/bin/pytest -q collector/tests/collector-case` | `21 passed in 5.20s` |
| `npm run test:collector` (whole) | `4 failed, 257 passed in 259.19s (0:04:19)` |
| `test_C03_live_folder` alone, after the first suite run | `1 failed` (design/ecad/case/additions.csv grew: 2126 in the data against 2431 on disk); after a fresh `npm run collect`: `1 passed in 103.02s` |

The other 3 failures of the whole run are outside my files and come from design files that changed during the day: `collector-wiring::test_not_drawn_joints_are_shown_open` (connections.md has no row that starts "NOT DRAWN" now), `part-notes::test_every_ring_line_covered` and `test_generator_reproduces_wording` (ring TP lines no longer in bom.csv). Not rerun after the fresh collect; none touches the case.

## TESTS (each line of the brief)
- Every one of the 40 solids is in the data: `test_links.py::test_every_one_of_the_40_solids_is_in_the_data`. Passed.
- Every one of the 90 lines has exactly one class; the class counts add up to 90: `test_every_line_of_the_parts_list_has_exactly_one_class_and_the_counts_add_up`. Passed.
- Lines without a solid at most 5 (today 3), solids without a line at most 2 (today 0): the bounds named in test_links.py (`LINES_WITHOUT_SOLID_BOUND`, `SOLIDS_WITHOUT_LINE_BOUND`).
- Every linked id exists in the parts record: `test_every_linked_id_exists_in_the_parts_record`. Passed.
- Red first, kept broken fixtures in `collector/tests/collector-case/fixtures/` (`RING_EXPLORER_BROKEN=<fixture>` makes the same real-data test read it; seen red 2026-11-13):
  - `line-removed` (MECH6 out of the mapping): `E ... 'case:MECH6: 0 entries in the record, not 1'` and the sum 89.
  - `matches-nothing` (a solid with no line counted as linked): `E ... "solid 'zz_nothing' links to nothing and is not listed as without a parts-list line"`.
  - `qty0-fitted` (PA1-PA4 classed solid): `E ... 'case:PA1-PA4: class solid, but no solid holds its id'` and `quantity 0 but class 'solid'`.
  - The same defects are flagged from inside the suite by `test_checker_flags_*`, so the suite stays green.
- App unit tests `src/routes/case/case.test.tsx` (case-true-C01..C13): counts line (C01), class words (C03), board parts list and "Open this board" (C05, C06), model and refit lines (C07), the click from a solid to its card: every one of the 40 solids of the real bundle opens a line of the parts record (C10), counts line and class on every row on the real bundle (C11), main board click offers its 84 parts and a part opens its card (C12), a glide shows class 3D (C13). Mutations seen red and restored: countsLine order (C01), nodeNames (C04), classWords (C03, C11).
- Not run, by the owner's rule: any browser test, `npm run journeys`, `npm run checks`. jsdom does not draw: layout, the look of the new tags and whether the stage click works with the real 3D are unproven.

## Gaps and notes
- `case_links.py` is about 250 lines (above the 120-line guideline of my agent file; board.py is the same size). `guard.sh structural` is not in this checkout, so it was not run.
- The tag "3D" and the board titles are words of the screen; the board titles come from the Board picker's own list (`boards.GROUPS`).
- SPEC.md row (for the lead to write): status `built, not seen`; evidence `docs/lanes/case-true.handoff.md; collector/extract/case_links.py; collector/tests/collector-case (21 passed); src/routes/case/case.test.tsx (253 unit tests passed)`.
- The model is fitted to the ring as it was before 13 November; this change does not refit it.

questions_for_owner: none

RESULT: done, the case data links 40 of 40 solids and places all 90 parts-list lines (25 in the 3D model, 61 on the boards, 1 not fitted, 3 without a solid) and the Case screen shows them with the boards' parts, built and unit-tested but seen by nobody; 3 other collector tests fail on design files that changed outside this lane.

## Follow-up: the 3 failing collector tests (lead's request, 2026-11-13 afternoon)

### (a) collector-wiring: joints "stated in text only"
- Design change found: `design/wiring/connections.md` has no "NOT DRAWN" cell any more. Today only R16's "Drawn?" cell begins "Stated in text only". The Count line (line 71) says "R10, R15 and R16 are stated in text only", but the cells of R10 ("Specified and landed") and R15 ("Each end is drawn in its own files ...") do not say so, and product-wiring.csv agrees with the cells (R10 and R15 lines are `specified and landed`).
- Followed the file's cells: `collector/extract/wiring.py` `drawn_state()`: `not-drawn`, `text-only` (cell begins "Stated in text only") or `drawn`; schema enum and `src/contract/records.ts` regenerated; the screens treat both non-drawn states as open, with their own words ("Stated in text only: no design file draws it."; list cell "text only"; count line "N not drawn in a design file").
- Tests: `test_joints_not_drawn_or_stated_in_text_only_are_shown_open` (the file's cells read separately by `wiringcheck.open_cells`), kept broken fixture `fixtures/text-only-shown-drawn` (R16 shown drawn): `E ... 'R16: the file says it is not drawn or stated in text only, shown as drawn'`, and `test_checker_flags_a_text_only_joint_shown_as_drawn`.
- DESIGN FAULT NOT BENT: `test_the_joints_the_count_line_names_equal_the_joints_shown_open` compares the joints the Count line names (R10, R15, R16) with the joints shown open (R16). It is kept as `xfail(strict=True)` with the reason in its mark: it fails today on the design's two disagreeing statements and turns into a visible failure when the file is made consistent (remove the mark then). Owner or the design lane should make the Count line and the cells say the same.
- Conductors per joint (done, one line of text in the existing detail panel, no new element): `connections[].conductors` = {complete, total} from product-wiring.csv by its `joint` column (e.g. R3: 10 of 10, R13: 14 of 14); the panel's state line adds "N of M conductors complete". R16 has no conductor line (carrier none): no text. The two "complete" states are compared by a test with `COMPLETE` of design/wiring/build_wiring.py. Test `test_each_joint_shows_its_conductors_from_product_wiring_csv_and_complete_means_what_build_wiring_says`; unit test design-sync-C20 (text-only words and the conductors line).

### (b) part-notes
- Design change: `design/bom.csv` test-pad line is now TP1, TP3, TP4, TP5, TP6, TP12, TP14, TP15 (+ TP17 to TP19, TP21); TP8, TP9, TP11 no longer exist.
- Regenerated with `python3 -I collector/tests/part-notes/gen_notes.py`: `content/part-notes.json` 148 to 145 notes (the three are gone, nothing added); parts without a note, said not invented: C25, C89, FRM1, LT1, RC1 (unchanged `NO_NOTE_YET`). `collector/tests/part-notes`: `22 passed`.

### Checks (command, last line)
| command | last line |
|---|---|
| `npm run collect` | `collector: 7f9fd03 -> .../explorer/public/data  ok 13` (0 unparsed) |
| `npm run test:collector` (whole, background, exit file 0) | `263 passed, 1 xfailed in 239.81s (0:03:59)` |
| `npm run test:unit` | `Test Files  35 passed (35)` / `Tests  254 passed (254)` |
| `npm run typecheck` | no output, exit 0 |
| `npm run check:types` | `types fresh: 32 declarations` |
| `npm run check:docs` | `check-contract-doc: ok (34 lane check ranges, 9 constants)` |
| `npm run guard` | `guard-no-ring-facts: clean` |

Not run, by the owner's rule: any browser test. The new text in the connection panel is unseen.

questions_for_owner: Should the Count line of design/wiring/connections.md name R10, R15 and R16 as "stated in text only", or only R16? The cells and product-wiring.csv say only R16; the explorer follows the cells.

RESULT: done, the 3 failing collector tests follow the design (wiring cells and notes) and the whole suite ends `263 passed, 1 xfailed`; the one xfail is a kept strict test of a design inconsistency (Count line names R10, R15, R16; cells say only R16), with the conductor count per joint added to the detail panel.

## Follow-up 2: the xfail removed (lead corrected line 71 of connections.md)
- Line 71 now says every joint is drawn or specified "except R16, which is stated in text only". `wiring.stated_open()` reads this wording and the earlier "R10, R15 and R16 are stated in text only"; `test_the_joints_the_count_line_names_equal_the_joints_shown_open` is a normal test now and passes (open set R16 = the Count line's R16). New tests: `test_reader_reads_both_wordings_of_the_count_line`, `test_checker_flags_a_count_line_that_names_a_joint_the_map_shows_drawn` (kept fixture `text-only-shown-drawn`).
- `npm run collect`: `collector: 51c76fd -> .../explorer/public/data  ok 13`. `.venv-pytest/bin/pytest -q collector/tests/collector-wiring`: `13 passed in 21.11s`. Unit tests: 254 passed (35 files). typecheck, check:docs, guard pass. The whole collector suite was not rerun after this change (only collector-wiring was).

questions_for_owner: none

RESULT: done, the strict xfail is gone and the count-line test passes on the corrected wording; collector-wiring 13 passed, 254 unit tests passed, collect 0 unparsed.
