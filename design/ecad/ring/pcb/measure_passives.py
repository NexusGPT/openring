#!/usr/bin/env python3
"""Measures the land pads of the chip parts C1, C4, R1, L1, FB1, X1, X2 on Nordic's own reference layout
(design/datasheets/nrf54lm20x_caaa_ref_pcb_0_2.pdf page 1, scale 12:1; reference designators from page 12) and prints
them next to the sizes of KiCad's library footprints.  Output: w1-evidence/passive-pads-measured.csv.
Run: design/.venv/bin/python -I measure_passives.py"""
import csv, math, os, warnings
warnings.filterwarnings('ignore')
import fitz
HERE = os.path.dirname(os.path.abspath(__file__))
doc = fitz.open(os.path.join(HERE, '../../../datasheets/nrf54lm20x_caaa_ref_pcb_0_2.pdf'))
S = 12 * 72 / 25.4
labels = {w[4]: ((w[0] + w[2]) / 2, (w[1] + w[3]) / 2) for w in doc[11].get_text('words')}
pads = []
for d in doc[0].get_drawings():
    if d['type'] == 'f' and 4 <= len(d['items']) <= 12:
        r = d['rect']
        if r.width / S < 2.6 and r.height / S < 2.6 and r.width > 5:
            pads.append((r.x0 + r.width / 2, r.y0 + r.height / 2, r.width / S, r.height / S))
rows = [['ref', 'size_class', 'pad_w_mm', 'pad_h_mm', 'centre_distance_mm', 'orientation', 'kicad_footprint', 'kicad_pad_w', 'kicad_pad_h', 'kicad_centre_distance']]
KICAD = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints'
import re
def kicad_pads(lib, name):
    t = open(os.path.join(KICAD, lib + '.pretty', name + '.kicad_mod')).read()
    out = []
    for m in re.finditer(r'\(pad "([12])" smd \w+\s+\(at ([-0-9.]+) ([-0-9.]+)\)\s+\(size ([0-9.]+) ([0-9.]+)\)', t):
        out.append((m.group(1), float(m.group(2)), float(m.group(4)), float(m.group(5))))
    assert len(out) == 2, (name, out)
    return name, out[0][2], out[0][3], round(abs(out[0][1] - out[1][1]), 3)   # file: pad 1 size across x, y (pads lie along x), centre distance
KI = {'C1': kicad_pads('Capacitor_SMD', 'C_0201_0603Metric'), 'C4': kicad_pads('Capacitor_SMD', 'C_0402_1005Metric'),
      'R1': kicad_pads('Resistor_SMD', 'R_0603_1608Metric'), 'L1': kicad_pads('Inductor_SMD', 'L_0603_1608Metric')}
for ref, cls in (('C1', '0201'), ('FB1', '0201'), ('R2', '0201'), ('C4', '0402'), ('C11', '0402'), ('R1', '0603'), ('L1', '0603(1608)'), ('X1', '2016'), ('X2', '2012')):
    lx, ly = labels[ref]
    near = sorted(pads, key=lambda q: math.hypot(q[0] - lx, q[1] - ly))[:2]
    a, b = near
    dist = math.hypot(a[0] - b[0], a[1] - b[1]) / S
    ori = 'vertical pair' if abs(a[0] - b[0]) < abs(a[1] - b[1]) else 'horizontal pair'
    k = KI.get(ref, ('', '', '', ''))
    rows.append([ref, cls, '%.3f' % a[2], '%.3f' % a[3], '%.3f' % dist, ori] + list(k))
with open(os.path.join(HERE, 'w1-evidence', 'passive-pads-measured.csv'), 'w', newline='') as f:
    csv.writer(f).writerows(rows)
for r in rows: print(','.join(str(x) for x in r))
