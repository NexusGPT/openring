# Review of the open circuit risks (ring section 9, case section 7)

Date: 2026-11-13 (work from 16:25 CET, `date`). Version: commit 796a0086 as the brief states (not checked here: this review runs no git). Paths are from ROOT. W = `design/ecad/risk-review-work/` (my text copies, page images, scripts, logs). Every maker quote sits on a line that starts `Quote:` with the text copy it is in; `W/verify_quotes.py` runs `grep -n -F` on each and writes `W/quotes-verify.log`.
Start: `design/wiring/deferred-work/deferred-facts.md` section "Item 27" (read in full).
Nothing here is applied outside the two risk sections: every other change is in "Proposed changes for the lead".

## Table

| Risk | Verdict | One line |
|---|---|---|
| ring 1 screen power sequence | CLOSED | Tailor sheet page 9 drawing gives the order; firmware.md line 381 must follow it (proposal P1, P2) |
| ring 2 SGM38046 AVIN | CLOSED | AVIN has only its 10 uF capacitor in the maker's own Figure 1; the netlist matches |
| ring 3 USB protection at 5.5 V | CLOSED | ring parts survive a fault (nPM1304 VBUS 22 V max), U9 only to 5.5 V; the case cuts VRING above 5.5 V (proposal P3) and the builder measures it |
| ring 4 antenna retune | NEEDS HARDWARE | match tuned with a network analyser on the first ring (M1) |
| ring 5 power chip pin numbers | CLOSED | 35 of 35 U2 balls equal Nordic Table 33 (script, 0 differences) |
| ring 6 back-powering of storage lines | CLOSED | U10 isolates the card when VDD_SD is off (TI); firmware.md lines 465 and 506 hold the rules |
| ring 7 3.0 V rail load at motor start | CLOSED | the motor is no longer on VDD_3V0 (U11 IN on VBAT); the rail carries the screen VCI and storage |
| ring 9 crystal X1 load | NEEDS HARDWARE | same crystal as Nordic's CAAA reference (CL 8 pF, no external capacitors); the 32 MHz accuracy is measured (M2) |
| ring 10 charger setting against the cell | CLOSED | 15 mA and 4.35 V are chip settings and a requirement of the custom cell (`design/mfg/specs/cell.md` line 78) |
| ring 11 place of U9 | CLOSED | U9 is on the main board 5.44 mm from J_BAND_B (routed board), as lead row 75 accepts; no file conflict on the place |
| ring 12 storage pads 1 and 7 | CLOSED | the maker's reference design pulls up all DAT0-3 lines, pads 1 and 7 included |
| case 2 U2 D+/D- open | CLOSED | open lines end in "Unknown Adapter", 500 mA; the case software overwrites IINLIM from the CC reading |
| case 3 PMID load | NEEDS HARDWARE | the document does not say whether a PMID load counts in IINLIM; the builder measures input current and VRING (M3) |
| case 4 USB over spring pins, no series resistors | NEEDS HARDWARE | no maker document on disk asks for series resistors; the first-case link test decides (M4) |
| case 5 strapping pins | CLOSED | IO45, IO46 default to 0 by internal pull-downs, IO3 is ignored while the eFuses stay 0; rule not to burn them (proposal P4) |
| case 7 thermistor window and JEITA | CLOSED | window 0 to 45 C computed (W/ts_window.log), equal to the cell's 0 to 45 C; the BQ25895 has no JEITA steps |
| case 9 TPS63802 MODE | CLOSED | MODE tied to GND = automatic power save, allowed by TI; not floating |

