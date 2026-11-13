# Test plan: Ring Explorer

Mode: APP. Designed before any test or code exists (the explorer folder holds only `docs/`). Inputs read in full: PRD.md, JOURNEYS.md, DATA-MAP.md, DESIGN.md, CONSTRAINTS.md, BUILD-MODE.md, plan-notes.md, lane-dag.json (30 lanes), plan.json (61 todos, capture_manifest, gaps, unverified), lanes/contract.brief.md. I also read the real `design/bom.csv`, `design/status.json` and the file names under `design/` to pick real inputs.

Not found on this machine: `REF/test-contract.md` and a `test-designer.md` seat file. The `## TESTS` blocks use the columns of my dispatch (test id, risk row, type, real input, entry, visible assertion, red-first case, runner, budget). If the brief generator needs another column set, the blocks map one to one.

## Facts that shape the plan

- Owner-reported app bugs: **none yet.** The owner's complaints so far ("I hate all of them, they are not as slick as the ring I shared") are about the ring's look, not about this app. No regression test is invented. Rule for the first real report: a test in `tests/regression/<date>-<slug>.spec.ts` that is red on the parent commit of the fix, quoting the owner's words and the screen. No lane in `docs/lane-dag.json` owns that folder (see Conflicts K5).
- Hosting: none (LOCAL, `127.0.0.1` only). So there is no hosted journey. The "hosted-only" risk class is replaced by: the app serves from `127.0.0.1:8790` only, and nothing loads from the internet (R-10).
- Restart: the app holds no state (DATA-MAP `state-home: none`). The restart risk is "a restarted server or a rebuilt bundle serves different bytes or loses a deep link": tests contract-C09 and fixture-a3-C01.
- Store: no database. The store risk is the generated bundle and the part notes file (DATA-MAP). Data-home tests are the collector tests, the cross-record test fixture-a3-C03, and the rebuild test seams-C05.
- The design changes while the app is built. Journeys run on a frozen copy (commit 99dfb85 plus a copy of look C), approved by the owner. The live app shows the slim A4-draft design. So: **no journey assertion depends on a live design value**; lane checks on the live bundle compare the screen to the bundle file read by the test, never to a literal.
- Disk: 4.6 GB free. No test may download a second browser or create or keep a file over 20 MB (contract-C08).

## 1. Risk map

P0 = data lost or wrong, or sent to a person. P1 = something the owner needs is unreachable or broken. P2 = slow or cosmetic. "Seen by" is the test type that can SEE the failure the way the owner would.

| risk | class | what goes wrong, in the owner's terms | seen by |
|---|---|---|---|
| R-01 | P0 | A number or name on screen is not what the design files say (typed in app source, or misread by the collector). The owner decides on a wrong size, battery or part. | guard on app source; collector tests that read the value back from the source line; journeys with literals from JOURNEYS.md on the frozen copy |
| R-02 | P0 | A line of the parts list has no card, or its card shows a wrong order code, a code shown as a bare code ("12.2", "NEW-..."), or no plain words. The owner sends a wrong code to a partner. 77 lines today, grouped references like "U5, U6, U7, U8", a comma inside a quoted cell. | collector tests on the real bom.csv; a test that opens all 77 cards; journey J1.3, J4.3 |
| R-03 | P0 | The partner bundle or the CSV that leaves the app is incomplete, corrupt, contains `.venv` or a secret, or holds a path that escapes the project. Real trap: `design/case/out/parts/pin_P3_D+.step` (a plus sign in a file name); look C files of 24.7 MB and 21.6 MB. | zip read-back tests; download journeys J6.1 and J6.2 with hashes |
| R-04 | P0 | A source that is missing, unreadable, unparsed, or made for an older design (A3 against A4) is shown as current and fine. The owner reads old data as today's design. | collector tests with broken copies; one browser check per route on EMPTY and STALE bundles; journeys J3.2 |
| R-05 | P0 | An area tile says a state that is not in `design/status.json`, or the tile and the screen banner disagree, or an invented state word appears, or a missing file shows a state instead of "state unknown". | collector-state tests; seams-C04 against the real status.json; J3.1 |
| R-06 | P0 | One bad or half-written source file stops the whole collector, so the bundle is empty; or a collect run writes into `design/` (the app is read-only). | collector runner test; sha256 of `design/` before and after a collect |
| R-07 | P1 | The journeys pass or fail on the wrong data: the live design instead of the frozen copy, another process on the port, a fixture that drifts between builds. A green that proves nothing. | journey global setup identity check; fixture byte stability test |
| R-08 | P1 | The 3D stage is blank or wrong while the page looks fine: no render, a model that fails to load, parts that do not map, rotate/explode/pick that do nothing. Hooks like `window.__stage.ready` can be true on a blank canvas. | every 3D assertion pairs a hook with canvas pixels (before and after) |
| R-09 | P1 | A screen or part cannot be reached: a tab missing, a route that 404s on reload, a part more than 3 clicks from Home, a `?part=` link that does not survive reload. | shell checks; "all 77 cards in 3 clicks" test; journeys |
| R-10 | P1 | The app loads something from the internet, listens beyond this Mac, or serves a file outside the project (path traversal, symlink, `%2F`, `+` read as space). Constraints 2 and 9. | static scan of the build; offline browser run with every non-127.0.0.1 request aborted; server tests |
| R-11 | P1 | The virtual ring does not behave as `firmware.md` says (hold times, states, light, vibration) or the timings are typed in app source. | table-driven engine test over every row of the transition table; J5.1 to J5.3 |
| R-12 | P1 | The wiring diagram is missing or unreadable (KiCad export absent), an SVG runs script, or a block opens the wrong page or the wrong parts. | collector-electronics tests; svg-viewer script-inert test; J4.1 to J4.3 |
| R-13 | P1 | A rejected exterior is shown as current, or with no approved exterior the stage shows something other than "Plain black slab". Owner's answers of 2026-11-10: slab; rejected looks "Not in the app". | look checks with `status.json` variants; text scan of all 9 routes |
| R-14 | P1 | The same part, count or state reads differently on two screens. | seams tests |
| R-15 | P1 | The test system itself: a test folder no default runner loads; a test that opens a visible window or downloads a browser; a file over 20 MB. | runner canary contract-C07; config and size checks contract-C08 |
| R-16 | P2 | Too slow: first paint 1500 ms, interaction 100 ms, route read 300 ms cold and 100 ms warm (PRD `Perf-budget`). Frame time has no number: recorded only (plan gap G7). | smoke-perf |
| R-17 | P2 | The S1 Gallery look and the anti-references ("cluttered dashboard", "wall of text", "toy") are broken: shadows, radius, fonts, over 120 words in a panel, accessibility floor. | computed-style and word-count checks; axe floor. The taste of "slick" stays with the taste judge, see Uncovered risks |

## 2. Shared design (every block below relies on this)

**Data sets.**
- FIX: `tests/fixtures/bundle/`, built by `make-fixture.sh` from a `git archive` of commit 99dfb85 plus a frozen copy of look C (compressed to GLB_MAX_MB, never the 24.7 MB original). Journeys and cross-screen checks run on FIX, served on `127.0.0.1:8797`. FIX status.json carries at least one tile in each of the four state words. FIX has no approved exterior, so the stage shows "Plain black slab".
- EMPTY: an empty folder as bundle. STALE: FIX with manifest records edited to `stale` (basis A3, current A4) and `unparsed`. BROKEN: a temp copy of the FIX source with a file deleted, a file made unreadable, and a CSV cut at 40 % of its bytes. LIVE: `npm run collect` on the live slim design; assertions on LIVE are structure only.
- Helpers in `tests/support/` (contract lane): `serveBundle(dir)` starts a `127.0.0.1` server on a free port from 8798 up for non-FIX bundles; a pixel helper `pxFill(region)` and `pxDiff(a, b, region)`.

**Three oracles, so one wrong layer cannot hide behind another.** (1) Collector tests compare the bundle to the source file, reading the value back from the cited `{file, line}`. (2) Lane checks compare the screen to the bundle file the test reads itself. (3) Journeys compare the screen to the literal in JOURNEYS.md (30 x 20 x 9.5 mm, 135 mAh, 33.6 x 33.4 x 55.2 mm, 700 mAh, 6.3 minutes, 77 lines, 146 parts, BT1, U5, SW1) on FIX only.

**The act-removed pattern.** Every interaction test has the form: assert the "before" state, perform the owner's act, assert the "after" state and that after differs from before. With the act deleted, before equals after, so the test is red. Each journey row says what that act is.

**3D pairing.** A 3D assertion is a hook value (`window.__stage.*`) AND a canvas pixel check from the pixel helper: at least 2 % of the canvas differs from the background (not blank), and before/after pixel difference is at least 1 % for a move. A hook alone never counts.

**Red-first.** Journey specs and lane checks must be seen red with assertion failures (never import or syntax errors), then green. Journeys: red at scaffold, before any surface exists (journeys-a and journeys-b acceptance). Lane checks: red on the lane's fork point with the lane's source removed, plus the named mutation in the row, restored after. The builder's report quotes the last line of each red and green run.

**Runners (to be created by the contract lane; the canary in contract-C07 proves they load everything).**
- `PY` = `npm run test:py`: pytest over `collector/tests/**`, `tests/fixtures/checks/**`, `tests/seams/data/**`.
- `UN` = `npm run test:unit`: vitest over `src/**/__checks__/*.test.ts(x)`, with `vendor/**` excluded.
- `GD` = `npm run test:guard`: the no-ring-facts guard and the static offline scan.
- `PW` = `npm run test:pw`: headless Playwright, project "checks": `tests/checks/**`, `tests/seams/**`, `src/**/__checks__/**/*.pw.ts`.
- `npm test` runs PY, UN, GD, PW in order and exits non-zero if any fails. Budget 8 min.
- `JR` = `npm run journeys`: headless Playwright, project "journeys": `journeys/*.spec.ts` and `tests/smoke/**` (`-- J1` filters one journey, `-- smoke` the smoke set). Exits non-zero on failure. Budget 5 min for J1 to J7, 3 min for smoke.
- Headless only, hard-coded (CONSTRAINTS 1). The one installed Chromium is used; no script may run `playwright install`.

**Budgets used below.** pytest per lane folder 20 s unless stated; vitest per lane 15 s; a Playwright lane check file 60 s; a journey 40 s.

