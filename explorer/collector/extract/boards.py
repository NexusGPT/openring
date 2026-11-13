"""boards (a helper of board.py, no extract() of its own): the list of boards held by board/index.json.

One entry per board file: the ring's main board, the band circuits (two per ring size) and the two case boards.
Everything is read at collect time from the board files; no copy of a board is kept in app source.

  per board   its file, the time of the file, its outline, its copper layers (one SVG per layer made by KiCad's own
              command line, with the board outline in every file), the parts placed on each face (reference, value,
              position, size) and its state.
  state       the rules check, run here with `kicad-cli pcb drc --severity-all`; the numbers are the count lines of
              the report that is saved next to the layer files ("** Found N DRC violations **" and
              "** Found N unconnected pads **"). The words are "routed and checked: 0 violations, 0 open connections"
              when both are 0, else "not finished: N connections open, M violations".

A board file that is missing or cannot be read still gets an entry, with its state in words (status 'not-checked').
"""
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import schematic  # noqa: E402  (its KiCad lookup: $KICAD_CLI, the app paths, then PATH)
from lib import csvread  # noqa: E402
from lib.source import pointer  # noqa: E402

BOM_FILES = {"ring": "design/bom.csv", "case": "design/case/case-bom.csv"}

# The five groups of the board picker. `glob` is a list of repo-relative patterns; `expect` is named in words when
# nothing matches. The words of `what` are plain words for the owner; the numbers and names come from the files.
GROUPS = [
    {"id": "ring", "title": "Ring main board", "bom": "ring", "glob": ["design/ecad/ring/pcb/ring.kicad_pcb"],
     "netlist": "design/ecad/ring/netlist.csv",
     "what": "The main circuit board inside the ring body. The other circuits and the parts of the ring connect to it."},
    {"id": "band-1", "title": "Band circuit 1", "bom": "ring", "glob": ["design/ecad/band/flex1-us*.kicad_pcb"],
     "netlist": None,
     "what": "A flexible circuit that runs through the band on the joystick side. One per ring size."},
    {"id": "band-2", "title": "Band circuit 2", "bom": "ring", "glob": ["design/ecad/band/flex2-us*.kicad_pcb"],
     "netlist": None,
     "what": "A flexible circuit that runs through the band on the other side. One per ring size."},
    {"id": "case-main", "title": "Case main board", "bom": "case", "glob": ["design/ecad/case/pcb/case_main.kicad_pcb"],
     "netlist": "design/ecad/case/netlist.csv",
     "what": "The main circuit board of the charging case."},
    {"id": "case-pins", "title": "Case pin board", "bom": "case", "glob": ["design/ecad/case/pcb/case_pins.kicad_pcb"],
     "netlist": "design/ecad/case/netlist.csv",
     "what": "The small circuit board of the charging case that carries the spring pins touched by the ring."},
]

SIZE_RX = re.compile(r"-us(\d+)\.kicad_pcb$", re.I)
VIOLATIONS_RX = re.compile(r"^\*\*\s*Found (\d+) DRC violations?\s*\*\*\s*$", re.M)
OPEN_RX = re.compile(r"^\*\*\s*Found (\d+) unconnected (?:pads?|items?)\s*\*\*\s*$", re.M)
CREATED_RX = re.compile(r"^\*\*\s*Created on (\S+)\s*\*\*\s*$", re.M)


def plural(n, one, many):
    return f"{n} {one if n == 1 else many}"


def state_words(violations, open_connections):
    """The banner words of a board whose rules check ran."""
    if violations == 0 and open_connections == 0:
        return "routed and checked: 0 violations, 0 open connections"
    return f"not finished: {plural(open_connections, 'connection', 'connections')} open, {plural(violations, 'violation', 'violations')}"


def parse_report(text):
    """(violations, open_connections, [count lines]) of a KiCad rules report, or None when a count line is absent."""
    v, o = VIOLATIONS_RX.search(text), OPEN_RX.search(text)
    if not (v and o):
        return None
    lines = [m.group(0).strip("* ").strip() for m in (v, o)]
    return int(v.group(1)), int(o.group(1)), lines


