"""board-files (board/index.json + board/plan-<side>.svg): the circuit board as planned, and the plain fact that it
is not routed yet.

Sources, read at collect time (no ring value is held here):
  design/ecad/ring/*.kicad_pcb and design/ecad/ring/pcb/*.kicad_pcb  when present: routed = the file holds tracks (segment, arc or via). The outline is its
                                Edge.Cuts bounding box, the parts are its footprints (reference, position, side by layer), in the file's own
                                coordinates; kicad-cli (found as schematic.py finds it) draws top and bottom.
  design/mech/thin/placement.csv  rows of layer `board`: the largest is the board outline, the others are parts. Each
                                part is on 'top' or 'bottom' by where its middle sits against the board's middle,
                                and only when it is within BOARD_SIDE_MM of a board face (else it is not placed and the
                                `missing` list says so).
  design/architecture.md        the notches of the outline, by their sentences ("notch ... x ... mm"); the newest
                                section stating one wins (a later section is read last).
Numbers x, y are the CENTRE of the rectangle in design mm (x along the finger, + fingertip; y across, + thumb).
The SVG is a plan seen from above the top face, +y (thumb side) up, titled "planned placement, not routed".
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import placements as plc  # noqa: E402
import schematic  # noqa: E402  (its KiCad lookup: $KICAD_CLI, the app paths, then PATH)
from lib import csvread  # noqa: E402
from lib.errors import SourceError  # noqa: E402
from lib.source import pointer  # noqa: E402

RECORD = "board-files"

PCB_DIR = "design/ecad/ring"
PCB_NAME = "ring.kicad_pcb"
ARCH = "design/architecture.md"
BOM = "design/bom.csv"
NUM = r"(\d+(?:\.\d+)?)"
EDGE_NOTCH = re.compile(r"notch of " + NUM + r" x " + NUM + r" mm on its ([a-z-]+) edge")
CORNER_NOTCH = re.compile(r"notch of the board, " + NUM + r" x " + NUM + r" mm, at the ([a-z-]+) corner")
TRACK = re.compile(r"\(\s*(segment|arc|via)\b")


def constants():
    c = json.loads((HERE.parent.parent / "contract" / "schema" / "constants.json").read_text(encoding="utf-8"))
    return c


def ring_refs(ctx):
    p = ctx.source_path(BOM)
    if not p.is_file():
        return set()
    out = set()
    for r in csvread.read(p):
        out.update(csvread.split_refs(r["cells"].get("reference", "")))
    return out


def fmt(v):
    return f"{v:.3f}".rstrip("0").rstrip(".")


def pcb_files(ctx):
    folder = ctx.source_path(PCB_DIR)
    out = []
    for f in (folder, folder / "pcb"):
        if f.is_dir():
            out += sorted(f.glob("*.kicad_pcb"))
    return out


def blocks(text, head):
    """[(first line, block text)] for every balanced `(head ...` block of a KiCad file, at any depth."""
    out = []
    for m in re.finditer(r"\(" + re.escape(head) + r"[\s\"]", text):
        depth, i, q = 0, m.start(), False
        while i < len(text):
            ch = text[i]
            if ch == '"':
                q = not q
            elif not q:
                depth += ch == "("
                depth -= ch == ")"
                if depth == 0:
                    break
            i += 1
        out.append((text.count("\n", 0, m.start()) + 1, text[m.start():i + 1]))
    return out


def pcb_outline(text, rel):
    """Bounding box of everything drawn on Edge.Cuts in a .kicad_pcb, centre form, or None."""
    xs, ys, first = [], [], None
    for head in ("gr_rect", "gr_line", "gr_arc", "gr_poly", "gr_circle"):
        for line, blk in blocks(text, head):
            if "Edge.Cuts" not in blk:
                continue
            first = line if first is None else min(first, line)
            for m in re.finditer(r"\((?:start|end|mid|xy|center) (-?[\d.]+) (-?[\d.]+)\)", blk):
                xs.append(float(m.group(1)))
                ys.append(float(m.group(2)))
    if not xs:
        return None
    return {"x": (min(xs) + max(xs)) / 2, "y": (min(ys) + max(ys)) / 2, "w": max(xs) - min(xs), "h": max(ys) - min(ys),
            "source": pointer(rel, first)}


def pcb_parts(text, refs):
    """Placed parts of a .kicad_pcb from its footprints: reference, centre, size (courtyard, else pads), side.
    Returns (placements with 'ref', names of footprints with no size)."""
    out, nosize = [], []
    for line, blk in blocks(text, "footprint"):
        ref = re.search(r'\(property "Reference" "([^"]*)"', blk)
        at = re.search(r"\(at (-?[\d.]+) (-?[\d.]+)", blk)
        lay = re.search(r'^\(footprint\s+"[^"]*"[\s\S]*?\(layer "([^"]+)"\)', blk)
        if not (ref and at and lay):
            continue
        side = "bottom" if lay.group(1).startswith("B.") else "top"
        cx, cy = float(at.group(1)), float(at.group(2))
        pts = []
        for _l, sub in blocks(blk, "fp_rect"):
            if "CrtYd" in sub:
                pts += [(float(a), float(b)) for a, b in re.findall(r"\((?:start|end) (-?[\d.]+) (-?[\d.]+)\)", sub)]
        if not pts:
            for _l, sub in blocks(blk, "pad"):
                m = re.search(r"\(at (-?[\d.]+) (-?[\d.]+)", sub)
                z = re.search(r"\(size (-?[\d.]+) (-?[\d.]+)", sub)
                if m and z:
                    px, py, w, h = float(m.group(1)), float(m.group(2)), float(z.group(1)), float(z.group(2))
                    pts += [(px - w / 2, py - h / 2), (px + w / 2, py + h / 2)]
        if pts:
            w = max(p[0] for p in pts) - min(p[0] for p in pts)
            h = max(p[1] for p in pts) - min(p[1] for p in pts)
        else:
            w = h = 1.0
            nosize.append(ref.group(1))
        r = ref.group(1)
        out.append({"name": r, "part_id": f"ring:{r}" if r in refs else None, "x": cx, "y": cy, "w": w, "h": h,
                    "side": side, "ref": r})
    return out, nosize


def board_rows(rows):
    """(outline row, part rows) of the layer `board`: the outline is the largest footprint."""
    b = [r for r in rows if r["layer"] == "board"]
    if not b:
        return None, []
    area = lambda r: r["size"]["x"] * r["size"]["y"]  # noqa: E731
    outline = max(b, key=area)
    return outline, [r for r in b if r is not outline]


def side_of(part, board, side_mm):
    """'top' / 'bottom', or None when the part is farther than side_mm from both faces."""
    half = board["size"]["z"] / 2
    top_face, bottom_face = board["centre"]["z"] + half, board["centre"]["z"] - half
    lo = part["centre"]["z"] - part["size"]["z"] / 2
    hi = part["centre"]["z"] + part["size"]["z"] / 2
    if hi < bottom_face - side_mm or lo > top_face + side_mm:
        return None
    return "top" if part["centre"]["z"] > board["centre"]["z"] else "bottom"


def find_notches(ctx, outline, parts, rows, missing):
    """Notches stated by architecture.md, placed on the outline. Later sections win: the LAST matching line is used."""
    p = ctx.source_path(ARCH)
    if not p.is_file():
        missing.append(f"{ARCH} (the board notches are read from it)")
        return []
    lines = p.read_text(encoding="utf-8").splitlines()
    ox, oy = outline["centre"]["x"], outline["centre"]["y"]
    hw, hh = outline["size"]["x"] / 2, outline["size"]["y"] / 2
    out = []

    def last(rx):
        hit = None
        for i, ln in enumerate(lines, 1):
            m = rx.search(ln)
            if m:
                hit = (i, m)
        return hit

    hit = last(CORNER_NOTCH)
    if hit:
        ln, m = hit
        w, h = float(m.group(1)), float(m.group(2))
        # the corner: the end named "hand" is the low-x end; the side is where the part that stands in a notch sits
        in_notch = next((r for r in parts if "notch" in (r["note"] or "")), None)
        sy = 1 if in_notch is None or in_notch["centre"]["y"] >= oy else -1
        sx = -1 if m.group(3).startswith("hand") else 1
        out.append({"name": "antenna notch", "x": ox + sx * (hw - w / 2), "y": oy + sy * (hh - h / 2), "w": w, "h": h,
                    "edge": f"{m.group(3)} corner", "position_known": in_notch is not None,
                    "source": pointer(ARCH, ln)})
    hit = last(EDGE_NOTCH)
    if hit:
        ln, m = hit
        w, h = float(m.group(1)), float(m.group(2))
        # which way is the thumb: the sign of y of the rows whose note starts "thumb side"
        ys = [r["centre"]["y"] for r in rows if (r["note"] or "").startswith("thumb side")]
        sy = (1 if sum(ys) >= 0 else -1) if ys else 1
        out.append({"name": "edge notch", "x": ox, "y": oy + sy * (hh - h / 2), "w": w, "h": h,
                    "edge": f"{m.group(3)} edge", "position_known": False, "source": pointer(ARCH, ln)})
        missing.append(f"where along the {m.group(3)} edge the {fmt(w)} x {fmt(h)} mm notch sits (drawn centred)")
    return out


def svg_plan(side, outline, notches, parts, title):
    margin = 4.0
    ox, oy = outline["x"], outline["y"]
    W, H = outline["w"] + 2 * margin, outline["h"] + 2 * margin + 3.0
    sx = lambda x: x - ox + outline["w"] / 2 + margin  # noqa: E731
    sy = lambda y: oy - y + outline["h"] / 2 + margin + 3.0  # noqa: E731
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {fmt(W)} {fmt(H)}" width="{fmt(W * 20)}" height="{fmt(H * 20)}" '
         f'font-family="sans-serif">',
         f"<title>{escape(title)}</title>",
         f'<rect width="{fmt(W)}" height="{fmt(H)}" fill="#14161a"/>',
         f'<text x="{fmt(margin)}" y="1.6" font-size="1.1" fill="#e8e8e8">{escape(title)}</text>',
         f'<text x="{fmt(margin)}" y="2.9" font-size="0.8" fill="#9aa0a6">{escape(side)} face, seen from above; '
         f'thumb side up; board {fmt(outline["w"])} x {fmt(outline["h"])} mm</text>']
    x0, y0 = sx(ox - outline["w"] / 2), sy(oy + outline["h"] / 2)
    o.append(f'<rect x="{fmt(x0)}" y="{fmt(y0)}" width="{fmt(outline["w"])}" height="{fmt(outline["h"])}" '
             f'fill="#1f5f3f" stroke="#d4af37" stroke-width="0.12"/>')
    for n in notches:
        o.append(f'<rect x="{fmt(sx(n["x"] - n["w"] / 2))}" y="{fmt(sy(n["y"] + n["h"] / 2))}" width="{fmt(n["w"])}" '
                 f'height="{fmt(n["h"])}" fill="#14161a" stroke="#d4af37" stroke-width="0.08" stroke-dasharray="0.3 0.2">'
                 f'<title>{escape(n["name"])}</title></rect>')
    for p in parts:
        px, py = sx(p["x"] - p["w"] / 2), sy(p["y"] + p["h"] / 2)
        o.append(f'<rect x="{fmt(px)}" y="{fmt(py)}" width="{fmt(p["w"])}" height="{fmt(p["h"])}" fill="#3a6ea5" '
                 f'fill-opacity="0.75" stroke="#cfe3ff" stroke-width="0.06"><title>{escape(p["name"])}</title></rect>')
        label = p["ref"] or p["name"]
        o.append(f'<text x="{fmt(sx(p["x"]))}" y="{fmt(sy(p["y"]) + 0.3)}" font-size="0.8" text-anchor="middle" '
                 f'fill="#ffffff">{escape(label)}</text>')
    o.append(f'<text x="{fmt(x0)}" y="{fmt(H - 1.2)}" font-size="0.8" fill="#9aa0a6">hand end</text>')
    o.append("</svg>")
    return "\n".join(o) + "\n"


def extract_base(ctx):
    side_mm = constants()["BOARD_SIDE_MM"]
    missing, sources, notes = [], [], []
    pcbs = pcb_files(ctx)
    routed = False
    pcb_rel = None
    kicad_out = {"top": None, "bottom": None}
    if pcbs:
        pcb_rel = ctx.rel(pcbs[0])
        sources.append(pcb_rel)
        try:
            text = pcbs[0].read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            raise SourceError(f"{pcb_rel} cannot be read: {e}", pcb_rel)
        routed = bool(TRACK.search(text))
        if not routed:
            missing.append("the board file holds no tracks (not routed)")
        cli = schematic._tool()
        if cli:
            # only what a reader needs: the edge, the copper pads, the part outlines, the fabrication layer's reference
            # text (no silkscreen, no value or net text); the back is mirrored so it reads as seen from behind
            for side, layers, flip in (("top", "Edge.Cuts,F.Cu,F.CrtYd,F.Fab", []), ("bottom", "Edge.Cuts,B.Cu,B.CrtYd,B.Fab", ["--mirror"])):
                dst = ctx.out_path(f"board/{side}.svg")
                r = subprocess.run([cli, "pcb", "export", "svg", "--mode-single", *flip, "--layers", layers, "--page-size-mode", "2",
                                    "--exclude-drawing-sheet", "-o", str(dst), str(pcbs[0])],
                                   capture_output=True, text=True, timeout=120)
                if r.returncode == 0 and dst.is_file() and dst.stat().st_size > 0:
                    kicad_out[side] = f"board/{side}.svg"
                else:
                    if dst.exists():
                        dst.unlink()
                    notes.append(f"kicad-cli could not draw the {side} side")
        else:
            notes.append("kicad-cli was not found ($KICAD_CLI, the KiCad app, PATH): no drawing of the board file")
        outline = pcb_outline(text, pcb_rel)
        fps, nosize = pcb_parts(text, ring_refs(ctx))
        if nosize:
            notes.append(f"{pcb_rel}: no courtyard or pad size for {', '.join(nosize)}; drawn 1 x 1")
        if outline is not None or fps:
            if outline is None:
                missing.append("an outline on the Edge.Cuts layer of the board file")
            for pl in fps:
                pl.pop("ref")
            data = {"routed": routed, "outline": outline, "svg": kicad_out, "placements": fps, "missing": missing}
            return data, {"status": "ok", "source": sources, "message": "; ".join(notes) or None}
    else:
        missing.append(f"{PCB_DIR}/{PCB_NAME}")

    # the plan from the placement table
    csv_path = ctx.source_path(plc.CSV)
    if not csv_path.is_file():
        if pcbs:
            data = {"routed": routed, "outline": None, "svg": kicad_out, "placements": [], "missing": missing}
            return data, {"status": "ok", "source": sources, "message": "; ".join(notes) or None}
        return None, {"status": "missing", "source": [plc.CSV], "message": f"{plc.CSV} is not there: no placement plan."}
    rows = plc.read_rows(ctx)
    sources.append(plc.CSV)
    board, parts = board_rows(rows)
    if board is None:
        raise SourceError(f"{plc.CSV} has no row of layer 'board'", plc.CSV)
    outline = {"x": board["centre"]["x"], "y": board["centre"]["y"], "w": board["size"]["x"], "h": board["size"]["y"],
               "source": pointer(plc.CSV, board["line"])}
    refs = ring_refs(ctx)
    placed, unplaced = [], []
    for r in parts:
        s = side_of(r, board, side_mm)
        if s is None:
            unplaced.append(r["name"])
            continue
        pid = f"ring:{r['reference']}" if r["reference"] and r["reference"] in refs else None
        placed.append({"name": r["name"], "part_id": pid, "x": r["centre"]["x"], "y": r["centre"]["y"],
                       "w": r["size"]["x"], "h": r["size"]["y"], "side": s, "ref": r["reference"]})
    if unplaced:
        missing.append(f"a board side for {len(unplaced)} part(s) too far from the board to place ({', '.join(unplaced)})")
    notches = find_notches(ctx, board, parts, rows, missing)
    sources.append(ARCH)

    svg = dict(kicad_out)
    if not routed:
        for side in ("top", "bottom"):
            mine = [p for p in placed if p["side"] == side]
            if not mine:
                continue
            rel = f"board/plan-{side}.svg"
            ctx.out_path(rel).write_text(
                svg_plan(side, outline, notches, mine, "Planned placement, not routed"), encoding="utf-8")
            svg[side] = rel
    for p in placed:
        p.pop("ref")
    data = {"routed": routed, "outline": outline, "svg": svg, "placements": placed, "missing": missing}
    if notches:
        data["notches"] = notches
    return data, {"status": "ok", "source": sources, "message": "; ".join(notes) or None}


def extract(ctx):
    """The board record: the ring board's plan (above) plus the list of every board (boards.py)."""
    import boards  # a peer helper; imported here because it reads this module's block scanner

    data, status = extract_base(ctx)
    entries, read = boards.collect(ctx, blocks, pcb_outline)
    if not read:
        return data, status
    if data is None:
        data = {"routed": False, "outline": None, "svg": {"top": None, "bottom": None}, "placements": [],
                "missing": ["the ring board plan (no placement table and no ring board file)"]}
        status = {"status": "ok", "source": [], "message": None}
    elif isinstance(status, str):
        status = {"status": status, "source": []}
    data["boards"] = entries
    msg = "; ".join(filter(None, [status.get("message"), *(f"{e['id']}: {n}" for e in entries for n in e["notes"][:1])]))
    status = dict(status)
    status["source"] = list(dict.fromkeys([*status.get("source", []), *read]))
    status["message"] = msg or None
    return data, status
