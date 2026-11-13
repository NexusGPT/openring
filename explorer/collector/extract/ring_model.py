"""ring-model (ring-model.json, exterior.glb, internals.glb).

internals.glb: design/mech/thin/out/thin-inside.glb (one top-level node per placement row, its children named '<part>__<class>' kept), converted once to glTF Y-up
and meshopt-compressed. Its top-level node names (a child is never a part) must equal the placement.csv part names; when they differ the model file is
older or newer than the csv and the record is 'unparsed' (the message names the difference).
exterior.glb: the look in design/status.json look.picked, else the one in look.in_design (shown as
'in-design': a model that is not approved). With no design/status.json, or no model file, the status is
'not-picked' and there is no file. A look listed in look.rejected is never used. A look id '<folder>-<variant>' is design/look/<folder>/out/
ring-<variant>.glb, an id without a dash is design/look/<id>/out/ring.glb.
Compression: the gltf-transform of this explorer folder (node_modules/.bin); without it the models ship
uncompressed and the record says so in the manifest message. A model above GLB_MAX_MB is refused.
part_ids of an inside node: its placement reference when that is in design/bom.csv, else the ids whose
`model_names` in content/part-notes.json name it (read at collect time); none = [] and counted in the message.
Exterior nodes (every named node that holds a mesh) join `nodes` with the kind from collector/cad/exterior-kinds.json.
Axis convention: see collector/cad/glb.py and extract/placements.py.
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

import placements as plc  # noqa: E402
import screens  # noqa: E402
from cad import glb  # noqa: E402
from lib import csvread  # noqa: E402
from lib.errors import SourceError  # noqa: E402
from lib.source import find_line, pointer  # noqa: E402

RECORD = "ring-model"

STATUS = "design/status.json"
BOM = "design/bom.csv"
LOOK_DIR = "design/look"


def glb_max_mb():
    c = json.loads((HERE.parent.parent / "contract" / "schema" / "constants.json").read_text(encoding="utf-8"))
    return c["GLB_MAX_MB"]


def read_status(ctx):
    p = ctx.source_path(STATUS)
    if not p.is_file():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("not an object")
    except ValueError as e:
        raise SourceError(f"{STATUS} cannot be read: {e}", STATUS)
    return data


def look_file(look_id):
    folder, _, variant = look_id.partition("-")
    return f"{LOOK_DIR}/{folder}/out/ring-{variant}.glb" if variant else f"{LOOK_DIR}/{look_id}/out/ring.glb"


def line_of(ctx, rel, needle):
    p = ctx.source_path(rel)
    return find_line(p.read_text(encoding="utf-8"), needle) if p.is_file() else None


def pick_exterior(status):
    """(look_id, picked) or (None, False). A rejected look is never used."""
    look = (status or {}).get("look") or {}
    rejected = set(look.get("rejected") or [])
    if look.get("picked") and look["picked"] not in rejected:
        return look["picked"], True
    for i in look.get("in_design") or []:
        if i not in rejected:
            return i, False
    return None, False


def finish(ctx, src, name, notes):
    """Convert to Y-up, compress when the tool is there, check the size cap; returns the bundle file name."""
    js, binary = glb.read(src)
    glb.to_y_up(js)
    out = ctx.out_path(name)
    cap = glb_max_mb() * 1024 * 1024
    with tempfile.TemporaryDirectory() as td:
        plain = Path(td) / "plain.glb"
        glb.write(plain, js, binary)
        tool = ctx.explorer_dir / "node_modules" / ".bin" / "gltf-transform"
        done = False
        if tool.is_file():
            try:
                glb.compress(plain, out, tool, Path(td) / "gltf-transform.log")
                done = True
            except (glb.GlbError, OSError) as e:
                notes.append(f"{name}: compression failed ({e}); shipped uncompressed")
        else:
            notes.append(f"{name}: gltf-transform is not installed; shipped uncompressed")
        if not done:
            shutil.copyfile(plain, out)
    size = out.stat().st_size
    if size > cap:
        raise SourceError(f"{name} is {size / 1048576:.2f} MB, above GLB_MAX_MB {glb_max_mb()}", src.name)
    return name


def part_refs(ctx):
    p = ctx.source_path(BOM)
    if not p.is_file():
        return set()
    refs = set()
    for r in csvread.read(p):
        refs.update(csvread.split_refs(r["cells"].get("reference", "")))
    return refs


def notes_links(ctx):
    """{model node name: [part ids]} from the `model_names` of content/part-notes.json (the one place that mapping
    lives). {} when the file is absent or unreadable."""
    folder = getattr(ctx, "content_dir", None) or ctx.explorer_dir / "content"
    p = Path(folder) / "part-notes.json"
    if not p.is_file():
        return {}
    try:
        notes = json.loads(p.read_text(encoding="utf-8")).get("notes", {})
    except (ValueError, AttributeError):
        return {}
    out = {}
    for pid, n in notes.items():
        for name in (n or {}).get("model_names", []) if isinstance(n, dict) else []:
            out.setdefault(name, []).append(pid)
    return out


def extract(ctx):
    if not ctx.source_path(plc.CSV).is_file():
        return None, {"status": "missing", "source": [plc.CSV], "message": f"{plc.CSV} is not in the design folder."}
    if not ctx.source_path(plc.INSIDE_GLB).is_file():
        return None, {"status": "missing", "source": [plc.INSIDE_GLB],
                      "message": f"{plc.INSIDE_GLB} is not in the design folder."}
    rows = plc.read_rows(ctx)
    notes = []
    status = read_status(ctx)
    sources = [plc.CSV, plc.INSIDE_GLB]

    # internals
    inside = ctx.source_path(plc.INSIDE_GLB)
    js, _ = glb.read(inside)
    roots = glb.scene_roots(js)
    want, have = [r["name"] for r in rows], [js["nodes"][i].get("name", "") for i in roots]
    if set(want) != set(have) or len(have) != len(set(have)):
        miss, extra = sorted(set(want) - set(have)), sorted(set(have) - set(want))
        raise SourceError(f"{plc.INSIDE_GLB} and {plc.CSV} disagree: only in the csv {miss}, only in the model {extra}; "
                          "rebuild the inside model", [plc.INSIDE_GLB, plc.CSV])
    finish(ctx, inside, "internals.glb", notes)
    internals = {"file": "internals.glb", "node_count": len(have), "source": pointer(plc.INSIDE_GLB)}
    materials = js.get("materials", [])

    def is_blend(i):
        n = js["nodes"][i]
        if "mesh" in n and materials:
            mat = js["meshes"][n["mesh"]]["primitives"][0].get("material")
            if mat is not None and materials[mat].get("alphaMode") == "BLEND":
                return True
        return any(is_blend(c) for c in n.get("children", []))

    def descendants(i):
        out = []
        for c in js["nodes"][i].get("children", []):
            out.append(c)
            out += descendants(c)
        return out

    by_name = {js["nodes"][i].get("name", ""): i for i in roots}
    known_classes = set(json.loads((HERE.parent / "cad" / "part-classes.json").read_text(encoding="utf-8"))["classes"])
    unknown_classes = set()

    # nodes
    refs = part_refs(ctx)
    links = notes_links(ctx)
    nodes = []
    for r in rows:
        kind = "plain"
        if "lit area" in (r["note"] or ""):
            kind = "screen"
        elif is_blend(by_name[r["name"]]) and not r["metal"]:
            kind = "glass"
        elif r["metal"]:
            kind = "finish metal"
        ids = [f"ring:{r['reference']}"] if r["reference"] and r["reference"] in refs else []
        if not ids:
            ids = list(links.get(r["name"], []))
        node = {"name": r["name"], "kind": kind, "layer": r["layer"] or None, "part_ids": ids}
        kids = []
        for c in descendants(by_name[r["name"]]):
            cname = js["nodes"][c].get("name", "")
            if "__" not in cname:
                continue
            cls = cname.rsplit("__", 1)[1]
            if cls not in known_classes:
                unknown_classes.add(cls)
            kids.append({"name": cname, "class": cls})
        if kids:
            node["children"] = kids
        nodes.append(node)
    if unknown_classes:
        notes.append(f"unknown child class(es) {sorted(unknown_classes)}; passed on as written")
    unlinked = [n["name"] for n in nodes if not n["part_ids"]]
    if unlinked:
        notes.append(f"{len(unlinked)} inside node(s) link to no parts-list line: {', '.join(unlinked)}")

    # block: the largest part by volume is the ring's block
    big = max(rows, key=lambda r: r["size"]["x"] * r["size"]["y"] * r["size"]["z"])
    block = {"size_mm": dict(big["size"]), "source": pointer(plc.CSV, big["line"])}

    # exterior
    look_id, picked = pick_exterior(status)
    exterior = {"status": "not-picked", "look_id": None, "file": None, "source": None}
    ext_band = None
    ext_nodes = []
    if look_id:
        rel = look_file(look_id)
        exterior["look_id"] = look_id
        exterior["source"] = pointer(STATUS, line_of(ctx, STATUS, '"in_design"') if not picked else line_of(ctx, STATUS, '"picked"'))
        if ctx.source_path(rel).is_file():
            ejs, _ = glb.read(ctx.source_path(rel))
            finish(ctx, ctx.source_path(rel), "exterior.glb", notes)
            exterior.update(file="exterior.glb", source=pointer(rel))
            sources.append(rel)
            for i, n in enumerate(ejs["nodes"]):
                if n.get("name") == "band" and "mesh" in n:
                    ex = glb.accessor_extent(ejs, i, 0)
                    if ex:
                        ext_band = (round(ex[1] - ex[0], 3), pointer(rel))
            exterior["status"] = "picked" if picked else "in-design"
            ext_nodes = [n["name"] for n in ejs["nodes"] if "mesh" in n and n.get("name")]
        else:
            exterior["status"] = "absent"
            notes.append(f"the model file of look {look_id} is not at {rel}")
    if status is not None:
        sources.append(STATUS)

    # exterior nodes: kinds from the collector's table (the design folder holds none); a name the table lacks is plain
    table = json.loads((HERE.parent / "cad" / "exterior-kinds.json").read_text(encoding="utf-8"))["kinds"]
    listed = {n["name"] for n in nodes}
    unknown = []
    for name in ext_nodes:
        if name in listed:
            continue
        if name not in table:
            unknown.append(name)
        nodes.append({"name": name, "kind": table.get(name, "plain"), "layer": None, "part_ids": []})
        listed.add(name)
    if unknown:
        notes.append(f"exterior node(s) {unknown} are not in collector/cad/exterior-kinds.json; shown as plain")

    states = screens.states(ctx)
    screens.attach_pictures(ctx, states, notes)
    data = {
        "design_version": (status or {}).get("design_version"),
        "exterior": exterior, "internals": internals, "nodes": nodes, "block": block,
        "band": screens.band(ctx, rows, ext_band),
        "screens": {"rect": screens.rect(ctx, rows), "states": states},
    }
    sources += [screens.FIRMWARE, screens.ENVELOPE, screens.MANIFEST]
    sources = [s for s in dict.fromkeys(sources) if ctx.source_path(s).is_file()]
    st = {"status": "ok", "source": sources}
    if notes:
        st["message"] = "; ".join(notes)
    return data, st
