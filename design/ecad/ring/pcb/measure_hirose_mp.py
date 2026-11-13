#!/usr/bin/env python3
"""Reads the vector drawing of w1_hirose_fh35c-15s-0.3shw50_drawing.pdf page 1 (recommended PCB mounting pattern, 10:1) and prints the
mounting-pad rectangles against the lower contact row, in mm, to check the numbers used in make_footprints.py (J1 'MP' pads:
0.4 wide x 0.95 long, centre 0.7 beyond the end pad centre, bottom edge 0.2 above the lower row pad bottom).
Run: design/.venv/bin/python -I measure_hirose_mp.py"""
import os, warnings
warnings.filterwarnings('ignore')
import fitz
HERE = os.path.dirname(os.path.abspath(__file__))
doc = fitz.open(os.path.join(HERE, '../../../datasheets/w1_hirose_fh35c-15s-0.3shw50_drawing.pdf'))
K = 72 / 25.4 * 10          # points per mm at 10:1
rects = []
for d in doc[0].get_drawings():
    r = d['rect']
    if 8 < r.width < 40 and 8 < r.height < 60 and 520 < r.x0 and 180 < r.y0 < 420:
        rects.append((r.x0, r.y0, r.width, r.height))
mp = [r for r in rects if abs(r[2] / K - 0.4) < 0.02 and abs(r[3] / K - 0.95) < 0.03]
pads = [r for r in rects if abs(r[2] / K - 0.3) < 0.02 and abs(r[3] / K - 0.8) < 0.03]
print('mounting pads found:', len(mp), ' lower-row pads found (0.3 x 0.8):', len(pads))
print('lower-row pad centres (mm from the drawing origin):', ' '.join('%.2f' % ((p[0] + p[2] / 2) / K) for p in sorted(pads)))
print('MP centres:', ' '.join('%.2f' % ((m[0] + m[2] / 2) / K) for m in sorted(mp)))
for m in mp:
    cx = m[0] + m[2] / 2
    nearest = min(pads, key=lambda p: abs((p[0] + p[2] / 2) - cx))
    d = abs(cx - (nearest[0] + nearest[2] / 2)) / K
    bottom_gap = ((nearest[1] + nearest[3]) - (m[1] + m[3])) / K
    print('MP %.3f x %.3f mm, centre %.3f mm from the nearest drawn lower-row pad centre, bottom edge %.3f mm above the pad bottom' % (m[2] / K, m[3] / K, d, bottom_gap))
    print('  the pad row has 0.6 pitch: the end pad lies %.3f mm from the MP centre if the nearest drawn pad is 2 pitches inside (the drawing breaks the row in the middle and the end pads are drawn as other shapes)' % (d - 1.2))
