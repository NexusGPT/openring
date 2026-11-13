# Motor drive study: vibration without a reset

Date: 2026-11-11. Basis: design commit 804b91f (brief). Scope: the vibration motor M1 of the ring and the battery current limit of the power chip U2 (nPM1304), conflict S22 of architecture 17.18.

How to read the sources. "[spec pN]" is Nordic's nPM1304 Product Specification v1.0, `design/datasheets/npm1304_datasheet_v1_0.pdf`, page N as printed on the page (text copy `npm1304_datasheet_v1_0.txt` beside it). "[W0525 pN]" is Jinlong spec S-525113 rev 0, `design/datasheets/slim2_jinlong-w0525ab001d.pdf` (text copy `design/ecad/motor-drive/src_w0525_text.txt`). "[TLV755P pN]" is TI SBVS320D, `design/datasheets/motor_tlv755p.pdf` (text copy `src_tlv755p.txt`). "[budget" followed by a name is a line of `design/ecad/motor-drive/budget.log`, computed by `budget.py` from named constants, each constant with its source in the script. [ESTIMATE] marks a figure I chose, with its reason beside it. [CHOICE] marks a design decision.

## 1. The problem in numbers

- The limit. IBATLIM, "Discharging battery current limit", is 100 mA in the Min column, footnote "Validated through simulation" [spec p29 and p30]. I checked the column from the page itself: the value sits at x 361.8 to 381.7 under "Min." at x 351.1 to 371.3, not under "Typ." at x 398.9 (`columns_p29.log`; rendered page `page29.png`). A minimum here means Nordic guarantees only that loads up to 100 mA are not cut. Nordic adds: "It has not been designed for accurate current limiting", and above the limit "VSYS voltage drops below VSYSPOF causing the device to reset" [spec p28]. The nPM1304 has no register to raise it: the only related register is the status bit BCHGILIMSTATUS, "Discharge current limiter active" [spec p40].
- Where the limit sits. The limiter is in the CHARGER block between the VBAT pin and the internal VSYS supply: "If more current is required, CHARGER enters the SUPPLEMENT state to provide current from the battery, up to IBATLIM" [spec p27], and the block diagram shows the battery pack on VBAT and every regulator on VSYS [spec p6, `page6.png`]. A load wired to the battery side of the VBAT pin does not pass through it. This fact carries the recommendation.
- The motor. Jinlong W0525AB001D: rated 3.0 V [W0525 p6, 3-1-1]; operating 2.7 to 3.3 V [W0525 p5, 2-3-1]; rated current below 80 mA [W0525 p6, 3-1-4]; starting current below 175 mA, rotor held, at operating voltage [W0525 p6, 3-1-5]; starting voltage below 2.5 V [W0525 p6, 3-1-6]; 0.25 G average on a 100 g jig at 3.0 V [W0525 p6, 3-2-1]. It has its own drive IC and Hall sensor [W0525 p8, circuit description and part list items 3 and 10]. The spec states no start time: a search of the whole text for time, ms, rise, start, pulse, PWM, frequency and duty gives 13 hits, the start current and voltage rows and the life, humidity and drop test times, none a start time (`search_w0525_time.log`).
- The present drive (option e). The motor sits on VDD_3V0 (buck 2) through Q1 at full duty (architecture 17.16, row W6). A start costs 525 mW at the rail [budget P_START_RAIL] and 134.1 mA from a full cell at 4.35 V, 157.7 mA at 3.7 V, 176.8 mA at 3.30 V [budget E_START_CELL@4.35, @3.7, @3.3], with a converter efficiency of 90 % [ESTIMATE: Nordic's Figure 2, spec p9, shows about 93 to 95 % from 1 mA to 100 mA at 3.8 V in and 3.3 V out; 90 % is the figure architecture 17.18 used]. Every start is over 100 mA at every battery voltage, before any other load.
- The deeper fact. At stall the motor is at least 17.14 ohm [budget R_EFF_MIN: 3.0 V / 175 mA]. Scaled to its highest guaranteed start voltage, 2.5 V, a stalled motor draws 145.8 mA and takes 364.6 mW [budget I_STALL_AT_2V5, P_STALL_AT_2V5; ESTIMATE: current taken as proportional to voltage at stall, the rotor not turning]. With a 20 % margin the power chip can pass at most 80 mA [budget BUDGET_CHIP; CHOICE, because Nordic says the figure is from simulation and not accurate]. That is 313.2 mW at 4.35 V and 237.6 mW at 3.30 V into a converter, with no other load at all [budget P_AVAIL_ALONE@4.35, @3.3]. So no circuit that feeds this motor through the power chip can start it under the limit, unless the stall lasts less than what a capacitor in the ring can carry (section 3.1: about 0.03 ms per 22 uF part). The motor must be fed from outside the power chip.

## 2. Recommendation: feed the motor from the cell through its own 3.0 V regulator

One way, chosen: the motor gets its own linear regulator U11, a TI TLV75530PDQNR, with its input on the battery net VBAT and its output on a new net VMOT. The pin MOTOR switches U11 on and off through its EN pin. The motor's minus lead goes to ground. Q1 and D1 leave the design. The motor's current then flows from the cell straight to U11 and never through the nPM1304's battery path, so the limit sees only the rest of the ring.

### 2.1 Circuit (net by net)

| Net | Connections |
|---|---|
| VBAT | cell + (J_BAND_B pad 1, unchanged), U2 VBAT, C21, U4 PVIN (all unchanged), **U11 pin 4 IN, C83 pin 1** |
| MOTOR | U1 ball F6 (P3.01, unchanged), R61 pin 1 |
| MOT_EN | R61 pin 2, R62 pin 1, **U11 pin 3 EN** |
| VMOT | **U11 pin 1 OUT, C84 pin 1**, J_BAND_A pad 7 (MOT+), M1 + (red lead) |
| GND | U11 pin 2 GND and thermal pad, C83 pin 2, C84 pin 2, R62 pin 2, J_BAND_A pad 6 (MOT-), M1 - (blue lead) |

U11 pin numbers are the DQN column of TI's pin table: OUT 1, GND 2, EN 3, IN 4 [TLV755P p3 Table 4-1].

### 2.2 Parts

| Ref | Maker | Part number | Package and size | Value | Source read |
|---|---|---|---|---|---|
| U11 | Texas Instruments | TLV75530PDQNR | X2SON-4 (DQN0004A), 0.95 to 1.05 x 0.95 to 1.05 mm, 0.4 mm max height [TLV755P p41] | 3.0 V fixed, 500 mA LDO with active output discharge | `motor_tlv755p.pdf`: order code active, X2SON (DQN), reel of 3000 [TLV755P p28] |
| C83 | Murata | GRM155R60J106ME15 | 0402 (1.0 x 0.5 mm) | 10 uF, 6.3 V, X5R | named with this value, voltage and package in SGMICRO's SGM38046 datasheet Table 1 and 2 (`design/datasheets/p3_sgm38046.pdf` p4); Murata's own sheet was not reached (section 5) |
| C84 | Murata | GRM155R61A475MEAAD (since 2026-11-13; before: GRM155R60J106ME15, 10 uF) | 0402 (1.0 x 0.5 mm) | 4.7 uF, 10 V, X5R | `design/datasheets/w1d_murata_grm155r61a475meaa.pdf`; lead-decisions.md row "sim finding 4, correction" |
| R61 | Yageo | RC0201FR-07100RL | 0201 | 100 ohm, kept, now in series with EN | bom.csv line 62 (unchanged part) |
| R62 | Yageo | RC0201FR-07100KL | 0201 | 100 kohm, kept, now EN to ground | bom.csv line 63 (unchanged part) |
| M1 | Jinlong | W0525AB001D | 5.0 x 2.5 mm coin, two leads | unchanged | [W0525 p2, p4, p6] |
| Q1 | Diodes | DMN2450UFB4 | | **removed** | |
| D1 | onsemi | NSR0230P2T5G | | **removed** | |

### 2.3 Values and why

- U11 output 3.0 V, accuracy +-1.2 % in the DQN package [TLV755P p5]: 2.964 to 3.036 V [budget VMOT_MIN, VMOT_MAX], inside the motor's 2.7 to 3.3 V [W0525 p5]. No Q1 drop any more (today 0.7 ohm [bom.csv line 45] costs up to 0.12 V at a start, architecture 17.16).
- U11 current: the start 175 mA is under the 500 mA rating [TLV755P p4, Recommended Operating Conditions] and the current limit is 560 mA at least [TLV755P p5], 3.2 times the start [budget LDO_ICL_OVER_START]. The LDO never limits the motor.
- U11 dropout: 325 mV max at 500 mA for 2.5 to 3.3 V outputs, -40 to 125 C [TLV755P p6]. Taken as a resistance [ESTIMATE: TI gives only the 500 mA point], 0.65 ohm [budget R_LDO_DROPOUT]: 113.8 mV at a start and 52 mV running [budget LDO_VDO_START, LDO_VDO_RUN]. The motor keeps its full 3.0 V for a cell at or above 3.15 V at a start and 3.088 V running [budget VBAT_MIN_FULL_VOLT_START, VBAT_MIN_FULL_VOLT_RUN]; the firmware closes everything at 3.30 V (B2, firmware.md line 96).
- U11 input range 1.45 to 5.5 V [TLV755P p4]: the cell's 4.35 V charge voltage (architecture 17.13) and the charger's 4.65 V top setting [spec p29] are inside it.
- EN: on above 1.0 V, off below 0.3 V, 10 nA [TLV755P p6]. The pin MOTOR drives 1.8 V. R62 holds EN low while the main chip starts, in ship mode and when the main chip has no supply. Start-up 550 us [TLV755P p6]: 2.2 % of the shortest pulse MT of 25 ms [budget LDO_START_SHARE_MT; firmware.md section 3.1 table].
- C83 at IN and C84 at OUT: TI asks for 1 uF or more on each pin [TLV755P p3 Table 4-1, p4: COUT 1 to 200 uF]. Jinlong asks for a capacitor of 2 uF or more across the motor's leads to protect the drive IC [W0525 p14, 9-4]. 10 uF X5R 6.3 V in 0402 keeps more than 2 uF at 3.0 V [ESTIMATE: X5R 0402 parts keep roughly a third to a half of their value at half their rating; Murata's curve was not reached]. Using the part already named by the SGM38046 datasheet keeps the parts list short.
- Heat: at most 236.2 mW at a start from a full cell and 108 mW running [budget LDO_P_START_MAX, LDO_P_RUN_MAX]; with the DQN package's 168.4 C/W [TLV755P p5 Table 5.4] the steady rise for a running motor would be 18.19 C [budget LDO_RISE_RUN_STEADY], and the longest pattern is on for 600 ms of 800 ms (MF, firmware.md section 3.1), so the real rise is lower. Thermal shutdown is at 165 C [TLV755P p6].

