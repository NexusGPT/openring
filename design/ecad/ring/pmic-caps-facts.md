# nPM1304 external capacitors: the maker's words against the ring's circuit

Read at ROOT commit 84a44c03 (branch master). ROOT = `.`.

Sources and method:
- Maker: `design/datasheets/npm1304_datasheet_v1_0.txt` (15,227 lines). Line numbers are from `grep -n`. Page numbers are the printed page, taken from the last `--- page N` marker before the line (`pmic-caps-work/numbered-with-page.txt`).
- "picture" means the value was read from the PDF page image (`design/datasheets/npm1304_datasheet_v1_0.pdf`, pages 157 and 158), because the text dump does not give the connection. Figure 57 is config 1 CSP (page 157), Figure 59 is config 2 CSP (page 158).
- Murata DC-bias values are read by eye from the graphs in the PDF page images (no table in the text). They are approximate, about ±0.3 µF or ±5 percentage points.
- Ring values: `netlist.csv` (net, reference, pin) and `parts.csv` (value, maker part, footprint, sheet). Distances are centre to centre in mm from `pcb/placement-final.csv` (x_mm, y_mm, taken as the part centre), computed by `pmic-caps-work/dist.py` (`pmic-caps-work/distances-python.log`). A first awk pass gave wrong distances; it is saved as `pmic-caps-work/distances.log` and is not used.
- Every quote and line number here is checked by `pmic-caps-work/verify_quotes.py` (log `pmic-caps-work/verify-quotes.log`).

## 0. The datasheet's three configurations (Table 36, page 156)

| Config | BUCKs | LOADSWs | Lines (datasheet .txt) |
|---|---|---|---|
| 1 "Full configuration" | "Both configured" (13660) | "Both configured, LDO" (13664) / "mode" (13665) | 13652, 13656 |
| 2 "Simple configuration" | "One configured" (13661) | "One configured, load" (13666) / "switch mode" (13667) | 13653, 13657 |
| 3 "Minimal configuration" | "Not used" (13662) | "Not used" (13668) | 13654, 13658 |

Sources for the mode words: "Table 36: PCB application configuration" is at line 13717, page 156. The ring's VDD_MIC and VDD_SD outputs are LOADSW outputs; `sch-notes.md` does not say which mode they run in (grep for switch, LDO, regulator, LOADSW, load switch: no statement). `make_netlist.py:288` says "load switch mode outputs". `npm1304-reference.md:26` says "used as switches".

## 1. Pin groups

Ten pin groups. Each has the datasheet statement or the BOM row, then what the ring has. "Nominal" is the value printed in the BOM; the text gives no effective value for any group except the buck output (Table 18).

### G1. VBUS (balls B1, B2)

| Datasheet item | Words or value | Page, line |
|---|---|---|
| Text | No capacitor rule for VBUS in the text. The only capacitor hits in the text are listed in `pmic-caps-work/grep-capacitor.log`. | - |
| BOM config 1 | "C1" (14044), "1.0 μF" (14045), "Capacitor, X5R, 25 V, ±10%" (14046), "0603" (14047) | p157, Table 37 |
| BOM config 2 | "C1" (14364), "1.0 μF" (14365), "Capacitor, X5R, 25 V, ±10%" (14366) | p159, Table 38 |
| BOM config 3 | "C1" (14621), "1.0 μF" (14622), "Capacitor, X5R, 25 V, ±10%" (14623) | p160, Table 39 |
| Picture | C1 1.0 µF drawn on the VBUS(IN) pins, Figure 57 and Figure 59 | p157, p158 |
| Nominal or effective | Nominal only (the BOM value). Effective: not stated. | - |
| Min, max, voltage | Voltage 25 V in all three BOMs. Min and max: not stated. | - |
| Placement | "bypass capacitors must be connected as close as possible to the device." (14659) | p160 |
| Mode difference | None in the text: the same C1 in configs 1 to 3. | - |

