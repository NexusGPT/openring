"""collector-screens: the ring software's pictures of the screen states, against the real design (design/software/os/screens)
and kept broken inputs (collector-screens/fixtures). Check ids screen-face-C01..C09.

Red first: each real-data test reads its subject through `states()`. With RING_EXPLORER_BROKEN=<fixture> the same test reads
that fixture's patch applied to the real states, and fails. The tests named test_checker_flags_* prove the same from inside
the suite, so the suite stays green."""
import copy
import json
import os
import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import schema, screencheck  # noqa: E402
from realscreens import EXPLORER, SOURCE, real  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures"
DATA = EXPLORER / "public" / "data"
needs_design = pytest.mark.skipif(not (SOURCE / "manifest.md").is_file(), reason="the ring software's picture set is not in this checkout")

# The states of firmware.md 3.3 and the picture each one shows, read off manifest.md by hand: the first picture of the
# manifest whose scene names the state (SCR_STATUS: the scene "STANDBY ...", SCR_CHARGING: "CHARGING ..."). None = no picture.
EXPECTED = {
    "SCR_STATUS": "status", "SCR_NOTIFS": "notifications-empty", "SCR_NOTIF": "notification", "SCR_RECORDING": "recording",
    "SCR_REC_DIM": "recording-idle", "SCR_MENU": "menu", "SCR_RECORDINGS": None, "SCR_RECORDING_INFO": None,
    "SCR_SETTINGS": "settings", "SCR_CONFIRM": "confirm", "SCR_PAIR": "pairing", "SCR_MODES": "modes",
    "SCR_CONTROL": "control-media", "SCR_DEVICES": "devices", "SCR_DEVICE": "device", "SCR_MESSAGE": "message",
    "SCR_CHARGING": "charging", "SCR_TRANSFER": None, "SCR_ERROR": None, "SCR_RECOVERY": None, "SCR_FACTORY": None,
}


def patched(states, patch):
    out = copy.deepcopy(states)
    for s in out:
        key = re.match(r"\w+", s["state"]).group(0)
        if key in patch:
            for k, v in patch[key].items():
                if k == "pictures":
                    base = (s.get("pictures") or [{}])[0]
                    s["pictures"] = [{**base, **v[0]}]
                    s.pop("picture_words", None)
                elif v is None:
                    s.pop(k, None)
                    s.pop("pictures", None)
                else:
                    s[k] = v
    return out


def states():
    """The states under test: the real ones, or the broken fixture named by RING_EXPLORER_BROKEN."""
    st = real()["states"]
    name = os.environ.get("RING_EXPLORER_BROKEN")
    if name:
        return patched(st, json.loads((FIX / name / "patch.json").read_text(encoding="utf-8")))
    return st


def problems(st):
    r = real()
    return screencheck.check(st, r["bundle"], r["manifest"], SOURCE)


@needs_design
def test_screen_face_C01_the_record_has_the_21_states_and_the_manifest_the_21_pictures():
    assert len(real()["states"]) == 21
    assert len(screencheck.manifest(real()["manifest"])) == 21
    assert len([f for f in SOURCE.glob("*.png") if not f.name.endswith("-4x.png") and f.name != "all-screens.png"]) == 21


@needs_design
def test_screen_face_C02_every_state_has_a_picture_in_the_data_folder_or_words_that_it_has_none():
    assert problems(states()) == []


@needs_design
def test_screen_face_C03_the_state_to_picture_mapping_equals_the_one_read_off_the_manifest():
    got = {re.match(r"\w+", s["state"]).group(0): (s["pictures"][0]["name"] if s.get("pictures") else None) for s in states()}
    assert got == EXPECTED
    with_picture = [k for k, v in got.items() if v]
    assert len(with_picture) == 15 and len(got) - len(with_picture) == 6


@needs_design
def test_screen_face_C04_all_21_pictures_are_in_the_record_once_and_a_state_without_one_says_so_in_words():
    st = states()
    names = [p["name"] for s in st for p in s.get("pictures", [])]
    assert sorted(names) == sorted(screencheck.manifest(real()["manifest"]))
    for s in st:
        if not s.get("pictures"):
            assert s["picture_words"] == "The ring software has no picture for this screen."


