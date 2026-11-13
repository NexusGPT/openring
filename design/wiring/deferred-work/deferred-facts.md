# Facts for deferred items 27, 95, 112, 115

ROOT = .. Every path below is from ROOT. Triage = `design/wiring/deferred-triage.csv`.
Version read: ROOT commit 796a0086 (`git rev-parse --short HEAD`). Read window: 16:13 to 16:22 CET, Friday 13 November 2026 (`date`). `design/mfg/assembly/` and `design/sim/circuit/` are being edited by other helpers; a quote from them is as of this window.
Quote check: `design/wiring/deferred-work/deferred-facts-verify.log` runs every quote below through `grep -n -F` at its file and line.
Item 27 count: the triage text says "Six". No line in the two schematic notes says "six design" or "six risk" (case-insensitive grep over both files: 0 hits). The files hold 13 numbered ring risks (1 to 9 on one line, 10 to 13 on four lines) and 9 case risks. The lead decides which list the item means.

## Item 27: ring risks (`design/ecad/ring/sch-notes.md`, section 9) and case risks (`design/ecad/case/sch-notes.md`, section 7)

**1. Item text.** `design/wiring/deferred-triage.csv:28`: "Six design risks are listed for an electronics engineer to review"

**2. Sub-points and their state today.**

Ring section 9 heading: `design/ecad/ring/sch-notes.md:91` "## 9. Design risks an electronics engineer must review". Risks 1 to 9 are one line there: `design/ecad/ring/sch-notes.md:93` "1 to 9 of A3 stand (screen sequencing, SGM38046 AVIN". Their text is in `design/ecad/ring/evidence/a5/sch-notes_before.md` lines 114 to 122.

Ring risk 1, screen power sequencing (`evidence/a5/sch-notes_before.md:114`, "Screen power sequencing: VCI (VDD_3V0) and IOVCC (VDD_1V8) are on whenever the bucks run"). State: nothing found. Searched "SWIRE|power sequenc" in `design/wiring/lead-decisions.md`, `design/sim/circuit/sim-notes.md`, `design/ecad/ring/pcb/board-notes-r4.md`: no hit on the screen sequence.

Ring risk 2, SGM38046 AVIN (`evidence/a5/sch-notes_before.md:115`, "SGM38046 AVIN is drawn with only its 10 uF capacitor"). State: nothing found in the three state files for "AVIN". Maker: `design/datasheets/p3_sgm38046.txt:204` "Analog Power Pin. Place a bypass capacitor between this pin and ground." The line does not say where AVIN is fed from.

Ring risk 3, USB protection (`evidence/a5/sch-notes_before.md:116`, "TPD4E05U06 is an ESD part (IEC 61000-4-2) with 5.5 V maximum pin voltage"). State: `design/sim/circuit/sim-notes.md:86` "simulated: VRING at no load is at most 5.280 V" and its line 86 "Not covered: a USB source far above 5 V on VBUS_IN". Also `design/wiring/lead-decisions.md:60` "The protection part on the ring supply line works up to 5.5 V" (this row is about the case; the ring shares the part).

Ring risk 4, antenna retune (`evidence/a5/sch-notes_before.md:117`, "retune on the ring (bench B4)"). State: open. `design/wiring/lead-decisions.md:67` "Simulated, not proven; the simulated antenna is a stand-in that failed its own validation". Search "retune|C13|bench B4" in the three state files: no settling line.

Ring risk 5, nPM pin numbers (`evidence/a5/sch-notes_before.md:118`, "nPM1300: pin numbers provisional"). The current ring files name the nPM1304: `design/ecad/ring/sch-notes.md:95` "The charger setting: 15 mA and 4.35 V on the nPM1304". The W1 section (`design/ecad/ring/sch-notes.md:304` "## W1 (2026-11-13): exact footprints, maker pin numbers, order codes") gives pin numbers for J1, X1, X2, U11, SW1 to SW5 and DISP1, not for the power chip. State: open for the power chip pins (search "nPM13" in the W1 section: only its lead-decision citations).

