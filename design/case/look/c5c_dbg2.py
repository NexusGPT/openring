import sys, json
D = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case")
sys.path.insert(0, D)
import case as C, case_check as K
from build123d import import_step, Pos, Rot
prm = json.load(open(D + "/out/case_params.json"))
parts = {n: import_step(f"{D}/out/parts/{n}.step") for n in prm["parts"]}
rc = C.Ring(9, C.load_base()).parts_in_case(prm["zb"])
px, py = prm["pivot"]
for ln in ("lid", "lid_seam_trim"):
    for a in (0.0, 50.0):
        lo = Pos(px, py, 0) * (Rot(0, 0, a) * (Pos(-px, -py, 0) * parts[ln]))
        out = []
        for k in ("body", "glass", "joystick"):
            out.append((f"ring {k}", round(K.near_distance(lo, rc[k]), 3)))
        for k, v in parts.items():
            if k in ("lid", "lid_seam_trim", "hinge_pivot", "magnet_lid") or k.startswith("glide"):
                continue
            d = K.near_distance(lo, v)
            if d < 0.35: out.append((k, round(d, 3)))
        print(ln, a, out, flush=True)
