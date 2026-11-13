"""collector-parts: files.json and bundle.zip."""
import hashlib
import json
import os
import subprocess
import zipfile
from pathlib import Path

import pytest
from conftest import EXPLORER, read_json
from parts_support import collect, make_project, validate

REPO = EXPLORER.parent
MB = 1024 * 1024
AREAS = {"look", "inside", "electronics", "board", "parts", "behaviour", "case", "open"}

EXTRA = {
    "design/datasheets/part_a.pdf": "pdf",
    "design/case/out/parts/pin_P3_D+.step": "step with a plus",
    "design/look/shared/finishes.json": "{}",
    "design/look/q/direction.md": "rejected look q",
    "design/look/q/out/ring.glb": "glb of q",
    "design/look/ok/direction.md": "kept look",
    "design/mech/placement.csv": "a,b\n",
    "design/ecad/ring/netlist.csv": "a\n",
    "design/firmware.md": "fw\n",
    "design/status.json": json.dumps({"look": {"picked": None, "rejected": ["q"], "in_design": ["ok"]}}),
    "design/.venv/lib/site.py": "venv",
    "design/tools/__pycache__/m.cpython-39.pyc": "pyc",
    "design/tools/node_modules/x/index.js": "js",
    "design/tools/run.log": "log",
    "design/mech/logs/step.txt": "log dir",
    "design/mech/step.err": "err",
    "design/.env": "SECRET=1",
    "design/tools/api.key": "key",
    "design/.DS_Store": "ds",
    "design/big/huge.bin": 21 * MB,
    "design/tools/helper.py": "print(1)\n",
}


def build(tmp_path, git=True, extra=None):
    root = make_project(tmp_path / "repo", extra_files=extra if extra is not None else EXTRA, init_git=git)
    if git:  # a .venv the repository ignores, like the real one
        pass
    out = tmp_path / "out"
    r, m = collect(root, out, commit=None if git else "c" * 40)
    assert r.returncode == 0, r.stderr
    assert m["records"]["files"]["status"] == "ok", m["records"]["files"]
    return root, out, m, read_json(out / "files.json")


@pytest.fixture
def built(tmp_path):
    return build(tmp_path)


def paths(d):
    return [f["path"] for f in d["files"]]


def test_C03_size_area_plus_and_valid(built):
    root, out, _m, d = built
    by = {f["path"]: f for f in d["files"]}
    f = by["design/datasheets/part_a.pdf"]
    assert f["size_bytes"] == os.path.getsize(root / f["path"]) and f["area"] == "parts" and f["tracked"] is True
    assert "design/case/out/parts/pin_P3_D+.step" in by
    assert by["design/case/out/parts/pin_P3_D+.step"]["area"] == "case"
    assert by["requirements.md"]["area"] == "open" and by["design/status.json"]["area"] == "open"
    assert by["design/tools/helper.py"]["area"] == "other"
    assert {by[p]["area"] for p in ("design/look/shared/finishes.json", "design/mech/placement.csv",
                                     "design/ecad/ring/netlist.csv", "design/firmware.md", "design/bom.csv")} == {"look", "inside", "electronics", "behaviour", "parts"}
    assert f["modified"].endswith("Z")
    assert validate("files", out / "files.json").returncode == 0
    assert paths(d) == sorted(paths(d))


def test_C03_nothing_unsafe_is_listed(built):
    _root, _out, _m, d = built
    bad = [p for p in paths(d) if any(s in p for s in (".venv", "__pycache__", "node_modules", ".git/", ".env", ".key", ".log", ".err", "/logs/", ".DS_Store"))]
    assert bad == []


def test_C03_rejected_looks_are_left_out_and_said(built):
    _root, _out, m, d = built
    assert not [p for p in paths(d) if p.startswith("design/look/q/")]
    assert "design/look/ok/direction.md" in paths(d)
    assert "2 file(s) of the rejected exteriors" in m["records"]["files"]["message"]


def test_C03_oversize_file_is_listed_with_its_size_and_not_in_the_bundle(built):
    _root, out, m, d = built
    f = next(f for f in d["files"] if f["path"] == "design/big/huge.bin")
    assert f["size_bytes"] == 21 * MB
    assert "design/big/huge.bin" not in d["bundle"]["contents"]
    assert "design/big/huge.bin" in m["records"]["files"]["message"]
    with zipfile.ZipFile(out / "bundle.zip") as z:
        assert "design/big/huge.bin" not in z.namelist()


