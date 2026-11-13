"""collector-case link rules on a made-up parts list: no case value, only the rules of case_links.py."""
import sys
from pathlib import Path

COLLECTOR = Path(__file__).resolve().parents[2]
for p in (str(COLLECTOR), str(COLLECTOR / "extract")):
    sys.path.insert(0, p)

import case_links as L  # noqa: E402


def row(ref, function="", qty=1, source="", package="", pn=""):
    toks = [t.strip() for t in ref.split(",")]
    return {"line": 2, "tokens": toks, "ids": [f"case:{t}" for t in toks], "qty": qty, "item": "1", "function": function,
            "package": package, "size": "", "pn": pn, "source": source}


ROWS = [
    row("ZU1", "zz chip"),
    row("ZQ1-ZQ4", "zz springs"),
    row("ZM1", "zz widget holder"),
    row("ZM2", "zz cover (own part `zz_cap`)"),
    row("ZM3", "zz plate", source="design/case/out/case_plate.stl"),
    row("ZB1", "zz cell", pn="ZZC12345"),
    row("ZH1", "zz hinge pin", qty=0),
    row("ZM4", "zz screws"),
]


def test_each_rule_links_what_it_reads():
    names = ["spring_ZQ2", "widget_holder", "zz_cap", "plate", "cell_zzc12345", "ring_part_x", "chip_ZU1_left", "widget_holder_arm"]
    got = L.link_solids(names, ROWS)
    assert got["spring_ZQ2"] == {"ids": ["case:ZQ1-ZQ4"], "rule": "R0"}
    assert got["zz_cap"]["rule"] == "R1" and got["zz_cap"]["ids"] == ["case:ZM2"]
    assert got["plate"]["rule"] == "R2" and got["plate"]["ids"] == ["case:ZM3"]
    assert got["cell_zzc12345"]["rule"] == "R3" and got["cell_zzc12345"]["ids"] == ["case:ZB1"]
    assert got["widget_holder"]["rule"] == "R5" and got["widget_holder"]["ids"] == ["case:ZM1"]
    assert got["widget_holder_arm"] == {"ids": ["case:ZM1"], "rule": "R4"}
    assert "ring_part_x" not in got  # a name that matches nothing is not linked


def test_a_line_of_quantity_0_is_never_linked_to_a_solid():
    got = L.link_solids(["hinge_pin", "ZH1"], ROWS)
    assert "hinge_pin" not in got and "ZH1" not in got


def test_classes_one_per_line_and_the_counts_add_up():
    links = L.link_solids(["spring_ZQ2", "widget_holder"], ROWS)
    boards = [{"key": "main", "refs": ["ZU1", "ZM4x"]}]
    lines = L.classify(ROWS, links, boards)
    cls = {x["id"]: x["class"] for x in lines}
    assert cls["case:ZQ1-ZQ4"] == "solid" and cls["case:ZM1"] == "solid"
    assert cls["case:ZU1"] == "board" and cls["case:ZH1"] == "not-fitted"
    assert cls["case:ZM4"] == "no-solid" and [x for x in lines if x["id"] == "case:ZM4"][0]["reason"]
    n = L.counts(lines, ["spring_ZQ2", "widget_holder", "other"], links)
    assert n["solid"] + n["board"] + n["not_fitted"] + n["no_solid"] == n["lines"] == len(ROWS)
    assert (n["nodes_linked"], n["nodes_unlinked"]) == (2, 1)
