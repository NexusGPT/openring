# Digest: contract lane

One section per finished work item. Proofs are in `_captures/contract/`; the mutation table (16 rows, every one seen red then restored) is `_captures/contract/INVARIANT-PROBE-LOG.md`. The full Done-when run is `_captures/contract/done-when.log`.

## Setup (README, .gitignore, npm, component library)
- README.md and .gitignore written first. `<platform> apps vendor-package --dir .` placed `@<org>/apps-ui@0.9.0` in `vendor/<org>-apps-ui-0.9.0.tgz` (1.9 MB); its named next command `npm install` exited 0 (`_captures/contract/npm-install.log`, last line `exit=0`); `npm ls` shows `@<org>/apps-ui@0.9.0`.
- One `npm install` only. The first attempt failed on the shared npm cache (EACCES in `<home>/tmp/.npm-cache`), before any package was written; the one retry used a cache folder in the scratchpad. Not a space failure. Disk: 21 GB free after install; `node_modules` 795 MB.
- Playwright package installed, no browser downloaded; `tests/support/chromium.ts` finds the existing Chromium under `~/Library/Caches/ms-playwright` (override `CHROMIUM_PATH`).
- Blocked: none.

## functionality-bundle-contract
- 13 record schemas + `manifest` + `common` + `content/part-notes` in `contract/schema/`; `records.json` is the registry; `constants.json` the only home of values. TS types are generated (`npm run gen:types`, 32 declarations, `check:types` fails when stale). Schemas refuse unknown properties.
- `python collector/run.py --check-schemas` exits 0 and prints 14 names (13 records + manifest). A parts line without `refs` makes `--validate parts <file>` exit 1 (test `test_parts_line_without_refs_exits_1`, seen red).
- Choices to confirm (all in CONTRACT.md section 14): 13 records = the 14 DATA-MAP rows minus hand-written part-notes; screens folded into ring-model.json; DATA-MAP "blocks" = record `electronics` (electronics.json); case parts stored once in parts.json.

## functionality-collector-runner
- `collector/run.py` + `collector/lib/` (md, csvread, version, source, errors, schema, records, invariants). Zero extractors: exit 0, manifest lists 13 records `missing`. A raising extractor leaves only its record `unparsed` with the exception text; others byte-identical. `git_commit` equals `git rev-parse HEAD` (40 chars); a copy without `.git` needs `--commit`.
- Version reader: `Version A4-draft` read as own version, `follows ... A3` read as basis; stale when base tokens differ (A4 equals A4-draft).
- Checks: 51 pytest tests in `collector/tests/contract/`. The design venv has no pytest or jsonschema (nothing installed into it): the validator is stdlib-only (`lib/schema.py`) and pytest runs from `.venv-pytest` here (gitignored).
- `npm run collect` = `${COLLECT_PY:-../design/.venv/bin/python} collector/run.py`; run once: `collector: b6d5653 -> public/data  missing 13`.

## functionality-file-server
- `tools/serve-files` Vite plugin (dev and preview). Observed on a real server on 8790 with a bundle listing the datasheet: pdf 200 `application/pdf`; `..%2F..%2Fetc%2Fpasswd` 404; `/files/design/.venv/bin/python` 404; `lsof` shows `127.0.0.1:8790` only (`_captures/contract/lsof-8790.txt`); a second `vite` on 8790 exited 1 (`vite-second.log`). Server stopped by pid after. 10 vitest cases cover listing, traversal, symlink escape, methods, empty bundle.

## functionality-offline-local-libs
- three, React, @fontsource fonts (Libre Caslon Text, Geist sans, Geist mono) are npm dependencies; the meshopt decoder ships inside `three`. `grep -rn 'cdn.jsdelivr\|fonts.googleapis' src index.html` returns nothing; the guard also fails on any external http(s) address in `src` and `index.html` (seen red).
- NOT proven here: the 9-route offline run with `window.__stage.ready` needs the shell and the stage. The helpers exist (`blockOffline`, `waitStageReady`, tested by `tests/support/support.spec.ts`, seen red).

## consistency-no-ring-facts-guard
- `scripts/guard-no-ring-facts.mjs`, part of `npm test`. Clean tree exit 0; adding `const x = 'ZZ9'` under `src` exit 1 naming file and token, then reverted. Tokens come from the sample bundle (made-up values) and, once built, the fixture bundle; test files are excluded.

## ux-honest-states
- `src/contract/vocabulary.ts` (total records, area pill words exact), `StateBanner`, `StatePill` in `src/contract/ui/`, loader `src/data/` (one honest state per record, never blank). 27 vitest cases, mutations seen red.
- NOT proven here: the 9-route empty-bundle run (needs the shell).

