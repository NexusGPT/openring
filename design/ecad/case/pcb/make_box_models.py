#!/usr/bin/env python3
"""Writes the simple 3D models of pcb/models/ (STEP boxes and one cylinder, bottom face on the board, centred on the footprint origin). Run with the project python:
design/.venv/bin/python make_box_models.py.  Sizes (maker documents): ESP32-S3-MINI-1 15.4 x 20.5 x 2.4 (case_esp32s3_mini1.pdf p.42); XFL4020 4.0 x 4.0 x 2.1 and XFL4015 4.0 x 4.0 x 1.6
(w5_coilcraft_xfl4020.pdf p.3, w5_coilcraft_xfl4015.pdf p.2); TPS63802 DLA 2.0 x 3.0 x 1.0 (case_tps63802.pdf p.35); ZDSD LGA 10.0 x 9.0 x 0.95 (sdnand_zetta_family_atta.pdf p.15);
TPD4E05U06 DQA 1.0 x 2.5 x 0.55 (case_tpd4e05u06.pdf p.28); APTF1616 1.6 x 1.6 x 0.7 (case_kb_aptf1616.pdf p.1); Harwin P70 barrel dia 1.5, free height 2.8 (p3_harwin_p70_chipdip.pdf p.1)."""
import os
from build123d import Box, Cylinder, Align, export_step
H = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
C, M = Align.CENTER, Align.MIN
for name, (x, y, z) in {"box_esp32s3_mini1": (15.4, 20.5, 2.4), "box_xfl4020": (4.0, 4.0, 2.1), "box_xfl4015": (4.0, 4.0, 1.6), "box_dfn10": (2.0, 3.0, 1.0),
                        "box_lga16": (10.0, 9.0, 0.95), "box_uson10": (1.0, 2.5, 0.55), "box_led1616": (1.6, 1.6, 0.7)}.items():
    export_step(Box(x, y, z, align=(C, C, M)), os.path.join(H, name + ".step"))
export_step(Cylinder(0.75, 2.8, align=(C, C, M)), os.path.join(H, "cyl_harwin.step"))
print("written", sorted(os.listdir(H)))
