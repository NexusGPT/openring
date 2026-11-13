import sys
from build123d import import_step
D = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case/out/parts/")
for n in ("shell", "lid", "base_plate", "liner", "foot", "usb_bezel", "light_window", "seam_trim", "lid_seam_trim"):
    s = import_step(D + n + ".step")
    bb = s.bounding_box()
    print("%-14s valid %s solids %d vol %9.1f bbox x %.1f..%.1f y %.1f..%.1f z %.2f..%.2f" % (n, s.is_valid, len(s.solids()), s.volume, bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z, bb.max.Z))
