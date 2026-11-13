# Stepped enable of the motor regulator U11: pass line, written before any run of this test

Question (design/wiring/lead-decisions.md row "motor soft start (correction of "sim finding 4")"): does switching
the enable line of U11 in steps lower the cell's dip at a motor start, or make it worse? Report only; no rule.

Conditions: the ring1 deck of the bench (design/sim/circuit/make_decks.py deck_motor), built from the ring files
netlist.csv and parts.csv of the folder named in each run, with the cell at open-circuit 3.45 V and series
resistance R_SPEC = (3.45 - 3.0) / 0.230 = 1.9565 ohm (run_tests.py V20, I_SPEC; pass-lines.md R1.1), the
recording loads on (as ring1). Only the MOTOR pin waveform (and, in variant M2, the motor model) changes.

Enable patterns (U1 pin MOTOR, 1.8 V logic, the pulse starts at t = 30 ms as in ring1, total on window 80 ms):
- E1 one step: high from 30 ms to 110 ms (ring1 as it is).
- E3 stepped: 3 steps of 2 ms high and 2 ms low, then high to 110 ms (firmware/docs/step6-plan.md decision D3 (a),
  the plan's own [CHOICE] values).
- E3s stepped short (my choice, to see a step shorter than U11's start-up time tSTR 550 us of
  models/tlv755p30.lib): 3 steps of 0.3 ms high and 0.3 ms low, then high to 110 ms.

Motor models (M1 W0525AB001D, Jinlong spec p6: start 175 mA, run 80 mA at 3.0 V; start time 10 ms is the ESTIMATE
of make_decks.py SRC motor_start_s):
- M1 time-based, as ring1: start resistance 17.14 ohm for the first 10 ms after the first rising edge, then 37.5 ohm.
- M2 restart (motor-drive.md 3.2 and table row (b): "Chopping the supply of a motor with its own drive IC restarts
  the IC each time"): start resistance 17.14 ohm during every on time of the steps and for 10 ms after the last
  rising edge, then 37.5 ohm. M2 equals M1 for E1.

C84 values: 4.7 uF and 10 uF (nominal values, as parts.csv writes them). Info runs (not pass lines): C84 at its
DC-bias value at 3.0 V read from design/ecad/ring/pcb/u4-capacitors.md: 4.7 uF part about 3.25 uF (between 3.9 uF
at 2 V and 2.6 uF at 4 V, line 27), 10 uF part about 4.0 uF at 3 V (line 28).

Quantity: vbat_min = lowest voltage at the cell terminal (net VBAT at BT1 +) from 30.5 ms to 110 ms
(the same window start as ring1: meas from 0.0305).

PASS LINE (each run): vbat_min >= 3.0 V (decision 41, pass-lines.md R1.2).
Comparison reported for each C84 value and each motor model: vbat_min(E3) - vbat_min(E1) and
vbat_min(E3s) - vbat_min(E1); positive = the stepped enable lowers the dip, negative = it makes it worse.

Expected before the run (my prediction from the model text): with M2 the stepped enable is no better than one step
(each on time charges C84 again and the motor restarts); with M1 the stepped enable may look better only because
the start window of the motor model ends during the steps (an artefact of a time-based motor model).
written 2026-11-13 12:52:45 CET (date)

## Addendum 1, written after the first run and before the second (the pass line above is unchanged)

First run (out/, logs/stepped.log): every stepped case read lower than one step (E3: 2.9825 V at every C84 value). The trace
(diag2_E3_4p7.log) shows the lowest cell voltage falls in the LOW times of the steps (32.7 ms, 36.7 ms), when U11 is meant to be
off: in the bench's own model models/tlv755p30.lib the output stays driven for about 0.7 ms after EN falls (ramp node above 1,
decaying with 0.55 ms) while its 120 ohm pull-down is already on, so U11 carries 191 mA in place of 170 mA. That is a defect of
the model at a falling EN, not a property of the circuit; the first run is kept as a record and is not used for the answer.
Second run: the same cases with models/tlv755p30_dis.lib of this folder (OWN MODEL, two changes named in its header), the
reference E1 included, so both sides use the same model. Expected: E1 unchanged (3.02319 V at 4.7 uF, 2.99503 V at 10 uF:
the changes act only at a falling EN); with E3 each step charges C84 again from about 0 V, so the dip of each step is about
the dip of one step at the same C84 (no better); E3s (0.3 ms steps, shorter than tSTR 550 us) may differ.
addendum 1 written 2026-11-13 12:59:03 CET (date)

## Addendum 2, written after the second run and before the third (the pass line above is unchanged)

Second run (out_dis/, logs/stepped2.log) is not valid either: diag2_dis_E3_4p7_edge.log shows that at the falling EN edge the
model tlv755p30_dis.lib drives VMOT to -2.49 V and its input draws a false current near 1 A from the cell (the cell falls to
2.645 V within 15 us). The target-to-0-V change of addendum 1 is the cause. Third run: models/tlv755p30_sw.lib (OWN MODEL,
header names the two changes): with EN low a switch opens the pass path, OUT keeps only the 120 ohm pull-down and the load.
Expected: E1 unchanged (3.02319 V at 4.7 uF, 2.99503 V at 10 uF); during the low times the cell rises (U11 takes ~0 mA);
each rising edge charges C84 again from near 0 V through a new 550 us start-up, so each step dips about as deep as one step.
addendum 2 written 2026-11-13 13:01:27 CET (date)
