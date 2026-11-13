#!/usr/bin/env python3
"""Fit check of the recommended microphone sound path (mic-path.md), against the inside model v4.

Reads (read only):
  design/mech/thin/placement.csv   every part's centre and size (inside model v4)
  design/mech/thin/layers.json     layer of each part, band axis
  design/look/s1/out/ring-merged32e.step   the exterior body, used only to probe the floor under each sound hole
                                           and the wall thickness for the rejected options

Rules used (quoted in mic-path.md section 5):
  R1 check_thin.py line 25 and line 63: two parts may share at most LIMIT = 0.001 mm3.
  R2 architecture.md line 381: "Parts with a 0.2 mm keep-out" on the board.
  R3 check_thin.py line 26: WALL_MIN = 0.40 mm of metal (used here for the metal round a hole in the floor).
  R4 check_thin.py lines 8 and 161: the floor is at least 0.30; no under-board part lies below the floor top.
  R5 thin.py line 366: the panel pocket is the screen outline + 0.1 (27.45 x 12.9): the parts under the board stay inside it.
Design rules from the datasheet copies (mic-path.md section 4):
  D1 SPK0641HT4H-1 datasheet text line 369: "recommended Gasket Cavity Diameter is D >= 1.0mm"
  D2 same, lines 369-370: "recommended Case Hole Diameter is 1.0 <= D <= 1.5mm"
  D3 PUI guide text lines 112-113: external sound hole and gasket channel at least 0.1 mm larger than the microphone's sound hole.

Prints one line per check and ends with RESULT PASS or RESULT FAIL <what>. Exit 0 on PASS, 1 on FAIL.
"""
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design"))
PLACEMENT = ROOT / "mech/thin/placement.csv"
LAYERS = ROOT / "mech/thin/layers.json"
STEP = ROOT / "look/s1/out/ring-merged32e.step"

LIMIT = 0.001          # R1
KEEP = 0.20            # R2
WALL_MIN = 0.40        # R3
FLOOR_MIN = 0.30       # R4
POCKET_ADD = 0.10      # R5

# stack numbers of thin.py line 37-38 (P: under=1.00, gap=0.05, pad_t=0.02); board bottom comes from placement.csv
UNDER, GAP, PAD_T = 1.00, 0.05, 0.02
BORE_D = 18.95         # thin.py line 36 (bore_d)

# ---------------- the recommended design (mic-path.md section 3) ----------------
MIC = dict(part="Knowles SPK0641HT4H-1", L=4.00, W=3.00, H=1.00, tolL=0.10, tolW=0.10, tolH=0.10,
           port_d=0.25, port_tol=0.05, port_from_end=1.030, port_from_side=1.500)
# body centres (X, Y); length L along X, width W along Y; the port end of each part faces its own block end
MICS = {
    "mic_1": dict(ref="U5", cx=-10.8, cy=-4.8, port_end=-1),   # port toward the hand end (-X)
    "mic_2": dict(ref="U6", cx=10.8, cy=-4.8, port_end=+1),    # port toward the fingertip end (+X)
}
POCKET_DEPTH = 0.10    # floor pocket under each microphone, from the floor top down
POCKET_MARGIN = 0.20   # pocket outline = microphone outline at nominal size + 0.20 each side, clipped at the inner wall
GASKET_OD, GASKET_ID = 1.80, 1.00
HOLE_D = 1.00
SEAT_D, SEAT_DEPTH = 2.00, 0.10   # membrane seat: counterbore from the block's underside, coaxial with the hole


def rows():
    with open(PLACEMENT) as f:
        return list(csv.DictReader(f))


def fnum(r, k):
    v = r.get(k, "")
    return float(v) if v not in ("", None) else None


def extent(r):
    """Axis-aligned extent of a placement row. Rows with an angle are turned about the band axis (X):
    their X extent is exact, Y and Z use the half diagonal of size_y and size_z (conservative)."""
    x, y, z = fnum(r, "x"), fnum(r, "y"), fnum(r, "z")
    sx, sy, sz = fnum(r, "size_x"), fnum(r, "size_y"), fnum(r, "size_z")
    if fnum(r, "angle_deg") is not None:
        h = math.hypot(sy, sz) / 2
        return (x - sx / 2, x + sx / 2, y - h, y + h, z - h, z + h)
    return (x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2, z - sz / 2, z + sz / 2)


