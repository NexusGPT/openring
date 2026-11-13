"""Fit check of the case (C5d), read from the exported STEP files in out/parts/ and the ring: the accepted exterior merged32h, one real file per
size US 7 to 13 (design/look/s1/out/ring-merged32h-us<n>.step), and the ring's own pad positions read from the inside model's placement file
(design/mech/thin/placement.csv, rows pad_<net>; CASE_PLACEMENT points the check at another copy, for the can-fail run). The pins in out/parts were
built from the placement file at build time; this check reads the file again and fails when the pins no longer meet the pads it lists.

Exit 1 when any of these fails, for ring sizes US 7 to 13 (the per-size rings use COMPUTED bores, see case.py):
 1. two parts of the assembly (case parts plus the US 9 ring seated) intersect by more than 0.001 mm3 (every pair);
 2. the ring does not seat flat: band bottom not on the floor (gap outside -0.001 to 0.05 mm) or not on both flanks of the V wall;
    a ring part intersects a case part (every size);
 3. a spring pin does not meet the pad of its own net (pads from placement.csv): lateral offset above 0.1 mm, or pin height outside the contact
    window (travel);
 4. the closed lid is closer than 0.5 mm to the ring; the lid swung open (0 to the open angle) touches the ring or another part, or
    still covers the ring at the open angle;
 5. the cell, main board, USB-C socket or light is closer than 0.3 mm to a wall of the shell;
 6. a wrong placement (turned 180 degrees, across, flipped over) fits the pocket AND the pins find pads on it;
 7. (information only, open item R1) the roll play: how far the ring can turn about its own axis inside the pocket and what that does to the pad row;
 8. (new in C5) no outside face of the shell, lid or bottom plate is planar except the seam faces (a planar face counts as skin when its centre lies on the
    outside skin: within 0.012 of the skin's scale factor, about 0.5 mm, for C5b; on the bounding box faces for the C4 box); the same test run on the C4 shape (look/c4_out/parts) must find planar outside faces (self-test);
 9. (information only since C5b) plan outline smallest radius of curvature and the share of the wall within 5 degrees of vertical;
10. (new) the seam gap is 0.3 mm; the USB-C mouth sits 0.3 mm behind the skin; the charge light hole is 1.0 mm.
11, 12. (C5c) the lid's dome has no crease; the crown is one arc.
13. (C5d) the ring's round joystick (the real per-size part) is at least 0.3 mm from every case part, closed, at every size US 7 to 13 (printed per size);
14. (C5d) the pin holder is one valid solid, its front is at least 0.2 mm from the band at every size, and its bores hold the four pin barrels
    without contact (pairs in test 1 and 2a).
15. (r4) the main board and the pin board in the model are the routed board files as they are now (read again by KiCad's Python and kicad-cli);
    no part body on the main board's back face; every part body at least 0.3 mm from every rigid case part and not touching a lead.
16. (r4) the nine leads (W1 to W4, W7, the two thermistor leads, the cell leads W5 and W6): free room at least 0.05 mm to everything they are not
    soldered or glued to; cut length (path + 5 mm) within the parts list.
17. (r4) lid open, the ring lifted straight up in 0.25 mm steps until clear, every size: no common volume, smallest free space at least 0.10 mm except
    the seat contacts (pins, flank faces), printed with where it is.
CASE_CHECK_SKIP_R4=1 leaves out 15 to 17 (used only to compare with the C5d check).
Prints a last line starting with "case_check: PASS" or "case_check: FAIL" and the number of pairs checked.
"""
import itertools
import json
import math
import os
import sys

from build123d import Edge, GeomType, Pos, Rot, Vector, import_step

import case as C

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = C.OUT
LIMIT = 0.001
fails = 0
pairs = 0


def fail(msg):
    global fails
    fails += 1
    print("FAIL", msg)


def vmin_x(shape):
    return shape.bounding_box().min.X


def planar_outside(parts, z_seams, on_skin):
    """planar faces of the given parts that lie on the outside skin (on_skin(centre) is true) and are not seam faces. A face that is cut into the
    skin (the walls of the USB-C mouth, its chamfer, the light hole) and the faces inside the case are not skin. Returns (count, descriptions)."""
    bad = []
    for name, shp in parts.items():
        for f in shp.faces():
            if f.geom_type != GeomType.PLANE:
                continue
            c = f.center()
            n = f.normal_at(c)
            if any(abs(c.Z - z) < 0.02 and abs(n.Z) > 0.99 for z in z_seams):
                continue
            if abs(c.Z) < 0.5 and n.Z < -0.99:
                continue                                            # the foot's contact face and the marking field's floor
            if on_skin(c):
                bad.append(f"{name} face at ({c.X:.1f}, {c.Y:.1f}, {c.Z:.1f}) normal ({n.X:.2f}, {n.Y:.2f}, {n.Z:.2f}) area {f.area:.1f}")
    return len(bad), bad


def near_distance(a, b, far=3.0):
    """distance from the moving part `a` to the solid `b`, measured FACE BY FACE of `a` (a solid-to-solid distance_to returned 0.000 for pairs that are
    0.3 mm or more apart: a classification fault, see look/c5c-notes.md); pairs whose bounding boxes are more than `far` mm apart return `far`"""
    ba, bb = a.bounding_box(), b.bounding_box()
    gx = max(ba.min.X - bb.max.X, bb.min.X - ba.max.X, 0.0)
    gy = max(ba.min.Y - bb.max.Y, bb.min.Y - ba.max.Y, 0.0)
    gz = max(ba.min.Z - bb.max.Z, bb.min.Z - ba.max.Z, 0.0)
    if math.sqrt(gx * gx + gy * gy + gz * gz) > far:
        return far
    return min(f.distance_to(b) for f in a.faces())


def lid_crease(lid, zmin, axis, excl, zmax=None, r_excl=1.0, tol=0.005, ang=0.01):
    """largest angle (degrees) between the normals of two neighbour triangles of the lid's outer surface (above zmin, facing up or out, more than r_excl mm
    from the axis: the apex fan has noisy normals; and outside the thumb dimple, a circle (x, y, radius) in which the surface is deliberately curved)"""
    import numpy as np
    v, t = lid.tessellate(tol, ang)
    V = np.array([[p.X, p.Y, p.Z] for p in v])
    T = np.array(t)
    key = np.round(V, 4)
    _, idx, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
    inv = inv.ravel()
    W, T = V[idx], inv[T]
    a, b, c_ = W[T[:, 0]], W[T[:, 1]], W[T[:, 2]]
    n = np.cross(b - a, c_ - a)
    ar = np.linalg.norm(n, axis=1)
    ok = ar > 1e-9
    n[ok] /= ar[ok, None]
    cen = (a + b + c_) / 3
    sel = ok & (cen[:, 2] > zmin) & (n[:, 2] > -0.2) & (np.hypot(cen[:, 0] - axis[0], cen[:, 1] - axis[1]) > r_excl)
    if zmax is not None:
        sel &= cen[:, 2] < zmax
    if excl is not None:
        sel &= np.hypot(cen[:, 0] - excl[0], cen[:, 1] - excl[1]) > excl[2]
    edges = {}
    for fi in np.where(sel)[0]:
        for e in ((T[fi, 0], T[fi, 1]), (T[fi, 1], T[fi, 2]), (T[fi, 2], T[fi, 0])):
            edges.setdefault((min(e), max(e)), []).append(fi)
    worst = 0.0
    for fs in edges.values():
        if len(fs) == 2:
            d = float(np.clip(np.dot(n[fs[0]], n[fs[1]]), -1, 1))
            worst = max(worst, math.degrees(math.acos(d)))
    return worst, int(sel.sum())


