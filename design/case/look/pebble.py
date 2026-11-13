"""The pebble's outside form (version C5b), numpy only; case.py turns it into a solid.

Plan: a tapered, asymmetric superellipse (exponent N_EXP, no straight segment). Profile: the outline at height z is the widest outline
scaled about (XC, 0) by rho(z). From the bottom pole: a crown (centre lowest), an elliptical bottom edge (horizontal extent EB mm, vertical
extent VB mm), a straight wall (the seam is cut in it), an elliptical top edge (ET, VT) and the lid's crown (centre highest by CT mm).
Every piece meets the next with the same tangent: one continuous skin, no planar face.
"""
import math

import numpy as np

PEB = dict(ZW1=38.88, N_EXP=6.031, N_R=4.953, AX=22.44, AXR=22.953, B0=22.74, K=0.025, XC=8.459, EB=7.454, VB=3.057, ET=10.0, VT=1.834, CB=0.444, CT=0.683, S=22.513, H=41.4)


def _solve_top(H):
    """C5c: the top edge is an ellipse (ET wide, VT high) from the wall point z = ZW1; it ends at the angle where ONE circular arc through the apex
    (0, H) is tangent to it. Returns (angle, r_end, z_end, arc radius) with r in rho units * S (mm)."""
    S, et, vt, zw1 = PEB["S"], PEB["ET"], PEB["VT"], PEB["ZW1"]

    def f(th):
        r = (S - et) + et * math.cos(th)
        z = zw1 + vt * math.sin(th)
        h = H - z
        rc = (r * r + h * h) / (2 * h)
        return vt * math.cos(th) / (et * math.sin(th)) - r / (rc - h), r, z, rc
    lo, hi = 0.3, 1.5
    for _ in range(80):
        m = 0.5 * (lo + hi)
        if f(lo)[0] * f(m)[0] <= 0:
            hi = m
        else:
            lo = m
    th = 0.5 * (lo + hi)
    return (th,) + f(th)[1:]


def _curve(H, n=60):
    """dense (z, rho) from the bottom pole to the top pole, z increasing. Crown: ONE circular arc from the top edge's end to the apex."""
    S, eb, vb, et, vt, cb = (PEB[k] for k in ("S", "EB", "VB", "ET", "VT", "CB"))
    reb = 1 - eb / S
    zw1 = PEB["ZW1"]
    z, r = [], []
    for t in np.linspace(0, 1, n):                              # bottom crown: centre lowest
        r.append(reb * t)
        z.append(cb * (3 * t * t - 2 * t ** 3))
    for u in np.linspace(1, 0, 4 * n)[1:]:                      # bottom edge, flat end (u = 1) to the wall (u = 0)
        r.append(1 - u * eb / S)
        z.append(cb + vb * (1 - math.sqrt(max(0.0, 1 - (1 - u) ** 2))))
    z.append(zw1)
    r.append(1.0)
    th_e, r_e, z_e, rc = _solve_top(H)
    for th in np.linspace(0, th_e, 4 * n)[1:]:                  # top edge
        r.append(((S - et) + et * math.cos(th)) / S)
        z.append(zw1 + vt * math.sin(th))
    for rr in np.linspace(r_e, 0, 3 * n)[1:]:                   # crown: one arc, centre on the axis
        r.append(rr / S)
        z.append(H - rc + math.sqrt(max(0.0, rc * rc - rr * rr)))
    z, r = np.array(z), np.array(r)
    z = np.maximum.accumulate(z + 1e-9 * np.arange(len(z)))
    return z, r


def rho_of_z(z, H=None):
    H = PEB["H"] if H is None else H
    zc, rc = _curve(H)
    return np.interp(np.asarray(z, float), zc, rc)


def z_upper_of_rho(r, H=None):
    """z of the top surface at scale rho (the part above the wall)"""
    H = PEB["H"] if H is None else H
    zc, rc = _curve(H)
    top = zc >= PEB["ZW1"] - 1e-6
    zt, rt = zc[top], rc[top]
    return np.interp(np.clip(r, 0, 1), rt[::-1], zt[::-1])


