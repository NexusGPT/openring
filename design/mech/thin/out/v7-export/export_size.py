#!/usr/bin/env python3
"""Export the maker files of ONE ring size from the inside model v7 (thin.py; round joystick, no recording light; pads at X -1.0).

Run with the same exterior and bore as that size's check (THIN_EXTERIOR, THIN_OVERRIDE=bore_d=...), and the size as arg 1:
  every size: look/s1/out/ring-merged32h-usN.step (v7; the accepted exterior with the round joystick)
Writes into design/mfg/parts/<part>/ and the rows (one dict per written file) into out/v7-export/rows_usN.json.
Arg 2 'all' also writes the parts that are the same at every size (run it once, on US 9).
Also writes: the whole-ring assembly STEP of the size, a probe log (pockets cut: void points and metal beside them),
the body's dimension table (parts/body/body-usN.dims.csv) used by the drawings."""
import json
import math
import os
import sys

THIN = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design/mech/thin")
DESIGN = (__import__("pathlib").Path(__file__).resolve().parents[5].as_posix() + "/design")
PARTS = os.path.join(DESIGN, "mfg/parts")
OUTD = os.path.join(THIN, "out/v7-export")
sys.path.insert(0, THIN)
sys.path.insert(0, PARTS)
import thin  # noqa: E402
from build123d import import_step, export_step, export_stl, Compound, Vector, Solid  # noqa: E402
from OCP.BRepBuilderAPI import BRepBuilderAPI_Copy  # noqa: E402
from partlib import read_stl, mesh_info, bbox_of, write_clean_stl  # noqa: E402
from OCP.GProp import GProp_GProps  # noqa: E402
from OCP.BRepGProp import BRepGProp  # noqa: E402


def pvol(shape):
    """volume with a tight integration tolerance (the default one differs by about 0.01 mm3 between the same solid in memory and as re-read)"""
    g = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape.wrapped, g, 1e-7)
    return g.Mass()

SIZE = int(sys.argv[1])
ALL = len(sys.argv) > 2 and sys.argv[2] == "all"
assert thin.US_SIZE == SIZE, (thin.US_SIZE, SIZE)
EXT = os.environ["THIN_EXTERIOR"]
rows = []
log = []


