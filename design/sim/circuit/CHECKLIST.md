# Checklist (brief of the lead, 2026-11-13; opened 00:17 CET)

Close as `[x] N. item ... evidence: <file>` or `[-] N. item ... not done: <measured limit>`.

- [x] 1. a: make_decks.py builds each deck from netlist.csv and parts.csv (values and connections read, not retyped); a rerun gives new decks ... evidence: make_decks.py + circuit_lib.py; logs/make_decks_final.log; results/rerun_diff_broken1.txt
- [x] 2. b: models in models/: maker model where public (fetched with source address) else own model marked "own model" in line 1; every value with page ... evidence: models/*.lib, models/SOURCES.md (7 own models, first line marked; maker models fetched, unchanged, not runnable: logs/ti_tps2553_model_trial.out, logs/ti_model_trials/)
- [x] 3. b: nPM1304 model: regulator outputs with current limits, battery limit 100 mA, charger 15 mA and 4.35 V, power-fail threshold ... evidence: models/npm1304.lib (outputs, IBATLIM 100 mA, charger 15 mA and 4.35 V as parameters, power-fail 2.7 V hysteresis)
- [x] 4. b: cell model from cell.md as source plus series resistance; sweeps over a stated resistance range; limit resistance per pass line named ... evidence: make_decks.py add_cell, results/r1_row_limits.csv, sim-notes.md section 4
- [x] 5. c: pass-lines.md written before the first run of each test (time stamps) ... evidence: pass-lines.md time stamps 00:17, 00:26, 00:27:59, 00:46:10; expected-failures.md 00:51:47
- [x] 6. c1: motor start 175 mA, run 80 mA, recording on; cell >= 3.0 V; rails in range; largest passing cell resistance at 20 percent charge ... evidence: results/summary.txt ring1 line; results/r1_row_limits.csv; sim-notes.md finding 4 (the test fails by 5 mV: a finding)
- [x] 7. c2: power-up rails order and levels at cell 3.3 V and 4.35 V ... evidence: results/summary.txt ring2 line; results/info.txt
- [x] 8. c3: charge path VBUS 5 V through pads and protection part to the power chip: 15 mA, end 4.35 V, input current limit ... evidence: results/summary.txt ring3 line
- [x] 9. c4: storage supply inrush with C60 as in the files and with decision 24 (3.4 uF) ... evidence: results/summary.txt ring4 line; results/info.txt (ring4 lines)
- [x] 10. c5: level shifter and storage lines both ways with netlist pull-ups ... evidence: results/summary.txt ring5 line
- [x] 11. c6: joystick and record lines pressed and released ... evidence: results/summary.txt ring6 line; results/search_nordic_limits.log (Nordic limits not found, stand-in marked)
- [x] 12. c7: pads on the finger, voltage between any two pads 10 s after VBUS removal ... evidence: results/summary.txt ring7 line (fails: finding 1)
- [x] 13. d: case boost to VRING with the 401 mA current-limit part, 5 V ... evidence: results/summary.txt case1 line
- [x] 14. d: case cell charger: CE level at power-on and with the pin low against the charger thresholds (SIMULATED, rows C2.5 to C2.7), register values written and the defaults (DATASHEET FACT rows C2.8 to C2.12, a register value is not a circuit proof), charge current with defaults if CE were low (C2.13) ... evidence: results/summary.txt case2 line PASS 10 of 10 (13 Nov, sim-notes.md section 13); broken copy broken_case2_ce_gnd fails C2.5, C2.6 (results/prove_fail.log)
- [x] 15. d: case thermistor window at the stated resistors ... evidence: results/summary.txt case3 line
- [x] 16. d: case LED currents with the anode on SYS, R8 510, R9 and R10 270 ohm (SIMULATED rows C4.5 to C4.9) ... evidence: results/summary.txt case4 line PASS 5 of 5 (13 Nov, sim-notes.md section 13); broken copy broken_case4_anode_3v3 fails C4.6, C4.7 (results/prove_fail.log)
- [x] 17. d: case section 7 risk 1 (ESD part voltage): simulated or cannot, with reason ... evidence: sim-notes.md section 5 risk 1; results rows C1.2
- [-] 18. d: risk 2 (U2 D+/D- open) ... not done: risk 2 not simulated: the source detection of the BQ25895 has no public model (sim-notes.md section 5)
- [-] 19. d: risk 3 (PMID load while charging from USB) ... not done: risk 3 not simulated as a circuit: input current regulation has no model; arithmetic only (sim-notes.md section 5)
- [-] 20. d: risk 4 (full-speed USB over pins and wires) ... not done: risk 4 not simulated: no wire resistance, inductance or driver impedance in any file (sim-notes.md section 5)
- [-] 21. d: risk 5 (strapping pins) ... not done: risk 5 not simulated: pull states are inside the module (sim-notes.md section 5)
- [x] 22. d: risk 6 (LED dim) ... evidence: risk 6 simulated on the case circuit of 13 Nov (anode on SYS): case4 line, rows C4.5 to C4.9; green 2.07 mA at SYS 3.5 V; dim (0.85 mA green) if SYS were 3.0 V (information, sim-notes.md section 13)
- [x] 23. d: risk 7 (TS window) ... evidence: risk 7 simulated: case3 line
- [x] 24. d: risk 8 (CE pulled up by R21 to 3V3): CE level simulated (rows C2.5 to C2.7); defaults 4.208 V and 2.048 A still exceed the cell (datasheet facts C2.11, C2.12); what the software writes is a datasheet fact (C2.8 to C2.10), not a simulated proof ... evidence: case2 line (sim-notes.md section 13)
- [-] 25. d: risk 9 (TPS63802 MODE on GND) ... not done: risk 9 partly: 3V3 level simulated (case5 line); power-save behaviour not simulated (sim-notes.md section 5)
- [x] 26. e: run_all.sh runs every deck, compares by script, one line per test PASS or FAIL with value and limit, ends RESULT PASS or RESULT FAIL, exit 0 or 1; outputs in results/ ... evidence: run_all.sh; results/run_all.log last line RESULT FAIL, exit 1
- [x] 27. f: broken copy 1 (wrong capacitor value) fails its named test; expected failures written before the run ... evidence: results/prove_fail.log broken1_capacitor PROOF OK
- [x] 28. f: broken copy 2 (missing pull-up) fails its named test ... evidence: results/prove_fail.log broken2_pullup PROOF OK
- [x] 29. f: broken copy 3 (swapped regulator output) fails its named test ... evidence: results/prove_fail.log broken3_swapped PROOF OK
- [x] 30. g: tests that fail on the real design are kept failing and listed first with numbers; design not changed ... evidence: sim-notes.md section 1; the design files were not changed
- [x] 31. h: limits written plainly (maker model vs own model vs nothing; radio, sound, real cell); no sentence "proven on hardware" ... evidence: sim-notes.md section 6
- [x] 32. sim-notes.md: points a to h with file, command, result line per test; findings list; "Changes other files need"; last line RESULT: ... evidence: sim-notes.md (last line starts with RESULT:)
- [x] 33. final audit script run on final reply and files; audit output saved ... evidence: results/final_audit.txt (final audit script output)
- [x] 34. whole folder under 20 MB; no git command; nothing written outside design/sim/circuit/ ... evidence: du of the folder about 12 MB; no git command was run; writes only inside design/sim/circuit/
- [x] 35. removal of what was made outside the output folder (none expected) and listing saved ... evidence: nothing was made outside the output folder except the downloads inside work/ (inside the folder); no worktree, no process left running (logs/ps_final.txt)
- [x] 36. ring test 8 (microphone supply ripple, lead's message after 01:17): rows R8.1 and R8.2 written first (pass-lines.md section C, 01:18:40) ... evidence: results/summary.txt ring8 line; results/info.txt ring8 lines
