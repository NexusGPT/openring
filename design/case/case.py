"""Ring charging case, version C5d-r4 (2026-11-13): the two case boards are read from their routed board files on every run
(design/ecad/case/pcb/case_main.kicad_pcb and case_pins.kicad_pcb, read only; reader r4/case_boards.py): main board outline, thickness and every part
body from the board's own 3D export (kicad-cli), pin board islands and pads from its file. The board is placed so that its USB-C socket's real front
sits J1_LIP behind the skin (as before); new parts: the board retainer (printed, holds the main board), the foam pad and insulating sheet of the stack,
the thermistor bead and the nine leads (W1 to W7, two thermistor leads) as swept wires. Notes: case-model-r4-notes.md.

Older header follows. Ring charging case, version C5d: the soft cube C5c with its open points closed (2026-11-11):
- the ring is the accepted exterior merged32h, one real STEP file per size US 7 to 13 (its round, higher joystick), not a computed family;
- the pads (and so the pins) come from the inside model's placement file design/mech/thin/placement.csv (rows pad_<net>), not typed here;
- the pin holder is its own part (`pin_holder`, black LCP), heat-staked on the post's lug by two pegs moulded on the post;
- the two band rests in the dish stop 1.0 mm below the band's top with rounded edges (they ran to the rim before).

Older header follows. Ring charging case, version C5c (C5b plus detail: one-arc dome with a thumb dimple, seam trims, dish liner, stepped pocket, USB bezel and light window, foot ring, marking field).

Older header follows. Ring charging case, version C5b: the soft pebble inside C4's size (owner's pick "A: flat on a post", reference picture owner-2159, "make the case look extra good").

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
from build123d import (Axis, Box, Compound, Cone, Cylinder, Edge, Face, Pos, Rot, Solid, Sphere, Vector, Wire, export_gltf, export_step,
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
sys.path.insert(0, os.path.join(HERE, "r4"))
import case_boards as CB  # noqa: E402

OUT = os.environ.get("CASE_OUT", os.path.join(HERE, "out"))   # CASE_OUT: another output folder (pitch sweep, broken copy)
PARTS = os.path.join(OUT, "parts")
RINGDIR = os.path.join(HERE, "..", "look", "s1", "out")
# C5d: the ring is the accepted exterior merged32h, one real file per size (its round joystick: frame 5.4 mm, cap 4.4 mm, cap 1.48 mm above the frame,
# on the band's outer face at -84 / -81 / -78 degrees for US 7 / 8 / 9 to 13); bore and centre from the file's own measures json
RING_STEP_N = os.path.join(RINGDIR, "ring-merged32h-us{n}.step")
RING_MEAS_N = os.path.join(RINGDIR, "measures-merged32h-us{n}.json")
SIZES = list(range(7, 14))
# the ring's own pad positions: read from the inside model's placement file (never typed here); CASE_PLACEMENT picks another copy (the check's test copy)
PLACEMENT = os.environ.get("CASE_PLACEMENT", os.path.normpath(os.path.join(HERE, "..", "mech", "thin", "placement.csv")))

# ---------------- ring facts ----------------
BAND_T = 2.6                      # band thickness (R0 - ri), same at every size (measures json: R0 - ri = 2.6 at US 7 to 13)
BAND_W = 8.0                      # band width along its axis
BLOCK_HALF = 14.65                # block half length along the band axis


def _ring_info():
    out = {}
    for n in SIZES:
        with open(RING_MEAS_N.format(n=n)) as f:
            m = json.load(f)
        out[n] = dict(ri=float(m["info"]["ri"]), zc=float(m["info"]["zc"]), r0=float(m["info"]["R0"]), joy_deg=float(m["joystick_deg"]))
    return out


RING_INFO = _ring_info()


def read_placement(path=None):
    """The four charging pads of the ring's inside model (placement.csv rows pad_<net>): ring frame X band axis, Z toward the block, US 9.
    Returns the pad row's X offset, the pad disc diameter and thickness, the centre of the pad circle (fitted to the four pad centres), the pad face
    radius (centre radius minus half the thickness: the pads are flush with the bore) and, per pad, its net and its arc position s along the inner face
    (s = angle from the ring's bottom x face radius; + toward +Y)."""
    path = path or PLACEMENT
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            if r["part"].startswith("pad_"):
                rows.append(r)
    if len(rows) != 4:
        raise RuntimeError(f"{path}: {len(rows)} pad rows, need 4")
    P = np.array([[float(r["x"]), float(r["y"]), float(r["z"])] for r in rows])
    # circle through the pad centres in the ring's YZ plane, centre on Y = 0: y^2 + z^2 = 2 z zc + (rc^2 - zc^2), least squares
    A = np.stack([2 * P[:, 2], np.ones(len(P))], 1)
    sol, *_ = np.linalg.lstsq(A, (P[:, 1] ** 2 + P[:, 2] ** 2), rcond=None)
    zc_p = float(sol[0])
    rcs = np.hypot(P[:, 1], P[:, 2] - zc_p)
    t = float(rows[0]["size_z"])
    r_face = float(rcs.mean()) - t / 2
    pads = []
    for r, p in zip(rows, P):
        th = math.atan2(p[1], -(p[2] - zc_p))
        pads.append(dict(net=r["part"][4:], ref=r["reference"], s=th * r_face, x=float(p[0])))
    return dict(path=os.path.abspath(path), x=float(P[:, 0].mean()), x_spread=float(np.ptp(P[:, 0])), d=float(rows[0]["size_x"]), t=t, zc=zc_p,
                r_face=r_face, r_fit_spread=float(np.ptp(rcs)), pads=pads, pitch=float(np.mean(np.diff(sorted(pp["s"] for pp in pads)))))


PL = read_placement()
PAD_NETS = [p["net"] for p in PL["pads"]]
PIN_NO = {"VBUS": 1, "D-": 2, "D+": 3, "GND": 4}   # the case's own pin designators P1 to P4 (case-architecture.md section 2)
PAD_PITCH = PL["pitch"]           # arc pitch at the pad face (from placement.csv)
PAD_D = PL["d"]                   # pad disc diameter (from placement.csv)
PAD_T = PL["t"]                   # pad disc thickness (from placement.csv)
PAD_X_OFF = PL["x"]               # pad row offset along the band axis toward the light end (ring -X) (from placement.csv)
PAD_RECESS = PL["r_face"] - RING_INFO[9]["ri"]      # pad face radius minus the US 9 file's bore radius (0 = flush)


def joy_deg(n):
    return abs(RING_INFO[n]["joy_deg"])
# ---------------- pin (Harwin P70-6000045R, [LIST] proposed, not confirmed: conflict K1) ----------------
PIN = dict(free_h=2.80, work_h=2.10, plunger_d=0.60, barrel_d=1.06, barrel_h=1.85, flange_d=1.50, flange_h=0.40)   # r4: Harwin drawing P70-6000045R sheet 2 (design/datasheets/w15_harwin_drawing_P70-600_page-1.png): flange 1.50 x 0.40 at the board, body 1.06 dia to 1.85, plunger 0.60; C5d modelled the whole body as 1.50 x 1.85
PIN_H_MIN, PIN_H_MAX = 1.90, 2.20  # r4: the maker's working range of P70-6000045R, 1.90 (most compressed) to 2.20 (least) (design/case/pin-travel.md, Harwin C05604);
                                  # C5d assumed 2.15 to 2.65, above the maker's range
PIN_H0 = float(os.environ.get("CASE_PIN_H0", "2.05"))   # design height at US 10, centred in 1.90 to 2.20 (C5d: 2.35); CASE_PIN_H0: broken copy only
PIN_H0_OUT = float(os.environ.get("CASE_PIN_H0_OUT", "2.15"))   # r4: the two outer pins (pads about 21 degrees round the bore, band face tilted under the body): body clear of the band from 2.10 (r4/outer_pin_scan_fine.log), so 2.10 to 2.20, centred 2.15
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
PCB1 = dict(x=23.0, y=35.4, t=1.0)       # r4: not used for the board any more (outline and thickness come from the board file); kept: ecad/case/pcb/geom.py reads this line
CAV_YH = 20.35                    # underfloor cavity half width (cell 40.0 long + 0.35 each side); r4: grows where the board needs BOARD_WALL_GAP
# ---------------- r4: boards from their files, their holding and their leads ----------------
BOARD_WALL_GAP = 0.4              # main board edge to the cavity wall (C4 to C5d kept 0.4 on the -X side; check test 5 needs 0.3)
CAV_Y1 = 20.6                     # r4: cavity end on the socket side (+Y): the round-2 board ends at y 20.2 (board-notes.md Round 2), + BOARD_WALL_GAP
LEAD_GAP = 0.02                   # modelled gap of a lead or a retainer to what it touches (a solder joint, a pressed face), as HOLD_GAP
WIRE_D = 0.50                     # W1 to W4, W7: 30 AWG wire, outer diameter (start value: PTFE-insulated 30 AWG is 0.50 mm; maker code open)
CELL_LEAD_D = 1.0                 # W5, W6: the cell's own flying leads, outer diameter (start value, not in case_cell_dnk852338.pdf p.1)
CELL_LEAD_M = 10.0                # distance between the cell's two leads (case_cell_dnk852338.pdf p.1, item M = 10)
CELL_LEAD_ZDOWN = 1.0             # the leads leave the PCM end this far below the cell's top face (my reading of the side view, p.1)
TH1_D, TH1_LEAD_D = 1.6, 0.30     # thermistor bead and lead diameters (start values; 103AT-2 sheet not read)
REC_D = 0.70                      # wire recess in the pin holder's front wall behind the wire pads (depth along X)
RET = dict(web_t=0.8, post_d=1.6, clr=0.3, fence_y=(-10.0, 10.0))   # board retainer: web thickness, post diameter, clearance to bodies, fence span in y
FOAM_FREE = 0.8                   # foam pad under the cell: free thickness (compressed into the 0.4 gap)
LID_T = 4.0                       # lid thickness under the crown
LID_GAP = 0.3                     # the shadow gap of the seam (lid rides on 0.3 mm glides)
CEIL_CLR = 0.3                    # base rim above the ring's top
PIVOT_D = 3.0
LID_OPEN_TRY = (100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 160.0, 170.0, 180.0)
SEAM_EDGE = 0.9                   # keep-out from the outline at the seam for pivot, magnet and glides
POCKET_RV = 1.2                   # pocket plan corner radius (the block's own corners are about this round)
POCKET_RB = 0.6                   # pocket bottom edge radius (side gap to the block is only 0.15 mm)
FLARE_AX = 6.2                    # the block's flare into the band spans this axial half-length
LINER_T = 0.9                     # soft liner of the dish
DIMPLE = dict(d=8.0, depth=0.4, blend=1.5)   # thumb dimple on the lid
FIELD = dict(x=14.0, y=8.0, z=0.35)   # marking field under the base: size and the floor height (depth 0.35 at the centre, about 0.2 at its ends)
FOOT_IN = (0.669, 0.762)          # foot ring between these plan scale factors (inset 5.0 to 7.5 mm), 0.4 to 0.6 mm proud of the crowned base
BEZEL_W = 0.4                     # USB bezel frame width
BEZEL_SET = 0.2                   # bezel face set this far into the skin
TRIM = dict(h=0.4, d=0.4, chamfer=0.2)   # seam trims: band height and depth, chamfer on the seam edge
WELL_ROLL = 1.8                   # radius where the dish floor rolls into the wall
REST_DROP = 1.0                   # C5d: the two band rests end this far below the band's top face
REST_R_TOP = 0.8                  # C5d: round on the rests' top edges
REST_R_SIDE = 0.25                # C5d: round on the two vertical edges of each rest's flank face
# ---------------- pin holder (C5d): black LCP part that carries the four pin barrels in front of PCB2, heat-staked on the post's lug ----------------
HOLD_G = 0.35                     # holder front face to the band's inner face, smallest over US 7 to 13 and the holder's width
HOLD_HY = 5.5                     # holder half width (the lug's)
HOLD_LIP_T = 0.8                  # lip over the lug top
HOLD_LIP_X1 = 8.6                 # lip back edge (x), on the lug top
HOLD_BORE = 1.60                  # bores for the 1.50 mm pin barrels
HOLD_GAP = 0.02                   # modelled gap holder to lug, PCB2 islands and staking heads
STAKE = dict(d=1.0, hole=1.1, x=7.9, y=3.6, head_d=1.7, head_h=0.35, cb_d=1.8, cb_h=0.40)   # two heat stakes: peg on the lug top, head in a counterbore
MAG_COVER = 0.5                   # skin over the base magnet, so the rim shows no hole
J1_LIP = 0.3                      # the USB-C mouth sits this far behind the skin at its centre
JY = 8.0                          # J1 y start (as C4)
J1_YC = JY + 8.94 / 2
LED_Y = 6.0                       # charge light beside the socket (between U1 and J1)
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


# ---------------- ring family (one real file per size) ----------------
def ri_of(n):
    return RING_INFO[n]["ri"]


def r0_of(n):
    return RING_INFO[n]["r0"]


def zc_of(n):
    return RING_INFO[n]["zc"]                       # the block is fixed to the top of the band: the centre moves down as the bore grows


COSPHI = math.cos(math.radians(PHI))
TANPHI = math.tan(math.radians(PHI))


def cx_of(n):
    """x of the bore centre: the band rests on the two flanks, so the centre is R0 / cos(phi) from the apex line."""
    return X_A + r0_of(n) / COSPHI


def pad_face_r(n):
    """pad face radius at size n: the size's bore radius plus the placement's recess (0 when flush)"""
    return ri_of(n) + PAD_RECESS


def pad_angles(n, pl=None):
    """angle of each pad from the ring's bottom (the pad direction, case -X) at size n: the placement's arc position kept at this size's face radius"""
    pl = pl or PL
    return [p["s"] / pad_face_r(n) for p in pl["pads"]]


def pad_face_xy(n, k, pl=None):
    """Pad k face centre in the case frame (x, y): on the inner face, angle theta from the pad direction (-X)."""
    th = pad_angles(n, pl)[k]
    r = pad_face_r(n)
    return cx_of(n) - r * math.cos(th), r * math.sin(th)


def pad_face_xyz(n, k, zb, pl=None):
    """Pad k face centre in the case frame (x, y, z) at size n: the ring's X (band axis) maps to case -Z about the band centre height zb"""
    pl = pl or PL
    x, y = pad_face_xy(n, k, pl)
    return x, y, zb - pl["pads"][k]["x"]


class Ring:
    """Ring of size n in the ring frame (X band axis, Y across, Z toward the block), plus its placement into the case.
    C5d: body, glass and joystick are the real exterior file of this size (ring-merged32h-us<n>.step); the pads are discs at the placement.csv places."""

    def __init__(self, n, base=None, pl=None):
        self.n = n
        self.pl = pl or PL
        self.ri, self.r0, self.zc = ri_of(n), r0_of(n), zc_of(n)
        ch = load_base(n)
        self.body, self.glass, self.joystick = ch["body"], ch["glass"], ch["joystick"]
        self.pads = self._pads()

    def _pads(self):
        out = None
        for k, th in enumerate(pad_angles(self.n, self.pl)):
            r = pad_face_r(self.n) + self.pl["t"] / 2
            y, z = r * math.sin(th), self.zc - r * math.cos(th)
            p = Pos(self.pl["pads"][k]["x"], y, z) * (Rot(180.0 + math.degrees(th), 0, 0) * Cylinder(self.pl["d"] / 2, self.pl["t"]))
            out = p if out is None else out + p
        return out

    def place(self, shape, zb):
        return Pos(cx_of(self.n), 0, zb) * (Rot(0, 90, 0) * (Pos(0, 0, -self.zc) * shape))

    def parts_in_case(self, zb):
        return {"body": self.place(self.body, zb), "glass": self.place(self.glass, zb),
                "joystick": self.place(self.joystick, zb), "pads": self.place(self.pads, zb)}


_BASE = {}


def load_base(n=9):
    if n not in _BASE:
        r = import_step(RING_STEP_N.format(n=n))
        _BASE[n] = {c.label: c for c in r.children}
    return _BASE[n]


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


def dish_cutter(ax_x, z0, z1, rw0, rw1, roll, n=10):
    """the well as one smooth dish, a surface of revolution about the post's axis: flat floor, a quarter-circle roll of radius `roll` into a wall that
    flares from radius rw0 (at z0 + roll) to rw1 (at z1)"""
    V = lambda r, z: Vector(ax_x + r, 0, z)
    arc = []
    for k in range(n + 1):
        a = (math.pi / 2) * k / n
        arc.append((rw0 - roll + roll * math.sin(a), z0 + roll - roll * math.cos(a)))
    edges = [Edge.make_line(V(0, z0), V(*arc[0])), Edge.make_spline([V(*q) for q in arc]),
             Edge.make_line(V(*arc[-1]), V(rw1, z1)), Edge.make_line(V(rw1, z1), V(0, z1)), Edge.make_line(V(0, z1), V(0, z0))]
    return Solid.revolve(Face(Wire(edges)), 360, Axis((ax_x, 0, 0), (0, 0, 1))).fix()


def extrude_rr(x0, x1, yc, zc, w, h, r):
    """rounded-rectangle prism along X (profile in the plane x = x0)"""
    return Solid.extrude(Face(Wire.make_polygon(rrect_pts(x0, yc, zc, w, h, r), close=True)), Vector(x1 - x0, 0, 0))


def wall_prism(z0, z1, scale, npts=96):
    """a straight (ruled) loft of the wall's outline scaled by `scale`, between two planes: the skin's wall pushed in by (1 - scale) x the half size"""
    ts = BRepOffsetAPI_ThruSections(True, True, 1e-6)
    for z in (z0, z1):
        xx, yy = PB.outline_at(scale, npts)
        ts.AddWire(Wire([Edge.make_spline([Vector(a, b, z) for a, b in zip(xx, yy)], periodic=True)]).wrapped)
    ts.Build()
    return Solid(ts.Shape()).fix()


def ring_extrude(rho_in, rho_out, z0, z1, npts=120):
    """the band between two scaled outlines of the plan, extruded from z0 to z1"""
    def solid(rho):
        xx, yy = PB.outline_at(rho, npts)
        return Solid.extrude(Face(Wire([Edge.make_spline([Vector(a, b, z0) for a, b in zip(xx, yy)], periodic=True)])), Vector(0, 0, z1 - z0))
    return solid(rho_out) - solid(rho_in)


def band_prism(z0, z1):
    """the inner part of the seam band: the wall pushed in by TRIM['d'] (the body keeps this; the trim part wraps it)"""
    return wall_prism(z0, z1, 1 - TRIM["d"] / PB.PEB["AX"])


def trim_ring(z_a, z_b, chamfer_at_top):
    """seam trim: a band TRIM['h'] high and TRIM['d'] deep along the outline of the wall, with a TRIM['chamfer'] chamfer on its seam edge (own part).
    The neighbouring body is built with band_prism instead of the full wall in that band, so no boolean cut of the skin is needed."""
    ax = PB.PEB["AX"]
    ch = TRIM["chamfer"]
    rin = wall_prism(z_a - 0.1, z_b + 0.1, 1 - TRIM["d"] / ax)
    zs = (z_a, z_b - ch, z_b) if chamfer_at_top else (z_a, z_a + ch, z_b)
    scl = (1.0, 1.0, 1 - ch / ax) if chamfer_at_top else (1 - ch / ax, 1.0, 1.0)
    ts = BRepOffsetAPI_ThruSections(True, True, 1e-6)
    for z, sc_ in zip(zs, scl):
        xx, yy = PB.outline_at(sc_, 96)
        ts.AddWire(Wire([Edge.make_spline([Vector(a, b, z) for a, b in zip(xx, yy)], periodic=True)]).wrapped)
    ts.Build()
    return Solid(ts.Shape()).fix() - rin


z_lid_dbg = 38.0


def blend_dimple(lid, at):
    """tangent rim blend of the thumb dimple (radius DIMPLE['blend'])"""
    cand = [e for e in lid.edges() if math.hypot(e.center().X - at[0], e.center().Y - at[1]) < 7.0 and e.center().Z > z_lid_dbg]
    print("dimple edges near:", [(round(e.center().X, 1), round(e.center().Y, 1), round(e.center().Z, 2), round(e.bounding_box().size.X, 1), round(e.length, 1)) for e in cand], flush=True)
    es = [e for e in cand if 6.0 < e.length < 40.0]
    try:
        return fillet(es, DIMPLE["blend"])
    except Exception as ex:                                      # noqa: BLE001
        print("dimple blend not built:", repr(ex)[:100])
        return lid


def dimple_cutter(pivot, H):
    """thumb dimple on the lid, at the crown opposite the pivot: a sphere cap (chord DIMPLE d, depth DIMPLE depth) cut along the surface normal"""
    c = np.array([PB.PEB["XC"], 0.0])
    d = c - np.array(pivot)
    d /= np.linalg.norm(d)
    lo, hi = 0.0, 40.0
    for _ in range(50):
        m = 0.5 * (lo + hi)
        q = c + m * d
        if PB.rho_point(q[0], q[1]) < 0.55:
            lo = m
        else:
            hi = m
    q = c + lo * d
    fz = lambda x, y: float(PB.z_upper_of_rho(PB.rho_point(x, y), H))
    e = 0.3
    gx = (fz(q[0] + e, q[1]) - fz(q[0] - e, q[1])) / (2 * e)
    gy = (fz(q[0], q[1] + e) - fz(q[0], q[1] - e)) / (2 * e)
    nv = np.array([-gx, -gy, 1.0])
    nv /= np.linalg.norm(nv)
    dd, dp = DIMPLE["d"], DIMPLE["depth"]
    rs = (dd * dd / 4 + dp * dp) / (2 * dp)
    p0 = np.array([q[0], q[1], fz(q[0], q[1])])
    cen = p0 + nv * (rs - dp)
    return Pos(*cen) * (Rot(90, 0, 0) * Sphere(rs)), (float(q[0]), float(q[1]), rs)


# ---------------- build ----------------
def build(pin_shift=None):
    shift = PIN_SHIFT_X if pin_shift is None else pin_shift
    base = load_base(9)
    rings = {n: Ring(n) for n in SIZES}
    # ---- r4: the two boards, read from their files (KiCad's Python and kicad-cli, every run)
    boards = CB.read(os.path.join(OUT, "boards"))
    # ---- vertical levels
    cell_z0 = ZP + 0.4                                         # cell 0.4 above the bottom plate
    pcb1_z0 = cell_z0 + CELL["t"] + 0.3                        # PCB1 above the cell
    pcb1_z1 = pcb1_z0 + float(boards["main"]["json"]["thickness"])   # r4: thickness from the board file
    j1_top = pcb1_z1 + 3.31
    zf = round(j1_top + 0.3 + FT + 0.05, 1)                    # band floor
    zb = zf + BAND_W / 2 + FLOOR_GAP                           # band centre height (the band floats FLOOR_GAP above the floor)
    block_top = zb + BLOCK_HALF
    z_split = round(block_top + CEIL_CLR, 2)                   # base rim: the seam plane of the shell
    z_lid0 = round(z_split + LID_GAP, 2)                       # lid underside
    H = PB.PEB["H"]                                           # top of the crown (size limit of the brief)

    # ---- block silhouette in the case frame, over the seven real ring files (the block is fixed to the band's top; the junction blend differs by size)
    by0 = by1 = bz0n = None
    blk_x, nv_ = [], []
    for n in SIZES:
        bn = load_base(n)
        blk = bn["body"] & (box(-20, -BAND_W / 2 - 0.01, -20, 20, -20, 10) + box(BAND_W / 2 + 0.01, 20, -20, 20, -20, 10))
        bb, gb = blk.bounding_box(), bn["glass"].bounding_box()
        y0_, y1_ = min(bb.min.Y, gb.min.Y), max(bb.max.Y, gb.max.Y)
        by0 = y0_ if by0 is None else min(by0, y0_)
        by1 = y1_ if by1 is None else max(by1, y1_)
        z0_, z1_ = min(bb.min.Z, gb.min.Z), max(bb.max.Z, gb.max.Z)            # ring frame Z of the block's extent at this size
        blk_x.append((cx_of(n) + (z0_ - zc_of(n)), cx_of(n) + (z1_ - zc_of(n))))
        nv_ += [(p_.X, p_.Y) for sh_ in (blk, bn["glass"]) for p_ in sh_.tessellate(0.05)[0]]
    px0 = min(a for a, b in blk_x) - 0.3
    px1 = max(b for a, b in blk_x) + 0.3
    py0, py1 = by0 - POCKET_G, by1 + POCKET_G
    # locating pocket (closes roll play R1): the block is 14.75 mm wide except in its flare into the band (axial |x| < FLARE_AX); the pocket follows that
    bw = max(abs(y_) for ax_, y_ in nv_ if abs(ax_) > FLARE_AX + 0.3)
    pw = bw + POCKET_G

    # ---- well hull (band outer circle + the real joystick of every size, dilated by CLR)
    pts = []
    for n in SIZES:
        c, r0 = cx_of(n), r0_of(n)
        for k in range(120):
            a = 2 * math.pi * k / 120
            pts.append((round(c + r0 * math.cos(a), 3), round(r0 * math.sin(a), 3)))
        jv, _ = load_base(n)["joystick"].tessellate(0.03)
        for v in jv:
            pts.append((round(c + (v.Z - zc_of(n)), 3), round(v.Y, 3)))
    hull_w = dilate(hull2d(pts), CLR)
    print("well hull: %d points over the band circles and the seven real joysticks" % len(pts), flush=True)

    # ---- layout anchors (as C4: the cell sits left of the pocket wall; the electronics follow the cell)
    cell_x1 = px0 - WALL - 0.3
    x_c0 = cell_x1 - CELL["x"]
    x_lay = x_c0 - 3.8                                          # C4's left layout anchor (board, cavity), kept
    big_ = 400.0
    # ---- the outside skin
    plate = skin_part(H, 0.0, ZP)
    shell = skin_part(H, ZP, z_split - TRIM["h"]) + band_prism(z_split - TRIM["h"], z_split)
    lid_blank = band_prism(z_lid0, z_lid0 + TRIM["h"]) + skin_part(H, z_lid0 + TRIM["h"], H)
    print('skin bbox z', [(round(p.bounding_box().min.Z,2), round(p.bounding_box().max.Z,2)) for p in (plate, shell, lid_blank)], flush=True)
    print('skin parts: plate %.0f, shell blank %.0f, lid blank %.0f mm3, valid %s' % (plate.volume, shell.volume, lid_blank.volume, (plate.is_valid, shell.is_valid, lid_blank.is_valid)), flush=True)

    # ---- USB-C and light: the socket mouth sits J1_LIP behind the skin at its centre
    zj = pcb1_z1 + 3.31 / 2
    xs_min, xs_j = skin_x_left_range(JY, JY + 8.94, zj, H)      # the socket front sits J1_LIP behind the skin at the socket's outermost corner
    jx0 = xs_j + J1_LIP
    # r4: the board is placed so that the front of ITS socket body (the board's own 3D export) is jx0; C5d used x_lay + 1.9 with a socket front
    # read as 4.18 mm in front of the footprint origin, while the body ends 3.675 mm in front of it (KiCad's USB4105 model and footprint)
    pcb1_x0 = jx0 - CB.body_u_front(boards, "J1")

    # ---- cuts
    strips = None
    xfar = X_A - 25.0
    for sg in (1, -1):
        y0, y1 = FLANK_STRIP
        xa_m = X_A - FLANK_GAP / COSPHI
        poly = [(xa_m + y0 * TANPHI, sg * y0), (xa_m + y1 * TANPHI, sg * y1), (xfar, sg * y1), (xfar, sg * y0)]
        # C5d: the two rests stop REST_DROP below the band's top (they ran to the rim in C5c), their top edges are rounded REST_R_TOP and the two
        # vertical edges of the flank face REST_R_SIDE; the flank face keeps 3.55 to 5.55 mm of |y| and zf to the top minus the round
        st = prism_xy(poly, zf - 1, zb + BAND_W / 2 - REST_DROP)
        fl_v = [e for e in st.edges() if e.bounding_box().size.Z > 1.0 and e.center().X > xfar + 1.0]
        st = fillet(fl_v, REST_R_SIDE)
        top_e = [e for e in st.edges() if abs(e.center().Z - (zb + BAND_W / 2 - REST_DROP)) < 1e-3 and e.bounding_box().size.Z < 1e-3
                 and e.center().X > xfar + 0.5]
        st = fillet(top_e, REST_R_TOP)
        strips = st if strips is None else strips + st
    post_ax = X_A + (r0_of(7) + r0_of(13)) / 2 / COSPHI
    hull_max = max(math.hypot(x_ - post_ax, y_) for x_, y_ in hull_w)
    rw0 = max(r0_of(13) + 1.3 + CLR + WELL_ROLL, hull_max + 0.1)                      # dish wall radius at the floor: band, joystick nub and the roll
    rw1 = rw0 + 1.2                                                                   # flare to the rim
    print("dish: post axis x %.3f; hull radius %.3f; band rule %.3f; rw0 %.3f, rw1 %.3f" % (post_ax, hull_max, r0_of(13) + 1.3 + CLR + WELL_ROLL, rw0, rw1), flush=True)
    d_in = dish_cutter(post_ax, zf, z_split + 2, rw0, rw1, WELL_ROLL)                 # the dish surface (the liner's face)
    d_out = dish_cutter(post_ax, zf - LINER_T, z_split + 2, rw0 + LINER_T, rw1 + LINER_T, WELL_ROLL + LINER_T) & wall_prism(zf - 2, z_split + 3, 1 - 1.2 / PB.PEB["AX"])
    well = d_out
    liner_blank = (d_out - d_in) + (strips & d_out)         # the two V rests (flank faces) belong to the liner: one dark dish
    hull_w = [(round(post_ax + (rw1 + LINER_T) * math.cos(2 * math.pi * k_ / 90), 3), round((rw1 + LINER_T) * math.sin(2 * math.pi * k_ / 90), 3)) for k_ in range(90)]   # the dish's rim: what the swung lid must uncover
    pocket = rbox(px0, px1, -pw, pw, zb - BLOCK_HALF - 0.4, z_split + 2, POCKET_RV, POCKET_RB) + rbox(px0, px1, py0, py1, zb - FLARE_AX, zb + FLARE_AX, POCKET_RV, POCKET_RB)
    notch_y = py1 + 2.0
    notch = rbox(px0 + 1.0, px1 - 1.0, -notch_y, notch_y, block_top - 7.0, z_split + 2, 2.0, 1.5)
    # r4: the main board as routed (outline, thickness, every part body from the board's own files); the cavity keeps BOARD_WALL_GAP round it
    main_board, mb = CB.main_board(boards, pcb1_x0, pcb1_z0)
    bx = [x_ for x_, y_ in mb["outline_case"]]
    by_ = [y_ for x_, y_ in mb["outline_case"]]
    cav_x0, cav_x1 = pcb1_x0 - BOARD_WALL_GAP, cell_x1 + 0.6
    cav_y0, cav_y1 = -CAV_YH, CAV_Y1                            # r4: fixed design values; the check measures the board against them (test 5)
    # r4: the C5d cavity stays as it was below the board (bottom corners keep their wall); only the board's level (from 0.35 under the board to the
    # ceiling) grows to the board's -X edge and the socket-side end, BOARD_WALL_GAP round the board
    uf_low = rbox(x_lay + 1.5, cav_x1, -CAV_YH, CAV_YH, ZP - 0.01, zf - FT, 0.5)
    uf = uf_low + rbox(cav_x0, cav_x1, cav_y0, cav_y1, pcb1_z0 - 0.35, zf - FT, 0.5)
    # electronics volumes
    cell = box(x_c0, x_c0 + CELL["x"], -CELL["y"] / 2, CELL["y"] / 2, cell_z0, cell_z0 + CELL["t"])
    top = pcb1_z1
    p = {}
    p["main_board"] = main_board                               # one node, a child per part (PCB1, J1, U1, ... labelled by reference)
    p["cell_dnk852338"] = cell
    tabp = [(x_, y_) for x_, y_ in mb["outline_case"] if x_ < pcb1_x0 - 1e-6]          # the tab under the socket (board outline left of u = 0)
    tab_x = min(x_ for x_, y_ in tabp)
    tab_y0, tab_y1 = min(y_ for x_, y_ in tabp), max(y_ for x_, y_ in tabp)
    ceil_z = zf - FT                                           # the cavity's ceiling (underside of the floor)
    # ---- r4: stack below and above the board: foam pad under the cell, insulating sheet between cell and board (modelled at their compressed height)
    p["foam_pad"] = box(x_c0 + 0.5, x_c0 + CELL["x"] - 0.5, -CELL["y"] / 2 + 1.0, CELL["y"] / 2 - 1.0, ZP + LEAD_GAP, cell_z0 - LEAD_GAP)
    sh_x0, sh_x1 = max(x_c0, pcb1_x0) + 0.3, min(x_c0 + CELL["x"], pcb1_x0 + max(bx) - pcb1_x0) - 0.3
    p["insulation_sheet"] = box(sh_x0, sh_x1, max(-CELL["y"] / 2, min(by_)) + 0.3, min(CELL["y"] / 2, max(by_)) - 0.3, cell_z0 + CELL["t"] + LEAD_GAP, pcb1_z0 - LEAD_GAP)

    # ---- post with pin lug
    ypin = pin_ys()
    xbk = [pad_face_xy(10, k)[0] + (PIN_H0 if abs(ypin[k]) < 2.0 else PIN_H0_OUT) for k in range(4)]   # r4: inner pins 2.05, outer 2.15 at US 10
    inner = sorted(range(4), key=lambda k: abs(ypin[k]))
    x_b = xbk[inner[0]]                                         # inner island (the two middle pins)
    x_bo = xbk[inner[-1]]                                       # outer islands (the two outer pins), recessed toward the post
    z_pin = zb - PAD_X_OFF
    post_cx = X_A + (r0_of(7) + r0_of(13)) / 2 / COSPHI
    post_r = 6.0
    post_top = zb + 3.5
    post = cyl_z(post_cx, 0, zf, post_top, 2 * post_r)
    post = fillet(post.edges().filter_by_position(Axis.Z, post_top - 0.01, post_top + 0.01), 1.2)
    lug_hy, lug_z0, lug_z1 = HOLD_HY, zb - 3.0, post_top
    lug_x1 = post_cx - post_r + 1.5
    t2 = float(boards["pins"]["json"]["thickness"])                # r4: PCB2 thickness from its board file (C5d typed 0.8)
    lug = box(x_b + t2, lug_x1, -2.0, 2.0, lug_z0, lug_z1) + box(x_bo + t2, lug_x1, -lug_hy, lug_hy, lug_z0, lug_z1)
    post = post + lug
    # r4: PCB2's three islands from the board file; each island's front face is the base plane of the pins it carries (x_b inner, x_bo wings)
    k_of_ref = {f"P{PIN_NO[PAD_NETS[k]]}": k for k in range(4)}
    xface = lambda ref: x_b if k_of_ref[ref] in inner[:2] else x_bo
    isl, pb = CB.pin_board(boards, xface, z_pin)
    for ref, (py_, pz_) in pb["pins"].items():
        k = k_of_ref[ref]
        if abs(py_ - ypin[k]) > 0.01 or abs(pz_ - z_pin) > 0.01:
            raise RuntimeError(f"pin board file: {ref} at y {py_:.3f} z {pz_:.3f}; the ring's pad needs y {ypin[k]:.3f} z {z_pin:.3f}")
    p.update(isl)
    assert abs(float(pb["thickness"]) - t2) < 1e-9
    iy = pb["islands"]["pin_board_pcb2"]["y"]
    iz1 = max(v["z"][1] for v in pb["islands"].values())
    for k in range(4):
        h = xbk[k] - pad_face_xy(9, k)[0] - TIP_GAP              # modelled at contact with the US 9 pad
        net = PAD_NETS[k]
        ky = {1: 2, 2: 1}.get(k, k) if os.environ.get("CASE_PIN_SWAP") == "1" else k     # broken copy only: two middle pins swapped
        p[f"pin_P{PIN_NO[net]}_{net}"] = make_pin(xbk[k] + shift, ypin[ky], z_pin, h)

    # ---- pin holder (C5d): front face follows the band's inner face (largest x over US 7 to 13 at each y) HOLD_G in front of it; bores for the
    # four barrels; open at the back and bottom over the PCB2 islands; a lip on the lug top with two heat stakes (pegs moulded on the post)
    ys_h = np.linspace(-HOLD_HY, HOLD_HY, 45)
    xf_h = [max(cx_of(n) - math.sqrt(pad_face_r(n) ** 2 - y * y) for n in SIZES) + HOLD_G for y in ys_h]
    hz0 = lug_z0
    htop = post_top + HOLD_GAP
    x_bk = x_bo + t2 - HOLD_GAP                                # back of the holder's cheeks: the lug's outer front face, less the gap
    st_x = x_bo + t2 + 0.75
    lip_x1 = st_x + 1.05
    lip_top = htop + HOLD_LIP_T

    def holder_prism(xback, z0, z1):
        front = Edge.make_spline([Vector(float(x), float(y), z0) for x, y in zip(xf_h, ys_h)])
        a, b = Vector(float(xf_h[-1]), HOLD_HY, z0), Vector(float(xf_h[0]), -HOLD_HY, z0)
        w = Wire([front, Edge.make_line(a, Vector(xback, HOLD_HY, z0)), Edge.make_line(Vector(xback, HOLD_HY, z0), Vector(xback, -HOLD_HY, z0)),
                  Edge.make_line(Vector(xback, -HOLD_HY, z0), b)])
        return Solid.extrude(Face(w), Vector(0, 0, z1 - z0))
    hold = holder_prism(x_bk, hz0, htop) + holder_prism(lip_x1, htop, lip_top)
    hold = Solid(hold.solids()[0].wrapped) if len(hold.solids()) == 1 else hold
    ev = [e for e in hold.edges() if e.bounding_box().size.Z > 0.5 and abs(abs(e.center().Y) - HOLD_HY) < 1e-3 and e.center().X < x_bo]   # r4: x_bo (front corners sit at 5.64; x_b moved to 5.52 with the 2.05 pin height)
    hold = fillet(ev, 0.5)                                      # the two front corners
    eb = [e for e in hold.edges() if e.bounding_box().size.Z > 0.5 and abs(abs(e.center().Y) - HOLD_HY) < 1e-3 and abs(e.center().X - lip_x1) < 1e-3]
    hold = fillet(eb, 1.0)                                      # the lip's two back corners
    et = [e for e in hold.edges() if abs(e.center().Z - lip_top) < 1e-3 and e.bounding_box().size.Z < 1e-3]
    hold = fillet(et, 0.3)                                      # the top's outline
    ef = [e for e in hold.edges() if abs(e.center().Z - hz0) < 1e-3 and e.bounding_box().size.Z < 1e-3 and e.center().X < x_b - 0.5]
    hold = fillet(ef, 0.3)                                      # the bottom front edge
    g = HOLD_GAP
    hold = hold - box(x_b + t2 - g, lip_x1 + 1, -2.0 - g, 2.0 + g, hz0 - 1, htop)                           # the lug's inner nose
    hold = hold - box(x_b - g, x_b + t2 + g, iy[0] - g, iy[1] + g, hz0 - 1, iz1 + g)                       # inner island (r4: its size from the board file), open at the bottom
    wy1 = max(abs(v["y"][1]) for v in pb["islands"].values())
    for sg in (1, -1):
        y_a, y_b = sorted((sg * (iy[1] + g), sg * (wy1 + g)))
        hold = hold - box(x_bo - g, lip_x1 + 1, y_a, y_b, hz0 - 1, iz1 + g)                                   # outer islands (open back and bottom)
    # r4: the five wire pads (WP1 to WP4, WP7) are on the islands' FRONT face, which the holder covers: a recess REC_D deep in the holder's front
    # wall behind them, from the pads' top down through the holder's bottom, so the solder joints and the wires drop straight to the floor slot
    wps = {r: v for r, v in pb["pads"].items() if r.startswith("WP")}
    rec_z1 = max(v["z"] + v["sy"] / 2 for v in wps.values()) + 0.15
    for nm, v in pb["islands"].items():
        on = [w for w in wps.values() if v["y"][0] <= w["y"] <= v["y"][1]]
        if on:
            ry0 = max(v["y"][0], min(w["y"] for w in on) - WIRE_D / 2 - 0.35)
            ry1 = min(v["y"][1], max(w["y"] for w in on) + WIRE_D / 2 + 0.35)
            hold = hold - box(v["x"][0] - REC_D, v["x"][0] + 0.01, ry0, ry1, hz0 - 1, rec_z1)
    for k in range(4):
        xfk = float(np.interp(ypin[k], ys_h, xf_h))
        hold = hold - cyl_x(xfk - 1.0, xbk[k] + 0.01, ypin[k], z_pin, HOLD_BORE)
        cham = Pos(xfk + 0.05, ypin[k], z_pin) * (Rot(0, -90, 0) * Cone(HOLD_BORE / 2, HOLD_BORE / 2 + 0.3, 0.3))       # 0.2 x 45 degree lead-in chamfer at the face
        hold = hold - cham
    for sg in (1, -1):
        hold = hold - cyl_z(st_x, sg * STAKE["y"], htop - 0.1, lip_top + 0.1, STAKE["hole"])
        hold = hold - cyl_z(st_x, sg * STAKE["y"], lip_top - STAKE["cb_h"], lip_top + 0.1, STAKE["cb_d"])
        post = post + cyl_z(st_x, sg * STAKE["y"], post_top - 0.01, lip_top - STAKE["cb_h"] + g, STAKE["d"])
        post = post + cyl_z(st_x, sg * STAKE["y"], lip_top - STAKE["cb_h"] + g, lip_top - STAKE["cb_h"] + g + STAKE["head_h"], STAKE["head_d"])
    p["post"] = post
    p["pin_holder"] = hold
    holder_meta = dict(front_gap=HOLD_G, half_width=HOLD_HY, z0=hz0, z_top=htop, lip_top=lip_top, lip_x1=lip_x1, x_back=x_bk, stake_x=st_x,
                       stake_y=STAKE["y"], front_x_at_y0=float(np.interp(0.0, ys_h, xf_h)), front_x_at_edge=float(xf_h[0]),
                       bore=HOLD_BORE, wall_in_front_of_E1=float((x_b - g) - np.interp(0.0, ys_h, xf_h)), volume=float(hold.volume))
    slot = box(x_b - REC_D - 0.3, x_b + 4.0, -4.0, 4.0, zf - FT - 0.01, zf + 0.01)        # r4: starts under the holder's wire recess (C5d: x_b + 1.0)
    # ---- r4: the leads as swept wires (axis polylines, case frame); every end sits LEAD_GAP from the face of its solder joint
    pads1 = mb["pads"]
    leads, lead_meta = {}, {}
    zc_run = ceil_z - 0.6                                        # wires cross the cavity just under its ceiling
    if os.environ.get("CASE_LEAD_FAULT") == "1":                 # broken copy for check test 16 only: the wire run 0.6 mm lower (over U1's top)
        zc_run -= 0.6
    for wref in ("W1", "W2", "W3", "W4", "W7"):
        wp = wps["WP" + wref[1:]]
        isl_x = [v["x"][0] for v in pb["islands"].values() if v["y"][0] <= wp["y"] <= v["y"][1]][0]
        a = (isl_x - WIRE_D / 2 - LEAD_GAP, wp["y"], wp["z"])
        e = pads1[wref]
        pts = [a, (a[0], a[1], zc_run), (e["x"], e["y"], zc_run), (e["x"], e["y"], top + WIRE_D / 2 + LEAD_GAP)]
        leads[f"lead_{wref}"] = (pts, WIRE_D)
    # thermistor TH1: a bead glued on the cell's top face in the strip beside the board's +X edge, its two leads up over the edge and down into TH1.1, TH1.2
    th = [pads1[k] for k in ("TH1.1", "TH1.2")]
    bead_x = (pcb1_x0 + max(bx) - pcb1_x0 + x_c0 + CELL["x"]) / 2
    bead_y = sum(t_["y"] for t_ in th) / 2
    bead_z = cell_z0 + CELL["t"] + TH1_D / 2 + LEAD_GAP
    p["TH1_bead"] = Pos(bead_x, bead_y, bead_z) * Sphere(TH1_D / 2)
    zt_run = top + 1.0
    for i_, t_ in enumerate(th):
        sy_ = (-1, 1)[i_] * 0.45
        a = (bead_x, bead_y + sy_, bead_z + TH1_D / 2 + TH1_LEAD_D / 2 + LEAD_GAP)
        pts = [a, (bead_x, bead_y + sy_, zt_run), (t_["x"], bead_y + sy_, zt_run), (t_["x"], t_["y"], zt_run), (t_["x"], t_["y"], top + TH1_LEAD_D / 2 + LEAD_GAP)]
        leads[f"lead_TH1_{i_ + 1}"] = (pts, TH1_LEAD_D)
    # cell leads W5 (+, red) and W6 (-, black): out of the PCM end (y = +CELL y / 2), CELL_LEAD_M apart about the cell's centre line, into a pocket in the
    # cavity's +Y wall, up past the board's end and over to their plated holes; red on the +X side (nearer W5)
    cyc = x_c0 + CELL["x"] / 2
    ly = CELL["y"] / 2 + 1.0
    lz = cell_z0 + CELL["t"] - CELL_LEAD_ZDOWN
    zl_run = top + 1.0
    for wref, sx_ in (("W5", 1), ("W6", -1)):
        e = pads1[wref]
        ex = cyc + sx_ * CELL_LEAD_M / 2
        a = (ex, CELL["y"] / 2 + CELL_LEAD_D / 2 + LEAD_GAP, lz)
        pts = [a, (ex, ly, lz), (e["x"], ly, lz), (e["x"], ly, zl_run), (e["x"], e["y"], zl_run), (e["x"], e["y"], top + CELL_LEAD_D / 2 + LEAD_GAP)]
        leads[f"lead_{wref}"] = (pts, CELL_LEAD_D)
    lx_all = [q[0] for nm, (pts, d_) in leads.items() if nm in ("lead_W5", "lead_W6") for q in pts]
    lead_pocket = rbox(min(lx_all) - 1.0, max(lx_all) + 1.0, cav_y1 - 0.5, ly + CELL_LEAD_D / 2 + 0.3, lz - CELL_LEAD_D, zl_run + CELL_LEAD_D, 0.5)
    for nm, (pts, d_) in leads.items():
        p[nm] = swept_wire(pts, d_)
        lead_meta[nm] = dict(points=[[round(c, 4) for c in q] for q in pts], d=d_, length=sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)))
    # ---- r4: board retainer (printed, own part): a web under the cavity ceiling, posts that press the board onto the stack, a fence at the
    # board's +X edge that takes the push of a USB-C plug to the cavity wall
    ret, ret_meta = board_retainer(mb, pcb1_x0, top, pcb1_z0, ceil_z, cav_x1, leads, x_c0)
    p["board_retainer"] = ret

    # ---- seam layout: pivot, magnet, glides (2D at the seam plane)
    pocket_rect = [(px0 - 0.3, py0 - 0.3), (px1 + 0.3, py0 - 0.3), (px1 + 0.3, py1 + 0.3), (px0 - 0.3, py1 + 0.3)]
    relief_rect = [(px0, -RELIEF_Y), (px1, -RELIEF_Y), (px1, RELIEF_Y), (px0, RELIEF_Y)]
    notch_rect = [(px0 + 1.0, -notch_y), (px1 - 1.0, -notch_y), (px1 - 1.0, notch_y), (px0 + 1.0, notch_y)]
    lay = seam_layout(H, z_split, z_lid0, hull_w, pocket_rect, notch_rect, relief_rect)
    pivx, pivy = lay["pivot"]
    mx, my = lay["magnet"]
    z_top_piv = float(PB.z_upper_of_rho(PB.rho_point(pivx, pivy), H))
    pin_top = z_top_piv - 1.3

    # ---- USB-C mouth: a slot, a recess for the bezel (frame BEZEL_W wide, face set BEZEL_SET into the skin) and the light's hole
    w_s, h_s, r_s = 8.94 + 1.2, 3.31 + 1.2, 0.9
    x_o = xs_min - 1.0
    rec_x1 = min(xs_j + 1.2, tab_x - 0.35)                     # r4: the bezel's hidden inner end stays 0.35 mm from the real board tab (C5d: xs_j + 1.2)
    recess = extrude_rr(x_o, rec_x1, J1_YC, zj, w_s + 2 * BEZEL_W, h_s + 2 * BEZEL_W, r_s + BEZEL_W)
    slot_usb = extrude_rr(x_o, cav_x0 + 0.01, J1_YC, zj, w_s, h_s, r_s)
    bez_ring = recess - extrude_rr(x_o - 0.5, xs_j + 1.5, J1_YC, zj, w_s, h_s, r_s)
    p["usb_bezel"] = bez_ring & wall_prism(zj - 5, zj + 5, 1 - BEZEL_SET / PB.PEB["AX"])
    led = cyl_x(xs_min - 3.0, cav_x0 + 0.01, LED_Y, top + 0.35, DOT_D)
    led_x0 = pcb1_x0 + 0.6
    p["light_window"] = cyl_x(xs_min - 1.0, cav_x0, LED_Y, top + 0.35, DOT_D) & wall_prism(top - 2, top + 3, 1 - 0.0004)   # r4: ends at the cavity wall (C5d: 0.1 mm from the board edge)
    tabcut = box(tab_x - 0.4, cav_x0 + 0.01, tab_y0 - 0.35, tab_y1 + 0.35, pcb1_z0 - 0.35, top + 0.4)        # channel for the board tab that carries the socket (r4: the tab of the board file)
    # ---- apply cuts to the shell
    cuts = [well, pocket, notch, uf, slot, recess, slot_usb, led, tabcut, lead_pocket]
    cuts.append(cyl_z(pivx, pivy, z_split - 7.0, z_split + 0.5, PIVOT_D + 0.2))
    cuts.append(cyl_z(mx, my, z_split - 2.2, z_split - MAG_COVER, 4.2))
    for i_c, c in enumerate(cuts):
        shell = shell - c
        print('  shell after cutter', i_c, type(shell).__name__, shell.is_valid, len(shell.solids()), flush=True)
    liner = liner_blank & box(-big_, big_, -big_, big_, zf - LINER_T - 0.5, z_split)
    for c in (pocket, notch, slot):
        liner = liner - c
    if os.environ.get("CASE_LIFT_FAULT") == "1":                 # broken copy for check test 17 only: a tooth on the dish wall over the band's way out
        liner = liner + box(post_ax - rw1 - LINER_T / 2, X_A + 1.5, -1.0, 1.0, zb + BAND_W / 2 + 3.0, zb + BAND_W / 2 + 4.0)
    p["liner"] = liner
    p["shell"] = shell
    field = rbox(PB.PEB["XC"] - FIELD["x"] / 2, PB.PEB["XC"] + FIELD["x"] / 2, -FIELD["y"] / 2, FIELD["y"] / 2, -1.0, FIELD["z"], 1.5)
    p["foot"] = ring_extrude(FOOT_IN[0], FOOT_IN[1], 0.0, 1.2) - plate
    p["base_plate"] = plate - field
    # ---- seam trims (polished bands on both edges of the 0.3 mm gap, own parts)
    trim_s = trim_ring(z_split - TRIM["h"], z_split, True)
    p["shell"] = shell
    p["seam_trim"] = trim_s
    # ---- lid: the domed cap above the seam
    lid = lid_blank
    dimple, dimple_at = dimple_cutter((pivx, pivy), H)
    lid = lid - cyl_z(pivx, pivy, z_lid0 - 0.1, pin_top + 0.1, PIVOT_D + 0.2) - cyl_z(mx, my, z_lid0 - 0.1, z_lid0 + 1.6, 4.2)
    if not os.environ.get("CASE_NO_DIMPLE"):
        lid = blend_dimple(lid - dimple, dimple_at)
    trim_l = trim_ring(z_lid0, z_lid0 + TRIM["h"], False)
    p["lid"] = lid
    p["lid_seam_trim"] = trim_l
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
                j1_front=jx0, skin_x_at_j1=xs_j, pin_top=pin_top, pebble=PB.PEB, dimple=dimple_at, dish=dict(rw0=rw0, rw1=rw1, post_ax=post_ax), field=FIELD, flare_ax=FLARE_AX, pocket_half=pw,
                pin_holder=holder_meta, rests=dict(top=zb + BAND_W / 2 - REST_DROP, r_top=REST_R_TOP, r_side=REST_R_SIDE, strip=FLANK_STRIP),
                pin_nets={f"pin_P{PIN_NO[PAD_NETS[k]]}_{PAD_NETS[k]}": PAD_NETS[k] for k in range(4)},
                placement=dict(path=PL["path"], x=PL["x"], d=PL["d"], t=PL["t"], zc=PL["zc"], r_face=PL["r_face"], pitch=PL["pitch"],
                               pads=PL["pads"], recess=PAD_RECESS), ring_files=[RING_STEP_N.format(n=n) for n in SIZES], joy_deg={n: joy_deg(n) for n in SIZES})
    # r4: the boards as read, the cavity, the retainer and the leads
    meta.update(boards=dict(main_file=mb["file"], pins_file=pb["file"], main_thickness=mb["thickness"], pins_thickness=pb["thickness"],
                            main_outline=mb["outline_case"], main_u_range=mb["u_range"], main_d_range=mb["d_range"], main_back_side=mb["back_side"],
                            main_no_model=mb["no_model"], main_parts=mb["parts"], pins_islands=pb["islands"], pins_pins=pb["pins"], pins_pads=pb["pads"],
                            main_pads={k: v for k, v in pads1.items() if k[0] in "WT"}, j1_body_front_u=CB.body_u_front(boards, "J1"),
                            tab=dict(x=tab_x, y=(tab_y0, tab_y1))),
                cavity=dict(x0=cav_x0, x1=cav_x1, y0=cav_y0, y1=cav_y1, z0=pcb1_z0 - 0.35, z1=ceil_z, low=dict(x0=x_lay + 1.5, x1=cav_x1, y0=-CAV_YH, y1=CAV_YH, z0=ZP, z1=ceil_z), lead_pocket=[[lead_pocket.bounding_box().min.X, lead_pocket.bounding_box().max.X], [lead_pocket.bounding_box().min.Y, lead_pocket.bounding_box().max.Y], [lead_pocket.bounding_box().min.Z, lead_pocket.bounding_box().max.Z]]),
                retainer=ret_meta, leads=lead_meta, holder_recess=dict(depth=REC_D, z_top=rec_z1), slot=dict(x0=x_b - REC_D - 0.3, x1=x_b + 4.0, y=4.0),
                th1_bead=dict(x=bead_x, y=bead_y, z=bead_z, d=TH1_D), stack=dict(foam_free=FOAM_FREE, foam_model=cell_z0 - ZP - 2 * LEAD_GAP,
                                                                                  sheet=pcb1_z0 - cell_z0 - CELL["t"] - 2 * LEAD_GAP))
    return p, rings, meta


