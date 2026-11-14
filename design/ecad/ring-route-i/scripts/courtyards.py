# courtyards.py board REF... : print each courtyard outline vertex (model mm) and J1-vs-REF intersection area
import sys, pcbnew
from pcbnew import ToMM
O = 100.0
b = pcbnew.LoadBoard(sys.argv[1]); j = b.FindFootprintByReference("J1"); cj = j.GetCourtyard(j.GetLayer())
for r in ["J1"] + sys.argv[2:]:
    m = b.FindFootprintByReference(r); c = m.GetCourtyard(m.GetLayer())
    for o in range(c.OutlineCount()):
        ol = c.COutline(o)
        print(r, b.GetLayerName(m.GetLayer()), "outline", o, " ".join("(%.4f,%.4f)" % (ToMM(ol.CPoint(i).x) - O, ToMM(ol.CPoint(i).y) - O) for i in range(ol.PointCount())))
    if r != "J1":
        x = pcbnew.SHAPE_POLY_SET(cj); x.BooleanIntersection(c); print(r, "intersection area with J1 mm2 %.6f" % (x.Area() / 1e12))
