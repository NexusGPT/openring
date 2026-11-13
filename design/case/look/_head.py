"""Ring charging case, version C4: the pebble (owner's pick "A: flat on a post", reference picture owner-2159).

Units mm. Z up, bottom of the case at Z = 0. The ring stands with its band axis vertical, around a centre post; its block hangs
in a pocket beside the post; a flat cap lid swivels aside on a corner pin. Four spring pins on the post's pin lug touch the four
pads on the INSIDE of the band (opposite the block). The band is clamped between the pins (inside) and two flat flanks of a V wall
(outside), so one post serves US 7 to 13: the band is 2.6 mm thick at every size, the V wall puts the pad row within 0.157 mm
of the same place for every size, and the pin travel takes up the rest (numbers in out/case_params.json "pin_travel").

Ring: design/look/s1/out/ring-merged32e.step (US 9, read only). Other sizes are COMPUTED: the block, glass and joystick of the US 9
file are kept (the block is fixed to the top of the band), the band is a new tube with the bore of sizes.csv (bore 17.32 to 22.20 mm,
band 2.6 mm thick), the joystick is moved radially. Pads are computed too (the file's own contacts are the old outside ones).

Writes out/parts/<name>.step (one per part), out/case_assembly_US9.step and .glb (one named node per part, plus the US 9 ring),
out/case_<printed part>.stl, out/case_params.json, out/case_size.txt.
"""
import csv
import glob
import json
import math
import os

import numpy as np
from build123d import (Axis, Box, Compound, Cylinder, Face, Pos, Rot, Solid, Sphere, Vector, Wire, export_gltf, export_step,
                       export_stl, fillet, import_step)
from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

HERE = os.path.dirname(os.path.abspath(__file__))
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
PAD_PITCH = float(os.environ.get("CASE_PAD_PITCH", "2.0"))                  # parameter: arc pitch at the band's inner radius (mm); the inside model fixes the final value
PAD_D = 1.0                       # parameter: pad diameter
PAD_T = 0.1
PAD_X_OFF = -1.0                  # pad row 1.0 mm from the band's middle toward the light end (ring -X), parameter
# ---------------- pin (Harwin P70-6000045R, [LIST] proposed, not confirmed: conflict K1) ----------------
PIN = dict(free_h=2.80, work_h=2.10, plunger_d=0.60, barrel_d=1.50, barrel_h=1.85)
# my assumption for the contact window (stroke is not in the file read): the plunger may be pushed from 0.15 to 0.90 mm
# below its free height; fully pushed in it is flush with the 1.85 barrel (travel 0.95).
# Lower end: the barrel's edge must clear the concave pad row (sag 0.29 mm at 0.75 mm off a pad centre on US 7): 1.85 + 0.30.
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
PLATE_T = 1.5                     # bottom plate
Y_HALF = 22.0                     # outer half width (cell 40 long + 0.3 + wall 1.5 each side)
R_NEG, R_POS = 4.0, 14.0          # plan corner radii: -X corners (cell corners) / +X corners (pocket end)
R_TOP, R_BOT = 1.5, 2.5
CELL = dict(x=23.0, y=40.0, t=8.5)        # DNK852338 with PCM
PCB1 = dict(x=23.0, y=35.4, t=1.0)
LID_T = 4.0
LID_GAP = 0.4                     # the lid rides on three 0.4 mm glides: a constant shadow gap above the base
CEIL_CLR = 0.3                    # base rim above the ring's top
PIVOT_D = 3.0
GLIDE_D = 6.0
LID_OPEN_DEG = 100.0


def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def cyl_z(x, y, z0, z1, d):
    return Pos(x, y, (z0 + z1) / 2) * Cylinder(d / 2, z1 - z0)


def cyl_x(x0, x1, y, z, d):
    return Pos((x0 + x1) / 2, y, z) * (Rot(0, 90, 0) * Cylinder(d / 2, x1 - x0))


def prism_xy(poly, z0, z1):
    face = Face(Wire.make_polygon([Vector(x, y, z0) for x, y in poly], close=True))
    return Solid.extrude(face, Vector(0, 0, z1 - z0))


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


