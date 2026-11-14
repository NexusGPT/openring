# freespots.py board REF... : for each part (0201, pads 0.30 x 0.27 at +-0.285, courtyard 0.49 x 1.03), list legal spots on F.Cu (under face):
# courtyard clear of every other F courtyard (the eight parts themselves excluded, wherever they are), of the keep-free zones and the antenna zone,
# 0.15 inside the outline; each pad 0.10 or more from every F.Cu track, via and pad of another net, 0.21 from RF and USB copper (zone fill ignored, it refills).
# A spot is ranked by the distance from the part's signal pad to the nearest U1/U2 ball (or any pad) of the same net.
import sys, os, math, pcbnew
from pcbnew import ToMM
O = 100.0
EIGHT = {"C1", "C2", "C5", "C7", "C14", "FB1", "R71", "R72"}
b = pcbnew.LoadBoard(sys.argv[1])
cy = []
for m in b.GetFootprints():
    if (m.GetReference() in EIGHT and m.GetReference() in sys.argv[2:]) or m.GetLayer() != pcbnew.F_Cu: continue
    c = m.GetCourtyard(pcbnew.F_Cu)
    if not c.OutlineCount(): continue
    pts = [c.COutline(0).CPoint(i) for i in range(c.COutline(0).PointCount())]
    cy.append((min(ToMM(p.x) for p in pts) - O, min(ToMM(p.y) for p in pts) - O, max(ToMM(p.x) for p in pts) - O, max(ToMM(p.y) for p in pts) - O, m.GetReference()))
cy += [(-3.5, 3.4, -0.9, 5.6, "fold+"), (-3.5, -5.6, -0.9, -3.4, "fold-"), (-13.6, 3.1, -8.75, 6.3, "antenna")]
if os.environ.get("EXCL"): cy.append(tuple(map(float, os.environ["EXCL"].split(","))) + ("excluded",))
cu = []  # (net, kind, geom)
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T:
        if t.IsOnLayer(pcbnew.F_Cu): cu.append((t.GetNetname(), "c", (ToMM(t.GetPosition().x) - O, ToMM(t.GetPosition().y) - O, 0.1)))
    elif t.GetLayer() == pcbnew.F_Cu:
        cu.append((t.GetNetname(), "s", (ToMM(t.GetStart().x) - O, ToMM(t.GetStart().y) - O, ToMM(t.GetEnd().x) - O, ToMM(t.GetEnd().y) - O, ToMM(t.GetWidth()) / 2)))
for m in b.GetFootprints():
    if m.GetReference() in sys.argv[2:] or m.GetLayer() != pcbnew.F_Cu and m.GetReference() in EIGHT: continue
    for p in m.Pads():
        if p.IsOnLayer(pcbnew.F_Cu):
            bb = p.GetBoundingBox(); cu.append((p.GetNetname(), "r", (ToMM(bb.GetLeft()) - O, ToMM(bb.GetTop()) - O, ToMM(bb.GetRight()) - O, ToMM(bb.GetBottom()) - O)))
inner = []  # (net, kind, geom, layers) on In1, In2, B
CUL = [pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
for t in b.GetTracks():
    if t.Type() == pcbnew.PCB_VIA_T:
        inner.append((t.GetNetname(), "c", (ToMM(t.GetPosition().x) - O, ToMM(t.GetPosition().y) - O, 0.1), [l for l in CUL if t.IsOnLayer(l)]))
    elif t.GetLayer() in CUL:
        inner.append((t.GetNetname(), "s", (ToMM(t.GetStart().x) - O, ToMM(t.GetStart().y) - O, ToMM(t.GetEnd().x) - O, ToMM(t.GetEnd().y) - O, ToMM(t.GetWidth()) / 2), [t.GetLayer()]))
for m in b.GetFootprints():
    if m.GetReference() in sys.argv[2:]: continue
    for p in m.Pads():
        ls = [l for l in CUL if p.IsOnLayer(l)]
        if ls:
            bb = p.GetBoundingBox(); inner.append((p.GetNetname(), "r", (ToMM(bb.GetLeft()) - O, ToMM(bb.GetTop()) - O, ToMM(bb.GetRight()) - O, ToMM(bb.GetBottom()) - O), ls))
def via_ok(x, y, net):
    for n, k, g, ls in inner:
        if k == "c":
            d = math.hypot(g[0] - x, g[1] - y)
            if d < 0.30: return False          # hole to hole 0.20
            if n != net and d - g[2] - 0.1 < 0.075: return False
            continue
        if n == net: continue
        if k == "r": d = math.hypot(max(g[0] - x, 0, x - g[2]), max(g[1] - y, 0, y - g[3])) - 0.1
        else:
            if min(g[0], g[2]) > x + 0.5 or max(g[0], g[2]) < x - 0.5 or min(g[1], g[3]) > y + 0.5 or max(g[1], g[3]) < y - 0.5: continue
            vx, vy = g[2] - g[0], g[3] - g[1]; L = vx * vx + vy * vy
            t = 0 if L == 0 else max(0, min(1, ((x - g[0]) * vx + (y - g[1]) * vy) / L))
            d = math.hypot(x - g[0] - t * vx, y - g[1] - t * vy) - g[4] - 0.1
        if d < 0.08: return False
    for n, k, g in cu:   # F copper: other-net via holes
        if k == "c" and math.hypot(g[0] - x, g[1] - y) < 0.30: return False
    return True
def dpt_rect(px, py, r): return math.hypot(max(r[0] - px, 0, px - r[2]), max(r[1] - py, 0, py - r[3]))
def dseg_rect(g, r):
    # distance from segment (with half width) to rectangle, by sampling
    x0, y0, x1, y1, w = g; n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 0.01) + 1)
    return min(dpt_rect(x0 + (x1 - x0) * i / (n - 1), y0 + (y1 - y0) * i / (n - 1), r) for i in range(n)) - w
