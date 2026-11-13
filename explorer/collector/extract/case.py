"""case (case/index.json + case/case.glb): the charging case's model, numbers, parts and supplier items.

Sources, read at collect time (no case value is held here):
  design/case/out/parts/*.step     one node per file stem. Of the ring variants named ring_US<n>_*, only the smallest n
                                   is seated in the model (the case holds every size; one is shown). The lid is its own
                                   node; the hinge axis is the long axis of the node whose stem starts with 'hinge'.
  design/case/out/case_size.txt    the closed outer size (the line with "X <n> mm x Y <n> mm x Z <n> mm").
  design/case/case-architecture.md facts by their sentences (cell capacity, transfer minutes per recorded hour, ring
                                   charge time, charges per case charge), and section 8 (supplier items).
  design/case/case-bom.csv         the case parts: ids `case:<ref>`, the lines themselves live in parts.json.
  design/status.json               areas.case.why: the plain reason when the case is older than the design.
The model is made with build123d (design venv) from the STEP files, converted to glTF Y-up, meshopt-compressed when the
gltf-transform tool is installed, and held under GLB_MAX_MB. Version: the file says "Built against ... version <X>";
the runner turns that against the design's current version into the stale state.
Hinge point and axis are in DESIGN coordinates (Z up), like every record number; the GLB itself is Y-up.
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import case_links  # noqa: E402  (a peer helper: the links between solids, lines and boards)

RECORD = "case"

CASE_DIR = "design/case"
ARCH = f"{CASE_DIR}/case-architecture.md"
BOM = f"{CASE_DIR}/case-bom.csv"
SIZE = f"{CASE_DIR}/out/case_size.txt"
STEP_DIR = f"{CASE_DIR}/out/parts"
STATUS = "design/status.json"
DESIGN_DOC = "design/architecture.md"
GLB_NAME = "case/case.glb"
NUM = r"(\d+(?:\.\d+)?)"

# fact id, label, unit, regex on one line of the case architecture (group 1 = the number), value kind
FACTS = [
    ("case-cell", "Case cell capacity", "mAh", re.compile(r"\bcell " + NUM + r" mAh"), "number"),
    ("case-transfer", "Transfer time", "min per recorded hour",
     re.compile(NUM + r" min per recorded hour\. This is the planning figure"), "number"),
    ("case-ring-charge", "One ring charge takes", "min",
     re.compile(r"In the " + NUM + r" minutes a ring charge takes"), "number"),
    ("case-copied-per-charge", "Recorded hours copied during one ring charge", "h",
     re.compile(r"minutes a ring charge takes, the case copies " + NUM + r" recorded hours"), "number"),
    ("case-charges", "Ring charges from one full case cell", "charges",
     re.compile(r"Chosen " + NUM + r" mAh: " + NUM + r" charges"), "number2"),
]


def glb_max_mb():
    c = json.loads((HERE.parent.parent / "contract" / "schema" / "constants.json").read_text(encoding="utf-8"))
    return c["GLB_MAX_MB"]


def design_python(ctx):
    for cand in (ctx.design_dir / ".venv" / "bin" / "python", ctx.explorer_dir.parent / "design" / ".venv" / "bin" / "python"):
        if cand.is_file():
            return cand
    return None


# ---------------------------------------------------------------- model

def chosen_steps(folder):
    """STEP files to seat: every file, except ring variants other than the smallest size."""
    files = sorted(Path(folder).glob("*.step"))
    sizes = {}
    for f in files:
        m = re.match(r"ring_US(\d+)_", f.stem)
        if m:
            sizes[f] = int(m.group(1))
    keep = min(sizes.values()) if sizes else None
    return [f for f in files if f not in sizes or sizes[f] == keep]


def build_model(steps, out_glb, out_json):
    """build123d part: one labelled child per STEP file; writes the GLB and the bounding boxes (design mm)."""
    from build123d import Compound, export_gltf, import_step  # noqa: PLC0415

    kids, boxes = [], {}
    for f in steps:
        shape = import_step(str(f))
        shape.label = f.stem
        bb = shape.bounding_box()
        boxes[f.stem] = {"min": [bb.min.X, bb.min.Y, bb.min.Z], "max": [bb.max.X, bb.max.Y, bb.max.Z]}
        kids.append(shape)
    export_gltf(Compound(children=kids, label="case"), str(out_glb), binary=True)
    Path(out_json).write_text(json.dumps(boxes), encoding="utf-8")


def make_model(ctx, steps, notes):
    """(glb info dict or None). Runs build123d here, or in the design venv's python when this one lacks it."""
    from cad import glb  # noqa: PLC0415
    import ring_model  # noqa: PLC0415
    from lib.errors import SourceError  # noqa: PLC0415

    with tempfile.TemporaryDirectory() as td:
        raw, side = Path(td) / "raw.glb", Path(td) / "boxes.json"
        try:
            import build123d  # noqa: F401, PLC0415
            build_model(steps, raw, side)
        except ImportError:
            py = design_python(ctx)
            if py is None:
                notes.append("no python with build123d was found: the case has no 3D model")
                return None
            r = subprocess.run([str(py), str(Path(__file__).resolve()), "--build", str(raw), str(side), *map(str, steps)],
                               capture_output=True, text=True, timeout=600)
            if r.returncode != 0:
                raise SourceError("the STEP files could not be turned into a model: " + (r.stderr.strip().splitlines() or ["?"])[-1],
                                  STEP_DIR)
        boxes = json.loads(side.read_text(encoding="utf-8"))
        js, _ = glb.read(raw)
        have = set(glb.node_names(js))
        lost = sorted(f.stem for f in steps if f.stem not in have)
        if lost:
            raise SourceError(f"the model lost the part name(s) {lost[:5]}", STEP_DIR)
        name = ring_model.finish(ctx, raw, GLB_NAME, notes)
    return {"file": name, "boxes": boxes}


