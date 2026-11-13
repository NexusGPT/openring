"""Ring charging case, version C5b: the soft pebble inside C4's size (owner's pick "A: flat on a post", reference picture owner-2159, "make the case look extra good").

Units mm. Z up, bottom of the case at Z = 0. The ring stands with its band axis vertical, around a centre post; its block hangs
in a pocket beside the post; a domed cap lid swivels aside on a hidden pin. Four spring pins on the post's pin lug touch the four
pads on the INSIDE of the band (opposite the block). The band is clamped between the pins (inside) and two flat flanks of a V wall
(outside), so one post serves US 7 to 13 (numbers in out/case_params.json "pin_travel").

C5 changes the OUTSIDE only (mechanics and electronics layout as C4): the outside is one smooth skin, the soft pebble of look/pebble.py:
a tapered superellipse plan (no straight segment) scaled by a profile that runs from the top dome through the widest line to a crowned
base (one loft surface, no planar face). The seam is the plane z = z_split (shell top) and z_lid0 (lid underside), 0.3 mm apart.

Ring: design/look/s1/out/ring-merged32e.step (US 9, read only). Other sizes are COMPUTED: the block, glass and joystick of the US 9
file are kept, the band is a new tube with the bore of sizes.csv (bore 17.32 to 22.20 mm, band 2.6 mm thick), the joystick is moved radially.
Pads are computed too.

Writes out/parts/<name>.step (one per part), out/case_assembly_US9.step and .glb (one named node per part, plus the US 9 ring),
out/case_<printed part>.stl, out/case_params.json, out/case_size.txt.
"""
import copy
import csv
import glob
import json
import math
import os
import sys

import numpy as np
from build123d import (Axis, Box, Compound, Cylinder, Edge, Face, Pos, Rot, Solid, Sphere, Vector, Wire, export_gltf, export_step,
                       export_stl, fillet, import_step)
from matplotlib.path import Path as MPath
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.Approx import Approx_Centripetal
from OCP.BRepGProp import BRepGProp
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Pnt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "look"))
import pebble as PB  # noqa: E402

OUT = os.environ.get("CASE_OUT", os.path.join(HERE, "out"))   # CASE_OUT: another output folder (pitch sweep, broken copy)
PARTS = os.path.join(OUT, "parts")
RINGDIR = os.path.join(HERE, "..", "look", "s1", "out")
RING_STEP = os.path.join(RINGDIR, "ring-merged32e.step")
SIZES_CSV = os.path.join(RINGDIR, "sizes.csv")
SIZES = list(range(7, 14))

# ---------------- ring facts (ring file ring-merged32e, measures-merged32e.json) ----------------
ZC9, RI9 = -9.875, 9.475          # bore centre height and bore radius of the US 9 file (ring frame: X band axis, Z toward the block)
BAND_T = 2.6                      # band thickness (R0 - ri), same at every size
BAND_W = 8.0                      # band width along its axis
BLOCK_HALF = 14.65                # block half length along the band axis
JOY_ANGLE = 78.0                  # joystick nub at 78 degrees from the block side, on the -Y side
ZSPLIT_R = -1.5                   # ring frame Z above which the US 9 body is kept for the computed sizes

# ---------------- pads (inside face of the band, opposite the block) ----------------
PAD_NETS = ["VBUS", "D-", "D+", "GND"]
PAD_PITCH = float(os.environ.get("CASE_PAD_PITCH", "2.4"))                  # design/architecture.md 17.15: four discs 2.4 mm apart
PAD_D = 1.6                       # design/architecture.md 17.15: pad diameter 1.6
PAD_T = 0.1
PAD_X_OFF = -1.0                  # pad row 1.0 mm from the band's middle toward the light end (ring -X), parameter
# ---------------- pin (Harwin P70-6000045R, [LIST] proposed, not confirmed: conflict K1) ----------------
PIN = dict(free_h=2.80, work_h=2.10, plunger_d=0.60, barrel_d=1.50, barrel_h=1.85)
PIN_H_MIN, PIN_H_MAX = PIN["barrel_h"] + 0.30, PIN["free_h"] - 0.15
PIN_H0 = 2.35                     # design height at US 10 (middle of the window)
TIP_GAP = 0.03                    # modelled gap between pin tip and pad face (keeps boolean checks clean)
PIN_SHIFT_X = float(os.environ.get("CASE_PIN_SHIFT_X", "0.0"))                # fault-injection hook (case_check.py broken copy): moves all pins in X
# ---------------- V wall ----------------
PHI = 20.0                        # the band touches two flat flanks tangent at +-20 degrees from the pad direction
FLANK_GAP = 0.01
FLOOR_GAP = 0.01                  # modelled gap between band bottom and floor
RELIEF_Y = 10.4                   # pocket relief beside the band: the block flares into the band over 4 mm (junction blend)
FLANK_STRIP = (3.3, 5.8)          # |y| range of the flank strips
CLR = 0.3                         # clearance around the ring envelope (well)
POCKET_G = 0.15                   # pocket side clearance each side (block 14.75 wide)
# ---------------- shell ----------------
X_A = 0.0                         # x of the V apex line (all x follow from it)
WALL = 1.5
FT = 1.8                          # floor thickness under the band (shell 1.2 + soft finish 0.6)
ZP = 3.00                         # bottom plate: its top face (the pebble's base is crowned, so the plate is a shallow bowl)
CELL = dict(x=23.0, y=40.0, t=8.5)        # DNK852338 with PCM
PCB1 = dict(x=23.0, y=35.4, t=1.0)
CAV_YH = 20.35                    # underfloor cavity half width (cell 40.0 long + 0.35 each side)
LID_T = 4.0                       # lid thickness under the crown
LID_GAP = 0.3                     # the shadow gap of the seam (lid rides on 0.3 mm glides)
CEIL_CLR = 0.3                    # base rim above the ring's top
PIVOT_D = 3.0
LID_OPEN_TRY = (100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0, 170.0, 180.0)
SEAM_EDGE = 0.9                   # keep-out from the outline at the seam for pivot, magnet and glides
POCKET_RV = 1.2                   # pocket plan corner radius (the block's own corners are about this round)
POCKET_RB = 0.6                   # pocket bottom edge radius (side gap to the block is only 0.15 mm)
WELL_ROLL = 1.8                   # radius where the dish floor rolls into the wall
MAG_COVER = 0.5                   # skin over the base magnet, so the rim shows no hole
J1_LIP = 0.3                      # the USB-C mouth sits this far behind the skin at its centre
JY = 8.0                          # J1 y start (as C4)
J1_YC = JY + 8.94 / 2
LED_Y = 6.75                      # charge light beside the socket (between U1 and J1)
DOT_D = 1.0                       # the light's dot


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def cyl_z(x, y, z0, z1, d):
    return Pos(x, y, (z0 + z1) / 2) * Cylinder(d / 2, z1 - z0)


