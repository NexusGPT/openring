"""key-numbers (facts.json): size, weight, battery, recording hours, storage, each with unit and source.

Order of reading, per fact: a '## Key numbers' table of architecture.md first; else the places in
CANDIDATES, newest section first (the file says a later section wins over an earlier one). A fact
no place states reliably is left out and named in the status message; it is never guessed.
"""
import csv
import re

from lib import md  # noqa: E402
from lib.errors import SourceError  # noqa: E402
from lib.version import is_stale, read_own  # noqa: E402

RECORD = "key-numbers"

ARCH = "design/architecture.md"
MASS = "design/mech/out/mass-estimate.csv"

# header of the column for the newest design version: the last column headed like A4
LATEST = r"^[A-Z]{1,2}\d+$"
_NUM = r"\d+(?:\.\d+)?"
_RANGE = rf"{_NUM}(?: to {_NUM})?"

# id -> (label, unit, value pattern, candidates). A candidate is
#   ("line", heading_re, line_re)                      the first line of the section matching line_re
#   ("row", heading_re, row_re, column_re)             a table row whose first cell matches row_re,
#                                                      the cell of the column whose header matches column_re
# The value is group 1 of the value pattern, searched in the line or the cell.
FACTS = [
    ("size", "Size", "mm", rf"({_NUM} x {_NUM} x {_NUM}) mm", [
        ("line", r"^17\.1\b", r"[Bb]lock\b[^0-9\n]{0,12}"),
        ("line", r"^16\.1\b", r"[Bb]lock\b[^0-9\n]{0,12}"),
        ("line", r"^1\.", r"[Bb]lock\b[^0-9\n]{0,12}"),
    ]),
    ("battery", "Battery", "mAh", rf"(?<![\d.])({_RANGE}) ?mAh\b(?! per)", [
        ("line", r"^17\.3\b", r"^\s*[-*]?\s*Cell capacity"),
        ("row", r"^16\.4\b", r"^Cell$", LATEST),
        ("row", r"^2\.", r"^Cell$", r"^Key figures"),
    ]),
    ("hours", "Recording hours", "hours", rf":\s*({_RANGE}) hours", [
        ("line", r"^17\.5\b", r"\bmAh:\s*\d"),
        ("line", r"^16\.8\b", r"\bcell:\s*\d"),
        ("row", r"^4\.", r"^Hours on", r"^Recording"),
    ]),
    ("storage", "Storage", "GB", r"\b(\d+) ?GB\b", [
        ("row", r"^16\.4\b", r"^Storage$", LATEST),
        ("row", r"^2\.", r"^Storage$", r"^Part"),
    ]),
]

_KEY_LABELS = [("size", r"size"), ("weight", r"weight|mass"), ("battery", r"batter|cell"),
               ("hours", r"hour"), ("storage", r"storage")]
_LABELS = {f[0]: (f[1], f[2]) for f in FACTS}
_LABELS["weight"] = ("Weight", "g")


def _find_value(pattern, text):
    m = re.search(pattern, text)
    return m.group(1) if m else None


def _fact(fid, value, unit, file, line):
    label = _LABELS[fid][0]
    return {"id": fid, "label": label, "value": f"{value} {unit}", "unit": unit,
            "source": {"file": file, "line": line}}


def _from_key_table(text):
    """Facts from a '## Key numbers' table: first column names the fact, second holds the value."""
    found = {}
    sec = md.section(text, r"^Key numbers\b")
    if sec is None:
        return found
    first, last, _ = sec
    for t in md.tables(text, first, last):
        for row, line in zip(t["rows"], t["row_lines"]):
            for fid, rx in _KEY_LABELS:
                if fid not in found and re.search(rx, row[0], re.I) and len(row) > 1 and row[1]:
                    unit = _LABELS[fid][1]
                    val = row[1].strip()
                    val = re.sub(rf"\s*{re.escape(unit)}$", "", val)
                    found[fid] = _fact(fid, val, unit, ARCH, line)
    return found


