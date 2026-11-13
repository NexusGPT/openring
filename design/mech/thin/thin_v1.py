#!/usr/bin/env python3
"""3D inside model of the thin AI recorder ring (architecture.md section 17, A5-draft).

Axes: X along the finger (+X fingertip), Y across (+Y thumb side), Z up.
Origin: centre of the block's underside. Band axis along X at (Y 0, Z ZC).
Angles are measured around the finger from the top, plus toward +Y.
Running this file writes placement.csv, layers.json, out/thin-inside.glb, out/thin-inside.step.
Test override (no file edit): THIN_OVERRIDE="motor_angle=-53.9" python thin.py
"""
import os
import sys
import csv
import json
import copy
import math
import struct
from pathlib import Path

from build123d import (Box, Cylinder, Pos, Rot, Solid, Wire, Face, Vector, Axis,
                       Compound, fillet, export_step)

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"

# ------------------------------------------------------------------ numbers
S17 = "architecture.md s17"
P = dict(
    # outside (17.1)
    block_x=29.3, block_y=14.75, block_z=3.2, plan_r=2.5,
    band_w=8.0, band_t=2.6, shoulder_t=3.6, shoulder_w=13.0, shoulder_deg=38.0,
    bore_d=18.95, bore_gap=0.4,             # bore top 0.4 mm under the block underside
    # block stack (17.2), Z from the underside
    floor=0.40, gap=0.05, under=1.00, board_t=0.30, foam_t=0.10, screen_t=0.80,
    adh_t=0.10, glass_t=0.40,
    # screen and board
    scr_x=27.35, scr_y=12.8, board_x=27.2, board_y=12.6,
    lit_x=21.6, lit_y=10.8,
    # band stack (17.3)
    liner_t=0.30, flex_t=0.15, sw_t=0.53, plate_t=0.40, shell_t=0.50, shell_edge=0.60,
    joy_deg=38.0, rec_deg=62.0, motor_angle=-49.0, motor_pocket_angle=-49.0, taper_start_deg=61.0, cell_deg_end=77.0,
    joy_cap_d=4.6, joy_open_d=5.0, joy_sw_off=1.9, rec_cap=(5.0, 3.0),
    motor_d=7.0, motor_t=2.1, motor_gap=0.2,
    cell_t=1.6, cell_w=6.0, cell_len=38.0, cell_gap=0.2,
    prot=(1.5, 5.0),   # arc length 2.0 in the architecture; 1.5 so it clears the motor rim (C8)
    pad_d=1.0, pad_x=(-2.4, -0.8, 0.8, 2.4),
)
# a switch's own outline, 16.4: 2.6 x 1.6 x 0.53
SW = (2.6, 1.6, 0.53)
# ---- values the builder chose (listed in thin-notes.md, "Chosen by the builder")
CH = dict(
    clear=0.05,           # pocket clearance per side around the panel
    glass_rim=0.50,       # metal rim around the glass
    joy_sw_off=2.1,       # architecture says 1.9; 1.9 makes two switches overlap (conflict C1)
    tail_pocket_x=-14.05,
    mic_slot=(1.2, 0.3),
    slot_w=2.6, slot_y=0.6, tail_w=2.2, tail_x=-4.7, tail_y=5.9, tail_zlo=-0.9,
    shoulder_cav_deg=(30.0, 54.0),   # wide (11.8 mm) cavity at each shoulder
    channel_end_deg=30.0,            # channel runs from +30 round the bottom to -30
    notch_antenna=True, notch_motor=False, notch_joy=True,
    bump_deg=(19.0, 57.0), taper_end_deg=85.0,   # thick shoulder 19 to 57, easing to the band thickness by 85 (lead ruling)
)
if os.environ.get("THIN_OVERRIDE"):
    for kv in os.environ["THIN_OVERRIDE"].split(","):
        k, v = kv.split("=")
        P[k] = float(v)

R_IN = P["bore_d"] / 2                      # 9.475
ZC = -P["bore_gap"] - R_IN                  # band axis height: -9.875
R_LINER = R_IN + P["liner_t"]               # 9.775
R_OUT = R_IN + P["band_t"]                  # 12.075
R_OUT_SH = R_IN + P["shoulder_t"]           # 12.575
R_CELL_C = R_LINER + P["cell_t"] / 2        # 10.575 centre line of the cell
R_SW0 = R_LINER + P["flex_t"]               # switch bottom 9.925
R_SW1 = R_SW0 + P["sw_t"]                   # switch top 10.455
MOTOR_ROOF = 0.1                            # pocket roof above the motor's front face
R_PL1 = R_SW1 + P["plate_t"]                # plate top 10.855

