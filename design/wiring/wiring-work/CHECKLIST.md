# Checklist (product wiring list), started 2026-11-13 07:46 CET

Brief fields: Owns, Must not touch, Writes to, Done when present. "Quality reference to copy": no file is named; the brief's "Bar (each can fail)" list 1 to 6 is used as the quality reference (my reading, stated in the notes).

- [x] 1. product-wiring.csv: one line per conductor. evidence: design/wiring/product-wiring.csv (67 lines), wiring-work/check-final3.log
- [x] 2. csv columns (id, joint, signals, ends with board/ref/pin/face, carrier, join at each end, proof per end and carrier, state). evidence: header of product-wiring.csv; COLUMNS in build_wiring.py
- [x] 3. build_wiring.py builds csv from files; only system-joints rows typed. evidence: build_wiring.py, wiring-work/build12.log
- [x] 4. build twice gives the same file. evidence: wiring-work/cmp-run12-run13.log (empty, cmp exit 0 in wiring-work/final3-run.time)
- [x] 5. check: every off-board pin and board-to-board land in exactly one line. evidence: wiring-work/check-final3.log (89 of 89)
- [x] 6. check: signal names agree or pairing rule named. evidence: check_wiring.py ends-disagree; wiring-work/broken-final4.log
- [x] 7. check: lead cut length for 7 sizes or "not size dependent". evidence: check_wiring.py lead-length; broken-final4.log
- [x] 8. check: no `not drawn`. evidence: check_wiring.py state check; check-final3.log `not drawn 0`
- [x] 9. check prints counts per state and per joint. evidence: wiring-work/check-final3.log
- [x] 10. check finds quoted proofs again. evidence: check_wiring.py proof-text and proof-board; broken-final4.log proof_wrong_line
- [x] 11. broken: terminal in two lines. evidence: wiring-work/broken/terminal_twice.log
- [x] 12. broken: terminal in no line. evidence: wiring-work/broken/terminal_missing.log
- [x] 13. broken: ends disagree. evidence: wiring-work/broken/ends_disagree.log
- [x] 14. broken: lead without length. evidence: wiring-work/broken/lead_no_length.log
- [x] 15. broken: proof line without the quoted text. evidence: wiring-work/broken/proof_wrong_line.log
- [x] 16. system-joints.csv R10 rows with sources. evidence: design/wiring/system-joints.csv rows 1 to 3
- [x] 17. system-joints.csv R15 rows with sources. evidence: system-joints.csv rows 5 to 8
- [x] 18. system-joints.csv R16 row (no conductor, gap). evidence: system-joints.csv row 9
- [x] 19. silent sources not invented, missing listed. evidence: product-wiring-notes.md "missing in the design files"
- [x] 20. connections.md Part 1 cells, table shape, Count line, dated note. evidence: wiring-work/apply_connections.log, connections-fieldcount.log, connections.diff
- [x] 21. connections.md Parts 2 to 6 dated line each. evidence: wiring-work/connections.diff
- [x] 22. draw_wiring.py makes svg and pdf from the csv. evidence: wiring-work/draw-final3.log, product-wiring.svg, product-wiring.pdf
- [x] 23. drawing count equals csv count, printed. evidence: wiring-work/draw-final3.log (67 and 67)
- [x] 24. picture converted without a browser and read. evidence: wiring-work/pictures/final3-svg.png, final3-pdf-1.png; notes Step 5
- [x] 25. notes written step by step. evidence: design/wiring/product-wiring-notes.md
- [x] 26. final build then check, last line quoted. evidence: notes Step 4, wiring-work/check-final3.log
- [x] 27. questions_for_owner and missing list at the end. evidence: product-wiring-notes.md
- [x] 28. last line of notes is the RESULT line. evidence: product-wiring-notes.md last line
- [x] 29. rules kept: writes only in Owns and wiring-work; no git; no browser; nice -n 19; no stream to /dev/null. evidence: commands of this session (no git, no browser); file list in notes "Files delivered"
- [x] 30. design-file problems reported to the lead. evidence: final reply (J1 face, PRT1 not a part, length differences); notes Step 6
- [x] 31. final reply under 3,500 characters, audit run. evidence: wiring-work/final-reply.txt, wiring-work/audit.log
- [x] 32. lead ruling: state specified and landed, check incomplete and state-kind, share complete printed, screen one line per signal contact. evidence: wiring-work/check-final3.log, broken-final4.log, notes Step 7 and 8
