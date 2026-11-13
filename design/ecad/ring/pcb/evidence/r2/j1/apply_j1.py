# apply_j1.py: lead's message (owner's decision, layout C of screen-cable-study.md 4.3): J1 to the screen face at (-4.933, -0.003),
# rotation 270 (contact-1 row, the FPC entry, toward +X: j1_rot.log); test pads whose courtyard meets J1's move to free places on
# the screen face between X -3.2 and +13.5 (net and number kept). Writes placement-final.csv.
import sys, csv
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[7].as_posix() + "/design/wiring/ring-board-plan-work"))
from geom import place
from rules import overlap, inside, override_cy, KEEPOUTS
T = (__import__("pathlib").Path(__file__).resolve().parents[7].as_posix() + "/design/ecad/ring/pcb/placement-final.csv")
rows = list(csv.DictReader(open(T))); hdr = list(rows[0].keys())
R = {r['reference']: r for r in rows}
j = R['J1']; print('J1 (%s, %s, %s, %s) -> (-4.933, -0.003, 270, B)' % (j['x_mm'], j['y_mm'], j['rotation_deg'], j['side']))
j.update(x_mm='-4.933', y_mm='-0.003', rotation_deg='270', side='B', zone='Z13 screen face (layout C)', kicad_x='95.067', kicad_y='99.997')
def cy(r):
    x, y, rot = float(r['x_mm']), float(r['y_mm']), int(r['rotation_deg'])
    c, _ = place(r['footprint'], x, y, rot); return override_cy(r['reference'], c, x, y, rot)
jc = cy(j)
print('J1 courtyard (geom.py, as check_placement measures it) X %.3f..%.3f Y %.3f..%.3f' % (jc[0], jc[2], jc[1], jc[3]))
tps = [r for r in rows if r['reference'].startswith('TP')]
move = [r for r in tps if overlap(cy(r), jc)]
stay = [r for r in tps if r not in move]
print('test pads under J1: %d %s; staying: %s' % (len(move), ' '.join(r['reference'] for r in move), ' '.join(r['reference'] for r in stay)))
cand = [(x, y) for x in (-2.65, -1.60, -0.55) for y in (-2.10, -1.05, 0.0, 1.05, 2.10)] + [(0.50, -2.10), (0.50, -3.15), (-0.55, -3.15)]
taken = [cy(r) for r in stay] + [jc]
for r in move:
    for (x, y) in cand:
        c, _ = place(r['footprint'], x, y, 0)
        if not inside(c, r['reference']) or any(overlap(c, t) for t in taken) or any(overlap(c, k['r']) for k in KEEPOUTS if k['name'] == 'antenna'):
            continue
        if not (-3.2 <= c[0] and c[2] <= 13.5): continue
        print('move %s (%s, %s) -> (%.3f, %.3f)' % (r['reference'], r['x_mm'], r['y_mm'], x, y))
        r.update(x_mm='%.3f' % x, y_mm='%.3f' % y, rotation_deg='0', kicad_x='%.3f' % (x + 100), kicad_y='%.3f' % (y + 100))
        taken.append(c); cand.remove((x, y)); break
    else:
        raise SystemExit('no place for %s' % r['reference'])
w = csv.DictWriter(open(T, 'w', newline=''), hdr); w.writeheader(); w.writerows(rows); print('written', T)
