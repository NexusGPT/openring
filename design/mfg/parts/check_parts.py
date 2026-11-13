"""Check every file listed in index.csv. Exit 0 and last line 'RESULT PASS files=<n>' when all hold, else exit 1 and 'RESULT FAIL ...'.
Run from this folder: ../../.venv/bin/python check_parts.py
v6.2 (2026-11-11): also checks each STEP's volume against index.csv (0.01 mm3, tight integration); bore measured at x=3.55."""
import csv, os, sys
from build123d import import_step, Box, Pos
from partlib import read_stl, mesh_info, bbox_of

HERE = os.path.dirname(os.path.abspath(__file__))
DESIGN = os.path.abspath(os.path.join(HERE, "..", ".."))
errs = []
nfiles = 0


def fail(msg):
    errs.append(msg); print("FAIL", msg, flush=True)


def bore_of(body):
    """Bore diameter: on a line along Z at x=3.55, y=0 the body is metal in two pieces (the band's side wall at the bottom, the
    block above the bore); the gap between them is the bore. v6.2 bodies have the band channel cut (X -3.4 to 3.4) and the
    motor pocket (to X 3.3), so the line runs in the band's side wall beside the channel, not at x=0."""
    z0, z1 = bbox_of(body)[0][2] - 1, bbox_of(body)[1][2] + 1
    hit = body & (Pos(3.55, 0, (z0 + z1) / 2) * Box(0.02, 0.02, z1 - z0))
    segs = sorted((s_.bounding_box().min.Z, s_.bounding_box().max.Z) for s_ in hit.solids())
    gaps = [b[0] - a[1] for a, b in zip(segs, segs[1:]) if b[0] - a[1] > 5]
    return gaps[0] if len(gaps) == 1 else None


sizes = {r["us_size"]: float(r["bore_mm"]) for r in csv.DictReader(open(os.path.join(DESIGN, "look/s1/out/sizes.csv")))}
rows = list(csv.DictReader(open(os.path.join(HERE, "index.csv"))))
steps = {}
for r in rows:
    if r["status"] == "not modelled" and not r["path"]:
        continue
    nfiles += 1
    p = os.path.join(DESIGN, r["path"])
    tag = r["path"]
    if not os.path.isfile(p):
        fail("missing file " + tag); continue
    want_lo = [float(r["bbox_x" + "min"]), float(r["bbox_ymin"]), float(r["bbox_zmin"])]
    want_ext = [float(r["bbox_x_mm"]), float(r["bbox_y_mm"]), float(r["bbox_z_mm"])]
    if r["format"] == "STEP":
        try:
            s = import_step(p)
        except Exception as ex:
            fail("cannot re-import %s: %r" % (tag, ex)); continue
        n = len(s.solids())
        from OCP.GProp import GProp_GProps
        from OCP.BRepGProp import BRepGProp
        vol = 0.0
        for so in s.solids():
            g = GProp_GProps(); BRepGProp.VolumeProperties_s(so.wrapped, g, 1e-7); vol += g.Mass()
        if abs(vol - float(r["volume_mm3"])) > 0.01:
            fail("%s volume %.4f, index says %s" % (tag, vol, r["volume_mm3"]))
        if n != int(r["solids"]):
            fail("%s has %d solids, index says %s" % (tag, n, r["solids"]))
        lo, hi = bbox_of(s)
        for a, w, nm in zip(lo, want_lo, "xyz"):
            if abs(a - w) > 0.01: fail("%s bbox min %s = %.4f, index says %.4f" % (tag, nm, a, w))
        for l, h, w, nm in zip(lo, hi, want_ext, "xyz"):
            if abs((h - l) - w) > 0.01: fail("%s bbox extent %s = %.4f, index says %.4f" % (tag, nm, h - l, w))
        steps[(r["part"], r["ring_size"])] = (lo, hi)
        if r["part"] == "body" and r["ring_size"] in sizes:
            b = bore_of(s)
            if b is None: fail("%s: bore not measurable" % tag)
            elif abs(b - sizes[r["ring_size"]]) > 0.01:
                fail("%s bore %.4f, sizes.csv %.4f" % (tag, b, sizes[r["ring_size"]]))
            else:
                print("ok bore %s US %s: %.4f vs sizes.csv %.4f" % (r["part"], r["ring_size"], b, sizes[r["ring_size"]]), flush=True)
    elif r["format"] == "STL":
        n, closed, manifold, (mlo, mhi) = mesh_info(read_stl(p))
        if not closed: fail("%s is not closed (open edges)" % tag)
        if n != int(r["triangles"]): fail("%s has %d triangles, index says %s" % (tag, n, r["triangles"]))
        key = (r["part"], r["ring_size"])
        if key not in steps: fail("%s: its STEP was not checked before it" % tag)
        else:
            lo, hi = steps[key]
            for a, b, nm in zip(list(mlo) + list(mhi), list(lo) + list(hi), ["xmin", "ymin", "zmin", "xmax", "ymax", "zmax"]):
                if abs(a - b) > 0.02: fail("%s mesh %s %.4f differs from STEP %.4f" % (tag, nm, a, b))
    else:
        fail("unknown format %s in %s" % (r["format"], tag))
print("checked %d files, %d problems" % (nfiles, len(errs)))
if errs:
    print("RESULT FAIL files=%d problems=%d" % (nfiles, len(errs))); sys.exit(1)
print("RESULT PASS files=%d" % nfiles)
