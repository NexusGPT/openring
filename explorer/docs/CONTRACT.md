# Contract: Ring Explorer

Where a brief and this file disagree, this file wins: follow it and report the conflict.

This file is owned by the contract lane. It freezes what every other piece builds against. A change here is a change of the contract: it is made by the contract lane only, and every consumer is listed first. Values (ports, limits) live in `contract/schema/constants.json`, named in `docs/CONSTANTS.md`.

## 1. Output encoding

- Every string from the data bundle is rendered as React text. Nothing from the bundle is ever parsed as HTML.
- `dangerouslySetInnerHTML` is never used. A check greps `src/` for it.
- An SVG (schematic page, board plan) is shown through `<img src="/data/...">` only. It is never inlined and never put in `innerHTML`, so a script inside it cannot run. `tools/serve-files` also sends `Content-Security-Policy: default-src 'none'` with every SVG.
- A link to a design file uses `/files/<path>`; the server answers only for paths listed in `files.json`.

## 2. Line and part counts

- A LINE is one row of a parts-list csv (`design/bom.csv` for the ring, `design/case/case-bom.csv` for the case). A PART is one unit: PARTS = the sum of `quantity` over the lines.
- `parts.json` carries `totals.ring` and `totals.case`, each with `lines`, `parts`, `priced_lines`, `unpriced_lines`. The words "77 lines" and "146 parts" on any screen are `totals.ring.lines` and `totals.ring.parts`; the case is never added to them.
- A line holds `refs[]`, split from the reference cell on comma or semicolon; each token is kept as written (a range such as `R14-R22` stays one token). `quantity` is not required to equal the number of refs. `quantity` 0 is a history line the design keeps but does not fit (case-bom.csv, 'history only, NOT fitted'): it is read and kept, counts no part, and the part card says 'Not fitted (history only)'.
- Invariants enforced by the collector (`collector/lib/invariants.py`): `part_ids` equal `<bom>:<ref>` for every ref; one part id belongs to exactly one line; totals equal the lines.

## 3. Records and files (13 collected records)

The bundle is `public/data/` (or the folder named by `EXPLORER_BUNDLE`). One record = one primary file with a JSON Schema in `contract/schema/<schema>.schema.json`; the TypeScript type is made from the schema (`npm run gen:types` writes `src/contract/records.ts`; `npm run check:types` fails when it is stale). The registry is `contract/schema/records.json`.

| Record id | File in the bundle | Schema | TS type | DATA-MAP row |
|---|---|---|---|---|
| ring-model | ring-model.json (+ exterior.glb, internals.glb) | ring-model | RingModel | ring-model, with screens |
| part-placements | placements.json | part-placements | PartPlacements | part-placements |
| parts | parts.json | parts | Parts | parts (ring and case lines) |
| key-numbers | facts.json | key-numbers | KeyNumbers | key-numbers |
| area-states | areas.json | area-states | AreaStates | area-states |
| look-options | looks/index.json (+ looks/) | look-options | LookOptions | look-options |
| electronics | electronics.json | electronics | Electronics | blocks, plus pin plan and power budget |
| schematic-pages | schematic/index.json (+ pages) | schematic-pages | SchematicPages | schematic-pages |
| board-files | board/index.json (+ svg per board and copper layer, one rules report per board) | board-files | BoardFiles | board-files |
| firmware-rules | behaviour.json | firmware-rules | FirmwareRules | firmware-rules |
| case | case/index.json (+ case.glb) | case | Case | case-model, case-facts, case-parts |
| open-items | open.json | open-items | OpenItems | open-items, decisions |
| files | files.json (+ bundle.zip) | files | Files | files |

Besides these: `manifest.json` (schema `manifest`) and the hand-written part notes (schema `content/part-notes`, type `PartNotes`). The notes are not extracted, but they travel with the bundle: the collector validates `explorer/content/part-notes.json` and copies it to `<bundle>/content/part-notes.json`, listed in `manifest.content["part-notes"]` (same fields as a record entry: `ok`, `missing` when the file is absent, `unparsed` when it breaks the schema, the word limits or the no-absolute-path rule). The one URL is `dataUrl('content/part-notes.json')`, which works in dev, preview and the static build; the app reads it with `loadPartNotes()` / `usePartNotes()` from `src/data`, never from `/content/...`. The manifest still lists exactly 13 `records`.

