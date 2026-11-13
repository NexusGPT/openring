import pytest

from lib import csvread, md, source, version
from lib.errors import SourceError

ARCH = "Version A4-draft, 2026-11-10. Sections still describe Version A3.\n"
FW = "Version F2, 2026-11-10. Follows `design/architecture.md` version A3 (read at 15:48).\n"


def test_version_reader_handles_a4_draft_and_follows_a3():
    assert version.read_own(ARCH) == "A4-draft"
    assert version.read_follows(FW) == "A3"
    assert version.read_own(FW) == "F2"
    assert version.read_follows("no such line") is None


def test_stale_when_the_base_token_differs():
    assert version.is_stale("A3", "A4-draft")
    assert not version.is_stale("A4", "A4-draft")
    assert not version.is_stale(None, "A4")
    assert not version.is_stale("A3", None)


TEXT = """# Title

## 1. First

| A | B |
|---|---|
| a1 | b1 |
| a2 | b\\|2 |

## 2. Second

| C |
|---|
| c1 |
"""


def test_markdown_table_by_heading_with_lines():
    t = md.table_after_heading(TEXT, r"^1\. First")
    assert t["columns"] == ["A", "B"]
    assert t["rows"] == [["a1", "b1"], ["a2", "b|2"]]
    assert t["row_lines"] == [7, 8]
    assert md.table_after_heading(TEXT, r"^2\. Second")["rows"] == [["c1"]]
    assert md.table_after_heading(TEXT, r"^3\. Missing") is None


def test_csv_reader_keeps_line_numbers_across_multiline_cells(tmp_path):
    f = tmp_path / "x.csv"
    f.write_text('item,reference\n"one\ntwo",ZZ1\nthree,ZZ2\n')
    rows = csvread.read(f, required=["item", "reference"])
    assert [r["line"] for r in rows] == [2, 4]
    assert rows[0]["cells"]["item"] == "one\ntwo"


def test_csv_reader_names_a_missing_column(tmp_path):
    f = tmp_path / "x.csv"
    f.write_text("item\nzz\n")
    with pytest.raises(SourceError, match="reference"):
        csvread.read(f, required=["item", "reference"])


def test_split_refs_keeps_ranges_as_written():
    assert csvread.split_refs("U5, U6, U7, U8") == ["U5", "U6", "U7", "U8"]
    assert csvread.split_refs("R14-R22") == ["R14-R22"]
    assert csvread.split_refs("A; B") == ["A", "B"]


def test_source_pointer_refuses_absolute_and_parent_paths():
    assert source.pointer("design/a.md", 3) == {"file": "design/a.md", "line": 3}
    with pytest.raises(ValueError):
        source.pointer("/abs/a.md")
    with pytest.raises(ValueError):
        source.pointer("design/../a.md")
    with pytest.raises(ValueError):
        source.pointer("a.md", 0)


def test_relativize_turns_absolute_source_paths_into_repo_paths(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    text = f"LIST,{root}/design/parts/mcu.md section 1a ; {root}/prices.md table 1"
    assert source.relativize(text, root) == "LIST,design/parts/mcu.md section 1a ; prices.md table 1"