def layer_label(name):
    """Plain words for a KiCad copper layer name: F.Cu top copper, B.Cu bottom copper, In<N>.Cu inner copper N."""
    if name == "F.Cu":
        return "Top copper"
    if name == "B.Cu":
        return "Bottom copper"
    m = re.fullmatch(r"In(\d+)\.Cu", name)
    return f"Inner copper {m.group(1)}" if m else name


def copper_layers(text):
    """Copper layer names of a board file, in the order of its layer table."""
    m = re.search(r"\(layers\s*\n(.*?)\n\t?\)", text, re.S)
    if not m:
        return []
    return [n for n in re.findall(r'\(\d+ "([^"]+\.Cu)"', m.group(1))]


def covers(on, name):
    """True when a layer list of a board item ('F.Cu', '*.Cu', 'F&B.Cu') holds the copper layer `name`."""
    if name in on or "*.Cu" in on:
        return True
    return any("&" in x and name.split(".")[0] in x.split(".")[0].split("&") for x in on)


def layer_items(text, layers, blocks):
    """{layer: number of tracks, vias, zones and pads on it}, counted in the board file."""
    count = {name: 0 for name in layers}

    def names(blk):
        m = re.search(r'\(layers?((?:\s+"[^"]+")+)\)', blk)
        return re.findall(r'"([^"]+)"', m.group(1)) if m else []

    for head in ("segment", "arc", "via", "zone", "pad"):
        for _ln, blk in blocks(text, head):
            on = names(blk)
            for name in layers:
                if covers(on, name):
                    count[name] += 1
    return count


def bom_tokens(ctx, bom):
    """Reference tokens of a parts list, as written ('R14-R22' stays one token)."""
    p = ctx.source_path(BOM_FILES[bom])
    if not p.is_file():
        return set()
    out = set()
    for r in csvread.read(p):
        out.update(csvread.split_refs(r["cells"].get("reference", "")))
    return out


def part_id_of(ref, bom, tokens):
    """'<bom>:<token>' for a reference: the token that is the reference, or the range token that holds it."""
    if ref in tokens:
        return f"{bom}:{ref}"
    m = re.fullmatch(r"([A-Za-z]+)(\d+)", ref)
    if not m:
        return None
    for t in tokens:
        r = re.fullmatch(r"([A-Za-z]+)(\d+)-(?:\1)?(\d+)", t)
        if r and r.group(1) == m.group(1) and int(r.group(2)) <= int(m.group(2)) <= int(r.group(3)):
            return f"{bom}:{t}"
    return None


def footprint_parts(text, bom, tokens, blocks):
    """Placed parts of a board file: reference, value, centre, size (courtyard, else pads), side."""
    out = []
    for _line, blk in blocks(text, "footprint"):
        ref = re.search(r'\(property "Reference" "([^"]*)"', blk)
        val = re.search(r'\(property "Value" "([^"]*)"', blk)
        at = re.search(r"\(at (-?[\d.]+) (-?[\d.]+)(?: (-?[\d.]+))?", blk)
        lay = re.search(r'^\(footprint\s+"[^"]*"[\s\S]*?\(layer "([^"]+)"\)', blk)
        if not (ref and at and lay):
            continue
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
        angle = float(at.group(3)) if at.group(3) else 0.0
        if round(angle / 90) % 2 == 1 and abs(angle % 90) < 1:
            w, h = h, w
        r = ref.group(1)
        value = (val.group(1) if val else "").strip()
        out.append({"ref": r, "part_id": part_id_of(r, bom, tokens), "value": value if value not in ("", "~") else None,
                    "x": float(at.group(1)), "y": float(at.group(2)), "w": round(w, 4), "h": round(h, 4),
                    "side": "bottom" if lay.group(1).startswith("B.") else "top"})
    return out


def stamp(path):
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")


def run_cli(cmd, timeout=180):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, str(e)
    return r.returncode == 0, (r.stderr or r.stdout or "").strip()


