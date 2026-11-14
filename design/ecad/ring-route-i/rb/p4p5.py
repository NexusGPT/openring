"""P4 (antenna feed, USB pair) and P5 (crystal lines) on the ring board, from the Gerber/drill read-back."""
import sys, os, math, json, collections
import numpy as np
from scipy import ndimage
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p3_lib as L, rb_res as S, rb_lib as R
OUT = os.environ['RBOUT']  # ring-lines copy
def log(s):
    print(s); sys.stdout.flush()
b, c, rows = L.load('ring')
rs = [S.RHO / 0.018] * 4
H, T, ER = 0.065, 0.018, 4.1      # fab/stackup.txt (L1 to L2 prepreg 0.065, copper 0.018), plan section d header (er 4.1; ring.kicad_pcb stackup block also 4.1)
gm = [b.group_map(k) for k in range(4)]
grp_nets = c['grp_nets']
def grp_of_net(n): return L.net_group(c, n)
def gname(g):
    ns = grp_nets.get(g)
    return '+'.join(sorted(ns)) if ns else '(no netlist pad in that copper)'
def draws_of(groups):
    """draw list per layer whose midpoint copper group is in groups"""
    out = {k: [] for k in range(4)}
    for k, Ly in enumerate(b.layers):
        for d in Ly.draws:
            i, j = b.ij((d[0] + d[2]) / 2, (d[1] + d[3]) / 2); l = b.labs[k][i, j]
            if l and int(gm[k][l]) in groups:
                out[k].append(d)
    return out
def mask_of(drs):
    m = np.zeros((b.H, b.W), dtype=bool)
    for (x1, y1, x2, y2, w, _) in drs:
        ln = math.hypot(x2 - x1, y2 - y1)
        if ln > 0:
            nx, ny = -(y2 - y1) / ln * w / 2, (x2 - x1) / ln * w / 2
            b._poly_exact(m, [(x1 + nx, y1 + ny), (x2 + nx, y2 + ny), (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)])
        b._circ_exact(m, x1, y1, w); b._circ_exact(m, x2, y2, w)
    return m
def other_mask(k, own_groups):
    g = gm[k][b.labs[k]]
    own = np.isin(g, list(own_groups))
    return b.masks[k] & ~own
def clear(mline, k, own_groups, where_excl=None):
    """min edge-to-edge distance from the line mask to other-net copper on layer k; returns (mm, (x,y), other group)"""
    om = other_mask(k, own_groups)
    dist, (ii, jj) = ndimage.distance_transform_edt(~om, return_indices=True)
    d = np.where(mline, dist, np.inf)
    if where_excl is not None:
        d = np.where(where_excl, d, np.inf)
    if not np.isfinite(d.min()):
        return None
    p = np.unravel_index(np.argmin(d), d.shape)
    oi, oj = ii[p], jj[p]
    og = int(gm[k][b.labs[k][oi, oj]])
    x, y = b.xy(*p)
    return d.min() * b.res, (round(x, 3), round(y, 3)), gname(og)
def widths(drs):
    w = collections.Counter()
    for k in drs:
        for d in drs[k]:
            w[round(d[4], 4)] += math.hypot(d[2] - d[0], d[3] - d[1])
    return w
def gdraph(groups):
    def ok(k, x, y):
        i, j = b.ij(x, y); l = b.labs[k][i, j]
        return bool(l) and int(gm[k][l]) in groups
    return S.DGraph(b, ok, rs)
def plen(G, a, z):
    def nodes(p):
        ns = []
        for k, Ly in enumerate(b.layers):
            for f in Ly.flashes:
                if f[3] == p[0] and f[4] == p[1]:
                    kk = G.key(k, f[0], f[1])
                    if kk in G.adj: ns.append(kk)
        return ns
    r = G.shortest(nodes(a), nodes(z), by='len')
    return (r[1], r[3]) if r else (None, None)
