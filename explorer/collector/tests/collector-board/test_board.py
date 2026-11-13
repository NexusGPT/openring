"""collector-board: board/index.json and board/plan-<side>.svg from small made-up design files (no ring value)."""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from conftest import read_json, run_collector  # noqa: E402

SHA = "b" * 40
HEAD = "part,reference,layer,x,y,z,size_x,size_y,size_z,angle_deg,metal,note\n"
# board: z 5.0, thickness 0.4 -> faces 5.2 (top) and 4.8 (bottom). zz_under hangs below, zz_over sits above, zz_far is 9 mm away.
CSV = HEAD + (
    "zz_plate,ZB1,board,1.0,2.0,5.0,20.0,10.0,0.4,,False,plate\n"
    "zz_under,ZU1,board,-3.0,1.0,4.5,3.0,2.0,0.6,,True,\n"
    "zz_over,ZO1,board,4.0,-1.5,5.6,2.0,2.0,0.6,,True,\n"
    "zz_far,ZF1,board,0.0,0.0,14.0,2.0,2.0,0.5,,True,\n"
    "zz_ant,ZA1,board,-8.0,5.0,4.7,1.0,2.0,0.8,,False,stands in the board notch\n"
    "zz_flex,ZX1,band,0.0,4.0,0.0,1.0,1.0,0.1,,False,thumb side: flex\n"
    "zz_screen,ZS1,screen,0.0,0.0,6.0,20.0,10.0,0.5,,True,\n"
)
ARCH = """# Architecture

Version ZV1.

## 1. Old

A notch of the board, 9.9 x 9.9 mm, at the hand-end corner (older sentence, later one wins).

## 2. New

Antenna: it sits in a notch of the board, 1.5 x 3.0 mm, at the hand-end corner (found by the model).
The cap needs a notch of 2.5 x 0.5 mm on its thumb-side edge (found by the model).
"""
BOM = "item,reference,quantity\nPlate,ZB1,1\nUnder,ZU1,1\nOver,ZO1,1\nFar,ZF1,1\nAnt,ZA1,1\n"
TRACKS = '(kicad_pcb (version 1)\n  (segment (start 0 0) (end 1 1) (width 0.2) (layer "F.Cu") (net 1))\n)\n'
NO_TRACKS = '(kicad_pcb (version 1)\n  (gr_rect (start 0 0) (end 10 5) (layer "Edge.Cuts"))\n)\n'


