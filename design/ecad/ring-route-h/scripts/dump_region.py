# dump_region.py board x0 x1 y0 y1 : every track, via and pad (all copper layers) touching the box, model mm (KiCad - 100)
import sys, pcbnew
from pcbnew import ToMM
O = 100.0
b = pcbnew.LoadBoard(sys.argv[1]); x0, x1, y0, y1 = map(float, sys.argv[2:6])
def P(v): return (ToMM(v.x) - O, ToMM(v.y) - O)
def inbox(bb): return not (ToMM(bb.GetRight())-O < x0 or ToMM(bb.GetLeft())-O > x1 or ToMM(bb.GetBottom())-O < y0 or ToMM(bb.GetTop())-O > y1)
for t in b.GetTracks():
    if not inbox(t.GetBoundingBox()): continue
    if t.Type() == pcbnew.PCB_VIA_T:
        print("VIA %-10s %s-%s (%.3f,%.3f) d%.3f %s" % (t.GetNetname(), b.GetLayerName(t.TopLayer()), b.GetLayerName(t.BottomLayer()), *P(t.GetPosition()), ToMM(t.GetWidth(pcbnew.F_Cu)), "locked" if t.IsLocked() else ""))
    else:
        print("SEG %-10s %-6s (%.3f,%.3f)-(%.3f,%.3f) w%.3f %s" % (t.GetNetname(), b.GetLayerName(t.GetLayer()), *P(t.GetStart()), *P(t.GetEnd()), ToMM(t.GetWidth()), "locked" if t.IsLocked() else ""))
for m in b.GetFootprints():
    for p in m.Pads():
        if inbox(p.GetBoundingBox()):
            print("PAD %s.%s %-10s %s (%.3f,%.3f)" % (m.GetReference(), p.GetNumber(), p.GetNetname(), ",".join(b.GetLayerName(l) for l in p.GetLayerSet().CuStack()), *P(p.GetPosition())))
    cy = m.GetCourtyard(pcbnew.F_Cu if m.GetLayer() == pcbnew.F_Cu else pcbnew.B_Cu)
    if cy.OutlineCount():
        bb = cy.BBox()
        if not (ToMM(bb.GetRight())-O < x0 or ToMM(bb.GetLeft())-O > x1 or ToMM(bb.GetBottom())-O < y0 or ToMM(bb.GetTop())-O > y1):
            print("CRTYD %s %s x %.3f..%.3f y %.3f..%.3f" % (m.GetReference(), b.GetLayerName(m.GetLayer()), ToMM(bb.GetLeft())-O, ToMM(bb.GetRight())-O, ToMM(bb.GetTop())-O, ToMM(bb.GetBottom())-O))
print("dump done")
