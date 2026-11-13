# Review 2 checklist (commit c64c4e6)

Read:
- [x] 1. requirements.md incl. changes after sign-off. evidence: read in full (204 lines, wc.log); G11, G20
- [x] 2. design/architecture.md in full (17.24-17.27, Key numbers newest). evidence: read lines 1-829; G02, G03, G10
- [x] 3. design/bom.csv + notes. evidence: read in full (87 lines); G04, G05, G13, G14. bom-notes.md not read (section 6 of the review)
- [-] 4. design/ecad/ring/ sch-notes.md, netlist.csv, parts.csv, open-pins.csv, pcb/board-notes.md. not done in full: sch-notes, netlist, open-pins, board-notes searched and read in part; parts.csv not read row by row (90-minute limit); G09, G23
- [x] 5. thin-notes.md v6 to v6.2 (lines 240-405), placement.csv rows; studies by RESULT line (studies_result_lines.log); merged32g report lines 1-25 and RESULT. evidence: thin_v62_results.log
- [-] 6. design/mfg/: index.csv rows, specs body, band-liner, band-flex-tails, joystick-nub, cover-glass, main-board, cell, record-cap searched or read; assembly.md read in part (steps 2, 5, 7, 8, 10, 13, 16, 21, conflict table); maker-files-v62-notes.md read. not done in full: assembly.md steps not all read
- [-] 7. design/firmware.md searched by topic, not in full; firmware-f6-notes RESULT line only
- [x] 8. case text files at scratch export: case-architecture.md full, case-notes.md lines 25-45, case.py pad and joystick lines. case-bom.csv not read. evidence: case-architecture_at_c64c4e6.md (cmp equal)
- [x] 9. software/bring-up.md full; factory-package.md not read beyond its size (studies_result_lines.log)
- [x] 10. review 1 design-review-1.md full. review/CHECKLIST.md: size only
- [x] 11. READ-FIRST.template.html State of the design table. evidence: readfirst_state.txt

Run (logs in review-2/):
- [x] 12. df -h / >= 5 GB: 13 GB available at 10:49 (start command output)
- [x] 13. check_bom.py. evidence: check_bom.log, exit=0
- [x] 14. check_docs.py. evidence: check_docs.log, exit=0
- [x] 15. check_parts.py. evidence: check_parts.log, exit=0, RESULT PASS files=90
- [x] 16. firmware-check.py. evidence: firmware_check.log, exit=0
- [x] 17. ecad/ring/check_netlist.py (on a sandbox copy, because it writes ring-kicad.xml in place). evidence: check_netlist.log, exit=0
- [x] 18. fake attack on check_bom (B1, B2, B3). evidence: fakes/fakes_results.log
- [x] 19. fake attack on firmware-check (W1 to W5). evidence: fakes/fakes_results.log
- [x] 20. fake attack on check_docs (S1 to S5). evidence: fakes/fakes_results.log, fakes/fakes_results_2.log
- [x] 21. 3D logs read under design/mech/thin/out/v6/ (builds not run). evidence: thin_v62_results.log

Owner rules searched:
- [x] 22. record only on long press of joystick: firmware.md:144, :198; fakes W1, W2 fail
- [x] 23. light visible whenever a mic records: netlist.csv:351, :352; firmware.md:770; visibility declared open D3
- [x] 24. one control, no record button: record-cap.md:3, architecture.md:544; stale row G10
- [x] 25. sizes US 7 to 13: requirements.md:22; thin_v62_results.log; case G08

Deliver:
- [x] 26. F01..F30 status each. evidence: design-review-2.md section 3; audit_final.log "F rows 30"
- [x] 27. findings table with file:line quotes. evidence: audit_final.log
- [x] 28. Declared open table (D1 to D17)
- [x] 29. contradictions (K1 to K16)
- [x] 30. not read / not checked (section 6)
- [x] 31. counts per severity, RESULT last line
