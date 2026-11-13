"""collector-behaviour-C01..C06: the firmware rules record, on a made-up firmware file and on the real one."""
import importlib.util
from pathlib import Path

import pytest

from conftest import COLLECTOR, EXPLORER, read_json, run_collector

REAL_ROOT = EXPLORER.parent

FIRMWARE = """# Fixture firmware

Version F9, 2026-01-01. Follows `design/architecture.md` version A3 (fixture).

## 1. State machine

### 1.1 States

| State | Meaning | Microphones (VDD_MIC) | Storage (VDD_SD) | Screen | Radio |
|---|---|---|---|---|---|
| `STANDBY` | idle | off | off | on for 5 s after input | advertising |
| `RECORDING` | storing audio | on | on | off, on for 3 s after input | advertising |
| `CHARGING` | in the case | off | off | charging screen | off |

### 1.2 Transitions

| From | Event | To | Actions |
|---|---|---|---|
| `STANDBY` | long press of the record button | `RECORDING` | open; M1 |
| `STANDBY` | VBUS appears | `CHARGING` | none |
| `RECORDING` | long press of the record button | `STANDBY` | close; M2 |
| `RECORDING` | short press (a bump) | `RECORDING` | highlight marker; MH |
| `RECORDING` | double press | `RECORDING` | nothing |
| `RECORDING` | battery reaches B5 | `STANDBY` | close; M3 |
| `RECORDING` | chunk write fails 3 times | `STANDBY` | MF |
| `CHARGING` | joystick centre | `CHARGING` | none |

## 2. Controls

### 2.1 Record button

| Gesture | Timing | In `RECORDING` | In `STANDBY` | In every other state |
|---|---|---|---|---|
| Long press | held 1,000 ms; fires at the mark | stop the recording | start a recording | ignored |
| Short press | held 40 ms to 600 ms | highlight marker | screen on | screen on |
| Double press | two short presses | does nothing | does nothing | does nothing |

| Parameter | Value |
|---|---|
| Long press | 1,000 ms hold, for start and for stop |
| Short press | 40 ms to 600 ms |
| Double-press window | 400 ms after a release |

### 2.2 Joystick

- Holding a direction for 500 ms repeats it every 150 ms.

| Screen | Up | Down | Left | Right | Centre |
|---|---|---|---|---|---|
| SCR_MENU | previous | next | back | open | open |
| SCR_STATUS | none | none | none | open | open |

## 3. Feedback

### 3.1 Motor

| Id | Event | Pattern (on / off in ms) | Total ms |
|---|---|---|---|
| M1 | started | 80 on | 80 |
| M2 | stopped | 80 on, 120 off, 80 on | 280 |
| MH | highlight | 40 on | 40 |

### 3.2 Recording light

- The light is steady on exactly while VDD_MIC is on and dark while it is off.
"""

ARCH = """# Fixture architecture

Version A9-draft, 2026-01-01.

### 16.5 Thumb control

- Behind it: four SKTAAAE010 switches.
- Centre press: both switches of an opposite pair close within 40 ms.
- Record button: its own cap over one switch.

### 17.3 Band

- Switch names: SW1 = up.

### 17.8 Revision

- Flex tails: thumb side carries the record switch.
"""


