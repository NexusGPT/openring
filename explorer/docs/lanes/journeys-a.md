# Lane notes: journeys-a

Files: `journeys/J1.spec.ts` (J1#1 to J1#4), `journeys/J3.spec.ts` (J3#1 to J3#3), `journeys/J6.spec.ts` (J6#1, J6#2). Proof runs: `_captures/journeys-a/`.

## How to run
- Bundle: `EXPLORER_BUNDLE=<folder>` (default `.cache/fixture-99dfb85/data`, which does not exist until piece `fixture-a3`). Design files: `EXPLORER_SOURCE=<folder holding design/>` (default `.cache/fixture-99dfb85/src`). The Playwright config reads the same two variables for the server, so the tests and the app see one bundle.
- Until the fixture exists: `EXPLORER_BUNDLE=$PWD/public/data EXPLORER_SOURCE=$(dirname $PWD) npm run journeys -- J1 J3 J6` (from the explorer folder). Headless, port 8797, started and stopped by the run.
- A missing bundle stops a test with: "journey setup: no bundle at <path> (manifest.json missing). Set EXPLORER_BUNDLE ...".
- Every expected value (key numbers, area states, layer ids, part line, note, open items, board plan, file list, totals) is read from the bundle, `content/part-notes.json` or the design file. No ring fact is typed in a spec.
- Every step arrives by the click the journey names (tile, top bar entry). Only J1.1 types the address (`/`); J3.1 types `/parts` only as a starting point, then clicks top bar "Home".
- Test titles hold the id in quotes once (`const J1_1 = "J1#1"`): `grep -ohE '"J[0-9]+#[0-9]+"' journeys/*.ts | sort | uniq -d` prints nothing.

## Element ids the specs need (grammar `<route>.<element>`; none of these were pinned in docs, so the screen pieces must match them)
| id | where | what the spec reads |
|---|---|---|
| `app.tab-home`, `app.tab-open`, `app.tab-files`, `app.tab-parts`, `app.tab-board` | shell (exist) | top bar entries; `aria-current="page"` on the current one |
| `app.stage` > `canvas`; `window.__stage` | shell, stage | drag, screenshots, `azimuthDeg`, `autoRotate`, `explode`, `layerBoxes`, `screenPos` |
| `home.section-numbers` > `home.key-number` (`data-fact=<fact id>`) | Home (as built) | each fact row shows the fact value from facts.json |
| `home.area-tile` with `data-area=<id>`, one `home.state-pill` (`data-state`) inside | Home (as built) | pill text = areas.json state; click = go to that route |
| `inside.explode-slider` (accessible name "Open it up"), `inside.explode-open` | Inside (as built) | slider: real mouse drag; J1#3/J1#4 open the ring with `inside.explode-open` first |
| `inside.layer-row` (one per layer, label text) | Inside | label of each layer of placements.json |
| `inside.part-card` (`data-part-id`), `inside.part-card-exact-toggle`, `inside.part-card-exact`, `inside.part-card-no-line` | PartCard (exist) | card text, exact data, source links (`a[target=_blank]`, or `[aria-disabled=true]` with "not on disk") |
| `board.state-banner`, `board.plan-mark` with `data-side=top\|bottom` | Board | banner words from the vocabulary + `missing[]`; one mark per placement |
| `open.item-row` with `data-id`, `data-group` (`decision` for decisions), `data-date` on decisions; `open.item-who`, `open.item-ask`; `open.group-heading` (4); `open.filter-chip` ("waiting on a supplier") | Open items | row counts, supplier rows, dates newest first |
| `open.file-group` with `data-area`; `open.file-row`, `open.file-size`, `open.file-date`; `open.download-bundle`; `open.bundle-entry` | Files section (`/open#files`) | groups = distinct areas of files.json; download; entries listed |
| `parts.totals`, `parts.export-csv` | Parts | "<n> lines" and "<n> parts" of the ring totals; download `bom.csv` |

## What each test asserts (first assertion is a visible element, so a missing screen fails at once with a named message)
- J1#1: key numbers panel shows every fact value; 8 tiles, each one pill equal to its state; stage ready; canvas at least 2 % non-background; after a 200 px drag azimuth moved over 20 degrees, `autoRotate` is false and stays still, picture differs by at least 1 %; no console or http error; no "npm run collect" text.
- J1#2: Home tile "Inside" leads to `/inside`; slider drag 0 to 1 gives `explode()` over 0.95; every consecutive layer pair is at least `EXPLODE_MIN_GAP_MM` apart and further apart than when closed; picture differs by at least 2 %; one layer row per layer.
- J1#3: click at `screenPos(<model name of ring:BT1>)` opens `inside.part-card` for `ring:BT1` (URL `part=ring%3ABT1`); card holds the note what and why, each size number, key figures, the open action; maker part number hidden until "Exact data" opens; the pixels around the cell change; control: an object with no parts-list line shows "no parts-list line for this object".
- J1#4: the source link of BT1 (a file on disk and listed in files.json) opens a new tab at `/files/<path>`, answers 200, not HTML, not empty. Branch for an unserved source (greyed, "not on disk") runs only when the bundle has a model-linked part with one; otherwise an annotation `not-exercised` is recorded.
- J3#1: Home reached by the top bar; pills equal areas.json and are vocabulary words; click Board gives `/board`, tab "Board" current.
- J3#2: banner contains the vocabulary sentence and every `missing` entry (absent when the bundle says routed); plan marks equal the placements, per side.
- J3#3: before the chip, rows = all four groups; 4 headings; decision dates newest first; after the chip exactly the supplier requests, each with its who and its ask.
- J6#1: files grouped by every area in files.json with size and date; download event; `.zip`; size equals files.json; starts with `PK`; `unzip -tq` clean; entry count equals the page list; the file with a plus sign in its name is in the zip with the same sha256 as the design file.
- J6#2: totals text; download named `bom.csv`; sha256 equals `design/bom.csv`; an independent CSV reader finds as many records as the ring parts total (parser cross-checked against Python: 78 and 78).

## State today
- Fork point 0a6bd65 (no shell, no screens), clean archive copy: 9 of 9 red, each on a missing element, quoted in `_captures/journeys-a/red-run-forkpoint.txt`.
- Shared working copy: screens land while this lane runs (Home, Inside), so a step can be green there when its surface is built (J3#1 was green once Home landed). `_captures/journeys-a/red-run-live.txt` is the run on the working copy at the time.
- Not done: mutation evidence (break the screen, see red; remove the act, see red) needs the screens. The mutation per step is the one in docs/TEST-PLAN.md section 3 (column "red-first"); the surface lanes or the verifier run it. Nothing in these specs was seen green on a correct screen yet.

## Findings
- Element ids above were not pinned anywhere; the screen lanes must follow this table or tell this lane to change it.
- A shared journey helper file (`journeys/support.ts`) would remove the bundle-reading code repeated in the three specs; this lane does not own that path.
- Frozen-copy check (contract-C11) is not in these specs; they trust `EXPLORER_BUNDLE`. Plan text values such as "30 x 20 x 9.5 mm" are not asserted, only the bundle's own facts.
- J1.1 plan row asks for the label "Plain black slab"; not asserted (no bundle field holds it).
- Journey-C01 (all 77 lines, `journeys-a-C01`) is not written: it is a separate row, not one of the nine steps in this brief.

## Changes after the lead's round (2026-11-10, each with its reason; no assertion weakened)
1. Ids aligned to the built Home and Inside (table above). Reason: the screens carry their own ids; `home.key-numbers` never existed.
2. J1#2 opening check follows the bundle's `explode` field per layer: a vector layer moves at least the minimum gap along its direction; the radial band grows outward by at least the minimum gap; neighbouring layers with the same opening axis end at least the minimum gap apart along it (tolerance 0.001 mm for float rounding). Reason: the band wraps the body, no vertical gap exists there. The slider drag now waits for `explode()` above 0.99 (0.95 left 5 % of the travel).
3. J1#3 and J1#4 open the ring first (`inside.explode-open`), wait for `explode()` to settle, then take the point from `screenPos` (polled until not null after the route change). Reason: the journey opens the ring, then clicks the cell.
4. J1#1: after the drag the ring glides to rest (damping, slow in software rendering). The test now requires `autoRotate` false and a turn rate that falls (last half second under 1 degree or under 0.6 of the first), never a steady turn.
5. J1#3 no-line control: every object of this bundle has a parts-list line (notes plus ring-model links), so no click can show "no parts-list line"; the control records an annotation `not-exercised` instead of failing. It fails if an unlinked object is on screen and does not show the words.
6. Runs use a snapshot copy of `public/data` (the collector rewrites that folder while other pieces run; a run during a rewrite saw "Not built yet" on Home).

## Result at the end of the round (snapshot bundle, `_captures/journeys-a/run-J1-J3-6.txt`, last line `exit=1`)
J1#1 pass, J1#2 pass, J1#3 pass, J1#4 fail (greyed-link branch: a click at `screenPos('main_chip')` with the ring open selects nothing: something else is in front or the point is empty; the served-link half of J1#4 passed). J3#1 pass, J3#2 fail (no `board.plan-mark`: Board not built), J3#3 fail (no `open.item-row`: Open items not built).
