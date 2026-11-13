# Specification: custom full-face screen panel, reference DISP1

Requirement page for a panel maker. It asks for a custom self-lit colour panel (AMOLED or another self-lit type the maker proposes) that fills the top face of a smart ring, bonded under the ring's flat cover glass, and for the way its tail connects to the ring's main board. The maker answers the numbered questions at the end. All dimensions in mm. Coordinates: X along the finger (minus: the hand end, plus: the fingertip end), Y across the finger (plus: the thumb side, where the radio antenna is), Z up from the underside of the ring's top block. Each value names the design file and line it comes from (`file:line`); values computed from them are printed by the script `design/mfg/specs/screen-panel-work/calc.py` in its log `design/mfg/specs/screen-panel-work/logs/calc.log` (cited by line). Drawing: `design/mfg/specs/screen-panel-work/panel-envelope.svg` (top view and side view).

## What it is
One display panel with its own flexible tail, lying in a pocket of the ring's titanium block, between the main board (below) and the cover glass (above), bonded to the glass over its whole front face. The ring's owner asked for "a wide screen with no black border" (`design/wiring/lead-decisions.md:94`). The panel replaces a stock 0.95 inch 120 x 240 AMOLED (lit area 21.6 x 10.8, outline 12.8 x 27.35 x 0.8: `design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt:43`, `design/parts/thin-bezel-parts.md:37`), which is the reference below for the electrical interface. The block is the thin one, 3.20 mm (`design/wiring/lead-decisions.md:94`).

## Quantity per ring
1 per ring. The same panel for all ring sizes US 7 to 13: the block does not change with the size (`design/mfg/specs/cover-glass.md:51`).

## Material
The maker's choice of panel technology, stated in the answer (question 1). The front face must take an optically clear adhesive bond to glass over its whole area (section f, cover and bonding).

## Process
The maker's own. The tail and its contact end are part of the panel (section "How the panel connects in the thin block" below). Any folding of a drive area behind the panel is the maker's to propose: public sources describe a drive area "often bent 180° (COP - Chip on Plastic) to hide the driver IC" with a bend zone that "needs extra reinforcement and precise clearance" (`design/parts/thin-bezel-parts.md:21`), but give no border figure for a named folded part (`design/parts/thin-bezel-parts.md:92`); the maker states what it can do (questions 2 to 4).

## Finish and colour
Front face: the panel's black when off must match the black print of the cover glass round it (`design/mfg/specs/cover-glass.md:18`). Back face: flat, no part standing proud of the 0.80 envelope (section a; `design/mfg/specs/screen-panel-work/logs/calc.log:10`).

## General tolerance and tighter tolerances
Outline and thickness: the maximum values of section a are limits including the maker's tolerance (the stock part's thickness was 0.8 +-0.1: `design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt:101`, which would not fit; question 5). Lit area position against the outline: the maker states its tolerance (question 6).

## Critical dimensions

### a. The room the panel must fit (the envelope)

Stack in the block (each term with its source; sum in `design/mfg/specs/screen-panel-work/logs/calc.log:9`):

| Z from the block underside | layer | thickness | source |
|---|---|---|---|
| 1.45 to 1.75 | main board | 0.30 | `design/mech/thin/out/v10/before/placement.csv:22`, `design/mfg/specs/screen-panel-work/logs/calc.log:2` |
| 1.75 to 1.85 | foam frame, 1.2 wide round the board edge | 0.10 | `design/mech/thin/out/v10/before/placement.csv:23`, `design/mfg/specs/screen-panel-work/logs/calc.log:2` |
| 1.85 to 2.65 | the panel (this page) | 0.80 maximum | `design/mech/thin/out/v10/before/placement.csv:24`, `design/mfg/specs/screen-panel-work/logs/calc.log:2` |
| 2.65 to 2.75 | clear adhesive to the glass | 0.10 | `design/mech/thin/out/v10/before/placement.csv:26`, `design/mfg/specs/screen-panel-work/logs/calc.log:2` |
| 2.75 to 3.1755 | flat cover glass | 0.4255 | `design/look/s1/merged417flat-notes.md:60`; seat 3.7200 (`design/look/s1/merged417flat-notes.md:67`) and top 4.1455 (`design/look/s1/merged417flat-notes.md:59`) of the flat-glass block, each lowered by 0.9700 (`design/look/s1/out/work-flat/measure-flat-final-us9.log:89`) for the thin block: `design/mfg/specs/screen-panel-work/logs/calc.log:7` |

