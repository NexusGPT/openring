#!/usr/bin/env python3
"""cable_layouts.py: lays the STOCK screen cable of the Tailor Pixels TOH095XVT-01 along three layouts in the ring's block and
prints, for every cable run and every neighbouring part, the smallest free space (negative = overlap depth).

Read only. Inputs (read at run time, never written):
  design/mech/thin/placement.csv                          Z stack (board, foam, screen, glass rows), body box
  design/wiring/ring-board-plan-work/placement-plan.csv   every board part: place, face, turn
  design/ecad/ring/pcb/OpenRing.pretty/*.kicad_mod        courtyards (F.CrtYd) of the board parts
Geometry: axis-aligned boxes. A cable run is cut into pieces of at most 0.05 mm of path; each piece is the box of its centre-line
chord grown by half the cable thickness, with the cable's width at that path position (maker drawing p5, see CABLE below).
Folds are true circular arcs of the centre line. Coordinates: inside-model mm, X along the finger (+X fingertip), Y across
(+Y thumb, antenna side), Z up, origin at the centre of the block underside (design/mech/thin/thin.py line 28).

Usage: cable_layouts.py <r_in> <t>     inner fold radius and cable thickness in mm (start values 0.30 and 0.14, see the study)
"""
import csv
import math
import re
import sys
from pathlib import Path

ROOT = Path((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix()))
R_IN = float(sys.argv[1]) if len(sys.argv) > 1 else 0.30
T = float(sys.argv[2]) if len(sys.argv) > 2 else 0.14
RC = R_IN + T / 2                       # centre-line radius of every fold

# ---------------------------------------------------------------- stock cable, maker drawing p5 (tail_measure.log)
CABLE = dict(wide_w=12.402, wide_y0=-6.198, wide_y1=6.204, wide_end=12.0,   # full width to 11.496, corner r 0.5 -> 12.0
             neck_w=4.805, neck_start=12.5, total=20.0, stiff_len=3.2, contact_t=0.20)


def width_at(s, rotated):
    """Y interval of the cable at path position s (mm from the panel end). Conservative: the wide width is kept to the end of
    the shoulder fillets (s 12.5). Rotated (screen turned 180 deg about Z): Y is mirrored."""
    if s < CABLE["neck_start"]:
        y0, y1 = CABLE["wide_y0"], CABLE["wide_y1"]
    else:
        c = (CABLE["wide_y0"] + CABLE["wide_y1"]) / 2
        y0, y1 = c - CABLE["neck_w"] / 2, c + CABLE["neck_w"] / 2
    return (-y1, -y0) if rotated else (y0, y1)


def thick_at(s):
    return CABLE["contact_t"] if s > CABLE["total"] - CABLE["stiff_len"] else T


# ---------------------------------------------------------------- Z stack from design/mech/thin/placement.csv
rows = {r["part"]: r for r in csv.DictReader(open(ROOT / "design/mech/thin/placement.csv"))}


def zr(name):
    r = rows[name]
    z, h = float(r["z"]), float(r["size_z"])
    return round(z - h / 2, 4), round(z + h / 2, 4)


Z_BD0, Z_BD1 = zr("main_board")           # board under face, screen face
Z_SC0, Z_SC1 = zr("screen")               # panel underside, panel top
Z_GB = zr("cover_glass")[0]
Z_FLOOR = round(Z_BD0 - 1.00 - 0.05, 4)   # thin.py lines 269-270: under 1.00, gap 0.05
ZTOP = Z_BD0 - 0.02                       # thin.py line 271: top of every part hanging under the board (pad 0.02)
LOWER_GLASS = 0.40                        # thin.py line 425 (lower glass 0.4: ASSUMED split, thin-notes.md line 39)
X_PANEL = float(rows["screen"]["size_x"]) / 2          # 13.675
X_POCKET = X_PANEL + 0.05                               # panel pocket = panel + 0.05 per side (body.md line 89)
X_SKIN = float(rows["outer_body"]["size_x"]) / 2        # 14.65 (body box; end_wall.log: flat end face 14.650 from Z 1.0 up)
Y_POCKET = float(rows["screen"]["size_y"]) / 2 + 0.05   # 6.45
print(f"stack (placement.csv): floor top {Z_FLOOR}, board {Z_BD0}..{Z_BD1}, panel {Z_SC0}..{Z_SC1}, glass bottom {Z_GB}; "
      f"panel end X +-{X_PANEL}, pocket face +-{X_POCKET}, body end skin +-{X_SKIN}, pocket half width {Y_POCKET}")
