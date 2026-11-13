Computed from the board fabrication files and design documents; nothing here was measured on hardware.

Pre-registration frozen: 2026-11-13 11:15:47 CET (read from date; no measurement had been run before this line)

# Board read-back from the fabrication files

Everything below is computed from files (fabrication data and design documents) and stated as computed; nothing was measured on hardware.

## 0. Pre-registration (written before any measurement; frozen)

Hypothesis: the fabrication files of this product's circuit boards make the circuits that the netlists describe, and their power paths and controlled lines meet the design's own limits.
Falsifier: any pass line below that ends FAIL with its numbers falsifies the hypothesis for that board or line; a broken copy (P2) that is NOT detected falsifies the claim that the read-back can see opens and shorts.
Spend cap: 3 hours of work and 250 tool calls (brief); work folder under 150 MB; no tokens or money beyond that. No browser, no web request.
Writes to: this file and design/wiring/readback-work/. Design files are read only. check_band.py is not run; the 14 flex*-drc.rpt files are not touched.
Version under test: ROOT commit b9ec3cfa (ROOT = .). Fab files read as they sit in the repository (ring fab files dated 2026-11-13 11:02, band 2026-11-13 00:30).

Disclosure of what I knew before freezing: I had read the document lines quoted below, the fab/ directory listings, the headers of some Gerber and drill files (aperture lists, attribute lines, drill file function lines), and the list of net names. I had NOT run any extraction, resistance or impedance computation. One earlier report is on disk (ring/pcb/board-notes-r3.md line 54: "XL1 8.90 mm ... XL2 7.75 mm, nearest ... 0.085 mm ... 0.090 mm ... Plan d.4 (0.20 mm) is not met"); I read that line before freezing and my crystal pass line (P5) does not change because of it.

### 0.1 Methods (fixed)

