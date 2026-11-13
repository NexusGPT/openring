# Design review 2: the AI recorder ring, whole design (independent)

Reviewer: judge helper, 2026-11-11, started 10:49 CET (first `date` of the run, saved in the shell output of the start command). I did not produce this design. Bar (lead, written before the work): S1 = cannot be built or cannot work as written, unsafe, or breaks an owner rule (record only on a long press of the joystick; a light visible whenever a microphone records; one control, no record button; sizes US 7 to 13). S2 = a builder must guess a build value, or two files give two values for one quantity and both read as current. S3 = smaller defects. The design passes only if no S1 finding is open. Owner's bar: "There should be no ambiguity to build it 100%".

Version judged: commit c64c4e6 of `.` (`git rev-parse --short HEAD` printed c64c4e6 at 10:49). The working tree differs from the commit only in design/case/ (in rework), firmware/ (new, out of scope), new datasheet PDFs and three plan files at the root (`git status --short` at the start). The case was read from the export given in the brief; its `case-architecture.md` is byte-equal to `git show c64c4e6:design/case/case-architecture.md` (`review-2/case-architecture_at_c64c4e6.md`, `cmp` printed "export-matches-commit"). Case findings below apply to the commit, not to the rework in progress. Later news from the lead: commit fd79dc2 changes four files only (`review-2/fd79dc2_stat.log`): design/status.json, make_one_pager.py and two explorer files. I read design/status.json in the working tree (`git status --short` lists no change to it, so it equals fd79dc2). It changes no finding; it adds evidence to G08 (K17). READ-FIRST.template.html, cited by G02, G03 and G09, is not in fd79dc2.

Logs, copies and fakes: `design/review/review-2/`. Paths are relative to the repository root; `CASE/` stands for `<scratch>/case-at-c64c4e6/design/case/`.

## 1. Verdict per area

