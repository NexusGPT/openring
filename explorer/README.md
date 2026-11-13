# Ring Explorer

## What it is, and who it is for

- A browser app on this Mac that shows the whole ring design: the outside, the inside, the wiring, the circuit board, every part, how the ring behaves, the charging case, and what is still open.
- It is for the owner first, who wants to see what is being built, and later for a build partner who needs exact files and order codes.
- It is a viewer. It reads the design files and shows them. It changes nothing.

## Run it

1. Build the data from the design files: `npm run collect`
2. Start the app: `npm run dev`
3. Open http://127.0.0.1:8790

The app uses port 8790 only. If that port is busy the start fails; it never moves to another port.

A shared copy (the public site) is built from a folder that leaves some files out. Name a JSON list of `{what, count, why}` in `EXPLORER_LEFT_OUT` when you run `npm run collect` for that copy: the Files screen then says what is missing.

## Prove it

- `npm test` runs the unit checks, the collector checks, the type check and the guard against ring facts written in app source.
- `npm run journeys` walks the seven journeys of `docs/JOURNEYS.md` in a headless browser on port 8797, against a frozen copy of the design.
- All tests are headless. None opens a browser window.

## Where things are

| Path | What is there |
|---|---|
| `docs/PRD.md`, `docs/JOURNEYS.md`, `docs/DATA-MAP.md` | the signed spec, the journeys, the 13 data records |
| `docs/CONTRACT.md` | the rules every screen and helper builds against; it wins over any brief |
| `contract/schema/` | one JSON Schema per record; the single source of every data shape |
| `src/contract/` | TypeScript types made from the schemas, the wording of honest states |
| `collector/` | the Python collector: design files to JSON, validated against the schemas |
| `public/data/` | the data the collector builds; deleted and rebuilt at any time, never committed |
| `tools/serve-files/` | the local file server for `/data` and `/files` |
| `src/` | the app: routes, stage, components |
| `tests/`, `journeys/` | checks and journeys |

## What it deliberately does not do

- It does not edit the design, save decisions, order parts or track suppliers.
- It has no sign-in and is not hosted. It runs on this Mac only.
- It has no phone layout and no AI chat in version 1.
- It never writes a ring fact in its own source: every value comes from the data the collector builds.

## What is not built yet

- All nine screens exist and read the collected data (13 kinds of data, all read without error on the current design).
- Not proven in a browser since 2026-11-10: the owner ordered no browser tests. The journey tests J1 to J8 are written; the last run passed 9 of 10 checks, and J2, J4, J5 and J7 were never run to the end. The changes made after that order (the Inside screen rebuild, the one-control Behaviour screen, the case materials, the "Not in this copy" list) passed the type check, the guard and the unit tests only. The owner judges the rendered screens.
- The review of every screen by independent reviewers has not run.
- The part notes generator (`collector/tests/part-notes/gen_notes.py`) fails on the newest design: the parts list has no line yet for the light pipe, and the case notes name parts of an older case.