Ring today:
- C71: 1.0 µF, 25 V, part GRM155R61E105KA12D, footprint Chip_0402, sheet power, 2.854 mm from U2 (netlist line 296, parts.csv line 28).
- C72: 100 nF, part CL03A104KP3NNNC, footprint Chip_0201, sheet power, 2.844 mm from U2 (netlist line 297, parts.csv line 33).
- No other capacitor on VBUS (netlist lines 296 to 302).
- Murata GRM155R61E105KA12 (`w1b_murata_grm155r61e105ka12.txt`): "静電容量 1.0μF ±10%" (line 82), "定格電圧 25Vdc" (line 90). DC bias picture (PDF page 3): about -60 % at 5 V, about -80 % at 10 V, about -93 % at 25 V.
- CL03A104KP3NNNC is not a Murata part and no document for it is in the brief's list; voltage not stated in any document read.

### G2. VBUSOUT (ball C3)

| Datasheet item | Words or value | Page, line |
|---|---|---|
| Text | "VBUSOUT must have a decoupling capacitor. The capacitor is discharged by RPDVBUSOUT once VBUS has" | p16, line 810 |
| BOM config 1 | "C5" (14048), "1.0 μF" (14049), "Capacitor, X5R, 10 V, ±10%" (14050), "0603" (14051) | p157 |
| BOM config 2 | "C5, C14" (14368), "1.0 μF" (14369), "Capacitor, X5R, 10 V, ±10%" (14370) | p159 |
| BOM config 3 | "C5" (14625), "1.0 μF" (14626), "Capacitor, X5R, 10 V, ±10%" (14627) | p160 |
| Picture | C5 drawn at VBUSOUT, Figure 57 and Figure 59 | p157, p158 |
| Nominal or effective | Nominal only. | - |
| Min, max | Not stated. Voltage 10 V (BOM). | - |
| Placement | generic: 14659 | p160 |

Ring today:
- C73: 1.0 µF, part GRM033R60J105MEA2D, footprint Chip_0201, sheet power, 4.904 mm (netlist line 305, parts.csv line 34).
- Voltage rating: not stated in any document read. The file `design/datasheets/motor_murata_GRM033R60J105MEA2.pdf` is an HTML "Not Found" page, not a datasheet (`pmic-caps-work/motor_033_head.log`).

### G3. VSYS (balls C1, C2) and PVDD (ball C7)

| Datasheet item | Words or value | Page, line |
|---|---|---|
| Text | "VBUS supplies VSYS. When VBUS is disconnected, VSYS is supplied by its decoupling capacitors until it is" | p27, line 1636 |
| Text | "VSYS must not be supplied from an external source." | p27, line 1646 |
| BOM config 1 | "C2, C3, C4, C7, C8," (14052), "C9, C10, C11, C12" (14053), "10 μF" (14054), "Capacitor, X5R, 16 V, ±20%" (14055), "0603" (14056) | p157 |
| BOM config 2 | "C2, C4, C7" (14372), "10 μF" (14373), "Capacitor, X5R, 16 V, ±20%" (14374) | p159 |
| BOM config 3 | "C4" (14629), "10 μF" (14630), "Capacitor, X5R, 10 V, ±20%" (14631) | p160 |
| Picture | Figure 57 draws C2, C3, C4 (10 µF) on the VSYS and PVDD node. The text gives no ball for each. | p157 |
| Nominal or effective | Nominal only. | - |
| Min, max | Not stated. Voltage 16 V (configs 1 and 2), 10 V (config 3). | - |
| Mode difference | Config 1 lists C2, C3, C4 here; config 2 lists C2, C4; config 3 lists C4 (BOM rows above). | - |

