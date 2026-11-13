import sys, math
from build123d import import_step, Vector, Box, Pos
s = import_step((__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/look/s1/out/ring-merged32.step"))
by = {c.label: c for c in s.children}
body, glass = by["body"], by["glass"]
ZC = -9.875
def outer(a, x=0.0):
    ar = math.radians(a)
    r = 14.0
    while r > 5:
        p = Vector(x, r*math.sin(ar), ZC + r*math.cos(ar))
        if body.is_inside(p): return round(r, 3)
        r -= 0.01
for a in (0, 19, 38, 49, 62, 80, 95, 110, 130, 180, 250, 311):
    print("angle", a, "outer r at X0:", outer(a), " at X3:", outer(a, 3.0), " at X3.8:", outer(a, 3.8))
for y in (0, 3, 5, 6.4, 7.0):
    g = glass & Pos(0, y, 3) * Box(0.05, 0.05, 6)
    bb = g.bounding_box() if g is not None else None
    print("glass at y", y, (round(bb.min.Z,3), round(bb.max.Z,3)) if bb else None)
