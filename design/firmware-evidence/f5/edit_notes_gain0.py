import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
reps = [
("| Knowles clock range; gain -11 dB (0x12); microphone pins; level and clipping figures (3, 6) |",
 "| Knowles clock range; gain 0 dB (0x28, as in F4, lead's decision on H16); microphone pins; level and clipping figures (3, 6) |"),
("| header `gain_code` 0x12; die temperature from the nPM1304 (1, 3) |",
 "| header `gain_code` 0x28 (unchanged from F4); die temperature from the nPM1304 (1, 3) |"),
("| H1, H5 to H9, H12, H15 updated; H8, H9 closed; H16 to H19 new |",
 "| H1, H5 to H9, H12, H15 updated; H8, H9 closed; H16 to H19 new, H16 closed by the lead's decision |"),
("- Gain: -26 - (-37) = 11 dB; gain -11 dB; register 2 x (-11) + 0x28 = 18 = 0x12.",
 "- Gain (corrected 2026-11-11 by the lead's decision on H16): the new part is -26 - (-37) = 11 dB more sensitive; the gain stays 0 dB, as in F4; register 2 x 0 + 0x28 = 0x28. The first F5 text had -11 dB, register 2 x (-11) + 0x28 = 18 = 0x12 (`before/firmware-F5-before-gain0.md`)."),
("- Levels at -11 dB: 94 dB SPL is stored at -26 - 11 = -37 dBFS (as in F4); full scale at 94 + 37 = 131 dB SPL; the AOP of 120 dB SPL is stored at 120 - 94 - 37 = -11 dBFS. At 0 dB (not chosen) full scale is at 94 + 26 = 120 dB SPL.",
 "- Levels at 0 dB (chosen): 94 dB SPL is stored at -26 dBFS (F4, old part: -37 dBFS), 11 dB higher; full scale at 94 + 26 = 120 dB SPL, equal to the AOP of 120 dB SPL (Knowles line 105), so the digital path clips where the microphone does (F4: 94 + 37 = 131 dB SPL); a speaking voice at 60 to 70 dB SPL is stored at 60 - 94 - 26 = -60 to 70 - 94 - 26 = -50 dBFS. At -11 dB (not chosen) 94 dB SPL would be stored at -37 dBFS and full scale at 131 dB SPL.\n- Downstream of the stored level: none to recompute. F5 has no level meter and no voice-activity threshold (removed in F2); the clipped-sample flag (header bit 4) is set at the 16-bit limits -32768 and 32767 whatever the gain; T-MIC passes on channel against channel (within 3 dB of the mean of the 2), with no absolute level, so its limits do not change."),
("power sums -89.8 dBFS (SNR 63.8 dB) at 0 dB and -96.5 dBFS (SNR 59.5 dB) at -11 dB.",
 "power sums -89.8 dBFS (SNR 63.8 dB) at 0 dB, the chosen gain, and -96.5 dBFS (SNR 59.5 dB) at -11 dB."),
("1. **Gain against noise (H16).** The brief and architecture 17.19 ask the gain to change by 11 dB. Done as asked (-11 dB). By the arithmetic of section 2, this costs about 4 dB of stored signal-to-noise against 0 dB, under the stated assumption. The lead decides.",
 "1. **Gain against noise (H16), closed.** The first brief asked the gain to change by 11 dB; the first F5 text applied -11 dB and raised H16: by the arithmetic of section 2 that costs about 4 dB of stored signal-to-noise against 0 dB, under the stated assumption. The lead decided on 2026-11-11: gain 0 dB (0x28). F5 now has 0 dB in section 4.1, the header `gain_code`, change list item 3, H16 and check 18b. Architecture 17.19 still says \"so the gain setting changes\"; with this decision the setting stays and only the stored level changes (architecture owner)."),
("gain equal to the sensitivity difference read from both datasheet text files, register 2 x gain + 0x28, header `gain_code` equal;",
 "gain 0 dB (lead's decision on H16), register 0x28 = 2 x 0 + 0x28, header `gain_code` equal, and the stored full scale, 94 dB SPL minus the sensitivity of the Knowles copy, equal to the AOP of the same copy (120 dB SPL), and equal to the full scale stated in 4.1 (the first F5 check required the gain to equal minus the sensitivity difference);"),
("9. `probe_check3.log`: which names check 3 accepts as board nets on F5 (LED_A, LED_K).",
 "9. `probe_check3.log`: which names check 3 accepts as board nets on F5 (LED_A, LED_K).\n"
 "10. Gain correction (lead's decision on H16): `edit_gain0.log` (6 replacements in firmware.md), check 18b rewritten; `check_gain0_run1.log`: exit 0, 0 failures. Broken copies remade from the corrected file with two new cases written before the run (`expected_broken_gain0.txt`: b10 gain reverted to -11 dB, b11 header gain_code 0x12): `make_broken_gain0.log`, `run_broken_gain0.log`, folder `broken_gain0/`: eleven copies exit 1 as expected, the control exits 0, 0 cases differ. The earlier final run is kept as `check_final_before_gain0.log`; `check_final.log` is the run on the corrected files."),
("exits 0 on it (check_final.log) and 1 on each of the nine broken copies (run_broken_final.log).",
 "exits 0 on it (check_final.log) and 1 on each of the eleven broken copies, the gain reverted to -11 dB included (run_broken_gain0.log)."),
]
bad = 0
for a, b in reps:
    n = s.count(a)
    print(n, a[:70])
    if n == 1:
        s = s.replace(a, b)
    else:
        bad += 1
open(p, "w", encoding="utf-8").write(s)
print("not applied:", bad)