def say(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    log.append(s)


def rel(p):
    return os.path.relpath(p, DESIGN)


def emit(part, size, shape, source, status, stl=False, model_volume=None):
    d = os.path.join(PARTS, part)
    os.makedirs(d, exist_ok=True)
    base = os.path.join(d, part + ("" if size == "all" else "-us%s" % size))
    # v7: each solid is written as a fresh copy (the v7 cap's shank, a solid made by booleans, was silently left out of a compound
    # STEP, out/v7/probe/probe_capsolids.log and probe_capstep2.log); the file's solid count and volume are checked against the model below
    solids = [Solid(BRepBuilderAPI_Copy(x.wrapped).Shape()) for x in shape.solids()]
    m_n, m_v = len(solids), sum(pvol(x) for x in solids)
    shape = Compound(children=list(solids), label=part) if len(solids) != 1 else solids[0]
    shape.label = part
    export_step(shape, base + ".step")
    st = import_step(base + ".step")                      # figures come from the file as written
    lo, hi = bbox_of(st)
    vol = sum(pvol(s) for s in st.solids())
    if len(st.solids()) != m_n or abs(vol - m_v) > 0.01:
        raise RuntimeError(f"{part} US {size}: STEP has {len(st.solids())} solids and {vol:.4f} mm3, the model {m_n} and {m_v:.4f}")
    say(f"STEP {part} US {size}: {len(st.solids())} solids, {vol:.4f} mm3, the same as the model ({m_n}, {m_v:.4f})")
    ext = [h - l for l, h in zip(lo, hi)]
    common = dict(part=part, ring_size=size, units="mm", bbox_x_mm=round(ext[0], 4), bbox_y_mm=round(ext[1], 4),
                  bbox_z_mm=round(ext[2], 4), bbox_xmin=round(lo[0], 4), bbox_ymin=round(lo[1], 4), bbox_zmin=round(lo[2], 4),
                  volume_mm3=round(vol, 4), solids=len(st.solids()), source=source, status=status)
    rows.append(dict(common, format="STEP", path=rel(base + ".step"), triangles="", watertight=""))
    if model_volume is not None:
        say(f"volume {part} US {size}: model {model_volume:.4f}, STEP as written {vol:.4f}, difference {abs(vol - model_volume):.4f} mm3 (rule 0.01)")
    if stl:
        export_stl(shape, base + ".stl", tolerance=0.01, angular_tolerance=0.1)
        dropped = write_clean_stl(base + ".stl")
        n, closed, manifold, (mlo, mhi) = mesh_info(read_stl(base + ".stl"))
        mext = [h - l for l, h in zip(mlo, mhi)]
        rows.append(dict(common, format="STL", path=rel(base + ".stl"), bbox_x_mm=round(mext[0], 4), bbox_y_mm=round(mext[1], 4),
                         bbox_z_mm=round(mext[2], 4), bbox_xmin=round(float(mlo[0]), 4), bbox_ymin=round(float(mlo[1]), 4),
                         bbox_zmin=round(float(mlo[2]), 4), triangles=n,
                         watertight=("yes" if manifold else "yes (non-manifold: separate solids touch along an edge)") if closed else "no",
                         status=status + ("; %d zero-area triangles removed from the STL" % dropped if dropped else "")))
        say(f"wrote {part} US {size}: solids {len(st.solids())}, STL triangles {n}, closed {closed}, manifold {manifold}, dropped {dropped}")
    else:
        say(f"wrote {part} US {size}: solids {len(st.solids())} (STEP only)")
    return st


m = thin.build()
S = {p.name: p.solids() for p in m["parts"]}
ctx = m["ctx"]
P = thin.P
src = f"design/mech/thin/thin.py v7 built at US {SIZE} ({os.path.basename(EXT)}, bore {P['bore_d']})"
say(f"US {SIZE}: exterior {EXT}, bore {P['bore_d']}, joystick {P['joy_deg']}, motor {P['motor_angle']}, window {P['motor_window']}, parts {len(m['parts'])}")

# ---- body
body = S["outer_body"]["metal"]
mvol = pvol(body)
say(f"body solids {len(body.solids())}, shells {len(body.shells())}, valid {body.is_valid}")
st = emit("body", SIZE, body, src + " (outer_body)", "machined body WITH the inside pockets cut (model v7)", stl=True, model_volume=mvol)
blo, bhi = bbox_of(st)
elo, ehi = bbox_of(m["body0"])
say("bbox body STEP " + " ".join(f"{v:.4f}" for v in blo + bhi) + " ; exterior body " + " ".join(f"{v:.4f}" for v in elo + ehi)
    + f" ; largest difference {max(abs(a - b) for a, b in zip(blo + bhi, elo + ehi)):.4f} mm (rule 0.01)")

# ---- probes: void points (pockets) and the first metal beside each, marching from the void point
def jp(a, x, t, r):
    ar = math.radians(a)
    return Vector(x, r * math.sin(ar) + t * math.cos(ar), thin.ZC + r * math.cos(ar) - t * math.sin(ar))


def march(p0, d, step=0.01, lim=5.0):
    k = 0.0
    while k < lim:
        q = p0 + d * k
        if st.is_inside(q):
            return k, q
        k += step
    return None, None


probes = [("board cavity", Vector(0, 0, 0.9), Vector(0, 0, -1)),
          ("band channel (cell space, 180 deg)", jp(180, 0.0, 0.0, thin.R_LINER + 0.8), jp(180, 0, 0, 1) - jp(180, 0, 0, 0)),
          ("joystick pocket", jp(P["joy_deg"], 0.0, 3.0, thin.R_LINER + 0.5), Vector(1, 0, 0)),
          ("motor pocket", jp(P["motor_angle"], P["motor_x"], 0.0, thin.R_LINER + 1.25), jp(P["motor_angle"], 0, 0, 1) - jp(P["motor_angle"], 0, 0, 0))]
if ctx.get("window") is not None:
    wc = ctx["window_removed"].center()
    probes.append(("motor window", wc, Vector(0, -1, 0)))
for name, p0, d in probes:
    d = d * (1 / d.length)
    inside = st.is_inside(p0)
    k, q = march(p0, d)
    say(f"probe US {SIZE} {name}: point ({p0.X:.3f}, {p0.Y:.3f}, {p0.Z:.3f}) in metal: {inside}; first metal beside it "
        + (f"{k:.2f} mm away at ({q.X:.3f}, {q.Y:.3f}, {q.Z:.3f}): in metal True" if k is not None else "not found within 3 mm"))

# ---- per-size parts
emit("band-liner", SIZE, S["band_liner"]["resin"], src + " (band_liner__resin)", "0.3 resin skin with the stiffener fill; ribbons and pads cut out", stl=True)
emit("cell", SIZE, S["cell"]["cell"], src + " (cell__cell)", f"pouch body only (sealed edge, tabs not in it); {ctx['cell_len_mm']} mm on its centre line")
emit("flex-tail-thumb", SIZE, S["band_flex_thumb"]["flex"], src + " (band_flex_thumb__flex)", "joystick-side ribbon: vertical piece, trunk, bend, flat head; 0.15 thick, no copper")
emit("joystick-stiffener", SIZE, S["band_flex_thumb"]["metal"], src + " (band_flex_thumb__metal)", "flat stiffener 6.4 x 6.4 x 0.075 under the ribbon head")
emit("flex-tail-away", SIZE, S["band_flex_away"]["flex"], src + " (band_flex_away__flex)", "other-side ribbon to the cell and the pads; 0.15 thick, no copper")
emit("joystick-dam", SIZE, S["joystick_dam"]["polymer"], src + " (joystick_dam__polymer)", "dam round the switch head (as dispensed and cured)")
emit("glass-seal", SIZE, S["glass_seal"]["polymer"], src + " (glass_seal__polymer)", "seal ring 0.05 under the glass edge")
say(f"joystick US {SIZE}: frame top r {ctx['joy_frame_top']}, cap rim r {ctx['joy_cap_rim']}, flange top r {thin.R_PL1:.4f}, cap rim to flange top {ctx['joy_cap_rim'] - thin.R_PL1:.4f} mm (the one CAP1 file needs the same figure at every size)")
if "motor_window_seal" in S:
    emit("motor-window-seal", SIZE, S["motor_window_seal"]["polymer"], src + " (motor_window_seal__polymer)", "sealant plug in the motor window (US 7, 8, 9 only)")

# ---- whole-ring assembly of the size
kids = []
for p in m["parts"]:
    for cls, s in p.solids().items():
        for k_, x in enumerate(s.solids()):
            c_ = Solid(BRepBuilderAPI_Copy(x.wrapped).Shape())
            c_.label = f"{p.name}__{cls}"
            kids.append(c_)
asm = Compound(children=kids, label=f"ring_us{SIZE}")
n_model = len(kids)
os.makedirs(os.path.join(PARTS, "assembly"), exist_ok=True)
ap = os.path.join(PARTS, "assembly", f"ring-assembly-us{SIZE}.step")
export_step(asm, ap)
sa = import_step(ap)
lo, hi = bbox_of(sa)
ext = [h - l for l, h in zip(lo, hi)]
rows.append(dict(part="ring-assembly", ring_size=SIZE, units="mm", format="STEP", path=rel(ap), bbox_x_mm=round(ext[0], 4), bbox_y_mm=round(ext[1], 4),
                 bbox_z_mm=round(ext[2], 4), bbox_xmin=round(lo[0], 4), bbox_ymin=round(lo[1], 4), bbox_zmin=round(lo[2], 4),
                 volume_mm3=round(sum(pvol(s) for s in sa.solids()), 4), solids=len(sa.solids()), triangles="", watertight="", source=src,
                 status=f"every part of the model placed ({len(m['parts'])} parts, children named <part>__<class>)"))
say(f"wrote ring-assembly US {SIZE}: {len(sa.solids())} solids (model {n_model}), {len(m['parts'])} parts")
if len(sa.solids()) != n_model:
    raise RuntimeError(f"ring-assembly US {SIZE}: STEP has {len(sa.solids())} solids, the model {n_model}")

# ---- body dimension table for the drawing (values from the model at this size)
dims = [("Ring size", f"US {SIZE}", "bore %.4f" % P["bore_d"]),
        ("Joystick opening centre (exterior)", "%.1f deg" % P["joy_deg"], "round opening dia 5.6 through the wall, axis on the radial line; frame FRM1 bonded in it"),
        ("Joystick pocket", "7.0 x 6.8", "from the bore to the roof r %.4f (flange top + 0.05)" % (thin.R_PL1 + P["roof_gap"])),
        ("Channel not cut over the joystick", "+-%.3f deg" % ctx["joy_span_deg"], "about the joystick centre"),
        ("Band channel", "6.8 wide", "r %.4f to %.4f, from +30 through the bottom to -30 deg" % (thin.R_IN, thin.R_OUT - P["shell_t"])),
        ("Motor pocket", "dia 5.2 x 2.65", "axis at %.1f deg, X %.1f; floor 0.05 under the motor" % (P["motor_angle"], P["motor_x"])),
        ("Floor slots (2)", "2.0 x 0.6", "X -3.5 to -1.5, Y +-5.9, from Z %.2f to %.2f" % (P["slot_z0"], ctx["Z_FLOOR"] + 0.6)),
        ("Panel pocket", "27.45 x 12.9, R 0.1", "floor top Z %.2f" % ctx["Z_FLOOR"]),
        ("Microphone pockets (2)", "4.4 x 3.35 x 0.10", "centres X +-10.8, Y -4.775"),
        ("Glass seat", "lowered 0.05", "under the glass footprint, outside the panel pocket"),
        ("Cable fold pocket", "0.55 x 5.4 x 2.0", "centre X -13.775")]
if ctx.get("window") is not None:
    wr = ctx["window_removed"].bounding_box()
    dims.append(("Motor window", "%.3f long x %.3f high" % (wr.size.X, wr.size.Z),
                 "X %.3f to %.3f, Y %.3f to %.3f, Z %.3f to %.3f; removed %.4f mm3" % (wr.min.X, wr.max.X, wr.min.Y, wr.max.Y, wr.min.Z, wr.max.Z, ctx["window_removed"].volume)))
with open(os.path.join(PARTS, "body", f"body-us{SIZE}.dims.csv"), "w") as f:
    f.write("feature,value,where\n")
    for a, b, c in dims:
        f.write('"%s","%s","%s"\n' % (a, b, c))

# ---- parts that are the same at every size (written once, from the US 9 build)
# v7: fresh compounds here. Building the assembly above called p.solids() again, and a build123d Compound takes its children
# from the earlier compound: S["joystick_cap"]["polymer"] then held the flange only (the cap's shank was lost, out/v7/probe/
# probe_capsolids.log). The solid counts below are the model's own sub-solid lists.
S = {p.name: p.solids() for p in m["parts"]}
NSUB = {p.name: {c: sum(len(x.solids()) for x in v) for c, v in p.subs.items()} for p in m["parts"]}
say("model sub-solids: joystick_cap polymer %d, joystick_frame metal %d, main_board pcb %d" % (NSUB["joystick_cap"]["polymer"], NSUB["joystick_frame"]["metal"], NSUB["main_board"]["pcb"]))
assert len(S["joystick_cap"]["polymer"].solids()) == NSUB["joystick_cap"]["polymer"] == 2
if ALL:
    s9 = f"design/mech/thin/thin.py v7 built at US 9; same shape at every size"
    emit("cover-glass", "all", S["cover_glass"]["glass"], s9 + " (cover_glass__glass, the exterior's glass)", "formed cover glass; black print outside the lit area with no opening (print not geometry)")
    emit("joystick-cap", "all", S["joystick_cap"]["polymer"], s9 + " (joystick_cap__polymer)", "CAP1 round cap dia 4.40 with its 6.9 x 6.4 x 0.4 flange, dish 0.25, ridges at 0.7, 1.3, 1.9; one moulded part; placed at the US 9 position (-78 deg)", stl=True)
    emit("joystick-frame", "all", S["joystick_frame"]["metal"], s9 + " (joystick_frame__metal)", "FRM1 round frame ring OD 5.40, bore 4.80, 1.30 long; placed at the US 9 position (-78 deg)", stl=True)
    emit("main-board", "all", S["main_board"]["pcb"], s9 + " (main_board__pcb)", "bare board core 27.2 x 12.6 with the antenna notch, no other hole; no mask, pads, copper or parts")
    emit("mic-gasket", "all", Compound(children=S["mic_gasket_1"]["foam"].solids() + S["mic_gasket_2"]["foam"].solids()), s9 + " (mic_gasket_1, mic_gasket_2)", "two foam rings OD 1.8, bore 1.0, at the nominal gap (free thickness chosen per unit)")
    emit("mic-membrane", "all", Compound(children=S["mic_membrane_1"]["polymer"].solids() + S["mic_membrane_2"]["polymer"].solids()), s9 + " (mic_membrane_1, mic_membrane_2)", "two membrane discs dia 2.0 x 0.10")

json.dump(rows, open(os.path.join(OUTD, f"rows_us{SIZE}.json"), "w"), indent=1)
open(os.path.join(OUTD, f"export_us{SIZE}.txt"), "w").write("\n".join(log) + "\n")
print(f"export_size.py: US {SIZE} done, {len(rows)} rows")