def crown_profile(lid, xc, rmax, step=0.5):
    """top surface height of the lid along the line y = 0 from the axis outward (vertical lines through the solid)"""
    out = []
    r = 0.0
    while r <= rmax + 1e-9:
        hit = lid.intersect(Edge.make_line((xc + r, 0, 20), (xc + r, 0, 60)))
        zs = [v.Z for e in (hit or []) for v in e.vertices()]
        out.append((r, max(zs) if zs else float("nan")))
        r += step
    return out


def inflections(prof, tol=0.003):
    """second differences of z(r) with the wrong sign (z(r) must stay concave down from the apex to the end): list of (r, second difference)"""
    bad = []
    for i in range(1, len(prof) - 1):
        d2 = prof[i - 1][1] - 2 * prof[i][1] + prof[i + 1][1]
        if d2 > tol:
            bad.append((prof[i][0], d2))
    return bad


def main():
    global pairs
    with open(os.path.join(OUT, "case_params.json")) as f:
        prm = json.load(f)
    parts = {n: import_step(os.path.join(OUT, "parts", f"{n}.step")) for n in prm["parts"]}
    rings = {n: C.Ring(n) for n in prm["sizes"]}
    zb, zf = prm["zb"], prm["zf"]
    print(f"ring sizes checked: US {prm['sizes']} (real exterior files: {', '.join(os.path.basename(C.RING_STEP_N.format(n=n)) for n in prm['sizes'])})")
    pl = C.PL
    print(f"pads read from {pl['path']}: row at X {pl['x']:.3f} mm (spread {pl['x_spread']:.3f}), discs {pl['d']:.2f} x {pl['t']:.2f} mm, "
          f"face radius {pl['r_face']:.4f} about Z {pl['zc']:.4f} (fit spread {pl['r_fit_spread']:.4f}), arc pitch {pl['pitch']:.4f} mm; "
          + "; ".join(f"{p_['net']} ({p_['ref']}) arc {p_['s']:+.4f}" for p_ in pl["pads"]))
    bp = prm.get("placement", {})
    if bp:
        print(f"model built from {bp['path']}: row at X {bp['x']:.3f} mm, arc pitch {bp['pitch']:.4f} mm")
    only = os.environ.get("CASE_CHECK_ONLY_R4", "")                 # broken copies of r4: only new tests ("1" = 15, 16, 17; or a list like "15,16"); the full check is the proof run
    if only:
        sel = {15, 16, 17, 18} if only == "1" else {int(t) for t in only.split(",")}
        print(f"CASE_CHECK_ONLY_R4={only}: tests 1 to 14 left out; runs {sorted(sel)}")
        if 15 in sel:
            test15_boards(parts, prm)
        if 16 in sel:
            test16_leads(parts, prm)
        if 17 in sel:
            test17_lift(parts, prm, rings)
        if 18 in sel:
            test18_contacts(parts, prm)
        print(f"pairs checked {pairs}; failures {fails}")
        print(f"case_check: {'PASS' if fails == 0 else 'FAIL'}, {pairs} pairs checked, {fails} failures, ring sizes US {prm['sizes']} (only tests {sorted(sel)})")
        return 1 if fails else 0

    # 1. assembly with the US 9 ring: every pair
    r9 = rings[9].parts_in_case(zb)
    allp = dict(parts)
    allp.update({f"ring_US9_{k}": v for k, v in r9.items() if k != "pads"})
    worst = 0.0
    for a, b in itertools.combinations(sorted(allp), 2):
        if a.startswith("ring_") and b.startswith("ring_"):
            continue
        pairs += 1
        v = C.common(allp[a], allp[b])
        worst = max(worst, v if v == v else 0)
        if not (v <= LIMIT):
            fail(f"intersection {a} x {b}: {v:.4f} mm3")
    print(f"assembly US 9: {len(allp)} parts, every pair, largest intersection {worst:.6f} mm3")

    shell = parts["shell"]
    pin_names = sorted(prm["pin_nets"])                      # pin_P<n>_<net>, the net is the pad it must meet
    net_of = prm["pin_nets"]
    k_of_net = {p_["net"]: k for k, p_ in enumerate(pl["pads"])}
    if sorted(net_of.values()) != sorted(k_of_net):
        fail(f"pin nets {sorted(net_of.values())} are not the placement's pad nets {sorted(k_of_net)}")
    lo, hi = prm["pin_window"]
    pin_heights_all = []
    for n in prm["sizes"]:
        rg = rings[n]
        rc = rg.parts_in_case(zb)
        pin_n, face_n = {}, []
        for i, pn in enumerate(pin_names):
            fx, fy, fz = C.pad_face_xyz(n, k_of_net[net_of[pn]], zb, pl)     # face centre of the pad of this pin's net, from placement.csv
            face_n.append(Vector(fx, fy, fz))
            pb = parts[pn].bounding_box()
            # the pin at this size: same base plane and axis, plunger pushed in until its tip is C.TIP_GAP from the pad face
            pin_n[pn] = C.make_pin(pb.max.X, (pb.min.Y + pb.max.Y) / 2, (pb.min.Z + pb.max.Z) / 2, pb.max.X - fx - C.TIP_GAP)
        # 2a. every ring part against every case part (pins at their working compression for this size)
        worst = 0.0
        for a in sorted(parts):
            for k in ("body", "glass", "joystick"):
                pairs += 1
                v = C.common(pin_n.get(a, parts[a]), rc[k])
                worst = max(worst, v if v == v else 0)
                if not (v <= LIMIT):
                    fail(f"US {n}: ring {k} x {a} intersect {v:.4f} mm3")
        print(f"US {n}: ring parts x case parts ({3 * len(parts)} pairs), largest intersection {worst:.6f} mm3")
        # 2b. floor and flanks
        xl = prm["cx"][str(n)] - (prm["ri"][str(n)] + 1.3)
        line = Edge.make_line((xl, 0, 0), (xl, 0, 60))
        zr = [v.Z for e in (rc["body"].intersect(line) or []) for v in e.vertices()]
        zs_ = [v.Z for sh_ in (shell, parts["liner"]) for e in (sh_.intersect(line) or []) for v in e.vertices() if abs(v.Z - zf) < 0.3]      # the floor is the liner's top face in C5c
        gf = (min(zr) - max(zs_)) if zr and zs_ else float("nan")
        pairs += 1
        okf = gf == gf and -0.001 <= gf <= 0.05
        print(f"US {n}: band bottom to floor {gf:.4f} mm: {'OK' if okf else 'FAIL'}")
        if not okf:
            fail(f"US {n} floor gap {gf}")
        for sd, ys in (("-Y", [-y for y in (3.6, 4.0, 4.4, 4.8, 5.2, 5.6)]), ("+Y", [3.6, 4.0, 4.4, 4.8, 5.2, 5.6])):
            g = []
            for y in ys:
                line = Edge.make_line((-30, y, zb), (60, y, zb))
                xs = [v.X for sh_ in (shell, parts["liner"]) for e in (sh_.intersect(line) or []) for v in e.vertices()]      # the V rests belong to the liner in C5c
                xr = [v.X for e in (rc["body"].intersect(line) or []) for v in e.vertices()]
                xf = [x for x in xs if abs(x - (prm["x_a"] + abs(y) * C.TANPHI)) < 0.3]
                xrb = [x for x in xr if abs(x - (prm["cx"][str(n)] - math.sqrt(prm["r0"][str(n)] ** 2 - y * y))) < 0.3]
                if xf and xrb:
                    g.append((min(xrb) - max(xf)) * C.COSPHI)
            pairs += 1
            gmin = min(g) if g else None
            ok = gmin is not None and -0.001 <= gmin <= 0.05 and len(g) == len(ys)
            print(f"US {n}: flank {sd}: smallest normal gap band to flank {gmin if gmin is None else round(gmin, 4)} mm over {len(g)} lines: {'OK' if ok else 'FAIL'}")
            if not ok:
                fail(f"US {n} flank {sd} gap {gmin}")
        # 2c. post to bore
        dpost = min(parts[k].distance_to(rc["body"]) for k in ("post", "pin_board_pcb2", "pin_board_pcb2_wing_L", "pin_board_pcb2_wing_R"))
        dhold = near_distance(parts["pin_holder"], rc["body"])
        pairs += 2
        print(f"US {n}: post and pin board to the ring body {dpost:.3f} mm (needs > 0.2): {'OK' if dpost > 0.2 else 'FAIL'}")
        print(f"US {n}: 14 pin holder front to the ring body {dhold:.3f} mm, face by face (needs > 0.2): {'OK' if dhold > 0.2 else 'FAIL'}")
        if dpost <= 0.2:
            fail(f"US {n} post too close {dpost}")
        if dhold <= 0.2:
            fail(f"US {n} pin holder too close {dhold}")
        # 13. the round joystick against every case part (closed), face by face of the joystick
        dj = {k: near_distance(rc["joystick"], parts[k]) for k in parts}
        kj = min(dj, key=dj.get)
        pairs += len(parts)
        okj = dj[kj] >= 0.3 and C.common(rc["joystick"], parts[kj]) <= LIMIT
        print(f"US {n}: 13 joystick (real part, {C.joy_deg(n):.0f} degrees) clearance to the case {dj[kj]:.3f} mm, nearest part {kj} (needs >= 0.3): {'OK' if okj else 'FAIL'}")
        if not okj:
            fail(f"US {n} joystick clearance {dj[kj]:.3f} to {kj}")
        # 3. pins against pads
        for i, pn in enumerate(pin_names):
            pb = parts[pn].bounding_box()
            base_x = pb.max.X
            py, pz = (pb.min.Y + pb.max.Y) / 2, (pb.min.Z + pb.max.Z) / 2
            fc = face_n[i]
            off = math.hypot(py - fc.Y, pz - fc.Z)
            height = base_x - fc.X
            pin_heights_all.append(height)
            ok = off <= 0.1 and lo <= height <= hi
            pairs += 1
            print(f"US {n} {pn}: pad {net_of[pn]} face centre ({fc.X:.3f}, {fc.Y:.3f}, {fc.Z:.3f}); pin axis ({py:.3f}, {pz:.3f}); lateral offset {off:.3f} <= 0.1; "
                  f"pin height {height:.3f} (window {lo:.2f} to {hi:.2f}): {'OK' if ok else 'FAIL'}")
            if not ok:
                fail(f"US {n} {pn} offset {off:.3f} height {height:.3f}")
        # 4a. closed lid clearance
        dmin = min(parts["lid"].distance_to(rc[k]) for k in ("body", "glass", "joystick"))
        pairs += 1
        print(f"US {n}: closed lid to ring {dmin:.3f} mm (needs >= 0.5): {'OK' if dmin >= 0.5 else 'FAIL'}")
        if dmin < 0.5:
            fail(f"US {n} lid clearance {dmin:.3f}")
    spread = max(pin_heights_all) - min(pin_heights_all)
    print(f"pin travel used over US 7 to 13 and 4 pins: heights {min(pin_heights_all):.3f} to {max(pin_heights_all):.3f}, spread {spread:.3f} mm "
          f"(plunger travel from free height {C.PIN['free_h']}: {C.PIN['free_h'] - max(pin_heights_all):.3f} to {C.PIN['free_h'] - min(pin_heights_all):.3f} mm)")

    # 4b. lid swung open: sweep about the pivot
    lid = parts["lid"]
    px, py = prm["pivot"]
    ang = prm["lid_open_deg"]
    steps = [ang * i / 12 for i in range(13)]
    lid_group = ("lid", "lid_seam_trim")
    others = [k for k in parts if k not in ("lid", "lid_seam_trim", "hinge_pivot", "magnet_lid") and not k.startswith("glide")]
    minring, minother, maxov = 1e9, 1e9, 0.0
    for a in steps:
        for ln in lid_group:
            lo_ = Pos(px, py, 0) * (Rot(0, 0, a) * (Pos(-px, -py, 0) * parts[ln]))
            for n in (7, 9, 13):
                rc = rings[n].parts_in_case(zb)
                for k in ("body", "glass", "joystick"):
                    pairs += 1
                    minring = min(minring, near_distance(lo_, rc[k]))
            for k in others:
                pairs += 1
                minother = min(minother, near_distance(lo_, parts[k]))
            for k in ("shell", "liner", "post", "seam_trim", "magnet_base", "base_plate"):
                pairs += 1
                maxov = max(maxov, C.common(lo_, parts[k]))
            for n in (7, 9, 13):
                rc = rings[n].parts_in_case(zb)
                for k in ("body", "glass", "joystick"):
                    pairs += 1
                    maxov = max(maxov, C.common(lo_, rc[k]))
    lo_end = Pos(px, py, 0) * (Rot(0, 0, ang) * (Pos(-px, -py, 0) * lid))
    cover = C.prism_xy(prm_hull(prm), 0.0, 100.0)
    pocket = C.box(prm["px0"], prm["px1"], prm["py0"], prm["py1"], 0.0, 100.0)
    ov = C.common(lo_end, cover) + C.common(lo_end, pocket)
    pairs += 2
    ok = minring >= 0.5 and minother >= 0.3 and ov <= LIMIT and maxov <= LIMIT and minother > 0.0 and minring > 0.0
    print(f"lid swung 0 to {ang:.0f} degrees in {len(steps)} steps: closest to a ring (US 7, 9, 13) {minring:.3f} mm, closest to another case part {minother:.3f} mm (face-by-face distance), largest common volume with any part {maxov:.6f} mm3; "
          f"lid over the well and pocket at {ang:.0f} degrees: {ov:.4f} mm3: {'OK' if ok else 'FAIL'}")
    if not ok:
        fail(f"lid swing ring {minring:.3f} other {minother:.3f} cover {ov:.3f}")

    # 5. electronics inside the shell
    walls = [parts["shell"], parts["base_plate"]]
    # r4: the socket and the light are parts of main_board (the board's own 3D export, children labelled by reference); measured on their own
    mb_kids = {c.label: c for c in parts["main_board"].children}
    sub = {"cell_dnk852338": parts["cell_dnk852338"], "main_board": parts["main_board"], "J1_usb4105": mb_kids.get("J1"), "LED1": mb_kids.get("LED1")}
    for k in ("cell_dnk852338", "main_board", "J1_usb4105", "LED1"):
        if sub[k] is None:
            fail(f"{k}: not found in out/parts")
            continue
        d = min(sub[k].distance_to(w) for w in walls)
        pairs += 1
        print(f"{k}: distance to the shell walls {d:.3f} mm (needs >= 0.3): {'OK' if d >= 0.3 else 'FAIL'}")
        if d < 0.3:
            fail(f"{k} wall distance {d:.3f}")

    # 6. wrong placements
    for n in (7, 9, 13):
        rg = rings[n]
        cxn = prm["cx"][str(n)]
        poses = {
            "turned": lambda s: Pos(cxn, 0, 0) * (Rot(0, 0, 180) * (Pos(-cxn, 0, 0) * s)),
            "across": lambda s: Pos(cxn, 0, 0) * (Rot(0, 0, 90) * (Pos(-cxn, 0, 0) * s)),
            "flipped": lambda s: Pos(0, 0, zb) * (Rot(180, 0, 0) * (Pos(0, 0, -zb) * s)),
        }
        for wname, fn in poses.items():
            rc = {k: fn(v) for k, v in rg.parts_in_case(zb).items()}
            worst = 0.0
            for a in ("shell", "post", "pin_board_pcb2", "pin_board_pcb2_wing_L", "pin_board_pcb2_wing_R", "pin_holder", "lid"):
                for k in ("body", "glass", "joystick"):
                    pairs += 1
                    worst = max(worst, C.common(parts[a], rc[k]))
            padc = [s.center() for s in rc["pads"].solids()]
            dpin = min(math.dist((parts[pn].bounding_box().min.X, (parts[pn].bounding_box().min.Y + parts[pn].bounding_box().max.Y) / 2,
                                  (parts[pn].bounding_box().min.Z + parts[pn].bounding_box().max.Z) / 2), (c.X, c.Y, c.Z))
                       for pn in pin_names for c in padc)
            pairs += 1
            blocked = worst >= 1.0
            safe = dpin > 1.0
            if wname == "flipped":
                ok = blocked or safe
                msg = "blocked by the case" if blocked else ("not blocked, but no pin reaches a pad (closest %.2f mm)" % dpin)
            else:
                ok = blocked
                msg = "blocked by the case" if blocked else "FITS"
            print(f"US {n} wrong placement '{wname}': largest intersection with the case {worst:.2f} mm3; pin tip to nearest pad {dpin:.2f} mm; {msg}: {'OK' if ok else 'FAIL'}")
            if not ok:
                fail(f"US {n} wrong placement {wname}: intersection {worst:.2f}, pin to pad {dpin:.2f}")

    # 7. roll play: ring turned about its own (vertical) axis inside the pocket, in 0.25 degree steps, until it touches the shell
    for n in prm["sizes"]:
        rg = rings[n]
        cxn = prm["cx"][str(n)]
        res = []
        for sign in (1, -1):
            th = 0.0
            while th < 8.0:
                th += 0.25
                rc = rg.parts_in_case(zb)
                moved = {k: Pos(cxn, 0, 0) * (Rot(0, 0, sign * th) * (Pos(-cxn, 0, 0) * rc[k])) for k in ("body", "glass", "joystick")}
                pairs += 1
                if max(C.common(shell, moved[k]) for k in moved) > LIMIT:
                    break
            res.append(th - 0.25)
        shift = max(rg.ri * math.sin(math.radians(t)) for t in res)
        allow = C.PAD_D / 2 - C.PIN["plunger_d"] / 2
        okr = shift <= allow
        print(f"US {n}: roll play +{res[0]:.2f} / -{res[1]:.2f} degrees before the ring touches the shell (0.25 degree steps); pad row moves at most {shift:.3f} mm "
              f"(a {C.PIN['plunger_d']} mm pin tip stays on a {C.PAD_D} mm pad up to {allow:.2f} mm): {'OK' if okr else 'FAIL'}")
        pairs += 1
        if not okr:
            fail(f"US {n} roll play moves the pad row {shift:.3f} mm (allowed {allow:.2f})")

    # 8. no planar outside face (new in C5)
    outer_parts = {k: parts[k] for k in ("shell", "lid", "base_plate", "seam_trim", "lid_seam_trim", "usb_bezel", "light_window", "foot")}
    sys.path.insert(0, os.path.join(HERE, "look"))
    import pebble as PB
    PB.PEB.update(prm["pebble"])
    skin5 = lambda p: PB.rho_point(p.X, p.Y) >= float(PB.rho_of_z(p.Z, prm["h_tot"])) - 0.012
    nbad, bad = planar_outside(outer_parts, (prm["z_split"], prm["z_lid0"]), skin5)
    pairs += len(outer_parts)
    print(f"planar outside faces of shell, lid, bottom plate (seam faces excluded): {nbad}: {'OK' if nbad == 0 else 'FAIL'}")
    for b in bad[:10]:
        print("   ", b)
    if nbad:
        fail(f"{nbad} planar outside faces")
    c4 = {n: import_step(os.path.join(HERE, "look", "c4_out", "parts", f"{n}.step")) for n in ("shell", "lid", "base_plate")}
    bbs = [v.bounding_box() for v in c4.values()]
    lo = (min(b.min.X for b in bbs), min(b.min.Y for b in bbs), min(b.min.Z for b in bbs))
    hi = (max(b.max.X for b in bbs), max(b.max.Y for b in bbs), max(b.max.Z for b in bbs))
    skin4 = lambda p: any(abs(v - l) < 0.05 or abs(v - h) < 0.05 for v, l, h in zip((p.X, p.Y, p.Z), lo, hi))
    n4, bad4 = planar_outside(c4, (36.16, 36.56), skin4)
    pairs += 1
    print(f"self-test on the C4 shape (look/c4_out/parts): {n4} planar outside faces found: {'OK, the test sees them' if n4 > 0 else 'FAIL, the test is blind'}")
    for b in bad4[:6]:
        print("   ", b)
    if n4 == 0:
        fail("planar test finds nothing on the C4 shape")

    # 9. plan outline and profile (new in C5)
    rmin = PB.min_plan_radius()
    vf = PB.vertical_fraction(prm["h_tot"])
    pairs += 2
    # C5b: the owner's brief dropped the C5 limits (plan radius 12 mm, 40 percent vertical wall): size comes first, so these two are information only
    print(f"INFO plan outline smallest radius of curvature {rmin:.2f} mm (C5 limit 12 dropped in C5b: the 40 mm cell's corners set it)")
    print(f"INFO wall within 5 degrees of vertical over at most {vf * 100:.1f} percent of the height (C5 limit 40 dropped in C5b)")

    # 10. seam gap, USB mouth lip, light dot
    gap = prm["z_lid0"] - prm["z_split"]
    lip = prm["j1_front"] - prm["skin_x_at_j1"]
    pairs += 3
    okg, okl, okd = abs(gap - 0.3) < 1e-6, abs(lip - 0.3) < 0.02, abs(C.DOT_D - 1.0) < 1e-9
    print(f"seam shadow gap {gap:.3f} mm (needs 0.3): {'OK' if okg else 'FAIL'}; USB-C mouth {lip:.3f} mm behind the skin (needs 0.3): {'OK' if okl else 'FAIL'}; light dot {C.DOT_D:.2f} mm (needs 1.0): {'OK' if okd else 'FAIL'}")
    if not (okg and okl and okd):
        fail("seam, lip or dot")

    # 11a/11b (new in C5c): the lid's dome has no crease (facets above the top edge's start differ by at most 2 degrees, outside the thumb dimple);
    # the top edge band (ZW1 to ZW1 + 0.7 mm) has a radius of curvature of at least 0.30 mm and no facet pair above 10 degrees
    dx_, dy_, drs = prm["dimple"]
    zw1 = prm["pebble"]["ZW1"]
    axis_ = (prm["pebble"]["XC"], 0.0)
    mx_, nt_ = lid_crease(parts["lid"], zw1 + 0.7, axis_, (dx_, dy_, 6.0))
    pairs += 1
    print(f"11a lid dome (z above {zw1 + 0.7:.2f} mm): {nt_} facets, largest angle between neighbour facets {mx_:.2f} degrees (apex fan within 1 mm of the axis and the dimple's 6 mm circle left out; needs <= 2): {'OK' if mx_ <= 2.0 else 'FAIL'}")
    if mx_ > 2.0:
        fail(f"lid dome crease {mx_:.2f} degrees")
    redge = prm["pebble"]["VT"] ** 2 / prm["pebble"]["ET"]
    mb_, nb_ = lid_crease(parts["lid"], zw1 - 0.15, axis_, (dx_, dy_, 6.0), zmax=zw1 + 0.7)
    pairs += 1
    okb = redge >= 0.30 and mb_ <= 10.0
    print(f"11b lid edge band (z {zw1 - 0.15:.2f} to {zw1 + 0.7:.2f} mm): smallest radius of curvature of the edge ellipse {redge:.3f} mm (needs >= 0.30), {nb_} facets, largest angle between neighbour facets {mb_:.2f} degrees (needs <= 10): {'OK' if okb else 'FAIL'}")
    if not okb:
        fail(f"lid edge band radius {redge:.3f} angle {mb_:.2f}")
    # 12. the crown is one arc: z(r) along y = 0 has no inflection from the apex to the wall (new in C5c)
    prof = crown_profile(parts["lid"], prm["pebble"]["XC"], 21.0)
    bad = inflections(prof)
    pairs += 1
    zs_ = [z for r, z in prof]
    print(f"lid crown profile along y = 0 ({len(prof)} points, apex z {zs_[0]:.3f}): inflection points {len(bad)} (needs 0): {'OK' if not bad and all(z == z for z in zs_) else 'FAIL'}")
    if bad or any(z != z for z in zs_):
        fail(f"lid crown inflection at r {[round(b[0], 1) for b in bad]}")

    # 14. the pin holder is its own valid solid
    ph = parts["pin_holder"]
    pairs += 1
    okh = ph.is_valid and len(ph.solids()) == 1 and ph.volume > 50.0
    print(f"14 pin holder: {len(ph.solids())} solid, valid {ph.is_valid}, volume {ph.volume:.1f} mm3: {'OK' if okh else 'FAIL'}")
    if not okh:
        fail("pin holder solid")

    if os.environ.get("CASE_CHECK_SKIP_R4") != "1":
        test15_boards(parts, prm)
        test16_leads(parts, prm)
        test17_lift(parts, prm, rings)
        test18_contacts(parts, prm)

    print(f"pairs checked {pairs}; failures {fails}")
    print(f"case_check: {'PASS' if fails == 0 else 'FAIL'}, {pairs} pairs checked, {fails} failures, ring sizes US {prm['sizes']}")
    return 1 if fails else 0


