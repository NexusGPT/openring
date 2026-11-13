"""b2 geometry: outer pins radial (axis through the US 10 bore centre and the pad centre), working height 2.05 along the axis; where do their base
points (the pin board land centres) land against the inner pins' bases, which stay axial at 2.05? Land dia 1.70 (P70-6000045R footprint, board-notes.md
part a), barrel 1.50. usage: python radial_pins.py"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import case as C  # noqa: E402

H = 2.05
n = 10
r = C.pad_face_r(n)
cx = C.cx_of(n)
th = C.pad_angles(n)
base = {}
for k, p in enumerate(C.PL["pads"]):
    fx, fy = C.pad_face_xy(n, k)
    if abs(fy) > 2.0:                                   # outer: radial
        bx, by = cx - (r - H) * math.cos(th[k]), (r - H) * math.sin(th[k])
        kind = "radial, tilt %.2f deg" % math.degrees(th[k])
    else:
        bx, by = fx + H, fy
        kind = "axial"
    base[p["net"]] = (bx, by)
    print(f"{p['net']}: pad face ({fx:.3f}, {fy:.3f}) at {math.degrees(th[k]):.2f} deg; base ({bx:.3f}, {by:.3f}) {kind}")
d = math.dist(base["VBUS"], base["D-"])
print(f"US {n}: bore centre x {cx:.3f}, pad face radius {r:.4f}")
print(f"distance between the base centres of P1 (radial) and P2 (axial): {d:.3f} mm; two 1.70 mm lands need 1.70 plus the island gap and edge copper; two 1.50 barrels need 1.50")
print(f"C5d / axial outer pin base for comparison: ({C.pad_face_xy(n, 0)[0] + H:.3f}, {C.pad_face_xy(n, 0)[1]:.3f})")
