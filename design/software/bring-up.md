# How the software gets on the ring and how it is configured

Date: 2026-11-11. Sources: the behaviour specification `design/firmware.md` (version F6, cited as FW with its section), the assembly order `design/mfg/assembly/assembly.md` (AS with its step), and the reader's findings `design/software/research-toolchain.md` (RT with its section). Tags of the reader's file: [F] = the page was opened and read; [S] = search text only. A step marked [S] must be confirmed on the bench before it is trusted.

## 0. What exists and what does not

- Exists: the behaviour specification (states, gestures, storage format, USB commands, power rules, factory tests) and the list of 15 software pieces to write, W1 to W15, with their order (FW 10.2, 10.3).
- Does not exist: any source code, the test fixture, a driver for the ring's screen (no Zephyr driver exists for the SH8501A, FW 10.2 W2), the battery model of the real cell.
- So nothing can be put on a ring today. The steps below are the procedure once the pieces are written.

## 1. The three entrances to the chip

| Entrance | Where | When it can be used | What it does |
|---|---|---|---|
| Programming contacts (SWD) | test pads TP3 SWDCLK, TP4 SWDIO, TP5 NRESET on the circuit board (FW 9.3 flow table, step 5) | only on the bare board, before the ring is closed | writes the start program, the software and the settings; sets the lock |
| Debug text output | test pads DBG_TX P1.15 and DBG_RX P1.16, 115,200 baud, development builds only (FW 9.4) | bare board | reads the log |
| USB through the charging pads | pads CP1 to CP4 on the inside of the band: VBUS, D-, D+, GND (architecture 17.15) | from the moment the cables are joined, for the whole life of the ring | identity, tests, settings, first charge, ship mode, software update with rollback |
| Bluetooth | radio | when the phone link exists (that work is stopped) | not part of bring-up |

After assembly step 17 only the four pads reach the chip (FW 9.2). A ring whose software no longer starts USB cannot be rescued today. Proposed addition, not yet in the specification and not size-checked: a rescue mode in the start program (hold the joystick while the ring gets power in the case; the start program accepts a new image over USB).

## 2. What you need on the bench

- A computer. Nordic's install page lists Ubuntu 24.04 as tested with Nordic hardware and Windows 11 x64 as built and tested; the reader's summary of that page shows "Not supported" beside macOS 26 with an unclear layout (RT 2). Check that page before you install on a Mac.
- Nordic's development kit nRF54LM20 DK (PCA10184). Nordic offers no kit for the ring's exact chip, the nRF54LM20A; the kit emulates it with the board target `nrf54lm20dk/nrf54lm20a/cpuapp` (RT 1, [F] Zephyr board page).
- Nordic's nPM1304 evaluation kit, for the power chip and for the battery model (RT 6).
- A debug probe: SEGGER J-Link is the default in the kit's table (RT 4). Whether the kit's own debug-out header can program the ring's 1.8 V board, and at which voltage, was not found in a readable source (RT 4): confirm it in the kit's hardware guide before the first board is connected.
- A fixture that touches TP3, TP4, TP5, ground and the supply on the bare board, and a fixture or the charging case that touches the four pads. Neither is designed yet (FW 10.2 W13; the case design holds the pins).

## 3. Install the tools (RT 2, [F] read through a page summary: check each command on first use)

```
nrfutil install sdk-manager
nrfutil sdk-manager search
nrfutil sdk-manager install <version>
nrfutil sdk-manager toolchain launch --ncs-version <version> --shell
```

- Use an nRF Connect SDK version of 3.1.1 or later. Version 3.1.1 is the first with support for the nRF54LM20A, marked experimental there (RT 1). Write the chosen version into the software's own files and never build with "latest".
- The command-line build tool is `west`; the SDK installs it.

## 4. First proof on the development kit (RT 4, [F] Zephyr board page, example adapted to the A target)

```
west build -b nrf54lm20dk/nrf54lm20a/cpuapp samples/hello_world
west flash
```

- If the kit answers with a readback protection error: `west flash --recover` (RT 4, RT 8).
- Log output: over the kit's serial port, or over the probe with `CONFIG_LOG_BACKEND_RTT` and `CONFIG_USE_SEGGER_RTT` (RT 5).

## 5. Develop the software on the kit, in this order (FW 10.3)

W1 board files, W12 state machine, W9 gestures, W10 feedback on the kit; W4 audio with microphone evaluation boards; W5 storage with a storage breakout; W6 USB; W8 power with the nPM1304 kit; W2 the screen driver when screen samples arrive; W7, W11, W13, W14 last.