def one_board(ctx, group, path, cli, blocks, pcb_outline):
    """The entry of one board file."""
    rel = ctx.rel(path)
    m = SIZE_RX.search(path.name)
    size = f"US {m.group(1)}" if m else None
    bid = f"{group['id']}-us{m.group(1)}" if m else group["id"]
    entry = {"id": bid, "group": group["id"], "title": group["title"], "what": group["what"], "size_label": size,
             "file": rel, "file_time": stamp(path), "outline": None, "layers": [], "placements": [], "missing": [], "notes": [],
             "state": None}
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        entry["state"] = {"status": "not-checked", "words": f"the board file cannot be read: {e}", "violations": None,
                          "open_connections": None, "checked_at": None, "report": None, "report_lines": [], "source": pointer(rel, None)}
        return entry
    entry["outline"] = pcb_outline(text, rel)
    if entry["outline"] is None:
        entry["missing"].append("an outline on the Edge.Cuts layer of the board file")
    tokens = bom_tokens(ctx, group["bom"])
    entry["placements"] = footprint_parts(text, group["bom"], tokens, blocks)
    names = copper_layers(text)
    items = layer_items(text, names, blocks)
    for name in names:
        rec = {"id": name, "label": layer_label(name), "svg": None, "items": items.get(name, 0)}
        if cli:
            dst = ctx.out_path(f"board/{bid}/{name}.svg")
            ok, err = run_cli([cli, "pcb", "export", "svg", "--mode-single", "--layers", f"Edge.Cuts,{name}", "--page-size-mode", "2",
                               "--exclude-drawing-sheet", "-o", str(dst), str(path)])
            if ok and dst.is_file() and dst.stat().st_size > 0:
                rec["svg"] = f"board/{bid}/{name}.svg"
            else:
                if dst.exists():
                    dst.unlink()
                entry["notes"].append(f"kicad-cli could not draw {layer_label(name).lower()}: {err[:120]}")
        entry["layers"].append(rec)
    if not names:
        entry["missing"].append("copper layers in the board file")
    if not cli:
        entry["notes"].append("kicad-cli was not found ($KICAD_CLI, the KiCad app, PATH): no layer pictures and no rules check")

    # the rules check
    state = {"status": "not-checked", "words": "the rules check has not run", "violations": None, "open_connections": None,
             "checked_at": None, "report": None, "report_lines": [], "source": pointer(rel, None)}
    if cli:
        dst = ctx.out_path(f"board/{bid}/drc.rpt")
        ok, err = run_cli([cli, "pcb", "drc", "--severity-all", "--format", "report", "-o", str(dst), str(path)])
        parsed = parse_report(dst.read_text(encoding="utf-8", errors="replace")) if dst.is_file() else None
        if ok and parsed:
            v, o, lines = parsed
            created = CREATED_RX.search(dst.read_text(encoding="utf-8", errors="replace"))
            state.update({"status": "routed-checked" if v == 0 and o == 0 else "not-finished", "words": state_words(v, o),
                          "violations": v, "open_connections": o, "report": f"board/{bid}/drc.rpt", "report_lines": lines,
                          "checked_at": created.group(1).replace("T", " ")[:16] if created else None})
        else:
            state["words"] = f"the rules check did not give a report: {err[:120]}"
            if dst.exists():
                dst.unlink()
    entry["state"] = state
    # a board file older than the netlist it is built from
    if group["netlist"]:
        net = ctx.source_path(group["netlist"])
        if net.is_file() and net.stat().st_mtime > path.stat().st_mtime + 60:
            entry["notes"].append(f"The board file is from {stamp(path)}; its netlist {group['netlist']} is newer ({stamp(net)}).")
    return entry


def missing_board(group):
    where = group["glob"][0]
    return {"id": group["id"], "group": group["id"], "title": group["title"], "what": group["what"], "size_label": None, "file": None,
            "file_time": None, "outline": None, "layers": [], "placements": [], "missing": [where], "notes": [],
            "state": {"status": "not-checked", "words": f"the board file is not there: {where}", "violations": None,
                      "open_connections": None, "checked_at": None, "report": None, "report_lines": [], "source": None}}


def collect(ctx, blocks, pcb_outline):
    """[board entry] for every group; (entries, source files read)."""
    cli = schematic._tool()
    out, read = [], []
    for g in GROUPS:
        files = []
        for pat in g["glob"]:
            files += sorted(ctx.source_root.glob(pat))
        if not files:
            out.append(missing_board(g))
            continue
        for f in sorted(files, key=lambda p: [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", p.name)]):
            out.append(one_board(ctx, g, f, cli, blocks, pcb_outline))
            read.append(ctx.rel(f))
    return out, read
