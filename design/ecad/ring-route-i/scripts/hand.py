# hand.py in out NET sx sy slayer [NET sx sy slayer ...]
# Local exact-clearance maze search (0.025 grid) from a walled-in stub end to the nearest copper of the same net that lies
# more than 1.2 mm from the start; adds the found tracks (0.100) and microvias (0.20/0.10) to the board; refills zones; saves.
# Clearances are the board's rules measured to the exact item edges (pads by their bounding box): track centre 0.125 from
# other copper (0.075 gap + half width), 0.25 from RF/USB copper, 0.15 from PWR tracks; via centre 0.175 from other copper on
# every layer it spans (0.30 to RF/USB), via centres 0.30 apart (hole to hole 0.20), 0.25 from the board edge, none in the
# antenna zone or a tail keep-out, no track in the antenna zone. TOL 0.006 extra for the raster.
import heapq, math, os, sys
NOBOX = [x for x in os.environ.get("NOBOX", "").split(";") if x]
CTRL = set(x for x in os.environ.get("CTRL", "").split(",") if x)   # route-i: extra nets kept like RF (crystal lines XL1 XL2 XC1 XC2)
TW = float(os.environ.get("TW", "0.1")); SUP = set(os.environ.get("SUP", "VBAT,VMOT,U1_VBUS").split(",")); tw_of = lambda n: TW if n in SUP else 0.1; RFK = float(os.environ.get("RFKEEP", "0") or 0); WINP = float(os.environ.get("WIN", "2.0"))
import numpy as np
import pcbnew
from pcbnew import FromMM, ToMM, VECTOR2I
O = 100.0; G = 0.025; TOL = 0.006
CU = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]; LN = {"F": 0, "In1": 1, "In2": 2, "B": 3}
RF = {"ANT1_NODE", "ANT2_NODE", "ANT3_NODE", "RF_FEED", "ANT_TRIM"}; USB = {"USB_DP", "USB_DN"}
PWR = {"VBUS", "VBAT", "VSYS", "SW1", "SW2", "VDD_1V8", "VDD_3V0", "VMOT"}
KO = [(-13.60, 3.10, -9.20, 6.30), (-9.20, 3.30, -8.75, 6.30), (-3.50, -5.60, -1.00, -3.40), (-3.50, 3.40, -1.00, 5.60)]
ANT = KO[:2]
src, dst = sys.argv[1], sys.argv[2]
jobs = [(sys.argv[i], float(sys.argv[i + 1]), float(sys.argv[i + 2]), LN[sys.argv[i + 3]], sys.argv[i + 4], sys.argv[i + 5]) for i in range(3, len(sys.argv), 6)]
b = pcbnew.LoadBoard(src)

def items():
    out = []
    for f in b.GetFootprints():
        for p in f.Pads():
            ls = [i for i, l in enumerate(CU) if p.IsOnLayer(l)]
            if not ls: continue
            bb = p.GetBoundingBox()
            out.append((p.GetNetname(), ls, "pad", (ToMM(bb.GetLeft()) - O, ToMM(bb.GetTop()) - O, ToMM(bb.GetRight()) - O, ToMM(bb.GetBottom()) - O), f.GetReference() + "." + p.GetNumber()))
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            i0, i1 = CU.index(t.TopLayer()), CU.index(t.BottomLayer())
            out.append((t.GetNetname(), list(range(min(i0, i1), max(i0, i1) + 1)), "via", (ToMM(t.GetPosition().x) - O, ToMM(t.GetPosition().y) - O, ToMM(t.GetWidth(t.TopLayer())) / 2), ""))
        else:
            out.append((t.GetNetname(), [CU.index(t.GetLayer())], "seg", ((ToMM(t.GetStart().x) - O, ToMM(t.GetStart().y) - O), (ToMM(t.GetEnd().x) - O, ToMM(t.GetEnd().y) - O), ToMM(t.GetWidth()) / 2), ""))
    return out

def dist_field(it, XX, YY):
    """distance from grid points to the item's copper edge (negative inside)"""
    k, d = it[2], it[3]
    if k == "pad":
        x0, y0, x1, y1 = d
        dx = np.maximum(np.maximum(x0 - XX, XX - x1), 0); dy = np.maximum(np.maximum(y0 - YY, YY - y1), 0)
        return np.hypot(dx, dy)
    if k == "via":
        return np.hypot(XX - d[0], YY - d[1]) - d[2]
    (ax, ay), (cx, cy), r = d
    vx, vy = cx - ax, cy - ay; L2 = vx * vx + vy * vy
    t = np.clip(((XX - ax) * vx + (YY - ay) * vy) / L2, 0, 1) if L2 > 0 else 0
    return np.hypot(XX - ax - t * vx, YY - ay - t * vy) - r

