#!/usr/bin/env python3
"""Fit check for the thin ring model v7 (architecture 17.29, 17.30). v7 adds: 11. the recording light is gone: no part named or
referenced as LED1, LG1, LP1, R41 or Q2 (or recording_led, light_guide, light_pipe), the main board is solid at the old guide hole
(X -12.425, Y -2.95), the foam has no notch there, the cover glass has no opening there, and the clear adhesive covers the whole
panel; 12. the round joystick: frame FRM1 outer diameter 5.40 and bore 4.80, its top 0.50 above the body surface; cap CAP1 diameter
4.40, its top measured along its axis at radii 0.0, 0.7, 1.3, 1.6 and 1.9 against the heights the design gives (rim plane 1.400
above the frame top, dish 0.25, ridges 0.08); the expected values are written here, not read from thin.P.
(Docstring of v5 follows.)  Fit check for the thin ring model v5 (thin.py: turned joystick in the exterior's opening, top-port microphones over floor holes,
light guide, U11, glass seal, joystick dam). Exit 1 on any finding, 0 when everything fits.
v5 adds: 6. microphone holes and seats of the exterior coaxial with the model's ports, gaskets and membranes (0.05);
7. light column (riser, LP1) inside the clear ledge and clear of the cable bond; 8. frame inside the exterior's opening;
9. metal >= 0.40 round the opening, the joystick pocket, the motor pocket and the microphone seats (real figures printed);
the 0.20 ring under each membrane seat is reported as a KNOWN EXCEPTION (mic-path.md line 79, open item O3 line 200);
10. the two ribbon fold volumes beside the floor slots (assembly.md K-A6) are free of parts.

1. no two parts intersect (> LIMIT mm3, sub-solid against sub-solid); outer_body and band_liner touch by design
2. every part lies inside the exterior body's envelope (the imported body before the cavities); the cover glass is the
   exterior's own and is skipped; the two caps stand proud by design (to the exterior's own nub and pill top) and are checked against a proud allowance
3. motor: out of the block interior, and at least WALL_MIN of metal at every rim point (ray method)
4. block stack: layer thicknesses add up to the glass top height and the floor is at least 0.30
5. the GLB: top-level nodes = placement.csv rows, every child named <part>__<class> with a known class; triangles under 600000
Last line: RESULT PASS pairs=<n> parts=<n>   (or RESULT FAIL ...)
"""
import csv
import math
import json
import struct
import sys
import itertools
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import thin  # noqa: E402
from build123d import Box, Cylinder, Pos, Vector  # noqa: E402

LIMIT = 0.001
WALL_MIN = 0.40
TRI_MAX = 600000


def vol(s):
    try:
        return s.volume
    except Exception:
        return 0.0


def common(a, b):
    ba, bb = a.bounding_box(), b.bounding_box()
    if (ba.max.X < bb.min.X or bb.max.X < ba.min.X or ba.max.Y < bb.min.Y or bb.max.Y < ba.min.Y
            or ba.max.Z < bb.min.Z or bb.max.Z < ba.min.Z):
        return 0.0
    return vol(a & b)


