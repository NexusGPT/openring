# parts.py board REF... : place, side, rotation, pads (net, layers, centre, size) and courtyard of each part
import sys, pcbnew
from pcbnew import ToMM
O = 100.0
b = pcbnew.LoadBoard(sys.argv[1])
for r in sys.argv[2:]:
    m = b.FindFootprintByReference(r); c = m.GetCourtyard(m.GetLayer())
    pts = [c.COutline(0).CPoint(i) for i in range(c.COutline(0).PointCount())] if c.OutlineCount() else []
    print("%s %s at (%.3f,%.3f) rot %.1f courtyard x %.3f..%.3f y %.3f..%.3f" % (r, b.GetLayerName(m.GetLayer()), ToMM(m.GetPosition().x) - O, ToMM(m.GetPosition().y) - O, m.GetOrientationDegrees(),
          min(ToMM(p.x) for p in pts) - O, max(ToMM(p.x) for p in pts) - O, min(ToMM(p.y) for p in pts) - O, max(ToMM(p.y) for p in pts) - O))
    for p in m.Pads():
        bb = p.GetBoundingBox()
        print("   pad %s %-8s (%.3f,%.3f) x %.3f..%.3f y %.3f..%.3f" % (p.GetNumber(), p.GetNetname(), ToMM(p.GetPosition().x) - O, ToMM(p.GetPosition().y) - O, ToMM(bb.GetLeft()) - O, ToMM(bb.GetRight()) - O, ToMM(bb.GetTop()) - O, ToMM(bb.GetBottom()) - O))
