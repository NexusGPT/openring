"""rb_lib.py: Gerber / Excellon reader, rasteriser and connectivity extractor (pure Python, numpy, scipy, Pillow).
Reads fabrication data only. The X2 net attribute (TO.N) is kept for a label-versus-geometry cross check and is never used
to join copper. Written for the board read-back, see ../board-readback.md section 0.1 (M1, M4)."""
import re, math, os, glob
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage


# ---------------------------------------------------------------- Gerber
class Layer:
    def __init__(self, name):
        self.name = name
        self.draws = []     # (x1,y1,x2,y2,w,netattr)
        self.flashes = []   # (x,y,polys,ref,pin,netattr,kind)  polys = list of polygons or ('c',x,y,d)
        self.regions = []   # (poly, ref, pin, netattr)


def _eval(expr, args):
    e = re.sub(r'\$(\d+)', lambda m: '(%r)' % args.get(int(m.group(1)), 0.0), expr)
    e = e.replace('x', '*').replace('X', '*')
    return float(eval(e, {'__builtins__': {}}, {}))


def _rot(pts, deg):
    if not deg:
        return pts
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return [(x * c - y * s, x * s + y * c) for x, y in pts]


def _circle_poly(cx, cy, d, n=24):
    r = d / 2.0
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def macro_polys(prims, args):
    """prims: list of primitive strings -> list of polygons (x,y lists) at the origin"""
    out = []
    for p in prims:
        f = [t for t in p.split(',')]
        code = int(f[0])
        if code == 1:
            exp, d, cx, cy = [_eval(t, args) for t in f[1:5]]
            rot = _eval(f[5], args) if len(f) > 5 else 0
            assert exp == 1, 'clear macro primitive'
            c = _rot([(cx, cy)], rot)[0]
            out.append(_circle_poly(c[0], c[1], d))
        elif code == 4:
            exp = _eval(f[1], args); n = int(_eval(f[2], args))
            assert exp == 1
            v = [_eval(t, args) for t in f[3:3 + 2 * (n + 1)]]
            rot = _eval(f[3 + 2 * (n + 1)], args) if len(f) > 3 + 2 * (n + 1) else 0
            pts = [(v[2 * i], v[2 * i + 1]) for i in range(n + 1)]
            out.append(_rot(pts, rot))
        elif code == 20:
            exp, w, x1, y1, x2, y2 = [_eval(t, args) for t in f[1:7]]
            rot = _eval(f[7], args) if len(f) > 7 else 0
            assert exp == 1
            dx, dy = x2 - x1, y2 - y1
            L = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / L * w / 2, dx / L * w / 2
            pts = [(x1 + nx, y1 + ny), (x2 + nx, y2 + ny), (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)]
            out.append(_rot(pts, rot))
        elif code == 21:
            exp, w, h, cx, cy = [_eval(t, args) for t in f[1:6]]
            rot = _eval(f[6], args) if len(f) > 6 else 0
            assert exp == 1
            pts = [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]
            out.append(_rot(pts, rot))
        else:
            raise ValueError('macro primitive %d not supported' % code)
    return out


