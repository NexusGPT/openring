"""Software renderer for the case pictures (numpy + Pillow; scipy only for blurs). No 3D library, no browser.

Reads look/meshes.npz (made by look/meshes.py from the assembly STEP), smooths normals across faces that meet under 30 degrees,
rasterises with a depth buffer at 2x supersampling (final 1600 x 1200), lights it like a product photo (soft key light from the upper
left, weaker fill, rim light, a studio environment reflected in the metal, soft shadow map plus contact shadow on a light grey ground)
and writes look/case-closed.png, case-open.png, case-open-empty.png, case-side.png, case-in-hand.png, and (C5d) case-post-closeup.png (lid open, no ring:
the post, the pin holder and the four pin tips) and case-post-closeup-ring.png (the same view with the US 9 ring seated).
CASE_OUT picks the folder of case_params.json (default ../out).

Run (from design/case): nice -n 19 ../.venv/bin/python look/render.py [name ...]
"""
import json
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter

HERE = os.path.dirname(os.path.abspath(__file__))
LOOK = os.environ.get("LOOK_OUT", HERE)
sys.path.insert(0, HERE)
import pebble as PB  # noqa: E402

W, Hh, SS = 1600, 1200, 2
SKIP = {"main_board", "cell_dnk852338", "U1_esp32s3_mini1", "U2_bq25895", "L1_1uH", "U3_tps63802", "L2_0u47", "U5_tps2553", "U4_zdsd64g",
        }


# ---------------------------------------------------------------- meshes
def weld(v, t, nd=4):
    key = np.round(v, nd)
    _, idx, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    inv = inv.ravel()
    return v[idx], inv[t]


def smooth_normals(v, t, deg=30.0):
    """per-corner normals (F,3,3): area weighted mean of the face normals of the faces at that vertex within deg of this face"""
    v, t = weld(v, t)
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    fn = np.cross(b - a, c - a)
    ar = np.linalg.norm(fn, axis=1)
    ok = ar > 1e-12
    fn[ok] /= ar[ok, None]
    F = len(t)
    cv = t.ravel()
    cf = np.repeat(np.arange(F), 3)
    order = np.argsort(cv, kind="stable")
    cvs, cfs = cv[order], cf[order]
    cnt = np.bincount(cvs, minlength=len(v))
    mv = cnt.max()
    start = np.concatenate([[0], np.cumsum(cnt)[:-1]])
    inc = -np.ones((len(v), mv), int)
    pos = np.arange(len(cvs)) - start[cvs]
    inc[cvs, pos] = cfs
    out = np.zeros((F, 3, 3))
    cosd = math.cos(math.radians(deg))
    for k in range(3):
        g = inc[t[:, k]]                                    # (F, mv)
        valid = g >= 0
        gn = fn[np.where(valid, g, 0)]                      # (F, mv, 3)
        d = (gn * fn[:, None, :]).sum(2)
        w = np.where(valid & (d >= cosd), ar[np.where(valid, g, 0)], 0.0)
        s = (gn * w[:, :, None]).sum(1)
        nn = np.linalg.norm(s, axis=1)
        s = np.where(nn[:, None] > 1e-12, s / np.maximum(nn, 1e-12)[:, None], fn)
        out[:, k] = s
    return v, t, out, fn


def rho_point_vec(x, y, n_, ax, axr, b0, k, xc):
    lo = np.full(len(x), 1e-4)
    hi = np.full(len(x), 3.0)
    for _ in range(50):
        r = 0.5 * (lo + hi)
        un = (x - xc) / np.where(x < xc, ax, axr) / r
        cs = np.clip(un, -1, 1)
        bb = b0 * (1 - k * cs) * r
        f = np.abs(un) ** n_ + np.abs(y / bb) ** n_
        big = f > 1
        lo = np.where(big, r, lo)
        hi = np.where(big, hi, r)
    return 0.5 * (lo + hi)