# ---------------- r4 tests: the boards from their files, the leads, the straight lift out ----------------
RIGID_GAP = 0.3          # 15b: a part body to any rigid case part (as test 5: 0.3 mm to the walls)
LEAD_FREE = 0.05         # 16: a lead to anything it is not soldered or glued to (wires are flexible; the modelled path must exist without touching)
LIFT_STEP = 0.25         # 17: lift step (mm)
LIFT_FREE = 0.10         # 17: smallest free space to every case part except the seat contacts (reason in the test's print line)
LIFT_EXACT = 0.5         # 17: screen value (point to point, mm) below which a step is measured exactly (sampling: ring 0.2 mm, case 0.1 mm)
STRIP_ALLOW = 5.0        # 16: two stripped and soldered ends, 2.5 mm each (board-notes.md part f allowance)
BOM_CUT = {"lead_W1": 30, "lead_W2": 30, "lead_W3": 30, "lead_W4": 30, "lead_W7": 20, "lead_W5": 40, "lead_W6": 40}   # case-bom.csv items 27, 59, 28


def _kids(shape):
    return {c.label: c for c in shape.children} if shape.children else {}


def test15_boards(parts, prm):
    """15. the main board and the pin board in the model are the board files as they are now (read again here), and every part body keeps
    RIGID_GAP from every rigid case part and does not touch a lead"""
    global pairs
    sys.path.insert(0, os.path.join(HERE, "r4"))
    import case_boards as CB
    B = CB.read(os.path.join(OUT, "boards_check"))
    bm = prm["boards"]
    x0, z0 = prm["pcb1_x0"], prm["pcb1_z"][0]
    mb, info = CB.main_board(B, x0, z0)
    fresh = {c.label: c.bounding_box() for c in mb.children}
    have = {k: v.bounding_box() for k, v in _kids(parts["main_board"]).items()}
    worst, bad = 0.0, []
    for k, bb in fresh.items():
        if k not in have:
            bad.append(f"{k} missing")
            continue
        h = have[k]
        dev = max(abs(a - b) for a, b in zip((bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z), (h.min.X, h.min.Y, h.min.Z, h.max.X, h.max.Y, h.max.Z)))
        worst = max(worst, dev)
        if dev > 0.01:
            bad.append(f"{k} moved {dev:.3f}")
    extra = sorted(set(have) - set(fresh))
    pairs += len(fresh)
    ok = not bad and not extra
    print(f"15a main board in the model = {os.path.basename(info['file'])} now: {len(fresh)} pieces (board + {len(fresh) - 1} part bodies), largest box difference {worst:.4f} mm"
          f" (needs <= 0.01; rebuild with case.py if not): {'OK' if ok else 'FAIL ' + '; '.join(bad[:6] + ['extra ' + e for e in extra[:6]])}")
    if not ok:
        fail(f"15a main board differs from its file: {bad[:6]} {extra[:6]}")
    ol = [(round(a, 4), round(b, 4)) for a, b in info["outline_case"]]
    ol0 = [(round(a, 4), round(b, 4)) for a, b in bm["main_outline"]]
    pairs += 1
    print(f"15a main board outline from the file: {len(ol)} corners, x {min(a for a, b in ol):.3f} to {max(a for a, b in ol):.3f}, y {min(b for a, b in ol):.3f} to {max(b for a, b in ol):.3f}, "
          f"thickness {info['thickness']:.3f}; same as the build: {'OK' if ol == ol0 else 'FAIL'}")
    if ol != ol0:
        fail("15a main board outline changed since the build")
    back = [b for b in info["back_side"] if b["has_model"]]
    print(f"15a main board back face: {len(info['back_side'])} footprints ({', '.join(b['ref'] for b in info['back_side'])}), {len(back)} with a body: {'OK' if not back else 'FAIL'}")
    pairs += 1
    if back:
        fail(f"15a part bodies on the main board's back face: {back}")
    # pin board: islands and pins as built
    isl_now, pinfo = CB.pin_board(B, lambda r: prm["x_b"] if r in ("P2", "P3") else prm["x_bo"], prm["z_pin"])
    for nm, s in isl_now.items():
        b1, b2 = s.bounding_box(), parts[nm].bounding_box()
        dev = max(abs(a - b) for a, b in zip((b1.min.X, b1.min.Y, b1.min.Z, b1.max.X, b1.max.Y, b1.max.Z), (b2.min.X, b2.min.Y, b2.min.Z, b2.max.X, b2.max.Y, b2.max.Z)))
        pairs += 1
        print(f"15a {nm}: y {b1.min.Y:.3f} to {b1.max.Y:.3f}, z {b1.min.Z:.3f} to {b1.max.Z:.3f}, x {b1.min.X:.3f} to {b1.max.X:.3f}; model differs by {dev:.4f}: {'OK' if dev <= 0.01 else 'FAIL'}")
        if dev > 0.01:
            fail(f"15a {nm} differs from the pin board file by {dev:.3f}")
    for ref, (py, pz) in pinfo["pins"].items():
        pn = [k for k in prm["pin_nets"] if k.startswith(f"pin_{ref}_")][0]
        pb_ = parts[pn].bounding_box()
        off = math.hypot(py - (pb_.min.Y + pb_.max.Y) / 2, pz - (pb_.min.Z + pb_.max.Z) / 2)
        pairs += 1
        print(f"15a {ref} on the pin board file at y {py:.3f} z {pz:.3f}; model pin {pn} axis offset {off:.4f} (needs <= 0.01): {'OK' if off <= 0.01 else 'FAIL'}")
        if off > 0.01:
            fail(f"15a {ref} pin board file vs model pin offset {off:.3f}")
    # 15b: every part body to the rigid case parts and to the leads
    soft = [k for k in parts if k.startswith("lead_") or k in ("TH1_bead", "insulation_sheet", "foam_pad")]   # flexible parts: no contact needed, not 0.3
    rigid = [k for k in parts if k not in soft and k != "main_board"]
    near = []
    nb = 0
    for ref, body in _kids(parts["main_board"]).items():
        if ref == "PCB1":
            continue
        nb += 1
        for k in rigid + soft:
            pairs += 1
            d = near_distance(body, parts[k], far=1.0)
            near.append((d, ref, k))
            lim = RIGID_GAP if k in rigid else 0.0
            if d < lim or (d == 0.0 and C.common(body, parts[k]) > LIMIT):
                fail(f"15b {ref} to {k} {d:.3f} mm (needs {'>= %.1f' % RIGID_GAP if k in rigid else 'no contact'})")
    near.sort()
    rg = [n for n in near if n[2] in rigid]
    sf = [n for n in near if n[2] in soft]
    print(f"15b {nb} part bodies of the main board: smallest distance to a rigid case part {rg[0][0]:.3f} mm ({rg[0][1]} to {rg[0][2]}; needs >= {RIGID_GAP}); "
          f"to a lead or the thermistor {sf[0][0]:.3f} mm ({sf[0][1]} to {sf[0][2]}; needs > 0)")
    for d, ref, k in rg[:8]:
        print(f"    15b {ref} to {k}: {d:.3f} mm")
    # 15c: the board itself (PCB1, from the file's outline) to every rigid case part except the retainer, whose posts and fence press on it by design
    pcb = _kids(parts["main_board"])["PCB1"]
    dp = sorted((near_distance(pcb, parts[k], far=1.0), k) for k in rigid if k not in ("board_retainer", "cell_dnk852338"))
    dcell = near_distance(pcb, parts["cell_dnk852338"], far=1.0)
    pairs += len(dp)
    okp = dp[0][0] >= RIGID_GAP
    print(f"15c the main board (outline from the file) to the rigid case parts: smallest {dp[0][0]:.3f} mm to {dp[0][1]}, then {dp[1][0]:.3f} to {dp[1][1]} "
          f"(needs >= {RIGID_GAP}; left out by design: the retainer, which presses on it, and the cell, {dcell:.3f} mm below it with the insulating sheet between): {'OK' if okp else 'FAIL'}")
    if not okp:
        fail(f"15c main board to {dp[0][1]} {dp[0][0]:.3f} mm")
    tops = sorted(((v["z"][1], k) for k, v in bm["main_parts"].items()), reverse=True)[:5]
    print("15b tallest bodies (top z, case frame): " + ", ".join(f"{k} {z:.3f} ({z - prm['pcb1_z'][1]:.3f} above the board)" for z, k in tops)
          + f"; cavity ceiling z {prm['cavity']['z1']:.3f}")


