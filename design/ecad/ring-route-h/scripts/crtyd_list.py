# crtyd_list.py board x0 x1 y0 y1 : every courtyard (polygon extents) on each face touching the box
import sys, pcbnew
from pcbnew import ToMM
O = 100.0
b = pcbnew.LoadBoard(sys.argv[1]); x0, x1, y0, y1 = map(float, sys.argv[2:6])
for m in sorted(b.GetFootprints(), key=lambda m: m.GetReference()):
    c = m.GetCourtyard(m.GetLayer())
    if not c.OutlineCount(): continue
    pts = [c.COutline(o).CPoint(i) for o in range(c.OutlineCount()) for i in range(c.COutline(o).PointCount())]
    l, r, t, bo = min(ToMM(p.x) for p in pts) - O, max(ToMM(p.x) for p in pts) - O, min(ToMM(p.y) for p in pts) - O, max(ToMM(p.y) for p in pts) - O
    if r < x0 or l > x1 or bo < y0 or t > y1: continue
    print("%-3s %-8s x %7.3f..%7.3f y %7.3f..%7.3f" % (b.GetLayerName(m.GetLayer())[0], m.GetReference(), l, r, t, bo))
