# v6 refresh of cell, band liner, record cap and five earlier pages: changed places

Files in design/mfg/specs/. Sources: AR = design/architecture.md section (17.11 to 17.13, 17.16, 17.18, 17.22, 17.25, 17.26, 17.27); TN = design/mech/thin/thin-notes.md (sections "Model v6, continued", "Model v6.1", "Model v6.2"); FW = design/firmware.md F6 sections 8.1 and 8.5; AS = design/mfg/assembly/assembly.md. No number was invented. Line numbers are as the files stand now.

## Bar grep (v6-refresh-grep.log, exit 0)
Hits in my own notes (v5-refresh-notes.md) are former values and are not repeated here. The other hits, each a former value named as such or a negation:
- band-flex-tails.md:46 "2.6 x 0.6": "before v6.2 2.6 x 0.6".
- band-liner.md:64 "2.6 x 0.6": "before v6.2 2.6 x 0.6".
- body.md:3 "thumb side": the retired name, "the older name ... is retired". body.md:8 "150 degrees", "record cap": "Before v5 this page listed ..." and "no record cap". body.md:90 "2.6 x 0.6": "Earlier text of this line" (the lead's wording, kept).
- joystick-nub.md:6 "150 degrees": "Before v5: four switches in a cross at 2.1 mm at +150 degrees".
- cell.md:6 "28.4", "+167": "Before v5 this page gave 28.4 mm, an arc from -39 to +167 degrees".
- record-cap.md:1 and :3 "record cap": the title line is kept (links), and the text says the part does not exist.

## Changed lines
| file:line | old (short) | new (short) | source |
|---|---|---|---|
| cell.md whole file | 28.4 mm, -39 to +167, thumb side, 15 to 20 mAh, 154 degrees constant | rewritten: -Y joystick side; table per size US 7 to 13 (from, to, length, radius, volume, mAh, hours); section 1.6 x 6.0; 4.35 V; charge 15 mA = 0.85 C of 17.6 mAh; peak 228 mA (S12); protection start 43.8 / 41.5 / 39.5; cell 0.10 from the dam; 0.075 mm resin to the ribbon | AR 17.26 table, 17.25, 17.22 (228 mA at 3.30 V), 17.13, 17.18; TN "what the body spec and the cell spec must state per size"; FW 8.1 (4.35 V, 10 percent end, charge times), 8.5 |
| cell.md:6 | 28.4 mm at US 9, arc to +167 | 33.936 to 46.121; US 9 +48.713 to -98.986; sealed edge 2.0, tabs at +Y end; protection +39.5 to +47.6 at US 9 | TN lines 67 (v4 cell row, protection circuit) and 264 |
| cell.md:29 to 45 (table) | 28.4, 10.58, 154 deg, -39, 167, 15 and 20 mAh, 32 mA least charge | per-size rows; 17.6 and 31.9 mAh; 15 mA; 228 mA; dam 0.10; resin 0.075 | AR 17.26, 17.22; TN |
| cell.md Ring sizes | calculated 24.0 to 32.8 mm | measured table, 7 rows | AR 17.26 |
| cell.md open points 3, 4, 6 to 9 | 154 deg constant; second charger part; 15 to 20 mAh | angles from the model; charge 15 mA confirmed by Grepow; 17.6 to 31.9 mAh; new points 7 (peak discharge), 8 (cure temperature, K-A8), 9 (protection circuit place) | AR 17.22, 17.26; AS K-A8 |
| band-liner.md:3, :6 | cast over cell, flex tails, motor tail | adds ribbons embedded 0.075 each side, four pads set flush, fill under the stiffener 6.4 x 6.4 x 0.075, 0.1 mm strips beside the joystick pocket, seals before the cast | AR 17.12, 17.15, 17.26, 17.27; AS steps 8, 19, 21 |
| band-liner.md:15 | cell limit during cure; repair not possible | order of seals, dam, cast; K-A8 (cell live); K-A5 (ribbons inside one cast, S19) | AS steps 19 to 21, K-A5, K-A8 |
| band-liner.md:31, :34, :37 | none | pointer to the new section; pads flush, no resin in the pocket or through the slots; core ring per size | AS step 21 |
| band-liner.md:50 | slot seal and dam, "neither is designed" | slot seal with SEAL2 on US 7 to 9, dam DAM1; materials not chosen (S26) | AR 17.27, AS steps 19, 20 |
| band-liner.md:51 to 54 (new points 9 to 12) | none | K-A12 two-shot proposal; K-A5 and S19; fill of strips and under the stiffener; pad flush | AS K-A12, K-A5, step 21; AR 17.26 |
| band-liner.md:56 to 66 (new section) | none | table: ribbon 1.4 x 0.15 in 0.075 resin; pads dia 1.6, 0.07 thick, 158.23 to 201.77 deg; stiffener; strips; DAM1 0.15 / 0.05; slots 2.0 x 0.6; SEAL2 0.79 to 0.81 mm3, US 7 to 9 only; cell 0.10 from the dam | AS steps 8, 19, 20, 21; TN "Model v6, continued", "Model v6.2"; AR 17.27 |
| record-cap.md | whole page for CAP2 | title line kept; "This part does not exist ... Do not make this part."; long press 1.0 s on SW2 | AR 17.11; lead's text |
| body.md:3 | v5 header | v6.2 header; merged32g on US 7 and 8; joystick and motor per size | AR 17.25, 17.26 |
| body.md:74 | pocket r 9.775 to 10.955 | bore to a flat roof, roof radius 10.9026 at US 9; 0.1 strips | AR 17.26; TN "K12" lines and last-section table |
| body.md:71, :75 | joystick -78 | -78 US 9 to 13, -81.0 US 8, -84.0 US 7 | AR 17.25 |
| body.md:76 | flange 6.4, 6.9 "follows" | flange 6.9 x 6.4 as built; roof 0.05 above; 0.050 free space | AR 17.24 K12, 17.26; TN K12 line |
| body.md:77 | 1.11 toward the bottom | 1.1 (US 9), per size in the last section | TN per-size table |
| body.md:79 | pocket depth | adds "pocket floor 0.05 under the motor" | AR 17.27 |
| body.md:80, :81 | motor -44 per size to follow; metal 0.425 | -47.0, -45.5, -44.0, -45.0, -43.5, -42.5, -42.5; metal 0.425 / 0.450 / 0.475 | AR 17.25 to 17.27; TN "Per-size table, v6.2 values" |
| body.md:90 (second half only; the lead's first half kept) | slot depth 1.2 at US 9, per size to follow; channel ends at 30 deg | slot bottom Z -0.20, -0.20, -0.23, -0.63, -1.04, -1.45, -1.85; channel sentence removed | AR 17.26 |
| body.md:96, :102, :114 | per size to follow; US 9 only passes | values per size in the last section; passes at all 7 sizes in v6.2 | AR 17.26, 17.27 |
| body.md:124 on (new last section) | none | table per size: joystick, roof span +-19.693 to +-15.747, roof radius, motor angle, slot bottom, window, metal beside the opening | TN "What the body spec ... per size", v6.2 per-size and window tables |
| joystick-nub.md:6, :31, :49 | -78 deg only | -78 / -81.0 / -84.0 | AR 17.25 |
| joystick-nub.md:32 | pocket r 9.775 to 10.955 | bore to roof, r 10.9026 at US 9; straight entry; 0.1 strips | AR 17.26; TN |
| joystick-nub.md:33, :34 | flange "today" 6.4 and "to follow" 6.9 (two rows) | one row: flange 6.9 x 6.4, roof 0.05 above, held on four sides; second row removed | AR 17.24 K12, 17.26 |
| joystick-nub.md:37 | stiffener 6.4 x 6.4 "to follow" | 6.4 x 6.4 x 0.075 as built, class metal (stainless or polyimide, not chosen) | AR 17.26; TN K13 line |
| joystick-nub.md:61, :64 | flange play open | closed in v6; K-A12 named; sources 17.25, 17.26 | AS K-A12 |
| main-board.md:58 | joystick -78 | adds -81.0 on US 8, -84.0 on US 7 | AR 17.25 |
| band-flex-tails.md:3 | v5 US 9 only; US 7, 13 fail | v6.2 passes all 7 sizes | AR 17.26, 17.27 |
| band-flex-tails.md:11, :20 | motor -44; stiffener thickness follows | motor angle range; 0.075 stiffener | AR 17.26; TN |
| band-flex-tails.md:39, :42, :43, :44 | -78; motor -44 per size to follow; protection 39.5; cell 39.175 with a note on 39.185 | per size values; protection 43.8 / 41.5 / 39.5 and 0.075 resin; cell per size, angles in cell.md | AR 17.25, 17.26 |
| band-flex-tails.md:46 | width 1.4, slot 2.0 x 0.6 "X = -2.2", 1.2 deep, depth to follow | slot X -3.5 to -1.5 only (the lead's size kept; the old "X = -2.2" removed, it was the centre of the 2.6 slot); bottom Z per size; fold zone marked a v5 figure | AR 17.27, 17.26; TN v6.2 body spec |
| band-flex-tails.md:52 | route per size to follow | slot bottom per size given; flat pattern open | AR 17.26 |

## Per size items the model answered ("to follow" removed)
Flange 6.9 and stiffener 6.4 x 6.4 x 0.075 (body, joystick-nub, band-flex-tails); motor angle per size; protection circuit start per size; floor slot bottom per size; joystick angle per size. The cover glass and main-board pages needed no change against 17.25 to 17.27 (main-board.md:58 only).

## Not done, said plainly
- The fold room 2.6 x 2.2 x 1.03 is a model v5 figure: no v6 source measures it for the 2.0 slot; kept and labelled.
- body.md:77 "1.1" at US 9 against "1.11" in v5: the v6 table gives 1.1; both are the same scan.
- The joystick-nub.md and body.md STEP and drawing status lines are not changed.
- No git, no thin.py. No numbers outside the sources above were added.

## check_assembly.py
Run from the project root: `design/.venv/bin/python design/mfg/assembly/check_assembly.py`, before my edits exit 0 and after my edits exit 0, last lines "E1 PASS all 225 distinct path:line citations open", "RESULT PASS". No cited line of body.md, band-liner.md, joystick-nub.md, main-board.md, cover-glass.md or band-flex-tails.md moved: I kept every cited line in place (body.md:3, 5, 83, 90, 93, 117; band-liner.md:15, 28, 34, 37, 43, 45, 48, 50 checked after the edits) and put new rows and sections after them. Old and new line numbers: none moved. The meaning of a few cited lines changed only in wording (body.md:90 and band-liner.md:15, 50).

RESULT: done, cell.md rewritten to 17.26, band-liner.md corrected and extended, record-cap.md replaced, five other pages brought to 17.25 to 17.27; bar grep hits are all named former values, check_assembly.py exits 0.
