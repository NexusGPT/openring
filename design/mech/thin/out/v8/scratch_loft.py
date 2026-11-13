import math, time
from build123d import Solid, Wire, Face, Vector, loft
RC, T = 0.755, 0.11
Z0 = 0.59
YC = 5.9 - RC
def section(th_deg, x0, x1, sg=1):
    th = math.radians(th_deg)
    n = (math.cos(th), math.sin(th))
    def pt(x, off):
        y = YC + (RC + off) * n[0]
        z = Z0 + (RC + off) * n[1]
        return Vector(x, sg * y, z)
    w = Wire.make_polygon([pt(x0, -T/2), pt(x1, -T/2), pt(x1, T/2), pt(x0, T/2)], close=True)
    return w
t0 = time.time()
N = 9
secs = []
for i in range(N + 1):
    th = 90.0 * i / N
    f = th / 90.0
    x0 = -3.4 + (-3.5 + 3.4) * f
    x1 = -1.6 + (-1.0 + 1.6) * f
    secs.append(section(th, x0, x1))
s = Solid.make_loft(secs, False)
print("valid", s.is_valid, "vol", s.volume, "t", time.time() - t0)
# analytic: integral w t RC dtheta, w = 1.8 + 0.7 f
an = sum((1.8 + 0.7 * (i + 0.5) / 2000) * T * RC * (math.pi / 2 / 2000) for i in range(2000))
print("analytic", an)
bb = s.bounding_box(); print(bb.min, bb.max)
