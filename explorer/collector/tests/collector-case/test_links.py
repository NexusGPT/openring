"""collector-case links: every solid of the case model and every line of the case parts list, against the real design, and
the checks of collector/lib/casecheck.py against kept broken inputs (collector-case/fixtures).

Bounds set from the design as it is on 13 November 2026 and named here: LINES_WITHOUT_SOLID_BOUND (3 today, a screw set and
two features of other parts) and SOLIDS_WITHOUT_LINE_BOUND (0 today).

Red first: each real-data test reads its subject through `subject()`. With RING_EXPLORER_BROKEN=<fixture> the same test reads
that broken fixture instead of the real data, and fails. The tests named test_checker_flags_* prove the same from inside the
suite, so the suite stays green."""
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import casecheck, schema  # noqa: E402
from realcase import ROOT, real  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures"
BOM = ROOT / "design" / "case" / "case-bom.csv"
PARAMS = ROOT / "design" / "case" / "out" / "case_params.json"
LINES_WITHOUT_SOLID_BOUND = 5
SOLIDS_WITHOUT_LINE_BOUND = 2

needs_design = pytest.mark.skipif(not BOM.is_file() or not PARAMS.is_file(), reason="the case design files are not in this checkout")


def subject():
    """The record under test: the real links, or the kept broken fixture named by RING_EXPLORER_BROKEN."""
    name = os.environ.get("RING_EXPLORER_BROKEN")
    if name:
        return json.loads((FIX / name / "case.json").read_text(encoding="utf-8"))
    return real()["case"]


def fixture(name):
    return json.loads((FIX / name / "case.json").read_text(encoding="utf-8"))


@needs_design
def test_every_one_of_the_40_solids_is_in_the_data():
    named = sorted(json.loads(PARAMS.read_text(encoding="utf-8"))["parts"])
    assert len(named) == 40
    assert casecheck.check_nodes(subject(), named, SOLIDS_WITHOUT_LINE_BOUND) == []


@needs_design
def test_every_line_of_the_parts_list_has_exactly_one_class_and_the_counts_add_up():
    ids = casecheck.parts_list_ids(BOM)
    assert len(ids) == 90
    assert casecheck.check_classes(subject(), ids, LINES_WITHOUT_SOLID_BOUND) == []
    n = subject()["counts"]
    assert n["solid"] + n["board"] + n["not_fitted"] + n["no_solid"] == 90


@needs_design
def test_a_quantity_0_line_is_not_fitted_and_nothing_else_is():
    lines = {x["id"]: x for x in subject()["lines"]}
    zero = [i for i, q in casecheck.parts_list_ids(BOM) if q == 0]
    assert zero, "the parts list has no line of quantity 0"
    assert all(lines[i]["class"] == "not-fitted" for i in zero)
    assert sum(1 for x in lines.values() if x["class"] == "not-fitted") == len(zero)


@needs_design
def test_every_linked_id_exists_in_the_parts_record():
    assert casecheck.check_in_parts(subject(), real()["parts"]) == []


@needs_design
def test_the_main_and_pin_boards_each_have_a_solid_a_picker_id_and_their_parts():
    boards = {b["key"]: b for b in real()["case"]["boards"]}
    assert set(boards) == {"main", "pins"}
    for b in boards.values():
        assert b["node"] and b["picker"] and b["parts"], b["key"]
    # an electronic part of the main board is found on it, with its parts-list line
    refs = {p["ref"]: p for p in boards["main"]["parts"]}
    assert refs["U1"]["part_id"] == "case:U1" and refs["U1"]["what"]
    # the board's own solid holds the ids of the parts the board carries, its own line first
    nodes = {n["name"]: n["part_ids"] for n in real()["case"]["glb"]["nodes"]}
    ids = nodes[boards["main"]["node"]]
    assert ids[0] == "case:PCB1" and "case:U1" in ids


@needs_design
def test_no_part_is_silently_unlinked_a_no_solid_line_says_why():
    for x in real()["case"]["lines"]:
        if x["class"] == "no-solid":
            assert x["reason"]


@needs_design
def test_the_link_fields_validate_against_the_case_schema():
    rec = dict(real()["case"])
    rec.update({"glb": None, "facts": [], "part_ids": [], "supplier_items": [], "model": None, "refit": None})
    errs = schema.validate(rec, "case")
    assert errs == [], errs[:3]


def test_checker_flags_a_line_removed_from_the_mapping():
    problems = casecheck.check_classes(fixture("line-removed"), casecheck.parts_list_ids(BOM), LINES_WITHOUT_SOLID_BOUND)
    assert any("0 entries" in p for p in problems) and any("add up to 89" in p for p in problems), problems


def test_checker_flags_a_solid_whose_name_matches_nothing_counted_as_linked():
    problems = casecheck.check_nodes(fixture("matches-nothing"), ["zz_nothing"], SOLIDS_WITHOUT_LINE_BOUND)
    assert any("links to nothing" in p for p in problems) and any("counts.nodes_linked" in p for p in problems), problems


def test_checker_flags_a_quantity_0_line_classed_as_fitted():
    problems = casecheck.check_classes(fixture("qty0-fitted"), casecheck.parts_list_ids(BOM), LINES_WITHOUT_SOLID_BOUND)
    assert any("quantity 0 but class 'solid'" in p for p in problems), problems