def clear(rect, net):
    for n, k, g in cu:
        if n == net and net != "": continue
        if k == "c": d = dpt_rect(g[0], g[1], rect) - g[2]
        elif k == "r": d = max(g[0] - rect[2], rect[0] - g[2], g[1] - rect[3], rect[1] - g[3], 0) if not (g[0] < rect[2] and rect[0] < g[2] and g[1] < rect[3] and rect[1] < g[3]) else -1
        else:
            if g[0] > rect[2] + 0.5 and g[2] > rect[2] + 0.5: continue
            if g[0] < rect[0] - 0.5 and g[2] < rect[0] - 0.5: continue
            if g[1] > rect[3] + 0.5 and g[3] > rect[3] + 0.5: continue
            if g[1] < rect[1] - 0.5 and g[3] < rect[1] - 0.5: continue
            d = dseg_rect(g, rect)
        if d < (0.21 if n in RFUSB else 0.10): return False
    return True
RFUSB = {"ANT1_NODE", "ANT2_NODE", "ANT3_NODE", "RF_FEED", "ANT_TRIM", "USB_DP", "USB_DN"}
for ref in sys.argv[2:]:
    m = b.FindFootprintByReference(ref); nets = {p.GetNumber(): p.GetNetname() for p in m.Pads()}
    sig = [k for k in nets if nets[k] != "GND"]
    tgt = {}
    for k in sig:
        tgt[k] = [(ToMM(p.GetPosition().x) - O, ToMM(p.GetPosition().y) - O, f.GetReference() + "." + p.GetNumber()) for f in b.GetFootprints() if f.GetReference() in ("U1", "U2") for p in f.Pads() if p.GetNetname() == nets[k]]
    res = []
    x = -13.3
    while x <= 13.3:
        y = -6.0
        while y <= 6.0:
            for rot in (0, 90):
                hx, hy = (0.515, 0.245) if rot == 0 else (0.245, 0.515)
                c = (x - hx, y - hy, x + hx, y + hy)
                if c[0] < -13.475 or c[2] > 13.475 or c[1] < -6.175 or c[3] > 6.175: continue
                if any(not (c[2] <= q[0] or c[0] >= q[2] or c[3] <= q[1] or c[1] >= q[3]) for q in cy): continue
                pp = {"1": (x + 0.285, y) if rot == 0 else (x, y - 0.285), "2": (x - 0.285, y) if rot == 0 else (x, y + 0.285)}
                ok = True
                for k in pp:
                    hw, hh = (0.135, 0.15) if rot == 0 else (0.15, 0.135)
                    if not clear((pp[k][0] - hw, pp[k][1] - hh, pp[k][0] + hw, pp[k][1] + hh), nets[k]): ok = False; break
                if not ok: continue
                vok = {k: via_ok(pp[k][0], pp[k][1], nets[k]) for k in pp}
                if os.environ.get("VIA") and not all(vok[k] for k in pp if nets[k] != "GND" or os.environ.get("VIA") == "all"): continue
                if os.environ.get("NEAR"):
                    nx, ny, nd = map(float, os.environ["NEAR"].split(","))
                    if math.hypot(x - nx, y - ny) > nd: continue
                for flip in (False, True):
                    q = pp if not flip else {"1": pp["2"], "2": pp["1"]}
                    if os.environ.get("NEARPAD"):
                        nx, ny, nd = map(float, os.environ["NEARPAD"].split(","))
                        if any(math.hypot(q[k][0] - nx, q[k][1] - ny) > nd for k in sig): continue
                    d = sum(min(math.hypot(q[k][0] - t[0], q[k][1] - t[1]) for t in tgt[k]) if tgt[k] else 0 for k in sig)
                    if os.environ.get("BALL"):
                        bx, by = map(float, os.environ["BALL"].split(",")); d = min(math.hypot(q[k][0] - bx, q[k][1] - by) for k in sig)
                    res.append((round(d, 3), round(x, 3), round(y, 3), rot + (180 if flip else 0), {k: (round(q[k][0], 3), round(q[k][1], 3)) for k in q}, "vias " + ",".join("%s:%s" % (k, vok[k if not flip else ('2' if k == '1' else '1')]) for k in q)))
            y = round(y + 0.05, 3)
        x = round(x + 0.05, 3)
    res.sort()
    if os.environ.get("SPREAD"):
        sp = float(os.environ["SPREAD"]); kept = []
        for r in res:
            if all(math.hypot(r[1] - k[1], r[2] - k[2]) >= sp or r[3] != k[3] for k in kept): kept.append(r)
        res = kept
    print("%s nets %s targets %s: %d legal spots; best 12:" % (ref, nets, {k: [t[2] for t in tgt[k]] for k in tgt}, len(res)))
    for r in res[:int(os.environ.get('TOP', '12'))]: print("   d %.3f at (%.3f,%.3f) rot-code %d pads %s %s" % r)
