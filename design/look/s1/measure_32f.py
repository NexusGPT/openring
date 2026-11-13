#!/usr/bin/env python3
"""Measure the merged32f exterior from its STEP file (the geometry itself, no number taken from exterior.py).

Run:  ../../.venv/bin/python measure_32f.py [<step>] [--compare <merged32e step>]
Default step: out/ring-merged32f.step. Prints:
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
STEP = args[0] if args else OUT + "/ring-merged32f.step"

WALL_MIN = 0.40
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
print("thinnest metal on each side over the depths 0.1, 0.2, 0.3: " + ", ".join("%s %.3f" % (k, v) for k, v in side_min.items()) + " (rule %.2f at 0.1, as check_thin.py)" % WALL_MIN)

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
r1 = Pos(-13.25, -4.7, 3.5) * Box(0.8, 0.8, 0.6)
left1 = {n: round(vol(s & r1), 6) for n, s in parts.items() if n != "glass" and vol(s & r1) > 1e-7}
print("round-1 light place X -13.65..-12.85, Y -5.1..-4.3, Z 3.2..3.8: solids other than the glass there: %s" % (left1 or "none"))
if left1:
    fails.append("solid at X -13.25, Y -4.7")

# ---- old light place
old = Pos(-12.0, 0.0, 3.85) * Box(1.0, 1.0, 0.3)
left = {n: vol(s & old) for n, s in parts.items() if n != "glass"}
gold = (parts["glass"] & old)
gtop = gold.bounding_box().max.Z if vol(gold) > 0 else None
print("old light place X -12.5..-11.5, Y -0.5..0.5, Z 3.70..4.00: solids other than the glass there: %s; glass top there Z %s"
      % ({n: round(v, 5) for n, v in left.items() if v > 1e-7} or "none", "%.4f" % gtop if gtop is not None else "none"))
if any(v > 1e-7 for v in left.values()):
    fails.append("solid left at the old light place")
if gtop is not None and gtop > 3.85 + 1e-4:
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

print("findings: %d" % len(fails))
for f in fails:
    print("  " + f)
print("RESULT PASS" if not fails else "RESULT FAIL " + "; ".join(fails))
sys.exit(1 if fails else 0)