Z_FLOOR = P["floor"]
Z_UB0 = Z_FLOOR + P["gap"]                  # 0.45 underside of the lowest part
Z_BD0 = Z_UB0 + P["under"]                  # 1.45 board underside
Z_BD1 = Z_BD0 + P["board_t"]                # 1.75
Z_FO1 = Z_BD1 + P["foam_t"]                 # 1.85
Z_SC1 = Z_FO1 + P["screen_t"]               # 2.65
Z_AD1 = Z_SC1 + P["adh_t"]                  # 2.75
Z_GL1 = Z_AD1 + P["glass_t"]                # 3.15


# ------------------------------------------------------------------ helpers
def box(sx, sy, sz, cx, cy, cz):
    return Pos(cx, cy, cz) * Box(sx, sy, sz)


def gpos(a, t, r, x=0.0):
    """Global (x, y, z) of local point (tangent t, radial r) at angle a (deg)."""
    ar = math.radians(a)
    return (x, r * math.sin(ar) + t * math.cos(ar), ZC + r * math.cos(ar) - t * math.sin(ar))


def rloc(a):
    return Pos(0, 0, ZC) * Rot(-a, 0, 0)


def lbox(a, sx, st, sr, x, t, r0):
    """Box in the band frame: X size sx, tangent size st, radial from r0 to r0+sr."""
    return rloc(a) * (Pos(x, t, r0 + sr / 2) * Box(sx, st, sr))


def lcyl(a, d, r0, r1, x=0.0, t=0.0):
    return rloc(a) * (Pos(x, t, (r0 + r1) / 2) * Cylinder(d / 2, r1 - r0))


def cyl_x(r, x0, x1):
    return Pos((x0 + x1) / 2, 0, ZC) * Cylinder(r, x1 - x0, rotation=(0, 90, 0))


def sector(r0, r1, a0, a1, x0, x1):
    """Annular sector about the band axis, angles a0 to a1 (deg from the top, + toward +Y)."""
    def pt(x, r):
        ar = math.radians(a0)
        return Vector(x, r * math.sin(ar), ZC + r * math.cos(ar))
    w = Wire.make_polygon([pt(x0, r0), pt(x1, r0), pt(x1, r1), pt(x0, r1)], close=True)
    return Solid.revolve(Face(w), a1 - a0, Axis((0, 0, ZC), (-1, 0, 0)))


def r_outer(a):
    """Outer radius of the band at |angle| a (deg) on the shoulder: flat to bump end, then easing."""
    a = abs(a)
    b1, e = P["taper_start_deg"], CH["taper_end_deg"]
    if a <= b1:
        return R_OUT_SH
    if a >= e:
        return R_OUT
    return R_OUT_SH - (R_OUT_SH - R_OUT) * (a - b1) / (e - b1)


def taper(sgn, a0, a1):
    pts = []
    n = int(round(a1 - a0))
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        pts.append((a, r_outer(a)))
    poly = [(R_IN, a0)] + [(r, a) for a, r in pts] + [(R_IN, a1)]
    hw = P["band_w"] / 2
    vs = [Vector(-hw, sgn * r * math.sin(math.radians(a)), ZC + r * math.cos(math.radians(a))) for r, a in poly]
    return Solid.extrude(Face(Wire.make_polygon(vs, close=True)), Vector(2 * hw, 0, 0))


def fuse_all(shapes):
    s = shapes[0]
    for o in shapes[1:]:
        s = s + o
    return s


def rbox(sx, sy, sz, cx, cy, cz, r):
    b = Box(sx, sy, sz)
    b = fillet(b.edges().filter_by(Axis.Z), r)
    return Pos(cx, cy, cz) * b