res = {}
# ---------------- P4.1 to P4.3 antenna feed
ANT = ['ANT1_NODE', 'ANT2_NODE', 'ANT3_NODE', 'RF_FEED']
ag = set(grp_of_net(n) for n in ANT)
ad = draws_of(ag)
w = widths(ad)
log('P4 antenna feed nets %s: draws per layer %s, total drawn length by width (mm): %s' % (ANT, {k + 1: len(v) for k, v in ad.items()}, {k: round(v, 3) for k, v in w.items()}))
wmode = max(w, key=w.get)
z, ee = S.z_microstrip_hj(wmode, H, T, ER)
zs = {ww: S.z_microstrip_hj(ww, H, T, ER)[0] for ww in w}
log('P4.1 antenna Z0 at modal width %.3f mm (h %.3f, t %.3f, er %.1f): %.2f ohm (eeff %.3f); min width %.3f -> %.2f ohm, max width %.3f -> %.2f ohm; limit 45 to 55 ohm' % (wmode, H, T, ER, z, ee, min(w), zs[min(w)], max(w), zs[max(w)]))
for er2 in (3.9, 4.5):
    log('P4.1 sensitivity er %.1f: %.2f ohm' % (er2, S.z_microstrip_hj(wmode, H, T, er2)[0]))
res['P4_1'] = dict(widths_mm=w, modal=wmode, Z0=z, eeff=ee, Z_min_width=zs[min(w)], Z_max_width=zs[max(w)], layers_with_draws={k + 1: len(v) for k, v in ad.items()})
m1 = mask_of(ad[0])
u1c = [f for f in b.layers[0].flashes if f[3] == 'U1' and f[4] == 'C1'][0]
xx, yy = b.xy(*np.indices(m1.shape)) if False else (None, None)
cl = clear(m1, 0, ag)
log('P4.2 antenna L1 draws: nearest other-net L1 copper %.4f mm at %s (net %s); limit >= 0.200 mm' % cl[0:1] + ('' if False else '') if False else 'P4.2 antenna L1 draws: nearest other-net L1 copper %.4f mm at %s (copper of %s); limit >= 0.200 mm' % (cl[0], cl[1], cl[2]))
# excluding the first 1.0 mm from U1 ball C1
ii, jj = np.indices(m1.shape)
X = b.x0 + (jj + 0.5) * b.res; Y = b.y1 - (ii + 0.5) * b.res
far = np.hypot(X - u1c[0], Y - u1c[1]) > 1.0
cl2 = clear(m1, 0, ag, far)
log('P4.2b same, excluding pixels within 1.0 mm of U1 ball C1 (%.3f,%.3f): %.4f mm at %s (copper of %s)' % (u1c[0], u1c[1], cl2[0], cl2[1], cl2[2]))
res['P4_2'] = dict(min_clear_mm=cl[0], at=cl[1], other=cl[2], min_clear_excl_1mm=cl2[0], at2=cl2[1], other2=cl2[2])
# reference: L2 GND under the line
gG = grp_of_net('GND')
g2 = gm[1][b.labs[1]]
gnd2 = b.masks[1] & (g2 == gG)
anyl2 = b.masks[1]
cov = (gnd2 & m1).sum() / m1.sum()
oth = (anyl2 & ~gnd2 & m1).sum()
log('P4.3 antenna reference: L2 GND under the line draws covers %.4f percent of the line pixels (%d of %d); L2 copper of other nets under the line: %d pixels' % (cov * 100, (gnd2 & m1).sum(), m1.sum(), oth))
unc = m1 & ~gnd2
lab_u, nu = ndimage.label(unc)
for q in range(1, nu + 1):
    ys, xs = np.nonzero(lab_u == q)
    x0_, y0_ = b.xy(ys.min(), xs.min()); x1_, y1_ = b.xy(ys.max(), xs.max())
    log('P4.3 uncovered cluster %d: %d pixels (%.4f mm2), x %.3f..%.3f y %.3f..%.3f' % (q, len(ys), len(ys) * b.res ** 2, min(x0_, x1_), max(x0_, x1_), min(y0_, y1_), max(y0_, y1_)))