Ring today (all on net VSYS):
- C74: 10 µF, part GRM155R60J106ME15D, Chip_0402, sheet power, 2.210 mm (netlist line 365, parts.csv line 35).
- C75: 10 µF, part GRM155R60J106ME15D, Chip_0402, sheet power, 1.994 mm (netlist line 366, parts.csv line 36).
- C76: 1.0 nF, no part number, Chip_0201, sheet power, 3.338 mm (netlist line 367, parts.csv line 37).
- C77: 1.0 nF, no part number, Chip_0201, sheet power, 3.712 mm (netlist line 368, parts.csv line 38).
- C88: 10 µF, part GRT188R61A106KE13D, Chip_0603, sheet power, 2.804 mm (netlist line 369, parts.csv line 30).
- Pin 2 of C74, C75, C76, C77 and C88 is on GND (netlist lines 71, 72, 73, 74, 85).
- Murata GRM155R60J106ME15 (`w1d_murata_grm155r60j106me15.txt`): "静電容量 10µF ±20%" (line 49), "定格電圧 6.3Vdc" (line 52). DC bias picture (PDF page 2): about 10 µF at 0 V, about 6 µF at 2 V, about 4 µF at 3 V, about 3 µF at 4 V, about 2 µF at 6 V, about 1.7 µF at 6.3 V.
- Murata GRT188R61A106KE13 (`w1c_murata_grt188r61a106ke13.txt`): "Capacitance 10μF ±10%" (line 79), "Rated Voltage 10Vdc" (line 91). DC bias picture (PDF page 3): about 0 % at 0 V, about -30 % at 2 V, about -60 % at 4 V, about -78 % at 6 V, about -90 % at 10 V.
- Ring comment `make_netlist.py:286` and `sch-notes.md:215` both say "X5R 16 V" for C88. The part's document says 10 Vdc (line 91).
- Sum of nominal values on VSYS: 30.002 µF (3 × 10 µF plus 2 × 1.0 nF).

### G4. VBAT (balls D1, D2)

| Datasheet item | Words or value | Page, line |
|---|---|---|
| Text | No capacitor rule for VBAT in the text. | - |
| BOM config 1 | "C6" (14057), "2.2 μF" (14058), "Capacitor, X5R, 10 V, ±10%" (14059), "0603" (14060) | p157 |
| BOM config 2 | "C6" (14376), "2.2 μF" (14377), "Capacitor, X5R, 10 V, ±10%" (14378) | p159 |
| BOM config 3 | "C6" (14633), "2.2 μF" (14634), "Capacitor, X5R, 10 V, ±10%" (14635) | p160 |
| Picture | C6 drawn on the VBAT line, Figure 57 and Figure 59 | p157, p158 |
| Nominal or effective | Nominal only. | - |
| Min, max | Not stated. Voltage 10 V (BOM). | - |
| Placement | generic: 14659 | p160 |

Ring today:
- C85: 2.2 µF, part 0402ZC225KAT2A, Chip_0402, sheet power, 2.130 mm (netlist line 290, parts.csv line 29). The voltage rating is not in any document read here: the Kyocera/AVX files on disk (`w13_kyocera_6293.pdf`, `w13_kyocera_6844.pdf`) have no hit for this code, 2.2 µF or a rated voltage (`pmic-caps-work/w13-kyocera-grep-all.log`: 0 hits). `sch-notes.md:214` says "X5R 10 V" for it; that is the ring's own note.
- C21: 4.7 µF, part GRM155R61A475MEAAD, Chip_0402, sheet screen, 4.986 mm (netlist line 288, parts.csv line 70). `sch-notes.md:214` says "C21 stays for U4".
- C83: 10 µF, part GRM155R60J106ME15, Chip_0402, sheet controls, 10.097 mm (netlist line 289, parts.csv line 91).
- Murata GRM155R61A475MEAA (`w1d_murata_grm155r61a475meaa.txt`): "静電容量 4.7µF ±20%" (line 52), "定格電圧 10Vdc" (line 55). DC bias picture (PDF page 2): about 4.6 µF at 0 V, about 2.6 µF at 4 V, about 1.7 µF at 6 V, about 0.95 µF at 10 V.

### G5. Buck outputs VOUT1 (ball B6) and VOUT2 (ball C6), with the inductor side SW1 (B7) and SW2 (D7)

