# firmware.md for ring v7: no recording light, round joystick

Date 2026-11-11. Source: `design/architecture.md` 17.11, 17.29, 17.30. Files changed: `design/firmware.md` (40 change blocks, listed below with old and new text), `design/firmware-check.py` (one netlist fact dropped, new check 21, docstring). Nothing else was written outside this folder. No git command was run.

## What the v7 rule is in firmware.md

- Section 3.2 is now "Recording sign on the screen": rule R-SIGN (in `RECORDING` the screen is never dark; at least the red dot and the timer; full picture SCR_RECORDING for 3 s after any input; dimmed picture SCR_REC_DIM after 3 s without input, lowest of the 3 brightness levels [CHOICE]).
- One code path: `rec_mics_on()` is the only code that enables VDD_MIC; it draws the dot and timer first and enables VDD_MIC only if the screen accepted the frame (4.5 start step 2).
- New transition row (1.2): `STANDBY`, "long press of the joystick centre, recording sign not drawn" -> `STANDBY`, VDD_MIC stays off, M3, event log. The table now has 72 rows (was 71).
- Test SIGN-1 (W12 state-machine tests): every row of 1.2, then a 10 s idle run at 100 ms ticks; VDD_MIC on must mean OLED_PWR_EN high, the screen not blanked and the red dot in the last frame; a forced draw failure must leave VDD_MIC off.
- Factory test 0x41 T-LIGHT is replaced by T-SIGN (jig camera: red dot lit in every frame while VDD_MIC is on). It moves from assembly step 5 (board, no screen yet) to the "not tested here" column of step 5; it runs at step 18.
- Lines that would have made the screen dark while recording were changed to dim instead: 1.1 `RECORDING` screen cell, 2.2 lock, collision C4, 3.3 opening line, 8.2 `RECORDING` screen supply, 8.7 current-limit item 2. These lines name no removed part; they had to change or they contradict R-SIGN.
- Control: the centre switch is written "centre switch SW2 (net BTN_REC)"; "nub" became "round cap" in current rules (2.1, 2.2 heading, 3.1, 10.5 item 27, peripheral table, 10.1 table). The 2.2 heading names the round joystick with five switches SW1 up, SW3 down, SW4 toward the hand, SW5 toward the fingertip, SW2 centre. Long press 1.0 s starts and stops; a short press while recording marks a highlight (unchanged).
- Budget (8.5): the 1.5 mA counted for the light is taken out in words: 4.1 - 1.5 = 2.6 mA [CALC] plus the dot, whose cost is a bench item with no number. The thresholds of 1.1 and the hours of 8.5 stay at 4.1 mA, the figure architecture 17.26 still uses [CHOICE, see "Decisions for the lead"].
- History lines (change lists, closed issues H3, H4, H15) keep their text and gain a tag that says "removed in v7".

## Checks (last lines; logs in `design/firmware-v7-evidence/`)

| Run | Log | Last lines |
|---|---|---|
| Baseline, old checker, old firmware.md | `check-baseline-before-edit.log` | `0 failures`, `exit 0` |
| New checker, new firmware.md | `check-v7-pass.log` | `check 21 v7: 6 rule groups checked, 0 lines name a removed part without 'removed in v7'; netlist.csv still holds none of LED1, R41, Q2`, `0 failures`, `exit 0` |
| Broken copy: LED1 line put back in 3.2 | `check-broken-led1.log` | `FAIL v7: line 338 names a removed part ...`, `1 failures`, `exit 1` |
| Broken copy: a "Record button" row put back | `check-broken-record-button.log` | `FAIL removed name 'record button' ...`, `FAIL v7: line 952 ...`, `2 failures`, `exit 1` |
| Broken copy: 8.2 `RECORDING` screen back to "when the screen is on" | `check-broken-screen-dark.log` | `FAIL v7: the screen supply of RECORDING in 8.2 must be on for the whole recording`, `1 failures`, `exit 1` |
| grep of firmware.md for LED1, R41, Q2, LG1, LP1, recording light, light window, record button, nub | `grep-removed-names.log` | 16 lines, all 16 contain "removed in v7" |
| Diffs | `firmware-md.diff`, `firmware-check-py.diff` | |

Broken copies are in the scratch folder `<scratch>/broken/`.

## What is not proven

- That SIGN-1 and T-SIGN exist as code: they are written as rules only; no firmware test was written or run (the firmware folder was out of scope).
- The always-lit dot's current: no number exists; bench item on the new panel (architecture 17.30).
- That the lowest brightness level is readable outdoors and still visible to others as a recording sign: not tested.
- That a panel failing during a recording is caught: R-SIGN only refuses a start when the first frame is not accepted; nothing checks the panel during a recording (stated in 3.2 "What is lost").
- The checker reads text; it cannot prove the meaning of a sentence. Review still owns that.
- netlist.csv held LED1, R41 and Q2 at my baseline run and no longer holds them at my last run: another helper changed it during this work. The checker only reports these three parts; it does not judge the netlist.

## Decisions for the lead

1. **Recording current kept at 4.1 mA for thresholds and hours.** Taking 1.5 mA out of every computed figure would change B15/B5/B2 minutes and every hours table and break the match with architecture 17.26, which I may not edit. I wrote the light-free figure (2.6 mA plus the dot) and kept 4.1 mA as a fixed choice until the bench measures the dot. Change it if you prefer the 2.6 mA figure.
2. **Case `PAIR` (two opposite switches) stays as the second centre source**, as 17.11 still states it. It was never the primary; the brief asked to replace it only as a primary centre press. Remove it if v7 drops the fallback.
3. **Header and change list not touched:** the header still says "Version F6 ... sections 17.11 to 17.26" and there is no "Changes for v7" list, because my brief allowed only lines that name a removed part or the old control. These notes are the change record until you add one.
4. **New transition row** ("recording sign not drawn") changes the row count to 72 and shifts every line number after line 147 by one.

## Lines in `firmware/` that name a removed part (read only, not changed)