def test16_leads(parts, prm):
    """16. the nine leads: no contact with anything they are not soldered or glued to (free room >= LEAD_FREE), and cut length within the parts list"""
    global pairs
    ends = {"lead_W1": ("pin_board_pcb2_wing_R", "main_board"), "lead_W2": ("pin_board_pcb2", "main_board"), "lead_W3": ("pin_board_pcb2", "main_board"),
            "lead_W4": ("pin_board_pcb2_wing_L", "main_board"), "lead_W7": ("pin_board_pcb2", "main_board"),
            "lead_TH1_1": ("TH1_bead", "main_board"), "lead_TH1_2": ("TH1_bead", "main_board"),
            "lead_W5": ("cell_dnk852338", "main_board"), "lead_W6": ("cell_dnk852338", "main_board")}
    for ln in sorted(prm["leads"]):
        L = parts[ln]
        m = prm["leads"][ln]
        res = []
        for k in parts:
            if k == ln:
                continue
            pairs += 1
            if k == "main_board":
                d = min(near_distance(L, c, far=2.0) for c in parts[k].children if c.label != "PCB1")    # the bodies; the board itself is the solder end
                res.append((d, "main_board bodies"))
                continue
            d = near_distance(L, parts[k], far=2.0)
            res.append((d, k))
        res.sort()
        free = [r for r in res if r[1] not in ends[ln]]
        att = [r for r in res if r[1] in ends[ln]]
        ok = free[0][0] >= LEAD_FREE
        cut = m["length"] + STRIP_ALLOW
        bom = BOM_CUT.get(ln)
        okl = bom is None or cut <= bom
        print(f"16 {ln}: diameter {m['d']:.2f} mm, path {m['length']:.1f} mm, cut {cut:.1f} mm (parts list {bom if bom else 'none'}): {'OK' if okl else 'FAIL'}; "
              f"smallest free room {free[0][0]:.3f} mm to {free[0][1]}, then {free[1][0]:.3f} to {free[1][1]} (needs >= {LEAD_FREE}); ends at "
              + ", ".join(f"{k} {d:.3f}" for d, k in att) + f": {'OK' if ok else 'FAIL'}")
        if not ok:
            fail(f"16 {ln} free room {free[0][0]:.3f} to {free[0][1]}")
        if not okl:
            fail(f"16 {ln} cut {cut:.1f} longer than the parts list {bom}")