def main():
    m = thin.build()
    P, ctx = m["parts"], m["ctx"]
    by = {p.name: p for p in P}
    solids = {p.name: p.solids() for p in P}
    findings, errors = [], []
    pairs = 0
    import os
    skip = bool(os.environ.get("THIN_CHECK_SKIP_PAIRS"))     # debug only: the result line then says DEBUG, never PASS
    for a, b in itertools.combinations(P, 2):
        if skip:
            break
        if {a.name, b.name} == {"outer_body", "band_liner"}:
            continue
        pairs += 1
        for ca, sa in solids[a.name].items():
            for cb, sb in solids[b.name].items():
                try:
                    v = common(sa, sb)
                except Exception as e:
                    errors.append(f"ERROR boolean {a.name}__{ca} x {b.name}__{cb}: {e}")
                    continue
                if v > LIMIT:
                    findings.append(f"COLLISION {a.name}__{ca} x {b.name}__{cb}: {v:.4f} mm3")
    print(f"pairs checked: {pairs}", flush=True)
    env = m["envelope"]
    # inside-the-body test on the vertices of every sub-solid (boolean common with the full exterior body is too slow for 70 sub-solids)
    proud = {"joystick_cap": ctx["rtop_joy_exterior"], "joystick_frame": ctx["rtop_joy_exterior"]}   # v7: the frame stands 0.50 proud too
    n_pts = 0
    for p in P:
        if p.name in ("outer_body", "cover_glass"):
            continue
        for c, s in solids[p.name].items():
            vs = s.vertices()
            step = max(1, len(vs) // 300)
            bad = []
            for v in vs[::step]:
                n_pts += 1
                if not env.is_inside(Vector(v.X, v.Y, v.Z)):
                    bad.append(v)
            if p.name in proud:
                rmax = max(math.hypot(v.Y, v.Z - thin.ZC) for v in bad) if bad else 0
                if bad:
                    print(f"proud by design: {p.name}__{c} {len(bad)} vertices outside the body surface, top r {rmax:.3f} (exterior top {proud[p.name]:.3f})")
                if rmax > proud[p.name] + 0.01:
                    findings.append(f"OUTSIDE body envelope {p.name}__{c}: top r {rmax:.3f} above the exterior's {proud[p.name]:.3f}")
            elif bad:
                v = bad[0]
                findings.append(f"OUTSIDE body envelope {p.name}__{c}: {len(bad)} of {len(vs[::step])} sampled vertices, e.g. ({v.X:.2f}, {v.Y:.2f}, {v.Z:.2f})")
    print(f"inside-body test: {n_pts} vertices sampled")
    # motor
    box_ = Pos(0, 0, (ctx["Z_FLOOR"] + ctx["Z_GB"]) / 2) * Box(27.45, 12.9, ctx["Z_GB"] - ctx["Z_FLOOR"])
    blk = sum(vol(s & box_) for s in solids["vibration_motor"].values())
    print(f"motor x block interior: {blk:.4f} mm3 (limit {LIMIT})")
    if blk > LIMIT:
        findings.append(f"MOTOR enters the block interior: {blk:.4f} mm3")
    body = solids["outer_body"]["metal"]
    w, where = thin.motor_rim_min_wall(body)
    print(f"motor rim: least metal along the outward ray {w:.3f} mm at {where} (limit {WALL_MIN})")
    if w < WALL_MIN - 1e-9:
        findings.append(f"WALL under {WALL_MIN} mm at the motor rim: {w:.3f} mm at {where}")
    # v4: pads on the inside face of the band, flush with the liner's inner face, 4 of them at the pitch of P["pad_pitch"] along the arc
    pads = [n for n in by if n.startswith("pad_")]
    if len(pads) != 4:
        findings.append(f"PADS: {len(pads)} pad parts, expected 4")
    rmin = []
    for n in pads:
        g = solids[n]["gold"]
        rr = [math.hypot(v.Y, v.Z - thin.ZC) for v in g.vertices()]
        rmin.append(min(rr))
        if abs(min(rr) - thin.R_IN) > 0.002:
            findings.append(f"PADS {n}: inner face at r {min(rr):.4f}, not flush with the liner inner face r {thin.R_IN:.4f}")
        if max(rr) > thin.R_LINER:
            findings.append(f"PADS {n}: reaches r {max(rr):.3f}, beyond the liner (r {thin.R_LINER:.3f})")
    cen = [math.degrees(math.atan2(solids[n]["gold"].center().Y, solids[n]["gold"].center().Z - thin.ZC)) % 360 for n in pads]
    pitch = [math.radians(cen[i + 1] - cen[i]) * thin.R_IN for i in range(len(cen) - 1)]
    print(f"pads: inner face r {min(rmin):.4f} to {max(rmin):.4f} (liner inner face {thin.R_IN:.4f}); centres at {[round(c, 2) for c in cen]} deg; pitch along the arc {[round(x, 3) for x in pitch]} mm")
    for x in pitch:
        if abs(x - thin.P["pad_pitch"]) > 0.02:
            findings.append(f"PADS pitch {x:.3f} mm differs from {thin.P['pad_pitch']}")
    # v6.3 (architecture 17.28, G01): the pad row stands at X -1.0 (the case pins' X, case.py PAD_X_OFF = -1.0). The expected value is written here,
    # not read from thin.P, so a model with another pad_x fails.
    PAD_X_EXPECTED, PAD_X_TOL, PAD_CABLE_MARGIN = -1.0, 0.01, 0.30
    px_found = {}
    for n in pads:
        cx = solids[n]["gold"].center().X
        px_found[n] = cx
        if abs(cx - PAD_X_EXPECTED) > PAD_X_TOL:
            findings.append(f"PADS X {n}: pad X {cx:.3f}, expected {PAD_X_EXPECTED} within {PAD_X_TOL}")
    print(f"pads X (test a): {', '.join(f'{n} {x:.4f}' for n, x in px_found.items())} (expected {PAD_X_EXPECTED} +-{PAD_X_TOL})")
    # (b) each pad lies fully on the cable that carries it (band_flex_away): the pad's disc grown by g, cut to the cable's layer (R_F0 to R_F1),
    # leaves no volume outside the cable. The margin is the largest g (bisection, 9 steps from 1.2 mm) with 0 outside; at least 0.30. (A point
    # classifier is not used: is_inside gave a false "outside" at a seam inside the cable on US 8, out/v63/probe_cable_us8.log.) No other part touches the pad.
    flex_all = solids["band_flex_away"]["flex"]
    cable_layer = thin.cyl_x(thin.R_F1, -5, 5) - thin.cyl_x(thin.R_F0, -5, 5)
    margins = {}
    for n in pads:
        g = solids[n]["gold"]
        a_n = math.degrees(math.atan2(g.center().Y, g.center().Z - thin.ZC))
        def outside(gr, a_n=a_n, g=g):
            disc = thin.lplace(a_n, Cylinder(thin.P["pad_d"] / 2 + gr, 1.0), x=g.center().X, r=(thin.R_F0 + thin.R_F1) / 2)
            return vol((disc & cable_layer) - flex_all)
        lo, hi = 0.0, 1.2
        if outside(0.0) > 1e-6:
            margins[n] = -1.0            # the pad itself is not on the cable
            continue
        for _ in range(9):
            mid = (lo + hi) / 2
            if outside(mid) < 1e-6:
                lo = mid
            else:
                hi = mid
        margins[n] = lo
    print("pads on the cable (test b): margin pad edge to cable edge " + ", ".join(f"{n} {v:.3f}" for n, v in margins.items()) + f" mm (rule {PAD_CABLE_MARGIN})")
    for n, v in margins.items():
        if v < PAD_CABLE_MARGIN:
            findings.append(f"PADS cable {n}: margin to the cable's edge {v:.3f} under {PAD_CABLE_MARGIN}")
    for n in pads:
        for o in P:
            if o.name == n:
                continue
            for co, so in solids[o.name].items():
                v = common(solids[n]["gold"], so)
                if v > LIMIT:
                    findings.append(f"PADS collision {n} x {o.name}__{co}: {v:.4f} mm3")
    # v4: metal all round the joystick frame's opening, measured on the curved surface 0.1 mm under it
    a_j = thin.P["joy_deg"]
    env0 = m["body0"]
    rs = ctx["r_outer_joy"] - 0.1
    def run_x(x_edge, sg):
        n = 0.0
        while n < 2.0:
            if not body.is_inside(Vector(sg * (x_edge + n + 0.005), rs * math.sin(math.radians(a_j)), thin.ZC + rs * math.cos(math.radians(a_j)))):
                break
            n += 0.01
        return round(n, 2)
    def run_t(t_edge, sg):
        d0 = math.asin(sg * t_edge / rs)
        n = 0.0
        while n < 2.0:
            d = d0 + sg * (n + 0.005) / rs
            if not body.is_inside(Vector(0.0, rs * math.sin(math.radians(a_j) + d), thin.ZC + rs * math.cos(math.radians(a_j) + d))):
                break
            n += 0.01
        return round(n, 2)
    hx, ht = thin.P["opening"][0] / 2, thin.P["opening"][1] / 2      # v5: 6.6 along X, 5.6 around the band (v4 had them swapped)
    ox = (run_x(hx, 1), run_x(hx, -1))
    ot = (run_t(ht, 1), run_t(ht, -1))
    print(f"joystick opening at {a_j} deg, 0.1 mm under the surface (r {rs:.3f}): metal beside it along X {ox}, along the band {ot} mm (rule {WALL_MIN})")
    for lab, v in (("along X", ox), ("along the band", ot)):
        if min(v) < WALL_MIN:
            findings.append(f"OPENING metal {lab} {min(v):.2f} mm under {WALL_MIN} at the joystick frame")
    # ---- v5 checks
    import numpy as np  # noqa: F401
    def inside(b, x, y, z):
        return b.is_inside(Vector(x, y, z))
    def edge(b, x0, y0, z0, dx, dy, start=0.0, lim=3.0, step=0.0025, want_metal=True):
        """distance from (x0, y0) along (dx, dy) at height z0 to the first point whose metal state equals want_metal
        (coarse steps of 8 x step, then the last coarse interval again at step)"""
        d = start
        while d < lim:
            if inside(b, x0 + dx * d, y0 + dy * d, z0) == want_metal:
                e = max(start, d - 8 * step)
                while e < d:
                    if inside(b, x0 + dx * e, y0 + dy * e, z0) == want_metal:
                        return e
                    e += step
                return d
            d += 8 * step
        return None
    # 6. microphone holes and seats of the exterior, coaxial with the model's ports, gaskets and membranes
    for sg, gk, mb in ((-1, "mic_gasket_1", "mic_membrane_1"), (1, "mic_gasket_2", "mic_membrane_2")):
        nx, ny = sg * thin.P["mic_port_x"], thin.P["mic_y"]
        for lab, z in (("hole", 0.20), ("seat", 0.05)):
            e = {k: edge(env0, nx, ny, z, dx, dy) for k, (dx, dy) in {"+X": (1, 0), "-X": (-1, 0), "+Y": (0, 1), "-Y": (0, -1)}.items()}
            if None in e.values():
                findings.append(f"MIC {lab} at X {nx} Y {ny} Z {z}: no edge found {e}")
                continue
            cx, cy = nx + (e["+X"] - e["-X"]) / 2, ny + (e["+Y"] - e["-Y"]) / 2
            dia = ((e["+X"] + e["-X"]) + (e["+Y"] + e["-Y"])) / 2
            off = math.hypot(cx - nx, cy - ny)
            print(f"mic {lab} of the exterior at Z {z}: centre ({cx:.4f}, {cy:.4f}), dia {dia:.4f}; model port axis ({nx:.3f}, {ny:.3f}); offset {off:.4f} mm (limit 0.05)")
            if off > 0.05:
                findings.append(f"MIC {lab} centre ({cx:.3f}, {cy:.3f}) off the model's port axis by {off:.3f} mm")
        for n in (gk, mb):
            c = list(solids[n].values())[0].bounding_box().center()
            off = math.hypot(c.X - nx, c.Y - ny)
            print(f"mic {n}: centre ({c.X:.4f}, {c.Y:.4f}) offset from the port axis {off:.4f} mm")
            if off > 0.05:
                findings.append(f"MIC {n} off the port axis by {off:.3f} mm")
        # metal round the seat: horizontal, at Z 0.05, from the seat edge outward (16 directions), contiguous metal
        worst = (9, None)
        for k in range(16):
            ph = 2 * math.pi * k / 16
            dx, dy = math.cos(ph), math.sin(ph)
            st = edge(env0, nx, ny, 0.05, dx, dy)
            out = edge(env0, nx, ny, 0.05, dx, dy, start=st + 0.0025, lim=6.0, want_metal=False)
            w = (out - st) if out is not None else 6.0 - st
            if w < worst[0]:
                worst = (w, round(math.degrees(ph)))
        print(f"mic seat at X {nx}: least metal round the seat at Z 0.05 {worst[0]:.3f} mm toward {worst[1]} deg (rule {WALL_MIN})")
        if worst[0] < WALL_MIN:
            findings.append(f"MIC seat at X {nx}: metal {worst[0]:.3f} mm under {WALL_MIN}")
        # ring under the membrane seat (between the seat top Z 0.10 and the pocket bottom): KNOWN EXCEPTION
        body = solids["outer_body"]["metal"]
        zs = [z / 1000 for z in range(0, 450, 5)]
        col = [z for z in zs if inside(body, nx + 0.75, ny, z)]
        ring = (max(col) - min(col) + 0.005) if col else 0.0
        print(f"KNOWN EXCEPTION mic at X {nx}: metal ring between the seat (dia 2.0) and the hole (dia 1.0) is {ring:.3f} mm thick "
              f"(Z {min(col):.3f} to {max(col) + 0.005:.3f}); under the floor rule 0.30 and the wall rule {WALL_MIN}; source mic-path.md line 79 (check.log C26w), open item O3 (mic-path.md line 200)")
        col2 = [z for z in zs if inside(body, nx - sg * 1.5, ny, z)]
        print(f"mic at X {nx}: floor under the 0.10 pocket beside the seat {max(col2) - min(col2) + 0.005:.3f} mm (floor rule 0.30)")
        if max(col2) - min(col2) + 0.005 < 0.30 - 1e-6:
            findings.append(f"MIC floor under the pocket at X {nx} under 0.30")
    # 11. (v7, architecture 17.30) the recording light is removed
    GONE_NAMES = {"recording_led", "light_guide", "light_pipe"}
    GONE_REFS = {"LED1", "LG1", "LP1", "R41", "Q2"}
    for p in P:
        if p.name in GONE_NAMES or p.ref in GONE_REFS:
            findings.append(f"LIGHT part still in the model: {p.name} ({p.ref})")
    OLD_HOLE = (-12.425, -2.95)                       # the v5 to v6.3 guide hole, riser and print window
    zb = (ctx["Z_BD0"] + ctx["Z_BD1"]) / 2
    pcb_ok = solids["main_board"]["pcb"].is_inside(Vector(OLD_HOLE[0], OLD_HOLE[1], zb))
    foam_ok = solids["foam"]["foam"].is_inside(Vector(OLD_HOLE[0], OLD_HOLE[1], ctx["Z_BD1"] + 0.05))
    gl = solids["cover_glass"]["glass"]
    zg = [ctx["Z_GB"] + k * (ctx["Z_GT"] - ctx["Z_GB"]) / 12 for k in range(1, 12)]
    gl_in = [z for z in zg if gl.is_inside(Vector(OLD_HOLE[0], OLD_HOLE[1], z))]
    glass_t = gl.bounding_box()
    print(f"light removed (v7): parts named or referenced as a light part: {[p.name for p in P if p.name in GONE_NAMES or p.ref in GONE_REFS]}; "
          f"board solid at the old hole {pcb_ok}; foam solid there {foam_ok}; glass column there {len(gl_in)} of {len(zg)} points in glass")
    if not pcb_ok:
        findings.append(f"LIGHT hole: the main board is not solid at X {OLD_HOLE[0]} Y {OLD_HOLE[1]}")
    if not foam_ok:
        findings.append(f"LIGHT notch: the foam is not solid at X {OLD_HOLE[0]} Y {OLD_HOLE[1]}")
    if len(gl_in) < len(zg) - 1:     # the top point may meet the curved face
        findings.append(f"LIGHT window: the cover glass has an opening at X {OLD_HOLE[0]} Y {OLD_HOLE[1]} ({len(gl_in)} of {len(zg)} points in glass)")
    ab = solids["clear_adhesive"]["polymer"].bounding_box()
    sb = solids["screen"]["screen"].bounding_box()
    dfa = max(abs(ab.min.X - sb.min.X), abs(ab.max.X - sb.max.X), abs(ab.min.Y - sb.min.Y), abs(ab.max.Y - sb.max.Y))
    print(f"clear adhesive over the whole panel: outline X {ab.min.X:.3f} to {ab.max.X:.3f}, Y {ab.min.Y:.3f} to {ab.max.Y:.3f}; panel X {sb.min.X:.3f} to {sb.max.X:.3f}; largest difference {dfa:.4f}")
    if dfa > 0.001:
        findings.append(f"ADHESIVE does not cover the whole panel: {dfa:.4f} mm")
    # 12. (v7, architecture 17.29) the round joystick, measured on the solids along the joystick's own axis
    FRAME_OD, FRAME_ID, FRAME_PROUD, CAP_D, CAP_RIM, CAP_EDGE, DISH, RIDGES, RIDGE_W, RIDGE_H, TOL = 5.40, 4.80, 0.50, 4.40, 1.400, 0.30, 0.25, (0.70, 1.30, 1.90), 0.25, 0.08, 0.01
    a_j0 = math.radians(thin.P["joy_deg"])
    def lpt(x, t, r):
        return Vector(x, r * math.sin(a_j0) + t * math.cos(a_j0), thin.ZC + r * math.cos(a_j0) - t * math.sin(a_j0))
    fr = solids["joystick_frame"]["metal"] if "joystick_frame" in solids else None
    capp = solids["joystick_cap"]["polymer"]
    r_surf = ctx["r_outer_joy"]
    if fr is None:
        findings.append("JOYSTICK frame FRM1 missing")
    else:
        zmid = r_surf - 0.1
        def radial_edge(sol, z, start, outward, lim=4.0, step=0.0025):
            d = start
            while d < lim:
                ins = sol.is_inside(lpt(d, 0.0, z))
                if ins != outward:
                    return d
                d += step
            return None
        # frame: from the axis outward, the first metal point is the bore, the next air point the outside
        b_in = radial_edge(fr, zmid, 0.0, False)
        b_out = radial_edge(fr, zmid, (b_in or 0) + 0.005, True)
        b_in_t = None
        d = 0.0
        while d < 4.0:
            if fr.is_inside(lpt(0.0, d, zmid)):
                b_in_t = d
                break
            d += 0.0025
        # frame top: along the axis direction at radius 2.55 (inside the ring wall), from above down to metal
        def top_down(sol, x, t, z_from, z_to, step=0.0025):
            z = z_from
            while z > z_to:
                if sol.is_inside(lpt(x, t, z)):
                    return z
                z -= step
            return None
        f_top = top_down(fr, 2.55, 0.0, r_surf + 3.0, r_surf - 2.0)
        print(f"joystick frame FRM1: bore dia {2 * b_in:.4f} (along X) / {2 * b_in_t:.4f} (around the band), outer dia {2 * b_out:.4f}, top {f_top - r_surf:.4f} above the body surface r {r_surf} "
              f"(expected {FRAME_ID}, {FRAME_OD}, {FRAME_PROUD} within {TOL})")
        for lab, got, exp in (("bore", 2 * b_in, FRAME_ID), ("bore around the band", 2 * b_in_t, FRAME_ID), ("outer diameter", 2 * b_out, FRAME_OD), ("top above the surface", f_top - r_surf, FRAME_PROUD)):
            if abs(got - exp) > TOL:
                findings.append(f"JOYSTICK frame {lab} {got:.4f}, expected {exp} within {TOL}")
        # cap: diameter at the frame top's level, and its top along the axis at 5 radii against the design's heights
        c_out = radial_edge(capp, f_top, 0.0, True)
        print(f"joystick cap CAP1: diameter {2 * c_out:.4f} at the frame top's level (expected {CAP_D}); radial clearance to the bore {b_in - c_out:.4f}")
        if abs(2 * c_out - CAP_D) > TOL:
            findings.append(f"JOYSTICK cap diameter {2 * c_out:.4f}, expected {CAP_D} within {TOL}")
        if b_in - c_out < 0.15:
            findings.append(f"JOYSTICK cap to frame bore {b_in - c_out:.4f} under 0.15")
        a_d = CAP_D / 2 - CAP_EDGE
        R_d = (a_d ** 2 + DISH ** 2) / (2 * DISH)
        def design_h(rho):          # height of the cap's top above the frame top at radius rho (rho <= a_d), from the design values
            h = CAP_RIM - DISH + R_d - math.sqrt(R_d ** 2 - rho ** 2)
            if any(abs(rho - rr) < RIDGE_W / 2 - 1e-9 for rr in RIDGES) or rho in RIDGES:
                h += RIDGE_H
            return h
        worst_cap = 0.0
        for rho in (0.0, 0.70, 1.30, 1.60, 1.90):
            for (dx, dt) in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                z = top_down(capp, dx * rho, dt * rho, f_top + 3.0, f_top - 1.0, step=0.001)
                got = z - f_top
                exp = design_h(rho)
                worst_cap = max(worst_cap, abs(got - exp))
                if abs(got - exp) > TOL:
                    findings.append(f"JOYSTICK cap top at radius {rho} ({dx},{dt}): {got:.4f} above the frame top, expected {exp:.4f} within {TOL}")
            print(f"joystick cap top at radius {rho:.2f} (+X): {top_down(capp, rho, 0.0, f_top + 3.0, f_top - 1.0, step=0.001) - f_top:.4f} above the frame top (design {design_h(rho):.4f})")
        print(f"joystick cap: largest difference to the design heights {worst_cap:.4f} (limit {TOL}); rim plane {CAP_RIM} above the frame top, highest point {CAP_RIM + RIDGE_H:.3f}")
    # 8. frame inside the exterior's opening
    def local(v):
        a = math.radians(a_j)
        return v.X, v.Y * math.cos(a) - (v.Z - thin.ZC) * math.sin(a)
    fxh = fth = (b_out if fr is not None else 9.9)      # v7: round frame, outer radius measured in 12.
    for depth in (0.05, 0.3, 0.6):
        rr = ctx["r_outer_joy"] - depth
        def pt(x, t):
            a = math.radians(a_j) + t / rr                # along the band on the arc of radius rr (a flat line would leave the surface)
            return (x, rr * math.sin(a), thin.ZC + rr * math.cos(a))
        def scan(dx, dt):
            d = 0.0
            while d < 5.0:
                if env0.is_inside(Vector(*pt(dx * d, dt * d))):
                    e = max(0.0, d - 0.02)
                    while e < d and not env0.is_inside(Vector(*pt(dx * e, dt * e))):
                        e += 0.0025
                    return e
                d += 0.02
            return None
        ex = (scan(1, 0), scan(-1, 0)); et = (scan(0, 1), scan(0, -1))
        if None in ex or None in et:
            findings.append(f"FRAME opening scan at depth {depth}: no edge found {ex} {et}")
            continue
        et = tuple(rr * math.sin(v / rr) for v in et)     # arc length to the flat wall's distance from the opening's axis plane
        print(f"opening at {depth} mm under the surface: X +{ex[0]:.4f} / -{ex[1]:.4f}, band +{et[0]:.4f} / -{et[1]:.4f} (size {ex[0] + ex[1]:.4f} x {et[0] + et[1]:.4f}); "
              f"frame half sizes X {fxh:.4f} band {fth:.4f}; clearance X {min(ex) - fxh:.4f} band {min(et) - fth:.4f}")
        if min(ex) - fxh < 0 or min(et) - fth < 0:
            findings.append(f"FRAME outside the opening at depth {depth}")
    # 9. metal round the joystick pocket: X walls outward along X; roof outward along the radius (outside the opening)
    pkx, pkt, pr0, pr1 = ctx["pocket_j"]
    body = solids["outer_body"]["metal"]
    def lp(x, t, r):
        a = math.radians(a_j)
        return Vector(x, r * math.sin(a) + t * math.cos(a), thin.ZC + r * math.cos(a) - t * math.sin(a))
    worst = (9, None)
    for t in (-3.3, -2.0, 0.0, 2.0, 3.3):
        for r in (thin.R_IN + 0.05, pr0 + 0.05, (pr0 + pr1) / 2, pr1 - 0.05):   # v6: the pocket reaches the bore
            for sx in (1, -1):
                d = pkx / 2 + 0.0025
                while d < 6 and not body.is_inside(lp(sx * d, t, r)):
                    d += 0.0025
                d0 = d
                while d < 6 and body.is_inside(lp(sx * d, t, r)):
                    d += 0.0025
                if d - d0 < worst[0]:
                    worst = (d - d0, ("X wall", sx, t, round(r, 3)))
    for (x, t) in ((0.0, 3.1), (0.0, -3.1), (3.4, 0.0), (-3.4, 0.0), (3.4, 3.1), (-3.4, -3.1)):
        n = 0.0
        for i in range(int(4.0 / 0.01)):
            if body.is_inside(lp(x, t, pr1 + i * 0.01)):
                n += 0.01
        if n < worst[0]:
            worst = (n, ("roof", x, t))
    print(f"joystick pocket: least metal outward {worst[0]:.3f} mm at {worst[1]} (rule {WALL_MIN})")
    if worst[0] < WALL_MIN:
        findings.append(f"POCKET metal {worst[0]:.3f} under {WALL_MIN} at {worst[1]}")
    # flange to the shell above it (radial play) and switch bases above the liner (v4 inherited; reported)
    def first_metal_up(x, t, r0):
        r = r0
        while r < r0 + 4 and not body.is_inside(lp(x, t, r)):
            r += 0.0025
        return r - r0
    print(f"joystick flange: free space from the flange top (r {thin.R_PL1:.3f}) to metal at band +3.1: {first_metal_up(0.0, 3.1, thin.R_PL1):.3f} mm, "
          f"at band -3.1: {first_metal_up(0.0, -3.1, thin.R_PL1):.3f} mm, at X 3.1: {first_metal_up(3.1, 0.0, thin.R_PL1):.3f} mm")
    # v6 (K13): each switch base on the flat ribbon head: gap from the base to the ribbon part (0 = seated)
    for n in ("joy_sw_fingertip", "joy_sw_hand", "joy_sw_up", "joy_sw_down", "joy_sw_centre"):
        g = solids[n]["polymer"].distance_to(solids["band_flex_thumb"]["flex"])
        print(f"switch {n}: base to the flat ribbon head {g:.4f} mm")
        if g > 0.005:
            findings.append(f"SWITCH {n} not seated on the head: {g:.4f} mm")
    print(f"stiffener {ctx.get('stiffener_t')} thick, head Z {ctx.get('head_z')}; size US {thin.US_SIZE}: motor {thin.P['motor_angle']} deg, "
          f"pcm_a0 {thin.P['pcm_a0']}, slot bottom Z {thin.P['slot_z0']}; joystick span of the roof +-{ctx.get('joy_span_deg')} deg")
    print(f"cell: start {ctx['cell_start_deg']} end {ctx['cell_end_deg']} sweep {ctx['cell_sweep_deg']} deg, {ctx['cell_len_mm']} mm on r {thin.R_CELL_C:.4f}, "
          f"{1.6 * 6.0 * ctx['cell_len_mm']:.1f} mm3, {ctx['cell_mah_lo_hi'][0]} to {ctx['cell_mah_lo_hi'][1]} mAh")
    # v6.1: motor glue line, wall to the block's cavity, metal under the pocket floor
    mot = solids["vibration_motor"]["metal"]
    bodym = solids["outer_body"]["metal"]
    for n_, c_ in (("outer_body", "metal"), ("joystick_dam", "polymer"), ("joy_sw_up", "polymer"), ("band_flex_thumb", "flex")):
        g = mot.distance_to(solids[n_][c_])
        print(f"motor free space to {n_}__{c_}: {g:.4f} mm (rule 0.05 to the body, the dam and SW1)")
        if n_ != "band_flex_thumb" and g < 0.05 - 1e-6:
            findings.append(f"MOTOR free space to {n_} {g:.4f} under 0.05")
    if ctx.get("window") is None:
        wall = ctx["motor_cut"].distance_to(ctx["panel_cut"])
        print(f"metal between the motor pocket and the block's cavity: {wall:.4f} mm (rule 0.30); no window on US {thin.US_SIZE}")
        if wall < 0.30 - 1e-6:
            findings.append(f"MOTOR pocket wall to the block cavity {wall:.4f} under 0.30")
        if "motor_window_seal" in by:
            findings.append("SEAL2 present on a size without a window")
        # v6.2: the motor pocket and the -Y floor slot (the slot opens into the cavity; same 0.30 rule)
        zf = ctx["Z_FLOOR"]
        slot_ = Pos(thin.P["slot_x"], -thin.P["tail_y"], (zf + 0.6 + thin.P["slot_z0"]) / 2) * Box(thin.P["slot_w"], 0.6, zf + 0.6 - thin.P["slot_z0"])
        ws = ctx["motor_cut"].distance_to(slot_)
        print(f"metal between the motor pocket and the -Y floor slot: {ws:.4f} mm (rule 0.30)")
        if ws < 0.30 - 1e-6:
            findings.append(f"MOTOR pocket to the -Y floor slot {ws:.4f} under 0.30")
    else:
        # v6.2 window rules (architecture 17.27)
        rem, gm, gp = ctx["window_removed"], ctx["grow_m"], ctx["grow_p"]
        thin_left = vol(bodym & gm & gp)
        print(f"window on US {thin.US_SIZE}: metal left within 0.30 of both the motor pocket and the cavity {thin_left:.4f} mm3 (rule 0: every edge left is at least 0.30)")
        if thin_left > LIMIT:
            findings.append(f"WINDOW leaves metal thinner than 0.30: {thin_left:.4f} mm3")
        rb = rem.bounding_box()
        area = 0.0
        for fc in rem.faces():
            if ctx["panel_cut"].distance_to(fc.center()) < 1e-4:
                area += fc.area
        print(f"window: metal removed {rem.volume:.4f} mm3, extent X {rb.min.X:.3f} to {rb.max.X:.3f} ({rb.size.X:.3f} long), Y {rb.min.Y:.3f} to {rb.max.Y:.3f}, "
              f"Z {rb.min.Z:.3f} to {rb.max.Z:.3f} ({rb.size.Z:.3f} high); opening area on the cavity side {area:.4f} mm2")
        if "motor_window_seal" not in by:
            findings.append("SEAL2 missing on a size with a window")
        else:
            seal = solids["motor_window_seal"]["polymer"]
            gap = vol(rem - seal - ctx["motor_off"])
            print(f"SEAL2: volume {seal.volume:.4f} mm3; window not filled (outside the 0.05 glue zone) {gap:.4f} mm3 (rule under 0.001); seal to the motor {seal.distance_to(mot):.4f} mm")
            if gap > LIMIT:
                findings.append(f"SEAL2 leaves {gap:.4f} mm3 of the window open")
        near = []
        for pp in P:
            if pp.name in ("outer_body", "vibration_motor", "motor_window_seal"):
                continue
            dmin = min(sv.distance_to(rem) for sv in solids[pp.name].values())
            near.append((dmin, pp.name))
        near.sort()
        print("window: nearest parts " + ", ".join(f"{n_} {d_:.4f}" for d_, n_ in near[:5]) + " mm (rule 0.30)")
        for d_, n_ in near:
            if d_ < 0.30 - 1e-6:
                findings.append(f"WINDOW within 0.30 of {n_}: {d_:.4f} mm")
        zf, zt = ctx["Z_FLOOR"], ctx["Z_BD0"] - 0.02
        fold = Pos(-2.2, -4.5, (zf + zt) / 2) * Box(2.6, 2.2, zt - zf)
        slot = Pos(thin.P["slot_x"], -thin.P["tail_y"], (zf + 0.6 + thin.P["slot_z0"]) / 2) * Box(thin.P["slot_w"], 0.6, zf + 0.6 - thin.P["slot_z0"])
        micp = [Pos(sg * thin.P["mic_pocket_cx"], thin.P["mic_pocket_cy"], zf) * Box(thin.P["mic_pocket"][0], thin.P["mic_pocket"][1], 0.2) for sg in (-1, 1)]
        for lab, sol, lim in (("the -Y ribbon fold volume", fold, 0.30), ("the -Y floor slot (metal left between them, rule 0.30 as every edge)", slot, 0.30), ("microphone pocket U5", micp[0], 1e-6), ("microphone pocket U6", micp[1], 1e-6)):
            d_ = sol.distance_to(rem)
            print(f"window to {lab}: {d_:.4f} mm")
            if d_ < lim:
                findings.append(f"WINDOW reaches {lab}: {d_:.4f} mm")
    am = math.radians(thin.P["motor_angle"])
    worstf = (9, None)
    for xx in (-2.4, -1.6, -0.8, 0.0, 0.8, 1.6, 2.4):
        for tt in (-2.4, -1.6, -0.8, 0.0, 0.8, 1.6, 2.4):
            if xx * xx + tt * tt > 2.55 ** 2:
                continue
            z0 = thin.R_LINER - thin.P["motor_glue"] - 0.0025
            n_ = 0.0
            for i in range(int(1.5 / 0.005)):
                zz = z0 - i * 0.005
                v = Vector(xx + thin.P["motor_x"], zz * math.sin(am) + tt * math.cos(am), thin.ZC + zz * math.cos(am) - tt * math.sin(am))
                if bodym.is_inside(v):
                    n_ += 0.005
                elif n_ > 0:
                    break
            if 0 < n_ < worstf[0]:
                worstf = (n_, (xx, tt))
    print(f"metal under the motor pocket floor (toward the bore, where there is any): least {worstf[0]:.3f} mm at motor frame x, t {worstf[1]} (rule 0.40)")
    if worstf[1] is not None and worstf[0] < 0.40 - 1e-6:
        findings.append(f"MOTOR pocket floor metal {worstf[0]:.3f} under 0.40")
    # least free space round the motor, the protection circuit and the ribbons (reported; under 0.10 is listed)
    for a_, b_ in (("vibration_motor", "joystick_dam"), ("vibration_motor", "joy_sw_up"), ("vibration_motor", "band_flex_thumb"),
                   ("vibration_motor", "outer_body"), ("cell_protection", "band_flex_away"), ("cell_protection", "outer_body"),
                   ("cell_protection", "cell"), ("band_flex_away", "outer_body"), ("band_flex_thumb", "outer_body"), ("cell", "joystick_dam")):
        g = min(sa.distance_to(sb) for sa in solids[a_].values() for sb in solids[b_].values())
        print(f"free space {a_} to {b_}: {g:.4f} mm{'  (UNDER 0.10)' if g < 0.10 else ''}")
    # 10. ribbon fold volumes (K-A6), free of every part
    for sg in (1, -1):
        y0, y1 = sorted((sg * 3.4, sg * 5.6))
        fb = Pos(-2.2, (y0 + y1) / 2, (ctx["Z_FLOOR"] + thin.P.get("ztop", ctx["Z_BD0"] - 0.02)) / 2) * Box(2.6, y1 - y0, (ctx["Z_BD0"] - 0.02) - ctx["Z_FLOOR"])
        tot = 0.0
        hit = []
        for p in P:
            if p.name.startswith("band_flex"):
                continue
            for c, sol in solids[p.name].items():
                v = common(sol, fb)
                if v > LIMIT:
                    hit.append(f"{p.name}__{c} {v:.4f}")
                tot += v
        print(f"ribbon fold volume {'+Y' if sg > 0 else '-Y'}: X -3.5 to -0.9, Y {y0} to {y1}, Z {ctx['Z_FLOOR']:.2f} to {ctx['Z_BD0'] - 0.02:.2f} "
              f"(2.6 x 2.2 x {ctx['Z_BD0'] - 0.02 - ctx['Z_FLOOR']:.2f}); parts in it {tot:.4f} mm3 {hit}")
        if hit:
            findings.append(f"FOLD volume {sg:+d} not free: {hit}")
    # U11, C83, C84: plan distance to the +Y floor slot; the ribbons' free space to each slot end (v6.2: slots X -3.5 to -1.3)
    sx0, sx1 = thin.P["slot_x"] - thin.P["slot_w"] / 2, thin.P["slot_x"] + thin.P["slot_w"] / 2
    sy0, sy1 = thin.P["tail_y"] - 0.3, thin.P["tail_y"] + 0.3
    for n_, c_ in (("motor_regulator", "chip"), ("motor_cap_in", "ceramic"), ("motor_cap_out", "ceramic")):
        bb_ = solids[n_][c_].bounding_box()
        dx_ = max(0.0, bb_.min.X - sx1, sx0 - bb_.max.X)
        dy_ = max(0.0, sy0 - bb_.max.Y, bb_.min.Y - sy1)
        print(f"{n_} to the +Y floor slot (X {sx0:.2f} to {sx1:.2f}, Y {sy0:.2f} to {sy1:.2f}) in plan: {math.hypot(dx_, dy_):.3f} mm")
    rx0, rx1 = thin.P["tail_x"] - thin.P["tail_w"] / 2, thin.P["tail_x"] + thin.P["tail_w"] / 2
    print(f"ribbon X {rx0:.2f} to {rx1:.2f} in the slot X {sx0:.2f} to {sx1:.2f}: free space to the -X end {rx0 - sx0:.3f}, to the +X end {sx1 - rx1:.3f} mm (rule 0.15)")
    if min(rx0 - sx0, sx1 - rx1) < 0.15 - 1e-9:
        findings.append("SLOT end clearance to the ribbon under 0.15")
    # stack
    gcen = by["cover_glass"].subs["glass"][0].bounding_box()
    t = thin.P
    stack = [("floor", ctx["Z_FLOOR"]), ("gap", t["gap"]), ("parts under the board", t["under"]), ("board", t["board_t"]),
             ("foam", t["foam_t"]), ("screen", t["scr_t"]), ("adhesive", t["adh_t"]), ("glass at the centre line", ctx["Z_GT"] - ctx["Z_GB"])]
    tot = sum(v for _, v in stack)
    print("block stack: " + " + ".join(f"{n} {v:.2f}" for n, v in stack) + f" = {tot:.3f} mm; glass top {ctx['Z_GT']:.3f}")
    if abs(tot - ctx["Z_GT"]) > 1e-6:
        findings.append(f"STACK sum {tot:.3f} differs from the glass top {ctx['Z_GT']:.3f}")
    if ctx["Z_FLOOR"] < 0.30:
        findings.append(f"STACK floor {ctx['Z_FLOOR']:.3f} under 0.30")
    lowest = min(s.bounding_box().min.Z for n in ("main_chip", "storage", "screen_supply_coil", "mic_1", "mic_2", "power_coil_1", "screen_connector",
                                                  "motor_regulator", "motor_cap_in", "motor_cap_out")
                 for s in solids[n].values())
    print(f"lowest under-board part Z {lowest:.3f}, floor top Z {ctx['Z_FLOOR']:.3f}")
    if lowest < ctx["Z_FLOOR"] - 1e-9:
        findings.append(f"STACK under-board part at Z {lowest:.3f} below the floor top {ctx['Z_FLOOR']:.3f}")
    # GLB
    g = (HERE / "out" / "thin-inside.glb").read_bytes()
    n, _ = struct.unpack("<II", g[12:20])
    j = json.loads(g[20:20 + n])
    rows = [r["part"] for r in csv.DictReader(open(HERE / "placement.csv"))]
    top = [j["nodes"][i]["name"] for i in j["scenes"][0]["nodes"]]
    if top != rows:
        findings.append(f"GLB top-level nodes differ from placement.csv: {len(top)} vs {len(rows)}")
    badc = 0
    for i in j["scenes"][0]["nodes"]:
        nd = j["nodes"][i]
        for c in nd.get("children", []):
            cn = j["nodes"][c]["name"]
            if not cn.startswith(nd["name"] + "__") or cn[len(nd["name"]) + 2:] not in thin.CLASSES:
                badc += 1
                findings.append(f"GLB child name {cn} is not <part>__<class>")
    tris = int((HERE / "out" / "triangles.txt").read_text().strip())
    print(f"GLB: {len(top)} top-level nodes, {len(j['nodes']) - len(top)} children, {badc} bad child names, {tris} triangles (limit {TRI_MAX})")
    if tris >= TRI_MAX:
        findings.append(f"GLB triangles {tris} >= {TRI_MAX}")
    for e in errors:
        print(e)
    for f in findings:
        print(f)
    bad = len(findings) + len(errors)
    print(f"check_thin: {len(findings)} findings, {len(errors)} errors")
    print(f"RESULT {'FAIL' if bad else ('DEBUG-NO-PAIRS' if skip else 'PASS')} pairs={pairs} parts={len(P)}")   # skipping the pairs can never give PASS
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
