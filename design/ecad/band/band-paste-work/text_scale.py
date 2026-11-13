#!/usr/bin/env python3
"""Scale of each drawing and the paper height of the land label text.
The legend lines 'LAND n = ...' are 0.5 mm apart on the board (build_band.py board_end_detail); their pitch on the PDF page
(pdftotext -bbox, points) gives the scale; paper text height = scale x board text height (0.3 mm legend and nets, 0.6 mm land numbers).
usage: text_scale.py <fab dir> <out dir>"""
import os, re, subprocess, sys

fab, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
PT = 25.4 / 72
for k in (1, 2):
    for u in range(7, 14):
        n = f"flex{k}-us{u}"
        h = os.path.join(out, n + ".html")
        subprocess.run(["pdftotext", "-bbox", os.path.join(fab, n + "-drawing.pdf"), h], check=True)
        words = re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', open(h).read())
        land = sorted(float(w[1]) for w in words if w[4] == "LAND")
        pitch = [b - a for a, b in zip(land, land[1:])]
        p = sorted(pitch)[len(pitch) // 2] * PT        # median pitch on paper, mm
        scale = p / 0.5
        print(f"{n}: LAND lines {len(land)}, pitch on paper {p:.3f} mm, scale {scale:.2f} : 1, "
              f"text 0.3 mm -> {0.3 * scale:.2f} mm on paper, land numbers 0.6 mm -> {0.6 * scale:.2f} mm")
