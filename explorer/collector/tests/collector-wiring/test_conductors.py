"""collector-wiring, conductor lines (conductor-view-C01..C09): the list of conductors of each connection equals the lines of
design/wiring/product-wiring.csv, and each value shown is read back from the {file, line} it cites.

Red first: with RING_EXPLORER_BROKEN_CSV=remove-line or change-terminal the same real-data test compares the bundle with a broken
copy of the file (made here from the real file, so it never goes stale) and fails on that line. The test_checker_flags_* tests prove
the same from inside the suite."""
import copy
import os
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import wiringcheck  # noqa: E402
from realrun import ROOT, real  # noqa: E402

CSV = ROOT / "design" / "wiring" / "product-wiring.csv"
needs_design = pytest.mark.skipif(not CSV.is_file(), reason="design/wiring/product-wiring.csv is not in this checkout")


def cmap():
    return real()["electronics"]["connection_map"]


def broken_copy(kind, tmp_path):
    """A copy of the real file with one defect: 'remove-line' drops the W010 line; 'change-terminal' changes the pin of the first end of W010."""
    lines = CSV.read_text(encoding="utf-8").splitlines(keepends=True)
    at = next(i for i, ln in enumerate(lines) if ln.startswith("W010,"))
    if kind == "remove-line":
        del lines[at]
    else:
        import csv, io
        row = next(csv.reader(io.StringIO(lines[at])))
        row[8] = row[8] + " X"
        out = io.StringIO()
        csv.writer(out, lineterminator="\n").writerow(row)
        lines[at] = out.getvalue()
    p = tmp_path / "product-wiring.csv"
    p.write_text("".join(lines), encoding="utf-8")
    return p


def subject_csv(tmp_path):
    name = os.environ.get("RING_EXPLORER_BROKEN_CSV")
    return broken_copy(name, tmp_path) if name else CSV


@needs_design
def test_conductor_lines_equal_the_file_and_each_value_reads_back_from_its_cited_line(tmp_path):
    assert wiringcheck.check_conductor_lines(cmap(), subject_csv(tmp_path), ROOT) == []


@needs_design
def test_the_count_per_connection_equals_the_conductor_lines_of_the_file():
    rows = wiringcheck.file_rows(CSV)
    want = {}
    for _, r in rows:
        if r["carrier_kind"] != "none":
            want[r["joint"]] = want.get(r["joint"], 0) + 1
    got = {c["id"]: len(c["conductor_lines"]) for c in cmap()["connections"] if c.get("conductor_lines")}
    assert got == want
    for c in cmap()["connections"]:
        if c.get("conductor_lines"):
            assert c["conductors"]["total"] == len(c["conductor_lines"])


@needs_design
def test_conductors_of_copper_wire_spring_pin_and_inside_the_part_are_each_read_back_from_their_line():
    """At least 6 conductors spread over four kinds: each shown value equals the cell of the line it cites (read here with csv, line by line)."""
    at_line = dict(wiringcheck.file_rows(CSV))  # {first line of a row: its cells}, a row may span several lines
    shown = [k for c in cmap()["connections"] for k in c.get("conductor_lines") or []]
    picked = []
    for kind in ("copper", "wire", "spring pin", "inside the part"):
        picked += [k for k in shown if k["carrier"]["kind"] == kind][:2]
    assert len(picked) >= 6 and {k["carrier"]["kind"] for k in picked} == {"copper", "wire", "spring pin", "inside the part"}
    for k in picked:
        row = at_line[k["source"]["line"]]
        assert row["id"] == k["id"]
        assert (row["signal_A"], row["signal_B"]) == (k["signal_a"], k["signal_b"])
        assert (row["end_A_ref"], row["end_A_pin"], row["end_A_face"], row["end_A_board"]) == (k["first"]["part"], k["first"]["pin"], k["first"]["face"], k["first"]["board"])
        assert (row["end_B_ref"], row["end_B_pin"], row["end_B_face"], row["end_B_board"]) == (k["last"]["part"], k["last"]["pin"], k["last"]["face"], k["last"]["board"])
        assert (row["carrier"], row["carrier_kind"], row["state"]) == (k["carrier"]["text"], k["carrier"]["kind"], k["state"])


@needs_design
def test_a_line_without_a_conductor_is_shown_apart_with_its_reason():
    rows = [(n, r) for n, r in wiringcheck.file_rows(CSV) if r["carrier_kind"] == "none"]
    assert rows, "the file holds no line without a conductor"
    shown = {k["id"]: k for c in cmap()["connections"] for k in c.get("no_conductor") or []}
    for n, r in rows:
        assert shown[r["id"]]["reason"] == r["carrier"] and shown[r["id"]]["source"]["line"] == n
        assert r["id"] not in {k["id"] for c in cmap()["connections"] for k in c.get("conductor_lines") or []}


@needs_design
def test_the_whole_product_count_equals_the_file():
    rows = [r for _, r in wiringcheck.file_rows(CSV) if r["carrier_kind"] != "none"]
    f = cmap()["conductor_file"]
    assert f["status"] == "ok" and f["total"] == len(rows)
    assert f["complete"] == sum(r["state"] in ("drawn and routed", "specified and landed") for r in rows)


@needs_design
def test_checker_flags_a_removed_line(tmp_path):
    problems = wiringcheck.check_conductor_lines(cmap(), broken_copy("remove-line", tmp_path), ROOT)
    assert any(p.startswith("W010:") for p in problems), problems


@needs_design
def test_checker_flags_a_changed_terminal(tmp_path):
    problems = wiringcheck.check_conductor_lines(cmap(), broken_copy("change-terminal", tmp_path), ROOT)
    assert any(p.startswith("W010: first terminal pin") for p in problems), problems


@needs_design
def test_checker_flags_a_dropped_conductor_and_a_wrong_state():
    m = copy.deepcopy(cmap())
    c = next(c for c in m["connections"] if c.get("conductor_lines"))
    c["conductor_lines"][0]["state"] = "zz"
    first_id = c["conductor_lines"][0]["id"]
    assert any(p.startswith(f"{first_id}: state") for p in wiringcheck.check_conductor_lines(m, CSV, ROOT))
    c["conductor_lines"].pop(1)
    assert any("conductors shown" in p for p in wiringcheck.check_conductor_lines(m, CSV, ROOT))
