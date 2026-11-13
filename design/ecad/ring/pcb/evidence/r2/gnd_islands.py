# gnd_islands.py board: groups the GND copper (zone fill pieces, pads, tracks, vias) by contact and prints every group
# outside the largest one with its box (model mm), to find the ground pieces the rules check calls unconnected
import sys, math, pcbnew
from pcbnew import ToMM, VECTOR2I
b = pcbnew.LoadBoard(sys.argv[1])
CU = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
nodes = []   # (kind, layers, geom)
for z in b.Zones():
    if z.GetNetname() != 'GND' or z.GetIsRuleArea(): continue
    for l in CU:
        if not z.IsOnLayer(l): continue
        ps = z.GetFilledPolysList(l)
        for i in range(ps.OutlineCount()):
            one = pcbnew.SHAPE_POLY_SET(); one.AddOutline(ps.Outline(i))
            for h in range(ps.HoleCount(i)): one.AddHole(ps.Hole(i, h))
            nodes.append(('fill', {l}, one))
for f in b.GetFootprints():
    for p in f.Pads():
        if p.GetNetname() == 'GND':
            nodes.append(('pad %s.%s' % (f.GetReference(), p.GetNumber()), {l for l in CU if p.IsOnLayer(l)}, p))
for t in b.GetTracks():
    if t.GetNetname() != 'GND': continue
    if t.Type() == pcbnew.PCB_VIA_T:
        i0, i1 = CU.index(t.TopLayer()), CU.index(t.BottomLayer())
        nodes.append(('via', set(CU[min(i0, i1):max(i0, i1) + 1]), t))
    else:
        nodes.append(('track', {t.GetLayer()}, t))
par = list(range(len(nodes)))
def f_(a):
    while par[a] != a: par[a] = par[par[a]]; a = par[a]
    return a
def pts(n):
    k, ls, g = n
    if k == 'fill': return []
    if k == 'track': return [g.GetStart(), g.GetEnd()]
    return [g.GetPosition()]
fills = [i for i, n in enumerate(nodes) if n[0] == 'fill']
items = [i for i, n in enumerate(nodes) if n[0] != 'fill']
for i in items:
    for j in fills:
        if nodes[i][1] & nodes[j][1] and any(nodes[j][2].Contains(p) for p in pts(nodes[i])):
            par[f_(i)] = f_(j)
for a in range(len(items)):
    for c in range(a + 1, len(items)):
        i, j = items[a], items[c]
        if not nodes[i][1] & nodes[j][1]: continue
        gi, gj = nodes[i][2], nodes[j][2]
        hit = False
        for p in pts(nodes[i]):
            if gj.HitTest(p, 1000): hit = True; break
        if not hit:
            for p in pts(nodes[j]):
                if gi.HitTest(p, 1000): hit = True; break
        if hit: par[f_(i)] = f_(j)
groups = {}
for i in range(len(nodes)): groups.setdefault(f_(i), []).append(i)
big = max(groups.values(), key=len)
print('ground groups', len(groups), 'largest', len(big))
for g in groups.values():
    if g is big: continue
    names = []
    xs, ys = [], []
    for i in g:
        k, ls, geo = nodes[i]
        if k == 'fill':
            bb = geo.BBox(); xs += [ToMM(bb.GetLeft()) - 100, ToMM(bb.GetRight()) - 100]; ys += [ToMM(bb.GetTop()) - 100, ToMM(bb.GetBottom()) - 100]
            names.append('fill ' + b.GetLayerName(list(ls)[0]))
        else:
            for p in pts(nodes[i]): xs.append(ToMM(p.x) - 100); ys.append(ToMM(p.y) - 100)
            names.append(k + ' ' + ','.join(b.GetLayerName(l) for l in sorted(ls)))
    print('GROUP box X %.2f..%.2f Y %.2f..%.2f: %s' % (min(xs), max(xs), min(ys), max(ys), '; '.join(names)[:400]))