def parse_gerber(path):
    L = Layer(os.path.basename(path))
    macros, aps = {}, {}
    cur_ap, x, y = None, 0.0, 0.0
    ref = pin = net = None
    region = None
    in_region = False
    fmt_div = 1e6
    txt = open(path).read()
    # split into statements: '%...%' blocks (may hold several '*' lines) and plain 'cmd*'
    pos = 0
    stmts = []
    for m in re.finditer(r'%([^%]*)%|([^%*]*)\*', txt):
        if m.group(1) is not None:
            stmts.append(('P', m.group(1)))
        else:
            s = m.group(2).strip()
            if s:
                stmts.append(('C', s))
    for kind, s in stmts:
        if kind == 'P':
            parts = [t for t in s.split('*') if t.strip()]
            head = parts[0]
            if head.startswith('FSLA'):
                m = re.match(r'FSLAX(\d)(\d)Y(\d)(\d)', head)
                fmt_div = 10 ** int(m.group(2))
            elif head.startswith('MO'):
                assert head == 'MOMM', head
            elif head.startswith('AM'):
                name = head[2:]
                prims = [t.strip() for t in parts[1:] if not t.strip().startswith('0 ') and not t.strip() == '0']
                macros[name] = prims
            elif head.startswith('ADD'):
                m = re.match(r'ADD(\d+)([A-Za-z0-9_]+),?(.*)', head)
                n, t, a = int(m.group(1)), m.group(2), m.group(3)
                vals = [float(v) for v in a.split('X')] if a else []
                aps[n] = (t, vals)
            elif head.startswith('TO.P'):
                f = head[5:].split(',')
                ref, pin = f[0], f[1]
            elif head.startswith('TO.N'):
                net = head[5:]
            elif head.startswith('TD'):
                ref = pin = net = None
            elif head.startswith('LP'):
                assert head == 'LPD', 'clear polarity not supported'
            continue
        # plain command
        if s.startswith('G04'):
            continue
        if s in ('G01',):
            continue
        if s.startswith(('G02', 'G03', 'G75', 'G74')) and not s.startswith('G75'):
            raise ValueError('arc not supported: ' + s)
        if s == 'G75':
            continue
        if s == 'G36':
            in_region = True
            region = []
            continue
        if s == 'G37':
            if region and len(region) >= 3:
                L.regions.append((region, ref, pin, net))
            in_region = False
            region = None
            continue
        if s.startswith('M02'):
            continue
        m = re.match(r'^D(\d+)$', s)
        if m and int(m.group(1)) >= 10:
            cur_ap = int(m.group(1))
            continue
        m = re.match(r'^(?:X(-?\d+))?(?:Y(-?\d+))?(?:D0([123]))?$', s)
        if not m:
            raise ValueError('unparsed: ' + s)
        nx = float(m.group(1)) / fmt_div if m.group(1) is not None else x
        ny = float(m.group(2)) / fmt_div if m.group(2) is not None else y
        d = m.group(3)
        if in_region:
            if d == '2':
                if region and len(region) >= 3:
                    L.regions.append((region, ref, pin, net))
                region = [(nx, ny)]
            elif d == '1':
                region.append((nx, ny))
            x, y = nx, ny
            continue
        if d == '1':
            t, v = aps[cur_ap]
            assert t == 'C', 'draw with non-circular aperture'
            L.draws.append((x, y, nx, ny, v[0], net))
        elif d == '3':
            t, v = aps[cur_ap]
            if t == 'C':
                polys = [('c', nx, ny, v[0])]
            elif t == 'R':
                w, h = v[0], v[1]
                polys = [[(nx - w / 2, ny - h / 2), (nx + w / 2, ny - h / 2), (nx + w / 2, ny + h / 2), (nx - w / 2, ny + h / 2)]]
            elif t == 'O':
                w, h = v[0], v[1]
                polys = []
                if w >= h:
                    r = h / 2
                    polys.append([(nx - w / 2 + r, ny - r), (nx + w / 2 - r, ny - r), (nx + w / 2 - r, ny + r), (nx - w / 2 + r, ny + r)])
                    polys.append(('c', nx - w / 2 + r, ny, h)); polys.append(('c', nx + w / 2 - r, ny, h))
                else:
                    r = w / 2
                    polys.append([(nx - r, ny - h / 2 + r), (nx + r, ny - h / 2 + r), (nx + r, ny + h / 2 - r), (nx - r, ny + h / 2 - r)])
                    polys.append(('c', nx, ny - h / 2 + r, w)); polys.append(('c', nx, ny + h / 2 - r, w))
            else:
                prims = macros[t]
                args = {i + 1: vv for i, vv in enumerate(v)}
                polys = []
                for pg in macro_polys(prims, args):
                    polys.append([(nx + a, ny + b) for a, b in pg])
            L.flashes.append((nx, ny, polys, ref, pin, net, t))
        x, y = nx, ny
    return L


