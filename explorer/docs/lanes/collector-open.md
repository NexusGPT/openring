# Lane collector-open

Extractor: `collector/extract/open_items.py` (record `open-items`, file `open.json`). Tests: `collector/tests/collector-open/` (C01 to C10, made-up fixture files).

Reads, from the design at the fork commit f4d782a (architecture A5-draft):
- supplier requests: section 12 rows 12.n become S1..S7; the S rows of 16.9 and 17.6 follow; "S1 (changed)" replaces S1 (ask = the row's item text, since those tables have no ask column). Live: 13 (S1..S13).
- bench tests: section 13 B1..B5, B6..B9 from the later tables, and the 4 `[CHECK n]` lines of `design/bench/bench-plan.md`. Live: 13.
- risks: `requirements.md` section 6 table, R1..R8. Live: 8.
- decisions: a line with `owner, <ISO date>` or starting `Owner,` (date in the line or the nearest heading), one decision per quoted sentence after the mark, verbatim, file and line. Live: 17.

Left out by design: case supplier items (case record); the parts list's open actions (in the parts record, not copied); `blocks` (the schema has no field for what an item blocks); per-item unreadable state (the schema has none, so an unreadable row is left out and named with its reason in the manifest message).

Proof: `_captures/collector-open/pytest-red.log` (stand-in extractor, 10 failed), `pytest-green.log` (10 passed), `run.log` and `data/` (live run, open-items ok).
