I moved the wiring diagram and parts list to A7, and all five inputs are in. The netlist check passes, KiCad's ERC finds 0 violations, and check_bom.py has 3 failures, all of the kind the brief allows. The details are in `design/ecad/ring/sch-notes.md` section 12, and its last line starts with `RESULT: done`.

**Checks (logs in `design/ecad/ring/evidence/`)**
- run_all.sh with tag a7_final (`a7/run_all_a7_final.log`): gen_sch, erc, pdf and check_netlist all exit 0. `check_a7_final.log` ends `RESULT PASS netlist netlist.csv`.
- ERC: `erc-report_a7_final.txt` says "ERC messages: 0 Errors 0 Warnings 0".
- The new checks can fail. One broken copy with six pins moved (`a7/broken/`) ends `RESULT FAIL 7` with exit 1. It hit A7-1 to A7-5, the KiCad compare, and A6-3, which I had not predicted: A6-3 lists C71 on VBUS and the copy moved C71.
- `check_bom.py` (`a7/check_bom.log`): 3 failures. They are the section 2 part names IM68D128B, IM68D128BV01XTMA1 and NSR0230P2T5G, which are no longer in the parts list. The A6 parts list had 0. Section 12.4 gives the architecture.md rows to change (lines 41 and 51, plus 50 and 60, which don't fail but are out of date).
- `open-pins.csv`: 105 rows before, 63 after; U2 rows went from 34 to 0 (`a7/counts.log`).
- No new or changed parts list cell holds an absolute path (169 cells checked, `a7/abs_paths.log`).

**What changed**
- **Power chip U2:** it now has its 35 real balls from `npm1304-balls.csv`, no GPIO4, and order code nPM1304-CAAA-R7.
  - C71 is now 1.0 uF 25 V; new C85 (2.2 uF, battery balls) and C88 (third 10 uF on VSYS).
  - D4: the LOADSW chapter gives no capacitor rule, so I followed Nordic's configuration 2 (page 158): C86 1.0 uF on VDD_MIC, C87 on VDD_SD.
- **Motor:** the motor-drive study's changes W1 to W12 and B1 to B6 are in. That means U11 TLV75530PDQNR, C83, C84 and the net VMOT, with Q1 and D1 removed. Pad 6 of J_BAND_A is now ground.
- **Microphones:** U5 and U6 are now the SPK0641HT4H-1 with 8 pins, nets unchanged. The membranes MEM1, MEM2 and gaskets GSK2, GSK3 follow the new path.
  - The datasheet says no Class 2 capacitor near the microphone. So C35 and C36 must be Class 1 and their old X5R order code is removed.
- **Recording light:** R41 is 820 ohm and LED1 pad 1 is the cathode. The LED1 line has its new text and place, and LG1 and LP1 are new lines.
- **Cell and earlier decisions:** BT1 now reads 20 to 27 mAh at US 9 and 18.2 mAh at US 7. One control, the 8 and 7 pad split, and U10 with C81 and C82 are checked again.

**Choices and refusals (section 12.2)**
- I kept C76 and C77. Nordic's reference leaves them out but doesn't say to remove them.
- Several capacitors have empty order codes, each with an open action: C71, C85, C86, C87, C88, C35, C36 and R41. No maker sheet for a matching part is on file, and I fetched nothing.
- I made no change in firmware.md, architecture.md, mech, or pcb. What the board file must change is listed in section 12.3.

**New open points (section 12.5)**
- VDD_SD now carries 5.9 uF. The C60 line cites a 5 uF limit from another maker's storage part; the actual part's limit has not been read.
- C31 and C32 are X5R parts on the microphone supply, so they must be placed away from the microphones.

**Before you commit**
- I did not run a full check of the A6 files before editing; the A6 baseline is the saved A6 evidence.
- Other helpers changed architecture.md, case/, look/ and mfg/ meanwhile (`a7/untouched.log`), not my commands. Cited line numbers re-checked (`a7/arch_lines_recheck.log`).

RESULT: done, check_netlist.py RESULT PASS (exit 0), ERC 0 violations, check_bom.py exit 1 with 3 section 2 part failures