print(f"cable: thickness t {T}, contact end {CABLE['contact_t']}, fold inner radius {R_IN} (centre line {RC:.3f})")

# ---------------------------------------------------------------- board parts
FP_DIR = ROOT / "design/ecad/ring/pcb/OpenRing.pretty"
HEIGHT = {  # height below the board's under face, mm; source in brackets
    "ANT_Johanson": (1.20, "antenna datasheet T 1.20 (ring-board-plan.md e)"),
    "Chip_0201": (0.30, "[start value, not sourced]"), "Chip_0402": (0.50, "thin.py line 388 ASSUMED"),
    "Chip_0603": (0.80, "[start value, not sourced]"), "FPC_Hirose": (1.00, "catalog p3 0.9 +-0.1, max"),
    "L_Murata_1269AS": (1.00, "bom.csv line 30, 1.0 max"), "L_TDK_MLZ1608": (0.80, "[start value, not sourced]"),
    "LGA-8_Knowles": (1.00, "placement.csv mic_1"), "LGA-9_CSNP32": (0.80, "placement.csv storage z 1.005 h 0.75 -> bottom 0.63"),
    "UQFN-16": (0.55, "[start value, not sourced]"), "USON-10": (0.55, "[start value, not sourced]"),
    "WLCSP-16": (0.77, "placement.csv U4 bottom 0.662"), "WLCSP-35": (0.69, "placement.csv U2 bottom 0.742"),
    "WLCSP-61": (0.58, "placement.csv U1 bottom 0.850"), "X2SON-4": (0.42, "placement.csv U11 0.4 + pad"),
    "XTAL_Kyocera": (0.52, "placement.csv X1 0.5 ASSUMED"), "XTAL_TXC": (0.52, "placement.csv X2 0.5 ASSUMED"),
    "TESTPAD": (0.0, "flat copper on the screen face"), "J_BAND": (0.24, "thin.py: foot top 1.40, flex 0.11, stiffener 0.10"),
}


def courtyard(fp):
    name = fp.split(":")[1]
    if name.startswith("J_BAND"):
        return (-1.25, -1.10, 1.25, 1.10)          # keep-out X -3.50..-1.00, |Y| 3.40..5.60 (ring-board-plan.md f.1) about (-2.25, +-4.325)
    txt = (FP_DIR / f"{name}.kicad_mod").read_text()
    xs, ys = [], []
    for blk in re.findall(r"\((?:fp_rect|fp_line)(.*?)\(layer \"F\.CrtYd\"\)", txt, re.S):
        for a, b in re.findall(r"\((?:start|end) ([-\d.]+) ([-\d.]+)\)", blk):
            xs.append(float(a)); ys.append(float(b))
    return (min(xs), min(ys), max(xs), max(ys))


def height(fp):
    for k, v in HEIGHT.items():
        if k in fp:
            return v[0]
    raise KeyError(fp)


parts = []          # (ref, face, x0, x1, y0, y1, z0, z1)
for r in csv.DictReader(open(ROOT / "design/wiring/ring-board-plan-work/placement-plan.csv")):
    cx0, cy0, cx1, cy1 = courtyard(r["footprint"])
    th = math.radians(float(r["rotation_deg"]))
    pts = []
    for lx, ly in ((cx0, cy0), (cx0, cy1), (cx1, cy0), (cx1, cy1)):
        # KiCad: local Y points down; position = model + (100, 100), no mirror (ring-board-plan.md line 20)
        gx = lx * math.cos(th) + ly * math.sin(th)
        gy = -lx * math.sin(th) + ly * math.cos(th)
        pts.append((float(r["x_mm"]) + gx, float(r["y_mm"]) + gy))
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    h = height(r["footprint"])
    if r["side"] == "F":
        parts.append((r["reference"], "under", x0, x1, y0, y1, ZTOP - h, ZTOP))
    else:
        parts.append((r["reference"], "screen", x0, x1, y0, y1, Z_BD1, Z_BD1 + 0.035))