band = ndimage.distance_transform_edt(~m1) * b.res <= 0.5
bandc = (gnd2 & band).sum() / band.sum()
log('P4.3b +-0.50 mm band: L2 GND covers %.2f percent; L2 other-net copper pixels in the band %d' % (bandc * 100, (anyl2 & ~gnd2 & band).sum()))
res['P4_3'] = dict(cov_pct=cov * 100, uncovered_px=int(m1.sum() - (gnd2 & m1).sum()), other_net_px=int(oth), band_cov_pct=bandc * 100)
# nearest other-net copper per layer
per = {}
for k in range(4):
    r = clear(m1, k, ag)
    per[k + 1] = r
    log('P4 nearest other-net copper to the antenna line (planar distance from the line footprint) on L%d: %.4f mm at %s (copper of %s)' % (k + 1, r[0], r[1], r[2]))
res['P4_per_layer'] = per
# lengths by leg
G = gdraph(ag)
legs = [('ANT1_NODE', ('U1', 'C1'), ('L2', '1')), ('ANT2_NODE', ('L2', '2'), ('L3', '1')), ('ANT3_NODE', ('L3', '2'), ('L4', '1')), ('RF_FEED', ('L4', '2'), ('ANT1', '1'))]
tot = 0; ok = True
legl = {}
for n, a, z_ in legs:
    gg = gdraph({grp_of_net(n)})
    ln, path = plen(gg, a, z_)
    tl = sum(math.hypot(d[2] - d[0], d[3] - d[1]) for d in draws_of({grp_of_net(n)})[0] + draws_of({grp_of_net(n)})[1] + draws_of({grp_of_net(n)})[2] + draws_of({grp_of_net(n)})[3])
    log('P4 antenna leg %s %s -> %s: shortest drawn path %s mm; all drawn copper of the net %.3f mm' % (n, a, z_, ('%.3f' % ln) if ln is not None else 'n/a', tl))
    legl[n] = (ln, tl)
    if ln is None: ok = False
    else: tot += ln
log('P4 antenna line, sum of legs (shortest paths): %.3f mm (plan R2.0 point 3: 16.4 mm; no tolerance written: reported)%s' % (tot, '' if ok else ' (a leg missing)'))
res['P4_len'] = dict(legs=legl, sum=tot)
# ---------------- USB pair
dp, dn = grp_of_net('USB_DP'), grp_of_net('USB_DN')
ud = {'DP': draws_of({dp}), 'DN': draws_of({dn})}
for nm in ud:
    log('P4 USB_%s draws per layer %s; width by length %s' % (nm, {k + 1: len(v) for k, v in ud[nm].items()}, {k: round(v, 3) for k, v in widths(ud[nm]).items()}))
