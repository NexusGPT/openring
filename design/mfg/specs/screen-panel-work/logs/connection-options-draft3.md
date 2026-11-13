# How the custom panel connects to the main board in the thin block: options

Written from the clock reading in `design/mfg/specs/screen-panel-work/logs/clock.log:1` (no git command run; the design version is the lead's statement). Read only: every file named below. Coordinates: X along the finger (minus: hand end), Y across (plus: thumb and antenna side), Z up from the block underside. Citations are `file:line` from the repository root, as in the requirement page.

Sources:
- Stack and plan: `design/mfg/specs/screen-panel-work/logs/calc.log` (script `calc.py`; it reads its inputs from the design files and prints the file and line of each).
- Board: `design/mfg/specs/screen-panel-work/logs/read_board2.log` (script `read_board.py`, run with KiCad's own Python through `design/ecad/ring/pcb/run_kipy.sh`, on `design/ecad/ring/pcb/ring.kicad_pcb`, read only). This routed board is the taller block's: J1 on the screen face at (-4.933, -0.003) (`design/ecad/ring/pcb/placement-final.csv:80`). No routed board with J1 on the under face at the hand end exists.
- Thin model v9: the copies in `design/mech/thin/out/v10/before/` (the live folder is being rewritten by another helper).

## What every option shares

| Z | what | source |
|---|---|---|
| 0.40 | floor top | `design/mfg/specs/screen-panel-work/logs/calc.log:14` |
| 1.43 | land faces under the board, parts hang from here | `design/mfg/specs/screen-panel-work/logs/calc.log:14` |
| 1.45 to 1.75 | main board 0.30 | `design/mech/thin/out/v10/before/placement.csv:22`, `design/mfg/specs/screen-panel-work/logs/calc.log:2` |
| 1.75 to 1.85 | foam frame 0.10 | `design/mech/thin/out/v10/before/placement.csv:23`, `design/mfg/specs/screen-panel-work/logs/calc.log:2` |
| 1.85 to 2.65 | panel 0.80 | `design/mech/thin/out/v10/before/placement.csv:24`, `design/mfg/specs/screen-panel-work/logs/calc.log:2` |
| 2.65 to 2.75 | clear adhesive 0.10 | `design/mech/thin/out/v10/before/placement.csv:26`, `design/mfg/specs/screen-panel-work/logs/calc.log:2` |
| 2.75 to 3.1755 | flat cover glass 0.4255 | `design/mfg/specs/screen-panel-work/logs/calc.log:7` (seat 3.7200 `design/look/s1/merged417flat-notes.md:67`, top 4.1455 `design/look/s1/merged417flat-notes.md:59`, both lowered 0.9700 `design/look/s1/out/work-flat/measure-flat-final-us9.log:89`) |

Board top to glass underside: 1.00 = foam 0.10 + panel 0.80 + adhesive 0.10 (`design/mfg/specs/screen-panel-work/logs/calc.log:9`). The glass top, 3.1755 (`design/mfg/specs/screen-panel-work/logs/calc.log:7`), stays inside the 3.20 block (`design/wiring/lead-decisions.md:18`). No option changes this stack: nothing of the connection may stand between the board top and the panel.

Consequence for every option: the routed board carries J1 and eight 0201 parts on its screen face (`design/mfg/specs/screen-panel-work/logs/read_board2.log:8`, `design/mfg/specs/main-board.md:6`). In the thin block that face has 0.10 of foam over it (`design/mech/thin/out/v10/before/placement.csv:23`), so these parts move to the under face. Board work in all three options.

## Option A: tail to J1 on the board's under face at the hand end (the plan of the thin model)

What: the panel's tail, at most 5.0 wide (4.8 at its contact end, the width J1 takes for 15 contacts: `design/wiring/screen-cable-study.md:55`), leaves the panel's hand end, folds down in the tail pocket of the end wall, folds under the board end and enters J1 (Hirose FH35C-15S-0.3SHW) on the under face at (-11.650, -0.150), turned 270 (`design/mech/thin/out/v10/before/placement.csv:18`).

- Height: J1 is 0.9 +-0.1 high, 1.8 with the lever open (`design/wiring/screen-cable-study.md:59`). Hanging from 1.43 it ends 0.13 above the floor at 0.9 and 0.03 above it at 1.0 (`design/mfg/specs/screen-panel-work/logs/calc.log:15`, `design/mfg/specs/screen-panel-work/logs/calc.log:16`). The stack above the board does not change (glass top 3.1755: `design/mfg/specs/screen-panel-work/logs/calc.log:7`). The tail is latched before the board goes into the block.
- Tail length: the path from the panel end to J1 is 3.487 mm (`design/wiring/screen-cable-study.md:117`); J1's entry is at s 2.04 along it (`design/wiring/screen-cable-study.md:118`) and the tail goes in 1.45 (`design/wiring/screen-cable-study.md:60`). The stock tail failed here by its size: 16.513 mm of it had no place (`design/wiring/screen-cable-study.md:117`) and it was 12.402 wide at J1 (`design/wiring/screen-cable-study.md:118`).
- Pocket: the thin model has a tail pocket 0.55 x 5.4 x 2.0 at X -13.775 (`design/mech/thin/out/v10/before/thin.py:530`): X -14.05 to -13.5, metal left at the end 0.6 (`design/mfg/specs/screen-panel-work/logs/calc.log:50`). The study of the stock tail used an inner bend radius of 0.30 and a 0.14 tail (`design/wiring/screen-cable-study.md:111`): the pocket then reaches X -14.165 and the wall keeps 0.485; at radius 0.70 it keeps 0.085 (`design/wiring/screen-cable-study.md:119`). So the maker's smallest bend radius decides the end wall.
- Antenna: the tail centred on J1 spans Y -2.65 to 2.35 at 5.0 wide, 0.75 from the copper-free zone and 0.3 into the radio corner's Y range (`design/mfg/specs/screen-panel-work/logs/calc.log:45`); at 4.8 wide Y -2.55 to 2.25, 0.85 and 0.2 (`design/mfg/specs/screen-panel-work/logs/calc.log:44`).
- Board area: J1's land field, X -13.325 to -9.975, Y -3.2 to 2.9: 20.44 mm2 with no part courtyard today (`design/mfg/specs/screen-panel-work/logs/read_board2.log:11`); copper there: two ground tracks on F.Cu (`design/mfg/specs/screen-panel-work/logs/read_board2.log:12`), four VDD_MIC segments on In1.Cu (`design/mfg/specs/screen-panel-work/logs/read_board2.log:13`), two vias (`design/mfg/specs/screen-panel-work/logs/read_board2.log:14`). The under face has 133.39 of 342.15 mm2 free of courtyards, 39.0 percent (`design/mfg/specs/screen-panel-work/logs/read_board2.log:9`).
- Re-routing: J1 moves 6.717 toward the hand end (`design/mfg/specs/screen-panel-work/logs/calc.log:43`). Its 11 signal and supply nets (`design/mfg/specs/screen-panel-work/logs/calc.log:51`) run today to J1's lands at X -6.41 and -3.53, for example ELVSS 13.31 mm and LCD_MOSI 15.22 mm of track (`design/mfg/specs/screen-panel-work/logs/read_board2.log:106`, `design/mfg/specs/screen-panel-work/logs/read_board2.log:116`). In the hand-end strip X -13.6 to -8.75 the tracks are on F.Cu, In1.Cu and In2.Cu only (`design/mfg/specs/screen-panel-work/logs/read_board2.log:37` to `design/mfg/specs/screen-panel-work/logs/read_board2.log:42`); the screen face B.Cu there has its ground pour and no track. So the nets can run on B.Cu to the hand end and drop by microvias to J1's lands; the board keeps 4 layers (`design/mfg/specs/screen-panel-work/logs/read_board2.log:4`). How much ground pour the screen face loses is not measured here.
- Asks of the maker: a tail of at most 5.0 width with an FH35C contact end, 0.2 +-0.03 thick at the contacts with its stiffener, 4.8 wide (`design/wiring/screen-cable-study.md:55`; the stock tail: `design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt:115`, `design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt:136`), and two 90 degree folds near the panel end (`design/wiring/screen-cable-study.md:116`).
- Worse at: the hand end of the board is re-routed (each of the 11 nets longer by about the 6.717 move: `design/mfg/specs/screen-panel-work/logs/calc.log:43`, `design/mfg/specs/screen-panel-work/logs/calc.log:51`), it takes the 20.44 mm2 field (`design/mfg/specs/screen-panel-work/logs/read_board2.log:11`), and J1 allows 2 reflow passes (`design/mfg/assembly/hotbar-joint.md:13`).
- Better at: the panel can be tested before it goes in and swapped without heat; the build guide keeps a connector step.

## Option B: tail soldered by hot bar to lands on the board's under face (no connector)

What: the path of A, but the tail's contact end is pressed by a hot bar onto lands on the under face at the hand end, as the two band ribbons are joined (`design/mfg/assembly/hotbar-joint.md:9`, 15 lands there).

- Where: the strip X -13.6 to -12.4, Y -2.65 to 2.35 has no courtyard (`design/mfg/specs/screen-panel-work/logs/read_board2.log:31`); the edge band rule keeps tracks and vias out up to X -13.45 (`design/mfg/specs/screen-panel-work/logs/read_board2.log:102`), so the lands sit from X -13.45 inward.
- Land row: at the hot-bar pitch this design uses, 0.30 lands at 0.51 pitch (`design/mfg/assembly/hotbar-joint.md:36`), 15 lands make a row 7.44 long (`design/mfg/specs/screen-panel-work/logs/calc.log:46`): wider than the 5.0 tail (`design/mfg/specs/screen-panel-work/logs/calc.log:45`) and the 5.4 pocket (`design/mech/thin/out/v10/before/thin.py:530`). At 0.3 pitch with 0.15 lands the row is 4.35 (`design/mfg/specs/screen-panel-work/logs/calc.log:47`) and fits a 4.8 tail (`design/wiring/screen-cable-study.md:55`), but no file of this design gives hot-bar data at that pitch: the maker or a joint test decides.
- Height: flex 0.11 + solder 0.03 = 0.14 under the board (`design/mfg/specs/screen-panel-work/logs/calc.log:55`), against J1's 0.9 (`design/wiring/screen-cable-study.md:59`). Glass top unchanged (`design/mfg/specs/screen-panel-work/logs/calc.log:7`).
- Board area: the strip, 6.00 mm2 (`design/mfg/specs/screen-panel-work/logs/read_board2.log:31`) instead of 20.44 (`design/mfg/specs/screen-panel-work/logs/read_board2.log:11`); the same re-routing as A.
- Build guide: the joint is made outside the block: panel face down on a soft fixture, the board on its back with the foam, the tail folded round the board end onto the lands, under face up, the hot bar pressing down. The band ribbons cannot use such a posture in place (`design/mfg/assembly/hotbar-joint.md:10`); here the board is still free. The joined panel and board go into the block as one, and the band ribbon joint, made today with the board parts face up on a fixture (`design/mfg/assembly/assembly.md:202`), is then made with the panel under the board: the fixture changes.
- Asks of the maker: a solderable contact end, its pitch, land size and joint process, and whether the maker makes the joint on our board.
- Worse at: no swap without heat, no socket test before joining, a new fixture, the pitch question.

## Option C: lands on the board's screen face at the hand end, panel shortened

What: no fold under the board. The board's screen face gets the lands at the hand end, X -13.4 to -12.85; the panel ends just short of them, at -12.8 (`design/mfg/specs/screen-panel-work/logs/calc.log:48`); the tail is soldered before the panel is laid down and folds back over onto the board.

- Lit length lost: the panel's hand end moves from -13.675: 0.875 shorter (`design/mfg/specs/screen-panel-work/logs/calc.log:48`).
- Height: nothing under the board and no end pocket; the fold stays in the 0.9 between board top and panel front (`design/mfg/specs/screen-panel-work/logs/calc.log:52`).
- Board area: screen face lands only; that face is 89.9 percent free (`design/mfg/specs/screen-panel-work/logs/read_board2.log:10`).
- Worse at: it adds 0.875 of black border at the hand end (`design/mfg/specs/screen-panel-work/logs/calc.log:48`), against the request for a face with no border, and it has the no-swap and pitch problems of B.

Rejected without a table: J1 on the screen face, as on the routed board: a 0.9 connector against the 0.1 foam gap, over by 0.8 (`design/mfg/specs/screen-panel-work/logs/calc.log:52`).

## Judgement (mine; the lead decides)

Option A. It keeps a standard contact end for the panel (the FH35C, already in this design's library, netlist and build guide: `design/ecad/ring/parts.csv:82`), keeps the glass top at 3.1755 inside the 3.20 block (`design/mfg/specs/screen-panel-work/logs/calc.log:7`, `design/wiring/lead-decisions.md:18`), lets the panel be tested and swapped without heat, and its height risk (J1 at its 1.0 maximum leaves 0.03 above the floor: `design/mfg/specs/screen-panel-work/logs/calc.log:16`) is the room the 1.00 microphones already use (`design/mech/thin/out/v10/before/placement.csv:11`). Its cost is board work that the other options share in part: the screen-face parts move in every option, and B re-routes the same nets. B is the fall-back if the maker cannot make an FH35C contact end of at most 5.0 width (`design/mfg/specs/screen-panel-work/logs/calc.log:45`); C only if no tail can fold at the hand end.

RESULT: done, three connection options are worked out from the thin model and the routed board, option A (tail to J1 on the under face at the hand end) is judged best for the lead to decide, and the requirement page carries A with B and C as alternates.