## 3. One row per journey step (JOURNEYS.md J1 to J7, 20 steps)

All journeys: runner `JR` (`npm run journeys -- J<n>`), FIX bundle on 8797, desktop 1512x982, each test starts from a fresh page load of Home and reaches its screen by the click path in the "entry" cell. Before every journey the global setup reads `/data/manifest.json` and stops the run unless `git_commit` starts with `99dfb85` (R-07). The testids below are placeholders; `docs/CONTRACT.md` fixes the grammar.

| step | test id | risk | type | real input | entry (click path) | visible assertion (works · fails) | red-first and act-removed | budget |
|---|---|---|---|---|---|---|---|---|
| J1.1 | J1#1 | R-01 R-08 R-04 | journey e2e | FIX built from commit 99dfb85; ring facts of that design (30 x 20 x 9.5 mm, 135 mAh) | type `127.0.0.1:8797/`; then drag the ring 200 px | Works: panel shows "30 x 20 x 9.5 mm" and "135 mAh" among 5 key numbers; 8 area tiles each with one pill from the vocabulary; label "Plain black slab" on the stage; canvas at least 2 % non-background and at least 1 % different after the drag, `azimuthDeg()` moved over 20 degrees. Fails: blank canvas; the text "Run npm run collect"; any console error | Red at scaffold. Mutation: drop the facts render line, numbers vanish, red. Act-removed: no drag, pixel diff 0, red | 30 s |
| J1.2 | J1#2 | R-08 | journey e2e | FIX `placements.json` layers from `placement.csv` (cover glass, screen, board, cell, housing) | Home, click tile "Inside", drag slider "open it up" from 0 to 1 | Works: `layerBoxes()` gaps at least EXPLODE_MIN_GAP_MM and canvas differs at least 2 % from the closed view; the layer list shows the 5 layers. A layer with no model is a text row. Fails: slider moves, picture unchanged | Mutation: explode offset times 0, red. Act-removed: slider untouched, gaps 0, red | 30 s |
| J1.3 | J1#3 | R-02 R-01 | journey e2e | FIX part BT1 (cell, 135 mAh, Grepow quote) and its note in `part-notes.json` | Inside, real mouse click on the cell at `screenPos('cell')` | Works: card shows "Battery cell", "Stores the energy", "Custom order", the numbers 4.6, 13, 25, "135 mAh", "quote from Grepow"; the maker part number is hidden until "Exact data" is opened; the cell is highlighted on the canvas (pixel diff around it). Fails: "no parts-list line for this object", another part's card, or no card | Mutation: unlink BT1 `model_names`, red. Act-removed: no click, no card, red | 30 s |
| J1.4 | J1#4 | R-03 R-10 | journey e2e | FIX BT1 source cell and the real file `design/datasheets/mic_infineon_im73d122v01_en.pdf` (U5); one FIX source that points outside the project (the real bom has absolute paths and https links) | Inside, click the cell, in the card click link "source" | Works: a new tab opens at a `/files/design/...` URL that answers 200 with a PDF or text body that is not an error page. For a source that is not served: the link is greyed, `aria-disabled`, shows the vocabulary reason, and no tab opens. An https source opens with `target=_blank` and is never fetched by the app. Fails: tab with 404 or empty page | Mutation: break the `/files/` route prefix, red. Act-removed: no click, no popup event, red | 30 s |
| J2.1 | J2#1 | R-13 R-08 | journey e2e | FIX `looks/` options A, B, C (frozen A3 copy; look C compressed) | Home, click tile "Look", drag one option | Works: 3 panels, each with its title, two-line thesis and "worse at" line from the bundle; the dragged option turns over 20 degrees with its canvas changing; the other two follow only if the visible "rotate together" switch is on. Fails: a blank panel for a missing option (it must show a labelled placeholder) | Mutation: render only options[0], red. Act-removed: no drag, azimuth unchanged, red | 40 s |
| J2.2 | J2#2 | R-13 R-08 | journey e2e | FIX `finishes.json` (4 finishes, frozen from `viewer.js:11-16`, incl. "Slate Titanium") | Look, click switch "finish", click "Slate Titanium" | Works: 4 finish buttons; body and band material colour equals the finish colour on all 3 options; the mean colour of each option's ring pixels moved toward that colour; `aria-pressed` on the active one. Fails: button pressed, ring unchanged | Mutation: apply finish to option 0 only, red. Act-removed: no click, colours unchanged, red | 30 s |
| J2.3 | J2#3 | R-08 | journey e2e | FIX look options | Look, click switch "view", click "on a finger" | Works: 4 views listed; `fingerVisible()` true on every option and the canvas differs at least 2 % from the three-quarter view. Fails: ring floats without a finger | Mutation: finger node hidden, red. Act-removed: red | 30 s |
| J3.1 | J3#1 | R-05 R-09 | journey e2e | FIX `areas.json` and FIX `status.json` (all four state words present) | type the address (or top bar "Home"), click the "Board" tile | Works: before the click, the 8 pills are the four vocabulary words as in `areas.json`; after it the URL is `/board` and tab "Board" is current. Fails: tile reads "state unknown" on FIX, or the click goes elsewhere | Mutation: swap two area ids in the tile map, red. Act-removed: no click, URL stays `/`, red | 20 s |
| J3.2 | J3#2 | R-04 R-01 | journey e2e | FIX `board.json` (not routed, outline 27.0 x 17.4 mm); the missing file `design/ecad/ring/ring.kicad_pcb` | Home, click tile "Board" | Works: a banner that says "not routed" and names `ring.kicad_pcb`; the plan shows one mark per placed part, as many as `board.json` lists, on both sides. Fails: a plan with no banner (looks ready to build) | Mutation: hide banner when `routed` is not true, red. Act-removed: no navigation, no banner, red | 30 s |
| J3.3 | J3#3 | R-05 R-01 | journey e2e | FIX `open.json` from architecture sections 12 and 13 (7 supplier requests, 5 bench tests, risks, dated decisions) | top bar "Open items", click chip "waiting on a supplier" | Works: before the click the list is longer; after it exactly 7 rows, each with a non-empty who and a non-empty "what to ask"; 4 group headings; decisions with dates newest first. Fails: list unchanged, a row with no who | Mutation: filter ignores the chip, red. Act-removed: no click, row count equals before, red | 20 s |
| J4.1 | J4#1 | R-12 R-04 | journey e2e | FIX `blocks.json` (7 blocks) and `schematic/` (8 SVG pages, real KiCad export of the A3 wiring) | Home, tile "Electronics", click block "Microphones" | Works: the viewer image loads the microphone page (`naturalWidth` above 0, crop at least 2 % non-blank) beside the block diagram, and the page file read by the test contains the text "U5". Fails: broken image icon; a PDF link shown instead when the SVG exists | Mutation: map block to the wrong page file, red. Act-removed: no click, viewer empty, red | 30 s |
| J4.2 | J4#2 | R-12 | journey e2e | FIX microphone page SVG; U5 position parsed from the SVG file by the test | Electronics, page list shows 8 pages, click zoom to 400 % centred on U5 | Works: scale 4.0 plus or minus 0.05; the crop around U5 differs from the 100 % crop and is at least 2 % non-blank; U5's text size times scale is at least 8 px. Fails: blank crop, scale stuck at 1.0 | Mutation: zoom buttons do nothing, red. Act-removed: scale 1.0, red | 30 s |
| J4.3 | J4#3 | R-02 R-09 | journey e2e | FIX `blocks.json` refs for the microphone page (U5 to U8) and `parts.json` | Electronics, click "parts of this page", click row U5 | Works: Parts opens with chip "page: Microphones" and only the lines whose refs sit on that page (count equals the oracle from `blocks.json`); the U5 card shows the microphone with IM73D122V01. Fails: all 77 lines shown | Mutation: ignore the page filter, red. Act-removed: red | 30 s |
| J5.1 | J5#1 | R-11 R-08 | journey e2e | FIX `behaviour.json` (from `firmware.md`: long press 1000 ms, motor M1 [80]) | Home, tile "Behaviour", mouse down on the record button, hold 1000 ms, release. Second run: the same hold on the button of the 3D ring | Works: state label "Recording", light `data-on` true and red-dominant pixels at the light on the ring, one vibration mark, the timer text changed between two reads 1.2 s apart. Both entry paths give the same result (owner answer "Both"). Fails: still "Standby" | Mutation: change engine threshold from 1000 to 1001, red. Act-removed: no hold, Standby, red | 40 s |
| J5.2 | J5#2 | R-11 | journey e2e | FIX `behaviour.json` (short press 40 to 600 ms) | Behaviour, in Recording, click the button for 200 ms | Works: highlight marks go from 0 to 1, state stays "Recording", timer keeps running. Fails: state leaves Recording, or no mark | Mutation: short press stops recording, red. Act-removed: marks stay 0, red | 30 s |
| J5.3 | J5#3 | R-11 | journey e2e | FIX `behaviour.json` (M2 [80,120,80]) | Behaviour, in Recording, hold the button 1000 ms | Works: "Standby", light off (no red pixels), 2 vibration marks added. Fails: stays Recording | Mutation: stop path skips the motor pattern, red. Act-removed: red | 30 s |
| J6.1 | J6#1 | R-03 | journey e2e | FIX `files.json` and `bundle.zip` (includes `design/bom.csv`, `design/architecture.md`, `design/case/out/parts/pin_P3_D+.step`) | top bar "Files", click "Download partner bundle" | Works: files grouped in 8 areas with size and date; a download event; file name ends `.zip`; size equals the bundle file; starts with bytes `PK`; `unzip -t` clean; the page lists as many entries as the zip holds; the plus-sign file is in the zip with the right bytes. Fails: HTML error page saved as zip; button disabled with "run npm run collect" while the zip exists | Mutation: serve the index page for `bundle.zip`, red. Act-removed: no click, no download event, red | 40 s |
| J6.2 | J6#2 | R-03 R-02 | journey e2e | FIX `design/bom.csv` of commit 99dfb85 (77 lines, quoted commas) | top bar "Parts", click "Export CSV" | Works: totals "77 lines" and "146 parts" before; download named `bom.csv`; sha256 equals the source file; parsing with a CSV reader gives 77 records. Fails: filtered or re-quoted export | Mutation: export the visible rows after a filter, red. Act-removed: red | 30 s |
| J7.1 | J7#1 | R-01 R-08 | journey e2e | FIX `case/` (33.6 x 33.4 x 55.2 mm, 700 mAh, 6.3 minutes per recorded hour) | Home, tile "Case", click "Open lid" | Works: facts read "33.6 x 33.4 x 55.2 mm", "700 mAh", "6.3 minutes per recorded hour"; after the click `nodeRotationDeg('lid')` is at least 90 within 1.5 s and the canvas differs at least 2 %; the ring node is visible inside the case box. Fails: "6.4", lid fixed | Mutation: lid rotation 0, red. Act-removed: lid closed, red | 30 s |
| J7.2 | J7#2 | R-02 R-08 | journey e2e | FIX case parts (pin_P1_VBUS, pin_P2_D-, pin_P3_D+, pin_P4_GND) | Case, real mouse click on the pins at `screenPos('pin_P1_VBUS')` | Works: card with "spring pins", "VBUS", "D-", "D+", "GND" (the plus and minus signs kept); pins highlighted by pixel diff. Fails: no card, or "D+" shown as "D " | Mutation: strip `+` in names, red. Act-removed: no click, no card, red | 30 s |

