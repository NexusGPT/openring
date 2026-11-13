# Lane notes: case

Files: `src/routes/case/` (index, Facts, PartsList, Supplier, model, case.css), `tests/checks/case/` (case.spec.ts, run.config.ts), captures `_captures/case/`.

## What it does
- Panel: key numbers (every fact of `case/index.json`, source on hover), the lid button, the card of the selected case part (PartCard, route `case`), the parts list (one row per case line of `parts.json`, counts from `totals.case`), and the supplier items.
- Stage: `show: case`, `lidOpen` = a viewing angle (`OPEN_DEG` in model.ts, a presentation value, not a case fact), `names` = hover tags from the parts lines. A click on a pin node writes `?part=case:P1`; the card reads it. A list row writes the same.
- Honest states: missing / unparsed = banner only; stale = the contract sentence, the record's own reason line (manifest message), content dimmed.

## Checks (`tests/checks/case`, run: `npx playwright test -c tests/checks/case/run.config.ts`)
Own apps on 8833 (live) and 8834 (empty). C01 facts · C02 parts rows and counts · C03 lid >= 90 deg · C04 click on a pin in 3D · C05 list row card, close · C06 stale · C07 empty bundle · C08 no page scroll.

## Open points for other pieces
See the report of this lane (lid picture, 6.37 vs 6.3 minutes, panel height).
