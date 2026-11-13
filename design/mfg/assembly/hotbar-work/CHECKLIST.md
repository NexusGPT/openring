# Checklist, hot-bar joint study (brief of the lead, 2026-11-13, version 8a54884d; read at 0f3fcd0e, logs/version-diff.log)

- [x] 1. Read in full: wiring-review-3.md (G1, G3), hand-derivations item 5, hotbar-solder.log, fixture-search.log, band-interface.md, assembly.md steps 2, 4, 6 to 9, 14 to 18 and section 3, thin.py and thin-notes.md (slots, tails, fold volume, board), board-notes-r3.md. evidence: citations printed in logs/audit-final.log (CIT lines). thin.py and thin-notes.md were read in the parts named by the brief, not every line (1090 and 492 lines).
- [x] 2. Q1 solder source: paste in pass 2; aperture per stencil thickness; height arithmetic; stencil thickness not set in any file; board change list. evidence: logs/q1_paste.log, logs/stencil-search.log, logs/stencil-ringfiles.log, logs/paste_at_lands.log; hotbar-joint.md sections 1 and 7.
- [x] 3. Q2 orientation: twist-free poses are turns about X only; 0, 90, 180 degree poses. evidence: logs/geom_check.log (POSE line, CLEARANCE line); hotbar-joint.md 2.2.
- [x] 4. Q2 free ribbon length per size, 14 ribbons. evidence: logs/geom_check.log (14 FLEX lines).
- [x] 5. Q2 lift and tilt at US 7 and US 13: 0.000 mm, 0.00 deg, arithmetic in hotbar-joint.md 2.3. evidence: logs/geom_check.log.
- [x] 6. Q2 options A, B, C with what each changes, no decision. evidence: hotbar-joint.md 2.5.
- [x] 7. Q3 fixture drawn (hotbar-fixture.svg, values with sources logs/fixture-values.log, render logs/hotbar-fixture-render4.png); board marks tried and rejected with the scan. evidence: logs/scan_bars.log, logs/check_bars.log.
- [x] 8. Q4 sub-steps, land table, meter check, open land rule. evidence: hotbar-joint.md section 4; dumps/probe-pads.csv, dumps/netpads.csv.
- [x] 9. Q5 Hirose page 6 read and quoted; parts within 3 mm on both faces. evidence: logs/hirose-p6-reading.txt; logs/geom_check.log NEAR lines; logs/prt1_distance.log.
- [x] 10. Bar 1: numbers with sources or arithmetic; starting values marked and listed (section 6, 20 items). evidence: logs/audit-final.log (NUMBERS line, 0 unmatched; the match is "found in a log or cited file", not a per-number source proof).
- [x] 11. Bar 2: geometry script and planted copy changes the verdict. evidence: logs/geom_check.log, planted/geom_check-planted.log, planted/plant.diff.
- [x] 12. Bar 3: board list (section 7), guide text steps 2, 4, 16 (section 8), questions_for_owner (1 question). evidence: hotbar-joint.md.
- [x] 13. Last line RESULT. evidence: logs/audit-final.log "LAST LINE is RESULT: True".
- [x] 14. Only owned files written. evidence: logs/gitstatus-before.log, logs/gitstatus-after.log, logs/gitstatus-diff.log.
- [x] 15. Work folder under 50 MB. evidence: logs/du.log.
- [x] 16. No browser, no web request, no check_band.py, no model rebuild; KiCad runs at nice -n 19 one at a time. evidence: commands in this session; nothing to save beyond the logs of each run.
- [x] 17. No em or en dashes in my files. evidence: logs/audit-final.log DASHES lines.
- [x] 18. Final reply under 3,500 characters. evidence: logs/final-reply-length.log.
- [x] 19. Final audit run over the file and the reply. evidence: logs/audit-final.log.

Looks at results before the final one (all kept): logs/geom_check-run1.log, logs/geom_check-run2.log, planted/geom_check-planted-run1.log, logs/paste_at_lands-run1.log (counted footprint rows as lands, fixed), logs/audit-run1.log to audit-run3.log, logs/hotbar-fixture-render.png to render3.png.
Expectation differences (logs/diff_expected.log): 26 extra parts within 3 mm, all real parts of the board file (my expectation list named only 5); no other difference.

## Option D (lead's message after acceptance, 2026-11-13)
- [x] D1. 1.8 foot through slot and notch; land grids that fit 1.8 with the present rules. evidence: logs/geom_check.log lines "D FOOT", "D GRID", "D NOTCH".
- [x] D2. Extra length per tail and whether the generator takes it as one parameter. evidence: logs/geom_check.log "D EXTRA LENGTH", "D FLEX" lines; build_band.py lines 160, 199 to 201, 213, 391 (read, cited in hotbar-joint.md D2).
- [x] D3. Room above the land places, cable of layout C, J1, blade path. evidence: logs/geom_check.log "D ROOM ABOVE", "D CABLE PLAN", "D BLADE".
- [x] D4. Screen face parts within 3 mm, J1 distance, what is under the board, the support. evidence: logs/geom_check.log "D NEAR", "D SUPPORT".
- [x] D5. Change lists (ring board, band boards, model, guide). evidence: logs/check_notch.log, logs/q1_paste_D.log; hotbar-joint.md D5.
- [x] D6. What D does not solve. evidence: hotbar-joint.md D6.
- [x] D7. Planted control changes the D verdict. evidence: planted/geom_check-planted.log last RESULT line "tails long enough as drawn 1 of 14".
- [x] D8. RESULT line last, naming four options; audit rerun. evidence: logs/audit-final.log.
Earlier looks kept: logs/geom_check-D1.log, logs/audit-D1.log to audit-D3.log, logs/geom_check-before-D.py.txt. check_notch.py tests bounding boxes of tracks against the notch (a track whose box meets it is listed, so the list can be longer than the copper truly cut).
