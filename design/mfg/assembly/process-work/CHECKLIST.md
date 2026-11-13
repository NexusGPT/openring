# Checklist (process sheet)

Brief fields: Owns, Must not touch, Writes to, Done when present; no separate "quality reference to copy" is named: the brief's Bar 1 to 4 is used as the quality reference.

- [x] 1. Read the named sources (notes, gaps, joints.csv, check_joints.py, assembly.md steps 2 to 9 and 14 to 18, band-interface.md 4 to 8, case procedure, lead-decisions rows 68, 70, 71). evidence: this run's reads; logs/rows-before-sample.log, logs/gap-clauses-before.txt
- [x] 2. Before state saved: check_joints.py `RESULT FAIL 365`. evidence: logs/check-before.log, joints-before.csv, logs/before-sha.txt
- [x] 3. P1 alloy SAC305 kept, no part limit forbids it. evidence: process.md P1.1, logs/calc.log
- [x] 4. P1 named paste with type and flux class from the maker's datasheet (Kester NP505-HR T4 ROL0). evidence: design/datasheets/proc_kester_np505hr_*, logs/audit.log
- [x] 5. P1 named wire (Kester 275 SAC305, 0.25/0.4/0.5 mm). evidence: proc_kester_275_*, logs/audit.log
- [x] 6. P1 residues washed or left, consequences for liner, probing, screen. evidence: process.md P1.5
- [x] 7. P2 thickness and material per board: ring parts face, ring screen face, band ribbons, case main board, with area-ratio arithmetic and rule source. evidence: logs/stencil_calc.log, logs/calc.log, T1
- [x] 8. P2 reduced openings named (J1, test pads, U2 thermal pad, discs). evidence: process.md P2, logs/case_noland.log
- [x] 9. P3 profile from the paste maker; table against J1 (page 6 read myself: img/hirose_p6-6.png), Alps, main chip, power chip, microphones, cell. evidence: process.md P3. U1 and U2 peak limits: not done, no saved document (Nordic refused, logs/fetch4.log): named unverified
- [x] 10. P4 hand soldering per class incl. motor, cell tabs, case wires, case cell leads, thermistor, spring pins (Harwin documents searched). evidence: process.md P4, HW line 326
- [x] 11. P5 hot plate temperature and time, disc height arithmetic, flush check moved. evidence: logs/calc.log
- [x] 12. P6 tools list. evidence: process.md P6
- [x] 13. P7 fiducials list. evidence: process.md P7, JL
- [x] 14. P8 change list incl. paste openings, fiducials, case step, J1 continuity step order. evidence: process.md P8 (U2 pad 25 needs no change: logs/case_noland.log)
- [x] 15. Group 1 only alloy and flux, rest MISSING with hotbar-joint.md. evidence: logs/fill.log
- [x] 16. joints.csv filled, joint-gaps.md rebuilt with make_gaps.py. evidence: logs/fill.log, logs/make_gaps.log
- [x] 17. check_joints.py after: `RESULT FAIL 160`; each failing row waits for P8 or hotbar-joint.md, counts per reason. evidence: logs/check-final.log, logs/reason-counts.log
- [x] 18. No rule of check_joints.py edited; R4 limitation reported. evidence: process.md P8 note
- [x] 19. 13 tests still pass. evidence: logs/tests.log, logs/tests-sha.log
- [x] 20. Fetched files saved as proc_* with address and date. evidence: logs/fetch-times.log, logs/proc-sha.log
- [x] 21. Audit of citations. evidence: logs/audit.log
- [x] 22. process.md ends with lead list, questions_for_owner, RESULT line. evidence: process.md tail
- [x] 23. Work folder under 50 MB. evidence: logs/du-final.log
- [x] 24. No git, no browser, no edit outside Owns. evidence: commands of this run; the copy of run_tests.py writes into WORK/tests only
