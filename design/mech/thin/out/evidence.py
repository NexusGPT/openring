import sys, itertools, math
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/mech/thin"))
import thin
from build123d import Vector
def collisions(label):
    m = thin.build(); P = m["parts"]; res = []
    for a, b in itertools.combinations(P, 2):
        if {a["name"], b["name"]} == {"outer_body", "band_liner"}: continue
        ba, bb = a["solid"].bounding_box(), b["solid"].bounding_box()
        if (ba.max.X < bb.min.X or bb.max.X < ba.min.X or ba.max.Y < bb.min.Y or bb.max.Y < ba.min.Y or ba.max.Z < bb.min.Z or bb.max.Z < ba.min.Z): continue
        x = a["solid"] & b["solid"]; v = x.volume if x is not None else 0.0
        if v > 0.001: res.append(f"{a['name']} x {b['name']} {v:.4f}")
    print(label, "->", res if res else "no collision")
    return m
thin.CH["joy_sw_off"] = 1.9; collisions("C1 joystick switches at 1.9 mm from the centre"); thin.CH["joy_sw_off"] = 2.1
thin.CH["notch_antenna"] = False; collisions("C2 no antenna notch in the board"); thin.CH["notch_antenna"] = True
thin.CH["notch_motor"] = False; collisions("C3 no motor-rim notch in the board"); thin.CH["notch_motor"] = True
m = collisions("final model")
# wall measurement along polar rays through the shell
body = [p for p in m["parts"] if p["name"] == "outer_body"][0]["solid"]
env = m["envelope"]
def wall(a, t, r, label):
    # point on the cavity rim; ray outward from the band axis through it
    x, y, z = thin.gpos(a, t, r)
    d = Vector(0, y, z - thin.ZC); L = d.length; d = d * (1 / L)
    n = 0; step = 0.005; first = None; last = None
    for i in range(0, 600):
        p = Vector(x, y, z) + d * (i * step)
        ins = body.is_inside(p)
        if ins:
            n += 1; first = first if first is not None else i * step; last = i * step
    print(f"{label}: material along the outward ray {n*step:.3f} mm (from {first} to {last})")
wall(-38.0, 3.6, thin.R_LINER + 2.1 + 0.075, "motor pocket rim (front, toward the top)")
wall(-38.0, -3.6, thin.R_LINER + 2.1 + 0.075, "motor pocket rim (front, toward the bottom)")
wall(-38.0, 0.0, thin.R_LINER + 2.1 + 0.075, "motor pocket centre")
wall(0.0, 0.0, thin.R_OUT - 0.5 - 0.01, "plain band wall at the top (inside the block)")
wall(120.0, 0.0, thin.R_OUT - 0.5 - 0.01, "plain band wall at 120 deg")
# corner wall at the panel corner (diagonal)
import math
print("panel-corner wall (analytic): outer arc centre (12.15, 4.875) r 2.5; cavity corner (13.725, 6.45):",
      round(2.5 - math.hypot(13.725 - 12.15, 6.45 - 4.875), 3))
