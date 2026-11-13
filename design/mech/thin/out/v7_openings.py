import sys
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/mech/thin"))
import thin
from build123d import Vector
m = thin.build()
by = {p.name: p for p in m["parts"]}
body = by["outer_body"].subs["metal"][0]
ctx = m["ctx"]
def run(a, x0, t0, dx, dt, r, cap=2.0, step=0.01):
    n = 0.0
    while n < cap:
        x = x0 + dx * (n + 0.005); t = t0 + dt * (n + 0.005)
        p = Vector(*thin.gpos(a, t, r, x))
        if not body.is_inside(p):
            break
        n += step
    return round(n, 2)
for name, a, rout, hx, ht in (("joystick opening (frame 5.4 x 6.4 + 0.2)", thin.P["joy_deg"], ctx["r_outer_joy"], 2.8, 3.3),
                              ("record opening (pill 4.4 x 2.4 + 0.2)", thin.P["rec_deg"], ctx["r_outer_rec"], 2.3, 1.3)):
    print(name, "at", a, "deg, body surface r", rout)
    for depth in (0.1, 0.3, 0.6):
        r = rout - depth
        print(f"  depth {depth} under the surface: metal beside the opening +X {run(a, hx, 0, 1, 0, r)}  -X {run(a, -hx, 0, -1, 0, r)}"
              f"  along the band +t {run(a, 0, ht, 0, 1, r)}  -t {run(a, 0, -ht, 0, -1, r)}  (mm, capped at 2.0)")
# collisions of the caps with the body, from the pair test
import itertools
for pn in ("joystick_cap", "record_cap"):
    tot = 0.0
    for c, s in by[pn].solids().items():
        x = s & body
        tot += x.volume if x is not None else 0.0
    print(pn, "x outer_body common volume:", round(tot, 5), "mm3")
