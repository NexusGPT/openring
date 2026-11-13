"""Made-up fixture project for the collector-parts tests: no ring value is written here."""
import csv
import io
import json
import subprocess
import sys
from pathlib import Path

from conftest import COLLECTOR, EXPLORER, read_json, run_collector

EXTRACT = COLLECTOR / "extract"
HEADER = ["item", "reference", "quantity", "function", "maker", "maker_part_number", "package", "size_mm", "value",
          "key_figures", "evidence", "source_file_or_url", "unit_price_and_currency_at_qty1", "open_action"]
ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
       "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin"}

ARCH = """# Zed system

Version Z9-draft, 2026-01-01.

How to read this:
- Every item has ONE fixed choice.
- **[DS]** = read from the maker's datasheet.
- **[LIST]** = from a listing only.
- **[CALC]** = calculated here.
- **[BENCH]** = one named test can change it.

## 1. Things

## 12. Items only a supplier can close

| # | Item | Who | What to ask for |
|---|---|---|---|
| 12.1 | Widget drawing | Acme Widgets | the drawing of widget W1 |
| 12.2 | Cell | Voltaic | a quote for the cell |

## 13. Other
"""
CASE_ARCH = """# Case architecture (version C2)

Built against `design/architecture.md` version Z1 and `requirements.md` section 2.7.

## 8. Items only a supplier can close

| # | Item | Who | What to ask |
|---|---|---|---|
| S1 | Cell | Boxco | a cell with leads |
"""


def bom_text(rows, header=HEADER):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def row(item="Thing", ref="X1", qty="1", function="does a thing", maker="Maker", mpn="MP-1", package="", size="",
        value="", figures="", evidence="DS", source="design/doc.md section 1", price="", action=""):
    return [item, ref, qty, function, maker, mpn, package, size, value, figures, evidence, source, price, action]


def git_init(root):
    for cmd in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "zz"]):
        subprocess.run(["git", "-C", str(root), *cmd], check=True, env=ENV, capture_output=True)


def make_project(root, ring_rows=None, case_rows=None, ring_header=HEADER, extra_files=None, init_git=True):
    root = Path(root)
    (root / "design" / "case").mkdir(parents=True, exist_ok=True)
    ring_rows = ring_rows if ring_rows is not None else [row()]
    case_rows = case_rows if case_rows is not None else [row(ref="C1", item="1")]
    (root / "design" / "bom.csv").write_text(bom_text(ring_rows, ring_header), encoding="utf-8")
    (root / "design" / "case" / "case-bom.csv").write_text(bom_text(case_rows), encoding="utf-8")
    (root / "design" / "architecture.md").write_text(ARCH, encoding="utf-8")
    (root / "design" / "case" / "case-architecture.md").write_text(CASE_ARCH, encoding="utf-8")
    (root / "design" / "doc.md").write_text("doc\n")
    for n in ("requirements.md", "feasibility.md", "partners.md"):
        (root / n).write_text("zz\n")
    for rel, content in (extra_files or {}).items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, int):
            with p.open("wb") as fh:
                fh.truncate(content)
        elif isinstance(content, bytes):
            p.write_bytes(content)
        else:
            p.write_text(content, encoding="utf-8")
    if init_git:
        git_init(root)
    return root


def collect(root, out, commit=None):
    args = ["--source", str(root), "--out", str(out), "--extractors", str(EXTRACT)]
    if commit:
        args += ["--commit", commit]
    r = run_collector(*args)
    manifest = read_json(Path(out) / "manifest.json") if (Path(out) / "manifest.json").exists() else None
    return r, manifest


def validate(record, path):
    return run_collector("--validate", record, str(path))
