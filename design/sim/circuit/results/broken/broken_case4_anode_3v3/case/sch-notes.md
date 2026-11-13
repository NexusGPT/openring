# Charging case schematic: notes

Contract: `design/case/case-architecture.md` version C2 (change list at its top; sections 2 to 6) and `design/case/case-bom.csv`. Designators are frozen in `bom_refs_snapshot.csv` (89 electrical designators from the C2 case-bom.csv, file time 15:48, written by `make_snapshot.py`; ranges R14-R22, W1-W4, W5-W6 expanded; PCB1, PCB2, MECH1 to MECH7 are mechanical). The C1 snapshot (50 designators) is kept as `evidence/bom_refs_snapshot_C1.csv`. `check_netlist.py` checks against the snapshot and only prints a difference to the live case-bom.csv.

Method and tools as in the ring (`design/ecad/ring/`): `make_netlist.py` writes `netlist.csv` (source of truth, 279 pin rows, 61 nets, 17 no-connect pins), `parts.csv` (89 parts), `symbols.csv`, `additions.csv`, `open-pins.csv`; `gen_sch.py` (copied from the ring, project name, sheets and power flag changed) writes `case.kicad_sym`, `case.kicad_sch` and 6 sub-sheets, `case.kicad_pro`, `sym-lib-table`; `check_netlist.py` is the check; `run_all.sh`, `prove_fail.sh`, `render_pdf.py` as in the ring. Footprint names sit in the field `Footprint_plan`.

Rebuild: `cd design/ecad/case && ../../.venv/bin/python make_netlist.py && bash run_all.sh <tag>`.

## 1. Block by block

**ESP32-S3 module, light, pull-ups (sheet 2).** U1 ESP32-S3-MINI-1-N8, all 65 pins from Table 3-1 of `case_esp32s3_mini1.pdf` p.11-12, wired as section 6 of the architecture: GND pins 1, 2, 42, 43, 46 to 65; 3V3 pin 3 with C9 10 uF and C10 100 nF; IO0 = BOOT with R22 10 kohm to 3V3 and test pad TP1; IO1/IO2 = CC1_SENSE/CC2_SENSE; IO4 = RING_TOUCH; IO5 = VRING_SENSE; IO6 = CHG_OTG (R27 100 kohm to GND, C2); IO7 = CHG_INT_N (R16 10 kohm to 3V3); IO8/IO17 = I2C_SDA/I2C_SCL (R14, R15 10 kohm); IO9, IO10, IO11, IO12, IO13, IO14 = SD_D3, SD_D2, SD_CMD, SD_CLK, SD_D0, SD_D1; IO15 = VRING_EN (R25 100 kohm to GND); IO16 = VRING_FAULT_N (R17 10 kohm); IO18 = CHG_CE_N (R21 10 kohm to 3V3, sim finding 2); IO19/IO20 = USB_D-/USB_D+; IO21, IO47, IO48 = LED_R, LED_G, LED_B through R8 510 ohm, R9 270 ohm, R10 270 ohm to the cathodes of LED1, whose common anode (pin 1) is on SYS (sim finding 3); IO33 to IO42 to test pads TP6 to TP15; TXD0/RXD0 to TP3/TP4; EN with R23 10 kohm to 3V3, C30 1 uF to GND and TP2; IO3, IO26, IO45, IO46 no-connect.