def overlap_vol(a, b):
    dx = min(a[1], b[1]) - max(a[0], b[0])
    dy = min(a[3], b[3]) - max(a[2], b[2])
    dz = min(a[5], b[5]) - max(a[4], b[4])
    return dx * dy * dz if dx > 0 and dy > 0 and dz > 0 else 0.0


def plan_gap(a, b):
    dx = max(a[0] - b[1], b[0] - a[1], 0.0)
    dy = max(a[2] - b[3], b[2] - a[3], 0.0)
    if dx == 0 and dy == 0:
        ox = min(a[1], b[1]) - max(a[0], b[0])
        oy = min(a[3], b[3]) - max(a[2], b[2])
        return -min(ox, oy)
    return math.hypot(dx, dy)


def main():
    out = []
    fails = []

    def line(tag, ok, text):
        s = f"{tag} {'PASS' if ok else 'FAIL'} {text}" if ok is not None else f"{tag} INFO {text}"
        print(s, flush=True)
        if ok is False:
            fails.append(tag)

    R = rows()
    L = json.load(open(LAYERS))
    layer_of = {}
    for lay in L["layers"]:
        for p in lay["parts"]:
            layer_of.setdefault(p, []).append(lay["name"])
    by = {r["part"]: r for r in R}
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    line("C00", None, f"inputs: {PLACEMENT} sha256 {sha(PLACEMENT)}; {LAYERS} sha256 {sha(LAYERS)}; {STEP} sha256 {sha(STEP)}")
    once = all(len(layer_of.get(r["part"], [])) == 1 for r in R) and len(layer_of) == len(R)
    line("C01", once and "mic_1" in by and "mic_2" in by and layer_of["mic_1"] == ["board"] and layer_of["mic_2"] == ["board"],
         f"placement.csv {len(R)} rows, layers.json {len(layer_of)} parts, every part in exactly one layer: {once}; mic_1 and mic_2 rows in layer 'board'")

    mb = by["main_board"]
    z_bd0 = fnum(mb, "z") - fnum(mb, "size_z") / 2
    ztop = z_bd0 - PAD_T
    z_floor = z_bd0 - UNDER - GAP
    z_pk = z_floor - POCKET_DEPTH
    line("C02", abs(z_floor - 0.40) < 1e-6, f"stack: board underside Z {z_bd0:.3f} (main_board row), part tops Z {ztop:.3f} (pad {PAD_T}), floor top Z {z_floor:.3f}, pocket bottom Z {z_pk:.3f}")

    scr = by["screen"]
    pk_x, pk_y = (fnum(scr, "size_x") + POCKET_ADD) / 2, (fnum(scr, "size_y") + POCKET_ADD) / 2
    bx, by_ = fnum(mb, "size_x") / 2, fnum(mb, "size_y") / 2
    line("C03", None, f"interior pocket (R5) X +-{pk_x:.3f} Y +-{pk_y:.3f}; board outline X +-{bx:.3f} Y +-{by_:.3f}, corner radius 0.8 (placement.csv main_board note)")

    others = [r for r in R if r["part"] not in ("mic_1", "mic_2", "outer_body")]
    under_board = [r for r in others if layer_of[r["part"]] == ["board"] and r["part"] != "main_board"]

    geo = {}
    for nm, m in MICS.items():
        for tag_size, (ls, ws, hs) in (("nominal", (MIC["L"], MIC["W"], MIC["H"])),
                                       ("max", (MIC["L"] + MIC["tolL"], MIC["W"] + MIC["tolW"], MIC["H"] + MIC["tolH"]))):
            box = (m["cx"] - ls / 2, m["cx"] + ls / 2, m["cy"] - ws / 2, m["cy"] + ws / 2, ztop - hs, ztop)
            geo[(nm, tag_size)] = box
        n = geo[(nm, "nominal")]
        px = (n[1] - MIC["port_from_end"]) if m["port_end"] > 0 else (n[0] + MIC["port_from_end"])
        py = n[2] + MIC["port_from_side"]
        m["port"] = (px, py)
        line(f"C10.{nm}", None, f"{m['ref']} {MIC['part']} body X {n[0]:.3f}..{n[1]:.3f} Y {n[2]:.3f}..{n[3]:.3f} Z {n[4]:.3f}..{n[5]:.3f} "
             f"(centre {m['cx']:.3f}, {m['cy']:.3f}, {(n[4] + n[5]) / 2:.3f}); on the board's under face, port facing -Z at X {px:.3f} Y {py:.3f}")

    # R1: no overlap with any other part (maximum size)
    for nm in MICS:
        b = geo[(nm, "max")]
        worst = max(((overlap_vol(b, extent(r)), r["part"]) for r in others), key=lambda t: t[0])
        line(f"C11.{nm}", worst[0] <= LIMIT, f"overlap of the body at maximum size with every other part (box test, {len(others)} parts): largest {worst[0]:.4f} mm3 with {worst[1]} (R1 limit {LIMIT})")
    b1, b2 = geo[("mic_1", "max")], geo[("mic_2", "max")]
    line("C12", overlap_vol(b1, b2) <= LIMIT, f"mic_1 x mic_2 at maximum size: {overlap_vol(b1, b2):.4f} mm3")

    # R2: 0.2 keep-out on the board, nominal outlines
    for nm in MICS:
        b = geo[(nm, "nominal")]
        gaps = sorted((plan_gap(b, extent(r)), r["part"]) for r in under_board)
        line(f"C13.{nm}", gaps[0][0] >= KEEP - 1e-9, f"plan gap to the nearest board part: {gaps[0][0]:.3f} mm to {gaps[0][1]}, next {gaps[1][0]:.3f} to {gaps[1][1]} (R2 keep-out {KEEP})")

    # R5: inside the interior pocket (max size) and pads on the board (nominal, with the corner radius)
    for nm in MICS:
        b = geo[(nm, "max")]
        inside = b[0] >= -pk_x and b[1] <= pk_x and b[2] >= -pk_y and b[3] <= pk_y
        line(f"C14.{nm}", inside, f"body at maximum size inside the interior pocket: X {b[0]:.3f}..{b[1]:.3f} in +-{pk_x:.3f}, Y {b[2]:.3f}..{b[3]:.3f} in +-{pk_y:.3f}; least margin {min(b[0] + pk_x, pk_x - b[1], b[2] + pk_y, pk_y - b[3]):.3f} mm")
        n = geo[(nm, "nominal")]
        rc = 0.8
        corners_ok = True
        for cx_, cy_ in ((n[0], n[2]), (n[0], n[3]), (n[1], n[2]), (n[1], n[3])):
            if abs(cx_) > bx + 1e-9 or abs(cy_) > by_ + 1e-9:
                corners_ok = False
            ax, ay = bx - rc, by_ - rc
            if abs(cx_) > ax and abs(cy_) > ay and math.hypot(abs(cx_) - ax, abs(cy_) - ay) > rc + 1e-9:
                corners_ok = False
        line(f"C15.{nm}", corners_ok, f"nominal outline on the board (27.2 x 12.6, corner radius 0.8): X {n[0]:.3f}..{n[1]:.3f}, Y {n[2]:.3f}..{n[3]:.3f}")

    # R4: Z. Lid of the tallest part above the pocket bottom; floor under the pocket at least 0.30
    for nm in MICS:
        lid_max = geo[(nm, "max")][4]
        lid_nom = geo[(nm, "nominal")][4]
        lid_min = ztop - (MIC["H"] - MIC["tolH"])
        line(f"C16.{nm}", lid_max - z_pk > 0, f"gap from lid to pocket bottom: nominal {lid_nom - z_pk:.3f}, tallest part {lid_max - z_pk:.3f}, shortest part {lid_min - z_pk:.3f} mm (must stay above 0; the gasket fills it)")
        line(f"C17.{nm}", z_pk >= FLOOR_MIN - 1e-9, f"floor under the pocket {z_pk:.3f} mm (R4 at least {FLOOR_MIN}); a part at maximum height is {z_floor - lid_max:.3f} mm below the floor top, so the pocket is needed")

    # pocket outline: clipped at the inner wall; metal to the floor slots
    pockets = {}
    for nm in MICS:
        n = geo[(nm, "nominal")]
        pkb = (max(n[0] - POCKET_MARGIN, -pk_x), min(n[1] + POCKET_MARGIN, pk_x), max(n[2] - POCKET_MARGIN, -pk_y), min(n[3] + POCKET_MARGIN, pk_y))
        pockets[nm] = pkb
        slot_gap = min(plan_gap(pkb + (0, 1), (-2.2 - 1.3, -2.2 + 1.3, s * 5.9 - 0.3, s * 5.9 + 0.3, 0, 1)) for s in (1, -1))
        line(f"C18.{nm}", slot_gap >= WALL_MIN, f"floor pocket X {pkb[0]:.3f}..{pkb[1]:.3f} Y {pkb[2]:.3f}..{pkb[3]:.3f} depth {POCKET_DEPTH}; metal to the nearest floor slot (thin.py slot X -2.2, 2.6 x 0.6 at Y +-5.9) {slot_gap:.3f} mm (R3 {WALL_MIN})")

    # gasket and hole against the datasheet rules
    for nm, m in MICS.items():
        px, py = m["port"]
        n = geo[(nm, "nominal")]
        marg = min(px - n[0], n[1] - px, py - n[2], n[3] - py) - GASKET_OD / 2
        line(f"C19.{nm}", marg >= 0.0, f"gasket ring OD {GASKET_OD} ID {GASKET_ID} centred on the port lies on the lid: least margin to the lid edge {marg:.3f} mm")
    line("C20", GASKET_ID >= 1.0, f"gasket cavity diameter {GASKET_ID} (D1: at least 1.0)")
    line("C21", 1.0 <= HOLE_D <= 1.5, f"case hole diameter {HOLE_D} (D2: 1.0 to 1.5)")
    line("C22", HOLE_D >= MIC["port_d"] + MIC["port_tol"] + 0.1 and GASKET_ID >= MIC["port_d"] + MIC["port_tol"] + 0.1,
         f"hole {HOLE_D} and gasket {GASKET_ID} against port {MIC['port_d']} + {MIC['port_tol']} + 0.1 = {MIC['port_d'] + MIC['port_tol'] + 0.1:.2f} (D3)")
    line("C23", abs(GASKET_ID - HOLE_D) < 1e-9, f"gasket bore {GASKET_ID} equals the hole {HOLE_D} (PUI guide lines 101-103: gasket as close as possible to the external hole)")
    lid = geo[('mic_1', 'nominal')][4]
    line("C24", None, f"channel from port to the room, one straight vertical bore: gasket bore d {GASKET_ID} from Z {z_pk:.2f} to {lid:.2f} ({lid - z_pk:.2f} nominal), "
         f"hole d {HOLE_D} from Z {SEAT_DEPTH:.2f} to {z_pk:.2f} ({z_pk - SEAT_DEPTH:.2f}), membrane seat d {SEAT_D} from Z 0.00 to {SEAT_DEPTH:.2f}: total {lid:.2f} mm")

    # exterior probes (STEP): the hole opens to air at the underside; metal round the hole
    from build123d import import_step, Vector  # noqa: E402
    s = import_step(str(STEP))
    body = {c.label: c for c in s.children}["body"]
    ins = lambda x, y, z: body.is_inside(Vector(x, y, z))
    for nm, m in MICS.items():
        px, py = m["port"]
        zs = [round(-0.20 + 0.01 * k, 3) for k in range(0, 61)]
        col = [ins(px, py, z) for z in zs]
        z_under = next((z for z, c in zip(zs, col) if c), None)
        air_below = not ins(px, py, -0.05) and not ins(px, py, -0.5) and not ins(px, py, -1.0)
        metal_col = all(ins(px, py, z) for z in (0.02, 0.10, 0.20, 0.28))
        line(f"C25.{nm}", air_below and metal_col and z_under is not None and abs(z_under) <= 0.02,
             f"exterior at the port X {px:.3f} Y {py:.3f}: body underside at Z {z_under}, air at Z -0.05, -0.5 and -1.0: {air_below}; metal from Z 0.02 to 0.28 before the hole is cut: {metal_col}")
        rr = SEAT_D / 2 + WALL_MIN
        ring = all(ins(px + rr * math.cos(t), py + rr * math.sin(t), zz) for t in [k * math.pi / 12 for k in range(24)] for zz in (0.02, 0.15, 0.28))
        line(f"C26.{nm}", ring, f"metal at {WALL_MIN} mm from the membrane seat edge (seat d {SEAT_D}) all round (24 directions, Z 0.02, 0.15, 0.28): {ring} (R3)")
        web = z_pk - SEAT_DEPTH
        line(f"C26w.{nm}", None, f"metal web between the membrane seat (Z 0 to {SEAT_DEPTH}) and the pocket bottom (Z {z_pk:.2f}): {web:.2f} mm over a ring from d {HOLE_D} to d {SEAT_D}; "
             f"below the 0.30 stack floor of R4 in this ring only: a local departure, no project rule covers it")
        # air gap to a finger the size of the bore (a cylinder continued along X): an estimate, not a pass or fail
        zc = L["band_axis"]["z"]
        rf = BORE_D / 2
        zskin = zc + math.sqrt(max(rf * rf - py * py, 0.0))
        line(f"C27.{nm}", None, f"[ESTIMATE] a finger as a cylinder of the bore ({BORE_D} mm, axis Z {zc}) lies at Z {zskin:.3f} under the hole: air gap {(z_under or 0) - zskin:.3f} mm; at Y 0 the gap is {(0 - (zc + rf)):.3f} mm")

    # walls for the rejected options: thickness of metal outward from the interior pocket
    def run(x0, y0, z, dx, dy, step=0.005, reach=3.0):
        n = 0.0
        while n < reach and ins(x0 + dx * (n + step / 2), y0 + dy * (n + step / 2), z):
            n += step
        return n
    for z in (0.35, 0.84, 1.20):
        wy = run(-11.0, -pk_y, z, 0, -1)
        wyp = run(-11.0, pk_y, z, 0, 1)
        wx = run(-pk_x, -4.8, z, -1, 0)
        wxp = run(pk_x, -4.8, z, 1, 0)
        line(f"C28.z{z}", None, f"metal outward from the interior pocket at Z {z}: -Y wall at X -11 {wy:.3f} mm, +Y wall at X -11 {wyp:.3f}, hand end at Y -4.8 {wx:.3f}, fingertip end at Y -4.8 {wxp:.3f}")

    # second-best path: a slit under the lid from the gasket bore to an end wall, at the pocket depth
    for nm, m in MICS.items():
        px, py = m["port"]
        inner = (pk_x - abs(px)) - GASKET_ID / 2
        wz = run(math.copysign(pk_x, px), py, 0.35, math.copysign(1, px), 0)
        line(f"C30.{nm}", None, f"second best (end-wall slit): from the gasket bore edge to the inner end wall {inner:.3f} mm, through the end wall at Z 0.35 {wz:.3f} mm, "
             f"total {inner + wz:.3f} mm; slit height = lid gap {geo[(nm, 'nominal')][4] - z_pk:.3f} nominal, {geo[(nm, 'max')][4] - z_pk:.3f} to {ztop - (MIC['H'] - MIC['tolH']) - z_pk:.3f} with the height tolerance")

    # brief item 4: the larger top-port parts placed where today's 3.5 x 2.65 part sits
    old = {nm: (fnum(by[nm], "x"), fnum(by[nm], "y")) for nm in ("mic_1", "mic_2")}
    for label, (ls, ws, hs) in (("4.0x3.0x1.0 L along X", (4.0, 3.0, 1.0)), ("4.0x3.0x1.0 L along Y", (3.0, 4.0, 1.0)),
                                ("4.0x2.0x1.1 L along X", (4.0, 2.0, 1.1)), ("4.0x2.0x1.1 L along Y", (2.0, 4.0, 1.1))):
        for nm, (ox, oy) in old.items():
            b = (ox - ls / 2, ox + ls / 2, oy - ws / 2, oy + ws / 2, ztop - hs, ztop)
            hits = [(overlap_vol(b, extent(r)), r["part"]) for r in others if overlap_vol(b, extent(r)) > LIMIT]
            near = sorted((plan_gap(b, extent(r)), r["part"]) for r in under_board)[0]
            wall = max(0.0, -pk_y - b[2], b[3] - pk_y, -pk_x - b[0], b[1] - pk_x)
            below = max(0.0, z_floor - b[4])
            line(f"C29.{nm}.{label.replace(' ', '_')}", None,
                 f"at today's centre ({ox}, {oy}): X {b[0]:.3f}..{b[1]:.3f} Y {b[2]:.3f}..{b[3]:.3f}; past the interior wall by {wall:.3f} mm; below the floor top by {below:.3f} mm; "
                 f"part overlaps {[(p, round(v, 4)) for v, p in hits]}; nearest board part {near[1]} at {near[0]:.3f} mm (keep-out {KEEP})")

    print(f"checks: {sum(1 for _ in fails)} failed")
    print("RESULT PASS" if not fails else "RESULT FAIL " + ", ".join(fails))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
