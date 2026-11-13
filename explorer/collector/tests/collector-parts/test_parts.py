"""collector-parts: parts.json from the ring and case parts lists."""
import csv
import json
import re
import subprocess
from pathlib import Path

import pytest
from conftest import EXPLORER, read_json
from parts_support import ARCH, HEADER, bom_text, collect, make_project, row, validate

REPO = EXPLORER.parent
FIXTURE_COMMIT = "99dfb85"


def parts_of(tmp_path, **kw):
    root = make_project(tmp_path / "repo", **kw)
    out = tmp_path / "out"
    r, m = collect(root, out)
    assert r.returncode == 0, r.stderr
    return root, out, m


def line(data, ref, bom="ring"):
    return next(x for x in data["lines"] if x["bom"] == bom and ref in x["refs"])


def test_C01_columns_refs_price_and_counts(tmp_path):
    rows = [
        row(item="Main", ref="U1", function="Bluetooth, USB, 4 inputs", maker="Acme", mpn="AC-1", price="GBP 1.25", action="12.1"),
        row(item="Group", ref="U5, U6; U7, U8", qty="4", mpn="GR-4", action="12.2: Voltaic must answer the cell code"),
        row(item="Range", ref="R14-R22", qty="9", mpn="", action=""),
    ]
    _root, out, m = parts_of(tmp_path, ring_rows=rows)
    assert m["records"]["parts"]["status"] == "ok", m["records"]["parts"]
    d = read_json(out / "parts.json")
    u1 = line(d, "U1")
    assert (u1["function"], u1["maker"], u1["maker_part_number"]) == ("Bluetooth, USB, 4 inputs", "Acme", "AC-1")
    assert u1["price"] == {"amount": 1.25, "currency": "GBP", "raw": "GBP 1.25"}
    assert u1["open_action"] == "Acme Widgets: the drawing of widget W1"
    g = line(d, "U7")
    assert g["refs"] == ["U5", "U6", "U7", "U8"] and g["maker_part_number"] == "GR-4"
    assert g["part_ids"] == ["ring:U5", "ring:U6", "ring:U7", "ring:U8"]
    assert g["open_action"].startswith("12.2: Voltaic")  # text that names who stays as written
    r = line(d, "R14-R22")
    assert r["refs"] == ["R14-R22"] and r["quantity"] == 9 and r["maker_part_number"] is None and r["open_action"] is None
    assert d["totals"]["ring"] == {"lines": 3, "parts": 14, "priced_lines": 1, "unpriced_lines": 2}
    assert d["totals"]["case"]["lines"] == 1
    assert d["priced_sums"] == [{"amount": 1.25, "bom": "ring", "currency": "GBP"}]
    assert u1["source"] == {"file": "design/bom.csv", "line": 2}
    assert validate("parts", out / "parts.json").returncode == 0


def test_C01_evidence_legend_comes_from_how_to_read_this(tmp_path):
    _root, out, _m = parts_of(tmp_path)
    leg = {e["code"]: e for e in read_json(out / "parts.json")["evidence_legend"]}
    assert list(leg) == ["DS", "LIST", "CALC", "BENCH"]
    assert leg["DS"]["meaning"] == "read from the maker's datasheet."
    assert leg["DS"]["source"] == {"file": "design/architecture.md", "line": ARCH.splitlines().index("- **[DS]** = read from the maker's datasheet.") + 1}


def test_C01_case_open_action_resolves_through_case_section_8(tmp_path):
    rows = [row(ref="C1", action="S1"), row(ref="C2", action="S1 and more"), row(ref="C3", action="bench B1")]
    _root, out, _m = parts_of(tmp_path, case_rows=rows)
    d = read_json(out / "parts.json")
    assert line(d, "C1", "case")["open_action"] == "Boxco: a cell with leads"
    assert line(d, "C2", "case")["open_action"] == "Boxco: a cell with leads (and more)"
    assert line(d, "C3", "case")["open_action"] == "bench B1"
    assert line(d, "C1", "case")["part_ids"] == ["case:C1"]


def test_C01_case_made_for_older_design_is_said_in_the_message(tmp_path):
    _root, _out, m = parts_of(tmp_path)
    msg = m["records"]["parts"]["message"]
    assert "design Z1" in msg and "Z9-draft" in msg


