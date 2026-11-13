"""collector-model: placements.json, ring-model.json, internals.glb, exterior.glb from small made-up design files."""
import json
import struct
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "extract"))

from cad import glb  # noqa: E402
from conftest import read_json, run_collector  # noqa: E402

SHA = "a" * 40
HEAD = "part,reference,layer,x,y,z,size_x,size_y,size_z,angle_deg,metal,note\n"
CSV = HEAD + (
    "shell,,body,0,0,1,10,6,2,,True,block 10 x 6 x 2 plus band 3.5 x 2\n"
    "top,G1,glass,0,0,2.1,9,5,0.2,,False,\n"
    "lcd,D1,screen,0,0,1.5,9,5,0.4,,True,\"lit area 7 (X) x 4 (Y) centred X 0.5 Y -0.25 (note)\"\n"
    "cpu,U1,board,1,1,0.8,2,2,0.5,,True,\n"
    "cell,,band,0,0,-5,4,8,0.5,90,False,curved\n"
)
LAYERS = {"layers": [
    {"name": "glass", "parts": ["top"], "explode": {"mode": "axis", "dir": [0, 0, 1], "distance": 5}},
    {"name": "screen", "parts": ["lcd"], "explode": {"mode": "axis", "dir": [0, 0, 1], "distance": 4}},
    {"name": "board", "parts": ["cpu"], "explode": {"mode": "axis", "dir": [0, 0, 1], "distance": 3}},
    {"name": "band", "parts": ["cell"], "explode": {"mode": "radial", "distance": 2, "part_dirs": {}}},
    {"name": "body", "parts": ["shell"], "explode": {"mode": "axis", "dir": [0, 0, -1], "distance": 1}},
]}
FIRMWARE = """# Firmware

## 3. Screens

### 3.3 Screen

| Screen | Shown in | Fields, top to bottom |
|---|---|---|
| SCR_A | `IDLE` | time (HH:MM), battery % with icon, "Ready" |
| SCR_B | `BUSY` | red dot and "REC", timer HH:MM:SS, storage left |

Next.
"""
ENVELOPE = 'LIMITS = {"band_inner_d_size9": 17.5, "screen_active_x": 6.0, "screen_active_y": 3.0}\nSCREEN_CX, SCREEN_CY = 0.2, -0.1\n'
BOM = "item,reference,quantity\nGlass,G1,1\nDisplay,D1,1\nChip,U1,1\n"


def make_glb(path, names, roots_rotated=False, blend=()):
    pos = struct.pack("<9f", 0, 0, 0, 1, 0, 0, 0, 1, 0)
    nodes = [{"name": n, "mesh": i} for i, n in enumerate(names)]
    scene_nodes = list(range(len(names)))
    if roots_rotated:
        nodes = [{"name": "root", "children": list(range(1, len(names) + 1)), "rotation": list(glb.ROT_Z_UP_TO_Y_UP)}] + [
            {"name": n, "mesh": i} for i, n in enumerate(names)]
        scene_nodes = [0]
    js = {
        "asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": scene_nodes}], "nodes": nodes,
        "meshes": [{"name": n, "primitives": [{"attributes": {"POSITION": 0}, "material": 1 if n in blend else 0}]} for n in names],
        "materials": [{"name": "solid"}, {"name": "clear", "alphaMode": "BLEND"}],
        "accessors": [{"bufferView": 0, "componentType": 5126, "count": 3, "type": "VEC3", "min": [0, 0, 0], "max": [1, 1, 0]}],
        "bufferViews": [{"buffer": 0, "byteLength": 36}], "buffers": [{"byteLength": 36}],
    }
    glb.write(path, js, pos)


def make_tree_glb(path, parts, blend_children=()):
    """parts = {part: [classes]}: one top-level node per part, one mesh child '<part>__<class>' per class."""
    pos = struct.pack("<9f", 0, 0, 0, 1, 0, 0, 0, 1, 0)
    nodes, meshes, roots = [], [], []
    for part, classes in parts.items():
        idx = len(nodes)
        roots.append(idx)
        nodes.append({"name": part, "children": list(range(idx + 1, idx + 1 + len(classes)))})
        for cls in classes:
            cname = f"{part}__{cls}"
            nodes.append({"name": cname, "mesh": len(meshes)})
            meshes.append({"name": cname, "primitives": [{"attributes": {"POSITION": 0}, "material": 1 if cname in blend_children else 0}]})
    js = {"asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": roots}], "nodes": nodes, "meshes": meshes,
          "materials": [{"name": "solid"}, {"name": "clear", "alphaMode": "BLEND"}],
          "accessors": [{"bufferView": 0, "componentType": 5126, "count": 3, "type": "VEC3", "min": [0, 0, 0], "max": [1, 1, 0]}],
          "bufferViews": [{"buffer": 0, "byteLength": 36}], "buffers": [{"byteLength": 36}]}
    glb.write(path, js, pos)