| Area | Verdict | Why (finding ids) |
|---|---|---|
| Requirements coverage | buildable with declared gaps | The four owner rules hold in firmware and wiring (section 3 below, F05, F25). Not met and declared: P1, P2, A2, T1, S6, C3 (`requirements.md:182` to `requirements.md:204`). G11 (stale line). |
| Architecture consistency | not clean | G10 (section 2 still lists a record button, the nPM1300 and the joystick at +38 while it says it lists the current ring). Precedence rule resolves it, so S3. |
| Parts list | not buildable as written | G04 (pad size and pitch), G05 (joystick nub line), G13, G14 |
| Wiring diagram | not complete, although the package calls it complete | G09 (53 provisional pin numbers, RT1 place open) |
| Circuit board | not buildable (declared) | D1: placed, not routed, footprints PROVISIONAL, board file older than wiring A7 (G23) |
| Mechanics (inside model, exterior, body) | not buildable as written | G02 (screen cable does not fit), G03 (antenna pads off the board), both inside a model the package calls final; the 7-size fit check itself passes (`review-2/thin_v62_results.log`) |
| Maker files and drawings | buildable for shape | `check_parts.py` `RESULT PASS files=90`; G12 (stale status line) |
| Assembly order | not buildable as written | G06 (US 13 motor angle); declared conflicts K-A2, K-A5, K-A8, K-A12 (D11, D12) |
| Behaviour rules | buildable as written | owner rules hold; G16, G18, G22 are S3 |
| Charging case | not buildable as written | G01 (pins miss the ring's pads), G07 (which pin), G08 (US 7 and US 8 joystick); declared D4 (roll) |
| Software guides | buildable as a procedure; no code exists (declared D14) | `design/software/bring-up.md:9` "So nothing can be put on a ring today." |

Answer: no. As committed, a team cannot build a ring that charges in its own case (G01), cannot fit the named screen's cable (G02), and cannot solder the antenna where the model puts it (G03).

## 2. Findings

| Id | Sev | Area | Finding | Evidence (file:line, quoted) | Requirement |
|---|---|---|---|---|---|
| G01 | S1 | charging case | The case's four pins stand 1.0 mm from the band's middle along the finger; the ring's pads are centred on the band's middle (X 0.000). With a 1.6 mm pad (radius 0.8) and a 0.6 mm pin tip, the pin centre lands 0.2 mm off the pad's edge: no reliable contact, so the case cannot charge or read the ring. The case model checks pins against its own pads, which it places at the same offset, so its check passes. Not declared as open: the case notes record it as a decision. | `CASE/case.py:63` "PAD_X_OFF = -1.0                  # pad row 1.0 mm from the band's middle toward the light end"; `CASE/case-notes.md:33` "Pad row 1.0 mm from the band's middle toward the light end"; `design/mech/thin/placement.csv:45` "pad_VBUS,CP1,band,0.000,3.527" (column 4 is x, header line 1); `CASE/case-architecture.md:196` "a 0.6 mm pin tip" | C1, C4 |
| G02 | S1 | mechanics (inside model) | The named screen's cable is 12.4 mm wide where it folds; the inside model folds a 5.0 mm cable in a 5.4 mm pocket that does not exist on the part. Declared as open item S27, but the package calls the inside model final, so this blocks a final part. | `design/architecture.md:755` "A 12.4 mm fold does not fit beside the antenna. Open item S27."; `design/supplier-package/READ-FIRST.template.html:61` "Inside of the ring</td><td class=\"final\">3D final for assessment, 7 sizes" | D1, D6 (screen) |
| G03 | S1 | mechanics, circuit board | The antenna's four pads are off the board in the inside model, so it cannot be soldered as drawn. Declared (S15, K-A9), but it sits in the inside model the package calls final. | `design/architecture.md:513` "its 4 pads are off the board and cannot be soldered as drawn"; `design/mfg/assembly/assembly.md:99` "ANT1 stands in the corner notch and its pads are off the board, so it cannot be soldered"; READ-FIRST line 61 as above | T2 |
| G04 | S2 | parts list | The parts list gives the charging pads as 1.0 mm discs at 1.6 mm pitch; the flex spec, liner, inside model and case use 1.6 mm discs at 2.4 mm. Two current values for one part. | `design/bom.csv:66` "round pad,1.0 dia,gold pad 1.0 mm" and "4 pads, 1.6 mm pitch"; `design/mfg/specs/band-flex-tails.md:37` "charging pad diameter \| 1.6 mm"; `design/mfg/specs/band-flex-tails.md:38` "charging pad pitch \| 2.4 mm along the arc" | C4 |
| G05 | S2 | parts list | The joystick nub line keeps the 17.3 values: switches at 2.1 mm, a 5.0 mm opening, stack 3.1. The nub spec and model give 2.4 mm and an opening of 6.6 x 5.6. | `design/bom.csv:86` "switches in a cross at 2.1 mm from the centre" and "the seal of the 5.0 mm opening"; `design/mfg/specs/joystick-nub.md:34` "switch cross radius \| 2.4 mm"; `design/mfg/specs/body.md:93` "joystick opening 6.6 x 5.6" | D5 |
| G06 | S2 | assembly order | Step 7 places the motor pads at -39.5 degrees on US 13; the body spec and 17.27 put the US 13 motor at -42.5. The step also keeps a note that the motor clearance fix is "in work", closed by v6.2. | `design/mfg/assembly/assembly.md:138` "-39.5 at US 13"; `design/mfg/specs/body.md:90` "-47.0, -45.5, -44.0, -45.0, -43.5, -42.5, -42.5 degrees on US 7 to 13"; `design/mfg/assembly/assembly.md:43` "Open: the motor's free space to the body is under the lead's 0.05 mm rule" | S2 sizes |
| G07 | S2 | charging case | The case parts table names Mill-Max 0981 pins; the same file says the Harwin P70 is used, unconfirmed, with its stroke unknown. A builder cannot tell which pin to buy (review 1 F16). | `CASE/case-architecture.md:94` "\| P1-P4 \| Spring pins \| Mill-Max 0981-0-15-20-87-14-11-0 \|"; `CASE/case-architecture.md:31` "unchanged: Harwin P70-6000045R, proposed, not confirmed (K1)"; `CASE/case-architecture.md:190` "the stroke is NOT in the file read" | C4 |
| G08 | S2 | charging case | The case checks US 7 to 13 with the joystick at 78 degrees at every size; the ring puts it at 84 (US 7) and 81 (US 8). The case's fit at those two sizes is not proven. | `CASE/case.py:55` "JOY_ANGLE = 78.0"; `CASE/case-notes.md:41` "joystick at 78 degrees"; `design/mfg/specs/joystick-nub.md:31` "-78 deg (US 9 to 13); -81.0 (US 8); -84.0 (US 7)"; the status file still states the case fit as proven: `design/status.json:37` "its fit check passes for ring sizes US 7 to 13" | S2 sizes, C1 |
| G09 | S2 | wiring diagram | The package marks the wiring "complete" and final, but 53 pin numbers are provisional (including Q2's gate, source and drain, the light switch, and SW2, the record switch), and where RT1 sits is left to the owner. | `design/supplier-package/READ-FIRST.template.html:63` "Wiring diagram</td><td class=\"final\">complete"; `design/ecad/ring/sch-notes.md:60` "53 provisional pin numbers"; `design/ecad/ring/open-pins.csv:50` "Q2,G,G,\"datasheet DS40239 p1 names terminals D, S, G but prints no pad numbers\""; `design/bom.csv:79` "the owner must say whether RT1 sits on the cell (17.3) or on the main board (W13)" | U5, U6 |
| G10 | S3 | architecture | Section 2 says it lists the current ring but keeps the nPM1300, the joystick at +38 and a record button at +62. The precedence rule (line 3) and 17.11 and 17.13 override it. | `design/architecture.md:36` "This table is at A5: it lists the parts of the current ring (section 17)."; `design/architecture.md:45` "\| Power chip \| nPM1300, WLCSP package"; `design/architecture.md:48` "\| Record button \| 1 x SKTAAAE010 under its own cap, on the band at +62 degrees"; `design/architecture.md:544` "- Record button: removed." | owner rule: one control |
| G11 | S3 | requirements | Change item 19 still says the charger cannot go below 32 mA and is an open choice; item 14 says the nPM1304 is set to 15 mA. | `requirements.md:200` "the nPM1300 cannot go below 32 mA, so the charger part is an open hardware choice"; `requirements.md:195` "The power chip is now the nPM1304 (architecture 17.13), set to 15 mA" | C3 |
| G12 | S3 | maker files | The body spec says at its head that the body files carry every pocket, and further down that they are outer shape only. | `design/mfg/specs/body.md:5` "The body files carry every inside pocket since 2026-11-11"; `design/mfg/specs/body.md:105` "Status in that index: outer shape only, cavities not cut" | bar |
| G13 | S3 | parts list | The parts list keeps positions from earlier models: the protection circuit at -35 to -27 degrees and the joystick frame at 78 degrees for every size. | `design/bom.csv:53` "17.10 put it from -35 to -27 degrees"; `design/mfg/specs/cell.md:36` "43.8 deg (US 7), 41.5 deg (US 8), 39.5 deg (US 9 to 13)"; `design/bom.csv:56` "joystick frame 6.4 x 5.4 on the outer face at 78 degrees on the joystick side" | bar |
| G14 | S3 | parts list | The board line says 15 test pads (22 exist), and the TP16 to TP19 line describes all four as the pad of spare pin P3.05; TP17 is VDD_1V8, TP18 GND, TP19 SHPHLD. | `design/bom.csv:54` "15 test pads"; `design/bom.csv:80` "W12 test pad for the 11th spare pin P3.05"; `design/ecad/ring/netlist.csv:329` "VDD_1V8,TP17"; `design/ecad/ring/netlist.csv:249` "SHPHLD,TP19" | bar |
| G15 | S3 | charging case | The case's ring-charge text keeps the 15 to 20 mAh cell and the 32 mA minimum. | `CASE/case-architecture.md:114` "The ring's charger draws 15 to 20 mA x 4.35 V"; `design/architecture.md:789` "The charge current stays 15 mA: 0.85 C of 17.6 mAh" | C2 |
| G16 | S3 | behaviour rules | The firmware still says it follows case version C1; the case is C5b. RT1's place stays open in H12 (review 1 F23). | `design/firmware.md:3` "`design/case/case-architecture.md` version C1"; `CASE/case-architecture.md:1` "(version C5b)"; `design/firmware.md:1042` "\| H12 \|" | bar |
| G17 | S3 | check `check_bom.py` | The check passes a parts list with a separate record button added back (fake B1) and one with 9.9 mm pads at 7.7 mm pitch (fake B3). It caught the removed light transistor (B2). | `review-2/fakes/fakes_results.log` lines "B1 ... got PASS (exit 0)", "B3 ... got PASS (exit 0)", "B2 ... got FAIL (exit 1)" | owner rule: one control |
| G18 | S3 | check `firmware-check.py` | The check passes a firmware file in which Bluetooth opcode 0x02 starts a recording (fake W3). It caught the long press that keeps recording (W1, review 1 F25), a short press that starts (W2), VDD_MIC on in standby (W4) and an unknown state (W5). The real file is right: `design/firmware.md:683` "Bluetooth cannot start or stop a recording". | `review-2/fakes/fakes_results.log` "W3 ... got PASS (exit 0)" | owner rule: long press only |
| G19 | S3 | check `check_docs.py` | The check passes a spec with a stale value that still stands somewhere in architecture.md (nub cross radius 2.1, fake S2; pad pitch 1.6, fake S4), and reads only the "Critical dimensions" table (my first pad-pitch fakes S1 and S3 edited another liner table and passed; the real check run on that cause is `review-2/fakes/S3_check_docs.log`, `RESULT PASS`). Control S5 (7.77, in no source) fails. | `review-2/fakes/fakes_results.log` "S2 ... got PASS (exit 0)"; `review-2/fakes/fakes_results_2.log` "S4 ... got PASS (exit 0)", "S5 ... got FAIL (exit 1)" | bar |
| G20 | S3 | requirements | No weight estimate exists (review 1 F19). | `design/architecture.md:822` "Weight is not stated: no mass estimate exists for this ring." | S5 |
| G21 | S3 | bench plan | The bench plan still wires only two joystick directions (review 1 F18). | `design/bench/bench-plan.md:48` "two push buttons to ground (the ring's 2-direction thumb control)" | D5, A8 |
| G22 | S3 | behaviour rules | Only firmware stops the microphone clock from back-powering the microphones while VDD_MIC, and so the light, is off; it needs a driver change (review 1 F30). | `design/firmware.md:411` "**MIC_A_CLK is driven low whenever VDD_MIC is off**" and "applying the sleep state at stop and at boot is a driver change" | U6 |
| G23 | S3 | circuit board | The board notes and file describe a board older than wiring A7: tail pad groups 6 and 9 (wiring 8 and 7), U2 as 33 pins, the 2.8 x 0.6 joystick notch the spec dropped. The board is declared not routed (D1). | `design/ecad/ring/pcb/board-notes.md:24` "J_BAND_A (6 pads) and J_BAND_B (9 pads)"; `design/ecad/ring/pcb/board-notes.md:43` "U2 (33 pins P1 to P33"; `design/ecad/ring/pcb/board-notes.md:22` "notch 2.8 x 0.6 on the +Y edge"; `design/mfg/specs/main-board.md:33` "joystick notch \| 0 (none)" | bar |

### Owner rules: where they hold (searched, no finding)

- Long press only: `design/firmware.md:144` "\| `STANDBY` \| long press of the joystick centre \| `RECORDING` \| open; M1 \|" and `design/firmware.md:198` "Only a long press of the joystick centre starts or stops a recording". The check now enforces it (fakes W1, W2 fail).
- Light whenever a microphone records: VDD_MIC comes only from U2 ball A4 and drives Q2's gate (`design/ecad/ring/netlist.csv:351` "VDD_MIC,Q2,G,G,input", `design/ecad/ring/netlist.csv:352` "VDD_MIC,U2,A4,LSOUT1/VOUTLDO1,power_out"); VDD_3V0 is on in every awake state (`design/firmware.md:770` row `RECORDING` "on \| on \| on \| on"). Whether the light can be SEEN is declared unproven (D3).
- One control: `design/mfg/specs/record-cap.md:3` "This part does not exist."; `design/architecture.md:544` "- Record button: removed." Only section 2's stale row disagrees (G10).
- Sizes US 7 to 13: `requirements.md:22` "7 sizes, US 7 to 13"; seven body files (`design/mfg/parts/index.csv` rows body 7 to 13); every size passes the saved fit logs (`review-2/thin_v62_results.log`: US 7, 8 and the US 9 default `RESULT PASS pairs=1175 parts=49`; US 10 to 13 `RESULT PASS pairs=1127 parts=48`). Not checked in the case at US 7 and 8 (G08).

## 3. Status of review 1 findings F01 to F30

| Id | Status | Evidence |
|---|---|---|
| F01 | closed (position and window); visibility declared open (D3) | `design/architecture.md:688` "Window: round, 0.4 mm, in the black print of the cover glass at X -12.425, Y -2.95"; `design/mfg/specs/cover-glass.md:41` "recording light window \| dia 0.4 mm, at X -12.425, Y -2.95" |
| F02 | closed | `design/architecture.md:652` "Part: 2 x Knowles SPK0641HT4H-1, top port"; `design/bom.csv:9` "top port facing down through the floor" |
| F03 | closed | `design/architecture.md:555` "They sit in the resin liner, not in the metal body"; `design/mfg/specs/body.md:82` "charging pad holes \| 0 (none)" |
| F04 | partly closed | wiring: `design/architecture.md:574` "8 pads on the joystick side's cable (J_BAND_A: joystick switches, centre switch, motor)", `review-2/check_netlist.log:34` "J_BAND_A 8 pads and J_BAND_B 7 pads"; the board file still has 6 and 9 (G23) |
| F05 | closed | `design/firmware.md:741` "on whenever VBUS is present"; `design/architecture.md:565` "`CHARGE_CURRENT` = 15 mA" |
| F06 | open, declared (D2) | `design/architecture.md:674` "NOT DECIDED: the fix changes the ring's look, which is the owner's decision." |
| F07 | closed in the wiring; board lacks U10 (D1) | `design/architecture.md:573` "a level shifter is added: U10, Texas Instruments SN74AXC4T774RSVR" |
| F08 | closed | `requirements.md:22` "7 sizes, US 7 to 13"; `design/architecture.md:608` "Version 1 has 7 sizes, US 7 to 13" |
| F09 | closed for US 7 to 13 (US 5 and 6 dropped) | `review-2/thin_v62_results.log` (seven sizes `RESULT PASS`); `design/architecture.md:781` "\| US 7 \| -84.0 deg \| -47.0 deg \| 33.936 mm" |
| F10 | closed as a document; conflicts inside it declared (D11, D12) | `design/architecture.md:714` "28 steps, each with what is joined" |
| F11 | closed as a statement; rating declared not met (D5) | `requirements.md:204` "S6 Water and dust, IP65 or better: NOT MET ON PAPER" |
| F12 | closed | `requirements.md:198` "the recessed button no longer exists; U3 is carried by the joystick's centre press and by firmware instead" |
| F13 | closed | `design/architecture.md:77` "REPLACED by section 17.13 (4.35 V, 15 mA, the band cell). Do not use" |
| F14 | partly closed (grid named; pitch open to Nordic, D10; board footprint still the old reading) | `design/architecture.md:575` "the ball pitch is open to Nordic"; `design/ecad/ring/pcb/board-notes.md:42` "Two project sources disagree" |
| F15 | closed | `design/mfg/specs/body.md:90` "Floor slots 2.0 x 0.6 at Y = +-5.9, from X = -3.5 to X = -1.5" |
| F16 | open (G07) | `CASE/case-architecture.md:94` "Mill-Max 0981-0-15-20-87-14-11-0" |
| F17 | partly closed (motor, record switch, cell fixed; pads, nub, protection circuit stale: G04, G05, G13) | `design/bom.csv:44` "at -44 degrees"; `design/bom.csv:66` "1.0 dia" |
| F18 | open (G21) | `design/bench/bench-plan.md:48` "two push buttons to ground" |
| F19 | open (G20) | `design/architecture.md:822` "Weight is not stated" |
| F20 | partly closed (cell, motor, light, microphone rows updated; nPM1300, +38 joystick, record button rows stay: G10) | `design/architecture.md:49` "W0525AB001D"; `design/architecture.md:48` "Record button" |
| F21 | closed | `design/mfg/specs/main-board.md:39` "board fill, populated area \| 72 percent" |
| F22 | partly closed (spec fixed; board notes keep the notch, G23) | `design/mfg/specs/main-board.md:33` "joystick notch \| 0 (none)"; `design/ecad/ring/pcb/board-notes.md:22` "notch 2.8 x 0.6" |
| F23 | open (G16) | `design/firmware.md:3` "version C1"; `design/firmware.md:1042` "\| H12 \|" |
| F24 | open, declared (D8); the C5b case text no longer states a nub height (search for "proud" in CASE/case-architecture.md and CASE/case.py: one hit, the lid pin, line 198) | `design/mfg/specs/joystick-nub.md:57` "the design partner confirms" |
| F25 | closed (the check now fails the same fake) | `review-2/fakes/W1_firmware-check.log` "FAIL a long press in RECORDING must go to STANDBY and close the recording" |
| F26 | closed | `review-2/check_netlist.log:34` "ok   A6-9 J_BAND_A 8 pads and J_BAND_B 7 pads equal the BAND_SPLIT table" |
| F27 | partly closed (size and place given; limits open, D7) | `design/mfg/specs/cell.md:36` "protection circuit start"; `design/bom.csv:53` "thresholds not stated in the architecture" |
| F28 | closed | `design/bom.csv:48` "820 ohm 1 %" with "820 ohm gives 1.502 mA" |
| F29 | closed (part removed) | `design/mfg/specs/record-cap.md:3` "This part does not exist." |
| F30 | open (G22) | `design/firmware.md:411` "MIC_A_CLK is driven low whenever VDD_MIC is off" |

Counts: closed 17 (F02, F03, F05, F08, F09, F12, F13, F15, F21, F25, F26, F28, F29, plus F01, F07, F10, F11 closed with a declared remainder); partly closed 6 (F04, F14, F17, F20, F22, F27); open 7 (F06, F16, F18, F19, F23, F24, F30).

## 4. Declared open (the design says these are open)

| Id | Item | Where declared | My severity | Counts as a finding? |
|---|---|---|---|---|
| D1 | Circuit board placed, not routed; PROVISIONAL footprints; no U10, U11 and others in the board file | `design/ecad/ring/pcb/board-notes.md:1` "Placed, not routed."; `design/architecture.md:512` S14; READ-FIRST "not routed" | S1 | no (declared, not called final); its stale content is G23 |
| D2 | Antenna under metal; no radio figure; owner decides the resin corner | `design/architecture.md:674`; S24 at `design/architecture.md:522` | S2 | no |
| D3 | Brightness of the light at the window unproven (estimate 0.08 to 3.8 mcd) | `design/architecture.md:693` "NOT PROVEN: how bright the window is." | S1 (owner rule: visible) | no (declared, bench) |
| D4 | Case does not hold the ring's roll to the pad tolerance | `CASE/case-architecture.md:196` "So the roll is NOT held to the pad's tolerance" | S1 | no (case is "draft" in READ-FIRST) |
| D5 | Water and dust: no rating can be claimed; seals not chosen | `requirements.md:204`; `design/architecture.md:729` | S2 | no |
| D6 | No rescue mode; a broken start program means a scrapped ring | `design/architecture.md:526` S28; `design/mfg/assembly/assembly.md:125` "a broken boot loader after step 17 means a scrapped ring" | S2 | no |
| D7 | The curved cell does not exist; charge and discharge limits, protection limits unknown (motor start up to 228 mA) | `design/architecture.md:508` S12; `design/firmware.md:1037` H7 "open" | S1 | no |
| D8 | Joystick nub height above the frame not given | `design/mfg/specs/joystick-nub.md:57` | S2 | no |
| D9 | Case pin stroke unknown | `CASE/case-architecture.md:215` S4 | S2 | the parts-table contradiction is G07 |
| D10 | Main chip ball pitch, A1 corner | `design/ecad/ring/sch-notes.md:168` "Open point O5" | S2 | no |
| D11 | Liner build: dam must exist before the cast (K-A12), ribbons embedded 0.075 mm (K-A5), floor slot sealant (K-A2) | `design/mfg/assembly/assembly.md:330`, `:323`, `:320`; S26 at `design/architecture.md:524` | S2 | no |
| D12 | Cell live during the cast, heat limit unknown | `design/mfg/assembly/assembly.md:326` "OPEN: no source states the limit (S12)." | S2 (safety, unmeasured) | no |
| D13 | Board thickness 0.28 in the STEP against 0.3 | `design/mfg/specs/main-board.md:61` | S3 | no |
| D14 | No software exists | `design/software/bring-up.md:9`; READ-FIRST "specified, not written" | S1 | no |
| D15 | Ring charge time under 90 minutes unproven | `requirements.md:195` "C3 Ring charge time, under 90 minutes: UNPROVEN." | S3 | no |
| D16 | Screen connector pitch, switch land pattern (S8, S9) | `design/bom.csv:11`, `design/bom.csv:39` | S2 | no |
| D17 | Screen cable width (S27) and antenna mount (S15) | `design/architecture.md:525`, `:513` | S1 | yes: they block the inside model the package calls final (G02, G03) |

## 5. Contradictions (one quantity, two values, both read as current)

| # | Quantity | Value A | Value B |
|---|---|---|---|
| K1 | charging pad diameter and pitch | `design/bom.csv:66` "1.0 dia", "1.6 mm pitch" | `design/mfg/specs/band-flex-tails.md:37` "1.6 mm", `:38` "2.4 mm along the arc" |
| K2 | pad row along the finger | `CASE/case.py:63` "PAD_X_OFF = -1.0" | `design/mech/thin/placement.csv:45` x "0.000" |
| K3 | joystick switch cross radius | `design/bom.csv:86` "2.1 mm" | `design/mfg/specs/joystick-nub.md:34` "2.4 mm" |
| K4 | joystick opening | `design/bom.csv:86` "5.0 mm opening" | `design/mfg/specs/body.md:93` "6.6 x 5.6" |
| K5 | US 13 motor angle | `design/mfg/assembly/assembly.md:138` "-39.5 at US 13" | `design/mfg/specs/body.md:90` "-42.5 degrees on US 7 to 13" (last value of the list) |
| K6 | case spring pin | `CASE/case-architecture.md:94` "Mill-Max 0981" | `CASE/case-architecture.md:31` "Harwin P70-6000045R" |
| K7 | joystick angle on US 7 and 8 | `CASE/case.py:55` "78.0" | `design/mfg/specs/joystick-nub.md:31` "-81.0 (US 8); -84.0 (US 7)" |
| K8 | protection circuit position | `design/bom.csv:53` "-35 to -27 degrees" | `design/mfg/specs/cell.md:36` "39.5 deg (US 9 to 13)" |
| K9 | body files cut or not | `design/mfg/specs/body.md:5` "carry every inside pocket" | `design/mfg/specs/body.md:105` "cavities not cut" |
| K10 | state of the wiring | READ-FIRST line 63 "complete" | `design/ecad/ring/sch-notes.md:60` "53 provisional pin numbers" |
| K11 | lowest charge current | `requirements.md:200` "cannot go below 32 mA" | `requirements.md:195` "set to 15 mA" |
| K12 | record button | `design/architecture.md:48` "Record button" row | `design/architecture.md:544` "Record button: removed." |
| K13 | number of test pads | `design/bom.csv:54` "15 test pads" | `design/bom.csv:55`, `:80`, `:87`: TP1 to TP22 |
| K14 | RT1 place | `design/architecture.md:292` "on the main board beside the cell" | `design/bom.csv:79` "on the cell, wired in flex tail 2" |
| K15 | tail pad counts | `design/ecad/ring/pcb/board-notes.md:24` "6 pads", "9 pads" | `design/bom.csv:81` "= 8 pads", `design/bom.csv:82` "= 7 pads" |
| K17 | case fit at US 7 and 8 | `design/status.json:37` "its fit check passes for ring sizes US 7 to 13" | `CASE/case.py:55` "JOY_ANGLE = 78.0" against `design/mfg/specs/joystick-nub.md:31` "-84.0 (US 7)" |
| K16 | ring cell in the case text | `CASE/case-architecture.md:114` "15 to 20 mA" | `design/architecture.md:789` "17.6 mAh" |

## 6. What I did not read or could not check

- Read in part only: `design/architecture.md` sections 1 to 15 (read, judged by the precedence rule); `design/firmware.md` (searched by topic; read in part, not in full); `design/ecad/ring/parts.csv`, `symbols.csv`, `additions.csv` (not read row by row); `design/mech/thin/thin-notes.md` sections before "Model v6, continued" (headings only); the four studies (their RESULT lines, `review-2/studies_result_lines.log`); `design/software/factory-package.md` and `design/firmware-f6-notes.md` (RESULT line only); `CASE/case-bom.csv` (not read).
- Not opened: the PDF and SVG drawings, the STEP, STL and GLB files, the KiCad schematic and board, `design/ecad/case/`. Reason: 90-minute limit and no 3D builds allowed. I read the saved model logs instead (`review-2/thin_v62_results.log`); I did not run thin.py, check_thin.py, exterior.py or case.py.
- G01 rests on the files' coordinates (case.py and placement.csv), not on a run of the case model against the ring's own pads. A pin tip of 0.6 mm is the case file's own figure.
- `check_netlist.py` writes `ring-kicad.xml` and an evidence log in its own folder, so I ran it on a copy in `review-2/sandbox/` (KiCad export from the copied schematic): `RESULT PASS netlist netlist.csv`, exit 0. The sandbox links architecture.md, bom.csv, parts/, mech/ and datasheets/ read-only.
- No datasheet was read except the nPM1304 ship-mode exit (`design/datasheets/npm1304_datasheet_v1_0.txt:9084` "Applying a voltage on VBUS > VBUSPOR."), which supports the VBUS wake.
- Nothing was built or measured.

Checks run (each log in review-2/; last line quoted): `check_bom.py` "exit=0" (line before: "lines 86, designators 140, section-2 rows 21, section-2 part tokens 25, failures 0"); `firmware-check.py` "exit=0" ("0 failures"); `check_docs.py` "exit=0" ("RESULT PASS"); `check_parts.py` "exit=0" ("RESULT PASS files=90"); `check_netlist.py` (sandbox) "exit=0" ("RESULT PASS netlist netlist.csv"). Fakes: 13 faulty copies over two runs; 7 passed a check that should have failed them (B1, B3, W3, S1, S2, S3, S4; S1 and S3 because the edited table is not read, G19), 6 were caught (B2, W1, W2, W4, W5, S5). Run 1 predictions differed from results on W1, W2, W4 (I expected the old weakness; the check is stronger now) and S3 (cause found: the edited row is outside the checked table).

## 7. Counts

Findings: 23 (G01 to G23). S1: 3 (G01, G02, G03). S2: 6 (G04 to G09). S3: 14 (G10 to G23). Declared open: 17 (D1 to D17), of which D17 is counted as G02 and G03. Contradictions: 17 (K1 to K17). Review 1: 17 closed, 6 partly closed, 7 open.

RESULT: done, the design does not pass: S1 3, S2 6, S3 14 open findings (the case pins miss the ring's pads; the screen cable and the antenna mount block the inside model called final).