Ring risk 6, back-powering (`evidence/a5/sch-notes_before.md:119`, "Back-powering: when VDD_SD is off, U1 must not drive SD lines high"). Its own text says "Firmware rule." (`evidence/a5/sch-notes_before.md:119`) State: nothing found in the three state files.

Ring risk 7, VDD_3V0 load (`evidence/a5/sch-notes_before.md:120`, "VDD_3V0 load: motor 90 mA max plus the screen VCI"). Its own text: "Motor start current is not in the motor datasheet read here." State: partly simulated, `design/sim/circuit/sim-notes.md:62` "motor 17.14 ohm for 10 ms then 37.5 ohm for 70 ms" (the motor is modelled with a resistance, not a current from the datasheet). Motor datasheet: `design/datasheets/motor_3A-03208B.pdf` is a PDF with no text copy on disk; not read in this pass.

Ring risk 8, recording light (`evidence/a5/sch-notes_before.md:121`, "Recording light: Q2 gate is driven by VDD_MIC itself"). State: settled by removal. `design/ecad/ring/sch-notes.md:294` "## 13. v7 changes (2026-11-11): the recording light removed in v7, round joystick" and `design/wiring/lead-decisions.md:40` "which version v7 removed".

Ring risk 9, crystal X1 and load (`evidence/a5/sch-notes_before.md:122`, "Crystal X1 package pads and the crystal load"). State: the crystal lines are settled for clearance (`design/wiring/lead-decisions.md:76`, "The 0.20 mm clearance holds outside the main chip's ball field"). The load capacitance is not settled: search "load capac|crystal load" in the three state files: no hit. Maker: no text copy of the X1 crystal sheet on disk (search `design/datasheets/*.txt` for "load capacitance|CL =|load capacitor": no hit).

Ring risk 10, charger setting (`design/ecad/ring/sch-notes.md:95`, "until Grepow states the cell's own limit (open item S12)"). State: decision row set 15 mA and 4.35 V: `design/wiring/lead-decisions.md:13` "The charger is set to 15 mA and ends at 4.35 V." Still open: `design/mfg/specs/cell.md:44` "open item S12: Grepow confirms" and `design/sim/circuit/sim-notes.md:131` "Nothing in the bench or in the files fixes them". Maker: `design/sim/circuit/src/npm1304.txt:1427` "The charge current limit is set between 4 mA and 100 mA in 0.5 mA steps."

Ring risk 11, USB flex and U9 position (`design/ecad/ring/sch-notes.md:96`, "the VBUS ESD part U9 sits at the board end, not at the pads."). Conflict in the state files: `design/wiring/lead-decisions.md:15` "The protection part U9 sits on VBUS, D+ and D-." and `design/wiring/lead-decisions.md:75` "U9 is not moved." and "a 0.085 mm gap to U9's pads". These do not say the same place. Not reconciled here.

Ring risk 12, storage pads 1 and 7 (`design/ecad/ring/sch-notes.md:97`, "Confirm RSV pads tolerate a pull-up."). The pad map in use is the SD-mode map: `design/ecad/ring/sch-notes.md:36` "1 DAT2, 2 DAT3 = SDC_CS". The RSV names are the SPI-mode column of the maker sheet: `design/sim/circuit/src/slim2_cs-sdnand-20230403.txt:109` "RSV" (pin 1) and `:152` "RSV" (pin 7). Maker SD-mode table, `design/datasheets/slim_cs-sdnand-spec-sipeed.txt:235` "DAT2" and `:260` "DAT1"; footnote `:269` "The extended DAT lines (DAT1-DAT3) are input on power up." Pull-up: `design/sim/circuit/src/slim2_cs-sdnand-20230403.txt:485` "The host shall pull-up all DAT0-3 lines by RDAT, even if the host uses the SDNAND as 1-bit mode only in SD mode." (copy page 11, marker at line 475). State: partly settled by sim, `design/sim/circuit/sim-notes.md:112` "pull-up R63 (SD_DAT1) removed from both files", which tests the level shifter, not the pad. Search "pads 1 and 7|RSV" in lead-decisions and sim-notes: no settling line.

