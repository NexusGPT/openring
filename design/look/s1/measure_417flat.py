#!/usr/bin/env python3
"""Measure the merged417flat exterior from its STEP file (the geometry itself, no number taken from exterior.py).
measure_417flat.py = measure_417.py with the checks the flat top changes (owner card 2026-11-13, "Flat glass, 4.15 mm"):
  check (1) is replaced by check (1f): the top above Z 0 is 4.145 within 0.005 (--flat-top) at the centre, near both long
            edges and near both ends, and on the whole grid of check (1);
  check (2f) added: the glass is 0.4255 thick within 0.005 (--glass-t) on every vertical line of a grid over the flat face
            (X -13.4..13.4, Y -6.3..6.3) and over the lit area, and its seat is at Z 3.72 within 0.005 (--seat);
  check (4) added (bar 3, the fold): at X -3.5, -1.75, 0, 1.75, 3.5 (5 stations across the band's 8.0 width) on both long sides,
            the largest angle between the outward normals of two faces meeting on the block-to-band junction (section vertices,
            |Y| > 6.0, Z -1.5 to 3.70) is under 2 degrees; X +-4.5, +-5.5 are printed as well. Its verdict is its own line
            "FOLD PASS" or "FOLD FAIL"; it is counted in the RESULT line only with --fold-gate.
Every other check, and every limit, is measure_417.py's.
--- measure_417.py's own description follows ---
Started from measure_32f.py as it is run for merged32h (--angle <size angle> --round 5.6 --no-light); every check of that
run is kept, with the rule round the joystick opening at 0.50 (lead's rule for merged32h). New for merged417:
  --ref <merged32h step of the same size>  (required) the accepted variant, measured the same way in this run
  --lift <mm>     how much higher the glass, its seat and the top must be than in --ref (0.970 for merged417; 0 = control run)
  --height <mm>   the cable study's flat-stack block height (4.170): printed against the measured top, not checked
  check (1) block height above Z 0 (highest point of body and glass inside the block's plan) = the --ref top + --lift, within
            0.005 (lead's ruling 2026-11-13, reading A);
  check (2) glass seat (lowest point of the cover glass over the floor) = ref + lift, within 0.005;
  check (3) body wall round the cavity envelope (panel pocket of thin.py: X +-13.725, Y +-6.45, corner 0.1, from the floor
            top Z 0.40 to the glass seat) by place class (side x height zone): nowhere thinner than in --ref (step 0.001).
  The light-place checks near the top (round-1 place, old place) are moved up by --lift with the top.

Run:  ../../.venv/bin/python measure_417.py <step> --ref <merged32h step> --lift 0.970 --height <mm> --angle <deg> --round 5.6 --no-light
Prints:
  bore (from the body), the joystick opening's two sizes and centre angle, whether it runs through the wall,
  the metal left on its four sides 0.1 mm under the surface (rule 0.40, as check_thin.py measures it) and at 0.2 and 0.3,
  the light window's centre X, Y and size, what is left at the old light place (X -12.5..-11.5, Y -0.5..0.5),
  the list of solids (the three placeholder specks must be gone), the joystick frame against the opening,
  and with --compare, every solid that must not change against merged32e.
Last line: RESULT PASS, or RESULT FAIL <what>.
Axes as thin-notes.md: X along the finger, Y across, Z up, band axis along X; angles from the top, negative toward -Y.
"""
import math
import sys
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/look/shared"))
from build123d import import_step, Vector, Box, Pos

OUT = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/look/s1/out")
args = [a for a in sys.argv[1:]]
cmp_path = None
if "--compare" in args:
    i = args.index("--compare")
    cmp_path = args[i + 1]
    del args[i:i + 2]
A_ARG = None
ROUND = None
if "--round" in args:                  # merged32h: round opening of this diameter (both sizes of the opening = it)
    i = args.index("--round")
    ROUND = float(args[i + 1])
    del args[i:i + 2]
NO_LIGHT = "--no-light" in args       # since 2026-11-12 (architecture 17.30): the accepted exterior must hold NO light solid
if NO_LIGHT:
    args.remove("--no-light")
if "--angle" in args:                  # merged32g: the expected joystick centre angle of this size (e.g. -84)
    i = args.index("--angle")
    A_ARG = float(args[i + 1])
    del args[i:i + 2]
def _opt(name, conv=float):
    if name in args:
        i = args.index(name)
        v = conv(args[i + 1])
        del args[i:i + 2]
        return v
    return None
REF = _opt("--ref", str)
FLAT_TOP = _opt("--flat-top")
GLASS_T = _opt("--glass-t")
SEAT_Z = _opt("--seat")
FOLD_GATE = "--fold-gate" in args
SLIT_REF = _opt("--slit-ref", str)       # merged417flatw: the windowless merged417flat file of the same size (window depth)
SLIT_Z0 = _opt("--slit")                 # merged417flatw: slot bottom Z of this size (the slit and the windows run from it to 1.53)
if FOLD_GATE:
    args.remove("--fold-gate")
LIFT = _opt("--lift")
HEIGHT = _opt("--height")
if None in (REF, LIFT, HEIGHT, FLAT_TOP, GLASS_T, SEAT_Z):
    sys.exit("measure_417flat.py: --ref, --lift, --height, --flat-top, --glass-t and --seat are required")
STEP = args[0]

WALL_MIN = 0.50                      # lead's rule for merged32h and merged417 (measure_32f.py used 0.40)
OPEN_X, OPEN_T = 6.6, 5.6          # lead's ruling 2026-11-11: the exterior's frame 6.4 x 5.4 plus 0.2 (X x along the band)
if ROUND is not None:
    OPEN_X = OPEN_T = ROUND
LIGHT = (-12.425, -2.95, 0.4)       # provisional light window (lead, from the light-path helper)
MIC_XS, MIC_Y, HOLE_D, SEAT_D, SEAT_T = (-11.77, 11.77), -4.8, 1.0, 2.0, 0.10   # mic-path.md section 5
A_JOY = A_ARG if A_ARG is not None else -78.0            # where the opening is expected (brief, thin.py P["joy_deg"]); the measured centre is reported below
fails = []


def load(path):
    s = import_step(path)
    return {c.label: c for c in s.children}


def vol(s):
    try:
        return s.volume
    except Exception:
        return 0.0


print("step:", STEP)
parts = load(STEP)
print("solids in the file:", sorted(parts), "count", len(parts))
for n in sorted(parts):
    print("  solid %-9s volume %.4f mm3" % (n, vol(parts[n])))
body = parts["body"]
inside = lambda x, y, z: body.is_inside(Vector(x, y, z))

# ---- bore, from the body: scan the line X 0, Y 0 below the block
def scan_z(z0, dz, lim):
    z = z0
    while abs(z - z0) < lim:
        if inside(0.0, 0.0, z):
            return z
        z += dz
    return None
zmid = -10.0
zt = scan_z(zmid, 0.001, 20)          # going up from inside the bore: first metal = top of the bore
zb = scan_z(zmid, -0.001, 20)         # going down: first metal = bottom of the bore
ZC, RI = (zt + zb) / 2, (zt - zb) / 2
print("bore from the body: top Z %.3f, bottom Z %.3f, axis Z %.4f, radius %.4f (diameter %.3f)" % (zt, zb, ZC, RI, 2 * RI))


