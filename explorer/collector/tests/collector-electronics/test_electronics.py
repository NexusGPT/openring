"""collector-electronics: the electronics and schematic-pages records on a made-up design (no ring value)."""
import json
import stat
import xml.dom.minidom

import pytest

from conftest import RUN, EXPLORER, read_json, run_collector

EXTRACT = EXPLORER / "collector" / "extract"

SCH = """(kicad_sch (version 1)
(title_block (title "Zed schematic") (rev "Z9") (comment 1 "architecture.md Z9-draft"))
(sheet (at 1 1) (size 5 5) (property "Sheetname" "Alpha block" (at 0 0 0)) (property "Sheetfile" "zed_alpha.kicad_sch" (at 0 0 0)) (instances (project "zed" (path "/x" (page "2")))))
(sheet (at 1 1) (size 5 5) (property "Sheetname" "Beta: block" (at 0 0 0)) (property "Sheetfile" "zed_beta.kicad_sch" (at 0 0 0)) (instances (project "zed" (path "/x" (page "3")))))
(sheet (at 1 1) (size 5 5) (property "Sheetname" "Gamma" (at 0 0 0)) (property "Sheetfile" "zed_gamma.kicad_sch" (at 0 0 0)) (instances (project "zed" (path "/x" (page "4")))))
)
"""
PARTS = """reference,symbol,value,mpn,footprint,sheet,dnp
U1,s,v,m,f,alpha,no
U2,s,v,m,f,alpha,no
R10,s,v,m,f,beta,no
R9,s,v,m,f,beta,no
C1,s,v,m,f,gamma,no
"""
NETLIST = """net,reference,pin_number,pin_name,pin_type
SIG_A,U1,1,x,passive
SIG_A,R9,1,x,passive
LOCAL,U1,2,x,passive
LOCAL,U2,1,x,passive
RAIL,U1,3,x,passive
RAIL,R10,1,x,passive
RAIL,C1,1,x,passive
,C1,2,x,no_connect
,U1,4,x,no_connect
,R9,2,x,no_connect
"""
OPEN = """reference,pin_number,pin_name,why_open,closed_by
U1,P1,a,w,c
U1,P2,b,w,c
R9,,value or part number,w,c
"""
ARCH = """# Zed

Version Z9-draft, 2026-01-01.

## 4. Budget

| Consumer | Recording | Standby |
|---|---|---|
| Thing | 1 mA | 0 |

## 7. Pins

| Signal | Pin | Ball | Notes |
|---|---|---|---|
| SIG_ONE | P1.01 | A1 | fast |
| SIG_TWO | P1.02 | A2 | |
| SIG_THREE | P1.03 | A3 | |

## 16. Slim

### 16.6 Pins that change

- SIG_TWO and SIG_THREE become spare test pads. SIG_ONE keeps its ball.

### 16.8 Current

- Recording 2 mA.
- Standby 0.1 mA.

### 17.5 Current again

Recording about 3 mA here.
"""
FAKE = """#!/bin/sh
if [ "$1" = "version" ]; then echo 9.9.9; exit 0; fi
out=""
while [ $# -gt 0 ]; do if [ "$1" = "-o" ]; then out="$2"; shift; fi; shift; done
for n in "zed" "zed-Alpha block" "zed-Beta: block" "zed-Gamma"; do
  printf '<svg xmlns="http://www.w3.org/2000/svg"><rect width="1" height="1"/></svg>' > "$out/$n.svg"
done
"""


@pytest.fixture
def design(tmp_path):
    root = tmp_path / "repo"
    ring = root / "design" / "ecad" / "ring"
    ring.mkdir(parents=True)
    (ring / "ring.kicad_sch").write_text(SCH)
    (ring / "parts.csv").write_text(PARTS)
    (ring / "netlist.csv").write_text(NETLIST)
    (ring / "open-pins.csv").write_text(OPEN)
    (ring / "ring-schematic.pdf").write_bytes(b"%PDF-1.4\n")
    (root / "design" / "architecture.md").write_text(ARCH)
    return root


@pytest.fixture
def fake_cli(tmp_path):
    p = tmp_path / "bin" / "kicad-cli"
    p.parent.mkdir()
    p.write_text(FAKE.replace('"zed', '"ring').replace("zed-", "ring-"))
    p.chmod(p.stat().st_mode | stat.S_IXUSR)
    return p


def collect(design, tmp_path):
    out = tmp_path / "out"
    r = run_collector("--source", str(design), "--out", str(out), "--extractors", str(EXTRACT), "--commit", "a" * 40)
    assert r.returncode == 0, r.stderr
    return out, read_json(out / "manifest.json")["records"]