# fixed volumes that are not board parts
FIXED = [
    ("ANT_ZONE", "zone", -13.60, -8.75, 3.10, 6.30, Z_BD0, Z_BD1),          # copper-free zone, all 4 layers (lead-decisions.md "W2, rule on places")
    ("RESIN_CORNER", "zone", -14.80, -8.60, 2.05, 7.375, 0.0, 2.75),        # body.md line 143
    ("MIC_GSK_U5", "body", -12.67, -10.87, -5.70, -3.90, 0.30, ZTOP - 1.0),  # gasket on the floor up to the lid (placement.csv GSK2)
    ("MIC_GSK_U6", "body", 10.87, 12.67, -5.70, -3.90, 0.30, ZTOP - 1.0),
    ("BAND_NECK_A", "band", -3.40, -1.60, -6.20, -5.60, Z_FLOOR, ZTOP),       # band circuit necks rising from the floor slots (thin.py v8)
    ("BAND_NECK_B", "band", -3.40, -1.60, 5.60, 6.20, Z_FLOOR, ZTOP),
]
for f in FIXED:
    parts.append(f)
PCB = ("PCB1", "board", -13.6, 13.6, -6.3, 6.3, Z_BD0, Z_BD1)


def box_gap(a, b):
    """smallest free space between two boxes (x0,x1,y0,y1,z0,z1); negative = overlap depth (least axis)"""
    d, ov = [], []
    for i in (0, 2, 4):
        g = max(a[i] - b[i + 1], b[i] - a[i + 1])
        d.append(max(g, 0.0)); ov.append(g)
    if all(g < 0 for g in ov):
        return max(ov)
    return math.sqrt(sum(x * x for x in d))


# ---------------------------------------------------------------- path builder
class Path2:
    """centre line in the XZ plane, as a list of (s0, s1, x0, z0, x1, z1) chords of at most 0.05 mm"""

    def __init__(self, x, z, ang, rotated):
        self.x, self.z, self.a, self.s, self.rot = x, z, ang, 0.0, rotated
        self.ch = []
        self.marks = []

    def mark(self, name):
        self.marks.append((name, round(self.s, 3), round(self.x, 3), round(self.z, 3)))

    def line(self, L):
        n = max(1, int(math.ceil(L / 0.05)))
        for i in range(n):
            x1 = self.x + math.cos(self.a) * L / n
            z1 = self.z + math.sin(self.a) * L / n
            self.ch.append((self.s, self.s + L / n, self.x, self.z, x1, z1))
            self.x, self.z, self.s = x1, z1, self.s + L / n

    def arc(self, R, sweep_deg):
        """turn by sweep (+ = counter-clockwise in the XZ plane seen from -Y) on a centre-line radius R"""
        sw = math.radians(sweep_deg)
        sg = 1 if sw > 0 else -1
        cx = self.x + R * math.cos(self.a + sg * math.pi / 2)
        cz = self.z + R * math.sin(self.a + sg * math.pi / 2)
        phi0 = self.a - sg * math.pi / 2
        L = abs(sw) * R
        n = max(2, int(math.ceil(L / 0.05)))
        for i in range(n):
            p1 = phi0 + sw * (i + 1) / n
            x1, z1 = cx + R * math.cos(p1), cz + R * math.sin(p1)
            self.ch.append((self.s, self.s + L / n, self.x, self.z, x1, z1))
            self.x, self.z, self.s = x1, z1, self.s + L / n
        self.a += sw

    def boxes(self, s_max=None):
        out = []
        for s0, s1, x0, z0, x1, z1 in self.ch:
            if s_max is not None and s0 >= s_max:
                break
            sm = (s0 + s1) / 2
            y0, y1 = width_at(sm, self.rot)
            h = thick_at(sm) / 2
            out.append((sm, (min(x0, x1) - h, max(x0, x1) + h, y0, y1, min(z0, z1) - h, max(z0, z1) + h)))
        return out