def hinge_of(boxes):
    for stem, b in sorted(boxes.items()):
        if stem.startswith("hinge"):
            size = [b["max"][i] - b["min"][i] for i in range(3)]
            i = max(range(3), key=lambda k: size[k])
            axis = [0.0, 0.0, 0.0]
            axis[i] = 1.0
            c = [(b["max"][k] + b["min"][k]) / 2 for k in range(3)]
            return {"point": dict(zip("xyz", c)), "axis": dict(zip("xyz", axis))}
    return None


def link_ids(stem, refs):
    """Case part ids a node stands for: its stem's first token when it is a reference of the case parts list (a range
    token such as P1-P4 covers the numbers in it)."""
    out = []
    for tok in re.split(r"[_]", stem):
        for r in refs:
            if r == tok or _in_range(r, tok):
                out.append(f"case:{r}")
        if out:
            break
    return sorted(set(out))


def _in_range(token, ref):
    m = re.match(r"^([A-Za-z]+)(\d+)-(?:[A-Za-z]+)?(\d+)$", token)
    n = re.match(r"^([A-Za-z]+)(\d+)$", ref)
    return bool(m and n and m.group(1) == n.group(1) and int(m.group(2)) <= int(n.group(2)) <= int(m.group(3)))


# ---------------------------------------------------------------- text sources

def case_refs(ctx):
    from lib import csvread  # noqa: PLC0415

    p = ctx.source_path(BOM)
    if not p.is_file():
        return []
    out = []
    for r in csvread.read(p, ["reference"]):
        out += csvread.split_refs(r["cells"].get("reference", ""))
    return out


def fmt(v):
    return f"{float(v):.3f}".rstrip("0").rstrip(".")


def read_facts(ctx, notes):
    from lib.source import pointer  # noqa: PLC0415

    facts = []
    p = ctx.source_path(SIZE)
    if p.is_file():
        for i, ln in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            m = re.search(r"X " + NUM + r" mm x Y " + NUM + r" mm x Z " + NUM + r" mm", ln)
            if m:
                facts.append({"id": "case-size", "label": "Closed case outer size",
                              "value": " x ".join(m.groups()), "unit": "mm", "source": pointer(SIZE, i)})
                break
        else:
            notes.append(f"{SIZE} has no line 'X <n> mm x Y <n> mm x Z <n> mm': no size fact")
    else:
        notes.append(f"{SIZE} is not there: no size fact")
    a = ctx.source_path(ARCH)
    if a.is_file():
        lines = a.read_text(encoding="utf-8").splitlines()
        for fid, label, unit, rx, kind in FACTS:
            for i, ln in enumerate(lines, 1):
                m = rx.search(ln)
                if m:
                    if kind == "number2":  # "<mAh>: <charges>": the second number is the fact
                        v = m.group(2)
                    else:
                        v = m.group(1)
                    facts.append({"id": fid, "label": label, "value": float(v) if "." in v else int(v), "unit": unit,
                                  "source": pointer(ARCH, i)})
                    break
            else:
                notes.append(f"no sentence for the fact '{label}' in {ARCH}")
    else:
        notes.append(f"{ARCH} is not there: no figures")
    return facts


