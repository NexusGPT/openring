#!/usr/bin/env python3
"""Read the board plan rows of the parts the model draws and their footprints (F.Fab body outline, courtyard, pads, descr).
Writes board_rows.json and prints one line per part. Read only: placement-plan.csv, footprint-sources.csv, OpenRing.pretty/*.kicad_mod."""
import csv, json, math, re, sys
from pathlib import Path
ROOT = Path((__import__("pathlib").Path(__file__).resolve().parents[6].as_posix()))
PLAN = ROOT / "design/wiring/ring-board-plan-work/placement-plan.csv"
LIB = ROOT / "design/ecad/ring/pcb/OpenRing.pretty"
SRC = ROOT / "design/ecad/ring/pcb/footprint-sources.csv"
REFS = sys.argv[1].split(",") if len(sys.argv) > 1 else None

def sexp_blocks(txt, head):
    out, i = [], 0
    while True:
        j = txt.find("(" + head, i)
        if j < 0:
            return out
        d, k = 0, j
        while True:
            if txt[k] == "(":
                d += 1
            elif txt[k] == ")":
                d -= 1
                if d == 0:
                    break
            k += 1
        out.append(txt[j:k + 1])
        i = k + 1

def nums(s, key):
    m = re.search(r"\(" + key + r"\s+([-\d.]+)\s+([-\d.]+)", s)
    return (float(m.group(1)), float(m.group(2))) if m else None

def layer(s):
    m = re.search(r'\(layers?\s+"([^"]+)"', s)
    return m.group(1) if m else None

def read_fp(name):
    txt = (LIB / (name + ".kicad_mod")).read_text()
    fab, crt = [], []
    for kind in ("fp_rect", "fp_line"):
        for b in sexp_blocks(txt, kind + "\n") + sexp_blocks(txt, kind + " "):
            st, en = nums(b, "start"), nums(b, "end")
            L = layer(b)
            if st and en:
                (fab if L == "F.Fab" else crt if L == "F.CrtYd" else []).extend([st, en])
    for b in sexp_blocks(txt, "fp_poly"):
        L = layer(b)
        pts = [(float(a), float(c)) for a, c in re.findall(r"\(xy\s+([-\d.]+)\s+([-\d.]+)\)", b)]
        (fab if L == "F.Fab" else crt if L == "F.CrtYd" else []).extend(pts)
    pads = []
    for b in sexp_blocks(txt, "pad "):
        nm = re.match(r'\(pad\s+"([^"]*)"', b).group(1)
        at = re.search(r"\(at\s+([-\d.]+)\s+([-\d.]+)(?:\s+([-\d.]+))?\)", b)
        sz = nums(b, "size")
        pads.append(dict(name=nm, x=float(at.group(1)), y=float(at.group(2)), rot=float(at.group(3) or 0), sx=sz[0], sy=sz[1],
                         shape=re.match(r'\(pad\s+"[^"]*"\s+\w+\s+(\w+)', b).group(1)))
    descr = re.search(r'\(descr\s+"([^"]*)"', txt)
    bb = lambda P: None if not P else (min(p[0] for p in P), min(p[1] for p in P), max(p[0] for p in P), max(p[1] for p in P))
    return dict(fab=bb(fab), crtyd=bb(crt), pads=pads, descr=descr.group(1) if descr else "")

def to_board(x, y, rot, cx, cy):
    """KiCad footprint local (x, y) at orientation rot (deg) to the model's board X, Y (model = KiCad - 100, no flip: plan R2.5)."""
    t = math.radians(rot)
    return cx + x * math.cos(t) + y * math.sin(t), cy - x * math.sin(t) + y * math.cos(t)

rows = {r["reference"]: r for r in csv.DictReader(open(PLAN))}
src = {r["reference"]: r for r in csv.DictReader(open(SRC))}
res = {}
for ref in (REFS or rows):
    r = rows[ref]
    fpn = r["footprint"].split(":")[1]
    if not (LIB / (fpn + ".kicad_mod")).exists():
        print(f"{ref}: footprint {fpn} not in {LIB}")
        continue
    fp = read_fp(fpn)
    cx, cy, rot = float(r["x_mm"]), float(r["y_mm"]), float(r["rotation_deg"])
    x0, y0, x1, y1 = fp["fab"]
    cs = [to_board(x, y, rot, cx, cy) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    bx = (min(c[0] for c in cs), max(c[0] for c in cs)); by = (min(c[1] for c in cs), max(c[1] for c in cs))
    pads = []
    for p in fp["pads"]:
        px, py = to_board(p["x"], p["y"], rot, cx, cy)
        q = (p["rot"] + rot) % 180
        sx, sy = (p["sx"], p["sy"]) if abs(q) < 1 or abs(q - 180) < 1 else (p["sy"], p["sx"])
        pads.append((p["name"], round(px, 4), round(py, 4), sx, sy))
    res[ref] = dict(footprint=fpn, side=r["side"], x=cx, y=cy, rot=rot, fab_local=fp["fab"], crtyd_local=fp["crtyd"],
                    body_x=(round(bx[0], 4), round(bx[1], 4)), body_y=(round(by[0], 4), round(by[1], 4)),
                    body_size=(round(bx[1] - bx[0], 4), round(by[1] - by[0], 4)), pads=pads, descr=fp["descr"],
                    source=(src.get(ref, {}).get("maker_document_file", ""), src.get(ref, {}).get("page", "")))
    print(f"{ref} {fpn} side {r['side']} at ({cx:.3f}, {cy:.3f}) rot {rot:g}: F.Fab local {fp['fab']} -> body X {bx[0]:.3f} to {bx[1]:.3f}, Y {by[0]:.3f} to {by[1]:.3f} "
          f"(size {bx[1]-bx[0]:.3f} x {by[1]-by[0]:.3f}); {len(pads)} pads; source {src.get(ref, {}).get('maker_document_file', '')} {src.get(ref, {}).get('page', '')}")
    print(f"   descr: {fp['descr'][:400]}")
out = Path(__file__).resolve().parent / "board_rows.json"
json.dump(res, open(out, "w"), indent=1)
print(f"wrote {out} ({len(res)} rows)")
