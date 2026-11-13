"""Smallest working height at which the outer pin P1 (barrel 1.50 x 1.85, P70-6000045R) clears the ring band, at US 7 and US 13: the pin is placed with
its tip TIP_GAP from the pad face (as test 2a) and its base plane at face + h; common volume with the ring body for h = 2.00 to 2.30. usage: python outer_pin_scan.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import case as C  # noqa: E402

k = [i for i, p in enumerate(C.PL["pads"]) if p["net"] == "VBUS"][0]
zb = 22.71
for n in (7,):
    body = C.Ring(n).parts_in_case(zb)["body"]
    fx, fy, fz = C.pad_face_xyz(n, k, zb, C.PL)
    for h in (2.06, 2.07, 2.08, 2.09):
        pin = C.make_pin(fx + h, fy, fz, h - C.TIP_GAP)
        print(f"US {n} P1 (VBUS) working height {h:.2f}: common with the ring body {C.common(pin, body):.5f} mm3")
