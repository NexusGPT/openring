# Checklist, ring 3D model (brief from team-lead, 2026-11-10, start 15:04) - OLD BLOCK MODEL, replaced by the inside model in design/mech/thin/ (thin.py, model v9; notes design/mech/thin/model-v9-notes.md) with the exterior in design/look/s1/; the numbers below describe the one-block model of version A1 and are not edited

Expected before the first full run: ring.py exit 0; check_fit.py exit 0; with RING_OVERRIDE=cell_t=5.6 exit 1.
Differences seen: run1 band fillet failed (logs/run1_ring.log); run2 offset failed (logs/run2.log); run3 check_fit exit 1 with 5 findings (foam pad x cable fold, gasket x 4 screws; logs/run3.log), fixed; band orientation wrong in run3 (base bbox Z min -10.08, logs/run2.log tail), fixed; side view band lines wrong, fixed (run6).

- [x] 1. ring.py one parametric script, DIM_TABLE at top. evidence: ring.py
- [x] 2. dimensions.csv from the table, ASSUMED marked (25 rows). evidence: dimensions.csv
- [x] 3. ring formula checked on Wikipedia "Ring size", cited. evidence: src_text/wikipedia_ring_size_raw.txt line 81, dimensions.csv ring_a
- [x] 4. top shell walls 1.0, r3.0, glass seat. evidence: logs/thin_spots.log (nominal wall 1.0), ring.py build_top_shell
- [x] 5. 4 mic openings at X -12.0, -5.5, +1.0, +7.5. evidence: ring.py build_top_shell, out/top-view.png
- [x] 6. clear-window recess at X +4.0. evidence: out/top-view.png, placement.csv clear_window
- [x] 7. 5.0 joystick opening at X -6.0. evidence: out/section-across-x-6.png
- [x] 8. recessed button opening at X +4.0. evidence: logs/thin_spots.log (recess skin 0.2)
- [x] 9. base: floor 0.8, window X -12.6, 4 holes, groove, cradle. evidence: out/section-along-y-2.5.png, out/section-end-x0-bands.png
- [x] 10. band sizes 5..13. evidence: out/base-size5.stl .. base-size13.stl, logs/derived.log
- [x] 11. internal parts at their sizes (34 solids). evidence: placement.csv
- [x] 12. placement.csv. evidence: placement.csv (34 parts + header)
- [x] 13. check_fit.py checks and exits 1 on any. evidence: logs/run3.log (exit 1 on real findings)
- [x] 14. fails with cell +1 mm. evidence: logs/failproof_cell_plus1.log (exit 1); normal run logs/final_donewhen.log (exit 0)
- [x] 15. STEP assembly size 9. evidence: out/ring-assembly-size9.step
- [x] 16. 10 STL + STEP. evidence: logs/final_donewhen.log file list
- [x] 17. drawings PNG+SVG (5 views), each PNG read. evidence: out/*.png
- [x] 18. mech-notes.md with all sections. evidence: mech-notes.md, logs/audit2.log
- [x] 19. Done-when exit 0. evidence: logs/final_donewhen.log
- [x] 20. only design/mech/ written, no git run. evidence: commands in this session
