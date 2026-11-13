"""Search for the pebble's outline and profile (numpy only). Finds the smallest outer form whose skin keeps >= MARGIN mm
from every cut of the C4 layout (cavity, well, pocket, relief, notch), plan radius of curvature >= 12 mm, wall not
vertical (within 5 degrees) for more than 40 percent of the height. Output: look/explore_best.json and the log.
Run: nice -n 19 ../.venv/bin/python look/explore.py   (from design/case)"""
import json, math, os, sys
import numpy as np
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "c4_params.json")))
MARGIN = 1.15
LID_GAP, LID_T = 0.3, 4.0
HULL = np.array(P["hull_w"])


def levels(zp):
    cz0 = zp + 0.4
    p0 = cz0 + 8.5 + 0.3
    p1 = p0 + 1.0
    zf = round(p1 + 3.31 + 0.3 + 1.8 + 0.05, 1)
    zb = zf + 4.01
    bt = zb + 14.65
    zs = round(bt + 0.3, 2)
    return dict(cz0=cz0, p0=p0, p1=p1, zf=zf, zb=zb, bt=bt, zs=zs, zl=zs + LID_GAP, H=zs + LID_GAP + LID_T)


def cons_points(zp, L, xmin=-11.48):
    """points (x,y,z) that must stay MARGIN inside the skin"""
    pts = []
    xa, xb, yh = xmin + 1.5, 15.92, 20.35
    zlo, zhi = zp, L["zf"] - 1.8
    for x in np.linspace(xa, xb, 6):
        for y in (-yh, yh):
            for z in np.linspace(zlo, zhi, 4):
                pts.append((x, y, z))
    for y in np.linspace(-yh, yh, 9):
        for x in (xa, xb):
            for z in (zlo, zhi):
                pts.append((x, y, z))
    px0, px1, py = P["px0"], P["px1"], P["py1"]
    zlow = L["zb"] - 14.65 - 0.4
    for x in np.linspace(px0, px1, 6):
        for y in (-py, py):
            for z in (zlow, L["zb"] - 8.6, L["zb"], L["zs"]):
                pts.append((x, y, z))
    for y in np.linspace(-py, py, 5):
        for z in (zlow,):
            pts.append((px1, y, z))
            pts.append((px0, y, z))
    # notch (finger scoop): reduced to 2.0 mm each side of the pocket
    ny = py + 2.0
    for x in (px0 + 1.0, px1 - 1.0):
        for y in (-ny, ny):
            for z in (L["bt"] - 7.0, L["zs"]):
                pts.append((x, y, z))
    for (x, y) in HULL[::3]:
        for z in (L["zf"], 0.5 * (L["zf"] + L["zs"]), L["zs"]):
            pts.append((x, y, z))
    return np.array(pts)


def profile(z, zm, cl, pl, cu, pu):
    z = np.asarray(z, float)
    t = np.where(z < zm, (zm - z) / cl, (z - zm) / cu)
    p = np.where(z < zm, pl, pu)
    return np.clip(1 - np.clip(np.abs(t), 0, 1) ** p, 0, 1) ** (1.0 / p)


def plan(t, n, ax, b0, k, xc, axr=None):
    axr = ax if axr is None else axr
    c, s = np.cos(t), np.sin(t)
    cs = np.sign(c) * np.abs(c) ** (2.0 / n)
    sn = np.sign(s) * np.abs(s) ** (2.0 / n)
    return xc + np.where(cs < 0, ax, axr) * cs, b0 * (1 - k * cs) * sn, cs


def cloud(q, H, nt=240, nz=100):
    zm, cl, pl, cu, pu, n, ax, b0, k, xc, axr, lean = q
    zs = np.linspace(0, H, nz)
    sc = profile(zs, zm, cl, pl, cu, pu)
    t = np.linspace(0, 2 * np.pi, nt, endpoint=False)
    x0, y0, _ = plan(t, n, ax, b0, k, xc, axr)
    X = (xc + lean * zs / H)[:, None] + (x0 - xc)[None, :] * sc[:, None]
    Y = y0[None, :] * sc[:, None]
    Z = np.repeat(zs[:, None], nt, 1)
    return np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1), (x0, y0, zs, sc)


def min_radius(q):
    zm, cl, pl, cu, pu, n, ax, b0, k, xc, axr, lean = q
    t = np.linspace(0, 2 * np.pi, 2000, endpoint=False)
    x, y, _ = plan(t, n, ax, b0, k, xc, axr)
    dx, dy = np.gradient(x, t), np.gradient(y, t)
    ddx, ddy = np.gradient(dx, t), np.gradient(dy, t)
    kap = np.abs(dx * ddy - dy * ddx) / (dx * dx + dy * dy) ** 1.5
    return 1.0 / kap.max()


