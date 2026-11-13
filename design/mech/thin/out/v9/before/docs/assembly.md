# Assembly procedure of the ring (review findings F10 and F11)

Basis: first written on design commit a0cf952 (2026-11-11, 00:50 to 01:00); brought to the inside model v6 and architecture 17.22 to 17.26 on the working tree at commit 6ccb258 or later (2026-11-11, from 05:38), what changed then is in `design/mfg/assembly/v6-update-notes.md`; brought to design version 7 on 2026-11-11 (architecture 17.29 and 17.30: round joystick, cap CAP1 and round frame FRM1, gloss black finish; the recording light and its parts are removed in v7), what changed is in `design/mfg/assembly/v7-update-notes.md`. Step numbers are unchanged since the first issue, so other files that cite a step stay right. Each citation of a file and line below is re-read by `check_assembly.py`, which prints the cited line; each citation of `design/firmware.md` is by section number and name (no line number, the file grows), and `check_assembly.py` checks that the cited section holds the cited name.

Who this is for: the owner or a partner who builds the ring. Read sections 1 and 2 in order. Section 3 lists the places where the design, as written today, makes an order impossible or forces an irreversible step before a test. Section 4 answers F11 (water and dust). Section 5 says who must still decide each open material. Section 6 lists changes other files need.

## 0. Words used here

- BLOCK: the flat top part of the ring that holds the screen. BAND: the hoop round the finger. SHOULDER: where the band flows into the block (`design/architecture.md:415`).
- BODY (HSG1): the one metal part that is both block and band (`design/architecture.md:420`).
- CHANNEL: the open groove inside the band, 6.8 mm wide, open toward the finger (`design/architecture.md:440`).
- LINER (LNR1): the 0.3 mm resin skin cast into the channel. It closes the channel and touches the finger (`design/architecture.md:440`).
- RIBBON: a thin flexible circuit (FLEX1, FLEX2) that carries wires from the main board into the band (`design/architecture.md:441`).
- HARNESS: in this file, a ribbon with its band parts already soldered on (a word of this file, not of the design).
- REFLOW: soldering in an oven, where printed solder paste melts under every part at once.
- SWD: the two-wire programming port of the main chip (SWDCLK, SWDIO), reached through test pads (`design/architecture.md:291`).
- SHIP MODE: a state of the power chip in which the battery is cut off from everything and the ring draws almost nothing until it is woken (`design/datasheets/npm1304_datasheet_v1_0.txt:9059`).
- JIG: a holding fixture with spring pins that touch pads and connect a test computer.
- [PROPOSED]: this file proposes the process because no design file names one. The reason follows the tag. A proposal is not a design decision.
- [CALC]: a figure worked here from sourced numbers; the working is in the text.
- Face names on the main board: the UNDER face carries all parts and faces the block floor; the TOP face is bare and faces the screen (`design/ecad/ring/pcb/board-notes.md:53`, `design/mfg/specs/main-board.md:6`).

State of the files today (2026-11-12). The inside model v7 (no light parts, round joystick) is measured: its fit check ends `RESULT PASS` at every ring size US 7 to 13, 1080 pairs and 47 parts on US 7, 8 and 9 and 1034 pairs and 46 parts on US 10 to 13 (logs `design/mech/thin/out/v7/lead/us7.log` to `design/mech/thin/out/v7/lead/us13.log`; section "Model v7" at `design/mech/thin/thin-notes.md:430`; architecture 17.31). The maker files in `design/mfg/parts/` are exported from that model v7 (`design/mfg/parts/index.csv`; `design/mech/thin/out/v7-export/check_parts_v7.log` ends `RESULT PASS files=88`). The exterior of v7 is merged32h (`design/look/s1/merged32h-report.md:70`). The specs in `design/mfg/specs/` are brought to v7 (`design/mfg/specs/joystick-nub.md:1`). This file follows architecture 17.11 to 17.31 wherever an older file differs, and says so at each step.

Ring sizes: version 1 has 7 sizes, US 7 to 13. Each size has its own body, liner, cell length and ribbon lengths; the block, board, glass, cap CAP1 and frame FRM1 are the same at every size (`design/architecture.md:610`, `design/mech/thin/thin-notes.md:245`). Several angles and depths in the band change by size: see the table "What changes by ring size at assembly" below. Where a step gives a US 9 figure, the table gives the figure of the other sizes.

### What changes by ring size at assembly

From the model v6 (`design/architecture.md:783` to `design/architecture.md:789`, `design/architecture.md:794`; `design/mech/thin/thin-notes.md:275` to `design/mech/thin/thin-notes.md:281`). The block's contents (board, screen, glass, seal, microphones) are the same at every size (`design/mech/thin/thin-notes.md:245`).

| Size | Joystick angle | Motor angle | Protection circuit starts at | Floor slot bottom Z | Joystick pocket roof radius | Cell from / to | Cell length on its centre line |
|---|---|---|---|---|---|---|---|
| US 7 | -84.0 deg | -47.0 deg | 43.8 deg | -0.20 | 10.0898 | +53.78 to -106.994 deg | 33.936 mm |
| US 8 | -81.0 | -45.5 | 41.5 | -0.20 | 10.4962 | +51.081 to -102.943 | 36.547 mm |
| US 9 | -78.0 | -44.0 | 39.5 | -0.23 | 10.9026 | +48.713 to -98.986 | 39.175 mm |
| US 10 | -78.0 | -45.0 | 39.5 | -0.63 | 11.3090 | +48.372 to -98.111 | 40.914 mm |
| US 11 | -78.0 | -43.5 | 39.5 | -1.04 | 11.7154 | +48.055 to -97.308 | 42.651 mm |
| US 12 | -78.0 | -42.5 | 39.5 | -1.45 | 12.1218 | +47.76 to -96.567 | 44.387 mm |
| US 13 | -78.0 | -42.5 | 39.5 | -1.85 | 12.5282 | +47.485 to -95.883 | 46.121 mm |

Pad angles: the four pads stay 2.4 mm apart along the arc at every size, so their angles change with the bore: pitch angle = 2.4 / (bore / 2) (`design/mech/thin/thin-notes.md:75`); the pads stay where they are against the block (`design/architecture.md:754`).

