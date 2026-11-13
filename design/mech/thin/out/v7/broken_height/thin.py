#!/usr/bin/env python3
"""3D inside model v7 of the thin AI recorder ring (architecture.md 17.29, 17.30): exterior ring-merged32h (round opening 5.6);
round joystick: frame FRM1 (ring 5.40 / 4.80, 0.80 under to 0.50 over the surface) and cap CAP1 (4.40, rim 1.400 above the frame
top, edge 0.30, dish 0.25, ridges at 0.7 / 1.3 / 1.9, flange 6.9 x 6.4 x 0.4); recording light removed (no LED1, LG1, LP1, board
hole, foam notch, print window); pads, motor, cell, slots, seals as v6.3.

(Docstring of v5 follows.)  3D inside model v5 of the thin AI recorder ring (architecture.md 17.11, 17.15 correction, 17.19, 17.21, 17.22, 17.23).

v5 against v4: exterior ring-merged32f.step (it carries the joystick opening 6.6 X x 5.6 band and the two underside
microphone holes and seats); joystick nub, frame and opening turned 90 degrees (nub 4.6 along X); top-port microphones
SPK0641HT4H-1 under the board with floor pockets, gaskets and membranes (no wall slots); recording light on the top-view
LED1 with the light guide LG1, foam notch and LP1 on the real 2.951 ledge, cable bond drawn; U11, C83, C84 for the motor;
glass seat lowered 0.05 with a seal ring; a dam round the joystick's switch head.

(Docstring of v4 follows.)  3D inside model v4 of the thin AI recorder ring (architecture.md sections 17, 17.11 and 17.12).

v4: ONE control (joystick at -78 deg on the -Y side, five switches: four directions plus SW2 under the nub's centre), no record
button, four charging pads on the INSIDE face of the band at 180 deg set in the resin liner, ribbons embedded in the liner,
motor on the joystick side, cell from +Y to the joystick, recording light on a reverse-mount LED through the board.
(Docstring of v2 follows.)  3D inside model v2 of the thin AI recorder ring (architecture.md sections 17 and 17.7).

v2: the shell is the exterior helper's body (imported STEP), cavities cut in it; parts are detailed
sub-solids, each part one node with children `<part>__<class>`; curved parts are true curved solids.
Axes: X along the finger (+X fingertip), Y across (+Y thumb), Z up; origin centre of the block underside.
Band axis along X at Z = ZC. Angles from the top, plus toward +Y.
Writes placement.csv, layers.json, out/thin-inside.glb, out/thin-inside.step.
Env: THIN_EXTERIOR=<step file> (default ring-merged32b.step if it exists, else ring-merged32.step),
     THIN_OVERRIDE="motor_angle=-60" (P keys).  The v1 box model is kept as thin_v1.py.
"""
import os
import sys
import csv
import json
import math
import copy
import struct
from pathlib import Path

