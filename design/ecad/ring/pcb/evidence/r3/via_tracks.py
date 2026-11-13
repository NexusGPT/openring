# tracks whose end lies within 0.12 mm of the U1 F4 and F9 land centres, with layer, net, other end and lock state
import sys, math, pcbnew
from pcbnew import ToMM
b = pcbnew.LoadBoard(sys.argv[1]); O = 100.0
u1 = b.FindFootprintByReference("U1")
for ball in ("F4", "F9", "D6", "E9", "F8"):
    pad = [p for p in u1.Pads() if p.GetNumber() == ball][0]
    c = (ToMM(pad.GetPosition().x) - O, ToMM(pad.GetPosition().y) - O)
    print(ball, "net %r" % pad.GetNetname())
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            p = (ToMM(t.GetPosition().x) - O, ToMM(t.GetPosition().y) - O)
            if math.dist(p, c) < 0.12: print("  via at %.3f,%.3f" % p, b.GetLayerName(t.TopLayer()), b.GetLayerName(t.BottomLayer()), t.GetNetname(), "dist %.4f" % math.dist(p, c))
            continue
        s = (ToMM(t.GetStart().x) - O, ToMM(t.GetStart().y) - O); e = (ToMM(t.GetEnd().x) - O, ToMM(t.GetEnd().y) - O)
        for a_, o in ((s, e), (e, s)):
            if math.dist(a_, c) < 0.12:
                print("  track end %.4f from centre" % math.dist(a_, c), b.GetLayerName(t.GetLayer()), t.GetNetname(), "to %.3f,%.3f" % o, "locked", t.IsLocked())