def _from_candidates(text, fid, value_re, cands):
    unit = _LABELS[fid][1]
    for cand in cands:
        sec = md.section(text, cand[1])
        if sec is None:
            continue
        first, last, _ = sec
        if cand[0] == "line":
            lines = text.splitlines()
            for n in range(first + 1, last + 1):
                ln = lines[n - 1]
                if re.search(cand[2], ln):
                    pat = value_re if fid != "size" else cand[2] + value_re
                    v = _find_value(pat, ln)
                    if v:
                        return _fact(fid, v, unit, ARCH, n)
        else:
            for t in md.tables(text, first, last):
                hits = [i for i, c in enumerate(t["columns"]) if re.search(cand[3], c)]
                col = (hits[-1] if cand[3] == LATEST else hits[0]) if hits else None
                if col is None:
                    continue
                for row, line in zip(t["rows"], t["row_lines"]):
                    if re.search(cand[2], row[0]):
                        v = _find_value(value_re, row[col]) if fid != "hours" else (
                            row[col] if re.fullmatch(r"[\d.,]+", row[col].strip()) else None)
                        if v:
                            return _fact(fid, v.replace(",", ""), unit, ARCH, line)
    return None


def _weight(ctx, current):
    """Sum of mass_g over the item rows of the mass file; None when the file cannot give one
    figure that agrees with its own TOTAL row."""
    path = ctx.source_path(MASS)
    if not path.is_file():
        return None, "design/mech/out/mass-estimate.csv is absent"
    raw = path.read_text(encoding="utf-8")
    m = re.search(r"\bVersion:?\s+([A-Z]{1,2}\d+(?:-[A-Za-z]+)?)", raw)
    if m is None:
        return None, ("mass-estimate.csv names no design version, so its weight may have been estimated "
                      "for an earlier ring and is not shown as the current one")
    if current is None or is_stale(m.group(1), current):
        return None, (f"mass-estimate.csv was made for design {m.group(1)}; the design is now {current}, "
                      "so its weight is not shown")
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        header = next(reader, [])
        if "mass_g" not in header or "item" not in header:
            return None, "mass-estimate.csv has no item and mass_g columns"
        ci, cm = header.index("item"), header.index("mass_g")
        total, listed, total_line, prev = 0.0, None, None, reader.line_num
        for row in reader:
            line = prev + 1
            prev = reader.line_num
            if len(row) <= cm or not any(c.strip() for c in row):
                continue
            try:
                grams = float(row[cm])
            except ValueError:
                return None, f"mass-estimate.csv line {line}: mass_g {row[cm]!r} is not a number"
            if row[ci].strip().upper().startswith("TOTAL"):
                listed, total_line = grams, line
            else:
                total += grams
    if total_line is None:
        return None, "mass-estimate.csv has no TOTAL row to check the sum against"
    if abs(total - listed) > 0.05:
        return None, f"mass-estimate.csv items add to {total:.3f} g but its TOTAL row says {listed} g"
    return _fact("weight", f"{listed:g}", "g", MASS, total_line), None


def extract(ctx):
    path = ctx.source_path(ARCH)
    if not path.is_file():
        return None, {"status": "missing", "source": [ARCH], "message": f"{ARCH} is absent."}
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise SourceError(f"{ARCH} cannot be read: {e}", ARCH)
    facts = _from_key_table(text)
    problems = []
    for fid, _label, _unit, value_re, cands in FACTS:
        if fid not in facts:
            f = _from_candidates(text, fid, value_re, cands)
            if f:
                facts[fid] = f
            else:
                problems.append(f"{fid}: no readable statement in {ARCH}")
    if "weight" not in facts:
        w, why = _weight(ctx, read_own(text))
        if w:
            facts["weight"] = w
        else:
            problems.append(f"weight: {why}")
    if not facts:
        raise SourceError(f"{ARCH} states none of the key numbers in a form that can be read", ARCH)
    order = ["size", "weight", "battery", "hours", "storage"]
    data = {"design_version": read_own(text), "facts": [facts[k] for k in order if k in facts]}
    sources = [ARCH] + ([MASS] if "weight" in facts and facts["weight"]["source"]["file"] == MASS else [])
    notes = []
    if problems:
        notes.append("Left out, not readable: " + "; ".join(problems) + ".")
    msg = " ".join(notes) or None
    return data, {"status": "ok", "source": sources, "message": msg}
