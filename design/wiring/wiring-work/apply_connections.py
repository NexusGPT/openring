#!/usr/bin/env python3
"""Bring the "Drawn?" cell of each joint of connections.md Part 1 to the files of 13 November (bar 5).
Only the last cell of each Part 1 row changes; the table keeps its 8 columns. A dated note goes at the top,
one dated line at the top of Parts 2 to 6, and the sentence after "Count: 21 joints (...)." is brought up to date."""
import re
import sys

F = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/connections.md")
DATE = "2026-11-13 08:05 CET"
CSV = "design/wiring/product-wiring.csv"

CELLS = {
    "R1": "Drawn (13 Nov): RPCB lands J_BAND_A 1 to 8 (footprint J_BAND_A_BOARD) carry the RN nets; the 7 FLEX1 boards design/ecad/band/flex1-us7 to us13 carry the tail lands J_BAND_A_TAIL 1 to 8; hot bar (band-interface.md line 60). %s: the 10 lines that start at these lands are `drawn and routed`." % CSV,
    "R2": "Drawn (13 Nov): RPCB lands J_BAND_B 1 to 7 (footprint J_BAND_B_BOARD) carry the RN nets; the 7 FLEX2 boards flex2-us7 to us13 carry J_BAND_B_TAIL 1 to 7; hot bar. %s: the 7 lines that start at these lands are `drawn and routed`." % CSV,
    "R3": "Drawn and routed (13 Nov) in the 7 FLEX1 boards: J_BAND_A lands 1 to 4 to terminal 3 of SW1, SW3, SW4, SW5, land 5 to SW2 terminals 1 and 3 (Alps numbers, band-interface.md section 4). Terminal 1 of SW1, SW3, SW4, SW5 is not soldered (joined to 3 inside the part). %s: 10 lines, all `drawn and routed`." % CSV,
    "R4": "Drawn and routed (13 Nov) in the 7 FLEX1 boards: switch terminal 4 (and 2 of SW2) on a B.Cu GND star to J_BAND_A lands 6 and 8 (band-notes.md section g item 3). %s: 10 lines, all `drawn and routed`." % CSV,
    "R5": "Drawn and routed (13 Nov): FLEX1 lands W0525AB001D_Lands 1 (VMOT) and 2 (GND) to J_BAND_A lands 7 and 6 in the 7 FLEX1 boards; red lead to land 1, blue to land 2, AWG32, cut length per size (band-interface.md section 6). %s: 4 lines (2 copper, 2 leads), `drawn and routed`." % CSV,
    "R6": "Drawn and routed (13 Nov): FLEX2 lands PRT1_Tabs 1 (VBAT) and 2 (GND) to J_BAND_B lands 1 and 2 in the 7 FLEX2 boards. The tabs on these lands are the PRT1 output tabs (row R10). %s: 2 copper lines `drawn and routed`." % CSV,
    "R7": "Drawn and routed (13 Nov): FLEX2 land PRT1_Tabs 3 (NTC) to J_BAND_B land 3 in the 7 FLEX2 boards. RT1 sits on the PRT1 board and reaches that land through tab NTC (row R10, text only). RT1 order code NCP15XH103F03RC (RP). %s: 1 line `drawn and routed`." % CSV,
    "R8": "Stated in text only (13 Nov): RT1 pin 2 is joined on the PRT1 board to tab P-, which lands on FLEX2 land PRT1_Tabs 2 and so on J_BAND_B land 2 (band-interface.md line 114; cell.md line 84). The PRT1 board is drawn in no file. %s: 1 line `stated in text only`." % CSV,
    "R9": "Drawn and routed (13 Nov): CP1 to CP4 (CP_Pad_1.6, 1.6 mm disc lands on B.Cu) to J_BAND_B lands 4 to 7 in the 7 FLEX2 boards; RP rows CP1 to CP4 now say 1.6 mm. Gold disc soldered on each land (band-interface.md section 8). %s: 4 lines `drawn and routed`." % CSV,
    "R10": "Stated in text only (13 Nov; was NOT DRAWN): band-interface.md section 5 and cell.md lines 83 and 84 give the three output tabs P+ (BT1 pin 1, VBAT), P- (BT1 pin 2, GND), NTC (RT1 pin 1) and their order; their FLEX2 lands PRT1_Tabs 1, 2, 3 are drawn in the 7 FLEX2 boards. PRT1 is not a part of RN or RP (RP names it only in BT1's footprint) and not in RPCB. Rows typed in design/wiring/system-joints.csv. %s: 3 lines (and R8)." % CSV,
    "R11": "Drawn (13 Nov): RN and RPCB; the antenna is on its maker's land pattern on the board's under face, no notch (lead-decisions.md row W2). The rules check run by build_wiring.py (design/wiring/wiring-work/drc/) shows no open connection at ANT1 pad 1 or on RF_FEED at the time of the build. The board is still being routed. %s: 1 line." % CSV,
    "R12": "Drawn (13 Nov): ANT1 pads 2 and 3 on ANT_TRIM (to LT1, 0 ohm) and pad 4 on GND in RN and RPCB; same rules check: no open connection at these pads at the time of the build. %s: 3 lines." % CSV,
    "R13": "Drawn (13 Nov) in RN and RPCB: J1 pads 1 to 15 carry the RN nets; contact k on position k (RS line 38); DISP1 pins 3 and 4 closed by the Tailor table page 5 (RS line 309). J1 is still on the under face (F.Cu) in RPCB; the decided place is the screen face (screen-cable-study.md section 4.3; lead-decisions.md row 'block height 4.17 mm'), moved by the board helper now. %s: 15 lines `drawn, not routed` (J1 face)." % CSV,
    "R14": None,
    "R15": "Stated in text only (13 Nov; was NOT DRAWN): the ring pad to case pin table of design/ecad/case/pcb/board-notes.md Part g (from CS 17). Each end is drawn in its own files (CP1 to CP4 in the FLEX2 boards; P1 to P4 in design/ecad/case/pcb/case_pins.kicad_pcb); no file holds both ends. Rows typed in design/wiring/system-joints.csv. %s: 4 lines." % CSV,
    "R16": "Stated in text only (13 Nov; was NOT DRAWN): no conductor by design. E1 is drawn in case_pins.kicad_pcb (net RING_TOUCH); the band is 2.28 to 2.42 mm from PCB2's front face behind the 1.97 mm pin holder wall (CA lines 64 and 235). Row typed in design/wiring/system-joints.csv. %s: 1 line." % CSV,
    "C1": "Drawn and routed (13 Nov): case BT1 red lead + to PCB1 pad W5 (design/ecad/case/pcb/case_main.kicad_pcb), cut 13.0 mm (case board-notes.md Round 2 wiring table). %s: 1 line." % CSV,
    "C2": "Drawn and routed (13 Nov): case BT1 black lead - to PCB1 pad W6, cut 15.2 mm (same table). %s: 1 line." % CSV,
    "C3": "Drawn (13 Nov): TH1 pins 1 (TS) and 2 (GND) to PCB1 plated holes TH1.1 and TH1.2 (footprint NTC_wired), 10 mm leads; TH1 is glued on the cell face (case board-notes.md conflict 3). %s: 2 lines." % CSV,
    "C4": "Drawn (13 Nov) in case_pins.kicad_pcb: P1 to P4 (footprint HARWIN_P70_6000045R) with nets VRING, USB_D-, USB_D+, GND; soldered to PCB2 (CA line 238). In %s the spring pins are the carriers of the 4 R15 lines." % CSV,
    "C5": "Drawn and routed (13 Nov): WP1 to WP4 and WP7 on case_pins.kicad_pcb, W1 to W4 and W7 on case_main.kicad_pcb, cut 15.6 to 16.3 mm (case board-notes.md Round 2 wiring table); the rules checks of both boards show no open connection. %s: 5 lines." % CSV,
    "C6": "Drawn (13 Nov) in CN and case_main.kicad_pcb (J1 USB4105 on PCB1). Not a conductor between boards or to an off-board part of the product: no line in %s." % CSV,
}

