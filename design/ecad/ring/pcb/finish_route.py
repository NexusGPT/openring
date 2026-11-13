#!/usr/bin/env python3
"""finish_route.py in.kicad_pcb out.kicad_pcb [rounds] -- completes the connections the automatic router left open, with a
grid maze router (0.025 mm grid, 4 layers, 8 directions, laser microvia stacks), net by net, on the board's own rules:
track 0.100 mm, gap 0.075 mm (0.20 mm to the RF line and the USB pair outside their chip exit areas), via 0.20 / 0.10 with its
land 0.075 mm from other copper and hole-to-hole 0.20, no copper in the antenna zone, no via in a tail keep-out, copper
0.20 mm from the board edge (edge band 0.15 plus half a track). Every added track and via is a normal (unlocked) item.
The open connections come from KiCad's own rules check (kicad-cli pcb drc, JSON). Prints each connection it adds or fails.
Run with ./run_kipy.sh finish_route.py ..."""
import heapq, json, math, os, subprocess, sys, time
import numpy as np
import pcbnew
from pcbnew import VECTOR2I, FromMM, ToMM

HERE = os.path.dirname(os.path.abspath(__file__))
KC = os.environ.get("KICAD_CLI", "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli")
src, dst = sys.argv[1], sys.argv[2]
RIPUP = int(sys.argv[3]) if len(sys.argv) > 3 else 3        # rip-up rounds
RIP = 0.8                                                   # rip-up area: the open group's box plus 0.8 mm
G = 0.025
X0, Y0, W, H = -13.6, -6.3, 27.2, 12.6
NX, NY = int(round(W / G)) + 1, int(round(H / G)) + 1
OX = OY = 100.0
CU = [pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu]
TW, GAP = 0.1, 0.075
RF = {"ANT1_NODE", "ANT2_NODE", "ANT3_NODE", "RF_FEED", "ANT_TRIM"}
USB = {"USB_DP", "USB_DN"}
ANT_ZONE = [(-13.60, 3.10, -9.20, 6.30), (-9.20, 3.30, -8.75, 6.30)]
TAILS = [(-3.50, -5.60, -1.00, -3.40), (-3.50, 3.40, -1.00, 5.60)]
EXITS = [(1.90, -0.75, 2.80, -0.05), (3.80, 0.80, 4.75, 1.95)]
PWR = {"VBUS", "VBAT", "VSYS", "SW1", "SW2", "VDD_1V8", "VDD_3V0", "VMOT"}
M = 0.025         # round 2: 0.025 (run 2 left one gap of 0.0744 at 0.02); raster safety margin: a cell centre stands for its whole 0.025 cell

def ix(x): return int(round((x - X0) / G))
def iy(y): return int(round((y - Y0) / G))
XS = X0 + np.arange(NX) * G
YS = Y0 + np.arange(NY) * G
XX, YY = np.meshgrid(XS, YS)          # [y, x]

def disk(r):
    n = int(math.ceil(r / G))
    return [(dx, dy) for dx in range(-n, n + 1) for dy in range(-n, n + 1) if (dx * G) ** 2 + (dy * G) ** 2 <= r * r + 1e-12]
def dilate(m, r):
    out = np.zeros_like(m)
    for dx, dy in disk(r):
        sx0, sx1 = max(0, dx), NX + min(0, dx)
        sy0, sy1 = max(0, dy), NY + min(0, dy)
        out[sy0:sy1, sx0:sx1] |= m[sy0 - dy:sy1 - dy, sx0 - dx:sx1 - dx]
    return out

def capsule(a, b_, r):
    """boolean raster of a segment a-b with half width r"""
    x0, x1 = min(a[0], b_[0]) - r, max(a[0], b_[0]) + r
    y0, y1 = min(a[1], b_[1]) - r, max(a[1], b_[1]) + r
    i0, i1 = max(0, ix(x0) - 1), min(NX, ix(x1) + 2)
    j0, j1 = max(0, iy(y0) - 1), min(NY, iy(y1) + 2)
    px, py = XX[j0:j1, i0:i1], YY[j0:j1, i0:i1]
    dx, dy = b_[0] - a[0], b_[1] - a[1]
    L2 = dx * dx + dy * dy
    t = np.clip(((px - a[0]) * dx + (py - a[1]) * dy) / L2, 0, 1) if L2 > 0 else 0
    d = np.hypot(px - (a[0] + t * dx), py - (a[1] + t * dy))
    return (j0, j1, i0, i1), d <= r + 1e-9

def load(path):
    b = pcbnew.LoadBoard(path)
    return b

