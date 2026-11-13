# Complete design package: the bar and the plan

Written by the lead, 2026-11-12. This file is the plan of record for the owner's request below. It survives a session change: read it first.

## The owner's words (2026-11-12)

- about 23:13: "you're missing all the wiring and all. Please make the design 100%"
- about 23:16: "don't offload any work to any other engineer. It needs to be ready to build from a stupid person"
- about 23:27: "expecting it as good as thid: <home>/Downloads/memo-nrf52840-usb-c-dual-microphone-board-package.zip"

## The bar (what the reference package holds; read by the lead at 23:30)

| The reference has | Its figures | OpenRing today |
|---|---|---|
| A board file that opens in KiCad fully routed | 52 x 28 mm, 4 copper layers, 54 parts, 470 track segments, 183 vias, 5 copper zones | ring board: 100 parts placed, 0 tracks, built from an older circuit; case boards: no file; band circuits: no file |
| Its own footprint library, one exact footprint per part | 16 footprints | ring: 13 footprints marked provisional, 60 open pin rows; case: 12 open pin rows |
| The schematic | 111 symbols, 33 nets | ring: 118 parts, 93 nets, checks pass; case: 89 parts, 61 nets |
| A 3D file of the assembled board | board.step | none for the boards |
| Design data: rules, net classes, layer stack | design.json | ring rules chosen, stack assumed |
| Firmware with the real board definition (pins) | Zephyr app, devicetree, flash scripts | ring software steps 1 to 5; the board definition is step 7 |
| A build sheet | build_sheet.md | assembly notes exist; no step-by-step guide for a first-time builder |

The reference is another maker's package. Nothing of it is copied into this project or into the public repository.

## What "100 percent" means here (lead's reading, told to the owner)

1. Every connection of `connections.md` is drawn in a board file or a wiring drawing, with both ends named.
2. Every board passes KiCad's rules check with 0 violations and 0 unconnected pads, and has its fabrication files.
3. No file leaves work to another person: each of the 163 lines of `deferred-items.md` gets a fixed value with its source, or a step in the build guide with the tool and the expected reading.
4. A build guide takes a first-time builder from ordering to a working ring and case.
5. Limit that cannot be removed on paper: values that only a built unit can show (antenna match on the real body, cell limits from its maker, acoustic results). For each, the design fixes a start value from the maker's public document and the build guide gives the measurement and the action. The lead says so wherever it applies; it never claims such a value as proven.

## Work packages

