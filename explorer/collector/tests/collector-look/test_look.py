"""collector-look: looks/index.json and looks/<id>.glb from small made-up design files."""
import json
import struct
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from cad import glb  # noqa: E402
from conftest import read_json, run_collector  # noqa: E402

SHA = "a" * 40
VIEWER = """const X = 1;
const FINISHES = {
  'Zed One':   { color: 0x102030, rough: 0.5, env: 1.0 },
  'Zed Two':   { color: 0xabcdef, rough: 0.125, env: 1.0 },
  'Zed Three': { color: 0x000001, rough: 0.9, env: 1.1 },
  'Zed Four':  { color: 0xffffff, rough: 0.0, env: 1.0 },
};
"""
LONG = " ".join(f"w{i}" for i in range(40))


def make_glb(path, size=(0.04, 0.02, 0.01)):
    pos = struct.pack("<9f", 0, 0, 0, size[0], 0, 0, 0, size[1], size[2])
    js = {"asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": [0]}], "nodes": [{"name": "body", "mesh": 0}],
          "meshes": [{"primitives": [{"attributes": {"POSITION": 0}}]}],
          "accessors": [{"bufferView": 0, "componentType": 5126, "count": 3, "type": "VEC3", "min": [0, 0, 0], "max": list(size)}],
          "bufferViews": [{"buffer": 0, "byteLength": 36}], "buffers": [{"byteLength": 36}]}
    path.parent.mkdir(parents=True, exist_ok=True)
    glb.write(path, js, pos)


