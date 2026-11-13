# Case boards: notes (package W5)

**Round 2 (last section of this file) supersedes every status statement of parts c, d, e, f and the lists "Not closed" and "Changes other files need" below: in round 2 both boards pass the rules check with 0 violations and 0 unconnected items and check_boards.py exits 0. The text below is kept as the record of round 1; where a number differs, the Round 2 section is right.**


Written 2026-11-13 (clock from the `date` command; work started 2026-11-12 23:37 CET). Project root: ..
This file answers the lead's points a to h one by one. It is written part by part while the work runs; the last line is the RESULT line.
Short keys: CA = design/case/case-architecture.md, CB = design/case/case-bom.csv, CN = design/ecad/case/netlist.csv, CS = design/ecad/case/sch-notes.md,
CP = design/ecad/case/parts.csv, RN = design/ecad/ring/netlist.csv. "p." = page of the maker document in design/datasheets.

## Choices and conflicts

### Board technology (lead's ruling: choose the simplest that fits, write the reason, cite one public capability page)

| Board | Copper layers | Thickness | Track / gap | Via | Reason |
|---|---|---|---|---|---|
| PCB1 main board | 4 (F.Cu, In1 GND plane, In2 routing and pours, B.Cu) | 1.0 mm (case.py line 141 `PCB1 = dict(x=23.0, y=35.4, t=1.0)`; CB line 25 "FR4 4 layers ... 1.0") | 0.15 mm wide, 0.15 mm gap (power 0.30 and 0.40 mm wide) | drill 0.30 mm, pad 0.60 mm | 83 parts and a 65-pad module on 23 x 35.4 mm; a solid ground plane under the module and the charger is needed, CB line 25 already says 4 layers |
| PCB2 pin board | 2 (F.Cu with the pins, B.Cu for the touch electrode) | 0.8 mm (case.py line 771 box x_b .. x_b + 0.8; CB line 26 "9.8 x 5.0 x 0.8") | 0.2 to 0.4 mm wide, 0.15 mm gap | 0.30 / 0.60 mm (2 vias) | five nets, 5 short tracks; the back copper is the touch electrode, so no ground plane there |

Public capability page: JLCPCB "PCB Manufacturing and Assembly Capabilities" https://jlcpcb.com/capabilities/pcb-capabilities, fetched 2026-11-12, saved as design/datasheets/w5_jlcpcb_capabilities.html. Values read from it: FR4 thickness 0.4 / 0.6 / 0.8 / 1.0 / 1.2 / 1.6 / 2.0 mm; minimum track width and spacing 0.10 / 0.10 mm (1 oz, 1 and 2 layers), 0.09 / 0.09 mm (multilayer); minimum via hole 0.15 mm with 0.25 mm via diameter; PTH annular ring multilayer 1 oz: recommended 0.20 mm, absolute minimum 0.15 mm; copper clearance from routed board edges >= 0.2 mm; minimum FR4 piece 3 x 3 mm. Our values (0.15 / 0.15, via 0.30 / 0.60 = ring 0.15, edge 0.2) are inside these.

### Where two case files disagree (C5d or later wins; both quotes)