mdp = mask_of(sum(ud['DP'].values(), [])); mdn = mask_of(sum(ud['DN'].values(), []))
wdp = widths(ud['DP']); wdn = widths(ud['DN'])
wm = max(wdp, key=wdp.get)
z0, _ = S.z_microstrip_hj(wm, H, T, ER)
# gap between the legs: EDT from DN draw mask evaluated on DP draw pixels within 0.3 mm of DN
dist_dn = ndimage.distance_transform_edt(~mdn) * b.res
vals = dist_dn[mdp & (dist_dn < 0.3)]
gaps = np.round(vals / 0.005) * 0.005
cnt = collections.Counter(gaps.tolist())
gmode = max(cnt, key=cnt.get)
log('P4.4 USB pair: modal width %.3f mm; gap DP to DN: min %.4f mm, median %.4f mm, modal %.3f mm over %d pixels within 0.3 mm; Z0 each line %.2f ohm; Zdiff at modal gap %.2f ohm, at min gap %.2f ohm; limit 81 to 99 ohm' % (wm, vals.min(), float(np.median(vals)), gmode, len(vals), z0, S.zdiff_ipc2141(z0, gmode, H), S.zdiff_ipc2141(z0, float(vals.min()), H)))
res['P4_4'] = dict(modal_w=wm, gap_min=float(vals.min()), gap_median=float(np.median(vals)), gap_mode=gmode, Z0=z0, Zdiff_mode=S.zdiff_ipc2141(z0, gmode, H), Zdiff_min=S.zdiff_ipc2141(z0, float(vals.min()), H))
cl_dp = clear(mdp | mdn, 0, {dp, dn})
mu = mdp | mdn
covu = (gnd2 & mu).sum() / mu.sum()
log('P4.3u USB pair reference: L2 GND under the pair draws covers %.4f percent of the pair pixels (%d of %d); L2 other-net copper under them: %d px' % (covu * 100, (gnd2 & mu).sum(), mu.sum(), (anyl2 & ~gnd2 & mu).sum()))
res['P4_3u'] = dict(cov_pct=covu * 100, uncovered_px=int(mu.sum() - (gnd2 & mu).sum()), other_px=int((anyl2 & ~gnd2 & mu).sum()))
log('P4 USB pair (both legs) nearest copper of any other net on L1: %.4f mm at %s (copper of %s) (plan: 0.200 mm class gap)' % (cl_dp[0], cl_dp[1], cl_dp[2]))
res['P4_usb_other'] = cl_dp
Gp, Gn = gdraph({dp}), gdraph({dn})
l_dp, _ = plen(Gp, ('U1', 'H7'), ('J_BAND_B', '6')); l_dn, _ = plen(Gn, ('U1', 'H6'), ('J_BAND_B', '5'))
t_dp = sum(math.hypot(d[2] - d[0], d[3] - d[1]) for k in ud['DP'] for d in ud['DP'][k]); t_dn = sum(math.hypot(d[2] - d[0], d[3] - d[1]) for k in ud['DN'] for d in ud['DN'][k])
log('P4.5 USB legs: D+ shortest drawn path U1 H7 -> J_BAND_B 6 = %s mm, D- U1 H6 -> J_BAND_B 5 = %s mm, mismatch %s mm; total drawn lengths D+ %.3f D- %.3f mismatch %.3f; limit mismatch <= 0.10 mm' % (
    ('%.3f' % l_dp) if l_dp else 'n/a', ('%.3f' % l_dn) if l_dn else 'n/a', ('%.3f' % abs(l_dp - l_dn)) if l_dp and l_dn else 'n/a', t_dp, t_dn, abs(t_dp - t_dn)))
res['P4_5'] = dict(l_dp=l_dp, l_dn=l_dn, mismatch=(abs(l_dp - l_dn) if l_dp and l_dn else None), t_dp=t_dp, t_dn=t_dn)
# vias in the pair: holes whose centre pixel lies in the net group on 2 or more layers
nv = 0
for d in b.drills:
    if d['plated'] and d['span']:
        for (hx, hy, dia) in d['holes']:
            i, j = b.ij(hx, hy)
            for gx in (dp, dn):
                if sum(1 for k in range(d['span'][0] - 1, d['span'][1]) if b.labs[k][i, j] and int(gm[k][b.labs[k][i, j]]) == gx) >= 2: nv += 1
