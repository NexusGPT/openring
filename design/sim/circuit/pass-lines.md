# Pass lines (written before the first run of each test)

Format: one row per pass line. `qty` is the exact name the bench prints. `op` is the test that must hold (measured op limit). A limit may be a short arithmetic expression; the checker evaluates it. Units are SI (V, A, ohm, s, F) unless the column says otherwise. Every row has its source (file and page or line). `STATUS` rows are not pass lines: they are facts the tests rest on.

Order proof: this file was started at the time in its first section's header line below (command `date`); the header of each section says which decks had run. Later sections carry their own time stamp.

## Section A: ring tests 1 to 7 (started 2026-11-13 00:17 CET (command date). One trial deck of test 1 was run at about 00:23 to debug the deck (two results seen: cell minimum 2.9938 V at R_SPEC, chip path 78 mA); no other deck had run)

Stand-in values used in several rows (each is stated so a reader can overrule it):
- V20 = 3.45 V is the cell open-circuit voltage used for "20 percent charge". No file gives the open-circuit voltage of the custom cell. The firmware rule B5 (firmware.md section 1.1, "average voltage at or under 3.45 V" at 5 percent state of charge) is used as a lower bound for 20 percent: the real cell at 20 percent is at or above it. The sweeps also run 3.30 V (rule B2) and 3.60 V (own assumption, no file) as information.
- R_SPEC = (V20 - 3.0 V) / 0.230 A = 1.957 ohm. Decision 41 (wiring/lead-decisions.md, item 41): "a 230 mA pulse of 100 ms leaves at least 3.0 V at the cell at 20 percent charge". So 1.957 ohm is the largest cell resistance (cell plus its protection circuit) the cell specification allows at V20. The rows marked "at R_SPEC" run with that resistance.

