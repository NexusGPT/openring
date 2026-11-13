"""calibration of the face-by-face swing distance and the common-volume test (C5c). Output look/c5c_calib_swing.log"""
import sys, json
D = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case")
sys.path.insert(0, D)
import case as C, case_check as K
from build123d import import_step, Pos, Rot
prm = json.load(open(D + "/out/case_params.json"))
P = {n: import_step(f"{D}/out/parts/{n}.step") for n in ("lid", "shell", "liner", "seam_trim", "lid_seam_trim")}
px, py = prm["pivot"]
for label, dz in (("lid in place (gap 0.3 mm by construction)", 0.0), ("lid pushed 0.5 mm down into the shell", -0.5)):
    out = {}
    for a in (0.0, 50.0, 100.0):
        lo = Pos(px, py, dz) * (Rot(0, 0, a) * (Pos(-px, -py, 0) * P["lid"]))
        out[a] = {k: (round(K.near_distance(lo, P[k]), 3), round(C.common(lo, P[k]), 3)) for k in ("shell", "liner", "seam_trim")}
    print(label, "(face distance mm, common volume mm3) per part at 0 / 50 / 100 degrees:", out, flush=True)
