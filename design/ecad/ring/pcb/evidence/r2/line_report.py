# line_report.py board: (1) antenna line: closest copper of another net on L1 and on L2 to the line's L1 tracks (edge to edge),
# and the count of other-net items on L1 and L2 closer than 0.50 mm (outside RF_CHIP_EXIT); (2) XL1, XL2: routed length
# (tracks, all layers) and every other-net track or via within 0.20 mm of them
import sys, math, pcbnew
from pcbnew import ToMM
b = pcbnew.LoadBoard(sys.argv[1])
RF = {"ANT1_NODE", "ANT2_NODE", "ANT3_NODE", "RF_FEED"}
EXIT = (1.90, -0.75, 2.80, -0.05)
def m(v): return (ToMM(v.x) - 100, ToMM(v.y) - 100)
def pseg(p, a, c):
    dx, dy = c[0] - a[0], c[1] - a[1]; L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2)); return math.dist(p, (a[0] + t * dx, a[1] + t * dy))
def samples(a, c):
    n = max(2, int(math.dist(a, c) / 0.01)); return [(a[0] + (c[0] - a[0]) * i / n, a[1] + (c[1] - a[1]) * i / n) for i in range(n + 1)]
def items(layer):
    out = []
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            if t.IsOnLayer(layer): out.append((t.GetNetname(), 'via', [m(t.GetPosition())], ToMM(t.GetWidth(layer)) / 2))
        elif t.GetLayer() == layer:
            out.append((t.GetNetname(), 'track', samples(m(t.GetStart()), m(t.GetEnd())), ToMM(t.GetWidth()) / 2))
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.IsOnLayer(layer):
                bb = p.GetBoundingBox(); x0, y0, x1, y1 = ToMM(bb.GetLeft()) - 100, ToMM(bb.GetTop()) - 100, ToMM(bb.GetRight()) - 100, ToMM(bb.GetBottom()) - 100
                pts = [(x0 + (x1 - x0) * i / 6, y0 + (y1 - y0) * j / 6) for i in range(7) for j in range(7)]
                out.append((p.GetNetname(), 'pad %s.%s' % (f.GetReference(), p.GetNumber()), pts, 0.0))
    return out
rf = [(m(t.GetStart()), m(t.GetEnd()), ToMM(t.GetWidth()) / 2) for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T and t.GetLayer() == pcbnew.F_Cu and t.GetNetname() in RF]
for lname, layer in (('L1', pcbnew.F_Cu), ('L2', pcbnew.In1_Cu)):
    best = None; n05 = 0
    for net, kind, pts, hw in items(layer):
        if net in RF or net == 'ANT_TRIM' or (net == 'GND' and layer == pcbnew.In1_Cu): continue
        if net == 'GND' and kind.startswith('via') is False and layer == pcbnew.F_Cu and False: continue
        dmin = None
        for p in pts:
            if EXIT[0] <= p[0] <= EXIT[2] and EXIT[1] <= p[1] <= EXIT[3]: continue
            d = min(pseg(p, a, c) - w for a, c, w in rf) - hw
            dmin = d if dmin is None else min(dmin, d)
        if dmin is None: continue
        if dmin < 0.5: n05 += 1
        if best is None or dmin < best[0]: best = (dmin, net, kind)
    print('%s: closest other-net copper to the antenna line edge: %.3f mm (%s, %s); items under 0.50 mm: %d' % (lname, best[0], best[1], best[2], n05))
for xl in ('XL1', 'XL2'):
    segs = [(m(t.GetStart()), m(t.GetEnd()), t.GetLayer(), ToMM(t.GetWidth()) / 2) for t in b.GetTracks() if t.Type() == pcbnew.PCB_TRACE_T and t.GetNetname() == xl]
    L = sum(math.dist(a, c) for a, c, l, w in segs); nv = sum(1 for t in b.GetTracks() if t.Type() == pcbnew.PCB_VIA_T and t.GetNetname() == xl)
    near = {}
    for t in b.GetTracks():
        if t.GetNetname() in (xl, ''): continue
        for a, c, l, w in segs:
            if t.Type() == pcbnew.PCB_VIA_T:
                if not t.IsOnLayer(l): continue
                d = pseg(m(t.GetPosition()), a, c) - w - ToMM(t.GetWidth(l)) / 2
            elif t.GetLayer() == l:
                d = min(pseg(p, a, c) for p in samples(m(t.GetStart()), m(t.GetEnd()))) - w - ToMM(t.GetWidth()) / 2
            else: continue
            if d < 0.20:
                k = (t.GetNetname(), b.GetLayerName(l)); near[k] = min(near.get(k, 9), d)
    print('%s: routed length %.2f mm in %d tracks, %d vias; other nets within 0.20 mm: %s' % (xl, L, len(segs), nv, ', '.join('%s on %s %.3f' % (k[0], k[1], v) for k, v in sorted(near.items(), key=lambda kv: kv[1])) or 'none'))
