"""Adds three silkscreen marks (W5 +, W6 -, TH1) to the bottom face of case_main.kicad_pcb, same style as W1 to W4, W7 (height 1.0, stroke 0.15, width 0.60, mirrored, centred).
Positions from search_B.log of this folder. Idempotent. Nothing but PCB_TEXT on B.SilkS is added."""
import sys, pcbnew
from pcbnew import FromMM, VECTOR2I
MARKS = [("W5 +", 115.55, 81.25), ("W6 -", 108.8, 82.8), ("TH1", 120.25, 83.15)]
path = sys.argv[1]
b = pcbnew.LoadBoard(path)
have = [(d.GetText()) for d in b.GetDrawings() if d.GetClass() == "PCB_TEXT" and d.GetLayer() == pcbnew.B_SilkS]
for (txt, x, y) in MARKS:
    if txt in have:
        print("exists", txt); continue
    t = pcbnew.PCB_TEXT(b)
    t.SetText(txt); t.SetLayer(pcbnew.B_SilkS)
    t.SetTextSize(VECTOR2I(FromMM(0.60), FromMM(1.0))); t.SetTextThickness(FromMM(0.15))
    t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
    t.SetMirrored(True); t.SetPosition(VECTOR2I(FromMM(x), FromMM(y)))
    b.Add(t); print("added", txt)
b.Save(path)