def world(a_deg, x, t, r):
    """point at band angle a (deg), offset x along X, t along the tangent, r from the band axis (thin.py gpos)"""
    a = math.radians(a_deg)
    return (x, r * math.sin(a) + t * math.cos(a), ZC + r * math.cos(a) - t * math.sin(a))


def surf_r(a_deg, x, shape=None):
    """outer surface radius at angle a and X x: walking out from the bore in 0.05 steps, then back in 0.0025 steps"""
    ins = (lambda px, py, pz: shape.is_inside(Vector(px, py, pz))) if shape is not None else inside
    r = RI + 0.01
    seen = False
    while r < RI + 8:
        if ins(*world(a_deg, x, 0.0, r)):
            seen = True
        elif seen:
            break
        r += 0.05
    else:
        return None
    while not ins(*world(a_deg, x, 0.0, r)):
        r -= 0.0025
    return r + 0.00125

# ---- opening: angular extent at mid wall, X 0
r_side = min(surf_r(A_JOY, 3.5), surf_r(A_JOY, -3.5))   # beside the 6.6 opening (X +-3.3), on the flat before the 0.4 edge rounding
print("outer surface radius at %.0f deg beside the opening (X +-3.5, smaller): %.3f" % (A_JOY, r_side))
r_mid = (RI + r_side) / 2
open_angles = []
a = -50.0
while a > -110.0:                      # coarse 0.1 degree scan, then the two edges refined to 0.005 degree
    if not inside(*world(a, 0.0, 0.0, r_mid)):
        open_angles.append(a)
    a -= 0.1
if open_angles:
    hi, lo = max(open_angles), min(open_angles)
    while not inside(*world(hi + 0.005, 0.0, 0.0, r_mid)):
        hi += 0.005
    while not inside(*world(lo - 0.005, 0.0, 0.0, r_mid)):
        lo -= 0.005
    open_angles = [hi, lo]
if not open_angles:
    print("opening: NONE found between -50 and -110 deg at r %.3f, X 0" % r_mid)
    fails.append("no joystick opening")
    a_c = A_JOY
else:
    a_hi, a_lo = max(open_angles), min(open_angles)
    a_c = (a_hi + a_lo) / 2
    print("opening at r %.3f (mid wall), X 0: free from %.2f to %.2f deg, centre %.2f deg" % (r_mid, a_lo, a_hi, a_c))
    print("joystick opening centre angle %.3f deg, expected %.1f (tolerance 0.05)" % (a_c, A_JOY))
    if abs(a_c - A_JOY) > 0.05:
        fails.append("opening centre %.2f deg, not %.1f" % (a_c, A_JOY))


def edge_walk(test, lim, coarse=0.05, fine=0.0025):
    """smallest n in [0, lim) where test(n) changes from its value at 0: coarse steps, then fine steps back"""
    v0 = test(0.0)
    n = 0.0
    while n < lim and test(n) == v0:
        n += coarse
    if n >= lim:
        return lim
    m = n - coarse
    while test(m + fine) == v0:
        m += fine
    return m + fine / 2


def free_run(a_deg, x0, t0, r, dx, dt, lim=6.0):
    """distance from (x0, t0) along (dx, dt) at radius-plane r (flat local frame) until metal"""
    return edge_walk(lambda n: inside(*world(a_deg, x0 + dx * n, t0 + dt * n, r)), lim)

# sizes through the wall (flat local frame at the measured centre angle, as the box in thin.py)
sizes = []
depths = []
r = RI + 0.05
while r < r_side - 0.05:
    depths.append(r)
    r += 0.25
depths.append(r_side - 0.06)
through = True
for r in depths:
    c = world(a_c, 0.0, 0.0, r)
    if inside(*c):
        through = False
        print("  r %.3f: centre point is metal" % r)
        continue
    xp, xm = free_run(a_c, 0, 0, r, 1, 0), free_run(a_c, 0, 0, r, -1, 0)
    tp, tm = free_run(a_c, 0, 0, r, 0, 1), free_run(a_c, 0, 0, r, 0, -1)
    # near the surface the flat tangent line runs out of the curved hump into the air before it meets metal (first run:
    # 12.000 at r 12.775 and 13.014, out/work-32f/measure-32f-run2.log); sizes are taken where the line stays in the wall
    if r <= r_side - 0.5:
        sizes.append((r, xp + xm, tp + tm, xp, xm, tp, tm))
    print("  r %.3f: open along X %.3f (+X %.3f, -X %.3f), along the band (tangent) %.3f (toward the block %.3f, toward the bottom %.3f)"
          % (r, xp + xm, xp, xm, tp + tm, tp, tm))
# outside the surface: the opening must also open to the air (centre just above the surface is not metal), and the bore side
air_out = not inside(*world(a_c, 0.0, 0.0, r_side + 0.05))
air_in = not inside(*world(a_c, 0.0, 0.0, RI - 0.05))
print("opening goes through the wall: %s (%d radii sampled from %.3f to %.3f, centre open at %d of them; bore side open %s; outside open %s)"
      % ("YES" if through and air_in and air_out else "NO", len(depths), depths[0], depths[-1], len(sizes), air_in, air_out))
if not (through and air_in and air_out):
    fails.append("opening not through the wall")
if sizes:
    sx = [s[1] for s in sizes]
    st = [s[2] for s in sizes]
    print("opening size along X: min %.3f max %.3f; along the band: min %.3f max %.3f (over %d radii)" % (min(sx), max(sx), min(st), max(st), len(sizes)))
    if max(abs(v - OPEN_X) for v in sx) > 0.01:
        fails.append("opening along X %.3f..%.3f, not %.1f" % (min(sx), max(sx), OPEN_X))
    if max(abs(v - OPEN_T) for v in st) > 0.01:
        fails.append("opening along the band %.3f..%.3f, not %.1f" % (min(st), max(st), OPEN_T))

# ---- metal around the opening (check_thin.py method: on the curved surface rs = r_outer - depth; X runs straight, band runs along the arc)
def metal_x(rs, sg):
    # from the centre outward along X: find the opening edge, then count metal until the outside
    a = math.radians(a_c)
    y, z = rs * math.sin(a), ZC + rs * math.cos(a)
    edge = edge_walk(lambda n: inside(sg * n, y, z), 6.0) if not inside(0.0, y, z) else 0.0
    if edge > OPEN_X / 2 + 0.3:          # no metal at the opening's edge: a missing rim is 0 metal, not the scan cap
        return edge, 0.0
    m = edge_walk(lambda n: inside(sg * (edge + 0.003 + n), y, z), 4.0)
    return edge, m + 0.003


def metal_t(rs, sg):
    # along the arc at radius rs from the centre angle: find the edge, then count metal (arc length) until the outside
    d = 0.0
    def pt(d):
        aa = math.radians(a_c) + sg * d / rs
        return (0.0, rs * math.sin(aa), ZC + rs * math.cos(aa))
    edge = edge_walk(lambda n: inside(*pt(n)), 8.0) if not inside(*pt(0.0)) else 0.0
    if edge > OPEN_T / 2 + 0.3:          # no metal at the opening's edge on this arc: a missing rim is 0 metal
        return edge, 0.0
    m = edge_walk(lambda n: inside(*pt(edge + 0.003 + n)), 4.0)
    return edge, m + 0.003

