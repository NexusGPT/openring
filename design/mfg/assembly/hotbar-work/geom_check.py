"""Geometry check of the hot-bar joint (hotbar-joint.md, Q2 and Q5). Plain Python 3, reads only.
usage: python3 -I geom_check.py <dumps_dir> <thin.py> <band_geom.py>
Inputs:
  <dumps_dir>/flexK-usN-dump.txt  written by dump_boards.py from copies of the 14 band boards (outline segments, stiffener, lands)
  <dumps_dir>/ring-dump.txt       written by dump_boards.py from a copy of ring.kicad_pcb (part boxes, J_BAND pads)
  thin.py                         the model's numbers, read as text (P dict), never run
  band_geom.py                    the band designer's formula of the finished path per size (pure math), loaded from its path
Prints per size and tail: flat length, finished path, free length, foot width against slot width, the lift and tilt the free
length allows, and a verdict. Then the fixed clearances of the fold and the parts within 3 mm of the J_BAND lands.
"""
import sys, os, re, math, importlib.util

dumps, thin_path, bg_path = sys.argv[1], sys.argv[2], sys.argv[3]
thin = open(thin_path).read()


def P(name):
    m = re.search(r"\b" + name + r"=\(?([-0-9.]+)(?:,\s*([-0-9.]+))?\)?", thin)
    if not m:
        raise SystemExit(f"thin.py has no {name}")
    return (float(m.group(1)), float(m.group(2))) if m.group(2) and thin[m.start():m.end()].count("(") else float(m.group(1))


slot_w, tail_y, tail_w = P("slot_w"), P("tail_y"), P("tail_w")
fold_r, t_fin, joint, pad_t = P("fold_r_in"), P("flex_fin"), P("joint"), P("pad_t")
stiff_t, under, gap, board_t = P("stiff_t"), P("under"), P("gap"), P("board_t")
foot_x, foot_y1 = P("foot_x"), P("foot_y1")
spec = importlib.util.spec_from_file_location("band_geom_ro", bg_path)
bg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bg)
Z_BD0 = bg.Z_BD0                      # board underside 1.45 (band_geom.py line 33, from the STEP files)
Z_FLOOR = Z_BD0 - under - gap         # thin.py lines 335 and 336: Z_UB0 = Z_BD0 - under, Z_FLOOR = Z_UB0 - gap
Z_LAND = Z_BD0 - pad_t
Z_TAIL_TOP = Z_LAND - joint
RC = fold_r + t_fin / 2
Z_ARC0 = Z_TAIL_TOP - t_fin / 2 - RC
LF = (tail_y - RC) - foot_y1
LARC = math.pi / 2 * RC
print(f"inputs: slot_w {slot_w} tail_y {tail_y} tail_w {tail_w} fold_r_in {fold_r} flex_fin {t_fin} joint {joint} pad_t {pad_t} "
      f"stiff_t {stiff_t} under {under} gap {gap} foot_x {foot_x} foot_y1 {foot_y1} Z_BD0 {Z_BD0}")
print(f"heights: floor top Z {Z_FLOOR:.3f}, board land face Z {Z_LAND:.3f}, foot top Z {Z_TAIL_TOP:.3f}, fold starts Z {Z_ARC0:.3f}")
gap_land_floor = Z_LAND - Z_FLOOR
back_gap = Z_TAIL_TOP - t_fin - stiff_t - Z_FLOOR
u_loop = 2 * fold_r + 2 * t_fin
above_floor = (Z_ARC0 - Z_FLOOR) + LARC + LF
print(f"fold: centre radius {RC:.3f}, arc {LARC:.3f}, flat foot {LF:.3f}; ribbon above the floor top in the finished ring "
      f"{Z_ARC0 - Z_FLOOR:.3f} + {LARC:.3f} + {LF:.3f} = {above_floor:.3f}")
print(f"CLEARANCE land face to floor {gap_land_floor:.3f}; foot back (stiffener) to floor {back_gap:.3f}; "
      f"a 180 degree loop at the fold radius needs {u_loop:.3f} -> slack store under the board: {'YES' if u_loop <= gap_land_floor else 'NO'}")