def zone_of(s):
    if s < CABLE["neck_start"]:
        return "wide"
    if s < CABLE["total"] - CABLE["stiff_len"]:
        return "neck"
    return "stiff"


def report(label, cab, obstacles, skip=()):
    """per (cable zone, obstacle): smallest free space"""
    best = {}
    for s, b in cab:
        z = zone_of(s)
        for o in obstacles:
            if o[0] in skip:
                continue
            g = box_gap(b, o[2:])
            k = (z, o[0])
            if k not in best or g < best[k][0]:
                best[k] = (g, s)
    print(f"  -- {label}: smallest free space, cable run x neighbour (negative = overlap depth), only pairs under 1.0 mm")
    worst = None
    for (z, name), (g, s) in sorted(best.items(), key=lambda kv: kv[1][0]):
        if g < 1.0:
            print(f"     {z:5s} x {name:13s} {g:+.3f} mm at s {s:.2f}")
        if worst is None or g < worst[0]:
            worst = (g, z, name)
    return worst


def plan_overlap(cab, zone):
    """area of the zone (x0,x1,y0,y1) covered in plan by the cable pieces (union over X strips)"""
    xs = sorted({round(b[0], 4) for _, b in cab} | {round(b[1], 4) for _, b in cab} | {zone[0], zone[1]})
    area = 0.0
    for xa, xb in zip(xs, xs[1:]):
        xm = (xa + xb) / 2
        if not (zone[0] <= xm <= zone[1]):
            continue
        ys = [(b[2], b[3]) for _, b in cab if b[0] <= xm <= b[1]]
        if not ys:
            continue
        lo = max(min(y[0] for y in ys), zone[2]); hi = min(max(y[1] for y in ys), zone[3])
        if hi > lo:
            area += (xb - xa) * (hi - lo)
    return area


def j1_box(face, x_front, direction, yc):
    """closed housing of J1 (catalog p3: body 3.0, leads 0.05 on the FPC side and 0.15 on the lever side, 6.1 wide, 0.9 +-0.1 high)
    direction: +1 when the cable enters moving +X, -1 when it enters moving -X. x_front = housing front face (FPC side)."""
    xa = x_front - direction * 0.05
    xb = x_front + direction * (3.0 + 0.15)
    x0, x1 = min(xa, xb), max(xa, xb)
    if face == "under":
        return ("J1_NEW", "under", x0, x1, yc - 3.05, yc + 3.05, ZTOP - 1.0, ZTOP)
    return ("J1_NEW", "screen", x0, x1, yc - 3.05, yc + 3.05, Z_BD1 + 0.02, Z_BD1 + 0.02 + 1.0)


results = []
print()
# ================================================================= LAYOUT A1: hand end, down the end wall, under the board end into J1 as placed
print("=== LAYOUT A1: hand end (screen as today), stock cable down the end wall into J1 at its place (-11.65, -0.15, turn 270, under face)")
j1 = [p for p in parts if p[0] == "J1"][0]
x_j1_front = j1[2] + 0.05                      # housing front face (courtyard 6.1 x 3.6 is wider than the housing by 0.125 per side)
x_fpc_end = x_j1_front + 1.45                  # catalog p3 detail: FPC inserted (1.45) from the front face
z_entry = ZTOP - 0.35 - 0.10                   # catalog p3 detail: FPC bottom (0.35) above the board face, 0.2 thick: centre 0.45 below
z_ledge = Z_SC0 + LOWER_GLASS + T / 2
p = Path2(-X_PANEL, z_ledge, math.pi, False)
p.mark("panel end")
p.arc(RC, 90)                                  # turn down (seen from -Y: moving -X, turning toward -Z is counter-clockwise)
p.line(max(0.0, (z_ledge - RC) - (z_entry + RC)))
p.arc(RC, 90)                                  # turn to +X
p.line(x_fpc_end - p.x)
p.mark("FPC end at J1")
need = p.s
print(f"  path panel end -> J1 FPC end: {need:.3f} mm; the stock cable is {CABLE['total']} mm: {CABLE['total'] - need:.3f} mm left over with no place drawn")
print(f"  width at the J1 entry (s {need - 1.45:.2f}): {width_at(need - 1.45, False)[1] - width_at(need - 1.45, False)[0]:.3f} mm; J1 takes {CABLE['neck_w']} "
      f"(catalog p5 F 4.8 for 15 contacts); the neck starts at s {CABLE['neck_start']}")