| id | qty | op | limit | unit | source |
|---|---|---|---|---|---|
| R1.1 | motor.rmax_ocv345 | >= | (3.45-3.0)/0.230 | ohm | decision 41 (230 mA, 3.0 V, 20 percent); V20 stand-in above. Rmax = largest Rcell for which every row R1.2 to R1.8 still holds |
| R1.2 | motor.vbat_min_spec | >= | 3.0 | V | decision 41; wiring/lead-decisions.md; firmware.md 3.1 |
| R1.3 | motor.v18_min_spec | >= | 1.71 | V | nPM1304 datasheet p45 Table 19 VOUT[n]ACC -5 percent of 1.8 V (VSET1 47 k, p43 Table 15) |
| R1.4 | motor.v18_max_spec | <= | 1.89 | V | same, +5 percent |
| R1.5 | motor.v30_min_spec | >= | 2.85 | V | nPM1304 p45 VOUT[n]ACC -5 percent of 3.0 V (VSET2 150 k, p43 Table 16) |
| R1.6 | motor.v30_max_spec | <= | 3.15 | V | same, +5 percent |
| R1.7 | motor.vmot_min_spec | >= | 2.7 | V | Jinlong W0525AB001D spec p5 item 2-3-1 operating voltage 2.7 to 3.3 V (as read in ecad/motor-drive/motor-drive.md section 1) |
| R1.8 | motor.vsys_min_spec | >= | 2.7 | V | nPM1304 p109 Table 27 VSYSPOF default falling threshold 2.7 V (below it the chip resets) |
| R1.9 | motor.ibatpath_max_spec | <= | 0.100 | A | nPM1304 p29 Table 14 IBATLIM 100 mA (Min column), p11 maximum VSYS load from battery 100 mA |
| R1.10 | motor.ildo_max_spec | <= | 0.560 | A | TLV755P datasheet p5 ICL minimum 560 mA |
| R2.1 | powerup.v18_min_c330 | >= | 1.71 | V | nPM1304 p45, p43 (as R1.3), cell 3.3 V, settled value after 20 ms |
| R2.2 | powerup.v18_peak_c330 | <= | 1.89 | V | nPM1304 p45 +5 percent (overshoot limit) |
| R2.3 | powerup.v30_min_c330 | >= | 2.85 | V | nPM1304 p45, p43 |
| R2.4 | powerup.v30_peak_c330 | <= | 3.15 | V | nPM1304 p45 |
| R2.5 | powerup.vmot_peak_c330 | <= | 0.1 | V | motor-drive.md section 2.3: R62 holds EN low so U11 is off while the chip starts; 0.1 V is the limit for "off" |
| R2.6 | powerup.vsd_pre_peak_c330 | <= | 0.1 | V | firmware.md 8.1: LDSW2 boot-off |
| R2.7 | powerup.vsd_min_c330 | >= | 2.7 | V | CS Semiconductor CSNP32GCR01-BOW datasheet p4: Vcc 2.7 to 3.6 V |
| R2.8 | powerup.vsd_peak_c330 | <= | 3.6 | V | same |
| R2.9 | powerup.vmic_min_c330 | >= | 1.6 | V | Knowles SPK0641HT4H-1 supply 1.6 to 3.6 V (ecad/ring/sch-notes.md section 12.4, new text of architecture line 41) |
| R2.10 | powerup.order_sd_after_3v0_c330 | > | 0 | s | VDD_SD is fed from VDD_3V0 (netlist LSIN2); it cannot be valid before it |
| R2.11 | powerup.v18_min_c435 | >= | 1.71 | V | as R2.1, cell 4.35 V |
| R2.12 | powerup.v18_peak_c435 | <= | 1.89 | V | as R2.2 |
| R2.13 | powerup.v30_min_c435 | >= | 2.85 | V | as R2.3 |
| R2.14 | powerup.v30_peak_c435 | <= | 3.15 | V | as R2.4 |
| R2.15 | powerup.vmot_peak_c435 | <= | 0.1 | V | as R2.5 |
| R2.16 | powerup.vsd_pre_peak_c435 | <= | 0.1 | V | as R2.6 |
| R2.17 | powerup.vsd_min_c435 | >= | 2.7 | V | as R2.7 |
| R2.18 | powerup.vsd_peak_c435 | <= | 3.6 | V | as R2.8 |
| R2.19 | powerup.vmic_min_c435 | >= | 1.6 | V | as R2.9 |
| R2.20 | powerup.order_sd_after_3v0_c435 | > | 0 | s | as R2.10 |
| R3.1 | charge.icc_min | >= | 0.0135 | A | nPM1304 p29 ICHG 15 mA set (lead decision 65) minus ICHGACC 10 percent; CC region = cell open-circuit 3.0 to 4.0 V, Rcell 0.5 to 3 ohm |
| R3.2 | charge.icc_max | <= | 0.0165 | A | same, plus 10 percent |
| R3.3 | charge.vbat_end_max | <= | 4.35*1.01 | V | nPM1304 p29 VTERM 4.35 V (decision 65, register option 4V35 p36) with VTERMACC +1 percent at TJ above 0 C; highest terminal voltage over an open-circuit sweep of 3.0 to 4.40 V |
| R3.4 | charge.vbat_end_min | >= | 4.35*0.99 | V | same, -1 percent; terminal voltage once the charge current has fallen to the termination current (10 percent of 15 mA, p29 ITERM) |
| R3.5 | charge.ibus_max | <= | 0.095 | A | nPM1304 p17 Table 9 IBUS100MA minimum 95 mA (default limit before the firmware sets another); load = charge 16.5 mA plus recording loads plus a storage write |
| R3.6 | charge.vbus_chip_min | >= | 4.0 | V | nPM1304 p13 Table 6 VBUSOP minimum 4.0 V, at the chip's VBUS balls, case VBUS 5.0 V, contact path resistance 0 to 2 ohm (stated range, no file gives it) |
| R3.7 | charge.vbus_chip_valid_margin | >= | 0.210 | V | nPM1304 p17 VBUSVALIDR 210 mV: VBUS minus VBAT must exceed it for the chip to accept VBUS, at the highest cell voltage 4.35 V |
| R4.1 | inrush.ils_peak_ss50 | <= | 0.100 | A | nPM1304 p69 Table 20 ILS 100 mA; soft start 50 mA as firmware.md 8.1 table (LDSW2 soft-start-microamp 50,000); VDD_SD capacitors as in the files |
| R4.2 | inrush.ils_peak_ss25 | <= | 0.100 | A | same with the register default 25 mA (p77 LDSWCONFIG reset 0x00) |
| R4.3 | inrush.ibuck2_peak_ss50 | <= | 0.200 | A | nPM1304 p45 Table 19 IOUT 200 mA (BUCK2 feeds LSIN2) |
| R4.4 | inrush.v30_min_ss50 | >= | 2.85 | V | nPM1304 p45 -5 percent of 3.0 V: the storage inrush must not pull the 3.0 V rail out of range |
| R4.5 | inrush.vsd_final_ss50 | >= | 2.7 | V | CS datasheet p4 Vcc minimum |
| R4.6 | inrush.ils_peak_ss50_d24 | <= | 0.100 | A | as R4.1 with C60 changed to 2.2 uF (decision 24, 3.4 uF total), run by the bench option --set C60=2.2uF |
| R5.1 | shifter.ab_high_at_card_min | >= | 0.625*3.0 | V | CS CSNP32GCR01-BOW p8 VIH minimum 0.625 Vcc at Vcc 3.0 V (SCK, MOSI, CS lines B side; A side driven high at the main chip's 1.8 V) |
| R5.2 | shifter.ab_low_at_card_max | <= | 0.25*3.0 | V | CS p8 VIL maximum 0.25 Vcc |
| R5.3 | shifter.ba_high_at_chip_min | >= | 0.7*1.8 | V | main chip input high 0.7 x VDD: Nordic nRF54LM20A limit NOT FOUND on disk; stand-in = nRF54L15 datasheet of another maker (IndieSemiC ISC-nRF54L15-A p15, Table 3), sibling chip |
| R5.4 | shifter.ba_low_at_chip_max | <= | 0.3*1.8 | V | same stand-in, input low 0.3 x VDD |
| R5.5 | shifter.idle_high_at_chip_min | >= | 0.7*1.8 | V | card lines released (card outputs Hi-Z), pull-ups R60 R63 R64 R65 to VDD_SD, shifter B to A: same stand-in |
| R5.6 | shifter.pullup_high_at_card_min | >= | 0.625*3.0 | V | pulled-up card inputs (DAT1, DAT2) with the card's worst input leakage 10 uA (CS p8 IIN): level must stay above VIH |
| R5.7 | shifter.vcc_isolation_leak_max | <= | 0.1 | V | SN74AXC4T774 datasheet SCES898C (design/datasheets/w1_ti_sn74axc4t774.pdf) p6 and sch-notes.md 11.3: with VDD_SD off, B-port nodes must not be driven above 100 mV isolation level by the A side |
| R6.1 | joy.pressed_max | <= | 0.3*1.8 | V | main chip input low 0.3 x VDD, stand-in as R5.3 (Nordic limit NOT FOUND); pressed = Alps SKTAAAE010 contact resistance 500 mohm max (design/datasheets/slim_alps-skta-aaae010-orwin.txt line 70) against the chip's internal pull-up swept 5 kohm to 100 kohm (its real value is NOT FOUND in any file on disk) |
| R6.2 | joy.released_min | >= | 0.7*1.8 | V | main chip input high 0.7 x VDD, same stand-in; released = open switch, internal pull-up only, leakage 0 |
| R6.3 | joy.pressed_current_max | <= | 0.0005 | A | design value: the pressed current through the switch (below its rating 10 uA minimum load to 50 mA, Alps spec 5.1 and 5.2, same file lines 53 and 54) must be 500 uA or less to keep standby cost small; the switch minimum load is 10 uA at 1 V DC |
| R6.4 | joy.pressed_current_min | >= | 0.00001 | A | Alps SKTAAAE010 minimum rating 1 V DC 10 uA (same file line 54): the wetting current must reach 10 uA when pressed, at Rpu 100 kohm and 1.8 V |
| R7.1 | pads.vbus_gnd_10s | < | 0.1 | V | decision 22, 33 (wiring/lead-decisions.md): 10 s after the ring leaves the case, the voltage between any two pads is under 0.1 V. Model holds only the leakage the makers state (TPD4E05U06 10 nA max, codes_tpd4e05u06 text line 25); a leak the makers do not state can only make the true voltage lower, so this value is an upper bound |
| R7.2 | pads.dp_gnd_10s | < | 0.1 | V | same, D+ to GND |
| R7.3 | pads.dn_gnd_10s | < | 0.1 | V | same, D- to GND |
| R7.4 | pads.vbus_dp_10s | < | 0.1 | V | same, VBUS to D+ |

## Section A addendum: rows added before the first run of tests 4, 5 and 7 (added 00:26 CET by command date; no deck of tests 2 to 7 had run; the test-1 trial is named above)

| id | qty | op | limit | unit | source |
|---|---|---|---|---|---|
| R4.7 | inrush.t90_ss50 | <= | 0.0018 | s | time for VDD_SD to reach 90 percent of its final value after the host enables LDSW2 at soft start 50 mA. Limit: Nordic's own stated soft start time, nPM1304 p69 Table 20 tSS 1.8 ms (stated for 10 uF, 25 mA, 0 V to 5 V). The storage supply must not take longer than the maker's own figure |
| R4.8 | inrush.t90_ss25 | <= | 0.0018 | s | same at the register default soft start 25 mA (p77 LDSWCONFIG reset value 0x00 = 25 mA) |
| R5.8 | shifter.idle_high_at_shifter_min | >= | 2.0 | V | SN74AXC4T774 datasheet SCES898C p5 Table 5.3: data input VIH 2.0 V for VCCI 3 V to 3.6 V; card lines released (card outputs Hi-Z) with the card's worst leakage 10 uA (CS p8 IIN) and the shifter input leakage 8 uA (SCES898C p6 II, data inputs, -40 to 125 C) on the 47 kohm pull-ups |
| R7.5 | pads.vbus_gnd_10s_hist | < | 0.1 | V | same as R7.1 with the worst of three cell voltages 3.3 V, 3.8 V, 4.35 V (R7.1 to R7.4 are the maximum over these three runs) |

Notes on the rows above, written before the runs:
- Expected on the real design: R7.1, R7.4 and R7.5 may FAIL. Reason to expect it: the chip keeps VBUS connected to VSYS until VBUS falls to VBAT plus 160 mV (nPM1304 p17 VBUSVALIDF), the VBUS capacitors C71, C72 (and C11 through R1) then hold that charge, and the only stated leakage is 10 nA per protection channel. Nordic states no VBUS leakage. The model therefore has no path that brings VBUS to 0.1 V in 10 s.
- R1.1 to R1.8: 233 mA total cell current is not known before the run; R_SPEC is a stand-in from decision 41. If the cell current at the start is above 230 mA, R1.2 fails at R_SPEC.

## Section A addendum 2: rows added before the first run of test 5 (added 00:3x CET, see the time stamp line below; no deck of tests 2 to 7 had run)

| id | qty | op | limit | unit | source |
|---|---|---|---|---|---|
| R5.9 | shifter.card_low_at_shifter_max | <= | 0.8 | V | SN74AXC4T774 datasheet SCES898C p5 Table 5.3: data input VIL 0.8 V for VCCI 3 V to 3.6 V; card drives DAT0 low through its weakest allowed output (VOL 0.125 VCC at 100 uA, CS p8) against the 47 kohm pull-up R60 |
| R5.10 | shifter.card_high_at_shifter_min | >= | 2.0 | V | same file p5, VIH 2.0 V; card drives DAT0 high through its weakest allowed output (VOH 0.75 VCC at 100 uA, CS p8) with the shifter input leakage 8 uA (SCES898C p6) |
00:27:59

## Section B: case tests (written before any case deck was built or run; time stamp on the last line of this section)

Facts the case rows rest on (each with its source; page numbers are PDF pages):
- BQ25895 (design/datasheets/case_bq25895.pdf): boost mode regulation BOOSTV default 5.126 V (p42 Table 8-18 REG0A), accuracy -3 to +3 percent at I(PMID) = 0 (p9), output current range up to 3.1 A (p9), over-voltage threshold 5.8 to 6.0 V rising (p9); input current limit register IINLIM default 500 mA (p32 Table 8-8), actual limit is the lower of the register and the ILIM pin; pin limit IINMAX = KILIM / RILIM with KILIM 320 / 355 / 390 (p9); charge current ICHG default 2048 mA (p36 REG04); charge voltage VREG default 4.208 V (p38 REG06); TS thresholds V(LTF) 73.25 percent, V(HTF) 48.25 percent, V(TCO) 44.75 percent of REGN (p9); TI's own example for a 0 to 45 C window with a 103AT thermistor: RTHCOLD 27.28 kohm, RTHHOT 4.91 kohm, RT1 5.21 kohm, RT2 29.87 kohm (p23).
- TPS2553 (design/datasheets/case_tps2553.pdf): current limit equations p16 and p17: IOSmax = 22980 / R^0.94, IOSnom = 23950 / R^0.977, IOSmin = 25230 / R^1.016 (mA, R in kohm, 15 to 232 kohm), rDS(on) 85 mohm typ, 95 mohm max for the DBV package at 25 C (p6).
- Cell DNK852338 (design/datasheets/case_cell_dnk852338.pdf p1): 700 mAh, charge voltage 4.2 V, recommended charge current 0.2 C, allowed maximum charge current 0.5 C (350 mA), maximum continuous discharge 1 C, internal impedance below 60 mohm, over-charge protection at 4.275 +- 0.05 V.
- LED1 APTF1616 (design/datasheets/case_kb_aptf1616.pdf): forward voltage at 20 mA, typical and maximum: red 2.0 and 2.5 V, green 3.3 and 4.1 V, blue 3.3 and 4.0 V. The sheet gives no forward voltage at lower current; the bench uses an exponential diode with ideality factor n swept 2 to 4 (own assumption, stated) fixed at 20 mA by the sheet's typical value.
- TPS63802 (design/datasheets/case_tps63802.pdf p6): feedback regulation voltage 500 mV, accuracy -1 to +1 percent in PWM mode. ESP32-S3-MINI-1 (design/datasheets/case_esp32s3_mini1.pdf p27): supply 3.0 to 3.6 V.

| id | qty | op | limit | unit | source |
|---|---|---|---|---|---|
| C1.1 | vring.noload_min | >= | 4.0 | V | VRING at no load with the boost at -3 percent of 5.126 V; ring chip VBUS operating minimum 4.0 V, nPM1304 datasheet p13 Table 6 |
| C1.2 | vring.noload_max | <= | 5.5 | V | VRING at no load with the boost at +3 percent of 5.126 V (BQ25895 p9) against the ESD part's reverse stand-off 5.5 V (TPD4E05U06, design/datasheets/codes_tpd4e05u06.pdf, text line 541, and the ring chip's VBUSOVP 5.5 V, nPM1304 p17). This is case risk 1 |
| C1.3 | vring.ilimit_short_min | >= | 0.400 | A | current limit of U5 into a short, nominal R5 from parts.csv, IOSmin equation p17 of the TPS2553 sheet; the lead's brief names 401 mA, the equation gives 400.6 mA at exactly 59.0 kohm, so 0.400 is the whole-number floor |
| C1.4 | vring.ilimit_short_max | <= | 3.1 | A | IOSmax of U5 against the boost's output current range 3.1 A (BQ25895 p9): the source can carry the limit |
| C1.5 | vring.v_at_load_min | >= | 4.0 | V | VRING with a 0.39 A load (just under the guaranteed limit) and the cell at 3.0 V; limit as C1.1 |
| C1.6 | vring.sense_max | <= | 3.6 | V | VRING_SENSE (divider R12, R13 read from parts.csv) at the highest VRING, against the ESP32-S3 supply maximum 3.6 V (case_esp32s3_mini1.pdf p27, Table 6-1 VDD33; the pin limit itself was not found, so the supply maximum is used) |
| C2.4 | charge.ilim_pin_min | >= | 0.500 | A | DATASHEET FACT (KILIM p9) applied to R11 from parts.csv, expected PASS 1.23 A (unchanged row, label added 13 Nov): ILIM pin limit from R11 read from parts.csv: KILIM minimum 320 / R11 (p9) must not be the binding limit below the 500 mA register default |
| C2.5 | charge.ce_poweron_min | >= | 1.3 | V | SIMULATED. CE node (U2 pin 9 = U1 IO18 = R21 pin 1) at power-on, R21 from parts.csv to 3V3 at its lowest allowed 3.0 V (ESP32-S3-MINI-1 p27), module pin not driven but with its internal weak pull-down 45 kohm (p27, worst case), CE input leakage 1 uA (BQ25895 p10 IIN_BIAS) and pin leakage 50 nA (p27). Against the charger's input high threshold VIH 1.3 V (BQ25895 p10, pins OTG, CE, PSEL, QON). Replaces old C2.1 to C2.3 for the case circuit with R21 on 3V3 | expected PASS, about 2.446 V |
| C2.6 | charge.icc_poweron_max | <= | 1e-6 | A | SIMULATED level through a DATASHEET FACT rule: charging needs CE low (BQ25895 p4 Table 6-1 and p21: "Battery charging is enabled when CHG_CONFIG = 1 and CE pin = Low"). The deck lets the charger charge with its power-on defaults (2.048 A, 4.208 V) only when V(CE) is below VIH 1.3 V; the charge current is taken from the same current-source model as the old C2.3 (input power with 500 mA input limit, converter efficiency 0.90 MODEL CHOICE). 1 uA is the numerical zero | expected PASS, 0 A |
| C2.7 | charge.ce_low_max | <= | 0.4 | V | SIMULATED circuit with a DATASHEET FACT level: the software drives IO18 low; the module pin low level VOL at most 0.1 x VDD = 0.36 V at VDD 3.6 V (ESP32-S3-MINI-1 p27), R21 from parts.csv to 3V3 at 3.6 V; against the charger's input low threshold VIL 0.4 V (BQ25895 p10). So that the software CAN start charging | expected PASS, 0.36 V (margin 0.04 V) |
| C2.8 | charge.ichg_written | <= | 0.350 | A | DATASHEET FACT, not a circuit result: REG04 ICHG code written by the case software (code read from design/ecad/case/sch-notes.md section 9: 0000010) times the register step 64 mA (BQ25895 p36 Table 8-12, bit weights 4096 to 64 mA, offset 0; cross-check: default code 0100000 gives 2048 mA); against the cell's allowed maximum 0.5 C = 350 mA (cell sheet p1). A register value cannot be proven by a circuit simulation | expected PASS, 0.128 A |
| C2.9 | charge.ichg_code_max_written | <= | 0.350 | A | DATASHEET FACT: highest ICHG code the software rule allows (sch-notes section 9: never above 0000101) times 64 mA (p36); against 350 mA | expected PASS, 0.320 A |
| C2.10 | charge.vreg_written | <= | 4.2 | V | DATASHEET FACT: REG06 VREG code written (sch-notes section 9: 010110) gives 3.840 V + code x 16 mV (BQ25895 p38 Table 8-14, offset 3.840 V, bit weights 512 to 16 mV; cross-check: default code 010111 gives 4.208 V); against the cell's charge voltage 4.2 V (cell sheet p1) | expected PASS, 4.192 V |
| C2.11 | charge.vreg_default | > | 4.2 | V | DATASHEET FACT kept visible: the power-on charge voltage 4.208 V (code 010111, p38) EXCEEDS the cell's 4.2 V. This row holds when the fact is true; it is the reason CE is held high (C2.5, C2.6) | expected PASS, 4.208 V |
| C2.12 | charge.ichg_reg_default | > | 0.350 | A | DATASHEET FACT kept visible: the power-on charge current 2.048 A (code 0100000, p36) EXCEEDS the cell's 350 mA | expected PASS, 2.048 A |
| C2.13 | charge.icc_default_ce_low | > | 0.350 | A | SIMULATED with MODEL CHOICE efficiency 0.90: charge current the charger would push into the cell with the defaults if CE were low (module pin driven low), 5 V input, 500 mA input limit: what R21 prevents. Same quantity as old C2.3, which was 0.602227 A | expected PASS, about 0.602 A |
| C3.1 | ts.cold_edge_rth_low | >= | 27.28e3*0.95 | ohm | thermistor resistance at which VTS falls to V(LTF) = 73.25 percent of REGN, RT1 and RT2 read from parts.csv, TH1 swept; TI's 0 C value is 27.28 kohm (p23), tolerance band 5 percent (own choice) |
| C3.2 | ts.cold_edge_rth_high | <= | 27.28e3*1.05 | ohm | same quantity, upper side |
| C3.3 | ts.hot_edge_rth_low | >= | 4.91e3*0.95 | ohm | thermistor resistance at which VTS falls to V(TCO) = 44.75 percent of REGN; TI's 45 C value is 4.91 kohm (p23), same 5 percent band |
| C3.4 | ts.hot_edge_rth_high | <= | 4.91e3*1.05 | ohm | same quantity, upper side |
| C3.5 | ts.vts_25c_min | >= | 0.4825 | ratio | VTS / REGN with TH1 at its nominal 10 kohm (parts.csv) must lie between V(HTF) and V(LTF) so that charging may start at 25 C |
| C3.6 | ts.vts_25c_max | <= | 0.7325 | ratio | same, upper side |
| C4.5 | led.red_current_min | >= | 0.002 | A | SIMULATED. LED1 anode on SYS (netlist), SYS at 3.5 V (BQ25895 minimum system voltage default, p35, lead range 3.5 to 4.35 V), R8 from parts.csv (510 ohm), U1 pin driven low modelled as 17.68 ohm = 0.495 V / 28 mA (ESP32-S3-MINI-1 p27 VOL and IOL), red die as the forward-current curve read from the Kingbright sheet p3 (points in case_decks.py, own graph readings, plus or minus 0.15 V) shifted by +0.15 V (the weakest corner). Limit 2 mA: 10 percent of the sheet's 20 mA test current (own choice for visible, unchanged from old C4.1). Replaces old C4.1 | expected PASS, about 2.7 mA |
| C4.6 | led.green_current_min | >= | 0.002 | A | SIMULATED, same, green die, R9 from parts.csv (270 ohm). Unchanged limit of old C4.2 | expected PASS, narrowly, about 2.05 mA |
| C4.7 | led.blue_current_min | >= | 0.002 | A | SIMULATED, same, blue die, R10 from parts.csv (270 ohm). Unchanged limit of old C4.3 | expected PASS, about 2.2 mA |
| C4.8 | led.max_current | <= | 0.020 | A | SIMULATED: largest current of the three colours with SYS at 4.35 V and the curve shifted by -0.15 V (the strongest corner), against the sheet's 20 mA test current. Unchanged limit of old C4.4 | expected PASS, about 5.5 mA |
| C4.9 | led.off_current_max | <= | 1e-5 | A | SIMULATED, rests on the curve start points: the three pins driven high at start-up (3V3 rail from R3 and R4 of parts.csv, 3.3075 V), SYS 4.35 V, curve shifted by -0.15 V: the LED sees at most SYS - 3V3 = 1.04 V, below the start of conduction of every curve (red 1.70 V, green 2.50 V, blue 2.40 V minus 0.15 V). The model has no current below the first curve point, so this row tests the headroom against the curve start, not a measured leakage (the sheet gives none). 10 uA is the numerical bound | expected PASS, 0 A |
| C5.1 | boost3v3.vout_min | >= | 3.0 | V | 3V3 rail from the feedback divider R3 and R4 read from parts.csv, VFB 0.5 V -1 percent (TPS63802 p6), against the ESP32-S3 supply minimum 3.0 V (p27) |
| C5.2 | boost3v3.vout_max | <= | 3.6 | V | same at VFB +1 percent against 3.6 V (p27) |
00:46:10

