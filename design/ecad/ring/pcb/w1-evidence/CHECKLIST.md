# W1 checklist (brief, builder rules, and the three lead messages of 2026-11-13)

Evidence paths are relative to `design/ecad/ring/pcb/w1-evidence/` unless they start with `design/`.

- [x] 1. a: library OpenRing.pretty, one file per distinct package of the main-board parts (21 files; band parts are band-circuits'). evidence: final_check_footprints_good.log
- [x] 2. a: pad numbers or ball names as the maker document. evidence: final_check_footprints_good.log; final_measure_u1.log
- [x] 3. a: maker land pattern where the document gives one. evidence: doc-lines.txt; pages/*.png
- [x] 4. a: a courtyard in each footprint. evidence: courtyard_area.log
- [x] 5. a: document name and page in each description. evidence: final_check_footprints_good.log
- [x] 6. a: no description holds PROVISIONAL. evidence: final_check_footprints_good.log
- [x] 7. a: standard passives checked against a maker document. evidence: passive-pads-measured.csv
- [-] 8. a: 0805 pad sizes against a maker document. not done: no readable 0805 maker land (notes, Not closed 2)
- [x] 9. b: footprint-sources.csv, 118 rows, band parts name the band library. evidence: design/ecad/ring/pcb/footprint-sources.csv
- [x] 10. c: maker pin numbers in make_netlist.py (U1, U2, U3, U4, U5, U6, U9, U10, U11, ANT1, X1, X2, J1, DISP1); band pins kept as before. evidence: make_netlist.diff
- [x] 11. c: run_all.sh regenerates. evidence: final_run_all.log
- [x] 12. c: open-pins.csv no rows. evidence: design/ecad/ring/open-pins.csv
- [x] 13. c: ERC 0 and 0. evidence: final_erc_report.txt
- [x] 14. c: check_netlist.py PASS. evidence: final_check_netlist_full.log
- [x] 15. d: C71 closed (AVX 06033C105KAT2A). evidence: avx_query output in final audit; pages/avx_c0g_p3-3.png; datasheets/w1_kyocera_avx_x7r_dielectric.pdf
- [x] 16. d: C85 closed (AVX 0402ZC225KAT2A)
- [x] 17. d: C86 closed (AVX 0603ZC105KAT2A)
- [x] 18. d: C87 closed (same code)
- [x] 19. C60 (lead addition): 2.2 uF AVX 0402ZC225KAT2A in make_netlist.py, parts.csv, bom.csv. evidence: parts.diff; bom.diff
- [-] 20. d: C88. not done: no readable 10 uF 16 V table (notes, Not closed 1)
- [-] 21. d: L71. not done: no readable Murata or other inductor sheet
- [-] 22. d: L72. same
- [-] 23. d: RT1. same
- [-] 24. d: C35 Class 1: three options listed with height and area, lead picks. not done: no readable 0603 C0G 100 nF; evidence avx_c0g_options.log
- [-] 25. d: C36. same
- [x] 26. d: one-line reason per part; Knowles sentence quoted with page. evidence: footprint-notes.md section d
- [x] 27. d: bom.csv and bom-notes.md changed for these lines only; check_bom before and after failures 0. evidence: bom.diff; check_bom_before.log; final_check_bom_after.log
- [x] 28. e (changed by lead): band footprints and band interface file not mine; custom-part-interfaces.md removed; charging pad 1.6 in parts.csv; band rows in footprint-sources.csv. evidence: footprint-sources.csv; parts.diff
- [x] 29. f: check_footprints.py pass, two broken copies fail, band library absent reports not yet delivered without failing. evidence: final_check_footprints_*.log
- [x] 30. g: Not closed list (9 items). evidence: footprint-notes.md
- [x] 31. deferred items answered. evidence: footprint-notes.md
- [x] 32. lists Not closed and Changes other files need; last line RESULT:. evidence: footprint-notes.md
- [x] 33. distributor copy tried (Mouser, DigiKey, LCSC): none returned a sheet. evidence: fetch_attempts.log
- [x] 34. file types of datasheets named by the lead checked. evidence: datasheet_types.log
- [x] 35. no browser, no secret, no git, stderr kept. evidence: this run
- [x] 36. final audit saved. evidence: final_audit.log

## Round 2 (supersedes items 15 to 28 where they differ)
- [x] R1. band pins restored to makers' numbers (SW 1 to 4, M1 and BT1 1, 2). evidence: final_check_netlist_full.log; final_check_band.log (RESULT: PASS boards checked 14)
- [x] R2. check_footprints finds every band pin on a band-library pad; fails when the band library is missing. evidence: final_check_footprints_good.log; final_check_footprints_band_absent.log
- [x] R3. C35, C36 = 1.0 nF C0G 0402 AVX 04025A102JAT2A; value text, bom.csv, bom-notes.md, sch-notes.md O10. evidence: avx_c0g_options.log; bom.diff
- [x] R4. L71, L72, L10 one Murata 1269AS-H-2R2M=P2 footprint from sheet p5. evidence: doc w1b_murata_1269as-h-2r2m.pdf p5; pages/murata_1269as_p5-5.png
- [x] R5. C71, C86, C87 Murata GRM155R61E105KA12D; RT1 confirmed; C85, C60 AVX cell cited. evidence: avx_x7r_cells.log; pages/avx_x7r_p3-3.png
- [-] R6. C88 code. not done: no 10 uF 16 V row at 1.0 mm or less (pages/avx_x7r_p3-3.png)
- [x] R7. notes section Round 2 with both check lines and the RESULT line last. evidence: footprint-notes.md
- [x] R8. final audit rerun. evidence: final_audit.log
