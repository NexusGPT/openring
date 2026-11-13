
## 4. check_board.py (note N7)

Header of `design/ecad/ring/pcb/check_board.py` documents it; code at lines 177 and 178: environment variable `CHECK_BOARD_OUT` (an existing folder) puts `<board name>-drc.json` there; unset or empty, the report is written beside the board as before. Proof on copies of the ring board in W (with its project file and a library table pointing to the design libraries): `logs/board/test-with_CHECK_BOARD_OUT.log` (exit 0, `RESULT: PASS`, report found in the output folder and none beside the board copy) and `logs/board/test-default_without_the_variable.log` (exit 0, report beside the board copy); the same two cases are in the runner (`SECTION check_board ok=2 of 2`). Earlier looks: a first run on a copy without the `.kicad_pro` project file failed on 1812 rules violations, an artefact of my copy (`logs/board/with-out-option.log`, report kept in `copies/board-out-run1-no-kicad_pro/`); the second run with the project file passed (`logs/board/with-out-option-run2.log`); a run without the variable (`logs/board/default-no-option.log`).

## 5. Honest files as they stand at the end (`final/`), every failing line classified

| check | result | failing lines | class |
|---|---|---|---|
| check_wiring.py --require-complete on `design/wiring/product-wiring.csv` | exit 1 (`final/check_wiring-live.log`) | 4 `field-newline` and 4 `rebuild` lines, all W054 to W057 `proof_carrier` (the 28 CRs) | real fault of the list (the generator is fixed, the list is not regenerated; owner: whoever regenerates it). Defect of my rule: 0. Before my change: `RESULT PASS` (`base/check_wiring.log`) |
| check_joints.py on `joints.csv` | exit 0, `RESULT PASS joints 99` (`final/check_joints-live.log`) | none | same result as before (reviewer: `RESULT PASS joints 99`) |
| check_assembly.py on `assembly.md` | exit 1 (`final/check_assembly-live.log`) | `A1 FAIL placement rows not in any step: side_slit_seal(SEAL3)` and `T1 FAIL 26 of 154` (26 `TOKEN` lines) | A1 is an old rule: placement.csv has a new row the guide does not name (real fault of the guide, not of my rules). The 26 T1 lines: the guide cites `design/mech/thin/placement.csv:N` and the file now has other rows there (its rows moved since the citations were written: most by 9 rows, see the last column); for each of the 26 the named designator or part name is the key cell of a row elsewhere in the same file (`final/where-are-the-rows.log`, last line `REJECTED 26, of which the named token is a row key elsewhere in the same file: 26`). Real faults of the guide, owner: guide-fix4. Defect of my rule: 0. At 17:54, before the rows were added, `T1 PASS` and `RESULT PASS` (`assembly/live-now.log`) |

The 26 citations (guide line: cited file:line, token, where its row is now):

