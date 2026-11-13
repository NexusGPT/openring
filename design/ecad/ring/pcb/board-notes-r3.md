# Ring main board, round 3: the routed board of ring-route-f becomes the design's board

Written 2026-11-13 from 10:53 (`evidence/r3/start.txt`). Evidence: `evidence/r3/` beside this file (R3 below). Copies of every file before my change: `R3/before/` (listing `R3/before_listing.log`). Checklist: `R3/CHECKLIST.md`. Base: commit b3fc2db1. I made no git write.

## Step 1. Circuit (bar 2)

- `../make_netlist.py` (diff `R3/diff_make_netlist.txt`): U1 F4 = LCD_TE, F9 = OLED_PWR_EN, D6, E9, F8 = no-connect; SPARE_P1_02, SPARE_P1_14, SPARE_P1_30 gone; TP8, TP9, TP11 in `TP_REMOVED` and in the not-placed list (they are in the frozen bom snapshot, as TP2 and TP13 of round 2). Each line names "lead's decision of 2026-11-13, pin changes for routing". Run: `R3/a_make_netlist2.log` `netlist rows 404 parts 110 nets 84`, `exit 0` (round 2: 407, 113, 87).
- First chain run, before the expectations changed: `R3/check_netlist_w2r3_first.log` `RESULT FAIL 6 netlist netlist.csv`; the five section 7 rows LCD_TE, OLED_PWR_EN, SPARE_P1_02, SPARE_P1_14, SPARE_P1_30 and the row count `42 of 47`. Nothing else failed.
- Expected values changed in `../check_netlist.py` (diff `R3/diff_check_netlist.txt`), each with the ruling "lead's decision of 2026-11-13, pin changes for routing":
  1. `W2_OPEN`: before `'H4': 'JOY_CENTER'}`, after the same plus `'F8': 'SPARE_P1_02'` (P1.02 stays in the section 7 spare row, marked not connected).
  2. Added check: U1 D6, E9, F8 no-connect; SPARE_P1_02, SPARE_P1_14, SPARE_P1_30, TP8, TP9, TP11 absent (a new pass condition, nothing loosened).
  3. The section 7 rows themselves come from `design/architecture.md` (step 5): LCD_TE P1.14 F4, OLED_PWR_EN P1.30 F9, spare row without P1.14 and P1.30. Rows checked: before 47, after 45.
- Final chain: `R3/final/run_all.log` ends `run_all exit 0`; ERC `R3/final/erc-report.txt` line 22 `** ERC messages: 0  Errors 0  Warnings 0`; `R3/final/check_netlist.log` last line `check_netlist exit 0`, line before `RESULT PASS netlist netlist.csv`.
- `check_footprints.py`: `R3/final/check_footprints.log` `RESULT PASS 110 parts, 19 footprints, 404 pins have pads, pad counts equal footprint-sources.csv, no PROVISIONAL`, `exit 0`.

## Step 2. Board (bars 1 and 3)

