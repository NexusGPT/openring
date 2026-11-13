import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
reps = [
("Status in F4 of the issues raised in F1 and F2, after the lead's decisions and architecture A5-draft (H8 changes in F4: the charger switch-on is no longer blocked, only the current is; H14 and H15 are new):\n\n| Id | Conflict | Status in F3 | Firmware choice | Who acts |",
 "Status in F5 of the issues raised in F1 to F4, after architecture A5-draft sections 17.13 to 17.23 (H8 and H9 close in F5; H16 to H19 are new):\n\n| Id | Conflict | Status | Firmware choice | Who acts |"),
("| 1.280 MHz, ratio 80, exactly 16 kHz, inside the 1.2 to 1.65 MHz normal mode [DS] | bench B2 measures the current |",
 "| 1.280 MHz, ratio 80, exactly 16 kHz, inside the 1.000 to 4.800 MHz performance mode of the microphone of 17.19 [DS line 95] | bench B2 measures the current |"),
("on the main board beside the cell, on the nPM1300 NTC pin (lead's note); sch-notes section 3 still lists the RT1 value as OPEN 12.2 | charger limits of section 8.1 | schematic owner: write 10 kilo-ohm and the part for RT1; its beta sets `thermistor-beta` |",
 "on the power chip's NTC pin (nPM1304 ball D3, netlist.csv) | charger limits of section 8.1 | schematic owner: the RT1 part, with B25/50 = 3,380 K for the chip's 10 kilo-ohm type [NPM p24] |"),
("| closed: PMIC_INT on nPM1300 GPIO0, SHPHLD on test pad TP19 (sch-notes sections 2 and 8) | `pmic-int-pin = 0`; wake from `SHIP` and `OFF` only by VBUS | Nordic datasheet (action 12.2) confirms the VBUS exit |",
 "| closed: PMIC_INT on nPM1304 GPIO0 (ball D6), SHPHLD on test pad TP19 (netlist.csv); VBUS above 3.9 V ends ship mode [NPM p116, p17] | `pmic-int-pin = 0`; wake from `SHIP` and `OFF` only by VBUS | none |"),
("| H7 | The motor draws below 80 mA running and up to 175 mA at each start (architecture 17.16) from a cell of 20 to 27 mAh: 2.9 to 3.9 C running, 6.4 to 8.6 C at the start. (Before 2026-11-11: 85 mA, 15 to 20 mAh, 4.3 to 5.7 C.) No cell discharge limit and no protection-circuit trip current is in the architecture. | open | the patterns are unchanged; B15 and B5 stop recording before the cell is low, but a trip of the protection circuit at 85 mA would cut power in a pulse |",
 "| H7 | The motor draws below 80 mA running and up to 175 mA at each start (architecture 17.16), now straight from the cell through U11 (17.22): 4.4 C running and 9.6 C at the start on the smallest cell, 18.2 mAh, and 2.4 C and 5.3 C on the largest, 32.9 mAh [CALC, section 3.1]. A start takes up to 228 mA from the cell with every other load on (17.22). No cell discharge limit and no protection-circuit trip current is on file. | open | the patterns are unchanged; B15 and B5 stop recording before the cell is low, but a trip of the protection circuit in a motor start would cut power in a pulse |"),
("| H8 | The nPM1300's lowest charge current, 32 mA, is above 1 C for this cell, 1.6 to 2.1 C on 15 to 20 mAh (architecture 17.5, 17.10, S12). | open, blocked (current only) | `CHARGE_CURRENT` has no value and the build fails while it is unset; the charger is on whenever VBUS is present (R-CHG); the charging states stay; T-CHARGE has no pass limit and fails when the charger is off with VBUS present | Grepow (highest charge current), then Nordic or a second charger part (S12) |",
 "| H8 | F4: the power chip of F4 could not charge under 32 mA, above 1 C of the cell. | closed by architecture 17.13: the nPM1304 charges from 4 mA [NPM p24] | `CHARGE_CURRENT` = 15 mA, 0.82 C of the smallest cell; T-CHARGE passes at 13.5 to 16.5 mA | Grepow states the cell's own limit (S12); the value changes in one place |"),
("| H9 | The IM68D128B has no datasheet in `design/datasheets/` (architecture section 2: figures from the IM68D121J brief). | open | 1.280 MHz, ratio 80 and the 50 ms discard stay as in F2, from the IM73D122V01 datasheet | design lead: save the IM68D128B datasheet, then check section 10.5 item 24 |",
 "| H9 | F4: the microphone had no datasheet on disk. | closed by architecture 17.19: the Knowles SPK0641HT4H-1 has a datasheet copy | 1.280 MHz, ratio 80 and the 50 ms discard, now from that copy (sections 4.1, 4.5) | Knowles or a distributor confirms the part is made (S23) |"),
("| open | RT1 on the nPM1300 NTC pin, 10 kilo-ohm, limits of section 8.1 |",
 "| open | RT1 on the nPM1304 NTC pin, 10 kilo-ohm, limits of section 8.1 |"),
("| open | F4 follows 17.11 (later sections win); BTN_REC is the centre switch in case `SW2` | architecture owner: rewrite those lines |",
 "| open | F4 and F5 follow 17.11 (later sections win); BTN_REC is the centre switch in case `SW2` | architecture owner: rewrite those lines |\n"
 "| H16 | The brief and architecture 17.19 ask the gain to change by 11 dB for the more sensitive microphone. At -11 dB the microphone's own noise, -26 - 64.5 - 11 = -101.5 dBFS(A), falls under the noise of a 16-bit sample, -(6.02 x 16 + 1.76) = -98.1 dBFS; the stored signal-to-noise at 94 dB SPL drops from about 63.8 dB at 0 dB gain to about 59.5 dB [CALC, `design/firmware-f5-notes.md`; assumes the PDM truncates to 16 bits after the gain; not A-weighted]. At 0 dB the store clips at 120 dB SPL, the microphone's own overload point. | open | gain -11 dB (0x12) as the brief asks; one constant | the lead: keep -11 dB or go back to 0 dB; bench B7 can measure the floor |\n"
 "| H17 | Architecture section 3 still says \"the power chip stops discharge at 3.1 V\" and section 2 and 3 still name the older power chip; motor-drive.md section 2.4 uses that 3.1 V. The nPM1304 specification read gives a power-fail reset at VSYSPOF, 2.7 V by default (2.5 to 3.4 V) [NPM p109], and a brownout at 2.4 V [NPM p29]; no 3.1 V cut-off was found. | open | B2 at 3.30 V and B5 at 3.45 V stay; VSYSPOF stays at its default (section 8.7) | architecture owner: rewrite section 3; the cell maker: the protection circuit's undervoltage limit (S12) |\n"
 "| H18 | Architecture 17.15 and 17.17 give the recording hours at 4.0 mA (4.5 to 8.2 hours across US 7 to 13); with the microphones of 17.19 the current is 4.1 mA and the hours are 4.4 to 8.0 [CALC, section 8.5]. | open | F5 uses 4.1 mA | architecture owner: update 17.17 and the key numbers |\n"
 "| H19 | Assembly step 25 reads the boot count after FACTORY ENTER and expects the same count after VBUS is removed and put back; removing VBUS in `FACTORY_TEST` reboots the ring (section 1.2), so the count rises by 1. Its stated reason (a motor start over the 100 mA limit) is also out of date since 17.22, and its step 2 still lists Q1 and D1 (17.23 says 17.22 wins). | open | section 9.3 sends FACTORY_EXIT before the count is read; the check stays as a proof of no reset | assembly owner: update steps 2 and 25 |"),
]
bad = 0
for a, b in reps:
    n = s.count(a)
    print(n, a[:70])
    if n == 1:
        s = s.replace(a, b)
    else:
        bad += 1
lines = s.rstrip("\n").split("\n")
assert lines[-1].startswith("RESULT:")
lines[-1] = sys.argv[2]
s = "\n".join(lines) + "\n"
open(p, "w", encoding="utf-8").write(s)
print("not applied:", bad)