# materials: name -> (albedo rgb, spec rgb, spec amount, rough, emissive)
MAT = {
    "silver": ((0.46, 0.47, 0.49), (0.93, 0.94, 0.96), 0.80, 0.50, 0.0),
    "white": ((0.90, 0.90, 0.89), (0.9, 0.9, 0.9), 0.10, 0.6, 0.0),
    "gold": ((0.95, 0.72, 0.30), (1.0, 0.78, 0.36), 0.85, 0.20, 0.0),
    "blackmetal": ((0.05, 0.05, 0.055), (0.55, 0.55, 0.6), 0.55, 0.28, 0.0),
    "glass": ((0.01, 0.01, 0.012), (0.9, 0.92, 0.95), 0.80, 0.06, 0.0),
    "green": ((0.05, 0.9, 0.2), (0.4, 0.9, 0.5), 0.2, 0.3, 1.0),
    "dark": ((0.03, 0.03, 0.035), (0.3, 0.3, 0.3), 0.3, 0.4, 0.0),
    "coin_gold": ((0.85, 0.65, 0.28), (0.95, 0.75, 0.35), 0.7, 0.3, 0.0),
    "coin_silver": ((0.7, 0.7, 0.72), (0.9, 0.9, 0.92), 0.7, 0.3, 0.0),
    "ground": ((0.86, 0.86, 0.87), (0.5, 0.5, 0.5), 0.0, 1.0, 0.0),
    "liner": ((0.035, 0.035, 0.04), (0.30, 0.30, 0.33), 0.22, 0.7, 0.0),
    "trim": ((0.62, 0.62, 0.64), (1.0, 1.0, 1.0), 0.98, 0.1, 0.0),
    "bezel": ((0.10, 0.10, 0.11), (0.85, 0.85, 0.9), 0.90, 0.15, 0.0),
    "lamp": ((0.55, 1.0, 0.65), (0.4, 0.9, 0.5), 0.2, 0.3, 1.0),
    "titanium": ((0.40, 0.40, 0.42), (0.82, 0.83, 0.86), 0.80, 0.40, 0.0),
    "mattblack": ((0.015, 0.015, 0.017), (0.10, 0.10, 0.10), 0.05, 0.9, 0.0),
    "foot": ((0.03, 0.03, 0.035), (0.20, 0.20, 0.22), 0.15, 0.8, 0.0),
}
MATNAMES = list(MAT)
MID = {n: i for i, n in enumerate(MATNAMES)}


def part_material(name):
    if name == "ring_US9_body":
        return "titanium"
    if name == "post":
        return "silver"
    if name.startswith("pin_board"):
        return "mattblack"
    if name == "pin_holder":
        return "dark"
    if name == "liner":
        return "liner"
    if name in ("seam_trim", "lid_seam_trim"):
        return "trim"
    if name == "usb_bezel":
        return "bezel"
    if name == "light_window":
        return "lamp"
    if name == "foot":
        return "foot"
    if name in ("shell", "lid", "base_plate"):
        return "silver"
    if name == "post":
        return "white"
    if name.startswith("pin_P") or name == "ring_US9_pads":
        return "gold"
    if name == "ring_US9_body" or name.startswith("hinge") or name.startswith("magnet"):
        return "blackmetal"
    if name in ("ring_US9_glass", "ring_US9_joystick"):
        return "glass"
    if name == "LED1":
        return "green"
    if name.startswith("glide"):
        return "white"
    return "dark"


