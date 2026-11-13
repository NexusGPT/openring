#!/usr/bin/env python3
"""Geometry of the two boards, read from the case model (design/case/case.py and design/case/out/case_params.json).
Every number carries the line or key it comes from.  Frames:
  PCB1 board frame: u = case x - pcb1_x0 (right), d = - case y (down, KiCad y direction); v = case y (up) where a comment says so.
  PCB2 board frame: seen from the front face (the face with the spring pins): kx = - case y, ky = - (case z - z_pin).
If case.py changes, the asserts below fail and name the line.
Since case model round 4 (2026-11-13) the model READS the two boards from their files (design/case/r4/case_boards.py). The board-frame places the old
model held as reserved boxes (the socket front, the module box, the floor slot) no longer exist in case.py: they are FROZEN below at the values the
committed boards were generated from (case.py of commit 61620f6e), and the asserts at the end compare them with what the model records of the board file
(case_params.json key boards)."""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
CASE_DIR = os.path.abspath(os.path.join(HERE, "..", "..", "..", "case"))
SRC = open(os.path.join(CASE_DIR, "case.py")).read().splitlines()
P = json.load(open(os.path.join(CASE_DIR, "out", "case_params.json")))


def line_with(pattern):
    for i, l in enumerate(SRC):
        if re.search(pattern, l):
            return i + 1, l
    raise AssertionError("case.py line not found: " + pattern)


def num(pattern, group=1, cast=float):
    n, l = line_with(pattern)
    m = re.search(pattern, l)
    return cast(m.group(group)), n


# ---------------- PCB1 (case.py line 141: PCB1 = dict(x=23.0, y=35.4, t=1.0); case_params.json pcb1_x0)
(BOARD_W, _), (BOARD_H, _), (BOARD_T, L_PCB1) = (num(r"PCB1 = dict\(x=([\d.]+)"), num(r"PCB1 = dict\(x=[\d.]+, y=([\d.]+)"), num(r"PCB1 = dict\(x=[\d.]+, y=[\d.]+, t=([\d.]+)"))
# round 2: the board may grow toward +y (d negative, the socket side) up to the cavity wall (case.py line 142 CAV_YH = 20.35, 0.15 mm kept): d from BOARD_D0 to BOARD_D1
EXTEND = float(__import__('os').environ.get('CASE_EXTEND', '0'))
PCB1_X0 = P["pcb1_x0"]                         # case_params.json key pcb1_x0 (case.py line 702: pcb1_x0 = x_lay + 1.9)
PCB1_Z = P["pcb1_z"]                           # key pcb1_z: (z0, z1) of PCB1
# ---------------- J1 (case.py lines 172-174: J1_LIP, JY = 8.0, J1_YC = JY + 8.94 / 2; line 745 j1 box 7.35 x 8.94; case_params.json j1_front)
JY, L_JY = num(r"^JY = ([\d.]+)")
J1_W = 8.94                                    # case.py line 174 / USB4105 drawing p.1 (8.94)
J1_YC = JY + J1_W / 2
J1_FRONT_U = -3.4499136232021907               # FROZEN (case.py of 61620f6e: j1_front - pcb1_x0, the reserved socket box). Today the key j1_front is the real
                                               # socket body front of the board's 3D export; the board tab edge is checked against the board file below
