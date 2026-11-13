import sys
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case"))
sys.argv = ["x"]
import numpy as np, math
import case as C, pebble as PB
exec(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case/look/dbg9.py")).read().split("def rep(")[0].split("H = PB.PEB")[0])
H = PB.PEB["H"]; ct = PB.PEB["CT"]; vt = PB.PEB["VT"]; et = PB.PEB["ET"]; S = PB.PEB["S"]; ret = 1 - et / S; zw1 = H - ct - vt
a = [(37.96, float(PB.rho_of_z(37.96, H)))] + [(zw1 + vt * math.sqrt(1 - (1 - u) ** 2), 1 - u * et / S) for u in (0.02, 0.06, 0.12, 0.2, 0.3, 0.42, 0.55, 0.7, 0.85, 1.0)] + [(H - ct * t * t, ret * t) for t in (0.92, 0.8, 0.6, 0.35)] + [(H, 0.0)]
b = [(37.96, float(PB.rho_of_z(37.96, H)))] + [(z, r) for z, r in PB.sections(H) if 37.96 + 0.15 < z < H - 0.15 and 0 < r and not (r > 0.9999 and (z < 37.96 + 0.6))] + [(H, 0.0)]
print("A", [(round(z, 3), round(r, 4)) for z, r in a])
print("B", [(round(z, 3), round(r, 4)) for z, r in b])