from build123d import (Box, Cylinder, Sphere, Pos, Rot, Solid, Wire, Face, Vector, Axis, Compound,
                       fillet, export_step, import_step)

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
EXT_DIR = Path((__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/look/s1/out"))
EXT_FILE = os.environ.get("THIN_EXTERIOR") or str(EXT_DIR / ("ring-merged32h.step"))   # v7: the accepted exterior merged32h (round joystick)
CLASSES = ["metal", "gold", "pcb", "chip", "ceramic", "polymer", "glass", "screen", "foam", "flex", "cell", "resin", "mark"]

P = dict(
    band_w=8.0, band_t=2.6, bore_d=18.95, bore_gap=0.4,
    board_x=27.2, board_y=12.6, board_t=0.30, scr_x=27.35, scr_y=12.8, scr_t=0.80, lit_x=21.6, lit_y=10.8,
    adh_t=0.10, foam_t=0.10, under=1.00, gap=0.05, pad_t=0.02,
    liner_t=0.30, flex_t=0.15, sw_t=0.53, plate_t=0.40, shell_t=0.50, shell_edge=0.60, travel=0.15,
    joy_deg=-78.0, motor_angle=-44.0, motor_pocket_angle=-44.0, motor_x=0.7,
    pcm_a0=39.5, cell_gap_mm=0.2, cell_clear=0.15,
    motor_d=5.0, motor_t=2.5, cell_t=1.6, cell_w=6.0, prot=(1.5, 5.0),
    pad_deg=180.0, pad_d=1.6, pad_pitch=2.4, cpad_t=0.07, joy_sw_off=2.4,
    pad_x=-1.0,          # v6.3 (architecture 17.28, G01): the pad row at X -1.0 (toward the hand end, ring -X) where the case pins stand (case.py PAD_X_OFF)
    pad_margin=0.45,     # v6.3: cable land beyond the pad edge, all round (the check needs 0.30)
    # v5: every pair below is (along X, around the band) (17.11; 17.15 correction)
    flange=(6.9, 6.4), opening=(5.6, 5.6), pocket=(7.0, 6.8),   # v6: flange 6.9 along X (K12); v7: opening round 5.6 (merged32h)
    # v7 (architecture 17.29, exterior merged32h H32): round frame FRM1 and round textured cap CAP1
    frame_od=5.40, frame_id=4.80, frame_below=0.80, frame_proud=0.50,
    cap_d=4.40, cap_rim=0.900,   # BROKEN COPY: the cap at its old height (v6.3 nub 0.900 above the frame)
     cap_edge=0.30, cap_dish=0.25, ridge_rs=(0.70, 1.30, 1.90), ridge_w=0.25, ridge_h=0.08,
    roof_gap=0.05, stiff=(6.4, 6.4), stiff_t=0.075,      # v6: channel roof 0.05 over the flange (K12); stiffener under the head (K13)
    dam_gap=0.05, dam_wx=0.25, dam_wt=0.15, dam_cell=0.10,
    tail_w=1.4, tail_x=-2.6, tail_y=5.9, slot_x=-2.5, slot_w=2.0,   # v6.2: slots X -3.5 to -1.5: the ruling X -1.3 plus the allowed extra 0.20 (US 12, out/v6/probe_extra_cut.log)
    head_x=3.2, head_t=3.2,
    # microphones (17.19; mic-path.md section 4 and 5)
    mic_x=10.8, mic_y=-4.8, mic_port_x=11.77, mic_pocket=(4.4, 3.35), mic_pocket_cx=10.8, mic_pocket_cy=-4.775,
    # screen ledge and cable bond (light-path.md section 4; the light itself is removed in v7, architecture 17.30)
    ledge=2.951, bond_x1=-12.775, bond_y=(-6.198, 6.204),
    # glass seat seal (K-A4)
    seal_t=0.05,
    wall_min=0.30,       # v6.2: least metal between the motor pocket and the block's cavity (17.27)
    motor_glue=0.05,     # v6.1: glue line all round the motor, the pocket floor included
)
_OVR = {}
if os.environ.get("THIN_OVERRIDE"):
    for kv in os.environ["THIN_OVERRIDE"].split(","):
        k, v = kv.split("=")
        P[k] = float(v)
        _OVR[k] = float(v)

# v6 (architecture 17.24, K24 and K25): values per ring size, chosen by the bore (nearest row). The joystick (-78), the pads,
# the block, the board and every part in the block are the same at every size. Bores from design/look/s1/out/measures-merged32f-usN.json.
# pcm_a0: start of the protection circuit, 0.30 mm of arc past the point where the +Y ribbon (outer face Y 5.975) meets the liner
#   face, never below v5's 39.5 (out/v6/table_formulas.log). slot_z0: bottom of the two floor slots, 0.05 below the point where
#   the channel (it ends at 30 deg) starts at the slot's inner edge Y 5.6, never above v5's -0.2 (same log). The slot is deepened
#   instead of opening the channel: it removes metal only in its slot section (v6.2: 2.0 x 0.6), the channel would remove it over 6.8 mm of width.
# motor_angle: the first angle (0.5 deg steps) that keeps the motor out of the block interior (out/v6/scan_us7.log .. scan2_us10_13.log),
# pocket at the same angle. v6.1: on US 10 to 13 the first angle that also keeps 0.30 of metal between the motor pocket and the
# block cavity (out/v6/scan_wall_10_13.log); US 7, 8, 9 have none that keeps 0.05 to SW1 and the dam (scan_wall_7_9.log): v6 angles kept.
# joy_deg: -84 at US 7, -81 at US 8, -78 from US 9 (architecture 17.25).
SIZE_TABLE = {
    #       bore     joy_deg motor_angle pcm_a0 slot_z0 motor_window   (joystick per size: 17.25; window: 17.27)
    7:  (17.3196, -84.0, -47.0, 43.8, -0.20, 1),
    8:  (18.1324, -81.0, -45.5, 41.5, -0.20, 1),
    9:  (18.9452, -78.0, -44.0, 39.5, -0.23, 1),
    10: (19.7580, -78.0, -45.0, 39.5, -0.63, 0),
    11: (20.5708, -78.0, -43.5, 39.5, -1.04, 0),
    12: (21.3836, -78.0, -42.5, 39.5, -1.45, 0),
    13: (22.1964, -78.0, -42.5, 39.5, -1.85, 0),   # v6.2: -42.5 for 0.30 to the -Y slot (out/v6/probe_us13_angles.log)
}
US_SIZE = min(SIZE_TABLE, key=lambda k: abs(SIZE_TABLE[k][0] - P["bore_d"]))
if abs(SIZE_TABLE[US_SIZE][0] - P["bore_d"]) > 0.05:
    raise RuntimeError(f"bore {P['bore_d']} is not a ring size of SIZE_TABLE")
for _k, _v in zip(("joy_deg", "motor_angle", "pcm_a0", "slot_z0", "motor_window"), SIZE_TABLE[US_SIZE][1:]):
    if _k not in _OVR:
        P[_k] = _v
if "motor_pocket_angle" not in _OVR:
    P["motor_pocket_angle"] = P["motor_angle"]

R_IN = P["bore_d"] / 2
ZC = -P["bore_gap"] - R_IN
R_LINER = R_IN + P["liner_t"]
R_OUT = R_IN + P["band_t"]
R_SW0 = R_LINER                      # switch base underside (v6: on the flat ribbon head over the stiffener, K13)
R_SW1 = R_SW0 + P["sw_t"]
R_PL1 = R_SW1 + P["travel"] + P["plate_t"]   # plate (the nub's flange) stands 0.15 above the switch tops
R_F0 = R_IN + (P["liner_t"] - P["flex_t"]) / 2    # embedded ribbon: inner face (0.075 of resin under it)
R_F1 = R_F0 + P["flex_t"]
R_CELL_C = R_LINER + P["cell_t"] / 2
SW = (2.6, 1.6, 0.53)
MOTOR_ROOF = 0.1
CHAN_END = 30.0


# ------------------------------------------------------------------ helpers
def vol(s):
    try:
        return s.volume
    except Exception:
        return 0.0


def box(sx, sy, sz, cx, cy, cz):
    return Pos(cx, cy, cz) * Box(sx, sy, sz)


def rbox(sx, sy, sz, cx, cy, cz, r):
    b = fillet(Box(sx, sy, sz).edges().filter_by(Axis.Z), r)
    return Pos(cx, cy, cz) * b


def gpos(a, t, r, x=0.0):
    ar = math.radians(a)
    return (x, r * math.sin(ar) + t * math.cos(ar), ZC + r * math.cos(ar) - t * math.sin(ar))


def rloc(a):
    return Pos(0, 0, ZC) * Rot(-a, 0, 0)


def lplace(a, solid, x=0.0, t=0.0, r=0.0):
    """Place a solid built in the band frame (local z radial) at angle a, offsets x, t, r."""
    return rloc(a) * (Pos(x, t, r) * solid)


def cyl_x(r, x0, x1):
    return Pos((x0 + x1) / 2, 0, ZC) * Cylinder(r, x1 - x0, rotation=(0, 90, 0))


def sector(r0, r1, a0, a1, x0, x1):
    def pt(x, r):
        ar = math.radians(a0)
        return Vector(x, r * math.sin(ar), ZC + r * math.cos(ar))
    w = Wire.make_polygon([pt(x0, r0), pt(x1, r0), pt(x1, r1), pt(x0, r1)], close=True)
    return Solid.revolve(Face(w), a1 - a0, Axis((0, 0, ZC), (-1, 0, 0)))


def arcspan(a0, a1):
    """angles from a0 going through the bottom to a1 (a1 may be negative); returns (start, sweep) in 0..360."""
    s = a0 % 360
    e = a1 % 360
    return s, (e - s) % 360


def sector_through(r0, r1, a0, a1, x0, x1):
    s, sw = arcspan(a0, a1)
    return sector(r0, r1, s, s + sw, x0, x1)


def compound(solids):
    solids = [s for s in solids if s is not None]
    return Compound(children=solids) if len(solids) != 1 else solids[0]


def fuse(shapes):
    s = shapes[0]
    for o in shapes[1:]:
        s = s + o
    return s


def quarter(cx, cz, r_in, r_out, sx, sz, width, y=0.0):
    """Quarter ring about an axis along Y at (cx, cz); quadrant signs sx, sz."""
    ring = Pos(cx, y, cz) * Cylinder(r_out, width, rotation=(90, 0, 0))
    ring = ring - Pos(cx, y, cz) * Cylinder(r_in, width + 1, rotation=(90, 0, 0))
    q = Pos(cx + sx * r_out / 2, y, cz + sz * r_out / 2) * Box(r_out, width + 2, r_out)
    return ring & q


def dome(a_r, h):
    R = (a_r ** 2 + h ** 2) / (2 * h)
    return (Pos(0, 0, h - R) * Sphere(R)) & Pos(0, 0, h / 2) * Box(2 * a_r + 0.2, 2 * a_r + 0.2, h)


# ------------------------------------------------------------------ the exterior
def load_exterior():
    s = import_step(EXT_FILE)
    by = {c.label: c for c in s.children}
    return by["body"], by["glass"], by.get("contacts"), by.get("joystick"), by.get("button")


def probe_outer1(body, a, x=0.0):
    ar = math.radians(a)
    r = 14.5
    while r > 5:
        if body.is_inside(Vector(x, r * math.sin(ar), ZC + r * math.cos(ar))):
            return round(r, 3)
        r -= 0.01
    return None


def probe_outer(body, a):
    """Outer radius of the exterior body at angle a. v5: merged32f has the joystick opening (6.6 along X) at this angle, so
    X 0 and +-3 lie in the hole (v4 crashed here, min() of None); probe just outside the opening's X edges, at +-(3.3 + 0.05)."""
    hx = P["opening"][0] / 2 + 0.05
    rs = [r for r in (probe_outer1(body, a, x) for x in (hx, -hx)) if r is not None]
    if not rs:
        raise RuntimeError(f"probe_outer: no metal at angle {a} at X +-{hx}")
    return min(rs)


# ------------------------------------------------------------------ model
class Part:
    def __init__(self, name, ref, layer, centre, size, angle=None, metal=False, note=""):
        self.name, self.ref, self.layer, self.centre, self.size = name, ref, layer, centre, size
        self.angle, self.metal, self.note = angle, metal, note
        self.subs = {}

    def add(self, cls, solid):
        assert cls in CLASSES, cls
        if solid is not None:
            self.subs.setdefault(cls, []).append(solid)
        return self

    def solids(self):
        return {c: compound(v) for c, v in self.subs.items()}


def build():
    body0, glass, contacts0, joy_ext, btn_ext = load_exterior()
    gcentre = glass & Pos(0, 0, 3) * Box(0.05, 0.05, 6)
    Z_GB = round(gcentre.bounding_box().min.Z, 4)
    Z_AD0 = Z_GB - P["adh_t"]
    Z_SC0 = Z_AD0 - P["scr_t"]
    Z_BD1 = Z_SC0 - P["foam_t"]
    Z_BD0 = Z_BD1 - P["board_t"]
    Z_UB0 = Z_BD0 - P["under"]
    Z_FLOOR = Z_UB0 - P["gap"]
    ZTOP = Z_BD0 - P["pad_t"]                 # top of every part hanging under the board
    ctx = dict(Z_GB=Z_GB, Z_AD0=Z_AD0, Z_SC0=Z_SC0, Z_BD0=Z_BD0, Z_BD1=Z_BD1, Z_UB0=Z_UB0, Z_FLOOR=Z_FLOOR,
               Z_GT=glass.bounding_box().max.Z, exterior=EXT_FILE)
    parts = []

    def newp(*a, **k):
        p = Part(*a, **k)
        parts.append(p)
        return p

    pads = []                                  # (cx, cy, sx, sy) gold pad rectangles on the board underside

    # ---------- under-board parts (all hang from ZTOP)
    def ball_chip(name, ref, sx, sy, h, cx, cy, cols, rows, pitch, bd, skip, note):
        stand = bd * 0.75
        p = newp(name, ref, "board", (cx, cy, ZTOP - stand - h / 2), (sx, sy, h), None, True, note)
        p.add("chip", box(sx, sy, h, cx, cy, ZTOP - stand - h / 2))
        p.add("mark", box(sx - 0.5, sy - 0.5, 0.012, cx, cy, ZTOP - stand - h - 0.004))
        balls, n = [], 0
        for i in range(cols):
            for j in range(rows):
                if n >= cols * rows - skip and False:
                    continue
                bx = cx + (i - (cols - 1) / 2) * pitch
                by_ = cy + (j - (rows - 1) / 2) * pitch
                if (i in (0, cols - 1)) and (j in (0, rows - 1)) and skip > 0 and (i, j) in [(0, 0), (cols - 1, rows - 1)][:skip]:
                    continue
                balls.append(Pos(bx, by_, ZTOP - bd / 2) * Sphere(bd / 2))
                pads.append((bx, by_, bd * 0.9, bd * 0.9))
        p.add("metal", compound(balls))
        p.note += f"; {len(balls)} solder balls dia {bd}, pitch {pitch}"
        return p

    ball_chip("main_chip", "U1", 3.02, 2.43, 0.43, 4.0, 0.0, 9, 7, 0.325, 0.20, 2, "nRF54LM20A WLCSP-61 (61 balls: 9 x 7 grid less 2 corners), balls toward the board, marking plate on the exposed face")
    ball_chip("power_chip", "U2", 3.1, 2.4, 0.5, 8.5, 0.0, 7, 5, 0.40, 0.25, 0, "nPM1300 WLCSP-35 (7 x 5 balls); height 0.5 ASSUMED")
    ball_chip("screen_supply_chip", "U4", 2.0, 2.0, 0.58, 4.0, -3.5, 4, 4, 0.40, 0.25, 0, "SGM38046 WLCSP-2x2-16B (4 x 4 balls)")

    def coil(name, ref, sx, sy, h, cx, cy, note):
        cap = 0.30
        p = newp(name, ref, "board", (cx, cy, ZTOP - h / 2), (sx, sy, h), None, True, note)
        p.add("ceramic", box(sx - 2 * cap, sy, h, cx, cy, ZTOP - h / 2))
        for s in (-1, 1):
            p.add("metal", box(cap, sy, h, cx + s * (sx / 2 - cap / 2), cy, ZTOP - h / 2))
            pads.append((cx + s * (sx / 2 - cap / 2), cy, cap, sy * 0.8))
        return p

    coil("screen_supply_coil", "L10", 2.5, 2.0, 1.0, 6.5, -3.5, "wound block with two end caps")
    coil("power_coil_1", "L71", 2.0, 1.6, 1.0, 8.5, 3.2, "nPM1300 buck 1 inductor: wound block, two end caps")
    coil("power_coil_2", "L72", 2.0, 1.6, 1.0, 11.0, 3.2, "nPM1300 buck 1 inductor: wound block, two end caps")

    def xtal(name, ref, sx, sy, cx, cy, note):
        h = 0.5
        p = newp(name, ref, "board", (cx, cy, ZTOP - h / 2), (sx, sy, h), None, True, note)
        p.add("ceramic", box(sx, sy, 0.3, cx, cy, ZTOP - 0.15))
        p.add("metal", box(sx - 0.1, sy - 0.1, 0.2, cx, cy, ZTOP - 0.4))
        for s in (-1, 1):
            pads.append((cx + s * (sx / 2 - 0.25), cy, 0.5, sy * 0.7))
        return p

    xtal("crystal_32M", "X1", 2.0, 1.6, 3.0, 3.0, "ceramic base with metal lid; height 0.5 ASSUMED")
    xtal("crystal_32k", "X2", 2.0, 1.2, 5.5, 3.0, "ceramic base with metal lid; height 0.5 ASSUMED")

    # storage: body + 8 pads
    p = newp("storage", "U3", "board", (-5.0, 0.0, ZTOP - 0.05 - 0.375), (8.0, 6.2, 0.75), None, True,
             "CSNP32GCR01-BOW LGA-8: 8 gold pads 0.7 x 0.5 (positions ASSUMED), marking plate on the exposed face")
    p.add("chip", box(8.0, 6.2, 0.75, -5.0, 0.0, ZTOP - 0.05 - 0.375))
    p.add("mark", box(6.0, 3.0, 0.012, -5.0, 0.0, ZTOP - 0.05 - 0.756))
    for ix in range(4):
        for iy in (-1, 1):
            px, py = -5.0 + (ix - 1.5) * 1.8, iy * 2.4
            p.add("gold", box(0.7, 0.5, 0.05, px, py, ZTOP - 0.025))
            pads.append((px, py, 0.8, 0.6))

    # microphones (v5, 17.19): Knowles SPK0641HT4H-1, top port, 4.00 (X) x 3.00 (Y) x 1.00, under the board, port facing the floor
    MH = 1.00
    my = P["mic_y"]
    for nm, ref, sg in (("mic_1", "U5", -1), ("mic_2", "U6", 1)):
        mx, portx = sg * P["mic_x"], sg * P["mic_port_x"]
        p = newp(nm, ref, "board", (mx, my, ZTOP - MH / 2), (4.0, 3.0, MH), None, True,
                 f"Knowles SPK0641HT4H-1 top port 4.00 x 3.00 x 1.00 (mic-path.md section 3), pads up on the board's under face; lid faces -Z with the "
                 f"port dia 0.25 at X {portx:.2f} Y {my:.2f} (1.03 from its block-end edge), over the floor hole; substrate 0.2 / lid 0.8 split ASSUMED")
        p.add("pcb", box(4.0, 3.0, 0.2, mx, my, ZTOP - 0.1))
        lid = box(4.0, 3.0, MH - 0.2, mx, my, ZTOP - 0.2 - (MH - 0.2) / 2)
        port = Pos(portx, my, ZTOP - MH + 0.05) * Cylinder(0.125, 0.1)
        p.add("metal", lid - port)
        for k in range(4):                                    # 8 lands (mic-path.md section 9 item 26), drawn as 2 rows of 4
            for s in (-1, 1):
                pads.append((mx + (k - 1.5) * 0.9, my + s * 1.1, 0.45, 0.5))
        # gasket ring (foam, OD 1.8, bore 1.0) from the pocket bottom (floor top - 0.10) to the lid; membrane disc in the underside seat
        zpb = Z_FLOOR - 0.10
        gk = newp(f"mic_gasket_{1 if sg < 0 else 2}", f"GSK{2 if sg < 0 else 3}", "body", (portx, my, (zpb + ZTOP - MH) / 2), (1.8, 1.8, ZTOP - MH - zpb), None, False,
                  f"foam gasket ring OD 1.8, bore 1.0, PSA both faces (mic-path.md section 5 piece 2), on the pocket bottom Z {zpb:.2f} up to the lid; "
                  f"free thickness chosen per unit 0.10/0.20/0.30, drawn at the nominal gap")
        gk.add("foam", (Pos(portx, my, (zpb + ZTOP - MH) / 2) * Cylinder(0.9, ZTOP - MH - zpb)) - (Pos(portx, my, (zpb + ZTOP - MH) / 2) * Cylinder(0.5, 1.0)))
        mb = newp(f"mic_membrane_{1 if sg < 0 else 2}", f"MEM{1 if sg < 0 else 2}", "body", (portx, my, 0.05), (2.0, 2.0, 0.10), None, False,
                  "acoustic membrane disc dia 2.0, at most 0.10 thick with its adhesive ring, in the 2.0 x 0.10 seat flush with the underside (mic-path.md section 5 piece 6); part not chosen")
        mb.add("polymer", Pos(portx, my, 0.05) * Cylinder(1.0, 0.10))

    # antenna (stands in the board notch)
    p = newp("antenna", "ANT1", "board", (-12.7, 4.4, Z_UB0 + 0.6), (1.6, 3.2, 1.2), None, False,
             "Johanson 2450AT18D0100001E: ceramic body, two metal end terminations (ASSUMED shape); stands in the board notch")
    p.add("ceramic", box(1.6, 2.4, 1.2, -12.7, 4.4, Z_UB0 + 0.6))
    for s in (-1, 1):
        p.add("metal", box(1.6, 0.4, 1.2, -12.7, 4.4 + s * 1.4, Z_UB0 + 0.6))

    # connector J1
    p = newp("screen_connector", "J1", "board", (-12.0, 0.0, ZTOP - 0.45), (3.2, 5.2, 0.9), None, True,
             "FH35C-15S-0.3SHW: housing, latch bar, 15 contacts at 0.3 pitch (shape ASSUMED); tail enters from the hand end")
    p.add("polymer", box(3.2, 5.2, 0.9, -12.0, 0.0, ZTOP - 0.45))
    p.add("metal", box(0.4, 4.8, 0.3, -11.0, 0.0, ZTOP - 0.75))
    for k in range(15):
        yk = (k - 7) * 0.3
        p.add("gold", box(0.2, 0.16, 0.2, -13.0, yk, ZTOP - 0.45))
        pads.append((-12.4, yk, 0.5, 0.16))

    # ---------- motor regulator (v5, architecture 17.22): U11 and its two 0402 capacitors, on the board's under face beside
    # J_BAND_B, where the cell's ribbon (band_flex_away) enters through the +Y floor slot at X -2.2, Y +5.9
    def chip0402(name, ref, cx, cy, note):
        h = 0.5                                                          # 0402 1.0 x 0.5, height 0.5 ASSUMED (10 uF part not chosen)
        p = newp(name, ref, "board", (cx, cy, ZTOP - h / 2), (1.0, 0.5, h), None, True, note)
        p.add("ceramic", box(0.6, 0.5, h, cx, cy, ZTOP - h / 2))
        for s in (-1, 1):
            p.add("metal", box(0.2, 0.5, h, cx + s * 0.4, cy, ZTOP - h / 2))
            pads.append((cx + s * 0.4, cy, 0.3, 0.5))
        return p
    UX, UY = P.get("u11_x", 0.0), P.get("u11_y", 4.2)
    p = newp("motor_regulator", "U11", "board", (UX, UY, ZTOP - 0.2), (1.0, 1.0, 0.4), None, True,
             "TI TLV75530PDQNR 3.0 V 500 mA regulator, X2SON 1.0 x 1.0 x 0.4 (architecture 17.22); input on VBAT, output VMOT to the motor; "
             "beside J_BAND_B (cell ribbon, +Y slot); 4 pads 0.25 x 0.4 ASSUMED")
    p.add("chip", box(1.0, 1.0, 0.4, UX, UY, ZTOP - 0.2))
    p.add("mark", box(0.6, 0.6, 0.012, UX, UY, ZTOP - 0.4 - 0.004))
    for sx_ in (-1, 1):
        for sy_ in (-1, 1):
            pads.append((UX + sx_ * 0.3, UY + sy_ * 0.3, 0.25, 0.4))
    chip0402("motor_cap_in", "C83", UX, UY + 1.25, "10 uF 0402 at U11's input (VBAT), nearest the cell ribbon's land (architecture 17.22)")
    chip0402("motor_cap_out", "C84", UX + 1.2, UY + 0.8, "10 uF 0402 at U11's output (VMOT), also the motor maker's capacitor across its leads (architecture 17.22)")

    # ---------- v7 (architecture 17.30): no recording light: no LED1 and its lands, no light guide LG1, no 0.50 board hole, no foam notch, no LP1
    notch_a = box(1.8, 3.6, 1.0, -13.6 + 0.9, 4.5, Z_BD0 + 0.15)
    outline = rbox(P["board_x"], P["board_y"], P["board_t"], 0, 0, (Z_BD0 + Z_BD1) / 2, 0.8)
    core = rbox(P["board_x"], P["board_y"], P["board_t"] - 0.02, 0, 0, (Z_BD0 + 0.02 + Z_BD1) / 2, 0.8) - notch_a
    mask = rbox(P["board_x"], P["board_y"], 0.02, 0, 0, Z_BD0 + 0.01, 0.8) - notch_a
    p = newp("main_board", "PCB1", "board", (0.0, 0.0, (Z_BD0 + Z_BD1) / 2), (P["board_x"], P["board_y"], P["board_t"]), None, False,
             "27.2 x 12.6 x 0.3, corner radius 0.8 (ASSUMED), antenna notch 1.8 x 3.6; no other hole (v7: the light guide's hole is removed); "
             "solder-mask face with gold pad rectangles under each part")
    p.add("pcb", core)
    p.add("resin", mask)
    p.add("gold", compound([box(sx, sy, P["pad_t"], cx, cy, Z_BD0 - P["pad_t"] / 2) for cx, cy, sx, sy in pads]))

    # ---------- foam, adhesive, screen, glass
    foam = box(P["board_x"], P["board_y"], P["foam_t"], 0, 0, Z_BD1 + P["foam_t"] / 2) - box(P["board_x"] - 2.4, P["board_y"] - 2.4, 1, 0, 0, Z_BD1 + 0.05)   # v7: no notch
    p = newp("foam", "FOAM1", "screen", (0.0, 0.0, Z_BD1 + P["foam_t"] / 2), (P["board_x"], P["board_y"], P["foam_t"]), None, False,
             "frame 1.2 wide round the board edge (the open middle is an ASSUMED shape); no notch (v7)")
    p.add("foam", foam)

    sx0 = -P["scr_x"] / 2
    LG = P["ledge"]
    lower = box(P["scr_x"], P["scr_y"], 0.4, 0, 0, Z_SC0 + 0.2)
    upper = box(P["scr_x"] - LG, P["scr_y"], 0.4, sx0 + LG + (P["scr_x"] - LG) / 2, 0, Z_SC0 + 0.6)
    lit_cx = -29.3 / 2 + 5.33 + P["lit_x"] / 2
    p = newp("screen", "DISP1", "screen", (0.0, 0.0, Z_SC0 + P["scr_t"] / 2), (P["scr_x"], P["scr_y"], P["scr_t"]), None, True,
             f"glass panel; ledge (lower glass only) {LG} long at the hand end, X {sx0:.3f} to {sx0 + LG:.3f}, from the maker's drawing (light-path.md line 11); "
             f"no driver IC drawn on the ledge (the maker drawing shows none, light-path.md line 78); "
             f"lit area 21.6 (X) x 10.8 (Y) centred X {lit_cx:.3f} Y 0; tail bonded on the ledge X {sx0:.3f} to {P['bond_x1']}")
    p.add("screen", lower + upper)
    p.add("mark", box(P["lit_x"], P["lit_y"], 0.01, lit_cx, 0, Z_SC0 + P["scr_t"] - 0.005))
    # tail: bonded on the ledge top (maker drawing: X -13.675 to -12.775, Y -6.198 to 6.204), then bend out, down the hand end, bend under the board end
    tw, tt = 5.0, 0.2
    by0, by1 = P["bond_y"]
    bond = box(P["bond_x1"] - sx0, by1 - by0, tt, (sx0 + P["bond_x1"]) / 2, (by0 + by1) / 2, Z_SC0 + 0.4 + tt / 2)
    zA = Z_SC0 + 0.4 + tt / 2                 # centre line of the bonded tail on the ledge top
    zB = Z_BD0 - 0.12                         # centre line of the run under the board end
    xe = sx0                                  # panel hand end
    rc = 0.2
    pt = newp("screen_tail", "DISP1", "screen", (xe - 0.1, 0.0, (zA + zB) / 2), (0.475, tw, zA - zB + tt), None, True,
              f"tail 0.2 thick: bond on the ledge top {P['bond_x1'] - sx0:.3f} x {by1 - by0:.3f} (maker drawing, light-path.md line 13); then 5.0 wide: "
              f"two 90 degree bends, down the hand end, under the board end to J1 (the maker's tail is 12.4 wide for 11.496 mm: conflict K in thin-notes v5)")
    pt.add("flex", bond)
    pt.add("flex", quarter(xe, zA - rc, rc - tt / 2, rc + tt / 2, -1, +1, tw))
    pt.add("flex", box(tt, tw, (zA - rc) - (zB + rc), xe - rc, 0, ((zA - rc) + (zB + rc)) / 2))
    pt.add("flex", quarter(xe, zB + rc, rc - tt / 2, rc + tt / 2, -1, -1, tw))
    ctx["bond_x"] = (round(sx0, 3), P["bond_x1"])
    ctx["ledge_x"] = (round(sx0, 3), round(sx0 + LG, 3))
    p2 = newp("clear_adhesive", "ADH1", "glass", (0.0, 0.0, Z_AD0 + P["adh_t"] / 2), (P["scr_x"], P["scr_y"], P["adh_t"]), None, False,
              "same outline as the panel: the glass is bonded to the panel over the whole face (architecture 17.30, v7)")
    p2.add("polymer", box(P["scr_x"], P["scr_y"], P["adh_t"], 0, 0, Z_AD0 + P["adh_t"] / 2))
    pg = newp("cover_glass", "GL1", "glass", (0.0, 0.0, (Z_GB + ctx["Z_GT"]) / 2),
              (29.1, 14.56, ctx["Z_GT"] - Z_GB), None, False,
              "the exterior file's formed glass, unchanged (%s); black print outside the lit area with no opening (v7: no light window, architecture 17.30; "
              "the exterior file's separate 'light' skin solid is not used)" % os.path.basename(EXT_FILE))
    pg.add("glass", glass)

    # ---------- body = imported exterior with cavities
    cav = []
    pocket_main = rbox(P["scr_x"] + 0.1, P["scr_y"] + 0.1, 8.0, 0, 0, Z_FLOOR + 4.0, 0.1)
    cav.append(pocket_main)
    cav.append(box(0.55, 5.4, 2.0, -13.775, 0, (Z_BD0 + Z_SC0) / 2))            # tail fold pocket
    # v5: no wall slots; a 0.10 pocket in the floor under each microphone (mic-path.md line 71). Holes and seats are the exterior's.
    mpx, mpy = P["mic_pocket"]
    for sg in (-1, 1):
        cav.append(box(mpx, mpy, 0.20, sg * P["mic_pocket_cx"], P["mic_pocket_cy"], Z_FLOOR))
    ctx["mic_pocket_bottom"] = round(Z_FLOOR - 0.10, 4)
    for sgn in (1, -1):
        # v6: slot from Z_FLOOR + 0.6 down to the size's slot_z0 (it must reach the channel, K25)
        sz1 = Z_FLOOR + 0.6
        cav.append(box(P["slot_w"], 0.6, sz1 - P["slot_z0"], P["slot_x"], sgn * P["tail_y"], (sz1 + P["slot_z0"]) / 2))
    ctx["slot_z0"] = P["slot_z0"]
    cw = (P["band_w"] - 2 * P["shell_edge"]) / 2
    ja = P["joy_deg"]
    r_joy = probe_outer(body0, ja)
    ctx["r_outer_joy"] = r_joy
    # joystick: pocket for the switches and the dam (7.0 along X x 6.8 around the band); the opening through the shell
    # (6.6 along X x 5.6 around the band) is the exterior's own and is not cut again here.
    # v6 (K12): over the joystick the channel is not cut; the pocket's flat roof stands roof_gap (0.05) above the flange top.
    # The channel is cut on both sides up to the radial line where the pocket's band edge (3.4) meets the roof.
    pkx, pkt = P["pocket"]
    roof = R_PL1 + P["roof_gap"]
    dlt = math.degrees(math.asin((pkt / 2) / roof))
    chan = (sector_through(R_IN, R_OUT - P["shell_t"], CHAN_END, ja - dlt, -cw, cw)
            + sector_through(R_IN, R_OUT - P["shell_t"], ja + dlt, -CHAN_END, -cw, cw)
            + sector_through(R_IN, R_LINER, ja - dlt, ja + dlt, -cw, cw))
    cav.append(chan)
    zlow = R_IN - 0.3
    # v6: the pocket is 7.0 along X from the bore up to the roof, so the one-piece nub with its 6.9 flange goes in straight from the
    # bore side before the liner is cast (assembly.md step 13); the channel elsewhere is 6.8 (the liner's cast fills the 0.1 each side)
    pocket_j = lplace(ja, Box(pkx, pkt, roof - zlow), r=(roof + zlow) / 2)
    cav.append(pocket_j)
    ctx["pocket_j"] = (pkx, pkt, round(R_LINER, 4), round(roof, 4))
    ctx["joy_span_deg"] = round(dlt, 3)
    # glass seat (K-A4): lowered 0.05 under the glass's own footprint, outside the panel pocket; the seal ring fills it
    gface = [fc for fc in glass.faces() if abs(fc.normal_at().Z + 1) < 1e-6 and abs(fc.bounding_box().min.Z - Z_GB) < 1e-4]
    seat = Solid.extrude(gface[0], Vector(0, 0, -P["seal_t"])) - pocket_main
    cav.append(seat)
    # motor pocket (the motor stands beside the ribbon: x offset)
    # v6.1: the pocket floor is motor_glue (0.05) below the motor's back face; in v6 the floor was the back face itself, so metal
    # that the channel and liner do not reach (near the channel end at 30 deg) touched the motor's back edge (out/v6/probe_gap_us*.log)
    mh = P["motor_t"] + MOTOR_ROOF + P["motor_glue"]
    motor_cut = lplace(P["motor_pocket_angle"], Cylinder((P["motor_d"] + 0.2) / 2, mh), x=P["motor_x"], r=R_LINER - P["motor_glue"] + mh / 2)
    cav.append(motor_cut)
    ctx["motor_cut"] = motor_cut
    ctx["panel_cut"] = pocket_main
    body = copy.deepcopy(body0)
    for c in cav:
        body = body - c
    # v6.2 (architecture 17.27): on the sizes flagged in SIZE_TABLE (US 7, 8, 9) the motor pocket opens into the block's cavity
    # through a window: all metal within wall_min (0.30) of both the motor pocket and the cavity is removed, so every edge left
    # is at least 0.30 thick. Construction: the pocket cylinder grown by 0.30 (radius and both ends) intersected with the cavity
    # (panel pocket) grown by 0.30 (plan and floor). The window is sealed (SEAL2) from the band side, 0.05 clear of the motor.
    ctx["window"] = None
    if P["motor_window"]:
        wm = P["wall_min"]
        grow_m = lplace(P["motor_pocket_angle"], Cylinder((P["motor_d"] + 0.2) / 2 + wm, mh + 2 * wm), x=P["motor_x"],
                        r=R_LINER - P["motor_glue"] + mh / 2)
        grow_p = rbox(P["scr_x"] + 0.1 + 2 * wm, P["scr_y"] + 0.1 + 2 * wm, 8.0 + 2 * wm, 0, 0, Z_FLOOR + 4.0, 0.1 + wm)
        window = grow_m & grow_p
        removed = body & window
        body = body - window
        ctx["window"] = window
        ctx["window_removed"] = removed
        ctx["grow_m"], ctx["grow_p"] = grow_m, grow_p
    pb = newp("outer_body", "", "body", (0.0, 0.0, 1.6), (29.3, 14.75, 3.2), None, True,
              "the exterior helper's body (%s: it carries the joystick opening 6.6 x 5.6 and the two microphone holes dia 1.0 with seats dia 2.0 x 0.10) "
              "with cavities cut in it here: panel pocket, tail pocket, 2 microphone floor pockets 0.10 deep, 2 floor slots, band channel, joystick pocket, "
              "motor pocket, glass seat lowered 0.05; band %.1f x %.1f (width x thickness)" % (os.path.basename(EXT_FILE), P["band_w"], P["band_t"]))
    pb.add("metal", body)
    # seal ring under the glass edge (K-A4), 0.05 thick, in the lowered seat
    sl = newp("glass_seal", "SEAL1", "glass", (0.0, 0.0, Z_GB - P["seal_t"] / 2), (29.1, 14.56, P["seal_t"]), None, False,
              "perimeter seal ring 0.05 thick between the glass underside and the body's seat, which is lowered 0.05 inside the body under the glass footprint "
              "(assembly.md K-A4, step 23: die-cut double-sided waterproof acrylic tape PROPOSED there); the outer shape does not change")
    sl.add("polymer", seat)
    if ctx["window"] is not None:
        motor_off = lplace(P["motor_angle"], Cylinder(P["motor_d"] / 2 + P["motor_glue"], P["motor_t"] + 2 * P["motor_glue"]), x=P["motor_x"],
                           r=R_LINER + P["motor_t"] / 2)
        seal2 = ctx["window_removed"] - motor_off
        ctx["seal2"] = seal2
        ctx["motor_off"] = motor_off
        bb = seal2.bounding_box()
        s2 = newp("motor_window_seal", "SEAL2", "body", (round(bb.center().X, 3), round(bb.center().Y, 3), round(bb.center().Z, 3)),
                  (bb.size.X, bb.size.Y, bb.size.Z), None, False,
                  f"sealant plug in the window between the motor pocket and the block's cavity (US {US_SIZE}, architecture 17.27), applied from the band side "
                  f"with the floor-slot sealant before the liner is cast, 0.05 clear of the motor; volume {seal2.volume:.4f} mm3")
        s2.add("polymer", seal2)
    # envelope for the inside test: the exterior body before the cavities, with its own openings filled (the parts in them are inside the ring's outline)
    fills = [lplace(ja, Cylinder(P["opening"][0] / 2 + 0.02, r_joy - (R_IN - 0.3)), r=(r_joy + R_IN - 0.3) / 2) & cyl_x(r_joy, -10, 10)]   # v7: round opening
    for sg in (-1, 1):
        fills.append(Pos(sg * P["mic_port_x"], P["mic_y"], 0.15) * Cylinder(1.02, 0.30))
    envelope = fuse([body0] + fills)
    if contacts0 is not None:
        envelope = envelope + contacts0
    ctx["envelope"] = envelope

    # ---------- band parts (v4)
    cw_l = cw
    ja = P["joy_deg"]
    mA, mX = P["motor_angle"], P["motor_x"]
    tw_, tx = P["tail_w"], P["tail_x"]
    R_FM = (R_F0 + R_F1) / 2
    sgn_y = {"thumb": -1, "away": 1}              # the joystick side is -Y (17.11): band_flex_thumb serves it
    a_in = math.degrees(math.asin(P["tail_y"] / R_FM))        # where the vertical ribbon meets the embedded layer
    z_in = ZC + math.sqrt(R_FM ** 2 - P["tail_y"] ** 2)
    z_top = Z_BD0
    ang = lambda mm, r: math.degrees(mm / r)

    # cell: from the +Y end (protection circuit after the slot) through the bottom to the joystick
    pang = ang(P["prot"][0], R_CELL_C)
    pa0 = P["pcm_a0"]
    cell_s = pa0 + pang + ang(P["cell_gap_mm"], R_CELL_C)
    dam_out_t = P["head_t"] + P["dam_gap"] + P["dam_wt"]               # v5: the dam's outer face around the band (K-A3)
    cell_e = 360.0 + ja - math.degrees(math.asin((dam_out_t + P["dam_cell"]) / R_LINER))   # v5: clears the dam by 0.10 (v4: switch footprint + 0.15)
    ctx["cell_end_clear_t"] = round(dam_out_t + P["dam_cell"], 3)
    sw = cell_e - cell_s
    P["cell_a0"], P["cell_a1"] = cell_s, cell_e - 360.0
    ctx["cell_start_deg"], ctx["cell_end_deg"], ctx["cell_sweep_deg"] = round(cell_s, 3), round(cell_e - 360.0, 3), round(sw, 3)

    # ribbons (embedded in the liner): pieces as (r0, r1, a0, a1, x0, x1)
    ribbon = {"thumb": [], "away": []}
    ja_h = math.degrees(P["head_t"] / R_FM)
    head_a0, head_a1 = ja - ja_h, ja + ja_h                    # head under the switches (negative angles)
    # v6 (K13): the head is flat, 6.4 x 6.4 x 0.15, its top face is the switch bases' face (local z R_SW0); a flat stiffener
    # 6.4 x 6.4 under it; the liner fills under the stiffener. Stiffener thickness from the geometry: the head's top stays at
    # R_SW0 = R_LINER (nothing above moves) and 0.075 of resin stays under the stiffener at its middle (as under every ribbon):
    # t = liner 0.30 - head 0.15 - resin 0.075 = 0.075.
    stf_t = P["liner_t"] - P["flex_t"] - (P["liner_t"] - P["flex_t"]) / 2
    assert abs(stf_t - P["stiff_t"]) < 1e-9
    ZH1, ZH0 = R_SW0, R_SW0 - P["flex_t"]
    ZS0 = ZH0 - stf_t
    head_flat = lplace(ja, Box(2 * P["head_x"], 2 * P["head_t"], P["flex_t"]), r=(ZH0 + ZH1) / 2)
    stiffener = lplace(ja, Box(P["stiff"][0], P["stiff"][1], stf_t), r=(ZS0 + ZH0) / 2)
    liner_fill = (lplace(ja, Box(P["stiff"][0], P["stiff"][1], ZS0 - (R_IN - 0.3)), r=(ZS0 + R_IN - 0.3) / 2) - cyl_x(R_IN, -10, 10))
    # bend: from the head's edge (band +3.2, toward the slot) down into the embedded layer at band 3.6 (beyond the dam)
    phi = math.asin(3.6 / R_FM)
    def jp(t, z):                               # joystick frame (t around the band, z radial) to the model axes
        a = math.radians(ja)
        return Vector(0, z * math.sin(a) + t * math.cos(a), ZC + z * math.cos(a) - t * math.sin(a))
    bpts = [(P["head_t"], ZH0), (R_F0 * math.sin(phi), R_F0 * math.cos(phi)), (R_F1 * math.sin(phi), R_F1 * math.cos(phi)), (P["head_t"], ZH1)]
    bw = Wire.make_polygon([jp(t, z) + Vector(tx - tw_ / 2, 0, 0) for t, z in bpts], close=True)
    bend = Solid.extrude(Face(bw), Vector(tw_, 0, 0))
    ctx["stiffener_t"] = round(stf_t, 4)
    ctx["head_z"] = (round(ZH0, 4), round(ZH1, 4))
    tr_a = ja + math.degrees(phi)
    ribbon["thumb"].append((R_F0, R_F1, tr_a, -a_in, tx - tw_ / 2, tx + tw_ / 2))      # trunk from the bend to the slot angle
    pad_row = [(-1.5 + k) * P["pad_pitch"] for k in range(4)]                                   # arc offsets on the inside face (mm)
    pad_ang = [P["pad_deg"] + math.degrees(o / R_IN) for o in pad_row]
    pa_lo, pa_hi = pad_ang[0] - math.degrees((P["pad_d"] / 2 + P["pad_margin"]) / R_IN), pad_ang[-1] + math.degrees((P["pad_d"] / 2 + P["pad_margin"]) / R_IN)   # v6.3: margin in mm (was 0.5 deg)
    px0, px1 = P["pad_x"] - P["pad_d"] / 2 - P["pad_margin"], P["pad_x"] + P["pad_d"] / 2 + P["pad_margin"]               # v6.3: strip X follows the pad row
    ribbon["away"].append((R_F0, R_F1, a_in, pa_lo + 4.0, tx - tw_ / 2, tx + tw_ / 2))           # trunk from the slot to the pads
    ribbon["away"].append((R_F0, R_F1, pa_lo, pa_lo + 5.0, tx - tw_ / 2, px1))                   # jog to the pad strip
    ribbon["away"].append((R_F0, R_F1, pa_lo, pa_hi, px0, px1))                                  # pad strip
    pad_solids = []
    for k, (nm, px) in enumerate(zip(("VBUS", "D-", "D+", "GND"), pad_ang)):
        pd = lplace(px, Cylinder(P["pad_d"] / 2, 1.0), x=P["pad_x"], r=R_IN) & (cyl_x(R_IN + P["cpad_t"], -5, 5) - cyl_x(R_IN, -5, 5))
        pad_solids.append(pd)

    # liner: true curved skin, with the ribbons and the pads cut out of it (they fill the voids)
    liner = sector_through(R_IN, R_LINER, CHAN_END, -CHAN_END, -cw_l, cw_l) + liner_fill
    voids = [head_flat, stiffener, bend]
    for key, pcs in ribbon.items():
        sg = sgn_y[key]
        for (r0, r1, a0, a1, x0, x1) in pcs:
            voids.append(sector_through(r0, r1, a0, a1, x0, x1))
        voids.append(box(tw_, 0.15, z_top - z_in, tx, sg * P["tail_y"], (z_in + z_top) / 2))
    for v in voids:
        liner = liner - v
    for pd in pad_solids:
        liner = liner - pd
    pl = newp("band_liner", "", "band", (0.0, 0.0, ZC - R_IN - P["liner_t"] / 2),
              (2 * cw_l, 2 * math.pi * (R_IN + 0.15) * (360 - 2 * CHAN_END) / 360, P["liner_t"]), 180.0, False,
              "0.3 mm resin skin, a true curved shell from +30 round the bottom to -30 degrees; size_y = arc length at its mid radius; "
              "the two embedded ribbons (0.075 resin under, 0.075 over) and the four pads are cut out of it")
    pl.add("resin", liner)

    def bandpart(name, ref, a, t, r0, r1, x, size, metal, note):
        c = gpos(a, t, (r0 + r1) / 2, x)
        return newp(name, ref, "band", c, size, a, metal, note)

    # v7 (architecture 17.29; exterior merged32h): round frame FRM1, a separate ring bonded in the round opening, and the round
    # textured cap CAP1 (one moulded part with its flange). Built in the joystick's local frame (z radial, at the joystick angle),
    # as the exterior builds them: frame from frame_below under the body surface (r_joy) to frame_proud above it; cap rim (the
    # plane where the dish and the rounded edge meet) cap_rim above the frame top; dish spherical, its rim where the edge round
    # starts (radius cap_d/2 - cap_edge); each ridge is the cap's own top surface raised ridge_h inside a ring ridge_w wide.
    clipcyl = lambda r: cyl_x(r, -10, 10)
    def top_r(sol, default):
        if sol is None:
            return default
        return max(math.hypot(v.Y, v.Z - ZC) for v in sol.vertices())
    rtop_joy = top_r(joy_ext, r_joy + 1.98)
    ctx["rtop_joy_exterior"] = round(rtop_joy, 3)
    r_ft = r_joy + P["frame_proud"]                      # frame top (local z)
    r_f0 = r_joy - P["frame_below"]                      # frame bottom
    z_rim = r_ft + P["cap_rim"]                          # cap rim plane
    ctx["joy_frame_top"], ctx["joy_frame_bottom"], ctx["joy_cap_rim"] = round(r_ft, 4), round(r_f0, 4), round(z_rim, 4)
    frame_l = Pos(0, 0, (r_f0 + r_ft) / 2) * (Cylinder(P["frame_od"] / 2, r_ft - r_f0) - Cylinder(P["frame_id"] / 2, r_ft - r_f0 + 1.0))
    frame = rloc(ja) * frame_l
    cap0 = R_PL1                                         # the shank starts on the flange top
    cap_l = Pos(0, 0, (cap0 + z_rim) / 2) * Cylinder(P["cap_d"] / 2, z_rim - cap0)
    cap_l = fillet(cap_l.edges().group_by(Axis.Z)[-1], P["cap_edge"])
    a_d = P["cap_d"] / 2 - P["cap_edge"]
    R_d = (a_d ** 2 + P["cap_dish"] ** 2) / (2 * P["cap_dish"])
    cap_l = cap_l - Pos(0, 0, z_rim - P["cap_dish"] + R_d) * Sphere(R_d)
    lifted = Pos(0, 0, P["ridge_h"]) * cap_l
    ridges = None
    for rr_ in P["ridge_rs"]:
        ring_ = Pos(0, 0, z_rim) * (Cylinder(rr_ + P["ridge_w"] / 2, 4.0) - Cylinder(rr_ - P["ridge_w"] / 2, 4.2))
        rg = (lifted & ring_) - cap_l
        ridges = rg if ridges is None else ridges + rg
    cap_l = cap_l + ridges
    ctx["cap_dish_sphere_r"] = round(R_d, 4)
    nub = rloc(ja) * cap_l
    fl_x, fl_t = P["flange"][0], P["flange"][1]
    zr = lambda sx, sy, sz, rr: fillet(Box(sx, sy, sz).edges().filter_by(Axis.Z), rr)
    flange = lplace(ja, zr(fl_x, fl_t, P["plate_t"], 1.0), r=R_PL1 - P["plate_t"] / 2)
    pj = bandpart("joystick_cap", "CAP1", ja, 0.0, R_SW1 + P["travel"], z_rim + P["ridge_h"], 0.0, (fl_x, fl_t, z_rim + P["ridge_h"] - R_PL1 + P["plate_t"]), False,
                  f"round cap {P['cap_d']:.2f} (one moulded part with its flange, Makrolon 2407 901510 black PC), at {ja:.1f} deg on the -Y side: shank from the flange top "
                  f"(r {R_PL1:.3f}) to the rim plane r {z_rim:.3f} = {P['cap_rim']:.3f} above the frame top, top edge rounded {P['cap_edge']}, spherical dish {P['cap_dish']} deep "
                  f"(sphere r {R_d:.3f}), ridges at {', '.join(f'{x:.2f}' for x in P['ridge_rs'])} ({P['ridge_w']} wide, {P['ridge_h']} high); flange {fl_x} x {fl_t} x {P['plate_t']} "
                  f"0.15 above the switch tops; body surface r {r_joy}, exterior cap top r {rtop_joy:.3f}")
    pj.add("polymer", nub)
    pj.add("polymer", flange)
    pfr = bandpart("joystick_frame", "FRM1", ja, 0.0, r_f0, r_ft, 0.0, (P["frame_od"], P["frame_od"], r_ft - r_f0), True,
                   f"round frame ring OD {P['frame_od']:.2f}, bore {P['frame_id']:.2f}, from r {r_f0:.3f} ({P['frame_below']} under the surface) to r {r_ft:.3f} "
                   f"({P['frame_proud']} above), titanium grade 5, bonded in the exterior's round opening dia {P['opening'][0]} (0.10 radial gap); "
                   f"cap to bore {(P['frame_id'] - P['cap_d']) / 2:.2f} radial")
    pfr.add("metal", frame)
    jo = P["joy_sw_off"]
    names = {"joy_sw_fingertip": ("SW5", jo, 0.0, SW[1], SW[0]), "joy_sw_hand": ("SW4", -jo, 0.0, SW[1], SW[0]),
             "joy_sw_up": ("SW1", 0.0, jo, SW[0], SW[1]), "joy_sw_down": ("SW3", 0.0, -jo, SW[0], SW[1]),
             "joy_sw_centre": ("SW2", 0.0, 0.0, SW[0], SW[1])}
    for nm, (ref, x, t, sx, st) in names.items():
        ps = bandpart(nm, ref, ja, t, R_SW0, R_SW1, x, (sx, st, SW[2]), True,
                      "SKTAAAE010 2.6 x 1.6 x 0.53: base plus actuator dome (dome 0.18 high, base 0.35); cross at %.1f from the centre%s; stands on the liner (ribbon embedded under it)"
                      % (jo, "; SW2 = the centre press (17.11)" if nm == "joy_sw_centre" else ""))
        ps.add("polymer", lplace(ja, Box(sx, st, 0.35), x=x, t=t, r=R_SW0 + 0.175))
        ps.add("metal", lplace(ja, dome(0.5, 0.18), x=x, t=t, r=R_SW0 + 0.35))
    # dam round the switch head (K-A3): a frame on the liner, 0.05 off the switch bases, up to the switch base tops, filling to the
    # pocket and channel walls so the cast resin cannot run between the switches and the flange
    pkx, pkt = P["pocket"]
    ix, it_ = 2 * (P["head_x"] + P["dam_gap"]), 2 * (P["head_t"] + P["dam_gap"])
    dam_top = R_SW0 + 0.35
    ring = lplace(ja, Box(pkx, 2 * dam_out_t, dam_top - (R_IN - 0.3)), r=(dam_top + R_IN - 0.3) / 2) - lplace(ja, Box(ix, it_, 4.0), r=dam_top)
    dam = (ring - cyl_x(R_LINER, -10, 10)) - bend - liner_fill      # v6: the ring lies wholly in the pocket (7.0 x 6.8 from the bore up)
    pdm = bandpart("joystick_dam", "DAM1", ja, 0.0, R_LINER, dam_top, 0.0, (pkx, 2 * dam_out_t, dam_top - R_LINER), False,
                   f"dam round the joystick's switch head (assembly.md K-A3, step 20): frame on the liner, inside {ix:.2f} (X) x {it_:.2f} (band), outside {pkx} x {2 * dam_out_t:.2f}, "
                   f"up to the switch base tops (r {dam_top:.3f}); UV-curing dam material PROPOSED in assembly.md step 20")
    pdm.add("polymer", dam)
    # motor: Jinlong W0525AB001D 5.0 x 2.5, beside the ribbon, with a pigtail that lands on the ribbon
    pm = bandpart("vibration_motor", "M1", mA, 0.0, R_LINER, R_LINER + P["motor_t"], mX,
                  (P["motor_d"], P["motor_d"], P["motor_t"]), True,
                  "Jinlong W0525AB001D coin 5.0 x 2.5 (design/parts/slim-2.md 1.4; lead wires, generic shape) at %.1f deg on the joystick side, %.1f off the band centre so the 1.4 wide ribbon passes beside it; pigtail lands on the ribbon" % (mA, mX))
    coin = fillet(Cylinder(P["motor_d"] / 2, P["motor_t"]).edges(), 0.2)
    pm.add("metal", lplace(mA, coin, x=mX, r=R_LINER + P["motor_t"] / 2))
    pm.add("mark", lplace(mA, Cylinder(min(2.0, P["motor_d"] / 3), 0.012), x=mX, r=R_LINER + P["motor_t"]))
    px_ = mX - P["motor_d"] / 2 - 0.45                                  # pigtail beside the rim, over the ribbon's width
    pm.add("flex", lplace(mA, Box(0.5, 1.0, 0.1), x=px_ + 0.15, t=-1.2, r=R_LINER + P["motor_t"] / 2))
    pm.add("flex", lplace(mA, Box(0.1, 1.0, P["motor_t"] / 2), x=px_ - 0.1, t=-1.2, r=R_LINER + P["motor_t"] / 4))
    # cell
    s, sw_ = cell_s, sw
    seal_deg = math.degrees(2.0 / R_CELL_C)
    cell_body = sector(R_LINER, R_LINER + P["cell_t"], s + seal_deg, s + sw_, -P["cell_w"] / 2, P["cell_w"] / 2)
    try:
        cell_body = fillet(cell_body.edges(), 0.3)
    except Exception as e:
        ctx["cell_fillet_error"] = str(e)
    seal = sector(R_LINER + 0.55, R_LINER + 1.05, s, s + seal_deg, -P["cell_w"] / 2, P["cell_w"] / 2)
    ln = 2 * math.pi * R_CELL_C * sw_ / 360
    ctx["cell_len_mm"] = round(ln, 3)
    ctx["cell_mah_lo_hi"] = (round(P["cell_t"] * P["cell_w"] * ln * 0.054, 1), round(P["cell_t"] * P["cell_w"] * ln * 0.072, 1))
    pc = newp("cell", "BT1", "band", (0.0, 0.0, ZC - R_CELL_C), (P["cell_w"], ln, P["cell_t"]), 180.0, True,
              f"curved pouch cell 1.6 x 6.0 on its centre line (radius {R_CELL_C:.3f}), from +{s:.1f} through the bottom to {cell_e - 360:.1f} deg "
              f"({sw_:.1f} deg, {ln:.2f} mm); rounded pouch, 2.0 mm sealed edge and two tabs at the +Y end next to the protection circuit; ends 0.15 mm short of the joystick switch footprint")
    pc.add("cell", cell_body)
    pc.add("polymer", seal)
    pm_end = pa0 + pang
    for tx_ in (-1.6, 1.6):
        pc.add("metal", sector(R_LINER + 0.75, R_LINER + 0.85, pm_end, s + seal_deg * 0.5, tx_ - 0.5, tx_ + 0.5))
    # protection circuit with the temperature sensor, at the +Y end, between the slot and the cell
    pp = bandpart("cell_protection", "", pa0 + pang / 2, 0.0, R_LINER, R_LINER + P["cell_t"], 0.0,
                  (P["prot"][1], P["prot"][0], P["cell_t"]), True,
                  f"2 x 5 mm (1.5 along the band) protection circuit with the cell's temperature sensor, from {pa0:.1f} to {pa0 + pang:.1f} deg (generic: small pcb with a chip)")
    pp.add("pcb", sector(R_LINER, R_LINER + 0.5, pa0, pa0 + pang, -2.5, 2.5))
    pp.add("chip", sector(R_LINER + 0.5, R_LINER + 1.2, pa0 + pang * 0.2, pa0 + pang * 0.8, -1.5, 1.5))
    # pads: gold, inside face of the band, in the liner, flush with its inner face
    for (nm, ref), pd, pa in zip((("VBUS", "CP1"), ("D-", "CP2"), ("D+", "CP3"), ("GND", "CP4")), pad_solids, pad_ang):
        pdp = bandpart(f"pad_{nm}", ref, pa, 0.0, R_IN, R_IN + P["cpad_t"], P["pad_x"], (P["pad_d"], P["pad_d"], P["cpad_t"]), True,
                       f"charging pad {nm}, gold disc {P['pad_d']} dia, {P['cpad_t']} thick, on the INSIDE face of the band at {pa:.2f} deg and X {P['pad_x']:.1f} ({P['pad_pitch']} mm pitch along the arc), "
                       f"in the resin liner, flush with its inner face, on the ribbon's land; the metal body has no hole")
        pdp.add("gold", pd)
    # ribbons
    for nm, ref, key, note in (
            ("band_flex_thumb", "J_BAND_A", "thumb", "joystick side (-Y): 5 switch lines and ground, motor 2; slot at Y -5.9; embedded in the liner to the head under the switches"),
            ("band_flex_away", "J_BAND_B", "away", "other side (+Y): cell 2, temperature sensor 1, pads 4; slot at Y +5.9; embedded in the liner under the cell to the pads at 180 deg")):
        sg = sgn_y[key]
        pf = newp(nm, ref, "band", (tx, sg * P["tail_y"], (z_in + z_top) / 2), (tw_, 0.15, z_top - z_in), None, False,
                  note + "; leaves the board underside through the floor slot")
        pf.add("flex", box(tw_, 0.15, z_top - z_in, tx, sg * P["tail_y"], (z_in + z_top) / 2))
        for (r0, r1, a0, a1, x0, x1) in ribbon[key]:
            pf.add("flex", sector_through(r0, r1, a0, a1, x0, x1))
        if key == "thumb":                       # v6: flat head, bend and stiffener (K13)
            pf.add("flex", head_flat)
            pf.add("flex", bend)
            pf.add("metal", stiffener)
            pf.note += (f"; v6: flat head 6.4 x 6.4 x 0.15 under the five switches on a flat stiffener 6.4 x 6.4 x {stf_t:.3f} "
                        f"(stainless or polyimide, drawn as metal), the liner fills under it; a bend joins the head's edge to the embedded trunk")
    return dict(parts=parts, ctx=ctx, body0=body0, envelope=envelope)


def motor_rim_min_wall(body, angle=None, n=24, step=0.025, reach=4.2):
    """Least metal (body solid) along the outward radial ray from n points on each rim circle of the motor."""
    a = P["motor_angle"] if angle is None else angle
    worst = (9e9, None)
    for face, r in (("back", R_LINER), ("front", R_LINER + P["motor_t"])):
        for k in range(n):
            ph = 2 * math.pi * k / n
            x, t = P["motor_d"] / 2 * math.cos(ph), P["motor_d"] / 2 * math.sin(ph)
            px, py, pz = gpos(a, t, r, x + P["motor_x"])
            d = Vector(0, py, pz - ZC)
            d = d * (1 / d.length)
            metal = 0.0
            for i in range(int(reach / step)):
                if body.is_inside(Vector(px, py, pz) + d * (i * step)):
                    metal += step
            if metal < worst[0]:
                worst = (metal, (face, round(math.degrees(ph)), round(px, 2), round(py, 2), round(pz, 2)))
    return worst


LAYER_ORDER = ["glass", "screen", "board", "band", "body"]


def layers_json(parts):
    out = {"units": "mm", "up": "+Z", "axes": "X along the finger (+X fingertip), Y across (+Y thumb), Z up",
           "band_axis": {"y": 0.0, "z": ZC, "direction": "X"}, "layers": []}
    ex = {"glass": ([0, 0, 1], 14.0), "screen": ([0, 0, 1], 9.0), "board": ([0, 0, 1], 4.0), "body": ([0, 0, -1], 6.0)}
    for L in LAYER_ORDER:
        e = {"name": L, "parts": [p.name for p in parts if p.layer == L]}
        if L == "band":
            dirs = {}
            for p in parts:
                if p.layer == "band":
                    a = p.angle if p.angle is not None else 180.0
                    if p.name.startswith("band_flex"):
                        a = -38.0 if p.name.endswith("thumb") else 38.0
                    ar = math.radians(a)
                    dirs[p.name] = [0.0, round(math.sin(ar), 5), round(math.cos(ar), 5)]
            e["explode"] = {"mode": "radial", "distance": 9.0, "note": "each part moves outward along its radius from the band axis", "part_dirs": dirs}
        else:
            d, dist = ex[L]
            e["explode"] = {"mode": "axis", "dir": d, "distance": dist}
        out["layers"].append(e)
    return out


def write_csv(parts):
    cols = ["part", "reference", "layer", "x", "y", "z", "size_x", "size_y", "size_z", "angle_deg", "metal", "note"]
    with open(HERE / "placement.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for p in parts:
            x, y, z = p.centre
            w.writerow([p.name, p.ref, p.layer, f"{x:.3f}", f"{y:.3f}", f"{z:.3f}", f"{p.size[0]:.3f}", f"{p.size[1]:.3f}",
                        f"{p.size[2]:.3f}", "" if p.angle is None else f"{p.angle:.2f}", str(bool(p.metal)), p.note])


# ------------------------------------------------------------------ export
LIN_DEFL, ANG_DEFL = 0.005, 0.1
BALL_PARTS = ("main_chip", "power_chip", "screen_supply_chip")   # solder balls 0.2 to 0.25 dia: 0.45 rad is round at any zoom          # linear deflection 0.005 mm, angular 0.1 rad


def mesh_smooth(shape, lin=LIN_DEFL, ang=ANG_DEFL):
    """Per B-rep face: indexed vertices, smooth normals inside a face, hard edges between faces."""
    import numpy as np
    P_, N_, I_ = [], [], []
    off = 0
    for f in shape.faces():
        v, t = f.tessellate(lin, ang)
        if not t:
            continue
        V = np.array([(p.X, p.Y, p.Z) for p in v], dtype=np.float64)
        T = np.array(t, dtype=np.int64)
        fn = np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]])
        N = np.zeros_like(V)
        for k in range(3):
            np.add.at(N, T[:, k], fn)
        ln = np.linalg.norm(N, axis=1, keepdims=True)
        ln[ln == 0] = 1
        N /= ln
        P_.append(V)
        N_.append(N)
        I_.append(T + off)
        off += len(V)
    if not P_:
        return None
    return np.vstack(P_).astype(np.float32), np.vstack(N_).astype(np.float32), np.vstack(I_).astype(np.uint32)


