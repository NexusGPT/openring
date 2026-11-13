# movej1.py in out x y rot : put J1 on F.Cu (the under face) at model (x, y) turned rot; pad nets kept; no refill; prints pads and courtyard
import sys, pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I
O = 100.0
b = pcbnew.LoadBoard(sys.argv[1]); x, y, rot = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
m = b.FindFootprintByReference("J1")
before = {(p.GetNumber(), round(ToMM(p.GetPosition().x), 4), round(ToMM(p.GetPosition().y), 4)): p.GetNetname() for p in m.Pads()}
nets0 = sorted((p.GetNumber(), p.GetNetname()) for p in m.Pads())
print("J1 before layer", b.GetLayerName(m.GetLayer()), "pos (%.3f,%.3f) rot %.1f" % (ToMM(m.GetPosition().x) - O, ToMM(m.GetPosition().y) - O, m.GetOrientationDegrees()))
if m.GetLayer() != pcbnew.F_Cu:
    m.Flip(m.GetPosition(), pcbnew.FLIP_DIRECTION_LEFT_RIGHT)
m.SetOrientationDegrees(rot); m.SetPosition(VECTOR2I(FromMM(x + O), FromMM(y + O)))
print("J1 after layer", b.GetLayerName(m.GetLayer()), "pos (%.3f,%.3f) rot %.1f" % (ToMM(m.GetPosition().x) - O, ToMM(m.GetPosition().y) - O, m.GetOrientationDegrees()))
for p in m.Pads():
    bb = p.GetBoundingBox()
    print("pad %-3s net %-9s layer %s centre (%.3f,%.3f) x %.3f..%.3f y %.3f..%.3f" % (p.GetNumber(), p.GetNetname(), ",".join(b.GetLayerName(l) for l in p.GetLayerSet().CuStack()), ToMM(p.GetPosition().x) - O, ToMM(p.GetPosition().y) - O, ToMM(bb.GetLeft()) - O, ToMM(bb.GetRight()) - O, ToMM(bb.GetTop()) - O, ToMM(bb.GetBottom()) - O))
cy = m.GetCourtyard(pcbnew.F_Cu); bb = cy.BBox()
print("courtyard F x %.3f..%.3f y %.3f..%.3f" % (ToMM(bb.GetLeft()) - O, ToMM(bb.GetRight()) - O, ToMM(bb.GetTop()) - O, ToMM(bb.GetBottom()) - O))
nets1 = sorted((p.GetNumber(), p.GetNetname()) for p in m.Pads())
print("pad nets unchanged:", nets0 == nets1)
b.Save(sys.argv[2]); print("saved", sys.argv[2])