| Datasheet item | Words or value | Page, line |
|---|---|---|
| Text | "Recommended values for the inductor are shown in the following table." | p44, line 3143 |
| Table 17, inductor | "Nominal inductance" (3147), "2.2" (3148), "μH" (3149); "Inductor tolerance" (3150), "≤ 20" (3151), "%" (3152); "DC resistance (DCR)" (3153), "≤ 400" (3154), "mΩ" (3155); "Saturation current (Isat)" (3156), "> 350" (3157), "mA" (3158); "Rated current (Imax)" (3159), "> 200" (3160) | p44 |
| Table 18, output capacitor | "Effective capacitance" (3172), "≥ 4" (3173), "μF" (3174); "ESR" (3175), "≤ 50" (3176), "mΩ" (3177); "Table 18: Recommended capacitor specifications" (3178) | p45 |
| Test condition | "C = 10 µF" (3242), with "VOUT = 3.3 V" (3241) for the start-up time tSTRT | p45 |
| BOM config 1 | "C2, C3, C4, C7, C8," (14052) and "C9, C10, C11, C12" (14053), 10 µF, 16 V (14054 to 14056) | p157 |
| BOM config 2 | "C2, C4, C7" (14372), 10 µF, 16 V (14373 to 14374) | p159 |
| BOM config 3 | none (BUCKs not used) | p156 |
| Placement | "The BUCK supply voltage should be decoupled with high performance capacitors as close as possible to" (14656) / "the supply pins." (14657) | p160 |

Words: Table 18 is the only figure in the text that is an effective (derated) value. The text does not say which pin each capacitor sits on. The inductor side (SW1, SW2 to the coil): no capacitor is named in the text. Picture: C7 on VOUT1 and C8 on VOUT2, Figure 57.

Nominal or effective: effective ≥ 4 µF (Table 18); nominal 10 µF (BOM). Voltage: 16 V (BOM). Min and max beyond "≥ 4" are not stated.

Ring today:
- VOUT1 net VDD_1V8: C78, 10 µF, part GRM155R60J106ME15D, Chip_0402, sheet power, 4.736 mm (netlist line 311, parts.csv line 40). Also C4, 10 µF, sheet main, 6.378 mm, which the ring's own note says serves U1 (`sch-notes.md:30`).
- VOUT2 net VDD_3V0: C79, 10 µF, part GRM155R60J106ME15D, Chip_0402, sheet power, 5.523 mm (netlist line 329, parts.csv line 42). It is the only capacitor on that net.
- SW1 (ball B7): L71 pin 1 only (netlist line 263). No capacitor on the SW1 net.
- SW2 (ball D7): L72 pin 1 only (netlist line 265). No capacitor on the SW2 net.
- Coil placement from U2 centre (placement-final.csv): L71 5.143 mm, L72 3.768 mm. Coil pin 2 is on VDD_1V8 (netlist line 316) and VDD_3V0 (line 332).
- Coil parts: 2.2 µH 1269AS-H-2R2M=P2, 2.5 × 2.0 mm (parts.csv lines 39, 41). The coil's DCR is not read here (the ring's own note at `design/wiring/lead-decisions.md` line 24 says 156 mΩ max; the Murata coil document was not in this task).
- Murata GRM155R60J106ME15 DC bias (PDF page 2): about 4 µF at 3.0 V. At 1.8 V the picture gives about 6.5 µF (read between the 0 V and 2 V points, by eye).

### G6. Load switches and LDO: inputs LSIN1 (ball B4) and LSIN2 (ball B5), outputs LSOUT1 (ball A4) and LSOUT2 (ball A5)

