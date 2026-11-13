# Checklist for bench plan B2 (builder, brief of 2026-11-12)

Closed as `[x] ... evidence: <file>` or `[-] ... not done: <measured limit>`.

- [x] 1. bench-plan.md is version B2; B1 kept as bench-plan-B1.md beside it evidence: design/bench/bench-plan.md line 3 ('Version B2'); design/bench/bench-plan-B1.md; logs/final_audit.log (B1 unchanged)
- [x] 2. Kits and parts follow the ring's current parts: power chip kit for the nPM1304 evidence: bench-plan.md section 2 row 3 (nPM1304 EK, nPM1304-EK)
- [x] 3. ... microphone: the ring's part (Knowles SPK0641HT4H-1) or its maker's evaluation board evidence: bench-plan.md section 2 row 4 (Knowles SPK0641HT4H-1 on CB-MIC; no maker evaluation board found, bench-kits.md section 3)
- [x] 4. ... motor (Jinlong W0525AB001D) and its own regulator (TLV75530PDQNR) evidence: bench-plan.md section 2 rows 5 and 6; section 4.1 CB-MOT
- [x] 5. ... five switches for the joystick, the centre as the record control evidence: bench-plan.md section 2 row 7 (Adafruit 504); wiring rows 34 to 38
- [x] 6. ... the ring's screen or the closest kit that can show the recording sign evidence: bench-plan.md section 2 row 8 (Waveshare 10507); tests T4 and T2
- [x] 7. ... the storage part evidence: bench-plan.md section 2 rows 9 and 10
- [x] 8. For every kit or part: maker, exact order code, what it stands in for, source file and line evidence: bench-plan.md section 2 columns Maker, Order code, Ring part, Choice source
- [x] 9. Order codes not in saved files: public page read only, no account/cart/contact/name; page and date cited; else "not confirmed" evidence: bench-kits.md header; logs/fetch_all.log; plan statuses 'not confirmed' for rows 4, 5, 11
- [x] 10. Recording light removed from the wiring and the tests evidence: bench-plan.md section 1 and wiring table; logs/check_FINAL_bench-plan.log (R3 OK)
- [x] 11. Test of the screen as the recording sign: microphones get power only after the screen shows the sign; no state records with the screen dark (firmware.md R-SIGN, SIGN-1) evidence: bench-plan.md section 5 test T4
- [x] 12. Every pass line from the current design files, with file and section evidence: bench-plan.md section 5 columns Source and Quote; logs/check_FINAL_bench-plan.log (R4 OK)
- [x] 13. Recording current pass line: states the figure the design uses today, says the always-lit sign has no measured figure, and the bench test that measures it is explicit evidence: bench-plan.md section 5 test T2
- [x] 14. Wiring table: every connection between kits, pin to pin, with the ring's net name evidence: bench-plan.md section 4.2 (43 rows)
- [x] 15. bench-kits.md updated to the same parts evidence: design/bench/bench-kits.md
- [x] 16. check_bench.py reads bench-plan.md and design/bom.csv evidence: design/bench/check_bench.py
- [x] 17. check fails when the plan names a part number (power chip, microphone, motor, screen) not in the parts list (or its stated kit) evidence: logs/check_FINAL_bench-plan-faulty.log (RESULT FAIL, R1 and R2)
- [x] 18. check fails when the plan names the recording light as current evidence: logs/check_FINAL_bench-plan-faulty-light.log (RESULT FAIL, R3); logs/check_FINAL_bench-plan-B1.log
- [x] 19. check fails when a test has no pass line evidence: logs/check_FINAL_bench-plan-faulty-passline.log (RESULT FAIL, R4)
- [x] 20. RESULT PASS on bench-plan.md (B2) evidence: logs/check_FINAL_bench-plan.log (RESULT PASS)
- [x] 21. RESULT FAIL on bench-plan-B1.md evidence: logs/check_FINAL_bench-plan-B1.log (RESULT FAIL)
- [x] 22. RESULT FAIL on one faulty copy of B2 evidence: logs/check_FINAL_bench-plan-faulty.log (RESULT FAIL)
- [x] 23. Logs of the three runs kept evidence: logs/check_FINAL_*.log, check_v2_*.log, check_v3_bench-plan.log, check_run0_b2_first.log, check_run1_b2.log (the first-version set check_final_* was overwritten; reported in b2-notes.md section 3)
- [x] 24. b2-notes.md: every kit and part changed from B1 to B2 with source of the new choice evidence: design/bench/b2-notes.md section 1
- [x] 25. b2-notes.md: every order code marked confirmed (source) or not confirmed evidence: design/bench/b2-notes.md section 2
- [x] 26. b2-notes.md: the check's three log lines evidence: design/bench/b2-notes.md section 3
- [x] 27. b2-notes.md: what the bench still cannot prove evidence: design/bench/b2-notes.md section 4
- [x] 28. Last line of b2-notes.md is `RESULT: <done|blocked>, <one sentence>` evidence: last line of design/bench/b2-notes.md
- [x] 29. Never run git; no browser; no supplier contact, purchase, sign-up; no requester/owner/company name in any web request; stop no foreign process evidence: conduct items: web record in b2-notes.md section 5; logs/fetch_all.log; logs/final_audit.log (no request names a project, owner or company)
- [x] 30. Shell rules: absolute paths, no stderr thrown away, writes only in design/bench/ evidence: all commands used absolute paths; logs/bench_listing.log
- [x] 31. Final reply under 3,500 characters; final audit script run and saved evidence: logs/b2-final-reply.md; logs/final_audit.log
- [x] 32. Files my run wrote outside design/bench/: none (listing saved) evidence: logs/bench_listing.log (every file under design/bench/; no worktree, process or install left)