J1_TAB_FRONT = 1.6                             # case.py line 741 'jx0 + 1.6': the board tab starts this far behind the socket front
J1_ORIGIN_FROM_FRONT = 4.18                    # USB4105 drawing p.1: mating face at y = +4.18 mm in the footprint frame
J1_U = J1_FRONT_U + J1_ORIGIN_FROM_FRONT
J1_D = -J1_YC
# tab: the model tab is y JY .. JY + 8.94 (case.py line 741); the shell slot pads (x +-4.32, 1.0 wide) need +-5.02 round the socket centre for a 0.2 mm copper edge
TAB_HALF = 5.1                                  # ours: 4.32 + 0.5 + 0.2 (JLCPCB capability: copper clearance from routed edges >= 0.2 mm) + 0.08
TAB_U0 = J1_FRONT_U + J1_TAB_FRONT              # tab front edge (u)
# ---------------- U1 (case.py line 744: box(pcb1_x0 + 0.6, pcb1_x0 + 0.6 + 15.4, -15.6, 4.9, ...))
U1_X0, U1_W, U1_V0, U1_V1 = 0.6, 15.4, -15.6, 4.9     # FROZEN: the reserved module box of case.py at 61620f6e (line 744); the model now takes U1 from the board file
U1_L = U1_V1 - U1_V0                           # module length 20.5 mm (case_esp32s3_mini1.pdf Figure 10-1 p.42)
# W5 change: the module overhangs the board edge at its antenna end (Espressif: antenna area at or beyond the board edge). The model's reserved volume sits fully on the
# board (v -15.6 .. 4.9); moved here by U1_OVERHANG + 2.1 toward -v. The cavity half width is 20.35 (case.py line 142 CAV_YH), the module end then is 0.65 mm from its wall.
U1_OVERHANG = 2.0
U1_MODEL_V0, U1_MODEL_V1 = U1_V0, U1_V1
BOARD_D1 = BOARD_H / 2                     # unchanged end (antenna end), d = +17.7
BOARD_D0 = -BOARD_H / 2 - EXTEND           # socket end moves out by EXTEND mm
U1_V0 = -(BOARD_H / 2) - U1_OVERHANG
U1_V1 = U1_V0 + U1_L
U1_U = U1_X0 + U1_W / 2
U1_D = -(U1_V0 + U1_V1) / 2
U1_BODY = (U1_X0, -U1_V1, U1_X0 + U1_W, -U1_V0)            # (u0, d0, u1, d1)
# antenna: module antenna area 5.05 mm at the -Y end (case_esp32s3_mini1.pdf Figure 11-1 p.45); the module is rotated 180 degrees so the antenna is at v = U1_V0
ANT_AREA = 5.05
ANT_KEEPOUT = (0.0, -(U1_V0 + ANT_AREA), 16.5, BOARD_D1)   # u 0..16.5, v from the board edge to the antenna boundary (no copper, no parts, no vias)
ANT_KEEPOUT_V = (U1_V0, U1_V0 + ANT_AREA)
# ---------------- LED1 (case.py line 175 LED_Y = 6.0 and line 746: LED box at pcb1_x0 + 0.6 .. + 1.6)
LED_Y, L_LED = num(r"^LED_Y = ([\d.]+)")
LED_U = 1.6                                    # model centre is 1.4; moved +0.2 mm so the pad copper keeps 0.2 mm from the board edge
LED_D = -(LED_Y + 0.1)                         # moved 0.1 mm up (+v) so the courtyards of the LED and the module do not touch
# ---------------- floor slot for the wires (case.py line 827: slot = box(x_b + 1.0, x_b + 4.0, -4.0, 4.0, ...))
X_B = P["x_b"]
SLOT = (16.457156508802775, -4.0, 19.457156508802775, 4.0)   # FROZEN in the board frame (61620f6e: x_b + 1.0 - pcb1_x0 .. x_b + 4.0 - pcb1_x0); the model's own slot today: case.py "slot = box(x_b - REC_D - 0.3, x_b + 4.0"
# ---------------- PCB2 (case.py lines 771-773)
PCB2_T = 0.8
Z_PIN = P["z_pin"]
PCB2_Z_HALF = 2.5
PCB2_INNER_HALF_MODEL = 1.95                   # line 771: box(x_b, x_b + 0.8, -1.95, 1.95, z_pin - 2.5, z_pin + 2.5)
PCB2_WING_IN_MODEL, PCB2_WING_OUT = 2.05, 4.9  # lines 772-773
YPIN = P["ypin"]                               # key ypin: [3.521, 1.197, -1.197, -3.521] (P1..P4)
X_B_INNER, X_BO = P["x_b"], P["x_bo"]          # keys x_b, x_bo: front face x of the inner island and the two wings
# our widths (see board-notes.md): P2/P3 pads dia 1.7 at |y| 1.197 reach 2.047, so the inner island needs >= 2.25 for a 0.2 mm copper edge
PCB2_INNER_HALF = 2.25
PCB2_WING_IN = PCB2_INNER_HALF + 0.10          # the model's 0.1 mm gap between islands (2.05 - 1.95)
assert abs(PCB2_WING_IN_MODEL - PCB2_INNER_HALF_MODEL - 0.10) < 1e-9


# ---------------- the frozen values against the board file as the model reads it (case_params.json key boards)
_B = P.get("boards")
if _B:
    assert abs(_B["main_u_range"][0] - TAB_U0) < 1e-5, "board tab edge %r is not TAB_U0 %r" % (_B["main_u_range"][0], TAB_U0)
    assert abs(_B["main_u_range"][1] - BOARD_W) < 1e-6, "board width"
    assert abs(_B["main_d_range"][1] - BOARD_H / 2) < 1e-6, "board antenna end"
    assert abs(_B["main_thickness"] - BOARD_T) < 1e-6 and abs(_B["pins_thickness"] - PCB2_T) < 1e-6, "board thickness"
    BOARD_EXTEND_BUILT = -_B["main_d_range"][0] - BOARD_H / 2      # how far the committed board grows toward the socket side (CASE_EXTEND at its build)


def dist_to_rect(u, d, r):
    dx = max(r[0] - u, 0, u - r[2])
    dy = max(r[1] - d, 0, d - r[3])
    return (dx * dx + dy * dy) ** 0.5


if __name__ == "__main__":
    for k in ("BOARD_W", "BOARD_H", "BOARD_T", "PCB1_X0", "J1_FRONT_U", "J1_U", "J1_D", "TAB_U0", "TAB_HALF", "U1_U", "U1_D", "U1_BODY", "ANT_KEEPOUT",
              "LED_U", "LED_D", "SLOT", "Z_PIN", "YPIN", "X_B_INNER", "X_BO", "PCB2_INNER_HALF", "PCB2_WING_IN", "PCB2_WING_OUT"):
        print(k, globals()[k])
    print("case.py lines: PCB1", L_PCB1, "JY", L_JY, "LED_Y", L_LED)
    if _B:
        print("board file as the model reads it: u", _B["main_u_range"], "d", _B["main_d_range"], "built with CASE_EXTEND", round(BOARD_EXTEND_BUILT, 6))
