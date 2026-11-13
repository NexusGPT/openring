The joint table, its check and the gap list are built. The check fails today as the red-first proof: 95 of 99 joints have a gap. 4 are complete.

**Delivered** (ROOT/design/mfg/assembly/)
- `joints.csv`: 99 rows, the 15 columns of the brief. 81 rows are joint ends of the wiring list and 18 are board passes (ring board 2 faces, 14 band boards, 2 case boards). A field with no source holds MISSING and the gap column says what is missing.
- `check_joints.py`: 5 rules (missing row, empty or MISSING or gap, unknown step, paste layer missing or with no opening, check before its step). Pads come from KiCad pad dumps of board copies; openings come from the Gerber flashes. The pad to flash match is 302 of 302 (ring F), 45 of 45 (ring B) and 261 of 261 (case main F).
- `joint-gaps.md`: 95 lines in 13 groups, each with the file that must say it and the lead decision (none settles a solder, flux, paste, profile, fixture or fiducial).
- `joint-table-notes.md`: method, counts and limits. Its last line is the RESULT line.
- Work folder `joint-table-work/` (5.6M): builder, audit, tests, logs.

**Bars**
1. `logs/final/count_ends.log`: `ARITHMETIC 81 ends in joints.csv + 53 ends with no joint = 134 = 2 x 67 lines`. The 53 ends with no joint: copper on one board 10, inside the part 9, made by the part's maker 24, switch terminals not soldered 8, sensing gap 2.
2. `logs/final/check.log` exit 1, last line `RESULT FAIL 365` (R1 0, R2 360, R3 0, R4 1, R5 4). Its lines name the 15 G1 lands J-W001-A to J-W032-A with `solder_source` MISSING. `logs/final/tests.log` last line: `TESTS PASS 13 of 13 as expected`. The 3-row miniature gives `RESULT PASS joints 3`. Six broken copies of the miniature, and the same six breaks of the real table, each fail on their own rule only.
3. `logs/final/audit_citations.log` last line: `AUDIT cited lines found 1837 of 1837 total, fields with a citation 1287 of 1287, rows 99, problems 0`.

**Gaps beyond review 3 G1 to G7**
- The case main board has no build step. Its charger U2 thermal pad (pad 25) has no paste opening (the R4 line).
- No board has a fiducial, but step 2 locates by "fiducials of the board file".
- No searched file names a flux (81 rows) or a reflow or plate profile.
- Spring pins P1 to P4: the only words are "solder P1 to P4 to PCB2".
- J1: no tool is named, and no continuity check comes before step 17.
- The disc check "flush with the liner" sits in step 8 but needs step 21 (4 R5 lines, G5).

**Limits**
- The 4 complete rows (case pin tips on the discs) take step 28 as the step that makes the contact, and step 28 itself checks nothing.
- The hot-bar heat (260 C, 4 s, 20 N) is a starting value. The same line gives a 3 s limit.
- The Harwin documents were not searched (unverified).
- I typed the times in four expectation files by hand, and they were wrong. Each file now has a CORRECTION line.
- After the ring board gains parts, `dump_pads.py` must run again on a new copy.
- No git, browser, web request or check_band.py.

questions_for_owner: none

RESULT: done, 99 joints, 4 complete, 95 with a gap; check_joints.py exit 1, RESULT FAIL 365