# twist-free poses: the board may only turn about an axis parallel to X (see hotbar-joint.md 2.2).
# 180 degrees: parts face up, but board +Y goes to -Y: J_BAND_B lies over the FLEX1 slot (the swap).
# 90 degrees, hinged at the FLEX1 side: FLEX1 rises straight from its slot and its foot lies on the standing board.
rise = (Z_ARC0 - Z_FLOOR) + LARC                     # ribbon from the floor top to the foot's outer end, finished ring
z_foot_outer = Z_FLOOR + rise                        # FLEX1 straight up: foot outer end (u 1.745, board |Y| 5.145) at this Z
z_of = lambda yb: z_foot_outer + (yb - (-(tail_y - RC)))   # board y (negative side) -> Z in the standing pose
board_half = P("board_y") / 2
cav_half = (P("scr_y") + 0.1) / 2                    # thin.py line 528: pocket_main = rbox(scr_x + 0.1, scr_y + 0.1, ...)
screen_face_y = tail_y + t_fin / 2 + joint + pad_t + board_t
jb_lo, jb_hi = z_of(foot_y1), z_of(tail_y - RC)      # J_BAND_B foot (board y +3.4 .. +5.145) in that pose
need2 = (jb_hi - Z_FLOOR)                            # FLEX2 would at least have to rise this far from its slot top, then cross the board
print(f"POSE 90 deg (board on its -Y edge, FLEX1 straight up): board bottom edge Z {z_of(-board_half):.3f} (floor {Z_FLOOR:.3f}); "
      f"screen face at |Y| {screen_face_y:.3f}, cavity wall at |Y| {cav_half:.3f}: gap {cav_half - screen_face_y:.3f}; "
      f"J_BAND_B foot then at Z {jb_lo:.3f} to {jb_hi:.3f}: FLEX2 needs at least {need2:.3f} of rise plus the crossing of the board, against a free length of 0")
rows = []
for k in (1, 2):
    for us in bg.SIZES:
        f = os.path.join(dumps, f"flex{k}-us{us}-dump.txt")
        segs = []
        stiff = []
        for line in open(f):
            m = re.match(r"edge Line ([-0-9.]+),([-0-9.]+) -> ([-0-9.]+),([-0-9.]+)", line)
            if m:
                segs.append(tuple(float(v) for v in m.groups()))
            m = re.match(r"User.1 shape Line box x ([-0-9.]+) ([-0-9.]+) y ([-0-9.]+) ([-0-9.]+)", line)
            if m:
                stiff.append(tuple(float(v) for v in m.groups()))
        xs = [s[0] for s in segs] + [s[2] for s in segs]
        x0, x1 = min(xs), max(xs)
        flat = x1 - x0

        def width_at(x):
            ys = []
            for (ax, ay, bx, by) in segs:
                if min(ax, bx) - 1e-9 <= x <= max(ax, bx) + 1e-9 and abs(bx - ax) > 1e-9:
                    ys.append(ay + (by - ay) * (x - ax) / (bx - ax))
            return max(ys) - min(ys) if len(ys) >= 2 else float("nan")
        foot_w = width_at(x0 + 0.8)          # middle of the foot (u 0 to 1.745)
        neck_w = width_at(x0 + 3.5)          # past the fold taper (u 2.931)
        # stiffener near the foot: the User.1 lines with x < x0 + 2 (line width 0.05: centre lines are the box middles)
        sx = [((a + b) / 2) for (a, b, c, d) in stiff if b < x0 + 2.0 and (b - a) < 0.1]
        sy = [((c + d) / 2) for (a, b, c, d) in stiff if b < x0 + 2.0 and (d - c) < 0.1]
        st_len = max(sx) - min(sx) if sx else float("nan")
        st_w = max(sy) - min(sy) if sy else float("nan")
        s = bg.Size(us)
        path = bg.FOOT_EXTRA + (s.path1 if k == 1 else s.path2)
        free = flat - path
        lift = max(free, 0.0)
        # tilt about an X axis through the OTHER tail's fold line (that tail keeps its length): this foot edge, 2 x (tail_y - RC) away, rises by that distance x sin(theta)
        y_edge = 2 * (tail_y - RC)
        tilt = math.degrees(math.asin(min(lift / y_edge, 1.0))) if lift > 0 else 0.0
        passes = foot_w <= slot_w
        verdict_lift = "board can be lifted %.3f mm" % lift if lift >= 0.05 else "NO LIFT (free length under the 0.05 length tolerance)"
        verdict = ("FOOT PASSES SLOT" if passes else "FOOT DOES NOT PASS SLOT") + "; " + verdict_lift
        rows.append((k, us, flat, path, free, foot_w, neck_w, st_w, st_len, lift, tilt, verdict))
        print(f"FLEX{k} US {us}: flat length {flat:.4f} (outline x {x0:.4f} to {x1:.4f}); finished path {path:.4f}; free length {free:+.4f}; "
              f"foot width {foot_w:.3f}, neck width {neck_w:.3f}, stiffener (centre lines) {st_w:.3f} x {st_len:.3f}; slot {slot_w:.3f}; "
              f"allowed lift {lift:.3f} mm, allowed tilt {tilt:.2f} deg; VERDICT {verdict}")