## Done-when (run from the explorer folder, `_captures/contract/done-when.log`)
1. npm install exit 0, apps-ui from vendor/: pass (`exit=0`, `npm ls` shows `@<org>/apps-ui@0.9.0`).
2. `npx tsc --noEmit`: exit 0, `error TS` count 0: pass.
3. `collector/run.py` with no extractors: exit 0, 13 records `missing`: pass.
4. `pytest collector/tests/contract`: `51 passed`: pass.
5. `npx playwright test --list -c tests/playwright.config.ts`: exit 0 with 1 test, not 0: pass on exit code, differs on count (Playwright exits 1 for an empty suite; CONTRACT section 14).
6. CONTRACT.md statements: `check-contract-doc: ok (30 lane check ranges, 9 constants)`: pass.

## Hosted-ready
Owner news: the app will be put online as a static site. Changed, so nothing exists only in the dev server:
- `npm run build` = `vite build` + `scripts/stage-static.mjs`: copies the data bundle to `dist/data/` and every file listed in `files.json` (allow-list; a listed file missing on disk fails the build) to `dist/files/<path>`. The partner zip is built by the collector, so it is already in the bundle. `vite.config.ts` has a relative `base`, so the build works from `/` and from `/ring/`.
- `src/data/urls.ts`: `dataUrl()`, `fileUrl()`, `routerBasename()`, all relative to the app root read from the loaded script. The loader uses them; the shell must give the router `routerBasename()` and never write `/data` or `/files` by hand. `tools/serve-files` stays for local development. Rule written in CONTRACT.md section 10.
- No absolute address, port or path: `manifest.source_root` is now the design folder's name (schema refuses `/`, drive paths, `file:`); the collector marks a record `unparsed` when any string holds an absolute path, drive path, `file://`, `localhost` or `127.0.0.1` (`lib/invariants.check_no_absolute`; `lib/source.relativize` for extractors: the bom.csv source cells hold absolute paths today, the parts extractor must relativize them); the guard now fails on `localhost`, `127.0.0.1` and any external http(s) address in `src` and `index.html`. `index.html` got `<link rel="icon" href="data:,">` so a host without a favicon gives no 404.
- Check that can fail: `npm run test:hosted` (`tests/static/hosted.spec.ts`): builds, serves `dist/` with a plain node static server (`tests/support/static-server.ts`, no vite) on a free port under `/ring/`, loads the home route: 0 console errors and 0 http errors, the app itself read `/ring/data/manifest.json`, one listed file answers 200 under `/ring/files/`, an unlisted file answers 404, and no absolute address or path is in the build.
- Proof so far: run against a probe entry (`HOSTED_ENTRY`, files in `_captures/contract/probe/`) on the sample bundle: 2 passed (`_captures/contract/hosted-probe.log`). Seen red: dataUrl returning `/data/...` (manifest 404 under `/ring/`); a `http://localhost` string used in the build; stage-static copying the whole source. NOT proven: the real home route; `npm run build` fails until the shell's `src/main.tsx` is merged, so the spec stays red against the real entry until then.
- Tests added: 55 pytest (was 51), 30 vitest (was 27).

## Conflicts to report
- Plan acceptance texts use bare test ids (`[data-testid=state-banner]`); CONTRACT section 6 sets `<route>.<element>`, read as the suffix form.
- Plan file names `screens.json`, `blocks.json` differ from the contract (section 14).
- Hook TESTPLAN1 fired on the first source write: journeys are written by the journey lanes, not this one.
- Playwright `webServer` runs in the config folder; `cwd: '..'` is set so vite finds its config.
- Could not open `REF/browser-mechanics.md` from the explorer folder at first (project root `.claude/` is not above it); read it later from the path the hook gave.

RESULT: done, 6 of 6 Done-when lines pass (the playwright list shows 1 test instead of 0).

## Probe by the lead, 2026-11-10: do part names survive from a STEP design file to the browser model?

Yes. `collector/cad/step_to_glb.py` run by the lead on `design/mech/thin/out/thin-inside.step`: the result has 38 nodes, all 38 named: 1 assembly node and the 37 parts of `placement.csv`, in the same names (`outer_body`, `band_liner`, `cover_glass`, ...). The case reader can therefore build its model from the case's STEP file with real shapes and names; true-size blocks are not needed as a fallback.

## conductor-view (2026-11-13)
- Electronics: each connection lists its conductors one by one from `design/wiring/product-wiring.csv`; fields `conductor_lines`, `no_conductor`, `conductor_file` (CONTRACT.md section 15). Handoff: `docs/lanes/conductor-view.handoff.md`.