pocket_x = X_PANEL + RC + T / 2 + 0.05
print(f"  end pocket needed: X {-pocket_x:.3f} to {-X_POCKET:.3f}, width {CABLE['wide_w'] + 0.4:.2f} (cable + 0.20 each side) "
      f"against the model's tail pocket 0.55 x 5.4 (thin.py line 467); wall left to the skin {X_SKIN - pocket_x:.3f}")
cab = p.boxes()
obst = [q for q in parts if q[1] in ("under", "zone", "body")] + [PCB]
w = report("A1", cab, obst, skip=("J1",))
ov = plan_overlap(cab, (-13.60, -8.75, 3.10, 6.30))
ovr = plan_overlap(cab, (-14.80, -8.60, 2.05, 7.375))
print(f"  plan area of the antenna copper-free zone covered by cable: {ov:.3f} mm2; of the resin radio corner: {ovr:.3f} mm2")
results.append(("A1", w, ov))

# ================================================================= LAYOUT A2: hand end, bend-back under the panel, J1 on the screen face
print()
print("=== LAYOUT A2: hand end (screen as today), cable bent back under the panel, J1 on the board's screen face (block grows)")
z_entry2 = Z_BD1 + 0.02 + 0.35 + 0.10            # FPC centre 0.45 above the screen face pad
dh = (Z_BD1 + 0.02 + 1.0 + 0.05) - Z_SC0         # panel underside must clear J1 max height 1.0 by 0.05
z_ledge2 = Z_SC0 + dh + LOWER_GLASS + T / 2
p = Path2(-X_PANEL, z_ledge2, math.pi, False)
p.arc(RC, 90)
drop = (z_ledge2 - RC) - (z_entry2 + RC)
p.line(max(0.0, drop))
p.arc(RC, 90)
p.line(CABLE["total"] - p.s)
cab = p.boxes()
ov = plan_overlap(cab, (-13.60, -8.75, 3.10, 6.30))
print(f"  block grows {dh:.3f} mm; straight drop between the two folds {drop:.3f} mm (negative = the folds do not fit)")
print(f"  plan area of the antenna copper-free zone (4.85 x 3.20 = 15.52 mm2) covered by the cable: {ov:.3f} mm2; "
      f"cable underside over the zone: Z {min(b[4] for s, b in cab if -13.6 <= (b[0] + b[1]) / 2 <= -8.75):.3f}, zone top Z {Z_BD1}")
results.append(("A2", None, ov))

# ================================================================= LAYOUT B: screen turned, fingertip end wall, two layers under the board, J1 under face
print()
print("=== LAYOUT B: screen turned 180 deg, cable down the fingertip end wall, two flat layers under the board, J1 under face at the fingertip end")
z1 = Z_FLOOR + T / 2                             # layer 1 on the floor
z2 = ZTOP - 0.35 - 0.10                          # layer 2 at the J1 entry height
rc2 = (z2 - z1) / 2
print(f"  fold between the two layers: centre radius {rc2:.3f}, inner radius {rc2 - T / 2:.3f} (start value {R_IN}): "
      f"{'OK' if rc2 - T / 2 >= R_IN - 1e-9 else 'TOO TIGHT by %.3f' % (R_IN - (rc2 - T / 2))}")
x_j1_front_B = 13.6 - 0.10 - 0.15 - 3.0           # housing back (lever side, leads 0.15) 0.10 inside the board end
x_end_B = x_j1_front_B + 1.45
p = Path2(X_PANEL, Z_SC0 + LOWER_GLASS + T / 2, 0.0, True)
p.arc(RC, -90)
p.line(max(0.0, (p.z - RC) - (z1 + RC)))
p.arc(RC, -90)                                    # now moving -X on the floor
s_l1 = p.s
x_l1 = p.x
# solve the layer length a so that the cable ends at x_end_B: path = s_l1 + a + pi*rc2 + (x_end_B - (x_l1 - a))
a = (CABLE["total"] - s_l1 - math.pi * rc2 - (x_end_B - x_l1)) / 2
p.line(a)
p.arc(rc2, -180)                                  # fold up and back to +X
p.line(x_end_B - p.x)
print(f"  layer length {a:.3f}: layer 1 X {x_l1 - a:.3f}..{x_l1:.3f} on the floor, layer 2 X {x_l1 - a:.3f}..{x_end_B:.3f}; "
      f"J1 housing X {x_j1_front_B - 0.05:.3f}..{x_j1_front_B + 3.15:.3f}; cable end s {p.s:.3f}")
