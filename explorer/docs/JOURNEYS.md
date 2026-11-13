# Journeys: Ring Explorer
real-data: the ring design in this project at git commit 7274c69 (77 parts-list lines; example parts: U1 main chip nRF54LM20A, BT1 cell 135 mAh, SW1 joystick SKRHADE010), confirmed by the owner 2026-11-10
state-home: see docs/DATA-MAP.md

One role: the owner (later a build partner with the same rights). The app is read-only, so every "writes" cell is "none" and "may" is always "view".

## J1: See the ring and understand one part   (roles: owner)
Trigger: the owner wants to know what is inside the ring · Done when: a part card shows what the part is, why it is there, and its order code

| step | actor · may | screen | arrives by (from screen · control) | sees | does | reads (DATA-MAP row) | writes | visible result | needs first | on failure | test |
|---|---|---|---|---|---|---|---|---|---|---|---|
| J1.1 | owner · view | Home | typed address localhost | the ring in 3D, 5 key numbers, 8 area tiles with their state | rotates the ring | ring-model, key-numbers, area-states | none | the ring turns; numbers read 30 x 20 x 9.5 mm, 135 mAh | data bundle built by the collector | a message "run npm run collect" with the command | J1#1 |
| J1.2 | owner · view | Inside | Home · tile "Inside" | the ring assembled, a slider "open it up" | drags the slider | ring-model, part-placements | none | glass, screen, board, cell and housing separate into layers | part-placements from the 3D model | layers that have no model are listed as text | J1#2 |
| J1.3 | owner · view | Inside | Inside · click on the cell | the cell highlighted, a part card on the side | reads | parts, part-notes | none | card: "Battery cell. Stores the energy. Custom order, 4.6 x 13 x 25 mm, 135 mAh minimum. Open: quote from Grepow" | parts list line BT1 | card says "no parts-list line for this object" | J1#3 |
| J1.4 | owner · view | Inside | part card · link "source" | the source file or datasheet of that figure | opens it | files | none | the datasheet PDF or the note opens in a new tab | file exists in design/datasheets | the link is shown greyed with "not on disk" | J1#4 |

## J2: Compare the exterior options   (roles: owner)
Trigger: the owner must pick the ring's look · Done when: the three options are seen side by side in the same view and finish

| step | actor · may | screen | arrives by | sees | does | reads | writes | visible result | needs first | on failure | test |
|---|---|---|---|---|---|---|---|---|---|---|---|
| J2.1 | owner · view | Look | Home · tile "Look" | options A, B, C in 3D, each with its two-line thesis and what it is worse at | rotates one | look-options | none | all three rotate together or one alone | look-options from design/look | a missing option shows a labelled placeholder | J2#1 |
| J2.2 | owner · view | Look | Look · switch "finish" | four finishes | picks Slate Titanium | look-options | none | body and band change colour on all options | none | none | J2#2 |
| J2.3 | owner · view | Look | Look · switch "view" | three-quarter, top, side, on a finger | picks "on a finger" | look-options | none | the ring sits on a finger-sized cylinder | none | none | J2#3 |

## J3: Check where the design stands   (roles: owner)
Trigger: the owner wants to know what is finished and what is open · Done when: each open item names who must act

| step | actor · may | screen | arrives by | sees | does | reads | writes | visible result | needs first | on failure | test |
|---|---|---|---|---|---|---|---|---|---|---|---|
| J3.1 | owner · view | Home | typed address or the top bar "Home" | 8 area tiles: done, in progress, not started, waiting on a supplier | clicks the tile "Board" state | area-states | none | goes to Board | area-states from the project record export | tile shows "state unknown" | J3#1 |
| J3.2 | owner · view | Board | Home · tile "Board" | a banner "not routed yet" and the placement plan | reads | board-files, area-states | none | the banner names what is missing | none | none | J3#2 |
| J3.3 | owner · view | Open items and files | top bar · "Open items" | supplier requests (7), bench tests (5), risks, past decisions with dates | filters "waiting on a supplier" | open-items, decisions | none | the list shortens to supplier items, each with who and what to ask | open-items from architecture section 12 and 13 | empty filter says "nothing waiting" | J3#3 |

## J4: Follow the circuit from a block to a part   (roles: owner, partner)
Trigger: the owner or partner wants to see how a function is wired · Done when: the wiring page of that function is on screen and its parts are listed

| step | actor · may | screen | arrives by | sees | does | reads | writes | visible result | needs first | on failure | test |
|---|---|---|---|---|---|---|---|---|---|---|---|
| J4.1 | owner · view | Electronics | Home · tile "Electronics" | the block diagram: chip, 4 microphones, storage, screen, power, controls, case link | clicks "Microphones" | blocks, schematic-pages | none | the microphone page of the wiring diagram opens beside the diagram | schematic exported as SVG | page shown as PDF link if no SVG | J4#1 |
| J4.2 | owner · view | Electronics | Electronics · page list | the 8 pages | zooms into U5 | schematic-pages | none | the page zooms; U5 IM73D122V01 is readable | none | none | J4#2 |
| J4.3 | owner · view | Parts | Electronics · "parts of this page" | the parts list filtered to the microphone page | clicks U5 | parts | none | the part card of the microphone opens | parts list | none | J4#3 |

