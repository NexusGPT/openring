# lists vias and tracks touching U1 lands D6 E9 F4 F8 F9 and the TP8 TP9 TP11 footprints of a board
import sys, math, pcbnew
from pcbnew import ToMM
b = pcbnew.LoadBoard(sys.argv[1]); O = 100.0
LN = {"F.Cu": "L1", "In1.Cu": "L2", "In2.Cu": "L3", "B.Cu": "L4"}
fps = {f.GetReference(): f for f in b.GetFootprints()}
for ball in ["D6", "E9", "F4", "F8", "F9"]:
    pad = [p for p in fps["U1"].Pads() if p.GetNumber() == ball][0]
    c = (ToMM(pad.GetPosition().x) - O, ToMM(pad.GetPosition().y) - O)
    print("ball", ball, "net %r" % pad.GetNetname(), "centre %.3f,%.3f" % c)
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            p = (ToMM(t.GetPosition().x) - O, ToMM(t.GetPosition().y) - O)
            if math.dist(p, c) < 0.002:
                print("  via", LN[b.GetLayerName(t.TopLayer())], LN[b.GetLayerName(t.BottomLayer())], t.GetNetname(), "locked", t.IsLocked(), "type", t.GetViaType())
        else:
            s = (ToMM(t.GetStart().x) - O, ToMM(t.GetStart().y) - O); e = (ToMM(t.GetEnd().x) - O, ToMM(t.GetEnd().y) - O)
            if math.dist(s, c) < 0.002 or math.dist(e, c) < 0.002:
                o = e if math.dist(s, c) < 0.002 else s
                print("  track", LN[b.GetLayerName(t.GetLayer())], t.GetNetname(), "to %.3f,%.3f" % o, "w %.3f" % ToMM(t.GetWidth()), "locked", t.IsLocked())
for r in ["TP8", "TP9", "TP11"]:
    f = fps.get(r)
    if not f: print(r, "absent"); continue
    print(r, "at %.3f,%.3f" % (ToMM(f.GetPosition().x) - O, ToMM(f.GetPosition().y) - O), "flipped", f.IsFlipped(), "pads", [(p.GetNumber(), p.GetNetname(), b.GetLayerName(p.GetLayer())) for p in f.Pads()])
    for p in f.Pads():
        hits = [t for t in b.GetTracks() if t.HitTest(p.GetPosition()) or (t.Type() != pcbnew.PCB_VIA_T and (p.HitTest(t.GetStart()) or p.HitTest(t.GetEnd())))]
        print("  items touching pad", p.GetNumber(), len(hits), [(t.GetNetname(), b.GetLayerName(t.GetLayer())) for t in hits])
print("footprints", len(fps))