## 4. TESTS blocks, one per lane of docs/lane-dag.json

Common to every block: existing tests to prune = none (greenfield; see section 5). Test ids follow the contract grammar `<lane>-C01..C99`. Runner codes are those of section 2. Test files sit inside the lane's own `owns` paths.

## TESTS: contract
Test files: `collector/tests/contract/test_*.py`, `scripts/check-*.mjs`, `tests/support/*.selftest.ts`. Never `design/`.

| test id | risk row (class) | type | real input (captured from) | entry (click path / event) | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| contract-C01 | R-01 R-02 (P0) | contract (schema) | the 14 schemas; a `parts.json` made from real bom.csv rows U1, U2 and the grouped line "U5, U6, U7, U8" | `python collector/run.py --check-schemas` | Works: exit 0 and 14 schema names printed; `tsc --noEmit` has 0 "error TS". Fails: a `parts.json` whose line lacks `refs` makes the validator exit 1 | Mutation: make `refs` optional in the schema, the bad file passes, red | PY | 20 s |
| contract-C02 | R-06 (P0) | integration | a copy of the real `design/` (no `.venv`): `bom.csv` cut at 40 % of its bytes; a file with mode 000; a file deleted | `python collector/run.py` on each copy | Works: exit 0; only that record is `unparsed` or `missing` with the exception text in `message`; every other record unchanged. Fails: exit non-zero or an empty bundle | Mutation: let the runner re-raise, red. Act-removed: no bad input, the expected `unparsed` is absent, red | PY | 20 s |
| contract-C03 | R-06 (P0) | integration | the live `design/` folder (read only) | sha256 of every file under `design/` (skip `.venv`) before and after `npm run collect` | Works: identical lists, `git status --porcelain design/` unchanged. Fails: any change (the app is read-only, CONSTRAINTS 4) | Mutation: have the runner write a cache file into `design/`, red | PY | 30 s |
| contract-C04 | R-10 R-03 (P1) | integration | the running file server; real paths `design/datasheets/mic_infineon_im73d122v01_en.pdf` and `design/case/out/parts/pin_P3_D+.step`; the machine's LAN address | HTTP GETs on `/files/...` | Works: 200 with `application/pdf` for the PDF; the `+` file returns its exact bytes (sha equal to disk); `/files/..%2F..%2Fetc%2Fpasswd`, `/files/design/.venv/bin/python`, a symlink out of the tree and an absolute path all 404; connecting through the LAN address is refused; a second server on 8790 fails, it does not move port. Fails: any of these served | Mutation: decode `%2F` before the root check, traversal returns 200, red | PY | 20 s |
| contract-C05 | R-10 (P1) | static scan | `index.html` and `dist/**` after `npm run build` | `npm run test:guard` | Works: no `http(s)://` host other than `127.0.0.1` and no `@import url(`, `fonts.googleapis`, `cdn.` in emitted js, css, html. Fails: any hit names the file | Mutation: add `<link href="https://fonts.googleapis.com/...">`, red | GD | 30 s |
| contract-C06 | R-01 (P0) | unit (guard) | distinctive tokens taken from the FIX bundle AND the LIVE bundle (part refs `BT1`, `U5`, `SW1`; `135 mAh`; `30 x 20 x 9.5`; state words; `Battery cell`) | guard over `explorer/src` (not `tests/`, not `content/`) | Works: exit 0 on a clean tree. Fails: a line `const x = 'BT1'` exits 1 naming file and token. Also catches a number-unit literal such as `'135 mAh'` | Mutation: add that line, red; remove it, green. Allowed words come only from `src/contract/vocabulary.ts` | GD | 15 s |
| contract-C07 | R-15 (P1) | runner canary | every test-like file in the repo | `node scripts/check-runners.mjs` (part of `npm test`) | Works: each test file is listed by exactly one of pytest, vitest, Playwright "checks", Playwright "journeys"; exit 0. Fails: it names each orphan file | Mutation: add `tests/orphan/x.spec.ts`, red. Also red if `vendor/**` tests are collected | GD | 20 s |
| contract-C08 | R-15 (P1) | config and size scan | `tests/playwright.config.ts`, `package.json` scripts, `git ls-files` plus untracked files of `explorer/` | `npm run test:guard` | Works: `headless: true` is fixed (an env override cannot turn it off); no script contains `playwright install`; no file in `explorer/` over 20 MB (the 24.7 MB look C `ring.glb` must not be here); one `node_modules`. Fails: names the offender | Mutation: create a 21 MB file, red; set `headless:false`, red | GD | 20 s |
| contract-C09 | R-09 (P1) | restart | the server and the FIX bundle | start, GET `/data/parts.json` and `/inside?part=ring%3ABT1`, kill by pid, start again, GET again | Works: same bytes and same status both times, no state carried. Fails: different bytes or 404 on the deep link after restart | Mutation: cache the bundle in memory with a timestamp header, red | PY | 20 s |
| contract-C10 | R-04 R-06 (P0) | integration | a git repo copy with a known HEAD | `python collector/run.py` with zero extractors | Works: exit 0; manifest lists 13 records `missing`; `git_commit` equals `git rev-parse HEAD`. Fails: another commit or a crash | Mutation: hard-code a commit string, red | PY | 15 s |
| contract-C11 | R-07 (P1) | journey setup | server started on a bundle that is not FIX (the LIVE bundle) | `npm run journeys -- J1` | Works: the run stops at once with the message "journey run is not on the frozen copy 99dfb85" and exits non-zero; with FIX it proceeds. Also stops if the port answers with another manifest. Fails: runs on live data | Mutation: remove the setup check, the run proceeds on LIVE, red | JR | 15 s |
| contract-C12 | R-08 R-17 (P1) | self-test of the test tool | two real canvas screenshots; one pair identical, one pair with a 2 % painted square | pixel helper self-test | Works: identical gives 0 %, the painted square gives at least 2 % and below 3 %. Fails: a helper that returns 0 or 100 always | Mutation: helper returns 0, red | UN | 10 s |

## TESTS: shell
Test files: `src/app/__checks__/*.test.tsx` (UN) and `src/app/__checks__/*.pw.ts` (PW).

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| shell-C01 | R-04 (P0) | browser check | EMPTY bundle; STALE bundle (FIX with firmware and parts records `stale`, basis A3, current A4) | open each of the 9 routes | Works: each route shows the banner whose text is a `vocabulary.ts` entry; the side panel text is not empty; on STALE the line "Made for design A3; the design is now A4. Being redone." shows AND the content is still on screen, dimmed, not hidden; 0 console errors. Fails: blank page, hidden content, raw error | Red at fork point (no routes). Mutation: hide content when stale, red | PW | 45 s |
| shell-C02 | R-09 (P1) | browser check | FIX | from Home click each of the 9 tabs and "Files"; reload on each route; open `/inside?part=ring%3ABT1` directly | Works: URL path changes and `aria-current` moves; reload returns the same page (no 404); the deep link keeps its part. Fails: a tab with no route, 404 on reload | Mutation: remove the "Files" link, red | PW | 40 s |
| shell-C03 | R-08 (P1) | browser check | FIX; viewports 1512x982 and 1280x800 | Home, Inside, Parts in turn | Works: the stage canvas keeps one element (`data-stage-id` equal, `window.__stage.contexts === 1`) and stays at least 2 % non-blank; stage share of width is 0.608 plus or minus 0.02; no page scroll on Home. Fails: canvas recreated per route, or Home scrolls | Mutation: mount a stage per route, red | PW | 40 s |
| shell-C04 | R-04 (P0) | browser check | FIX manifest; the same manifest with `git_dirty: true` | Home | Works: the stamp equals `built_at` and the first 7 characters of `git_commit`; dirty adds "files changed since". Fails: a fixed string or time | Mutation: render `new Date()`, red | PW | 20 s |
| shell-C05 | R-17 (P2) | unit and scan | `src/styles/**` | `npm test` | Works: hex colours appear only in `tokens.css`; brand text font includes "Libre Caslon Text"; panels have `box-shadow: none` and radius 0 (pills 999px). Fails: names the rule | Mutation: add a shadow to a panel, red | UN | 15 s |
| shell-C06 | R-08 (P2) | browser check | FIX | Electronics, click `panel-expand`, then Escape | Works: panel at least 0.9 of main width, then 0.392 plus or minus 0.02; azimuth unchanged. Fails: stage resets rotation | Mutation: remount the stage on expand, red | PW | 25 s |