- W1, the ring's own board description: a board folder named `ring_nrf54lm20a` with `board.yml`, `board.cmake` and the devicetree, started from the kit's files (FW 10.2; RT 3, Zephyr board porting page).

## 6. Configure the power chip (FW 8.1; RT 6)

The settings live in the board's devicetree, in one place each:

| Setting | Value | Devicetree property (Zephyr binding `nordic,npm1304-charger`, RT 6 [F]) |
|---|---|---|
| Charge current | 15 mA | `current-microamp = <15000>` |
| Charge end voltage | 4.35 V | `term-microvolt = <4350000>` |
| End of charge | 10 percent of the charge current | `term-current-percent = <10>` |
| Input current limit | 500 mA | `vbus-limit-microamp = <500000>` |
| Battery temperature sensor | 10 kilo-ohm, beta 3,380 | `thermistor-ohms = <10000>`, `thermistor-beta = <3380>` |
| Two supply rails | 1.8 V and 3.0 V | regulator nodes of `nordic,npm1304-regulator` |

- Several property names of FW 8.1 are still marked TO CONFIRM there; the charger names above are confirmed by the binding page.
- Nordic's desktop app nPM PowerUP exports the power chip's whole configuration as a devicetree overlay (RT 6).
- Battery model: connect the real curved cell to the nPM1304 evaluation kit, profile it with nPM PowerUP, and put the model file it writes into the software for the fuel gauge library (RT 6 [F]). No size limit for a cell of 18 to 32 mAh was found; Nordic recommends profiling your own battery (RT 6 [S]). The cell does not exist yet (open item S12).

## 7. Put the software on a real ring

Stage A, bare circuit board (AS step 5; FW 9.3 flow table):
1. The fixture feeds a battery voltage on the cell lands and 10 kilo-ohm on the sensor land, and touches TP3, TP4, TP5.
2. Write the start program (MCUboot), the software image and the settings with the factory mark set to 1. Tool: `west flash`, or Nordic's `nrfutil device program --firmware <file> --options chip_erase_mode=ERASE_ALL` followed by `nrfutil device reset --reset-kind=RESET_PIN` ([S], RT 4 and research-production.md section 4: confirm with `nrfutil device program --help`).
3. Read everything back and compare.
4. Set the lock of the start program (FW 9.2 rule 4; the chip's register for it is still TO CONFIRM, FW 10.5 item 33).
5. Run the board tests over USB on the cable lands: identity, storage, clock crystal, radio, both microphones, light, charger state.
6. This is the last use of the programming contacts.

Stage B, ring with its cables joined, then closed (AS steps 16 to 27; FW 9.3):
1. Step 16: the ring starts on its own cell; with power on the pads it charges and answers GET_INFO over USB.
2. Step 18: the fixture sends FACTORY ENTER and runs every test: screen, joystick, centre press, motor, microphones, light, storage, radio, crystal, charger.
3. Steps 20, 21, 24: joystick, motor, microphones and screen again after the dam, the liner and the leak test.
4. Step 25: every test again on the closed ring, then one recording on the cell alone.
5. Step 26: first charge at 15 mA to 50 percent, 0.59 to 1.06 hours by ring size.
6. Step 27: SHIP_ENTER, power removed, the ring sleeps until it meets a charger.

Later updates: over USB through the pads. The case or a computer sends FW_BEGIN, FW_DATA blocks and FW_END; the start program checks the signature and swaps; a version that fails its 30 second self-test is swapped back (FW 9.2).

## 8. Check that it works

- From a phone: Nordic's app nRF Connect for Mobile shows the ring's advertising and its services (RT 7 [S]).
- From a computer: the reference tool W15 speaks the USB commands of FW section 6 (not written yet).
- The ring's own event log and crash record are read with GET_LOG (FW 9.4).

## 9. Lock and unlock (RT 8, summary quotes of Nordic's page: check the exact words there)

- The chip's debug access is closed by a register (UICR.APPROTECT). A closed chip is opened again only by an erase of everything.
- A second register (UICR.ERASEPROTECT) blocks that erase. With both set the chip cannot be unlocked or recovered. Do not set both on development units.

## 10. Not verified, to settle before the first board

- The exact `nrfutil device` commands (search text only; Nordic's manual pages refused automated reading).
- The maturity of the nRF54LM20A support in the SDK version chosen (experimental in 3.1.1).
- Programming a 1.8 V target from the kit's debug-out header.
- Mac support of the SDK version chosen.
- The devicetree names marked TO CONFIRM in FW 8.1, and the lock register of FW 9.2.
- No fuel gauge binding for the nPM1304 was found in Zephyr; the fuel gauge is Nordic's library in the nRF Connect SDK (RT 1).
