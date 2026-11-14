"""rb_res.py: resistance (pixel mesh), drawn-copper graph (lengths, track-sum resistance), clearance, impedance formulas."""
import math, heapq
import numpy as np
from PIL import Image, ImageDraw
import scipy.sparse as sp
import scipy.sparse.linalg as spl
from scipy import ndimage

RHO = 1.72e-5      # ohm mm (band-interface.md line 132)
VIA_R = 1e-3       # ohm per layer step (brief: 1 milliohm per microvia)


def pad_mask(b, k, ref, pin):
    """boolean raster of every flash/region of ref,pin on layer k"""
    im = Image.new('L', (b.W, b.H), 0)
    dr = ImageDraw.Draw(im)
    L = b.layers[k]
    for f in L.flashes:
        if f[3] == ref and f[4] == pin:
            for pg in f[2]:
                if pg and pg[0] == 'c':
                    b._dcirc(dr, pg[1], pg[2], pg[3])
                else:
                    b._dpoly(dr, pg)
    for (rg, r, p, n) in L.regions:
        if r == ref and p == pin:
            b._dpoly(dr, rg)
    return np.asarray(im, dtype=bool)


def net_masks(b, group):
    out = []
    for k in range(len(b.layers)):
        gm = b.group_map(k)
        out.append(b.masks[k] & (gm[b.labs[k]] == group))
    return out


def build_mesh(b, group, rs):
    """rs: sheet resistance per layer (ohm/sq). returns dict(masks, idx, N, G sparse)"""
    masks = net_masks(b, group)
    idx, N = [], 0
    for m in masks:
        ix = -np.ones(m.shape, dtype=np.int64)
        n = int(m.sum())
        ix[m] = np.arange(N, N + n)
        idx.append(ix); N += n
    I, J, Gv = [], [], []
    for k, m in enumerate(masks):
        g = 1.0 / rs[k]
        for a, bb in ((m[:, :-1] & m[:, 1:], (slice(None), slice(0, -1), slice(None), slice(1, None))), (m[:-1, :] & m[1:, :], None)):
            pass
        h = m[:, :-1] & m[:, 1:]
        ii = idx[k][:, :-1][h]; jj = idx[k][:, 1:][h]
        I.append(ii); J.append(jj); Gv.append(np.full(ii.shape, g))
        v = m[:-1, :] & m[1:, :]
        ii = idx[k][:-1, :][v]; jj = idx[k][1:, :][v]
        I.append(ii); J.append(jj); Gv.append(np.full(ii.shape, g))
    # holes: join adjacent copper layers through the barrel: 1 milliohm per layer step, spread over the hole area
    nvia = 0
    for d in b.drills:
        if not d['plated'] or d['span'] is None:
            continue
        a, c = d['span']
        for (hx, hy, dia) in d['holes']:
            i0, j0 = b.ij(hx, hy)
            r = max(1, int(round(dia / 2.0 / b.res)))
            ys, xs = np.ogrid[-r:r + 1, -r:r + 1]
            disk = (ys * ys + xs * xs) <= r * r
            ks = []
            for k in range(a - 1, c):
                if 0 <= i0 < b.H and 0 <= j0 < b.W and masks[k][i0, j0]:
                    ks.append(k)
            if len(ks) < 2:
                continue
            nvia += 1
            for q in range(len(ks) - 1):
                k1, k2 = ks[q], ks[q + 1]
                sl = (slice(i0 - r, i0 + r + 1), slice(j0 - r, j0 + r + 1))
                m1 = masks[k1][sl] & masks[k2][sl] & disk
                n = int(m1.sum())
                if n == 0:
                    continue
                gi = 1.0 / (VIA_R * (k2 - k1)) / n
                I.append(idx[k1][sl][m1]); J.append(idx[k2][sl][m1]); Gv.append(np.full(n, gi))
    I = np.concatenate(I); J = np.concatenate(J); Gv = np.concatenate(Gv)
    A = sp.coo_matrix((np.concatenate([Gv, Gv, -Gv, -Gv]), (np.concatenate([I, J, I, J]), np.concatenate([I, J, J, I]))), shape=(N, N)).tocsr()
    return dict(masks=masks, idx=idx, N=N, G=A, nvia=nvia)


def pad_nodes(b, mesh, pads):
    nodes = set()
    for (ref, pin) in pads:
        for k in range(len(b.layers)):
            if not any((f[3] == ref and f[4] == pin) for f in b.layers[k].flashes) and not any((r == ref and p == pin) for (_, r, p, _) in b.layers[k].regions):
                continue
            pm = pad_mask(b, k, ref, pin) & mesh['masks'][k]
            nodes |= set(mesh['idx'][k][pm].tolist())
    return sorted(nodes)


