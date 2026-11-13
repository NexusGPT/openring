"""The pebble's outside form (version C5b), numpy only; case.py turns it into a solid.

Plan: a tapered, asymmetric superellipse (exponent N_EXP, no straight segment). Profile: the outline at height z is the widest outline
scaled about (XC, 0) by rho(z). From the bottom pole: a crown (centre lowest), an elliptical bottom edge (horizontal extent EB mm, vertical
extent VB mm), a straight wall (the seam is cut in it), an elliptical top edge (ET, VT) and the lid's crown (centre highest by CT mm).
Every piece meets the next with the same tangent: one continuous skin, no planar face.
"""
import math

import numpy as np

PEB = dict(N_EXP=6.031, N_R=4.953, AX=22.44, AXR=22.953, B0=22.74, K=0.025, XC=8.459, EB=7.454, VB=3.057, ET=10.0, VT=1.834, CB=0.444, CT=0.683, S=22.513, H=41.4)


def _curve(H, n=60):
    """dense (z, rho) from the bottom pole to the top pole, z increasing"""
    S, eb, vb, et, vt, cb, ct = (PEB[k] for k in ("S", "EB", "VB", "ET", "VT", "CB", "CT"))
    reb, ret = 1 - eb / S, 1 - et / S
    z, r = [], []
    for t in np.linspace(0, 1, n):                              # bottom crown: centre lowest
        r.append(reb * t)
        z.append(cb * (3 * t * t - 2 * t ** 3))
    for u in np.linspace(1, 0, 4 * n)[1:]:                      # bottom edge, flat end (u = 1) to the wall (u = 0)
        r.append(1 - u * eb / S)
        z.append(cb + vb * (1 - math.sqrt(max(0.0, 1 - (1 - u) ** 2))))
    z.append(H - ct - vt)
    r.append(1.0)
    for u in np.linspace(0, 1, 4 * n)[1:]:                      # top edge
        r.append(1 - u * et / S)
        z.append(H - ct - vt + vt * math.sqrt(max(0.0, 1 - (1 - u) ** 2)))
    for t in np.linspace(1, 0, n)[1:]:                          # lid crown: centre highest
        r.append(ret * t)
        w = 1 - t
        z.append(H - ct + ct * (3 * w * w - 2 * w ** 3))
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
    top = zc >= H - PEB["CT"] - PEB["VT"] - 1e-6
    zt, rt = zc[top], rc[top]
    return np.interp(np.clip(r, 0, 1), rt[::-1], zt[::-1])


def sections(H=None, *_):
    """(z, rho) bottom to top for the loft; first and last are the poles (rho 0)"""
    H = PEB["H"] if H is None else H
    S, eb, vb, et, vt, cb, ct = (PEB[k] for k in ("S", "EB", "VB", "ET", "VT", "CB", "CT"))
    reb, ret = 1 - eb / S, 1 - et / S
    out = [(0.0, 0.0)]
    for t in (0.35, 0.6, 0.8, 0.92):
        out.append((cb * (3 * t * t - 2 * t ** 3), reb * t))
    for u in (1.0, 0.85, 0.7, 0.55, 0.42, 0.3, 0.2, 0.12, 0.06, 0.02):
        out.append((cb + vb * (1 - math.sqrt(1 - (1 - u) ** 2)), 1 - u * eb / S))
    zw0, zw1 = cb + vb, H - ct - vt
    for f in (0.0, 0.25, 0.5, 0.75, 1.0):
        out.append((zw0 + f * (zw1 - zw0), 1.0))
    for u in (0.02, 0.06, 0.12, 0.2, 0.3, 0.42, 0.55, 0.7, 0.85, 1.0):
        out.append((zw1 + vt * math.sqrt(1 - (1 - u) ** 2), 1 - u * et / S))
    for t in (0.92, 0.8, 0.6, 0.35):
        out.append((H - ct + ct * (3 * (1 - t) ** 2 - 2 * (1 - t) ** 3), ret * t))
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
