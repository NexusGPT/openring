import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
reps = [
("inside the microphone's normal mode, 1.2 to 1.65 MHz [DS table 5]. Accepted by the lead (H1).",
 "inside the microphone's performance mode, 1.000 to 4.800 MHz [DS Table 3, line 95], and outside its low-power mode, 350 to 800 kHz [DS Table 4, line 121]. Accepted by the lead (H1)."),
("| `min_pdm_clk_freq` / `max_pdm_clk_freq` | 1,200,000 / 1,650,000 Hz (normal mode [DS]) |",
 "| `min_pdm_clk_freq` / `max_pdm_clk_freq` | 1,200,000 / 1,650,000 Hz **[CHOICE]**: kept from F4 so the driver's pick stays 1.280 MHz; the window lies inside the performance mode, 1.000 to 4.800 MHz [DS line 95] |"),
("| Gain | `gain_db = 0`, register value 0x28 = 0 dB on both GAINL and GAINR (driver writes `2 * gain_db + NRF_PDM_GAIN_DEFAULT`, range 0x00 = -20 dB to 0x50 = +20 dB) [SRC 2, SRC 3] |",
 "| Gain | `gain_db = -11`, register value 0x12 = -11 dB on both GAINL and GAINR [CALC: 2 x (-11) + 0x28 = 40 - 22 = 18 = 0x12] (driver writes `2 * gain_db + NRF_PDM_GAIN_DEFAULT`, range 0x00 = -20 dB to 0x50 = +20 dB) [SRC 2, SRC 3]. F4 had 0 dB (0x28) for a microphone of -37 dBFS; the SPK0641HT4H-1 is -26 dBFS [DS line 100], 11 dB more [CALC: -26 - (-37)], so the gain drops by 11 dB and a sound gives the same stored level as in F4 |"),
("| Channel order in memory | left = mic 1 (LR to ground, at X = -11 mm), right = mic 2 (LR to VDD_MIC, at X = +11 mm) (architecture W4, 16.3) |",
 "| Channel order in memory | left = mic 1 (U5, pin 3 SELECT on GND, at X = -10.8 mm), right = mic 2 (U6, pin 3 SELECT on VDD_MIC, at X = +10.8 mm) (architecture 17.19, netlist.csv) |"),
("- The microphone with L/R to ground drives data after the falling clock edge; with L/R to VDD after the rising edge [DS table 8]. Which nRF channel each lands in is checked by factory test T-MIC (section 9.3) and is listed in section 10.5.\n- Gain stays at 0 dB: raw samples are stored, gain is applied later off the ring.",
 "- Wiring of each microphone (sch-notes section 12.1 item 14, netlist.csv): pin 1 DATA (U5 through R31, U6 through R32, both onto MIC_A_DATA), pin 2 CLOCK on MIC_A_CLK, pin 3 SELECT (U5 on GND, U6 on VDD_MIC), pin 4 Vdd on VDD_MIC, pins 5 to 8 GROUND. The datasheet's timing figure gives each SELECT level its own half of the clock cycle [DS Figure 1, sheet 3]; its text copy does not name the edge in words, so which nRF channel each microphone lands in is checked by factory test T-MIC on every ring (section 9.3) and listed in section 10.5.\n- Levels with the gain of -11 dB [CALC, `design/firmware-f5-notes.md`]: a 94 dB SPL tone at 1 kHz is stored at -26 - 11 = -37 dBFS, as in F4; full scale (a clipped sample, chunk flag bit 4) is reached at 94 + 37 = 131 dB SPL, above the microphone's acoustic overload point of 120 dB SPL [DS line 105], which is stored at 120 - 94 - 37 = -11 dBFS. Samples are stored as they come from the PDM; any further gain is applied off the ring. The cost of the lower gain on the noise floor is hardware issue H16."),
("From the datasheet [DS tables 5 and 6]: VDD ramp-up time at most 50 ms; start-up time 20 ms to ±0.5 dB sensitivity and 50 ms to ±0.2 dB, after VDD and clock are applied; mode switch time 20 ms; clock-off current 1 µA with the clock pulled low; the data pin is high-impedance in standby.",
 "From the datasheet [DS Table 2, text lines 79 to 89]: power-up time at most 50 ms (from Vdd at or above its minimum); wake-up time at most 15 ms; mode change time at most 10 ms; in sleep mode (clock under 250 kHz) DATA is high-impedance [DS note 3] and the part draws 26 µA with the clock stopped [DS Table 5]. Supply 1.6 to 3.6 V, VDD_MIC is 1.8 V [DS line 74]. Current 630 µA typical, 710 µA maximum at 1.8 V, measured at a 2.4 MHz clock [DS Table 3, line 97]; at the ring's 1.280 MHz the datasheet gives no figure (section 10.5, item 6)."),
("2. `regulator_enable()` on the nPM1300 load switch 1 (VDD_MIC).",
 "2. `regulator_enable()` on the nPM1304 load switch 1 (VDD_MIC, ball A4 LSOUT1, netlist.csv)."),
("3. Wait 1 ms. Rail rise [CALC]: soft-start 25 mA into 2 x (1 µF + 100 nF) = 2.2 µF to 1.8 V takes 2.2 µF x 1.8 V / 25 mA = 0.16 ms (the capacitor per microphone is that of F2; the schematic of the two-microphone board is not re-read).",
 "3. Wait 1 ms. Rail rise [CALC]: soft-start 25 mA [NPM p77, LDSW1SOFTSTARTSEL] into C31 + C32 + C35 + C36 + C86 = 1.0 + 1.0 + 0.1 + 0.1 + 1.0 = 3.2 µF on VDD_MIC (netlist.csv, parts.csv) to 1.8 V takes 3.2 µF x 1.8 V / 25 mA = 0.23 ms."),
("5. Discard the first 50 ms of samples (800 frames at 16 kHz) so the stored audio has settled to ±0.2 dB.",
 "5. Discard the first 50 ms of samples (800 frames at 16 kHz). With step 3 the first kept frame comes at least 1 + 50 = 51 ms after VDD_MIC is enabled, after the 50 ms power-up time [DS Table 2]."),
("| 74 | 1 | gain_code | 0x28 |", "| 74 | 1 | gain_code | 0x12 (the PDM gain register, -11 dB, section 4.1) |"),
("| 114 | 2 | temp_c_x10 | nPM1300 die temperature, 0.1 °C, signed |", "| 114 | 2 | temp_c_x10 | nPM1304 die temperature [NPM p99], 0.1 °C, signed |"),
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