| Datasheet item | Words or value | Page, line |
|---|---|---|
| Text | "Two load switches are available for use as switches or LDO regulators (LDO). They have dedicated input" (4648), "pins where voltage cannot exceed VSYS." (4649) | p67 |
| Text, load switch mode | "Soft start is enabled by default. This ensures that the current to LSOUT[n] is limited for tSS. Once soft" (4678, 4679); "Current limiting is only" (4679), "available from the power source connected to LSIN[n]." (4680) | p68 |
| Text, LDO mode (build B00) | "This information is valid for Build code B00 and later:" (4691); "The LDO can be supplied from VOUT1, VOUT2 or VSYS, but must comply with VINLDO." (4694); "The LDO should always be used with soft start enabled. This can be configured via register settings:" (4695) | p68 |
| Table 20 | "Soft start current limit = 25 mA, 10 µF, 0 V" (4728) with "to 5 V" (4729), "tSS" (4726), "Soft start time" (4727), "1.8" "ms" (4730-4731). "Input voltage range" (4738): "1.0" (4739) to "VSYS" (4740). | p69 |
| Capacitor rule in 6.4 | None in the text of 6.4 (lines 4647 to 4760 contain no "capacitor" word; `grep-capacitor.log`). | - |
| BOM config 1 (LDO mode) | "C9, C10, C11, C12" (14053), "10 μF" (14054), "Capacitor, X5R, 16 V, ±20%" (14055), "0603" (14056). Picture: C9 and C10 on VOUTLDO1, C11 and C12 on VOUTLDO2. | p157 |
| BOM config 2 (load switch mode) | "C5, C14" (14368), "1.0 μF" (14369), "Capacitor, X5R, 10 V, ±10%" (14370). Picture: C14 on LSOUT1 only. | p158 (picture), p159 (BOM) |
| BOM config 3 | none | p160 |
| Nominal or effective | Nominal only. | - |
| Placement | generic: 14659 | p160 |

Ring today:
- LSOUT1 (VDD_MIC, ball A4): C31 1 µF, GRM033R60J105MEA2D, Chip_0201, sheet mics, 18.014 mm (netlist line 335, parts.csv line 52); C32 1 µF, same part, Chip_0201, sheet mics, 2.802 mm (line 336, parts.csv line 56); C35 1 nF C0G, 04025A102JAT2A, Chip_0402, sheet mics, 17.584 mm (line 337); C36 1 nF C0G, same, Chip_0402, sheet mics, 3.409 mm (line 338); C86 1.0 µF, GRM155R61E105KA12D, Chip_0402, sheet power, 6.227 mm (line 339, parts.csv line 31). Sum of nominal values 3.002 µF. No 10 µF.
- LSOUT2 (VDD_SD, ball A5): C60 2.2 µF, 0402ZC225KAT2A, Chip_0402, sheet storage, 15.063 mm (netlist line 344, parts.csv line 66); C61 100 nF, CL03A104KP3NNNC, Chip_0201, sheet storage, 16.226 mm (line 345); C82 100 nF, CL03A104KP3NNNC, Chip_0201, sheet storage, 8.281 mm (line 346); C87 1.0 µF, GRM155R61E105KA12D, Chip_0402, sheet power, 5.708 mm (line 347, parts.csv line 32). Sum 3.4 µF. No 10 µF.
- Ring note on the mode: `make_netlist.py:288` "load switch mode outputs: Nordic configuration 2 (one LOADSW in load switch mode) puts C14 1.0 uF on LSOUT1". `sch-notes.md:216`: "Applied to both outputs: C86 on VDD_MIC at ball A4, C87 on VDD_SD at ball A5".
- Murata GRM155R61E105KA12 (C86 and C87 part): rated 25 Vdc (`w1b_murata_grm155r61e105ka12.txt` line 90). Its DC bias is in G1.

### G7. VDDIO (ball E4)

