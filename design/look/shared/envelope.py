"""Shared contract for the exterior look studies of the ring recorder.

Axes: X along the finger, Y across the finger (+Y = thumb side), Z up. Units: mm.
Origin: centre of the block's underside (Z = 0 is the surface that rests on the finger).

Every look study imports this file, builds its exterior solids, and calls export_look().
The engineering inside is fixed: the exterior must contain KEEP_IN and respect LIMITS.
"""
from build123d import (Box, Pos, Compound, Color, fillet, Axis, export_gltf, export_step)

# --- fixed engineering volume the exterior must enclose -------------------------------
# Inner cavity of the electronics (28.0 x 18.0 x 8.5, vertical edges r 2.0), grown by the
# minimum wall of 0.8 mm at the sides and floor. The top of the cavity is closed by the
# cover glass (0.5 mm) or by a 0.8 mm skin.
KEEP_IN_X = 29.6      # 28.0 + 2 x 0.8
KEEP_IN_Y = 19.6      # 18.0 + 2 x 0.8
KEEP_IN_Z = 9.3       # floor 0.8 + cavity 8.0 + glass 0.5
KEEP_IN_R = 2.8       # vertical edge radius of the keep-in volume

LIMITS = {
    "block_max_x": 33.0,   # the block may not be longer than this
    "block_max_y": 22.0,
    "block_max_z": 10.5,
    "screen_active_x": 21.6,   # visible display area, centred at (SCREEN_CX, SCREEN_CY)
    "screen_active_y": 10.8,
    "band_width_min": 5.0, "band_width_max": 9.0, "band_wall_min": 1.6,
    "band_inner_d_size9": 18.95,   # US size 9
    "mic_inlets": 4,               # sound inlets, each at least 0.5 square mm of open area
}
SCREEN_CX, SCREEN_CY = 0.0, -2.5   # centre of the display under the glass (fixed by the board)

# names every exported part must use (the viewer assigns materials by these names)
PART_NAMES = ("body", "glass", "screen", "band", "joystick", "button", "light",
              "mic_1", "mic_2", "mic_3", "mic_4", "contacts")


def keep_in():
    """The solid every exterior must fully contain."""
    b = Pos(0, 0, KEEP_IN_Z / 2) * Box(KEEP_IN_X, KEEP_IN_Y, KEEP_IN_Z)
    return fillet(b.edges().filter_by(Axis.Z), KEEP_IN_R)


def check_exterior(outer, tol=0.02):
    """outer = the solid outer skin of the block (body plus glass, no cavity, no band).
    Returns a list of failures (empty list = pass)."""
    fails = []
    bb = outer.bounding_box()
    sx, sy, sz = bb.max.X - bb.min.X, bb.max.Y - bb.min.Y, bb.max.Z - bb.min.Z
    if sx > LIMITS["block_max_x"] + 1e-6: fails.append(f"block X {sx:.2f} > {LIMITS['block_max_x']}")
    if sy > LIMITS["block_max_y"] + 1e-6: fails.append(f"block Y {sy:.2f} > {LIMITS['block_max_y']}")
    if sz > LIMITS["block_max_z"] + 1e-6: fails.append(f"block Z {sz:.2f} > {LIMITS['block_max_z']}")
    if bb.min.Z < -1e-6: fails.append(f"block goes below Z 0: {bb.min.Z:.2f}")
    k = keep_in()
    outside = k - outer
    v = outside.volume if outside is not None else 0.0
    if v > tol: fails.append(f"keep-in volume sticks out of the exterior by {v:.3f} cubic mm")
    return fails


def export_look(parts, out_dir, name="ring"):
    """parts = dict name -> solid. Names must come from PART_NAMES. Writes <name>.glb and <name>.step."""
    import os
    os.makedirs(out_dir, exist_ok=True)
    missing = [n for n in PART_NAMES if n not in parts]
    extra = [n for n in parts if n not in PART_NAMES]
    if missing or extra:
        raise SystemExit(f"part names: missing {missing}, unknown {extra}")
    kids = []
    for n in PART_NAMES:
        s = parts[n]
        s.label = n
        kids.append(s)
    asm = Compound(label=name, children=kids)
    export_gltf(asm, os.path.join(out_dir, name + ".glb"), binary=True,
                linear_deflection=0.01, angular_deflection=0.1)
    export_step(asm, os.path.join(out_dir, name + ".step"))
    return asm
