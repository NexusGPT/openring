"""Debug run (not the proof): with the pins at 2.05: every pin at its working compression per size against the ring body, glass, joystick (as test 2a),
and pins, islands, holder, post against each other. usage: CASE_OUT=<folder> python quick_pins.py"""
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import case as C  # noqa: E402
from build123d import import_step  # noqa: E402

prm = json.load(open(os.path.join(C.OUT, "case_params.json")))
names = sorted(prm["pin_nets"]) + ["pin_holder", "post", "pin_board_pcb2", "pin_board_pcb2_wing_L", "pin_board_pcb2_wing_R", "liner", "shell"]
parts = {n: import_step(os.path.join(C.OUT, "parts", f"{n}.step")) for n in names}
k_of = {p["net"]: k for k, p in enumerate(C.PL["pads"])}
worst = 0.0
for n in prm["sizes"]:
    rc = C.Ring(n).parts_in_case(prm["zb"])
    for pn in sorted(prm["pin_nets"]):
        fx, fy, fz = C.pad_face_xyz(n, k_of[prm["pin_nets"][pn]], prm["zb"], C.PL)
        b = parts[pn].bounding_box()
        pin = C.make_pin(b.max.X, (b.min.Y + b.max.Y) / 2, (b.min.Z + b.max.Z) / 2, b.max.X - fx - C.TIP_GAP)
        for k in ("body", "glass", "joystick"):
            v = C.common(pin, rc[k])
            worst = max(worst, v)
            if v > 0.001:
                print(f"US {n} {pn} x ring {k}: {v:.4f} mm3")
    d = min(parts[k].distance_to(rc["body"]) for k in ("post", "pin_board_pcb2", "pin_board_pcb2_wing_L", "pin_board_pcb2_wing_R", "pin_holder"))
    print(f"US {n}: largest pin x ring common so far {worst:.6f} mm3; holder/post/islands to ring body {d:.3f} mm")
bad = 0
for a, b in itertools.combinations(names, 2):
    v = C.common(parts[a], parts[b])
    if v > 0.001:
        bad += 1
        print(f"INTERSECT {a} x {b}: {v:.4f}")
print(f"quick_pins: pin x ring largest {worst:.6f} mm3; part pairs intersecting {bad}")
