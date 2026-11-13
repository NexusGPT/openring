# same_copper.py <a> <b>: compares every track, via and zone fill (layer, net, geometry) of two boards
import sys, pcbnew
def items(p):
    b = pcbnew.LoadBoard(p); s = []
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            s.append(("via", t.GetNetname(), t.GetPosition().x, t.GetPosition().y, t.TopLayer(), t.BottomLayer(), t.GetWidth(pcbnew.F_Cu), t.GetDrill(), t.IsLocked()))
        else:
            s.append(("trk", t.GetNetname(), t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y, t.GetLayer(), t.GetWidth(), t.IsLocked()))
    for z in b.Zones():
        for l in z.GetLayerSet().CuStack():
            f = z.GetFilledPolysList(l)
            s.append(("zone", z.GetNetname(), l, round(f.Area()), f.TotalVertices()))
    return sorted(map(str, s))
a, c = items(sys.argv[1]), items(sys.argv[2])
sa, sc = set(a), set(c)
print("items a %d, b %d; only in a %d; only in b %d" % (len(a), len(c), len(sa - sc), len(sc - sa)))
for x in sorted(sa - sc)[:20]: print("only a", x)
for x in sorted(sc - sa)[:20]: print("only b", x)
print("RESULT SAME COPPER" if a == c else "RESULT DIFFERENT")
