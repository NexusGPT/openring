"""Lead's correction of 2026-11-11: the PDM gain stays 0 dB (0x28)."""
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
reps = [
("sensitivity -26 dBFS against -37 dBFS, so the PDM gain goes from 0 dB to -11 dB (register 0x28 to 0x12);",
 "the new part is 11 dB more sensitive (-26 dBFS against -37 dBFS at 94 dB SPL); the PDM gain stays 0 dB (register 0x28, as in F4), so the stored level rises by 11 dB and full scale moves from 131 to 120 dB SPL, the microphone's own overload point (lead's decision of 2026-11-11 on hardware issue H16);"),
("| Gain | `gain_db = -11`, register value 0x12 = -11 dB on both GAINL and GAINR [CALC: 2 x (-11) + 0x28 = 40 - 22 = 18 = 0x12] (driver writes `2 * gain_db + NRF_PDM_GAIN_DEFAULT`, range 0x00 = -20 dB to 0x50 = +20 dB) [SRC 2, SRC 3]. F4 had 0 dB (0x28) for a microphone of -37 dBFS; the SPK0641HT4H-1 is -26 dBFS [DS line 100], 11 dB more [CALC: -26 - (-37)], so the gain drops by 11 dB and a sound gives the same stored level as in F4 |",
 "| Gain | `gain_db = 0`, register value 0x28 = 0 dB on both GAINL and GAINR [CALC: 2 x 0 + 0x28 = 0x28] (driver writes `2 * gain_db + NRF_PDM_GAIN_DEFAULT`, range 0x00 = -20 dB to 0x50 = +20 dB) [SRC 2, SRC 3]. F4 also had 0 dB (0x28), for a microphone of -37 dBFS; the SPK0641HT4H-1 is -26 dBFS [DS line 100], 11 dB more [CALC: -26 - (-37)], so with the same gain a sound is stored 11 dB higher than in F4 (lead's decision, H16) |"),
("- Levels with the gain of -11 dB [CALC, `design/firmware-f5-notes.md`]: a 94 dB SPL tone at 1 kHz is stored at -26 - 11 = -37 dBFS, as in F4; full scale (a clipped sample, chunk flag bit 4) is reached at 94 + 37 = 131 dB SPL, above the microphone's acoustic overload point of 120 dB SPL [DS line 105], which is stored at 120 - 94 - 37 = -11 dBFS. Samples are stored as they come from the PDM; any further gain is applied off the ring. The cost of the lower gain on the noise floor is hardware issue H16.",
 "- Levels with the gain of 0 dB [CALC, `design/firmware-f5-notes.md`]: a 94 dB SPL tone at 1 kHz is stored at -26 dBFS (F4, old part: -37 dBFS); full scale (a clipped sample, chunk flag bit 4) is reached at 94 + 26 = 120 dB SPL, equal to the microphone's acoustic overload point of 120 dB SPL [DS line 105], so the digital path clips where the microphone does (F4: 94 + 37 = 131 dB SPL); a speaking voice at 60 to 70 dB SPL is stored at 60 - 94 - 26 = -60 to 70 - 94 - 26 = -50 dBFS. The microphone's noise, -26 - 64.5 = -90.5 dBFS(A), stays above the noise of a 16-bit sample, -98.1 dBFS (H16). Samples are stored as they come from the PDM; any further gain is applied off the ring. No firmware rule uses an absolute stored level: there is no level meter and no voice-activity threshold (removed in F2); the clipped-sample flag is at the 16-bit limits whatever the gain; T-MIC compares the two channels with each other (section 9.3), so its pass limits do not change."),
("| 74 | 1 | gain_code | 0x12 (the PDM gain register, -11 dB, section 4.1) |",
 "| 74 | 1 | gain_code | 0x28 (the PDM gain register, 0 dB, section 4.1) |"),
("| H16 | The brief and architecture 17.19 ask the gain to change by 11 dB for the more sensitive microphone. At -11 dB the microphone's own noise, -26 - 64.5 - 11 = -101.5 dBFS(A), falls under the noise of a 16-bit sample, -(6.02 x 16 + 1.76) = -98.1 dBFS; the stored signal-to-noise at 94 dB SPL drops from about 63.8 dB at 0 dB gain to about 59.5 dB [CALC, `design/firmware-f5-notes.md`; assumes the PDM truncates to 16 bits after the gain; not A-weighted]. At 0 dB the store clips at 120 dB SPL, the microphone's own overload point. | open | gain -11 dB (0x12) as the brief asks; one constant | the lead: keep -11 dB or go back to 0 dB; bench B7 can measure the floor |",
 "| H16 | The first F5 brief asked the gain to drop by 11 dB for the more sensitive microphone. At -11 dB the microphone's own noise, -26 - 64.5 - 11 = -101.5 dBFS(A), falls under the noise of a 16-bit sample, -(6.02 x 16 + 1.76) = -98.1 dBFS; the stored signal-to-noise at 94 dB SPL would drop from about 63.8 dB at 0 dB gain to about 59.5 dB [CALC, `design/firmware-f5-notes.md`; assumes the PDM truncates to 16 bits after the gain; not A-weighted]. At 0 dB the store clips at 94 + 26 = 120 dB SPL, the microphone's own overload point [DS line 105]. | closed by the lead's decision of 2026-11-11: gain 0 dB | gain 0 dB (0x28), section 4.1 | none; bench B7 can measure the floor |"),
("the gain register equals 2 x gain + 0x28 with the gain equal to the sensitivity difference;",
 "the gain is 0 dB, the register 0x28 (2 x 0 + 0x28), the header `gain_code` equal to it, and the stored full scale (94 dB SPL minus the sensitivity read from the Knowles copy) equal to the acoustic overload point read from the same copy;"),
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
