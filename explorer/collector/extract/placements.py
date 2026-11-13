"""part-placements (placements.json): where every part of the inside model sits, and the layers the ring opens into.

Sources (read at collect time, no count or name held here): design/mech/thin/placement.csv (one row per part:
part, reference, layer, x, y, z, size_x, size_y, size_z, angle_deg, metal, note) and design/mech/thin/layers.json
(the layers, top to bottom, each with its explode direction).

Coordinates stay in DESIGN coordinates, as in the CSV: x along the finger (+ fingertip), y across (+ thumb),
z up, mm, origin at the centre of the block's underside. Only the GLB files are converted to glTF Y-up (see
collector/cad/glb.py); a consumer maps a record vector (x, y, z) to the GLB's space as (x, z, -y).
Layers: `order` 0 is the bottom layer; layers.json lists them top to bottom, so the order is its reverse.
z_min / z_max of a layer: the range of z over its parts (centre -/+ half of size_z).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lib import csvread  # noqa: E402
from lib.errors import SourceError  # noqa: E402
from lib.source import pointer  # noqa: E402

RECORD = "part-placements"

INSIDE_DIR = "design/mech/thin"
CSV = f"{INSIDE_DIR}/placement.csv"
LAYERS = f"{INSIDE_DIR}/layers.json"
INSIDE_GLB = f"{INSIDE_DIR}/out/thin-inside.glb"
COLUMNS = ["part", "reference", "layer", "x", "y", "z", "size_x", "size_y", "size_z", "angle_deg", "metal", "note"]


def _num(cell, col, line):
    try:
        return float(cell)
    except ValueError:
        raise SourceError(f"{CSV} line {line}: {col} {cell!r} is not a number", CSV)


def read_rows(ctx):
    """[{name, reference, layer, centre{x,y,z}, size{x,y,z}, angle, metal, note, line}] from placement.csv."""
    path = ctx.source_path(CSV)
    rows = csvread.read(path, COLUMNS)
    out, seen = [], set()
    for r in rows:
        c, ln = r["cells"], r["line"]
        name = c["part"].strip()
        if not name:
            raise SourceError(f"{CSV} line {ln}: a row has no part name", CSV)
        if name in seen:
            raise SourceError(f"{CSV} line {ln}: part name {name!r} appears twice", CSV)
        seen.add(name)
        angle = c["angle_deg"].strip()
        out.append({
            "name": name, "reference": c["reference"].strip(), "layer": c["layer"].strip(), "line": ln,
            "centre": {k: _num(c[k], k, ln) for k in ("x", "y", "z")},
            "size": {k: _num(c[f"size_{k}"], f"size_{k}", ln) for k in ("x", "y", "z")},
            "angle": _num(angle, "angle_deg", ln) if angle else None,
            "metal": c["metal"].strip().lower() in ("true", "1", "yes"),
            "note": c["note"].strip() or None,
        })
    return out


def read_layers(ctx):
    """The layers.json layers (top to bottom) or None when the file is absent."""
    path = ctx.source_path(LAYERS)
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        layers = data["layers"]
        assert isinstance(layers, list)
    except (ValueError, KeyError, AssertionError) as e:
        raise SourceError(f"{LAYERS} cannot be read: {e}", LAYERS)
    return layers


def explode_of(layer):
    """The record's `explode` for one layers.json layer: a direction {x,y,z}, 'radial', or None."""
    ex = layer.get("explode")
    if not ex:
        return None
    mode = ex.get("mode")
    if mode == "radial":
        return "radial"
    if mode == "axis":
        d = ex.get("dir")
        if not (isinstance(d, list) and len(d) == 3):
            raise SourceError(f"{LAYERS}: layer {layer.get('name')!r} has an axis explode without a 3-number dir", LAYERS)
        return {"x": float(d[0]), "y": float(d[1]), "z": float(d[2])}
    raise SourceError(f"{LAYERS}: layer {layer.get('name')!r} has explode mode {mode!r}, which this reader does not know", LAYERS)


def rotation_text(angle):
    if angle is None:
        return "none"
    return f"{angle:g} deg around the band axis, measured from the top, plus toward the thumb"


def build(ctx):
    rows = read_rows(ctx)
    if not rows:
        raise SourceError(f"{CSV} has no rows", CSV)
    declared = read_layers(ctx)
    row_layers = []
    for r in rows:
        if r["layer"] not in row_layers:
            row_layers.append(r["layer"])
    if declared is None:
        top_to_bottom = [{"name": n} for n in row_layers]
        layer_src = pointer(CSV)
    else:
        top_to_bottom = [dict(layer) for layer in declared]
        known = {layer.get("name") for layer in top_to_bottom}
        extra = [n for n in row_layers if n not in known]
        if extra:
            raise SourceError(f"{CSV} uses layer(s) {extra} that {LAYERS} does not list", [CSV, LAYERS])
        layer_src = pointer(LAYERS)
    layers = []
    for order, layer in enumerate(reversed(top_to_bottom)):
        members = [r for r in rows if r["layer"] == layer.get("name")]
        if not members:
            continue
        zs = [(r["centre"]["z"] - r["size"]["z"] / 2, r["centre"]["z"] + r["size"]["z"] / 2) for r in members]
        item = {"id": layer["name"], "label": layer["name"], "order": 0, "z_min": min(a for a, _ in zs),
                "z_max": max(b for _, b in zs), "source": layer_src}
        ex = explode_of(layer)
        if ex is not None:
            item["explode"] = ex
        layers.append(item)
    for i, item in enumerate(layers):
        item["order"] = i
    placements = [{
        "name": r["name"], "centre": r["centre"], "size": r["size"], "rotation": rotation_text(r["angle"]),
        "metal": r["metal"], "layer": r["layer"], "zone": None, "note": r["note"], "source": pointer(CSV, r["line"]),
    } for r in rows]
    return {"layers": layers, "placements": placements}


def extract(ctx):
    if not ctx.source_path(CSV).is_file():
        return None, {"status": "missing", "source": [CSV], "message": f"{CSV} is not in the design folder."}
    data = build(ctx)
    src = [CSV] + ([LAYERS] if ctx.source_path(LAYERS).is_file() else [])
    return data, {"status": "ok", "source": src}