### 2.4 Worst-case current through the power chip (the limited path)

The motor is no longer in this path. The brief's sum (motor start, screen at 55 mW, recording at 4.0 mA, radio):

- Motor: 0 mA through the chip (it draws from VBAT through U11).
- Screen: 55 mW (architecture section 4 line 101), all of it counted as if it passed the chip [conservative: in fact the panel supply U4 has PVIN on VBAT (make_netlist.py line 275), so only VCI 3.2 mA at 2.8 V and IOVCC 1 mA at 1.8 V pass the chip].
- Radio: TX 5.0 mA (architecture line 40), taken at 3.0 V, 15 mW [ESTIMATE: the supply voltage behind Nordic's figure is not on file; 3.0 V rather than the chip's 1.8 V rail does not underestimate].
- Recording: 4.0 mA from the cell (architecture 17.5 line 465 and 17.15).
- Arithmetic: (55 + 15) mW / (0.9 x V) + 4.0 mA. At the power chip's cut-off of 3.1 V (architecture line 78): 29.09 mA, a margin of 70.91 % under 100 mA [budget R_CHIP_BRIEF@3.1, R_MARGIN_BRIEF@3.1]. At a full cell, 4.35 V: 21.88 mA [budget R_CHIP_BRIEF@4.35]. Even at 2.7 V, the default reset threshold VSYSPOF [spec p109]: 32.81 mA [budget R_CHIP_BRIEF@2.7].
- With a storage write burst on top (25 mA max at 3.3 V, `design/datasheets/slim2_cs-sdnand-20230403.pdf` p8, IOP write; 0.3 mA of it is already in the 4.0 mA, architecture line 90): 55.65 mA at 3.1 V, margin 44.35 % [budget R_CHIP_WITH_SD@3.1, R_MARGIN_WITH_SD@3.1]; 63.3 mA at 2.7 V, margin 36.7 % [budget R_CHIP_WITH_SD@2.7, R_MARGIN_WITH_SD@2.7].
- Stated margin of the recommendation: the current through the power chip stays at or under 55.65 mA down to the 3.1 V cut-off with every load the brief names plus a storage write, at least 44 % under the 100 mA guaranteed minimum, whatever the motor does.

