"""print the structure of a board STEP written by kicad-cli: children, labels, bounding boxes. usage: inspect_step.py <file.step>"""
import sys

from build123d import import_step

s = import_step(sys.argv[1])
bb = s.bounding_box()
print("whole: x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f" % (bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z, bb.max.Z))


def walk(c, depth=0):
    for k in c.children:
        b = k.bounding_box()
        print("  " * depth, repr(k.label), type(k).__name__, "solids", len(k.solids()),
              "x %.3f..%.3f y %.3f..%.3f z %.3f..%.3f" % (b.min.X, b.max.X, b.min.Y, b.max.Y, b.min.Z, b.max.Z))
        if depth < 2:
            walk(k, depth + 1)


walk(s)
