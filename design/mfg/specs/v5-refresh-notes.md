# v5 refresh of five maker spec pages: changed places

Files: body.md, joystick-nub.md, main-board.md, cover-glass.md, band-flex-tails.md (all in design/mfg/specs/). Line numbers are the lines in the files as they stand now. Sources: TN = design/mech/thin/thin-notes.md (section Model v5, lines 99 to 200); AR = design/architecture.md section number (17.11, 17.15, 17.19, 17.21, 17.22, 17.23, 17.24); MP = design/mech/mic-path/mic-path.md; LP = design/mech/light-path/light-path.md; AS = design/mfg/assembly/assembly.md. No number was invented. Per-size values (motor angle, protection circuit start, floor slot depth) are written at US 9 with one sentence that the per-size value follows from the next model version (AR 17.24). Flange 6.9 and the 6.4 x 6.4 stiffener are written as "to follow" (AR 17.24 rulings K12, K13).

## Remaining hits of the bar grep (v5-refresh-grep.log, exit 0, 8 lines)
Each hit names a former value ("before v5") or says the thing does not exist. None states an old value as current.
- joystick-nub.md:6 "record button": "the ring has no record button". Also "Before v5: four switches in a cross at 2.1 mm at +150 degrees" (former value, named).
- body.md:8 "record button", "record cap", "150 degrees": "no record button, no record cap"; "Before v5 this page listed ... the joystick at 150 degrees".
- body.md:78 "51 deg", "7.0 mm | " not matched as current: "before v5: 7.0 mm at 51 deg".
- body.md:90 "microphone slot": "no microphone slot exists in any wall".
- body.md:122 "51 deg": "before v5 it set the motor at 51 deg".
- band-flex-tails.md:9 and :40 "record button": "no record switch and no record button".
- band-flex-tails.md:35 "four switches": "before v5: four switches plus a record switch".