### 2.5 The cell itself (open item S12)

The cell now gives the motor's current directly: 175 mA at a start plus the chip path, 227.5 mA at 3.30 V and 215.8 mA at 4.35 V with the storage write included [budget R_CELL_TOTAL_START@3.3, @4.35]. Today's drive, with the same loads, draws 229.3 mA at 3.30 V and 174.9 mA at 4.35 V [budget E_CELL_TOTAL_START_SAME_LOADS@3.3, @4.35]: about the same at a low cell and less at a full one, because a buck turns voltage into current and an LDO does not. The cell maker's discharge limit and the trip current of its protection circuit stay unknown (S12, H7) in every option; this study does not close them. A second effect follows: the cell's own resistance (not on file, S12) drops VBAT at each start, and VSYS follows it. Bench step B-M5 measures this with the real cell or a resistance standing in for it.

### 2.6 Vibration strength

Claim: the maker's 0.25 G average, measured by Jinlong on a 100 g jig at 3.0 V [W0525 p6, 3-2-1], because U11 holds the motor at 3.0 V +-1.2 % for any cell voltage of 3.15 V or more. This is the same rating as today, not more; today's drive gives the motor up to 0.12 V less at a start through Q1. The strength inside the ring, on a finger, is not measured by anyone (bench F1 of firmware.md and step B-M4 below).

### 2.7 What it costs

