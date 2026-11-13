"""collector-state-C01..C03: key numbers and area states, on made-up fixture files."""
import importlib.util
import json
import re
import shutil
from pathlib import Path

import pytest

from conftest import COLLECTOR, EXPLORER, read_json, run_collector

EXTRACT = COLLECTOR / "extract"
REAL_ROOT = EXPLORER.parent


def load(name):
    spec = importlib.util.spec_from_file_location(f"state_{name}", EXTRACT / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


facts, areas = load("facts"), load("areas")


class Ctx:
    def __init__(self, root):
        self.source_root = Path(root)

    def source_path(self, rel):
        return self.source_root / rel


ARCH_OLD = """# Fixture ring

Version ZV4, 2026-01-01.

## 1. What it is made of

One block, 11 x 7 x 5 mm, on a band.

## 2. Fixed parts

| Function | Part | Maker | Size (mm) | Key figures | Evidence |
|---|---|---|---|---|---|
| Cell | zz pouch | Zmaker | 1 x 2 x 3 | 77 mAh minimum | [CALC] |
| Storage | ZZ-STORE, 64 Gbit = 8 GB SD NAND | Zmaker | 6 x 8 | spi | [DS] |

## 4. Current budget

| Consumer | Recording | Standby |
|---|---|---|
| Chip | 3 mA | 0 |
| Hours on 77 mAh | 1,234 | 4,500 |
"""

ARCH_NEW = ARCH_OLD.replace("Version ZV4", "Version ZV5-draft") + """
## 16. Slim

### 16.1 Block

- Block: 9 x 6 x 4 mm, rounded.

### 16.4 Parts

| Function | ZV3 | ZV4 | Evidence |
|---|---|---|---|
| Cell | big | tiny, 55 mAh minimum | [CALC] |
| Storage | 8 GB | 4 GB SD NAND | [DS] |

### 16.8 Hours

- On a 55 mAh cell: 12 hours at 4.0 mA; 3 hours at 13 mA.

## 17. Thinner

### 17.1 Outside

- Block: 8.5 x 5.5 x 2 mm, rolled edge.

### 17.3 Band

- Cell capacity [CALC]: 1 x 2 x 3 = 6 cubic mm x 0.5 to 0.7 mAh per cubic mm = 21 to 27 mAh.

### 17.5 Hours

Recording about 4 mA. On 21 to 27 mAh: 5.1 to 6.7 hours at 4 mA; 1 hours at 13 mA.
"""

MASS = 'item,volume_mm3,material,mass_g,density_source\na,1,x,1.500,"Version ZV4 estimate, n"\nb,1,x,2.250,n\nTOTAL size 1,,,3.75,sum\n'

STATUS = {
    "design_version": "ZV4-draft", "updated": "2026-02-03",
    "areas": {
        "look": {"state": "in progress", "why": "w1", "who": "lead"},
        "inside": {"state": "done", "why": "w2", "who": "lead"},
        "electronics": {"state": "not started", "why": "w3", "who": "lead"},
        "board": {"state": "waiting on a supplier", "why": "w4", "who": "owner"},
        "parts": {"state": "in progress", "why": "w5", "who": "lead"},
        "behaviour": {"state": "in progress", "why": "w6", "who": "lead"},
        "case": {"state": "in progress", "why": "w7", "who": "lead"},
        "open": {"state": "waiting on a supplier", "why": "w8", "who": "owner"},
    },
    "look": {"picked": None, "rejected": ["x", "y"], "in_design": ["z"]},
}


def make(tmp_path, arch=ARCH_OLD, mass=MASS, status=STATUS, firmware=None):
    root = tmp_path / "repo"
    (root / "design" / "mech" / "out").mkdir(parents=True)
    (root / "design" / "architecture.md").write_text(arch)
    if mass is not None:
        (root / "design" / "mech" / "out" / "mass-estimate.csv").write_text(mass)
    if status is not None:
        (root / "design" / "status.json").write_text(status if isinstance(status, str) else json.dumps(status, indent=1))
    if firmware is not None:
        (root / "design" / "firmware.md").write_text(firmware)
    return root


def by_id(data, key="facts"):
    return {x["id"]: x for x in data[key]}


# ---- C01: key numbers

def test_c01_value_and_source_line_agree(tmp_path):
    root = make(tmp_path)
    data, status = facts.extract(Ctx(root))
    f = by_id(data)
    assert f["size"]["value"] == "11 x 7 x 5 mm"
    assert f["battery"]["value"] == "77 mAh"
    lines = (root / "design" / "architecture.md").read_text().splitlines()
    for fid in ("size", "battery", "hours", "storage"):
        src = f[fid]["source"]
        assert src["file"] == "design/architecture.md"
        number = re.match(r"[\d.,]+", f[fid]["value"]).group(0)
        assert number.replace(",", "") in lines[src["line"] - 1].replace(",", ""), fid
    assert f["hours"]["value"] == "1234 hours"
    assert f["storage"]["value"] == "8 GB"
    assert status["status"] == "ok"


def test_c01_newest_section_wins(tmp_path):
    data, _ = facts.extract(Ctx(make(tmp_path, arch=ARCH_NEW)))
    f = by_id(data)
    assert f["size"]["value"] == "8.5 x 5.5 x 2 mm"
    assert f["battery"]["value"] == "21 to 27 mAh"
    assert f["hours"]["value"] == "5.1 to 6.7 hours"
    assert f["storage"]["value"] == "4 GB"
    assert data["design_version"] == "ZV5-draft"


def test_c01_weight_is_the_item_sum_with_its_line(tmp_path):
    root = make(tmp_path)
    data, status = facts.extract(Ctx(root))
    w = by_id(data)["weight"]
    assert w["value"] == "3.75 g"
    line = (root / "design/mech/out/mass-estimate.csv").read_text().splitlines()[w["source"]["line"] - 1]
    assert line.startswith("TOTAL")


def test_c01_weight_not_shown_from_a_mass_file_without_or_with_an_older_version(tmp_path):
    for name, mass, word in (("none", MASS.replace("Version ZV4 estimate, ", ""), "no design version"),
                             ("old", MASS.replace("ZV4 estimate", "ZV3 estimate"), "ZV3")):
        data, status = facts.extract(Ctx(make(tmp_path / name, mass=mass)))
        assert "weight" not in by_id(data)
        assert "weight" in status["message"] and word in status["message"]
        assert status["status"] == "ok" and len(data["facts"]) == 4


def test_c01_weight_left_out_when_sum_disagrees_or_file_absent(tmp_path):
    bad = MASS.replace("3.75", "9.99")
    data, status = facts.extract(Ctx(make(tmp_path / "a", mass=bad)))
    assert "weight" not in by_id(data)
    assert "weight" in status["message"] and "9.99" in status["message"]
    data, status = facts.extract(Ctx(make(tmp_path / "b", mass=None)))
    assert "weight" not in by_id(data) and "absent" in status["message"]


def test_c01_key_numbers_table_is_read_first(tmp_path):
    arch = ARCH_NEW + "\n## Key numbers\n\n| Number | Value |\n|---|---|\n| Size | 3 x 2 x 1 mm |\n| Battery | 9 mAh |\n"
    data, _ = facts.extract(Ctx(make(tmp_path, arch=arch)))
    f = by_id(data)
    assert f["size"]["value"] == "3 x 2 x 1 mm" and f["battery"]["value"] == "9 mAh"
    assert f["hours"]["value"] == "5.1 to 6.7 hours"


def test_c01_unreadable_fact_is_left_out_and_named(tmp_path):
    arch = ARCH_OLD.replace("| Hours on 77 mAh | 1,234 | 4,500 |", "| Hours on 77 mAh | many | 4,500 |")
    data, status = facts.extract(Ctx(make(tmp_path, arch=arch)))
    assert "hours" not in by_id(data) and "hours" in status["message"]


def test_c01_missing_and_unreadable_sources(tmp_path):
    from lib.errors import SourceError
    root = make(tmp_path / "m")
    (root / "design" / "architecture.md").unlink()
    data, status = facts.extract(Ctx(root))
    assert data is None and status["status"] == "missing"
    with pytest.raises(SourceError):
        facts.extract(Ctx(make(tmp_path / "u", arch="# nothing here\n", mass=None)))


# ---- C02: area states

def test_c02_states_equal_the_file(tmp_path):
    data, status = areas.extract(Ctx(make(tmp_path)))
    assert [a["id"] for a in data["areas"]] == list(STATUS["areas"])
    for a in data["areas"]:
        assert a["state"] == STATUS["areas"][a["id"]]["state"]
        assert a["why"] == STATUS["areas"][a["id"]]["why"]
        assert a["source"]["file"] == "design/status.json"
    assert data["look"] == STATUS["look"] and data["updated"] == "2026-02-03"


def test_c02_source_line_points_at_the_area(tmp_path):
    root = make(tmp_path)
    data, _ = areas.extract(Ctx(root))
    lines = (root / "design/status.json").read_text().splitlines()
    for a in data["areas"]:
        assert f'"{a["id"]}"' in lines[a["source"]["line"] - 1]


def test_c02_no_status_file_gives_eight_unknown(tmp_path):
    data, status = areas.extract(Ctx(make(tmp_path, status=None)))
    assert len(data["areas"]) == 8
    assert {a["state"] for a in data["areas"]} == {"state unknown"}
    assert status["status"] == "missing"


def test_c02_unknown_word_is_not_passed_through(tmp_path):
    st = json.loads(json.dumps(STATUS))
    st["areas"]["inside"]["state"] = "half done"
    data, _ = areas.extract(Ctx(make(tmp_path, status=st)))
    a = by_id(data, "areas")["inside"]
    assert a["state"] == "state unknown" and "half done" in a["why"]
    assert by_id(data, "areas")["look"]["state"] == "in progress"


def test_c02_bad_json_is_unreadable(tmp_path):
    from lib.errors import SourceError
    with pytest.raises(SourceError):
        areas.extract(Ctx(make(tmp_path, status="{not json")))


def test_c02_missing_area_entry_reads_unknown(tmp_path):
    st = json.loads(json.dumps(STATUS))
    del st["areas"]["board"]
    data, _ = areas.extract(Ctx(make(tmp_path, status=st)))
    assert len(data["areas"]) == 8
    assert by_id(data, "areas")["board"]["state"] == "state unknown"


def test_c02_live_status_file_read_back():
    p = REAL_ROOT / "design" / "status.json"
    if not p.is_file():
        pytest.skip("no design/status.json in this checkout")
    live = json.loads(p.read_text())
    data, _ = areas.extract(Ctx(REAL_ROOT))
    for a in data["areas"]:
        assert a["state"] == live["areas"][a["id"]]["state"]
    assert data["look"]["rejected"] == live["look"]["rejected"]


# ---- C03: staleness

FIRMWARE_A3 = "# fw\n\nVersion F9. Follows `design/architecture.md` version ZV3 (read at noon).\n"


def test_c03_behaviour_is_stale_against_a_newer_architecture(tmp_path):
    arch = ARCH_OLD.replace("Version ZV4", "Version ZV4")
    data, status = areas.extract(Ctx(make(tmp_path, arch=arch, firmware=FIRMWARE_A3)))
    b = by_id(data, "areas")["behaviour"]
    assert b["stale"] is True and b["basis_version"] == "ZV3" and b["current_version"] == "ZV4"
    assert by_id(data, "areas")["look"]["stale"] is False


def test_c03_draft_suffix_is_the_same_version(tmp_path):
    arch = ARCH_OLD.replace("Version ZV4", "Version ZV3-draft")
    data, _ = areas.extract(Ctx(make(tmp_path, arch=arch, firmware=FIRMWARE_A3)))
    b = by_id(data, "areas")["behaviour"]
    assert b["stale"] is False and b["current_version"] == "ZV3-draft"


def test_c03_status_file_itself_made_for_older_design_turns_record_stale(tmp_path):
    root = make(tmp_path, arch=ARCH_OLD.replace("Version ZV4", "Version ZV9"))
    out = tmp_path / "bundle"
    ex = tmp_path / "ex"
    ex.mkdir()
    shutil.copy(EXTRACT / "areas.py", ex / "areas.py")
    shutil.copy(EXTRACT / "facts.py", ex / "facts.py")
    r = run_collector("--source", str(root), "--out", str(out), "--extractors", str(ex), "--commit", "a" * 40)
    assert r.returncode == 0, r.stderr
    m = read_json(out / "manifest.json")["records"]
    assert m["area-states"]["status"] == "stale"
    assert m["area-states"]["basis_version"] == "ZV4-draft" and m["area-states"]["current_version"] == "ZV9"
    assert m["key-numbers"]["status"] == "ok"
    assert m["parts"]["status"] == "missing"
    assert (out / "areas.json").is_file() and (out / "facts.json").is_file()


def test_runner_end_to_end_ok_and_no_absolute_paths(tmp_path):
    root = make(tmp_path)
    out = tmp_path / "bundle"
    ex = tmp_path / "ex"
    ex.mkdir()
    for n in ("areas", "facts"):
        shutil.copy(EXTRACT / f"{n}.py", ex / f"{n}.py")
    r = run_collector("--source", str(root), "--out", str(out), "--extractors", str(ex), "--commit", "a" * 40)
    assert r.returncode == 0, r.stderr
    m = read_json(out / "manifest.json")["records"]
    assert m["key-numbers"]["status"] == "ok", m["key-numbers"]
    assert str(tmp_path) not in (out / "facts.json").read_text() + (out / "areas.json").read_text()


def test_runner_no_status_file_still_writes_eight_unknown(tmp_path):
    root = make(tmp_path, status=None)
    out = tmp_path / "bundle"
    ex = tmp_path / "ex"
    ex.mkdir()
    shutil.copy(EXTRACT / "areas.py", ex / "areas.py")
    r = run_collector("--source", str(root), "--out", str(out), "--extractors", str(ex), "--commit", "a" * 40)
    assert r.returncode == 0, r.stderr
    assert read_json(out / "manifest.json")["records"]["area-states"]["status"] == "missing"
    assert {a["state"] for a in read_json(out / "areas.json")["areas"]} == {"state unknown"}
