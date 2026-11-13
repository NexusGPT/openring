# Lane notes: open-files

Files: `src/routes/open-files/` (index, OpenItems, ItemRow, model, BundleCard, HandOff, AreaFiles, FileLine, Disclosure, filesModel, format, states, open.css), `tests/checks/open-files/` (open-files.spec.ts, made.ts, run.config.ts), captures `_captures/open-files/`.

## What it does
- Panel (right of the shell's stage): title + the `open` area pill, then two sections.
- OPEN ITEMS: chips (all, waiting on a supplier, bench tests, risks, decisions; `aria-pressed`, each with its count). Four groups; a supplier row = who (left) + item, what to ask, source; decisions newest first with date, quote, speaker, source. In the "all" view a group shows 5 rows and "Show N more" (the rest stay in the page). The supplier chip adds one chip per supplier ("who must act"). A filter that leaves nothing says `nothing waiting`.
- FILES (`/open#files`, the top-bar "Files" entry): (1) "For a build partner": `Download partner bundle` (a link with `download` to `dataUrl(bundle.file)`), size and file count, "What is inside" lists every entry. Disabled with `run npm run collect` when `files.bundle` is null or the zip does not answer (HEAD check, an HTML answer counts as absent). (2) "For a manufacturer" and "For a 3D printer", read from `files.json` by PATH RULES in `filesModel.ts`: manufacturer = wiring-diagram PDF, parts list, then under `design/mfg/` specification, drawing (PDF), STEP; printer = every `.stl` under `design/mfg/`, grouped by part, a `size<N>` token in the name becomes "Ring size N" in numeric order. A kind or set with no file says `Not made yet` and what is coming; no dead link. (3) "Every file, by area": one closed group per area (count and total size), a name search that opens the groups it finds rows in. Each row: name, folder, size, date, Open (new tab) and Save (download); URLs through `fileUrl()` (a `+` is encoded).
- Honest states: a record that is down shows the contract's banner (`StateBanner route="open"`); the other section still shows. Stale = content dimmed + banner. Manifest message of `files` (what is left out) shows as one quiet line.
- Motion: shell tokens only; groups open with a grid-rows + opacity transition, rows fade on a filter change, instant under `prefers-reduced-motion` (primitives.css). The jump to `#files` is an instant scroll (a smooth scroll was cancelled under load and left the section out of view: C10 red once).

## Conflicts between the dispatch message and the brief (the brief won)
1. Dispatch: write to `src/routes/open/`. Brief `Owns`: `src/routes/open-files/**`. Built in `open-files/` (the shell maps that folder to the route `open`, `src/app/routes.ts`).
2. Brief work items count 7 supplier rows and 8 area groups ("on the fixture"); the live bundle has 13 supplier rows and 8 areas (look, inside, electronics, parts, behaviour, case, open, other: no `board`). The screen shows what the bundle holds.
3. Brief `TESTS`: "docs/TEST-PLAN.md has no `## TESTS` block" but TEST-PLAN.md section 3 lists open-files-C01..C03 (rows around line 331). My ids C01..C12 cover those three rows and more.

## Checks (`tests/checks/open-files`, run: `npx playwright test -c tests/checks/open-files/run.config.ts`)
Starts its own apps on 8821 (made-up bundle), 8822 (0 suppliers, no zip, empty hand-off), 8823 (empty bundle), 8824 (live bundle); stops only those. C01 groups, who, date order · C02 chip + who chips + aria-pressed · C03 nothing waiting · C04 area groups, size/date, `+` file bytes · C05 zip download size + entries · C06 hand-off sets and ring sizes · C07 Not made yet · C08 disabled button · C09 empty bundle · C10 Files lands on the section · C11 no page scroll at 3 viewports · C12 live bundle counts.

## Open points for other pieces
1. The classification of the hand-off files is by path rule (`design/mfg/`, `.stl`, `.step`, a name with `spec` or `wiring`, the file `bom.csv`). When the design lane names the folders differently (for example a subfolder per part) the rules in `filesModel.ts` are the one place to change; the collector's `files.json` needs no new field.
2. Empty bundle: the browser logs one `Failed to load resource ... 404` (manifest.json), from the data layer, as in the home notes. C09 allows only that `/data/` 404.
3. The panel is not widened by this screen (the shell owns the expand state; the owner has the expand button). At 1440x900 the rows fit the default width.
4. Mutation evidence: `_captures/open-files/MUTATIONS.log` (run on a copy of the folder, `MUT_ROOT=<copy> python3 _captures/open-files/mutate.py`, so the owner's running app never saw a broken file). C01..C10 and C12 went red on their mutation; C11's first three mutations stayed green (the overflow was clipped or fitted) and are logged as invalid; the fourth (`.groups` 900px wide) went red.
5. The stage draws its own `open.state-banner` on an empty bundle next to the panel's (same note as home): C09 counts the panel's.
6. The collector rewrites `public/data` while it runs; a check reading it at that moment fails. C12 reads the live bundle only inside its own test.
7. Under a machine load above 100 (other helpers rendering WebGL) the checks take 5 minutes and a check can time out; a rerun of that one check passes.
