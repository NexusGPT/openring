"""collector-boards: the boards list built from the real board files, and the checks of collector/lib/boardcheck.py against
kept broken inputs (collector-boards/fixtures/<name>/board/...).

Red first: each real-data test reads its subject through `subject()`. With RING_EXPLORER_BROKEN=<fixture> the same test reads
that broken fixture instead of the real data, and fails. The tests named test_checker_flags_* prove the same from inside the
suite, so the suite stays green."""
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "collector-wiring"))

from lib import boardcheck, schema  # noqa: E402
from realrun import ROOT, real  # noqa: E402

sys.path.insert(0, str(ROOT / "explorer" / "collector" / "extract"))
import schematic  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures"

needs_kicad = pytest.mark.skipif(schematic._tool() is None, reason="kicad-cli is not on this machine")


def subject():
    """(boards, bundle folder, source root) under test: the real ones, or the kept broken fixture named by RING_EXPLORER_BROKEN."""
    name = os.environ.get("RING_EXPLORER_BROKEN")
    if name:
        return fixture(name)
    r = real()
    return r["board"]["boards"], r["bundle"], r["root"]


def fixture(name):
    d = FIX / name
    return json.loads((d / "board" / "index.json").read_text(encoding="utf-8"))["boards"], d, ROOT


@needs_kicad
def test_every_board_has_its_file_and_a_copper_layer_picture_that_is_not_empty():
    boards, bundle, root = subject()
    assert boardcheck.check_files_and_layers(boards, bundle, root) == []


@needs_kicad
def test_the_list_holds_the_ring_board_14_band_circuits_and_2_case_boards():
    boards = real()["board"]["boards"]
    groups = [b["group"] for b in boards]
    assert groups.count("ring") == 1
    assert groups.count("band-1") == 7 and groups.count("band-2") == 7  # two circuits per ring size, US 7 to 13
    assert groups.count("case-main") == 1 and groups.count("case-pins") == 1
    assert len(boards) == 17
    for g in ("band-1", "band-2"):
        assert {b["size_label"] for b in boards if b["group"] == g} == {f"US {n}" for n in range(7, 14)}


@needs_kicad
def test_each_state_equals_the_count_lines_of_its_rules_report():
    boards, bundle, _root = subject()
    assert boardcheck.check_states(boards, bundle) == []


@needs_kicad
def test_a_board_whose_report_counts_open_connections_is_not_finished():
    boards, bundle, _root = subject()
    assert boardcheck.check_ring_not_finished(boards, bundle) == []


@needs_kicad
def test_the_ring_board_state_is_not_finished_while_its_report_counts_open_connections():
    boards, bundle, _root = subject()
    ring = next(b for b in boards if b["group"] == "ring")
    v, o = boardcheck.report_numbers((Path(bundle) / ring["state"]["report"]).read_text(encoding="utf-8"))
    if o:
        assert ring["state"]["status"] == "not-finished"
        assert ring["state"]["words"].startswith("not finished: ")
    else:
        assert ring["state"]["status"] in ("routed-checked", "not-finished")


@needs_kicad
def test_real_output_validates_against_the_schema():
    errs = schema.validate(real()["board"], "board-files")
    assert errs == [], errs[:3]


@needs_kicad
def test_each_board_names_its_parts_on_each_face():
    for b in real()["board"]["boards"]:
        assert b["placements"], b["id"]
        assert {p["side"] for p in b["placements"]} <= {"top", "bottom"}


def test_checker_flags_a_board_whose_file_is_missing():
    boards, bundle, root = fixture("no-file")
    problems = boardcheck.check_files_and_layers(boards, bundle, root)
    assert any("is not on disk" in p for p in problems), problems


def test_checker_flags_an_empty_layer_file():
    boards, bundle, root = fixture("empty-layer")
    problems = boardcheck.check_files_and_layers(boards, bundle, root)
    assert any("no picture file" in p or "holds no drawing" in p or "empty" in p for p in problems), problems


def test_checker_flags_a_state_that_differs_from_its_report():
    boards, bundle, _root = fixture("state-vs-report")
    problems = boardcheck.check_states(boards, bundle)
    assert any("the report says 0 and 3" in p for p in problems), problems


def test_checker_flags_a_ring_board_called_routed_while_its_report_counts_open_connections():
    boards, bundle, _root = fixture("ring-claims-routed")
    problems = boardcheck.check_ring_not_finished(boards, bundle)
    assert any("counts 3 open connections" in p for p in problems), problems