def ibox(it):
    k, d = it[2], it[3]
    if k == "pad": return d
    if k == "via": return (d[0] - d[2], d[1] - d[2], d[0] + d[2], d[1] + d[2])
    (ax, ay), (cx, cy), r = d
    return (min(ax, cx) - r, min(ay, cy) - r, max(ax, cx) + r, max(ay, cy) + r)

def near(it, p, r):
    x0, y0, x1, y1 = ibox(it)
    return x0 - r <= p[0] <= x1 + r and y0 - r <= p[1] <= y1 + r

def route(net, sx, sy, sl, its, tx="a", ty="a", forbid=()):
    own = [it for it in its if it[0] == net]
    tgt = [it for it in own if not near(it, (sx, sy), 1.2)] if tx in ("a", "x") else [it for it in own if near(it, (float(tx), float(ty)), 0.03)]
    if tx == "x": tgt = [it for it in own if it[2] != "pad" and not near(it, (sx, sy), 0.06)]
    if not tgt: print(net, "no target copper"); return None
    allx = [sx] + [c for it in tgt for c in (ibox(it)[0], ibox(it)[2])]
    ally = [sy] + [c for it in tgt for c in (ibox(it)[1], ibox(it)[3])]
    X0, X1 = max(-13.6, min(allx) - WINP), min(13.6, max(allx) + WINP)
    Y0, Y1 = max(-6.3, min(ally) - 2.0), min(6.3, max(ally) + 2.0)
    XS = np.arange(X0, X1 + 1e-9, G); YS = np.arange(Y0, Y1 + 1e-9, G)
    XX, YY = np.meshgrid(XS, YS); NY, NX = XX.shape
    tb = np.zeros((4, NY, NX), bool); vb = np.zeros((4, NY, NX), bool); tg = np.zeros((4, NY, NX), bool)
    def win(bx, m):
        i0 = max(0, int((bx[0] - m - X0) / G) - 1); i1 = min(NX, int((bx[2] + m - X0) / G) + 2)
        j0 = max(0, int((bx[1] - m - Y0) / G) - 1); j1 = min(NY, int((bx[3] + m - Y0) / G) + 2)
        return j0, j1, i0, i1
    for it in its:
        bx = ibox(it)
        if bx[2] < X0 - 1 or bx[0] > X1 + 1 or bx[3] < Y0 - 1 or bx[1] > Y1 + 1: continue
        if it[0] == net:
            if it in tgt:
                j0, j1, i0, i1 = win(bx, 0)
                if j1 <= j0 or i1 <= i0: continue
                dd = dist_field(it, XX[j0:j1, i0:i1], YY[j0:j1, i0:i1])
                for l in it[1]: tg[l, j0:j1, i0:i1] |= dd <= (0.0 if it[2] == "pad" else -0.01)
            continue
        big = it[0] in RF or it[0] in USB or it[0] in CTRL   # route-i: the crystal lines (env CTRL) keep 0.25 / 0.30 like RF
        ct = 0.25 if big else (0.15 if ((it[0] in PWR or net in PWR) and it[2] == "seg") else 0.125)   # route-d: PWR gap also when the routed net is PWR
        ct += (tw_of(net) - 0.1) / 2   # route-e: wider own track (env TW, supply nets SUP only)
        cv = 0.30 if big else 0.175
        j0, j1, i0, i1 = win(bx, 0.35)
        if j1 <= j0 or i1 <= i0: continue
        dd = dist_field(it, XX[j0:j1, i0:i1], YY[j0:j1, i0:i1])
        for l in it[1]:
            tb[l, j0:j1, i0:i1] |= dd < ct + TOL
            vb[l, j0:j1, i0:i1] |= dd < cv + TOL
        if it[0] in RF and RFK:   # route-d: keep In1 (L2) under the antenna line ground: no own track or via there
            k = RFK; tb[1, j0:j1, i0:i1] |= dd < k + 0.05 + TOL; vb[1, j0:j1, i0:i1] |= dd < k + 0.10 + TOL
        if it[2] == "via":
            hole = np.hypot(XX[j0:j1, i0:i1] - it[3][0], YY[j0:j1, i0:i1] - it[3][1]) < 0.30 + TOL
            for l in range(4): vb[l, j0:j1, i0:i1] |= hole
    for it in own:                      # own vias: hole to hole too
        if it[2] == "via":
            bx = ibox(it); j0, j1, i0, i1 = win(bx, 0.35)
            if j1 <= j0 or i1 <= i0: continue
            hole = np.hypot(XX[j0:j1, i0:i1] - it[3][0], YY[j0:j1, i0:i1] - it[3][1]) < 0.30 + TOL
            for l in range(4): vb[l, j0:j1, i0:i1] |= hole
    # board edge, keep-outs
    hx, hy, rc = 13.6, 6.3, 0.8
    def outside(m):
        o = (np.abs(XX) > hx - m) | (np.abs(YY) > hy - m)
        cr = (np.abs(XX) > hx - rc) & (np.abs(YY) > hy - rc) & (np.hypot(np.abs(XX) - (hx - rc), np.abs(YY) - (hy - rc)) > rc - m)
        return o | cr
    tb |= outside(0.20)[None]; vb |= outside(0.25)[None]
    for k in KO:
        m = (XX > k[0] - 0.11) & (XX < k[2] + 0.11) & (YY > k[1] - 0.11) & (YY < k[3] + 0.11)
        vb |= m[None]
    for k in ANT:
        m = (XX > k[0] - 0.06) & (XX < k[2] + 0.06) & (YY > k[1] - 0.06) & (YY < k[3] + 0.06)
        tb |= m[None]
    for bxs in NOBOX:   # route-d: NOBOX="layer,x0,y0,x1,y1;..." no own copper there
        q = [float(v) for v in bxs.split(",")]; m = (XX > q[1]) & (XX < q[3]) & (YY > q[2]) & (YY < q[4]); tb[int(q[0])] |= m; vb[int(q[0])] |= m
    for (fx, fy) in forbid:
        vb |= (np.hypot(XX - fx, YY - fy) < 0.30 + TOL)[None]
    vb |= tb      # a via cell must also be free for a track on its layers (checked per span below)
    si, sj = int(round((sx - X0) / G)), int(round((sy - Y0) / G))
    print(net, "start", (sx, sy, sl), "cell free:", not tb[sl, sj, si], "window", (round(X0, 2), round(Y0, 2), round(X1, 2), round(Y1, 2)))
    tb[sl, sj, si] = False
    import os
    if os.environ.get("MAP"):
        r = int(float(os.environ["MAP"]) / G)
        for l in range(4):
            print("layer", l, "rows y from", round(Y0 + (sj - r) * G, 3), "cols x from", round(X0 + (si - r) * G, 3), "(# track blocked, v via-only blocked, . free, S start, T target)")
            for j in range(max(0, sj - r), min(NY, sj + r + 1)):
                row = ""
                for i in range(max(0, si - r), min(NX, si + r + 1)):
                    row += "S" if (j, i) == (sj, si) else "T" if tg[l, j, i] else "#" if tb[l, j, i] else "v" if vb[l, j, i] else "."
                print(row)
    # exact start point, then search
    D = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
    LC = [1.2, 1.0, 1.0, 1.3]
    VC = 12.0     # a via costs 12 cells (0.3 mm)
    tlist = np.argwhere(tg)
    if len(tlist) == 0: print(net, "target not in window"); return None
    tx = X0 + tlist[:, 2] * G; ty = Y0 + tlist[:, 1] * G
    def h(i, j): return float(np.min(np.hypot(tx - (X0 + i * G), ty - (Y0 + j * G)))) / G if len(tlist) < 50 else 0.0
    # heuristic: distance to the target box centre would be inadmissible; use a cheap lower bound
    tbx = (tx.min(), ty.min(), tx.max(), ty.max())
    def hb(i, j):
        x, y = X0 + i * G, Y0 + j * G
        dx = max(tbx[0] - x, 0, x - tbx[2]); dy = max(tbx[1] - y, 0, y - tbx[3])
        return math.hypot(dx, dy) / G
    start = (sl, sj, si)
    best = {start: 0.0}; prev = {}
    pq = [(hb(si, sj), 0.0, start)]
    n = 0; end = None
    while pq:
        f, g, s = heapq.heappop(pq)
        if g > best.get(s, 1e18) + 1e-9: continue
        n += 1
        l, j, i = s
        if tg[l, j, i]: end = s; break
        if n > 3000000: break
        for di, dj, c in D:
            i2, j2 = i + di, j + dj
            if not (0 <= i2 < NX and 0 <= j2 < NY) or tb[l, j2, i2]: continue
            if di and dj and (tb[l, j, i2] or tb[l, j2, i]): continue
            g2 = g + c * LC[l]; s2 = (l, j2, i2)
            if g2 < best.get(s2, 1e18) - 1e-9:
                best[s2] = g2; prev[s2] = s; heapq.heappush(pq, (g2 + hb(i2, j2), g2, s2))
        for l2 in range(4):
            if l2 == l: continue
            lo, hi = min(l, l2), max(l, l2)
            if vb[lo:hi + 1, j, i].any() and not (s == start and not vb[lo:hi + 1, j, i][[k for k in range(hi - lo + 1) if lo + k != sl]].any() and False): continue
            g2 = g + VC; s2 = (l2, j, i)
            if g2 < best.get(s2, 1e18) - 1e-9:
                best[s2] = g2; prev[s2] = s; heapq.heappush(pq, (g2 + hb(i, j), g2, s2))
    print(net, "expanded", n, "found", end is not None)
    if end is None: return None
    path = [end]
    while path[-1] in prev: path.append(prev[path[-1]])
    path.reverse()
    pts = [(l, X0 + i * G, Y0 + j * G) for (l, j, i) in path]
    pts[0] = (sl, sx, sy)
    return pts

