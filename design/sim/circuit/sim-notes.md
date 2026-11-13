# Circuit bench of the ring and the charging case: notes

Written 2026-11-13, starting at 00:07 (times from the `date` command). Folder: `design/sim/circuit/`. Every path below is relative to that folder unless it starts with a slash.

The bench reads `design/ecad/ring/netlist.csv`, `parts.csv` and `design/ecad/case/netlist.csv`, `parts.csv`, writes 13 ngspice decks, runs them through KiCad's own ngspice library, and compares every result with the pass lines in `pass-lines.md` by script. Nothing here is a measurement of a built unit. Every simulated result rests on a model made from the makers' documents (section "Limits").

Command to run everything: `sh design/sim/circuit/run_all.sh` (about 215 seconds; output also in `results/run_all.log`).
Last lines of that run (from `results/run_all.log`): `tests: 13, pass: 9, fail: 4, seconds: 213` and `RESULT FAIL`. The exit code is 1 because 4 tests fail on the real design (they are findings, section 1).
Inputs of this run: `results/inputs.txt` (size, time and sha256 of the four circuit files and of `pass-lines.md`). The ring files changed while I worked (modification times 00:20:59, 00:30:08 and 00:56:46; the switch pad numbers differed between my first and my second look). The final run used the ring files of 00:56:46 (netlist.csv sha256 c95dfaa0..., see `results/inputs.txt`); those files already hold the lead's later changes: C60 2.2 uF, C35 and C36 1nF C0G, L71 and L72 the Murata 1269AS-H-2R2M=P2. If the footprint helper rewrites the files later, rerun `sh run_all.sh`.

## 1. Findings: tests that fail on the real design (the design was not changed)

Each finding says what fails, with the numbers from `results/rows.csv`, and what evidence points the other way.

