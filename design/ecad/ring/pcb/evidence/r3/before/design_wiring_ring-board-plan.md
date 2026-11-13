# Ring main board: stack, rules, ball escape, antenna mount, placement and routing method (package W2)

Written 2026-11-13 from 00:02 to 00:47 (clock: `date` on the Mac, CET). Writer: the W2 helper. No source file of the project was changed. Working files (scripts, measured tables, cut pages): `design/wiring/ring-board-plan-work/`.

Sources were read in the order of the brief. Short names used below:
- **NRF-PCB** = `design/datasheets/nrf54lm20x_caaa_ref_pcb_0_2.pdf` (Nordic reference layout of the main chip U1, 14 pages, scale 12:1). Its drawings are vectors. I did not read them only as pictures: `ring-board-plan-work/escape.py` and `trace.py` read every pad, track, hole and copper area of pages 1, 3, 4, 5, 6 to 10, at 0.029398 mm per PDF point (25.4 / 72 / 12), with the board frame of page 1 as origin. Output: `ring-board-plan-work/nordic-escape.csv` (one row per ball).
- **W1-PADS** = `design/ecad/ring/pcb/w1-evidence/u1-measured-pads.csv` (the ring-parts helper's 61 U1 land centres measured on NRF-PCB page 1, its log ends `RESULT PASS: 61 names matched 61 pads (59 on the 0.325 grid, C1 and D3 off it)`). My own extraction gives the same 61 positions (`ring-board-plan-work/q3.py`).
- **NPM-DS** = `design/datasheets/npm1304_datasheet_v1_0.pdf` (and its `.txt`).
- **JOH3, JOH5** = Johanson antenna datasheet `antenna_johanson_2450AT18D0100001E.pdf` page 3, and the 8-page copy `antenna_johanson_2450AT18D0100001E_8p.pdf` page 5.
- **NET** = `design/ecad/ring/netlist.csv` (398 rows, 93 nets), **PARTS** = `design/ecad/ring/parts.csv` (118 parts), **PLACE** = `design/mech/thin/placement.csv`.
- Maker capability pages (fetched with the fetch tool on 2026-11-13, no browser):
  - **PCBWAY-HDI** = https://www.pcbway.com/hdi-pcb.html
  - **PCBWAY-025** = https://www.pcbway.com/blog/News/Congratulations_on_the_Success_of_PCBWay_4_layer_Ultra_thin_0_25_mm_and_High_Den_9291acf1.html
  - **SUGA-AL** = https://suga-pcba.com/manufacturing-capabilities/advanced-pcb/hdi-any-layer/
  - **JLC** = https://jlcpcb.com/capabilities/pcb-capabilities (copy on disk: `design/datasheets/w5_jlcpcb_capabilities.html`)
  - **NEXT** = https://www.nextpcb.com/pcb-type/hdi-pcb

Footprints: the ring-parts helper's library `design/ecad/ring/pcb/OpenRing.pretty/` is used (notes `pcb/footprint-notes.md`). U1 is `WLCSP-61_nRF54LM20A-CAAA`: its 61 pad centres are identical to W1-PADS (compared by script: same 61 names, largest difference 0.0 mm), lands 0.200 round. U2 is `WLCSP-35_nPM1304-CAAA`: 7 columns at 0.419, 5 rows at 0.440, lands 0.225 round (the nominal ball, NPM-DS Table 35). The footprint notes call U1's grid "8 rows by up to 10 columns": those are the ball NAMES (rows A, B, D to H plus C1; numbers 1 to 10); the land centres lie on 7 physical rows and 9 physical columns at 0.325, with C1 and D3 off the grid, as a.1 says. The two descriptions are of the same 61 centres. Tail lands: band-interface.md section 2, not the J_BAND footprints of the library.

Coordinates: inside-model mm (PLACE), X along the finger (-X hand end), Y across: -Y is the joystick side with tail A, +Y the side of tail B and the antenna (main-board.md line 3; PLACE rows J_BAND_A, J_BAND_B), seen from the populated face. KiCad position = model + (100, 100), no mirror (`design/ecad/ring/pcb/board-notes.md` line 23). L1 is the populated face (KiCad F.Cu, toward the floor), the last layer faces the screen.

## Summary of the decisions

| Point | Decision |
|---|---|
| Copper layers and thickness | **Plan A (recommended): 4 copper layers, any-layer laser microvias, 0.267 mm over copper (calculation in c), 0.30 mm finished.** Keeps the block at 3.20 mm. Plan B (fallback, fixed now with its trigger in g): 6 layers any-layer, 0.433 mm over copper, block grows to at least 3.283 mm. 6 copper layers cannot be built at 0.30 mm from any published value I found (c.3). |
| U1 escape | 3 signal layers (L1, L2, L3); L4 is the ground plane under them; all vias laser microvias in the pad. Needs 3 balls left unconnected: E5 (SPARE_P1_19), E6 (MIC_B_CLK), E8 (SPARE_P1_01): their test pads TP10, TP20, TP7 go. With all 61 balls connected the escape needs 4 signal layers, as Nordic's own layout. |
| U2 escape | 2 layers: L1 (19 balls) and L2 (8 microvias in pad); 8 balls are no-connect. |
| Rules | track 0.10 mm, gap 0.075 mm (board minimum 0.065 / 0.065), laser microvia 0.10 mm drill on a 0.20 mm land (ring 0.05), stacked up to 3, all filled and plated over. No through via, no mechanical via. |
| Antenna | **[Replaced in Round 2, R2.0]** On the board, under face, at the hand-end corner on the +Y edge, long side along the edge, Johanson land pattern. The board notch is removed. Board copper keep-out X -13.6 to -9.45, Y 3.10 to 6.3 on all 4 layers. Needs from the body: the resin radio corner of the antenna study, extended to X -9.3, with a floor pocket 3.6 x 2.0 x 0.20 mm under the antenna. |
| Routing | scripted escapes, RF, USB pair, crystals and power first, locked; then Freerouting 2.5.0 for the rest; ends at KiCad DRC 0 violations and 0 unconnected. |

---

## a. Escape of U1 (nRF54LM20A, CSP 61, CAAA)

### a.1 Geometry, measured on Nordic's layout

Numbers below are measured on NRF-PCB with the scripts named above (not read by eye):

| What | Value | Where measured |
|---|---|---|
| Ball sites | 61 lands on 7 physical rows and 9 physical columns, pitch 0.325 mm both ways; C1 (ANT) sits 0.065 mm off its row, D3 (VSS) 0.07 mm off its column | NRF-PCB page 1; `q3.py` output, W1-PADS |
| Name to site | rows A, B, C/D (one physical row), E, F, G, H; physical column k carries the numbers 1, 2, 4, 5, 6, 7, 8, 9, 10 (number 3 is used only by D3). The physical site in row C/D, column 3 has no ball | W1-PADS; NET ball names |
| Body | 3.020 x 2.430 mm | NRF-PCB page 12 outline (W1 script `measure_u1.py`) |
| Land on L1 | round, 0.200 mm diameter | NRF-PCB page 1: the 61 lands are 0.2 mm round strokes |
| Gap between two neighbour lands | 0.325 - 0.200 = 0.125 mm | calculation |
| Microvia | 0.100 mm hole in a 0.200 mm land, ring 0.050 mm, placed in the ball land | NRF-PCB pages 1 to 5: 0.0998 mm white holes inside 0.2 mm lands |
| Nordic track width at the chip | 0.095 to 0.100 mm on L2 to L4, 0.1 to 0.229 mm on L1 | `trace.py` (column "tracks") |
| Nordic least track-to-land gap at the chip | L1 0.092, L2 0.096, L3 0.096, L4 0.097 mm | `trace.py` clearance pass |
| Layers Nordic uses at the chip | 8 copper layers; L1 to L4 carry the escape, pages 6 to 10 (L5 to L8) hold only one copper area each and the 73 through vias 0.4 / 0.2 mm, none inside the chip body | `escape.py`: L5 to L8 have 0 tracks |
| Nordic's via spans at U1 | in the body: 15 single L1-L2, 15 stacked L1-L3, 6 stacked L1-L4, 4 buried L3-L4, 2 L2-L3 | `spans.py` |

What fits between two lands or two vias (both are 0.200 mm round on 0.325 mm pitch):
- Gap 0.125 mm. One track of the finest published class needs 0.065 + 2 x 0.065 = 0.195 mm (0.065 / 0.065 mm: PCBWAY-HDI "0.065mm/0.065mm", SUGA-AL "0.065/0.065 mm fine production"). 0.195 > 0.125: **no track passes between two neighbour lands or two neighbour vias, on any layer.** Even SUGA-AL's selected 35/35 um needs 0.105 mm, which leaves 0.010 mm per side: not used.
- Two parallel tracks leaving neighbour sites in a straight line are 0.325 mm apart: gap 0.325 - 0.100 = 0.225 mm for a 0.100 mm track, against 0.075 needed. Fits.
- A track that passes an empty site between two vias has 0.650 - 0.200 = 0.450 mm: one 0.100 track with 0.175 mm each side.

So each layer can only take out the balls of the outermost ring that still has a via on that layer. Rings of the 7 x 9 site grid: ring 1 (28 sites, 27 balls: the B1 site is empty), ring 2 (20 sites, 20 balls with B2 and D3), ring 3 (12 sites, 11 balls: the C/D-3 site is empty), ring 4 (row E, columns 5, 6, 7: 3 balls). Four rings mean four signal layers if every ball is used. Nordic's layout uses exactly four: L1 26 balls (E1 by the top copper area), L2 14 plus two ground balls, L3 13 plus E8 and F8 (stub vias with no track), L4 5 (`nordic-escape.csv`).

### a.2 How the ring board does it with 3 signal layers

- L1: ring 1 less A1 and A2 (25 balls) plus B2, which leaves west through the empty B1 site between the A1 and C1 lands (gap 0.585 - 0.200 = 0.385 mm: a 0.100 track has 0.142 mm each side; Nordic does the same, `nordic-escape.csv` row B2).
- L2: ring 2, 18 signal balls, each by a microvia L1-L2 in its land, each track straight out through the ring 1 site in front of it (ring 1 sites have no via on L2). D3 (VSS) also drops to L2 by a microvia in its land and joins the L2 ground west of the body, under the C1 site, as in Nordic's layout (`nordic-escape.csv` row D3).
- L3: ring 3 and the one useful ring 4 ball, 11 balls by two stacked microvias in the land: D5 to D8 and F4 to F8 straight out; E4 north through the empty C/D-3 site (distance to the D3 land centre 0.253 mm; D3 has no copper on L3); E7 (PMIC_SCL) east through the E8 site, which is empty because E8 is not connected (gap to the D8 and F8 vias 0.325 - 0.100 - 0.050 = 0.175 mm). A1 and A2 (crystal) also go to L3, as in Nordic's layout, and run south inside the body along the column 1 and column 2 lines, which have no via on L3, so that the crystal lines lie between the L2 ground and the L4 plane (d.4).
- L4: the ground plane, no escape track.
- Signals that leave U1's west face south of the ANT ball (E2, F1, F2, G1) must cross the RF line (d.1): they cross on L3, under the L2 ground, by a stack 0.2 to 0.5 mm west of the body edge (rows E2, F1, F2, G1 of the table).
- Not connected: E5 (SPARE_P1_19), E6 (MIC_B_CLK), E8 (SPARE_P1_01). In NET they go to test pads TP10, TP20, TP7 only (NET rows `SPARE_P1_19 : TP10.1 U1.E5`, `MIC_B_CLK : TP20.1 U1.E6`, `SPARE_P1_01 : TP7.1 U1.E8`); no function uses them. Keeping them would need a fourth signal layer. They keep their land (the ball is soldered) and get no via and no track.
- The ground balls of ring 1 (A7, E1, F10) do not get a via in the land, and their ground stacks do not sit just outside the body either: the L2 track of B7 runs north along the line of A7, E2's runs west along the line of E1, F9's runs east along the line of F10, 0.325 mm apart, which leaves no room for a 0.200 via between two lines (0.200 + 2 x 0.075 + 0.100 = 0.450 > 0.325). Each leaves on L1 by a 0.15 mm track into the L1 ground copper, and that copper reaches L4 through stacks at least 1.0 mm from the body, where the escape lines have turned away (g.5 places them).

Count: L1 26, L2 19 (18 signals and D3), L3 13 (11 of rings 3 and 4, plus A1 and A2), not connected 3, total 61 (`tables.py` output).

Check that can fail: `ring-board-plan-work/check_escape.py` builds every land, via land and straight escape track of a.3 per layer and measures the least copper gap between different balls (pass line 0.075 mm). Its log `check_escape.log` ends `RESULT PASS least gap per layer [('L1', 0.109), ('L2', 0.123), ('L3', 0.123)]`. A broken copy that keeps E8 connected (`check_escape_broken_E8.py`) ends `RESULT FAIL least gap per layer [('L1', 0.109), ('L2', 0.123), ('L3', -0.15)]`: E7's track runs through E8's via.

**Are 6 copper layers enough for U1? Yes. Are 4 enough? Yes, with the 3 balls above left unconnected (3 signal layers plus one ground plane). With all 61 connected, 4 signal layers plus a plane are needed, which is 5 or more copper layers.**

Orientation: the footprint is W1-PADS as drawn (top view, +x right, +y down, A1 at x -1.302, y -0.978), placed at PLACE U1 (X 4.000, Y 0.000) with rotation 0, the same view as Nordic's page 1. Faces: row A faces -Y, row H faces +Y, column 1 faces -X (toward the antenna at the hand end), column 10 faces +X. I compared the four rotations by the weighted distance from the balls to the parts they serve (`ring-board-plan-work/rot.py`): rotation 0 scores 134.9, 90 138.8, 180 141.3, 270 136.0; rotation 0 is the lowest and is Nordic's own.

### a.3 Ball by ball

Columns: ball; name in the Nordic symbol; net in NET; land centre on the ring board (model X, Y); layer it leaves on; via; where the track goes; Nordic's reference for the same ball (layer it leaves the body on, via span and place), from `nordic-escape.csv`.

| Ball | Pin | Net | Land X, Y (mm) | Layer | Via | Escape | Nordic reference |
|---|---|---|---|---|---|---|---|
| A1 | XC2 | XC2 | 2.698, -0.978 | L3 | 2 stacked microvias L1-L2, L2-L3 in pad | L3, south (+Y) along the column 1 line X 2.698 inside the body (column 1 sites have no via on L3), out through the H1 site, to X1 (d.4) | L3 uvia:L1-L3 in pad |
| A2 | XC1 | XC1 | 3.024, -0.978 | L3 | 2 stacked microvias L1-L2, L2-L3 in pad | L3, south (+Y) along the column 2 line X 3.024 inside the body (B2, D3, E2, F2, G2 have no via on L3), out through the H2 site, to X1 (d.4) | L3 uvia:L1-L3 in pad |
| A4 | VDD | VDD_1V8 | 3.347, -0.978 | L1 | none | L1 direct, track leaves north (-Y) | L1 no via |
| A5 | DCC | DCC | 3.674, -0.978 | L1 | none | L1 direct, track leaves north (-Y) | L1 no via |
| A6 | DECD | DECD | 3.997, -0.978 | L1 | none | L1 direct, track leaves north (-Y) | L1 no via |
| A7 | VSS | GND | 4.323, -0.975 | L1 | none | L1, 0.15 mm track north (-Y) into the L1 ground copper; its stacks to L4 sit at least 1.0 mm outside the body edge, off every L2 and L3 escape line (g.5) | L1 uvia:L1-L2 in pad |
| A8 | DECA | DECA | 4.650, -0.978 | L1 | none | L1 direct, track leaves north (-Y) | L1 no via |
| A9 | P2.01 | SD_SCK | 4.973, -0.978 | L1 | none | L1 direct, track leaves north (-Y) | L1 no via |
| A10 | P2.00 | SPARE_P2_00 | 5.299, -0.978 | L1 | none | L1 direct, track leaves north (-Y) | L1 no via |
| B2 | DECRF | DECA | 3.024, -0.652 | L1 | none | L1 direct, track leaves west (-X) | L1 no via |
| B4 | P1.15 | DBG_TX | 3.347, -0.652 | L2 | microvia L1-L2 in pad | L2, north (-Y), straight through the row A site | L3 uvia:L1-L3 in pad |
| B5 | P1.16 | DBG_RX | 3.674, -0.652 | L2 | microvia L1-L2 in pad | L2, north (-Y), straight through the row A site | L3 uvia:L1-L3 in pad |
| B6 | P1.20 | XL1 | 3.997, -0.652 | L2 | microvia L1-L2 in pad | L2, north (-Y), straight through the row A site | L3 uvia:L1-L3 in pad |
| B7 | P1.21 | XL2 | 4.323, -0.652 | L2 | microvia L1-L2 in pad | L2, north (-Y), straight through the row A site | L3 uvia:L1-L3 in pad |
| B8 | P1.26 | PMIC_SDA | 4.650, -0.652 | L2 | microvia L1-L2 in pad | L2, north (-Y), straight through the row A site | L2 uvia:L1-L2 in pad |
| B9 | P2.03 | SPARE_P2_03 | 4.973, -0.652 | L2 | microvia L1-L2 in pad | L2, north (-Y), straight through the row A site | L2 uvia:L1-L2 in pad |
| B10 | P2.02 | SD_MOSI | 5.299, -0.652 | L1 | none | L1 direct, track leaves east (+X) | L1 no via |
| C1 | ANT | ANT1_NODE | 2.698, -0.393 | L1 | none | L1 direct, track leaves west (-X) | L1 uvia:L3-L4 in pad |
| D3 | VSS | GND | 3.094, -0.325 | L2 | microvia L1-L2 in pad | microvia L1-L2 in the pad into the L2 ground copper, joined west along its row under the C1 site (L2 is solid ground there: the RF reference, d.1) | no exit uvia:L1-L2 in pad |
| D5 | SWDCLK | SWDCLK | 3.674, -0.325 | L3 | 2 stacked microvias L1-L2, L2-L3 in pad | L3, north (-Y), straight through the row B and row A sites | L3 uvia:L1-L3 in pad |
| D6 | P1.22 | LCD_TE | 3.997, -0.325 | L3 | 2 stacked microvias L1-L2, L2-L3 in pad | L3, north (-Y), straight through the row B and row A sites | L4 uvia:L1-L4 in pad |
| D7 | P1.25 | MIC_B_DATA | 4.323, -0.325 | L3 | 2 stacked microvias L1-L2, L2-L3 in pad | L3, north (-Y), straight through the row B and row A sites | L4 uvia:L1-L4 in pad |
| D8 | P1.28 | PMIC_INT | 4.650, -0.325 | L3 | 2 stacked microvias L1-L2, L2-L3 in pad | L3, north (-Y), straight through the row B and row A sites | L3 uvia:L1-L3 in pad |
| D9 | P2.05 | SD_CS | 4.973, -0.325 | L2 | microvia L1-L2 in pad | L2, east (+X), along its row through the column 10 site | L2 uvia:L1-L2 in pad |
| D10 | P2.04 | SD_MISO | 5.299, -0.325 | L1 | none | L1 direct, track leaves east (+X) | L1 no via |
| E1 | VSS | GND | 2.698, -0.002 | L1 | none | L1, 0.15 mm track west (-X) into the L1 ground copper; its stacks to L4 sit at least 1.0 mm outside the body edge, off every L2 and L3 escape line (g.5) | no exit no via |
| E2 | nRESET | NRESET | 3.024, -0.002 | L2 | microvia L1-L2 in pad | L2, west (-X), along its row through the column 1 site (crosses the RF line on L3: via L2-L3 at X 2.00) | L2 uvia:L1-L2 in pad |
| E4 | SWDIO | SWDIO | 3.347, -0.002 | L3 | 2 stacked microvias L1-L2, L2-L3 in pad | L3, north (-Y) through the empty site of column 3 in row C/D (no ball there), between D3 and D5, then through the B4 and A4 sites | L3 uvia:L1-L3 in pad |
| E5 | P1.19 | SPARE_P1_19 | 3.674, -0.002 | none | none | not connected: land only, no via, no track (its test pad is removed, see h) | L4 uvia:L1-L4 in pad |
| E6 | P1.24 | MIC_B_CLK | 3.997, -0.002 | none | none | not connected: land only, no via, no track (its test pad is removed, see h) | L4 uvia:L1-L4 in pad |
| E7 | P1.27 | PMIC_SCL | 4.323, -0.002 | L3 | 2 stacked microvias L1-L2, L2-L3 in pad | L3, east (+X), along row E through the empty E8 site, then the E9 and E10 sites | L4 uvia:L1-L4 in pad |
| E8 | P1.01 | SPARE_P1_01 | 4.650, -0.002 | none | none | not connected: land only, no via, no track (its test pad is removed, see h) | no exit uvia:L1-L3 in pad |
| E9 | P1.29 | OLED_PWR_EN | 4.973, -0.002 | L2 | microvia L1-L2 in pad | L2, east (+X), along its row through the column 10 site | L2 uvia:L1-L2 in pad |
| E10 | VDD | VDD_1V8 | 5.299, -0.002 | L1 | none | L1 direct, track leaves east (+X) | L1 no via |
| F1 | P1.13 | MIC_A_CLK | 2.698, +0.324 | L1 | none | L1 direct, track leaves west (-X) (crosses the RF line on L3: stack L1-L3 at X 2.30) | L1 no via |
| F2 | P1.11 | MIC_A_DATA | 3.024, +0.324 | L2 | microvia L1-L2 in pad | L2, west (-X), along its row through the column 1 site (crosses the RF line on L3: via L2-L3 at X 2.00) | L2 uvia:L1-L2 in pad |
| F4 | P1.14 | SPARE_P1_14 | 3.347, +0.324 | L3 | 2 stacked microvias L1-L2, L2-L3 in pad | L3, south (+Y), straight through the row G and row H sites | L3 uvia:L1-L3 in pad |
| F5 | P3.03 | SPARE_P3_03 | 3.674, +0.324 | L3 | 2 stacked microvias L1-L2, L2-L3 in pad | L3, south (+Y), straight through the row G and row H sites | L3 uvia:L1-L3 in pad |
| F6 | P3.01 | MOTOR | 3.997, +0.324 | L3 | 2 stacked microvias L1-L2, L2-L3 in pad | L3, south (+Y), straight through the row G and row H sites | L3 uvia:L1-L3 in pad |
| F7 | P1.05 | LCD_CS | 4.323, +0.324 | L3 | 2 stacked microvias L1-L2, L2-L3 in pad | L3, south (+Y), straight through the row G and row H sites | L3 uvia:L1-L3 in pad |
| F8 | P1.02 | SPARE_P1_02 | 4.650, +0.324 | L3 | 2 stacked microvias L1-L2, L2-L3 in pad | L3, south (+Y), straight through the row G and row H sites | no exit uvia:L1-L3 in pad |
| F9 | P1.30 | SPARE_P1_30 | 4.973, +0.324 | L2 | microvia L1-L2 in pad | L2, east (+X), along its row through the column 10 site | L2 uvia:L1-L2 in pad |
| F10 | VSS | GND | 5.299, +0.324 | L1 | none | L1, 0.15 mm track east (+X) into the L1 ground copper; its stacks to L4 sit at least 1.0 mm outside the body edge, off every L2 and L3 escape line (g.5) | L1 no via |
| G1 | P0.08 | JOY_LEFT | 2.698, +0.648 | L1 | none | L1 direct, track leaves west (-X) (crosses the RF line on L3: stack L1-L3 at X 2.30) | L1 no via |
| G2 | P0.07 | JOY_DOWN | 3.024, +0.648 | L2 | microvia L1-L2 in pad | L2, south (+Y), straight through the row H site | L2 uvia:L1-L2 in pad |
| G4 | P3.05 | SPARE_P3_05 | 3.347, +0.648 | L2 | microvia L1-L2 in pad | L2, south (+Y), straight through the row H site | L2 uvia:L1-L2 in pad |
| G5 | P3.04 | SPARE_P3_04 | 3.674, +0.648 | L2 | microvia L1-L2 in pad | L2, south (+Y), straight through the row H site | L2 uvia:L1-L2 in pad |
| G6 | TXRTUNE | TXRTUNE | 3.997, +0.648 | L2 | microvia L1-L2 in pad | L2, south (+Y), straight through the row H site | L2 uvia:L1-L2 in pad |
| G7 | P1.06 | LCD_DCX | 4.323, +0.648 | L2 | microvia L1-L2 in pad | L2, south (+Y), straight through the row H site | L2 uvia:L1-L2 in pad |
| G8 | P1.04 | LCD_MOSI | 4.650, +0.648 | L2 | microvia L1-L2 in pad | L2, south (+Y), straight through the row H site | L2 uvia:L1-L2 in pad |
| G9 | P1.03 | LCD_SCK | 4.973, +0.648 | L2 | microvia L1-L2 in pad | L2, south (+Y), straight through the row H site | L2 uvia:L1-L4 in pad |
| G10 | P1.31 | JOY_RIGHT | 5.299, +0.648 | L1 | none | L1 direct, track leaves east (+X) | L1 no via |
| H1 | P0.06 | JOY_UP | 2.698, +0.974 | L1 | none | L1 direct, track leaves west (-X) | L1 no via |
| H2 | P0.04 | BTN_REC | 3.024, +0.974 | L1 | none | L1 direct, track leaves south (+Y) | L1 no via |
| H4 | P0.03 | JOY_CENTER | 3.347, +0.974 | L1 | none | L1 direct, track leaves south (+Y) | L1 no via |
| H5 | P1.07 | LCD_RST | 3.674, +0.974 | L1 | none | L1 direct, track leaves south (+Y) | L1 no via |
| H6 | D- | USB_DN | 3.997, +0.974 | L1 | none | L1 direct, track leaves south (+Y) | L1 no via |
| H7 | D+ | USB_DP | 4.323, +0.974 | L1 | none | L1 direct, track leaves south (+Y) | L1 no via |
| H8 | DECUSB | VDD_USB_3V3 | 4.650, +0.974 | L1 | none | L1 direct, track leaves south (+Y) | L1 no via |
| H9 | VBUS | U1_VBUS | 4.973, +0.974 | L1 | none | L1 direct, track leaves south (+Y) | L1 no via |
| H10 | P1.00 | SPARE_P1_00 | 5.299, +0.974 | L1 | none | L1 direct, track leaves south (+Y) | L1 no via |

Differences from Nordic, ball by ball (last column): Nordic takes B4 to B7 to L3 and D6, D7, E5, E6, E7 to L4; the ring board takes B4 to B7 to L2 and D6, D7, E7 to L3 and leaves E5, E6, E8 unconnected. Nordic grounds A7 with a microvia to L2; the ring board grounds A7 on L1 outside the body, because its L2 track B7 passes the A7 site. D3 is the same in both (microvia to L2). Nordic leaves E8 and F8 as stub vias to L3 with no track; the ring board routes F8 to its test pad TP8. Every other ball leaves on the same layer as in Nordic's layout. Nordic's C1 has an L3-L4 buried via under its land: that is a ground via between Nordic's L3 and L4 planes, not a connection of the ANT ball (L2 has no copper there).

---

## b. Escape of U2 (nPM1304, CSP 35, CAAA)

### b.1 Geometry

| What | Value | Source |
|---|---|---|
| Body | 3.0775 x 2.3775 mm (D x E, nominal) | NPM-DS page 155, Table 35 |
| Balls | 7 columns (1 to 7) at 0.419 mm (d), 5 rows (A to E) at 0.440 mm (e) | Table 35: D2 2.514 = 6 x 0.419, E2 1.76 = 4 x 0.44 |
| Ball diameter b | 0.195 min, 0.255 max | Table 35 |
| Land | round 0.225 mm (the nominal ball), solder mask opening = land | footprint `WLCSP-35_nPM1304-CAAA` (no mask margin set) |
| Gap between lands | 0.419 - 0.225 = 0.194 mm across columns, 0.440 - 0.225 = 0.215 mm across rows | calculation |
| One track between two lands | needs 0.195 mm at 0.065 / 0.065: 0.194 is short by 0.001 mm. **Not possible:** no track passes between two U2 lands | calculation, PCBWAY-HDI and SUGA-AL class |
| Nordic's CSP layout | 6 copper layers (NPM-DS pages 162 to 163, Figures 68 to 73); the outer ring leaves on the top layer, the inner 3 x 4 block has microvias in the land, Mid layer 1 carries most inner signals, Mid layer 2 a few, Mid layers 3, 4 and Bottom are ground with one track on Mid layer 4 | read from the pictures, NPM-DS pages 162 and 163 |
| Orientation on the ring board | footprint drawn as NPM-DS Figure 55 top view (A1 top left, columns 1 to 7 along x, rows A to E along y), at PLACE U2 (X 8.500, Y 0.000), rotated 90 degrees: footprint (x, y) goes to board (8.500 - y, x). Faces: column 7 (SW1, SW2, PVDD, PVSS1, PVSS2) faces +Y toward the two coils, column 1 (VBUS, VSYS, VBAT) faces -Y, row A faces +X, row E (I2C, VDDIO, VSET) faces -X toward U1 | with rotation 0 the two switching tracks would have to cross (B7 north of D7 on the +X face, the coils both at +Y); PLACE's box changes to 2.4 x 3.1 (h.1) |

### b.2 Escape plan

- L1: the 16 balls of the outer ring that are connected (A4 to A7, B1, B7, C1, C7, D1, D7, E1 to E5, E7; A1 to A3 and E6 are no-connect), plus B2, C2, D2, which join B1, C1, D1 on L1 because they carry the same net (VBUS, VSYS, VBAT). A copper bridge between two lands of the same net is allowed.
- L2: the 8 connected inner balls B4, B5, B6, C3, C6, D3, D4, D6, each by a microvia L1-L2 in the land. On L2 only these 8 vias exist in the U2 area, so every track leaves through an empty site (two microvia lands 0.419 apart leave 0.219 mm, still not used for a track; the lanes below never need it).
- No-connect, land only: A1, A2, A3 (LED0 to LED2), B3 (CC2), C4 (GPIO3), C5 (GPIO2), D5 (CC1), E6 (GPIO1) (NET: 8 pins of U2 with an empty net).
- Check: `ring-board-plan-work/check_escape_u2.py` (same method, lands 0.225, rotation of b.1); `check_escape_u2.log` ends `RESULT PASS [('L1', 0.194), ('L2', 0.219)]`.
- **U2 needs 2 layers (L1 and L2). Nordic's CSP layout uses 3 for signals (Top, Mid 1, Mid 2; read from the pictures, NPM-DS pages 162 and 163).**

| Ball | Pin | Net | Land X, Y (mm) | Layer | Via | Escape |
|---|---|---|---|---|---|---|
| A1 | LED0 | (no connect) | 9.380, -1.257 | none | none | not connected: land only |
| A2 | LED1 | (no connect) | 9.380, -0.838 | none | none | not connected: land only |
| A3 | LED2 | (no connect) | 9.380, -0.419 | none | none | not connected: land only |
| A4 | LSOUT1/VOUTLDO1 | VDD_MIC | 9.380, +0.000 | L1 | none | L1 east (+X) to C86 |
| A5 | LSOUT2/VOUTLDO2 | VDD_SD | 9.380, +0.419 | L1 | none | L1 east (+X) to C87 |
| A6 | AVSS | GND | 9.380, +0.838 | L1 | none | L1 east (+X), 0.15 mm, into the L1 ground copper; its stacks to L4 sit at least 1.0 mm east of the body, off the B6 line of L2 (g.5) |
| A7 | PVSS1 | GND | 9.380, +1.257 | L1 | none | L1 east (+X), 0.2 mm, to its own GND stack L1-L4 at (10.00, 1.26) (PVSS1, NPM-DS schematic note) |
| B1 | VBUS | VBUS | 8.940, -1.257 | L1 | none | L1 north (-Y), 0.25 mm; joined to B2 by a 0.15 mm copper bridge on L1; then on L3 (0.60) to tail B pad 4 |
| B2 | VBUS | VBUS | 8.940, -0.838 | L1 | none | joined to B1 on L1 (same net) |
| B3 | CC2 | (no connect) | 8.940, -0.419 | none | none | not connected: land only |
| B4 | LSIN1/VINLDO1 | VDD_1V8 | 8.940, +0.000 | L2 | microvia L1-L2 in pad | L2 east (+X) through the A4 site |
| B5 | LSIN2/VINLDO2 | VDD_3V0 | 8.940, +0.419 | L2 | microvia L1-L2 in pad | L2 east (+X) through the A5 site |
| B6 | VOUT1 | VDD_1V8 | 8.940, +0.838 | L2 | microvia L1-L2 in pad | L2 east (+X) through the A6 site |
| B7 | SW1 | SW1 | 8.940, +1.257 | L1 | none | L1 south (+Y) to Y 1.65, east along Y 1.65 to X 10.20, south to the west pad of L71 (11.00, 3.45); 0.15 mm, no via |
| C1 | VSYS | VSYS | 8.500, -1.257 | L1 | none | L1 north (-Y), 0.15 mm, to C75, C76, C77; joined to C2 on L1 |
| C2 | VSYS | VSYS | 8.500, -0.838 | L1 | none | joined to C1 on L1 (same net) |
| C3 | VBUSOUT | VBUSOUT | 8.500, -0.419 | L2 | microvia L1-L2 in pad | L2 north (-Y) through the C2 and C1 sites, to C73 |
| C4 | GPIO3 | (no connect) | 8.500, +0.000 | none | none | not connected: land only |
| C5 | GPIO2 | (no connect) | 8.500, +0.419 | none | none | not connected: land only |
| C6 | VOUT2 | VDD_3V0 | 8.500, +0.838 | L2 | microvia L1-L2 in pad | L2 south (+Y) through the C7 site |
| C7 | PVDD | VSYS | 8.500, +1.257 | L1 | none | L1 south (+Y), 0.15 mm, to C74 at (8.50, 2.15), between the two switching tracks |
| D1 | VBAT | VBAT | 8.060, -1.257 | L1 | none | L1 north (-Y), 0.15 mm; joined to D2 on L1; then on L3 (0.30) to tail B pad 1 and C85 |
| D2 | VBAT | VBAT | 8.060, -0.838 | L1 | none | joined to D1 on L1 (same net) |
| D3 | NTC | NTC | 8.060, -0.419 | L2 | microvia L1-L2 in pad | L2 west (-X) through the E3 site |
| D4 | SHPHLD | SHPHLD | 8.060, +0.000 | L2 | microvia L1-L2 in pad | L2 west (-X) through the E4 site |
| D5 | CC1 | (no connect) | 8.060, +0.419 | none | none | not connected: land only |
| D6 | GPIO0 | PMIC_INT | 8.060, +0.838 | L2 | microvia L1-L2 in pad | L2 west (-X) through the E6 site |
| D7 | SW2 | SW2 | 8.060, +1.257 | L1 | none | L1 south-west to (7.60, 1.72), south along X 7.60 to the west pad of L72 (8.50, 3.45); 0.15 mm, no via |
| E1 | VSET2 | VSET2 | 7.620, -1.257 | L1 | none | L1 north (-Y) to R72 |
| E2 | VSET1 | VSET1 | 7.620, -0.838 | L1 | none | L1 west (-X) to R71 |
| E3 | SCL | PMIC_SCL | 7.620, -0.419 | L1 | none | L1 west (-X), toward U1 E7 |
| E4 | VDDIO | VDD_1V8 | 7.620, +0.000 | L1 | none | L1 west (-X) |
| E5 | SDA | PMIC_SDA | 7.620, +0.419 | L1 | none | L1 west (-X), toward U1 B8 |
| E6 | GPIO1 | (no connect) | 7.620, +0.838 | none | none | not connected: land only |
| E7 | PVSS2 | GND | 7.620, +1.257 | L1 | none | L1 west (-X), 0.2 mm, to its own GND stack L1-L4 at (7.00, 1.26) (PVSS2, NPM-DS schematic note) |

PVSS1 (A7) and PVSS2 (E7) each get their own ground stack: NPM-DS schematic notes "Via to GND-layer on PVSS1" and "Via to GND-layer on PVSS2" (`npm1304_datasheet_v1_0.txt` lines 13788, 13789). AVSS (A6) has its own ground stack too.

---

## c. Layer stack, vias and rules

### c.1 What thin builds the makers publish

| Fact | Value | Source |
|---|---|---|
| Finished thickness range, HDI | 0.1 to 8.0 mm, "evaluation required for less than 0.2mm" | PCBWAY-HDI |
| A 4-layer HDI built and shipped at 0.25 mm | "4-layer first-order HDI ( 1 + 2 + 1 )", finished "0.25mm + / -0.025mm" (measured 0.247 mm), core 0.065 mm without copper, one sheet of 106 prepreg each side, inner copper 7 to 9 um, outer copper not more than 18 um, laser hole 0.1 mm, "Electroplated plug holes" | PCBWAY-025 |
| Any-layer HDI and thin builds | "Fine-pitch HDI fabrication from 1+N+1 through 7+N+7 and Any-Layer"; "4-layer, 0.25 mm ultra-thin HDI"; "0.35 mm BGA mobile Any-Layer" | SUGA-AL |
| Laser via | 0.10 mm standard, 0.075 fine; capture pad "Approximately 0.20 mm / 8 mil"; aspect ratio 0.75 to 0.8 : 1 recommended, 1 : 1 maximum; "Laser drilling accuracy is ±15 µm" | SUGA-AL |
| Laser via, second maker | "Standard 4 mil", minimum prepreg 0.06 mm for laser blind vias, minimum core 0.1 mm | PCBWAY-HDI (capability table and FAQ) |
| Track and gap | 0.065 / 0.065 mm | PCBWAY-HDI; SUGA-AL ("0.065/0.065 mm fine production") |
| Finished copper | 18 to 70 um | PCBWAY-HDI; SUGA-AL |
| Filled vias | "filled and plated", blind-via dimple 10 um or less | SUGA-AL |
| Solder mask bridge | 4 mil (0.1016 mm) green at 1 oz or less | SUGA-AL; PCBWAY-HDI |
| A large low-cost maker | thickness 0.4 to 4.5 mm; HDI laser via 0.075 to 0.15 mm; 0.1 / 0.2 mm via only for boards 1 mm or thinner | JLC (disk copy) |

No page I read gives a 6-layer board at 0.30 mm (search on 2026-11-13: no maker table lists a 6-layer any-layer board thinner than its general HDI range; NEXT gives no minimum).

### c.2 Plan A (recommended): 4 copper layers, any-layer, 0.30 mm

| Layer | Job | Copper | Dielectric to the next layer |
|---|---|---|---|
| L1 (F.Cu, populated face) | parts; U1 ring 1, U2 outer ring; RF feed line, USB pair, short local tracks; ground copper in free areas | 0.018 mm finished | 0.065 mm, one sheet 106 prepreg (PCBWAY-025) |
| L2 (In1.Cu) | U1 ring 2 and U2 inner escape; signals; ground copper everywhere else, solid under the RF line and the USB pair | 0.018 mm | 0.065 mm core (PCBWAY-025 core thickness) |
| L3 (In2.Cu) | U1 ring 3 and 4, crystal lines, screen bus, long signals, power (VDD_1V8, VDD_3V0, VBAT, VSYS) as wide tracks | 0.018 mm | 0.065 mm, one sheet 106 prepreg |
| L4 (B.Cu, screen face) | ground plane, solid, except the antenna keep-out; no part | 0.018 mm | solder mask over all |

- Thickness over copper: 4 x 0.018 + 3 x 0.065 = **0.267 mm**. Finished target with solder mask on both faces: **0.30 mm, tolerance +-0.025 mm** (the tolerance PCBWAY-025 states for its 0.25 mm 4-layer build). The 0.018 copper is the lowest finished copper both makers publish; any-layer builds plate every inner layer when its vias are filled, so I count 0.018 on every layer, more than PCBWAY-025's 7 to 9 um inner copper. Solder mask thickness is not published on the pages read: it is measured on the first lot (h.2).
- Block stack (architecture 17.2, line 426: floor 0.40, gap 0.05, parts 1.00, board 0.30, foam 0.10, screen 0.80, adhesive 0.10, glass 0.40, total 3.15, margin 0.05, block 3.20): **unchanged** at a 0.30 mm board. At the +0.025 tolerance limit the board is 0.325 and takes 0.025 of the 0.05 margin.
- Vias: every via is a laser microvia 0.100 mm drill, 0.200 mm land on each layer it touches, ring 0.050 mm, copper filled and plated over (SUGA-AL; PCBWAY-025 "Electroplated plug holes"). Spans built from them: L1-L2, L2-L3, L3-L4 (single), L1-L3 and L2-L4 (two stacked), L1-L4 (three stacked). Aspect ratio per via 0.065 / 0.100 = 0.65, inside SUGA-AL's 0.75 to 0.8 : 1. Ring 0.050 against SUGA-AL's +-15 um drill accuracy leaves 0.035 mm at the worst position; Nordic's own layout uses the same 0.2 / 0.1 via in the ball land (a.1). No through via and no mechanical drill on this board.
- Maker class to order: an any-layer HDI maker; the plan's numbers are taken from SUGA-AL (any-layer, 0.065 / 0.065, 0.10 laser, 0.20 capture pad) and PCBWAY-025 (the 0.25 mm 4-layer build and its dielectrics). The order states: 4 layers any-layer, the stack of this table, 0.30 +-0.025 finished, ENEPIG finish (the "nickel palladium gold" of PCBWAY-025's 0.25 mm build), green mask, vias filled and plated over, impedance coupons of d.1 and d.2, a cross-section coupon of one 3-high via stack.
- What it costs against 6 layers: one routing layer fewer (L1 to L3 for signals, L4 ground only), so the routing gate of g.8 decides; 3 test pads less (a.2); any-layer process instead of a 2-step build (higher board price; no price was asked, no supplier contacted).