Full grep: `design/firmware-v7-evidence/grep-firmware-code.log` (133 lines).
- `firmware/tests/core/src/test_round2.c:243`: comment "thumb still on the nub".
- `firmware/tests/core/evidence/r2-firmware-md-before.md`, `r2b-`, `r3-`, `r3b-`, `r4-firmware-md-before.md`: 26 lines each; these are copies of older firmware.md versions kept as test evidence (history).
- `firmware/docs/review/core-review-1/probe2.c:11`: "Q2:" is a question number, not the transistor. Not a removed part.
- No source file of `firmware/app` or `firmware/modules` names the light or its parts.
- Related, not a name: `firmware/modules/ring_core/src/state_table.json` and `state_actions.c` mirror the 71 rows of 1.2 with firmware.md line numbers in comments. The new row 72 and the shift of line numbers after line 147 are not in the code yet; the code owner must add the refusal row and R-SIGN.

## Changed lines in firmware.md (old and new text, line numbers)

### Change 1: old lines 17-17 -> new lines 17-17 (replace)

- OLD 17: 5. **Recording light** (architecture 17.21): no firmware change; R41 is 820 ohm for 1.50 mA (F4 wrote 680 ohm); the current budget keeps 1.5 mA (section 3.2).
- NEW 17: 5. **Recording light** (architecture 17.21): no firmware change; R41 is 820 ohm for 1.50 mA (F4 wrote 680 ohm); the current budget keeps 1.5 mA (section 3.2). [v7: removed in v7 (architecture 17.30): the recording light, LED1, R41, Q2, the light guide LG1, the light pipe LP1 and the light window are out; the recording sign is the screen, section 3.2]

### Change 2: old lines 22-22 -> new lines 22-22 (replace)

- OLD 22: `firmware-check.py` checks the F5 rules (section 10.6). The state machine, the gestures, the one-control rule, the recording rule and the hard-wired recording light are those of F4; the transition table gains one row (SHIP_SAMPLE) and has 61 rows.
- NEW 22: `firmware-check.py` checks the F5 rules (section 10.6). The state machine, the gestures, the one-control rule, the recording rule and the hard-wired recording light are those of F4; the transition table gains one row (SHIP_SAMPLE) and has 61 rows. [v7: removed in v7 (architecture 17.30): the recording light, LED1, R41, Q2, the light guide LG1, the light pipe LP1 and the light window are out; the recording sign is the screen, section 3.2]

### Change 3: old lines 25-26 -> new lines 25-26 (replace)

