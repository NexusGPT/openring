"""part-notes-C01 and part-notes-C02: content/part-notes.json against the parts lists and the architecture.

Each check is a function that returns a list of problems; the tests assert the real file gives none
and that a broken copy gives the expected problem (so each check is seen failing)."""
import copy
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
EXPLORER = HERE.parents[3]
sys.path.insert(0, str(EXPLORER / "collector"))
from lib import records, schema  # noqa: E402

DESIGN = EXPLORER.parent / "design"
NOTES = EXPLORER / "content" / "part-notes.json"
RING_BOM = DESIGN / "bom.csv"
CASE_BOM = DESIGN / "case" / "case-bom.csv"
CASE_PARAMS = DESIGN / "case" / "out" / "case_params.json"
THIN_PLACEMENT = DESIGN / "mech" / "thin" / "placement.csv"
ARCH = DESIGN / "architecture.md"


def refs(cell):
    return [t.strip() for t in re.split(r"[,;]", cell) if t.strip()]


def bom_rows(path):
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_notes():
    return json.loads(NOTES.read_text(encoding="utf-8"))["notes"]


def ring_ids():
    """{id: line number in bom.csv (header is line 1)} and the list of ring lines as id lists."""
    ids, lines = {}, []
    for n, r in enumerate(bom_rows(RING_BOM), start=2):
        rl = ["ring:" + t for t in refs(r["reference"])]
        lines.append((n, rl))
        for i in rl:
            ids[i] = n
    return ids, lines


# Parts of bom.csv that have no note yet (13 November 2026: lines added to the parts list after the notes were written). A note is never
# invented for them; the card for such a part says it has no plain-words note. The list must shrink: a part that gets a note leaves it.
NO_NOTE_YET = set()  # 2026-11-13: C25, C84, C89, FRM1, LT1 and RC1 have their notes; every ring line of the parts list is covered


def check_coverage(notes):
    """part-notes-C01 (coverage): every ring line has a note for each of its refs; no ring id outside the bom."""
    ids, lines = ring_ids()
    problems = []
    for n, rl in lines:
        for i in rl:
            if i not in notes and i not in NO_NOTE_YET:
                problems.append(f"bom.csv line {n}: no note for {i}")
            if i in notes and i in NO_NOTE_YET:
                problems.append(f"{i} has a note: take it out of NO_NOTE_YET")
    case_refs = {"case:" + t for r in bom_rows(CASE_BOM) for t in refs(r["reference"])}
    for k in notes:
        if k.startswith("ring:") and k not in ids:
            problems.append(f"{k}: not in bom.csv")
        if k.startswith("case:") and k not in case_refs:
            problems.append(f"{k}: not in case-bom.csv")
    return problems


def check_limits(notes):
    c = records.constants()
    problems = []
    for k, v in notes.items():
        if len(v["what"].split()) > c["NOTE_WHAT_WORDS"]:
            problems.append(f"{k}: what has {len(v['what'].split())} words, limit {c['NOTE_WHAT_WORDS']}")
        if len(v["why"].split()) > c["NOTE_WHY_WORDS"]:
            problems.append(f"{k}: why has {len(v['why'].split())} words, limit {c['NOTE_WHY_WORDS']}")
    return problems


FIXTURE_PLACEMENT = HERE.parent / "fixtures" / "placement.csv"
GEN = HERE.parent / "gen_notes.py"


def ring_placement_names(path=THIN_PLACEMENT):
    """None when the inside model's table is not written yet; else the part and reference columns."""
    if not path.exists():
        return None
    names = set()
    for r in bom_rows(path):
        names.update(x for x in (r.get("part"), r.get("reference")) if x)
    return names


def check_model_names(notes, placement=THIN_PLACEMENT):
    problems = []
    ring = ring_placement_names(placement)
    case = set(json.loads(CASE_PARAMS.read_text(encoding="utf-8"))["parts"])
    for k, v in notes.items():
        for m in v["model_names"]:
            if k.startswith("case:"):
                if m not in case:
                    problems.append(f"{k}: model name {m} not in case_params.json parts")
            elif ring is None:
                problems.append(f"{k}: model name {m} given but design/mech/thin/placement.csv does not exist")
            elif m not in ring:
                problems.append(f"{k}: model name {m} not in thin placement.csv")
    return problems