def load():
    spec = importlib.util.spec_from_file_location("behaviour_under_test", COLLECTOR / "extract" / "behaviour.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Ctx:
    def __init__(self, root):
        self.source_root = Path(root)

    def source_path(self, rel):
        return self.source_root / rel


@pytest.fixture
def fixture_root(tmp_path):
    (tmp_path / "design").mkdir()
    (tmp_path / "design" / "firmware.md").write_text(FIRMWARE)
    (tmp_path / "design" / "architecture.md").write_text(ARCH)
    return tmp_path


def rules(root):
    return load().extract(Ctx(root))


def test_C01_states_transitions_motors(fixture_root):
    d, st = rules(fixture_root)
    assert st["status"] == "ok" and (st["basis_version"], st["current_version"]) == ("A3", "A9-draft")
    assert [s["id"] for s in d["states"]] == ["STANDBY", "RECORDING", "CHARGING"]
    assert [s["microphones"] for s in d["states"]] == ["off", "on", "off"]
    t = {(x["from"], x["event_kind"]): x for x in d["transitions"]}
    assert t[("STANDBY", "long_press")]["to"] == "RECORDING" and t[("STANDBY", "long_press")]["motor_ids"] == ["M1"]
    assert t[("RECORDING", "short_press")]["to"] == "RECORDING" and "highlight" in t[("RECORDING", "short_press")]["actions"]
    assert t[("RECORDING", "long_press")]["to"] == "STANDBY" and t[("RECORDING", "long_press")]["motor_ids"] == ["M2"]
    m = {p["id"]: p for p in d["motor_patterns"]}
    assert m["M1"]["pulses"] == [{"on_ms": 80, "off_ms": 0}]
    assert m["M2"]["pulses"] == [{"on_ms": 80, "off_ms": 120}, {"on_ms": 80, "off_ms": 0}] and m["M2"]["total_ms"] == 280


def test_C02_event_kinds(fixture_root):
    d, _ = rules(fixture_root)
    kinds = {x["event_text"]: x["event_kind"] for x in d["transitions"]}
    assert kinds["VBUS appears"] == "vbus"
    assert kinds["double press"] == "double_press"
    assert kinds["battery reaches B5"] == "battery"
    assert kinds["chunk write fails 3 times"] == "storage"
    assert kinds["joystick centre"] == "joystick"


def test_C03_gesture_timings_and_joystick(fixture_root):
    d, _ = rules(fixture_root)
    g = {x["kind"]: x for x in d["gestures"]}
    assert g["long_press"]["min_hold_ms"] == 1000
    assert (g["short_press"]["min_hold_ms"], g["short_press"]["max_hold_ms"]) == (40, 600)
    assert g["short_press"]["window_ms"] == 400 and g["double_press"]["window_ms"] == 400
    assert {"state": "RECORDING", "effect": "stop the recording"} in g["long_press"]["per_state"]
    assert g["joystick"]["window_ms"] == 500
    j = {x["direction"]: x["effect"] for x in d["joystick"]}
    assert set(j) == {"up", "down", "toward the hand", "toward the fingertip", "centre"}
    assert "SCR_MENU: previous" in j["up"]


def test_C04_light_rule_and_notes(fixture_root):
    d, _ = rules(fixture_root)
    assert d["light_rule"]["on_where_microphones_on"] is True
    assert [n["source"]["line"] for n in d["notes"]] == [7, 8, 9, 13, 17]
    assert all(n["source"]["file"] == "design/architecture.md" for n in d["notes"])


V7_LIGHT = "- **No recording light:** removed in v7 (architecture 17.30): the sign that a recording runs is the screen."


def test_C04b_light_removed_in_the_design_reads_as_no_light(fixture_root):
    """design/firmware.md 3.2 of 13 November: 'No recording light: removed in v7 ...' replaces 'The light is steady on exactly while VDD_MIC is on'."""
    fw = fixture_root / "design" / "firmware.md"
    fw.write_text(FIRMWARE.replace("- The light is steady on exactly while VDD_MIC is on and dark while it is off.", V7_LIGHT))
    d, _ = rules(fixture_root)
    assert d["light_rule"]["on_where_microphones_on"] is False
    assert d["light_rule"]["text"].startswith("No recording light")


def test_C04c_a_section_with_neither_statement_is_refused(fixture_root):
    """Red-first fixture: 3.2 says nothing about the light."""
    fw = fixture_root / "design" / "firmware.md"
    fw.write_text(FIRMWARE.replace("- The light is steady on exactly while VDD_MIC is on and dark while it is off.", "- Nothing is said here."))
    with pytest.raises(Exception, match="3.2 states neither"):
        rules(fixture_root)


def test_C05_failures_are_named(tmp_path):
    (tmp_path / "design").mkdir()
    assert rules(tmp_path)[0] is None and rules(tmp_path)[1]["status"] == "missing"
    fw = tmp_path / "design" / "firmware.md"
    fw.write_text(FIRMWARE.replace("| From | Event |", "| Origin | Event |"))
    with pytest.raises(Exception, match="transition"):
        rules(tmp_path)
    fw.write_text(FIRMWARE.replace("`CHARGING` | none", "`GONE` | none"))
    with pytest.raises(Exception, match="not in the state list"):
        rules(tmp_path)
    fw.write_text(FIRMWARE.replace("| 80 on | 80 |", "| 80 on | 99 |"))
    with pytest.raises(Exception, match="adds up"):
        rules(tmp_path)


def consistent(status, basis, current):
    """The contract: the record is stale exactly when both versions are known and their base tokens differ."""
    assert status in ("ok", "missing", "unparsed", "stale")
    if status in ("ok", "stale"):
        assert basis and current
        assert (status == "ok") == (basis.split("-")[0] == current.split("-")[0])


def test_C06_real_source_through_the_runner(tmp_path):
    """Structure only: the live design may change, so no version or count is pinned."""
    out = tmp_path / "out"
    r = run_collector("--source", str(REAL_ROOT), "--out", str(out), "--commit", "0" * 40)
    assert r.returncode == 0, r.stderr
    d = read_json(out / "behaviour.json")
    assert d["states"] and d["transitions"] and d["motor_patterns"]
    assert sum(1 for s in d["states"] if s["microphones"] == "on") == 1
    ids = {s["id"] for s in d["states"]}
    assert all(t["from"] in ids and t["to"] in ids for t in d["transitions"])
    man = read_json(out / "manifest.json")["records"]["firmware-rules"]
    consistent(man["status"], man["basis_version"], man["current_version"])


def test_C07_frozen_old_firmware_is_stale_with_its_counts(tmp_path):
    """A frozen copy of firmware F2 (made for A3) against a newer architecture."""
    (tmp_path / "design").mkdir()
    (tmp_path / "design" / "firmware.md").write_text((Path(__file__).parent / "fixtures" / "firmware-F2.md").read_text())
    (tmp_path / "design" / "architecture.md").write_text(ARCH)
    d, st = rules(tmp_path)
    assert (len(d["states"]), len(d["transitions"])) == (14, 60)
    assert (st["basis_version"], st["current_version"]) == ("A3", "A9-draft")
    out = tmp_path / "out"
    r = run_collector("--source", str(tmp_path), "--out", str(out), "--commit", "0" * 40)
    assert r.returncode == 0, r.stderr
    man = read_json(out / "manifest.json")["records"]["firmware-rules"]
    assert man["status"] == "stale" and man["basis_version"] == "A3"


def test_C08_the_consistency_check_catches_a_mismatch_marked_ok():
    consistent("ok", "A5-draft", "A5-draft")
    consistent("stale", "A3", "A5-draft")
    consistent("ok", "A5", "A5-draft")
    with pytest.raises(AssertionError):
        consistent("ok", "A3", "A5-draft")
    with pytest.raises(AssertionError):
        consistent("stale", "A5", "A5-draft")
