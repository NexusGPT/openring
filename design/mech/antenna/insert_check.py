"""Geometry of the recommended radio corner, measured on the inside model's STEP (nothing in design/mech/thin is changed).

The radio corner = the part of the metal body inside the box X -14.8 to -10.6, Y 2.05 to 7.6 (all Z): the design's own
keep-out (architecture.md line 156, 4.2 x 4.7 centred on ANT1, 4.2 along X) carried out through the body's outer skin.
It is made in resin instead of metal and bonded in. ANT1 moves down to hang from the board underside (pads on the board,
no notch): Z 0.23 to 1.43. A pocket 1.8 x 3.4 x 0.22 in the resin floor (Z 0.18 to 0.40) gives it 0.05 mm of air below.

Run: cd <repo>/design/mech/antenna && nice -n 19 ../../.venv/bin/python insert_check.py > insert_check.log 2>&1
"""
from pathlib import Path

from build123d import Box, Pos, import_step
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

HERE = Path(__file__).resolve().parent
STEP = HERE.parent / "thin" / "out" / "thin-inside.step"
KX0, KX1, KY0, KY1 = -14.8, -10.6, 2.05, 6.75          # keep-out 4.2 (X) x 4.7 (Y) centred on (-12.7, 4.4)
CUT = (KX0, KX1, KY0, 7.6, -1.0, 3.0)                    # carried through the body skin (body max Y 7.375 at the block)
ANT_OLD = (-13.5, -11.9, 2.8, 6.0, 0.45, 1.65)           # placement.csv line 13
ZTOP = 1.43                                              # board underside 1.45 minus pad 0.02 (thin.py line 197; measure.log main_board__gold Z)
ANT_NEW = (-13.5, -11.9, 2.8, 6.0, ZTOP - 1.2, ZTOP)     # hangs from the board underside
POCKET = (-12.7 - 0.9, -12.7 + 0.9, 4.4 - 1.7, 4.4 + 1.7, ANT_NEW[4] - 0.05, 0.40)


def bx(b):
    return Pos((b[0] + b[1]) / 2, (b[2] + b[3]) / 2, (b[4] + b[5]) / 2) * Box(b[1] - b[0], b[3] - b[2], b[5] - b[4])


def f3(v):
    return f"{v:.3f}"


def dist(a, b):
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    return d.Value()


top = import_step(str(STEP))
kids = {c.label: c for c in top.children}
body = kids["outer_body__metal"]
print(f"STEP {STEP}; body volume {f3(body.volume)} mm3")
cut = bx(CUT)
corner = body & cut
rest = body - cut
pocket = bx(POCKET)
corner_p = corner - pocket
cb = corner.bounding_box()
print(f"radio corner (body inside X {KX0} to {KX1}, Y {KY0} to body edge): volume {f3(corner.volume)} mm3 before the antenna pocket, "
      f"{f3(corner_p.volume)} mm3 after; bounding box X {f3(cb.min.X)} to {f3(cb.max.X)}, Y {f3(cb.min.Y)} to {f3(cb.max.Y)}, Z {f3(cb.min.Z)} to {f3(cb.max.Z)}")
print(f"metal body left: {f3(rest.volume)} mm3 (removed {f3(body.volume - rest.volume)} mm3)")

# seam faces: faces of the corner lying on the two cut planes
for name, test in (("seam on plane X = -10.6", lambda c: abs(c.X - KX1) < 1e-4),
                   ("seam on plane Y = 2.05", lambda c: abs(c.Y - KY0) < 1e-4)):
    fs = [f for f in corner.faces() if test(f.center()) and (f.bounding_box().max.X - f.bounding_box().min.X < 1e-4 or
                                                               f.bounding_box().max.Y - f.bounding_box().min.Y < 1e-4)]
    area = sum(f.area for f in fs)
    for f in fs:
        b = f.bounding_box()
        print(f"   {name}: face area {f3(f.area)} mm2, X {f3(b.min.X)} to {f3(b.max.X)}, Y {f3(b.min.Y)} to {f3(b.max.Y)}, Z {f3(b.min.Z)} to {f3(b.max.Z)}")
    print(f"{name}: {len(fs)} faces, bond area {f3(area)} mm2")

a_old, a_new = bx(ANT_OLD), bx(ANT_NEW)
print(f"antenna today Z {ANT_OLD[4]} to {ANT_OLD[5]}: least distance to the whole metal body {f3(dist(a_old, body))}")
print(f"antenna today: least distance to the metal left after the cut {f3(dist(a_old, rest))}")
print(f"antenna moved under the board, Z {f3(ANT_NEW[4])} to {f3(ANT_NEW[5])}: least distance to the metal left {f3(dist(a_new, rest))}")
print(f"antenna moved: overlap with the resin corner after the pocket {f3((a_new & corner_p).volume)} mm3 (0 = fits)")
print(f"antenna moved: least distance to the resin corner after the pocket {f3(dist(a_new, corner_p))}")
under = corner_p & bx((-13.5, -11.9, 2.8, 6.0, -1.0, ANT_NEW[4]))
ub = under.bounding_box()
print(f"resin left under the antenna: Z {f3(ub.min.Z)} to {f3(ub.max.Z)} -> {f3(ub.max.Z - ub.min.Z)} mm")
for lab in ("screen_connector__polymer", "screen_connector__gold", "screen_connector__metal", "screen__screen", "screen__chip",
            "screen_tail__flex", "mic_1__metal", "recording_led__polymer", "main_board__pcb"):
    s = kids[lab]
    x = a_new & s
    ov = x.volume if x is not None else 0.0
    print(f"antenna moved vs {lab}: least distance {f3(dist(a_new, s))}, overlap {f3(ov)} mm3")
for lab in ("screen_tail__flex", "screen_connector__polymer", "mic_1__metal", "recording_led__polymer", "light_pipe__glass"):
    x = corner & kids[lab]
    print(f"radio corner vs {lab}: overlap {f3(x.volume if x is not None else 0.0)} mm3 ({'no common solid' if x is None else 'common solid'})")
ok = (a_new & corner_p).volume < 1e-6 and dist(a_new, rest) > 0.7
print("RESULT insert measured" if ok else "RESULT insert check failed")
