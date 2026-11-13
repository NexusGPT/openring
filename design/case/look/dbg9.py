import sys, math
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case"))
import numpy as np
import case as C
import pebble as PB
from build123d import Wire, Edge, Vector, Solid
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.gp import gp_Pnt
from OCP.Approx import Approx_ChordLength, Approx_Centripetal, Approx_IsoParametric
H = PB.PEB["H"]; ct = PB.PEB["CT"]; vt = PB.PEB["VT"]; et = PB.PEB["ET"]; S = PB.PEB["S"]
ret = 1 - et / S
zw1 = H - ct - vt
def top_secs(tlist, edge_u=(0.02, 0.06, 0.12, 0.2, 0.3, 0.42, 0.55, 0.7, 0.85, 1.0)):
    out = [(37.96, float(PB.rho_of_z(37.96, H)))]
    out += [(zw1 + vt * math.sqrt(1 - (1 - u) ** 2), 1 - u * et / S) for u in edge_u]
    out += [(H - ct * t * t, ret * t) for t in tlist]
    out.append((H, 0.0))
    return out
def loft(secs, par=Approx_Centripetal, deg=3, ruled=False):
    ts = BRepOffsetAPI_ThruSections(True, ruled, 1e-6)
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
def rep(name, secs, **kw):
    s = loft(secs, **kw)
    v = np.array([[p.X, p.Y, p.Z] for p in s.tessellate(0.02, 0.1)[0]])
    top = v[:, 2] > 38.2
    rp = PB.rho_point_vec(v[top, 0], v[top, 1]); d = v[top, 2] - PB.z_upper_of_rho(rp, H)
    print(name, "zmax %.3f (H %.2f)" % (v[:, 2].max(), H), "dz range %.3f..%.3f" % (d.min(), d.max()), "valid", s.is_valid)
rep("current t list", top_secs((0.92, 0.8, 0.6, 0.35)))
rep("dense t", top_secs((0.96, 0.9, 0.82, 0.72, 0.6, 0.48, 0.36, 0.25, 0.15)))
rep("dense t chord", top_secs((0.96, 0.9, 0.82, 0.72, 0.6, 0.48, 0.36, 0.25, 0.15)), par=Approx_ChordLength)
rep("dense t deg 5", top_secs((0.96, 0.9, 0.82, 0.72, 0.6, 0.48, 0.36, 0.25, 0.15)), deg=5)
rep("dense t isoparametric", top_secs((0.96, 0.9, 0.82, 0.72, 0.6, 0.48, 0.36, 0.25, 0.15)), par=Approx_IsoParametric)
rep("no crown sections", top_secs(()))
print("--- case.skin_part")
def meas(name, s):
    v = np.array([[p.X, p.Y, p.Z] for p in s.tessellate(0.02, 0.1)[0]])
    top = v[:, 2] > 38.2
    rp = PB.rho_point_vec(v[top, 0], v[top, 1]); d = v[top, 2] - PB.z_upper_of_rho(rp, H)
    print(name, "zmax %.3f" % v[:, 2].max(), "dz %.3f..%.3f" % (d.min(), d.max()))
s = C.skin_part(H, 37.96, H)
meas("skin_part(37.96, H)", s)
print([(round(z, 2), round(r, 3)) for z, r in PB.sections(H) if 37.96 + 0.15 < z])

for nm, a_, b_ in (("lid", 37.96, H), ("plate", 0.0, 3.0), ("shell", 3.0, 37.66)):
    s_ = C.skin_part(H, a_, b_)
    v = np.array([[p.X, p.Y, p.Z] for p in s_.tessellate(0.02, 0.1)[0]])
    print(nm, "z", v[:, 2].min().round(3), v[:, 2].max().round(3), "x", v[:, 0].min().round(2), v[:, 0].max().round(2), "y", v[:, 1].min().round(2), v[:, 1].max().round(2), "valid", s_.is_valid)
    if nm == "lid": meas("lid", s_)