class Scene:
    def __init__(self, prm, open_lid=False, ring=True, coin=False, open_deg=None, c4=False, c4_gap=62.0, bar=None, clip_x=None):
        self.prm = prm
        z = np.load(os.path.join(LOOK, "meshes.npz"))
        PB.PEB.update(prm["pebble"])
        H = prm["h_tot"]
        pivot = np.array(prm["pivot"])
        ang = math.radians(prm["lid_open_deg"] if open_deg is None else open_deg) if open_lid else 0.0
        R = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
        V, T, N, FN, M = [], [], [], [], []
        off = 0
        for name in z["names"]:
            if name in SKIP:
                continue
            if not ring and name.startswith("ring_"):
                continue
            if name.startswith("pin_P") and not ring and False:
                continue
            v, t = z[name + "__v"].astype(float), z[name + "__t"]
            if clip_x is not None:
                # cutaway (C5d close-up): the lid and its riders are left out; every other part keeps only the triangles beyond the cut plane x = clip_x
                if name in ("lid", "lid_seam_trim", "magnet_lid", "hinge_pivot") or name.startswith("glide"):
                    continue
                keep = v[t].mean(1)[:, 0] >= clip_x
                t = t[keep]
                if len(t) == 0:
                    continue
            if open_lid and name in ("lid", "magnet_lid", "glide_1", "glide_2", "glide_3", "glide_4", "hinge_pivot"):
                # lid and what rides on it turn about the pivot; the glides stay on the base (they are the base's)
                if True:
                    v[:, :2] = (v[:, :2] - pivot) @ R.T + pivot
            vv, tt, nn, fn = smooth_normals(v, t)
            mats = np.full(len(tt), MID[part_material(name)])
            if name in ("shell", "lid", "base_plate"):
                c = vv[tt].mean(1)
                if open_lid and name == "lid":
                    cc = c.copy()
                    cc[:, :2] = (c[:, :2] - pivot) @ R + pivot          # back to the closed pose to classify
                    c = cc
                rp = PB.rho_point_vec(c[:, 0], c[:, 1])
                rz = np.array(PB.rho_of_z(c[:, 2], H))
                on_skin = rp >= rz - 0.035
                if name == "lid":
                    on_skin = c[:, 2] > prm["z_lid0"] + 0.02       # the whole top of the lid is skin (the crown's plan is rounder than the wall's)
                if name == "base_plate":
                    on_skin = np.ones(len(c), bool)
                at_seam = (np.abs(c[:, 2] - prm["z_split"]) < 0.02) | (np.abs(c[:, 2] - prm["z_lid0"]) < 0.02)
                if name == "shell":
                    mats = np.where(on_skin | at_seam, MID["silver"], MID["liner"])
                elif name == "lid":
                    mats = np.where(on_skin | at_seam, MID["silver"], MID["liner"])
                else:
                    mats = np.where(on_skin, MID["silver"], MID["liner"])
            if name == "J1_usb4105":
                mats[:] = MID["dark"]
            V.append(vv)
            T.append(tt + off)
            N.append(nn)
            FN.append(fn)
            M.append(mats)
            off += len(vv)
        if not open_lid:
            # dark liner behind the seam gap (the real case is dark there): a thin wall just inside the outline between the two seam planes
            ox, oy = PB.outline_at(0.985, 240)
            n_ = len(ox)
            pv = np.array([[ox[i], oy[i], z] for z in (prm["z_split"] - 0.5, prm["z_lid0"] + 0.5) for i in range(n_)])
            pt = []
            for i in range(n_):
                j = (i + 1) % n_
                pt += [[i, j, n_ + j], [i, n_ + j, n_ + i]]
            vv, tt, nn, fn = smooth_normals(pv, np.array(pt))
            V.append(vv); T.append(tt + off); N.append(nn); FN.append(fn); M.append(np.full(len(tt), MID["dark"])); off += len(vv)
        if c4:
            zc4 = np.load(os.path.join(LOOK, "c5b_meshes.npz"))
            dx = np.array([-c4_gap, 0.0, 0.0])
            for name in ("shell", "lid", "base_plate"):
                v = zc4[name + "__v"].astype(float) + dx
                vv, tt, nn, fn = smooth_normals(v, zc4[name + "__t"])
                V.append(vv); T.append(tt + off); N.append(nn); FN.append(fn); M.append(np.full(len(tt), MID["silver"])); off += len(vv)
        if bar:
            # 20 mm scale bar on the ground in front of the case(s)
            b0 = np.array(bar)
            bx = np.array([[0, 0, 0], [20, 0, 0], [20, 1.2, 0], [0, 1.2, 0], [0, 0, 0.5], [20, 0, 0.5], [20, 1.2, 0.5], [0, 1.2, 0.5]], float) + b0
            bt = np.array([[0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5], [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7], [4, 5, 6], [4, 6, 7]])
            vv, tt, nn, fn = smooth_normals(bx, bt)
            V.append(vv); T.append(tt + off); N.append(nn); FN.append(fn); M.append(np.full(len(tt), MID["dark"])); off += len(vv)
        if coin:
            cv, ct = make_coin(prm["coin_xy"])
            for sub, (v, t, m) in cv.items():
                vv, tt, nn, fn = smooth_normals(v, t)
                V.append(vv)
                T.append(tt + off)
                N.append(nn)
                FN.append(fn)
                M.append(np.full(len(tt), MID[m]))
                off += len(vv)
        self.V = np.vstack(V)
        self.T = np.vstack(T)
        self.N = np.vstack(N)
        self.FN = np.vstack(FN)
        self.M = np.concatenate(M)
        self.H = H


