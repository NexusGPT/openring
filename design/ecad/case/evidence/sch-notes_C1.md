# Charging case schematic: notes

Contract: `design/case/case-architecture.md` version C1 (sections 2 to 6) and `design/case/case-bom.csv`. Designators are frozen in `bom_refs_snapshot.csv` (50 electrical designators from case-bom.csv as first read on 2026-11-10; ranges R14-R22, W1-W4, W5-W6 expanded; PCB1, PCB2, MECH1 to MECH7 are mechanical). `check_netlist.py` checks against the snapshot and only prints a difference to the live case-bom.csv.

Method and tools as in the ring (`design/ecad/ring/`): `make_netlist.py` writes `netlist.csv` (source of truth, 271 pin rows, 62 nets, 12 no-connect pins), `parts.csv` (85 parts), `symbols.csv`, `additions.csv`, `open-pins.csv`; `gen_sch.py` (copied from the ring, project name, sheets and power flag changed) writes `case.kicad_sym`, `case.kicad_sch` and 6 sub-sheets, `case.kicad_pro`, `sym-lib-table`; `check_netlist.py` is the check; `run_all.sh`, `prove_fail.sh`, `render_pdf.py` as in the ring. Footprint names sit in the field `Footprint_plan`.

Rebuild: `cd design/ecad/case && ../../.venv/bin/python make_netlist.py && bash run_all.sh <tag>`.

## 1. Block by block

**ESP32-S3 module, light, pull-ups (sheet 2).** U1 ESP32-S3-MINI-1-N8, all 65 pins from Table 3-1 of `case_esp32s3_mini1.pdf` p.11-12, wired as section 6 of the architecture: GND pins 1, 2, 42, 43, 46 to 65; 3V3 pin 3 with C9 10 uF and C10 100 nF; IO0 = BOOT with R22 10 kohm to 3V3 and test pad TP1; IO1/IO2 = CC1_SENSE/CC2_SENSE; IO4 = RING_TOUCH; IO5 = VRING_SENSE; IO6 = CHG_OTG; IO7 = CHG_INT_N (R16 10 kohm to 3V3); IO8/IO17 = I2C_SDA/I2C_SCL (R14, R15 10 kohm); IO9, IO10, IO11, IO12, IO13, IO14 = SD_D3, SD_D2, SD_CMD, SD_CLK, SD_D0, SD_D1; IO15 = VRING_EN (R25 100 kohm to GND); IO16 = VRING_FAULT_N (R17 10 kohm); IO18 = CHG_CE_N (R21 10 kohm to GND); IO19/IO20 = USB_D-/USB_D+; IO21, IO47, IO48 = LED_R, LED_G, LED_B through R8 470 ohm, R9 150 ohm, R10 150 ohm to the cathodes of LED1, whose common anode (pin 1) is on 3V3; IO33 to IO42 to test pads TP6 to TP15; TXD0/RXD0 to TP3/TP4; EN with R23 10 kohm to 3V3, C30 1 uF to GND and TP2; IO3, IO26, IO45, IO46 no-connect.

**Power (sheet 3).** U2 BQ25895 per Table 6-1 and Figure 9-1 of `case_bq25895.pdf`: VBUS (1) = VBUS_IN with C1 1 uF; D+/D- (2, 3) to the USB-C data pins; STAT (4) with R24 10 kohm to 3V3; SCL, SDA, INT, OTG, CE (5 to 9) to U1; ILIM (10) R11 260 ohm to GND; TS (11): RT1 5.21 kohm from REGN, RT2 29.87 kohm and TH1 10 kohm 103AT NTC to GND; QON (12) to TP5; BAT (13, 14) with C6 10 uF and the cell BT1 (leads W5, W6); SYS (15, 16) with C4, C5 10 uF (20 uF); PGND (17, 18) and PowerPAD on GND; SW (19, 20) to L1 1 uH to SYS; BTST (21) C7 47 nF to SW; REGN (22) C8 4.7 uF 10 V; PMID (23) C2, C3 22 uF (44 uF, at least the 40 uF the table asks with OTG); DSEL (24) no-connect. U3 TPS63802 per Table 7-1 and Figure 10-1 of `case_tps63802.pdf`: VIN (10) and EN (1) on SYS with C11 10 uF; MODE (2) on GND (power save); L1/L2 (9/7) across L2 0.47 uH; VOUT (6) = 3V3 with C12 22 uF; FB (4) R3 560 kohm from 3V3 and R4 100 kohm to GND (3.300 V); PG (5) no-connect.