Steps this table touches: step 6 (ribbon FLEX1 length to the joystick head), step 7 (motor lead length to its pocket), step 8 (pad angles on FLEX2), step 9 (cell length and the protection circuit's start), step 10 (body per size: joystick opening and pocket, motor pocket, floor slot depth), step 13 (frame FRM1 and cap CAP1 at the joystick angle), step 14 (positions in the fixture), step 19 (slot depth to fill), step 20 (dam at the joystick angle), step 21 (mould core per size), step 26 (charge time per cell).

## 1. Parts and sub-assemblies that enter the ring

Order of the table: where the part ends up, from the top of the block to the finger. "Step" is the first step of section 2 that handles it.

| Part | Ref | What it is | Source of its size and place | Step |
|---|---|---|---|---|
| Cover glass `cover_glass` | GL1 | formed glass, 1.10 mm at the centre, rolls into the metal, black print outside the lit area with no opening (v7) | `design/architecture.md:490`, `design/mech/thin/placement.csv:27`, `design/mfg/specs/cover-glass.md:6` | 23 |
| Clear adhesive `clear_adhesive` | ADH1 | 0.10 mm optically clear adhesive, glass to screen over the whole face (17.30) | `design/architecture.md:426`, `design/mech/thin/placement.csv:26` | 23 |
| Screen `screen`, `screen_tail` | DISP1 | 0.95 inch AMOLED with a folded tail into J1 | `design/mech/thin/placement.csv:24`, `design/mech/thin/placement.csv:25` | 15 |
| Foam frame `foam` | FOAM1 | 0.10 mm foam frame, 1.2 mm wide, closed all round (v7) | `design/mech/thin/placement.csv:23`, `design/bom.csv:57` | 15 |
| Main board `main_board` | PCB1 | 27.2 x 12.6 x 0.3 mm, 6 layers, parts on the under face only | `design/mech/thin/placement.csv:22`, `design/mfg/specs/main-board.md:6` | 1 |
| Board parts | all refs of step 2 | chips, passives, microphones, connector, antenna, test pads | `design/bom.csv` | 2 |
| Motor regulator `motor_regulator` and its capacitors `motor_cap_in`, `motor_cap_out` | U11, C83, C84 | 3.0 V regulator from the cell for the motor, 10 uF in and out, under the board beside the +Y floor slot | `design/architecture.md:705`, `design/mech/thin/placement.csv:19` to `design/mech/thin/placement.csv:21`, `design/bom.csv:45`, `design/bom.csv:46` | 2 |
| Power chip capacitors | C85, C86, C87, C88 | VBAT 2.2 uF, two load switch outputs 1.0 uF, a third VSYS 10 uF | `design/bom.csv:67` to `design/bom.csv:69` | 2 |
| Microphone gaskets | GSK2, GSK3 | foam rings OD 1.8, bore 1.0, three thicknesses | `design/architecture.md:656`, `design/mech/mic-path/mic-path.md:70`, `design/bom.csv:59`, `design/mech/thin/placement.csv:12` | 12 |
| Microphone membranes | MEM1, MEM2 | discs 2.0 mm, at most 0.10 thick, in the underside seats | `design/mech/mic-path/mic-path.md:74`, `design/bom.csv:58`, `design/mech/thin/placement.csv:13` | 11 |
| Body `outer_body` | HSG1 | one metal body per size, with all cavities | `design/bom.csv:51`, `design/mech/thin/placement.csv:28` | 10 |
| Radio corner (only if the owner adopts it) | RC1 | resin corner of the body round the antenna | `design/architecture.md:674`, `design/architecture.md:676` | 10 |
| Joystick frame | FRM1 | round titanium ring, 5.40 outer diameter, 4.80 bore, 1.30 long, coated gloss black with the body, bonded in the round 5.60 opening with DP420 Black | `design/architecture.md:826`, `design/bom.csv:82`, `design/mfg/specs/joystick-nub.md:1` | 13 |
| Joystick cap `joystick_cap` | CAP1 | round moulded cap, shank 4.40, rim 1.400 above the frame top, ridged dish top, flange 6.90 along the finger x 6.40 x 0.40 (Makrolon 2407, colour 901510) | `design/architecture.md:826`, `design/bom.csv:81`, `design/mech/thin/thin-notes.md:249`, `design/mech/thin/placement.csv:34` | 13 |
| Joystick dam `joystick_dam` | DAM1 | UV-cured dam frame round the switch head, keeps the cast resin out of the switches | `design/bom.csv:55`, `design/mech/thin/placement.csv:39`, `design/mech/thin/thin-notes.md:251` | 20 |
| Joystick switches `joy_sw_*` | SW1, SW2, SW3, SW4, SW5 | five Alps SKTAAAE010, cross at 2.4 mm; SW2 is the centre press | `design/architecture.md:588`, `design/mech/thin/placement.csv:34` to `design/mech/thin/placement.csv:38` | 6 |
| Vibration motor `vibration_motor` | M1 | Jinlong W0525AB001D, 5.0 x 2.5 mm, two lead wires | `design/architecture.md:597`, `design/mech/thin/placement.csv:40` | 7 |
| Cell `cell` | BT1 | curved cell 1.6 x 6.0 mm, 39.175 mm at US 9, 33.936 to 46.121 mm over US 7 to 13 | `design/architecture.md:783` to `design/architecture.md:789`, `design/mech/thin/placement.csv:41` | 9 |
| Cell protection circuit `cell_protection` | PRT1 | 1.5 x 5 mm board on the cell tab, with the temperature sensor | `design/bom.csv:48`, `design/mech/thin/placement.csv:42` | 9 |
| Cell temperature sensor | RT1 | 10 k thermistor; on the cell (17.3) or on the board (W13): the owner decides | `design/bom.csv:74` | 9 |
| Ribbon, joystick side `band_flex_thumb` | FLEX1 | 1.4 mm wide, 8 lines, flat head 6.4 x 6.4 x 0.15 under the switches on a 6.4 x 6.4 x 0.075 stiffener (model v6, `design/mech/thin/thin-notes.md:250`) | `design/bom.csv:78`, `design/mech/thin/placement.csv:47`, `design/mech/thin/thin-notes.md:69` | 6 |
| Ribbon, other side `band_flex_away` | FLEX2 | 1.4 mm wide, 7 lines, to the cell and the pads | `design/bom.csv:79`, `design/mech/thin/placement.csv:48`, `design/mech/thin/thin-notes.md:69` | 8 |
| Charging pads `pad_VBUS`, `pad_D-`, `pad_D+`, `pad_GND` | CP1, CP2, CP3, CP4 | gold discs 1.6 mm on the inside face, in the liner, order VBUS, D-, D+, GND | `design/architecture.md:590`, `design/mech/thin/placement.csv:43` to `design/mech/thin/placement.csv:46` | 8 |
| Liner `band_liner` | LNR1 | 0.3 mm cast resin skin | `design/bom.csv:80`, `design/mech/thin/placement.csv:31` | 21 |
| Glass seal `glass_seal` | SEAL1 | die-cut seal ring 0.05 mm thick in the body's glass seat, lowered 0.05 mm; tape not chosen | `design/bom.csv:54`, `design/mech/thin/placement.csv:29`, `design/mech/thin/thin-notes.md:136` | 23 |
| Floor slot sealant | none | no part number and no part in the model; the need is open item S26 | `design/architecture.md:524` | 19 |

Not used: the record cap CAP2 and its opening (removed, `design/architecture.md:546`); the wall microphone slots (removed, `design/architecture.md:657`); the recording light with LED1, R41, Q2, the light guide LG1 and the light plug LP1, the print window and the board hole, all removed in v7 (`design/architecture.md:834`); the rectangular joystick nub and frame, removed in v7 (`design/architecture.md:826`).

## 2. Assembly order

Every step has five fields: Join (what is joined to what, with which material or process), Locate (the face or feature that sets the position), Before (what must be true first), Check (what proves the step), After (what cannot be undone once the step is done). Steps 1 to 5 are the board, 6 to 9 the band harness, 10 to 13 the body, 14 to 18 the joining and the open test, 19 to 23 the closing, 24 to 28 the closed ring.

Steps that change if the owner adopts the resin radio corner (`design/architecture.md:674`) carry a line "Radio corner:". The procedure is written for the one-piece metal body, which stays the design until the owner decides (`design/architecture.md:676`).

### Step 1. Accept the bare main board

- **Join:** nothing is joined. The bare board PCB1 (`main_board`) is accepted from the board maker.
- **Locate:** the outline 27.2 x 12.6 mm and the antenna notch 1.8 x 3.6 (`design/mfg/specs/main-board.md:27`, `design/mfg/specs/main-board.md:31`).
- **Before:** the board files exist. Today they do not: no track is drawn (`design/architecture.md:512`, open item S14), and the board file lacks U10, C81, C82 (`design/architecture.md:575`). This step cannot start until S14 is closed.
- **Check:** the board maker's electrical test of every net, thickness, warp (`design/mfg/specs/main-board.md:45`); no hole through the board (`design/mfg/specs/main-board.md:34`; the light guide hole is removed in v7).
- **After:** nothing irreversible.

### Step 2. Print paste, place every board part, reflow (one side)

- **Join:** every board part of `design/bom.csv` to the under face of PCB1, with solder paste and one reflow. The parts: U1 (`main_chip`), U2 (`power_chip`, nPM1304, `design/architecture.md:566`), R71, R72, U3 (`storage`), U10, U4 (`screen_supply_chip`), U5 (`mic_1`) and U6 (`mic_2`), Knowles SPK0641HT4H-1 (`design/architecture.md:654`, `design/bom.csv:9`), J1 (`screen_connector`), ANT1 (`antenna`), L2, L3, L4, C3, C12, X1 (`crystal_32M`), X2 (`crystal_32k`), L1, FB1, R1, R2, C1, C2, C5, C4, C6, C7, C10, C14, C11, L10 (`screen_supply_coil`), C21, C26, C27, C24, C25, C23, C22, C28, C29, C31, C32, C35, C36, R31, R32, R57, R58, R60, C60, U11 (`motor_regulator`, TLV75530PDQNR, at X 0.0, Y 4.2), C83 (`motor_cap_in`, X 0.0, Y 5.45), C84 (`motor_cap_out`, X 1.2, Y 5.0) (`design/architecture.md:705`, `design/mech/thin/placement.csv:19` to `design/mech/thin/placement.csv:21`; the places are the model's proposal until the board layout confirms them, `design/architecture.md:760`), U9, R61 and R62 (now on U11's enable pin, `design/architecture.md:705`), R66, R63, R64, R65, C61, C72, C80, C81, C82, C71, C73, C74, C75, C78, C79, C76, C77, C85, C86, C87, C88 (`design/bom.csv:67` to `design/bom.csv:69`), L71 (`power_coil_1`), L72 (`power_coil_2`). The motor switch and the motor diode of earlier versions are not fitted: they left the design (`design/architecture.md:705`). LED1, R41 and Q2 are removed in v7 and are not fitted (`design/architecture.md:834`). The test pads TP1 to TP22 (TP1, TP2, TP3, TP4, TP5, TP6, TP7, TP8, TP9, TP10, TP11, TP12, TP13, TP14, TP15, TP16, TP17, TP18, TP19, TP20, TP21, TP22) and the ribbon lands J_BAND_A and J_BAND_B are copper on the same face and get no paste [PROPOSED: reason, a solder bump on a test pad or a hot-bar land spoils the spring-pin contact and the hot-bar joint of step 16]. C13 is not mounted (`design/bom.csv:18`).
- **Locate:** fiducials of the board file; each part's land pattern (from S14).
- **Before:** step 1 passed. The antenna mount is decided: as drawn, ANT1 stands in the corner notch and its pads are off the board, so it cannot be soldered (`design/architecture.md:513`, open item S15).
- **Check:** X-ray of U1 (61 balls), U2, U4 and the U3 lands; optical inspection of every other part.
- **After:** reflow is not undone; a part can be reworked by hand until step 17.

### Step 3. Measure the microphone heights and choose the gaskets

- **Join:** nothing is joined. The height of each microphone lid below the board's under face is measured, and one of three gasket thicknesses is chosen per microphone (`design/mech/mic-path/mic-path.md:152`).
- **Locate:** the board's under face as zero; the lid of U5 and of U6.
- **Before:** step 2 passed.
- **Check:** the gap g = lid Z - 0.300; gasket 0.10 if g is under 0.07, 0.20 if g is 0.07 to 0.14, 0.30 if g is over 0.14 (`design/mech/mic-path/mic-path.md:152`, all three an [ESTIMATE] of that study). Record g and the choice against the board's serial number.
- **After:** nothing irreversible.

### Step 4. Clean and inspect the under face before the jig

- **Join:** nothing is joined. The under face of PCB1 is cleaned of flux residue round the test pads TP1 to TP22 and the ribbon lands J_BAND_A and J_BAND_B, then dried [PROPOSED: reason, the spring pins of step 5 and the hot-bar joints of step 16 need bare copper; the paste and flux of step 2 are not named by any file]. History: this step fitted the light guide LG1 until v6; the light guide is removed in v7 (`design/architecture.md:834`).
- **Locate:** the board on its outline in a cleaning carrier.
- **Before:** steps 2 and 3 passed.
- **Check:** under a microscope at 10 times, no residue on any test pad or ribbon land [PROPOSED]; the gasket choice of step 3 is still recorded against the board's serial number.
- **After:** nothing irreversible.

### Step 5. Program and test the board through its test pads (the only SWD access in the ring's life)

- **Join:** nothing is joined. A jig touches the under face. SWD: TP3 SWDCLK, TP4 SWDIO, TP5 NRESET, TP17 VDD_1V8, TP18 GND; log: TP1 DBG_TX, TP2 DBG_RX (`design/ecad/ring/sch-notes.md:44`, `design/architecture.md:291`). Power: the jig feeds a battery voltage on the J_BAND_B cell lands and a 10 k resistor on its thermistor land [PROPOSED: reason, the cell is not yet on the board and the power chip needs a battery and a thermistor reading], and VBUS, D-, D+, GND on the J_BAND_B pad lands, which are the USB lines of the four charging pads (`design/bom.csv:77`).
- **Locate:** the jig's pins on the test pads; the board sits on its outline.
- **Before:** step 4 passed. The signed image exists: MCUboot, the application, and the settings area with the factory flag at 1 (`design/firmware.md section 9.2, name MCUboot`, `design/firmware.md section 9.3, name factory flag`).
- **Check:** SWD write and read-back of MCUboot and the image; then over USB: GET_INFO gives the firmware version and the factory flag 1 (`design/firmware.md section 6.3, name GET_INFO`); the board-level factory tests T-STORE, T-XTAL, T-RADIO, T-CHARGE (`design/firmware.md section 9.3, name T-STORE`, `design/firmware.md section 9.3, name Factory flow`). T-SCREEN, T-SIGN, T-JOY, T-CENTRE and T-MOTOR wait for step 18; T-MIC1 and T-MIC2 are not run here, because a microphone gets power only after the screen shows the recording sign and no screen is joined at step 5; they run first at step 18 (`design/firmware.md section 9.3, ruling R18`; `design/firmware.md section 9.3, name Factory flow`).
- **After:** this is the last moment the SWD pads can be reached. They lie on the under face, which faces the block floor 0.05 mm away once the board is in the body (`design/architecture.md:426`). After step 17 the only way into the chip is USB through the charging pads; a broken boot loader after step 17 means a scrapped ring (conflict K-A1).

### Step 6. Solder the five joystick switches on the ribbon FLEX1

- **Join:** SW1 (up), SW3 (down), SW4 (toward the hand), SW5 (toward the fingertip) and SW2 (centre) to the head of FLEX1 (`band_flex_thumb`), with solder paste and reflow on a flat carrier [PROPOSED: reason, the head stays flat in the ring]. In model v6 the head is flat, 6.4 x 6.4 x 0.15, and lies on a flat stiffener of 6.4 x 6.4 x 0.075 mm under it, drawn as part of the ribbon (`design/mech/thin/thin-notes.md:250`, `design/architecture.md:795`); the flex maker bonds the stiffener to the head before this step [PROPOSED: reason, the stiffener holds the head flat during reflow; its material, stainless or polyimide, is the flex maker's, `design/mech/thin/thin-notes.md:250`].
- **Locate:** the cross at 2.4 mm from the cap axis, SW2 at the centre, 0.30 mm to its neighbours (`design/architecture.md:588`, `design/mech/thin/thin-notes.md:73`).
- **Before:** FLEX1 is made with its stiffener, in the length of its ring size (the joystick angle changes by size: table above). Today no outline exists (`design/bom.csv:78`; `design/mfg/specs/band-flex-tails.md:62`). The switch land pattern is open (S9, `design/bom.csv:39`).
- **Check:** each switch closes its own line and no other, measured with an ohmmeter on the ribbon's board end while pressing it; height 0.53 mm; every switch base flat on the head (the model gives 0.0000 mm, `design/mech/thin/thin-notes.md:250`), checked with a feeler of 0.02 mm [PROPOSED].
- **After:** nothing irreversible; a switch can be reworked until step 14.

### Step 7. Solder the motor's lead wires to FLEX1

- **Join:** M1 (`vibration_motor`, Jinlong W0525AB001D) to FLEX1, red lead to the + pad, blue to the - pad, by hand soldering (`design/architecture.md:597`, `design/architecture.md:605`).
- **Locate:** the motor pads of FLEX1 beside the motor's place, 0.7 mm off the band's centre line at the motor angle of the ring size: -44.0 degrees at US 9, -47.0 at US 7, -42.5 at US 13 (motor angles US 7 to 13: -47.0, -45.5, -44.0, -45.0, -43.5, -42.5, -42.5; `design/mech/thin/thin-notes.md` model v6.1 and v6.2; `design/architecture.md:783` to `design/architecture.md:789`; table above); the lead length as delivered is open (S10).
- **Before:** step 6 passed. The lead length is known (S10) so the lead can be cut to fit the pocket [PROPOSED: cut to the length the v6 model gives for the size; reason, a loose loop has no room in the channel, `design/mech/thin/thin-notes.md:69`].
- **Check:** apply 3.0 V through a 200 mA current limit to the ribbon's motor lines for 0.5 s: the motor vibrates [PROPOSED: reason, the motor has its own drive chip, rated 3.0 V, start under 175 mA, `design/architecture.md:598`]. In the ring the same lines carry VMOT from U11, red lead on VMOT (`design/architecture.md:705`, `design/bom.csv:44`).
- **After:** cut leads cannot be lengthened.

### Step 8. Make the charging pads on FLEX2

- **Join:** CP1 (`pad_VBUS`), CP2 (`pad_D-`), CP3 (`pad_D+`), CP4 (`pad_GND`) to the four pad lands of FLEX2 (`band_flex_away`). How the pad is made is open (`design/bom.csv:61`: "pad part or plating"). [PROPOSED default: the land itself is the pad, with thick hard gold; reason, a soldered disc adds a joint that sweat reaches through the liner edge.] The disc of the model is 1.6 mm, 0.07 thick, flush with the liner's inner face (`design/mech/thin/placement.csv:43`).
- **Locate:** four pads 2.4 mm apart along the arc, centred opposite the block, the row at X = -1.0 mm (toward the hand end of the block, ring -X; the case pins stand at X = -1.0, so a ring turned over in the case has its pads 2.0 mm from the pins and VBUS never meets GND; architecture 17.28; model v6.3), at 158.23, 172.74, 187.26 and 201.77 degrees at US 9, order VBUS, D-, D+, GND with rising angle (`design/mech/thin/thin-notes.md:75`); the pitch angle per size is 2.4 / (bore / 2) (table above).
- **Before:** FLEX2 is made (no outline exists today, `design/bom.csv:79`).
- **Check:** continuity from each pad to its land at the ribbon's board end; no short between pads.
- **After:** nothing irreversible.

### Step 9. Join the cell, its protection circuit and the thermistor to FLEX2

- **Join:** the output tabs of PRT1 (`cell_protection`, delivered on the cell's tab by the cell maker, `design/bom.csv:48`) to the cell lands of FLEX2, and RT1 to its land, by hand soldering at low heat [PROPOSED: reason, the joint is 0.2 mm from the cell, `design/mech/thin/thin-notes.md:67`; the cell maker states the limit, S12].
- **Locate:** at US 9 the cell's tab end lies at +48.713 degrees and PRT1 starts at +39.5 degrees, 0.2 mm before the cell (`design/mech/thin/thin-notes.md:264`, `design/mech/thin/thin-notes.md:67`). Per size the cell's ends and PRT1's start change: PRT1 starts at 43.8 degrees on US 7 and 41.5 on US 8 (`design/architecture.md:794`; table above).
- **Before:** the cell BT1 (`cell`) of the right size is delivered, 33.936 mm (US 7) to 46.121 mm (US 13) on its centre line (`design/architecture.md:783`, `design/architecture.md:789`; custom, S12, `design/architecture.md:508`). Its open-circuit voltage is measured. The protection limits are known from the cell maker (`design/bom.csv:48`).
- **Check:** the cell voltage appears on the two cell lands at the ribbon's board end; RT1 reads about 10 k at room temperature (`design/bom.csv:74`).
- **After:** from here the harness carries a live cell. The board end of FLEX2 must be covered with insulating tape until step 16 [PROPOSED: reason, a short there drains the cell through PRT1].

### Step 10. Accept the body, and fit the radio corner if adopted

- **Join:** nothing is joined in the one-piece design. The body HSG1 (`outer_body`) of the ring size is accepted.
- **Locate:** the body drawing per size. The body files carry every pocket, one STEP and STL per ring size (`design/mfg/specs/body.md:5`; design/mfg/parts/body/), cut from the inside model v7 (`design/mech/thin/thin-notes.md:430`).
- **Before:** the body has, per the model v6 (`design/mech/thin/thin-notes.md:275` to `design/mech/thin/thin-notes.md:282`): the two floor slots 2.0 x 0.6 from X -3.5 to X -1.5, Y -5.9 and +5.9 (model v6.2, architecture 17.27; before it 2.6 x 0.6) (`design/mfg/specs/body.md:89`), with their bottom at the Z of the size (table above); the round joystick opening 5.60 through the wall, its axis on the radial line at the joystick angle of the size, on the joystick side (v7, `design/look/s1/merged32h-report.md:21`), coated with the body in the same batch as the frame FRM1; the joystick pocket 7.0 along the finger x 6.8 round the band, open from the bore up to a flat roof at the radius of the size, with the channel left uncut over the joystick (`design/architecture.md:795`, `design/mech/thin/thin-notes.md:249`); the glass seat lowered 0.05 mm under the glass footprint, outside the panel pocket (`design/mfg/specs/body.md:82`); the two floor pockets, 1.0 mm holes and 2.0 x 0.10 mm membrane seats at X -11.77 and +11.77, Y -4.8 (`design/architecture.md:657`, `design/mech/mic-path/mic-path.md:71` to `design/mech/mic-path/mic-path.md:73`); no wall slots and no pad holes (`design/architecture.md:557`); the motor pocket 5.2 x 2.6 at the motor angle of the size (`design/mech/thin/thin-notes.md:273`).
- **Check:** the inspection list of `design/mfg/specs/body.md:92`, plus: the slot positions and depths; the pocket width 7.0 all the way from the bore to the roof (a 6.95 mm gauge block passes straight in [PROPOSED: reason, the 6.9 mm flange must pass straight, `design/mech/thin/thin-notes.md:255`]); the roof radius of the size; metal of at least 0.40 mm round the motor pocket and the pocket (`design/architecture.md:740`); metal round the round joystick opening at least 1.067 mm on the X sides and 1.094 (US 7) to 1.592 (US 13) toward the bottom (`design/look/s1/merged32h-report.md:30`, `design/look/s1/merged32h-report.md:36`); the opening 5.60 with a pin gauge; the 0.20 mm metal ring under each membrane seat (`design/mech/mic-path/mic-path.md:79`); no burr in the holes.
- **After:** nothing irreversible.
- **Radio corner:** if adopted, the resin corner RC1 is bonded to the body here, on the planes X -10.6 and Y 2.05 (`design/mech/antenna/antenna-study.md:91`), with an adhesive no file names (section 5). Its top carries part of the glass seat (`design/mech/antenna/antenna-study.md:92`). The check adds the two bonded seams (section 4, row 9).

### Step 11. Bond the two microphone membranes into the underside seats

- **Join:** MEM1 and MEM2 to the body, each a disc of 2.0 mm, at most 0.10 thick, with its own adhesive ring, pressed into its seat from outside (`design/mech/mic-path/mic-path.md:73`, `design/mech/mic-path/mic-path.md:74`). No part is chosen yet (S23, `design/architecture.md:521`).
- **Locate:** the 2.0 mm counterbore on the block's underside, coaxial with the 1.0 mm hole.
- **Before:** step 10 passed; the seats are clean and dry.
- **Check:** each disc flush with the underside within 0.02 mm and without wrinkles [PROPOSED: reason, the seat is 0.10 deep and the opening faces the finger, `design/mech/mic-path/mic-path.md:81`]; air passes the membrane (a soft puff test with a hand bulb, no flow through the adhesive ring) [PROPOSED].
- **After:** a removed membrane is destroyed; a new one can be fitted until step 17.

### Step 12. Bond the two microphone gaskets on the pocket bottoms

- **Join:** GSK2 and GSK3 (foam rings OD 1.80, bore 1.00, adhesive on both faces) to the bottom of each floor pocket (`design/mech/mic-path/mic-path.md:70`), in the thickness chosen in step 3 for the board that goes into this body.
- **Locate:** centred on the 1.0 mm hole; bore equal to the hole (`design/mech/mic-path/mic-path.md:109`).
- **Before:** step 11 passed; the board is paired with this body by serial number (the gasket follows the board).
- **Check:** bore concentric with the hole, seen under a microscope through the hole from below.
- **After:** nothing irreversible until step 17 presses the gaskets.

### Step 13. Bond the frame FRM1 in the round opening, cure it, then fit the round cap CAP1 with its flange from the bore

- **Join:** first the frame FRM1 (titanium grade 5, 5.40 outer diameter, 4.80 bore, 1.30 long, coated gloss black in the same batch as the body) is bonded into the round 5.60 opening from outside the band with 3M Scotch-Weld DP420 Black epoxy, 0.10 mm radial gap filled all round (`design/bom.csv:82`, `design/mfg/specs/joystick-nub.md:23`). Cure: 24 h at 22 C with no heat, the room temperature cure of 3M's data sheet for DP420 Black (revision June 2024, page 3: 4,500 psi overlap shear on aluminium after 24 h at 22 C); no oven, because the membranes of step 11 and the gaskets of step 12 are already in the body. Then the round cap CAP1 (`joystick_cap`, Makrolon 2407 colour 901510, shank 4.40 and flange as one moulded part, `design/bom.csv:81`) goes in straight from the bore: the 6.90 x 6.40 flange rises through the 7.0 x 6.8 pocket (0.05 mm on each side along the finger, 0.2 mm round the band), the 4.40 shank passes up through the 4.80 bore of FRM1 with 0.20 mm radial clearance, and the flange stops under the pocket roof, 0.05 mm below it, held on all four sides by the roof round the 5.60 opening (`design/mech/thin/thin-notes.md:249`, `design/architecture.md:826`).
- **Locate:** the opening at the joystick angle of the size (-84.0 at US 7, -81.0 at US 8, -78.0 from US 9: table above; `design/architecture.md:769`); FRM1 by the opening's wall, its top 0.50 above the band surface and its lower end 0.80 under it (a depth stop on the bonding fixture [PROPOSED: reason, the glue gap does not set the depth]); CAP1 by the frame's bore; the flange by the pocket walls and the roof.
- **Before:** steps 10 to 12 passed. FRM1 and the body were coated in the same batch (`design/mfg/specs/joystick-nub.md:22`). The bonding faces are degreased with isopropyl alcohol [PROPOSED: reason, the coated faces carry handling oil]. The DP420 has cured 24 h at 22 C before CAP1 goes in, because the cap is centred by the frame's bore and the frame must not move. The harness is not yet in the channel: the cap must go in before the switch head, which lies under the flange on the bore side (`design/mech/thin/thin-notes.md:255`).
- **Check:** after the cure: the DP420 bead is closed all round the frame, seen at 10 times, and no epoxy is in the bore; frame top 0.50 above the band surface. After the cap: the flange passes the pocket without tilting; the cap tilts in four directions and presses straight in with no contact to the bore; free play of the flange toward the roof about 0.05 mm (`design/mech/thin/thin-notes.md:249`); cap rim 1.400 above the frame top (`design/look/s1/merged32h-report.md:18`).
- **After:** the frame's bond cannot be undone. The cap can still be taken out through the bore until step 14.

### Step 14. Lay the two harnesses in the band channel and thread their ends through the floor slots

- **Join:** FLEX1 with SW1 to SW5 and M1, and FLEX2 with BT1, PRT1, RT1 and CP1 to CP4, into the channel. Each ribbon's board end is passed up through its floor slot into the block: FLEX1 through the slot at Y -5.9, FLEX2 through the slot at Y +5.9 (`design/mech/thin/thin-notes.md:69`). A fixture holds the parts in place until the cast [PROPOSED: reason, the liner that holds them does not exist until step 21].
- **Locate:** the flat switch head with its stiffener under the flange, the centre switch's dome 0.15 mm below the cap (`design/mech/thin/thin-notes.md:133`); motor in its pocket at the motor angle of the size; cell from +48.713 through the bottom to -98.986 degrees at US 9 (`design/mech/thin/thin-notes.md:264`; other sizes in the table above); pads at the angles of step 8 on the fixture's core; ribbons at X -3.3 to -1.9 (`design/mech/thin/thin-notes.md:69`).
- **Before:** steps 6 to 13 passed; the cap CAP1 is already in its pocket and the frame FRM1 is cured (step 13). The ribbon run is drawn in the model with the ribbons inside the liner (`design/architecture.md:587`); how that is built is conflict K-A5.
- **Check:** the pads sit on the fixture's core at the right angles (gauge); the board ends stand up through both slots with their full free length.
- **After:** nothing irreversible.

### Step 15. Put the foam and the screen on the board, and plug the screen into J1

- **Join:** FOAM1 (`foam`) on the board's top face; DISP1 (`screen`) on the foam; the screen's tail (`screen_tail`) folded round the board's hand end into J1 on the under face, latch closed (`design/mech/thin/placement.csv:25`, `design/mech/thin/placement.csv:18`).
- **Locate:** the foam frame on the board outline, closed all round (its notch is removed in v7, `design/architecture.md:834`); the screen on the board outline.
- **Before:** step 5 passed.
- **Check:** the latch is closed over the whole tail width (visual under a microscope).
- **After:** nothing irreversible; J1 can be opened until step 17.

### Step 16. Solder the ribbon ends to the board (the cell connects here)

- **Join:** the board end of FLEX1 to J_BAND_A and of FLEX2 to J_BAND_B, on the board's under face, by hot-bar soldering [PROPOSED: reason, a thin ribbon on a row of lands is joined in one press, and the lands got no paste in step 2]. The board with its screen is held above the open block, under face up, while the ribbons rise through the slots (conflict K-A6). The model v5 keeps a free volume of 2.6 x 2.2 x 1.03 mm beside each slot under the board for one fold of the ribbon (`design/mech/thin/thin-notes.md:134`).
- **Locate:** the land rows of J_BAND_A (8 lands) and J_BAND_B (7 lands) (`design/bom.csv:76`, `design/bom.csv:77`).
- **Before:** steps 14 and 15 passed. The insulating tape of step 9 is removed just before the joint.
- **Check:** once FLEX2 is joined, the battery voltage reaches the power chip. Above 2.75 V the chip powers up by itself (`design/datasheets/npm1304_datasheet_v1_0.txt:413`, `design/datasheets/npm1304_datasheet_v1_0.txt:1674`) and the ring boots to STANDBY with no VBUS (`design/firmware.md section 1.2, name STANDBY`). Proof: the jig's spring pins on CP1 to CP4 give USB; the ring enumerates and GET_INFO answers (`design/firmware.md section 6.3, name GET_INFO`). That proves the four pads, FLEX2 and J_BAND_B at once.
- **After:** the ring now runs on its own cell. It draws about 0.03 mA in STANDBY [ESTIMATE of `design/firmware.md section 8.5, name 0.03 mA`]: 24.4 days on the smallest cell of 17.6 mAh [CALC: 17.6 / 0.03 / 24 = 24.4 days; cell `design/architecture.md:791`]. The joints cannot be reached after step 17.

### Step 17. Lower the board and screen into the block

- **Join:** PCB1 into the block cavity and DISP1 into the panel pocket (27.45 x 12.9, `design/mech/thin/thin-notes.md:21`), no adhesive [PROPOSED: reason, the screen is held from above by the glass through ADH1, `design/mfg/specs/cover-glass.md:6`]. The ribbons slide back down through the slots as the board goes down, and each takes one fold in the free volume beside its slot (`design/mech/thin/thin-notes.md:134`); the bend radius of that fold is the flex maker's (`design/mech/thin/thin-notes.md:159`).
- **Locate:** the panel pocket walls; the board on the block stack: floor 0.40, gap 0.05, parts 1.00, board 0.30, foam 0.10, screen 0.80 (`design/architecture.md:426`). The microphone lids press the gaskets of step 12 (`design/mech/mic-path/mic-path.md:85`). U11, C83 and C84 sit 0.985 mm or more from the +Y slot in plan (`design/mech/thin/thin-notes.md:135`).
- **Before:** step 16 passed.
- **Check:** the screen lies flat and below the glass seat; seen from above, the screen is centred in the pocket within 0.05 mm per side (the pocket clearance is 0.05, `design/mfg/specs/body.md:89`).
- **After:** the board's under face, its test pads and the ribbon joints are closed for good. Lifting the board after this tears the ribbons.

### Step 18. Test the open ring through the charging pads

- **Join:** nothing is joined. The jig gives VBUS through CP1 to CP4. The ring goes to CHARGING (`design/firmware.md section 1.2, name CHARGING`), the jig sends FACTORY ENTER (`design/firmware.md section 9.3, name ENTER`).
- **Locate:** the jig's core in the bore, spring pins on the four pads.
- **Before:** step 17 passed; the factory flag is still 1.
- **Check:** every factory test of section 9.3 (`design/firmware.md section 9.3, name T-STORE`), as the factory flow lists it (`design/firmware.md section 9.3, name Factory flow`): T-SCREEN (screen without glass), T-SIGN (the recording sign on the screen, `design/firmware.md section 9.3, name T-SIGN`), T-JOY and T-CENTRE (a jig finger presses the cap), T-MOTOR, T-MIC1 and T-MIC2 (through gaskets, holes and membranes), T-STORE, T-RADIO (in the metal body, no glass yet), T-XTAL, T-CHARGE (reports the state and the current; its pass range is in `design/firmware.md section 9.3, name T-CHARGE`).
- **After:** nothing irreversible. This is the last full test before steps 19 to 23, which cannot be undone.

### Step 19. Seal the two floor slots round the ribbons

- **Join:** a sealant into each floor slot, round the ribbon, applied from the channel side. On ring sizes US 7, 8 and 9 the same sealant, in the same step, also closes the window between the motor pocket and the block's cavity: the plug SEAL2, 0.79 to 0.81 cubic mm, about 4.0 x 1.1 mm, applied from the band side up to the motor's adhesive bead (`design/architecture.md` 17.27; `design/mech/thin/thin-notes.md` section "Model v6.2"). On US 10 to 13 there is no window and no SEAL2. No file names it: the design only names the need (bench item B8, `design/architecture.md:473`). [PROPOSED: a thick, non-flowing UV-curing dam material; reason, it must not run up into the block under the board, it is reached only from the channel, and it cures without heat next to the cell.]
- **Locate:** the slot 2.0 x 0.6 mm (model v6.2, `design/architecture.md` 17.27; before it 2.6 x 0.6) and the ribbon 1.4 x 0.15 in it: the open area to fill is 0.99 square mm per slot [CALC: 2.0 x 0.6 - 1.4 x 0.15; slot size `design/mech/thin/thin-notes.md:21`]. The slot's bottom lies deeper on larger sizes (Z -0.20 on US 7 to Z -1.85 on US 13, table above), so the length of slot to fill changes by size.
- **Before:** step 18 passed.
- **Check:** the sealant fills the slot all round the ribbon, seen at 20 times from the channel side; after curing, USB still enumerates (the ribbon was not cut).
- **After:** the slots are closed. The board cannot come out.

### Step 20. Dam the joystick pocket (DAM1)

- **Join:** DAM1 (`joystick_dam`), a dispensed UV-cured dam frame round the switch head, so the resin of step 21 cannot run between the switches and the flange (`design/bom.csv:55`, `design/mech/thin/placement.csv:39`). It is 0.15 mm wide round the band, 0.05 mm off the switch bases, fills to the pocket's walls along the finger, and rises to the top of the switch bases (`design/mech/thin/thin-notes.md:117`); in v6 it is that frame less the liner, the bend and the fill, wholly in the pocket (`design/mech/thin/thin-notes.md:251`). The dam material is not chosen (open item S26, `design/architecture.md:524`).
- **Locate:** inside the joystick pocket, round the five switch bases on the flat head, at the joystick angle of the size (table above). The motor stands 0.07 to 0.08 mm from the dam on US 7 to US 9 (`design/architecture.md:797`): the dam must not grow toward the motor.
- **Before:** steps 13, 14 and 19 passed: the frame and the cap are in (step 13), the flat head with its stiffener sits under the flange (step 14), the slots are sealed (step 19). The dam waits for all three, because it is dispensed from the bore round the head in its final place. What holds the dam up before the liner exists is conflict K-A12.
- **Check:** the dam is closed all round the head, seen from the bore at 20 times; T-JOY and T-CENTRE pass again (`design/firmware.md section 9.3, name T-JOY`, `design/firmware.md section 9.3, name T-CENTRE`).
- **After:** the switches cannot be reworked. The dam closes the pocket round its edge only; under the head the liner's resin still reaches the stiffener (`design/mech/thin/thin-notes.md:153`, K15).

### Step 21. Cast the resin liner

- **Join:** the liner LNR1 (`band_liner`), resin cast into the channel over the parts, 0.3 mm thick, closing the channel toward the finger (`design/architecture.md:440`, `design/mfg/specs/band-liner.md:15`). The resin grade is open (`design/mfg/specs/band-liner.md:43`). The mould core is a ring of the size's inner diameter (`design/mfg/specs/band-liner.md:37`) and presses on the four pads so they stay flush and free of resin [PROPOSED: reason, the pads must be flush with the liner, `design/architecture.md:559`]. At the joystick the resin fills under the stiffener and a 0.1 mm strip on each side of the pocket along its length, where the 7.0 mm pocket is wider than the 6.8 mm channel (`design/architecture.md:795`, `design/mech/thin/thin-notes.md:255`), up to the dam.
- **Locate:** the core sets the inner diameter; the band's two edge walls set the width 6.8 mm (`design/mfg/specs/band-liner.md:28`).
- **Before:** steps 19 and 20 passed (DAM1 cured). The cell maker has stated the highest temperature the cell may see, and the resin cures below it (`design/mfg/specs/band-liner.md:45`; bench item B8, `design/architecture.md:473`). Whether the 0.2 mm swelling gap above the cell is filled is decided (`design/mfg/specs/band-liner.md:48`). The ring is live in STANDBY during the cast (step 16).
- **Check:** the cell's temperature during the cure, logged through the ring's own thermistor reading and a thermocouple on the shell over the cell [PROPOSED]; the band-liner inspection list (`design/mfg/specs/band-liner.md:34`): thickness at 6 points, inner diameter with a ring gauge, no voids over the cell or the ribbons; pads flush and clean; then USB enumerates, T-JOY, T-CENTRE and T-MOTOR pass.
- **After:** everything in the band is closed. Repair is not possible after casting (`design/architecture.md:440`).

### Step 22. Clean and inspect the glass seat and the screen face before the bond

- **Join:** nothing is joined. The body's glass seat and the screen's top face are cleaned with isopropyl alcohol and lint-free wipes, then blown with ionised air [PROPOSED: reason, the cast of step 21 runs next to the block, and a speck on the seat breaks the line of SEAL1 while a speck on the screen shows under ADH1]. History: this step placed the light plug LP1 until v6; the light plug is removed in v7 (`design/architecture.md:834`).
- **Locate:** the seat land between the panel pocket and the glass edge, 0.825 mm at each end and 0.83 mm at each side (step 23).
- **Before:** step 21 passed.
- **Check:** under a lamp at a low angle, no resin, dust or fibre on the seat or the screen [PROPOSED]; the screen still sits flat in its pocket (`design/mfg/specs/body.md:89`).
- **After:** nothing irreversible.

### Step 23. Bond the cover glass: to the screen with ADH1, and to the body with a perimeter seal

- **Join:** GL1 (`cover_glass`) to the screen through ADH1 (`clear_adhesive`, 0.10 mm, `design/architecture.md:426`), and to the body's glass seat with the seal ring SEAL1 (`glass_seal`), a die-cut adhesive ring 0.05 mm thick under the glass edge outside the panel pocket (`design/bom.csv:54`, `design/mech/thin/placement.csv:29`). The tape itself is not chosen and its compressed thickness is unknown (`design/mech/thin/thin-notes.md:160`, K22; open item S26). [PROPOSED order: ADH1 laminated to the glass's inner face first; then SEAL1 on the seat; then the glass pressed down under vacuum. Reason: no liquid can run into the screen pocket, nothing needs heat, and the bond line has a fixed thickness.]
- **Locate:** the glass outline in the body's recess: the metal lip round the glass is 0.1 mm along X and 0.095 mm across [CALC: (29.3 - 29.1) / 2 and (14.75 - 14.56) / 2; glass `design/mech/thin/placement.csv:27`, block `design/architecture.md:419`]. The seat land between the panel pocket and the glass edge is 0.825 mm at each end and 0.83 mm at each side [CALC: (29.1 - 27.45) / 2 and (14.56 - 12.9) / 2; pocket `design/mech/thin/thin-notes.md:21`]. The print has no opening (`design/mfg/specs/cover-glass.md:6`).
- **Before:** step 22 passed. The seat is lowered 0.05 mm inside the body (`design/mfg/specs/body.md:82`): SEAL1 lies from Z 2.70 to 2.75, under the glass's underside at Z 2.75 (`design/mech/thin/thin-notes.md:136`, `design/mech/thin/placement.csv:29`), 0.0293 mm from the clear adhesive (`design/mech/thin/thin-notes.md:132`).
- **Check:** no bubble anywhere under the glass, since ADH1 covers the whole face (`design/architecture.md:833`); the glass edge flush with the metal within 0.05 mm all round [PROPOSED]; SEAL1 continuous all round, seen through the glass edge.
- **After:** the screen, J1 and the board are closed for good.
- **Radio corner:** if adopted, part of the seat is the resin corner's top (`design/mech/antenna/antenna-study.md:92`); the seal must hold on resin and on metal.

### Step 24. Cure and check the closed ring for leaks

- **Join:** nothing is joined. The seal of step 23 reaches its full strength (time from the tape's maker).
- **Locate:** none.
- **Before:** step 23 passed.
- **Check:** [PROPOSED] a pressure-decay leak test is not possible, because the ring has no port. On every ring: a 10 minute dip in water at 0.1 m, then T-MIC1, T-MIC2, T-SCREEN and USB enumeration pass, and no mist under the glass [PROPOSED: reason, a quick screen for a gross leak before the type test of section 4]. On sample rings only: the IP65 type test of section 4.
- **After:** nothing new.

### Step 25. Final test of the closed ring

- **Join:** nothing is joined. Jig on the pads, FACTORY ENTER.
- **Locate:** the jig's core in the bore.
- **Before:** step 24 passed; the factory flag is still 1 (it is cleared only by SHIP_ENTER, `design/firmware.md section 9.3, name SHIP_ENTER`).
- **Check:** every factory test again (section 9.3, `design/firmware.md section 9.3, name T-STORE`): T-RADIO now in the final body with glass (Bluetooth); USB enumeration proves the four pads; T-JOY and T-CENTRE (joystick); T-MOTOR (motor); T-MIC1 and T-MIC2 through the membranes (microphones); T-SIGN through the glass (the recording sign on the screen, `design/firmware.md section 9.3, name T-SIGN`); T-SCREEN through the glass (screen); T-STORE, T-XTAL, T-CHARGE. Then one test on the cell alone [PROPOSED]: VBUS off, a long press of 1.0 s on the centre of the cap CAP1 (SW2) starts a recording with motor pulse M1, a second long press stops it; VBUS on again and GET_INFO shows the same boot count (`design/firmware.md section 6.3, name GET_INFO`). Reason: the motor now runs from its own regulator U11 on the cell, outside the power chip's 100 mA battery limit, so a motor start no longer passes the power chip (`design/architecture.md:704`, `design/architecture.md:706`); but nothing is measured, and a start still takes up to 228 mA from the cell, whose own discharge limit and protection trip current are unknown (`design/architecture.md:710`, S12). This test shows on the real cell that the protection circuit does not trip and the ring does not reset; the jig's VBUS would hide it.
- **After:** nothing new.

### Step 26. First charge

- **Join:** nothing is joined. VBUS on the pads; the charger runs at CHARGE_CURRENT 15 mA to 4.35 V (`design/architecture.md:567`, `design/architecture.md:635`).
- **Locate:** the jig's core.
- **Before:** step 25 passed.
- **Check:** T-CHARGE shows the charger on; the battery voltage (battery_mv in the answer of GET_BATTERY, `design/firmware.md section 6.3, name GET_BATTERY`) rises. Charge to 50 percent before ship mode [PROPOSED: reason, a partly charged cell ages less in storage and still wakes the ring in the case; the cell maker may set another level, S12]. A full charge takes 1.17 to 2.13 hours over US 7 to 13 [CALC: 17.6 / 15 and 31.9 / 15; capacities `design/architecture.md:783`, `design/architecture.md:789`].
- **After:** nothing new.

### Step 27. Put the ring in ship mode

- **Join:** nothing is joined. The jig sends FACTORY sub-command SHIP_ENTER 0x7F (`design/firmware.md section 9.3, name SHIP_ENTER`) and then removes VBUS. The datasheet ties ship mode entry to VBUS being gone: "When VBUS is not present, the device enters Ship mode immediately. The host software must wait until EVENTSVBUSIN0SET ... to ensure VBUS is disconnected" (`design/datasheets/npm1304_datasheet_v1_0.txt:9064`, page 116). The firmware F6 does this: it waits for VBUS removal, then writes TASKENTERSHIPMODE (`design/firmware.md section 9.3, name SHIP_ENTER`, `design/firmware.md section 8.4, name TASKENTERSHIPMODE`). Sample rings get SHIP_SAMPLE 0x7E instead, which keeps the factory flag (`design/firmware.md section 9.3, name SHIP_SAMPLE`).
- **Locate:** the jig's core.
- **Before:** step 26 passed.
- **Check:** while VBUS is still on, the jig's Bluetooth scanner receives the ring's ship beacon; with VBUS gone the beacon stops within 1 s and none is seen for 60 s (`design/firmware.md section 9.3, name SHIP_ENTER`, ruling R20: a ring with no paired device does not advertise in STANDBY, so silence alone would prove nothing). On sample rings only: VBUS back on wakes the ring (`design/datasheets/npm1304_datasheet_v1_0.txt:9084`, VBUS above VBUSPOR, 3.9 V at `design/datasheets/npm1304_datasheet_v1_0.txt:841`) and it boots (`design/firmware.md section 1.2, name VBUSPOR`); such a ring is shipped with SHIP_SAMPLE, so its factory flag stays set and it can be tested again (`design/firmware.md section 9.3, name SHIP_SAMPLE`).
- **After:** on a ring shipped with SHIP_ENTER the factory flag is clear: the factory tests answer NOT_ALLOWED from now on (`design/firmware.md section 9.3, name NOT_ALLOWED`). Only VBUS wakes the ring: SHPHLD is on TP19 (`design/ecad/ring/sch-notes.md:44`), under the board.

### Step 28. Pack

- **Join:** nothing is joined. The ring goes into its case.
- **Locate:** the case pocket (`design/architecture.md:556`).
- **Before:** step 27 passed.
- **Check:** serial number, ring size and the test records of steps 5, 18, 21, 25 and 27 are kept together.
- **After:** nothing new.

## 3. Order conflicts

Each conflict names the files and lines that cause it, and gives at most one way out, marked as a proposal. Nothing here is a redesign. The status column is the state on the model v6, architecture 17.22 to 17.26 and firmware F6 (2026-11-11, 05:38 on); the details are in `design/mfg/assembly/v6-update-notes.md`.

| # | Conflict | Caused by | One way out (PROPOSAL) | Status (model v6) |
|---|---|---|---|---|
| K-A1 | The board is testable through its test pads only before step 17. The test pads are on the populated under face (`design/ecad/ring/pcb/board-notes.md:53`; footprint `design/ecad/ring/pcb/build_board.py:253`), which faces the block floor 0.05 mm away (`design/architecture.md:426`). After bonded glass and a cast band only the four charging pads remain. A boot loader fault after step 17 cannot be repaired. | `design/architecture.md:291` (W12), `design/firmware.md section 9.2, name MCUboot` (MCUboot) | PROPOSAL: treat USB through the pads as the only service port after step 17, and lock the MCUboot area against USB writes before step 5 ends, so a bad update cannot remove the way back. | CHANGED: the boot loader lock is applied in firmware F6 (`design/firmware.md section 9.2, name Boot loader locked`). The access limit itself stays, by design. |
| K-A2 | The floor slots must be sealed before the cast, but no file names how. B8 names "sealing at the two floor slots" as a bench question only. | `design/architecture.md:473`, `design/mfg/specs/band-liner.md:50`, `design/mfg/specs/body.md:116` | PROPOSAL: step 19 as written (UV-curing dam from the channel side), proven on the bench B8 housing. | OPEN: no sealant in the parts list or the model; open item S26 (`design/architecture.md:524`). The slot is deeper on larger sizes (table "What changes by ring size"). |
| K-A3 | The cast resin runs into the joystick pocket and locks the switches and the flange: the channel is filled over the parts, and nothing stops it at the switch head. | `design/architecture.md:440`, `design/mech/thin/placement.csv:32` (flange 0.15 above the switch tops) | PROPOSAL: step 20 as written (a dam round the head), proven with bench item B9 (`design/architecture.md:511`). | CHANGED: the dam DAM1 is a part of the model and the parts list (`design/mech/thin/thin-notes.md:117`, `design/mech/thin/thin-notes.md:251`, `design/bom.csv:55`). Still open: its material (S26) and that it seals the pocket's edge only (K15, `design/mech/thin/thin-notes.md:153`). See K-A12. |
| K-A4 | No glass-to-body adhesive or seal existed, and the seat had no room for one. | `design/mech/antenna/antenna-study.md:92`, `design/mfg/specs/cover-glass.md:6` | PROPOSAL: lower the glass seat by the seal's thickness (about 0.05 mm) inside the body; the outer shape does not change. | CLOSED in the geometry by model v5: seat lowered 0.05, seal ring SEAL1 0.05 thick (`design/mech/thin/thin-notes.md:117`, `design/mech/thin/thin-notes.md:136`, `design/mfg/specs/body.md:82`, `design/bom.csv:54`). Open: the tape and its compressed thickness (K22, `design/mech/thin/thin-notes.md:160`; S26). |
| K-A5 | The liner is said to be cast in place over the parts (17.3, band-liner spec), but the model puts each ribbon inside the liner with 0.075 mm of resin on each side, and the parts stand on that resin, reached through windows not yet drawn. A single cast cannot make a ribbon float 0.075 mm under parts that are soldered to it; the alternative, a laminate liner made first (S19), is not proven by any maker. | `design/architecture.md:440`, `design/architecture.md:587`, `design/architecture.md:517`, `design/mech/thin/thin-notes.md:81`, `design/mech/thin/thin-notes.md:85` | PROPOSAL: build the first bench housing (B8) with the cast-in-place route of step 21, where the 0.075 mm layer is the solder joint's own height filled by the resin, and measure the liner's thickness over the ribbon; the mechanical designer then keeps or drops the laminate. | OPEN: unchanged in model v5 (`design/mech/thin/thin-notes.md:117`); v6 adds the flat head on a stiffener with liner fill under it (`design/mech/thin/thin-notes.md:250`), which does not answer how the trunk is embedded. S26, S19. |
| K-A6 | Each ribbon has parts at its band end and a joint of 8 lands (FLEX1) or 7 lands (FLEX2) at its board end, and passes a closed slot of 2.0 x 0.6 mm (2.6 x 0.6 before model v6.2). So the board-end joint must be made after threading, with the board held above the block (step 16). The ribbon's slack needs room when the board goes down. | `design/mech/thin/thin-notes.md:69`, `design/bom.csv:76`, `design/bom.csv:77`, `design/mfg/specs/band-flex-tails.md:61` | PROPOSAL: reserve a free area beside each slot on the under face for one fold of the ribbon. | CHANGED: the model v5 keeps a free volume of 2.6 x 2.2 x 1.03 mm beside each slot, checked empty (`design/mech/thin/thin-notes.md:134`). Open: whether one fold fits that height (bend radius, K21, `design/mech/thin/thin-notes.md:159`), and the board layout keeping it free (S14). |
| K-A7 | Ship mode must come last, but SHIP_ENTER cleared the factory flag, and the firmware's ship entry was written for the older power chip. | `design/datasheets/npm1304_datasheet_v1_0.txt:9062` | PROPOSAL: a separate FACTORY sub-command that enters ship mode and keeps the flag, for samples only. | CLOSED by firmware F6: SHIP_SAMPLE 0x7E keeps the flag (`design/firmware.md section 9.3, name SHIP_SAMPLE`); both ship commands wait for VBUS removal and write TASKENTERSHIPMODE (`design/firmware.md section 9.3, name SHIP_ENTER`, `design/firmware.md section 8.4, name TASKENTERSHIPMODE`). |
| K-A8 | The cell is live from step 16 to the end, through the cast (step 21) and the glass bond. The cast's heat limit is unknown: the cell maker must state it. | `design/mfg/specs/band-liner.md:15`, `design/mfg/specs/band-liner.md:45`, `design/architecture.md:473` | PROPOSAL: join the cell at step 9 as written, but keep the ring on VBUS through the core's pad pins during the cure, so the charger, not the cell, carries the load, and log the thermistor. | OPEN: no source states the limit (S12). |
| K-A9 | ANT1 cannot be soldered in step 2 as drawn: its pads are off the board in the corner notch. | `design/architecture.md:513` (S15) | PROPOSAL: none here; the layout engineer closes S15 before step 1. | OPEN: S15 unchanged (`design/architecture.md:513`). |
| K-A10 | The body spec put the floor slots at X -4.7, outside the channel; the model needs X -2.2. | `design/mech/thin/thin-notes.md:91` | PROPOSAL: change the body spec to X -2.2. | CLOSED: the body spec now says X -2.2 (`design/mfg/specs/body.md:89`); the model keeps it (`design/mech/thin/thin-notes.md:117`). |
| K-A11 | CLOSED in v7: the light guide and the light plug are removed in v7, so no conflict with the screen remains. | `design/architecture.md:834` | none needed. | closed (v7) |
| K-A12 | NEW, the sources contradict each other: the dam DAM1 is drawn standing ON the liner (its frame starts at the liner's face and rises to the switch base tops), but it must exist BEFORE the liner is cast, because its job is to keep the cast out of the pocket. Before the cast there is nothing under the dam between the head's edge and the pocket wall but the open space down to the mould core. | `design/mech/thin/placement.csv:39` ("frame on the liner"), `design/bom.csv:55` ("dam frame on the liner"), `design/mech/thin/thin-notes.md:251` (the dam is the frame less the liner), against `design/mfg/specs/band-liner.md:50` (dam BEFORE the cast) and step 20 | PROPOSAL: cast the liner in two shots: first the skin under the joystick only, with a removable plug filling the pocket above the stiffener; then DAM1 on that cured skin; then the rest of the liner. The mechanical designer decides (S26). | OPEN, new |

## 4. Water and dust (F11)

What IP65 asks, in plain words. The first digit 6 means dust-tight: "No ingress of dust; complete protection against contact (dust-tight). A vacuum must be applied. Test duration of up to 8 hours based on airflow." The second digit 5 means water jets: "Water projected by a nozzle ( 6.3 mm (0.25 in) ) against enclosure from any direction shall have no harmful effects", for "1 minute per square meter for at least 3 minutes", with "12.5 litres per minute", at a pressure of 30 kPa at a distance of 3 m. Source: the Wikipedia page "IP code" (https://en.wikipedia.org/wiki/IP_code), a summary of the standard IEC 60529, read on 2026-11-11; the standard itself was not read. The signed requirement is S6 "IP65 or better" (`requirements.md:26`).

| # | Opening or joint | Sealing means the design names today | What IP65 asks of it | Can the design as written claim it? |
|---|---|---|---|---|
| 1 | Cover glass to body, all round the block | the seal ring SEAL1, 0.05 mm, in a seat lowered 0.05 mm (`design/mfg/specs/cover-glass.md:6`, `design/bom.csv:54`); tape not chosen (S26) | no dust and no harmful water through the seam from any direction | needs a test (and a chosen tape) |
| 2 | Joystick: the frame FRM1 seam and the cap CAP1 in its bore | the frame seam is closed by the DP420 Black bond all round (step 13); the cap has 0.20 mm radial clearance in the bore and no seal (`design/mfg/specs/joystick-nub.md:48`); sealing at the cap is a bench question (B9, `design/architecture.md:511`). The switches themselves are rated "IP6X and IPX7" (`design/architecture.md:47`) | the pocket behind the cap may get wet only if nothing is harmed: switches sealed, their joints inside the cast resin, the dam DAM1 tight (`design/bom.csv:55`; edge only, K15) | needs a test (and a dam material, S26, and an answer to K-A12) |
| 3 | Two microphone holes, 1.0 mm, on the block's underside | a water and dust membrane in a 2.0 x 0.10 mm seat (`design/mech/mic-path/mic-path.md:13`, `design/architecture.md:656`); no part chosen (S23) | the membrane holds dust and the jets at 30 kPa | needs a test (and a chosen membrane) |
| 4 | Print of the cover glass | no opening: the print window is removed in v7 (`design/mfg/specs/cover-glass.md:6`) | nothing beyond row 1 | yes, it adds no path |
| 5 | Liner to band, along both band edges and at the two liner ends | the cast resin's own grip on the metal (`design/architecture.md:440`); no primer or grade named (`design/mfg/specs/band-liner.md:43`) | no water under the liner at the edge seams | needs a test (resin grade first) |
| 6 | The four pads in the liner | the cast resin round each pad (`design/architecture.md:557`, `design/mech/thin/thin-notes.md:75`); no seal of the pad edge named | no water along the pad edge to the ribbon | needs a test |
| 7 | The two floor slots for the ribbons | none named; B8 names the question (`design/architecture.md:473`) | inside the ring, behind the liner: they matter only if rows 5 or 6 leak; they also keep the cast out of the block | cannot today (step 19 proposes a means) |
| 8 | Screen, board and parts inside the block | behind rows 1 and 3 | nothing of their own | follows rows 1 and 3 |
| 9 | Radio corner seams, only if adopted | "two bonded seams" (`design/mech/antenna/antenna-study.md:79`), adhesive not named | no dust and no harmful water through the seams | needs a test |

What can be claimed today: no water or dust rating. Row 7 names no sealing means at all; row 2 names none at the cap (the frame seam is bonded) and relies on the switches' own rating and the dam; rows 1, 3, 5, 6 and 9 name a means with no chosen material and no test; rows 4 and 8 add no path of their own. Model v5 gave row 1 its seal ring SEAL1 (K-A4), which moves it from "cannot" to "needs a test". The ring as designed today is not rated, and IP65 is not met on paper.

The test that would prove IP65 (to describe, not to order: bench purchases are on hold). On finished rings, after step 24 (sample size from the test house [PROPOSED: at least 3 rings, one per size group: US 7, US 10, US 13]):
1. Before: all factory tests of step 25 pass, and the screen shows no mist.
2. Dust (first digit 6): the dust chamber of IEC 60529 for the 6, with a vacuum applied, up to 8 hours.
3. Water jets (second digit 5): the 6.3 mm nozzle, 12.5 litres per minute, 30 kPa at 3 m, from every direction, 1 minute per square metre and at least 3 minutes; the ring turned so the jet reaches the joystick, the microphone holes, the liner edges and the pads.
4. After: all factory tests pass again; no mist under the glass; then one ring is cut open on the seams of rows 1, 2, 5 and 6 to look for dust and water traces [PROPOSED: reason, the ring has no port, so only a cut shows what got in].
A pass on all rings in both tests gives IP65. Water by immersion (IPX7 or IPX8) is a separate test; IPX7 does not imply IPX5 (same source).

## 5. Who decides or supplies

| Open material or process | Used in step | Who decides or supplies | Open item |
|---|---|---|---|
| Glass seal SEAL1: the tape and its compressed thickness (the seat depth is set, 0.05 mm) | 23 | the mechanical designer, with the glass maker | S26 |
| Clear adhesive ADH1 (product, outline) | 23 | the design partner (`design/bom.csv:53`) | new |
| Foam FOAM1 (product 0.10 mm, outline closed all round) | 15 | the design partner (`design/bom.csv:57`) | new |
| Casting resin of the liner (grade, skin certificate, cure heat) | 21 | a ring maker or the design partner, with the cell maker's heat limit | S13, B8, S12 |
| Sealant of the floor slots | 19 | the mechanical designer; bench B8 | S26, B8 |
| Dam DAM1: material, and how it stands before the cast (K-A12) | 20, 21 | the mechanical designer; bench B9 | S26, B9 |
| Stiffener of the joystick head (stainless or polyimide) and its bond to the head | 6 | the flex maker | S26 |
| Adhesive of the joystick frame: fixed, 3M Scotch-Weld DP420 Black, 24 h at 22 C | 13 | fixed in v7 (`design/mfg/specs/joystick-nub.md:23`); bench B9 proves the bond on the coated titanium | B9 |
| Places of U11, C83, C84 on the board | 2 | the layout engineer | S22 |
| Cap CAP1 and frame FRM1: fixed, Makrolon 2407 colour 901510 moulded; Ti-6Al-4V turned, separate part | 13 | fixed in v7 (`design/mfg/specs/joystick-nub.md:16`); a moulder and the body maker quote (`design/bom.csv:81`, `design/bom.csv:82`) | B9 |
| Microphone gasket foam and its three thicknesses | 3, 12 | a gasket maker; bench B7 | S23 |
| Microphone membrane, at most 0.10 mm | 11 | Gore or another membrane maker | S23 |
| Charging pads: plated land or soldered disc | 8 | the design partner and the flex maker (`design/bom.csv:61`) | S19 |
| Ribbon outlines, lengths per size, the fold's bend radius (K-A6) | 6, 8, 14, 16, 17 | the mechanical designer, the flex maker and the layout engineer | S16, S14, S26 |
| Ribbon-to-board joint (hot bar) and the solder of the band parts | 7, 9, 16 | the design partner and the flex maker (`design/mfg/specs/band-flex-tails.md:61`) | new |
| Cell heat limit for soldering and for the cast; charge level for storage | 9, 21, 26 | the cell maker | S12 |
| Radio corner resin and its adhesive | 10, 23 | the owner decides the corner; then the body maker | S24 |
| Test jig (spring pins on the test pads, the pad core, speaker, camera) | 5, 18, 25 | the firmware designer (work item W13, `design/firmware.md section 10.2, name W13`) with the builder | new |
| Motor pocket fix (free space to the body under 0.05 mm at US 9 to 13) | 7, 10, 14 | the mechanical designer (`design/architecture.md:796`) | new |
| IP65 test house and sample size | section 4 | the owner | new |

## 6. Changes other files need (not made here)

The changes listed at the first issue of this file are made in the files they named, except the two rows below that are still open. New rows follow from model v6.

| # | File and line | Present text | New text |
|---|---|---|---|
| 1 | `requirements.md:26` | "IP65 or better" | add: not met by the design today (assembly.md section 4; architecture 17.23) |
| 2 | `design/bom.csv` new row | none (no part for the floor slot sealant) | Floor slot sealant, 2 slots, UV-curing dam material, open item S26 (assembly.md step 19) |
| 3 | `design/mech/thin/placement.csv:39` and `design/bom.csv:55` | "frame on the liner" | frame round the switch head, made before the liner is cast (assembly.md step 20, K-A12) |
| 4 | `design/architecture.md:716` (17.23) | "its step 2 still lists the motor switch Q1 and diode D1, and its step 25 still warns of a reset at a motor start; 17.22 wins" | step 2 lists U11, C83, C84 (no motor switch, no diode); step 25 tests the cell's protection at a motor start (17.22) |
| 5 | `design/architecture.md:524` (S26) | "how the liner is built with the ribbons inside" | add: how the dam DAM1 stands before the liner is cast (K-A12) |
| 6 | `design/mech/thin/placement.csv:32`, `design/mech/thin/placement.csv:33` | (done by the inside model v7) | no light rows remain; joystick_cap is the round cap CAP1 and joystick_frame the frame FRM1 (inside model v7, design/mech/thin/thin-notes.md section "Model v7") |
| 7 | `design/mfg/tools/draw.py:40` | (done by the maker files v7) | sheets and maker files from the inside model v7: joystick-cap and joystick-frame (FRM1), no light parts (design/mfg/parts/index.csv) |

RESULT: done, 28 numbered steps (numbers unchanged) brought to design version 7 (architecture 17.29 and 17.30): no step fits a light guide or a light plug (both removed in v7, steps 4 and 22 now clean and inspect), step 13 bonds the frame FRM1 with DP420 Black (24 h at 22 C) and then fits the round cap CAP1 with its flange from the bore; of 12 conflict rows 4 are closed (K-A4, K-A7, K-A10, K-A11), 3 changed (K-A1, K-A3, K-A6), 5 open (K-A2, K-A5, K-A8, K-A9, K-A12); no water or dust rating can be claimed today; the check script passes (v7-check.log).