## TESTS: stage
Test files: `src/stage/__checks__/stage.test.ts` (UN), `src/stage/__checks__/stage.pw.ts` against `src/stage/harness.html` (PW).

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| stage-C01 | R-08 (P1) | browser check | the real `design/look/viewer/sample/out/ring.glb`, and the FIX `internals.glb` | harness page | Works: canvas at least 2 % differs from the row background (method of `check_viewer.py`); `unmappedNodes()` is empty; clear colour white, alpha 0. Fails: blank canvas with `ready` true | Mutation: comment out the render call, red | PW | 30 s |
| stage-C02 | R-08 (P1) | browser check | FIX internals | drag 200 px on the canvas | Works: `azimuthDeg()` moves over 20 degrees, `autoRotate` false, pixels differ at least 1 % before and after, 3 more frames drawn. Fails: only the hook moves | Mutation: disable the orbit controls, red. Act-removed: red | PW | 20 s |
| stage-C03 | R-04 R-08 (P0) | browser check | a copy of the real GLB cut to 40 % of its bytes; a missing GLB URL | harness page | Works: the vocabulary placeholder is visible, 0 uncaught errors. Fails: blank canvas or an unhandled error | Mutation: swallow the loader error, red | PW | 20 s |
| stage-C04 | R-13 (P1) | browser check | an exterior record `not picked`; one with a picked exterior | harness page | Works: not picked gives a dark slab whose bounding box equals the bundle's block size within 0.05 mm, hook `exteriorKind() === 'slab'`, dark pixels in the centre; rejected exteriors never load. Fails: a look-C mesh appears | Mutation: load option c when not picked, red | PW | 20 s |
| stage-C05 | R-11 (P1) | browser check | FIX `screens.json` (the "recording" screen fields); the same with `screens.json` missing | harness, set state "recording" | Works: `screenFields()` equals the labels in the file AND the screen region is no longer black; missing file gives a black face and the banner "missing". Fails: fields typed in code | Mutation: hard-code a label, guard and test red | PW | 20 s |

## TESTS: svg-viewer
Test files: `src/components/SvgViewer/__checks__/*.test.tsx` (UN) and `*.pw.ts` with a dev harness (PW).

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| svg-viewer-C01 | R-12 (P1) | unit | one real KiCad page SVG | zoom in 4 times, then "fit" | Works: scale 4.0 after the buttons; "fit" gives 1.0. Fails: scale unchanged | Mutation: zoom step 0, red. Act-removed: red | UN | 10 s |
| svg-viewer-C02 | R-12 R-10 (P1) | browser check | the same SVG with `<script>window.__pwn=1</script>` and `onload="window.__pwn=1"` injected | harness | Works: the image shows through `<img>` or `<object>` with scripts off; `window.__pwn` stays undefined; the crop is at least 2 % non-blank at zoom 4. Fails: script ran | Mutation: render by `innerHTML`, red | PW | 20 s |

## TESTS: part-card
Test files: `src/components/PartCard/__checks__/*.test.tsx` (UN).

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| part-card-C01 | R-02 (P0) | unit | FIX `parts.json` and `part-notes.json`, **all 77 lines** | render the card for each line id | Works: every card has non-empty "what", non-empty "why", a maker order code or a named open action, and an evidence level. The open action reads as words, never a bare `12.2` or `NEW-...`. Grouped line "U5, U6, U7, U8" shows quantity 4. Fails: any blank field or bare code (names the id) | Mutation: blank one note's `why`, red; leave the raw `NEW-` code, red | UN | 15 s |
| part-card-C02 | R-02 (P0) | unit | line BT1 | render | Works: "Battery cell" and "Grepow" before the disclosure; the maker part number hidden until "Exact data" opens. Fails: part number visible early | Mutation: render the number always, red | UN | 10 s |
| part-card-C03 | R-03 R-10 (P1) | unit | three real source cells: a path under `design/datasheets`, an absolute path outside `design/`, an https link; one line with no note | render | Works: served file link has `target=_blank` and an `href` under `/files/`; not served gives `aria-disabled="true"` plus the vocabulary reason; https link has `rel=noopener`; the line with no note says so in words and still shows its data. Fails: dead link that looks live | Mutation: drop `aria-disabled`, red | UN | 10 s |

## TESTS: part-notes
Test files: `collector/tests/part-notes/test_*.py`.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| part-notes-C01 | R-02 (P0) | data check | `content/part-notes.json` against bom.csv of commit 99dfb85 | pytest | Works: 77 of 77 ring lines covered; every `model_names` entry exists in `placement.csv` (ring) or `case_params.json` (case); word limits hold (NOTE_WHAT_WORDS, NOTE_WHY_WORDS). Fails: an id not in the bom, or a missing line, is named | Mutation: delete one note, red | PY | 10 s |
| part-notes-C02 | R-01 R-02 (P0) | data check | notes for BT1, U1, SW1 and every note that holds a number with a unit | pytest | Works: each number-with-unit in a note (such as 135 mAh, 4.6 x 13 x 25 mm) appears in the line's row or in `architecture.md`. Fails: a figure that exists nowhere | Mutation: change 135 to 153 in the BT1 note, red | PY | 10 s |
| part-notes-C03 | R-04 (P1) | data check | the same notes against the LIVE bom.csv (slim design) | pytest, report only | Works: prints notes with no line and lines with no note, never fails; the card shows "no plain-words note yet" in that case (part-card-C03). Fails: crash | n/a: report check, not a gate; the gate is part-notes-C01 on FIX | PY | 10 s |

## TESTS: collector-parts
Test files: `collector/tests/collector-parts/test_*.py`.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| collector-parts-C01 | R-02 R-01 (P0) | unit and integration | real `bom.csv`: U1 row (a quoted comma in "Bluetooth, USB, ..."), U2 row (price "GBP 1.25"), grouped refs, `open_action` values `12.2` and `NEW-...` and empty | pytest on a git-archive copy of 99dfb85 and on the live folder | Works: FIX 77 lines and 146 parts; U1 maker "Nordic" and part number `NRF54LM20A-CAAA-R7` in the right columns; ref `U7` resolves to `IM73D122V01XTMA1`; every `12.x` open action resolves to a section 12 item with a who (BT1 gives Grepow); LIVE counts equal rows and sum of quantity of the file read by the test. Fails: columns shifted | Mutation: split on every comma, red | PY | 20 s |
| collector-parts-C02 | R-04 R-06 (P0) | unit | bom.csv copy without the `reference` column; a copy with one short row; a copy with accents and a curly apostrophe in `item` and `maker` | pytest | Works: `unparsed` with the file name in `message`, exit 0; accents and apostrophes round-trip exactly. Fails: crash or a mangled name | Mutation: ignore the missing column, red | PY | 15 s |
| collector-parts-C03 | R-03 R-10 (P0) | integration | live folder; files `design/datasheets/mic_infineon_im73d122v01_en.pdf`, `design/case/out/parts/pin_P3_D+.step`, `design/look/c/out/ring.glb` (24.7 MB) | pytest | Works: size equals `os.path.getsize`; the `+` is in the stored path; no path holds `.venv` or `__pycache__`; every one of the 8 areas has files or an explicit empty list; a file over 20 MB is listed with `oversize: true` and a reason in words, never silently dropped. Fails: path escaping `design/` | Mutation: stop skipping `.venv`, red | PY | 30 s |
| collector-parts-C04 | R-03 (P0) | integration | FIX source | pytest builds `bundle.zip` | Works: `testzip()` is None; entry list equals `files.json` `bundle`; no `.venv/`, `__pycache__/`, `.git/`, `.env`, `*.key`, no leading `/` or `..` in a name; 20 sampled entries (incl. the `+` file) read back with sha equal to disk; zip at most 20 MB on FIX. Fails: names the entry | Mutation: add the `.venv` folder to the walk, red | PY | 30 s |

## TESTS: collector-model
Test files: `collector/tests/collector-model/test_*.py`.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| collector-model-C01 | R-08 R-01 (P1) | integration | real `placement.csv` of 99dfb85 and `design/mech/ring.py` | pytest | Works: node names of `internals.glb` equal the set of `part` values in the CSV; at least 5 layers ordered top to bottom by the CSV's own height column (computed by the test), including cover glass, screen, circuit board, cell. Fails: node missing or order wrong | Mutation: sort layers by name, red | PY | 90 s |
| collector-model-C02 | R-03 R-15 (P1) | integration | live `design/look/c/out/ring.glb` (24,748,132 bytes) and FIX frozen look C | pytest | Works: every `.glb` in the bundle is at most GLB_MAX_MB; a raw GLB over the limit is compressed or the record is `unparsed` with a reason, never copied as is. Fails: names the file | Mutation: skip the meshopt step, red | PY | 120 s |
| collector-model-C03 | R-13 R-06 (P1) | integration | FIX design copy without `design/status.json`; a copy where `look/` is missing | pytest | Works: exterior record `not picked`, exit 0; no look folder gives `missing`. Fails: crash | Mutation: require status.json, red | PY | 20 s |
| collector-model-C04 | R-04 (P0) | integration | the LIVE placement file while the slim design is being rewritten (columns changed); a copy with a missing column | pytest | Works: `unparsed` or `stale` with the file name and a message; the run goes on. Fails: stale model shown as current | Mutation: ignore a missing column, red | PY | 20 s |

## TESTS: collector-state
Test files: `collector/tests/collector-state/test_*.py`.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| collector-state-C01 | R-01 (P0) | integration | `architecture.md` of 99dfb85 | pytest | Works: size "30 x 20 x 9.5 mm" and battery "135 mAh", each with `{file, line}` whose line, read back by the test, contains the value. Fails: a value whose source line does not contain it | Mutation: shift the line number by 1, red | PY | 15 s |
| collector-state-C02 | R-05 (P0) | integration | the real live `design/status.json` (A4-draft; look, inside, electronics, parts, behaviour, case "in progress", board "not started"); a copy with state "half done"; the file absent | pytest | Works: live: 8 areas whose states equal the file's (read by the test); "half done" gives `unparsed` for that area, not a state word; absent file gives 8 x `unknown`. Fails: invented word shown | Mutation: pass unknown words through, red | PY | 15 s |
| collector-state-C03 | R-04 (P0) | integration | a temp copy where `architecture.md` says "Version A4" and `firmware.md` says "Follows design/architecture.md version A3"; the real pair "A4-draft" | pytest | Works: the behaviour area has `stale=true`, basis A3, current A4; the real "A4-draft" case gives the result `SOURCE-CONTRACT.md` states. Fails: stale not flagged | Mutation: skip the version compare, red | PY | 15 s |

## TESTS: collector-look
Test files: `collector/tests/collector-look/test_*.py`.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| collector-look-C01 | R-13 (P1) | integration | `design/look/a`, `b`, `c` of 99dfb85 | pytest | Works: options a, b, c; each thesis sentence at most 20 words; at most 3 trade-offs of at most 12 words; 4 finishes. Fails: a long sentence | Mutation: raise the cap, red | PY | 20 s |
| collector-look-C02 | R-13 R-04 (P1) | integration | live folder with the real `status.json` (`look.rejected` of a, b, c); an option folder without `ring.glb`; `finishes.json` absent | pytest | Works: rejected options carry `rejected=true` and the open-option count is 0; missing GLB gives status `missing`; missing finishes gives record `missing`, not an empty list. Fails: a rejected option counted as open | Mutation: ignore `rejected`, red | PY | 20 s |