side_min = {}
for depth in (0.1, 0.2, 0.3):
    rs = r_side - depth
    row = {}
    for lab, fn, sg in (("+X (fingertip)", metal_x, 1), ("-X (hand)", metal_x, -1),
                        ("toward the block", metal_t, 1), ("toward the bottom", metal_t, -1)):
        edge, m = fn(rs, sg)
        row[lab] = m
        side_min[lab] = min(side_min.get(lab, 9), m)
        print("metal %.1f mm under the surface (r %.3f), %-18s: edge at %.3f from the centre, metal %.3f mm%s"
              % (depth, rs, lab, edge, m, " (4.0 cap reached)" if m >= 3.99 else (" (NO RIM: no metal at the opening edge)" if m == 0.0 else "")))
    low = {k: v for k, v in row.items() if v < WALL_MIN}      # the rule at every measured depth (0.1, 0.2, 0.3)
    for k, v in low.items():
        fails.append("metal %s %.3f under %.2f at depth %.1f" % (k, v, WALL_MIN, depth))
print("thinnest metal on each side over the depths 0.1, 0.2, 0.3: " + ", ".join("%s %.3f" % (k, v) for k, v in side_min.items()) + " (rule %.2f at 0.1, 0.2 and 0.3)" % WALL_MIN)

# ---- joystick frame against the opening (the joystick is not changed; this only reports whether it fits)
joy = parts.get("joystick")
if joy is not None:
    jb = joy.bounding_box()
    # extent along the band: project the joystick's vertices on the tangent at the centre angle
    a = math.radians(a_c)
    tdir = (math.cos(a), -math.sin(a))
    ts = [v.Y * tdir[0] + (v.Z - ZC) * tdir[1] for v in joy.vertices()]
    if ROUND is not None:
        # a round frame has too few vertices for the projection: scan the solid itself, 0.2 above the body surface (inside the
        # frame's height), along X and along the band from the axis outward until it leaves the solid
        rj = r_side + 0.2
        ext = {}
        for lab, ux, ut in (("+X", 1, 0), ("-X", -1, 0), ("+t", 0, 1), ("-t", 0, -1)):
            ext[lab] = edge_walk(lambda n: joy.is_inside(Vector(*world(a_c, ux * n, ut * n, rj))), 4.0, coarse=0.02, fine=0.0005)
        jb_maxX, jb_minX = ext["+X"], -ext["-X"]
        ts = [-ext["-t"], ext["+t"]]
        print("joystick frame extent scanned at r %.3f: +X %.3f, -X %.3f, toward the block %.3f, toward the bottom %.3f" % (rj, ext["+X"], ext["-X"], ext["+t"], ext["-t"]))
        class _B:
            pass
        jb = _B(); jb.max = _B(); jb.min = _B(); jb.max.X, jb.min.X = jb_maxX, jb_minX
    jx = jb.max.X - jb.min.X
    jt = max(ts) - min(ts)
    print("joystick solid (frame and nub): along X %.3f (X %.3f..%.3f), along the band %.3f" % (jx, jb.min.X, jb.max.X, jt))
    if sizes:
        ox, ot = min(s[1] for s in sizes), min(s[2] for s in sizes)
        fit = jx <= ox and jt <= ot
        print("joystick frame fits the opening: %s (frame %.3f x %.3f, opening %.3f x %.3f, X x band)" % ("YES" if fit else "NO", jx, jt, ox, ot))
        if not fit:
            fails.append("joystick frame %.2f x %.2f does not fit the opening %.2f x %.2f" % (jx, jt, ox, ot))
        # clearance on each side: opening edge (from the scans, the row nearest the surface used for the sizes) minus the
        # joystick's own extent on that side (X from its bounding box, band direction from its vertices projected on the tangent)
        r_, _, _, xp_, xm_, tp_, tm_ = sizes[-1]
        clr = {"+X (fingertip)": xp_ - jb.max.X, "-X (hand)": xm_ + jb.min.X, "toward the block": tp_ - max(ts), "toward the bottom": tm_ + min(ts)}
        print("frame clearance in the opening at r %.3f: " % r_ + ", ".join("%s %.3f" % (k, v) for k, v in clr.items())
              + " mm (asked: 0.1 each side; pass at 0.09 or more, the scans step 0.0025)")
        for k, v in clr.items():
            if v < 0.09:
                fails.append("frame clearance %s %.3f under 0.09" % (k, v))

# ---- merged32h: the round cap's profile, measured on the joystick solid along lines parallel to the radial at the centre angle
if ROUND is not None and joy is not None:
    jins = lambda p: joy.is_inside(Vector(*p))
    def top_h(dx, dt):
        """height of the joystick's top surface above r_side (the body surface beside the opening) at offset dx along X, dt along the band"""
        h = 3.5
        while h > -0.5 and not jins(world(a_c, dx, dt, r_side + h)):
            h -= 0.02
        if h <= -0.5:
            return None
        h += 0.02
        while not jins(world(a_c, dx, dt, r_side + h)):
            h -= 0.001
        return h + 0.0005
    prof = {}
    for lab, ux, ut in (("+X", 1, 0), ("-X", -1, 0), ("toward the block", 0, 1), ("toward the bottom", 0, -1)):
        prof[lab] = [(k * 0.01, top_h(ux * k * 0.01, ut * k * 0.01)) for k in range(0, 281)]
    h0 = prof["+X"][0][1]
    print("cap profile (heights above the body surface r %.3f beside the opening): centre %.3f" % (r_side, h0))
    for lab, pr in prof.items():
        hs = [(d, h) for d, h in pr if h is not None]
        frame_h = [h for d, h in hs if 2.30 <= d <= 2.60]
        cap_pts = [(d, h) for d, h in hs if d <= 2.25]
        hmax = max(h for d, h in cap_pts)
        # ridges: an up-step then a down-step of more than 0.04 between neighbours 0.01 apart (the ridge walls)
        ups = [pr[k + 1][0] for k in range(len(pr) - 1) if pr[k][1] is not None and pr[k + 1][1] is not None and pr[k + 1][1] - pr[k][1] > 0.04 and pr[k][0] < 2.2]
        downs = [pr[k][0] for k in range(len(pr) - 1) if pr[k][1] is not None and pr[k + 1][1] is not None and pr[k][1] - pr[k + 1][1] > 0.04 and pr[k][0] < 2.2]
        ridges = []
        for u in ups:
            dn = [d for d in downs if d > u]
            if dn:
                ridges.append(((u + dn[0]) / 2, dn[0] - u + 0.01))
        # cap edge: last point of the cap (height above frame top + 0.05) before the frame plateau
        fh = sum(frame_h) / len(frame_h) if frame_h else float("nan")
        edge = max(d for d, h in cap_pts if h > fh + 0.05)
        print("  %-18s: frame top %.3f above the body; cap top (highest) %.3f above the body = %.3f above the frame; cap edge at %.2f from the axis; ridges (centre, width): %s"
              % (lab, fh, hmax, hmax - fh, edge, ", ".join("%.3f / %.3f" % r for r in ridges) or "none"))
        if [round(r[0], 1) for r in ridges] != [0.7, 1.3, 1.9]:
            fails.append("ridges %s on the %s line, not at 0.7, 1.3, 1.9" % ([round(r[0], 3) for r in ridges], lab))

# ---- light window
lt = parts.get("light")
if NO_LIGHT:
    if lt is None:
        print("light: no light solid, as required (recording light removed, architecture 17.30)")
    else:
        print("light: a light solid is present")
        fails.append("a light solid is present, the recording light is removed")
elif lt is None:
    print("light: no light solid")
    fails.append("no light solid")