# parts near the J_BAND lands (plan distance from the part's body box to the nearest land rectangle), both faces
ring = open(os.path.join(dumps, "ring-dump.txt")).read().splitlines()
parts, lands = [], []
mode = None
for line in ring:
    if line.startswith("ref,side"):
        mode = "parts"; continue
    if line.startswith("pads of J_BAND"):
        mode = "pads"; continue
    if line.startswith("board outline"):
        mode = None; continue
    if mode == "parts":
        r, side, x, y, rot, src, a, b, c, d = line.split(",")
        parts.append((r, side, float(x), float(y), src, float(a), float(b), float(c), float(d)))
    elif mode == "pads":
        ref, num, net, x, y, sx, sy, lay = line.split(",")
        x, y, sx, sy = float(x), float(y), float(sx), float(sy)
        lands.append((ref, num, net, x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2, lay))


def rect_gap(a, b):
    dx = max(a[0] - b[1], b[0] - a[1], 0.0)
    dy = max(a[2] - b[3], b[2] - a[3], 0.0)
    return math.hypot(dx, dy)


print(f"J_BAND lands read: {len(lands)}; layers of each: {sorted(set(l[7] for l in lands))}")
print("parts within 3.0 mm (plan) of any J_BAND land: ref, face, box source, nearest land, distance mm (model X = file x - 100, Y = file y - 100)")
near = []
for (r, side, x, y, src, a, b, c, d) in parts:
    if r.startswith("J_BAND"):
        continue
    best = min(((rect_gap((a, b, c, d), (l[3], l[4], l[5], l[6])), l[0] + " " + l[1]) for l in lands))
    if best[0] <= 3.0:
        near.append((best[0], r, side, src, best[1]))
for dist, r, side, src, land in sorted(near):
    print(f"NEAR {r},{'parts face F.Cu' if side == 'F' else 'screen face B.Cu'},{src},{land},{dist:.3f}")