Sum from the board's top face (1.75) to the glass underside (2.75): 1.00 = 0.10 foam + 0.80 panel + 0.10 adhesive (`design/mfg/specs/screen-panel-work/logs/calc.log:9`). So the panel, with everything on its back (stiffener, driver chip if folded behind, tail bond), is at most 0.80 thick (`design/mfg/specs/screen-panel-work/logs/calc.log:10`). Thinner is welcome: the thin block was chosen to keep the ring thin (`design/wiring/lead-decisions.md:94`).

| name | value | tolerance | source |
|---|---|---|---|
| panel outline, along the finger, maximum | 27.35 | maximum, tolerance included | pocket 27.45 less 0.05 each side: `design/mfg/specs/body.md:67`, `design/mfg/specs/screen-panel-work/logs/calc.log:21` |
| panel outline, across, maximum | 12.8 | maximum, tolerance included | pocket 12.9 less 0.05 each side: `design/mfg/specs/body.md:68`, `design/mfg/specs/screen-panel-work/logs/calc.log:21` |
| panel corners | square or rounded, inside the outline above | maker states | the pocket corner is 0.1 radius: `design/mech/thin/out/v10/before/thin.py:528` |
| panel thickness, maximum, everywhere over its outline | 0.80 | maximum, tolerance included | `design/mfg/specs/screen-panel-work/logs/calc.log:10` |
| metal wall of the block round the pocket, under the glass | 0.925 at the ends and the sides | not the maker's | `design/mfg/specs/screen-panel-work/logs/calc.log:26` |

Keep-out zones (seen from above, drawn in the top view):
- Radio antenna corner: the antenna's copper-free zone of the main board, X -13.60 to -8.75, Y 3.10 to 6.30, all copper layers (rule area of the board: `design/mfg/specs/screen-panel-work/logs/read_board2.log:104`). The antenna maker asks for no metal parts such as "batteries and screens directly underneath antenna" (`design/wiring/ring-board-plan.md:347`). The panel lies above this zone. Requested: no driver chip, no tail bond, no tail conductor and no metal stiffener over X -13.675 to -10.6, Y 2.05 to 6.4 (the area named for this in `design/architecture.md:684`). The lit area may cover it if the maker states what metal its layers put there (question 9); the antenna is then tested with that panel.
- Ledge, bond area and tail exit: at the hand end only (X minus end), within the outline of section a, and inside Y -2.65 to 2.35 for the tail exit (a 5.0 wide tail centred on the board connector at Y -0.15: `design/mfg/specs/screen-panel-work/logs/calc.log:45`). A ledge or bond area across the whole width at the hand end would put metal over the antenna corner (keep-out above); the maker states where its bond and drive area sit (question 3).
- The back face lies 0.10 over the main board (`design/mech/thin/out/v10/before/placement.csv:23`) (foam frame round the edge, air in the middle): nothing may stand out of the back face.

### b. The lit area

Wanted: as near the whole glass face as the maker can make it. The glass face is 29.3 x 14.75 with 2.5 corners (`design/look/s1/out/measures-merged417flat-us9.json:43` to `design/look/s1/out/measures-merged417flat-us9.json:49`, `design/look/s1/merged417flat-notes.md:64`); its flat part, inside a 0.42 rounded edge, is 28.46 x 13.91 (`design/mfg/specs/screen-panel-work/logs/calc.log:25`). From the glass edge to the panel there is the block wall and the pocket clearance, 0.925 + 0.05 (`design/mfg/specs/screen-panel-work/logs/calc.log:27`), which the maker cannot change; the panel's own unlit border adds to it.

| unlit border of the panel, each side | largest lit area | lit area | black seen from the glass edge to the lit edge | source |
|---|---|---|---|---|
| 0.5 | 26.35 x 11.8 | 310.93 mm2, 1.333 times the stock part's 233.28 | 1.475 | `design/mfg/specs/screen-panel-work/logs/calc.log:27` |
| 1.0 | 25.35 x 10.8 | 273.78 mm2, 1.174 times | 1.975 | `design/mfg/specs/screen-panel-work/logs/calc.log:29` |
| stock part, for comparison | 21.6 x 10.8 | 233.28 mm2 | 1.98 on the long sides, 2.38 at the fingertip end, 5.33 at the hand end | `design/mfg/specs/cover-glass.md:38` to `design/mfg/specs/cover-glass.md:40`, `design/mfg/specs/screen-panel-work/logs/calc.log:27`, `design/mfg/specs/screen-panel-work/logs/calc.log:34` |

