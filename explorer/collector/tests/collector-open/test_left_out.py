"""collector-open-C11..C13: the list of what a shared copy leaves out (made-up rows, no project value)."""
import importlib.util
import json

import pytest

from conftest import COLLECTOR


def load():
    spec = importlib.util.spec_from_file_location("files_extract", COLLECTOR / "extract" / "files.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_C11_no_file_named_means_nothing_left_out():
    assert load().left_out_list(None) == []
    assert load().left_out_list("") == []


def test_C12_rows_are_read_and_empty_groups_dropped(tmp_path):
    p = tmp_path / "left.json"
    p.write_text(json.dumps([{"what": " zz sheets ", "count": 3, "why": "zz reason"}, {"what": "zz none", "count": 0, "why": "zz"}]))
    assert load().left_out_list(str(p)) == [{"what": "zz sheets", "count": 3, "why": "zz reason"}]


@pytest.mark.parametrize("body", ["{", "{}", '[{"what": "zz", "count": "3", "why": "zz"}]', '[{"what": "", "count": 1, "why": "zz"}]', '[{"what": "zz", "count": true, "why": "zz"}]'])
def test_C13_a_named_file_that_is_wrong_is_an_error_never_a_silent_empty_list(tmp_path, body):
    p = tmp_path / "left.json"
    p.write_text(body)
    with pytest.raises(ValueError):
        load().left_out_list(str(p))
    with pytest.raises(ValueError):
        load().left_out_list(str(tmp_path / "absent.json"))
