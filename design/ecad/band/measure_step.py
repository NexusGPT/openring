"""Measure the path length of every delivered flex-tail STEP file (design/mfg/parts/flex-tail-*/), model v8: the files hold the fold and the foot already.
FLEX1 files have 6 solids (neck, fold, foot, trunk, head, bend), FLEX2 files 5 (neck, fold, foot, trunk, strip).  Thickness 0.11 at neck, fold, foot and head
(from the file), 0.15 (the embedded allowance, thin.py flex_t) at trunk and strip.  Length of a solid = volume / (width x thickness); the bend is the distance
between the mid points of its two end faces.  Writes model_lengths.csv (path_total includes the fold and foot: do NOT add FOOT_EXTRA again).
Run: design/.venv/bin/python -I measure_step.py <out.csv>.  Adapted from design/mech/thin/out/v8/measure_step_v8.py."""
import sys, csv, math
from build123d import import_step

sys.dont_write_bytecode = True
ROOT = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/mfg/parts")
T_EMB = 0.15


def bend_midline(sol):
    pts = []
    for v in sol.vertices():
        p = (round(v.Y, 5), round(v.Z, 5))
        if p not in pts:
            pts.append(p)
    assert len(pts) == 4, pts
    pairs = sorted(((math.dist(pts[i], pts[j]), i, j) for i in range(4) for j in range(i + 1, 4)))
    (d1, a, b) = pairs[0]
    for d2, c, d in pairs[1:]:
        if len({a, b, c, d}) == 4:
            m1 = ((pts[a][0] + pts[b][0]) / 2, (pts[a][1] + pts[b][1]) / 2)
            m2 = ((pts[c][0] + pts[d][0]) / 2, (pts[c][1] + pts[d][1]) / 2)
            return math.dist(m1, m2)
    raise RuntimeError("no end faces")


def width(s):
    b = s.bounding_box()
    return b.max.X - b.min.X


rows = []
for us in range(7, 14):
    for tail, key in (("FLEX1", "thumb"), ("FLEX2", "away")):
        sol = import_step(f"{ROOT}/flex-tail-{key}/flex-tail-{key}-us{us}.step").solids()
        assert len(sol) == (6 if tail == "FLEX1" else 5), (tail, us, len(sol))
        nb = sol[0].bounding_box()
        neck = nb.max.Z - nb.min.Z
        t_fin = min(nb.max.Y - nb.min.Y, 0.2)
        fold = sol[1].volume / (t_fin * (width(sol[0]) + width(sol[2])) / 2)
        foot = sol[2].volume / (width(sol[2]) * t_fin)
        trunk = sol[3].volume / (width(sol[3]) * T_EMB)
        if tail == "FLEX1":
            head = sol[4].volume / (width(sol[4]) * t_fin)
            bend = bend_midline(sol[5])
            total = neck + fold + foot + trunk + bend + head
            rows.append([tail, us, round(neck, 4), round(fold, 4), round(foot, 4), round(trunk, 4), round(bend, 4), round(head, 4), round(total, 4)])
        else:
            strip = sol[4].volume / (width(sol[4]) * T_EMB)
            total = neck + fold + foot + trunk + strip
            rows.append([tail, us, round(neck, 4), round(fold, 4), round(foot, 4), round(trunk, 4), "", round(strip, 4), round(total, 4)])
with open(sys.argv[1], "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["tail", "us", "neck", "fold", "foot", "trunk", "bend", "head_or_strip", "path_total"])
    w.writerows(rows)
print("rows", len(rows))
