# Checklist (brief of 2026-11-13, case pin board marks and wire order)
E = design/ecad/case/pcb/evidence/marks/

- [x] 1. m2 (a) front marks "P1 +" on the P1 wing and "P4 -" on the P4 wing, F.SilkS, 1.0 mm high. evidence: E add_marks.log, E pins_dump_after.log (2 PCB_TEXT F.Silkscreen), E s4_check_boards.log "ok   marks: ..."
- [x] 2. m2 (a) back marks P1 + / P4 GND / P2 D- / P3 D+ on B.SilkS (name above the pad, content below). evidence: E pins_dump_after.log (8 PCB_TEXT B.Silkscreen)
- [-] 3. m2 front mark "P2 D-" and "P3 D+" on the inner piece front: not done: no free place at 1.0 mm height (nearest spots are on the wings, E search_pins_F_inner.log); marks on the back instead (item 2)
- [x] 4. m2 marks at the main board wire pads W1 to W4, W7: bottom face, E main_dump_after.log (5 PCB_TEXT B.Silkscreen), E search_main_R_B.log
- [-] 5. m2 main board top face marks: not done: nearest free place for W1 is 2.38 mm away on the row of W2, the other four 5.06 to 5.60 mm away (E search_main_F_final.log)
- [-] 6. m2 (b) one outline proof: not applicable: the file holds 3 separate outlines (E pins_dump_before.log, 12 Edge.Cuts lines); (a) done
- [x] 7. text height statement: 1.0 mm high, stroke 0.15 mm, the maker's figure 40 mil (1.0 mm) in E ../capab_jlc.html.txt; board-notes.md Round 3
- [x] 8. copper, pads, outline unchanged: E dump_after.log (IDENTICAL both boards), E compare_fab.log (copper layer files equal except date lines), E diff_case_pins.txt and diff_case_main.txt (0 removed lines)
- [x] 9. rules check both boards 0 violations 0 unconnected: E s4_check_boards.log
- [x] 10. m4 five wire pads in netlist by make_netlist.py: E s4_make_netlist.log, E parity_before.log (5 without row) and E parity_after.log (0)
- [x] 11. netlist check passes: design/ecad/case/evidence/check_marks_s4.log last line RESULT PASS netlist netlist.csv
- [x] 12. check_boards.py passes and its broken copies fail: E s4_check_boards.log, E broken/exits.txt
- [x] 13. m3 numbered procedure in board-notes.md "Wiring table (replaces part f)": which end first, W4 first and W1 last with reason, W2 W3 twist (no source: lead's instruction), colours, cut lengths, strip length, continuity from each pin, no continuity between the five (10 pairs)
- [x] 14. fabrication files made again with the project script, list with sizes: E fab_exits.txt, E fab_sizes_final.txt, E compare_fab.log
- [x] 15. check_case_docs.py ends RESULT PASS: E s4_check_case_docs.log
- [x] 16. notes end with questions_for_owner and RESULT line: design/wiring/case-marks-notes.md
- [x] 17. nothing left outside my folders: E processes_after.txt (0 lines), E git_status_marks.log (0 ignored)
