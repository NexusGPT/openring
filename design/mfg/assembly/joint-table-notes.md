# Joint table: notes (method, counts, what could not be filled)

Project root ROOT = .. Work folder: `design/mfg/assembly/joint-table-work/` (WORK below). Clock (`date`): first command 12:58:20, final runs 13:17:21 to 13:17:33 (`WORK/logs/final/time.txt`). Two earlier full runs are kept with the same counts: 13:14:58 to 13:15:09 in `WORK/logs/final-run1/` (before the "no file" gap wording was narrowed to the files read) and 13:16:56 to 13:17:00 in `WORK/logs/final-run2/` (before joint-gaps.md labelled its group order as my judgment). Earlier looks: `WORK/logs/check-today.log` (first check run, same `RESULT FAIL 365`, made before the `--passes` option was added), `WORK/logs/build1.log` (a failed build: line numbers of product-wiring.csv, see below), `WORK/logs/count_ends.run1.log` (first count, which wrongly paired the disc joints with the pin contacts). I ran no git command, no browser, no web request and not `check_band.py`, and I changed no existing file.

## Delivered

- `design/mfg/assembly/joints.csv`: 99 rows, the 15 columns of the brief.
- `design/mfg/assembly/check_joints.py`: the check (rules R1 to R5 below).
- `design/mfg/assembly/joint-gaps.md`: one line per joint with a gap (95), in 13 groups sorted by what a builder would get wrong first.
- This file.
- WORK: `build_joints.py` (writes joints.csv and `citations.csv`), `dump_pads.py`, `probe_paste.py`, `audit_citations.py`, `count_ends.py`, `make_gaps.py`, `run_all.sh`, `tests/run_tests.py` with `tests/mini/` and `tests/broken/`, board copies in `boards/`, pad dumps in `pads/`, logs in `logs/` and `logs/final/`, `CHECKLIST.md`.

## Method

1. Every row is written by `WORK/build_joints.py`. Each filled field carries citations (file and quoted text). The script finds the line number of each quote by searching the file; no line number is typed by hand. The `source` cell lists field, file and line for every field (for example `step: design/mfg/assembly/assembly.md:208` in the 15 hot-bar rows); `WORK/citations.csv` keeps the quote of each citation.
2. Where no file gives a value, the field holds MISSING and the `gap` column says what is missing. Where a file gives a value but the builder still lacks something for it (for example the land numbers of a check probe, review 3 G2), the gap column says that too.
3. Pads are read with KiCad's Python (`design/ecad/ring/pcb/run_kipy.sh`) from copies of the boards in `WORK/boards/`, made at 13:02:41 (`WORK/logs/board-copy-time.txt`; the ring board copy has the same sha256 as the original, 0390aa0f..., also at the final run, `WORK/logs/final/inputs-sha.txt`). Paste openings are the flashes of the delivered paste Gerber. The pad-to-flash transform (same origin, Y turned) matches 302 of 302 F.Paste pads of the ring board, 45 of 45 B.Paste pads and 261 of 261 F.Paste pads of the case main board (`WORK/logs/probe_paste.log`).
4. Joint ends: an end of `product-wiring.csv` gets a row unless its join is copper on one board, made by the part's maker, not soldered, inside the part, or the sensing gap. A board pass row is required for the ring board's two faces, each of the 14 band boards and the two case boards.

## The check (`design/.venv/bin/python design/mfg/assembly/check_joints.py`)

It fails (exit 1, one line per problem, last line `RESULT FAIL n`) on: R1 a wiring end or board pass with no row; R2 an empty field, the word MISSING, or a gap text; R3 a step (or the step a check names) that is not a step heading of assembly.md (such as `### Step 16.`) or a numbered step of the case procedure in `design/ecad/case/pcb/board-notes.md`; R4 a paste layer file that does not exist or holds no opening at a land the row names; R5 a check marked possible at a step before the joint's step or before a `[needs step N]` or `[needs case N]` tag written in the check. It passes with `RESULT PASS joints <n>`. `--list-gaps` prints the gaps, exit 0. Step format: `16` (assembly.md) or `case 3` (case procedure).

Today (`WORK/logs/final/check.log`), exit 1, last line: `RESULT FAIL 365`. Lines per rule (`WORK/logs/final/check-rule-counts.txt`): R1 0, R2 360, R3 0, R4 1, R5 4. The problem lines hold `R2 MISSING: J-W001-A field solder_source` and the same line for each of the other 14 hot-bar lands of G1: J-W001-A, J-W002-A, J-W003-A, J-W004-A, J-W005-A, J-W011-A, J-W021-A, J-W022-A, J-W025-A, J-W026-A, J-W027-A, J-W029-A, J-W030-A, J-W031-A, J-W032-A (`WORK/logs/final/check-hotbar-solder.txt`, which also holds the five case wire A ends). The R4 line: `R4 paste: P-case_main paste layer design/ecad/case/pcb/fab/case_main/gerber/case_main-F_Paste.gbr holds no opening for land U2:25 (GND)`. The R5 lines: J-W029-B to J-W032-B, the step 8 disc check "flush with the liner's inner face" that needs step 21 (review 3 G5).