cab = p.boxes()
j1B = j1_box("under", x_j1_front_B, +1, -(CABLE["wide_y0"] + CABLE["wide_y1"]) / 2)
obst = [q for q in parts if q[1] in ("under", "zone", "body", "band") and q[0] != "J1"] + [PCB]
w = report("B cable", cab, obst)
print("  -- B: the new J1 housing against the board parts (negative = overlap)")
hits = []
for q in parts:
    if q[1] == "under" and q[0] != "J1":
        g = box_gap(j1B[2:], q[2:])
        if g < 0.10:
            hits.append((q[0], g))
for n_, g in sorted(hits, key=lambda h: h[1]):
    print(f"     J1_NEW x {n_:6s} {g:+.3f} mm")
# parts that the two wide layers displace: every under-face part whose box meets a cable piece
blocked = sorted({q[0] for q in obst if q[1] == "under" for s, b in cab if box_gap(b, q[2:]) < 0.05})
area_bl = sum((q[3] - q[2]) * (q[5] - q[4]) for q in parts if q[0] in blocked)
strip = (13.6 - (x_l1 - a)) * 12.6
print(f"  under-face parts the cable meets: {len(blocked)} ({', '.join(blocked)}); their courtyard boxes {area_bl:.2f} mm2")
print(f"  board strip under the two wide layers: X {x_l1 - a:.3f}..13.6 x 12.6 = {strip:.2f} mm2 (only parts under {ZTOP - (z2 + T / 2) - 0.05:.2f} mm high can stay there)")
print(f"  area use with that strip lost: 281.3 / ({342.2:.1f} - {strip:.2f}) = {281.3 / (342.2 - strip) * 100:.1f} percent (ring-board-plan.md R2.4: 281.3 of 342.2 today)")
results.append(("B", w, None))

# ================================================================= LAYOUT C: screen turned, bend-back under the panel, J1 on the screen face
print()
print("=== LAYOUT C: screen turned 180 deg, cable bent back under the panel at the fingertip end, J1 on the board's screen face (block grows)")
dhC = (Z_BD1 + 0.02 + 1.0 + 0.05) - Z_SC0
z_ledgeC = Z_SC0 + dhC + LOWER_GLASS + T / 2
z_entryC = Z_BD1 + 0.02 + 0.35 + 0.10
p = Path2(X_PANEL, z_ledgeC, 0.0, True)
p.arc(RC, -90)
dropC = (z_ledgeC - RC) - (z_entryC + RC)
p.line(max(0.0, dropC))
p.arc(RC, -90)
s_flat = p.s
x_endC = p.x - (CABLE["total"] - p.s)
p.line(CABLE["total"] - p.s)
x_frontC = x_endC + 1.45
yc = -(CABLE["wide_y0"] + CABLE["wide_y1"]) / 2
j1C = j1_box("screen", x_frontC, -1, yc)
print(f"  block grows {dhC:.3f} mm (panel underside {Z_SC0 + dhC:.3f}: J1 1.0 max on the screen face pad at {Z_BD1 + 0.02:.2f} + 0.05)")
print(f"  straight drop between the folds {dropC:.3f} mm ({'fits' if dropC >= 0 else 'folds do not fit: block must grow %.3f more' % (-dropC)})")
print(f"  cable flat from s {s_flat:.3f} at Z {z_entryC:.3f}; FPC end X {x_endC:.3f}; J1 on the screen face, turn: opening toward +X, "
      f"housing X {j1C[2]:.3f}..{j1C[3]:.3f}, Y {j1C[4]:.3f}..{j1C[5]:.3f}, centre ({(j1C[2] + j1C[3]) / 2:.3f}, {yc:.3f})")