1. **Ring test 7, pads on the finger (R7.1, R7.4, R7.5): 4.498 V on the VBUS pad 10 s after the ring leaves the case; the pass line is under 0.1 V.** With a cell at 4.35 V. With a cell at 3.8 V the pad stays at 3.924 V, at 3.3 V it stays at 3.551 V (`results/info.txt`, lines "ring7 info"). D+ and D- stay at 0 V (R7.2 and R7.3 pass). Cause, read from the model and the pages: the power chip keeps VBUS connected to VSYS until VBUS falls to VBAT plus 160 mV (nPM1304 datasheet p17, VBUSVALIDF). The capacitors C71 and C72 (and C11 through R1) then keep that charge. The only leakage the makers state is 10 nA per channel of the protection part U9 (TPD4E05U06, text copy line 564 of `src/codes_tpd4e05u06.txt`). Nordic states no VBUS leakage. Evidence the other way: a leak the makers do not state can only lower the real voltage, so the figure is an upper bound; a wet finger would also pull the pad down. What-if runs (not pass lines, not in the design): a bleeder from VBUS to GND of 1000 kohm gives 0.700 V, 440 kohm gives 0.078 V, 330 kohm gives 0.021 V (cell 3.8 V; `results/info.txt`, lines "ring7 what-if"). A meter of 10 Mohm does not discharge 5.8 uF in 10 s.
2. **Case test 2, cell charger (C2.1, C2.2, C2.3): at power-on the BQ25895 charges at its register defaults.** CE is held low by R21, so charging starts without firmware. CORRECTED: today's netlist pulls CE high by R21 to 3V3 (`design/ecad/case/netlist.csv` lines 14, 45); the charger waits for the case software (lead-decisions.md rows 'sim finding 2' and 'sim findings 2 and 3, as built into the case circuit'). Defaults from the datasheet: charge voltage 4.208 V (p38) against the cell's charge voltage 4.2 V (cell sheet p1); charge current 2.048 A (p36) against the cell's allowed maximum 0.5 C = 350 mA (cell sheet p1). With the default input limit of 500 mA (p32) and no other load the bench gives 602 mA into the cell, 0.86 C. With 0.9 W taken by the rest of the case it gives 363 mA. The charge current and end voltage of the BQ25895 are set by I2C registers, not by resistors; the resistors R11 (input limit) and RT1, RT2 (thermistor) are tested (C2.4 and test 3 pass). Evidence the other way: case firmware that writes REG04 and REG06 before the first charge would remove the finding; no file I read says that firmware does.
3. **Case test 4, LED currents (C4.2, C4.3): green and blue get 1.41 to 1.97 mA, the pass line is 2 mA.** Red passes with 2.99 to 3.18 mA. The pass line of 2 mA (10 percent of the sheet's 20 mA test current) is my own choice for "visible", stated in `pass-lines.md`. The sheet gives a typical forward voltage of 3.3 V at 20 mA for green and blue and the supply is 3.308 V, so the LEDs sit at the knee. `results/sensitivity.txt` shows the green current crossing 2 mA when the typical forward voltage at 20 mA is about 3.2 V (2.22 mA at n = 4, 1.92 mA at n = 3). The sheet gives no minimum forward voltage.
4. **Ring test 1, motor start (R1.1, R1.2): at the cell resistance of decision 41 the cell dips to 2.995 V; the pass line is 3.0 V.** Decision 41 asks that "a 230 mA pulse of 100 ms leaves at least 3.0 V at the cell at 20 percent charge". With the stand-in 3.45 V for the open-circuit voltage at 20 percent (see `pass-lines.md`, no file gives it) that is 1.9565 ohm. At that resistance the bench gives 2.99503 V (limit 3.0 V) and a peak cell current of 232.5 mA, not 230 mA. The largest cell resistance that passes is 1.9277 ohm at 3.45 V (R1.1 needs 1.9565). At 3.30 V (the firmware cut-off B2) it is 1.2213 ohm; at 3.60 V it is 2.7062 ohm. The margin is small and has a known cause: with C84 (10 uF) the dip is the moment U11 finishes charging C84 while the motor draws its start current. The settled cell voltage before the end of the start is 3.0232 V (passes by 23 mV, 3.0232 V minus 3.0 V). `results/sensitivity.txt`: with C84 at 4.7 uF, 3.3 uF or 2.0 uF the dip disappears (3.0232 V). The solver check in the same file gives 2.99458 to 2.99678 V over five solver settings, so the number is stable to 2.2 mV. `motor-drive.md` section 2.3 estimates that a 10 uF X5R 0402 part keeps a third to a half of its value at half its rating, so the real dip may be smaller; I did not model that derating. Verdict: the pass line is missed by 5 mV (3.0 V minus 2.99503 V) with the files as they are; treat it as marginal, not as a failure of the circuit.

Tests that pass: ring 8 (microphone supply ripple), ring 2 (power-up), ring 3 (charge path), ring 4 (storage inrush), ring 5 (level shifter), ring 6 (joystick), case 1 (boost to VRING), case 3 (thermistor window), case 5 (3V3 rail). Several of these pass because the model is built from the same stated values the pass line uses (section 6, "Limits"); the table in section 3 says which.

## 2. Points a to h of the brief

| Point | Where | Command | Result |
|---|---|---|---|
| a. deck builder reads the files | `make_decks.py`, `circuit_lib.py` | `python make_decks.py` (also `--ring-dir`, `--case-dir`, `--set REF=VALUE`) | `wrote 13 decks`, `logs/make_decks_final2.log`. Every passive value and every IC connection comes from the files. Each deck ends with two comment lines: parts included and parts left out with the reason (`results/deck_parts.json`). A rerun on a changed netlist gives changed decks: `results/rerun_diff_broken1.txt`, `rerun_diff_broken2.txt`, `rerun_diff_broken3.txt` (diffs of the real decks against the decks of the three broken copies; the netlist change shows in the deck) |
| b. models | `models/`, `models/SOURCES.md` | none | 7 own models, each marked "own model" in its first line with the page of every value. No maker model could be run (section 6). Cell: voltage source with series resistance, swept (section 4) |
| c. ring tests with pass lines first | `pass-lines.md`, `run_tests.py` | `sh run_all.sh` | rows R1.1 to R8.2, 66 rows. Order: section 3 |
| d. case tests | `case_decks.py`, `case_tests.py`, pass-lines section B | same | rows C1.1 to C5.2, 22 rows; the nine risks: section 5 |
| e. runner | `run_all.sh` | `sh run_all.sh` | one line per test, then `RESULT FAIL`, exit 1; output in `results/` |
| f. bench can fail | `prove_fail.sh`, `prove_fail.py`, `expected-failures.md` | `sh prove_fail.sh` | `PROOF RESULT OK` (`results/prove_fail.log`); section 7 |
| g. failing tests kept | section 1 | none | 4 tests fail, the design was not changed |
| h. limits | section 6 | none | written plainly |

## 3. Tests, pass lines and results

Order proof for the pass lines (they come first): `pass-lines.md` section A carries the time 00:17 (command `date`) and says one trial deck of test 1 was run at about 00:23 to debug the deck; section A addenda carry 00:26 and 00:27:59; section B (case) ends with the time stamp 00:46:10, and the file `case_decks.py` was created at 00:47:28 (file system creation time). `expected-failures.md` ends with 00:51:47, before any broken copy ran. The two sentences in those files about the time of a trial run are from my own clock readings.

Result lines, verbatim from `results/summary.txt`:

```
FAIL ring1 motor start: 8 of 10 rows hold; R1.1: motor.rmax_ocv345 = 1.92771 needs >= (3.45-3.0)/0.230 ohm; R1.2: motor.vbat_min_spec = 2.99503 needs >= 3.0 V
PASS ring2 power-up: 20 of 20 rows hold; tightest row R2.2: powerup.v18_peak_c330 = 1.8 holds <= 1.89
PASS ring3 charge path: 7 of 7 rows hold; tightest row R3.3: charge.vbat_end_max = 4.35 holds <= 4.35*1.01
PASS ring4 storage inrush: 8 of 8 rows hold; tightest row R4.4: inrush.v30_min_ss50 = 3 holds >= 2.85
PASS ring5 level shifter and storage lines: 10 of 10 rows hold; tightest row R5.8: shifter.idle_high_at_shifter_min = 2.34009 holds >= 2.0
PASS ring6 joystick and record lines: 4 of 4 rows hold; tightest row R6.3: joy.pressed_current_max = 0.000359964 holds <= 0.0005
FAIL ring7 pads on the finger: 2 of 5 rows hold; R7.1: pads.vbus_gnd_10s = 4.49786 needs < 0.1 V; R7.4: pads.vbus_dp_10s = 4.49786 needs < 0.1 V; R7.5: pads.vbus_gnd_10s_hist = 4.49786 needs < 0.1 V
PASS ring8 microphone supply ripple: 2 of 2 rows hold; tightest row R8.2: mic.ripple_5mm = 0.004385 holds <= 0.010
PASS case1 boost to VRING: 6 of 6 rows hold; tightest row C1.3: vring.ilimit_short_min = 0.400619 holds >= 0.400
FAIL case2 cell charger: 1 of 4 rows hold; C2.1: charge.vreg_default = 4.208 needs <= 4.2 V; C2.2: charge.ichg_reg_default = 2.048 needs <= 0.350 A; C2.3: charge.icc_input_limited_max = 0.602227 needs <= 0.350 A
PASS case3 thermistor window: 6 of 6 rows hold; tightest row C3.4: ts.hot_edge_rth_high = 4929.85 holds <= 4.91e3*1.05
FAIL case4 LED currents: 2 of 4 rows hold; C4.2: led.green_current_min = 0.00196783 needs >= 0.002 A; C4.3: led.blue_current_min = 0.00196783 needs >= 0.002 A
PASS case5 design risks: 2 of 2 rows hold; tightest row C5.2: boost3v3.vout_max = 3.34055 holds <= 3.6
RESULT FAIL
```

What each test does and what its numbers mean (values from `results/values.json` and `results/info.txt`):

| Test | What the deck does | Result and reading |
|---|---|---|
| ring1 motor start | cell (open-circuit 3.45 V, series resistance swept), U2 model, U11 model, motor 17.14 ohm for 10 ms then 37.5 ohm for 70 ms, recording loads on (main chip 3 mA, 2 microphones, storage write 25 mA, screen 55 mW), pulse of 80 ms. Command via `run_all.sh`; deck `results/decks/ring1_motor.cir` | cell minimum 2.995 V; VDD_1V8 stays 1.8 V; VDD_3V0 minimum 2.885 V (limit 2.85); VMOT minimum 2.912 V (limit 2.7); VSYS minimum 2.985 V (limit 2.7); chip battery path 80.6 mA (limit 100 mA); U11 219.5 mA (limit 560 mA). Resistance limit per row at 3.45 V: `results/r1_row_limits.csv` (cell at 3.0 V: 1.932 ohm; VDD_3V0 at 2.85 V: 2.172 ohm; VMOT at 2.7 V: 3.127 ohm; VSYS at 2.7 V: 3.586 ohm; VDD_1V8 at 1.71 V: 3.051 ohm; R1.4, R1.6, R1.9 and R1.10 hold over the whole sweep to 4 ohm). So the cell voltage is the limit, then VDD_3V0 |
| ring2 power-up | cell 3.3 V and 4.35 V (1 ohm), the host enables LDSW2 at 20 ms and LDSW1 at 40 ms | 1.8 V, 3.0 V rails settle at the set values; VDD_SD and VDD_MIC rise 0.37 ms and 0.19 ms after their enables (0.0203677 s minus 0.02 s, and 0.0401926 s minus 0.04 s, `results/info.txt`); VMOT stays 0 V (R62 and U11 off). Both bucks start together at 1.99 ms (nPM1304 p45 states one start time of 1.2 ms and no order). The peaks equal the set values because the model has no overshoot: the peak rows cannot fail on the model; they test the wiring (shown by broken copy 3) |
| ring3 charge path | VBUS 5 V through a path resistance (0.5 ohm, and 2 ohm for the worst case), pads, U9, to U2 | charge current 15.0 mA over cell open-circuit 3.0, 3.6, 4.0 V and cell resistance 0.5 and 3 ohm (R3.1 and R3.2); terminal voltage 4.350 V once the current falls to 1 mA at open-circuit 4.349 V; VBUS demand with a recording running and 15 mA charge: 36.0 mA peak (limit 95 mA); VBUS at the chip 4.927 V with 2 ohm path (limit 4.0 V); VBUS minus VBAT 0.586 V at a full cell (limit 0.210 V). The 15 mA and the 4.35 V are parameters of the model taken from decision 65 and p29, so these rows test the connection, not the chip |
| ring4 storage inrush | LDSW2 enabled at 10 ms with soft start 50 mA and 25 mA; C60 from the file (2.2 uF) and with `--set C60=2.2uF` | switch current 50 mA and 25 mA (clamp of the model), VDD_3V0 minimum 3.000 V, VDD_SD final 2.99994 V, time to 90 percent 0.185 ms (50 mA) and 0.370 ms (25 mA) against 1.8 ms (p69). `parts.csv` already reads C60 2.2 uF, total 3.40 uF. With the earlier 4.7 uF (5.9 uF total) the time was 0.320 ms. What-if, soft start off: 14.88 A, VDD_3V0 falls to 2.303 V |
| ring5 level shifter | 1.8 V chip, 3.0 V card, pull-ups R60, R63, R64, R65 from the netlist, four phases (chip high, chip low, card released, VDD_SD off) | card inputs see 2.999 V high and 0.0036 V low (limits 1.875 V and 0.75 V); chip sees 1.8 V and 0 V (limits 1.26 V and 0.54 V); released DAT0 sits at 2.340 V at the shifter input (limit 2.0 V) with the worst leakages (10 uA card, 8 uA shifter); pulled-up DAT1 and DAT2 sit at 2.594 V (limit 1.875 V); card low at the shifter 0.220 V (limit 0.8 V), card high 2.949 V (limit 2.0 V); isolation 0 V (limit 0.1 V) |
| ring6 joystick | five switches read from the netlist (contact 0.5 ohm), chip pull-up 5 k, 13 k and 100 k to 1.8 V | pressed 0.00018 V (limit 0.54 V), released 1.8 V (limit 1.26 V), pressed current 18 uA to 360 uA (limits 10 uA and 500 uA). The Nordic limits for the nRF54LM20A are not on disk: the search `results/search_nordic_limits.log` lists 12 Nordic or Nordic-related files; only `mcu_nrf54l15_ds_v2.2.pdf` (a sibling chip from another maker) holds VIH and VIL. The stand-in is 0.7 x VDD and 0.3 x VDD from that file p15. The real value of the chip's internal pull-up is NOT FOUND in any file |
| ring8 microphone supply (added by the lead, rows R8.1 and R8.2 in `pass-lines.md` section C) | 1.8 V behind LDSW1 (0.2 ohm, nPM1304 p69), C86 and C31 from parts.csv, track 2 mm or 5 mm at 0.5 nH per mm (lead) and 9.33 mohm per mm (copper 0.10 mm x 0.018 mm, resistivity 1.68e-8 ohm m, standard value), C35 1nF at the pin, microphone current a square 0 to 1.42 mA (2 x 710 uA, Knowles sheet) at 1.536 MHz; one microphone only | ripple at the Vdd pin 2.53 mV peak to peak (2 mm) and 4.38 mV (5 mm), limit 10 mV. The microphone sheet gives no ripple limit; 10 mV is the lead's limit |
| ring7 pads | VBUS 5 V for 50 ms through a switch that opens, cell at 3.3, 3.8, 4.35 V, 10 s run | finding 1 |
| case1 boost | cell (3.0 to 4.2 V, 60 mohm), BQ25895 boost (5.126 V, accuracy plus or minus 3 percent), U5 with R5 from parts.csv, C2, C3, C15, C16, R12, R13, U6 | VRING 4.972 V to 5.280 V at no load; 4.901 V with 0.39 A, cell 3.0 V; current into a short 400.6 mA (minimum corner), 445.8 mA (nominal), 497.4 mA (maximum corner): the "401 mA" of the brief is the minimum corner; VRING_SENSE 1.688 V |
| case2 charger | register defaults and the ILIM resistor R11 | finding 2; ILIM pin limit 1.231 A at the minimum KILIM (row C2.4 passes against 0.5 A) |
| case3 thermistor | TS divider RT1, RT2 from parts.csv, TH1 swept | cold edge at TH1 = 27320 ohm and hot cut-off at 4930 ohm against TI's example 27280 and 4910 ohm (p23); VTS at 25 C is 0.589 of REGN (window 0.4825 to 0.7325). The match with TI's example values is a check that the bench reads the divider correctly |
| case4 LED | LED1, R8, R9, R10 from the files, 3V3 = 3.308 V | finding 3 |
| case5 rail | U3 as an ideal error amplifier closed through R3, R4 from parts.csv | 3V3 = 3.3075 V nominal, 3.274 V to 3.341 V with VFB plus or minus 1 percent; ESP32-S3 wants 3.0 to 3.6 V (p27) |

Rows that hold only because the model is made from the same numbers (they test connections, not the chip): R2.x peaks, R3.1 to R3.4, R4.1 to R4.3, R5.7, R7.2, R7.3, C1.1, C1.2.

## 4. The cell, sweeps and the resistance limit

The cell BT1 is a voltage source with a series resistance. `cell.md` gives no resistance; the case cell sheet gives below 60 mohm for the case cell only. The bench sweeps the resistance: test 1 at open-circuit 3.30, 3.45 and 3.60 V with a bisection of the resistance (largest passing value above), and a sweep of 0.25 to 4 ohm for the limit of each pass line (`results/r1_row_limits.csv`); test 3 at 0.5 and 3 ohm. The capacity of the cell in `parts.csv` is read but not used (all tests are short). The open-circuit voltage at 20 percent charge is not in any file; 3.45 V is the firmware rule B5 voltage (`firmware.md` section 1.1) used as a stand-in, and the other two values are shown so the reader can read the result at his own value.

## 5. The nine design risks of case `sch-notes.md` section 7

| Risk | Answer |
|---|---|
| 1. ESD part on VRING, 5.5 V | simulated: VRING at no load is at most 5.280 V with the boost at plus 3 percent (row C1.2 passes, margin 0.22 V, 5.5 V minus 5.27977 V). Not covered: a USB source far above 5 V on VBUS_IN |
| 2. D+/D- of U2 open | cannot be simulated: the source detection of the BQ25895 is a digital algorithm with no public model. The datasheet default for an unknown adapter, 500 mA (p32), is used in case test 2 |
| 3. PMID load while charging from USB | cannot be simulated as a circuit (the input current regulation of the BQ25895 has no model). Arithmetic from bench numbers, not a simulation: the ring link can take 0.40 to 0.50 A (C1.3 and C1.4) from a default input limit of 0.5 A |
| 4. full-speed USB over pins and 30 AWG wires | cannot be simulated with sources on disk: the wire length is in `design/wiring/connections.md` (30 mm for W1 to W4, note N17), but no file gives the wire resistance and inductance, the pin contact, or the driver impedance of the ESP32-S3; a pass line would rest on invented values |
| 5. strapping pins IO3, IO45, IO46 open | cannot be simulated: the pull states sit inside the module; no model |
| 6. green and blue LED dim | simulated: finding 3 |
| 7. TS window | simulated: row C3.1 to C3.6 pass; the window edges agree with TI's example to 0.15 and 0.4 percent |
| 8. CE pulled low by R21 | simulated: finding 2 (charging starts with register defaults that exceed the cell sheet) |
| 9. TPS63802 MODE on GND | partly simulated: the 3V3 level from the feedback divider passes (3.274 V to 3.341 V). The power-save behaviour (ripple, load steps) cannot be simulated here: TI's own model (`models/tps63802_trans.lib`) did not run in ngspice and an own behavioural model would not show it. PG unused is a netlist fact (U3 pin 5 is a no-connect pin) |

## 6. Limits, written plainly

- Which behaviours rest on a maker's model: none. TI's PSpice models of the TPS2553, TPS63802 and TLV75530P were fetched and kept unchanged in `models/`, but ngspice could not run them (`models/SOURCES.md`, `logs/ti_tps2553_model_trial.out`, `logs/ti_model_trials/`). Nordic, CS Semiconductor, Kingbright, Texas Instruments (BQ25895, SN74AXC4T774, TPD4E05U06) publish no SPICE model that was found.
- Which behaviours rest on our own models: all of them. Each own model uses numbers of the makers' documents with the page beside it. Numbers that are mine are marked MODEL CHOICE in the model file: nPM1304 buck efficiency 0.90 and output fall 5 V per ampere above 200 mA, SN74AXC4T774 output impedance 57 ohm, TLV755P dropout resistance 0.65 ohm, BQ25895 boost output resistance 50 mohm and converter efficiency 0.90, LED ideality 2 to 4.
- What no circuit simulation can show here: radio (antenna match, range), sound (microphone, sound path), the real cell (open-circuit voltage curve, resistance, protection circuit trip, ageing), real board layout (traces, vias, parasitic inductance), temperature, EMC, the firmware itself, real timing of the power chip's start sequence (the datasheet states none), the battery-current limit's accuracy (Nordic: "has not been designed for accurate current limiting", p28), and the real VBUS leakage of the nPM1304 (not stated).
- No result in this folder has been measured on hardware, and no sentence in it claims one.
- Estimates used as inputs (not maker values): motor start time 10 ms (`motor-drive.md` line 153), main chip 3 mA, screen 55 mW, 20 percent open-circuit voltage 3.45 V.
- The nPM1304 model has no overshoot, no ripple, one common start for both bucks; the VDD_1V8 and VDD_3V0 peak rows therefore cannot fail on the model alone.

## 7. Proof that the bench can fail (point f)

Command: `sh prove_fail.sh`. Last line of `results/prove_fail.log`: `PROOF RESULT OK`. Expected failures were written first (`expected-failures.md`, time stamp 00:51:47, corrected once at 00:52 before any copy ran). Copies are made by exact text edits of the real files (the edits are in `prove_fail.py`); the real files are not changed.

| Copy | Change | Test that fails | Rows that failed | Expected |
|---|---|---|---|---|
| broken1_capacitor | C60 2.2uF becomes 470uF in `parts.csv` | ring4 | R4.7 (0.0255 s against 0.0018 s), R4.8 (0.0513 s against 0.0018 s); R4.1 to R4.6 stayed green | yes |
| broken2_pullup | pull-up R63 (SD_DAT1) removed from both files | ring5 | R5.6 (0 V against 1.875 V); the other nine rows stayed green | yes |
| broken3_swapped | U2 balls B6 (VOUT1) and C6 (VOUT2) swap nets | ring2 | R2.2, R2.3, R2.7, R2.12, R2.13, R2.17, plus R2.10 and R2.20 (VDD_SD never reaches 2.7 V, "no value") | yes; R2.10 and R2.20 were not listed, added to `expected-failures.md` after the first run |

The first run of broken3 (`logs/prove_fail_2.log`) did not fail the expected rows, because the deck then read the rails at the regulator pins. I changed the deck to read the rails at the consumer pins (U1 pin A4 and the screen pin VCI), and the second run passed. The first runs of copies 1 and 2 failed with "no value" (solver stop) before I fixed the bench to separate an aborted run from a threshold that was never crossed; the saved first log is `logs/prove_fail_1.log`.

## 8. Problems found while building, and how they were settled (rule 3)

- Solver numbers: the first trial of test 1 (maximum time step 50 us) gave 3.00441 V (`logs/trial_run_tests3.log`). Cause (from the solver check in `results/sensitivity.txt`): the minimum is a sharp dip and the time step was too coarse. With a step of 5 us or less the settings of that file agree within 2.2 mV; the row with a 20 us step gives 2.99678 V. Fixed in `make_decks.py` (step 5 us).
- A resistor named `Rshort` next to a parameter `rshort` was read as 1 ohm (the case boost showed a short circuit at no load). After the rename the no-load VRING reads 4.972 V to 5.280 V (`results/values.json`). Fixed by renaming the elements (`Rcellx`, `Rpathx`, `Rbleedx`, `Rshortx`).
- Two nets `USB_D+` and `USB_D-` became one node name. Fixed in `circuit_lib.py` (`node()`).
- A deck run that aborts, times out (90 s) or hits a singular matrix now gives no values and a FAIL with its reason (`bench.py`); an unmet threshold (for example VDD_SD never reaches 2.7 V) gives no value for the rows that need it.
- Test 3 and test 7 need `method=gear` and looser tolerances (reltol 0.005); the default options abort when VBUS becomes valid in the middle of the ramp. Their numbers are therefore at that tolerance. The charge current reads 0.0149999 A.
- Expectation against result (written in `pass-lines.md` before the runs): R7.1, R7.4, R7.5 were expected to fail (they did); the cell current at the start was expected to possibly exceed 230 mA (it did: 232.5 mA). Nothing differed except the first broken3 run (section 7).
- The `ring4` test: with `parts.csv` already at C60 2.2 uF the "decision 24" variant equals the base run; the 4.7 uF variant is run as information.
- TI models: a time-boxed attempt to make ngspice run them was stopped; logs are kept in `logs/ti_model_trials/`, with the conversion script `convert_pspice.py`.
- Files I moved or compressed to stay under 20 MB (nothing deleted): scratch waveform dumps are now `work/w_x.txt.gz`, `work/w_def.txt.gz`, `work/w_tight.txt.gz`; the extracted TI downloads in `work/dl/x_*` are inside `work/dl/extracted_ti_downloads.tar.gz` (the zips stay). Trial decks moved to `logs/trial_decks/`. The folder is about 12 MB.

## 9. Not closed

- The open-circuit voltage of the real cell at 20 percent charge, its series resistance, and the protection circuit trip current (`cell.md` open point S12). Nothing in the bench or in the files fixes them; the build guide measurement (cell terminal during a motor start, pass at 3.0 V) is the test.
- Nordic's input limits and the internal pull-up of the nRF54LM20A: searched in the Nordic documents on disk (`results/search_nordic_limits.log`), not found; the stand-in is the nRF54L15 document of another maker (p15).
- Real VBUS leakage of the nPM1304 after the case is removed (finding 1): not stated by Nordic. The build guide measurement (10 s after removal, under 0.1 V between pads) decides; this bench predicts it will read several volts unless something discharges VBUS.
- Risks 2, 3, 4 and 5 of the case: not simulated, reasons in section 5.
- Power-save behaviour of the TPS63802 (risk 9): not simulated.

## 10. Changes other files need (listed, not made)

1. `design/mfg/specs/cell.md` and `design/wiring/lead-decisions.md` item 41: the requirement "a 230 mA pulse of 100 ms leaves at least 3.0 V at the cell at 20 percent charge" is 5 mV short in the bench at the resistance it implies, because the peak cell current is 232.5 mA (start 175 mA plus the charging of C84 plus the other loads). Either state the pulse as 235 mA, or state the cell resistance limit (1.92 ohm at 3.45 V, 1.22 ohm at 3.30 V), and state the open-circuit voltage at 20 percent charge that the requirement assumes.
2. `design/ecad/ring/` (VBUS net, owner of the ring circuit): add a discharge path from VBUS to GND, for example 330 kohm (0.021 V at 10 s in the what-if run), or change the build guide pass line; without one the 10 s measurement on the pads is expected to fail (finding 1). The what-if is in `results/info.txt`.
3. `design/ecad/case/` (R21 on CE, firmware of the case): hold CE high at power-on (pull R21 to 3V3) so that charging waits for firmware, and have the firmware write REG04 (charge current, at most 350 mA, recommended 140 mA) and REG06 (4.2 V or less) before it enables charging; the BQ25895 has no resistor that sets these values.
4. `design/ecad/case/` (LED1, R9, R10): move the green and blue anode supply above 3V3 (for example SYS) or accept the dim LEDs; at 3.308 V and 150 ohm they get 1.4 to 2.0 mA.
5. `design/wiring/w7-facts.md` question 2 and `design/ecad/ring/sch-notes.md` O9: the storage supply is now 3.40 uF in `parts.csv` (C60 2.2 uF); the bench shows the soft start takes 0.185 ms against the 1.8 ms of nPM1304 p69.

## 11. Files

`run_all.sh`, `run_tests.py`, `make_decks.py`, `circuit_lib.py`, `case_decks.py`, `case_tests.py`, `bench.py`, `ngrun.py` (runs one deck through KiCad's `libngspice.dylib`: the KiCad bundle has the library but no `ngspice` program, `-b` batch mode cannot be used), `prove_fail.sh`, `prove_fail.py`, `sensitivity.py`, `search_nordic_limits.py`, `pdf2txt.py`, `pgof.py`, `pass-lines.md`, `expected-failures.md`, `CHECKLIST.md`, `models/`, `decks/` (the decks of the current files), `results/` (final run), `logs/` (trial runs and first versions), `src/` (text copies of the maker documents used for page numbers), `work/` (scratch and downloads).

RESULT: done, 13 tests, 9 pass and 4 fail on the real design (ring motor start by 5 mV, ring pads on the finger, case charger defaults, case LED currents), bench proof of 3 broken copies OK

## 12. Circuit changes C1, C2, C3 of 2026-11-13 (bench rerun on the changed ring files)

What changed in `design/ecad/ring` (lead decisions "sim finding 1", "sim finding 4 (item 41)", "sim finding 4, correction", and change C3): R73 330 kohm from VBUS to GND (finding 1); C84 4.7 uF in place of 10 uF (finding 4); C90 10 uF beside C79 on VDD_3V0 (nPM1304 Table 18 page 45, effective 4 uF or more). Pass lines unchanged (`pass-lines.md`). Section 1 above describes the files before this change.

Rows before (unchanged copy of the ring files, `design/ecad/ring-circuit-work/bench_base2/`) and after (this folder, `results/`): R1.1 rmax 1.9277121 FAIL to 2.07389145 ohm PASS; R1.2 cell minimum 2.99503 V FAIL to 3.02319 V PASS; R7.1, R7.4, R7.5 4.49786 V FAIL to 0.0270141 V PASS. No row goes from PASS to FAIL (88 rows each side). ring1 and ring7 now read PASS. The 3.0 V rail rows: R1.5 VDD_3V0 minimum at a motor start 2.88534 V to 2.9046 V (the same 2.9046 V with C1 and C2 alone, `ring-circuit-work/bench_patched/rows.csv`, so the change comes from C84); R1.6, R2.3, R2.4, R2.13, R2.14, R4.4 unchanged. The buck model is ideal (no ripple, `models/npm1304.lib` line 2), so the bench cannot show the ripple benefit of C90. The what-if with the chip's soft start disabled reads VDD_3V0 minimum 2.303 V before and 2.598 V after. case2 and case4 still FAIL, as before this change: case4 gives no value ("singular matrix" at node n_3v3) since the case netlist changed at 11:47; that is the case circuit, not this change. The ring7 what-if lines in `results/info.txt` now add their bleeder on top of R73, though their text still says "not in the design" (`run_tests.py`, not changed here).

Stepped enable of U11 (row "motor soft start"; pass line written before the run: `decks/stepped/pass-line.md`; script `decks/stepped/stepped.py`; decks and results `results/stepped/`; log `logs/stepped_enable_c2.log`). Cell 3.45 V, 1.9565 ohm. Patterns: one step; 3 steps of 2 ms high and 2 ms low (firmware step6-plan decision D3 (a)); 3 steps of 0.3 ms. Result on the changed files: at C84 4.7 uF the lowest cell voltage is 3.02320 V with one step and 3.02320 to 3.02321 V with steps; at C84 10 uF it is 3.00261 V with one step, 3.00261 V with 2 ms steps and 3.00249 V with 0.3 ms steps. A stepped enable does not lower the dip: each rising edge starts U11 again and charges C84 again. U11 is the project's own model `decks/stepped/models/tlv755p30_sw.lib`: the bench model `models/tlv755p30.lib` keeps its output driven for about 0.7 ms after EN falls while its pull-down is on, which made steps read 40.7 mV worse in a first run (`ring-circuit-work/stepped/`). With C90 present, even C84 at 10 uF reads 3.00261 V, against 2.99504 V without C90 (`ring-circuit-work/stepped/out_sw/` and `out_sw_c3/`). Report only; no rule is written from it.

## 13. Case tests on the case circuit of 13 Nov

Written 2026-11-13 from 16:15 (times from `date`). Why: the two case tests that failed (case2 "cell charger", case4 "LED currents") had been written against an older case circuit. Since then the lead's row "sim findings 2 and 3, as built into the case circuit" (`design/wiring/lead-decisions.md` line 34; also lines 30 and 31) put CE on 3.3 V through R21 and the status light on SYS with R8 510 ohm, R9 and R10 270 ohm (`design/ecad/case/sch-notes.md` section 9). The tests now judge that circuit. Nothing outside this folder was changed.

**Run lines.** Base before my change (old pass lines, old code; `work/case-13nov/base_full.log`): `FAIL case2 cell charger: 1 of 4 rows hold ...`, `FAIL case4 LED currents: 0 of 4 rows hold ...`, `tests: 13, pass: 11, fail: 2` and `RESULT FAIL`. After (`sh run_all.sh`, exit 0, `work/case-13nov/run_all_final_exit.txt`, `work/case-13nov/run_all_final_stdout.txt`, `results/run_all.log`): 13 lines PASS/FAIL, `tests: 13, pass: 13, fail: 0`, last line `RESULT PASS`.
```
PASS case2 cell charger: 10 of 10 rows hold; tightest row C2.10: charge.vreg_written = 4.192 holds <= 4.2
PASS case4 LED currents: 5 of 5 rows hold; tightest row C4.6: led.green_current_min = 0.00206642 holds >= 0.002
```
The ring tests PASS in both runs; both runs read the same ring and case files (ring netlist.csv sha256 2727a3c7..., mtime 15:58:46, in `work/case-13nov/base_full/inputs.txt` and `results/inputs.txt`). No pass line was loosened: the 2 mA and 20 mA limits of the LED rows and the 350 mA and 4.2 V limits of the charger rows are the old numbers.

**Order proof (pass lines first).** `work/case-13nov/date_start.txt` 16:15:47; old file saved as `work/case-13nov/pass-lines.before.md`; new rows written into `pass-lines.md` section D, then `work/case-13nov/date_pass_lines_saved.txt` 16:17:27 and the copy `work/case-13nov/pass-lines.judged.md` (same sha256 4048c2a8... as `results/inputs.txt` shows for the judged run). `case_decks.py` was changed at 16:18:03 and `case_tests.py` at 16:18:36 (file times), the expected failures of the broken copies are in `expected-failures.md` (time stamp 16:42:57), and the first run that judged the new rows is `work/case-13nov/debug1.log` (a debug run of C2 and C4 only, kept, 10 of 10 and 5 of 5 rows hold), then the broken copies, then the full runs (first full run 16:43 to 16:46, `work/case-13nov/run_all_first_pass.log`, `rows_first_pass.csv`; final full run 16:46:30 to 16:49:27). One earlier attempt of `prove_fail.py --only` crashed with a KeyError in my own new option (log overwritten by the next run, so no file shows it); fixed in `prove_fail.py`.

**What changed per row.** Old rows are kept in `pass-lines.md` section D as `old-C2.1` to `old-C4.4` and are no longer read. Label per row (the same label is in the `kind` column of `results/rows.csv`).

| New row | Quantity and new pass line | Old pass line | Label | Result |
|---|---|---|---|---|
| C2.5 | CE level at power-on, pin not driven (45 kohm weak pull-down), 3V3 3.0 V, leakage 1.05 uA: at least 1.3 V (charger VIH, BQ25895 p10) | none (old C2.1: VREG default at most 4.2 V) | SIMULATED | 2.44595 V |
| C2.6 | charge current with the defaults at that CE level: at most 1e-6 A; rule "charging needs CE low" BQ25895 p4 and p21 | none (old C2.3: at most 0.350 A) | SIMULATED level, DATASHEET rule | 2.6e-15 A |
| C2.7 | CE level when the software drives IO18 low (VOL at most 0.1 x VDD = 0.36 V, ESP32-S3-MINI-1 p27, 3V3 3.6 V): at most 0.4 V (VIL, BQ25895 p10) | none | SIMULATED (pin level from the sheet) | 0.360315 V (margin 0.04 V) |
| C2.4 | ILIM pin limit at least 0.5 A | same limit, label added | DATASHEET FACT (KILIM p9) on R11 | 1.23077 A |
| C2.8, C2.9 | ICHG written 0000010 = 0.128 A; highest allowed code 0000101 = 0.320 A; at most 0.350 A (cell sheet p1). Codes read from `sch-notes.md` section 9, step 64 mA (BQ25895 p36) | old C2.2: default 2.048 A at most 0.350 A | DATASHEET FACT, page 36 | 0.128 A, 0.32 A |
| C2.10 | VREG written 010110 = 3.840 V + 22 x 16 mV, at most 4.2 V (p38) | old C2.1 | DATASHEET FACT, page 38 | 4.192 V |
| C2.11, C2.12 | the power-on defaults 4.208 V and 2.048 A are ABOVE 4.2 V and 0.350 A (holds when the fact is true) | old C2.1, C2.2 (at most) | DATASHEET FACT, pages 38 and 36 | 4.208 V, 2.048 A |
| C2.13 | charge current the charger would push with the defaults if CE were low: above 0.350 A (efficiency 0.90 is a MODEL CHOICE) | old C2.3 | SIMULATED | 0.602227 A (0.86 C) |
| C4.5 to C4.7 | colour current at SYS 3.5 V, curves shifted +0.15 V, pin low = 17.68 ohm (0.495 V / 28 mA, ESP32 p27): at least 0.002 A, R8 510, R9 and R10 270 ohm from `parts.csv`, anode net from `netlist.csv` | old C4.1 to C4.3, same limit | SIMULATED (curve points are my graph readings of Kingbright p3, plus or minus 0.15 V) | red 2.80 mA, green 2.07 mA, blue 2.22 mA |
| C4.8 | largest current at SYS 4.35 V, curves -0.15 V: at most 0.020 A | old C4.4, same limit | SIMULATED | 5.67 mA |
| C4.9 | current with the three pins high (the software drives them high at start-up), SYS 4.35 V: at most 1e-5 A | none | SIMULATED, but rests on the curve start points (the model has no current below the first point): it tests the 1.04 V headroom against the curve starts, not a measured leakage | 1.6e-17 A |

The LED model changed: the old deck used an exponential diode with ideality 2 to 4 (own assumption) and found its nodes no more. The new one uses the sheet's current-voltage curves (p3). Green at 3.5 V is the tightest row: 2.07 mA against 2 mA (3.5 percent); with typical curves green is 2.47 mA and the sch-notes table gives 2.2 mA.

**The power-on defaults still exceed the cell (kept visible).** REG04 default 2.048 A and REG06 default 4.208 V (C2.11, C2.12, datasheet facts) against the cell's 350 mA and 4.2 V; with CE low the charger would push 602 mA, 0.86 C (C2.13). What prevents charging with them: C2.5 (CE sits at 2.45 V at power-on even with the module pin undriven and pulling down, against the charger's VIH 1.3 V) and C2.6 (no charge current at that level). The pin is "not yet driven" in the model as a high-impedance pin with the module's own 45 kohm weak pull-down (worst case). The module sheet does not say what the pin does in reset beyond that. C2.7 shows the software can pull CE low (0.36 V against 0.4 V; thin margin, 0.04 V, at the sheet's VOL maximum).