**Power (sheet 3).** U2 BQ25895 per Table 6-1 and Figure 9-1 of `case_bq25895.pdf`: VBUS (1) = VBUS_IN with C1 1 uF; D+/D- (2, 3) not connected (C2: no 9 V / 12 V handshake); STAT (4) with R24 10 kohm to 3V3; SCL, SDA, INT, OTG, CE (5 to 9) to U1; ILIM (10) R11 260 ohm to GND; TS (11): RT1 5.23 kohm from REGN, RT2 30.1 kohm and TH1 10 kohm 103AT NTC to GND; QON (12) to TP5; BAT (13, 14) with C6 10 uF and the cell BT1 (leads W5, W6); SYS (15, 16) with C4, C5 10 uF (20 uF); PGND (17, 18) and PowerPAD on GND; SW (19, 20) to L1 1 uH to SYS; BTST (21) C7 47 nF to SW; REGN (22) C8 4.7 uF 10 V; PMID (23) C2, C3 22 uF (44 uF, at least the 40 uF the table asks with OTG); DSEL (24) = CHG_DSEL with R28 10 kohm to 3V3 (C2). U3 TPS63802 per Table 7-1 and Figure 10-1 of `case_tps63802.pdf`: VIN (10) and EN (1) on SYS with C11 10 uF; MODE (2) on GND (power save); L1/L2 (9/7) across L2 0.47 uH; VOUT (6) = 3V3 with C12 22 uF; FB (4) R3 511 kohm from 3V3 and R4 91 kohm to GND (3.308 V, C2); PG (5) no-connect.

**USB-C input (sheet 4).** J1 USB4105-GF-A, pins from the drawing's pin/signal table: VBUS A4, A9, B4, B9 = VBUS_IN; GND A1, A12, B1, B12 and the shell; CC1 A5 with R1 5.1 kohm to GND and R6 100 kohm to CC1_SENSE; CC2 B5 with R2 5.1 kohm and R7 100 kohm to CC2_SENSE; Dp1/Dp2 (A6, B6), Dn1/Dn2 (A7, B7), SBU1/SBU2 no-connect (C2).

**Ring link (sheet 5).** U5 TPS2553 (SOT-23 pins from Table 5-1 of `case_tps2553.pdf`): IN (1) on PMID with C16 100 nF; GND (2); EN (3) = VRING_EN; FAULT (4) = VRING_FAULT_N; ILIM (5) R5 59.0 kohm to GND (401 mA); OUT (6) = VRING with C15 10 uF. R12 100 kohm / R13 47 kohm divider VRING to VRING_SENSE. U6 TPD4E05U06 (Table 4-2): D1+ = USB_D+, D1- = USB_D-, D2+ and D2- on VRING, GND 3 and 8, NC 6, 7, 9, 10 open. Spring pins and wires along Y: P1/W1 VRING (ring VBUS), P2/W2 USB_D-, P3/W3 USB_D+, P4/W4 GND. E1 touch electrode with wire W7 to RING_TOUCH. The five pin-board wire pads WP1 WP2 WP3 WP4 WP7 (PCB2, flat pads, the other end of W1 W2 W3 W4 W7) are parts of the netlist on this sheet with the net of their wire (made by make_netlist.py; review 2026-11-13 minor m4); netlist.csv has 284 rows and 94 parts since then.

**Storage (sheet 6).** U4 ZDSD64GLQEAG-R in SD 4-bit mode (names from section 5 of `sdnand_zetta_family_atta.pdf`): CLK through R26 22 ohm from SD_CLK, CMD, DAT0 to DAT2, CD/DAT3 to U1; R18, R19, R20, R29, R30 10 kohm pull-ups on CMD, D0, D1, D2, D3 (R29, R30 from C2); VDD on 3V3 with C13 100 nF and C14 4.7 uF.

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
| R11, RT1, RT2, TH1 | 260 ohm, 5.23 k, 30.1 k, 10 k 103AT | C2 architecture section 4 and TI Figure 9-1 |
| R27 | 100 kohm CHG_OTG to GND | C2 section 6 IO6 (OTG_CONFIG resets to 1) |
| R28 | 10 kohm DSEL to 3V3 | C2 section 6 Other pins; Table 6-1 |
| R29, R30 | 10 kohm SD_D2, SD_D3 to 3V3 | C2 section 6 (Zetta RDAT 10 to 100 kohm) |
| R14 to R22, R24 | 10 kohm | architecture section 6; Table 6-1 asks 10 kohm on STAT, SCL, SDA, INT |
| U3 set: C11, C12, L2, R3, R4 | 10 uF, 22 uF, 0.47 uH, 511 k, 91 k | TPS63802 Figure 10-1 and Table 10-1; divider from C2 section 4 (3.308 V) |
| R5 | 59.0 kohm | architecture (inside 15 to 232 kohm, Table 5-1) |
| C16 | 100 nF | Table 5-1 IN pin ("0.1 uF or greater") |
| C15 | 10 uF | case-bom C-set "VRING 10 uF" |
| R1, R2 | 5.1 kohm | architecture, USB-C sink |
| R6, R7, R12, R13, R23, C30, R25, R26 | as section 6 | architecture section 6 |
| C9, C10, C13, C14 | 10 uF, 100 nF, 100 nF, 4.7 uF | case-bom C-set |

