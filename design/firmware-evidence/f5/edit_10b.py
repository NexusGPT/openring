import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
reps = [
("(read 2026-11-11: pages 8 to 11, 17 to 30, 36, 37, 40, 41, 69, 77, 99, 107 to 109, 116 to 120, 136, 144 to 146)",
 "(read 2026-11-11: pages 8 to 11, 17, 22 to 30, 36, 37, 40, 41, 69, 77, 99, 107 to 109, 116 to 120, 130, 136, 144 to 146)"),
("3. The nPM1300 leaves hibernate on VBUS, the register of its ship-mode task, its I2C address, and its hibernate and ship currents (nPM1300 datasheet, architecture action 12.2).",
 "3. Devicetree names for the nPM1304: every property of section 8.1 marked TO CONFIRM (the compatible of the MFD and regulator nodes, `host-int-gpios`, `pmic-int-pin`, `ship-to-active-time-ms`, the regulator, load switch, thermistor, die-temperature, trickle, VBUS-limit and charging-enable properties), whether the nPM13xx family drivers of SRC 11 serve the nPM1304 (charger sensor channels, register read and write calls), and the driver call that writes a task register. Who answers: the firmware designer, from the nPM1304 binding files and drivers of the nRF Connect SDK version the build pins (not on disk), before work item W1. Closed by the nPM1304 specification: the I2C address 0x6B [NPM p120], the ship task and its VBUS rule [NPM p116, p118], the ship current 370 nA typical [NPM p11]."),
("4. The fuel gauge needs a battery model for the actual Grepow cell; how Nordic's tools make one was not read.",
 "4. The fuel gauge needs a battery model of the actual Grepow cells; Nordic makes it with the nPM PowerUP application [NPM p99]. Whether one model serves the seven cell lengths of US 7 to 13 or each needs its own: the firmware designer with the cell maker (S12)."),
("5. Which nRF PDM channel (left or right) receives the microphone with L/R to ground under the driver's default map (factory test T-MIC checks it on every ring); for the IM68D128B the L/R pin function is not read (item 24).",
 "5. Which nRF PDM channel (left or right) receives U5 (SELECT on GND) and U6 (SELECT on VDD_MIC) under the driver's default map: the Knowles text copy shows the timing figure without naming the edge in words [DS Figure 1]. Factory test T-MIC checks it on every ring; the firmware designer reads the figure on the PDF page and confirms it on the development kit."),
("6. Microphone current at 1.280 MHz (the IM73D122V01 datasheet gives 768 kHz, 1.536 MHz and higher only; the IM68D128B figure, 0.58 mA, is from the IM68D121J brief).",
 "6. Microphone current at 1.280 MHz: the Knowles datasheet gives 630 µA typical at its 2.4 MHz test clock [DS line 97] and no figure at 1.280 MHz; bench test B2 measures it. The 0.58 mA of the old part in the subtraction of section 8.5 comes from F4 (architecture 16.8), not from a datasheet."),
("14. Whether 25 ms motor pulses are felt (bench test F1) and the motor spin-up time.",
 "14. Whether 25 ms motor pulses are felt (bench test F1), the motor spin-up time and the start allowance of 10 ms at 175 mA used for the fuel gauge (section 8.3): bench step B-M3 of motor-drive.md section 2.9. The T-MOTOR pass line of 20 mV is an estimate until bench step B-M5."),
("21. What the nPM1300 charger does in its cool and warm regions (reduced current, `term-warm-microvolt`), the charge temperature range of the Grepow cell, and the beta of RT1 (part not chosen; sch-notes lists RT1 as OPEN 12.2).",
 "21. Closed for the chip: in the cool region the nPM1304 halves the charge current, in the warm region it charges to the reduced voltage [NPM p25, Table 12]. Still open: the charge temperature range of the Grepow cell (the cell maker, S12) and the RT1 part, which must have B25/50 = 3,380 K to match the chip's 10 kilo-ohm type [NPM p24] (the schematic owner)."),
("24. The IM68D128B datasheet is not in `design/datasheets/`: its PDM clock range (the firmware uses 1.280 MHz), start-up time (50 ms discard, section 4.5), the data edge of the L/R pin, current and supply ramp are taken from the IM73D122V01 datasheet and the IM68D121J brief and not verified for it.",
 "24. Closed in F5: the microphone of 17.19 has a datasheet copy on disk; its clock range, power-up time and current are cited from it (sections 4.1, 4.5). The copy is a third-party host's copy of Knowles Rev A (2016): Knowles or a distributor confirms the part is still made (S23)."),
("26. The fuel-gauge battery model for the curved 15 to 20 mAh cell, the accuracy of its state of charge at 4.0 mA and the cell's discharge limit against the motor pulse of 85 mA (hardware issue H7).",
 "26. The fuel-gauge battery model for the curved cells of 18.2 to 32.9 mAh, the accuracy of its state of charge at 4.1 mA with the motor's charge added, and the cell's discharge limit against the motor start of 175 mA (hardware issue H7). Who answers: the cell maker (S12), then the bench."),
("30. The power chip's VBUS detection threshold, and that nothing on the nPM1300 can drive voltage onto VBUS (the nPM1300 datasheet was not read, `design/parts/research-charger.md` read only the charge-current pages).",
 "30. Read in F5: VBUS is valid at 210 mV above VBAT and wakes the chip above 3.9 V [NPM p17]. Not read: whether any nPM1304 function drives VBUS (its VBUSOUT pin, ball C3, is on a net of its own with nothing else on it, netlist.csv); the schematic owner confirms with the specification's VBUSOUT section."),
("31. The cell's highest charge current (open item S12): the 1 C limit of section 8.1 is the rule until the cell's maker answers.",
 "31. The cell's highest charge current (open item S12): `CHARGE_CURRENT` 15 mA, 0.82 C of the smallest cell, stays until the cell's maker answers.\n"
 "32. The sign the `nrf_fuel_gauge` library expects for a discharge current, and its call for an added current (section 8.3): the firmware designer, from SRC 12 at the pinned SDK version.\n"
 "33. The nRF54LM20A's own write protection for the MCUboot area (section 9.2, K-A1 rule 4) and the register or UICR setting that holds it: the firmware designer, from Nordic's nRF54LM20A product specification (not on disk).\n"
 "34. What the nPM1304 does when TASKENTERSHIPMODE is written while VBUS is still present: the specification asks the host to wait for VBUS removal first [NPM p116], which section 8.4 does; the case itself is not described. Nordic answers if it matters."),
]
bad = 0
for a, b in reps:
    n = s.count(a)
    print(n, a[:70])
    if n == 1:
        s = s.replace(a, b)
    else:
        bad += 1
# 10.6 paragraph: replace whole Run: line
i = s.index("\nRun: `design/.venv/bin/python -I design/firmware-check.py`")
j = s.index("\n", i + 1)
new106 = open(sys.argv[2], encoding="utf-8").read().strip("\n")
s = s[:i + 1] + new106 + s[j:]
open(p, "w", encoding="utf-8").write(s)
print("not applied:", bad)