# hot-bar blade over each foot (plan): which parts of the parts face does a blade of width w (along X, centred on the foot) and
# length along Y over the stiffener (or the whole foot) overlap?  Blade centred at X -2.25 (footprint origin, band-interface.md line 58).
fx0, fx1 = foot_x
cx = (fx0 + fx1) / 2
for w, (y0, y1), name in ((3.0, (3.45, 5.05), "3.0 x stiffener (band-interface.md line 137)"), (3.0, (foot_y1, tail_y - RC), "3.0 x whole foot"),
                          (2.5, (3.45, 5.05), "2.5 x stiffener"), (2.5, (foot_y1, tail_y - RC), "2.5 x whole foot")):
    hits = []
    for sg in (1, -1):
        blade = (cx - w / 2 + 100, cx + w / 2 + 100, min(sg * y0, sg * y1) + 100, max(sg * y0, sg * y1) + 100)
        for (r, side, x, y, src, a, b, c, d) in parts:
            if side != "F" or r.startswith("J_BAND"):
                continue
            ox = min(blade[1], b) - max(blade[0], a)
            oy = min(blade[3], d) - max(blade[2], c)
            if ox > 0 and oy > 0:
                hits.append(f"{r} (overlap {ox:.3f} x {oy:.3f})")
            else:
                g = rect_gap(blade, (a, b, c, d))
                if g < 0.30:
                    hits.append(f"{r} clear by {g:.3f}")
    print(f"BLADE {name}: X {cx - w / 2:.3f} to {cx + w / 2:.3f}: " + ("; ".join(hits) if hits else "no part within 0.30"))
print(f"RESULT geometry: tails checked {len(rows)}; foot passes slot {sum(1 for r in rows if r[5] <= slot_w)} of {len(rows)}; "
      f"lift possible {sum(1 for r in rows if r[9] >= 0.05)} of {len(rows)}; parts within 3 mm {len(near)}")

# ======================= OPTION D: joint on the board's SCREEN face, made in place from above (lead's message 2026-11-13) =======================
# Rules of the band boards (band-interface.md line 15): copper to edge 0.30, land to land 0.15; tail land 0.30 x 0.30 (line 91).
# Board rules (design/ecad/ring/pcb/fab/stackup.txt line 19): gap 0.065 minimum, 0.075 used by the design.
EDGE, L2L, LAND = 0.30, 0.15, 0.30
D_FOOT_MAX = slot_w - 2 * 0.15        # 0.15 at each end of the slot (lead-decisions.md line 37): 1.80
print(f"D FOOT: widest foot that passes the slot with 0.15 each side = {slot_w:.2f} - 2 x 0.15 = {D_FOOT_MAX:.3f}")
J1 = [p for p in parts if p[0] == "J1"][0]
j1_y = max(abs(J1[7] - 100), abs(J1[8] - 100))       # J1 body reaches |Y| this far (screen face)
d_foot_end = j1_y + 0.10                               # foot end 0.10 clear of J1 in plan [START]
d_flat_avail = (tail_y - RC) - d_foot_end              # flat run on top of the board, from the fold to the foot end
print(f"D LENGTH AVAILABLE on the screen face: fold ends at |Y| {tail_y - RC:.3f}, J1 reaches |Y| {j1_y:.3f}, foot end at |Y| {d_foot_end:.3f}: flat run {d_flat_avail:.3f}")
grids = []
for cols, px in ((3, 0.51), (3, 0.45), (2, 0.51)):
    for rows_, py in ((3, 0.45), (3, 0.51), (4, 0.45), (4, 0.51), (3, 0.90), (4, 0.90)):
        if cols * rows_ < 8:
            continue
        width = (cols - 1) * px + LAND + 2 * EDGE
        length = (rows_ - 1) * py + LAND + EDGE          # copper to the foot end edge; the fold side carries the lines on
        ok_w = width <= D_FOOT_MAX + 1e-9 and px - LAND >= L2L - 1e-9
        ok_l = length <= d_flat_avail + 1e-9 and py - LAND >= L2L - 1e-9
        grids.append((cols, px, rows_, py, width, length, ok_w and ok_l))
        print(f"D GRID {cols} columns at {px:.2f} x {rows_} rows at {py:.2f}: foot width {width:.3f} ({'fits' if ok_w else 'FAILS'} {D_FOOT_MAX:.2f}), "
              f"land span plus end margin {length:.3f} ({'fits' if ok_l else 'FAILS'} {d_flat_avail:.3f}); {'GRID FITS' if ok_w and ok_l else 'grid fails'}")
