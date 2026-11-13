"""Measure the 2.4 GHz chip antenna ANT1 against the metal around it (review finding F06).

Reads design/mech/thin/placement.csv and design/mech/thin/layers.json for the parts, their layer and their
metal flag, and the inside model's STEP (design/mech/thin/out/thin-inside.step) for the real shapes: the
body's pocket walls, floor, end roll and the formed cover glass are not boxes, so their distances are
measured by casting straight rays from the antenna body and reading where each ray enters and leaves
each solid.

Run: cd <repo>/design/mech/antenna && nice -n 19 ../../.venv/bin/python measure_antenna.py > measure.log 2>&1
Last line: RESULT measured (only when every check below ran and the STEP antenna matches placement.csv).
"""
import csv
import json
import sys
from pathlib import Path

from build123d import import_step
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.IntCurvesFace import IntCurvesFace_ShapeIntersector
from OCP.TopAbs import TopAbs_IN, TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
from OCP.gp import gp_Dir, gp_Lin, gp_Pnt

HERE = Path(__file__).resolve().parent
THIN = HERE.parent / "thin"
PLACEMENT = THIN / "placement.csv"
LAYERS = THIN / "layers.json"
STEP = THIN / "out" / "thin-inside.step"
ARCH_KEEPOUT = (4.2, 4.7)      # design/architecture.md line 156: "no copper and no metal within 4.2 x 4.7 mm"
REACH = 30.0                   # ray length, mm (longer than the block)
N = 5                          # rays per face edge (N x N grid)


def f3(v):
    return f"{v:.3f}"


# ------------------------------------------------------------------ inputs
rows = list(csv.DictReader(open(PLACEMENT)))
byname = {r["part"]: r for r in rows}
layer_of = {}
for lay in json.load(open(LAYERS))["layers"]:
    for p in lay["parts"]:
        layer_of[p] = lay["name"]
ant = byname["antenna"]
ax, ay, az = float(ant["x"]), float(ant["y"]), float(ant["z"])
sx, sy, sz = float(ant["size_x"]), float(ant["size_y"]), float(ant["size_z"])
A = dict(x0=ax - sx / 2, x1=ax + sx / 2, y0=ay - sy / 2, y1=ay + sy / 2, z0=az - sz / 2, z1=az + sz / 2)
print(f"inputs: {PLACEMENT} ({len(rows)} rows), {LAYERS} ({len(layer_of)} parts in layers), {STEP}")
print(f"antenna row (placement.csv line {[r['part'] for r in rows].index('antenna') + 2}): {ant['reference']} centre ({ax}, {ay}, {az}) size {sx} x {sy} x {sz}")
print(f"antenna box: X {f3(A['x0'])} to {f3(A['x1'])}, Y {f3(A['y0'])} to {f3(A['y1'])}, Z {f3(A['z0'])} to {f3(A['z1'])}")
print("axes (layers.json): X along the finger (+X fingertip, -X hand end), Y across (+Y thumb), Z up (+Z the glass)")

# ------------------------------------------------------------------ STEP solids
top = import_step(str(STEP))
solids = {}          # label -> list of TopoDS_Solid
for ch in top.children:
    lab = ch.label
    exp = TopExp_Explorer(ch.wrapped, TopAbs_SOLID)
    lst = []
    while exp.More():
        lst.append(exp.Current())
        exp.Next()
    solids[lab] = lst
print(f"STEP: {len(solids)} labelled shapes")


def part_of(label):
    return label.split("__")[0]


def cls_of(label):
    return label.split("__")[1] if "__" in label else ""


def metal_flag(label):
    p = byname.get(part_of(label))
    return p["metal"] if p else "?"


bb = top.children[[c.label for c in top.children].index("antenna__ceramic")].bounding_box()
bbm = top.children[[c.label for c in top.children].index("antenna__metal")].bounding_box()
step_box = (min(bb.min.X, bbm.min.X), max(bb.max.X, bbm.max.X), min(bb.min.Y, bbm.min.Y), max(bb.max.Y, bbm.max.Y),
            min(bb.min.Z, bbm.min.Z), max(bb.max.Z, bbm.max.Z))
match = all(abs(a - b) < 0.002 for a, b in zip(step_box, (A["x0"], A["x1"], A["y0"], A["y1"], A["z0"], A["z1"])))
print(f"STEP antenna box: X {f3(step_box[0])} to {f3(step_box[1])}, Y {f3(step_box[2])} to {f3(step_box[3])}, "
      f"Z {f3(step_box[4])} to {f3(step_box[5])}; same as placement.csv: {match}")

isect = {}


