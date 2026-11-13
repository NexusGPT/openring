"""Second pass on connections.md Part 1 (lead's ruling of 2026-11-13: state `specified and landed`; ring board round 3)."""
F = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/connections.md")
CSV = "design/wiring/product-wiring.csv"
CELLS = {
 "R5": "Drawn and routed (13 Nov): FLEX1 lands W0525AB001D_Lands 1 (VMOT) and 2 (GND) to J_BAND_A lands 7 and 6 in the 7 FLEX1 boards. The motor leads are specified and landed: red lead to land 1, blue to land 2, AWG32, cut length per size (band-interface.md section 6). %s: 2 copper lines `drawn and routed`, 2 lead lines `specified and landed`." % CSV,
 "R11": "Drawn (13 Nov) in RN and RPCB; the antenna is on its maker's land pattern on the board's under face, no notch (lead-decisions.md row W2). Whether the feed is routed follows the ring board, which is being routed again (round 3): %s gives the state at each build (rules check by build_wiring.py, design/wiring/wiring-work/drc/)." % CSV,
 "R12": "Drawn (13 Nov): ANT1 pads 2 and 3 on ANT_TRIM (to LT1, 0 ohm) and pad 4 on GND in RN and RPCB. Routed or not: as R11, the state of each build is in %s." % CSV,
 "R13": "Drawn (13 Nov) in RN and RPCB: J1 pads 1 to 15 carry the RN nets; contact k on position k (RS line 38); DISP1 pins 3 and 4 closed by the Tailor table page 5 (RS line 309); pin 3 (MTP) carries no signal and has no line. At the build of 08:11 J1 stood on the screen face (B.Cu) and its pads were open in the main board's rules check (round 3 routing). %s: 14 lines, `drawn, not routed` until J1 is routed." % CSV,
 "C1": "Drawn (13 Nov): case BT1 red lead + to PCB1 pad W5 (design/ecad/case/pcb/case_main.kicad_pcb), cut 13.0 mm (case board-notes.md Round 2 wiring table). The lead's gauge is in no file. %s: 1 line `drawn, not routed`." % CSV,
 "C2": "Drawn (13 Nov): case BT1 black lead - to PCB1 pad W6, cut 15.2 mm (same table). The lead's gauge is in no file. %s: 1 line `drawn, not routed`." % CSV,
 "C3": "Drawn (13 Nov): TH1 pins 1 (TS) and 2 (GND) to PCB1 plated holes TH1.1 and TH1.2 (footprint NTC_wired), 10 mm leads; TH1 is glued on the cell face (case board-notes.md conflict 3). Lead marking and gauge are in no file. %s: 2 lines `drawn, not routed`." % CSV,
 "C5": "Drawn (13 Nov): WP1 to WP4 and WP7 on case_pins.kicad_pcb, W1 to W4 and W7 on case_main.kicad_pcb, 30 AWG, cut 15.6 to 16.3 mm (case board-notes.md Round 2 wiring table); no open connection in either board's rules check. Wire colour or marking is in no file. %s: 5 lines `drawn, not routed`." % CSV,
}
OLD_TOP_END = "they describe the files of 12 November.\n\n"
ADD = ("Update 2026-11-13 08:13 CET (product-wiring helper, second pass): the lead's ruling adds the state `specified and landed` "
       "for leads, wires, tabs, spring pins and a part's own cable (ends landed, carrier fully specified); the cells of R5, R11, R12, "
       "R13, C1, C2, C3 and C5 follow it and the ring board's round 3.\n\n")
text = open(F, encoding="utf-8").read()
assert "second pass" not in text
lines = text.split("\n")
changed = 0
part1 = False
for i, ln in enumerate(lines):
    if ln.startswith("## Part 1."):
        part1 = True
    elif ln.startswith("## Part 2."):
        part1 = False
    if part1 and ln.startswith("| "):
        jid = ln.split(" | ")[0][2:].strip()
        if jid in CELLS:
            body = ln[:-2]
            k = body.rfind(" | ")
            lines[i] = body[:k] + " | " + CELLS[jid] + " |"
            changed += 1
text = "\n".join(lines)
assert text.count(OLD_TOP_END) == 1
text = text.replace(OLD_TOP_END, OLD_TOP_END + ADD)
open(F, "w", encoding="utf-8").write(text)
print("cells changed:", changed, "of", len(CELLS))