pocketC = X_PANEL + RC + T / 2 + 0.05
# analytic check of the first fold against the panel's end corner (X_PANEL, ledge top): the fold's inner face has radius R_IN about
# (X_PANEL, z_ledgeC - RC) and runs at X >= X_PANEL, so its least distance to the corner is R_IN - (RC - T/2) = 0 at s = 0 (the cable
# leaves the ledge at its edge) and the end face X = X_PANEL is never crossed. A box piece of the first 0.05 mm can show a small
# negative value there: a chord's box grows T/2 to both sides.
print(f"  fold 1 inner face to the panel end corner (analytic): {R_IN - (RC - T / 2):.3f} mm at s 0, then growing; inner face X >= {X_PANEL} everywhere")
rmax_C = ((z_ledgeC) - (z_entryC)) / 2 - T / 2
rmax_C2 = ((z_ledgeC) - (Z_BD1 + 0.02 + T / 2)) / 2 - T / 2
print(f"  largest inner fold radius C allows at this height: {rmax_C:.3f} (cable straight at the J1 entry height) or {rmax_C2:.3f} "
      f"(cable down on the board, then an S-rise of 0.40 in the neck to the J1 entry)")
print(f"  fingertip end pocket: X {X_POCKET:.3f} to {pocketC:.3f}, Y +-{(CABLE['wide_w'] + 0.4) / 2:.2f}, wall left to the skin {X_SKIN - pocketC:.3f} "
      f"(body.md wall rule: least metal 0.30 by analogy with the motor pocket rule wall_min, thin.py line 83)")
cab = p.boxes()
# panel as two glass plates: lower glass full length, upper glass without the 2.951 ledge (screen turned: ledge at the fingertip end)
panelC = ("PANEL_LOWER", "screen", -X_PANEL, X_PANEL, -6.4, 6.4, Z_SC0 + dhC, Z_SC0 + dhC + LOWER_GLASS)
panelC2 = ("PANEL_UPPER", "screen", -X_PANEL, X_PANEL - 2.951, -6.4, 6.4, Z_SC0 + dhC + LOWER_GLASS, Z_SC0 + dhC + 0.8)
obstC = [q for q in parts if q[1] in ("screen", "zone")] + [PCB, panelC, panelC2, j1C]
w = report("C cable", cab, obstC, skip=("J1_NEW",) + tuple(q[0] for q in parts if q[0].startswith("TP")))
print("  -- C: the new J1 housing on the screen face against the test pads and the panel")
for q in parts + [panelC, panelC2]:
    if q[1] == "screen" and q[0] != "J1_NEW":
        g = box_gap(j1C[2:], q[2:])
        if g < 0.30:
            print(f"     J1_NEW x {q[0]:6s} {g:+.3f} mm")
tp_under = sorted({q[0] for q in parts if q[0].startswith("TP") for s, b in cab if box_gap(b, q[2:]) < 0.0 or
                   (b[0] < q[3] and b[1] > q[2] and b[2] < q[5] and b[3] > q[4])})
print(f"  test pads under the cable in plan (copper, no height; reachable only before the panel goes on): {len(tp_under)} {tp_under}")
ovC = plan_overlap(cab + [(0, j1C[2:])], (-13.60, -8.75, 3.10, 6.30))
dz = min(box_gap(b, (-13.60, -8.75, 3.10, 6.30, Z_BD0, Z_BD1)) for s, b in cab + [(0, j1C[2:])])
print(f"  antenna copper-free zone: covered in plan {ovC:.3f} mm2; least distance from cable or J1 to the zone {dz:.3f} mm; "
      f"to ANT1's body {min(box_gap(b, [q for q in parts if q[0] == 'ANT1'][0][2:]) for s, b in cab + [(0, j1C[2:])]):.3f} mm")
u4 = [q for q in parts if q[0] == "U4"][0]
print(f"  J1 centre to U4 centre (screen supply chip, other face): {math.hypot((j1C[2] + j1C[3]) / 2 - (u4[2] + u4[3]) / 2, yc - (u4[4] + u4[5]) / 2):.2f} mm "
      f"(today J1 (-11.65, -0.15) to U4: {math.hypot(-11.65 - (u4[2] + u4[3]) / 2, -0.15 - (u4[4] + u4[5]) / 2):.2f} mm)")