def intervals(label, p0, d):
    """Return the (t_in, t_out) spans where the ray p0 + t d (t > 0) is inside the solids of label."""
    out = []
    for i, s in enumerate(solids[label]):
        key = (label, i)
        if key not in isect:
            it = IntCurvesFace_ShapeIntersector()
            it.Load(s, 1e-6)
            isect[key] = it
        it = isect[key]
        it.Perform(gp_Lin(gp_Pnt(*p0), gp_Dir(*d)), 0.0, REACH)
        ts = sorted({round(it.WParameter(k), 6) for k in range(1, it.NbPnt() + 1)})
        ts = [0.0] + ts
        for a, b in zip(ts, ts[1:]):
            if b - a < 1e-5:
                continue
            m = (a + b) / 2
            cl = BRepClass3d_SolidClassifier(s, gp_Pnt(p0[0] + m * d[0], p0[1] + m * d[1], p0[2] + m * d[2]), 1e-7)
            if cl.State() == TopAbs_IN:
                if out and abs(out[-1][1] - a) < 1e-5:
                    out[-1] = (out[-1][0], b)
                else:
                    out.append((a, b))
    return sorted(out)


def face_grid(direction):
    """N x N origins on the antenna face that points along direction, slightly outside it."""
    e = 1e-4
    pts = []
    for i in range(N):
        for j in range(N):
            u, v = (i + 0.5) / N, (j + 0.5) / N
            if direction == "-X":
                pts.append((A["x0"] - e, A["y0"] + u * sy, A["z0"] + v * sz))
            elif direction == "+X":
                pts.append((A["x1"] + e, A["y0"] + u * sy, A["z0"] + v * sz))
            elif direction == "-Y":
                pts.append((A["x0"] + u * sx, A["y0"] - e, A["z0"] + v * sz))
            elif direction == "+Y":
                pts.append((A["x0"] + u * sx, A["y1"] + e, A["z0"] + v * sz))
            elif direction == "-Z":
                pts.append((A["x0"] + u * sx, A["y0"] + v * sy, A["z0"] - e))
            elif direction == "+Z":
                pts.append((A["x0"] + u * sx, A["y0"] + v * sy, A["z1"] + e))
    return pts


DIRS = {"-X": (-1, 0, 0), "+X": (1, 0, 0), "-Y": (0, -1, 0), "+Y": (0, 1, 0), "-Z": (0, 0, -1), "+Z": (0, 0, 1)}
NAMES = {"-X": "hand-end wall (-X)", "+Y": "thumb-side wall (+Y)", "-Y": "side wall away from the thumb (-Y)",
         "-Z": "floor (-Z)", "+X": "toward the fingertip (+X)", "+Z": "up, toward the glass (+Z)"}
labels = [l for l in solids if not l.startswith("antenna__")]

print()
print("== 1. Each direction: first metal of the body, its thickness, then what is beyond it")
print(f"   ({N} x {N} = {N * N} rays per antenna face, straight out along the face normal; distances in mm from the antenna face)")
summary = {}
for dn in ("-X", "+Y", "-Y", "-Z", "+X"):
    d = DIRS[dn]
    gaps, thick, firsts, beyond = [], [], {}, set()
    for p0 in face_grid(dn):
        body = intervals("outer_body__metal", p0, d)
        if body:
            gaps.append(body[0][0])
            thick.append(body[0][1] - body[0][0])
            after = [lab for lab in labels if lab != "outer_body__metal"
                     and any(t0 > body[0][1] - 1e-6 and t0 < body[0][1] + 3.0 for t0, _ in intervals(lab, p0, d))]
            beyond.add(",".join(after) if after else "air")
        hits = []
        for lab in labels:
            iv = intervals(lab, p0, d)
            if iv:
                hits.append((iv[0][0], lab))
        if hits:
            t, lab = min(hits)
            firsts.setdefault(lab, []).append(t)
    if gaps:
        print(f"   {NAMES[dn]}: body metal at {f3(min(gaps))} to {f3(max(gaps))} from the antenna face; "
              f"metal thickness on these rays {f3(min(thick))} to {f3(max(thick))}; rays that hit the body {len(gaps)} of {N * N}; "
              f"beyond the metal (next 3 mm): {sorted(beyond)}")
    else:
        print(f"   {NAMES[dn]}: no ray meets the body within {REACH} mm")
    for lab, ts in sorted(firsts.items(), key=lambda kv: min(kv[1])):
        print(f"      first thing met on {len(ts)} of {N * N} rays: {lab} (part metal flag {metal_flag(lab)}) at {f3(min(ts))} to {f3(max(ts))}")
    summary[dn] = (min(gaps) if gaps else None, min(thick) if thick else None)

print()
print("== 2. Straight up from the antenna's top face to the outside air (every solid crossed, in order)")
stacks = {}
for p0 in face_grid("+Z"):
    seq = []
    for lab in [l for l in solids if not l.startswith("antenna__")]:
        for t0, t1 in intervals(lab, p0, DIRS["+Z"]):
            seq.append((round(p0[2] + t0, 3), round(p0[2] + t1, 3), lab))
    seq.sort()
    key = tuple((lab, round(z1 - z0, 3)) for z0, z1, lab in seq)
    stacks.setdefault(key, []).append((p0, seq))
