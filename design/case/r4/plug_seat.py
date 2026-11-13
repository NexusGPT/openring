"""Does a USB-C plug seat fully? GCT USB4105 drawing (design/datasheets/case_usb4105.pdf p.1, "Plug and Receptacle Mating View"): mated, the plug's
overmold face is at least 1.85 mm in front of the receptacle front ("1.85 Min"); the overmold is at most 6.5 mm high ("6.5 Max"). The overmold cannot
enter the case's mouth slot (4.51 mm high), so it stops on the outermost skin in front of it. Seats fully when (socket front x) - (smallest skin x over
the overmold's face) <= 1.85. The overmold width is not in the drawing: computed for 8.34 mm (the receptacle's own opening, the smallest a plug can be)
and 12.35 mm (a common overmold width; my value, no saved source). usage: plug_seat.py <case_params.json>"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import case as C  # noqa: E402

prm = json.load(open(sys.argv[1]))
C.PB.PEB.update(prm["pebble"])
H = prm["h_tot"]
z1 = prm["pcb1_z"][1]
zj = z1 + 3.31 / 2
yc = C.J1_YC
front = prm["boards"]["j1_body_front_u"] + prm["pcb1_x0"]
print(f"socket body front x {front:.4f} (board STEP), model j1_front {prm['j1_front']:.4f}, skin at the socket's outermost corner {prm['skin_x_at_j1']:.4f}: "
      f"front to skin {front - prm['skin_x_at_j1']:.4f} mm behind")
for w in (8.34, 12.35):
    xs = [C.skin_x_left(y, z, H) for y in np.linspace(yc - w / 2, yc + w / 2, 41) for z in np.linspace(zj - 3.25, zj + 3.25, 27)]
    xs = [x for x in xs if x is not None]
    xmin = min(xs)
    gap = front - xmin
    print(f"overmold {w:.2f} x 6.50 mm centred on the socket: outermost skin x {xmin:.4f}; overmold face {gap:.3f} mm in front of the socket front "
          f"(drawing allows 1.85 at least): {'seats fully' if gap <= 1.85 else 'does NOT seat fully'}")