# ------------------------------------------------------------------ model
def build():
    parts = []

    def add(name, ref, layer, solid, centre, size, angle=None, metal=False, note=""):
        parts.append(dict(name=name, ref=ref, layer=layer, solid=solid, centre=centre,
                          size=size, angle=angle, metal=metal, note=note))

    sh = P["shoulder_deg"]
    # ---- outer body envelope (before cavities)
    block = rbox(P["block_x"], P["block_y"], P["block_z"], 0, 0, P["block_z"] / 2, P["plan_r"])
    ring = cyl_x(R_OUT, -P["band_w"] / 2, P["band_w"] / 2) - cyl_x(R_IN, -10, 10)
    b0, b1 = CH["bump_deg"]
    hw = P["shoulder_w"] / 2
    bumps = [sector(R_IN, R_OUT_SH, b0, b1, -hw, hw), sector(R_IN, R_OUT_SH, 360 - b1, 360 - b0, -hw, hw)]
    for sgn in (1, -1):
        bumps.append(taper(sgn, b1 - 2.0, CH["taper_end_deg"]))   # starts 2 deg inside the wide sector so the fuse overlaps
    envelope = ((block + fuse_all(bumps)) + ring).clean()
    assert envelope.is_valid, "envelope fuse is invalid"

    # ---- cavities
    cav = []
    # block cavity: panel + 0.05 per side, from the floor top to the adhesive top
    sx, sy = P["scr_x"] + 2 * CH["clear"], P["scr_y"] + 2 * CH["clear"]
    cav.append(rbox(sx, sy, Z_AD1 - Z_FLOOR, 0, 0, (Z_AD1 + Z_FLOOR) / 2, 0.1))
    # glass recess (rim 0.5 mm all round, concentric with the 2.5 plan radius)
    gx, gy = P["block_x"] - 2 * CH["glass_rim"], P["block_y"] - 2 * CH["glass_rim"]
    cav.append(rbox(gx, gy, P["block_z"] - Z_AD1 + 0.5, 0, 0, Z_AD1 + (P["block_z"] - Z_AD1 + 0.5) / 2,
                    P["plan_r"] - CH["glass_rim"]))
    # pocket for the screen tail fold at the hand end
    cav.append(box(0.55, 5.4, 2.0, (CH["tail_pocket_x"] - 13.5) / 2, 0, 1.45))
    # microphone slots through the -Y wall
    for mx in (-11.0, 11.0):
        cav.append(box(CH["mic_slot"][0], 1.2, CH["mic_slot"][1], mx, -P["block_y"] / 2 + 0.6, Z_BD0 - 0.98 / 2))
    # floor slots for the two flex tails
    for sgn in (1, -1):
        cav.append(box(CH["slot_w"], CH["slot_y"], 1.0, CH["tail_x"], sgn * CH["tail_y"], 0.0))
    # band channel: 0.5 shell, 0.6 edges -> 6.8 wide, from liner outer to shell inner, angles 30 to 330
    ce = CH["channel_end_deg"]
    cw = (P["band_w"] - 2 * P["shell_edge"]) / 2        # 3.4
    cav.append(sector(R_IN, R_OUT - P["shell_t"], ce, 360 - ce, -cw, cw))
    # wide shoulder cavity (11.8 mm) at each shoulder
    s0, s1 = CH["shoulder_cav_deg"]
    sw_ = (P["shoulder_w"] - 2 * P["shell_edge"]) / 2   # 5.9
    cav.append(sector(R_IN, R_OUT - P["shell_t"], s0, s1, -sw_, sw_))
    cav.append(sector(R_IN, R_OUT - P["shell_t"], 360 - s1, 360 - s0, -sw_, sw_))
    # joystick pocket + 5.0 opening
    ja = P["joy_deg"]
    cav.append(lbox(ja, 7.0, 6.0, R_PL1 + 0.1 - R_LINER, 0, 0, R_LINER))
    cav.append(lcyl(ja, P["joy_open_d"], R_PL1 + 0.1, R_OUT_SH + 1.0))
    # record button opening (cap + 0.2 per side) through the shell
    ra = P["rec_deg"]
    cav.append(lbox(ra, P["rec_cap"][0] + 0.4, P["rec_cap"][1] + 0.4, R_OUT_SH + 1.0 - R_LINER, 0, 0, R_LINER))
    # motor pocket (designed position; the part itself uses motor_angle)
    ma_design = P["motor_pocket_angle"]
    cav.append(lcyl(ma_design, P["motor_d"] + 0.2, R_LINER, R_LINER + P["motor_t"] + MOTOR_ROOF))
    # charging pad holes at the bottom
    for px in P["pad_x"]:
        cav.append(lcyl(180.0, P["pad_d"], R_OUT - P["shell_t"] - 0.01, R_OUT + 0.5, x=px))
    body = copy.deepcopy(envelope)
    for c in cav:
        body = body - c
    add("outer_body", "", "body", body, (0.0, 0.0, P["block_z"] / 2),
        (P["block_x"], P["block_y"], P["block_z"]), None, True,
        "ONE metal shell: block 29.3 x 14.75 x 3.2 r2.5 plus band 8.0 x 2.6 (3.1 at the shoulders, 13 wide); "
        "cavities for every part; rolled edges not modelled")

    # ---- band liner
    liner = sector(R_IN, R_LINER, ce, 360 - ce, -cw, cw) + sector(R_IN, R_LINER, s0, s1, -sw_, sw_) \
        + sector(R_IN, R_LINER, 360 - s1, 360 - s0, -sw_, sw_)
    add("band_liner", "", "band", liner, (0.0, 0.0, ZC - R_IN - P["liner_t"] / 2),
        (2 * sw_, 2 * math.pi * R_LINER * (360 - 2 * ce) / 360, P["liner_t"]), 180.0, False,
        "0.3 mm resin liner closing the channel toward the finger; angles +30 round the bottom to -30; "
        "size_y = arc length at its mid radius")

    # ---- glass stack
    add("cover_glass", "GL1", "glass", rbox(gx, gy, P["glass_t"], 0, 0, Z_AD1 + P["glass_t"] / 2,
                                            P["plan_r"] - CH["glass_rim"]),
        (0.0, 0.0, Z_AD1 + P["glass_t"] / 2), (gx, gy, P["glass_t"]), None, False,
        "size assumed: block minus 0.5 mm rim; top 0.05 under the block top")
    add("clear_adhesive", "ADH1", "glass", box(P["scr_x"], P["scr_y"], P["adh_t"], 0, 0, Z_SC1 + P["adh_t"] / 2),
        (0.0, 0.0, Z_SC1 + P["adh_t"] / 2), (P["scr_x"], P["scr_y"], P["adh_t"]), None, False,
        "same outline as the panel")
    lit_cx = -P["block_x"] / 2 + 5.33 + P["lit_x"] / 2
    add("screen", "DISP1", "screen", box(P["scr_x"], P["scr_y"], P["screen_t"], 0, 0, Z_FO1 + P["screen_t"] / 2),
        (0.0, 0.0, Z_FO1 + P["screen_t"] / 2), (P["scr_x"], P["scr_y"], P["screen_t"]), None, True,
        f"lit area 21.6 (X) x 10.8 (Y) centred X {lit_cx:.3f} Y 0 (5.33 to the hand end, 2.38 to the fingertip end, "
        "1.98 each long side, from the block edge)")
    add("foam", "FOAM1", "screen", box(P["board_x"], P["board_y"], P["foam_t"], 0, 0, Z_BD1 + P["foam_t"] / 2),
        (0.0, 0.0, Z_BD1 + P["foam_t"] / 2), (P["board_x"], P["board_y"], P["foam_t"]), None, False,
        "solid pad at board size (a frame in the real part)")
    # screen tail fold at the hand end: vertical strip beside the panel, then under the board end
    tl = 0.2
    tv = box(tl, 5.0, 1.0, -13.675 - tl / 2, 0, 1.75)
    th = box(0.275, 5.0, tl, -13.6 - 0.275 / 2, 0, Z_BD0 - tl / 2)
    add("screen_tail", "DISP1", "screen", tv + th, (-13.775, 0.0, 1.75), (0.275 + tl, 5.0, 1.0), None, True,
        "folded tail 0.2 thick, 5.0 wide: down the hand end beside the panel (Z 2.25 to 1.25), then 0.275 mm "
        "under the board end into connector J1; tail insertion into J1 is shown as touching its face")

    # ---- main board with two notches
    notch_a = box(1.8, 3.6, 1.0, -13.6 + 0.9, 4.5, Z_BD0 + 0.15)
    notch_m = box(3.6, 2.0, 1.0, 0.0, -P["board_y"] / 2 + 1.0, Z_BD0 + 0.15)
    board = box(P["board_x"], P["board_y"], P["board_t"], 0, 0, Z_BD0 + P["board_t"] / 2)
    if CH["notch_antenna"]:
        board = board - notch_a
    if CH["notch_motor"]:
        board = board - notch_m
    if CH["notch_joy"]:
        board = board - box(2.8, 0.6, 1.0, 0.0, P["board_y"] / 2 - 0.3, Z_BD0 + 0.15)
    add("main_board", "PCB1", "board", board, (0.0, 0.0, Z_BD0 + P["board_t"] / 2),
        (P["board_x"], P["board_y"], P["board_t"]), None, False,
        "6 layers, one side populated (under side); notch 1.8 x 3.6 at the hand-end +Y corner for the antenna "
        "(1.2 tall > 1.0 under the board, conflict C2); notch 2.8 x 0.6 at the +Y edge for the joystick cap (thicker shoulder lifts its rim into the board layer, C9)")

    def under(name, ref, layer, sx, sy, h, cx, cy, note, metal=True):
        add(name, ref, layer, box(sx, sy, h, cx, cy, Z_BD0 - h / 2), (cx, cy, Z_BD0 - h / 2), (sx, sy, h),
            None, metal, note)

    under("main_chip", "U1", "board", 3.02, 2.43, 0.43, 4.0, 0.0, "nRF54LM20A WLCSP-61, hangs under the board")
    under("power_chip", "U2", "board", 3.1, 2.4, 0.5, 8.5, 0.0, "nPM1300 WLCSP; height 0.5 ASSUMED (not in the architecture)")
    under("screen_supply_chip", "U4", "board", 2.0, 2.0, 0.58, 4.0, -3.5, "SGM38046")
    under("screen_supply_coil", "L10", "board", 2.5, 2.0, 1.0, 6.5, -3.5, "1269AS-H-2R2M, next to U4")
    under("storage", "U3", "board", 8.0, 6.2, 0.75, -5.0, 0.0, "CSNP32GCR01-BOW, LGA-8")
    under("mic_1", "U5", "board", 3.5, 2.65, 0.98, -11.0, -P["block_y"] / 2 + 0.925 + 1.325,
          "IM68D128B against the -Y cavity wall; port sideways through the 1.2 x 0.3 slot at X -11")
    under("mic_2", "U6", "board", 3.5, 2.65, 0.98, 11.0, -P["block_y"] / 2 + 0.925 + 1.325,
          "IM68D128B against the -Y cavity wall; port sideways through the 1.2 x 0.3 slot at X +11")
    add("antenna", "ANT1", "board", box(1.6, 3.2, 1.2, -12.7, 4.4, Z_UB0 + 0.6), (-12.7, 4.4, Z_UB0 + 0.6),
        (1.6, 3.2, 1.2), None, False,
        "3.2 along Y; stands in the board notch (Z 0.45 to 1.65) under the unlit strip at the hand end")
    under("screen_connector", "J1", "board", 3.2, 5.2, 0.9, -12.0, 0.0,
          "15 positions 0.3 pitch, 5.2 across Y x 3.2 along X x 0.9; tail enters from the hand end")
    under("crystal_32M", "X1", "board", 2.0, 1.6, 0.5, 3.0, 3.0, "height 0.5 ASSUMED")
    under("crystal_32k", "X2", "board", 2.0, 1.2, 0.5, 5.5, 3.0, "height 0.5 ASSUMED")
    under("power_coil_1", "L71", "board", 2.0, 1.6, 1.0, 8.5, 3.2, "nPM1300 buck 1 inductor")
    under("power_coil_2", "L72", "board", 2.0, 1.6, 1.0, 11.0, 3.2, "nPM1300 buck 1 inductor")

    # ---- band parts
    def bandpart(name, ref, solid, a, t, r0, r1, x, size, metal, note):
        c = gpos(a, t, (r0 + r1) / 2, x)
        add(name, ref, "band", solid, c, size, a, metal, note)

    # flex tails
    tw, tx, ty = CH["tail_w"], CH["tail_x"], CH["tail_y"]
    for nm, sgn, note in (("band_flex_thumb", 1, "thumb side: 5 switch lines + ground, to the joystick and record switches"),
                          ("band_flex_away", -1, "other side: motor 2, cell 2 + temperature 1, pads 4 (two stacked layers)")):
        z0, z1 = CH["tail_zlo"], Z_BD0
        add(nm, "J_BAND_A" if sgn > 0 else "J_BAND_B", "band", box(tw, 0.15, z1 - z0, tx, sgn * ty, (z0 + z1) / 2), (tx, sgn * ty, (z0 + z1) / 2),
            (tw, 0.15, z1 - z0), None, False,
            note + "; leaves the board underside through the floor slot; run inside the band not drawn")
    # joystick
    ja = P["joy_deg"]
    cap = lcyl(ja, P["joy_cap_d"], R_PL1, R_OUT_SH + 0.5) & cyl_x(R_OUT_SH, -10, 10)
    bandpart("joystick_cap", "", cap, ja, 0.0, R_PL1, R_OUT_SH, 0.0, (4.6, 4.6, R_OUT_SH - R_PL1), False,
             "cap 4.6 dia from the plate top (r 10.855; the 0.4 plate is not a listed part, its zone is left empty) to the outer surface, clipped flush; "
             "5.0 mm sealed opening in the shell")
    jo = CH["joy_sw_off"]
    SWREF = {"joy_sw_fingertip": "SW5", "joy_sw_hand": "SW4", "joy_sw_up": "SW1", "joy_sw_down": "SW3"}
    for nm, (x, t, sx, st) in {"joy_sw_fingertip": (jo, 0.0, SW[1], SW[0]),
                               "joy_sw_hand": (-jo, 0.0, SW[1], SW[0]),
                               "joy_sw_up": (0.0, jo, SW[0], SW[1]),
                               "joy_sw_down": (0.0, -jo, SW[0], SW[1])}.items():
        bandpart(nm, SWREF[nm], lbox(ja, sx, st, SW[2], x, t, R_SW0), ja, t, R_SW0, R_SW1, x, (sx, st, SW[2]), True,
                 "SKTAAAE010 2.6 x 1.6 x 0.53 on the flex at r 9.925; cross at %.1f from the centre" % jo)
    # record button
    ra = P["rec_deg"]
    rc = lbox(ra, P["rec_cap"][0], P["rec_cap"][1], R_OUT_SH + 0.5 - R_PL1, 0, 0, R_PL1) & envelope
    bandpart("record_cap", "", rc, ra, 0.0, R_PL1, r_outer(ra), 0.0, (5.0, 3.0, r_outer(ra) - R_PL1), False,
             "cap 5.0 (X) x 3.0 (along the arc) from the plate top (r 10.855) to the outer surface, flush")
    bandpart("record_switch", "SW2", lbox(ra, SW[0], SW[1], SW[2], 0, 0, R_SW0), ra, 0.0, R_SW0, R_SW1, 0.0,
             (SW[0], SW[1], SW[2]), True, "SKTAAAE010 on the same flex, under its cap")
    # motor
    mA = P["motor_angle"]
    bandpart("vibration_motor", "M1", lcyl(mA, P["motor_d"], R_LINER, R_LINER + P["motor_t"]), mA, 0.0, R_LINER,
             R_LINER + P["motor_t"], 0.0, (P["motor_d"], P["motor_d"], P["motor_t"]), True,
             "VC0720B088L coin 7.0 dia x 2.1, flat disc: its front rim reaches polar radius 12.38; shoulder 3.6 thick (ruling on C3)")
    # cell: arc on its centre line
    ang = math.degrees(P["cell_len"] / R_CELL_C)
    a0 = 180 - ang / 2
    cell = sector(R_LINER, R_LINER + P["cell_t"], a0, a0 + ang, -P["cell_w"] / 2, P["cell_w"] / 2)
    add("cell", "BT1", "band", cell, (0.0, 0.0, ZC - R_CELL_C), (P["cell_w"], P["cell_len"], P["cell_t"]), 180.0, True,
        f"curved cell 1.6 x 6.0 x 38 on its centre line (radius {R_CELL_C:.3f}); arc {a0:.1f} to {a0 + ang:.1f} deg "
        f"({ang:.1f} deg); size_y = arc length")
    # protection circuit: beyond the cell's -77 end, toward the top, 2 mm along the arc
    pa0 = a0 + ang
    pang = math.degrees(P["prot"][0] / R_CELL_C)
    pc = pa0 + pang / 2
    bandpart("cell_protection", "", sector(R_LINER, R_LINER + P["cell_t"], pa0, pa0 + pang, -P["prot"][1] / 2, P["prot"][1] / 2), pc, 0.0,
             R_LINER, R_LINER + P["cell_t"], 0.0, (P["prot"][1], P["prot"][0], P["cell_t"]), True,
             f"2 x 5 mm on the cell tab, from {pa0 - 360:.1f} deg to {pa0 + pang - 360:.1f} deg (-77 end); thickness = cell envelope 1.6")
    # pads
    for nm, ref, px in zip(("VBUS", "D-", "D+", "GND"), ("CP1", "CP2", "CP3", "CP4"), P["pad_x"]):
        r0, r1 = R_OUT - P["shell_t"], R_OUT
        bandpart(f"pad_{nm}", ref, lcyl(180.0, P["pad_d"], r0, r1 + 0.3, x=px) & cyl_x(R_OUT, -10, 10), 180.0, 0.0, r0, r1, px,
                 (P["pad_d"], P["pad_d"], P["shell_t"]), True,
                 f"charging pad {nm}, 1.0 dia, through the shell at the lowest point, X {px}; outer face clipped flush with the band surface")
    return dict(parts=parts, envelope=envelope)


