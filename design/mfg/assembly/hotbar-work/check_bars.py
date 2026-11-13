"""Is the place of each proposed copper alignment bar free on F.Cu of a copy of ring.kicad_pcb?
usage: run_kipy.sh check_bars.py <board> ; prints the nearest F.Cu track, pad and filled zone copper to each bar (plan distance)."""
import sys, math, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
bars = []
for sg in (1, -1):
    for (x0, x1, y0, y1) in ((-3.65, -3.55, 3.40, 4.00), (-0.95, -0.85, 3.40, 4.00)):
        a, c = sorted((sg * y0, sg * y1))
        bars.append((x0 + 100, x1 + 100, a + 100, c + 100))

def seg_rect_dist(p, q, r, n=40):
    best = 9e9
    for i in range(n + 1):
        t = i / n
        x, y = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
        dx = max(r[0] - x, 0, x - r[1]); dy = max(r[2] - y, 0, y - r[3])
        best = min(best, math.hypot(dx, dy))
    return best

for r in bars:
    near = []
    for t in b.GetTracks():
        if t.GetLayer() != pcbnew.F_Cu and t.GetClass() != "PCB_VIA":
            continue
        if t.GetClass() == "PCB_VIA":
            c = t.GetPosition(); p = (c.x / 1e6, c.y / 1e6); d = seg_rect_dist(p, p, r) - t.GetWidth() / 2e6
            near.append((d, f"via {t.GetNetname()}"))
        else:
            s, e = t.GetStart(), t.GetEnd()
            d = seg_rect_dist((s.x / 1e6, s.y / 1e6), (e.x / 1e6, e.y / 1e6), r) - t.GetWidth() / 2e6
            near.append((d, f"track {t.GetNetname()} w {t.GetWidth()/1e6:.3f}"))
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if not p.IsOnLayer(pcbnew.F_Cu):
                continue
            bb = p.GetBoundingBox()
            pr = (bb.GetLeft() / 1e6, bb.GetRight() / 1e6, bb.GetTop() / 1e6, bb.GetBottom() / 1e6)
            dx = max(r[0] - pr[1], pr[0] - r[1], 0); dy = max(r[2] - pr[3], pr[2] - r[3], 0)
            near.append((math.hypot(dx, dy), f"pad {fp.GetReference()}.{p.GetNumber()} {p.GetNetname()}"))
    zone_hit = []
    for z in b.Zones():
        if not z.IsOnLayer(pcbnew.F_Cu):
            continue
        poly = z.GetFilledPolysList(pcbnew.F_Cu)
        for (x, y) in ((r[0], r[2]), (r[1], r[3]), ((r[0] + r[1]) / 2, (r[2] + r[3]) / 2)):
            if poly.Contains(pcbnew.VECTOR2I(int(x * 1e6), int(y * 1e6))):
                zone_hit.append(z.GetNetname())
    near.sort()
    print(f"bar X {r[0]-100:.2f}..{r[1]-100:.2f} Y {r[2]-100:.2f}..{r[3]-100:.2f}: nearest " + "; ".join(f"{n} {d:.3f}" for d, n in near[:3]) + f"; F.Cu zone fill at the bar: {sorted(set(zone_hit)) or 'none'}")
