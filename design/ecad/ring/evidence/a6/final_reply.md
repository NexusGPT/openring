A6 report. Changes (a) to (h) are all done. No commit (git is outside Owns).

Folders: ring = design/ecad/ring ; proofs = design/ecad/ring/evidence/a6 ; parts list = design (bom.csv, bom-notes.md note appended).

Checks (logs in proofs):
- check_netlist.py: last line "RESULT PASS netlist netlist.csv", exit 0, 39 ok lines (check_netlist_final.log). Broken copies, each exit 1: b1 removes the net from U10 pin 12 (4 FAIL lines), b2 joins U3 CLK to SD_SCK (4), b3 puts J_BAND_A pad 7 on GND (2), b4 puts CP1 on VBUSOUT (7) (broken/).
- ERC: kicad-cli sch erc --severity-all --exit-code-violations -o erc_final_report.txt ring.kicad_sch: exit 0, "Found 0 violations" (erc_final.log).
- check_bom.py: "lines 78, designators 130, section-2 rows 21, section-2 part tokens 27, failures 0", exit 0 (check_bom_final.log). Every reference is one token without spaces.
- One-edit proof: motor rows of BAND_SPLIT set to side B gave PASS and 0 ERC violations with 6 and 9 pads (swap/ and evidence/check_a6_swapB.log), then restored; delivered split: 8 pads on A, 7 on B.

Settled:
(a) U2 nPM1304 CSP-35, order code empty ("S18: Nordic"), all 33 balls provisional in open-pins.csv (105 rows in all); passives and VSET resistors kept, marked "to confirm against the nPM1304 product specification".
(b) CAP2 removed, CAP1 kept, SW2 stays on BTN_REC as the nub's centre switch.
(c) sch-notes.md 11.2: VBUS has one source (pad CP1); D- and D+ hold only U1, U9, pad, tail; U9 TPD4E05U06 stays (12 kV contact, 5.5 V stand-off). The chip's D+/D- state without VBUS has no source in the project: O4.
(d) F07 confirmed: storage VIH 0.625 x 3.0 V = 1.875 V is above the chip's 1.8 V; the chip has one I/O supply (A4, E10); the storage part has no 1.8 V option. Added U10 SN74AXC4T774RSVR (TI SCES898C, no supplier contact), C81, C82. The board does not have U10 yet.
(e) BAND_SPLIT table at make_netlist.py line 128; the motor is on side A, the lead confirms (O2).
(f) Only 15 mA and 4.35 V remain (check A6-5). (h) 67.5 dB(A).
(g) F14: the 8 x 10 name grid is right (19 of 80 sites empty); the 9 x 7 reading with 0.325 mm pitch cannot fit the 3.02 mm body; the pitch is open to Nordic (O5).

Conflicts in read-only files (both lines in sch-notes.md 11.6): research-npm1304.md lists nPM1304-CAAA-R, the brief says no order code is there (not used); architecture.md still has 4.40 V, 68 dB(A) and the nPM1300 row; pcb/build_board.py hardcodes 6 pads, so the board must be rebuilt for U2, U10, C81, C82 and the 8 and 7 pads.
Open points: O1 Nordic (ball map, order code, passives); O2 lead (motor tail); O3 lead (U10 against VDD 3.0 V); O4 Nordic (USB pads); O5 Nordic (package drawing); O6 ring maker and case designer; O7 owner (RT1, sizes); O8 board owner and lead.
Not done: git status of proofs (git is not mine); prove_a5.sh, prove_fail.sh not rerun (not owned).

RESULT: done, check_netlist.py ends "RESULT PASS netlist netlist.csv" (exit 0), KiCad ERC "Found 0 violations" (0 errors), check_bom.py 0 failures; F07 settled with the level shifter U10 SN74AXC4T774RSVR on sources (chip I/O follows VDD at 1.8 V, storage VIH 1.875 V at 3.0 V, storage has no 1.8 V option) and F14 settled as the 8 x 10 name grid right with the ball pitch left open to Nordic; open points O1 to O8
