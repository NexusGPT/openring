#!/usr/bin/env python3
"""Dimensioned drawings of the made parts, from their STEP files.

For every design/mfg/parts/<part>/*.step: a sheet (A3 landscape) with three
views in third-angle layout (front, top above it, right side to its right), at a stated
standard scale, overall dimension lines with numbers, and a title block (part
name, reference, material, scale, design version, date, "all dimensions in mm").
Written as design/mfg/drawings/<part>.svg and <part>.pdf.
Exit 1 if any STEP file cannot be read (or a drawing cannot be written).

Axes of the STEP file are used as they are: front looks along +Y (X right, Z up),
top looks down -Z (X right, Y up), right side looks along -X (Y right, Z up).

Run: design/.venv/bin/python design/mfg/tools/draw.py [--parts DIR] [--out DIR] [--only NAME]
"""
import argparse
import csv
import datetime
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

MFG = Path(__file__).resolve().parent.parent
DESIGN_VERSION = "inside model v6.3 (architecture 17.24 to 17.28, 2026-11-11)"
SCALES = [50, 20, 10, 5, 4, 2, 1, 0.5, 0.2]  # drawing size / real size

# default title block data; keys are matched as substrings of the part folder name
META = [
    ("ring-assembly", "Ring assembly, every part placed", "whole ring", "see the part sheets"),
    ("body", "Metal body (block and band), inside pockets cut", "HSG1",
     "Ti-6Al-4V grade 5, black PVD (default, to confirm with the maker)"),
    ("liner", "Band liner, resin cast", "LNR1",
     "Skin-safe cast resin (grade open: maker proposes)"),
    ("glass-seal", "Glass seal ring under the glass edge, 0.05", "SEAL1", "Double-sided waterproof acrylic tape (proposed, assembly.md K-A4)"),
    ("motor-window-seal", "Motor window seal (US 7, 8, 9 only)", "SEAL2", "Same sealant as the floor slots (architecture 17.27)"),
    ("glass", "Cover glass", "GL1",
     "Chemically strengthened aluminosilicate glass, black print (default)"),
    ("joystick-frame", "Joystick frame 6.4 x 5.4 (in the body's opening)", "CAP1 frame", "Open: machined in the body or a separate metal part"),
    ("joystick-stiffener", "Stiffener under the joystick ribbon head", "FLEX1 stiffener", "Stainless or polyimide, 0.075 (to confirm with the flex maker)"),
    ("joystick-dam", "Dam round the joystick switch head", "DAM1", "UV-curing dam material (proposed, assembly.md step 20)"),
    ("joystick", "Joystick nub with its 6.9 x 6.4 flange", "CAP1",
     "Open: design partner and maker"),
    ("flex-tail-thumb", "Band flex tail, joystick side", "FLEX1",
     "Polyimide, 2 copper layers (default, to confirm with the maker)"),
    ("flex-tail-away", "Band flex tail, other side", "FLEX2",
     "Polyimide, 2 copper layers (default, to confirm with the maker)"),
    ("board", "Main board, bare (with the 0.50 light-guide hole)", "PCB1",
     "6 layers, 0.3 mm thick (default, to confirm with the maker)"),
    ("light-guide", "Recording light guide", "LG1", "Clear PC or PMMA, three aluminium-coated mirror faces"),
    ("light-plug", "Recording light plug", "LP1", "Clear block, custom"),
    ("mic-gasket", "Microphone gaskets (2)", "GSK2, GSK3", "Closed-cell foam, PSA both faces"),
    ("mic-membrane", "Microphone membranes (2)", "MEM1, MEM2", "Hydrophobic acoustic membrane, at most 0.10"),
    ("cell", "Curved cell, pouch body", "BT1",
     "Open: Grepow (custom order)"),
]

KEYDIMS = [
    ("Bore per size, US 7 8 9 10 11 12 13", "17.32 18.13 18.95 19.76 20.57 21.38 22.20", "sizes.csv"),
    ("Band width / band thickness", "8.0 / 2.6", "17.1"),
    ("Block height at the centre line / long edges", "3.85 / 2.95", "17.8"),
    ("Joystick centre, from the top, joystick side", "-84 (US 7), -81 (US 8), -78 (US 9 to 13) deg", "17.25"),
    ("Floor slots, both", "2.0 x 0.6 at X -3.5 to -1.5, Y +-5.9", "thin-notes v6.2"),
]


