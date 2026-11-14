"""independent cross-check (from the BOARD FILE through pcbnew, not from the Gerber): min copper-to-copper distance, same layer, between the
nets named and every other-net track, via land and pad outline. Run with run_kipy.sh. Zone fills are not included."""
import sys, math, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])  # ring-lines copy
mm = pcbnew.ToMM
def segdist(p, a, c):
    dx, dy = c[0] - a[0], c[1] - a[1]; L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)
def seg_seg(a, c, e, f):
    # minimum distance between two segments (no crossing handled: crossing -> 0)
    def ccw(p, q, r): return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    if ccw(a, c, e) * ccw(a, c, f) < 0 and ccw(e, f, a) * ccw(e, f, c) < 0: return 0.0
    return min(segdist(a, e, f), segdist(c, e, f), segdist(e, a, c), segdist(f, a, c))
items = []   # (layer, kind, net, geometry)
for t in b.GetTracks():
    if t.GetClass() == 'PCB_VIA':
        p = (mm(t.GetPosition().x), mm(t.GetPosition().y)); r = mm(t.GetWidth(pcbnew.F_Cu)) / 2 if False else mm(t.GetWidth()) / 2
        for ly in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
            if t.IsOnLayer(ly):
                items.append((ly, 'via', t.GetNetname(), (p, p, r)))
    elif t.GetClass() == 'PCB_TRACK':
        items.append((t.GetLayer(), 'track', t.GetNetname(), ((mm(t.GetStart().x), mm(t.GetStart().y)), (mm(t.GetEnd().x), mm(t.GetEnd().y)), mm(t.GetWidth()) / 2)))
for fp in b.GetFootprints():
    for pd in fp.Pads():
        for ly in (pcbnew.F_Cu, pcbnew.B_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu):
            if pd.IsOnLayer(ly):
                poly = pd.GetEffectivePolygon(ly) if hasattr(pd, 'GetEffectivePolygon') else None
                try:
                    o = poly.Outline(0); pts = [(mm(o.CPoint(i).x), mm(o.CPoint(i).y)) for i in range(o.PointCount())]
                except Exception as e:
                    continue
                items.append((ly, 'pad', pd.GetNetname(), pts))
def dist(g1, g2, k2):
    a, c, r = g1
    if k2 == 'pad':
        pts = g2; best = 1e9
        for i in range(len(pts)):
            e, f = pts[i], pts[(i + 1) % len(pts)]
            best = min(best, seg_seg(a, c, e, f) - r)
        # inside the pad polygon (centre line start point inside)?
        return best
    e, f, r2 = g2
    return seg_seg(a, c, e, f) - r - r2
def run(label, nets, ownnets, layers):
    best = {}
    for (ly, k, n, g) in items:
        if n in nets and k == 'track' and ly in layers:
            for (ly2, k2, n2, g2) in items:
                if ly2 == ly and n2 not in ownnets and n2 != '':
                    d = dist(g, g2, k2)
                    if d < best.get(ly, (1e9,))[0]: best[ly] = (d, n2, k2, g[0])
    for ly, v in best.items():
        print('XCHECK %s on %s: min distance %.4f mm to %s (%s) near (%.3f,%.3f)' % (label, b.GetLayerName(ly), v[0], v[1], v[2], v[3][0], v[3][1]))
ANT = {'ANT1_NODE', 'ANT2_NODE', 'ANT3_NODE', 'RF_FEED'}
run('antenna feed tracks', ANT, ANT, {pcbnew.F_Cu})
run('XL1 tracks', {'XL1'}, {'XL1'}, {pcbnew.In1_Cu, pcbnew.F_Cu, pcbnew.In2_Cu, pcbnew.B_Cu})
run('XL2 tracks', {'XL2'}, {'XL2'}, {pcbnew.In1_Cu, pcbnew.F_Cu, pcbnew.In2_Cu, pcbnew.B_Cu})
run('XC1 tracks', {'XC1'}, {'XC1'}, {pcbnew.In2_Cu, pcbnew.In1_Cu})
run('XC2 tracks', {'XC2'}, {'XC2'}, {pcbnew.In2_Cu, pcbnew.In1_Cu})
run('USB pair tracks vs other nets', {'USB_DP', 'USB_DN'}, {'USB_DP', 'USB_DN'}, {pcbnew.F_Cu})
