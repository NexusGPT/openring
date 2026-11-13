import pcbnew
from pcbnew import ToMM, FromMM, VECTOR2I
b = pcbnew.BOARD()
for txt in ("P1 +", "P4 -", "P4 GND", "P1+", "GND", "P4", "P2 D-", "P3 D+", "W1", "W4 GND"):
    for (w, h, th) in ((1.0, 1.0, 0.15), (0.7, 1.0, 0.15), (0.6, 1.0, 0.15)):
        t = pcbnew.PCB_TEXT(b)
        t.SetText(txt); t.SetLayer(pcbnew.F_SilkS)
        t.SetTextSize(VECTOR2I(FromMM(w), FromMM(h))); t.SetTextThickness(FromMM(th))
        t.SetPosition(VECTOR2I(0, 0)); t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_CENTER); t.SetVertJustify(pcbnew.GR_TEXT_V_ALIGN_CENTER)
        sh = t.GetEffectiveTextShape()
        bb = sh.BBox()
        print("%-8s size %.2fx%.2f -> ink w %.3f h %.3f  x %.3f..%.3f y %.3f..%.3f" % (txt, w, h, ToMM(bb.GetWidth()), ToMM(bb.GetHeight()), ToMM(bb.GetLeft()), ToMM(bb.GetRight()), ToMM(bb.GetTop()), ToMM(bb.GetBottom())))