def mm(v): return ToMM(v)
def board_items(b):
    """copper items: (net, layers(list of idx), kind, data)"""
    items = []
    for f in b.GetFootprints():
        for p in f.Pads():
            ls = [i for i, l in enumerate(CU) if p.IsOnLayer(l)]
            if not ls: continue
            poly = p.GetEffectivePolygon(pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu)
            bb = p.GetBoundingBox()
            items.append((p.GetNetname(), ls, "pad", (mm(bb.GetLeft()) - OX, mm(bb.GetTop()) - OY, mm(bb.GetRight()) - OX, mm(bb.GetBottom()) - OY, p.GetShape() == pcbnew.PAD_SHAPE_CIRCLE)))
    for t in b.GetTracks():
        if t.Type() == pcbnew.PCB_VIA_T:
            i0, i1 = CU.index(t.TopLayer()), CU.index(t.BottomLayer())
            items.append((t.GetNetname(), list(range(min(i0, i1), max(i0, i1) + 1)), "via", (mm(t.GetPosition().x) - OX, mm(t.GetPosition().y) - OY, mm(t.GetWidth(t.TopLayer())) / 2)))
        else:
            items.append((t.GetNetname(), [CU.index(t.GetLayer())], "seg", ((mm(t.GetStart().x) - OX, mm(t.GetStart().y) - OY), (mm(t.GetEnd().x) - OX, mm(t.GetEnd().y) - OY), mm(t.GetWidth()) / 2)))
    return items

def raster(item, extra=0.0):
    net, ls, kind, d = item
    if kind == "pad":
        x0, y0, x1, y1, circ = d
        # (round 2 run 6 tried pads 0.02 larger here: 12 nets open in the first pass against 7; removed. The via margin
        # below covers the pad corner case instead)
        if circ:
            return capsule(((x0 + x1) / 2, (y0 + y1) / 2), ((x0 + x1) / 2, (y0 + y1) / 2), (x1 - x0) / 2 + extra)
        i0, i1 = max(0, ix(x0 - extra)), min(NX, ix(x1 + extra) + 1)
        j0, j1 = max(0, iy(y0 - extra)), min(NY, iy(y1 + extra) + 1)
        px, py = XX[j0:j1, i0:i1], YY[j0:j1, i0:i1]
        m = (px >= x0 - extra - 1e-9) & (px <= x1 + extra + 1e-9) & (py >= y0 - extra - 1e-9) & (py <= y1 + extra + 1e-9)
        return (j0, j1, i0, i1), m
    if kind == "via":
        x, y, r = d
        return capsule((x, y), (x, y), r + extra)
    a, b_, r = d
    return capsule(a, b_, r + extra)

def in_exit(item):
    net, ls, kind, d = item
    if kind != "seg": return False
    a, b_, r = d
    for e in EXITS:
        if min(a[0], b_[0]) < e[2] and max(a[0], b_[0]) > e[0] and min(a[1], b_[1]) < e[3] and max(a[1], b_[1]) > e[1]:
            return True
    return False