## Section D: case tests rewritten for the case circuit of 13 Nov (written BEFORE the run that judges them; time stamp on the last line of this section)

Why: lead-decisions.md line 34 (row "sim findings 2 and 3, as built into the case circuit"): CE is pulled to 3.3 V by R21; the status light anode is on SYS with R8 510 ohm and R9, R10 270 ohm. The rows above that are replaced (C2.1 to C2.3, C4.1 to C4.4) are kept below under the ids old-C2.1 and so on; they are no longer read by the bench. No limit of a surviving row was changed: the 2 mA and 20 mA limits of the LED rows are the old limits; the 350 mA and 4.2 V limits are the old ones too, now applied to what the software writes (DATASHEET FACT rows) and no longer to the chip's power-on defaults (which still exceed them: C2.11, C2.12 show it). The column after the source is the result I expected before any run of these rows.

Each new row says in its source cell whether it is SIMULATED (a circuit result of the deck) or a DATASHEET FACT (a number from a maker's sheet, not a circuit result; a register value cannot be proven by a circuit simulation).

Expected for the broken copies (written before they run): broken_case2_ce_gnd (R21 pin 2 moved from 3V3 to GND in netlist.csv): C2.5 FAILS (CE at 0 V) and C2.6 FAILS (0.602 A); C2.7 to C2.13 hold. broken_case4_anode_3v3 (LED1 pin A moved from SYS to 3V3 in netlist.csv): C4.6 and C4.7 FAIL (green and blue about 1.6 to 1.7 mA at 3.3 V); C4.5, C4.8, C4.9 hold.

| id | qty | op | limit | unit | source | expected |
|---|---|---|---|---|---|---|
| old-C2.1 | charge.vreg_default | <= | 4.2 | V | BQ25895 power-on charge voltage 4.208 V (p38) against the cell's charge voltage 4.2 V (cell sheet p1). CE is held low by R21, so charging starts with these register values until firmware writes REG06 (case risk 8) |
| old-C2.2 | charge.ichg_reg_default | <= | 0.350 | A | BQ25895 power-on charge current 2.048 A (p36) against the cell's allowed maximum 0.5 C = 350 mA (cell sheet p1) |
| old-C2.3 | charge.icc_input_limited_max | <= | 0.350 | A | charge current with the default input limit 500 mA (REG00 default, p32), 5 V, no other load, converter efficiency 0.90 (MODEL CHOICE, the sheet gives curves only), against 0.5 C = 350 mA |
| old-C4.1 | led.red_current_min | >= | 0.002 | A | LED current with the pins low, LED supply 3V3 and R8 470 ohm from the files, typical forward voltage 2.0 V at 20 mA; limit is 10 percent of the sheet's 20 mA test current (own choice for "visible", stated) |
| old-C4.2 | led.green_current_min | >= | 0.002 | A | same for green, R9 150 ohm, typical 3.3 V at 20 mA; best case over n = 2 to 4 |
| old-C4.3 | led.blue_current_min | >= | 0.002 | A | same for blue, R10 150 ohm, typical 3.3 V at 20 mA; best case over n = 2 to 4 |
| old-C4.4 | led.max_current | <= | 0.020 | A | no LED above the sheet's 20 mA test current (the sheet's absolute maximum was not read; 20 mA is the figure all its columns use) |

