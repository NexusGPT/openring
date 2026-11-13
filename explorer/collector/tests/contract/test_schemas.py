import json
import shutil

import pytest

from conftest import SAMPLE_BUNDLE, read_json, run_collector
from lib import invariants, records, schema

IDS = records.record_ids()


def test_there_are_13_records_and_14_schema_names():
    assert len(IDS) == 13
    r = run_collector("--check-schemas")
    assert r.returncode == 0, r.stderr
    names = r.stdout.split()
    assert len(names) == 14 and names[-1] == "manifest"


@pytest.mark.parametrize("rid", IDS)
def test_sample_record_is_valid(rid):
    rec = records.by_id()[rid]
    d = read_json(SAMPLE_BUNDLE / rec["file"])
    assert schema.validate(d, rec["schema"]) == []
    if rid in invariants.SINGLE:
        assert invariants.SINGLE[rid](d) == []


def test_sample_manifest_and_part_notes_are_valid():
    assert schema.validate(read_json(SAMPLE_BUNDLE / "manifest.json"), "manifest") == []
    notes = read_json(SAMPLE_BUNDLE / "content" / "part-notes.json")
    assert schema.validate(notes, "content/part-notes") == []
    assert invariants.check_part_notes(notes) == []


def test_parts_line_without_refs_exits_1(tmp_path):
    d = read_json(SAMPLE_BUNDLE / "parts.json")
    del d["lines"][0]["refs"]
    f = tmp_path / "parts.json"
    f.write_text(json.dumps(d))
    r = run_collector("--validate", "parts", str(f))
    assert r.returncode == 1
    assert "refs" in r.stderr


def test_valid_parts_file_exits_0():
    r = run_collector("--validate", "parts", str(SAMPLE_BUNDLE / "parts.json"))
    assert r.returncode == 0, r.stderr


def test_unknown_record_exits_2():
    assert run_collector("--validate", "nope", str(SAMPLE_BUNDLE / "parts.json")).returncode == 2


@pytest.mark.parametrize("mutate,why", [
    (lambda d: d["lines"][0].update(part_ids=["ring:XX"]), "part_ids must be <bom>:<ref>"),
    (lambda d: d["lines"][1].update(quantity=5), "totals must equal the sum of quantity"),
    (lambda d: d["lines"][1].update(refs=["ZZ9", "ZZ6"], part_ids=["ring:ZZ9", "ring:ZZ6"]), "one ref belongs to one line"),
    (lambda d: d["lines"][0].update(evidence="MAYBE"), "evidence is an enum"),
    (lambda d: d["lines"][0].update(bom="shop", part_ids=["shop:ZZ9"]), "bom is ring or case"),
    (lambda d: d["totals"]["ring"].update(lines=99), "line count is rows"),
])
def test_parts_rules_reject(mutate, why, tmp_path):
    d = read_json(SAMPLE_BUNDLE / "parts.json")
    mutate(d)
    errs = schema.validate(d, "parts") or invariants.check_parts(d)
    assert errs, why


def test_lines_and_parts_mean_rows_and_sum_of_quantity():
    d = read_json(SAMPLE_BUNDLE / "parts.json")
    ring = [ln for ln in d["lines"] if ln["bom"] == "ring"]
    assert d["totals"]["ring"]["lines"] == len(ring)
    assert d["totals"]["ring"]["parts"] == sum(ln["quantity"] for ln in ring)


def test_area_states_need_the_8_areas():
    d = read_json(SAMPLE_BUNDLE / "areas.json")
    d["areas"] = d["areas"][:7]
    assert schema.validate(d, "area-states")
    d = read_json(SAMPLE_BUNDLE / "areas.json")
    d["areas"][1]["id"] = "look"
    assert invariants.check_area_states(d)


def test_area_state_words_are_the_five_exact_words():
    d = read_json(SAMPLE_BUNDLE / "areas.json")
    d["areas"][0]["state"] = "in-progress"
    assert schema.validate(d, "area-states")


def test_files_reject_traversal_and_duplicates():
    d = read_json(SAMPLE_BUNDLE / "files.json")
    d["files"].append(dict(d["files"][0]))
    assert invariants.check_files(d)
    d = read_json(SAMPLE_BUNDLE / "files.json")
    d["files"][0]["path"] = "/etc/passwd"
    assert schema.validate(d, "files")
    d["files"][0]["path"] = "a/../b"
    assert invariants.check_files(d)


def test_part_notes_word_limits_come_from_constants():
    c = records.constants()
    d = read_json(SAMPLE_BUNDLE / "content" / "part-notes.json")
    d["notes"]["ring:ZZ9"]["what"] = " ".join(["w"] * (c["NOTE_WHAT_WORDS"] + 1))
    assert invariants.check_part_notes(d)


def test_schema_validator_refuses_unknown_keywords(tmp_path):
    (tmp_path / "x.schema.json").write_text(json.dumps({"type": "object", "if": {}}))
    with pytest.raises(schema.SchemaError):
        schema.validate({}, "x", schema_dir=tmp_path)


def test_every_record_schema_refuses_extra_properties():
    for rid in IDS:
        rec = records.by_id()[rid]
        d = read_json(SAMPLE_BUNDLE / rec["file"])
        d["zz_extra"] = 1
        assert schema.validate(d, rec["schema"]), rid


def test_manifest_source_root_is_a_relative_label():
    m = read_json(SAMPLE_BUNDLE / "manifest.json")
    for bad in ["/Users/x/repo", "C:\\\\repo", "file:///repo"]:
        m["source_root"] = bad
        assert schema.validate(m, "manifest"), bad
    m["source_root"] = "ai-ring-recorder"
    assert schema.validate(m, "manifest") == []
