#!/usr/bin/env python3
"""The 0.06 mm metal at Z 2.65 to 2.71 over the screen tail's fold pocket (corner_probe2.log): measured on the body of the thin.py of folder arg 1,
along Z at X -13.90 and Y 0.00, 1.50, 2.04, 2.06, 2.60 (0.005 steps). Read only."""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
import thin  # noqa: E402
from build123d import Vector  # noqa: E402
m = thin.build()
body = {p.name: p for p in m["parts"]}["outer_body"].solids()["metal"]
for y in (0.0, 1.5, 2.04, 2.06, 2.6):
    zs = [2.4 + k * 0.005 for k in range(0, 101)]
    ins = [z for z in zs if body.is_inside(Vector(-13.90, y, z))]
    print(f"{sys.argv[1].split('/')[-1] or sys.argv[1]}: X -13.90 Y {y:.2f}: metal at Z {min(ins):.3f} to {max(ins):.3f} ({len(ins)} of {len(zs)} points from Z 2.400 to 2.900)" if ins else f"X -13.90 Y {y:.2f}: no metal from Z 2.4 to 2.9")