MAT = {"metal": ([0.72, 0.73, 0.76, 1], 0.95, 0.35), "gold": ([0.85, 0.65, 0.2, 1], 1.0, 0.3), "pcb": ([0.08, 0.35, 0.2, 1], 0.0, 0.6),
       "chip": ([0.05, 0.05, 0.06, 1], 0.1, 0.5), "ceramic": ([0.8, 0.75, 0.62, 1], 0.0, 0.7), "polymer": ([0.12, 0.12, 0.14, 1], 0.0, 0.5),
       "glass": ([0.6, 0.8, 0.95, 0.35], 0.0, 0.05), "screen": ([0.03, 0.03, 0.06, 1], 0.2, 0.2), "foam": ([0.25, 0.25, 0.27, 1], 0.0, 0.9),
       "flex": ([0.9, 0.6, 0.1, 1], 0.0, 0.5), "cell": ([0.75, 0.78, 0.8, 1], 0.6, 0.4), "resin": ([0.9, 0.85, 0.7, 0.55], 0.0, 0.3),
       "mark": ([0.9, 0.9, 0.9, 1], 0.0, 0.6)}


def write_glb(parts, layers, path):
    import numpy as np
    buf = bytearray()
    views, accs, meshes, nodes, mats = [], [], [], [], []
    cls_mat = {}
    for c in CLASSES:
        col, met, rough = MAT[c]
        cls_mat[c] = len(mats)
        m = {"name": f"mat_{c}", "pbrMetallicRoughness": {"baseColorFactor": col, "metallicFactor": met, "roughnessFactor": rough}}
        if col[3] < 1.0:
            m["alphaMode"] = "BLEND"
        mats.append(m)
    pdirs = layers["layers"][3]["explode"]["part_dirs"]
    tris_total = 0
    top = []
    for p in parts:
        kids = []
        for cls, solid in p.solids().items():
            mm = mesh_smooth(solid, ang=0.45 if (cls == 'metal' and p.name in BALL_PARTS) else ANG_DEFL)
            if mm is None:
                continue
            pos, nor, idx = mm
            tris_total += len(idx)
            ids = []
            for arr, comp, typ, tgt in ((pos, 5126, "VEC3", 34962), (nor, 5126, "VEC3", 34962), (idx.reshape(-1), 5125, "SCALAR", 34963)):
                while len(buf) % 4:
                    buf.append(0)
                off = len(buf)
                buf += arr.tobytes()
                views.append({"buffer": 0, "byteOffset": off, "byteLength": arr.nbytes, "target": tgt})
                a = {"bufferView": len(views) - 1, "componentType": comp, "count": int(arr.shape[0]), "type": typ}
                if arr is pos:
                    a["min"], a["max"] = pos.min(0).tolist(), pos.max(0).tolist()
                accs.append(a)
                ids.append(len(accs) - 1)
            meshes.append({"name": f"{p.name}__{cls}", "primitives": [{"attributes": {"POSITION": ids[0], "NORMAL": ids[1]},
                                                                      "indices": ids[2], "material": cls_mat[cls], "mode": 4}]})
            nodes.append({"name": f"{p.name}__{cls}", "mesh": len(meshes) - 1, "extras": {"class": cls}})
            kids.append(len(nodes) - 1)
        extras = {"reference": p.ref, "layer": p.layer, "metal": bool(p.metal), "angle_deg": p.angle,
                  "centre": [round(c, 4) for c in p.centre]}
        extras["explode_dir"] = pdirs[p.name] if p.layer == "band" else next(l for l in layers["layers"] if l["name"] == p.layer)["explode"]["dir"]
        nodes.append({"name": p.name, "children": kids, "extras": extras})
        top.append(len(nodes) - 1)
    while len(buf) % 4:
        buf.append(0)
    gltf = {"asset": {"version": "2.0", "generator": "thin.py v7", "extras": {"units": "mm", "up": "+Z (CAD axes, not glTF Y-up)"}},
            "scene": 0, "scenes": [{"name": "thin_ring_inside", "nodes": top, "extras": {"units": "mm", "up": "+Z", "layers": layers["layers"], "classes": CLASSES}}],
            "nodes": nodes, "meshes": meshes, "materials": mats, "accessors": accs, "bufferViews": views, "buffers": [{"byteLength": len(buf)}]}
    js = json.dumps(gltf, separators=(",", ":")).encode()
    while len(js) % 4:
        js += b" "
    total = 12 + 8 + len(js) + 8 + len(buf)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(js), 0x4E4F534A) + js)
        f.write(struct.pack("<II", len(buf), 0x004E4942) + bytes(buf))
    return tris_total


def main():
    OUT.mkdir(exist_ok=True)
    m = build()
    parts = m["parts"]
    write_csv(parts)
    layers = layers_json(parts)
    with open(HERE / "layers.json", "w") as f:
        json.dump(layers, f, indent=1)
    tris = write_glb(parts, layers, OUT / "thin-inside.glb")
    kids = []
    for p in parts:
        for cls, s in p.solids().items():
            s.label = f"{p.name}__{cls}"
            kids.append(s)
    export_step(Compound(children=kids, label="thin_ring_inside"), str(OUT / "thin-inside.step"))
    with open(OUT / "triangles.txt", "w") as f:
        f.write(f"{tris}\n")
    print(f"thin.py v7: {len(parts)} parts, exterior {os.path.basename(EXT_FILE)}, {tris} triangles, ZC={ZC:.3f}; wrote placement.csv, layers.json, "
          f"out/thin-inside.glb, out/thin-inside.step")
    print("ctx:", {k: v for k, v in m["ctx"].items() if isinstance(v, (int, float, str, tuple, list, type(None)))})
    return 0


if __name__ == "__main__":
    sys.exit(main())