## 3. Additions and removals against case-bom.csv

C2 case-bom.csv lists every placed designator: 89 in the snapshot, 89 placed, 0 added, 0 removed (`evidence/check_c2.log`). The parts this schematic added in C1 (C1 to C16, R24, R25, R26, W7, TP1 to TP16) are now case-bom lines; R27 to R30 came with C2. `additions.csv` marks them `in_bom_now`.

R14 to R22 assignment (case-bom gives the count, not the order): R14 SDA, R15 SCL, R16 INT, R17 FAULT, R18 SD_CMD, R19 SD_D0, R20 SD_D1, R21 CHG_CE_N (to GND), R22 BOOT.

## 4. Open pins

`open-pins.csv`, 12 rows: U4 8 pads (SD names known, LGA8x2 pad numbers not in a readable drawing, supplier item S3); BT1 2 leads; U2 PowerPAD (no number in Table 6-1); J1 shell (no number in the pin table). Open part codes: L1, L2 and every passive without a maker code (case-bom says "choose maker part").

## 5. ERC

`erc-report.txt` after C2: 0 violations (errors and warnings, severity all). One PWR_FLAG on GND (ground has no power output pin). A copy without it reports 1 `power_pin_not_driven` error (`evidence/broken/exits.txt`), so the check is live.

## 6. Conflicts with the case architecture

All seven C1 conflicts are closed by C2; each is checked by `check_netlist.py` (lines `C2: ...` in `evidence/check_c2.log`):
1. TPS2553 pin numbers: C2 states EN 3, FAULT 4, GND 2, as Table 5-1. Closed.
2. LED1 common anode on 3V3, cathodes driven low through R8, R9, R10: C2 section 6. Closed.
3. DSEL: C2 adds R28 10 kohm to 3V3, as Table 6-1. Closed.
4. Fifth pin-board wire W7: in C2 and case-bom. Closed.
5. TPS63802 divider: C2 uses 511 k / 91 k (TI Table 10-5 row for 3.3 V). Closed.
6. L1 1 uH: settled in C2. Closed.
7. R24, R25, R26: now case-bom lines. Closed.

New in C2 and applied: CHG_OTG R27 100 kohm to GND; SD_D2/SD_D3 pull-ups R29/R30; USB-C D+/D- no longer reach U2 (J1 A6, B6, A7, B7 and U2 pins 2, 3 no-connect); RT1 5.23 k, RT2 30.1 k.

Conflicts left open: none.

## 7. Design risks an electronics engineer must review

