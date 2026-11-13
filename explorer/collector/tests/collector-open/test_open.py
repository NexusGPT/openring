"""collector-open-C01..C06: open items on made-up fixture files (no ring value comes from the real design)."""
import importlib.util
import os
import shutil
from pathlib import Path

import pytest

from conftest import COLLECTOR, read_json, run_collector

EXTRACT = Path(os.environ.get("OPEN_ITEMS_FILE", COLLECTOR / "extract" / "open_items.py"))


def load():
    spec = importlib.util.spec_from_file_location("open_items_under_test", EXTRACT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Ctx:
    def __init__(self, root):
        self.source_root = Path(root)

    def source_path(self, rel):
        return self.source_root / rel


ARCH = """# Fixture thing

Version ZV5-draft, 2026-01-01. Owner, 2026-02-03, wrote: "Make it round".

## 12. Items only a supplier can close

| # | Item | Who | What to ask for |
|---|---|---|---|
| 12.1 | Screen code | Acme Pixels | the datasheet and 5 samples |
| 12.2 | Chip pins | Chipco | the PDF |
| 12.3 | Storage | Zeta | pad drawing |
| 12.4 | Motor | a distributor | maker name |
| 12.5 | Light | Brightco | datasheet |
| 12.6 | Membrane | Goretex | die-cut |
| 12.7 | Cell | Cellco | a quote |

## 13. Choices a bench test can change

| # | Fixed choice | Test | Changes to |
|---|---|---|---|
| B1 | two mics | record a talk | one directional mic |
| B2 | budget | measure current | day rules |
| B3 | screen | measure screen | other screen |
| B4 | antenna | network analyser | new values |
| B5 | block size | wear dummies | block size |

### 16.9 Open items added by Z4

| # | Item | Who closes it |
|---|---|---|
| S1 (changed) | Smaller cell, 9 mAh minimum | Cellco |
| S8 | Outline drawing | Maker Two |
| B6 | Two switches | bench |
| ?? | Row with a strange id | someone |
| S9 | Row with no one | |

### 16.10 Cost

Owner, 2026-04-05, in order: "first words"; then "second words".

The owner said "no date here" once.
- Owner, on the curved thing: "inherits the heading date".
"""

REQS = """# Requirements

## 6. Risks

| Risk | Why | What reduces it |
|---|---|---|
| Too big | it is big | wear dummies |
| Too hot | heat | fan |
| Too dim | light | lamp |

## 7. Open decisions

| D5 | Screen control | Button | Owner, 2026-11-10: "Button plus stick" |
"""


@pytest.fixture
def root(tmp_path):
    (tmp_path / "design").mkdir()
    (tmp_path / "design" / "architecture.md").write_text(ARCH)
    (tmp_path / "requirements.md").write_text(REQS)
    return tmp_path


def extract(root):
    return load().extract(Ctx(root))


def test_C01_seven_supplier_requests_each_with_who(root):
    data, st = extract(root)
    sup = {s["id"]: s for s in data["supplier_requests"]}
    # 7 from section 12, plus S8 added later; S9 has no 'who' and is left out
    assert [s["id"] for s in data["supplier_requests"]] == [f"S{n}" for n in range(1, 9)]
    assert all(s["who"].strip() and s["ask"].strip() for s in sup.values())
    assert sup["S2"]["who"] == "Chipco" and sup["S2"]["ask"] == "the PDF" and sup["S2"]["section"] == "12"
    assert sup["S2"]["source"] == {"file": "design/architecture.md", "line": 10}
    assert len([s for s in sup.values() if s["section"] == "12"]) == 6  # S1 replaced


def test_C02_changed_row_replaces_earlier_one(root):
    data, _ = extract(root)
    s1 = [s for s in data["supplier_requests"] if s["id"] == "S1"]
    assert len(s1) == 1
    assert s1[0]["who"] == "Cellco" and "9 mAh" in s1[0]["item"] and s1[0]["section"] == "16.9"


def test_C03_bench_tests(root):
    data, _ = extract(root)
    ids = [b["id"] for b in data["bench_tests"]]
    assert ids == ["B1", "B2", "B3", "B4", "B5", "B6"]
    assert "record a talk" in data["bench_tests"][0]["detail"]


def test_C04_decisions_have_date_quote_and_readable_line(root):
    data, _ = extract(root)
    dec = data["decisions"]
    assert len(dec) >= 3
    quotes = [d["quote"] for d in dec]
    assert "Make it round" in quotes and "no date here" not in quotes
    for d in dec:
        assert len(d["date"]) == 10 and d["date"][4] == "-"
        text = (root / d["source"]["file"]).read_text().splitlines()[d["source"]["line"] - 1]
        assert d["quote"] in text
    by = {d["quote"]: d for d in dec}
    assert by["first words"]["date"] == "2026-04-05" and by["second words"]["date"] == "2026-04-05"
    assert by["Button plus stick"]["source"]["file"] == "requirements.md"


def test_C05_risks(root):
    data, _ = extract(root)
    assert [r["id"] for r in data["risks"]] == ["R1", "R2", "R3"]
    assert data["risks"][0]["text"].startswith("Too big") and "wear dummies" in data["risks"][0]["text"]


def test_C06_unreadable_rows_are_named_not_guessed(root):
    data, st = extract(root)
    assert st["status"] == "ok"
    assert "Row with a strange id" not in str(data)
    assert "'??'" in st["message"] and "S9" in st["message"]
    assert all(s["id"] != "S9" for s in data["supplier_requests"])


def test_C07_missing_architecture_is_missing(tmp_path):
    data, st = load().extract(Ctx(tmp_path))
    assert data is None and st["status"] == "missing"


def test_C08_no_section_12_is_unparsed(root):
    (root / "design" / "architecture.md").write_text("# x\n\nVersion ZV5\n")
    from lib.errors import SourceError
    with pytest.raises(SourceError):
        extract(root)


def test_C09_bench_plan_checks(root):
    (root / "design" / "bench").mkdir()
    (root / "design" / "bench" / "bench-plan.md").write_text(
        "# Plan\n\n- [CHECK 1] Find the pins. Look at the headers.\n- [CHECK 2] \n")
    data, st = extract(root)
    c = [b for b in data["bench_tests"] if b["id"].startswith("CHECK")]
    assert [b["id"] for b in c] == ["CHECK 1"] and c[0]["source"]["line"] == 3
    assert "CHECK 2" in st["message"]


def test_C10_runner_accepts_the_record(root, tmp_path):
    ext = tmp_path / "ext"
    ext.mkdir()
    shutil.copy(EXTRACT, ext / "open_items.py")
    out = tmp_path / "out"
    r = run_collector("--source", str(root), "--out", str(out), "--extractors", str(ext), "--commit", "0123456789abcdef0123456789abcdef01234567")
    assert r.returncode == 0, r.stderr
    m = read_json(out / "manifest.json")["records"]["open-items"]
    assert m["status"] == "ok", m
    assert len(read_json(out / "open.json")["supplier_requests"]) == 8