def make_coin(xy, d=23.25, th=2.33, rim=2.6, n=96):
    """1 euro coin: gold ring, silver centre (as drawn on the coin), lying flat at xy"""
    cx, cy = xy
    out = {}
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    for nm, r0, r1, mat in (("ring", d / 2 - 2.9, d / 2, "coin_gold"), ("centre", 0.0, d / 2 - 2.9, "coin_silver")):
        V, T = [], []
        def ring_pts(r, z):
            return np.stack([cx + r * np.cos(a), cy + r * np.sin(a), np.full(n, z)], 1)
        zb, zt = 0.0, th
        if r0 == 0.0:
            zt = th - 0.35
        outer_b, outer_t = ring_pts(r1, zb), ring_pts(r1, zt)
        V = [outer_b, outer_t]
        T = []
        for i in range(n):
            j = (i + 1) % n
            T += [[i, j, n + j], [i, n + j, n + i]]
        if r0 > 0:
            inner_t = ring_pts(r0, zt)
            V.append(inner_t)
            for i in range(n):
                j = (i + 1) % n
                T += [[n + i, n + j, 2 * n + j], [n + i, 2 * n + j, 2 * n + i]]
            # a raised rim: lift the outer top ring edge slightly (flat coin face)
        else:
            c = np.array([[cx, cy, zt]])
            V.append(c)
            for i in range(n):
                j = (i + 1) % n
                T.append([n + i, n + j, 2 * n])
        out[nm] = (np.vstack(V), np.array(T), mat)
    return out, None


# ---------------------------------------------------------------- camera and raster
def look_at(eye, target, up=(0, 0, 1)):
    f = np.asarray(target, float) - np.asarray(eye, float)
    f /= np.linalg.norm(f)
    r = np.cross(f, up)
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return r, u, f


class Cam:
    def __init__(self, eye, target, fov=None, ortho_h=None, w=W * SS, h=Hh * SS, up=(0, 0, 1)):
        self.eye = np.asarray(eye, float)
        self.r, self.u, self.f = look_at(eye, target, up)
        self.w, self.h = w, h
        self.fov, self.ortho_h = fov, ortho_h

    def project(self, P):
        d = P - self.eye
        x, y, z = d @ self.r, d @ self.u, d @ self.f
        if self.ortho_h is not None:
            s = self.h / self.ortho_h
            return self.w / 2 + x * s, self.h / 2 - y * s, z, np.ones_like(z)
        s = (self.h / 2) / math.tan(math.radians(self.fov) / 2)
        return self.w / 2 + x / z * s, self.h / 2 - y / z * s, z, 1.0 / z

    def ray(self, px, py):
        """world ray directions for pixel coordinates"""
        if self.ortho_h is not None:
            s = self.h / self.ortho_h
            x, y = (px - self.w / 2) / s, -(py - self.h / 2) / s
            o = self.eye + x[..., None] * self.r + y[..., None] * self.u
            return o, np.broadcast_to(self.f, o.shape)
        s = (self.h / 2) / math.tan(math.radians(self.fov) / 2)
        x, y = (px - self.w / 2) / s, -(py - self.h / 2) / s
        d = x[..., None] * self.r + y[..., None] * self.u + self.f
        d /= np.linalg.norm(d, axis=-1, keepdims=True)
        return np.broadcast_to(self.eye, d.shape), d


def rasterize(cam, V, T, need_attr=True):
    w, h = cam.w, cam.h
    sx, sy, sz, iw = cam.project(V)
    depth = np.full((h, w), np.inf)
    tid = -np.ones((h, w), np.int32)
    bw = np.zeros((h, w, 3), np.float32) if need_attr else None
    persp = cam.ortho_h is None
    X, Y, Z = sx[T], sy[T], sz[T]
    xmin = np.floor(X.min(1)).astype(int)
    xmax = np.ceil(X.max(1)).astype(int)
    ymin = np.floor(Y.min(1)).astype(int)
    ymax = np.ceil(Y.max(1)).astype(int)
    keep = (xmax >= 0) & (xmin < w) & (ymax >= 0) & (ymin < h) & (Z.min(1) > 0.01)
    for i in np.where(keep)[0]:
        x0, x1 = max(xmin[i], 0), min(xmax[i], w - 1)
        y0, y1 = max(ymin[i], 0), min(ymax[i], h - 1)
        ax_, ay_, bx_, by_, cx_, cy_ = X[i, 0], Y[i, 0], X[i, 1], Y[i, 1], X[i, 2], Y[i, 2]
        den = (by_ - cy_) * (ax_ - cx_) + (cx_ - bx_) * (ay_ - cy_)
        if abs(den) < 1e-12:
            continue
        px = np.arange(x0, x1 + 1) + 0.5
        py = (np.arange(y0, y1 + 1) + 0.5)[:, None]
        l0 = ((by_ - cy_) * (px - cx_) + (cx_ - bx_) * (py - cy_)) / den
        l1 = ((cy_ - ay_) * (px - cx_) + (ax_ - cx_) * (py - cy_)) / den
        l2 = 1 - l0 - l1
        m = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
        if not m.any():
            continue
        if persp:
            iz = l0 / Z[i, 0] + l1 / Z[i, 1] + l2 / Z[i, 2]
            z = 1.0 / iz
        else:
            z = l0 * Z[i, 0] + l1 * Z[i, 1] + l2 * Z[i, 2]
        sub = depth[y0:y1 + 1, x0:x1 + 1]
        upd = m & (z < sub)
        if not upd.any():
            continue
        sub[upd] = z[upd]
        tid[y0:y1 + 1, x0:x1 + 1][upd] = i
        if need_attr:
            if persp:
                b = np.stack([l0 / Z[i, 0], l1 / Z[i, 1], l2 / Z[i, 2]], -1) * z[..., None]
            else:
                b = np.stack([l0, l1, l2], -1)
            bw[y0:y1 + 1, x0:x1 + 1][upd] = b[upd]
    return depth, tid, bw


