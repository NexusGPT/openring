F = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/wiring/connections.md")
CSV = "design/wiring/product-wiring.csv"
LD = "design/wiring/lead-decisions.md"
CELLS = {
 "C1": "Drawn (13 Nov): case BT1 red lead + to PCB1 pad W5, cut 13.0 mm (case board-notes.md Round 2 wiring table); the cell's own lead as delivered, polarity measured before cutting (%s row 'case cell BT1 leads'). %s: 1 line `specified and landed`." % (LD, CSV),
 "C2": "Drawn (13 Nov): case BT1 black lead - to PCB1 pad W6, cut 15.2 mm; own lead as delivered (%s row 'case cell BT1 leads'). %s: 1 line `specified and landed`." % (LD, CSV),
 "C3": "Drawn (13 Nov): TH1 pins 1 (TS) and 2 (GND) to PCB1 plated holes TH1.1 and TH1.2 (footprint NTC_wired), either way round; bare 0.5 mm tin plated 42 alloy leads cut to 10 mm, joint 5 mm or more from the bead (%s row 'case thermistor TH1 leads'; design/case/lead-specs.md). %s: 2 lines `specified and landed`." % (LD, CSV),
 "C5": "Drawn (13 Nov): WP1 to WP4 and WP7 on case_pins.kicad_pcb, W1 to W4 and W7 on case_main.kicad_pcb; 30 AWG stranded, red, white, green, black, yellow, cut 15.6 to 16.3 mm (%s row 'case wires W1 to W4 and W7: colour'). %s: 5 lines `specified and landed`." % (LD, CSV),
}
OLD = "and the ring board's round 3.\n\n"
ADD = ("Update 2026-11-13 08:29 CET (product-wiring helper, third pass): the cells of C1, C2, C3 and C5 cite the lead's rows "
       "of design/wiring/lead-decisions.md on the case leads and wires; those 9 lines are now `specified and landed`.\n\n")
text = open(F, encoding="utf-8").read()
assert "third pass" not in text and text.count(OLD) == 1
lines = text.split("\n"); part1 = False; changed = 0
for i, ln in enumerate(lines):
    if ln.startswith("## Part 1."): part1 = True
    elif ln.startswith("## Part 2."): part1 = False
    if part1 and ln.startswith("| "):
        jid = ln.split(" | ")[0][2:].strip()
        if jid in CELLS:
            body = ln[:-2]; k = body.rfind(" | "); lines[i] = body[:k] + " | " + CELLS[jid] + " |"; changed += 1
text = "\n".join(lines).replace(OLD, OLD + ADD)
open(F, "w", encoding="utf-8").write(text); print("cells changed:", changed)