TOP = ("Update %s (product-wiring helper): the column \"Drawn?\" of Part 1 is brought to the files of 13 November "
       "(band circuits in design/ecad/band, routed case boards in design/ecad/case/pcb, the ring board as it was being "
       "routed). R10, R15 and R16 are no longer \"not drawn\": each is now stated in text with its source, and each "
       "conductor end to end is one line of %s (built by design/wiring/build_wiring.py, checked by "
       "design/wiring/check_wiring.py). Other columns and Parts 2 to 6 are not rewritten; they describe the files of "
       "12 November.\n\n" % (DATE, CSV))

PART_LINE = ("Note %s: this part describes the files of 12 November. The present state of each conductor is in %s "
             "and in the column \"Drawn?\" of Part 1.\n\n" % (DATE, CSV))

COUNT_OLD = "3 are not drawn: R10, R15, R16."
COUNT_NEW = ("On 13 November none is not drawn: R10, R15 and R16 are stated in text only (see %s); "
             "on 12 November 3 were not drawn." % CSV)

text = open(F, encoding="utf-8").read()
if "product-wiring helper" in text:
    sys.exit("already applied")
lines = text.split("\n")
changed = 0
in_part1 = False
for i, ln in enumerate(lines):
    if ln.startswith("## Part 1."):
        in_part1 = True
    elif ln.startswith("## Part 2."):
        in_part1 = False
    if in_part1 and ln.startswith("| ") and not ln.startswith("| #") and not ln.startswith("|---"):
        cells = ln.split(" | ")
        jid = cells[0][2:].strip()
        if jid in CELLS and CELLS[jid] is not None:
            assert ln.endswith(" |"), ln[:40]
            body = ln[:-2]
            k = body.rfind(" | ")
            lines[i] = body[:k] + " | " + CELLS[jid] + " |"
            changed += 1
text = "\n".join(lines)
assert text.count(COUNT_OLD) == 1
text = text.replace(COUNT_OLD, COUNT_NEW)
# dated note at the top: after the first heading line and its blank line
head_end = text.index("\n\n") + 2
text = text[:head_end] + TOP + text[head_end:]
for n in range(2, 7):
    m = re.search(r"^## Part %d\..*\n\n" % n, text, re.M)
    text = text[:m.end()] + PART_LINE + text[m.end():]
open(F, "w", encoding="utf-8").write(text)
print("cells changed:", changed, "of", sum(1 for v in CELLS.values() if v))