# chosen for the numbers below: 3 x 3 at 0.45 (the only fitting grid with 3 columns); centred on the neck X tail_x
tail_x = P("tail_x")
gcols = [tail_x - 0.45, tail_x, tail_x + 0.45]
grows = [d_foot_end + EDGE + LAND / 2 + k * 0.45 for k in range(3)]
d_lands = [(x - LAND / 2, x + LAND / 2, y - LAND / 2, y + LAND / 2) for x in gcols for y in grows]
print(f"D LANDS (3 x 3 at 0.45, 0.30 x 0.30) X centres {', '.join(f'{x:.3f}' for x in gcols)}; |Y| centres {', '.join(f'{y:.3f}' for y in grows)}")
# heights: foot ON TOP of the board, lands down, on B.Cu lands
Z_TOP = Z_BD0 + board_t
z_foot_c = Z_TOP + pad_t + joint + t_fin / 2
z_arc_c = z_foot_c - RC                                # fold centre height; centre |Y| = tail_y - RC as today
d_extra = (z_foot_c - (Z_TAIL_TOP - t_fin / 2))         # the neck is longer by the rise of the foot centre line; fold and foot length as today
print(f"D HEIGHTS: board top Z {Z_TOP:.3f}; foot centre line Z {z_foot_c:.3f} (today {Z_TAIL_TOP - t_fin / 2:.3f}); fold centre Z {z_arc_c:.3f}, |Y| {tail_y - RC:.3f}")
print(f"D EXTRA LENGTH per tail = {z_foot_c:.3f} - {Z_TAIL_TOP - t_fin / 2:.3f} = {d_extra:.3f} (board {board_t} + 2 x (land {pad_t} + joint {joint}) + flex {t_fin}); same at every size")
# notch: where the ribbon (inner and outer face of the fold) crosses the board's thickness
def fold_y(z, r):
    dz = z - z_arc_c
    return (tail_y - RC) + math.sqrt(max(r * r - dz * dz, 0.0))
r_in, r_out = fold_r, fold_r + t_fin
y_min = min(fold_y(Z_BD0, r_in), fold_y(Z_TOP, r_in))
y_max = max(fold_y(Z_BD0, r_out), fold_y(Z_TOP, r_out), tail_y + t_fin / 2)
notch_in = y_min - 0.10                                # 0.10 clear [START]
print(f"D NOTCH: inside the board thickness (Z {Z_BD0:.3f} to {Z_TOP:.3f}) the ribbon occupies |Y| {y_min:.3f} to {y_max:.3f}; notch from the edge |Y| {board_half:.2f} "
      f"in to |Y| {notch_in:.3f} ({board_half - notch_in:.3f} deep), X {tail_x - tail_w / 2 - 0.15:.2f} to {tail_x + tail_w / 2 + 0.15:.2f} (neck 1.8 + 0.15 each side, as the slot)")
print(f"D FOLD TOP: outer face of the fold reaches Z {z_arc_c + r_out:.3f}; foot top with stiffener Z {Z_TOP + pad_t + joint + t_fin + stiff_t:.3f}; cavity wall |Y| {cav_half:.3f} against fold outer |Y| {y_max:.3f}: {cav_half - y_max:.3f} clear")
# room above: panel underside = board top + 1.07 (assembly.md line 219); cable of layout C floats 0.40 above the board (screen-cable-study.md line 172)
foot_top = Z_TOP + pad_t + joint + t_fin + stiff_t
print(f"D ROOM ABOVE: foot top {foot_top - Z_TOP:.3f} above the board; panel underside 1.070 above: {1.070 - (foot_top - Z_TOP):.3f} clear; cable plane 0.400 above: {0.400 - (foot_top - Z_TOP):.3f} clear in height")
# cable plan: flat run straight from its end at X -4.833 (s 20) toward +X; neck 4.805 wide (|Y| 2.402) from s 12.497; wide part 12.401 up to s 11.997 (screen-cable-study.md lines 42, 43, 178)
x_of_s = lambda s_: -4.833 + (20.0 - s_)
print(f"D CABLE PLAN: neck (|Y| up to 2.402) from X -4.833 to {x_of_s(12.497):.3f}; wide part (|Y| up to 6.204) from X {x_of_s(11.997):.3f} toward +X; "
      f"lands X {gcols[0] - 0.15:.3f} to {gcols[-1] + 0.15:.3f}, foot |Y| {d_foot_end:.3f} to {tail_y - RC:.3f}: neck clear by {d_foot_end - 2.402:.3f} in Y, wide part clear by {x_of_s(11.997) - (tail_x + tail_w / 2):.3f} in X")