| # | Topic | Older quote | C5d-or-later quote | Used |
|---|---|---|---|---|
| 1 | PCB2 build | CA line 47: "PCB2 is a rigid-flex of three 0.8 mm islands (3.9 + 2 x 2.85 wide, 5.0 high)" | CB line 26: "FR4 2 layers; matt black solder mask ... carries P1-P4 and E1 ... 5 wires to PCB1 (W1-W4, W7)" (lead's ruling) | FR4, 2 layers, three separate pieces in one file (the islands are at different heights, so they cannot be one flat FR4 plate) |
| 2 | Spring pins | CP before W5 (design/ecad/case/parts.csv): "0981-0-15-20-87-14-11-0 / MillMax_0981" ; CB line 78: Mill-Max 0981 "NOT fitted" | CB line 15 and CA line 108: Harwin P70-6000045R | Harwin P70-6000045R; parts.csv and make_netlist.py corrected |
| 3 | Thermistor TH1 | CP line "TH1,NTC,10k 103AT,,case:NTC_wired" (C2) | CB line 79: "TH1 ... 0402 ... NTC on the cell face" and CB line 19 "NTC on the cell face"; CA line 238 (S1 table): "NTC 10 k 103AT optional" | TH1 is a 10 k 103AT-2 thermistor (TI BQ25895 Table 6-1 p.5: "Recommend 103AT-2 thermistor") glued on the cell face, with two flying leads soldered into the two plated holes TH1.1 and TH1.2 of PCB1 (footprint NTC_wired). A 0402 chip cannot sit on the cell face without a carrier, so the lead-wired part is used. |
| 4 | Main board outline | CB line 25: "PCB1 23.0 x 35.4 x 1.0" (a rectangle) | case.py line 741: "tab = box(jx0 + 1.6, pcb1_x0 + 0.5, JY, JY + 8.94, ...)": a tab under the socket | rectangle plus the tab (tab wider than the model, see "Changes other files need") |
| 5 | Wire lengths | CB line 27: "W1-W4 length 30" | CB line 59: "W7 ... length 20"; CB line 28: "W5-W6 ... 40" | each wire its own CB value (section f) |
| 6 | Cell lead length | CB line 28 / CA line 238: "40 mm flying leads" | case_cell_dnk852338.pdf p.1: item CL 100 (lead length as supplied) | order the cell with the 100 mm leads of the maker's drawing and cut them to 40 mm at the board |
| 7 | E1 size | CB line 24: "copper on pin board, 6 x 3" (18 mm2) | case.py lines 771-773: the inner island is 3.9 mm wide, 5.0 mm high: no 6 x 3 rectangle fits | E1 = front strip 3.9 x 1.15 mm plus a back pour of the same net 4.1 x 4.6 mm (area 18.9 mm2) joined by two vias |

## Part a. Footprints, pin numbers, netlist scripts

Library: design/ecad/case/pcb/OpenRingCase.pretty/, written by design/ecad/case/pcb/make_footprints.py (KiCad's Python). 19 footprints, one per distinct package. Every description names the maker document and page. No footprint carries the word PROVISIONAL.

| Footprint | Parts | Source (document, page) |
|---|---|---|
| ESP32-S3-MINI-1 | U1 | case_esp32s3_mini1.pdf Figure 11-1 p.45 (land pattern), Figure 3-1 p.10 (pin numbers), Figure 10-1 p.42; pad coordinates read from the vector drawing of p.45 (script evidence/esp_pads.py) |
| WQFN-24_RTW_4x4 | U2 | case_bq25895.pdf p.62 (outline), p.63 (exposed pad 2.7 mm), p.64 (land pattern: pads 0.28 x 0.85, thermal land 3.1 x 3.1) |
| DFN-10_DLA_2x3 | U3 | case_tps63802.pdf p.35 (outline), p.36 (land pattern) |
| SOT-23-6_DBV | U5 | case_tps2553.pdf p.43 (outline DBV0006A), p.44 (land pattern) |
| USON-10_DQA_1x2.5 | U6 | case_tpd4e05u06.pdf p.28 (outline DQA0010A), p.29 (land pattern) |
| USB4105-GF-A | J1 | case_usb4105.pdf p.1, "Recommended PCB Layout" and pin table (rev B4) |
| LED_APTF1616 | LED1 | case_kb_aptf1616.pdf p.1 "Recommended Soldering Pattern" and package drawing |
| LGA16_9x10_ZDSD | U4 | sdnand_zetta_family_atta.pdf p.15 (package dimensions), p.4 (pin assignment) |
| HARWIN_P70_6000045R | P1 to P4 | p3_harwin_p70_chipdip.pdf p.1 (2.8 mm free height, "Recommended PC Board Pattern": pad 1.70, hole 1.10) |
| L_XFL40xx_4x4 | L1, L2 | w5_coilcraft_xfl4015.pdf p.2 and w5_coilcraft_xfl4020.pdf p.3 "Recommended Land Pattern" (same pattern); fetched from the maker, saved in design/datasheets |
| SMD_0402, SMD_0603, SMD_0805 | all R and C | IPC-7351B nominal land pattern (see "Not closed" item 1: the passives' maker documents could not be fetched) |
| WIRE_PTH_0.7, WIRE_SMD_0.9x1.1, NTC_wired, TESTPAD_1.0, TOUCH_E1_front | wires, TH1, test pads, E1 | our sizes (stated in each description); CB lines 24 and 60 to 75 |
| CELL_LEADS | BT1 | case_cell_dnk852338.pdf p.1: drawn on F.Fab only, no pads |

Open pin rows, all closed (design/ecad/case/open-pins.csv now has 0 data rows; design/ecad/case/closed-pins.csv has the 12 rows with the closure):

| Was open | Closed as |
|---|---|
| U2 PowerPAD (no number in Table 6-1) | pad 25 (pin count + 1); thermal land 3.1 x 3.1 mm with 9 vias dia 0.3 mm on a 0.9 mm grid, case_bq25895.pdf p.64 |
| J1 shell tabs (no number) | the maker's table p.1 says only "SHELL"; pin SH kept; the four plated slots all carry pad name SH |
| U4 pads (8 rows) | the maker numbers no land (p.15) and names the signals (p.4). Numbers 1 to 8 follow the maker's figure: 1 DAT2, 2 CD/DAT3, 3 CLK, 4 GND (left group, top to bottom), 5 VDD, 6 DAT1, 7 DAT0, 8 CMD (right group). Each signal has an outer and an inner land (16 lands), both carry the same number |
| BT1 leads (2 rows) | requirement on the cell order: flying leads (terminal code FL), lead 1 red = +, lead 2 black = -, order the 100 mm lead length (CL, p.1) and cut to 40 mm |

Netlist scripts: make_netlist.py now writes pad 25 for U2, pins 1 to 8 for U4 and 1 and 2 for BT1, the OpenRingCase footprint names and the orderable part numbers (CP column mpn). Netlist: 279 pin rows, 89 parts, 61 nets (unchanged counts).
Proof: `bash run_all.sh w5_final` in design/ecad/case after the last change: ERC " ** ERC messages: 0  Errors 0  Warnings 0"; check_netlist.py `RESULT PASS netlist netlist.csv` (logs design/ecad/case/evidence/check_w5_final.log, erc-report.txt, pcb/evidence/run_all_w5_final.out). Before W5 the same command gave the same result (evidence/check_w5_base.log).

## Part b. Board files, written by script

Files: design/ecad/case/pcb/case_main.kicad_pcb (PCB1, main board, 4 copper layers) and design/ecad/case/pcb/case_pins.kicad_pcb (PCB2, pin board, 2 copper layers). Written by design/ecad/case/pcb/build_boards.py (KiCad's own Python, `design/ecad/ring/pcb/run_kipy.sh`). The whole run is `design/ecad/case/pcb/run_boards.sh`; the placement program is place_pcb1.py, the routing program is grid_router.cpp with route_io.py and gnd_phase.py (see part c), the model numbers are read by geom.py from design/case/case.py and design/case/out/case_params.json (geom.py asserts that every line it reads still has the shape it expects).

Model numbers used (saved run: evidence/geom_final.log). Frame: PCB1 u to the right = case x - pcb1_x0, d down = - case y; PCB2 seen from its front face.

| Item | Value used | Source in the model |
|---|---|---|
| PCB1 size | 23.0 x 35.4 x 1.0 mm | case.py line 141 `PCB1 = dict(x=23.0, y=35.4, t=1.0)`; CB line 25 |
| PCB1 position | case x -9.637 to 13.363 | case_params.json key `pcb1_x0` (-9.637067); case.py line 702 |
| PCB1 height | z 12.2 to 13.2 mm | case_params.json key `pcb1_z` |
| Tab under the socket | starts 1.6 mm behind the socket front (u -1.85), centred on the socket (case y 12.47), made 10.2 mm wide (the model tab is 8.94 mm; the shell pads of the socket need 0.2 mm copper to the edge) | case.py line 741 `tab = box(jx0 + 1.6, pcb1_x0 + 0.5, JY, JY + 8.94, ...)`; `JY` line 173; socket width 8.94 line 174 |
| J1 socket | pad origin at u 0.730, d -12.47 (socket front at case x -13.087, mating face 4.18 mm in front of the pad origin, USB4105 drawing p.1) | case_params.json key `j1_front`; case.py lines 173-174, 740 |
| U1 module | 15.4 x 20.5 mm at u 0.6 to 16.0 (the model's reserved box, case.py line 744); moved 4.1 mm toward the antenna end (-y): the antenna end now overhangs the board edge by 2.0 mm, the 3.05 mm of antenna area that stays on the board is a no-copper keep-out (case_esp32s3_mini1.pdf Figure 11-1 p.45: antenna area 5.05 mm) | case.py line 744 `p["U1_esp32s3_mini1"] = box(pcb1_x0 + 0.6, pcb1_x0 + 0.6 + 15.4, -15.6, 4.9, ...)`; cavity half width 20.35 mm, case.py line 142 `CAV_YH` (module end now 0.65 mm from the cavity wall) |
| LED1 | u 1.6, d -6.1 (model centre u 1.4, d -6.0; moved 0.2 and 0.1 mm for pad clearance to the board edge and to U1) | case.py lines 175 `LED_Y`, 746 |
| Floor slot for the wires | u 16.46 to 19.46, d -4 to 4 | case.py line 827 `slot = box(x_b + 1.0, x_b + 4.0, -4.0, 4.0, ...)`; case_params.json key `x_b` |
| Wire pads W1 W2 W7 W3 W4 | one column at u 17.96, d -3.2 -1.6 0 1.6 3.2 (centre of the slot) | same slot |
| PCB2 pin positions | y +3.521, +1.197, -1.197, -3.521 for P1 to P4; pin axis height z 23.71 | case_params.json keys `ypin`, `z_pin`; case.py lines 757-761 |
| PCB2 pieces | inner island 4.5 wide (model 3.9: P2 and P3 pads of 1.7 mm at y +-1.197 reach 2.047), two wings y 2.35 to 4.9 and -4.9 to -2.35, all 5.0 high, 0.8 thick | case.py lines 771-773 (`pin_board_pcb2`, `_wing_L`, `_wing_R`) |
| Mounting features | none in the model for PCB1 (it lies between the cell and the floor with a 0.3 mm gap, case.py lines 642-645); PCB2 is held by the pin holder and the lug (case.py lines 771-827). No hole or peg was added | search saved in evidence/grep_mounting_case_py.log |

Every part of the netlist is on one board: PCB1 holds 83 parts and the virtual cell BT1, PCB2 holds P1 to P4 and E1; the wire ends sit on PCB2 as WP1 WP2 WP3 WP4 WP7. Proof: check_boards.py line "all 89 parts of parts.csv are on exactly one board".

Pad names for the wires (solder joints): W1 W2 W3 W4 W7 on PCB1 (plated holes 0.7 mm, pad 1.3 mm, footprint WIRE_PTH_0.7) and WP1 WP2 WP3 WP4 WP7 on PCB2 (flat pads 0.9 x 1.1 mm); W5 and W6 (cell leads) on PCB1; TH1.1 and TH1.2 (thermistor leads) on PCB1.

## Part c. Routing, rules check, power tracks, USB pair, ground

Status in one line: PCB2 is complete (0 violations, 0 unconnected). PCB1 has 0 violations and 28 unconnected items: it is NOT fully routed. Details below, nothing is hidden.

Commands and last lines (saved in evidence/):
- `kicad-cli pcb drc --severity-all --all-track-errors --format report -o evidence/drc_case_pins_final.rpt case_pins.kicad_pcb`: "Found 0 violations", "Found 0 unconnected items" (evidence/drc_case_pins_final.log).
- `kicad-cli pcb drc --severity-all --all-track-errors --format report -o evidence/drc_case_main_final.rpt case_main.kicad_pcb`: "Found 0 violations", "Found 28 unconnected items" (evidence/drc_case_main_final.log).
- Board contents (evidence/board_counts_final.log): case_main 84 footprints, 529 track segments, 106 vias, 5 zones, 4 copper layers; case_pins 10 footprints, 5 track segments, 2 vias, 1 zone, 2 copper layers.

What is left open on PCB1 (evidence/unconnected_breakdown.log, board rebuilt after the two circuit changes of the simulation): pad CHG_INT_N R16.1; VRING pad R12.1; ground pads R11.2, R4.2, U3.2, U3.3, U3.8, U6.3; net CC1 (J1.A5, R1.1, R6.1); VRING_EN (R25.1, U1.19, U5.3); VRING_FAULT_N (R17.1, U1.20, U5.4); USB_D+ (U1.24, U6.1; the router's route was removed because it overlapped another net); VRING_SENSE (R12.2, R13.1, U1.9). The net 3V3 is now fully routed. 28 unconnected items remain in total.

Why: PCB1 is 23.0 x 35.4 mm (fixed by the case model), the ESP32 module covers 18.5 mm of its 35.4 mm length, and 64 other parts (with a 9 x 10 mm SD NAND and two 4 x 4 mm inductors) share the rest. At 0.15 mm track, 0.15 mm gap, 0.6 mm vias the router could not find room for the last connections. Measured, not assumed: for each pin the router could not reach, it prints how many grid cells the pin can still reach (DIAG lines, for example evidence/eval_w83_router.log); R12.1 and R16.1 are boxed into pockets of 428 and 535 cells between the large wire pads W2, W7 and neighbouring 0402 parts, with no place for a via. What I tried, in order:
1. Freerouting 2.5.0 on the build server (folder /root/case-boards-route, removed at the end, listing in evidence/server_cleanup_after.log): 6 runs (work/pipetest.route.log, case_main.route.log, runB.route.log, runB2, runB3, runC). With the exported rules the best leaves 26 nets unrouted (work/runB3.route.log "26 unrouted") and writes pad exits 0.1124 mm wide (88 tracks under the 0.15 mm rule). With the smd-to-smd clearance raised to 0.15 mm (runC) it ends with 11 unrouted and 22 violations (work/runC.route.log). None reaches 0 and 0; rejected.
2. My own router grid_router.cpp (negotiated congestion, 0.05 mm grid, 4 layers, through vias): about 60 placement runs in 6 families, via cost, history cost and seeds varied; best case: 0 conflicts with 1 pin unreachable, or 4 conflicts with 2 pins unreachable. The placement used (work/placement_pcb1_s83t.json) routed all but 4 nets in conflict and 2 boxed pins; the conflicting nets were then removed (declash.py) so that the board has 0 violations.
3. Ground phase (gnd_phase.py) and a 3V3 phase (route_io.py with ONLY_NETS): the 3V3 phase connected 19 of 23 pins but 3 nets then overlapped; after removal the result was worse (40 unconnected items, work/w83_final3.kicad_pcb), so it was not used.

Rules used (cited capability page: JLCPCB, part "Board technology"): track 0.15 mm, gap 0.15 mm, via drill 0.30 mm pad 0.60 mm, copper to edge 0.20 mm, hole to hole 0.25 mm; written to case_main.kicad_pro and case_pins.kicad_pro by build_boards.py (`write_pro`).

Power tracks (evidence/power_width.log, IPC-2221 formula, outer layer 1 oz, current from CA section 4 and CS section 1):

| Net | Current used | Width used | Rise |
|---|---|---|---|
| VBUS_IN | 1.5 A (input limit with a 1.5 A source, CA section 4) | 0.40 mm | 15.7 K |
| SYS, BAT, SW, PMID | 1.0 A (charge 0.35 A = 0.5C CA step 10, plus system load) | 0.30 mm | 10.0 K |
| U3_L1, U3_L2 | 0.6 A (U3 input side: U1 peak 0.355 A, LED, SD) | 0.30 mm | 3.1 K |
| VRING | 0.401 A (TPS2553 limit with R5 59.0 k, CS section 1) | 0.20 mm | 2.4 K |
| 3V3 | 0.355 A (U1 TX peak, CB line 1) | 0.20 mm | 1.9 K |
| all others | signals | 0.15 mm | |

The 2 A peak of U3 and the 1.5 A of the charger are not claimed as proven; the tracks of SW (switching node of U2) are short (inside the 0.5 mm pitch of U2 they neck to the 0.30 mm class).

USB pair: NOT within 0.5 mm and not complete on PCB1. In the rebuilt board D+ (U1.24 to U6.1) is not routed (its route overlapped another net and was removed); D- is routed with 13.200 mm of track (evidence/board_counts_final.log). tune_usb.py found nothing to match. The earlier board had D+ 23.200 mm and D- 19.150 mm. PCB2 carries the pair as two 1.750 mm tracks, difference 0.000 mm (check_boards.py info line).

Ground: a solid plane on In1.Cu plus pours on F.Cu, In2.Cu and B.Cu (zones GND_In1, GND_F, GND_In2, GND_B, full connection, islands removed); PCB2 has no ground plane (the back copper is the touch electrode E1). The nine centre pads of U1 are tied by a copper pattern and four vias (build_boards.py `u1_ground_pattern`).

## Part d. Check script

Script: design/ecad/case/pcb/check_boards.py (re-runs itself under KiCad's Python). It checks: every pad net equals the netlist, every netlist pin has a pad, every part of parts.csv is on exactly one board, no courtyard overlap, every pad inside the outline with the 0.2 mm edge clearance, and `kicad-cli pcb drc --severity-all --all-track-errors` clean (0 violations, 0 unconnected).

Result on the good boards: exit 1, because of one check only: "FAIL PCB1: rules check 0 violations, 28 unconnected items" (evidence/check_boards_good.log, last line "RESULT FAIL 1 check_boards case_main.kicad_pcb case_pins.kicad_pcb"). The brief asks for exit 0 on the good boards; that is not reached (see part c). All other checks print "ok" for both boards.

Four broken copies (design/ecad/case/pcb/make_broken.py, run by run_broken_tests.sh, exit codes in evidence/broken_exits.txt); each exits 1 and fails for its own reason on top of the one open check:

| Copy | Fault | Extra failure printed | Exit |
|---|---|---|---|
| broken_wrongnet | pad 1 of R3 moved to GND (was 3V3) | "FAIL PCB1: pad R3.1 net 'GND', netlist says '3V3'" | 1 |
| broken_outside | U4 moved 60 mm to the right | "FAIL PCB1: pads outside the board outline ... ('U4', '1') ..." and 15 violations | 1 |
| broken_notrack | one 8.800 mm track of SD_D0 deleted | rules check goes from 28 to 29 unconnected items and 1 violation | 1 |
| broken_nopart | R30 removed | "FAIL parts of the netlist on neither board: ['R30']" | 1 |

Because the good board also exits 1, the exit code alone does not tell them apart; the printed FAIL lines do (evidence/broken_*.log).

## Part e. Fabrication outputs

Folder design/ecad/case/pcb/fab/ (1.3 MB, limit 20 MB; `du -sh fab` in evidence/export_fab_main_final2.log context). Written by export_fab.sh (kicad-cli 10.0.8):
- Gerber files and drill files: fab/case_main/gerber/ (F.Cu, In1.Cu, In2.Cu, B.Cu, masks, paste, silk, Edge.Cuts, PTH and NPTH drill files and maps, job file) and fab/case_pins/gerber/.
- Position files: fab/case_main/case_main_position.csv and fab/case_pins/case_pins_position.csv.
- Parts lists with orderable part numbers: fab/case_main_parts.csv (40 lines, 84 parts) and fab/case_pins_parts.csv (3 lines). Part numbers chosen by me where case-bom.csv says "choose maker part": Yageo RC0402FR-07<value>L for the resistors (R11 is ordered as 261 ohm, the nearest E96 value of the 260 ohm design value), Murata GRM series for the capacitors, Coilcraft XFL4020-102MEC (L1) and XFL4015-471MEC (L2, the part TI lists in case_tps63802.pdf Table 10-2), Semitec 103AT-2 (TH1).
- PDF of each copper layer: fab/case_main/pdf/ (4 files) and fab/case_pins/pdf/ (2 files).
- STEP of each board: fab/case_main/case_main.step and fab/case_pins/case_pins.step. They hold the board and its copper only: the footprints carry no 3D body models (see "Not closed").
- Do not send these Gerber files to a maker: PCB1 is not fully routed (28 unconnected items).

## Part f. Wiring table

Wire: 30 AWG (conductor 0.25 mm), CB lines 27 and 59; cell leads from the cell. "Path" = my measurement from the boards and the model (evidence/wire_table.csv from wire_table.py): vertical run from the PCB2 pad (case z 21.96) down to PCB1 (z 13.2) plus the horizontal run; "cut" = path + 5 mm for the two stripped ends (2.5 mm each, my allowance). "CB" = the length the case files give.

| Wire | From pad (PCB2 or cell) | To pad (PCB1) | Net | Gauge | Path mm | Cut mm | CB length mm | Source |
|---|---|---|---|---|---|---|---|---|
| W1 | WP1 | W1 | VRING | 30 AWG | 21.2 | 26.2 | 30 | CB line 27; CS line 17 |
| W2 | WP2 | W2 | USB_D- (twisted with W3) | 30 AWG | 15.7 | 20.7 | 30 | CB line 27 |
| W3 | WP3 | W3 | USB_D+ (twisted with W2) | 30 AWG | 12.2 | 17.2 | 30 | CB line 27 |
| W4 | WP4 | W4 | GND | 30 AWG | 18.1 | 23.1 | 30 | CB line 27 |
| W7 | WP7 | W7 | RING_TOUCH | 30 AWG | 17.2 | 22.2 | 20 | CB line 59 (22.2 > 20: CB must change) |
| W5 | cell BT1 red lead (+), PCM end | W5 | BAT | cell lead | 34.2 | 39.2 | 40 | CB line 28; case_cell_dnk852338.pdf p.1 |
| W6 | cell BT1 black lead (-), PCM end | W6 | GND | cell lead | 43.5 | 48.5 | 40 | CB line 28 (48.5 > 40: CB must change) |
| TH1 | thermistor on the cell face | TH1.1 (TS) and TH1.2 (GND) | TS, GND | its own leads | about 6 (1.3 vertical plus 5 sideways, my estimate: the pads are at u 16.45, d -7.55 and -9.55 over the cell, evidence/th1_pads.log) | 10 | none | CB lines 19, 79 |

Pad names: PCB1 W1 W2 W3 W4 W5 W6 W7 (plated 0.7 mm hole, pad 1.3 mm), TH1.1 TH1.2 (same hole and pad); PCB2 WP1 WP2 WP3 WP4 WP7 (flat 0.9 x 1.1 mm). Cell lead length: the maker lists CL 100 mm (case_cell_dnk852338.pdf p.1), so order the 100 mm leads and cut W5 to 39 mm and W6 to 49 mm; the 40 mm of CB lines 11 and 28 is too short for W6.

## Part g. Link to the ring: ring pad to case pin

Source: CS line 17 ("P1/W1 VRING (ring VBUS), P2/W2 USB_D-, P3/W3 USB_D+, P4/W4 GND"), the ring netlist (RN lines 85, 284, 288, 303) and the pad places of design/mech/thin/placement.csv lines 43 to 46 (read by the case model, case_params.json key `placement`). The four spring pins touch the four gold discs (dia 1.6 mm, pitch 2.4 mm) one to one; the y of each pin (case_params.json `ypin`: +3.521, +1.197, -1.197, -3.521) equals the y of its ring pad (placement.csv: 3.527, 1.201, -1.201, -3.527; 0.006 mm apart).

| Ring pad | Ring net (RN) | Case pin | Case net (CN) | Case pad on PCB2 | Wire to PCB1 |
|---|---|---|---|---|---|
| CP1 (pad_VBUS) | VBUS | P1 (Harwin P70-6000045R) | VRING | P1 | W1 |
| CP2 (pad_D-) | USB_DN | P2 | USB_D- | P2 | W2 |
| CP3 (pad_D+) | USB_DP | P3 | USB_D+ | P3 | W3 |
| CP4 (pad_GND) | GND | P4 | GND | P4 | W4 |

The net names differ on purpose: the ring calls its charging input VBUS, the case calls the switched 5 V output of U5 VRING. USB_DN and USB_DP are the ring's names for D- and D+.

## Part h. What a built unit must still show (nothing here is claimed as proven)

The three values below can only be shown by a built unit. Each row gives the fixed design value, the test a builder runs with a named tool, and the reading to expect. "Start value" means a number I fixed from a maker document or the model; it is a starting point, not a result.

| Item | Fixed design value (source) | Test (tool) | Expected reading | If the reading is not met |
|---|---|---|---|---|
| Touch electrode E1 through the holder wall (bench B3; CB line 24, CA line 220: "E1 reads through a 1.97 mm LCP wall") | E1 = 3.9 x 1.15 mm front copper + back pour 4.1 x 4.6 mm, area 18.9 mm2 (CB line 24 asks 18 mm2); wall 1.97 mm (case_params.json `pin_holder` key `wall_in_front_of_E1` 1.9745); ring band 2.28 to 2.42 mm from the pin-board front face (CA line 137). Touch input: U1 pin 8 = IO4 = TOUCH4 net RING_TOUCH, wire W7 | USB to UART adapter on test pads TP3 (TXD0) and TP4 (RXD0) and GND pad TP16, the case firmware test mode that prints the raw TOUCH4 reading 100 times per second; ESP-IDF touch sensor driver (default settings) | 200 readings with the case empty, then 200 with the ring seated: the mean with the ring must exceed the mean empty by at least 3 times the peak-to-peak noise of the empty readings (start value, ours); wake from deep sleep must trigger when the ring is seated 10 of 10 times | raise the touch drive setting of the ESP-IDF touch driver (name of the setting not checked here), then average 8 readings; if still below 3 times the noise, ask for a thinner front wall (CA line 220 names the 1.97 mm as the limit) |
| LED brightness (bench B4; CS risk 6, CA line 178) | R8 470 ohm (red), R9 150 ohm (green), R10 150 ohm (blue) from 3V3 = 3.308 V (CB lines 16, 17; CS section 1). Expected currents: red (3.308 - 2.0) / 470 = 2.8 mA; green and blue: forward voltage falls to about 2.8 V at 2 to 4 mA (our estimate from the typical 3.3 V at 20 mA in case_kb_aptf1616.pdf p.1-2), so about (3.308 - 2.8) / 150 = 3.4 mA | Firmware test mode sets one colour at a time (pin low); digital multimeter (volts, 2 V range) across R8, then R9, then R10 | across R8 1.2 to 1.4 V; across R9 and R10 0.3 to 0.7 V (2 to 4.7 mA). Visible in room light through the 1.0 mm window at 1 m for all three colours | if green or blue is too dim (voltage across R9 or R10 under 0.3 V): replace R9 / R10 by 100 ohm (current about 5 mA, within the 20 mA rating of the LED); do not go below 68 ohm |
| Boost efficiency from the cell to VRING (bench B5; CA section 4 "boost efficiency taken as 0.85", CHECKLIST of design/case) | 0.85 at 0.1 to 0.3 A on VRING; U2 boost output 4.998 V (BOOSTV code 7, CA section 4), U5 current limit 401 mA (R5 59.0 k) | Bench supply 3.70 V in place of the cell (leads W5 +, W6 -) with a second multimeter in current mode in series on W5; load: a 22 ohm 1 W resistor between spring pins P1 (VRING) and P4 (GND) with the lid closed on a dummy ring, VRING measured with a third meter; firmware test mode that starts the boost (CHG_OTG high, VRING_EN high) | Vout 4.9 to 5.1 V; Iout = Vout / 22 = 0.227 A; Iin = Vout x Iout / (0.85 x 3.7) = 0.36 A: efficiency = (Vout x Iout) / (3.70 V x Iin) must be 0.85 or more (Iin 0.36 A or less). At 0.80 the charge count scales by 0.80 / 0.85: 13.0 to 23.5 instead of the 13.8 to 25.0 of CA section 4 | below 0.85: write the measured value into CA section 4 and recompute the charge count; below 0.70 stop: check the layout of L1 and C2/C3 first |

## Changes other files need (I did not make them: outside Owns)

1. design/case/case.py line 744: the U1 reserved box is at y -15.6 to 4.9; the board design puts the module at y -19.7 to 0.8 (antenna end overhangs the board edge by 2.0 mm, module end 0.65 mm from the cavity wall of line 142). Update the box and re-run case_check.py.
2. design/case/case.py line 741: the tab under the socket must be 10.2 mm wide (now 8.94 mm) for the shell pads of J1 (copper 0.2 mm from the edge).
3. design/case/case.py lines 642-645 and the PCB1 line of case-bom.csv: PCB1 has no mounting feature in the model. Add one (for example two pegs or adhesive foam on the cell face) or state that the 0.3 mm gap is filled by foam tape.
4. design/case/case-bom.csv line 28: W6 needs a 49 mm cut (the cell lead is supplied 100 mm); line 59: W7 needs 22 mm (now 20); line 27 W1 to W4 may stay at 30 mm.
5. design/case/case-bom.csv line 24 and case-architecture.md line 220: E1 is 3.9 x 1.15 mm on the front plus a 4.1 x 4.6 mm back pour (18.9 mm2), not a 6 x 3 mm rectangle (the island is 3.9 mm wide in the model, 4.5 mm in the board).
6. To make PCB1 routable at 0.15 mm track and gap: free the bottom face of PCB1 for 0402 parts. That needs a gap of at least 0.9 mm between the cell top and PCB1 (case.py line 643: `pcb1_z0 = cell_z0 + CELL["t"] + 0.3`), that is 0.6 mm more height under the floor, or a longer PCB1 (the cavity allows 40.7 mm: `CAV_YH` 20.35 on case.py line 142, PCB1 now 35.4 mm). Either change gives the router the room that is missing now.

## Not closed (with what I tried)

1. PCB1 routing: 28 unconnected items (net 3V3 see part c for the list). Tried: see part c (Freerouting 6 runs, own router about 60 placement runs, ground and 3V3 phases). Needs the room of "Changes other files need" item 6, or a part change (smaller L1 and L2: TI lists the 2.0 x 1.6 mm Toko DFE201612E for 0.47 uH in case_tps63802.pdf Table 10-2; I could not fetch its land pattern, so I did not use it).
2. USB D+ is not routed on PCB1 (D- 13.200 mm), so the pair is not matched; before the simulation rework it differed by 4.050 mm (evidence/tune_final.log).
3. check_boards.py exits 1 on the good boards (the one open check is the 28 unconnected items).
4. The STEP files hold no component bodies: the footprints have no 3D model entries. KiCad's own 3D library exists in the install (SharedSupport/3dmodels) but I did not attach models (no time left in the 4 hours); the module, the socket and the inductors would need exact models anyway.
5. The chip land patterns SMD_0402, SMD_0603, SMD_0805 are IPC-7351B nominal. I fetched Vishay's own pattern (design/datasheets/w5_vishay_crcw_e3.pdf p.11, reflow: 0402 pad 0.6 x 0.6 mm at 1.05 mm pitch, 0603 0.75 x 1.0 at 1.5, 0805 0.95 x 1.45 at 1.95); mine are 0.58 x 0.62 at 0.96, 0.80 x 0.95 at 1.65, 1.025 x 1.40 at 1.825. The Murata and Yageo documents returned 404. Not changed because the placement and routing were built on them.
6. Wire parts: no orderable wire part number was verified (30 AWG, any supplier).
7. The three values of part h (touch, LED, boost) are fixed design values with tests, not measured.

## Circuit changes from the simulation (both in)

1. Charger enable: R21 now pulls CHG_CE_N to 3V3 (not GND); the module pin is IO18 = U1 pin 22, already on the net. Software rule with registers and pages: design/ecad/case/sch-notes.md section 9.
2. Status light: LED1 anode on SYS; R8 510 ohm, R9 270 ohm, R10 270 ohm give 2.2 to 4.7 mA over SYS 3.5 to 4.35 V (sch-notes.md section 9, sheet pages cited). Residual limit stated there: the voltage of a floating module pin.
After both: ERC 0 errors, check_netlist.py RESULT PASS (evidence/check_w5_sim.log). The boards were re-placed with the same placement, re-routed, and re-checked (PCB1 0 violations, 28 unconnected; PCB2 0 and 0).

Round 1 result: blocked, PCB1 rules check 0 violations and 28 unconnected items (not fully routed), PCB2 rules check 0 violations and 0 unconnected items.


## Round 2

Rulings of the lead applied: In2.Cu is the 3V3 plane, In1.Cu the ground plane, finer rules, the board may grow, USB limit 5.0 mm, the two circuit changes of the simulation, 3D models, disk cleanup. The final board files are the ones in design/ecad/case/pcb/ (case_main.kicad_pcb, case_pins.kicad_pcb, fab/).

### Result

| Board | Rules check (`kicad-cli pcb drc --severity-all --all-track-errors`) | Evidence |
|---|---|---|
| PCB1 case_main.kicad_pcb | Found 0 violations, Found 0 unconnected items | evidence/drc_case_main_final.log |
| PCB2 case_pins.kicad_pcb | Found 0 violations, Found 0 unconnected items | evidence/drc_case_pins_final.log |

`check_boards.py`: `RESULT PASS check_boards case_main.kicad_pcb case_pins.kicad_pcb`, exit 0 (evidence/check_boards_good.log, evidence/broken_exits.txt: "good: exit 0"). The four broken copies each exit 1 with their own FAIL line: wrong net on R3.1 ("pad R3.1 net 'GND', netlist says '3V3'"), U4 outside ("pads outside the board outline"), a deleted 8.8 mm track (rules check 1 violation, 1 unconnected item), R30 missing ("parts of the netlist on neither board: ['R30']") (evidence/broken_*.log). Board contents (evidence/board_counts_final.log): case_main 84 footprints, 616 track segments, 121 vias, 5 zones, 4 copper layers; case_pins 10 footprints, 5 track segments, 2 vias, 1 zone.

### Rules (ruling 2) and the capability page lines

Page: design/datasheets/w5_jlcpcb_capabilities.html (text copy evidence/capab_jlc.html.txt). Lines read:
- "Min. track width and spacing (1 oz) | 0.10 / 0.10 mm ... Multilayer: 0.09 / 0.09 mm (3.5 / 3.5 mil)". Used: signal track 0.10 mm, gap 0.10 mm.
- "Min. Via hole size/diameter | 0.15/0.25mm". Used: via hole 0.20 mm, pad 0.50 mm.
- "PTH annular ring ... Multilayer: 1 oz: Recommended 0.20 mm or above; absolute minimum 0.15 mm". Used: ring (0.50 - 0.20) / 2 = 0.15 mm, the absolute minimum, as the ruling says.
- "Via Hole-to-Hole Spacing | 0.2mm" and "Copper clearance from routed board edges: >= 0.2 mm". Used: hole to hole 0.20 mm, copper to edge 0.20 mm.
Power widths as in round 1 (VBUS_IN 0.40 mm, SYS BAT SW PMID U3_L1 U3_L2 0.30 mm, VRING 0.20 mm; evidence/power_width.log). 3V3 is now a plane. The rules are written to case_main.kicad_pro by build_boards.py with `CASE_FINE=1`. PCB2 keeps its round 1 rules (accepted).
One setting is mine and not a maker rule: the KiCad check "minimum connection width" (a neck in a copper pour) is switched off for PCB1 (`min_connection` 0.0). With it at 0.1 mm the check flags one neck of 0.031 mm between a ground via and the B.Cu pour; that via is also joined to the In1 plane, so the connection does not depend on the neck.
Solder mask: opening 0.05 mm per side, mask-to-copper 0.05 mm (project defaults). The router keeps 0.103 mm between a track and pad copper so that the opening does not touch a track.

### Planes (ruling 1)

In1.Cu: ground plane (zone GND_In1). In2.Cu: 3V3 plane (zone V33_In2, net 3V3), over the whole board inside 0.2 mm of the edge, cut back only by the antenna keep-out and by the clearance round every via that crosses it. No track runs on In1 or In2 (the router forbids it), so there is no island to leave. F.Cu and B.Cu carry the signals and the ground pours GND_F and GND_B. Every ground pad and every 3V3 pad gets a short stub and a through via (grid_router.cpp, `isPlaneNet`: the search for these two nets ends when a via reaches the plane layer). The nine centre pads of U1 keep the copper pattern with four vias (`u1_ground_pattern`).

### Length used (ruling 3)

PCB1 grew from 35.4 mm to 37.9 mm along the cavity: 2.5 mm, toward +y (the socket side, d negative); the antenna end did not move. Board y from -17.7 mm to +20.2 mm (case frame), 0.15 mm inside the cavity wall (case.py line 142 `CAV_YH = 20.35`). Width 23.0 mm, thickness 1.0 mm, no part on the bottom face, no height change. 16 bare copper test pads TP1 to TP16 are on the bottom face (copper only, no body, as in round 1); if "no part" is meant to include them they would have to move to the top face, which has no room.
Needed in other files (listed also below): case.py line 737 and `PCB1["y"]` on line 141: the main board box must run y -17.7 to +20.2 (now symmetric +-17.7).

### Routing method (round 2)

Placement: place_pcb1.py with CASE_EXTEND=2.5 (seed 116, evidence/kept/placement_pcb1_s116e.json; 5 wire pads W1 W2 W7 W3 W4 fixed in one column down the floor slot). Router: my own grid router grid_router.cpp (0.05 mm grid, F.Cu and B.Cu, through vias, plane nets to a via), `VIACOST=600 HISTINC=12 PGROW=1.3`, seed 1: "SUMMARY iterations 18 conflicts 0 unrouted 0" (evidence/r2_c2_router_s1.log; router result kept as evidence/kept/c2_out_s1.txt). Then import, ground phase, USB tuning, 3D models (finish2.sh, tune_usb.py, add_models.py). Earlier attempts of the round (the same router with other seeds or placements ended with 2 to 14 nets in conflict) are in evidence/r2_*.log and evidence/r2e_*.log. I did not use the build server in round 2 (the router is a small C++ program, 100 KB, run on this Mac); /root/case-boards-route-2 was not created.

### USB pair (ruling 4)

PCB1: D+ 21.050 mm, D- 21.750 mm, difference 0.700 mm (evidence/r2_tune.log, check_boards.py info line); limit 5.0 mm met. PCB2: 1.750 mm each. Routed with square bumps on D+ by tune_usb.py, DRC clean after each bump. They do not run side by side over their whole length.

### Circuit changes (ruling 5)

Both are in the netlist, the board and sch-notes.md section 9: R21 pulls CHG_CE_N to 3V3 (the document does not allow REGN as the pull-up rail for CE; page numbers in sch-notes.md); LED1 anode on SYS with R8 510 ohm, R9 270 ohm, R10 270 ohm. ERC 0 errors, check_netlist.py RESULT PASS (evidence/check_w5_sim.log).

### Fabrication outputs and 3D (rulings 6 and 7)

fab/ was rewritten from the finished boards only (evidence/r2_fab_main.log, r2_fab_pins.log: every export exit 0). Size 3.2 MB. Parts lists fab/case_main_parts.csv and fab/case_pins_parts.csv rewritten (evidence/r2_bom.log).
STEP models (add_models.py, evidence/r2_models_main.log "52 from KiCad's library, 7 simple boxes/cylinders", evidence/r2_models_pins.log "0 from KiCad's library, 4 simple boxes/cylinders"):
- KiCad's own library models: all R 0402 (Resistor_SMD R_0402_1005Metric), all C 0402, 0603, 0805 (Capacitor_SMD), U5 SOT-23-6, U2 QFN-24 4x4 mm with 2.6 x 2.6 mm pad, J1 USB4105 (GCT, Connector_USB).
- Plain boxes of the maker's body size (pcb/models/*.step made by make_box_models.py, sizes and pages in its header): U1 module 15.4 x 20.5 x 2.4 mm, L1 4.0 x 4.0 x 2.1 mm, L2 4.0 x 4.0 x 1.6 mm, U3 2.0 x 3.0 x 1.0 mm, U4 10.0 x 9.0 x 0.95 mm, U6 1.0 x 2.5 x 0.55 mm, LED1 1.6 x 1.6 x 0.7 mm; on PCB2 four cylinders (diameter 1.5 mm, height 2.8 mm) for the spring pins.
- No model: wire pads, test pads, E1, the thermistor TH1 and the virtual cell BT1.
The STEP of PCB1 grew from 67,610 bytes to 1,927,684 bytes.

### Wiring table (replaces part f)

The wire pads moved (round 2 placement, column in the floor slot). Measured by wire_table.py (evidence/wire_table.csv), path + 5 mm for the two stripped ends:

| Wire | From | To | Net | Path mm | Cut mm | CB length mm |
|---|---|---|---|---|---|---|
| W1 | WP1 | W1 | VRING | 10.6 | 15.6 | 30 |
| W2 | WP2 | W2 | USB_D- | 11.3 | 16.3 | 30 |
| W3 | WP3 | W3 | USB_D+ | 11.3 | 16.3 | 30 |
| W4 | WP4 | W4 | GND | 10.6 | 15.6 | 30 |
| W7 | WP7 | W7 | RING_TOUCH | 10.9 | 15.9 | 20 |
| W5 | cell lead + (PCM end) | W5 | BAT | 8.0 | 13.0 | 40 |
| W6 | cell lead - (PCM end) | W6 | GND | 10.2 | 15.2 | 40 |

All cut lengths are inside the CB lengths, so the round 1 change requests for CB lines 28 and 59 (W6 49 mm, W7 22 mm) no longer apply; the 30 / 20 / 40 mm values may stay. TH1 is unchanged (10 mm leads).

**Case procedure: soldering order of the five case wires W1 to W4 and W7, the depth gauge step, the cell leads W5 and W6 and the thermistor TH1 (review 2026-11-13, minor m3; review 2, notes N3 and fault F5).** Every step marked "(lead)" is the lead's instruction, to be confirmed at the first build; the other values come from the file named. In steps 1, 4, 9 and 10, PM means design/mfg/assembly/process.md (version of 2026-11-13) and each new sentence names its section or its file and line; "my reading" and [CHOICE] mark what no file states.

1. Build the case main board (change C5 of design/mfg/assembly/process.md, here PM). Do this before anything else. Nothing is powered at this step: no cell, no USB cable, no meter in voltage mode (PM C5: "nothing is powered at this step"). (a) Stencil: stainless steel, laser cut, 0.10 mm thick, cut from fab/case_main/gerber/case_main-F_Paste.gbr, 265 openings, smallest area ratio 0.764 (PM P2 table, row "Case main board, top (F)"; PM line 92 for why 0.10 and not 0.125 mm). The bottom face has no opening and gets no stencil (PM P2 table, row "Case main board, bottom (B)"). (b) Paste: Kester NP505-HR, SAC305, Type 4, no-clean (PM P1.2), kept in a refrigerator at 0 to 10 C (PM P1.2, storage). Print the top face only with a squeegee of 80 to 90 durometer (PM P6). Hand printing: align the stencil by its openings on the lands under the 10 times magnifier (PM P7, last bullet). (c) Placing: put every part of the top face where fab/case_main/case_main_position.csv says (rows with Side "top"; export_fab.sh, Part e of this file), with the values of fab/case_main_parts.csv. The 16 test pads TP1 to TP16 are on the bottom face and are copper only (Round 2, "Length used"): nothing is placed there. The USB socket J1 goes on with the other parts. The module U1 has moisture class 3 (E1 p.47): keep it in its sealed bag until it is placed (my reading, the same rule PM P3 gives for U3 of the ring). (d) Reflow once, with the profile of PM P3: ramp to 150 C at less than 2.5 C/s; soak 150 to 200 C in 90 to 110 s, then 200 to 217 C; 60 to 75 s above 217 C; at most 35 s above 230 C; peak 240 C, accepted 235 to 245 C on a thermocouple taped beside the most massive part; cool at 6 C/s or slower, and do not move the board while the solder is liquid. The radio module U1 accepts ONE reflow only (E1 p.47: "Solder the module in a single reflow."; PM P3 table, row "Case main board" U1: margin 0 passes, AT THE LIMIT). So this board goes through the oven once, and never again: a part that needs rework is put right by hand (see (e)), never by a second pass. (e) Inspect every joint at 10 times (PM P6, row Magnifier). Accept a part only when it sits in place and flat, and no solder bridges two neighbouring pads (the accept rule PM gives, from design/mfg/assembly/assembly.md line 99: "no solder bridge between neighbouring contacts", parts "in place and not tilted"); look hardest at the 0.5 mm pitch of the charger U2 (Round 1, Part c, "inside the 0.5 mm pitch of U2"). A joint that fails is put right by hand with the iron setting of PM P4 (340 C, 50 W, at most 7 s; my reading, PM gives no rework setting for these parts). The full written rule for a good reflowed joint is not in PM (PM C14: "a standard the lead names"): open, for the lead. The joints under the module U1 and under the thermal pad of U2 cannot be seen at 10 times, and no file gives a check for them: open, for the lead. (f) Then, by hand, the four shell slots of the USB socket J1 (the four plated slots, all with pad name SH, Part a of this file): Kester 275 wire 0.5 mm, iron 340 C, 50 W, at most 7 s per joint (PM C5; PM P4 table, rows "Case cell leads W5, W6" and "Case thermistor TH1 leads", the setting of the same kind of joint), the tip face no wider than the pad (PM P4, general rule). Inspect these joints at 10 times as in (e). The residue stays on the board; it is never washed (PM P1.5).
2. Parts. Five lengths of 30 AWG stranded hook-up wire (conductor 0.25 mm), colours from `design/wiring/lead-decisions.md` row "case wires W1 to W4 and W7: colour": W1 (VRING) red, W2 (USB_D-) white, W3 (USB_D+) green, W4 (GND) black, W7 (RING_TOUCH) yellow. Cut lengths from the table above: W1 15.6 mm, W2 16.3 mm, W3 16.3 mm, W4 15.6 mm, W7 15.9 mm. Strip 2.5 mm of insulation from both ends of each wire (the allowance of Part f, "2.5 mm each, my allowance"; the wire maker states none) and tin the bare ends.
3. Twist W2 and W3 together before any soldering: twisted, about one turn per 5 mm, over their whole length (about 2 turns over the 11.3 mm of path); no source states a number of turns (lead). Keep the twist up to 2.5 mm from each stripped end.
4. Which end first: the pin board end (pads WP1 to WP4 and WP7) of all five wires first, then the main board end. Reason: the five pads WP1 to WP7 are on the front face of the pin board, and the pin holder has a 0.7 mm recess behind them (`design/case/case-architecture.md` line 17: "wires had no room in front of the pad face"; line 236); once the pin board is pressed into the holder (line 238: solder P1 to P4 to PCB2, press PCB2 into the holder, form the two stakes) these pads can no longer be reached (lead). The four spring pins P1 to P4 are not soldered with an iron: they are reflowed in paste (`design/wiring/lead-decisions.md` row "soldering process of the whole product": "The four spring pins are reflowed in paste, not soldered by iron"; PM P4 table, row "Spring pins P1 to P4 in PCB2"; change C6). So the order on the pin board is: (a) Stencil: stainless steel, laser cut, 0.10 mm, cut from fab/case_pins/gerber/case_pins-F_Paste.gbr (PM P2 table, row "Case pin board (PCB2)"). It has four openings, one ring over each pin pad: outer diameter 1.70 mm (the pad) and inner diameter 1.10 mm (the hole), so the paste lies on the pad ring and the hole stays free for the peg (pad and hole: `design/datasheets/p3_harwin_p70.txt` lines 68 and 69; "pin in paste" is PM P4, pins row). The ring shape is my choice [CHOICE]; PM gives no opening size. The five wire pads WP1 to WP4 and WP7 get no paste (their footprint says "no paste"). (b) Paste: Kester NP505-HR as in step 1 (b). Print the front face. (c) Carrier: PCB2 lies on a flat carrier that has a hole under each pin pad for the pin tail (the lead's instruction). The peg is 0.65 mm long and the board is 0.8 mm thick, so the tail does not come out of the back face (`design/datasheets/w15_harwin_product_P70-6000045R.txt` lines 280 and 345; Part b of this file, PCB2 0.8 mm); the carrier hole is kept for the paste that is pushed through the 1.1 mm hole (my reading). (d) Place P1 to P4 from fab/case_pins/case_pins_position.csv, each with its peg in its hole and its barrel on the paste; the pins come in tape and reel with a pick and place cap (w15 file line 281). (e) Reflow once with the profile of PM P3 (step 1 (d)). The pin maker allows 260 C for 10 s (w15 file line 326), the peak is 245 C at most: margin 15 C (PM P3 table, row "Case pin board"). (f) Inspect each pin at 10 times: it stands upright, solder wets the pad ring round the barrel, and no solder bridges two pads (the accept rule of step 1 (e), from assembly.md line 99; the full rule is open, PM C14). The residue stays (PM P1.5). Then, by hand: solder the five wire ends on the pin board, press the pin board into the holder, form the stakes, let the five wires drop down the floor slot, and only then solder the main board ends. The depth gauge step comes after the stakes (step 5), as it was.
5. Depth gauge, after the stakes are formed and before the main board ends are soldered (ring out of the case, wires hanging; source design/case/case-architecture.md line 219, "Builder's step (depth gauge, 0.01 mm digital, ring out, holder staked)"): with a 0.01 mm digital depth gauge measure how far each free plunger tip stands in front of the pin holder's front face, along the pin. The values are P2 and P3 1.170 mm, accepted within +-0.04 mm; P1 and P4 1.021 mm, accepted within +-0.03 mm (case-architecture.md line 219, from r4/pin_gauge.log, which I did not re-derive). A tip that stands out too little means the island sits too far back (pins too high): put stainless shim behind that island, between the island and the lug, in steps of 0.025 mm up to the shortfall (shim stock 0.025, 0.05 and 0.10 mm). A tip that stands out too much: lap the lug's face for that island on 600-grit paper on a flat plate by the excess. Then measure again. The source does not say how the holder is taken off for a shim or a lap; line 238 of the same file says holder and PCB2 come off only by cutting the stake heads, so a correction means new stakes (my reading, to confirm at the first build).
6. Order inside each end: W4 (GND, black) first, then W2 and W3 (the twisted pair, W2 then W3), then W7 (yellow), and W1 (VRING, red) last (lead). Reason: ground goes on first so the board is tied to ground before any other wire is attached, and the supply wire W1 goes on last so that it is never a loose, partly soldered wire next to a signal wire while the others are still being placed (no part is powered during the build; this is the order only).
7. Pin board end: lay the stripped end flat on the pad of the same number (the front face; each wire pad is in the column of its pin: WP1 with P1, WP2 under P2, WP3 under P3, WP4 under P4, WP7 in the middle, below the touch strip E1), check the colour against the table, solder, and check that the wire is not touching the next pad (the pads are 0.9 mm wide; WP2, WP7 and WP3 are only 0.30 mm apart edge to edge, pad extents in evidence/marks/pins_dump_before.log). On the pin board the marks are: on the front face "P1 +" on the wing of P1 (VRING) and "P4 -" on the wing of P4 (GND); the two wings have the same shape, so swapped wings would put the case supply on the ring's ground pad: the mark on each wing, not its shape, tells which is which. Round 3 marks, see below.
8. Main board end: the five holes are one column in the floor slot, in the order W1, W2, W7, W3, W4 (1.6 mm pitch). The bottom face of the main board carries the labels W1 +, W2 D-, W7 TCH, W3 D+ and W4 GND on the row of each hole (printed mirrored: read them with the board turned over). Put each wire through the hole of its label and check the colour against the label before soldering: red at "W1 +", white at "W2 D-", yellow at "W7 TCH", green at "W3 D+", black at "W4 GND". Solder in the order of step 6. The face on which the joint is made is not fixed by any file (the pads are plated through, `design/wiring/product-wiring.csv` "through hole,F.Cu,B.Cu"): solder on the face the wire stands out of (lead).
9. Check after soldering (case not powered and the cell lead W5 not yet soldered or the cell unplugged, so that nothing on the board is live; lead): with a multimeter on continuity, one probe on the plunger tip of each spring pin and the other on the main board pad: P1 to W1, P2 to W2, P3 to W3, P4 to W4 must all beep (a short, below about 50 ohm, lead); the touch strip E1 on the pin board front to W7 must beep. Then no continuity between any two of the five main board pads: the ten pairs W1-W2, W1-W3, W1-W4, W1-W7, W2-W3, W2-W4, W2-W7, W3-W4, W3-W7, W4-W7 must not beep. A reading of about 147 kohm between W1 and W4 is normal (R12 100 kohm plus R13 47 kohm from VRING through VRING_SENSE to ground, `design/ecad/case/netlist.csv`); a beep is a short. Wait for a steady reading before you write the number down: the capacitor C15 (10 uF, `design/ecad/case/parts.csv` line 52, net VRING in `design/ecad/case/netlist.csv` line 252) is on the VRING line and charges through the meter, so the reading moves until C15 is charged (PM P8, change C15; review 3 G10). A wire that fails is reheated or replaced before the pin board goes on.
10. Cell leads W5 and W6 and thermistor TH1 (they come after step 9, because step 9 needs the cell lead W5 not yet soldered: my reading; marks added 2026-11-13, review 2 fault F5). Marks on the bottom face of the main board, same size and style as the five wire labels of step 7 (silkscreen colour assumed white, see Round 3; 1.0 mm high, printed mirrored: read them with the board turned over; script design/wiring/case-marks-2-work/add_marks_2.py, text items in case_main.kicad_pcb): "W5 +" 1.35 mm from the hole W5 (BAT), "W6 -" 1.45 mm from the hole W6 (GND), "TH1" 1.45 mm below the two thermistor holes TH1.1 and TH1.2 (positions in design/wiring/case-marks-2-work/search_B.log). Lead colours (design/wiring/lead-decisions.md, rows "case cell BT1 leads" and "case thermistor TH1 leads"): the cell's red lead (+) goes through the hole marked "W5 +", cut 13.0 mm; the cell's black lead (-) goes through the hole marked "W6 -", cut 15.2 mm; 2 mm stripped. Before cutting, measure the cell with the red probe on the red lead: the reading must be positive, between 3.0 and 4.35 V; a negative reading means the colours are reversed on that cell, and the cell is set aside. Never swap the two: a reversed cell on the charger is a fault. After the two cell lead joints are made, check them: red probe on pad W5, black probe on pad W6, meter on volts: the reading must again be positive, between 3.0 and 4.35 V, the same as before cutting (PM P8, change C16; values from `design/wiring/lead-decisions.md` line 70, row "case cell BT1 leads": "the reading must be positive, between 3.0 and 4.35 V"). A reading outside this range, or a negative one, means a bad joint or swapped leads: reheat or redo the joint, and never go on with the case until the reading is right (my reading). The thermistor leads are bare, with no colour and no polarity: cut to 10 mm, one in each of the two holes at the mark "TH1" (either way round), joints 5 mm or more from the bead, at most 7 seconds at 340 degrees C with a 50 W iron.

### Disk (ruling 8)

My scratch folder pcb/work (261 MB at the end) was deleted with one command; what the notes cite was copied first to evidence/kept/. The pcb folder is now 20 MB (`du -sh` in evidence/disk_final.log).

### Changes other files need (round 2 list, replaces the round 1 list where it differs)

1. design/case/case.py line 737 (and `PCB1["y"]` line 141): the main board is 23.0 x 37.9 mm, y from -17.7 to +20.2 mm; the model box is 35.4 mm and symmetric. Re-run case_check.py.
2. case.py line 744: the U1 box moves 4.1 mm toward -y (2.0 mm overhang), as in round 1.
3. case.py line 741: the tab under the socket is 10.2 mm wide.
4. case.py lines 642-645: PCB1 has no mounting feature in the model.
5. case-bom.csv lines 24 and 25: E1 is 3.9 x 1.15 mm plus a back pour (18.9 mm2); PCB1 is 37.9 mm long.
6. case-bom.csv: R8 510 ohm, R9 and R10 270 ohm, R21 to 3V3 (the netlist and parts.csv already hold them).

### Not closed

1. The 16 test pads are on the bottom face (see "Length used").
2. Chip land patterns are IPC-7351B nominal (Vishay comparison in round 1 item 5); no maker part number for the wire.
3. A floating module pin on the LED cathodes: the sheet does not bound the voltage (sch-notes.md section 9).
4. "Minimum connection width" check off for PCB1 (see Rules).

## Round 3 (review 2026-11-13, minors m2, m3, m4)

Written 2026-11-13 11:47 CET (clock from the `date` command). Evidence folder: design/ecad/case/pcb/evidence/marks/ (copies of every file before the change in before/). Only silkscreen text, the netlist rows and the notes changed; copper, pads, nets and outlines are the same (proof below).

### m2: marks on the pin board and the wire holes

Why (a) and not (b): the pin board file holds three separate closed outlines, not one: 12 Edge.Cuts lines = 3 rectangles, x 95.1 to 97.65 (the P1 wing), 97.75 to 102.25 (the inner piece with P2, P3, E1) and 102.35 to 104.9 (the P4 wing), 0.10 mm gap between them, nothing joins them (evidence/marks/pins_dump_before.log, "DRAW PCB_SHAPE Edge.Cuts" 12 times; design/wiring/review-work/case_pins_outline.log lists the lines). The two wings have the same 2.55 x 5.0 mm shape, so they can be swapped; the fault is therefore "no mark" and the marks below close it. Nothing joins the pieces in the file, so a one outline proof is not possible.

Marks (silkscreen text, height 1.0 mm, stroke 0.15 mm; script add_marks.py, KiCad's Python; the texts are in the board files):

| Board, face | Text | At (x, y mm, board frame) | Width | On |
|---|---|---|---|---|
| PCB2 front (F.SilkS, the face with the pins and the five wire pads) | P1 + | 96.379, 98.45 | 0.55 | wing of P1 (VRING) |
| PCB2 front | P4 - | 103.621, 98.45 | 0.55 | wing of P4 (GND) |
| PCB2 back (B.SilkS, mirrored) | P1 and + | 96.479, 98.45 and 96.479, 101.40 | 0.60 | wing of P1: the name above the pad, what it carries below |
| PCB2 back | P4 and GND | 103.521, 98.45 and 103.521, 101.65 | 0.60 | wing of P4 |
| PCB2 back | P2 and D- | 98.803, 98.45 and 98.803, 101.65 | 0.60 | inner piece, P2 |
| PCB2 back | P3 and D+ | 101.197, 98.45 and 101.197, 101.65 | 0.60 | inner piece, P3 |
| PCB1 bottom (B.SilkS, mirrored) | W1 +, W2 D-, W7 TCH, W3 D+, W4 GND | 119.95, 96.80; 120.25, 98.40; 120.40, 100.00; 120.25, 101.60; 120.50, 103.20 | 0.60 | on the row of holes W1, W2, W7, W3, W4, to the right of each hole |

Text size: the maker's smallest legible text is 40 mil (1.0 mm) high with a stroke of at least 0.15 mm ("Legend: Minimum Line Width >=0.15mm, Minimum text height 40 mil (1.0mm)", design/ecad/case/pcb/evidence/capab_jlc.html.txt, saved page design/datasheets/w5_jlcpcb_capabilities.html), so the texts are 1.0 mm high and meet it; the width of the characters (0.55 and 0.60 mm instead of 1.0 mm) is narrowed so the text fits the 2.55 mm wing and is not limited by the maker's sheet. The project's own setting (min_text_height 0.8 in case_main.kicad_pro) is looser and not used. Distance to every pad opening at least 0.15 mm (the maker's "Pad To Silkscreen 0.15mm") and 0.2 mm to the edge of the piece, from the search evidence/marks/search_marks.py (logs search_pins_*.log, search_main_*.log).

What does not fit (measured, not assumed):
- "P4 GND" in one line on the wing front needs 3.35 mm of width at 0.6 mm character width (evidence/marks/measure_ink.log); the wing is 2.55 mm. The front text is therefore "P4 -" and "P1 +"; the full word GND is on the back of the wing.
- The front of the inner piece has no free place for a 1.0 mm text (the touch strip E1 and the two pads fill it): the nearest free places the search finds for "P2" and "P3" are on the wings (evidence/marks/search_pins_F_inner.log, x 96.9 and 103.0), which would mislead. The inner piece marks are on its back only. The inner piece cannot be mixed up with a wing (it is 4.5 mm wide and carries E1), and P2 and P3 are tied to their pads by the copper.
- Main board front (top) face: the nearest free place for "W1 +" is 2.38 mm from W1 but on the row between the holes W1 and W2 (it would read as W2's label), and for the other four labels the nearest free places are 5.06 to 5.60 mm away, among other parts (evidence/marks/search_main_F_final.log); a label that far away or beside the wrong hole would mislead, so the labels are on the bottom face, in the row of each hole (evidence/marks/search_main_R_B.log). The holes are plated through, so the labels are next to the wire ends that stand out of the bottom face; this is why step 8 of the soldering order tells the builder to check each colour against its label.
- The silkscreen colour is not stated in any file; white is assumed (lead, to confirm at the board order).

Check: check_boards.py now has a sixth check (marks): fails when a wing text is missing or stands on the other wing, when a text is below 1.0 mm high or 0.15 mm stroke, or when a wire hole of PCB1 has no label in its row. Broken copies (evidence/marks/broken/, exits.txt): no marks on the pin board (6 FAIL), the P1 and P4 texts exchanged (4 FAIL), 0.6 mm text (3 FAIL), no marks on the main board (5 FAIL), and the four earlier copies from make_broken.py regenerated from the new main board (wrong net, outside, track removed, part removed) all exit 1.

### m4: the five wire pads in the netlist

The netlist (netlist.csv, made by make_netlist.py) describes both case boards; the main board holds the circuit and the pin board holds P1 to P4, E1 and the wire ends. The five wire pads of PCB2 are now parts of the netlist like P1 to P4: WP1 (VRING), WP2 (USB_D-), WP3 (USB_D+), WP4 (GND) and WP7 (RING_TOUCH), symbol PIN1, footprint OpenRingCase:WIRE_SMD_0.9x1.1, sheet ringlink, listed in additions.csv as added parts (the case bill of materials has no row for them: they are pads, not parts). Counts: 284 netlist rows (279 before), 94 parts (89 before), 61 nets (unchanged). check_boards.py no longer special-cases WP1 to WP7 (they are placed parts that must have a pad and a net that equals the net of W1 to W4 and W7 in the netlist), and make_bom.py writes them in fab/case_pins_parts.csv with a note (the old note carried an unfilled "W%s"). The schematic is generated from the same tables (gen_sch.py), so case_ringlink.kicad_sch now shows them.

### m3: soldering order

Written in "Wiring table (replaces part f)" above (numbered steps 1 to 10).

### Files made again

fab/case_pins/ and fab/case_main/ with export_fab.sh (every export exit 0, evidence/marks/fab_exits.txt) and the parts lists with make_bom.py. Compared with the files before: the same list of files; every copper, mask, paste, outline, drill and job file is equal to its earlier copy except the creation-date lines; only case_pins-F_Silkscreen.gbr, case_pins-B_Silkscreen.gbr and case_main-B_Silkscreen.gbr changed (evidence/marks/compare_fab.log). Pads, tracks, vias, zones and outlines read back from the boards are identical before and after (evidence/marks/dump_after.log).

## Round 4 (process sheet changes C4, C5, C6, C15, C16)

Written 2026-11-13 from 13:47 (clock from the `date` command). PM = design/mfg/assembly/process.md. Work folder: design/ecad/case/pcb/case-proc-work/ (every log). No pad, hole, track, zone or outline of either board changed (proof in case-proc-notes.md).

### Fabrication notes for both case boards (PCB1 case_main, PCB2 case_pins)

These notes go to the board maker and the stencil maker with the Gerber files of fab/case_main/ and fab/case_pins/ (export_fab.sh).

1. Panel (change C4; PM P7 and its first lines): no new copper on either board. Each board is delivered in a panel with rails of 5 mm (PM P7, first bullet: "The board maker's assembly rule: 5 mm tooling edges"), and three fiducials of 1 mm, centred 3.85 mm from the panel edges, on the rails, not in a line (PM P7: "1 mm fiducials centered at 3.85 mm from the panel edges"; three is a [CHOICE], PM "for the lead to confirm"). PCB1 panel: three on the top face (F). PCB2 panel: three on the top face (F), the face with the pins (PM P7, bullet "Case main board panel: three on the top face (F). Case pin board panel: three on F."). The bottom face of PCB1 has no paste, so it gets no fiducial for paste. PCB2 is three separate pieces in one file (Round 3, m2): all three pieces stay in the same panel.
2. Fiducial mask opening: not in any saved document (PM P7, last bullet); the board maker takes it from the fiducial footprint it uses. Open, for the lead.
3. Stencils (PM P2 table, rows "Case main board, top (F)", "Case main board, bottom (B)" and "Case pin board (PCB2)"): both stencils stainless steel, laser cut, 0.10 mm. PCB1: F paste file with 265 openings, no bottom stencil. PCB2: F paste file with 4 openings, one ring over each spring pin pad, outer 1.70 mm, inner 1.10 mm (added by case-proc-work/add_pin_paste.py; the ring shape is a [CHOICE] of this round: PM gives no opening size). The rings are drawn as stroked circles of 0.30 mm width in case_pins-F_Paste.gbr (two half arcs each, 8 arcs in all), not as flashed pads; the stencil maker reads them as four ring openings.
4. Copper weight: 35 um on outer layers (1 oz) and 17.5 um on inner layers, for the boards that have inner layers (PCB1 only) (`design/wiring/lead-decisions.md` row "board read-back test: the lead's rulings on its four open points", ruling 4: "ordered with 35 um outer copper (1 oz) and 17.5 um inner copper where a board has inner layers; this is written into the case board notes at the next change of those files").
5. Reflow after paste: the assembly follows the case procedure, steps 1 and 4 (one reflow of the main board with the profile of PM P3; one reflow of the pin board with the same profile).


RESULT: done, PCB1 rules check 0 violations and 0 unconnected items, PCB2 rules check 0 violations and 0 unconnected items.