Settled risks, line still says so (checked 2026-11-13):
- ring 8: `design/ecad/ring/sch-notes.md` line 305 (294 before the decision lines) "## 13. v7 changes (2026-11-11): the recording light removed in v7, round joystick". Confirmed.
- ring 13: `design/wiring/lead-decisions.md` line 44 "The centre press is ONE switch, SW2, under the cap's centre"; `design/ecad/ring/sch-notes.md` line 87 "SW2 centre switch under the round joystick cap". Confirmed.
- case 6: `design/ecad/case/sch-notes.md` line 87 (83 before the decision lines) "CLOSED by design (sim finding 3, section 9)"; `design/ecad/case/netlist.csv` line 219 "SYS,LED1,1,A,passive". Confirmed.
- case 8: `design/ecad/case/sch-notes.md` line 90 (85 before the decision lines) "CE is pulled high by R21"; `design/ecad/case/netlist.csv` line 14 "3V3,R21,2,~,passive" and line 45 "CHG_CE_N,R21,1,~,passive". Confirmed.

Case 8 conflict (brief point 3): `design/sim/circuit/sim-notes.md` line 16 "CE is held low by R21, so charging starts without firmware" is the first finding and is WRONG for today's circuit: the netlist puts R21 between CHG_CE_N and 3V3 (lines 14 and 45 above), so CE is high at power-on. The case notes (line 90) are right. A second, smaller conflict: `design/wiring/lead-decisions.md` line 30 says "the resistor R21 goes to the charger's own REGN supply"; line 34 of the same file and the netlist say 3.3 V. The netlist and line 34 are right. Proposals P5 and P6.

## Ring risks

### Ring 1: screen power sequence
Today: VCI = VDD_3V0 (`netlist.csv` line 335), IOVCC = VDD_1V8 (line 318), SWIRE from the screen tail pin 6 to U4 C3 (lines 274 to 276), AVDDEN = OLED_PWR_EN from U1 F9 with R66 100 kohm to GND (lines 204 to 206, 104), U4 PVIN on VBAT (line 298).
Maker documents: Tailor TOH095XVT-01 sheet page 9 (no text in the PDF: the page is a drawing; I read it as an image, `W/tailor-p-09.png`, rendered by `pdftoppm` at 200 dpi).
Quote: design/ecad/risk-review-work/tailor-toh095xvt-01.txt | The power on/off sequence is illustrated below
Quote: design/ecad/risk-review-work/tailor-toh095xvt-01.txt | Swire protocol setting pin of Power IC
Quote: design/datasheets/p3_sgm38046.txt | The device can be shut down by pulling both AVDDEN
Quote: design/datasheets/p3_sgm38046.txt | AVDDEN On → SWIRE On → SWIRE Off → AVDDEN Off
Quote: design/datasheets/p3_sgm38046.txt | SWIRE On → AVDDEN On → SWIRE Off → AVDDEN Off
What the page 9 drawing shows (my reading of the image; the labels are small and blurred, the numbers below are the legible ones): IOVCC and VCC rise with "No Order" between them; RESX goes high after VCC; a gap marked ">10ms" from RESX high to the first interface data; "Initial setting & Sleep out" then ">120ms" to "Display on"; Swire stays low through "Unknown", "Reset" and "Sleep out" and starts only after "Display on"; ELVDD and ELVSS follow ">66.7ms" after "Display on", with "Ten_dly<400us" and a "10ms" ramp. The page shows no power-off drawing.
Verdict: CLOSED. (1) The rails: VCI and IOVCC both come on with the bucks; the sheet allows "No Order", so the circuit is right as it is. (2) The SGM38046 stays in shutdown while the screen is off: SWIRE is low from power-up until after "Display on" (page 9), and AVDDEN is held low by R66 and OLED_PWR_EN; both low is shutdown (SGM38046 page 14). (3) Either start order of AVDDEN and SWIRE is allowed by SG Micro (sequences 1 and 3), so OLED_PWR_EN may go high before "Display on". (4) The firmware order in `design/firmware.md` line 381 differs from page 9 in step (5): it says the vendor code makes SWIRE run BEFORE "sleep out"; page 9 shows SWIRE only after "Display on". Line 381 must change (P1), and open item 23 at line 1158 closes (P2). Off: SG Micro sequence 1 (SWIRE off, then AVDDEN off after tOFF_DLY > 300 us) is what line 382 already does.
Check on the first unit (confirmation, not a gate): M5.