| Datasheet item | Words or value | Page, line |
|---|---|---|
| Text | No capacitor rule for VDDIO in the text. | - |
| BOM config 1 | "C13" (14061), "100 nF" (14062), "Capacitor, X5R" (14063), "0201" (14064) | p157 |
| BOM config 2 | "C13" (14380), "100 nF" (14381), "Capacitor, X5R" (14382), "0201" (14383) | p159 |
| BOM config 3 | "C13" (14637), "100 nF" (14638), "Capacitor, X5R" (14639), "0201" (14640) | p160 |
| Pin description | "Supply for TWI and GPIOs" (13536) | p153 |
| Table 36 | "VDDIO" (13713), "Configured" (13714 to 13716) in all three configs | p156 |
| Nominal or effective | Nominal only. Voltage not stated. | - |

Ring today: VDDIO is on net VDD_1V8 (netlist line 328). Capacitors on that net:
- C80: 100 nF, CL03A104KP3NNNC, Chip_0201, sheet power, 5.604 mm (netlist line 312, parts.csv line 43).
- C1: 100 nF, CL03A104KP3NNNC, Chip_0201, sheet main, 2.514 mm (line 307). C2: 100 nF, same, sheet main, 1.945 mm (line 308). C5: 100 nF, same, sheet main, 7.272 mm (line 310). Per `sch-notes.md:30`, C1, C2, C5 serve U1.
- C81: 100 nF, same code, sheet storage, 8.043 mm (line 313).
- C4 (10 µF, sheet main, 6.378 mm) and C78 (10 µF, sheet power, 4.736 mm) are also on this net (lines 309, 311).
- No capacitor is on the VDDIO ball alone; all share VDD_1V8. No document for CL03A104KP3NNNC was read.

### G8. NTC (ball D3)

| Datasheet item | Words or value | Page, line |
|---|---|---|
| Text | "Note:  If a capacitor is placed in parallel with the thermistor, the max capacitance is 100 pF." | p24, line 1466 |
| Table (electrical) | "Capacitance in parallel with the thermistor" (7517), "0" (7518), "100" (7519), "pF" (7520) | p100 |

Ring today: NTC net has U2 D3 (netlist line 200), RT1 pin 1 (line 199), J_BAND_B pin 3 (line 198). No capacitor on the NTC net.

### G9. Grounds AVSS (ball A6), PVSS1 (ball A7), PVSS2 (ball E7)

| Datasheet item | Words or value | Page, line |
|---|---|---|
| Figure 57 text | "Via to GND-layer on PVSS1" (13961), "Via to GND-layer on PVSS2" (13962), "Net tie" (13963, 13964) | p157 |
| Figure 59 text | "Via to GND-layer on PVSS1" (14275), "Net tie" (14276) | p158 |
| Text | "A PCB with a minimum of two layers, including a ground plane, is recommended for optimal performance." (14655) | p160 |

Ring today: AVSS (A6) on GND (netlist line 126), PVSS1 (A7) on GND (line 127), PVSS2 (E7) on GND (line 128). The netlist has no via or net-tie entry. The PCB via list was not read (the `pcb` folder is for other agents; `placement-final.csv` was read for part positions only).

### G10. Other pins with no capacitor rule

GPIO0 to GPIO3, SCL, SDA, VSET1, VSET2, SHPHLD, LED0 to LED2, CC1, CC2: the datasheet text and BOM name no capacitor for these pins. The figure text names "Optional TWI pull-up resistors" (R1, R2), which are resistors. Ring: VSET1 (netlist 361 to 362) and VSET2 (363 to 364) have only the R71 and R72 resistors. Not stated for the others.

## 2. Requirements D2 to D7 (`npm1304-reference.md`, rows D2 to D7)

Each row: maker's requirement (quote and line), ring today, difference in numbers.

**D2. VBAT capacitor**
- Maker: BOM "C6" "2.2 μF" "Capacitor, X5R, 10 V, ±10%" (14057 to 14059, page 157). Picture: C6 on VBAT (Figures 57 and 59). Reference row says "C6 2.2 uF, 10 V, at the VBAT balls" (`npm1304-reference.md:24`).
- Ring: C85 2.2 µF (0402ZC225KAT2A, 2.130 mm, sheet power); C21 4.7 µF (4.986 mm, sheet screen); C83 10 µF (10.097 mm, sheet controls).
- Difference: C85 is 2.2 µF, the same nominal value as C6; its voltage rating is not stated in any document read (C6 is 10 V). C21 (4.7 µF) and C83 (10 µF) are extra capacitors on VBAT.