class Grid:
    def __init__(self, items):
        self.net_ids = {}
        self.lab = np.full((4, NY, NX), -1, dtype=np.int32)      # copper owner per cell (one net per cell)
        self.big = np.full((4, NY, NX), -1, dtype=np.int32)      # RF / USB copper widened by 0.125 (their 0.20 gap)
        self.trk = np.full((4, NY, NX), -1, dtype=np.int32)      # tracks only (the PWR 0.10 track gap)
        self.padlab = np.full((4, NY, NX), -1, dtype=np.int32)   # pads only (pin access halo)
        self.pwrtrk = np.zeros((4, NY, NX), bool)                # PWR tracks
        self.vias = []                                            # via centres (hole to hole)
        self.endlab = np.full((4, NY, NX), -1, dtype=np.int32)   # round 2: open escape ends (pin access halo)
        self.l2keep_t = np.zeros((NY, NX), bool); self.l2keep_v = np.zeros((NY, NX), bool)   # round 2: L2 under RF / USB
        # round 2 (run 8: a router via L2-L4 at U1 D10's land centre failed check_escapes): no router via within 0.10 mm of
        # a U1 or U2 ball centre, on any layer (the plan's tables fix every via of a ball land)
        self.landvia = np.zeros((NY, NX), bool)
        for (x_, y_) in BALLS:
            (j0, j1, i0, i1), m = capsule((x_, y_), (x_, y_), 0.10)
            v = self.landvia[j0:j1, i0:i1]; v[m] = True
        for it in items:
            self.add(it)
        for (n_, l_, p_) in OPEN_ENDS:
            if n_ in OPEN_NOW:
                (j0, j1, i0, i1), m = capsule(p_, p_, 0.06)
                v = self.endlab[l_, j0:j1, i0:i1]; v[m] = self.nid(n_)
        edge = np.zeros((NY, NX), bool)
        hx, hy, rc = 13.6, 6.3, 0.8
        ax, ay = np.abs(XX), np.abs(YY)
        m = 0.20
        edge |= (ax > hx - m) | (ay > hy - m)
        corner = (ax > hx - rc) & (ay > hy - rc) & (np.hypot(ax - (hx - rc), ay - (hy - rc)) > rc - m)
        edge |= corner
        self.edge_track = edge
        mv = 0.25
        self.edge_via = (ax > hx - mv) | (ay > hy - mv) | ((ax > hx - rc) & (ay > hy - rc) & (np.hypot(ax - (hx - rc), ay - (hy - rc)) > rc - mv))
        ant = np.zeros((NY, NX), bool)
        for r in ANT_ZONE:
            ant |= (XX > r[0] - 0.125) & (XX < r[2] + 0.125) & (YY > r[1] - 0.125) & (YY < r[3] + 0.125)
        self.ant = ant
        tail = np.zeros((NY, NX), bool)
        for r in TAILS:
            tail |= (XX > r[0] - 0.1) & (XX < r[2] + 0.1) & (YY > r[1] - 0.1) & (YY < r[3] + 0.1)
        self.tail = tail
    def nid(self, n):
        if n not in self.net_ids: self.net_ids[n] = len(self.net_ids)
        return self.net_ids[n]
    def add(self, it):
        net, ls, kind, d = it
        k = self.nid(net) if net else 10 ** 6       # pads with no net block every net
        (j0, j1, i0, i1), m = raster(it)
        for l in ls:
            v = self.lab[l, j0:j1, i0:i1]; v[m] = k
            if kind == "pad":
                v3 = self.padlab[l, j0:j1, i0:i1]; v3[m] = k
        if kind == "seg":
            for l in ls:
                v = self.trk[l, j0:j1, i0:i1]; v[m] = k
                if net in PWR:
                    v2 = self.pwrtrk[l, j0:j1, i0:i1]; v2[m] = True
        if (net in RF or net in USB) and kind == "seg" and not in_exit(it):
            (j0, j1, i0, i1), m = raster(it, 0.125)
            for l in ls:
                v = self.big[l, j0:j1, i0:i1]; v[m] = k
            if ls == [0] and net in L2KEEP_NETS:
                # round 2 (plan d.1, d.2: L2 is the line's reference): no L2 track of another net under the antenna line or
                # the USB pair, or within 0.20 mm of the line's edge; no via through L2 there
                (j0, j1, i0, i1), m = raster(it, L2KEEP + TW / 2 + M)
                v = self.l2keep_t[j0:j1, i0:i1]; v[m] = True
                (j0, j1, i0, i1), m = raster(it, L2KEEP + 0.1 + M)
                v = self.l2keep_v[j0:j1, i0:i1]; v[m] = True
        if kind == "via":
            self.vias.append((d[0], d[1]))
    def blocked(self, n, win):
        """track-centre and via-centre blocked masks for net n inside window (j0, j1, i0, i1)"""
        j0, j1, i0, i1 = win
        k = self.net_ids.get(n, -5)
        tb, vb = [], []
        oe = ((self.endlab >= 0) & (self.endlab != k)).any(axis=0)
        oe_t, oe_v = dilate(oe, 0.20), dilate(oe, 0.25)
        for l in range(4):
            other = (self.lab[l] >= 0) & (self.lab[l] != k)
            otherbig = (self.big[l] >= 0) & (self.big[l] != k)
            t = dilate(other, TW / 2 + GAP + M) | dilate(otherbig, TW / 2 + GAP + M) | self.edge_track | self.ant
            if n in PWR:
                t |= dilate((self.trk[l] >= 0) & (self.trk[l] != k), TW / 2 + 0.1 + M)
            else:
                t |= dilate(self.pwrtrk[l] & (self.lab[l] != k), TW / 2 + 0.1 + M)
            # round 2: via centres 0.01 farther from other copper (runs 2 and 3: a via 0.0744 from a pad corner, the raster
            # error on a diagonal is up to 0.025)
            v = dilate(other, 0.1 + GAP + M + 0.01) | dilate(otherbig, 0.1 + GAP + M + 0.01) | self.edge_via | self.ant | self.tail
            # round 2: another net's open escape end keeps room for its own via (0.25 to a track centre, 0.30 to a via)
            if END_HARD:
                t |= oe_t; v |= oe_v
            v = v | self.landvia
            if l == 1 and n != "GND" and n not in RF and n not in USB:
                t = t | self.l2keep_t; v = v | self.l2keep_v
            # own copper 0.05 deep is always free for a track centre (the track stays inside it)
            own = (self.lab[l] == k)
            deep = ~dilate(~own, TW / 2 - G)      # round 2: the centre cells of a 0.10 track count as own (was none)
            t &= ~deep
            tb.append(t[j0:j1, i0:i1]); vb.append(v[j0:j1, i0:i1])
        hv = np.zeros((j1 - j0, i1 - i0), bool)
        for (x, y) in self.vias:
            ci, cj = ix(x) - i0, iy(y) - j0
            n_ = int(math.ceil(0.30 / G))
            for dx, dy in disk(0.32):
                a, c = cj + dy, ci + dx
                if 0 <= a < hv.shape[0] and 0 <= c < hv.shape[1]:
                    hv[a, c] = True
        for l in range(4):
            vb[l] = vb[l] | hv
        # pin access: cells within 0.35 mm of another net's pad cost more (a route should not seal a pin it passes)
        halo = []
        for l in range(4):
            pm = (self.padlab[l] >= 0) & (self.padlab[l] != k)
            # round 2: the free end of another net's escape counts as a pin (a route should not seal it either)
            em = ((self.endlab >= 0) & (self.endlab != k)).any(axis=0)     # every layer: the end may need a via
            halo.append((dilate(pm, 0.35)[j0:j1, i0:i1]).astype(np.int8) + 2 * dilate(em, 0.35)[j0:j1, i0:i1].astype(np.int8))
        return tb, vb, halo