UNIT = r"(?:mAh|mm|kohm|ohm|uF|nF|pF|uH|nH|kHz|MHz|GHz|mA|uA|V|Wh|GB|MB|mg|g|ms|hours?|degrees?|percent)"
FIG = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)\s*" + UNIT + r"\b")


def check_figures(notes):
    """part-notes-C02: each number with a unit in a note appears in the line's row or in the architecture."""
    arch = ARCH.read_text(encoding="utf-8")
    rows = {"ring:" + t: " ".join(r.values()) for r in bom_rows(RING_BOM) for t in refs(r["reference"])}
    rows.update({"case:" + t: " ".join(r.values()) for r in bom_rows(CASE_BOM) for t in refs(r["reference"])})
    problems = []
    for k, v in notes.items():
        for fld in ("what", "why"):
            for m in FIG.finditer(v[fld]):
                num = m.group(1)
                hay = rows.get(k, "") + " " + arch
                if not re.search(r"(?<![\w.])" + re.escape(num) + r"(?![\w.])", hay):
                    problems.append(f"{k} {fld}: figure '{m.group(0)}' is in no row and not in architecture.md")
    return problems


def check_shape(doc):
    return schema.validate(doc, "content/part-notes")


# ---- the real file passes

def test_schema_valid():
    assert check_shape(json.loads(NOTES.read_text(encoding="utf-8"))) == []


def test_every_ring_line_covered():
    ids, lines = ring_ids()
    notes = load_notes()
    assert check_coverage(notes) == []
    covered = sum(1 for _, rl in lines if all(i in notes or i in NO_NOTE_YET for i in rl))
    print(f"ring lines covered: {covered}/{len(lines)}; ring ids {len(ids)}")
    assert covered == len(lines)


def test_bt1_starts_battery_cell():
    assert load_notes()["ring:BT1"]["what"].startswith("Battery cell")


def test_word_limits():
    assert check_limits(load_notes()) == []


def test_model_names_exist():
    # case names are checked against case_params.json; ring names against the fixture (live table: see the C03 report)
    case_only = {k: v for k, v in load_notes().items() if k.startswith("case:")}
    assert check_model_names(case_only) == []


def test_no_invented_figures():
    assert check_figures(load_notes()) == []


def test_notes_are_plain():
    # no blank fields, no bare codes like "12.2" or "NEW-6" in a note
    for k, v in load_notes().items():
        for fld in ("what", "why", "checked_against"):
            assert v[fld].strip(), f"{k} {fld} blank"
        assert not re.search(r"\bNEW-\d+|\b12\.\d\b", v["what"] + v["why"]), k


# ---- each check seen failing on a broken copy

def test_mutation_missing_note_named():
    n = load_notes()
    del n["ring:U1"]
    assert any("ring:U1" in p and "no note" in p for p in check_coverage(n))


def test_mutation_note_for_a_part_listed_as_without_note_is_named(monkeypatch):
    # the list is empty since 2026-11-13 (every ring line has its note): the rule is kept alive on a planted entry
    monkeypatch.setitem(globals(), "NO_NOTE_YET", {"ring:FRM1"})
    n = copy.deepcopy(load_notes())
    n["ring:FRM1"] = copy.deepcopy(n["ring:U1"])
    assert any("take it out of NO_NOTE_YET" in p for p in check_coverage(n))


def test_mutation_id_not_in_bom_named():
    n = load_notes()
    n["ring:ZZ99"] = copy.deepcopy(n["ring:U1"])
    assert any("ring:ZZ99" in p and "not in bom.csv" in p for p in check_coverage(n))


def test_mutation_word_limit():
    n = load_notes()
    n["ring:U1"]["what"] = " ".join(["word"] * 40)
    assert any("ring:U1" in p for p in check_limits(n))


def test_mutation_model_name_unknown():
    n = load_notes()
    n["case:U1"]["model_names"] = ["no_such_object"]
    assert any("case:U1" in p for p in check_model_names(n))
    n["ring:U1"]["model_names"] = ["no_such_object"]
    assert any("ring:U1" in p for p in check_model_names(n, FIXTURE_PLACEMENT))


def test_mutation_invented_figure():
    n = load_notes()
    n["ring:BT1"]["why"] = "It stores 153 mAh."
    assert any("153 mAh" in p for p in check_figures(n))