Ring risk 13, centre press (`design/ecad/ring/sch-notes.md:98`, "13. Centre press: SW2 under the centre of the round cap"). State: settled. `design/wiring/lead-decisions.md:44` "The centre press is ONE switch, SW2, under the cap's centre". Also `design/ecad/ring/sch-notes.md:87` "SW2 centre switch under the round joystick cap".

Case section 7 (`design/ecad/case/sch-notes.md:76` "## 7. Design risks an electronics engineer must review"):

Case risk 1, ESD on VRING (`design/ecad/case/sch-notes.md:78`, "TPD4E05U06 allows 5.5 V maximum on a pin"). State: simulated, `design/sim/circuit/sim-notes.md:86`, and `design/wiring/lead-decisions.md:60` (item 26 accepted: "at most 5.5 V" is measured by the builder). Maker: `design/sim/circuit/src/codes_tpd4e05u06.txt:458` "Input pin voltage" with `:459` "0", `:460` "5.5", `:461` "V" (recommended operating range, VIO 0 to 5.5 V).

Case risk 2, U2 D+/D- open (`design/ecad/case/sch-notes.md:79`, "TI's allowance for this is open item S5"). State: open. Search "S5" in `design/wiring/lead-decisions.md` and `design/sim/circuit/sim-notes.md`: no hit. Maker: `design/sim/circuit/src/case_bq25895.txt:323` "D+/D- based USB host/charging port detection."

Case risk 3, PMID load (`design/ecad/case/sch-notes.md:80`, "PMID load while charging from USB (supplier item S5)."). State: `design/sim/circuit/sim-notes.md:88` "cannot be simulated as a circuit". No lead decision (search "PMID" in lead-decisions: no hit).

Case risk 4, spring pins and 30 AWG (`design/ecad/case/sch-notes.md:81`, "Full-speed USB host over spring pins and 30 AWG wires; no series resistors on D+/D-."). State: `design/sim/circuit/sim-notes.md:89` "cannot be simulated with sources on disk". `design/wiring/lead-decisions.md:60` (item 92): "the ring is listed by the case's chip and 100 MB are copied without an error" is a test on the first case.

Case risk 5, strapping pins (`design/ecad/case/sch-notes.md:82`, "Strapping pins IO3, IO45, IO46 left open per the series datasheet (C2)."). State: `design/sim/circuit/sim-notes.md:90` "cannot be simulated: the pull states sit inside the module; no model". Maker: `design/sim/circuit/src/case_esp32s3_mini1.txt:917` "For the strapping" and `:918` "pin mapping between the chip and modules, please refer to Chapter 8 Module Schematics." Boot pins: `:922` "Strapping pin: GPIO0 and GPIO46", `:924` "Strapping pin: GPIO45", `:931` "Strapping pin: GPIO3". The module schematic (chapter 8) is not in the text copy.

Case risk 6, status light LED (`design/ecad/case/sch-notes.md:83`, "CLOSED by design (sim finding 3, section 9)"). State: closed by lead decision, `design/wiring/lead-decisions.md:31` "The case's status light takes its supply from the charger's system output SYS".

Case risk 7, TS window and JEITA (`design/ecad/case/sch-notes.md:84`, "check the JEITA window."). State: partly. `design/sim/circuit/sim-notes.md:72` "window 0.4825 to 0.7325". JEITA: search "JEITA" in `design/sim/circuit/src/case_bq25895.txt`: 0 hits. Open for the JEITA limits.

Case risk 8, charger enable CE (`design/ecad/case/sch-notes.md:85`, "CLOSED by design (sim finding 2, section 9): CE is pulled high by R21"). State: closed by lead decision, `design/wiring/lead-decisions.md:30` "The case's cell charger does not charge until its software has set it." Conflict: `design/sim/circuit/sim-notes.md:16` "CE is held low by R21, so charging starts without firmware" (the first finding text, not corrected in that file).

