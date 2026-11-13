# Screen cable study: can the STOCK cable of the screen reach J1?

Written 2026-11-13, 03:55 to 04:20 (Mac clock, `date`). Writer: the screen-cable helper. Repository read at commit 7ccf41a (master); files cited with their line as read. No design file was changed. Work files: `design/wiring/screen-cable-work/` (scripts, logs, maker crops marked as maker content in `README-maker-content.txt`).

Short answer: **no layout puts the stock cable inside the present ring.** The one layout that fits needs the block 0.97 mm taller (layout C). Every layout that keeps the block height fails on a printed number (sections 4.1 to 4.4).

Coordinates: inside-model mm, X along the finger (+X fingertip, -X hand end), Y across (+Y thumb and antenna side), Z up from the block underside (`design/mech/thin/thin.py` line 28). "s" = path length along the cable, measured from the panel end.

## 1. Which screen part and which connector

- **Screen: Tailor Pixels TOH095XVT-01.** Sources:
  - `design/bom.csv` line 10 (DISP1).
  - `design/architecture.md` line 833, section 17.30 (the newest section that names the screen): "version 1 keeps the present part, Tailor Pixels TOH095XVT-01".
  - `design/architecture.md` line 870 (17.32).
- **The other saved document is not the current part.** `display_TR095A120SPC.pdf` (Truly) is cited only as a power reference "same glass size" (`architecture.md` line 101).
- **Drawing used:** `design/datasheets/display_TOH095XVT-01.pdf`, page 5 (drawing V0, vectors). It is readable enough for the measurement, so the study is not blocked.
- **Connector: J1, Hirose FH35C-15S-0.3SHW(50).** Sources: `bom.csv` line 11; `design/wiring/ring-board-plan-work/placement-plan.csv` line 78.
  - Today's place: (-11.650, -0.150), face F, turn 270 degrees.
  - Face F is the board's under face, toward the floor (`ring-board-plan.md` line 20).
  - Maker documents: `design/datasheets/w1_hirose_fh35c_series_catalog.pdf`, pages 1 to 6.

## 2. The stock cable, measured

Method: `screen-cable-work/tail_measure.py` reads the vector lines of page 5 with PyMuPDF. Its log `tail_measure.log` ends `RESULT done`.

**Scale check.** The scale comes from the panel outline printed on the same page: 12.8 gives 5.1430 pt/mm in X, and 27.35 gives 5.1547 pt/mm in Y. Four other printed dimensions are re-measured at that scale as checks:

| Printed | Measured |
|---|---|
| 20 | 19.999 |
| 3.2 | 3.203 |
| 4.8 | 4.805 |
| 0.8 | 0.799 |

Raw vectors: `tail_vectors.log`.

The figures below run from the panel end (the end of the lower glass) along the cable. Y is from the panel's centre line, as seen in the front view (the lit face).