### Ring 2: SGM38046 AVIN
Today: net SGM_AVIN holds U4 A2 and C22 only (`netlist.csv` lines 242, 243); C22 is 10 uF GRM155R60J106ME15 (`parts.csv` line 73). PVIN on VBAT.
Quote: design/datasheets/p3_sgm38046.txt | Analog Power Pin. Place a bypass capacitor between this pin and ground.
Quote: design/datasheets/p3_sgm38046.txt | Supply Input Voltage, AVIN, PVIN to AGND
Quote: design/datasheets/p3_sgm38046.txt | GRM155R60J106ME15
Figure 1 (page 4, read as an image `W/sgm38046-p-04.png`): VIN joins PVIN with C1 4.7 uF; AVIN has only C2 10 uF to ground and no wire to VIN. Table 1 and Table 2 list C2 as 10 uF/6.3 V/X5R GRM155R60J106ME15. The block diagram (page 13, `W/sgm38046-p-13.png`) draws AVIN into the UVLO block only.
Verdict: CLOSED. The ring copies the maker's Figure 1 exactly (AVIN to its own 10 uF, same Murata code). The sheet does not say where AVIN is fed from inside the chip: not in a document on disk. It does not need to be known: the maker's application circuit is the rule, and the ring follows it. No change.

### Ring 3: USB protection at 5.5 V
Today: U9 TPD4E05U06 on USB_DP, USB_DN and VBUS (`netlist.csv` lines 285, 289, 307, 308). VBUS also feeds U2 B1, B2, R1 to U1 H9, C71, C72, R73.
Quote: design/ecad/risk-review-work/case_tpd4e05u06.txt | Reverse stand-off voltage
Quote: design/ecad/risk-review-work/case_tpd4e05u06.txt | surges above the reverse standoff voltage of 5.5V.
Quote: design/datasheets/npm1304_datasheet_v1_0.txt | Overvoltage protection threshold
Quote: design/datasheets/npm1304_datasheet_v1_0.txt | SYSREG is disabled when VBUSvoltage is above the overvoltage threshold VBUSOVP, or below the
Quote: design/ecad/risk-review-work/case_bq25895.txt | VBUS over-voltage rising threshold
Quote: design/ecad/risk-review-work/case_tps2553.txt | Voltage range on IN, OUT, EN or EN, ILIM, FAULT
Facts: the nPM1304 VBUS takes up to 22 V absolute (Table 4, text lines 562 to 568) and turns its system regulator off above VBUSOVP 5.5 V; U9 stands off 5.5 V and conducts above it. On the case side, the BQ25895 passes VBUS to PMID up to its 14 V over-voltage threshold, and the TPS2553 IN is rated to 7 V: so a USB source above 5.5 V would reach the ring's pads. Nothing in the case cuts VRING on over-voltage today (search "VRING_SENSE" in `design/case/case-architecture.md`: only line 175, the divider).
Verdict: CLOSED with one design rule added (P3): the case software reads VRING_SENSE (divider 100 kohm / 47 kohm, `case-architecture.md` line 175) and drives VRING_EN low when VRING exceeds 5.5 V (1.759 V at the pin, = 5.5 x 47 / 147). The builder's check of lead row 60 item 26 stays (M6). The USB data part of the old risk (impedance) is settled by lead row 75 (full speed only).

### Ring 4: antenna retune
Today: ANT1 Johanson 2450AT18D0100 with the match L2, C3, L3, C12, L4, C13 (not mounted), C89 (not fitted) and LT1 (lead row 20).
Quote: design/ecad/risk-review-work/antenna_johanson_2450AT18D0100.txt | Antenna Matching Network
Quote: design/ecad/risk-review-work/antenna_johanson_2450AT18D0100.txt | (Can be swapped)
Quote: design/ecad/risk-review-work/antenna_johanson_2450AT18D0100.txt | Radiated efficiency is 72%
The maker gives a matching network on its 20 x 40 mm evaluation board only; values for another board are not in a document on disk. Lead row 67 records that the simulated antenna failed its own validation.
Verdict: NEEDS HARDWARE: measurement M1. Values stay Nordic's until then.

