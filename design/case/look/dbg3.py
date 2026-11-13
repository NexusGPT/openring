import sys, json
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case"))
import case as C
from build123d import Edge, import_step
prm = json.load(open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case/out/case_params.json")))
shell = import_step((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case/out/parts/shell.step"))
for n in (7, 9):
    xl = prm["cx"][str(n)] - (prm["ri"][str(n)] + 1.3)
    line = Edge.make_line((xl, 0, 0), (xl, 0, 60))
    r = shell.intersect(line)
    print(n, "xl", round(xl, 3), "zf", prm["zf"], "intersect type", type(r).__name__, [round(v.Z, 3) for e in (r or []) for v in e.vertices()] if r is not None else None)
    for y in (0.3, 1.0, 2.0):
        r = shell.intersect(Edge.make_line((xl, y, 0), (xl, y, 60)))
        print("   y", y, [round(v.Z, 3) for e in (r or []) for v in e.vertices()] if r is not None else None)
