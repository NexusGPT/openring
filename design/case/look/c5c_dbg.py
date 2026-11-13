import sys, json, math
D = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case")
sys.path.insert(0, D)
import numpy as np
from build123d import import_step, Pos, Rot
lid = import_step(D + "/out/parts/lid.step")
prm = json.load(open(D + "/out/case_params.json"))
v, t = lid.tessellate(0.01, 0.02)
V = np.array([[p.X, p.Y, p.Z] for p in v]); T = np.array(t)
key = np.round(V, 4); _, idx, inv = np.unique(key, axis=0, return_index=True, return_inverse=True); inv = inv.ravel()
W, T = V[idx], inv[T]
a, b, c = W[T[:, 0]], W[T[:, 1]], W[T[:, 2]]
n = np.cross(b - a, c - a); ar = np.linalg.norm(n, axis=1); n /= np.maximum(ar, 1e-12)[:, None]
cen = (a + b + c) / 3
dx, dy, _ = prm["dimple"]
sel = (ar > 1e-9) & (cen[:, 2] > prm["z_lid0"] + 0.8) & (n[:, 2] > -0.2) & (np.hypot(cen[:, 0] - prm["pebble"]["XC"], cen[:, 1]) > 1.0) & (np.hypot(cen[:, 0] - dx, cen[:, 1] - dy) > 6.0)
ed = {}
for fi in np.where(sel)[0]:
    for e in ((T[fi, 0], T[fi, 1]), (T[fi, 1], T[fi, 2]), (T[fi, 2], T[fi, 0])):
        ed.setdefault((min(e), max(e)), []).append(fi)
res = []
for e, fs in ed.items():
    if len(fs) == 2:
        res.append((math.degrees(math.acos(float(np.clip(np.dot(n[fs[0]], n[fs[1]]), -1, 1)))), e, fs))
res.sort(reverse=True)
print("worst", [round(r[0], 2) for r in res[:8]], "p99.9", np.percentile([r[0] for r in res], 99.9))
for d, e, fs in res[:6]:
    m = (W[e[0]] + W[e[1]]) / 2
    print("  x %.2f y %.2f z %.2f angle %.2f rho %.3f dist to dimple %.1f areas %.5f %.5f" % (m[0], m[1], m[2], d, math.hypot(m[0] - prm["pebble"]["XC"], m[1]) / 22.5, math.hypot(m[0] - dx, m[1] - dy), ar[fs[0]] / 2, ar[fs[1]] / 2))
