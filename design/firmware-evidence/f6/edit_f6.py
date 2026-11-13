"""F6: the measured cells of architecture 17.26 replace the calculated cells of 17.17."""
import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()

charge_old = """| Ring size | Battery (architecture 17.17) | Charge time at 15 mA from empty [CALC] |
|---|---|---|
| US 7 | 18.2 to 24.3 mAh | 1.21 to 1.62 hours |
| US 8 | 19.3 to 25.7 mAh | 1.29 to 1.71 hours |
| US 9 | 20.4 to 27.2 mAh | 1.36 to 1.81 hours |
| US 10 | 21.5 to 28.6 mAh | 1.43 to 1.91 hours |
| US 11 | 22.6 to 30.1 mAh | 1.51 to 2.01 hours |
| US 12 | 23.6 to 31.5 mAh | 1.57 to 2.10 hours |
| US 13 | 24.7 to 32.9 mAh | 1.65 to 2.19 hours |"""
charge_new = """| Ring size | Battery (architecture 17.26, measured) | Charge time at 15 mA from empty [CALC] |
|---|---|---|
| US 7 | 17.6 to 23.5 mAh | 1.17 to 1.57 hours |
| US 8 | 18.9 to 25.3 mAh | 1.26 to 1.69 hours |
| US 9 | 20.3 to 27.1 mAh | 1.35 to 1.81 hours |
| US 10 | 21.2 to 28.3 mAh | 1.41 to 1.89 hours |
| US 11 | 22.1 to 29.5 mAh | 1.47 to 1.97 hours |
| US 12 | 23.0 to 30.7 mAh | 1.53 to 2.05 hours |
| US 13 | 23.9 to 31.9 mAh | 1.59 to 2.13 hours |"""
rec_old = """| Ring size | Battery (architecture 17.17) | Recording hours at 4.1 mA |
|---|---|---|
| US 7 | 18.2 to 24.3 mAh | 4.44 to 5.93 |
| US 8 | 19.3 to 25.7 mAh | 4.71 to 6.27 |
| US 9 | 20.4 to 27.2 mAh | 4.98 to 6.63 |
| US 10 | 21.5 to 28.6 mAh | 5.24 to 6.98 |
| US 11 | 22.6 to 30.1 mAh | 5.51 to 7.34 |
| US 12 | 23.6 to 31.5 mAh | 5.76 to 7.68 |
| US 13 | 24.7 to 32.9 mAh | 6.02 to 8.02 |

Architecture 17.17 gives these hours at 4.0 mA (4.5 to 8.2 across the sizes); the difference is hardware issue H18."""
rec_new = """| Ring size | Battery (architecture 17.26, measured) | Recording hours at 4.1 mA |
|---|---|---|
| US 7 | 17.6 to 23.5 mAh | 4.29 to 5.73 |
| US 8 | 18.9 to 25.3 mAh | 4.61 to 6.17 |
| US 9 | 20.3 to 27.1 mAh | 4.95 to 6.61 |
| US 10 | 21.2 to 28.3 mAh | 5.17 to 6.90 |
| US 11 | 22.1 to 29.5 mAh | 5.39 to 7.20 |
| US 12 | 23.0 to 30.7 mAh | 5.61 to 7.49 |
| US 13 | 23.9 to 31.9 mAh | 5.83 to 7.78 |

Architecture 17.26 gives the same hours at 4.1 mA, rounded to one decimal (4.3 to 7.8 across the sizes)."""

