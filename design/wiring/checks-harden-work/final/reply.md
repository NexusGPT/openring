Report (checks-harden). Notes: `design/wiring/checks-harden-notes.md` (last line `RESULT: done, ...`). Work folder `design/wiring/checks-harden-work/`.

Tests: `run_all_tests.py`, last line of `logs/run_all_tests-final.log`: `TESTS PASS 142 of 142 as expected` (check_wiring 52 of 52, check_joints 35 of 35, check_assembly 35 of 35, check_board option 2 of 2, existing joint-table tests 18 of 18, unchanged).

I1 check_wiring.py: new rules states-net, states-face, states-tail, states-colour, states-cut, states-copper (independent reads of netlists, pcbnew pads and the source tables), rebuild (every column against `build_wiring.py` run in memory), field-newline. The 5 reviewer copies now fail, each on its own line (for example `FAIL[states-net] W001 end A J_BAND_A.1 states net 'JOY_DOWN', the ring netlist says 'JOY_UP'`); 10 other fake files still fail. Notes section 1 says per field which way and what the second way cannot catch.
N2: `build_wiring.py` line 974 strips the CR (proof on a copy in W: `cr-proof.log`, live list CR 28, rebuilt copy CR 0). The generator was not run on the real list.
I2 check_joints.py: rules R6 (check: method and pass value or condition) and R7 (heat) as data tables. Dry run on the real table: 1 row rejected, J-W027-A (`final/check_joints-list-weak-snapshot1-final-rules.log`); guide-fix4 has since amended it, live table: `WEAK 0 lines in 99 rows`. Check "ok" and heat "hot" now fail.
I3 check_assembly.py: T1 (citation holds the designator, net or part of its sentence), P1 (paste on the 15 ribbon lands from joints.csv), L1 (tab, motor and disc lands from product-wiring.csv and joints.csv). The 3 reviewer faults fail on isolated copies. Of the 45 wrong bom citations (fault H5) T1 rejects 41, none of the 5 right ones; the 4 missed are named with the reason (`assembly/bom-cites-45-list.log`).
N7: `check_board.py` env var `CHECK_BOARD_OUT`, documented in the header, default unchanged, proof on a copy in W.

Honest files at the end, every failing line classified (defects of my rules: 0): check_wiring FAIL on 4 fields W054 to W057 (the 28 CRs; list not regenerated: real fault); check_joints `RESULT PASS joints 99`; check_assembly FAIL on `A1` (placement row side_slit_seal(SEAL3) in no step) and 26 T1 citations to `placement.csv:N` whose rows moved (listed in notes section 5 for guide-fix4; each named part is a row key elsewhere in the file).

Not caught (notes section 6): prose citations of most files, facts of the guide other than the listed forms, pairing choices of the generator.

questions_for_owner:
1. Is "continuity" alone a pass reading for R6? I accepted it so the existing mini test passes unchanged.
2. May the tool of a heat (R7) come from the row's tool field? Same reason.
3. Should the guide cite prose lines with a quote, as the wiring list does, so a check can compare them?