def meta_for(part):
    name, ref, mat = part, "see design/mfg/parts/index.csv", f"see design/mfg/specs/{part}.md"
    for key, n, r, m in META:
        if key in part.lower():
            name, ref, mat = n, r, m
            break
    idx = MFG / "parts" / "index.csv"
    if idx.is_file():  # tolerant: use columns whose names contain these words, if a row names the part
        try:
            with open(idx, newline="", encoding="utf-8") as fh:
                for row in csv.DictReader(fh):
                    if part in " ".join(str(v) for v in row.values()):
                        for k, v in row.items():
                            kl = (k or "").lower()
                            if v and "ref" in kl:
                                ref = v
                            if v and "material" in kl:
                                mat = v
                        break
        except Exception:
            pass
    return name, ref, mat


def edge_points(edge):
    try:
        L = edge.length
    except Exception:
        L = 1.0
    gt = str(getattr(edge, "geom_type", "")).upper()
    n = 2 if "LINE" in gt else max(8, min(120, int(L / 0.15)))
    pts = []
    try:
        for i in range(n + 1):
            p = edge @ (i / n)
            pts.append((p.X, p.Y))
    except Exception:                 # v6.2: OCC cannot evaluate some projected B-spline edges ("knots too close"); the edge is skipped
        SKIPPED[0] += 1
        return []
    return pts


SKIPPED = [0]


def project(shape, origin, up, centre, expect):
    """Hidden-line projection. OCC can return nothing or lose edges for an unlucky
    camera line, so the result is accepted only when its outline equals the STEP
    bounding box (within 0.1 mm) (expect = (width, height)); otherwise the camera is moved by a
    tiny offset (0.01 to 0.3 mm) and tried again."""
    from build123d import Vector
    last = None
    for eps in (0.0, 0.01, 0.03, 0.1, 0.3):
        o = [origin[0], origin[1], origin[2]]
        for i in range(3):
            if abs(up[i]) < 0.5 and abs(o[i] - centre[i]) < 500:
                o[i] += eps  # shift sideways only, not along the viewing axis
        # keep the viewing direction: shift the camera along the two axes that are not the view axis
        try:
            vis, hid = shape.project_to_viewport(Vector(*o), Vector(*up), look_at=Vector(*centre))
        except Exception as ex:      # v6.2: the hidden-line projection itself can fail for one camera line; try the next offset
            print(f"WARNING projection failed at camera offset {eps}: {type(ex).__name__}")
            continue
        n0 = SKIPPED[0]
        v, h = [p for p in (edge_points(e) for e in vis) if p], [p for p in (edge_points(e) for e in hid) if p]
        if SKIPPED[0] > n0:
            print(f"WARNING {SKIPPED[0] - n0} projected edges could not be evaluated and are left out of this view")
        if v:
            e = extents(v + h)
            last = (e[1] - e[0], e[3] - e[2])
            d = max(abs(last[0] - expect[0]), abs(last[1] - expect[1]))
            if d <= 0.1:  # a smooth silhouette edge can be missed by 0.05 mm (cover glass)
                if d > 0.02:
                    print(f"WARNING drawn outline differs from the STEP box by {d:.3f} mm (dimension numbers are the STEP box)")
                return v, h
    raise ValueError(f"projection does not match the STEP box: got {last}, expected {expect}")


def extents(polys):
    xs = [p[0] for pl in polys for p in pl]
    ys = [p[1] for pl in polys for p in pl]
    return min(xs), max(xs), min(ys), max(ys)


def fmt(v):
    return f"{v:.2f}"