- TP8, TP9, TP11 on the route-f board, checked first: `R3/tp_copper_routef.log`: each pad `net ''`, copper layer B.Cu only, `copper items touching: 0` (tracks, vias and zone fill tested against the pad shape).
- My script (KiCad Python) `R3/rm_tp.py` took the route-f board (sha1 4376679f86a76961b3b2d293f9dada8e46bc05e1), deleted TP8, TP9, TP11 and saved it as pcb/ring.kicad_pcb: `R3/rm_tp2.log` `in:  footprints 100, vias 457, tracks 5551, zones 13`, `out: footprints 97, vias 457, tracks 5551, zones 13`. (A first try crashed in KiCad's Python after removing the footprints and saved nothing: `R3/rm_tp.log` `exit 1`.) Copper compared item by item: `R3/same_copper.log` `RESULT SAME COPPER` (6042 items each). Delivered board sha1 0c8c903d87d9b5270cd7b494ea30e0edc9641831 (`R3/final/board_sha.log`).
- Rules check as the project runs it, inside `pcb/`: `kicad-cli pcb drc --severity-all --all-track-errors -o drc-report.txt ring.kicad_pcb`: `R3/final/drc.log` `Found 0 violations`, `Found 0 unconnected items`, last line `drc exit 0`.
- `placement-final.csv` and `footprint-sources.csv`: TP8, TP9, TP11 rows removed (`R3/edit_tables.log`: 101 -> 98 and 114 -> 111 lines).
- `design/wiring/ring-board-plan.md` a.3, rows D6, E9, F4, F8, F9 as built (each line before and after in `R3/edit_plan_a3.log`): D6, E9, F8 "none"; F4 LCD_TE "through via L1-L4 in pad", escape "router joins the via: L4 toward (2.992, -0.025)"; F9 OLED_PWR_EN "blind via L1-L3 in pad", "router joins the via: L3 toward (5.100, 0.500)" (the router tracks at the vias: `R3/via_tracks.log`). Each row names the decision and the old escape.
- `check_escapes.py` reads that table (diff `R3/diff_check_escapes.txt`): (a) the span rule reads "through via L1-L4" and "blind via L1-L3"; on all 96 rows it parses only F4 and F9 differently (`R3/span_compare.log` `rows 96 differ 2`); (b) a row whose escape starts "router joins the via" needs no locked escape track (route-f's F4 and F9 have none); pad net, via span, one via and via net are still checked.

## Step 3. Board check (bar 4)

- `./run_kipy.sh check_board.py` in `pcb/`: `R3/final/check_board.log`: `checked: 97 parts (1), 362 pad nets (2), 3060 courtyard pairs (3), 362 pads and every courtyard, via and track for the outline and keep-outs (4), 97 table positions (5), escapes: RESULT PASS (6), rules check: 0 violations, 0 unconnected (7)`, `RESULT: PASS`, last line `check_board exit 0`.
- Broken copies on this board (`R3/run_broken.sh`, logs `R3/broken/check_<kind>.log`, summary `R3/broken/summary.log`), each `exit 1` with its own fault: net `FAIL 2 U1 pad A4 net 'GND' but netlist says 'VDD_1V8'`; outside `FAIL 4 C79 pad 1 centre outside the outline`; track (MIC_A_DATA In1.Cu 12.1 mm deleted) `FAIL 7 rules check: 2 violations {'via_dangling': 1, 'track_dangling': 1}, 1 unconnected items`; missing `FAIL 1 C5 has 0 footprints`; antvia `FAIL 4 via (GND) inside the antenna copper-free zone at (-11.000, 4.000)`; swap `FAIL 6 check_escapes.py exit 1: FAIL U1 B4: via ('L1', 'L3'), plan ('L1', 'L2')`.

## Step 4. Fabrication files (bar 5)

- `make_fab.sh` changed: one position file per face as well, and a drill report (diff `R3/diff_make_fab.txt`); `make_fab_docs.py`: the stack line counts the test pads from parts.csv (was "19 test pads"). Run 11:02:59 to 11:03:05 (`R3/fab_start.txt`, `R3/make_fab.done` `make_fab exit 0`), log `R3/make_fab.log` (folder size line `19M`). Files with sizes in bytes: `R3/fab_listing.log`.
- Gerber (`fab/gerber/`): `ring-F_Cu.gbr` 235631, `ring-In1_Cu.gbr` 238396, `ring-In2_Cu.gbr` 282494, `ring-B_Cu.gbr` 157469 (the 4 copper layers); `ring-F_Mask.gbr` 11699, `ring-B_Mask.gbr` 2240 (solder mask); `ring-F_Paste.gbr` 10677, `ring-B_Paste.gbr` 2235 (stencil); `ring-F_Silkscreen.gbr` 450, `ring-B_Silkscreen.gbr` 450 (print); `ring-Edge_Cuts.gbr` 977 (board outline); `ring-job.gbrjob` 3666 (job file).
- Drill (`fab/drill/`), one file per via span, all 0.100 mm: `ring-front-in1.drl` 2217 (L1-L2, 123 holes), `ring-front-in2.drl` 1397 (L1-L3, 69), `ring-in1-in2.drl` 1707 (L2-L3 buried, 86), `ring-in1-back.drl` 967 (L2-L4, 41), `ring-in2-back.drl` 1386 (L3-L4, 68), `ring-PTH.drl` 1405 (L1-L4, 70), `ring-NPTH.drl` 264 (no holes); each with a `-drl_map.pdf` map; `ring-drill-report.txt` 1907 (the counts). Total 457, equal to the board's via count (`R3/rm_tp2.log`).
- Position: `ring-pos-front.csv` 5024 (74 parts), `ring-pos-back.csv` 1433 (21 parts: J1, C1, C2, C5, C7, C14, R71, R72, FB1 and the 12 test pads), `ring-pos.csv` 6422 (95); C13 and C89 are not fitted and not listed (`R3/pos_vs_placement.log`).
- Others: `ring.ipc356` 91287 (net list for the bare-board test), `pdf/ring-<layer>.pdf` per copper layer with the outline, `ring.step` 18136644 (3D board), `ring-parts-list.csv` 15267 (97 lines, order codes), `stackup.txt` 2192 and `stackup.svg` 3219 (stack and order notes).
- For the maker: the 70 L1-L4 vias are KiCad "through" vias of 0.100 mm in `ring-PTH.drl`; the stack notes (`stackup.txt`, plan c.2) say every via is a laser microvia and L1-L4 is a stack of three. The maker must read the PTH file as stacks, not drill it.

## Step 5. Specification and architecture (bar 6)

- `design/architecture.md` section 7 (`R3/edit_architecture.log`, lines before and after, 942 lines kept): LCD_TE P1.14 F4 (D6 not connected), OLED_PWR_EN P1.30 F9 (E9 not connected), JOY_CENTER "not connected", DBG_RX "not connected", spare row without P1.14 and P1.30, naming P1.01, P1.19, P2.03, P3.05 and P1.02 as not connected.
- `design/firmware.md` lines 77 and 84 edited in place, no line added or removed (`R3/edit_firmware.log`, `R3/edit_firmware2.log`, `lines 1241 before and after 1241`; `R3/diff_firmware.txt` holds 2 changed lines). The dropped pins are named by ball (F8, D6, E9), because the firmware check fails a P-number that section 7 no longer lists (first try: `R3/firmware_check.log` `3 failures`). The other "D6" lines of firmware.md (85, 866, 1187) are the power chip's ball D6 and stay (`R3/firmware_grep_after.log`).
- `python3 design/firmware-check.py`: `R3/final/firmware_check.log` `0 failures`, last line `exit 0`.

## Step 6. Parts list (bar 7)

- `design/bom.csv` rows PCB1 and "Test pads" only (`R3/edit_bom.log`, `R3/edit_bom2.log`, `R3/diff_bom.txt`: 2 lines changed, 87 lines kept). PCB1: 4 copper layers, any-layer microvias, 0.30 mm, 12 test pads, parts on both faces. Test pad line: TP1, TP3, TP4, TP5, TP6, TP12, TP14, TP15 (quantity 8) and its text names all 12 pads of parts.csv (`R3/tp_parts.log`: TP1 TP3 TP4 TP5 TP6 TP12 TP14 TP15 TP17 TP18 TP19 TP21); TP17 to TP19 and TP21 keep their own lines, so no pad is counted twice. No row added.
- `python3 design/tools/check_bom.py`: `R3/final/check_bom.log` one FAIL, `FAIL designator RC1 is in netlist.csv or placement.csv and missing from the parts list`, last line `exit 1`; the same RC1 line as round 2 (`R2/a_check_bom.log`). Before my bom edit, with the new netlist: `R3/check_bom_before.log` also failed on TP8, TP9, TP11.

## Not proven about this board

- J1's mounting pads are not on ground: `R3/j1_pads.log` `pads with no net: ['3', 'MP', 'MP']` (pin 3 is no-connect in the netlist: `R3/j1_pin3_netlist.log` `,J1,3,MTP,no_connect`).
- Antenna line (`R3/line_report.log`, script `R2/line_report.py` on the delivered board): L1 closest other-net copper 0.169 mm (DECA), 53 items under 0.50 mm; L2 closest 0.034 mm (NRESET), 42 items under 0.50 mm. Plan d.1's 0.50 mm is not met. Routing notes: `design/ecad/ring-route-f/notes.md` `added In1 copper within 0.2 mm plan view of antenna copper 0 (closest 0.223)`; `design/ecad/ring-route-e/notes.md` `closest 0.515`.
- Crystal lines (`R3/line_report.log`): XL1 8.90 mm, nearest DECD and U1_VBUS 0.085 mm on In1.Cu; XL2 7.75 mm, nearest PMIC_SDA 0.090 mm on In1.Cu. Plan d.4 (0.20 mm) is not met. Earlier figure: `design/ecad/ring-route-e/notes.md` `XL2 closest other-net copper 0.082 mm (In1, PMIC_SDA)`.
- Under U1 D6 (no net now) a DECD In2.Cu track ends 0.070 mm from the land centre (`R3/via_tracks.log`); D6 has no via, so no contact; the rules check passes.
- `make_board.sh` does not rebuild this board: route-f was closed by hand steps; `route_fixed.py` was not changed for the new rows (not run).
- Plan a.3 rows B5, B9, G4, H4 and its "Count" line still read as before; the scripts treat B5, B9, G4, H4 as none (`NC_R2`). Rows outside my five were not edited.
- Not run: `check_band.py` (it rewrites 14 band report files). The broken copies of check_netlist and the A5 proofs were not rerun.
- I removed one temporary copy of each table I wrote in R3 while editing (`tmp_placement-final.csv`, `tmp_footprint-sources.csv`, same content as the delivered files).

questions_for_owner: none

RESULT: done, the route-f copper less three netless test pads is ring.kicad_pcb, the rules check prints Found 0 violations and Found 0 unconnected items, check_board.py prints RESULT: PASS, netlist, ERC, firmware and parts list follow the five pin changes, and the fabrication files are in pcb/fab/.
