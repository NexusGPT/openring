| Case | Run | Cells | Time steps | End value | Run time (s) | S11 before match at 2.40 / 2.44 / 2.48 GHz (dB) | Zin at 2.44 GHz (ohm) | Radiated share at 2.40 / 2.44 / 2.48 GHz (percent) | Peak gain at 2.44 GHz (dBi) |
|---|---|---|---|---|---|---|---|---|---|
| A as designed: metal body with the floor pocket | h2_A | 1412721 | 19602 | -30.93 dB | 99 | -0.12 / -0.14 / -0.15 | 0.40 -4.25j | 8.3 / 8.3 / 8.6 | -6.59 |
| B resin corner | h2_B | 1412721 | 41624 | -30.57 dB | 153 | -0.20 / -0.21 / -0.25 | 0.73 -21.77j | 1.7 / 2.0 / 1.9 | -13.69 |

| Case | Best three-part match (topology, solved values) | Worst S11 after match, 2.400 to 2.480 GHz (dB) | Same with values snapped to 0.1 nH / 0.1 pF | Snapped values | ABCD cross-check of the unsnapped worst S11 (dB) | Return-loss rule (6 dB) | Radiated-share rule (10 percent) | Case verdict |
|---|---|---|---|---|---|---|---|---|
| A | shunt inductor, series capacitor, shunt inductor: L 1.18 nH, C 3.02 pF, L 0.24 nH | -1.84 | -0.95 | L 1.2 nH, C 3.0 pF, L 0.2 nH | -1.84 | fail (worst return loss 1.84 dB) | fail | FAIL (tool not validated) |
| B | shunt inductor, series inductor, shunt inductor: L 6.43 nH, L 3.58 nH, L 1.90 nH | -2.52 | -2.50 | L 6.4 nH, L 3.6 nH, L 1.9 nH | -2.52 | fail (worst return loss 2.52 dB) | fail | FAIL (tool not validated) |

Worst S11 of every topology the search tried (dB), from the JSON field match.all_patterns_worst_db:
- A: LCL -1.84, LCC -1.51, CLL -1.77, CLC -1.42, CCL -0.57, CCC -0.11
- B: LLL -2.52, LLC -2.48, LCL -2.42, LCC -0.63, CLL -2.51, CLC -2.15, CCL -2.42, CCC -0.16

Input impedance before matching (results/h2_*_zin.csv, at the port):
| Case | 2.00 GHz | 2.40 GHz | 2.44 GHz | 2.48 GHz | 2.50 GHz | 3.00 GHz |
|---|---|---|---|---|---|---|
| A | 0.17 -25.70j (S11 -0.05 dB) | 0.36 -6.21j (S11 -0.12 dB) | 0.40 -4.25j (S11 -0.14 dB) | 0.43 -2.26j (S11 -0.15 dB) | 0.44 -1.25j (S11 -0.15 dB) | 0.48 +35.92j (S11 -0.11 dB) |
| B | 0.81 -46.62j (S11 -0.15 dB) | 0.69 -24.05j (S11 -0.20 dB) | 0.73 -21.77j (S11 -0.21 dB) | 0.82 -19.54j (S11 -0.25 dB) | 0.87 -18.46j (S11 -0.27 dB) | 1.59 +11.83j (S11 -0.52 dB) |
