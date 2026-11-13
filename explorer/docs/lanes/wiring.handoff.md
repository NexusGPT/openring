# Handoff: wiring (lanes wiring-data, then wiring-screens)

Owner's ask, 2026-11-13: "you need to do the wiring on the ring explorer"; card answer "In the two existing screens, same look (Recommended)". Electronics gains a connection map; Board becomes a board picker with the copper layers. L1 Stage and S1 Gallery unchanged. No browser of any kind was opened: the screens are built and not seen by anyone until the owner opens them.

## What to open (the dev server on http://localhost:8790 is the lead's, pid 36469; it was not touched and already serves the new code and the new data)

1. http://localhost:8790/electronics : scroll under the wiring diagram to "What is joined to what". Expect: a map of 19 boxes (5 boards with an ink border, 14 parts) and 21 lines, each with a small pill (R1 to R16, C1 to C6). Three pills are orange and their lines dashed (R10, R15, R16: no design file draws them). A "Map | List" switch. Click a pill (or a row of the list): below it, the two ends in the file's words, what it carries, how it is made, the rows from band-interface.md and board-notes.md (lands, lead cut length per ring size, wire cut lengths, ring pad to case pin), whether a design file draws it, and the files that prove it (links when the file is in the Files list). "Open this board" on a board end opens Board. Deep link: http://localhost:8790/electronics?conn=R15
2. http://localhost:8790/board : a picker above the plan with 5 buttons (ring main board, band circuit 1, band circuit 2, case main board, case pin board); a band circuit adds a "Ring size" row (US 7 to 13). Under it: a state line (ring board today: "not finished: 242 connections open, 138 violations", orange, with the date and time of the board file and of the rules check), the outline with the parts of each face, buttons for each copper layer (Top copper, Inner copper 1, Inner copper 2, Bottom copper on the ring board), "All layers" and "No copper", and "Connections on this board" (each opens in Electronics). The other 16 boards say "routed and checked: 0 violations, 0 open connections". Deep link: http://localhost:8790/board?board=band-1&size=US%209&layer=all

What the owner may see that is not mine: the part cards of the Board screen say "no parts-list line" for every part, because the `parts` record is `unparsed` on the design as it is now (design/case/case-bom.csv:69: quantity 0 is below 1). `firmware-rules` is unparsed too (design/firmware.md: 3.2 does not state that the light is on exactly while the microphones are on). Both come from design files that changed after the last build; neither is in my lanes.

## Part 1: wiring-data (built)

- `collector/extract/boards.py` (helper of board.py): the boards list. 17 entries: ring board, 7 + 7 band circuits (US 7 to 13), case main and pin boards. Per entry: file, file time, outline, copper layers (one SVG per layer from `kicad-cli pcb export svg`, outline in each file), parts on each face (reference, value, position, size), state from `kicad-cli pcb drc --severity-all` (the report is saved as `board/<id>/drc.rpt`; the state numbers equal its count lines). A missing or unreadable board file still gets an entry with its state in words. Note when a board file is older than its netlist.
- `collector/extract/wiring.py` (helper of electronics.py): the connection map from `design/wiring/connections.md` Part 1: 21 connections, the count the file states ("Count: 21 joints"); R14 ("No joint") left out as the file leaves it out. Details from band-interface.md sections 2 and 6 and board-notes.md "Wiring table" and "Part g"; proof files from the "Stated at" cell through the file's key table.
- Schemas: optional `boards` in board-files, optional `connection_map` in electronics. The manifest still lists 13 records. `npm run gen:types` rewrote `src/contract/records.ts` (+159 lines).
- `collector/lib/wiringcheck.py`, `collector/lib/boardcheck.py`: the checks the tests use.
- Docs: CONTRACT.md section 15 (+ check id ranges wiring-data and wiring-screens, + the component map rows), DATA-MAP.md, SOURCE-CONTRACT.md.
- `npm run collect` ended with exit 0: `collector: 25c8741 -> .../explorer/public/data  ok 11  unparsed 2` (unparsed: parts, firmware-rules, both pre-existing, see above). Generated SVGs: 40 files, 1.2 MB in total (`public/data/board`).
- What is held in the collector as vocabulary, not read from files: the five picker groups with their plain-words descriptions (`GROUPS` in boards.py); the words of connections.md that name a board or a part (`NODE_RULES`) and how a joint is made (`HOW_RULES`) in wiring.py. Nothing of it is in app source.