def test_C03_area_without_files_is_absent_not_invented(built):
    _root, _out, _m, d = built
    assert {f["area"] for f in d["files"]} <= AREAS | {"other"}
    assert "board" not in {f["area"] for f in d["files"]}  # board has no folder of its own yet


def test_C04_bundle_matches_files_json(built):
    root, out, _m, d = built
    with zipfile.ZipFile(out / "bundle.zip") as z:
        assert z.testzip() is None
        names = z.namelist()
        assert names == d["bundle"]["contents"]
        assert d["bundle"]["file"] == "bundle.zip" and d["bundle"]["size_bytes"] == (out / "bundle.zip").stat().st_size
        for n in names:
            assert not n.startswith("/") and ".." not in n.split("/")
            assert not any(s in n for s in (".venv/", "__pycache__/", ".git/", ".env", ".key", "node_modules/"))
            assert hashlib.sha256(z.read(n)).hexdigest() == hashlib.sha256((root / n).read_bytes()).hexdigest()
    assert "design/case/out/parts/pin_P3_D+.step" in names and "requirements.md" in names
    assert set(names) <= set(paths(d))


def test_C04_a_copy_without_git_walks_the_folder_and_reads_tracked(tmp_path):
    root, out, _m, d = build(tmp_path, git=False)
    assert all(f["tracked"] is True for f in d["files"])  # an archive holds only tracked files
    assert not any(".venv" in p or "__pycache__" in p for p in paths(d))
    with zipfile.ZipFile(out / "bundle.zip") as z:
        assert z.namelist() == d["bundle"]["contents"]


def test_untracked_file_is_listed_untracked_and_gitignored_one_is_not_listed(tmp_path):
    root = make_project(tmp_path / "repo", extra_files={"design/.gitignore": "ignored.txt\n", "design/ignored.txt": "x"})
    (root / "design" / "fresh.md").write_text("new\n")
    out = tmp_path / "out"
    r, _m = collect(root, out)
    d = read_json(out / "files.json")
    by = {f["path"]: f for f in d["files"]}
    assert by["design/fresh.md"]["tracked"] is False and by["design/doc.md"]["tracked"] is True
    assert "design/ignored.txt" not in by


def test_no_design_folder_is_missing(tmp_path):
    root = tmp_path / "bare"
    root.mkdir()
    (root / "requirements.md").write_text("x")
    r, m = collect(root, tmp_path / "out", commit="d" * 40)
    assert r.returncode == 0 and m["records"]["files"]["status"] == "missing"


def test_C03_live_folder(tmp_path):
    out = tmp_path / "out"
    r, m = collect(REPO, out, commit="e" * 40)
    assert r.returncode == 0, r.stderr
    assert m["records"]["files"]["status"] == "ok", m["records"]["files"]
    d = read_json(out / "files.json")
    by = {f["path"]: f for f in d["files"]}
    pdf = "design/datasheets/mic_infineon_im73d122v01_en.pdf"
    assert by[pdf]["area"] == "parts" and by[pdf]["size_bytes"] == os.path.getsize(REPO / pdf)
    assert not [p for p in by if ".venv" in p or "__pycache__" in p]
    rejected = json.loads((REPO / "design" / "status.json").read_text())["look"]["rejected"]
    assert not [p for p in by if any(p.startswith(f"design/look/{x}/") for x in rejected)]
    for p, f in by.items():  # other work writes untracked files while this runs, so only tracked ones are held to the size
        if f["tracked"]:
            assert (REPO / p).is_file() and f["size_bytes"] == os.path.getsize(REPO / p), p
    with zipfile.ZipFile(out / "bundle.zip") as z:
        assert z.testzip() is None
        assert z.namelist() == d["bundle"]["contents"]
    for pid in ("requirements.md", "design/bom.csv", "design/architecture.md"):
        assert pid in by