@needs_design
def test_screen_face_C05_the_copies_are_the_source_pictures_byte_for_byte():
    r = real()
    for s in r["states"]:
        for p in s.get("pictures", []):
            assert screencheck.sha(r["bundle"] / p["file"]) == screencheck.sha(SOURCE / f"{p['name']}.png") == p["sha256"]
            assert (p["width"], p["height"], p["scale"]) == (240, 120, 4)


@needs_design
def test_screen_face_C06_the_picture_has_the_aspect_and_pixel_pitch_of_the_lit_area_of_the_record():
    # 21.6 x 10.8 mm lit area (placement.csv line 24) / 240 x 120 pixels = 0.09 mm each way, so a pixel is square
    note = (SOURCE.parents[3] / "design" / "mech" / "thin" / "placement.csv").read_text(encoding="utf-8").splitlines()[23]
    m = re.search(r"lit area\s+([\d.]+)\s*\(X\)\s*x\s*([\d.]+)\s*\(Y\)", note)
    w, h = float(m.group(1)), float(m.group(2))
    assert abs(w / 240 - h / 120) < 1e-9


@needs_design
def test_screen_face_C07_every_picture_has_a_pure_black_outer_frame():
    out = []
    for f in sorted(SOURCE.glob("*.png")):
        if f.name != "all-screens.png":
            out += screencheck.border_problems(f.read_bytes(), f.name)
    assert out == []


@needs_design
def test_screen_face_C08_the_record_validates_against_its_schema():
    rec = {"design_version": None, "exterior": {"status": "absent", "look_id": None, "file": None, "source": None},
           "internals": {"file": "x.glb", "node_count": 0, "source": {"file": "a", "line": None}}, "nodes": [], "block": {"size_mm": {"x": 1, "y": 1, "z": 1}, "source": {"file": "a", "line": 1}},
           "band": {"width_mm": 1, "inner_diameter_mm": 1, "source": {"file": "a", "line": 1}},
           "screens": {"rect": {"cx": 0, "cy": 0, "w": 21.6, "h": 10.8, "source": {"file": "a", "line": 1}}, "states": states()}}
    assert schema.validate(rec, "ring-model") == []


@pytest.mark.skipif(not (DATA / "ring-model.json").is_file(), reason="npm run collect has not been run")
def test_screen_face_C09_the_collected_data_folder_holds_what_the_record_says():
    rec = json.loads((DATA / "ring-model.json").read_text(encoding="utf-8"))
    assert screencheck.check(rec["screens"]["states"], DATA, (SOURCE / "manifest.md").read_text(encoding="utf-8"), SOURCE) == []


# ---- the checker itself, against the kept broken inputs ----

@needs_design
@pytest.mark.parametrize("name,fragment", [("missing-file", "zz-missing.png is not in the data folder"), ("wrong-state", "belongs to 2 states"), ("no-words", "must have pictures or words")])
def test_checker_flags_the_kept_broken_fixture(name, fragment):
    st = patched(real()["states"], json.loads((FIX / name / "patch.json").read_text(encoding="utf-8")))
    got = problems(st)
    assert any(fragment in p for p in got), got


@needs_design
def test_checker_flags_a_picture_whose_bytes_changed(tmp_path):
    r = real()
    import shutil
    b = tmp_path / "bundle"
    shutil.copytree(r["bundle"], b)
    f = b / "screens" / "menu.png"
    f.write_bytes(f.read_bytes()[:-1] + b"\x00")
    got = screencheck.check(r["states"], b, r["manifest"], SOURCE)
    assert any("screens/menu.png" in p and "differs" in p for p in got), got


def test_checker_flags_a_picture_that_is_not_black_at_the_edge():
    import struct
    import zlib

    def png(w, h, px):
        raw = b"".join(b"\x00" + b"".join(bytes(px(x, y)) for x in range(w)) for y in range(h))
        chunk = lambda k, d: struct.pack(">I", len(d)) + k + d + struct.pack(">I", zlib.crc32(k + d))
        return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")

    assert screencheck.border_problems(png(6, 4, lambda x, y: (0, 0, 0)), "ok") == []
    assert screencheck.border_problems(png(6, 4, lambda x, y: (0, 0, 9) if (x, y) == (5, 2) else (0, 0, 0)), "bad")
