import json
import subprocess

from conftest import SAMPLE_BUNDLE, read_json, run_collector
from lib import records

IDS = records.record_ids()
GOOD_PARTS = f"""
import json
RECORD = 'parts'
def extract(ctx):
    return json.load(open({str(SAMPLE_BUNDLE / 'parts.json')!r})), 'ok'
"""


def collect(source, out, folder, *extra):
    return run_collector("--source", str(source), "--out", str(out), "--extractors", str(folder), *extra)


def test_zero_extractors_lists_13_records_missing(tmp_path, source_repo):
    out = tmp_path / "out"
    r = collect(source_repo, out, tmp_path / "no-such-folder")
    assert r.returncode == 0, r.stderr
    m = read_json(out / "manifest.json")
    assert sorted(m["records"]) == sorted(IDS) and len(IDS) == 13
    assert {e["status"] for e in m["records"].values()} == {"missing"}
    assert not (out / "parts.json").exists()


def test_manifest_commit_equals_git_rev_parse(tmp_path, source_repo, extractors):
    folder, _ = extractors
    out = tmp_path / "out"
    assert collect(source_repo, out, folder).returncode == 0
    head = subprocess.run(["git", "-C", str(source_repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    m = read_json(out / "manifest.json")
    assert m["git_commit"] == head and len(head) == 40
    assert m["git_dirty"] is False
    assert m["source_root"] == "repo"  # a relative label, never an absolute path


def test_dirty_tree_is_reported(tmp_path, source_repo, extractors):
    folder, _ = extractors
    (source_repo / "design" / "note.md").write_text("changed\n")
    out = tmp_path / "out"
    collect(source_repo, out, folder)
    assert read_json(out / "manifest.json")["git_dirty"] is True


def test_a_copy_without_git_needs_a_commit_and_records_it(tmp_path, extractors):
    folder, _ = extractors
    copy = tmp_path / "copy"
    (copy / "design").mkdir(parents=True)
    out = tmp_path / "out"
    assert collect(copy, out, folder).returncode == 2
    sha = "99dfb85" + "0" * 33
    assert collect(copy, out, folder, "--commit", sha).returncode == 0
    assert read_json(out / "manifest.json")["git_commit"] == sha


def test_a_raising_extractor_makes_only_its_record_unparsed(tmp_path, source_repo, extractors):
    folder, write = extractors
    write("good_parts", GOOD_PARTS)
    base_out = tmp_path / "base"
    assert collect(source_repo, base_out, folder).returncode == 0
    write("boom", "RECORD = 'key-numbers'\ndef extract(ctx):\n    raise RuntimeError('zz exploded')\n")
    out = tmp_path / "out"
    r = collect(source_repo, out, folder)
    assert r.returncode == 0, r.stderr
    m, base = read_json(out / "manifest.json"), read_json(base_out / "manifest.json")
    assert m["records"]["key-numbers"]["status"] == "unparsed"
    assert "zz exploded" in m["records"]["key-numbers"]["message"]
    for rid in IDS:
        if rid != "key-numbers":
            assert m["records"][rid] == base["records"][rid], rid
    assert (out / "parts.json").read_bytes() == (base_out / "parts.json").read_bytes()
    assert not (out / "facts.json").exists()


def test_source_error_names_the_file(tmp_path, source_repo, extractors):
    folder, write = extractors
    write("bad", "from lib.errors import SourceError\nRECORD = 'open-items'\ndef extract(ctx):\n    raise SourceError('cannot read table', 'design/architecture.md')\n")
    out = tmp_path / "out"
    collect(source_repo, out, folder)
    e = read_json(out / "manifest.json")["records"]["open-items"]
    assert e["status"] == "unparsed" and e["source"] == ["design/architecture.md"]


def test_output_that_breaks_its_schema_is_unparsed_and_not_written(tmp_path, source_repo, extractors):
    folder, write = extractors
    write("bad", "RECORD = 'parts'\ndef extract(ctx):\n    return {'lines': [{'bom': 'ring'}]}, 'ok'\n")
    out = tmp_path / "out"
    assert collect(source_repo, out, folder).returncode == 0
    e = read_json(out / "manifest.json")["records"]["parts"]
    assert e["status"] == "unparsed" and "schema" in e["message"]
    assert not (out / "parts.json").exists()


def test_stale_status_from_versions(tmp_path, source_repo, extractors):
    folder, write = extractors
    body = f"""
import json
RECORD = 'area-states'
def extract(ctx):
    d = json.load(open({str(SAMPLE_BUNDLE / 'areas.json')!r}))
    return d, {{'status': 'ok', 'source': ['design/status.json'], 'basis_version': 'A3', 'current_version': 'A4-draft'}}
"""
    write("areas", body)
    out = tmp_path / "out"
    collect(source_repo, out, folder)
    e = read_json(out / "manifest.json")["records"]["area-states"]
    assert e["status"] == "stale" and e["basis_version"] == "A3" and e["current_version"] == "A4-draft"
    assert (out / "areas.json").exists()


def test_helper_modules_are_skipped_and_unknown_record_is_an_error(tmp_path, source_repo, extractors):
    folder, write = extractors
    write("helper", "X = 1\n")
    assert collect(source_repo, tmp_path / "o1", folder).returncode == 0
    write("odd", "RECORD = 'not-a-record'\ndef extract(ctx):\n    return None, 'missing'\n")
    assert collect(source_repo, tmp_path / "o2", folder).returncode == 1


def test_two_extractors_for_one_record_is_an_error(tmp_path, source_repo, extractors):
    folder, write = extractors
    write("a", "RECORD = 'parts'\ndef extract(ctx):\n    return None, 'missing'\n")
    write("b", "RECORD = 'parts'\ndef extract(ctx):\n    return None, 'missing'\n")
    assert collect(source_repo, tmp_path / "o", folder).returncode == 1


def test_a_part_id_another_record_points_at_must_exist(tmp_path, source_repo, extractors):
    folder, write = extractors
    write("good_parts", GOOD_PARTS)
    body = f"""
import json
RECORD = 'case'
def extract(ctx):
    d = json.load(open({str(SAMPLE_BUNDLE / 'case' / 'index.json')!r}))
    d['part_ids'] = ['case:NOPE']
    return d, 'ok'
"""
    write("case", body)
    out = tmp_path / "out"
    collect(source_repo, out, folder)
    m = read_json(out / "manifest.json")
    assert m["records"]["case"]["status"] == "unparsed" and "NOPE" in m["records"]["case"]["message"]
    assert m["records"]["parts"]["status"] == "ok"
    assert not (out / "case" / "index.json").exists()


def test_rerun_is_byte_identical_for_unchanged_source(tmp_path, source_repo, extractors):
    folder, write = extractors
    write("good_parts", GOOD_PARTS)
    a, b = tmp_path / "a", tmp_path / "b"
    collect(source_repo, a, folder)
    collect(source_repo, b, folder)
    assert (a / "parts.json").read_bytes() == (b / "parts.json").read_bytes()


def test_extra_files_stay_inside_the_bundle(tmp_path, source_repo, extractors):
    folder, write = extractors
    write("odd", "RECORD = 'files'\ndef extract(ctx):\n    ctx.out_path('../escape.txt')\n    return None, 'missing'\n")
    out = tmp_path / "out"
    collect(source_repo, out, folder)
    e = read_json(out / "manifest.json")["records"]["files"]
    assert e["status"] == "unparsed" and "leaves the bundle" in e["message"]
    assert not (tmp_path / "escape.txt").exists()


def test_a_record_holding_an_absolute_path_or_local_address_is_unparsed(tmp_path, source_repo, extractors):
    for n, bad in enumerate(["/Users/someone/design/parts/a.md", "see http://localhost:8790/x", "C:\\\\design\\\\a.md", "file:///tmp/a"]):
        folder, write = extractors
        body = f"""
import json
RECORD = 'key-numbers'
def extract(ctx):
    d = json.load(open({str(SAMPLE_BUNDLE / 'facts.json')!r}))
    d['facts'][0]['label'] = {bad!r}
    return d, 'ok'
"""
        write("facts", body)
        out = tmp_path / f"out{n}"
        collect(source_repo, out, folder)
        e = read_json(out / "manifest.json")["records"]["key-numbers"]
        assert e["status"] == "unparsed" and "absolute or local address" in e["message"], bad
        assert not (out / "facts.json").exists()


def test_relative_paths_pass_the_absolute_check():
    from lib import invariants
    assert invariants.check_no_absolute({"a": "design/parts/mcu.md section 1a", "b": ["R14-R22", "a/b/etc/x"]}) == []


def notes_dir(tmp_path, text=None):
    d = tmp_path / "content"
    d.mkdir()
    if text is None:
        text = (SAMPLE_BUNDLE / "content" / "part-notes.json").read_text()
    (d / "part-notes.json").write_text(text)
    return d


def test_part_notes_travel_with_the_bundle(tmp_path, source_repo, extractors):
    folder, _ = extractors
    out = tmp_path / "out"
    assert collect(source_repo, out, folder, "--content", str(notes_dir(tmp_path))).returncode == 0
    m = read_json(out / "manifest.json")
    assert m["content"]["part-notes"]["status"] == "ok"
    assert m["content"]["part-notes"]["source"] == ["content/part-notes.json"]
    assert len(m["records"]) == 13  # part notes are listed like a record but are not one of the 13
    assert read_json(out / "content" / "part-notes.json") == read_json(SAMPLE_BUNDLE / "content" / "part-notes.json")


def test_part_notes_missing_invalid_and_broken(tmp_path, source_repo, extractors):
    folder, _ = extractors
    out = tmp_path / "o1"
    collect(source_repo, out, folder, "--content", str(tmp_path / "no-content"))
    assert read_json(out / "manifest.json")["content"]["part-notes"]["status"] == "missing"
    assert not (out / "content" / "part-notes.json").exists()
    for n, text in enumerate(["{nope", json.dumps({"notes": {"ring:ZZ9": {"what": "x"}}}),
                              json.dumps({"notes": {"ring:ZZ9": {"what": "a", "why": "b", "checked_against": "/Users/x/a.md", "model_names": []}}})]):
        d = tmp_path / f"c{n}"
        d.mkdir()
        out = tmp_path / f"o{n + 2}"
        collect(source_repo, out, folder, "--content", str(notes_dir(d, text)))
        e = read_json(out / "manifest.json")["content"]["part-notes"]
        assert e["status"] == "unparsed", text
        assert not (out / "content" / "part-notes.json").exists()