- Board area: U11 about 1.0 x 1.0 mm plus two 0402 parts, minus Q1 (1.0 x 0.6, bom.csv line 45) and D1 (SOD-923). The board's courtyards already cover 72 % (`design/ecad/ring/pcb/board-notes.md` line 27); whether three more small parts fit is a layout question, open below. Height 0.4 mm for U11 [TLV755P p41]; 0402 parts are about 0.5 mm [ESTIMATE from Murata's size code; sheet not reached]; both under the 1.0 mm limit of the brief.
- Ship mode: U11 stays on the cell. Its shutdown current is 0.1 uA typical and 1 uA max [TLV755P p5]. At 1 uA alone a 17.6 mAh cell would last 733.3 days [budget SHIP_DAYS_ON_LDO_ALONE]; in the worst case ship-mode drain grows by up to 3.5 times [budget SHIP_FACTOR; ESTIMATE of 0.4 uA for the nPM1304 alone read off Figure 3, spec p9].
- Fuel gauge: the nPM1304 measures battery current inside its own path [spec p99]; the motor's charge now bypasses it. Bound: one MF pattern is at most 0.02917 mAh [budget MF_CHARGE_BOUND], and 100 such patterns a day would be 2.917 mAh, 16.57 % of a 17.6 mAh cell [budget MOTOR_MAH_PER_DAY_BOUND, MOTOR_DAY_SHARE_SMALL_CELL; ESTIMATE, a deliberate over-count]. The firmware must add the motor's charge (pulse time x 80 mA, plus a start allowance) to the gauge (change F3 below).
- The 3.0 V rail gets lighter: without the motor buck 2 carries 29.7 mA at most (storage 25, screen VCI 3.2, light 1.5) [budget BUCK2_LOAD_WITHOUT_MOTOR]; today a start with a storage write asks 204.7 mA of a converter rated 200 mA [budget BUCK2_LOAD_PRESENT_START; spec p45]. The "NOT CHECKED" rail margin of architecture 17.16 is closed by this change.

### 2.8 Wiring changes (NOT made here; each line names the file and its present text)