def sample_points(shape, step=0.1, tol=0.03, box=None):
    """points on the surface of `shape`: its triangles (tessellated at tol): vertices, points every `step` along each edge, and area / step^2 points inside each triangle; with box (x0, x1, y0, y1)
    only the faces whose bounding box meets that plan box"""
    import numpy as np
    from build123d import Compound as Cp
    if box is not None:
        fs = [f for f in shape.faces() if (lambda b: b.max.X >= box[0] and b.min.X <= box[1] and b.max.Y >= box[2] and b.min.Y <= box[3])(f.bounding_box())]
        if not fs:
            return np.zeros((0, 3))
        shape = Cp(children=fs)
    v, t = shape.tessellate(tol, 0.2)
    V = np.array([[p.X, p.Y, p.Z] for p in v])
    T = np.array(t)
    if len(T) == 0:
        return V
    A, B_, C_ = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    out = [np.unique(np.round(V, 4), axis=0)]
    # edges: points every `step` along each triangle edge longer than `step` (thin triangles are covered by their edges)
    for P0, P1 in ((A, B_), (B_, C_), (C_, A)):
        Ln = np.linalg.norm(P1 - P0, axis=1)
        k = np.ceil(Ln / step).astype(int)
        for kk in np.unique(k[k >= 2]):
            sel = k == kk
            f = (np.arange(1, kk) / kk)[None, :, None]
            out.append((P0[sel][:, None, :] + f * (P1[sel] - P0[sel])[:, None, :]).reshape(-1, 3))
    # inside: area / step^2 points per triangle, on a fixed pseudo-random barycentric pattern (seed 1)
    area = 0.5 * np.linalg.norm(np.cross(B_ - A, C_ - A), axis=1)
    n = np.floor(area / (step * step)).astype(int)
    rng = np.random.default_rng(1)
    idx = np.repeat(np.arange(len(T)), n)
    if len(idx):
        u, v = rng.random(len(idx)), rng.random(len(idx))
        flip = u + v > 1
        u[flip], v[flip] = 1 - u[flip], 1 - v[flip]
        out.append(A[idx] + u[:, None] * (B_ - A)[idx] + v[:, None] * (C_ - A)[idx])
    return np.vstack(out)