## TESTS: collector-electronics
Test files: `collector/tests/collector-electronics/test_*.py`.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| collector-electronics-C01 | R-12 (P1) | integration | the real KiCad CLI run on `design/ecad/ring` of 99dfb85 | pytest | Works: 8 SVG files parse as XML; the microphone page text contains "U5"; 7 blocks; block "Microphones" lists U5, U6, U7, U8; pin plan at least 30 rows. Fails: a page that is empty XML | Mutation: write 0-byte SVGs, red | PY | 90 s |
| collector-electronics-C02 | R-12 R-02 (P0) | integration | blocks and `parts.json` of FIX | pytest | Works: every ref a block lists exists in the parts list. Fails: names the ref | Mutation: add `U99` to a block, red | PY | 15 s |
| collector-electronics-C03 | R-12 R-04 (P1) | integration | `KICAD_CLI` set to a missing binary | pytest | Works: pages record `missing` with a link to `design/ecad/ring/ring-schematic.pdf`; exit 0. Fails: crash or no link | Mutation: let the missing binary raise, red | PY | 20 s |

## TESTS: collector-board
Test files: `collector/tests/collector-board/test_*.py`.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| collector-board-C01 | R-04 R-01 (P0) | integration | `placement.csv` of 99dfb85; no `ring.kicad_pcb` | pytest | Works: `routed=false`; outline 27.0 x 17.4 mm; both sides non-empty; `mic1` on bottom, `recording_light` on top (sides computed independently by the test from the CSV); `missing` names `design/ecad/ring/ring.kicad_pcb`. Fails: routed true with no board file | Mutation: default `routed` to true, red | PY | 15 s |
| collector-board-C02 | R-04 (P0) | unit | a small synthetic `.kicad_pcb` that contains tracks (no real routed board exists yet; marked synthetic) | pytest | Works: `routed=true`. Fails: stays false | Mutation: ignore tracks, red | PY | 10 s |

## TESTS: collector-behaviour
Test files: `collector/tests/collector-behaviour/test_*.py`.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| collector-behaviour-C01 | R-11 (P1) | integration | real `design/firmware.md` tables (state, transition, gesture, motor) | pytest | Works: STANDBY long_press goes to RECORDING with M1 [80]; RECORDING short_press stays with highlight; long_press goes to STANDBY with M2 [80,120,80]; timings read back from the file: long 1000 ms, short 40 to 600, double 400; light on only in RECORDING. Fails: a number not in the file | Mutation: swap M1 and M2, red | PY | 15 s |
| collector-behaviour-C02 | R-11 R-04 (P0) | unit | a copy of `firmware.md` with the columns reordered; one with a table removed | pytest | Works: `unparsed` with the file name; never wrong numbers. Fails: values from the wrong column | Mutation: parse by position, red | PY | 15 s |

## TESTS: collector-case
Test files: `collector/tests/collector-case/test_*.py`.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| collector-case-C01 | R-01 (P0) | integration | `design/architecture.md` section 8, `design/case/` of 99dfb85 | pytest | Works: facts "33.6 x 33.4 x 55.2 mm", "700 mAh", "6.3 minutes per recorded hour" each with a source line that contains it; 74 case lines. Fails: "6.4" or a value with no source line | Mutation: edit the fact to 6.4, red | PY | 20 s |
| collector-case-C02 | R-08 R-03 (P1) | integration | `case.glb` and the real part name `pin_P3_D+` | pytest | Works: nodes include `lid`, `pin_P1_VBUS`, `pin_P2_D-`, `pin_P3_D+`, `pin_P4_GND`, `ring_US5_block` with the `+` and `-` kept in JSON; `case.glb` at most GLB_MAX_MB. Fails: a missing node | Mutation: strip `+`, red | PY | 60 s |

## TESTS: collector-open
Test files: `collector/tests/collector-open/test_*.py`.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| collector-open-C01 | R-05 R-01 (P0) | integration | `architecture.md` sections 12 and 13 of 99dfb85 | pytest | Works: 7 supplier requests each with a non-empty who and a non-empty "what to ask"; 5 bench tests; at least 3 decisions with an ISO date and a `{file, line}` that contains the quote when read back. Fails: a request with no who is flagged "who missing", never blank | Mutation: drop one who, red | PY | 15 s |
| collector-open-C02 | R-04 (P1) | integration | a copy of the file with section 12 renamed | pytest | Works: `unparsed` with the section name; exit 0. Fails: empty list shown as "nothing waiting" | Mutation: treat a missing section as empty, red | PY | 15 s |

## TESTS: behaviour-engine
Test files: `src/engine/behaviour/__checks__/*.test.ts` (UN), with a fake clock.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| behaviour-engine-C01 | R-11 (P1) | unit | FIX `behaviour.json` (from `firmware.md`) | the 4 cases of the plan | Works: hold 1000 ms in STANDBY gives RECORDING, light true, pulses [80]; 200 ms tap then 400 ms idle gives highlight 1 and RECORDING; hold 1000 ms gives STANDBY with 2 pulses; hold 700 ms changes nothing. Fails: any mismatch | Mutation: `>=` to `>` at 1000, red | UN | 10 s |
| behaviour-engine-C02 | R-11 (P1) | unit (table driven) | every row of the transition table in FIX `behaviour.json`, plus boundaries 39, 40, 599, 600, 601, 999, 1000 ms | loop over rows | Works: each gesture gives the row's `to` state and motor pattern; boundaries fall on the file's numbers. Fails: names the row | Mutation: ignore the second row, red | UN | 10 s |
| behaviour-engine-C03 | R-01 R-11 (P1) | guard | folder `src/engine/behaviour` | grep | Works: no state name or timing literal (`RECORDING`, `STANDBY`, `1000`). Fails: names the line | Mutation: add `1000`, red | GD | 5 s |

## TESTS: home
Test files: `tests/checks/home/home.spec.ts` (ids `home-C01..`). Run on LIVE and EMPTY at lane time; on FIX once fixture-a3 exists.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| home-C01 | R-01 (P0) | browser check | the bundle's `facts.json` read by the test | open Home | Works: each key number on screen equals the bundle value (no literal in the test). Fails: a different value | Mutation: format the value in code, red | PW | 30 s |
| home-C02 | R-05 (P0) | browser check | LIVE `areas.json` and the real `status.json`; a bundle without status.json | open Home, click each tile | Works: 8 tiles, each with one pill from the vocabulary equal to `areas.json`; no status.json gives 8 x "state unknown"; each tile leads to its route. Fails: a tile with no state or a wrong route | Mutation: swap two tile targets, red. Act-removed: red | PW | 40 s |
| home-C03 | R-04 (P0) | browser check | EMPTY | open Home | Works: banner with the command `npm run collect` in a `<code>` element; 0 console errors. Fails: blank page | Mutation: remove banner, red | PW | 15 s |
| home-C04 | R-13 R-08 (P1) | browser check | LIVE (no approved exterior) | open Home, drag | Works: "Plain black slab" label visible; canvas at least 2 % non-blank and moves on drag; no page scroll at 1512x982 and 1280x800. Fails: a rejected look shown | Mutation: show look A, red | PW | 30 s |

## TESTS: look
Test files: `tests/checks/look/look.spec.ts`.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| look-C01 | R-13 (P1) | browser check | FIX (3 options); FIX with `status.json look.picked='b'`; LIVE with real `look.rejected=['a','b','c']` | open Look | Works: 3 panels with bundle titles; picked shows only b with "Picked"; rejected gives 0 panels and the banner "New options in design". Fails: a rejected panel | Mutation: drop the rejected filter, red | PW | 40 s |
| look-C02 | R-13 (P1) | browser check | LIVE with rejected looks; all 9 routes | text scan | Works: no option title (MONOLITH and the B and C titles) and no "Earlier options" link anywhere in the app ("Not in the app"). Fails: names route and text | Mutation: add a link "Earlier options", red | PW | 40 s |
| look-C03 | R-08 (P1) | browser check | FIX `finishes.json` | click each finish, then "On a finger" | Works: body colour hook equals the finish colour on all options and the ring's mean pixel colour moved; finger visible and canvas differs; `aria-pressed` follows. Fails: hook right, picture unchanged | Mutation: set only the hook, red. Act-removed: red | PW | 40 s |
| look-C04 | R-04 (P1) | browser check | FIX copy where option c has no `ring.glb` | open Look | Works: a labelled placeholder for c; a and b still render. Fails: blank panel or all blank | Mutation: throw on a missing GLB, red | PW | 25 s |

## TESTS: inside
Test files: `tests/checks/inside/inside.spec.ts`.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| inside-C01 | R-08 (P1) | browser check | FIX placements | slider 0 then 1; keyboard ArrowRight | Works: at 1 every layer gap at least EXPLODE_MIN_GAP_MM and the canvas differs; at 0 centres equal placements within 0.05 mm; keyboard moves the slider; a layer without a model is a text row. Fails: closed view not restored | Mutation: no reset at 0, red. Act-removed: red | PW | 40 s |
| inside-C02 | R-02 R-08 (P0) | browser check | FIX parts and placements, incl. the unlinked object "gasket" | real mouse click at `screenPos('cell')`, then at `screenPos('gasket')`, reload | Works: URL holds `part=ring%3ABT1`, the card says "Battery cell"; gasket says "no parts-list line for this object"; reload keeps the selection; the card never belongs to a neighbour part. Fails: wrong card | Mutation: pick nearest part, red | PW | 40 s |
| inside-C03 | R-02 R-09 (P1) | browser check | FIX parts; typed texts "grepow", "u5", "MICROPHONE", "microphone", "D+", "(", "Würth" | type in search | Works: grepow lists ring:BT1; case-insensitive lists equal; `D+`, `(` and an accent never throw, they list or say "nothing found" in plain words; choose a result selects it and opens its card. Fails: regex error, blank | Mutation: build a `RegExp` from the text, "(" breaks, red | PW | 30 s |
| inside-C04 | R-04 (P0) | browser check | EMPTY and STALE | open Inside | Works: banner in vocabulary words; panel not empty; stale content still shown. Fails: hidden | Mutation: hide when stale, red | PW | 20 s |

