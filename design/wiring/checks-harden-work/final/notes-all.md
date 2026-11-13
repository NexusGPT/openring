# Hardening of three wiring checks (review 4, instrument faults I1, I2, I3, notes N2 and N7)

Builder: checks-harden. Work folder W = `design/wiring/checks-harden-work/` (scripts, broken copies in `copies/`, logs in `logs/`, final runs in `final/`). Clock: started 17:31 (`date`), tests last run 18:04. Files changed (all in Owns): `design/wiring/check_wiring.py`, `design/wiring/build_wiring.py` (the CR fix only), `design/mfg/assembly/check_joints.py`, `design/mfg/assembly/check_assembly.py`, `design/ecad/ring/pcb/check_board.py` (output folder option only). I ran no git, no browser, no web request, no generator that writes a delivered file (the generator ran only with `WIRING_OUT` in W and `WIRING_NO_DRC=1`), no `check_band.py` (search of my scripts and logs: `final/search-check_band.log`). `joints.csv`, `assembly.md`, `product-wiring.csv` and the review folder were only read.

## Result in one block

- Test runner `run_all_tests.py` in W, last line of `logs/run_all_tests-final.log`: `TESTS PASS 142 of 142 as expected` (check_wiring 52 of 52, check_joints 35 of 35, check_assembly 35 of 35, check_board option 2 of 2, existing joint-table tests 18 of 18; the existing tests passed unchanged, `joint-table-work/tests/expect.txt` was not edited).
- Reviewer's faulty copies, before (reviewer's logs) and after (my runs, same entry points): check_wiring `RESULT fakes=17 differs=5` before; now all 5 faulty copies fail, each on a line naming its fault, and the 10 other fake files I re-ran still fail. check_joints `differs=2` before; both fail now. check_assembly `differs=3` before; all 3 fail now on isolated copies. Details per check below.
- Honest files as they stand at the end (final/): check_wiring FAIL on 4 lines of the list (28 carriage returns in W054 to W057, the generator is fixed, the list is not regenerated: a real fault of the list), check_joints PASS 99, check_assembly FAIL on 1 old rule (A1, a placement row in no step) and 26 citations of the new rule T1 (placement.csv rows moved: real faults of the guide). Defects of my rules: 0 (each classified below).
- Two judgement calls that the owner or lead should confirm are listed at the end (`questions_for_owner`).

## 1. check_wiring.py (fault I1) and generator note N2

Rules added (`check_wiring.py` lines 141 to 380; header lists them):

| rule | what it compares | read independently of the generator? | second way (rebuild) |
|---|---|---|---|
| field-newline | any field with a CR or a newline, a short row, an extra field | yes (the csv as read with `newline=""`) | n/a |
| states-net | `signal_A`, `signal_B` of each end against the net of that pin in the netlist (file read here) and against the pad net on every board of the end (ring board, 7 flex1 or 7 flex2 boards, case boards, through pcbnew); `carrier_net` against the end nets | yes: netlist rows by their own loop, pad nets by pcbnew `pad_of` (generator function, same pcbnew read) | yes |
| states-face | the faces stated at an end against the pad layers in the board file; for a J_BAND land the main board face and the tail land face on the flex at all 7 sizes | yes (pcbnew layers) | yes |
| states-tail | the join text "tail land N" of the flex named: the flex is the line's carrier, the land is the line's own J_BAND pin, and that land has the line's net on the flex board at all 7 sizes | yes (pcbnew) | yes |
| states-colour | motor lead colour against the land table of band-interface.md (own regex), case wire colours against lead-decisions.md, cell lead colours against board-notes.md; the marking and the carrier text must both carry it | yes (own regexes on the source files) | yes |
| states-cut | cut length at each of the 7 sizes against the `lead cut length` row (header order 7 to 13 checked), the case wiring table, the thermistor 10 mm | yes (own regexes) | yes |
| states-copper | copper length per size within 0.001 mm of the shortest path of that size's board | shares the generator's `copper_graph` and `dijkstra`: a wrong path model is in both | yes |
| rebuild | every column of every line against the line `build_wiring.py` builds today (its `main()` run in memory, its output file captured, nothing written) | no: shares the generator's readers (`board`, `pad_of`, `find_line`) | n/a |