### c.3 Why 6 layers cannot be 0.30 mm

Least 6-layer build from the published minimums: 6 copper layers x 0.018 (least finished copper, PCBWAY-HDI and SUGA-AL) + 5 dielectrics x 0.060 (least laser prepreg, PCBWAY-HDI FAQ) = 0.108 + 0.300 = **0.408 mm** over copper, before solder mask. That is 0.108 mm over 0.30.

### c.4 Plan B (fallback): 6 copper layers, any-layer, 0.433 mm

| Layer | Job | Copper | Dielectric below |
|---|---|---|---|
| L1 | parts and short tracks, as Plan A | 0.018 | 0.065 (106) |
| L2 | U1 ring 2, U2 inner, signals, ground copper | 0.018 | 0.065 |
| L3 | U1 ring 3 and 4, crystals, signals | 0.018 | 0.065 |
| L4 | ground plane | 0.018 | 0.065 |
| L5 | power (wide tracks) and signals | 0.018 | 0.065 |
| L6 | ground plane (screen face) | 0.018 | mask |

Thickness over copper 6 x 0.018 + 5 x 0.065 = **0.433 mm**, finished 0.46 +-0.04 mm (0.04 is my figure, 10 percent of 0.433 rounded up; no page gives a 6-layer tolerance). Block stack: 3.15 - 0.30 + 0.433 = 3.283 mm with no margin; at 0.46 finished, 3.31; with the 0.05 margin kept, **block 3.36 mm (+0.16)**. Same vias, rules and escapes as Plan A (L4 and L6 stay ground, so the 3 balls of a.2 stay unconnected in both plans and the netlist change is the same). L5 adds one routing layer for power and long signals.

