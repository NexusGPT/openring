#!/usr/bin/env python3
"""Cover glass bottom and top Z at given (X, Y) points, read from the exterior STEP that the inside model v4 uses
(thin.load_exterior, read only). Usage: glass_probe.py  (points are listed below). Output: one line per point."""
import sys
from pathlib import Path

THIN = Path((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/mech/thin"))
sys.path.insert(0, str(THIN))
import thin  # noqa: E402
from build123d import Box, Pos  # noqa: E402

POINTS = [("window v4 (thin-notes row D)", -13.25, -4.7), ("window first layout", -12.425, -3.2), ("window recommended", -12.425, -2.95),
          ("centre", 0.0, 0.0), ("Y -3.2 at X -13.45", -13.45, -3.2), ("Y -3.2 at X -13.0", -13.0, -3.2),
          ("Y -3.2 at X -12.0", -12.0, -3.2), ("Y -3.2 at X -11.0", -11.0, -3.2)]
body, glass, *_ = thin.load_exterior()
print(f"exterior file: {thin.EXT_FILE}")
for name, x, y in POINTS:
    c = glass & Pos(x, y, 3.0) * Box(0.02, 0.02, 8.0)
    try:
        bb = c.bounding_box()
        print(f"{name}: X {x} Y {y}: glass bottom Z {bb.min.Z:.3f} top Z {bb.max.Z:.3f} thickness {bb.max.Z - bb.min.Z:.3f}")
    except Exception as e:
        print(f"{name}: X {x} Y {y}: no glass ({e})")
