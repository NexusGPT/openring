# Ring main board, round 5: board A2 of the thin ring (2026-11-13)

Computed from the board files; nothing here was measured on hardware. Work, logs and scripts: `design/ecad/ring-apply-a2/` (below: A/; its `notes.md` holds every step). The board comes from `design/ecad/ring-route-g` (board A1: J1 to the under face), `design/ecad/ring-route-h` (board A2: the eight 0201 parts to the under face) and `design/ecad/ring-route-i` (board A2b: the controlled-line limits met again). Decision: the last row of `design/wiring/lead-decisions.md`. The earlier notes `board-notes.md` to `board-notes-r4.md` are unchanged.

## What changed from round 4
- `ring.kicad_pcb`: byte copy of board A2b, `design/ecad/ring-route-i/pcb/ring-thin-a2b.kicad_pcb` (A/logs/a2b-in-sha.log): A2 (`design/ecad/ring-route-h`) with three controlled-line limits brought back (route-i notes.md): C5's VDD_1V8 run moved off In1 under the antenna line (now In2 and B.Cu there), a DECA In2 run beside XC2 and a DECA branch beside XL2 removed; copper A2 to A2b: removed 76, added 13 items, nets DECA and VDD_1V8 only; no part moved. `ring.kicad_pro` and `ring.kicad_dru` were already equal to A2's (same file). J1 on the under face (F.Cu) at X -11.650, Y -0.150, turned 270, cable opening toward X minus; its 11 nets run on the screen face (B.Cu) to one F-B via in each land. C1, C2, C5, C7, C14, FB1, R71, R72 on the under face. The screen face holds only the 12 test pads.
- The round-4 board, its placement table, report, pictures and fabrication files are kept in `fallback-417/` (README.md there) for the 4.17 mm block with the stock screen.
- `placement-final.csv`: the rows of J1 and the eight parts, written from the board (A/scripts/update_placement.py; diff A/logs/placement-final.diff, 9 rows).
- `check_escapes.py` (check 6 of check_board.py): declared exception `A2_ROUTER_ESCAPE` for U2 E1 (VSET2) and E2 (VSET1): R71 and R72 moved away from U2, their locked L1 escapes are gone and router copper meets the lands (A/logs/check_escapes.diff).
- `drc-report.txt`, `fab/` (make_fab.sh), `pictures/ring-<layer>.svg`: regenerated on A2. Screen face: no paste opening, 12 mask openings (A/logs/paste-mask-counts.log).

## Checks (A/check_all.sh; last lines in A/notes.md)
- Rules check: Found 0 violations, Found 0 unconnected items.
- check_board.py RESULT: PASS; check_footprints.py RESULT PASS; check_netlist.py RESULT PASS.
- Placement table read-back: RESULT PASS; a broken row fails.

## The 8 controlled-line limits (bar 6 of A/check_all.sh; script design/ecad/ring-route-i/scripts/lines_all.sh)
All 8 met on A2b as on round 4 (design/ecad/ring-route-i/logs/lines_check-final.log `RESULT PASS`): antenna L1 clearance 0.2055 mm; antenna ground under the line outside the copper-free zone 100.0 percent; XC1 0.205 mm; XC2 0.21 mm; USB Zdiff 92.1 / 104.7 ohm as accepted; XL1 shortest path 9.343 mm as accepted; beyond 1.0 mm outside U1's body only U1_VBUS beside XL1 (0.0908) and LCD_SCK beside XL2 (0.1705), as accepted. The same script on fallback-417 gives the same figures (round 4). Board A2 itself failed three of them (antenna ground 94.0920 percent, XC2 0.1900 mm, a DECA via 0.0862 mm from XL2): design/ecad/ring-route-i/logs/lines_check2-i00.log.

## What is left
- The J1 lines W040 to W053 of the wiring list name the custom panel tail of design/mfg/specs/screen-panel-custom.md section e (lead's ruling, build_wiring.py changed; A/notes.md); no panel maker is chosen yet.
- The joint-table test "real ring-B regions moved 1.0 mm" (design/mfg/assembly/joint-table-work/tests/run_tests.py line 210) expects 17 screen-face paste regions; A2's screen face has none, and joints.csv row P-ring-B still describes the screen-face pass (A/notes.md).
- Documents that still state the round-4 places are listed in A/notes.md step 6.
