#!/usr/bin/env python3
"""Collision check for ring.py. Exit 1 on any finding, 0 when everything fits.

Checks, all from the real model built by ring.build():
 1. pairwise intersection volume of all internal solids (> LIMIT mm3 is a finding)
 2. each internal solid against the top shell and against the base of every size 5 to 13
 3. each internal solid must lie inside the envelope minus the housing (inner cavity,
    openings and pockets included; the envelope adds the joystick stem's travel past the wall)
 4. the antenna keep-out volume must hold no metal part (the board is allowed)
 5. wall-thickness rule: on every housing solid (top shell, base of each size) sample points on every
    face (triangle centres of a 0.15 mm tessellation), cast a ray from each point into the material
    along the inward normal, and take the distance to the first face it meets as the local thickness.
    Any thickness under min_wall (dimensions.csv) is a finding. Findings closer than 1.0 mm to each
    other count as one place.
The swelling volume and the motor sleeve are internal solids, so entering them is caught by 1.
Also prints the smallest gaps (distance between solids) for the notes.
"""
import sys
import itertools
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ring  # noqa: E402

LIMIT = 0.001  # mm3


def vol(shape):
    try:
        return shape.volume
    except Exception:
        return 0.0


def inter_vol(a, b):
    ba, bb = a.bounding_box(), b.bounding_box()
    if (ba.max.X < bb.min.X or bb.max.X < ba.min.X or ba.max.Y < bb.min.Y or bb.max.Y < ba.min.Y
            or ba.max.Z < bb.min.Z or bb.max.Z < ba.min.Z):
        return 0.0
    return vol(a & b)


def ray_hits(shape, p, d):
    from OCP.BRepIntCurveSurface import BRepIntCurveSurface_Inter
    from OCP.gp import gp_Lin, gp_Pnt, gp_Dir
    it = BRepIntCurveSurface_Inter()
    it.Init(shape.wrapped, gp_Lin(gp_Pnt(*p), gp_Dir(*d)), 1e-7)
    ws = []
    while it.More():
        ws.append(it.W())
        it.Next()
    return sorted(w for w in ws if w > 1e-4)


def thin_places(shape, limit, tol=0.15):
    """Return (n_samples, list of places); a place = (thickness, x, y, z) of its thinnest sample.
    Each triangle centre is projected onto the true surface; the normal comes from BRepGProp_Face,
    which follows the face orientation (outward from the material)."""
    from OCP.BRepGProp import BRepGProp_Face
    from OCP.BRep import BRep_Tool
    from OCP.ShapeAnalysis import ShapeAnalysis_Surface
    from OCP.gp import gp_Pnt, gp_Vec
    hits = []
    n = 0
    tmin = [9e9, None]
    for f in shape.faces():
        verts, tris = f.tessellate(tol)
        surf = ShapeAnalysis_Surface(BRep_Tool.Surface_s(f.wrapped))
        gp = BRepGProp_Face(f.wrapped)
        for t in tris:
            a, b, c = (verts[i] for i in t)
            ctr = (a + b + c) / 3
            uv = surf.ValueOfUV(gp_Pnt(ctr.X, ctr.Y, ctr.Z), 1e-6)
            pnt, vec = gp_Pnt(), gp_Vec()
            gp.Normal(uv.X(), uv.Y(), pnt, vec)
            if vec.Magnitude() < 1e-12:
                continue
            vec.Normalize()
            n += 1
            p = (pnt.X() - vec.X() * 1e-5, pnt.Y() - vec.Y() * 1e-5, pnt.Z() - vec.Z() * 1e-5)
            w = [x for x in ray_hits(shape, p, (-vec.X(), -vec.Y(), -vec.Z())) if x > 1e-3]
            if w and w[0] < tmin[0]:
                tmin[0], tmin[1] = w[0], (round(pnt.X(), 2), round(pnt.Y(), 2), round(pnt.Z(), 2))
            if w and w[0] < limit - 1e-3:   # 0.001 mm ray noise; exactly 0.5 is not under 0.5
                hits.append((w[0], pnt.X(), pnt.Y(), pnt.Z()))
    hits.sort()
    places = []
    for h in hits:
        if all((h[1] - q[1]) ** 2 + (h[2] - q[2]) ** 2 + (h[3] - q[3]) ** 2 > 1.0 for q in places):
            places.append(h)
    return n, places, tmin


