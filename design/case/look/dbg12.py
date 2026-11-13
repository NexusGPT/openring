import sys, os, json
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case"))
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case/look"))
from build123d import import_step
import case_check as K
import pebble as PB
D = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case")
prm = json.load(open(D + "/out/case_params.json")); PB.PEB.update(prm["pebble"])
parts = {n: import_step(f"{D}/out/parts/{n}.step") for n in ("shell", "lid", "base_plate")}
skin5 = lambda p: PB.rho_point(p.X, p.Y) >= float(PB.rho_of_z(p.Z, prm["h_tot"])) - 0.012
n, bad = K.planar_outside(parts, (prm["z_split"], prm["z_lid0"]), skin5)
print("C5b planar skin faces", n, bad[:6])
c4 = {n_: import_step(f"{D}/look/c4_out/parts/{n_}.step") for n_ in ("shell", "lid", "base_plate")}
bbs = [v.bounding_box() for v in c4.values()]
lo = (min(b.min.X for b in bbs), min(b.min.Y for b in bbs), min(b.min.Z for b in bbs)); hi = (max(b.max.X for b in bbs), max(b.max.Y for b in bbs), max(b.max.Z for b in bbs))
skin4 = lambda p: any(abs(v - l) < 0.05 or abs(v - h) < 0.05 for v, l, h in zip((p.X, p.Y, p.Z), lo, hi))
n4, bad4 = K.planar_outside(c4, (36.16, 36.56), skin4)
print("C4 planar skin faces", n4, bad4[:6])
