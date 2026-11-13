#!/usr/bin/env python3
"""Gap from E1 (front face of PCB2's inner island, x = x_b) to the band's inner face, ring sizes US 7 to 13.
Reads only design/case/out/case_params.json (written by case.py): x_b, cx (bore centre x), ri (bore radius), pad_face_r not needed
because the recess is 0 here (checked: pad faces are flush). Band inner face at lateral offset y: x = cx - sqrt(ri^2 - y^2).
E1 front strip is 3.9 mm wide (board-notes.md line 189 / conflict 7), so y runs -1.95..+1.95."""
import json
R = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case/out/case_params.json")
d = json.load(open(R))
xb = d["x_b"]
print("x_b", xb, "pad_x_off", d["pad_x_off"])
import math
lo, hi, edge = [], [], []
for n in range(7, 14):
    cx, ri = d["cx"][str(n)], d["ri"][str(n)]
    g0 = xb - (cx - ri)
    ge = xb - (cx - math.sqrt(ri**2 - 1.95**2))
    pin_inner = d["pin_heights"][str(n)][1]
    print(f"US {n}: ri {ri:.4f} cx {cx:.4f} gap(y=0) {g0:.3f} gap(y=+-1.95) {ge:.3f} inner pin height {pin_inner:.3f} diff gap-pin {g0-pin_inner:.4f}")
    lo.append(g0); hi.append(ge)
print(f"range at y=0: {min(lo):.3f} to {max(lo):.3f}; at E1 strip edge: {min(hi):.3f} to {max(hi):.3f}")
# cross-check: face radius implied by the inner pin height (pad at y = ypin[1]) against ri, to prove the recess is 0 (band face = bore)
print("ypin", d["ypin"])
for n in range(7, 14):
    cx, ri = d["cx"][str(n)], d["ri"][str(n)]
    y = d["ypin"][1]
    xface = xb - d["pin_heights"][str(n)][1]
    s = cx - xface            # = r*cos(theta) ; r*sin(theta) = y
    r = math.hypot(s, y)
    print(f"US {n}: implied face radius {r:.4f} vs ri {ri:.4f} diff {r-ri:+.4f}")