def read_supplier_items(ctx, notes):
    from lib import md  # noqa: PLC0415
    from lib.source import pointer  # noqa: PLC0415

    a = ctx.source_path(ARCH)
    if not a.is_file():
        return []
    text = a.read_text(encoding="utf-8")
    t = md.table_after_heading(text, r"^\d+\.\s+Items only a supplier can close", level=2)
    if t is None:
        notes.append(f"{ARCH} has no table 'Items only a supplier can close'")
        return []
    cols = [c.lower() for c in t["columns"]]
    need = ("#", "item", "who", "what to ask")
    if any(n not in cols for n in need):
        notes.append(f"the supplier table of {ARCH} lacks a column of {need}")
        return []
    ix = {n: cols.index(n) for n in need}
    out = []
    for cells, line in zip(t["rows"], t["row_lines"]):
        vals = {n: cells[ix[n]].strip() for n in need}
        if not all(vals.values()):
            notes.append(f"{ARCH} line {line}: a supplier row has an empty cell; left out")
            continue
        out.append({"id": vals["#"], "item": vals["item"], "who": vals["who"], "ask": vals["what to ask"],
                    "section": f"section {_section_number(text, t['line'])} of {Path(ARCH).name}",
                    "source": pointer(ARCH, line)})
    return out


def _section_number(text, line):
    last = "?"
    for i, ln in enumerate(text.splitlines(), 1):
        if i > line:
            break
        m = re.match(r"^#{1,6}\s+(\d+(?:\.\d+)*)\.?\s", ln)
        if m:
            last = m.group(1)
    return last


def versions(ctx):
    from lib import version  # noqa: PLC0415

    basis = current = None
    a = ctx.source_path(ARCH)
    if a.is_file():
        m = re.search(r"Built against\s+`?[\w/.-]*architecture\.md`?\s+version\s+([A-Z]{1,2}\d+(?:-[A-Za-z]+)?)",
                      a.read_text(encoding="utf-8"))
        basis = m.group(1) if m else None
    d = ctx.source_path(DESIGN_DOC)
    if d.is_file():
        current = version.read_own(d.read_text(encoding="utf-8"))
    return basis, current


def stale_reason(ctx):
    p = ctx.source_path(STATUS)
    try:
        why = json.loads(p.read_text(encoding="utf-8"))["areas"]["case"]["why"]
        return why if isinstance(why, str) and why.strip() else None
    except (OSError, ValueError, KeyError, TypeError):
        return None


def extract(ctx):
    from lib import version  # noqa: PLC0415
    from lib.errors import SourceError  # noqa: PLC0415

    case_dir = ctx.source_path(CASE_DIR)
    if not case_dir.is_dir():
        return None, {"status": "missing", "source": [CASE_DIR], "message": f"{CASE_DIR} is not there."}
    notes, sources = [], [CASE_DIR]
    refs = case_refs(ctx)
    facts = read_facts(ctx, notes)
    items = read_supplier_items(ctx, notes)
    sources += [f for f in (SIZE, ARCH, BOM) if ctx.source_path(f).is_file()]

    glb_info, nodes, links = None, [], {}
    steps = chosen_steps(ctx.source_path(STEP_DIR)) if ctx.source_path(STEP_DIR).is_dir() else []
    if steps:
        model = make_model(ctx, steps, notes)
        if model:
            lid = next((f.stem for f in steps if f.stem == "lid"), None)
            if lid is None:
                raise SourceError(f"{STEP_DIR} has no lid.step: the lid must be its own node", STEP_DIR)
            names = [f.stem for f in steps]
            extra = case_links.build(ctx, names, notes)
            by_name = {x["name"]: x["part_ids"] for x in extra.get("links", [])}
            nodes = [{"name": n, "part_ids": by_name[n] if n in by_name else link_ids(n, refs)} for n in names]
            glb_info = {"file": model["file"], "lid_node": lid, "hinge": hinge_of(model["boxes"]), "nodes": nodes}
            links = {k: v for k, v in extra.items() if k != "links"}
            if glb_info["hinge"] is None:
                notes.append("no hinge part among the STEP files: the lid has no hinge axis")
    else:
        notes.append(f"no STEP files in {STEP_DIR}: the case has no 3D model")

    basis, current = versions(ctx)
    if basis is None:
        notes.append(f"{ARCH} does not say which design version it was built against")
    msg = "; ".join(notes)
    if version.is_stale(basis, current):
        why = stale_reason(ctx)
        msg = " ".join(x for x in (why, msg) if x)
    data = {"glb": glb_info, "facts": facts, "part_ids": [f"case:{r}" for r in refs], "supplier_items": items}
    if links:
        data.update(links)
        data["model"] = case_links.model_source(ctx)
        data["refit"] = case_links.refit_note(ctx)
        sources += [f for f in (case_links.PARAMS, case_links.DECISIONS, *case_links.BOARD_FILES) if ctx.source_path(f).is_file()]
    return data, {"status": "ok", "source": sources, "basis_version": basis, "current_version": current,
                  "message": msg or None}


if __name__ == "__main__":
    if len(sys.argv) > 4 and sys.argv[1] == "--build":
        build_model([Path(a) for a in sys.argv[4:]], sys.argv[2], sys.argv[3])