### Ring 5: power chip pin numbers
Quote: design/datasheets/npm1304_datasheet_v1_0.txt | Table 33: Pin descriptions
Quote: design/datasheets/npm1304_datasheet_v1_0.txt | The default VBUS current limit of 100 mA is used until the power source capability is detected. Host
Check: `W/ring5_balls.py` reads Table 33 from the datasheet text copy and every U2 row of `netlist.csv`: "Table 33 balls read: 35", "U2 rows in netlist: 35", "RESULT differences 0" (`W/ring5_balls.log`).
The other parts of the old item: the inductor and thermistor codes are closed by lead row 24 (L71, L72 1269AS-H-2R2M=P2; RT1 NCP15XH103F03RC). CC1, CC2 open: the chip runs at its 100 mA default until the software sets the limit (quote above; firmware sets 500 mA, `design/firmware.md` line 881).
Verdict: CLOSED. The risk text named the nPM1300; the circuit carries the nPM1304 with Nordic's ball map.

### Ring 6: back-powering of the storage lines (and the microphone clocks)
Today: U10 SN74AXC4T774 between the chip and the card, VCCA on VDD_1V8, VCCB on VDD_SD (ring `sch-notes.md` line 173); pull-ups R60, R63, R64, R65 to VDD_SD (`netlist.csv` lines 353 to 356).
Quote: design/ecad/risk-review-work/w1_ti_sn74axc4t774.txt | VCCA or VCCB is less than 100 mV, both I/O ports
Quote: design/ecad/risk-review-work/w1_ti_sn74axc4t774.txt | drawn from or to an input, output, or combined I/O
Verdict: CLOSED. With VDD_SD off the shifter's ports go high-impedance, so a chip line cannot feed the card. Between 100 mV and the working supply the isolation is not stated, so the software rule stays: `design/firmware.md` line 506 ("no storage line is driven high while VDD_SD is off") and line 465 ("MIC_A_CLK is driven low whenever VDD_MIC is off"). Both are written. No change.

### Ring 7: 3.0 V rail load at motor start
Today: U11 IN on VBAT (`netlist.csv` line 295), so the motor is not on VDD_3V0. VDD_3V0 = U2 VOUT2 (line 339) feeds the screen VCI (line 335) and the storage switch LSIN2 (line 338). The screen panel supply U4 PVIN is on VBAT (line 298).
Quote: design/ecad/risk-review-work/slim2_jinlong-w0525ab001d.txt | Starting current
Quote: design/ecad/risk-review-work/slim2_jinlong-w0525ab001d.txt | Below 175 mA
Quote: design/datasheets/npm1304_datasheet_v1_0.txt | Two 200 mA buck regulators
Quote: design/ecad/risk-review-work/slim2_cs-sdnand-20230403.txt | Operation current
Verdict: CLOSED. The 175 mA start current of the motor is drawn from the cell through U11 (lead row 14), not from the 200 mA buck. The storage part's operation current is 25 mA maximum (CS sheet, text line 158). The screen driver's VCI current is not in a document on disk (lead row 17): the build guide already measures it. No change.

### Ring 9: crystal X1 load
Today: X1 Kyocera CX2016DB32000D0WZRC1 (`parts.csv` line 16), no load capacitors in the netlist.
Quote: design/ecad/risk-review-work/w1_kyocera_cx2016db_catalog_page10.txt | Load Capacitance (Unit:pF) Ex.: D1:8.1pF
Quote: design/parts/nordic-ref-text/bom_caaa.txt | XTAL SMD 2016, 32MHz, Cl=8pF, Tot: ±40ppm
The order code "D0" is 8.0 pF in Kyocera's how-to-order table; Nordic's CAAA reference uses the same code with no external capacitors. How the chip's internal load capacitance is set: not in a document on disk (no nRF54LM20A product specification on disk; search "INTCAP|internal load cap" in `design/datasheets`, `design/parts`, `design/firmware.md`: no hit).
Verdict: NEEDS HARDWARE: measurement M2 (32 MHz accuracy). The factory test T-XTAL covers only the 32.768 kHz crystal (`design/firmware.md` line 1033).