def test_mutation_shape():
    doc = {"notes": {"ring:U1": {"what": "x", "why": "", "checked_against": "a", "model_names": []}}}
    assert check_shape(doc)


# ---- part-notes-C03: report against the LIVE design/bom.csv (never a gate)

def live_report(notes, bom_path=RING_BOM):
    """(lines with no note, ring note ids with no line) against the bom at bom_path."""
    have, no_note = set(), []
    for n, r in enumerate(bom_rows(bom_path), start=2):
        for t in refs(r["reference"]):
            have.add("ring:" + t)
            if "ring:" + t not in notes:
                no_note.append(f"bom.csv line {n}: ring:{t}")
    no_line = sorted(k for k in notes if k.startswith("ring:") and k not in have)
    return no_note, no_line


def test_live_report_never_fails():
    no_note, no_line = live_report(load_notes())
    print(f"part-notes-C03 live bom: {len(no_note)} lines with no note, {len(no_line)} notes with no line")
    for x in no_note + no_line:
        print("  ", x)
    assert isinstance(no_note, list) and isinstance(no_line, list)


def test_mutation_live_report_names_removed_line():
    n = load_notes()
    first = bom_rows(RING_BOM)[0]["reference"].split(",")[0].strip()
    del n["ring:" + first]
    no_note, _ = live_report(n)
    assert any(f"ring:{first}" in x and "line 2" in x for x in no_note)


# ---- the generator reproduces the wording; model names are checked on a fixture, reported on the live table

def run_gen(out, placement=None):
    import subprocess
    cmd = [sys.executable, "-I", str(GEN), str(out)] + ([str(placement)] if placement else [])
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    return json.loads(Path(out).read_text(encoding="utf-8"))["notes"]


def wording(notes):
    return {k: {f: v[f] for f in ("what", "why", "checked_against")} for k, v in notes.items()}


def check_wording(committed, regenerated):
    return [f"{k}: wording differs from gen_notes.py" for k in sorted(set(committed) | set(regenerated))
            if wording(committed).get(k) != wording(regenerated).get(k)]


def test_generator_reproduces_wording(tmp_path):
    regen = run_gen(tmp_path / "regen.json")
    assert check_wording(load_notes(), regen) == []


def test_mutation_wording_edit_is_caught(tmp_path):
    regen = run_gen(tmp_path / "regen.json")
    n = load_notes()
    n["ring:U1"]["what"] += " extra"
    assert any("ring:U1" in p for p in check_wording(n, regen))


def test_every_fixture_object_is_linked(tmp_path):
    notes = run_gen(tmp_path / "fx.json", FIXTURE_PLACEMENT)
    linked = {m for k, v in notes.items() if k.startswith("ring:") for m in v["model_names"]}
    parts = {r["part"] for r in bom_rows(FIXTURE_PLACEMENT)}
    assert parts - linked == set()
    assert notes["ring:DISP1"]["model_names"] == ["screen", "screen_tail"]
    assert check_model_names(notes, FIXTURE_PLACEMENT) == []


def test_mutation_unlinked_fixture_object_is_caught(tmp_path):
    notes = run_gen(tmp_path / "fx.json", FIXTURE_PLACEMENT)
    notes["ring:BT1"]["model_names"] = []
    linked = {m for k, v in notes.items() for m in v["model_names"]}
    assert "cell" not in linked


def live_model_report(notes, placement=THIN_PLACEMENT, tmp=None):
    """Notes whose model_names differ from what gen_notes.py makes from the live placement table."""
    regen = run_gen(tmp / "live.json", placement)
    return [f"{k}: file {notes.get(k, {}).get('model_names')} live {regen[k]['model_names']}"
            for k in sorted(regen) if notes.get(k, {}).get("model_names") != regen[k]["model_names"]]


def test_live_model_names_report_never_fails(tmp_path):
    diff = live_model_report(load_notes(), tmp=tmp_path)
    print(f"part-notes-C03 live placement.csv: {len(diff)} notes with model_names out of date")
    for d in diff:
        print("  ", d)
    if diff:
        print("   refresh with: python3 -I collector/tests/part-notes/gen_notes.py")
    assert isinstance(diff, list)


def test_mutation_live_model_report_names_change(tmp_path):
    n = load_notes()
    n["ring:BT1"]["model_names"] = ["stale_name"]
    assert any(d.startswith("ring:BT1") for d in live_model_report(n, tmp=tmp_path))