def test17_lift(parts, prm, rings):
    """17. lid open, every size: the ring is lifted straight up (+Z) out of its seat in LIFT_STEP steps until its lowest point is above the highest point of
    the case. Screen: surface points of the ring (0.2 mm spacing) against surface points (0.1 mm) of every case part near the path, every step; exact: the
    smallest step of each part again with OCC (face by face distance and common volume), and the common volume at every step where the screen is below 0.3.
    Seat contacts (the ring rests on them, so they are measured but not counted as free space): the four spring pins at their working compression for the
    size, and the two flank faces of the V wall (part of the liner, |y| in the flank strip)."""
    global pairs
    import numpy as np
    from scipy.spatial import cKDTree
    from build123d import Compound as Cp
    print(f"17 pass line (fixed before the first run): no common volume above {LIMIT} mm3 with any case part at any step, and free space >= {LIFT_FREE} mm to every "
          f"case part except the seat contacts (4 pins, 2 flank faces). Reason for {LIFT_FREE}: the smallest designed gap on the way out other than the seat is the "
          f"block's guide in its pocket, {C.POCKET_G} mm per side (case.py POCKET_G); a feature that closes the path below {LIFT_FREE} mm fails. Free space is "
          f"taken from the first step ({LIFT_STEP} mm) on; the common volume from the seated pose (0 mm) on.")
    px, py = prm["pivot"]
    ang = prm["lid_open_deg"]
    swing = ("lid", "lid_seam_trim", "magnet_lid", "hinge_pivot") + tuple(k for k in parts if k.startswith("glide"))
    case = {}
    for k, s in parts.items():
        case[k] = Pos(px, py, 0) * (Rot(0, 0, ang) * (Pos(-px, -py, 0) * s)) if k in swing else s
    zf, zb = prm["zf"], prm["zb"]
    fy0, fy1 = prm["rests"]["strip"]
    flank_box = C.box(-30, prm["x_a"] + fy1 * C.TANPHI + 0.6, fy0 - 0.05, fy1 + 0.05, zf - 1.5, prm["rests"]["top"] + 1.0)
    flank_box = flank_box + C.box(-30, prm["x_a"] + fy1 * C.TANPHI + 0.6, -fy1 - 0.05, -fy0 + 0.05, zf - 1.5, prm["rests"]["top"] + 1.0)
    case["liner (flank faces)"] = case["liner"] & flank_box
    case["liner"] = case["liner"] - flank_box
    top_case = max(s.bounding_box().max.Z for s in case.values())
    pin_names = sorted(prm["pin_nets"])
    pl = C.PL
    k_of_net = {p_["net"]: k for k, p_ in enumerate(pl["pads"])}
    results = {}
    for n in prm["sizes"]:
        rc = rings[n].parts_in_case(zb)
        ring = {k: rc[k] for k in ("body", "glass", "joystick")}
        rb = Cp(children=list(ring.values())).bounding_box()
        lift_max = top_case - rb.min.Z + LIFT_STEP
        steps = [i * LIFT_STEP for i in range(int(math.ceil(lift_max / LIFT_STEP)) + 1)]
        sc = dict(case)
        for pn in pin_names:                                        # pins at the working compression of this size (as test 2a)
            fx, fy, fz = C.pad_face_xyz(n, k_of_net[prm["pin_nets"][pn]], zb, pl)
            pb = parts[pn].bounding_box()
            sc[pn] = C.make_pin(pb.max.X, (pb.min.Y + pb.max.Y) / 2, (pb.min.Z + pb.max.Z) / 2, pb.max.X - fx - C.TIP_GAP)
        seat = set(pin_names) | {"liner (flank faces)"}
        # parts near the lift corridor (plan box of the ring + 2 mm, above the floor - 1)
        cand = {k: s for k, s in sc.items() if (lambda b: b.max.X > rb.min.X - 2 and b.min.X < rb.max.X + 2 and b.max.Y > rb.min.Y - 2 and b.min.Y < rb.max.Y + 2
                                                 and b.max.Z > rb.min.Z - 1)(s.bounding_box())}
        RP = np.vstack([sample_points(s, step=0.2) for s in ring.values()])     # ring at 0.2 mm, case parts at 0.1 mm
        trees, sel_xy, zr = {}, {}, {}
        for k, s in cand.items():
            P = sample_points(s, box=(rb.min.X - 1.5, rb.max.X + 1.5, rb.min.Y - 1.5, rb.max.Y + 1.5))
            P = P[(P[:, 0] > rb.min.X - 1.5) & (P[:, 0] < rb.max.X + 1.5) & (P[:, 1] > rb.min.Y - 1.5) & (P[:, 1] < rb.max.Y + 1.5)]
            if len(P):
                trees[k] = cKDTree(P)
                lo_, hi_ = P.min(axis=0) - 1.0, P.max(axis=0) + 1.0              # only ring points that can come within 1 mm of this part
                sel_xy[k] = np.where((RP[:, 0] > lo_[0]) & (RP[:, 0] < hi_[0]) & (RP[:, 1] > lo_[1]) & (RP[:, 1] < hi_[1]))[0]
                zr[k] = (lo_[2], hi_[2])
        print(f"17 US {n}: sampled {len(RP)} ring points and {sum(t_.n for t_ in trees.values())} case points in {len(trees)} parts", flush=True)
        screen = {k: [] for k in trees}
        for dz in steps:
            for k, tr in trees.items():
                Q = RP[sel_xy[k]]
                zq = Q[:, 2] + dz
                Q = Q[(zq > zr[k][0]) & (zq < zr[k][1])] + np.array([0.0, 0.0, dz])
                if len(Q) == 0:
                    screen[k].append(1.0)
                    continue
                d, _ = tr.query(Q, distance_upper_bound=1.0)
                screen[k].append(float(d.min()) if np.isfinite(d.min()) else 1.0)
        print(f"17 US {n}: screened {len(steps)} steps", flush=True)
        # exact: at every step where the screen is below LIFT_EXACT mm (and at each part's smallest screen step), OCC face-to-face distances between the
        # ring faces and the part's faces near the closest screened points; boundaries that touch or cross give 0 (contact: fail)
        ring_faces = [(f, f.bounding_box()) for s in ring.values() for f in s.faces()]
        rf_lo = np.array([[b.min.X, b.min.Y, b.min.Z] for f, b in ring_faces])
        rf_hi = np.array([[b.max.X, b.max.Y, b.max.Z] for f, b in ring_faces])
        n_exact, worst_common, touches = 0, 0.0, []
        best = {}
        for k, vals in screen.items():
            cfs = [(f, f.bounding_box()) for f in cand[k].faces()]
            cf_lo = np.array([[b.min.X, b.min.Y, b.min.Z] for f, b in cfs])
            cf_hi = np.array([[b.max.X, b.max.Y, b.max.Z] for f, b in cfs])
            CPk = trees[k].data
            i_min = int(np.argmin(vals[1:])) + 1
            todo = sorted(set([j for j, v in enumerate(vals) if v < LIFT_EXACT] + [i_min]))
            exact = {}
            for j in todo:
                dz = steps[j]
                Q = RP[sel_xy[k]] + np.array([0.0, 0.0, dz])
                d, jj = trees[k].query(Q, distance_upper_bound=vals[j] + 0.25)
                m = d <= vals[j] + 0.2
                rp, cp = Q[m], CPk[jj[m]]
                if len(rp) == 0:
                    continue
                sh = np.array([0.0, 0.0, dz])
                near_r = [i_ for i_ in range(len(ring_faces)) if np.any(np.all((rp >= rf_lo[i_] + sh - 0.3) & (rp <= rf_hi[i_] + sh + 0.3), axis=1))]
                near_c = [i_ for i_ in range(len(cfs)) if np.any(np.all((cp >= cf_lo[i_] - 0.3) & (cp <= cf_hi[i_] + 0.3), axis=1))]
                if not near_r or not near_c:
                    continue
                dex = min((Pos(0, 0, dz) * ring_faces[a][0]).distance_to(cfs[b][0]) for a in near_r for b in near_c)
                exact[j] = dex
                n_exact += 1
                pairs += 1
                if dex <= 1e-6:                                         # boundaries meet: the pass line counts the common volume (as tests 1 and 2)
                    cv = max(C.common(Pos(0, 0, dz) * s_, cand[k]) for s_ in ring.values())
                    worst_common = max(worst_common, cv if cv == cv else 0.0)
                    touches.append((k, dz, cv))
                    if not (cv <= LIMIT):
                        fail(f"17 US {n}: ring lifted {dz:.2f} mm meets {k}: common volume {cv:.4f} mm3 (exact distance {dex:.4f})")
            later = {j: v for j, v in exact.items() if j >= 1}
            if later:
                jb = min(later, key=later.get)
                best[k] = (later[jb], steps[jb], vals[jb])
        free = sorted((v[0], k, v[1]) for k, v in best.items() if k not in seat)
        seat_l = sorted((v[0], k, v[1]) for k, v in best.items() if k in seat)
        ok = free[0][0] >= LIFT_FREE and worst_common <= LIMIT
        results[n] = (free[0], seat_l[0] if seat_l else None)
        print(f"17 US {n}: lifted 0 to {steps[-1]:.2f} mm in {len(steps)} steps of {LIFT_STEP} mm (clear when the ring's lowest point passes z {top_case:.2f}); "
              f"{len(trees)} case parts near the path, {len(RP)} ring surface points; smallest free space {free[0][0]:.3f} mm to {free[0][1]} at lift {free[0][2]:.2f} mm, "
              f"next {free[1][0]:.3f} to {free[1][1]} at {free[1][2]:.2f}; seat contacts smallest {seat_l[0][0]:.3f} mm ({seat_l[0][1]} at {seat_l[0][2]:.2f}); "
              f"{n_exact} exact measurements (every step with a screen value below {LIFT_EXACT} mm); steps where boundaries meet: {len(touches)} "
              f"({', '.join(sorted({t[0] for t in touches})) or 'none'}), largest common volume {worst_common:.6f} mm3 (limit {LIMIT}): {'OK' if ok else 'FAIL'}")
        if free[0][0] < LIFT_FREE:
            fail(f"17 US {n}: free space {free[0][0]:.3f} mm to {free[0][1]} at lift {free[0][2]:.2f} mm (needs >= {LIFT_FREE})")
    return results