else:
    lb = lt.bounding_box()
    cx, cy = (lb.min.X + lb.max.X) / 2, (lb.min.Y + lb.max.Y) / 2
    print("light window: centre X %.3f Y %.3f; size X %.3f x Y %.3f; Z %.3f..%.3f; volume %.5f mm3"
          % (cx, cy, lb.max.X - lb.min.X, lb.max.Y - lb.min.Y, lb.min.Z, lb.max.Z, vol(lt)))
    if abs(cx - LIGHT[0]) > 0.01 or abs(cy - LIGHT[1]) > 0.01:
        fails.append("light centre %.3f, %.3f not %.3f, %.3f" % (cx, cy, LIGHT[0], LIGHT[1]))
    if abs((lb.max.X - lb.min.X) - LIGHT[2]) > 0.01 or abs((lb.max.Y - lb.min.Y) - LIGHT[2]) > 0.01:
        fails.append("light size %.3f x %.3f not %.2f" % (lb.max.X - lb.min.X, lb.max.Y - lb.min.Y, LIGHT[2]))
    g = parts["glass"]
    gb = (g & (Pos(cx, cy, 2.0) * Box(0.05, 0.05, 4.0))).bounding_box()
    print("glass top under the light centre Z %.3f; light top Z %.3f, light bottom Z %.3f" % (gb.max.Z, lb.max.Z, lb.min.Z))

# ---- the round-1 light place X -13.25, Y -4.7 (must be empty)
r1 = Pos(-13.25, -4.7, 3.5 + LIFT) * Box(0.8, 0.8, 0.6)          # merged417: moved up by LIFT with the top
left1 = {n: round(vol(s & r1), 6) for n, s in parts.items() if n != "glass" and vol(s & r1) > 1e-7}
print("round-1 light place X -13.65..-12.85, Y -5.1..-4.3, Z %.2f..%.2f: solids other than the glass there: %s" % (3.2 + LIFT, 3.8 + LIFT, left1 or "none"))
if left1:
    fails.append("solid at X -13.25, Y -4.7")

# ---- old light place
old = Pos(-12.0, 0.0, 3.85 + LIFT) * Box(1.0, 1.0, 0.3)          # merged417: moved up by LIFT with the top
left = {n: vol(s & old) for n, s in parts.items() if n != "glass"}
gold = (parts["glass"] & old)
gtop = gold.bounding_box().max.Z if vol(gold) > 0 else None
print("old light place X -12.5..-11.5, Y -0.5..0.5, Z %.2f..%.2f: solids other than the glass there: %s; glass top there Z %s"
      % (3.70 + LIFT, 4.00 + LIFT, {n: round(v, 5) for n, v in left.items() if v > 1e-7} or "none", "%.4f" % gtop if gtop is not None else "none"))
if any(v > 1e-7 for v in left.values()):
    fails.append("solid left at the old light place")
if gtop is not None and gtop > 3.85 + LIFT + 1e-4:
    fails.append("glass raised at the old light place")

# ---- microphone openings on the underside (found from the body: scans along X and Y through the seat and the hole)
def span(fixed, axis, z, c0, lim=2.0):
    """free length through the point c0 along axis ('x' or 'y') at height z: (minus side, plus side) to the first metal"""
    def p(n):
        return (c0 + n, fixed, z) if axis == "x" else (fixed, c0 + n, z)
    from_m = edge_walk(lambda n: inside(*p(-n)), lim, coarse=0.02, fine=0.001)
    from_p = edge_walk(lambda n: inside(*p(n)), lim, coarse=0.02, fine=0.001)
    return from_m, from_p
for k, (mx, nm) in enumerate(zip(MIC_XS, ("mic_1", "mic_2"))):
    res = {}
    for lab, z in (("seat", 0.05), ("hole", 0.20)):
        xm, xp = span(MIC_Y, "x", z, mx)
        ym, yp = span(mx, "y", z, MIC_Y)
        res[lab] = (mx + (xp - xm) / 2, MIC_Y + (yp - ym) / 2, xm + xp, ym + yp)
        print("microphone opening %d (%s) %s at Z %.2f: centre X %.3f Y %.3f; diameter along X %.3f, along Y %.3f"
              % (k + 1, nm, lab, z, res[lab][0], res[lab][1], res[lab][2], res[lab][3]))
    # seat depth: along Z at a point in the ring between hole and seat edge (radius 0.75), from Z -0.2 up to the first metal
    zr = -0.2 + edge_walk(lambda n: inside(mx + 0.75, MIC_Y, -0.2 + n), 1.0, coarse=0.01, fine=0.0005)
    # hole top: on the axis, from Z -0.2 up to the first metal
    zh = -0.2 + edge_walk(lambda n: inside(mx, MIC_Y, -0.2 + n), 2.0, coarse=0.01, fine=0.0005)
    print("microphone opening %d: seat depth from the underside Z 0: %.3f; hole runs to Z %.3f (a blind end: the inside model's floor pocket opens it)" % (k + 1, zr, zh))
    for lab, d in (("seat", SEAT_D), ("hole", HOLE_D)):
        cx_, cy_, dx_, dy_ = res[lab]
        if abs(cx_ - mx) > 0.01 or abs(cy_ - MIC_Y) > 0.01 or abs(dx_ - d) > 0.01 or abs(dy_ - d) > 0.01:
            fails.append("mic opening %d %s centre %.3f, %.3f size %.3f x %.3f" % (k + 1, lab, cx_, cy_, dx_, dy_))
    if abs(zr - SEAT_T) > 0.005:
        fails.append("mic opening %d seat depth %.3f" % (k + 1, zr))
    m = parts.get(nm)
    if m is None:
        fails.append("no %s node" % nm)
    else:
        mb = m.bounding_box()
        print("node %s: centre X %.3f Y %.3f, size %.3f x %.3f, Z %.3f..%.3f" % (nm, (mb.min.X + mb.max.X) / 2, (mb.min.Y + mb.max.Y) / 2,
              mb.max.X - mb.min.X, mb.max.Y - mb.min.Y, mb.min.Z, mb.max.Z))
# no wall slot on the -Y wall: points just inside the -Y wall face at the old slot places and along the whole wall
slot_pts = [(x, -7.375 + 0.15, z) for x in [i * 0.25 for i in range(-50, 51)] for z in (1.2, 1.4, 1.6)]
in_slit = (lambda p: -3.60 <= p[0] <= -1.40) if SLIT_Z0 is not None else (lambda p: False)
open_slit = [p for p in slot_pts if in_slit(p) and not inside(*p)]
if SLIT_Z0 is not None:
    print("-Y wall inside the slit X -3.60..-1.40 (left out of the check below; the slit is meant to be open there): %d of %d points open" % (len(open_slit), len([p for p in slot_pts if in_slit(p)])))
slot_pts = [p for p in slot_pts if not in_slit(p)]
open_pts = [p for p in slot_pts if abs(p[0]) < 11.9 and not inside(*p)]
print("-Y wall, 0.15 inside its face, X -12.5..12.5 every 0.25 at Z 1.2, 1.4, 1.6: %d of %d points are not metal (a slot would show here)%s"
      % (len(open_pts), len([p for p in slot_pts if abs(p[0]) < 11.9]), (": e.g. " + str(open_pts[:3])) if open_pts else ""))
if open_pts:
    fails.append("wall slot on the -Y wall: %d points open" % len(open_pts))

