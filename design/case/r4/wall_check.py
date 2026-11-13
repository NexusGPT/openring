"""Thinnest shell wall round the under-floor cavity (and r4's lead pocket): plan distance from the cavity outline to the skin's outline (look/pebble.py)
at heights from the bottom plate to the ceiling. usage: wall_check.py <case_params.json> [base]   ('base': the C5d cavity, rebuilt from its parameters)"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "look"))
import pebble as PB  # noqa: E402

prm = json.load(open(sys.argv[1]))
PB.PEB.update(prm["pebble"])
H = prm["h_tot"]
if len(sys.argv) > 2 and sys.argv[2] == "base":
    x0, x1 = prm["x_lay"] + 1.5, prm["cell_x0"] + 23.0 + 0.6
    y0, y1 = -20.35, 20.35
    z0, z1 = prm["zp"], prm["zf"] - 1.8
    boxes = [("cavity", x0, x1, y0, y1, z0, z1)]
else:
    c = prm["cavity"]
    lo = c["low"]
    boxes = [("cavity below the board", lo["x0"], lo["x1"], lo["y0"], lo["y1"], lo["z0"], lo["z1"]),
             ("cavity at the board", c["x0"], c["x1"], c["y0"], c["y1"], c["z0"], c["z1"])]
    lp = c["lead_pocket"]
    boxes.append(("lead pocket", lp[0][0], lp[0][1], lp[1][0], lp[1][1], lp[2][0], lp[2][1]))


def seg_dist(P, poly):
    A = np.asarray(poly)
    B = np.roll(A, -1, axis=0)
    out = np.full(len(P), 1e9)
    for a, ab in zip(A, B - A):
        t = np.clip(((P - a) @ ab) / max(ab @ ab, 1e-12), 0, 1)
        out = np.minimum(out, np.hypot(*(P - (a + t[:, None] * ab)).T))
    return out


worst = (1e9, None)
for name, x0, x1, y0, y1, z0, z1 in boxes:
    for z in np.linspace(max(z0, 0.05), z1, 12):
        poly = np.array(PB.outline_at(float(PB.rho_of_z(z, H)), 720)).T
        pts = np.array([(x, y0) for x in np.linspace(x0, x1, 200)] + [(x, y1) for x in np.linspace(x0, x1, 200)]
                       + [(x0, y) for y in np.linspace(y0, y1, 200)] + [(x1, y) for y in np.linspace(y0, y1, 200)])
        d = seg_dist(pts, poly)
        i = int(np.argmin(d))
        if d[i] < worst[0]:
            worst = (float(d[i]), (name, round(float(pts[i][0]), 2), round(float(pts[i][1]), 2), round(float(z), 2)))
print("thinnest wall round the cavity (plan distance cavity outline to skin, box corners not rounded): %.3f mm at %s (name, x, y, z)" % worst)
