import json, sys
_a = sys.argv[1:]
sys.argv = [sys.argv[0]]
import place_pcb1 as P
seed = _a[0] if _a else "24"
pl = json.load(open(P.os.path.join(P.HERE, "work", "placement_pcb1_s%s.json" % seed)))
for r, (u, d, rot, side) in pl.items():
    it = P.items[r]; it.u, it.d, it.rot = u, d, rot
P.total_cost()
bad = []
rl = list(P.items)
for i, a in enumerate(rl):
    ca = P._courts[a]
    o = (P.outside_pen(ca) + P.pad_outside_pen(a)) if a not in ("J1", "U1") else 0
    if o > 0: bad.append(("outside", a, round(o, 3)))
    if P.items[a].side == "F" and a != "U1" and P.overlap_area(ca, P.ANT) > 0: bad.append(("antenna", a))
    for b in rl[i + 1:]:
        pp = P.pair_pen(a, b) / 400
        if pp > 0: bad.append(("overlap", a, b, round(pp, 3)))
for x in bad: print(x)
print("total", len(bad))
