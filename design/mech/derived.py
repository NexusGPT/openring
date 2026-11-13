import sys, math
sys.path.insert(0, ".")
import ring
m = ring.build(size=9)
P = {p["name"]: p["solid"].bounding_box() for p in m["parts"]}
def r(v): return f"{v:.3f}".rstrip("0").rstrip(".")
for n in sorted(P):
    b = P[n]; print(f"BBOX {n} X {r(b.min.X)} {r(b.max.X)} Y {r(b.min.Y)} {r(b.max.Y)} Z {r(b.min.Z)} {r(b.max.Z)}")
k = m["keepout"].bounding_box(); print(f"KEEPOUT X {r(k.min.X)} {r(k.max.X)} Y {r(k.min.Y)} {r(k.max.Y)} Z {r(k.min.Z)} {r(k.max.Z)}")
print(f"motor body to keep-out: {r(k.min.X - P['motor'].max.X)}; sleeve into keep-out: {r(P['motor_sleeve'].max.X - k.min.X)}")
print(f"motor sleeve start to joystick body end: {r(P['motor_sleeve'].min.X - P['joystick_body'].max.X)}; joystick board end {r(P['joystick_board'].max.X)}")
g = P["cover_glass"]; print(f"GLASS {r(g.max.X - g.min.X)} x {r(g.max.Y - g.min.Y)} x {r(g.max.Z - g.min.Z)}")
for s in (5, 9, 13): print(f"BAND size {s} inner d {ring.ring_d(s):.2f}")
print("SCREWS", ring.screw_xy())
