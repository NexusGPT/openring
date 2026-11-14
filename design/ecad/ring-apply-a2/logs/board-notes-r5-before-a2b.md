# Ring main board, round 5: board A2 of the thin ring (2026-11-13)

Computed from the board files; nothing here was measured on hardware. Work, logs and scripts: `design/ecad/ring-apply-a2/` (below: A/; its `notes.md` holds every step). The board comes from `design/ecad/ring-route-g` (board A1: J1 to the under face) and `design/ecad/ring-route-h` (board A2: the eight 0201 parts to the under face). Decision: the last row of `design/wiring/lead-decisions.md`. The earlier notes `board-notes.md` to `board-notes-r4.md` are unchanged.

## What changed from round 4
- `ring.kicad_pcb`: byte copy of `design/ecad/ring-route-h/pcb/ring-thin-a2.kicad_pcb` (A/logs/a2-in-sha.log). `ring.kicad_pro` and `ring.kicad_dru` were already equal to A2's (same file). J1 on the under face (F.Cu) at X -11.650, Y -0.150, turned 270, cable opening toward X minus; its 11 nets run on the screen face (B.Cu) to one F-B via in each land. C1, C2, C5, C7, C14, FB1, R71, R72 on the under face. The screen face holds only the 12 test pads.
- The round-4 board, its placement table, report, pictures and fabrication files are kept in `fallback-417/` (README.md there) for the 4.17 mm block with the stock screen.
- `placement-final.csv`: the rows of J1 and the eight parts, written from the board (A/scripts/update_placement.py; diff A/logs/placement-final.diff, 9 rows).
- `check_escapes.py` (check 6 of check_board.py): declared exception `A2_ROUTER_ESCAPE` for U2 E1 (VSET2) and E2 (VSET1): R71 and R72 moved away from U2, their locked L1 escapes are gone and router copper meets the lands (A/logs/check_escapes.diff).
- `drc-report.txt`, `fab/` (make_fab.sh), `pictures/ring-<layer>.svg`: regenerated on A2. Screen face: no paste opening, 12 mask openings (A/logs/paste-mask-counts.log).

## Checks (A/check_all.sh; last lines in A/notes.md)
- Rules check: Found 0 violations, Found 0 unconnected items.
- check_board.py RESULT: PASS; check_footprints.py RESULT PASS; check_netlist.py RESULT PASS.
- Placement table read-back: RESULT PASS; a broken row fails.

## The 8 controlled-line limits on A2 (A/logs/p4p5-a2.log, A/logs/xcheck-a2.log; the fallback board gives round 4's figures, A/logs/p4p5-fb417.log)
Three are exceeded on A2, all by copper of the moved parts: the antenna ground reference under the line (94.0920 percent, limit 100 percent outside the copper-free zone), XC2 gap (0.1900 mm to DECA, limit 0.20) and XL2 gap (a DECA via 0.0862 mm from XL2 outside U1's ball field, beyond the lead's waiver). Antenna L1 clearance 0.2055 mm and XC1 0.2050 mm are met; USB and XL1 are as accepted in round 4. Table: A/notes.md step 4.

## What is left
- The three line limits above.
- The J1 lines W040 to W053 of the wiring list name the custom panel tail of design/mfg/specs/screen-panel-custom.md section e (lead's ruling, build_wiring.py changed; A/notes.md); no panel maker is chosen yet.
- The joint-table test "real ring-B regions moved 1.0 mm" (design/mfg/assembly/joint-table-work/tests/run_tests.py line 210) expects 17 screen-face paste regions; A2's screen face has none, and joints.csv row P-ring-B still describes the screen-face pass (A/notes.md).
- Documents that still state the round-4 places are listed in A/notes.md step 6.