def components(items, n):
    """connected groups of net n's items (pads, tracks, vias), by raster overlap on a shared layer"""
    its = [it for it in items if it[0] == n]
    ras = [raster(it) for it in its]
    par = list(range(len(its)))
    def f(a):
        while par[a] != a:
            par[a] = par[par[a]]; a = par[a]
        return a
    for a in range(len(its)):
        (aj0, aj1, ai0, ai1), am = ras[a]
        for c in range(a + 1, len(its)):
            if not set(its[a][1]) & set(its[c][1]): continue
            (cj0, cj1, ci0, ci1), cm = ras[c]
            j0, j1, i0, i1 = max(aj0, cj0), min(aj1, cj1), max(ai0, ci0), min(ai1, ci1)
            if j0 >= j1 or i0 >= i1: continue
            if (am[j0 - aj0:j1 - aj0, i0 - ai0:i1 - ai0] & cm[j0 - cj0:j1 - cj0, i0 - ci0:i1 - ci0]).any():
                par[f(a)] = f(c)
    groups = {}
    for a in range(len(its)):
        groups.setdefault(f(a), []).append(its[a])
    return list(groups.values())

def cells_of(group, win):
    j0, j1, i0, i1 = win
    s = set()
    for it in group:
        (aj0, aj1, ai0, ai1), m = raster(it)
        ys, xs = np.nonzero(m)
        for y, x in zip(ys + aj0, xs + ai0):
            if j0 <= y < j1 and i0 <= x < i1:
                for l in it[1]:
                    s.add((l, y - j0, x - i0))
    return s

