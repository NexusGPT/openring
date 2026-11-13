# AI ring recorder: firmware architecture

Version F6, with F7 part 1 (2026-11-11): rulings R1 to R8 of firmware/docs/core-delta-1.md and R9 to R14 of firmware/docs/core-delta-2.md and R15, R16 in sections 1 and 2, and F7 part 2 (2026-11-11): section 7 rewritten for three paired devices and keyboard, media and pointer control; and F7 part 3 (2026-11-12, after design review 3): rulings R17 (the control session and the screens for control modes and paired devices: sections 2.1, 2.2, 3.3, 3.4, 7.4, 7.5), section 7.6 (Apple's notification, media and time services, from software step 3), R18 (the microphone factory tests run only with the screen fitted: section 9.3), R20 (ship beacon so the factory can prove ship mode: section 9.3) and R19 (the recording current reads 2.6 mA plus a 1.5 mA allowance for the lit sign: section 8.5); and F7 part 4 (2026-11-12, software step 4, the screens as built and the lead's rulings on its review `firmware/docs/step4-review.md`): the notification screens, the lock fact, the low-battery message and the fields of each screen (sections 1.2, 2.2, 3.1, 3.3, 3.4); and F7 part 5 (2026-11-12, software step 5): section 7.7, the relay service for notifications from a helper app; 2026-11-11. Follows `design/architecture.md` version A5-draft, sections 17.11 to 17.26 (read 2026-11-11: section 17 is the current ring; where sections disagree, the later section wins: 17.26 over 17.25 and so on down to 17.11, then 17.10, then 17.8 over 17.7, then 17.1 to 17.6, then 16, then the rest), `design/ecad/ring/sch-notes.md` section 12 (wiring A7) with `design/ecad/ring/netlist.csv`, `design/ecad/motor-drive/motor-drive.md` section 2, `design/mfg/assembly/assembly.md`, the nPM1304 Product Specification v1.0 (`design/datasheets/npm1304_datasheet_v1_0.txt`, page numbers are the document's own, written [NPM pN]), `design/case/case-architecture.md` (this file was written against case version C1; the case is now C5d, and its pad order VBUS, D-, D+, GND is the one this file uses; the rest of C5d was not re-read for this file) and `requirements.md`. The hardware is fixed; where it blocks a requirement, the conflict is in "Hardware issues found" at the end. The owner's rule that never changes: "The ring shouldn't CONSTANTLY record, only when a long press on it. Then you have a live storing audio". Ring sizes of version 1: "US 7 to 13" (owner, 2026-11-11).

Changes from F5 to F6 (2026-11-11; architecture 17.26: the inside model v6 measured the cell at every ring size; 17.25 moves the joystick on US 7 and US 8 and changes nothing in these rules; the figures and their arithmetic are in `design/firmware-f6-notes.md`):
1. **Measured cells** (17.26): US 7 17.6 to 23.5 mAh up to US 13 23.9 to 31.9 mAh replace the calculated cells of 17.17 (before: 18.2 to 32.9 mAh). The smallest cell is 17.6 mAh (sections 1.1, 3.1, 8.1, 8.5, 9.3, 10.5, H7, H8).
2. **Thresholds on 17.6 mAh**: B15 39 min, B5 13 min, B2 5 min at 4.1 mA (before: 40, 13, 5 min on 18.2 mAh) (section 1.1).
3. **Charge**: `CHARGE_CURRENT` stays 15,000 µA, 0.85 C of 17.6 mAh; the compile limit (1 C of the smallest cell) becomes 17,600 µA (before: 18,200); the charge time table follows the measured cells (section 8.1).
4. **Hours**: recording 4.3 to 7.8 hours, standby 24.4 to 44.3 days, a Plaud's 13 mA 1.4 to 2.5 hours across US 7 to 13 (section 8.5). The motor's place per size follows 17.26 (sections 3.1, 4.7). H18 closes: 17.26 computes the hours at 4.1 mA.
No behaviour changes: states, transitions, gestures, patterns and rules are those of F5.

Changes from F4 to F5 (2026-11-11; one item per point of the lead's brief; each names its source and the sections here; the figures and their arithmetic are in `design/firmware-f5-notes.md`):
1. **Power chip nPM1304** (architecture 17.13 and 17.18; [NPM] pages 24, 28 to 30, 36, 37, 40, 107 to 109, 116 to 120, 146; `design/parts/research-npm1304.md`; `design/mfg/assembly/assembly.md` section 3 K-A7 and section 6 changes 1 to 3). Every nPM1300 name and setting of F4 is replaced. (a) `CHARGE_CURRENT` = 15,000 µA (15 mA, 17.13), termination 4.35 V (register BCHGVTERM value 9, [NPM p36]), termination current 10 % ([NPM p37]); charge time per ring size from 17.17 (section 8.1). (b) The F4 discharge-limit setting is removed: the nPM1304 has none; its battery current limit IBATLIM is fixed, 100 mA minimum ([NPM p28 to p30]); the firmware reads the limiter status bit and acts (section 8.7). (c) Section 8.4 rewritten: ship mode by the ship task TASKENTERSHIPMODE after VBUS removal ([NPM p116]), no timed hibernate; new FACTORY sub-command SHIP_SAMPLE that enters ship mode and keeps the factory flag, for sample rings only (sections 1.2, 9.3). (d) Devicetree properties of the power chip: only those the nPM1304 binding confirms on disk stay plain; every other one is marked TO CONFIRM with who answers (section 8.1).
2. **Vibration motor on its own regulator U11** (architecture 17.16 and 17.22; `design/ecad/motor-drive/motor-drive.md` section 2.8 changes F1 to F5): MOTOR enables U11 through R61 and R62 (net MOT_EN); U11 feeds the motor on VMOT from the cell; up to 0.55 ms from MOTOR high to power; no PWM (section 3.1). The fuel gauge does not see the motor's charge, so the firmware adds it (section 8.3). Factory test T-MOTOR reads the battery voltage dip (section 9.3).
3. **Microphones Knowles SPK0641HT4H-1** (architecture 17.19; `design/mech/mic-path/mic-path.md` section 9 item 34; datasheet copy `design/mech/mic-path/datasheets/knowles-spk0641ht4h-1_chipsmall.txt`): the new part is 11 dB more sensitive (-26 dBFS against -37 dBFS at 94 dB SPL); the PDM gain stays 0 dB (register 0x28, as in F4), so the stored level rises by 11 dB and full scale moves from 131 to 120 dB SPL, the microphone's own overload point (lead's decision of 2026-11-11 on hardware issue H16); clock range, power-up time and current from the datasheet copy; recording current 4.0 + 2 x (0.63 - 0.58) = 4.1 mA (sections 4.1, 4.5, 5.3, 8.5).
4. **Battery per ring size** (architecture 17.15 and 17.17; since F6, 17.26): the measured cell is 17.6 to 23.5 mAh at US 7, 18.9 to 25.3 at US 8, 20.3 to 27.1 at US 9, 21.2 to 28.3 at US 10, 22.1 to 29.5 at US 11, 23.0 to 30.7 at US 12 and 23.9 to 31.9 mAh at US 13 (in F5, before the measurement, the calculated 18.2 to 24.3 up to 24.7 to 32.9 mAh). Minutes of every threshold use the smallest cell, 17.6 mAh (18.2 mAh before F6); every hours figure is a range across the sizes; every C-rate is recomputed (sections 1.1, 3.1, 8.1, 8.5, H7).
5. **Recording light** (architecture 17.21): no firmware change; R41 is 820 ohm for 1.50 mA (F4 wrote 680 ohm); the current budget keeps 1.5 mA (section 3.2). [v7: removed in v7 (architecture 17.30): the recording light, LED1, R41, Q2, the light guide LG1, the light pipe LP1 and the light window are out; the recording sign is the screen, section 3.2]
6. **Wiring A7** (`design/ecad/ring/sch-notes.md` section 12, `design/ecad/ring/netlist.csv`): nets VMOT and MOT_EN and part U11 are new, Q1 and D1 and the nets MOTOR_DRV and MOTOR_G are gone, the microphones have 8 pins (1 DATA, 2 CLOCK, 3 SELECT, 4 Vdd). Every chip pin named here is checked against `netlist.csv` by `firmware-check.py` (section 10.6).
7. **Assembly** (`design/mfg/assembly/assembly.md` steps 5, 18, 20, 21, 24, 25, 26, 27 and conflict K-A1): the factory flow of section 9.3 follows the steps (board stage, open ring, closed ring); K-A1 is applied: the USB update path cannot write the boot loader area (section 9.2); the first charge to 50 percent before ship mode is marked PROPOSED (section 9.3).
8. **Phone link** (architecture 18; `design/protocol/`): nothing of the link protocol enters F5. Section 7 gains one sentence at its top; sections 7.1 to 7.4 are those of F4.

`firmware-check.py` checks the F5 rules (section 10.6). The state machine, the gestures, the one-control rule, the recording rule and the hard-wired recording light are those of F4; the transition table gains one row (SHIP_SAMPLE) and has 61 rows. [v7: removed in v7 (architecture 17.30): the recording light, LED1, R41, Q2, the light guide LG1, the light pipe LP1 and the light window are out; the recording sign is the screen, section 3.2]

Changes from F3 to F4 (architecture A5-draft sections 17.11 and 17.12; owner, 2026-11-10: "I think we may not need a button on top of joystick and just have long press on joystick as recording button. So D1 but just joystick, no button"; each item names its section here):
1. **One control** (17.11): the separate record button is removed (no pill, no cap, no opening). The record gesture lives on the joystick's CENTRE press: long press 1.0 s starts a recording from standby, long press 1.0 s stops it, a short press while recording marks a highlight, a double press does nothing; a direction (up, down, toward the hand, toward the fingertip) never starts or stops a recording (sections 1.2, 2.1, 2.2). The owner's rule is unchanged: "The ring shouldn't CONSTANTLY record, only when a long press on it. Then you have a live storing audio". [v7: the record button is gone since 17.11 and the rectangular nub is removed in v7; the one control is the round joystick (architecture 17.29), centre switch SW2 (net BTN_REC)]
2. **Source of the centre press, both cases** (17.11): build constant `CENTRE_SOURCE` = `SW2` (a real switch on BTN_REC P0.04 under the nub's centre, the first choice) or `PAIR` (two opposite switches within 40 ms, 16.5, bench B6). One table row per case (section 2.1); every other rule holds for both. A long press held through a slight roll of the thumb does not end early (centre key latch, section 2.2). [v7: the record button is gone since 17.11 and the rectangular nub is removed in v7; the one control is the round joystick (architecture 17.29), centre switch SW2 (net BTN_REC)]
3. **Guard against accidental starts** (section 2.1): hold 1,000 ms (fixed by 17.11), a warning pulse MW at 500 ms, M1 at the start, release before 1,000 ms cancels; the short-press ceiling goes from 600 ms to 450 ms so a short press can never be buzzed; its cost is listed in section 2.1.
4. **Four collisions, the record gesture wins** (section 2.2): C1 the centre in SCR_RECORDING, C2 a long press in menu, settings, confirm and pairing screens, C3 the 400 ms window and the dead double press on menu screens, C4 the screen-off lock. The other F3 centre roles stay.
5. **Charging turns on** (review finding F05; 17.5, 17.6, `design/parts/research-charger.md`): the charger is on in every state where the pads carry power (rule R-CHG, section 1.2; action "charge on" in every row into `CHARGING`, section 8.1). The charge current is the named parameter `CHARGE_CURRENT`, still without a value (open item S12); the limit the cell imposes is at most 1 C, 15 to 20 mA; the nPM1300 cannot go below 32 mA, so the charger part is an open hardware choice and the rules hold for whichever is chosen (section 8.1, H8). Leaving ship mode on first power by VBUS stays.
6. **Charging pads on the inside of the band** (17.12): they touch the skin when worn. Section 8.6 states what the firmware does and does not do: VBUS is an input; nothing is driven onto the pads when no case is present. Section 6.1 follows 17.12.
7. Names that follow: the motor table gains MW (section 3.1); factory test T-BTN becomes T-CENTRE and T-JOY covers both centre cases (section 9.3); SCR_CONFIRM "Yes" text (section 3.3). The state and transition tables keep their column shapes and 60 rows; only event texts and actions change. `firmware-check.py` checks the F4 rules (section 10.6).

Changes from F2 to F3 (architecture A5-draft; each item names its architecture section):
1. **Two microphones on one stereo input** (16.4, 16.6): two Infineon IM68D128B, mic 1 on the left channel and mic 2 on the right channel of the one PDM instance `pdm20` (MIC_A_CLK, MIC_A_DATA). MIC_B_DATA P1.25 is an unused test pad. Pin P1.24 (ball E6, the former MIC_B_CLK) has no track and no test pad on the ring board: the 4-layer board leaves three balls unconnected (`design/wiring/ring-board-plan.md` section a.2). Removed: the second instance, the block pairing between instances, the PDM skew field and its test T-SKEW, microphone tests 3 and 4.
2. **Audio format** (16.6): 2 channels, 16 kHz, 16 bits, raw: 2 x 16,000 x 2 = 64,000 bytes per second, 230.4 MB per hour. A chunk keeps its 512 ms (8,192 frames) and so every time value of F2 (flush interval, 1.536 s worst-case loss, S30 at 3,516 chunks); its bytes halve: 1 header sector + 64 payload sectors = 33,280 bytes (was 129 sectors, 66,048 bytes). Sections 4.3, 5.2, 5.3, 5.4, 5.6, 6.3, 6.4 and 7.2 carry the new numbers. RAM budget 305,408 bytes (was 411,904).
3. **Storage 4 GB, about 16 hours** (16.4): CS Semiconductor CSNP32GCR01-BOW, SD NAND in SPI mode, 3.7 GB usable; 16.9 hours on 4,000,000,000 bytes and 15.6 hours on 3.7 GB (section 5.6). The wiring and the driver stack are those of F2.
4. **Joystick = four switches** (16.5, 16.6, 17.3): SW1 up on JOY_UP, SW3 down on JOY_DOWN, SW4 toward the hand on JOY_LEFT, SW5 toward the fingertip on JOY_RIGHT. A centre press is read when the two switches of an opposite pair close within 40 ms (section 2.2). The JOY_CENTER pin P0.03 is unused. Screens and menu keep their mapping.
5. **Record button = its own switch SW2 on BTN_REC** (17.3, 17.8): same gestures as F2 (long press 1.0 s starts, long press 1.0 s stops, short press marks a highlight, double press does nothing). [v7: the record button is gone since 17.11 and the rectangular nub is removed in v7; the one control is the round joystick (architecture 17.29), centre switch SW2 (net BTN_REC)]
6. **Vibration motor VC0720B088L** at full duty from the 3.0 V rail through Q1 (17.4): same patterns M1, M2, M3, MH, MT, MF; 85 mA maximum (section 3.1; the cell rate is hardware issue H7). **Replaced 2026-11-11 by architecture 17.16: the motor is the Jinlong W0525AB001D, below 80 mA running and below 175 mA at each start; the patterns and the pin are unchanged.**
7. **Battery about 15 to 20 mAh** (17.10, which corrects 17.8): thresholds B15, B5, B2 recomputed in minutes (section 1.1); recording hours at 4.0 mA: 3.8 to 5.0, and 1.2 to 1.5 hours at a Plaud's 13 mA (section 8.5). The 10-hour target (requirement P2) is not met (architecture 17.5).
8. **Charge current blocked** (17.5, 17.6): the power chip's minimum charge current, 32 mA, is above 1 C for this cell (1.6 to 2.1 C on 15 to 20 mAh). The charging states stay; the charge-current setting and the T-CHARGE limits are BLOCKED on open item S12 and no value is set (section 8.1). The charge voltage is 4.35 V, the cell's type (architecture section 2 and S12).
9. **Four pads on the band** (17.3, 17.8): the ring charges and transfers through VBUS, D-, D+, GND, 1.0 mm pads on the outside of the band (at -150 degrees in 17.8). The states `CHARGING` and `TRANSFER` stay; their text follows (sections 1.1, 6.1).
10. `firmware-check.py` checks the F3 rules that can be checked (section 10.6). Nothing else changes: no state, transition, gesture or pattern was redesigned.
11. **Correction of 2026-11-10 (21:30 work), architecture 17.10 wins over 17.8**: the cell is about 15 to 20 mAh (1.6 x 6.0 x 28.4 mm), not 19 to 25 mAh. Recomputed from it: recording 3.8 to 5.0 hours at 4.0 mA and 1.2 to 1.5 hours at 13 mA; capacity left and minutes at B15, B5, B2 (section 1.1); the 85 mA pulse is 4.3 to 5.7 C (section 3.1, H7); the charge minimum of 32 mA is 1.6 to 2.1 C (section 8.1, H8); standby 500 to 670 hours, 21 to 28 days (section 8.5); motor at +51 degrees (section 4.7).

Changes from F1 to F2 (kept as written in F2):
1. The recording light has no chip pin (architecture A2 section 9, W5): the F1 light output pin, its patterns and its pattern player are removed; section 3.2 states what the hardware does and what it costs. H4 is closed. [v7: removed in v7 (architecture 17.30): the recording light, LED1, R41, Q2, the light guide LG1, the light pipe LP1 and the light window are out; the recording sign is the screen, section 3.2]
2. Microphone clock 1.280 MHz with ratio 80 (H1) is accepted by the lead and written into architecture A3; H1 is closed.
3. Joystick and button use the chip's internal pull-ups (architecture W1). [v7: the record button is gone since 17.11 and the rectangular nub is removed in v7; the one control is the round joystick (architecture 17.29), centre switch SW2 (net BTN_REC)]
4. Charger temperature limits for thermistor RT1, 10 kilo-ohm on the nPM1300 NTC pin (H5 closed; section 8.1).
5. PMIC_INT is nPM1300 GPIO0 and SHPHLD sits on test pad TP19 (sch-notes section 2); ship mode is left by VBUS (H6 closed; the VBUS exit stays to confirm, section 10.5).
6. The case is a full-speed USB host (ESP32-S3-MINI-1): section 6.1 states what the Zephyr stack does with a full-speed host, sets 64-byte bulk packets for full speed, and recomputes the transfer time.
7. Contact pad order from -Y to +Y: VBUS, D-, D+, GND (section 6.1).
8. Motor noise rule: samples during each motor pulse and for 50 ms after it are marked in the chunk header (sections 4.7 and 5.3).
9. Schematic firmware rules (sch-notes section 9): microphone clocks held low while VDD_MIC is off (section 4.5), storage lines never driven high while VDD_SD is off (section 5.1), screen power sequence with OLED_PWR_EN and SWIRE (section 3.3).
10. `firmware-check.py` checks the new rules that can be checked (section 10.6).
11. **Owner decision** ("The ring shouldn't CONSTANTLY record, only when a long press on it"): day mode is removed completely. Removed states: `DAY_LISTEN`, `DAY_REC`, `VOICE_NOTE`; `MEETING_REC` is renamed `RECORDING`, the one recording mode (4 microphones, 1.280 MHz, ratio 80, 16 kHz, 16 bits, raw). Removed rules and parts: the speech detector (old section 4.4: high-pass, energy, noise floor, 12 dB / 6 dB / -60 dBFS thresholds, 5 of 8 trigger, 8 s hang time), the pre-roll ring (24,576 bytes) and pre-roll chunks, the detector state (2,048 bytes), the 640 kHz mono 8 kHz listening clock and the listening-to-recording mode switch gap, the 30-minute segment split, the day-mode menu item and setting, the voice-note function (long press in standby, 300 s limit, SCR_VOICE screen), the BLE "start meeting", "stop", "day mode on" and "day mode off" commands, the 1- and 2-channel chunk formats (recording types 2 and 3, sample rate 8,000, header fields pre-roll flag, gap_before_us, pre_roll_chunks), and the microphone check in the update self-test.
12. **New controls** (lead's reading of the owner): a long press (1,000 ms) starts a recording and a long press (1,000 ms) stops it; a short press during a recording marks a highlight; a short press outside a recording wakes the screen; a double press does nothing. A bump or short press never starts and never stops a recording. Removed: double press to start or stop.
13. VDD_MIC, and so the recording light, is on only in `RECORDING`, exactly while audio is stored (H3 closed; H2 closed with the removed state). Factory microphone tests are made as short test recordings. [v7: removed in v7 (architecture 17.30): the recording light, LED1, R41, Q2, the light guide LG1, the light pipe LP1 and the light window are out; the recording sign is the screen, section 3.2]
14. Light resistor 680 ohm (1.5 mA) and the recording current of 4.9 mA (27 hours) copied from architecture A3. RAM budget 411,904 bytes (was 438,528); worst-case loss on sudden power loss 1.536 s; `firmware-check.py` adds checks for the removed names, the microphone rail and the long-press rule. [v7: removed in v7 (architecture 17.30): the recording light, LED1, R41, Q2, the light guide LG1, the light pipe LP1 and the light window are out; the recording sign is the screen, section 3.2]

How to read this:
- Every item has one fixed choice. A value marked **[BENCH]** is fixed now and one named bench test can change it.
- **[SRC n]** = a fact read from a primary source; the list of sources is in section 10.4. A fact without [SRC] that is not a design choice is listed in section 10.5 as not verified.
- **[DS]** = from the Knowles SPK0641HT4H-1 datasheet Rev A, a third-party host's copy, text `design/mech/mic-path/datasheets/knowles-spk0641ht4h-1_chipsmall.txt` (line numbers of that text), the microphone of architecture 17.19.
- **[NPM pN]** = nPM1304 Product Specification v1.0, page N as printed (`design/datasheets/npm1304_datasheet_v1_0.txt`).
- **TO CONFIRM** = a name or value no file on disk confirms; section 10.5 names who answers.
- **[CALC]** = arithmetic shown on the line.
- Platform: nRF Connect SDK with Zephyr, application core of the nRF54LM20A (Cortex-M33, `cpuapp`) [SRC 1]. The FLPR RISC-V core is not used.
- All multi-byte fields are little-endian. All CRC-32 values are CRC-32/ISO-HDLC (polynomial 0x04C11DB7 reflected, init 0xFFFFFFFF, final XOR 0xFFFFFFFF), computed with Zephyr `crc32_ieee()`.

Peripheral instances (fixed), from the pin plan in `architecture.md` section 7 and the device file [SRC 1]:

| Function | Instance | Pins (architecture section 7) | Why this instance |
|---|---|---|---|
| Microphones 1 and 2 (one stereo input) | `pdm20` | MIC_A_CLK P1.13, MIC_A_DATA P1.11 | one instance serves both microphones on one clock and one data line (architecture 16.6); the chip's second PDM instance is not used [SRC 1] |
| Unused pins | none | MIC_B_DATA P1.25; pins P1.24 and P0.03 and balls F8, D6 and E9 not connected | P1.25 is a test pad since architecture 16.6: unused, the firmware never configures or reads it. P1.24 (ball E6, the former MIC_B_CLK) and P0.03 (ball H4, the former JOY_CENTER test pad) have no track and no test pad on the ring board (`design/wiring/ring-board-plan.md` section a.2; second routing round, `design/wiring/lead-decisions.md`); the firmware never configures them. Ring board round 3 (lead's decision of 2026-11-13, pin changes for routing; architecture section 7): ball F8 (the former spare pin with test pad TP8), ball D6 (LCD_TE before) and ball E9 (OLED_PWR_EN before) are not connected; P1.14 and P1.30 are no longer spare pins (their test pads TP9, TP11 are removed): they carry LCD_TE and OLED_PWR_EN; the firmware never configures the pins of balls F8, D6 and E9 |
| Storage | `spi00` (SPIM) | SD_SCK P2.01, SD_MOSI P2.02, SD_MISO P2.04, SD_CS P2.05 | only fast SPIM, 32 MHz maximum [SRC 1, SRC 3]; the development kit uses the same SCK, MOSI, MISO pins for `spi00` [SRC 9] |
| Screen | `spi21` (SPIM) | LCD_SCK P1.03, LCD_MOSI P1.04, LCD_CS P1.05, LCD_DCX P1.06 | port P1 instance; SPIM21 maximum data rate 8 Mbit/s [SRC 3] |
| Power chip | `i2c22` (TWIM) | PMIC_SDA P1.26, PMIC_SCL P1.27 | `i2c21` shares address 0xc7000 with `spi21` and cannot run at the same time [SRC 1]; `i2c22` is free |
| Debug log | `uart20` (UARTE), send only | DBG_TX P1.15; pin P1.16 (the former DBG_RX) not connected on the ring board | `uart20` shares 0xc6000 with `spi20`/`i2c20`, both unused |
| Joystick (round, five switches; architecture 17.29) | GPIO with the chip's internal pull-up (`GPIO_PULL_UP \| GPIO_ACTIVE_LOW`, architecture W1), Zephyr `gpio-keys` input driver | BTN_REC P0.04 (SW2), JOY_UP P0.06 (SW1), JOY_DOWN P0.07 (SW3), JOY_LEFT P0.08 (SW4), JOY_RIGHT P1.31 (SW5) | `gpio-keys` has `debounce-interval-ms` [SRC 14]; BTN_REC is the net of the centre switch SW2 (net BTN_REC) under the round cap when `CENTRE_SOURCE` is `SW2`, and unused (left as an input with the pull-up) when it is `PAIR` |
| Motor | GPIO output, active high | MOTOR P3.01 | the pin switches the motor regulator U11 on and off through R61 (net MOT_EN), so patterns in ms need no PWM (motor-drive.md, regulator U11) |
| Screen extras | GPIO | LCD_RST P1.07 (output), LCD_TE P1.14 (input, rising edge), OLED_PWR_EN P1.30 (output) | ring board round 3: LCD_TE moved from ball D6 to P1.14 (ball F4), OLED_PWR_EN from ball E9 to P1.30 (ball F9); balls D6 and E9 not connected (architecture section 7) |
| Power chip interrupt | GPIO input | PMIC_INT P1.28 | driven by the nPM1304's GPIO0 (ball D6, netlist.csv); `host-int-gpios` of the power chip node (property name TO CONFIRM, section 8.1) |
| USB | `usbhs` (DWC2 core, `nordic,nrf-usbhs-nrf54l`) | dedicated D+, D-, VBUS | [SRC 1, SRC 5] |
| 32.768 kHz crystal | LFXO | XL1 P1.20, XL2 P1.21 | |
| Time base | `grtc` | none | [SRC 1] |
| Watchdog | `wdt31` | none | [SRC 1] |

## 1. State machine

### 1.1 States

| State | Meaning | Microphones (VDD_MIC) | Storage (VDD_SD) | Screen | Radio |
|---|---|---|---|---|---|
| `SHIP` | factory ship mode of the nPM1304; the main chip has no power (when entered with VBUS present, the chip first waits for VBUS removal, section 8.4) | off | off | off | off |
| `OFF` | same ship mode, entered by the user or by an empty battery | off | off | off | off |
| `BOOT` | power-on: clocks, power chip setup, storage mount, superblock read | off | on | off | off |
| `RECOVERY` | the superblock says a recording was open at power loss: scan and close it | off | on | shows "Recovering" | off |
| `STANDBY` | idle, ready; nothing is captured | off | off | on for 5 s after input, else off | advertising |
| `RECORDING` | a recording is being stored: 2 channels (2 microphones), 16 kHz, 16 bits, raw | on | on | never dark: SCR_RECORDING for 3 s after any input, else SCR_REC_DIM, the red dot and the timer dimmed (rule R-SIGN, section 3.2) | advertising |
| `CHARGING` | VBUS present (ring in the case, on the four pads inside the band), USB not configured by the host | off | off | charging screen for 5 s after insertion | off |
| `TRANSFER` | VBUS present and USB configured by the case, over the four pads inside the band | off | on | transfer screen for 5 s, then off | off |
| `ERR_STORAGE_FULL` | free space at or under the reserve; recording refused | off | off | as `STANDBY` | advertising |
| `ERR_BATTERY_LOW` | battery at threshold B5; recording refused | off | off | as `STANDBY` | advertising |
| `ERR_STORAGE_FAULT` | storage did not initialise or a write failed after retries | off | off | error screen 10 s | advertising |
| `ERR_MIC_FAULT` | the PDM instance delivered no block for 100 ms while recording | off | off | error screen 5 s | advertising |
| `ERR_CHARGER` | the nPM1304 reported a charge error (register BCHGERRREASON, [NPM p41]) | off | off | error screen 10 s | off |
| `FACTORY_TEST` | factory test mode, driven over USB by the test jig; microphone tests make real recordings (section 9.3) | off (on only inside a test recording) | per test | per test | per test |

Rule (owner, F2): **the microphones and VDD_MIC are on only in `RECORDING`**, that is exactly while audio is being stored. Nothing is captured, analysed or buffered in any other state.

Battery thresholds (state of charge from the Nordic fuel gauge library, section 8.3, with the motor's charge added; voltage from the nPM1304 system monitor ADC [NPM p99], averaged over 10 s). Recomputed in F6 for the measured cells of ring sizes US 7 to 13, 17.6 to 31.9 mAh (architecture 17.26), and a recording current of 4.1 mA (section 8.5). A threshold protects a minimum of recording time, so its minutes are given on the smallest cell, 17.6 mAh at US 7 (architecture 17.26: "Every rule that protects a minimum of recording time uses the smallest cell: **17.6 mAh (US 7)**"):
- **B15**: state of charge at or under 15 %. Warning only.
- **B5**: state of charge at or under 5 %, or average voltage at or under 3.45 V. Recording stops; new recordings refused.
- **B2**: state of charge at or under 2 %, or average voltage at or under 3.30 V. Everything closes; the ring goes to `OFF`. 3.30 V stays above the nPM1304's power-fail reset, whose falling threshold VSYSPOF is 2.7 V by default and 3.4 V at most [NPM p109] (the default is kept), so the firmware closes files before the power chip resets. It must also stay above the cell protection circuit's undervoltage limit, which the cell maker has not stated (open item S12).
- The percentages stay 15, 5 and 2: they are shares of the cell, so the cell size changes what they mean in time, not their value. Capacity left on the smallest cell [CALC]: B15 2.64 mAh, B5 0.88 mAh, B2 0.35 mAh (17.6 mAh times 15, 5 and 2 %). Time left at 4.1 mA on 17.6 mAh [CALC: 2.64 / 4.1 x 60 = 38.6, 0.88 / 4.1 x 60 = 12.9, 0.352 / 4.1 x 60 = 5.2]: B15 39 min, B5 13 min, B2 5 min. On the largest cell, 31.9 mAh at US 13, the same shares give B15 70 min, B5 23 min, B2 9 min [CALC: 4.785, 1.595 and 0.638 mAh / 4.1 x 60 = 70.0, 23.3 and 9.3]. Recording time from full at 4.1 mA: 4.3 to 7.8 hours across US 7 to 13 (section 8.5). The share is the fuel gauge's, whose model of these cells is not verified (section 10.5, item 26).

Storage thresholds (section 5.6): **S30** = free space at or under 30 minutes of audio (warning); **SFULL** = free space at or under the reserve of 16 chunks (stop).

### 1.2 Transitions

Common actions used in the table:
- **close** = write the partial chunk, write the index CLOSE record, write the superblock with the open flag cleared, stop PDM, clocks low, VDD_MIC off, VDD_SD off.
- **open** = VDD_SD on, mount, write the superblock with the open flag set and the new recording id, VDD_MIC on, start PDM (section 4.5 sequence).
- **M1, M2, M3, MH, MT, MF** = motor patterns of section 3.1.
- **long press** = the joystick centre held 1,000 ms (section 2.1). **short press** = the centre held 40 to 450 ms with no second press in the 400 ms window. **double press** = two short presses (section 2.1).
- **charge on** = the charger is enabled and set to `CHARGE_CURRENT` (section 8.1); if it is already on, nothing changes. **charge off** = the charger is disabled.

| From | Event | To | Actions |
|---|---|---|---|
| `SHIP` | VBUS appears (case contact) | `BOOT` | the nPM1304 leaves ship mode (VBUS above VBUSPOR, 3.9 V [NPM p17, p116]) and powers the bucks; the chip starts; charge on |
| `OFF` | VBUS appears | `BOOT` | as above, including charge on |
| `BOOT` | init done, superblock open flag clear, no VBUS, battery above B5 | `STANDBY` | VDD_SD off |
| `BOOT` | init done, superblock open flag set | `RECOVERY` | keep VDD_SD on |
| `BOOT` | init done, VBUS present | `CHARGING` | VDD_SD off; charge on |
| `BOOT` | storage init fails 3 times, 200 ms apart | `ERR_STORAGE_FAULT` | log event; MF |
| `BOOT` | battery at B2 and no VBUS | `OFF` | enter ship mode (section 8.4) |
| `BOOT` | battery at B5 and no VBUS | `ERR_BATTERY_LOW` | VDD_SD off; M3 (ruling R13) |
| `RECOVERY` | scan done, no VBUS | `STANDBY` | write index CLOSE record with state RECOVERED; clear open flag; VDD_SD off |
| `RECOVERY` | scan done, VBUS present | `CHARGING` | same actions; charge on |
| `RECOVERY` | read error during scan | `ERR_STORAGE_FAULT` | log event; MF |
| `STANDBY` | long press of the joystick centre | `RECORDING` | only with the superblock open flag clear, the battery above B5, free space above SFULL and the recording sign drawn (rulings R1, R4b; rule R-SIGN, section 3.2; otherwise the next four rows, in their order): M1; open (ruling R21: M1 starts at the press, before storage is opened, as section 4.4 says) |
| `STANDBY` | long press, superblock open flag set | `RECOVERY` | no recording starts (ruling R4b: a recording never starts while the open flag is set); VDD_SD on; mount; `RECOVERY` scans and closes the unfinished recording; the wearer presses again |
| `STANDBY` | long press of the joystick centre, battery at B5 | `STANDBY` | no recording starts; screen "Battery low" 3 s (ruling R1) |
| `STANDBY` | long press of the joystick centre, free space at SFULL | `STANDBY` | no recording starts; screen "Storage full" 3 s (ruling R1) |
| `STANDBY` | long press of the joystick centre, recording sign not drawn | `STANDBY` | no recording starts: the screen did not accept the red dot and the timer (rule R-SIGN, section 3.2); VDD_MIC stays off; M3; event log record |
| `STANDBY` | short press of the joystick centre | `STANDBY` | screen off: screen on, status screen, 5 s; screen on: the centre action of the screen (section 2.2), then MT (ruling R6) |
| `STANDBY` | double press of the joystick centre | `STANDBY` | nothing; with a control session open it closes the session (ruling R17, section 3.4) |
| `STANDBY` | menu "Power off" confirmed | `OFF` | save settings and time; M2; ship mode |
| `STANDBY` | VBUS appears | `CHARGING` | charge on |
| `STANDBY` | battery reaches B15 | `STANDBY` | M3 once per discharge; SCR_MESSAGE "Battery low" for 5 s (F7 part 4: the status screen no longer shows the battery). While SCR_PAIR is shown or a control session is open nothing is shown, and neither the pairing window nor the session is touched; M3 is then the warning |
| `STANDBY` | battery reaches B5 | `ERR_BATTERY_LOW` | M3 |
| `STANDBY` | battery reaches B2 | `OFF` | save settings and time; ship mode |
| `STANDBY` | free space at SFULL | `ERR_STORAGE_FULL` | M3 |
| `STANDBY` | storage fault set at entry (rule R-STB) | `ERR_STORAGE_FAULT` | none; the 60 s retry starts (ruling R11) |
| `RECORDING` | long press of the joystick centre | `STANDBY` | close; M2 |
| `RECORDING` | short press of the joystick centre | `RECORDING` | highlight marker; MH; screen 3 s with highlight count |
| `RECORDING` | double press of the joystick centre | `RECORDING` | nothing (no highlight, no stop); with a control session open it closes the session (ruling R17, section 3.4) |
| `RECORDING` | BLE control "highlight" from a bonded phone | `RECORDING` | highlight marker; MH |
| `RECORDING` | VBUS appears (case insertion during a recording) | `CHARGING` | close; M2; charge on |
| `RECORDING` | battery reaches B15 | `RECORDING` | M3 once per discharge |
| `RECORDING` | battery reaches B5 | `ERR_BATTERY_LOW` | close; M3 |
| `RECORDING` | battery reaches B2 | `OFF` | close; ship mode |
| `RECORDING` | free space reaches S30 | `RECORDING` | M3 once; screen 3 s "30 min left" |
| `RECORDING` | free space at SFULL | `ERR_STORAGE_FULL` | close; M3 |
| `RECORDING` | chunk write fails 3 times | `ERR_STORAGE_FAULT` | stop PDM; clocks low; VDD_MIC off; superblock left open (RECOVERY at next boot); MF |
| `RECORDING` | the PDM instance gives no block for 100 ms | `ERR_MIC_FAULT` | close; MF |
| `RECORDING` | sudden power loss (cell cut, short, brown-out) during a write | `BOOT` | nothing runs; at the next power-on the open flag leads to `RECOVERY`; loss bounded in section 5.5 |
| `CHARGING` | USB configured by the case (`USBD_MSG_CONFIGURATION`) | `TRANSFER` | VDD_SD on; mount; charge on stays |
| `CHARGING` | VBUS removed, free space above SFULL, battery above B5 | `STANDBY` | none |
| `CHARGING` | VBUS removed, free space at SFULL, battery above B5 | `ERR_STORAGE_FULL` | none (ruling R2: with the battery at B5 the next row applies) |
| `CHARGING` | VBUS removed, battery at B2 | `OFF` | save settings and time; ship mode (ruling R10) |
| `CHARGING` | VBUS removed, battery at B5 | `ERR_BATTERY_LOW` | none |
| `CHARGING` | nPM1304 event charge error | `ERR_CHARGER` | log BCHGERRREASON and BCHGERRSENSOR [NPM p41]; charge off; MF |
| `CHARGING` | long press | `CHARGING` | refused: M3; screen "In case" 3 s; charge on stays |
| `TRANSFER` | USB suspended or unconfigured by the case | `CHARGING` | finish the current command; VDD_SD off; charge on |
| `TRANSFER` | VBUS removed | `STANDBY` | abort the command; VDD_SD off |
| `TRANSFER` | command FW_END accepted | `BOOT` | `boot_request_upgrade(BOOT_UPGRADE_TEST)`; reboot (section 9.2) |
| `TRANSFER` | command FACTORY_ENTER with the factory flag set | `FACTORY_TEST` | section 9.3 |
| `TRANSFER` | long press | `TRANSFER` | refused: M3 |
| `ERR_STORAGE_FULL` | VBUS appears | `CHARGING` | charge on |
| `ERR_STORAGE_FULL` | long press | `ERR_STORAGE_FULL` | refused: M3; screen "Storage full" 3 s |
| `ERR_STORAGE_FULL` | battery reaches B5 | `ERR_BATTERY_LOW` | M3 |
| `ERR_STORAGE_FULL` | battery reaches B2 | `OFF` | ship mode |
| `ERR_BATTERY_LOW` | VBUS appears | `CHARGING` | charge on |
| `ERR_BATTERY_LOW` | long press | `ERR_BATTERY_LOW` | refused: M3; screen "Battery low" 3 s |
| `ERR_BATTERY_LOW` | battery reaches B2 | `OFF` | save settings and time; ship mode |
| `ERR_STORAGE_FAULT` | VBUS appears | `CHARGING` | charge on; the case reads the event log (GET_LOG) |
| `ERR_STORAGE_FAULT` | 60 s elapsed | `ERR_STORAGE_FAULT` | retry storage: the caller runs the storage init and reports the result as an event (ruling R3; every 60 s while in this state; ruling R14: at most one try per call of the tick, whatever the delay, the next one 60 s after it) |
| `ERR_STORAGE_FAULT` | storage retry succeeds, superblock open flag set | `RECOVERY` | keep VDD_SD on; `RECOVERY` scans and closes the unfinished recording (ruling R9) |
| `ERR_STORAGE_FAULT` | storage retry succeeds, superblock open flag clear | `STANDBY` | none (rule R-STB applies) |
| `ERR_STORAGE_FAULT` | storage retry fails | `ERR_STORAGE_FAULT` | none; the next try comes 60 s later (ruling R3) |
| `ERR_STORAGE_FAULT` | battery reaches B2 | `OFF` | ship mode |
| `ERR_MIC_FAULT` | 5 s elapsed | `STANDBY` | the fault is in the event log |
| `ERR_MIC_FAULT` | VBUS appears | `CHARGING` | charge on |
| `ERR_MIC_FAULT` | battery reaches B2 | `OFF` | save settings and time; ship mode (ruling R15) |
| `ERR_CHARGER` | VBUS removed | `STANDBY` | none |
| `ERR_CHARGER` | battery reaches B2 | `OFF` | save settings and time; ship mode (ruling R15) |
| `FACTORY_TEST` | command FACTORY_EXIT | `BOOT` | reboot |
| `FACTORY_TEST` | command SHIP_ENTER | `SHIP` | clear the factory flag; ship mode (waits for VBUS removal, section 8.4) |
| `FACTORY_TEST` | command SHIP_SAMPLE (sample rings only) | `SHIP` | keep the factory flag; ship mode (waits for VBUS removal, section 8.4) |
| `FACTORY_TEST` | VBUS removed, no ship command accepted | `BOOT` | reboot |

The table has 72 transitions.

Rules that apply to every state:
- Only a long press of the joystick centre starts or stops a recording. A short press, a double press and a joystick direction (up, down, toward the hand, toward the fingertip) never start and never stop one; neither does Bluetooth or the case (the case only closes a recording by its VBUS, row "case insertion").
- **R-CHG (charging):** in every state where VBUS is present the charger is on at `CHARGE_CURRENT`. It is turned on by the first VBUS event (on first power, in `BOOT`, before storage is mounted) and by every row into `CHARGING`; the firmware turns it off only in the row `CHARGING` to `ERR_CHARGER`; otherwise only the charger itself stops it (full, thermistor limits, die temperature) or VBUS removal. The charge setting is in section 8.1. Ruling R8: charge on is sent on every appearance of VBUS, in every state, also where no row changes the state (`BOOT`, `RECOVERY`).
- **R-STB (entry into `STANDBY`, rulings R1, R11, R15):** every row from another state into `STANDBY` checks the facts first, in this order: battery at B2 with no VBUS goes to `OFF` (ruling R15); the storage fault set goes to `ERR_STORAGE_FAULT` (and so back to the 60 s retry); battery at B5 to `ERR_BATTERY_LOW`; free space at SFULL to `ERR_STORAGE_FULL`. It does so through the row of `STANDBY` for that fact ("battery reaches B2", "storage fault set at entry", "battery reaches B5", "free space at SFULL"), with that row's actions. This covers the rows `TRANSFER` VBUS removed, `ERR_STORAGE_FAULT` storage retry succeeds with the open flag clear, `ERR_MIC_FAULT` 5 s elapsed, `ERR_CHARGER` VBUS removed and `RECOVERY` scan done, no VBUS. The same order (B2 before B5) holds for every row that leaves `CHARGING` or `TRANSFER` when VBUS goes (ruling R10).
- **R15 (B2 with no VBUS, the lead's ruling):** with no VBUS, a battery at B2 always ends in `OFF`. The level is a fact, not only an event: on entry into any state (`STANDBY` through R-STB, `ERR_STORAGE_FAULT`, `ERR_STORAGE_FULL`, `ERR_BATTERY_LOW`, `ERR_MIC_FAULT`, `ERR_CHARGER`, and at "init done" or a failed storage init in `BOOT`) the core checks it first and, at B2 with no VBUS, takes that state's "battery reaches B2" row to `OFF` (a state without such a row gets one, with the same actions as the other B2 rows). The order of the entry checks is: B2, then the storage fault, then B5, then storage full. `RECOVERY` is the one exception already ruled (R4b: at B2 the ring goes `OFF` without recovery and the open flag stays set).
- **R16 (B2 when VBUS goes, the lead's ruling):** R15 holds at two moments, not one: on entry into a state, and whenever VBUS is removed, in every state. When VBUS goes and the battery is at B2, the ring takes that state's "battery reaches B2" row to `OFF`. This covers a ring that entered `ERR_STORAGE_FAULT` (or any state) in its case and is then taken out. A state that reacts to "VBUS removed" with its own row keeps that row; the B2 check comes first. In `CHARGING` the row "VBUS removed, battery at B2" is that check. A state with no "battery reaches B2" row (`TRANSFER`, `RECOVERY`, `FACTORY_TEST`) takes its own "VBUS removed" row, or none, and reaches `OFF` through the B2 check of the state it enters (R15, R-STB) or at the end of the scan (`RECOVERY`).
- **Storage fault (ruling R11):** the storage fault is a fact the core keeps. It is set on entering `ERR_STORAGE_FAULT` and cleared only by a successful storage init ("init done", "storage retry succeeds"). Leaving the case does not hide a broken storage.
- **Open flag (ruling R9):** the open flag is cleared only by two things: a successful close of a recording ("close") and "scan done" at the end of `RECOVERY` ("clear open flag"). Asking for recovery clears nothing. A read error during the scan goes to `ERR_STORAGE_FAULT` with the flag still set.
- **Order at "init done" (rulings R4, R5, R12, correction R4b):** battery events that arrive in `BOOT` before "init done" are not applied at once: the level is kept and this order decides; at B2 (no VBUS) the row "battery at B2 and no VBUS" (to `OFF`, no recovery: the open flag stays set and the next start-up recovers); else a start-up with an unfinished recording takes the row "init done, superblock open flag set" first (`RECOVERY`); at the end of the scan the battery rule applies: "scan done, VBUS present" goes to `CHARGING`, "scan done, no VBUS" enters `STANDBY` through rule R-STB (at B5 to `ERR_BATTERY_LOW`); else at B5 (no VBUS) the row "battery at B5 and no VBUS" (to `ERR_BATTERY_LOW`); else the row "init done, superblock open flag clear, no VBUS, battery above B5" or "init done, VBUS present". If the storage init fails instead (row "storage init fails 3 times"), a kept B2 with no VBUS runs the row "`ERR_STORAGE_FAULT`, battery reaches B2" (to `OFF`) on entering `ERR_STORAGE_FAULT` (ruling R15).
- **R4b (open flag):** a recording never starts while the superblock open flag is set. A long press in `STANDBY` with the flag set takes the row "long press, superblock open flag set" (to `RECOVERY`); the wearer presses again after the recovery.
- The watchdog (`wdt31`, 8 s) resets the chip when the system work queue that feeds it stops (section 9.4); a reset during a recording leaves the open flag set, so `BOOT` goes to `RECOVERY`.
- Only one recording is open at a time. A storage operation never runs while the case reads (USB `BUSY` status, section 6).

## 2. Controls

### 2.1 Record gesture: the centre press of the joystick (the one control; architecture 17.11)

The ring has one control, the joystick (owner, 2026-11-10: "I think we may not need a button on top of joystick and just have long press on joystick as recording button. So D1 but just joystick, no button"). The separate button of F3, its switch role and its cap are gone. The record gesture lives on the joystick's CENTRE press only; a direction (up, down, toward the hand, toward the fingertip) never starts and never stops a recording. How the ring reads a centre press is the table "Centre source" below and section 2.2. The gesture recogniser runs on the two events that reading produces, CENTRE_DOWN and CENTRE_UP, with times from the GRTC uptime in ms. Mapping (owner: "only when a long press on it"):

| Gesture | Timing | In `RECORDING` | In `STANDBY` | In every other state |
|---|---|---|---|---|
| Long press | the centre held 1,000 ms; fires at the 1,000 ms mark while still held, once per press; the release after it does nothing | stop the recording | start a recording (only with the open flag clear, the battery above B5 and free space above SFULL; otherwise recovery first, or the message "Battery low" or "Storage full", rulings R1, R4b) | refused with M3 (`CHARGING`, `TRANSFER`, `ERR_STORAGE_FULL`, `ERR_BATTERY_LOW`); ignored elsewhere |
| Short press | held 40 ms to 450 ms, and no second press begins within 400 ms of its release; fires when that window closes | highlight marker | screen off: screen on (status screen 5 s); screen on: the centre action of the screen (section 2.2) | screen off: screen on; screen on: the centre action of the screen (section 2.2) |
| Double press | two short presses, the second beginning 60 ms to 400 ms after the first release | does nothing; closes an open control session (ruling R17) | does nothing, on menu screens too; closes an open control session (ruling R17) | does nothing |
| Graze | held under 40 ms | ignored | ignored | ignored |
| Held 450 ms to 999 ms | | ignored (the pulse MW sounds at 500 ms) | ignored (the pulse MW sounds at 500 ms) | ignored |

| Parameter | Value |
|---|---|
| Debounce | 20 ms on every switch (`debounce-interval-ms = <20>`) |
| Long press | 1,000 ms hold, for start and for stop |
| Short press | 40 ms to 450 ms **[CHOICE]**: F3 had 600 ms; the ceiling sits under the 500 ms warning pulse so a short press can never be buzzed |
| Double-press window | 400 ms after a release; a second press starting 60 ms to 400 ms after it makes the pair a double press |
| Warning pulse | MW (section 3.1) at 500 ms of a continuous centre hold, in `STANDBY` and `RECORDING` **[CHOICE]**: half the hold, so the user has 500 ms to lift before anything happens; the Vibration setting never turns it off |
| Release hold-off | 30 ms **[CHOICE]**: longer than the 20 ms debounce so one contact bounce cannot fake a release, shorter than the 60 ms minimum gap of a double press |
| Direction decision window | 40 ms (architecture 16.5 gives it for the pair; the same value is used in case `SW2` **[CHOICE]**: one rule for both cases) |
| Event time of a highlight | the time of CENTRE_DOWN (used for the highlight marker) |

Centre source: build constant `CENTRE_SOURCE`, `SW2` by default (architecture 17.11 first choice; the rebuild of 17.12 must show that the switch fits under the centre of the round cap of 17.29) or `PAIR` (17.11 second choice). Every rule outside this table is the same for both cases.

| Case (`CENTRE_SOURCE`) | Input that reports a centre press | Debounce | Timing it needs |
|---|---|---|---|
| `SW2` | SW2 on BTN_REC P0.04, the centre switch SW2 (net BTN_REC), a real switch under the centre of the round cap: its debounced press edge is CENTRE_DOWN | 20 ms (`gpio-keys`) on SW2 and on each direction switch | a direction switch that closed 0 to 40 ms before SW2 is dropped and the centre wins; one that closed 40 ms or more before SW2 keeps its direction and SW2 is ignored until all switches are open; nothing else |
| `PAIR` | SW1 with SW3, or SW4 with SW5 (architecture 16.5, 17.3, bench B6): the two debounced press edges of an opposite pair inside 40 ms are CENTRE_DOWN, stamped at the second edge; BTN_REC P0.04 is unused | 20 ms on each of the four direction switches | the 40 ms decision window opened by the first switch (section 2.2); CENTRE_DOWN comes up to 40 ms after the first edge, so a start fires up to 40 ms later than in case `SW2` |

Guard against accidental starts. The round cap sits where the thumb rests, so a thumb at rest can hold the centre. The guard, in order:
- **G1** the hold is 1,000 ms (fixed by 17.11): nothing happens before it.
- **G2** at 500 ms of the hold the motor gives MW, one pulse, in `STANDBY` and in `RECORDING`; letting go before 1,000 ms cancels with no state change and no other effect.
- **G3** at 1,000 ms a start gives M1 and the recording sign, the red dot and the timer, is on the screen before VDD_MIC comes on (rule R-SIGN, section 3.2); a stop gives M2.
- **G4** a press that began as a direction, or in which a direction switch was already held, is never a centre press (section 2.2); a thumb rolling during a held centre does not end it (section 2.2).
- **G5** a press fires once; holding on after the start does not stop the recording, a new press is needed.
- Cost: the first 1.0 s of a meeting is not recorded (no audio is kept before the start, owner rule) plus the 50 ms discard of section 4.5, and up to 40 ms more in case `PAIR`; a start needs one still second of thumb; MW at 500 ms of a stop hold, and of any hold that passes 500 ms in `RECORDING`, is a motor pulse inside the audio, marked like every pulse (section 4.7); a short press longer than 450 ms is lost. Not guarded: a thumb that rests on the centre for a full second without lifting does start a recording, and the user is told by M1 and the red dot on the screen; the same press stops it.

Rules:
- **A short press, a double press or a direction never starts and never stops a recording.** Start and stop need the centre held for a full second.
- A highlight fires 400 ms after the release (when the double-press window closes), but its marker carries the time of CENTRE_DOWN.
- A press that begins inside the 400 ms window of an earlier short press cancels that short press and is judged on its own: short again, the pair is a double press (nothing happens, except that an open control session closes, ruling R17); held 1,000 ms, a long press from its own CENTRE_DOWN.
- In `CHARGING` and `TRANSFER` the long press is refused with M3.
- A long press always means start or stop (or refused); it never has a menu meaning.
- **Ruling R7:** a centre hold is cancelled by any change of state. The wearer must release and press again. A hold that began in `CHARGING`, `TRANSFER` or an error state never starts a recording, even if the ring leaves that state before the 1,000 ms mark.

### 2.2 Joystick (the round joystick of architecture 17.29, five switches under one round cap: SW1 up JOY_UP P0.06, SW3 down JOY_DOWN P0.07, SW4 toward the hand JOY_LEFT P0.08, SW5 toward the fingertip JOY_RIGHT P1.31, SW2 the centre (net BTN_REC); the centre press comes from SW2 or from an opposite pair, section 2.1; the JOY_CENTER pin is unused)

- Debounce 20 ms (`gpio-keys`), one event per press. Holding a direction for 500 ms repeats it every 150 ms.
- Names in the table below: Up = SW1, Down = SW3, Left = SW4 (toward the hand), Right = SW5 (toward the fingertip), Centre = a centre press (a short press of it, section 2.1).
- **Direction events.** A direction switch that closes (after the 20 ms debounce) opens a 40 ms decision window and sends nothing yet. If a centre press starts in the window (case `SW2`: SW2 closes; case `PAIR`: the opposite switch closes, rule below) the direction is dropped. If the window ends, or the switch is released first, with no centre press, the direction event is sent at that moment, so a direction event comes at most 40 ms after its press edge. After a direction event is sent, every other switch is ignored until all switches are open.
- **Centre key** (both cases). CENTRE_DOWN is the start of a centre press (section 2.1, table "Centre source"), accepted only when no direction switch has been closed for 40 ms or more. Once CENTRE_DOWN is accepted the key stays down, through any roll of the thumb, until SW2 (case `SW2`) and all four direction switches have been open together for the 30 ms release hold-off; CENTRE_UP is stamped at the instant the last one opened. While the key is down no direction event is sent and every closure of a direction switch is discarded, so a thumb that rolls toward a direction, or lets one side of the pair go, does not end a long press early: only a full release does. The 1,000 ms of a long press count from CENTRE_DOWN.
- **Centre press, case `PAIR`** (no fifth switch; architecture 16.5, 17.3; bench B6): a centre press is read when the two switches of an opposite pair, SW1 with SW3 or SW4 with SW5, close within 40 ms of each other, measured between their two debounced press edges. Rules, in this order: (1) the first switch pressed (after the 20 ms debounce) opens the 40 ms decision window; (2) if the opposite switch of that pair closes inside the window, CENTRE_DOWN is sent at that moment; (3) if the window ends, or the first switch is released, with no opposite closure, the direction event of the first switch is sent at that moment; (4) a switch that is not the opposite of a held switch is ignored while the held switch stays down; (5) a centre press has no repeat. A close of the opposite switch after the window is ignored (the press was a direction).
- A direction never starts or stops a recording (architecture 17.11; this replaces the sentence of architecture section 9 that said the joystick never starts or stops one: the centre press does, directions do not).
- **Lock:** when the screen is off, or shows the dimmed SCR_REC_DIM in `RECORDING`, the first joystick event (a direction or a short press of the centre) only turns the full screen on; it is not acted on. A long press is not an event of this rule (collision C4). The screen turns off 5 s after the last input; in `RECORDING` it never turns off: 3 s after the last input it dims to SCR_REC_DIM (rule R-SIGN, section 3.2). There is no other lock. Exception (ruling R17): while a control session is open, no joystick event is held back by this rule (section 3.4).

Screens are listed in section 3.3. Mapping per screen:

| Screen | Up | Down | Left | Right | Centre |
|---|---|---|---|---|---|
| SCR_STATUS | open SCR_NOTIFS (F7 part 4; F6 said none) | none | none | open SCR_MENU | open SCR_MENU |
| SCR_NOTIFS (F7 part 4) | previous notification | next notification | back to SCR_STATUS | open SCR_NOTIF | open SCR_NOTIF |
| SCR_NOTIF (F7 part 4) | previous notification | next notification | dismiss: the negative action (section 7.6), only when the notification has it | the positive action (section 7.6), only when the notification has it | back to SCR_NOTIFS |
| SCR_RECORDING | none | none | none | none | highlight marker (section 2.1; collision C1) |
| SCR_MENU | previous item | next item | close menu, back to SCR_STATUS | open item | open item |
| SCR_RECORDINGS | previous recording | next recording | back to SCR_MENU | open SCR_RECORDING_INFO | open SCR_RECORDING_INFO |
| SCR_RECORDING_INFO | none | none | back to SCR_RECORDINGS | none | none |
| SCR_SETTINGS | previous setting | next setting | back to SCR_MENU | change value | change value |
| SCR_MODES | previous mode | next mode | back to SCR_MENU | open a control session in that mode (SCR_CONTROL) | open a control session in that mode (SCR_CONTROL) |
| SCR_CONTROL (control session, section 3.4) | sent to the active device (section 7.5) | sent to the active device | sent to the active device | sent to the active device | sent to the active device; in `RECORDING` the highlight marker, and nothing is sent |
| SCR_DEVICES | previous device | next device | back to SCR_MENU | open SCR_DEVICE for that device | open SCR_DEVICE for that device |
| SCR_DEVICE | previous item | next item | back to SCR_DEVICES | do the item | do the item |
| SCR_CONFIRM | none | none | "No" (back) | none | "Yes" |
| SCR_PAIR | none | none | cancel pairing | none | none |
| SCR_MESSAGE | dismiss | dismiss | dismiss | dismiss | dismiss |
| SCR_CHARGING, SCR_TRANSFER, SCR_ERROR | none | none | none | none | turn screen off |
| SCR_FACTORY | reported to the jig | reported to the jig | reported to the jig | reported to the jig | reported to the jig |

The Centre column is the action of a short press of the centre (section 2.1) when the screen is on. Menu items in SCR_MENU, in this order: "Recordings", "Control", "Devices", "Pair device", "Settings", "Power off" (F6 had four items; "Control" and "Devices" are new in F7 part 3 and "Pair phone" is renamed "Pair device"). "Power off" is shown only in `STANDBY`; in every other state the menu has the first five items, because the table of section 1.2 has a power-off row only for `STANDBY` (F7 part 4). When the state leaves `STANDBY` with the menu open, the selection moves to the last of the five items, and an open "Power off" question closes; "Power off" is sent to the core only in `STANDBY`. A confirmed power off that the core no longer accepts because the state left `STANDBY` first is dropped. Settings in SCR_SETTINGS, in this order: "Screen brightness" (3 levels), "Vibration" (on/off; off disables MH and joystick ticks only, never M1, M2, M3, MF, MW), "Time format" (24 h / 12 h), "About" (firmware version, serial).

Collisions between the F3 roles of the centre press and the record gesture. The record gesture wins each time; the F3 role changes as stated. Every F3 centre role not listed here stays as it was (SCR_STATUS opens the menu, menus open items, SCR_CONFIRM "Yes", SCR_SETTINGS change value, SCR_CHARGING, SCR_TRANSFER and SCR_ERROR turn the screen off), because a short press with the screen on has nothing to wake.
- **C1** SCR_RECORDING, F3 centre: "show SCR_STATUS for 3 s". Collides with the highlight of a short press in `RECORDING`. Result: the short press marks the highlight and shows the highlight count for 3 s; the status screen is no longer reachable from the centre during a recording.
- **C2** a long press in `STANDBY` on any screen (SCR_MENU, SCR_SETTINGS, SCR_CONFIRM, SCR_PAIR, SCR_RECORDINGS). F3 gave the centre no long-press role, but a user holding the centre to answer "Yes" on SCR_CONFIRM now starts a recording. Result: the long press starts a recording from any screen; open screens are discarded; an open pairing window (SCR_PAIR) is closed.
- **C3** timing and the dead double press. F3 centre actions in menus came at once (at most 40 ms after the press edge); the record gesture decides a short press only when the 400 ms double-press window has closed, and a double press does nothing even in a menu. Result: every centre action in a menu comes at least 400 ms after the release, and a second quick press does not repeat it. Exception (ruling R17): with a control session open, a double press closes the session (section 3.4).
- **C4** the screen-off lock. F3: the first joystick event only wakes the screen. A long press with the screen off must start a recording. Result: the lock covers directions and short presses only; a long press with the screen off starts a recording; in `RECORDING` a short press with the screen dimmed (SCR_REC_DIM) marks the highlight and shows SCR_RECORDING for 3 s.

## 3. Feedback

### 3.1 Motor (MOTOR, P3.01, high = on)

The motor is the Jinlong W0525AB001D (brushless coin, 5.0 mm diameter x 2.5 mm, 3.0 V, below 80 mA running, below 175 mA at each start, starts below 2.5 V [Jinlong spec S-525113 rev 0, architecture sections 2 and 17.16]) in the joystick-side shoulder of the band at -47.0 degrees on US 7 to -39.5 degrees on US 13 (-44.0 at US 9; architecture 17.26), joined by two lead wires to flex tail A (J_BAND_A pad 7 MOT+ on VMOT, pad 6 MOT- on GND, netlist.csv).
- **Drive** (architecture 17.22; motor-drive.md section 2.1; netlist.csv): the motor runs from its own 3.0 V regulator U11 (Texas Instruments TLV75530PDQNR), whose input is the cell (net VBAT) and whose output is the net VMOT that feeds the motor. The pin MOTOR drives U11's EN pin (pin 3) through R61 100 ohm on the net MOT_EN, with R62 100 kilo-ohm from MOT_EN to ground, so the motor stays off while the chip starts and in `SHIP` and `OFF`. MOTOR high = motor on at 3.0 V (2.964 to 3.036 V for a cell at 3.15 V or more, motor-drive.md section 2.3); MOTOR low = U11 off. There is no PWM: the motor's maker rates it only for 2.7 to 3.3 V DC, and a pulse train would restart its own drive chip at each on time (an estimate of motor-drive.md section 3.2).
- **Start delay**: from MOTOR high to power on VMOT takes up to 0.55 ms (U11 start-up 550 µs, motor-drive.md section 2.3); that is 2.2 % of the shortest pulse, MT of 25 ms [CALC: 0.55 / 25]. The pattern times below are MOTOR-pin times; the player does not lengthen them.
- **Outside the power chip's battery limit**: the motor's current flows from the cell through U11 and never through the nPM1304's battery path, so the chip's battery current limit IBATLIM (section 8.7) does not see it (architecture 17.22).

A `k_timer` plays each pattern; a new pattern replaces the one playing, except that M1, M2, M3 and MF are never cut short by MH or MT.

| Id | Event | Pattern (on / off in ms) | Total ms |
|---|---|---|---|
| M1 | recording started | 80 on | 80 |
| M2 | recording stopped by the user, by BLE, by case insertion | 80 on, 120 off, 80 on | 280 |
| M3 | low battery (B15, B5), storage S30 or SFULL, an action refused | 80 on, 120 off, 80 on, 120 off, 80 on | 480 |
| MH | highlight marked | 40 on | 40 |
| MT | joystick move or select (only when screen is on) | 25 on | 25 |
| MW | the centre held 500 ms, a start or stop is 500 ms away (warning, section 2.1) | 60 on | 60 |
| MF | fault (storage, microphone, charger) | 300 on, 200 off, 300 on | 800 |

- The 1, 2 and 3 pulse counts follow requirement U4 and architecture section 9. MW is new in F4: one 60 ms pulse **[CHOICE]**, between MT (25 ms) and M1 (80 ms), felt at the thumb that rests on the round cap; **[BENCH]** test F1 also judges it. It sounds only while the centre is held, so no other pattern can run at the same time.
- A pulse draws below 80 mA while the motor runs and up to 175 mA at its start, from the cell through U11, outside the power chip's 100 mA battery limit (motor-drive.md). On the smallest cell, 17.6 mAh at US 7, that is 4.5 C running and 9.9 C at the start; on the largest, 31.9 mAh at US 13, 2.5 C and 5.5 C [CALC: 80 / 17.6 = 4.55, 175 / 17.6 = 9.94, 80 / 31.9 = 2.51, 175 / 31.9 = 5.49; architecture 17.16, 17.26]; whether the cell and its protection circuit allow it is hardware issue H7.
- **Motor charge for the fuel gauge** (motor-drive.md section 2.8 change F3): the power chip measures the battery current inside its own path [NPM p99] and does not see the motor. The firmware adds, for every ON pulse of a pattern, the charge t_on x 80 mA + 10 ms x 175 mA (the second term is the start allowance, an **[ESTIMATE]** until bench step B-M3 of motor-drive.md section 2.9 measures the start; each pulse is counted as a start **[CHOICE]**: an over-count if the motor still turns after a gap of 120 ms or more, which no file states). Per pattern [CALC, `design/firmware-f5-notes.md`]: M1 8.15 mA.s, M2 16.30, M3 24.45, MH 4.95, MT 3.75, MW 6.55, MF 51.50 mA.s. How the sum enters the gauge is section 8.3.
- Every motor pulse during audio capture is marked in the chunk headers, from MOTOR high to 50 ms after MOTOR low (section 4.7), so later cleanup can mute it. The pattern start time is also logged as an event.
- MT follows the lock fact of section 3.3 (F7 part 4): the first direction from the dimmed SCR_REC_DIM only shows the full picture and gives no MT; in a control session a direction gives MT also when the screen is off, because it is acted on.
- MT is the shortest pulse; whether 25 ms is felt is **[BENCH]** test F1 (wear test: 5 people feel or do not feel MT; if fewer than 4 feel it, MT becomes 40 ms).

### 3.2 Recording sign on the screen (architecture 17.30)

- **No recording light:** removed in v7 (architecture 17.30): LED1, R41, Q2, the light guide LG1, the light pipe LP1, the light window in the glass print and its plug are out of the design. The firmware had no light code before and has none now. The sign that a recording runs is the screen, drawn by the firmware.
- **R-SIGN, the screen is never dark while recording** (the lead's rule of 17.30): in `RECORDING` the screen is on from the start of the recording to its close and shows at least the red dot and the timer of this recording. Any input (any switch of the joystick) shows the full recording picture SCR_RECORDING for 3 s; 3 s after the last input it dims to SCR_REC_DIM (section 3.3) until the next input.
- **Dimmed** **[CHOICE]**: SCR_REC_DIM draws only the red dot and the timer HH:MM:SS on true black, at the lowest of the three levels of the setting "Screen brightness" (section 2.2), which is panel level 85 of 255 (the three levels are 85, 170 and 255), never 0; the timer is redrawn once per second.
- **One code path:** the function `rec_mics_on()` is the only code that enables VDD_MIC (section 4.5, start step 2). It first powers the screen if it is off (sequence of section 3.3) and draws the red dot and the timer at 00:00:00; it enables VDD_MIC only when the screen driver has accepted that frame (`display_write()` returned 0 and the display is not blanked). If it fails, VDD_MIC stays off and the row "long press of the joystick centre, recording sign not drawn" applies (section 1.2). The close turns VDD_MIC off before the screen may leave the recording pictures. Nothing in `RECORDING` blanks the screen or drives OLED_PWR_EN low: the screen-off timer, the lock of section 2.2 and the current-limit action of section 8.7 dim to SCR_REC_DIM instead.
- **Start of the sign in the screens part (F7 part 4, software step 4):** the function `rscr_sign_start()` is the call that `rec_mics_on()` makes for the first frame. The screens thread draws the frame and the caller waits for the answer, 5 s at most. An answer of 0 means the panel accepted the frame with the red dot. A call that times out is cancelled: its frame is never drawn later, and a later call never receives its answer. The call is refused on the screens thread itself and when the screens did not start; it may be made while the core step runs. Until software step 6 nothing calls it.
- **Test SIGN-1** (proves that no state records with the screen dark), one of the state-machine tests of W12 (section 10.2): for every row of the table of 1.2, run from its From state with a screen stub that records blanking, OLED_PWR_EN and every frame; after the row, and at every 100 ms tick of a 10 s idle run after it, VDD_MIC on must mean OLED_PWR_EN high, the screen not blanked and the last frame holding the red dot pixels. A forced draw failure at the start must leave VDD_MIC off. One failing case fails the build. Factory test T-SIGN (section 9.3) checks the same on each ring with the jig camera.
- **Cost: a bench item, no number.** The always-lit red dot and timer draw current from the screen for the whole recording; the cost is measured on the new panel (bench, architecture 17.30) and is not counted in section 8.5. The 1.5 mA once counted for the recording light, removed in v7, is out of the budget (section 8.5).
- **What is lost** (architecture 17.30): the sign is drawn by software and is no longer wired to the microphone supply; a firmware fault or a panel that fails during a recording can leave a recording without a visible sign. SIGN-1 tests the firmware and T-SIGN the panel at the factory; nothing tests the panel during use.

### 3.3 Screen

Screen: 120 x 240 pixels, RGB565. The wearer sees it 240 wide and 120 high (landscape: the long side lies along the finger); the screen code draws in a 240 x 120 frame and one function turns it for the panel (the lead's ruling of 2026-11-12, after the screen designs the owner accepted; F6 said portrait). The screen is off in every state except for the times stated (requirement P6); in `RECORDING` it is never dark (rule R-SIGN, section 3.2). Fonts (F7 part 4): the drawing library's built-in face at 14, 16, 28 and 32 px; no font file is added (F6 said two sizes). Colours: white text on black; grey for the second line; red for the recording dot; green for charging and for "Yes"; amber for warnings. Content stays 18 px from the edges. There is no status bar: the battery, the storage left and the Bluetooth icon are not drawn on SCR_STATUS and SCR_RECORDING (the owner's round 3 of the film designs: the screen content takes the full space); SCR_CHARGING shows the battery.

**Lock fact (F7 part 4).** The screens part keeps the fact that the lock of section 2.2 reads: it is true when the screen is fully lit (not off and not SCR_REC_DIM) or a control session is open, and false otherwise. A joystick event with the fact false only turns the full screen on: SCR_STATUS, or the screen of the state (SCR_CHARGING, SCR_TRANSFER, SCR_ERROR, SCR_RECOVERY, SCR_FACTORY, SCR_RECORDING). The fact is computed and stored under one lock.

**Screen times (F7 part 4).** SCR_PAIR stays on for its whole 60 s window (a passkey that disappears after 5 s cannot be typed); SCR_RECOVERY and SCR_FACTORY stay on while their state lasts; a message stays 3 s ("Battery low" at B15: 5 s); every other screen turns off 5 s after the last input. SCR_MESSAGE in `RECORDING` keeps the red dot and the timer.

| Screen | Shown in | Fields, top to bottom |
|---|---|---|
| SCR_STATUS | `STANDBY`, error states after their message | time HH:MM (12 h with AM or PM when set) and "Ready" (F7 part 4; F6 also listed battery, storage left and a Bluetooth icon) |
| SCR_NOTIFS (F7 part 4) | Up from SCR_STATUS | "Notifications" with the count, the stored notifications newest first (section 7.6), the selected one highlighted, a green dot for unread; "None" when empty |
| SCR_NOTIF (F7 part 4) | from SCR_NOTIFS | title (the word "Notification" when there is none; the app identifier is never shown), message on two lines, the dismiss at the left edge and the positive action at the right edge, each drawn only when the notification has it. A dismiss changes the store only when the iPhone reports the removal; the screen then returns to SCR_NOTIFS |
| SCR_RECORDING | `RECORDING` (3 s after input) | the waveform (a drawn set of lines; not live until a microphone level exists), red dot and "Recording", timer HH:MM:SS of this recording, "N marked" after the first highlight, the mode name in a control session (F7 part 4; F6 also listed battery, storage left and "Hold 1 s to stop") |
| SCR_REC_DIM | `RECORDING`, from 3 s after the last input to the next input | red dot and timer HH:MM:SS only, true black elsewhere, lowest brightness level (section 3.2) |
| SCR_MENU | joystick from SCR_STATUS | 6 items of section 2.2, selected item highlighted |
| SCR_RECORDINGS | menu "Recordings" | list of the 20 newest: date, start time, duration, transferred tick |
| SCR_RECORDING_INFO | from SCR_RECORDINGS | date, start, duration, channels, highlights, size in MB, state (new, transferred, recovered) |
| SCR_SETTINGS | menu "Settings" | 4 settings of section 2.2 with their values |
| SCR_CONFIRM | "Power off", "Remove" on SCR_DEVICE | question, "Yes: short press centre", "No: left" |
| SCR_PAIR | menu "Pair device", when a slot is free | "Pair", 6-digit passkey (section 7.4; "--- ---" until it exists), time left of 60 s |
| SCR_MODES | menu "Control" | the four control modes of section 7.5 in the order Media, Presenter, Pointer, Agent; the last used mode highlighted |
| SCR_CONTROL | an open control session in `STANDBY` (section 3.4) | mode name, name of the active device, "Not connected" while the active device has no level 4 link, "Press twice to leave" |
| SCR_DEVICES | menu "Devices" | the paired devices as pills in slot order by name, the active one on the light fill, a ring on the one under the cursor; a name longer than its pill is cut with dots; "No device" when none is paired |
| SCR_DEVICE | from SCR_DEVICES | the device name, then two items: "Use", "Remove" |
| SCR_MESSAGE | refused actions, warnings | one line of text, 3 s ("Battery low", "Storage full", "30 min left", "In case", "Remove a device first"); "Battery low" at B15 stays 5 s and is amber (F7 part 4) |
| SCR_CHARGING | `CHARGING` (5 s after insertion, 5 s after any input) | battery % and icon, "Charging" or "Full", time to full in minutes from the fuel gauge |
| SCR_TRANSFER | `TRANSFER` (5 s after start, 5 s after any input) | "Transfer", recordings left to send, percent of the current recording |
| SCR_ERROR | error states | error name, error code (event log code, section 9.4), "Put in case" for storage faults |
| SCR_RECOVERY | `RECOVERY` | "Recovering", chunks scanned |
| SCR_FACTORY | `FACTORY_TEST` | test name, step, result |

Screen power sequence (sch-notes sections 2 and 7 item 2, and section 9 item 1). VCI (VDD_3V0) and IOVCC (VDD_1V8) are on whenever the bucks run. The SGM38046 is in shutdown only when AVDDEN (OLED_PWR_EN) and SWIRE are both low; SWIRE is driven by the SH8501A, not by the nRF.
- On (Tailor sheet page 9): (1) LCD_RST low; VCI and IOVCC are already on (no order between them); (2) OLED_PWR_EN high (SG Micro allows AVDDEN before SWIRE); (3) wait 10 ms or more; (4) LCD_RST high, wait 10 ms or more; (5) send the vendor start-up code and DCS "sleep out", wait 120 ms or more; (6) DCS "display on"; the SH8501A starts SWIRE and ELVDD, ELVSS 66.7 ms or more after "display on": draw nothing that matters before that.
- Off: (1) DCS "display off"; (2) DCS "sleep in", wait 120 ms (the SH8501A stops SWIRE); (3) OLED_PWR_EN low; (4) LCD_RST low. The SGM38046 is then in shutdown (both inputs low).
- While the screen is off, OLED_PWR_EN is low in every state; LCD_SCK, LCD_MOSI, LCD_CS and LCD_DCX stay at their idle levels (IOVCC is on, so no line back-powers the screen).
- The waits and the SWIRE level of the SH8501A at reset come from the vendor start-up code (architecture action 12.1) and are listed in section 10.5.

### 3.4 Control session and device screens (F7 part 3, ruling R17)

- **Modes.** The menu item "Control" opens SCR_MODES. Right or Centre on a mode opens a **control session** in that mode and shows SCR_CONTROL. The first time, Media is highlighted.
- **Session.** The ring sends keys and pointer moves only in an open control session (section 7.5). In a session, Up, Down, Left, Right and a short press of the centre are sent to the active device as the mode's table says, and they do nothing else on the ring.
- **Leaving.** A double press of the centre closes the session and shows SCR_MODES (in `RECORDING`: SCR_RECORDING), also when the screen was off (F7 part 4). The session also closes by itself after 30 minutes with no joystick action **[CHOICE]**, when the ring enters any state other than `STANDBY` and `RECORDING`, and when the active device is removed.
- **Screen.** SCR_CONTROL follows the normal rule: the screen turns off 5 s after the last input. The lock of section 2.2 does not apply in a session: with the screen off, an action is sent at once and also turns the screen on.
- **Recording.** A long press records as always (section 2.1) and does not close the session: this is the one exception to collision C2, which discards every other open screen. In `RECORDING` the screen shows SCR_RECORDING and SCR_REC_DIM as rule R-SIGN says, and SCR_RECORDING adds the mode's name. The four directions are sent, also from SCR_REC_DIM, and each shows SCR_RECORDING for 3 s. A short press of the centre is the highlight marker and is not sent.
- **No link.** While the active device has no level 4 link (section 7.4), an action sends nothing and SCR_CONTROL shows "Not connected". The ring advertises to the active device as section 7.3 says.
- **Devices.** The menu item "Devices" opens SCR_DEVICES. A device's name is the first 16 characters of its Bluetooth device name, read once after pairing and stored with its slot; a device with no name is shown as "Device 1", "Device 2" or "Device 3" by its slot. Right or Centre opens SCR_DEVICE. "Use" makes the device the active one (section 7.4) and returns to SCR_DEVICES. "Remove" asks on SCR_CONFIRM, then removes the device (section 7.4).
- **Pairing.** The menu item "Pair device" opens SCR_PAIR for the lowest free slot. With three paired devices it shows SCR_MESSAGE "Remove a device first". The first paired device becomes the active one; a later one becomes active only through "Use": pairing a second or third device leaves the active device as it is (F7 part 4: the devices part does this itself, section 7.4). The ring holds one link at a time: the link of the active device is interrupted while the new device pairs, the link of the new device ends right after the bonding, and the ring advertises to the active device again.
- **Core.** The states and the table of section 1.2 do not change. The session is a flag of the screens part that the control part reads. Software step 2 built the flag and the key tables; the screens come with software step 4.

## 4. Audio pipeline

### 4.1 PDM settings

The Zephyr driver `drivers/audio/dmic_nrfx_pdm.c` serves each PDM instance as its own device (one `DEVICE_DT_INST_DEFINE` per enabled node), one stream per instance, 1 or 2 channels, 16-bit samples only [SRC 2]. F3 enables one instance, `pdm20`, as one device with 2 channels.

The driver picks the PDM clock with `nrfx_pdm_prescalers_calc()`: for each ratio offered by the chip it divides the 32 MHz base clock by an integer prescaler, keeps only clocks inside the requested minimum and maximum PDM clock, and picks the closest sample rate [SRC 4]. On this chip the ratios are 48, 50, 64, 80, 96, 150 and 192 and the prescaler is 4 to 126 [SRC 3]. **1.536 MHz is not reachable**: 32 MHz / 1.536 MHz = 20.83, not an integer [CALC]; prescaler 20 gives 1.600 MHz and 16,667 Hz at ratio 96, prescaler 21 gives 1.524 MHz and 15,873 Hz [CALC]. The firmware therefore uses **1.280 MHz, ratio 80** (32 MHz / 25 = 1.280 MHz; 1,280,000 / 80 = 16,000 Hz exactly [CALC]), inside the microphone's performance mode, 1.000 to 4.800 MHz [DS Table 3, line 95], and outside its low-power mode, 350 to 800 kHz [DS Table 4, line 121]. Accepted by the lead (H1).

There is one recording mode (owner, F2): 2 microphones on one stereo input, 16 kHz, 16 bits, raw (architecture 16.6). The one instance gets these settings:

| Setting | `pdm20` (mics 1, 2) |
|---|---|
| Devicetree `clock-source` | `"PCLK32M"` (section 4.2) |
| `pcm_rate` | 16,000 |
| `pcm_width` | 16 |
| `req_num_chan` | 2 |
| `req_chan_map_lo` | `dmic_build_channel_map(0,0,PDM_CHAN_LEFT) \| dmic_build_channel_map(1,0,PDM_CHAN_RIGHT)` (driver default map, left on falling edge) [SRC 2] |
| `min_pdm_clk_freq` / `max_pdm_clk_freq` | 1,200,000 / 1,650,000 Hz **[CHOICE]**: kept from F4 so the driver's pick stays 1.280 MHz; the window lies inside the performance mode, 1.000 to 4.800 MHz [DS line 95] |
| Clock the driver picks | 1.280 MHz, prescaler 25, ratio 80 [CALC from SRC 4 algorithm] |
| Gain | `gain_db = 0`, register value 0x28 = 0 dB on both GAINL and GAINR [CALC: 2 x 0 + 0x28 = 0x28] (driver writes `2 * gain_db + NRF_PDM_GAIN_DEFAULT`, range 0x00 = -20 dB to 0x50 = +20 dB) [SRC 2, SRC 3]. F4 also had 0 dB (0x28), for a microphone of -37 dBFS; the SPK0641HT4H-1 is -26 dBFS [DS line 100], 11 dB more [CALC: -26 - (-37)], so with the same gain a sound is stored 11 dB higher than in F4 (lead's decision, H16) |
| Channel order in memory | left = mic 1 (U5, pin 3 SELECT on GND, at X = -10.8 mm), right = mic 2 (U6, pin 3 SELECT on VDD_MIC, at X = +10.8 mm) (architecture 17.19, netlist.csv) |
| `block_size` | 1,024 bytes = 512 samples = 256 stereo frames = 16 ms |
| Blocks (`k_mem_slab`, devicetree `queue-size`) | 8 (`queue-size = <8>`) |

- Wiring of each microphone (sch-notes section 12.1 item 14, netlist.csv): pin 1 DATA (U5 through R31, U6 through R32, both onto MIC_A_DATA), pin 2 CLOCK on MIC_A_CLK, pin 3 SELECT (U5 on GND, U6 on VDD_MIC), pin 4 Vdd on VDD_MIC, pins 5 to 8 GROUND. The datasheet's timing figure gives each SELECT level its own half of the clock cycle [DS Figure 1, sheet 3]; its text copy does not name the edge in words, so which nRF channel each microphone lands in is checked by factory test T-MIC on every ring (section 9.3) and listed in section 10.5.
- Levels with the gain of 0 dB [CALC, `design/firmware-f5-notes.md`]: a 94 dB SPL tone at 1 kHz is stored at -26 dBFS (F4, old part: -37 dBFS); full scale (a clipped sample, chunk flag bit 4) is reached at 94 + 26 = 120 dB SPL, equal to the microphone's acoustic overload point of 120 dB SPL [DS line 105], so the digital path clips where the microphone does (F4: 94 + 37 = 131 dB SPL); a speaking voice at 60 to 70 dB SPL is stored at 60 - 94 - 26 = -60 to 70 - 94 - 26 = -50 dBFS. The microphone's noise, -26 - 64.5 = -90.5 dBFS(A), stays above the noise of a 16-bit sample, -98.1 dBFS (H16). Samples are stored as they come from the PDM; any further gain is applied off the ring. No firmware rule uses an absolute stored level: there is no level meter and no voice-activity threshold (removed in F2); the clipped-sample flag is at the 16-bit limits whatever the gain; T-MIC compares the two channels with each other (section 9.3), so its pass limits do not change.

### 4.2 Channel alignment (one PDM instance)

- Both microphones share one clock and one data line on one instance, so there is no start offset between instances, no skew to measure and no block pairing. The two channels of a frame are read from the same data line on the two clock edges, half a PDM clock apart: 1 / 1.280 MHz / 2 = 390.6 ns [CALC], 0.006 of a sample at 16 kHz, not corrected.
- Devicetree `clock-source = "PCLK32M"`. With that source the driver starts the transfer inside `dmic_trigger()` itself [SRC 2, `trigger_start()` and `request_clock`]. For clock accuracy the application requests the 32 MHz crystal (HFXO) through the nRF clock control on-off service and waits until it runs before it starts the microphones, and releases it after they stop.
- Start sequence: configure the device; request HFXO; `dmic_trigger(pdm20, DMIC_TRIGGER_START)`.
- A missing block (driver error, queue full) is replaced by zeros of the same length, sets chunk flag bit 7 ("dropout"), is counted in the header field `dropout_blocks` and is logged, so the recording never changes length.

### 4.3 Buffers

| Buffer | Samples | Bytes | Duration |
|---|---|---|---|
| PDM DMA block | 512 | 1,024 | 16 ms stereo at 16 kHz |
| PDM slab, 8 blocks | 4,096 | 8,192 | 128 ms at 16 kHz stereo |
| Chunk payload (section 5.3) | 16,384 | 32,768 | 512 ms of 2 channels |
| Chunk with its header sector | | 33,280 | |
| Chunk ring, 3 chunks | 49,152 | 99,840 | 1,536 ms of 2 channels |
| USB read buffers, 2 x 32 sectors | | 32,768 | |

Data path: each 16 ms, `dmic_read()` returns one block of 256 stereo frames from `pdm20`, already interleaved (channel 0 = mic 1, 1 = mic 2); the audio thread copies it into the current chunk and frees the block. After 32 blocks the chunk is full and goes to the storage thread's queue. 2 x 16,000 x 2 = 64,000 bytes per second, 230.4 MB per hour [CALC; architecture 16.6].

### 4.4 Recording start and stop timing

- Start: the long press fires at the 1,000 ms mark (section 2.1); M1 runs at once; the microphones start (section 4.5); the first kept frame is 50 ms after the PDM start. The press and M1 fall before or inside the discarded 50 ms and the marked motor interval (section 4.7).
- Stop: the long press fires at the 1,000 ms mark; the frames up to that mark are kept (they hold the sound of the press; the press start time is written to the event log); then close and M2. M2 runs after VDD_MIC is off, so it is never in the audio.
- Nothing is captured before the start press, and no earlier audio is kept in RAM (owner, F2).

### 4.5 Microphone power sequencing

From the datasheet [DS Table 2, text lines 82 to 90]: power-up time at most 50 ms (from Vdd at or above its minimum); wake-up time at most 15 ms; mode change time at most 10 ms; in sleep mode (clock under 250 kHz) DATA is high-impedance [DS note 3, line 171] and the part draws 26 µA with the clock stopped [DS Table 5, line 145]. Supply 1.6 to 3.6 V, VDD_MIC is 1.8 V [DS line 74]. Current 630 µA typical, 710 µA maximum at 1.8 V, measured at a 2.4 MHz clock [DS Table 3, line 97]; at the ring's 1.280 MHz the datasheet gives no figure (section 10.5, item 6).

Start (entering `RECORDING`):
1. Request HFXO; wait until it runs.
2. `regulator_enable()` on the nPM1304 load switch 1 (VDD_MIC, ball A4 LSOUT1, netlist.csv), called only by `rec_mics_on()` after the screen accepted the red dot and the timer (rule R-SIGN, section 3.2); a failed draw leaves VDD_MIC off and no recording starts.
3. Wait 1 ms. Rail rise [CALC]: soft-start 25 mA [NPM p77, LDSW1SOFTSTARTSEL] into C31 + C32 + C35 + C36 + C86 = 1.0 + 1.0 + 0.1 + 0.1 + 1.0 = 3.2 µF on VDD_MIC (netlist.csv, parts.csv) to 1.8 V takes 3.2 µF x 1.8 V / 25 mA = 0.23 ms.
4. Configure and start the PDM instance (section 4.2).
5. Discard the first 50 ms of samples (800 frames at 16 kHz). With step 3 the first kept frame comes at least 1 + 50 = 51 ms after VDD_MIC is enabled, after the 50 ms power-up time [DS Table 2]. The recording timestamp is the time of the first kept frame.


Stop: `dmic_trigger(pdm20, DMIC_TRIGGER_STOP)`; wait for the driver to release its blocks (`dmic_read()` returns an error); apply the pin sleep state so MIC_A_CLK is driven low; `regulator_disable()` on VDD_MIC (active discharge on, section 8.1); release HFXO. Only after VDD_MIC is off may the screen leave the recording pictures (rule R-SIGN, section 3.2).

Rule (sch-notes section 9 item 6): **MIC_A_CLK is driven low whenever VDD_MIC is off**, so no clock back-powers the microphones through its pin. Order: clock low before VDD_MIC goes off, VDD_MIC on before the clock starts. MIC_A_DATA is an input with no pull while VDD_MIC is off. At boot the pin sleep state (clock pins output low) is applied before VDD_MIC is ever enabled. The Zephyr driver applies only the default pin state, at init [SRC 2]; applying the sleep state at stop and at boot is a driver change (section 10.2, item W3).

### 4.6 RAM budget

The chip has 512 KB of RAM; Zephyr's device file gives the application `cpuapp_sram` of 511 KB (523,264 bytes) in a secure build [SRC 1]. Static allocation:

| Item | Bytes |
|---|---|
| PDM DMA blocks, `pdm20`, 8 x 1,024 | 8,192 |
| Chunk ring, 3 x 33,280 | 99,840 |
| USB read buffers, 2 x 16,384 | 32,768 |
| USB stack buffer pool | 8,192 |
| Bluetooth host and controller | 40,960 |
| Display draw buffers, 2 x 120 x 40 x 2 | 19,200 |
| Display library heap | 24,576 |
| Thread stacks (10 threads) | 24,576 |
| Kernel, drivers, C library data | 16,384 |
| Log buffer | 4,096 |
| Crash record, retained RAM | 1,024 |
| Fuel gauge state | 1,024 |
| Recordings list cache, 256 x 64 | 16,384 |
| System heap | 8,192 |
| **Total** | **305,408** |

- Margin: 523,264 - 305,408 = 217,856 bytes [CALC]. F3 removes the blocks of the second instance (8,192 bytes) and halves the chunk ring (198,144 to 99,840 bytes): 411,904 - 8,192 - 98,304 = 305,408 [CALC]. The buffers F2 removed are in the change list at the top.
- The Bluetooth, display library, stack and kernel lines are allocations, not measurements; the linker map of the first build checks them (section 10.2). If the build exceeds a line, the margin pays for it; the chunk ring is never reduced below 3 chunks.

### 4.7 Motor noise in the audio

The motor sits in the joystick-side shoulder of the band (-47.0 to -39.5 degrees by ring size, architecture 17.26) and the microphones under the board with their ports through the block's underside (architecture 17.19); the one metal body joins them, so a pulse can reach the audio (not measured). The rule below does not depend on the path.
- Rule: the samples are kept and **marked**. A motor interval runs from the frame at which MOTOR goes high to 50 ms after MOTOR goes low: pulse length in frames + 800 frames [CALC: 50 ms x 16,000 Hz]. The start delay of U11, up to 0.55 ms (section 3.1), falls inside the interval, which begins at MOTOR high.
- The audio thread takes the MOTOR edge times from the motor pattern player (cycle counter) and converts them to frame numbers of the current chunk; every interval that overlaps a chunk is written in that chunk's header (section 5.3, offsets 144 to 179) and sets flag bit 3. An interval that spans two chunks is written in both, cut at the chunk edge.
- At recording start, M1 (80 ms) runs while the first 50 ms are discarded (section 4.5); the rest of the pulse plus 50 ms is marked in the first chunk.
- MW (section 2.1) at 500 ms of a hold inside `RECORDING` is a motor pulse like any other and is marked the same way.

## 5. Storage

### 5.1 Driver stack

- SD card over SPI: devicetree node `compatible = "zephyr,sdhc-spi-slot"` on `spi00` with `spi-max-frequency = <16000000>`, child `compatible = "zephyr,sdmmc-disk"` with `disk-name = "SD"` [SRC 6, SRC 7]. The driver sends the 74 start clocks at 400 kHz, then switches to the requested clock [SRC 7]; it supports multi-block read and write (CMD18, CMD25, with CMD12 after a multi-block read) and checks a CRC-16 on every data block [SRC 7].
- 16 MHz = SPIM00 core clock 128 MHz / prescaler 8 [SRC 3: core frequency 128 MHz, divisor 4 to 126; CALC]. It stays under the 25 MHz SPI-mode limit of SD cards (SD specification, not read here: section 10.5). The raw bit rate is 16 Mbit/s = 2.0 MB/s [CALC]; recording needs 0.064 MB/s.
- Rule (sch-notes section 9 item 6; pull-ups R60, R63 to R65 go to VDD_SD, architecture W3): **no storage line is driven high while VDD_SD is off.** Before VDD_SD goes off: `DISK_IOCTL_CTRL_DEINIT`, then `spi00` is suspended so its pin sleep state applies, in which SD_SCK, SD_MOSI, SD_CS and SD_MISO are inputs with no pull (disconnected). After VDD_SD comes on: wait 1 ms, resume `spi00` (default pin state: SD_CS output high, SD_SCK and SD_MOSI outputs low), then `DISK_IOCTL_CTRL_INIT`. At boot the sleep state is applied before any SPI use. The development kit already has a `spi00_sleep` state [SRC 9]; the suspend call is listed in section 10.5.
- The firmware uses the Zephyr disk access API with no file system: `disk_access_write()`, `disk_access_read()`, `disk_access_ioctl()` with `DISK_IOCTL_CTRL_INIT` after VDD_SD comes on and `DISK_IOCTL_CTRL_DEINIT` before it goes off [SRC 6], and `DISK_IOCTL_GET_SECTOR_COUNT` at mount.

### 5.2 Layout: raw, append-only log (no file system)

Choice: raw sector layout, written as an append-only circular log of self-checking chunks, with a two-copy superblock.

Why, against FAT (FatFs) and littlefs:
- **Power-loss safety:** FAT rewrites its allocation table and a directory entry as a file grows; a cut in that write can lose the whole file. Here a chunk carries its own CRCs and a sequence number; after a cut, the scan in `RECOVERY` keeps every chunk whose CRCs match and stops at the first one that does not. No metadata is rewritten while recording.
- **Write speed:** one 65-sector multi-block write (CMD25) per chunk, sequential addresses, no table updates in between.
- **Wear:** every data sector is written once per lap of the card (4 GB at 64,000 bytes per second is about 16 hours of audio per lap [CALC, architecture 16.4]); index sectors once per record; the superblock 2 times per recording, alternating between 2 sectors. The card's own wear levelling (its controller) is not documented for the CSNP32GCR01-BOW (section 10.5).
- The case reads the ring through the custom protocol of section 6, not as a disk, so no host needs a file system on the card.

Sector map (512-byte sectors, LBA = sector number):

| LBA from | LBA to | Content |
|---|---|---|
| 0 | 0 | superblock copy A |
| 1 | 1 | superblock copy B |
| 2 | 2,047 | event and crash log, ring of 2,046 records, 1 record per sector (section 9.4) |
| 2,048 | 8,191 | reserved, zero; LBA 4,096 to 4,160 is the factory test area (section 9.3) |
| 8,192 | 73,727 | index log, ring of 65,536 records, 1 record per sector (section 5.4) |
| 73,728 | 81,919 | reserved, zero |
| 81,920 | card end | chunk area: `chunk_count_total` = floor((sector count - 81,920) / 65) chunks of 65 sectors |

Chunk with sequence number s starts at LBA 81,920 + (s mod `chunk_count_total`) x 65.

### 5.3 Recording format, byte by byte

A recording is a run of chunks with the same `recording_id`. Each chunk = 1 header sector (512 bytes) + 64 payload sectors (32,768 bytes) = 33,280 bytes. Payload: signed 16-bit samples, interleaved by frame (frame = one sample per channel, channel 0 first). A chunk holds 8,192 frames of 2 channels (512 ms at 16 kHz). Unused payload bytes in the last chunk are zero.

Chunk header:

| Offset | Size | Field | Value |
|---|---|---|---|
| 0 | 4 | magic | 0x4B435252 (ASCII "RRCK") |
| 4 | 2 | header_version | 1 |
| 6 | 2 | header_size | 512 |
| 8 | 4 | chunk_seq | global, starts at 1, +1 per chunk, never reused |
| 12 | 4 | recording_id | starts at 1, +1 per recording, never reused |
| 16 | 4 | chunk_in_recording | 0 for the first chunk |
| 20 | 2 | flags | bit 0 first chunk; bit 1 last chunk; bit 2 reserved (0); bit 3 a motor interval (section 4.7) touches this chunk; bit 4 a sample clipped (-32768 or 32767); bit 5 time not set; bit 6 battery at B15 or under; bit 7 dropout (a PDM block replaced by zeros); bits 8 to 15 zero |
| 22 | 1 | recording_type | 1 recording (the only type); 2 factory test recording (section 9.3) |
| 23 | 1 | channels | 2 |
| 24 | 4 | sample_rate_hz | 16,000 |
| 28 | 1 | sample_format | 1 = signed 16-bit little-endian, interleaved |
| 29 | 1 | mic_mask | 0x03 (bit n set = mic n+1 present, channel order ascending) |
| 30 | 2 | reserved | 0 |
| 32 | 4 | frames | valid frames in this payload |
| 36 | 4 | payload_bytes | frames x channels x 2 |
| 40 | 8 | first_frame_index | frames since the first kept frame of this recording |
| 48 | 8 | utc_ms | Unix time in ms of the first frame, signed; 0 when time is not set |
| 56 | 8 | uptime_ns | ns since boot of the first frame (cycle counter based) |
| 64 | 4 | reserved | 0 (F2 held the PDM skew here; one instance has none) |
| 68 | 4 | pdm_clock_hz | 1,280,000 |
| 72 | 2 | pdm_ratio | 80 |
| 74 | 1 | gain_code | 0x28 (the PDM gain register, 0 dB, section 4.1) |
| 75 | 1 | reserved | 0 |
| 76 | 2 | highlight_count | highlight markers written in this chunk's header, 0 to 8 |
| 78 | 2 | reserved | 0 |
| 80 | 32 | highlight_frame | 8 x 4 bytes: for each marker, the frame number of CENTRE_DOWN counted from the first kept frame of the recording (not an offset inside the chunk). The marker is written in the header of the chunk that is being filled when the highlight fires; a highlight fires 440 to 850 ms after CENTRE_DOWN (section 2.1), so that is often the chunk after the frame's own (ruling R24, software step 6). 0xFFFFFFFF when unused |
| 112 | 2 | battery_mv | battery voltage at the chunk start |
| 114 | 2 | temp_c_x10 | nPM1304 die temperature [NPM p99], 0.1 °C, signed |
| 116 | 4 | boot_count | from the superblock |
| 120 | 4 | dropout_blocks | PDM blocks replaced by zeros in this chunk |
| 124 | 4 | fw_version | major << 24, minor << 16, patch |
| 128 | 4 | reserved | 0 |
| 132 | 4 | cycle_hz | `sys_clock_hw_cycles_per_sec()` used for the ns fields |
| 136 | 4 | reserved | 0 |
| 140 | 4 | reserved | 0 |
| 144 | 4 | motor_count | motor intervals in this chunk, 0 to 4; a fifth interval is merged into the fourth (end frame moved) |
| 148 | 32 | motor_frames | 4 x (start frame u32, end frame u32, exclusive) inside this chunk, end = MOTOR low + 50 ms; 0xFFFFFFFF pairs when unused |
| 180 | 324 | reserved | 0 |
| 504 | 4 | payload_crc32 | CRC-32 over the 32,768 payload bytes |
| 508 | 4 | header_crc32 | CRC-32 over header bytes 0 to 507 |

- Highlight markers: in the chunk header of the chunk where the press happened (frame offset of the first press edge), and the first 32 again in the index CLOSE record (ms from recording start).
- Timestamps: `utc_ms` for wall time, `uptime_ns` for exact spacing between chunks.

### 5.4 Superblock and index records

Superblock (LBA 0 and 1; written to LBA `sb_seq` mod 2; at mount the copy with a valid CRC and the higher `sb_seq` wins):

| Offset | Size | Field |
|---|---|---|
| 0 | 4 | magic 0x42535252 ("RRSB") |
| 4 | 2 | version 1 |
| 6 | 2 | size 512 |
| 8 | 4 | sb_seq |
| 12 | 4 | card_sectors |
| 16 | 4 | chunk_area_first_lba = 81,920 |
| 20 | 4 | chunk_count_total |
| 24 | 4 | head_chunk_seq (next chunk to write) |
| 28 | 4 | tail_chunk_seq (oldest chunk not freed) |
| 32 | 4 | next_recording_id |
| 36 | 4 | index_head (next index record number) |
| 40 | 4 | index_tail |
| 44 | 1 | open_flag (1 = a recording is open) |
| 45 | 3 | reserved 0 |
| 48 | 4 | open_recording_id |
| 52 | 4 | open_first_chunk_seq |
| 56 | 4 | boot_count |
| 60 | 4 | log_head |
| 64 | 444 | reserved 0 |
| 508 | 4 | crc32 over bytes 0 to 507 |

Index record (1 per sector at LBA 8,192 + (record number mod 65,536)):

| Offset | Size | Field |
|---|---|---|
| 0 | 4 | magic 0x58495252 ("RRIX") |
| 4 | 2 | version 1 |
| 6 | 1 | type: 1 CLOSE, 2 CONFIRM, 3 DELETE |
| 7 | 1 | close state: 1 COMPLETE, 2 RECOVERED; 0 for CONFIRM and DELETE |
| 8 | 4 | record number |
| 12 | 4 | recording_id |
| 16 | 4 | first_chunk_seq |
| 20 | 4 | chunk_count |
| 24 | 1 | recording_type |
| 25 | 1 | channels (2) |
| 26 | 2 | highlight_count |
| 28 | 4 | sample_rate_hz (16,000) |
| 32 | 8 | start_utc_ms |
| 40 | 8 | duration_frames |
| 48 | 4 | digest: CRC-32 over the `payload_crc32` values of all chunks in order, as 4-byte little-endian words |
| 52 | 4 | reserved 0 |
| 56 | 128 | 32 x 4 bytes: highlight times in ms from the start; 0xFFFFFFFF when unused |
| 184 | 324 | reserved 0 |
| 508 | 4 | crc32 over bytes 0 to 507 |

A recording's state is its last record: CLOSE = new, CONFIRM = transferred, DELETE = deleted.

### 5.5 Write strategy and power loss

- **VDD_SD on for the whole recording.** It goes on at open and off after close. Between recordings it is off.
- **Flush interval:** a chunk is written as soon as it is full: every 512 ms. The partial last chunk is written at close. The superblock is written twice per recording (open, close).
- **Energy trade:** the card idles at 0.17 mA standby (architecture section 2) = 0.51 mW at 3.0 V [CALC]. Switching the rail off between chunks would need a card start-up (74 clocks, CMD0, CMD8, ACMD41 polling, at 400 kHz) every 512 ms; this pays only if one start-up costs under 0.17 mA x 0.512 s = 87 µC [CALC]. The start-up charge of the CSNP32GCR01-BOW is not documented. Fixed choice now: rail on during a recording. **[BENCH]** test S1 measures the start-up charge and time; under 87 µC, the meeting-mode rule changes to "rail off between chunks".
- **Write retries:** a failed chunk write is retried 2 times at once (3 tries); then `ERR_STORAGE_FAULT`.
- **Sudden power loss (cell cut, short, a power-fail reset of the nPM1304 when VSYS falls under VSYSPOF [NPM p107], for example when the load passes the battery current limit, section 8.7):** audio lost = audio still in RAM. Normal case: the chunk being filled plus at most 1 chunk being written = 1,024 ms [CALC]. **Worst case** (the ring full because the card stalls): 3 chunks = **1.536 s** [CALC]. Everything written before is kept: no written sector is ever rewritten during a recording.
- **Power loss during a write:** the chunk in flight fails its CRC and is dropped by `RECOVERY`; the superblock is never in flight while a chunk is written. Whether the card's controller can damage other sectors on a cut is not documented (section 10.5); `RECOVERY` also verifies every chunk of the open recording, not only the last.
- **`RECOVERY` scan:** from `open_first_chunk_seq`, read each chunk header; keep it while magic, header CRC, payload CRC, `recording_id` and `chunk_seq` (previous + 1) all match; stop at the first mismatch. Write the CLOSE record with state RECOVERED, set `head_chunk_seq` past the last good chunk, clear `open_flag`.

### 5.6 Free-space accounting

- used chunks = `head_chunk_seq` - `tail_chunk_seq`; free chunks = `chunk_count_total` - used.
- SFULL: free chunks at or under 16 (reserve; the last chunk of an open recording always fits).
- S30: free chunks at or under 3,516 = 30 min x 60 s / 0.512 s, rounded up [CALC].
- Screen "storage left" = free chunks x 0.512 s, shown in hours and minutes.
- The sector count is read at mount. Example for 4,000,000,000 bytes = 7,812,500 sectors: (7,812,500 - 81,920) / 65 = 118,932 chunks (rounded down) = 60,893 s = 16.9 hours of audio [CALC]. Example for the 3.7 GB usable (architecture 16.4) = 7,226,562 sectors: 109,917 chunks = 56,278 s = 15.6 hours [CALC]. Which size the card really shows at mount is not read here (section 10.5).

### 5.7 Deletion after confirmed transfer

- The case sends CONFIRM with the digest it computed from the chunks it received (section 6.3). The ring compares it with the digest in the CLOSE record. Match: the ring appends a CONFIRM record. No match: status `DIGEST_MISMATCH`, nothing changes.
- The case then sends DELETE. The ring refuses DELETE for a recording without a CONFIRM record (`NOT_CONFIRMED`).
- On DELETE the ring appends a DELETE record, then moves `tail_chunk_seq` forward over every leading recording (in chunk order) whose state is DELETED, and writes the superblock. Space is freed only from the tail, in recording order. A deleted recording in the middle stays counted as used until the ones before it are deleted.
- Audio sectors are not erased; they are overwritten on the next lap. READ_RANGE refuses deleted recordings (`NOT_FOUND`).

## 6. Transfer protocol over USB (in the case)

### 6.1 Device class

- Controller: `usbhs`, a Synopsys DWC2 core, compatible `"nordic,nrf-usbhs-nrf54l", "snps,dwc2"`, served by `drivers/usb/udc/udc_dwc2.c` with the nRF54L glue `udc_dwc2_nrf_usbhs_nrf54l.h` [SRC 1, SRC 5]. The driver reports the speed found at bus reset (`UDC_BUS_SPEED_HS` or `UDC_BUS_SPEED_FS`, see the full-speed rule below) and detects VBUS through the USB regulator events (`UDC_EVT_VBUS_READY`, `UDC_EVT_VBUS_REMOVED`) [SRC 5]. The development kit enables it as `zephyr_udc0` [SRC 9].
- Stack: Zephyr's USB device stack "device_next" (`usbd_init()`, `usbd_enable()`, `usbd_msg_register_cb()`, `USBD_DEVICE_DEFINE`, `USBD_DEFINE_CLASS`, `usbd_ep_enqueue()`) [SRC 8].
- **Class: one vendor-specific interface** (class 0xFF, subclass 0x00, protocol 0x00), written for this product with `USBD_DEFINE_CLASS`, with 1 bulk OUT endpoint (0x01) and 1 bulk IN endpoint (0x81). Two descriptor sets: **full speed, `wMaxPacketSize` = 64 bytes** (the case's host is full speed, below); high speed, `wMaxPacketSize` = 512 bytes. The configuration is registered for both speeds with `usbd_add_configuration(..., USBD_SPEED_FS, ...)` and `usbd_add_configuration(..., USBD_SPEED_HS, ...)` [SRC 8]. The class picks its endpoint descriptors with `usbd_bus_speed()`, as the stack's own `loopback.c` does [SRC 16]. The `loopback.c` class is the model (section 10.2).
- **Full-speed host (the case).** The case's chip, ESP32-S3-MINI-1-N8, is a USB 2.0 full-speed host only (`design/case/case-architecture.md` section 1). What the Zephyr stack does then, from the sources [SRC 16]: after each bus reset the DWC2 driver reads the enumerated speed from the core's DSTS register (`priv->enumspd = usb_dwc2_get_dsts_enumspd(dsts)`); `udc_dwc2_device_speed()` returns `UDC_BUS_SPEED_FS` for the full-speed values and `UDC_BUS_SPEED_HS` only for `USB_DWC2_DSTS_ENUMSPD_HS3060`; `usbd_core.c` stores `USBD_SPEED_FS` in `status.speed` when the controller is not at high speed; `usbd_ch9.c` then serves the full-speed configuration descriptors (`uds_ctx->fs_desc`). So the ring enumerates as a full-speed device with the 64-byte bulk endpoints, and no firmware switch is needed. Whether the nRF54LM20A's USBHS PHY falls back to full speed on the wire when the host sends no high-speed chirp is a hardware fact not documented in what was read (section 10.5); case bench test B1 (`design/case/case-architecture.md` section 1, supplier item S2) proves it.
- **Contact pads**: four pads on the INSIDE face of the band, at the point opposite the block (180 degrees), in a row around the band, set in the resin liner and not in the metal body (architecture 17.12, which replaces 17.3 and 17.8: F3 had them on the outside of the band at -150 degrees), in the order VBUS, D-, D+, GND (the same name order as the case pins P1 to P4 in `design/case/case-architecture.md` section 6). Pitch and pad size are measured in the rebuild of 17.12 and are not stated here; hardware issue H10 about the axis wording is replaced by 17.12's "in a row around the band". They touch the skin when the ring is worn: section 8.6.
- Not chosen: mass storage (`usbd_msc.c` exists [SRC 8]) needs a file system the case would mount, and the raw layout of section 5 has none; it also gives no confirm-then-delete step. CDC ACM adds a serial line layer for no gain.
- The ring answers USB only in `CHARGING` / `TRANSFER` and `FACTORY_TEST`; the USB device stack runs only while VBUS is present (section 8.6). It enters `TRANSFER` on `USBD_MSG_CONFIGURATION` [SRC 8].

### 6.2 Message layout

Every request and every response starts with this 16-byte header, followed by `length` payload bytes:

| Offset | Size | Field |
|---|---|---|
| 0 | 2 | magic 0x5252 |
| 2 | 1 | opcode |
| 3 | 1 | status (0 in requests) |
| 4 | 4 | tag (chosen by the case, echoed in the response) |
| 8 | 4 | length of the payload in bytes |
| 12 | 4 | crc32 of the payload (0 when length is 0) |

- The case sends one request, then reads exactly 16 + `length` bytes of response. No zero-length packet ends a transfer; the length field does.
- Status codes: 0 OK, 1 BAD_MAGIC, 2 BAD_CRC, 3 UNKNOWN_OPCODE, 4 BAD_ARG, 5 NOT_FOUND, 6 NOT_CONFIRMED, 7 BUSY, 8 STORAGE_ERROR, 9 DIGEST_MISMATCH, 10 FW_ERROR, 11 NOT_ALLOWED.
- A request with a wrong magic or CRC gets a response with that status and no payload.

### 6.3 Commands

| Opcode | Name | Request payload | Response payload |
|---|---|---|---|
| 0x01 | GET_INFO | none | protocol version u16 (1), fw_version u32, device id u64 (FICR), card_sectors u32, chunk_count_total u32, free_chunks u32, recordings u32 (not deleted), boot_count u32, factory flag u8 = 35 bytes |
| 0x02 | LIST_RECORDINGS | first u32 (0 = oldest not deleted), max u16 (1 to 64) | count u16, then count x 64-byte entries: recording_id u32, type u8, channels u8, state u8 (1 new, 2 transferred, 3 recovered), reserved u8, first_chunk_seq u32, chunk_count u32, sample_rate_hz u32, start_utc_ms i64, duration_frames u64, digest u32, highlight_count u16, reserved u16, reserved 20 bytes |
| 0x03 | READ_RANGE | recording_id u32, first_chunk u32 (0-based in the recording), chunk_count u32 (1 to 256) | chunk_count x 33,280 bytes: each chunk exactly as stored (header sector + payload) |
| 0x04 | CONFIRM | recording_id u32, digest u32 (computed by the case) | none (status OK or DIGEST_MISMATCH) |
| 0x05 | DELETE | recording_id u32 | free_chunks u32 after the deletion |
| 0x06 | SET_TIME | utc_ms i64, tz_offset_min i16 | none |
| 0x07 | GET_BATTERY | none | battery_mv u16, soc_percent_x10 u16, charging state u8 (0 off, 1 trickle, 2 constant current, 3 constant voltage, 4 full, 5 error), die temp 0.1 °C i16, time to full in min u16 |
| 0x08 | FW_BEGIN | image_size u32, image_crc32 u32 | none; erases the secondary slot (section 9.2) |
| 0x09 | FW_DATA | offset u32, then 1 to 4,096 image bytes | none |
| 0x0A | FW_END | none | none; verifies the CRC, requests the upgrade, the ring reboots after sending OK |
| 0x0B | GET_LOG | first record u32, max u16 (1 to 32) | count u16, then count x 512-byte log records (section 9.4) |
| 0x0C | REBOOT | none | none |
| 0x0D | FACTORY | sub-command u8, arguments (section 9.3) | test result (section 9.3); NOT_ALLOWED when the factory flag is clear |

- The case sends SET_TIME and GET_BATTERY first on every insertion, then LIST_RECORDINGS.
- The ring answers BUSY when a command arrives while the previous one is still running.

### 6.4 Resume and integrity

- Chunks never change after they are written, until DELETE. So the case resumes by keeping (recording_id, next chunk) in its own storage and sending READ_RANGE from that chunk. No state is kept on the ring for a transfer.
- On each chunk the case checks magic, `header_crc32`, `payload_crc32`, `recording_id` and that `chunk_in_recording` is the expected one. On a failure it reads that chunk again, up to 3 times, then reports the recording as failed and does not CONFIRM it.
- When the last chunk arrives, the case computes the digest (section 5.4) from the `payload_crc32` values it received and sends CONFIRM. Only after OK does it upload the recording and send DELETE. Fixed rule: the case sends DELETE only after the recording is stored on the case's own storage and the case has checked every chunk CRC again from that copy.
- Transfer time at full speed [CALC]: stored bytes per recorded hour of 2-channel audio = 3,600 s / 0.512 s = 7,031.25 chunks x 33,280 bytes = 234,000,000 bytes. At the full-speed bulk ceiling of 1.216 MB/s used by the case (19 packets of 64 bytes per 1 ms frame; a USB 2.0 figure the case document marks as not read) this is 234.0 / 1.216 = 192.4 s = **3.21 minutes per recorded hour**; a 10-hour day (not reachable on any cell of US 7 to 13, at most 8.0 hours, section 8.5) would take 32.1 minutes, and a full 4 GB card (16.9 hours) 54.2 minutes. The audio alone, 230.4 MB, takes 3.16 minutes; the 0.05 minutes more are the chunk header sectors (1 in 65). The case document's 6.32 minutes and architecture section 8's 6.3 minutes count the F2 audio of four channels and are out of date (hardware issue H11). The card's read over SPI (at most 2.0 MB/s raw at 16 MHz) is no longer the limit. **[BENCH]** test S2 measures the card read rate; case bench test B1 measures the end-to-end rate.

## 7. Bluetooth

F7 part 2 (2026-11-11). Standard Bluetooth services come first (`design/software/os/design.md` section 2): the ring is a Bluetooth keyboard, media remote and pointer for up to three paired devices, one of them active. The home-made link protocol (design/protocol/) stays paused; nothing of it is here. The iPhone services (notifications, media, time) are section 7.6, built by software step 3. What the software has built and tested of this section is listed in `firmware/docs/devices-control-notes.md` and `firmware/docs/step2-round3.md`; this section is the rule, built or not.

### 7.1 Stack and role

- Peripheral role only, one connection at a time: the link of the active device (section 7.4). Zephyr Bluetooth host with the nRF Connect SDK controller (section 10.5: support of this chip by the controller is not checked here). TX power 0 dBm. LE data length extension on (`CONFIG_BT_USER_DATA_LEN_UPDATE` [SRC 15]), ATT MTU 247.
- Bluetooth carries keys and pointer moves to the active device (sections 7.2 and 7.5), and the control, status, time and small files of the ring service. Recordings over 64 chunks go through the case.
- No message of any Bluetooth service can start or stop a recording (owner, F2: only a long press does).

### 7.2 Services and characteristics

Standard services from Zephyr: Battery Service 0x180F (`subsys/bluetooth/services/bas`) and Device Information 0x180A (`subsys/bluetooth/services/dis.c`) [SRC 10].

Human Interface Device service 0x1812 (nRF Connect SDK, `CONFIG_BT_HIDS`). Three input reports, no output report, no boot protocol:

| Report ID | Use | Length without the ID | Layout |
|---|---|---|---|
| 1 | keyboard | 8 bytes | modifiers u8, reserved u8, six key usages u8 (usage page 0x07); all 0 = released |
| 2 | consumer control | 2 bytes | one usage u16 (usage page 0x0C); 0 = released |
| 3 | pointer | 3 bytes | buttons u8 (bit 0 = button 1), dx i8, dy i8 (negative dy is up) |

- Every report characteristic needs an encrypted, authenticated link (security level 4, section 7.4; `CONFIG_BT_HIDS_DEFAULT_PERM_RW_AUTHEN`).
- No HID report and no write to the HID control point is a command to the ring: a host write is counted and changes nothing.

Ring service, UUID `a3c10000-5b7e-4f2a-9c1d-7e2b6f4d8a90` (fixed for this product). Every characteristic needs an encrypted, authenticated link (security level 4, section 7.4):

| Characteristic | UUID | Properties | Layout |
|---|---|---|---|
| Control | `a3c10001-5b7e-4f2a-9c1d-7e2b6f4d8a90` | write with response | opcode u8: 0x01 highlight (only in `RECORDING`); no arguments. Bluetooth cannot start or stop a recording (owner, F2: only a long press does). A refused command returns ATT error 0x80 (application error) |
| Status | `a3c10002-5b7e-4f2a-9c1d-7e2b6f4d8a90` | read, notify | 20 bytes: state u8 (index in the table of section 1.1, `SHIP` = 0), battery % u8, battery_mv u16, free_chunks u32, open recording_id u32 (0 = none), elapsed s u32, highlight_count u16, flags u8 (bit 0 recording, bit 1 charging, bit 2 time not set), reserved u8. Notified on every state change and every 10 s while connected |
| Time | `a3c10003-5b7e-4f2a-9c1d-7e2b6f4d8a90` | write with response | utc_ms i64, tz_offset_min i16 (10 bytes), same meaning as USB SET_TIME |
| Fetch control | `a3c10004-5b7e-4f2a-9c1d-7e2b6f4d8a90` | write with response, notify | request: opcode u8 + arguments: 0x01 LIST (first u32), 0x02 FETCH (recording_id u32, first_chunk u32), 0x03 CONFIRM (recording_id u32, digest u32), 0x04 DELETE (recording_id u32), 0x05 CANCEL. Notify: opcode u8, status u8 (codes of section 6.2), then the same payload as the USB response (LIST: up to 3 entries of 64 bytes per notification) |
| Fetch data | `a3c10005-5b7e-4f2a-9c1d-7e2b6f4d8a90` | notify | byte offset u32 in the chunk stream, then 240 bytes of chunk data (the last packet shorter). The chunks are the stored 33,280-byte chunks, as over USB |

- Small-file rule: FETCH is allowed for a recording of at most 64 chunks (64 x 33,280 = 2,129,920 bytes, about 2.1 MB: 33 s of audio [CALC: 64 x 0.512 s]); a longer one returns NOT_ALLOWED.
- Resume, integrity, CONFIRM and DELETE follow section 6.4.

### 7.3 Advertising

| States | Advertising |
|---|---|
| `STANDBY`, `RECORDING`, `ERR_STORAGE_FULL`, `ERR_BATTERY_LOW`, `ERR_STORAGE_FAULT`, `ERR_MIC_FAULT`, with at least one paired device | connectable, on the local identity of the active device's slot (section 7.4). Interval 100 ms (160 x 0.625 ms) for the first 30 s after a boot, a dropped link or a change of the active device, then 1,000 ms (1,600 x 0.625 ms). Only the device paired on the active slot may connect (filter accept list, `CONFIG_BT_FILTER_ACCEPT_LIST` [SRC 15]) |
| The same states with no paired device | none until the pairing window opens |
| Pairing window (SCR_PAIR open, 60 s) | connectable, 100 ms interval (160 x 0.625 ms), open to any device, on the local identity of the free slot being paired |
| `SHIP`, `OFF`, `BOOT`, `RECOVERY`, `CHARGING`, `TRANSFER`, `ERR_CHARGER`, `FACTORY_TEST` | none (the radio test of section 9.3 advertises on its own) |

- Stranger rule: outside the pairing window, a link whose peer is not the device paired on the active slot is ended by the ring within 1 s, before any pairing request is answered. It holds with or without the filter accept list (simulation: 102 ms).
- Connection parameters requested by the ring: interval 30 to 50 ms, peripheral latency 4, supervision timeout 4 s; during FETCH, interval 7.5 to 15 ms, latency 0.
- Advertising data (11 bytes): flags; appearance 961 (keyboard); complete list of 16-bit service UUIDs with 0x1812 (Apple's accessory rule: the HID service is in the advertising data).
- Scan response (29 bytes): complete local name "Ring" plus the last 4 hex digits of the device id; the ring service UUID.

### 7.4 Pairing, bonding, security

- LE Secure Connections only (`CONFIG_BT_SMP_SC_ONLY` [SRC 15]). IO capability: display only. The ring shows a 6-digit passkey on SCR_PAIR; the user types it on the other device. Result: authenticated, encrypted link = security mode 1, level 4.
- Pairing is accepted only while SCR_PAIR is open (60 s, opened from the menu, for one free slot; `CONFIG_BT_SMP_APP_PAIRING_ACCEPT`). Outside it, pairing requests are rejected.
- Paired devices: at most 3 (`CONFIG_BT_MAX_PAIRED=3`, `CONFIG_BT_ID_MAX=3`). Each has its own slot 0, 1 or 2, with one local Bluetooth identity and one bond per slot, stored with Zephyr settings in RRAM. F6 had 2 bonds and removed the oldest; F7 removes nothing by itself.
- With three paired devices SCR_PAIR does not open and a fourth pairing is refused. The wearer first removes a device on SCR_DEVICE (section 3.4).
- Removing a paired device deletes its bond (the keys of both sides) and ends its link.
- Active device: exactly one slot is active; the wearer picks it on SCR_DEVICE (section 3.4). A newly paired device becomes the active one only when no device is active (F7 part 4). When one is active it stays active, its identity and its bond are kept, and no change of the active device is reported; the wearer makes the new device the active one with "Use" on SCR_DEVICE. A change of the active device ends the link, changes the local identity and advertises to the chosen device (section 7.3). A key or a pointer move is sent only over a level 4 link of the active device; from the change until that link is up, nothing is sent.
- Privacy on (`CONFIG_BT_PRIVACY` [SRC 15]), resolvable private address renewed every 15 minutes (`CONFIG_BT_RPA_TIMEOUT=900` [SRC 15]).

### 7.5 Control modes

Four modes. The plan's three (media, presenter, pointer) and a fourth, agent, from the owner's words of 2026-11-11: "You can even control claude code with it". The wearer picks the mode on SCR_MODES and the active device on SCR_DEVICES (section 3.4). In an open control session each joystick action sends this to the active device:

| Mode | Centre, short press | Up | Down | Toward the hand (left) | Toward the fingertip (right) |
|---|---|---|---|---|---|
| Media | play or pause (consumer 0x00CD) | volume up (0x00E9) | volume down (0x00EA) | previous track (0x00B6) | next track (0x00B5) |
| Presenter | nothing | previous slide (Left Arrow 0x50) | next slide (Right Arrow 0x4F) | previous slide (Left Arrow 0x50) | next slide (Right Arrow 0x4F) |
| Pointer | click (button 1) | move up 16 units | move down 16 units | move left 16 units | move right 16 units |
| Agent | accept (Return 0x28) | Up Arrow 0x52 | Down Arrow 0x51 | decline (Escape 0x29) | accept (Return 0x28) |

- Presenter option `presenter_pages`: Page Up 0x4B and Page Down 0x4E replace the Left and Right Arrow keys.
- Agent mode sends these keys only. It types no text.
- A key goes out only for a real action of the wearer on the joystick (Apple's accessory rule), only while a control session is open (section 3.4), and only for these five actions.
- The centre long press sends nothing to any device in any mode: it belongs to the recorder (section 2.1). In `RECORDING` a centre short press is a highlight and sends nothing either.
- A held direction repeats as in section 2.2 (after 500 ms, then every 150 ms).
- Every key, usage or button press is followed by its release report. A release that fails to send is retried every 50 ms, at most 20 times; during that wait (at most 1 s) the wearer's next action is dropped. If the link is gone, the release is dropped with it.

### 7.6 Apple's services (the iPhone part)

The ring is the Bluetooth client of the iPhone for three Apple services. Apple's documents give the data formats; the nRF Connect SDK v3.4.2 gives the client code. Nothing here starts or stops a recording: the iPhone part calls nothing in the core (rule of section 7.1).

- **When.** After the link of the active device reaches security level 4 (section 7.4) the ring looks, one after the other, for the GATT service (to subscribe to Service Changed), Apple Notification Center Service (UUID 7905F431-B5CE-4E99-A40F-4B1E122D00D0), Apple Media Service (89D3502B-0F36-433A-8EF4-C502AD55F8DC) and Current Time Service (0x1805). A service that is not there (an Android phone, a Mac) is "not found": no error, no retry, the inbox stays empty, an action returns "no such notification" and a media command returns "not connected".
- **Discovery and links.** A discovery that is running when the link ends is dropped with its session: it counts no service as missing and does not move the next session, which looks for the three services again.
- **Service Changed.** When it is indicated the ring stops the three services (unsubscribes; the inbox and the media record are emptied), then looks for the three services again and subscribes to those it finds. Apple: the Notification Center Service is not guaranteed to be present at any time.
- **Sessions.** The inbox, the media record and the services' subscriptions live for one link (or until Service Changed). When the link ends everything stored from the iPhone is emptied. After a reconnect the ring subscribes again and rebuilds the inbox from the notifications the iPhone sends again (Apple: the service keeps no state across sessions). The clock is not emptied.
- **Inbox.** The last 16 notifications, newest first; the 17th pushes the oldest out. Per notification: the iPhone's id (u32), category (0..11), flags (silent, important, pre-existing, has a positive action, has a negative action: Apple's EventFlags bits 0 to 4), application identifier (at most 48 bytes), title (48), message (160), date (15 characters, `yyyyMMdd'T'HHmmSS`), a read mark. All strings are UTF-8, NUL terminated and cut at a character boundary, never inside one. Added makes a new entry (the same id replaces the old entry and moves it to the front); Modified replaces category, flags and text and keeps the place (an id that is not held is ignored); Removed deletes the entry.
- **Attributes.** For each Added or Modified event the ring asks for the application identifier, the title (maximum length 48), the message (maximum length 160) and the date, one request at a time, 13 bytes; the answer may come in any number of fragments and is spliced. A request without an answer in 3 s, with a wrong answer or whose write fails is asked for once more; after the second failure it is given up. Bytes that are not the answer to the request in flight (for example a late answer of the earlier request) are skipped.
- **Actions.** `rip_action(id, positive|negative)` sends Perform Notification Action (CommandID 2, id, ActionID 0 or 1). A dismiss chosen on the ring is the negative action. An action for a notification that does not have that action (its flag is not set) is refused and sends nothing. The ring's inbox changes only when the iPhone reports the removal.
- **Media.** The ring registers for the player's PlaybackInfo and the track's artist and title. It stores the track title (at most 64 bytes), the artist (48) and the player state (paused or playing: state 0 or 1 of PlaybackInfo) as the iPhone reports them. `rip_media_command` sends Remote Command play 0, pause 1, next track 3, previous track 4, volume up 5, volume down 6. The stored state changes only on the iPhone's report, never on the ring's own command (Apple: a written command does not prove that the player acted). The Media control mode of section 7.5 keeps its keyboard-style keys.
- **Time.** After the link is ready the ring subscribes to Current Time, reads Local Time Information (zone in 15-minute units, daylight saving offset) and then Current Time. The ring's clock (milliseconds, a "time is set" flag and a "zone known" flag, section 9.1) holds UTC = the iPhone's local time minus zone minus daylight offset, with the offset in minutes, and is set again at each Current Time notification (the zone is read again after each). The time value is paired with the moment it arrived, so a zone read that returns later moves nothing. When the iPhone gives no zone (no such characteristic, or the unknown values) the clock keeps the local time and the "zone known" flag is false. A zone read that fails after a good one keeps the last zone of that link and is counted.
- **Link settings.** ATT MTU 247 (section 7.1); attribute answers are fragmented by the sender to the negotiated MTU.
- **Where it shows.** The screens that show the inbox and the media state, and the controls that call the dismiss and the media commands, come with software step 4; until then these are functions with tests only.
- **Not proven.** Nothing of this section ran against a real iPhone. The formats that rest only on Nordic's kit code, and the Local Time Information layout, are listed in `firmware/docs/step3-round2.md` section 8.

### 7.7 Relay service (notifications from a helper app; F7 part 5, software step 5)

Android has no standard Bluetooth service for notifications (`design/software/os/research-platforms.md` section 4). A helper app on the phone reads the notifications with the user's permission and writes them to this service of the ring. The helper app is specified in `design/software/os/android-helper-spec.md`; it is not built. Nothing here starts or stops a recording: the relay part calls nothing in the core (rule of section 7.1).

Relay service, UUID `a3c20000-5b7e-4f2a-9c1d-7e2b6f4d8a90` (fixed for this product; the ring is the GATT server). Every characteristic needs an encrypted, authenticated link (security level 4, section 7.4). All numbers are little endian.

| Characteristic | UUID | Properties | Use |
|---|---|---|---|
| In | `a3c20001-5b7e-4f2a-9c1d-7e2b6f4d8a90` | write with response | frames from the helper to the ring |
| Out | `a3c20002-5b7e-4f2a-9c1d-7e2b6f4d8a90` | notify | frames from the ring to the helper |
| Info | `a3c20003-5b7e-4f2a-9c1d-7e2b6f4d8a90` | read | 6 bytes: protocol version u8 (1), store size u8 (16), application identifier limit u8 (48), title limit u8 (48), message limit u8 (160), date length u8 (15) |

Frames written to In (the first byte is the opcode):

| Opcode | Name | Bytes after the opcode | Meaning |
|---|---|---|---|
| 0x01 | HELLO | version u8 | the helper starts a session. The ring empties what the relay stored and answers READY on Out |
| 0x02 | PUT | id u32, total u16, offset u16, then data bytes | one piece of the record of notification `id`. `total` is the length of the whole record, `offset` the place of this piece. Pieces arrive in order, the first with offset 0; a piece with offset 0 drops an unfinished record and begins a new one. The record is stored when offset plus the data length equals `total` |
| 0x03 | REMOVE | id u32 | the phone removed the notification |
| 0x04 | CLEAR | none | the phone has no notification left: the ring empties what the relay stored |

The record of a PUT: category u8 (the values of section 7.6, 0 to 11; the ring does not read the category, and a value above 11 is stored as received, never refused), flags u8 (the bits of section 7.6: silent 0, important 1, pre-existing 2, has a positive action 3, has a negative action 4; the other bits must be 0), then fields, each as type u8, length u8, bytes: type 1 application identifier, 2 title, 3 message, 4 date (`yyyyMMdd'T'HHmmSS`). Each type at most once, in any order; a missing field is empty. A record is at least 2 and at most 512 bytes. A text longer than its limit is cut at a character, as in section 7.6. A PUT for an id that is stored replaces that notification and keeps its place and its read mark; a new id goes to the front, and the 17th pushes the oldest out.

Frames notified on Out:

| Opcode | Name | Bytes after the opcode | When |
|---|---|---|---|
| 0x81 | READY | version u8 (1), store size u8 (16) | after HELLO |
| 0x82 | ACTION | id u32, action u8 (0 positive, 1 negative) | the wearer chose an action on the ring |
| 0x83 | ERROR | code u8, id u32 (0 when none) | a frame was refused |

- **Refusals.** A frame that is refused changes nothing in the store. The write is answered with ATT error 0x80 and, when the helper has subscribed to Out, ERROR is notified. Codes: 1 unknown opcode or wrong frame length; 2 no HELLO in this session; 3 PUT piece out of order or beyond `total`; 4 `total` under 2 or over 512; 5 record malformed (a field runs past the end, a type is unknown or repeated, a flag bit above 4 is set); 6 version not supported; 7 the link's notifications come from Apple's service.
- **Sessions.** The relay's notifications live for one link, as in section 7.6: when the link ends they are emptied, and the helper sends HELLO and its notifications again after it reconnects (those that were already there with the pre-existing flag). A PUT that is not finished when the link ends is dropped.
- **One source per link.** The inbox of section 7.6 is the one store for both sources; the screens read it and do not know the source. The first of the two that is used on a link fixes the source of that link until the link ends. Apple's notification service found first: every relay frame on that link is refused with code 7. A relay HELLO accepted first: the ring does not use Apple's notification service on that link, also when it finds that service later, and relay frames stay accepted (a device with a helper app is not an iPhone; the case is built and tested so that neither source can write into the other's store).
- **Actions.** A dismiss chosen on the ring is the negative action. The ring notifies ACTION and changes nothing in the store; the entry leaves when the helper sends REMOVE. An action that the notification does not have (its flag is not set) is refused on the ring and sends nothing. With no subscription to Out the action is refused on the ring.
- **Read mark.** The read mark lives on the ring only.
- **Details (lead's answers to the questions of the helper specification, 2026-11-12).** The date is the phone's local time; its last two digits are the seconds; the ring stores the date like every text (up to 15 bytes, cut at a character, ended at a zero byte) and does not read it; the 15 digits and the letter T of the format are stored unchanged. A PUT carries at least 1 data byte and may carry as many as the link allows; the ring accepts every piece size. CLEAR may be sent at any time in a session, also when the user takes the notification permission away on the phone. HELLO starts a session also when the helper has not subscribed to Out; READY is then not delivered, so the helper subscribes first. An accepted HELLO drops every frame that still waits for Out from before it, so READY always has room. A frame that is already being sent at that moment can still arrive before READY: the helper ignores every Out frame between its HELLO and READY. An ACTION frame that was queued and then cannot be sent after its retries is lost; the notification stays on the ring until the helper removes it. An action whose ACTION frame cannot be queued for Out is refused on the ring, like an action with no subscription. A frame is one write: a write longer than the link's payload (a prepared or long write) is refused with the ATT error for an invalid offset, not with 0x80. The ring does not sort by date: the order is the order of arrival, newest first. The positive action is reachable on the ring: Right on SCR_NOTIF (section 2.2). The advertising of section 7.3 is unchanged: the helper finds the ring by its name or its bond and the relay service by discovery.
- **Not built in step 5:** the helper app; media and time from an Android phone (the Media screen shows the track only with an iPhone); the status, time and file characteristics of the ring service of section 7.2.

## 8. Power management

### 8.1 nPM1304 settings (devicetree, Zephyr nPM13xx drivers)

The power chip is the Nordic nPM1304, U2, order code nPM1304-CAAA-R7 (architecture 17.13 and 17.18). Drivers: the Zephyr nPM13xx family `drivers/mfd/mfd_npm13xx.c`, `drivers/regulator/regulator_npm13xx.c`, `drivers/sensor/nordic/npm13xx_charger/npm13xx_charger.c` [SRC 11]. Fuel gauge: nRF Connect SDK library `nrf_fuel_gauge` [SRC 12]. The only nPM1304 binding text on disk is the charger page as quoted in `design/parts/research-npm1304.md` [SRC 17]; it confirms the compatible `"nordic,npm1304-charger"` and the properties `current-microamp`, `term-microvolt` and `term-current-percent`. Every other property name below is the F4 name of the same nPM13xx driver family and is marked **TO CONFIRM**: the firmware designer reads the nPM1304 binding files of the nRF Connect SDK version the build pins before work item W1 (section 10.5, item 3). Where the chip function behind a property is confirmed by the specification, the page is given. No property is added that F4 did not have, except the charger's compatible, which [SRC 17] confirms.

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
| | `current-microamp` | `CHARGE_CURRENT` = 15,000 (15 mA, architecture 17.13: 1 C of the smallest cell of the range, kept until the cell's maker states its own limit, open item S12). The chip takes 4 to 100 mA in 0.5 mA steps [NPM p24, p29]. On the smallest cell, 17.6 mAh (US 7, architecture 17.26), 15 mA is 0.85 C; on the largest, 31.9 mAh (US 13), 0.47 C [CALC: 15 / 17.6 = 0.852, 15 / 31.9 = 0.470]. With the chip's accuracy of plus or minus 10 % [NPM p29] the current is 13.5 to 16.5 mA, at most 0.94 C on 17.6 mAh [CALC: 16.5 / 17.6 = 0.9375] | [SRC 17] |
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
2. **`CHARGE_CURRENT` is one named constant**, set in one place, in microamps: 15,000. A build fails to compile when it is unset, above 17,600 (1 C of the smallest cell, 17.6 mAh, architecture 17.26), under 4,000 or over 100,000, or not a multiple of 500 [NPM p24]. The firmware disables the charger before it writes the current register and enables it after [NPM p24: "CHARGER must be disabled before changing the current setting in register BCHGISET"].
3. **Charge time per ring size** [CALC: capacity / 15 mA; this is the constant-current time, a lower bound: the constant-voltage end adds time until the current falls to 1.5 mA, and in the cool region the current is 7.5 mA and the time doubles]. The chip's charge timeout, 7 hours for constant current and constant voltage together [NPM p30], is above every row.

| Ring size | Battery (architecture 17.26, measured) | Charge time at 15 mA from empty [CALC] |
|---|---|---|
| US 7 | 17.6 to 23.5 mAh | 1.17 to 1.57 hours |
| US 8 | 18.9 to 25.3 mAh | 1.26 to 1.69 hours |
| US 9 | 20.3 to 27.1 mAh | 1.35 to 1.81 hours |
| US 10 | 21.2 to 28.3 mAh | 1.41 to 1.89 hours |
| US 11 | 22.1 to 29.5 mAh | 1.47 to 1.97 hours |
| US 12 | 23.0 to 30.7 mAh | 1.53 to 2.05 hours |
| US 13 | 23.9 to 31.9 mAh | 1.59 to 2.13 hours |

4. **Leaving ship mode on first power stays** (row `SHIP`, VBUS appears, section 8.4): the exit is by VBUS only.
5. The thermistor limits and the die-temperature limits stop and resume charging by themselves (rows above); they are not a reason to hold the charger off.

### 8.2 What is on in each state

| State | VDD_1V8 | VDD_3V0 | VDD_MIC | VDD_SD | Screen supply (OLED_PWR_EN) | HFXO | Radio | Wake sources |
|---|---|---|---|---|---|---|---|---|
| `SHIP`, `OFF` | off | off | off | off | off | off | off | VBUS only (section 8.4) |
| `BOOT`, `RECOVERY` | on | on | off | on | on in `RECOVERY` | on | off | runs to completion |
| `STANDBY` | on | on | off | off | when the screen is on | when the radio runs | advertising | the 4 direction inputs (JOY_UP, JOY_DOWN, JOY_LEFT, JOY_RIGHT) and BTN_REC when `CENTRE_SOURCE` is `SW2`, PMIC_INT, GRTC timer, radio |
| `RECORDING` | on | on | on | on | on for the whole recording (rule R-SIGN, section 3.2) | on | advertising | PDM blocks every 16 ms, as `STANDBY` |
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
1. Close everything (recording, storage, USB, radio, screen); save the settings and the time in RRAM. If the storage cannot be unmounted within its wait (a USB command still holds it), USB is closed first and the unmount is tried once more; ship mode then goes on in any case, with the event 0x0290 logged (the supply of the storage is cut by ship mode itself). The wait for the screen to blank is at most 1,000 ms **[CHOICE]**; ship mode never waits longer for the screen (rulings of 2026-11-13 after review 2 of step 6, findings R2-04 and R2-05). SHIP_ENTER first clears the factory flag; SHIP_SAMPLE keeps it at 1.
2. Write SHPHLDCONFIG with the default press time (96 ms) and trigger TASKSHPHLDCFGSTROBE: the specification requires both before ship mode [NPM p116, p118].
3. If VBUS is present, wait for the event EVENTVBUSREMOVED (register EVENTSVBUSIN0SET, [NPM p136]), reported on PMIC_INT. While it waits the ring does nothing else: no screen, no radio, no storage, the USB stack is disabled on `UDC_EVT_VBUS_REMOVED` (section 8.6). Only the factory commands reach this step with VBUS present: every row into `OFF` starts from a state without VBUS (section 1.2).
4. Write TASKENTERSHIPMODE = 1 [NPM p118]. The chip isolates the battery and the main chip loses its supply.
5. If the main chip still runs 1 s after step 4 **[CHOICE]**, it logs the event and goes back to step 3 once; the jig of section 9.3 sees advertising stop or not and reports a fail.

Exit: a voltage on VBUS above VBUSPOR, 3.9 V [NPM p17, p116]. Holding SHPHLD low for 96 ms also wakes the chip [NPM p116, p117], but SHPHLD sits on test pad TP19 (netlist.csv), which is closed under the board after assembly step 17, so in use only the case wakes the ring. After a wake the chip resets and sets the bit SHIPMODEEXIT in RSTCAUSE [NPM p146]; `BOOT` logs it (section 8.7).

Current in ship mode: 370 nA typical for the nPM1304 [NPM p11] plus U11, at most 1 µA (motor-drive.md section 2.7). The cell protection circuit's own drain is not stated (S12).

### 8.5 Expected current per state (architecture 17.15, 17.19 and 17.26, the current ring)

| | Recording | Standby |
|---|---|---|
| From the cell | about 4.1 mA [CALC: 4.0 + 2 x (0.63 - 0.58)] | about 0.03 mA |
| Hours on the smallest cell, 17.6 mAh at US 7 [CALC] | 4.3 | 587 (24.4 days) |
| Hours across US 7 to 13, 17.6 to 31.9 mAh [CALC] | 4.3 to 7.8 | 587 to 1,063 (24.4 to 44.3 days) |
| Hours at a Plaud's 13 mA, 17.6 to 31.9 mAh [CALC] | 1.4 to 2.5 | |

Recording current: architecture 17.15 and 17.17 used 4.0 mA, which counts the old microphones at 2 x 0.58 mA; the SPK0641HT4H-1 draws 0.63 mA at 1.8 V [DS line 97], so F5 uses 4.0 + 2 x (0.63 - 0.58) = 4.1 mA. This counts the 0.10 mA rise as if drawn from the cell, an over-count: through the 1.8 V rail it is 2 x 0.05 x 1.8 / (3.8 x 0.9) = 0.05 mA from the cell [CALC]. Recording hours: 17.6 / 4.1 = 4.29 and 31.9 / 4.1 = 7.78. At 13 mA: 17.6 / 13 = 1.35 and 31.9 / 13 = 2.45. Standby at 0.03 mA: 17.6 / 0.03 = 587 hours = 24.4 days and 31.9 / 0.03 = 1,063 hours = 44.3 days. Per ring size at 4.1 mA [CALC, `design/firmware-f6-notes.md`]:

| Ring size | Battery (architecture 17.26, measured) | Recording hours at 4.1 mA |
|---|---|---|
| US 7 | 17.6 to 23.5 mAh | 4.29 to 5.73 |
| US 8 | 18.9 to 25.3 mAh | 4.61 to 6.17 |
| US 9 | 20.3 to 27.1 mAh | 4.95 to 6.61 |
| US 10 | 21.2 to 28.3 mAh | 5.17 to 6.90 |
| US 11 | 22.1 to 29.5 mAh | 5.39 to 7.20 |
| US 12 | 23.0 to 30.7 mAh | 5.61 to 7.49 |
| US 13 | 23.9 to 31.9 mAh | 5.83 to 7.78 |

Architecture 17.26 gives the same hours at 4.1 mA, rounded to one decimal (4.3 to 7.8 across the sizes).

Caveat, from architecture section 4 and 16.8: the main-chip, storage, radio and power-chip lines are estimates, not datasheet values, and bench test B2 replaces them; the microphone line is from the Knowles datasheet copy at its 2.4 MHz test clock, not at the ring's 1.280 MHz (section 10.5, item 6). The recording light is removed in v7 (architecture 17.30): the 4.0 mA of architecture 17.15 counted 1.5 mA for it, so without the light the computed recording figure is 4.1 - 1.5 = 2.6 mA [CALC] plus the always-lit red dot and timer of section 3.2, whose cost is a bench item on the new panel (architecture 17.30) with no number yet. The thresholds of 1.1 and the hours of this section stay computed at 4.1 mA, the figure of architecture 17.26, until that bench result and a restated architecture figure **[CHOICE]**; 4.1 mA no longer counts a light. It excludes the motor (section 3.1) and the screen. **Requirement P2 (10 hours of recording) is NOT met by this ring**: the owner chose thinness over hours on 2026-11-10 (architecture 17.5). In every state other than `RECORDING` the microphones are off.

**R19 (the recording figure after v7, the lead's ruling after design review 3).** The 4.1 mA of this section stays the planning figure and now reads: 2.6 mA computed for the ring with the light removed, plus an allowance of 1.5 mA for the lit sign of section 3.2 (the red dot and the timer at the lowest brightness level). The allowance equals the removed light's 1.5 mA and is not measured. The bench plan's test T2 (`design/bench/bench-plan.md`, version B2) measures the recording current with the sign shown. If the sign costs more than 1.5 mA, the hours of this section and the thresholds of section 1.1 are computed again from the measured figure (hours = cell capacity / current).

### 8.6 Pads on the inside of the band touch the skin (architecture 17.12)

The four pads are on the inside face of the band and touch the finger whenever the ring is worn, with no case present. What the firmware does:
1. **VBUS is an input only.** No GPIO, no regulator and no charger function of the firmware drives a voltage onto VBUS; nothing is driven onto any pad when no case is present. The only source of voltage on VBUS is the case.
2. **D+ and D- are not driven while worn.** The USB device stack is enabled (`usbd_enable()`) only after the power chip reports VBUS (`UDC_EVT_VBUS_READY`) and disabled (`usbd_disable()`) on `UDC_EVT_VBUS_REMOVED`; with VBUS absent the stack is off and the firmware sets no level on D+ or D- (what the chip's USB pins do when the peripheral is off is listed in section 10.5, item 29).
3. **A case is recognised only by VBUS** as reported by the power chip: no test pulse, no probing of the pads, no resistance measurement.
4. GND: nothing.
What the firmware does not do:
- It cannot tell skin or sweat from a case except through the power chip's own VBUS detection: VBUS counts as valid at 210 mV above VBAT, rising [NPM p17, VBUSVALIDR], and wakes the chip from ship mode above 3.9 V [NPM p17, VBUSPOR] (section 10.5, item 30). A voltage that high on the pads is treated as a case: in `RECORDING` it closes the recording (row `RECORDING`, VBUS appears).
- It does not protect the pads from corrosion or leakage through sweat: that is the wiring notes and the plating (17.12: gold-plated, flush with the liner), hardware issue H14.
- It has no switch of its own that opens the pads: whether a hardware switch is needed is for the wiring notes (17.12).

### 8.7 Battery current limit and reset causes of the nPM1304

- **The limit is fixed.** The nPM1304 limits the current it draws from the battery: IBATLIM, "Discharging battery current limit", 100 mA in the minimum column, "Validated through simulation" [NPM p29 and its footnote, p30]; the maximum VSYS load from the battery is also 100 mA [NPM p11]. No register sets it. Nordic: "It has not been designed for accurate current limiting", and "If the system load exceeds the discharge current limit, VSYS voltage drops below VSYSPOF causing the device to reset" [NPM p28].
- **What passes it.** Since 17.22 the motor does not. With the screen at full white, the radio, recording and a storage write together, the chip path stays at or under 55.7 mA down to 3.1 V (architecture 17.22; motor-drive.md section 2.4).
- **The status bit and what the firmware does.** Register BCHGILIMSTATUS, field BCHGILIMBATACTIVE, "Discharge current limiter active" [NPM p40]. The specification read names no interrupt for it, so the firmware reads it with every battery sample (section 8.3: every 1 s in `RECORDING`, every 60 s in the other awake states). When it reads ACTIVE:
  1. an event log record "battery current limit active" with battery_mv, the state and whether the screen is on;
  2. the screen goes off at once and stays off for 10 s, except in `RECORDING`, where it shows SCR_REC_DIM for those 10 s and never goes dark (rule R-SIGN, section 3.2) **[CHOICE]**: the screen is the largest load on the chip's path (motor-drive.md section 4);
  3. a recording goes on: nothing is closed and nothing is refused, because only a long press stops a recording (owner's rule) and a reset would end in `RECOVERY` anyway (section 5.5);
  4. no motor pattern is played for it.
  When it reads ACTIVE again with the screen already off, the event is logged once more with a count and nothing else changes.
- **Reset causes.** `BOOT` reads the nPM1304 register RSTCAUSE [NPM p146] (bits SHIPMODEEXIT, BOOTMONITORTIMEOUT, WATCHDOGTIMEOUT, LONGPRESSTIMEOUT, THERMALSHUTDOWN, VSYSLOW, SWRESET) and the charger error log CHARGERERRREASON and CHARGERERRSENSOR [NPM p146], writes them into the event log beside the main chip's own reset reason (section 9.4), then clears them with TASKCLRERRLOG [NPM p145]. VSYSLOW means a power-fail reset (VSYS under VSYSPOF): a load above the limit or an empty cell. After a thermal shutdown VSYSLOW can be set instead of THERMALSHUTDOWN [NPM p144].
- **Power-fail warning: not used** **[CHOICE]**. POFCONFIG stays at its reset value (warning off) and VSYSPOF at its default falling threshold, 2.7 V [NPM p109]. The warning needs a power-chip GPIO wired to the main chip [NPM p107, p108]; the only one wired is GPIO0, which is PMIC_INT (netlist.csv). B2 at 3.30 V closes the files first (section 1.1).

## 9. Time keeping, firmware update, factory test, logging

### 9.1 Time keeping

- Base: the GRTC system timer of the nRF54LM20A [SRC 1] running from the 32.768 kHz crystal (20 ppm, architecture section 2: up to 1.73 s per day [CALC: 20e-6 x 86,400]).
- Wall time = GRTC uptime + a UTC offset. The offset is set by USB SET_TIME at every case insertion, by the Bluetooth Time characteristic, and from an iPhone's Current Time and Local Time Information (section 7.6). With an iPhone that gives no time zone the clock holds that iPhone's local time and its "zone known" flag is false; a recording started then carries the flag, and the next SET_TIME corrects the clock.
- In `SHIP` and `OFF` the chip has no power and time is lost. The last time is saved in RRAM on entry; after the next boot the ring uses it as a guess, marks the time "not set" (chunk flag bit 5, `utc_ms` = 0) and shows "--:--" until the next SET_TIME. Since every wake comes from VBUS, the case sets the time at once.

### 9.2 Firmware update over USB, with rollback

- Boot loader: MCUboot, with the Zephyr image API `boot_request_upgrade()`, `boot_is_img_confirmed()`, `boot_write_img_confirmed()` [SRC 13] and image writing through `subsys/dfu/img_util/flash_img.c` [SRC 10].
- RRAM layout, 2,036 KB in total [SRC 1]: MCUboot 64 KB at 0x00000000; slot 0 (running image) 976 KB at 0x00010000; slot 1 (update) 976 KB at 0x00104000; settings (bonds, user settings, saved time, factory flag) 20 KB at 0x001F8000 [CALC: 64 + 976 + 976 + 20 = 2,036].
- MCUboot mode: swap using move, so an image that is not confirmed is swapped back at the next reset.
- **Boot loader locked against USB writes** (assembly conflict K-A1, applied). After assembly step 17 only the four pads reach the chip, and a broken boot loader would scrap the ring. Rules: (1) the USB update path (FW_BEGIN, FW_DATA, FW_END) writes only slot 1, 0x00104000 to 0x001F7FFF: FW_BEGIN refuses an `image_size` above 976 KB (999,424 bytes) and FW_DATA refuses an offset plus length past it, both with BAD_ARG; (2) no command writes the MCUboot area (0x00000000 to 0x0000FFFF) or slot 0, so MCUboot itself is never updated in the field; (3) the settings area is written only by the settings subsystem; (4) the MCUboot area is also write-protected by the chip's own memory protection, set over SWD at assembly step 5 before the board leaves its test pads. The nRF54LM20A mechanism for (4) and its register are TO CONFIRM (section 10.5, item 33); until it is confirmed, rules (1) to (3) carry the lock [CALC: 0x00104000 + 976 x 1,024 = 0x001F8000].
- Sequence: the case sends FW_BEGIN (erase slot 1), FW_DATA blocks of 4,096 bytes, FW_END. The ring checks the image CRC-32, calls `boot_request_upgrade(BOOT_UPGRADE_TEST)` and reboots. MCUboot checks the signature and swaps.
- Self-test of the new image, at most 30 s after boot: storage mounts, Bluetooth enables, USB enumerates again if VBUS is present. The microphones are not powered in the self-test (they are on only while a recording is stored); a PDM fault in the first recording after an update leads to `ERR_MIC_FAULT` and an event log record. All pass: `boot_write_img_confirmed()`. Any fails, or 30 s pass: reboot without confirming, and MCUboot restores the old image.
- Update allowed only with the battery above 30 % or VBUS present (always true in the case).

### 9.3 Factory test mode

- Entry: USB FACTORY sub-command 0x01 (ENTER) while the factory flag in settings is 1. The flag is written when the factory first programs the ring (assembly step 5), and cleared only by SHIP_ENTER (sub-command 0x7F). SHIP_SAMPLE (0x7E) enters ship mode and keeps the flag, for sample rings only, so a ring woken for a sample check can be tested again (assembly conflict K-A7). With the flag clear, FACTORY returns NOT_ALLOWED. Exit: FACTORY sub-command 0x02 (EXIT, ruling R22 of software step 6): the ring reboots, as the row "command FACTORY_EXIT" of section 1.2 says.
- Each test is a FACTORY sub-command; the response is result u8 (0 pass, 1 fail, 2 timeout) plus the measured values. The jig decides pass or fail with the limits below.

| Sub | Test | Part | Method | Pass |
|---|---|---|---|---|
| 0x10 | T-MIC1, T-MIC2 (argument 1 or 2) | each microphone | a 2 s test recording (recording_type 2) through the normal path while the jig speaker plays 1 kHz; report RMS level of each channel in dBFS and the count of identical consecutive samples | the tested channel within 3 dB of the mean of the 2; no channel stuck (no run of 1,000 equal samples); tapping only mic n raises channel n first (checks the channel map, section 4.1) |
| 0x20 | T-SCREEN | screen | full red, green, blue, white, black, 1 s each, then a grid | jig camera sees each colour, no dead row or column |
| 0x30 | T-JOY | joystick, 4 directions and the centre | the jig presses up (SW1), down (SW3), left (SW4), right (SW5) in turn; then the centre by the build's `CENTRE_SOURCE`: case `SW2`, SW2 alone; case `PAIR`, SW1 with SW3 and then SW4 with SW5, each pair closed within 20 ms of each other; then a roll test: centre held, SW4 closed 300 ms later, everything released after 1,200 ms | each direction within 1 s of its press, no other event; the centre reported once per press (twice in case `PAIR`), a centre press gives no up, down, left or right; the roll test gives one held centre of about 1,200 ms and no direction |
| 0x31 | T-CENTRE | the centre press as the record gesture | jig presses the centre once, twice (200 ms gap), and long (1,500 ms) | ring reports single, double, long, and the pulse MW at 500 ms of the long press; factory test mode reports the events and never starts a recording |
| 0x40 | T-MOTOR | motor | the power chip's ADC reads VBAT once before MOTOR goes high; MOTOR on 500 ms; VBAT read again 250 ms into the pulse; the ring reports both and the dip. The chip's battery current is not used: the motor's current does not pass the chip (section 3.1; motor-drive.md change F5) | jig accelerometer sees vibration; VBAT drops during the pulse by 20 mV or more **[ESTIMATE]**: 80 mA through 0.25 ohm of cell, protection circuit and ribbon; bench step B-M5 of motor-drive.md section 2.9 measures the real dip and then fixes this line |
| 0x41 | T-SIGN | recording sign on the screen (rule R-SIGN, section 3.2; replaces the light test, the light is removed in v7) | two 1 s test recordings 1 s apart; the ring reports the times VDD_MIC went on and off; the jig camera films the screen | in every camera frame between VDD_MIC on and VDD_MIC off the red dot is lit; no such frame shows a dark screen |
| 0x50 | T-STORE | storage | VDD_SD on, init, write 65 sectors at LBA 4,096, read back, compare CRC; time both; then delete every test recording (recording_type 2) the jig made | data equal; write at least 0.5 MB/s; read at least 1.0 MB/s; no test recording left |
| 0x60 | T-RADIO | radio | advertise 10 s at 0 dBm, 100 ms interval | jig RSSI at 20 cm at or above -60 dBm |
| 0x70 | T-CHARGE | charger | with VBUS, read the charge state (BCHGCHARGESTATUS [NPM p40, p41]), the latched errors (BCHGERRREASON [NPM p41]) and the battery current; the result is fail when the state is off or an error is latched (rule R-CHG) | state trickle, constant current, constant voltage or completed; in constant current the current is 13.5 to 16.5 mA [CALC: 15 mA plus or minus 10 %, NPM p29]. At the board stage (assembly step 5) the jig's battery source sets what is seen, so only the state is judged there |
| 0x71 | T-XTAL | 32.768 kHz crystal | count GRTC against the USB start-of-frame count over 10 s | within 50 ppm |
| 0x7E | SHIP_SAMPLE | | sample rings only: keep the factory flag; start the ship beacon (ruling R20 below); ship mode: the ring waits for VBUS removal, then writes TASKENTERSHIPMODE (section 8.4) | before VBUS is removed the jig receives the ship beacon; VBUS removed: the beacon stops within 1 s and stays off for 60 s; VBUS back: the ring wakes and FACTORY ENTER works again |
| 0x7F | SHIP_ENTER | | clear the factory flag; start the ship beacon (ruling R20 below); ship mode: the ring waits for VBUS removal, then writes TASKENTERSHIPMODE (section 8.4) | before VBUS is removed the jig receives the ship beacon; after VBUS is removed the beacon stops within 1 s and stays off for 60 s (assembly step 27) |

Sub-command 0x11 (the F2 skew test) is removed in F3: the ring answers BAD_ARG. Sub-command 0x41 is T-SIGN: the light and its test are removed in v7 (architecture 17.30).

Factory flow, step by step of `design/mfg/assembly/assembly.md` (the jig is work item W13):

| Assembly step | Stage | Access | What the firmware is asked to do or pass | Not tested here, and why |
|---|---|---|---|---|
| 5 | board | SWD on test pads TP3 SWDCLK, TP4 SWDIO, TP5 NRESET; USB on the J_BAND_B lands; the jig feeds a battery voltage on the cell lands and 10 kilo-ohm on the thermistor land | write and read back MCUboot, the image and the settings with the factory flag 1; set the boot loader lock (section 9.2); GET_INFO; T-STORE, T-XTAL, T-RADIO, T-CHARGE (state only) | T-SCREEN, T-SIGN, T-JOY, T-CENTRE, T-MOTOR: the screen, the switches and the motor are not joined yet. T-MIC1, T-MIC2: ruling R18 below. This is the last SWD access of the ring's life |
| 16 | ribbons joined, cell live | USB through the pads CP1 to CP4 | the ring boots to `STANDBY` on its cell (no VBUS); with VBUS on the pads it goes to `CHARGING`, enumerates and GET_INFO answers | |
| 18 | open ring | USB through the pads; FACTORY ENTER | every test: T-SCREEN, T-JOY, T-CENTRE, T-MOTOR, T-MIC1, T-MIC2, T-SIGN, T-STORE, T-RADIO, T-XTAL, T-CHARGE | |
| 20 | joystick pocket dammed | as step 18 | T-JOY, T-CENTRE | |
| 21 | liner cast | as step 18 | USB enumerates; T-JOY, T-CENTRE, T-MOTOR | |
| 24 | after the leak dip | as step 18 | T-MIC1, T-MIC2, T-SCREEN; USB enumerates | |
| 25 | closed ring | as step 18 | every test again, then the cell-only check below | |
| 26 | first charge | VBUS on the pads | charge to 50 percent before ship mode **[PROPOSED]** (below) | |
| 27 | ship | VBUS on the pads, then removed | SHIP_ENTER, then the jig removes VBUS; sample rings get SHIP_SAMPLE instead | |

- **R18 (microphones in the factory, the lead's ruling after design review 3):** a microphone gets power only through `rec_mics_on()`, after the screen shows the recording sign (rule R-SIGN, section 3.2). Factory test mode has no other path. At step 5 no screen is joined, so T-MIC1 and T-MIC2 do not run there; they run first at step 18 and again at steps 24 and 25. Cost: a microphone fault is found at step 18, after the ribbons are joined, and no longer on the bare board.
- Cell-only check of step 25 **[PROPOSED by assembly step 25]**: the jig sends FACTORY_EXIT (the ring reboots into `CHARGING`) and reads `boot_count` n with GET_INFO; it removes VBUS (`CHARGING` to `STANDBY`, no reboot); a long press starts a recording with M1 and a second long press stops it with M2; it puts VBUS back (`STANDBY` to `CHARGING`); GET_INFO must give n again, and GET_LOG must show no power-chip reset cause (section 8.7). Then the jig lists the recording, confirms it with its digest and deletes it (section 5.7), so the ring ships empty. FACTORY_EXIT comes first because removing VBUS in `FACTORY_TEST` reboots the ring (section 1.2), which would add 1 to the count.
- First charge of step 26 **[PROPOSED by assembly step 26]**: the charger runs at `CHARGE_CURRENT`, 15 mA, to 4.35 V; the jig reads GET_BATTERY until the state of charge reaches 50 percent (500 in `soc_percent_x10`), then goes to step 27. From an empty cell that takes about 0.59 to 1.06 hours across US 7 to 13 [CALC: 0.5 x 17.6 / 15 = 0.587 and 0.5 x 31.9 / 15 = 1.063]. The cell's maker may set another storage level (S12); the reading depends on the battery model (section 10.5, item 4).
- Ship of step 27: SHIP_ENTER, then VBUS removed; the ring writes TASKENTERSHIPMODE only after the event EVENTVBUSREMOVED (section 8.4). The jig checks the ship beacon of ruling R20.
- **R20 (ship beacon, the lead's ruling after design review 3):** a ring that leaves the factory has no paired device, and such a ring does not advertise in `STANDBY` (section 7.3), so "no advertising for 60 s" would be true with or without ship mode. From the moment SHIP_ENTER or SHIP_SAMPLE is accepted until the ring writes TASKENTERSHIPMODE, the ring sends a ship beacon: advertising that cannot be connected to, every 100 ms, at 0 dBm, with the name "Ring" plus the last 4 hex digits of the device id. The jig must receive the beacon while VBUS is on, see it stop within 1 s of removing VBUS, and see none for 60 s. The beacon exists only in `FACTORY_TEST`.

### 9.4 Logging and crash capture

- Development builds: Zephyr logging to `uart20` on DBG_TX P1.15 at 115,200 baud, send only (pin P1.16, the former DBG_RX, has no pad on the ring board). Production builds: no UART output; DBG_TX is an input with pull-down.
- Event log (both builds): each state change, fault, battery threshold and transfer command becomes a 512-byte record: magic 0x474C5252 ("RRLG") u32, record seq u32, uptime_ns u64, utc_ms i64, code u16, state u8, reserved u8, 16 bytes of arguments, crash block (below, zero when not a crash), CRC-32 in the last 4 bytes. Records wait in the 4 KB RAM log buffer (8 records) and are written to the log area (LBA 2 to 2,047) at the next time VDD_SD is on; when the buffer is full, the oldest unwritten record is dropped and a "dropped" count is kept. The codes are listed in the section "Event log codes" near the end of this document (ruling R23).
- Crash capture: `k_sys_fatal_error_handler()` is overridden to write a crash block (fault reason u32, PC u32, LR u32, PSR u32, thread name 16 bytes, 64 words of the faulting stack) into 1 KB of retained RAM (`zephyr,retained-ram`, `drivers/retained_mem/retained_mem_zephyr_ram.c` [SRC 10]) and the reset reason code into `gpregret1` [SRC 1], then reboot. `BOOT` copies a valid crash block into the event log and clears it.
- Power-chip reset causes: `BOOT` writes the nPM1304's RSTCAUSE and charger error log into the event log, then clears them (section 8.7).
- Watchdog: `wdt31`, 8 s timeout, fed every 1 s by a work item on the system work queue (the product has no main loop). While a recording runs it is fed only when the audio and storage threads have both reported progress in the last 2 s; with no recording it is fed at every turn. A stalled system work queue, or a recording thread without progress, ends in a reset after 8 s.

## 10. Work breakdown

### 10.1 What exists in the SDK

| Module | SDK part | Source |
|---|---|---|
| PDM capture, 1 instance (`pdm20`) | `drivers/audio/dmic_nrfx_pdm.c` with nrfx `nrfx_pdm` | SRC 2, SRC 4 |
| SD card over SPI | `drivers/sdhc/sdhc_spi.c`, `drivers/disk/sdmmc_subsys.c`, disk access API | SRC 6, SRC 7 |
| USB device, high speed | `drivers/usb/udc/udc_dwc2.c` + nRF54L glue, USB device stack "device_next" | SRC 5, SRC 8 |
| Power chip | nPM13xx MFD, regulator and charger drivers | SRC 11 |
| Fuel gauge | `nrf_fuel_gauge` library (nRF Connect SDK, nrfxlib) | SRC 12 |
| Joystick (five switches) | `gpio-keys` input driver | SRC 14 |
| Bluetooth | Zephyr host, BAS, DIS services | SRC 10, SRC 15 |
| Boot loader, update | MCUboot image API, `flash_img` | SRC 10, SRC 13 |
| Retained RAM, reset reason | `retained_mem_zephyr_ram.c`, `gpregret1` | SRC 1, SRC 10 |
| Display bus | MIPI DBI over SPI (`drivers/mipi_dbi/mipi_dbi_spi.c`), display library (LVGL module) | SRC 10 |
| Board start point | `boards/nordic/nrf54lm20dk` (nRF54LM20A application core) | SRC 9 |

### 10.2 What must be written

| Id | Module | Work |
|---|---|---|
| W1 | Board files `ring_nrf54lm20a` | devicetree with the pins of the table at the top, peripheral instances, nPM1304 node of section 8.1 (property names TO CONFIRM first), partitions of section 9.2; based on `nrf54lm20dk` |
| W2 | Screen driver `display_sh8501a.c` | **No Zephyr driver exists for the SH8501A**: `drivers/display/` (167 entries) and `dts/bindings/display/` (132 entries) list none [SRC 10]. Write a Zephyr display driver on MIPI DBI over SPI in 4-wire mode (LCD_DCX as data/command), RGB565, 120 x 240, with reset on LCD_RST, tear-effect input on LCD_TE, panel supply on OLED_PWR_EN, `display_write()` of partial areas, `display_blanking_on/off()`, brightness. Model: the AMOLED driver `display_rm67162.c`, which uses MIPI DBI and a TE GPIO [SRC 10]. Needs the SH8501A datasheet and the vendor start-up code (architecture action 12.1). SPI clock 8 MHz (the SPIM21 maximum [SRC 3]): a full frame of 57,600 bytes takes 57.6 ms [CALC] |
| W3 | Pin sleep states | patch to the dmic driver that applies the pin sleep state at boot and after stop, so MIC_A_CLK is low whenever VDD_MIC is off (section 4.5); `spi00` suspend and resume around VDD_SD (section 5.1) |
| W4 | Audio service | 2-channel chunk fill from the one PDM instance, dropout fill, motor interval marking |
| W5 | Storage service | raw log of section 5: chunk writer, superblock, index, recovery scan, free-space accounting, deletion |
| W6 | USB vendor class and protocol | class of section 6.1 with `USBD_DEFINE_CLASS`, command handlers, firmware update path |
| W7 | Bluetooth ring service | section 7.2 characteristics, fetch flow, pairing window UI |
| W8 | Power service | thresholds, fuel gauge loop with the motor's charge added (section 8.3), rail control, ship entry by TASKENTERSHIPMODE after VBUS removal (section 8.4), the battery current limit status and the reset causes (section 8.7) |
| W9 | Input gestures | centre key and both `CENTRE_SOURCE` cases (sections 2.1 and 2.2), gesture recogniser of section 2.1, warning pulse MW, joystick repeat, collisions C1 to C4, screen lock |
| W10 | Feedback | motor pattern player with the limits of section 3.1, the motor charge per pulse for the gauge (section 8.3), and the MOTOR edge times for section 4.7; the recording sign of section 3.2 with test SIGN-1 (no light code: the light is removed in v7) |
| W11 | User interface | the screens of section 3.3 |
| W12 | State machine | section 1, one table-driven module; every row of 1.2 is one test case |
| W13 | Factory test | section 9.3 sub-commands (SHIP_SAMPLE included), the factory flow by assembly step, the boot loader lock of section 9.2, jig protocol |
| W14 | Logging and crash | section 9.4 |
| W15 | Case-side reference tool | a host program that speaks section 6 over USB, for bench use before the case exists |

### 10.3 Order of work

W1, W12, W9, W10 on the development kit first; then W4 with the microphone evaluation boards on the kit; W5 with an SD NAND breakout on `spi00`; W6; W8 with Nordic's nPM1304-EK kit (architecture 17.18) and the motor adapter of motor-drive.md section 2.9; W2 when the screen samples and start-up code arrive; W7, W11, W13, W14 last.

### 10.4 Sources read for this document

| Id | Source (fetched 2026-11-10) |
|---|---|
| SRC 1 | Zephyr `dts/vendor/nordic/nrf54lm20_a_b.dtsi`, main branch: `pdm20` 0xd0000, `pdm21` 0xd1000, `spi00` 32 MHz, `spi21`/`i2c21` both 0xc7000, `usbhs` "nordic,nrf-usbhs-nrf54l", `grtc`, `tdm`, `wdt30`/`wdt31`, `gpregret1`/`gpregret2`, `cpuapp_sram` 511 KB, `cpuapp_rram` 2,036 KB |
| SRC 2 | Zephyr `drivers/audio/dmic_nrfx_pdm.c` and `include/zephyr/audio/dmic.h`, main |
| SRC 3 | nrfx `bsp/stable/mdk/nrf54l/nrf54lm20a/nrf54lm20a_types.h` (PDM ratios 48 to 192, PRESCALER divisor 4 to 126, GAINL 0x00 / 0x28 / 0x50, CLKSELECT PCLK32M / ACLK) and `nrf54lm20a_application_peripherals.h` (SPIM00 32 Mbit/s and 128 MHz core with divisor 4 to 126; SPIM20 to SPIM22 8 Mbit/s; USBHS present) |
| SRC 4 | nrfx `drivers/src/nrfx_pdm.c` (`nrfx_pdm_prescalers_calc()`) and `hal/nrf_pdm.h` |
| SRC 5 | Zephyr `drivers/usb/udc/udc_dwc2.c` and `drivers/usb/udc/udc_dwc2_nrf_usbhs_nrf54l.h` |
| SRC 6 | Zephyr `drivers/disk/sdmmc_subsys.c` (`zephyr,sdmmc-disk`, `DISK_IOCTL_CTRL_INIT`, `DISK_IOCTL_CTRL_DEINIT`) |
| SRC 7 | Zephyr `drivers/sdhc/sdhc_spi.c` and `drivers/sdhc/Kconfig.spi` (`zephyr,sdhc-spi-slot`, 400 kHz start, multi-block, CRC-16, `spi-max-frequency`) |
| SRC 8 | Zephyr `include/zephyr/usb/usbd.h`, `include/zephyr/usb/usbd_msg.h`, `subsys/usb/device_next/class/` listing |
| SRC 9 | Zephyr `boards/nordic/nrf54lm20dk/` listing, `nrf54lm20_a_b_cpuapp_common.dtsi`, `nrf54lm20dk_nrf54lm20_a_b-pinctrl.dtsi` |
| SRC 10 | Zephyr tree listing (GitHub API, main) and contents listings of `drivers/display` and `dts/bindings/display`; `drivers/display/display_rm67162.c` |
| SRC 11 | Zephyr `drivers/mfd/mfd_npm13xx.c`, `drivers/regulator/regulator_npm13xx.c`, `drivers/sensor/nordic/npm13xx_charger/npm13xx_charger.c`, bindings `nordic,npm13xx-common.yaml`, `nordic,npm13xx-charger-common.yaml`, `nordic,npm13xx-regulator-common.yaml`, `include/zephyr/dt-bindings/regulator/npm13xx.h` (fetched 2026-11-10 for F4; the chip-specific charger binding read then was that of the older chip, see the change list F4 to F5) |
| SRC 12 | nrfxlib `nrf_fuel_gauge/include/nrf_fuel_gauge.h`, main |
| SRC 13 | Zephyr `include/zephyr/dfu/mcuboot.h` |
| SRC 14 | Zephyr `dts/bindings/input/gpio-keys.yaml` |
| SRC 15 | Zephyr `subsys/bluetooth/host/Kconfig` and `subsys/bluetooth/common/Kconfig` |
| DS | Knowles SPK0641HT4H-1 datasheet Rev A, third-party copy, text `design/mech/mic-path/datasheets/knowles-spk0641ht4h-1_chipsmall.txt` (read 2026-11-11) |
| NPM | Nordic nPM1304 Product Specification v1.0, 173 pages, `design/datasheets/npm1304_datasheet_v1_0.txt` (read 2026-11-11: pages 8 to 11, 17, 22 to 30, 36, 37, 40, 41, 69, 77, 99, 107 to 109, 116 to 120, 130, 136, 144 to 146) |
| SRC 17 | `design/parts/research-npm1304.md` section 1, source [Z]: Nordic's nRF Connect SDK binding page `nordic,npm1304-charger` (processed text, not a raw copy): `current-microamp` 4 to 100 mA in 0.5 mA steps, `term-microvolt` 3.6 to 3.65 V and 4.0 to 4.65 V in 50 mV steps, `term-current-percent` default 10 |
| SRC 16 | Zephyr `drivers/usb/udc/udc_dwc2.c` (`udc_dwc2_device_speed()`, DSTS ENUMSPD), `subsys/usb/device_next/usbd_core.c` (`status.speed`), `usbd_ch9.c` (`fs_desc` / `hs_desc`), `usbd_device.c` (`usbd_bus_speed()`), `class/loopback.c`, main, fetched 2026-11-10 |
| DOC | `design/architecture.md` A5-draft (sections 2, 7, 9, 14, 16.4 to 16.6, 17.3 to 17.8 read 2026-11-10; 17.10 to 17.23 read 2026-11-11), `design/case/case-architecture.md` C5d (sections 1, 5, 6; first read at version C1), `design/ecad/ring/sch-notes.md` (sections 2, 7, 8, 9; section 12 read 2026-11-11), `design/ecad/ring/netlist.csv` and `parts.csv` (2026-11-11), `design/ecad/motor-drive/motor-drive.md` section 2, `design/mfg/assembly/assembly.md`, `design/mech/mic-path/mic-path.md` sections 3 and 9 (2026-11-11) |

### 10.5 Facts not verified from a primary source

1. The nRF Connect SDK Bluetooth controller (SoftDevice Controller) supports the nRF54LM20A; only the Zephyr device file was read.
2. MCUboot "swap using move" works on the nRF54LM20A RRAM in the nRF Connect SDK, and which signature type the SDK uses by default there.
3. Devicetree names for the nPM1304: every property of section 8.1 marked TO CONFIRM (the compatible of the MFD and regulator nodes, `host-int-gpios`, `pmic-int-pin`, `ship-to-active-time-ms`, the regulator, load switch, thermistor, die-temperature, trickle, VBUS-limit and charging-enable properties), whether the nPM13xx family drivers of SRC 11 serve the nPM1304 (charger sensor channels, register read and write calls), and the driver call that writes a task register. Who answers: the firmware designer, from the nPM1304 binding files and drivers of the nRF Connect SDK version the build pins (not on disk), before work item W1. Closed by the nPM1304 specification: the I2C address 0x6B [NPM p120], the ship task and its VBUS rule [NPM p116, p118], the ship current 370 nA typical [NPM p11].
4. The fuel gauge needs a battery model of the actual Grepow cells; Nordic makes it with the nPM PowerUP application [NPM p99]. Whether one model serves the seven cell lengths of US 7 to 13 or each needs its own: the firmware designer with the cell maker (S12).
5. Which nRF PDM channel (left or right) receives U5 (SELECT on GND) and U6 (SELECT on VDD_MIC) under the driver's default map: the Knowles text copy shows the timing figure without naming the edge in words [DS Figure 1]. Factory test T-MIC checks it on every ring; the firmware designer reads the figure on the PDF page and confirms it on the development kit.
6. Microphone current at 1.280 MHz: the Knowles datasheet gives 630 µA typical at its 2.4 MHz test clock [DS line 97] and no figure at 1.280 MHz; bench test B2 measures it. The 0.58 mA of the old part in the subtraction of section 8.5 comes from F4 (architecture 16.8), not from a datasheet.
7. Closed in F3: one PDM instance has no start skew (bench test A1 and the F2 skew test are removed).
8. Closed in F3: one PDM instance, no drift between instances to verify.
9. The PDM clock pin level after `nrfx_pdm_stop()` (work item W3 makes it defined).
10. The SD SPI-mode clock limit of 25 MHz and the card start-up sequence (SD Physical Layer specification, not read).
11. Card start-up time and charge, write stall times, read and write speed in SPI mode, usable size and power-loss behaviour of the CSNP32GCR01-BOW (architecture 16.4; bench tests S1 and S2).
12. Whether the Zephyr SD stack issues one CMD25 for a multi-sector `disk_access_write()`; the SPI host driver supports it [SRC 7].
13. SH8501A command set, start-up code, timing of reset and sleep-out, and support of the standard DCS commands (architecture action 12.1).
14. Whether 25 ms motor pulses are felt (bench test F1), the motor spin-up time and the start allowance of 10 ms at 175 mA used for the fuel gauge (section 8.3): bench step B-M3 of motor-drive.md section 2.9. The T-MOTOR pass line of 20 mV is an estimate until bench step B-M5.
15. RAM use of the Bluetooth stack, the display library, thread stacks and the kernel (allocations in section 4.6; the first build's linker map checks them).
16. The cycle counter rate behind `k_cycle_get_32()` on this chip (stored in each chunk as `cycle_hz`, so the files stay correct whatever it is).
17. USB vendor id and product id for production (question for the owner).
18. Zephyr API names used here but not opened in this run: `k_sys_fatal_error_handler()`, `k_cycle_get_32()`, `k_cyc_to_ns_floor64()`, `sys_clock_hw_cycles_per_sec()`, `irq_lock()`, `crc32_ieee()`, `regulator_enable()`, `regulator_disable()`, `disk_access_write()`, `disk_access_read()`, `disk_access_ioctl()`, `DISK_IOCTL_GET_SECTOR_COUNT`, the compatible string `zephyr,retained-ram` (only the driver file name was seen), and the unit (seconds) of `CONFIG_BT_RPA_TIMEOUT` (only the option name was seen).
19. That the nRF54LM20A USBHS PHY completes enumeration at full speed with a full-speed host (case supplier item S2, case bench test B1); the Zephyr stack side is read [SRC 16].
20. The 1.216 MB/s full-speed bulk ceiling (USB 2.0 figure, not read here; taken from the case document).
21. Closed for the chip: in the cool region the nPM1304 halves the charge current, in the warm region it charges to the reduced voltage [NPM p25, Table 12]. Still open: the charge temperature range of the Grepow cell (the cell maker, S12) and the RT1 part, which must have B25/50 = 3,380 K to match the chip's 10 kilo-ohm type [NPM p24] (the schematic owner).
22. That suspending `spi00` with the Zephyr device power-management call applies its pin sleep state, and that the sleep state can set the pins as inputs with no pull.
23. Closed (risk review 2026-11-13): the Tailor sheet page 9 draws Swire low through power-up, reset and sleep out; at "sleep in" the screen maker gives no drawing, so the off order of line 382 is SG Micro's sequence 1.
24. Closed in F5: the microphone of 17.19 has a datasheet copy on disk; its clock range, power-up time and current are cited from it (sections 4.1, 4.5). The copy is a third-party host's copy of Knowles Rev A (2016): Knowles or a distributor confirms the part is still made (S23).
25. The SD-mode clock limit of the CSNP32GCR01-BOW in SPI mode (16 MHz is used) and that its 3.7 GB usable size is what `DISK_IOCTL_GET_SECTOR_COUNT` returns.
26. The fuel-gauge battery model for the curved cells of 17.6 to 31.9 mAh (architecture 17.26), the accuracy of its state of charge at 4.1 mA with the motor's charge added, and the cell's discharge limit against the motor start of 175 mA (hardware issue H7). Who answers: the cell maker (S12), then the bench.
27. Whether the centre key of section 2.2 reads a centre press reliably on the real round cap in both cases (bench item B6, architecture 16.5), whether the real switch SW2 fits under the centre of the round cap (architecture 17.11, 17.12), and whether the F4 values 30 ms release hold-off, 40 ms decision window in case `SW2`, MW at 500 ms and the 450 ms short-press ceiling suit a thumb at rest (all marked [CHOICE]).
28. How the 120 x 240 screen, whose long side lies along the finger (architecture 16.1), is rotated by the display driver; F3 keeps the screen layouts of section 3.3.

29. What the nRF54LM20A's USB pins do when the USB peripheral is disabled and no VBUS is present (section 8.6, item 2); only the Zephyr stack side is stated.
30. Read in F5: VBUS is valid at 210 mV above VBAT and wakes the chip above 3.9 V [NPM p17]. Not read: whether any nPM1304 function drives VBUS (its VBUSOUT pin, ball C3, is on a net of its own with nothing else on it, netlist.csv); the schematic owner confirms with the specification's VBUSOUT section.
31. The cell's highest charge current (open item S12): `CHARGE_CURRENT` 15 mA, 0.85 C of the smallest cell (17.6 mAh), stays until the cell's maker answers.
32. The sign the `nrf_fuel_gauge` library expects for a discharge current, and its call for an added current (section 8.3): the firmware designer, from SRC 12 at the pinned SDK version.
33. The nRF54LM20A's own write protection for the MCUboot area (section 9.2, K-A1 rule 4) and the register or UICR setting that holds it: the firmware designer, from Nordic's nRF54LM20A product specification (not on disk).
34. What the nPM1304 does when TASKENTERSHIPMODE is written while VBUS is still present: the specification asks the host to wait for VBUS removal first [NPM p116], which section 8.4 does; the case itself is not described. Nordic answers if it matters.

### 10.6 What `firmware-check.py` checks

Run: `design/.venv/bin/python -I design/firmware-check.py` (exit 0 = pass, 1 = a rule fails). It reads `design/architecture.md`, `design/ecad/ring/netlist.csv` and the Knowles datasheet copy `design/mech/mic-path/datasheets/knowles-spk0641ht4h-1_chipsmall.txt`. Kept from F2 to F4: sections 1 to 10 present; every state of a transition is in the state list, every listed state has a transition out and, except `SHIP` and `BOOT`, one in, and the number of transition rows equals the number stated under the table; every pin and signal name is in architecture section 7, no spare pin is used, and each signal-pin pair matches; the RAM lines sum to the total, at most 512 KB; the charge voltage equals the cell's type in architecture section 2; each PDM clock line divides 32 MHz by a whole prescaler of 4 to 126, uses a ratio of the chip and gives 16,000 or 8,000 Hz; 64-byte bulk packets at full speed (6.1); the motor marking rule (4.7); the schematic rules for the microphone clock (4.5), the storage lines (5.1) and the screen sequence (3.3); thermistor value and ordered limits (8.1); none of the removed names outside the change lists; VDD_MIC on in exactly one state (1.1) and one power-table row (8.2), the recording state; only a long press starts or stops a recording, a short or double press never changes state, and no direction, button or other event touches the recording state; the gesture, centre-source, warning-pulse, hold-off and collision rules of F4; the audio format and chunk arithmetic; one PDM instance; the joystick switches against architecture 17.3 and the 40 ms rule against 16.5; unused pins only on lines that say unused; four pads in order; every row into `CHARGING` and both ship-exit rows say "charge on", `charging-enable` is on whenever VBUS is present, R-CHG stated; section 8.6 states VBUS is an input only; `questions_for_owner` and the RESULT line. Changed in F5 (each replaces an F4 check that asserted what F5 changes): the header says Version F5, follows A5 sections 17.11 to 17.23 and has the list "Changes from F4 to F5" with 8 items; the removed-name rule runs from that list to "How to read this" and now also bans the older power chip's name, the F3 battery range, the old microphone and datasheet names and the discharge-limit property; `CHARGE_CURRENT` is 15,000 µA in `current-microamp`, a multiple of 500 inside 4,000 to 100,000 and at most 1 C of the smallest cell of architecture 17.17, and T-CHARGE has a pass limit (in F4 both were BLOCKED on S12); the microphone mode range is read from the Knowles datasheet copy (F4 used fixed numbers of the older part), the microphone part name is in 4.1 and 8.5, and the gain is 0 dB, the register 0x28 (2 x 0 + 0x28), the header `gain_code` equal to it, and the stored full scale (94 dB SPL minus the sensitivity read from the Knowles copy) equal to the acoustic overload point read from the same copy; section 3.1 names U11, MOT_EN, VMOT and the 0.55 ms delay and never Q1, and architecture 17.22 names U11 (F4 checked Q1 and full duty on VDD_3V0); the battery minutes of 1.1 and the hours of 8.5 are recomputed from the smallest and largest cells of architecture 17.17 and the recording current 4.0 + 2 x (0.63 - 0.58) mA (F4 checked a single range against architecture 17.10); the ship section 8.4 names TASKENTERSHIPMODE, the VBUS removal and EVENTVBUSREMOVED and no timed hibernate; SHIP_SAMPLE keeps the factory flag in 9.3 and in 1.2; section 7 starts with the protocol sentence. New in F5: every "SIGNAL Pn.nn" pair and every chip pin of firmware.md is checked against the U1 rows of `netlist.csv`, and the power chip, microphone and motor nets this file names (GPIO0 on PMIC_INT, LSOUT1 on VDD_MIC, LSOUT2 on VDD_SD, U5 and U6 SELECT, U11 EN, OUT and IN, R61 and R62) against their netlist rows. Changed in F6: the cells per size are read from the measured table of architecture 17.26 (no longer 17.17); the compile limit of 8.1 must equal 1 C of the smallest cell, 17,600 µA; the header says Version F6 with sections 17.11 to 17.26 and the list "Changes from F5 to F6" has 4 items; and no line outside the change lists may name a value of the calculated cells (18.2, 24.3 or 32.9 mAh, or 18,200 µA) unless the word "before" stands within 60 characters of it. Changed in v7 (architecture 17.29 and 17.30): the netlist fact "Q2 whose gate is VDD_MIC" is no longer required; any line naming LED1, R41, Q2, LG1, LP1, T-LIGHT, "recording light", "light window", "hard-wired", "record button" or "nub" fails unless it says "removed in v7"; section 3.2 must state rule R-SIGN (never dark, red dot and timer, dimmed after 3 s, full picture on any input, the one function `rec_mics_on()`, test SIGN-1, the dot's cost a bench item); the `RECORDING` screen cell of 1.1 must say never dark and its 8.2 row must keep the screen on; 4.5 must enable VDD_MIC only after the sign is drawn; the refusal row "recording sign not drawn" must stay in `STANDBY`; 9.3 must hold T-SIGN and no T-LIGHT row; 8.5 must not count a light and must name the dot's cost as a bench item; the centre switch is written "centre switch SW2 (net BTN_REC)"; the 2.2 heading names the round joystick with five switches. Rules it cannot check (timing values, protocol layouts, the meaning of text) are checked by review.

## Hardware issues found

Status in F5 of the issues raised in F1 to F4, after architecture A5-draft sections 17.13 to 17.23 (H8 and H9 close in F5; H16 to H19 are new):

| Id | Conflict | Status | Firmware choice | Who acts |
|---|---|---|---|---|
| H1 | Architecture A1 and A2 section 5 fixed the PDM clock at 1.536 MHz with ratio 96. The chip's PDM divides 32 MHz by an integer 4 to 126 [SRC 3, SRC 4]: 1.536 MHz needs 20.83, so 16 kHz cannot be made at 1.536 MHz. | closed: architecture A3 section 5 now gives 1.280 MHz, ratio 80 | 1.280 MHz, ratio 80, exactly 16 kHz, inside the 1.000 to 4.800 MHz performance mode of the microphone of 17.19 [DS line 95] | bench B2 measures the current |
| H2 | F1: microphones 1 and 2 share MIC_A_CLK, so a one-microphone low-power state of F1 clocked both. | closed: the owner removed that state (change list); every recording clocks all 4 | none | none |
| H3 | F1: the light follows VDD_MIC and was on all day in a state the owner has now removed. | closed: VDD_MIC is on only while audio is stored, so the light is on exactly then; [v7: removed in v7 (architecture 17.30): the recording light, LED1, R41, Q2, the light guide LG1, the light pipe LP1 and the light window are out; the recording sign is the screen, section 3.2] | none | none |
| H4 | F1: the light circuit of architecture sections 7 and 9 contradicted itself. | closed by architecture A2: no chip pin touches the light; [v7: removed in v7 (architecture 17.30): the recording light, LED1, R41, Q2, the light guide LG1, the light pipe LP1 and the light window are out; the recording sign is the screen, section 3.2] | no light code | none |
| H5 | F1: no thermistor on the cell. | closed: RT1, 10 kilo-ohm, on the power chip's NTC pin (nPM1304 ball D3, netlist.csv) | charger limits of section 8.1 | schematic owner: the RT1 part, with B25/50 = 3,380 K for the chip's 10 kilo-ohm type [NPM p24] |
| H6 | F1: PMIC_INT GPIO and SHPHLD not named. | closed: PMIC_INT on nPM1304 GPIO0 (ball D6), SHPHLD on test pad TP19 (netlist.csv); VBUS above 3.9 V ends ship mode [NPM p116, p17] | `pmic-int-pin = 0`; wake from `SHIP` and `OFF` only by VBUS | none |
| H7 | The motor draws below 80 mA running and up to 175 mA at each start (architecture 17.16), now straight from the cell through U11 (17.22): 4.5 C running and 9.9 C at the start on the smallest cell, 17.6 mAh, and 2.5 C and 5.5 C on the largest, 31.9 mAh [CALC, section 3.1; architecture 17.26]. A start takes up to 228 mA from the cell with every other load on (17.22). No cell discharge limit and no protection-circuit trip current is on file. | open | the patterns are unchanged; B15 and B5 stop recording before the cell is low, but a trip of the protection circuit in a motor start would cut power in a pulse | cell maker (Grepow), through open item S12: maximum pulse current of the cell and its protection circuit |
| H8 | F4: the power chip of F4 could not charge under 32 mA, above 1 C of the cell. | closed by architecture 17.13: the nPM1304 charges from 4 mA [NPM p24] | `CHARGE_CURRENT` = 15 mA, 0.85 C of the smallest cell (17.6 mAh); T-CHARGE passes at 13.5 to 16.5 mA | Grepow states the cell's own limit (S12); the value changes in one place |
| H9 | F4: the microphone had no datasheet on disk. | closed by architecture 17.19: the Knowles SPK0641HT4H-1 has a datasheet copy | 1.280 MHz, ratio 80 and the 50 ms discard, now from that copy (sections 4.1, 4.5) | Knowles or a distributor confirms the part is made (S23) |
| H10 | The pad order: architecture section 8 says "from -Y to +Y"; 17.3 lists the pads at X = -2.4, -0.8, +0.8, +2.4 mm, and 17.8 puts them at -150 degrees. | open, same name order in both | VBUS, D-, D+, GND in that order | architecture owner: state the axis of the order on the band; case owner: the case pins |
| H11 | Architecture section 8 and the case document still give 6.3 minutes per recorded hour (four channels of audio, 461 MB). | closed 2026-11-13: `design/architecture.md` line 303 carries REPLACED and `design/case/case-architecture.md` line 88 gives 3.21 min | 3.21 minutes per recorded hour with 2 channels (section 6.4) | architecture owner and case owner |
| H12 | Architecture 17.3 and 17.8 put the cell's temperature sensor in the band's flex tail (other side); sch-notes and bom-notes (conflict 5) put RT1 on the main board beside the cell. | closed 2026-11-11: RT1 sits on the cell, on its protection circuit PRT1 (`design/bom.csv` line 75; `design/wiring/lead-decisions.md` row 34) | RT1 on the nPM1304 NTC pin, 10 kilo-ohm, limits of section 8.1 | schematic owner: where RT1 sits and its part; the limits apply to the cell, not the board |
| H13 | Architecture sections 1, 3, 4, 5, 6, 7 and 9 and the rows of the section 2 table for the joystick (+38 degrees) and the second control (+62 degrees) still describe the A3 or earlier ring (four microphones, the flat A3 cell, 68 mA charge, 4.40 V); section 17.8 wins by the architecture's own rule. | open | F3 follows 17.8, then 17.1 to 17.6, then 16 | architecture owner: rewrite when the open items of 16.9 close |
| H14 | Architecture 17.12 puts the four pads on the inside of the band, touching the skin; whether any voltage or leakage path reaches them without a case, and how sweat is kept from corroding them, is to be stated in the wiring notes (17.12). | open | VBUS is an input, nothing is driven onto the pads, USB off without VBUS (section 8.6) | wiring notes owner (schematic), then the case owner |
| H15 | Architecture section 9 (first two bullets), 16.5 (the line on the record button), 17.3 (the table row for the record button and the line "SW2 = record button") and 17.8 still describe a separate record button and a joystick that never starts a recording; 17.11 removes the button and puts the record gesture on the centre press. [v7: the record button is gone since 17.11 and the rectangular nub is removed in v7; the one control is the round joystick (architecture 17.29), centre switch SW2 (net BTN_REC)] | closed 2026-11-13: every record button line of `design/architecture.md` (23, 153, 229, 300, 356, 369, 433, 455, 482, 515) carries REPLACED by 17.11 or is reworded | F4 and F5 follow 17.11 (later sections win); BTN_REC is the centre switch in case `SW2` | architecture owner: rewrite those lines |
| H16 | The first F5 brief asked the gain to drop by 11 dB for the more sensitive microphone. At -11 dB the microphone's own noise, -26 - 64.5 - 11 = -101.5 dBFS(A), falls under the noise of a 16-bit sample, -(6.02 x 16 + 1.76) = -98.1 dBFS; the stored signal-to-noise at 94 dB SPL would drop from about 63.8 dB at 0 dB gain to about 59.5 dB [CALC, `design/firmware-f5-notes.md`; assumes the PDM truncates to 16 bits after the gain; not A-weighted]. At 0 dB the store clips at 94 + 26 = 120 dB SPL, the microphone's own overload point [DS line 105]. | closed by the lead's decision of 2026-11-11: gain 0 dB | gain 0 dB (0x28), section 4.1 | none; bench B7 can measure the floor |
| H17 | Architecture section 3 still says "the power chip stops discharge at 3.1 V" and section 2 and 3 still name the older power chip; motor-drive.md section 2.4 uses that 3.1 V. The nPM1304 specification read gives a power-fail reset at VSYSPOF, 2.7 V by default (2.5 to 3.4 V) [NPM p109], and a brownout at 2.4 V [NPM p29]; no 3.1 V cut-off was found. | open | B2 at 3.30 V and B5 at 3.45 V stay; VSYSPOF stays at its default (section 8.7) | architecture owner: rewrite section 3; the cell maker: the protection circuit's undervoltage limit (S12) |
| H18 | Architecture 17.15 and 17.17 gave the recording hours at 4.0 mA; with the microphones of 17.19 the current is 4.1 mA. | closed by architecture 17.26, which computes the hours at 4.1 mA on the measured cells (4.3 to 7.8 hours) | 4.1 mA (section 8.5) | none |
| H19 | Assembly step 25 reads the boot count after FACTORY ENTER and expects the same count after VBUS is removed and put back; removing VBUS in `FACTORY_TEST` reboots the ring (section 1.2), so the count rises by 1. Its stated reason (a motor start over the 100 mA limit) is also out of date since 17.22, and its step 2 still lists Q1 and D1 (17.23 says 17.22 wins). | closed 2026-11-13: assembly step 25 sends FACTORY_EXIT first and then reads the count, and step 2 no longer lists Q1 and D1 (design/mfg/assembly/assembly.md, steps 25 and 2) | section 9.3 sends FACTORY_EXIT before the count is read; the check stays as a proof of no reset | assembly owner: update steps 2 and 25 |

## Event log codes (ruling R23, software step 6)

The event log record of section 9.4 carries one of these codes (u16) and up to 16 bytes of arguments (little-endian, unused bytes 0). The list is the one of `firmware/modules/ring_rhw/include/ring_rhw/rrec_spec.h` (`enum rrec_log_code`); that file and this table hold the same 27 codes (26 until the ruling of 2026-11-13 that added 0x0290). "FW l.N" in a row is a line of this document as it stood when the code was written (commit 783ddc4).

| Code | Name | When | Arguments |
|---|---|---|---|
| 0x0001 | `RREC_LOG_STATE_CHANGE` | each state change, FW l.1062 | from u8, to u8, row u16 (FW 1.2 row number of the core's table), event u8 (enum rc_event) |
| 0x0002 | `RREC_LOG_REC_START` | recording opened | recording_id u32, press t_ms i64 (FW l.448) |
| 0x0003 | `RREC_LOG_REC_STOP_PRESS` | stop press start time (FW l.448) | recording_id u32, press start t_ms i64 |
| 0x0004 | `RREC_LOG_ZONE_UNKNOWN` | recording started with the zone unknown (FW l.1004; ruling D8) | recording_id u32 |
| 0x0005 | `RREC_LOG_SIGN_REFUSED` | row FW l.148: sign not drawn | rscr_sign_start() answer i32 |
| 0x0010 | `RREC_LOG_FAULT_STORAGE_INIT` | storage init failed 3 times (FW l.138) | last errno i32 |
| 0x0011 | `RREC_LOG_FAULT_CHUNK_WRITE` | chunk write failed 3 times (FW l.168) | chunk_seq u32, errno i32 |
| 0x0012 | `RREC_LOG_FAULT_MIC` | no PDM block for 100 ms (FW l.169) | blocks so far u32 |
| 0x0013 | `RREC_LOG_FAULT_CHARGER` | charge error (FW l.176) | BCHGERRREASON u8, BCHGERRSENSOR u8 |
| 0x0014 | `RREC_LOG_FAULT_SCAN_READ` | read error during the recovery scan (FW l.143) | lba u32, errno i32 |
| 0x0015 | `RREC_LOG_STORAGE_RETRY` | 60 s retry result (FW l.191) | result i32 (0 = success) |
| 0x0016 | `RREC_LOG_DROPOUT` | a PDM block replaced by zeros (FW l.430) | recording_id u32, chunk_in_recording u32, block index in the chunk u8 |
| 0x0020 | `RREC_LOG_BATTERY` | a battery threshold reached, either way (FW l.1062) | level u8 (enum rc_batt), soc_x10 u16, mean mv u16 |
| 0x0021 | `RREC_LOG_STORAGE_S30` | free space reached S30 | free chunks u32 |
| 0x0022 | `RREC_LOG_STORAGE_SFULL` | free space reached SFULL | free chunks u32 |
| 0x0100 | `RREC_LOG_XFER_BASE` | a transfer command: code = 0x0100 / opcode (0x0101 to 0x010D), FW l.1062 | status u8, tag u32, request length u32, first u32 argument |
| 0x0200 | `RREC_LOG_MOTOR_PATTERN` | pattern started (FW l.333) | pattern u8 (enum rrec_pattern), t_ms i64 |
| 0x0210 | `RREC_LOG_ILIM_ACTIVE` | battery current limit active (FW l.991, l.995) | battery_mv u16, state u8, screen on u8, count u32 |
| 0x0220 | `RREC_LOG_PMIC_RESET` | nPM1304 RSTCAUSE and charger error log at boot (FW l.996) | RSTCAUSE u8, CHARGERERRREASON u8, CHARGERERRSENSOR u8 |
| 0x0221 | `RREC_LOG_MAIN_RESET` | the main chip's reset reason beside it (FW l.996) | reason u32, gpregret1 u8 |
| 0x0230 | `RREC_LOG_CRASH` | a crash block copied at boot (FW l.1063); crash block filled | none (the crash block is filled) |
| 0x0240 | `RREC_LOG_RECOVERY_DONE` | RECOVERY closed a recording (FW l.646) | recording_id u32, chunks kept u32, head_chunk_seq u32 |
| 0x0250 | `RREC_LOG_SHIP_RETRY` | still running 1 s after the ship task (FW l.941) | try u8 |
| 0x0260 | `RREC_LOG_TIME_GUESS` | the saved time at boot, used as a guess only (FW l.1005; ruling D18) | saved utc_ms i64 |
| 0x0270 | `RREC_LOG_SELFTEST` | update self-test end (FW l.1014) | result u8 (0 pass, 1 fail, 2 timeout), items passed mask u8 (bit 0 storage, 1 Bluetooth, 2 USB) |
| 0x0280 | `RREC_LOG_DROPPED` | records dropped from the full RAM buffer (FW l.1062) | count u32 |
| 0x0290 | `RREC_LOG_UNMOUNT_FAILED` | storage could not be unmounted when a row asked for VDD_SD off (FW l.178, l.179); written at the first failed try of a step and once more when the retries of that step end, never once per try (rulings of 2026-11-13 after review finding R6-03: 27 codes) | errno i32 (at the end: 0 when the unmount then succeeded, else the last errno), state u8 (enum rc_state), try u8 (1 at the first failed try; at the end the number of tries made) |


## questions_for_owner

1. USB ids: the ring needs a USB vendor id and product id before production. Buy a vendor id from the USB-IF, or use a product id under a vendor that lends them (for prototypes the firmware uses the Zephyr project's test ids)?

RESULT: done, F5 follows architecture 17.11 to 17.23, wiring A7 and the assembly order; the check runs and their exit codes are listed in design/firmware-f5-notes.md.
