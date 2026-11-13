# Ring main board (W2): notes

**State on 2026-11-13: this file is the record of round 1 (22 connections open at its end). The board is finished in `board-notes-r3.md`: routed, rules check 0 violations and 0 unconnected, parts on both faces, 12 test pads, fabrication files in `fab/`. Where this file and `board-notes-r3.md` differ, round 3 is right.** The ring's main board: 27.2 x 12.6 mm, 0.30 mm thick, 4 copper layers (any-layer laser microvias), 104 parts on the populated face and 19 test pads on the screen face, built from `../netlist.csv` and the footprint libraries `OpenRing.pretty` and `../../band/OpenRingBand.pretty`, placed by the plan's round 2 table and routed by script. It is not fully routed: 22 connections are open (point e). Written 2026-11-13. Evidence folder (logs, copies, pictures): `<work>/ring-board-evidence/`, named EV below.

## Rebuild with one command

`design/ecad/ring/pcb/make_board.sh` runs, in order: `build_board.py` (board, stack, outline, footprints, placement, rules, rule areas, ground zones), `route_fixed.py` (scripted copper, locked), `finish_route.py` (all other connections, grid maze router with rip-up, zones refilled), `kicad-cli pcb drc` (report `drc-report.txt`) and `check_board.py`. Logs go to `build-logs/`. The delivered `ring.kicad_pcb` is the output of the run of 02:52 to 03:34 (`EV/make_board_start2.txt`, `EV/make_board_run2.log`, its logs copied to `EV/final_run1/`), run with the `finish_route.py` now on disk. One run takes about 42 minutes. `board-top.png`, `board-top.svg`, `board-bottom.png`, `board-bottom.svg`, `placement-report.csv` and `provisional-footprints.json` in this folder belong to the old 6-layer board of 10 Nov and describe nothing on this board; the pictures of this board are in `pictures/`.

## a. Circuit changes (plan h.1, the part in design/ecad/ring)

- `make_netlist.py`: U1 balls E5, E6, E8 no-connect; TP7, TP10, TP20 removed (other test pads keep their numbers); ANT1 pins 2 and 3 on the new net ANT_TRIM with LT1 pin 1 (LT1 0201, 0 ohm, fitted; pin 2 GND); C89 0201, not fitted, on ANT3_NODE (pin 2 GND); LT1 and C89 in the additions list; TP7, TP10 in the not-placed list (they are in the frozen bom snapshot). Result 117 parts, 91 nets, 411 pin rows (`EV/a_make_netlist2.log`, last line `exit 0`).
- `run_all.sh w2b`: `EV/a_run_all2.log` last line `run_all exit 0`; ERC: `** ERC messages: 0  Errors 0  Warnings 0` (`EV/a_erc_counts.txt`).
- `check_netlist.py`: `EV/a_check_netlist.log`, line `RESULT PASS netlist netlist.csv`. Expected-value edits, each forced by the change: (1) in the section 7 loop, `W2_OPEN = {E5: SPARE_P1_19, E6: MIC_B_CLK, E8: SPARE_P1_01}`: these rows must show the ball no-connect and the net absent (before: the net on a test pad), and MIC_B_CLK leaves `A5_SPARE`; (2) check A5-2: E6 must be no-connect and MIC_B_CLK absent (before: E6 on MIC_B_CLK with TP20).
- `check_footprints.py`: `EV/b_check_footprints.log`, `RESULT PASS 117 parts, 19 footprints, 411 pins have pads, pad counts equal footprint-sources.csv, no PROVISIONAL`.
- `design/ecad/band/check_band.py` (`run_kipy.sh -I`): `EV/a_check_band.log`, `RESULT: PASS boards checked 14`.
- `design/bom.csv`: LT1 and C89 lines added (LT1 without order code: no saved maker document shows a 0201 0 ohm code, lead decision 127, 128); TP7, TP10 leave the TP1 to TP15 line (13 pads), TP20 leaves the TP20 to TP22 line (2 pads). `tools/check_bom.py`: `EV/a_check_bom.log`, last line `... failures 0`, then `exit 0`. `design/bom-notes.md`: section "W2 ring main board".

## b. Board file (build_board.py)