def bb_gap(a, b):
    ba, bb = a.bounding_box(), b.bounding_box()
    dx = max(bb.min.X - ba.max.X, ba.min.X - bb.max.X, 0)
    dy = max(bb.min.Y - ba.max.Y, ba.min.Y - bb.max.Y, 0)
    dz = max(bb.min.Z - ba.max.Z, ba.min.Z - bb.max.Z, 0)
    return (dx * dx + dy * dy + dz * dz) ** 0.5


def main():
    m = ring.build(size=None)
    P = m["parts"]
    findings = []
    errors = []
    n_pairs = 0
    for a, b in itertools.combinations(P, 2):
        n_pairs += 1
        try:
            v = inter_vol(a["solid"], b["solid"])
        except Exception as e:
            errors.append(f"ERROR boolean {a['name']} x {b['name']}: {e}")
            continue
        if v > LIMIT:
            findings.append(f"COLLISION part-part {a['name']} x {b['name']}: {v:.4f} mm3")
    housings = [("top_shell", m["top_shell"])] + [(f"base_size{s}", b) for s, b in m["bases"].items()]
    n_house = 0
    for hn, hs in housings:
        for p in P:
            n_house += 1
            try:
                v = inter_vol(p["solid"], hs)
            except Exception as e:
                errors.append(f"ERROR boolean {p['name']} x {hn}: {e}")
                continue
            if v > LIMIT:
                findings.append(f"COLLISION part-housing {p['name']} x {hn}: {v:.4f} mm3")
    cavity = m["envelope"] - m["top_shell"] - m["bases"][9]
    for p in P:
        pv = vol(p["solid"])
        out = pv - vol(p["solid"] & cavity)
        if out > LIMIT:
            findings.append(f"OUTSIDE cavity {p['name']}: {out:.4f} mm3 of {pv:.4f}")
    ko = m["keepout"]
    for p in P:
        if p["metal"]:
            v = inter_vol(p["solid"], ko)
            if v > LIMIT:
                findings.append(f"KEEPOUT antenna keep-out entered by metal part {p['name']}: {v:.4f} mm3")
    limit = ring.D["min_wall"]
    for hn, hs in housings:
        ns, places, tmin = thin_places(hs, limit)
        print(f"wall rule {hn}: {ns} samples, {len(places)} places under {limit} mm; thinnest {tmin[0]:.3f} mm at {tmin[1]}")
        for w, x, y, zz in places:
            findings.append(f"THIN {hn}: {w:.3f} mm at X {x:.2f} Y {y:.2f} Z {zz:.2f}")
    # smallest gaps, for the notes (not a pass/fail item)
    gaps = []
    for a, b in itertools.combinations(P, 2):
        if bb_gap(a["solid"], b["solid"]) < 0.6:
            try:
                gaps.append((a["solid"].distance_to(b["solid"]), a["name"], b["name"]))
            except Exception as e:
                errors.append(f"ERROR distance {a['name']} x {b['name']}: {e}")
    for p in P:
        for hn, hs in housings[:2]:
            if bb_gap(p["solid"], hs) < 0.6:
                try:
                    gaps.append((p["solid"].distance_to(hs), p["name"], hn))
                except Exception as e:
                    errors.append(f"ERROR distance {p['name']} x {hn}: {e}")
    gaps.sort()
    print(f"parts: {len(P)}, part-part pairs: {n_pairs}, part-housing pairs: {n_house}, limit {LIMIT} mm3")
    touching = [g for g in gaps if g[0] < 1e-4]
    open_gaps = [g for g in gaps if g[0] >= 1e-4]
    print(f"touching pairs (gap < 0.0001 mm, designed contact such as a part on the board): {len(touching)}")
    for g, a, b in touching:
        print(f"  TOUCH {a} x {b}")
    print("smallest open gaps (mm), first 25:")
    for g, a, b in open_gaps[:25]:
        print(f"  GAP {g:.3f} {a} x {b}")
    for e in errors:
        print(e)
    for f in findings:
        print(f)
    bad = len(findings) + len(errors)
    print(f"check_fit: {len(findings)} findings, {len(errors)} errors -> exit {1 if bad else 0}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