Corners of the lit area: rounded concentric with the glass corner is preferred: radius 1.025 at a 0.5 border, 0.525 at a 1.0 border (`design/mfg/specs/screen-panel-work/logs/calc.log:27`, `design/mfg/specs/screen-panel-work/logs/calc.log:29`); square is accepted. The maker gives the smallest unlit border it can make on each of the four sides (hand end, fingertip end, thumb side, other side), with the tail at the hand end (question 2). Public figures for stock bar panels are about 0.9 to 1.0 on the long sides and 2.5 to 2.9 at the ends (`design/parts/thin-bezel-parts.md:91`); this request asks for less.

### c. Resolution and pixels: two options to price

Today's software draws a 240 x 120 picture (landscape, long side along the finger) and turns it for a 120 x 240 panel, in 16-bit colour RGB565 (`design/firmware.md:350`; `firmware/modules/ring_screens/include/ring_screens/rscr_draw.h:15` to `firmware/modules/ring_screens/include/ring_screens/rscr_draw.h:16`). The stock pitch is 0.09 (21.6 / 240), 282 pixels per inch (`design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt:77`, `design/mfg/specs/screen-panel-work/logs/calc.log:34`).

| option | border 0.5 (lit 26.35 x 11.8: `design/mfg/specs/screen-panel-work/logs/calc.log:27`) | border 1.0 (lit 25.35 x 10.8: `design/mfg/specs/screen-panel-work/logs/calc.log:29`) | source |
|---|---|---|---|
| 1: the same 120 x 240 pixels | pitch 0.1098 along the finger, 0.0983 across: pixels 1.117 times longer than wide; with square pixels at 0.0983 the lit area is 23.59 x 11.8 | pitch 0.1056 along, 0.09 across: 1.173 times longer than wide; square at 0.09 gives 21.6 x 10.8 | `design/mfg/specs/screen-panel-work/logs/calc.log:36`, `design/mfg/specs/screen-panel-work/logs/calc.log:39` |
| 2: the maker's resolution at the stock pitch 0.09 | 292 x 131 pixels (1.328 times the pixels of today) | 281 x 120 pixels (1.171 times) | `design/mfg/specs/screen-panel-work/logs/calc.log:37`, `design/mfg/specs/screen-panel-work/logs/calc.log:40` |

What each costs the ring's software (for the maker's information; the ring maker decides):
- Option 1, non-square pixels: no code change; the 21 drawn screens (`firmware/docs/step4-report.md:8`) appear stretched along the finger by the ratio above. With square pixels, no code change and no stretch, but the lit area does not fill the face.
- Option 2: the picture size is a constant of the drawing code (`firmware/modules/ring_screens/include/ring_screens/rscr_draw.h:15`), but the 21 screens are laid out in pixels with fonts of 14, 16, 28 and 32 pixels and a margin of 18 pixels (`design/firmware.md:350`): each screen is laid out again and its saved reference picture (`design/software/os/screens/manifest.md:3` to `design/software/os/screens/manifest.md:23`) made again. One full picture grows from 57600 to 76504 bytes (border 0.5: `design/mfg/specs/screen-panel-work/logs/calc.log:37`) or 67440 bytes (border 1.0: `design/mfg/specs/screen-panel-work/logs/calc.log:40`), and its transfer at the 8 Mbit/s of the ring's display bus from 57.6 ms to 76.5 ms or 67.4 ms (`design/firmware.md:79`, `design/mfg/specs/screen-panel-work/logs/calc.log:38`, `design/mfg/specs/screen-panel-work/logs/calc.log:41`).
- Either option: a driver chip other than the stock one needs a new display driver in the ring software (`design/firmware.md:1090`).

### d. Electrical interface: the 15 contacts, asked unchanged

The board, its panel supply chip and the software's start order are made for these 15 contacts. Asked: the same contacts, functions and voltage ranges (contact k of the tail on contact k of the board connector, `design/ecad/ring/sch-notes.md:38`).

