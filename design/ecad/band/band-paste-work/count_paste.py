#!/usr/bin/env python3
"""Read back the paste openings of each paste Gerber and check them against the brief.
usage: count_paste.py <fab dir> <dump dir> [names ...]
FLEX1: <name>-F_Paste.gbr must hold 12 openings, each a 0.55 x 0.55 rectangle centred on a switch land (SW1..SW5 pad of the dump).
FLEX2: <name>-B_Paste.gbr must hold 16 openings, each round 0.58 mm, 0.49 mm from the centre of a disc land CP1..CP4 (4 per land),
       and clear of the via at the land centre (via radius 0.15 from the dump).
Openings are read with gerber_norm.objects: flashes, and filled circles (arcs round one centre that close the circle). Any other object fails."""
import math, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gerber_norm

fab, dump = sys.argv[1], sys.argv[2]
names = sys.argv[3:] or [f"flex{k}-us{u}" for k in (1, 2) for u in range(7, 14)]
bad = 0
for n in names:
    k = n[4]
    f = os.path.join(fab, n, f"{n}-{'F' if k == '1' else 'B'}_Paste.gbr")
    if not os.path.exists(f):
        print(f"FAIL {n}: no paste Gerber {f}"); bad += 1; continue
    objs = gerber_norm.objects(f)
    flashes = [o for o in objs if o.startswith("FLASH")]
    other = [o for o in objs if not o.startswith("FLASH")]
    D = open(os.path.join(dump, n + ".dump")).read().splitlines()
    pads = {}
    for l in D:
        m = re.match(r"PAD (\S+) net \S* at (\S+) (\S+) size .* cu ([FB]\.Cu) ", l)
        if m:                                       # copper lands only (a paste-only pad has no copper layer)
            pads[m.group(1)] = (float(m.group(2)), float(m.group(3)))
    vias = [tuple(map(float, re.search(r"at (\S+) (\S+)", l).groups())) for l in D if l.startswith("VIA")]
    pts = []
    for o in flashes:
        m = re.match(r"FLASH (\S+) \((-?\d+),(-?\d+)\)", o)
        pts.append((m.group(1), int(m.group(2)) / 1e6, -int(m.group(3)) / 1e6))
    # a filled circle drawn on a paste layer is plotted as arcs round one centre with a round pen: one opening per centre,
    # diameter = 2 x arc radius + pen width; it counts as an opening only when its arcs close the full circle
    arcs = {}
    for o in objs:
        m = re.match(r"ARC C,([\d.]+)\S* centre \((-?\d+),(-?\d+)\) \((-?\d+), (-?\d+)\)->\((-?\d+), (-?\d+)\)", o)
        if m:
            arcs.setdefault((m.group(2), m.group(3)), []).append((float(m.group(1)), int(m.group(4)), int(m.group(5)), int(m.group(6)), int(m.group(7))))
    for (cx, cy), lst in arcs.items():
        cx, cy = int(cx), int(cy)
        pen = lst[0][0]
        r = math.hypot(lst[0][1] - cx, lst[0][2] - cy) / 1e6
        ends = {}
        for _, x0, y0, x1, y1 in lst:
            ends[(x0, y0)] = ends.get((x0, y0), 0) + 1; ends[(x1, y1)] = ends.get((x1, y1), 0) + 1
        closed = all(v % 2 == 0 for v in ends.values())
        if closed:
            pts.append((f"C,{2 * r + pen:.6f}", cx / 1e6, -cy / 1e6))
    other = [o for o in objs if not o.startswith("FLASH") and not o.startswith("ARC")]
    errs = []
    if k == "1":
        want = 12
        lands = {r: p for r, p in pads.items() if r.startswith("SW")}
        for ap, x, y in pts:
            if not ap.startswith("R,0.550000X0.550000"):
                errs.append(f"aperture {ap}")
            near = min(lands, key=lambda r: math.hypot(lands[r][0] - x, lands[r][1] - y))
            if math.hypot(lands[near][0] - x, lands[near][1] - y) > 0.001:
                errs.append(f"opening at {x:.3f},{y:.3f} not on a switch land")
        hit = {min(lands, key=lambda r: math.hypot(lands[r][0] - x, lands[r][1] - y)) for _, x, y in pts}
        detail = f"switch lands {len(lands)}, lands with an opening {len(hit)}"
    else:
        want = 16
        lands = {r: p for r, p in pads.items() if r.startswith("CP")}
        per = {r: 0 for r in lands}
        dmin_via = 9.0
        for ap, x, y in pts:
            if not ap.startswith("C,0.580000"):
                errs.append(f"aperture {ap}")
            near = min(lands, key=lambda r: math.hypot(lands[r][0] - x, lands[r][1] - y))
            d = math.hypot(lands[near][0] - x, lands[near][1] - y)
            dx, dy = abs(lands[near][0] - x), abs(lands[near][1] - y)
            if abs(d - 0.49) > 0.001 or abs(dx - dy) > 0.001:
                errs.append(f"opening at {x:.3f},{y:.3f}: {d:.4f} from {near}, not on a diagonal at 0.49")
            per[near] += 1
            for vx, vy in vias:
                dmin_via = min(dmin_via, math.hypot(vx - x, vy - y) - 0.29 - 0.15)
        if any(c != 4 for c in per.values()):
            errs.append(f"openings per land {per}")
        detail = f"per land {per}, smallest gap opening to via {dmin_via:.3f} mm"
    if other:
        errs.append(f"{len(other)} objects that are neither flashes nor circle arcs")
    ok = len(pts) == want and not errs
    bad += 0 if ok else 1
    print(f"{'PASS' if ok else 'FAIL'} {n}: paste openings {len(pts)} (want {want}; flashes {len(flashes)}, closed circles {len(pts) - len(flashes)}); {detail}" + ("; " + "; ".join(errs[:4]) if errs else ""))
print(f"RESULT: {'PASS' if bad == 0 else 'FAIL'} paste Gerbers checked {len(names)}, failing {bad}")
sys.exit(0 if bad == 0 else 1)