**USB-C input (sheet 4).** J1 USB4105-GF-A, pins from the drawing's pin/signal table: VBUS A4, A9, B4, B9 = VBUS_IN; GND A1, A12, B1, B12 and the shell; CC1 A5 with R1 5.1 kohm to GND and R6 100 kohm to CC1_SENSE; CC2 B5 with R2 5.1 kohm and R7 100 kohm to CC2_SENSE; Dp1/Dp2 (A6, B6) = USB_C_DP, Dn1/Dn2 (A7, B7) = USB_C_DN to U2; SBU1/SBU2 no-connect.

**Ring link (sheet 5).** U5 TPS2553 (SOT-23 pins from Table 5-1 of `case_tps2553.pdf`): IN (1) on PMID with C16 100 nF; GND (2); EN (3) = VRING_EN; FAULT (4) = VRING_FAULT_N; ILIM (5) R5 59.0 kohm to GND (401 mA); OUT (6) = VRING with C15 10 uF. R12 100 kohm / R13 47 kohm divider VRING to VRING_SENSE. U6 TPD4E05U06 (Table 4-2): D1+ = USB_D+, D1- = USB_D-, D2+ and D2- on VRING, GND 3 and 8, NC 6, 7, 9, 10 open. Spring pins and wires along Y: P1/W1 VRING (ring VBUS), P2/W2 USB_D-, P3/W3 USB_D+, P4/W4 GND. E1 touch electrode with wire W7 to RING_TOUCH.

**Storage (sheet 6).** U4 ZDSD64GLQEAG-R in SD 4-bit mode (names from section 5 of `sdnand_zetta_family_atta.pdf`): CLK through R26 22 ohm from SD_CLK, CMD, DAT0 to DAT2, CD/DAT3 to U1; R18, R19, R20 10 kohm pull-ups on CMD, D0, D1; VDD on 3V3 with C13 100 nF and C14 4.7 uF.

**Test pads (sheet 7).** TP1 BOOT, TP2 EN, TP3 TXD0, TP4 RXD0, TP5 QON, TP6 to TP15 IO33 to IO42, TP16 GND.

## 2. Values and their basis

| Part | Value | Basis |
|---|---|---|
| C1 | 1 uF | BQ25895 Table 6-1 VBUS |
| C2, C3 | 22 uF each | Table 6-1 PMID: 40 uF minimum with OTG up to 2.4 A |
| C4, C5 | 10 uF each | Table 6-1 SYS 20 uF; section 9.2.2.3 |
| C6 | 10 uF | Table 6-1 BAT |
| C7 | 47 nF | Table 6-1 BTST 0.047 uF |
| C8 | 4.7 uF 10 V | Table 6-1 REGN |
| L1 | 1 uH | case-bom (section 9.2.2.3 "1-uH ... recommended") |
| R11, RT1, RT2, TH1 | 260 ohm, 5.21 k, 29.87 k, 10 k 103AT | case-bom and architecture section 4 (Figure 9-1 shows 260 ohm, 5.23 k, 30.1 k) |
| R14 to R22, R24 | 10 kohm | architecture section 6; Table 6-1 asks 10 kohm on STAT, SCL, SDA, INT |
| U3 set: C11, C12, L2, R3, R4 | 10 uF, 22 uF, 0.47 uH, 560 k, 100 k | TPS63802 Figure 10-1 and Table 10-1 (one 22 uF for VOUT up to 3.6 V); divider from the architecture |
| R5 | 59.0 kohm | architecture (inside 15 to 232 kohm, Table 5-1) |
| C16 | 100 nF | Table 5-1 IN pin ("0.1 uF or greater") |
| C15 | 10 uF | case-bom C-set "VRING 10 uF" |
| R1, R2 | 5.1 kohm | architecture, USB-C sink |
| R6, R7, R12, R13, R23, C30, R25, R26 | as section 6 | architecture section 6 |
| C9, C10, C13, C14 | 10 uF, 100 nF, 100 nF, 4.7 uF | case-bom C-set |

## 3. Additions and removals against case-bom.csv

Added (36, each with its reason in `additions.csv`): C1 to C16 (C-set split, plus C16); R24 (STAT pull-up), R25 (VRING_EN pull-down), R26 (SD_CLK series), all three named in architecture section 6 but missing from case-bom; W7 (fifth pin-board wire, for E1); TP1 to TP16.

Not placed: `C-set` (placeholder line, split into C1 to C16).

R14 to R22 assignment (case-bom gives the count, not the order): R14 SDA, R15 SCL, R16 INT, R17 FAULT, R18 SD_CMD, R19 SD_D0, R20 SD_D1, R21 CHG_CE_N (to GND), R22 BOOT.

## 4. Open pins