Best plan that keeps 0.30: Plan A. It costs one routing layer and 3 test pads, and needs an any-layer maker.

### c.5 Design rules (one set, used by KiCad, the DSN and the order)

| Rule | Value | Why |
|---|---|---|
| Least track width (board) | 0.065 mm | PCBWAY-HDI, SUGA-AL |
| Least gap, copper to copper (board) | 0.065 mm | same |
| Net class Default | track 0.100, gap 0.075 | Nordic's chip area uses 0.095 to 0.100 tracks with 0.092 to 0.097 gaps (a.1); 0.075 keeps 0.010 over the maker minimum |
| Net class RF | track 0.120, gap 0.200 | d.1 |
| Net class USB | track 0.100, gap 0.075 inside the pair, 0.200 to other copper | d.2 |
| Net class PWR | track 0.150 on L1, 0.300 on L3, gap 0.100 | d.5 |
| Microvia (every via) | drill 0.100, land 0.200 | c.2 |
| Least annular ring | 0.050 mm | (0.200 - 0.100) / 2; fixes the trial's 116 "annular_width" errors, which came from a 0.1 ring rule with 0.25 / 0.15 vias (`probe/route-probe.md` finding 1) |
| Least via diameter | 0.200 mm; least hole 0.100 mm | c.2; fixes the trial's "via_diameter" and "drill_out_of_range" errors on 0.2 / 0.1 vias (finding 4) |
| Hole to hole | 0.200 mm | two vias on the 0.325 pitch have 0.225 mm between holes; Nordic builds exactly this |
| Copper to board edge | 0.100 mm in the KiCad rule, plus a 0.15 mm keep-out band drawn inside the outline for the router (g.4) | project value kept; the band stops Freerouting from reaching the edge (trial finding 3) |
| Solder mask | U1 lands: opening = land (0.200, no expansion), bridge 0.125; U2 lands 0.225 with opening = land, bridge 0.194; other parts 0.025 expansion | SUGA-AL bridge 0.1016 mm green |
| Courtyards | library courtyard, 0.10 mm margin | `board-notes.md` line 27 |

---

## d. Controlled lines

Impedance numbers come from `ring-board-plan-work/zcalc.py`: Hammerstad-Jensen microstrip with Wheeler's thickness correction; edge-coupled pair by the IPC-2141 form Zdiff = 2 Z0 (1 - 0.48 e^(-0.96 s / h)). Inputs: copper 0.018 mm, dielectric constant 4.1 (JLC: "3313 Perpreg 4.1"; no page I read gives the value for 106 prepreg, so the coupons of h.2 measure it).

### d.1 Antenna feed, 50 ohm [values replaced in Round 2, R2.0]

- Line on L1, reference L2 (h 0.065 mm): **width 0.120 mm** (calculation gives 0.117 mm for 50.0 ohm; at 0.120, 49.3 ohm; effective dielectric constant 3.14). Copper of L1 beside it kept 0.200 mm away (more than 3 h = 0.195, so the formula of a plain microstrip holds). L2 solid ground under the whole line and 0.50 mm each side; no L2 track crosses under it. Ground stacks L1-L4 on both sides every 1.0 mm, 0.30 mm from the line edge.
- Nordic uses L3 as the reference with L2 cleared (NRF-PCB: no L2 copper under C1 and the line, `trace.py`); on this thinner stack L2 is the reference and is kept solid.
- Route (fixed): U1 C1 land (2.698, -0.393) west on L1 through the chip match L2, C3, L3, C12 (f.1) to (0.50, -0.39); south along X 0.50 to (0.50, 3.30); west along Y 3.30 to (-7.20, 3.30); 45 degrees to (-7.40, 3.50); north (+Y) along X -7.40 to (-7.40, 5.70); 45 degrees to (-7.60, 5.90); west along Y 5.90 past C89, L4 and C13 (e.4) into antenna land pin 1 at (-10.00, 5.90). Length 2.20 + 3.69 + 7.70 + 0.28 + 2.20 + 0.28 + 2.40 = 18.8 mm (the legs; the chip match parts sit on the first). Bends: 45 degree chamfers, no right angle. On L1 the line passes 0.34 mm under U11's courtyard (U11 from Y 3.70), above U3's (to Y 3.20), and 0.24 mm from the far-row lands of J_BAND_B (land edge Y 3.60, band-interface.md section 2), more than the 0.20 RF gap. Over X -3.60 to -0.90 the stitching row on the +Y side of the line is left out (no via in the tail keep-out); the -Y row stays. Every signal that must cross the line crosses on L3.

### d.2 USB D+ and D- (USB_DP, USB_DN) [values replaced in Round 2, R2.0]

- Pair on L1, reference L2 solid: **track 0.100, gap 0.075 inside the pair: 91.5 ohm differential, 54.4 ohm each line** (zcalc.py). Target 90 ohm.
- Route: U1 H6 (D-) at (3.997, 0.974) and H7 (D+) at (4.323, 0.974), south (+Y) on L1, a 0.40 mm jog east at Y 1.60 (west of the H8 and H9 tracks, which run south-east to C10, R1, C11), then straight south between X1 and X2 (X2 moves to X 6.00, h.1: the gap between their pads becomes about 0.8 mm, and the pair with 0.20 mm each side needs 0.675), to Y 4.30, west into U9 at (2.90, 5.15) (flow-through over its pins 2, D-, and 1, D+), then west along Y 5.98 (D+ on the edge-side line Y 6.065, D- on the inner line Y 5.89); D- turns -Y at X -2.505 into land 5 (-2.505, 4.775) and D+ goes on to X -3.015 and turns into land 6 (-3.015, 4.775) (band-interface.md section 2), so the two lines never cross. D+ is then 0.51 mm longer: a serpentine on D- beside U9 takes up the difference to within 0.10 mm. Beside C83 the pair keeps 0.14 mm to its pads (more than 0.075, less than the 0.20 class gap, over 1.0 mm of length). U9 sits 5.1 mm from the J_BAND_B pads (sch-notes 11.2 item 4 asks for "next to"; the ribbon fold zone and U11, C83, C84 hold the closer area).
- Length match inside the pair: 0.10 mm or less (my rule). No via in the pair. Stub to U9: through its pads (flow-through), no branch.

### d.3 Screen bus

LCD_SCK (G9), LCD_MOSI (G8), LCD_DCX (G7), LCD_CS (F7), LCD_TE (D6), LCD_RST (H5) to J1 positions 10, 12, 11, 9, 7, 8 (NET). Not impedance-controlled (a short SPI bus); on L2 and L3, each with a ground layer next to it (L2 tracks over L3 copper areas or L1 ground; L3 tracks under L2 ground and over L4). LCD_SCK keeps 0.20 mm to any other signal over its whole length. Length from U1 to J1 at most 20 mm each (U1 at X 4, J1 at X -12: 16 mm straight).

### d.4 Crystals

- 32 MHz (X1 at 3.0, 3.0, PLACE): XC1 (A2) and XC2 (A1) on L3, between the L2 ground and the L4 plane, width 0.100, 0.20 mm from any other L3 copper, length 6.0 mm or less each, the two lengths within 0.5 mm. Path (a.3 rows A1, A2): south inside the body along X 2.698 and X 3.024, out through the H1 and H2 sites, into X1 pads 1 and 3 by stacked vias L3-L2-L1 in the X1 pads (about 3.5 to 4.5 mm). L1 copper under X1: ground only.
- 32.768 kHz (X2 at 6.0, 3.0, moved from 5.5, h.1): XL1 (B6) and XL2 (B7) leave on L2 north (a.3), turn at Y -1.6, cross to L3 by a microvia L2-L3 0.3 mm outside the body, run east of the body and south on L3 to X2 pads 1 and 2 (stacked vias in the pads). Width 0.100, 0.20 mm from any other copper of the same layer, length 9 mm or less each.
- These lengths are longer than Nordic's (its crystals are beside the chip, NRF-PCB page 1), because PLACE fixes X1 and X2 south of U1 while the crystal balls face north and west. The effect is measured on the first unit (h.2: frequency offset at 32 MHz and start-up of the 32 kHz oscillator).

### d.5 Power paths and widths

Track width for 10 C rise by IPC-2221 (I = k dT^0.44 A^0.725, k 0.048 outer, 0.024 inner, A in square mil; `ring-board-plan-work/zcalc.py` and the run of 00:22), copper 0.018 mm:

| Current | L1 (outer) | L2, L3 (inner) |
|---|---|---|
| 0.1 A | 0.024 mm | 0.063 mm |
| 0.2 A | 0.063 mm | 0.165 mm |
| 0.3 A | 0.111 mm | 0.289 mm |
| 0.5 A | 0.225 mm | 0.584 mm |

| Net | Design current | Source of the current | Width L1 / L2-L3 | Vias where it changes layer |
|---|---|---|---|---|
| VBUS (tail B pad 4 to U2 B1, B2; R1; U9) | 0.5 A | NPM-DS line 752: limits IBUS100MA and IBUS500MA; the ring sets 100 mA, 0.5 A is the next setting | 0.25 / 0.60 | 4 stacks |
| VBAT (tail B pad 1 to U2 D1, D2, U11 pin 4, U4 A1) | 0.3 A | 228 mA at a motor start with every other load on (architecture.md line 508, item S12) | 0.15 / 0.30 | 3 stacks |
| VSYS (U2 C1, C2, C7 and C74, C75, C76, C77, C88) | 0.2 A | VSYS up to 100 mA (NPM-DS line 18); buck input pulses: 0.2 A | 0.15 / 0.30 (kept on L1, short) | 2 stacks |
| SW1, SW2 (U2 B7, D7 to the coils) | 0.2 A | two 200 mA bucks (NPM-DS line 30) | 0.15 on L1 only | none (no via in a switching node) |
| VDD_1V8, VDD_3V0 (buck outputs) | 0.2 A | same | 0.15 / 0.30 | 2 stacks per layer change |
| VDD_MIC, VDD_SD (load switches) | 0.1 A | "Two 100 mA Load switches" (NPM-DS line 31) | 0.10 / 0.10 | 1 stack |
| VMOT (U11 pin 1 to tail A pad 7) | 0.3 A | same motor start as VBAT | 0.15 / 0.30 | 3 stacks |
| ELVDD, ELVSS (U4 to J1) | 0.1 A | no current on file for the screen; 0.1 A is my figure for a 0.95 inch panel, checked on the unit (h.2) | 0.10 / 0.15 | 2 stacks |
| GND | all returns | | L4 plane; L2 copper; L1 copper in free areas; every ground pad its own stack within 0.4 mm | |

Inside a ball field a power track may neck to the land width (0.100) for at most 0.5 mm.

---

## e. Antenna mount (one fixed design)

Facts that fix it:
- The antenna is 3.20 x 1.60 x 1.20 mm (JOH5 page 2 / 5-page copy page 2: L 3.20, W 1.60, T 1.20). Only 1.00 mm is free under the board (architecture 17.2), which is why the model put it in a notch with its pads off the board (architecture line 443; S15, line 513).
- Johanson's land pattern: four lands 1.0 x 0.6 mm, 1.0 / 2.0 / 1.0 mm across and 0.6 / 0.7 / 0.6 mm deep (JOH3; antenna-study.md section 2). Pins 1 and 4 are at one end (feed end), pins 2 and 3 at the other; pin 1 FEED, pins 2, 3, 4 GND, "Can be swapped" with pin 4 as alternate feed (5-page copy page 2, terminal configuration).
- Ground clearance: evaluation board 4.0 wide x 6.0 deep from the edge (JOH3); "thin edge" 8 mm along the edge x 3.4 mm deep, 1.5 mm of it below the lands, an L/C part "to adjust the initial frequency" at the far end (JOH5); "no other metallic components like batteries and displays directly underneath antenna" (JOH5, circular board note). A pi (or shunt-series-shunt) network beside the feed (JOH5 note 5).
- The body around it today: metal 0.050 under, 0.225 and 0.450 beside (antenna-study.md section 1).

