# Lane notes: home

Files: `src/routes/home/` (index, KeyNumbers, AreaTiles, NextUp, states, model, home.css), `tests/checks/home/` (home.spec.ts, run.config.ts), captures `_captures/home/`.

## What it does
- Panel (right of the shell's stage): title + design stamp (from the bundle), the exterior-not-picked banner when `ring-model.exterior.status` is not `picked`, KEY NUMBERS (one row per fact of `key-numbers`, plus a row "not known yet for this ring" for each fact the manifest message `Left out, not readable: <name>: <reason>` names; the reason shows on hover/focus), THE 8 AREAS (each tile = Link to the area, one StatePill, `why`, a stale line when `stale`), WHAT IS NEXT FOR YOU (areas whose `who` is `owner` and not done; else the first supplier requests of `open-items`; "nothing waiting" when there are none).
- Source on demand: hover or focus a key number; the link opens `fileUrl(file)` in a new tab when the file is in `files.json`, else plain text "(not in the files list)".
- Honest states: empty bundle (key-numbers and area-states both down) = ONE panel banner (`missing` or `unparsed`); otherwise a banner per section that is down; a stale record keeps its content dimmed with the stale banner. Stage steering: `useStageScene({show:'exterior', preset:'three-quarter'})`; the stage auto-rotates by itself (`__stage.autoRotate`).
- Kit: nothing from `@<org>/apps-ui` is used; its StatTiles/Tile carry their own `--nx-*` tokens and CSS and the app has no kit import, so S1 tokens + the contract's StatePill/StateBanner were used.

## Checks (`tests/checks/home`, run: `npx playwright test -c tests/checks/home/run.config.ts`)
Starts its own apps on 8804 (live bundle) and 8806 (empty bundle); stop anything on those ports first. Mutations seen red: `_captures/home/mutate.py`, log `_captures/home/MUTATIONS.log`. C01 values vs bundle · C02 8 tiles/pills/routes · C03 empty banner · C04 slab label, ring drawn and turning, no page scroll at 1512x982 and 1280x800 · C05 source on hover · C06 left-out fact · C07 next items.

## Open points for other pieces
1. Empty bundle: the browser logs one `Failed to load resource ... 404` (manifest.json). It comes from the data layer, not the screen; C03 filters 404s of `/data/` only. A "0 console errors" bar needs the dev middleware to answer an absent bundle with 200 or the data layer not to request it (src/data, tools/serve-files).
2. Empty bundle: the stage draws its own `home.state-banner` (route prop = scene route) next to the panel's; two banners with the same id are on screen. Tests scope to `app.panel`.
3. Panel height: at 1512x982 all three sections fit; at 1440x900 and 1280x800 the panel scrolls inside itself (page does not). "What is next" is then below the fold.
4. `open-items` is missing in the live bundle today (collector-open not landed); next-items then come from the areas owned by the owner.
