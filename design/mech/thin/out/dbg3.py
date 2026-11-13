import sys, math
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/mech/thin"))
import thin
from build123d import Vector
m = thin.build(); body = [p for p in m["parts"] if p["name"] == "outer_body"][0]["solid"]
px, py, pz = 3.38, -6.78, -2.78
d = Vector(0, py, pz - thin.ZC); d = d * (1 / d.length)
prev = None; 
for i in range(0, 120):
    p = Vector(px, py, pz) + d * (i * 0.025)
    ins = body.is_inside(p)
    if ins != prev:
        print(f"s={i*0.025:.3f} r={math.hypot(p.Y, p.Z - thin.ZC):.3f} inside={ins}")
        prev = ins
print("r_outer at angle", thin.r_outer(43.7), "R_OUT_SH", thin.R_OUT_SH)