## Part 2: wiring-screens (built)

- Electronics: `WiringSection.tsx` (map or list switch, count line, note), `ConnectionMap.tsx`, `ConnectionList.tsx`, `ConnectionDetail.tsx`, `src/components/wiring/wiringModel.ts` (layout and lookups, shared by both screens; moved there after the lane-dag change), styles appended to `electronics.css`. URL: `?conn=<id>`, `&cview=list`, `&cpart=<part id>`. The existing part card is reused for the part ends.
- Board: `BoardPicker.tsx`, `LayerToggle.tsx`, `StateLine.tsx`, `ConnectionsOfBoard.tsx`; `index.tsx`, `model.ts`, `PlanSvg.tsx` (several pictures stacked under the marks), `useBoard.ts`, `board.css`. URL: `?board=<group>&size=<US n>&layer=<id|all|none>` besides the existing `side`, `part`, `object`, `view`. Data without the list of boards falls back to the single ring plan with a sentence saying so.
- Honest states: no connection map in the data; a count that differs from the stated one; a connections.md that cannot be read; a board file missing, unreadable or older than its netlist; a layer without a picture (its button is off); a board with nothing to draw (the other boards still show).
- Docs: surfaces/electronics.md and board.md (change notes), TEST-PLAN.md (two new blocks).

## Checks (command, last line)

| command | last line |
|---|---|
| `npm run collect` | `collector: 25c8741 -> explorer/public/data  ok 11  unparsed 2` |
| `npm run typecheck` | no output, exit 0 |
| `npm run check:types` | `types fresh: 32 declarations` |
| `npm run check:docs` | `check-contract-doc: ok (32 lane check ranges, 9 constants)` |
| `npm run guard` | `guard-no-ring-facts: clean` |
| `npm run test:unit` | `Tests  238 passed \| 1 skipped (239)` (33 files) |
| `.venv-pytest/bin/pytest -q collector/tests/collector-wiring collector/tests/collector-boards` | `19 passed in 62.92s (0:01:02)` |
| `npm run test:collector` (whole suite) | `10 failed, 233 passed in 613.74s (0:10:13)` : the 10 failures are outside my files and caused by the design as it is today: collector-behaviour C06 (firmware-rules unparsed), collector-parts C01 (case-bom.csv:69 quantity 0), 8 tests of part-notes (parts list and notes out of step). None touches board or electronics. |

## TESTS

- Connection count equals the count the file states: `collector/tests/collector-wiring/test_wiring.py::test_count_equals_the_count_the_file_states` (also equals the joint rows of the table, read separately).
- Two ends and a source file that exists, per connection: `test_every_connection_has_two_ends_and_an_existing_source_file`. Joints named open equal the file's NOT DRAWN rows: `test_not_drawn_joints_are_shown_open`.
- Every board has its file and a copper layer picture that is not empty: `collector/tests/collector-boards/test_boards.py::test_every_board_has_its_file_and_a_copper_layer_picture_that_is_not_empty`. State numbers equal the count lines of the report: `test_each_state_equals_the_count_lines_of_its_rules_report`. The ring board is "not finished" while its report counts open connections: `test_the_ring_board_state_is_not_finished_while_its_report_counts_open_connections` and `test_a_board_whose_report_counts_open_connections_is_not_finished`. The list is 1 + 14 + 2: `test_the_list_holds_the_ring_board_14_band_circuits_and_2_case_boards`.
- Red first (kept broken fixtures; `RING_EXPLORER_BROKEN=<fixture>` makes the same real-data test read the fixture, and it fails; seen red on 2026-11-13):
  - `collector/tests/collector-wiring/fixtures/count-short/` : `E AssertionError ... '20 connections, the file states 21'`
  - `.../fixtures/one-end/` (a connection with one end removed): `E assert ['R4: 1 ends, not 2'] == []`
  - `.../fixtures/missing-source/`: `E ... "R2: source file 'design/wiring/not-there.md' does not exist"`
  - `collector/tests/collector-boards/fixtures/no-file/`: `E ... "x: board file 'design/ecad/ring/pcb/not-there.kicad_pcb' is not on disk"`
  - `.../fixtures/empty-layer/` (a 0-byte layer file): `E ... 'x: layer F.Cu has no picture file'`
  - `.../fixtures/state-vs-report/` (report says 3 open, state says 0): `E ... 'x: state says 0 violations and 0 open, the report says 0 and 3'`
  - `.../fixtures/ring-claims-routed/`: `E ... "x: its report counts 3 open connections but its state is 'routed-checked'"`
  - Inside the suite the `test_checker_flags_*` tests prove the same, so the suite stays green.
