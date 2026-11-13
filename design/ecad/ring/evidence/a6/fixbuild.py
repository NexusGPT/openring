P = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/ecad/ring/evidence/a6/build_notes.py")
s = open(P).read()
a = "    V[k] = ln(f, p)\n"
b = "    if f == BOM and p.startswith(',') and p.endswith(','):\n        p = ',\"?' + p[1:-1] + '\"?,'\n    V[k] = ln(f, p)\n"
assert s.count(a) == 1
s = s.replace(a, b)
s = s.replace("(BOM, r',\"?U5,U6\"?,')", "(BOM, r',U5,U6,')")
open(P, 'w').write(s)