Schematic generator `design/ecad/ring/make_netlist.py`:
- W1. Line 135, present `('VDD_3V0', 'MOT+', 'A'),` becomes `('VMOT', 'MOT+', 'A'),`.
- W2. Line 134, present `('MOTOR_DRV', 'MOT-', 'A'),` becomes `('GND', 'MOT-', 'A'),` (tail A keeps 8 pads; the motor's return gets its own ground pad).
- W3. Lines 308 and 309, present `part('M1', 'MOTOR', 'VC0720B088L', 'VC0720B088L', 'ring:FPC_TAIL_2', BD,` / `{'+': 'VDD_3V0', '-': 'MOTOR_DRV'})` become M1 W0525AB001D with `{'+': 'VMOT', '-': 'GND'}` (the part name change is architecture 17.16 and already owed).
- W4. Lines 310 and 311, present `part('D1', 'NSR0230P2', ...` / `{'K': 'VDD_3V0', 'A': 'MOTOR_DRV'})`: delete.
- W5. Lines 312 and 313, present `part('Q1', 'DMN2450UFB4', ...` / `{'G': 'MOTOR_G', 'S': 'GND', 'D': 'MOTOR_DRV'})`: delete.
- W6. Line 314, present `two('R61', 'R', '100R', '', 'ring:R_0201', K, 'MOTOR', 'MOTOR_G')` becomes `... 'MOTOR', 'MOT_EN')`.
- W7. Line 315, present `two('R62', 'R', '100k', '', 'ring:R_0201', K, 'MOTOR_G', 'GND')` becomes `... 'MOT_EN', 'GND')`.
- W8. New after line 315: U11 TLV75530PDQNR, pins IN VBAT, EN MOT_EN, OUT VMOT, GND GND (symbol and footprint X2SON-4 with thermal pad to GND, TI pin numbers OUT 1, GND 2, EN 3, IN 4); C83 10 uF GRM155R60J106ME15 0402 from VBAT to GND; C84 the same from VMOT to GND. [Since 2026-11-13 C84 is 4.7 uF, Murata GRM155R61A475MEAAD, 10 V (lead-decisions.md row "sim finding 4, correction"); C83 stays 10 uF.]
- W9. Line 342, present `('R61', 'W6 gate series resistor 100 ohm'), ('R62', 'W6 gate pull-down 100 kohm'),` becomes `('R61', 'motor regulator enable series 100 ohm'), ('R62', 'motor regulator enable pull-down 100 kohm'),`, plus rows for U11, C83, C84.

`design/ecad/ring/additions.csv`:
- W10. Line 7, present `R61,added,W6 gate series resistor 100 ohm` becomes `R61,added,motor regulator enable series resistor 100 ohm (motor-drive.md)`.
- W11. Line 8, present `R62,added,W6 gate pull-down 100 kohm` becomes `R62,added,motor regulator enable pull-down 100 kohm (motor-drive.md)`.
- W12. New rows: `U11,added,motor 3.0 V regulator from VBAT, TLV75530PDQNR (motor-drive.md)`, `C83,added,U11 input 10 uF`, `C84,added,U11 output and motor 10 uF (Jinlong 9-4 asks 2 uF or more)`. [Since 2026-11-13 C84 is 4.7 uF, Murata GRM155R61A475MEAAD, 10 V (lead-decisions.md row "sim finding 4, correction"); C83 stays 10 uF.]

`design/bom.csv`:
- B1. Line 45, present `Motor switch,Q1,1,"N-channel MOSFET, 1.8 V gate drive, switches the motor from VDD_3V0 at full duty (architecture 17.4)",Diodes Inc.,DMN2450UFB4,...`: delete.
- B2. Line 46, present `Motor diode,D1,1,flyback Schottky diode across the motor,onsemi,NSR0230P2T5G,...`: delete.
- B3. New row: `Motor regulator,U11,1,"3.0 V LDO from VBAT for the motor, enabled by MOTOR; keeps the motor current out of the nPM1304 battery limit",Texas Instruments,TLV75530PDQNR,X2SON-4 (DQN),1.0 x 1.0 x 0.4 max,3.0 V,"500 mA, dropout 325 mV max at 500 mA, +-1.2 %, shutdown 1 uA max",DS,design/datasheets/motor_tlv755p.pdf p3 p5 p6 p28 p41`.
- B4. New row: `Capacitor 10 uF 0402 6.3 V,"C83,C84",2,"U11 input and output; C84 is also the 2 uF or more across the motor that Jinlong asks",Murata,GRM155R60J106ME15,0402,1.0 x 0.5,10 uF,"X5R, 6.3 V",DS,design/datasheets/p3_sgm38046.pdf p4 Table 1`. [Since 2026-11-13 C84 is 4.7 uF, Murata GRM155R61A475MEAAD, 10 V (lead-decisions.md row "sim finding 4, correction"); C83 stays 10 uF.]
- B5. Line 44 (M1), present open action `S21: the electronics designer must recheck the motor switch Q1 and the 3.0 V rail for 175 mA at start (they were sized for 85 mA)` becomes `S21 closed by design/ecad/motor-drive/motor-drive.md: the motor is fed from VBAT by U11, outside the nPM1304 limit`.
- B6. Lines 62 and 63, present function texts `W6 gate series resistor 100 ohm` and `W6 gate pull-down 100 kohm` become `motor regulator enable series resistor 100 ohm` and `motor regulator enable pull-down 100 kohm`.

`design/firmware.md`:
- F1. Section 3.1, line 266, present `It runs at full duty from the 3.0 V rail (VDD_3V0) through Q1 (architecture 17.4): a pulse in the table is the motor on at 3.0 V, with no PWM. The pin drives the gate of Q1 (DMN2450UFB4) through R61 100 ohm, with R62 100 kilo-ohm from gate to ground, so the motor stays off while the chip starts and in SHIP and OFF (architecture W6).` becomes: it runs from its own 3.0 V regulator U11 (TLV75530P) fed from the cell; the pin drives U11's EN through R61 100 ohm, with R62 100 kilo-ohm from EN to ground, so the motor stays off while the chip starts and in SHIP and OFF; a pulse is the motor on at 3.0 V, with no PWM; MOTOR high to motor powered is up to 0.55 ms.
- F2. Line 279, present `A pulse draws below 80 mA while the motor runs and up to 175 mA at its start, from the cell through the 3.0 V rail:` becomes `... from the cell through U11, outside the power chip's 100 mA battery limit (motor-drive.md):`, the C-rates unchanged.
- F3. New line in 3.1: the motor's charge is not in the power chip's battery current measurement; the gauge adds, per pattern, the ON time x 80 mA plus a start allowance of 175 mA for the first 10 ms [ESTIMATE until bench B-M3 measures it].
- F4. Line 62 (peripheral table), present `the motor runs at full duty (on or off), so patterns in ms need no PWM (architecture 17.4)` becomes `... (motor-drive.md, regulator U11)`.
- F5. Line 798 (factory test T-MOTOR), present `jig accelerometer sees vibration; battery current rises by 30 mA or more during the pulse` becomes `jig accelerometer sees vibration; VBAT drops during the pulse` (the power chip no longer sees the motor's current, spec p99).

For the lead (read-only files I must not touch): architecture.md row W6 (line 285) and section 17.16 "Drive", "Q1" and "D1" bullets (lines 595 to 597 when read at 01:00; the file is being edited by others) describe Q1 on VDD_3V0; S21 and S22 can be marked closed by design once the lead accepts this.

### 2.9 Bench test on Nordic's kit nPM1304-EK (order code nPM1304-EK [spec p168])

The kit's user guide is not on file; the names below are the chip's pins, and the kit's header names must be read from Nordic's guide before wiring.

Connect:
- A lab supply as the "cell": 3.30 V, then 3.45 V, then 4.35 V, through a series resistor that stands for the cell's resistance (the value S12 returns; until then 1 ohm and 3 ohm [ESTIMATE: a range for a 20 mAh pouch cell]). Call its output the battery node.
- Shunt S1, 0.5 ohm, between the battery node and the kit's VBAT input. S1 carries only the chip path.
- A small adapter board with U11 TLV75530PDQNR, C83, C84, R61, R62 as in 2.1. U11 IN on the battery node (upstream of S1). EN from a host GPIO at 1.8 V. W0525AB001D on VMOT, stuck with its tape to a 100 g block on foam, as Jinlong's test [W0525 p6 and p7], with a 3-axis accelerometer on the block.
- Loads on the kit's outputs standing in for the ring: VOUT2 set to 3.0 V with an electronic load of 25 mA (storage write) plus 5.0 mA (radio, at 3.0 V as in the budget) plus 3.2 mA plus 1.5 mA; VOUT1 at 1.8 V with 2.76 mA plus 3.0 mA; and on VSYS a resistor drawing 55 mW to stand for the screen as the worst case. The loads stay on through every pulse.
- Set POFCONFIG so that a power-fail warning appears on a GPIO [spec p108 and p109]; read RSTCAUSE after each run [spec p120, register on p146].

Measure, with a scope at 10 us per point or finer:
- B-M1: the voltage across S1 (chip path current) through each pattern M1, M2, M3, MH, MT, MW, MF (firmware.md section 3.1), 50 times each, and then M2 1,000 times: 1350 patterns per supply voltage [budget BENCH_PATTERN_COUNT].
- B-M2: VSYS minimum and VMOT during each start.
- B-M3: the whole current at the battery node (second shunt), for S12, and the start time: how long the motor's current stays above 80 mA.
- B-M4: vibration in G (average over the pulse) against the same motor on the present drive (3.0 V through Q1).
- B-M5: the same runs with the series resistor at 3 ohm.

Pass line:
- Chip path current at or under 80 mA at every point of every pattern, at all three supply voltages and both resistors.
- BCHGILIMSTATUS [spec p40] never reads 1 when polled during a pulse, no power-fail warning edge, and RSTCAUSE shows no new reset after the 1350 patterns.
- VMOT at or above 2.7 V while the motor runs, and the motor starts on every pattern (accelerometer).
- Vibration within 10 % of the present drive at 3.30 V.
- Record, without a pass line: the whole cell current peak and the VSYS minimum, for S12 and the cell maker.

## 3. Options rejected

| Option | What it is | Why rejected (numbers in 3.1 to 3.5) |
|---|---|---|
| (a) Storage capacitor | capacitor on the motor's supply, refilled through a resistor or a current-limited switch | at a 10 ms start it needs 3261 uF, 296.4 parts of 22 uF in 0402, 43.25 % of one face of the board; at 190 ms, 5632 parts; one part carries 0.03373 ms. Current-limited switches on file are too loose (TPS22946 60 to 115 mA, 435 mA inrush) |
| (b) Soft start | series resistor, or a pulse train on MOTOR | a resistor that lets the motor run (3.05 ohm at most) still lets 145 mA through the chip at stall; a resistor for the budget (39.95 ohm) leaves the motor no voltage. Chopping the supply of a motor with its own drive IC restarts the IC each time and is outside Jinlong's spec |
| (c) nPM1304 outputs | load switch, LDO or LED driver of the nPM1304 | load switch limits only during its soft start; LDO 50 mA, 30 mA short of the running current; LED driver 5 mA; both load switches already carry VDD_MIC and VDD_SD; and all three sit behind the same battery limit |
| (d) Another vibration part | lower start current in the 5.0 x 2.5 mm pocket | none on file fits the pocket and has a lower start current; the next smallest coins are 6 mm; the smallest LRA on file is 6.00 x 3.43 mm |
| (e) No change | Q1 on VDD_3V0 | every start is over the limit at every battery voltage (134.1 to 188.2 mA from the cell between 4.35 and 3.1 V before other loads), and even running with the screen on passes 100 mA at 3.45 V |

### 3.1 (a) Storage capacitor

- Start duration. Not in the W0525 spec (section 1). Bounds: at most 190 ms, the "Response Time at rated voltage to 90% full amplitude" of a coin BLDC of the same build, INEED C0620BLDCL27 [`design/datasheets/slim_ineed-c0620bldcl27-spec.pdf` p4, 4-6; text `src_slim_ineed-c0620bldcl27-spec.txt` line 255]; 10 ms as a low case [ESTIMATE: my choice, not a maker's figure and not derived; it is twenty times shorter than the INEED bound]. 1 ms is shown only for scale.
- Allowed sag on the motor node: from 3.0 V to the 2.5 V start voltage plus the Q1 drop at 175 mA: 0.3775 V [budget A_DV_ALLOWED].
- Current the capacitor must give: the motor's share of the 80 mA chip budget at 3.30 V with the brief's other loads is 51.91 mA at the rail [budget MOTOR_SHARE_RAIL@3.3], so the capacitor gives 175 - 51.91 = 123.1 mA [budget A_I_EXCESS]. The largest refill resistor that still holds the share is 7.273 ohm [budget A_R_REFILL].
- Capacitance C = I x t / dV: 326.1 uF for 1 ms, 3261 uF for 10 ms, 6.195e+04 uF for 190 ms [budget A_C_NEEDED@1.0ms, @10.0ms, @190.0ms].
- Real part: Murata GRM155R60J226ME11D, 22 uF 6.3 V X5R 0402 (named in `p3_sgm38046.pdf` p4 Table 1), about 11 uF at 3.0 V [ESTIMATE, half; Murata's curve not reached]. Parts: 29.64, 296.4 and 5632 [budget A_PARTS@...]; bodies alone 14.82, 148.2 and 2816 square mm [budget A_AREA@...], that is 4.325 %, 43.25 % and 821.7 % of one face of the 27.2 x 12.6 mm board, 342.7 square mm [budget A_AREA_SHARE@..., BOARD_AREA], on a board whose courtyards already cover 72 % (board-notes.md line 27). The band channel (6.8 mm wide) holds the cell and the two ribbons (architecture 17.15) and has no free length on file. One part carries 0.03373 ms of start [budget A_T_CARRIED_BY_ONE_PART].
- Current-limited switch instead of a resistor: TI TPS22946 limits at 60 to 115 mA (CL low) or 28 to 60 mA (CL open) at 3.3 V in, allows 375 to 685 mA for 8 ms after it is turned on, and turns off after 7 to 15 ms of limiting [`motor_tps22946.pdf` p1, p5, p6]. TI TPS2553 cannot be set lower than 50 to 100 mA (ILIM tied to IN) [`case_tps2553.pdf` p7]. TI TPS63900 limits its average input at 50 or 100 mA but gives typical values only [`motor_tps63900.pdf` p5, p12, p13]. Each still needs the capacitor above to start the motor. Analog Devices MAX4995 was not reached (curl error 92 twice, `fetch_max4995.log`, `fetch_max4995_2.log`).

### 3.2 (b) Soft start

- Series resistor. For the motor to run at 80 mA and stay at 2.7 V or more, the resistor can be at most 3.05 ohm [budget B_RS_MAX_FOR_RUN]. With it a stall still draws 143.6 mA at the rail, 145 mA from the cell at 3.30 V [budget B_STALL_RAIL_WITH_RS, B_STALL_CELL@3.3]. A resistor that holds a stall to the motor's 51.91 mA share would be 39.95 ohm [budget B_RS_FOR_SHARE]; 80 mA through it would leave the motor -0.2523 V [budget B_VRUN_WITH_RS_SHARE], that is, it cannot run near its rating.
- Pulse train on MOTOR. Jinlong's circuit page: the drive IC feeds the coil and switches it from the Hall sensor's reading [W0525 p8]; the IC takes its supply from the two motor leads, the only connections [W0525 p6, 3-1-2]. Each off time of a pulse train cuts that supply; each on time is then a new start at the stall current, so the peak does not fall [ESTIMATE: my reading of the circuit page, not a statement by Jinlong]. Jinlong rates the motor only for 2.7 to 3.3 V DC [W0525 p5], warns of "functional and life problems if you use it different from the standard" [W0525 p14, 9-1] and gives no guarantee outside the spec [W0525 p14, 9-11]; it states no PWM rating. A pulse train is therefore not allowed for this motor (and the present firmware already uses none, firmware.md line 266). With a capacitor across the leads a pulse train becomes a lossy resistor: the average current equals the motor's average current, as with the resistor above.

### 3.3 (c) nPM1304 outputs

- Load switch: "Soft start is enabled by default. This ensures that the current to LSOUT[n] is limited for tSS. Once soft start is complete, there will be no current limiting provided by the load switch" [spec p68]. tSS is 1.8 ms (25 mA, 10 uF) and ILS 100 mA max [spec p69, Max column per `columns_p69.log`]; soft-start levels 25, 50, 75, 100 mA [spec p77, LDSWCONFIG]. A limit of 1.8 ms cannot cover a start of 10 to 190 ms.
- LDO mode: 50 mA output [spec p70], 30 mA under the motor's running current [budget C_LDO_SHORT].
- LED drivers: 5 mA sink [spec p80], 75 mA short [budget C_LED_SHORT].
- Both load switches are taken: LDSW1 is VDD_MIC and LDSW2 is VDD_SD (architecture section 3 lines 70 and 72; firmware.md lines 695 and 697).
- Above all, the bucks run from VSYS [spec p6] and a load switch's input "cannot exceed VSYS" [spec p67], so every nPM1304 output sits behind the same battery limit and none can supply a start the limit forbids.

### 3.4 (d) Another vibration part

The pocket fits only a 5.0 mm motor (architecture 17.15); the owner's rule keeps the ring's shape and the motor's pocket. Parts with a maker document on file (`design/parts/slim-2.md` section 1 and `design/parts/slim.md` 6.4):
- Vybronics VC0625B001L and VC0625B002L: 6 mm, start current not in the document (slim-2.md 1.1, 1.2).
- Vybronics VC0720B088L: 7 mm, start 120 mA max (slim-2.md 1.3). Even this, through the chip, would be 360 mW at 3.0 V [budget D_VC0720_START_RAIL], over the 237.6 mW the limit allows at 3.30 V [budget P_AVAIL_ALONE@3.3].
- Jinlong W0625SS001D: 6 mm, start 175 mA (slim-2.md 1.5).
- INEED C0620BLDCL27 and Vybronics VW0620AB001U: 6 mm, start 150 mA (slim-2.md 1.6).
- LRA: the smallest on file is Vybronics VLV200634A, 6.00 x 3.43 mm, too thick (slim.md 6.4). Rectangular brushed parts of `design/parts/ui.md` 4a are 2.90 mm tall or more [S], over 2.5 mm.
- Not done: a new web search for 5 mm or smaller parts. This session had no web search tool; I fetched only known maker URLs.

### 3.5 (e) No change

Risk, computed (nothing measured; no bench result is on file, and architecture 17.16 and 17.18 list bench B5 as still to do): from the cell, a start alone is 134.1 mA at 4.35 V, 157.7 mA at 3.7 V, 176.8 mA at 3.30 V and 188.2 mA at 3.1 V [budget E_START_CELL@...]; with the brief's other loads, 156 to 217.3 mA, 55.98 % to 117.3 % over the limit [budget E_TOTAL_START@4.35, @3.1, E_OVER_START_PCT@4.35, @3.1]. Running with the screen on is 103.8 mA at 3.45 V [budget E_TOTAL_RUN@3.45]. If the real limit is under these, VSYS falls below VSYSPOF and the chip resets [spec p28]: at M1 and M2, the start and the stop of a recording. Nordic gives no typical or maximum value, so the size of the real margin, if any, is unknown.

## 4. Does the same limit threaten anything else?

Without the motor, the largest loads that can happen at once through the power chip are the screen at full white and full brightness (55 mW, architecture line 101), a storage write (25 mA max at 3.0 V, 75 mW, `slim2_cs-sdnand-20230403.pdf` p8), the radio transmitting (15 mW, architecture line 40, taken at 3.0 V), the microphones (2.76 mA at 1.8 V, architecture line 88), the main chip (3.0 mA at 1.8 V, an estimate, architecture line 89) and the recording light (1.5 mA at 3.0 V, architecture line 91): 159.9 mW in all [budget OTHER_LOADS_PEAK_MW]. Through a 90 % converter that is 53.83 mA at 3.30 V, 57.3 mA at 3.1 V and 65.79 mA at 2.7 V [budget OTHER_LOADS_PEAK@3.3, @3.1, @2.7], 42.7 % under 100 mA at the 3.1 V cut-off [budget OTHER_LOADS_MARGIN@3.1]. So with the motor moved out, nothing else in the ring reaches the limit; the screen counted whole is pessimistic, because its panel supply already sits on VBAT (make_netlist.py line 275). The inputs that are estimates (main chip, radio voltage, efficiency) are the weak points, and bench step B-M1 measures the sum.

## 5. Open items and what I could not do

- Murata's own capacitor sheets: the old spec URL returned a 404 page and the PDF interface returned a script page (`fetch_GRM155R60J475ME47.log`, `fetch_api1.log`; the HTML files saved under `design/datasheets/motor_murata_*.pdf` are those pages, not datasheets). Capacitor values and packages come from SGMICRO's table; heights and DC-bias curves are estimates.
- Samsung's capacitor page returned HTML without data (`fetch_sam1.log`; file `motor_samsung_CL05A475MQ5NRNC.pdf` is that page).
- Analog Devices' MAX4995 sheet: curl error 92 twice; not read.
- nPM1304-EK user guide: not on file, not fetched.
- The start time of the W0525: not stated by Jinlong; bounded in 3.1; bench B-M3 measures it.
- The cell's resistance and discharge limit (S12): unknown; they set how far VBAT dips at a start in every option.
- Layout: whether U11, C83 and C84 fit beside the cell's entry on a board at 72 % courtyard fill.
- No web search tool was available in this session (the brief allowed it); the search for a smaller vibration part was not repeated.
- Finding outside my files, for the firmware owner: firmware.md line 703 sets `dischg-limit-microamp` to 1,000,000 with "the other allowed value, 200,000". Those are nPM1300 settings. In the nPM1304 spec the only discharge-limit register is the status bit BCHGILIMSTATUS; a search for "discharg", "IBATLIM" and "ILIM" found no setting (`search_npm1304_dischg.log`, 57 lines, the ILIM hits are the VBUS input limit). The line must go or be marked as not applying.
- Charging while a pattern plays: the charger feeds the VBAT net, and U11 then takes part of that current. The charger's end-of-charge test (current under 10 % of ICHG, ITERM, spec p29) could be delayed by a pulse in the last minutes of a charge. The only pattern the firmware plays at the case is M2 when a recording is stopped by case insertion (firmware.md section 3.1 table), at the start of a charge, so this does not arise in normal use.

## 6. Files of this study

`design/ecad/motor-drive/`: `budget.py`, `budget.log` (final), `budget_run1.log` and `compare_run1.log` (first run and its check against `expected_before_run1.txt`), `budget_run2.log`, `diff_run1_run2.log` (run 2 dropped two repeated lines and added four, no figure changed), `diff_run2_run3.log` (run 3 only added lines), `search_w0525_time.log`, `audit.py` and `audit.log` (final check of this file), `columns.py` with `columns_p6.log`, `columns_p9.log`, `columns_p29.log`, `columns_p45.log`, `columns_p69.log` and the rendered pages `page6.png`, `page9.png`, `page29.png`, `page45.png`, `page69.png`, the text copies `src_*.txt`, `search_vbat_loads.log`, the fetch logs `fetch_*.log`, and `CHECKLIST.md`. `design/datasheets/`: `motor_tlv755p.pdf`, `motor_tps7a20.pdf` (fetched, not used), `motor_tps22946.pdf`, `motor_tps63900.pdf`, and the failed pages named in section 5.

RESULT: done, one recommendation (motor on its own TLV75530P regulator fed from the cell, outside the nPM1304 battery limit) keeps the power chip's battery current at or under 55.65 mA down to 3.1 V, 44 % under the 100 mA minimum, with options (a) to (e) rejected by computed figures in budget.log.