Proof that it can fail (`WORK/tests/run_tests.py`, log `WORK/logs/final/tests.log`, last line `TESTS PASS 13 of 13 as expected`): a hand-made complete miniature of 3 rows (`WORK/tests/mini/mini-joints.csv`, its own 2-line wiring file and 1 board pass) gives `RESULT PASS joints 3`; six broken copies of the miniature (row removed, field emptied, step 29, paste on J_BAND_A:1 with no opening, a paste file that does not exist, check possible at step 5 for a step 7 joint) each exit 1 with lines of their own rule only; the same six breaks of the real joints.csv each exit 1 and add new lines of their own rule only. Kept copies and logs: `WORK/tests/broken/`.

## Counts (bar 1, `WORK/logs/final/count_ends.log`)

The wiring list has 67 lines (66 conductors and the sensing gap W058), 134 ends. Ends with a row: hand solder 21, hand solder at low heat 3, hot bar 15, pressed contact 18, reflow 20, solder (spring pins) 4: 81. Ends with no joint: copper on one board 10, inside the part 9, made by the part's maker 24 (cell 2, motor 2, pack 4, screen 14, thermistor 2), switch terminal 1 or 2 not soldered by design 8, the sensing gap W058 2: 53. Arithmetic: 81 + 53 = 134 = 2 x 67. Of the 132 conductor ends, 81 have a row and 51 have no joint (81 + 51 = 132 = 2 x 66). Five physical joints are named at two wiring ends (motor lands M1:1 and M1:2, cell pack lands PRT1:1 to 3), so the 81 end rows hold 76 distinct joints. Board pass rows: 18. Rows: 81 + 18 = 99.

Complete rows: 4 (J-W054-A to J-W057-A, the case pin tips on the gold discs). Rows with a gap: 95 (`WORK/logs/final/list-gaps.log`, `GAPS 95 of 99 rows`).

## Citations (bar 3, `WORK/logs/final/audit_citations.log`)

The audit reads the source cell of every row and runs `grep -n -F` with the quote of each citation. Last line: `AUDIT cited lines found 1837 of 1837 total, fields with a citation 1287 of 1287, rows 99, problems 0`.

## What could not be filled, and why (`WORK/logs/final/missing-counts.log`)

MISSING per field: flux 81 (none of the searched files names a flux: design/mfg, band-interface.md, the case board-notes.md, case-architecture.md, lead-decisions.md, screen-cable-study.md, `WORK/logs/flux-search.log`; `design/mfg/assembly/v7-update-notes.md` line 27 says "No file names the flux or the cleaner."), solder_source 63, heat 54 (no reflow or plate profile in assembly.md, band-interface.md or design/mfg/specs, `WORK/logs/profile-search.log`), alignment 22 (the hot-bar fixture is drawn nowhere; no board has a fiducial, `WORK/logs/fiducial-search.log`), tool 20, orientation 15 (the hot bar faces, review 3 G3), check 8, step 1 (no step builds the case main board), check_possible_at_this_step 1. New beyond review 3: the case main board has no build step at all, and the charger U2's thermal pad (pad 25) gets no paste; no board has a fiducial although step 2 locates by "fiducials of the board file".

## Evidence against, and limits

- The four complete rows take step 28 ("The ring goes into its case.") as the step that makes the pin-on-disc contact; step 28 itself checks nothing about it. The check cited is the case's own light sequence and the first-case USB test (lead-decisions.md row "case items 26, 89, 91, 92").
- The brief speaks of spring pins pressed in; the wiring list says P1 to P4 are soldered to PCB2 (`solder (P1 to P4 soldered to PCB2)`). I followed the wiring list. The Harwin documents in design/datasheets were not searched for a solder limit: unverified.
- The hot-bar heat (260 C, 4 s, 20 N) is filled from band-interface.md line 137, where it is the band builder's starting value and the same line gives the limit as 260 C 3 s; this is written in the 15 gap cells.
- `product-wiring.csv` holds carriage returns inside cells, so Python's universal newlines count more lines than `grep -n`; the builder and the audit read with `newline=''` (`WORK/logs/patch2.log`).
- Paste Gerbers of the ring board are dated 11:02, the board 10:58. Today they agree (302 of 302, 45 of 45). The ring board is about to gain parts: after that, `dump_pads.py` must run again on a new copy before the check is trusted.
- The times in the first line of four expectation files (`WORK/logs/expect-*.txt`, `WORK/tests/expect.txt`) were typed by hand and are wrong; each file has a CORRECTION line with its real write time.
- An early grep of lead-decisions.md failed (ugrep complexity limit, `WORK/logs/lead-decisions-search.log`); the search was done again in Python (`WORK/logs/lead-decisions-search2.log`). No row of lead-decisions.md names a solder alloy or form, a flux, a paste or stencil, a reflow profile, a hot bar, a fixture or a fiducial; its rows "case cell BT1 leads" and "case thermistor TH1 leads" give lead handling and the thermistor's iron and heat, which the table uses. "No file" in a gap cell means none of the files read for this table (the brief's sources and the files they cite), not the whole project.
- The checker reads pad dumps from `WORK/pads/`; a paste row on a board with no dump fails R4.

## questions_for_owner

none

RESULT: done, 99 joints (81 joint ends of the wiring list and 18 board passes), 4 complete and 95 with a gap; check_joints.py ends RESULT FAIL 365 as the red-first proof, its 15 hot-bar lines of G1 included.
