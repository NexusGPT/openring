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


def _extent(sol, fixed, axis, lo, hi, step=0.05):
    """(a, b) of the first contiguous inside run of `sol` along `axis` (0 X, 1 Y, 2 Z) with the other two coordinates in `fixed`, edges by bisection (1e-4); None if empty."""
    def pt(t):
        c = list(fixed)
        c[axis] = t
        return Vector(*c)
    n = int(round((hi - lo) / step))
    ts = [lo + k * (hi - lo) / n for k in range(n + 1)]
    ins = [sol.is_inside(pt(t)) for t in ts]
    if True not in ins:
        return None
    i0 = ins.index(True)
    i1 = i0
    while i1 + 1 <= n and ins[i1 + 1]:
        i1 += 1
    def edge(out_t, in_t):
        for _ in range(16):
            mid = (out_t + in_t) / 2
            if sol.is_inside(pt(mid)):
                in_t = mid
            else:
                out_t = mid
        return (out_t + in_t) / 2
    a = ts[i0] if i0 == 0 else edge(ts[i0 - 1], ts[i0])
    b = ts[i1] if i1 == n else edge(ts[i1 + 1], ts[i1])
    return a, b


def check_band_circuits(thin, m, P, by, solids, ctx):
    """13. the band circuits as drawn. Returns the findings (a list of strings); prints one line per measurement."""
    out = []
    TOL = 0.005
    EXP = dict(neck_w=1.8, neck_x=(-3.4, -1.6), foot_x=(-3.5, -1.0), foot_top=1.40, flex_t=0.11, foot_y=(3.4, 5.145), fold_in=0.70, fold_out=0.81,
               fold_centre=(5.145, 0.59), stiff_t=0.10, stiff_x=(-3.45, -0.95), stiff_y=(3.45, 5.05), strip_x=(-3.4, 0.25), land_z_gap=0.03, land_t=0.02)
    # the circuits' own geometry file: neck width, fold radius, flat run, flex thickness, joint (read only, no bytecode written into design/ecad)
    gfile = Path((__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/ecad/band/band_geom.py"))
    G = None
    if gfile.exists():
        import importlib.util
        sys.dont_write_bytecode = True
        spec = importlib.util.spec_from_file_location("band_geom_v8", str(gfile))
        G = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(G)
        for lab, got, exp in (("TAIL_W", G.TAIL_W, EXP["neck_w"]), ("TAIL_X", G.TAIL_X, -2.5), ("R_FOLD_IN", G.R_FOLD_IN, EXP["fold_in"]), ("T_FLEX", G.T_FLEX, EXP["flex_t"]),
                              ("JOINT", G.JOINT, EXP["land_z_gap"]), ("LF", G.LF, EXP["foot_y"][1] - EXP["foot_y"][0])):
            if abs(got - exp) > 1e-3:
                out.append(f"BAND circuits: band_geom.{lab} = {got} differs from this check's expected {exp}")
        print(f"band circuits (band_geom.py): neck {G.TAIL_W} at X centre {G.TAIL_X}, fold inner radius {G.R_FOLD_IN}, flex {G.T_FLEX}, joint {G.JOINT}, flat foot {G.LF:.4f}, fold arc {G.LARC:.4f}")
    else:
        out.append(f"BAND circuits: {gfile} not found")
    ZC, R_FM = thin.ZC, (thin.R_F0 + thin.R_F1) / 2
    a_in = math.degrees(math.asin(5.9 / R_FM))
    ja = thin.P["joy_deg"]
    a_tr = ja + math.degrees(math.asin(3.6 / R_FM))
    sample = {"band_flex_thumb": (-1, 0.5 * (a_tr - a_in), None), "band_flex_away": (1, 90.0, 180.0)}      # side, trunk angle, strip angle
    body = solids["outer_body"]["metal"]
    def ext_msg(name, tag, ex, want):
        got = "none" if ex is None else f"{ex[0]:.4f} to {ex[1]:.4f}"
        ok = ex is not None and abs(ex[0] - want[0]) <= TOL and abs(ex[1] - want[1]) <= TOL
        print(f"band circuit {name} {tag}: X {got} (drawn {want[0]} to {want[1]}, width {want[1] - want[0]:.2f}){'' if ok else '  FAIL'}")
        if not ok:
            out.append(f"BAND circuit {name} {tag}: X {got}, drawn {want[0]} to {want[1]}")
        return ok
    for name, (sg, a_trunk, a_strip) in sample.items():
        fl = solids[name]["flex"]
        # neck in the slot: between the floor top and the start of the fold
        ex = _extent(fl, (0.0, sg * 5.9, 0.50), 0, -6.0, 2.0)
        ext_msg(name, "neck in the slot (Z 0.50)", ex, EXP["neck_x"])
        if ex is not None:
            slot = _extent(body, (0.0, sg * 5.9, ctx["Z_FLOOR"] - 0.05), 0, -6.0, 2.0)     # the slot's air gap at the same Y, just under the floor top: first inside run is metal, so look for the air run
            # the slot is the air run between two metal runs: scan the metal state and take the air interval that contains the neck centre
            c = (ex[0] + ex[1]) / 2
            lo_ = hi_ = c
            for _ in range(2000):
                if body.is_inside(Vector(lo_, sg * 5.9, ctx["Z_FLOOR"] - 0.05)):
                    break
                lo_ -= 0.005
            for _ in range(2000):
                if body.is_inside(Vector(hi_, sg * 5.9, ctx["Z_FLOOR"] - 0.05)):
                    break
                hi_ += 0.005
            print(f"band circuit {name} slot X {lo_:.3f} to {hi_:.3f} (centre {(lo_ + hi_) / 2:.3f}); neck centre {c:.3f}: off-centre {abs((lo_ + hi_) / 2 - c):.3f}, free to the ends {ex[0] - lo_:.3f} / {hi_ - ex[1]:.3f} (rule 0.15; centred within 0.01)")
            if abs((lo_ + hi_) / 2 - c) > 0.01:
                out.append(f"BAND circuit {name}: neck centre {c:.3f} is not the slot centre {(lo_ + hi_) / 2:.3f}")
        # trunk (embedded layer, mid radius)
        ra = math.radians(a_trunk)
        ex = _extent(fl, (0.0, R_FM * math.sin(ra), ZC + R_FM * math.cos(ra)), 0, -6.0, 3.0)
        ext_msg(name, f"trunk at {a_trunk:.1f} deg", ex, EXP["neck_x"])
        if a_strip is not None:
            rs = math.radians(a_strip)
            ex = _extent(fl, (0.0, R_FM * math.sin(rs), ZC + R_FM * math.cos(rs)), 0, -6.0, 3.0)
            ext_msg(name, f"pad strip at {a_strip:.1f} deg", ex, EXP["strip_x"])
        # foot: X at Z 1.35, |Y| run at X -2.25, top and bottom faces
        ex = _extent(fl, (0.0, sg * 4.3, 1.35), 0, -6.0, 2.0)
        ext_msg(name, "foot (Z 1.35, |Y| 4.3)", ex, EXP["foot_x"])
        ey = _extent(fl, (-2.25, 0.0, 1.35), 1, sg * 3.0 if sg > 0 else -6.0, 6.0 if sg > 0 else -3.0)
        gy = None if ey is None else (min(abs(ey[0]), abs(ey[1])), max(abs(ey[0]), abs(ey[1])))
        okf = gy is not None and abs(gy[0] - EXP["foot_y"][0]) <= TOL      # the inboard end of the foot; the other end runs on into the fold at this height
        print(f"band circuit {name} foot inboard end |Y| {'none' if gy is None else f'{gy[0]:.4f}'} (drawn {EXP['foot_y'][0]}; run at Z 1.35 to |Y| {'none' if gy is None else f'{gy[1]:.4f}'} including the fold's outer face){'' if okf else '  FAIL'}")
        if not okf:
            out.append(f"BAND circuit {name}: foot inboard end |Y| {gy}, drawn {EXP['foot_y'][0]}")
        ez = _extent(fl, (-2.25, sg * 4.3, 0.0), 2, 1.0, 1.6, step=0.01)
        okz = ez is not None and abs(ez[1] - EXP["foot_top"]) <= TOL and abs((ez[1] - ez[0]) - EXP["flex_t"]) <= TOL
        print(f"band circuit {name} foot Z {'none' if ez is None else f'{ez[0]:.4f} to {ez[1]:.4f} (thick {ez[1] - ez[0]:.4f})'} (drawn top {EXP['foot_top']}, thick {EXP['flex_t']}){'' if okz else '  FAIL'}")
        if not okz:
            out.append(f"BAND circuit {name}: foot Z {ez}, drawn top {EXP['foot_top']} thick {EXP['flex_t']}")
        # fold: inner and outer radius about the arc centre, at two angles; width at 45 degrees
        yc, zc = EXP["fold_centre"]
        for th in (30.0, 60.0):
            t_ = math.radians(th)
            lo, hi = None, None
            pr = lambda r_: Vector(-2.25, sg * (yc + r_ * math.cos(t_)), zc + r_ * math.sin(t_))
            for k in range(0, 1001):                    # inner face: first inside point going outward from r 0.5; outer face: first inside point going inward from r 1.0
                if fl.is_inside(pr(0.5 + k * 0.0005)):
                    lo = 0.5 + k * 0.0005
                    break
            for k in range(0, 1001):
                if fl.is_inside(pr(1.0 - k * 0.0005)):
                    hi = 1.0 - k * 0.0005
                    break
            if hi is None:
                lo = None
            okr = lo is not None and abs(lo - EXP["fold_in"]) <= TOL and abs(hi - EXP["fold_out"]) <= TOL
            print(f"band circuit {name} fold at {th:.0f} deg: radius {'none' if lo is None else f'{lo:.4f} to {hi:.4f}'} (drawn inner {EXP['fold_in']}, outer {EXP['fold_out']}){'' if okr else '  FAIL'}")
            if not okr:
                out.append(f"BAND circuit {name}: fold radius at {th:.0f} deg {lo} to {hi}, drawn {EXP['fold_in']} to {EXP['fold_out']}")
        t_ = math.radians(45.0)
        zz = zc + 0.755 * math.sin(t_)
        yy = sg * (yc + 0.755 * math.cos(t_))
        ew = _extent(fl, (0.0, yy, zz), 0, -6.0, 2.0)
        wmid = None if ew is None else ew[1] - ew[0]
        okw = wmid is not None and abs(wmid - (EXP["neck_w"] + (2.5 - EXP["neck_w"]) / 2)) <= 0.02
        print(f"band circuit {name} fold width at 45 deg: {'none' if wmid is None else f'{wmid:.4f}'} (taper from 1.8 to 2.5: 2.15){'' if okw else '  FAIL'}")
        if not okw:
            out.append(f"BAND circuit {name}: fold width at 45 deg {wmid}, drawn 2.15")
        # foot stiffener (polyimide, class polymer in the ribbon part)
        sp = by[name].subs.get("polymer", [])
        if len(sp) != 1:
            out.append(f"BAND circuit {name}: {len(sp)} foot stiffener solids, expected 1")
        else:
            bb = sp[0].bounding_box()
            okS = (abs(bb.min.X - EXP["stiff_x"][0]) <= TOL and abs(bb.max.X - EXP["stiff_x"][1]) <= TOL and abs(abs(bb.min.Y if sg > 0 else bb.max.Y) - EXP["stiff_y"][0]) <= TOL
                   and abs(abs(bb.max.Y if sg > 0 else bb.min.Y) - EXP["stiff_y"][1]) <= TOL and abs((bb.max.Z - bb.min.Z) - EXP["stiff_t"]) <= TOL
                   and abs(bb.max.Z - (EXP["foot_top"] - EXP["flex_t"])) <= TOL)
            print(f"band circuit {name} foot stiffener: X {bb.min.X:.4f} to {bb.max.X:.4f}, |Y| {min(abs(bb.min.Y), abs(bb.max.Y)):.4f} to {max(abs(bb.min.Y), abs(bb.max.Y)):.4f}, Z {bb.min.Z:.4f} to {bb.max.Z:.4f} "
                  f"(thick {bb.max.Z - bb.min.Z:.4f}; drawn thick {EXP['stiff_t']}, X {EXP['stiff_x']}, |Y| {EXP['stiff_y']}, under the foot){'' if okS else '  FAIL'}")
            if not okS:
                out.append(f"BAND circuit {name}: foot stiffener differs from the drawn one")
    # head stiffener (FLEX1): volume / (6.4 x 6.4) is its thickness
    hs = solids["band_flex_thumb"]["metal"]
    t_head = hs.volume / (6.4 * 6.4)
    print(f"band circuit band_flex_thumb head stiffener: volume {hs.volume:.4f} mm3 / (6.4 x 6.4) = thick {t_head:.4f} (drawn {EXP['stiff_t']})")
    if abs(t_head - EXP["stiff_t"]) > 0.001:
        out.append(f"BAND circuit head stiffener thick {t_head:.4f}, drawn {EXP['stiff_t']}")
    # the lands of the main board (band-interface.md section 2) lie inside each foot and the foot top is the joint under their faces
    bz = min(s_.bounding_box().min.Z for s_ in by["main_board"].subs["gold"])
    LANDS_X = (-3.015, -2.505, -1.995, -1.485)
    for name, sg in (("band_flex_thumb", -1), ("band_flex_away", 1)):
        fl = solids[name]["flex"]
        gap = bz - EXP["foot_top"]
        okj = abs(gap - EXP["land_z_gap"]) <= TOL and abs(bz - (ctx["Z_BD0"] - EXP["land_t"])) <= TOL
        print(f"band circuit {name}: board land faces at Z {bz:.4f}; foot top Z {EXP['foot_top']}: joint space {gap:.4f} (drawn {EXP['land_z_gap']}){'' if okj else '  FAIL'}")
        if not okj:
            out.append(f"BAND circuit {name}: joint space {gap:.4f}, drawn {EXP['land_z_gap']}")
        worst = 9.0
        for ly in (3.875, 4.775):
            for lx in LANDS_X:
                # the land's footprint must lie over the foot: probe its four corners at the foot's top face
                for dx in (-0.15, 0.15):
                    for dy in (-0.275, 0.275):
                        if not fl.is_inside(Vector(lx + dx, sg * ly + dy, EXP["foot_top"] - 0.01)):
                            worst = -1.0
        dmin = min((Pos(lx, sg * ly, bz + EXP["land_t"] / 2) * Box(0.30, 0.55, EXP["land_t"])).distance_to(fl) for ly in (3.875, 4.775) for lx in LANDS_X)
        print(f"band circuit {name}: 8 board lands (X {LANDS_X[0]} to {LANDS_X[-1]}, |Y| 3.875 and 4.775) over the foot: corners over the foot {'all' if worst > 0 else 'NOT all'}; least land to foot {dmin:.4f} mm")
        if worst < 0:
            out.append(f"BAND circuit {name}: a board land is not over the foot")
        if abs(dmin - EXP["land_z_gap"]) > TOL:
            out.append(f"BAND circuit {name}: land to foot {dmin:.4f}, drawn joint space {EXP['land_z_gap']}")
    return out


def report_ribbon_clearances(by, solids):
    """Reported only (a collision is found by the pair test of 1.): the least free space from each part of each ribbon to the parts round it.
    Groups: FLEX1 'foot' (vertical neck, fold, flat foot, foot stiffener), 'trunk', 'head' (flat head, bend, head stiffener); FLEX2 'foot', 'trunk', 'strip'."""
    groups = {}
    for name in ("band_flex_thumb", "band_flex_away"):
        fl = by[name].subs["flex"]
        stf = by[name].subs.get("polymer", [])
        if name == "band_flex_thumb":
            groups[name] = {"foot": fl[0:3] + stf, "trunk": fl[3:4], "head": fl[4:6] + by[name].subs.get("metal", [])}
        else:
            groups[name] = {"foot": fl[0:3] + stf, "trunk": fl[3:4], "strip": fl[4:5]}
    partners = ["vibration_motor", "cell", "cell_protection", "outer_body", "joystick_frame", "joystick_cap", "joy_sw_fingertip", "joy_sw_hand", "joy_sw_up",
                "joy_sw_down", "joy_sw_centre", "joystick_dam", "main_board", "band_flex_thumb", "band_flex_away", "motor_regulator", "motor_cap_in", "motor_cap_out", "storage"]
    out = []
    WALL_MIN_RIBBON = 0.10          # v8: the flex outline tolerance is +-0.10 (JLCPCB flex page, band-notes.md), so no part of a ribbon may touch the body (the channel wall or the slot wall)
    for name, grp in groups.items():
        for gname, gs in grp.items():
            for pn in partners:
                if pn == name:
                    continue
                best = None
                for pcls, psolids in by[pn].subs.items():
                    for ps in psolids:
                        for g in gs:
                            d = g.distance_to(ps)
                            if best is None or d < best:
                                best = d
                print(f"RIBBON-CLEARANCE {name} {gname} to {pn}: {best:.4f} mm")
                if pn == "outer_body" and best < WALL_MIN_RIBBON - 1e-6:
                    out.append(f"RIBBON {name} {gname} is {best:.4f} from the body, under {WALL_MIN_RIBBON}")
    return out


# 14. (v9) the board parts as the board plan places them, and the antenna's copper-free zone. Expected values are read from the plan's own files
# (design/wiring/ring-board-plan-work/placement-plan.csv; design/ecad/ring/pcb/OpenRing.pretty: F.Fab outline, pads, descr), never from thin.P or thin.BOARD.
PLAN_CSV = Path((__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/wiring/ring-board-plan-work/placement-plan.csv"))
FP_LIB = Path((__import__("pathlib").Path(__file__).resolve().parents[6].as_posix() + "/design/ecad/ring/pcb/OpenRing.pretty"))
BOARD_DRAWN = ("U1", "U2", "U3", "U4", "U5", "U6", "U11", "X1", "X2", "L10", "L71", "L72", "ANT1", "J1", "C83", "C84")   # the parts the model draws on the board
ZONE_X, ZONE_Y = (-13.60, -8.75), (3.10, 6.30)        # copper-free zone, ring-board-plan.md R2.0 item 2 (lead-decisions.md row "W2, rule on places")
ZONE_OWNER = "ANT1"                                   # the antenna's own body, terminations and lands are allowed in it (ring-board-plan.md e.3)
MOTOR_ZONE_MIN = 1.0                                  # motor body to the antenna keep-out, the lead's 1.0 mm (design/mech/mech-notes.md line 54)
BTOL = 0.01


def _fp_read(name):
    import re
    txt = (FP_LIB / (name + ".kicad_mod")).read_text()
    fab = []
    for m in re.finditer(r'\((fp_rect|fp_line)\s*\(start\s+([-\d.]+)\s+([-\d.]+)\)\s*\(end\s+([-\d.]+)\s+([-\d.]+)\)(.*?)\(layer\s+"([^"]+)"\)', txt, re.S):
        if m.group(7) == "F.Fab":
            fab += [(float(m.group(2)), float(m.group(3))), (float(m.group(4)), float(m.group(5)))]
    pads = [(m.group(1), float(m.group(2)), float(m.group(3)), float(m.group(4) or 0), float(m.group(5)), float(m.group(6)))
            for m in re.finditer(r'\(pad\s+"([^"]*)"\s+\w+\s+\w+\s*\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)\s*\(size\s+([-\d.]+)\s+([-\d.]+)\)', txt)]
    d = re.search(r'\(descr\s+"([^"]*)"', txt)
    descr = d.group(1) if d else ""
    t = re.search(r'(?:[A-Z]\s+)?(\d+(?:\.\d+)?)\s*x\s*(?:[A-Z]\s+)?(\d+(?:\.\d+)?)\s*x\s*(?:[A-Z]\s+)?(\d+(?:\.\d+)?)', descr)
    import hashlib
    return dict(fab=(min(p[0] for p in fab), min(p[1] for p in fab), max(p[0] for p in fab), max(p[1] for p in fab)) if fab else None,
                pads=pads, height=float(t.group(3)) if t else None, sha1=hashlib.sha1(txt.encode()).hexdigest()[:12])


def _turn(x, y, rot):
    t = math.radians(rot)
    return x * math.cos(t) + y * math.sin(t), -x * math.sin(t) + y * math.cos(t)


def check_board_plan(thin, P, by, solids, ctx):
    """14a. every drawn board part within BTOL of its plan row: place (body centre), body size (F.Fab turned; height where the footprint's descr gives
    one), turn (the part's declared turn, and every footprint land present as a gold land of the board, every ball of a ball chip on its land)."""
    out = []
    import hashlib
    plan = {r["reference"]: r for r in csv.DictReader(open(PLAN_CSV))}
    print(f"board plan: {PLAN_CSV} sha1 {hashlib.sha1(PLAN_CSV.read_bytes()).hexdigest()[:12]}, {len(plan)} rows")
    board_parts = {p.ref: p for p in P if p.layer == "board" and p.name != "main_board"}
    extra = sorted(set(board_parts) - set(BOARD_DRAWN))
    missing = sorted(set(BOARD_DRAWN) - set(board_parts))
    if extra or missing:
        out.append(f"BOARD-PLAN parts drawn on the board differ from the list: extra {extra}, missing {missing}")
    golds = [s_ for g_ in by["main_board"].subs.get("gold", []) for s_ in g_.solids()]
    gboxes = []
    for s_ in golds:
        b_ = s_.bounding_box()
        gboxes.append(((b_.min.X + b_.max.X) / 2, (b_.min.Y + b_.max.Y) / 2, b_.max.X - b_.min.X, b_.max.Y - b_.min.Y))
    worst = 0.0
    for ref in BOARD_DRAWN:
        if ref not in board_parts or ref not in plan:
            out.append(f"BOARD-PLAN {ref}: not in the model or not in the plan")
            continue
        p = board_parts[ref]
        r = plan[ref]
        fpn = r["footprint"].split(":")[1]
        fp = _fp_read(fpn)
        rot = float(r["rotation_deg"])
        cx, cy = float(r["x_mm"]), float(r["y_mm"])
        x0, y0, x1, y1 = fp["fab"]
        cs = [_turn(a, b, rot) for a, b in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
        ex_x = (cx + min(c[0] for c in cs), cx + max(c[0] for c in cs))
        ex_y = (cy + min(c[1] for c in cs), cy + max(c[1] for c in cs))
        body = [s_ for cls, lst in p.subs.items() if cls != "mark" for g_ in lst for s_ in g_.solids()]
        bxs = [s_.bounding_box() for s_ in body]
        gx = (min(b_.min.X for b_ in bxs), max(b_.max.X for b_ in bxs))
        gy = (min(b_.min.Y for b_ in bxs), max(b_.max.Y for b_ in bxs))
        gz = (min(b_.min.Z for b_ in bxs), max(b_.max.Z for b_ in bxs))
        dcx, dcy = (gx[0] + gx[1]) / 2 - cx, (gy[0] + gy[1]) / 2 - cy
        dsx, dsy = (gx[1] - gx[0]) - (ex_x[1] - ex_x[0]), (gy[1] - gy[0]) - (ex_y[1] - ex_y[0])
        bad = []
        if max(abs(dcx), abs(dcy)) > BTOL:
            bad.append(f"place off by ({dcx:+.4f}, {dcy:+.4f})")
        if max(abs(dsx), abs(dsy)) > BTOL:
            bad.append(f"body {gx[1] - gx[0]:.4f} x {gy[1] - gy[0]:.4f}, plan {ex_x[1] - ex_x[0]:.4f} x {ex_y[1] - ex_y[0]:.4f}")
        hz = None
        if fp["height"] is not None:
            # height of the body below the land faces (ball chips have no descr height); the board's under face is Z_BD0, lands pad_t thick
            hz = (ctx["Z_BD0"] - thin.P["pad_t"]) - gz[0]
            if abs(hz - fp["height"]) > BTOL:
                bad.append(f"height {hz:.4f}, footprint {fp['height']}")
        mrot = p.rot
        if mrot is None or abs(((mrot - rot) + 180) % 360 - 180) > BTOL:
            bad.append(f"turn {mrot}, plan {rot:g}")
        n_ok, n_l = 0, 0
        balls = []
        if ref in ("U1", "U2", "U4"):
            balls = [s_.bounding_box().center() for g_ in p.subs.get("metal", []) for s_ in g_.solids()]
        n_b = 0
        for (nm, px, py, prot, psx, psy) in fp["pads"]:
            dx, dy = _turn(px, py, rot)
            qx, qy = cx + dx, cy + dy
            q = round(prot + rot) % 180
            wsx, wsy = (psx, psy) if q == 0 else (psy, psx)
            n_l += 1
            if any(abs(g[0] - qx) <= BTOL and abs(g[1] - qy) <= BTOL and abs(g[2] - wsx) <= BTOL and abs(g[3] - wsy) <= BTOL for g in gboxes):
                n_ok += 1
            if balls and any(abs(b_.X - qx) <= BTOL and abs(b_.Y - qy) <= BTOL for b_ in balls):
                n_b += 1
        if n_ok != n_l:
            bad.append(f"lands on the board {n_ok} of {n_l}")
        if balls and (n_b != n_l or len(balls) != n_l):
            bad.append(f"balls on the lands {n_b} of {n_l} ({len(balls)} balls)")
        worst = max(worst, abs(dcx), abs(dcy), abs(dsx), abs(dsy))
        print(f"BOARD-PLAN {ref} ({p.name}): plan ({cx:.3f}, {cy:.3f}) turn {rot:g}, body {ex_x[1] - ex_x[0]:.4f} x {ex_y[1] - ex_y[0]:.4f}"
              + (f" x {fp['height']}" if fp["height"] is not None else "") + f" ({fpn} sha1 {fp['sha1']}); model centre off ({dcx:+.4f}, {dcy:+.4f}), "
              f"body {gx[1] - gx[0]:.4f} x {gy[1] - gy[0]:.4f}" + (f", height {hz:.4f}" if hz is not None else "") + f", turn {mrot}, lands {n_ok} of {n_l}"
              + (f", balls {n_b} of {n_l}" if balls else "") + ("  FAIL" if bad else "  ok"))
        for b_ in bad:
            out.append(f"BOARD-PLAN {ref}: {b_}")
    print(f"BOARD-PLAN: {len(BOARD_DRAWN)} parts, largest place or size difference {worst:.4f} mm (limit {BTOL})")
    return out


def check_zone(thin, P, by, solids, ctx):
    """14b. no metal part (class metal or gold) in the copper-free zone X -13.60 to -8.75, Y 3.10 to 6.30, over the whole height of the block, except
    the antenna's own; the board's gold lands there must be the antenna's footprint lands. Also prints the radio corner, the antenna's free space to
    metal, and the motor's distance to the zone (rule MOTOR_ZONE_MIN)."""
    out = []
    zb = Pos((ZONE_X[0] + ZONE_X[1]) / 2, (ZONE_Y[0] + ZONE_Y[1]) / 2, 0.0) * Box(ZONE_X[1] - ZONE_X[0], ZONE_Y[1] - ZONE_Y[0], 12.0)
    plan = {r["reference"]: r for r in csv.DictReader(open(PLAN_CSV))}
    ra = plan[ZONE_OWNER]
    fa = _fp_read(ra["footprint"].split(":")[1])
    alands = []
    for (nm, px, py, prot, psx, psy) in fa["pads"]:
        dx, dy = _turn(px, py, float(ra["rotation_deg"]))
        alands.append((float(ra["x_mm"]) + dx, float(ra["y_mm"]) + dy))
    hits = []
    for p in P:
        if p.ref == ZONE_OWNER:
            continue
        for cls in ("metal", "gold"):
            for g_ in p.subs.get(cls, []):
                for s_ in g_.solids():
                    v = common(s_, zb)
                    if v <= LIMIT:
                        continue
                    if p.name == "main_board" and cls == "gold":
                        c_ = s_.bounding_box().center()
                        if any(abs(c_.X - ax) <= BTOL and abs(c_.Y - ay) <= BTOL for ax, ay in alands):
                            continue
                    hits.append(f"{p.name}__{cls} {v:.4f} mm3")
    print(f"ZONE copper-free X {ZONE_X[0]} to {ZONE_X[1]}, Y {ZONE_Y[0]} to {ZONE_Y[1]}, Z -6 to 6: metal or gold of parts other than {ZONE_OWNER} and its lands: "
          f"{len(hits)} {hits}")
    if hits:
        out.append(f"ZONE holds metal: {hits}")
    other = []
    for p in P:
        v = sum(common(s_, zb) for lst in p.subs.values() for g_ in lst for s_ in g_.solids())
        if v > LIMIT:
            other.append(f"{p.name} {v:.4f}")
    print(f"ZONE: every part with volume in the zone prism (mm3, any class): {', '.join(other)}")
    # radio corner
    if "radio_corner" not in by:
        out.append("ZONE radio corner RC1 missing")
    else:
        rc = by["radio_corner"]
        cls = sorted(rc.subs)
        rb = solids["radio_corner"]["resin"].bounding_box() if "resin" in rc.subs else None
        print(f"radio corner RC1: classes {cls}; X {rb.min.X:.3f} to {rb.max.X:.3f}, Y {rb.min.Y:.3f} to {rb.max.Y:.3f}, Z {rb.min.Z:.3f} to {rb.max.Z:.3f}; "
              f"volume {solids['radio_corner']['resin'].volume:.4f} mm3")
        if cls != ["resin"]:
            out.append(f"ZONE radio corner classes {cls}, expected ['resin']")
        body = solids["outer_body"]["metal"]
        for lab, pt in (("pocket floor under ANT1", Vector(-10.8, 5.25, ctx["Z_FLOOR"] - 0.10)), ("floor beside the pocket", Vector(-13.0, 5.25, ctx["Z_FLOOR"] - 0.10))):
            print(f"radio corner: {lab} at ({pt.X}, {pt.Y}, {pt.Z:.2f}): metal {body.is_inside(pt)}, resin {solids['radio_corner']['resin'].is_inside(pt)}")
    # antenna: free space to the nearest metal (other parts' metal and gold, the body)
    if "antenna" in by:
        ant = [s_ for lst in by["antenna"].subs.values() for g_ in lst for s_ in g_.solids()]
        best = []
        for p in P:
            if p.name == "antenna":
                continue
            for cls in ("metal", "gold"):
                for g_ in p.subs.get(cls, []):
                    for s_ in g_.solids():
                        if p.name == "main_board" and cls == "gold":
                            c_ = s_.bounding_box().center()
                            if any(abs(c_.X - ax) <= BTOL and abs(c_.Y - ay) <= BTOL for ax, ay in alands):
                                continue
                        bb_ = s_.bounding_box()
                        if bb_.min.X > -4.0:
                            continue
                        d_ = min(a_.distance_to(s_) for a_ in ant)
                        best.append((d_, f"{p.name}__{cls}"))
        best.sort()
        print("ANTENNA free space to metal (nearest 5, its own lands excluded): " + ", ".join(f"{n_} {d_:.4f}" for d_, n_ in best[:5]) + " mm")
        ab = by["antenna"].subs["ceramic"][0].bounding_box()
        print(f"ANTENNA body X {ab.min.X:.3f} to {ab.max.X:.3f}, Y {ab.min.Y:.3f} to {ab.max.Y:.3f}, Z {ab.min.Z:.3f} to {ab.max.Z:.3f}; floor top Z {ctx['Z_FLOOR']:.3f}, "
              f"pocket bottom Z {ctx.get('rc_pocket_bottom')}: under the antenna {ab.min.Z - ctx.get('rc_pocket_bottom', ab.min.Z):.4f} mm of room")
    # motor to the zone (item 44)
    mot = solids["vibration_motor"]["metal"]
    dmz = mot.distance_to(zb)
    print(f"MOTOR body to the copper-free zone prism: {dmz:.4f} mm (rule {MOTOR_ZONE_MIN}, design/mech/mech-notes.md line 54)")
    if dmz < MOTOR_ZONE_MIN:
        out.append(f"MOTOR body {dmz:.4f} from the copper-free zone, under {MOTOR_ZONE_MIN}")
    return out


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
        # v7: the cap stands where the accepted exterior's cap stands (two-sided; the proud test of 2. is one-sided)
        capr = max(math.hypot(v.Y, v.Z - thin.ZC) for v in capp.vertices())
        dtop = capr - ctx["rtop_joy_exterior"]
        print(f"joystick cap top r {capr:.3f} against the exterior's joystick top r {ctx['rtop_joy_exterior']:.3f}: difference {dtop:+.3f} mm (limit 0.02)")
        if abs(dtop) > 0.02:
            findings.append(f"JOYSTICK cap top r {capr:.3f} is {dtop:+.3f} from the exterior's joystick top r {ctx['rtop_joy_exterior']:.3f} (limit 0.02)")
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
    # 13. (v8) the two band circuits as drawn in design/ecad/band (band-interface.md sections 2, 3, 9; band-notes.md "Changes other files need").
    # Every expected value is written here (or read from design/ecad/band/band_geom.py, the circuits' own geometry file, read only), never from thin.P, and every
    # value is measured on the solids. A model whose tail width goes back to 1.4 in ONE place (neck, trunk, strip, fold) fails by its own line.
    findings.extend(check_band_circuits(thin, m, P, by, solids, ctx))
    findings.extend(report_ribbon_clearances(by, solids))
    # 14. (v9) board parts as the board plan places them; the antenna's copper-free zone and the radio corner
    findings.extend(check_board_plan(thin, P, by, solids, ctx))
    findings.extend(check_zone(thin, P, by, solids, ctx))
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
