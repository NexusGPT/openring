### 8.1 nPM1304 settings (devicetree, Zephyr nPM13xx drivers)

The power chip is the Nordic nPM1304, U2, order code nPM1304-CAAA-R7 (architecture 17.13 and 17.18). Drivers: the Zephyr nPM13xx family `drivers/mfd/mfd_npm13xx.c`, `drivers/regulator/regulator_npm13xx.c`, `drivers/sensor/nordic/npm13xx_charger/npm13xx_charger.c` [SRC 11]. Fuel gauge: nRF Connect SDK library `nrf_fuel_gauge` [SRC 12]. The only nPM1304 binding text on disk is the charger page as quoted in `design/parts/research-npm1304.md` [SRC 17]; it confirms the compatible `"nordic,npm1304-charger"` and the properties `current-microamp`, `term-microvolt` and `term-current-percent`. Every other property name below is the F4 name of the same nPM13xx driver family and is marked **TO CONFIRM**: the firmware designer reads the nPM1304 binding files of the nRF Connect SDK version the build pins before work item W1 (section 10.5, item 3). Where the chip function behind a property is confirmed by the specification, the page is given. No property is added that F4 did not have.

| Block | Setting | Value | Source of the property |
|---|---|---|---|
| Power chip node | `compatible`, bus, address | compatible of the MFD node TO CONFIRM; on `i2c22` at 400 kHz; 7-bit address 0x6B (110 1011) | address and "I2C compatible up to 400 kHz" [NPM p120]; compatible TO CONFIRM |
| | `host-int-gpios` | P1.28 (PMIC_INT), active high | TO CONFIRM |
| | `pmic-int-pin` | 0 (nPM1304 GPIO0, ball D6, drives PMIC_INT, netlist.csv) | TO CONFIRM |
| | `ship-to-active-time-ms` | 96 (the chip's default SHPHLD press time tshipToActive [NPM p117]; SHPHLD is on test pad TP19 and is not used in the field) | TO CONFIRM |
| BUCK1 (VDD_1V8) | `regulator-init-microvolt`, `regulator-boot-on`, `regulator-always-on` | 1,800,000; on; on (VSET1 47 kilo-ohm sets 1.8 V in hardware, architecture 17.18) | TO CONFIRM |
| | `regulator-initial-mode` | `NPM13XX_BUCK_MODE_AUTO` | TO CONFIRM |
| BUCK2 (VDD_3V0) | `regulator-init-microvolt`, `regulator-boot-on`, `regulator-always-on` | 3,000,000; on; on (VSET2 150 kilo-ohm sets 3.0 V in hardware, architecture 17.18) | TO CONFIRM |
| | `regulator-initial-mode` | `NPM13XX_BUCK_MODE_AUTO` | TO CONFIRM |
| LDSW1 (VDD_MIC, ball A4 LSOUT1) | `regulator-initial-mode` | `NPM13XX_LDSW_MODE_LDSW` (load switch) | TO CONFIRM |
| | `soft-start-microamp`, `active-discharge`, `regulator-boot-off` | 25,000; on; off at boot | soft-start levels 25, 50, 75, 100 mA and active discharge exist [NPM p77]; names TO CONFIRM |
| LDSW2 (VDD_SD, ball A5 LSOUT2) | `regulator-initial-mode` | `NPM13XX_LDSW_MODE_LDSW` | TO CONFIRM |
| | `soft-start-microamp`, `active-discharge`, `regulator-boot-off` | 50,000; on; off at boot | as LDSW1 [NPM p77]; names TO CONFIRM |
| Charger | `compatible` | `"nordic,npm1304-charger"` | [SRC 17] |
| | `term-microvolt` | 4,350,000 (4.35 V, the cell's type: architecture section 2; register BCHGVTERM value 9 = 4.35 V [NPM p36]; range 3.60, 3.65 and 4.00 to 4.65 V in 50 mV steps [NPM p29]) | [SRC 17] |
| | `current-microamp` | `CHARGE_CURRENT` = 15,000 (15 mA, architecture 17.13: 1 C of the smallest cell of the range, kept until the cell's maker states its own limit, open item S12). The chip takes 4 to 100 mA in 0.5 mA steps [NPM p24, p29]. On the smallest cell, 18.2 mAh (US 7), 15 mA is 0.82 C; on the largest, 32.9 mAh (US 13), 0.46 C [CALC: 15 / 18.2, 15 / 32.9]. With the chip's accuracy of plus or minus 10 % [NPM p29] the current is 13.5 to 16.5 mA, at most 0.91 C on 18.2 mAh [CALC: 16.5 / 18.2] | [SRC 17] |
| | `term-current-percent` | 10 (charging ends when the current falls under 10 % of `CHARGE_CURRENT`, 1.5 mA [CALC: 0.10 x 15]; the chip offers 10 %, the default, or 5 % [NPM p37, register BCHGITERMSEL]) | [SRC 17] |
| | `trickle-microvolt` | 2,900,000 (the default; the other value is 2.5 V [NPM p37, BCHGVTRICKLESEL]) | TO CONFIRM |
| | `vbus-limit-microamp` | 500,000 (VBUS input current limit; the chip limits at 100 mA or 500 mA, 95 mA and 495 mA minimum [NPM p17]) | TO CONFIRM |
| | `thermistor-ohms`, `thermistor-beta` | 10,000 (RT1, 10 kilo-ohm, on the nPM1304 NTC pin, ball D3, netlist.csv; where RT1 sits is hardware issue H12), 3,380 (B25/50 of the 10 kilo-ohm type the chip supports [NPM p24, Table 10]; the RT1 part must match it, section 10.5) | TO CONFIRM |
| | `thermistor-cold-millidegrees` | 0 (no charging at or under 0 °C) | limits settable from -20 to +60 °C [NPM p24]; TO CONFIRM |
| | `thermistor-cool-millidegrees` | 10,000 (cool region from 0 to 10 °C; the chip halves the charge current there, to 7.5 mA [NPM p25, Table 12; CALC: 0.5 x 15]) | TO CONFIRM |
| | `thermistor-warm-millidegrees` | 40,000 (warm region from 40 to 45 °C; full current, reduced termination voltage [NPM p25, Table 12]) | TO CONFIRM |
| | `thermistor-hot-millidegrees` | 45,000 (no charging at or over 45 °C) | TO CONFIRM |
| | `term-warm-microvolt` | 4,100,000 (charge voltage in the warm region, register BCHGVTERMR [NPM p36]) | TO CONFIRM |
| | `charging-enable` | on whenever VBUS is present (rule R-CHG, section 1.2; action "charge on" in every row into `CHARGING`; register BCHGENABLESET [NPM p22]) | TO CONFIRM |
| | `dietemp-stop-millidegrees`, `dietemp-resume-millidegrees` | 90,000, 80,000 (kept from F4; the chip's defaults are 110 °C and 100 °C [NPM p29]; 90 and 80 °C are rows of its example table [NPM p26, Table 13]) | TO CONFIRM |
| Battery discharge limit | none | the nPM1304 has no setting for it: its battery current limit IBATLIM is fixed (section 8.7). F4's discharge-limit row belonged to the older chip and is removed (architecture 17.22) | [NPM p28 to p30, p40] |

Charger rules (F5):
1. **Charging turns on.** Charging is on in every state where VBUS is present (R-CHG, section 1.2). First power: the nPM1304 leaves ship mode on VBUS (section 8.4) and `BOOT` turns the charger on before it mounts storage, so a ring leaving the factory charges the first time it sits in the case.
2. **`CHARGE_CURRENT` is one named constant**, set in one place, in microamps: 15,000. A build fails to compile when it is unset, above 18,200 (1 C of the smallest cell, 18.2 mAh, architecture 17.17), under 4,000 or over 100,000, or not a multiple of 500 [NPM p24]. The firmware disables the charger before it writes the current register and enables it after [NPM p24: "CHARGER must be disabled before changing the current setting in register BCHGISET"].
3. **Charge time per ring size** [CALC: capacity / 15 mA; this is the constant-current time, a lower bound: the constant-voltage end adds time until the current falls to 1.5 mA, and in the cool region the current is 7.5 mA and the time doubles]. The chip's charge timeout, 7 hours for constant current and constant voltage together [NPM p30], is above every row.

| Ring size | Battery (architecture 17.17) | Charge time at 15 mA from empty [CALC] |
|---|---|---|
| US 7 | 18.2 to 24.3 mAh | 1.21 to 1.62 hours |
| US 8 | 19.3 to 25.7 mAh | 1.29 to 1.71 hours |
| US 9 | 20.4 to 27.2 mAh | 1.36 to 1.81 hours |
| US 10 | 21.5 to 28.6 mAh | 1.43 to 1.91 hours |
| US 11 | 22.6 to 30.1 mAh | 1.51 to 2.01 hours |
| US 12 | 23.6 to 31.5 mAh | 1.57 to 2.10 hours |
| US 13 | 24.7 to 32.9 mAh | 1.65 to 2.19 hours |

4. **Leaving ship mode on first power stays** (row `SHIP`, VBUS appears, section 8.4): the exit is by VBUS only.
5. The thermistor limits and the die-temperature limits stop and resume charging by themselves (rows above); they are not a reason to hold the charger off.

### 8.2 What is on in each state

| State | VDD_1V8 | VDD_3V0 | VDD_MIC | VDD_SD | Screen supply (OLED_PWR_EN) | HFXO | Radio | Wake sources |
|---|---|---|---|---|---|---|---|---|
| `SHIP`, `OFF` | off | off | off | off | off | off | off | VBUS only (section 8.4) |
| `BOOT`, `RECOVERY` | on | on | off | on | on in `RECOVERY` | on | off | runs to completion |
| `STANDBY` | on | on | off | off | when the screen is on | when the radio runs | advertising | the 4 direction inputs (JOY_UP, JOY_DOWN, JOY_LEFT, JOY_RIGHT) and BTN_REC when `CENTRE_SOURCE` is `SW2`, PMIC_INT, GRTC timer, radio |
| `RECORDING` | on | on | on | on | when the screen is on | on | advertising | PDM blocks every 16 ms, as `STANDBY` |
| `CHARGING` | on | on | off | off | when the screen is on | when USB runs | off | PMIC_INT (VBUS removed, charge events), USB, inputs |
| `TRANSFER` | on | on | off | on | when the screen is on | on | off | USB, PMIC_INT, inputs |
| error states | on | on | off | off | when the screen is on | when the radio runs | per section 7.3 | as `STANDBY` |

Between events the application core sleeps in System ON idle (Zephyr idle thread); System OFF is not used, because the GRTC time and Bluetooth must keep running. The motor supply VMOT (U11) is on only while MOTOR is high, in any state; U11 stays on the cell and draws at most 1 µA when off, ship mode included (motor-drive.md section 2.7).

### 8.3 Battery measurement

- The nPM1304's system monitor measures the battery voltage, the battery current and the thermistor [NPM p99, section 7.1]. The charger sensor driver gives voltage, current and temperature channels (`SENSOR_CHAN_GAUGE_VOLTAGE`, `SENSOR_CHAN_GAUGE_AVG_CURRENT`, `SENSOR_CHAN_GAUGE_TEMP`) [SRC 11; that the family driver serves the nPM1304 is TO CONFIRM, section 10.5 item 3]. Each sample feeds `nrf_fuel_gauge_process()`, which returns the state of charge [SRC 12]; `nrf_fuel_gauge_tte_get()` and `nrf_fuel_gauge_ttf_get()` give time to empty and to full [SRC 12].
- **The motor's charge is added.** The chip measures the battery current inside its own path [NPM p99]; the motor draws from the cell through U11, outside that path (section 3.1). The motor player sums the charge of every pulse since the last sample (t_on x 80 mA + 10 ms x 175 mA per pulse, section 3.1; the allowance is an **[ESTIMATE]** until bench step B-M3 measures the start). The current fed to the gauge is I_fed = I_measured + Q_motor / t_sample, counted as a discharge [CALC example: one MF, 51.50 mA.s, in a 1 s sample adds 51.5 mA to that sample]. The sign the library expects for a discharge is TO CONFIRM (section 10.5, item 32). U11 is a linear regulator, so its input current equals the motor current within its own small ground current (motor-drive.md section 2.5).
- Sampling: every 1 s in the recording states (thresholds use the mean of the last 10), every 60 s in the other awake states (thresholds use the single sample). Every sample also reads the battery current limit status (section 8.7).
- The battery current during a discharge has a full scale of 140 mA [NPM p99]; the chip path stays at or under 55.7 mA with every load on (architecture 17.22).
- The fuel gauge needs a battery model of the actual cells; Nordic makes it with its nPM PowerUP application [NPM p99]. One model per ring size or one for all is open (section 10.5, item 4).

### 8.4 Ship mode entry and exit (nPM1304 ship task after VBUS removal, [NPM p116])

The nPM1304 enters ship mode through its task register TASKENTERSHIPMODE [NPM p118]. Its specification states: "When VBUS is not present, the device enters Ship mode immediately. The host software must wait until EVENTSVBUSIN0SET on page 136 to ensure VBUS is disconnected and discharged before writing to the register" [NPM p116]. EVENTSVBUSIN0SET holds the event EVENTVBUSREMOVED, "VBUS removed" [NPM p136]. There is no timer: the firmware does not use hibernate (TASKENTERHIBERNATE), and F4's timed hibernate is removed.

Entry, in this order, for `SHIP` (FACTORY sub-commands SHIP_ENTER and SHIP_SAMPLE, section 9.3) and for `OFF` (menu "Power off", or B2):
1. Close everything (recording, storage, USB, radio, screen); save the settings and the time in RRAM. SHIP_ENTER first clears the factory flag; SHIP_SAMPLE keeps it at 1.
2. Write SHPHLDCONFIG with the default press time (96 ms) and trigger TASKSHPHLDCFGSTROBE: the specification requires both before ship mode [NPM p116, p118].
3. If VBUS is present, wait for the event EVENTVBUSREMOVED (register EVENTSVBUSIN0SET, [NPM p136]), reported on PMIC_INT. While it waits the ring does nothing else: no screen, no radio, no storage, the USB stack is disabled on `UDC_EVT_VBUS_REMOVED` (section 8.6). Only the factory commands reach this step with VBUS present: every row into `OFF` starts from a state without VBUS (section 1.2).
4. Write TASKENTERSHIPMODE = 1 [NPM p118]. The chip isolates the battery and the main chip loses its supply.
5. If the main chip still runs 1 s after step 4 **[CHOICE]**, it logs the event and goes back to step 3 once; the jig of section 9.3 sees advertising stop or not and reports a fail.

Exit: a voltage on VBUS above VBUSPOR, 3.9 V [NPM p17, p116]. Holding SHPHLD low for 96 ms also wakes the chip [NPM p116, p117], but SHPHLD sits on test pad TP19 (netlist.csv), which is closed under the board after assembly step 17, so in use only the case wakes the ring. After a wake the chip resets and sets the bit SHIPMODEEXIT in RSTCAUSE [NPM p146]; `BOOT` logs it (section 8.7).

Current in ship mode: 370 nA typical for the nPM1304 [NPM p11] plus U11, at most 1 µA (motor-drive.md section 2.7). The cell protection circuit's own drain is not stated (S12).

### 8.5 Expected current per state (architecture 17.15, 17.17 and 17.19, the current ring)

| | Recording | Standby |
|---|---|---|
| From the cell | about 4.1 mA [CALC: 4.0 + 2 x (0.63 - 0.58)] | about 0.03 mA |
| Hours on the smallest cell, 18.2 mAh at US 7 [CALC] | 4.4 | 607 (25.3 days) |
| Hours across US 7 to 13, 18.2 to 32.9 mAh [CALC] | 4.4 to 8.0 | 607 to 1,097 (25.3 to 45.7 days) |
| Hours at a Plaud's 13 mA, 18.2 to 32.9 mAh [CALC] | 1.4 to 2.5 | |

Recording current: architecture 17.15 and 17.17 use 4.0 mA, which counts the old microphones at 2 x 0.58 mA; the SPK0641HT4H-1 draws 0.63 mA at 1.8 V [DS line 97], so F5 uses 4.0 + 2 x (0.63 - 0.58) = 4.1 mA. This counts the 0.10 mA rise as if drawn from the cell, an over-count: through the 1.8 V rail it is 2 x 0.05 x 1.8 / (3.8 x 0.9) = 0.05 mA from the cell [CALC]. Recording hours: 18.2 / 4.1 = 4.44 and 32.9 / 4.1 = 8.02. At 13 mA: 18.2 / 13 = 1.40 and 32.9 / 13 = 2.53. Standby at 0.03 mA: 18.2 / 0.03 = 607 hours = 25.3 days and 32.9 / 0.03 = 1,097 hours = 45.7 days. Per ring size at 4.1 mA [CALC, `design/firmware-f5-notes.md`]:

| Ring size | Battery (architecture 17.17) | Recording hours at 4.1 mA |
|---|---|---|
| US 7 | 18.2 to 24.3 mAh | 4.44 to 5.93 |
| US 8 | 19.3 to 25.7 mAh | 4.71 to 6.27 |
| US 9 | 20.4 to 27.2 mAh | 4.98 to 6.63 |
| US 10 | 21.5 to 28.6 mAh | 5.24 to 6.98 |
| US 11 | 22.6 to 30.1 mAh | 5.51 to 7.34 |
| US 12 | 23.6 to 31.5 mAh | 5.76 to 7.68 |
| US 13 | 24.7 to 32.9 mAh | 6.02 to 8.02 |

Architecture 17.17 gives these hours at 4.0 mA (4.5 to 8.2 across the sizes); the difference is hardware issue H18.

Caveat, from architecture section 4 and 16.8: the main-chip, storage, radio and power-chip lines are estimates, not datasheet values, and bench test B2 replaces them; the microphone line is from the Knowles datasheet copy at its 2.4 MHz test clock, not at the ring's 1.280 MHz (section 10.5, item 6). The recording figure includes the recording light (1.50 mA at 3.0 V, section 3.2). It excludes the motor (section 3.1) and the screen. **Requirement P2 (10 hours of recording) is NOT met by this ring**: the owner chose thinness over hours on 2026-11-10 (architecture 17.5). In every state other than `RECORDING` the microphones and the light are off.