- 4 copper layers F.Cu (L1), In1.Cu (L2), In2.Cu (L3), B.Cu (L4); stack of plan c.2 in the board setup: copper 0.018 each, dielectrics 0.065 (106 prepreg, core, 106 prepreg), masks 0.0165, board 0.30, finish ENEPIG.
- Outline 27.2 x 12.6, corners r 0.8, no notch.
- 104 footprints loaded unchanged from the two libraries (none drawn); the 19 test pads on B.Cu (plan R2.5).
- Placement: the plan's round 2 table as it stood at 01:12, copied to `placement-plan-r2.csv` here (the plan's file changed again at 02:41, see Not closed). Corrections, each printed with its reason in `EV/final_run1/1_build_board.log`: rotation 180 for L2, L3, L4 (pin 1 toward the chip side of the antenna line) and X1 (the two L3 crystal lines would cross); C4, FB1, C1, R71, C2 turned so that the pad on a ball's escape line is that ball's net; R1 0.25 mm west (room for the VBAT stack of tail B); C86 and C87 change places; C10 turned 90 and moved to (5.60, 1.94).
- Rules of c.5 in `ring.kicad_pro` (track 0.065, gap 0.065, via 0.20 / 0.10, ring 0.05, hole to hole 0.20, hole clearance 0.075, copper to edge 0.10; classes Default 0.100 / 0.075, RF 0.120, USB 0.100, PWR 0.150) and `ring.kicad_dru` (RF line 0.20 to other copper and USB pair 0.20 to other tracks and vias, outside their chip exit areas; PWR 0.10 track gap; antenna zone: only the antenna's own tracks).
- Rule areas (9): antenna copper-free zone of round 2 (X -13.60 to -8.75, Y 3.10 to 6.30, less X -9.20 to -8.75, Y 3.10 to 3.30; no via, no zone fill); tail keep-outs A and B (no via); router edge band 0.15 (4 strips); RF_CHIP_EXIT and USB_CHIP_EXIT (scope only). Ground zones on all 4 layers.
- J1 courtyard (`make_footprints.py`, `OpenRing.pretty`): closed housing 6.1 along the row (catalogue p3, A) by 3.35 (catalogue p3, top view), widened to the outer land edges 3.6 (catalogue p4, B), because the lands stand 0.125 beyond 3.35 on each side: 6.1 x 3.6 (`EV/b_j1_footprint.diff`).

## c. Scripted copper (route_fixed.py, every piece locked)

- U1 and U2 escapes read from the plan's tables a.3 and b.2 (layer, via, direction); an escape stops 0.075 mm before a placed part's pad of another net: 12 do (`EV/final_run1/2_route_fixed.log`, lines `ESCAPE ... stopped`).
- Antenna line 0.120 on L1 along the round 2 path with L2, L3, C3, C12, L4, C13, C89, stubs, LT1 and its ground stack, ANT1 pin 4 stack, shunt ground stacks, 16 stitching stacks of 28 sites; line legs 16.12 mm.
- USB pair 0.100 / 0.075 from H6, H7 to U9 pins 1, 2 and tail B lands 5, 6, with two length bumps on D-: D- 14.075, D+ 14.075 mm.
- Crystal lines XC1, XC2 on L3 into X1 (stacked vias in the pads): 4.926 and 4.956 mm. XL1, XL2: only their escapes are scripted.
- SW1, SW2 to the coils, PVDD to C74, PVSS1 and PVSS2 stacks, tail exits with stacks outside the keep-outs (VBAT, VBUS, VMOT, NTC, GND, joystick lines), ground stacks at 37 ground pads.
- Count: `scripted segments 162 vias by span {'L1-L2': 27, 'L1-L3': 28, 'L1-L4': 69, 'L2-L3': 2} locked items 288`.
- `check_escapes.py` (ball, layer, via span, net, direction, against tables a.3 and b.2): `EV/g/check_escapes_fixed4.log` `RESULT PASS` (96 balls); a copy with U1 B4 and D5 swapped: `EV/g/check_escapes_broken_swap.log` `RESULT FAIL 2`. On the delivered board it runs inside check_board.py (check 6: `RESULT PASS`).

## d. Placement

- 104 parts at the table positions within 0.05 mm, except the 4 declared moves above; 0 courtyard overlaps except the pair U5 and U3 that the plan declares (R2.3); every pad inside the outline; every courtyard inside it (ANT1, U5, U6 allowed past by 0.10 / 0.20 / 0.20, R2.5); no courtyard of another part in the antenna zone or a tail keep-out; no via in them. Proof: `check_board.py`, checks 1 to 6 pass on the delivered board (`EV/final2/5_check_board.log`: `checked: 104 parts (1), 369 pad nets (2), 3741 courtyard pairs (3), 369 pads ... (4), 104 table positions (5), escapes: RESULT PASS (6), rules check: 13 violations, 22 unconnected (7)`).

## e. Routing

- Freerouting 2.5.0 (plan steps g.6 to g.8) on the build server in my own folder, DSN prepared by `fix_dsn.py` (six via spans, GND, RF and USB left out, wire keep-out on the antenna zone). Best result of each run (Freerouting's own count, `EV/route/runs_summary.log`): r1 one pass 150 unrouted; r2 30-pass limit, 22 passes done, best 121; r2w (PWR 0.100) stopped by me, best 148; r3 (via in pad allowed) stopped by me, best 132; r4 (final scripted copper) 18 passes, best 121. r1 imported into KiCad: 74 unconnected items (`EV/route/drc_r1.log`).
- Because the router's leftovers sit at U1 and U2, I wrote `finish_route.py`: a grid maze router (0.025 mm grid, 4 layers, the board's own gaps plus a 0.02 mm grid margin, pin-access cost, rip-up of nearby routes). Finishing Freerouting's r1 with it left 29 unconnected items and 8 clearance errors (`EV/fin/finish_r1b.log`); routing the scripted board with it alone left 20 (`EV/fin/finish_m9.log`), so the rebuild uses it alone.
- Delivered board, `kicad-cli pcb drc --severity-all --all-track-errors`: `EV/final2/4_drc.log`, `Found 13 violations` and `Found 22 unconnected items`. The 13 violations: 12 track_dangling and 1 via_dangling (`EV/final2/drc-report.txt`): locked escape ends of nets that stay open, and the scripted F2 via L2-L3.
- Counts (`EV/final2/stats.log`): 104 footprints, 91 nets, 2304 track segments (F.Cu 326, In1.Cu 851, In2.Cu 850, B.Cu 277), 457 vias (F.Cu-B.Cu 75, F.Cu-In1.Cu 125, F.Cu-In2.Cu 73, In1.Cu-B.Cu 24, In1.Cu-In2.Cu 86, In2.Cu-B.Cu 74), 288 locked items, 4 ground zones, 9 rule areas.

## f. Open connections on 4 layers (no layer added, thickness unchanged)

22 unconnected items (`EV/final2/open_nets.txt`), each with its two ends (model mm):
- VDD_1V8 (7): U10 pad 16 (-6.45, -4.00) to U10 pad 15 (-6.45, -4.40); L3 track (-4.35, -3.88) to TP17 (-7.10, 0.00); C5 pad 1 (1.05, -2.22) to U10 pad 5 (-4.05, -4.00); A4 escape (3.35, -0.98) to E10 escape (5.30, -0.00); C2 pad 1 (6.67, 0.38) to C1 pad 1 (6.01, 0.06); U2 E4 escape (7.62, 0.00) to L2 track (8.94, 0.00); L2 track (8.94, 0.84) to L2 track (13.05, 0.45). Cause found: `finish_route.py` stops a net after 12 joins and VDD_1V8 has more groups; with 80 joins the run of 03:35 routed it but left 16 other nets open after its first rip-up round, which took 27 minutes, with two rounds still to go at 04:15 (`EV/final_run2_stopped/3_finish_route.log`); I stopped it there and kept this board, and `finish_route.py` is back to the version that made it.
- GND (2): two pieces of the ground zones at (-13.60, -6.30) not joined (F.Cu to In1.Cu, F.Cu to F.Cu).
- DCC: A5 escape (3.67, -0.98) to L1 pad 1 (1.00, -3.64). TXRTUNE: R2 pad 1 (2.00, 1.53) to G6 escape (4.00, 0.65). SWIRE: J1 pad 6 (-10.17, 0.45) to U4 C3 (4.25, -3.65). XL1: B6 escape (4.00, -0.65) to X2 pad 1 (5.28, 3.35). XL2: B7 escape (4.32, -0.65) to X2 pad 2 (6.72, 3.35). SD_SCK: A9 escape (4.97, -0.98) to U10 pad 1 (-5.85, -3.85). SD_MISO: U10 pad 4 (-4.65, -3.80) to D10 escape (5.30, -0.33). LCD_MOSI: G8 escape (4.65, 0.65) to J1 pad 12 (-10.17, -1.35). VDD_USB_3V3: H8 escape (4.65, 0.97) to C10 pad 1 (5.60, 2.22). DBG_RX: TP2 (-5.00, 0.00) to B5 escape (3.67, -0.65). SPARE_P2_03: TP13 (-2.90, 0.00) to B9 escape (4.97, -0.65). SPARE_P3_05: G5 escape (3.35, 0.65) to TP16 (-6.05, -2.10). JOY_CENTER: TP22 (-3.95, 2.10) to H4 escape (3.35, 0.97).
- Congestion: the open ends sit at U1 (squares X 2.4 to 6.4, Y -2.3 to 1.7 hold 15 of the 44 ends) and in the corridor from U1 west under U3 to the test pads and U10. Pictures per copper layer: `pictures/ring-F.Cu.svg`, `ring-In1.Cu.svg`, `ring-In2.Cu.svg`, `ring-B.Cu.svg` (kicad-cli).
- Three changes that stay on 4 layers, each with its cost:
  1. Drop the test pads of four lines with no function on the board: SPARE_P2_03 (TP13), SPARE_P3_05 (TP16), JOY_CENTER (TP22), DBG_RX (TP2). Four of the 13 open nets other than VDD_1V8 and GND go, all long runs from U1 to the screen face under U3. Cost: no probe on those pins (DBG_RX: the debug serial receive line; SWD stays), netlist, parts list and test fixture change, as plan a.2 did for E5, E6, E8.
  2. Put X2 (32.768 kHz crystal) beside U1's B6, B7 balls on the row A side, as Nordic's layout does: XL1 and XL2 then need about 2 mm instead of a run around U1. Cost: about 2.0 x 1.4 mm in zone Z1 (C6, FB1, C7 move), the model's row X2 changes, plan d.4 lengths change.
  3. Bring U10 to zone Z15 next to U1's SD balls (plan f.1) and take two of R57, R58, R71, R72, C2, C14 out of the 1.5 mm strip between U1 and U2: SD_SCK, SD_MISO, DCC, TXRTUNE, VDD_USB_3V3 and the VDD_1V8 links at the chip are runs blocked there. Cost: a placement round (R2.3 found no room for U10 in Z15 while C60, C61, C24 and the RF corridor hold it).

## g. check_board.py

- Delivered board: `run_kipy.sh check_board.py` exits 1 because check 7 fails (`EV/final2/5_check_board.log`, last line `exit 1`, the line before `RESULT: FAIL, 1 problems`); checks 1 to 6 pass.
- Five broken copies (`make_broken.py`, `EV/g/broken2/`), each exits 1 and names its fault: net (`FAIL 2 U1 pad A4 net 'GND' but netlist says 'VDD_1V8'`), outside (`FAIL 4 C79 pad 1 centre outside the outline`), track (LCD_TE 6.825 mm on In2.Cu deleted: `FAIL 7 ... 23 unconnected items`, one more than the board), missing (`FAIL 1 C5 has 0 footprints`), antenna via (`FAIL 4 via (GND) inside the antenna copper-free zone at (-11.000, 4.000)`); each log ends `exit 1`.

## h. Fabrication files

Not made: the board is not fully routed (point e). `make_fab.sh` and `make_fab_docs.py` (Gerber per layer, drill per layer pair, IPC-D-356, position file, parts list with order codes, PDF per copper layer, stack drawing with the order notes of c.2, STEP) are written and were not run; `fab/` does not exist.

## i. What a built unit must still show

The plan's list h.2 and R2.7 (antenna match, radio corner, thickness, impedance coupons, microphone decoupling, prepreg dielectric constant, both crystals, USB high speed, buck ripple, stacked via reliability, screen supply ripple, test pad contact). Added by this board: L4 carries 277 track segments (`EV/final2/stats.log`), so the ground plane is cut: the antenna return loss and the USB eye are measured with it; 290 of the 308 PWR track segments are 0.100 mm, under the d.5 widths: the drop on VBAT, VSYS, VDD_1V8 and VDD_3V0 at full load is measured.

## Not closed

- 22 unconnected items and 13 dangling items (points e, f). Tried: 4 Freerouting runs (r1 to r4), via in pad, a PWR-width variant, my maze router with pin-access costs and rip-up (runs m4 to m9, one full rebuild and one stopped), 10 rotation and 4 position corrections.
- The plan's placement table changed at 02:41 (a further round: U4, L10, X2 and 48 rows moved, C21, C25, C26, C27 to 0402). Not applied: the board was placed, scripted and routed on the round 2 table; the change needs make_netlist.py, parts.csv and bom.csv edits for the four parts and a new 42-minute run.
- USB 0.20 gap to other copper is kept to tracks and vias, not to pads (pads at 0.075); d.5 power widths not met (point i).
- Plan faults (sent to the lead in one message): antenna land at the rounded corner (fixed by R2.0), J_BAND courtyards (fixed in the band library), keep-out Y 2.90 against 3.10, e.4 match-part courtyards, duplicated LT1/C89 rows. Found later: f.3 tail A exits follow land numbers that differ from the band library (exits made by the library); d.2 flow-through over U9 is impossible (pins 9, 10 have no net); C12's stub must leave the line at its corner.

## Changes other files need

- `design/mech/thin/placement.csv`: the round 2 rows of plan R2.6 and X1 rotated 180.
- `design/bom.csv` row PCB1: "6 layer micro-via" and "22 test pads TP1 to TP22" become 4 layers any-layer HDI, 0.30 mm, 19 test pads.
- `design/ecad/band/band-interface.md` section 2 against `J_BAND_A_BOARD.kicad_mod`: lands 1, 4, 6, 8 differ (plan R2.6).
- `design/architecture.md` lines of plan h.1 (keep-out, antenna, 4 layers) and the firmware board definition (MIC_B_CLK on E6 is gone).

RESULT: blocked, the 4-layer 0.30 mm board is placed and routed but its rules check reports 13 violations (dangling) and 22 unconnected items, so no fabrication files were made.