def test_sources_are_relative_and_resolved(tmp_path):
    abs_in = str(tmp_path / "repo" / "design" / "doc.md")
    rows = [row(ref="A1", source=f"{abs_in} section 2 ; /Users/someone/other/design/doc.md ; /Users/someone/elsewhere-evidence/note.txt ; "
                                 "https://shop.example/item/1 ; doc.md 3.1 ; design/gone.pdf p2 ; section 4",
                function=f"see {abs_in}")]
    _root, out, m = parts_of(tmp_path, ring_rows=rows)
    assert m["records"]["parts"]["status"] == "ok", m["records"]["parts"]
    ln = line(read_json(out / "parts.json"), "A1")
    src = ln["sources"]
    assert [(s["path"], s["on_disk"]) for s in src] == [
        ("design/doc.md", True), ("design/doc.md", True), (None, False), (None, False),
        ("design/doc.md", True), ("design/gone.pdf", False), (None, False)]
    assert src[0]["raw"] == "design/doc.md section 2"
    assert src[2]["raw"] == "elsewhere-evidence/note.txt"
    assert src[3]["url"] == "https://shop.example/item/1"
    assert ln["function"] == "see design/doc.md"
    assert "/Users/" not in json.dumps(ln)


def test_C02_missing_reference_column_is_unparsed_exit_0(tmp_path):
    header = [c for c in HEADER if c != "reference"]
    root = make_project(tmp_path / "repo")
    (root / "design" / "bom.csv").write_text(",".join(header) + "\nThing,1,does,Maker,MP,,,,,DS,x,,\n", encoding="utf-8")
    out = tmp_path / "out"
    r, m = collect(root, out)
    assert r.returncode == 0, r.stderr
    e = m["records"]["parts"]
    assert e["status"] == "unparsed" and "bom.csv" in e["message"] and "reference" in e["message"]
    assert not (out / "parts.json").exists()


@pytest.mark.parametrize("cells,word", [
    ({"ref": ""}, "reference"),
    ({"qty": ""}, "quantity"),
    ({"qty": "two"}, "quantity"),
    ({"qty": "-1"}, "quantity"),
    ({"price": "about 3"}, "price"),
])
def test_C02_a_bad_row_is_unparsed_with_its_line(tmp_path, cells, word):
    rows = [row(ref="A1"), row(**cells)]
    root = make_project(tmp_path / "repo", ring_rows=rows)
    r, m = collect(root, tmp_path / "out")
    assert r.returncode == 0, r.stderr
    e = m["records"]["parts"]
    assert e["status"] == "unparsed" and "design/bom.csv:3" in e["message"] and word in e["message"]


def test_C02_a_history_line_with_quantity_0_is_kept_and_counts_no_part(tmp_path):
    """design/case/case-bom.csv, row PA1-PA4 of 13 November: quantity 0, 'history only, NOT fitted'. Read, kept, 0 parts; never unparsed."""
    rows = [row(item="Fitted", ref="U1"), row(item="Old", ref="PA1-PA4", qty="0", function="history only, NOT fitted: an old pin")]
    _root, out, m = parts_of(tmp_path, ring_rows=rows)
    assert m["records"]["parts"]["status"] == "ok", m["records"]["parts"]
    d = read_json(out / "parts.json")
    old = line(d, "PA1-PA4")
    assert old["quantity"] == 0 and "NOT fitted" in old["function"]
    assert d["totals"]["ring"]["lines"] == 2 and d["totals"]["ring"]["parts"] == 1


def test_C02_a_short_row_does_not_crash(tmp_path):
    root = make_project(tmp_path / "repo")
    p = root / "design" / "bom.csv"
    p.write_text(p.read_text() + "Short,S1\n", encoding="utf-8")
    r, m = collect(root, tmp_path / "out")
    assert r.returncode == 0, r.stderr
    assert m["records"]["parts"]["status"] == "unparsed" and "bom.csv:3" in m["records"]["parts"]["message"]


def test_C02_accents_and_curly_apostrophe_round_trip(tmp_path):
    item, maker = "Condénsateur d’entrée µF", "Établissements Dürr ’s"
    _root, out, _m = parts_of(tmp_path, ring_rows=[row(item=item, maker=maker, ref="K1")])
    ln = line(read_json(out / "parts.json"), "K1")
    assert (ln["item"], ln["maker"]) == (item, maker)


def test_missing_ring_list_is_missing_and_missing_case_list_only_drops_case(tmp_path):
    root = make_project(tmp_path / "repo", init_git=False)
    (root / "design" / "case" / "case-bom.csv").unlink()
    (root / "design" / "bom.csv").rename(root / "design" / "bom.old")
    r, m = collect(root, tmp_path / "o1", commit="a" * 40)
    assert r.returncode == 0 and m["records"]["parts"]["status"] == "missing"
    (root / "design" / "bom.old").rename(root / "design" / "bom.csv")
    r, m = collect(root, tmp_path / "o2", commit="a" * 40)
    d = read_json(tmp_path / "o2" / "parts.json")
    assert m["records"]["parts"]["status"] == "ok" and "case-bom.csv" in m["records"]["parts"]["message"]
    assert d["totals"]["case"]["lines"] == 0


