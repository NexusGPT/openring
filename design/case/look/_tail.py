def pin_ys(pitch=None):
    """Pin y positions: the pad y of the middle size (US 10) for each pin (pads sit at ri sin(theta); the pin row is straight)."""
    out = []
    for k in range(4):
        out.append(round(pad_face_xy(10, k, pitch)[1], 3))
    return out


def make_pin(xb, y, z, h):
    """Pin axis along X, base plane at x = xb, tip pole at x = xb - h; barrel 1.85 long, plunger 0.6, dome 0.3 radius."""
    r = PIN["plunger_d"] / 2
    barrel = cyl_x(xb - PIN["barrel_h"], xb, y, z, PIN["barrel_d"])
    dome = Pos(xb - h + r, y, z) * Sphere(r)
    ln = (xb - PIN["barrel_h"] + 0.01) - (xb - h + r)
    if ln > 0.02:
        return barrel + cyl_x(xb - h + r, xb - PIN["barrel_h"] + 0.01, y, z, PIN["plunger_d"]) + dome
    return barrel + dome


def size_text(parts):
    names = ("shell", "base_plate", "lid", "hinge_pivot")
    bb = Compound(children=[parts[n] for n in names]).bounding_box()
    return bb, (f"closed case outer size X {bb.size.X:.1f} mm x Y {bb.size.Y:.1f} mm x Z {bb.size.Z:.1f} mm "
                f"(X {bb.min.X:.2f} to {bb.max.X:.2f}, Y {bb.min.Y:.2f} to {bb.max.Y:.2f}, Z {bb.min.Z:.2f} to {bb.max.Z:.2f}); "
                f"volume of the box {bb.size.X*bb.size.Y*bb.size.Z/1000:.1f} cm3")


def pin_heights(parts, rings, meta, n):
    """Pin extension (height from the base plane to the pad face) of every pin at size n: x_b - pad face x."""
    return [meta["xb"][k] - pad_face_xy(n, k)[0] for k in range(4)]


def main():
    os.makedirs(PARTS, exist_ok=True)
    for f in glob.glob(os.path.join(PARTS, "*.step")):
        os.remove(f)                                   # C3 parts are kept in out/old_C3/parts
    parts, rings, meta = build()
    for name, shp in parts.items():
        export_step(shp, os.path.join(PARTS, f"{name}.step"))
    ring9 = rings[9].parts_in_case(meta["zb"])
    kids = []
    for k, v in ring9.items():
        v.label = f"ring_US9_{k}"
        kids.append(v)
    nodes = []
    for name, shp in parts.items():
        s = shp.moved(shp.location)
        s.label = name
        nodes.append(s)
    nodes.append(Compound(children=kids, label="ring_US9"))
    asm = Compound(children=nodes, label="case_assembly_US9")
    export_step(asm, os.path.join(OUT, "case_assembly_US9.step"))
    export_gltf(asm, os.path.join(OUT, "case_assembly_US9.glb"), binary=True)
    for n in ("shell", "base_plate", "lid", "post", "hinge_pivot"):
        export_stl(parts[n], os.path.join(OUT, f"case_{n}.stl"))
    bb, txt = size_text(parts)
    with open(os.path.join(OUT, "case_size.txt"), "w") as f:
        f.write(txt + "\n")
    hts = {n: pin_heights(parts, rings, meta, n) for n in SIZES}
    allh = [h for v in hts.values() for h in v]
    params = dict(
        pin=PIN, pin_window=[PIN_H_MIN, PIN_H_MAX], pad_pitch=PAD_PITCH, pad_d=PAD_D, pad_x_off=PAD_X_OFF, pad_nets=PAD_NETS,
        tip_gap=TIP_GAP, phi=PHI, flank_gap=FLANK_GAP, sizes=SIZES, ri={n: ri_of(n) for n in SIZES}, r0={n: r0_of(n) for n in SIZES},
        zc={n: zc_of(n) for n in SIZES}, cx={n: cx_of(n) for n in SIZES}, x_a=X_A,
        pin_heights={str(n): hts[n] for n in SIZES},
        pin_travel=dict(min_height=min(allh), max_height=max(allh), spread=max(allh) - min(allh),
                        needed_stroke=max(allh) - min(allh) + 0.2),
        parts=sorted(parts), size_box=[bb.size.X, bb.size.Y, bb.size.Z], clearance=CLR, pocket_g=POCKET_G,
        lid_open_deg=LID_OPEN_DEG, lid_gap=LID_GAP, **meta,
    )
    with open(os.path.join(OUT, "case_params.json"), "w") as f:
        json.dump(params, f, indent=1, default=float)
    print(txt)
    print("parts:", len(parts))
    print("pin heights spread %.3f mm (window %.2f to %.2f)" % (max(allh) - min(allh), PIN_H_MIN, PIN_H_MAX))
    print("case.py done")


if __name__ == "__main__":
    main()