def test_datasheets_are_indexed_not_zipped_and_named_in_the_list(tmp_path):
    from parts_support import row
    rows = [row(ref="A1", source="/Users/x/proj/design/datasheets/part_a.pdf p2 ; https://shop.example/a")]
    root = make_project(tmp_path / "repo", ring_rows=rows, extra_files=EXTRA)
    out = tmp_path / "out"
    r, _m = collect(root, out)
    assert r.returncode == 0, r.stderr
    d = read_json(out / "files.json")
    ds = "design/datasheets/part_a.pdf"
    assert ds in paths(d) and ds not in d["bundle"]["contents"]
    with zipfile.ZipFile(out / "bundle.zip") as z:
        assert ds not in z.namelist()
        lines = z.comment.decode().splitlines()
    assert "project folder" in lines[0] and "Files screen" in lines[0]
    size = os.path.getsize(root / ds)
    assert f"{ds}\t{size} bytes\thttps://shop.example/a" in lines
    assert not [n for n in z.namelist() if n.startswith("design/datasheets/")]


MFG = {
    "design/mfg/part-map.csv": "mfg_part,reference,item\nwidget,W1,Widget\nwidget,W2,Widget\ngadget,G1,Gadget\n",
    "design/mfg/parts/index.csv": "a\n",
    "design/mfg/parts/index.csv.orig": "old",
    "design/mfg/parts/make.py": "print(1)",
    "design/mfg/parts/run.sh": "x",
    "design/mfg/parts/check.log": "log",
    "design/mfg/parts/__pycache__/m.pyc": "p",
    "design/mfg/tools/draw.py": "x",
    "design/mfg/tools/notes.txt": "x",
    "design/mfg/parts/widget/widget.step": "s",
    "design/mfg/parts/widget/widget-us10.stl": "s",
    "design/mfg/parts/gadget/gadget.step": "s",
    "design/mfg/parts/mystery/mystery.step": "s",
    "design/mfg/drawings/widget-us12.pdf": "p",
    "design/mfg/drawings/widget-us12.svg": "<svg/>",
    "design/mfg/specs/gadget.md": "spec",
    "design/mfg/mfg-notes.md": "notes",
}


def test_mfg_files_get_area_part_ids_kind_and_size(tmp_path):
    root = make_project(tmp_path / "repo", extra_files=MFG)
    out = tmp_path / "out"
    r, m = collect(root, out)
    assert r.returncode == 0, r.stderr
    d = read_json(out / "files.json")
    by = {f["path"]: f for f in d["files"]}
    g = lambda n: by["design/mfg/" + n]
    assert all(f["area"] == "inside" for p, f in by.items() if p.startswith("design/mfg/"))
    assert (g("parts/widget/widget.step")["kind"], g("parts/widget/widget.step")["part_ids"], g("parts/widget/widget.step")["ring_size"]) == ("step", ["ring:W1", "ring:W2"], None)
    assert (g("parts/widget/widget-us10.stl")["kind"], g("parts/widget/widget-us10.stl")["ring_size"], g("parts/widget/widget-us10.stl")["part_ids"]) == ("stl", 10, ["ring:W1", "ring:W2"])
    assert (g("drawings/widget-us12.pdf")["kind"], g("drawings/widget-us12.pdf")["ring_size"]) == ("drawing", 12)
    assert g("drawings/widget-us12.svg")["kind"] == "view"
    assert (g("specs/gadget.md")["kind"], g("specs/gadget.md")["part_ids"]) == ("specification", ["ring:G1"])
    assert "kind" not in g("mfg-notes.md") and g("mfg-notes.md")["part_ids"] == []
    assert g("parts/mystery/mystery.step")["part_ids"] == []
    assert "mystery" in m["records"]["files"]["message"] and "widget" not in m["records"]["files"]["message"].split("part-map.csv")[1]
    # helpers and leftovers are left out of the list
    assert not [p for p in by if p.endswith((".py", ".sh", ".orig", ".pyc")) or p.startswith("design/mfg/tools/")]
    # files outside design/mfg carry none of the new fields
    assert all(not ({"kind", "part_ids", "ring_size"} & set(f)) for p, f in by.items() if not p.startswith("design/mfg/"))
    assert validate("files", out / "files.json").returncode == 0
    with zipfile.ZipFile(out / "bundle.zip") as z:
        assert not [n for n in z.namelist() if n.endswith((".py", ".sh"))]


def test_mfg_without_a_map_names_every_part_never_guesses(tmp_path):
    files = {k: v for k, v in MFG.items() if k != "design/mfg/part-map.csv"}
    root = make_project(tmp_path / "repo", extra_files=files)
    out = tmp_path / "out"
    r, m = collect(root, out)
    d = read_json(out / "files.json")
    assert all(f["part_ids"] == [] for f in d["files"] if f["path"].startswith("design/mfg/"))
    assert "widget" in m["records"]["files"]["message"]