| Item | Value | How read (page 5) |
|---|---|---|
| Bond on the glass ledge | the cable lies on the ledge from 0.900 mm inside the panel end; bond fingers 0.101 to 0.900 inside, Y -5.805 to +5.805 | vectors; also `design/mech/light-path/light-path.md` lines 9 to 12 |
| Wide part | 12.401 wide (Y -6.198 to +6.204); straight sides to 11.496 mm beyond the panel end; outer corners r 0.50 (0.501 / 0.496); ends at 11.997 | vectors (no printed number) |
| Neck | 4.805 wide (Y -2.402 to +2.402); starts at 12.497 after inner fillets of r about 0.5; runs to the cable end | vectors; printed 4.8 |
| Cable end | 19.999 mm from the panel end | printed 20 |
| Contact field and stiffener | 16.796 to 19.999 (3.203 long), on the neck | printed 3.2; front-view grid and side view |
| Thickness at the contact end | 0.2 +-0.03 including the polyimide (PI) stiffener | printed "0.2+-0.03含PI补强" |
| Thickness elsewhere | **not printed.** The side view draws the cable 0.095 and the stiffener 0.101 thick; these are drawn lines, not dimensions. Start value for this study: **t = 0.14** (Hirose's reference single-sided FPC: coverlay 25 + adhesive 25 + gold 3 + copper 35 + adhesive 25 + base 25 µm, catalogue p6). Also run at t = 0.10. | side view vectors; catalogue p6 |
| Contact face | the contacts are on the BACK face, the face that lies on the ledge at the bond. The stiffener is on the front (lit) face. | back view draws the 15 fingers as pads "1 ... 15"; front view shows the stiffener grid; side view "Contact Side" leader |
| Contacts | 15 at 0.297 pitch (0.3) | back view finger edges |
| A line across the full width at 2.999 mm | its meaning is not labelled | vectors |
| Bend radius, cable layers, where the copper runs in the wide part | **not in the document** | none: `[not sourced]` |

What J1 takes (Hirose catalogue):
- **Any contact face.** FH35C is a "dual-sided" connector with top and bottom contacts (p1, features 1 and 6). Which face of the cable carries the contacts therefore never decides a layout.
- **The cable.** FPC 0.2 +-0.03 thick (p2, spec sheet p1). For 15 contacts it is F = 4.8 wide (p5). The stock cable matches both.
- **The housing** (p3):
  - 6.1 along the contact row (A).
  - 3.0 +-0.15 deep, leads 0.05 out on the FPC side and 0.15 on the lever side.
  - 0.9 +-0.1 high; 1.8 high with the lever open.
- **The cable in the housing** (p3 detail): it enters parallel to the board, its underside (0.35) above the board, and it goes in (1.45) from the front face.

## 3. Room in the ring

Stack. Source: `design/mech/thin/placement.csv` rows main_board, screen, cover_glass; and `thin.py` lines 269 to 271. Each script prints the stack on its first line.

| Layer | Z (mm) |
|---|---|
| Floor top | 0.40 |
| Lowest point allowed for 1.00 mm parts under the board | 0.45 |
| Board | 1.45 to 1.75 |
| Foam | 1.75 to 1.85 (0.10) |
| Panel | 1.85 to 2.65 (lower glass 0.40, ASSUMED split: `thin-notes.md` line 39) |
| Glass bottom | 2.75 |

Plan, measured at the ends of the block:
- **Panel and pocket:** panel X +-13.675; panel pocket face X +-13.725, Y +-6.45 (`body.md` line 89).
- **End wall:** the body's flat end face is at X +-14.650 from Z 1.0 up. So the metal at each end is **0.925** thick. From the body file `design/mfg/parts/body/body-us9.stl` by `end_wall.py`; its log `end_wall.log` ends `  Z 3.2..3.4: no vertex`.
- **Today's cable pocket:** 0.55 x 5.4 x 2.0 at X -13.775 (`thin.py` line 467).

**The board's two faces.**
- The under face carries every part. The space under it is 1.00 high.
- The screen face carries only the 19 test pads (`placement-plan.csv`, side B, at X -7.1 to -2.9).
- Board area use today: 281.3 of 342.2 mm² (82.2 percent; `ring-board-plan.md` R2.4).

**Antenna (`lead-decisions.md` row "W2, rule on places"; `placement-plan.csv` ANT1):**
- **Copper-free zone:** X -13.60 to -8.75, Y 3.10 to 6.30, on all layers.
- **Antenna:** ANT1 at (-10.80, 5.25).
- **Resin radio corner:** X -14.80 to -8.60, Y 2.05 to the skin (`body.md` line 143).
- **Maker rule:** "no other metallic components like batteries and displays directly underneath antenna" (Johanson, quoted in `ring-board-plan.md` e).

**What decides every layout: the stock cable's size against the room.**
- The cable is 20 mm long, and 12.4 mm wide for its first 12 mm.
- The direct path from the panel end to J1 is 3.5 mm. That leaves about 16.5 mm of cable with no place.
- The block offers two volumes large enough for the 12.4 x 12 mm wide part:
  - the space under the board, which the parts fill;
  - the panel-to-board space, which is 0.10 mm.

## 4. Layouts

**Fold radius.** The maker gives no bend radius. Fixed start value: inner radius **0.30 mm** (2.1 x t). It is checked again at **0.70** (the value the project uses for the band circuit, `thin.py` line 75). A real module must show the radius: section 6.

**Checker.** `screen-cable-work/cable_layouts.py <r_in> <t>` builds each path and checks it:
- The cable runs are built as true arcs and straight runs, cut into 0.05 mm boxes.
- The neighbours come from `placement-plan.csv` with their KiCad courtyards and heights.
- For every pair (cable run x part) it prints the smallest free space.
- Logs and their last lines:
  - `layouts_r030_t014.log`: `RESULT done r_in=0.3 t=0.14`
  - `layouts_r070_t014.log`: `RESULT done r_in=0.7 t=0.14`
  - `layouts_r030_t010.log`: `RESULT done r_in=0.3 t=0.1`

Numbers below are from r_in 0.30, t 0.14 unless stated.

### 4.1 Layout A: the cable stays at the hand end (screen as today)

**A1. Down the hand-end wall into J1 at its place.**
- **Path:** a 90 degree fold down at X -13.675, a drop in an end pocket, a 90 degree fold under the board, then into J1 (front face at X -13.275, opening toward -X).
- **Length:** the path needs 3.487 mm. That leaves **16.513 mm** of the 20 mm cable with no room drawn anywhere.
- **Width at J1:** at J1's entry (s 2.04) the cable is still **12.402** wide, where J1 takes 4.8.
- **End pocket needed:** X -14.165 to -13.725, 12.80 wide. Today's pocket is 5.4 wide. Wall left: 0.485 (at r_in 0.70: 0.085).
- **Free space** (only the worst pairs; negative = overlap):

| Cable against | Free space (mm) |
|---|---|
| Resin radio corner | -1.078 |
| ANT1 | -0.520 |
| Microphone U5 | -0.520 |
| Copper-free zone | 5.339 mm² covered in plan |

**A2. Bent back under the panel at the hand end, J1 on the board's screen face.**
- The geometry of layout C, mirrored to the hand end; the block grows 0.970.
- The wide part then lies over **15.054 of the zone's 15.52 mm²**, 0.40 above its copper layers.

**A hand-end layout cannot exist, for this reason.**
- Any hand-end path puts the wide part (Y -6.198 to +6.204) across the zone's Y band (3.10 to 6.30) between X -13.675 and the panel end plus the fold.
- It does so vertically in the end wall (A1) or flat under the panel (A2).
- The bond itself already lies over Y 3.1 to 6.2 at X -13.675 to -12.775 (open item S24).

**Verdict A1: DOES NOT FIT** (16.513 mm of cable with no place; 12.402 wide at a 4.8 connector; -0.520 to ANT1 and U5).
**Verdict A2: DOES NOT FIT** (15.054 mm² of the antenna's copper-free zone covered by the cable; block +0.970).

### 4.2 Layout B: screen turned 180 degrees, cable down the fingertip wall, folded in two layers under the board, J1 under face at the fingertip end

**Path:**
1. A 90 degree fold down at X +13.675.
2. A drop to the floor.
3. Layer 1 on the floor running -X, 9.586 long (X 4.089 to 13.675).
4. A half turn up.
5. Layer 2 at the J1 entry height running +X into a new J1, housing X 10.300 to 13.500, opening toward -X.

**Result:**
- **Fold too tight:** the half turn between the two layers has inner radius **0.185**. That is 0.115 under the 0.30 start value and 0.515 under 0.70.
- **Parts in the way:** the wide layers meet **36 under-face parts**, among them every 1.00 mm part of the fingertip half (worst pairs below).

| Cable against | Free space (mm) |
|---|---|
| L71, L72, L10, U6 | -0.480 |
| U4, L1 | -0.475 |
| U1 | -0.381 |

- **Microphone hole:** the floor layer passes 0.340 from U6's gasket over the microphone hole.
- **New J1 overlaps 12 parts:** R1 and C88 by -0.800, L71 by -0.397, and others.
- **Board area:** the 119.84 mm² strip under the two layers can hold only parts under 0.33 mm high. Placing the board's parts then needs **126.5 percent** of the board that is left.

**Verdict B: DOES NOT FIT.** Fold inner radius 0.185 < 0.30; 36 parts overlap; area 126.5 percent.

### 4.3 Layout C: screen turned 180 degrees, cable bent back under the panel at the fingertip end, J1 on the board's screen face

**Path:**
1. From the ledge (now at the fingertip end), a 90 degree fold down at X +13.675.
2. A straight drop of 0.330.
3. A 90 degree fold to -X at the J1 entry height Z 2.220.
4. A flat run under the panel. The cable floats 0.40 above the board and 0.53 under the panel.
5. Into J1 on the screen face.

**Where J1 goes:**
- J1 centre at (-4.933, -0.003), turned so its opening faces +X (toward the fingertip).
- Housing X -6.533 to -3.333, Y -3.053 to +3.047.
- The cable end lands at X -4.833 (s 20).

**Free space:**

| Pair | Free space (mm) |
|---|---|
| Cable to the board | 0.370 (stiffened end) / 0.400 (wide part, neck) |
| Cable to the lower glass | 0.500 |
| J1 to the panel | 0.050 |
| Cable or J1 to the antenna's copper-free zone | 2.218 |
| Cable or J1 to ANT1 | 2.478 |

- Copper-free zone covered: 0.000 mm².
- The fold's inner face meets the panel's end corner at 0.000 (analytic, s 0: the cable leaves the ledge at its edge). It never crosses the end face. One 0.05 mm box piece prints -0.013 there; that comes from the box method, not the geometry.

**Fold radius:**
- At this height the folds accept an inner radius up to **0.465** with the cable straight at J1 height, or **0.655** with the cable first laid down on the board and then rising 0.40 in the neck.
- At 0.70 the folds miss by 0.470 (straight) or about 0.05 (laid down): the block would need that much more height.

**Verdict C: FITS WITH CHANGES.** Each change and its size:

1. **Block height +0.970 mm** (3.20 to 4.17). This changes the outside shape and the glass seat height. **Owner decision.** It comes from J1 standing between board and panel: 0.9 +0.1 maximum height, plus 0.05 clearance, less today's 0.10 foam gap. With fold inner radius 0.70 it becomes about +1.02.
2. **J1 moves to the screen face** at (-4.933, -0.003), turned with its opening toward +X. It is removed from the under face at (-11.650, -0.150). This frees 6.1 x 3.35 mm at the hand end: J1's metal leaves the antenna corner, where it stood 0.20 from the zone.
   - The board gets parts on both faces: one more assembly pass.
   - J1's lands go on the last copper layer. Today that layer is the ground plane over U3 and U1 (`ring-board-plan.md` line 27).
   - J1 to the screen supply chip U4: 9.02 mm (today 15.34).
3. **Test pads.** 16 of the 19 test pads lie under J1's housing (-0.015 each). They move elsewhere on the screen face, which is free from X -3.2 to +13.5.
   - 11 pads lie under the cable in plan. They have no height and the cable floats 0.40 above them, so they can stay. They are reachable before the panel goes on.
4. **Fingertip end pocket** in the body: X 13.725 to 14.165, Y +-6.40, from Z 2.15 to the ledge top. Metal left to the skin: 0.485 (0.525 at t 0.10). Nothing is cut at the hand end; today's 0.55 x 5.4 tail pocket there is no longer needed.
5. **Foam FOAM1** (0.10) cannot stay as a frame round the board edge: the cable passes the whole width at the fingertip end. The panel hangs from the glass (clear adhesive ADH1 over the whole face, `cover-glass.md` line 6). Any spacer must leave X -4.8 to +14.2 open across Y +-6.4.
6. **Screen turned 180 degrees**, with two consequences:
   - **Software:** the picture is turned by one function (`firmware/docs/step4-report.md` line 7). The same report, line 50: "Which way the panel is turned on the real ring is not known."
   - **The lit area moves 3.6 mm toward the hand end.** The panel's active area lies 1.003 from one end and 4.751 from the ledge end (`light-path.md` section 1). Turned, it runs X -12.672 to +8.924. The glass print window today is X -9.318 to +12.268 (borders 5.33 at the hand end and 2.38 at the fingertip, `cover-glass.md` lines 39 to 40). It would become 1.98 at the hand end and 5.72 at the fingertip. **Owner question.**
7. **Assembly order:** the cable is plugged into J1 with the lever open (1.8 high) while the glass-and-panel unit is folded away like a book. Then the lever is closed and the panel folded down.
8. **Antenna:** the bond fingers leave the ledge over the antenna (S24 goes away). No metal comes nearer to it.

**C-thin** (same as C, but the panel is lifted only enough for the cable and the neck passes a board slot to J1 on the under face; same script):
- Block +0.090.
- The half turn round the 0.40 lower glass has inner radius **0.212** (0.088 under 0.30).
- The neck must turn down between X -2.238 and +2.062. A slot there meets **15 under-face parts** in plan, including U3 (also -0.800 to J1), the radio match L2, L3, C3, C12 and the crystal X1.

**Verdict C-thin: DOES NOT FIT** (fold 0.212 < 0.30; 15 parts in the slot's plan).

### 4.4 D (computed only, not laid against the parts): a chamber added beyond the fingertip end

The cable runs straight out of the ledge, makes one half turn down, and comes back into J1 at the board's fingertip end.

**Result:**
- **Block length:** the block grows **8.771 mm** longer (outside shape).
- **J1:** a J1 at that board end meets the 12 parts listed under B.

**Verdict D: DOES NOT FIT** without an 8.8 mm longer block plus a re-placement.

## 5. Recommendation and what it changes

**Option for the lead.**
- No layout carries the stock cable inside the present block (3.20 mm), the present board outline (27.2 x 12.6) and the present outside shape.
- **The cheapest way to use the stock module as sold is layout C, which costs 0.97 mm of block height.** That is an owner decision. The block would go from 3.20 to 4.17 mm, against the owner's "MUCH THINER NEEDED".

What C changes:
- **Board placement rows:**
  - J1 from (-11.650, -0.150, under face, 270) to (-4.933, -0.003, screen face, opening toward +X).
  - 16 test pads move off J1's footprint.
  - Nothing else on the under face moves, and the board outline does not change.
- **Body:** 0.97 mm taller; a fingertip end pocket 12.8 x 0.44 deep; the hand-end tail pocket goes.
- **Stack:** the panel-to-board space goes from 0.10 (foam) to 1.07, with no frame foam where the cable passes.
- **Cover glass:** the print window moves 3.6 mm toward the hand end.
- **Software:** the picture is turned 180 degrees.
- **Antenna:** better than today. J1's metal and the bond fingers leave the hand-end corner. The nearest cable or J1 metal is 2.218 mm outside the copper-free zone.

**What the other routes cost:**

| Route | What it needs |
|---|---|
| Any hand-end route | Copper over or inside the antenna's zone (5.3 to 15.1 mm²) |
| A thin route with a board slot (C-thin) | Moving U3, the radio match and the crystal |
| A route under the board (B) | Board area of 126.5 percent |
| A longer block (D) | 8.8 mm more length |

**If the owner refuses the 0.97 mm:** the stock module cannot be used, and open item S27 (a narrower cable from the screen maker) is the only route that keeps the block. The owner's rule forbids that route today. So the owner chooses between the two (questions below).

## 6. Not proven and limits

- **Fold radius:** the maker gives none. The 0.30 inner radius is a start value. Measure it on a real module: fold the wide part 180 degrees at 0.30, 0.45 and 0.65 over a mandrel, 10 cycles, then check all 15 lines for continuity and resistance.
- **Cable thickness:** away from the contact end it is not printed. The start value is 0.14 (Hirose's reference stack). Measure it with a micrometer on a real module. Layout C is not sensitive to it: +0.970 at t 0.10 and at 0.14.
- **Lower glass:** 0.40 is the model's assumed split (`thin-notes.md` line 39). It sets the C-thin half turn.
- **Copper in the cable:** where it runs inside the wide part is not drawn. The whole outline is treated as copper.
- **Part heights:** for 0201, 0603, MLZ1608, UQFN-16 and USON-10 they are start values (`[not sourced]`, listed in `cable_layouts.py` HEIGHT). Only layout B depends on them, and B fails on the fold and on 1.00 mm parts anyway.
- **Geometry method:** boxes, not the CAD solids of `thin.py`. The checker does not re-run the full model check. C must be built in the model (owner of `design/mech/thin/`) before it is called fitted.
- **A lower connector than FH35C:** it would cut C's 0.97. One check of Hirose's public page was refused (HTTP 403), and no other source was searched. Not proven either way.
- **A connector-free joint:** soldering or bonding the contact end straight onto board lands is not studied.

## 7. Round 2: how small can the growth of layout C become

Written 2026-11-13, 04:17 to 04:30 (Mac clock). Sections 1 to 6 above are unchanged.

### 7.1 C-solder: no connector, the contact end soldered by a hot bar on the board's screen face

**Which way the contacts look after the fold back.**
- Section 2: the contacts are on the face that lies on the glass ledge, so on the ledge they look down (-Z).
- In layout C the cable turns 180 degrees in one plane (fold 1) and runs -X under the panel. A turn in one plane turns the face with it, so **the contacts then look UP, at the panel, not at the board.**
- No bending in one plane can bring the contacts down while the cable still runs -X.
- **So C-solder needs a second half turn (fold 2):**
  - fold 2 sits in the neck at s 13.0;
  - after it the cable runs +X with the contacts down;
  - the stiffened end lies on the lands under the upper run.
- **A twist cannot replace fold 2.** It would make the neck's edges 2.02 times longer than the free neck (4.300 mm); a film does not stretch that far (`solder_r020_t014.log`).

**Height.**
- The two stacked runs and fold 2 set the height. Growth = 2 x inner radius + 2 x t.
- Checked by `screen-cable-work/cable_round2.py <r_in> <t>`, which uses the same box engine as sections 4.
- Joint 0.03 and land 0.02 as in `design/ecad/band/band-interface.md` section 3.

| Fold inner radius | Block growth (t 0.14) | Block height | Least free space (cable to panel / to board / upper run to lower run) | Fold 1 | Metal left at the fingertip end | Log, last line |
|---|---|---|---|---|---|---|
| 0.20 | +0.680 | 3.88 | 0.050 / 0.020 (the joint, by design) / 0.340 over the stiffened end | two quarter turns, straight drop 0.050 | 0.585 | `solder_r020_t014.log`: `RESULT done C-solder r_in=0.2 t=0.14 growth=0.680` |
| 0.30 | +0.880 | 4.08 | 0.050 / 0.020 / 0.540 | half turn, then a rise of 0.150 | 0.485 | `solder_r030_t014.log`: `RESULT done C-solder r_in=0.3 t=0.14 growth=0.880` |
| 0.45 | +1.180 | 4.38 | 0.050 / 0.020 / 0.840 | half turn, then a rise of 0.450 | 0.335 | `solder_r045_t014.log`: `RESULT done C-solder r_in=0.45 t=0.14 growth=1.180` |

- At t 0.10 and inner radius 0.20 the growth is +0.600 (`solder_r020_t010.log`: `RESULT done C-solder r_in=0.2 t=0.1 growth=0.600`).
- Every run prints -0.009 to -0.016 to the lower glass at s 0.07. As in section 4.3, that comes from the first box piece at the ledge's edge (analytic 0.000), not from the geometry.

**Antenna.** Copper-free zone covered: 0.000 mm². Least distance to the zone: 10.012 mm.

**Land pattern** (r_in 0.20; the place moves by at most 0.10 mm at the other radii):
- 15 lands, 0.15 across x 2.0 along X, pitch 0.30, gap 0.15. The board rule is 0.075 (`ring-board-plan.md` line 29).
- Place: X 5.425 to 7.425, centred on Y -0.003.
- Pin 1 at Y +2.097 and pin 15 at Y -2.103: pin 1 lies toward +Y. This was worked out from the back view of page 5 (pin 1 left, cable end down) and the final position: cable end toward +X, contacts toward -Z. The board check must confirm it, the way `check_band.py` confirms the band lands.
- The stiffened end lies at X 4.525 to 7.725.
- Lands to the nearest test pad: 7.875 mm.
- Land field to the screen supply chip U4: 4.95 mm (today J1 to U4: 15.34). U1 stands under the lands on the other face, X 2.39 to 5.61. The lands are on the last copper layer, today a ground plane, so the routing changes there.
- J1 leaves the board.

**The stiffener and the hot bar.**
- The 0.1 mm PI stiffener is on the face away from the contacts (section 2). After fold 2 it faces up, so the hot bar presses on the stiffener. The heat passes through the stiffener and the cable film into the joints.
- The band circuits are soldered the same way: through 0.11 mm of film and a 0.10 mm stiffener (`band-interface.md` line 60 and section 7). Same bar, same process.
- **Not proven** (none is printed in the screen maker's document):
  - that the gold contact fingers of this cable, made for a plug-in connector, take solder;
  - their gold thickness;
  - the heat the bond on the glass ledge tolerates. The ledge bond is 16.8 mm away along the cable.
- **Test before any ring:** hot-bar one module on a test board with the band settings (260 C, 4 s, 20 N, `band-interface.md` section 7); check all 15 lines for continuity and the 0.15 gaps for bridges; then light the screen.

**Assembly order:**
1. Pre-tin the 15 lands (stencil 0.05).
2. With the board out of the body and its screen face up, lay the stiffened end on the lands, contacts down. The cable lies flat toward -X and the glass-and-panel unit lies beyond the board's hand end.
3. Hot-bar it.
4. Fold 2: turn the cable back over the joint toward +X. The glass-and-panel unit now lies beyond the fingertip end.
5. Fold 1: turn the glass-and-panel unit over onto the board like a book.
6. Insert the unit in the body.
- **Rework:** a bad joint means removing the screen with heat. Count the screen as lost on a failed joint.

**Verdict C-solder: FITS WITH CHANGES.**
- Block +0.680 mm at fold inner radius 0.20, +0.880 at 0.30, +1.180 at 0.45.
- Plus every change of layout C (section 4.3) except J1, which is replaced by the 15 lands.
- It beats layout C (+0.97) only if the cable folds at inner radius 0.20 to about 0.34; at 0.345 both cost 0.97. An inner radius of 0.20 is 1.4 times the cable's 0.14 start thickness and is not proven: the fold test of section 6 must pass at 0.20.

### 7.2 C-low: the lowest connector found in a public maker document

**Search.**
- Hirose's site answered HTTP 403 to every page.
- JAE's and Amphenol's sites answered 403; Molex's and Panasonic's did not answer.
- Kyocera AVX answered. Its list of FPC connectors shows three 0.3 mm pitch series: 6293, 6841 and 6844. Their documents are saved:
  - `design/datasheets/w13_kyocera_6293.pdf` (SHA-1 c15064025887a61082c870493cea85f902836eae)
  - `design/datasheets/w13_kyocera_6844.pdf` (SHA-1 4cbbd40bf7cfe5a7c5e68c76e6486c0f45816f21)
  - The 6841 document was read but not saved: 6841 is vertical (stands upright), so it does not apply.

| Series | Kind | Height | 15 contacts | Cable | Fits the stock cable? |
|---|---|---|---|---|---|
| Hirose FH35C (today's J1) | contacts on both faces, back flip | 0.9 +-0.1 | yes | 0.2 +-0.03 | yes |
| Kyocera 6293, order code 04 6293 615 105 468+ | contacts on both faces, back flip | 0.90 +-0.10 (drawing, "ACTUATOR OPEN" view) | yes, A 4.2 / B 6.1 | 0.20 +-0.03, width A+0.6 = 4.8 | yes, the same height as FH35C |
| Kyocera 6844, order code 04 6844 715 002 846+ | bottom contact, one-touch lock | 0.95 +-0.05 | yes | 0.2 +-0.03, but the cable needs side ears (A+1.4 = 5.6 wide) for its lock | no: the stock cable is a straight 4.805 wide (section 2) |

Notes:
- The order codes are built from the "ORDERING CODE" line on each sheet, with "XX" = 15 positions.
- The 6844 table lists 15 positions (A 4.2, B 6.1, C 5.59), but its "APPLICABLE FPC" drawing gives the cable two side ears, and the stock cable has none.

**Verdict C-low:**
- No lower connector was found in a document I could open. Every connector found reaches 1.00 mm at its upper tolerance, so **the growth stays +0.97**.
- Not proven: makers whose pages refused me (Hirose, JAE, Molex, Panasonic, Amphenol) may print a lower part.

### 7.3 The other saved screen: Truly TR095A120SPC

- **The cable cannot be measured from the saved copy.**
  - `design/datasheets/display_TR095A120SPC.pdf` has 10 pages, a reseller copy (Panox Display, printed on every page).
  - Its contents (page 3) list "EXTERNAL DIMENSIONS", but no such page is in the file. Pages 1 to 10 are cover, revisions, contents, scope, general information, optical, interface, block diagram and timing.
  - No cable outline, width or length is printed anywhere in it.
- **Facts it does print** (page 5, page 8):
  - LTPS glass outline 12.8 x 27.35 and encapsulation glass 12.8 x 24.4: a ledge of 2.95, the same as Tailor Pixels.
  - Active area 10.8 x 21.6.
  - Glass 0.2 (LTPS) + 0.305 (encapsulation), total 0.78.
  - **30 contacts.** They include touch (TP_SDA, TP_SCL, VDD_TP, TP_INT, TP_RST) and two NFC pins. So its cable is not the 15-contact cable, and J1 (15 contacts) does not take it.
- **Verdict:** whether that module fits at 3.20 or with less growth: **not answerable from the files.** The missing page must come from Truly. Truly's public site answered, but I did not search it for a datasheet; contacting a maker is outside my rules.
- **What can be said from the printed numbers:**
  - Its thinner lower glass (0.2 against the 0.40 model value) would loosen fold 1 only.
  - The height of every C route is set by the connector, or by fold 2 in C-solder, not by fold 1.
  - So without a shorter or folded-by-the-maker cable, the Truly module would need the same growth.

### 7.4 Table for the owner

| Route | Block height | What it needs | Risks |
|---|---|---|---|
| Today's design with a narrower cable from the screen maker (open item S27) | 3.20 | a custom cable from Tailor Pixels; no change to the ring | against the owner's rule (work is offloaded to the screen maker); maker answer, fee and lead time unknown |
| C-solder, fold inner radius 0.20 | 3.88 (+0.68) | screen turned 180 degrees; stock screen; 15 lands on the board's screen face instead of J1; the hot bar already used for the band circuits; taller body with an end pocket; print window of the glass moved 3.6 mm | 0.20 fold not proven (1.4 x cable thickness); the plug-in gold fingers are not rated for solder by the maker; a bad joint loses the screen |
| C-solder, fold inner radius 0.30 | 4.08 (+0.88) | as above | as above, the fold less tight |
| C with J1 (Hirose FH35C, or Kyocera 6293 at the same height) | 4.17 (+0.97) | screen turned 180 degrees; stock screen and stock connector on the board's screen face; parts on both faces of the board; taller body; print window moved | fold up to inner radius 0.465 allowed; screen can be unplugged and replaced |
| C-solder, fold inner radius 0.45 | 4.38 (+1.18) | as C-solder | worse than C with J1 |
| Truly TR095A120SPC instead | not known | the missing dimension page from Truly; a 30-contact connector or lands | the module's cable is not drawn in any saved file |

## questions_for_owner

1. **Block height for the stock screen cable.**
   - Evidence: sections 4.3, 7.1 and 7.4. No layout at 3.20 mm fits (4.1, 4.2, 4.4).
   - Options:
     - (a) +0.68 mm (3.88), with the screen soldered (C-solder). It holds only if the fold test passes at inner radius 0.20.
     - (b) +0.97 mm (4.17), with a connector, so the screen can be replaced (C).
     - (c) Keep 3.20 mm and allow a cable made for us by the screen maker (S27).
   - My reading: (b), with (a) after a passing fold test. Both keep the module as its maker sells it.
2. **Screen turned 180 degrees.**
   - Evidence: every C route needs it; `cover-glass.md` lines 39 to 40.
   - The dark border of the face moves to the fingertip end: 5.72 there and 1.98 at the hand end, where today it is 5.33 at the hand end and 2.38 at the fingertip.
   - Option: accept the moved border (best reading), or no.
3. **The Truly module.** Should its full datasheet (the "EXTERNAL DIMENSIONS" page) be obtained so it can be measured?
   - Evidence: 7.3. The saved copy lacks the page; its interface has 30 contacts.

RESULT: done, the least growth found for the stock cable is +0.68 mm (C-solder, hot bar, fold inner radius 0.20, not yet proven) against +0.97 mm with a connector (no lower connector found in a readable maker document); the Truly cable cannot be measured from the saved copy.