| # | Package | Output | Depends on |
|---|---|---|---|
| W1 | Ring footprints and open parts | exact footprints from maker documents, part numbers for every open line, pin numbers closed in the netlist scripts | none |
| W2 | Ring board stack, rules, antenna mount | written decisions with sources (Nordic reference layout, antenna maker's layout) | route trial, W1 |
| W3 | Ring board placement and routing | `design/ecad/ring/pcb/ring.kicad_pcb` routed, 0 and 0, fabrication files, board STEP | W1, W2 |
| W4 | Band flexible circuits (two tails) | board files with switches, motor, cell tabs, sensor, charging pads; outline from the band model | interface with W3 fixed by the lead |
| W5 | Case boards (main board and pin board) | board files routed, 0 and 0, fabrication files, STEP | none |
| W6 | Product wiring drawing | one drawing of all 21 connections, both ends, wire lengths | W3, W4, W5 |
| W7 | Deferred items | every line of `deferred-items.md` closed or moved into the build guide | runs beside all |
| W8 | Board definition in the firmware | pins of the routed board in the ring software (software step 7) | W3 |
| W9 | Build guide | `design/build-guide.md` | all |
| W10 | Independent review, then the app and the public repository | review file, published package | all |

Added after the list of open items was sorted (`deferred-triage.csv`, one line per item with its package):

| # | Package | Output | Depends on |
|---|---|---|---|
| W11 | Mechanics, screen cable, cell and seals (30 items) | the open values settled in the models and part specifications: the screen cable at the fold (12.4 mm stock against 5.0 mm in the model), the motor clearance on sizes US 9 to 13, the seals of the two openings, the inside model for design v7 | none |
| W12 | Assembly steps and materials (11 items) | every material with a part number, every step in an order that can be built | W11 |
| W13 | Documents (4 items) | the architecture sections that still describe older rings rewritten | all |

Items per package: W1 24, W2 7, W3 4, W4 6, W5 11, W7 15, W8 4, W9 25, W11 30, W12 11, W13 4. 17 items describe parts or options the design no longer uses (no action). 5 are owner decisions already taken or not needed to build.

## State

- 23:35: inventories done (`connections.md`, `deferred-items.md`). A routing trial on a copy of the placed board runs (`probe/route-probe.md`).
- 23:38: running: ring-parts (W1), case-boards (W5), route-probe (trial; first pass left 88 of 124 items unrouted), os-relay (relay step, round 2). Open items sorted into packages (deferred-triage.csv).
- 23:39: W2 input read by the lead: Nordic's reference layout for the main chip's package (design/datasheets/nrf54lm20x_caaa_ref_pcb_0_2.pdf, 14 pages) has 8 copper layers (pages: Top Side, Mid-Layer 1 to 6, Bottom Side), board area 10.05 x 10.90 mm (page 12), the antenna match parts L2, C3, L3, C12, L4, C13 directly beside the chip (page 13). The ring board is planned with 6 layers and 0.30 mm thickness: the stack is decided in W2 after the routing trial.
- 00:02: routing trial ended (137 of 225 by the automatic router; stops at U1 and U2). Started: ring-board-plan (opus, W2: stack, vias, ball escapes, antenna mount, placement zones, routing method; design/wiring/ring-board-plan.md). W11 (mechanics) and W12 (assembly) start after band-circuits and ring-board-plan report, because both will list changes the models need and both read the models now.

## Simulation and test bench (owner, 2026-11-13 about 00:04: "can you find a way of properly simulating the PCB and board and all and testing ti ?")

Five levels, each with a pass line written before its run and a broken copy that must fail. Work list items under "Design the ring hardware"; plan file `design/sim/plan.json`.

| # | Level | What it shows | What it cannot show | Tool | Starts |
|---|---|---|---|---|---|
| S1 | Circuit simulation | rail levels, the cell's dip at a motor start, charge current and end voltage, inrush, logic levels, pad voltage on the finger | anything a maker gives no figure for; the real cell | ngspice (inside KiCad 10.0.8), decks made from the netlists | 00:08, helper circuit-sim |
| S2 | Antenna field simulation | the antenna's match and radiated share inside the metal body on a finger, start values for the match parts; first checked against the antenna maker's own evaluation board | the exact figure of a built ring (model accuracy) | openEMS on the build server | 00:08, helper antenna-sim |
| S3 | Routed boards read back | the fabrication files hold the same connections as the circuit; resistance and drop of power paths; impedance of the antenna line and the USB pair | solder quality, a maker's errors | KiCad exports (IPC-D-356, Gerber), scripts | after W3, W4, W5 |
| S4 | Ring software on the real pin map | each pin the software uses is the ball the circuit gives it; the software tests pass with the real board definition on the simulated chip | timing and drivers on real silicon | the software's own test run on the build server | after W3 and software step 7 |
| S5 | Boards in the 3D models | no collision, stated clearances, every ring size | tolerances of real parts | the model scripts | after W3, W4, W5 |

After the simulations: the build guide (W9) carries the tests for the first built boards (power-up steps with expected readings, the factory tests of the behaviour specification).
- 00:34: band circuits delivered and rerun by the lead (14 boards pass). Started model-band-fit: the 3D model takes the tails as drawn (1.8 mm neck) and the fit check runs at US 7 to 13. Only reader of design/mech/thin/out besides it: antenna-sim (reads, never writes).
- 00:37: ring footprints delivered and rerun by the lead (27 footprints, 410 pins). Round 2 sent (band library for band parts, C60, maker sheets through the reader part-docs). Facts passed to ring-board-plan: J1 is 6.1 x 4.2 mm, the Class 1 capacitors are 0805 so far.
- 00:39: ring board plan read and decided: 4 layers, laser microvias, 0.30 mm, antenna on the board, no notch. Round 2 runs: the plan against the real footprints, with a complete placement table. The relay step: round 2 committed, the lead's full rerun and a second review run.
- 00:53: ring footprints closed (9a6c1c3). Started ring-board (opus builder, W3, limit 5 h): circuit changes of the plan, the board rebuilt on 4 layers with the two libraries, scripted ball escapes, placement, routing, checks, fabrication files; if 4 layers leave a connection open it stops and reports, no extra layer. Relay step: second review read, round 3 with the builder.
- 01:24: circuit simulation delivered: 12 tests, 4 findings on the design, decided (discharge resistor on the ring's VBUS, C84 4.7 uF, case charger held off until set, case light on SYS); changes with ring-board and case-boards.
- 01:26: antenna simulation round 1: tool not validated (the chip antenna's inside is not published), ring cases 8.3 and 2.0 percent radiated, nothing decided. Round 2 ordered with a validation on a published printed antenna, a calibrated stand-in, eight ring cases.
