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


# ---------------- pebble helper ----------------
def pebble(x0, x1, y0, y1, z0, z1, rn, rp, r_top=0.0, r_bot=0.0):
    s = box(x0, x1, y0, y1, z0, z1)
    xm = (x0 + x1) / 2
    vert = [e for e in s.edges() if abs(e.bounding_box().size.Z - (z1 - z0)) < 1e-6]
    for sel, rad in (([e for e in vert if e.center().X < xm], rn), ([e for e in vert if e.center().X >= xm], rp)):
        s = fillet(sel_edges(s, sel), rad)
        vert = [e for e in s.edges() if abs(e.bounding_box().size.Z - (z1 - z0)) < 1e-6]
    if r_top:
        s = fillet(s.edges().filter_by_position(Axis.Z, z1 - 0.01, z1 + 0.01), r_top)
    if r_bot:
        s = fillet(s.edges().filter_by_position(Axis.Z, z0 - 0.01, z0 + 0.01), r_bot)
    return s


def sel_edges(s, edges):
    """Edges of s (fresh from s.edges()) that match the given edges by position; fillet needs edges of the same shape."""
    keys = {tuple(round(v, 3) for v in (e.center().X, e.center().Y, e.center().Z)) for e in edges}
    return [e for e in s.edges() if tuple(round(v, 3) for v in (e.center().X, e.center().Y, e.center().Z)) in keys]


def pebble_flat(x0, x1, y0, y1, z0, z1, rn, rp):
    return pebble(x0, x1, y0, y1, z0, z1, rn, rp, 0.0, 0.0)


