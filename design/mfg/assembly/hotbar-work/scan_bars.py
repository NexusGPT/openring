"""Find free places for 0.10 x 0.60 copper alignment bars beside each foot X edge on F.Cu of a copy of ring.kicad_pcb.
Free = at least 0.10 mm (plan) from every F.Cu track, via and pad of the board (zones ignored: a refill clears around new copper).
usage: run_kipy.sh scan_bars.py <board>"""
import sys, math, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
items = []
for t in b.GetTracks():
    if t.GetClass() == "PCB_VIA":
        c = t.GetPosition(); w = t.GetWidth(pcbnew.F_Cu) / 1e6
        items.append(("via " + t.GetNetname(), (c.x / 1e6, c.y / 1e6), (c.x / 1e6, c.y / 1e6), w / 2))
    elif t.GetLayer() == pcbnew.F_Cu:
        s, e = t.GetStart(), t.GetEnd()
        items.append(("track " + t.GetNetname(), (s.x / 1e6, s.y / 1e6), (e.x / 1e6, e.y / 1e6), t.GetWidth() / 2e6))
pads = []
for fp in b.GetFootprints():
    for p in fp.Pads():
        if p.IsOnLayer(pcbnew.F_Cu):
            bb = p.GetBoundingBox()
            pads.append((f"pad {fp.GetReference()}.{p.GetNumber()}", (bb.GetLeft() / 1e6, bb.GetRight() / 1e6, bb.GetTop() / 1e6, bb.GetBottom() / 1e6)))

def dist_rect(r):
    best = (9e9, "")
    for name, p, q, hw in items:
        n = 30
        for i in range(n + 1):
            t = i / n
            x, y = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
            d = math.hypot(max(r[0] - x, 0, x - r[1]), max(r[2] - y, 0, y - r[3])) - hw
            if d < best[0]:
                best = (d, name)
    for name, pr in pads:
        d = math.hypot(max(r[0] - pr[1], pr[0] - r[1], 0), max(r[2] - pr[3], pr[2] - r[3], 0))
        if d < best[0]:
            best = (d, name)
    return best

for sg, jn in ((1, "J_BAND_B"), (-1, "J_BAND_A")):
    for side, xs in (("left (-X) edge", [(-3.65 - k * 0.05, -3.55 - k * 0.05) for k in range(0, 5)]), ("right (+X) edge", [(-0.95 + k * 0.05, -0.85 + k * 0.05) for k in range(0, 5)])):
        found = []
        for (x0, x1) in xs:
            for j in range(0, 23):
                y0 = 3.40 + j * 0.05
                y1 = y0 + 0.60
                if y1 > 5.15 + 1e-9:
                    break
                a, c = sorted((sg * y0, sg * y1))
                d, n = dist_rect((x0 + 100, x1 + 100, a + 100, c + 100))
                if d >= 0.10:
                    found.append((x0, x1, y0, y1, d, n))
        if found:
            f = sorted(found, key=lambda v: (abs(v[0] - xs[0][0]), v[2]))[0]
            print(f"{jn} {side}: FREE bar X {f[0]:.2f} to {f[1]:.2f}, |Y| {f[2]:.2f} to {f[3]:.2f} (nearest {f[5]} {f[4]:.3f}); {len(found)} free places")
        else:
            print(f"{jn} {side}: NO free 0.10 x 0.60 place within 0.20 of the foot edge, |Y| 3.40 to 5.15")
