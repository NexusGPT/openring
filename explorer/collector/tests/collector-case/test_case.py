"""collector-case: case/index.json and case/case.glb from a small made-up case folder (no case value)."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

COLLECTOR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(COLLECTOR))

from cad import glb  # noqa: E402
from conftest import EXPLORER, read_json, run_collector  # noqa: E402

SHA = "c" * 40
DESIGN_PY = EXPLORER.parent / "design" / ".venv" / "bin" / "python"
CAP = json.loads((EXPLORER / "contract" / "schema" / "constants.json").read_text())["GLB_MAX_MB"]

ARCH = """# Zz case architecture (version Z2)

Built against `design/architecture.md` version Z1 and `requirements.md` section 9.

## 1. Choice

- Speed: 7.25 min per recorded hour. This is the planning figure for the chosen part.
- In the 61 minutes a ring charge takes, the case copies 8.5 recorded hours.

```
 [cell 345 mAh with PCM, BT1]
```

Cell sizing: Chosen 345 mAh: 2.75 charges.

## 8. Items only a supplier can close

| # | Item | Who | What to ask |
|---|---|---|---|
| S1 | Widget | Acme | the widget in 3 colours |
| S2 | Gadget | Bolt | a quote for 20 |
"""
BOM = ("item,reference,quantity,function\n"
       "1,U1,1,chip\n"
       "2,\"P1-P4\",4,pins\n"
       "3,R1; R2,2,resistors\n")
SIZE = "closed case outer size X 12.5 mm x Y 8.5 mm x Z 40.25 mm (X -6 to 6)\n"
STATUS = {"design_version": "Z1", "areas": {"case": {"state": "in progress", "why": "zz: made for the old ring", "who": "lead"}}}
STEP_SCRIPT = """
import sys
from build123d import Box, Cylinder, Pos, export_step
out = sys.argv[1]
def w(stem, shape):
    export_step(shape, f"{out}/{stem}.step")