results.append(("C", w, ovC))

# ================================================================= LAYOUT C-thin: as C but the panel only lifted for the cable, neck down a board slot to J1 under face
print()
print("=== LAYOUT C-thin: screen turned, bend-back under the panel in a gap of t + 0.05, neck down a board slot to J1 on the under face")
gap = T + 0.05
dhT = gap - (Z_SC0 - Z_BD1)
z_ledgeT = Z_SC0 + dhT + LOWER_GLASS + T / 2
z_gapT = Z_BD1 + 0.025 + T / 2
rcT = (z_ledgeT - z_gapT) / 2
print(f"  block grows {dhT:.3f}; the bend-back is one half turn between Z {z_ledgeT:.3f} and {z_gapT:.3f}: centre radius {rcT:.3f}, "
      f"inner {rcT - T / 2:.3f} (start value {R_IN}): {'OK' if rcT - T / 2 >= R_IN - 1e-9 else 'TOO TIGHT by %.3f' % (R_IN - (rcT - T / 2))}")
p = Path2(X_PANEL, z_ledgeT, 0.0, True)
p.arc(rcT, -180)
x_neck = p.x - (CABLE["neck_start"] - p.s)
x_stiff = p.x - (CABLE["total"] - CABLE["stiff_len"] - p.s)
print(f"  in the gap the neck starts at X {x_neck:.3f}; the stiffened end starts at X {x_stiff:.3f}: the neck must turn down through the board "
      f"between X {x_stiff:.3f} and {x_neck:.3f} (slot about 5.2 x 0.6), J1 under it")
slot = ("SLOT", "board", x_stiff, x_neck, yc - 2.6, yc + 2.6, Z_BD0, Z_BD1)
j1T = j1_box("under", x_stiff - 0.6, -1, yc)
hitsT = []
for q in parts:
    if q[1] == "under" and q[0] != "J1":
        # plan gap (X, Y only): the slot cuts the board through its full thickness, so any part whose courtyard meets it in plan must move
        g1 = box_gap(slot[2:6] + (0.0, 1.0), q[2:6] + (0.0, 1.0))
        g2 = box_gap(j1T[2:], q[2:])
        if min(g1, g2) < 0.05:
            hitsT.append((q[0], round(g1, 3), round(g2, 3)))
print(f"  under-face parts hit by the slot in plan or by J1 there (slot plan gap, J1 gap; negative = overlap depth on the least axis): {len(hitsT)}")
for h in sorted(hitsT, key=lambda h: min(h[1], h[2])):
    print(f"     {h[0]:6s} slot {h[1]:+.3f}  J1 {h[2]:+.3f}")
results.append(("C-thin", (min(min(h[1], h[2]) for h in hitsT) if hitsT else 9, "", ""), None))

# ================================================================= D (computed only, not laid against the parts): a chamber beyond the fingertip end
print()
print("=== D (computed only): screen turned, cable straight out of the ledge into a chamber added beyond the fingertip end of the block, one half turn down, back under the board into J1 at the board's fingertip end (under face)")
z_ledgeD = Z_SC0 + LOWER_GLASS + T / 2
z_entryD = ZTOP - 0.35 - 0.10
dropD = (z_ledgeD - z_entryD) - 2 * RC
x_fpc_D = 13.6 - 0.05 - 1.45
aD = (CABLE["total"] - math.pi * RC - dropD - (X_PANEL - x_fpc_D)) / 2
chamber_end = X_PANEL + aD + RC + T / 2 + 0.05
print(f"  straight out {aD:.3f}, turn centre radius {RC:.3f}, drop {dropD:.3f}; chamber to X {chamber_end:.3f}: block longer by {chamber_end - X_POCKET:.3f} mm "
      f"at the fingertip end (outside shape), and J1 at the board's fingertip end meets the parts listed under B")

print()
for r in results:
    print(f"SUMMARY {r[0]}: worst pair {r[1]}; antenna zone covered {r[2]}")
print(f"RESULT done r_in={R_IN} t={T}")