def cyl_x(x0, x1, y, z, d):
    return Pos((x0 + x1) / 2, y, z) * (Rot(0, 90, 0) * Cylinder(d / 2, x1 - x0))


def prism_xy(poly, z0, z1):
    face = Face(Wire.make_polygon([Vector(x, y, z0) for x, y in poly], close=True))
    return Solid.extrude(face, Vector(0, 0, z1 - z0))


def rbox(x0, x1, y0, y1, z0, z1, r_vert, r_all=0.0):
    """box with rounded vertical edges (r_vert) and, if r_all, all other edges rounded too (soft cutter)"""
    s = box(x0, x1, y0, y1, z0, z1)
    s = fillet(s.edges().filter_by(Axis.Z), r_vert)
    if r_all:
        horiz = [e for e in s.edges() if abs(e.bounding_box().size.Z) < 1e-6 or e.bounding_box().size.Z < (z1 - z0) - 1e-6]
        s = fillet(horiz, r_all)
    return s


def vol(shape):
    g = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, g)
    return g.Mass()


def common(a, b):
    ba, bb = a.bounding_box(), b.bounding_box()
    if (ba.max.X < bb.min.X or bb.max.X < ba.min.X or ba.max.Y < bb.min.Y or bb.max.Y < ba.min.Y
            or ba.max.Z < bb.min.Z or bb.max.Z < ba.min.Z):
        return 0.0
    op = BRepAlgoAPI_Common(a.wrapped, b.wrapped)
    op.Build()
    return vol(op.Shape()) if op.IsDone() else float("nan")


def hull2d(pts):
    pts = sorted(set(map(tuple, pts)))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo = []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    up = []
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def dilate(poly, r, n=24):
    pts = []
    for (x, y) in poly:
        for k in range(n):
            a = 2 * math.pi * k / n
            pts.append((round(x + r * math.cos(a), 4), round(y + r * math.sin(a), 4)))
    return hull2d(pts)


# ---------------- ring family ----------------
def bores():
    out = {}
    with open(SIZES_CSV) as f:
        for r in csv.DictReader(f):
            out[int(r["us_size"])] = float(r["bore_mm"])
    return out


BORE = bores()


def ri_of(n):
    return RI9 + (BORE[n] - BORE[9]) / 2.0          # US 9 keeps the file's own bore radius 9.475


def r0_of(n):
    return ri_of(n) + BAND_T


def zc_of(n):
    return ZC9 - (ri_of(n) - RI9)                   # the block is fixed to the top of the band: the centre moves down as the bore grows


COSPHI = math.cos(math.radians(PHI))
TANPHI = math.tan(math.radians(PHI))


def cx_of(n):
    """x of the bore centre: the band rests on the two flanks, so the centre is R0 / cos(phi) from the apex line."""
    return X_A + r0_of(n) / COSPHI


def pad_angles(n, pitch=None):
    p = PAD_PITCH if pitch is None else pitch
    ri = ri_of(n)
    return [(k * p) / ri for k in (-1.5, -0.5, 0.5, 1.5)]


def pad_face_xy(n, k, pitch=None):
    """Pad k face centre in the case frame (x, y): on the inner face, angle theta from the pad direction (-X)."""
    th = pad_angles(n, pitch)[k]
    ri = ri_of(n)
    return cx_of(n) - ri * math.cos(th), ri * math.sin(th)


