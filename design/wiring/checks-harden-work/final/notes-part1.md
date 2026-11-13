# Hardening of three wiring checks (review 4, instrument faults I1, I2, I3, notes N2 and N7)

Builder: checks-harden. Work folder W = `design/wiring/checks-harden-work/` (scripts, broken copies in `copies/`, logs in `logs/`, final runs in `final/`). Clock: started 17:31 (`date`), tests last run 18:04. Files changed (all in Owns): `design/wiring/check_wiring.py`, `design/wiring/build_wiring.py` (the CR fix only), `design/mfg/assembly/check_joints.py`, `design/mfg/assembly/check_assembly.py`, `design/ecad/ring/pcb/check_board.py` (output folder option only). I ran no git, no browser, no web request, no generator that writes a delivered file (the generator ran only with `WIRING_OUT` in W and `WIRING_NO_DRC=1`), no `check_band.py`. `joints.csv`, `assembly.md`, `product-wiring.csv` and the review folder were only read.

## Result in one block

- Test runner `run_all_tests.py` in W, last line of `logs/run_all_tests-final.log`: `TESTS PASS 142 of 142 as expected` (check_wiring 52 of 52, check_joints 35 of 35, check_assembly 35 of 35, check_board option 2 of 2, existing joint-table tests 18 of 18; the existing tests passed unchanged, `joint-table-work/tests/expect.txt` was not edited).
- Reviewer's faulty copies, before (reviewer's logs) and after (my runs, same entry points): check_wiring `RESULT fakes=17 differs=5` before; now all 5 faulty copies fail, each on a line naming its fault, and the 12 other fakes still fail. check_joints `differs=2` before; both fail now. check_assembly `differs=3` before; all 3 fail now on isolated copies. Details per check below.
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
| the other 12 fakes | failed | all 12 still exit 1 | same names |

The reviewer's own files were made from the list with the 28 CRs, so they also fail on field-newline; the isolated copies are made from the corrected list (`copies/rebuilt-fixed.csv`), so each fails only for its own fault. Control `honest_fixed_copy`: exit 0.