RING_NET = {"VBUS": "VBUS", "D-": "USB_DN", "D+": "USB_DP", "GND": "GND"}     # band circuit names (design/ecad/band/band-interface.md lines 37, 38, 80, 81)
NET_PAIR = {"VBUS": "VRING", "USB_DN": "USB_D-", "USB_DP": "USB_D+", "GND": "GND"}  # supply, data minus, data plus, ground (design/ecad/case/pcb/board-notes.md part g)
CONTACT_CSV = os.environ.get("CASE_CONTACT_CSV", os.path.normpath(os.path.join(HERE, "..", "wiring", "ring-case-contact.csv")))


def test18_contacts(parts, prm, rings=None):
    """18. per size: which pin stands over which ring pad, found from COORDINATES (pad face centres of the seated ring from placement.csv, pin axes
    from out/parts); nets paired supply/supply, D-/D-, D+/D+, ground/ground (ring names: band circuit; case names: the pin board file); every pin's
    working height (base plane to pad face) inside the maker's 1.90 to 2.20 mm. Writes CONTACT_CSV (28 lines)."""
    global pairs
    import csv as _csv
    sys.path.insert(0, os.path.join(HERE, "r4"))
    import case_boards as CB
    pj = json.load(open(os.path.join(OUT, "boards", "pins.json")))
    case_net = {f["ref"]: f["pads"][0]["net"] for f in pj["footprints"] if f["ref"] in ("P1", "P2", "P3", "P4")}
    pins = {}
    for pn in prm["pin_nets"]:
        b = parts[pn].bounding_box()
        pins["P" + pn.split("_")[1][1:]] = (b.max.X, (b.min.Y + b.max.Y) / 2, (b.min.Z + b.max.Z) / 2)
    lo, hi = C.PIN_H_MIN, C.PIN_H_MAX
    rows = []
    for n in prm["sizes"]:
        bad = []
        for k, pad in enumerate(C.PL["pads"]):
            fx, fy, fz = C.pad_face_xyz(n, k, prm["zb"], C.PL)
            ref = min(pins, key=lambda r: math.hypot(pins[r][1] - fy, pins[r][2] - fz))
            bx, py, pz = pins[ref]
            off = math.hypot(py - fy, pz - fz)
            h = bx - fx
            rn, cn = RING_NET[pad["net"]], case_net[ref]
            ok_pair = NET_PAIR[rn] == cn and ref == "P%d" % (k + 1) and off <= 0.1
            ok_h = lo <= h <= hi
            pairs += 1
            rows.append(dict(ring_pad=pad["ref"], ring_net=rn, case_pin=ref, case_net=cn, ring_size=f"US {n}", working_height_mm=f"{h:.3f}",
                             in_range="yes" if ok_h else "no", tip_to_pad_mm=f"{off:.3f}"))
            print(f"18 US {n} {pad['ref']} ({rn}) under {ref} ({cn}): tip to pad {off:.3f} mm; pin working height {h:.3f} mm inside {lo:.2f} to {hi:.2f}: "
                  f"{'OK' if ok_h else 'FAIL'}; each pin over its pad, nets paired: {'OK' if ok_pair else 'FAIL'}")
            if not ok_h:
                bad.append(f"{ref} height {h:.3f}")
            if not ok_pair:
                bad.append(f"{pad['ref']} {rn} under {ref} {cn} offset {off:.3f}")
        for b_ in bad:
            fail(f"18 US {n}: {b_}")
    with open(CONTACT_CSV, "w", newline="") as fh:
        w = _csv.DictWriter(fh, fieldnames=["ring_pad", "ring_net", "case_pin", "case_net", "ring_size", "working_height_mm", "in_range", "tip_to_pad_mm"])
        w.writeheader()
        w.writerows(rows)
    print(f"18 wrote {CONTACT_CSV}: {len(rows)} lines")


def prm_hull(prm):
    return prm["hull_w"]


if __name__ == "__main__":
    sys.exit(main())
