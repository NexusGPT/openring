import sys, math, json
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case"))
import numpy as np
import case as C
from build123d import import_step
P = json.load(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case/out/case_params.json")))
hull = P["hull_w"]
print("hull", len(hull))
d = C.dilate(C.hull2d(hull), 1.8, 36)
print("dilated", len(d))
print('simplified', len(C.simplify_convex(d)))
w = C.rolled_prism(d, 19.7, 40.0, 1.8)
print("rolled valid", w.is_valid, "vol", round(w.volume, 1), "faces", len(w.faces()))
w2 = C.prism_xy(d, 19.7, 40.0)
print("plain valid", w2.is_valid, "vol", round(w2.volume, 1))
w3 = C.prism_xy(hull, 19.7, 40.0)
print("hull prism valid", w3.is_valid)
try:
    fx = w.fix()
    print("fixed valid", fx.is_valid, round(fx.volume, 1))
except Exception as e:
    print("fix failed", repr(e)[:100])
from OCP.ShapeFix import ShapeFix_Shape
sf = ShapeFix_Shape(w.wrapped); sf.Perform()
from build123d import Solid
w4 = Solid(sf.Shape()); print("shapefix valid", w4.is_valid, round(w4.volume, 1))
# simplified polygons, plain prism valid?
P = C.simplify_convex(d)
print("simplified prism valid", C.prism_xy([tuple(p) for p in P], 19.7, 40).is_valid)
# which section pair invalid: build with only 2 sections
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from build123d import Wire, Vector
for n_ in (2, 3, 5):
    ts = BRepOffsetAPI_ThruSections(True, True, 1e-6)
    for i in range(n_):
        ph = (math.pi / 2) * i / (n_ - 1) if n_ > 1 else 0
        ts.AddWire(Wire.make_polygon([Vector(float(x), float(y), 19.7 + 0.3 * i) for x, y in P], close=True).wrapped)
    ts.Build()
    print("identical sections", n_, Solid(ts.Shape()).is_valid)
