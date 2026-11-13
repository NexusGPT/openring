#!/usr/bin/env python3
"""Measures the 61 land centres of U1 (nRF54LM20A-CAAA, WLCSP-61) from Nordic's own reference layout
(design/datasheets/nrf54lm20x_caaa_ref_pcb_0_2.pdf, page 1 'Top Side (Scale 12:1)' for the pads and
page 11 'Assembly Top' for the 3.020 x 2.430 body outline), and maps the ball names of Nordic's reference schematic
(design/parts/nrf54lm20a-csp61-pins.csv, from nrf54lm20x_caaa_ref_schematic_0_2.pdf page 1) onto them.
Output: pcb/w1-evidence/u1-measured-pads.csv (ball, x_mm, y_mm), centred on the body, +x right, +y down (top view).
Run with the project's python: design/.venv/bin/python -I measure_u1.py"""
import csv, os, sys, warnings
warnings.filterwarnings('ignore')
import fitz
HERE = os.path.dirname(os.path.abspath(__file__))
DS = os.path.join(HERE, '../../../datasheets')
doc = fitz.open(os.path.join(DS, 'nrf54lm20x_caaa_ref_pcb_0_2.pdf'))
S = 12 * 72 / 25.4                      # points per mm at scale 12:1
# body outline from page 11 (assembly): the 3.020 x 2.430 rectangle round U1
body = None
for d in doc[10].get_drawings():
    r = d['rect']
    if abs(r.width / S - 3.02) < 0.01 or abs(r.height / S - 2.43) < 0.01:
        pass
# the closed body outline is drawn on page 12 as one 4-line path; page 11 holds its two long edges
for d in doc[11].get_drawings():
    r = d['rect']
    if abs(r.width / S - 3.020) < 0.002 and abs(r.height / S - 2.430) < 0.002:
        body = r; break
if body is None:
    sys.exit('body outline 3.020 x 2.430 not found')
cx, cy = (body.x0 + body.x1) / 2, (body.y0 + body.y1) / 2
pts = set()
for d in doc[0].get_drawings():
    if d['type'] == 's' and abs((d.get('width') or 0) - 0.2 * S) < 0.01 and d['rect'].width == 0 and d['rect'].height == 0:
        col = tuple(round(v, 2) for v in d['color'])
        if col != (0.93, 0.18, 0.31): continue
        p = d['items'][0][1]
        if body.x0 < p.x < body.x1 and body.y0 < p.y < body.y1:
            pts.add((round(p.x, 1), round(p.y, 1)))
pts = sorted(pts)
print('pad centres inside the body outline:', len(pts))
P = 0.325
x0 = min(p[0] for p in pts); y0 = min(p[1] for p in pts)
grid = {}; off = []
for (x, y) in pts:
    i = (x - x0) / (P * S); j = (y - y0) / (P * S)
    if abs(i - round(i)) < 0.08 and abs(j - round(j)) < 0.08:
        grid[(round(j), round(i))] = (x, y)
    else:
        off.append((x, y))
print('on the 0.325 grid:', len(grid), ' off the grid:', len(off))
rows = 'ABDEFGH'; cols = [1, 2, 4, 5, 6, 7, 8, 9, 10]
names = {r['ball']: r['pin_name_as_printed'] for r in csv.DictReader(open(os.path.join(HERE, '../../../parts/nrf54lm20a-csp61-pins.csv')))}
out = {}
for (j, i), (x, y) in grid.items():
    out['%s%d' % (rows[j], cols[i])] = (x, y)
# the two balls off the grid carry the names C1 (ANT) and D3 (VSS): C1 lies between rows B and D, D3 between columns 2 and 4
for (x, y) in off:
    i = (x - x0) / (P * S); j = (y - y0) / (P * S)
    if abs(i - 0) < 0.1 and 1.5 < j < 2.0: out['C1'] = (x, y)
    elif 1.0 < i < 1.5 and abs(j - 2) < 0.1: out['D3'] = (x, y)
    else: sys.exit('unexpected off-grid pad %s' % ((x, y),))
missing = sorted(set(names) - set(out)); extra = sorted(set(out) - set(names))
print('names without a pad:', missing, ' pads without a name:', extra)
if missing or extra or len(out) != 61:
    sys.exit('MAPPING FAIL')
# orientation proof: only one of the four ways to lay the name grid on the measured pads fits all 61 sites
sites = set(out.values())
occ_names = {(rows.index(b[0]) if b[0] in rows else None, int(b[1:])) for b in names if b[0] in rows}
pad_rc = set(grid.keys())   # (row, column) of the 59 pads on the 0.325 grid
grid_names = {(rows.index(b[0]), cols.index(int(b[1:]))) for b in names if b[0] in rows and int(b[1:]) in cols}
ok = []
for nm, f in (('A1 top left (used)', lambda j, i: (j, i)), ('mirrored left-right', lambda j, i: (j, 8 - i)),
              ('mirrored top-bottom', lambda j, i: (6 - j, i)), ('rotated 180', lambda j, i: (6 - j, 8 - i))):
    mapped = {f(j, i) for (j, i) in grid_names}
    on_grid = {rc for rc in pad_rc if rc in {(j, i) for j in range(7) for i in range(9)}}
    ok.append((nm, len(mapped & on_grid), len(mapped), len(on_grid)))
for nm, hit, nn, npad in ok:
    print('orientation test %-22s names %d on grid, pads %d on grid, coincide %d' % (nm, nn, npad, hit))
best = [nm for nm, hit, nn, npad in ok if hit == nn == npad]
print('orientations that fit every name on a pad:', best)
if best != ['A1 top left (used)']:
    sys.exit('ORIENTATION NOT UNIQUE: %s' % best)
os.makedirs(os.path.join(HERE, 'w1-evidence'), exist_ok=True)
with open(os.path.join(HERE, 'w1-evidence', 'u1-measured-pads.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['ball', 'x_mm', 'y_mm'])
    for b in sorted(out, key=lambda b: (b[0], int(b[1:]))):
        x, y = out[b]; w.writerow([b, '%.3f' % ((x - cx) / S), '%.3f' % ((y - cy) / S)])
print('RESULT PASS: 61 names matched 61 pads (59 on the 0.325 grid, C1 and D3 off it)')
