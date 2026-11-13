# Handoff: design-sync (readers and tests follow the design files of 13 November)

## Each failure traced to its design line

1. `parts` unparsed, collector-parts C01.
   - File: `design/case/case-bom.csv`, row `PA1-PA4` (csv line 78 of the file; the reader counts 69 rows+lines of multi-line cells).
   - New text: quantity `0`, function "history only, NOT fitted: Mill-Max 0981 spring pin, the first P1-P4 (C2); it does not fit: flange 2.11 mm against a 1.60 mm pad pitch ...". Old reader: `quantity 0 is below 1` made the whole record unparsed.
   - Change: `collector/extract/parts.py` reads quantity 0 (still refuses a negative or non-number); `contract/schema/parts.schema.json` quantity minimum 0; `src/contract/records.ts` regenerated; `PartCard.tsx` shows "Not fitted (history only)"; CONTRACT.md section 2 says it. The line counts 0 parts.
   - Red first (kept): `collector-parts/test_parts.py` parametrized case `{"qty": "-1"}` is refused with its line; `test_C02_a_history_line_with_quantity_0_is_kept_and_counts_no_part` fails on the old reader (unparsed). PartCard test `part-card-C10`.
2. `firmware-rules` unparsed, collector-behaviour C06.
   - File: `design/firmware.md` section 3.2, now "### 3.2 Recording sign on the screen (architecture 17.30)", line 339: "**No recording light:** removed in v7 ... The sign that a recording runs is the screen". Old text (the reader looked for it): "exactly while VDD_MIC is on".
   - Change: `collector/extract/behaviour.py` `_light` reads the "No recording light" line and gives `on_where_microphones_on: false` with that sentence; it still reads the old sentence as true; a section with neither is refused (named).
   - Red first (kept): `test_C04b_light_removed_in_the_design_reads_as_no_light`; `test_C04c_a_section_with_neither_statement_is_refused`.
3. part-notes (8 tests): `design/bom.csv` changed after `content/part-notes.json` was written.
   - Notes whose part no longer exists, now removed: ring LED1, R41, LG1, LP1, Q2 (the recording light, removed in v7, architecture 17.30) and ring TP2, TP7, TP10, TP13, TP22 (test pads the parts list no longer holds; TP17 and TP21 are now covered by the test-pad note of TP1).
   - Parts without a note (said, not invented; `NO_NOTE_YET` in test_part_notes.py): ring C25, C89, FRM1, LT1, RC1.
   - Case model objects the case model no longer has, dropped from the notes' `model_names`: J1_usb4105, L1_1uH, L2_0u47, LED1, U1_esp32s3_mini1, U2_bq25895, U3_tps63802, U4_zdsd64g, U5_tps2553 (`design/case/out/case_params.json` of 13 November 05:55).
   - Change: `gen_notes.py` (groups of removed parts out; lines without a group and missing model objects reported instead of asserted), regenerated `content/part-notes.json` (148 notes), tests follow. Red first: `test_mutation_note_for_a_part_listed_as_without_note_is_named`; the existing mutation tests stay.

No defect in a design file was found; no test was bent to hide one.

## Commands

| command | result |
|---|---|
| `npm run collect` | `collector: 4e1f237 -> .../explorer/public/data  ok 13` (0 unparsed) |
| `npm run typecheck`, `check:types` (`types fresh: 32 declarations`), `check:docs` (`check-contract-doc: ok (33 lane check ranges, 9 constants)`), `guard` (`guard-no-ring-facts: clean`) | pass |
| `npm run test:unit` | `Test Files  34 passed (34)`, `Tests  242 passed (242)` |
| `npm run test:collector` | `1 failed, 247 passed in 197.74s (0:03:17)` (exit 1). The one failure: `collector-parts/test_files.py::test_C03_live_folder`, `AssertionError: design/sim/antenna/results/ledger_round2.csv` with `5676 == 5814` (size in the data against size on disk). Cause: another helper appends to that file while it runs simulations, so it grew between the data build and the test; not a reader defect. Rerun of that one test alone: `1 passed in 53.73s`. Neither the test nor the reader was changed for it. |

## Behaviour screen and the light (for the lead)

- `src/engine/behaviour/engine.test.ts` line 117 now expects the record's own `light_rule` value (false today); engine tests: 7 passed.
- The Behaviour screen, per the lead's ruling: `src/routes/behaviour/Readout.tsx` draws the "Light" row (and its lamp) only when `light_rule.on_where_microphones_on` is true; `src/routes/behaviour/index.tsx` passes `light` to the 3D stage only then. With the record at false nothing replaces them. Unit tests `src/routes/behaviour/__tests__/readout.test.tsx` (design-sync-C10 false: no row, no lamp, seen red when the row was forced on; design-sync-C11 true: row drawn and follows the state). The stage hand-over is a one-line condition and has no test of its own.

## Open

- Nothing.

questions_for_owner: none

RESULT: done, `npm run collect` ends with 0 unparsed and the collector suite ends with 247 passed and 1 failed (test_C03_live_folder, a file another helper grew during the run; it passes alone), unit tests 242 passed.
