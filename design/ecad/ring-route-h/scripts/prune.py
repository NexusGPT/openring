# prune.py in out NET[,NET...] : remove, repeatedly, every track of the listed nets with an end that touches nothing else of its net on its layer
# (no other track end or track body, no via, no pad), and every via of those nets that touches fewer than two items; refill; save.
import sys, math, pcbnew
from pcbnew import ToMM
O = 100.0
b = pcbnew.LoadBoard(sys.argv[1]); NETS = set(sys.argv[3].split(","))
def P(v): return (ToMM(v.x) - O, ToMM(v.y) - O)
def dseg(p, s, e):
    dx, dy = e[0]-s[0], e[1]-s[1]; L = dx*dx+dy*dy; t = 0 if L == 0 else max(0, min(1, ((p[0]-s[0])*dx+(p[1]-s[1])*dy)/L))
    return math.hypot(p[0]-s[0]-t*dx, p[1]-s[1]-t*dy)
removed = []
while True:
    tr = [t for t in b.GetTracks() if t.GetNetname() in NETS]
    pads = [(p, p.GetNetname()) for m in b.GetFootprints() for p in m.Pads() if p.GetNetname() in NETS]
    def touches(pt, lay, net, me):
        for o in tr:
            if o is me or o.GetNetname() != net: continue
            if o.Type() == pcbnew.PCB_VIA_T:
                if o.IsOnLayer(lay) and math.hypot(pt[0] - P(o.GetPosition())[0], pt[1] - P(o.GetPosition())[1]) <= ToMM(o.GetWidth(lay)) / 2 + 1e-3: return True
            elif o.GetLayer() == lay and dseg(pt, P(o.GetStart()), P(o.GetEnd())) <= ToMM(o.GetWidth()) / 2 + 1e-3: return True
        for p, n in pads:
            if n == net and p.IsOnLayer(lay) and p.HitTest(pcbnew.VECTOR2I(pcbnew.FromMM(pt[0] + O), pcbnew.FromMM(pt[1] + O))): return True
        return False
    gone = []
    for t in tr:
        if t.Type() == pcbnew.PCB_VIA_T:
            pt = P(t.GetPosition()); n = 0
            for o in tr:
                if o is t or o.GetNetname() != t.GetNetname() or o.Type() == pcbnew.PCB_VIA_T: continue
                if t.IsOnLayer(o.GetLayer()) and (math.hypot(P(o.GetStart())[0] - pt[0], P(o.GetStart())[1] - pt[1]) <= 0.101 or math.hypot(P(o.GetEnd())[0] - pt[0], P(o.GetEnd())[1] - pt[1]) <= 0.101): n += 1
            for p, nn in pads:
                if nn == t.GetNetname() and any(p.IsOnLayer(l) and t.IsOnLayer(l) for l in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu)) and p.HitTest(t.GetPosition()): n += 1
            if n < 2: gone.append(t)
        else:
            for pt in (P(t.GetStart()), P(t.GetEnd())):
                if not touches(pt, t.GetLayer(), t.GetNetname(), t): gone.append(t); break
    if not gone: break
    for t in gone:
        removed.append((t.GetNetname(), "via" if t.Type() == pcbnew.PCB_VIA_T else b.GetLayerName(t.GetLayer()), P(t.GetPosition()) if t.Type() == pcbnew.PCB_VIA_T else (P(t.GetStart()), P(t.GetEnd())), t.IsLocked()))
        b.Delete(t)
print("removed", len(removed))
for r in removed: print("  ", r)
b.BuildConnectivity(); pcbnew.ZONE_FILLER(b).Fill(b.Zones()); b.Save(sys.argv[2]); print("saved", flush=True)