# ---------------------------------------------------------------- Excellon
def parse_drill(path):
    """returns dict(span=(a,b) or None for NPTH, plated, holes=[(x,y)], tools)"""
    txt = open(path).read().splitlines()
    func = None
    for ln in txt:
        m = re.search(r'TF\.FileFunction,(.*)', ln)
        if m:
            func = m.group(1).strip()
    tools, cur, holes = {}, None, []
    body = False
    for ln in txt:
        ln = ln.strip()
        if ln == '%':
            body = True
            continue
        if ln.startswith(';'):
            continue
        m = re.match(r'^T(\d+)C([\d.]+)', ln)
        if m:
            tools[int(m.group(1))] = float(m.group(2))
            continue
        m = re.match(r'^T(\d+)$', ln)
        if m:
            cur = int(m.group(1))
            continue
        m = re.match(r'^X(-?[\d.]+)Y(-?[\d.]+)(?:G85X(-?[\d.]+)Y(-?[\d.]+))?$', ln)
        if m and body:
            holes.append((float(m.group(1)), float(m.group(2)), tools.get(cur, 0)))
            if m.group(3):
                holes.append((float(m.group(3)), float(m.group(4)), tools.get(cur, 0)))
    span, plated = None, False
    if func:
        f = func.split(',')
        if f[0] in ('Plated', 'MixedPlating'):
            plated = True
            span = (int(f[1]), int(f[2]))
        elif f[0] in ('NonPlated',):
            span = None
    return dict(func=func, span=span, plated=plated, holes=holes, path=path)


# ---------------------------------------------------------------- Board
def _to_px(x, y, x0, y1, res):
    return (x - x0) / res - 0.5, (y1 - y) / res - 0.5


