# makes a test ring-like STEP (block plus band) in tools/testdata/parts/body
from build123d import *
import sys
out = sys.argv[1]
with BuildPart() as p:
    with BuildSketch():
        RectangleRounded(29.3, 14.75, 2.5)
    extrude(amount=3.2)
    with Locations((0, 0, -9.875)):
        Cylinder(12.05, 8.0, rotation=(0, 90, 0), mode=Mode.ADD)
    with Locations((0, 0, -9.875)):
        Cylinder(9.475, 8.0, rotation=(0, 90, 0), mode=Mode.SUBTRACT)
export_step(p.part, out)