def vertical_fraction(q, H, deg=5.0):
    """largest, over all azimuths of the outline, share of the height where the wall is within deg of vertical"""
    pts, _ = cloud(q, H, nt=120, nz=200)
    P = pts.reshape(200, 120, 3)
    dz = P[1, 0, 2] - P[0, 0, 2]
    # skip the two ends: the dome ends are by construction not vertical
    d = np.hypot(np.diff(P[:, :, 0], axis=0), np.diff(P[:, :, 1], axis=0)) / dz
    return float(np.mean(d < math.tan(math.radians(deg)), axis=0).max())


def mouth_x(q, L):
    zm, cl, pl, cu, pu, n, ax, b0, k, xc, axr, lean = q
    zj = L["p1"] + 1.65
    s = float(profile(zj, zm, cl, pl, cu, pu))
    t = np.linspace(0, 2 * np.pi, 4000)
    xx, yy, _ = plan(t, n, ax, b0, k, xc, axr)
    sel = (np.abs(yy * s - 12.5) < 0.1) & (xx < xc)
    xcz = xc + lean * zj / (L['H'])
    return float((xcz + (xx[sel] - xc) * s).min()) if sel.any() else 99.0


def evaluate(v):
    zp, zm, pl, pu, n, ax, b0, k, xc, axr, lean = v
    L = levels(zp)
    H = L["H"]
    if not (6 < zm < H - 6):
        return 1e9, None
    q = (zm, zm, pl, H - zm, pu, n, ax, b0, k, xc, axr, lean)
    xj = mouth_x(q, L)
    xmin = -11.48
    pts, (x0, y0, zs, sc) = cloud(q, H)
    tree = cKDTree(pts)
    c = cons_points(zp, L, xmin)
    d, _ = tree.query(c)
    inside = np.ones(len(c), bool)
    for i, (x, y, z) in enumerate(c):
        s = float(profile(z, zm, zm, pl, H - zm, pu))
        if s <= 0:
            inside[i] = False
            continue
        xcz = xc + lean * z / H
        u = (x - xcz) / ((ax if x < xcz else axr) * s)
        bu = b0 * (1 - k * u) * s
        g = (abs(u) ** n + abs((y) / bu) ** n) ** (1 / n) if bu > 0 else 9
        inside[i] = g < 1
    dd = np.where(inside, d, -d)
    viol = max(0.0, MARGIN - dd.min())
    bx = pts[:, 0].max() - pts[:, 0].min()
    by = pts[:, 1].max() - pts[:, 1].min()
    rmin = min_radius(q)
    vf = vertical_fraction(q, H)
    pen = 4000 * viol + 400 * max(0, 12.5 - rmin) + 20000 * max(0, vf - 0.40)
    pen += 400 * max(0, -17.0 - xj)
    return bx * by + 40 * H + pen, dict(bx=bx, by=by, H=H, rmin=rmin, vf=vf, dmin=float(dd.min()), xj=float(xj), L=L)


def main():
    rng = np.random.default_rng(7)
    lo = np.array([1.5, 8, 2.4, 2.2, 2.0, 18, 18, -0.3, -4.0, 14, -6.0])
    hi = np.array([5.5, 30, 12.0, 5.0, 3.4, 36, 32, 0.35, 14.0, 36, 30.0])
    best = np.array([3.33, 8.0, 5.7, 3.3, 3.4, 30.4, 24.9, 0.03, 12.95, 28.0, 0.0])
    bv, _ = evaluate(best)
    print("start", bv)
    step = (hi - lo) * 0.05
    for it in range(9000):
        cand = np.clip(best + rng.normal(size=len(lo)) * step * (0.5 + 0.5 * (0.999 ** it)) * (rng.random(len(lo)) < 0.4), lo, hi)
        f, _ = evaluate(cand)
        if f < bv:
            best, bv = cand, f
    f, info = evaluate(best)
    names = ["zp", "zm", "pl", "pu", "n", "ax", "b0", "k", "xc", "axr", "lean"]
    out = dict(zip(names, map(float, best)))
    out.update({k: (v if k != "L" else {a: float(b) for a, b in v.items()}) for k, v in info.items()})
    out["objective"] = float(f)
    json.dump(out, open(os.path.join(HERE, "explore_best.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
