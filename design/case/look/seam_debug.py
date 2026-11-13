import sys, os, json, math
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case"))
import numpy as np
import case as C
import pebble as PB
P = json.load(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case/look/c4_params.json")))
H = 42.96; z_split = 36.16 + 3.0 ; 
# recompute levels as case.build does
cell_z0 = C.ZP + 0.4; p0 = cell_z0 + 8.5 + 0.3; p1 = p0 + 1.0; zf = round(p1 + 3.31 + 0.3 + 1.8 + 0.05, 1); zb = zf + 4.01
zs = round(zb + 14.65 + 0.3, 2); zl = round(zs + 0.3, 2); H = round(zl + 4.0, 2)
print("levels", zf, zb, zs, zl, H)
px0, px1, py0, py1 = P["px0"], P["px1"], P["py0"], P["py1"]
rs = float(PB.rho_of_z(zs, H)); print("rho seam", rs)
seam = np.array(PB.outline_at(rs, 360)).T
print("seam bbox", seam.min(0), seam.max(0))
hull = np.array(P["hull_w"])
print("hull bbox", hull.min(0), hull.max(0))
G = np.array([(x, y) for x in np.arange(seam[:,0].min(), seam[:,0].max(), 0.6) for y in np.arange(seam[:,1].min(), seam[:,1].max(), 0.6)])
G = G[C.inside(G, seam)]
d_out = C.seg_dist(G, seam)
d_h = C.seg_dist(G, hull); d_h = np.where(C.inside(G, hull), -d_h, d_h)
thick = np.array([float(PB.z_upper_of_rho(PB.rho_point(x, y), H)) - zl for x, y in G])
for r, t in ((2.5, 2.5), (2.0, 1.5), (1.6, 1.0)):
    ok = (d_out >= r + 0.9) & (d_h >= r + 0.7) & (thick >= t)
    print("r", r, "thick", t, "count", ok.sum(), "(outline only", (d_out >= r+0.9).sum(), "well only", (d_h >= r+0.7).sum(), "thick only", (thick >= t).sum(), ")")
    if ok.sum(): print("  sample", G[ok][:5].tolist())
print("max thickness", thick.max(), "at", G[thick.argmax()])
