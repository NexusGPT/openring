"""Builder's depth-gauge numbers: for each pin, the free plunger tip's stand-out in front of the pin holder's front face along the pin axis
(ring out, pin free at 2.80 mm, maker drawing), from out/case_params.json and case.py's holder front rule. usage: python pin_gauge.py"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import case as C  # noqa: E402

P = json.load(open(os.path.join(C.OUT, "case_params.json")))
for k, p in enumerate(C.PL["pads"]):
    y = P["ypin"][k]
    xf = max(C.cx_of(n) - math.sqrt(C.pad_face_r(n) ** 2 - y * y) for n in C.SIZES) + C.HOLD_G     # holder front face at this y (case.py holder rule)
    xb = P["xb"][k]
    stand = C.PIN["free_h"] - (xb - xf)
    hs = [float(P["pin_heights"][str(n)][k]) for n in C.SIZES]
    print(f"P{k + 1} ({p['net']}): base plane x {xb:.3f}, holder face x {xf:.3f}: free tip stands {stand:.3f} mm in front of the holder face; "
          f"working heights {min(hs):.3f} to {max(hs):.3f}")
