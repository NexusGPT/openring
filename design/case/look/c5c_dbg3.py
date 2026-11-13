import sys, json
D = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case")
sys.path.insert(0, D)
import case as C
from build123d import import_step
P = D + "/out/parts/"
lid = import_step(P + "lid.step"); sh = import_step(P + "shell.step"); tr = import_step(P + "lid_seam_trim.step"); st = import_step(P + "seam_trim.step")
print("lid valid", lid.is_valid, "vol", lid.volume, "solids", len(lid.solids()), "faces", len(lid.faces()))
print("common lid x shell", C.common(lid, sh), "lid.distance_to(shell)", lid.distance_to(sh))
print("lid x lid_seam_trim", C.common(lid, tr), "dist", lid.distance_to(tr))
print("lid x seam_trim dist", lid.distance_to(st), "shell x seam_trim", sh.distance_to(st), C.common(sh, st))
# which faces of lid are near the shell
best = []
for f in lid.faces():
    d = f.distance_to(sh)
    if d < 0.05:
        c = f.center(); best.append((round(d, 3), f.geom_type.name, round(c.X, 1), round(c.Y, 1), round(c.Z, 2), round(f.area, 1)))
print(best[:8])