# screen-face parts near the new lands; J1; parts face parts under the support
foot_rects = [(tail_x - tail_w / 2 + 100, tail_x + tail_w / 2 + 100, sg * d_foot_end + 100, sg * (tail_y - RC) + 100) for sg in (1, -1)]
foot_rects = [(a, b, min(c, d), max(c, d)) for (a, b, c, d) in foot_rects]
dl = []
for sg in (1, -1):
    for (a, b, c, d) in d_lands:
        y0, y1 = sorted((sg * c, sg * d))
        dl.append((a + 100, b + 100, y0 + 100, y1 + 100))
nearD = []
for (r, side, x, y, src, a, b, c, d) in parts:
    if r.startswith("J_BAND") or side != "B":
        continue
    g = min(rect_gap((a, b, c, d), l) for l in dl)
    gf = min(rect_gap((a, b, c, d), f) for f in foot_rects)
    if g <= 3.0:
        nearD.append((g, r, gf))
for g, r, gf in sorted(nearD):
    print(f"D NEAR screen face {r}: to the nearest new land {g:.3f}, to the foot outline {gf:.3f}")
ly0, ly1 = grows[0] - LAND / 2 - 0.15, grows[-1] + LAND / 2 + 0.15     # blade and support: the land span plus 0.15 [START]
sup = [(tail_x - tail_w / 2 + 100, tail_x + tail_w / 2 + 100, min(sg * ly0, sg * ly1) + 100, max(sg * ly0, sg * ly1) + 100) for sg in (1, -1)]
for sr in sup:
    print(f"D BLADE X {sr[0]-100:.2f} to {sr[1]-100:.2f}, Y {sr[2]-100:.3f} to {sr[3]-100:.3f}: to J1 body (0.9 high, screen face) {rect_gap(sr, (J1[5], J1[6], J1[7], J1[8])):.3f} in plan")
for sr in sup:
    hits = [(rect_gap((a, b, c, d), sr), r) for (r, side, x, y, src, a, b, c, d) in parts if side == "F" and not r.startswith("J_BAND")]
    hits = sorted(h for h in hits if h[0] < 0.5)
    print(f"D SUPPORT under the board X {sr[0]-100:.2f} to {sr[1]-100:.2f}, Y {sr[2]-100:.2f} to {sr[3]-100:.2f} (parts face): parts within 0.5: "
          + ("; ".join(f"{r} {g:.3f}" for g, r in hits) if hits else "none") + f"; post height floor to board underside {Z_BD0 - Z_FLOOR:.3f}")
d_pass = D_FOOT_MAX <= slot_w - 0.3 + 1e-9
for (k, us, flat, path, free, *_rest) in rows:
    verdict = "length enough as drawn" if free >= d_extra - 1e-9 else f"BOARD MUST GROW by {d_extra - free:.3f}"
    print(f"D FLEX{k} US {us}: free length {free:+.4f} against the extra {d_extra:.3f} needed: {verdict}")
print(f"RESULT option D: foot {D_FOOT_MAX:.2f} passes slot {slot_w:.2f}: {'yes' if d_pass else 'no'}; grids that fit {sum(1 for g in grids if g[6])} of {len(grids)}; "
      f"extra length {d_extra:.3f} per tail; tails long enough as drawn {sum(1 for r in rows if r[4] >= d_extra - 1e-9)} of {len(rows)}; screen face parts within 3 mm {len(nearD)}")
