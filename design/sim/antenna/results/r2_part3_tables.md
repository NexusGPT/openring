
**protocol (frozen stand-in, eps 28.08)**

| Case | Run | eps_r | End | S11 before match at 2.40 / 2.44 / 2.48 (dB) | Zin at 2.44 (ohm) | Largest return loss in 2.0-3.0 GHz (dB at GHz) | Radiated / incident power at 2.40 / 2.44 / 2.48 (percent) | Radiated share of accepted power at 2.40 / 2.44 / 2.48 (percent) | Best three-part match | Worst S11 after (dB) | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D free air | r3L_D | 28.08 | -40 dB reached, 127710 steps (-40.79 dB) | -0.00 / -0.03 / -0.01 | 0.10 +30.14j | 1.0 at 3.000 | 0.03 / 0.03 / 0.03 | 31.4 / 5.0 / 16.3 | CCC: C 1.09 pF, C 0.50 pF, C 1.75 pF | -0.10 | FAIL |
| A metal body + pocket, finger | r3L_A | 28.08 | cap, 128898 steps, energy -33.99 dB | -0.01 / -0.20 / -0.08 | 1.01 +42.96j | 2.9 at 2.610 | 0.18 / 0.33 / 0.64 | 78.4 / 7.3 / 34.0 | LCC: L 2.99 nH, C 0.51 pF, C 1.05 pF | -0.18 | FAIL |
| B resin corner, finger | r3L_B | 28.08 | -40 dB reached, 117018 steps (-40.33 dB) | -0.03 / -0.02 / -0.04 | 0.08 +30.65j | 13.1 at 2.990 | 0.01 / 0.01 / 0.01 | 1.0 / 2.0 / 1.4 | CCC: C 0.54 pF, C 0.37 pF, C 1.82 pF | -0.81 | FAIL |

**re-tune 1 (22)**

| Case | Run | eps_r | End | S11 before match at 2.40 / 2.44 / 2.48 (dB) | Zin at 2.44 (ohm) | Largest return loss in 2.0-3.0 GHz (dB at GHz) | Radiated / incident power at 2.40 / 2.44 / 2.48 (percent) | Radiated share of accepted power at 2.40 / 2.44 / 2.48 (percent) | Best three-part match | Worst S11 after (dB) | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D free air | r3T_D | 43.50 | cap, 130000 steps, energy -25.63 dB | 0.01 / -0.66 / -0.80 | 3.60 +47.60j | 7.5 at 2.525 | 0.35 / 0.77 / 3.30 | -221.3 / 5.5 / 19.6 | LCL: L 0.20 nH, C 0.10 pF, L 0.20 nH | 0.00 | FAIL |
| A metal body + pocket, finger | r3T_A | 31.26 | cap, 128601 steps, energy -31.88 dB | -0.19 / -0.16 / -0.55 | 0.96 +52.73j | 2.7 at 2.560 | 0.30 / 0.66 / 1.38 | 6.9 / 18.4 / 11.6 | LCC: L 3.70 nH, C 0.56 pF, C 0.64 pF | -1.14 | FAIL |
| B resin corner, finger | r3T_B | 41.00 | -40 dB reached, 127413 steps (-41.22 dB) | -0.29 / -0.42 / -1.00 | 2.05 +41.73j | 20.1 at 2.575 | 0.13 / 0.27 / 0.61 | 2.1 / 2.9 / 2.9 | LCC: L 4.25 nH, C 0.59 pF, C 0.96 pF | -3.36 | FAIL |

**re-tune 2 (23)**

| Case | Run | eps_r | End | S11 before match at 2.40 / 2.44 / 2.48 (dB) | Zin at 2.44 (ohm) | Largest return loss in 2.0-3.0 GHz (dB at GHz) | Radiated / incident power at 2.40 / 2.44 / 2.48 (percent) | Radiated share of accepted power at 2.40 / 2.44 / 2.48 (percent) | Best three-part match | Worst S11 after (dB) | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| D free air | r3U_D | 45.80 | cap, 129789 steps, energy -21.26 dB | -0.35 / -2.88 / -5.25 | 72.56 +122.21j | 8.0 at 2.465 | 1.04 / 5.58 / 8.19 | 13.3 / 11.5 / 11.7 | LCL: L 2.01 nH, C 1.06 pF, L 10.57 nH | -1.29 | FAIL |
| A metal body + pocket, finger | r3U_A | 33.85 | cap, 129789 steps, energy -33.43 dB | -0.17 / -0.55 / -1.05 | 4.75 +70.87j | 2.6 at 2.515 | 0.56 / 1.18 / 3.54 | 14.7 / 9.9 / 16.5 | LCC: L 3.28 nH, C 0.79 pF, C 0.10 pF | -0.84 | FAIL |
| B resin corner, finger | r3U_B | 44.90 | cap, 130000 steps, energy -39.91 dB | -1.30 / -4.16 / -21.55 | 39.67 +69.46j | 22.6 at 2.478 | 0.63 / 1.84 / 3.20 | 2.4 / 3.0 / 3.2 | LCL: L 2.67 nH, C 1.05 pF, L 16.83 nH | -4.63 | FAIL |
| B2 resin corner, no floor under antenna, finger | r3U_B2 | 44.90 | -40 dB reached, 122661 steps (-41.03 dB) | -1.09 / -2.99 / -16.84 | 24.98 +66.38j | 22.8 at 2.485 | 0.52 / 1.51 / 3.09 | 2.3 / 3.0 / 3.2 | LCL: L 2.40 nH, C 1.04 pF, L 20.00 nH | -4.60 | FAIL |
| E antenna on screen face, resin corner, finger | r3U_E | 44.90 | cap, 128601 steps, energy -29.88 dB | -0.83 / -2.13 / -15.00 | 17.07 +65.64j | 22.3 at 2.490 | 1.06 / 3.27 / 7.59 | 6.1 / 8.4 / 7.8 | LCC: L 2.99 nH, C 0.92 pF, C 0.10 pF | -4.02 | FAIL |

Ranking by radiated / incident power at 2.44 GHz (highest first), per set:
- protocol (frozen stand-in, eps 28.08): A (0.33 percent) > D (0.03 percent) > B (0.01 percent)
- re-tune 1 (22): D (0.77 percent) > A (0.66 percent) > B (0.27 percent)
- re-tune 2 (23): D (5.58 percent) > E (3.27 percent) > B (1.84 percent) > B2 (1.51 percent) > A (1.18 percent)
