# Source contract: what the collector reads

The collector turns design files into the bundle. This file says how an extractor is written and which design file feeds which record. The design files under git win over any bundle copy.

## An extractor

- A module in `collector/extract/` with `RECORD` (one of the 13 record ids, `contract/schema/records.json`) and `extract(ctx) -> (data, status)`.
- `data` is the record's primary JSON (valid against its schema) or `None`.
- `status` is `'ok' | 'missing' | 'unparsed' | 'stale'`, or a dict `{status, source: [repo-relative paths], basis_version, current_version, message}`. Return `'missing'` with `None` when the source file is absent. Raise `lib.errors.SourceError(message, file)` when it is present but unreadable. Any other exception becomes `unparsed` with its text.
- When `basis_version` and `current_version` are both set and their base tokens differ (`A3` against `A4-draft`), the runner turns `ok` into `stale`. Read versions with `lib.version.read_own(text)` and `read_follows(text)`.
- `ctx` has `source_root`, `design_dir`, `out_dir`, `commit`, `rel(path)`, `source_path(rel)` and `out_path(rel)` (a safe path inside the bundle for an extra file: GLB, SVG, zip).
- A module without `extract()` is a helper and is skipped. One record has one extractor. A second extractor for a record, or a `RECORD` outside the registry, makes the run exit 1.
- The runner validates the output, runs the record's invariants (`collector/lib/invariants.py`), checks that every part id another record names exists in `parts.json`, and writes `<bundle>/<file>` as JSON with sorted keys. A record that fails validation is written nowhere and listed `unparsed`.
- Helpers in `collector/lib/`: `md` (headings, tables with line numbers), `csvread` (rows with line numbers, `split_refs`), `version`, `source.pointer(file, line)`, `errors`, `schema`, `records` (registry, constants).
- Run: `npm run collect`, or `python collector/run.py [--source <dir>] [--out <dir>] [--commit <sha>]`. `--source` reads the design from a copy (a `git archive` has no `.git`, so pass `--commit`).

## Which file feeds which record

| Record | Source files |
|---|---|
| parts | `design/bom.csv` (ring), `design/case/case-bom.csv` (case), `design/architecture.md` ("How to read this" for the evidence legend, sections 12 and 8 for open actions), `content/part-notes.json` |
| files | the project folder (see the area rule below), `git ls-files` for the tracked flag |
| part-placements, ring-model | `design/mech/placement.csv`, `design/architecture.md` section 6 stack table, `design/look/shared/envelope.py`, `design/status.json` (look picked), `design/firmware.md` section 3.3 (screen states) |
| key-numbers | `design/architecture.md` (`## Key numbers` table first, else sections 1, 2, 4), `design/mech/out/mass-estimate.csv` |
| area-states | `design/status.json`; basis against `architecture.md` current version |
| look-options | `design/look/<id>/out/ring.glb`, `plain-text.json`, `direction.md`, `design/look/shared/finishes.json`, `design/status.json` |
| electronics, schematic-pages | `design/ecad/ring/` (sheets, `netlist.csv`, `parts.csv`), `kicad-cli sch export svg`, `design/architecture.md` sections 4 and 7. Field `connection_map` of electronics: `design/wiring/connections.md` (Part 1 table, its key table and its "Count" line), `design/ecad/band/band-interface.md` sections 2 and 6, `design/ecad/case/pcb/board-notes.md` "Wiring table" and "Part g", `design/bom.csv` and `design/case/case-bom.csv` (part ids). Fields `conductor_lines`, `no_conductor` and `conductor_file` of the connection map: `design/wiring/product-wiring.csv` (one conductor per line; the columns `joint`, `id`, `signal_A/B`, `end_A_*`, `end_B_*`, `join_A/B`, `carrier_kind`, `carrier`, `state`, `state_reason`, `copper_mm_us<n>`, `cut_mm_us<n>`; the meaning of the states is in `design/wiring/build_wiring.py`). The file missing or unreadable is said in `conductor_file.status` |
| board-files | `design/ecad/ring/*.kicad_pcb` when present, else `design/mech/placement.csv`. Field `boards`: `design/ecad/ring/pcb/ring.kicad_pcb`, `design/ecad/band/flex1-us*.kicad_pcb` and `flex2-us*.kicad_pcb` (two circuits per ring size), `design/ecad/case/pcb/case_main.kicad_pcb` and `case_pins.kicad_pcb`; per board `kicad-cli pcb export svg` (one copper layer plus the outline per file) and `kicad-cli pcb drc --severity-all` (the state), both at collect time; the netlists `design/ecad/ring/netlist.csv` and `design/ecad/case/netlist.csv` only to say a board file is older than its netlist |
| firmware-rules | `design/firmware.md` sections 1.1, gesture table, motor table, joystick table |
| case | `design/case/` (`case-bom.csv`, `out/case_size.txt`, `out/parts/*.step`, `case-architecture.md`); links and boards: `out/case_params.json` (file time), `design/ecad/case/pcb/case_main.kicad_pcb` and `case_pins.kicad_pcb` (footprints), `design/wiring/lead-decisions.md` (the refit row) |
| open-items | `design/architecture.md` sections 12 and 13, `requirements.md` risks, every source line quoting `owner, <date>` |

