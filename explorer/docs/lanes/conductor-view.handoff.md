# Handoff: conductor-view

Owner's words, 2026-11-13: "the connexions and wiring is far from being 100% i see". Built: each connection of the Electronics screen lists its conductors one by one, read from design/wiring/product-wiring.csv. No browser of any kind was run: nobody has seen the screen.

## What the owner should see, and where

Open http://localhost:8790/electronics?conn=R3 (tab Wiring, scroll to "What is joined to what"; the dev server was not touched and already serves the new data).
- Above the map: the line "66 of 66 conductors complete · 1 line without a conductor" (read from the data, on today's file).
- Open any connection (click a pill or a list row). Under the facts and above "Files that prove it": a "Conductors" section. R3 lists 10 rows: id (W001...), signal, first terminal (part and pin), last terminal, carrier kind, state.
- A "Ring size" row of buttons (sizes from the file). Click a row: it opens to the board, face and join at each end, the carrier text, the state reason, the length for the chosen size (copper or cut, in mm), and the file with its line number.
- R16 (no conductor, capacitive sensing): no rows; under "No conductor" the reason from the file (W058) with its line.

## What changed

- Collector: `collector/extract/wiring.py` `conductor_data()`; checks `collector/lib/wiringcheck.py` `check_conductor_lines()`.
- Contract (optional fields, old bundles stay valid): `connection_map.connections[].conductor_lines[]`, `.no_conductor[]`, `connection_map.conductor_file`; `contract/schema/electronics.schema.json`; `src/contract/records.ts` regenerated.
- Screen: `src/routes/electronics/ConductorList.tsx` (new), `ConnectionDetail.tsx`, `WiringSection.tsx`, `electronics.css`; helpers in `src/components/wiring/wiringModel.ts`.
- Docs: CONTRACT.md (section 15 note, check ids conductor-view-C01..C99), DATA-MAP.md, SOURCE-CONTRACT.md, surfaces/electronics.md, TEST-PLAN.md (block conductor-view), DIGEST.md.
- Honest states in the screen: file missing or unreadable (the note, no count, no rows); a bundle without the fields ("not in the data yet"); a connection with no conductor line; a count of the connection that differs from the rows shown.
- Ring-size buttons are component state, not in the URL (Electronics has no ring-size choice of its own).

## TESTS

- added `collector/tests/collector-wiring/test_conductors.py` (8 tests): conductor count per connection equals the file; every shown value read back from its cited `{file, line}` (csv read on its own); 6+ conductors over copper, wire, spring pin, inside the part; no-conductor lines apart; whole-product count equals the file; `test_checker_flags_*` for the broken copies.
- added `src/routes/electronics/conductors.test.tsx` (13 tests, C01..C13) and `conductors.real.test.tsx` (3 tests, C20..C22, real bundle in jsdom).
- changed: none. Existing fixtures untouched (the new fields are optional).
- retired: none.
- Red first (times from `date`):
  - 16:23:48 collector, before the code: `1 failed in 21.71s` (`R3: 0 conductors shown, the file has 10`).
  - 16:28:38 unit, before the code: `Tests  11 failed | 1 passed (12)`.
  - Broken copies of the file (made from the real file at run time; both proofs kept), 16:38:01: `RING_EXPLORER_BROKEN_CSV=remove-line` -> `1 failed, 7 deselected in 20.31s`; `=change-terminal` -> `1 failed, 7 deselected in 22.38s` (message: `W010: first terminal pin shows 'reaches land J_BAND_A:5', line says 'reaches land J_BAND_A:5 X'`). The removed-line copy fails on W010 as well (its cited line no longer holds W010); the same two cases pass as `test_checker_flags_a_removed_line` and `test_checker_flags_a_changed_terminal`.
  - Mutations seen red then restored: `productCountWords` (C05), the count test `!==` to `<` (C13).

## Checks (last line of each run)

| command | last line |
|---|---|
| `npm run collect` (16:31) | `collector: c0d6a8c -> explorer/public/data  ok 13`, exit 0 |
| `npm run typecheck` | `> tsc --noEmit` (no output after it, exit 0) |
| `npm run check:types` | `types fresh: 32 declarations` |
| `npm run check:docs` | `check-contract-doc: ok (36 lane check ranges, 9 constants)` |
| `npm run guard` | `guard-no-ring-facts: clean` |
| `npm run test:unit` | `Tests  281 passed (281)` (40 files) |
| `.venv-pytest/bin/pytest -q collector/tests/collector-wiring` | `21 passed in 20.55s` |
| `npm run test:collector` (whole suite, background, exit code file `/tmp/cv-collector-all.exit` = 0) | `288 passed in 240.00s (0:04:00)` |

Data now: 66 conductor lines, 1 line without a conductor, 66 of 66 complete (`public/data/electronics.json`, `conductor_file`).

## Not done, not proven

- Nobody has looked at the layout: the 6-column row grid (one column per value; below 720 px three columns) is unseen. jsdom does not draw.
- `wiring.py` is now 436 lines and `wiringcheck.py` 189; both exceed the 120-line module guideline of the agent file (the same size class as the existing extractors). `guard.sh structural` is not in this checkout, so it was not run.
- The `REF/` doctrine files of the agent file are not on this machine path (as in the wiring handoff); built from the surface files, DESIGN.md and the existing Electronics conventions.

questions_for_owner: none

RESULT: done, each connection on Electronics lists its conductors from product-wiring.csv (66 of 66 complete today) with collector, unit and doc checks all green and no browser run.
