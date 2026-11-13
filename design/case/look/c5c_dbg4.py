import sys
D = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case")
sys.path.insert(0, D)
from build123d import import_step, Solid
P = D + "/out/parts/"
lid = import_step(P + "lid.step"); sh = import_step(P + "shell.step")
print("raw", lid.distance_to(sh))
lf = lid.fix(); sf = sh.fix()
print("lid fixed", lf.distance_to(sh), "shell fixed", lid.distance_to(sf))
print("solid types", type(lid).__name__, type(sh).__name__, "lid orientation vol", lid.volume, "shell vol", sh.volume)
# distance between lid and shell faces individually
m = min(lid.distance_to(f) for f in sh.faces()[:400])
print("min over first 400 shell faces", m)
import numpy as np
dd = sorted((lid.distance_to(f), i) for i, f in enumerate(sh.faces()))[:4]
print(dd)
