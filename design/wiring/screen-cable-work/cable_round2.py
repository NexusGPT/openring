#!/usr/bin/env python3
"""cable_round2.py <r_in> <t>: round 2 of the screen cable study, variant C-solder (no connector; the cable's contact end soldered
by a hot bar onto 15 lands on the board's screen face). Uses the geometry engine of cable_layouts.py (imported, its own run silenced).

Path (screen turned 180 deg, ledge at the fingertip end, s = path length from the panel end):
  fold 1 at the fingertip end down to the upper leg (contacts then look UP, at the panel: section 2 of the study),
  upper leg toward -X under the panel, fold 2 (half turn down) in the neck at s FOLD2_S, lower leg toward +X with the contact face
  DOWN, the stiffened end soldered on the lands. Joint 0.03 and land 0.02 as in design/ecad/band/band-interface.md section 3.
Prints the block growth, every smallest free space (cable pieces against board, panel, its own other leg) and the land pattern."""
import contextlib
import io
import math
import sys

sys.argv = [sys.argv[0]] + sys.argv[1:3]
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
with contextlib.redirect_stdout(io.StringIO()):
    import cable_layouts as CL

R_IN, T, RC = CL.R_IN, CL.T, CL.RC
Z_BD1, Z_SC0, X_PANEL = CL.Z_BD1, CL.Z_SC0, CL.X_PANEL
LAND_T, JOINT = 0.02, 0.03              # band-interface.md section 3: land face 0.02 over the board, joint 0.03 after the hot bar
FOLD2_S = 13.0                          # fold 2 starts in the neck (neck from s 12.5, stiffened end from s 16.8: tail_measure.log)
CLEAR = 0.05                            # least space under the panel, as in layout C

z_low = Z_BD1 + LAND_T + JOINT + T / 2            # lower leg centre line (its underside on the joints)
end_top = Z_BD1 + LAND_T + JOINT + CL.CABLE["contact_t"]   # top of the stiffened end (0.2 with the stiffener)
z_up = z_low + 2 * RC                             # upper leg centre line after the half turn of fold 2
pb = z_up + T / 2 + CLEAR                         # panel underside
dh = pb - Z_SC0
print(f"C-solder r_in {R_IN} t {T}: lower leg centre {z_low:.3f}, stiffened end top {end_top:.3f}, upper leg centre {z_up:.3f}, "
      f"panel underside {pb:.3f}: block grows {dh:.3f} mm (formula 2 r_in + 2 t = {2 * R_IN + 2 * T:.3f})")
print(f"  upper leg underside over the stiffened end: {z_up - T / 2 - end_top:+.3f} mm free")

z_ledge = pb + CL.LOWER_GLASS + T / 2
p = CL.Path2(X_PANEL, z_ledge, 0.0, True)
diff = (z_ledge - 2 * RC) - z_up
if diff >= 0:
    p.arc(RC, -90); p.line(diff); p.arc(RC, -90)
    dip = None
else:
    p.arc(RC, -180)                                   # half turn, ends below z_up, then an S up to z_up
    dz = -diff
    phi = math.degrees(math.acos(1 - dz / (2 * RC)))
    p.arc(RC, -phi); p.arc(RC, phi)
    dip = z_ledge - 2 * RC - T / 2