# ---------------------------------------------------------------- lighting
def unit(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def studio_env(d, cam):
    """radiance seen along world direction d (N,3): a studio around the camera frame"""
    x, y, z = d @ cam.r, d @ cam.u, -(d @ cam.f)          # z toward the viewer
    up = np.clip(y, -1, 1)
    base = 0.26 + 0.32 * smoothstep(-0.25, 0.85, up)       # soft sky gradient
    base = np.where(up < -0.15, 0.16 + 0.10 * smoothstep(-1, -0.15, up), base)
    # key softbox upper left, large
    kd = unit(np.array([-0.62, 0.62, 0.48]))
    ang = np.arccos(np.clip(x * kd[0] + y * kd[1] + z * kd[2], -1, 1))
    key = 1.5 * (1 - smoothstep(0.12, 0.70, ang))
    # second broad light right-above, weaker
    fd = unit(np.array([0.7, 0.45, 0.35]))
    ang2 = np.arccos(np.clip(x * fd[0] + y * fd[1] + z * fd[2], -1, 1))
    fill = 0.45 * (1 - smoothstep(0.15, 0.7, ang2))
    # rim strip behind right
    rd = unit(np.array([0.85, 0.15, -0.5]))
    ang3 = np.arccos(np.clip(x * rd[0] + y * rd[1] + z * rd[2], -1, 1))
    rim = 1.1 * (1 - smoothstep(0.08, 0.40, ang3))
    # dark flag: darker band at the lower left, so the metal has contrast
    fl = unit(np.array([-0.5, -0.45, 0.45]))
    ang4 = np.arccos(np.clip(x * fl[0] + y * fl[1] + z * fl[2], -1, 1))
    flag = 0.30 * (1 - smoothstep(0.1, 0.8, ang4))
    return np.clip(base + key + fill + rim - flag, 0.02, 3.0)


def box_blur_shadow(smap, u, v, depth_ref, rad, bias):
    """soft shadow: average of 12 samples around (u,v) in the shadow map; returns light fraction"""
    h, w = smap.shape
    acc = np.zeros(u.shape)
    offs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (.7, .7), (-.7, .7), (.7, -.7), (-.7, -.7), (1.6, .4), (-1.6, -.4), (.4, -1.6), (-.4, 1.6)]
    for ox, oy in offs:
        uu = np.clip((u + ox * rad).astype(int), 0, w - 1)
        vv = np.clip((v + oy * rad).astype(int), 0, h - 1)
        acc += (smap[vv, uu] > depth_ref - bias)
    return acc / len(offs)


