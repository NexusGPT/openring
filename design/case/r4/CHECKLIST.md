# Checklist, case model r4 (boards from their files)

Output folder: design/case/r4/

- [x] 1. Baseline PASS 3447 pairs, 22 min 42 s. evidence: base_check.log
- [x] 2. Round 2 read; list items 1 to 6 handled (1 to 4 in the model, 5 and 6 in the BOM and texts). evidence: ../case-model-r4-notes.md sections 2, 10; edit_bom.log; edit_docs1.log
- [x] 3. Main board outline, thickness, bodies read from the files. evidence: final_check.log lines "15a"
- [x] 4. Pin board read from its file. evidence: final_check.log "15a pin_board" lines
- [-] 5. A part moved on the board changes the model: not done as its own moved-part run; shown by the broken copies (board longer, J1 taller) whose builds follow the edited files. evidence: broken_board_long_check.log, broken_part_tall_check.log. Limit: time.
- [x] 6. 23.0 x 37.9, asymmetric, U1 overhang, 10.2 tab, wire pads from the file. evidence: inspect_now.log, final_check.log "15a main board outline"
- [x] 7. 16 back-face test pads, no body. evidence: final_check.log "15a main board back face"
- [x] 8. Holding feature, 2 options, numbers, USB push/pull. evidence: ../case-model-r4-notes.md sections 4, 7
- [x] 9. Holder and stakes kept (pockets and a recess cut). evidence: final_check.log "14 pin holder"
- [x] 10. Nine leads modelled and checked. evidence: final_check.log lines "16"
- [x] 11. Lift test with pre-written pass line. evidence: final_check.log lines "17"
- [x] 12. case_check PASS 8012 pairs 0 failures. evidence: final_check.log
- [x] 13. Board 1 mm too long fails. evidence: broken_board_long_check.log
- [x] 14. Part 1 mm too tall fails. evidence: broken_part_tall_check.log
- [x] 15. Wall in lift path fails. evidence: broken_lift_wall_check.log
- [x] 16. check_case_docs PASS. evidence: final_docs2.log
- [x] 17. Doc lines corrected and listed. evidence: edit_bom.log, edit_docs1.log, edit_docs2.log
- [x] 18. out/ regenerated; pictures listed as older, none re-rendered. evidence: final_build.log; notes "Not proven and limits"
- [x] 19. Notes complete with RESULT last line. evidence: ../case-model-r4-notes.md
- [x] 20. Heavy runs one at a time, nice 19, .done files. evidence: run_final.sh, run_broken2.sh
- [x] 21. Outside unchanged. evidence: outside_compare.log
- [x] 22. No browser, no git, no secret; scratch model files removed with listing. evidence: scratch_removed_list.log, scratch_after.log
- [x] 23. Ring files and dates. evidence: ring_files_dates.log, placement_compare.log
- [x] 24. Final audit. evidence: final_audit.log