def swept_wire(pts, d):
    """a wire of diameter d along the polyline pts (axis): one cylinder per segment and a ball at every point (round bends and round ends).
    Returned as a compound of solids (no boolean between them: the lead's own pieces overlap, as one wire)."""
    r = d / 2
    kids = [Pos(*q) * Sphere(r) for q in pts]
    for a, b in zip(pts[:-1], pts[1:]):
        v = Vector(*b) - Vector(*a)
        if v.length < 1e-6:
            continue
        kids.append(Solid.make_cylinder(r, v.length, __import__("build123d").Plane(origin=Vector(*a), z_dir=v.normalized())))
    return Compound(children=kids)


def board_retainer(mb, x0, top, z0, ceil_z, cav_x1, leads, x_c0):
    """printed board retainer: a web RET web_t thick under the ceiling (LEAD_GAP below it) over the main board, with the socket and the wire zone left
    open; posts RET post_d down to LEAD_GAP above the board's top face at spots at least RET clr from every part body and lead; a fence between the
    board's +X edge and the cavity's +X wall over RET fence_y. Returns (solid, meta)."""
    parts = mb["parts"]
    xs = [x_ for x_, y_ in mb["outline_case"]]
    ys = [y_ for x_, y_ in mb["outline_case"]]
    bx0, bx1, by0, by1 = x0, max(xs), min(ys), max(ys)
    w1 = ceil_z - LEAD_GAP
    w0 = w1 - RET["web_t"]
    # keep-outs in plan: bodies that reach above the web's underside less RET clr, and every lead segment above the board
    tall = [v for k, v in parts.items() if v["z"][1] > w0 - RET["clr"]]
    lead_boxes = []
    for nm, (pts, d_) in leads.items():
        for a, b in zip(pts[:-1], pts[1:]):
            if max(a[2], b[2]) > top:
                lead_boxes.append((min(a[0], b[0]) - d_ / 2, max(a[0], b[0]) + d_ / 2, min(a[1], b[1]) - d_ / 2, max(a[1], b[1]) + d_ / 2, max(a[2], b[2]) + d_ / 2))
    rp = RET["post_d"] / 2
    m = rp + RET["clr"]
    cands = []
    for gx in np.arange(bx0 + m, bx1 - m + 1e-9, 0.25):
        for gy in np.arange(by0 + m, by1 - m + 1e-9, 0.25):
            ok = all(not (v["x"][0] - m < gx < v["x"][1] + m and v["y"][0] - m < gy < v["y"][1] + m) for v in parts.values())
            ok = ok and all(not (lb[0] - m < gx < lb[1] + m and lb[2] - m < gy < lb[3] + m) for lb in lead_boxes)
            if ok:
                cands.append((gx, gy))
    if len(cands) < 3:
        raise RuntimeError("board retainer: only %d free post spots on the board" % len(cands))
    C_ = np.array(cands)
    # four posts spread over the board: start at the spot nearest the board's centre-of-area corner, then farthest-point picks
    picks = [int(np.argmin(np.hypot(C_[:, 0] - bx1, C_[:, 1] - by1)))]
    while len(picks) < 4:
        dmin = np.min([np.hypot(C_[:, 0] - C_[i, 0], C_[:, 1] - C_[i, 1]) for i in picks], axis=0)
        picks.append(int(np.argmax(dmin)))
    posts = [tuple(map(float, C_[i])) for i in picks]
    web = box(bx0, cav_x1 - LEAD_GAP, by0, by1, w0, w1)
    for v in tall:
        web = web - box(v["x"][0] - RET["clr"], v["x"][1] + RET["clr"], v["y"][0] - RET["clr"], v["y"][1] + RET["clr"], w0 - 1, w1 + 1)
    for lb in lead_boxes:
        if lb[4] > w0 - RET["clr"]:
            web = web - box(lb[0] - RET["clr"], lb[1] + RET["clr"], lb[2] - RET["clr"], lb[3] + RET["clr"], w0 - 1, w1 + 1)
    sol = web
    for (px_, py_) in posts:
        sol = sol + cyl_z(px_, py_, top + LEAD_GAP, w0 + 0.01, RET["post_d"])
    fy0, fy1 = max(RET["fence_y"][0], by0), min(RET["fence_y"][1], by1)
    fence = box(bx1 + LEAD_GAP, cav_x1 - LEAD_GAP, fy0, fy1, z0, w0 + 0.01)
    sol = sol + fence
    sol = sol.clean() if hasattr(sol, "clean") else sol
    meta = dict(posts=posts, post_d=RET["post_d"], post_len=w0 - top - LEAD_GAP, web=(w0, w1), web_t=RET["web_t"], fence=dict(x=(bx1 + LEAD_GAP, cav_x1 - LEAD_GAP), y=(fy0, fy1), z=(z0, w0)),
                n_solids=len(sol.solids()), volume=float(sol.volume), free_spots=len(cands), tall_cut=[k for k, v in parts.items() if v["z"][1] > w0 - RET["clr"]])
    return sol, meta