## Folder-to-area rule (files.json `area`)

| Path starts with | Area |
|---|---|
| `design/look/` | look |
| `design/mech/` | inside |
| `design/ecad/` | electronics |
| `design/bom.csv`, `design/bom-notes.md`, `design/parts/`, `design/datasheets/` | parts |
| `design/firmware`, `design/firmware.md` | behaviour |
| `design/case/` | case |
| `design/architecture.md`, `design/status.json`, `requirements.md`, `feasibility.md`, `partners.md` | open |
| anything else | `other` |

`board` has no folder of its own yet; board files will sit under `design/ecad/` and keep the area `electronics` until the owner or the lead says otherwise.

## collector-state (key-numbers, area-states)

- key-numbers: per fact, a `## Key numbers` table of `architecture.md` first (first column names the fact, second holds the value); else the newest section that states it (17.x, then 16.x, then sections 1, 2, 4), as the file says a later section wins. A fact no place states in a readable form is left out of `facts[]` and named in the manifest message; none is guessed. Weight is the item sum of `design/mech/out/mass-estimate.csv`, accepted only when it agrees with the file's TOTAL row and the file names a design version whose base token matches the current one; a file that names none, or an older one, gives no weight fact and the manifest message says why. `value` is `<number> <unit>`, `source.line` is the line holding the number.
- area-states: the five state words of the contract only. A word outside them reads `state unknown` with the file's word in `why` (the record has no per-area `unparsed`). No status file: record `missing`, data still written with 8 x `state unknown`. Unreadable JSON: record `unparsed`. Per-area basis: `status.json` area `basis_version` if given, else the area's document (behaviour: `design/firmware.md` "Follows ... version"; parts: `design/bom-notes.md`; case: `design/case/case-architecture.md`). The record's own basis is the status file's `design_version`, so a status file made for an older design turns the record `stale`.

## collector-model (ring-model, part-placements)

Current sources (the design A5 thin ring; `design/mech/placement.csv` of design A3 is no longer read): `design/mech/thin/placement.csv`, `design/mech/thin/layers.json`, `design/mech/thin/out/thin-inside.glb`, `design/look/<folder>/out/ring-<variant>.glb` for the look id `<folder>-<variant>` of `design/status.json` (`look.picked`, else the first of `look.in_design` not in `look.rejected`), `design/firmware.md` 3.3, `design/look/shared/envelope.py`, `design/bom.csv` (reference tokens that give `part_ids`). No count or part name is held in the readers. Exterior status: `picked` only when `look.picked` is set; an in-design look ships as `not-picked` WITH `look_id` and `file` (in design, not approved); with no `status.json` it is `not-picked` with `file` null. A model file whose node names differ from the csv makes ring-model `unparsed`, naming the difference.
Axes: record numbers (centres, sizes, layer `z_min`/`z_max`, `explode`) stay in design coordinates (x along the finger, y across + thumb, z up, mm). Both GLBs are glTF Y-up: converted once in `collector/cad/glb.py` (top-level nodes get the rotation of -90 degrees about X); a record vector (x, y, z) is (x, z, -y) in a GLB. Layer `order` 0 is the bottom layer (layers.json lists top to bottom). `explode` (optional, additive): a direction vector or `radial`, from layers.json.
