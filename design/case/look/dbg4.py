import sys
from build123d import Edge, import_step, Vector
shell = import_step((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case/out/parts/shell.step"))
print("valid", shell.is_valid, "vol", round(shell.volume, 1), "type", type(shell).__name__, "solids", len(shell.solids()), "faces", len(shell.faces()))
for x, y in ((2.0, 0.0), (5.0, 3.0), (-5.0, 0.0), (30.0, 0.0), (10.0, 18.0)):
    r = shell.intersect(Edge.make_line((x, y, 0), (x, y, 60)))
    print(x, y, None if r is None else [round(v.Z, 2) for e in r for v in e.vertices()])
    zs = []
    for f in shell.faces():
        pass
