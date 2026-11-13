import sys
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case"))
import numpy as np
import case as C
import pebble as PB
from build123d import Wire, Edge, Vector, Solid
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.gp import gp_Pnt
from OCP.Approx import Approx_ChordLength, Approx_Centripetal, Approx_IsoParametric
H = PB.PEB["H"]
def loft(secs, par=None, deg=3):
    ts = BRepOffsetAPI_ThruSections(True, False, 1e-6)
    if deg: ts.SetMaxDegree(deg)
    if par is not None: ts.SetParType(par)
    for z, r in secs:
        if r == 0.0:
            ts.AddVertex(BRepBuilderAPI_MakeVertex(gp_Pnt(PB.PEB["XC"], 0, z)).Vertex())
        else:
            xx, yy = PB.outline_at(r, 96)
            ts.AddWire(Wire([Edge.make_spline([Vector(a, b, z) for a, b in zip(xx, yy)], periodic=True)]).wrapped)
    ts.Build()
    return Solid(ts.Shape())
S = PB.PEB["S"]; reb = 1 - PB.PEB["EB"] / S; cb = PB.PEB["CB"]
full = PB.sections(H)
bot = [(z, r) for z, r in full if z < 3.0]
for name, secs, kw in [
  ("as built", bot + [(3.0, float(PB.rho_of_z(3.0, H)))], {}),
  ("chord", bot + [(3.0, float(PB.rho_of_z(3.0, H)))], dict(par=Approx_ChordLength)),
  ("centripetal", bot + [(3.0, float(PB.rho_of_z(3.0, H)))], dict(par=Approx_Centripetal)),
  ("deg 0 (auto)", bot + [(3.0, float(PB.rho_of_z(3.0, H)))], dict(deg=0)),
  ("pole at 0.5 flat start", [(0.0, 0.0)] + [(cb * t * t, reb * t) for t in (0.5, 0.75, 0.9)] + bot[5:] + [(3.0, float(PB.rho_of_z(3.0, H)))], {}),
]:
    try:
        s = loft(secs, **kw)
        v = np.array([[p.X, p.Y, p.Z] for p in s.tessellate(0.1)[0]])
        print(name, "z", v[:, 2].min().round(2), v[:, 2].max().round(2), "x", v[:, 0].min().round(1), v[:, 0].max().round(1), "y", v[:, 1].min().round(1), v[:, 1].max().round(1), "n sec", len(secs))
    except Exception as e:
        print(name, "FAILED", repr(e)[:80])
print([ (round(z,2), round(r,3)) for z, r in bot])