def pin_ys():
    """Pin y positions: the pad y of the middle size (US 10) for each pin (pads sit at r sin(theta); the pin row is straight)."""
    out = []
    for k in range(4):
        out.append(round(pad_face_xy(10, k)[1], 3))
    return out


def make_pin(xb, y, z, h):
    """Pin axis along X, base plane at x = xb, tip pole at x = xb - h; flange 1.50 x 0.40, body 1.06 to 1.85 from the base, plunger 0.6, dome 0.3 radius."""
    r = PIN["plunger_d"] / 2
    barrel = cyl_x(xb - PIN["barrel_h"], xb, y, z, PIN["barrel_d"]) + cyl_x(xb - PIN["flange_h"], xb, y, z, PIN["flange_d"])
    dome = Pos(xb - h + r, y, z) * Sphere(r)
    ln = (xb - PIN["barrel_h"] + 0.01) - (xb - h + r)
    if ln > 0.02:
        return barrel + cyl_x(xb - h + r, xb - PIN["barrel_h"] + 0.01, y, z, PIN["plunger_d"]) + dome
    return barrel + dome


def size_text(parts):
    names = ("shell", "base_plate", "lid", "hinge_pivot", "foot")
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
    for n in ("shell", "base_plate", "lid", "post", "hinge_pivot", "pin_holder", "board_retainer"):
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