Case risk 9, TPS63802 MODE (`design/ecad/case/sch-notes.md:86`, "TPS63802 MODE on GND (power save) for low quiescent current"). State: `design/sim/circuit/sim-notes.md:94` "partly simulated". Maker: `design/sim/circuit/src/case_tps63802.txt:298` "Set LOW for power save mode, set HIGH for forced PWM mode." Ripple and load steps not simulated.

**3. Options per open sub-point** (no recommendation)

- Ring 1: (a) get the screen maker's power sequence (page 9 is not in the text copy `design/datasheets/slim_tailor-toh095xvt-01-p4-8.txt`); sch-notes section 9 stays open. (b) Write the order into firmware bring-up only; no ECAD change.
- Ring 2: (a) keep AVIN on its own 10 uF (no file change). (b) Join AVIN to PVIN (netlist change in `design/ecad/ring/make_netlist.py`).
- Ring 3: (a) keep the 5.5 V limit with the measurement in the build guide (no change). (b) Add an over-voltage clamp on VBUS (parts and netlist change).
- Ring 4: (a) keep retune as bench B4 (no change). (b) Retune before board round 3 (ring board files change).
- Ring 5: (a) confirm the nPM1304 pins against `design/datasheets/npm1304_datasheet_v1_0.txt` and close; the risk text names nPM1300. (b) Leave open.
- Ring 6: (a) firmware rule only (no file change). (b) Hardware gate on the SD lines (netlist change).
- Ring 7: (a) read the motor's start current from its sheet (PDF) and add it to the power sim. (b) Keep as written.
- Ring 9: (a) keep Nordic's no-external-load-capacitor rule (no change). (b) Add load capacitors (netlist change), after reading the crystal sheet.
- Ring 10: (a) keep 15 mA and 4.35 V; S12 stays open in `design/mfg/specs/cell.md:44`. (b) Change the charge settings in `design/mfg/specs/cell.md:40` to `:41` and the firmware charge step, if Grepow's limit differs.
- Ring 11: (a) keep U9 where routed (`design/wiring/lead-decisions.md:75`) and correct `design/ecad/ring/sch-notes.md:96` to match. (b) Move U9 to the board end and re-route the USB pair.
- Ring 12: (a) state that the SD-mode map applies (`design/ecad/ring/sch-notes.md:36`) and drop the SPI-mode RSV wording at line 97. (b) Keep the pull-ups the maker asks for (line 485) and confirm on the first card.
- Case 2: (a) leave S5 open; the charger then uses the CC reading (`design/ecad/case/sch-notes.md:79`), no file change. (b) Get the supplier answer and write it into `design/ecad/case/sch-notes.md`.
- Case 3: (a) keep the arithmetic in `design/sim/circuit/sim-notes.md:88`. (b) Measure PMID on the first case (bench).
- Case 4: (a) keep the first-case test (`design/wiring/lead-decisions.md:60`). (b) Add series resistors on D+/D- (case netlist change).
- Case 5: (a) keep open until the ESP32-S3-MINI-1 module schematic is read. (b) Add pulls on IO3, IO45, IO46 (case netlist change).
- Case 7: (a) read the JEITA limits from the BQ25895 sheet (no text copy: PDF `design/datasheets/case_bq25895.pdf`) and check the TS divider. (b) Keep as is.
- Case 8: (a) reconcile `design/sim/circuit/sim-notes.md:16` with the closed text (`design/ecad/case/sch-notes.md:85`); no circuit change. (b) Re-run the charger simulation.
- Case 9: (a) keep MODE on GND (power save, `design/sim/circuit/src/case_tps63802.txt:298`). (b) Tie MODE high for forced PWM (case netlist change).

## Item 95: straight lift-out and the C5c pictures

**1. Item text.** `design/wiring/deferred-triage.csv:96`: "Straight lift-out is not simulated; the other case pictures are C5c renders, not re-rendered."

**2. Sub-points and state today.**