**Broken copies** (`prove_fail.py`, `results/broken/<copy>/run.log`, full output `results/prove_fail.log` last line `PROOF RESULT OK`, exit 0, `work/case-13nov/prove_fail_all_exit.txt`; first run of the two case copies alone: `work/case-13nov/prove_fail_case.log`). `sh prove_fail.sh` runs the three ring copies and the two case copies.
- broken_case2_ce_gnd (R21 pin 2 from 3V3 to GND in the copy of `netlist.csv`): fails the named row C2.5 (CE -0.00859 V needs at least 1.3) and C2.6 (0.602227 A needs at most 1e-6); the other eight rows of the test stayed green. As expected in `expected-failures.md`.
- broken_case4_anode_3v3 (LED1 pin A from SYS to 3V3): fails the named row C4.6 (green 1.59371 mA needs at least 2 mA) and C4.7 (blue 1.73116 mA); C4.5, C4.8, C4.9 stayed green. As expected.

**Information, not rows** (`results/info.txt`): SYS at 3.0 V (cell only, if SYS follows the cell; the lead's range starts at 3.5 V), curves +0.15 V: red 1.91, green 0.85, blue 1.03 mA, so the green and blue lights are dim on a low cell with no USB. A green die at the sheet's maximum VF 4.1 V at 20 mA (p2) gives 2.61 mA at SYS 4.35 V and would not light at 3.5 V (not run at 3.5 V). With typical curves at 4.35 V: red 4.61, green 4.76, blue 5.19 mA.

**What stays unproven without hardware.** Register values (C2.8 to C2.12) are datasheet facts: no circuit simulation shows that the software really writes them, reads them back, turns the watchdog off, or that the chip accepts them; the chip's behaviour at CE (C2.6) uses the datasheet rule, not a chip model. The module pin's state during reset and boot is not in the sheet beyond the weak resistors. SYS between 3.5 and 4.35 V is the lead's range, not a simulated chip output (nothing simulates the BQ25895 SYS). The LED curves are my graph readings; the real dies at the sheet's maximum VF may be much dimmer at 3.5 V. The efficiency 0.90 in C2.13 is a model choice. R21 and the resistors are nominal values (no 1 percent tolerance). CHECKLIST rows 14, 16, 22 and 24 were updated to match.

RESULT: done, case2 and case4 now judge the case circuit of 13 Nov (13 of 13 tests PASS, exit 0; broken copies fail on C2.5 and C4.6; register values are labelled datasheet facts)