# ---- specks: placeholder solids inside the band wall
specks = [n for n in ("band", "button", "contacts") if n in parts]
small = {n: round(vol(s), 4) for n, s in parts.items() if vol(s) < 0.1 and n != "light"}
print("placeholder solids band, button, contacts present: %s; solids under 0.1 mm3 other than the light: %s" % (specks or "none", small or "none"))
if specks:
    fails.append("specks present: " + ",".join(specks))

# ---- unchanged against merged32e
if cmp_path:
    e = load(cmp_path)
    print("compare with:", cmp_path)
    for n in ("glass", "joystick", "screen"):
        a_, b_ = parts[n], e[n]
        ba, bb = a_.bounding_box(), b_.bounding_box()
        dv = abs(vol(a_) - vol(b_))
        db = max(abs(p - q) for p, q in zip((ba.min.X, ba.min.Y, ba.min.Z, ba.max.X, ba.max.Y, ba.max.Z), (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)))
        sym = vol(a_ - b_) + vol(b_ - a_)
        print("  %-8s volume f %.4f e %.4f; bbox max diff %.5f; symmetric difference %.6f mm3" % (n, vol(a_), vol(b_), db, sym))
        if sym > 1e-4 or db > 1e-4:
            fails.append("%s changed against merged32e" % n)
    be = e["body"]
    print("  body: volume f %.4f e %.4f; difference %.4f mm3" % (vol(body), vol(be), vol(be) - vol(body)), flush=True)
    # body outside the opening region: a box around the opening (local frame, 0.3 margin) is taken away from both, the rest must match
    a = math.radians(a_c)
    from build123d import Rot
    keep = Pos(0, 0, ZC) * Rot(-a_c, 0, 0) * Pos(0, 0, (RI - 0.5 + RI + 6) / 2) * Box(OPEN_X + 0.6, OPEN_T + 0.6, 6.5)
    for mx in (-11.0, 11.0):          # old wall slots (merged32e)
        keep = keep + Pos(mx, -7.375, 1.4) * Box(2.0, 1.2, 1.0)
    for mx in MIC_XS:                 # new underside openings
        keep = keep + Pos(mx, MIC_Y, 0.2) * Box(2.6, 2.6, 0.8)
    bf_o, be_o = body - keep, be - keep
    sym = vol(bf_o - be_o) + vol(be_o - bf_o)
    print("  body outside the opening region (opening box + 0.3 each side) and the old and new microphone regions: volume f %.4f e %.4f, symmetric difference %.6f mm3" % (vol(bf_o), vol(be_o), sym))
    if sym > 1e-3:
        fails.append("body changed outside the opening region")
    # band outline and hump: outer radius at X +-3.0 (beside the opening) every 2 degrees from -120 to -40, f against e
    worst = 0.0
    for k in range(-120, -39, 4):
        for x in (3.5, -3.5, 3.7, -3.7):
            rf = surf_r(k, x)
            re_ = surf_r(k, x, be)
            worst = max(worst, abs(rf - re_))
    print("  band outer radius beside the opening (X +-3.5, +-3.7, -120 to -40 deg every 4): largest f-e difference %.4f mm" % worst)
    if worst > 0.006:
        fails.append("band outline changed %.4f" % worst)
    print("  solids in merged32e not in merged32f:", sorted(set(e) - set(parts)), "; in merged32f not in merged32e:", sorted(set(parts) - set(e)))

# ================= merged417: height, glass seat and walls round the cavity, against the accepted variant (--ref) =================
# Lines are met through plane sections: the shape is cut by the plane that holds the line (X = x for a vertical line, Z = z for
# a horizontal one), the section edges are turned into polylines with a chord error under 1e-5 mm, and the line is crossed with
# them in the plane. First version used OCC IntCurvesFace_ShapeIntersector: on the run-2 files it raised Standard_Failure
# (out/work-417/measure-417-us9.log, -us12.log, run 2) and returned no point for a line that crosses the body (-us13.log, run 2).
import numpy as np
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_QuasiUniformDeflection
from OCP.gp import gp_Pln, gp_Pnt, gp_Dir
from build123d import Compound as _Compound
_SECT = {}


def _section(shape, key):
    kind, v = key
    if (id(shape), key) in _SECT:
        return _SECT[(id(shape), key)]
    pln = gp_Pln(gp_Pnt(v, 0, 0), gp_Dir(1, 0, 0)) if kind == "x" else gp_Pln(gp_Pnt(0, 0, v), gp_Dir(0, 0, 1))
    op = BRepAlgoAPI_Section(shape.wrapped, pln)
    op.Build()
    A, B = [], []
    for e in _Compound(op.Shape()).edges():
        c = BRepAdaptor_Curve(e.wrapped)
        q = GCPnts_QuasiUniformDeflection(c, 1e-5)
        pts = [q.Value(i) for i in range(1, q.NbPoints() + 1)]
        xy = [(pp.Y(), pp.Z()) if kind == "x" else (pp.X(), pp.Y()) for pp in pts]
        A += xy[:-1]
        B += xy[1:]
    seg = (np.array(A, float).reshape(-1, 2), np.array(B, float).reshape(-1, 2))
    _SECT[(id(shape), key)] = seg
    return seg


def hits(shape, p, d, lim=40.0):
    """parameters (distance from p along unit direction d) where the line meets the shape's boundary, sorted"""
    if abs(d[2]) > 0.999:                      # vertical line: plane X = p.x, coordinates (Y, Z)
        key, o, u = ("x", round(p[0], 6)), np.array([p[1], p[2]]), np.array([d[1], d[2]])
    elif abs(d[2]) < 1e-9:                     # horizontal line: plane Z = p.z, coordinates (X, Y)
        key, o, u = ("z", round(p[2], 6)), np.array([p[0], p[1]]), np.array([d[0], d[1]])
    else:
        raise ValueError("hits: only vertical or horizontal lines")
    A, B = _section(shape, key)
    if len(A) == 0:
        return []
    E = B - A
    den = u[0] * E[:, 1] - u[1] * E[:, 0]
    ok = np.abs(den) > 1e-12
    AO = A - o
    t = (AO[:, 0] * E[:, 1] - AO[:, 1] * E[:, 0])
    s = (AO[:, 0] * u[1] - AO[:, 1] * u[0])
    t = t[ok] / den[ok]
    s = s[ok] / den[ok]
    t = t[(s >= -1e-12) & (s <= 1 + 1e-12) & (np.abs(t) <= lim)]
    return sorted(float(v) for v in t)


ref = load(REF)
print("reference (accepted variant):", REF)
rb, rg = ref["body"], ref["glass"]


def top_and_seat(b, g):
    """block top = highest Z of body and glass on the vertical lines X 0, Y -6..6 every 0.5 and X -12..12 every 2 at Y 0;
    glass seat = lowest Z of the glass on the line X 0, Y 0; body top at the seat = highest Z of the body on X 0, Y +-6.8"""
    tops = []
    for x, y in [(0.0, 0.5 * k) for k in range(-12, 13)] + [(2.0 * k, 0.0) for k in range(-6, 7)]:
        hg = hits(g, (x, y, 0.0), (0, 0, 1))
        hb = hits(b, (x, y, 0.0), (0, 0, 1))
        tops.append((max(hg + hb), x, y))
    gz = hits(g, (0.0, 0.0, 0.0), (0, 0, 1))
    bz = [max(hits(b, (0.0, s * 6.8, 0.0), (0, 0, 1))) for s in (1, -1)]
    return max(tops), min(gz), max(gz), bz
