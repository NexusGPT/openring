# How the custom panel connects to the main board in the thin block: options

Written 2026-11-13 from 20:30 (clock from `date`). Design read at the working tree said to be commit 7cac82ba (no git command run; the match is the lead's statement). Read only: every file named below. Coordinates: inside model mm, X along the finger (+X fingertip, -X hand end), Y across (+Y thumb and antenna side), Z up from the block underside. Logs in `logs/` of this folder.

Sources of the numbers (each line opens in the file named):
- Stack and plan: `logs/calc.log` (script `calc.py`, reads its inputs from the files and prints the file and line of each).
- Board: `logs/read_board2.log` (script `read_board.py`, run with KiCad's own Python through `design/ecad/ring/pcb/run_kipy.sh`, board file `design/ecad/ring/pcb/ring.kicad_pcb`, read only). The routed board is the one of the taller block: J1 on the screen face at (-4.933, -0.003) (`design/ecad/ring/pcb/placement-final.csv` line 80). No routed board with J1 on the under face at the hand end exists.
- Thin model v9: `design/mech/thin/out/v10/before/placement.csv` and `thin.py` (the v9 copies; the live folder is being rewritten by another helper).

## What every option shares (the stack, `logs/calc.log` lines 2 to 16)

| Z from the block underside | what | source |
|---|---|---|
| 0.40 | floor top | `thin.py` line 61 (`under=1.00, gap=0.05`), calc.log line 14 |
| 1.43 | land faces under the board (parts hang from here) | `thin.py` line 61 (`pad_t=0.02`), calc.log line 14 |
| 1.45 to 1.75 | main board 0.30 | placement.csv line 22 |
| 1.75 to 1.85 | foam frame 0.10 | placement.csv line 23 |
| 1.85 to 2.65 | panel, 0.80 | placement.csv line 24 |
| 2.65 to 2.75 | clear adhesive 0.10 | placement.csv line 26 |
| 2.75 to 3.1755 | flat cover glass 0.4255 | `design/look/s1/merged417flat-notes.md` lines 67 (seat 3.7200), 59 (top 4.1455), 60 (0.4255), shifted down by 0.9700 (`design/look/s1/out/work-flat/measure-flat-final-us9.log` line 89) |

Board top to glass underside: 2.75 - 1.75 = 1.00 = foam 0.10 + panel 0.80 + adhesive 0.10 (calc.log line 9). The glass top lands at 3.1755, inside the 3.20 mm block (`design/wiring/lead-decisions.md` line 18: "The block stays 3.20 mm"). No option below changes this stack: the panel never gets more than 0.80, and nothing of the connection may stand between the board's top face and the panel (0.10 of foam).

Consequence for every option (not a choice): the routed board carries J1 and eight 0201 parts (C1, C2, C5, C7, C14, FB1, R71, R72) on its screen face (`logs/read_board2.log` line 8, "face B (screen face): 21 parts"). In the thin block the screen face has 0.10 of foam over it, so these nine parts must move to the under face or be removed. This is board work in all three options.

## Option A: tail to J1 on the board's under face at the hand end (the 12 November plan)

What: the panel's tail, at most 5.0 wide (4.8 at its contact end, the width J1 takes for 15 contacts: `design/wiring/screen-cable-study.md` line 55), leaves the panel's hand end, folds down in the tail pocket of the end wall, folds under the board end and enters J1 (Hirose FH35C-15S-0.3SHW) on the under face at (-11.650, -0.150), turned 270, opening toward the hand end (placement.csv line 18).

- Height: J1 is 0.9 +-0.1 high (`screen-cable-study.md` line 59). It hangs from 1.43: at 0.9 it ends at 0.53, 0.13 above the floor; at the catalogue maximum 1.0 it ends at 0.43, 0.03 above the floor (calc.log lines 15, 16), the same room the two 1.00 mm microphones use. The stack above the board is unchanged: 3.1755 against the 3.20 block. With the lever open J1 is 1.8 high (line 59): the tail must be latched before the board goes into the body.
- Tail length: the path from the panel end to J1 is 3.487 mm (`screen-cable-study.md` line 117), with the tail's front face entry at s 2.04 (line 118) and 1.45 of insertion (line 60). The maker sets the final length from our drawing; the stock tail was 20 mm and that was the reason layout A failed (line 117: 16.513 mm with no place, line 118: 12.402 wide at J1).
- Pocket: model v9 has a tail pocket 0.55 x 5.4 x 2.0 at X -13.775 (`thin.py` line 530): X -14.05 to -13.50, metal left at the end 0.6 (calc.log line 50). With two 90 degree folds of inner radius 0.30 and a 0.14 tail the pocket must reach X -14.165 (wall left 0.485); at inner radius 0.70 the wall left is 0.085 (`screen-cable-study.md` line 119). So the tail's smallest bend radius, which the maker must state, decides the end wall: 0.30 or less keeps 0.485 of metal.
- Antenna: the tail centred on J1 spans Y -2.65 to 2.35 at 5.0 wide (Y -2.55 to 2.25 at 4.8): 0.75 (0.85) from the copper-free zone at Y 3.10, and 0.30 (0.20) into the radio corner's Y range from 2.05 (calc.log lines 45, 46). J1's housing stood 0.20 from the zone in this place (`screen-cable-study.md` line 200).
- Board area: J1's land field on the under face, X -13.325 to -9.975, Y -3.2 to 2.9 (3.35 x 6.1): 20.44 mm2, no courtyard of any part in it today; copper there: two ground tracks on F.Cu, four VDD_MIC segments on In1.Cu, two vias, the ground pour on all four layers (`logs/read_board2.log` lines 11 to 18). The under face has 133.39 mm2 free of courtyards of 342.15 (39.0 percent; line 9).
- Re-routing: J1 moves 6.717 mm toward the hand end (calc.log line 44). Its 11 signal and supply nets are routed today to J1 at X -6.41 and -3.53 (read_board2.log lines 98 to 108: ELVSS 13.31 mm, ELVDD 15.50, VDD_3V0 23.19, VDD_1V8 78.04 (the whole rail), SWIRE 13.45, LCD_TE 9.92, LCD_RST 13.08, LCD_CS 11.29, LCD_SCK 21.32, LCD_DCX 12.93, LCD_MOSI 15.22). Each must reach the hand end. The screen face (B.Cu) carries no track in the hand-end strip X -13.6 to -8.75, only the ground pour (read_board2.log lines 50 to 64: the B.Cu entry is the GND zone; the tracks listed there are on F.Cu, In1.Cu, In2.Cu); In1.Cu and In2.Cu there carry MIC1_DATA, SDC_CS, VDD_MIC, VDD_SD and MIC_A_CLK. So the board helper routes these nets on B.Cu (cutting the ground pour of the screen face at the hand end) and drops them with microvias to J1's lands; four layers stay (`lead-decisions.md` line 18). How much ground the screen face loses is not measured here.
- Asks of the maker: a tail of at most 5.0 width with a contact end for FH35C (0.2 +-0.03 thick at the contacts with its stiffener, 4.8 wide, 15 contacts at 0.3 pitch; `screen-cable-study.md` line 55; stock drawing `design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt` lines 115, 136), its bend radius, and a fold of 90 degrees twice within 0.55 mm of the panel end.
- Worse at: needs the board re-routed at the hand end (all 11 nets longer by about 6.7 mm), takes 20.44 mm2 of the under face and J1's 0.9 height; J1 has 2 reflow passes in its limit (`design/mfg/assembly/hotbar-joint.md` line 13).
- Better at: the panel can be tested before it goes in, swapped without heat, and the build guide keeps its connector step.

## Option B: tail hot-bar soldered to a row of lands on the board's under face (no connector)

What: the same path as A, but the tail's contact end is pressed by a hot bar onto 15 lands on the under face at the hand end, as the two band ribbons are joined (`design/mfg/assembly/hotbar-joint.md`).

- Where the lands could sit: X -13.45 to -12.25 on the under face (inside the edge band keep-out, which ends at X -13.45: read_board2.log line 92 'EDGE_BAND_2'). That strip, X -13.6 to -12.4, Y -2.65 to 2.35, has no courtyard and only the ground pour (read_board2.log lines 33 to 38).
- Land row: at the pitch this design already uses for a hot-bar joint, 0.30 lands at 0.51 pitch (`hotbar-joint.md` line 36), 15 lands make a row 7.44 long (calc.log line 47): the tail would be wider than the 5.0 limit and the tail pocket (5.4) would have to grow, and the row would come within reach of the copper-free zone. At 0.30 pitch with 0.15 lands the row is 4.35 long (calc.log line 48) and fits a 4.8 tail, but no file of this design gives hot-bar data at 0.30 pitch: the maker or a joint test decides.
- Height: tail plus solder about 0.14 under the board (flat parts 0.11 and joint 0.03 in the band ribbons: `thin.py` line 81 `joint=0.03`, line 80 `flex_fin=0.11` as the comparison), against J1's 0.9. Stack above the board unchanged (3.1755).
- Board area: about 1.2 x 5.0 = 6.00 mm2 (read_board2.log line 33) instead of 20.44; the same re-routing of 11 nets to the hand end as A.
- Build guide: the joint is made outside the body: the panel face down on a soft fixture, the board laid on its back with the foam, the tail folded 180 degrees round the board end onto the lands, the board's under face up, the hot bar presses down. This is the posture the band ribbons cannot use (`hotbar-joint.md` line 9: no arrangement works for them in place); here the board is free. The joined panel and board then go into the body as one unit, and the band ribbon joint (assembly step with the board parts face up on the fixture: `design/mfg/assembly/assembly.md` line 202) must then be made with the panel hanging under the board: the fixture changes.
- Asks of the maker: a solderable (or anisotropic film) contact end, its pitch, land size and joint process, and whether they make the joint themselves on our board.
- Worse at: no rework without heat (a bad panel means a de-bonded joint on a finished board), the panel cannot be tested in a socket before joining, a new fixture, the pitch question above.

## Option C: lands on the board's screen face at the hand end, panel shortened

What: no fold under the board. The board's screen face gets 15 lands at the hand end, X -13.40 to -12.85; the panel ends 0.05 short of them at X -12.80; the tail is soldered to them before the panel is laid down and folds back over onto the board.

- Cost in lit length: the panel's hand end moves from -13.675 to -12.80: 0.875 shorter (calc.log line 48), so the hand-end border grows by the same.
- Height: no pocket in the end wall and nothing under the board; the fold stays inside the 0.90 between board top and panel front.
- Board area: screen face lands only (the screen face is 89.9 percent free: read_board2.log line 10).
- Worse at: it contradicts the request for no black border (0.875 more at the hand end), and has the no-rework and pitch problems of B.

Rejected without a table: J1 on the screen face (as on the routed board) needs 0.9 above the board where the thin stack has 0.10.

## Judgement (mine; the lead decides)

Option A. It keeps the panel's interface standard (an FH35C contact end, the part this design already carries in its library, netlist and build guide), keeps the stack at 3.1755 inside the 3.20 block, allows a test and a swap of the panel without heat, and its only height risk (J1 at its 1.0 maximum leaves 0.03 above the floor) is the one the microphones already live with. Its cost is board work that every option shares in part (the nine screen-face parts must move anyway; B also moves the 11 nets to the hand end). B is the fall-back if the maker cannot make a 5.0 wide FH35C contact end or if the 0.9 of J1 is wanted for something else; C only if the maker cannot fold a tail at the hand end at all.

RESULT: done, three connection options are worked out from the thin model and the routed board (A: tail to J1 on the under face at the hand end, B: hot-bar lands there, C: lands on the screen face with a 0.875 shorter panel), A is judged best for the lead to decide, and the requirement page carries A with B and C as alternates.
