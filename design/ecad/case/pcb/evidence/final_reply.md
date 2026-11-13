Round 2 is done. RESULT: done. Both boards pass the rules check, and check_boards.py exits 0. Notes: design/ecad/case/pcb/board-notes.md (section "Round 2" is last; its last line starts with RESULT:).

Rules check (`kicad-cli pcb drc --severity-all --all-track-errors`):
- case_main.kicad_pcb: Found 0 violations, Found 0 unconnected items (evidence/drc_case_main_final.log).
- case_pins.kicad_pcb: Found 0 violations, Found 0 unconnected items (evidence/drc_case_pins_final.log).
- check_boards.py: `RESULT PASS check_boards case_main.kicad_pcb case_pins.kicad_pcb`, exit 0. The four broken copies each exit 1 with their own FAIL line (evidence/broken_exits.txt).

What was done, by ruling:
1. In1 is the ground plane, In2 the 3V3 plane; every ground and 3V3 pad has a stub and a via; no track on In1 or In2.
2. Rules: signal track and gap 0.10 mm, via 0.20 / 0.50 mm (ring 0.15 mm), power widths as before. The capability page lines are quoted in the notes. One setting of mine: the KiCad "minimum connection width" check is off for PCB1 (it flagged one 0.031 mm neck of a pour whose via is also on the In1 plane).
3. Length: 2.5 mm used, 35.4 to 37.9 mm, toward the socket side, inside the cavity (case.py line 142). Other files need case.py line 737 and line 141 changed.
4. USB on PCB1: D+ 21.050 mm, D- 21.750 mm, difference 0.700 mm (limit 5.0 mm). PCB2: 1.750 mm each.
5. Both simulation circuit changes were already in (CE pulled to 3V3, LED anode on SYS, R8 510, R9 and R10 270 ohm); ERC 0 errors, check_netlist.py `RESULT PASS`.
6. fab/ rewritten from the finished boards only (3.2 MB).
7. STEP models: KiCad library models for R and C 0402, C 0603, C 0805, SOT-23-6, QFN-24 (U2) and the USB-C socket (52 parts). Plain boxes of the maker's size for U1, L1, L2, U3, U4, U6, LED1 and cylinders for the four spring pins. No model for pads, E1, TH1, the cell.
8. Scratch folder pcb/work (261 MB) deleted; the pcb folder is 19 MB. Cited files are in evidence/kept/.

Method: my own grid router, run on this Mac (small program), best of several runs with 0 conflicts and 0 unrouted; the server was not used in round 2.

Wire cut lengths are now 13 to 16 mm (all inside the case-bom lengths).

Open points, in the notes: the 16 test pads are bare copper on the bottom face (no room on top); chip land patterns are IPC-7351B nominal; the voltage of a floating module pin on the LED cathodes is not bounded by the sheet.
