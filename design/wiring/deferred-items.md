# Deferred items: design files of the ring recorder and its charging case

Scope: text files under `design/` (minus the folders the brief names) and `requirements.md`. From `design/firmware.md` only the section "Hardware issues found" (lines 1176 to 1201). Working files (raw hit lists) sit in the session scratchpad, not in the project.

Kinds used: left to a person; value open; value assumed; footprint or pin map provisional; needs a maker's answer; needs hardware to measure; drawing or file missing.

## Part 1. Open items

| No | Subject | Item | Kind | Where (file:line) | Quote (from that line) |
|---|---|---|---|---|---|
| 1 | ring circuit board | Board is placed but not routed: 225 connections have no track. | left to a person | design/ecad/ring/pcb/build_board.py:2; design/ecad/ring/pcb/board-notes.md:31; design/architecture.md:512; design/mfg/assembly/assembly.md:90 | `1. Route everything (225 connections).` |
| 2 | ring circuit board | Antenna mount: ANT1 pads sit off the board in the corner notch and cannot be soldered as drawn. | left to a person | design/architecture.md:513; design/ecad/ring/pcb/board-notes.md:33; design/mfg/assembly/assembly.md:326 | `The mount needs a decision (this is the largest open item).` |
| 3 | ring circuit board | Antenna keep-out is drawn only on a drawing layer, not as a rule area; the J1 pads reach into it. | left to a person | design/ecad/ring/pcb/board-notes.md:32 | `is drawn on Dwgs.User only, centred on ANT1, not as a rule area.` |
| 4 | ring circuit board | Length and impedance rules for USB D+/D- and the screen bus are not set. | left to a person | design/ecad/ring/pcb/board-notes.md:34 | `have none set. None is in a project file.` |
| 5 | ring circuit board | U5 and U6 courtyards leave the board outline (declared exceptions). | left to a person | design/ecad/ring/pcb/board-notes.md:35 | `so their courtyards leave the outline` |
| 6 | ring circuit board | Joystick notch was placed for the old joystick position; whether it stays is not settled. | left to a person | design/ecad/ring/pcb/board-notes.md:36 | `architecture 17.8 moved the joystick to the bottom of the band` |
| 7 | ring circuit board | Board stack: copper 0.012 mm and equal dielectric split are assumed; the fab and layout engineer must confirm. | value assumed | design/ecad/ring/pcb/build_board.py:489; design/ecad/ring/pcb/build_board.py:491; design/ecad/ring/pcb/board-notes.md:31 | `ASSUMED copper 0.012` (489); `fab and layout engineer to confirm` (491) |
| 8 | ring circuit board | Board outline corner radius 0.8 mm is assumed. | value assumed | design/ecad/ring/pcb/board-notes.md:22 | `corner radius 0.8 (ASSUMED` |
| 9 | ring circuit board | U1 ball names (8 x 10 grid) disagree with placement.csv (9 x 7 less 2 corners); the names used are not settled. | value open | design/ecad/ring/pcb/build_board.py:493; design/ecad/ring/pcb/board-notes.md:42 | `which disagrees with placement.csv's '9 x 7 grid less 2 corners'` (493); `Two project sources disagree; I used the names` (42) |
| 10 | ring circuit board | Places of U11, C83 and C84 on the board are still to be set. | left to a person | design/mfg/assembly/assembly.md:368; design/mfg/specs/main-board.md:62 | `Places of U11, C83, C84 on the board` |
| 11 | ring circuit board | Board surface finish and solder-mask colour are not stated; finished thickness and layer count still open (points 2 and 3). | value open | design/mfg/specs/main-board.md:18; design/mfg/specs/main-board.md:29 | `surface finish and solder-mask colour are not stated` |
| 12 | ring circuit board | 0.50 mm non-plated hole is not drawn on the board; its hole-to-copper rule is open. | left to a person | design/ecad/ring/v7-wiring-notes.md:58; design/mech/light-path/light-path.md:120 | `is not drawn in` (v7-wiring-notes 58); `the hole-to-copper rule for a 0.5 non-plated hole` (light-path 120) |
| 13 | ring circuit board | Footprints drawn as PROVISIONAL: U1, U2, U3, U4, U5, U6, ANT1, J1, L10, L71, L72, J_BAND_A and J_BAND_B (pitch or pin numbers not on disk). | footprint or pin map provisional | design/ecad/ring/pcb/build_board.py:199, 206, 212, 221, 227, 233, 239, 245, 250, 271; design/ecad/ring/pcb/provisional-footprints.json:2-14; design/ecad/ring/pcb/board-notes.md:42-47 | `PROVISIONAL: pitch 0.325 and ball dia 0.20 from placement.csv` (199) |
| 14 | ring circuit board | Pin maps marked PROVISIONAL: X1, X2, Q1, Q2 and LED1. LED1 pad 1 is the KiCad cathode, but the netlist puts P1 as the anode. | footprint or pin map provisional | design/ecad/ring/pcb/build_board.py:69, 70, 72; design/ecad/ring/pcb/board-notes.md:48 | `PROVISIONAL, KiCad LED pad 1 = cathod` (70) |
| 15 | ring circuit board | U9 and the 0201, 0402, 0603 and other library parts are not checked against a maker drawing. | drawing or file missing | design/ecad/ring/pcb/board-notes.md:49 | `Not verified against a maker drawing: U9` |
| 16 | ring circuit board | Orientation of the SGMICRO part (U4) A1 is not read from its drawing. | drawing or file missing | design/ecad/ring/pcb/build_board.py:498; design/ecad/ring/pcb/board-notes.md:44 | `orientation of A1 not read from the SGMICRO drawing` |
| 17 | ring circuit board | The sound port in the -Y wall of the microphone footprint is not drawn. | drawing or file missing | design/ecad/ring/pcb/build_board.py:503 | `the sound port in the -Y wall is not drawn` |
| 18 | ring circuit board | Flex tail connector pads on this board are a pad group only; the flex tail and its connector are not drawn. | drawing or file missing | design/ecad/ring/pcb/build_board.py:514 | `PROVISIONAL: pad group only` |
| 19 | ring circuit board | Power chip balls LED0 to LED2 are left open. | value open | design/ecad/ring/make_netlist.py:33 | `(all left open)` |
| 20 | ring circuit board | Main chip ball pitch is open to Nordic (review finding F14); the CAAA package drawing is needed (sch-notes O5). | needs a maker's answer | design/architecture.md:577; design/ecad/ring/sch-notes.md:191 | `the ball pitch is open to Nordic (review finding F14)`; `ball pitch, ball diameter, A1 corner and orientation of the CAAA package` (sch-notes 191) |
| 21 | ring circuit board | nPM1304 ball map equals the nPM1300 map: not confirmed and must not be assumed (sch-notes O1, S18); orderable part number left empty. | needs a maker's answer | design/architecture.md:568; design/ecad/ring/sch-notes.md:187; design/bom-notes.md:73 | `What is NOT confirmed and must not be assumed` (568); `nPM1304 ball map against the nPM1300` (sch-notes 187) |
| 22 | ring circuit board | State of the main chip's USB D- and D+ pads when VBUS is absent: no source in the project (sch-notes O4). | needs a maker's answer | design/ecad/ring/sch-notes.md:190 | `state of the main chip's USB D- and D+ pads when VBUS is absent` |
| 23 | ring circuit board | Level shifter U10 choice (sch-notes O3): keep it, or move the main chip VDD to 3.0 V; price and stock of SN74AXC4T774RSVR not read. | left to a person | design/ecad/ring/sch-notes.md:189; design/ecad/ring/sch-notes.md:163 | `the level shifter U10 against the alternative of moving the main chip's VDD` (189); `Open point O3: the lead confirms this choice` (163) |
| 24 | ring circuit board | VDD_SD storage supply carries 5.9 uF; the Zetta limit of 5 uF is another maker's part and the CSNP32 limit is not read (sch-notes O9). | value open | design/ecad/ring/sch-notes.md:277 | `VDD_SD now carries C60 4.7 uF, C61, C82 100 nF and C87 1.0 uF = 5.9 uF.` |
| 25 | ring circuit board | Microphone decoupling C31, C32 (1 uF X5R) on VDD_MIC against the Class 1 rule (sch-notes O10); C35 and C36 must be Class 1 (bom-notes). | value open | design/ecad/ring/sch-notes.md:278; design/bom-notes.md:84 | `C31, C32 1 uF X5R on VDD_MIC against Knowles` (278); `C35,C36 must be Class 1 dielectric` (84) |
| 26 | ring circuit board | ESD part TPD4E05U06 allows 5.5 V maximum on VRING; U2 D+ and D- are open (design risks 1 and 2). | value open | design/ecad/case/sch-notes.md:78; design/ecad/case/sch-notes.md:79 | `ESD part on VRING: TPD4E05U06 allows 5.5 V maximum on a pin.` (78) |
| 27 | ring circuit board | Six design risks are listed for an electronics engineer to review (sch-notes section 7 and 9). | left to a person | design/ecad/case/sch-notes.md:76; design/ecad/ring/sch-notes.md:91 | `## 7. Design risks an electronics engineer must review` |
| 28 | ring circuit board | Open point O12: the VSYS ball C2 is typed passive in the symbol (cause not read in full). | value open | design/ecad/ring/sch-notes.md:280 | `VSYS ball C2 is typed passive in the symbol` |
| 29 | band and its wiring | Which flex tail carries the motor (BAND_SPLIT), and any later move of a line (sch-notes O2); the lead confirms the split after the inside model is rebuilt. | left to a person | design/ecad/ring/sch-notes.md:188; design/ecad/ring/check_netlist.py:361; design/ecad/ring/open-pins.csv:23 | `which tail carries the motor` (188); `confirmation of the motor's tail is left open` (361) |
| 30 | band and its wiring | Tail routes of both flex tails (S16) are not settled; the ribbons are not routable as drawn. | value open | design/architecture.md:537; design/mfg/specs/band-flex-tails.md:58 | `Flex ribbons: not routable as drawn (open item S16).` |
| 31 | band and its wiring | J_BAND_A and J_BAND_B pad numbers are the schematic's own order, not the maker's pin numbers. | footprint or pin map provisional | design/ecad/ring/make_netlist.py:456; design/ecad/ring/open-pins.csv:23-37 | `pad numbers are this schematic's own order` (open-pins 23) |
| 32 | band and its wiring | Pad order VBUS, D-, D+, GND: the axis of the order on the band is not stated (architecture section 8 and 17.3 and 17.8 disagree). | left to a person | design/firmware.md:1191 | `open, same name order in both` |
| 33 | band and its wiring | Pads on the inside of the band touch the skin: whether any voltage or leakage path reaches them without a case, and how sweat is kept off, is to be stated in the wiring notes. | left to a person | design/firmware.md:1195 | `is to be stated in the wiring notes (17.12)` |
| 34 | band and its wiring | Cell temperature sensor RT1: flex tail 2 (17.3, 17.8) or main board beside the cell (W13, conflict 5); RT1 part code is OPEN. | value open | design/firmware.md:1193; design/bom-notes.md:47; design/ecad/ring/additions.csv:33; design/ecad/ring/parts.csv:44 | `sch-notes and bom-notes (conflict 5) put RT1 on the main board beside the cell.` (firmware 1193); `part code OPEN` (additions 33) |
| 35 | band and its wiring | Flex tail materials and sizes are defaults: base polyimide with two copper layers, pad finish and coverlay colour, length, width and path of each tail. | needs a maker's answer | design/mfg/specs/band-flex-tails.md:17; design/mfg/specs/band-flex-tails.md:23; design/mfg/specs/band-flex-tails.md:46 | `Default, to confirm with the maker: polyimide base` (17); `Pad finish and coverlay colour: open point 2` (23); `Length, width and path of each tail are open point 4` (46) |
| 36 | band and its wiring | Liner made as a laminate with the two ribbons inside it: can it be made, and how is it repaired (S19). | needs a maker's answer | design/architecture.md:517; design/mfg/specs/band-liner.md:52 | `can it be made, and how is it repaired` (architecture 517); `Conflict K-A5 (S19): the ribbons embedded with 0.075 mm` (band-liner 52) |
| 37 | band and its wiring | Ribbon joint at the board end (K-A6) and ribbon outlines, lengths per size and fold bend radius are not settled. | left to a person | design/mfg/assembly/assembly.md:323; design/mfg/assembly/assembly.md:373 | `Each ribbon has parts at its band end` (323); `Ribbon outlines, lengths per size, the fold's bend radius (K-A6)` (373) |
| 38 | band and its wiring | Ribbon line count and 2-layer build (7 and 8 lines in 1.4 mm) are an assumption; the fold room beside each slot is the flex maker's (K10, K21). | needs a maker's answer | design/mech/thin/thin-notes.md:94; design/mech/thin/thin-notes.md:159 | `the flex maker must confirm` (94); `the flex maker's (band-flex-tails.md line 62, open point 4)` (159) |
| 39 | band and its wiring | Lead wire length as delivered is open (S10). | value open | design/architecture.md:605 | `The lead length as delivered is open item S10.` |
| 40 | band and its wiring | Motor part conflict: 16.4 gives Vybronics VC0625B001L (6 mm, 2.5 V, 100 mA); 17.3 and 17.4 give VC0720B088L (7 mm, 3.0 V, 85 mA). | value open | design/bom-notes.md:43 | `Motor: 16.4 says Vybronics VC0625B001L` |
| 41 | band and its wiring | Motor start: the 3.0 V rail margin at a motor start is open (S21); the start current against the cell limit needs bench proof (S22). | value open | design/architecture.md:519; design/architecture.md:645; design/architecture.md:712 | `still open: the 3.0 V rail's margin at a motor start` (519); `Open item S22: the motor's start current against the nPM1304's battery current limit.` (645) |
| 42 | band and its wiring | Motor start time (W0525) is not in its spec; bounds are taken from a sister part. | value assumed | design/ecad/motor-drive/motor-drive.md:153; design/ecad/motor-drive/motor-drive.md:197 | `Start duration. Not in the W0525 spec` (153); `The start time of the W0525: not stated by Jinlong` (197) |
| 43 | band and its wiring | Motor drive budget uses [ESTIMATE] values (buck efficiency, radio supply, MCU current, start phase, derate, ship current, 100 patterns a day). | value assumed | design/ecad/motor-drive/budget.py:22, 36, 40, 46, 50, 61, 64, 101, 128, 144, 175 | `[ESTIMATE] buck efficiency` (22); `[ESTIMATE] lower bound of the high-current start phase` (46) |
| 44 | band and its wiring | Motor free space to the body is 0.042 mm on US 9 and 0.000 on US 11 to 13; motor body is 0.175 mm from the antenna keep-out (open radio risk). | value open | design/architecture.md:796; design/mech/mech-notes.md:53 | `Open in the model (fix in work)` (796); `The motor body ends 0.175 mm from the antenna keep-out` (mech-notes 53) |
| 45 | band and its wiring | Motor window seal for US 7, 8 and 9 (S26 gains): sealant and method not settled; the ways out are not tried. | value open | design/architecture.md:810; design/mech/thin/thin-notes.md:334 | `Open item S26 gains: the seal of the motor window on US 7, 8 and 9` (810); `Ways out for US 7, 8 and 9 (none tried` (334) |
| 46 | band and its wiring | Motor lead terminals P1 (+) and P2 (-) are this schematic's names; the maker gives colours only. | footprint or pin map provisional | design/ecad/ring/open-pins.csv:48-49 | `the maker gives colours, not numbers` |
| 47 | band and its wiring | Wiring changes W1 to W12, B1 to B6 and F1 to F5 are listed but not made. | left to a person | design/ecad/motor-drive/reply.txt:9 | `Wiring changes (not made): W1 to W12` |
| 48 | screen and its cable | Screen cable is 12.4 mm wide where the model folds 5.0 mm (K16); Tailor Pixels must answer whether a 5.0 mm cable can be made (S27). | needs a maker's answer | design/architecture.md:757; design/architecture.md:762 | `K16 (the screen maker's cable is 12.4 mm wide` (757); `Tailor Pixels must answer whether the TOH095XVT-01` (762) |
| 49 | screen and its cable | Screen connector FH35C footprint is assumed; its pitch is inferred from the 4.8 mm tail (S8); connector pin count and pin-out not settled. | footprint or pin map provisional | design/architecture.md:359; design/architecture.md:57; design/parts/ui.md:18 | `FH35C footprint assumed` (359); `the pitch is inferred from the 4.8 mm tail (open item S8)` (57) |
| 50 | screen and its cable | Screen connector J1 pin positions: the Hirose drawing and position numbering are not read; tail contact k is assumed on connector position k. | drawing or file missing | design/ecad/ring/open-pins.csv:8-22; design/ecad/ring/make_netlist.py:455; design/ecad/ring/pcb/build_board.py:508 | `its drawing and position numbering are not read` (open-pins 8); `not from the Hirose drawing (not read)` (build_board 508) |
| 51 | screen and its cable | Screen DISP1 pin table: MTP and VCI numbering (pin 3 absent, pin 4 twice) is not settled (S8). | footprint or pin map provisional | design/ecad/ring/open-pins.csv:50-51; design/ecad/ring/make_netlist.py:463 | `pin 3 is absent and pin 4 appears twice` (open-pins 50); `number provisional` (make_netlist 463) |
| 52 | screen and its cable | Lit window brightness is not proven (estimate 5 to 25 percent). | needs hardware to measure | design/architecture.md:695 | `NOT PROVEN: how bright the window is.` |
| 53 | screen and its cable | Metal on the screen ledge over the antenna (S24) and the ledge glass clear check (S25, S-L1): the screen maker answers. | needs a maker's answer | design/architecture.md:682; design/architecture.md:698; design/mech/light-path/light-path.md:117 | `Open item S24: metal on the screen panel's ledge over the antenna` (682); `Open item S25: the screen maker confirms the ledge glass is clear` (698) |
| 54 | screen and its cable | Screen weight is not known: the maker's sheet says "Weight TBD". | value open | design/architecture.md:870; design/parts/ui-pass2.md:21 | `the maker's sheet says "Weight TBD"` |
| 55 | screen and its cable | Screen start-up code (SH8501A) is needed from the vendor for the ring panel; the bench panel is a different part. | drawing or file missing | design/bench/bench-kits.md:45 | `It needs the vendor's start-up code for the SH8501A (open item 12.1)` |
| 56 | screen and its cable | Screen candidates: driver datasheets, pin tables and connectors not read; a custom panel MOQ is not found. | drawing or file missing | design/parts/slim.md:33; design/parts/slim.md:276; design/parts/thin-bezel-products.md:109 | `Driver datasheet: not in document.` (slim 33); `not read; page not rea` (slim 276, after `7.4 EDO095-180120`); `Not found: a published custom AMOLED outline-cut MOQ` (109) |
| 57 | screen and its cable | Screen power: the panel supply must be proven off with OLED_PWR_EN low, and a panel failure in use is not proven. | needs hardware to measure | design/bench/b2-notes.md:55 | `That the panel supply is really off with OLED_PWR_EN low` |
| 58 | antenna | Antenna match inductors and capacitor are to be retuned on the real board. | needs hardware to measure | design/architecture.md:55; design/bom.csv:13 | `retuned on the real board [BENCH]` (architecture 55); `retune on the real board` (bom 13) |
| 59 | antenna | Antenna efficiency, gain, range and detuning are not claimed; the bench kit has no network analyser (return loss test B planned). | needs hardware to measure | design/mech/antenna/antenna-study.md:68; design/mech/antenna/final-reply.md:36 | `Cannot be claimed here: any efficiency, gain, range or detuning` (68); `The bench kit lacks a network analyser` (final-reply 36) |
| 60 | antenna | Antenna received-signal RSSI target uses an [ESTIMATE]. | value assumed | design/mech/antenna/antenna-study.md:131 | `Mean RSSI of T2 worn no more than 10 dB below T0 [ESTIMATE` |
| 61 | antenna | Antenna study checklist: integers in the texts are not done. | left to a person | design/mech/antenna/CHECKLIST.md:35 | `Open, not done here: integers in the texts` |
| 62 | cell and power | Cell discharge limit and protection trip current are unknown (S12); the start current and the charge setting depend on them. | needs a maker's answer | design/architecture.md:508; design/architecture.md:710; design/ecad/motor-drive/motor-drive.md:198; design/firmware.md:1188 | `The cell's own discharge limit and its protection circuit's trip current stay unknown (S12)` (710); `cell maker (Grepow), through open item S12` (firmware 1188) |
| 63 | cell and power | Cell heat limit during the cast is unknown; the cell is live from step 16 to the end (K-A8). | needs a maker's answer | design/mfg/assembly/assembly.md:325; design/architecture.md:728 | `The cast's heat limit is unknown: the cell maker must state it.` |
| 64 | cell and power | Cell chemistry, format and size are not stated; the cell changes to 2.60 x 11.9 x 19.0 mm (S1) and its peak discharge is 228 mA. | needs a maker's answer | design/mfg/specs/cell.md:12; design/architecture.md:354; design/mfg/specs/cell.md:44; design/mfg/specs/cell.md:75 | `cell chemistry and format are not stated beyond` (cell 12); `Open item S1 changes to this size.` (architecture 354) |
| 65 | cell and power | Charge setting CHARGE_CURRENT 15 mA stays until the cell maker states its limit (S12); the value changes in one place. | value assumed | design/architecture.md:567; design/firmware.md:1189 | `CHARGE_CURRENT` = 15 mA (architecture 567); `Grepow states the cell's own limit (S12)` (firmware 1189) |
| 66 | cell and power | Power budget currents are estimates, not from a datasheet (main chip, storage, radio, power chips). | value assumed | design/architecture.md:89; design/architecture.md:90; design/architecture.md:93; design/architecture.md:94 | `3.0 mA at 1.8 V, estimate, not from a datasheet` |
| 67 | cell and power | Datasheet values conflict: nPM1304 range (3.5 V), the battery quiescent current between versions, and the QFN52 package for the chip. | value open | design/parts/research-npm1304.md:25; design/parts/mcu.md:115; design/parts/mcu.md:16 | `Conflicting range` (npm1304 25); `Open conflict: the battery quiescent current differs` (mcu 115); `CONFLICT (open)` (mcu 16) |
| 68 | cell and power | 3.0 V rail margin at a motor start and the screen VCI current are not checked: not on file. | value open | design/architecture.md:603 | `NOT CHECKED: the screen's VCI current is not on file` |
| 69 | cell and power | Power-fail and discharge cut-off: section 3 still says 3.1 V; the nPM1304 read gives 2.7 V default; the cell maker gives the undervoltage limit (S12). | value open | design/firmware.md:1198 | `Architecture section 3 still says` |
| 70 | cell and power | Requirement P1 (battery 130 mAh or more) and P2 (10 hours meeting mode) are NOT MET on paper; the owner chose thinness. | value open | requirements.md:182; requirements.md:183 | `P2 Meeting mode, 10 hours or more: NOT MET.`; `P1 Battery in the block, 130 mAh or more` |
| 71 | cell and power | Requirement C3 (ring charge time under 90 minutes) is UNPROVEN. | needs hardware to measure | requirements.md:195 | `C3 Ring charge time, under 90 minutes: UNPROVEN.` |
| 72 | microphones | Microphone SPK0641HT4H-1 orderable code and stock are open (S23); the reel code is not known. | needs a maker's answer | design/architecture.md:41; design/architecture.md:662; design/mech/mic-path/mic-path.md:198 | `orderable code open, S23` (41); `O1 Orderable code and stock of the SPK0641HT4H-1: not checked` (mic-path 198) |
| 73 | microphones | Microphone seal and membrane (at most 0.10 mm): no part chosen (Gore to quote). | needs a maker's answer | design/architecture.md:58; design/mech/mic-path/mic-path.md:201 | `no part chosen` (architecture 58); `O4 Membrane at most 0.10 thick: no part chosen` (mic-path 201) |
| 74 | microphones | Gasket foam material and its three thicknesses are estimates; a gasket maker must answer. | value assumed | design/mech/mic-path/mic-path.md:199; design/mfg/assembly/assembly.md:370 | `O2 Gasket material and the three thicknesses: [ESTIMATE]` |
| 75 | microphones | Acoustic figures are order-of-magnitude estimates; whether the ring hears a room through openings facing the finger is NOT PROVEN (bench B7). | needs hardware to measure | design/mech/mic-path/acoustic_estimates.py:2; design/architecture.md:659 | `Order-of-magnitude acoustic figures` (acoustic 2); `NOT PROVEN: how well the ring hears a room` (architecture 659) |
| 76 | microphones | SPG08P4HM4H-1 height and port diameter not verified; the IM68D128B datasheet copy returned no usable text. | drawing or file missing | design/mech/mic-path/mic-path.md:50; design/parts/research-microphone-port.md:53; design/parts/research-microphone-port.md:51 | `height not verified` (mic-path 50); `package size and port diameter: not re` (research 53); `the Mouser copy retu` (research 51) |
| 77 | microphones | 0.20 mm metal ring under each membrane seat is an open point (O3). | value open | design/mech/mic-path/mic-path.md:200; design/architecture.md:662 | `O3 The 0.20 mm metal ring under each membrane seat` |
| 78 | microphones | Thumb side: conflict K8, no opening in a side wall; whether a finger or thumb covers the opening (O5) is not known. | value open | design/mech/mic-path/mic-path.md:83; design/mech/mic-path/mic-path.md:202 | `The thumb (conflict K8): there is no opening in a side wall.` (83); `Whether the finger, the thumb or the next finger covers the opening` (202) |
| 79 | microphones | SNR falls from 67.5 to 64.5 dB(A); bench B1 compares recordings. | needs hardware to measure | design/mech/mic-path/mic-path.md:203 | `O6 SNR falls from 67.5 to 64.5 dB(A); bench B1 compares recordings` |
| 80 | case board | Case pin numbers without numbers: U2 PowerPAD and J1 shell tabs (table 6-1 and pin table). | footprint or pin map provisional | design/ecad/case/open-pins.csv:2; design/ecad/case/open-pins.csv:5; design/ecad/case/make_netlist.py:23; design/ecad/case/make_netlist.py:45 | `PowerPAD has no number in Table 6-1` (open-pins 2); `shell tabs have no number in the pin table` (open-pins 5) |
| 81 | case board | Case U4 SD NAND pad numbers (LGA8x2 9x10) are not in a text-readable drawing; names are known. | drawing or file missing | design/ecad/case/open-pins.csv:6-13; design/ecad/case/sch-notes.md:55 | `pad numbers of the LGA8x2 9x10 package not in a text-readable drawing` |
| 82 | case board | Case cell BT1 leads: the datasheet gives terminals WC and FL only; the lead order waits on the cell order (S1). | needs a maker's answer | design/ecad/case/open-pins.csv:3; design/ecad/case/open-pins.csv:4 | `cell leads: datasheet gives terminals WC/FL only` |
| 83 | case board | Case cell protection circuit and its tolerance are not read; the page size is used. | needs a maker's answer | design/case/c6/c6-notes.md:15 | `The cell's own protection circuit and its tolerance are not read` |
| 84 | case board | Harwin P70-6000045R pin (fitted, K1): stroke and length tolerance are not confirmed. | needs a maker's answer | design/case/case-notes.md:79; design/case/case-notes.md:127; design/case/look/c5e_bom.py:21 | `its stroke is still to be confirmed` (case-notes 79); `the Harwin P70's length tolerance and its stroke are not in the files rea` (case-notes 127) |
| 85 | case board | Holder: the moulder has not confirmed the 0.79 mm walls between bores in LCP. | needs a maker's answer | design/case/c5d-open-points-handover.md:44 | `the moulder has not confirmed the 0.79 mm walls` |
| 86 | case board | Holder stake strength is not tested; the five wires below the holder are not modelled. | needs hardware to measure | design/case/c5d-open-points-handover.md:44 | `the stake strength is not tested` |
| 87 | case board | Touch electrode E1 reads through a 1.97 mm LCP wall: bench B3 must confirm it. | needs hardware to measure | design/case/c5d-open-points-handover.md:44; design/case/case-architecture.md:220 | `the touch electrode E1 now reads through a 1.97 mm LCP wall (bench B3)` |
| 88 | case board | LED1 green and blue are active low and dim at 3.3 V through 150 ohm (bench B4). | needs hardware to measure | design/case/case-architecture.md:178; design/ecad/case/sch-notes.md:83 | `active low (bench B4)` (178); `LED green and blue need 3.3 V typical at 20 mA` (sch-notes 83) |
| 89 | case board | Boost efficiency 0.85 is assumed and untested (bench B5); it sets the charge count. | value assumed | design/case/CHECKLIST.md:15 | `boost efficiency 0.85 assumed, untested: bench B5` |
| 90 | case board | PMID load while charging: TI's allowance is open (S5); D+ and D- open. | needs a maker's answer | design/ecad/case/sch-notes.md:79 | `TI's allowance for this is open item S5` |
| 91 | case board | Wi-Fi antenna screening if the finish is metal (conflict K2): a proposal to confirm with a maker. | needs a maker's answer | design/case/case-architecture.md:232 | `proposal to confirm with a maker` |
| 92 | case board | Full-speed USB of the ring's chip under the ESP32-S3 host (bench B1) is a condition not yet shown on the bench. | needs hardware to measure | design/case/case-architecture.md:76 | `Condition: the ring's nRF54LM20A must run its high-speed USB device at full speed` |
| 93 | case mechanics | Lid pad force: the 1.0 mm silicone pad must push the block down with more than 159 gf (bench B2). | needs hardware to measure | design/case/case-notes.md:113 | `the 1.0 mm silicone pad compressed to 0.7 mm must push the block down with more than 159 gf` |
| 94 | case mechanics | Lid friction fit and droop on the pivot (bench B7, old C4 note; not re-checked in C5d). | needs hardware to measure | design/case/look/c4_case-notes.md:42 | `bench item B7 (friction fit, droop)` |
| 95 | case mechanics | Straight lift-out is not simulated; the other case pictures are C5c renders, not re-rendered. | left to a person | design/case/c5d-open-points-handover.md:45; design/case/c5d-open-points-handover.md:46 | `The other pictures (side, underside, in-hand, compare) are the C5c renders` |
| 96 | ring body and mechanics | Body spec open point 5 values (board, foam, adhesive, liner, flex stack) and open point 2 values are not settled. | value open | design/mfg/specs/body.md:39; design/mfg/specs/body.md:48 | `open point 5` (body 39) |
| 97 | ring body and mechanics | Body model values to confirm, not in the architecture, taken from the 3D model. | value assumed | design/mfg/specs/body.md:88 | `Model values to confirm (not in the architecture` |
| 98 | ring body and mechanics | Body variants for sizes other than US 9: the per-size values are not in the body spec. | drawing or file missing | design/mfg/specs/body.md:113 | `Body variants for sizes other than US 9: the values per size are in the` |
| 99 | ring body and mechanics | Body defaults: CNC from bar with multi-axis, titanium grade and black PVD, ISO 2768-m; each to confirm with the maker. | value assumed | design/mfg/specs/body.md:17; design/mfg/tools/draw_merged32c.py:35 | `Default, to confirm with the maker: CNC machining from bar` (body 17); `Ti-6Al-4V grade 5, black PVD (default, to confirm with the maker` (draw 35) |
| 100 | ring body and mechanics | Joystick centre press and feel: bench B6 (centre press) and B9 (feel, sealing, wear); cap feel and tilt in motion not tested. | needs hardware to measure | design/mfg/specs/joystick-nub.md:101; design/architecture.md:398; design/mech/thin/thin-notes.md:470 | `Bench items B6 (centre press) and B9 (feel, sealing` (joystick-nub 101); `B6 \| Centre press by two opposite switches \| bench, first housing print` (architecture 398); `Cap feel, tilt clearance in motion` (thin-notes 470) |
| 101 | ring body and mechanics | Joystick opening relies on the switches' own ratings; still open. | value open | design/mfg/specs/joystick-nub.md:102 | `The joystick opening relies on the switches' own rating` |
| 102 | ring body and mechanics | Mechanical dimensions marked ASSUMED: 30 lines in dimensions.csv (CHECKLIST says 25 rows); 32 lines in ring.py. | value assumed | design/mech/dimensions.csv:7 (and the other ASSUMED rows); design/mech/ring.py:28; design/mech/CHECKLIST.md:7 | `ASSUMED: minimum wall, skin, lip, ledge or rib for printed n` (dimensions 7) |
| 103 | ring body and mechanics | Mechanical values to confirm: mic port position, joystick stem diameter 2.5 mm, and availability of a non-metal M1.2 screw. | left to a person | design/mech/mech-notes.md:70 | `ASSUMED values to confirm: mic port position, joystick stem diameter 2.5` |
| 104 | ring body and mechanics | thin-inside.step was written by thin.py's own export and has not been checked. | left to a person | design/mech/thin/thin-notes.md:472 | `thin-inside.step was written by thin.py's own export, not checked` |
| 105 | ring body and mechanics | Coating thickness (S29) is not known; no figure. | value open | design/architecture.md:881 | `no figure (thickness open, S29)` |
| 106 | ring body and mechanics | DP420 bond on the gloss black coating is not tested. | needs hardware to measure | design/mfg/assembly/v7-update-notes.md:28; design/ecad/ring/v7-wiring-notes.md:64 | `The DP420 bond on the gloss black coating is not tested` (v7-update-notes 28); `the DP420 bond on the coated titanium` (v7-wiring-notes 64) |
| 107 | ring body and mechanics | Ring weight is not known: most parts have no figure; the cover glass has no density or mass source (S5). | value open | design/architecture.md:883; design/architecture.md:906 | `the weight of the ring is not known` (883); `no source gives a density or a mass: the cover glass` (906) |
| 108 | ring body and mechanics | Densities in the weight estimate are ASSUMED or unverified (cell, silicon packages, screen, foam, mic, switch, clear parts). | value assumed | design/mech/mass.py:15; design/mech/mass.py:16; design/mech/mass.py:17 | `ASSUMED: Li-polymer pouch about 2 g/cm3 overall` |
| 109 | ring body and mechanics | Cover glass grade and forming are defaults to confirm with the maker; dimensions refer to open point 2. | value assumed | design/mfg/specs/cover-glass.md:12; design/mfg/specs/cover-glass.md:28 | `Default, to confirm with the maker: chemically strengthened aluminos` (12); `glass thickness at the centre \| 1.10 mm \| open point 2` (28) |
| 110 | ring body and mechanics | Glass seal ring SEAL1 is 0.05 mm thick but its tape and sealing are not settled; the glass seat has no room for one (K-A4). | value open | design/mfg/specs/cover-glass.md:43; design/mfg/assembly/assembly.md:321; design/mfg/assembly/assembly.md:360 | `glass seal ring SEAL1 \| 0.05 mm thick \| open` (43); `No glass-to-body adhesive or seal existed` (321) |
| 111 | assembly and manufacturing | Floor slot sealant: no part number and no part in the model; the sealing method is not named. | left to a person | design/mfg/assembly/assembly.md:76; design/mfg/assembly/assembly.md:364; design/mfg/assembly/assembly.md:388 | `no part number and no part in the model` (76); `the mechanical designer; bench B8` (364) |
| 112 | assembly and manufacturing | Cast resin dam and resin: the cast resin runs into the joystick pocket and locks the switches (K-A3). | value open | design/mfg/assembly/assembly.md:320 | `The cast resin runs into the joystick pocket and locks the switches` |
| 113 | assembly and manufacturing | Test pads on the populated under face are testable only before step 17 (K-A1). | value open | design/mfg/assembly/assembly.md:318 | `The board is testable through its test pads only before step 17.` |
| 114 | assembly and manufacturing | Ship mode must come last, but SHIP_ENTER clears the factory flag; the proposal is a separate FACTORY sub-command (K-A7). | left to a person | design/mfg/assembly/assembly.md:324 | `Ship mode must come last, but SHIP_ENTER cleared the factory flag` |
| 115 | assembly and manufacturing | Dam DAM1 is drawn standing on the liner but must exist before the cast; its material and how it stands are open (K-A12). | value open | design/mfg/assembly/assembly.md:329; design/mfg/assembly/assembly.md:365 | `the dam DAM1 is drawn standing ON the liner` (329); `Dam DAM1: material, and how it stands before the cast (K-A12)` (365) |
| 116 | assembly and manufacturing | Casting resin of the liner: grade, skin certificate and cure heat are open (S13, B8, S12). | needs a maker's answer | design/mfg/assembly/assembly.md:363 | `Casting resin of the liner (grade, skin certificate, cure heat)` |
| 117 | assembly and manufacturing | Clear adhesive ADH1 and foam FOAM1 products are not chosen; the design partner supplies them. | needs a maker's answer | design/mfg/assembly/assembly.md:361; design/mfg/assembly/assembly.md:362 | `Clear adhesive ADH1 (product, outline)`; `Foam FOAM1 (product 0.10 mm, outline closed all round)` |
| 118 | assembly and manufacturing | Charging pads: plated land or soldered disc is open (S19). | left to a person | design/mfg/assembly/assembly.md:372 | `Charging pads: plated land or soldered disc` |
| 119 | assembly and manufacturing | Cap CAP1 and frame FRM1: a moulder and the body maker must quote; the joystick head stiffener is open (S26). | needs a maker's answer | design/mfg/assembly/assembly.md:369; design/mfg/assembly/assembly.md:366 | `a moulder and the body maker quote` (369); `Stiffener of the joystick head (stainless or polyimide)` (366) |
| 120 | assembly and manufacturing | Microphone membrane at most 0.10 mm (Gore, S23) and microphone gasket foam with three thicknesses (bench B7) are open. | needs a maker's answer | design/mfg/assembly/assembly.md:371; design/mfg/assembly/assembly.md:370 | `Microphone membrane, at most 0.10 mm` (371); `Microphone gasket foam and its three thicknesses` (370) |
| 121 | assembly and manufacturing | IP65 test is not run (bench purchases on hold); S6 IP65 is NOT MET ON PAPER (two openings have no sealing means). | needs hardware to measure | design/mfg/assembly/assembly.md:349; requirements.md:204 | `The test that would prove IP65 (to describe, not to order: bench purchases are on hold)` (349); `S6 Water and dust, IP65 or better: NOT MET ON PAPER` (requirements 204) |
| 122 | assembly and manufacturing | Assembly check_assembly.py fails A1 and A2 (also on the base copy). | left to a person | design/cell-sweep-notes.md:30 | `check_assembly.py: exit 1, RESULT FAIL A1, A2` |
| 123 | assembly and manufacturing | Assembly step 25 reads the boot count after FACTORY ENTER and expects the same count after VBUS is removed; the assembly owner updates steps 2 and 25 (H19). | left to a person | design/firmware.md:1200 | `Assembly step 25 reads the boot count after FACTORY ENTER` |
| 124 | assembly and manufacturing | Changes other files need, listed in the assembly file but still open. | left to a person | design/mfg/assembly/assembly.md:381; design/mfg/assembly/assembly.md:383 | `except the two rows below that are still open` |
| 125 | parts list | SKTAAAE010 switch outline and land pattern (S9), price and production status: no file closes them. | drawing or file missing | design/bom-notes.md:52; design/ecad/ring/make_netlist.py:454 | `SKTAAAE010 outline and land pattern (S9), price` |
| 126 | parts list | Order codes for open BOM lines: items 5, 6 and 9 plus the 100 nF X7R, 15-position 0.5 mm connector, M1.2 insert and 0.2 mm foam codes are not found. | needs a maker's answer | design/parts/order-codes.md:158 | `items 5, 6 and 9 plus the 100 nF X7R` |
| 127 | parts list | Order codes with maker sheets for C71, C85, C86, C87, C88, C35, C36 and R41 are not on file. | needs a maker's answer | design/ecad/ring/sch-notes.md:279; design/ecad/ring/open-pins.csv:52-56; design/ecad/ring/open-pins.csv:60-61 | `Order codes with maker sheets for C71` (sch-notes 279); `no maker sheet of such a part is on file` (open-pins 52) |
| 128 | parts list | Part numbers left OPEN: L71 and L72 (2.2 uH), RT1 (10k NTC) on the parts list. | needs a maker's answer | design/ecad/ring/parts.csv:37; design/ecad/ring/parts.csv:39; design/ecad/ring/open-pins.csv:57-59 | `L71,L,2.2uH,OPEN 12.2` |
| 129 | parts list | Schematic addition values (C73 to C79) are taken from the DK kit design and must be confirmed against the ring part. | value assumed | design/bom.csv:70; design/bom.csv:71; design/bom.csv:72; design/bom.csv:73 | `value from the nPM1300 kit design (DK PCA10184); to confirm against` (bom 70) |
| 130 | parts list | Light path changes listed but not made in the files: R41 680 ohm to 820 ohm, LG1 and LP1 rows, placement rows, netlist and KiCad footprint. | left to a person | design/mech/light-path/light-path.md:123; design/mech/light-path/light-path.md:145 | `## 10. Changes other files need (not made here)`; `"R41,R,680R,,ring:R_0201,controls,no" \| 820R` |
| 131 | parts list | Light path owner and maker questions: KPG-1005SURC-TT orderable and datasheet; LG1 guide maker (mirror coat, glue); light on the -Y side not the thumb side. | needs a maker's answer | design/mech/light-path/light-path.md:118; design/mech/light-path/light-path.md:119; design/mech/light-path/light-path.md:121 | `is KPG-1005SURC-TT orderable, and its current datasheet.` (118); `the mirror coat, the glue.` (119); `the light is on the -Y side` (121) |
| 132 | parts list | Core chip datasheet values not read: part number, package, PDM, current, sleep and modules. | drawing or file missing | design/parts/core.md:13; design/parts/core.md:42 | `Orderable part number, as printed \| not read` |
| 133 | parts list | Cell candidate fields not read (charge voltage, protection, currents, certifications, datasheet link). | drawing or file missing | design/parts/power.md:21; design/parts/power.md:145; design/parts/power.md:166 | `Charge voltage \| not in the pages read` (21); `(2) MAX17260 datasheet: analog.com page timed out (not read)` (166) |
| 134 | parts list | Main chip (mcu) datasheet gaps: exact orderable strings, reference PCB, package drawings, land patterns and DK part numbers not read. | needs a maker's answer | design/parts/mcu.md:15; design/parts/mcu.md:68; design/parts/mcu.md:90; design/parts/mcu.md:120; design/parts/mcu.md:139 | `Exact orderable strings (with -R / -R7 tape suffix): not read` (15); `Not found. The reference PCB PDF` (68); `Package drawing and pad dimensions: not read for the GEAG part.` (90) |
| 135 | parts list | Candidate memory and battery datasheets not read: package drawings and currents (MKDV, ZDSD32, CSNP32, eMMC). | drawing or file missing | design/parts/slim-2.md:125; design/parts/slim-2.md:126; design/parts/slim.md:156; design/parts/slim.md:186 | `MKDV16GCL-STP, MKDV32GCL-STH / -STP / -STL maker package drawing and` (slim-2 125); `Currents: not read in this run` (slim 156) |
| 136 | parts list | Screen controller and switch candidates: TPA511GLFS not verified; tactile KXT and EVP-AA not read; recommended pad not in catalog. | drawing or file missing | design/parts/ui-pass3.md:118; design/parts/ui.md:108; design/parts/ui-pass3.md:174 | `C&K (Littelfuse) TPA511GLFS, not verified.` (118); `Tactile KXT and EVP-AA: not read` (ui 108); `Recommended target pad: not in the catalog page.` (174) |
| 137 | parts list | Bench kit price and stock not read (nPM1304 EK and others); B1 price total not recomputed. | value open | design/bench/bench-kits.md:32; design/bench/b2-notes.md:21 | `price and stock of the nPM1304 EK at any seller` (bench-kits 32); `B1 price total (313.66) is not recomputed for B2` (b2-notes 21) |
| 138 | parts list | Bench kit: the kit on sale carries the nRF54LM20B while the ring names the nRF54LM20A; the A chip rules on the kit are new in B2. | value open | design/bench/bench-plan-B1.md:88; design/bench/bench-kits.md:13 | `The kit on sale carries the nRF54LM20B, and the ring design names the nRF54LM20A.` |
| 139 | parts list | Bench seller order codes for Knowles SPK0641HT4H-1 and Jinlong W0525AB001D are not printed in any saved file; the Maker evaluation board for the mic is none found. | needs a maker's answer | design/bench/bench-plan.md:227; design/bench/b2-notes.md:27; design/bench/bench-kits.md:40 | `Seller order codes for the Knowles SPK0641HT4H-1 and the Jinlong W0525AB001D` (227); `Maker's evaluation board for the SPK0641HT4H-1: none found.` (kits 40) |
| 140 | parts list | Reference device Plaud NotePin: order code not confirmed. | value open | design/bench/bench-plan.md:42 | `\| Plaud \| not confirmed \| not confirmed \|` |
| 141 | parts list | Android research unknowns: RingConn Gen 2 battery unresolved; Aina AI ring OLED not confirmed; Pixel Watch 3 not checked; RingOS WAMR not fetched. | value open | design/parts/research-android-devices.md:46; design/parts/research-android-devices.md:54; design/parts/research-ring-os.md:18 | `RingConn Gen 2 \| Unresolved: 12 mAh` (46); `WAMR (WebAssembly Micro Runtime) on Zephyr` (ring-os 18) |
| 142 | tests | Bench items B1 to B9 are not run; the 10 hour target is measured first (B2). | needs hardware to measure | design/architecture.md:387; design/architecture.md:473; design/architecture.md:474; design/architecture.md:509; design/architecture.md:510; design/architecture.md:511 | `It is the first bench test (B2).` (387); `B8 \| Resin-closed band: heat while charging` (473) |
| 143 | tests | Bench plan open points 1 to 6: EK battery polarity, EK VDDIO supply, Power Profiler header names, SDK sample names, Plaud export format. | drawing or file missing | design/bench/bench-plan.md:225; design/bench/bench-plan.md:226; design/bench/bench-plan.md:228; design/bench/bench-plan.md:229; design/bench/bench-plan.md:230 | `EK battery connector polarity and the label of each EK header` (225); `How the EK supplies the PMIC's VDDIO` (226) |
| 144 | tests | The DK pin table could not be read; the DK pin check (CHECK 1) is open. | drawing or file missing | design/bench/bench-plan-B1.md:55; design/bench/bench-plan.md:129 | `The DK's pin table could not be read` (B1 55); `how the EK ties VDDIO is not read` (bench-plan 129) |
| 145 | tests | Charging at 15 mA to 4.35 V and the cell's discharge limit (S12): no battery cell on the bench. | needs hardware to measure | design/bench/bench-plan.md:219; design/bench/b2-notes.md:58 | `Charging at 15 mA to 4.35 V and the cell's discharge limit (open item S12)` |
| 146 | tests | Motor drive test on Nordic's nPM1304-EK is planned, not run. | needs hardware to measure | design/ecad/motor-drive/motor-drive.md:116; design/ecad/motor-drive/reply.txt:9 | `2.9 Bench test on Nordic's kit nPM1304-EK` |
| 147 | tests | Light path: how much light reaches the surface cannot be claimed without a bench test. | needs hardware to measure | design/mech/light-path/light-path.md:111 | `Cannot be claimed without a bench test` |
| 148 | tests | Android: heat on the finger with an Android chip awake is a bench test. | needs hardware to measure | design/android-study.md:66 | `Heat on the finger with an Android chip awake: a bench test.` |
| 149 | other (owner, requirements, firmware, Android) | Android module thickness, real sleep and awake currents, Wear OS licence, and watch battery figures are unknown until a maker or Google answers. | needs a maker's answer | design/android-study.md:43; design/android-study.md:64; design/android-study.md:65; design/android-study.md:39 | `Unknown until a maker answers: the module's thickness` (43); `Whether Google licenses Wear OS for such a device` (64); `The watch battery figures used for the current estimate: confirm from the makers' own specification sheets.` (65) |
| 150 | other (owner, requirements, firmware, Android) | Software study: battery cost of an open Bluetooth link and of live audio, and processing margin of the chip for the LC3 path, are to be measured. | needs hardware to measure | design/software-platform-study.md:58; design/software-platform-study.md:59 | `The battery cost of an open Bluetooth link and of live audio` (58) |
| 151 | other (owner, requirements, firmware, Android) | Requirements marked Proposed or Bench with no source: weight S5, directional A4, hand effects A8, standby P7, screen type D3. | needs hardware to measure | requirements.md:25; requirements.md:35; requirements.md:39; requirements.md:51; requirements.md:70 | `Proposed. No source: Aina publishes no weight. Bench` (25); `Bench. No published data exists` (39); `Bench: measure OLED power first.` (70) |
| 152 | other (owner, requirements, firmware, Android) | Owner decision O1: phone and video calls, later version or a vibration sensor. | left to a person | requirements.md:158 | `O1. Phone and video calls: leave to a later software version` |
| 153 | other (owner, requirements, firmware, Android) | Owner decision O2: screen type if OLED power is high. | left to a person | requirements.md:159 | `O2. Screen type if OLED power is high` |
| 154 | other (owner, requirements, firmware, Android) | Owner decision O3: no target price is set. | left to a person | requirements.md:160 | `O3. Price position: no target price is set yet.` |
| 155 | other (owner, requirements, firmware, Android) | Requirement C1: the case's seat must be redesigned for the changed ring. | left to a person | requirements.md:194 | `CHANGED, the case's seat must be redesigned.` |
| 156 | other (owner, requirements, firmware, Android) | Firmware issue H11: architecture section 8 and the case document still give 6.3 minutes per recorded hour. | value open | design/firmware.md:1192 | `Architecture section 8 and the case document still give 6.3 minutes per recorded hour` |
| 157 | other (owner, requirements, firmware, Android) | Firmware issue H13: architecture sections still describe the A3 or earlier ring; the architecture owner rewrites them when the open items of 16.9 close. | left to a person | design/firmware.md:1194 | `still describe the A3 or earlier ring` |
| 158 | other (owner, requirements, firmware, Android) | Firmware issue H15: architecture sections still describe a separate record button. | left to a person | design/firmware.md:1196 | `still describe a separate record button` |
| 159 | other (owner, requirements, firmware, Android) | Firmware F5 notes: motor start allowance (10 ms at 175 mA) and T-MOTOR pass line are estimates (bench B-M3, B-M5); microphone current at 1.280 MHz needs bench B2; VBUS drive function is not read. | value assumed | design/firmware-f5-notes.md:76; design/firmware-f5-notes.md:78; design/firmware-f5-notes.md:81 | `The motor start allowance (10 ms at 175 mA) and the T-MOTOR pass line` (76); `Microphone current at 1.280 MHz` (78); `Whether any nPM1304 function drives VBUS` (81) |
| 160 | other (owner, requirements, firmware, Android) | Model and file revisions still to follow: exterior variant merged32h, inside model v5 and v7 not built, wiring diagram, parts list; record-cap.md has no v7 content; exterior files hold a light solid. | drawing or file missing | design/architecture.md:661; design/architecture.md:827; design/mfg/assembly/v7-update-notes.md:29; design/supplier-package/v3-notes.md:66; design/supplier-package/v3-notes.md:69 | `Files that follow at the next revisions` (661); `The inside model v7 is not built yet` (v7-update 29); `has no v7 content` (v3-notes 69) |
| 161 | other (owner, requirements, firmware, Android) | Supplier package: the circuit board layout is named as not ready; the working-folder files are not checked against the package copies. | left to a person | design/supplier-package/make_one_pager.py:64; design/supplier-package/v3-notes.md:76 | `Not ready: the circuit board layout (who routes it is not decided)` (make_one_pager 64); `Not done / unverified` (v3-notes 75) |
| 162 | ring circuit board | Ring cell BT1 tab order is open and its protection circuit (on the tab, at -77 degrees) is not drawn. | footprint or pin map provisional | design/ecad/ring/open-pins.csv:6-7; design/ecad/ring/make_netlist.py:103 | `tab order and its protection circuit (on the tab, at -77 degrees) not drawn` |
| 163 | ring circuit board | Joystick switches SW1 to SW5 (SKTAAAE010): two terminals each, no terminal numbers or drawing (S9). | footprint or pin map provisional | design/ecad/ring/open-pins.csv:38-47; design/ecad/ring/make_netlist.py:454 | `shows two terminals but no terminal numbers or drawing` |


## Part 2. The same items grouped by subject

| Subject | Count | Item numbers (Part 1) |
|---|---|---|
| ring circuit board | 30 | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 162, 163 |
| band and its wiring | 19 | 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47 |
| screen and its cable | 10 | 48, 49, 50, 51, 52, 53, 54, 55, 56, 57 |
| antenna | 4 | 58, 59, 60, 61 |
| cell and power | 10 | 62, 63, 64, 65, 66, 67, 68, 69, 70, 71 |
| microphones | 8 | 72, 73, 74, 75, 76, 77, 78, 79 |
| case board | 13 | 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92 |
| case mechanics | 3 | 93, 94, 95 |
| ring body and mechanics | 15 | 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110 |
| parts list | 17 | 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141 |
| assembly and manufacturing | 14 | 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124 |
| tests | 7 | 142, 143, 144, 145, 146, 147, 148 |
| other (owner, requirements, firmware, Android) | 13 | 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161 |
| total | 163 | 163 items (each item has one subject) |

## Part 3. Files named open-pins.csv, open-points, or with open in the name

Files found by name (not in the excluded folders, not .log): `design/ecad/ring/open-pins.csv`, `design/ecad/case/open-pins.csv`, `design/case/c5d-open-points-handover.md`. The image and log files with `open` in the name (for example `design/case/look/case-open.png`) are pictures or logs and carry no open-item rows.

Each row of the two CSV files, by file line number, mapped to a Part 1 item (all rows are held by an item):

| File | Row (line) | reference, pin, name | Part 1 item |
|---|---|---|---|
| design/ecad/ring/open-pins.csv | 2 | X1, P1, X1 | 14 |
| design/ecad/ring/open-pins.csv | 3 | X1, P2, X2 | 14 |
| design/ecad/ring/open-pins.csv | 4 | X2, P1, X1 | 14 |
| design/ecad/ring/open-pins.csv | 5 | X2, P2, X2 | 14 |
| design/ecad/ring/open-pins.csv | 6 | BT1, P1, + | 162 |
| design/ecad/ring/open-pins.csv | 7 | BT1, P2, - | 162 |
| design/ecad/ring/open-pins.csv | 8 | J1, P1, ELVSS | 50 |
| design/ecad/ring/open-pins.csv | 9 | J1, P2, ELVDD | 50 |
| design/ecad/ring/open-pins.csv | 10 | J1, P3, MTP | 50 |
| design/ecad/ring/open-pins.csv | 11 | J1, P4, VCI | 50 |
| design/ecad/ring/open-pins.csv | 12 | J1, P5, IOVCC | 50 |
| design/ecad/ring/open-pins.csv | 13 | J1, P6, SWIRE | 50 |
| design/ecad/ring/open-pins.csv | 14 | J1, P7, TE | 50 |
| design/ecad/ring/open-pins.csv | 15 | J1, P8, RESX | 50 |
| design/ecad/ring/open-pins.csv | 16 | J1, P9, CS | 50 |
| design/ecad/ring/open-pins.csv | 17 | J1, P10, SCL | 50 |
| design/ecad/ring/open-pins.csv | 18 | J1, P11, RS | 50 |
| design/ecad/ring/open-pins.csv | 19 | J1, P12, SDA | 50 |
| design/ecad/ring/open-pins.csv | 20 | J1, P13, GND | 50 |
| design/ecad/ring/open-pins.csv | 21 | J1, P14, GND | 50 |
| design/ecad/ring/open-pins.csv | 22 | J1, P15, GND | 50 |
| design/ecad/ring/open-pins.csv | 23 | J_BAND_A, 1, UP | 31 |
| design/ecad/ring/open-pins.csv | 24 | J_BAND_A, 2, DOWN | 31 |
| design/ecad/ring/open-pins.csv | 25 | J_BAND_A, 3, LEFT | 31 |
| design/ecad/ring/open-pins.csv | 26 | J_BAND_A, 4, RIGHT | 31 |
| design/ecad/ring/open-pins.csv | 27 | J_BAND_A, 5, CENTRE | 31 |
| design/ecad/ring/open-pins.csv | 28 | J_BAND_A, 6, MOT- | 31 |
| design/ecad/ring/open-pins.csv | 29 | J_BAND_A, 7, MOT+ | 31 |
| design/ecad/ring/open-pins.csv | 30 | J_BAND_A, 8, GND | 31 |
| design/ecad/ring/open-pins.csv | 31 | J_BAND_B, 1, CELL+ | 31 |
| design/ecad/ring/open-pins.csv | 32 | J_BAND_B, 2, CELL- | 31 |
| design/ecad/ring/open-pins.csv | 33 | J_BAND_B, 3, NTC | 31 |
| design/ecad/ring/open-pins.csv | 34 | J_BAND_B, 4, VBUS | 31 |
| design/ecad/ring/open-pins.csv | 35 | J_BAND_B, 5, D- | 31 |
| design/ecad/ring/open-pins.csv | 36 | J_BAND_B, 6, D+ | 31 |
| design/ecad/ring/open-pins.csv | 37 | J_BAND_B, 7, GND | 31 |
| design/ecad/ring/open-pins.csv | 38 | SW1, P1, ~ | 163 |
| design/ecad/ring/open-pins.csv | 39 | SW1, P2, ~ | 163 |
| design/ecad/ring/open-pins.csv | 40 | SW2, P1, ~ | 163 |
| design/ecad/ring/open-pins.csv | 41 | SW2, P2, ~ | 163 |
| design/ecad/ring/open-pins.csv | 42 | SW3, P1, ~ | 163 |
| design/ecad/ring/open-pins.csv | 43 | SW3, P2, ~ | 163 |
| design/ecad/ring/open-pins.csv | 44 | SW4, P1, ~ | 163 |
| design/ecad/ring/open-pins.csv | 45 | SW4, P2, ~ | 163 |
| design/ecad/ring/open-pins.csv | 46 | SW5, P1, ~ | 163 |
| design/ecad/ring/open-pins.csv | 47 | SW5, P2, ~ | 163 |
| design/ecad/ring/open-pins.csv | 48 | M1, P1, + | 46 |
| design/ecad/ring/open-pins.csv | 49 | M1, P2, - | 46 |
| design/ecad/ring/open-pins.csv | 50 | DISP1, 3, MTP | 51 |
| design/ecad/ring/open-pins.csv | 51 | DISP1, 4, VCI | 51 |
| design/ecad/ring/open-pins.csv | 52 | C71, , order code | 127 |
| design/ecad/ring/open-pins.csv | 53 | C85, , order code | 127 |
| design/ecad/ring/open-pins.csv | 54 | C88, , order code | 127 |
| design/ecad/ring/open-pins.csv | 55 | C86, , order code | 127 |
| design/ecad/ring/open-pins.csv | 56 | C87, , order code | 127 |
| design/ecad/ring/open-pins.csv | 57 | L71, , value or part number | 128 |
| design/ecad/ring/open-pins.csv | 58 | L72, , value or part number | 128 |
| design/ecad/ring/open-pins.csv | 59 | RT1, , value or part number | 34 |
| design/ecad/ring/open-pins.csv | 60 | C35, , order code | 127 |
| design/ecad/ring/open-pins.csv | 61 | C36, , order code | 127 |
| design/ecad/case/open-pins.csv | 2 | U2, PAD, PowerPAD | 80 |
| design/ecad/case/open-pins.csv | 3 | BT1, P1, + | 82 |
| design/ecad/case/open-pins.csv | 4 | BT1, P2, - | 82 |
| design/ecad/case/open-pins.csv | 5 | J1, SH, SHELL | 80 |
| design/ecad/case/open-pins.csv | 6 | U4, P1, CLK | 81 |
| design/ecad/case/open-pins.csv | 7 | U4, P2, CMD | 81 |
| design/ecad/case/open-pins.csv | 8 | U4, P3, DAT0 | 81 |
| design/ecad/case/open-pins.csv | 9 | U4, P4, DAT1 | 81 |
| design/ecad/case/open-pins.csv | 10 | U4, P5, DAT2 | 81 |
| design/ecad/case/open-pins.csv | 11 | U4, P6, CD/DAT3 | 81 |
| design/ecad/case/open-pins.csv | 12 | U4, P7, VDD | 81 |
| design/ecad/case/open-pins.csv | 13 | U4, P8, GND | 81 |
| design/case/c5d-open-points-handover.md | 43 | Harwin P70 pin still proposed, stroke not confirmed | 84 |
| design/case/c5d-open-points-handover.md | 44 | moulder walls 0.79 mm not confirmed; stake strength not tested; five wires not modelled; E1 reads through a 1.97 mm wall (bench B3) | 85, 86, 87 |
| design/case/c5d-open-points-handover.md | 45 | ring checked in seated pose only; straight lift not simulated | 95 |
| design/case/c5d-open-points-handover.md | 46 | other pictures are C5c renders | 95 |
| design/case/c5d-open-points-handover.md | 1-41 (six-point table, Findings, Files changed, Checks) | every row reads as held or closed (six points marked hold; findings closed); the rebuild rule is a condition, not an open item | none |


## Part 4. Search record

Source list: `find design` with the brief's folder prunes and `-name` prunes (out, evidence, logs, sandbox, concepts, options, feedback, old_C5, src_text, __pycache__), file kinds .md .csv .json .py .txt .sh, then `grep` excluded `*.log`. That gives 351 files; `requirements.md` is added (352 files). `design/firmware.md` is searched only at lines 1176 to 1201.

Commands (each run over the 352 files, case-insensitive, binary files skipped):

1. `grep -i -I -w -F -h -- "<phrase>" <352 files>` once per phrase (word-bounded). Hits per phrase below; the substring count (no `-w`) is in the last column.

2. `grep -i -I -w -E -n -- "<all phrases as one alternation>" <352 files>` gave 2,832 hit lines (`hits_all`). `design/firmware.md` with the same command gave 159 hit lines; 11 fall in lines 1176 to 1201 (kept as the search scope). Total in scope: 2843 hit lines; 1861 distinct sentences (`uniq_idx`).
3. Kept and dropped counts: a per-hit split for each phrase was NOT made (not done: 2,843 hit lines and 80 tool calls). Every distinct sentence was read in batches and classified; the kept ones are the Part 1 items (163 items, 245 quoted fragments checked against their cited files). Dropped hit lines, by source kind, were: code lines (574 hits in `.py` files), vendor datasheet and source text (70 hits), test fixtures under `testdata/` (98), planning JSON (5), and the `drc-report.txt` unconnected-item lines (225 hits, all counted as one item, number 1). Old copies in `old_*` folders and `c4`/`c5` notes repeat sentences that are merged into items; superseded notes were not counted again.

| Phrase | Word hits (-w) | Substring hits |
|---|---|---|
| layout engineer | 10 | 10 |
| engineer | 17 | 35 |
| has to | 11 | 11 |
| still has to | 1 | 1 |
| to be confirmed | 10 | 10 |
| confirm with | 73 | 73 |
| to confirm | 110 | 110 |
| ask the | 2 | 2 |
| maker must | 20 | 20 |
| supplier must | 1 | 1 |
| the fab | 3 | 3 |
| OPEN | 1143 | 1688 |
| ASSUMED | 185 | 185 |
| assumed | 185 | 185 |
| PROVISIONAL | 72 | 72 |
| provisional | 72 | 72 |
| TBD | 10 | 10 |
| to be decided | 1 | 1 |
| to decide | 0 | 0 |
| not decided | 3 | 3 |
| undecided | 0 | 0 |
| not verified | 30 | 30 |
| unverified | 31 | 31 |
| not read | 367 | 401 |
| unread | 1 | 2 |
| not checked | 34 | 34 |
| unknown | 30 | 31 |
| placeholder | 9 | 11 |
| estimate | 117 | 127 |
| retune | 6 | 8 |
| tuned on | 0 | 2 |
| bench | 555 | 574 |
| prototype will | 0 | 0 |
| later | 41 | 67 |
| open item | 150 | 169 |
| open point | 162 | 223 |
| not drawn | 26 | 26 |
| not routed | 4 | 4 |
| not built | 15 | 15 |
| missing | 281 | 283 |

Phrases with zero word hits: `to decide`, `undecided`, `tuned on`, `prototype will`. The phrase `to be decided` has 1 word hit.

Firmware section: `grep -n` over `design/firmware.md` lines 1176 to 1201 gave 11 hit lines (H1, H7, H10, H11, H12, H13, H14, H15, H16, H17 and H19, one line each), all read.


## Part 5. Not searched
- Folders named by the brief and excluded from the search: `design/review`, `design/.venv`, `design/datasheets`, `design/software`, `design/look`, `design/manufacturing-research`, `design/firmware-evidence`, `design/firmware-v7-evidence`, `design/protocol`. Any folder named `out`, `evidence`, `logs`, `sandbox`, `concepts`, `options`, `feedback`, `old_C5`, `src_text` or `__pycache__`. Every file ending in `.log`.
- Exact-path rule used: `design/case/look` and `design/mech/light-path/tools` are searched (only `design/look` is excluded).
- `design/firmware.md`: only lines 1176 to 1201 ("Hardware issues found") are searched. Lines 1202 onward (`questions_for_owner`) and the rest of the file are not searched.
- Files the search reached but did not classify one by one: the vendor text under `design/bench/sources`, `design/ecad/motor-drive/src_*`, `design/parts/nordic-ref-text` (70 hits, dropped as vendor text); the `testdata` fixtures (98 hits, copies of spec files; their open-point sentences repeat the real spec files); code (574 hits, read, kept only where a comment states open work).
- Pictures named `*open*.png` in `design/case` are not text and were not read. `design/case/look/render_open.log` is a log (excluded).
- Not verified outside the files: no maker website, datasheet or price was checked; every value is as the files state it.
- Raw hit lists and scripts are in the session scratchpad (not the project): `<scratch>/hits_all.txt`, `<scratch>/hits_scope.txt`, `<scratch>/uniq_idx.txt`, `<scratch>/items_raw.txt`, `<scratch>/audit2.py`.

RESULT: done, 163 open items are listed in Part 1 from 2,843 search hit lines, and 1,861 distinct sentences were read and classified.
