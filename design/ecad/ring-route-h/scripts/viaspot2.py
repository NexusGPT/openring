# viaspot2.py board x0 y0 x1 y1 SPAN NET : grid points (0.025) in the box where a 0.20/0.10 via of NET spanning SPAN (F-In1, F-In2, F-B, In1-B, ...)
# keeps 0.175 + 0.006 from every other-net copper edge (tracks, vias, pads) on each layer it spans, 0.30 from every via centre;
# for NET GND also: inside the GND fill on its top and bottom layer. Prints up to 20 points, nearest to the box centre first.
import sys, math, pcbnew
from pcbnew import ToMM, FromMM, VECTOR2I
O = 100.0; b = pcbnew.LoadBoard(sys.argv[1]); x0, y0, x1, y1 = map(float, sys.argv[2:6]); span = sys.argv[6].split("-"); net = sys.argv[7]
LN = {"F": pcbnew.F_Cu, "In1": pcbnew.In1_Cu, "In2": pcbnew.In2_Cu, "B": pcbnew.B_Cu}; order = ["F", "In1", "In2", "B"]
layers = [LN[n] for n in order[order.index(span[0]):order.index(span[1]) + 1]]
def P(v): return (ToMM(v.x) - O, ToMM(v.y) - O)
def ps(p, s, e):
    dx, dy = e[0]-s[0], e[1]-s[1]; L = dx*dx+dy*dy; t = 0 if L == 0 else max(0, min(1, ((p[0]-s[0])*dx+(p[1]-s[1])*dy)/L))
    return math.hypot(p[0]-s[0]-t*dx, p[1]-s[1]-t*dy)
obs = []; vc = []
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T:
        vc.append(P(t.GetPosition()))
        if t.GetNetname() != net and any(t.IsOnLayer(l) for l in layers): obs.append(("c", P(t.GetPosition()), 0.1))
    elif t.GetNetname() != net and t.GetLayer() in layers: obs.append(("s", P(t.GetStart()), P(t.GetEnd()), ToMM(t.GetWidth()) / 2))
for m in b.GetFootprints():
    for p in m.Pads():
        if p.GetNetname() != net and any(p.IsOnLayer(l) for l in layers):
            bb = p.GetBoundingBox(); obs.append(("r", (ToMM(bb.GetLeft()) - O, ToMM(bb.GetTop()) - O, ToMM(bb.GetRight()) - O, ToMM(bb.GetBottom()) - O)))
fills = {}
if net == "GND":
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != "GND": continue
        for l in (layers[0], layers[-1]):
            if z.IsOnLayer(l): fills[l] = z.GetFilledPolysList(l)
out = []
cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
x = x0
while x <= x1 + 1e-9:
    y = y0
    while y <= y1 + 1e-9:
        ok = all(math.hypot(x - v[0], y - v[1]) >= 0.30 for v in vc)
        for o in obs:
            if not ok: break
            if o[0] == "c": d = math.hypot(x - o[1][0], y - o[1][1]) - o[2]
            elif o[0] == "s": d = ps((x, y), o[1], o[2]) - o[3]
            else: r = o[1]; d = math.hypot(max(r[0] - x, 0, x - r[2]), max(r[1] - y, 0, y - r[3]))
            if d < 0.181: ok = False
        if ok and net == "GND":
            pt = VECTOR2I(FromMM(x + O), FromMM(y + O))
            ok = all(l in fills and fills[l].Contains(pt) for l in (layers[0], layers[-1]))
        if ok: out.append((round(math.hypot(x - cx, y - cy), 3), round(x, 3), round(y, 3)))
        y = round(y + 0.025, 4)
    x = round(x + 0.025, 4)
out.sort(); print("legal points", len(out)); [print("  (%.3f,%.3f) d %.3f" % (o[1], o[2], o[0])) for o in out[:20]]
