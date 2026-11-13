# Checklist, antenna study F06 (brief from the lead, design commit ff89faf)

- [x] 1. Script design/mech/antenna/measure_antenna.py reads placement.csv and layers.json (STEP only if needed) evidence: measure.log line 1 (inputs); STEP needed for walls and formed glass (antenna-study.md section 1)
- [x] 2. It prints the distance to each metal surface: two side walls, end wall, floor evidence: measure.log lines 10, 12, 14, 17
- [x] 3. It prints what lies above up to the outside air, by layer, with thicknesses evidence: measure.log lines 26 to 110
- [x] 4. It prints whether the screen panel covers the antenna evidence: measure.log lines 112 to 116
- [x] 5. measure.log saved, last line `RESULT measured` evidence: measure.log line 159; audit_final.log "measure.log last line"
- [x] 6. Johanson requirements quoted with pages: ground clearance area evidence: antenna-study.md section 2; johanson_8p_text.log lines 158, 326; ds8_p3.png, ds8_p5.png
- [x] 7. Johanson: matching evidence: johanson_8p_text.log lines 169, 316, 384
- [x] 8. Johanson: efficiency or gain evidence: johanson_8p_text.log lines 34 to 44; johanson_text.log lines 37 to 45
- [x] 9. Johanson: board size they were measured on evidence: johanson_8p_text.log line 33; ds8_p3.png (40 x 20)
- [x] 10. Datasheet searched first in design/datasheets; fetched with getpdf.sh only if absent evidence: johanson_urls.log (search of repo), fetch_1.log, fetch_2.log, datasheet_hashes.log
- [x] 11. Plain statement of what can and cannot be claimed; no invented efficiency or range evidence: antenna-study.md section 3; audit_final.log NUMBER lines
- [x] 12. Option (a) with its variants: glass end (a1), hand-end insert (a2), resin-filled slot (a3), plus radio corner (a4) evidence: antenna-study.md section 4 table; audit_final.log "options table row"
- [x] 13. Option (b) evidence: antenna-study.md section 4 row (b)
- [x] 14. Option (c) evidence: antenna-study.md section 4 row (c)
- [x] 15. Option (d) evidence: antenna-study.md section 4 row (d)
- [x] 16. Option (e) evidence: antenna-study.md section 4 row (e)
- [x] 17. Metal-case practice cited only from sources opened; blocked pages recorded evidence: fetch_appnotes2.log, fetch_appnotes3.log, html_nordic_head.log, html_silabs.log, taoglas_head.log, abracon_text.log, search_metal_case.log
- [x] 18. Exactly ONE recommendation with exact geometry evidence: audit_final.log "recommendation headings: 1"; insert_check.log
- [x] 19. List of files that would change, one line per change; files not changed evidence: antenna-study.md section 5 items 1 to 15; changed_since_start.log (my writes only in mech/antenna and datasheets/antenna_*; the other files listed there are other helpers' work)
- [x] 20. Bench test: what to build, what to measure, pass line evidence: antenna-study.md section 6; bench-plan.md lines 21 to 22
- [x] 21. What the owner would see evidence: antenna-study.md section 7
- [x] 22. Every number carries a source or [ESTIMATE] evidence: audit_final.log (decimal numbers, CALC arithmetic, citations)
- [x] 23. Options table covers (a) to (e) evidence: audit_final.log "options table row"
- [x] 24. Last line of antenna-study.md `RESULT: ...` evidence: audit_final.log "last line"
- [x] 25. Writes only in design/mech/antenna/ and design/datasheets/antenna_* evidence: changed_since_start.log
- [x] 26. No git, no install, no browser, no folder deleted evidence: commands of this run (none of these used); pages read as PNG rendered by PyMuPDF (render_pages.log)
- [x] 27. Heavy commands one at a time with nice -n 19 evidence: STEP runs measure.log, insert_check.log were run one after the other with nice
- [x] 28. Owner's shape kept: no thicker, wider or longer block evidence: antenna-study.md section 5 (the corner keeps the body's outer shape)
- [x] 29. Plain English, no em dashes evidence: audit_final.log "em dashes: 0" for both files
- [x] 30. Final reply under 3,500 characters evidence: final-reply.md length 3493 (printed by the trim step)
- [x] 31. Final audit run, output saved evidence: audit_final.log

Open, not done here: integers in the texts (ray counts, page numbers, pass-line choices) are checked by the audit only where listed (counts of file changes and blocked downloads); the rest were checked by reading the cited lines (audit_final.log CITE lines). Earlier audit passes: audit_run1.log, audit_run2.log, audit_run3.log. Earlier crash: insert_check_run1_crash.log (empty intersection, fixed).