def read_rows(path_or_text):
    text = path_or_text.read_text(encoding="utf-8") if isinstance(path_or_text, Path) else path_or_text
    import io
    return list(csv.DictReader(io.StringIO(text)))


def check_real(root, rows_ring, rows_case, tmp_path):
    out = tmp_path / "out"
    r, m = collect(root, out, commit="b" * 40)
    assert r.returncode == 0, r.stderr
    assert m["records"]["parts"]["status"] == "ok", m["records"]["parts"]
    d = read_json(out / "parts.json")
    assert d["totals"]["ring"]["lines"] == len(rows_ring) == sum(1 for x in d["lines"] if x["bom"] == "ring")
    assert d["totals"]["ring"]["parts"] == sum(int(x["quantity"]) for x in rows_ring)
    assert d["totals"]["case"]["lines"] == len(rows_case)
    assert d["totals"]["case"]["parts"] == sum(int(x["quantity"]) for x in rows_case)
    first = d["lines"][0]
    assert (first["maker"], first["maker_part_number"]) == (rows_ring[0]["maker"] or None, rows_ring[0]["maker_part_number"] or None)
    for x in rows_ring:  # every ref resolves to its own line
        ref0 = [t.strip() for t in x["reference"].replace(";", ",").split(",") if t.strip()]
        ln = line(d, ref0[0])
        assert ln["maker_part_number"] == (x["maker_part_number"] or None)
    for x in d["lines"]:
        for s in x["sources"]:
            assert s["path"] is None or not s["path"].startswith("/")
        if x["bom"] == "ring" and x["open_action"] and re.fullmatch(r"\d+\.\d+", x["open_action"]):
            pytest.fail(f"unresolved item id left as the open action of {x['part_ids']}: {x['open_action'][:40]}")
    assert validate("parts", out / "parts.json").returncode == 0
    return d


def test_C01_live_folder_counts_equal_the_file(tmp_path):
    # Other work edits the live design while tests run: snapshot the four source files once, then compare the
    # record with an independent csv read of that same snapshot (never with a number).
    snap = tmp_path / "snap"
    for rel in ("design/bom.csv", "design/architecture.md", "design/case/case-bom.csv", "design/case/case-architecture.md"):
        (snap / rel).parent.mkdir(parents=True, exist_ok=True)
        (snap / rel).write_bytes((REPO / rel).read_bytes())
    ring = read_rows(snap / "design" / "bom.csv")
    case = read_rows(snap / "design" / "case" / "case-bom.csv")
    d = check_real(snap, ring, case, tmp_path)
    assert d["evidence_legend"], "no evidence legend read from architecture.md"
    assert sum(len(x["part_ids"]) for x in d["lines"] if x["bom"] == "case") == sum(
        len([t for t in re.split(r"[,;]", x["reference"]) if t.strip()]) for x in case)


def test_C01_git_archive_copy_of_fixture_commit(tmp_path):
    ok = subprocess.run(["git", "-C", str(REPO), "cat-file", "-e", FIXTURE_COMMIT], capture_output=True)
    if ok.returncode != 0:
        pytest.skip(f"commit {FIXTURE_COMMIT} not in this repository")
    dest = tmp_path / "archive"
    dest.mkdir()
    paths = ["design/bom.csv", "design/architecture.md", "design/case/case-bom.csv", "design/case/case-architecture.md"]
    tar = subprocess.run(["git", "-C", str(REPO), "archive", FIXTURE_COMMIT, *paths], capture_output=True, check=True)
    subprocess.run(["tar", "-x", "-C", str(dest)], input=tar.stdout, check=True)
    ring = read_rows(dest / "design" / "bom.csv")
    case = read_rows(dest / "design" / "case" / "case-bom.csv")
    d = check_real(dest, ring, case, tmp_path)
    # a source path that points into the original checkout is made relative, never kept absolute
    assert "/Users/" not in json.dumps(d)
    # a section-12 id in the file resolves to a named who
    ids = [x for x in ring if re.fullmatch(r"\d+\.\d+", x["open_action"].strip())]
    assert ids, "the fixture commit has no section 12 id to check"
    for x in ids:
        ln = line(d, [t.strip() for t in x["reference"].split(",")][0])
        assert ln["open_action"] != x["open_action"].strip() and ": " in ln["open_action"]
    bt1 = line(d, "BT1")
    assert "Grepow" in bt1["open_action"] and line(d, "U7")["maker_part_number"] == next(x["maker_part_number"] for x in ring if "U7" in x["reference"])
