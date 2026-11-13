# Expected failures of the three broken copies (written before any broken copy was run)

Written at the time on the last line of this file (command `date`). The broken copies are made by `make_broken.py` from the real `netlist.csv` and `parts.csv` of `design/ecad/ring/`; the real files are never changed. Each copy is run with the full bench for the test named, and the bench must print FAIL for that test with the rows named here. A different failing row, or a pass, means the bench cannot tell the fault and the proof fails.

| copy | change | test that must FAIL | rows expected to fail | why (from the pass lines) |
|---|---|---|---|---|
| broken1_capacitor | parts.csv C60 value 2.2uF becomes 470uF | R4 (ring4 storage inrush) | R4.7 and R4.8 | at a soft start current of 50 mA or 25 mA the 3.0 V supply takes more than 1.8 ms to reach 90 percent with 470 uF (about 28 ms and 56 ms); R4.1 to R4.5 are expected to stay green |
| broken2_pullup | netlist.csv and parts.csv: pull-up R63 (SD_DAT1 to VDD_SD) removed | R5 (ring5 level shifter and storage lines) | R5.6 | the card's DAT1 input then floats and the card's leakage pulls it to ground, below 0.625 x 3.0 V |
| broken3_swapped | netlist.csv: U2 pin B6 (VOUT1) and pin C6 (VOUT2) swap nets | R2 (ring2 power-up) | R2.2, R2.3, R2.7 and R2.12, R2.13, R2.17 | VDD_1V8 then carries the 3.0 V output (peak above 1.89 V: R2.2, R2.12); VDD_3V0 the 1.8 V output (minimum below 2.85 V: R2.3, R2.13); VDD_SD hangs on VDD_3V0 and stays below 2.7 V (R2.7, R2.17) |

Each result line is compared by script (`prove_fail.py`), which prints `PROOF OK` or `PROOF FAILED` per copy.
2026-11-13 00:51:47 CET
Correction of the broken3 row, made at 00:52 (command date, 00:51:56 at the last check) before any broken copy ran: my first draft listed R2.4 and R2.14 (a 3.0 V peak on VDD_3V0), which is wrong because VDD_3V0 would carry 1.8 V; the row above is the corrected list.

Addition made after the first run of broken3 (the first run, at 01:01, read the rails at the regulator pins, so the swap did not show; the deck now reads the rails at the consumer pins U1 A4 and DISP1 VCI): the rows R2.10 and R2.20 (order of VDD_SD after VDD_3V0) can also report "no value", because VDD_SD never reaches 2.7 V when VDD_3V0 carries 1.8 V. They are listed by the script as extra failing rows, not as expected ones. The first run of broken1 and broken2 matched this file exactly (PROOF OK, logs/prove_fail_2.log).

## Case copies of 13 Nov (written at 16:42:57 CET, command date, before either copy ran; same table form)

| copy | change | test that must FAIL | rows expected to fail | why (from pass-lines.md section D) |
|---|---|---|---|---|
| broken_case2_ce_gnd | case netlist.csv: R21 pin 2 moves from 3V3 to GND | C2 (case2 cell charger) | C2.5 and C2.6 | CE then sits at 0 V at power-on (C2.5 needs at least 1.3 V) and the charger charges with its defaults, 0.602 A (C2.6 needs at most 1e-6 A); C2.4 and C2.7 to C2.13 stay green |
| broken_case4_anode_3v3 | case netlist.csv: LED1 pin A (anode) moves from SYS to 3V3 | C4 (case4 LED currents) | C4.6 and C4.7 | the green and blue colours get only the 3.3075 V rail: about 1.6 to 1.7 mA, below 2 mA; C4.5, C4.8, C4.9 stay green |

The named row of the first copy is C2.5, of the second C4.6. Both copies are made by `prove_fail.py` (one exact text edit each, checked to happen once); the copies run with `run_tests.py --case-dir`.
16:42:57
