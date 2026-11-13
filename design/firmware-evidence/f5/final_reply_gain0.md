The gain correction is applied: the PDM gain is 0 dB (register 0x28) everywhere in F5. `design/.venv/bin/python -I design/firmware-check.py` exits 0 on the delivered file (check_final.log, 0 failures). On each of eleven broken copies it exits 1, including the copy with the gain reverted to -11 dB (run_broken_gain0.log, 0 cases differ from the expectations written before the run).

Changed in `design/firmware.md` (edit_gain0.log, 6 replacements; line count still 1048):
- Change list item 3: the new part is 11 dB more sensitive, the gain stays 0 dB, the stored level rises by 11 dB, and full scale moves from 131 to 120 dB SPL. F4 also used 0 dB (0x28) for the old part, so the gain itself did not change from F4.
- Section 4.1: `gain_db = 0`, register 2 x 0 + 0x28 = 0x28. A 94 dB SPL tone is stored at -26 dBFS (F4: -37). Full scale is 94 + 26 = 120 dB SPL, equal to the AOP (Knowles line 105); F4 was 131. A voice at 60 to 70 dB SPL is stored at 60 - 94 - 26 = -60 to -50 dBFS. Microphone noise is -90.5 dBFS, above the 16-bit floor of -98.1 dBFS.
- Header `gain_code`: 0x28. H16: closed by your decision, with its arithmetic. Section 10.6 describes the new gain rule.
- Downstream: nothing to recompute. There is no level meter and no voice-activity threshold. The clipped-sample flag sits at the 16-bit limits whatever the gain. The T-MIC pass limits compare the two channels, with no absolute level. Section 4.1 states this.

Check 18b now requires: gain 0 dB, register 0x28, header `gain_code` equal to it, and stored full scale (94 minus the Knowles sensitivity) equal to the AOP read from the Knowles text, which must also match the full scale stated in 4.1. It printed: sensitivity -26 dBFS, gain 0 dB, register 0x28, full scale 120 dB SPL, AOP 120 dB SPL.

Broken copies (broken_gain0/): the nine earlier cases, plus b10 (gain -11 dB, register 0x12; 5 FAIL lines) and b11 (header gain_code 0x12; 1 FAIL line). All exit 1; the unchanged control exits 0.

Notes (`design/firmware-f5-notes.md`): section 1 rows, the section 2 gain, level, noise and downstream lines, section 4 item 1 (closed), the section 6 check text, run 10, and the RESULT line are updated. The run before the correction is kept as check_final_before_gain0.log. A new conflict for the architecture owner: architecture 17.19 still says "so the gain setting changes".

Files: design/firmware.md, design/firmware-check.py, design/firmware-f5-notes.md, evidence in design/firmware-evidence/f5/

RESULT: done, gain 0 dB applied, firmware-check.py exit 0