class Board:
    """layers: list of (name, path) in copper order top to bottom; drills: list of paths"""

    def __init__(self, name, layer_paths, drill_paths, res=0.005, margin=0.3):
        self.name, self.res = name, res
        self.layers = [parse_gerber(p) for _, p in layer_paths]
        self.lnames = [n for n, _ in layer_paths]
        self.drills = [parse_drill(p) for p in drill_paths]
        xs, ys = [], []
        for L in self.layers:
            for (a, b, c, d, w, _) in L.draws:
                xs += [a - w / 2, c + w / 2]; ys += [b - w / 2, d + w / 2]
            for f in L.flashes:
                for pg in f[2]:
                    if pg and pg[0] == 'c':
                        xs += [pg[1] - pg[3] / 2, pg[1] + pg[3] / 2]; ys += [pg[2] - pg[3] / 2, pg[2] + pg[3] / 2]
                    else:
                        xs += [p[0] for p in pg]; ys += [p[1] for p in pg]
            for (rg, *_r) in L.regions:
                xs += [p[0] for p in rg]; ys += [p[1] for p in rg]
        self.x0, self.x1 = min(xs) - margin, max(xs) + margin
        self.y0, self.y1 = min(ys) - margin, max(ys) + margin
        self.W = int(math.ceil((self.x1 - self.x0) / res)); self.H = int(math.ceil((self.y1 - self.y0) / res))
        self.masks = [self.raster(L) for L in self.layers]

    def px(self, x, y):
        return (x - self.x0) / self.res, (self.y1 - y) / self.res   # continuous pixel coords (pixel i covers [i,i+1))

    def ij(self, x, y):
        u, v = self.px(x, y)
        return int(math.floor(v)), int(math.floor(u))   # row, col

    def xy(self, i, j):
        return self.x0 + (j + 0.5) * self.res, self.y1 - (i + 0.5) * self.res

    def _dpoly(self, dr, pts):
        dr.polygon([(self.px(x, y)[0] - 0.5, self.px(x, y)[1] - 0.5) for x, y in pts], fill=1)

    def _dcirc(self, dr, cx, cy, d):
        u, v = self.px(cx, cy)
        r = d / 2.0 / self.res
        dr.ellipse([u - r - 0.5, v - r - 0.5, u + r - 0.5, v + r - 0.5], fill=1)

    def _bbox_idx(self, xmin, xmax, ymin, ymax):
        j0 = max(0, int(math.floor((xmin - self.x0) / self.res - 0.5)) - 1); j1 = min(self.W - 1, int(math.ceil((xmax - self.x0) / self.res - 0.5)) + 1)
        i0 = max(0, int(math.floor((self.y1 - ymax) / self.res - 0.5)) - 1); i1 = min(self.H - 1, int(math.ceil((self.y1 - ymin) / self.res - 0.5)) + 1)
        return i0, i1, j0, j1

    def _centres(self, i0, i1, j0, j1):
        xs = self.x0 + (np.arange(j0, j1 + 1) + 0.5) * self.res
        ys = self.y1 - (np.arange(i0, i1 + 1) + 0.5) * self.res
        return np.meshgrid(xs, ys)

    def _poly_exact(self, mask, pts):
        """set every pixel whose centre lies inside the polygon (no outline pixels)"""
        from matplotlib.path import Path
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        i0, i1, j0, j1 = self._bbox_idx(min(xs), max(xs), min(ys), max(ys))
        if i1 < i0 or j1 < j0:
            return
        X, Y = self._centres(i0, i1, j0, j1)
        inside = Path(np.asarray(pts)).contains_points(np.column_stack([X.ravel(), Y.ravel()])).reshape(X.shape)
        mask[i0:i1 + 1, j0:j1 + 1] |= inside

    def _circ_exact(self, mask, cx, cy, d):
        r = d / 2.0
        i0, i1, j0, j1 = self._bbox_idx(cx - r, cx + r, cy - r, cy + r)
        if i1 < i0 or j1 < j0:
            return
        X, Y = self._centres(i0, i1, j0, j1)
        mask[i0:i1 + 1, j0:j1 + 1] |= ((X - cx) ** 2 + (Y - cy) ** 2) <= r * r

    def raster(self, L):
        mask = np.zeros((self.H, self.W), dtype=bool)
        for (a, b, c, d, w, _) in L.draws:
            dx, dy = c - a, d - b
            ln = math.hypot(dx, dy)
            if ln > 0:
                nx, ny = -dy / ln * w / 2, dx / ln * w / 2
                self._poly_exact(mask, [(a + nx, b + ny), (c + nx, d + ny), (c - nx, d - ny), (a - nx, b - ny)])
            self._circ_exact(mask, a, b, w); self._circ_exact(mask, c, d, w)
        for f in L.flashes:
            for pg in f[2]:
                if pg and pg[0] == 'c':
                    self._circ_exact(mask, pg[1], pg[2], pg[3])
                else:
                    self._poly_exact(mask, pg)
        # regions (zones): PIL scan fill, even-odd inside one region, regions OR-ed (outline pixels included, so plane edges
        # may be one pixel wider than exact)
        im = Image.new('L', (self.W, self.H), 0)
        dr = ImageDraw.Draw(im)
        for (rg, *_r) in L.regions:
            self._dpoly(dr, rg)
        return mask | np.asarray(im, dtype=bool)

    # ---- connectivity
    def connectivity(self, barrel=True):
        """returns dict: labels per layer, group id per (layer,label), holes info"""
        labs, nlab = [], []
        for m in self.masks:
            lab, n = ndimage.label(m)   # 4-connectivity
            labs.append(lab); nlab.append(n)
        off = np.concatenate([[0], np.cumsum(nlab)])
        parent = list(range(int(off[-1]) + 1))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        def union(a, b):
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra
        stats = dict(holes=0, via_nolayercopper=0, intermediate_nocopper=0, join_ops=0)
        N = len(self.masks)
        for dr_ in self.drills:
            if not dr_['plated'] or dr_['span'] is None:
                continue
            a, b = dr_['span']
            for (hx, hy, _t) in dr_['holes']:
                i, j = self.ij(hx, hy)
                stats['holes'] += 1
                present = []
                for k in range(a - 1, b):
                    if 0 <= i < self.H and 0 <= j < self.W and labs[k][i, j] > 0:
                        present.append(k)
                if (a - 1) not in present or (b - 1) not in present:
                    stats['via_nolayercopper'] += 1
                chain_ok = all(k in present for k in range(a - 1, b))
                if not chain_ok:
                    stats['intermediate_nocopper'] += 1
                if barrel:
                    ks = present
                    for q in range(1, len(ks)):
                        union(int(off[ks[0]] + labs[ks[0]][i, j]), int(off[ks[q]] + labs[ks[q]][i, j])); stats['join_ops'] += 1
                else:   # stack of microvias: only adjacent layers that both have copper
                    for k in range(a - 1, b - 1):
                        if k in present and (k + 1) in present:
                            union(int(off[k] + labs[k][i, j]), int(off[k + 1] + labs[k + 1][i, j])); stats['join_ops'] += 1
        self.labs, self.off, self._find = labs, off, find
        # final group of every (layer,label)
        self.stats = stats
        return stats

    def group_at(self, k, i, j):
        l = self.labs[k][i, j]
        if l == 0:
            return None
        return self._find(int(self.off[k] + l))

    def group_map(self, k):
        """array (labels+1) -> group id for layer k"""
        n = int(self.off[k + 1] - self.off[k])
        return np.array([0] + [self._find(int(self.off[k] + l)) for l in range(1, n + 1)], dtype=np.int64)

    def pads(self):
        """list of dict(ref,pin,layer,x,y,group,netattr) for every flash and region that carries TO.P"""
        out = []
        for k, L in enumerate(self.layers):
            for (x, y, polys, ref, pin, net, t) in L.flashes:
                if ref is None:
                    continue
                i, j = self.ij(x, y)
                out.append(dict(ref=ref, pin=pin, layer=k, x=x, y=y, group=self.group_at(k, i, j), netattr=net))
            for (rg, ref, pin, net) in L.regions:
                if ref is None:
                    continue
                # a point inside: centroid of the vertices, fallback to first vertex
                cx = sum(p[0] for p in rg) / len(rg); cy = sum(p[1] for p in rg) / len(rg)
                i, j = self.ij(cx, cy)
                g = self.group_at(k, i, j) if 0 <= i < self.H and 0 <= j < self.W else None
                out.append(dict(ref=ref, pin=pin, layer=k, x=cx, y=cy, group=g, netattr=net))
        return out