(a) "not simulated". `design/case/c5d-open-points-handover.md:45`: "the straight lift out is not simulated as a motion." State: contradicted in the case files. `design/case/case-architecture.md:18` "test 17: lid open, ring lifted straight up in 0.25 mm steps until clear, every size". `design/case/case-notes.md:10` "Lift out simulated in 0.25 mm steps at every size (test 17)." Test code: `design/case/case_check.py:676` "the ring is lifted straight up (+Z) out of its seat in LIFT_STEP steps". Result: `design/case/r4/final_check.log:157` "17 pass line (fixed before the first run)"; `design/case/r4/final_check.log:160` "lifted 0 to 33.75 mm in 136 steps of 0.25 mm". Method: `design/case/case-model-r4-notes.md:59` "lifted along +Z in 0.25 mm steps". Lid at 100 degrees (same line). Search for a motion, sweep or continuous path in the case files: not run; the test is discrete steps.

(b) "the other case pictures are C5c renders, not re-rendered." `design/case/c5d-open-points-handover.md:46`: "The other pictures (side, underside, in-hand, compare) are the C5c renders; the outside did not change." Also `design/case/c5d-open-points-handover.md:14` names the renderer `case/look/render.py` and writes `case/look/case-closed.png` and `case/look/case-open.png` (US 9 seated). State: which pictures were re-rendered in C5d is not stated line by line. Search "render" in `design/wiring/lead-decisions.md`: no line for item 95. Nothing found that settles it.

(c) Decision rows: search "item 95|^| 95 " in `design/wiring/lead-decisions.md` and `design/wiring/w11-item-values.md`: nothing found.

**3. Documents on disk.** No maker document covers the lift-out. The check is a model.

**4. Options.** (a) Accept test 17 as the straight lift-out: edit the wording in `design/case/c5d-open-points-handover.md:45`; no model or picture change. (b) Keep "not simulated as a motion": add a continuous-motion check in `design/case/case_check.py` and re-run; no picture change. (c) Re-render the four pictures named in `design/case/c5d-open-points-handover.md:46` with `design/case/look/render.py`, after (a) or (b).

## Item 112: cast resin and the joystick pocket (K-A3)

**1. Item text.** `design/wiring/deferred-triage.csv:113`: "Cast resin dam and resin: the cast resin runs into the joystick pocket and locks the switches (K-A3)."

**2. Sub-points and state today.**

(a) Resin runs into the pocket, K-A3. `design/architecture.md:723` "K-A3: the cast resin would run into the joystick pocket and lock the switches; no dam is designed." Older text. Current: `design/mfg/assembly/assembly.md:331` "CHANGED: the dam DAM1 is a part of the model and the parts list". Still open: "its material (S26)" and "seals the pocket's edge only (K15" (same line 331). State: changed, not closed. Lead decisions: nothing found (search "dam|DAM1|K-A3" in `design/wiring/lead-decisions.md`: only item 101 at line 45, which says "The switches' own rating and the dam stay as they are").

(b) Dam seals the edge only (K15). `design/mech/thin/thin-notes.md:153` "K15 The dam closes the pocket round its edge only." Same line: "(my reading of the geometry, not measured)". `design/mfg/assembly/assembly.md:255` "under the head the liner's resin still reaches the stiffener". State: open. Search "dam|DAM1|K-A3|K-A12|K15" in `design/sim/circuit/sim-notes.md`, `design/ecad/ring/pcb/board-notes-r4.md`, `design/ecad/case/pcb/board-notes.md`, `design/wiring/lead-decisions.md`: one hit, `design/wiring/lead-decisions.md:45` "the dam stay as they are" (item 101, water rating; it does not settle the dam).

(c) Resin. `design/mfg/assembly/assembly.md:257` "### Step 21. Cast the resin liner" and its text: Master Bond EP30Med. `design/mfg/specs/band-liner.md:43` "Viscosity and cure time: not in a saved sheet". Maker: `design/datasheets/w12_masterbond-medical-device-applications.txt:37` "EP30Med: Optically clear, two component epoxy". Viscosity and cure time are not on that line. State: open for cure data.