def put(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def direction(title, trades):
    return (f"# Look Q: {title}\n\n**Thesis.** {LONG}. Second.\n\n## Key\n- not this\n\n## Worse than a box\n"
            + "".join(f"- **T{i}:** {LONG}\n" for i in range(trades)))


@pytest.fixture
def design(tmp_path):
    root = tmp_path / "src"
    for f in ("qa", "qb", "qc"):
        make_glb(root / f"design/look/{f}/out/ring.glb")
        put(root, f"design/look/{f}/direction.md", direction(f"Name {f}", 5))
    put(root, "design/look/qa/plain-text.json", json.dumps(
        {"title": "Plain A", "sentence": "Short one.", "worse_at": ["a b c", "d e", "f", "g"]}))
    (root / "design/look/qd/out").mkdir(parents=True)  # folder without a model
    put(root, "design/look/qd/direction.md", direction("Name qd", 1))
    make_glb(root / "design/look/viewer/out/ring.glb")  # must be excluded
    put(root, "design/look/shared/envelope.py", "X = 1\n")
    put(root, "design/look/viewer/viewer.js", VIEWER)
    put(root, "design/status.json", json.dumps({"look": {"picked": None, "rejected": ["qa", "qb", "qc"], "in_design": []}}))
    return root


def collect(design, tmp_path):
    out = tmp_path / "out"
    r = run_collector("--source", str(design), "--out", str(out), "--commit", SHA)
    return r, out


def index(out):
    return read_json(out / "looks" / "index.json")


def entry(out):
    return read_json(out / "manifest.json")["records"]["look-options"]


def test_options_texts_and_limits(design, tmp_path):
    r, out = collect(design, tmp_path)
    assert r.returncode == 0, r.stderr
    assert entry(out)["status"] == "ok", entry(out)
    d = index(out)
    ids = [o["id"] for o in d["options"]]
    assert ids == ["qa", "qb", "qc", "qd"], ids  # viewer and shared never listed
    for o in d["options"]:
        assert len(o["sentence"].split()) <= 20, o
        assert len(o["worse_at"]) <= 3
        assert all(len(w.split()) <= 12 for w in o["worse_at"]), o
    qa = d["options"][0]
    assert qa["title"] == "Plain A" and qa["sentence"] == "Short one." and qa["worse_at"] == ["a b c", "d e", "f"]
    qb = d["options"][1]
    assert qb["title"] == "Name qb" and len(qb["worse_at"]) == 3


def test_size_measured_and_model_shipped(design, tmp_path):
    r, out = collect(design, tmp_path)
    o = index(out)["options"][0]
    assert o["glb"]["bounds_mm"] == {"x": 40.0, "y": 20.0, "z": 10.0}
    assert (out / o["glb"]["file"]).stat().st_size == o["glb"]["size_bytes"] > 0


def test_four_finishes_read_from_viewer(design, tmp_path):
    r, out = collect(design, tmp_path)
    f = index(out)["finishes"]
    assert [x["name"] for x in f] == ["Zed One", "Zed Two", "Zed Three", "Zed Four"]
    assert f[1]["colour"] == "#abcdef" and f[1]["roughness"] == 0.125
    assert f[0]["source"]["file"] == "design/look/viewer/viewer.js" and f[0]["source"]["line"] == 3


def test_folder_without_model_is_listed_missing(design, tmp_path):
    r, out = collect(design, tmp_path)
    qd = [o for o in index(out)["options"] if o["id"] == "qd"][0]
    assert qd["glb"] is None
    assert "qd: no model file" in entry(out)["message"]


def test_rejected_flags_and_open_count(design, tmp_path):
    put(design, "design/status.json", json.dumps({"look": {"picked": None, "rejected": ["qa", "qb", "qc", "qd"], "in_design": []}}))
    r, out = collect(design, tmp_path)
    o = {x["id"]: x for x in index(out)["options"]}
    assert o["qa"]["rejected"] and o["qb"]["rejected"] and o["qc"]["rejected"]
    assert "0 option(s) not rejected" in entry(out)["message"]
    assert "New options in design" in entry(out)["message"]
    assert index(out)["picked"] is None


def test_in_design_variant_id(design, tmp_path):
    make_glb(design / "design/look/qs/out/ring-v9.glb", (0.03, 0.01, 0.01))
    put(design, "design/look/qs/direction.md", direction("Slab", 2))
    make_glb(design / "design/look/qs/out/ring.glb")
    put(design, "design/status.json", json.dumps({"look": {"picked": None, "rejected": ["qa"], "in_design": ["qs-v9"]}}))
    r, out = collect(design, tmp_path)
    d = index(out)
    s = [o for o in d["options"] if o["id"] == "qs-v9"]
    assert len(s) == 1 and s[0]["in_design"] and not s[0]["rejected"] and s[0]["glb"]["bounds_mm"]["x"] == 30.0
    assert not [o for o in d["options"] if o["id"] == "qs"]  # the bare folder is not listed twice
    assert "1 option(s) not rejected" in entry(out)["message"] or "not rejected" in entry(out)["message"]


def test_picked(design, tmp_path):
    put(design, "design/status.json", json.dumps({"look": {"picked": "qb", "rejected": [], "in_design": []}}))
    r, out = collect(design, tmp_path)
    assert index(out)["picked"] == "qb"


def test_no_status_and_no_viewer(design, tmp_path):
    (design / "design/status.json").unlink()
    (design / "design/look/viewer/viewer.js").unlink()
    r, out = collect(design, tmp_path)
    assert entry(out)["status"] == "ok"
    d = index(out)
    assert d["finishes"] == [] and "no finishes" in entry(out)["message"]
    assert all(not o["rejected"] for o in d["options"])


def test_broken_status_is_unparsed(design, tmp_path):
    put(design, "design/status.json", "{nope")
    r, out = collect(design, tmp_path)
    assert entry(out)["status"] == "unparsed"


def test_broken_model_is_listed_without_model(design, tmp_path):
    (design / "design/look/qb/out/ring.glb").write_bytes(b"not a glb at all, just text bytes")
    r, out = collect(design, tmp_path)
    qb = [o for o in index(out)["options"] if o["id"] == "qb"][0]
    assert qb["glb"] is None and "cannot be read" in entry(out)["message"]


def test_variant_block_size_from_measures_with_line(design, tmp_path):
    make_glb(design / "design/look/qs/out/ring-v9.glb", (0.03, 0.01, 0.02))
    put(design, "design/look/qs/out/measures-v9.json", '{\n "variant": "v9",\n "block_size": [\n  11.5,\n  7.25,\n  3.5\n ]\n}\n')
    put(design, "design/status.json", json.dumps({"look": {"picked": None, "rejected": [], "in_design": ["qs-v9"]}}))
    r, out = collect(design, tmp_path)
    o = [x for x in index(out)["options"] if x["id"] == "qs-v9"][0]
    assert o["glb"]["bounds_mm"] == {"x": 11.5, "y": 7.25, "z": 3.5}  # the block, not the 30 x 10 x 20 model
    assert o["source"] == {"file": "design/look/qs/out/measures-v9.json", "line": 3}


def test_block_size_from_designs_json_with_line(design, tmp_path):
    put(design, "design/look/viewer/designs.json", '{\n "qa": {\n  "size": "1 x 2 x 3 mm"\n },\n "qb": {\n  "title": "x",\n  "size": "12.5 x 6.25 x 3 mm"\n }\n}\n')
    r, out = collect(design, tmp_path)
    o = [x for x in index(out)["options"] if x["id"] == "qb"][0]
    assert o["glb"]["bounds_mm"] == {"x": 12.5, "y": 6.25, "z": 3.0}
    assert o["source"] == {"file": "design/look/viewer/designs.json", "line": 7}


def test_no_block_size_says_so(design, tmp_path):
    r, out = collect(design, tmp_path)
    assert "qa: no block size in the design files" in entry(out)["message"]


def test_viewer_plain_text_preferred_over_direction(design, tmp_path):
    put(design, "design/look/viewer/plain-text.json", json.dumps(
        {"qb": {"sentence": "Hand written line.", "tradeoffs": ["One.", "Two."]}}))
    r, out = collect(design, tmp_path)
    o = {x["id"]: x for x in index(out)["options"]}
    assert o["qb"]["sentence"] == "Hand written line." and o["qb"]["worse_at"] == ["One.", "Two."]
    assert o["qc"]["sentence"].startswith("W0 w1") or o["qc"]["sentence"].startswith("w0")  # no entry: direction.md


def test_cut_at_whole_word_and_no_dots(design, tmp_path):
    r, out = collect(design, tmp_path)
    o = {x["id"]: x for x in index(out)["options"]}
    for w in o["qb"]["worse_at"]:
        assert "..." not in w and not w.endswith(".") and len(w.split()) == 12 and w.split()[-1] == "w10", w


VARIANT_JS = VIEWER + """const VARIANT_LABELS = { v9: 'Round face', v8: 'Old face' };
function makeList() {
  if (state.variant === 'v9') {
    m1.thesis = 'Own line of v9, it is short.';
    m1.worse = ['First v9 trade.', 'Second v9 trade is long, with a clause that keeps going on and on and on.', 'Third.'];
  }
}
"""


def variant_design(design):
    make_glb(design / "design/look/qs/out/ring-v9.glb")
    put(design, "design/look/qs/direction.md", direction("Slab", 2))
    put(design, "design/look/viewer/plain-text.json", json.dumps({"qs": {"sentence": "Old folder line.", "tradeoffs": ["Old."]}}))
    put(design, "design/look/viewer/viewer.js", VARIANT_JS)
    put(design, "design/status.json", json.dumps({"look": {"picked": None, "rejected": [], "in_design": ["qs-v9"]}}))


def test_variant_text_comes_from_its_own_entry(design, tmp_path):
    variant_design(design)
    r, out = collect(design, tmp_path)
    o = [x for x in index(out)["options"] if x["id"] == "qs-v9"][0]
    assert o["sentence"] == "Own line of v9, it is short."
    assert o["worse_at"][0] == "First v9 trade." and o["worse_at"][1] == "Second v9 trade is long" and len(o["worse_at"]) == 3
    assert o["title"] == "Slab: Round face" and "v9" not in o["title"]
    assert o["source"] == {"file": "design/look/viewer/viewer.js", "line": 11}


def test_variant_without_entry_falls_back_and_says_so(design, tmp_path):
    variant_design(design)
    put(design, "design/look/viewer/viewer.js", VIEWER)
    r, out = collect(design, tmp_path)
    o = [x for x in index(out)["options"] if x["id"] == "qs-v9"][0]
    assert o["sentence"].startswith("W0") and o["sentence"] != "Old folder line."  # direction.md, not the folder's viewer line
    assert "no entry for variant v9" in entry(out)["message"]
    assert o["title"] == "Slab"


def test_cut_at_clause_end(design, tmp_path):
    variant_design(design)
    r, out = collect(design, tmp_path)
    assert "keeps going" not in " ".join([x for x in index(out)["options"] if x["id"] == "qs-v9"][0]["worse_at"])
