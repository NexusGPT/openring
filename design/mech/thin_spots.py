#!/usr/bin/env python3
"""Thin spots of the housing, measured on the real solids by distance between probe solids and the
housing faces, plus the matching formula from the dimension table. Prints one line per spot."""
import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ring  # noqa: E402
from build123d import Vertex  # noqa: E402

m = ring.build(size=9)
D = ring.D
z = ring.levels()
shell = m["top_shell"]
base = m["bases"][9]


def thickness_along(solid, p0, direction, max_len=3.0, step=0.005):
    """Walk from p0 (inside material) along direction; return length of material until the first exit."""
    n = 0
    x, y, zz = p0
    dx, dy, dz = direction
    inside = solid.is_inside((x, y, zz))
    if not inside:
        return None
    while n * step < max_len:
        n += 1
        if not solid.is_inside((x + dx * n * step, y + dy * n * step, zz + dz * n * step)):
            return n * step
    return max_len


def line(name, val, formula):
    print(f"THIN {name}: measured {val if val is None else round(val, 3)} mm | formula {formula}")


# glass seat outer lip at the -Y corner, Z 9.25, along the diagonal from the outer corner centre
cx, cy = -(D["block_x"] / 2 - D["corner_r"]), -(D["block_y"] / 2 - D["corner_r"])
ang = math.radians(225)
best = None
for a in range(180, 271, 2):
    t = math.radians(a)
    p = (cx + (D["corner_r"] - 0.001) * math.cos(t), cy + (D["corner_r"] - 0.001) * math.sin(t), z["glass0"] + 0.25)
    v = thickness_along(shell, p, (-math.cos(t), -math.sin(t), 0))
    if v is not None and (best is None or v < best):
        best = v
line("glass seat lip at the -X -Y corner (Z 9.25)", best, "seat outline r2.35 vs outer r3.0, see dimensions.csv")
# screen pocket corner, Z 8.5
best = None
for a in range(180, 271, 2):
    t = math.radians(a)
    p = (cx + (D["corner_r"] - 0.001) * math.cos(t), cy + (D["corner_r"] - 0.001) * math.sin(t), 8.5)
    v = thickness_along(shell, p, (-math.cos(t), -math.sin(t), 0))
    if v is not None and (best is None or v < best):
        best = v
line("wall at the screen pocket corner (Z 8.5)", best, "3.0 - |(13.725,9.05)-(12,7)|")
ly = (D["strip_y0"] + D["strip_y1"]) / 2
line("top skin over the antenna pocket", thickness_along(shell, (D["ant_xc"], ly, D["block_z"] - 0.001), (0, 0, -1)),
     f"{D['block_z']} - ({z['board1']} + {D['ant_z']} + {D['pocket_clear']})")
bb = [p for p in m["parts"] if p["name"] == "joystick_board"][0]["solid"].bounding_box()
line("top skin over the joystick board pocket", thickness_along(shell, ((bb.min.X + bb.max.X) / 2, (bb.min.Y + bb.max.Y) / 2, D["block_z"] - 0.001), (0, 0, -1)),
     "9.5 - (8.8 + 0.05)")
bzc = z["board0"] - D["btn_z"] / 2
line("wall skin beside the record button opening (in the recess)", thickness_along(shell, (D["btn_xc"] + D["btn_open_x"] / 2 + 0.05, D["strip_y1"] + 0.001, bzc), (0, 1, 0)),
     f"wall {D['wall']} - recess {D['btn_recess']}")
x, y = ring.screw_xy()[0]
line("floor under the screw head", thickness_along(base, (x, y + D["screw_head_d"] / 2 + 0.15 - 0.2, D["screw_head_t"] + 0.001), (0, 0, 1)),
     f"{D['floor_t']} - {D['screw_head_t']} (between clearance hole and counterbore edge)")
line("floor under the gasket groove", thickness_along(base, (0, -D["block_y"] / 2 + D["wall"] / 2, 0.001), (0, 0, 1)),
     f"{D['floor_t']} - {D['gasket_d']}")
line("floor ledge over the contact board", thickness_along(base, (D["cb_xc"] + 1.0, 4.5, D["cb_t"] + 0.001), (0, 0, 1)),
     f"{D['floor_t']} - {D['cb_t']}")
line("screw rib wall between pilot hole and cell side", thickness_along(shell, (D["boss_x0"] + 0.001, -D["screw_y"], 2.0), (1, 0, 0)),
     f"{D['screw_x']} - {D['screw_core_d']}/2 - {D['boss_x0']}")
line("nominal wall at X = 0, Y -10 (Z 4)", thickness_along(shell, (0, -D["block_y"] / 2 + 0.001, 4.0), (0, 1, 0)), "wall 1.0")
