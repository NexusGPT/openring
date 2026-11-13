"""What follows the board's 0.505 mm move (lead's ruling): (1) the status light LED1 (body from the board's STEP) against its light window in the shell;
(2) the wall the touch electrode E1 reads through; (3) the lead lengths and the cell to board gap. Before (C5d, out of 2026-11-11, params copy
r4/case_params_before_r4.json) and after (the given build). usage: follow_board.py <out folder>"""
import json
import os
import sys

from build123d import import_step

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1]
P = json.load(open(os.path.join(OUT, "case_params.json")))
B = json.load(open(os.path.join(HERE, "case_params_before_r4.json")))
mb = import_step(os.path.join(OUT, "parts", "main_board.step"))
led = [c for c in mb.children if c.label == "LED1"][0].bounding_box()
win = import_step(os.path.join(OUT, "parts", "light_window.step")).bounding_box()
wy, wz = (win.min.Y + win.max.Y) / 2, (win.min.Z + win.max.Z) / 2
ly, lz = (led.min.Y + led.max.Y) / 2, (led.min.Z + led.max.Z) / 2
print(f"(1) LED1 body (board STEP): x {led.min.X:.3f} to {led.max.X:.3f}, y {led.min.Y:.3f} to {led.max.Y:.3f}, z {led.min.Z:.3f} to {led.max.Z:.3f}")
print(f"    light window (shell part, dia {win.size.Y:.2f}): x {win.min.X:.3f} to {win.max.X:.3f}, axis y {wy:.3f} z {wz:.3f}")
print(f"    window axis to LED centre: y {wy - ly:+.3f} mm, z {wz - lz:+.3f} mm (axis inside the LED's y and z span: "
      f"{led.min.Y <= wy <= led.max.Y and led.min.Z <= wz <= led.max.Z}); air gap window end to LED's -X face {led.min.X - win.max.X:.3f} mm")
bl = B["pcb1_x0"] + 0.6
print(f"    C5d (reserved box): LED x {bl:.3f} to {bl + 1.6:.3f}, y 5.2 to 6.8, z {B['pcb1_z'][1]:.3f} to {B['pcb1_z'][1] + 0.7:.3f}; window end x {B['pcb1_x0'] - 0.1:.3f}: gap {bl - (B['pcb1_x0'] - 0.1):.3f} mm")
h0, h1 = B["pin_holder"], P["pin_holder"]
print(f"(2) E1 reads through the holder's front wall: {h1['wall_in_front_of_E1']:.4f} mm now, {h0['wall_in_front_of_E1']:.4f} mm in C5d "
      f"(PCB2 did not move: x_b {P['x_b']:.4f} / {B['x_b']:.4f}); E1 front strip on the island's front face at z {P['z_pin'] + 1.70:.2f} (board file ky 98.3), "
      f"the wire recess ends at z {P['holder_recess']['z_top']:.2f}, below E1")
print("(3) leads (path from the model; cut = path + 5 mm):")
for k, v in sorted(P["leads"].items()):
    print(f"    {k}: path {v['length']:.1f} mm, cut {v['length'] + 5:.1f} mm, diameter {v['d']:.2f}")
print(f"    board back z {P['pcb1_z'][0]:.3f}; cell top z {P['zp'] + 0.4 + 8.5:.3f}: gap {P['pcb1_z'][0] - P['zp'] - 0.4 - 8.5:.3f} mm (insulating sheet model {P['stack']['sheet']:.3f} mm in it)")
print(f"    board x {P['pcb1_x0']:.3f} to {P['pcb1_x0'] + 23.0:.3f} over the cell x {P['cell_x0']:.3f} to {P['cell_x0'] + 23.0:.3f} (C5d board x {B['pcb1_x0']:.3f})")
