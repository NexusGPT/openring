"""Fit check of the case C5 (tests 1 to 7 as C4; 8 to 10 are new), read from the exported STEP files in out/parts/ and the ring (file ring-merged32e, sizes computed).

Exit 1 when any of these fails, for ring sizes US 7 to 13 (the per-size rings use COMPUTED bores, see case.py):
 1. two parts of the assembly (case parts plus the US 9 ring seated) intersect by more than 0.001 mm3 (every pair);
 2. the ring does not seat flat: band bottom not on the floor (gap outside -0.001 to 0.05 mm) or not on both flanks of the V wall;
    a ring part intersects a case part (every size);
 3. a spring pin does not meet its pad: lateral offset above 0.1 mm, or pin height outside the contact window (travel);
 4. the closed lid is closer than 0.5 mm to the ring; the lid swung open (0 to the open angle) touches the ring or another part, or
    still covers the ring at the open angle;
 5. the cell, main board, USB-C socket or light is closer than 0.3 mm to a wall of the shell;
 6. a wrong placement (turned 180 degrees, across, flipped over) fits the pocket AND the pins find pads on it;
 7. (information only, open item R1) the roll play: how far the ring can turn about its own axis inside the pocket and what that does to the pad row;
 8. (new in C5) no outside face of the shell, lid or bottom plate is planar except the seam faces (a planar face counts as skin when its centre lies on the
    outside skin: within 0.012 of the skin's scale factor, about 0.5 mm, for C5b; on the bounding box faces for the C4 box); the same test run on the C4 shape (look/c4_out/parts) must find planar outside faces (self-test);
 9. (information only since C5b) plan outline smallest radius of curvature and the share of the wall within 5 degrees of vertical;
10. (new) the seam gap is 0.3 mm; the USB-C mouth sits 0.3 mm behind the skin; the charge light hole is 1.0 mm.
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
            if on_skin(c):
                bad.append(f"{name} face at ({c.X:.1f}, {c.Y:.1f}, {c.Z:.1f}) normal ({n.X:.2f}, {n.Y:.2f}, {n.Z:.2f}) area {f.area:.1f}")
    return len(bad), bad


def main():
    global pairs
    with open(os.path.join(OUT, "case_params.json")) as f:
        prm = json.load(f)
    parts = {n: import_step(os.path.join(OUT, "parts", f"{n}.step")) for n in prm["parts"]}
    base = C.load_base()
    rings = {n: C.Ring(n, base) for n in prm["sizes"]}
    zb, zf = prm["zb"], prm["zf"]
    print(f"ring sizes checked: US {prm['sizes']} (bores computed from sizes.csv; US 9 is the real file)")

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
    pin_names = [f"pin_P{i+1}_{prm['pad_nets'][i]}" for i in range(4)]
    lo, hi = prm["pin_window"]
    pin_heights_all = []
    for n in prm["sizes"]:
        rg = rings[n]
        rc = rg.parts_in_case(zb)
        pads = sorted(rc["pads"].solids(), key=lambda s: s.center().Y)
        pin_n, face_n = {}, []
        for i, ps in enumerate(pads):
            inner = min((f for f in ps.faces() if 0.85 * math.pi * (C.PAD_D / 2) ** 2 <= f.area <= 1.15 * math.pi * (C.PAD_D / 2) ** 2), key=lambda f: math.hypot(f.center().X - prm["cx"][str(n)], 0.0))
            face_n.append(inner.center())
            pb = parts[pin_names[i]].bounding_box()
            # the pin at this size: same base plane and axis, plunger pushed in until its tip is C.TIP_GAP from the pad face
            pin_n[pin_names[i]] = C.make_pin(pb.max.X, (pb.min.Y + pb.max.Y) / 2, (pb.min.Z + pb.max.Z) / 2, pb.max.X - inner.center().X - C.TIP_GAP)
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
        zs_ = [v.Z for e in (shell.intersect(line) or []) for v in e.vertices() if abs(v.Z - zf) < 0.3]
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
                xs = [v.X for e in (shell.intersect(line) or []) for v in e.vertices()]
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
        pairs += 1
        print(f"US {n}: post and pin board to the ring body {dpost:.3f} mm (needs > 0.2): {'OK' if dpost > 0.2 else 'FAIL'}")
        if dpost <= 0.2:
            fail(f"US {n} post too close {dpost}")
        # 3. pins against pads
        for i, ps in enumerate(pads):
            pn = pin_names[i]
            pb = parts[pn].bounding_box()
            base_x = pb.max.X
            py, pz = (pb.min.Y + pb.max.Y) / 2, (pb.min.Z + pb.max.Z) / 2
            fc = face_n[i]
            off = math.hypot(py - fc.Y, pz - fc.Z)
            height = base_x - fc.X
            pin_heights_all.append(height)
            ok = off <= 0.1 and lo <= height <= hi
            pairs += 1
            print(f"US {n} {pn}: pad face centre ({fc.X:.3f}, {fc.Y:.3f}, {fc.Z:.3f}); pin axis ({py:.3f}, {pz:.3f}); lateral offset {off:.3f} <= 0.1; "
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
    others = [k for k in parts if k not in ("lid", "hinge_pivot", "magnet_lid") and not k.startswith("glide")]
    minring, minother = 1e9, 1e9
    for a in steps:
        lo_ = Pos(px, py, 0) * (Rot(0, 0, a) * (Pos(-px, -py, 0) * lid))
        for n in (7, 9, 13):
            rc = rings[n].parts_in_case(zb)
            for k in ("body", "glass", "joystick"):
                pairs += 1
                minring = min(minring, lo_.distance_to(rc[k]))
        for k in others:
            pairs += 1
            minother = min(minother, lo_.distance_to(parts[k]))
    lo_end = Pos(px, py, 0) * (Rot(0, 0, ang) * (Pos(-px, -py, 0) * lid))
    cover = C.prism_xy(prm_hull(prm), 0.0, 100.0)
    pocket = C.box(prm["px0"], prm["px1"], prm["py0"], prm["py1"], 0.0, 100.0)
    ov = C.common(lo_end, cover) + C.common(lo_end, pocket)
    pairs += 2
    ok = minring >= 0.5 and minother >= 0.3 and ov <= LIMIT
    print(f"lid swung 0 to {ang:.0f} degrees in {len(steps)} steps: closest to a ring (US 7, 9, 13) {minring:.3f} mm, closest to another case part {minother:.3f} mm; "
          f"lid over the well and pocket at {ang:.0f} degrees: {ov:.4f} mm3: {'OK' if ok else 'FAIL'}")
    if not ok:
        fail(f"lid swing ring {minring:.3f} other {minother:.3f} cover {ov:.3f}")

    # 5. electronics inside the shell
    walls = [parts["shell"], parts["base_plate"]]
    for k in ("cell_dnk852338", "main_board", "J1_usb4105", "LED1"):
        d = min(parts[k].distance_to(w) for w in walls)
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
            for a in ("shell", "post", "pin_board_pcb2", "pin_board_pcb2_wing_L", "pin_board_pcb2_wing_R", "lid"):
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
    for n in (7, 9, 13):
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
        print(f"INFO US {n}: roll play +{res[0]:.2f} / -{res[1]:.2f} degrees before the ring touches the shell; pad row moves at most {shift:.3f} mm "
              f"(a 0.6 mm pin tip stays on a 1.0 mm pad up to {allow:.2f} mm): {'within' if shift <= allow else 'NOT within, open item R1'}")


    # 8. no planar outside face (new in C5)
    outer_parts = {k: parts[k] for k in ("shell", "lid", "base_plate")}
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

    print(f"pairs checked {pairs}; failures {fails}")
    print(f"case_check: {'PASS' if fails == 0 else 'FAIL'}, {pairs} pairs checked, {fails} failures, ring sizes US {prm['sizes']}")
    return 1 if fails else 0


def prm_hull(prm):
    return prm["hull_w"]


if __name__ == "__main__":
    sys.exit(main())