print(f"  fold 1: ledge centre {z_ledge:.3f}; {'two quarter turns with a straight drop %.3f' % diff if dip is None else 'half turn dips to underside %.3f, then an S up %.3f' % (dip, -diff)}")
s_after1 = p.s
x_after1 = p.x
p.line(FOLD2_S - p.s)
x_f2 = p.x
p.arc(RC, 180)                                        # heading -X, turn down and back to +X
p.line(CL.CABLE["total"] - p.s)
x_end = p.x
s_stiff = CL.CABLE["total"] - CL.CABLE["stiff_len"]
x_stiff0 = x_end - (CL.CABLE["total"] - s_stiff)
print(f"  fold 1 ends at s {s_after1:.3f}, X {x_after1:.3f}; fold 2 at X {x_f2:.3f} (s {FOLD2_S}); cable end X {x_end:.3f}; stiffened end on the lands X {x_stiff0:.3f}..{x_end:.3f}")
cab = p.boxes()
panel_lo = ("PANEL_LOWER", "screen", -X_PANEL, X_PANEL, -6.4, 6.4, pb, pb + CL.LOWER_GLASS)
panel_up = ("PANEL_UPPER", "screen", -X_PANEL, X_PANEL - 2.951, -6.4, 6.4, pb + CL.LOWER_GLASS, pb + 0.8)
obst = [CL.PCB, panel_lo, panel_up] + [q for q in CL.parts if q[1] == "zone"]
w = CL.report("C-solder cable", cab, obst)
# self clearance: upper leg pieces (s < FOLD2_S) against lower leg pieces (s > fold 2 end), and fold-1 dip against the lower leg
s_f2_end = FOLD2_S + math.pi * RC
upper = [(s, b) for s, b in cab if s < FOLD2_S]
lower = [(s, b) for s, b in cab if s > s_f2_end]
self_gap = min(CL.box_gap(a, b) for _, a in upper for _, b in lower)
print(f"  own legs: least free space upper leg x lower leg {self_gap:+.3f} mm (box pieces; the stiffened end is drawn 0.2 thick about the "
      f"neck's centre line, so its true top is {end_top - (z_low + 0.1):.3f} higher: analytic line above)")
ov = CL.plan_overlap(cab, (-13.60, -8.75, 3.10, 6.30))
print(f"  antenna zone covered in plan {ov:.3f} mm2; least distance to the zone "
      f"{min(CL.box_gap(b, (-13.60, -8.75, 3.10, 6.30, CL.Z_BD0, Z_BD1)) for s, b in cab):.3f} mm")
pocket = X_PANEL + RC + T / 2 + 0.05
print(f"  fingertip end pocket to X {pocket:.3f}: metal left to the skin {CL.X_SKIN - pocket:.3f}")
# land pattern: 15 lands, pitch 0.30, centred on the cable centre line; pin order from the contact-face view (back view p5: pin 1 left,
# 15 right, tail end down). Final pose: tangent to the end = +X, contact face normal = -Z. Page right u = v x w with v = -X, w = -Z:
# u = (-X) x (-Z) = X x Z = -Y. So pin 1 (left, u < 0) lies at +Y.
yc = -(CL.CABLE["wide_y0"] + CL.CABLE["wide_y1"]) / 2
print(f"  lands: 15 x (0.15 across x 2.0 along X), pitch 0.30, X {x_end - 2.3:.3f}..{x_end - 0.3:.3f}, pin 1 at Y {yc + 2.1:+.3f}, "
      f"pin 15 at Y {yc - 2.1:+.3f} (pin 1 toward +Y); gap between lands 0.15 (board rule 0.075, ring-board-plan.md line 29)")
tp = [q for q in CL.parts if q[0].startswith("TP")]
land_box = (x_end - 2.3, x_end - 0.3, yc - 2.175, yc + 2.175, Z_BD1, Z_BD1 + LAND_T)
print(f"  lands to the nearest test pad: {min(CL.box_gap(land_box, q[2:]) for q in tp):.3f} mm")
u1 = [q for q in CL.parts if q[0] == "U1"][0]
u4 = [q for q in CL.parts if q[0] == "U4"][0]
lc = ((land_box[0] + land_box[1]) / 2, yc)
print(f"  land field centre ({lc[0]:.3f}, {lc[1]:.3f}) to U4 centre {math.hypot(lc[0] - (u4[2] + u4[3]) / 2, lc[1] - (u4[4] + u4[5]) / 2):.2f} mm "
      f"(under face; U1 spans X {u1[2]:.2f}..{u1[3]:.2f} below it)")
# a twist instead of fold 2 (flip the contact face without stacking): edge stretch of a 180 deg twist over the free neck length
L_free = s_stiff - CL.CABLE["neck_start"]
w2 = CL.CABLE["neck_w"] / 2
print(f"  alternative, a 180 deg twist of the neck: free neck {L_free:.3f} mm, edge path {math.hypot(L_free, math.pi * w2):.3f} mm: "
      f"edge stretch {math.hypot(L_free, math.pi * w2) / L_free:.2f} times its length (a film does not stretch: not possible)")
print(f"RESULT done C-solder r_in={R_IN} t={T} growth={dh:.3f}")