`manifest.json` = `{built_at, git_commit, git_dirty, source_root, records:{<record>:{status, source[], basis_version, current_version, message}}}`. It always lists all 13 records.

Rules for every record:
- Every value carries `source: {file, line}` (file relative to the repository root). No value without one.
- The app never computes a ring fact: it renders bundle values.
- A shape changes only by adding an OPTIONAL field. A new required field is a contract change that lists every consumer first. Schemas refuse unknown properties, so a producer cannot add a field the schema does not know.
- Case parts are stored once, in `parts.json` (`bom: "case"`). `case/index.json` holds their ids (`part_ids`), never a copy.
- `ring-model.json` holds the screen geometry and the fields drawn per screen state (`screens`). There is no separate screens file.
- `exterior.status`: `picked` (approved model), `in-design` (a model file exists, not approved: the stage shows it, banner `exterior-in-design`), `not-picked` (no exterior model: the stage shows a plain black slab at the ring's true size, `block.size_mm`, banner `exterior-not-picked`), `absent`. Rejected exteriors are never in the bundle as current options and never shown.

## 4. Component-to-shape map

| Piece | Reads |
|---|---|
| shell (tab bar, freshness stamp) | manifest |
| StateBanner, StatePill (`src/contract/ui`) | a manifest entry, or `areas[].state` |
| Stage (3D) | ring-model, part-placements, look-options (models), case (models) |
| PartCard | one `parts` line + its `part-notes` entry + `files` (source links) |
| SvgViewer | the `svg` paths of schematic-pages and board-files |
| Home | key-numbers, area-states, ring-model, open-items |
| Look | look-options, ring-model |
| Inside | ring-model, part-placements, parts, part-notes, files |
| Electronics | electronics (incl. connection_map), schematic-pages, parts, board-files (the boards a connection end opens), files |
| Board | board-files (incl. boards[]), parts, area-states, electronics (the connections of the shown board) |
| Parts | parts, part-notes, files |
| Behaviour | firmware-rules, ring-model (screens) |
| Case | case, parts, part-notes |
| Open items and files | open-items, files, area-states |
| behaviour engine | firmware-rules only |

Data access in the app goes through `src/data` (`useRecord(id)`): it validates every record against its schema in the browser and returns one honest state. A screen never calls `fetch` itself.

## 5. Honest-state vocabulary

A record is in one of four states: `ok`, `missing`, `unparsed`, `stale`. The words are in `src/contract/vocabulary.ts` and nowhere else; banners and pills render them, a screen never writes its own.

- missing: "Not built yet. Run npm run collect."
- unparsed: "The file changed and cannot be read: <file>. Fix the file, then run npm run collect."
- stale: "Made for design <basis>; the design is now <current>. Being redone." The content stays on screen, dimmed.
- exterior not designed (no exterior model): "Exterior not designed yet. The stage shows a plain black slab at the ring's true size." (key `exterior-not-picked`)
- exterior in design (a model exists, not approved): "Exterior in design, not approved yet. The stage shows the model drawn so far." (key `exterior-in-design`)
- new options: "New options in design."
- board not routed: "Board not routed yet. Missing: <list>." (the list comes from the bundle)
- Area pill words, exactly: done, in progress, not started, waiting on a supplier, state unknown.

A screen whose source is missing, unreadable or made for an older design says so in words and still shows what it has. Staleness: the extractor reads the version a file was made for (`follows ... A3`) and the current design version (`Version A4-draft`); the base tokens (A3, A4) are compared, so `A4` and `A4-draft` match.

## 6. Test id grammar

`data-testid` = `<route>.<element>`; route is one of `home look inside electronics board parts behaviour case open`, or `app` for the shell; element is kebab-case (`inside.part-card`, `app.tab-bar`). A shared component takes the route that hosts it (`parts.state-banner`). A test selects by exact id, or by suffix: `[data-testid$=".part-card"]`. Helpers: `testId()` in `src/contract/ids.ts`, `byTestId()` and `bySuffix()` in `tests/support/page.ts`.

Departure from the plan: the acceptance texts in `docs/plan.json` write bare ids (`[data-testid=state-banner]`, `part-card`, `area-tile`). Read each as the suffix form of the grammar above.

## 7. Part id grammar

`<bom>:<ref>`, bom in `{ring, case}`, ref = a token from the reference cell (`ring:BT1`, `case:P1`). Regex `PART_ID_RE` in `src/contract/ids.ts`. The URL keeps the selection as `?part=<id>` (url-encoded).

## 8. Check ids

Each lane numbers its checks `<lane>-C01..C99` (regex `CHECK_ID_RE`), using its lane id from `docs/lane-dag.json`: shell-C01..C99, stage-C01..C99, svg-viewer-C01..C99, part-card-C01..C99, part-notes-C01..C99, collector-parts-C01..C99, collector-model-C01..C99, collector-state-C01..C99, collector-look-C01..C99, collector-electronics-C01..C99, collector-board-C01..C99, collector-behaviour-C01..C99, collector-case-C01..C99, collector-open-C01..C99, behaviour-engine-C01..C99, home-C01..C99, look-C01..C99, inside-C01..C99, electronics-C01..C99, board-C01..C99, parts-C01..C99, behaviour-C01..C99, case-C01..C99, open-files-C01..C99, fixture-a3-C01..C99, journeys-a-C01..C99, journeys-b-C01..C99, seams-C01..C99, smoke-perf-C01..C99, contract-C01..C99, wiring-data-C01..C99, wiring-screens-C01..C99, design-sync-C01..C99, case-true-C01..C99, screen-face-C01..C99, conductor-view-C01..C99. A check id is unique across the repository.

## 9. Ports, hosts, files

- App: 127.0.0.1 port 8790, `strictPort`. A second server on the port fails; it never moves.
- Journeys and tests started by Playwright: 127.0.0.1 port 8797.
- Nothing binds to another interface. Both ports are named in `contract/schema/constants.json` (`APP_PORT`, `JOURNEY_PORT`); `npm run check:docs` fails when this file and that file disagree.
- `/data/*` is served from `EXPLORER_BUNDLE` (default `public/data`); `/files/<path>` from the repo root (`EXPLORER_SOURCE`, default the parent folder), read-only, only for paths listed in `files.json`, never outside the repo root.
- No file loads from the internet: fonts, three.js, React, the meshopt decoder come from npm packages. The Playwright helper `blockOffline` aborts every request to a host other than 127.0.0.1.

## 10. Hosted-ready: nothing exists only in the dev server

The app is local-first and is later put online as a static site. Rules:
- `npm run build` = `vite build` + `scripts/stage-static.mjs`. `dist/` is then complete for any static host, in any sub-path (`base` is relative): `dist/data/` is the whole data bundle, `dist/files/<path>` holds every file listed in `files.json` (allow-list only; a listed file that is not on disk fails the build). The partner bundle zip is built by the collector ahead of time (inside the data bundle, listed in `files.json`), never on request.
- The `/data` and `/files` middleware in `tools/serve-files` is for local development only. The app never builds those URLs by hand: it calls `dataUrl(rel)` and `fileUrl(path)` from `src/data/urls.ts`, which are relative to the app root (read from where the script was loaded), and gives the router `routerBasename()`. A link to a design file is always `fileUrl(<path from files.json>)`.
- No absolute localhost address, no port, no absolute path in app source (the guard fails on `localhost`, `127.0.0.1` and any external http(s) address), in the build output or in the bundle (the collector refuses a record holding an absolute path, a drive path, `file://` or a local host name, and `manifest.source_root` is the relative name of the design folder). Extractors turn source paths relative with `lib.source.relativize`.
- Check that can fail: `npm run test:hosted` (`tests/static/hosted.spec.ts`) builds the app, serves `dist/` with a plain static node server (no vite) on a free port under `/ring/`, loads the home route with 0 console errors and 0 http errors, requires that the app itself read `/ring/data/manifest.json`, requires the part notes (`data/content/part-notes.json`, made by the collector) and one listed file to answer 200 from `/ring/files/<path>` and an unlisted file to answer 404, and scans the build for absolute addresses and paths. It needs the shell (`src/main.tsx`); `HOSTED_ENTRY=<html>` builds another entry to prove the mechanics before then.
- Hosting itself, sign-in and who may open the site are not decided here.

## 11. Stage test API

`window.__stage` is typed in `src/contract/stage-api.ts` (`StageApi`). The stage lane implements it; checks read only those members.

## 12. Bundles used by tests

- `fixture`: `.cache/fixture-99dfb85/data` and `.cache/fixture-99dfb85/src` (made by the fixture lane).
- `sample`: `tests/support/sample-bundle` (made-up values, part ref `ZZ9`; for the contract's own tests and the guard).
- `empty`: a new empty folder; every record then reads missing.
- Choose with `EXPLORER_BUNDLE` and `EXPLORER_SOURCE`; helpers in `tests/support/bundle.ts`.

## 13. No ring facts in source

`npm run guard` reads the sample bundle (and the fixture bundle when built), collects every part ref, maker part number, firmware state id and label, finish name, look title and size string, and fails when one appears in `src/**` (test files excluded). Test files may name sample or fixture values.

## 14. Departures from the plan, found while building the contract

1. 13 collected records, as the brief counts: the plan's 14 DATA-MAP rows minus the hand-written part-notes. `screens.json` is folded into `ring-model.json`; the DATA-MAP row "blocks" is the record `electronics` (blocks, links, pin plan, power budget in `electronics.json`, the name the plan's checks use). The 14 schema names printed by `python collector/run.py --check-schemas` are these 13 plus `manifest`; the part-notes schema is printed on stderr as `content: content/part-notes`; `common` holds shared definitions.
2. `npx playwright test --list` exits 1 with "No tests found" when no test exists (Playwright 1.65; only the `--pass-with-no-tests` flag changes it). The contract owns one real test, `tests/support/support.spec.ts`, so the command exits 0 and lists 1 test.
3. The design venv has no `pytest` and no `jsonschema` package. The collector validates with its own small validator (`collector/lib/schema.py`, standard library only); pytest runs from `.venv-pytest` in this folder (`python3 -m venv .venv-pytest && .venv-pytest/bin/pip install pytest`; gitignored). The design venv is untouched.

## 15. Wiring: the boards list and the connection map (added 2026-11-13, owner's ask "you need to do the wiring on the ring explorer")

Two OPTIONAL fields on existing records. The manifest still lists exactly 13 records. A consumer reads them as "not in the data" when absent.

`board-files.boards[]` (read by Board; made by `collector/extract/boards.py`, called from `board.py`): one entry per board file.
- Boards: the ring's main board (`group` `ring`), the band circuits (`band-1`, `band-2`, one entry per ring size, `size_label` such as `US 9`), the case boards (`case-main`, `case-pins`). A group whose file is not there still has an entry: `file` null, `state.status` `not-checked`, the words say which file is missing.
- `id`, `group`, `title`, `what` (plain words), `size_label`, `file` (repo-relative), `file_time` (`YYYY-MM-DD HH:MM`, time of the board file), `outline` (same shape as the record's own), `layers[]`, `placements[]`, `missing[]`, `notes[]`, `state`.
- `layers[]`: one per copper layer of the board file: `id` (the file's own name, e.g. `F.Cu`), `label` (plain words: Top copper, Bottom copper, Inner copper N), `svg` (a bundle path `board/<id>/<layer>.svg`, made by `kicad-cli pcb export svg` with the board outline in each file, every layer seen from above, page = board area, so the picture starts at the outline's corner), `items` (tracks, vias, zones and pads on the layer, counted in the board file; 0 means the layer has no copper).
- `placements[]`: the parts on each face: `ref`, `part_id` (null when the parts list has no such line; a range token such as `P1-P4` holds its members), `value`, centre `x`, `y` and size `w`, `h` in the board file's own mm (y counts downwards), `side` `top` or `bottom`.
- `state`: `status` `routed-checked` | `not-finished` | `not-checked`; `violations` and `open_connections` are the numbers of the rules report saved at `report` (`board/<id>/drc.rpt`, made at collect time by `kicad-cli pcb drc --severity-all`); they equal its count lines `** Found N DRC violations **` and `** Found N unconnected pads **`, which `report_lines` repeats. `words` is exactly `routed and checked: 0 violations, 0 open connections` when both are 0, else `not finished: N connections open, M violations` (`1 connection`, `1 violation` in the singular); for `not-checked` it says why the check did not run. The screen shows `words` with `file_time` and `checked_at`; it never writes a state word of its own.
- Honest remarks about the files go to `notes[]` (for example: the board file is older than its netlist).

`electronics.connection_map` (read by Electronics; made by `collector/extract/wiring.py`, called from `electronics.py`): the boards and off-board parts as `nodes[]`, every joint as `connections[]`.
- Source: `design/wiring/connections.md`, its Part 1 table. A row the file marks "No joint" is not a connection. `stated_count` is the count the file states ("Count: N joints"); `note` says when the table holds another number or cannot be read.
- `nodes[]`: `id`, `label` (plain words), `kind` `board` | `part`, `board` (for a board node, its group id in `board-files.boards[].group`: the click on this end opens that board), `scope` `ring` | `case`, `part_ids[]`.
- `connections[]`: `id` (the file's own, R1 to R16, C1 to C6), `signal` (nets or supplies as the file writes them), `ends[]` (exactly two: `node` and `text`, the end in the file's words: part, land or pin), `how` (`kind`: hot bar, soldered land, spring pin, lead wire, connector, touch with no contact, gold disc, board track, flex circuit line, not stated or other; `text` the carrier in the file's words; `conductors`), `drawn` (`state` `drawn` | `not-drawn`, `words` the file's own), `details[]` (rows read from `design/ecad/band/band-interface.md` sections 2 and 6 and `design/ecad/case/pcb/board-notes.md` "Wiring table" and "Part g": land lists, lead cut lengths, wire cut lengths, ring pad to case pin), `proof[]` (the files named by the row's "Stated at" cell, through the key table at the head of connections.md, each with its lines and the nearest section heading), `source` (the row in connections.md).
- A connection the sources mark "NOT DRAWN" has `drawn.state` `not-drawn` and is shown as open, in words.

Check ids of this change: wiring-data-C01..C99 (the tests of `collector/tests/collector-wiring` and `collector-boards`) and wiring-screens-C01..C99 (the unit tests beside the two routes).

## 16. Case: every solid linked, every line placed (added 2026-11-13, owner's words "You need to make sure we have the true case with everything")

Six OPTIONAL fields on `case/index.json` (made by `collector/extract/case_links.py`, called from `case.py`). A consumer reads them as "not in the data" when absent. The manifest still lists exactly 13 records.

- `lines[]`: one entry per line of `design/case/case-bom.csv` (90 today), each in exactly ONE class: `solid` (a solid of the model is that part: `nodes[]` names them), `board` (a footprint of a case board carries its reference: `boards[]` names the board keys), `not-fitted` (quantity 0, "history only, NOT fitted"), `no-solid` (none of these: `reason` says why in the words of the line's own cells). Also `id` (the line's first part id), `part_ids[]`, `source` (its row in the csv).
- `counts`: `lines`, `solid`, `board`, `not_fitted`, `no_solid` (they add up to `lines`), `nodes`, `nodes_linked`, `nodes_unlinked`. The Case screen's counts line is these numbers.
- `glb.nodes[].part_ids[]`: the ids of the lines a solid stands for, by the rules of the extractor (reference token in the name, own part name in back quotes, file name in the source cell, maker part number, a child of another solid, the words of the function). A board's solid also holds the ids of the parts its board file carries, its own line first (so a click on the board opens the board's card). A solid no rule links has no ids and is named in `unlinked_nodes[]` with the text "no parts-list line".
- `boards[]`: `key` (`main`, `pins`: the word after the first underscore of the board file's name), `title` (the Board picker's title), `node` (the solid that is the board), `picker` (the Board picker's group id, for `/board?board=<picker>`), `file`, `parts[]` (`ref`, `value`, `part_id`, `what`: every footprint of the file, with its parts-list line when there is one).
- `model`: the model's parameter file (`design/case/out/case_params.json`) and its file time. `refit`: the decision cell of the row "block height ...: what follows" of `design/wiring/lead-decisions.md`, with its place, or null when the file has no such row. The app shows both as they are and writes no decision of its own.
- Bounds the collector test sets from the design of 13 November 2026: at most 5 lines without a solid (3 today), at most 2 solids without a line (0 today).

Check ids of this change: case-true-C01..C99 (the unit tests of `src/routes/case/case.test.tsx`, the collector tests of `collector/tests/collector-case/test_links.py` and `test_link_rules.py`).

Change 2026-11-13 (follow-up of lane case-true): `connection_map.connections[].drawn.state` is `drawn` | `text-only` | `not-drawn`: `not-drawn` when the "Drawn?" cell begins "Not drawn", `text-only` when it begins "Stated in text only"; both are shown as open. New optional `connections[].conductors` (`complete`, `total`): the conductor lines of `design/wiring/product-wiring.csv` whose `joint` column names the joint (a line with `carrier_kind` none is no conductor); complete = state `drawn and routed` or `specified and landed` (the two states of `COMPLETE` in `design/wiring/build_wiring.py`, compared by a test). The detail panel shows "N of M conductors complete" in its state line.

Change 2026-11-13 (lane conductor-view, owner: "the connexions and wiring is far from being 100% i see"; SPEC row 19): three OPTIONAL fields, so a bundle without them stays valid (the screen then says "not in the data yet"). Made by `collector/extract/wiring.py` (`conductor_data`) from `design/wiring/product-wiring.csv`.
- `connection_map.connections[].conductor_lines[]`: each conductor whose `joint` column names the connection, in the file's order. `id` (W001...), `signal_a`, `signal_b` (the columns `signal_A`, `signal_B`), `first` and `last` (`board`, `part`, `pin`, `face`, `join`: the columns `end_A_board`, `end_A_ref`, `end_A_pin`, `end_A_face`, `join_A`, and the same with B), `carrier` (`kind` = `carrier_kind`, `text` = `carrier`), `state`, `state_reason`, `lengths[]` (`size` "US n", `kind` `copper` | `cut`, `mm` as the file writes it: from the columns `copper_mm_us<n>` and `cut_mm_us<n>` that are filled), `source` (`design/wiring/product-wiring.csv` and the 1-based first line of the row).
- `connection_map.connections[].no_conductor[]`: a line of the file whose `carrier_kind` is `none` (no conductor): `id`, `reason` (its `carrier` text), `state`, `state_reason`, `source`. Never in `conductor_lines`, never in a count.
- `connection_map.conductor_file`: `status` `ok` | `missing` | `unreadable`, `note` (words, when not ok), `complete` and `total` over every conductor line of the file (complete = the two `COMPLETE` states, as for `conductors`), `no_conductor` (how many lines have no conductor), `source`. The Electronics count line above the map is exactly `complete` of `total`.
- `conductors` (the count of a connection) equals the length of its `conductor_lines`; the screen says in words when it does not.
Check ids of this change: conductor-view-C01..C99 (collector tests `collector/tests/collector-wiring/test_conductors.py`; unit tests `src/routes/electronics/conductors.test.tsx` and `conductors.real.test.tsx`).
