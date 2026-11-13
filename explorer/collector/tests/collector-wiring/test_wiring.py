"""collector-wiring: the connection map built from the real design/wiring/connections.md, and the checks of
collector/lib/wiringcheck.py against kept broken inputs (collector-wiring/fixtures).

Red first: each real-data test reads its subject through `subject()`. With RING_EXPLORER_BROKEN=<fixture> the same test
reads that broken fixture instead of the real data, and fails. The tests named test_checker_flags_* prove the same
from inside the suite, so the suite stays green."""
import json
import os
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import schema, wiringcheck  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "extract"))
import wiring  # noqa: E402
from realrun import ROOT, real  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures"
CONNECTIONS = ROOT / "design" / "wiring" / "connections.md"


def subject():
    """The connection map under test: the real one, or the kept broken fixture named by RING_EXPLORER_BROKEN."""
    name = os.environ.get("RING_EXPLORER_BROKEN")
    if name:
        return json.loads((FIX / name / "electronics.json").read_text(encoding="utf-8"))["connection_map"]
    return real()["electronics"]["connection_map"]


def fixture_map(name):
    return json.loads((FIX / name / "electronics.json").read_text(encoding="utf-8"))["connection_map"]


needs_design = pytest.mark.skipif(not CONNECTIONS.is_file(), reason="design/wiring/connections.md is not in this checkout")


@needs_design
def test_count_equals_the_count_the_file_states():
    text = CONNECTIONS.read_text(encoding="utf-8")
    cmap = subject()
    assert wiringcheck.check_count(cmap, text) == []
    assert len(cmap["connections"]) == wiringcheck.stated_in_file(text)


@needs_design
def test_every_connection_has_two_ends_and_an_existing_source_file():
    assert wiringcheck.check_ends_and_sources(subject(), ROOT) == []


@needs_design
def test_joints_not_drawn_or_stated_in_text_only_are_shown_open():
    text = CONNECTIONS.read_text(encoding="utf-8")
    cmap = subject()
    assert wiringcheck.open_cells(text), "the file marks no joint as not drawn or stated in text only"
    assert wiringcheck.check_open(cmap, text) == []


@needs_design
def test_the_joints_the_count_line_names_equal_the_joints_shown_open():
    text = CONNECTIONS.read_text(encoding="utf-8")
    named = wiring.stated_open(text)
    assert named, "the Count line names no joint as stated in text only"
    open_ids = {c["id"] for c in subject()["connections"] if c["drawn"]["state"] != "drawn"}
    assert open_ids == set(named), (sorted(open_ids), sorted(named))


@needs_design
def test_each_joint_shows_its_conductors_from_product_wiring_csv_and_complete_means_what_build_wiring_says():
    import csv

    rows = list(csv.DictReader((ROOT / "design" / "wiring" / "product-wiring.csv").open(encoding="utf-8", newline="")))
    build = (ROOT / "design" / "wiring" / "build_wiring.py").read_text(encoding="utf-8")
    m = re.search(r'^STATES = \[(.*?)\]', build, re.M)
    states = re.findall(r'"([^"]+)"', m.group(1))
    assert tuple(states[:2]) == wiring.COMPLETE_STATES
    by = {c["id"]: c for c in subject()["connections"]}
    want = {}
    for r in rows:
        if r["carrier_kind"] != "none":
            e = want.setdefault(r["joint"], [0, 0])
            e[1] += 1
            e[0] += r["state"] in wiring.COMPLETE_STATES
    assert want, "product-wiring.csv holds no conductor"
    got = {k: [c["conductors"]["complete"], c["conductors"]["total"]] for k, c in by.items() if "conductors" in c}
    assert got == {k: v for k, v in want.items() if k in by}, (got, want)
    assert sum(v[1] for v in got.values()) == sum(v[1] for v in want.values())


@needs_design
def test_real_output_validates_against_the_schema():
    errs = schema.validate(real()["electronics"], "electronics")
    assert errs == [], errs[:3]


@needs_design
def test_details_come_from_the_band_and_case_notes():
    by = {c["id"]: c for c in real()["electronics"]["connection_map"]["connections"]}
    assert any("lands" in d["label"] for d in by["R1"]["details"])
    assert any("lead cut length" in d["label"].lower() for d in by["R5"]["details"])
    assert any(d["label"].startswith("Wire W") for d in by["C5"]["details"])


def test_checker_flags_a_short_count():
    cmap = fixture_map("count-short")
    problems = wiringcheck.check_count(cmap, CONNECTIONS.read_text(encoding="utf-8"))
    assert any("the file states" in p for p in problems), problems


def test_checker_flags_a_connection_with_one_end_removed():
    problems = wiringcheck.check_ends_and_sources(fixture_map("one-end"), ROOT)
    assert any("1 ends, not 2" in p for p in problems), problems


def test_checker_flags_a_missing_source_file():
    problems = wiringcheck.check_ends_and_sources(fixture_map("missing-source"), ROOT)
    assert any("does not exist" in p for p in problems), problems


def test_checker_flags_a_text_only_joint_shown_as_drawn():
    problems = wiringcheck.check_open(fixture_map("text-only-shown-drawn"), CONNECTIONS.read_text(encoding="utf-8"))
    assert any("shown as drawn" in p for p in problems), problems


def test_reader_reads_both_wordings_of_the_count_line():
    assert wiring.stated_open("On 13 November R10, R15 and R16 are stated in text only.") == ["R10", "R15", "R16"]
    assert wiring.stated_open("every joint is drawn, except R16, which is stated in text only (it has no conductor).") == ["R16"]
    assert wiring.stated_open("every joint is drawn.") is None


def test_checker_flags_a_count_line_that_names_a_joint_the_map_shows_drawn():
    cmap = fixture_map("text-only-shown-drawn")
    shown = {c["id"] for c in cmap["connections"] if c["drawn"]["state"] != "drawn"}
    named = wiring.stated_open(CONNECTIONS.read_text(encoding="utf-8"))
    assert shown != set(named)