Time stamp of section D (command date, rows and expectations written before the case2 and case4 decks were changed and before any run that judges them): 16:17:27 CET

## Section C: ring test 8, supply ripple at a microphone (rows written before the deck of test 8 was built or run; time stamp on the last line)

Request of the lead (message 2026-11-13 after 01:17): 1.0 nF at the Vdd pin (C35 from parts.csv) and the 1 uF part (C31) behind a track of 2 mm and 5 mm; track 0.5 nH per mm (lead's figure) and the resistance of copper 0.10 mm wide, 0.018 mm thick: R = 1.68e-8 ohm m x length / (0.10e-3 m x 0.018e-3 m) = 9.33 mohm per mm (resistivity 1.68e-8 is the standard value for copper, not from a file). Microphone current: Knowles SPK0641HT4H-1 supply current 630 uA typical, 710 uA maximum at 1.8 V (design/datasheets/w1b_knowles_spk0641ht4h-1_chipdip.pdf p2, text copy src/knowles_spk0641.txt lines 183 and 184, test clock 2.4 MHz); worst case modelled as a square current between 0 and 2 x 710 uA = 1.42 mA at 1.536 MHz, 50 percent duty. Upstream of C31: C86 (from parts.csv) at the LDSW1 output with the switch resistance RDSONLS 200 mohm (nPM1304 p69) from an ideal 1.8 V. One microphone is modelled; the second is not added. The microphone sheet gives no ripple limit; 10 mV peak to peak is the lead's limit.

| id | qty | op | limit | unit | source |
|---|---|---|---|---|---|
| R8.1 | mic.ripple_2mm | <= | 0.010 | V | peak to peak at the Vdd pin, track 2 mm; lead's limit |
| R8.2 | mic.ripple_5mm | <= | 0.010 | V | same, track 5 mm |
01:18:40
