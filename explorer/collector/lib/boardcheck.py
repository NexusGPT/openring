"""Checks of the boards list (board-files, field boards). Each returns a list of problems in plain words; an empty list
means the list passes. The numbers of a board's state are compared with the count lines of its rules report, read here
with patterns of their own."""
import re
from pathlib import Path


def report_numbers(text):
    """(violations, open connections) as the report's own count lines state them, or None for a missing line."""
    v = re.search(r"Found (\d+) DRC violations?", text)
    o = re.search(r"Found (\d+) unconnected (?:pads?|items?)", text)
    return (int(v.group(1)) if v else None), (int(o.group(1)) if o else None)


def check_files_and_layers(boards, bundle, root):
    """Every board has its file on disk and at least one copper layer picture that is not empty."""
    problems = []
    if not boards:
        return ["the boards list is empty"]
    for b in boards:
        bid = b.get("id")
        if not b.get("file") or not (Path(root) / b["file"]).is_file():
            problems.append(f"{bid}: board file {b.get('file')!r} is not on disk")
        layers = b.get("layers") or []
        if not layers:
            problems.append(f"{bid}: no copper layer")
        full = 0
        for l in layers:
            svg = l.get("svg")
            f = Path(bundle) / svg if svg else None
            if f is None or not f.is_file() or f.stat().st_size == 0:
                problems.append(f"{bid}: layer {l.get('id')} has no picture file")
                continue
            if "<path" not in f.read_text(encoding="utf-8", errors="replace"):
                problems.append(f"{bid}: layer {l.get('id')} picture holds no drawing")
                continue
            if l.get("items", 0) > 0:
                full += 1
        if layers and full == 0:
            problems.append(f"{bid}: every copper layer picture is empty")
    return problems


def check_states(boards, bundle):
    """The numbers of each state equal the count lines of its report; the status and the words follow from the numbers."""
    problems = []
    for b in boards:
        bid, st = b.get("id"), b.get("state") or {}
        if st.get("status") == "not-checked":
            continue
        rep = st.get("report")
        f = Path(bundle) / rep if rep else None
        if f is None or not f.is_file():
            problems.append(f"{bid}: no rules report on disk")
            continue
        v, o = report_numbers(f.read_text(encoding="utf-8", errors="replace"))
        if v is None or o is None:
            problems.append(f"{bid}: the report has no count lines")
            continue
        if (st.get("violations"), st.get("open_connections")) != (v, o):
            problems.append(f"{bid}: state says {st.get('violations')} violations and {st.get('open_connections')} open, "
                            f"the report says {v} and {o}")
        finished = v == 0 and o == 0
        if finished != (st.get("status") == "routed-checked"):
            problems.append(f"{bid}: status {st.get('status')!r} does not follow from the report ({v} violations, {o} open)")
        words = st.get("words", "")
        if finished and words != "routed and checked: 0 violations, 0 open connections":
            problems.append(f"{bid}: words {words!r} do not state a finished board")
        if not finished and not re.fullmatch(rf"not finished: {o} connections? open, {v} violations?", words):
            problems.append(f"{bid}: words {words!r} do not state {o} open and {v} violations")
    return problems


def check_ring_not_finished(boards, bundle):
    """A board whose report counts open connections is never called routed and checked (the ring board's rule)."""
    problems = []
    for b in boards:
        st = b.get("state") or {}
        rep = st.get("report")
        f = Path(bundle) / rep if rep else None
        if f is None or not f.is_file():
            continue
        v, o = report_numbers(f.read_text(encoding="utf-8", errors="replace"))
        if o and st.get("status") != "not-finished":
            problems.append(f"{b.get('id')}: its report counts {o} open connections but its state is {st.get('status')!r}")
    ring = [b for b in boards if b.get("group") == "ring"]
    if not ring:
        problems.append("the list has no ring board")
    return problems