- guide line 51: design/mech/thin/placement.csv:27 is not the row of GL1, cover_glass; the key cell holds GL1 at line(s) [36]
- guide line 52: design/mech/thin/placement.csv:26 is not the row of ADH1, clear_adhesive; the key cell holds ADH1 at line(s) [35]
- guide line 53: design/mech/thin/placement.csv:24 is not the row of DISP1, J1, screen_tail; the key cell holds DISP1 at line(s) [33, 34]
- guide line 53: design/mech/thin/placement.csv:25 is not the row of DISP1, J1, screen_tail; the key cell holds DISP1 at line(s) [33, 34]
- guide line 54: design/mech/thin/placement.csv:23 is not the row of ADH1, AN010, FOAM1; the key cell holds ADH1 at line(s) [35]
- guide line 55: design/mech/thin/placement.csv:22 is not the row of J1, PCB1, main_board; the key cell holds J1 at line(s) [18]
- guide line 61: design/mech/thin/placement.csv:28 is not the row of HSG1, outer_body; the key cell holds outer_body at line(s) [37]
- guide line 64: design/mech/thin/placement.csv:32 is not the row of CAP1, joystick_cap; the key cell holds CAP1 at line(s) [41]
- guide line 65: design/mech/thin/placement.csv:39 is not the row of DAM1, joystick_dam; the key cell holds DAM1 at line(s) [48]
- guide line 66: design/mech/thin/placement.csv:34 is not the row of SKTAAAE010, SW1, SW2, SW3; the key cell holds SW1 at line(s) [45]
- guide line 66: design/mech/thin/placement.csv:38 is not the row of SKTAAAE010, SW1, SW2, SW3; the key cell holds SW1 at line(s) [45]
- guide line 67: design/mech/thin/placement.csv:40 is not the row of M1, W0525AB001D, vibration_motor; the key cell holds M1 at line(s) [49]
- guide line 68: design/mech/thin/placement.csv:41 is not the row of BT1; the key cell holds BT1 at line(s) [50]
- guide line 69: design/mech/thin/placement.csv:42 is not the row of PRT1, cell_protection; the key cell holds cell_protection at line(s) [51]
- guide line 71: design/mech/thin/placement.csv:47 is not the row of FLEX1, band_flex_thumb; the key cell holds band_flex_thumb at line(s) [56]
- guide line 72: design/mech/thin/placement.csv:48 is not the row of FLEX2, band_flex_away; the key cell holds band_flex_away at line(s) [57]
- guide line 73: design/mech/thin/placement.csv:43 is not the row of CP1, CP2, CP3, CP4; the key cell holds CP1 at line(s) [52]
- guide line 73: design/mech/thin/placement.csv:46 is not the row of CP1, CP2, CP3, CP4; the key cell holds CP1 at line(s) [52]
- guide line 74: design/mech/thin/placement.csv:31 is not the row of EP30Med, LNR1, band_liner; the key cell holds band_liner at line(s) [40]
- guide line 75: design/mech/thin/placement.csv:29 is not the row of SEAL1, glass_seal; the key cell holds SEAL1 at line(s) [38]
- guide line 150: design/mech/thin/placement.csv:43 is not the row of CP1, CP2, CP3, CP4; the key cell holds CP1 at line(s) [52]
- guide line 218: design/mech/thin/placement.csv:25 is not the row of DISP1, J1, screen_tail; the key cell holds DISP1 at line(s) [33, 34]
- guide line 251: design/mech/thin/placement.csv:39 is not the row of DAM1, joystick_dam; the key cell holds DAM1 at line(s) [48]
- guide line 275: design/mech/thin/placement.csv:29 is not the row of ADH1, SEAL1, clear_adhesive, glass_seal; the key cell holds ADH1 at line(s) [35]
- guide line 277: design/mech/thin/placement.csv:29 is not the row of SEAL1; the key cell holds SEAL1 at line(s) [38]
- guide line 340: design/mech/thin/placement.csv:39 is not the row of DAM1; the key cell holds DAM1 at line(s) [48]
- REJECTED 26, of which the named token is a row key elsewhere in the same file: 26

## 6. What each check still cannot catch

- check_wiring: a wrong reading of a source that the generator and the check read the same way (board reader, copper path model); a wrong `state_reason` or `waits_for` text is only caught if the generator would build another one; the pairing of pads by the generator ("nearest") is not judged; copper lengths are compared with the generator's own path model.
- check_joints: a check that names a method and a pass word but not the right measurement (it cannot know that "beeps" is the right test for that joint); "continuity" and "reads" are weak forms; a heat value with a unit and a tool word is accepted whatever the value (it is not compared with process.md); a `file:N` pass citation is accepted when line N holds any pass form, not the right one.
- check_assembly: T1 reads `.csv` citations and 3 prose files only: citations of other prose files (architecture.md, thin-notes.md, datasheets) are not read, because 208 of 361 of them name a token that is not on the cited line and 35 still do after a shared-word test, mostly right citations of tables of numbers (`assembly/exp-md-too.log`, `assembly/exp-md-union.log`, experiment copy `assembly/check_assembly-exp.py`); a citation to a wrong row when the sentence names no part, names the part by words only, or sits in a long list that also names the wrong row's part (4 of the 45, above); P1 and L1 read only the forms listed (tab, motor, disc lands, the ribbon land paste); other facts of the guide are not compared with the tables, and a rewording of those sentences fails the check until the form is restored or the rule changed.

## 7. Bar items

- "No existing rule loosened or removed": no existing rule text was edited in the three checks; the additions are new rules (R6, R7 in check_joints, T1, P1, L1, X0 in check_assembly, six `states-*`, `field-newline` and `rebuild` in check_wiring). In check_assembly the only change to existing code is the argument parsing (`--joints`, `--wiring`).
- Each new rule has its own broken copy kept in W with the rejecting line (tables below); the runner is `run_all_tests.py`.
- A change that turns a green check of the base red: none was rejected; the existing joint-table tests (18) and the base results are as before.

## questions_for_owner

1. Is "continuity" a named reading that passes R6 on its own? I accepted it so that the existing mini test of `joint-table-work/tests/run_tests.py` ("fake continuity [needs case 8]") passes unchanged; the strict reading ("a number or a named reading such as beeps") would reject a check that only says "continuity".
2. Should the tool of a heat (R7) be read from the row's tool field too? I allowed it so the existing mini heat "fake 300 C 2 s" passes; strict reading: the heat text itself names the tool.
3. T1 does not read most prose citations (see section 6). Should the guide cite prose lines with a quote (like the wiring list does, `file:line|quote`) so that a check can compare them?
