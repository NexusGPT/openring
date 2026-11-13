# Checklist for the case design (helper: case builder)

Evidence folder: design/case/evidence/

- [x] 1. case-architecture.md exists with a block diagram. evidence: case-architecture.md section 2
- [-] 2. One fixed part per function, maker part number and evidence tag for each. Done for the 10 active parts and cell (evidence/bom_check_2.log: "rows with maker part number: 10"); not done for passives, inductors, wires, screws and printed parts: they carry an open_action instead (no maker document read for them in the 60-minute limit)
- [x] 3. Central chip choice justified from datasheets (ESP32-S3 full speed DS p.55-56; ESP32-P4 high speed, no Wi-Fi). evidence: evidence/read_esp.log, evidence/read_p4.log, evidence/grep_usb.log
- [x] 4. Full speed 12 Mbit/s time stated: 5.12 min bound, 6.32 min bulk ceiling. evidence: evidence/calc_case.log
- [x] 5. Transfer time per recorded hour for the choice: 6.32 min. evidence: evidence/calc_case.log
- [x] 6. Power tree with every voltage. evidence: case-architecture.md section 4; values from evidence/read_bq2.log, evidence/calc_case.log
- [x] 7. Charge and transfer sequence step by step. evidence: case-architecture.md section 5
- [x] 8. Pin plan of U1 pin by pin. evidence: case-architecture.md section 6 from evidence/mini1_pintable.log
- [x] 9. Supplier items table. evidence: case-architecture.md section 8
- [x] 10. Functions covered (boost with limit U2+U5, charger with power path U2, protection in BT1 PCM, voltage sense U2 ADC, 8 GB storage U4, USB-C J1 with R1 R2, pins P1-P4, lid latch, touch presence E1, LED1, Wi-Fi U1). evidence: case-bom.csv, case-architecture.md section 3
- [x] 11. Cell gives 3 charges by arithmetic: 700 mAh -> 3.26 (boost efficiency 0.85 assumed, untested: bench B5). evidence: evidence/calc_case.log
- [-] 12. Ring charge under 90 minutes: the case supplies at least 401 mA at 4.998 V (evidence/calc_case.log); the 90 minutes depend on the ring's charger setting, not measured, not in my files to change
- [x] 13. Pins meet pads at X -12.6, Y +-1.27 and +-3.81, 1.6 mm pads, in the working window. evidence: evidence/run_done_final.log
- [x] 14. Fits block and bands US 5 and US 13, no intersection. evidence: evidence/run_done_final.log
- [x] 15. case-bom.csv 14 columns, every row has part number or open_action. evidence: evidence/bom_check.log, evidence/bom_check_2.log
- [x] 16. case.py builds body, lid, base, boards, cell, USB-C, 4 pins, ring US 13 and US 5. evidence: evidence/run_done_final.log, evidence/final_listing.log
- [x] 17. case_check.py exits 1 on intersection above 0.001 mm3 or pin out of stroke. evidence: evidence/run_fault_test.log
- [x] 18. Failed once (24 failures, exit 1) then restored (cmp identical). evidence: evidence/run_fault_test.log
- [x] 19. Exports: STEP assemblies, STL body, lid, base, PNG top and sections. evidence: evidence/final_listing.log
- [x] 20. Each PNG looked at with Read; labels fixed 5 times (evidence/edit_labels.log to edit_labels5.log). The earlier out/case_section_pins_US5.png is stale and listed in case-notes.md O10
- [x] 21. Outer size stated: 33.6 x 33.4 x 55.2 mm. evidence: out/case_size.txt
- [x] 22. case-notes.md with rejected choices, open points, questions_for_owner, RESULT last line. evidence: case-notes.md
- [x] 23. Done command exit 0. evidence: evidence/run_done_final.log
- [x] 24. Writes only in design/case/ and design/datasheets/case_*.pdf; no git run. evidence: evidence/final_listing.log
- [x] 25. Ring side unchanged: no ring file edited (all edits in design/case/)
- [x] 26. Web requests carried no personal or company name (URLs in evidence/download*.log, html logs)
- [x] 27. Headless: matplotlib Agg in case.py
- [x] 28. No file name starts with REPORT, SUMMARY, FINDINGS or ANALYSIS. evidence: evidence/final_listing.log
- [x] 29. Final reply under 3,500 characters. evidence: evidence/final_reply.md, evidence/audit.log
- [x] 30. Limits: started 15:05:06 CET; done command last run ended 15:28:29 CET (evidence/run_done_final.log); under 150 tool calls
- [x] 31. Final audit run. evidence: evidence/audit.log