**D3. VSYS and PVDD capacitors**
- Maker: BOM "C2, C3, C4, C7, C8, C9, C10, C11, C12" "10 μF" "Capacitor, X5R, 16 V, ±20%" (14052 to 14056, page 157). Picture: C2, C3, C4 on the VSYS and PVDD node (Figure 57). Reference row: "three of 10 uF, 16 V, at balls C1, C2 and C7; two of them return to PVSS1 and PVSS2 as drawn" (`npm1304-reference.md:25`). The text gives no ball numbers for the three capacitors.
- Ring: three 10 µF on VSYS: C74 (6.3 V part, `w1d` line 52), C75 (6.3 V part), C88 (10 V part, `w1c` line 91). Plus C76 and C77, 1.0 nF each, with no part number. The reference row's "Add a third 10 uF" no longer applies: C88 is in the netlist (line 369) and `sch-notes.md:215` lists it.
- Difference: count 3 against 3 (met). Rating 16 V (maker) against 6.3 V (C74, C75) and 10 V (C88). Two 1.0 nF capacitors (C76, C77) are not in the maker's list. The return to PVSS1 and PVSS2: the maker's figure shows net ties and vias (13961 to 13964); the netlist puts all VSYS capacitors on GND and has no separate return (netlist lines 365 to 369 and 126 to 128).

**D4. Load-switch or regulator outputs (C9 to C12 and config 2)**
- Maker, config 1 (LDO mode): "C9, C10, C11, C12" "10 μF" "Capacitor, X5R, 16 V, ±20%" (14053 to 14056, page 157); picture: C9 and C10 on VOUTLDO1, C11 and C12 on VOUTLDO2. Maker, config 2 (load switch mode): "C5, C14" "1.0 μF" "Capacitor, X5R, 10 V, ±10%" (14368 to 14370, page 159); picture: C14 on LSOUT1 only (Figure 59, page 158). Text: "The LDO should always be used with soft start enabled." (4695, page 68).
- Ring: LSOUT1 (VDD_MIC) has no 10 µF; it has C86 1.0 µF (25 V) and C31, C32 (1 µF), C35, C36 (1 nF). LSOUT2 (VDD_SD) has no 10 µF; it has C60 2.2 µF, C61 and C82 (100 nF), C87 1.0 µF (25 V).
- Difference in numbers: 10 µF on LSOUT1: maker 2 (config 1), ring 0. 10 µF on LSOUT2: maker 2 (config 1), ring 0. Config 2 value: 1.0 µF on LSOUT1 in both; rating 10 V (maker) against 25 V (C86, `w1b` line 90). Config 2 draws nothing on LSOUT2 (picture); ring has four capacitors on LSOUT2 (C60, C61, C82, C87).
- Mode: the ring files say "load switch mode outputs" (`make_netlist.py:288`) and "used as switches" (`npm1304-reference.md:26`). `sch-notes.md` does not state the mode.

**D5. GPIO4**
- Maker: Table 33 (page 153) lists GPIO0 (13514), GPIO1 (13542), GPIO2 (13486) and GPIO3 (13482). It has no GPIO4 line (`pmic-caps-work/gpio4-table33.log`: 0 hits). Figure 56 (QFN, page 156) shows GPIO4 (13752, 13824).
- Ring: no GPIO4 in `netlist.csv` or `npm1304-balls.csv` (`pmic-caps-work/gpio4-ring.log`: no hits).
- Difference: 0. Not a capacitor row.