- OLD 25: 1. **One control** (17.11): the separate record button is removed (no pill, no cap, no opening). The record gesture lives on the joystick's CENTRE press: long press 1.0 s starts a recording from standby, long press 1.0 s stops it, a short press while recording marks a highlight, a double press does nothing; a direction (up, down, toward the hand, toward the fingertip) never starts or stops a recording (sections 1.2, 2.1, 2.2). The owner's rule is unchanged: "The ring shouldn't CONSTANTLY record, only when a long press on it. Then you have a live storing audio".
- OLD 26: 2. **Source of the centre press, both cases** (17.11): build constant `CENTRE_SOURCE` = `SW2` (a real switch on BTN_REC P0.04 under the nub's centre, the first choice) or `PAIR` (two opposite switches within 40 ms, 16.5, bench B6). One table row per case (section 2.1); every other rule holds for both. A long press held through a slight roll of the thumb does not end early (centre key latch, section 2.2).
- NEW 25: 1. **One control** (17.11): the separate record button is removed (no pill, no cap, no opening). The record gesture lives on the joystick's CENTRE press: long press 1.0 s starts a recording from standby, long press 1.0 s stops it, a short press while recording marks a highlight, a double press does nothing; a direction (up, down, toward the hand, toward the fingertip) never starts or stops a recording (sections 1.2, 2.1, 2.2). The owner's rule is unchanged: "The ring shouldn't CONSTANTLY record, only when a long press on it. Then you have a live storing audio". [v7: the record button is gone since 17.11 and the rectangular nub is removed in v7; the one control is the round joystick (architecture 17.29), centre switch SW2 (net BTN_REC)]
- NEW 26: 2. **Source of the centre press, both cases** (17.11): build constant `CENTRE_SOURCE` = `SW2` (a real switch on BTN_REC P0.04 under the nub's centre, the first choice) or `PAIR` (two opposite switches within 40 ms, 16.5, bench B6). One table row per case (section 2.1); every other rule holds for both. A long press held through a slight roll of the thumb does not end early (centre key latch, section 2.2). [v7: the record button is gone since 17.11 and the rectangular nub is removed in v7; the one control is the round joystick (architecture 17.29), centre switch SW2 (net BTN_REC)]

### Change 4: old lines 38-38 -> new lines 38-38 (replace)

- OLD 38: 5. **Record button = its own switch SW2 on BTN_REC** (17.3, 17.8): same gestures as F2 (long press 1.0 s starts, long press 1.0 s stops, short press marks a highlight, double press does nothing).
- NEW 38: 5. **Record button = its own switch SW2 on BTN_REC** (17.3, 17.8): same gestures as F2 (long press 1.0 s starts, long press 1.0 s stops, short press marks a highlight, double press does nothing). [v7: the record button is gone since 17.11 and the rectangular nub is removed in v7; the one control is the round joystick (architecture 17.29), centre switch SW2 (net BTN_REC)]

### Change 5: old lines 47-47 -> new lines 47-47 (replace)

- OLD 47: 1. The recording light has no chip pin (architecture A2 section 9, W5): the F1 light output pin, its patterns and its pattern player are removed; section 3.2 states what the hardware does and what it costs. H4 is closed.
- NEW 47: 1. The recording light has no chip pin (architecture A2 section 9, W5): the F1 light output pin, its patterns and its pattern player are removed; section 3.2 states what the hardware does and what it costs. H4 is closed. [v7: removed in v7 (architecture 17.30): the recording light, LED1, R41, Q2, the light guide LG1, the light pipe LP1 and the light window are out; the recording sign is the screen, section 3.2]

### Change 6: old lines 49-49 -> new lines 49-49 (replace)

- OLD 49: 3. Joystick and button use the chip's internal pull-ups (architecture W1).
- NEW 49: 3. Joystick and button use the chip's internal pull-ups (architecture W1). [v7: the record button is gone since 17.11 and the rectangular nub is removed in v7; the one control is the round joystick (architecture 17.29), centre switch SW2 (net BTN_REC)]

### Change 7: old lines 59-60 -> new lines 59-60 (replace)

- OLD 59: 13. VDD_MIC, and so the recording light, is on only in `RECORDING`, exactly while audio is stored (H3 closed; H2 closed with the removed state). Factory microphone tests are made as short test recordings.
- OLD 60: 14. Light resistor 680 ohm (1.5 mA) and the recording current of 4.9 mA (27 hours) copied from architecture A3. RAM budget 411,904 bytes (was 438,528); worst-case loss on sudden power loss 1.536 s; `firmware-check.py` adds checks for the removed names, the microphone rail and the long-press rule.
- NEW 59: 13. VDD_MIC, and so the recording light, is on only in `RECORDING`, exactly while audio is stored (H3 closed; H2 closed with the removed state). Factory microphone tests are made as short test recordings. [v7: removed in v7 (architecture 17.30): the recording light, LED1, R41, Q2, the light guide LG1, the light pipe LP1 and the light window are out; the recording sign is the screen, section 3.2]
- NEW 60: 14. Light resistor 680 ohm (1.5 mA) and the recording current of 4.9 mA (27 hours) copied from architecture A3. RAM budget 411,904 bytes (was 438,528); worst-case loss on sudden power loss 1.536 s; `firmware-check.py` adds checks for the removed names, the microphone rail and the long-press rule. [v7: removed in v7 (architecture 17.30): the recording light, LED1, R41, Q2, the light guide LG1, the light pipe LP1 and the light window are out; the recording sign is the screen, section 3.2]

### Change 8: old lines 82-82 -> new lines 82-82 (replace)

- OLD 82: | Buttons and joystick | GPIO with the chip's internal pull-up (`GPIO_PULL_UP \| GPIO_ACTIVE_LOW`, architecture W1), Zephyr `gpio-keys` input driver | BTN_REC P0.04 (SW2), JOY_UP P0.06 (SW1), JOY_DOWN P0.07 (SW3), JOY_LEFT P0.08 (SW4), JOY_RIGHT P1.31 (SW5) | `gpio-keys` has `debounce-interval-ms` [SRC 14]; since F4 BTN_REC is the centre switch under the nub when `CENTRE_SOURCE` is `SW2`, and unused (left as an input with the pull-up) when it is `PAIR` |
- NEW 82: | Joystick (round, five switches; architecture 17.29) | GPIO with the chip's internal pull-up (`GPIO_PULL_UP \| GPIO_ACTIVE_LOW`, architecture W1), Zephyr `gpio-keys` input driver | BTN_REC P0.04 (SW2), JOY_UP P0.06 (SW1), JOY_DOWN P0.07 (SW3), JOY_LEFT P0.08 (SW4), JOY_RIGHT P1.31 (SW5) | `gpio-keys` has `debounce-interval-ms` [SRC 14]; BTN_REC is the net of the centre switch SW2 (net BTN_REC) under the round cap when `CENTRE_SOURCE` is `SW2`, and unused (left as an input with the pull-up) when it is `PAIR` |

### Change 9: old lines 102-102 -> new lines 102-102 (replace)

- OLD 102: | `RECORDING` | a recording is being stored: 2 channels (2 microphones), 16 kHz, 16 bits, raw | on | on | off, on for 3 s after input | advertising |
- NEW 102: | `RECORDING` | a recording is being stored: 2 channels (2 microphones), 16 kHz, 16 bits, raw | on | on | never dark: SCR_RECORDING for 3 s after any input, else SCR_REC_DIM, the red dot and the timer dimmed (rule R-SIGN, section 3.2) | advertising |

### Change 10: old lines 144-144 -> new lines 144-144 (replace)

- OLD 144: | `STANDBY` | long press of the joystick centre | `RECORDING` | only with the superblock open flag clear, the battery above B5 and free space above SFULL (rulings R1, R4b; otherwise the next three rows, in their order): open; M1 |
- NEW 144: | `STANDBY` | long press of the joystick centre | `RECORDING` | only with the superblock open flag clear, the battery above B5, free space above SFULL and the recording sign drawn (rulings R1, R4b; rule R-SIGN, section 3.2; otherwise the next four rows, in their order): open; M1 |

### Change 11: old lines 148-147 -> new lines 148-148 (insert)

- NEW 148: | `STANDBY` | long press of the joystick centre, recording sign not drawn | `STANDBY` | no recording starts: the screen did not accept the red dot and the timer (rule R-SIGN, section 3.2); VDD_MIC stays off; M3; event log record |

### Change 12: old lines 205-205 -> new lines 206-206 (replace)

- OLD 205: The table has 71 transitions.
- NEW 206: The table has 72 transitions.

### Change 13: old lines 245-245 -> new lines 246-246 (replace)

- OLD 245: Centre source: build constant `CENTRE_SOURCE`, `SW2` by default (architecture 17.11 first choice; the rebuild of 17.12 must show that the switch fits under the nub's centre) or `PAIR` (17.11 second choice). Every rule outside this table is the same for both cases.
- NEW 246: Centre source: build constant `CENTRE_SOURCE`, `SW2` by default (architecture 17.11 first choice; the rebuild of 17.12 must show that the switch fits under the centre of the round cap of 17.29) or `PAIR` (17.11 second choice). Every rule outside this table is the same for both cases.

### Change 14: old lines 249-249 -> new lines 250-250 (replace)

- OLD 249: | `SW2` | SW2 on BTN_REC P0.04, a real switch under the nub's centre: its debounced press edge is CENTRE_DOWN | 20 ms (`gpio-keys`) on SW2 and on each direction switch | a direction switch that closed 0 to 40 ms before SW2 is dropped and the centre wins; one that closed 40 ms or more before SW2 keeps its direction and SW2 is ignored until all switches are open; nothing else |
- NEW 250: | `SW2` | SW2 on BTN_REC P0.04, the centre switch SW2 (net BTN_REC), a real switch under the centre of the round cap: its debounced press edge is CENTRE_DOWN | 20 ms (`gpio-keys`) on SW2 and on each direction switch | a direction switch that closed 0 to 40 ms before SW2 is dropped and the centre wins; one that closed 40 ms or more before SW2 keeps its direction and SW2 is ignored until all switches are open; nothing else |

### Change 15: old lines 252-252 -> new lines 253-253 (replace)

- OLD 252: Guard against accidental starts. The nub sits where the thumb rests, so a thumb at rest can hold the centre. The guard, in order:
- NEW 253: Guard against accidental starts. The round cap sits where the thumb rests, so a thumb at rest can hold the centre. The guard, in order:

### Change 16: old lines 255-255 -> new lines 256-256 (replace)

- OLD 255: - **G3** at 1,000 ms a start gives M1 and the recording light comes on with VDD_MIC; a stop gives M2.
- NEW 256: - **G3** at 1,000 ms a start gives M1 and the recording sign, the red dot and the timer, is on the screen before VDD_MIC comes on (rule R-SIGN, section 3.2); a stop gives M2.

### Change 17: old lines 258-258 -> new lines 259-259 (replace)

- OLD 258: - Cost: the first 1.0 s of a meeting is not recorded (no audio is kept before the start, owner rule) plus the 50 ms discard of section 4.5, and up to 40 ms more in case `PAIR`; a start needs one still second of thumb; MW at 500 ms of a stop hold, and of any hold that passes 500 ms in `RECORDING`, is a motor pulse inside the audio, marked like every pulse (section 4.7); a short press longer than 450 ms is lost. Not guarded: a thumb that rests on the centre for a full second without lifting does start a recording, and the user is told by M1 and the light; the same press stops it.
- NEW 259: - Cost: the first 1.0 s of a meeting is not recorded (no audio is kept before the start, owner rule) plus the 50 ms discard of section 4.5, and up to 40 ms more in case `PAIR`; a start needs one still second of thumb; MW at 500 ms of a stop hold, and of any hold that passes 500 ms in `RECORDING`, is a motor pulse inside the audio, marked like every pulse (section 4.7); a short press longer than 450 ms is lost. Not guarded: a thumb that rests on the centre for a full second without lifting does start a recording, and the user is told by M1 and the red dot on the screen; the same press stops it.

### Change 18: old lines 268-268 -> new lines 269-269 (replace)

- OLD 268: ### 2.2 Joystick (four direction switches under one nub: SW1 up JOY_UP P0.06, SW3 down JOY_DOWN P0.07, SW4 toward the hand JOY_LEFT P0.08, SW5 toward the fingertip JOY_RIGHT P1.31; the centre press comes from SW2 or from an opposite pair, section 2.1; the JOY_CENTER pin is unused)
- NEW 269: ### 2.2 Joystick (the round joystick of architecture 17.29, five switches under one round cap: SW1 up JOY_UP P0.06, SW3 down JOY_DOWN P0.07, SW4 toward the hand JOY_LEFT P0.08, SW5 toward the fingertip JOY_RIGHT P1.31, SW2 the centre (net BTN_REC); the centre press comes from SW2 or from an opposite pair, section 2.1; the JOY_CENTER pin is unused)

### Change 19: old lines 276-276 -> new lines 277-277 (replace)

- OLD 276: - **Lock:** when the screen is off, the first joystick event (a direction or a short press of the centre) only turns the screen on; it is not acted on. A long press is not an event of this rule (collision C4). The screen turns off 5 s after the last input (3 s in `RECORDING`). There is no other lock.
- NEW 277: - **Lock:** when the screen is off, or shows the dimmed SCR_REC_DIM in `RECORDING`, the first joystick event (a direction or a short press of the centre) only turns the full screen on; it is not acted on. A long press is not an event of this rule (collision C4). The screen turns off 5 s after the last input; in `RECORDING` it never turns off: 3 s after the last input it dims to SCR_REC_DIM (rule R-SIGN, section 3.2). There is no other lock.

### Change 20: old lines 300-300 -> new lines 301-301 (replace)

- OLD 300: - **C4** the screen-off lock. F3: the first joystick event only wakes the screen. A long press with the screen off must start a recording. Result: the lock covers directions and short presses only; a long press with the screen off starts a recording; in `RECORDING` a short press with the screen off marks the highlight and turns the screen on for 3 s.
- NEW 301: - **C4** the screen-off lock. F3: the first joystick event only wakes the screen. A long press with the screen off must start a recording. Result: the lock covers directions and short presses only; a long press with the screen off starts a recording; in `RECORDING` a short press with the screen dimmed (SCR_REC_DIM) marks the highlight and shows SCR_RECORDING for 3 s.

### Change 21: old lines 323-323 -> new lines 324-324 (replace)

- OLD 323: - The 1, 2 and 3 pulse counts follow requirement U4 and architecture section 9. MW is new in F4: one 60 ms pulse **[CHOICE]**, between MT (25 ms) and M1 (80 ms), felt at the thumb that rests on the nub; **[BENCH]** test F1 also judges it. It sounds only while the centre is held, so no other pattern can run at the same time.
- NEW 324: - The 1, 2 and 3 pulse counts follow requirement U4 and architecture section 9. MW is new in F4: one 60 ms pulse **[CHOICE]**, between MT (25 ms) and M1 (80 ms), felt at the thumb that rests on the round cap; **[BENCH]** test F1 also judges it. It sounds only while the centre is held, so no other pattern can run at the same time.

### Change 22: old lines 329-329 -> new lines 330-330 (replace)

- OLD 329: ### 3.2 Recording light
- NEW 330: ### 3.2 Recording sign on the screen (architecture 17.30)

### Change 23: old lines 331-333 -> new lines 332-338 (replace)

- OLD 331: - No chip pin touches the light (architecture 17.21, netlist.csv): VDD_3V0, R41 820 ohm, LED1 (Kingbright KPG-1005SURC-TT, nets LED_A and LED_K), transistor Q2 whose gate is VDD_MIC. The light is steady on exactly while VDD_MIC is on and dark while it is off. The firmware has no light pattern and no light code. F5 changes nothing here.
- OLD 332: - The firmware's only influence is when VDD_MIC is on: only in `RECORDING` (section 1.1), including the test recordings of factory tests T-MIC and T-LIGHT (section 9.3). So the light is on exactly while audio is stored (H3 closed).
- OLD 333: - Cost: light current (3.0 V - 1.767 V) / (820 ohm + 0.7 ohm) = 1.50 mA from VDD_3V0 [CALC; 1.767 V at 1.5 mA from the maker's curve and R41 820 ohm, architecture 17.21; 0.7 ohm is Q2, sch-notes section 12.1 item 20] = 1.50 x 3.0 / (3.8 x 0.9) = 1.32 mA from the cell [CALC], only while recording. The recording current of 4.0 mA in architecture 17.15 already counts 1.5 mA for the light, so the budget keeps it (section 8.5). F4 wrote (3.0 V - 2.0 V) / 680 ohm = 1.5 mA; with the light's real 1.767 V, 680 ohm gives 1.81 mA (architecture 17.21), which is why R41 became 820 ohm.
- NEW 332: - **No recording light:** removed in v7 (architecture 17.30): LED1, R41, Q2, the light guide LG1, the light pipe LP1, the light window in the glass print and its plug are out of the design. The firmware had no light code before and has none now. The sign that a recording runs is the screen, drawn by the firmware.
- NEW 333: - **R-SIGN, the screen is never dark while recording** (the lead's rule of 17.30): in `RECORDING` the screen is on from the start of the recording to its close and shows at least the red dot and the timer of this recording. Any input (any switch of the joystick) shows the full recording picture SCR_RECORDING for 3 s; 3 s after the last input it dims to SCR_REC_DIM (section 3.3) until the next input.
- NEW 334: - **Dimmed** **[CHOICE]**: SCR_REC_DIM draws only the red dot and the timer HH:MM:SS on true black, at the lowest of the three levels of the setting "Screen brightness" (section 2.2); the timer is redrawn once per second.
- NEW 335: - **One code path:** the function `rec_mics_on()` is the only code that enables VDD_MIC (section 4.5, start step 2). It first powers the screen if it is off (sequence of section 3.3) and draws the red dot and the timer at 00:00:00; it enables VDD_MIC only when the screen driver has accepted that frame (`display_write()` returned 0 and the display is not blanked). If it fails, VDD_MIC stays off and the row "long press of the joystick centre, recording sign not drawn" applies (section 1.2). The close turns VDD_MIC off before the screen may leave the recording pictures. Nothing in `RECORDING` blanks the screen or drives OLED_PWR_EN low: the screen-off timer, the lock of section 2.2 and the current-limit action of section 8.7 dim to SCR_REC_DIM instead.
- NEW 336: - **Test SIGN-1** (proves that no state records with the screen dark), one of the state-machine tests of W12 (section 10.2): for every row of the table of 1.2, run from its From state with a screen stub that records blanking, OLED_PWR_EN and every frame; after the row, and at every 100 ms tick of a 10 s idle run after it, VDD_MIC on must mean OLED_PWR_EN high, the screen not blanked and the last frame holding the red dot pixels. A forced draw failure at the start must leave VDD_MIC off. One failing case fails the build. Factory test T-SIGN (section 9.3) checks the same on each ring with the jig camera.
- NEW 337: - **Cost: a bench item, no number.** The always-lit red dot and timer draw current from the screen for the whole recording; the cost is measured on the new panel (bench, architecture 17.30) and is not counted in section 8.5. The 1.5 mA once counted for the recording light, removed in v7, is out of the budget (section 8.5).
- NEW 338: - **What is lost** (architecture 17.30): the sign is drawn by software and is no longer wired to the microphone supply; a firmware fault or a panel that fails during a recording can leave a recording without a visible sign. SIGN-1 tests the firmware and T-SIGN the panel at the factory; nothing tests the panel during use.

### Change 24: old lines 337-337 -> new lines 342-342 (replace)

- OLD 337: Screen: 120 x 240 pixels, RGB565, portrait. The screen is off in every recording state except for the times stated (requirement P6). Font: one bitmap font at 16 px and one at 32 px (for the timer). Colours: white text on black; red for the recording dot; amber for warnings.
- NEW 342: Screen: 120 x 240 pixels, RGB565, portrait. The screen is off in every state except for the times stated (requirement P6); in `RECORDING` it is never dark (rule R-SIGN, section 3.2). Font: one bitmap font at 16 px and one at 32 px (for the timer). Colours: white text on black; red for the recording dot; amber for warnings.

### Change 25: old lines 343-342 -> new lines 348-348 (insert)

- NEW 348: | SCR_REC_DIM | `RECORDING`, from 3 s after the last input to the next input | red dot and timer HH:MM:SS only, true black elsewhere, lowest brightness level (section 3.2) |

### Change 26: old lines 421-421 -> new lines 427-427 (replace)

- OLD 421: 2. `regulator_enable()` on the nPM1304 load switch 1 (VDD_MIC, ball A4 LSOUT1, netlist.csv). The recording light turns on here (hardware, section 3.2).
- NEW 427: 2. `regulator_enable()` on the nPM1304 load switch 1 (VDD_MIC, ball A4 LSOUT1, netlist.csv), called only by `rec_mics_on()` after the screen accepted the red dot and the timer (rule R-SIGN, section 3.2); a failed draw leaves VDD_MIC off and no recording starts.

### Change 27: old lines 427-427 -> new lines 433-433 (replace)

- OLD 427: Stop: `dmic_trigger(pdm20, DMIC_TRIGGER_STOP)`; wait for the driver to release its blocks (`dmic_read()` returns an error); apply the pin sleep state so MIC_A_CLK is driven low; `regulator_disable()` on VDD_MIC (active discharge on, section 8.1); release HFXO. The light goes dark with the rail.
- NEW 433: Stop: `dmic_trigger(pdm20, DMIC_TRIGGER_STOP)`; wait for the driver to release its blocks (`dmic_read()` returns an error); apply the pin sleep state so MIC_A_CLK is driven low; `regulator_disable()` on VDD_MIC (active discharge on, section 8.1); release HFXO. Only after VDD_MIC is off may the screen leave the recording pictures (rule R-SIGN, section 3.2).

### Change 28: old lines 788-788 -> new lines 794-794 (replace)

- OLD 788: | `RECORDING` | on | on | on | on | when the screen is on | on | advertising | PDM blocks every 16 ms, as `STANDBY` |
- NEW 794: | `RECORDING` | on | on | on | on | on for the whole recording (rule R-SIGN, section 3.2) | on | advertising | PDM blocks every 16 ms, as `STANDBY` |

### Change 29: old lines 841-841 -> new lines 847-847 (replace)

- OLD 841: Caveat, from architecture section 4 and 16.8: the main-chip, storage, radio and power-chip lines are estimates, not datasheet values, and bench test B2 replaces them; the microphone line is from the Knowles datasheet copy at its 2.4 MHz test clock, not at the ring's 1.280 MHz (section 10.5, item 6). The recording figure includes the recording light (1.50 mA at 3.0 V, section 3.2). It excludes the motor (section 3.1) and the screen. **Requirement P2 (10 hours of recording) is NOT met by this ring**: the owner chose thinness over hours on 2026-11-10 (architecture 17.5). In every state other than `RECORDING` the microphones and the light are off.
- NEW 847: Caveat, from architecture section 4 and 16.8: the main-chip, storage, radio and power-chip lines are estimates, not datasheet values, and bench test B2 replaces them; the microphone line is from the Knowles datasheet copy at its 2.4 MHz test clock, not at the ring's 1.280 MHz (section 10.5, item 6). The recording light is removed in v7 (architecture 17.30): the 4.0 mA of architecture 17.15 counted 1.5 mA for it, so without the light the computed recording figure is 4.1 - 1.5 = 2.6 mA [CALC] plus the always-lit red dot and timer of section 3.2, whose cost is a bench item on the new panel (architecture 17.30) with no number yet. The thresholds of 1.1 and the hours of this section stay computed at 4.1 mA, the figure of architecture 17.26, until that bench result and a restated architecture figure **[CHOICE]**; 4.1 mA no longer counts a light. It excludes the motor (section 3.1) and the screen. **Requirement P2 (10 hours of recording) is NOT met by this ring**: the owner chose thinness over hours on 2026-11-10 (architecture 17.5). In every state other than `RECORDING` the microphones are off.

### Change 30: old lines 861-861 -> new lines 867-867 (replace)

- OLD 861:   2. the screen goes off at once and stays off for 10 s **[CHOICE]**: the screen is the largest load on the chip's path (motor-drive.md section 4);
- NEW 867:   2. the screen goes off at once and stays off for 10 s, except in `RECORDING`, where it shows SCR_REC_DIM for those 10 s and never goes dark (rule R-SIGN, section 3.2) **[CHOICE]**: the screen is the largest load on the chip's path (motor-drive.md section 4);

### Change 31: old lines 898-898 -> new lines 904-904 (replace)

- OLD 898: | 0x41 | T-LIGHT | recording light | two 1 s test recordings 1 s apart (the light has no chip pin; it follows VDD_MIC) | jig light sensor: on, off, on, following VDD_MIC within 10 ms |
- NEW 904: | 0x41 | T-SIGN | recording sign on the screen (rule R-SIGN, section 3.2; replaces the light test, the light is removed in v7) | two 1 s test recordings 1 s apart; the ring reports the times VDD_MIC went on and off; the jig camera films the screen | in every camera frame between VDD_MIC on and VDD_MIC off the red dot is lit; no such frame shows a dark screen |

### Change 32: old lines 906-906 -> new lines 912-912 (replace)

- OLD 906: Sub-command 0x11 (the F2 skew test) is removed in F3: the ring answers BAD_ARG. T-LIGHT is the same test as in F2.
- NEW 912: Sub-command 0x11 (the F2 skew test) is removed in F3: the ring answers BAD_ARG. Sub-command 0x41 is T-SIGN: the light and its test are removed in v7 (architecture 17.30).

### Change 33: old lines 912-912 -> new lines 918-918 (replace)

- OLD 912: | 5 | board | SWD on test pads TP3 SWDCLK, TP4 SWDIO, TP5 NRESET; USB on the J_BAND_B lands; the jig feeds a battery voltage on the cell lands and 10 kilo-ohm on the thermistor land | write and read back MCUboot, the image and the settings with the factory flag 1; set the boot loader lock (section 9.2); GET_INFO; T-STORE, T-XTAL, T-RADIO, T-MIC1, T-MIC2, T-LIGHT, T-CHARGE (state only) | T-SCREEN, T-JOY, T-CENTRE, T-MOTOR: the screen, the switches and the motor are not joined yet. This is the last SWD access of the ring's life |
- NEW 918: | 5 | board | SWD on test pads TP3 SWDCLK, TP4 SWDIO, TP5 NRESET; USB on the J_BAND_B lands; the jig feeds a battery voltage on the cell lands and 10 kilo-ohm on the thermistor land | write and read back MCUboot, the image and the settings with the factory flag 1; set the boot loader lock (section 9.2); GET_INFO; T-STORE, T-XTAL, T-RADIO, T-MIC1, T-MIC2, T-CHARGE (state only) | T-SCREEN, T-SIGN, T-JOY, T-CENTRE, T-MOTOR: the screen, the switches and the motor are not joined yet. This is the last SWD access of the ring's life |

### Change 34: old lines 914-914 -> new lines 920-920 (replace)

- OLD 914: | 18 | open ring | USB through the pads; FACTORY ENTER | every test: T-SCREEN, T-JOY, T-CENTRE, T-MOTOR, T-MIC1, T-MIC2, T-LIGHT, T-STORE, T-RADIO, T-XTAL, T-CHARGE | |
- NEW 920: | 18 | open ring | USB through the pads; FACTORY ENTER | every test: T-SCREEN, T-JOY, T-CENTRE, T-MOTOR, T-MIC1, T-MIC2, T-SIGN, T-STORE, T-RADIO, T-XTAL, T-CHARGE | |

### Change 35: old lines 945-945 -> new lines 951-951 (replace)

- OLD 945: | Buttons, joystick | `gpio-keys` input driver | SRC 14 |
- NEW 951: | Joystick (five switches) | `gpio-keys` input driver | SRC 14 |

### Change 36: old lines 965-965 -> new lines 971-971 (replace)

- OLD 965: | W10 | Feedback | motor pattern player with the limits of section 3.1, the motor charge per pulse for the gauge (section 8.3), and the MOTOR edge times for section 4.7 (no light code: the light has no pin) |
- NEW 971: | W10 | Feedback | motor pattern player with the limits of section 3.1, the motor charge per pulse for the gauge (section 8.3), and the MOTOR edge times for section 4.7; the recording sign of section 3.2 with test SIGN-1 (no light code: the light is removed in v7) |

### Change 37: old lines 1029-1029 -> new lines 1035-1035 (replace)

- OLD 1029: 27. Whether the centre key of section 2.2 reads a centre press reliably on the real nub in both cases (bench item B6, architecture 16.5), whether the real switch SW2 fits under the nub's centre (architecture 17.11, 17.12), and whether the F4 values 30 ms release hold-off, 40 ms decision window in case `SW2`, MW at 500 ms and the 450 ms short-press ceiling suit a thumb at rest (all marked [CHOICE]).
- NEW 1035: 27. Whether the centre key of section 2.2 reads a centre press reliably on the real round cap in both cases (bench item B6, architecture 16.5), whether the real switch SW2 fits under the centre of the round cap (architecture 17.11, 17.12), and whether the F4 values 30 ms release hold-off, 40 ms decision window in case `SW2`, MW at 500 ms and the 450 ms short-press ceiling suit a thumb at rest (all marked [CHOICE]).

### Change 38: old lines 1041-1041 -> new lines 1047-1047 (replace)

- OLD 1041: Run: `design/.venv/bin/python -I design/firmware-check.py` (exit 0 = pass, 1 = a rule fails). It reads `design/architecture.md`, `design/ecad/ring/netlist.csv` and the Knowles datasheet copy `design/mech/mic-path/datasheets/knowles-spk0641ht4h-1_chipsmall.txt`. Kept from F2 to F4: sections 1 to 10 present; every state of a transition is in the state list, every listed state has a transition out and, except `SHIP` and `BOOT`, one in, and the number of transition rows equals the number stated under the table; every pin and signal name is in architecture section 7, no spare pin is used, and each signal-pin pair matches; the RAM lines sum to the total, at most 512 KB; the charge voltage equals the cell's type in architecture section 2; each PDM clock line divides 32 MHz by a whole prescaler of 4 to 126, uses a ratio of the chip and gives 16,000 or 8,000 Hz; 64-byte bulk packets at full speed (6.1); the motor marking rule (4.7); the schematic rules for the microphone clock (4.5), the storage lines (5.1) and the screen sequence (3.3); thermistor value and ordered limits (8.1); none of the removed names outside the change lists; VDD_MIC on in exactly one state (1.1) and one power-table row (8.2), the recording state; only a long press starts or stops a recording, a short or double press never changes state, and no direction, button or other event touches the recording state; the gesture, centre-source, warning-pulse, hold-off and collision rules of F4; the audio format and chunk arithmetic; one PDM instance; the joystick switches against architecture 17.3 and the 40 ms rule against 16.5; unused pins only on lines that say unused; four pads in order; every row into `CHARGING` and both ship-exit rows say "charge on", `charging-enable` is on whenever VBUS is present, R-CHG stated; section 8.6 states VBUS is an input only; `questions_for_owner` and the RESULT line. Changed in F5 (each replaces an F4 check that asserted what F5 changes): the header says Version F5, follows A5 sections 17.11 to 17.23 and has the list "Changes from F4 to F5" with 8 items; the removed-name rule runs from that list to "How to read this" and now also bans the older power chip's name, the F3 battery range, the old microphone and datasheet names and the discharge-limit property; `CHARGE_CURRENT` is 15,000 µA in `current-microamp`, a multiple of 500 inside 4,000 to 100,000 and at most 1 C of the smallest cell of architecture 17.17, and T-CHARGE has a pass limit (in F4 both were BLOCKED on S12); the microphone mode range is read from the Knowles datasheet copy (F4 used fixed numbers of the older part), the microphone part name is in 4.1 and 8.5, and the gain is 0 dB, the register 0x28 (2 x 0 + 0x28), the header `gain_code` equal to it, and the stored full scale (94 dB SPL minus the sensitivity read from the Knowles copy) equal to the acoustic overload point read from the same copy; section 3.1 names U11, MOT_EN, VMOT and the 0.55 ms delay and never Q1, and architecture 17.22 names U11 (F4 checked Q1 and full duty on VDD_3V0); the battery minutes of 1.1 and the hours of 8.5 are recomputed from the smallest and largest cells of architecture 17.17 and the recording current 4.0 + 2 x (0.63 - 0.58) mA (F4 checked a single range against architecture 17.10); the ship section 8.4 names TASKENTERSHIPMODE, the VBUS removal and EVENTVBUSREMOVED and no timed hibernate; SHIP_SAMPLE keeps the factory flag in 9.3 and in 1.2; section 7 starts with the protocol sentence. New in F5: every "SIGNAL Pn.nn" pair and every chip pin of firmware.md is checked against the U1 rows of `netlist.csv`, and the power chip, microphone and motor nets this file names (GPIO0 on PMIC_INT, LSOUT1 on VDD_MIC, LSOUT2 on VDD_SD, U5 and U6 SELECT, U11 EN, OUT and IN, R61 and R62) against their netlist rows. Changed in F6: the cells per size are read from the measured table of architecture 17.26 (no longer 17.17); the compile limit of 8.1 must equal 1 C of the smallest cell, 17,600 µA; the header says Version F6 with sections 17.11 to 17.26 and the list "Changes from F5 to F6" has 4 items; and no line outside the change lists may name a value of the calculated cells (18.2, 24.3 or 32.9 mAh, or 18,200 µA) unless the word "before" stands within 60 characters of it. Rules it cannot check (timing values, protocol layouts, the meaning of text) are checked by review.
- NEW 1047: Run: `design/.venv/bin/python -I design/firmware-check.py` (exit 0 = pass, 1 = a rule fails). It reads `design/architecture.md`, `design/ecad/ring/netlist.csv` and the Knowles datasheet copy `design/mech/mic-path/datasheets/knowles-spk0641ht4h-1_chipsmall.txt`. Kept from F2 to F4: sections 1 to 10 present; every state of a transition is in the state list, every listed state has a transition out and, except `SHIP` and `BOOT`, one in, and the number of transition rows equals the number stated under the table; every pin and signal name is in architecture section 7, no spare pin is used, and each signal-pin pair matches; the RAM lines sum to the total, at most 512 KB; the charge voltage equals the cell's type in architecture section 2; each PDM clock line divides 32 MHz by a whole prescaler of 4 to 126, uses a ratio of the chip and gives 16,000 or 8,000 Hz; 64-byte bulk packets at full speed (6.1); the motor marking rule (4.7); the schematic rules for the microphone clock (4.5), the storage lines (5.1) and the screen sequence (3.3); thermistor value and ordered limits (8.1); none of the removed names outside the change lists; VDD_MIC on in exactly one state (1.1) and one power-table row (8.2), the recording state; only a long press starts or stops a recording, a short or double press never changes state, and no direction, button or other event touches the recording state; the gesture, centre-source, warning-pulse, hold-off and collision rules of F4; the audio format and chunk arithmetic; one PDM instance; the joystick switches against architecture 17.3 and the 40 ms rule against 16.5; unused pins only on lines that say unused; four pads in order; every row into `CHARGING` and both ship-exit rows say "charge on", `charging-enable` is on whenever VBUS is present, R-CHG stated; section 8.6 states VBUS is an input only; `questions_for_owner` and the RESULT line. Changed in F5 (each replaces an F4 check that asserted what F5 changes): the header says Version F5, follows A5 sections 17.11 to 17.23 and has the list "Changes from F4 to F5" with 8 items; the removed-name rule runs from that list to "How to read this" and now also bans the older power chip's name, the F3 battery range, the old microphone and datasheet names and the discharge-limit property; `CHARGE_CURRENT` is 15,000 µA in `current-microamp`, a multiple of 500 inside 4,000 to 100,000 and at most 1 C of the smallest cell of architecture 17.17, and T-CHARGE has a pass limit (in F4 both were BLOCKED on S12); the microphone mode range is read from the Knowles datasheet copy (F4 used fixed numbers of the older part), the microphone part name is in 4.1 and 8.5, and the gain is 0 dB, the register 0x28 (2 x 0 + 0x28), the header `gain_code` equal to it, and the stored full scale (94 dB SPL minus the sensitivity read from the Knowles copy) equal to the acoustic overload point read from the same copy; section 3.1 names U11, MOT_EN, VMOT and the 0.55 ms delay and never Q1, and architecture 17.22 names U11 (F4 checked Q1 and full duty on VDD_3V0); the battery minutes of 1.1 and the hours of 8.5 are recomputed from the smallest and largest cells of architecture 17.17 and the recording current 4.0 + 2 x (0.63 - 0.58) mA (F4 checked a single range against architecture 17.10); the ship section 8.4 names TASKENTERSHIPMODE, the VBUS removal and EVENTVBUSREMOVED and no timed hibernate; SHIP_SAMPLE keeps the factory flag in 9.3 and in 1.2; section 7 starts with the protocol sentence. New in F5: every "SIGNAL Pn.nn" pair and every chip pin of firmware.md is checked against the U1 rows of `netlist.csv`, and the power chip, microphone and motor nets this file names (GPIO0 on PMIC_INT, LSOUT1 on VDD_MIC, LSOUT2 on VDD_SD, U5 and U6 SELECT, U11 EN, OUT and IN, R61 and R62) against their netlist rows. Changed in F6: the cells per size are read from the measured table of architecture 17.26 (no longer 17.17); the compile limit of 8.1 must equal 1 C of the smallest cell, 17,600 µA; the header says Version F6 with sections 17.11 to 17.26 and the list "Changes from F5 to F6" has 4 items; and no line outside the change lists may name a value of the calculated cells (18.2, 24.3 or 32.9 mAh, or 18,200 µA) unless the word "before" stands within 60 characters of it. Changed in v7 (architecture 17.29 and 17.30): the netlist fact "Q2 whose gate is VDD_MIC" is no longer required; any line naming LED1, R41, Q2, LG1, LP1, T-LIGHT, "recording light", "light window", "hard-wired", "record button" or "nub" fails unless it says "removed in v7"; section 3.2 must state rule R-SIGN (never dark, red dot and timer, dimmed after 3 s, full picture on any input, the one function `rec_mics_on()`, test SIGN-1, the dot's cost a bench item); the `RECORDING` screen cell of 1.1 must say never dark and its 8.2 row must keep the screen on; 4.5 must enable VDD_MIC only after the sign is drawn; the refusal row "recording sign not drawn" must stay in `STANDBY`; 9.3 must hold T-SIGN and no T-LIGHT row; 8.5 must not count a light and must name the dot's cost as a bench item; the centre switch is written "centre switch SW2 (net BTN_REC)"; the 2.2 heading names the round joystick with five switches. Rules it cannot check (timing values, protocol layouts, the meaning of text) are checked by review.

### Change 39: old lines 1051-1052 -> new lines 1057-1058 (replace)

- OLD 1051: | H3 | F1: the light follows VDD_MIC and was on all day in a state the owner has now removed. | closed: VDD_MIC is on only while audio is stored, so the light is on exactly then | none | none |
- OLD 1052: | H4 | F1: the light circuit of architecture sections 7 and 9 contradicted itself. | closed by architecture A2: no chip pin touches the light | no light code | none |
- NEW 1057: | H3 | F1: the light follows VDD_MIC and was on all day in a state the owner has now removed. | closed: VDD_MIC is on only while audio is stored, so the light is on exactly then; [v7: removed in v7 (architecture 17.30): the recording light, LED1, R41, Q2, the light guide LG1, the light pipe LP1 and the light window are out; the recording sign is the screen, section 3.2] | none | none |
- NEW 1058: | H4 | F1: the light circuit of architecture sections 7 and 9 contradicted itself. | closed by architecture A2: no chip pin touches the light; [v7: removed in v7 (architecture 17.30): the recording light, LED1, R41, Q2, the light guide LG1, the light pipe LP1 and the light window are out; the recording sign is the screen, section 3.2] | no light code | none |

### Change 40: old lines 1063-1063 -> new lines 1069-1069 (replace)

- OLD 1063: | H15 | Architecture section 9 (first two bullets), 16.5 (the line on the record button), 17.3 (the table row for the record button and the line "SW2 = record button") and 17.8 still describe a separate record button and a joystick that never starts a recording; 17.11 removes the button and puts the record gesture on the centre press. | open | F4 and F5 follow 17.11 (later sections win); BTN_REC is the centre switch in case `SW2` | architecture owner: rewrite those lines |
- NEW 1069: | H15 | Architecture section 9 (first two bullets), 16.5 (the line on the record button), 17.3 (the table row for the record button and the line "SW2 = record button") and 17.8 still describe a separate record button and a joystick that never starts a recording; 17.11 removes the button and puts the record gesture on the centre press. [v7: the record button is gone since 17.11 and the rectangular nub is removed in v7; the one control is the round joystick (architecture 17.29), centre switch SW2 (net BTN_REC)] | open | F4 and F5 follow 17.11 (later sections win); BTN_REC is the centre switch in case `SW2` | architecture owner: rewrite those lines |

