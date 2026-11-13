# Lane notes: parts

Files: `src/routes/parts/` (index, model, useParts, Totals, FilterBar, Row, parts.css), `tests/checks/parts/` (parts.spec.ts, run.config.ts), captures `_captures/parts/`.

## What it does
- Panel frame as Home and Inside: serif title, mono stamp, mono section labels. Sections: TOTALS (the bundle's `totals.ring` words "78 lines" "128 parts", priced sums per currency from `priced_sums`, unpriced count, Export CSV), THE LIST (filter chips, shown count, one row per ring line), THE CHARGING CASE (collapsed group, own lines, not in the ring totals).
- Row: part + refs + quantity, maker, order code, price, evidence code (legend meaning on hover), open action (one line). Narrow panel = two lines per row; at 700 px of panel width and more (expanded panel) = one line of columns (container query).
- A row opens the PartCard in place (never rebuilt here). Selection = the address `?part=<id>` (shell contract), so the stage highlights the object; the screen asks the stage for `show: internals` and `explode: 0.5` while a line is open. Escape or a second click closes. A line with several refs shows one chip per ref to switch the card.
- Filters (one model, in the address): `?f=code|drawing` (exclusive) `,supplier` and `?page=<schematic page id>` (set by Electronics, "parts of this page"; removable chip). "clear all" appears only when something is on. Reload keeps it.
- Export CSV: an anchor to `fileUrl(<source file of the ring lines>)` with `download="bom.csv"`: the source file itself, whatever the filter. Disabled with words when the file is not in files.json.
- Honest states: record missing/unparsed = one banner (contract words) and no list; stale parts record = banner, content dimmed; case lines made for an older design = the contract's stale sentence above the case group, group dimmed (read from the parts manifest message `Case lines were made for design X; the design is now Y.`); empty filter result = a sentence; loading = hairline skeleton.
- Kit: nothing from `@<org>/apps-ui` (the app has no kit import; same choice as Home): S1 tokens, contract StateBanner.

## Definitions chosen (the brief does not define them)
- has an order code: `maker_part_number` is not empty.
- made to drawing: no `maker_part_number`. The row says "made to drawing" in the code column. A line the maker has not given a code yet (a resistor whose distributor must answer) falls here too: the bundle has no field that tells the two apart.
- needs a supplier's answer: `open_action` is not empty (36 of 78 today). The brief says "a section 12 item" (S12/12.x): the record has no such flag, and the open-items record is not in the live bundle.
- Made-to-drawing card: shows the maker files when `files.json` has a file whose file NAME holds the part reference as a whole word; else the sentence "The maker file for this part is not made yet."

## Checks (`npx playwright test -c tests/checks/parts/run.config.ts`, own app on 8806, one app at a time)
C01 rows and cells equal the bundle, totals words · C02 row opens the card, Escape/second click close, address holds the part, address opens it on load · C03 supplier filter, reload keeps it, clear all restores · C04 has-code / made-to-drawing split and exclusive, combine with supplier · C05 download is bom.csv, sha256 equal to the source · C06 case group, ring totals untouched, contract stale sentence, dimmed · C07 no page scroll at 1512x982, 1440x900, 1280x800; rows at least 40 px · C08 selection survives a filter change (address) · C09 sample bundle: grouped line chips, page filter · C10 empty bundle: one banner with the command, no rows, 0 console errors (a 404 of `/data/` is the data layer's, as in Home).
Mutations (each seen red): `_captures/parts/mutate.py`, log `_captures/parts/MUTATIONS.log` (works on a scratch copy, never on the shared source). Pictures: `_captures/parts/*.png` (`shoot.ts`).

## Open points for other pieces
1. Brief and message disagree on numbers: brief says 77 lines and 146 parts (older fixture); the live bundle has 78 lines and 128 parts; the screen reads the bundle, so both are fine. The brief's "lane ids parts-C01..C99" matches.
2. The shell widens the panel only by its user toggle (`app.panel-expand`); there is no way for a screen to ask for it. The list works at the default width (two-line rows) and uses the extra width when the owner expands.
3. Empty bundle: the browser logs one 404 for manifest.json (data layer), as Home reports.
4. The part card's evidence row prints the legend text with backticks (`design/datasheets/`): part-card lane.
5. The collector lane's files record has no per-part maker-file tag; "links to maker files" works by file name until it has.