**D6. Ground of the two bucks (PVSS1 and PVSS2)**
- Maker: "Via to GND-layer on PVSS1" (13961), "Via to GND-layer on PVSS2" (13962), "Net tie" (13963, 13964), page 157; the same on Figure 59 (14275, 14276), page 158.
- Ring: A7 (PVSS1) and E7 (PVSS2) on GND (netlist lines 127, 128). No via or net tie in the netlist.
- Difference: not verifiable from the files read (PCB vias not read).

**D7. Capacitor size**
- Maker: the 1.0 µF, 2.2 µF and 10 µF capacitors are 0603 (for example 14047, 14056, 14060). C13 is 0201 in all three BOMs (14064, 14383, 14640). The reference row says "Nordic lists 0603 for every capacitor" (`npm1304-reference.md:29`): this is not what the tables say, because C13 is 0201.
- Ring sizes (parts.csv footprint): 0603 only C88. 0402: C4, C21, C35, C36, C60, C71, C74, C75, C78, C79, C83, C85, C86, C87. 0201: C1, C2, C5, C31, C32, C61, C72, C73, C76, C77, C80, C81, C82.
- Difference: ring 10 µF parts are 0402 (C4, C74, C75, C78, C79, C83) and 0603 (C88); maker 0603. Murata DC bias (picture): the 6.3 V 10 µF part reads about 4 µF at 3.0 V and about 2.5 µF to 3 µF at 4.35 V (interpolated by eye between 3 V and 4 V, and 4 V and 6 V). The 10 V 10 µF part (C88) reads about 4 µF at 4 V.

## 3. What I could not find

- Voltage rating of the Kyocera/AVX 2.2 µF part 0402ZC225KAT2A (C85, C60): not in the two Kyocera files searched (`w13-kyocera-grep-all.log`: 0 hits); no other document searched. Not stated.
- Voltage rating and DC bias of GRM033R60J105MEA2D (C73, C31, C32): the file on disk is a 404 page (`motor_033_head.log`). Not stated.
- Rating and DC bias of CL03A104KP3NNNC (100 nF, C1, C2, C5, C61, C72, C80, C81, C82): no document read. Not stated.
- Rating and value of C76 and C77 (1.0 nF, no part number): not stated in any document.
- Min, max and effective values for every pin group except the buck output (Table 18): not stated in the text.
- Which ball each VSYS and LSOUT capacitor sits on, from the text: not stated. Only the picture shows the position.
- A capacitor rule for the load-switch mode (6.4, pages 67 to 69): not stated. Only Table 20 uses 10 µF as a test condition.
- The mode (switch or LDO) of the ring's VDD_MIC and VDD_SD outputs: not stated in `sch-notes.md`.
- The PCB via list (for D6): not read.
- The coil's DCR against the 400 mΩ limit: the coil document was not read in this task.
- Murata DC-bias readings are by eye from the graphs (±0.3 µF or ±5 percentage points). Not a table value.
- Document `design/datasheets/w1c_murata_grt188r61a106ke13.pdf` is not in the brief's list; read because C88 is on VSYS.

## 4. Mismatches in the repo files (found while checking)

- `npm1304-reference.md:23` says C71 is 4.7 µF, GRM155R60J475ME47D. `parts.csv:28` and `design/wiring/lead-decisions.md:24` say 1.0 µF, 25 V, GRM155R61E105KA12D. The ring now has 1.0 µF, 25 V (D1 done).
- `npm1304-reference.md:25` says "Add a third 10 uF". C88 is already on VSYS (netlist line 369).
- `npm1304-reference.md:29` says "Nordic lists 0603 for every capacitor". C13 is 0201 (14064).
- `make_netlist.py:286` and `sch-notes.md:215` say C88 is "X5R 16 V". The part's document says 10 Vdc (`w1c` line 91).
- `npm1304-reference.md:26` says the outputs are used as switches. `sch-notes.md` does not say so.

RESULT: done, 10 pin groups covered; of the six rows D2 to D7, 3 are not met (D3 rating, D4 10 µF count and rating, D7 size), D5 is met, and 2 cannot be checked from the files (D2 rating, D6 vias).