LF = [1.5, 1.0, 1.0, 2.0]       # L4 2.0 (round 2 tried 5.0 in run 4 and 3.0 in run 5: more nets open; back to 2.0)
END_HARD = os.environ.get("END_HARD", "0") == "1"   # hard protection of escape ends: tried, worse (board-notes-r2.md step 5)
HW = 1.3          # round 2: weighted A* (heuristic x 1.3): long nets finish inside the expansion limit
# round 2: L2 keep-clear under the antenna line: run 4 (0.20 mm from the edge, antenna line and USB pair) left 12 nets open in
# the first pass; now no L2 copper of another net under the antenna line or within the board gap 0.075 of its edge
# lead's ruling (round 2, after run 7): run 5's rule is the rule: no copper of another net on L2 under the antenna line
# (0.075 mm from its edge, the board gap); ground on L2 under it. L2KEEP=-1 turns it off for a trial.
L2KEEP = float(os.environ.get("L2KEEP", "0.075"))
L2KEEP_NETS = RF if L2KEEP >= 0 else set()
def astar(starts, goals, tb, vb, halo, viacost=20):
    goal_set = goals
    gl = np.array([(g[1], g[2]) for g in goals])
    def h(y, x):
        d = np.min(np.abs(gl[:, 0] - y) + np.abs(gl[:, 1] - x)) if len(gl) < 2000 else 0
        return d
    # coarse heuristic: distance to goal bbox
    gy0, gy1, gx0, gx1 = gl[:, 0].min(), gl[:, 0].max(), gl[:, 1].min(), gl[:, 1].max()
    def hb(y, x):
        dy = max(gy0 - y, 0, y - gy1); dx = max(gx0 - x, 0, x - gx1)
        return max(dx, dy) + 0.414 * min(dx, dy)
    best = {}
    pq = []
    for s in starts:
        l, y, x = s
        if tb[l][y, x] and s not in goal_set:
            continue
        best[s] = 0.0
        heapq.heappush(pq, (hb(y, x), 0.0, s, None))
    prev = {}
    NYw, NXw = tb[0].shape
    steps = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0), (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
    n = 0
    while pq:
        f_, g_, s, p = heapq.heappop(pq)
        if s in prev: continue
        prev[s] = p
        n += 1
        if n > 3000000: return None, n
        if s in goal_set and p is not None:
            path = [s]
            while prev[path[-1]] is not None:
                path.append(prev[path[-1]])
            return path[::-1], n
        l, y, x = s
        for dy, dx, c in steps:
            yy, xx = y + dy, x + dx
            if 0 <= yy < NYw and 0 <= xx < NXw and not tb[l][yy, xx]:
                if dy and dx and (tb[l][y, xx] or tb[l][yy, x]):
                    continue
                ns = (l, yy, xx)
                hv_ = halo[l][yy, xx]
                ng = g_ + c * LF[l] * (1.0 if not hv_ else 4.0 if hv_ == 1 else 12.0)
                if ng < best.get(ns, 1e18):
                    best[ns] = ng; heapq.heappush(pq, (ng + HW * hb(yy, xx), ng, ns, s))
        # via: to any other layer, all spanned layers free for a via here; no other layer change of this path within
        # 0.32 mm behind (hole to hole 0.20 between two vias of one route)
        recent = False
        q = s; steps_back = 0
        while q is not None and steps_back < 14:
            pq_ = prev.get(q)
            if pq_ is not None and pq_[0] != q[0] and math.hypot(pq_[1] - y, pq_[2] - x) * G < 0.32:
                recent = True; break
            q = pq_; steps_back += 1
        for l2 in (range(4) if not recent else []):
            if l2 == l: continue
            lo, hi = min(l, l2), max(l, l2)
            if all(not vb[k][y, x] for k in range(lo, hi + 1)) and not tb[l2][y, x]:
                ns = (l2, y, x); ng = g_ + viacost * (1 + 0.5 * (hi - lo - 1))
                if ng < best.get(ns, 1e18):
                    best[ns] = ng; heapq.heappush(pq, (ng + HW * hb(y, x), ng, ns, s))
    return None, n

def path_to_copper(path, win):
    j0, j1, i0, i1 = win
    segs, vias = [], []
    pts = [(int(l), round(float(X0 + (x + i0) * G), 4), round(float(Y0 + (y + j0) * G), 4)) for l, y, x in path]
    k = 0
    while k < len(pts):
        l = pts[k][0]
        run = [pts[k]]
        while k + 1 < len(pts) and pts[k + 1][0] == l:
            k += 1; run.append(pts[k])
        # simplify collinear
        simp = [run[0]]
        for q in run[1:]:
            if len(simp) >= 2:
                a, b_ = simp[-2], simp[-1]
                if abs((b_[1] - a[1]) * (q[2] - b_[2]) - (b_[2] - a[2]) * (q[1] - b_[1])) < 1e-9:
                    simp[-1] = q; continue
            simp.append(q)
        for a, b_ in zip(simp[:-1], simp[1:]):
            segs.append((l, (a[1], a[2]), (b_[1], b_[2])))
        if k + 1 < len(pts):
            # layer change(s) at this cell: one via over the whole span of consecutive changes
            l0 = l; m = k + 1
            while m + 1 < len(pts) and pts[m + 1][1:] == pts[m][1:]:
                m += 1
            l1 = pts[m][0]
            vias.append((pts[k][1], pts[k][2], min(l0, l1), max(l0, l1)))
            k = m
        else:
            k += 1
    return segs, vias

def drc_unconnected(path):
    rep = path[:-10] + "-fin.json"
    subprocess.run([KC, "pcb", "drc", "--severity-all", "--all-track-errors", "--refill-zones", "--format", "json", "-o", rep, path], capture_output=True, text=True)
    j = json.load(open(rep))
    return j.get("unconnected_items", []), j.get("violations", [])

def route_net(n, items, grid, quiet=False):
    """connects every group of net n (ground: only the group of the reported item); returns the new items, or None"""
    new = []
    comps = components(items + new, n)
    tries = 0
    # round 2 (lead's ruling f): the join limit follows the net's group count (round 1 stopped VDD_1V8 after a fixed 12
    # joins); each join merges at least two groups, so groups + 4 joins always suffice when every join succeeds
    limit = max(12, len(comps) + 4)
    bad = set()           # round 2: items of groups that failed; in the first pass the other groups are still joined
    first_fail = None
    while len(comps) > 1 and tries < limit:
        tries += 1
        comps.sort(key=lambda g: len(g))
        free = [g for g in comps if not any(repr(it) in bad for it in g)]
        if not free or (len(free) == 1 and len(comps) == len(free)):
            break
        g0 = free[0]; rest = [it for g in comps if g is not g0 for it in g]
        pts = []
        for it in g0 + rest:
            (aj0, aj1, ai0, ai1), m = raster(it)
            pts += [(aj0, ai0), (aj1, ai1)]
        pj = [p_[0] for p_ in pts]; pi = [p_[1] for p_ in pts]
        mg = int(3.0 / G)
        win = (max(0, min(pj) - mg), min(NY, max(pj) + mg), max(0, min(pi) - mg), min(NX, max(pi) + mg))
        tb, vb, halo = grid.blocked(n, win)
        S = ends_or_all(g0, win)
        T = set()
        for g in comps:
            if g is not g0:
                T |= ends_or_all(g, win)
        t0 = time.time()
        path, nexp = astar(S, T, tb, vb, halo)
        if not path:          # the free ends are walled in: any cell of the groups
            S, T = cells_of(g0, win), cells_of(rest, win)
            path, nexp2 = astar(S, T, tb, vb, halo); nexp += nexp2
        if not path:
            if not quiet:
                print("  FAIL", n, "group of", len(g0), "items at (%.2f, %.2f, %.2f, %.2f), expanded" % bbox_of(g0), nexp, "in %.1fs" % (time.time() - t0)); sys.stdout.flush()
            if not PARTIAL[0]:
                return None, g0
            first_fail = first_fail or g0
            bad |= {repr(it) for it in g0}
            continue
        segs, vias = path_to_copper(path, win)
        for l, a, c in segs:
            it = (n, [l], "seg", (a, c, TW / 2)); new.append(it); grid.add(it)
        for x, y, l0, l1 in vias:
            it = (n, list(range(l0, l1 + 1)), "via", (x, y, 0.1)); new.append(it); grid.add(it)
        comps = components(items + new, n)
    if first_fail is not None or len(comps) > 1:
        return (new if new else None), (first_fail or sorted(comps, key=len)[0])
    return new, None

OPEN_ENDS, OPEN_NOW = [], set()
def free_ends(group):
    """end points of the group's tracks that touch nothing else of the group (an escape's free end)"""
    out = []
    for it in group:
        if it[2] != "seg": continue
        a, c, r = it[3]
        for p_ in (a, c):
            hit = False
            for o in group:
                if o is it: continue
                if o[2] == "pad":
                    x0, y0, x1, y1, _ = o[3]
                    if x0 - 1e-6 <= p_[0] <= x1 + 1e-6 and y0 - 1e-6 <= p_[1] <= y1 + 1e-6 and set(o[1]) & set(it[1]): hit = True
                elif o[2] == "via":
                    if math.hypot(o[3][0] - p_[0], o[3][1] - p_[1]) <= o[3][2] + 1e-6 and set(o[1]) & set(it[1]): hit = True
                else:
                    a2, c2, r2 = o[3]
                    if set(o[1]) & set(it[1]) and (math.dist(a2, p_) < 1e-4 or math.dist(c2, p_) < 1e-4 or
                                                   (min(a2[0], c2[0]) - 1e-4 <= p_[0] <= max(a2[0], c2[0]) + 1e-4 and min(a2[1], c2[1]) - 1e-4 <= p_[1] <= max(a2[1], c2[1]) + 1e-4 and
                                                    abs((c2[0] - a2[0]) * (p_[1] - a2[1]) - (c2[1] - a2[1]) * (p_[0] - a2[0])) < 1e-6)):
                        hit = True
                if hit: break
            if not hit:
                out.append((it[1][0], p_))
    # round 2: a via whose far layer touches nothing else of the group is a free end there too (a scripted crossing stack,
    # for example U1 G1's L1-L3 stack or F2's L2-L3 via: the route continues on L3, as plan a.2 means)
    for it in group:
        if it[2] != "via": continue
        x_, y_, r_ = it[3]; used = set()
        for o in group:
            if o is it: continue
            if o[2] == "seg":
                a2, c2, r2 = o[3]
                if math.dist(a2, (x_, y_)) <= r_ + 1e-6 or math.dist(c2, (x_, y_)) <= r_ + 1e-6: used |= set(o[1])
            elif o[2] == "pad":
                x0, y0, x1, y1, _ = o[3]
                if x0 - 1e-6 <= x_ <= x1 + 1e-6 and y0 - 1e-6 <= y_ <= y1 + 1e-6: used |= set(o[1])
            elif o[2] == "via" and math.dist((o[3][0], o[3][1]), (x_, y_)) < 1e-4: used |= set(o[1])
        if used and len(used & set(it[1])) == 1:
            far = max(it[1]) if min(used & set(it[1])) == min(it[1]) else min(it[1])
            out.append((far, (x_, y_)))
    return out
def ends_or_all(group, win):
    fe = free_ends(group)
    allc = cells_of(group, win)
    if not fe:
        return allc
    j0, j1, i0, i1 = win
    keep = set()
    for (l, p_) in fe:
        cx, cy = ix(p_[0]) - i0, iy(p_[1]) - j0
        for (ll, yy, xx) in allc:
            if ll == l and abs(yy - cy) <= 2 and abs(xx - cx) <= 2:
                keep.add((ll, yy, xx))
    # a group with free ends may still be joined at its pads when the ends are walled in: ends first, pads as the fallback
    return keep if keep else allc
PARTIAL = [False]     # first pass: keep the connections made before a failure; rip-up: all or nothing
def bbox_of(group):
    xs, ys = [], []
    for it in group:
        if it[2] == "pad": xs += [it[3][0], it[3][2]]; ys += [it[3][1], it[3][3]]
        elif it[2] == "via": xs.append(it[3][0]); ys.append(it[3][1])
        else: xs += [it[3][0][0], it[3][1][0]]; ys += [it[3][0][1], it[3][1][1]]
    return min(xs), min(ys), max(xs), max(ys)
def touches(it, box):
    bx = bbox_of([it]); return bx[0] < box[2] and bx[2] > box[0] and bx[1] < box[3] and bx[3] > box[1]

b = load(src)
base = board_items(b)
BALLS = [(mm(p_.GetPosition().x) - OX, mm(p_.GetPosition().y) - OY) for f_ in b.GetFootprints() if f_.GetReference() in ("U1", "U2") for p_ in f_.Pads()]
routes = {}        # net -> items added here
def all_items():
    return base + [it for v in routes.values() for it in v]
unc, viol = drc_unconnected(src)
nets = []
for u in unc:
    for it in u["items"]:
        d = it.get("description", "")
        if "[" in d:
            n = d.split("[", 1)[1].split("]", 1)[0]
            if n not in nets and n not in RF and n not in USB and n != "GND": nets.append(n)
            break
# round 2: short nets first (the half perimeter of the box round the net's pads, smallest first): the short local joins at
# U1 (DCC, TXRTUNE, VDD_USB_3V3, the crystal lines) are made before long runs fill the chip's surroundings
def span_of_net(n):
    its = [it for it in base if it[0] == n and it[2] == "pad"]
    if not its: return 1e9
    bx = bbox_of(its); return (bx[2] - bx[0]) + (bx[3] - bx[1])
nets.sort(key=span_of_net)
# round 2: nets with an open escape end at U1 or U2 first (they have the least room), short first among them
def at_chip(n):
    for g_ in components(base, n):
        for (l_, p_) in free_ends(g_):
            if 1.5 < p_[0] < 10.5 and -2.6 < p_[1] < 2.6:
                return 0
    return 1
CHIP_FIRST = {n: at_chip(n) for n in nets}
nets.sort(key=lambda n: (CHIP_FIRST[n], span_of_net(n)))
# round 2 (b): the nets run 10 left open at U1's escapes go first of all (R2/full10/build-logs/3_finish_route.log)
# run 11 with this order (DECD, U1_VBUS, LCD_MOSI, OLED_PWR_EN, MIC_A_CLK, XL2, XL1 first) ended at 28 unconnected items
# against run 10's 11: off by default (FIRST_NETS=a,b,... turns it on)
FIRST = [n_ for n_ in os.environ.get("FIRST_NETS", "").split(",") if n_]
nets.sort(key=lambda n: (FIRST.index(n) if n in FIRST else len(FIRST)))
if os.environ.get("ONLY_NETS"):          # trial on a piece of the board (board-notes-r2.md): route only these nets
    nets = [n for n in nets if n in os.environ["ONLY_NETS"].split(",")]
print("open nets from the rules check:", len(nets), "unconnected items", len(unc)); sys.stdout.flush()
print("order (short first):", " ".join("%s %.1f" % (n, span_of_net(n)) for n in nets)); sys.stdout.flush()
# round 2: free ends of the open nets' escapes (scripted stubs), for the pin access halo of Grid.blocked
OPEN_ENDS = []
OPEN_NOW = set(nets)
for n_ in nets:
    for g_ in components(base, n_):
        if len(g_) > 1 or g_[0][2] != "pad":
            for (l_, p_) in free_ends(g_):
                OPEN_ENDS.append((n_, l_, p_))
print("open escape ends protected:", len(OPEN_ENDS)); sys.stdout.flush()
grid = Grid(all_items())
failed = {}
PARTIAL[0] = True
for n in nets:
    new, g0 = route_net(n, all_items(), grid)
    if new:
        routes[n] = routes.get(n, []) + new
        print("  routed", n, len(new), "items"); sys.stdout.flush()
    if g0 is not None:
        failed[n] = g0
PARTIAL[0] = False
print("first pass: failed", len(failed), sorted(failed)); sys.stdout.flush()
# rip-up and reroute: for a failed net, take out the routes of other nets near its open group, route it, then route them again;
# kept only when every net taken out is routed again
SWAPPED = set()
for rnd in range(RIPUP):
    progress = False
    for n in list(failed):
        g0 = failed[n]
        bx = bbox_of(g0); box = (bx[0] - RIP, bx[1] - RIP, bx[2] + RIP, bx[3] + RIP)
        victims = [m for m, its in routes.items() if m != n and any(touches(it, box) for it in its)]
        if not victims:
            continue
        saved = {m: routes.pop(m) for m in victims}
        g2 = Grid(all_items())
        new, _ = route_net(n, all_items(), g2, quiet=True)
        ok = new is not None
        newfail = {}
        if ok:
            routes[n] = routes.get(n, []) + new
            for m in sorted(victims, key=lambda m: (CHIP_FIRST.get(m, 1), span_of_net(m))):
                nm, gm = route_net(m, all_items(), g2, quiet=True)
                if nm is None:
                    newfail[m] = gm
                    # round 2: one victim may lose its route if the failed net is a chip escape net and the victim is
                    # not (it has room elsewhere and is retried below); never the same victim twice
                    if not (CHIP_FIRST.get(n, 1) == 0 and len(newfail) == 1 and CHIP_FIRST.get(m, 1) == 1 and m not in SWAPPED):
                        ok = False; break
                else:
                    routes[m] = nm
        if ok:
            del failed[n]; grid = g2; progress = True
            for m, gm in newfail.items():
                failed[m] = gm; SWAPPED.add(m)
            print("  rip-up: routed", n, "after taking out", victims, ("; now open: %s" % sorted(newfail)) if newfail else ""); sys.stdout.flush()
        else:
            routes.pop(n, None)
            for m in victims: routes[m] = saved[m]
    print("rip-up round", rnd, "failed", len(failed), sorted(failed)); sys.stdout.flush()
    if not progress: break
    grid = Grid(all_items())
    for n in list(failed):           # a net that failed may pass now that others moved
        PARTIAL[0] = True
        new, g0 = route_net(n, all_items(), grid, quiet=True)
        PARTIAL[0] = False
        if new:
            routes[n] = routes.get(n, []) + new
        if g0 is None:
            del failed[n]
            print("  routed on retry", n); sys.stdout.flush()
        else:
            failed[n] = g0

# write the routes into the board
for n, its in routes.items():
    for it in its:
        if it[2] == "seg":
            a, c, r = it[3]; l = it[1][0]
            t = pcbnew.PCB_TRACK(b); t.SetLayer(CU[l]); t.SetStart(VECTOR2I(FromMM(a[0] + OX), FromMM(a[1] + OY)))
            t.SetEnd(VECTOR2I(FromMM(c[0] + OX), FromMM(c[1] + OY))); t.SetWidth(FromMM(TW)); t.SetNet(b.FindNet(n)); b.Add(t)
        else:
            x, y, r = it[3]; l0, l1 = it[1][0], it[1][-1]
            v = pcbnew.PCB_VIA(b)
            v.SetViaType(pcbnew.VIATYPE_THROUGH if (l0, l1) == (0, 3) else pcbnew.VIATYPE_BLIND if l0 == 0 or l1 == 3 else pcbnew.VIATYPE_BURIED)
            v.SetLayerPair(CU[l0], CU[l1]); v.SetPosition(VECTOR2I(FromMM(x + OX), FromMM(y + OY))); v.SetWidth(FromMM(0.2)); v.SetDrill(FromMM(0.1))
            v.SetNet(b.FindNet(n)); b.Add(v)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(dst, b)
# clean-up: unlocked tracks and vias the rules check calls dangling are removed (dead ends of the automatic router), repeatedly
for k_ in range(12):
    unc, viol = drc_unconnected(dst)
    ids = set()
    for v in viol:
        if v["type"] in ("track_dangling", "via_dangling"):
            for it in v["items"]:
                ids.add(it["uuid"])
    if not ids: break
    b = load(dst)
    rm = [t for t in b.GetTracks() if t.m_Uuid.AsString() in ids and not t.IsLocked()]
    if not rm: break
    for t in rm: b.Remove(t)
    pcbnew.SaveBoard(dst, b)
    print("clean-up pass", k_, "removed", len(rm), "dangling items"); sys.stdout.flush()
b = load(dst)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(dst, b)
unc, viol = drc_unconnected(dst)
kinds = {}
for v in viol: kinds[v["type"]] = kinds.get(v["type"], 0) + 1
print("final: unconnected", len(unc), "violations", len(viol), kinds)
