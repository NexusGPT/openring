import sys, time, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pebble as PB
from build123d import Edge, Wire, Vector, Solid, Box, Pos
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.gp import gp_Pnt

def loft_solid(H, npts=96):
    ts = BRepOffsetAPI_ThruSections(True, False, 1e-6)
    secs = PB.sections(H)
    for i, (z, r) in enumerate(secs):
        if r == 0.0:
            ts.AddVertex(BRepBuilderAPI_MakeVertex(gp_Pnt(PB.PEB["XC"], 0, z)).Vertex())
        else:
            x, y = PB.outline_at(r, npts)
            w = Wire([Edge.make_spline([Vector(a, b, z) for a, b in zip(x, y)], periodic=True)])
            ts.AddWire(w.wrapped)
    ts.Build()
    return Solid(ts.Shape())

if __name__ == "__main__":
    H = 42.96
    t0 = time.time()
    s = loft_solid(H)
    print("loft", time.time() - t0, "valid", s.is_valid, "vol", s.volume, "faces", len(s.faces()))
    bb = s.bounding_box(); print(bb.min, bb.max)
    t0 = time.time()
    b = s & (Pos(0, 0, 18) * Box(200, 200, 36))
    print("bool", time.time() - t0, b.is_valid, b.volume)