def test_pages_svg_blocks_links_pins_budget(design, fake_cli, tmp_path, monkeypatch):
    monkeypatch.setenv("KICAD_CLI", str(fake_cli))
    out, recs = collect(design, tmp_path)
    assert recs["schematic-pages"]["status"] == "ok", recs["schematic-pages"]
    pages = read_json(out / "schematic" / "index.json")
    assert [p["id"] for p in pages["pages"]] == ["overview", "alpha", "beta", "gamma"]
    assert pages["exporter"]["version"] == "9.9.9"
    for p in pages["pages"]:
        xml.dom.minidom.parse(str(out / p["svg"]))  # parses as XML
        assert "/" != p["svg"][0]
    assert pages["pages"][1]["part_ids"] == ["ring:U1", "ring:U2"]
    assert recs["electronics"]["status"] == "ok", recs["electronics"]
    e = read_json(out / "electronics.json")
    assert [b["label"] for b in e["blocks"]] == ["Alpha block", "Beta: block", "Gamma"]
    assert e["blocks"][1]["part_ids"] == ["ring:R9", "ring:R10"]  # natural order
    links = {(l["from"], l["to"]): l["nets"] for l in e["links"]}
    assert links == {("alpha", "beta"): ["RAIL", "SIG_A"], ("alpha", "gamma"): ["RAIL"], ("beta", "gamma"): ["RAIL"]}
    assert len(e["pin_plan"]["rows"]) == 3
    notes = {r[0]: r[3] for r in e["pin_plan"]["rows"]}
    assert notes["SIG_ONE"] == "fast" and "spare test pad" in notes["SIG_TWO"] and "spare" in notes["SIG_THREE"]
    assert e["pin_plan"]["source"]["line"] > 1
    assert [r[1] for r in e["power_budget"]["rows"][1:]] == ["Recording 2 mA.", "Standby 0.1 mA.", "Recording about 3 mA here."]
    assert recs["electronics"]["message"].startswith("2 pin numbers are provisional")


def test_missing_kicad_cli_falls_back_to_pdf(design, tmp_path, monkeypatch):
    monkeypatch.setenv("KICAD_CLI", str(tmp_path / "no" / "such" / "kicad-cli"))
    out, recs = collect(design, tmp_path)
    assert recs["schematic-pages"]["status"] == "missing"
    assert "kicad-cli" in recs["schematic-pages"]["message"]
    pages = read_json(out / "schematic" / "index.json")
    assert all(p["svg"] is None and p["pdf"] == "design/ecad/ring/ring-schematic.pdf" for p in pages["pages"])
    assert recs["electronics"]["status"] == "ok"  # the other record does not depend on the tool


def test_failing_kicad_cli_is_unparsed_not_ok(design, tmp_path, monkeypatch):
    bad = tmp_path / "bad-cli"
    bad.write_text("#!/bin/sh\necho boom >&2\nexit 3\n")
    bad.chmod(0o755)
    monkeypatch.setenv("KICAD_CLI", str(bad))
    out, recs = collect(design, tmp_path)
    assert recs["schematic-pages"]["status"] == "unparsed" and "exited 3" in recs["schematic-pages"]["message"]


def test_svg_with_absolute_path_is_refused(design, fake_cli, tmp_path, monkeypatch):
    fake_cli.write_text(fake_cli.read_text().replace('<rect', '<text>/Users/zz/a.kicad_sch</text><rect'))
    monkeypatch.setenv("KICAD_CLI", str(fake_cli))
    out, recs = collect(design, tmp_path)
    assert recs["schematic-pages"]["status"] == "unparsed" and "absolute" in recs["schematic-pages"]["message"]


def test_no_connect_pins_make_no_link(design, fake_cli, tmp_path, monkeypatch):
    monkeypatch.setenv("KICAD_CLI", str(fake_cli))
    out, _ = collect(design, tmp_path)
    nets = {n for l in read_json(out / "electronics.json")["links"] for n in l["nets"]}
    assert "" not in nets and "LOCAL" not in nets


def test_missing_pin_table_is_unparsed(design, tmp_path, monkeypatch):
    monkeypatch.setenv("KICAD_CLI", str(tmp_path / "none"))
    (design / "design" / "architecture.md").write_text("Version Z9-draft\n\n## 7. Pins\n\nnothing\n")
    out, recs = collect(design, tmp_path)
    assert recs["electronics"]["status"] == "unparsed" and "section 7" in recs["electronics"]["message"]
