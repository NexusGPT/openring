# linestretch.py board : (1) USB pair: each leg's tracks sampled every 0.01 mm; edge gap to the other leg's tracks (centre distance
# minus both half widths); length coupled at 0.075 (+-0.005), and the uncoupled length per fan-out region (U1: Y < 2.5; U9: X 1.5..4.8,
# Y > 4.5 ... excluding the west run; J_BAND_B: X < -1.0); total track length per leg.
# (2) XL1, XL2: each track sampled every 0.01 mm; distance to the nearest other-net copper on the same layer (tracks, via lands, pad
# outlines, and the filled zones); stretches under 0.20 with their neighbour nets, and their largest distance outside U1's body (F.Fab box).
import sys, math, os, pcbnew
FAR = float(os.environ.get("FAR", "0") or 0)
from pcbnew import ToMM, FromMM, VECTOR2I
b = pcbnew.LoadBoard(sys.argv[1]); O = 100.0; ST = 0.01
P = lambda v: (ToMM(v.x) - O, ToMM(v.y) - O)
def segd(p, a, c):
    dx, dy = c[0]-a[0], c[1]-a[1]; L2 = dx*dx+dy*dy; t = 0 if L2 == 0 else max(0, min(1, ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/L2)); return math.hypot(p[0]-a[0]-t*dx, p[1]-a[1]-t*dy)
def tracks(n): return [(t.GetLayer(), P(t.GetStart()), P(t.GetEnd()), ToMM(t.GetWidth())/2) for t in b.GetTracks() if t.GetNetname() == n and t.GetClass() == "PCB_TRACK"]
def samples(ts):
    for (ly, a, c, r) in ts:
        L = math.hypot(c[0]-a[0], c[1]-a[1]); n = max(1, int(round(L / ST)))
        for k in range(n):
            yield ly, (a[0] + (c[0]-a[0])*(k+0.5)/n, a[1] + (c[1]-a[1])*(k+0.5)/n), L / n, r
dp, dn = tracks("USB_DP"), tracks("USB_DN")
def region(p):
    if p[1] < 2.5: return "U1 fan-out"
    if p[0] < -1.0: return "J_BAND_B fan-out"
    if p[1] > 4.5 and p[0] > 1.5: return "U9 fan-out"
    return "other"
for nm, own, oth in (("USB_DP", dp, dn), ("USB_DN", dn, dp)):
    tot = 0; cpl = 0; reg = {}
    for ly, p, dl, r in samples(own):
        tot += dl
        g = min(segd(p, a, c) - r - r2 for (l2, a, c, r2) in oth)
        if abs(g - 0.075) <= 0.005: cpl += dl
        else: reg[region(p)] = reg.get(region(p), 0) + dl
    print("USB %s total track %.3f mm; coupled at 0.075 %.3f mm; not at 0.075: %s" % (nm, tot, cpl, {k: round(v, 3) for k, v in sorted(reg.items())}))
u1 = b.FindFootprintByReference("U1")
fab = [d for d in u1.GraphicalItems() if d.GetLayer() == pcbnew.F_Fab]
bb = fab[0].GetBoundingBox()
for d in fab[1:]: bb.Merge(d.GetBoundingBox())
ub = (ToMM(bb.GetLeft())-O, ToMM(bb.GetTop())-O, ToMM(bb.GetRight())-O, ToMM(bb.GetBottom())-O)
print("U1 body (F.Fab box) x %.3f..%.3f y %.3f..%.3f" % ub)
def outside(p): return math.hypot(max(ub[0]-p[0], 0, p[0]-ub[2]), max(ub[1]-p[1], 0, p[1]-ub[3]))
for n in ("XL1", "XL2"):
    oth = {}
    for t in b.GetTracks():
        if t.GetNetname() == n or t.GetNetname() == "": continue
        for ly in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
            if not t.IsOnLayer(ly): continue
            if t.GetClass() == "PCB_VIA": q = P(t.GetPosition()); oth.setdefault(ly, []).append((t.GetNetname(), q, q, ToMM(t.GetWidth(ly))/2))
            else: oth.setdefault(ly, []).append((t.GetNetname(), P(t.GetStart()), P(t.GetEnd()), ToMM(t.GetWidth())/2))
    pads = {}
    for m in b.GetFootprints():
        for pd in m.Pads():
            if pd.GetNetname() in (n, ""): continue
            for ly in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
                if pd.IsOnLayer(ly):
                    o = pd.GetEffectivePolygon(ly).Outline(0); pts = [P(o.CPoint(i)) for i in range(o.PointCount())]
                    pads.setdefault(ly, []).append((pd.GetNetname() + " pad " + m.GetReference() + "." + pd.GetNumber(), pts))
    zones = {}
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname() == n: continue
        for ly in z.GetLayerSet().Seq():
            if ly in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu): zones.setdefault(ly, []).append((z.GetNetname() + " zone", z.GetFilledPolysList(ly)))
    tot = 0; under = 0; runs = []; cur = None; pernet = {}
    for ly, p, dl, r in samples(tracks(n)):
        tot += dl; best = (9, "")
        if FAR and outside(p) <= FAR: cur = None; continue   # ring-lines FAR: only points farther than FAR outside U1 body
        for (nn, a, c, r2) in oth.get(ly, []):
            d = segd(p, a, c) - r - r2
            if d < best[0]: best = (d, nn)
            if d < 0.2: pernet[nn] = min(pernet.get(nn, 9), d)   # ring-lines: every neighbour under 0.20, not only the nearest
        for (nn, pts) in pads.get(ly, []):
            d = min(segd(p, pts[i], pts[(i+1) % len(pts)]) for i in range(len(pts))) - r
            if d < best[0]: best = (d, nn)
        for (nn, fp) in zones.get(ly, []):
            if best[0] > 0.2 and fp.Collide(VECTOR2I(FromMM(p[0]+O), FromMM(p[1]+O)), FromMM(r + 0.2)): best = (0.199, nn + " (fill within 0.20)")
        if best[0] < 0.2 - 1e-6:
            under += dl
            if cur and cur["ly"] == ly and math.hypot(p[0]-cur["last"][0], p[1]-cur["last"][1]) < 0.03:
                cur["len"] += dl; cur["last"] = p; cur["nets"].add(best[1]); cur["min"] = min(cur["min"], best[0]); cur["out"] = max(cur["out"], outside(p))
            else:
                cur = dict(ly=ly, first=p, last=p, len=dl, nets={best[1]}, min=best[0], out=outside(p)); runs.append(cur)
        else: cur = None
    print("%s total track %.3f mm, under 0.20: %.3f mm in %d stretches" % (n, tot, under, len(runs)))
    print("%s per neighbour net (tracks and vias) minimum gap under 0.20: %s" % (n, {k: round(v, 4) for k, v in sorted(pernet.items())}))
    for s in runs:
        print("  %s %s (%.3f,%.3f)-(%.3f,%.3f) length %.3f min %.4f neighbours %s; farthest outside U1 body %.3f mm%s" % (n, b.GetLayerName(s["ly"]), s["first"][0], s["first"][1], s["last"][0], s["last"][1], s["len"], s["min"], sorted(s["nets"]), s["out"], "  OVER 1.0" if s["out"] > 1.0 else ""))
