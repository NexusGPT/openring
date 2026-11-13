#!/usr/bin/env python3
"""Check the manufacturing specifications.

Exit 0 when every spec file exists, has every required heading (with text
under it), and every number in the value cell of its "Critical dimensions"
table is found (within 0.02) in design/architecture.md or in the bounding box
of the part's STEP file(s) in design/mfg/parts/<part>/.  Exit 1 otherwise.

Added after review 2 (finding G19): a second rule reads EVERY table row of every spec page, not only
"Critical dimensions". For the quantities in CURRENT below (charging pad pitch, charging pad diameter, switch
cross radius of the joystick nub) a row that states the quantity must give the value the architecture's CURRENT
section gives (17.28 for the pads, 17.15 for the cross), within 0.02, even when the stale value still stands
somewhere else in architecture.md (fakes S1 to S4). The rule is limited to these named quantities: a general
"any number must be somewhere in the architecture" rule over all tables would fail the real pages, which
carry model figures per size, and tolerances.

Run: design/.venv/bin/python design/mfg/tools/check_docs.py
Options: --specs DIR  --arch FILE  --parts DIR  (for a trial on a copy)
"""
import argparse
import re
import sys
from pathlib import Path

MFG = Path(__file__).resolve().parent.parent
DESIGN = MFG.parent
TOL = 0.02
# record-cap is left out since 2026-11-11: the part does not exist (architecture 17.11); its page only says so.
SPECS = ["body", "band-liner", "cover-glass", "joystick-nub",
         "band-flex-tails", "main-board", "cell"]
PARTDIRS = {"band-flex-tails": ["flex-tail-thumb", "flex-tail-away"]}
HEADINGS = ["What it is", "Quantity per ring", "Material", "Process",
            "Finish and colour",
            "General tolerance and tighter tolerances",
            "Critical dimensions", "What to inspect", "Ring sizes", "Files",
            "Open points", "Source lines"]
NUM = re.compile(r"\d+(?:\.\d+)?")
# quantity name, architecture heading, regex (group 1 = the current value) in that section,
# regexes (group 1 = the value) that find the quantity in a table row of a spec page
CURRENT = [
    ("charging pad pitch", r"^### 17\.28 ", r"pitch ([\d.]+) mm along the arc",
     [r"pad pitch \| ([\d.]+)", r"charging pads?\b[^|]*\|[^|]*\bpitch ([\d.]+) mm"]),
    ("charging pad diameter", r"^### 17\.28 ", r"Diameter ([\d.]+) mm",
     [r"pad diameter \| ([\d.]+)", r"charging pads?\b[^|]*\|[^|]*\bdia ([\d.]+)"]),
    ("switch cross radius", r"^### 17\.15 ", r"at ([\d.]+) mm from the centre",
     [r"switch cross radius \| ([\d.]+)"]),
]


def arch_numbers(path):
    text = Path(path).read_text(encoding="utf-8")
    return sorted({float(x) for x in NUM.findall(text)})


def step_extents(partdir):
    """Bounding-box extents of every STEP file in partdir. Returns (list, errors)."""
    vals, errs = [], []
    if not partdir.is_dir():
        return vals, errs
    for f in sorted(list(partdir.glob("*.step")) + list(partdir.glob("*.stp"))):
        try:
            from build123d import import_step
            bb = import_step(str(f)).bounding_box()
            vals += [bb.size.X, bb.size.Y, bb.size.Z]
        except Exception as e:  # a STEP file that cannot be read is an error
            errs.append(f"{f}: cannot read STEP ({e})")
    return vals, errs


def sections(text):
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r"##\s+(.*\S)\s*$", line)
        if m:
            cur = m.group(1)
            out[cur] = []
        elif cur is not None:
            out[cur].append(line)
    return {k: "\n".join(v).strip() for k, v in out.items()}


def table_rows(body):
    rows = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or set(cells[0]) <= set("-: "):
            continue
        rows.append(cells)
    return rows


def current_values(arch_text, problems):
    vals = {}
    for name, head, pat, _ in CURRENT:
        m = re.search(head, arch_text, re.M)
        sec = ""
        if m:
            rest = arch_text[m.end():]
            e = re.search(r"^#{2,3} ", rest, re.M)
            sec = rest[: e.start()] if e else rest
        v = re.search(pat, sec)
        if not v:
            problems.append(f"architecture: current value of '{name}' not found (section {head[3:].strip()}, pattern {pat})")
        else:
            vals[name] = float(v.group(1))
    return vals


def check_current(spec_name, text, vals, problems):
    """Every table row of the page that states a quantity of CURRENT must give its current value."""
    n = 0
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        for name, _, _, pats in CURRENT:
            if name not in vals:
                continue
            for pat in pats:
                for m in re.finditer(pat, line):
                    n += 1
                    if abs(float(m.group(1)) - vals[name]) > TOL:
                        problems.append(f"{spec_name}: row states {name} {m.group(1)}, architecture gives {vals[name]}: {line.strip()[:90]}")
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--specs", default=str(MFG / "specs"))
    ap.add_argument("--arch", default=str(DESIGN / "architecture.md"))
    ap.add_argument("--parts", default=str(MFG / "parts"))
    a = ap.parse_args()
    arch = arch_numbers(a.arch)
    problems, checked, rows_n, cur_n = [], 0, 0, 0
    cur_vals = current_values(Path(a.arch).read_text(encoding="utf-8"), problems)
    for name in SPECS:
        f = Path(a.specs) / f"{name}.md"
        if not f.is_file():
            problems.append(f"{name}: spec file missing ({f})")
            continue
        secs = sections(f.read_text(encoding="utf-8"))
        cur_n += check_current(name, f.read_text(encoding="utf-8"), cur_vals, problems)
        for h in HEADINGS:
            if h not in secs:
                problems.append(f"{name}: heading missing: {h}")
            elif len(secs[h]) < 3:
                problems.append(f"{name}: heading empty: {h}")
        cd = secs.get("Critical dimensions", "")
        rows = table_rows(cd)
        if not rows or [c.lower() for c in rows[0][:1]] != ["name"]:
            problems.append(f"{name}: Critical dimensions has no table with header 'name'")
            continue
        if len(rows) < 2:
            problems.append(f"{name}: Critical dimensions table has no rows")
        step_vals, errs = [], []
        for d in PARTDIRS.get(name, [name]):
            v, e = step_extents(Path(a.parts) / d)
            step_vals += v
            errs += e
        problems += [f"{name}: {e}" for e in errs]
        for r in rows[1:]:
            rows_n += 1
            if len(r) != 4:
                problems.append(f"{name}: row does not have 4 cells: {r}")
                continue
            nums = [float(x) for x in NUM.findall(r[1])]
            if not nums:
                problems.append(f"{name}: no number in value cell of row '{r[0]}'")
            for n in nums:
                checked += 1
                ok = any(abs(n - v) <= TOL for v in arch) or \
                    any(abs(n - v) <= TOL for v in step_vals)
                if not ok:
                    problems.append(
                        f"{name}: '{r[0]}' value {n} not in architecture or STEP box (+-{TOL})")
    for p in problems:
        print("FAIL", p)
    print(f"checked {len(SPECS)} specs, {rows_n} table rows, {checked} values, "
          f"{cur_n} current-value rows, {len(problems)} problems")
    print("RESULT PASS" if not problems else "RESULT FAIL")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
