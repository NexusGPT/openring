import sys, json
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case/look"))
import numpy as np
import pebble as PB
prm = json.load(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case/out/case_params.json")))
PB.PEB.update(prm["pebble"])
z = np.load((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case/look/meshes.npz"))
v = z["lid__v"]; H = prm["h_tot"]
top = v[:, 2] > prm["z_lid0"] + 1.0
x, y, zz = v[top, 0], v[top, 1], v[top, 2]
rp = PB.rho_point_vec(x, y)
zf = PB.z_upper_of_rho(rp, H)
d = zz - zf
print("lid top vertices", top.sum(), "dz = surface z - nominal z(rho): min %.3f max %.3f mean %.3f" % (d.min(), d.max(), d.mean()))
for lo, hi in ((0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 1.0)):
    m = (rp >= lo) & (rp < hi)
    if m.any(): print("rho %.1f-%.1f: n %d dz %.3f .. %.3f" % (lo, hi, m.sum(), d[m].min(), d[m].max()))
print("top z max", zz.max(), "H", H)