## TESTS: electronics
Test files: `tests/checks/electronics/electronics.spec.ts`.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| electronics-C01 | R-12 R-01 (P1) | browser check | bundle `blocks.json`, `electronics.json` read by the test | open Electronics | Works: block count and pin plan row count equal the files; the power budget has the row "From the cell". Fails: a count off by one | Mutation: slice the table, red | PW | 30 s |
| electronics-C02 | R-12 (P1) | browser check | FIX schematic pages | click block "Microphones"; expand the panel; Escape | Works: viewer image loads within 1 s, `naturalWidth` above 0, crop at least 2 % non-blank. Fails: broken image | Mutation: wrong page map, red. Act-removed: red | PW | 30 s |
| electronics-C03 | R-02 R-09 (P1) | browser check | FIX `blocks.json` refs | click "parts of this page" | Works: Parts opens filtered; line set equals the oracle (refs of that page) | Mutation: pass no filter, red | PW | 25 s |
| electronics-C04 | R-12 R-04 (P1) | browser check | FIX with the schematic record `missing` | open Electronics | Works: PDF link shown with words; blocks still listed. Fails: empty screen | Mutation: hide blocks when pages missing, red | PW | 20 s |

## TESTS: board
Test files: `tests/checks/board/board.spec.ts`.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| board-C01 | R-04 (P0) | browser check | FIX `board.json` (`routed:false`); a copy with `routed:true` (synthetic) | open Board | Works: not routed shows a banner with "not routed" and the missing file name; routed true shows no such banner. Fails: a ready-looking board with no banner | Mutation: ignore `routed`, red | PW | 25 s |
| board-C02 | R-01 R-08 (P1) | browser check | FIX `board.json` | open Board; click "Bottom"; click `mic1` | Works: plan holds one `data-part` per listed placement (count equals the file); `aria-pressed` on Bottom and every `data-side=top` element hidden; `mic1` opens the card of ring:U5 or the words "no parts-list line"; stage isolates the board layer. Fails: toggle changes nothing | Mutation: toggle sets only the pressed state, red. Act-removed: red | PW | 35 s |

## TESTS: parts
Test files: `tests/checks/parts/parts.spec.ts`.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| parts-C01 | R-02 R-01 (P0) | browser check | bundle `parts.json` (live 77 lines, 146 parts) read by the test | open Parts | Works: table model holds all lines, last line reachable by scroll and its item text equals the file's last row; totals "N lines" and "M parts" equal the file; click U5 opens its card. Fails: virtualised table cuts the last row | Mutation: off by one in the row window, red | PW | 40 s |
| parts-C02 | R-02 (P1) | browser check | filters "has code", "made to drawing", "needs supplier"; reload | click chips, reload, clear all | Works: "needs supplier" leaves exactly the lines whose open action is a section 12 item (oracle from `parts.json`); clear all restores every line; reload keeps the filter (URL query); chips carry `aria-pressed`. Fails: filter ignored | Mutation: filter on the wrong field, red. Act-removed: red | PW | 40 s |
| parts-C03 | R-03 (P0) | browser check | live `design/bom.csv` | click "Export CSV" with no filter, then with "needs supplier" on | Works: both downloads are `bom.csv` and byte-equal (sha256) to the source file. Fails: filtered or re-quoted CSV | Mutation: export visible rows, red | PW | 30 s |

## TESTS: behaviour
Test files: `tests/checks/behaviour/behaviour.spec.ts`.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| behaviour-C01 | R-11 (P1) | browser check | bundle `behaviour.json` read by the test; every gesture row | for each row perform the gesture on the panel button, then on the ring's button in 3D | Works: `behaviour-state` label equals the row's `to` state label from the file; light `data-on` and the ring's light pixels (red-dominant or not) match the table; vibration marks equal the pattern length. Both control paths agree (owner answer "Both"). Fails: panel works, 3D press does nothing | Mutation: unbind the 3D press, red. Act-removed: red | PW | 60 s |
| behaviour-C02 | R-11 (P1) | browser check | keyboard | hold Space 1000 ms; hold 700 ms | Works: Space acts as the button; 700 ms changes nothing. Fails: either differs | Mutation: threshold 600, red | PW | 20 s |
| behaviour-C03 | R-04 (P0) | browser check | LIVE (firmware follows A3, design is A4-draft) and STALE | open Behaviour | Works: the stale line is shown and the simulator still works. Fails: hidden or disabled | Mutation: disable when stale, red | PW | 20 s |

## TESTS: case
Test files: `tests/checks/case/case.spec.ts`.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| case-C01 | R-01 (P0) | browser check | bundle `case/` facts read by the test | open Case | Works: size, mAh and charge time on screen equal the file; the case parts list rows equal the file's count. Fails: a value from code | Mutation: hard-code a figure, guard and test red | PW | 30 s |
| case-C02 | R-08 R-02 (P1) | browser check | FIX case nodes incl. `pin_P3_D+` | click "Open lid", click it again, click pins by mouse at `screenPos(...)` | Works: lid at least 90 degrees within 1.5 s and back to 0; canvas differs; each pin card text holds its signal name (VBUS, D-, D+, GND). Fails: lid hook only | Mutation: lid fixed, red. Act-removed: red | PW | 35 s |
| case-C03 | R-04 (P0) | browser check | FIX with `case.glb` missing | open Case | Works: banner in words, facts and parts still shown. Fails: empty screen | Mutation: hide facts on model error, red | PW | 20 s |

## TESTS: open-files
Test files: `tests/checks/open-files/open-files.spec.ts`.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| open-files-C01 | R-05 (P0) | browser check | bundle `open.json` read by the test | open "Open items", click "waiting on a supplier"; a bundle with 0 supplier requests | Works: row count after the click equals the file's supplier count and is below the count before; each row has who and what to ask; 0 supplier items says "nothing waiting"; chip `aria-pressed`. Fails: stale list | Mutation: filter on the wrong field, red. Act-removed: red | PW | 35 s |
| open-files-C02 | R-03 (P0) | browser check | FIX `files.json` incl. `design/case/out/parts/pin_P3_D+.step`; a bundle with no `bundle.zip` | open "Files", click a file link, click "Download partner bundle" | Works: 8 area groups, size and date per row; the `+` file downloads with sha equal to disk (the link is encoded); the zip button downloads a `.zip` of the same size as the file; absent zip gives a disabled button with "run npm run collect". Fails: `+` read as space, 404 page saved | Mutation: do not encode `+`, red | PW | 40 s |
| open-files-C03 | R-04 (P0) | browser check | EMPTY and STALE | open the screen | Works: banner, panel not empty, 0 console errors | Mutation: crash on empty `open.json`, red | PW | 20 s |

## TESTS: fixture-a3
Test files: `tests/fixtures/checks/test_*.py` (PY). The fixture itself is built by `make-fixture.sh`.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| fixture-a3-C01 | R-07 (P1) | integration | commit 99dfb85 plus frozen look C | run `make-fixture.sh` twice | Works: exit 0 both times; sha256 of every JSON file equal across runs; `manifest.git_commit` starts `99dfb85`; 77 lines and 146 parts; no file over 20 MB; the build succeeds with the live design path made unreadable (it reads only the archive). Fails: names the differing file | Mutation: put `built_at` now into a JSON, red | PY | 90 s |
| fixture-a3-C02 | R-07 (P1) | data check | JOURNEYS.md real-data line | pytest | Works: FIX holds U1 `NRF54LM20A`, BT1 135 mAh, SW1 `SKRHADE010`, key numbers 30 x 20 x 9.5 mm and 135 mAh, 4 microphones; `status.json` has all four state words; 3 look options not rejected; finishes include "Slate Titanium". Fails: a journey literal missing | Mutation: delete SW1 row, red | PY | 15 s |
| fixture-a3-C03 | R-02 R-04 R-14 (P0) | cross-record data check | the whole FIX bundle | pytest | Works: every `open_action` of a line resolves to an open item; every ref in `blocks.json` exists in `parts.json`; every note id exists; every placement links to a part or is flagged; every source link is served or marked; line counts equal across `parts`, `files` and `bundle`. Fails: names the dangling reference | Mutation: rename a ref in `blocks.json`, red | PY | 20 s |