def scale_text(s):
    return f"{s:g}:1" if s >= 1 else f"1:{1 / s:g}"


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(part, shape, table=None):
    bb = shape.bounding_box(optimal=True)
    dx, dy, dz = bb.size.X, bb.size.Y, bb.size.Z
    c = bb.center()
    D = 1000.0
    views = {
        "front": ((c.X, c.Y - D, c.Z), (0, 0, 1)),
        "top": ((c.X, c.Y, c.Z + D), (0, 1, 0)),
        "side": ((c.X + D, c.Y, c.Z), (0, 0, 1)),
    }
    expect = {"front": (dx, dz), "top": (dx, dy), "side": (dy, dz)}
    proj = {k: project(shape, o, u, (c.X, c.Y, c.Z), expect[k]) for k, (o, u) in views.items()}
    ext = {k: extents(v[0] + v[1]) for k, v in proj.items()}
    size = {k: (e[1] - e[0], e[3] - e[2]) for k, e in ext.items()}
    # sheet A3 landscape, mm
    W, H = 420.0, 297.0
    gap = 38.0
    availW, availH = 365.0, 195.0
    scale = SCALES[-1]
    for s in SCALES:
        w = (size["front"][0] + size["side"][0]) * s + gap
        h = (size["front"][1] + size["top"][1]) * s + gap
        if w <= availW and h <= availH:
            scale = s
            break
    fw, fh = (size["front"][0] * scale, size["front"][1] * scale)
    tw, th = (size["top"][0] * scale, size["top"][1] * scale)
    sw, sh = (size["side"][0] * scale, size["side"][1] * scale)
    totw = fw + gap + sw
    toth = th + gap + fh
    x0 = 22 + (availW - totw) / 2 + 10
    y0 = 20 + (availH - toth) / 2 + 12  # top of the layout
    # anchor (top-left corner of each view box)
    pos = {"top": (x0, y0), "front": (x0, y0 + th + gap),
           "side": (x0 + fw + gap, y0 + th + gap)}
    out = []
    a = out.append
    a(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" '
      f'viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">')
    a('<defs><marker id="ar" markerWidth="6" markerHeight="4" refX="6" refY="2" orient="auto">'
      '<path d="M6,0 L0,2 L6,4 z" fill="#000"/></marker>'
      '<marker id="al" markerWidth="6" markerHeight="4" refX="0" refY="2" orient="auto">'
      '<path d="M0,0 L6,2 L0,4 z" fill="#000"/></marker></defs>')
    a(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#fff"/>')
    a(f'<rect x="8" y="8" width="{W - 16}" height="{H - 16}" fill="none" stroke="#000" stroke-width="0.7"/>')

    def draw_view(key):
        vis, hid = proj[key]
        ex = ext[key]
        ox, oy = pos[key]
        h = size[key][1] * scale

        def T(p):  # real (x,y) -> sheet; y flips
            return (ox + (p[0] - ex[0]) * scale, oy + h - (p[1] - ex[2]) * scale)
        for pl in hid:
            pts = " ".join(f"{T(p)[0]:.3f},{T(p)[1]:.3f}" for p in pl)
            a(f'<polyline points="{pts}" fill="none" stroke="#777" stroke-width="0.12" stroke-dasharray="1.2,0.8"/>')
        for pl in vis:
            pts = " ".join(f"{T(p)[0]:.3f},{T(p)[1]:.3f}" for p in pl)
            a(f'<polyline points="{pts}" fill="none" stroke="#000" stroke-width="0.3" stroke-linejoin="round"/>')
        return ox, oy, size[key][0] * scale, h

    boxes = {k: draw_view(k) for k in ("top", "front", "side")}
    names = {"top": "TOP", "front": "FRONT", "side": "RIGHT SIDE"}
    axes = {"top": "X right, Y up", "front": "X right, Z up", "side": "Y right, Z up"}

    def hdim(x1, x2, y, ybase, val):
        # horizontal dimension line at y, extension lines down/up from ybase
        sgn = 1 if y > ybase else -1
        a(f'<line x1="{x1:.3f}" y1="{ybase + sgn * 1.5:.3f}" x2="{x1:.3f}" y2="{y + sgn * 2:.3f}" stroke="#000" stroke-width="0.15"/>')
        a(f'<line x1="{x2:.3f}" y1="{ybase + sgn * 1.5:.3f}" x2="{x2:.3f}" y2="{y + sgn * 2:.3f}" stroke="#000" stroke-width="0.15"/>')
        a(f'<line x1="{x1:.3f}" y1="{y:.3f}" x2="{x2:.3f}" y2="{y:.3f}" stroke="#000" stroke-width="0.2" marker-start="url(#al)" marker-end="url(#ar)"/>')
        a(f'<text x="{(x1 + x2) / 2:.3f}" y="{y - 1.2:.3f}" font-size="4" text-anchor="middle">{fmt(val)}</text>')

    def vdim(y1, y2, x, xbase, val):
        sgn = 1 if x > xbase else -1
        a(f'<line x1="{xbase + sgn * 1.5:.3f}" y1="{y1:.3f}" x2="{x + sgn * 2:.3f}" y2="{y1:.3f}" stroke="#000" stroke-width="0.15"/>')
        a(f'<line x1="{xbase + sgn * 1.5:.3f}" y1="{y2:.3f}" x2="{x + sgn * 2:.3f}" y2="{y2:.3f}" stroke="#000" stroke-width="0.15"/>')
        a(f'<line x1="{x:.3f}" y1="{y1:.3f}" x2="{x:.3f}" y2="{y2:.3f}" stroke="#000" stroke-width="0.2" marker-start="url(#al)" marker-end="url(#ar)"/>')
        a(f'<text x="{x + 5.2:.3f}" y="{(y1 + y2) / 2:.3f}" font-size="4" text-anchor="middle" '
          f'transform="rotate(-90 {x + 5.2:.3f} {(y1 + y2) / 2:.3f})">{fmt(val)}</text>')

    # overall dimensions: width under each view, height at its right (side view: right too)
    vals = {"top": (dx, dy), "front": (dx, dz), "side": (dy, dz)}
    for k, (ox, oy, w, h) in boxes.items():
        vw, vh = vals[k]
        hdim(ox, ox + w, oy + h + 9, oy + h, vw)
        vdim(oy, oy + h, ox + w + 9, ox + w, vh)
        a(f'<text x="{ox:.3f}" y="{oy - 3:.3f}" font-size="3.6" font-weight="bold">{names[k]}</text>')
        a(f'<text x="{ox + 22:.3f}" y="{oy - 3:.3f}" font-size="3" fill="#444">({axes[k]})</text>')

    # title block, bottom right
    name, ref, mat = meta_for(part)
    tbx, tby, tbw, tbh = W - 8 - 190, H - 8 - 44, 190, 44
    a(f'<rect x="{tbx}" y="{tby}" width="{tbw}" height="{tbh}" fill="none" stroke="#000" stroke-width="0.5"/>')
    rows = [("PART", name), ("REFERENCE", ref), ("MATERIAL", mat),
            ("SCALE", scale_text(scale)),
            ("DESIGN VERSION", DESIGN_VERSION),
            ("DATE", datetime.date.today().isoformat()),
            ("FILE", f"{part} (STEP in design/mfg/parts/{part}/)")]
    rh = 5.2
    for i, (k, v) in enumerate(rows):
        y = tby + 6 + i * rh
        a(f'<line x1="{tbx}" y1="{y - 4:.2f}" x2="{tbx + tbw}" y2="{y - 4:.2f}" stroke="#000" stroke-width="0.1"/>')
        a(f'<text x="{tbx + 2}" y="{y:.2f}" font-size="2.6" fill="#444">{k}</text>')
        a(f'<text x="{tbx + 36}" y="{y:.2f}" font-size="3.2">{esc(v)}</text>')
    a(f'<text x="{tbx + 2}" y="{tby + tbh - 2.2:.2f}" font-size="3.6" font-weight="bold">ALL DIMENSIONS IN MM</text>')
    a(f'<text x="{tbx + 80}" y="{tby + tbh - 2.2:.2f}" font-size="2.8">General tolerance ISO 2768-m (default). Overall size from the STEP bounding box.</text>')
    # note, bottom left
    a(f'<text x="14" y="{H - 14}" font-size="3" fill="#333">Third-angle projection. Solid lines visible, dashed grey hidden. '
      f'Overall size X {fmt(dx)} x Y {fmt(dy)} x Z {fmt(dz)} mm (STEP axes).</text>')
    if table:
        a(f'<text x="14" y="14" font-size="3.4" font-weight="bold" fill="#b00000">INSIDE POCKETS ARE CUT IN THE 3D FILE. The views give the outline (hidden edges dashed); the pockets are dimensioned in the table, taken from the model at this size.</text>')
        tx, ty = 14.0, 24.0                      # top-left corner of the sheet, clear of the views
        a(f'<text x="{tx}" y="{ty}" font-size="3.0" font-weight="bold">POCKETS AND OPENINGS, mm and deg (thin.py v6.3 at this size)</text>')
        for i, (lab, val, where) in enumerate(table):
            yy = ty + 4.4 + i * 6.4
            a(f'<text x="{tx}" y="{yy:.1f}" font-size="2.6">{esc(lab)}</text>'
              f'<text x="{tx + 52}" y="{yy:.1f}" font-size="2.6" font-weight="bold">{esc(val)}</text>'
              f'<text x="{tx + 3}" y="{yy + 2.8:.1f}" font-size="2.1" fill="#444">{esc(where)}</text>')
    if part == "ring-assembly":
        kx, ky = 14.0, 222.0
        a(f'<text x="{kx}" y="{ky}" font-size="3.4" font-weight="bold">KEY DIMENSIONS, mm (from design/architecture.md; US 9 unless stated)</text>')
        for i, (lab, val, src) in enumerate(KEYDIMS):
            yy = ky + 4.6 + i * 4.2
            a(f'<text x="{kx}" y="{yy:.1f}" font-size="2.9">{esc(lab)}</text>'
              f'<text x="{kx + 78}" y="{yy:.1f}" font-size="2.9">{esc(val)}</text>'
              f'<text x="{kx + 150}" y="{yy:.1f}" font-size="2.9" fill="#444">{esc(src)}</text>')
    a("</svg>")
    return "\n".join(out), scale, (dx, dy, dz)


def write_pdf(svg_path, pdf_path):
    import fitz
    doc = fitz.open(str(svg_path))
    pdf = doc.convert_to_pdf()
    Path(pdf_path).write_bytes(pdf)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", default=str(MFG / "parts"))
    ap.add_argument("--out", default=str(MFG / "drawings"))
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    parts, out = Path(a.parts), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    files = []
    if parts.is_dir():
        for d in sorted(p for p in parts.iterdir() if p.is_dir()):
            if a.only and d.name != a.only:
                continue
            if d.name in ("assembly", "old_merged32c") and not a.only:
                continue                     # whole-ring assemblies and the old files are not drawn by default
            for f in sorted(list(d.glob("*.step")) + list(d.glob("*.stp"))):
                files.append((d.name, f))
    if not files:
        print(f"no STEP files under {parts}")
        sys.exit(0)
    failed = 0
    for part, f in files:
        # one sheet per STEP file; with several STEP files in a folder the file stem is added
        # (several STEP files in a folder: the US 9 file is the part's main sheet, the others keep their file name)
        n_in = sum(1 for p, _ in files if p == part)
        stem = part if (n_in == 1 or "us9" in f.stem) else f.stem
        try:
            from build123d import import_step
            shape = import_step(str(f))
            bb = shape.bounding_box(optimal=True)
            if bb.size.X <= 0 and bb.size.Y <= 0 and bb.size.Z <= 0:
                raise ValueError("empty shape")
        except Exception as e:
            failed += 1
            print(f"ERROR cannot read {f}: {e}")
            continue
        try:
            table = None
            tf = f.with_suffix(".dims.csv")
            if tf.is_file():
                with open(tf, newline="", encoding="utf-8") as fh:
                    table = [(r["feature"], r["value"], r["where"]) for r in csv.DictReader(fh)]
            svg, scale, (dx, dy, dz) = build_svg(stem, shape, table)
            sp, pp = out / f"{stem}.svg", out / f"{stem}.pdf"
            sp.write_text(svg, encoding="utf-8")
            write_pdf(sp, pp)
            print(f"OK {f} -> {sp.name}, {pp.name}  scale {scale_text(scale)}  "
                  f"size {dx:.2f} x {dy:.2f} x {dz:.2f} mm")
        except Exception as e:
            failed += 1
            print(f"ERROR drawing {f}: {type(e).__name__}: {e}")
    print(f"{len(files) - failed} drawn, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