class Ring:
    """Ring of size n in the ring frame (X band axis, Y across, Z toward the block), plus its placement into the case."""

    def __init__(self, n, base):
        self.n = n
        d = ri_of(n) - RI9
        zc = zc_of(n)
        self.ri, self.r0, self.zc, self.d = ri_of(n), r0_of(n), zc, d
        ch = base
        if n == 9:
            self.body = ch["body"]
        else:
            upper = ch["body"] & box(-20, 20, -20, 20, ZSPLIT_R, 10)
            tube = cyl_x(-BAND_W / 2, BAND_W / 2, 0, zc, 2 * self.r0)
            bore = cyl_x(-BAND_W / 2 - 0.01, BAND_W / 2 + 0.01, 0, zc, 2 * self.ri)
            self.body = (upper + tube) - bore
        self.glass = ch["glass"]
        s = math.radians(JOY_ANGLE)
        self.joystick = Pos(0, -math.sin(s) * d, -d + math.cos(s) * d) * ch["joystick"]
        self.pads = self._pads()

    def _pads(self):
        out = None
        for k, th in enumerate(pad_angles(self.n)):
            r = self.ri + PAD_T / 2
            y, z = r * math.sin(th), self.zc - r * math.cos(th)
            p = Pos(PAD_X_OFF, y, z) * (Rot(180.0 + math.degrees(th), 0, 0) * Cylinder(PAD_D / 2, PAD_T))
            out = p if out is None else out + p
        return out

    def place(self, shape, zb):
        return Pos(cx_of(self.n), 0, zb) * (Rot(0, 90, 0) * (Pos(0, 0, -self.zc) * shape))

    def parts_in_case(self, zb):
        return {"body": self.place(self.body, zb), "glass": self.place(self.glass, zb),
                "joystick": self.place(self.joystick, zb), "pads": self.place(self.pads, zb)}


def load_base():
    r = import_step(RING_STEP)
    return {c.label: c for c in r.children}


def simplify_convex(poly, turn_deg=4.0, max_len=10.0):
    """thin a convex polygon: keep a vertex when the direction has turned turn_deg since the last kept one or the run is max_len long"""
    P = np.array(poly, float)
    m = len(P)
    ang = np.arctan2(np.roll(P, -1, 0)[:, 1] - P[:, 1], np.roll(P, -1, 0)[:, 0] - P[:, 0])
    keep = [0]
    a0, l = ang[0], 0.0
    for i in range(1, m):
        l += float(np.hypot(*(P[i] - P[i - 1])))
        da = abs((ang[i] - a0 + math.pi) % (2 * math.pi) - math.pi)
        if da >= math.radians(turn_deg) or l >= max_len:
            keep.append(i)
            a0, l = ang[i], 0.0
    return P[keep]


def rolled_prism(poly, z0, z1, R, n=9):
    """convex polygon prism whose bottom edge is a quarter circle of radius R (a ruled loft through n insets): the dish floor rolling into the wall"""
    P = simplify_convex(poly)
    m = len(P)
    # outward vertex normals of the convex polygon (counter-clockwise from hull2d)
    e = np.roll(P, -1, 0) - P
    nrm = np.stack([e[:, 1], -e[:, 0]], 1)
    nrm /= np.linalg.norm(nrm, axis=1)[:, None]
    vn = nrm + np.roll(nrm, 1, 0)
    vn /= np.linalg.norm(vn, axis=1)[:, None]
    ts = BRepOffsetAPI_ThruSections(True, True, 1e-6)
    for i in range(n):
        phi = (math.pi / 2) * i / (n - 1)
        d, z = R * (1 - math.sin(phi)), z0 + R * (1 - math.cos(phi))
        Q = P - vn * d
        ts.AddWire(Wire.make_polygon([Vector(float(x), float(y), z) for x, y in Q], close=True).wrapped)
    ts.AddWire(Wire.make_polygon([Vector(float(x), float(y), z1) for x, y in P], close=True).wrapped)
    ts.Build()
    return Solid(ts.Shape()).fix()


# ---------------- the pebble skin ----------------
def pebble_solid(H, npts=96, n_low=30, n_up=32):
    """The outer skin as one solid: a loft through scaled copies of the plan (look/pebble.py), the two poles as points.
    No planar face: base and lid top are crowned."""
    ts = BRepOffsetAPI_ThruSections(True, False, 1e-6)
    ts.SetMaxDegree(3)
    for z, r in PB.sections(H, n_low, n_up):
        if r == 0.0:
            ts.AddVertex(BRepBuilderAPI_MakeVertex(gp_Pnt(PB.PEB["XC"], 0, z)).Vertex())
        else:
            xx, yy = PB.outline_at(r, npts)
            ts.AddWire(Wire([Edge.make_spline([Vector(a, b, z) for a, b in zip(xx, yy)], periodic=True)]).wrapped)
    ts.Build()
    return Solid(ts.Shape())


def skin_part(H, z0, z1, npts=96, nmax=34):
    """the part of the skin between the planes z0 and z1 as one loft with planar end faces (no boolean on the skin): z0 = 0 and z1 = H end in the poles"""
    lo_m, hi_m = (0.15 if z0 > 0 else 0.0), (0.15 if z1 < H else 0.0)
    mid = [(z, r) for z, r in PB.sections(H) if z0 + lo_m < z < z1 - hi_m and 0.0 < r and not (r > 0.9999 and (z < z0 + 0.6 or z > z1 - 0.6))]
    secs = [(z0, 0.0 if z0 <= 0 else float(PB.rho_of_z(z0, H)))] + mid + [(z1, 0.0 if z1 >= H else float(PB.rho_of_z(z1, H)))]
    ts = BRepOffsetAPI_ThruSections(True, False, 1e-6)
    ts.SetMaxDegree(3)
    ts.SetParType(Approx_Centripetal)
    for z, r in secs:
        if r == 0.0:
            ts.AddVertex(BRepBuilderAPI_MakeVertex(gp_Pnt(PB.PEB["XC"], 0, z)).Vertex())
        else:
            xx, yy = PB.outline_at(r, npts)
            ts.AddWire(Wire([Edge.make_spline([Vector(a, b, z) for a, b in zip(xx, yy)], periodic=True)]).wrapped)
    ts.Build()
    return Solid(ts.Shape()).fix()