def sections(H=None, *_):
    """(z, rho) bottom to top for the loft; first and last are the poles (rho 0)"""
    H = PEB["H"] if H is None else H
    S, eb, vb, et, vt, cb = (PEB[k] for k in ("S", "EB", "VB", "ET", "VT", "CB"))
    reb = 1 - eb / S
    out = [(0.0, 0.0)]
    for t in (0.35, 0.6, 0.8, 0.92):
        out.append((cb * (3 * t * t - 2 * t ** 3), reb * t))
    for u in (1.0, 0.85, 0.7, 0.55, 0.42, 0.3, 0.2, 0.12, 0.06, 0.02):
        out.append((cb + vb * (1 - math.sqrt(1 - (1 - u) ** 2)), 1 - u * eb / S))
    zw0, zw1 = cb + vb, PEB["ZW1"]
    for f in (0.0, 0.25, 0.5, 0.75, 1.0):
        out.append((zw0 + f * (zw1 - zw0), 1.0))
    th_e, r_e, z_e, rc = _solve_top(H)
    for f in (0.02, 0.06, 0.12, 0.2, 0.3, 0.42, 0.55, 0.7, 0.85, 1.0):
        th = th_e * f
        out.append((zw1 + vt * math.sin(th), ((S - et) + et * math.cos(th)) / S))
    for f in (0.88, 0.74, 0.58, 0.42, 0.28, 0.16, 0.07):
        rr = r_e * f
        out.append((H - rc + math.sqrt(rc * rc - rr * rr), rr / S))
    out.append((H, 0.0))
    return out


def n_of_t(t):
    """exponent: N_EXP on the -X side, N_R on the +X side, blended smoothly with cos t"""
    return PEB["N_EXP"] + (PEB["N_R"] - PEB["N_EXP"]) * (1 + np.cos(t)) / 2


def unit_plan(n_pts=120, w=1.0):
    """w < 1 rounds the plan toward an ellipse (exponent 2 + (n - 2) w): used near the poles so the crowns close without a pinch"""
    ax, axr, b0, k, xc = (PEB[a] for a in ("AX", "AXR", "B0", "K", "XC"))
    t = np.linspace(0, 2 * np.pi, n_pts, endpoint=False)
    n = 2.0 + (n_of_t(t) - 2.0) * w
    c, s = np.cos(t), np.sin(t)
    cs = np.sign(c) * np.abs(c) ** (2.0 / n)
    sn = np.sign(s) * np.abs(s) ** (2.0 / n)
    return xc + np.where(cs < 0, ax, axr) * cs, b0 * (1 - k * cs) * sn


def outline_at(rho, n_pts=120):
    tt = min(max(rho / 0.78, 0.0), 1.0)
    x, y = unit_plan(n_pts, tt * tt * (3 - 2 * tt))
    xc = PEB["XC"]
    return xc + (x - xc) * rho, y * rho


def rho_point(x, y):
    return float(rho_point_vec(np.array([float(x)]), np.array([float(y)]))[0])


def rho_point_vec(x, y):
    ax, axr, b0, k, xc = (PEB[a] for a in ("AX", "AXR", "B0", "K", "XC"))
    x, y = np.asarray(x, float), np.asarray(y, float)
    lo = np.full(len(x), 1e-4)
    hi = np.full(len(x), 3.0)
    for _ in range(50):
        r = 0.5 * (lo + hi)
        un = (x - xc) / np.where(x < xc, ax, axr) / r
        cs = np.clip(un, -1, 1)
        vn = y / (b0 * (1 - k * cs) * r)
        n = n_of_t(np.arctan2(vn, un))
        f = np.abs(un) ** n + np.abs(vn) ** n
        big = f > 1
        lo = np.where(big, r, lo)
        hi = np.where(big, hi, r)
    return 0.5 * (lo + hi)


def cloud(H=None, nt=240, nz=160):
    H = PEB["H"] if H is None else H
    zs = np.linspace(0, H, nz)
    rs = rho_of_z(zs, H)
    x, y = unit_plan(nt)
    xc = PEB["XC"]
    X = xc + (x - xc)[None, :] * rs[:, None]
    Y = y[None, :] * rs[:, None]
    Z = np.repeat(zs[:, None], nt, 1)
    return np.stack([X.ravel(), Y.ravel(), Z.ravel()], 1)


def min_plan_radius():
    t = np.linspace(0, 2 * np.pi, 4000, endpoint=False)
    x, y = unit_plan(4000)
    dx, dy = np.gradient(x, t), np.gradient(y, t)
    ddx, ddy = np.gradient(dx, t), np.gradient(dy, t)
    kap = np.abs(dx * ddy - dy * ddx) / (dx * dx + dy * dy) ** 1.5
    return float(1.0 / kap.max())


def vertical_fraction(H=None, deg=5.0):
    H = PEB["H"] if H is None else H
    pts = cloud(H, nt=180, nz=400).reshape(400, 180, 3)
    dz = pts[1, 0, 2] - pts[0, 0, 2]
    d = np.hypot(np.diff(pts[:, :, 0], axis=0), np.diff(pts[:, :, 1], axis=0)) / dz
    return float(np.mean(d < math.tan(math.radians(deg)), axis=0).max())
