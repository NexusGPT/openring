#!/usr/bin/env python3
"""Radio corner: the metal left round it (faster form of corner_probe.py, which was stopped: out/v9/corner_probe_stopped.log).
Builds the model of folder arg 1 (env as the caller). On each bond plane of the corner (X = -8.60, Y = 2.05) the metal body is cut with a slab
0.01 thick on the metal side; on that small section the runs of metal are measured along Z (every 0.05 along the plane) and along the plane's other
axis (every 0.1 in Z) with is_inside at 0.01 steps. Prints the thinnest runs, the section pieces, the antenna to metal and to resin. Read only."""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
import thin  # noqa: E402
from build123d import Vector, Box, Pos  # noqa: E402
m = thin.build()
by = {p.name: p for p in m["parts"]}
body = by["outer_body"].solids()["metal"]
rc = by["radio_corner"].solids()["resin"]
X1, Y0 = thin.RC_X[1], thin.RC_Y0
slabX = Pos(X1 + 0.005, (Y0 + 9.0) / 2, 1.0) * Box(0.01, 9.0 - Y0, 8.0)          # X -8.60 to -8.59, Y 2.05 to 9.0, Z -3 to 5
slabY = Pos((-16.0 + X1) / 2, Y0 - 0.005, 1.0) * Box(X1 - (-16.0), 0.01, 8.0)    # Y 2.04 to 2.05, X -16 to -8.60
secX, secY = body & slabX, body & slabY
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
for lab, sec, along in (("X -8.60", secX, "Y"), ("Y 2.05", secY, "X")):
    sols = sec.solids()
    print(f"plane {lab}: metal section pieces {len(sols)}: " + "; ".join(
        f"{'Y' if along == 'Y' else 'X'} {(s.bounding_box().min.Y if along == 'Y' else s.bounding_box().min.X):.3f} to {(s.bounding_box().max.Y if along == 'Y' else s.bounding_box().max.X):.3f}, Z {s.bounding_box().min.Z:.3f} to {s.bounding_box().max.Z:.3f}, area {s.volume / 0.01:.3f} mm2" for s in sols))
    c0 = X1 + 0.005 if along == "Y" else Y0 - 0.005
    lo, hi = (Y0 + 0.01, 8.0) if along == "Y" else (-14.79, X1 - 0.01)
    n = int((hi - lo) / 0.05)
    for i in range(n + 1):
        u = lo + i * 0.05
        pt = (lambda z: Vector(c0, u, z)) if along == "Y" else (lambda z: Vector(u, c0, z))
        for a, b in runs([(-1.0 + k * 0.01, sec.is_inside(pt(-1.0 + k * 0.01))) for k in range(0, 451)]):
            res.append((b - a, f"plane {lab}: metal along Z at {along} {u:.2f}: Z {a:.2f} to {b:.2f}"))
    for k in range(0, 46):
        z = -0.95 + k * 0.1
        n2 = int((hi - lo) / 0.01)
        pt2 = (lambda u: Vector(c0, u, z)) if along == "Y" else (lambda u: Vector(u, c0, z))
        for a, b in runs([(lo + j * 0.01, sec.is_inside(pt2(lo + j * 0.01))) for j in range(n2 + 1)]):
            res.append((b - a, f"plane {lab}: metal along {along} at Z {z:.2f}: {along} {a:.2f} to {b:.2f}"))
res.sort()
print(f"metal runs measured on the two bond planes: {len(res)}; the thinnest 12:")
for w, s in res[:12]:
    print(f"  {w:.3f} mm  {s}")
cb = rc.bounding_box()
print(f"corner RC1: volume {rc.volume:.4f} mm3, X {cb.min.X:.3f} to {cb.max.X:.3f}, Y {cb.min.Y:.3f} to {cb.max.Y:.3f}, Z {cb.min.Z:.3f} to {cb.max.Z:.3f}")
ant = [s for v in by["antenna"].subs.values() for g in v for s in g.solids()]
print(f"antenna to the metal body: {min(a.distance_to(body) for a in ant):.4f} mm; antenna to the resin corner: {min(a.distance_to(rc) for a in ant):.4f} mm")