(t_new, x_new, y_new), gs_new, gt_new, bt_new = top_and_seat(body, parts["glass"])
(t_ref, x_ref, y_ref), gs_ref, gt_ref, bt_ref = top_and_seat(rb, rg)
print("block top above the finger-side face (Z 0): this file %.4f at X %.1f Y %.1f; reference %.4f at X %.1f Y %.1f; difference %.4f"
      % (t_new, x_new, y_new, t_ref, x_ref, y_ref, t_new - t_ref))
print("glass on X 0, Y 0: this file Z %.4f to %.4f (%.4f thick); reference Z %.4f to %.4f (%.4f thick)"
      % (gs_new, gt_new, gt_new - gs_new, gs_ref, gt_ref, gt_ref - gs_ref))
print("body top at X 0, Y +6.8 / -6.8 (the seat under the glass edge): this file %.4f / %.4f; reference %.4f / %.4f"
      % (bt_new[0], bt_new[1], bt_ref[0], bt_ref[1]))
# check (1), lead's ruling 2026-11-13 (reading A): top above Z 0 = the reference's measured top + LIFT, within 0.005
t_ask = t_ref + LIFT
print("check (1) of measure_417.py (reference top + lift = %.4f) does not apply to the flat top: replaced by check (1f)" % t_ask)
# check (1f): flat top. Lines: centre; near both long edges (Y +-6.3, the flat ends at Y +-6.375 where the 1.0 roll starts) at
# X -10, 0, 10; near both ends (X +-13.4, the flat ends at X +-13.45 where the 1.2 roll starts) at Y -5, 0, 5; and check (1)'s grid
tops_f = []
for lab, x, y in ([("centre", 0.0, 0.0)] + [("long edge +Y", xx, 6.3) for xx in (-10.0, 0.0, 10.0)] + [("long edge -Y", xx, -6.3) for xx in (-10.0, 0.0, 10.0)]
                  + [("end +X", 13.4, yy) for yy in (-5.0, 0.0, 5.0)] + [("end -X", -13.4, yy) for yy in (-5.0, 0.0, 5.0)]
                  + [("grid", 0.0, 0.5 * k) for k in range(-12, 13)] + [("grid", 2.0 * k, 0.0) for k in range(-6, 7)]):
    tz = max(hits(parts["glass"], (x, y, 0.0), (0, 0, 1)) + hits(body, (x, y, 0.0), (0, 0, 1)))
    tops_f.append((tz, lab, x, y))
    if lab != "grid":
        print("  top at %-12s X %6.2f Y %5.2f: Z %.4f" % (lab, x, y, tz))
lo_, hi_ = min(tops_f), max(tops_f)
okf = all(abs(t[0] - FLAT_TOP) <= 0.005 for t in tops_f)
print("check (1f) flat top: %d lines, Z %.4f (%s X %.2f Y %.2f) to %.4f (%s X %.2f Y %.2f), asked %.3f within 0.005: %s"
      % (len(tops_f), lo_[0], lo_[1], lo_[2], lo_[3], hi_[0], hi_[1], hi_[2], hi_[3], FLAT_TOP, "PASS" if okf else "FAIL"))
if not okf:
    fails.append("flat top %.4f..%.4f, not %.3f" % (lo_[0], hi_[0], FLAT_TOP))
# check (2f): glass thickness on the flat face and the lit area, and the seat
from envelope_slim import SCREEN_CX, SCREEN_CY, LIT_X, LIT_Y
gl = []
def _on_flat(x, y, m=0.47):
    # inside the plan rounded rectangle (half 14.65 x 7.375, corner 2.5) shrunk by m: the face is flat there
    hx, hy, rc = 14.65 - m, 7.375 - m, 2.5 - m
    ax, ay = abs(x), abs(y)
    if ax > hx or ay > hy:
        return False
    cx, cy = hx - rc, hy - rc
    return not (ax > cx and ay > cy and (ax - cx) ** 2 + (ay - cy) ** 2 > rc ** 2)
pts_g = [(-14.18 + 28.36 * i / 20, -6.905 + 13.81 * j / 20) for i in range(21) for j in range(21)]
n_all = len(pts_g)
pts_g = [q for q in pts_g if _on_flat(*q)]
print("check (2f) grid: %d of %d points of the 21 x 21 grid lie on the flat face (plan shrunk by 0.47); the others are on the rolls" % (len(pts_g), n_all))
pts_g += [(SCREEN_CX - LIT_X / 2 + LIT_X * i / 12, SCREEN_CY - LIT_Y / 2 + LIT_Y * j / 8) for i in range(13) for j in range(9)]
for x, y in pts_g:
    hg = hits(parts["glass"], (x, y, 0.0), (0, 0, 1))
    gl.append((max(hg) - min(hg), min(hg), max(hg), x, y) if len(hg) >= 2 else (None, None, None, x, y))
miss = [g for g in gl if g[0] is None]
good = [g for g in gl if g[0] is not None]
tmin, tmax = min(good), max(good)
smin, smax = min(g[1] for g in good), max(g[1] for g in good)
okg = not miss and all(abs(g[0] - GLASS_T) <= 0.005 for g in good)
oks = not miss and abs(smin - SEAT_Z) <= 0.005 and abs(smax - SEAT_Z) <= 0.005
print("check (2f) glass thickness on %d vertical lines (21 x 21 over X -14.18..14.18, Y -6.905..6.905 kept on the flat face; 13 x 9 over the lit area %.1f x %.1f at %.3f, %.3f): %.4f (X %.2f Y %.2f) to %.4f (X %.2f Y %.2f), lines with no glass %d, asked %.4f within 0.005: %s"
      % (len(gl), LIT_X, LIT_Y, SCREEN_CX, SCREEN_CY, tmin[0], tmin[3], tmin[4], tmax[0], tmax[3], tmax[4], len(miss), GLASS_T, "PASS" if okg else "FAIL"))
print("check (2f) glass seat (glass bottom) on the same lines: Z %.4f to %.4f, asked %.3f within 0.005: %s" % (smin, smax, SEAT_Z, "PASS" if oks else "FAIL"))
if not okg:
    fails.append("glass thickness %.4f..%.4f, not %.4f" % (tmin[0], tmax[0], GLASS_T))
if not oks:
    fails.append("glass seat %.4f..%.4f, not %.3f" % (smin, smax, SEAT_Z))
print("  study figure --height %.3f: %s by %.4f. It is the flat-stack number of screen-cable-study.md 4.3 (3.20 + 0.970, the stack of "
      "architecture.md line 426); the real block has a crown (top 3.85 at the centre line in merged32h), so it is printed only, not checked"
      % (HEIGHT, "met" if abs(t_new - HEIGHT) <= 0.005 else "NOT met", t_new - HEIGHT))
# check (2): the glass seat over the floor (the floor top Z 0.40 is the same in both files, so the difference is the Z difference)
d_seat = gs_new - gs_ref
print("check (2) glass seat (lowest glass Z on X 0, Y 0): this file %.4f, reference %.4f, higher by %.4f, asked %.3f (tolerance 0.005): %s"
      % (gs_new, gs_ref, d_seat, LIFT, "PASS" if abs(d_seat - LIFT) <= 0.005 else "FAIL"))
if abs(d_seat - LIFT) > 0.005:
    fails.append("glass seat higher by %.4f, not %.3f" % (d_seat, LIFT))
for k in range(2):
    if abs((bt_new[k] - bt_ref[k]) - LIFT) > 0.005:
        fails.append("body top at the seat higher by %.4f, not %.3f" % (bt_new[k] - bt_ref[k], LIFT))
