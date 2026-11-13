F5 is done: `design/firmware.md` is version F5 and `design/.venv/bin/python -I design/firmware-check.py` exits 0 on it (check_final.log; rerun after the last notes edit: check_final2.log). On each of nine broken copies it exits 1 (run_broken_final.log, 0 cases differ from the expectation written before the run).

What F5 carries (one change-list item per brief point, each naming its source):
1. nPM1304: `CHARGE_CURRENT` = 15,000 µA (0.82 C of 18.2 mAh); 4.35 V = BCHGVTERM value 9 [p36]; 10 % termination [p37]; charge time per size (1.21 to 2.19 h). The discharge-limit row is removed. IBATLIM is fixed at 100 mA minimum [p28 to p30]. New section 8.7 polls BCHGILIMBATACTIVE: on ACTIVE it logs, the screen goes off for 10 s, and a recording never stops. RSTCAUSE is logged at boot. In 8.4 the ship task is written after EVENTVBUSREMOVED [p116], with no timer. New sub-command SHIP_SAMPLE keeps the factory flag (61 transitions). Devicetree: 4 charger items confirmed from research-npm1304.md; every other property is TO CONFIRM (the firmware designer, from the SDK bindings).
2. Motor: U11 through R61, R62 and MOT_EN; up to 0.55 ms delay; no PWM. Gauge adds t_on x 80 mA + 10 ms x 175 mA per pulse (ESTIMATE). T-MOTOR reads the VBAT dip.
3. Knowles SPK0641HT4H-1: gain -11 dB (0x12). Levels and clipping recomputed. 4.1 mA recording.
4. Thresholds on 18.2 mAh: B15 40, B5 13, B2 5 min. Hours 4.4 to 8.0 across US 7 to 13.
5. R41 820 ohm, 1.50 mA. 6. Pins and 20 named nets are checked against netlist.csv. 7. Factory flow by assembly step. K-A1 applied (the USB path cannot write MCUboot). The 50 percent first charge is PROPOSED. 8. Protocol sentence at the top of section 7.

Check: extended (new check 18). Replaced F4 assertions are listed in notes section 6. New check on the F4 copy: exit 1, 157 failures.

Conflicts for you (notes section 4):
- H16: the brief's -11 dB costs about 4 dB SNR (16-bit floor). Your call: keep it or go back to 0 dB.
- H17: architecture section 3 "3.1 V cut-off" is not in the nPM1304 spec (VSYSPOF 2.7 V).
- H18: 17.17 hours at 4.0 mA against 4.1 mA.
- H19: the boot-count check of assembly step 25 would see +1 (F5 sends FACTORY_EXIT first).

Not done:
- Nothing fetched, so 12 items stay unconfirmed (notes section 3).
- `design/review/attack_fwcheck.py` not run: it writes outside my files.
- Other files' line citations into firmware.md now point to other lines.
- My probe wrote a .pyc file into `design/__pycache__/`. I removed the file, but the empty folder stays (no folder deletes).

Files: design/firmware.md, design/firmware-check.py, design/firmware-f5-notes.md, evidence in design/firmware-evidence/f5/

RESULT: done, F5 written, firmware-check.py exit 0