- App tests: `src/routes/electronics/wiring.test.tsx` (wiring-screens-C01..C13), `src/routes/board/board.test.tsx` (C20..C31), `src/routes/board/real-data.test.tsx` (C40..C45: the two screens rendered in jsdom on the real bundle read from `public/data` through a stubbed fetch; skipped when the bundle is not built). Mutations seen red and restored: `isOpen` (C04, C05, C06, C31), `layersShown` order (C24), the state words (C28, C29), the parallel numbering (C01).
- Not run, by the owner's rule: any browser test, `npm run journeys`, `npm run checks`. jsdom does not draw: how the screens look, where the map's boxes and pills fall on the real data, and whether the click targets work in a real browser are unproven until the owner opens them.

## Requirement row 15 of docs/SPEC.md (for the lead to write)

Status: `built, not seen`.
Evidence: `docs/lanes/wiring.handoff.md; explorer/collector/extract/boards.py, wiring.py; contract/schema/board-files.schema.json (boards), electronics.schema.json (connection_map); src/routes/electronics/ (WiringSection), src/routes/board/ (BoardPicker, StateLine); collector/tests/collector-wiring and collector-boards (19 passed); src/routes/{electronics,board}/*.test.tsx (238 unit tests passed); screens opened by nobody yet: http://localhost:8790/electronics and /board`.

## Deviations, things set aside, gaps

- The agent file's `REF/doctrine.md`, `REF/ux-canon.md`, `REF/frontend-architecture.md` could not be read: the project root with `.claude/skills/<platform>-app-builder/references` is not on this machine path (the explorer folder has no `.claude`). I built from the surface files, the PRD, DESIGN.md and the existing screens' own conventions. Rules there that I did not read could contradict something I did. The owner's rules named in the brief were followed over everything else.
- File size: `wiring.py` 339 lines and `boards.py` 282 lines exceed the 120-line module guideline of my agent file; existing extractors (board.py 334 lines) are the same size. `guard.sh structural` is not in this checkout, so it was not run.
- The map's layout is computed (levels from one end of the longest chain, the ring side first). On the real data it gives 9 levels and up to 4 boxes on a level; that is a prediction from numbers, not a look.
- `README.md` still says nothing about the two additions (owned by the contract lane).
- `docs/lane-dag.json` was not touched. The ring board file changes while its owner routes it: the numbers on the screen are those of the last `npm run collect` (138 violations, 242 open connections at 07:01 on 2026-11-13); run `npm run collect` again for newer ones.

questions_for_owner: none

Note: file list re-read after the lane-dag change; generated data went to public/data only, nothing to content/.

RESULT: done, the connection map (21 connections) and the board picker (17 boards with copper layers and rules-check states) are built from `npm run collect` data and served by the dev server on http://localhost:8790, with 19 collector tests, 238 unit tests and 7 red-first fixtures passing; no browser test run, 10 other collector tests fail on design files that changed outside these lanes.