def motor_rim_min_wall(body, angle=None, n=24, step=0.025, reach=4.2):
    """Metal thickness along the outward radial ray (from the band axis) at points of the motor's rim
    (n points on the back circle and n on the front circle). Returns (min, (face, deg, x, y, z))."""
    a = P["motor_angle"] if angle is None else angle
    worst = (9e9, None)
    for face, r in (("back", R_LINER), ("front", R_LINER + P["motor_t"])):
        for k in range(n):
            ph = 2 * math.pi * k / n
            x, t = P["motor_d"] / 2 * math.cos(ph), P["motor_d"] / 2 * math.sin(ph)
            px, py, pz = gpos(a, t, r, x)
            d = Vector(0, py, pz - ZC)
            d = d * (1 / d.length)
            metal = 0.0
            for i in range(int(reach / step)):
                p = Vector(px, py, pz) + d * (i * step)
                if body.is_inside(p):
                    metal += step
            if metal < worst[0]:
                worst = (metal, (face, round(math.degrees(ph)), round(px, 2), round(py, 2), round(pz, 2)))
    return worst


LAYER_ORDER = ["glass", "screen", "board", "band", "body"]


def layers_json(parts):
    out = {"units": "mm", "up": "+Z", "axes": "X along the finger (+X fingertip), Y across (+Y thumb), Z up",
           "band_axis": {"y": 0.0, "z": ZC, "direction": "X"}, "layers": []}
    ex = {"glass": ([0, 0, 1], 14.0), "screen": ([0, 0, 1], 9.0), "board": ([0, 0, 1], 4.0),
          "body": ([0, 0, -1], 6.0)}
    for L in LAYER_ORDER:
        names = [p["name"] for p in parts if p["layer"] == L]
        e = {"name": L, "parts": names}
        if L == "band":
            e["explode"] = {"mode": "radial", "distance": 9.0,
                            "note": "each part moves outward along its radius from the band axis; "
                                    "part_dirs gives the unit vector [x, y, z] per part"}
            dirs = {}
            for p in parts:
                if p["layer"] == "band":
                    a = p["angle"] if p["angle"] is not None else 180.0
                    if p["name"].startswith("band_flex"):
                        a = 38.0 if p["name"].endswith("thumb") else -38.0
                    ar = math.radians(a)
                    dirs[p["name"]] = [0.0, round(math.sin(ar), 5), round(math.cos(ar), 5)]
            e["explode"]["part_dirs"] = dirs
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
            x, y, z = p["centre"]
            w.writerow([p["name"], p["ref"], p["layer"], f"{x:.3f}", f"{y:.3f}", f"{z:.3f}",
                        f"{p['size'][0]:.3f}", f"{p['size'][1]:.3f}", f"{p['size'][2]:.3f}",
                        "" if p["angle"] is None else f"{p['angle']:.2f}", str(bool(p["metal"])), p["note"]])


