"""C5b: search the plan and the edge radii (numpy). Size first: bbox X <= 45.4, Y <= 45.9, H fixed 41.4; the skin keeps >= MARGIN from every cut
of the C4 layout; the seam lies in the straight wall; J1 keeps C4's room. Maximises plan radius and edge radii. Log: look/explore2.log"""
import json, math, os, sys
import numpy as np
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pebble as PB
import explore as E

MARGIN, H = 1.15, 41.4
NAMES = ["ZP", "N_EXP", "N_R", "XC", "AX", "AXR", "B0", "K", "EB", "VB", "ET", "VT", "CB", "CT"]
LO = np.array([1.5, 3.0, 2.2, 8.0, 20.0, 20.0, 21.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.3, 0.5])
HI = np.array([4.0, 7.0, 6.0, 13.0, 25.0, 25.0, 23.0, 0.06, 9.0, 8.0, 10.0, 6.0, 1.5, 2.0])


def setp(v):
    for k, x in zip(NAMES, v):
        if k != "ZP":
            PB.PEB[k] = float(x)
    PB.PEB["S"] = float(v[6]) * 0.99
    PB.PEB["H"] = H


def evaluate(v, detail=False):
    setp(v)
    zp = float(v[0])
    L = E.levels(zp)
    if L["zl"] + 0.3 > H - PB.PEB["CT"] - PB.PEB["VT"] - 0.0:
        pen_seam = 1000 * (L["zl"] + 0.5 - (H - PB.PEB["CT"] - PB.PEB["VT"]))
    else:
        pen_seam = 0.0
    pen_seam = 1000 * max(0.0, L["zl"] + 0.5 - (H - PB.PEB["CT"] - PB.PEB["VT"]))
    pts = PB.cloud(H, 200, 160)
    bx, by = np.ptp(pts[:, 0]), np.ptp(pts[:, 1])
    c = E.cons_points(zp, L, -11.48)
    d, _ = cKDTree(pts).query(c)
    rp = PB.rho_point_vec(c[:, 0], c[:, 1])
    rz = PB.rho_of_z(c[:, 2], H)
    ins = rp < rz
    dd = np.where(ins, d, -d)
    viol = max(0.0, MARGIN - dd.min())
    # J1: skin x over y 8..16.94 at the socket height
    zj = L["p1"] + 1.65
    xs = []
    for y in np.linspace(8.0, 16.94, 7):
        o = PB.outline_at(float(PB.rho_of_z(zj, H)), 1600)
        sel = (np.abs(o[1] - y) < 0.06) & (o[0] < PB.PEB["XC"])
        xs.append(o[0][sel].min() if sel.any() else 99.0)
    xj = max(xs)
    pen_j = 50 * max(0.0, xj + 10.55)
    pen_size = 100 * max(0.0, bx - 45.4) + 100 * max(0.0, by - 45.9)
    rmin = PB.min_plan_radius()
    score = -(1.0 * min(rmin, 14) + 1.2 * (v[9] + v[11]) + 0.5 * (v[8] + v[10]))
    tot = score + 400 * viol + pen_j + pen_size + pen_seam
    if detail:
        return tot, dict(bx=float(bx), by=float(by), dmin=float(dd.min()), rmin=rmin, xj=float(xj), seam_room=float(H - PB.PEB["CT"] - PB.PEB["VT"] - L["zl"]), L=L)
    return tot


def main():
    rng = np.random.default_rng(11)
    best = None
    bv = 1e12
    for i in range(1500):
        v = LO + rng.random(len(LO)) * (HI - LO)
        f = evaluate(v)
        if f < bv:
            best, bv = v, f
    print("random best", bv)
    step = (HI - LO) * 0.06
    for it in range(5000):
        cand = np.clip(best + rng.normal(size=len(LO)) * step * (0.4 + 0.6 * 0.9995 ** it) * (rng.random(len(LO)) < 0.35), LO, HI)
        f = evaluate(cand)
        if f < bv:
            best, bv = cand, f
    f, info = evaluate(best, True)
    out = dict(zip(NAMES, map(float, best)))
    out.update(info)
    out["objective"] = float(f)
    json.dump(out, open(os.path.join(HERE, "explore2_best.json"), "w"), indent=1, default=float)
    print(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