for key, lst in sorted(stacks.items(), key=lambda kv: -len(kv[1])):
    xs = sorted({round(p[0], 3) for p, _ in lst})
    ys = sorted({round(p[1], 3) for p, _ in lst})
    print(f"   stack on {len(lst)} of {N * N} rays (ray X in {xs}, Y in {ys}), antenna top at Z {f3(A['z1'])}:")
    seq = lst[0][1]
    zprev = A["z1"]
    for z0, z1, lab in seq:
        if z0 - zprev > 1e-3:
            print(f"      Z {f3(zprev)} to {f3(z0)}: open space {f3(z0 - zprev)}")
        print(f"      Z {f3(z0)} to {f3(z1)}: {lab} (layer {layer_of.get(part_of(lab), '?')}, part metal flag {metal_flag(lab)}) {f3(z1 - z0)}")
        zprev = z1
    print(f"      above Z {f3(zprev)}: outside air")

print()
print("== 3. Does the screen panel cover the antenna? (plan view, X-Y footprints from the STEP bounding boxes)")
afoot = (A["x0"], A["x1"], A["y0"], A["y1"])
aarea = sx * sy


def overlap(b):
    w = max(0.0, min(afoot[1], b.max.X) - max(afoot[0], b.min.X))
    h = max(0.0, min(afoot[3], b.max.Y) - max(afoot[2], b.min.Y))
    return w * h


for lab in ("screen__screen", "screen__chip", "screen__mark", "screen_tail__flex", "foam__foam", "main_board__pcb",
            "clear_adhesive__polymer", "cover_glass__glass", "screen_connector__polymer", "screen_connector__gold"):
    ch = top.children[[c.label for c in top.children].index(lab)]
    b = ch.bounding_box()
    print(f"   {lab}: footprint X {f3(b.min.X)} to {f3(b.max.X)}, Y {f3(b.min.Y)} to {f3(b.max.Y)}, Z {f3(b.min.Z)} to {f3(b.max.Z)}; "
          f"bounding-box overlap with the antenna footprint {f3(overlap(b))} of {f3(aarea)} mm2")
print("   note: screen__mark is the lit (active) area drawn on the panel top; screen__chip is the driver IC on the ledge")

print()
print("== 4. Least 3D distance from the antenna (ceramic and terminations) to every metal solid within 3 mm")
ant_shapes = solids["antenna__ceramic"] + solids["antenna__metal"]
near = []
for lab in labels:
    if metal_flag(lab) != "True" and cls_of(lab) not in ("metal", "gold"):
        continue
    best = None
    for s in solids[lab]:
        for a_ in ant_shapes:
            ds = BRepExtrema_DistShapeShape(a_, s)
            if ds.IsDone():
                v = ds.Value()
                best = v if best is None else min(best, v)
    if best is not None and best < 3.0:
        near.append((best, lab))
for v, lab in sorted(near):
    print(f"   {lab} (layer {layer_of.get(part_of(lab), '?')}, metal flag {metal_flag(lab)}): {f3(v)}")

print()
print(f"== 5. The design's keep-out {ARCH_KEEPOUT[0]} x {ARCH_KEEPOUT[1]} mm (architecture.md line 156) centred on the antenna")
kx0, kx1 = ax - ARCH_KEEPOUT[0] / 2, ax + ARCH_KEEPOUT[0] / 2
ky0, ky1 = ay - ARCH_KEEPOUT[1] / 2, ay + ARCH_KEEPOUT[1] / 2
print(f"   keep-out reaches X {f3(kx0)} to {f3(kx1)}, Y {f3(ky0)} to {f3(ky1)} (orientation as the BOM row does not say which side is 4.2; "
      f"the other way round it reaches X {f3(ax - 2.35)} to {f3(ax + 2.35)}, Y {f3(ay - 2.1)} to {f3(ay + 2.1)})")
inside = []
for c in top.children:
    if c.label.startswith("antenna__"):
        continue
    b = c.bounding_box()
    w = max(0.0, min(kx1, b.max.X) - max(kx0, b.min.X))
    h = max(0.0, min(ky1, b.max.Y) - max(ky0, b.min.Y))
    if w * h > 0:
        inside.append((c.label, w * h))
for lab, ar in inside:
    print(f"   inside the keep-out column (bounding box, any Z): {lab} (metal flag {metal_flag(lab)}) overlap {f3(ar)} mm2")
body_in = any(l == "outer_body__metal" for l, _ in inside)
print(f"   body metal inside the keep-out: {body_in}")

print()
print("== 6. Summary")
for dn in ("-X", "+Y", "-Y", "-Z"):
    g, t = summary[dn]
    print(f"   {NAMES[dn]}: gap {f3(g) if g is not None else 'none'} mm, metal {f3(t) if t is not None else 'none'} mm")
ok = match and all(summary[d][0] is not None for d in ("-X", "+Y", "-Z"))
print("RESULT measured" if ok else "RESULT not measured: STEP antenna differs from placement.csv or a wall was not found")
