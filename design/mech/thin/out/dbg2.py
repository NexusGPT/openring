import sys
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[4].as_posix() + "/design/mech/thin"))
from thin import *
block = rbox(P["block_x"], P["block_y"], P["block_z"], 0, 0, P["block_z"] / 2, P["plan_r"])
ring = cyl_x(R_OUT, -P["band_w"] / 2, P["band_w"] / 2) - cyl_x(R_IN, -10, 10)
hw = 6.5
bumps = [sector(R_IN, R_OUT_SH, 19, 57, -hw, hw), sector(R_IN, R_OUT_SH, 303, 341, -hw, hw), taper(1, 55, 85), taper(-1, 55, 85)]
b = fuse_all(bumps)
print("bumps", b.volume, b.is_valid, type(b).__name__)
e = block + b
print("blk+b", e.volume, e.is_valid)
e = e + ring
print("+ring", e.volume, e.is_valid)
e = e.clean()
print("clean", e.volume, e.is_valid)
