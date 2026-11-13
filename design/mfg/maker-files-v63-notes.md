# Maker files from the inside model v6.3 (pad row at X = -1.0 mm): not regenerated

Work 2026-11-11, 11:05 to 13:35 (clock from `date`). The time limit of 150 minutes was reached while the seven fit checks were still running (the machine's load was 50 to 120 during the first runs; one check took 10 to 35 minutes), so the export (step 5) was not started.

## Done
- Steps 1 to 4: thin.py (`pad_x = -1.0`, `pad_margin`), check_thin.py (tests a and b), US 9 outputs regenerated (placement.csv x = -1.000 on the four pad rows). Details, the results table and the broken copy: `design/mech/thin/thin-notes.md`, section "Model v6.3"; logs in `design/mech/thin/out/v63/`.
- Fit check: US 7, 8, 9 `RESULT PASS pairs=1175 parts=49`, US 10 and US 11 `RESULT PASS pairs=1127 parts=48`. US 12 and US 13 were running (pid 4886, `design/mech/thin/out/v63/run_v63.sh`; logs `size_us12_v63.log`, `size_us13_v63.log`).
- Steps 6 and 7 (text): `design/mfg/specs/band-liner.md` row "charging pads" and `design/mfg/specs/band-flex-tails.md` (FLEX2 line and the pad pitch row) state the row at X = -1.0 mm with the reason and "architecture 17.28". `design/mfg/assembly/assembly.md`: step 8 states the row at X = -1.0 mm; G06 fixed in step 7 (US 13 motor -42.5, with the list -47.0, -45.5, -44.0, -45.0, -43.5, -42.5, -42.5), and the per-size table's motor column corrected the same way (US 10 to 13 had the v6 values -43.0, -41.5, -40.5, -39.5); the placement.csv citation in step 8 moved from line 44 to 45. The "Open: the motor's free space ..." sentence was removed: thin-notes.md v6.2 closes it with "every v6.2 check that ran passes: ... each RESULT PASS" and the v6.1 table (motor free space 0.0500 to 0.1000, rule 0.05). `check_assembly.py` after the edits: `RESULT PASS`, exit 0 (out/v63/check_assembly.log). Note: that run was before the step 8 edit; it was not rerun.

## Not done (limit: time)
- Step 5: no maker file was exported, no index.csv change, no `old_v62/` move, no check_parts.py run, no sheet redrawn. Files that would change: band-liner (STEP, STL) and flex-tail-away per size, every `assembly/ring-assembly-usN.step`, and the drawings of those. The `parts/` files are still the v6.2 ones and still show the pads at X = 0.
- Prepared only as text: version strings in `parts/export_parts.py`, `out/v7-export/export_size.py` and `tools/draw.py` now say v6.3 (not run).
- Next command: `cd design/mfg/parts && nice -n 19 ../../.venv/bin/python export_parts.py 9 7 8 10 11 12 13`, then `check_parts.py`, then `draw.py` for band-liner, flex-tail-away and the assemblies.

## Not changed
Everything outside "Owns", the case, bom.csv, architecture.md, body.md, check_docs.py.

RESULT: blocked, the time limit was reached before the export: fit checks PASS at US 7 to 11, US 12 and 13 still running, no maker file regenerated