reps = [
("Version F5, 2026-11-11. Follows `design/architecture.md` version A5-draft, sections 17.11 to 17.23 (read 2026-11-11: section 17 is the current ring; where sections disagree, the later section wins: 17.23 over 17.22 and so on down to 17.11,",
 "Version F6, 2026-11-11. Follows `design/architecture.md` version A5-draft, sections 17.11 to 17.26 (read 2026-11-11: section 17 is the current ring; where sections disagree, the later section wins: 17.26 over 17.25 and so on down to 17.11,"),
("Changes from F4 to F5 (2026-11-11;",
 "Changes from F5 to F6 (2026-11-11; architecture 17.26: the inside model v6 measured the cell at every ring size; 17.25 moves the joystick on US 7 and US 8 and changes nothing in these rules; the figures and their arithmetic are in `design/firmware-f6-notes.md`):\n"
 "1. **Measured cells** (17.26): US 7 17.6 to 23.5 mAh up to US 13 23.9 to 31.9 mAh replace the calculated cells of 17.17 (before: 18.2 to 32.9 mAh). The smallest cell is 17.6 mAh (sections 1.1, 3.1, 8.1, 8.5, 9.3, 10.5, H7, H8).\n"
 "2. **Thresholds on 17.6 mAh**: B15 39 min, B5 13 min, B2 5 min at 4.1 mA (before: 40, 13, 5 min on 18.2 mAh) (section 1.1).\n"
 "3. **Charge**: `CHARGE_CURRENT` stays 15,000 µA, 0.85 C of 17.6 mAh; the compile limit (1 C of the smallest cell) becomes 17,600 µA (before: 18,200); the charge time table follows the measured cells (section 8.1).\n"
 "4. **Hours**: recording 4.3 to 7.8 hours, standby 24.4 to 44.3 days, a Plaud's 13 mA 1.4 to 2.5 hours across US 7 to 13 (section 8.5). The motor's place per size follows 17.26 (sections 3.1, 4.7). H18 closes: 17.26 computes the hours at 4.1 mA.\n"
 "No behaviour changes: states, transitions, gestures, patterns and rules are those of F5.\n\n"
 "Changes from F4 to F5 (2026-11-11;"),
("Recomputed in F5 for the cells of ring sizes US 7 to 13, 18.2 to 32.9 mAh (architecture 17.17), and a recording current of 4.1 mA (section 8.5). A threshold protects a minimum of recording time, so its minutes are given on the smallest cell, 18.2 mAh at US 7 (architecture 17.17: \"must use the smallest cell of the smallest size: 18.2 mAh (US 7)\"):",
 "Recomputed in F6 for the measured cells of ring sizes US 7 to 13, 17.6 to 31.9 mAh (architecture 17.26), and a recording current of 4.1 mA (section 8.5). A threshold protects a minimum of recording time, so its minutes are given on the smallest cell, 17.6 mAh at US 7 (architecture 17.26: \"Every rule that protects a minimum of recording time uses the smallest cell: **17.6 mAh (US 7)**\"):"),
("Capacity left on the smallest cell [CALC]: B15 2.73 mAh, B5 0.91 mAh, B2 0.36 mAh (18.2 mAh times 15, 5 and 2 %). Time left at 4.1 mA on 18.2 mAh [CALC]: B15 40 min, B5 13 min, B2 5 min. On the largest cell, 32.9 mAh at US 13, the same shares give B15 72 min, B5 24 min, B2 10 min [CALC]. Recording time from full at 4.1 mA: 4.4 to 8.0 hours across US 7 to 13 (section 8.5).",
 "Capacity left on the smallest cell [CALC]: B15 2.64 mAh, B5 0.88 mAh, B2 0.35 mAh (17.6 mAh times 15, 5 and 2 %). Time left at 4.1 mA on 17.6 mAh [CALC: 2.64 / 4.1 x 60 = 38.6, 0.88 / 4.1 x 60 = 12.9, 0.352 / 4.1 x 60 = 5.2]: B15 39 min, B5 13 min, B2 5 min. On the largest cell, 31.9 mAh at US 13, the same shares give B15 70 min, B5 23 min, B2 9 min [CALC: 4.785, 1.595 and 0.638 mAh / 4.1 x 60 = 70.0, 23.3 and 9.3]. Recording time from full at 4.1 mA: 4.3 to 7.8 hours across US 7 to 13 (section 8.5)."),
("in the joystick-side shoulder of the band at -44 degrees (architecture 17.15),",
 "in the joystick-side shoulder of the band at -47.0 degrees on US 7 to -39.5 degrees on US 13 (-44.0 at US 9; architecture 17.26),"),
("On the smallest cell, 18.2 mAh at US 7, that is 4.4 C running and 9.6 C at the start; on the largest, 32.9 mAh at US 13, 2.4 C and 5.3 C [CALC: 80 / 18.2, 175 / 18.2, 80 / 32.9, 175 / 32.9; architecture 17.16, 17.17];",
 "On the smallest cell, 17.6 mAh at US 7, that is 4.5 C running and 9.9 C at the start; on the largest, 31.9 mAh at US 13, 2.5 C and 5.5 C [CALC: 80 / 17.6 = 4.55, 175 / 17.6 = 9.94, 80 / 31.9 = 2.51, 175 / 31.9 = 5.49; architecture 17.16, 17.26];"),
("The motor sits in the joystick-side shoulder of the band (-44 degrees, architecture 17.15)",
 "The motor sits in the joystick-side shoulder of the band (-47.0 to -39.5 degrees by ring size, architecture 17.26)"),
("On the smallest cell, 18.2 mAh (US 7), 15 mA is 0.82 C; on the largest, 32.9 mAh (US 13), 0.46 C [CALC: 15 / 18.2, 15 / 32.9]. With the chip's accuracy of plus or minus 10 % [NPM p29] the current is 13.5 to 16.5 mA, at most 0.91 C on 18.2 mAh [CALC: 16.5 / 18.2]",
 "On the smallest cell, 17.6 mAh (US 7, architecture 17.26), 15 mA is 0.85 C; on the largest, 31.9 mAh (US 13), 0.47 C [CALC: 15 / 17.6 = 0.852, 15 / 31.9 = 0.470]. With the chip's accuracy of plus or minus 10 % [NPM p29] the current is 13.5 to 16.5 mA, at most 0.94 C on 17.6 mAh [CALC: 16.5 / 17.6 = 0.9375]"),
("above 18,200 (1 C of the smallest cell, 18.2 mAh, architecture 17.17),",
 "above 17,600 (1 C of the smallest cell, 17.6 mAh, architecture 17.26),"),
(charge_old, charge_new),
("### 8.5 Expected current per state (architecture 17.15, 17.17 and 17.19, the current ring)",
 "### 8.5 Expected current per state (architecture 17.15, 17.19 and 17.26, the current ring)"),
("| Hours on the smallest cell, 18.2 mAh at US 7 [CALC] | 4.4 | 607 (25.3 days) |\n| Hours across US 7 to 13, 18.2 to 32.9 mAh [CALC] | 4.4 to 8.0 | 607 to 1,097 (25.3 to 45.7 days) |\n| Hours at a Plaud's 13 mA, 18.2 to 32.9 mAh [CALC] | 1.4 to 2.5 | |",
 "| Hours on the smallest cell, 17.6 mAh at US 7 [CALC] | 4.3 | 587 (24.4 days) |\n| Hours across US 7 to 13, 17.6 to 31.9 mAh [CALC] | 4.3 to 7.8 | 587 to 1,063 (24.4 to 44.3 days) |\n| Hours at a Plaud's 13 mA, 17.6 to 31.9 mAh [CALC] | 1.4 to 2.5 | |"),
("Recording current: architecture 17.15 and 17.17 use 4.0 mA,", "Recording current: architecture 17.15 and 17.17 used 4.0 mA,"),
("Recording hours: 18.2 / 4.1 = 4.44 and 32.9 / 4.1 = 8.02. At 13 mA: 18.2 / 13 = 1.40 and 32.9 / 13 = 2.53. Standby at 0.03 mA: 18.2 / 0.03 = 607 hours = 25.3 days and 32.9 / 0.03 = 1,097 hours = 45.7 days. Per ring size at 4.1 mA [CALC, `design/firmware-f5-notes.md`]:",
 "Recording hours: 17.6 / 4.1 = 4.29 and 31.9 / 4.1 = 7.78. At 13 mA: 17.6 / 13 = 1.35 and 31.9 / 13 = 2.45. Standby at 0.03 mA: 17.6 / 0.03 = 587 hours = 24.4 days and 31.9 / 0.03 = 1,063 hours = 44.3 days. Per ring size at 4.1 mA [CALC, `design/firmware-f6-notes.md`]:"),
(rec_old, rec_new),
("From an empty cell that takes about 0.61 to 1.10 hours across US 7 to 13 [CALC: 0.5 x 18.2 / 15 and 0.5 x 32.9 / 15].",
 "From an empty cell that takes about 0.59 to 1.06 hours across US 7 to 13 [CALC: 0.5 x 17.6 / 15 = 0.587 and 0.5 x 31.9 / 15 = 1.063]."),
("26. The fuel-gauge battery model for the curved cells of 18.2 to 32.9 mAh,", "26. The fuel-gauge battery model for the curved cells of 17.6 to 31.9 mAh (architecture 17.26),"),
("`CHARGE_CURRENT` 15 mA, 0.82 C of the smallest cell, stays", "`CHARGE_CURRENT` 15 mA, 0.85 C of the smallest cell (17.6 mAh), stays"),
("4.4 C running and 9.6 C at the start on the smallest cell, 18.2 mAh, and 2.4 C and 5.3 C on the largest, 32.9 mAh [CALC, section 3.1].",
 "4.5 C running and 9.9 C at the start on the smallest cell, 17.6 mAh, and 2.5 C and 5.5 C on the largest, 31.9 mAh [CALC, section 3.1; architecture 17.26]."),
("| `CHARGE_CURRENT` = 15 mA, 0.82 C of the smallest cell; T-CHARGE passes", "| `CHARGE_CURRENT` = 15 mA, 0.85 C of the smallest cell (17.6 mAh); T-CHARGE passes"),
("| H18 | Architecture 17.15 and 17.17 give the recording hours at 4.0 mA (4.5 to 8.2 hours across US 7 to 13); with the microphones of 17.19 the current is 4.1 mA and the hours are 4.4 to 8.0 [CALC, section 8.5]. | open | F5 uses 4.1 mA | architecture owner: update 17.17 and the key numbers |",
 "| H18 | Architecture 17.15 and 17.17 gave the recording hours at 4.0 mA; with the microphones of 17.19 the current is 4.1 mA. | closed by architecture 17.26, which computes the hours at 4.1 mA on the measured cells (4.3 to 7.8 hours) | 4.1 mA (section 8.5) | none |"),
]
bad = 0
for a, b in reps:
    n = s.count(a)
    print(n, a[:70].replace("\n", " "))
    if n == 1:
        s = s.replace(a, b)
    else:
        bad += 1
open(p, "w", encoding="utf-8").write(s)
print("not applied:", bad)