def write(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


@pytest.fixture
def design(tmp_path):
    root = tmp_path / "src"
    d = root / "design"
    write(root, "design/mech/thin/placement.csv", CSV)
    write(root, "design/mech/thin/layers.json", json.dumps(LAYERS))
    for sub in ("mech/thin/out", "look/q/out"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    make_tree_glb(d / "mech/thin/out/thin-inside.glb", {"shell": ["metal"], "top": ["glass"], "lcd": ["screen", "pcb"],
                  "cpu": ["chip", "mark", "weird"], "cell": ["cell"]}, blend_children=("top__glass",))
    write(root, "design/firmware.md", FIRMWARE)
    write(root, "design/look/shared/envelope.py", ENVELOPE)
    write(root, "design/bom.csv", BOM)
    write(root, "design/status.json", json.dumps({"design_version": "T1", "look": {"picked": None, "rejected": ["old"], "in_design": ["q-one"]}}))
    make_glb(d / "look/q/out/ring-one.glb", ["body", "band", "glass", "lcd", "mystery"], roots_rotated=True)
    return root


def collect(design, tmp_path):
    out = tmp_path / "out"
    r = run_collector("--source", str(design), "--out", str(out), "--commit", SHA)
    return r, out


def entry(out, rec):
    return read_json(out / "manifest.json")["records"][rec]


def test_internals_node_set_equals_placement_parts(design, tmp_path):
    r, out = collect(design, tmp_path)
    assert r.returncode == 0, r.stderr
    assert entry(out, "ring-model")["status"] == "ok", entry(out, "ring-model")
    js, _ = glb.read(out / "internals.glb")
    csv_parts = {p["name"] for p in read_json(out / "placements.json")["placements"]}
    top = {js["nodes"][i]["name"] for i in glb.scene_roots(js)}
    assert top == csv_parts == {"shell", "top", "lcd", "cpu", "cell"}
    model = read_json(out / "ring-model.json")
    assert model["internals"]["node_count"] == 5
    assert csv_parts <= {n["name"] for n in model["nodes"]}  # the exterior nodes join them


def test_layers_ordered_bottom_to_top_with_explode(design, tmp_path):
    _, out = collect(design, tmp_path)
    layers = read_json(out / "placements.json")["layers"]
    assert [x["id"] for x in layers] == ["body", "band", "board", "screen", "glass"]
    assert [x["order"] for x in layers] == [0, 1, 2, 3, 4]
    assert layers[0]["explode"] == {"x": 0.0, "y": 0.0, "z": -1.0}
    assert layers[1]["explode"] == "radial"
    glass = layers[4]
    assert glass["z_min"] == pytest.approx(2.0) and glass["z_max"] == pytest.approx(2.2)


def test_placement_values_come_from_the_file(design, tmp_path):
    _, out = collect(design, tmp_path)
    pl = {p["name"]: p for p in read_json(out / "placements.json")["placements"]}
    assert pl["cpu"]["centre"] == {"x": 1.0, "y": 1.0, "z": 0.8} and pl["cpu"]["metal"] is True
    assert pl["cell"]["rotation"].startswith("90 deg") and pl["shell"]["rotation"] == "none"
    assert pl["cpu"]["source"] == {"file": "design/mech/thin/placement.csv", "line": 5}


def test_internals_glb_is_converted_to_y_up_once(design, tmp_path):
    _, out = collect(design, tmp_path)
    js, _ = glb.read(out / "internals.glb")
    for r in glb.scene_roots(js):
        assert js["nodes"][r]["rotation"] == pytest.approx(list(glb.ROT_Z_UP_TO_Y_UP))
    # the exterior already carries the rotation on its root: not applied a second time
    ejs, _ = glb.read(out / "exterior.glb")
    assert ejs["nodes"][glb.scene_roots(ejs)[0]]["rotation"] == pytest.approx(list(glb.ROT_Z_UP_TO_Y_UP))


def test_exterior_in_design_is_not_approved(design, tmp_path):
    _, out = collect(design, tmp_path)
    ext = read_json(out / "ring-model.json")["exterior"]
    assert ext["status"] == "in-design" and ext["look_id"] == "q-one" and ext["file"] == "exterior.glb"
    assert (out / "exterior.glb").is_file()


def test_exterior_picked(design, tmp_path):
    write(design, "design/status.json", json.dumps({"look": {"picked": "q-one", "rejected": [], "in_design": []}}))
    _, out = collect(design, tmp_path)
    assert read_json(out / "ring-model.json")["exterior"]["status"] == "picked"


def test_rejected_look_is_never_shown(design, tmp_path):
    write(design, "design/status.json", json.dumps({"look": {"picked": None, "rejected": ["q-one"], "in_design": ["q-one"]}}))
    _, out = collect(design, tmp_path)
    ext = read_json(out / "ring-model.json")["exterior"]
    assert ext == {"status": "not-picked", "look_id": None, "file": None, "source": None}
    assert not (out / "exterior.glb").exists()


def test_without_status_json_exterior_is_not_picked_and_run_exits_0(design, tmp_path):
    (design / "design/status.json").unlink()
    r, out = collect(design, tmp_path)
    assert r.returncode == 0
    ext = read_json(out / "ring-model.json")["exterior"]
    assert ext["status"] == "not-picked" and ext["file"] is None
    assert entry(out, "ring-model")["status"] == "ok"
    assert not (out / "exterior.glb").exists()


def test_every_glb_in_the_bundle_is_within_the_cap(design, tmp_path):
    _, out = collect(design, tmp_path)
    cap = json.loads((Path(__file__).resolve().parents[3] / "contract/schema/constants.json").read_text())["GLB_MAX_MB"]
    files = list(out.rglob("*.glb"))
    assert files
    assert all(f.stat().st_size <= cap * 1024 * 1024 for f in files)


def test_model_larger_than_the_cap_is_refused(design, tmp_path, monkeypatch):
    import ring_model

    monkeypatch.setattr(ring_model, "glb_max_mb", lambda: 0.00001)
    from lib.errors import SourceError

    class Ctx:
        explorer_dir = tmp_path / "none"

        def out_path(self, rel):
            return tmp_path / rel

    with pytest.raises(SourceError, match="GLB_MAX_MB"):
        ring_model.finish(Ctx(), design / "design/mech/thin/out/thin-inside.glb", "x.glb", [])


def test_model_and_csv_that_disagree_make_the_record_unparsed(design, tmp_path):
    make_tree_glb(design / "design/mech/thin/out/thin-inside.glb", {"shell": ["metal"], "top": ["glass"], "lcd": ["screen"], "cpu": ["chip"], "extra": ["metal"]})
    r, out = collect(design, tmp_path)
    assert r.returncode == 0
    e = entry(out, "ring-model")
    assert e["status"] == "unparsed" and "extra" in e["message"] and "cell" in e["message"]
    assert not (out / "ring-model.json").exists()


def test_layer_missing_from_layers_json_is_unparsed(design, tmp_path):
    bad = dict(LAYERS, layers=LAYERS["layers"][:-1])
    write(design, "design/mech/thin/layers.json", json.dumps(bad))
    _, out = collect(design, tmp_path)
    e = entry(out, "part-placements")
    assert e["status"] == "unparsed" and "body" in e["message"]


def test_unknown_explode_mode_is_unparsed(design, tmp_path):
    bad = json.loads(json.dumps(LAYERS))
    bad["layers"][0]["explode"] = {"mode": "spiral"}
    write(design, "design/mech/thin/layers.json", json.dumps(bad))
    _, out = collect(design, tmp_path)
    assert entry(out, "part-placements")["status"] == "unparsed"


def test_no_layers_json_layers_come_from_the_csv(design, tmp_path):
    (design / "design/mech/thin/layers.json").unlink()
    _, out = collect(design, tmp_path)
    layers = read_json(out / "placements.json")["layers"]
    assert {x["id"] for x in layers} == {"body", "glass", "screen", "board", "band"}
    assert all("explode" not in x for x in layers)


def test_missing_placement_csv_is_missing_and_exit_0(design, tmp_path):
    (design / "design/mech/thin/placement.csv").unlink()
    r, out = collect(design, tmp_path)
    assert r.returncode == 0
    assert entry(out, "part-placements")["status"] == "missing"
    assert entry(out, "ring-model")["status"] == "missing"


def test_non_numeric_cell_is_unparsed(design, tmp_path):
    write(design, "design/mech/thin/placement.csv", HEAD + "shell,,body,zero,0,1,10,6,2,,True,\n")
    _, out = collect(design, tmp_path)
    assert entry(out, "part-placements")["status"] == "unparsed"


def test_screen_rect_band_block_and_states(design, tmp_path):
    _, out = collect(design, tmp_path)
    m = read_json(out / "ring-model.json")
    assert m["screens"]["rect"] == {"cx": 0.5, "cy": -0.25, "w": 7.0, "h": 4.0, "source": {"file": "design/mech/thin/placement.csv", "line": 4}}
    assert m["band"]["width_mm"] == 3.5 and m["band"]["inner_diameter_mm"] == 17.5
    assert m["block"]["size_mm"] == {"x": 10.0, "y": 6.0, "z": 2.0}
    assert m["design_version"] == "T1"
    states = {s["state"]: s for s in m["screens"]["states"]}
    assert list(states) == ["SCR_A", "SCR_B"]
    assert [f["kind"] for f in states["SCR_A"]["fields"]] == ["text", "battery", "text"]
    assert [f["kind"] for f in states["SCR_B"]["fields"]] == ["dot", "timer", "storage"]
    assert states["SCR_B"]["source"]["line"] == 10


def test_screen_rect_falls_back_to_envelope_file(design, tmp_path):
    write(design, "design/mech/thin/placement.csv", CSV.replace('"lit area 7 (X) x 4 (Y) centred X 0.5 Y -0.25 (note)"', "plain"))
    _, out = collect(design, tmp_path)
    r = read_json(out / "ring-model.json")["screens"]["rect"]
    assert (r["cx"], r["cy"], r["w"], r["h"]) == (0.2, -0.1, 6.0, 3.0)
    assert r["source"]["file"] == "design/look/shared/envelope.py"


def test_part_ids_only_for_references_in_the_parts_list(design, tmp_path):
    _, out = collect(design, tmp_path)
    ids = {n["name"]: n["part_ids"] for n in read_json(out / "ring-model.json")["nodes"]}
    assert ids["cpu"] == ["ring:U1"]  # shell and cell have no reference: see the notes-link tests
    kinds = {n["name"]: n["kind"] for n in read_json(out / "ring-model.json")["nodes"]}
    assert kinds["top"] == "glass" and kinds["lcd"] == "screen" and kinds["shell"] == "finish metal"


def test_no_absolute_path_in_the_records(design, tmp_path):
    _, out = collect(design, tmp_path)
    for f in ("placements.json", "ring-model.json"):
        assert str(design) not in (out / f).read_text()


def test_glb_helper_roundtrip_and_refuses_non_glb(tmp_path):
    p = tmp_path / "a.glb"
    make_glb(p, ["a"])
    js, binary = glb.read(p)
    assert glb.node_names(js) == ["a"] and len(binary) == 36
    (tmp_path / "b.glb").write_bytes(b"nope")
    with pytest.raises(glb.GlbError):
        glb.read(tmp_path / "b.glb")


def test_tool_absent_ships_uncompressed_and_says_so(design, tmp_path, monkeypatch):
    import ring_model

    class Ctx:
        explorer_dir = tmp_path / "no-explorer"

        def out_path(self, rel):
            return tmp_path / rel

    notes = []
    ring_model.finish(Ctx(), design / "design/mech/thin/out/thin-inside.glb", "u.glb", notes)
    assert (tmp_path / "u.glb").is_file() and "not installed" in notes[0]


def test_exterior_nodes_have_kinds_from_the_collector_table(design, tmp_path):
    _, out = collect(design, tmp_path)
    kinds = {n["name"]: n["kind"] for n in read_json(out / "ring-model.json")["nodes"]}
    table = json.loads((Path(__file__).resolve().parents[2] / "cad" / "exterior-kinds.json").read_text())["kinds"]
    assert kinds["body"] == table["body"] == "finish metal" and kinds["band"] == table["band"]
    assert kinds["glass"] == "glass"
    assert kinds["lcd"] == "screen"  # a name the inside model already lists keeps its single entry
    assert kinds["mystery"] == "plain"
    assert "mystery" in entry(out, "ring-model")["message"]
    names = [n["name"] for n in read_json(out / "ring-model.json")["nodes"]]
    assert len(names) == len(set(names))


def test_every_exterior_node_has_a_kind(design, tmp_path):
    _, out = collect(design, tmp_path)
    ejs, _ = glb.read(out / "exterior.glb")
    kinds = {n["name"]: n["kind"] for n in read_json(out / "ring-model.json")["nodes"]}
    unmapped = [n["name"] for n in ejs["nodes"] if "mesh" in n and not kinds.get(n["name"])]
    assert unmapped == []


def test_no_exterior_file_adds_no_exterior_nodes(design, tmp_path):
    (design / "design/status.json").unlink()
    _, out = collect(design, tmp_path)
    names = {n["name"] for n in read_json(out / "ring-model.json")["nodes"]}
    assert "mystery" not in names and "band" not in names


def _extract_with_notes(design, tmp_path, notes):
    import importlib.util

    spec = importlib.util.spec_from_file_location("run_mod", Path(__file__).resolve().parents[2] / "run.py")
    run_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_mod)
    import ring_model

    content = tmp_path / "content"
    content.mkdir()
    (content / "part-notes.json").write_text(json.dumps({"notes": notes}))
    ctx = run_mod.Ctx("ring-model", design, tmp_path / "o", SHA)
    ctx.content_dir = content
    (tmp_path / "o").mkdir()
    return ring_model.extract(ctx)


def test_part_ids_fall_back_to_part_notes_model_names(design, tmp_path):
    notes = {"ring:HSG9": {"model_names": ["shell"]}, "ring:ZZ1": {"model_names": ["cpu"]}, "ring:Q1": {"model_names": []}}
    data, st = _extract_with_notes(design, tmp_path, notes)
    ids = {n["name"]: n["part_ids"] for n in data["nodes"]}
    assert ids["shell"] == ["ring:HSG9"]  # no reference: the notes link it
    assert ids["cpu"] == ["ring:U1"]  # the reference wins over the notes
    assert ids["cell"] == []
    assert "1 inside node(s) link to no parts-list line: cell" in st["message"]


def test_part_ids_without_a_notes_file_stay_empty(design, tmp_path):
    data, st = _extract_with_notes(design, tmp_path, {})
    ids = {n["name"]: n["part_ids"] for n in data["nodes"]}
    assert ids["shell"] == [] and ids["cell"] == []
    assert "2 inside node(s)" in st["message"]


def test_children_are_never_parts_and_come_with_their_class(design, tmp_path):
    r, out = collect(design, tmp_path)
    assert entry(out, "ring-model")["status"] == "ok", entry(out, "ring-model")
    nodes = {n["name"]: n for n in read_json(out / "ring-model.json")["nodes"]}
    assert nodes["cpu"]["children"] == [{"name": "cpu__chip", "class": "chip"}, {"name": "cpu__mark", "class": "mark"},
                                        {"name": "cpu__weird", "class": "weird"}]
    assert nodes["lcd"]["children"][1] == {"name": "lcd__pcb", "class": "pcb"}
    assert "cpu__chip" not in nodes  # a child is not a node of the record
    assert nodes["top"]["kind"] == "glass"  # the blend material sits on the child


def test_unknown_class_is_listed_in_the_message_not_an_error(design, tmp_path):
    _, out = collect(design, tmp_path)
    e = entry(out, "ring-model")
    assert e["status"] == "ok" and "weird" in e["message"] and "chip" not in e["message"].split("unknown child class")[1]


def test_compression_keeps_the_node_tree(design, tmp_path):
    _, out = collect(design, tmp_path)
    js, _ = glb.read(out / "internals.glb")
    names = glb.node_names(js)
    assert {"cpu", "cpu__chip", "cpu__mark", "cpu__weird", "lcd__screen", "top__glass"} <= set(names)
    assert len(names) == 5 + 8 and len(glb.scene_roots(js)) == 5
    by = {n["name"]: n for n in js["nodes"]}
    assert [js["nodes"][c]["name"] for c in by["cpu"]["children"]] == ["cpu__chip", "cpu__mark", "cpu__weird"]


def test_part_with_no_children_has_no_children_field(design, tmp_path):
    make_tree_glb(design / "design/mech/thin/out/thin-inside.glb", {"shell": [], "top": [], "lcd": [], "cpu": [], "cell": []})
    _, out = collect(design, tmp_path)
    assert all("children" not in n for n in read_json(out / "ring-model.json")["nodes"] if n["name"] in ("shell", "cpu"))