## Changed lines
| file:line | old (short) | new (short) | source |
|---|---|---|---|
| body.md:3 | Y +Y thumb side; plus is the thumb side | -Y is the joystick side; minus is the joystick side; joystick -78, motor -44 | AR 17.11; AR 17.15; TN line 53 |
| body.md:8 | 2 microphone slots, record cap, 4 charging-pad holes | floor pockets, holes and seats; joystick opening and pocket; one control, no record cap; no pad holes | AR 17.11, 17.12, 17.19 |
| body.md:20, :111 | pad holes masked | microphone seats masked | AR 17.12, 17.19 |
| body.md:62 to 66 | microphone slot length 1.2, height 0.3, X 11 | floor pocket 4.4 x 3.35 x 0.10 (X -13.0 to -8.6 and 8.6 to 13.0, Y -6.45 to -3.10; floor 0.305); hole dia 1.0 at X +-11.77, Y -4.8; seat dia 2.0 x 0.10; ring 0.205; metal 0.720 | MP lines 71 to 75, 79; TN "Measured on the built geometry"; AR 17.24 |
| body.md:71 to 77 | frame 6.4 x 5.4 at 150 deg; position 150 deg; record cap opening and position (88 deg) | opening 6.6 x 5.6 at -78; frame 6.4 x 5.4; pocket 7.0 x 6.8, r 9.775 to 10.955, metal 0.500; flange 6.9 to follow; metal 0.57 and 1.11 | TN lines 53, 163 to 176, K12; AR 17.15, 17.24 |
| body.md:78 to 81 | motor 7.0 x 2.1 at 51 deg, metal 0.400 | 5.0 (pocket 5.2) x 2.5 (pocket 2.6) at -44 deg (US 9), 0.7 off centre line, metal 0.425; per size to follow | TN lines 163 to 176; AR 17.15, 17.24 |
| body.md:82 | pad holes dia 1.0 at -150 deg, X +-0.8, +-2.4 | no pad holes; four 1.6 mm pads in the liner | AR 17.12, 17.15 |
| body.md:83 (new) | none | glass seat lowered 0.05 for SEAL1 | TN "Assembly inputs"; AS K-A4; AR 17.23, 17.24 |
| body.md:90 | Mic slot Z = 0.96 | slot depth 1.2 at US 9, per size to follow; fold room 2.6 x 2.2 x 1.03; channel ends at 30 deg; no microphone slot | TN K25, K-A6 line, lines 163 to 176; AR 17.24 |
| body.md:93 | mic slot and pad hole inspection | opening, microphone holes and seats, motor pocket 5.2 x 2.6 at -44 | same rows above |
| body.md:96, :102 | all pockets identical across sizes; model checks US 9 only | motor angle and slot depth per size; US 9 pass, US 7 and 13 fail, others not run; US 5 and 6 out of v1 | AR 17.17, 17.24 |
| body.md:110, :114, :116, :118, :119 | record cap clearance; open point 7, 9; (new 11, 12) | motor and nub clearance; per-size note; opening 6.6 x 5.6; ring 0.205 (S23); sealing (S26) | AR 17.24, 17.23 |
| body.md:122 | 17.10 wins, motor at 51 deg | 17.11, 17.12, 17.15, 17.19, 17.23, 17.24 win | AR |
| body.md:117 to 119 numbering | 10 after 12 | 10 moved above 11 and 12 | layout only |
| joystick-nub.md:3, :6, :9 | at the bottom of the band (+150); four switches; cross 2.1; two-opposite-switch centre press | -78 on the joystick side; five switches; cross 2.4; SW2 centre; 1.0 s long press | TN lines 163 to 176; AR 17.11, 17.15 |
| joystick-nub.md:27 to 37 | nub/frame "along the band" and "across the band"; 150 deg; band 3.6 thick 135 to 165; cross 2.1 | along the finger / around the band; -78; pocket 7.0 x 6.8; flange 6.4 and 6.9 to follow; cross 2.4; SW2 0.15 to dome; stiffener 6.4 x 6.4 to follow | TN lines 163 to 176, K12, K13, "Cross under the turned nub"; AR 17.24 |
| joystick-nub.md:43, :46, :49, :60, :61, :64 | 40 ms centre press; four switches close; 150 deg; B6 centre post; cross 2.1 vs 1.9 | SW2 first choice, 40 ms fallback; five switches; -78; B6 text; cross 2.4 and overlap figures; sources | AR 17.11, 17.15, 17.24; TN |
| main-board.md:3 | none | refreshed note; -Y joystick side | AR 17.24 |
| main-board.md:31 | notch "thumb side" | +Y side, away from the joystick | AR 17.11 |
| main-board.md:33 | joystick notch 2.8 and 0.6 (two rows) | none (no notch since v3) | TN line 171 and C13 |
| main-board.md:34 to 38 (new) | none | hole dia 0.50 at X -12.425, Y -2.95; LED1 at X -9.70, Y -2.10; U11 X 0.0, Y 4.2; C83 X 0.0, Y 5.45; C84 X 1.2, Y 5.0; keep-free X -3.5 to -0.9, Y +-3.4 to +-5.6 | TN line 171 and "Motor electronics", "Recording light"; AR 17.21, 17.22; LP "copper pad to hole 0.20" |
| main-board.md:39 | fill 57 percent | 72 percent, layout answers | AR 17.22 |
| main-board.md:41, :42 | microphones at X -11.0 and 11 | U5 X -10.8, U6 X +10.8, Y -4.8; ports X +-11.77 | AR 17.19 |
| main-board.md:58 (open point 4), :63, :64, :67 | notch maybe needed; (new 9, 10); mic slots source | closed; U11 and hole copper rule open; sources | TN K20; LP S-L4; AR 17.22 |
| cover-glass.md:3, :6 | seal not designed, no room | SEAL1 0.05 (Z 2.70 to 2.75) in a seat lowered 0.05; tape not chosen; window dia 0.4 at X -12.425, Y -2.95; LP1; glass 0.959 there | TN lines 163 to 176 and "Glass seal ring"; AR 17.21, 17.23; LP |
| cover-glass.md:41, :42 (new) | none | window row; seal row (old window dia 0.6 at X -13.25, Y -4.7 named as before 17.21) | AR 17.15 (replaced), 17.21; TN |
| cover-glass.md:43, :46, :58 to 61, :64 | open point numbers 4 to 6 | new open point 4 (seal, window); renumbered; sources | AR 17.21, 17.23 |
| band-flex-tails.md:1, :3 | thumb side; "NOT routable as drawn" | joystick side; both ribbons drawn and checked at US 9, 1.4 wide, in the liner; US 7 and 13 fail; B8 and S19 | AR 17.15, 17.24 K24, K25 |
| band-flex-tails.md:9 to 11 | FLEX1 with record switch SW2 and four switches; line counts open | five switches, SW2 centre; no record switch; 8 and 7 pads; pads in the liner | AR 17.11, 17.12, 17.14 |
| band-flex-tails.md:20 | stiffener not stated | plus 6.4 x 6.4 stiffener under the switch head, to follow | AR 17.24 K13 |
| band-flex-tails.md:35 to 44 | 4 switch groups plus record; pad dia 1.0 at X +-0.8, +-2.4, -150 deg; joystick 150; record switch 88; motor 7.0 x 2.1 at 51; cell -39 to +167 | 5 switches; pad 1.6 mm, pitch 2.4, at 158.2, 172.7, 187.3, 201.8 deg; -78; SW2; cross 2.4; motor 5.0 x 2.5 at -44; protection circuit 39.5; cell +48.711 to -98.981, 39.185 mm | AR 17.15, 17.24; TN "Cell at US 9" |
| band-flex-tails.md:46 | width 2.2, slot X -4.7 | width 1.4, slot X -2.2, 1.2 deep at US 9; fold room 2.6 x 2.2 x 1.03 | TN line 175, K21; AR 17.24 |
| band-flex-tails.md:52, :58, :59, :66 | length per size open; S16; line count; sources | per-size route to follow; S16 answered at US 9; 8 and 7 pads; sources | AR 17.14, 17.24 |

## Not done, said plainly
- Per-size numbers for the motor angle, the protection circuit start and the slot depth, and the 6.9 flange and stiffener thickness: not in any source; not written.
- Not touched, outside the five pages: body.md Files status, drawings, STEP and STL; the older STEP stubs of the flex tails; bom.csv.
- The US 5 and 6 columns of the body.md size table are kept, marked reference only (body.md:102).
- No git, no thin.py, no check_thin.py run. Line numbers were read from the files after the last edit; rows give the first line of a group of lines

RESULT: done, five spec pages brought to model v5 and 17.24; the bar grep ends with 8 hits, each a "before v5" or "does not exist" sentence, each explained above.