def find_board_files(gerber_dir, prefix, drill_dir=None):
    """ring/case style names"""
    order = ['F_Cu', 'In1_Cu', 'In2_Cu', 'B_Cu']
    lp = []
    for n in order:
        p = os.path.join(gerber_dir, '%s-%s.gbr' % (prefix, n))
        if os.path.exists(p):
            lp.append((n, p))
    return lp


def read_netlist(path):
    import csv
    rows = list(csv.DictReader(open(path)))
    return [(r['net'], r['reference'], r['pin_number']) for r in rows]


def compare(board, netlist_rows, refs_scope=None):
    """expected grouping vs extracted components. netlist_rows: [(net, ref, pin)]. refs_scope: set of refs the
    board may carry (None = all). Returns dict of counts and finding lists (M4)."""
    pads = board.pads()
    refs_present = set(p['ref'] for p in pads)
    exp = {}
    for net, ref, pin in netlist_rows:
        if refs_scope is not None and ref not in refs_scope:
            continue
        exp[(ref, pin)] = net
    # pads of this board only (reference present on the board's fab data)
    exp_here = {k: v for k, v in exp.items() if k[0] in refs_present}
    by_pad = {}
    for p in pads:
        by_pad.setdefault((p['ref'], p['pin']), []).append(p)
    missing = [k for k in exp_here if k not in by_pad]
    absent_refs = sorted(set(k[0] for k in exp if k[0] not in refs_present))
    extra = [k for k in by_pad if k not in exp]   # pads in copper that the netlist does not list
    # groups per net
    net_groups, grp_nets = {}, {}
    unnetted = []
    for k, ps in by_pad.items():
        if k not in exp_here:
            continue
        net = exp_here[k]
        for p in ps:
            if p['group'] is None:
                continue
            if net == '' or net is None:
                unnetted.append((k, p['group']))
                continue
            net_groups.setdefault(net, set()).add(p['group'])
            grp_nets.setdefault(p['group'], set()).add(net)
    opens = {n: len(g) - 1 for n, g in net_groups.items() if len(g) > 1}
    shorts = {g: sorted(ns) for g, ns in grp_nets.items() if len(ns) > 1}
    nc_touch = [(k, sorted(grp_nets[g])) for k, g in unnetted if g in grp_nets]
    res = dict(nets=len(net_groups), pads=len(exp_here), pads_found=len(exp_here) - len(missing),
               shorts=sum(len(ns) - 1 for ns in shorts.values()) + len(nc_touch), opens=sum(opens.values()),
               missing=len(missing), absent_refs=absent_refs, open_nets=opens, short_groups=list(shorts.values()),
               nc_touch=nc_touch, missing_pads=missing, unlisted_pads=extra)
    res['net_groups'] = net_groups
    res['grp_nets'] = grp_nets
    return res
