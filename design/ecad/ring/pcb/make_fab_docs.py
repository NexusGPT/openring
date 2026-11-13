#!/usr/bin/env python3
"""make_fab_docs.py -- writes fab/ring-parts-list.csv (one line per placed part with its order code) and fab/stackup.txt plus
fab/stackup.svg (the stack of design/wiring/ring-board-plan.md c.2 with the order notes). Called by make_fab.sh."""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
RING = os.path.dirname(HERE)
DESIGN = os.path.dirname(os.path.dirname(RING))
F = os.path.join(HERE, "fab")
BAND_ONLY = {"RT1", "BT1", "SW1", "SW2", "SW3", "SW4", "SW5", "M1", "CP1", "CP2", "CP3", "CP4", "DISP1"}

parts = list(csv.DictReader(open(os.path.join(RING, "parts.csv"))))
bom = {}
for r in csv.DictReader(open(os.path.join(DESIGN, "bom.csv"))):
    for ref in [x.strip() for x in r["reference"].split(",")]:
        bom[ref] = r
pos = {}
for r in csv.DictReader(open(os.path.join(F, "ring-pos.csv"))):
    pos[r["Ref"]] = r
with open(os.path.join(F, "ring-parts-list.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["reference", "value", "maker", "order_code", "package", "footprint", "fitted", "x_mm", "y_mm", "rotation", "side", "open_action"])
    n = 0
    for p in parts:
        ref = p["reference"]
        if ref in BAND_ONLY:
            continue
        b = bom.get(ref, {})
        q = pos.get(ref, {})
        w.writerow([ref, p["value"], b.get("maker", ""), b.get("maker_part_number", "") or p["mpn"], b.get("package", ""), p["footprint"],
                    "no (DNP)" if p["dnp"] == "yes" else "yes", q.get("PosX", ""), q.get("PosY", ""), q.get("Rot", ""), q.get("Side", ""),
                    b.get("open_action", "")])
        n += 1
print("parts list lines:", n)

layers = [("F.Mask (solder mask, green)", "about 0.0165 (measured on the first lot)"),
          ("L1 F.Cu: parts, U1 ring 1, U2 outer ring, RF line, USB pair, ground copper", "0.018 finished copper"),
          ("dielectric 1: one sheet of 106 prepreg (laser microvias L1-L2)", "0.065"),
          ("L2 In1.Cu: U1 ring 2, U2 inner escape, signals, ground copper (solid under the RF line)", "0.018"),
          ("dielectric 2: core (laser microvias L2-L3)", "0.065"),
          ("L3 In2.Cu: U1 rings 3 and 4, crystal lines, long signals, power", "0.018"),
          ("dielectric 3: one sheet of 106 prepreg (laser microvias L3-L4)", "0.065"),
          ("L4 B.Cu: ground plane, screen face: J1, eight 0201 passives, %d test pads" % sum(1 for p in parts if p["reference"].startswith("TP")), "0.018"),
          ("B.Mask (solder mask, green)", "about 0.0165")]
notes = [
    "Board: 27.2 x 12.6 mm, corner radius 0.8, no notch, 4 copper layers, any-layer HDI.",
    "Finished thickness 0.30 mm +-0.025 (0.267 mm over copper: 4 x 0.018 + 3 x 0.065).",
    "Every via is a laser microvia: 0.10 mm hole, 0.20 mm land, one per dielectric; stacked vias (L1-L3, L2-L4, L1-L4) are",
    "  stacks of single microvias at the same place, copper filled and plated over (also the vias in pads). No through hole,",
    "  no mechanical drill. Each drill file of drill/ is one layer pair; a pair that spans more than one dielectric is a stack.",
    "Track and gap: 0.065 / 0.065 mm minimum, design uses 0.100 / 0.075 (RF 0.120 with 0.20 gap; USB pair 0.100 / 0.075).",
    "Finish: ENEPIG. Solder mask green both sides; U1 and U2 land openings equal the land (no expansion).",
    "Impedance coupons: one 0.120 mm microstrip on L1 over L2 (target 50 ohm) and one 0.100 / 0.075 mm pair (target 90 ohm",
    "  differential), built with the board; dielectric constant of the 106 prepreg measured on the coupon.",
    "Cross-section coupon: one 3-high via stack (L1-L4), after the maker's thermal stress test.",
    "Source: design/wiring/ring-board-plan.md section c.2 (Plan A) and h.2.",
]
with open(os.path.join(F, "stackup.txt"), "w") as f:
    f.write("Ring main board stack (top = populated face L1)\n\n")
    for l, t in layers:
        f.write("%-95s %s mm\n" % (l, t))
    f.write("\nOrder notes\n")
    for n_ in notes:
        f.write(n_ + "\n")
H = 40
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="%d" font-family="Helvetica" font-size="13">' % (len(layers) * H + 60 + len(notes) * 18)]
svg.append('<rect width="100%" height="100%" fill="white"/>')
y = 20
for l, t in layers:
    col = "#3a7d3a" if "Mask" in l else "#c87533" if "Cu" in l else "#e8d9a8"
    svg.append('<rect x="20" y="%d" width="300" height="%d" fill="%s" stroke="black"/>' % (y, H - 6, col))
    svg.append('<text x="335" y="%d">%s, %s mm</text>' % (y + 22, l.replace("&", "and"), t))
    y += H
y += 10
for n_ in notes:
    svg.append('<text x="20" y="%d">%s</text>' % (y, n_.replace("<", "less than ").replace("&", "and"))); y += 18
svg.append("</svg>")
open(os.path.join(F, "stackup.svg"), "w").write("\n".join(svg))
print("stackup.txt and stackup.svg written")