## TESTS: journeys-a
Test files: `journeys/J1.spec.ts`, `journeys/J3.spec.ts`, `journeys/J6.spec.ts` (rows J1#1 to J1#4, J3#1 to J3#3, J6#1, J6#2 of section 3).

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| J1#1..J1#4, J3#1..J3#3, J6#1, J6#2 | per section 3 | journey e2e | FIX | per section 3 | per section 3 | red at scaffold: `npm run journeys -- J1 J3 J6` exits non-zero with assertion failures only; every step id appears in a test title; no duplicate test ids | JR | 3 min for the 9 |
| journeys-a-C01 | R-09 R-02 (P1) | journey e2e | FIX, all 77 lines | from Home click Parts, then each row in turn | Works: every line opens a card with its own heading within 3 clicks of Home (counted by the helper); no card repeats another's text. Fails: names the line | Mutation: break the row click for lines after 50 (virtualised), red | JR | 60 s |
| journeys-a-C02 | R-15 (P1) | self-check | the spec files | `grep -oE '"J[0-9]+#[0-9]+"'` | Works: no duplicate id. Fails: duplicate | n/a: scaffold check | JR | 5 s |

## TESTS: journeys-b
Test files: `journeys/J2.spec.ts`, `journeys/J4.spec.ts`, `journeys/J5.spec.ts`, `journeys/J7.spec.ts` (rows J2#1..3, J4#1..3, J5#1..3, J7#1..2 of section 3).

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| J2#1..J2#3, J4#1..J4#3, J5#1..J5#3, J7#1..J7#2 | per section 3 | journey e2e | FIX | per section 3 | per section 3 | red at scaffold: `npm run journeys -- J2 J4 J5 J7` exits non-zero with assertion failures only; every step id appears in a test title | JR | 4 min for the 11 |

## TESTS: seams
Test files: `tests/seams/*.spec.ts` (PW) and `tests/seams/data/test_*.py` (PY).

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| seams-C01 | R-14 R-02 (P0) | browser check | FIX, ring:BT1 and ring:U5 | open the card from Inside, Parts, Board (BT1) and Parts, Electronics (U5) | Works: the card text is identical from every entry. Fails: names the two texts that differ | Mutation: a second card component with a different label, red | PW | 40 s |
| seams-C02 | R-14 (P1) | browser check | FIX | Home, Parts, Files | Works: "77 lines" and "146 parts" equal on all three. Fails: a differing count | Mutation: count parts as lines on one screen, red | PW | 30 s |
| seams-C03 | R-14 R-05 (P0) | browser check | FIX with its `status.json` | each of 8 areas | Works: the Home tile pill text equals the banner text of that area's screen. Fails: names the area | Mutation: map two areas to one state, red | PW | 40 s |
| seams-C04 | R-05 (P0) | browser check | the REAL live `design/status.json` read by the test | LIVE bundle, open Home | Works: each tile pill equals the file's state for that area. Fails: a tile whose word is not in the file | Mutation: default to "in progress", red | PW | 30 s |
| seams-C05 | R-04 R-01 (P0) | rebuild check | a temp copy of the FIX source with the U1 price and one area state edited | `npm run collect` into a temp bundle, serve it, reload the card and Home | Works: the new price and state show after a rebuild plus refresh (PRD "Reactivity"); the old ones are gone. Fails: stale cache shows the old value | Mutation: serve the old bundle from cache, red. Act-removed: no edit, no change, red | PW | 60 s |
| seams-C06 | R-14 R-17 (P2) | browser check plus scan | all 9 routes | scan sources and measure | Works: `'not started'`, `'in progress'`, `'waiting on a supplier'` appear only in `src/contract`; the tab bar box (x, y, height) is equal on all 9 routes. Fails: names the file or route | Mutation: type a state word in a route, red | PW | 30 s |

## TESTS: smoke-perf
Test files: `tests/smoke/*.spec.ts`. Runner `JR -- smoke`.

| test id | risk row (class) | type | real input | entry | visible assertion (works · fails) | red-first case | runner | budget |
|---|---|---|---|---|---|---|---|---|
| smoke-perf-C01 | R-04 R-10 (P0) | smoke | 9 routes x 3 bundles: FIX, EMPTY, STALE | open each route | Works: 0 console errors, 0 failed requests; STALE shows the stale line and content on every route. Fails: names route and bundle | Mutation: inject `console.error` in one route, red | JR | 120 s |
| smoke-perf-C02 | R-10 (P1) | offline run | FIX and LIVE | abort every request whose host is not `127.0.0.1`, open all 9 routes | Works: `window.__stage.ready` true on stage routes, 0 console errors, fonts render (computed family loaded). Fails: a route that waits for the network | Mutation: add a font `<link>` to Google, red | JR | 90 s |
| smoke-perf-C03 | R-16 (P2) | performance | FIX; PRD `Perf-budget`; 3 runs, median | open each route cold and warm; a tab click; the explode slider | Works: first paint at most 1500 ms, route read at most 300 ms cold and 100 ms warm, interaction at most 100 ms; all numbers written to `tests/smoke/out/perf.json`; frame time recorded only (plan G7). Fails: names route and number | Mutation: add a 400 ms delay, red | JR | 120 s |
| smoke-perf-C04 | R-17 (P2) | accessibility | 9 routes | axe-core; Tab walk of J1 | Works: 0 violations of button-name, link-name, label, color-contrast; focus ring visible on the slider, search and the card's source link. Fails: names rule and element | Mutation: remove an `aria-label`, red | JR | 60 s |
| smoke-perf-C05 | R-17 (P2) | style floor | 9 routes | computed styles and word count | Works: `[data-panel]` has no shadow and radius 0; first heading in "Libre Caslon Text"; at most PANEL_MAX_WORDS words before the first disclosure. Fails: names route | Mutation: add 200 words, red | JR | 30 s |

## 5. Prune list

Rule for every test that will ever be added (applied by the lead at each merge and by the independent reviewer): a test stays only if its row names (1) a risk row, (2) a real input and where it was captured, (3) a visible assertion, (4) a red-first case seen red, (5) a default runner of section 2. A test that fails any of the five is USELESS and is deleted in the same change. A test that passes with its own action deleted is WEAK and is rewritten, never kept.

| existing test | verdict | reason | action |
|---|---|---|---|
| none under `explorer/` (the folder holds only `docs/`) | n/a | greenfield | none |
| the demo test and example spec a starter generates (`example.spec.ts`, `App.test.tsx`, any counter test) | USELESS | cannot fail on a named risk | delete when the contract lane scaffolds |
| tests shipped inside `vendor/**` (the vendored component library) | USELESS here | not our code; slows `npm test`; may fail on its own setup | exclude `vendor/**` in vitest, pytest and Playwright config; contract-C07 fails if they are collected |
| any test that asserts only that a hook is true (`window.__stage.ready`) | WEAK | green on a blank canvas | rewrite with the 3D pairing rule |
| any `agent.assert` or screenshot-only check standing in for a P0 or P1 row | WEAK | covers no risk row | add the deterministic assertion of the row |
| a test pinned to a live design value (30 x 20 x 9.5 mm on the live app, "77" on live) | USELESS | the live design is changing | rewrite to read the bundle (lane check) or move to FIX (journey) |
| a test asserting that rejected looks A, B, C appear on the live Look screen | USELESS | owner: "Not in the app" | rewrite per look-C01 and look-C02 |
| `design/tools/check_bom.py`, `design/mech/check_fit.py`, `design/look/viewer/check_viewer.py`, `design/firmware-check.py` and the `check*.log` files beside them | KEEP, out of scope | they guard the design, not the app; run by nobody in the explorer runners | leave in place; do not add to `npm test`. The pixel method of `check_viewer.py` is reused in stage-C01 |
| a source-text-only test (greps a component for a string) used as proof of behaviour | USELESS | passes with the feature dead | delete; keep only the guard (contract-C06) and scans that are labelled as scans |

## 6. Coverage and uncovered risks

Every P0 and P1 row has at least one KEEP test above: R-01 (contract-C06, collector-state-C01, collector-case-C01, home-C01, J1#1, J7#1), R-02 (part-card-C01, collector-parts-C01, journeys-a-C01), R-03 (collector-parts-C04, J6#1, J6#2, parts-C03), R-04 (shell-C01, smoke-perf-C01, collector-*-C0x), R-05 (collector-state-C02, seams-C03, seams-C04), R-06 (contract-C02, contract-C03), R-07 (contract-C11, fixture-a3-C01), R-08 (stage-C01, C02, every 3D journey), R-09 (shell-C02, journeys-a-C01), R-10 (contract-C04, C05, smoke-perf-C02), R-11 (behaviour-engine-C02, behaviour-C01, J5), R-12 (svg-viewer-C02, electronics-C02, J4), R-13 (look-C01, look-C02, stage-C04), R-14 (seams-C01 to C03), R-15 (contract-C07, C08).

| risk row | why no test | how it is watched instead |
|---|---|---|
| R-17 "slick" and the anti-references (taste) | taste is not a deterministic assertion; the floor (shadows, radius, fonts, words, a11y) is covered | the taste judge and the 7 reviewer seats against the S1 board; the owner judges every screen on localhost (PRD Review contract) |
| R-16 frame time of the 3D stage | the PRD gives no number (plan gap G7) | recorded in `tests/smoke/out/perf.json`; gated once the owner sets a number |
| Safari | tests run Chromium only; one browser download, no second (disk) | the owner opens it in Chrome or Safari on this Mac; a Safari issue arrives as an owner bug and gets a regression test |
| the owner's reading "does this show me what I am building" | a judgement | version 1 acceptance: the owner opens every screen (PRD Rollout) |
| the real routed-board branch (board-C01 routed true) | no routed board exists; the test uses a synthetic `board.json` flip, marked synthetic | re-run on the real board when the board is routed |
| the live design while it is rewritten | values change daily | LIVE runs gate structure and read-back equality only; the owner sees the live app |

## 7. Conflicts

Conflicts between the signed documents and the plan, with exact lines. None is changed here; the tests follow the left-hand source and say so.

- K1. `docs/JOURNEYS.md` line 2 `real-data: the ring design in this project at git commit 7274c69` against `docs/BUILD-MODE.md` "Contract deltas" (5) `journeys run on a frozen copy of design A3 (commit 99dfb85 plus look C)`. The tests use 99dfb85 (contract-C11, fixture-a3-C01). JOURNEYS line 2 still names 7274c69.
- K2. `docs/JOURNEYS.md` J1.3 `4.6 x 13 x 25 mm` against plan.json `ux-part-card` `4.6 x 13.0 x 25.0`. J1#3 matches the numbers 4.6, 13 and 25 as numbers, not as one string.
- K3. `docs/JOURNEYS.md` J4.1 `the block diagram: chip, 4 microphones, storage, screen, power, controls, case link` and J4.2 `the 8 pages` against plan.json `functionality-electronics-extract` `8 SVG files ... 7 blocks` and `docs/BUILD-MODE.md` delta (2) `blocks come from the 7 schematic sheets`. 8 pages against 7 sheets, and a "case link" block that the 7 sheets may not give. The tests assert 7 blocks and 8 pages as the plan says and do not assert a "case link" block.
- K4. `docs/JOURNEYS.md` J1.4 `file exists in design/datasheets` / on failure `the link is shown greyed with "not on disk"` against the real `design/bom.csv`: source cells hold absolute paths outside `design/` (for example `<work>/ai-ring-recorder-bom-evidence/nordic_caaa_bom.txt`) and https links. A file that exists but is not served is not "not on disk". J1#4 and part-card-C03 expect a greyed link with a vocabulary reason; the words need a line in `docs/CONTRACT.md`.
- K5. `docs/PRD.md` Test plan `Regression: one test per bug the owner reports ... Mutation: each check proven to fail once` against `docs/lane-dag.json`: no lane owns `tests/regression/` or a mutation record. This plan puts mutation evidence in each row and each lane report; `tests/regression/` stays empty until a bug is reported.
- K6. `docs/CONSTRAINTS.md` rule 6 `no file over 20 MB` against the real `design/look/c/out/ring.glb` (24,748,132 bytes) and `ring.step` (21,584,771 bytes), the plan's frozen copy of look C, and `docs/JOURNEYS.md` J6 `one archive with every design file` (plan-notes: partner bundle = every file under `design/`). The fixture must hold a compressed look C; the live bundle lists the two big files as `oversize` and the plan cannot say whether they enter the zip. Tests collector-parts-C03, collector-parts-C04 and contract-C08 hold the 20 MB line on the fixture; the live choice is in questions_for_owner.
- K7. `docs/lane-dag.json` lane contract acceptance `the testid grammar '<route>.<element>'` against plan.json todos that name `[data-testid=area-tile]`, `part-card`, `state-banner` without a route. The testids in this plan are placeholders; `docs/CONTRACT.md` wins once it exists.
- K8. `docs/PRD.md` `Perf-budget: first-paint 1500ms · interaction 100ms · route-read 300ms cold / 100ms warm` against plan.json `functionality-smoke-perf` `cold and warm route reads ... (cold recorded)` which gates only warm. smoke-perf-C03 gates all four numbers as the signed PRD says.
- K9. `docs/lane-dag.json` surface lane acceptance `tests/checks/<lane> ... pass against the live collect AND against an empty bundle` and `smoke-perf` `npm run journeys -- smoke` against `plan.json` `cap-collector` `npm test exits 0`: no document says which runner loads `tests/checks`, `tests/seams` or `src/**/__checks__`. Section 2 defines `npm test` (PY, UN, GD, PW) and `npm run journeys` (JR); contract-C07 proves nothing is orphaned. The contract lane must create these scripts.
- K10. `docs/JOURNEYS.md` J6.2 `Export CSV ... bom.csv downloads` does not say whether the export is the full file or the filtered view. plan.json `interaction-parts-export` says the file equals the source `design/bom.csv`. parts-C03 and J6#2 test the full file even with a filter on.

## TESTS: wiring-data (added 2026-11-13, owner's ask "you need to do the wiring on the ring explorer")
Test files: `collector/tests/collector-wiring/test_wiring.py`, `collector/tests/collector-boards/test_boards.py`. Checks in `collector/lib/wiringcheck.py` and `collector/lib/boardcheck.py`. Runner: `npm run test:collector`. No browser test (owner: "don't do any test on chrome"). Real input: the design folder as it is when the test runs; the extractors run once per test process.

| test id | risk | type | real input | entry | visible assertion (works · fails) | red-first case (kept fixture) | runner | budget |
|---|---|---|---|---|---|---|---|---|
| wiring-data-C01 | the map shows a count the file does not state | integration | `design/wiring/connections.md` | pytest | Works: the number of connections equals "Count: N joints" and the number of joint rows of the Part 1 table. Fails: names both numbers | `fixtures/count-short` (one connection dropped) | PY | 60 s with the boards run |
| wiring-data-C02 | a connection with one end, or no source file | integration | same | pytest | Works: every connection has 2 ends that name a node, text on each end, and a source file and proof files that exist. Fails: names the connection | `fixtures/one-end`, `fixtures/missing-source` | PY | same |
| wiring-data-C03 | a joint no file draws shown as drawn | integration | same | pytest | Works: the connections marked open equal the rows the file begins with NOT DRAWN | none (reads the file itself) | PY | same |
| wiring-data-C04 | a board without its file or with an empty layer picture | integration | the 17 board files, `kicad-cli` | pytest | Works: each board has its file on disk and at least one copper layer picture that is not empty. Fails: names the board and layer | `fixtures/no-file`, `fixtures/empty-layer` | PY | same |
| wiring-data-C05 | a state that differs from its rules report | integration | the saved reports | pytest | Works: each state's numbers equal the count lines of its report; status and words follow. Fails: shows both numbers | `fixtures/state-vs-report` (report says 3 open, state says 0) | PY | same |
| wiring-data-C06 | the ring board called finished while its report counts open connections | integration | the ring board report | pytest | Works: state `not-finished` while the report counts open connections. Fails: names the count | `fixtures/ring-claims-routed` | PY | same |
| wiring-data-C07 | the list is not the 1 + 14 + 2 boards, schema breaks | integration | both records | pytest | Works: 17 boards, 7 sizes per band circuit; both records validate against their schemas | none | PY | same |

Red-first run: `RING_EXPLORER_BROKEN=<fixture> .venv-pytest/bin/pytest -q collector/tests/<folder> -k <test>` reads the kept broken fixture in place of the real data; the same test then fails.

## TESTS: wiring-screens (added 2026-11-13)
Test files: `src/routes/electronics/wiring.test.tsx` (check ids wiring-screens-C01..C13), `src/routes/board/board.test.tsx` (wiring-screens-C20..C31). Runner: `npm run test:unit` (vitest, jsdom). Made-up data only. NOT run: any browser test or journey (owner: "don't do any test on chrome", and "I look myself" on how the screens are proven). What the unit tests do not prove: how the two screens look, where the map's nodes and pills sit on the real data, and whether a click in a real browser reaches the right element. The owner opens http://localhost:8790/electronics and http://localhost:8790/board and judges.

| test id | risk | assertion | red-first case |
|---|---|---|---|
| wiring-screens-C01..C04 | map layout and lookups | parallel lines numbered; levels follow the longest chain; an end with no node left out of the lines; a board's connections; typed-word filter | mutations of `edgesOf` and `isOpen` seen red |
| wiring-screens-C05..C06 | map and list | one pill per connection, the open one marked; list filter, not-drawn word, click | mutation of `isOpen` seen red |
| wiring-screens-C07..C13 | the section | no map in the data said in words (and not while loading); count line and note; the chosen connection in words; board link only for a known board; part references; map or list; empty list | none |
| wiring-screens-C20..C25 | board helpers | groups, sizes, plan of an entry, layer choice, stack order, dates in words | mutation of `layersShown` seen red |
| wiring-screens-C26..C31 | board parts | picker, layer buttons, state line in the data's words, missing file and notes, link back to the connections | mutation of the state words seen red |

## TESTS: case-true (added 2026-11-13)
Test files: `collector/tests/collector-case/test_links.py` (real design), `test_link_rules.py` (made-up list), `src/routes/case/case.test.tsx` (check ids case-true-C01..C13). Runners: `npm run test:collector`, `npm run test:unit`. No browser test or journey (owner: "I look myself").

| test id | risk | type | assertion | red-first case (kept fixture) |
|---|---|---|---|---|
| case-true-collector-1 | a solid of the model is missing from the data, or links to nothing without being named | integration | the 40 solids of `case_params.json` are in the data; each links to a line or is named in `unlinked_nodes`; at most 2 are unlinked | `fixtures/matches-nothing` (a solid counted as linked with no line) |
| case-true-collector-2 | a parts-list line has no class, two, or is lost; the four counts do not add up | integration | each of the 90 lines is in exactly one class; the counts add up to 90; at most 5 lines without a solid; every no-solid line has a reason | `fixtures/line-removed` (the sum is 89) |
| case-true-collector-3 | a quantity-0 line classed as fitted | integration | the lines of quantity 0 are exactly the `not-fitted` ones | `fixtures/qty0-fitted` |
| case-true-collector-4 | a linked id the parts record does not have; a board without its solid, picker id or parts | integration | every id of lines, solids and board parts is in `parts.json`; two boards, each with a solid, a picker id and parts; the main board's solid holds `case:PCB1` first and `case:U1` | none |
| case-true-collector-5 | a rule links the wrong thing | unit | each rule links what it reads; a quantity-0 line is never linked; classes add up | none |
| case-true-C01..C04 | counts line, class words, solid names | unit | made-up data | mutations of `countsLine`, `nodeNames`, `classWords` seen red |
| case-true-C05..C07 | board parts, "open this board", model and refit lines | unit | made-up data | none |
| case-true-C10..C13 | the click from a solid to its card on the real bundle (jsdom) | unit | every one of the 40 solids opens a line of the parts record; counts line equals the data's; board parts of the main board; a glide shows its class | none |

Red-first run: `RING_EXPLORER_BROKEN=<fixture> .venv-pytest/bin/pytest -q collector/tests/collector-case/test_links.py`.

## questions_for_owner

- Should the partner bundle include the two large files of the rejected look C (24.7 MB and 21.6 MB), or list them as "too large, sent separately"? The tests assume the second: the zip stays under 20 MB on the test copy and the live list marks them. Nothing waits on the answer.

RESULT: done, 20 journey-step rows (J1 to J7, every step) and 30 `## TESTS` blocks (one per lane of docs/lane-dag.json) designed, 10 conflicts listed.

## TESTS: conductor-view (added 2026-11-13, owner's words "the connexions and wiring is far from being 100% i see")
Test files: `collector/tests/collector-wiring/test_conductors.py` (real design; check helpers in `collector/lib/wiringcheck.py`: `check_conductor_lines`), `src/routes/electronics/conductors.test.tsx` (made-up data, check ids conductor-view-C01..C13), `src/routes/electronics/conductors.real.test.tsx` (the real bundle in jsdom, C20..C22). Runners: `npm run test:collector`, `npm run test:unit`. No browser.

| test id | risk | assertion | red-first case |
|---|---|---|---|
| conductor-view-collector-1 | R-01: a conductor line missing, or a shown terminal, signal, carrier or state not what the file says | the number of conductors of each connection equals the lines of `product-wiring.csv`; each shown value is read back from the `{file, line}` it cites (csv read on its own, not with the extractor's reader) | `RING_EXPLORER_BROKEN_CSV=remove-line` and `=change-terminal` (broken copies made from the real file at run time) fail on W010 |
| conductor-view-collector-2 | R-01: kinds not covered | at least 6 conductors over copper, wire, spring pin and inside the part, each value equal to its cited line | none (the sample is fixed by kind) |
| conductor-view-collector-3 | R-14: a count differs from the rows | `conductors.total` equals the rows of the connection; `conductor_file` complete and total equal the file | `test_checker_flags_*` |
| conductor-view-collector-4 | R-04: a no-conductor line counted or lost | each `carrier_kind none` line is shown apart with its reason and line, and is no row | none |
| conductor-view-C01..C04 | R-01: rows differ from the record | one row per conductor with signal, terminals, carrier, state; a row opens to the joins, source and the length of the chosen size; no length said in words | mutations of the count and of the length words seen red |
| conductor-view-C05..C07 | R-04, R-14: count line | "N of M" read from the record; file missing, unreadable or fields absent said in words, no count | mutation of `productCountWords` seen red |
| conductor-view-C08..C13 | R-04, R-14: honest states | no conductor line said; a smaller or larger count of the connection said; equal count says nothing; a no-conductor line shown apart | mutation of the count test (`!==` to `<`) seen red on C13 |
| conductor-view-C20..C22 | R-01 on the real bundle | the electronics record passes the browser schema; rows of every connection equal its `conductor_lines`; the count line equals `conductor_file` | none |