`open-pins.csv`, 12 rows: U4 8 pads (SD names known, LGA8x2 pad numbers not in a readable drawing, supplier item S3); BT1 2 leads; U2 PowerPAD (no number in Table 6-1); J1 shell (no number in the pin table). Open part codes: L1, L2 and every passive without a maker code (case-bom says "choose maker part").

## 5. ERC

`erc-report.txt`: 0 violations (errors and warnings, severity all). One PWR_FLAG on GND (ground has no power output pin). A copy without it reports 1 `power_pin_not_driven` error (`evidence/broken/exits.txt`), so the check is live.

## 6. Conflicts with the case architecture

1. TPS2553 pin numbers: the architecture writes "U5 EN (pin 4)" and "FAULT (pin 2)". Table 5-1 of the datasheet, SOT-23 TPS2553: EN = 3, FAULT = 4, GND = 2, ILIM = 5, IN = 1, OUT = 6. The nets follow the architecture (IO15 to EN, IO16 to FAULT); the pin numbers follow the datasheet.
2. LED1 APTF1616SEEZGQBDC is common anode (pin 1; red, green, blue cathodes on 2, 3, 4: package drawing p.1). The architecture writes "470 ohm to LED1 red anode". Kept the GPIO, resistor, LED order of the architecture; the common anode goes to 3V3 and the GPIOs drive low to light (firmware: active low).
3. BQ25895 DSEL: Table 6-1 says "Connect the DSEL to a logic rail via 10-kohm resistor"; the architecture says not connected. Kept not connected (DSEL is open drain; it only signals the D+/D- detection).
4. The pin board carries E1 and P1 to P4, but case-bom PCB2 says "4 wires to PCB1". E1 needs a fifth: W7 added.
5. TPS63802 divider: the architecture uses 560 k / 100 k (3.300 V by its formula); TI Figure 10-1 shows R1 511 k, R2 91 k, and Table 10-1 lists 511 k and 562 k for 3.3 V. Kept 560 k / 100 k.
6. BQ25895 L1: case-bom 1 uH from section 9.2.2.3; the Figure 9-1 label in the extracted text reads 2.2 uH. Kept 1 uH.
7. STAT pull-up, VRING_EN pull-down and SD_CLK series resistor are in architecture section 6 but have no case-bom line: R24, R25, R26 added.

## 7. Design risks an electronics engineer must review

1. ESD part on VRING: TPD4E05U06 allows 5.5 V maximum on a pin (Recommended Operating Conditions). VRING is PMID (USB VBUS through the RBFET, or the 4.998 V boost); a USB source at the top of its range sits close to that limit.
2. PMID load while charging from USB (supplier item S5): U5 draws from PMID while the BQ25895 charges BT1.
3. Full-speed USB host over spring pins and 30 AWG wires; no series resistors on D+/D-. The ESP32-S3 internal PHY and the ring's high-speed device must agree on full speed (case item S2).
4. SD 4-bit bus: pull-ups only on CMD, D0, D1 as the architecture says; SD practice puts pull-ups on D2 and D3 as well. Pad numbers of U4 are open.
5. Strapping pins IO3, IO45, IO46 left floating; the module datasheet names IO0 and IO46 as strapping pins. Confirm the boot mode and the flash voltage with the ESP32-S3 series datasheet.
6. LED green and blue need 3.3 V typical forward voltage at 20 mA; from 3V3 through 150 ohm they will be dim (bench B4).
7. TS window: RT1/RT2 values from the architecture differ from TI Figure 9-1 (5.23 k, 30.1 k); check the JEITA window with the chosen NTC.
8. BQ25895 CE pulled low by R21: charging starts without firmware; OTG pin floats until U1 drives IO6 (no pull resistor in the architecture).
9. TPS63802 MODE on GND (power save) for low quiescent current; PG unused.

## 8. Proofs

- `check_netlist.py`: `evidence/check_c1.log` (exit 0): 65 of 65 U1 pins as section 6, the other-pins sentence, spring pin order, CC resistors, TS divider, U5, designators, every pin once, no single-pin net, 7 rails with one source each, KiCad export equal to netlist.csv.
- It fails on broken copies: `evidence/broken/exits.txt` (P2 moved to USB_D+: exit 1; U1 pin 19 moved to VRING_FAULT_N: exit 1).
- ERC: `erc-report.txt`. PDF: `case-schematic.pdf`, 7 pages, all read (`evidence/pdf_c1_p1.png` to `p7.png`), 0 overlapping word pairs (`evidence/render_c1.log`).

## questions_for_owner

none

RESULT: done, check_netlist.py exit 0, ERC 0 errors, 12 provisional pin numbers in open-pins.csv.
