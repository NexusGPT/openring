import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
reps = [
("nPM1300 node of section 8.1,", "nPM1304 node of section 8.1 (property names TO CONFIRM first),"),
("| W8 | Power service | thresholds, fuel gauge loop, rail control, hibernate entry, `pmic_ship_enter()` after the datasheet check |",
 "| W8 | Power service | thresholds, fuel gauge loop with the motor's charge added (section 8.3), rail control, ship entry by TASKENTERSHIPMODE after VBUS removal (section 8.4), the battery current limit status and the reset causes (section 8.7) |"),
("W8 with an nPM1300 evaluation kit;", "W8 with Nordic's nPM1304-EK kit (architecture 17.18) and the motor adapter of motor-drive.md section 2.9;"),
("| W10 | Feedback | motor pattern player with the limits of section 3.1, and the MOTOR edge times for section 4.7 (no light code: the light has no pin) |",
 "| W10 | Feedback | motor pattern player with the limits of section 3.1, the motor charge per pulse for the gauge (section 8.3), and the MOTOR edge times for section 4.7 (no light code: the light has no pin) |"),
("| W13 | Factory test | section 9.3 sub-commands, jig protocol |",
 "| W13 | Factory test | section 9.3 sub-commands (SHIP_SAMPLE included), the factory flow by assembly step, the boot loader lock of section 9.2, jig protocol |"),
("| SRC 11 | Zephyr `drivers/mfd/mfd_npm13xx.c`, `drivers/regulator/regulator_npm13xx.c`, `drivers/sensor/nordic/npm13xx_charger/npm13xx_charger.c`, bindings `nordic,npm13xx-common.yaml`, `nordic,npm1300-charger.yaml`, `nordic,npm13xx-charger-common.yaml`, `nordic,npm13xx-regulator-common.yaml`, `include/zephyr/dt-bindings/regulator/npm13xx.h` |",
 "| SRC 11 | Zephyr `drivers/mfd/mfd_npm13xx.c`, `drivers/regulator/regulator_npm13xx.c`, `drivers/sensor/nordic/npm13xx_charger/npm13xx_charger.c`, bindings `nordic,npm13xx-common.yaml`, `nordic,npm13xx-charger-common.yaml`, `nordic,npm13xx-regulator-common.yaml`, `include/zephyr/dt-bindings/regulator/npm13xx.h` (fetched 2026-11-10 for F4; the chip-specific charger binding read then was that of the older chip, see the change list F4 to F5) |"),
("| DS | Infineon IM73D122V01 datasheet 1.00 (tables 5, 6, 8) |",
 "| DS | Knowles SPK0641HT4H-1 datasheet Rev A, third-party copy, text `design/mech/mic-path/datasheets/knowles-spk0641ht4h-1_chipsmall.txt` (read 2026-11-11) |\n"
 "| NPM | Nordic nPM1304 Product Specification v1.0, 173 pages, `design/datasheets/npm1304_datasheet_v1_0.txt` (read 2026-11-11: pages 8 to 11, 17 to 30, 36, 37, 40, 41, 69, 77, 99, 107 to 109, 116 to 120, 136, 144 to 146) |\n"
 "| SRC 17 | `design/parts/research-npm1304.md` section 1, source [Z]: Nordic's nRF Connect SDK binding page `nordic,npm1304-charger` (processed text, not a raw copy): `current-microamp` 4 to 100 mA in 0.5 mA steps, `term-microvolt` 3.6 to 3.65 V and 4.0 to 4.65 V in 50 mV steps, `term-current-percent` default 10 |"),
("| DOC | `design/architecture.md` A5-draft (sections 2, 7, 9, 14, 16.4 to 16.6, 17.3 to 17.8; read 2026-11-10), `design/case/case-architecture.md` C1 (sections 1, 5, 6), `design/ecad/ring/sch-notes.md` (sections 2, 7, 8, 9) |",
 "| DOC | `design/architecture.md` A5-draft (sections 2, 7, 9, 14, 16.4 to 16.6, 17.3 to 17.8 read 2026-11-10; 17.10 to 17.23 read 2026-11-11), `design/case/case-architecture.md` C1 (sections 1, 5, 6), `design/ecad/ring/sch-notes.md` (sections 2, 7, 8, 9; section 12 read 2026-11-11), `design/ecad/ring/netlist.csv` and `parts.csv` (2026-11-11), `design/ecad/motor-drive/motor-drive.md` section 2, `design/mfg/assembly/assembly.md`, `design/mech/mic-path/mic-path.md` sections 3 and 9 (2026-11-11) |"),
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