def put(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


@pytest.fixture
def design(tmp_path):
    root = tmp_path / "src"
    put(root, "design/mech/thin/placement.csv", CSV)
    put(root, "design/architecture.md", ARCH)
    put(root, "design/bom.csv", BOM)
    return root


def collect(root, tmp_path):
    out = tmp_path / "out"
    r = run_collector("--source", str(root), "--out", str(out), "--commit", SHA)
    assert r.returncode == 0, r.stderr
    return out


def entry(out):
    return read_json(out / "manifest.json")["records"]["board-files"]


def test_unrouted_plan_from_the_placement_table(design, tmp_path):
    out = collect(design, tmp_path)
    d = read_json(out / "board" / "index.json")
    assert entry(out)["status"] == "ok"
    assert d["routed"] is False
    o = d["outline"]
    assert (o["w"], o["h"], o["x"], o["y"]) == (20.0, 10.0, 1.0, 2.0)
    assert o["source"] == {"file": "design/mech/thin/placement.csv", "line": 2}
    assert "design/ecad/ring/ring.kicad_pcb" in d["missing"]
    # sides worked out here from the table, independently of the extractor
    rows = {}
    for ln in CSV.splitlines()[1:]:
        c = ln.split(",")
        if c[2] == "board" and c[0] != "zz_plate":
            rows[c[0]] = (float(c[5]), float(c[8]))
    top_face, bottom_face = 5.0 + 0.2, 5.0 - 0.2
    want = {}
    for n, (z, h) in rows.items():
        if z + h / 2 < bottom_face - 2.0 or z - h / 2 > top_face + 2.0:
            continue
        want[n] = "top" if z > 5.0 else "bottom"
    got = {p["name"]: p["side"] for p in d["placements"]}
    assert got == want
    assert got["zz_under"] == "bottom" and got["zz_over"] == "top"
    assert "zz_far" not in got and any("zz_far" in m for m in d["missing"])
    assert not any(":" in m.split(" ")[0] for m in d["missing"])  # the app writes "Missing: <list>": no label of our own
    ids = {p["name"]: p["part_id"] for p in d["placements"]}
    assert ids["zz_under"] == "ring:ZU1"


def test_each_side_has_its_own_svg_marked_not_routed(design, tmp_path):
    out = collect(design, tmp_path)
    d = read_json(out / "board" / "index.json")
    assert d["svg"]["top"] == "board/plan-top.svg" and d["svg"]["bottom"] == "board/plan-bottom.svg"
    for side in ("top", "bottom"):
        text = (out / d["svg"][side]).read_text(encoding="utf-8")
        root = ET.fromstring(text)  # parses as XML
        assert "Planned placement, not routed" in text
        assert str(out) not in text and "/Users/" not in text
    assert "ZU1" in (out / "board/plan-bottom.svg").read_text() and "ZO1" not in (out / "board/plan-bottom.svg").read_text()
    assert "ZO1" in (out / "board/plan-top.svg").read_text()


def test_a_side_with_no_part_has_no_svg(design, tmp_path):
    put(design, "design/mech/thin/placement.csv", "\n".join(l for l in CSV.splitlines() if "zz_over" not in l) + "\n")
    out = collect(design, tmp_path)
    d = read_json(out / "board" / "index.json")
    assert d["svg"]["top"] is None and d["svg"]["bottom"] == "board/plan-bottom.svg"
    assert not (out / "board" / "plan-top.svg").exists()


def test_notches_use_the_latest_sentence_and_say_what_is_not_known(design, tmp_path):
    out = collect(design, tmp_path)
    d = read_json(out / "board" / "index.json")
    n = {x["name"]: x for x in d["notches"]}
    corner, edge = n["antenna notch"], n["edge notch"]
    assert (corner["w"], corner["h"]) == (1.5, 3.0)
    assert (edge["w"], edge["h"]) == (2.5, 0.5)
    arch = ARCH.splitlines()
    assert "1.5 x 3.0" in arch[corner["source"]["line"] - 1]
    assert "2.5 x 0.5" in arch[edge["source"]["line"] - 1]
    # hand-end corner on the +y side (the part in the notch is at y above the board middle): flush with both edges
    assert corner["x"] == pytest.approx(1.0 - 10.0 + 1.5 / 2) and corner["y"] == pytest.approx(2.0 + 5.0 - 3.0 / 2)
    assert corner["position_known"] is True and edge["position_known"] is False
    assert edge["y"] == pytest.approx(2.0 + 5.0 - 0.5 / 2)  # thumb side is +y: the flex row says so
    assert any("thumb-side edge" in m for m in d["missing"])


def test_a_board_file_with_tracks_is_routed(design, tmp_path):
    put(design, "design/ecad/ring/zz.kicad_pcb", TRACKS)
    out = collect(design, tmp_path)
    d = read_json(out / "board" / "index.json")
    assert d["routed"] is True
    assert not any("kicad_pcb" in m and m.startswith("design/") for m in d["missing"])
    assert "design/ecad/ring/zz.kicad_pcb" in entry(out)["source"]
    assert d["svg"]["top"] is None or d["svg"]["top"].startswith("board/")  # drawn only when kicad-cli exists


def test_a_board_file_without_tracks_is_not_routed(design, tmp_path):
    put(design, "design/ecad/ring/zz.kicad_pcb", NO_TRACKS)
    out = collect(design, tmp_path)
    d = read_json(out / "board" / "index.json")
    assert d["routed"] is False
    assert "the board file holds no tracks (not routed)" in d["missing"]
    assert d["outline"]["w"] == 10.0 and d["outline"]["source"]["file"] == "design/ecad/ring/zz.kicad_pcb"


def test_no_placement_file_reads_missing(design, tmp_path):
    (design / "design/mech/thin/placement.csv").unlink()
    out = collect(design, tmp_path)
    e = entry(out)
    assert e["status"] == "missing" and "placement.csv" in e["message"]
    assert not (out / "board" / "index.json").exists()


def test_no_board_row_is_unparsed_with_the_file_name(design, tmp_path):
    put(design, "design/mech/thin/placement.csv", HEAD + "zz_a,Z1,band,0,0,0,1,1,1,,False,\n")
    out = collect(design, tmp_path)
    e = entry(out)
    assert e["status"] == "unparsed" and "placement.csv" in e["message"]


def test_no_architecture_file_still_gives_the_plan_and_says_so(design, tmp_path):
    (design / "design/architecture.md").unlink()
    out = collect(design, tmp_path)
    d = read_json(out / "board" / "index.json")
    assert d["routed"] is False and "notches" not in d
    assert any("architecture.md" in m for m in d["missing"])


# ---- a real (small, made-up) KiCad board file: two footprints, an outline, no tracks, read and drawn with the real tool
PCB = """(kicad_pcb
	(version 20241229)
	(generator "pcbnew")
	(generator_version "9.0")
	(general (thickness 0.3))
	(paper "A4")
	(layers
		(0 "F.Cu" signal)
		(2 "B.Cu" signal)
		(5 "F.SilkS" user "F.Silkscreen")
		(7 "B.SilkS" user "B.Silkscreen")
		(15 "F.CrtYd" user "F.Courtyard")
		(13 "B.CrtYd" user "B.Courtyard")
		(17 "F.Fab" user)
		(19 "B.Fab" user)
		(25 "Edge.Cuts" user)
	)
	(net 0 "")
	(gr_rect
		(start 0 0)
		(end 20 10)
		(stroke (width 0.1) (type default))
		(fill no)
		(layer "Edge.Cuts")
	)
	(footprint "zz:Top"
		(layer "F.Cu")
		(at 5 3)
		(property "Reference" "ZT1" (at 0 0 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))
		(fp_rect (start -1 -0.5) (end 1 0.5) (stroke (width 0.05) (type default)) (fill no) (layer "F.CrtYd"))
		(pad "1" smd rect (at -0.5 0) (size 0.6 0.6) (layers "F.Cu" "F.Mask"))
	)
	(footprint "zz:Bot"
		(layer "B.Cu")
		(at 12 6 90)
		(property "Reference" "ZB1" (at 0 0 0) (layer "B.SilkS") (effects (font (size 1 1) (thickness 0.15)) (justify mirror)))
		(pad "1" smd rect (at -1 0) (size 1 1) (layers "B.Cu" "B.Mask"))
		(pad "2" smd rect (at 1 0) (size 1 1) (layers "B.Cu" "B.Mask"))
	)
)
"""


def real_tool():
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "extract"))
    import schematic
    return schematic._tool()