def add(net, pts):
    nobj = b.FindNet(net); added = []
    # compress straight runs
    keep = [pts[0]]
    for k in range(1, len(pts) - 1):
        a, c, d = keep[-1], pts[k], pts[k + 1]
        if c[0] != a[0] or d[0] != c[0]: keep.append(c); continue
        v1 = (round((c[1] - a[1]) / G), round((c[2] - a[2]) / G)); v2 = (round((d[1] - c[1]) / G), round((d[2] - c[2]) / G))
        if v1[0] * v2[1] - v1[1] * v2[0] != 0 or (v1[0] * v2[0] + v1[1] * v2[1]) < 0: keep.append(c)
    keep.append(pts[-1])
    for a, c in zip(keep[:-1], keep[1:]):
        if a[0] == c[0]:
            if math.hypot(c[1] - a[1], c[2] - a[2]) < 1e-6: continue
            t = pcbnew.PCB_TRACK(b); t.SetLayer(CU[a[0]]); t.SetStart(VECTOR2I(FromMM(a[1] + O), FromMM(a[2] + O)))
            t.SetEnd(VECTOR2I(FromMM(c[1] + O), FromMM(c[2] + O))); t.SetWidth(FromMM(tw_of(net))); t.SetNet(nobj); b.Add(t)
            added.append("seg %s (%.3f,%.3f)-(%.3f,%.3f)" % (["F", "In1", "In2", "B"][a[0]], a[1], a[2], c[1], c[2]))
        else:
            l0, l1 = min(a[0], c[0]), max(a[0], c[0])
            v = pcbnew.PCB_VIA(b)
            v.SetViaType(pcbnew.VIATYPE_THROUGH if (l0, l1) == (0, 3) else pcbnew.VIATYPE_BLIND if l0 == 0 or l1 == 3 else pcbnew.VIATYPE_BURIED)
            v.SetLayerPair(CU[l0], CU[l1]); v.SetPosition(VECTOR2I(FromMM(a[1] + O), FromMM(a[2] + O))); v.SetWidth(FromMM(0.2)); v.SetDrill(FromMM(0.1)); v.SetNet(nobj); b.Add(v)
            added.append("via %s-%s (%.3f,%.3f)" % (["F", "In1", "In2", "B"][l0], ["F", "In1", "In2", "B"][l1], a[1], a[2]))
    for s in added: print("  add", net, s)
    return added

ok = True
for (net, sx, sy, sl, tx, ty) in jobs:
    forbid = []
    for tries in range(6):
        pts = route(net, sx, sy, sl, items(), tx, ty, forbid)
        if pts is None: break
        vs = [(pts[k][1], pts[k][2]) for k in range(1, len(pts)) if pts[k][0] != pts[k - 1][0]]
        bad = [v2 for k, v2 in enumerate(vs) for v1 in vs[:k] if 1e-6 < math.hypot(v2[0] - v1[0], v2[1] - v1[1]) < 0.30]
        if not bad: break
        print(net, "own vias closer than 0.30, retry forbidding", bad[0]); forbid.append(bad[0]); pts = None
    if pts is None: ok = False; print("FAILED", net, sx, sy); continue
    add(net, pts)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(dst); print("saved", dst, "all found" if ok else "some failed")
