Report, case model r4 (notes: design/case/case-model-r4-notes.md; logs in design/case/r4/).

Proof lines:
- Full check r4/final_check.log: `case_check: PASS, 8012 pairs checked, 0 failures, ring sizes US [7, 8, 9, 10, 11, 12, 13]`, exit 0.
- Doc check r4/final_docs2.log: `RESULT PASS (0 findings)`, exit 0.
- Baseline r4/base_check.log: `case_check: PASS, 3447 pairs checked, 0 failures`, 22 min 42 s.

Bar:
1. Boards from their files: KiCad's Python + kicad-cli STEP on every build and again in the check (test 15a: 59 part bodies, 0 bodies on the 16 back-face test pads, box difference 0.0000 mm).
2. PASS above at US 7 to 13.
3. Lift test 17 (pass line printed before the first run: common volume <= 0.001 mm3, free space >= 0.10 mm, pins and flank faces counted as seat contacts): smallest free space US 7 0.172, US 8 0.175, US 9 0.182, US 10 0.188, US 11 0.163, US 12 0.141, US 13 0.121 mm, all to the block pocket (shell) at 0.25 mm lift; outer pins graze the band at US 7 to 9 (at most 0.000151 mm3).
4. Holding: printed board retainer (4 posts dia 1.6, 2.86 long; 0.8 web; fence to the +X wall for the plug push), foam pad 0.8 mm under the cell, 0.25 mm insulating sheet; BOM MECH18 to MECH20. Pull is held by clamp friction, else 0.4 mm to the wall (not proven). Nine leads as swept wires, test 16: cuts 9.7 to 16.2 mm, all within the parts list.
5. Broken copies, each fails its test: board 1 mm longer `FAIL 15c main board to shell 0.000 mm`; J1 1 mm taller `FAIL 15b J1 to shell 0.000 mm`; wire run lower `FAIL 16 lead_W3 free room 0.000`; tooth in lift path 252 FAIL lines in test 17. Each log's last check line is `case_check: FAIL`, then the run wrapper's end line with exit 1.

Your ruling (fix A): board moved 0.505 mm to -X; socket front 0.3000 mm behind the skin; a standard plug seats (overmold stops 0.887 to 0.893 mm in front, drawing allows 1.85). LED window axis 0.100 mm off the LED centre, air gap 1.200 mm (window now ends at the cavity wall). E1 wall 1.9745 mm, unchanged. Cell to board 0.300 mm. Outside numbers identical to C5d (r4/outside_compare.log).

Findings for others: board-notes and make_footprints.py take 4.18 (courtyard) as the socket's mating face; real body front is 3.675. design/ecad/case/pcb/geom.py would stop at its own assert if build_boards.py is rerun (case.py U1 box line gone, pcb1_x0 moved). placement.csv was rewritten at 04:18 by another helper; pad rows unchanged. check_case_docs takes the pair count from look/c5d_check_lead_rerun.log (3447): when you rerun and replace that log, the "3447 pairs checked" lines need the new count.

Process notes: the first proof chain failed 15c (light window 0.100 mm, bezel 0.195 mm from the real tab); fixed inside only, logs kept as r4/run1_*. Two broken builds failed first (model paths in the copies), fixed by text edit, logs kept. I deleted my two run1 .done files and 315 model files of my debug and broken builds (listing r4/scratch_removed_list.log, r4 now 6.3 MB). Pictures not re-rendered; four inside views may show the moved floor slot (unchecked).

RESULT: done, commit none (no git), case_check exit 0