(d) Dam material (S26). `design/architecture.md:524` "the dam of the joystick pocket (material not chosen)". `design/bom.csv:58` "S26: dam material and process; bench B9". State: open.

**3. Documents on disk.** No datasheet on disk for a dam material. `design/datasheets/w12_3m-dp420-copy-w11v-text.txt:68` "Epoxy Adhesive DP420 NS Black" (the floor-slot sealant, item 45; no "UV" in that file). `design/datasheets/w12_masterbond-medical-device-applications.txt:211` "UV curable adhesive formulated for TPU bonding" (UV17Med, a bonding adhesive; not named for the dam). No document covers the dam.

**4. Options.** (a) Keep step 20 as written (dam before cast) and choose a dam material: edit `design/bom.csv:58`, `design/mech/thin/placement.csv:39` and `design/mfg/assembly/assembly.md` step 20. (b) Cast the liner in two shots per the K-A12 proposal (`design/mfg/assembly/assembly.md:340`), with a removable plug above the stiffener: edit steps 20 and 21 and `design/mfg/specs/band-liner.md` item 9. (c) Drop the dam and seal the pocket with another part: changes the parts list (`design/bom.csv:58`) and `design/mech/thin/thin-notes.md:153`.

## Item 115: dam DAM1 standing on the liner (K-A12)

**1. Item text.** `design/wiring/deferred-triage.csv:116`: "Dam DAM1 is drawn standing on the liner but must exist before the cast; its material and how it stands are open (K-A12)."

**2. Sub-points and state today.**

(a) Drawn standing on the liner. `design/mech/thin/placement.csv:39` "frame on the liner". `design/bom.csv:58` "UV-cured dam frame on the liner round the switch head". State: as drawn. Step 20 text `design/mfg/assembly/assembly.md:251` "The dam material is not chosen" (see also 112(d)).

(b) Must exist before the cast. `design/mfg/assembly/assembly.md:340` "but it must exist BEFORE the liner is cast". `design/mfg/specs/band-liner.md:50` "the dam DAM1 of the joystick pocket come BEFORE the cast". State: open in the model, the drawing has it on the liner.

(c) Material. Not chosen: `design/bom.csv:58` "dispensed UV-cure dam"; `design/mech/thin/placement.csv:39` "UV-curing dam material PROPOSED in assembly.md step 20". State: open (S26). No lead decision (search "DAM1|dam material" in `design/wiring/lead-decisions.md`: none).

(d) How it stands. `design/mfg/assembly/assembly.md:253` "What holds the dam up before the liner exists is conflict K-A12." `design/mfg/assembly/assembly.md:340` "PROPOSAL: cast the liner in two shots". State: proposal only; `design/mfg/specs/band-liner.md:51` "The mechanical designer decides (S26)."

(e) Assembly table. `design/mfg/assembly/assembly.md:377` "Dam DAM1: material, and how it stands before the cast (K-A12)" with owner "the mechanical designer; bench B9". State: open.

**3. Documents on disk.** As for item 112 (no dam material sheet). The liner resin sheet is the Master Bond line above; the cure time is not in it.

**4. Options.** (a) Two-shot cast per K-A12 (`design/mfg/assembly/assembly.md:340`): edit steps 20 and 21 and `design/mfg/specs/band-liner.md` item 9; bom and placement stay. (b) Dam cast on a removable core before the liner (no two shots): edit steps 20 and 21, and `design/mech/thin/placement.csv:39` ("frame on the liner" to "frame on the core"). (c) Keep the dam on the liner as drawn and say so: edit `design/mfg/assembly/assembly.md:340` to show the conflict stays open.

RESULT: done, 4 items (27 with 13 ring and 9 case sub-points, 95, 112, 115) carry quotes checked in deferred-facts-verify.log; conflicts found: case risk 8 CE (sim-notes:16 vs case sch-notes:85), ring risk 11 U9 position, item 95 test 17 vs handover, and K-A3 architecture:723 vs the DAM1 model.
