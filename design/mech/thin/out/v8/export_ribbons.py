#!/usr/bin/env python3
"""v8: export ONLY the two ribbon maker files of ONE ring size (derived from out/v7-export/export_size.py, the project exporter: same emit(), same fresh-copy and
solid-count and volume checks). Writes flex-tail-thumb/ and flex-tail-away/ (the ribbon, and the polyimide foot stiffener as its own file) and out/v8/rows_flex_usN.json.

(v7 docstring)  Export the maker files of ONE ring size from the inside model v7 (thin.py; round joystick, no recording light; pads at X -1.0).

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
OUTD = os.path.join(THIN, "out/v8")
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


def emit(part, size, shape, source, status, stl=False, model_volume=None, folder=None):
    d = os.path.join(PARTS, folder or part)
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
P = thin.P
src = f"design/mech/thin/thin.py v8 built at US {SIZE} ({os.path.basename(EXT)}, bore {P['bore_d']})"
say(f"US {SIZE}: exterior {EXT}, bore {P['bore_d']}, parts {len(m['parts'])}")
for tag, nm in (("thumb", "band_flex_thumb"), ("away", "band_flex_away")):
    pv = {c: [x for x in sub.solids()] for c, sub in S[nm].items()}
    note = {"thumb": "joystick-side ribbon (FLEX1): vertical neck 1.8 wide, 90 degree fold (inner radius 0.70), flat foot 2.5 wide, trunk, bend, flat head; 0.11 thick outside the liner, 0.15 embedded; no copper",
            "away": "other-side ribbon (FLEX2): vertical neck 1.8 wide, 90 degree fold (inner radius 0.70), flat foot 2.5 wide, trunk, pad strip X -3.4 to 0.25; 0.11 thick outside the liner, 0.15 embedded; no copper"}[tag]
    emit("flex-tail-" + tag, SIZE, S[nm]["flex"], src + f" ({nm}__flex)", note)
    emit("flex-tail-" + tag + "-footstiffener", SIZE, S[nm]["polymer"], src + f" ({nm}__polymer)", "polyimide stiffener 0.10 thick under the foot, X -3.45 to -0.95, |Y| 3.45 to 5.05", folder="flex-tail-" + tag)
with open(os.path.join(OUTD, f"rows_flex_us{SIZE}.json"), "w") as f:
    json.dump(rows, f, indent=1)
with open(os.path.join(OUTD, f"export_flex_us{SIZE}.txt"), "w") as f:
    f.write("\n".join(log) + "\n")
say("done")
