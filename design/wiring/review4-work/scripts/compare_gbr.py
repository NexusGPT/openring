# Compares the opening sets (kind, centre, size rounded to 0.001) of two paste gerbers, with my parser of gerber_check.py.
import sys, importlib.util, collections
spec = importlib.util.spec_from_file_location("g", (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/wiring/review4-work/scripts/gerber_parse_only.py"))
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
a = collections.Counter((f[0].split(":")[0], round(f[1], 3), round(f[2], 3), round(f[3], 3), round(f[4], 3)) for f in g.parse(sys.argv[1]))
b = collections.Counter((f[0].split(":")[0], round(f[1], 3), round(f[2], 3), round(f[3], 3), round(f[4], 3)) for f in g.parse(sys.argv[2]))
print("delivered features", sum(a.values()), "regenerated", sum(b.values()), "only delivered", sum((a - b).values()), "only regenerated", sum((b - a).values()))
for k in list((a - b).elements())[:5]: print("only delivered", k)
for k in list((b - a).elements())[:5]: print("only regenerated", k)
