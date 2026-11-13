import sys
from build123d import import_step
f = sys.argv[1]
s = import_step(f)
print(type(s).__name__, "label", getattr(s, "label", None))
def walk(o, d=0):
    ch = list(getattr(o, "children", []))
    bb = o.bounding_box()
    print("  " * d + f"{type(o).__name__} '{o.label}' vol={getattr(o,'volume',0):.2f} faces={len(o.faces())} bbox=({bb.min.X:.2f},{bb.min.Y:.2f},{bb.min.Z:.2f})..({bb.max.X:.2f},{bb.max.Y:.2f},{bb.max.Z:.2f}) valid={o.is_valid}")
    for c in ch:
        walk(c, d + 1)
walk(s)