## J5: See how the ring behaves   (roles: owner)
Trigger: the owner wants to check the recording rule · Done when: a long press on the virtual button starts a recording and the light turns on

| step | actor · may | screen | arrives by | sees | does | reads | writes | visible result | needs first | on failure | test |
|---|---|---|---|---|---|---|---|---|---|---|---|
| J5.1 | owner · view | Behaviour | Home · tile "Behaviour" | the ring with a virtual joystick (its centre press is the only button), the state name "Standby" | holds the joystick's centre 1 second | firmware-rules | none | state "Recording", red light on, one vibration mark, timer runs | firmware-rules from firmware.md | none | J5#1 |
| J5.2 | owner · view | Behaviour | Behaviour · the joystick's centre | the recording state | taps the centre once | firmware-rules | none | a highlight mark appears; the recording continues | none | none | J5#2 |
| J5.3 | owner · view | Behaviour | Behaviour · the joystick's centre | the recording state | holds the centre 1 second | firmware-rules | none | state "Standby", light off, two vibration marks | none | none | J5#3 |

## J6: Hand the design to a build partner   (roles: owner)
Trigger: the owner wants to send the design to a firm · Done when: one archive with every design file is downloaded

| step | actor · may | screen | arrives by | sees | does | reads | writes | visible result | needs first | on failure | test |
|---|---|---|---|---|---|---|---|---|---|---|---|
| J6.1 | owner · view | Open items and files | top bar · "Files" | every file grouped by area with size and date | clicks "Download partner bundle" | files | none | a zip downloads; the page lists what it contains | bundle built by the collector | button disabled with "run npm run collect" | J6#1 |
| J6.2 | owner · view | Parts | top bar · "Parts" | the full parts list with totals | clicks "Export CSV" | parts | none | bom.csv downloads | none | none | J6#2 |

## J7: See the charging case   (roles: owner)
Trigger: the owner wants to see the case · Done when: the case is seen in 3D with the ring seated

| step | actor · may | screen | arrives by | sees | does | reads | writes | visible result | needs first | on failure | test |
|---|---|---|---|---|---|---|---|---|---|---|---|
| J7.1 | owner · view | Case | Home · tile "Case" | the closed case in 3D, size 33.6 x 33.4 x 55.2 mm, 700 mAh, 6.3 minutes per recorded hour | opens the lid | case-model, case-facts | none | the lid opens and the ring shows on its 4 pins | case-model from design/case | none | J7#1 |
| J7.2 | owner · view | Case | Case · click on the pins | the pins highlighted and their part card | reads | case-parts | none | card: spring pins, VBUS, D-, D+, GND | case parts list | none | J7#2 |

## Screen links (derived from every "arrives by" cell)

| screen | link in (from · control · step) | link out (to · control · step) | owning lane |
|---|---|---|---|
| Home | typed address (J1.1) · top bar "Home" (J3.1) | 8 area tiles to each screen (J1.2, J2.1, J3.1, J4.1, J5.1, J7.1) | named at the plan step |
| Look | Home tile (J2.1) | top bar | named at the plan step |
| Inside | Home tile (J1.2) | part card "source" to a file (J1.4) | named at the plan step |
| Electronics | Home tile (J4.1) | "parts of this page" to Parts (J4.3) | named at the plan step |
| Board | Home tile (J3.2) | part card | named at the plan step |
| Parts | top bar (J6.2) · Electronics (J4.3) | part card; export | named at the plan step |
| Behaviour | Home tile (J5.1) | top bar | named at the plan step |
| Case | Home tile (J7.1) | part card (J7.2) | named at the plan step |
| Open items and files | top bar (J3.3, J6.1) | file download (J6.1) | named at the plan step |

SIGN-OFF: owner, 2026-11-10, walked on the diagram: "Approve the journeys (Recommended)"

CHANGE after sign-off, 2026-11-10: J7.1 transfer figure 6.4 corrected to 6.3 minutes per recorded hour (design/architecture.md section 8). Approved by the owner in plan mode with the build plan, reading 5: "One figure in the journeys is corrected: data transfer takes 6.3 minutes per recorded hour".

Change after sign-off, 2026-11-10, asked by the owner: "I think we may not need a button on top of joystick and just have long press on joystick as recording button. So D1 but just joystick, no button". J5.1 to J5.3 now press the joystick's centre; the separate record button is gone from the ring and from the screen. Nothing else in the journeys changed.