M1 Gerber reader (Python, own script, `ROOT/design/.venv/bin/python`, packages numpy, scipy, Pillow): reads RS-274X/X2 copper layers: apertures C, R, O, and macros (primitives 1, 4, 20, 21), draws (D01 lines, round or rectangular aperture), flashes (D03), regions (G36/G37, even-odd fill). Every board's copper layers are rasterised (5 micrometre pixels for ring and band, 10 micrometre for the case boards). Excellon drill files (X2 line `TF.FileFunction,Plated,a,b,...` gives the layer span; PTH = all copper layers; NPTH ignored) join copper of the layers they span at each hole position. Connected components (4-neighbour) of copper + holes give the extracted connectivity. The X2 net attributes (`TO.N`) are NOT used to join anything; the `TO.P,ref,pin` attribute names a flash (which pad it is) and is used only to say which pad sits at that place.
M2 Expected grouping: ring: ROOT/design/ecad/ring/netlist.csv; case: ROOT/design/ecad/case/netlist.csv; band flex1/flex2: the rows of the ring netlist.csv for the references that exist on the flex board (J_BAND_A, M1, SW1-SW5 on flex1; J_BAND_B, PRT1, CP1-CP4 on flex2), because build_band.py reads exactly that file (line 20, 41-44) and band-interface.md section 2 tables define the J_BAND lands; the two land tables of band-interface.md are parsed and compared with the netlist rows (a mismatch is reported).
M3 Route A (IPC-D-356 read-back, ring only, because only ring/pcb/fab/ holds a .ipc356): the pad records (327) and via records (317/307) are parsed; pad (ref, pin) to net groups compared with the netlist as PARTITIONS (names may differ; two pads are together iff they share a net). Route A also checks the pad coordinates of the IPC-D-356 file against the flashes of the Gerber copper (position match within 0.01 mm).
M4 Counting, per board: nets compared = nets of the expected grouping with at least one pad on this board; pads compared = expected pads (ref, pin) of references that appear in this board's fab data; short = a connected copper component holding pads of two or more expected nets, or an expected-no-net pad (net empty) joined to a netted pad; counted as number of (component, extra net) pairs; open = a net whose pads lie in more than one component, counted as components minus one; missing = expected pad of a present reference that has no flash on any copper layer (counted separately and counted as a failure of P1 for that board; a reference absent from the fab data of every board of its netlist is also counted missing). For the case netlist (one file for two boards) each board is compared on its own pads; a net with pads on both boards must be in one component only within each board. Rule for a stack via with no copper on an intermediate layer: the barrel model connects through (reported as a count); the alternative (stack of microvias, open at that layer) is computed too and any difference is reported.
M5 Resistance: copper resistivity 1.72e-5 ohm mm (the value band-interface.md line 132 uses); sheet resistance = resistivity / finished copper thickness: ring 0.018 mm (fab/stackup.txt), band 0.012 mm (band-interface.md line 132; the board file's own stackup block is read and any difference reported), case: from the board file's stackup block. The net's copper pixels on every layer (draws, pads, regions) form a resistor mesh (each 4-neighbour link = one square of sheet resistance); a hole joins the copper of adjacent layers with 1 milliohm per layer step (the brief's stated figure; no file gives barrel plating). Source pads and sink pads are ideal equipotentials; R = V / I from a sparse solve (scipy). Validated first on synthetic tracks of known resistance (straight and 45 degree) and cross-checked on real nets against the sum of rho L / (w t) over the drawn tracks. The ring GND plane is not solved (not asked).
M6 Impedance: microstrip by Hammerstad and Jensen with Wheeler's thickness correction (the form the plan's zcalc.py uses, plan section d header), dielectric constant 4.1 (the plan's value, section d header; the board file's stackup value is reported as a sensitivity), copper 0.018 mm, h 0.065 mm (fab/stackup.txt: L1 to L2 prepreg). Differential: Zdiff = 2 Z0 (1 - 0.48 exp(-0.96 s / h)) (IPC-2141 edge-coupled form, the plan's form), s = drawn gap, w = drawn width. Drawn width and gap are taken from the Gerber draws (aperture width; edge-to-edge distance between the two legs from the raster). The standard formula's own validity is not extended beyond the plan's statement.
M7 Lengths: shortest path along drawn copper from one terminal pad to the other: nodes are draw end points, flashes join all draw end points inside them by straight chords, via steps cost nothing (vertical length ignored, stated), plus the sum of all drawn lengths of the net as a second figure.
M8 Nearest other-net copper: Euclidean distance transform of the raster (5 micrometre pixel; resolution stated), per layer, from the line's copper to copper of any other net (net of a component = the expected net of its pads).
M9 Broken copies (P2): a work copy of ring.kicad_pcb (the repository file is not edited), edited by KiCad's Python (run_kipy.sh); fabrication files exported again with kicad-cli by the same options as ring/pcb/make_fab.sh (Gerber, drill, IPC-D-356) into the work folder. Cut copy: the net LCD_SCK; its track segments in descending length; the first segment whose removal raises KiCad's own count of unconnected items by one (pcbnew connectivity) is removed. Joined copy: the nets LCD_SCK and LCD_MOSI; one new track segment of the width 0.100 mm is added on the layer where a point of an LCD_SCK segment and a point of an LCD_MOSI segment are nearest. Control: an unedited copy exported the same way must pass P1 on both routes. Expected, written now: Route A (IPC-D-356 lists pad-to-net assignments, not copper) will NOT see the cut and will NOT see the join; Route B (Gerber) will see both.

### 0.2 Pass lines, limits and their sources (fixed)

Verdict words: PASS, FAIL, REPORT (no written limit: the figure is reported, not judged), CANNOT TELL (tool failure). "Met" in the RESULT line = PASS items; "failed" = FAIL items; REPORT items are counted apart.

P1 (17 boards: ring, case_main, case_pins, flex1-us7 to us13, flex2-us7 to us13). PASS for a board iff shorts = 0 and opens = 0 and missing pads = 0 on Route B, and on Route A for the ring (partition identical, pad sets identical). Reported per board: nets compared, pads compared, shorts, opens, missing.
P2 PASS iff (control passes P1 on both routes) and (cut copy: Route B shows exactly one open, on LCD_SCK, and nothing else differs from the control) and (joined copy: Route B shows exactly one short joining LCD_SCK and LCD_MOSI and nothing else differs from the control). Route A results are reported per copy (expected: not detected, M9); P2 is judged on Route B, as P1 is the conjunction of both routes and a copy that fails either fails P1.
P3 Power paths (copper only; wires, cell and connector contact resistance are not in fab files). Currents and limits:
 - Ring VBAT: band land J_BAND_B pin 1 to U2 D1+D2 (merged) and to U11 pin 4, at 235 mA (brief). Limit: no written limit in the design files read (motor-drive.md, band-notes.md, band-interface.md, architecture.md, sim/circuit/pass-lines.md R1.2 gives 3.0 V at the cell, with no share for the board copper): REPORT.
 - Ring VMOT: U11 pin 1 (OUT) to J_BAND_A pin 7, at 175 mA and 80 mA (motor-drive.md: start 175 mA, rated below 80 mA). Limit: motor operating window 2.7 to 3.3 V (motor-drive.md line 11; pass-lines.md R1.7) against U11 output 2.964 to 3.036 V (motor-drive.md line 46): total allowed drop 2.964 - 2.7 = 0.264 V from U11 OUT to the motor, VMOT plus return. The judged quantity is the sum for the longest band size, US 13: ring VMOT + band VMOT + band GND (ring GND plane not solved), at 175 mA and at 80 mA, against 264 mV. Per size US 7 to 13 reported.
 - Ring VBUS: J_BAND_B pin 4 to U2 B1+B2 (merged), at 15 mA (the design's charge current: architecture.md line 45 "set to 15 mA", pass-lines.md R3.1) and, as a second line, at 100 mA (IBUS100MA, plan d.5 row VBUS). Limit: chip VBUS minimum 4.0 V (pass-lines.md R3.6, nPM1304 p13) from a 5.0 V case VBUS with a contact path of 0 to 2 ohm (same row): allowed copper drop 5.0 - 4.0 - 2 ohm x I = 0.970 V at 15 mA, 0.800 V at 100 mA. PASS iff drop is at or under each.
 - Ring VDD_1V8: source U2 B6 (VOUT1) to the load pad with the highest resistance from the source (all other pads of the net are loads), at 0.2 A (plan d.5 design current for the buck output, the load the design states). Limit: 1.8 V rail with -5 percent (pass-lines.md R1.3, 1.71 V; nPM1304 p45): 90 mV copper drop, with the regulator at its nominal 1.8 V (my reading: the file gives the accuracy band of the regulator itself, none for the copper).
 - Ring VDD_SD: source U2 A5 (LSOUT2) to the farthest load pad, at 0.1 A (plan d.5 design current for the load switches) and, as a second line, 25 mA (storage write, sim-notes.md ring1 row). Limit: SD card Vcc 2.7 to 3.6 V (pass-lines.md R2.7) with VDD_3V0 at 3.0 V nominal (R1.5/R1.6): 300 mV drop (same reading as above).
 - Band circuits (US 7, 9, 13 first, then all 14 boards): motor lines VMOT and GND on flex1 from J_BAND_A pins 7 and 6 / 8 to the motor lands M1 pins 1 and 2 at 175 mA and 80 mA; cell lines VBAT and GND on flex2 from J_BAND_B pin 1 and pins 2 / 7 to the PRT1 pins 1 and 2 (the cell tabs) at 227.5 mA (band-interface.md line 133). Limits: motor lines judged in the VMOT sum above; plus the design's own stated figures, band-interface.md line 132 (US 13: VMOT 6.90 mm, 8.7 mV; GND 10.30 mm, 12.9 mV at 175 mA) and line 133 (US 13: VBAT 11.0 mV, GND 12.5 mV at 227.5 mA): PASS iff the measured drop of US 13 is not above 1.10 times the stated figure (10 percent tolerance is my choice, stated). All other band figures: REPORT. NOTE: the brief names "band-notes.md (its voltage drop table)"; band-notes.md has no such table (grep "drop" finds only lines 11 and 17); the only drop figures are in band-interface.md lines 132 and 133 and are used.
 - Case: VRING from U5 pin 6 (OUT) to W1 (case_main) and from W1 to P1 (case_pins) at 0.400 A (current limit, pass-lines.md C1.3 "0.400"). Limit: VRING at 0.39 A load, cell at 3.0 V, is 4.901 V (sim-notes.md line 70) and the ring chip needs 4.0 V (C1.5): copper drop of both boards together at most 0.901 V. Cell lines: BAT from U2 13+14 (merged) to W5 and GND from U2 pad 25 to W6 at 0.350 A (the cell's allowed maximum charge current, pass-lines.md C2.2/C2.3): REPORT (no written limit). The GND solve on the case board uses a coarser raster (20 micrometre) if memory needs it; stated if used.
 Resistance and drop are reported for every path with the figure from the Gerber mesh and the cross-check figure from drawn track lengths.
P4 (ring): target values from ring-board-plan.md section d and h.2: antenna feed 50 ohm (d.1), USB differential 90 ohm (d.2), tolerance plus or minus 10 percent (h.2 table row "Impedance": "if outside +-10 percent, the width is changed"): 45 to 55 ohm and 81 to 99 ohm.
 - P4.1 antenna line = nets ANT1_NODE, ANT2_NODE, ANT3_NODE, RF_FEED (ANT_TRIM is not the feed). Z0 from the drawn width of its L1 runs (the width of the longest runs) in 45 to 55 ohm: PASS/FAIL; the minimum and maximum drawn width reported.
 - P4.2 L1 clearance of the antenna line (draws) to other-net L1 copper at least 0.200 mm (d.1 "kept 0.200 mm away"; net class RF gap 0.200, c.5): strict, the whole line, one pixel (0.005 mm) of resolution is not forgiven; the value excluding the first 1.0 mm from U1 ball C1 also reported.
 - P4.3 reference: L2 under the line draws is GND copper at 100 percent of the sampled centreline points (every 0.02 mm) (d.1 "L2 solid ground under the whole line"), and no L2 copper of another net under the line; the coverage of +-0.50 mm either side reported.
 - P4.4 USB pair Zdiff in 81 to 99 ohm by M6 from drawn width and gap (min and median gap reported); P4.5 mismatch of the two legs (shortest pad-to-pad paths U1 H6/H7 to J_BAND_B 5/6) at most 0.10 mm (d.2 "Length match inside the pair: 0.10 mm or less"). Reported: Z0 each line; lengths of each leg, total drawn length; the antenna line length by leg against the plan's 16.4 mm (R2.0 point 3; no tolerance written: REPORT); nearest other-net copper to the antenna line per layer L1 to L4 (REPORT).
P5 (ring): XC1, XC2 (32 MHz): each at most 6.0 mm, the two within 0.5 mm of each other (d.4); XL1, XL2: each at most 9 mm (d.4, h.2); other-net copper on the same layer at least 0.20 mm (d.4 "0.20 mm from any other L3 copper"/"any other copper of the same layer", applied to every layer the line runs on). Judged: 4 length items + 1 match item + 4 gap items. Width and layer(s) reported.

Pilot (before the main run): synthetic checks of the Gerber reader and the solver (known-pass and known-fail cases), a hand-labelled sample of real pads (each label read from the board file and the netlist case by case; saved), a known-correct expected grouping run through the real inputs for every board, and a scorer check with a planted short and a planted open on a synthetic copy. Any change to a scorer after the pilot is listed in section "deviations".

## 1. Results (computed 2026-11-13 11:49:10; tables rebuilt from results/*.json by readback-work/make_tables.py; log lines in readback-work/logs/)

Everything is computed from the fabrication files (Gerber copper, Excellon drill, IPC-D-356) by readback-work/rb_lib.py (reader, rasteriser, connectivity), rb_res.py (mesh resistance, drawn-copper graph, impedance formulas), run_p1.py (P1 and P2), p3_ring.py, p3_band.py, p3_case.py (P3), p4p5.py (P4 and P5). A pixel is 0.005 mm (ring, band) or 0.010 mm (case boards, and 0.050 mm for the case GND solve); a clearance read from a pixel raster reads slightly high (0.125 against 0.122 at the antenna in the board-file cross-check below).

Short answer: on none of the 17 boards does the fabrication copper join two nets or split one (shorts 0, opens 0; the ring board agrees on the IPC-D-356 route too). Both planted faults were found by the Gerber route and neither by the IPC-D-356 route. The power paths meet every limit the design writes. The controlled lines do not meet the plan: antenna clearance and ground reference, the USB pair gap, one crystal length and all four crystal clearances.

### P1 per board (Route B: Gerber + drill read-back; field names are those of the results/p1_*.json files)

| board | nets compared (nets) | pads compared (pads) | shorts | opens | missing pads (missing) | refs of its netlist in no fab file | stack-model shorts/opens | route A | P1 |
|---|---|---|---|---|---|---|---|---|---|
| ring | 84 | 359 | 0 | 0 | 0  | BT1, DISP1, RT1 | 0/0 | pads 359, nets 84, joined 0, split 0, coords 362/362 | FAIL |
| case_main | 61 | 272 | 0 | 0 | 0  | BT1 | 0/0 | n/a (no .ipc356 in fab/) | FAIL |
| case_pins | 5 | 10 | 0 | 0 | 0  | - | 0/0 | n/a (no .ipc356 in fab/) | PASS |
| flex1-us7 | 7 | 30 | 0 | 0 | 8 (SW1-2, SW3-2, SW4-2, SW5-2, SW3-1, SW4-1, SW5-1, SW1-1) | - | 0/0 | n/a (no .ipc356 in fab/) | FAIL |
| flex1-us8 | 7 | 30 | 0 | 0 | 8 (SW1-2, SW3-2, SW4-2, SW5-2, SW3-1, SW4-1, SW5-1, SW1-1) | - | 0/0 | n/a (no .ipc356 in fab/) | FAIL |
| flex1-us9 | 7 | 30 | 0 | 0 | 8 (SW1-2, SW3-2, SW4-2, SW5-2, SW3-1, SW4-1, SW5-1, SW1-1) | - | 0/0 | n/a (no .ipc356 in fab/) | FAIL |
| flex1-us10 | 7 | 30 | 0 | 0 | 8 (SW1-2, SW3-2, SW4-2, SW5-2, SW3-1, SW4-1, SW5-1, SW1-1) | - | 0/0 | n/a (no .ipc356 in fab/) | FAIL |
| flex1-us11 | 7 | 30 | 0 | 0 | 8 (SW1-2, SW3-2, SW4-2, SW5-2, SW3-1, SW4-1, SW5-1, SW1-1) | - | 0/0 | n/a (no .ipc356 in fab/) | FAIL |
| flex1-us12 | 7 | 30 | 0 | 0 | 8 (SW1-2, SW3-2, SW4-2, SW5-2, SW3-1, SW4-1, SW5-1, SW1-1) | - | 0/0 | n/a (no .ipc356 in fab/) | FAIL |
| flex1-us13 | 7 | 30 | 0 | 0 | 8 (SW1-2, SW3-2, SW4-2, SW5-2, SW3-1, SW4-1, SW5-1, SW1-1) | - | 0/0 | n/a (no .ipc356 in fab/) | FAIL |
| flex2-us7 | 6 | 14 | 0 | 0 | 0  | - | 0/0 | n/a (no .ipc356 in fab/) | PASS |
| flex2-us8 | 6 | 14 | 0 | 0 | 0  | - | 0/0 | n/a (no .ipc356 in fab/) | PASS |
| flex2-us9 | 6 | 14 | 0 | 0 | 0  | - | 0/0 | n/a (no .ipc356 in fab/) | PASS |
| flex2-us10 | 6 | 14 | 0 | 0 | 0  | - | 0/0 | n/a (no .ipc356 in fab/) | PASS |
| flex2-us11 | 6 | 14 | 0 | 0 | 0  | - | 0/0 | n/a (no .ipc356 in fab/) | PASS |
| flex2-us12 | 6 | 14 | 0 | 0 | 0  | - | 0/0 | n/a (no .ipc356 in fab/) | PASS |
| flex2-us13 | 6 | 14 | 0 | 0 | 0  | - | 0/0 | n/a (no .ipc356 in fab/) | PASS |

### P2 broken copies of the ring board (each exported again with kicad-cli into readback-work/p2/<name>/fab)

| copy | Route B shorts | Route B opens (net) | Route A joined/split | draws read | what the edit was |
|---|---|---|---|---|---|
| control | 0  | 0  | 0 / 0 | 5551 | byte copy, no edit |
| resave | 0  | 0  | 0 / 0 | 5551 | loaded and saved by pcbnew, no edit |
| cut | 0  | 1 {'LCD_SCK': 1} | 0 / 0 | 5550 | one LCD_SCK segment removed |
| join | 1 [['LCD_MOSI', 'LCD_SCK']] | 0  | 0 / 0 | 5552 | one added segment LCD_SCK to LCD_MOSI |

### P3 power paths (R from the pixel mesh of the drawn copper; check = sum of rho L/(w t) on the minimum-resistance track path where the drawn-track graph reached both pads)

| path | from -> to | R mesh (mohm) | R track-sum (mohm) | current | drop (mV) | limit | verdict |
|---|---|---|---|---|---|---|---|
| ring VBAT | J_BAND_B-1 -> U2-D1+U2-D2 | 291.99 | 284.92 | 235mA | 68.62 | REPORT (no written limit) | REPORT |
| ring VBAT | J_BAND_B-1 -> U11-4 | 92.18 | 87.27 | 235mA | 21.66 | REPORT (no written limit) | REPORT |
| ring VBAT | J_BAND_B-1 -> U4-A1 | 310.81 | 299.53 | 235mA | 73.04 | REPORT (no written limit) | REPORT |
| ring VMOT | U11-1 -> J_BAND_A-7 | 205.26 | 170.11 | 175mA | 35.92 | part of the 264 mV sum below | REPORT |
| ring VMOT | U11-1 -> J_BAND_A-7 | 205.26 | 170.11 | 80mA | 16.42 | part of the 264 mV sum below | REPORT |
| ring VBUS | J_BAND_B-4 -> U2-B1+U2-B2 | 206.14 | 188.04 | 15mA | 3.09 | <= 970 mV | PASS |
| ring VBUS | J_BAND_B-4 -> U2-B1+U2-B2 | 206.14 | 188.04 | 100mA | 20.61 | <= 800 mV | PASS |
| ring VBUS (other loads) | J_BAND_B-4 -> U9-4 | 52.45 | 52.01 | 15mA | 0.79 | REPORT (no written limit) | REPORT |
| ring VBUS (other loads) | J_BAND_B-4 -> R1-1 | 162.59 | 152.24 | 15mA | 2.44 | REPORT (no written limit) | REPORT |
| ring VDD_1V8 farthest load | U2-B6 -> TP17-1 | 275.09 | n/a | 200mA | 55.02 | <= 90 mV | PASS |
| ring VDD_SD farthest load | U2-A5 -> C82-1 | 439.70 | 422.49 | 100mA | 43.97 | <= 300 mV | PASS |
| ring VDD_SD farthest load | U2-A5 -> C82-1 | 439.70 | 422.49 | 25mA | 10.99 | <= 300 mV | PASS |

#### band circuits, every size (mohm and mV; motor lines at 175 and 80 mA, cell lines at 227.5 mA)

| size | VMOT mohm | VMOT mV 175 / 80 | GND lands 6+8 mohm | GND mV 175 / 80 | GND land 6 only mV 175 | cell VBAT mohm | VBAT mV | cell GND 2+7 mohm | GND mV | GND land 2 only mV |
|---|---|---|---|---|---|---|---|---|---|---|
| US 7 | 38.77 | 6.78 / 3.10 | 55.06 | 9.63 / 4.40 | 9.81 | 46.78 | 10.64 | 50.44 | 11.47 | 12.19 |
| US 8 | 39.16 | 6.85 / 3.13 | 55.42 | 9.70 / 4.43 | 9.87 | 45.98 | 10.46 | 49.64 | 11.29 | 12.01 |
| US 9 | 39.27 | 6.87 / 3.14 | 55.56 | 9.72 / 4.44 | 9.90 | 45.27 | 10.30 | 48.92 | 11.13 | 11.84 |
| US 10 | 42.89 | 7.51 / 3.43 | 59.15 | 10.35 / 4.73 | 10.53 | 46.09 | 10.49 | 49.75 | 11.32 | 12.03 |
| US 11 | 45.00 | 7.88 / 3.60 | 61.29 | 10.73 / 4.90 | 10.90 | 47.71 | 10.85 | 51.36 | 11.69 | 12.40 |
| US 12 | 45.51 | 7.96 / 3.64 | 61.76 | 10.81 / 4.94 | 10.98 | 49.36 | 11.23 | 53.01 | 12.06 | 12.77 |
| US 13 | 47.33 | 8.28 / 3.79 | 63.59 | 11.13 / 5.09 | 11.30 | 51.04 | 11.61 | 54.69 | 12.44 | 13.16 |

Case: VRING main 6.53 mohm (2.61 mV at 0.400 A), pins board 0.44 mohm (0.17 mV); BAT 4.89 mohm (1.71 mV at 0.350 A); GND 1.22 mohm (0.43 mV) at the 50 um raster; VRING at the 50 um raster 6.70 mohm (resolution check).

### P4 and P5 (ring)

| id | item | figure | limit | verdict | results field |
|---|---|---|---|---|---|
| P2.control | control copy (byte copy and re-saved copy) | shorts/opens/missing(local) 0/0/0; refs in no fab file ['BT1', 'DISP1', 'RT1'] | passes P1 | FAIL | p1_ring_p2_control.json, p1_ring_p2_resave.json |
| P2.cut | cut copy | opens 1 {'LCD_SCK': 1}, shorts 0 | exactly one open on LCD_SCK, nothing else | PASS | p1_ring_p2_cut.json |
| P2.join | joined copy | shorts 1 [['LCD_MOSI', 'LCD_SCK']], opens 0 | exactly one short LCD_SCK-LCD_MOSI, nothing else | PASS | p1_ring_p2_join.json |
| P2.routeA | Route A on cut and join copies (expected: not detected) | cut joined/split 0/0, join 0/0 | REPORT (written expectation: not detected) | REPORT | routeA fields |
| P3.VMOT.sum.175mA | VMOT total at 175mA: ring VMOT 35.92 + band US13 VMOT 8.28 + band US13 GND (lands 6+8) 11.13 | 55.33 mV | <= 264 mV (2.964 - 2.7) | PASS | p3_ring.json VMOT, p3_band.json us13 |
| P3.VMOT.sum.80mA | VMOT total at 80mA: ring VMOT 16.42 + band US13 VMOT 3.79 + band US13 GND (lands 6+8) 5.09 | 25.30 mV | <= 264 mV (2.964 - 2.7) | PASS | p3_ring.json VMOT, p3_band.json us13 |
| P3.ring.VBUS.15mA | ring VBUS land to U2 B1+B2 at 15mA | 3.09 mV | <= 970 mV | PASS | p3_ring.json VBUS |
| P3.ring.VBUS.100mA | ring VBUS land to U2 B1+B2 at 100mA | 20.61 mV | <= 800 mV | PASS | p3_ring.json VBUS |
| P3.ring.VDD_1V8.200mA | ring VDD_1V8 source to farthest pad TP17-1 at 200mA | 55.02 mV | <= 90 mV | PASS | p3_ring.json VDD_1V8 |
| P3.ring.VDD_SD.100mA | ring VDD_SD source to farthest pad C82-1 at 100mA | 43.97 mV | <= 300 mV | PASS | p3_ring.json VDD_SD |
| P3.ring.VDD_SD.25mA | ring VDD_SD source to farthest pad C82-1 at 25mA | 10.99 mV | <= 300 mV | PASS | p3_ring.json VDD_SD |
| P3.VMOT.sum.us7.175mA | VMOT total US 7 at 175mA (ring VMOT + band VMOT + band GND) | 52.34 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us7.80mA | VMOT total US 7 at 80mA (ring VMOT + band VMOT + band GND) | 23.93 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us8.175mA | VMOT total US 8 at 175mA (ring VMOT + band VMOT + band GND) | 52.47 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us8.80mA | VMOT total US 8 at 80mA (ring VMOT + band VMOT + band GND) | 23.99 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us9.175mA | VMOT total US 9 at 175mA (ring VMOT + band VMOT + band GND) | 52.52 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us9.80mA | VMOT total US 9 at 80mA (ring VMOT + band VMOT + band GND) | 24.01 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us10.175mA | VMOT total US 10 at 175mA (ring VMOT + band VMOT + band GND) | 53.78 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us10.80mA | VMOT total US 10 at 80mA (ring VMOT + band VMOT + band GND) | 24.58 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us11.175mA | VMOT total US 11 at 175mA (ring VMOT + band VMOT + band GND) | 54.52 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us11.80mA | VMOT total US 11 at 80mA (ring VMOT + band VMOT + band GND) | 24.92 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us12.175mA | VMOT total US 12 at 175mA (ring VMOT + band VMOT + band GND) | 54.69 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.VMOT.sum.us12.80mA | VMOT total US 12 at 80mA (ring VMOT + band VMOT + band GND) | 25.00 mV | <= 264 mV (reported per size; the judged line is US 13) | REPORT | p3_band.json |
| P3.band.us13.vmot | band US13 VMOT at 175mA | 8.28 mV (stated 8.7 mV) | <= 9.57 mV (1.10 x stated, band-interface.md lines 132/133) | PASS | p3_band.json us13.vmot |
| P3.band.us13.gnd6 | band US13 motor GND (land 6 only, the stricter) at 175mA | 11.30 mV (stated 12.9 mV) | <= 14.19 mV (1.10 x stated, band-interface.md lines 132/133) | PASS | p3_band.json us13.gnd6 |
| P3.band.us13.vbat | band US13 cell VBAT at 227.5mA | 11.61 mV (stated 11.0 mV) | <= 12.10 mV (1.10 x stated, band-interface.md lines 132/133) | PASS | p3_band.json us13.vbat |
| P3.band.us13.cell_gnd2 | band US13 cell GND (land 2 only, the stricter) at 227.5mA | 13.16 mV (stated 12.5 mV) | <= 13.75 mV (1.10 x stated, band-interface.md lines 132/133) | PASS | p3_band.json us13.cell_gnd2 |
| P3.case.VRING | case VRING U5 OUT -> W1 (case_main) 2.61 mV + WP1 -> P1 (case_pins) 0.17 mV at 0.400 A | 2.79 mV | <= 901 mV | PASS | p3_case.json vring_main, vring_pins |
| P3.case.BAT | case BAT U2 13+14 -> W5 at 0.350 A | 1.71 mV | no written limit | REPORT | p3_case.json bat |
| P3.case.GND | case GND U2 25 -> W6 at 0.350 A (50 um raster) | 0.43 mV | no written limit | REPORT | p3_case.json gnd_50um |
| P4.1 | antenna feed Z0 (width 0.120 mm, Hammerstad-Jensen + Wheeler, er 4.1) | 49.31 ohm | 45 to 55 ohm | PASS | p4p5.json P4_1.Z0 |
| P4.2 | antenna L1 clearance to other-net copper (whole line; excluding 1.0 mm at U1 ball C1: 0.1950 mm) | 0.1250 mm at [102.283, -99.548] (copper of DECA) | >= 0.200 mm | FAIL | p4p5.json P4_2.min_clear_mm |
| P4.3 | antenna reference: share of line pixels over L2 GND (L2 other-net copper under the line: 0 px) | 96.647 percent (3101 px uncovered) | 100 percent and no other-net L2 copper | FAIL | p4p5.json P4_3 |
| P4.4 | USB Zdiff at the min / median / modal drawn gap (0.0778 / 0.1387 / 0.175 mm), width 0.100 mm | 92.10 / 101.90 / 104.70 ohm | 81 to 99 ohm at all three (stricter reading, stated) | FAIL | p4p5.json P4_4 |
| P4.usb.other | USB pair (both legs) nearest other-net L1 copper | 0.0900 mm (copper of (no netlist pad in that copper)) | plan: 0.200 mm class gap (d.2 "0.200 to other copper") REPORT | REPORT | p4p5.json P4_usb_other |
| P4.usb.ref | USB pair reference L2 GND coverage | 16.877 percent (96705 px uncovered; 19144 px of other-net L2 copper under the pair) | plan d.2: reference L2 solid; REPORT | REPORT | p4p5.json P4_3u |
| P4.5 | USB leg mismatch (shortest paths 14.075 / 14.075 mm; total drawn 14.523 / 14.493 mm, mismatch 0.030) | 0.000 mm | <= 0.10 mm | PASS | p4p5.json P4_5 |
| P4.len | antenna line length, sum of legs | 16.125 mm | plan 16.4 mm, no tolerance written | REPORT | p4p5.json P4_len |
| P4.near.L1 | nearest other-net copper to the antenna line on L1 | 0.1250 mm (copper of DECA) | REPORT | REPORT | p4p5.json P4_per_layer |
| P4.near.L2 | nearest other-net copper to the antenna line on L2 | 0.0000 mm (copper of GND) | REPORT | REPORT | p4p5.json P4_per_layer |
| P4.near.L3 | nearest other-net copper to the antenna line on L3 | 0.0000 mm (copper of SWDIO) | REPORT | REPORT | p4p5.json P4_per_layer |
| P4.near.L4 | nearest other-net copper to the antenna line on L4 | 0.0000 mm (copper of GND) | REPORT | REPORT | p4p5.json P4_per_layer |
| P5.XL1.len | XL1 length (shortest drawn path pad to pad; all drawn copper 8.897 mm) | 9.697 mm | <= 9.0 mm | FAIL | p4p5.json P5.XL1 |
| P5.XL2.len | XL2 length (shortest drawn path pad to pad; all drawn copper 7.751 mm) | 7.391 mm | <= 9.0 mm | PASS | p4p5.json P5.XL2 |
| P5.XC1.len | XC1 length (shortest drawn path pad to pad; all drawn copper 4.956 mm) | 4.956 mm | <= 6.0 mm | PASS | p4p5.json P5.XC1 |
| P5.XC2.len | XC2 length (shortest drawn path pad to pad; all drawn copper 4.926 mm) | 4.926 mm | <= 6.0 mm | PASS | p4p5.json P5.XC2 |
| P5.XC.match | |XC1 - XC2| | 0.030 mm | <= 0.5 mm | PASS | p4p5.json P5 |
| P5.XL1.gap | XL1 nearest other-net copper on its layers (L2 0.0873) | 0.0873 mm on L2 (copper of U1_VBUS) | >= 0.20 mm | FAIL | p4p5.json P5.XL1.clear |
| P5.XL2.gap | XL2 nearest other-net copper on its layers (L1 0.0990; L2 0.0919; L4 0.0939) | 0.0919 mm on L2 (copper of PMIC_SDA) | >= 0.20 mm | FAIL | p4p5.json P5.XL2.clear |
| P5.XC1.gap | XC1 nearest other-net copper on its layers (L3 0.1050) | 0.1050 mm on L3 (copper of SPARE_P3_04) | >= 0.20 mm | FAIL | p4p5.json P5.XC1.clear |
| P5.XC2.gap | XC2 nearest other-net copper on its layers (L3 0.1030) | 0.1030 mm on L3 (copper of SPARE_P3_03) | >= 0.20 mm | FAIL | p4p5.json P5.XC2.clear |

Verdict counts: {'FAIL': 18, 'PASS': 28, 'REPORT': 25}; per pass line: {'P1': {'FAIL': 9, 'PASS': 8}, 'P2': {'FAIL': 1, 'PASS': 2, 'REPORT': 1}, 'P3': {'REPORT': 17, 'PASS': 12}, 'P4': {'PASS': 2, 'FAIL': 3, 'REPORT': 7}, 'P5': {'FAIL': 5, 'PASS': 4}}


### How to read the P1 and P2 verdicts
- P1 verdict words follow the frozen rule (section 0.2): a board is FAIL if shorts, opens or missing pads are not zero, and I counted a reference of the netlist that is in no fab file of any board of that netlist as missing. That is why ring (BT1, DISP1, RT1: the cell, the screen, the cell thermistor; 19 netlist rows, logs/p1_global.log) and case_main (BT1, 2 rows) are FAIL with 0 shorts and 0 opens, and why the 7 flex1 boards are FAIL with 8 missing pads each (SW1, SW3, SW4, SW5 pins 1 and 2). Cause checked: the board file footprint Alps_SKTAAAE010_pads34 holds only pads 3 and 4 (logs/xcheck_sw.log), and band-interface.md line 103 says terminals 1 and 2 are not soldered because the part joins 1 to 3 and 2 to 4 inside. So these FAILs are a netlist-versus-footprint difference that the design already documents, not a copper fault. By the lead's own words (no two nets joined, no net split) all 17 boards are clean.
- P2 detection criteria are met (cut copy: exactly one open, LCD_SCK; join copy: exactly one short, LCD_MOSI with LCD_SCK; nothing else differs from the control). The formal P2 line FAILs only on its first clause, "control passes P1", because the control is the ring board again and inherits the ring's P1 FAIL from the three off-board references above. The control and the re-saved control have 0 shorts, 0 opens and 0 missing pads on the ring's own pads.
- IPC-D-356 route: the .ipc356 files of the control, the re-saved copy, the cut copy and the join copy are identical (0 differing lines, logs/p2_ipc_diff.log) while the Gerber copper layer of the edited layer differs by 2 lines. The IPC-D-356 file KiCad writes lists pad and via net assignments, not copper, so it cannot see an opened track or a joined pair of nets (as written in M9 before the run). Also found: its reference field is 6 characters, so J_BAND_A and J_BAND_B both read "J_BAND" (15 records); I resolved them by the pad coordinates (ipc_truncated_refs_resolved in results/p1_ring.json).
- Cut: segment of LCD_SCK, 1.675 mm on In2.Cu from (101.750, 97.450) to (103.425, 97.450), first in descending length whose removal raised KiCad's unconnected count by one (logs/p2_make_cut.log). Join: one 0.285 mm segment on In1.Cu from (104.973, 101.074) to (104.692, 101.122), width 0.100 mm (logs/p2_make_join.log); KiCad's own count stayed 0 after the join, so KiCad's connectivity does not flag it either.

### Reading of P3, P4, P5 verdicts (stricter reading where the text read two ways)
- P3: the mesh figure and the track-sum figure agree where both exist (ring VBAT to U11 pin 4: 92.18 and 93.66 mohm; ring VMOT: 205.26 and 210.55 mohm; band US 13 VMOT: 47.33 and 49.67 mohm). The mesh includes pads and via lands, the track-sum does not. 6 ring loads of VDD_1V8 and 14 band lines have no track-sum figure (the drawn-track graph did not reach both pads, mostly GND copper drawn as wide strokes); the mesh figure stands alone there. The via steps are the brief's 1 mohm per layer step; the ring has no figure for the barrel plating. The case boards' stackup is not in their board files; I used the design's own power_width.py line 3 (outer 35 um, inner 17.5 um), deviation D2.
- P3 VMOT sum: ring VMOT plus band VMOT plus band GND at US 13; the ring GND plane return is not solved (not asked), so the sum is a lower bound on the true loop; the sum stays far under the 264 mV limit (55.33 mV at 175 mA, table above).
- P4.4: the plan's own check (91.4 ohm at 0.100 / 0.075) is reproduced (logs/pilot_solver.log, expected_vs_found.log). The drawn pair is wider apart: gap 0.0778 mm at the tightest, 0.1387 median, 0.175 modal; Zdiff 92.10 / 101.90 / 104.70 ohm. The text of P4.4 did not say which gap; I took the stricter reading (all three inside 81 to 99), so FAIL. Under the min-gap reading alone it would be PASS.
- P5.XL1: the shortest drawn path pad to pad is 9.697 mm: 8.897 mm of track (equal to the 8.90 mm of board-notes-r3.md line 54) the last track end sits on the corner of the X2 pad 1 land, 0.794 mm from the pad centre (logs/dbg_xl2.log, logs/dbg_xl.log), and the path ends at the pad centre. By the frozen path rule FAIL; on track only (8.897 mm) it would be PASS.
- Cross-check of the clearances from the board file through pcbnew (logs/xcheck_clear.log, tracks, vias and pad outlines, zone fills excluded): antenna 0.122 mm (raster 0.125), XL1 0.0850 (0.0873), XL2 In1 0.0896 (0.0919), XL2 B.Cu 0.0911 (0.0939), XC1 0.1010 (0.105), XC2 0.1018 (0.103). The XL2 F.Cu figure differs (0.1376 against 0.0990) because the Gerber copper includes the L1 ground pour, which the cross-check leaves out. So the failures do not come from the raster.
- Already there: board-notes-r3.md line 54 states the crystal clearances 0.085 and 0.090 mm and "Plan d.4 (0.20 mm) is not met"; the same figures are found here from the fabrication files.
- Antenna reference (P4.3): two uncovered spots under the line draws: 255 pixels at x 101.928 to 102.043, y -99.663 to -99.568 (0.7 mm from ball C1) and 2846 pixels at x 90.643 to 91.243, y -105.958 to -105.843, which lies inside the plan's copper-free antenna zone (R2.0 point 2, X -13.60 to -8.75; the plan's ball C1 at X 2.698 is X 102.698 in the Gerber, so the offset is 100 and this cluster lies inside the zone; logs/limit_quotes2.log). The plan says both "L2 solid ground under the whole line" (d.1) and a copper-free zone there (R2.0): the plan disagrees with itself at the end of the line.
- Also found, not a pass line: the USB pair has L2 ground under only 16.877 percent of its pixels and 19144 pixels of other-net L2 copper under it (results/p4p5.json P4_3u), against plan d.2 "reference L2 solid"; its nearest other-net L1 copper is 0.0900 mm. The crystal lines are drawn on other layers than the plan says: XL1 only on L2, XL2 on L1, L2 and L4, XC1 and XC2 on L3 (plan d.4 says XL on L2 then L3).
- Antenna Z0 sensitivity to the dielectric constant (not on file for the 106 prepreg; plan value 4.1, the board file's stackup block also says 4.1): 50.38 ohm at 3.9 and 47.36 ohm at 4.5, both inside 45 to 55.

## 2. Deviations and changes after the freeze (each reason, and what it redid)
- D1 (pilot finding, before the P1 main run): the pin board's wire pads are named WP1 to WP7 in the fab data while the netlist names the wires W1 to W7; with only P1 to P4 and E1 expected, no net of case_pins had two pads, so a planted open could not show (logs/pilot_all.log before the fix). I added the pairing of build_boards.py line 61 (WP1 to W1 and so on) as expected pads. case_pins went from 5 to 10 pads compared; the earlier result is kept in results/v2_before_D1/.
- D2: the case boards' files hold no stackup block (M5 said to read it there). I used power_width.py line 3 (35 um outer, 17.5 um inner). The case P3 figures depend on it.
- D3: after the pilot showed that the first rasteriser (PIL polygon fill) made every track one pixel wider (about 3 percent too low a resistance against the analytic value on a straight test track; the log of that first pilot run, logs/pilot_solver.log, was overwritten by the rerun, so that raw record is lost and the figure is not repeated here), I replaced it with an exact pixel-centre rasteriser (mesh 1.0000; 45 degree test 1.0199). Redone with it: every P1 and P2 run, the pilots (pilot_scorer, pilot_all, hand_check, pilot_solver), all P3 and P4/P5 runs. Earlier logs and results are in logs/v1_pil_raster/ and results/v1_pil_raster/; no P1 result changed.
- D4: the drawn-track graph (used for lengths and the track-sum cross-check) was corrected five times after first runs showed paths missing: pad chords at zero resistance, flashes as nodes, snapping of end points within 3 um, joining overlapping lands, joining an end point lying inside another track. Earlier logs are in logs/v1_chord_R/. These changed only the cross-check figures and the lengths (XL1, XL2 got a path); the mesh resistances did not change.
- D5 (clarification of M2): PRT1 is not in the ring netlist; its pads were expected as pad 1 VBAT, pad 2 GND, pad 3 NTC (band-interface.md lines 111 to 113, build_band.py line 345).
- D6: the USB "nearest other-net copper" was first computed for D+ only (logs/v1_chord_R/p4p5_v6_usb_dp_only.log: 0.1200 mm); the board-file cross-check showed 0.0850 mm for the pair, so I redid it for both legs (0.0900 mm).
- D7: P4.4 and P5.XL1 readings as stated in section 1; they were not fixed in the freeze text.
- D8: the working tree of design/ecad/case was being edited by another agent while I ran (55 files differ from b9ec3cfa; logs/version_check.log). The case boards and netlist are therefore read from a git archive of b9ec3cfa extracted into readback-work/src_b9ec3cfa (a read of the repository, no write to it). The first case runs (working tree) are kept in logs/v3_worktree_case/ and results/v3_worktree_case/; they gave the same P1 figures and the same P3 case figures. The ring and band inputs have no difference between b9ec3cfa and the working tree (logs/version_check.log).
- Open finding (case_pins VRING, WP1 to P1): mesh 0.44 mohm against 2.15 mohm for the track sum, a factor of about five at sub-milliohm scale; cause not found; the verdict (0.17 mV from the mesh figure; the track-sum figure of 2.15 mohm is below 1 mV at 0.400 A; limit 901 mV for both boards) is the same under either figure.
- Not blind: the expectation file expected_vs_found.py was written after the runs from the design documents' own stated values (its first lines say so); the blind expectations were those of M9 and the pilot checks.
- Git: I ran no git write (the brief forbids it); the freeze text is saved as readback-work/board-readback_prereg_frozen_copy.md for the lead's commit; the pre-registration commit before the first run did not happen and the lead must commit.

## 3. What was not run, and why
- Route A (IPC-D-356) for the case boards and the 14 band boards: no .ipc356 in their fab/ folders; I did not export one.
- A broken-copy test on boards other than the ring (the brief asks for the ring only).
- The ring GND plane (not asked); ring VMOT sum therefore lacks the ring GND return.
- Ring VBAT drop: no written limit in the files read, so REPORT. Case cell lines: no written limit, REPORT.
- Wires, the cell, connector and pogo-pin contact resistance, and the cell tabs: not in fab files.
- Nothing measured on hardware. The dielectric constant 4.1 is the plan's assumption (a coupon measures it).
- The 14 flex*-drc.rpt files and check_band.py were not touched or run. No browser, no web request.

## 4. Proof files
Scripts, logs and results in design/wiring/readback-work/ (size in logs/misc_counts.log): logs/p1_*.log, logs/p3_*.log, logs/p4p5.log, logs/pilot_*.log, logs/hand_check.log (22 of 22 hand labels agree; labels in hand_labels.csv, excerpts in logs/hand_excerpts.log), logs/limit_quotes.log (the quoted limit lines), results/verdicts.json (every verdict with its source field), results/tables.md, CHECKLIST.md, the audit script audit.py with its output audit.log (its last line is quoted below).

### Last line of each proof file cited (verbatim, read by compose.py when this report was written)
- logs/p1_ring.log: `P1_DONE ring`
- logs/p3_ring.log: `P3_RING_DONE seconds 35.5`
- logs/p3_band.log: `P3_BAND_DONE`
- logs/p3_case.log: `P3_CASE_DONE seconds 2.3`
- logs/p4p5.log: `P4P5_DONE`
- logs/pilot_all.log: `PILOTALL flex2-us13 base shorts=0 opens=0 | planted open: ('USB_DP', 33.490176000000005, 1, 1) | planted short: ('VBAT', 'NTC', 0.322, 2, 1) | both shown: True`
- logs/pilot_scorer_rerun.log: `PILOT known-fail join LCD_SCK-LCD_MOSI   nets=84 pads=359 shorts=1 opens=0 missing=0 open_nets={} short_groups=[['LCD_MOSI', 'LCD_SCK']]`
- logs/pilot_solver.log: `PILOT 0.117 mm -> 49.99 ohm  (plan d.1: calculation gives 0.117 mm for 50.0 ohm)`
- logs/hand_check.log: `HAND agreement 22 of 22`
- logs/expected_vs_found.log: `EXPECT cases 20, differing 9`
- logs/p2_ipc_diff.log: `join B_Cu:        0 differing lines`
- logs/xcheck_clear.log: `XCHECK USB pair tracks vs other nets on F.Cu: min distance 0.0850 mm to GND (pad) near (104.400,105.200)`
- logs/xcheck_sw.log: `SWCHECK flex1-us13 SW5 footprint Alps_SKTAAAE010_pads34 pads ['3', '4']`
- logs/version_check.log: `P1 board=case_pins tag=None routeB nets=5 pads=10 shorts=0 opens=0 missing=0 absent_refs=['BT1', 'C1', 'C10', 'C11', 'C1`
- logs/audit_prev.log: `AUDIT done: claims checked numbers 1146 paths 175 quotes 16`

## 5. questions_for_owner
1. Should off-board references (cell BT1, screen DISP1, thermistor RT1) and the unsoldered switch terminals (SW pins 1 and 2 on four switches) count as "missing" in a fab-versus-netlist check, or be listed as known off-board parts? It decides whether P1 reads 17 of 17 or 8 of 17.
2. Which USB gap is the design gap, the plan's 0.075 mm or the drawn 0.14 to 0.175 mm? At 0.175 mm the pair is about 105 ohm differential, outside the plan's 90 ohm plus or minus 10 percent.
3. Is the antenna feed's reference to be solid under its last 0.6 mm (plan d.1) or copper-free (plan R2.0)?
4. What are the copper weights ordered for the case boards (I used 35 um outer, 17.5 um inner)?

RESULT: done, 1 of 5 pass lines met (P3) and 4 failed (P1, P2, P4, P5); by item 28 met, 18 failed, 25 reported only; no short or open on any of the 17 boards and both planted faults were found by the Gerber route.
