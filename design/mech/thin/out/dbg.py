import sys
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/mech/thin"))
import thin
from thin import *
block = rbox(P["block_x"], P["block_y"], P["block_z"], 0, 0, P["block_z"] / 2, P["plan_r"])
ring = cyl_x(R_OUT, -4, 4) - cyl_x(R_IN, -10, 10)
w = [sector(R_IN, R_OUT_SH, 19, 57, -6.5, 6.5), sector(R_IN, R_OUT_SH, 303, 341, -6.5, 6.5)]
t = [taper(1, 55, 85), taper(-1, 55, 85)]
for n, o in [("block", block), ("ring", ring), ("w0", w[0]), ("w1", w[1]), ("t0", t[0]), ("t1", t[1])]:
    print(n, type(o).__name__, o.volume, o.is_valid)
e = block + ring
print("b+r", type(e).__name__, e.is_valid)
for n, o in [("w0", w[0]), ("w1", w[1]), ("t0", t[0]), ("t1", t[1])]:
    e = e + o
    print("+", n, type(e).__name__, e.volume, e.is_valid)
print("---")
for name, f in [("clean", lambda x: x.clean()), ("fix", lambda x: x.fix()), ("solid", lambda x: x.solids()[0] if x.solids() else None)]:
    try:
        y = f(e); print(name, type(y).__name__, y.volume, y.is_valid)
    except Exception as ex:
        print(name, "ERR", ex)
# alternative: fuse the bumps first, then onto block+ring
b = w[0] + w[1] + t[0] + t[1]
print("bumps", b.volume, b.is_valid)
e2 = (block + b) 
print("block+bumps", e2.volume, e2.is_valid)
e3 = e2 + ring
print("then ring", e3.volume, e3.is_valid)
