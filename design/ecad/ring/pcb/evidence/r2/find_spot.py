# find_spot.py ref anchor_ref anchor_pin limit [avoid x0,y0,x1,y1 ...]: free places for one part of placement-final.csv
# (courtyards of the plan's geom.py and rules.py: no overlap, inside the outline, outside the keep-outs), its pad on the
# served net within `limit` of the anchor pin, its courtyard outside every avoid box; nearest first
import sys, csv, math
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/wiring/ring-board-plan-work"))
from geom import place
from rules import KEEPOUTS, overlap, inside, override_cy
T = (__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/ecad/ring/pcb/placement-final.csv")
NET = {(r['reference'], r['pin_number']): r['net'] for r in csv.DictReader(open((__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/ecad/ring/netlist.csv")))}
ref, aref, apin, lim = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
avoid = [tuple(map(float, a.split(','))) for a in sys.argv[5:]]
rows = list(csv.DictReader(open(T)))
P = {}
for r in rows:
    x, y, rot = float(r['x_mm']), float(r['y_mm']), int(r['rotation_deg'])
    cy, pads = place(r['footprint'], x, y, rot); P[r['reference']] = (r['side'], override_cy(r['reference'], cy, x, y, rot), pads, r)
me = P[ref][3]; net = NET[(aref, apin)]
ap = [p for p in P[aref][2] if p[0] == apin][0]
out = []
for i in range(-60, 61):
    for j in range(-60, 61):
        x, y = ap[1] + i * 0.05, ap[2] + j * 0.05
        for rot in (0, 90, 180, 270):
            cy, pads = place(me['footprint'], x, y, rot)
            mine = [p for p in pads if NET.get((ref, p[0])) == net]
            if not mine: continue
            d = min(math.dist((p[1], p[2]), (ap[1], ap[2])) for p in mine)
            if d > lim: continue
            if not inside(cy, ref): continue
            if any(overlap(cy, k['r']) for k in KEEPOUTS if ref not in k['allow']): continue
            if any(overlap(cy, a) for a in avoid): continue
            if any(s == 'F' and o != ref and overlap(cy, c) for o, (s, c, _, _) in P.items()): continue
            out.append((d, x, y, rot))
out.sort()
for o in out[:15]: print('%s at (%.3f, %.3f) rot %d: %.2f mm from %s.%s' % (ref, o[1], o[2], o[3], o[0], aref, apin))
print('places found', len(out))