1. ESD part on VRING: TPD4E05U06 allows 5.5 V maximum on a pin. With U2 D+/D- open no high-voltage handshake can raise VBUS (C2), but a USB source at the top of its range still sits close to the limit.
2. U2 D+/D- left open: C2 notes that TI's allowance for this is open item S5; the charger then sees no DCP and U1 sets the input limit from the CC reading.
Decision 2026-11-13: risk 2 CLOSED: open D+/D- end in "Unknown Adapter" 500 mA (BQ25895 Table 8-3); the case software writes IINLIM from the CC reading; see `design/ecad/risk-review.md`, case 2.
3. PMID load while charging from USB (supplier item S5).
Decision 2026-11-13: risk 3 NEEDS HARDWARE: input current and VRING measured with case and ring charging together (M3); see `design/ecad/risk-review.md`, case 3.
4. Full-speed USB host over spring pins and 30 AWG wires; no series resistors on D+/D-.
Decision 2026-11-13: risk 4 NEEDS HARDWARE: no maker document asks for series resistors; the first-case link test decides (M4); see `design/ecad/risk-review.md`, case 4.
5. Strapping pins IO3, IO45, IO46 left open per the series datasheet (C2).
Decision 2026-11-13: risk 5 CLOSED: IO45 and IO46 default to 0, IO3 is ignored while the eFuses stay 0; rule not to burn them (proposal P4); see `design/ecad/risk-review.md`, case 5.
6. CLOSED by design (sim finding 3, section 9): the LED anode is on SYS and the resistors give 2 to 5 mA in every colour.
7. TS window with RT1 5.23 k / RT2 30.1 k and the chosen NTC: check the JEITA window.
Decision 2026-11-13: risk 7 CLOSED: charge window about 0 to 45 C, equal to the cell sheet; the BQ25895 has no JEITA steps; see `design/ecad/risk-review.md`, case 7.
8. CLOSED by design (sim finding 2, section 9): CE is pulled high by R21, so the BQ25895 does not charge until U1 pulls CE low. OTG is now held low by R27 until U1 drives IO6.
9. TPS63802 MODE on GND (power save) for low quiescent current; PG unused.
Decision 2026-11-13: risk 9 CLOSED: MODE low is TI power save mode and is not floating; see `design/ecad/risk-review.md`, case 9.

## 8. Proofs

- `check_netlist.py` after C2: `evidence/check_c2.log` (exit 0): 65 of 65 U1 pins as section 6, the other-pins sentence, the 14 C2 items, spring pin order, CC resistors, designators, every pin once, no single-pin net, 7 rails with one source each, KiCad export equal to netlist.csv.
- It fails on broken copies, one per C2 change: `evidence/broken_c2_exits.txt` (8 case copies: R27 to 3V3, DSEL open, R29 missing, R30 to GND, USB-C D+ to U2, U5 EN and FAULT swapped, LED anode to GND, R4 to 3V3; each exit 1). The C1 copies: `evidence/broken/exits.txt`.
- ERC: `erc-report.txt` (0 violations). PDF: `case-schematic.pdf`, 7 pages; pages 3 (power), 4 (USB-C) and 6 (storage) carry the C2 changes and were read (`evidence/pdf_c2_p3.png`, `p4`, `p6`); every page changed its title block to C2; 0 overlapping word pairs (`evidence/render_c2.log`).

## questions_for_owner

none

RESULT: done, check_netlist.py exit 0, ERC 0 errors, 12 provisional pin numbers in open-pins.csv.


## 9. Changes from the circuit simulation (findings 2 and 3, lead decisions rows "sim finding 2" and "sim finding 3")

**Charger enable (finding 2).** R21 (10 kohm) now pulls CHG_CE_N (U2 pin 9 CE, U1 pin 22 = IO18, a module pin that already sits on this net and is not a strapping pin) to 3V3 instead of GND. CE is active low: "Battery charging is enabled when CHG_CONFIG = 1 and CE pin = Low. CE pin must be pulled High or Low" (case_bq25895.pdf p.4, Table 6-1, pin CE). So at power-on CE is high and the charger does not charge; the power-on defaults would be 2048 mA and 4.208 V (REG04 and REG06 reset values, p.36 and p.38; Table 8-4 p.21). Pull-up rail: I used 3V3, not REGN. The document names REGN only as the bias rail of the TS pin (p.5) and as a possible pull-up rail for STAT (p.15); it does not allow it for CE. Also, with REGN as pull-up the pin of U1 would sit at the REGN voltage (above the 3.6 V maximum of the module, case_esp32s3_mini1.pdf p.27 Table 6-3 VIH max VDD + 0.3 V) whenever U1 leaves the pin floating. Limit: 3V3 comes from SYS through U3, so for the first milliseconds after the battery or VBUS arrives CE is not yet held; the charger also starts its converter only after its own power-up sequence (p.15).

