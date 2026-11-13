import sys, math
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/mech/thin"))
import thin
from build123d import import_step, export_step, Cylinder, Sphere, Pos, Axis, fillet
P = thin.P
D = (__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/mech/thin/out/v7/probe/")
def tryw(nm, sh):
    try:
        export_step(sh, D + nm + ".step"); r = import_step(D + nm + ".step")
        print(nm, "OK solids", len(r.solids()), round(sum(x.volume for x in r.solids()), 4), flush=True)
    except Exception as e:
        print(nm, "FAIL", e, flush=True)
z_rim, cap0 = 14.97, 10.8526
cap = Pos(0, 0, (cap0 + z_rim) / 2) * Cylinder(2.2, z_rim - cap0)
tryw("a_cyl", cap)
cap = fillet(cap.edges().group_by(Axis.Z)[-1], 0.3)
tryw("b_fillet", cap)
a_d = 1.9; R_d = (a_d ** 2 + 0.25 ** 2) / 0.5
cap = cap - Pos(0, 0, z_rim - 0.25 + R_d) * Sphere(R_d)
tryw("c_dish", cap)
lifted = Pos(0, 0, 0.08) * cap
rg_all = None
for rr in (0.7, 1.3, 1.9):
    ring = Pos(0, 0, z_rim) * (Cylinder(rr + 0.125, 4.0) - Cylinder(rr - 0.125, 4.2))
    rg = (lifted & ring) - cap
    tryw(f"d_ridge_{rr}", rg)
    rg_all = rg if rg_all is None else rg_all + rg
full = cap + rg_all
tryw("e_full", full)
tryw("f_full_clean", full.clean())
tryw("g_rot", thin.rloc(-78.0) * full)
