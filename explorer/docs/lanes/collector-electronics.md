# Lane: collector-electronics

Files: `collector/extract/schematic.py` (record schematic-pages), `collector/extract/electronics.py` (record electronics), `collector/tests/collector-electronics/test_electronics.py`.

## What the records hold
- Pages: the root page (id `overview`) and every `(sheet ...)` of `design/ecad/ring/ring.kicad_sch`; title = Sheetname, number = its `(page "N")`; svg = `schematic/<id>.svg` in the bundle; pdf = `design/ecad/ring/ring-schematic.pdf`; part_ids from the `sheet` column of `parts.csv`.
- Blocks: the sub-pages (not the overview), same ids. On the live design A5-draft: 9 pages, 8 blocks (the brief said 7; the Band page is the eighth).
- Links: one per pair of blocks that share a net; a net on 3 pages gives 3 pairs. No-connect pins (empty net) are skipped.
- Pin plan: architecture.md section 7, with the signals that 16.6 turns into spare test pads marked in Notes (parsed from the 16.6 text, not listed in code). Section 17.4 confirms JOY_CENTER stays spare.
- Power budget: the section 4 table, then the lines of 16.8 and 17.5 as rows "Section N (replaces section 4)". Section 4 figures are not edited.
- Provisional pin numbers (rows of open-pins.csv with a pin number; 86 on the live design, plus 3 OPEN part numbers with no pin) are in the electronics status message, because electronics.schema has no field for them.

## Tool
`kicad-cli sch export svg` from `$KICAD_CLI`, else the KiCad app, else PATH. Missing tool: status `missing`, every svg null, pdf link kept, run exits 0. Tool failure or an SVG with an absolute path: `unparsed`.

## Check
`node scripts/run-pytest.mjs collector/tests/collector-electronics`
