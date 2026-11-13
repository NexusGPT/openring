"""Surface radius at the joystick per size: v6 probe (X +-2.85 on the radial line) against a probe at X 0 just outside the
round opening along the band (angle +- the opening's half width plus 0.05)."""
import math, os, sys
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/mech/thin"))
from build123d import import_step, Vector
EXT = (__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/look/s1/out")
JOY = {7: -84.0, 8: -81.0}
for n, bore in ((7, 17.3196), (8, 18.1324), (9, 18.9452), (10, 19.758), (11, 20.5708), (12, 21.3836), (13, 22.1964)):
    s = import_step(f"{EXT}/ring-merged32h-us{n}.step")
    by = {c.label: c for c in s.children}
    body, joy = by["body"], by["joystick"]
    ZC = -0.4 - bore / 2
    a = JOY.get(n, -78.0)
    def pr(ang, x):
        ar = math.radians(ang); r = 16.5
        while r > 5:
            if body.is_inside(Vector(x, r * math.sin(ar), ZC + r * math.cos(ar))):
                return round(r, 3)
            r -= 0.005
        return None
    old = min(pr(a, 2.85), pr(a, -2.85))
    d = math.degrees(2.85 / 13.0)
    new_t = (pr(a - d, 0.0), pr(a + d, 0.0))
    xs = [pr(a, x) for x in (2.85, 3.2, 3.6)]
    rtop = max(math.hypot(v.Y, v.Z - ZC) for v in joy.vertices())
    print(f"US {n}: angle {a}; v6 probe (X +-2.85) {old}; X 0 at angle -+{d:.2f} deg {new_t}; on the radial line at X 2.85 / 3.2 / 3.6 {xs}; exterior joystick top r {rtop:.3f}", flush=True)
