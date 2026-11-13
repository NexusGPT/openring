"""Slim pilot: a thin flat black glass slab on a narrow metal band.

Run:  cd <look folder> && ../.venv/bin/python s1/exterior.py [--variant block65|band41|band32]
  block65  (default) the 6.5 mm pilot with its 4.6 x 1.5 band; the contract check applies
  band41   battery in the band: block 4.10 tall, band 8.0 wide, wall 2.6 (band-battery study)
  band32   the same with a 3.20 block
Each run writes out/ring-<variant>.glb (+ .step); block65 also writes out/ring.glb.
"""
import sys, os, json
sys.path.insert(0, (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/look/shared"))
from envelope_slim import (LIMITS, SCREEN_CX, SCREEN_CY, LIT_X, LIT_Y, PART_NAMES,
                           check_exterior, export_look)
from build123d import Box, Cylinder, Pos, Rot, RectangleRounded, extrude, fillet, Axis, Align, Compound, Plane, Vector, Sphere

OUT = (__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/look/s1/out")

VARIANT = sys.argv[sys.argv.index("--variant") + 1] if "--variant" in sys.argv else "block65"
VARIANTS = {
    # height, band width X, band wall, band edge fillet, joystick (shape, X, length, height, proud), button (length, height), mic Z, ctrl Z
    "block65": dict(H=6.5, BW=4.6, BWALL=1.5, BEDGE=0.0, joy=("round", 6.0, 3.0, 3.0, 0.5), btn=(4.0, 1.5), mic_z=4.6, ctrl_z=3.3),
    "band41": dict(H=4.1, BW=8.0, BWALL=2.6, BEDGE=0.8, joy=("pill", 10.0, 5.6, 1.6, 0.4), btn=(4.0, 1.3), mic_z=2.6, ctrl_z=1.9),
    "band32": dict(H=3.2, BW=8.0, BWALL=2.6, BEDGE=0.8, joy=("pill", 10.0, 5.6, 1.2, 0.4), btn=(4.0, 1.0), mic_z=1.9, ctrl_z=1.5),
}
VARIANTS["merged32"] = dict(VARIANTS["band32"], merged=True)   # real numbers are in M (merged32 section)
VARIANTS["merged32b"] = dict(VARIANTS["band32"], merged=True, curved=True)   # real numbers are in B (merged32b section)
VARIANTS["merged32e"] = dict(VARIANTS["band32"], merged=True, curved=True, arc=True)
VARIANTS["merged32f"] = dict(VARIANTS["band32"], merged=True, curved=True, arc=True)   # merged32e + the inside model v4 openings (thin-notes K2, K3)
VARIANTS["merged32g"] = dict(VARIANTS["band32"], merged=True, curved=True, arc=True)   # merged32f with the joystick angle per ring size (architecture 17.25)
VARIANTS["merged32h"] = dict(VARIANTS["band32"], merged=True, curved=True, arc=True)   # merged32g with a round, textured, more proud joystick (owner 2026-11-11)
VARIANTS["merged417"] = dict(VARIANTS["band32"], merged=True, curved=True, arc=True)   # merged32h with everything above the board 0.970 higher (owner card 2026-11-13, screen-cable-study.md 4.3)
VARIANTS["merged417flat"] = dict(VARIANTS["band32"], merged=True, curved=True, arc=True)   # owner card 2026-11-13 "Flat glass, 4.15 mm": merged417 with a flat top, US 7 to 13
VARIANTS["merged417flatw"] = dict(VARIANTS["band32"], merged=True, curved=True, arc=True)   # owner 2026-11-13 "2: three windows": merged417flat + side slit and two blind windows
VARIANTS["merged32d1"] = dict(VARIANTS["band32"], merged=True, curved=True, arc=True)
VARIANTS["merged32d2"] = dict(VARIANTS["band32"], merged=True, curved=True, arc=True)
VARIANTS["merged32c"] = dict(VARIANTS["band32"], merged=True, curved=True, arc=True)   # numbers are in C (merged32c section)
V = VARIANTS[VARIANT]
KIND = "merged417flat" if VARIANT == "merged417flatw" else VARIANT   # merged417flatw takes every merged417flat branch
WIN = VARIANT == "merged417flatw"
MERGED = bool(V.get("merged"))
CURVED = bool(V.get("curved"))
ARC = bool(V.get("arc"))
STUDY = VARIANT != "block65"
# band variants: the band runs 0.6 up into the block (CHOSEN) so no flat band top shows outside the rounded underside edge
BAND_TOP = 0.0 if VARIANT == "block65" else 0.6

# ---- dimensions (mm), all from the briefs unless marked CHOSEN ----
BX, BY, BZ, CORNER_R = 28.6, 14.05, V["H"], 1.3
BOT_FILLET = 0.6
GLASS_T, GLASS_TOP_R = 0.5, 0.25
SCREEN_T = 0.02
BAND_W, BAND_WALL, BAND_ID, BAND_EDGE = V["BW"], V["BWALL"], LIMITS["band_inner_d_size9"], V["BEDGE"]
FINGER_GAP = 0.3                                   # block underside above the finger
JOY_KIND, JOY_X, JOY_L, JOY_H, JOY_PROUD = V["joy"]
CTRL_Z = V["ctrl_z"]
BTN_L, BTN_H, BTN_PROUD, BTN_X = V["btn"][0], V["btn"][1], 0.3, -5.0
LIGHT_D, LIGHT_T, LIGHT_X, LIGHT_Y = 1.0, 0.02, -12.0, 0.0
MIC_W, MIC_H, MIC_DEPTH, MIC_Z, MIC_XS = 1.4, 0.4, 0.3, V["mic_z"], (-11.0, 11.0)
PAD_D, PAD_XPOS, PAD_YS = 1.2, -11.0, (-3.0, -1.0, 1.0, 3.0)
# CHOSEN by the builder (listed in direction.md)
JOY_EDGE_R = 0.2       # rounding of the round joystick cap top edge (block65)
MIC_MESH_T = 0.06      # acoustic mesh solid at the slot bottom (mic_1, mic_2)
PAD_SINK = 0.1         # pad thickness, sunk into the underside so its face is flush at Z 0

BODY_H = BZ - GLASS_T

# --size <US size>: changes only the band bore. Bore per size from design/mech/dimensions.csv (band_inner_d_size<N>, read only).
SIZE = None
if "--size" in sys.argv:
    SIZE = int(sys.argv[sys.argv.index("--size") + 1])
    import csv
    _bores = {}
    with open((__import__("pathlib").Path(__file__).resolve().parents[3].as_posix() + "/design/mech/dimensions.csv"), newline="") as _f:
        for _row in csv.reader(_f):
            if _row and _row[0].startswith("band_inner_d_size"):
                _bores[int(_row[0][len("band_inner_d_size"):])] = float(_row[1])
    BAND_ID = _bores[SIZE]
    print(f"US size {SIZE}: bore {BAND_ID} mm (design/mech/dimensions.csv)")


def rrect(h, z0):
    return Pos(0, 0, z0) * extrude(RectangleRounded(BX, BY, CORNER_R), amount=h)


def pill(lx, lz, proud, x, z, y0):
    """pill cap standing `proud` from the wall plane y0 (+Y side), long side along X"""
    b = Pos(x, y0 + proud / 2, z) * Box(lx, proud, lz)
    return fillet(b.edges().filter_by(Axis.Y), lz / 2 - 0.005)


def main():
    os.makedirs(OUT, exist_ok=True)
    if ARC:
        return main_merged_c()
    if CURVED:
        return main_merged_b()
    if MERGED:
        return main_merged()
    wall_y = BY / 2
    body = rrect(BODY_H, 0)
    body = fillet(body.edges().filter_by(Plane.XY).group_by(Axis.Z)[0], BOT_FILLET)
    glass = rrect(GLASS_T, BODY_H)
    glass = fillet(glass.edges().filter_by(Plane.XY).group_by(Axis.Z)[-1], GLASS_TOP_R)

    mics = []
    for x in MIC_XS:
        slot = Pos(x, -wall_y + MIC_DEPTH / 2 - 0.5, MIC_Z) * Box(MIC_W, MIC_DEPTH + 1.0, MIC_H)
        slot = fillet(slot.edges().filter_by(Axis.Y), MIC_H / 2 - 0.005)
        mesh = Pos(x, -wall_y + MIC_DEPTH - MIC_MESH_T / 2, MIC_Z) * Box(MIC_W, MIC_MESH_T, MIC_H)
        mesh = fillet(mesh.edges().filter_by(Axis.Y), MIC_H / 2 - 0.005)
        mics.append((slot, mesh))
    pads = [Pos(PAD_XPOS, y, 0) * Cylinder(PAD_D / 2, PAD_SINK, align=(Align.CENTER, Align.CENTER, Align.MIN)) for y in PAD_YS]

    outer = body + glass          # skin before the inlets are cut (contract: inlets are openings)
    bb = outer.bounding_box()
    size = (bb.max.X - bb.min.X, bb.max.Y - bb.min.Y, bb.max.Z - bb.min.Z)
    print(f"block size: {size[0]:.2f} x {size[1]:.2f} x {size[2]:.2f} mm")
    if STUDY:
        fails = []
        print("band-battery study, contract not checked")
    else:
        fails = check_exterior(outer)
        print("check_exterior:", fails)
        if fails:
            print("exterior.py: contract check failed, exit 1")
            sys.exit(1)

    skin_body = body
    for slot, _ in mics:
        skin_body = skin_body - slot
    for p in pads:
        skin_body = skin_body - p
    if JOY_KIND == "round":
        to_y = Rot(-90, 0, 0)
        joy = Pos(JOY_X, wall_y, CTRL_Z) * to_y * Cylinder(JOY_L / 2, JOY_PROUD, align=(Align.CENTER, Align.CENTER, Align.MIN))
        joy = fillet(joy.edges().sort_by(Axis.Y)[-1:], JOY_EDGE_R)
    else:
        joy = pill(JOY_L, JOY_H, JOY_PROUD, JOY_X, CTRL_Z, wall_y)
    btn = pill(BTN_L, BTN_H, BTN_PROUD, BTN_X, CTRL_Z, wall_y)
    screen = Pos(SCREEN_CX, SCREEN_CY, BZ) * Box(LIT_X, LIT_Y, SCREEN_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    light = Pos(LIGHT_X, LIGHT_Y, BZ) * Cylinder(LIGHT_D / 2, LIGHT_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # band: ring around the finger, its top merged into the block (clipped flat at the block underside)
    ri = BAND_ID / 2
    zc = -FINGER_GAP - ri
    ring = (Pos(0, 0, zc) * Rot(0, 90, 0) * Cylinder(ri + BAND_WALL, BAND_W)) - (Pos(0, 0, zc) * Rot(0, 90, 0) * Cylinder(ri, BAND_W + 1))
    if BAND_EDGE > 0:
        ring = fillet(ring.edges(), BAND_EDGE)
    band = ring & Pos(0, 0, BAND_TOP - 40) * Box(60, 60, 40, align=(Align.CENTER, Align.CENTER, Align.MIN))
    contacts = Compound([Pos(PAD_XPOS, y, 0) * Cylinder(PAD_D / 2, PAD_SINK, align=(Align.CENTER, Align.CENTER, Align.MIN)) for y in PAD_YS])

    parts = {"body": skin_body, "glass": glass, "screen": screen, "band": band, "joystick": joy,
             "button": btn, "light": light, "mic_1": mics[0][1], "mic_2": mics[1][1], "contacts": contacts}
    rep = {"variant": VARIANT, "block_size": [round(v, 3) for v in size], "check_exterior": fails}
    for n, s in parts.items():
        b = s.bounding_box()
        rep[n] = {"volume": round(s.volume, 4), "min": [round(b.min.X, 3), round(b.min.Y, 3), round(b.min.Z, 3)],
                  "max": [round(b.max.X, 3), round(b.max.Y, 3), round(b.max.Z, 3)]}
    rep["mic_open_area_mm2"] = [round(m[1].volume / MIC_MESH_T, 3) for m in mics]
    json.dump(rep, open(OUT + "/measures-%s.json" % VARIANT, "w"), indent=1)
    if not STUDY:
        json.dump(rep, open(OUT + "/measures.json", "w"), indent=1)
        export_look(parts, OUT)
    export_look(parts, OUT, name="ring-" + VARIANT)
    print("exported: ring-%s.glb, ring-%s.step" % (VARIANT, VARIANT))
    print("exterior.py: done, exit 0")


# ================= merged32: block and band as one sculpted body =================
M = dict(BX=29.3, BY=14.75, H=3.2, R=2.5, TOP_R=0.9, BOT_R=1.2, GLASS=0.5,
         BW=8.0, WALL=2.6, EDGE=1.0, BORE_GAP=0.4, JUNC_R=4.0,
         SHOULDER_T=3.6, PHI_FULL=61.0, PHI_END=85.0, EDGE_ZONE=0.4,   # motor shoulders: 3.6 thick (19 to 61 degrees), easing to 2.6 by 85; edge rounding 0.4 there, 1.0 elsewhere
         JOY_DEG=38.0, JOY_CAP_D=4.6, JOY_BASE_D=5.6, JOY_PROUD=0.7, JOY_BASE_PROUD=0.15, JOY_DISH=0.25,
         BTN_DEG=62.0, BTN_L=5.0, BTN_W=3.0, BTN_PROUD=0.4, BTN_EDGE=0.3,
         MIC=(1.2, 0.3, 0.3, 1.7), PAD_D=1.0, PAD_XS=(-2.4, -0.8, 0.8, 2.4))


def build_merged():
    import math
    from build123d import Sphere, Vector, Vertex, Spline, ThreePointArc, BuildSketch, BuildLine, make_face, GeomType
    BXm, BYm, Hm = M["BX"], M["BY"], M["H"]
    ri = BAND_ID / 2
    R0 = ri + M["WALL"]                            # band outer radius, plain wall
    R1 = ri + M["SHOULDER_T"]                      # outer radius over the shoulders (vibration motor)
    zc = -M["BORE_GAP"] - ri                       # band axis; block underside is Z 0
    block = Pos(0, 0, Hm / 2) * Box(BXm, BYm, Hm)
    block = fillet(block.edges().filter_by(Axis.Z), M["R"])
    block = fillet(block.edges().filter_by(Plane.XY).group_by(Axis.Z)[0], M["BOT_R"])
    block = fillet(block.edges().filter_by(Plane.XY).group_by(Axis.Z)[-1], M["TOP_R"])

    def pt(r, deg):                                 # (y, z) of the point at `deg` from the top toward +Y
        a = math.radians(deg)
        return (r * math.sin(a), zc + r * math.cos(a))

    def tan(deg):                                   # unit tangent for rising angle
        a = math.radians(deg)
        return (math.cos(a), -math.sin(a))
    pf, pe = M["PHI_FULL"], M["PHI_END"]
    # band outline in the YZ plane, constant along X: radius R1 up to pf degrees from the top, easing to R0 by pe degrees
    with BuildSketch(Plane.YZ) as sk:
        with BuildLine():
            ThreePointArc(pt(R1, -pf), pt(R1, 0), pt(R1, pf))
            Spline(pt(R1, pf), pt(R0, pe), tangents=(tan(pf), tan(pe)))
            ThreePointArc(pt(R0, pe), pt(R0, 180), pt(R0, 360 - pe))
            Spline(pt(R0, 360 - pe), pt(R1, 360 - pf), tangents=(tan(360 - pe), tan(360 - pf)))
        make_face()
    env = extrude(sk.sketch, amount=M["BW"] / 2, both=True)
    # outer edges rounded: 0.4 over the shoulder zone, easing to 1.0 by pe degrees (variable-radius fillet along each edge)
    from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
    from build123d import Solid

    def phi_of(p):
        return abs(math.degrees(math.atan2(p.Y, p.Z - zc)))

    def rr(phi):
        if phi <= pf + 0.5:
            return M["EDGE_ZONE"]
        if phi >= pe - 0.5:
            return M["EDGE"]
        return M["EDGE_ZONE"] + (M["EDGE"] - M["EDGE_ZONE"]) * (phi - pf) / (pe - pf)
    mk = BRepFilletAPI_MakeFillet(env.wrapped)
    for e in env.edges():
        if e.geom_type == GeomType.LINE:
            continue
        mk.Add(rr(phi_of(e @ 0)), rr(phi_of(e @ 1)), e.wrapped)
    mk.Build()
    env = Solid(mk.Shape())
    print("variable edge rounding built, valid:", env.is_valid)
    fused = block + env

    def dist(shape, p):
        v = Vertex(p.X, p.Y, p.Z)
        return min(f.distance_to(v) for f in shape.faces())
    junc = [e for e in fused.edges() if all(dist(block, e @ t) < 2e-3 and dist(env, e @ t) < 2e-3 for t in (0.25, 0.5, 0.75))]
    reached = None
    for r in (4.0, 3.5, 3.0, 2.5):
        try:
            cand = fillet(junc, r)
            if cand.is_valid:
                fused, reached = cand, r
                break
        except Exception as ex:
            print(f"junction fillet {r} failed")
    print(f"junction edges {len(junc)}, junction fillet reached {reached}")
    if reached is None:
        print("exterior.py: junction fillet failed down to 2.5, exit 1")
        sys.exit(1)
    fused = fused - (Pos(0, 0, zc) * Rot(0, 90, 0) * Cylinder(ri, 60))   # bore, unbroken under the block

    def thick(deg, x=0.0, side=-1):
        """radial wall thickness from the bore at `deg` from the top (side -1 = -Y shoulder), at X = x"""
        a = math.radians(deg)
        n = 0
        r = ri + 0.005
        while r < ri + 6:
            p = Vector(x, side * r * math.sin(a), zc + r * math.cos(a))
            if not fused.is_inside(p):
                break
            r += 0.005
        return round(r - ri, 3)
    zone = [thick(d, x, sd) for d in (19, 25, 31, 38, 45, 51, 61) for x in (-4, -2, 0, 2, 4) for sd in (-1, 1)]
    prof = {d: thick(d) for d in (0, 19, 38, 61, 70, 85, 120, 180)}
    print("shoulder thickness at 38 degrees (X 0, -Y side):", thick(38), "mm")
    core = [thick(d, x, sd) for d in (19, 25, 31, 38, 45, 49, 55, 61) for x in (-3.6, -1.8, 0, 1.8, 3.6) for sd in (-1, 1)]
    print("shoulder zone 19..61 degrees, X -3.6..3.6, both sides: min %.3f max %.3f" % (min(core), max(core)))
    print("shoulder zone 19..57 degrees, X -4..4 (to the band edge), both sides: min %.3f max %.3f" % (min(zone), max(zone)))
    print("thickness by angle from the top (X 0, -Y side):", prof)
    return fused, dict(zc=zc, ro=R0, ri=ri, junction_fillet=reached, junction_edges=len(junc), shoulder_t_38=thick(38),
                       shoulder_zone_min_x36=min(core), shoulder_zone_min_x4=min(zone), thickness_by_angle=prof)


def main_merged():
    import math
    fused, info = build_merged()
    zc, ro = info["zc"], info["ro"]
    Hm, BXm, BYm = M["H"], M["BX"], M["BY"]
    wall_y = BYm / 2
    zsplit = Hm - M["GLASS"]
    # controls and slots on the walls
    ml, mh, md, mz = M["MIC"]
    mics = []
    for x in MIC_XS:
        slot = Pos(x, -wall_y + md / 2 - 0.5, mz) * Box(ml, md + 1.0, mh)
        slot = fillet(slot.edges().filter_by(Axis.Y), mh / 2 - 0.005)
        mesh = Pos(x, -wall_y + md - MIC_MESH_T / 2, mz) * Box(ml, MIC_MESH_T, mh)
        mesh = fillet(mesh.edges().filter_by(Axis.Y), mh / 2 - 0.005)
        mics.append((slot, mesh))
    for slot, _ in mics:
        fused = fused - slot
    # contact pads: thin curved pads flush with the band's outer surface at its lowest point
    pdepth = 0.1
    skin = (Pos(0, 0, zc) * Rot(0, 90, 0) * Cylinder(ro, 20)) - (Pos(0, 0, zc) * Rot(0, 90, 0) * Cylinder(ro - pdepth, 20))
    pads = []
    for x in M["PAD_XS"]:
        col = Pos(x, 0, zc - ro) * Cylinder(M["PAD_D"] / 2, 1.0, align=(Align.CENTER, Align.CENTER, Align.CENTER))
        pads.append(col & skin)
    contacts = Compound(pads)
    for p in pads:
        fused = fused - p
    # thumb stick and record button on the +Y (thumb side) shoulder of the band, normal to the surface
    import math
    ri, zc_ = info["ri"], zc

    def surf_r(deg, side=1, x=0.0):
        a = math.radians(deg)
        r = ri + 0.005
        while r < ri + 7:
            if not fused.is_inside(Vector(x, side * r * math.sin(a), zc_ + r * math.cos(a))):
                break
            r += 0.005
        return r

    def frame(deg):
        """point and outward normal of the +Y shoulder surface at `deg` from the top (X 0)"""
        a = math.radians(deg)
        rm, rp, r0 = surf_r(deg - 2), surf_r(deg + 2), surf_r(deg)
        drda = (rp - rm) / math.radians(4)
        rh = Vector(0, math.sin(a), math.cos(a))
        th = Vector(0, math.cos(a), -math.sin(a))
        n = (rh - th * (drda / r0)).normalized()
        P = Vector(0, r0 * math.sin(a), zc_ + r0 * math.cos(a))
        return P, n, r0
    JP, Jn, jr = frame(M["JOY_DEG"])
    BP, Bn, br = frame(M["BTN_DEG"])
    loc = lambda P, n: Plane(origin=(P.X, P.Y, P.Z), x_dir=(1, 0, 0), z_dir=(n.X, n.Y, n.Z))
    # joystick: base ring 5.6 across, 0.15 proud; cap 4.6 across, 0.7 proud, top edge rounded, 0.25 deep dish; both start 0.3 inside the shoulder
    base = Pos(0, 0, -0.3) * Cylinder(M["JOY_BASE_D"] / 2, 0.3 + M["JOY_BASE_PROUD"], align=(Align.CENTER, Align.CENTER, Align.MIN))
    cap = Pos(0, 0, -0.3) * Cylinder(M["JOY_CAP_D"] / 2, 0.3 + M["JOY_PROUD"], align=(Align.CENTER, Align.CENTER, Align.MIN))
    cap = fillet(cap.edges().group_by(Axis.Z)[-1], 0.2)
    dd, dr = M["JOY_DISH"], 1.8                       # dish depth, dish half width
    sph_r = (dr ** 2 + dd ** 2) / (2 * dd)
    cap = cap - Pos(0, 0, M["JOY_PROUD"] - dd + sph_r) * Sphere(sph_r)
    joy = loc(JP, Jn) * (base + cap)
    bl, bw, bproud = M["BTN_L"], M["BTN_W"], M["BTN_PROUD"]
    pill_b = Pos(0, 0, (bproud - 0.3) / 2) * Box(bl, bw, bproud + 0.3)
    pill_b = fillet(pill_b.edges().filter_by(Axis.Z), bw / 2 - 0.005)
    pill_b = fillet(pill_b.edges().group_by(Axis.Z)[-1], M["BTN_EDGE"])
    btn = loc(BP, Bn) * pill_b
    gap = joy.distance_to(btn)
    print("thumb stick at %d deg: surface radius %.3f, normal (%.3f, %.3f, %.3f)" % (M["JOY_DEG"], jr, Jn.X, Jn.Y, Jn.Z))
    print("record button at %d deg: surface radius %.3f" % (M["BTN_DEG"], br))
    print("plain band between joystick base and button: %.3f mm (asked: at least 1.0)" % gap)
    print("shoulder thickness under the stick (X 0, +Y side): %.3f mm" % (jr - ri))
    # glass = top 0.5 mm slice of the same solid; body = the rest
    cut = Pos(0, 0, zsplit + 20) * Box(80, 80, 40)
    glass = fused & cut
    body = fused - cut
    bb = (body + glass).bounding_box()
    blk = Pos(0, 0, Hm / 2) * Box(BXm, BYm, Hm)
    bbb = (fused & Pos(0, 0, 0) * Box(60, 60, Hm + 0.001, align=(Align.CENTER, Align.CENTER, Align.MIN))).bounding_box()
    print(f"block size: {BXm:.2f} x {BYm:.2f} x {Hm:.2f} mm")
    print("sculpt study, contract not checked")
    print("block bounding box (above Z 0): X %.3f..%.3f  Y %.3f..%.3f  Z %.3f..%.3f" % (bbb.min.X, bbb.max.X, bbb.min.Y, bbb.max.Y, bbb.min.Z, bbb.max.Z))
    print("whole bounding box: X %.3f..%.3f  Y %.3f..%.3f  Z %.3f..%.3f" % (bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z, bb.max.Z))
    screen = Pos(SCREEN_CX, SCREEN_CY, Hm) * Box(LIT_X, LIT_Y, SCREEN_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    light = Pos(LIGHT_X, LIGHT_Y, Hm) * Cylinder(LIGHT_D / 2, LIGHT_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # the band is one body with the block; `band` is a tiny solid hidden in the band wall so no seam is cut
    hidden = Pos(0, 0, zc - ro + M["WALL"] / 2) * Box(0.4, 0.4, 0.4)
    parts = {"body": body, "glass": glass, "screen": screen, "band": hidden, "joystick": joy,
             "button": btn, "light": light, "mic_1": mics[0][1], "mic_2": mics[1][1], "contacts": contacts}
    rep = {"variant": VARIANT, "block_size": [BXm, BYm, Hm], "info": info, "block_bbox_above_z0": [round(v, 3) for v in (bbb.min.X, bbb.min.Y, bbb.min.Z, bbb.max.X, bbb.max.Y, bbb.max.Z)]}
    for n, s in parts.items():
        b = s.bounding_box()
        rep[n] = {"volume": round(s.volume, 4), "min": [round(b.min.X, 3), round(b.min.Y, 3), round(b.min.Z, 3)],
                  "max": [round(b.max.X, 3), round(b.max.Y, 3), round(b.max.Z, 3)]}
    json.dump(rep, open(OUT + "/measures-%s.json" % VARIANT, "w"), indent=1)
    export_look(parts, OUT, name="ring-" + VARIANT)
    print("exported: ring-%s.glb, ring-%s.step" % (VARIANT, VARIANT))
    print("exterior.py: done, exit 0")


# ================= merged32b: curved glass over both long edges, controls on the side of the band =================
B = dict(BX=29.3, BY=14.75, H=3.45, R=2.5, BOT_R=1.2, LONG_R=2.0, END_R=1.2, GLASS_Z=2.75,
         BW=8.0, WALL=2.6, SHOULDER_T=3.6, PHI_FULL=61.0, PHI_END=85.0, EDGE_ZONE=0.4, EDGE=1.0, BORE_GAP=0.4, JUNC_R=4.0,
         JOY_DEG=95.0, JOY_T=3.6, JOY_FLAT0=80.0, JOY_FLAT1=110.0, JOY_EASE=12.0,
         FRAME_ARC=6.4, FRAME_X=5.4, FRAME_R=1.2, FRAME_PROUD=0.5, NUB_ARC=4.6, NUB_X=3.6, NUB_R=1.0, NUB_PROUD=0.9, NUB_DOME=0.15,
         BTN_DEG=62.0, BTN_L=4.4, BTN_W=2.4, BTN_PROUD=0.35, BTN_EDGE=0.3,
         MIC=(1.2, 0.3, 0.3, 1.4), PAD_D=1.0, PAD_XS=(-2.4, -0.8, 0.8, 2.4))


def build_merged_b():
    import math
    from build123d import Vector, Vertex, Spline, ThreePointArc, BuildSketch, BuildLine, make_face, GeomType, Solid
    from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
    BXm, BYm, Hm = B["BX"], B["BY"], B["H"]
    ri = BAND_ID / 2
    R0 = ri + B["WALL"]
    R1 = ri + B["SHOULDER_T"]
    zc = -B["BORE_GAP"] - ri
    # ---- block: flat top at Hm, quarter-round LONG_R on both long sides, END_R at the ends, bottom roll BOT_R
    block = Pos(0, 0, Hm / 2) * Box(BXm, BYm, Hm)
    block = fillet(block.edges().filter_by(Axis.Z), B["R"])
    block = fillet(block.edges().filter_by(Plane.XY).group_by(Axis.Z)[0], B["BOT_R"])
    mk = BRepFilletAPI_MakeFillet(block.wrapped)
    for e in block.edges().filter_by(Plane.XY).group_by(Axis.Z)[-1]:
        def rad_at(p):
            return B["LONG_R"] if abs(p.Y) > BYm / 2 - 0.2 else B["END_R"]
        mk.Add(rad_at(e @ 0), rad_at(e @ 1), e.wrapped)
    mk.Build()
    block = Solid(mk.Shape())
    print("block with curved top built, valid:", block.is_valid)
    # ---- band outline in the YZ plane, constant along X; radius R1 over the shoulders and the thumb zone, R0 elsewhere
    def sm(t):
        t = min(1.0, max(0.0, t))
        return t * t * (3 - 2 * t)
    pf, pe = B["PHI_FULL"], B["PHI_END"]

    def Rphi(phi):
        d = min(phi, 360 - phi)
        sh = 1.0 if d <= pf else 1.0 - sm((d - pf) / (pe - pf))
        j = 0.0
        if phi <= 180:
            f0, f1, e = B["JOY_FLAT0"], B["JOY_FLAT1"], B["JOY_EASE"]
            j = 1.0 if f0 <= phi <= f1 else (sm((phi - (f0 - e)) / e) if phi < f0 else 1.0 - sm((phi - f1) / e))
        return R0 + (R1 - R0) * (1 - (1 - sh) * (1 - j))

    def pt(r, deg):
        a = math.radians(deg)
        return (r * math.sin(a), zc + r * math.cos(a))

    def tan(deg):
        a = math.radians(deg)
        return (math.cos(a), -math.sin(a))
    p_end = B["JOY_FLAT1"] + B["JOY_EASE"]          # 122
    with BuildSketch(Plane.YZ.offset(-B["BW"] / 2)) as sk:
        with BuildLine():
            ThreePointArc(pt(R1, -pf), pt(R1, 0), pt(R1, pf))
            pts = [pt(Rphi(d), d) for d in [pf + 3.0 * i for i in range(int((p_end - pf) / 3.0) + 1)] + [p_end]]
            ded = []
            for q in pts:                              # drop duplicate points
                if not ded or abs(q[0] - ded[-1][0]) + abs(q[1] - ded[-1][1]) > 1e-6:
                    ded.append(q)
            Spline(ded)                                 # no end tangents: explicit ones make a tiny cusp that breaks the fillet
            ThreePointArc(pt(R0, p_end), pt(R0, 180), pt(R0, 360 - pe))
            Spline(pt(R0, 360 - pe), pt(R1, 360 - pf), tangents=(tan(360 - pe), tan(360 - pf)))
        make_face()
    env = extrude(sk.sketch, amount=B["BW"])
    if os.environ.get("ENV_ONLY"):
        print("sketch edges:", [(e.geom_type.name, round(e.length, 2), tuple(round(v, 2) for v in tuple(e @ 0)), tuple(round(v, 2) for v in tuple(e @ 1))) for e in sk.sketch.edges()])
        print("sketch face area", round(sk.sketch.area, 2), "n faces", len(sk.sketch.faces()))
        return env

    def phi_of(p):
        return math.degrees(math.atan2(p.Y, p.Z - zc)) % 360

    def rr(phi):
        if phi >= 298.5 or phi <= 61.5:
            return B["EDGE_ZONE"]
        return B["EDGE"]
    mk = BRepFilletAPI_MakeFillet(env.wrapped)
    for e in env.edges():
        if e.geom_type == GeomType.LINE or abs((e @ 0.5).X) < B["BW"] / 2 - 0.1:   # skip lateral lines and the x=0 seam loop of the two-way extrusion
            continue
        r_a, r_b = rr(phi_of(e @ 0)), rr(phi_of(e @ 1))
        if os.environ.get("EDGE_MODE") != "var":   # CHOSEN: constant 0.4 (a 0.4 to 1.0 variable rounding gives an invalid solid)
            r_a = r_b = B["EDGE_ZONE"]
        mk.Add(r_a, r_b, e.wrapped)
    mk.Build()
    env = Solid(mk.Shape())
    print("variable edge rounding built, valid:", env.is_valid)
    fused = block + env

    def dist(shape, p):
        v = Vertex(p.X, p.Y, p.Z)
        return min(f.distance_to(v) for f in shape.faces())
    junc = [e for e in fused.edges() if all(dist(block, e @ t) < 2e-3 and dist(env, e @ t) < 2e-3 for t in (0.25, 0.5, 0.75))]
    reached = None
    for r in (4.0, 3.5, 3.0, 2.5):
        try:
            cand = fillet(junc, r)
            if cand.is_valid:
                fused, reached = cand, r
                break
        except Exception:
            print(f"junction fillet {r} failed")
    print(f"junction edges {len(junc)}, junction fillet reached {reached}")
    if reached is None:
        print("exterior.py: junction fillet failed down to 2.5, exit 1")
        sys.exit(1)
    fused = fused - (Pos(0, 0, zc) * Rot(0, 90, 0) * Cylinder(ri, 60))

    def surf_r(deg, side=1, x=0.0, step=0.05):
        a = math.radians(deg)
        r = ri + 0.01
        while r < ri + 8:
            if not fused.is_inside(Vector(x, side * r * math.sin(a), zc + r * math.cos(a))):
                break
            r += step
        r -= step
        while r < ri + 8:
            r += 0.005
            if not fused.is_inside(Vector(x, side * r * math.sin(a), zc + r * math.cos(a))):
                break
        return r
    return fused, dict(zc=zc, ri=ri, R0=R0, junction_fillet=reached, junction_edges=len(junc)), surf_r


def main_merged_b():
    import math
    fused, info, surf_r = build_merged_b()
    zc, ri = info["zc"], info["ri"]
    Hm, BXm, BYm = B["H"], B["BX"], B["BY"]
    wall_y = BYm / 2
    ml, mh, md, mz = B["MIC"]
    mics = []
    for x in MIC_XS:
        slot = Pos(x, -wall_y + md / 2 - 0.5, mz) * Box(ml, md + 1.0, mh)
        slot = fillet(slot.edges().filter_by(Axis.Y), mh / 2 - 0.005)
        mesh = Pos(x, -wall_y + md - MIC_MESH_T / 2, mz) * Box(ml, MIC_MESH_T, mh)
        mesh = fillet(mesh.edges().filter_by(Axis.Y), mh / 2 - 0.005)
        mics.append((slot, mesh))
    for slot, _ in mics:
        fused = fused - slot
    ro = info["R0"]
    skin = (Pos(0, 0, zc) * Rot(0, 90, 0) * Cylinder(ro, 20)) - (Pos(0, 0, zc) * Rot(0, 90, 0) * Cylinder(ro - 0.1, 20))
    pads = [(Pos(x, 0, zc - ro) * Cylinder(B["PAD_D"] / 2, 1.0)) & skin for x in B["PAD_XS"]]
    contacts = Compound(pads)
    for p in pads:
        fused = fused - p

    def frame(deg):
        a = math.radians(deg)
        rm, rp, r0 = surf_r(deg - 2), surf_r(deg + 2), surf_r(deg)
        drda = (rp - rm) / math.radians(4)
        rh = Vector(0, math.sin(a), math.cos(a))
        th = Vector(0, math.cos(a), -math.sin(a))
        n = (rh - th * (drda / r0)).normalized()
        return Vector(0, r0 * math.sin(a), zc + r0 * math.cos(a)), n, r0
    JP, Jn, jr = frame(B["JOY_DEG"])
    BP, Bn, br = frame(B["BTN_DEG"])
    # local frame: Z along the surface normal, X along the band axis, Y along the arc
    loc = lambda P, n: Plane(origin=(P.X, P.Y, P.Z), x_dir=(1, 0, 0), z_dir=(n.X, n.Y, n.Z))

    def rrect_solid(lx, ly, z0, z1, r):
        sk2 = extrude(RectangleRounded(lx, ly, r), amount=z1 - z0)
        return Pos(0, 0, z0) * sk2
    # raised frame (6.4 along the arc x 5.4 along X, r 1.2) 0.5 proud, nub (4.6 x 3.6, r 1.0) 0.9 proud of the frame, slightly domed
    frame_s = rrect_solid(B["FRAME_X"], B["FRAME_ARC"], -0.3, B["FRAME_PROUD"], B["FRAME_R"])
    top = B["FRAME_PROUD"] + B["NUB_PROUD"]
    nub = rrect_solid(B["NUB_X"], B["NUB_ARC"], B["FRAME_PROUD"] - 0.2, top, B["NUB_R"])
    dome_h = B["NUB_DOME"]
    dome_r = ((B["NUB_ARC"] / 2) ** 2 + dome_h ** 2) / (2 * dome_h)
    nub = nub & (Pos(0, 0, top - dome_h - dome_r) * Sphere(dome_r + dome_h) if False else Pos(0, 0, top - dome_r) * Sphere(dome_r))
    joy = loc(JP, Jn) * (frame_s + nub)
    pill_b = Pos(0, 0, (B["BTN_PROUD"] - 0.3) / 2) * Box(B["BTN_L"], B["BTN_W"], B["BTN_PROUD"] + 0.3)
    pill_b = fillet(pill_b.edges().filter_by(Axis.Z), B["BTN_W"] / 2 - 0.005)
    pill_b = fillet(pill_b.edges().group_by(Axis.Z)[-1], B["BTN_EDGE"])
    btn = loc(BP, Bn) * pill_b
    gap = joy.distance_to(btn)
    print("joystick at %d deg: surface radius %.3f, normal (%.3f, %.3f, %.3f)" % (B["JOY_DEG"], jr, Jn.X, Jn.Y, Jn.Z))
    print("measured band thickness at 95 degrees (X 0, +Y side): %.3f mm" % (jr - ri))
    print("record button at %d deg: surface radius %.3f; plain band between button and joystick frame: %.3f mm (asked: at least 1.0)" % (B["BTN_DEG"], br, gap))
    t38 = surf_r(38) - ri
    t_m38 = surf_r(38, side=-1) - ri
    print("shoulder thickness at 38 degrees: +Y %.3f mm, -Y %.3f mm" % (t38, t_m38))
    # glass = everything above Z 2.75 inside the plan outline; body = the rest
    cut = Pos(0, 0, B["GLASS_Z"] + 20) * Box(80, 80, 40)
    glass = fused & cut
    body = fused - cut
    bbf = fused.bounding_box()
    bbb = (fused & (Pos(0, 0, 0) * Box(60, 60, Hm + 0.001, align=(Align.CENTER, Align.CENTER, Align.MIN)))).bounding_box()
    print(f"block size: {BXm:.2f} x {BYm:.2f} x {Hm:.2f} mm")
    print("sculpt study, contract not checked")
    print("block bounding box (above Z 0): X %.3f..%.3f  Y %.3f..%.3f  Z %.3f..%.3f" % (bbb.min.X, bbb.max.X, bbb.min.Y, bbb.max.Y, bbb.min.Z, bbb.max.Z))
    print("whole bounding box: X %.3f..%.3f  Y %.3f..%.3f  Z %.3f..%.3f" % (bbf.min.X, bbf.max.X, bbf.min.Y, bbf.max.Y, bbf.min.Z, bbf.max.Z))
    screen = Pos(SCREEN_CX, SCREEN_CY, Hm) * Box(LIT_X, LIT_Y, SCREEN_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    light = Pos(LIGHT_X, LIGHT_Y, Hm) * Cylinder(LIGHT_D / 2, LIGHT_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    hidden = Pos(0, 0, zc - ro + B["WALL"] / 2) * Box(0.4, 0.4, 0.4)
    parts = {"body": body, "glass": glass, "screen": screen, "band": hidden, "joystick": joy,
             "button": btn, "light": light, "mic_1": mics[0][1], "mic_2": mics[1][1], "contacts": contacts}
    rep = {"variant": VARIANT, "block_size": [BXm, BYm, Hm], "info": info, "joystick_thickness_95": round(jr - ri, 3),
           "block_bbox_above_z0": [round(v, 3) for v in (bbb.min.X, bbb.min.Y, bbb.min.Z, bbb.max.X, bbb.max.Y, bbb.max.Z)]}
    for n, s in parts.items():
        b = s.bounding_box()
        rep[n] = {"volume": round(s.volume, 4), "min": [round(b.min.X, 3), round(b.min.Y, 3), round(b.min.Z, 3)],
                  "max": [round(b.max.X, 3), round(b.max.Y, 3), round(b.max.Z, 3)]}
    json.dump(rep, open(OUT + "/measures-%s.json" % VARIANT, "w"), indent=1)
    # own export with a finer tessellation than export_look, so the long rolled edges stay smooth
    from build123d import export_gltf, export_step
    kids = []
    for n in PART_NAMES:
        parts[n].label = n
        kids.append(parts[n])
    asm = Compound(label="ring-" + VARIANT, children=kids)
    export_gltf(asm, os.path.join(OUT, "ring-%s.glb" % VARIANT), binary=True, linear_deflection=0.003, angular_deflection=0.05)
    export_step(asm, os.path.join(OUT, "ring-%s.step" % VARIANT))
    print("exported: ring-%s.glb, ring-%s.step" % (VARIANT, VARIANT))
    print("exterior.py: done, exit 0")


# ================= merged32c: the whole glass face is one arc across Y; joystick at the bottom of the band =================
C = dict(BX=29.3, BY=14.75, R=2.5, BOT_R=1.2, SIDE_R=1.0, END_R=1.2, ARC_R=30.7, TOP_Z=3.85, GLASS_Z=2.75,
         BW=8.0, WALL=2.6, SHOULDER_T=3.6, PHI_FULL=61.0, PHI_END=85.0, EDGE=0.4, BORE_GAP=0.4, JUNC_R=4.0,
         JOY_DEG=150.0, JOY_FLAT0=135.0, JOY_FLAT1=165.0, JOY_EASE=12.0,
         FRAME_ARC=6.4, FRAME_X=5.4, FRAME_R=1.2, FRAME_PROUD=0.5, NUB_ARC=4.6, NUB_X=3.6, NUB_R=1.0, NUB_PROUD=0.9, NUB_DOME=0.15,
         BTN_DEG=88.0, BTN_L=4.4, BTN_W=2.4, BTN_PROUD=0.35, BTN_EDGE=0.3,
         PAD_DEG=150.0, MIC=(1.2, 0.3, 0.3, 1.4), PAD_D=1.0, PAD_XS=(-2.4, -0.8, 0.8, 2.4))


JOY_SIDE, BTN_SIDE = 1, 1
# merged32f only (lead's rulings of 2026-11-11):
#  joystick opening = the exterior's own frame (FRAME_X 6.4 along X, FRAME_ARC 5.4 along the band) + 0.2 on each dimension;
#  light window from the light-path helper (provisional parameters: X -12.425, Y -2.95, round 0.4);
#  microphones: no wall slot; underside hole 1.0 through the floor (Z 0.10 to 0.30) with a coaxial seat 2.0 x 0.10 deep
#  (design/mech/mic-path/mic-path.md section 5 pieces 4, 5, 7 and section 9 item 25) at X -11.77 and +11.77, Y -4.8
# merged32h only (lead's ruling 2026-11-11): round opening, round frame, round textured cap 0.5 more proud
H32 = dict(OPEN_D=5.6, FRAME_D=5.4, CAP_D=4.4, CAP_EXTRA=0.5, EDGE_R=0.3, DISH=0.25, RIDGE_RS=(0.7, 1.3, 1.9), RIDGE_W=0.25, RIDGE_H=0.08)
F32 = dict(OPEN_X=6.4 + 0.2, OPEN_T=5.4 + 0.2, LIGHT_X=-12.425, LIGHT_Y=-2.95, LIGHT_D=0.4,
           MIC_XS=(-11.77, 11.77), MIC_Y=-4.8, HOLE_D=1.0, HOLE_Z1=0.30, SEAT_D=2.0, SEAT_T=0.10)
F_LIKE = KIND in ("merged32f", "merged32g", "merged32h", "merged417", "merged417flat")   # merged32g = merged32f + joystick angle per size
NO_BTN = KIND in ("merged32e", "merged32f", "merged32g", "merged32h", "merged417", "merged417flat")      # one control: no record button, no outside pads (pads move inside the band)
H_LIKE = KIND in ("merged32h", "merged417", "merged417flat")   # merged417 takes every merged32h branch (round textured joystick, no light)
# merged417 only (owner card 2026-11-13 "4.17 mm, stock screen with connector"; design/wiring/screen-cable-study.md section 4.3
# item 1, "Block height +0.970 mm (3.20 to 4.17)"): the connector J1 stands between the board and the panel, so the
# finger-side face, the band and the plan stay; the glass, its seat (GLASS_Z) and the top (TOP_Z) rise by LIFT417.
LIFT417 = 0.970 if KIND in ("merged417", "merged417flat") else 0.0
# merged417flat (owner option, lead 2026-11-13): the lowest crown the glass allows with the same seat. Rule kept: the glass is at
# least as thick over the screen panel's long edge (Y +-PANEL_Y/2 = 6.4, envelope_slim.py) as in merged417 (0.42 there, cover-glass.md
# line 29). The lowest top through that height is flat: TOP_Z = merged417 TOP_Z minus the arc's drop at Y 6.4.
FLAT417 = KIND == "merged417flat"
if KIND in ("merged32d1", "merged32d2", "merged32e", "merged32f", "merged32g", "merged32h", "merged417", "merged417flat"):
    # owner's red rectangle: joystick on the OUTER face of the -Y side, 78 degrees from the top, nub long side (4.6) along the finger
    C.update(JOY_DEG=78.0, JOY_FLAT0=63.0, JOY_FLAT1=93.0, NUB_ARC=3.6, NUB_X=4.6, FRAME_ARC=5.4, FRAME_X=6.4)
    JOY_SIDE = -1
    if KIND in ("merged32d1", "merged32e", "merged32f", "merged32g", "merged32h", "merged417", "merged417flat"):
        C.update(BTN_DEG=42.0)
        BTN_SIDE = -1
# merged32g: joystick centre angle per US size (architecture.md 17.25): US 7 84.0, US 8 81.0, US 9 to 13 78 degrees on the
# joystick side. Only the joystick solid and its opening follow C["JOY_DEG"]; the band outline keeps JOY_FLAT0 63 / JOY_FLAT1 93.
G32_JOY_DEG = {7: 84.0, 8: 81.0, 9: 78.0, 10: 78.0, 11: 78.0, 12: 78.0, 13: 78.0}
if KIND in ("merged32g", "merged32h", "merged417", "merged417flat"):
    C["JOY_DEG"] = G32_JOY_DEG[SIZE if SIZE else 9]
    # lead's ruling 2026-11-11: the thick zone (hump) moves with the joystick on US 7 and US 8, same shape as merged32f at
    # US 9 (flat 63 to 93 = 78 +- 15, ease 12). G32_ZONE "deg" keeps the widths in degrees, "mm" keeps them in mm along the
    # surface (scaled by the US 9 outer radius over this size's outer radius). US 9 to 13 stay exactly as merged32f.
    # chosen: "mm" (out/work-32g/zone-try2-*.log: with "mm" the metal toward the bottom at 0.1 is 1.089 on US 7 and US 8,
    # the same as US 9; with "deg" it is 0.839 and 0.964). G32_ZONE=deg in the environment rebuilds the other reading.
    G32_ZONE = os.environ.get("G32_ZONE", "mm")
    if C["JOY_DEG"] != 78.0:
        k = 1.0
        if G32_ZONE == "mm":
            k = (18.95 / 2 + C["SHOULDER_T"]) / (BAND_ID / 2 + C["SHOULDER_T"])
        half, ease = 15.0 * k, 12.0 * k
        C.update(JOY_FLAT0=C["JOY_DEG"] - half, JOY_FLAT1=C["JOY_DEG"] + half, JOY_EASE=ease)
        print("merged32g thick zone (%s): flat %.3f to %.3f deg, ease %.3f deg, so %.3f to %.3f deg with the ease"
              % (G32_ZONE, C["JOY_FLAT0"], C["JOY_FLAT1"], ease, C["JOY_FLAT0"] - ease, C["JOY_FLAT1"] + ease))
if LIFT417:
    # every radius stays as merged32h (ARC_R 30.7, SIDE_R 1.0, END_R 1.2, BOT_R 1.2, R 2.5, junction 4.0): the reasons are in
    # design/look/s1/merged417-notes.md. Only the heights above the board change.
    C["TOP_Z_32H"] = C["TOP_Z"]                         # merged32h's top: its block, band and blend are made at this height first
    C.update(TOP_Z=C["TOP_Z"] + LIFT417, GLASS_Z=C["GLASS_Z"] + LIFT417)
    print("merged417: top %.3f at the centre line, glass seat (body top) %.3f, both %.3f above merged32h" % (C["TOP_Z"], C["GLASS_Z"], LIFT417))
if FLAT417:
    import math as _m
    from envelope_slim import PANEL_Y as _PY
    _drop = C["ARC_R"] - _m.sqrt(C["ARC_R"] ** 2 - (_PY / 2) ** 2)
    C.update(TOP_Z=C["TOP_Z"] - _drop)
    # lead's ruling 2026-11-13 (replaces "the rounded long edges (1.0) and ends (1.2) stay" for the flat glass): the top's long
    # edges and ends are rolled 0.42, so the whole roll lies in the glass edge above the seat and the wall under the seat keeps
    # the plan thickness; the plan corner 2.5 stays
    C["ROLL_FLAT"] = 0.42
    print("merged417flat: flat top at %.4f (merged417 top minus the arc drop %.4f at Y %.2f); glass %.4f thick there and at the centre"
          % (C["TOP_Z"], _drop, _PY / 2, C["TOP_Z"] - C["GLASS_Z"]))


def build_merged_c():
    import math
    from build123d import Vector, Vertex, Spline, ThreePointArc, BuildSketch, BuildLine, make_face, GeomType, Solid
    from OCP.BRepFilletAPI import BRepFilletAPI_MakeFillet
    BXc, BYc = C["BX"], C["BY"]
    ri = BAND_ID / 2
    R0 = ri + C["WALL"]
    R1 = ri + C["SHOULDER_T"]
    zc = -C["BORE_GAP"] - ri
    # ---- block: plan rounded rectangle, bottom roll, top face = a cylinder segment of radius ARC_R (axis along X)
    block = Pos(0, 0, 2.1) * Box(BXc, BYc, 4.2)
    block = fillet(block.edges().filter_by(Axis.Z), C["R"])
    block = fillet(block.edges().filter_by(Plane.XY).group_by(Axis.Z)[0], C["BOT_R"])
    tall = None
    if LIFT417:                                           # merged417: the tall block, the plan box 0.970 taller, same plan corners and bottom roll
        tall = Pos(0, 0, (4.2 + LIFT417) / 2) * Box(BXc, BYc, 4.2 + LIFT417)
        tall = fillet(tall.edges().filter_by(Axis.Z), C["R"])
        tall = fillet(tall.edges().filter_by(Plane.XY).group_by(Axis.Z)[0], C["BOT_R"])

    def top_shape(block, top_z, lift, flat):
        """the crown (arc of ARC_R through top_z, or flat at top_z) and the top rolls SIDE_R / END_R"""
        arc_axis_z = top_z - C["ARC_R"]
        if flat:                                          # flat top instead of the arc
            block = block & (Pos(0, 0, top_z) * Box(60, 60, 20, align=(Align.CENTER, Align.CENTER, Align.MAX)))
        else:
            block = block & (Pos(0, 0, arc_axis_z) * Rot(0, 90, 0) * Cylinder(C["ARC_R"], 40))
        top_edges = [e for e in block.edges() if (e @ 0.5).Z > 2.5 and e.geom_type != GeomType.LINE or ((e @ 0.5).Z > 2.5 and abs((e @ 0.5).Y) > BYc / 2 - 0.05)]
        if lift:                                          # merged417: the same edge pick 0.970 higher (the plan-corner seam lines now reach Z 3.9)
            zt = 2.5 + lift
            top_edges = [e for e in block.edges() if (e @ 0.5).Z > zt and e.geom_type != GeomType.LINE or ((e @ 0.5).Z > zt and abs((e @ 0.5).Y) > BYc / 2 - 0.05)]
            if flat:                                      # flat top: its end edges are straight lines too
                top_edges = [e for e in block.edges() if abs((e @ 0.5).Z - top_z) < 1e-6]
        mk = BRepFilletAPI_MakeFillet(block.wrapped)
        for e in top_edges:
            def rad_at(p):
                if flat and lift:                     # merged417flat (lead's ruling 2026-11-13): one roll radius ROLL_FLAT
                    return C["ROLL_FLAT"]
                return C["SIDE_R"] if abs(p.Y) > BYc / 2 - 0.2 else C["END_R"]
            mk.Add(rad_at(e @ 0), rad_at(e @ 1), e.wrapped)
        mk.Build()
        block = Solid(mk.Shape())
        print("block with curved face built, valid:", block.is_valid, " top edges rounded:", len(top_edges))
        return block
    block = top_shape(block, C.get("TOP_Z_32H", C["TOP_Z"]), 0.0, False)      # merged32h's block (for merged417 at merged32h's heights)
    if LIFT417:
        tall = top_shape(tall, C["TOP_Z"], LIFT417, FLAT417)
    # ---- band outline in the YZ plane (R1 over the shoulders and the thumb zone at the bottom)
    def sm(t):
        t = min(1.0, max(0.0, t))
        return t * t * (3 - 2 * t)
    pf, pe = C["PHI_FULL"], C["PHI_END"]
    f0, f1, ez = C["JOY_FLAT0"], C["JOY_FLAT1"], C["JOY_EASE"]

    def Rphi(phi):
        d = min(phi, 360 - phi)
        sh = 1.0 if d <= pf else 1.0 - sm((d - pf) / (pe - pf))
        j = 0.0
        if phi <= 180:
            j = 1.0 if f0 <= phi <= f1 else (sm((phi - (f0 - ez)) / ez) if phi < f0 else 1.0 - sm((phi - f1) / ez))
        return R0 + (R1 - R0) * (1 - (1 - sh) * (1 - j))

    def pt(r, deg):
        a = math.radians(deg)
        return (r * math.sin(a), zc + r * math.cos(a))

    def sampled(a0, a1, step=3.0):
        n = int(round((a1 - a0) / step))
        return [pt(Rphi(a0 + (a1 - a0) * i / n), a0 + (a1 - a0) * i / n) for i in range(n + 1)]
    j0, j1 = f0 - ez, f1 + ez                            # 123, 177
    with BuildSketch(Plane.YZ.offset(-C["BW"] / 2)) as sk:
        with BuildLine():
            ThreePointArc(pt(R1, -pf), pt(R1, 0), pt(R1, pf))
            if j0 >= pe:
                Spline(sampled(pf, pe))
                ThreePointArc(pt(R0, pe), pt(R0, (pe + j0) / 2), pt(R0, j0))
                Spline(sampled(j0, j1))
                ThreePointArc(pt(R0, j1), pt(R0, (j1 + 360 - pe) / 2), pt(R0, 360 - pe))
            else:                                    # joystick zone runs on from the shoulder: one spline
                Spline(sampled(pf, j1))
                ThreePointArc(pt(R0, j1), pt(R0, (j1 + 360 - pe) / 2), pt(R0, 360 - pe))
            Spline(sampled(360 - pe, 360 - pf))
        make_face()
    env = extrude(sk.sketch, amount=C["BW"])
    if JOY_SIDE < 0:
        env = env.mirror(Plane.XZ)                   # thick zone on the -Y side (the shoulders are symmetric)
    mk = BRepFilletAPI_MakeFillet(env.wrapped)
    for e in env.edges():
        if e.geom_type == GeomType.LINE or abs((e @ 0.5).X) < C["BW"] / 2 - 0.1:
            continue
        mk.Add(C["EDGE"], C["EDGE"], e.wrapped)
    mk.Build()
    env = Solid(mk.Shape())
    print("band outline rounded 0.4, valid:", env.is_valid)
    fused = block + env

    def dist(shape, p):
        v = Vertex(p.X, p.Y, p.Z)
        return min(f.distance_to(v) for f in shape.faces())
    junc = [e for e in fused.edges() if all(dist(block, e @ t) < 2e-3 and dist(env, e @ t) < 2e-3 for t in (0.25, 0.5, 0.75))]
    reached = None
    for r in (4.0, 3.5, 3.0, 2.5):
        try:
            cand = fillet(junc, r)
            if cand.is_valid:
                fused, reached = cand, r
                break
        except Exception:
            print(f"junction fillet {r} failed")
    print(f"junction edges {len(junc)}, junction fillet reached {reached}")
    if reached is None:
        print("exterior.py: junction fillet failed down to 2.5, exit 1")
        sys.exit(1)
    if LIFT417:                                           # merged417: merged32h's block, band and blend united with the tall block
        fused = fused + tall
        print("merged417: merged32h block + band + blend united with the tall block, valid:", fused.is_valid)
        # the crease where merged32h's blend meets the taller wall (about 11 degrees at X 0, Z 2.24 at US 9) is NOT rounded: a
        # rounding builds on some sizes only (run 2: 2.0 on US 9 and 10, 1.0 on US 12 and 13, none of 2.0, 1.5, 1.0 on US 7, 8, 11;
        # out/work-417/build-417-us*.log, run 2, and diag-crease2-us7.log: 0.5 and 0.3 fail too), so all sizes keep the same
        # unrounded crease (an open look point in design/look/s1/merged417-notes.md)
    fused = fused - (Pos(0, 0, zc) * Rot(0, 90, 0) * Cylinder(ri, 60))

    def surf_r(deg, side=1, x=0.0, step=0.05):
        a = math.radians(deg)
        r = ri + 0.01
        while r < ri + 8:
            if not fused.is_inside(Vector(x, side * r * math.sin(a), zc + r * math.cos(a))):
                break
            r += step
        r -= step
        while r < ri + 8:
            r += 0.005
            if not fused.is_inside(Vector(x, side * r * math.sin(a), zc + r * math.cos(a))):
                break
        return r
    if WIN:
        # owner 2026-11-13 "2: three windows" (design/look/s1/slit-grille-notes.md, variant 2): on each long side the through slit
        # over the floor slot and two equal blind windows 0.20 deep along Y, filled black (solid slit_fill). The blind depth is
        # taken on a local piece of the body per side (a skin made on the whole body came out empty on -Y: work-flat/slit/
        # inspect-fill.log, try 3 of the variant study).
        global SLIT_FILL
        SLOT_Z0 = {7: -0.20, 8: -0.20, 9: -0.23, 10: -0.63, 11: -1.04, 12: -1.45, 13: -1.85}   # thin.py SIZE_TABLE slot_z0
        z0, z1 = SLOT_Z0[SIZE if SIZE else 9], 1.53
        dep = float(os.environ.get("WIN_DEPTH", "0.20"))   # 0.20 (owner pick, lead); WIN_DEPTH only for the broken copy of the depth check
        mnb = (Align.MIN, Align.MIN, Align.MIN)

        def ybox(x0, x1, s_, y0, y1, za, zb):
            ya, yb = (y0, y1) if s_ > 0 else (-y1, -y0)
            return Pos(x0, ya, za) * Box(x1 - x0, yb - ya, zb - za, align=mnb)
        cutw, fillw = None, None
        addw = lambda a_, b_: b_ if a_ is None else a_ + b_
        for s_ in (1, -1):
            slit = ybox(-3.55, -1.45, s_, 5.6, 14.0, z0, z1)
            fillw = addw(fillw, fused & slit)
            cutw = addw(cutw, slit)
            local = fused & ybox(-4.0, 4.0, s_, 5.0, 14.0, z0 - 0.3, z1 + 0.3)
            skin = local - (Pos(0, -s_ * dep, 0) * local)
            for x0 in (-1.05, 1.45):
                g = skin & ybox(x0, x0 + 2.1, s_, 6.0, 14.0, z0, z1)
                cutw = addw(cutw, g)
                fillw = addw(fillw, g)
        fused = fused - cutw
        SLIT_FILL = fillw
        print("merged417flatw: slit X -3.55..-1.45 and blind windows 0.20 deep at X -1.05..1.05, 1.45..3.55, Z %.2f to %.2f, both sides; body valid %s; black fill %d solids, volume %.4f"
              % (z0, z1, fused.is_valid, len(fillw.solids()), fillw.volume))
    return fused, dict(zc=zc, ri=ri, R0=R0, junction_fillet=reached, junction_edges=len(junc)), surf_r


def main_merged_c():
    import math
    from build123d import Vector
    fused, info, surf_r = build_merged_c()
    zc, ri, ro = info["zc"], info["ri"], info["R0"]
    BXc, BYc = C["BX"], C["BY"]
    wall_y = BYc / 2
    ml, mh, md, mz = C["MIC"]
    mics = []
    for x in MIC_XS:
        slot = Pos(x, -wall_y + md / 2 - 0.5, mz) * Box(ml, md + 1.0, mh)
        slot = fillet(slot.edges().filter_by(Axis.Y), mh / 2 - 0.005)
        mesh = Pos(x, -wall_y + md - MIC_MESH_T / 2, mz) * Box(ml, MIC_MESH_T, mh)
        mesh = fillet(mesh.edges().filter_by(Axis.Y), mh / 2 - 0.005)
        mics.append((slot, mesh))
    if F_LIKE:
        # no wall slot: each microphone opening is a seat (2.0 x 0.10 from the underside) and a 1.0 hole on to Z 0.30;
        # mic_1 / mic_2 = a thin dark disc (MIC_MESH_T) at the bottom of the seat, Z 0.04 to 0.10
        mics = []
        mn = (Align.CENTER, Align.CENTER, Align.MIN)
        for x in F32["MIC_XS"]:
            seat = Pos(x, F32["MIC_Y"], -0.5) * Cylinder(F32["SEAT_D"] / 2, 0.5 + F32["SEAT_T"], align=mn)
            hole = Pos(x, F32["MIC_Y"], -0.5) * Cylinder(F32["HOLE_D"] / 2, 0.5 + F32["HOLE_Z1"], align=mn)
            disc = Pos(x, F32["MIC_Y"], F32["SEAT_T"] - MIC_MESH_T) * Cylinder(F32["SEAT_D"] / 2, MIC_MESH_T, align=mn)
            mics.append((seat + hole, disc))
    for slot, _ in mics:
        fused = fused - slot
    # contact pads on the -Y side of the band at 150 degrees from the top, flush with the outer surface (thin curved pads)
    pa = math.radians(C["PAD_DEG"])
    skin = (Pos(0, 0, zc) * Rot(0, 90, 0) * Cylinder(ro, 20)) - (Pos(0, 0, zc) * Rot(0, 90, 0) * Cylinder(ro - 0.1, 20))
    pad_pt = Vector(0, -ro * math.sin(pa), zc + ro * math.cos(pa))
    pad_n = Vector(0, -math.sin(pa), math.cos(pa))
    ploc = Plane(origin=(pad_pt.X, pad_pt.Y, pad_pt.Z), x_dir=(1, 0, 0), z_dir=(pad_n.X, pad_n.Y, pad_n.Z))
    pads = []
    for x in C["PAD_XS"]:
        cyl = Pos(x, 0, 0) * Cylinder(C["PAD_D"] / 2, 1.0)
        pads.append((ploc * cyl) & skin)
    contacts = Compound(pads)
    if not NO_BTN:
        for p in pads:
            fused = fused - p

    def frame(deg, sd=1):
        a = math.radians(deg)
        rm, rp, r0 = surf_r(deg - 2, sd), surf_r(deg + 2, sd), surf_r(deg, sd)
        drda = (rp - rm) / math.radians(4)
        rh = Vector(0, sd * math.sin(a), math.cos(a))
        th = Vector(0, sd * math.cos(a), -math.sin(a))
        n = (rh - th * (drda / r0)).normalized()
        return Vector(0, sd * r0 * math.sin(a), zc + r0 * math.cos(a)), n, r0
    JP, Jn, jr = frame(C["JOY_DEG"], JOY_SIDE)
    BP, Bn, br = frame(C["BTN_DEG"], BTN_SIDE)
    loc = lambda P, n: Plane(origin=(P.X, P.Y, P.Z), x_dir=(1, 0, 0), z_dir=(n.X, n.Y, n.Z))

    def rrect_solid(lx, ly, z0, z1, r):
        return Pos(0, 0, z0) * extrude(RectangleRounded(lx, ly, r), amount=z1 - z0)
    frame_s = rrect_solid(C["FRAME_X"], C["FRAME_ARC"], -0.3, C["FRAME_PROUD"], C["FRAME_R"])
    top = C["FRAME_PROUD"] + C["NUB_PROUD"]
    nub = rrect_solid(C["NUB_X"], C["NUB_ARC"], C["FRAME_PROUD"] - 0.2, top, C["NUB_R"])
    dome_r = ((C["NUB_ARC"] / 2) ** 2 + C["NUB_DOME"] ** 2) / (2 * C["NUB_DOME"])
    nub = nub & (Pos(0, 0, top - dome_r) * Sphere(dome_r))
    if H_LIKE:
        # owner 2026-11-11: "Should be round with texture for thumb", "a bit more protruding". Lead's values: frame round,
        # outer diameter H32 FRAME_D, same height as today (-0.3 to FRAME_PROUD); cap round, diameter CAP_D at its top, its
        # rim NUB_PROUD + CAP_EXTRA above the frame, top edge rounded EDGE_R, a spherical dish DISH deep inside the rounded
        # edge, three concentric ridges (width RIDGE_W, height RIDGE_H above the dish) at RIDGE_RS.
        mn = (Align.CENTER, Align.CENTER, Align.MIN)
        frame_s = Pos(0, 0, -0.3) * Cylinder(H32["FRAME_D"] / 2, C["FRAME_PROUD"] + 0.3, align=mn)
        cap_top = C["FRAME_PROUD"] + C["NUB_PROUD"] + H32["CAP_EXTRA"]
        cap0 = C["FRAME_PROUD"] - 0.2
        cap = Pos(0, 0, cap0) * Cylinder(H32["CAP_D"] / 2, cap_top - cap0, align=mn)
        cap = fillet(cap.edges().group_by(Axis.Z)[-1], H32["EDGE_R"])
        a_d = H32["CAP_D"] / 2 - H32["EDGE_R"]                     # dish rim = where the rounded edge starts
        R_d = (a_d ** 2 + H32["DISH"] ** 2) / (2 * H32["DISH"])
        dish_c = Pos(0, 0, cap_top - H32["DISH"] + R_d)
        cap = cap - dish_c * Sphere(R_d)
        # each ridge = the cap's own top surface raised RIDGE_H, inside a ring RIDGE_W wide: it follows the dish and, for the
        # outer ridge, the start of the rounded edge, so it sits on the cap everywhere (no overhang)
        lifted = Pos(0, 0, H32["RIDGE_H"]) * cap
        ridges = None
        for rr_ in H32["RIDGE_RS"]:
            ring = Pos(0, 0, cap_top) * (Cylinder(rr_ + H32["RIDGE_W"] / 2, 4.0) - Cylinder(rr_ - H32["RIDGE_W"] / 2, 4.2))
            rg = (lifted & ring) - cap
            ridges = rg if ridges is None else ridges + rg
        cap = cap + ridges
        nub = cap
        print("merged32h: frame round %.2f, cap round %.2f, cap rim %.3f above the frame (was %.3f), dish %.2f, ridges %s x %.2f wide x %.2f high"
              % (H32["FRAME_D"], H32["CAP_D"], cap_top - C["FRAME_PROUD"], C["NUB_PROUD"], H32["DISH"], H32["RIDGE_RS"], H32["RIDGE_W"], H32["RIDGE_H"]))
    joy = loc(JP, Jn) * (frame_s + nub)
    pill_b = Pos(0, 0, (C["BTN_PROUD"] - 0.3) / 2) * Box(C["BTN_L"], C["BTN_W"], C["BTN_PROUD"] + 0.3)
    pill_b = fillet(pill_b.edges().filter_by(Axis.Z), C["BTN_W"] / 2 - 0.005)
    pill_b = fillet(pill_b.edges().group_by(Axis.Z)[-1], C["BTN_EDGE"])
    btn = loc(BP, Bn) * pill_b
    gap = joy.distance_to(btn)
    if F_LIKE:
        # K3: the joystick opening, sized on this file's own frame (lead's ruling: 17.11 orientation): 6.6 along X, 5.6 along
        # the band (tangent), centred under the joystick, placed as thin.py lplace(-78) = Pos(0, 0, ZC) * Rot(78, 0, 0).
        # Outer end 2.0 above the surface (as thin.py line 379); inner end in the bore, so it goes through the whole wall.
        a_f = JOY_SIDE * C["JOY_DEG"]
        r0_f, r1_f = ri - 0.2, jr + 2.0
        opening = Pos(0, 0, zc) * Rot(-a_f, 0, 0) * Pos(0, 0, (r0_f + r1_f) / 2) * Box(F32["OPEN_X"], F32["OPEN_T"], r1_f - r0_f)
        if H_LIKE:       # round opening, its axis on the radial at the joystick angle; no chamfer, as today
            opening = Pos(0, 0, zc) * Rot(-a_f, 0, 0) * Pos(0, 0, (r0_f + r1_f) / 2) * Cylinder(H32["OPEN_D"] / 2, r1_f - r0_f)
        fused = fused - opening
        if H_LIKE:
            print("merged32h: joystick opening round, diameter %.1f, at %.0f deg, cut from r %.3f to r %.3f" % (H32["OPEN_D"], a_f, r0_f, r1_f))
        else:
            print("merged32f: joystick opening %.1f (X) x %.1f (along the band) at %.0f deg, cut from r %.3f to r %.3f" % (F32["OPEN_X"], F32["OPEN_T"], a_f, r0_f, r1_f))
    fb, nb = frame_s.bounding_box(), nub.bounding_box()
    print("metal around the nub inside the frame, measured on the solids (local frame): -X %.3f, +X %.3f, -arc %.3f, +arc %.3f mm" % (nb.min.X - fb.min.X, fb.max.X - nb.max.X, nb.min.Y - fb.min.Y, fb.max.Y - nb.max.Y))
    print("joystick at %d deg (Y sign %+d): surface radius %.3f, normal (%.3f, %.3f, %.3f)" % (C["JOY_DEG"], JOY_SIDE, jr, Jn.X, Jn.Y, Jn.Z))
    print("measured band thickness under the joystick frame (X 0): %.3f mm" % (jr - ri))
    print("pads at 150 degrees on -Y: plain wall %.3f mm; joystick frame spans %.1f to %.1f degrees" % (surf_r(150, -1) - ri, C["JOY_DEG"] - 15.1, C["JOY_DEG"] + 15.1))
    if F_LIKE:
        print("merged32f: no record button, no outside pads, no placeholder solids")
    else:
        print("record button at %d deg (Y sign %+d): surface radius %.3f; plain band between button and joystick frame: %.3f mm" % (C["BTN_DEG"], BTN_SIDE, br, gap))
    print("shoulder thickness at 38 degrees: +Y %.3f mm, -Y %.3f mm; contacts side -Y at %d deg, plain wall %.3f mm" % (surf_r(38) - ri, surf_r(38, side=-1) - ri, C["PAD_DEG"], surf_r(C["PAD_DEG"], side=-1) - ri))
    cut = Pos(0, 0, C["GLASS_Z"] + 20) * Box(80, 80, 40)
    glass = fused & cut
    body = fused - cut
    bbf = fused.bounding_box()
    bbb = (fused & (Pos(0, 0, 0) * Box(60, 60, 4.0, align=(Align.CENTER, Align.CENTER, Align.MIN)))).bounding_box()
    if LIFT417:
        bbb = (fused & (Pos(0, 0, 0) * Box(60, 60, 4.0 + LIFT417, align=(Align.CENTER, Align.CENTER, Align.MIN)))).bounding_box()
        print("merged417: block size %.2f x %.2f x %.3f mm (%.3f at the centre line, %.3f at the long edges)"
              % (BXc, BYc, C["TOP_Z"], C["TOP_Z"], C["TOP_Z"] - (0.0 if FLAT417 else C["ARC_R"] - math.sqrt(C["ARC_R"] ** 2 - (BYc / 2) ** 2))))
    else:
        print(f"block size: {BXc:.2f} x {BYc:.2f} x {C['TOP_Z']:.2f} mm (3.85 at the centre line, 2.95 at the long edges)")
    print("sculpt study, contract not checked")
    print("block bounding box (above Z 0): X %.3f..%.3f  Y %.3f..%.3f  Z %.3f..%.3f" % (bbb.min.X, bbb.max.X, bbb.min.Y, bbb.max.Y, bbb.min.Z, bbb.max.Z))
    print("whole bounding box: X %.3f..%.3f  Y %.3f..%.3f  Z %.3f..%.3f" % (bbf.min.X, bbf.max.X, bbf.min.Y, bbf.max.Y, bbf.min.Z, bbf.max.Z))
    # lit screen plate: a thin curved shell 0.02 above the glass arc, 21.6 x 10.8
    az = C["TOP_Z"] - C["ARC_R"]
    shell = (Pos(0, 0, az) * Rot(0, 90, 0) * Cylinder(C["ARC_R"] + SCREEN_T, 60)) - (Pos(0, 0, az) * Rot(0, 90, 0) * Cylinder(C["ARC_R"], 60))
    screen = shell & (Pos(SCREEN_CX, SCREEN_CY, C["TOP_Z"]) * Box(LIT_X, LIT_Y, 4, align=(Align.CENTER, Align.CENTER, Align.CENTER)))
    if FLAT417:
        screen = Pos(SCREEN_CX, SCREEN_CY, C["TOP_Z"]) * Box(LIT_X, LIT_Y, SCREEN_T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    light = Pos(LIGHT_X, LIGHT_Y, C["TOP_Z"] - 0.01) * Cylinder(LIGHT_D / 2, LIGHT_T + 0.01, align=(Align.CENTER, Align.CENTER, Align.MIN))
    hidden = Pos(0, 0, zc - ro + C["WALL"] / 2) * Box(0.4, 0.4, 0.4)
    if NO_BTN:   # the contract's part list needs all 10 names: placeholders are 0.3 mm cubes hidden inside the band wall
        btn = Pos(1.0, 0, zc - ro + C["WALL"] / 2) * Box(0.3, 0.3, 0.3)
        contacts = Pos(-1.0, 0, zc - ro + C["WALL"] / 2) * Box(0.3, 0.3, 0.3)
    parts = {"body": body, "glass": glass, "screen": screen, "band": hidden, "joystick": joy,
             "button": btn, "light": light, "mic_1": mics[0][1], "mic_2": mics[1][1], "contacts": contacts}
    if F_LIKE:
        # K2: the light window at F32 LIGHT_X, LIGHT_Y, LIGHT_D (provisional, light-path helper); a skin from 0.01 under to
        # 0.02 over the glass's own top surface, so it follows the arc. The old light at X -12, Y 0 is not made.
        lw = Pos(F32["LIGHT_X"], F32["LIGHT_Y"], 0) * Cylinder(F32["LIGHT_D"] / 2, 20)
        parts["light"] = (lw & (Pos(0, 0, LIGHT_T) * glass)) - (Pos(0, 0, -0.01) * glass)
        # K3: the three specks (placeholder solids band, button, contacts inside the band wall) are not made
        for n in ("band", "button", "contacts"):
            del parts[n]
    if H_LIKE:
        # the recording light was removed from the design (architecture 17.30): the accepted variant makes no light solid.
        # merged32f and merged32g keep it (history).
        del parts["light"]
    rep = {"variant": VARIANT, "block_size": [BXc, BYc, C["TOP_Z"]], "info": info, "joystick_thickness_150": round(jr - ri, 3),
           "arc_r": C["ARC_R"], "top_z": C["TOP_Z"], "edge_z": C["TOP_Z"] - (C["ARC_R"] - math.sqrt(C["ARC_R"] ** 2 - (BYc / 2) ** 2)),
           "block_bbox_above_z0": [round(v, 3) for v in (bbb.min.X, bbb.min.Y, bbb.min.Z, bbb.max.X, bbb.max.Y, bbb.max.Z)]}
    for n, s_ in parts.items():
        b = s_.bounding_box()
        rep[n] = {"volume": round(s_.volume, 4), "min": [round(b.min.X, 3), round(b.min.Y, 3), round(b.min.Z, 3)],
                  "max": [round(b.max.X, 3), round(b.max.Y, 3), round(b.max.Z, 3)]}
    NAME = "ring-%s" % VARIANT + ("-us%d" % SIZE if SIZE else "")
    rep["us_size"], rep["bore"] = SIZE, BAND_ID
    if KIND in ("merged32g", "merged32h", "merged417", "merged417flat"):
        rep["joystick_deg"] = -C["JOY_DEG"]
        rep["thick_zone_flat_deg"] = [-C["JOY_FLAT0"], -C["JOY_FLAT1"]]
        rep["thick_zone_with_ease_deg"] = [-(C["JOY_FLAT0"] - C["JOY_EASE"]), -(C["JOY_FLAT1"] + C["JOY_EASE"])]
        rep["outer_radius_at_joystick_x0"] = round(jr, 4)
    rep["whole_bbox"] = [round(v, 3) for v in (bbf.min.X, bbf.min.Y, bbf.min.Z, bbf.max.X, bbf.max.Y, bbf.max.Z)]
    if LIFT417:
        rep["lift_over_merged32h"] = LIFT417
        rep["glass_seat_z"] = C["GLASS_Z"]
        if FLAT417:
            rep["flat_top"], rep["edge_z"], rep["arc_r"] = True, C["TOP_Z"], None
    json.dump(rep, open(OUT + "/measures-%s.json" % NAME[len("ring-"):], "w"), indent=1)
    from build123d import export_gltf, export_step
    kids = []
    for n in PART_NAMES:
        if n not in parts:             # merged32f leaves out the three placeholder specks
            continue
        parts[n].label = n
        kids.append(parts[n])
    if WIN:                            # merged417flatw: the black sealant in the slit and the two blind windows
        SLIT_FILL.label = "slit_fill"
        kids.append(SLIT_FILL)
    asm = Compound(label=NAME, children=kids)
    export_gltf(asm, os.path.join(OUT, NAME + ".glb"), binary=True, linear_deflection=0.004, angular_deflection=0.06)
    export_step(asm, os.path.join(OUT, NAME + ".step"))
    print("exported: %s.glb, %s.step" % (NAME, NAME))
    if LIFT417:                        # merged417 and merged417flat also write one STL of every solid (the same tessellation as its GLB)
        from build123d import export_stl
        export_stl(asm, os.path.join(OUT, NAME + ".stl"), tolerance=0.004, angular_tolerance=0.06)
        print("exported: %s.stl" % NAME)
    print("exterior.py: done, exit 0")


if __name__ == "__main__":
    main()
