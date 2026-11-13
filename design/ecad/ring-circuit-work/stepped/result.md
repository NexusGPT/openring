# Stepped enable of U11: result (report only, no rule)

Pass line and conditions: `pass-line.md` (written 12:52:45 before the first run; addenda 1 and 2 written before the second and third runs). Ring files: the patched copy `../patched/design/ecad/ring` (C84 set per case by the bench's own override). Cell 3.45 V open circuit, 1.9565 ohm.

Valid run: the third (`out_sw/`, log `../logs/stepped3.log`, table `out_sw/stepped_compare.csv`), U11 from the own model `models/tlv755p30_sw.lib`.

| C84 | one step E1 | 3 x 2 ms steps E3 | 3 x 0.3 ms steps E3s | pass line 3.0 V |
|---|---|---|---|---|
| 4.7 uF | 3.02320 V | 3.02320 V (0.00 mV) | 3.02320 V (0.00 mV) | all PASS |
| 10 uF | 2.99504 V | 2.99504 V (0.00 mV) | 2.99518 V (+0.14 mV) | all FAIL |
| 3.25 uF (info: 4.7 uF part at 3 V bias) | 3.02320 V | 3.02320 V | 3.02320 V | all PASS |
| 4.0 uF (info: 10 uF part at 3 V bias) | 3.02320 V | 3.02320 V | 3.02320 V | all PASS |

Motor models M1 and M2 give the same lowest value in every case of the table (`out_sw/stepped_compare.csv`).

Result. A stepped enable does not lower the cell's dip. Each rising edge starts U11 again and charges C84 again from near 0 V. So each step dips as deep as the single step: 2.9952 V at the steps against 2.9950 V for one step at 10 uF (`diag2_sw_E3_10uF.log`, `diag_sw_E3_10uF.log`). At 4.7 uF no step dips below the settled 3.0232 V. The best case is +0.14 mV (10 uF, 0.3 ms steps), far too small to matter. With the bench's own unchanged model `tlv755p30.lib`, the stepped enable even looks 40.7 mV worse at 4.7 uF (first run, `out/`). That comes from a defect of that model when EN falls: the output stays driven for about 0.7 ms while the 120 ohm pull-down is already on (`diag2_E3_4p7.log`). The second run (`out_dis/`) is not valid either: its model drew a false 1 A at the falling edge (`diag2_dis_E3_4p7_edge.log`). Both are kept as records.

Limits. The motor is a resistor in every run (17.14 ohm at start, 37.5 ohm running). Its own drive chip and its real start-up are not modelled, so a restart at each step (motor-drive.md 3.2) is shown only as the M2 start window. How fast the real TLV755P resets its soft start after a short low time is an assumption of the own model (header of `tlv755p30_sw.lib`). Info rows: at the DC-bias values of the two parts at 3 V (u4-capacitors.md lines 27, 28), even the 10 uF part, worth about 4.0 uF there, shows no dip below 3.0232 V. So the dip of 2.995 V seen with 10 uF comes from the nominal value. With the derated parts, C2 may gain less than the nominal runs show. This is not a reason to undo C2; at 4.7 uF every case passes.
