# Text pass 2: notes

Run: 2026-11-13, 12:54 to 12:59 CET (clock from `date`). ROOT = .. Work folder (copies before, logs, scripts): ROOT/design/wiring/text-pass-2-work/. Full before and after lines of every edit: text-pass-2-work/part2.diff (12 hunks, 26 changed lines). No git, no browser, no web request.

## Part 2: corrections (wc -l is the same before and after for every edited text file)

| Item | File and line | Done |
|---|---|---|
| 71 | requirements.md 195 (220 lines before and after) | The 82 to 109 minutes is marked REPLACED, Do not use, struck out. The per-size range is stated with its source: cell.md line 63, 1.17 to 1.57 hours at US 7 and 1.59 to 2.13 hours at US 13. |
| 121 | requirements.md 204 | The line now starts with: record of 2026-11-11, REPLACED by line 26 (S6) and by item 3 of the section "Changes after sign-off: owner decisions of 2026-11-13". Do not use the IP65 wording. |
| 11 | main-board.md 18 and 56 (69 lines) | Line 18 states ENEPIG and green solder mask on both sides, source stackup.txt line 20. Open point 3 (line 56) is marked CLOSED 2026-11-13 with the same source. |
| 156 | architecture.md 303 (941 lines) | 6.3 minutes marked REPLACED by firmware.md line 718 and case-architecture.md line 88 (3.21 minutes, 2 microphones), Do not use. |
| 158 | architecture.md 153 and 229 | Both marked REPLACED by section 17.11 (record button removed; one control, the joystick; long press of its centre records). Other record button lines are NOT marked (see lead list). |
| 103 | architecture.md 162 | The 4 screws M1.2 x 3 are marked REPLACED by lead-decisions.md line 57 with its words "The M1.2 screw is no longer in the design (not in the model, not in the parts list)". |
| 161 | design/supplier-package/make_one_pager.py 64 and 99 (226 lines) | The script is at design/supplier-package/, not design/mfg/tools/ (the lead's path does not exist). The English sentence (line 64) and its Chinese twin (line 99) no longer say the layout is not ready; they say the board is routed and passes its rules check with 0 unconnected items (board-notes-r3.md line 20) and that a built and tested board is not ready. Rebuilt with the command of the script header on the latest package ring-supplier-package-2026-11-12-97d5da6 (log onepager-build.log, exit 0, text in onepager-after.txt). Generated file changed: ROOT/supplier-package/ring-recorder-one-pager-EN-ZH.pdf (the old copy, dated 11 Nov, is saved as ring-recorder-one-pager-EN-ZH.before.pdf; the new one reads its counts from the 301 file package, so more than one sentence differs from the old PDF). Previews: onepager-preview-en.png and onepager-preview-zh.png (written by the script, in the work folder). |
| 18 | ecad/ring/pcb/provisional-footprints.json 13 and 14 (14 lines) | A grep of ROOT/design for the file name (py, sh, md, txt, csv, json, outside review, ring-route and ring-lines copies) finds no check that reads it. connections.md line 24 only lists it as a source file; board-notes.md line 7 says it belongs to the old 6-layer board and is obsolete. So both entries (J_BAND_A, J_BAND_B) now say REPLACED, history of the old board, and state the current footprint (land group only, hot-bar soldered, source J_BAND_x_BOARD.kicad_mod line 6). The file is still valid JSON. |
| 147 | light-path.md 1 (153 lines) | The first line said "history: the recording light is removed in v7 (architecture 17.30)". It now says the light was removed in design version 7 (architecture 17.30; architecture.md line 523) and the file is history. Line 111 (still reads as if the light exists) is not changed. |

## Part 1: deferred-triage.csv

163 rows, 6 fields each (verify_csv.log). Only column `state` of the 66 items changed; no other column (verify_csv.log: other columns changed 0). Rows whose state starts with `open`: 66 before, 51 after. 15 rows now start `closed 2026-11-13` (items 1, 5, 11, 12, 17, 18, 28, 52, 113, 114, 116, 117, 121, 147, 156); for each, the quote in the row was found with `grep -n -F` at the cited file and line (verify_csv.log: closed rows 15, not found 0). All 66 quotes of state-a and state-b were found again by grep first (findquotes.log); only items 11 and 161 no longer matched, because my own edits changed those lines.

Counts of the 51 open rows (counted by script from the csv): needs hardware 19, needs a maker's answer 14, owner 1, design work 17 (10, 27, 48, 61, 95, 102, 103, 112, 115, 122, 123, 124, 129, 157, 158, 160, 161).

Where I did not follow the lead's mapping, and why:
- Item 71 stays `open, needs hardware`. The contradiction is fixed, but the item itself is "C3 charge time under 90 minutes is UNPROVEN", which needs the built charge test; on paper US 13 (2.13 hours) is above 90 minutes.
- Item 161 stays `open, design work`. The one-pager is fixed, but design/supplier-package/READ-FIRST.template.html lines 69 and 106 still say the board is not routed.
- Item 103 stays open: the screw part is closed, but the ASSUMED mic port position and 2.5 mm stem (mech-notes.md line 70) are still to confirm.
- Item 158 stays open: lines 153 and 229 are done; other record button lines are outside the named lines.
- Item 18 is closed (stale json entries corrected). Item 147 is closed. Items 11, 121, 156 are closed.

## Left alone (not mine), state set to open, design work with the owner named
Items 10, 122, 123, 124 (assembly.md under independent review); 27, 95, 102, 112, 115, 129, 157 (the lead rules); 48 and 160 (taller block rework).

## For the lead
1. architecture.md still describes a record button without a REPLACED mark at lines 23 (block diagram), 300, 356, 369, 433, 455, 482 and 515 (item 158, firmware.md H15). Line 300 and 356 are comparison tables; check whether their section header already marks them old.
2. firmware.md line 1192 (H11) still says architecture and the case document give 6.3 minutes and the row is `open`; architecture.md line 303 is now fixed. firmware.md H15 (line 1196) likewise. Close both rows (I do not own firmware.md).
3. design/supplier-package/READ-FIRST.template.html lines 69, 106 and 115 still say the board is not routed and who routes it is not decided; the supplier package folders and zips (built 12 Nov) carry the old cover page. The one-pager text still lists "as an option the circuit board layout" (make_one_pager.py lines 68 and 103); I left it, as the brief names one sentence.
4. A copy of the script at explorer/dist/files/design/supplier-package/make_one_pager.py and of the json at explorer/dist/files/design/ecad/ring/pcb/provisional-footprints.json still hold the old text (generated explorer copy, not mine).
5. The one-pager PDF was replaced in place at ROOT/supplier-package/ring-recorder-one-pager-EN-ZH.pdf. If that folder is tracked, the lead commits it (git status was not run).
6. requirements.md line 195 (C3) still has "0.55 to 0.74 C for a cell of 20 to 27 mAh" before the replaced sentence; same old cell sizes, left as it is outside the named change.
7. main-board.md open point 2 (laminate, copper weight, via type, track and gap, tolerance, impedance: "the board maker proposes after the stack-up exists") is still open in text although stackup.txt now holds these values; the lead decides whether to close it.
8. Assembly lines I quoted for closed items 113, 114, 116, 117 (assembly.md 320, 326, 365, 363) are read-only quotes found today (12:5x to 12:59 CET); the independent reviewer may move these lines.

## Checks (log after-checks.log; base run base-checks.log is identical)
- `ROOT/design/.venv/bin/python ROOT/design/mfg/tools/check_docs.py`: exit 0, line `RESULT PASS`.
- `ROOT/design/.venv/bin/python ROOT/design/firmware-check.py`: exit 0, last line `0 failures`.
- `ROOT/design/.venv/bin/python ROOT/design/tools/check_bom.py`: exit 0, last line `lines 86, designators 129, section-2 rows 19, section-2 part tokens 24, switch lines 2, pad lines 1, designators against model and wiring 129, failures 0`.
No check was edited or weakened.

questions_for_owner: none

RESULT: done, open rows of deferred-triage.csv went from 66 to 51 (15 closed with a verified file and line); items 71, 103, 158 and 161 stay open for the reasons above.
