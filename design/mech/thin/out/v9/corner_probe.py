#!/usr/bin/env python3
"""Radio corner: the metal left round it. Builds the model of folder arg 1 (env as the caller) and measures, on the two bond planes of the corner
(X = -8.60, Y = 2.05) just on the metal side, every run of metal along Z (at each Y or X, 0.05 steps) and along the plane's other axis (at each Z,
0.02 steps), and prints the thinnest runs, the bond areas and the metal next to the antenna. Read only."""
import math, sys
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
import thin  # noqa: E402
from build123d import Vector  # noqa: E402
m = thin.build()
by = {p.name: p for p in m["parts"]}
body = by["outer_body"].solids()["metal"]
rc = by["radio_corner"].solids()["resin"]
E = 0.002
def runs(pts):
    out, cur = [], None
    for t, ins in pts:
        if ins and cur is None:
            cur = t
        if not ins and cur is not None:
            out.append((cur, t)); cur = None
    if cur is not None:
        out.append((cur, pts[-1][0]))
    return out
res = []
# plane X = -8.60 + E (metal side), Y from 2.05 to 7.6
X0 = thin.RC_X[1] + E
for i in range(0, 112):
    y = 2.06 + i * 0.05
    zs = [(-1.0 + k * 0.01, body.is_inside(Vector(X0, y, -1.0 + k * 0.01))) for k in range(0, 451)]
    for a, b in runs(zs):
        res.append((b - a, f"plane X -8.60: metal along Z at Y {y:.2f}: Z {a:.2f} to {b:.2f}"))
for k in range(0, 46):
    z = -0.95 + k * 0.1
    ys = [(2.06 + j * 0.01, body.is_inside(Vector(X0, 2.06 + j * 0.01, z))) for j in range(0, 560)]
    for a, b in runs(ys):
        res.append((b - a, f"plane X -8.60: metal along Y at Z {z:.2f}: Y {a:.2f} to {b:.2f}"))
# plane Y = 2.05 - E (metal side), X from -14.8 to -8.6
Y0 = thin.RC_Y0 - E
for i in range(0, 125):
    x = -14.79 + i * 0.05
    zs = [(-1.0 + k * 0.01, body.is_inside(Vector(x, Y0, -1.0 + k * 0.01))) for k in range(0, 451)]
    for a, b in runs(zs):
        res.append((b - a, f"plane Y 2.05: metal along Z at X {x:.2f}: Z {a:.2f} to {b:.2f}"))
for k in range(0, 46):
    z = -0.95 + k * 0.1
    xs = [(-14.79 + j * 0.01, body.is_inside(Vector(-14.79 + j * 0.01, Y0, z))) for j in range(0, 620)]
    for a, b in runs(xs):
        res.append((b - a, f"plane Y 2.05: metal along X at Z {z:.2f}: X {a:.2f} to {b:.2f}"))
res.sort()
print(f"metal runs on the two bond planes: {len(res)}; thinnest 12:")
for w, s in res[:12]:
    print(f"  {w:.3f} mm  {s}")
# bond faces: faces of the corner that lie on the two planes and touch metal
area = {"X -8.60": 0.0, "Y 2.05": 0.0}
for f in rc.faces():
    c = f.center()
    n = f.normal_at(c)
    if abs(abs(n.X) - 1) < 1e-6 and abs(c.X - thin.RC_X[1]) < 1e-4:
        if body.is_inside(Vector(c.X + E, c.Y, c.Z)) or True:
            area["X -8.60"] += f.area
    if abs(abs(n.Y) - 1) < 1e-6 and abs(c.Y - thin.RC_Y0) < 1e-4:
        area["Y 2.05"] += f.area
print(f"corner faces on the planes (resin to metal or to the cavity): X -8.60 {area['X -8.60']:.3f} mm2, Y 2.05 {area['Y 2.05']:.3f} mm2")
cb = rc.bounding_box()
print(f"corner RC1: volume {rc.volume:.4f} mm3, X {cb.min.X:.3f} to {cb.max.X:.3f}, Y {cb.min.Y:.3f} to {cb.max.Y:.3f}, Z {cb.min.Z:.3f} to {cb.max.Z:.3f}")
ant = [s for v in by["antenna"].subs.values() for g in v for s in g.solids()]
print(f"antenna to the metal body: {min(a.distance_to(body) for a in ant):.4f} mm; antenna to the resin corner: {min(a.distance_to(rc) for a in ant):.4f} mm")
