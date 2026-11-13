# Checklist: circuit changes C1 (R73) and C2 (C84 4.7 uF), phase 1 and 2

Started 2026-11-13 12:49:32 CET (date). Base: commit 6aa797bd.

## Phase 1 (write only in design/ecad/ring-circuit-work/)
- [x] 1. Read the four rows of lead-decisions.md in full. evidence: read in session (rows 28, 29, 33, 48 of design/wiring/lead-decisions.md); quoted in notes.md.
- [x] 2. Read make_netlist.py, gen_sch.py, check_netlist.py, run_all.sh; additions.csv, symbols.csv, sch-notes.md read in part. evidence: notes.md section 1.
- [x] 3. Source of netlist.csv and parts.csv is make_netlist.py. evidence: logs/source_proof.txt, logs/base_make_netlist.log.
- [x] 4. netlist.csv: R73 pad 1 VBUS, pad 2 GND. evidence: logs/patched_vs_base_ring.diff.
- [x] 5. parts.csv: R73 row. evidence: logs/patched_vs_base_ring.diff.
- [x] 6. parts.csv: C84 4.7uF GRM155R61A475MEAAD; C83 unchanged. evidence: logs/patched_vs_base_ring.diff.
- [x] 7. additions.csv: R73 with reason; C84 text. evidence: logs/patched_vs_base_ring.diff.
- [x] 8. Schematic source: gen_sch.py needs no change (draws by parts.csv sheet); R73 on power sheet. evidence: logs/r73_in_power_sheet.txt, logs/pdf_r73.txt.
- [x] 9. sch-notes.md: one dated paragraph. evidence: logs/patched2_edit.log; patched2/design/ecad/ring/sch-notes.md (last paragraph).
- [x] 10. bom.csv: split, R73 row, 14 fields. evidence: phase2_edit.py field check passed (logs/patched2_edit.log "edit exit 0"); logs/chain_patched2_check_bom.log "failures 0".
- [x] 11. bom-notes.md: two lines. evidence: logs/patched_vs_base_bom.diff.
- [x] 12. R73 code written with "not confirmed at a distributor". evidence: phase2_edit.py (make_netlist comment, additions, bom row, bom-notes, sch-notes).
- [x] 13. Each replacement matches once. evidence: phase2_edit.py once(); logs/patched2_edit.log "edit exit 0".
- [x] 14. Unpatched copy: ring1 FAIL, ring7 FAIL. evidence: bench_base/summary.txt; logs/diff_committed_vs_base_summary.txt.
- [x] 15. Patched copy: ring1 PASS, ring7 PASS. evidence: bench_patched/summary.txt.
- [x] 16. No row PASS to FAIL. evidence: logs/compare_base_patched.txt "PASS to FAIL: none".
- [x] 17. sim/circuit untouched in phase 1. evidence: logs/sim_tree_diff_phase1_sorted.txt "sorted diff exit 0".
- [x] 18. Stepped pass line written before run. evidence: stepped/pass-line.md (12:52:45), logs/stepped.start (12:56:55).
- [x] 19. Stepped at 4.7 uF. evidence: stepped/out_sw/stepped_compare.csv.
- [x] 20. Stepped at 10 uF. evidence: stepped/out_sw/stepped_compare.csv.
- [x] 21. No rule written. evidence: stepped/result.md (report only).
- [x] 22. Own models marked. evidence: stepped/models/tlv755p30_sw.lib header, tlv755p30_dis.lib header.
- [x] 23. check_netlist red on patched copy, reported to lead. evidence: logs/chain_patched2_check.log, logs/chain_base_check.log; SendMessage.
- [x] 24. DC bias effect reported. evidence: stepped/out_sw/stepped_compare.csv rows 3.25uF, 4.0uF.
- [x] 25. Work folder under 50 MB. evidence: logs/du_phase1.txt.
- [x] 26. Phase 1 notes and reply. evidence: notes.md.

## Phase 2 (only after the lead writes "review 3 has ended")
- [x] 27. Applied (C1, C2, C3, text fixes, check rows). evidence: p2/apply_edit.log, p2/tables_move.log, p2/regen_proof.txt.
- [x] 28. ERC 0 errors 0 warnings before and after. evidence: p2/erc-report_before.txt, design/ecad/ring/erc-report.txt.
- [x] 29. run_all.sh c2; check_netlist exit 0 (granted by the lead). evidence: p2/run_all_c2.log, design/ecad/ring/evidence/check_c2.log; fail proofs logs/failproof_summary.txt.
- [x] 30. check_bom failures 0. evidence: p2/check_bom_after.log.
- [x] 31. Bench in place. evidence: p2/summary_before.txt, sim/circuit/results/summary.txt, p2/compare_base2_inplace.txt.
- [x] 32. evidence: sim/circuit/decks/stepped/, results/stepped/, logs/stepped_enable_c2.log, sim-notes.md section 12.
- [x] 33. evidence: p2/pcb_diff.txt "pcb diff exit 0"; circuit-two-notes.md.
- [x] 34. evidence: design/ecad/ring/circuit-two-notes.md.

## Standing rules
- [x] 35. Heavy commands at nice -n 19, one at a time; long ones in background with exit files. evidence: logs/*.exit, logs/*.start.
- [x] 36. No stderr to /dev/null; no browser; no web; no git; no em dashes. evidence: commands in this session.
- [x] 37. Final audits: logs/audit_phase1.txt, logs/audit_phase2.txt ("with no match 0").

## Added by the lead in phase 2
- [x] 38. C3 C90 on VDD_3V0, bom row, bom-notes line, check row with fail proof. evidence: logs/patched3_netlist.diff, logs/failproof_summary.txt.
- [x] 39. C88 text fixes (make_netlist.py comment, sch-notes row 6) and the load switch sentence. evidence: phase2_edit.py, p2/apply_equal.txt.
- [x] 40. 3.0 V rail rows before and after. evidence: p2/compare_base2_inplace.txt.
