import sys
p = sys.argv[1]
s = open(p, encoding="utf-8").read()
reps = [
("- MCUboot mode: swap using move, so an image that is not confirmed is swapped back at the next reset.\n",
 "- MCUboot mode: swap using move, so an image that is not confirmed is swapped back at the next reset.\n"
 "- **Boot loader locked against USB writes** (assembly conflict K-A1, applied). After assembly step 17 only the four pads reach the chip, and a broken boot loader would scrap the ring. Rules: (1) the USB update path (FW_BEGIN, FW_DATA, FW_END) writes only slot 1, 0x00104000 to 0x001F7FFF: FW_BEGIN refuses an `image_size` above 976 KB (999,424 bytes) and FW_DATA refuses an offset plus length past it, both with BAD_ARG; (2) no command writes the MCUboot area (0x00000000 to 0x0000FFFF) or slot 0, so MCUboot itself is never updated in the field; (3) the settings area is written only by the settings subsystem; (4) the MCUboot area is also write-protected by the chip's own memory protection, set over SWD at assembly step 5 before the board leaves its test pads. The nRF54LM20A mechanism for (4) and its register are TO CONFIRM (section 10.5, item 33); until it is confirmed, rules (1) to (3) carry the lock [CALC: 0x00104000 + 976 x 1,024 = 0x001F8000].\n"),
("- Entry: USB FACTORY sub-command 0x01 (ENTER) while the factory flag in settings is 1. The flag is written when the factory first programs the ring, and cleared by SHIP_ENTER (sub-command 0x7F). With the flag clear, FACTORY returns NOT_ALLOWED.",
 "- Entry: USB FACTORY sub-command 0x01 (ENTER) while the factory flag in settings is 1. The flag is written when the factory first programs the ring (assembly step 5), and cleared only by SHIP_ENTER (sub-command 0x7F). SHIP_SAMPLE (0x7E) enters ship mode and keeps the flag, for sample rings only, so a ring woken for a sample check can be tested again (assembly conflict K-A7). With the flag clear, FACTORY returns NOT_ALLOWED."),
("| 0x40 | T-MOTOR | motor | MOTOR on 500 ms | jig accelerometer sees vibration; battery current rises by 30 mA or more during the pulse |",
 "| 0x40 | T-MOTOR | motor | the power chip's ADC reads VBAT once before MOTOR goes high; MOTOR on 500 ms; VBAT read again 250 ms into the pulse; the ring reports both and the dip. The chip's battery current is not used: the motor's current does not pass the chip (section 3.1; motor-drive.md change F5) | jig accelerometer sees vibration; VBAT drops during the pulse by 20 mV or more **[ESTIMATE]**: 80 mA through 0.25 ohm of cell, protection circuit and ribbon; bench step B-M5 of motor-drive.md section 2.9 measures the real dip and then fixes this line |"),
("| 0x70 | T-CHARGE | charger | with VBUS, read charge current and state; the result is fail when the state is \"off\" (the charger must be on while VBUS is present, rule R-CHG) | BLOCKED on open item S12: no pass limit is set (F2 had 61 to 75 mA for the A3 cell); the test reports current and state with result 0 and the jig records them |",
 "| 0x70 | T-CHARGE | charger | with VBUS, read the charge state (BCHGCHARGESTATUS [NPM p40, p41]), the latched errors (BCHGERRREASON [NPM p41]) and the battery current; the result is fail when the state is off or an error is latched (rule R-CHG) | state trickle, constant current, constant voltage or completed; in constant current the current is 13.5 to 16.5 mA [CALC: 15 mA plus or minus 10 %, NPM p29]. At the board stage (assembly step 5) the jig's battery source sets what is seen, so only the state is judged there |"),
("| 0x7F | SHIP_ENTER | | clear the factory flag; ship mode | |",
 "| 0x7E | SHIP_SAMPLE | | sample rings only: keep the factory flag; ship mode: the ring waits for VBUS removal, then writes TASKENTERSHIPMODE (section 8.4) | VBUS removed: no advertising for 60 s; VBUS back: the ring wakes and FACTORY ENTER works again |\n"
 "| 0x7F | SHIP_ENTER | | clear the factory flag; ship mode: the ring waits for VBUS removal, then writes TASKENTERSHIPMODE (section 8.4) | VBUS removed: no advertising for 60 s (assembly step 27) |"),
("Sub-command 0x11 (the F2 skew test) is removed in F3: the ring answers BAD_ARG. T-LIGHT is the same test as in F2.",
 "Sub-command 0x11 (the F2 skew test) is removed in F3: the ring answers BAD_ARG. T-LIGHT is the same test as in F2.\n\n"
 "Factory flow, step by step of `design/mfg/assembly/assembly.md` (the jig is work item W13):\n\n"
 "| Assembly step | Stage | Access | What the firmware is asked to do or pass | Not tested here, and why |\n"
 "|---|---|---|---|---|\n"
 "| 5 | board | SWD on test pads TP3 SWDCLK, TP4 SWDIO, TP5 NRESET; USB on the J_BAND_B lands; the jig feeds a battery voltage on the cell lands and 10 kilo-ohm on the thermistor land | write and read back MCUboot, the image and the settings with the factory flag 1; set the boot loader lock (section 9.2); GET_INFO; T-STORE, T-XTAL, T-RADIO, T-MIC1, T-MIC2, T-LIGHT, T-CHARGE (state only) | T-SCREEN, T-JOY, T-CENTRE, T-MOTOR: the screen, the switches and the motor are not joined yet. This is the last SWD access of the ring's life |\n"
 "| 16 | ribbons joined, cell live | USB through the pads CP1 to CP4 | the ring boots to `STANDBY` on its cell; GET_INFO answers | |\n"
 "| 18 | open ring | USB through the pads; FACTORY ENTER | every test: T-SCREEN, T-JOY, T-CENTRE, T-MOTOR, T-MIC1, T-MIC2, T-LIGHT, T-STORE, T-RADIO, T-XTAL, T-CHARGE | |\n"
 "| 20 | joystick pocket dammed | as step 18 | T-JOY, T-CENTRE | |\n"
 "| 21 | liner cast | as step 18 | USB enumerates; T-JOY, T-CENTRE, T-MOTOR | |\n"
 "| 24 | after the leak dip | as step 18 | T-MIC1, T-MIC2, T-SCREEN; USB enumerates | |\n"
 "| 25 | closed ring | as step 18 | every test again, then the cell-only check below | |\n"
 "| 26 | first charge | VBUS on the pads | charge to 50 percent before ship mode **[PROPOSED]** (below) | |\n"
 "| 27 | ship | VBUS on the pads, then removed | SHIP_ENTER, then the jig removes VBUS; sample rings get SHIP_SAMPLE instead | |\n\n"
 "- Cell-only check of step 25 **[PROPOSED by assembly step 25]**: the jig sends FACTORY_EXIT (the ring reboots into `CHARGING`) and reads `boot_count` n with GET_INFO; it removes VBUS (`CHARGING` to `STANDBY`, no reboot); a long press starts a recording with M1 and a second long press stops it with M2; it puts VBUS back (`STANDBY` to `CHARGING`); GET_INFO must give n again, and GET_LOG must show no power-chip reset cause (section 8.7). Then the jig lists the recording, confirms it with its digest and deletes it (section 5.7), so the ring ships empty. FACTORY_EXIT comes first because removing VBUS in `FACTORY_TEST` reboots the ring (section 1.2), which would add 1 to the count.\n"
 "- First charge of step 26 **[PROPOSED by assembly step 26]**: the charger runs at `CHARGE_CURRENT`, 15 mA, to 4.35 V; the jig reads GET_BATTERY until the state of charge reaches 50 percent (500 in `soc_percent_x10`), then goes to step 27. From an empty cell that takes about 0.61 to 1.10 hours across US 7 to 13 [CALC: 0.5 x 18.2 / 15 and 0.5 x 32.9 / 15]. The cell's maker may set another storage level (S12); the reading depends on the battery model (section 10.5, item 4).\n"
 "- Ship of step 27: SHIP_ENTER, then VBUS removed; the ring writes TASKENTERSHIPMODE only after the event EVENTVBUSREMOVED (section 8.4). The jig checks that no advertising is seen for 60 s."),
("- Watchdog: `wdt31`, 8 s timeout,",
 "- Power-chip reset causes: `BOOT` writes the nPM1304's RSTCAUSE and charger error log into the event log, then clears them (section 8.7).\n- Watchdog: `wdt31`, 8 s timeout,"),
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