What the second way cannot catch: a wrong reading of a source that the generator and the check share (the board reader, the Dijkstra model, `find_line` patterns); a source that was changed and a list that was rebuilt from it (the rebuild agrees with the source by construction, only the independent rules compare with the source text). What the independent rules cannot catch: a field they do not read (`state_reason`, `waits_for`, `join_B` and the other join texts); those are only compared by the rebuild.

N2 (carriage returns): the 28 bare CRs came from the source `design/wiring/ring-case-contact.csv`, which has CRLF line ends, quoted per line by `contact_lines()`. Fix in `build_wiring.py` line 974: `.rstrip("\r")`. Proof on a copy: `WIRING_NO_DRC=1 WIRING_OUT=<W>/copies/rebuilt-fixed.csv` ran the generator; `cr-proof.log`: live list `CR 28`, rebuilt copy `CR 0`, and the two lists differ in exactly 4 fields (`W054 W055 W056 W057 proof_carrier`). The generator was not run on the real list (another helper's edits). `check_wiring.py` now fails a CR or newline in a field (case cr_in_field, newline_in_field below) and, as the list is not regenerated, fails the live list today (honest files below).

Reviewer's faults: result before and after.

| reviewer's copy | before (`review4-work/fakes-check_wiring.log`) | after, reviewer's own file (`logs/cw/rev_*.log`) | after, isolated copy (table below) |
|---|---|---|---|
| W001 JOY_DOWN at both ends | passed (exit 0) | exit 1, `FAIL[states-net] W001 end A J_BAND_A.1 states net 'JOY_DOWN', the ring netlist says 'JOY_UP'` | wrong_net_both |
| W001 joined to FLEX1 tail land 2 | passed | exit 1, `FAIL[states-tail] W001 join text says FLEX1 tail land 2 but end A is ring main board J_BAND_A.1` | wrong_tail_land |
| W040 and W029 on the wrong face | passed | exit 1, one `FAIL[states-face]` line each for W040 and W029 | wrong_face_W040, wrong_face_W029 |
| motor lead colours swapped | passed | exit 1, `FAIL[states-colour] W023 source says red, the line says marking 'blue insulation'` | motor_colour_swap |
| cut length 9.99 | passed | exit 1, `FAIL[states-cut] W023 cut length at US 9 is '9.99', the source table says '1.08'` | cut_wrong_value_9.99 |
| the other fakes (10 re-run as files: empty, flood, oneline, nomark, nocut, swapB, springswap, wireswap, prooffake, dropped; the missing-file fake `crash_missing` was not re-run) | failed | all 10 still exit 1 (`logs/cw/rev_*.log`) | same names |

The reviewer's own files were made from the list with the 28 CRs, so they also fail on field-newline; the isolated copies are made from the corrected list (`copies/rebuilt-fixed.csv`), so each fails only for its own fault. Control `honest_fixed_copy`: exit 0.

## 2. check_joints.py (fault I2)

Rules added (data tables at `check_joints.py` lines 45 to 62, functions `weak_check` line 87 and `weak_heat` line 106; header documents them):

| rule | a row fails when | accepted forms (the data) |
|---|---|---|
| R6 weak-check | its check field has no METHOD form or no PASS form | METHOD: an instrument (ohmmeter, meter, continuity, probe, needle tips, diode mode, feeler, gauge, thermocouple, bench supply, jig, X-ray), a way of looking (inspection, optical, magnifier, microscope, by eye, "N times"), a named test or reading (T-xxx, FACTORY ENTER, GET_INFO, USB through, beep, reads, voltage, measured, height, lights). PASS: a number with a unit (mm V A mA ohm kohm k Mohm C C/s N s ms MB MHz %, a magnification "20 times" is not one), a named reading (beeps, no beep, reads open, reads the cell voltage, a diode drop, enumerates, answers, vibrates, 0 violations, continuity, positive, breathing, blink), a named visual condition (flat, no bridge, not tilted, no tilt, not skewed, touch nothing else, none of its tails lifted, in place, centred), "accept rules of step N" where step N of assembly.md exists and names its accept rules, or `file:N` whose line N exists and itself holds a pass form |
| R7 weak-heat | its heat field is not a HEAT form | a value with a unit (C, degrees C, s, seconds, N) together with a tool or process word (iron, tip, hot bar, blade, thermode, hot plate, reflow, oven, profile, pressed contact, hand solder) in the heat text or in the row's own tool field; or a profile Pn with `process.md Pn` and the section `## Pn.` existing in process.md; or `none` or `no heat` followed by `:` and a reason of 6 or more characters |

Dry run on the real table first, without failing (`--list-weak`, exit 0): table of 17:40 (`copies/joints-snapshot-1.csv`): 1 row would be rejected, `final/check_joints-list-weak-snapshot1-final-rules.log`:
`WEAK R6 J-W027-A | names no pass value or pass condition | land B3, FACTORY ENTER and T-CHARGE pass at the end of the step; an open NTC land reads as cold and T-CHARGE fails with the charger off (hotbar-joint.md section 4)`. The same dry run with the first version of my rules (`joints/dry-run-list-weak.log`, `joints/dry-run-list-weak-2.log`) gave the same 1 row. For the owner of `joints.csv` (guide-fix4): R6 rejected J-W027-A (a named firmware test without its pass value or a citation of it). It has since amended that check ("as step 14 Check (c) says (design/mfg/assembly/assembly.md:205)"): table of 17:45 (`copies/joints-snapshot-2.csv`) and the live table at the end: `WEAK 0 lines in 99 rows` (`final/check_joints-list-weak-snapshot2.log`, `final/check_joints-list-weak-live.log`); `final/joints-W027-before-after.log` shows the two texts. R7 rejected no real row (no R7 line in the dry runs above).

Bar for the existing tests: the mini table of `tests/run_tests.py` has a check "fake continuity [needs case 8]" and a heat "fake 300 C 2 s" with tool "fake iron". Two accommodations so that those tests pass unchanged: "continuity" counts as a named reading (a continuity test passes or fails), and the tool word of a heat may come from the row's tool field; an EMPTY tool field is left to R2 (otherwise the existing `field_emptied` copies would show an R7 line besides R2). See the questions at the end.

Reviewer's faults: result before and after.

| reviewer's copy | before (`fakes-check_joints.log`) | after |
|---|---|---|
| J-W026-A check = "ok" | passed (`RESULT PASS`) | exit 1, `R6 weak-check: J-W026-A check names no method (what is measured or looked at): 'ok'` (`logs/cj/rev_check_ok.log`, and the reviewer's file `rev_checkok_file`) |
| J-W061-B heat = "hot" | passed | exit 1, `R7 weak-heat: J-W061-B heat names no value with a unit (C, s, N) ...: 'hot'` (`logs/cj/rev_heat_hot.log`, `rev_heatok_file`) |
| the other fakes (8 re-run as files) | failed | the reviewer's files `rev_checkempty rev_dropped rev_empty rev_flood rev_gap rev_stepbad rev_brokenpaste rev_nofile` still exit 1 |

## 3. check_assembly.py (fault I3)

Rules added (`check_assembly.py` lines 263 to 526; header items (l), (m), (n)); the script takes `--joints FILE` and `--wiring FILE` besides the guide path:

| rule | what it compares | data |
|---|---|---|
| T1 (c) citation holds what its sentence names | for a `file:N` citation: the designators, part names, nets and part models of its item of the sentence (or of its table row) against line N of the cited file | `.csv` tables (not line 1): designators and part names must be in the row's key cells (columns ref, reference, part, item, net, name, *_ref), nets and models anywhere on the row; groups "a, b" and ranges "a to b" share the text before them; the end line of a range is read against the group; finding ids (F6, K15, W12) are no designators. Prose files: only band-interface.md, process.md, hotbar-joint.md (a token or a shared content word of the item). `TOKEN_FORMS`, `PROSE_FILES` |
| P1 (a) paste on the ribbon lands | from joints.csv: the J_BAND land rows (15), their group sizes (J_BAND_A 8, J_BAND_B 7), "paste printed ... in pass P of step S"; the guide step S must say the lands get paste, name PASS P and the two group sizes, and the Join of the hot bar step must say "on the solder layer that step S put on the N lands" (N the total) | read from joints.csv |
| L1 (b) which land gets which tab, lead, disc | from product-wiring.csv: tab P+/NTC/P- to land and net; the lands order; motor lands (+ red, joined to tail land 7; - to 6); disc lands (VBUS 4, D- 5, D+ 6, GND 7); the same facts in the orientation text of joints.csv; guide steps 7, 8 and 9 must say the same, in the forms the check reads (an unreadable form fails) | read from the two tables |

Reviewer's faults: result before and after.

| reviewer's copy | before (`fakes-check_assembly.log`) | after (isolated copies made from the live guide, same text change; table below) |
|---|---|---|
| G1 reintroduced (no paste on ribbon lands, step 14 on bare lands) | passed | `G1_reintroduced_both_steps`: `P1 FAIL step 2 says the ribbon lands get no paste, joints.csv says they get paste`; each half alone also fails (`G1_step2_only_no_paste`, `G1_step14_only_bare_lands`) |
| three cell tabs on swapped lands | passed | `cell_tabs_swapped`: `L1 FAIL step 9 puts tab P+ on land 2 (GND), product-wiring.csv has land 1 (VBAT) ...` |
| citation to a line that holds other text | passed | `citation_prose_wrong_line` (band-interface.md:123 to :3): `TOKEN line 141: ... band-interface.md:3 holds none of GND`; also `citation_bom_other_row`, `citation_placement_final_other_row`, `citation_netlist_other_row` |
| the 5 other fakes | failed | all still exit 1 (`rev_nocheck rev_noresult rev_flood rev_empty rev_cite2`, and the isolated `step_without_check_field`, `no_result_line`, `steps_twice`, `empty_file`, `citation_past_end`) |

The reviewer's own three files (`rev_g1`, `rev_tabs`, `rev_cite`) were made from the guide of review 4; they now fail on many lines of the live repository (45 stale bom citations and the rows added to placement.csv), so they do not show the new rules alone: the isolated copies do.

The 45 wrong `design/bom.csv:N` citations of fault H5 (reviewer's list `review4-work/bom-cites-judged.csv`) against the guide of review 4 (`review4-work/fakes-ca/honest.md`, the reviewer's honest copy): `assembly/bom-cites-45-list.log` ends `wrong citations 45, rejected by T1 41, not rejected 4`; none of the 5 right citations is rejected (`assembly/compare-bom-cites.log`: `right but rejected (false alarms): []`). The 4 it does not reject: `96 bom.csv:67`, `96 bom.csv:69` (a range inside a long list in which the wrong row's own designator C71 is also named), `162 bom.csv:48` (the sentence "The protection limits are known from the cell maker" names no part), `402 bom.csv:55` (the table row names the dam by words only). The live guide no longer cites those 45 (guide-fix4 corrected them): at the end `T1` finds 26 other citations wrong (below).

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

## Broken copies, one by one

check_wiring.py broken copies (made by make_wiring_fakes.py from the corrected list copies/rebuilt-fixed.csv), final run logs/all-check_wiring.log, one log per copy in logs/cw/

| broken copy (file in W) | result | rejecting line (first, cut at 150 characters) |
|---|---|---|
| honest_fixed_copy (copies/cw/honest_fixed_copy.csv) | as expected |  |
| empty (copies/cw/empty.csv) | as expected | FAIL[terminal-missing] case BT1 pin 1 (net 'BAT') is in no line |
| flood_duplicates (copies/cw/flood_duplicates.csv) | as expected | FAIL[terminal-twice] case BT1 pin 1 is in 4 lines: W059 W059x0 W059x1 W059x2 |
| one_line_covers_all (copies/cw/one_line_covers_all.csv) | as expected | FAIL[terminal-unknown] W001 end B SW1 SW2 SW3 SW4 SW5 J_BAND_A J_BAND_B J1 CP1 CP2 CP3 CP4 P1 P2 P3 P4.3 has no netlist row in its proof |
| no_marking_lead (copies/cw/no_marking_lead.csv) | as expected | FAIL[state-kind] W023 is `specified and landed` but carrier 'lead' has marking '', gauge or model 'AWG32 (Jinlong W0525AB001D lead)', cuts ['1.12', '1 |
| no_cut_lead (copies/cw/no_cut_lead.csv) | as expected | FAIL[lead-length] W023 lead has cut lengths ['1.12', '1.07', '', '1.14', '1.39', '1.44', '1.39'] and no 'not size dependent' |
| wrong_net_both (copies/cw/wrong_net_both.csv) | as expected | FAIL[states-net] W001 end A J_BAND_A.1 states net 'JOY_DOWN', the ring netlist says 'JOY_UP' |
| swap_B_ends (copies/cw/swap_B_ends.csv) | as expected | FAIL[terminal-unknown] W001 end B SW3.3 has no netlist row in its proof |
| wrong_tail_land (copies/cw/wrong_tail_land.csv) | as expected | FAIL[states-tail] W001 join text says FLEX1 tail land 2 but end A is ring main board J_BAND_A.1 |
| wrong_face_W040 (copies/cw/wrong_face_W040.csv) | as expected | FAIL[states-face] W040 end B J1.1 face states 'F.Cu', the board file has ['B.Cu'] |
| wrong_face_W029 (copies/cw/wrong_face_W029.csv) | as expected | FAIL[states-face] W029 end B CP1.1 face states 'F.Cu', the board file has ['B.Cu'] |
| spring_pin_swap (copies/cw/spring_pin_swap.csv) | as expected | FAIL[terminal-unknown] W054 end B P4.1 has no netlist row in its proof |
| case_wire_swap (copies/cw/case_wire_swap.csv) | as expected | FAIL[terminal-unknown] W063 end B W4.1 has no netlist row in its proof |
| motor_colour_swap (copies/cw/motor_colour_swap.csv) | as expected | FAIL[states-colour] W023 source says red, the line says marking 'blue insulation', carrier 'red lead wire AWG32 of the motor' |
| cut_wrong_value_9.99 (copies/cw/cut_wrong_value_9.99.csv) | as expected | FAIL[states-cut] W023 cut length at US 9 is '9.99', the source table says '1.08' |
| proof_text_fake (copies/cw/proof_text_fake.csv) | as expected | FAIL[proof-text] W023 proof_carrier: design/ecad/band/band-interface.md line 123 does not hold 'this sentence is not in the file' |
| row_dropped (copies/cw/row_dropped.csv) | as expected | FAIL[terminal-missing] ring CP2 pin 1 (net 'USB_DN') is in no line |
| net_in_netlist_only (copies/cw/net_in_netlist_only.csv) | as expected | FAIL[states-net] W040 end B J1.1 states net 'ELVDD', the ring netlist says 'ELVSS' |
| end_A_main_face_wrong (copies/cw/end_A_main_face_wrong.csv) | as expected | FAIL[states-face] W001 end A J_BAND_A.1 face states 'B.Cu', the board file has ['F.Cu'] |
| end_A_tail_face_wrong (copies/cw/end_A_tail_face_wrong.csv) | as expected | FAIL[states-face] W001 end A tail land face states 'B.Cu', the flex boards have ['F.Cu'] |
| tail_land_wrong_flex (copies/cw/tail_land_wrong_flex.csv) | as expected | FAIL[states-tail] W001 join text says FLEX2 tail land 1 but end A is ring main board J_BAND_A.1 |
| cut_one_size (copies/cw/cut_one_size.csv) | as expected | FAIL[states-cut] W023 cut length at US 13 is '1.40', the source table says '1.39' |
| cut_case_wire (copies/cw/cut_case_wire.csv) | as expected | FAIL[states-cut] W063 cut length at US 7 is '15.7', the source table says '15.6' |
| cut_thermistor (copies/cw/cut_thermistor.csv) | as expected | FAIL[states-cut] W061 cut length at US 10 is '12', the source table says '10' |
| case_wire_colour (copies/cw/case_wire_colour.csv) | as expected | FAIL[states-colour] W064 source says white, the line says marking 'green insulation', carrier 'wire 30 AWG stranded, white, cut 16.3 mm (path 11.' |
| cell_lead_colour (copies/cw/cell_lead_colour.csv) | as expected | FAIL[states-colour] W059 cell lead 1 marking 'black (-)', the source gives colour 'red' |
| copper_length_changed (copies/cw/copper_length_changed.csv) | as expected | FAIL[states-copper] W001 copper length at US 9 is '11.000', the board gives 11.584 |
| carrier_net_differs (copies/cw/carrier_net_differs.csv) | as expected | FAIL[states-net] W001 carrier net 'JOY_UP2' does not follow its end nets 'JOY_UP' and 'JOY_UP' |
| cr_in_field (copies/cw/cr_in_field.csv) | as expected | FAIL[field-newline] W001 field state_reason holds 1 carriage return and 0 newline characters (first at offset 9) |
| newline_in_field (copies/cw/newline_in_field.csv) | as expected | FAIL[field-newline] W001 field state_reason holds 0 carriage return and 1 newline characters (first at offset 9) |
| rebuild_state_reason (copies/cw/rebuild_state_reason.csv) | as expected | FAIL[rebuild] W001 field state_reason: list says 'all fine, trust me', the generator builds 'both ends in all 7 flex1 board files with net JOY_UP, cop |
| rebuild_join_B (copies/cw/rebuild_join_B.csv) | as expected | FAIL[rebuild] W001 field join_B: list says 'hand solder', the generator builds 'reflow' |
| rebuild_cut_note (copies/cw/rebuild_cut_note.csv) | as expected | FAIL[rebuild] W040 field cut_note: list says 'size dependent', the generator builds 'not size dependent' |
| rebuild_pad_pin_text (copies/cw/rebuild_pad_pin_text.csv) | as expected | FAIL[rebuild] W001 field end_B_pin: list says '4', the generator builds '3' |

check_joints.py broken copies (make_joints_fakes.py), final run logs/all-check_joints.log, one log per copy in logs/cj/

| broken copy (file in W) | result | rejecting line (first, cut at 150 characters) |
|---|---|---|
| real_snapshot_as_it_stands (copies/cj/real_snapshot_as_it_stands.csv) | as expected | R6 weak-check: J-W027-A check names no pass value or pass condition: 'land B3, FACTORY ENTER and T-CHARGE pass at the end of the step; an open NTC lan |
| real_with_W027_check_amended (copies/cj/real_with_W027_check_amended.csv) | as expected |  |
| check_ok (copies/cj/check_ok.csv) | as expected | R6 weak-check: J-W054-A check names no method (what is measured or looked at): 'ok' |
| check_looks_fine (copies/cj/check_looks_fine.csv) | as expected | R6 weak-check: J-W054-A check names no method (what is measured or looked at): 'looks fine, checked by the builder' |
| check_measure_without_pass (copies/cj/check_measure_without_pass.csv) | as expected | R6 weak-check: J-W054-A check names no pass value or pass condition: 'ohmmeter at the foot, optical inspection at 20 times' |
| check_pass_without_method (copies/cj/check_pass_without_method.csv) | as expected | R6 weak-check: J-W054-A check names no method (what is measured or looked at): 'the result is good enough and less than 5 is fine' |
| check_accept_rule_of_missing_step (copies/cj/check_accept_rule_of_missing_step.csv) | as expected | R6 weak-check: J-W054-A check names no pass value or pass condition: 'optical inspection; each joint passes the accept rules of step 99' |
| check_file_line_past_end (copies/cj/check_file_line_past_end.csv) | as expected | R6 weak-check: J-W054-A check names no pass value or pass condition: 'optical inspection; accept rule design/mfg/assembly/process.md:99999' |
| check_file_line_real_accepted (copies/cj/check_file_line_real_accepted.csv) | as expected |  |
| check_file_line_holds_no_pass_value (copies/cj/check_file_line_holds_no_pass_value.csv) | as expected | R6 weak-check: J-W054-A check names no pass value or pass condition: 'optical inspection; accept rule design/mfg/assembly/process.md:100' |
| check_file_line_other_text (copies/cj/check_file_line_other_text.csv) | as expected | R6 weak-check: J-W054-A check names no pass value or pass condition: 'optical inspection; accept rule design/mfg/assembly/process.md:1' |
| check_accept_rule_step_real_accepted (copies/cj/check_accept_rule_step_real_accepted.csv) | as expected |  |
| check_number_unit_accepted (copies/cj/check_number_unit_accepted.csv) | as expected |  |
| heat_hot (copies/cj/heat_hot.csv) | as expected | R7 weak-heat: J-W054-A heat names no value with a unit (C, s, N) and no profile with its file, and is not none with a reason: 'hot' |
| heat_warm_no_value (copies/cj/heat_warm_no_value.csv) | as expected | R7 weak-heat: J-W054-A heat names no value with a unit (C, s, N) and no profile with its file, and is not none with a reason: 'warm enough to melt the |
| heat_value_without_unit (copies/cj/heat_value_without_unit.csv) | as expected | R7 weak-heat: J-W054-A heat names no value with a unit (C, s, N) and no profile with its file, and is not none with a reason: 'iron 340' |
| heat_none_without_reason (copies/cj/heat_none_without_reason.csv) | as expected | R7 weak-heat: J-W054-A heat says none or no heat without a reason after a colon: 'none' |
| heat_profile_without_file (copies/cj/heat_profile_without_file.csv) | as expected | R7 weak-heat: J-W054-A heat names no value with a unit (C, s, N) and no profile with its file, and is not none with a reason: 'P3 profile' |
| heat_profile_missing_section (copies/cj/heat_profile_missing_section.csv) | as expected | R7 weak-heat: J-W054-A heat names no value with a unit (C, s, N) and no profile with its file, and is not none with a reason: 'P9 profile (process.md  |
| heat_value_no_tool_anywhere (copies/cj/heat_value_no_tool_anywhere.csv) | as expected | R7 weak-heat: J-W054-A heat names a value but no tool or process (neither here nor in the tool field): '340 C, 7 s' |
| heat_value_tool_in_tool_field_accepted (copies/cj/heat_value_tool_in_tool_field_accepted.csv) | as expected |  |
| heat_profile_with_file_accepted (copies/cj/heat_profile_with_file_accepted.csv) | as expected |  |
| heat_none_with_reason_accepted (copies/cj/heat_none_with_reason_accepted.csv) | as expected |  |
| rev_check_ok (copies/cj/rev_check_ok.csv) | as expected | R6 weak-check: J-W026-A check names no method (what is measured or looked at): 'ok' |
| rev_heat_hot (copies/cj/rev_heat_hot.csv) | as expected | R7 weak-heat: J-W061-B heat names no value with a unit (C, s, N) and no profile with its file, and is not none with a reason: 'hot' |

check_assembly.py broken copies (make_assembly_fakes.py, from a snapshot of the guide taken at the start of the run), final run logs/all-check_assembly.log, one log per copy in logs/ca/

| broken copy (file in W) | result | rejecting line (first, cut at 150 characters) |
|---|---|---|
| honest_snapshot (copies/ca/honest_snapshot.md) | as expected | no new line against itself |
| G1_reintroduced_both_steps (copies/ca/G1_reintroduced_both_steps.md) | as expected | P1 FAIL step 2 says the ribbon lands get no paste, joints.csv says they get paste: - **The 15 ribbon lands:** J_BAND_A (8 lands) and J_BAND_B (7 lands |
| G1_step2_only_no_paste (copies/ca/G1_step2_only_no_paste.md) | as expected | P1 FAIL step 2 says the ribbon lands get no paste, joints.csv says they get paste: - **The 15 ribbon lands:** J_BAND_A (8 lands) and J_BAND_B (7 lands |
| G1_step14_only_bare_lands (copies/ca/G1_step14_only_bare_lands.md) | as expected | P1 FAIL step 14 Join does not say 'on the solder layer that step 2 put on the 15 lands' |
| ribbon_land_count_wrong_step2 (copies/ca/ribbon_land_count_wrong_step2.md) | as expected | P1 FAIL step 2 gives J_BAND_A as 7, joints.csv has 8 lands; step 2 gives J_BAND_B as 8, joints.csv has 7 lands |
| ribbon_land_total_wrong_step14 (copies/ca/ribbon_land_total_wrong_step14.md) | as expected | P1 FAIL step 14 says step 2 put solder on 14 lands, joints.csv says step 2 and 15 lands |
| ribbon_paste_pass_wrong (copies/ca/ribbon_paste_pass_wrong.md) | as expected | P1 FAIL step 2 does not say PASS 2 for the ribbon lands |
| cell_tabs_swapped (copies/ca/cell_tabs_swapped.md) | as expected | L1 FAIL step 9 puts tab P+ on land 2 (GND), product-wiring.csv has land 1 (VBAT); step 9 puts tab P- on land 1 (VBAT), product-wiring.csv has land 2 ( |
| cell_tabs_NTC_and_Pminus_swapped (copies/ca/cell_tabs_NTC_and_Pminus_swapped.md) | as expected | L1 FAIL step 9 puts tab NTC on land 2 (GND), product-wiring.csv has land 3 (NTC); step 9 puts tab P- on land 3 (NTC), product-wiring.csv has land 2 (G |
| cell_tab_order_wrong (copies/ca/cell_tab_order_wrong.md) | as expected | L1 FAIL step 9 says the tabs in the order P+, NTC, P- lie on lands 1, 2, 3; product-wiring.csv gives lands 1, 3, 2 |
| motor_lead_land_swapped (copies/ca/motor_lead_land_swapped.md) | as expected | L1 FAIL step 7 does not say 'land 1, net VMOT, joined to land 7' (product-wiring.csv) |
| motor_check_lands_swapped (copies/ca/motor_check_lands_swapped.md) | as expected | L1 FAIL step 7 check does not name tail land 7 as (VMOT) (product-wiring.csv); step 7 check does not name tail land 6 as (GND) (product-wiring.csv) |
| motor_red_lead_on_minus (copies/ca/motor_red_lead_on_minus.md) | as expected | L1 FAIL step 7 puts the blue lead on the + land, product-wiring.csv says red |
| disc_lands_swapped (copies/ca/disc_lands_swapped.md) | as expected | L1 FAIL the disc step puts VBUS on land 5, product-wiring.csv has land 4; the disc step puts USB_DN on land 4, product-wiring.csv has land 5 |
| joints_table_tab_land_differs_from_wiring (copies/ca/joints_table_tab_land_differs_from_wiring.md) | as expected | L1 FAIL joints.csv J-W025-B says tab P+ on land 2 (GND), product-wiring.csv has land 1 (VBAT) |
| joints_table_says_no_paste_for_a_ribbon_land (copies/ca/joints_table_says_no_paste_for_a_ribbon_land.md) | as expected | P1 FAIL 1 of 15 J_BAND rows of joints.csv name no paste printed in a pass of a step |
| wiring_list_tab_land_differs_from_guide (copies/ca/wiring_list_tab_land_differs_from_guide.md) | as expected | L1 FAIL joints.csv J-W025-B says tab P+ on land 1 (VBAT), product-wiring.csv has land 2 (VBAT); joints.csv J-W033-B says tab P+ on land 1 (VBAT), prod |
| citation_prose_wrong_line (copies/ca/citation_prose_wrong_line.md) | as expected | TOKEN line 141: design/ecad/band/band-interface.md:3 holds none of GND (it holds: Written 2026-11-13 by the W4 builder. Project root: /Users/a) |
| citation_bom_other_row (copies/ca/citation_bom_other_row.md) | as expected | TOKEN line 159: design/bom.csv:48 holds none of BT1, PRT1, RT1, cell_protection (it holds: Capacitor 10 uF 0402 6.3 V,C83,1,U11 input (C84 at the outp |
| citation_placement_final_other_row (copies/ca/citation_placement_final_other_row.md) | as expected | TOKEN line 21: design/ecad/ring/pcb/placement-final.csv:78 holds none of J1 (it holds: C29,OpenRing:Chip_0402,F,-0.200,-2.850,270,Z12,99.800,97.150) |
| citation_netlist_other_row (copies/ca/citation_netlist_other_row.md) | as expected | TOKEN line 222: design/ecad/ring/netlist.csv:381 holds none of DISP1, ELVDD, ELVSS, J1, VDD_3V0 (it holds: XC2,X1,3,X2,passive) |
| citation_past_end (copies/ca/citation_past_end.md) | as expected | E1 FAIL citations that do not open: design/ecad/band/band-interface.md:9999 (file has 148 lines) |
| step_without_check_field (copies/ca/step_without_check_field.md) | as expected | C1 FAIL step 9 lacks Check |
| no_result_line (copies/ca/no_result_line.md) | as expected | G1 FAIL last line starts with RESULT: () |
| steps_twice (copies/ca/steps_twice.md) | as expected | B1 FAIL step numbers [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 1, 2, 3, 4, 5, 6, 7, 8, 9 |
| empty_file (copies/ca/empty_file.md) | as expected | S0 FAIL section 2 (between '## 2.' and '## 3.') not found |

RESULT: done, the three checks now fail the reviewer's faulty copies on lines that name each fault (TESTS PASS 142 of 142 as expected), N2 and N7 are done, and the honest files fail only on real faults of the list (28 CRs) and of the guide (26 stale placement.csv citations and one unnamed placement row).