def render_view(sc, cam, out_name, ground=True, coin_outline=None, lid_shadow=True, label=None, exposure=1.0):
    w, h = cam.w, cam.h
    V, T = sc.V, sc.T
    depth, tid, bw = rasterize(cam, V, T)
    hit = tid >= 0
    ti = np.where(hit, tid, 0)
    b = bw.astype(float)
    P = (V[T[ti]] * b[..., None]).sum(2)
    N = (sc.N[ti] * b[..., None]).sum(2)
    N = unit(N + 1e-12)
    mat = sc.M[ti]
    # ground
    o, d = cam.ray(*np.meshgrid(np.arange(w) + 0.5, np.arange(h) + 0.5))
    tg = -o[..., 2] / np.where(np.abs(d[..., 2]) < 1e-9, 1e-9, d[..., 2])
    Pg = o + d * tg[..., None]
    gvalid = (tg > 0) & ~hit
    if cam.ortho_h is not None:
        gvalid = gvalid & (np.abs(d[..., 2]) > 1e-6)
    Vd = -d                                                   # towards the viewer
    Nf = np.where((N * Vd).sum(-1, keepdims=True) < 0, -N, N)
    # shading of the object
    alb = np.array([MAT[n][0] for n in MATNAMES])[mat]
    spc = np.array([MAT[n][1] for n in MATNAMES])[mat]
    amt = np.array([MAT[n][2] for n in MATNAMES])[mat][..., None]
    emi = np.array([MAT[n][4] for n in MATNAMES])[mat][..., None]
    ndv = np.clip((Nf * Vd).sum(-1, keepdims=True), 0, 1)
    refl = unit(2 * (Nf * Vd).sum(-1, keepdims=True) * Nf - Vd)
    env = studio_env(refl.reshape(-1, 3), cam).reshape(h, w, 1)
    fres = 0.04 + 0.96 * (1 - ndv) ** 5
    # diffuse: key from upper left (camera frame), weak fill, rim
    def cl(v):
        return v[0] * (-cam.r) + v[1] * cam.u + v[2] * (-cam.f)
    Lk, Lf, Lr = unit(cl([0.62, 0.62, 0.48])), unit(cl([-0.7, 0.25, 0.4])), unit(cl([-0.2, 0.5, -0.8]))
    # shadow map from the key light (ortho)
    lcen = np.array([sc.V[:, 0].mean(), 0, 15.0])
    lcam = Cam(lcen + Lk * 300, lcen, ortho_h=140.0, w=1200, h=1200, up=tuple(cam.u))
    # object-only occluders (not the ground)
    sdepth, _, _ = rasterize(lcam, V, T, need_attr=False)
    sdepth = np.where(np.isinf(sdepth), 1e9, sdepth)

    def shadow_at(Pw, rad, bias):
        pxs, pys, pz, _ = lcam.project(Pw.reshape(-1, 3))
        # smap holds the nearest depth along light; lit when the point is not deeper than it
        hh, ww = sdepth.shape
        acc = np.zeros(len(pxs))
        offs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (.7, .7), (-.7, .7), (.7, -.7), (-.7, -.7), (1.7, .5), (-1.7, -.5), (.5, -1.7), (-.5, 1.7),
                (2.4, 0), (-2.4, 0), (0, 2.4), (0, -2.4)]
        for ox, oy in offs:
            uu = np.clip((pxs + ox * rad).astype(int), 0, ww - 1)
            vv = np.clip((pys + oy * rad).astype(int), 0, hh - 1)
            acc += (pz <= sdepth[vv, uu] + bias)
        return (acc / len(offs)).reshape(Pw.shape[:-1])

    wrap = lambda L: np.clip(((Nf * L).sum(-1, keepdims=True) + 0.35) / 1.35, 0, 1) ** 1.4
    sh = shadow_at(np.where(hit[..., None], P, 0.0), 4.0, 0.35)[..., None]
    sh = np.where(hit[..., None], sh, 1.0)
    diff = 0.95 * wrap(Lk) * (0.35 + 0.65 * sh) + 0.35 * wrap(Lf) + 0.30 * wrap(Lr) + 0.22
    # ambient occlusion in screen space from the position buffer (24 taps)
    Pz = np.where(hit, depth, np.nan)
    ao = ssao(P, Nf, hit, depth, cam)
    col = alb * diff * ao + spc * amt * env * (0.35 + 0.65 * fres) * (0.55 + 0.45 * ao) * (0.55 + 0.45 * sh)
    # satin sheen: broad spec lobe from key light
    hv = unit(Lk + Vd)
    sheen = np.clip((Nf * hv).sum(-1, keepdims=True), 0, 1) ** 18
    col = col + 0.10 * sheen * spc * amt * sh
    col = col + emi * alb * 1.6
    # ground
    if ground:
        gx, gy = Pg[..., 0], Pg[..., 1]
        gcol = np.array(MAT["ground"][0])[None, None, :] * np.ones((h, w, 1))
        # soft gradient
        yy = (np.arange(h) / h)[:, None]
        gcol = gcol * (0.93 + 0.12 * (1 - yy))[..., None]
        sg = shadow_at(Pg, 6.0, 0.05)
        # contact shadow: footprint blur from the object depth directly above (top view mask of the closed pebble, 1 where the object stands)
        fp = footprint(sc, Pg, gvalid)
        gsh = 1 - 0.55 * (1 - sg) - 0.42 * fp
        gcol = gcol * np.clip(gsh, 0.25, 1.0)[..., None]
        if coin_outline is not None:
            gcol = gcol * (1 - 0.65 * coin_outline(Pg)[..., None])
        col = np.where(gvalid[..., None], gcol, col)
        bgv = ~hit & ~gvalid
        col = np.where(bgv[..., None], np.array([0.93, 0.93, 0.94])[None, None, :], col)
    if not ground:
        col = np.where(hit[..., None], col, np.array([0.93, 0.93, 0.94])[None, None, :] / max(exposure, 1e-6))
    col = exposure * col
    # filmic tone map and gamma
    col = col / (1 + 0.18 * col)
    col = np.clip(col * 1.12, 0, 1) ** (1 / 2.2)
    # green LED bloom
    if np.any(mat[hit] == MID["green"]):
        gm = ((mat == MID["green"]) & hit).astype(float)
        bl = gaussian_filter(gm, 9 * SS) * 6
        col = np.clip(col + bl[..., None] * np.array([0.1, 0.9, 0.3]) * 0.55, 0, 1)
    img = Image.fromarray((col * 255 + 0.5).astype(np.uint8)).resize((w // SS, h // SS), Image.LANCZOS)
    img.save(os.path.join(LOOK, out_name))
    print("wrote", out_name, img.size)
    return img


_FP = {}


def footprint(sc, Pg, gvalid):
    """soft occupancy of the ground below the object: 1 where the object's base touches, falling off with blur"""
    key = id(sc)
    if key not in _FP:
        # rasterise the object from above, ortho, low resolution: mask and lowest height
        cam = Cam((sc.V[:, 0].mean(), 0, 300), (sc.V[:, 0].mean(), 0, 0), ortho_h=140.0, w=512, h=512, up=(0, 1, 0))
        d, tid, _ = rasterize(cam, sc.V, sc.T, need_attr=False)
        m = (tid >= 0).astype(float)
        lowz = np.where(tid >= 0, 300 - d, 0.0)             # z of the top surface
        near = m * np.exp(-np.maximum(lowz - 0.0, 0) / 18.0)
        a = gaussian_filter(near, 5.0)
        _FP[key] = (cam, a, gaussian_filter(m, 2.0))
    cam, a, m2 = _FP[key]
    px, py, _, _ = cam.project(Pg.reshape(-1, 3))
    u = np.clip(px.astype(int), 0, 511)
    v = np.clip(py.astype(int), 0, 511)
    out = (0.6 * a[v, u] + 0.9 * m2[v, u] * 0.0).reshape(Pg.shape[:-1])
    return np.clip(out * 1.6, 0, 1)


def ssao(P, N, hit, depth, cam, taps=20):
    h, w = depth.shape
    ao = np.ones((h, w, 1))
    Pf = np.where(hit[..., None], P, 0.0)
    rng = np.random.default_rng(3)
    acc = np.zeros((h, w))
    n = 0
    for rad in (6 * SS, 14 * SS, 30 * SS):
        for k in range(taps // 3 + 1):
            a = rng.random() * 2 * math.pi
            dx, dy = int(rad * math.cos(a)), int(rad * math.sin(a))
            Ps = np.roll(np.roll(Pf, dy, axis=0), dx, axis=1)
            hs = np.roll(np.roll(hit, dy, axis=0), dx, axis=1)
            dv = Ps - Pf
            dist = np.linalg.norm(dv, axis=-1)
            occ = np.clip((dv * N).sum(-1) / np.maximum(dist, 1e-6) - 0.15, 0, 1) * np.clip(1.0 - dist / 14.0, 0, 1)
            acc += np.where(hs & hit, occ, 0.0)
            n += 1
    ao = 1 - 1.1 * acc / n
    ao = gaussian_filter(np.clip(ao, 0, 1), 1.2 * SS)
    return np.clip(ao, 0.25, 1)[..., None]


# ---------------------------------------------------------------- views
def main():
    prm = json.load(open(os.path.join(os.environ.get("CASE_OUT", os.path.join(HERE, "..", "out")), "case_params.json")))
    which = set(sys.argv[1:]) or {"closed", "open", "open-empty", "side", "underside", "compare"}
    cx = 0.5 * (prm["x_min"] + prm["x_max"])
    zmid = 0.5 * prm["h_tot"]
    tgt = np.array([cx, 0, zmid])
    if "closed" in which:
        sc = Scene(prm)
        eye = tgt + 330 * unit(np.array([-0.70, -0.72, 0.62]))
        render_view(sc, Cam(eye, tgt + np.array([0, 0, 2]), fov=14.5), "case-closed.png")
    for nm, ring in (("open", True), ("open-empty", False)):
        if nm not in which:
            continue
        sc = Scene(prm, open_lid=True, ring=ring)
        tg = np.array([cx + 2.0, -2.0, zmid + 4.0])
        eye = tg + 330 * unit(np.array([-0.16, -0.40, 0.90]))
        render_view(sc, Cam(eye, tg, fov=15), f"case-{nm}.png")
    for nm, ring in (("post-closeup", False), ("post-closeup-ring", True)):
        if nm not in which:
            continue
        # cutaway: the case is cut by the plane x = -4.0 (the -X wall, the USB-C side, is left out) so the pin face of the post can be seen
        sc = Scene(prm, open_lid=False, ring=ring, clip_x=-4.0)
        hm = prm["pin_holder"]
        tg = np.array([hm["front_x_at_y0"] + 0.6, 0.0, prm["z_pin"] - 0.4])
        eye = tg + 330 * unit(np.array([-0.62, 0.14, 0.78]))
        render_view(sc, Cam(eye, tg, fov=3.9), f"case-{nm}.png", lid_shadow=False, exposure=1.5)
    if "side" in which:
        sc = Scene(prm)
        render_view(sc, Cam((cx, -400, zmid), (cx, 0, zmid), ortho_h=62.0), "case-side.png")
    if "underside" in which:
        sc = Scene(prm)
        tg = np.array([cx, 0, 6.0])
        eye = tg + 330 * unit(np.array([-0.62, -0.62, -0.42]))
        render_view(sc, Cam(eye, tg, fov=15), "case-underside.png", ground=False)
    if "in-hand" in which:
        sc_prm = dict(prm)
        sc_prm["coin_xy"] = (prm["x_max"] + 17.0, 4.0)
        sc = Scene(sc_prm, coin=True)
        tg = np.array([cx + 5.0, 3.0, 8.0])
        eye = tg + 330 * unit(np.array([-0.45, -0.62, 0.64]))
        pc = np.array([cx + 5.0, 0.0])

        def palm(Pg):
            x, y = Pg[..., 0] - pc[0], Pg[..., 1] - pc[1]
            hx, hy, r_ = 40.0, 22.5, 14.0
            qx, qy = np.abs(x) - (hx - r_), np.abs(y) - (hy - r_)
            dd = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r_
            return np.exp(-(dd / 0.45) ** 2)
        render_view(sc, Cam(eye, tg, fov=17), "case-in-hand.png", coin_outline=palm)
    if "compare" in which:
        from PIL import ImageDraw
        gap = 60.0
        bar0 = (cx - 10.0, -34.0, 0.0)
        sc = Scene(prm, c4=True, c4_gap=gap, bar=bar0)
        tg = np.array([cx - gap / 2, 0, zmid - 2.0])
        eye = tg + 420 * unit(np.array([0.0, -1.0, 0.42]))
        cam = Cam(eye, tg, fov=17)
        img = render_view(sc, cam, "case-compare-c5b-c5c.png", ground=True)
        d = ImageDraw.Draw(img)
        sx, sy, _, _ = cam.project(np.array([[cx, -34.0, 0.0], [cx - gap + 1.4, -22.0, 0.0], [cx, -22.0, 0.0]]))
        d.text((sx[0] / SS - 22, sy[0] / SS + 14), "20 mm", fill=(30, 30, 30))
        d.text((sx[1] / SS - 50, sy[1] / SS + 40), "C5b  45.5 x 45.9 x 41.4 mm", fill=(30, 30, 30))
        sx2 = cam.project(np.array([[cx + 5.0, -22.0, 0.0]]))
        d.text((sx2[0][0] / SS - 50, sx2[1][0] / SS + 75), "C5c  %.1f x %.1f x %.1f mm" % tuple(prm["size_box"]), fill=(30, 30, 30))
        img.save(os.path.join(LOOK, "case-compare-c5b-c5c.png"))


if __name__ == "__main__":
    main()
