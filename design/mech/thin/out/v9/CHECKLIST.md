# Model v9 checklist (from the lead's brief of 2026-11-13 and the builder rules)

- [x] 1. Baseline: fit check US 9 on the files as found (cdb1ddc), expect `RESULT PASS pairs=1080 parts=47`, via out/v9/run_check.sh (copy of out/v8/run_check.sh, log folder out/v9)
- [x] 2. Board parts: every part the model draws on the main board at the place, turn and body size of placement-plan.csv, footprint-sources.csv and OpenRing.pretty
- [x] 2a. Rows the plan found wrong: ANT1, J1, U4, L10, L71, L72, X2, U2, C84 (each)
- [x] 2b. Every other drawn row compared, and each one that differs found and listed
- [x] 2c. Side B = screen face (the 19 test pads): stated how the model treats it
- [x] 2d. No notch in the board outline
- [x] 3. Radio corner: resin part (class resin) X -14.80 to -8.60 at the hand-end corner, +Y side, Y 2.05 to the skin; floor pocket X -12.60 to -9.00, Y 4.25 to 6.25, 0.20 deep
- [x] 3a. ANT1 stands in the pocket's room
- [x] 3b. Metal left around the corner reported (numbers)
- [x] 3c. Free space antenna to metal reported (numbers)
- [x] 4. Named test in check_thin.py: every board part within 0.01 mm of its plan row (place, turn, body size)
- [x] 4a. Named test: the copper-free zone X -13.60 to -8.75, Y 3.10 to 6.30 holds no metal part
- [x] 4b. Broken copy (one part moved 0.3 mm) fails the test, log kept
- [x] 4c. Broken copy for the zone rule (one per new test), log kept
- [x] 5. Item 44: rule, motor free space to the body per size (7 sizes), motor to the copper-free zone per size; model changed only if a rule fails
- [x] 6. Item 104: thin-inside.step read back by a fresh process, solid count and volume per part against the model in memory
- [x] 6a. Item 104 for each regenerated maker file (fresh process)
- [x] 7. Fit check US 7 to 13 on the FINAL thin.py: one chain script at nice -n 19, real exit code to a .done file; end turn naming script, pid, logs
- [x] 8. Regenerate: export_parts.py 7 8 9 10 11 12 13 (body, band liner, joystick stiffener, main board, assembly, every changed part); index.csv rows (flex-tail rows corrected)
- [x] 8a. Drawings with design/mfg/tools/draw.py
- [x] 8b. Text of specs, assembly.md and architecture.md of band-fit-notes.md sections e and h (each line: value now, value needed)
- [x] 8c. Lines made wrong by v9, found by a search, each changed line listed
- [x] 8d. architecture.md line 156 (Sources 3 row 3)
- [x] 9. Final checks with last line quoted: 7 fit checks; check_parts.py; check_docs.py; check_band.py (`RESULT: PASS boards checked 14`)
- [x] 10. model-v9-notes.md: every changed value with its source; every changed text line; items 44 and 104 with numbers; "Not proven and limits"; questions_for_owner; last line `RESULT: <done|blocked>, <one sentence>`
- [x] 11. Stop-and-report conditions not crossed (outside shape, screen, cell capacity over 2 percent, block 3.20, board thickness or outline, board part place, ribbons of v8) or reported
- [x] 12. Rules: no git, no browser, nice -n 19 one heavy run at a time, no stderr to /dev/null, no secret, scratch files removed, clock from date

Evidence so far (04:25): 1 out/v9/baseline_us9.log (RESULT PASS pairs=1080 parts=47); 2a, 2b out/v9/board/compare_before.log and model-v9-notes.md b; 2c main-board.md last section and notes b; 2d thin.py main_board (no notch_a) and dev1_us9.log; 3a dev1_us9.log `ANTENNA body ... under the antenna 0.0300 mm of room`; 3b, 3c out/v9/corner_probe2.log; 4b out/v9/broken_place/named_test.log; 4c out/v9/broken_zone/named_test.log; 6 out/v9/item104/run_v8.log, run_v9.log, readback_fake.log. Items 2, 3, 4, 4a: green at US 9 (dev1_us9.log); closed by the 7-size chain. Item 7 running: out/v9/chain_fit.sh final, pid 3081, started 04:24:11.

Final (06:20): 2, 3, 4, 4a final_us7.log to final_us13.log (BOARD-PLAN 0.0000, ZONE 0 hits, RESULT PASS each); 5 model-v9-notes.md section j; 6a item104/maker_readback.log RESULT PASS files=52; 7 final_chain.done (7 sizes exit 0, hashes equal start and end); 8 export/export_parts_v9.log exit 0, index.csv 104 rows; 8a draw_v9.log 80 drawn, draw_v9_footstiffener.log 14 drawn; 8b, 8c, 8d notes sections l and m, final/line_alignment_3.log; 9 final_checks.done (check_bom fails on RC1 only, row given); 10 model-v9-notes.md; 11 no stop condition crossed (outside shape, screen, cell 0 percent, block 3.20, board outline and thickness, board places as the table, v8 ribbons all unchanged); 12 audit.log and audit2.log (12 unmatched items: deleted files named as deleted, name patterns, command texts and proposed text).