def resistance(mesh, src, snk):
    """R between two node sets (ideal equipotentials), solves the Laplace system"""
    G = mesh['G']; N = mesh['N']
    src = np.array(src, dtype=np.int64); snk = np.array(snk, dtype=np.int64)
    fixed = np.zeros(N, dtype=bool); fixed[src] = True; fixed[snk] = True
    V = np.zeros(N); V[src] = 1.0
    free = np.flatnonzero(~fixed)
    A = G[free][:, free]
    rhs = -G[free][:, src].sum(axis=1).A1
    # restrict to the component of the free nodes connected to the sources (others float)
    x = spl.spsolve(A.tocsc(), rhs) if len(free) else np.zeros(0)
    V[free] = x
    I = (G[src] @ V).sum()
    return (1.0 / I) if I > 0 else float('inf'), int(len(free))


# ------------------------------------------------------------ graph of drawn copper
class DGraph:
    def __init__(self, b, group_ok, rs, nets_of=None):
        """group_ok(k, x, y) -> bool: whether a draw midpoint belongs to the wanted copper"""
        self.adj = {}
        self.b, self.rs = b, rs
        self.total_len = 0.0
        self.draws = []
        for k, L in enumerate(b.layers):
            for (x1, y1, x2, y2, w, na) in L.draws:
                if not group_ok(k, (x1 + x2) / 2, (y1 + y2) / 2):
                    continue
                ln = math.hypot(x2 - x1, y2 - y1)
                self.total_len += ln
                self.draws.append((k, x1, y1, x2, y2, w, ln))
                a, c = self.key(k, x1, y1), self.key(k, x2, y2)
                if a == c:
                    continue
                self.edge(a, c, ln, rs[k] * ln / w)
        # an end point that lies inside the body of another draw (width / 2) joins it there (KiCad joins tracks that overlap)
        byl = {}
        for dd in self.draws:
            byl.setdefault(dd[0], []).append(dd)
        for k, lst in byl.items():
            for a in lst:
                for (px, py) in ((a[1], a[2]), (a[3], a[4])):
                    ek = self.key(k, px, py)
                    for bb in lst:
                        if bb is a:
                            continue
                        dx, dy = bb[3] - bb[1], bb[4] - bb[2]
                        L2 = dx * dx + dy * dy
                        if L2 == 0:
                            continue
                        t = max(0.0, min(1.0, ((px - bb[1]) * dx + (py - bb[2]) * dy) / L2))
                        qx, qy = bb[1] + t * dx, bb[2] + t * dy
                        dist = math.hypot(px - qx, py - qy)
                        if 0.0015 < dist <= bb[5] / 2 + 0.001:
                            qk = self.key(k, qx, qy)
                            self.edge(ek, qk, dist, 0.0)
                            for (ex, ey) in ((bb[1], bb[2]), (bb[3], bb[4])):
                                l_ = math.hypot(qx - ex, qy - ey)
                                if self.key(k, ex, ey) != qk:
                                    self.edge(qk, self.key(k, ex, ey), l_, rs[k] * l_ / bb[5])
        # flashes: join draw nodes inside the same flash by chords
        self.nodes_by_layer = {}
        for n in self.adj:
            self.nodes_by_layer.setdefault(n[0], []).append(n)
        for k, L in enumerate(b.layers):
            for f in L.flashes:
                if group_ok(k, f[0], f[1]):
                    self.adj.setdefault(self.key(k, f[0], f[1]), [])
            fb = []
            for f in L.flashes:
                if group_ok(k, f[0], f[1]):
                    xs, ys = [], []
                    for pg in f[2]:
                        if pg and pg[0] == 'c':
                            xs += [pg[1] - pg[3] / 2, pg[1] + pg[3] / 2]; ys += [pg[2] - pg[3] / 2, pg[2] + pg[3] / 2]
                        else:
                            xs += [p[0] for p in pg]; ys += [p[1] for p in pg]
                    fb.append((f, min(xs), max(xs), min(ys), max(ys)))
            for a_ in range(len(fb)):                      # overlapping lands of one layer (a via land on a pad edge) are one copper piece
                for c_ in range(a_ + 1, len(fb)):
                    A, B = fb[a_], fb[c_]
                    if A[1] <= B[2] + 0.002 and B[1] <= A[2] + 0.002 and A[3] <= B[4] + 0.002 and B[3] <= A[4] + 0.002:
                        self.edge(self.key(k, A[0][0], A[0][1]), self.key(k, B[0][0], B[0][1]), math.hypot(A[0][0] - B[0][0], A[0][1] - B[0][1]), 0.0)
            nodes = [n for n in self.adj if n[0] == k]      # draw end points and flash centres (overlapping lands join)
            for f in L.flashes:
                if not group_ok(k, f[0], f[1]):
                    continue
                xs, ys = [], []
                for pg in f[2]:
                    if pg and pg[0] == 'c':
                        xs += [pg[1] - pg[3] / 2, pg[1] + pg[3] / 2]; ys += [pg[2] - pg[3] / 2, pg[2] + pg[3] / 2]
                    else:
                        xs += [p[0] for p in pg]; ys += [p[1] for p in pg]
                x0, x1_, y0, y1_ = min(xs) - 0.002, max(xs) + 0.002, min(ys) - 0.002, max(ys) + 0.002
                ins = [n for n in nodes if x0 <= n[1] / 1000.0 <= x1_ and y0 <= n[2] / 1000.0 <= y1_]
                fk = self.key(k, f[0], f[1])
                self.adj.setdefault(fk, [])      # every flash is a node (a pad with no track on its own layer is reached by a hole)
                for n in ins:
                    if n != fk:
                        ln = math.hypot(n[1] / 1000.0 - f[0], n[2] / 1000.0 - f[1])
                        self.edge(fk, n, ln, 0.0)   # pad copper: ideal, length kept
                for i in range(len(ins)):
                    for j in range(i + 1, len(ins)):
                        ln = math.hypot(ins[i][1] - ins[j][1], ins[i][2] - ins[j][2]) / 1000.0
                        self.edge(ins[i], ins[j], ln, 0.0)
        # snap: nodes of one layer within 3 micrometres are one point (rounding of end points at the half micrometre)
        buckets = {}
        for n in list(self.adj):
            buckets.setdefault((n[0], n[1] // 3, n[2] // 3), []).append(n)
        for (k, bx, by), lst in buckets.items():
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for m in buckets.get((k, bx + dx, by + dy), []):
                        for n in lst:
                            if n < m and abs(n[1] - m[1]) <= 3 and abs(n[2] - m[2]) <= 3 and not any(e[0] == m for e in self.adj[n]):
                                self.edge(n, m, 0.0, 0.0)
        self.nodes_by_layer = {}
        for n in self.adj:
            self.nodes_by_layer.setdefault(n[0], []).append(n)
        # holes: zero length, 1 milliohm per layer step, between the nodes nearest the hole on each layer
        for d in b.drills:
            if not d['plated'] or d['span'] is None:
                continue
            a_, c_ = d['span']
            for (hx, hy, dia) in d['holes']:
                prev = None
                for k in range(a_ - 1, c_):
                    best = None
                    for n in self.nodes_by_layer.get(k, []):
                        dd = math.hypot(n[1] / 1000.0 - hx, n[2] / 1000.0 - hy)
                        if dd <= 0.06 and (best is None or dd < best[0]):
                            best = (dd, n)
                    if best:
                        if prev is not None:
                            self.edge(prev[1], best[1], 0.0, VIA_R * (k - prev[0]))
                        prev = (k, best[1])

    def key(self, k, x, y):
        return (k, int(round(x * 1000)), int(round(y * 1000)))

    def edge(self, a, c, ln, r):
        self.adj.setdefault(a, []).append((c, ln, r)); self.adj.setdefault(c, []).append((a, ln, r))

    def nearest(self, x, y, layers=None):
        best = None
        for n in self.adj:
            if layers is not None and n[0] not in layers:
                continue
            dd = math.hypot(n[1] / 1000.0 - x, n[2] / 1000.0 - y)
            if best is None or dd < best[0]:
                best = (dd, n)
        return best

    def shortest(self, srcs, snks, by='len'):
        """Dijkstra from the set of source nodes; returns (cost, length, resistance, path nodes) to the best sink"""
        snks = set(snks)
        dist = {}
        pq = []
        for s in srcs:
            dist[s] = (0.0, 0.0, 0.0, None); heapq.heappush(pq, (0.0, s))
        prev = {}
        while pq:
            d, n = heapq.heappop(pq)
            if n in snks:
                path = [n]
                while path[-1] in prev:
                    path.append(prev[path[-1]])
                return d, dist[n][1], dist[n][2], path[::-1]
            if d > dist[n][0]:
                continue
            for (m, ln, r) in self.adj.get(n, []):
                c = ln if by == 'len' else r
                nd = d + c
                if m not in dist or nd < dist[m][0]:
                    dist[m] = (nd, dist[n][1] + ln, dist[n][2] + r, n); prev[m] = n
                    heapq.heappush(pq, (nd, m))
        return None


# ------------------------------------------------------------ formulas
def z_microstrip_hj(w, h, t, er):
    """Hammerstad and Jensen (1980) microstrip impedance with Wheeler's (1977) strip-thickness width correction; mm.
    Returns (Z0 ohm, eeff)."""
    if t > 0:
        dw = t / math.pi * math.log(1 + 4 * math.e / (t / h * (1 / math.tanh(math.sqrt(6.517 * w / h))) ** 2))
        dwr = 0.5 * (1 + 1 / math.cosh(math.sqrt(er - 1))) * dw
    else:
        dwr = 0.0
    u = (w + dwr) / h
    a = 1 + 1 / 49 * math.log((u ** 4 + (u / 52) ** 2) / (u ** 4 + 0.432)) + 1 / 18.7 * math.log(1 + (u / 18.1) ** 3)
    bq = 0.564 * ((er - 0.9) / (er + 3)) ** 0.053
    ee = (er + 1) / 2 + (er - 1) / 2 * (1 + 10 / u) ** (-a * bq)
    f = 6 + (2 * math.pi - 6) * math.exp(-((30.666 / u) ** 0.7528))
    z01 = 376.730 / (2 * math.pi) * math.log(f / u + math.sqrt(1 + (2 / u) ** 2))
    return z01 / math.sqrt(ee), ee


def zdiff_ipc2141(z0, s, h):
    return 2 * z0 * (1 - 0.48 * math.exp(-0.96 * s / h))