Rule for the case's software, before it pulls CHG_CE_N low (IO18):
1. Write REG04 ICHG[6:0] (p.36, step 64 mA, offset 0): 140 mA is not a step; write 0000010 = 128 mA. Never write a code above 0000101 = 320 mA (the cell allows 350 mA, case_cell_dnk852338.pdf p.1). A code of 0 would disable charge.
2. Write REG06 VREG[5:0] (p.38, offset 3.840 V, step 16 mV): 4.192 V = 010110 (the default 4.208 V is 010111).
3. Write REG07 WATCHDOG[1:0] = 00 (p.39): watchdog timer off. The registers REG04 and REG06 are reset "by Watchdog" (p.36, 38), so the watchdog must be off in the same step or they return to the defaults.
4. Read the three registers back. Only then drive IO18 low (CHG_CE_N) and keep CHG_CONFIG (REG03 bit 4) = 1 (p.35).
Design risk 8 is closed by design.

**Status light (finding 3).** LED1 pin 1 (common anode) is on SYS (the net U2 pins 15 and 16 drive). SYS is taken as 3.5 V (minimum system voltage default, case_bq25895.pdf p.35) to 4.35 V (the lead's range; the cell charges to 4.2 V). Cathode drive: module pins low, VOL at most 0.1 x VDD = 0.33 V (case_esp32s3_mini1.pdf p.27).
Forward voltages: the sheet gives VF at 20 mA only (p.2: hyper red 2.0 typ and 2.5 max, green 3.3 typ and 4.1 max, blue 3.3 typ and 4.0 max). At 2 to 5 mA I read the typical curves on p.3: red 1.85 V at 2 mA and 1.93 V at 5 mA, green about 2.8 V and 3.0 V, blue about 2.75 V and 2.9 V (graph readings, plus or minus 0.15 V). Model VF = V0 + r x I: red 1.78 V + 0.03 V/mA, green and blue 2.67 V + 0.067 V/mA.
Result, I x (R + r) = SYS - V0 - VOL (VOL taken as 0.1 V):
| Colour | R | I at SYS 3.5 V | I at SYS 4.35 V |
|---|---|---|---|
| red, R8 | 510 ohm | 3.0 mA | 4.6 mA |
| green, R9 | 270 ohm | 2.2 mA | 4.7 mA |
| blue, R10 | 270 ohm | 2.2 mA | 4.7 mA |
All inside 2 to 5 mA. 510 ohm and 270 ohm are E24 values, ordered as Yageo RC0402FR-07510RL and RC0402FR-07270RL (the same family as every resistor in parts.csv). With VF tolerance of 0.15 V the currents move by about 0.3 mA.
Off states: a module pin that is high (3.3 V) leaves at most SYS - 3.3 V = 1.05 V across LED and resistor, below the start of conduction on every curve of p.3 (red starts near 1.7 V, green and blue near 2.3 V), so each colour is off and the pin sees 3.3 V, inside VDD + 0.3 V = 3.6 V (p.27). A floating pin: no current path, the cathode node drifts up by the LED's forward leakage, which the sheet does not give (it gives reverse current only, p.2). The pin's clamp diode to VDD would hold the node about one diode drop above VDD (about 3.7 V) at nanoampere level: this is above the 3.6 V figure by a small margin that the module sheet does not quantify. Residual limit, not closed by this sheet: firmware must drive the three pins high at start-up, and the module's own pull-ups are not listed as active during reset. With 3V3 absent and SYS present the clamp would light the LED; U3 is enabled from SYS (EN on SYS), so 3V3 follows SYS and the case does not occur. Design risk 6 is closed for brightness; the floating-pin voltage is the residual limit above.
