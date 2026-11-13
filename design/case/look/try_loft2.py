import sys, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pebble as PB
from build123d import Edge, Wire, Vector, Solid, Box, Pos
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.gp import gp_Pnt
from OCP.Approx import Approx_ChordLength, Approx_Centripetal, Approx_IsoParametric

H = 42.96
x, y = PB.unit_plan(2000)
A1 = 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))
zz = np.linspace(0, H, 20001)
Vexp = A1 * np.trapezoid(PB.rho_of_z(zz, H) ** 2, zz)
print("expected volume", Vexp)

def loft(secs, ruled, npts=96, smooth=False, maxdeg=None, par=None, vertex=True):
    ts = BRepOffsetAPI_ThruSections(True, ruled, 1e-6)
    if par is not None: ts.SetParType(par)
    if smooth: ts.SetSmoothing(True)
    if maxdeg: ts.SetMaxDegree(maxdeg)
    for z, r in secs:
        if r == 0.0:
            ts.AddVertex(BRepBuilderAPI_MakeVertex(gp_Pnt(PB.PEB["XC"], 0, z)).Vertex())
        else:
            xx, yy = PB.outline_at(r, npts)
            ts.AddWire(Wire([Edge.make_spline([Vector(a, b, z) for a, b in zip(xx, yy)], periodic=True)]).wrapped)
    ts.Build()
    return Solid(ts.Shape())

import traceback
cases = [
    ("nonruled 60 deg3", dict(maxdeg=3), PB.sections(H, 30, 32)),
    ("nonruled 60 deg3 smooth", dict(maxdeg=3, smooth=True), PB.sections(H, 30, 32)),
    ("nonruled 60 centripetal", dict(par=Approx_Centripetal), PB.sections(H, 30, 32)),
    ("ruled 100", dict(ruled=True), PB.sections(H, 50, 52)),
]
for name, kw, secs in cases:
    kw.setdefault("ruled", False)
    try:
        t0 = time.time()
        s = loft(secs, **kw)
        vs = s.tessellate(0.2)[0]
        v = np.array([[p.X, p.Y, p.Z] for p in vs])
        print(name, "t", round(time.time() - t0, 2), "valid", s.is_valid, "vol", round(s.volume), "ratio", round(s.volume / Vexp, 3),
              "tess bbox", v.min(0).round(1), v.max(0).round(1), "faces", len(s.faces()))
    except Exception as e:
        print(name, "FAILED", repr(e)[:100])