def skin_x_left_range(y0, y1, z, H, n=9):
    """(smallest, largest) x of the -X skin over y in [y0, y1] at height z"""
    xs = [skin_x_left(y, z, H) for y in np.linspace(y0, y1, n)]
    return min(xs), max(xs)


def rrect_pts(x, yc, zc, w, h, r, n=8):
    """rounded rectangle (w wide in Y, h high in Z, corner radius r) in the plane x, as 3D points"""
    pts = []
    for cy, cz, a0 in ((w / 2 - r, h / 2 - r, 0), (-(w / 2 - r), h / 2 - r, 90), (-(w / 2 - r), -(h / 2 - r), 180), (w / 2 - r, -(h / 2 - r), 270)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append(Vector(x, yc + cy + r * math.cos(a), zc + cz + r * math.sin(a)))
    return pts


def mouth_cutter(x_out, x_in, x_full, yc, zc, w, h, r, grow):
    """USB-C mouth: a curved lead-in flare (grows by `grow` mm per side at x_out, three sections, smooth) that narrows to the slot (w x h, radius r) at
    x_full, then the straight slot (an exact prism) to x_in"""
    ts = BRepOffsetAPI_ThruSections(True, False, 1e-6)          # smooth (not ruled): the lead-in is a curved flare, not flat facets
    ts.SetMaxDegree(2)
    x_mid = 0.5 * (x_out + x_full)
    for x, g in ((x_out, grow), (x_mid, 0.40 * grow), (x_full, 0.0)):
        ts.AddWire(Wire.make_polygon(rrect_pts(x, yc, zc, w + 2 * g, h + 2 * g, r + g), close=True).wrapped)
    ts.Build()
    flare = Solid(ts.Shape()).fix()
    slot = Solid.extrude(Face(Wire.make_polygon(rrect_pts(x_full, yc, zc, w, h, r), close=True)), Vector(x_in - x_full, 0, 0))
    return flare + slot


def skin_x_left(y, z, H):
    """x of the skin on the -X side at (y, z)"""
    ox, oy = PB.outline_at(float(PB.rho_of_z(z, H)), 3000)
    best = None
    for i in range(len(ox)):
        j = (i + 1) % len(ox)
        if (oy[i] - y) * (oy[j] - y) <= 0 and oy[i] != oy[j]:
            x = ox[i] + (ox[j] - ox[i]) * (y - oy[i]) / (oy[j] - oy[i])
            best = x if best is None else min(best, x)
    return best


def seg_dist(P, poly):
    """distance from points P (n,2) to the closed polyline poly (m,2)"""
    A = np.asarray(poly)
    B = np.roll(A, -1, axis=0)
    AB = B - A
    L2 = (AB ** 2).sum(1)
    out = np.full(len(P), 1e9)
    for a, ab, l2 in zip(A, AB, L2):
        t = np.clip(((P - a) @ ab) / max(l2, 1e-12), 0, 1)
        d = np.hypot(*(P - (a + t[:, None] * ab)).T)
        out = np.minimum(out, d)
    return out


def inside(P, poly):
    return MPath(np.asarray(poly)).contains_points(P)


def seam_layout(H, z_split, z_lid0, hull_w, pocket_rect, notch_rect, relief_rect):
    """Pivot, open angle, magnet and glide places at the seam plane (2D, numpy): all inside the seam outline by SEAM_EDGE plus their radius,
    clear of the well, pocket, relief and notch; lid thick enough there; the lid footprint turned about the pivot clears the well and pocket."""
    rs, rl = float(PB.rho_of_z(z_split, H)), float(PB.rho_of_z(z_lid0, H))
    seam = np.array(PB.outline_at(rs, 360)).T
    lidfp = np.array(PB.outline_at(rl, 360)).T
    cuts = [np.array(hull_w), np.array(relief_rect), np.array(notch_rect)]
    xs = np.arange(seam[:, 0].min(), seam[:, 0].max(), 0.6)
    ys = np.arange(seam[:, 1].min(), seam[:, 1].max(), 0.6)
    G = np.array([(x, y) for x in xs for y in ys])
    ins = inside(G, seam)
    G = G[ins]
    d_out = seg_dist(G, seam)
    d_cut = np.full(len(G), 1e9)
    for c in cuts:
        d = seg_dist(G, c)
        d_cut = np.minimum(d_cut, np.where(inside(G, c), -d, d))
    # lid thickness at each place: crown height minus the underside
    thick = np.array([float(PB.z_upper_of_rho(PB.rho_point(x, y), H)) - z_lid0 for x, y in G])

    def ok(r, tmin):
        return (d_out >= r + SEAM_EDGE) & (d_cut >= r + 0.7) & (thick >= tmin)

    # lid footprint sample (grid inside the lid outline)
    fx = np.arange(lidfp[:, 0].min(), lidfp[:, 0].max(), 1.0)
    fy = np.arange(lidfp[:, 1].min(), lidfp[:, 1].max(), 1.0)
    F = np.array([(x, y) for x in fx for y in fy])
    F = F[inside(F, lidfp)]
    F = np.vstack([F, lidfp])
    hullp = MPath(np.array(hull_w))
    pk = MPath(np.array(pocket_rect))
    best = None
    cand = np.where(ok(1.9, 2.2))[0]
    for ang in LID_OPEN_TRY:
        a = math.radians(ang)
        R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
        for i in cand:
            p = G[i]
            Q = (F - p) @ R.T + p
            hit = hullp.contains_points(Q).any() or pk.contains_points(Q).any()
            if not hit:
                # margin: the rotated outline stays 0.3 from the well and pocket polygons
                m = min(seg_dist(Q[-len(lidfp):], np.array(hull_w)).min(), seg_dist(Q[-len(lidfp):], np.array(pocket_rect)).min())
                if m >= 0.3 and (best is None or best[0] > ang or (best[0] == ang and m > best[3])):
                    best = (ang, tuple(p), i, m)
        if best is not None:
            break
    if best is None:
        raise RuntimeError("no pivot place found for the lid")
    ang, piv, ip, marg = best
    out = dict(open_deg=ang, pivot=piv, pivot_margin=marg)
    chosen = [piv]

    def far(r, tmin):
        idx = np.where(ok(r, tmin))[0]
        dmin = np.min([np.hypot(*(G[idx] - c).T) for c in chosen], axis=0)
        k = int(np.argmax(dmin))
        return tuple(G[idx[k]])
    mag = far(2.1, 2.2)
    chosen.append(mag)
    glides = []
    for _ in range(3):
        g = far(2.0, 0.0)
        glides.append(g)
        chosen.append(g)
    out.update(magnet=mag, glides=glides)
    return out


# ---------------- build ----------------
def build(pitch=None, pin_shift=None):
    shift = PIN_SHIFT_X if pin_shift is None else pin_shift
    base = load_base()
    rings = {n: Ring(n, base) for n in SIZES}
    # ---- vertical levels
    cell_z0 = ZP + 0.4                                         # cell 0.4 above the bottom plate
    pcb1_z0 = cell_z0 + CELL["t"] + 0.3                        # PCB1 above the cell
    pcb1_z1 = pcb1_z0 + PCB1["t"]
    j1_top = pcb1_z1 + 3.31
    zf = round(j1_top + 0.3 + FT + 0.05, 1)                    # band floor
    zb = zf + BAND_W / 2 + FLOOR_GAP                           # band centre height (the band floats FLOOR_GAP above the floor)
    block_top = zb + BLOCK_HALF
    z_split = round(block_top + CEIL_CLR, 2)                   # base rim: the seam plane of the shell
    z_lid0 = round(z_split + LID_GAP, 2)                       # lid underside
    H = PB.PEB["H"]                                           # top of the crown (size limit of the brief)

    # ---- block silhouette in the case frame (size independent in the ring frame)
    blk = base["body"] & (box(-20, -BAND_W / 2 - 0.01, -20, 20, -20, 10) + box(BAND_W / 2 + 0.01, 20, -20, 20, -20, 10))
    bb = blk.bounding_box()
    gb = base["glass"].bounding_box()
    by0, by1 = min(bb.min.Y, gb.min.Y), max(bb.max.Y, gb.max.Y)
    bz0, bz1 = min(bb.min.Z, gb.min.Z), max(bb.max.Z, gb.max.Z)            # ring frame Z of the block's extent
    blk_x = [(cx_of(n) + (bz0 - zc_of(n)), cx_of(n) + (bz1 - zc_of(n))) for n in SIZES]
    px0 = min(a for a, b in blk_x) - 0.3
    px1 = max(b for a, b in blk_x) + 0.3
    py0, py1 = by0 - POCKET_G, by1 + POCKET_G

    # ---- well hull (band outer circle + joystick, every size, dilated by CLR)
    pts = []
    jv, _ = base["joystick"].tessellate(0.05)
    s = math.radians(JOY_ANGLE)
    for n in SIZES:
        c, r0, d = cx_of(n), r0_of(n), ri_of(n) - RI9
        for k in range(120):
            a = 2 * math.pi * k / 120
            pts.append((round(c + r0 * math.cos(a), 3), round(r0 * math.sin(a), 3)))
        for v in jv:
            y, z = v.Y - math.sin(s) * d, v.Z - d + math.cos(s) * d
            pts.append((round(c + (z - zc_of(n)), 3), round(y, 3)))
    hull_w = dilate(hull2d(pts), CLR)

    # ---- layout anchors (as C4: the cell sits left of the pocket wall; the electronics follow the cell)
    cell_x1 = px0 - WALL - 0.3
    x_c0 = cell_x1 - CELL["x"]
    x_lay = x_c0 - 3.8                                          # C4's left layout anchor (board, cavity), kept
    # ---- the outside skin
    plate = skin_part(H, 0.0, ZP)
    shell = skin_part(H, ZP, z_split)
    lid_blank = skin_part(H, z_lid0, H)
    print('skin bbox z', [(round(p.bounding_box().min.Z,2), round(p.bounding_box().max.Z,2)) for p in (plate, shell, lid_blank)], flush=True)
    print('skin parts: plate %.0f, shell blank %.0f, lid blank %.0f mm3, valid %s' % (plate.volume, shell.volume, lid_blank.volume, (plate.is_valid, shell.is_valid, lid_blank.is_valid)), flush=True)

    # ---- USB-C and light: the socket mouth sits J1_LIP behind the skin at its centre
    zj = pcb1_z1 + 3.31 / 2
    xs_min, xs_j = skin_x_left_range(JY, JY + 8.94, zj, H)      # the socket front sits J1_LIP behind the skin at the socket's outermost corner
    jx0 = xs_j + J1_LIP
    pcb1_x0 = x_lay + 1.9

    # ---- cuts
    strips = None
    xfar = X_A - 25.0
    for sg in (1, -1):
        y0, y1 = FLANK_STRIP
        xa_m = X_A - FLANK_GAP / COSPHI
        poly = [(xa_m + y0 * TANPHI, sg * y0), (xa_m + y1 * TANPHI, sg * y1), (xfar, sg * y1), (xfar, sg * y0)]
        st = prism_xy(poly, zf - 1, z_split + 2)
        strips = st if strips is None else strips + st
    well0 = rolled_prism(dilate(hull2d(hull_w), WELL_ROLL, 36), zf, z_split + 2, WELL_ROLL)        # the dish rolls into the wall
    well = well0 - strips
    pocket = rbox(px0, px1, py0, py1, zb - BLOCK_HALF - 0.4, z_split + 2, POCKET_RV, POCKET_RB)          # soft pocket: rounded corners and bottom edges
    relief = box(px0, px1, -RELIEF_Y, RELIEF_Y, zb - 8.6, zb - BAND_W / 2 - 0.05) + box(px0, px1, -RELIEF_Y, RELIEF_Y, zb + BAND_W / 2 + 0.05, zb + 8.6)
    notch_y = py1 + 2.0
    notch = rbox(px0 + 1.0, px1 - 1.0, -notch_y, notch_y, block_top - 7.0, z_split + 2, 2.0, 1.5)
    cav_x0, cav_x1 = x_lay + 1.5, cell_x1 + 0.6
    uf = rbox(cav_x0, cav_x1, -CAV_YH, CAV_YH, ZP - 0.01, zf - FT, 0.5)
    # electronics volumes
    cell = box(x_c0, x_c0 + CELL["x"], -CELL["y"] / 2, CELL["y"] / 2, cell_z0, cell_z0 + CELL["t"])
    pcb1 = box(pcb1_x0, pcb1_x0 + PCB1["x"], -PCB1["y"] / 2, PCB1["y"] / 2, pcb1_z0, pcb1_z1)
    top = pcb1_z1
    p = {}
    j1 = box(jx0, jx0 + 7.35, JY, JY + 8.94, top, top + 3.31)
    tab = box(jx0 + 1.6, pcb1_x0 + 0.5, JY, JY + 8.94, pcb1_z0, pcb1_z1) if jx0 + 1.6 < pcb1_x0 else None
    p["main_board"] = pcb1 + tab if tab is not None else pcb1                 # a tab under the socket carries it out to the skin
    p["cell_dnk852338"] = cell
    p["U1_esp32s3_mini1"] = box(pcb1_x0 + 0.6, pcb1_x0 + 0.6 + 15.4, -15.0, 5.5, top, top + 2.4)
    p["J1_usb4105"] = j1
    p["LED1"] = box(pcb1_x0 + 0.6, pcb1_x0 + 0.6 + 1.6, LED_Y - 0.8, LED_Y + 0.8, top, top + 0.7)
    sx = pcb1_x0 + 0.6 + 15.4 + 0.8
    p["U2_bq25895"] = box(sx, sx + 4.0, -16.0, -12.0, top, top + 0.8)
    p["L1_1uH"] = box(sx, sx + 4.2, -10.5, -6.3, top, top + 2.0)
    p["U3_tps63802"] = box(sx, sx + 3.0, -4.5, -2.5, top, top + 0.8)
    p["L2_0u47"] = box(sx, sx + 4.0, -1.0, 3.0, top, top + 1.5)
    p["U5_tps2553"] = box(sx, sx + 2.9, 5.0, 6.6, top, top + 1.0)
    p["U4_zdsd64g"] = box(pcb1_x0 + 7.0, pcb1_x0 + 16.0, 6.0, 16.0, top, top + 1.0)

    # ---- post with pin lug
    xbk = [pad_face_xy(10, k, pitch)[0] + PIN_H0 for k in range(4)]
    ypin = pin_ys(pitch)
    x_b = xbk[1]
    x_bo = xbk[0]
    z_pin = zb - PAD_X_OFF
    post_cx = X_A + (r0_of(7) + r0_of(13)) / 2 / COSPHI
    post_r = 6.0
    post_top = zb + 3.5
    post = cyl_z(post_cx, 0, zf, post_top, 2 * post_r)
    post = fillet(post.edges().filter_by_position(Axis.Z, post_top - 0.01, post_top + 0.01), 1.2)
    lug_hy, lug_z0, lug_z1 = 5.5, zb - 3.0, post_top
    lug = box(x_b + 0.8, post_cx - post_r + 1.5, -2.0, 2.0, lug_z0, lug_z1) + box(x_bo + 0.8, post_cx - post_r + 1.5, -lug_hy, lug_hy, lug_z0, lug_z1)
    post = post + lug
    p["post"] = post
    p["pin_board_pcb2"] = box(x_b, x_b + 0.8, -1.95, 1.95, z_pin - 2.5, z_pin + 2.5)
    p["pin_board_pcb2_wing_L"] = box(x_bo, x_bo + 0.8, -4.9, -2.05, z_pin - 2.5, z_pin + 2.5)
    p["pin_board_pcb2_wing_R"] = box(x_bo, x_bo + 0.8, 2.05, 4.9, z_pin - 2.5, z_pin + 2.5)
    for k in range(4):
        h = xbk[k] - pad_face_xy(9, k, pitch)[0] - TIP_GAP        # modelled at contact with the US 9 pad
        p[f"pin_P{k+1}_{PAD_NETS[k]}"] = make_pin(xbk[k] + shift, ypin[k], z_pin, h)
    slot = box(x_b + 1.0, x_b + 4.0, -4.0, 4.0, zf - FT - 0.01, zf + 0.01)

    # ---- seam layout: pivot, magnet, glides (2D at the seam plane)
    pocket_rect = [(px0 - 0.3, py0 - 0.3), (px1 + 0.3, py0 - 0.3), (px1 + 0.3, py1 + 0.3), (px0 - 0.3, py1 + 0.3)]
    relief_rect = [(px0, -RELIEF_Y), (px1, -RELIEF_Y), (px1, RELIEF_Y), (px0, RELIEF_Y)]
    notch_rect = [(px0 + 1.0, -notch_y), (px1 - 1.0, -notch_y), (px1 - 1.0, notch_y), (px0 + 1.0, notch_y)]
    lay = seam_layout(H, z_split, z_lid0, hull_w, pocket_rect, notch_rect, relief_rect)
    pivx, pivy = lay["pivot"]
    mx, my = lay["magnet"]
    z_top_piv = float(PB.z_upper_of_rho(PB.rho_point(pivx, pivy), H))
    pin_top = z_top_piv - 1.3

    # ---- apply cuts to the shell
    cuts = [well, pocket, relief, notch, uf, slot]
    usb = mouth_cutter(xs_min - 1.0, cav_x0 + 0.01, xs_j + 0.2, J1_YC, zj, 8.94 + 1.2, 3.31 + 1.2, 0.9, 0.9)
    led = cyl_x(xs_min - 3.0, cav_x0 + 0.01, LED_Y, top + 0.35, DOT_D)
    tabcut = box(jx0 + 1.2, cav_x0 + 0.01, JY - 0.35, JY + 8.94 + 0.35, pcb1_z0 - 0.35, top + 0.4)          # channel for the board tab that carries the socket
    cuts += [usb, led, tabcut]
    cuts.append(cyl_z(pivx, pivy, z_split - 7.0, z_split + 0.5, PIVOT_D + 0.2))
    cuts.append(cyl_z(mx, my, z_split - 2.2, z_split - MAG_COVER, 4.2))
    for i_c, c in enumerate(cuts):
        print('cutter', i_c, type(c).__name__, c.is_valid, flush=True)
        shell = shell - c
        print('  shell after', i_c, type(shell).__name__, shell.is_valid, len(shell.solids()), flush=True)
    p["shell"] = shell
    p["base_plate"] = plate
    # ---- lid: the domed cap above the seam
    lid = lid_blank
    lid = lid - cyl_z(pivx, pivy, z_lid0 - 0.1, pin_top + 0.1, PIVOT_D + 0.2) - cyl_z(mx, my, z_lid0 - 0.1, z_lid0 + 1.6, 4.2)
    p["lid"] = lid
    p["hinge_pivot"] = cyl_z(pivx, pivy, z_split - 6.9, pin_top, PIVOT_D)
    p["magnet_base"] = cyl_z(mx, my, z_split - 2.1, z_split - MAG_COVER - 0.1, 4.0)
    p["magnet_lid"] = cyl_z(mx, my, z_lid0, z_lid0 + 1.5, 4.0)
    gl = [(pivx, pivy)] + list(lay["glides"])
    for i, (gx, gy) in enumerate(gl, 1):
        g = cyl_z(gx, gy, z_split, z_lid0, 5.0 if i == 1 else 4.0)
        if i == 1:
            g = g - cyl_z(gx, gy, z_split - 0.1, z_lid0 + 0.1, PIVOT_D + 0.4)      # washer around the pivot pin
        p[f"glide_{i}"] = g
    outl = np.array(PB.outline_at(1.0, 720))
    meta = dict(xb=xbk, x_bo=x_bo, zf=zf, zb=zb, z_split=z_split, z_lid0=z_lid0, h_tot=H, x_min=float(outl[0].min()), x_max=float(outl[0].max()),
                y_half=float(outl[1].max()), px0=px0, px1=px1, py0=py0, py1=py1, x_b=x_b, ypin=ypin, z_pin=z_pin, post_cx=post_cx, post_r=post_r,
                pivot=(pivx, pivy), magnet=(mx, my), cell_x0=x_c0, pcb1_x0=pcb1_x0, hull_w=hull_w, glides=gl, block_top=block_top,
                pcb1_z=(pcb1_z0, pcb1_z1), zp=ZP, x_lay=x_lay, lid_open_deg=lay["open_deg"], pivot_margin=lay["pivot_margin"],
                j1_front=jx0, skin_x_at_j1=xs_j, pin_top=pin_top, pebble=PB.PEB)
    return p, rings, meta


def pin_ys(pitch=None):
    """Pin y positions: the pad y of the middle size (US 10) for each pin (pads sit at ri sin(theta); the pin row is straight)."""
    out = []
    for k in range(4):
        out.append(round(pad_face_xy(10, k, pitch)[1], 3))
    return out


def make_pin(xb, y, z, h):
    """Pin axis along X, base plane at x = xb, tip pole at x = xb - h; barrel 1.85 long, plunger 0.6, dome 0.3 radius."""
    r = PIN["plunger_d"] / 2
    barrel = cyl_x(xb - PIN["barrel_h"], xb, y, z, PIN["barrel_d"])
    dome = Pos(xb - h + r, y, z) * Sphere(r)
    ln = (xb - PIN["barrel_h"] + 0.01) - (xb - h + r)
    if ln > 0.02:
        return barrel + cyl_x(xb - h + r, xb - PIN["barrel_h"] + 0.01, y, z, PIN["plunger_d"]) + dome
    return barrel + dome


def size_text(parts):
    names = ("shell", "base_plate", "lid", "hinge_pivot")
    bb = Compound(children=[parts[n] for n in names]).bounding_box()
    return bb, (f"closed case outer size X {bb.size.X:.1f} mm x Y {bb.size.Y:.1f} mm x Z {bb.size.Z:.1f} mm "
                f"(X {bb.min.X:.2f} to {bb.max.X:.2f}, Y {bb.min.Y:.2f} to {bb.max.Y:.2f}, Z {bb.min.Z:.2f} to {bb.max.Z:.2f}); "
                f"volume of the box {bb.size.X*bb.size.Y*bb.size.Z/1000:.1f} cm3")


def pin_heights(parts, rings, meta, n):
    """Pin extension (height from the base plane to the pad face) of every pin at size n: x_b - pad face x."""
    return [meta["xb"][k] - pad_face_xy(n, k)[0] for k in range(4)]


def main():
    os.makedirs(PARTS, exist_ok=True)
    for f in glob.glob(os.path.join(PARTS, "*.step")):
        os.remove(f)                                   # C3 parts are kept in out/old_C3/parts
    parts, rings, meta = build()
    for name, shp in parts.items():
        export_step(shp, os.path.join(PARTS, f"{name}.step"))
    ring9 = rings[9].parts_in_case(meta["zb"])
    kids = []
    for k, v in ring9.items():
        v.label = f"ring_US9_{k}"
        kids.append(v)
    nodes = []
    for name, shp in parts.items():
        s = copy.copy(shp)          # C4 used shp.moved(shp.location), which applied every part's location twice in the assembly
        s.label = name
        nodes.append(s)
    nodes.append(Compound(children=kids, label="ring_US9"))
    asm = Compound(children=nodes, label="case_assembly_US9")
    export_step(asm, os.path.join(OUT, "case_assembly_US9.step"))
    export_gltf(asm, os.path.join(OUT, "case_assembly_US9.glb"), binary=True)
    for n in ("shell", "base_plate", "lid", "post", "hinge_pivot"):
        export_stl(parts[n], os.path.join(OUT, f"case_{n}.stl"))
    bb, txt = size_text(parts)
    with open(os.path.join(OUT, "case_size.txt"), "w") as f:
        f.write(txt + "\n")
    hts = {n: pin_heights(parts, rings, meta, n) for n in SIZES}
    allh = [h for v in hts.values() for h in v]
    params = dict(
        pin=PIN, pin_window=[PIN_H_MIN, PIN_H_MAX], pad_pitch=PAD_PITCH, pad_d=PAD_D, pad_x_off=PAD_X_OFF, pad_nets=PAD_NETS,
        tip_gap=TIP_GAP, phi=PHI, flank_gap=FLANK_GAP, sizes=SIZES, ri={n: ri_of(n) for n in SIZES}, r0={n: r0_of(n) for n in SIZES},
        zc={n: zc_of(n) for n in SIZES}, cx={n: cx_of(n) for n in SIZES}, x_a=X_A,
        pin_heights={str(n): hts[n] for n in SIZES},
        pin_travel=dict(min_height=min(allh), max_height=max(allh), spread=max(allh) - min(allh),
                        needed_stroke=max(allh) - min(allh) + 0.2),
        parts=sorted(parts), size_box=[bb.size.X, bb.size.Y, bb.size.Z], clearance=CLR, pocket_g=POCKET_G,
        lid_gap=LID_GAP, **meta,
    )
    with open(os.path.join(OUT, "case_params.json"), "w") as f:
        json.dump(params, f, indent=1, default=float)
    print(txt)
    print("parts:", len(parts), "; valid solids: " + ", ".join(f"{k} {parts[k].is_valid}" for k in ("shell", "lid", "base_plate")))
    print("pin heights spread %.3f mm (window %.2f to %.2f)" % (max(allh) - min(allh), PIN_H_MIN, PIN_H_MAX))
    print("lid opens %.0f degrees; pivot %.2f, %.2f; J1 front %.2f behind skin %.2f" % (meta["lid_open_deg"], *meta["pivot"], meta["j1_front"], meta["skin_x_at_j1"]))
    print("case.py done")


if __name__ == "__main__":
    main()
