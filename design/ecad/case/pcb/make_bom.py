#!/usr/bin/env python3
"""Writes the parts list of each board with the orderable part numbers: fab/case_main_parts.csv and fab/case_pins_parts.csv (system python 3).
Source: design/ecad/case/parts.csv (mpn column written by make_netlist.py), the wire lengths of design/case/case-bom.csv lines 27, 28, 59."""
import csv, os
HERE = os.path.dirname(os.path.abspath(__file__))
CASE = os.path.dirname(HERE)
FAB = os.path.join(HERE, "fab")
os.makedirs(FAB, exist_ok=True)
parts = list(csv.DictReader(open(os.path.join(CASE, "parts.csv"))))
PCB2 = {"P1", "P2", "P3", "P4", "E1", "WP1", "WP2", "WP3", "WP4", "WP7"}
MAKER = [("RC0402", "Yageo"), ("GRM", "Murata"), ("XFL", "Coilcraft"), ("103AT", "Semitec"), ("DNK", "DNK Power"), ("P70-", "Harwin"), ("ESP32", "Espressif"),
         ("BQ", "Texas Instruments"), ("TPS", "Texas Instruments"), ("TPD", "Texas Instruments"), ("USB4105", "GCT"), ("APTF", "Kingbright"), ("ZDSD", "Zetta")]
WIRE_MM = {"W1": 30, "W2": 30, "W3": 30, "W4": 30, "W7": 20, "W5": 40, "W6": 40}   # case-bom.csv lines 27, 59, 28


def maker(mpn):
    for k, v in MAKER:
        if mpn.startswith(k):
            return v
    return ""


def line(ref, p):
    mpn = p["mpn"]
    note = ""
    if ref.startswith("TP"):
        note = "test pad, copper on the bottom face of PCB1 (no part to order)"
    elif ref in WIRE_MM:
        note = "wire 30 AWG, conductor 0.25 mm, thin insulation (outer dia 0.5 mm or less), cut length %d mm (CB lines 27, 28, 59); no maker part number verified" % WIRE_MM[ref]
        if ref in ("W5", "W6"):
            note = "lead of the cell BT1 (red = +, black = -), supplied 100 mm, cut to 40 mm; part of the cell"
    elif ref.startswith("WP"):
        note = "pin-board end of the wire with the same number (WP1 = W1): solder pad, no part"
    elif ref == "E1":
        note = "copper on PCB2 (no part to order)"
    elif ref == "TH1":
        note = "10 k NTC bead thermistor with two leads, glued on the cell face (TI BQ25895 Table 6-1 p.5)"
    elif ref == "BT1":
        note = "order with flying leads FL, 100 mm, lead 1 red = +, lead 2 black = -; NTC 103AT-2 option not used (TH1 is separate)"
    elif ref == "R11":
        note = "design value 260 ohm is not E96: ordered 261 ohm (ILIM cap 355 / 261 = 1.36 A)"
    elif ref in ("C4", "C5", "C6", "C11", "C15"):
        note = "10 V X5R chosen: DC bias loses less capacitance than on a 6.3 V part"
    return dict(ref=ref, value=p["value"], footprint=p["footprint"].split(":")[1], mpn=mpn, maker=maker(mpn), note=note)


def write(name, refs, extra=()):
    rows = [line(r, p) for r in refs for p in [next(x for x in parts if x["reference"] == r)]]
    rows += list(extra)
    groups = {}
    for r in rows:
        k = (r["value"], r["footprint"], r["mpn"], r["maker"], r["note"] if r["ref"].startswith("W") or r["ref"] in ("R11",) else "")
        groups.setdefault(k, []).append(r["ref"])
    out = os.path.join(FAB, name)
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["designators", "quantity", "value", "footprint", "manufacturer", "orderable_part_number", "note"])
        n = 0
        for (val, fpn, mpn, mk, note), rl in sorted(groups.items(), key=lambda kv: kv[1][0]):
            nt = note or next(r["note"] for r in rows if r["ref"] == rl[0])
            w.writerow([" ".join(sorted(rl, key=lambda x: (len(x), x))), len(rl), val, fpn, mk, mpn, nt])
            n += len(rl)
    print("wrote", out, "lines", len(groups), "parts", n)


main_refs = [p["reference"] for p in parts if p["reference"] not in PCB2]
write("case_main_parts.csv", main_refs)
write("case_pins_parts.csv", sorted(PCB2))
