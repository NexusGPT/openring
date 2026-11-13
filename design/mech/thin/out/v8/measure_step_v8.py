"""v8: path length (centre line) of every delivered flex-tail STEP file, measured on the file (solid volumes, end faces), per ring size, against the flat length of the
drawn board (design/ecad/band/band_geom.py Size.len1 / len2, the numbers check_band.py compares each outline with, and v7 path + FOOT_EXTRA).
Adapted from design/ecad/band/measure_step.py (which asserts 4 solids and the v7 piece order, so it cannot read the v8 files). Writes nothing into design/ecad.
Run: design/.venv/bin/python -I measure_step_v8.py   (prints a table; the last line is the count of boards over 0.05 mm)"""
import sys, math, importlib.util
from build123d import import_step

sys.dont_write_bytecode = True
ROOT = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/mfg/parts")
spec = importlib.util.spec_from_file_location("band_geom_v8", (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/band/band_geom.py"))
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)
T_EMB = 0.15            # embedded trunk and strip: the allowance of the model (thin.py flex_t)


def unique_yz(sol):
    pts = []
    for v in sol.vertices():
        p = (round(v.Y, 5), round(v.Z, 5))
        if p not in pts:
            pts.append(p)
    return pts


def bend_midline(sol):
    pts = unique_yz(sol)
    assert len(pts) == 4, pts
    pairs = sorted(((math.dist(pts[i], pts[j]), i, j) for i in range(4) for j in range(i + 1, 4)))
    (d1, a, b) = pairs[0]
    for d2, c, d in pairs[1:]:
        if len({a, b, c, d}) == 4:
            m1 = ((pts[a][0] + pts[b][0]) / 2, (pts[a][1] + pts[b][1]) / 2)
            m2 = ((pts[c][0] + pts[d][0]) / 2, (pts[c][1] + pts[d][1]) / 2)
            return math.dist(m1, m2)
    raise RuntimeError("no end faces")


def width(sol):
    b = sol.bounding_box()
    return b.max.X - b.min.X


over = 0
print("tail us | neck fold foot trunk (bend head | strip) = path | board flat length (band_geom) | difference | v7 path + FOOT_EXTRA")
for us in range(7, 14):
    S = G.Size(us)
    for tail, key in (("FLEX1", "thumb"), ("FLEX2", "away")):
        sol = import_step(f"{ROOT}/flex-tail-{key}/flex-tail-{key}-us{us}.step").solids()
        want_n = 6 if tail == "FLEX1" else 5
        assert len(sol) == want_n, (tail, us, len(sol))
        neck_b = sol[0].bounding_box()
        neck = neck_b.max.Z - neck_b.min.Z
        t_fin = min(neck_b.max.Y - neck_b.min.Y, 0.2)
        w_neck, w_foot = width(sol[0]), width(sol[2])
        fold = sol[1].volume / (t_fin * (w_neck + w_foot) / 2)
        foot = sol[2].volume / (w_foot * t_fin)
        trunk = sol[3].volume / (width(sol[3]) * T_EMB)
        if tail == "FLEX1":
            head = sol[4].volume / (width(sol[4]) * t_fin)
            bend = bend_midline(sol[5])
            total = neck + fold + foot + trunk + bend + head
            parts = f"{neck:.4f} {fold:.4f} {foot:.4f} {trunk:.4f} ({bend:.4f} {head:.4f})"
            want = S.len1
        else:
            strip = sol[4].volume / (width(sol[4]) * T_EMB)
            total = neck + fold + foot + trunk + strip
            parts = f"{neck:.4f} {fold:.4f} {foot:.4f} {trunk:.4f} | {strip:.4f}"
            want = S.len2
        diff = total - want
        over += abs(diff) > 0.05
        print(f"{tail} {us} | {parts} = {total:.4f} | {want:.4f} | {diff:+.4f} | {(S.path1 if tail == 'FLEX1' else S.path2) + G.FOOT_EXTRA:.4f}")
print(f"boards over 0.05 mm: {over} of 14")
