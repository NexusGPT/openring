"""J1: do the library 3D model's legs (solids that go below the board top) sit in the footprint's plated slots? Compares, in the STEP frame
(X = KiCad x, Y = -KiCad y), each J1 plated hole of the board file with the J1 model solids that reach below z 0.9.
usage: j1_model_vs_pads.py <main.json> <main.step>"""
import json
import sys

from build123d import import_step

d = json.load(open(sys.argv[1]))
fp = [f for f in d["footprints"] if f["ref"] == "J1"][0]
holes = [(p["num"], p["x"], -p["y"], p["drill"]) for p in fp["pads"] if p["drill"] > 0]
smd = [(p["num"], p["x"], -p["y"]) for p in fp["pads"] if p["drill"] == 0]
print("J1 footprint", fp["fpid"], "at", fp["x"], fp["y"], "rot", fp["rot"])
for h in holes:
    print(" plated hole %s at X %.3f Y %.3f drill %.3f" % h)
s = import_step(sys.argv[2])
j = [c for c in s.children if "USB4105" in (c.label or "")][0]
legs = []
for so in j.solids():
    b = so.bounding_box()
    if b.min.Z < 0.9:
        legs.append(((b.min.X + b.max.X) / 2, (b.min.Y + b.max.Y) / 2, b.min.Z, b.size.X, b.size.Y))
for l in legs:
    print(" model solid below the board top: centre X %.3f Y %.3f, bottom z %.3f, size %.3f x %.3f" % l)
bb = j.bounding_box()
print("model box X %.3f..%.3f Y %.3f..%.3f Z %.3f..%.3f" % (bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z, bb.max.Z))
sx = [p[1] for p in smd]
print("SMD pads X %.3f..%.3f (signal row)" % (min(sx), max(sx)))
for h in holes:
    near = min(legs, key=lambda l: (l[0] - h[1]) ** 2 + (l[1] - h[2]) ** 2) if legs else None
    if near:
        print(" hole %s: nearest leg at dX %+.3f dY %+.3f" % (h[0], near[0] - h[1], near[1] - h[2]))
