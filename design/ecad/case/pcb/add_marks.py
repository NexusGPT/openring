#!/usr/bin/env python3
"""Adds the wire and pin marks to the silkscreen of the two case boards (review 2026-11-13, minor m2). Silkscreen text only: no copper, pad, net or outline is touched.
usage: run_kipy.sh add_marks.py   (KiCad's Python; idempotent: it first removes the texts it wrote earlier, found by layer + text + position)
Sizes: height 1.0 mm, stroke 0.15 mm: the board maker's smallest legible text (evidence/capab_jlc.html.txt 'Minimum text height | 40 mil (1.0mm)',
'Minimum Line Width >=0.15mm'). Widths 0.55 mm (pin board front) and 0.60 mm (all other marks). Positions found by evidence/marks/search_marks.py (nearest spot with 0.15 mm
to every pad opening and 0.2 mm to the edge of its piece); back texts are mirrored so that they read right when the board is turned over."""
import os, pcbnew
from pcbnew import FromMM, VECTOR2I

HERE = os.path.dirname(os.path.abspath(__file__))
H = 1.0
TH = 0.15
# (layer, text, x, y, width, mirrored)
PINS = [
    ("F", "P1 +", 96.379, 98.45, 0.55),     # wing of P1 (VRING), front face = the face with the pins and the five wire pads
    ("F", "P4 -", 103.621, 98.45, 0.55),    # wing of P4 (GND)
    ("B", "P1", 96.479, 98.45, 0.60), ("B", "+", 96.479, 101.40, 0.60),
    ("B", "P2", 98.803, 98.45, 0.60), ("B", "D-", 98.803, 101.65, 0.60),
    ("B", "P3", 101.197, 98.45, 0.60), ("B", "D+", 101.197, 101.65, 0.60),
    ("B", "P4", 103.521, 98.45, 0.60), ("B", "GND", 103.521, 101.65, 0.60),
]
MAIN = [   # bottom face, one row per wire hole, to the right of the hole (column W1 W2 W7 W3 W4 at x 117.95, pitch 1.6 mm)
    ("B", "W1 +", 119.95, 96.80, 0.60), ("B", "W2 D-", 120.25, 98.40, 0.60), ("B", "W7 TCH", 120.40, 100.00, 0.60),
    ("B", "W3 D+", 120.25, 101.60, 0.60), ("B", "W4 GND", 120.50, 103.20, 0.60),
]


def apply(path, marks):
    b = pcbnew.LoadBoard(path)
    for d in list(b.GetDrawings()):
        if d.GetClass() == "PCB_TEXT" and d.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS):
            b.Remove(d)
    for (face, txt, x, y, w) in marks:
        t = pcbnew.PCB_TEXT(b)
        t.SetText(txt)
        t.SetLayer(pcbnew.F_SilkS if face == "F" else pcbnew.B_SilkS)
        t.SetTextSize(VECTOR2I(FromMM(w), FromMM(H)))
        t.SetTextThickness(FromMM(TH))
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER)
        t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
        t.SetMirrored(face == "B")
        t.SetPosition(VECTOR2I(FromMM(x), FromMM(y)))
        b.Add(t)
    b.Save(path)
    print("wrote", len(marks), "silkscreen texts to", path)


apply(os.path.join(HERE, "case_pins.kicad_pcb"), PINS)
apply(os.path.join(HERE, "case_main.kicad_pcb"), MAIN)