log('P4 USB pair holes in net copper: %d' % nv)
# ---------------- P5 crystals
P5 = [('XL1', ('U1', 'B6'), ('X2', '1'), 9.0), ('XL2', ('U1', 'B7'), ('X2', '2'), 9.0), ('XC1', ('U1', 'A2'), ('X1', '1'), 6.0), ('XC2', ('U1', 'A1'), ('X1', '3'), 6.0)]
res['P5'] = {}
lens = {}
for n, a, z_, lim in P5:
    g = grp_of_net(n); dd = draws_of({g}); G1 = gdraph({g})
    ln, path = plen(G1, a, z_)
    tl = sum(math.hypot(d[2] - d[0], d[3] - d[1]) for k in dd for d in dd[k])
    lens[n] = ln if ln is not None else tl
    log('P5 %s %s -> %s: shortest drawn path %s mm, all drawn copper %.3f mm, limit <= %.1f mm; layers with draws %s; widths %s' % (n, a, z_, ('%.3f' % ln) if ln is not None else 'n/a', tl, lim, {k + 1: len(v) for k, v in dd.items() if v}, {k: round(v, 3) for k, v in widths(dd).items()}))
    cls = {}
    for k in range(4):
        if dd[k]:
            mk = mask_of(dd[k]); r = clear(mk, k, {g}); cls[k + 1] = r
            log('P5 %s on L%d: nearest other-net copper %.4f mm at %s (copper of %s); limit >= 0.20 mm' % (n, k + 1, r[0], r[1], r[2]))
    res['P5'][n] = dict(path=ln, total=tl, limit=lim, clear=cls)
log('P5 XC match: |XC1 - XC2| = %.3f mm (limit <= 0.5 mm)' % abs(lens['XC1'] - lens['XC2']))
# ---------------- ring-lines additions (not part of the read-back's frozen lines; stated as additions)
# A1: P4.3 judged outside the antenna copper-free zone (lead's ruling): plan R2.0 point 2, X -13.60 to -8.75, Y 3.10 to 6.30 less the notch
# X -9.20 to -8.75, Y 3.10 to 3.30; board model = Gerber - 100 in X and Gerber y = -(model Y + 100)
MX = X - 100.0; MY = -Y - 100.0
inzone = (MX >= -13.60) & (MX <= -8.75) & (MY >= 3.10) & (MY <= 6.30) & ~((MX >= -9.20) & (MY <= 3.30))
mo = m1 & ~inzone
log('A1 antenna reference outside the copper-free zone: L2 GND covers %.4f percent of the line pixels (%d of %d); line pixels inside the zone %d' % ((gnd2 & mo).sum() / mo.sum() * 100, (gnd2 & mo).sum(), mo.sum(), (m1 & inzone).sum()))
# A2: USB edge-to-edge gap sampled on the D+ draw centrelines every 0.02 mm (distance to D- copper minus half the D+ width), coupled points
# (gap < 0.25 mm) only; Zdiff at each sampled gap
dd_dn = ndimage.distance_transform_edt(~mdn) * b.res
gs = []
for k in ud['DP']:
    for (x1, y1, x2, y2, w_, _) in ud['DP'][k]:
        ln = math.hypot(x2 - x1, y2 - y1); n_ = max(1, int(ln / 0.02))
        for q in range(n_ + 1):
            px, py = x1 + (x2 - x1) * q / n_, y1 + (y2 - y1) * q / n_
            i_, j_ = b.ij(px, py); gs.append(dd_dn[i_, j_] - w_ / 2)
gs = np.array(gs); cpl = gs[gs < 0.25]
zz = [S.zdiff_ipc2141(z0, float(g_), H) for g_ in cpl]
log('A2 USB edge gap on D+ centreline: %d samples, %d coupled (gap < 0.25 mm); coupled gap min %.4f median %.4f max %.4f mm; Zdiff min %.2f max %.2f ohm; coupled samples outside 81..99 ohm: %d; uncoupled samples %d' % (len(gs), len(cpl), cpl.min(), float(np.median(cpl)), cpl.max(), min(zz), max(zz), sum(1 for z_ in zz if z_ < 81 or z_ > 99), len(gs) - len(cpl)))
res['A1'] = dict(cov_out_pct=(gnd2 & mo).sum() / mo.sum() * 100); res['A2'] = dict(n=len(gs), coupled=len(cpl), gmin=float(cpl.min()), gmax=float(cpl.max()), zmin=min(zz), zmax=max(zz))
json.dump(res, open(OUT, 'w'), indent=1, default=float)
log('P4P5_DONE')