# ---------------- build ----------------
def build(pitch=None, pin_shift=None):
    shift = PIN_SHIFT_X if pin_shift is None else pin_shift
    base = load_base()
    rings = {n: Ring(n, base) for n in SIZES}
    # ---- vertical levels
    cell_z0 = PLATE_T + 0.4                                    # cell 0.4 above the bottom plate
    pcb1_z0 = cell_z0 + CELL["t"] + 0.3                        # PCB1 above the cell
    pcb1_z1 = pcb1_z0 + PCB1["t"]
    j1_top = pcb1_z1 + 3.31
    zf = round(j1_top + 0.3 + FT + 0.05, 1)                    # band floor
    zb = zf + BAND_W / 2 + FLOOR_GAP                           # band centre height (the band floats FLOOR_GAP above the floor)
    block_top = zb + BLOCK_HALF
    z_split = round(block_top + CEIL_CLR, 2)                   # base rim
    z_lid0 = z_split + LID_GAP
    h_tot = z_lid0 + LID_T

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

    # ---- plan outline
    cell_x1 = px0 - WALL - 0.3                                  # cell stays left of the pocket wall
    x_c0 = cell_x1 - CELL["x"]
    x_min = x_c0 - 3.8
    x_max = px1 + WALL
    pe = dict(x0=x_min, x1=x_max, y0=-Y_HALF, y1=Y_HALF)
    outer = pebble(x_min, x_max, -Y_HALF, Y_HALF, 0.0, z_split, R_NEG, R_POS, R_TOP, R_BOT)
    plate = outer & box(x_min - 1, x_max + 1, -Y_HALF - 1, Y_HALF + 1, -1, PLATE_T)
    shell = outer & box(x_min - 1, x_max + 1, -Y_HALF - 1, Y_HALF + 1, PLATE_T, z_split + 1)

    # ---- cuts
    strips = None
    xfar = X_A - 25.0
    for sg in (1, -1):
        y0, y1 = FLANK_STRIP
        xa_m = X_A - FLANK_GAP / COSPHI
        poly = [(xa_m + y0 * TANPHI, sg * y0), (xa_m + y1 * TANPHI, sg * y1), (xfar, sg * y1), (xfar, sg * y0)]
        st = prism_xy(poly, zf - 1, z_split + 2)
        strips = st if strips is None else strips + st
    well = prism_xy(hull_w, zf, z_split + 2) - strips
    pocket = box(px0, px1, py0, py1, zb - BLOCK_HALF - 0.4, z_split + 2)
    # finger notches at the pocket's top: room to pinch the block's upper end
    relief = box(px0, px1, -RELIEF_Y, RELIEF_Y, zb - 8.6, zb - BAND_W / 2 - 0.05) + box(px0, px1, -RELIEF_Y, RELIEF_Y, zb + BAND_W / 2 + 0.05, zb + 8.6)
    notch = box(px0 + 1.0, px1 - 1.0, py0 - 3.5, py1 + 3.5, block_top - 7.0, z_split + 2)
    uf = pebble_flat(x_min + WALL, cell_x1 + 0.6, -Y_HALF + WALL, Y_HALF - WALL, PLATE_T - 0.01, zf - FT, R_NEG - WALL, 0.5)
    # electronics volumes
    cell = box(x_c0, x_c0 + CELL["x"], -CELL["y"] / 2, CELL["y"] / 2, cell_z0, cell_z0 + CELL["t"])
    pcb1_x0 = x_min + WALL + 0.4
    pcb1 = box(pcb1_x0, pcb1_x0 + PCB1["x"], -PCB1["y"] / 2, PCB1["y"] / 2, pcb1_z0, pcb1_z1)
    top = pcb1_z1
    p = {}
    p["main_board"] = pcb1
    p["cell_dnk852338"] = cell
    p["U1_esp32s3_mini1"] = box(pcb1_x0 + 0.6, pcb1_x0 + 0.6 + 15.4, -15.0, 5.5, top, top + 2.4)
    jx0 = x_min + 0.3
    p["J1_usb4105"] = box(jx0, jx0 + 7.35, 8.0, 8.0 + 8.94, top, top + 3.31)
    p["LED1"] = box(pcb1_x0 + 0.6, pcb1_x0 + 0.6 + 1.6, -17.3, -15.7, top, top + 0.7)
    sx = pcb1_x0 + 0.6 + 15.4 + 0.8
    p["U2_bq25895"] = box(sx, sx + 4.0, -16.0, -12.0, top, top + 0.8)
    p["L1_1uH"] = box(sx, sx + 4.2, -10.5, -6.3, top, top + 2.0)
    p["U3_tps63802"] = box(sx, sx + 3.0, -4.5, -2.5, top, top + 0.8)
    p["L2_0u47"] = box(sx, sx + 4.0, -1.0, 3.0, top, top + 1.5)
    p["U5_tps2553"] = box(sx, sx + 2.9, 5.0, 6.6, top, top + 1.0)
    p["U4_zdsd64g"] = box(pcb1_x0 + 7.0, pcb1_x0 + 16.0, 6.0, 16.0, top, top + 1.0)

    # ---- post with pin lug
    # pin base planes: each pin stands on its own island of PCB2 so that every pin has the height PIN_H0 at US 10; the outer pads sit
    # nearer the post than the inner pads (the row is an arc), so the outer islands are recessed
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
    # pins
    for k in range(4):
        h = xbk[k] - pad_face_xy(9, k, pitch)[0] - TIP_GAP        # modelled at contact with the US 9 pad
        p[f"pin_P{k+1}_{PAD_NETS[k]}"] = make_pin(xbk[k] + shift, ypin[k], z_pin, h)
    # wire slot under the lug (PCB2 wires to PCB1), cut into the floor
    slot = box(x_b + 1.0, x_b + 4.0, -4.0, 4.0, zf - FT - 0.01, zf + 0.01)

    # ---- apply cuts to the shell
    cuts = [well, pocket, relief, notch, uf, slot]
    usb = box(x_min - 0.5, x_min + WALL + 0.01, 8.0 - 0.35, 8.0 + 8.94 + 0.35, top - 0.35, top + 3.31 + 0.35)
    led = cyl_x(x_min - 0.5, x_min + WALL + 0.01, -16.5, top + 0.35, 2.4)
    cuts += [usb, led]
    # lid pivot corner and magnet
    pivx, pivy = x_min + 4.5, -(Y_HALF - 4.5)
    cuts.append(cyl_z(pivx, pivy, z_split - 7.0, z_split + 0.5, PIVOT_D + 0.2))
    mx, my = x_max - 6.0, 15.5
    cuts.append(cyl_z(mx, my, z_split - 1.6, z_split + 0.5, 4.2))
    for c in cuts:
        shell = shell - c
    p["shell"] = shell
    p["base_plate"] = plate
    # ---- lid: flat cap, domed top, same outline as the base
    lid = pebble(x_min, x_max, -Y_HALF, Y_HALF, z_lid0, h_tot, R_NEG, R_POS, 3.0, 0.4)
    lid = lid - cyl_z(pivx, pivy, z_lid0 - 0.1, h_tot - 1.2, PIVOT_D + 0.2) - cyl_z(mx, my, z_lid0 - 0.1, z_lid0 + 1.6, 4.2)
    p["lid"] = lid
    p["hinge_pivot"] = cyl_z(pivx, pivy, z_split - 6.9, h_tot - 1.3, PIVOT_D)
    p["magnet_base"] = cyl_z(mx, my, z_split - 1.5, z_split, 4.0)
    p["magnet_lid"] = cyl_z(mx, my, z_lid0, z_lid0 + 1.5, 4.0)
    gl = [(pivx, pivy + 0.0), (x_min + 9.0, Y_HALF - 3.5 - 4.0), (x_max - 14.0, -(Y_HALF - 3.5 - 4.0))]
    gl = [(pivx, pivy), (pivx, -pivy), (x_max - 9.7, -19.3), (x_max - 9.7, 19.3)]
    for i, (gx, gy) in enumerate(gl, 1):
        g = cyl_z(gx, gy, z_split, z_lid0, GLIDE_D if i == 1 else 4.0)
        if i == 1:
            g = g - cyl_z(gx, gy, z_split - 0.1, z_lid0 + 0.1, PIVOT_D + 0.4)      # washer around the pivot pin
        p[f"glide_{i}"] = g
    # keep glides out of the notch and well cut: they sit on solid rim; verified by the collision check
    meta = dict(xb=xbk, x_bo=x_bo, zf=zf, zb=zb, z_split=z_split, z_lid0=z_lid0, h_tot=h_tot, x_min=x_min, x_max=x_max, y_half=Y_HALF, px0=px0, px1=px1,
                py0=py0, py1=py1, x_b=x_b, ypin=ypin, z_pin=z_pin, post_cx=post_cx, post_r=post_r, pivot=(pivx, pivy), magnet=(mx, my),
                cell_x0=x_c0, pcb1_x0=pcb1_x0, hull_w=hull_w, glides=gl, block_top=block_top, pcb1_z=(pcb1_z0, pcb1_z1))
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
        s = shp.moved(shp.location)
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
        lid_open_deg=LID_OPEN_DEG, lid_gap=LID_GAP, **meta,
    )
    with open(os.path.join(OUT, "case_params.json"), "w") as f:
        json.dump(params, f, indent=1, default=float)
    print(txt)
    print("parts:", len(parts))
    print("pin heights spread %.3f mm (window %.2f to %.2f)" % (max(allh) - min(allh), PIN_H_MIN, PIN_H_MAX))
    print("case.py done")


if __name__ == "__main__":
    main()
