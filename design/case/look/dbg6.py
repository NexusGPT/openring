import sys
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/case"))
import case as C
import pebble as PB
H = PB.PEB["H"]
W = C.pebble_solid(H)
print("W valid", W.is_valid, "vol", round(W.volume), type(W).__name__)
big = 400.0
shell = W & C.box(-big, big, -big, big, C.ZP, 38.06)
print("shell", shell.is_valid, round(shell.volume), len(shell.solids()))
uf = C.rbox(-9.98, 15.92, -20.35, 20.35, C.ZP - 0.01, 17.3, 0.5)
print("uf", uf.is_valid, round(uf.volume))
r = shell - uf
print("cut", type(r).__name__, len(r.solids()), r.is_valid, round(r.volume) if len(r.solids()) else None)
uf2 = C.rbox(-9.98, 15.92, -20.35, 20.35, C.ZP + 0.2, 17.3, 0.5)
r2 = shell - uf2
print("cut2 (cavity not open at the bottom)", len(r2.solids()), round(r2.volume) if len(r2.solids()) else None)
# is the cavity inside the skin?
import numpy as np
for (x, y, z) in ((-9.98, 20.35, C.ZP), (15.92, 20.35, C.ZP), (-9.98, -20.35, C.ZP + 0.4)):
    print((x, y, z), "rho_pt", round(PB.rho_point(x, y), 3), "rho_z", round(float(PB.rho_of_z(z, H)), 3))