The design:
1. **[Replaced in Round 2, R2.0]** **Place:** on the board's under face (L1, like every part), hand-end corner, +Y edge, long side along X. Lands (copper, 1.0 x 0.6 each): far end X -13.50 to -12.50, feed end X -10.50 to -9.50; edge row Y 5.60 to 6.20, inner row Y 4.30 to 4.90 (0.10 from the board edge at Y 6.30 and X -13.60). Antenna body X -13.10 to -9.90, Y 4.45 to 6.05, centre (-11.50, 5.25).
2. **Pins:** the library footprint (`ANT_Johanson_2450AT18D0100001E_3.2x1.6`) has pin 1 at (-1.5, -0.65), pin 2 at (1.5, -0.65), pin 3 at (1.5, 0.65), pin 4 at (-1.5, 0.65): pins 1 and 4 share one end. It is placed at (-11.50, 5.25) rotated 180 degrees, so that end is the feed end at +X. Feed-end edge land (-10.00, 5.90) = pin 1 FEED, net RF_FEED. Feed-end inner land (-10.00, 4.60) = pin 4, GND, by a 0.15 mm track east to a ground stack at (-9.20, 4.40), outside the keep-out. Far-end lands (-13.00, 5.90) = pin 2 and (-13.00, 4.60) = pin 3, joined on L1, then to the new frequency trim part LT1 (0201) at (-13.00, 3.60), whose other pad goes by a 0.15 mm track to a ground stack at (-13.40, 2.95), just outside the keep-out (land top Y 3.05) and 0.08 mm from J1's nearest mounting pad corner (f.4). LT1 starts fitted as 0 ohm (pins 2 and 3 grounded, the datasheet's normal function); the bench changes it (h.2).
3. **[Replaced in Round 2, R2.0]** **Keep-out (rule area, all 4 layers, no copper, no pad except the antenna's own lands, LT1 and their tracks):** X -13.60 to -9.45, Y 3.10 to 6.30. Its depth is 3.20, 0.20 less than the "thin edge" depth 3.40 of JOH5, because the screen connector J1 (6.1 mm housing, f.4) and microphone U5 leave no more room in Y; 1.20 of it lies below the inner lands (JOH5: 1.5). Its length on the board is 4.15 mm; beyond the board end the clearance continues in the resin corner (item 6) to the outer skin at X -14.8. JOH5's 8 mm length is not reached on the board: the board ends at X -13.6. The difference goes to the bench (h.2, return loss and signal).
4. **Match parts:** at the chip, as Nordic (NRF-PCB page 1: L2, L3, L4 in a row beside the ANT ball, C3, C12 shunts below them): **[Replaced in Round 2, R2.0 item 3]** L2 series at (1.70, -0.39), C3 shunt at (1.10, -1.31, rotation 90), L3 series at (0.48, -0.39), C12 shunt at (-0.12, -1.31, rotation 90), each shunt to its own ground stack. At the antenna, a pi, all 0201, courtyards at pad extents + 0.10 mm (as `board-notes.md` line 27): C13 (not fitted) shunt at (-9.10, 5.15), long side along Y, its courtyard 0.10 mm east of the keep-out edge; L4 series at (-8.45, 5.90), long side along X; C89 (new, not fitted) shunt at (-7.85, 5.15), long side along Y. Each shunt's upper pad joins the line by a 0.12 mm stub of 0.25 mm; its lower pad goes to its own ground stack. No two courtyards overlap (C13 X -9.35 to -8.85, L4 X -8.93 to -7.97 at Y 5.65 to 6.15, C89 X -8.10 to -7.60, both shunts Y 4.67 to 5.63). Values: PARTS (Nordic's CAAA list), retuned on the unit (h.2).
5. **Feed line:** d.1.
6. **What the antenna needs from the body (requirements):**
   - **[Replaced in Round 2, R2.0]** R1: the body inside X -14.80 to -9.30, Y 2.05 to the outer skin, all Z, is the resin radio corner, no metal coat, no metal print on the glass over it. Source: antenna-study.md section 5 (the corner X -14.8 to -10.6), extended from X -10.6 to X -9.3 because the antenna body now reaches X -9.90 (item 1); 0.60 mm more is kept beyond it.
   - **[Replaced in Round 2, R2.0]** R2: a pocket in that resin floor under the antenna: X -13.30 to -9.70, Y 4.25 to 6.25, depth 0.20 mm (floor top Z 0.40 to Z 0.20). The board's under face is at Z 1.45 (PLACE PCB1 centre Z 1.60, 0.30 thick), so the antenna bottom is at 1.45 - 1.20 = Z 0.25; 0.05 above the pocket bottom; 0.20 mm of resin under it. The panel pocket wall is at Y 6.45 (thin-notes line 21: panel pocket 12.9 wide), 0.20 beyond the pocket.
   - R3: no part of the screen panel, tail or J1 inside X -13.60 to -9.45, Y 3.10 to 6.30 on the board face (J1's housing ends at Y 2.90 at its new place, f.4). The screen's ledge above the board stays as an open point of the screen maker (antenna-study.md section 5).
   - "Resin corner" open point: decided here as kept and extended (R1, R2). The bench test T0 / T1 / T2 of antenna-study.md section 6 stays as written; with the antenna on the board, T1 (all metal) cannot be built without R2's pocket, so T1 uses a metal body with the same pocket.
7. **Board outline change:** the 1.8 x 3.6 notch is removed; the board is the full 27.2 x 12.6 rectangle with 0.8 corners (main-board.md point 4 already closes the joystick notch; `board-notes.md` line 22 still draws a 2.8 x 0.6 notch: it is removed too).

---

## f. Placement zones

### f.1 Zones [values replaced in Round 2, R2.0]

Fixed by PLACE (kept): U1 (4.0, 0.0), U2 (8.5, 0.0), U4 (4.0, -3.5), L10 (6.5, -3.5), X1 (3.0, 3.0), U3 (-5.0, 0.0), U5 (-10.8, -4.8), U6 (10.8, -4.8), J1 (-12.0, 0.0), U11 (0.0, 4.2), C83 (0.0, 5.45), C84 (1.2, 5.0). Changed (h.1): ANT1 (e); U2 rotated 90 degrees on its place (b.1); L71 and L72 swap places and move 0.25 mm to +Y (L71 to (11.0, 3.45), L72 to (8.5, 3.45), same size), so that each switching node reaches its coil without crossing the other and C74 fits between U2 and L72 (U2 table rows B7, C7, D7); X2 moves from X 5.50 to X 6.00 (same Y 3.0) to open the USB lane (d.2). None of these changes a part height, and each part stays inside the board outline, so the block stack does not change; the 3D fit check reruns on the new positions (g.1). Keep-free: the tail keep-outs X -3.50 to -1.00, Y +-3.40 to +-5.60 (band-interface.md section 2, fixed); antenna keep-out (e.3).

| Zone | Area (model mm) | Parts | Reason |
|---|---|---|---|
| Z1 chip north strip | X 2.4 to 6.0, Y -2.4 to -1.35 | L1 (DCC, at A5), C6, FB1, C7, C14 (DECA, DECRF), C4, C5 (VDD A4) | Nordic places them at the chip's row A side (NRF-PCB page 1); A4, A5, A6, A8 face -Y |
| Z2 chip west strip | X 0.6 to 2.45, Y -0.9 to 0.1 | L2, C3, L3, C12 (e.4) | Nordic places the match in a row beside the ANT ball (NRF-PCB page 1) |
| Z3 chip south strip | X 2.4 to 6.5, Y 1.35 to 2.15 | R2 (TXRTUNE, G6), C10 (DECUSB, H8), R1 and C11 (VBUS, H9) | the H row faces +Y; X1 begins at Y 2.2, X2 at Y 2.4; X 4.15 to 4.95 stays free of parts for the USB pair (d.2) |
| Z4 chip east strip | X 5.6 to 7.1, Y -1.6 to 1.6 | C1, C2 (VDD E10), R57, R58 (I2C pull-ups), R71, R72 (VSET1, VSET2 at U2's row E face) | E10 faces +X; U2's courtyard begins at X 7.21 |
| Z5 power chip | U2 (courtyard X 7.21 to 9.79, Y -1.64 to 1.64 after the rotation) and a band of about 1 mm round it | north (column 1 face, X 7.2 to 9.8, Y -3.2 to -1.64): C71, C72 (VBUS, B1), C85 (VBAT, D1), C73 (VBUSOUT, C3); east (row A face, X 9.8 to 11.65, Y -1.5 to 2.45): C86 (A4), C87 (A5), C75, C76, C77 (VSYS by L3); south between the switching tracks: C74 at (8.50, 2.15) (PVDD, C7); south of the coils (X 7.9 to 12.4, Y 4.45 to 6.2): C78 (VDD_1V8 at L72's output), C79 (VDD_3V0 at L71's output), C80, C88 (0603) | NPM-DS 9.3.4: capacitors "as close as possible to the supply pins". Capacity: these 16 parts need 17.9 mm2 of library courtyard (0402 1.292, 0201 0.667, 0603 2.839); the band round U2 holds about 16.5, so the 4 output-side parts (6.1 mm2) go to the coil outputs, in 7.9 mm2 |
| Z6 coils | L72 at (8.5, 3.45), L71 at (11.0, 3.45) | buck coils | PLACE positions swapped and moved 0.25 to +Y |
| Z7 microphone 1 support | X -8.7 to -4.0, Y -6.2 to -3.2 | C35 (0805) at (-7.15, -4.80), long side along X; R31 at (-5.20, -4.40); C31 at (-5.20, -5.40) (2.4 mm from U5, Class 2 away from the microphone) | f.4 |
| Z15 storage support | X -0.9 to 2.4, Y -6.2 to -1.4 (east of the J_BAND_A keep-out) | U10, C81, C82, R60, R63, R64, R65, C60, C61; C24 and R66 of the screen supply | beside U3's east pad column (U3 footprint pads 5 to 8 at X -1.5, Y -1.9 to +1.9), so the card lines SDC_* are short |
| Z8 antenna end | X -9.45 to -7.45, Y 3.5 to 6.2 | C89, L4, C13; LT1 inside the keep-out at (-13.0, 3.4) | e |
| Z9 tail B end | X -0.9 to 4.3, Y 3.7 to 6.2 (east of the ribbon fold zone) | U11, C83, C84 (fixed); U9 at (2.90, 5.15), long side along X | U9 as near J_BAND_B as the fold zone and U11 allow (d.2) |
| Z10 tail lands (fixed by the band helper) | J_BAND_A and J_BAND_B: 2 rows x 4 columns of lands 0.30 x 0.55, columns X -3.015, -2.505, -1.995, -1.485, rows at Y +-3.875 and +-4.775; keep-out for parts and holes X -3.50 to -1.00, Y +-3.40 to +-5.60 (no via inside it) | lands only | `design/ecad/band/band-interface.md` section 2; exits in f.3 |
| Z11 microphone 2 | north and west of U6 | C36 (0805) at (11.35, -2.37), long side along X; R32 at (8.28, -4.80), long side along Y, in the 0.85 mm strip between L10 and U6; C32 at (6.60, -1.95) (2.6 mm from U6) | f.4; Knowles: no Class 2 capacitor near the microphone (sch-notes 12.1 item 17) |
| Z12 screen supply | X 2.4 to 8.0, Y -6.2 to -4.6 and around U4 | C21, C22, C23, C26, C27 (C24, R66 in Z15; C25, C28, C29 at J1) | U4 and L10 fixed there |
| Z13 screen connector | around J1 | C25 (ELVDD), C28, C29 (ELVSS) | at the panel's supply pins |
| Z14 test pads | 6 pads in a 3 x 2 grid at X -6.70, -5.80, -4.90 and Y 4.30, 5.25 (TP1 to TP6; 0.24 mm from the RF line's rise at X -7.40); 8 pads in a 2 x 4 grid at X 12.15, 13.05 and Y -1.10, -0.20, 0.70, 1.60 (TP11 to TP18; 0.05 mm clear of C36's courtyard, 0.55 of L71's); 5 pads in a row at Y 5.60, X 4.70, 5.60, 6.50, 7.40, 12.90 (TP19, TP8, TP9, TP22, TP21) | 19 pads of 0.8 mm | free areas; K-A1 (only reachable before the board goes into the body) |
| C21 | in Z12 at U4's A1 (VBAT input of U4) | | U4 input capacitor (NET: C21 on VBAT) |

### f.4 The screen connector J1 and the two 0805 capacitors: do they fit? [values replaced in Round 2, R2.0]

Facts: J1 housing 6.1 mm along the contact row (Hirose catalogue p3, dimension A for 15 contacts), land rows 3.6 mm apart outer edge to outer edge (catalogue p4, B; footprint pads at local y +1.4 (0.8 long) and -1.475 (0.65 long)), mounting pads 0.4 x 0.95 at local x +-2.8; the library footprint's courtyard is 6.6 x 4.2 (`FPC_Hirose_FH35C-15S-0.3SHW.kicad_mod`). Catalogue p3 top view gives the closed housing depth as (3.35); the (4.2) is in the side "Detail drawing", where the flip lever stands open at 90 degrees (both read from the picture, catalogue page 3). C35, C36: Murata GRM2195C1H104JA01D, 0805, 2.0 x 1.25 x 0.85, courtyard 3.1 x 1.65 (`Chip_0805.kicad_mod`).

**J1 fits, after three changes:**
- X: at PLACE's X -12.0 the outer land edge is at -12.0 - 1.80 = -13.80, 0.20 mm outside the board end (X -13.60). The lands need a centre at X -13.60 + 0.10 + 1.80 = -11.70 or more. **J1 moves to X -11.65** (lands X -13.45 to -9.85; closed housing about X -13.33 to -9.98, inside the board).
- Y: the room is between microphone U5's courtyard (Y -3.20; U5 body 4.0 x 3.0 at Y -6.3 to -3.3) and the antenna keep-out. With the housing (6.1) centred at **Y -0.15**, it spans Y -3.20 to 2.90: it touches U5's courtyard (overlap 0) and the antenna keep-out starts 0.20 mm beyond, at Y 3.10 (e.3, 0.20 shallower than JOH5's 3.40). The +Y mounting pad's copper ends at Y -0.15 + 2.80 + 0.20 = 2.85.
- Courtyard: the library courtyard (6.6 x 4.2, centred) overlaps U5's by 0.25 and the antenna keep-out by 0.25 at this place. It must be the closed housing, 6.1 x 3.35 (h.1). The open lever (4.2 deep) appears only while the screen tail is plugged in, before the board goes into the body.
- The +X side: J1 ends near X -9.98, U3's courtyard starts at X -9.10: 0.88 mm, room for C25, C28, C29 (Z13).

**C35 and C36 (0805) fit, but not "next to the Vdd pin":**
- No room touches the microphones on the side of their pads: U5 has the board end 0.8 mm to its -X side (X -13.6 against -12.8), J1 on its +Y side, the board edge on its -Y side; U6 has L10 and the board edge on two sides.
- C35 at (-7.15, -4.80), courtyard X -8.70 to -5.60, Y -5.625 to -3.975: it touches U5's courtyard (X -8.70). Its near pad centre is at X -8.10, 2.7 mm from U5's centre and 1.9 mm from U5's +X body edge; the VDD_MIC track from C35 to U5 pin 4 is about 2.0 mm on L1. This needs the storage support parts to leave this area (Z15).
- C36 at (11.35, -2.37), courtyard X 9.80 to 12.90, Y -3.195 to -1.545: 0.005 mm from U6's courtyard (Y -3.20), 0.01 mm from U2's (X 9.79 with the rotation of b.1); the east test pad grid moves (Z14). Its track to U6 pin 4 is about 1.5 mm.
- Knowles sheet 4 asks for the 0.1 uF "next to each Vdd pin". 2.0 and 1.5 mm of track is the closest this board allows with an 0805. A 0603 Class 1 part (being checked by a reader) would fit at the same two places with 0.4 mm less courtyard; it would not reach closer, because the blocking parts are on the other sides. Whether the distance matters for noise is measured on the unit (h.2).

### f.2 Do the parts fit on one face? (area count) [values replaced in Round 2, R2.0]

- Board area: 27.2 x 12.6 less 4 corners of radius 0.8 = 342.2 mm2 (no notch; `ring-board-plan-work`, run of 00:13).
- Courtyards today: 236.2 mm2 for 100 footprints (measured with KiCad on `ring.kicad_pcb`, `area.py`; `board-notes.md` gives 241.6 with bounding boxes).
- Changes to the current circuit (each courtyard measured on the same board or computed with the 0.10 margin): removed Q1 1.148, D1 0.612, Q2 1.148, LED1 1.452, R41 0.761 (-5.121); removed TP7, TP10, TP20 (-2.376); added U10 2.8 x 2.0 = 5.6, U11 1.2 x 1.2 = 1.44, C83, C84, C85, C88 4 x 1.385, C81, C82, C86, C87, C89, LT1 6 x 0.761; microphones 4.2 x 3.2 against 10.48 each (+5.92); antenna 4.2 x 2.1 = 8.82 against 6.068 (+2.75). New total **254.5 mm2** (calculation of 00:22 plus C89 and LT1).
- Areas no part may use: the rest of the antenna keep-out 4.15 x 3.40 - 8.82 = 5.3 mm2; tail keep-outs 2 x 2.5 x 2.2 = 11.0 mm2, less the two land groups already counted in the courtyards (2.008 + 1.888 = 3.9 mm2).
- Library sizes (lead's message and footprint-notes.md, measured on the library courtyards): C35, C36 0805 5.551 each against 0.761 counted above (+9.580); C86, C87 0402 1.292 against 0.761 (+1.062); C88 0603 2.839 against 1.385 (+1.454); J1 6.1 x 3.35 = 20.44 against 16.556 (+3.88); antenna keep-out 0.20 shallower (4.15 x 3.20 - 8.82 = 4.46 against 5.3: -0.84). Total +15.14. The smaller library courtyard of the 0201 and 0402 parts (0.667 and 1.292 against 0.761 and 1.385) is not subtracted, so the sum below is on the high side.
- **Sum 254.5 + 5.3 + 11.0 - 3.9 + 15.1 = 282.0 of 342.2 mm2 = 82 percent. All 118 parts of PARTS that sit on the board fit by area** (the band parts SW1 to SW5, M1, BT1, RT1, CP1 to CP4 and DISP1 are not on the board). 82 percent is above the 72 percent the last placement packed, so placement follows the zones above. Method (deterministic, in `build_board.py`): a part with coordinates in this file goes there; every other part goes inside its zone, at the free place nearest the pad of the net it serves (the old script's rule, `board-notes.md` line 25), searching on a 0.05 mm grid with library courtyards; a part that finds no place in its zone takes the nearest free place outside it, and the script prints it. Check: 0 courtyard overlaps, every part inside the outline.

### f.3 Exits from the tail lands (fixed lands of band-interface.md section 2)

Geometry: lands 0.30 wide at 0.51 pitch leave 0.21 mm between columns: no track passes there (a 0.100 track needs 0.250). Rows 0.90 apart leave 0.35 mm between the rows: one track of 0.100 (0.125 each side) or 0.150 (0.100 each side) passes along X. No via is placed inside the keep-out; every exit ends in a stack L1-L3 or L1-L4 outside it.

| Tail | Land (X, Y) | Net | Exit on L1 | Stack outside the keep-out, then |
|---|---|---|---|---|
| B | 1 (-3.015, 3.875) | VBAT | west along Y 3.875, 0.15 | L1-L3 at (-3.75, 3.875); L3 0.30 to U2 D1/D2, C85, U11, U4 |
| B | 3 (-2.505, 3.875) | NTC | +Y to the row gap, east along Y 4.325, 0.10 | L1-L3 at (-0.85, 4.325); L3 to U2 D3 |
| B | 2, 7 (-1.995 / -1.485, 3.875) | GND | east along Y 3.875, joined, 0.20 | L1 ground copper, stacks L1-L4 at (-0.85, 3.875) |
| B | 4 (-1.995, 4.775) | VBUS | east along Y 4.775 through the free site, 0.25 | L1-L3 at (-0.85, 4.775); L3 0.60 to U9, R1, C71, C72, U2 B1/B2 |
| B | 5, 6 (-2.505 / -3.015, 4.775) | USB_DN, USB_DP | +Y out of the land, then east along Y 5.89 / 6.065 | none (d.2) |
| A | 2 (-3.015, -3.875) | JOY_DOWN | west along Y -3.875 | L1-L3 at (-3.75, -3.875) |
| A | 3 (-2.505, -3.875) | JOY_LEFT | +Y (toward the board middle) | L1-L3 at (-2.505, -3.25) |
| A | 1 (-1.995, -3.875) | JOY_UP | +Y | L1-L3 at (-1.995, -3.25) |
| A | 4 (-1.485, -3.875) | JOY_RIGHT | east along Y -3.875 | L1-L3 at (-0.85, -3.875) |
| A | 5 (-3.015, -4.775) | BTN_REC | west along Y -4.775 | L1-L3 at (-3.75, -4.775) |
| A | 7 (-2.505, -4.775) | VMOT | toward the row gap (Y -4.325), east along it, 0.15 (0.100 to each land) | L1-L3 at (-0.85, -4.325); L3 0.30 to U11 pin 1 and C84 |
| A | 6, 8 (-1.995 / -1.485, -4.775) | GND | east along Y -4.775, joined, 0.20 | L1 ground copper, stacks L1-L4 at (-0.85, -4.775) |

The stacks at Y +-3.25 sit 0.05 mm inside U3's courtyard line (Y +-3.20) but 1.9 mm from its nearest pad; a courtyard holds parts, not vias. With these exits the fixed lands do not make the board unroutable: every land reaches a layer outside the keep-out, and only VBAT, NTC, VBUS and VMOT need L3, which Plan A already reserves for power.

---

## g. Routing method (steps a builder runs)

All scripts run with KiCad's Python (`design/ecad/ring/pcb/run_kipy.sh <script>`). Each step ends with a check that can fail.

1. **Board file.** Change `build_board.py`: 4 copper layers (F.Cu, In1.Cu, In2.Cu, B.Cu), stack of c.2 (dielectrics 0.065, copper 0.018), board thickness 0.30; outline 27.2 x 12.6 with 0.8 corners and no notch; footprints of `OpenRing.pretty` (W1) for every part; the current NET (118 parts, 93 nets less the 3 dropped ball connections plus the changes of h.1); positions of PLACE and of f.1; U1 and U2 at rotation 0 (a.2, b.1). Run the inside model's fit check (`design/mech/thin/thin.py`, owned by W11) on the PLACE rows changed in h.1: last line `RESULT PASS`. Check: `check_board.py` passes (its fixed-position list updated with ANT1, U2, L71, L72, X2 of h.1) and `kicad-cli pcb drc` reports 0 courtyard overlaps.
2. **Rules.** Write c.5 into `ring.kicad_pro` (board minimums and net classes RF, USB, PWR with their nets) and a rules file `ring.kicad_dru` with: annular width min 0.05 for vias; hole-to-hole 0.20; a rule area "ANT_KEEPOUT" (all copper layers, no tracks, no vias, no zones, footprints allowed: ANT1, LT1); a rule "RF clearance 0.20" for RF_FEED and the ANT_NODE nets. Check: DRC on the placed board still 0 violations.
3. **Planes.** Draw ground zones: B.Cu (L4) the whole board less the keep-out; In1.Cu (L2) the whole board less the keep-out, priority below tracks; F.Cu ground in free areas, 0.2 mm from RF. Ground stacks come in step 5 (f).
4. **Router keep-out band.** A copper keep-out ring 0.15 mm wide inside the outline on all layers (the trial's 30 edge errors, `probe/route-probe.md` finding 3).
5. **Scripted copper, written by `route_fixed.py` (new script) from the tables of this file:** (a) every U1 and U2 escape of a.3 and b.2: via in the land as listed, track of the class width from the land 0.50 mm past the body edge in the listed direction, ending in a free end; (b) the RF line of d.1 with its stitching stacks; (c) the USB pair of d.2; (d) the crystal lines of d.4; (e) the power tracks of d.5 from U2 to its capacitors and coils, VBUS and VBAT from the tail B lands, VMOT; (f) the tail land exits of f.3; (g) every ground stack: at each ground pad within 0.4 mm, except where a scripted escape line runs; there the script moves the stack along the ground copper to the first point at least 0.10 mm (copper to copper) from every scripted track, searching outward on a 0.05 mm grid. Every scripted track and via is set **Locked**. Check: the script prints the count of scripted segments and vias; DRC 0 violations (unconnected allowed at this step).
6. **DSN.** Export with `export_dsn.py` (the trial's script). Then `fix_dsn.py` (new) edits the DSN: in `(library ...)` one padstack per span, each a 200 um circle on every layer it touches: `Via[0-1]_200:100_um`, `Via[1-2]_200:100_um`, `Via[2-3]_200:100_um`, `Via[0-2]_200:100_um`, `Via[1-3]_200:100_um`, `Via[0-3]_200:100_um`; in `(structure ...)` the line `(via "Via[0-1]_200:100_um" "Via[1-2]_200:100_um" "Via[2-3]_200:100_um" "Via[0-2]_200:100_um" "Via[1-3]_200:100_um" "Via[0-3]_200:100_um")`, `(rule (width 100) (clearance 75))`, and the class rules of c.5 in um. Check: `grep -c "type protect"` in the DSN equals the count of step 5; the six padstack names are present; the DSN rule width is 100.
7. **Router.** On the build server, as the trial (`probe/route-probe.md` "Setup and commands"): `nice -n 19 docker run --rm --cpus 8 eclipse-temurin:25-jre timeout 1200 java -jar freerouting-2.5.0.jar --gui.enabled=false -de ring.dsn -do ring.ses -mp 1 -mt 0`, then a second run with `-mp 20` and `timeout 3600`. Keep the SES with the lower unrouted count (Freerouting's own "unrouted" line).
8. **Import and clean.** `import_ses.py` into a copy; then `clean.py` (new): any track narrower than its class width is set to the class width; dangling tracks and vias are deleted; zones refilled. Check: `kicad-cli pcb drc --severity-all --all-track-errors` on the copy.
   - **Gate:** if the better of the two runs of step 7 has 1 or more unconnected items after step 8, switch to **Plan B** (c.4): step 1 with 6 layers, L5 as a signal and power layer, the same escapes; repeat steps 2 to 8. The decision is taken by this count, not by a person.
9. **End check.** `kicad-cli pcb drc --severity-all --all-track-errors --schematic-parity` on the final board: **0 violations and 0 unconnected items**, last line of the report kept. Then fabrication files: Gerber per layer, one drill file per via span (KiCad writes one per layer pair: the order states that each pair file is a stack of laser microvias, one per dielectric), IPC-D-356 netlist, position file, the stack drawing of c.2, and the board STEP.

---

## h. Lists

### h.1 Changes other files need

| File | Value now | Value needed | Reason |
|---|---|---|---|
| `design/ecad/ring/make_netlist.py` and `netlist.csv` | U1.E5 on SPARE_P1_19 with TP10; U1.E6 on MIC_B_CLK with TP20; U1.E8 on SPARE_P1_01 with TP7 | E5, E6, E8 no-connect; TP7, TP10, TP20 removed | a.2: the escape fits 3 signal layers only without them |
| same | ANT1 pins 2, 3 on GND | ANT1.2, ANT1.3 on new net ANT_TRIM with LT1.1; LT1.2 on GND; LT1 0201, 0 ohm fitted | e.2, JOH5 L/C part |
| same | ANT3_NODE: C12.1, L3.2, L4.1 | add C89.1 (C89 0201, not fitted, other pin GND) | e.4, JOH5 note 5 (pi network) |
| `design/ecad/ring/parts.csv`, `design/bom.csv` | no C89, no LT1; TP7, TP10, TP20 present | C89 (DNP), LT1 (0 ohm 0201) added; TP7, TP10, TP20 removed | same |
| `design/mech/thin/placement.csv` row ANT1 | X -12.700, Y 4.400, Z 1.050, size 1.600 x 3.200 x 1.200, "stands in the board notch" | X -11.500, Y 5.250, Z 0.850, size 3.200 x 1.600 x 1.200, "on the board's under face, Johanson land pattern, in the resin floor pocket" | e.1, e.6 R2 |
| same, row PCB1 | 0.300 thick, "antenna notch 1.8 x 3.6" | 0.300 thick, no notch | e.7 |
| same, rows L71 and L72 | L71 (8.500, 3.200), L72 (11.000, 3.200) | L71 (11.000, 3.450), L72 (8.500, 3.450) | f.1, b |
| same, row U2 | size 3.100 x 2.400 | size 2.400 x 3.100 (rotated 90 degrees on the same centre) | b.1 |
| same, row X2 (crystal_32k) | X 5.500, Y 3.000 | X 6.000, Y 3.000 | d.2 USB lane |
| same, row J1 (screen_connector) | X -12.000, Y 0.000, size 3.200 x 5.200 x 0.900 | X -11.650, Y -0.150, size 3.350 x 6.100 x 0.900 | f.4 (Hirose catalogue p3, p4); the screen tail's run to J1 follows (W11) |
| `design/ecad/ring/pcb/OpenRing.pretty/FPC_Hirose_FH35C-15S-0.3SHW.kicad_mod` | courtyard 6.6 x 4.2 centred | courtyard = closed housing 6.1 x 3.35, centred on the lands | f.4: the 6.6 x 4.2 courtyard overlaps U5 and the antenna keep-out by 0.25 each |
| same, row outer_body; `design/mech/thin/thin.py`; `design/mfg/specs/body.md` | metal body, notch in the board | resin radio corner X -14.80 to -9.30, Y 2.05 to the skin; floor pocket X -13.30 to -9.70, Y 4.25 to 6.25, 0.20 deep | e.6 R1, R2 |
| `design/architecture.md` line 156 | "no copper and no metal within 4.2 x 4.7 mm, on every layer" | "no copper on any board layer within X -13.60 to -9.45, Y 3.10 to 6.30; body resin within X -14.80 to -9.30 (radio corner)" | e.3, e.6 |
| `design/architecture.md` line 443 and S15 (line 513) | antenna in a notch, pads off the board | antenna on the board in a 0.20 floor pocket; S15 closed by this file | e |
| `design/architecture.md` 17.2 (line 426) and line 458 (the 17.x board row "0.3 mm, 6 layers") | board 0.30, 6 layers | board 0.30, 4 layers any-layer (Plan A); with Plan B: board 0.46, block 3.36 | c |
| `design/mfg/specs/main-board.md` | 6 layers; notch 1.8 x 3.6; open points 2 and 6 | 4 layers, stack of c.2, rules c.5, coupons of h.2; no notch; keep-out of e.3 | c, e |
| `design/ecad/ring/pcb/ring.kicad_pro` | via 0.25 / 0.15, microvia 0.2 / 0.1, annulus default 0.1, track 0.1, gap 0.1, 6 layers | c.5 values, 4 layers | c.5 (fixes trial findings 1 and 4) |
| `design/ecad/ring/pcb/build_board.py` | 6 layers, notch drawn, provisional footprints | g.1 | g |
| `design/ecad/ring/pcb/board-notes.md` line 22 | notch 2.8 x 0.6 at +Y edge | removed | main-board.md point 4 |
| firmware board definition (W8) | MIC_B_CLK on P1.24 (E6) | not available on the board | a.2 |

### h.2 Cannot be settled on paper (start value, and the measurement on a built unit)

| Item | Start value | Measurement on the unit |
|---|---|---|
| Antenna match | L2 3.6 nH, C3 1.2 pF, L3 4.7 nH, C12 0.5 pF, L4 3.3 nH, C13 and C89 not fitted, LT1 0 ohm (PARTS; e) | return loss 2.3 to 2.6 GHz with a network analyser through a pigtail at L4's input, on the bench and worn, in the body; retune the pi C89, L4, C13 and LT1 until at least 10 dB over 2400 to 2480 MHz (antenna-study.md section 6 pass line) |
| Radio corner, pocket and the screen ledge | e.6 | bench T0, T1, T2 of antenna-study.md section 6 |
| Finished board thickness and mask | 0.30 +-0.025 mm | micrometer on 5 boards of the first lot; cross-section coupon (copper, dielectric, mask) |
| Impedance | RF 50 ohm at 0.120 mm; USB 90 ohm at 0.100 / 0.075 (d) | TDR on the maker's coupons (one RF line, one pair, built with the board); if outside +-10 percent, the width is changed on the next lot by the ratio the coupon gives |
| VDD_MIC decoupling at 2.0 and 1.5 mm (C35, C36, f.4) | 0805 C0G 100 nF | microphone noise floor with and without a 100 nF part soldered directly across U5 and U6's Vdd and ground pads on one unit (bench B7) |
| Dielectric constant of the 106 prepreg | 4.1 (JLC value for 3313) | from the same coupon |
| 32 MHz crystal | XC lines 6.0 mm or less (d.4) | frequency offset of the 32 MHz clock with the radio test firmware (carrier at 2440 MHz on a spectrum analyser or the DK's RSSI scan), trim set by firmware |
| 32.768 kHz start-up | XL lines 9 mm or less | start-up time and frequency at room temperature on 3 units |
| USB high speed through the tail and pads | 90 ohm pair on the board, tail uncontrolled | the ring enumerates at high speed on a host through the case pads, 10 plug cycles |
| Buck ripple and coil heat | NPM-DS values | ripple on VDD_1V8 and VDD_3V0 at 200 mA load with an oscilloscope |
| Stacked via reliability | 3-high stacks (D3, ground) | cross-section coupon after the maker's thermal stress test |

---

questions_for_owner:
1. Thickness choice: Plan A keeps the board at 0.30 mm and the block at 3.20 mm, with one routing layer fewer and an any-layer maker; Plan B (6 layers) makes the block at least 3.28 mm, 3.36 mm with the present margin (c.2, c.4). Evidence: no published 6-layer build reaches 0.30 mm (c.3: 0.408 mm from the published minimums). My reading: Plan A, with Plan B started only by the routing count of g.8. Which do you take?
2. Look: the resin radio corner grows from about 4.0 x 5.3 mm (antenna-study.md) to about 5.5 x 5.3 mm at the hand-end corner on the thumb side, and its floor gets a 0.20 mm pocket (e.6). Is that corner of different material accepted?
3. Three spare test points go (E5, E6, E8 of the main chip: two spare pins and the second microphone clock, TP7, TP10, TP20). Nothing in the circuit uses them (a.2). My reading: accept.

RESULT: done, I recommend 4 copper layers with any-layer laser microvias at 0.30 mm finished (0.267 mm over copper), so 0.30 mm holds with 4 layers but not with 6 (least 0.408 mm; the fixed 6-layer fallback is 0.433 mm over copper and a 3.36 mm block).

---

# Round 2: the plan against the real footprints

Written 2026-11-13 from 00:45 to 01:14 (Mac clock); updated at 01:13 with the lead's ruling on the antenna (four facts from the board builder). Inputs: the lead's decisions (`design/wiring/lead-decisions.md`, rows "7, 11 (part), W2", "4, W2", "2, 3, 6, 8, W2", "radio corner", "25", "127, 128"); the libraries `design/ecad/ring/pcb/OpenRing.pretty/` (21 footprints) and `design/ecad/band/OpenRingBand.pretty/` (10 footprints), loaded with KiCad's Python (`design/ecad/ring/pcb/run_kipy.sh`); `design/ecad/ring/parts.csv` as on disk at 00:49 (re-read at 01:17: 117 rows, 104 on the board, C89 and LT1 included once each, TP7, TP10, TP20 gone; `placement-plan.csv` has exactly one row for each of the 104, no duplicate, R71 and R72 included); the lead's two messages of round 2 (C35, C36 are 0402 1.0 nF C0G; L71, L72 are 1269AS-H 2.5 x 2.0; C71, C85, C86, C87, C60 0402; C88 0603). Scripts and logs: `design/wiring/ring-board-plan-work/` (`rules.py`, `geom.py`, `make_placement2.py`, `check_placement.py`, `area3.py`, `j1check.py`, `probe_rot.py`, their `.log` files, `placement-final.png`).

The lead's decision replaces step g.8's gate: there is no automatic switch to 6 layers. If routing on 4 layers leaves a connection open, the builder stops and reports the count and the nets; the lead takes it to the owner.

## R2.0 First: the antenna mount and its keep-out change (point 6)

The lead's ruling of 2026-11-13 (after the builder's test build) fixes these values; they replace e.1 to e.7 where they differ.

1. **ANT1 at (-10.80, 5.25), rotation 180** (was (-11.50, 5.25)). Reason (builder's test build and my own check): at -11.50 the far-end edge land (X -13.50 to -12.50, Y 5.60 to 6.20) is cut by the board's 0.8 mm corner arc (centre (-12.80, 5.50); KiCad copper to edge 0.000). At -10.80 the land corner (-12.80, 6.20) is 0.70 mm from the arc centre: copper to edge exactly 0.10, the rule's value (`check_placement.py` passes it at equality, as KiCad's rules check does). Pins (library footprint, rotation 180, `probe_rot.py`): pin 1 FEED at (-9.30, 5.90); pin 4 GND at (-9.30, 4.60) with its ground stack at (-8.50, 4.20); pins 2 and 3 at X -12.30 to LT1.
2. **Copper-free zone: X -13.60 to -8.75, Y 3.10 to 6.30** (the lead's decision), less a notch X -9.20 to -8.75, Y 3.10 to 3.30 where the storage chip U3's body corner stands (U3 courtyard to Y 3.27; U3 has no copper there: its nearest pads, pins 1 to 4 at X -8.50, end at Y 2.255).
3. Parts moved with the antenna (all in `placement-plan.csv`): C13 (-8.30, 4.98, rotation 90), L4 (-7.75, 5.90, rotation 0), C89 (-7.15, 4.98, rotation 90), LT1 (-12.45, 3.25, rotation 0). The feed line: (0.00, -0.39) to (0.00, 3.30) to (-6.50, 3.30) to (-6.70, 3.50) to (-6.70, 5.70) to (-6.90, 5.90) to L4, then L4 to pin 1 at (-9.30, 5.90). The chip match (agreeing with the table; replaces e.4): L2 (1.70, -0.39), L3 (0.48, -0.39), C3 (1.10, -1.31, rotation 90), C12 (-0.12, -1.31, rotation 90). Line length, sum of the legs between parts: 0.71 + 0.65 + 0.20 + 3.69 + 6.50 + 0.28 + 2.20 + 0.28 + 0.57 + 1.27 = 16.4 mm.
4. LT1's ground is J1's +Y mounting pad (X -13.25 to -12.30, Y 2.45 to 2.85), tied to GND with a stacked via in that pad (R2.6: J1's mounting pads go on GND).
5. What the body needs, replacing e.6: resin corner X -14.80 to **-8.60**, Y 2.05 to the skin (lead's ruling); floor pocket **X -12.60 to -9.00**, Y 4.25 to 6.25, 0.20 deep (e.6 R2 moved by the same 0.70).

## R2.1 J1, the screen connector (point 1)

Facts:
- Catalogue page 3 (`w1_hirose_fh35c_series_catalog.pdf`) and drawing EDC3-338903-01 page 1 (`w1_hirose_fh35c-15s-0.3shw50_drawing.pdf`): A = 6.1 along the contact row (15 contacts), land rows 3.6 apart outer edge to outer edge (B, catalogue page 4), housing depth (3.35) in the top view; the (4.2) is in the side detail, where the flip lever stands open at 90 degrees. Read from the pictures, catalogue page 3 and drawing page 1: the FPC enters on the side of contact No. 1 (the 0.8 mm lands), the lever (back flip) is on the side of contact No. 2; the leads stand 0.05 +-0.15 out on the FPC side and 0.15 +-0.15 on the lever side, so the closed housing sits about centred on the lands.
- The library footprint has its odd row (contact No. 1, 0.8 mm lands) at local y +1.4 and its mounting pads `MP` at local (+-2.8, 1.125). At rotation 270 local +y points to -X: the FPC opening faces the hand end, where the screen tail comes in (PLACE row DISP1 tail: X -13.775, down the hand end, under the board end to J1). Pin 1 is then at the +Y end (-13.05, 1.95 at the final place), pins 13 to 15 (ground) at the -Y end.

At PLACE's (-12.0, 0.0), rotation 270 (`j1check.py`): lands X -13.80 to -10.20, Y -3.00 to 3.00. **It does not fit:** the lands pass the board end (X -13.60) by 0.20 mm, and the +Y mounting pad (Y 2.60 to 3.00) reaches 0.10 mm into the antenna keep-out (from Y 2.90). The library courtyard (X -13.87 to -10.13, Y -3.12 to 3.12, as read at 01:05) passes the board end and enters the keep-out and microphone U5's courtyard.

**Final: J1 at (-11.65, -0.15), rotation 270.** Lands X -13.45 to -9.85, Y -3.15 to 2.85; mounting pads X -13.25 to -12.30 at Y -3.15 to -2.75 and 2.45 to 2.85; closed housing about X -13.33 to -9.98, Y -3.20 to 2.90. It touches U5's courtyard (U5 body edge Y -3.30, courtyard 0.10 round the body), stays 0.20 from the copper-free zone (Y 3.10), and stays 0.81 mm from U3's courtyard (X -9.17). What moves: J1 by (+0.35, -0.15); J1's courtyard becomes the closed housing 6.10 x 3.35 (the library's courtyard, 3.74 x 6.24 as read at 01:05, overlaps U5's courtyard at this place); U5's and U6's courtyards become the body plus 0.10 (library: plus 0.145). The keep-out and the antenna do not move for J1.

## R2.2 The microphones and C35, C36 (point 2, with the lead's 0402 ruling)

- U5 at (-10.8, -4.8) rotation 90, U6 at (10.8, -4.8) rotation 270: the Knowles land view (datasheet page 6) puts the port 1.030 from the short end of pad 7 (read from the picture); PLACE puts the ports at X -11.77 and +11.77, toward each block end. With these rotations pin 4 (Vdd) is at (-10.125, -5.225) for U5 and (10.125, -4.375) for U6 (`probe_rot.py`, `j1check.py`).
- **C35 (0402) at (-8.25, -5.35), rotation 90**: its courtyard (X -8.65 to -7.85) is 0.05 from U5's (X -8.70); centre 1.88 mm from U5 pin 4. **C36 (0402) at (8.25, -3.40), rotation 90**: courtyard X 7.85 to 8.65, 0.05 from U6's, 0.18 from L10's; centre 2.12 mm from U6 pin 4. No place is closer: U5 has the board end (-X), the board edge (-Y) and J1 and U3 (+Y) on its other sides; U6 has the board edge, U2 and L10. Pin 4 is an inner land: it leaves by a microvia L1-L2 in the land and runs on L2 to a microvia in the capacitor's pad.
- C31 at (-9.50, -0.70), C32 at (6.20, -5.80): both more than 2.0 mm from the microphone bodies (enforced in `rules.py`, AVOID).

## R2.3 Zones against the real footprints (point 3)

| Part | Footprint fact | Effect on the plan |
|---|---|---|
| U3 | 9 pads: pins 1 to 4 in a column at X -8.50, pins 5 to 8 at X -1.50 (Y +-0.635, +-1.905, pads 0.8 x 0.7), pad 9 (-5.00, 2.60), courtyard X -9.17 to -0.83, Y -3.27 to 3.27 | RF line along Y 3.30 passes pad 9 (edge Y 3.00) at 0.24 mm: passes the RF check. The J_BAND courtyards of the band library (3.21 x 2.91) overlap U3's by 0.40: replaced by the keep-out rectangles (h.1). U3 and U5 courtyards overlap 0.07 mm; their bodies are 0.20 apart as the mechanical model fixed them (mic-path.md C13): counted as a declared exception |
| U4 | 2.0 x 2.0, pitch 0.5, courtyard 2.35 x 2.35 | moved from Y -3.50 to **-3.90** (with L10) so that the strip between U1 and U4 is 1.345 mm and holds U1's supply parts (C4, C6, FB1, C7); its fly capacitor C23 and input C22 are fixed beside it at (2.37, -3.40) and (2.37, -5.10); L1 moves to (1.00, -4.32) |
| L10, L71, L72 | 1269AS-H, courtyard 3.14 x 2.34 | L10 rotated 90 at (6.50, -3.90): at rotation 0 its courtyard overlapped U4's by 0.20. L72 at (8.87, 3.75), L71 at (12.02, 3.75), rotation 0 (long side along X): their courtyards touch (X 7.30 to 10.44 and 10.45 to 13.59). SW2 runs south along X 8.0 to L72's west pad (7.87, 3.75); SW1 runs east along Y 1.55 to X 10.95 then south to L71's west pad (11.02, 3.75); C74 (PVDD) at (9.05, 2.14) between U2 and L72. These replace the coil places of f.1 |
| U10 | UQFN-16 1.8 x 2.6, courtyard 2.54 x 3.34 | no room in Z15 once U1's supply parts and the RF corridor took theirs: **U10 at (-5.25, -4.60), rotation 90**, north of U3 between U5 and the tail A keep-out, C81 and C82 beside it; the card lines reach U3's two pad columns from there |
| U11 | X2SON 5 pads (thermal pad 5) | unchanged at (0.00, 4.20); C83 stays (0.00, 5.45); **C84 rotated 90 at (1.27, 5.00)** (at rotation 0 it overlapped C83); U9 at (3.12, 5.20) |
| X2 | 9HT11 courtyard 1.74 x 2.54 | rotation 90 at **(6.00, 3.35)** (was 3.00), so a 0402 fits between it and U1 |
| RF corridor X -0.83 to 2.32 | between U3's and U1's courtyards | holds the RF chain and the X 0.00 leg; every pad of another part is 0.20 mm or more from the line (check) |
| USB pair | | its west run moves to Y 5.95 and 6.125 (was 5.89, 6.065): 0.20 from C83's and C84's pads, 0.125 from the board edge |
| Test pads | 19 x TESTPAD_0.8 (courtyard 1.04 x 1.04, 20.6 mm2) | **all 19 go to the screen face (L4)**: flat copper with no height; with them on the parts face the first placement run found no place for C75 |

## R2.4 Area with the real libraries (point 4)

From `area3.log` (courtyard bounding boxes including the 0.05 line, as `footprint-notes.md` measures them):
- Board 342.2 mm2.
- Parts face: courtyards 275.6 mm2 (J1 as its housing, J_BAND as the keep-out rectangles, U5 and U6 body + 0.10); with every library courtyard unchanged, 281.2.
- Antenna copper-free zone on the board 15.43 mm2, of which 9.71 under ANT1 and LT1: 5.72 more that no part may use.
- **Sum 281.3 of 342.2 mm2 = 82.2 percent** (88.2 percent if the 20.6 mm2 of test pads stayed on the parts face). The routing reserves of the RF line, the USB pair and the switching tracks (about 18 mm2 of L1) come on top.

## R2.5 Placement table (point 5)

File: `design/wiring/ring-board-plan-work/placement-plan.csv` (columns reference, footprint, side, x_mm, y_mm, rotation_deg, zone, kicad_x, kicad_y; KiCad = model + (100, 100); side F = parts face L1, B = screen face L4; rotation in KiCad degrees). It is written by `make_placement2.py` run as `SEED=4 OUT=placement-plan.csv run_kipy.sh make_placement2.py`: parts with coordinates in `rules.py` (FIXED) go there; every other part goes to the free place nearest the pin it serves (ANCHOR), on a 0.05 mm grid within 3 mm and 0.1 mm beyond, rotation 0 then 90, avoiding courtyards, keep-outs and the routing reserves; SEED=4 is the one of 8 tried orders that placed all parts with the least total distance (1, 3 to 7 placed all; 2 and 8 left one part out: `seed*.log`).

Check: `check_placement.py placement-plan.csv` → `check_placement.log` ends `RESULT PASS` (104 parts, 85 on the parts face, 19 on the screen face; no courtyard overlap except the declared U5-U3 pair; every courtyard inside the outline (copper at exactly 0.10 from the edge passes), with ANT1, U5, U6 allowed 0.10 / 0.20 / 0.20 past it and their pads 0.10 inside; no part in a keep-out it is not allowed in; every pad of another part 0.20 mm or more from the RF line and the USB pair). Broken copy (C4 pushed onto U1, C79 pushed past the edge): `check_placement_broken.log` ends `RESULT FAIL 4`.

Parts placed more than 3 mm from the pin they serve (all decoupling or bias parts; distances from `place-final.log`): C26 8.2 and C27 8.2 (U4's AVDD and VON outputs), C21 6.1 (U4's VBAT input), C75 6.4 (VSYS), C25 5.3 (ELVDD at J1), C28 5.0 (ELVSS at J1), C11 3.5 (U1 VBUS), C24 3.3 (U4 VOUT), C78 3.1 and C80 3.9 (buck outputs), C73 3.8, C72 3.9 (VBUSOUT, VBUS), C32 3.9 and C31 5.8 (kept away from the microphones on purpose); resistors R57, R58, R60, R63, R64, R66, R61, R62, R1 (bias and series parts, position not critical). C29 (ELVSS) shows 14.3 mm from its anchor at J1 but sits at (3.65, -5.50), about 2.6 mm from U4's ELVSS ball D4, the source of that rail. The board has no free place nearer: this is the cost of the real footprints. Each gets a measurement on the unit (h.2 below).

| Ref | Footprint | Face | X | Y | Rot | Zone | Placed by |
|---|---|---|---|---|---|---|---|
| U1 | WLCSP-61_nRF54LM20A-CAAA | F | 4.000 | 0.000 | 0 | U1 | fixed in this file |
| C4 | Chip_0402 | F | 2.830 | -2.060 | 0 | Z1 | fixed in this file |
| C5 | Chip_0201 | F | 1.050 | -2.500 | 90 | Z1 | fixed in this file |
| C1 | Chip_0201 | F | 6.010 | 0.350 | 90 | Z4 | fixed in this file |
| C2 | Chip_0201 | F | 6.670 | 0.660 | 90 | Z4 | fixed in this file |
| L1 | L_TDK_MLZ1608_1.6x0.8 | F | 1.000 | -4.320 | 90 | Z1 | fixed in this file |
| C6 | Chip_0201 | F | 4.000 | -2.060 | 90 | Z1 | fixed in this file |
| FB1 | Chip_0201 | F | 4.650 | -2.060 | 90 | Z1 | fixed in this file |
| C7 | Chip_0201 | F | 5.600 | -1.750 | 0 | Z1 | fixed in this file |
| C14 | Chip_0201 | F | 6.010 | -0.840 | 90 | Z4 | fixed in this file |
| C10 | Chip_0201 | F | 5.420 | 1.710 | 0 | Z3 | fixed in this file |
| R1 | Chip_0603 | F | -4.100 | 4.900 | 90 | Z3 | script, 10.18 mm from anchor (5.6, 1.8) |
| C11 | Chip_0402 | F | 5.900 | 5.100 | 90 | Z3 | script, 3.50 mm from anchor (5.9, 1.6) |
| R2 | Chip_0201 | F | 2.000 | 1.250 | 90 | Z3 | script, 1.35 mm from anchor (3.3, 1.6) |
| X1 | XTAL_Kyocera_CX2016DB_2.0x1.6 | F | 3.000 | 3.000 | 0 | Z3 | fixed in this file |
| X2 | XTAL_TXC_9HT11_2.0x1.2 | F | 6.000 | 3.350 | 90 | Z3 | fixed in this file |
| L2 | Chip_0201 | F | 1.700 | -0.390 | 0 | Z2 | fixed in this file |
| C3 | Chip_0201 | F | 1.100 | -1.310 | 90 | Z2 | fixed in this file |
| L3 | Chip_0201 | F | 0.480 | -0.390 | 0 | Z2 | fixed in this file |
| C12 | Chip_0201 | F | -0.120 | -1.310 | 90 | Z2 | fixed in this file |
| L4 | Chip_0201 | F | -7.750 | 5.900 | 0 | Z8 | fixed in this file |
| C13 | Chip_0201 | F | -8.300 | 4.980 | 90 | Z8 | fixed in this file |
| ANT1 | ANT_Johanson_2450AT18D0100001E_3.2x1.6 | F | -10.800 | 5.250 | 180 | antenna | fixed in this file |
| LT1 | Chip_0201 | F | -12.450 | 3.250 | 0 | antenna | fixed in this file |
| C89 | Chip_0201 | F | -7.150 | 4.980 | 90 | Z8 | fixed in this file |
| U2 | WLCSP-35_nPM1304-CAAA | F | 8.500 | 0.000 | 270 | Z5 | fixed in this file |
| C71 | Chip_0402 | F | 10.400 | -2.130 | 0 | Z5 | fixed in this file |
| C85 | Chip_0402 | F | 8.520 | -2.130 | 0 | Z5 | fixed in this file |
| C88 | Chip_0603 | F | 10.300 | 5.550 | 0 | Z6 | script, 0.72 mm from anchor (11.0, 5.4) |
| C86 | Chip_0402 | F | 10.300 | 0.000 | 90 | Z5 | fixed in this file |
| C87 | Chip_0402 | F | 11.150 | 0.200 | 90 | Z5 | fixed in this file |
| C72 | Chip_0201 | F | 13.200 | -2.200 | 90 | Z5 | script, 3.90 mm from anchor (9.3, -2.1) |
| C73 | Chip_0201 | F | 8.100 | -5.900 | 0 | Z5 | script, 3.82 mm from anchor (8.5, -2.1) |
| C74 | Chip_0402 | F | 9.050 | 2.140 | 0 | Z5 | fixed in this file |
| C75 | Chip_0402 | F | 8.100 | 5.400 | 0 | Z5 | script, 6.43 mm from anchor (10.4, -0.6) |
| C76 | Chip_0201 | F | 10.450 | -1.200 | 0 | Z5 | script, 2.10 mm from anchor (10.4, 0.9) |
| C77 | Chip_0201 | F | 13.150 | -1.000 | 90 | Z5 | script, 2.55 mm from anchor (10.6, -1.0) |
| L71 | L_Murata_1269AS-H_2.5x2.0 | F | 12.020 | 3.750 | 0 | Z6 | fixed in this file |
| C78 | Chip_0402 | F | 6.780 | 5.300 | 90 | Z6 | script, 3.10 mm from anchor (9.88, 5.3) |
| L72 | L_Murata_1269AS-H_2.5x2.0 | F | 8.870 | 3.750 | 0 | Z6 | fixed in this file |
| C79 | Chip_0402 | F | 12.450 | 5.600 | 0 | Z6 | fixed in this file |
| C80 | Chip_0201 | F | 7.100 | 2.100 | 0 | Z6 | script, 3.88 mm from anchor (9.3, 5.3) |
| R71 | Chip_0201 | F | 6.670 | -0.520 | 90 | Z4 | fixed in this file |
| R72 | Chip_0201 | F | 6.670 | -1.700 | 90 | Z4 | fixed in this file |
| R57 | Chip_0201 | F | 13.200 | 0.600 | 90 | Z4 | script, 6.60 mm from anchor (6.6, 0.6) |
| R58 | Chip_0201 | F | 13.200 | 1.800 | 90 | Z4 | script, 6.77 mm from anchor (6.6, 0.3) |
| U5 | LGA-8_Knowles_SPK0641HT4H-1_3.0x4.0 | F | -10.800 | -4.800 | 90 | Z7 | fixed in this file |
| R31 | Chip_0201 | F | -7.550 | -3.650 | 0 | Z7 | script, 1.21 mm from anchor (-6.6, -4.4) |
| C31 | Chip_0201 | F | -9.500 | -0.700 | 90 | Z7 | script, 5.77 mm from anchor (-6.3, -5.5) |
| C35 | Chip_0402 | F | -8.250 | -5.350 | 90 | Z7 | fixed in this file |
| U6 | LGA-8_Knowles_SPK0641HT4H-1_3.0x4.0 | F | 10.800 | -4.800 | 270 | Z11 | fixed in this file |
| R32 | Chip_0201 | F | 8.250 | -4.900 | 90 | Z11 | fixed in this file |
| C32 | Chip_0201 | F | 6.200 | -5.800 | 0 | Z11 | script, 3.91 mm from anchor (6.5, -1.9) |
| C36 | Chip_0402 | F | 8.250 | -3.400 | 90 | Z11 | fixed in this file |
| U3 | LGA-9_CSNP32GCR01-BOW_8.0x6.2 | F | -5.000 | 0.000 | 0 | U3 | fixed in this file |
| U10 | UQFN-16_SN74AXC4T774RSV_1.8x2.6 | F | -5.250 | -4.600 | 90 | Z15 | script, 0.00 mm from anchor (-5.25, -4.6) |
| C81 | Chip_0201 | F | -7.250 | -4.600 | 90 | Z15 | script, 0.50 mm from anchor (-6.75, -4.6) |
| C82 | Chip_0201 | F | -2.950 | -5.950 | 0 | Z15 | script, 1.57 mm from anchor (-3.75, -4.6) |
| R60 | Chip_0201 | F | -9.500 | 0.500 | 90 | Z15 | script, 9.44 mm from anchor (-0.4, -2.0) |
| R63 | Chip_0201 | F | -9.500 | -2.400 | 90 | Z15 | script, 9.10 mm from anchor (-0.4, -2.4) |
| R64 | Chip_0201 | F | 4.900 | -5.700 | 90 | Z15 | script, 6.04 mm from anchor (-0.4, -2.8) |
| R65 | Chip_0201 | F | -1.400 | -5.950 | 0 | Z15 | script, 2.93 mm from anchor (-0.4, -3.2) |
| C60 | Chip_0402 | F | -0.400 | -2.750 | 90 | Z15 | script, 1.15 mm from anchor (-0.45, -1.6) |
| C61 | Chip_0201 | F | 0.350 | -2.500 | 90 | Z15 | script, 1.36 mm from anchor (-0.45, -3.6) |
| U4 | WLCSP-16_SGM38046_2.0x2.0_P0.5 | F | 4.000 | -3.900 | 0 | Z12 | fixed in this file |
| L10 | L_Murata_1269AS-H_2.5x2.0 | F | 6.500 | -3.900 | 90 | Z12 | fixed in this file |
| C21 | Chip_0603 | F | 1.000 | 1.300 | 90 | Z12 | script, 6.06 mm from anchor (2.4, -4.6) |
| C22 | Chip_0402 | F | 2.370 | -5.100 | 90 | Z12 | fixed in this file |
| C23 | Chip_0402 | F | 2.370 | -3.400 | 90 | Z12 | fixed in this file |
| C24 | Chip_0603 | F | -0.200 | -5.000 | 90 | Z12 | script, 3.28 mm from anchor (3.0, -5.7) |
| C25 | Chip_0603 | F | -5.750 | 4.900 | 90 | Z13 | script, 5.30 mm from anchor (-9.55, 1.2) |
| C26 | Chip_0603 | F | 12.200 | -1.900 | 90 | Z12 | script, 8.19 mm from anchor (5.0, -5.8) |
| C27 | Chip_0603 | F | 12.200 | 0.700 | 90 | Z12 | script, 8.16 mm from anchor (7.4, -5.9) |
| C28 | Chip_0402 | F | -7.850 | 3.700 | 0 | Z13 | script, 5.00 mm from anchor (-9.55, -1.0) |
| C29 | Chip_0402 | F | 3.650 | -5.500 | 0 | Z13 | script, 14.30 mm from anchor (-9.55, 0.0) |
| R66 | Chip_0201 | F | 1.350 | -5.900 | 0 | Z12 | script, 3.12 mm from anchor (2.5, -3.0) |
| J1 | FPC_Hirose_FH35C-15S-0.3SHW | F | -11.650 | -0.150 | 270 | Z13 | fixed in this file |
| J_BAND_A | J_BAND_A_BOARD | F | -2.250 | -4.325 | 0 | Z10 | fixed in this file |
| J_BAND_B | J_BAND_B_BOARD | F | -2.250 | 4.325 | 0 | Z10 | fixed in this file |
| U11 | X2SON-4_TLV755xxPDQN_1.0x1.0 | F | 0.000 | 4.200 | 0 | Z9 | fixed in this file |
| C83 | Chip_0402 | F | 0.000 | 5.450 | 0 | Z9 | fixed in this file |
| C84 | Chip_0402 | F | 1.270 | 5.000 | 90 | Z9 | fixed in this file |
| R61 | Chip_0201 | F | 1.100 | 3.550 | 90 | Z9 | script, 0.27 mm from anchor (1.0, 3.8) |
| R62 | Chip_0201 | F | 4.900 | 5.300 | 90 | Z9 | script, 4.03 mm from anchor (1.0, 4.3) |
| U9 | USON-10_TPD4E05U06DQA | F | 3.120 | 5.200 | 90 | Z9 | fixed in this file |
| TP1 | TESTPAD_0.8 | B | -3.950 | -1.050 | 0 | Z14 (L4) | script, 1.48 mm from anchor (-5.0, 0.0) |
| TP2 | TESTPAD_0.8 | B | -5.000 | 0.000 | 0 | Z14 (L4) | script, 0.00 mm from anchor (-5.0, 0.0) |
| TP3 | TESTPAD_0.8 | B | -3.950 | 0.000 | 0 | Z14 (L4) | script, 1.05 mm from anchor (-5.0, 0.0) |
| TP4 | TESTPAD_0.8 | B | -6.050 | 0.000 | 0 | Z14 (L4) | script, 1.05 mm from anchor (-5.0, 0.0) |
| TP5 | TESTPAD_0.8 | B | -5.000 | -1.050 | 0 | Z14 (L4) | script, 1.05 mm from anchor (-5.0, 0.0) |
| TP6 | TESTPAD_0.8 | B | -6.050 | -1.050 | 0 | Z14 (L4) | script, 1.48 mm from anchor (-5.0, 0.0) |
| TP8 | TESTPAD_0.8 | B | -6.050 | 1.050 | 0 | Z14 (L4) | script, 1.48 mm from anchor (-5.0, 0.0) |
| TP9 | TESTPAD_0.8 | B | -5.000 | 1.050 | 0 | Z14 (L4) | script, 1.05 mm from anchor (-5.0, 0.0) |
| TP11 | TESTPAD_0.8 | B | -5.000 | 2.100 | 0 | Z14 (L4) | script, 2.10 mm from anchor (-5.0, 0.0) |
| TP12 | TESTPAD_0.8 | B | -7.100 | 1.050 | 0 | Z14 (L4) | script, 2.35 mm from anchor (-5.0, 0.0) |
| TP13 | TESTPAD_0.8 | B | -2.900 | 0.000 | 0 | Z14 (L4) | script, 2.10 mm from anchor (-5.0, 0.0) |
| TP14 | TESTPAD_0.8 | B | -3.950 | 1.050 | 0 | Z14 (L4) | script, 1.48 mm from anchor (-5.0, 0.0) |
| TP15 | TESTPAD_0.8 | B | -6.050 | 2.100 | 0 | Z14 (L4) | script, 2.35 mm from anchor (-5.0, 0.0) |
| TP16 | TESTPAD_0.8 | B | -6.050 | -2.100 | 0 | Z14 (L4) | script, 2.35 mm from anchor (-5.0, 0.0) |
| TP17 | TESTPAD_0.8 | B | -7.100 | 0.000 | 0 | Z14 (L4) | script, 2.10 mm from anchor (-5.0, 0.0) |
| TP18 | TESTPAD_0.8 | B | -7.100 | -1.050 | 0 | Z14 (L4) | script, 2.35 mm from anchor (-5.0, 0.0) |
| TP19 | TESTPAD_0.8 | B | -5.000 | -2.100 | 0 | Z14 (L4) | script, 2.10 mm from anchor (-5.0, 0.0) |
| TP21 | TESTPAD_0.8 | B | -3.950 | -2.100 | 0 | Z14 (L4) | script, 2.35 mm from anchor (-5.0, 0.0) |
| TP22 | TESTPAD_0.8 | B | -3.950 | 2.100 | 0 | Z14 (L4) | script, 2.35 mm from anchor (-5.0, 0.0) |

## R2.6 Changes other files need (added to h.1)

| File | Value now | Value needed | Reason |
|---|---|---|---|
| `design/mech/thin/placement.csv` | ANT1 X -12.700, Y 4.400, 1.6 x 3.2; J1 (-12.000, 0.000) 3.2 x 5.2; U4 Y -3.500; L10 (6.500, -3.500) 2.5 x 2.0; L71 (8.500, 3.200), L72 (11.000, 3.200) 2.0 x 1.6; X2 (5.500, 3.000); U2 3.1 x 2.4; C84 (1.200, 5.000) | ANT1 (-10.800, 5.250) 3.2 x 1.6, Z 0.85; J1 (-11.650, -0.150) 3.35 x 6.1; U4 Y -3.900; L10 (6.500, -3.900) 2.0 x 2.5; L71 (12.020, 3.750), L72 (8.870, 3.750) 2.5 x 2.0; X2 (6.000, 3.350); U2 2.4 x 3.1; C84 (1.270, 5.000) | R2.0 to R2.3; the model's fit check reruns (W11) |
| same, outer_body and the radio corner (`thin.py`, `mfg/specs/body.md`) | corner X -14.80 to -9.30 (lead's row "radio corner"); pocket X -13.30 to -9.70 | corner X -14.80 to -8.60; pocket X -12.60 to -9.00, Y 4.25 to 6.25, 0.20 deep | R2.0 (lead's ruling) |
| `design/wiring/lead-decisions.md` row "2, 3, 6, 8, W2" and `design/architecture.md` line 156 | keep-out X -13.60 to -9.45, Y 2.90 to 6.30 | X -13.60 to -8.75, Y 3.10 to 6.30 (lead's ruling), less X -9.20 to -8.75, Y 3.10 to 3.30 | R2.0 |
| `design/ecad/ring/pcb/OpenRing.pretty/FPC_Hirose_FH35C-15S-0.3SHW.kicad_mod` | courtyard 3.74 x 6.24 (as read at 01:05) | the closed housing, 6.10 along the row x 3.35, centred on the lands | R2.1 |
| `OpenRing.pretty/LGA-8_Knowles_SPK0641HT4H-1_3.0x4.0.kicad_mod` | courtyard body + 0.145 | body + 0.10 | R2.1 (J1 and U5 bodies are 0.10 apart) |
| `design/ecad/band/OpenRingBand.pretty/J_BAND_A_BOARD.kicad_mod`, `J_BAND_B_BOARD.kicad_mod` | courtyard 3.21 x 2.91, overlapping U3's by 0.40 | the keep-out rectangle of band-interface.md section 2 (2.50 x 2.20) | R2.3 |
| `J_BAND_A_BOARD.kicad_mod` against `design/ecad/band/band-interface.md` section 2 | footprint pad 1 at (-1.485, -3.875), pad 4 at (-1.485, -4.775), pad 6 at (-1.995, -3.875), pad 8 at (-1.995, -4.775) (placed at (-2.25, -4.325), rotation 0, `probe_rot.py`) | the table: land 1 UP (-1.995, -3.875), land 4 RIGHT (-1.485, -3.875), land 6 MOT- (-1.995, -4.775), land 8 GND (-1.485, -4.775). One of the two files is wrong: the band helper settles which (lands 2, 3, 5, 7 agree; J_BAND_B agrees in all 7) | conflict found while placing; my exits of f.3 follow the table |
| `design/ecad/ring/make_netlist.py`, `netlist.csv` | J1 mounting pads MP without a net | MP on GND | R2.0 item 4 (LT1's ground) |
| `design/ecad/ring/pcb/build_board.py` | own placement | load `placement-plan.csv` (side B = flipped to the screen face for the 19 test pads) | R2.5 |

## R2.7 Added to h.2 (cannot be settled on paper)

| Item | Start value | Measurement on the unit |
|---|---|---|
| Screen supply with its capacitors 3 to 8 mm away (C21, C24, C26, C27, C25, C28) | positions of R2.5 | ripple on SGM_AVDD, SGM_VON, ELVDD, ELVSS at full white screen, and the screen's start-up, on 3 units |
| Buck outputs and VSYS with C78, C80, C75 3 to 6 mm away | positions of R2.5 | ripple on VDD_1V8, VDD_3V0, VSYS at 200 mA load |
| VDD_MIC at the microphones (C35, C36 1.0 nF C0G, 1.9 and 2.1 mm from pin 4) | lead's decision row 25 | noise floor of a silent recording (the lead's decision already names it) |
| Test pads on the screen face | 19 pads on L4 | probe contact with the pogo fixture before the board goes into the body |

RESULT: done, every one of the 104 board parts fits on the 4-layer board's parts face with the real footprints (check PASS, 82.2 percent of the area) once the 19 test pads move to the screen face, J1 moves to (-11.65, -0.15), the antenna and its copper-free zone move 0.70 mm toward the fingertip (lead's ruling: ANT1 X -10.80, zone X -13.60 to -8.75, Y 3.10 to 6.30), U4, L10, X2, L71, L72, C84 move, and 14 capacitors sit 3 to 8 mm from their pins.

---

# Round 3: regulator capacitors

Written 2026-11-13 from 01:13 to 01:50 (Mac clock). Scripts and logs in `design/wiring/ring-board-plan-work/`: `capdist.py` (distance check), `make_placement3.py` (search), `check_tailA.py`, logs `capdist-r2.log`, `capdist-r3try.log`, `r3a.log` to `r3i.log`, `check_tailA.log`. The round 2 table is kept as `placement-plan-r2.csv`. **`placement-plan.csv` is NOT replaced: no placement found meets the round 3 limits with the allowed means (R3.3), so the round 2 table stays the builder's table.**

## R3.0 Tail A exits, reworked to the footprint (band owner's ruling)

The footprint `J_BAND_A_BOARD` is right. Checked by `check_tailA.py` (footprint at (-2.25, -4.325), rotation 0; nets from `netlist.csv`): all 8 lands agree, `check_tailA.log` ends `RESULT PASS` with the least copper gap 0.100 mm. These rows replace the tail A rows of f.3:

| Land (X, Y) | Net | Exit on L1 | Stack outside the keep-out |
|---|---|---|---|
| 2 (-3.015, -3.875) | JOY_DOWN | west along Y -3.875, 0.10 | L1-L3 at (-3.75, -3.875) |
| 3 (-2.505, -3.875) | JOY_LEFT | +Y toward the board middle, 0.10 | L1-L3 at (-2.505, -3.25) |
| 6 (-1.995, -3.875) | GND (MOT-) | +Y, 0.20 | L1-L4 at (-1.995, -3.25) |
| 1 (-1.485, -3.875) | JOY_UP | east along Y -3.875, 0.10 | L1-L3 at (-0.85, -3.875) |
| 5 (-3.015, -4.775) | BTN_REC | west along Y -4.775, 0.10 | L1-L3 at (-3.75, -4.775) |
| 7 (-2.505, -4.775) | VMOT | into the row gap (Y -4.325), east along it, 0.15; it passes between lands 6/8 (both GND) and 1/4 | L1-L3 at (-0.85, -4.325) |
| 4 (-1.485, -4.775) | JOY_RIGHT | east along Y -4.775, 0.10 | L1-L3 at (-0.85, -4.775) |
| 8 (-1.995, -4.775) | GND | -Y, under the tail fold, 0.20 (lands 6 and 8 are no longer side by side; VMOT runs between them) | L1-L4 at (-1.995, -5.75), below the keep-out (Y -5.60) |

## R3.1 What each capacitor is and what the maker says (point 1)

Sources: SGM38046 sheet `design/datasheets/p3_sgm38046.pdf` page 3 (pin table), page 4 (Figure 1, typical application, and Table 1), page 15 ("Layout and Component Selection": "place the components as close as possible to the device and use wide and short traces for connections, especially for the high current loops in the outputs"; "If the flying capacitor is not placed close to the C1P/C1N pins, it may cause noise radiation"; "the EMI may be increased if the inductor is not placed close to SW1 and SW2 pins"; Figure 9, layout reference). nPM1304 specification `npm1304_datasheet_v1_0.pdf` section 9.3.4 page 160 ("The BUCK supply voltage should be decoupled with high performance capacitors as close as possible to the supply pins"; "All device grounds, VDD connections, and VDD bypass capacitors must be connected as close as possible to the device") and its CSP layout pages 162 and 163 (every capacitor beside the chip; read from the pictures). nRF54LM20A: Nordic's reference layout (NRF-PCB page 1: L1, C6 at the DCC/DECD balls).

| Cap | Net, pin | Role in its regulator | Rank (limit, pad centre to pin centre) | Round 2 distance (`capdist-r2.log`) |
|---|---|---|---|---|
| C21 4.7 uF 0603 | VBAT, U4 A1 PVIN | buck-boost input: pulsed current loop | must (1.5) | 7.02 |
| C24 10 uF 0603 | SGM_VOUT, U4 D1 | buck-boost output: pulsed current in boost mode ("high current loops in the outputs", page 15) | must (1.5) | 3.64 |
| C23 2.2 uF 0402 | C1P / C1N, U4 A4 / B4 | charge-pump flying capacitor (page 15) | must (1.5) | 2.93 |
| C27 4.7 uF 0603 | SGM_VON, U4 C4 | charge-pump output (pulsed) | must (1.5) | 9.00 |
| C22 10 uF 0402 | SGM_AVIN, U4 A2 | analog supply bypass ("Place a bypass capacitor", page 3) | should (3.0) | 1.38 |
| C26 4.7 uF 0603 | SGM_AVDD, U4 D2 | LDO output | should (3.0) | 8.67 |
| C25 10 uF 0603 | ELVDD, U4 D3 (OVDD) | LDO output to the panel | should (3.0) | 13.29 |
| C28, C29 22 uF 0402 | ELVSS, U4 D4 (OVSS) | LDO output to the panel | should (3.0) | 14.75, 2.82 |
| C74 10 uF 0402 | VSYS, U2 C7 PVDD | buck input ("BUCK supply voltage", 9.3.4) | must (1.5) | 0.89 |
| C78, C79 10 uF 0402 | VDD_1V8 at L71 pin 2, VDD_3V0 at L72 pin 2 | buck outputs (inductor current continuous; 9.3.4 names the supply side) | should (3.0) | 6.56, 2.81 |
| C75, C88 | VSYS, U2 C1/C2 | system rail bulk | should (3.0) | 6.71, 4.43 |
| C71, C72 | VBUS, U2 B1 | input | should (3.0) | 1.33, 4.31 |
| C85 | VBAT, U2 D1 | battery | should (3.0) | 0.87 |
| C80 100 nF, C73 | VDD_1V8; VBUSOUT | small bypass; VBUSOUT output | may | 6.42, 5.52 |
| C11 4.7 uF 0402 | U1_VBUS, U1 H9 | supply bypass (not a regulator) | should (3.0) | 4.68 |
| L1, C6 | DCC, DECD of U1 | U1's own DC/DC inductor and output | must (1.5) | 3.78, 0.80 |

## R3.2 The check (point 3)

`capdist.py <table>` prints each capacitor's distance (centre of its pad on the served net to the centre of the served pin; both pads for the flying capacitor) against its limit, and ends `RESULT FAIL n` when a must is over 1.5 or a should over 3.0. On the round 2 table: `capdist-r2.log` ends `RESULT FAIL 13`.

## R3.3 The search, and why no table meets the limits (point 2)

`make_placement3.py` keeps U1, U2, U3, U5, U6, J1, ANT1, the tail lands, the keep-outs, the RF parts, X1, U9, U11, C83, C84, L71, L72 and the round 2 parts next to U1 and U2; moves X2 0.40 mm (to (6.00, 3.75)) to open a place for C11; places L1 and C6 within 1.5 mm (found: 1.21 and 1.48); then tries the U4 block (U4 with L10 and its capacitors) at every place and rotation on a grid (X 1.0 to 7.25 by 0.25, Y -5.5 to -3.1 by 0.1, rotations 0, 90, 180, 270: 2,600 places), each time placing the four musts within 1.5 mm and then the U4 shoulds within 3.0 mm; every other part is placed afterwards as in round 2.

Result (`r3g.log`, `r3h.log`, `r3i.log`):
- **The four U4 musts can be met**, at one place: U4 at (3.00, -3.80), rotation 180, gives C21 1.10, C24 1.10, C23 0.92, C27 1.39 mm (`capdist-r3try.log`), with L10 at 3.12 mm from the SW pins (L10, the 2.5 x 2.0 coil, cannot come nearer than about 1.6 mm: its body is 1.17 mm from its pads across the pin side).
- **But then the U4 shoulds have no place**: C26 finds no free place anywhere within 9 mm of its pin, C25 lands 13.2 mm and C29 10.6 mm away, and the U1 and U2 shoulds C75 (3.91), C88 (4.12), C11 (3.13) pass their limits (`capdist-r3try.log` ends `RESULT FAIL 7`).
- With the U4 shoulds required too (`r3i.log`), none of the 2,600 places works: U4 itself overlaps (1,256), a must finds no place (1,222), L10 (110), C26 or C25 (12).
- Cause: the parts face is 82 percent full (R2.4) and the area round U4 is shared with U1's own supply parts (L1, C4 to C7, which must stay at U1's row A). The allowed means (moving bias resistors, rotating, the U4 block, X2, U9) free too little: the test pads already moved to the screen face in round 2.

What would free the room (not allowed in this round; for the lead): the 0603 parts of U4 (C21, C24, C25, C26, C27: 2.54 x 1.19 mm courtyard each, 3.02 mm2) in 0402 (1.685 x 0.84, 1.42 mm2) would free 8.0 mm2 next to U4; a part in 0402 needs the same value and voltage rating from a maker's sheet, which is the parts helper's question. Or the screen supply moves onto the screen's own tail (a part of the screen module), which is the screen maker's question.

## R3.4 Musts over 1.5 mm in the round 2 table, with their loop inductance (point 4)

Estimate: the connection is a track on L1 over the L2 ground at h 0.065 mm (c.2), 0.15 mm wide (net class PWR); inductance per length = Z0 x sqrt(eeff) / c with Z0 43.4 ohm and eeff 3.20 (Hammerstad-Jensen, `zcalc.py`, dielectric 4.1, copper 0.018) = 0.259 nH/mm (0.169 nH/mm at 0.30 mm wide); track length = 1.2 x the centre distance (one bend allowance, my figure); the return path is the L2 ground directly under the track, included in Z0.

| Part | Round 2 distance | Track (estimate) | Inductance at 0.15 mm | Nearest place found in round 3 |
|---|---|---|---|---|
| C21 (U4 PVIN) | 7.02 | 8.4 mm | 2.2 nH | 1.10 with U4 at (3.00, -3.80), rotation 180 |
| C27 (U4 VON) | 9.00 | 10.8 mm | 2.8 nH | 1.39, same |
| C24 (U4 VOUT) | 3.64 | 4.4 mm | 1.1 nH | 1.10, same |
| C23 (U4 flying) | 2.93 | 3.5 mm | 0.9 nH | 0.92, same |
| L1 (U1 DCC) | 3.78 | 4.5 mm | 1.2 nH | 1.21 with L1 at (3.67, -1.98) |
| C78, C79 (buck outputs, should) | 6.56, 2.81 | 7.9, 3.4 mm | 2.0, 0.9 nH | 1.60, 1.66 |

For the circuit simulation: put these inductances in series with each capacitor (and the same again in its ground return if the ground stack is not at the pad: the plan puts one stack at every ground pad, so the return adds little).

RESULT: blocked, no placement meets the round 3 limits on the 4-layer board's one face with the allowed means: the four U4 must-capacitors fit within 1.5 mm only if U4's output capacitors C26, C25, C29 lose their place, so placement-plan.csv stays the round 2 table, with the tail A exits reworked to the footprint (check PASS) and the loop inductances of R3.4 for the simulation.

---

# Round 4: regulator capacitors with the two new moves

Written 2026-11-13 from 02:04 to 02:45 (Mac clock). Inputs: the lead's round 4 ruling (moves 1 and 2); `design/ecad/ring/pcb/u4-capacitors.md` (last line: "RESULT: done, 4 of the 5 capacitors (C21, C25, C26, C27) can be 0402 with a smaller effective value, and C24 stays 0603 because 6.3 V is only 1.29 times its 4.9 V"). Scripts and logs in `design/wiring/ring-board-plan-work/`: `make_placement3.py`, `capdist.py`, `check_placement.py`, logs `r4a.log` to `r4m.log`, `r4-final.log`, `capdist-r4*.log`, `check_placement_r4*.log`.

**Result: a table passes both checks and is now `placement-plan.csv`** (the round 2 table is kept as `placement-plan-r2.csv`; the lead was told by one message at 02:42).

## R4.1 What the SGM38046 sheet says about a capacitor at the panel end (move 2)

Nothing. The sheet's layout text (`p3_sgm38046.pdf` page 15, "Layout and Component Selection") asks to "place the components as close as possible to the device" and to connect "the input and output bypass capacitors ... to the PCB ground plane"; Figure 1 (page 4) draws C5 (OVDD) and C8, C9 at the device. The word "panel" appears only in the product description (pages 1 and 14) and the thermal note (page 15); no sentence names a capacitor at the load end. So, as the lead ruled: one capacitor of each output rail at U4's ball; a second one (C29 on ELVSS) may sit at either end. ELVDD has only one capacitor (C25: `netlist.csv`, net ELVDD = C25, DISP1.2, J1.2, U4.D3), so C25 is at U4. In the passing table C29 is also at U4 (2.97 mm from D4); J1's ELVSS pin (pin 1) lies under J1's housing on the hand-end row, more than 3.0 mm from any free place.

## R4.2 Runs

| Run | Moves | Result (`capdist`) |
|---|---|---|
| r4a | move 2 only, five capacitors 0603 | FAIL 6: C26 has no place on the board; C25 13.2, C29 7.4, C75 3.9, C88 4.1, C11 3.1 mm |
| r4c to r4g | move 2 + C21, C25, C26, C27 in 0402 (the parts helper's subset) | r4g: PASS on the list of round 3 |
| r4h to r4m | the same, adding U1's VDD 10 uF C4 as a must (it is the input of U1's own DC/DC; same rule as C74) and C7 as a should | best before the last change: 1 overrun (C22 3.71) |
| **r4 (final)** | same; U1's DC/DC parts C4, L1, C6 placed by hand along U1's row A; U4's should capacitors placed in the order C26, C22, C25, C28, C29; U4 at (3.25, -3.80) rotation 180 (found by the grid search, 1,008 places) | **PASS** |

Every change kept within the ruling: four U4 capacitors in 0402; X2 shifted 0.90 mm toward +Y inside its zone (round 2 (6.00, 3.35) to (6.00, 4.25)) to open a place for C11 at U1's VBUS ball; C86 and C87 (load-switch outputs, no switching current) moved to free U2's east face for the VSYS capacitors; bias and series resistors moved. Not moved: U1, U2, U3, U5, U6, J1, ANT1, the band lands, the keep-outs, L71, L72, the RF parts. 48 of the 104 rows changed from round 2.

## R4.3 Checks

- Distance check `capdist.py placement-plan.csv` (`capdist-r4.log`) ends `RESULT PASS`. Values (mm, pad centre to pin centre): musts C21 0.90, C23 0.92, C24 1.30, C27 1.05 (U4); C74 0.89 (U2); L1 1.01, C6 0.90 (to L1's DECD pad, the inductor end of U1's DC/DC loop), C4 1.02 (U1); shoulds C22 2.81, C26 2.84, C25 2.59, C28 2.74, C29 2.97 (U4); C78 1.61, C79 1.66 (buck outputs at L71, L72 pad 2); C75 1.80, C88 2.06 (VSYS, nearest of U2's balls C1, C2, C7), C71 1.33, C72 2.20, C85 0.87 (U2); C11 1.52, C7 2.96 (U1). Mays: C80 4.82, C73 4.20.
- Placement check `check_placement.py placement-plan.csv` (`check_placement_r4.log`) ends `RESULT PASS` (104 parts, 85 parts face, 19 screen face; the U5-U3 courtyard note as in round 2).
- Broken copy (C21 moved 3.0 mm, C79 pushed past the edge): placement check `RESULT FAIL 5` (`check_placement_r4_broken.log`), distance check `RESULT FAIL 2` (`capdist-r4-broken.log`).
- Inductor L10 (SW1, SW2): 3.1 mm from the SW balls, as in round 3 (its 2.5 x 2.0 body keeps its pads at least about 1.6 mm away); ferrite FB1 (DECD to DECA of U1, not a capacitor): 3.2 mm from A6.

## R4.4 The new table

Command: `U4=3.25,-3.8,180 SUB=C21,C25,C26,C27 TAG=r4 run_kipy.sh make_placement3.py`, then the file is copied to `placement-plan.csv`. Rows (model mm; KiCad = model + (100, 100); face F = L1, B = L4):

| Ref | Footprint | Face | X | Y | Rot | Zone |
|---|---|---|---|---|---|---|
| U1 | WLCSP-61_nRF54LM20A-CAAA | F | 4.000 | 0.000 | 0 | U1 |
| C4 | Chip_0402 | F | 2.405 | -1.880 | 180 | Z1 |
| C5 | Chip_0201 | F | 1.247 | 0.522 | 270 | R3 |
| C1 | Chip_0201 | F | 6.010 | 0.350 | 90 | Z4 |
| C2 | Chip_0201 | F | 6.670 | 0.660 | 90 | Z4 |
| L1 | L_TDK_MLZ1608_1.6x0.8 | F | 4.475 | -2.005 | 0 | Z1 |
| C6 | Chip_0201 | F | 6.020 | -2.025 | 90 | Z1 |
| FB1 | Chip_0201 | F | 1.697 | 1.522 | 180 | R3 |
| C7 | Chip_0201 | F | 1.950 | 0.522 | 270 | R3 |
| C14 | Chip_0201 | F | 6.010 | -0.840 | 90 | Z4 |
| C10 | Chip_0201 | F | 5.420 | 1.710 | 0 | Z3 |
| R1 | Chip_0603 | F | 12.800 | -1.200 | 90 | Z3 |
| C11 | Chip_0402 | F | 5.673 | 2.474 | 0 | R3 |
| R2 | Chip_0201 | F | 1.300 | 2.500 | 90 | Z3 |
| X1 | XTAL_Kyocera_CX2016DB_2.0x1.6 | F | 3.000 | 3.000 | 0 | Z3 |
| X2 | XTAL_TXC_9HT11_2.0x1.2 | F | 6.000 | 4.250 | 90 | Z3 |
| L2 | Chip_0201 | F | 1.700 | -0.390 | 0 | Z2 |
| C3 | Chip_0201 | F | 1.100 | -1.310 | 90 | Z2 |
| L3 | Chip_0201 | F | 0.480 | -0.390 | 0 | Z2 |
| C12 | Chip_0201 | F | -0.120 | -1.310 | 90 | Z2 |
| L4 | Chip_0201 | F | -7.750 | 5.900 | 0 | Z8 |
| C13 | Chip_0201 | F | -8.300 | 4.980 | 90 | Z8 |
| ANT1 | ANT_Johanson_2450AT18D0100001E_3.2x1.6 | F | -10.800 | 5.250 | 180 | antenna |
| LT1 | Chip_0201 | F | -12.450 | 3.250 | 0 | antenna |
| C89 | Chip_0201 | F | -7.150 | 4.980 | 90 | Z8 |
| U2 | WLCSP-35_nPM1304-CAAA | F | 8.500 | 0.000 | 270 | Z5 |
| C71 | Chip_0402 | F | 10.400 | -2.130 | 0 | Z5 |
| C85 | Chip_0402 | F | 8.520 | -2.130 | 0 | Z5 |
| C88 | Chip_0603 | F | 11.200 | 0.757 | 0 | R3 |
| C86 | Chip_0402 | F | 11.600 | 5.400 | 0 | Z5 |
| C87 | Chip_0402 | F | 7.500 | 5.620 | 0 | Z5 |
| C72 | Chip_0201 | F | 11.140 | -1.057 | 270 | R3 |
| C73 | Chip_0201 | F | 8.300 | -4.900 | 90 | Z5 |
| C74 | Chip_0402 | F | 9.050 | 2.140 | 0 | Z5 |
| C75 | Chip_0402 | F | 10.300 | -0.857 | 270 | R3 |
| C76 | Chip_0201 | F | 11.800 | -0.500 | 90 | Z5 |
| C77 | Chip_0201 | F | 11.800 | -1.700 | 90 | Z5 |
| L71 | L_Murata_1269AS-H_2.5x2.0 | F | 12.020 | 3.750 | 0 | Z6 |
| C78 | Chip_0402 | F | 12.720 | 2.150 | 180 | R3 |
| L72 | L_Murata_1269AS-H_2.5x2.0 | F | 8.870 | 3.750 | 0 | Z6 |
| C79 | Chip_0402 | F | 9.870 | 5.350 | 0 | R3 |
| C80 | Chip_0201 | F | 8.700 | 5.600 | 90 | Z6 |
| R71 | Chip_0201 | F | 6.670 | -0.520 | 90 | Z4 |
| R72 | Chip_0201 | F | 6.670 | -1.700 | 90 | Z4 |
| R57 | Chip_0201 | F | 6.000 | 5.500 | 0 | Z4 |
| R58 | Chip_0201 | F | 11.900 | -2.800 | 0 | Z4 |
| U5 | LGA-8_Knowles_SPK0641HT4H-1_3.0x4.0 | F | -10.800 | -4.800 | 90 | Z7 |
| R31 | Chip_0201 | F | -7.300 | -5.100 | 90 | Z7 |
| C31 | Chip_0201 | F | -9.500 | -0.700 | 90 | Z7 |
| C35 | Chip_0402 | F | -8.250 | -5.350 | 90 | Z7 |
| U6 | LGA-8_Knowles_SPK0641HT4H-1_3.0x4.0 | F | 10.800 | -4.800 | 270 | Z11 |
| R32 | Chip_0201 | F | 13.250 | -4.900 | 90 | Z11 |
| C32 | Chip_0201 | F | 6.900 | 2.300 | 90 | Z11 |
| C36 | Chip_0402 | F | 8.250 | -3.400 | 90 | Z11 |
| U3 | LGA-9_CSNP32GCR01-BOW_8.0x6.2 | F | -5.000 | 0.000 | 0 | U3 |
| U10 | UQFN-16_SN74AXC4T774RSV_1.8x2.6 | F | -5.250 | -4.600 | 90 | Z15 |
| C81 | Chip_0201 | F | 0.650 | 1.750 | 90 | Z15 |
| C82 | Chip_0201 | F | 2.400 | -5.600 | 90 | Z15 |
| R60 | Chip_0201 | F | -7.900 | -3.900 | 90 | Z15 |
| R63 | Chip_0201 | F | -5.800 | 3.900 | 0 | Z15 |
| R64 | Chip_0201 | F | -9.500 | -2.600 | 90 | Z15 |
| R65 | Chip_0201 | F | -9.500 | 0.500 | 90 | Z15 |
| C60 | Chip_0402 | F | -4.350 | 4.000 | 0 | Z15 |
| C61 | Chip_0201 | F | -7.250 | -3.900 | 90 | Z15 |
| U4 | WLCSP-16_SGM38046_2.0x2.0_P0.5 | F | 3.250 | -3.800 | 180 | Z12 |
| L10 | L_Murata_1269AS-H_2.5x2.0 | F | 6.500 | -4.200 | 90 | Z12 |
| C21 | Chip_0402 | F | 4.900 | -3.450 | 90 | Z12 |
| C22 | Chip_0402 | F | 0.700 | -2.850 | 270 | Z12 |
| C23 | Chip_0402 | F | 1.600 | -3.300 | 90 | Z12 |
| C24 | Chip_0603 | F | 4.000 | -5.650 | 0 | Z12 |
| C25 | Chip_0402 | F | 0.300 | -5.850 | 180 | Z12 |
| C26 | Chip_0402 | F | 0.700 | -4.550 | 90 | Z12 |
| C27 | Chip_0402 | F | 1.600 | -5.050 | 90 | Z12 |
| C28 | Chip_0402 | F | -0.200 | -4.550 | 90 | Z12 |
| C29 | Chip_0402 | F | -0.200 | -2.850 | 270 | Z12 |
| R66 | Chip_0201 | F | 12.800 | 0.700 | 90 | Z12 |
| J1 | FPC_Hirose_FH35C-15S-0.3SHW | F | -11.650 | -0.150 | 270 | Z13 |
| J_BAND_A | J_BAND_A_BOARD | F | -2.250 | -4.325 | 0 | Z10 |
| J_BAND_B | J_BAND_B_BOARD | F | -2.250 | 4.325 | 0 | Z10 |
| U11 | X2SON-4_TLV755xxPDQN_1.0x1.0 | F | 0.000 | 4.200 | 0 | Z9 |
| C83 | Chip_0402 | F | 0.000 | 5.450 | 0 | Z9 |
| C84 | Chip_0402 | F | 1.270 | 5.000 | 90 | Z9 |
| R61 | Chip_0201 | F | -3.900 | 5.100 | 90 | Z9 |
| R62 | Chip_0201 | F | -4.600 | 5.100 | 90 | Z9 |
| U9 | USON-10_TPD4E05U06DQA | F | 3.120 | 5.200 | 90 | Z9 |
| TP1 | TESTPAD_0.8 | B | -3.950 | -1.050 | 0 | Z14 (L4) |
| TP2 | TESTPAD_0.8 | B | -5.000 | 0.000 | 0 | Z14 (L4) |
| TP3 | TESTPAD_0.8 | B | -3.950 | 0.000 | 0 | Z14 (L4) |
| TP4 | TESTPAD_0.8 | B | -6.050 | 0.000 | 0 | Z14 (L4) |
| TP5 | TESTPAD_0.8 | B | -5.000 | -1.050 | 0 | Z14 (L4) |
| TP6 | TESTPAD_0.8 | B | -6.050 | -1.050 | 0 | Z14 (L4) |
| TP8 | TESTPAD_0.8 | B | -6.050 | 1.050 | 0 | Z14 (L4) |
| TP9 | TESTPAD_0.8 | B | -5.000 | 1.050 | 0 | Z14 (L4) |
| TP11 | TESTPAD_0.8 | B | -5.000 | 2.100 | 0 | Z14 (L4) |
| TP12 | TESTPAD_0.8 | B | -7.100 | 1.050 | 0 | Z14 (L4) |
| TP13 | TESTPAD_0.8 | B | -2.900 | 0.000 | 0 | Z14 (L4) |
| TP14 | TESTPAD_0.8 | B | -3.950 | 1.050 | 0 | Z14 (L4) |
| TP15 | TESTPAD_0.8 | B | -6.050 | 2.100 | 0 | Z14 (L4) |
| TP16 | TESTPAD_0.8 | B | -6.050 | -2.100 | 0 | Z14 (L4) |
| TP17 | TESTPAD_0.8 | B | -7.100 | 0.000 | 0 | Z14 (L4) |
| TP18 | TESTPAD_0.8 | B | -7.100 | -1.050 | 0 | Z14 (L4) |
| TP19 | TESTPAD_0.8 | B | -5.000 | -2.100 | 0 | Z14 (L4) |
| TP21 | TESTPAD_0.8 | B | -3.950 | -2.100 | 0 | Z14 (L4) |
| TP22 | TESTPAD_0.8 | B | -3.950 | 2.100 | 0 | Z14 (L4) |

## R4.5 Changes other files need (added to h.1 and R2.6)

| File | Value now | Value needed | Reason |
|---|---|---|---|
| `design/ecad/ring/parts.csv`, `design/bom.csv`, `make_netlist.py` | C21, C26, C27 0603 4.7 uF (GRM188R61C475KAAJD); C25 0603 10 uF (GRM188R61C106KAALD) | C21, C26, C27 0402, Murata GRM155R61A475MEAAD (4.7 uF 10 V X5R); C25 0402, Murata GRM155R60J106ME15D (10 uF 6.3 V X5R); footprint Chip_0402 | `u4-capacitors.md` section 3 (effective capacitance at the rail voltage: about 2.4, 3.05, 2.55 and 2.7 uF) |
| `design/mech/thin/placement.csv` | U4 (4.000, -3.500); L10 (6.500, -3.500); X2 (5.500, 3.000) (and the round 2 values of R2.6) | U4 (3.250, -3.800), rotation 180; L10 (6.500, -4.200), 2.0 x 2.5; X2 (6.000, 4.250) | R4.2 |
| `design/wiring/ring-board-plan.md` h.2 | | add: SGM38046 output ripple with the four 0402 capacitors (effective 2.4 to 3.05 uF) at full white screen; U1 DC/DC ripple on DECD | `u4-capacitors.md` notes: the sheet gives no minimum capacitance |

RESULT: done, a placement with every must capacitor within 1.5 mm and every should within 3.0 mm of its pin passes both checks on the 4-layer board's one face (C21, C25, C26, C27 in 0402, U4 at (3.25, -3.80) rotated 180, X2 moved to (6.00, 4.25), 48 rows changed) and is now placement-plan.csv.

---

# Round 5: the smallest 0402 subset (lead's order)

Written 2026-11-13 from 02:42 to 02:53 (Mac clock). Lead's decision: C24 stays 0603 and is a must; subsets tried in the order {C21, C27}, {C21, C27, C26}, {C21, C27, C26, C25}; the first that passes both checks is used.

| Subset in 0402 | Runs | Best result (`capdist.py`) |
|---|---|---|
| {C21, C27} | full grid of 1,008 U4 places (`s1.log`), then 4 orders of U4's should capacitors x 4 best U4 places (16 runs) | FAIL: at best 2 overruns, for example C25 14.18 and C29 3.42 mm (U4 at (3.00, -5.00), rotation 180, `capdist-s1.log`); every run left C25, C26 or C22 without a place within 3.0 mm |
| {C21, C27, C26} | same 16 runs, then the full grid with the best order (`s2.log`) | FAIL: at best 2 overruns, for example C25 13.92 and C29 3.06 mm (U4 at (4.75, -4.00), rotation 0, `capdist-s2.log`); C22 3.53 and C29 5.05 with another order |
| **{C21, C27, C26, C25}** | round 4 (R4.2) | **PASS** (`capdist-r4.log`, `check_placement_r4.log`) |

So the table of round 4 stands, unchanged: `placement-plan.csv` (commands of R4.4). Its footprint column gives the size of each U4 capacitor: C21, C25, C26, C27 `OpenRing:Chip_0402`; C24 `OpenRing:Chip_0603`. The effective values under voltage and the deviation from the chip maker's table are recorded in `design/ecad/ring/pcb/u4-capacitors.md` for the board builder's notes and the build guide.

RESULT: done, the smallest 0402 subset that passes both checks is {C21, C27, C26, C25} (C24 stays 0603): the two smaller subsets leave two should capacitors over 3.0 mm, so placement-plan.csv stays the round 4 table that passes.