print("  body top at the seat higher by %.4f / %.4f" % (bt_new[0] - bt_ref[0], bt_new[1] - bt_ref[1]))

# check (3): walls round the cavity envelope. Rays leave the envelope outward, horizontally; the wall = the first exit from
# the body along the ray. Place classes: side (+Y long wall, -Y long wall, +X fingertip end, -X hand end, the four plan
# corners) x zone (low: Z 0.45 to 1.45, the part under the board that does not move; high: the top 1.00 under the seat,
# the part that moves up; mid: between). Z every 0.05 from 0.45 to seat - 0.02.
EX, EY, ER, ZF = 13.725, 6.45, 0.1, 0.40
WINX = ((-1.05, 1.05), (1.45, 3.55)); SLITX = (-3.55, -1.45); WIN_TOP = 1.53; WIN_LIMIT = 0.70


def env_rays():
    rays = []
    for x in [-12.0 + 1.0 * k for k in range(25)]:
        rays.append(("+Y wall", (x, EY), (0, 1)))
        rays.append(("-Y wall", (x, -EY), (0, -1)))
    for y in [-6.0 + 1.0 * k for k in range(13)]:
        rays.append(("+X end", (EX, y), (1, 0)))
        rays.append(("-X end", (-EX, y), (-1, 0)))
    for sx in (1, -1):
        for sy in (1, -1):
            cx, cy = sx * (EX - ER), sy * (EY - ER)
            for a in (15, 30, 45, 60, 75):
                ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
                rays.append(("corners", (cx + sx * ER * ca, cy + sy * ER * sa), (sx * ca, sy * sa)))
    return rays


def walls(b, seat):
    # heights: low and mid from the floor up (Z 0.45 every 0.05: the same Z in both files), high from the seat down
    # (seat - 0.02 - 0.05 k: the same depth under the seat in both files). First version used one grid from 0.45 up for all
    # three, so "high" compared Z 3.70 (0.02 under the 3.72 seat) with Z 2.70 (0.05 under the 2.75 seat): unlike places
    # (out/work-417/measure-417-us9.log, run 1).
    zs = []
    z = 0.45
    while z < seat - 1.0 - 1e-9:
        zs.append((z, "low" if z <= 1.45 + 1e-9 else "mid"))
        z = round(z + 0.05, 6)
    zs += [(round(seat - 0.02 - 0.05 * k, 6), "high") for k in range(20)]
    out = {}
    for z, zone in zs:
        for side, (px, py), (dx, dy) in env_rays():
            hs = [h for h in hits(b, (px, py, z), (dx, dy, 0.0), lim=10.0) if h > 1e-6]
            w = hs[0] if hs else None
            key = (side, zone)
            if SLIT_Z0 is not None and side in ("+Y wall", "-Y wall") and SLIT_Z0 - 1e-9 <= z <= WIN_TOP + 1e-9 and any(a <= px <= b for a, b in WINX):
                key = (side.replace(" wall", "") + " window", "metal behind a blind window")    # lead's ruling 3: own class, limit 0.70
            if w is not None and (key not in out or w < out[key][0]):
                out[key] = (w, px, py, z)
    return out
seat_new, seat_ref = min(bt_new), min(bt_ref)
w_new, w_ref = walls(body, seat_new), walls(rb, seat_ref)
print("check (3) body wall round the cavity envelope X +-%.3f, Y +-%.3f (corner %.1f), low/mid Z 0.45 up every 0.05 to seat - 1.0, high seat - 0.02 down every 0.05 for 20 levels (seat: this file %.4f, reference %.4f):"
      % (EX, EY, ER, seat_new, seat_ref))
for key in sorted(set(w_new) | set(w_ref)):
    a_, b_ = w_new.get(key), w_ref.get(key)
    ok = a_ is not None and b_ is not None and a_[0] >= b_[0] - 0.001
    if "window" in key[0]:
        ok = a_ is not None and a_[0] >= WIN_LIMIT
        print("  %-8s %s: this file %s; limit %.2f (lead's ruling); %s" % (key[0], key[1], "%.4f at X %.3f Y %.3f Z %.2f" % a_ if a_ else "none",
              WIN_LIMIT, "PASS" if ok else "UNDER THE LIMIT or missing"))
        if not ok:
            fails.append("metal behind the %s %.4f under %.2f" % (key[0], a_[0] if a_ else -1, WIN_LIMIT))
        continue
    print("  %-8s %-4s: this file %s; reference %s; %s" % (key[0], key[1],
          "%.4f at X %.3f Y %.3f Z %.2f" % a_ if a_ else "none", "%.4f at X %.3f Y %.3f Z %.2f" % b_ if b_ else "none",
          "not thinner" if ok else "THINNER or missing"))
    if not ok:
        fails.append("wall %s %s thinner than the reference" % key)
print("  thinnest wall overall: this file %.4f, reference %.4f" % (min(v[0] for v in w_new.values()), min(v[0] for v in w_ref.values())))


def walls_by_level(b, seat):
    out = {}
    for k in range(20):
        z = round(seat - 0.02 - 0.05 * k, 6)
        for side, (px, py), (dx, dy) in env_rays():
            hs = [h for h in hits(b, (px, py, z), (dx, dy, 0.0), lim=10.0) if h > 1e-6]
            if hs and ((side, k) not in out or hs[0] < out[(side, k)]):
                out[(side, k)] = hs[0]
    return out
lv_new, lv_ref = walls_by_level(body, seat_new), walls_by_level(rb, seat_ref)
for side in ("+X end", "-X end", "+Y wall", "-Y wall", "corners"):
    row = []
    for k in range(20):
        a_, b_ = lv_new.get((side, k)), lv_ref.get((side, k))
        row.append("%.2f: %s/%s%s" % (0.02 + 0.05 * k, "%.4f" % a_ if a_ else "-", "%.4f" % b_ if b_ else "-",
                                      "" if (a_ and b_ and a_ >= b_ - 0.001) else " THINNER"))
    print("  high zone by depth under the seat, %-8s (depth: this file/reference): %s" % (side, "; ".join(row)))