@pytest.mark.skipif(real_tool() is None, reason="kicad-cli is truly missing")
def test_a_real_board_file_without_tracks_is_placed_not_routed_and_drawn(design, tmp_path):
    put(design, "design/ecad/ring/pcb/zz.kicad_pcb", PCB)
    out = collect(design, tmp_path)
    d = read_json(out / "board" / "index.json")
    e = entry(out)
    assert e["status"] == "ok" and "design/ecad/ring/pcb/zz.kicad_pcb" in e["source"]
    assert d["routed"] is False and "the board file holds no tracks (not routed)" in d["missing"]
    assert (d["outline"]["w"], d["outline"]["h"], d["outline"]["x"], d["outline"]["y"]) == (20.0, 10.0, 10.0, 5.0)
    p = {x["name"]: x for x in d["placements"]}
    assert set(p) == {"ZT1", "ZB1"}
    assert (p["ZT1"]["side"], p["ZT1"]["x"], p["ZT1"]["y"], p["ZT1"]["w"], p["ZT1"]["h"]) == ("top", 5.0, 3.0, 2.0, 1.0)
    assert (p["ZB1"]["side"], p["ZB1"]["x"], p["ZB1"]["y"]) == ("bottom", 12.0, 6.0)
    assert p["ZB1"]["part_id"] == "ring:ZB1" and p["ZT1"]["part_id"] is None  # only ZB1 is in the fixture parts list
    for side in ("top", "bottom"):
        assert d["svg"][side] == f"board/{side}.svg"
        root = ET.fromstring((out / d["svg"][side]).read_text(encoding="utf-8"))
        assert root.tag.endswith("svg")