| contact | name | function | voltage | board net (source) |
|---|---|---|---|---|
| 1 | ELVSS | negative panel supply, from the panel supply chip | -2.3 to -2.1 V (`design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt:177`) | ELVSS (`design/ecad/ring/netlist.csv:38`) |
| 2 | ELVDD | positive panel supply, from the panel supply chip | 4.55 to 4.65 V (`design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt:181`) | ELVDD (`design/ecad/ring/netlist.csv:33`) |
| 3 | MTP | programming pin, not connected on the board | none | none (`design/ecad/ring/netlist.csv:387`) |
| 4 | VCI | driver chip analog supply | 2.7 to 3.6 V (`design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt:187`); the board gives its VDD_3V0 rail | VDD_3V0 (`design/ecad/ring/netlist.csv:336`) |
| 5 | IOVCC | driver chip interface and logic supply | 1.65 to 3.3 V (`design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt:191`); the board gives its VDD_1V8 rail | VDD_1V8 (`design/ecad/ring/netlist.csv:319`) |
| 6 | SWIRE | output of the driver chip that sets the panel supply chip | logic | SWIRE (`design/ecad/ring/netlist.csv:275`) |
| 7 | TE | tearing effect output | logic, IOVCC level | LCD_TE (`design/ecad/ring/netlist.csv:180`) |
| 8 | RESX | reset, active low | logic | LCD_RST (`design/ecad/ring/netlist.csv:174`) |
| 9 | CS | chip select | logic | LCD_CS (`design/ecad/ring/netlist.csv:165`) |
| 10 | SCL | serial clock | logic | LCD_SCK (`design/ecad/ring/netlist.csv:177`) |
| 11 | RS | data or command select | logic | LCD_DCX (`design/ecad/ring/netlist.csv:168`) |
| 12 | SDA | serial data in | logic | LCD_MOSI (`design/ecad/ring/netlist.csv:171`) |
| 13 | GND | ground | ground | GND (`design/ecad/ring/netlist.csv:92`) |
| 14 | GND | ground | ground | GND (`design/ecad/ring/netlist.csv:93`) |
| 15 | GND | ground | ground | GND (`design/ecad/ring/netlist.csv:94`) |