### Ring 10: charger setting against the cell's limit
Quote: design/datasheets/npm1304_datasheet_v1_0.txt | The charge current limit is set between 4 mA and 100 mA in 0.5 mA steps.
Quote: design/datasheets/npm1304_datasheet_v1_0.txt | 4V35
Today: `design/mfg/specs/cell.md` line 78 (section "Requirements on the cell", line 68): "accepts a constant current of 15 mA to 4.35 V at 0 to 45 C, every size"; lead row 65.
Verdict: CLOSED. Both values are settings the chip offers, and the cell is a custom part whose specification requires them; "until Grepow states" in ring `sch-notes.md` line 103 is history (the lead's row 65 replaced the question by a requirement).

### Ring 11: place of U9
Board: `pcb/placement-final.csv` line 88 "U9 ... 3.120,5.200,90" and line 82 "J_BAND_B ... -2.250,4.325"; the routed `pcb/ring.kicad_pcb` has U9 at 103.12, 105.2 and J_BAND_B at 97.75, 104.325 (`W/fp_pos.py`, `W/u9-board-positions.log`): 5.44 mm centre to centre; U9 to U1 5.27 mm.
Quote: design/ecad/risk-review-work/case_tpd4e05u06.txt | The optimum placement is as close to the connector as possible.
Quote: design/ecad/risk-review-work/case_tpd4e05u06.txt | away from the protected traces which are between the TVS and the connector.
Which file is right: there is no conflict on the place. ring `sch-notes.md` line 105 ("sits at the board end, not at the pads") means the main board, not the charging pads CP1 to CP4 in the band: true. `lead-decisions.md` line 15 names the nets (true: `netlist.csv` lines 285, 289, 307, 308) and line 75 says "U9 is not moved" (true: the routed board). `sch-notes.md` line 44 "at the main board end of J_BAND_B" is true in the same sense. What is not met is section 11.2 item 4 of ring `sch-notes.md` (line 164) "U9 must sit next to the J_BAND_B pads": it sits 5.44 mm away, half way to the chip.
Verdict: CLOSED by lead row 75 (accepted as routed; TI's rule is "as close as possible", not a distance). The board rule of TI's second quote (no unprotected line beside the protected run) is not checked here: the board is not my file. No change proposed.

### Ring 12: storage pads 1 and 7
Today: U3 pad 1 on SD_DAT2 with R64, pad 7 on SD_DAT1 with R63, both 47 kohm to VDD_SD (`netlist.csv` lines 230 to 233, 354, 355; `parts.csv` lines 65, 66).
Quote: design/ecad/risk-review-work/slim2_cs-sdnand-20230403.txt | The host shall pull-up all DAT0-3 lines by RDAT, even if the host uses the SDNAND as 1-bit mode only in SD mode. It is
Quote: design/ecad/risk-review-work/slim2_cs-sdnand-20230403.txt | RDAT and RCMD (10K~100 kΩ) are pull-up resistors protecting the CMD and the DAT lines against bus floating when SDNAND is in a
Quote: design/datasheets/slim_cs-sdnand-spec-sipeed.txt | The extended DAT lines (DAT1-DAT3) are input on power up.
Verdict: CLOSED. Pads 1 and 7 are DAT2 and DAT1 of the same pins the maker calls RSV in SPI mode; the maker's reference design pulls up all four DAT lines with 10 to 100 kohm; 47 kohm is inside. No change.

## Case risks

### Case 2: U2 D+/D- open
Today: `design/ecad/case/netlist.csv` lines 279, 280: U2 pins 2 and 3 no-connect.
Quote: design/ecad/risk-review-work/case_bq25895.txt | When the Data Contact Detection (DCD) timer of 500ms is expired, the non-standard
Quote: design/ecad/risk-review-work/case_bq25895.txt | Unknown Adapter
Quote: design/ecad/risk-review-work/case_bq25895.txt | The host can over-write IINLIM register to change the input current limit if needed.
Verdict: CLOSED. With nothing on D+/D- no BC1.2 or high voltage adapter is detected, the DCD timer runs out and Table 8-3 sets 500 mA ("Unknown Adapter"); the case software then writes IINLIM from the CC reading (`design/case/case-architecture.md` line 135). The sheet holds no sentence that allows or forbids open D+/D- pins: not in a document on disk; the pins only switch detection sources (leakage 1 uA max, text line 555). No change.

### Case 3: PMID load while charging from USB
Today: U5 TPS2553 IN on PMID (`case/sch-notes.md` line 17), R5 59.0 kohm (`case/parts.csv` line 50).
Quote: design/ecad/risk-review-work/case_bq25895.txt | The internal n-channel reverse block MOSFET (RBFET) is connected between VBUS and PMID with VBUS on
Quote: design/ecad/risk-review-work/case_bq25895.txt | always limited by the lower of IINLIM register or ILIM pin at all-time regardless of Input Current Optimizer (ICO)
Quote: design/ecad/risk-review-work/case_tps2553.txt | RILIM = 49.9kΩ
Quote: design/datasheets/npm1304_datasheet_v1_0.txt | It supports 4.0 V to 5.5 V for internal functions and
Arithmetic: the ring takes at most its VBUS limit (500 mA set by the ring software, `firmware.md` line 881); U5 limits at most 565 mA (49.9 kohm row; 59.0 kohm gives less). Whether a load on PMID is counted in the BQ25895's input current limit is not in a document on disk.
Verdict: NEEDS HARDWARE: measurement M3.

### Case 4: USB over spring pins, no series resistors
Quote: design/ecad/risk-review-work/case_esp32s3_ds.txt | ESP32-S3 features a full-speed USB OTG interface along with an integrated transceiver.
No document on disk asks for or rules out series resistors on D+/D- (search "series resist" in the ESP32-S3 and MINI-1 text copies: no hit).
Verdict: NEEDS HARDWARE: measurement M4 (the test of lead row 60, item 92).

### Case 5: strapping pins IO3, IO45, IO46
Today: `case/netlist.csv` lines 276 to 278 (IO45, IO46, IO3 no-connect); IO0 has R22 to 3V3.
Quote: design/ecad/risk-review-work/case_esp32s3_mini1.txt | Table 4-1. Default Configuration of Strapping Pins
Quote: design/ecad/risk-review-work/case_esp32s3_ds.txt | pin does not have any internal pull resistors and the strapping value must be controlled by the external circuit
Quote: design/ecad/risk-review-work/case_esp32s3_ds.txt | The default values of all the above eFuse parameters are 0, which means that they are not burnt.
Facts: Table 4-1 (module) gives GPIO45 and GPIO46 a weak pull-down (bit 0) and GPIO3 floating. GPIO45 = 0 gives VDD_SPI 3.3 V while EFUSE_VDD_SPI_FORCE = 0; GPIO0 = 1 gives SPI boot whatever GPIO46 is (Table 4-3); GPIO3 is "Ignored" while EFUSE_STRAP_JTAG_SEL = 0 (Table 3-5).
Verdict: CLOSED, with one rule written down (P4): the case's production never burns EFUSE_STRAP_JTAG_SEL or EFUSE_VDD_SPI_FORCE.

### Case 7: thermistor window and JEITA
Today: RT1 5.23 kohm REGN to TS, RT2 30.1 kohm TS to GND, TH1 103AT-2 (`case/netlist.csv` lines 96, 97, 164, 224 to 227; `case/parts.csv` lines 29 to 31).
Quote: design/ecad/risk-review-work/case_bq25895.txt | Select 0°C to 45°C range for Li-ion or Li-polymer battery,
Quote: design/ecad/risk-review-work/case_bq25895.txt | Cold temperature threshold, TS pin voltage rising threshold
Quote: design/ecad/risk-review-work/case_bq25895.txt | Recommend 103AT-2 thermistor.
Quote: design/ecad/risk-review-work/case_cell_dnk852338.txt | Charging Temperature Range
Quote: design/datasheets/w16_semitec_P12-13-AT-Thermistor.txt | 103AT-2、3
Computed (`W/ts_window.py`, `W/ts_window.log`, thresholds of the BQ25895 table, 103AT resistance table of Semitec): charging starts between -0.0 C (typical) and 40.0 C (HTF typical), stops below -1.2 to 1.1 C and above 44.3 to 45.7 C (TCO). The cell sheet gives "0 – 45°C" for charging. JEITA: the BQ25895 text has no JEITA step (search "JEITA" in `W/case_bq25895.txt`: 0 hits); Figure 8-7 shows "CHARGE at full C" across the whole window, and the cell sheet gives no reduced-current band.
Verdict: CLOSED. The window equals TI's own 0 to 45 C example (RT1 5.21 k, RT2 29.87 k, E96 values taken) and the cell's range. No change.

### Case 9: TPS63802 MODE
Today: `case/netlist.csv` line 126 "GND,U3,2,MODE,input".
Quote: design/ecad/risk-review-work/case_tps63802.txt | Set LOW for power save mode, set HIGH for forced PWM mode. It must not be
Quote: design/ecad/risk-review-work/case_tps63802.txt | allowing pulse-frequency-modulation for lower output currents. This mode is enabled by applying a low level.
Verdict: CLOSED. MODE tied low is TI's power save setting and is not floating. No change.

## Proposed changes for the lead

| Id | File, line | Old text | New text | Reason |
|---|---|---|---|---|
| P1 | `design/firmware.md` line 381 | "- On: (1) LCD_RST low; (2) OLED_PWR_EN high; (3) wait 10 ms; (4) LCD_RST high, wait 120 ms; (5) send the vendor start-up code, which makes the SH8501A drive SWIRE and so sets ELVDD and ELVSS; (6) DCS "sleep out", wait 120 ms, DCS "display on"." | "- On (Tailor sheet page 9): (1) LCD_RST low; VCI and IOVCC are already on (no order between them); (2) OLED_PWR_EN high (SG Micro allows AVDDEN before SWIRE); (3) wait 10 ms or more; (4) LCD_RST high, wait 10 ms or more; (5) send the vendor start-up code and DCS "sleep out", wait 120 ms or more; (6) DCS "display on"; the SH8501A starts SWIRE and ELVDD, ELVSS 66.7 ms or more after "display on": draw nothing that matters before that." | page 9 drawing: Swire low until after "Display on", ">66.7ms" |
| P2 | `design/firmware.md` line 1158 | "23. The SWIRE level of the SH8501A at reset and after "sleep in" (sch-notes section 9 item 1)." | "23. Closed (risk review 2026-11-13): the Tailor sheet page 9 draws Swire low through power-up, reset and sleep out; at "sleep in" the screen maker gives no drawing, so the off order of line 382 is SG Micro's sequence 1." | same |
| P3 | `design/case/case-architecture.md` line 175 (row IO5 VRING_SENSE) | "ADC1_CH4, divider 100 kΩ / 47 kΩ from VRING (5.0 V -> 1.60 V)" | "ADC1_CH4, divider 100 kΩ / 47 kΩ from VRING (5.0 V -> 1.60 V); the case software drives VRING_EN low when VRING_SENSE reads above 1.759 V (VRING above 5.5 V, the ring's U9 stand-off) and logs it" | ring 3 |
| P4 | `design/case/case-architecture.md` line 173 (row IO3) | "...used only when EFUSE_STRAP_JTAG_SEL is burnt (default 0) [DS esp32s3_ds section 3, Table 3-1 p.32]: left open |" | same text, then "; the production never burns EFUSE_STRAP_JTAG_SEL or EFUSE_VDD_SPI_FORCE (IO3 and IO45 stay open only while both are 0) |" | case 5 |
| P5 | `design/sim/circuit/sim-notes.md` line 16 | "CE is held low by R21, so charging starts without firmware." | add after it: "CORRECTED: today's netlist pulls CE high by R21 to 3V3 (`design/ecad/case/netlist.csv` lines 14, 45); the charger waits for the case software (lead rows 30, 34)." | case 8 conflict |
| P6 | `design/wiring/lead-decisions.md` line 30 | "(the resistor R21 goes to the charger's own REGN supply)" | "(the resistor R21 goes to 3.3 V, see the row of 03:15)" | line 34 and the netlist |

## Questions for makers

None. Each open point above is settled by a measurement on the first unit, because no maker document on disk is missing for a decision: the two facts not in a document (SGM38046 AVIN inside the chip; whether PMID load counts in the BQ25895 input limit) are covered by following the maker's figure (ring 2) and by M3 (case 3).

## Measurements for the builder

| Id | Risk | Instrument and points | Pass value and its source |
|---|---|---|---|
| M1 | ring 4 | vector network analyser, port at the antenna feed (C13 / LT1 pads), ring on the finger as worn, 2.40 to 2.48 GHz; change L2, C3, L3, C12, C13 values until met | return loss 6 dB or more over the band (pass line of lead row 67) |
| M2 | ring 9 | spectrum analyser or frequency counter, the ring's radio sending an unmodulated carrier at 2440 MHz (a test build of the ring software if the factory test T-RADIO has no carrier mode; not checked here), 25 C | carrier within 40 ppm of 2440 MHz, i.e. within 97.6 kHz (Nordic CAAA bill of materials, X1 "Tot: ±40ppm") |
| M3 | case 3 | USB-C power meter between a 5 V source and the case; multimeter at the ring's spring pins P1 (VRING) and P4 (GND); case cell charging and a ring charging in the seat at the same time | VRING 4.0 V or more (nPM1304 SYSREG "4.0 V to 5.5 V") and at most 5.5 V, and the case's input current never above the IINLIM the case software set |
| M4 | case 4 | the case's own USB host and a ring in the seat | the ring is listed by the case's chip and 100 MB copy without an error (lead row 60, item 92) |
| M5 | ring 1 (confirmation) | 2-channel oscilloscope on SWIRE (J1 pin 6) and LCD_RST, screen turned on by the software | SWIRE stays low until after "display on" and ELVDD comes up later (Tailor sheet page 9) |
| M6 | ring 3 | multimeter on VRING with the charger in use (lead row 60, item 26) | at most 5.5 V (TPD4E05U06 stand-off) |

## Checks run (after the decision lines were added)

- `design/.venv/bin/python design/ecad/ring/check_netlist.py` from `design/ecad/ring`: exit 0, last line "RESULT PASS netlist netlist.csv" (`W/after-check_netlist.log`; same output as before the edits, `W/diff-check_netlist.log` empty).
- `design/.venv/bin/python design/firmware-check.py`: exit 0, last line "0 failures" (`W/after-firmware-check.log`).
- `design/.venv/bin/python design/mfg/tools/check_docs.py`: exit 0, last line "RESULT PASS" (`W/after-check_docs.log`).
- Quotes: `W/quotes-verify.log`, last line "quotes checked 52, not found 0".
- Decision lines: 11 in ring section 9, 6 in case section 7; no existing line removed (`W/sch-notes-counts.log`: anchors shifted by exactly the added lines).

RESULT: done, 17 risks reviewed (the brief says 16 but its list names 17; 13 CLOSED, 4 NEEDS HARDWARE, 0 need a maker's answer) with 52 maker quotes all found again, 6 proposed changes and 6 builder measurements for the lead, and the three checks pass.
