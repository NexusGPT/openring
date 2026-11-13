import numpy as np
from build123d import import_step
asm = import_step((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case/out/case_assembly_US9.step"))
for k in asm.children:
    if k.label in ("LED1", "hinge_pivot", "shell", "J1_usb4105"):
        v, t = k.tessellate(0.1, 0.3)
        a = np.array([[p.X, p.Y, p.Z] for p in v])
        bb = k.bounding_box()
        print(k.label, "tess", a.min(0).round(2), a.max(0).round(2), "bbox", [round(x, 2) for x in (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)], "loc", k.location.position)