- Interface: 4-wire serial (SPI) with a data or command line (`design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt:49`); the ring's bus runs at up to 8 Mbit/s (`design/firmware.md:79`).
- Panel supply chip on the board: SG Micro SGM38046 (`design/ecad/ring/parts.csv:70`), set by the panel's SWIRE output (`design/ecad/ring/netlist.csv:276`). Its range: OVDD 2.8 to 4.6 V, OVSS -4.0 to -0.6 V, up to 90 mA for both together (`design/datasheets/p3_sgm38046.txt:37` to `design/datasheets/p3_sgm38046.txt:39`). The panel's ELVDD and ELVSS must lie in these ranges and its current at full white and full brightness must stay under 90 mA (question 12): the larger lit area draws more than the stock part.
- Start order the ring follows (stock maker's sheet page 9): VCI and IOVCC on in any order; reset low; supply chip enabled; wait 10 ms or more; reset high, wait 10 ms or more; start-up code and "sleep out", wait 120 ms or more; "display on", after which the driver chip starts SWIRE and the supplies 66.7 ms or more later (`design/firmware.md:381`). Off: "display off", "sleep in", wait 120 ms, supply chip off, reset low (`design/firmware.md:382`). The maker confirms this order holds for its panel or gives its own (question 13), and supplies its start-up code.
- What may differ, if the maker says so: the driver chip (with its command set and start-up code), the order of the 15 contacts on the tail (`design/ecad/ring/sch-notes.md:38`) (the board connector's wiring then follows), the number of ground contacts, the voltages inside the supply chip's ranges above.

### e. Cable and connection

Chosen (the design's present choice; the ring maker confirms with the panel maker's answer): a tail at most 5.0 wide leaving the panel's hand end, folding down at the hand end and under the main board into a 15-contact 0.3 mm pitch connector, Hirose FH35C-15S-0.3SHW (`design/ecad/ring/parts.csv:82`), on the board's under face at X -11.650, Y -0.150 (`design/mech/thin/out/v10/before/placement.csv:18`). The tail's contact end: 4.8 wide, 0.2 +-0.03 thick at the contacts including its stiffener (connector maker's figures, `design/wiring/screen-cable-study.md:55`; the stock tail had the same: `design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt:115`, `design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt:136`); the connector takes contacts on either face of the tail (`design/wiring/screen-cable-study.md:54`). Details and numbers in the section "How the panel connects in the thin block". Alternates the maker may propose: (B) the same path ending in a contact end soldered by hot bar to 15 lands on the board; (C) lands on the board's top face at the hand end with the panel shortened there. The maker may propose another way that keeps section a.

### f. Brightness, lifetime, cover and bonding, environment

- Brightness: at least 450 cd/m2 at the surface, the stock part's figure (`design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt:64`), measured under the cover glass and adhesive (question 14). The ring dims to level 85 of 255 for a sign that stays on while it records (`design/firmware.md:341`).
- Lifetime: the saved text copies of the stock sheet give none (searched: `design/mfg/specs/screen-panel-work/logs/grep-lifetime.log`). The maker states hours to half brightness at 450 cd/m2 (`design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt:64`) and at its own test level, and the burn-in it expects for a small red dot and a timer shown for hours (question 15).
- Cover and bonding: the panel is bonded under a flat chemically strengthened glass, 0.4255 thick (`design/look/s1/merged417flat-notes.md:60`), by 0.10 of optically clear adhesive over the whole front face (tesa 69404 in the design: `design/mfg/specs/cover-glass.md:6`, `design/mfg/specs/cover-glass.md:42`), so no air gap shows the edge of the lit area. The maker states whether it bonds the glass itself, which adhesive it qualifies, and the polariser or other front layers and their outline (the stock polariser was 12.2 x 23.8, smaller than the outline: `design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt:108`, `design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt:112`) (question 16).
- Environment: worn on a finger all day; the block is sealed round the glass (`design/mfg/specs/cover-glass.md:6`) but claims no water rating, so the panel sees skin heat and the humidity that passes the seal over time, and splash and sweat on the glass. The stock part's ranges: operating -20 to 70 C, storage -40 to 80 C (`design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt:83`, `design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt:86`), humidity 90 %RH max below 50 C (`design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt:230`): asked the same or wider, with the maker's humidity and temperature test and its result (question 17).

### g. Samples and quantities asked

Asked: unlit mechanical samples of the panel with its tail (for the fit in the block and the tail fold), then working samples with start-up code, then production. The maker states its smallest lot of each, its lead time for each, and its minimum production order (question 19). The numbers of samples and the order sizes the ring maker will ask for are set by the ring maker before the request goes out.

## What to inspect
On each sample: outline, and thickness at the centre and at 4 positions near the edges as for the cover glass (`design/mfg/specs/cover-glass.md:48`), against section a; lit area size and its position against the outline edges, on all four sides; tail width, length, contact end thickness, and its fit in the board connector; the tail fold at the hand end in a block sample (no crack, no lifted bond); start-up with the ring's own start order (section d) and current at full white; brightness under the bonded glass; colour of the off panel against the black print.

## Ring sizes
One panel for US 7 to 13 (`design/mfg/specs/cover-glass.md:51`).

## Files
Drawing: `design/mfg/specs/screen-panel-work/panel-envelope.svg`, made by `design/mfg/specs/screen-panel-work/make_envelope_svg.py` from `design/mfg/specs/screen-panel-work/logs/calc.log`. Board read: `design/mfg/specs/screen-panel-work/logs/read_board2.log`. Options worked out: `design/mfg/specs/screen-panel-work/connection-options.md`.

## How the panel connects in the thin block

Three ways were worked out (`design/mfg/specs/screen-panel-work/connection-options.md`). All keep the stack of section a: the glass top stays at 3.1755, inside the 3.20 block (`design/mfg/specs/screen-panel-work/logs/calc.log:7`, `design/wiring/lead-decisions.md:18`).

| | A: tail to a connector on the board's under face (chosen) | B: tail soldered by hot bar to lands there | C: lands on the board's top face, panel shortened |
|---|---|---|---|
| height under the board | connector 0.9 +-0.1 (`design/wiring/screen-cable-study.md:59`): 0.13 above the floor at 0.9, 0.03 at 1.0 (`design/mfg/specs/screen-panel-work/logs/calc.log:15`, `design/mfg/specs/screen-panel-work/logs/calc.log:16`) | tail 0.11 and solder 0.03, as the band ribbons (`design/mech/thin/out/v10/before/thin.py:81`) | none |
| tail | at most 5.0 wide, 4.8 at the contact end (`design/wiring/screen-cable-study.md:55`) | 4.35 row at 0.30 pitch, or 7.44 at the 0.51 pitch this design uses for hot bar (`design/mfg/specs/screen-panel-work/logs/calc.log:46`, `design/mfg/specs/screen-panel-work/logs/calc.log:47`) | as B |
| end wall pocket | 0.55 x 5.4 pocket at the hand end (`design/mech/thin/out/v10/before/thin.py:530`); with a tail bend of 0.30 inner radius (`design/wiring/screen-cable-study.md:111`) the wall keeps 0.485 of metal, at 0.70 only 0.085 (`design/wiring/screen-cable-study.md:119`) | as A | none |
| board area on the under face | 20.44 mm2, free of parts today (`design/mfg/specs/screen-panel-work/logs/read_board2.log:11`) | 6.00 mm2 (`design/mfg/specs/screen-panel-work/logs/read_board2.log:31`) | none (top face, 89.9 percent free: `design/mfg/specs/screen-panel-work/logs/read_board2.log:10`) |
| board work | connector moves 6.717 toward the hand end (`design/mfg/specs/screen-panel-work/logs/calc.log:43`); the panel nets ELVSS to LCD_MOSI re-routed on the 4 layers (`design/mfg/specs/screen-panel-work/logs/read_board2.log:4`) | as A | lands on the top face |
| lit length lost | none | none | 0.875 at the hand end (`design/mfg/specs/screen-panel-work/logs/calc.log:48`) |
| rework, test | panel can be tested and swapped | soldered: no swap without heat | as B |

Why A: a standard contact end, a panel that can be tested before it goes in and swapped without heat, and no loss of lit length. What it asks of the maker: the tail shape of section e and the smallest bend radius of the tail, which decides the metal left in the end wall. In all three, the main board loses the parts it carries today on its top face (the 0.10 foam gap, `design/mech/thin/out/v10/before/placement.csv:23`, leaves no room for them: `design/mfg/specs/screen-panel-work/logs/read_board2.log:8`).

## Questions the maker must answer
1. Which panel technology and which driver chip do you propose, and is the panel rigid or flexible?
2. The smallest unlit border you can make on each of the four sides (hand end with the tail, fingertip end, thumb side, other side), with the lit area outline and its position in a drawing.
3. Where your bond area, drive area and driver chip sit, flat or folded behind the panel, and their outline and thickness.
4. If the drive area is folded behind: the bend radius, the room it needs at the hand end, and whether everything stays inside the 0.80 thickness of section a (`design/mfg/specs/screen-panel-work/logs/calc.log:10`).
5. The panel thickness you can hold as a maximum including tolerance (section a asks 0.80 at most: `design/mfg/specs/screen-panel-work/logs/calc.log:10`), and the thinnest you can make.
6. The tolerance of the lit area position against the outline.
7. The price at option 1 (120 x 240) and option 2 (your resolution at the 0.09 pitch) of section c (`design/mfg/specs/screen-panel-work/logs/calc.log:34`), and which resolutions you can offer for the lit area you propose.
8. Pixel shape: can you make non-square pixels (option 1 at the full lit area), and what pitch can you make?
9. What metal your panel puts over the antenna corner of section a (the lit area layers, any conductor, any stiffener), so that the antenna can be tested with it.
10. Can your tail meet section e: at most 5.0 wide (`design/mfg/specs/screen-panel-work/logs/calc.log:45`), 4.8 wide and 0.2 +-0.03 thick at a contact end that fits the Hirose FH35C-15S-0.3SHW (`design/wiring/screen-cable-study.md:55`), leaving the hand end in the zone of section a?
11. The tail's smallest bend radius and how many 90 degree folds it takes in assembly (`design/wiring/screen-cable-study.md:116`); the tail length you need from our drawing.
12. ELVDD and ELVSS of your panel and its current at full white and full brightness, against the supply chip's ranges of section d.
13. Does the start order of section d hold for your panel? Send the start-up code and the sheet page with your power on and off sequence.
14. Brightness at the surface under 0.4255 of glass (`design/look/s1/merged417flat-notes.md:60`) and 0.10 of clear adhesive (`design/mfg/specs/cover-glass.md:42`).
15. Lifetime to half brightness, and burn-in of a small static sign shown for hours.
16. Do you bond the cover glass yourselves, with which adhesive, and what front layers (polariser) does the panel have, with their outline?
17. Operating and storage temperature and humidity, and the tests behind them.
18. Do you prefer option B (hot bar) or another way to connect to our board, and if so with what pitch, land size and joint process?
19. Your smallest lot and lead time for mechanical samples, for working samples, and your minimum production order.

## Open points
1. The lit area's corners, border and resolution: the maker's answer (questions 2, 7, 8).
2. The panel's metal over the antenna corner: the maker answers (question 9), then the antenna is tested with that panel (`design/architecture.md:684`).
3. The connection: A is the design's choice; the maker's answer to questions 10, 11 and 18 confirms it or opens B or C (`design/mfg/specs/screen-panel-work/connection-options.md`).
4. Sample numbers and order sizes are not set in any design file: the ring maker sets them before the request goes out.

## Source lines
`design/wiring/lead-decisions.md:94` (the decision), `design/wiring/lead-decisions.md:18` (board and block); `design/mech/thin/out/v10/before/placement.csv:18`, `design/mech/thin/out/v10/before/placement.csv:22` to `design/mech/thin/out/v10/before/placement.csv:26`; `design/mech/thin/out/v10/before/thin.py:61`, `design/mech/thin/out/v10/before/thin.py:528`, `design/mech/thin/out/v10/before/thin.py:530`; `design/look/s1/merged417flat-notes.md:59` to `design/look/s1/merged417flat-notes.md:67`; `design/mfg/specs/body.md:67` to `design/mfg/specs/body.md:68`; `design/mfg/specs/cover-glass.md:6`, `design/mfg/specs/cover-glass.md:38` to `design/mfg/specs/cover-glass.md:42`; `design/ecad/ring/netlist.csv` (J1 and DISP1 rows); `design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt`; `design/datasheets/p3_sgm38046.txt:37` to `design/datasheets/p3_sgm38046.txt:39`; `design/firmware.md:350`, `design/firmware.md:381` to `design/firmware.md:382`; `design/wiring/screen-cable-study.md:54` to `design/wiring/screen-cable-study.md:60`, `design/wiring/screen-cable-study.md:119`; the research files `design/parts/full-face-screen.md`, `design/parts/thin-bezel-parts.md`, `design/parts/thin-bezel-products.md`.

## What in other design files must follow once a maker answers
| file | what |
|---|---|
| `design/mfg/specs/cover-glass.md` | the glass is flat, 0.4255 thick (`design/look/s1/merged417flat-notes.md:60`), on the thin block (`design/mfg/specs/cover-glass.md:28` to `design/mfg/specs/cover-glass.md:35` describe the curved glass); the unprinted window takes the maker's lit area and position (`design/mfg/specs/cover-glass.md:36` to `design/mfg/specs/cover-glass.md:40`); the print colour is matched to the new panel off (`design/mfg/specs/cover-glass.md:18`) |
| `design/mfg/specs/body.md` | the panel pocket (`design/mfg/specs/body.md:67` to `design/mfg/specs/body.md:68`) if the maker's outline differs; the tail pocket at the hand end and the end wall left after it (from the maker's bend radius) |
| `design/ecad/ring/pcb/ring.kicad_pcb`, `design/ecad/ring/pcb/placement-final.csv`, `design/mfg/specs/main-board.md` | J1 back to the under face at the hand end (option A) or lands (B, C); the eight 0201 parts of the top face (`design/mfg/specs/main-board.md:6`) moved to the under face; the panel nets ELVSS to LCD_MOSI re-routed |
| `design/ecad/ring/netlist.csv`, `design/ecad/ring/parts.csv`, `design/ecad/ring/sch-notes.md` | DISP1's part number, and the contact order if the maker changes it; the supply chip's settings if ELVDD or ELVSS change |
| `design/bom.csv` | DISP1 line (today the stock part) |
| `design/firmware.md` (`design/firmware.md:348`), `firmware/modules/ring_screens/include/ring_screens/rscr_draw.h` | resolution, start order, start-up code, driver chip; under option 2 the 21 screens (`firmware/docs/step4-report.md:8`) laid out again |
| `design/software/os/screens/manifest.md` | the 21 reference pictures (`firmware/docs/step4-report.md:8`) made again if the resolution changes |
| `design/mech/thin/` (inside model) | panel outline, thickness, ledge or folded drive area, tail path and pocket |
| `design/architecture.md` (open item S24: `design/architecture.md:684`) | the antenna case with the maker's metal over the corner |
| `design/mfg/assembly/assembly.md` | the panel connection step (connector latch, or the hot-bar joint and its fixture for B) |
| `design/ecad/risk-review.md` (`design/ecad/risk-review.md:11`) | the start order checked again against the maker's sheet |
| `design/datasheets/` | the maker's sheet and drawing, saved |