COLORS = {"glass": [0.55, 0.8, 0.95, 0.35], "screen": [0.1, 0.1, 0.15, 1.0], "board": [0.1, 0.55, 0.25, 1.0],
          "band": [0.9, 0.55, 0.1, 1.0], "body": [0.75, 0.75, 0.8, 0.25]}


def mesh_of(solid, tol=0.03):
    v, t = solid.tessellate(tol, 0.2)
    return [(p.X, p.Y, p.Z) for p in v], [tuple(x) for x in t]


def write_glb(parts, layers, path):
    import numpy as np
    buf = bytearray()
    views, accs, meshes, nodes, mats = [], [], [], [], []
    lay_mat = {}
    for L in LAYER_ORDER:
        lay_mat[L] = len(mats)
        c = COLORS[L]
        m = {"name": f"mat_{L}", "pbrMetallicRoughness": {"baseColorFactor": c, "metallicFactor": 0.1,
                                                         "roughnessFactor": 0.6}}
        if c[3] < 1.0:
            m["alphaMode"] = "BLEND"
        mats.append(m)
    pdirs = layers["layers"][3]["explode"]["part_dirs"]
    for i, p in enumerate(parts):
        v, t = mesh_of(p["solid"])
        V = np.array(v, dtype=np.float32)
        T = np.array(t, dtype=np.int64)
        tri = V[T]                                   # (n,3,3) flat shaded
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        ln = np.linalg.norm(n, axis=1, keepdims=True)
        ln[ln == 0] = 1
        n = (n / ln).astype(np.float32)
        pos = tri.reshape(-1, 3).astype(np.float32)
        nor = np.repeat(n, 3, axis=0).astype(np.float32)
        off = len(buf)
        buf += pos.tobytes()
        views.append({"buffer": 0, "byteOffset": off, "byteLength": pos.nbytes, "target": 34962})
        accs.append({"bufferView": len(views) - 1, "componentType": 5126, "count": len(pos), "type": "VEC3",
                     "min": pos.min(0).tolist(), "max": pos.max(0).tolist()})
        pa = len(accs) - 1
        off = len(buf)
        buf += nor.tobytes()
        views.append({"buffer": 0, "byteOffset": off, "byteLength": nor.nbytes, "target": 34962})
        accs.append({"bufferView": len(views) - 1, "componentType": 5126, "count": len(nor), "type": "VEC3"})
        na = len(accs) - 1
        meshes.append({"name": p["name"], "primitives": [{"attributes": {"POSITION": pa, "NORMAL": na},
                                                           "material": lay_mat[p["layer"]], "mode": 4}]})
        extras = {"reference": p["ref"], "layer": p["layer"], "metal": bool(p["metal"]),
                  "angle_deg": p["angle"], "centre": [round(c, 4) for c in p["centre"]]}
        if p["layer"] == "band":
            extras["explode_dir"] = pdirs[p["name"]]
        else:
            extras["explode_dir"] = next(l for l in layers["layers"] if l["name"] == p["layer"])["explode"]["dir"]
        nodes.append({"name": p["name"], "mesh": i, "extras": extras})
    while len(buf) % 4:
        buf.append(0)
    gltf = {"asset": {"version": "2.0", "generator": "thin.py", "extras": {"units": "mm", "up": "+Z (CAD axes, not glTF Y-up)"}},
            "scene": 0,
            "scenes": [{"name": "thin_ring_inside", "nodes": list(range(len(nodes))),
                        "extras": {"units": "mm", "up": "+Z", "layers": layers["layers"]}}],
            "nodes": nodes, "meshes": meshes, "materials": mats, "accessors": accs, "bufferViews": views,
            "buffers": [{"byteLength": len(buf)}]}
    js = json.dumps(gltf, separators=(",", ":")).encode()
    while len(js) % 4:
        js += b" "
    total = 12 + 8 + len(js) + 8 + len(buf)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(js), 0x4E4F534A) + js)
        f.write(struct.pack("<II", len(buf), 0x004E4942) + bytes(buf))


def main():
    OUT.mkdir(exist_ok=True)
    m = build()
    parts = m["parts"]
    write_csv(parts)
    layers = layers_json(parts)
    with open(HERE / "layers.json", "w") as f:
        json.dump(layers, f, indent=1)
    write_glb(parts, layers, OUT / "thin-inside.glb")
    solids = []
    for p in parts:
        s = p["solid"]
        s.label = p["name"]
        solids.append(s)
    export_step(Compound(children=solids, label="thin_ring_inside"), str(OUT / "thin-inside.step"))
    print(f"thin.py: {len(parts)} parts, ZC={ZC:.3f}, wrote placement.csv, layers.json, out/thin-inside.glb, out/thin-inside.step")
    return 0


if __name__ == "__main__":
    sys.exit(main())
