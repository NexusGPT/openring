# diffitems.py before after : tracks and vias removed / added (all nets), model mm
import sys, pcbnew
from pcbnew import ToMM
O = 100.0
def key(b, t):
    if t.Type() == pcbnew.PCB_VIA_T:
        return (t.GetNetname(), "via", "%s-%s" % (b.GetLayerName(t.TopLayer()), b.GetLayerName(t.BottomLayer())), "(%.3f,%.3f)" % (ToMM(t.GetPosition().x) - O, ToMM(t.GetPosition().y) - O), "d%.3f/%.3f" % (ToMM(t.GetWidth(pcbnew.F_Cu) if False else t.GetFrontWidth() if hasattr(t, "GetFrontWidth") else 0), ToMM(t.GetDrillValue())), "locked" if t.IsLocked() else "")
    return (t.GetNetname(), "seg", b.GetLayerName(t.GetLayer()), "(%.3f,%.3f)-(%.3f,%.3f)" % (ToMM(t.GetStart().x) - O, ToMM(t.GetStart().y) - O, ToMM(t.GetEnd().x) - O, ToMM(t.GetEnd().y) - O), "w%.3f" % ToMM(t.GetWidth()), "locked" if t.IsLocked() else "")
A = pcbnew.LoadBoard(sys.argv[1]); B = pcbnew.LoadBoard(sys.argv[2])
a = sorted(key(A, t) for t in A.GetTracks()); bb = sorted(key(B, t) for t in B.GetTracks())
import collections
ca, cb = collections.Counter(a), collections.Counter(bb)
rem = sorted((ca - cb).elements()); add = sorted((cb - ca).elements())
for r in rem: print("REMOVE", *r)
for r in add: print("ADD", *r)
print("removed", len(rem), "added", len(add), "nets", sorted(set(r[0] for r in rem + add)))