# check (5), merged417flatw: the slit is open through the wall, the two blind windows are 0.20 deep and do not open the body
if SLIT_Z0 is not None:
    metal = []
    n5 = 0
    for s5 in (1, -1):
        for x5 in (-3.3, -2.5, -1.7):
            for z5 in (SLIT_Z0 + 0.05, 0.60, 1.45):
                for k in range(107):
                    y5 = s5 * (5.70 + 0.05 * k)
                    n5 += 1
                    if inside(x5, y5, z5):
                        metal.append((x5, round(y5, 2), round(z5, 2)))
    print("check (5) slit open: %d points on X -3.3, -2.5, -1.7, |Y| 5.70..11.00, Z %.2f, 0.60, 1.45, both sides: %d metal%s"
          % (n5, SLIT_Z0 + 0.05, len(metal), (": e.g. " + str(metal[:3])) if metal else ""))
    if metal:
        fails.append("slit not open: %d metal points" % len(metal))
    if SLIT_REF is None:
        fails.append("--slit given without --slit-ref: the window depth cannot be read")
    else:
        rbod = load(SLIT_REF)["body"]
        rin = lambda x, y, z: rbod.is_inside(Vector(x, y, z))
        xs5 = [round(-0.9 + 0.3 * k, 3) for k in range(7)] + [round(1.6 + 0.3 * k, 3) for k in range(7)]
        zs5 = []
        z_ = SLIT_Z0 + 0.02
        while z_ <= WIN_TOP + 1e-9:
            zs5.append(round(z_, 3)); z_ += 0.04
        dep, left_face, left_start = [], 0, 0
        for s5 in (1, -1):
            for x5 in xs5:
                for z5 in zs5:
                    if abs(z5 - WIN_TOP) < 0.005 or abs(z5 - SLIT_Z0) < 0.005:
                        left_face += 1; continue
                    if not (inside(x5, s5 * EY, z5) and rin(x5, s5 * EY, z5)):
                        left_start += 1; continue
                    a5 = [h for h in hits(body, (x5, s5 * EY, z5), (0, s5, 0.0), lim=10.0) if h > 1e-6]
                    b5 = [h for h in hits(rbod, (x5, s5 * EY, z5), (0, s5, 0.0), lim=10.0) if h > 1e-6]
                    if a5 and b5:
                        dep.append((b5[0] - a5[0], s5, x5, z5))
        dmin, dmax = min(dep), max(dep)
        okd = all(abs(d[0] - 0.20) <= 0.02 for d in dep)
        print("check (5) window depth against %s: %d points, depth %.4f (%s X %.2f Z %.2f) to %.4f (%s X %.2f Z %.2f), asked 0.20 within 0.02: %s; left out: %d on a window top or bottom face, %d whose start is not metal"
              % (SLIT_REF.split("/")[-1], len(dep), dmin[0], "+Y" if dmin[1] > 0 else "-Y", dmin[2], dmin[3], dmax[0], "+Y" if dmax[1] > 0 else "-Y", dmax[2], dmax[3],
                 "PASS" if okd else "FAIL", left_face, left_start))
        if not okd:
            fails.append("window depth %.4f..%.4f, not 0.20 within 0.02" % (dmin[0], dmax[0]))
    for s5 in (1, -1):
        ex = {}
        for x5 in (0.0, 1.25, 2.5):
            hs = [h for h in hits(body, (x5, s5 * 6.45, 0.60), (0, s5, 0.0), lim=10.0) if h > 1e-6]
            ex[x5] = hs[0] if hs else None
        d0, d2 = ex[1.25] - ex[0.0], ex[1.25] - ex[2.5]
        floor_ok = all(inside(x5, s5 * (6.45 + ex[x5] - 0.05), 0.60) for x5 in (0.0, 2.5))
        print("check (5) printed only (bar comparison, superseded by the depth above): blind windows, %s side, Z 0.60: wall to the outside %.4f at X 0 (window), %.4f at X 1.25 (bar), %.4f at X 2.5 (window); depth %.4f and %.4f (asked 0.20 within 0.02); 0.05 inside each window floor is metal: %s"
              % ("+Y" if s5 > 0 else "-Y", ex[0.0], ex[1.25], ex[2.5], d0, d2, floor_ok))
        # lead's ruling 2: the depth is the one read against the windowless file above; this bar comparison is printed only
        if not floor_ok:
            fails.append("blind windows %s side: window floor not metal" % ("+Y" if s5 > 0 else "-Y"))

# check (4), bar 3: the fold where the block meets the band, from this file's body (junc_angle method, copied here)
from build123d import Vertex as _V


def _outward(shape, face, p):
    n = face.normal_at(p)
    q = Vector(p.X + 0.002 * n.X, p.Y + 0.002 * n.Y, p.Z + 0.002 * n.Z)
    return Vector(-n.X, -n.Y, -n.Z) if shape.is_inside(q) else n


def _ang(a, b):
    return math.degrees(math.acos(max(-1.0, min(1.0, a.dot(b) / (a.length * b.length)))))


def fold_station(shape, x0, side):
    op = BRepAlgoAPI_Section(shape.wrapped, gp_Pln(gp_Pnt(x0, 0, 0), gp_Dir(1, 0, 0)))
    op.Build()
    ends = []
    for e in _Compound(op.Shape()).edges():
        for t, sg in ((0.0, 1.0), (1.0, -1.0)):
            d = e.tangent_at(t)
            ends.append((e @ t, Vector(sg * d.X, sg * d.Y, sg * d.Z)))
    verts = []
    for p, _ in ends:
        if side * p.Y > 6.0 and -1.5 < p.Z < 3.70 and not any((p - v).length < 1e-5 for v in verts):
            verts.append(p)
    fcs = shape.faces()
    rows = []
    for p in verts:
        vx = _V(p.X, p.Y, p.Z)
        ns = [_outward(shape, f, p) for f in fcs if f.distance_to(vx) < 1e-4]
        na = max([_ang(ns[i], ns[j]) for i in range(len(ns)) for j in range(i + 1, len(ns))] or [0.0])
        ts = [d for q, d in ends if (q - p).length < 1e-5]
        ta = max([180.0 - _ang(ts[i], ts[j]) for i in range(len(ts)) for j in range(i + 1, len(ts))] or [0.0])
        rows.append((p.Y, p.Z, na, ta))
    return sorted(rows, key=lambda r: r[1])
fold_worst = 0.0
win_edges = []
for side in (1, -1):
    for x0 in (-3.5, -1.75, 0.0, 1.75, 3.5, -4.5, 4.5, -5.5, 5.5):
        rows = fold_station(body, x0, side)
        if SLIT_Z0 is not None and any(a - 0.003 <= x0 <= b + 0.003 for a, b in WINX + (SLITX,)):
            # lead's ruling 1: vertices on the slit's and windows' own faces (top plane Z 1.53, bottom plane at the slot bottom)
            # are left out of the skin fold figure and printed apart
            edge = [r for r in rows if abs(r[1] - WIN_TOP) < 0.003 or abs(r[1] - SLIT_Z0) < 0.003]
            win_edges += [(max(r[2], r[3]), x0, side, r) for r in edge]
            rows = [r for r in rows if r not in edge]
        m = max([max(r[2], r[3]) for r in rows] or [0.0])
        band = abs(x0) <= 3.5
        if band:
            fold_worst = max(fold_worst, m)
        big = [r for r in rows if max(r[2], r[3]) >= 0.5]
        print("check (4) fold, %s side, X %+.2f%s: largest angle %.3f deg over %d vertices%s" % (
            "+Y" if side > 0 else "-Y", x0, "" if band else " (printed only, outside the 5 stations)", m, len(rows),
            (": " + "; ".join("Y %.3f Z %.3f normals %.3f tangents %.3f" % r for r in big)) if big else ""))
fold_ok = fold_worst < 2.0
if SLIT_Z0 is not None:
    we = max(win_edges) if win_edges else None
    print("check (4) window edges (left out of the skin fold): %d vertices, largest angle %s" % (len(win_edges),
          ("%.3f deg at X %+.2f %s Y %.3f Z %.3f" % (we[0], we[1], "+Y" if we[2] > 0 else "-Y", we[3][0], we[3][1])) if we else "none"))
print("check (4) fold over the 5 stations on both long sides: largest %.3f deg, asked under 2 degrees" % fold_worst)
print("FOLD PASS" if fold_ok else "FOLD FAIL largest angle %.3f deg at the block-to-band junction" % fold_worst)
if FOLD_GATE and not fold_ok:
    fails.append("fold %.3f deg at the junction" % fold_worst)

print("findings: %d" % len(fails))
for f in fails:
    print("  " + f)
print("RESULT PASS" if not fails else "RESULT FAIL " + "; ".join(fails))
sys.exit(1 if fails else 0)
