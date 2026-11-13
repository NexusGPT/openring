#!/usr/bin/env python3
"""Measures the wire runs of W1 to W7 and the cell leads and the thermistor from the two board files and the case model; writes evidence/wire_table.csv.
Run with KiCad's Python.  Path model (ours, stated in board-notes.md part f): from the pad on PCB2, straight down the free space below the pin holder to the floor slot,
through the slot, then in a straight line to the pad on PCB1; length = vertical run + horizontal run (taxicab) + 2 x 2.5 mm stripped and soldered end allowance."""
import csv, os, sys
import pcbnew
from pcbnew import ToMM
import geom
HERE = os.path.dirname(os.path.abspath(__file__))
CB = {"W1": 30, "W2": 30, "W3": 30, "W4": 30, "W7": 20, "W5": 40, "W6": 40}      # case-bom.csv lines 27, 59, 28
b1 = pcbnew.LoadBoard(os.path.join(HERE, "case_main.kicad_pcb"))
b2 = pcbnew.LoadBoard(os.path.join(HERE, "case_pins.kicad_pcb"))
f1 = {f.GetReference(): f for f in b1.GetFootprints()}
f2 = {f.GetReference(): f for f in b2.GetFootprints()}
rows = []
Z_PCB1_TOP = geom.PCB1_Z[1]
for w, wp in (("W1", "WP1"), ("W2", "WP2"), ("W3", "WP3"), ("W4", "WP4"), ("W7", "WP7")):
    p1 = f1[w].GetPosition(); p2 = f2[wp].GetPosition()
    u = ToMM(p1.x) - 100.0; d = ToMM(p1.y) - 100.0              # board frame of PCB1 (u right, d down)
    x_case = u + geom.PCB1_X0; y_case = -d
    # PCB2 pad: kx = 100 - y  ->  y = 100 - kx ; ky = 100 - dz  ->  dz = 100 - ky
    y2 = 100.0 - ToMM(p2.x); z2 = geom.Z_PIN + (100.0 - ToMM(p2.y))
    x2 = geom.X_B_INNER + 0.4 if abs(y2) < 2.3 else geom.X_BO + 0.4
    dz = z2 - Z_PCB1_TOP
    dh = abs(x_case - x2) + abs(y_case - y2)
    path = dz + dh
    rows.append([w, wp, "PCB2 pad %s (x %.2f y %.2f z %.2f case frame)" % (wp, x2, y2, z2), "PCB1 pad %s (x %.2f y %.2f z %.2f)" % (w, x_case, y_case, Z_PCB1_TOP),
                 f1[w].Pads()[0].GetNetname(), "%.1f" % path, "%.1f" % (path + 5.0), CB[w]])
for w, lead in (("W5", "red (+)"), ("W6", "black (-)")):
    p1 = f1[w].GetPosition()
    u = ToMM(p1.x) - 100.0; d = ToMM(p1.y) - 100.0
    x_case = u + geom.PCB1_X0; y_case = -d
    # cell lead leaves the PCM end of the cell; modelled cell: x_c0 .. x_c0+23 (case_params cell_x0), PCM end at the board edge side: lead exits at the cell top face, 0.3 mm below PCB1
    cell_x0 = -7.737067021407239
    lead_x = cell_x0 + (11.5 if w == "W5" else 12.5)
    lead_y = 20.0                                                # PCM end of the cell at y = +20 (case.py cell box y +-20)
    path = abs(x_case - lead_x) + abs(y_case - lead_y) + 0.3 + 1.0 + 8.5 * 0 + 2.0
    rows.append([w, "cell lead", "cell BT1 %s lead at the PCM end (x %.2f y %.2f)" % (lead, lead_x, lead_y), "PCB1 pad %s (x %.2f y %.2f)" % (w, x_case, y_case),
                 f1[w].Pads()[0].GetNetname(), "%.1f" % path, "%.1f" % (path + 5.0), CB[w]])
with open(os.path.join(HERE, "evidence", "wire_table.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["wire", "from", "pad_at_board2_or_cell", "pad_at_pcb1", "net", "path_mm", "path_plus_5mm_ends", "cut_length_mm_case_bom"])
    w.writerows(rows)
for r in rows:
    print(r)
