"""Shared contract for the SLIM exterior of the ring recorder.

Owner, 2026-11-10: "L but ALMOST NO BEZEL" (the long narrow slab around the 0.95 inch
120 x 240 screen), after "I hate all of them, they are not as slick as the ring I shared".

Axes: X along the finger (+X = fingertip), Y across the finger (+Y = thumb side), Z up. Units: mm.
Origin: centre of the block's underside (Z = 0 rests on the finger).

Sources: screen drawing Tailor Pixels TOH095XVT-01 page 5 (panel 12.8 x 27.35 x 0.8, polariser
12.2 x 23.8, lit area 10.8 x 21.6, encapsulation glass 24.4 long). The split of the unlit
border along X is INFERRED from that drawing (lit area centred in the 24.4 mm glass): 1.4 mm at
the fingertip end, 4.35 mm at the driver end ("chin"). Stack: design/mech/slim_budget.py.
"""
from build123d import Box, Pos, Compound, fillet, Axis, export_gltf, export_step

PANEL_X, PANEL_Y, PANEL_Z = 27.35, 12.8, 0.8
LIT_X, LIT_Y = 21.6, 10.8
CHIN, FAR_BORDER, SIDE_BORDER = 4.35, 1.4, 1.0        # unlit panel borders (chin INFERRED)
CLEAR = 0.15                                           # panel to wall, each side
WALL_MIN = 0.45                                        # metal side wall, machined
FLOOR, GLASS = 0.6, 0.5

KEEP_IN_X = PANEL_X + 2 * (CLEAR + WALL_MIN)           # 28.55
KEEP_IN_Y = PANEL_Y + 2 * (CLEAR + WALL_MIN)           # 14.0
KEEP_IN_Z = 6.5                                        # floor 0.6 + cavity 5.4 + glass 0.5
KEEP_IN_R = 1.3    # largest plan corner radius that keeps 0.3 mm of wall at the square panel corner
KEEP_IN_BOTTOM_R = 0.6   # the keep-in's bottom edge is rounded: an outer bottom fillet up to 0.6 keeps 0.45 mm of wall
KEEP_IN_TOP_R = 0.3      # the keep-in's top edge is rounded: the cover glass edge may be rounded up to 0.3

LIMITS = {
    "block_max_x": 29.0, "block_max_y": 14.4, "block_max_z": 6.8,
    "lit_to_edge_side_max": 1.9,      # lit area to the block edge, across the finger
    "lit_to_edge_far_max": 2.3,       # at the fingertip end
    "lit_to_edge_chin_max": 5.3,      # at the driver end; cannot be less with this panel
    "band_width_min": 4.0, "band_width_max": 6.0, "band_wall_min": 1.4,
    "band_inner_d_size9": 18.95,      # US size 9
    "mic_inlets": 2,                  # each at least 0.5 square mm open
}
# lit area centre: the chin is at -X (toward the hand), so the lit area sits toward the fingertip
SCREEN_CX, SCREEN_CY = (CHIN - FAR_BORDER) / 2, 0.0    # +1.475, 0.0
SCREEN_Z_TOP = KEEP_IN_Z - GLASS                       # the panel's top face, under the cover glass

# names every exported part must use (the viewer assigns materials by these names)
PART_NAMES = ("body", "glass", "screen", "band", "joystick", "button", "light",
              "mic_1", "mic_2", "contacts")


def keep_in():
    """The solid every slim exterior must fully contain."""
    b = Pos(0, 0, KEEP_IN_Z / 2) * Box(KEEP_IN_X, KEEP_IN_Y, KEEP_IN_Z)
    b = fillet(b.edges().filter_by(Axis.Z), KEEP_IN_R)
    b = fillet(b.edges().group_by(Axis.Z)[0], KEEP_IN_BOTTOM_R)
    return fillet(b.edges().group_by(Axis.Z)[-1], KEEP_IN_TOP_R)


def check_exterior(outer, tol=0.02):
    """outer = solid outer skin of the block (body plus glass, no cavity, no band), BEFORE the
    microphone slots and any other inlet or window is cut: inlets are openings, not skin.
    Returns a list of failures (empty list = pass)."""
    fails = []
    bb = outer.bounding_box()
    sx, sy, sz = bb.max.X - bb.min.X, bb.max.Y - bb.min.Y, bb.max.Z - bb.min.Z
    for name, v, lim in (("X", sx, "block_max_x"), ("Y", sy, "block_max_y"), ("Z", sz, "block_max_z")):
        if v > LIMITS[lim] + 1e-6:
            fails.append(f"block {name} {v:.2f} > {LIMITS[lim]}")
    if bb.min.Z < -1e-6:
        fails.append(f"block goes below Z 0: {bb.min.Z:.2f}")
    outside = keep_in() - outer
    v = outside.volume if outside is not None else 0.0
    if v > tol:
        fails.append(f"keep-in volume sticks out of the exterior by {v:.3f} cubic mm")
    # bezel: lit area to block edge
    side = sy / 2 - LIT_Y / 2
    far = bb.max.X - (SCREEN_CX + LIT_X / 2)
    chin = (SCREEN_CX - LIT_X / 2) - bb.min.X
    for name, v, lim in (("side", side, "lit_to_edge_side_max"), ("far end", far, "lit_to_edge_far_max"),
                         ("chin", chin, "lit_to_edge_chin_max")):
        if v > LIMITS[lim] + 1e-6:
            fails.append(f"bezel {name} {v:.2f} > {LIMITS[lim]}")
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