w("lid", Pos(0, 0, 10) * Box(10, 6, 1))
w("body", Box(10, 6, 8))
w("hinge_pin", Pos(0, -3, 10.5) * Cylinder(0.5, 12).rotate(__import__("build123d").Axis.Y, 90))
w("pin_P1_AAA", Pos(1, 0, 0) * Box(1, 1, 1))
w("pin_P2_D-", Pos(2, 0, 0) * Box(1, 1, 1))
w("pin_P3_D+", Pos(3, 0, 0) * Box(1, 1, 1))
w("ring_US7_block", Pos(0, 0, 4) * Box(5, 3, 1))
w("ring_US9_block", Pos(0, 0, 4) * Box(6, 3, 1))
w("U1_zzchip", Pos(-3, 0, 0) * Box(1, 1, 1))
"""


def put(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


@pytest.fixture
def design(tmp_path):
    root = tmp_path / "src"
    put(root, "design/case/case-architecture.md", ARCH)
    put(root, "design/case/case-bom.csv", BOM)
    put(root, "design/case/out/case_size.txt", SIZE)
    put(root, "design/status.json", json.dumps(STATUS))
    put(root, "design/architecture.md", "# A\n\nVersion Z5-draft, 2026.\n")
    return root


@pytest.fixture(scope="module")
def steps(tmp_path_factory):
    if not DESIGN_PY.is_file():
        pytest.skip("design venv (build123d) not found")
    d = tmp_path_factory.mktemp("steps")
    r = subprocess.run([str(DESIGN_PY), "-c", STEP_SCRIPT, str(d)], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return d


def collect(root, tmp_path):
    out = tmp_path / "out"
    r = run_collector("--source", str(root), "--out", str(out), "--commit", SHA)
    assert r.returncode == 0, r.stderr
    return out


def entry(out):
    return read_json(out / "manifest.json")["records"]["case"]


def line_of(root, fact):
    return (root / fact["source"]["file"]).read_text().splitlines()[fact["source"]["line"] - 1]


def test_facts_each_with_the_line_that_holds_them(design, tmp_path):
    out = collect(design, tmp_path)
    d = read_json(out / "case" / "index.json")
    f = {x["id"]: x for x in d["facts"]}
    assert (f["case-size"]["value"], f["case-size"]["unit"]) == ("12.5 x 8.5 x 40.25", "mm")
    assert (f["case-cell"]["value"], f["case-cell"]["unit"]) == (345, "mAh")
    assert f["case-transfer"]["value"] == 7.25
    assert f["case-ring-charge"]["value"] == 61 and f["case-copied-per-charge"]["value"] == 8.5
    assert f["case-charges"]["value"] == 2.75
    for x in f.values():
        for token in str(x["value"]).split(" x "):
            assert token in line_of(design, x), x["id"]


def test_case_parts_are_ids_only_and_supplier_items_have_who_and_ask(design, tmp_path):
    out = collect(design, tmp_path)
    d = read_json(out / "case" / "index.json")
    assert d["part_ids"] == ["case:U1", "case:P1-P4", "case:R1", "case:R2"]
    s = {x["id"]: x for x in d["supplier_items"]}
    assert set(s) == {"S1", "S2"}
    assert (s["S1"]["who"], s["S1"]["ask"], s["S1"]["item"]) == ("Acme", "the widget in 3 colours", "Widget")
    assert s["S2"]["section"] == "section 8 of case-architecture.md"
    assert "S2" in line_of(design, s["S2"])


def test_stale_state_with_a_plain_reason_when_built_for_an_older_design(design, tmp_path):
    out = collect(design, tmp_path)
    e = entry(out)
    assert (e["status"], e["basis_version"], e["current_version"]) == ("stale", "Z1", "Z5-draft")
    assert "zz: made for the old ring" in e["message"]
    # the content stays: the record is still written
    assert (out / "case" / "index.json").is_file()


def test_not_stale_when_the_versions_match(design, tmp_path):
    put(design, "design/architecture.md", "# A\n\nVersion Z1-draft, 2026.\n")
    out = collect(design, tmp_path)
    e = entry(out)
    assert e["status"] == "ok"
    assert "zz: made" not in (e["message"] or "")


def test_a_fact_with_no_sentence_is_left_out_and_named(design, tmp_path):
    put(design, "design/case/case-architecture.md", ARCH.replace("7.25 min per recorded hour. This is the planning figure", "slow"))
    out = collect(design, tmp_path)
    d = read_json(out / "case" / "index.json")
    assert "case-transfer" not in {x["id"] for x in d["facts"]}
    assert "Transfer time" in entry(out)["message"]


def test_no_case_folder_reads_missing(design, tmp_path):
    import shutil
    shutil.rmtree(design / "design" / "case")
    out = collect(design, tmp_path)
    assert entry(out)["status"] == "missing"
    assert not (out / "case" / "index.json").exists()


def test_no_step_files_gives_no_model_and_says_so(design, tmp_path):
    out = collect(design, tmp_path)
    d = read_json(out / "case" / "index.json")
    assert d["glb"] is None and "no STEP files" in entry(out)["message"]


def test_model_keeps_names_marks_the_lid_and_finds_the_hinge(design, steps, tmp_path):
    (design / "design/case/out/parts").mkdir(parents=True, exist_ok=True)
    for f in steps.glob("*.step"):
        (design / "design/case/out/parts" / f.name).write_bytes(f.read_bytes())
    out = collect(design, tmp_path)
    d = read_json(out / "case" / "index.json")
    g = d["glb"]
    names = {n["name"] for n in g["nodes"]}
    assert {"lid", "body", "hinge_pin", "pin_P1_AAA", "pin_P2_D-", "pin_P3_D+", "U1_zzchip"} <= names  # + and - kept
    assert g["lid_node"] == "lid" and g["file"] == "case/case.glb"
    # only the smallest ring size is seated
    assert "ring_US7_block" in names and "ring_US9_block" not in names
    # the pin node stands for the case part its range token covers
    by = {n["name"]: n["part_ids"] for n in g["nodes"]}
    assert by["pin_P2_D-"] == ["case:P1-P4"] and by["U1_zzchip"] == ["case:U1"] and by["lid"] == []
    # hinge: the long axis of the pin (length 12 along X), centred where the pin sits
    assert g["hinge"]["axis"] == {"x": 1.0, "y": 0.0, "z": 0.0}
    assert g["hinge"]["point"] == pytest.approx({"x": 0.0, "y": -3.0, "z": 10.5}, abs=1e-3)
    # the GLB itself carries the names, is Y-up and is under the cap
    f = out / g["file"]
    assert f.stat().st_size <= CAP * 1024 * 1024
    raw = f.read_bytes()
    assert raw[:4] == b"glTF"
    for n in ("lid", "pin_P2_D-", "pin_P3_D+"):
        assert n.encode() in raw
