import sys, pcbnew
from pcbnew import ToMM
b = pcbnew.LoadBoard(sys.argv[1])
for d in b.GetDrawings():
    if d.GetClass() == "PCB_TEXT":
        p = d.GetPosition(); s = d.GetTextSize()
        print("TEXT", b.GetLayerName(d.GetLayer()), repr(d.GetText()), "%.3f %.3f" % (ToMM(p.x), ToMM(p.y)), "mirrored", d.IsMirrored(), "h %.2f w %.2f stroke %.2f" % (ToMM(s.y), ToMM(s.x), ToMM(d.GetTextThickness())))
